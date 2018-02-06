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
import logging


from . import __version__
from .errors import *


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the DBL API."""

    BASE = 'https://discordbots.org/api'

    def __init__(self, connector=None, *, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession(connector=connector, loop=self.loop)
        self.token = 'a'

        user_agent = 'DBL-Python-Library (https://github.com/DiscordBotList/DBL-Python-Library {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, method, url, **kwargs):
        headers = {
            'User-Agent': self.user_agent,
            'Authorization': self.token
        }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = to_json(kwargs.pop('json'))

        kwargs['headers'] = headers

        # add auth like above??
        async with self.session.request(method, url, **kwargs) as response:
            text = await response.text()
            try:
                data = json.loads(text)
            except json.decoder.JSONDecodeError:
                data = {'message': text} if text else None
            except ValueError:
                data = {'message': text} if text else None

            if 300 > response.status >= 200:
                return data
            elif response.status == 400:
                raise HTTPException(data.pop('message', 'unknown'))
            elif response.status == 401:
                raise Unauthorized(data.pop('message', 'unknown'))
            elif response.status == 403:
                raise Forbidden(data.pop('message', 'unknown'))
            elif response.status == 404:
                raise NotFound(data.pop('message', 'unknown'))
            elif response.status == 429:
                raise Ratelimited(data.pop('message', 'unknown'))
            else:
                raise HTTPException(data.pop('message', 'Unknown error'), response)

    # async def get(self, *args, **kwargs):
    #     return self.request('GET', *args, **kwargs)
    #
    # async def post(self, *args, **kwargs):
    #     return self.request('POST', *args, **kwargs)

    # state management

    async def close(self):
        await self.session.close()

    async def recreate(self):
        self.session = aiohttp.ClientSession(connector=self.connector, loop=self.loop)

    async def post_server_count(self, id, token, guild_count, shard_count, shard_no):
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
        self.token = token
        await self.request('POST', f'{self.BASE}/bots/{id}/stats', json=payload)

    async def get_server_count(self, id):
        scount = await self.request('GET', f'{self.BASE}/bots/{id}/stats')
        return scount['server_count']

    async def get_upvote_count(self, id):
        ucount = await self.request('GET', f'{self.BASE}/bots/{id}')
        return ucount['points']

    async def get_upvote_info(self, id, token, onlyids):
        self.token = token
        if onlyids is True:
            return await self.request('GET', f'{self.BASE}/bots/{id}/votes?onlyids=true')
        else:
            return await self.request('GET', f'{self.BASE}/bots/{id}/votes')

    async def get_bot_info(self, id):
        return await self.request('GET', f'{self.BASE}/bots/{id}/stats')

    async def get_bots(self, limit, offset):
        return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}')

    async def get_user(self, id):
        return await self.request('GET', f'{self.BASE}/users/{id}')


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)
