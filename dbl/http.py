# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2018 Francis Taylor

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
from urllib.parse import urlencode
from ratelimiter import RateLimiter

import aiohttp

from . import __version__
from .errors import *
#from .webhookserverhandler import WebHook

log = logging.getLogger(__name__)


@asyncio.coroutine
def json_or_text(response):
    """Turns response into a properly formatted json or text object"""
    text = response.text(encoding='utf-8')
    if response.headers['content-type'] == 'application/json':
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
# NOTE: current implementation doesn't (a) maintain state over restart and (b) wait an hour when a 429 is hit

    async def request(self, method, url, **kwargs):
        """Handles requests to the API"""
        rate_limiter = RateLimiter(max_calls=59, period=60, callback=limited)
        # handles ratelimits. max_calls is set to 59 because current implementation will retry in 60s after 60 calls is reached. DBL has a 1h block so obviously this doesn't work well, as it will get a 429 when 60 is reached.

        async with rate_limiter:  # this works but doesn't 'save' over restart. need a better implementation.

            if not self.token:
                raise UnauthorizedDetected('Unauthorized (status code: 401): No TOKEN provided')

            headers = {
                'User-Agent': self.user_agent,
                'Authorization': self.token
            }

            if 'json' in kwargs:
                headers['Content-Type'] = 'application/json'
                kwargs['data'] = to_json(kwargs.pop('json'))

            kwargs['headers'] = headers

            # if not self._global_over.is_set():
            # wait until the global lock is complete
            #    await self._global_over.wait()

            # await lock
            # with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                async with self.session.request(method, url, **kwargs) as resp:
                    log.debug('%s %s with %s has returned %s', method,
                              url, kwargs.get('data'), resp.status)
                    text = await resp.text()
                try:
                    data = await json_or_text(resp)

                    # remaining = self._rl['quota']
                    # if remaining == '0' and resp.status != 429:
                    #     # we've depleted our current request quota
                    #     delta = 60
                    #
                    #     log.warning(
                    #         'A rate limit bucket has been exhausted (retry in: %s).', delta)
                    #     maybe_lock.defer()
                    #     self.loop.call_later(delta, lock.release)

                    if 300 > resp.status >= 200:
                        data = json.loads(text)
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
                        raise HTTPException(resp, data)
                    elif resp.status == 401:
                        raise Unauthorized(resp, data)
                    elif resp.status == 403:
                        raise Forbidden(resp, data)
                    elif resp.status == 404:
                        raise NotFound(resp, data)
                    else:
                        raise HTTPException(resp, data)
                finally:
                    # clean-up just in case
                    await resp.release()
            # We've run out of retries, raise.
            raise HTTPException(resp, data)

    async def close(self):
        await self.session.close()

    async def recreate(self):
        self.session = aiohttp.ClientSession(loop=self.session.loop)

    async def post_server_count(self, bot_id, guild_count, shard_count, shard_no):
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

        await self.request('POST', '{}/bots/{}/stats'.format(self.BASE, bot_id), json=payload)

    async def get_server_count(self, bot_id):
        '''Gets the server count of the given Bot ID'''
        return await self.request('GET', '{}/bots/{}/stats'.format(self.BASE, bot_id))

    async def get_bot_info(self, bot_id):
        '''Gets the information of the given Bot ID'''
        resp = await self.request('GET', '{}/bots/{}'.format(self.BASE, bot_id))
        resp['date'] = datetime.strptime(resp['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
        for k in resp:
            if resp[k] == '':
                resp[k] = None
        return resp

    async def get_upvote_info(self, bot_id, onlyids, days):
        '''Gets the upvote information of the given Bot ID'''
        params = {
            'onlyids': onlyids,
            'days': days
        }
        return await self.request('GET', '{}/bots/{}/votes?'.format(self.BASE, bot_id) + urlencode(params))

    async def get_bots(self, limit, offset):
        '''Gets an object of all the bots on DBL'''
        return await self.request('GET', '{}/bots?limit={}&offset={}'.format(self.BASE, limit, offset))

    # async def search_bots(self, limit, offset, query):
    #     return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}&search={query}')

    async def get_user_info(self, user_id):
        '''Gets an object of the user on DBL'''
        return await self.request('GET', '{}/users/{}'.format(self.BASE, user_id))

    # async def initialize_webhooks(self, auth: str = None):
    #     '''Initializes the webhook server'''
    #     # setup webhook server
    #     os.environ['HOOK_AUTH'] = str(auth)
    #     os.environ['WEBHOOKS'] = True
    #     await self.start_websocket_server()

    @property
    def bucket(self):
        # the bucket is just method + path w/ major parameters
        return '{0.method}:{0.url}'.format(self)


@asyncio.coroutine
def limited(until):
    """Handles the message shown when we are ratelimited"""
    duration = int(round(until - time.time()))
    mins = duration / 60
    fmt = 'We have exhausted a ratelimit quota. Retrying in %.2f seconds (%.3f minutes).'
    log.warn(fmt, duration, mins)


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)
