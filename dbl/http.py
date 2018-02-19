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
import json
import logging
import sys
import weakref
from ratelimiter import RateLimiter
from datetime import datetime, timedelta
from urllib.parse import urlencode

import aiohttp

from . import __version__
from .errors import *

log = logging.getLogger(__name__)


@asyncio.coroutine
def json_or_text(response):
    text = response.text(encoding='utf-8')
    if response.headers['content-type'] == 'application/json':
        return json.loads(text)
    return text


# class MaybeUnlock:
#     def __init__(self, lock):
#         self.lock = lock
#         self._unlock = True
#
#     def __enter__(self):
#         return self
#
#     def defer(self):
#         self._unlock = False
#
#     def __exit__(self, type, value, traceback):
#         if self._unlock:
#             self.lock.release()


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
        #self._locks = weakref.WeakValueDictionary()
        # self._rl = weakref.WeakValueDictionary()
        self._global_over = asyncio.Event(loop=self.loop)
        self._global_over.set()
        self.rate_limiter = RateLimiter(max_calls=60, period=60,
                                        callback=await self.limited)  # handles ratelimits

        user_agent = 'DBL-Python-Library (https://github.com/DiscordBotList/DBL-Python-Library {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, method, url, **kwargs):
        async with self.rate_limiter:  # this works but doesn't 'save' over restart. just pray and hope?
            #lock = self._locks.get(url)
            # if lock is None:
            #    lock = asyncio.Lock(loop=self.loop)
            #    if url is not None:
            #        self._locks[url] = lock

            # # key error -> quota
            # log.debug(self._rl)
            # quota = self._rl.get()
            # log.debug(quota)
            # if self._rl['quota'] is None:
            #     log.debug('remaining quota is Null.')
            #     remaining = 60
            #     self._rl['quota'] = remaining
            #     log.debug('setting ratelimit quota to default (%s)', remaining)
            # remaining = self._rl['quota']
            # log.debug(remaining)    # TEST
            # reset_at = self._rl['reset']
            # log.debug(reset_at)     # TEST
            # if reset_at is None:
            #     log.debug('reset time is Null.')
            #     reset_at = datetime.now() + timedelta(minutes=1)
            #     self._rl['reset'] = reset_at
            #     log.debug('setting reset time: %s', reset_at)
            # if reset_at.timestamp() < datetime.now().timestamp():
            #     log.debug('passed ratelimit quota reset time, resetting.')
            #     remaining = 60
            #     self._rl['quota'] = remaining
            #     log.debug('reset ratelimit quota')
            # else:
            #     remaining = remaining - 1
            #     self._rl['quota'] = remaining

            if not self.token:
                raise Unauthorized_Detected('Unauthorized (status code: 401): No TOKEN provided')

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

    def recreate(self):
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

        await self.request('POST', f'{self.BASE}/bots/{bot_id}/stats', json=payload)

    async def get_server_count(self, bot_id):
        '''Gets the server count of the given Bot ID'''
        return await self.request('GET', f'{self.BASE}/bots/{bot_id}/stats')

    async def get_bot_info(self, bot_id):
        '''Gets the information of the given Bot ID'''
        resp = await self.request('GET', f'{self.BASE}/bots/{bot_id}')
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
        return await self.request('GET', f'{self.BASE}/bots/{bot_id}/votes' + urlencode(params))

    async def get_bots(self, limit, offset):
        return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}')

    # async def get_bots(self, limit, offset, query):
    #     return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}&search={query}')

    async def get_user_info(self, user_id):
        return await self.request('GET', f'{self.BASE}/users/{user_id}')

    @property
    def bucket(self):
        # the bucket is just method + path w/ major parameters
        return '{0.method}:{0.url}'.format(self)

    async def limited(until):
        duration = int(round(until - time.time()))
        mins = duration / 60
        fmt = 'We have exhausted a ratelimit quota. Retrying in %.2f seconds (%.3f minutes).'
        log.warn(fmt, duration, mins)


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)
