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

__all__ = ["DBLClient"]

import typing as t

import aiohttp

from . import errors, types
from .autopost import AutoPoster
from .data import DataContainerMixin
from .http import HTTPClient


class DBLClient(DataContainerMixin):
    """Represents a client connection that connects to Top.gg.

    This class is used to interact with the Top.gg API.

    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Args:
        token (:obj:`str`): Your bot's Top.gg API Token.

    Keyword Args:
        default_bot_id (:obj:`typing.Optional` [ :obj:`int` ])
            The default bot_id. You can override this by passing it when calling a method.
        session (:class:`aiohttp.ClientSession`)
            An `aiohttp session`_ to use for requests to the API.
        **kwargs:
            Arbitrary kwargs to be passed to :class:`aiohttp.ClientSession` if session was not provided.
    """

    __slots__ = ("http", "default_bot_id", "_token", "_is_closed", "_autopost")
    http: HTTPClient

    def __init__(
        self,
        token: str,
        *,
        default_bot_id: t.Optional[int] = None,
        session: t.Optional[aiohttp.ClientSession] = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__()
        self._token = token
        self.default_bot_id = default_bot_id
        self._is_closed = False
        if session is not None:
            self.http = HTTPClient(token, session=session)
        self._autopost: t.Optional[AutoPoster] = None

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    async def _ensure_session(self) -> None:
        if self.is_closed:
            raise errors.ClientStateException("client has been closed.")

        if not hasattr(self, "http"):
            self.http = HTTPClient(self._token, session=None)

    def _validate_and_get_bot_id(self, bot_id: t.Optional[int]) -> int:
        bot_id = bot_id or self.default_bot_id
        if bot_id is None:
            raise errors.ClientException("bot_id or default_bot_id is unset.")

        return bot_id

    async def get_weekend_status(self) -> bool:
        """Gets weekend status from Top.gg.

        Returns:
            :obj:`bool`: The boolean value of weekend status.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        await self._ensure_session()
        data = await self.http.get_weekend_status()
        return data["is_weekend"]

    @t.overload
    async def post_guild_count(self, stats: types.StatsWrapper) -> None:
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
        """Posts your bot's guild count and shards info to Top.gg.

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Warning:
            You can't provide both args and kwargs at once.

        Args:
            stats (:obj:`~.types.StatsWrapper`)
                An instance of StatsWrapper containing guild_count, shard_count, and shard_id.

        Keyword Arguments:
            guild_count (:obj:`typing.Optional` [:obj:`typing.Union` [ :obj:`int`, :obj:`list` [ :obj:`int` ]]])
                Number of guilds the bot is in. Applies the number to a shard instead if shards are specified.
                If not specified, length of provided client's property `.guilds` will be posted.
            shard_count (:obj:`.typing.Optional` [ :obj:`int` ])
                The total number of shards.
            shard_id (:obj:`.typing.Optional` [ :obj:`int` ])
                The index of the current shard. Top.gg uses `0 based indexing`_ for shards.

        Raises:
            TypeError
                If no argument is provided.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
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
        self, bot_id: t.Optional[int] = None
    ) -> types.BotStatsData:
        """Gets a bot's guild count and shard info from Top.gg.

        Args:
            bot_id (int)
                ID of the bot you want to look up. Defaults to the provided Client object.

        Returns:
            :obj:`~.types.BotStatsData`:
                The guild count and shards of a bot on Top.gg.

        Raises:
            :obj:`~.errors.ClientException`
                If neither bot_id or default_bot_id was set.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        bot_id = self._validate_and_get_bot_id(bot_id)
        await self._ensure_session()
        response = await self.http.get_guild_count(bot_id)
        return types.BotStatsData(**response)

    async def get_bot_votes(self) -> t.List[types.BriefUserData]:
        """Gets information about last 1000 votes for your bot on Top.gg.

        Note:
            This API endpoint is only available to the bot's owner.

        Returns:
            :obj:`list` [ :obj:`~.types.BriefUserData` ]:
                Users who voted for your bot.

        Raises:
            :obj:`~.errors.ClientException`
                If default_bot_id isn't provided when constructing the client.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        if not self.default_bot_id:
            raise errors.ClientException(
                "you must set default_bot_id when constructing the client."
            )
        await self._ensure_session()
        response = await self.http.get_bot_votes(self.default_bot_id)
        return [types.BriefUserData(**user) for user in response]

    async def get_bot_info(self, bot_id: t.Optional[int] = None) -> types.BotData:
        """This function is a coroutine.

        Gets information about a bot from Top.gg.

        Args:
            bot_id (int)
                ID of the bot to look up. Defaults to the provided Client object.

        Returns:
            :obj:`~.types.BotData`:
                Information on the bot you looked up. Returned data can be found
                `here <https://docs.top.gg/api/bot/#bot-structure>`_.

        Raises:
            :obj:`~.errors.ClientException`
                If neither bot_id or default_bot_id was set.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
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

        Args:
            limit (int)
                The number of results to look up. Defaults to 50. Max 500 allowed.
            offset (int)
                The amount of bots to skip. Defaults to 0.
            sort (str)
                The field to sort by. Prefix with ``-`` to reverse the order.
            search (:obj:`dict` [ :obj:`str`, :obj:`typing.Any` ])
                The search data.
            fields (:obj:`list` [ :obj:`str` ])
                Fields to output.

        Returns:
            :obj:`~.types.DataDict`:
                Info on bots that match the search query on Top.gg.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
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

    async def get_user_info(self, user_id: int) -> types.UserData:
        """This function is a coroutine.

        Gets information about a user on Top.gg.

        Args:
            user_id (int)
                ID of the user to look up.

        Returns:
            :obj:`~.types.UserData`:
                Information about a Top.gg user.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        await self._ensure_session()
        response = await self.http.get_user_info(user_id)
        return types.UserData(**response)

    async def get_user_vote(self, user_id: int) -> bool:
        """Gets information about a user's vote for your bot on Top.gg.

        Args:
            user_id (int)
                ID of the user.

        Returns:
            :obj:`bool`: Info about the user's vote.

        Raises:
            :obj:`~.errors.ClientException`
                If default_bot_id isn't provided when constructing the client.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
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

        Keyword Arguments:
            options (:obj:`~.types.WidgetOptions`)
                A :obj:`~.types.WidgetOptions` object containing widget parameters.

        Returns:
            str: Generated widget URL.

        Raises:
            :obj:`~.errors.ClientException`
                If bot_id or default_bot_id is unset.
            TypeError:
                If options passed is not of type WidgetOptions.
        """
        if not isinstance(options, types.WidgetOptions):
            raise TypeError(
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
        """Closes all connections."""
        if self.is_closed:
            return

        if hasattr(self, "http"):
            await self.http.close()

        if self._autopost:
            self._autopost.cancel()

        self._is_closed = True

    def autopost(self) -> AutoPoster:
        """Returns a helper instance for auto-posting.

        Note:
            The second time you call this method, it'll return the same instance
            as the one returned from the first call.

        Returns:
            :obj:`~.autopost.AutoPoster`: An instance of AutoPoster.
        """
        if self._autopost is not None:
            return self._autopost

        self._autopost = AutoPoster(self)
        return self._autopost
