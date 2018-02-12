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
from datetime import datetime

import aiohttp

from . import __version__
from .errors import *


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
        self.session = kwargs.get('session') or aiohttp.ClientSession(loop=kwargs.get('loop'))

        user_agent = 'DBL-Python-Library (https://github.com/DiscordBotList/DBL-Python-Library {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, method, url, **kwargs):
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

        # add auth like above??
        async with self.session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            try:
                data = json.loads(text)
            except (json.decoder.JSONDecodeError, ValueError):
                data = {'message': text} if text else None

            if 300 > resp.status >= 200:
                return data
            elif resp.status == 400:
                raise HTTPException(resp, data.pop('message', 'unknown'))
            elif resp.status == 401:
                raise Unauthorized(resp, data.pop('message', 'unknown'))
            elif resp.status == 403:
                raise Forbidden(resp, data.pop('message', 'unknown'))
            elif resp.status == 404:
                raise NotFound(resp, data.pop('message', 'unknown'))
            elif resp.status == 429:
                raise RateLimited(resp, data.pop('message', 'unknown'))
            else:
                raise HTTPException(resp, data.pop('message', 'Unknown error'))

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

    async def get_upvote_info(self, bot_id, onlyids):
        '''Gets the upvote information of the given Bot ID'''
        if onlyids is True:
            return await self.request('GET', f'{self.BASE}/bots/{bot_id}/votes?onlyids=true')
        return await self.request('GET', f'{self.BASE}/bots/{bot_id}/votes')

    async def get_bots(self, limit, offset):
        return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}')

    # async def get_bots(self, limit, offset, query):
    #     return await self.request('GET', f'{self.BASE}/bots?limit={limit}&offset={offset}&search={query}')

    async def get_user_info(self, user_id):
        return await self.request('GET', f'{self.BASE}/users/{user_id}')


def to_json(obj):
    if json.__name__ == 'ujson':
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)
