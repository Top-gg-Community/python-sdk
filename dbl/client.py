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

import asyncio
import logging
from asyncio.tasks import Task
from typing import List, Optional, Union

import discord

from . import errors
from .http import HTTPClient

log = logging.getLogger(__name__)


class DBLClient:
    """Represents a client connection that connects to top.gg.
    This class is used to interact with the top.gg API.

    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    token: str
        Your bot's top.gg API Token.
    bot: discord.Client
        An instance of a discord.py Client object.
    autopost: Optional[bool]
        Whether to automatically post bot's guild count every 30 minutes.
        This will dispatch :meth:`on_guild_post`.
    **post_shard_count: Optional[bool]
        Whether to post the shard count on autopost.
        Defaults to False.
    **session: Optional[aiohttp session]
        An `aiohttp session`_ to use for requests to the API.
    **loop: Optional[event loop]
        An `event loop`_ to use for asynchronous operations.
        Defaults to ``bot.loop``.
    """

    bot: discord.Client
    bot_id: Optional[int]
    loop: asyncio.AbstractEventLoop
    autopost: Optional[bool]
    _post_shard_count: Optional[bool]
    _is_closed: bool
    http: HTTPClient
    autopost_task: Task
    autopost_timer: int

    def __init__(self, bot: discord.Client, token: str, autopost: bool = False,autopost_timer: int = 1800, **kwargs):
        self.bot = bot
        self.bot_id = None
        self.loop = kwargs.get("loop", bot.loop)
        self.autopost = autopost
        self._post_shard_count = kwargs.get("post_shard_count", False)
        self.http = HTTPClient(token, loop=self.loop, session=kwargs.get("session"))
        self._is_closed = False
        self.autopost_timer = autopost_timer

        if self.autopost:
            self.autopost_task = self.loop.create_task(self._auto_post())

    async def _ensure_bot_user(self):
        await self.bot.wait_until_ready()
        if self.bot_id is None:
            self.bot_id = self.bot.user.id

    async def _auto_post(self,time=autopost_timer):
        await self._ensure_bot_user()
        while not self.bot.is_closed():
            try:
                await self.post_guild_count(shard_count=self.bot.shard_count
                                            if self._post_shard_count
                                            else None)
                event_name = 'guild_post'
                log.debug('Dispatching %s event', event_name)
                self.bot.dispatch(event_name)
            except errors.HTTPException:
                pass
            await asyncio.sleep(time)

    @property
    def guild_count(self) -> int:
        """Gets the guild count from the provided Client object."""
        return len(self.bot.guilds)

    async def get_weekend_status(self):
        """This function is a coroutine.

        Gets weekend status from top.gg.

        Returns
        -------
        weekend status: bool
            The boolean value of weekend status.
        """
        data = await self.http.get_weekend_status()
        return data['is_weekend']

    async def post_guild_count(self, guild_count: Union[int, List[int]] = None, shard_count: int = None,
                               shard_id: int = None):
        """This function is a coroutine.

        Posts your bot's guild count and shards info to top.gg.

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Parameters
        ----------
        guild_count: Optional[Union[int, List[int]]]
            Number of guilds the bot is in. Applies the number to a shard instead if shards are specified.
            If not specified, length of provided client's property `.guilds` will be posted.
        shard_count: Optional[int]
            The total number of shards.
        shard_id: Optional[int]
            The index of the current shard. top.gg uses `0 based indexing`_ for shards.
        """
        await self._ensure_bot_user()
        if guild_count is None:
            guild_count = self.guild_count
        await self.http.post_guild_count(guild_count, shard_count, shard_id)

    async def get_guild_count(self, bot_id: int = None) -> dict:
        """This function is a coroutine.

        Gets a bot's guild count and shard info from top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot you want to look up. Defaults to the provided Client object.

        Returns
        -------
        stats: dict
            The guild count and shards of a bot on top.gg. The date field is returned in a datetime.datetime object.
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_guild_count(bot_id)

    async def get_bot_votes(self) -> List[str]:
        """This function is a coroutine.

        Gets information about last 1000 votes for your bot on top.gg.

        .. note::

            This API endpoint is only available to the bot's owner.

        Returns
        -------
        users: List[str]
            Users who voted for your bot.
        """
        await self._ensure_bot_user()
        return await self.http.get_bot_votes(self.bot_id)

    async def get_bot_info(self, bot_id: int = None) -> dict:
        """This function is a coroutine.

        Gets information about a bot from top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot to look up. Defaults to the provided Client object.

        Returns
        -------
        bot info: dict
            Information on the bot you looked up. Returned data can be found at https://top.gg/api/docs#bots
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_bot_info(bot_id)

    async def get_bots(self, limit: int = 50, offset: int = 0, sort: str = None, search: dict = None,
                       fields: list = None) -> dict:
        """This function is a coroutine.

        Gets information about listed bots on top.gg.

        Parameters
        ----------
        limit: int
            The number of results to look up. Defaults to 50. Max 500 allowed.
        offset: int
            The amount of bots to skip. Defaults to 0.
        sort: str
            The field to sort by. Prefix with ``-`` to reverse the order.
        search: dict
            The search data.
        fields: List[dict]
            Fields to output.

        Returns
        -------
        bots: dict
            Returns info on the bots on top.gg.
            https://top.gg/api/docs#bots
        """
        sort = sort or ""
        search = search or {}
        fields = fields or []
        return await self.http.get_bots(limit, offset, sort, search, fields)

    async def get_user_info(self, user_id: int) -> dict:
        """This function is a coroutine.

        Gets information about a user on top.gg.

        Parameters
        ----------
        user_id: int
            ID of the user to look up.

        Returns
        -------
        user data: dict
            Info about the user.
            https://top.gg/api/docs#users
        """
        return await self.http.get_user_info(user_id)

    async def get_user_vote(self, user_id: int) -> bool:
        """This function is a coroutine.

        Gets information about a user's vote for your bot on top.gg.

        Parameters
        ----------
        user_id: int
            ID of the user.

        Returns
        -------
        vote status: bool
            Info about the user's vote.
        """
        await self._ensure_bot_user()
        data = await self.http.get_user_vote(self.bot_id, user_id)
        return bool(data['voted'])

    async def generate_widget(self, options: dict = None) -> str:
        """This function is a coroutine.

        Generates a top.gg widget from provided options.

        Parameters
        ----------
        options: dict
            A dictionary consisting of options. For further information, see the :ref:`Widgets` section.

        Returns
        -------
        widget: str
            Generated widget URL.
        """
        bot_id = options.get("id")

        if bot_id is None:
            await self._ensure_bot_user()
            bot_id = self.bot_id
        opts = {
            "format"  : options.get("format") or "png",
            "type"    : options.get("type") or "",
            "noavatar": options.get("noavatar") or False,
            "colors"  : options.get("colors") or options.get("colours") or {}
        }

        widget_query = f"noavatar={str(opts['noavatar']).lower()}"
        for key, value in opts['colors'].items():
            widget_query += f"&{key.lower()}{'' if key.lower().endswith('color') else 'color'}={value:x}"
        widget_format = opts['format']
        widget_type = f"/{opts['type']}" if opts['type'] else ""

        url = f"""https://top.gg/api/widget{widget_type}/{bot_id}.{widget_format}?{widget_query}"""
        return url

    async def close(self):
        """This function is a coroutine.

        Closes all connections.
        """
        if self._is_closed:
            return
        else:
            await self.http.close()
            if self.autopost:
                self.autopost_task.cancel()
            self._is_closed = True
