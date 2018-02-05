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

import aiohttp
import asyncio
import json
import sys
import weakref
import logging
import datetime
from email.utils import parsedate_to_datetime

from . import __version__
from .errors import HTTPException, Forbidden, NotFound


@asyncio.coroutine
def json_or_text(response):
    text = yield from response.text(encoding='utf-8')
    if response.headers['content-type'] == 'application/json':
        return json.loads(text)
    return text


class MaybeUnlock:
    def __init__(self, lock):
        self.lock = lock
        self._unlock = True

    def __enter__(self):
        return self

    def defer(self):
        self._unlock = False

    def __exit__(self, type, value, traceback):
        if self._unlock:
            self.lock.release()


class Route:
    BASE = 'https://discordbots.org/api'

    def __init__(self, method, path, **parameters):
        self.path = path
        self.method = method
        url = (self.BASE + self.path)
        if parameters:
            self.url = url.format(**parameters)
        else:
            self.url = url

        @property
        def bucket(self):
            # the bucket is just method + path w/ major parameters
            return '{0.method}:{0.path}'.format(self)


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the DBL API."""

    SUCCESS_LOG = '{method} {url} has received {text}'
    REQUEST_LOG = '{method} {url} with {json} has returned {status}'

    def __init__(self, connector=None, *, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.connector = connector
        self.session = aiohttp.ClientSession(connector=connector, loop=self.loop)
        self.token = None
        self._locks = weakref.WeakValueDictionary()
        self._global_over = asyncio.Event(loop=self.loop)
        self._global_over.set()

        user_agent = 'DBL-Python-Library (https://github.com/DiscordBotList/DBL-Python-Library {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    @asyncio.coroutine
    def request(self, route, **kwargs):
        bucket = route.bucket
        method = route.method
        url = route.url

        # header creation
        headers = {
            'User-Agent': self.user_agent,
        }

        if self.token is not None:
            headers['Authorization'] = self.token

        # some checking if it's a JSON request
        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

            kwargs['headers'] = headers

        # thanks danny
        if not self._global_over.is_set():
            # wait until the global lock is complete
            yield from self._global_over.wait()

        yield from lock
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                r = yield from self.session.request(method, url, **kwargs)
                log.debug(self.REQUEST_LOG.format(method=method, url=url,
                                                  status=r.status, json=kwargs.get('data')))
                try:
                    # even errors have text involved in them so this is safe to call
                    data = yield from json_or_text(r)

                    # check if we have rate limit header information
                    remaining = r.headers.get('X-Ratelimit-Remaining')
                    if remaining == '0' and r.status != 429:
                        # we've depleted our current bucket
                        if header_bypass_delay is None:
                            now = parsedate_to_datetime(r.headers['Date'])
                            reset = datetime.datetime.fromtimestamp(
                                int(3600), datetime.timezone.utc)
                            delta = (reset - now).total_seconds()
                        else:
                            delta = header_bypass_delay

                        fmt = 'A rate limit bucket has been exhausted (bucket: {bucket}, retry: {delta}).'
                        log.info(fmt.format(bucket=bucket, delta=delta))
                        maybe_lock.defer()
                        self.loop.call_later(delta, lock.release)

                    # the request was successful so just return the text/json
                    if 300 > r.status >= 200:
                        log.debug(self.SUCCESS_LOG.format(method=method, url=url, text=data))
                        return data

                    # we are being rate limited
                    if r.status == 429:
                        fmt = 'We are being rate limited. Retrying in {:.2} seconds. Handled under the bucket "{}"'

                        # sleep a bit
                        retry_after = data['retry_after'] / 1000.0
                        log.info(fmt.format(retry_after, bucket))

                        # check if it's a global rate limit
                        is_global = data.get('global', False)
                        if is_global:
                            log.info(
                                'Global rate limit has been hit. Retrying in {:.2} seconds.'.format(retry_after))
                            self._global_over.clear()

                        yield from asyncio.sleep(retry_after, loop=self.loop)
                        log.debug('Done sleeping for the rate limit. Retrying...')

                        # release the global lock now that the
                        # global rate limit has passed
                        if is_global:
                            self._global_over.set()
                            log.debug('Global rate limit is now over.')

                        continue

                    # we've received a 502, unconditional retry
                    if r.status == 502 and tries <= 5:
                        yield from asyncio.sleep(1 + tries * 2, loop=self.loop)
                        continue

                    # the usual error cases
                    if r.status == 403:
                        raise Forbidden(r, data)
                    elif r.status == 404:
                        raise NotFound(r, data)
                    else:
                        raise HTTPException(r, data)
                finally:
                    # clean-up just in case
                    yield from r.release()

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    # state management

    @asyncio.coroutine
    def close(self):
        yield from self.session.close()

    def recreate(self):
        self.session = aiohttp.ClientSession(connector=self.connector, loop=self.loop)

    def _token(self, token):
        self.token = token

    @asyncio.coroutine
    def post_server_count(id, token, guild_count, shard_count, shard_no):
        payload = {
            'server_count': guild_count,
            'shard_count': shard_count,
            'shard_no': shard_no
        }
        self.token = token
        return self.request(Route('POST', '/bots/{id}/stats'), json=payload)

    @asyncio.coroutine
    def get_server_count(id):
        scount = self.request(Route('GET', '/bots/{id}/stats'))
        return scount['server_count']

    @asyncio.coroutine
    def get_upvote_count(id):
        ucount = self.request(Route('GET', '/bots/{id}/stats'))
        return ucount['points']

    @asyncio.coroutine
    def get_upvote_info(id, token):
        self.token = token
        return self.request(Route('GET', '/bots/{id}/votes'))

    @asyncio.coroutine
    def get_bot_info(id):
        return self.request(Route('GET', '/bots/{id}/stats'))

    @asyncio.coroutine
    def get_bots(limit, offset):
        headers['limit'] = limit
        headers['offset'] = offset

        return self.request(Route('GET', '/bots'))

    @asyncio.coroutine
    def get_user(id):
        return self.request(Route('GET', '/user/{id}'))

    @asyncio.coroutine
    def gen_widget_lrg(url):
        return self.request(Route('GET', url))

    @asyncio.coroutine
    def gen_widget_small(url):
        return self.request(Route('GET', url))
