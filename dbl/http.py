# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2019 Assanali Mukhanov

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
import os
import json
import logging
import sys
from datetime import datetime  # , timedelta
from ratelimiter import RateLimiter

import aiohttp

from . import __version__
from . import errors

log = logging.getLogger(__name__)

async def json_or_text(response):
    """Turns response into a properly formatted json or text object"""
    text = await response.text()
    if response.headers['Content-Type'] == 'application/json; charset=utf-8':
        return json.loads(text)
    return text


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the DBL API.

    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    token :
        A DBL API Token
    **session : Optional[aiohttp session]
        The session used to request to the API
    **loop
    """

    def __init__(self, token, **kwargs):
        self.BASE = 'https://discordbots.org/api'
        self.token = token
        self.loop = asyncio.get_event_loop() if kwargs.get('loop') is None else kwargs.get('loop')
        self.session = kwargs.get('session') or aiohttp.ClientSession(loop=kwargs.get('loop'))
        self._global_over = asyncio.Event(loop=self.loop)
        self._global_over.set()

        user_agent = 'DBL-Python-Library (https://github.com/DiscordBotList/DBL-Python-Library {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

# TODO: better implementation of ratelimits
# NOTE: current implementation doesn't maintain state over restart

    async def request(self, method, url, **kwargs):
        """Handles requests to the API"""
        url = "{0}{1}".format(self.BASE, url)
        rate_limiter = RateLimiter(max_calls=59, period=60, callback=limited)
        # handles ratelimits. max_calls is set to 59 because current implementation will retry in 60s after 60 calls is reached. DBL has a 1h block so obviously this doesn't work well, as it will get a 429 when 60 is reached.

        async with rate_limiter:  # this works but doesn't 'save' over restart. need a better implementation.

            if not self.token:
                raise UnauthorizedDetected("DBL token not provided")

            headers = {
                'User-Agent': self.user_agent,
                'Content-Type': 'application/json',
                'Authorization': self.token
            }

            if 'json' in kwargs:
                kwargs['data'] = to_json(kwargs.pop('json'))

            kwargs['headers'] = headers


            for tries in range(5):
                async with self.session.request(method, url, **kwargs) as resp:
                    log.debug('%s %s with %s has returned %s', method,
                              url, kwargs.get('data'), resp.status)

                    data = await json_or_text(resp)


                    if 300 > resp.status >= 200:
                        return data


                    if resp.status == 429:  # we are being ratelimited
                        fmt = 'We are being rate limited. Retrying in %.2f seconds (%.3f minutes).'

                        # sleep a bit
                        retry_after = json.loads(resp.headers.get('Retry-After'))
                        mins = retry_after / 60
                        log.warning(fmt, retry_after, mins)

                        # check if it's a global rate limit (True as only 1 ratelimit atm - /api/bots)
                        is_global = True  # is_global = data.get('global', False)
                        if is_global:
                            self._global_over.clear()

                        await asyncio.sleep(retry_after, loop=self.loop)
                        log.debug('Done sleeping for the rate limit. Retrying...')

                        # release the global lock now that the
                        # global rate limit has passed
                        if is_global:
                            self._global_over.set()
                            log.debug('Global rate limit is now over.')

                        continue


                    if resp.status == 400:
                        raise errors.HTTPException(resp, data)
                    elif resp.status == 401:
                        raise errors.Unauthorized(resp, data)
                    elif resp.status == 403:
                        raise errors.Forbidden(resp, data)
                    elif resp.status == 404:
                        raise errors.NotFound(resp, data)
                    else:
                        raise errors.HTTPException(resp, data)
            # We've run out of retries, raise.
            raise errors.HTTPException(resp, data)

    async def close(self):
        await self.session.close()

    async def recreate(self):
        self.session = aiohttp.ClientSession(loop=self.session.loop)

    async def post_guild_count(self, bot_id, guild_count, shard_count, shard_no):
        """Posts bot's guild count and shards info on DBL"""
        if shard_count:
            payload = {
                'server_count': guild_count,
                'shard_count': shard_count,
                'shard_no': shard_no
            }
        else:
            payload = {
                'server_count': guild_count
            }
        await self.request('POST', '/bots/{}/stats'.format(bot_id), json=payload)

    async def get_weekend_status(self):
        """Gets the weekend status from DBL"""
        return await self.request('GET', '/weekend')

    async def get_guild_count(self, bot_id):
        """Gets the guild count of the given Bot ID"""
        return await self.request('GET', '/bots/{}/stats'.format(bot_id))

    async def get_bot_info(self, bot_id):
        """Gets the information of the given Bot ID"""
        resp = await self.request('GET', '/bots/{}'.format(bot_id))
        resp['date'] = datetime.strptime(resp['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        for k in resp:
            if resp[k] == '':
                resp[k] = None
        return resp

    async def get_bot_upvotes(self, bot_id):
        """Gets your bot's last 1000 votes on DBL"""
        return await self.request('GET', '/bots/{}/votes'.format(bot_id))

    async def get_bots(self, limit, offset, sort, search, fields):
        """Gets an object of bots on DBL"""
        if limit > 500:
            limit = 50
        fields = ', '.join(fields)
        search = ' '.join(['{}: {}'.format(field, value) for field, value in search.items()])

        return await self.request('GET', '/bots', params={'limit': limit, 'offset': offset, 'sort': sort, 'search': search, 'fields': fields})

    async def get_user_info(self, user_id):
        """Gets an object of the user on DBL"""
        return await self.request('GET', '/users/{}'.format(user_id))

    async def get_user_vote(self, bot_id, user_id):
        """Gets an info whether the user has upvoted your bot"""
        return await self.request('GET', '/bots/{}/check'.format(bot_id), params={'userId': user_id})

async def limited(until):
    """Handles the message shown when we are ratelimited"""
    duration = round(until - datetime.datetime.now().timestamp())
    mins = duration / 60
    fmt = 'We have exhausted a ratelimit quota. Retrying in %.2f seconds (%.3f minutes).'
    log.warn(fmt, duration, mins)


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)
