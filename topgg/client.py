"""
The MIT License (MIT)

Copyright (c) 2021 Assanali Mukhanov & Top.gg
Copyright (c) 2024-2025 null8626 & Top.gg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = ["DBLClient"]

from collections import namedtuple
from base64 import b64decode
from time import time
import typing as t
import binascii
import aiohttp
import asyncio
import json

from . import errors, types
from .version import VERSION
from .autopost import AutoPoster
from .data import DataContainerMixin
from .ratelimiter import Ratelimiter, Ratelimiters


BASE_URL = 'https://top.gg/api'
MAXIMUM_DELAY_THRESHOLD = 5.0


class DBLClient(DataContainerMixin):
    """Represents a client connection that connects to Top.gg.

    This class is used to interact with the Top.gg API.

    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Args:
        token (:obj:`str`): Your Top.gg API Token.

    Keyword Args:
        session (:class:`aiohttp.ClientSession`)
            An `aiohttp session`_ to use for requests to the API.
    """

    __slots__ = ("id", "_token", "_autopost", "__session", "__own_session", "__ratelimiter", "__ratelimiters", "__current_ratelimit")

    def __init__(
        self,
        token: str,
        *,
        session: t.Optional[aiohttp.ClientSession] = None,
    ) -> None:
        super().__init__()

        self.__own_session = session is None
        self.__session = session or aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
        )
        self._token = token
        self._autopost: t.Optional[AutoPoster] = None

        try:
            encoded_json = token.split('.')[1]
            encoded_json += '=' * (4 - (len(encoded_json) % 4))
            encoded_json = json.loads(b64decode(encoded_json))
      
            self.id = int(encoded_json['id'])
        except (IndexError, ValueError, binascii.Error, json.decoder.JSONDecodeError):
            raise ValueError('Got a malformed API token.') from None

        endpoint_ratelimits = namedtuple('EndpointRatelimits', 'global_ bot')

        self.__ratelimiter = endpoint_ratelimits(
            global_=Ratelimiter(99, 1), bot=Ratelimiter(59, 60)
        )
        self.__ratelimiters = Ratelimiters(self.__ratelimiter)
        self.__current_ratelimit = None

    async def __request(
        self,
        method: str,
        path: str,
        params: t.Optional[dict] = None,
        body: t.Optional[dict] = None,
    ) -> dict:
        if self.is_closed:
            raise errors.ClientStateException('Client session is already closed.')

        if self.__current_ratelimit is not None:
            current_time = time()

            if current_time < self.__current_ratelimit:
                raise errors.Ratelimited(self.__current_ratelimit - current_time)
            else:
                self.__current_ratelimit = None

        ratelimiter = (
            self.__ratelimiters if path.startswith('/bots') else self.__ratelimiter.global_
        )

        kwargs = {}

        if body:
            kwargs['json'] = body

        if params:
            kwargs['params'] = params

        response = None
        retry_after = None
        output = None

        async with ratelimiter:
            try:
                response = await self.__session.request(
                    method,
                    BASE_URL + path,
                    headers={
                        'Authorization': f'Bearer {self.__token}',
                        'Content-Type': 'application/json',
                        'User-Agent': f'topggpy (https://github.com/top-gg-community/python-sdk {VERSION}) Python/',
                    },
                    **kwargs,
                )
                
                retry_after = float(response.headers.get('Retry-After', 0))

                if 'json' in response.headers['Content-Type']:
                    try:
                        output = await response.json()
                    except json.decoder.JSONDecodeError:
                        pass

                response.raise_for_status()

                return output
            except aiohttp.ClientResponseError:
                if response.status == 429:
                    if retry_after > MAXIMUM_DELAY_THRESHOLD:
                        self.__current_ratelimit = time() + retry_after

                        raise errors.Ratelimited(retry_after) from None

                    await asyncio.sleep(retry_after)

                    return await self.__request(method, path)

                raise errors.HTTPException(response, output) from None

    @property
    def is_closed(self) -> bool:
        return self.__session.closed

    async def get_weekend_status(self) -> bool:
        """Gets weekend status from Top.gg.

        Returns:
            :obj:`bool`: The boolean value of weekend status.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        
        response = await self.__request('GET', '/weekend')

        return response['is_weekend']

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

        Raises:
            TypeError
                If no argument is provided.
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        if stats:
            guild_count = stats.guild_count
        elif guild_count is None:
            raise TypeError("stats or guild_count must be provided.")

        await self.__request('POST', '/bots/stats', body={'server_count': guild_count})

    async def get_guild_count(self) -> types.BotStatsData:
        """Gets a bot's guild count and shard info from Top.gg.

        Args:
            bot_id (int)
                ID of the bot you want to look up. Defaults to the provided Client object.

        Returns:
            :obj:`~.types.BotStatsData`:
                The guild count and shards of a bot on Top.gg.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """

        response = await self.__request('GET', '/bots/stats')

        return types.BotStatsData(**response)

    async def get_bot_votes(self) -> t.List[types.BriefUserData]:
        """Gets information about last 1000 votes for your bot on Top.gg.

        Note:
            This API endpoint is only available to the bot's owner.

        Returns:
            :obj:`list` [ :obj:`~.types.BriefUserData` ]:
                Users who voted for your bot.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """

        response = await self.__request('GET', f'/bots/{self.id}/votes')
        
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
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """
        bot_id = bot_id or self.id
        response = await self.__request('GET', f'/bots/{bot_id}')
        return types.BotData(**response)

    async def get_user_vote(self, user_id: int) -> bool:
        """Gets information about a user's vote for your bot on Top.gg.

        Args:
            user_id (int)
                ID of the user.

        Returns:
            :obj:`bool`: Info about the user's vote.

        Raises:
            :obj:`~.errors.ClientStateException`
                If the client has been closed.
        """

        data = await self.__request('GET', '/bots/check', params={'userId': user_id})
        
        return bool(data["voted"])

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
    
    async def close(self) -> None:
        """Closes all connections."""

        if self._autopost:
            self._autopost.cancel()
       
        if self.__own_session and not self.__session.closed:
            await self.__session.close()

    async def __aenter__(self) -> "DBLClient":
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.close()