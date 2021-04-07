# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2021 Assanali Mukhanov

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

import logging
from typing import Callable, Dict, Optional, Union

import aiohttp
import discord
from aiohttp import web

log = logging.getLogger(__name__)


class WebhookManager:
    """
    This class is used as a manager for the Top.gg webhook.

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

    def dbl_webhook(self, route: str, auth_key: str):
        """Helper method that configures a route that listens to bot votes.

        Parameters
        ----------
        route: str
            The route to use for bot votes.
        auth_key: str
            The Authorization key that will be used to verify the incoming requests.
        """
        self._webhooks["dbl"] = {
            "route": route or "/dbl",
            "auth" : auth_key or "",
            "func" : self._bot_vote_handler
        }
        return self

    def dsl_webhook(self, route: str, auth_key: str):
        """Helper method that configures a route that listens to server votes.

        Parameters
        ----------
        route: str
            The route to use for server votes.
        auth_key: str
            The Authorization key that will be used to verify the incoming requests.
        """
        self._webhooks["dsl"] = {
            "route": route or "/dsl",
            "auth" : auth_key or "",
            "func" : self._guild_vote_handler
        }
        return self

    async def _bot_vote_handler(self, request: aiohttp.web.Request):
        data = await request.json()
        auth = request.headers.get("Authorization", "")
        if auth == self._webhooks["dbl"]["auth"]:
            self.bot.dispatch("dbl_vote", data)
            return web.Response(status=200, text="OK")
        return web.Response(status=401, text="Unauthorized")

    async def _guild_vote_handler(self, request: aiohttp.web.Request):
        data = await request.json()
        auth = request.headers.get("Authorization", "")
        if auth == self._webhooks["dsl"]["auth"]:
            self.bot.dispatch("dsl_vote", data)
            return web.Response(status=200, text="OK")
        return web.Response(status=401, text="Unauthorized")

    async def run(self, port: int):
        """Runs the webhook.

        Parameters
        ----------
        port: int
            The port to run the webhook on.
        """
        for webhook in self._webhooks:
            self.__app.router.add_post(self._webhooks[webhook]["route"], self._webhooks[webhook]["func"])
        runner = web.AppRunner(self.__app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', port)
        await self._webserver.start()
        self._is_closed = False

    @property
    def webserver(self) -> Optional[web.TCPSite]:
        """Returns the internal webserver that handles webhook requests.

        Returns
        --------
        Optional[:class:`aiohttp.web.TCPSite`]
            The internal webserver if it exists.
        """
        return getattr(self, '_webserver', None)

    async def close(self):
        """Stop the webhook."""
        await self._webserver.stop()
        self._is_closed = True
