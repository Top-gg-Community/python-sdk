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

import asyncio
import logging
import sys
import traceback
from asyncio.tasks import Task
from contextlib import suppress
from typing import Any, Dict, List, Optional, Union

import discord
from discord.ext.commands.bot import BotBase

# if sys.version_info >= (3, 8):
#     from typing import TypedDict
# else:
#     from typing_extensions import TypedDict
from . import errors, types
from .http import HTTPClient

log = logging.getLogger(__name__)


class DBLClient:
    """Represents a client connection that connects to Top.gg.
    This class is used to interact with the Top.gg API.

    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    bot: discord.Client
        An instance of a discord.py Client object.
    token: str
        Your bot's Top.gg API Token.
    autopost: bool
        Whether to automatically post bot's guild count every 30 minutes.
        This will dispatch :meth:`on_guild_post`.
    post_shard_count: bool
        Whether to post the shard count on autopost.
        Defaults to False.
    autopost_interval: Optional[int]
        Interval used by autopost to post server count automatically, measured in seconds. Defaults to 1800 (30
        minutes) if autopost is True, otherwise None.
    **session: :class:`aiohttp.ClientSession`
        An `aiohttp session`_ to use for requests to the API.
    """

    bot: discord.Client
    bot_id: Optional[int]
    loop: asyncio.AbstractEventLoop
    autopost: bool
    post_shard_count: bool
    _is_closed: bool
    http: HTTPClient
    autopost_task: Task
    autopost_interval: Optional[int]

    def __init__(
        self,
        bot: discord.Client,
        token: str,
        autopost: bool = False,
        post_shard_count: bool = False,
        autopost_interval: Optional[int] = None,
        **kwargs,
    ):
        self.bot = bot
        self.bot_id = None
        self.loop = bot.loop
        self.autopost = autopost
        self.post_shard_count = post_shard_count
        self.autopost_interval = autopost_interval
        self.http = HTTPClient(token, loop=self.loop, session=kwargs.get("session"))
        self._is_closed = False

        if not isinstance(self.autopost, bool):
            raise errors.ClientException("autopost must be of type bool")
        if not isinstance(self.post_shard_count, bool):
            raise errors.ClientException("post_shard_count must be of type bool")
        if self.autopost:
            if self.autopost_interval is None:
                self.autopost_interval = 1800
            if not isinstance(self.autopost_interval, int):
                raise errors.ClientException("autopost_interval must be of type int")
            if self.autopost_interval < 900:
                raise errors.ClientException(
                    "autopost_interval must be greater than or equal to 900 seconds (15 minutes)"
                )

            if not hasattr(self.bot, "on_autopost_error"):
                self.bot.on_autopost_error = self.on_autopost_error

            self.autopost_task = self.loop.create_task(self._auto_post())
        else:
            if self.post_shard_count:
                raise errors.ClientException(
                    "autopost must be activated if post_shard_count is passed"
                )
            if self.autopost_interval:
                raise errors.ClientException(
                    "autopost must be activated if autopost_interval is passed"
                )

    async def on_autopost_error(self, exception: Exception):
        # only print if there's no external autopost_error listeners.
        if isinstance(self.bot, BotBase) and self.bot.extra_events.get(
            "on_autopost_error"
        ):
            return

        print("Ignoring exception in auto post loop:", file=sys.stderr)
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )

    async def _ensure_bot_user(self):
        await self.bot.wait_until_ready()
        if self.bot_id is None:
            self.bot_id = self.bot.user.id

    async def _auto_post(self):
        await self._ensure_bot_user()
        while not self.bot.is_closed():
            try:
                log.debug(f"Attempting to post server count ({self.guild_count})")
                await self.post_guild_count(
                    shard_count=self.bot.shard_count if self.post_shard_count else None
                )
                event_name = "autopost_success"
                self.bot.dispatch(event_name)
            except Exception as e:
                event_name = "autopost_error"
                self.bot.dispatch(event_name, e)

                if isinstance(e, errors.Unauthorized):
                    raise

            await asyncio.sleep(self.autopost_interval)

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def guild_count(self) -> int:
        """Gets the guild count from the provided Client object."""
        return len(self.bot.guilds)

    async def get_weekend_status(self):
        """This function is a coroutine.

        Gets weekend status from Top.gg.

        Returns
        -------
        weekend status: bool
            The boolean value of weekend status.
        """
        data = await self.http.get_weekend_status()
        return data["is_weekend"]

    async def post_guild_count(
        self,
        guild_count: Optional[Union[int, List[int]]] = None,
        shard_count: Optional[int] = None,
        shard_id: Optional[int] = None,
    ):
        """This function is a coroutine.

        Posts your bot's guild count and shards info to Top.gg.

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Parameters
        ----------
        guild_count: Optional[Union[int, List[int]]]
            Number of guilds the bot is in. Applies the number to a shard instead if shards are specified.
            If not specified, length of provided client's property `.guilds` will be posted.
        shard_count: Optional[int]
            The total number of shards.
        shard_id: Optional[int]
            The index of the current shard. Top.gg uses `0 based indexing`_ for shards.
        """
        await self._ensure_bot_user()
        if guild_count is None:
            guild_count = self.guild_count
        await self.http.post_guild_count(guild_count, shard_count, shard_id)

    async def get_guild_count(self, bot_id: Optional[int] = None) -> types.BotStatsData:
        """This function is a coroutine.

        Gets a bot's guild count and shard info from Top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot you want to look up. Defaults to the provided Client object.

        Returns
        -------
        stats: :ref:`BotStatsData`
            The guild count and shards of a bot on Top.gg.
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        response = await self.http.get_guild_count(bot_id)
        return types.BotStatsData(**response)

    async def get_bot_votes(self) -> List[types.BriefUserData]:
        """This function is a coroutine.

        Gets information about last 1000 votes for your bot on Top.gg.

        .. note::
            This API endpoint is only available to the bot's owner.

        Returns
        -------
        users: List[:ref:`BriefUserData`]
            Users who voted for your bot.
        """
        await self._ensure_bot_user()
        response = await self.http.get_bot_votes(self.bot_id)
        return [types.BriefUserData(**user) for user in response]

    async def get_bot_info(self, bot_id: Optional[int] = None) -> types.BotData:
        """This function is a coroutine.

        Gets information about a bot from Top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot to look up. Defaults to the provided Client object.

        Returns
        -------
        bot info: :ref:`BotData`
            Information on the bot you looked up. Returned data can be found
            `here <https://docs.top.gg/api/bot/#bot-structure>`_.
        """
        await self._ensure_bot_user()
        if bot_id is None:
            bot_id = self.bot_id
        response = await self.http.get_bot_info(bot_id)
        return types.BotData(**response)

    async def get_bots(
        self,
        limit: int = 50,
        offset: int = 0,
        sort: str = None,
        search: Dict[str, Any] = None,
        fields: List[str] = None,
    ) -> Dict[str, Any]:
        """This function is a coroutine.

        Gets information about listed bots on Top.gg.

        Parameters
        ----------
        limit: int
            The number of results to look up. Defaults to 50. Max 500 allowed.
        offset: int
            The amount of bots to skip. Defaults to 0.
        sort: str
            The field to sort by. Prefix with ``-`` to reverse the order.
        search: Dict[str, Any]
            The search data.
        fields: List[str]
            Fields to output.

        Returns
        -------
        bots: dict
            Info on bots that match the search query on Top.gg.
        """
        sort = sort or ""
        search = search or {}
        fields = fields or []
        response = await self.http.get_bots(limit, offset, sort, search, fields)
        response["results"] = [
            types.BotData(**bot_data) for bot_data in response["results"]
        ]
        return response

    async def get_user_info(self, user_id: int) -> types.UserData:
        """This function is a coroutine.

        Gets information about a user on Top.gg.

        Parameters
        ----------
        user_id: int
            ID of the user to look up.

        Returns
        -------
        user data: :ref:`UserData`
            Information about a Top.gg user.
        """
        response = await self.http.get_user_info(user_id)
        return types.UserData(**response)

    async def get_user_vote(self, user_id: int) -> bool:
        """This function is a coroutine.

        Gets information about a user's vote for your bot on Top.gg.

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
        return bool(data["voted"])

    async def generate_widget(self, options: types.WidgetOptions) -> str:
        """This function is a coroutine.

        Generates a Top.gg widget from the provided :ref:`WidgetOptions` object.

        Parameters
        ----------
        options: :ref:`WidgetOptions`
            A :ref:`WidgetOptions` object containing widget parameters.

        Returns
        -------
        widget: str
            Generated widget URL.
        """
        if not isinstance(options, types.WidgetOptions):
            raise errors.ClientException(
                "options argument passed to generate_widget must be of type WidgetOptions"
            )
        bot_id = options.id

        if bot_id is None:
            await self._ensure_bot_user()
            bot_id = self.bot_id

        widget_query = f"noavatar={str(options.noavatar).lower()}"
        for key, value in options.colors.items():
            widget_query += f"&{key.lower()}{'' if key.lower().endswith('color') else 'color'}={value:x}"
        widget_format = options.format
        widget_type = f"/{options.type}" if options.type else ""

        url = f"""https://top.gg/api/widget{widget_type}/{bot_id}.{widget_format}?{widget_query}"""
        return url

    async def close(self):
        """This function is a coroutine.

        Closes all connections.
        """
        if self.is_closed:
            return
        else:
            await self.http.close()
            if self.autopost:
                self.autopost_task.cancel()
            self._is_closed = True

        with suppress(AttributeError):
            delattr(self.bot, "on_autopost_error")
