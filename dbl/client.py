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
import logging
from aiohttp import web

from .http import HTTPClient

log = logging.getLogger(__name__)


class DBLClient:
    """Represents a client connection that connects to discordbots.org.
    This class is used to interact with the DBL API.

    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ==========

    token :
        An API Token

    bot :
        An instance of a discord.py Bot or Client object
    **loop : Optional[event loop].
        The `event loop`_ to use for asynchronous operations.
        Defaults to ``bot.loop``.
    **session : Optional
        The `aiohttp session`_ to use for requests to the API.
    **webhook_auth: Optional
        The string for Authorization you set on the site for verification.
    **webhook_path: Optional
        The path for the webhook request.
    **webhook_port: Optional
        The port to run the webhook on. Will activate webhook when set.
    """

    def __init__(self, bot, token, **kwargs):
        self.bot = bot
        self.bot_id = None
        self.loop = kwargs.get('loop', bot.loop)
        self.autopost = kwargs.get('autopost')
        self.webhook_port = kwargs.get('webhook_port')
        self.webhook_auth = kwargs.get('webhook_auth', '')
        self.webhook_path = kwargs.get('webhook_path', '/dblwebhook')
        self.http = HTTPClient(token, loop=self.loop, session=kwargs.get('session'))
        self._is_closed = False
        if self.webhook_port:
            self.task2 = self.loop.create_task(self.webhook())
        if self.autopost:
            self.autopost_task = self.loop.create_task(self._auto_post())

    async def _ensure_bot_user(self):
        await self.bot.wait_until_ready()
        if self.bot_id is None:
            self.bot_id = self.bot.user.id

    async def _auto_post(self):
        await self._ensure_bot_user()
        while not self.bot.is_closed():
            await self.post_guild_count()
            self.bot.dispatch('guild_post')
            await asyncio.sleep(1800)

    def guild_count(self):
        """Gets the guild count from the Client/Bot object"""
        return len(self.bot.guilds)

    async def get_weekend_status(self):
        """This function is a coroutine.

        Gets weekend status from discordbots.org

        Returns
        =======

        weekend status: bool
            The boolean value of weekend status.
        """
        await self._ensure_bot_user()
        data = await self.http.get_weekend_status()
        return data['is_weekend']

    async def post_guild_count(
            self,
            shard_count: int = None,
            shard_no: int = None
    ):
        """This function is a coroutine.

        Posts your bot's guild count to discordbots.org

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Parameters
        ==========

        shard_count: int[Optional]
            The total number of shards.
        shard_no: int[Optional]
            The index of the current shard. DBL uses `0 based indexing`_ for shards.
        """
        await self._ensure_bot_user()
        await self.http.post_guild_count(self.bot_id, self.guild_count(), shard_count, shard_no)

    async def get_guild_count(self, bot_id: int = None):
        """This function is a coroutine.

        Gets a guild count from discordbots.org

        Parameters
        ==========

        bot_id: int[Optional]
            ID of the bot you want to lookup.
            Defaults to the discord.py Bot/Client provided in Client init.

        Returns
        =======

        stats: dict
            The guild count and shards of a bot.
            The date object is returned in a datetime.datetime object.
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_guild_count(bot_id)

    async def get_bot_upvotes(self):
        """This function is a coroutine.

        Gets information about last 1000 votes for your bot on discordbots.org

        .. note::

            This API endpoint is available to the owner of the bot only.

        Returns
        =======

        users: list
            Users who upvoted your bot.

        """
        await self._ensure_bot_user()
        return await self.http.get_bot_upvotes(self.bot_id)

    async def get_bot_info(self, bot_id: int = None):
        """This function is a coroutine.

        Gets information about a bot from discordbots.org

        Parameters
        ==========

        bot_id: int[Optional]
            ID of the bot you want to lookup.

        Returns
        =======

        bot info: dict
            Information on the bot you looked up.
            https://discordbots.org/api/docs#bots
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_bot_info(bot_id)

    async def get_bots(self, limit: int = 50, offset: int = 0, sort: str = None, search: dict = None, fields: list = None):
        """This function is a coroutine.

        Gets information about listed bots on discordbots.org

        Parameters
        ==========

        limit: int[Optional]
            The number of results you want to lookup. Defaults to 50. Max 500.
        offset: int[Optional]
            The amount of bots to skip. Defaults to 0.
        sort: str[Optional]
            The field to sort by. Prefix with ``-`` to reverse the order.
        search: dict[Optional]
            The search data.
        fields: list[Optional]
            Fields to output.

        Returns
        =======

        bots: dict
            Returns info on the bots on DBL.
            https://discordbots.org/api/docs#bots
        """
        sort = sort or "" # weird but works
        search = search or {}
        fields = fields or []
        await self._ensure_bot_user()
        return await self.http.get_bots(limit, offset, sort, search, fields)

    async def get_user_info(self, user_id: int):
        """This function is a coroutine.

        Gets information about a user on discordbots.org

        Parameters
        ==========

        user_id: int
            ID of the user you wish to lookup.

        Returns
        =======

        user data: dict
            Info about the user.
            https://discordbots.org/api/docs#users
        """
        await self._ensure_bot_user()
        return await self.http.get_user_info(user_id)

    async def get_user_vote(self, user_id: int):
        """This function is a coroutine.

        Gets information about the user's upvote for your bot on discordbots.org

        Parameters
        ==========

        user_id: int
            ID of the user you wish to lookup.

        Returns
        =======

        vote status: bool
            Info about the user's upvote.
        """
        await self._ensure_bot_user()
        data = await self.http.get_user_vote(self.bot_id, user_id)
        return bool(data['voted'])

    async def generate_widget_large(
            self,
            bot_id: int = None,
            top: str = '2C2F33',
            mid: str = '23272A',
            user: str = 'FFFFFF',
            cert: str = 'FFFFFF',
            data: str = 'FFFFFF',
            label: str = '99AAB5',
            highlight: str = '2C2F33'
    ):
        """This function is a coroutine.

        Generates a custom large widget. Do not add `#` to the color codes (e.g. #FF00FF become FF00FF).

        Parameters
        ==========

        bot_id: int
            ID of the bot you wish to make a widget for.
        top: str
            The hex color code of the top bar.
        mid: str
            The hex color code of the main section.
        user: str
            The hex color code of the username text.
        cert: str
            The hex color code of the certified text (if applicable).
        data: str
            The hex color code of the statistics (numbers only e.g. 44) of the bot.
        label: str
            The hex color code of the description (text e.g. guild count) of the statistics.
        highlight: str
            The hex color code of the data boxes.

        Returns
        =======

        URL of the widget: str
        """
        await self._ensure_bot_user()
        url = 'https://discordbots.org/api/widget/{0}.png?topcolor={1}&middlecolor={2}&usernamecolor={3}&certifiedcolor={4}&datacolor={5}&labelcolor={6}&highlightcolor={7}'
        if bot_id is None:
            bot_id = self.bot_id
        url = url.format(bot_id, top, mid, user, cert, data, label, highlight)
        return url

    async def get_widget_large(self, bot_id: int = None):
        """This function is a coroutine.

        Generates the default large widget.

        Parameters
        ==========

        bot_id: int
            ID of the bot you wish to make a widget for.

        Returns
        =======

        URL of the widget: str
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/{0}.png'.format(bot_id)
        return url

    async def generate_widget_small(
            self,
            bot_id: int = None,
            avabg: str = '2C2F33',
            lcol: str = '23272A',
            rcol: str = '2C2F33',
            ltxt: str = 'FFFFFF',
            rtxt: str = 'FFFFFF'
    ):
        """This function is a coroutine.

        Generates a custom large widget. Do not add `#` to the color codes (e.g. #FF00FF become FF00FF).

        Parameters
        ==========

        bot_id: int
            ID of the bot you wish to make a widget for.
        avabg: str
            The hex color code of the background of the avatar (if the avatar has transparency).
        lcol: str
            The hex color code of the left background color.
        rcol: str
            The hex color code of the right background color.
        ltxt: str
            The hex color code of the left text.
        rtxt: str
            The hex color code of the right text.

        Returns
        =======

        URL of the widget: str
        """
        await self._ensure_bot_user()
        url = 'https://discordbots.org/api/widget/lib/{0}.png?avatarbg={1}&lefttextcolor={2}&righttextcolor={3}&leftcolor={4}&rightcolor={5}'
        if bot_id is None:
            bot_id = self.bot_id
        url = url.format(bot_id, avabg, ltxt, rtxt, lcol, rcol)
        return url

    async def get_widget_small(self, bot_id: int = None):
        """This function is a coroutine.

        Generates the default small widget.

        Parameters
        ==========

        bot_id: int
            ID of the bot you wish to make a widget for.

        Returns
        =======

        URL of the widget: str
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/lib/{0}.png'.format(bot_id)
        return url

    async def webhook(self):
        async def vote_handler(request):
            req_auth = request.headers.get('Authorization')
            if self.webhook_auth == req_auth:
                data = await request.json()
                if data.get('type') == 'upvote':
                    event_name = 'dbl_vote'
                elif data.get('type') == 'test':
                    event_name = 'dbl_test'
                self.bot.dispatch(event_name, data)
                return web.Response()
            else:
                return web.Response(status=401)

        app = web.Application(loop=self.loop)
        app.router.add_post(self.webhook_path, vote_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', self.webhook_port)
        await self._webserver.start()

    async def close(self):
        """This function is a coroutine.

        Closes all connections."""
        if self._is_closed:
            return
        else:
            await self._webserver.stop()
            await self.http.close()
            if self.webhook_port:
                self.task2.cancel()
            if self.autopost:
                self.autopost_task.cancel()
            self._is_closed = True