# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2020 Assanali Mukhanov

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

from typing import Callable, Dict, Union

import aiohttp
import discord
from aiohttp import web


class WebhookManager:
    """
    This class is used as a manager for DBL and DSL webhooks.

    Parameters
    ----------

    bot: discord.Client
        The Client object that will be utilized by this manager's webhook(s) to emit events.
    """
    __app: web.Application
    _webhooks: Dict[str, Dict[str, Union[str, Callable]]]
    _webserver: web.TCPSite
    _is_closed: bool

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self._webhooks = {}
        self.__app = web.Application()
        self._is_closed = False

    def dbl_webhook(self, path: str, auth_key: str):
        if not path:
            path = "/dblwebhook"
        self._webhooks["dbl"] = {
            "path": path,
            "auth": auth_key,
            "func": self._bot_vote_handler
        }

    def dsl_webhook(self, path: str, auth_key: str):
        if not path:
            path = "/dslwebhook"
        self._webhooks["dsl"] = {
            "path": path,
            "auth": auth_key,
            "func": self._guild_vote_handler
        }

    async def _bot_vote_handler(self, request: aiohttp.web.Request):
        data = await request.json()
        self.bot.dispatch("dbl_vote", data)
        return web.Response(status=200)

    async def _guild_vote_handler(self, request: aiohttp.web.Request):
        data = await request.json()
        self.bot.dispatch("dsl_vote", data)
        return web.Response(status=200)

    async def run(self, port: int):
        for webhook in self._webhooks:
            self.__app.router.add_post(self._webhooks[webhook]["path"], self._webhooks[webhook]["func"])
        runner = web.AppRunner(self.__app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', port)
        await self._webserver.start()
        self._is_closed = False

    async def close(self):
        await self._webserver.stop()
        self._is_closed = True
