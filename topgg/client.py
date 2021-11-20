# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2021 Assanali Mukhanov

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import logging
import typing as t

import aiohttp

from . import errors, types
from .autopost import AutoPoster
from .data import DataContainerMixin
from .http import HTTPClient

log = logging.getLogger("topgg.client")


class DBLClient(DataContainerMixin):
    """Represents a client connection that connects to Top.gg.
    This class is used to interact with the Top.gg API.

    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    token: str
        Your bot's Top.gg API Token.
    default_bot_id: Optional[int]
        The default bot_id. You can override this by passing it when calling a method.
    session: :class:`aiohttp.ClientSession`
        An `aiohttp session`_ to use for requests to the API.
    """

    __slots__ = ("http", "default_bot_id", "_token", "_is_closed")
    http: HTTPClient

    def __init__(
        self,
        token: str,
        *,
        default_bot_id: t.Optional[int] = None,
        session: t.Optional[aiohttp.ClientSession] = None,
    ) -> None:
        super().__init__()
        self._token = token
        self.default_bot_id = default_bot_id
        self._is_closed = False
        if session is not None:
            self.http = HTTPClient(token, session=session)

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    async def _ensure_session(self) -> None:
        if not hasattr(self, "http"):
            self.http = HTTPClient(self._token, session=None)

    def _validate_and_get_bot_id(self, bot_id: t.Optional[int], /) -> int:
        bot_id = bot_id or self.default_bot_id
        if bot_id is None:
            raise TypeError("bot_id or default_bot_id is unset.")

        return bot_id

    async def get_weekend_status(self) -> bool:
        """This function is a coroutine.

        Gets weekend status from Top.gg.

        Returns
        -------
        weekend status: bool
            The boolean value of weekend status.
        """
        await self._ensure_session()
        data = await self.http.get_weekend_status()
        return data["is_weekend"]

    @t.overload
    async def post_guild_count(self, stats: types.StatsWrapper, /) -> None:
        ...

    @t.overload
    async def post_guild_count(
        self,
        *,
        guild_count: t.Union[int, t.List[int]],
        shard_count: t.Optional[int] = None,
        shard_id: t.Optional[int] = None,
    ) -> None:
        ...

    async def post_guild_count(
        self,
        stats: t.Any = None,
        *,
        guild_count: t.Any = None,
        shard_count: t.Any = None,
        shard_id: t.Any = None,
    ) -> None:
        """This function is a coroutine.

        Posts your bot's guild count and shards info to Top.gg.

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Parameters
        ----------
        stats: :obj:`~.types.StatsWrapper`
            An instance of StatsWrapper containing guild_count, shard_count, and shard_id.
        guild_count: Optional[Union[int, List[int]]]
            Number of guilds the bot is in. Applies the number to a shard instead if shards are specified.
            If not specified, length of provided client's property `.guilds` will be posted.
        shard_count: Optional[int]
            The total number of shards.
        shard_id: Optional[int]
            The index of the current shard. Top.gg uses `0 based indexing`_ for shards.
        """
        if stats:
            guild_count = stats.guild_count
            shard_count = stats.shard_count
            shard_id = stats.shard_id
        elif guild_count is None:
            raise TypeError("stats or guild_count must be provided.")
        await self._ensure_session()
        await self.http.post_guild_count(guild_count, shard_count, shard_id)

    async def get_guild_count(
        self, bot_id: t.Optional[int] = None, /
    ) -> types.BotStatsData:
        """This function is a coroutine.

        Gets a bot's guild count and shard info from Top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot you want to look up. Defaults to the provided Client object.

        Returns
        -------
        stats: :obj:`~.types.BotStatsData`
            The guild count and shards of a bot on Top.gg.
        """
        bot_id = self._validate_and_get_bot_id(bot_id)
        await self._ensure_session()
        response = await self.http.get_guild_count(bot_id)
        return types.BotStatsData(**response)

    async def get_bot_votes(self) -> t.List[types.BriefUserData]:
        """This function is a coroutine.

        Gets information about last 1000 votes for your bot on Top.gg.

        .. note::
            This API endpoint is only available to the bot's owner.

        Returns
        -------
        users: List[:obj:`~.types.BriefUserData`]
            Users who voted for your bot.
        """
        if not self.default_bot_id:
            raise errors.ClientException(
                "you must set default_bot_id when constructing the client."
            )
        await self._ensure_session()
        response = await self.http.get_bot_votes(self.default_bot_id)
        return [types.BriefUserData(**user) for user in response]

    async def get_bot_info(self, bot_id: t.Optional[int] = None, /) -> types.BotData:
        """This function is a coroutine.

        Gets information about a bot from Top.gg.

        Parameters
        ----------
        bot_id: int
            ID of the bot to look up. Defaults to the provided Client object.

        Returns
        -------
        bot info: :obj:`~.types.BotData`
            Information on the bot you looked up. Returned data can be found
            `here <https://docs.top.gg/api/bot/#bot-structure>`_.
        """
        bot_id = self._validate_and_get_bot_id(bot_id)
        await self._ensure_session()
        response = await self.http.get_bot_info(bot_id)
        return types.BotData(**response)

    async def get_bots(
        self,
        limit: int = 50,
        offset: int = 0,
        sort: t.Optional[str] = None,
        search: t.Optional[t.Dict[str, t.Any]] = None,
        fields: t.Optional[t.List[str]] = None,
    ) -> types.DataDict[str, t.Any]:
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
        bots: :obj:`~.types.DataDict`
            Info on bots that match the search query on Top.gg.
        """
        sort = sort or ""
        search = search or {}
        fields = fields or []
        await self._ensure_session()
        response = await self.http.get_bots(limit, offset, sort, search, fields)
        response["results"] = [
            types.BotData(**bot_data) for bot_data in response["results"]
        ]
        return types.DataDict(**response)

    async def get_user_info(self, user_id: int, /) -> types.UserData:
        """This function is a coroutine.

        Gets information about a user on Top.gg.

        Parameters
        ----------
        user_id: int
            ID of the user to look up.

        Returns
        -------
        user data: :obj:`~.types.UserData`
            Information about a Top.gg user.
        """
        await self._ensure_session()
        response = await self.http.get_user_info(user_id)
        return types.UserData(**response)

    async def get_user_vote(self, user_id: int, /) -> bool:
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
        if not self.default_bot_id:
            raise errors.ClientException(
                "you must set default_bot_id when constructing the client."
            )

        await self._ensure_session()
        data = await self.http.get_user_vote(self.default_bot_id, user_id)
        return bool(data["voted"])

    def generate_widget(self, *, options: types.WidgetOptions) -> str:
        """
        Generates a Top.gg widget from the provided :obj:`~.types.WidgetOptions` object.

        Parameters
        ----------
        options: :obj:`~.types.WidgetOptions`
            A :obj:`~.types.WidgetOptions` object containing widget parameters.

        Returns
        -------
        widget: str
            Generated widget URL.
        """
        if not isinstance(options, types.WidgetOptions):
            raise errors.ClientException(
                "options argument passed to generate_widget must be of type WidgetOptions"
            )

        bot_id = options.id or self.default_bot_id
        if bot_id is None:
            raise errors.ClientException("bot_id or default_bot_id is unset.")

        widget_query = f"noavatar={str(options.noavatar).lower()}"
        for key, value in options.colors.items():
            widget_query += f"&{key.lower()}{'' if key.lower().endswith('color') else 'color'}={value:x}"
        widget_format = options.format
        widget_type = f"/{options.type}" if options.type else ""

        url = f"""https://top.gg/api/widget{widget_type}/{bot_id}.{widget_format}?{widget_query}"""
        return url

    async def close(self) -> None:
        """This function is a coroutine.

        Closes all connections.
        """
        if self.is_closed:
            return

        if hasattr(self, "http"):
            await self.http.close()

        self._is_closed = True

    def autopost(self) -> AutoPoster:
        """
        Returns a helper instance for auto-posting.

        Returns
        -------
        autoposter: :obj:`~.autopost.AutoPoster`
            An instance of AutoPoster.
        """
        return AutoPoster(self)
