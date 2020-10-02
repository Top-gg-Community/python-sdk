from typing import Dict, Optional

import aiohttp
import discord
from aiohttp import web


class WebhookManager:
    """This class is used as a manager for DBL and DSL webhooks.

    Parameters
    ==========

    port: int
        """
    _webhooks: Dict[str, Dict[str, str]]
    port: Optional[int]

    def __init__(self, bot: discord.Client, port: Optional[int] = None):
        self.bot = bot
        self._webhooks = {}
        self.port = port
        self.__app = web.Application()

    def dbl_webhook(self, path: str, auth_key: str):
        if not path:
            path = "/dblwebhook"
        self._webhooks["dbl"] = {
            "path": path,
            "auth": auth_key
        }

    def dsl_webhook(self, path: str, auth_key: str):
        if not path:
            path = "/dslwebhook"
        self._webhooks["dsl"] = {
            "path": path,
            "auth": auth_key
        }

    @staticmethod
    async def _vote_or_test(request):
        data = await request.json()
        if data.get('type') == 'upvote':
            event_name = 'vote'
        elif data.get('type') == 'test':
            event_name = 'test'
        else:
            return
        return event_name

    async def dbl_vote_handler(self, request: aiohttp.web.Request):
        data = await request.json()
        event_type = await self._vote_or_test(request)
        self.bot.dispatch("dbl_{}".format(event_type), data)
        return web.Response(status=200)

    async def dsl_vote_handler(self, request):
        data = await request.json()
        event_type = await self._vote_or_test(request)
        self.bot.dispatch("dsl_{}".format(event_type), data)
        return web.Response(status=200)

    async def run(self):
        for webhook in self._webhooks:
            if webhook == "dbl":
                func = self.dbl_vote_handler
            else:  # dsl
                func = self.dsl_vote_handler
            self.__app.router.add_post(self._webhooks[webhook]["path"], func)
        runner = web.AppRunner(self.__app)
        await runner.setup()
        _webserver = web.TCPSite(runner, '0.0.0.0', self.port)
        await _webserver.start()
