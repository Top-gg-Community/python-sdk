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

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from typing import Any, Optional, overload, Union
from collections import namedtuple
from base64 import b64decode
from time import time
import binascii
import warnings
import asyncio
import json

from . import errors, types
from .autopost import AutoPoster
from .ratelimiter import Ratelimiter, Ratelimiters
from .data import DataContainerMixin
from .version import VERSION


BASE_URL = 'https://top.gg/api'
MAXIMUM_DELAY_THRESHOLD = 5.0


class DBLClient(DataContainerMixin):
    """
    Interact with the API's endpoints.

    Examples:

    .. code-block:: python

        # Explicit cleanup
        client = topgg.DBLClient(os.getenv('TOPGG_TOKEN'))

        # ...

        await client.close()

        # Implicit cleanup
        async with topgg.DBLClient(os.getenv('TOPGG_TOKEN')) as client:
            # ...

    :param token: Your Top.gg API token.
    :type token: :py:class:`str`
    :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting. Defaults to :py:obj:`None` (creates a new one instead)
    :type session: Optional[:class:`~aiohttp.ClientSession`]

    :exception TypeError: ``token`` is not a :py:class:`str` or is empty.
    :exception ValueError: ``token`` is not a valid API token.
    """

    id: int
    """This project's ID."""

    __slots__: tuple[str, ...] = (
        '__own_session',
        '__session',
        '__token',
        '__ratelimiter',
        '__ratelimiters',
        '__current_ratelimit',
        '_autopost',
        'id',
    )

    def __init__(
        self, token: str, *, session: Optional[ClientSession] = None, **kwargs
    ):
        super().__init__()

        if not isinstance(token, str) or not token:
            raise TypeError('An API token is required to use this API.')

        if kwargs.pop('default_bot_id', None):
            warnings.warn(
                'The default bot ID is now derived from the Top.gg API token itself',
                DeprecationWarning,
            )

        for key in kwargs.keys():
            warnings.warn(f'Ignored keyword argument: {key}', DeprecationWarning)

        self._autopost = None
        self.__own_session = session is None
        self.__session = session or ClientSession(
            timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
        )
        self.__token = token

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

    def __repr__(self) -> str:
        return f'<{__class__.__name__} {self.__session!r}>'

    def __int__(self) -> int:
        return self.id

    @property
    def is_closed(self) -> bool:
        """Whether the client is closed."""

        return self.__session.closed

    async def __request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        body: Optional[dict] = None,
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
            self.__ratelimiters
            if path.startswith('/bots')
            else self.__ratelimiter.global_
        )

        kwargs = {}

        if body:
            kwargs['json'] = body

        if params:
            kwargs['params'] = params

        status = None
        retry_after = None
        output = None

        async with ratelimiter:
            try:
                async with self.__session.request(
                    method,
                    BASE_URL + path,
                    headers={
                        'Authorization': f'Bearer {self.__token}',
                        'Content-Type': 'application/json',
                        'User-Agent': f'topggpy (https://github.com/top-gg-community/python-sdk {VERSION}) Python/',
                    },
                    **kwargs,
                ) as resp:
                    status = resp.status
                    retry_after = float(resp.headers.get('Retry-After', 0))

                    if 'json' in resp.headers['Content-Type']:
                        try:
                            output = await resp.json()
                        except json.decoder.JSONDecodeError:
                            pass

                    resp.raise_for_status()

                    return output
            except ClientResponseError:
                if status == 429:
                    if retry_after > MAXIMUM_DELAY_THRESHOLD:
                        self.__current_ratelimit = time() + retry_after

                        raise errors.Ratelimited(retry_after) from None

                    await asyncio.sleep(retry_after)

                    return await self.__request(method, path)

                raise errors.HTTPException(
                    output and output.get('message', output.get('detail')), status
                ) from None

    async def get_bot_info(self, id: Optional[int]) -> types.BotData:
        """
        Fetches a Discord bot from its ID.

        Example:

        .. code-block:: python

            bot = await client.get_bot_info(432610292342587392)

        :param id: The bot's ID. Defaults to your bot's ID.
        :type id: Optional[:py:class:`int`]

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Such query does not exist or the client has received other unfavorable responses from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: The requested bot.
        :rtype: :class:`.BotData`
        """

        return types.BotData(await self.__request('GET', f'/bots/{id or self.id}'))

    async def get_bots(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[types.SortBy] = None,
        *args,
        **kwargs,
    ) -> types.BotsData:
        """
        Fetches Discord bots that matches the specified query.

        Examples:

        .. code-block:: python

            # With defaults
            bots = await client.get_bots()

            # With explicit arguments
            bots = await client.get_bots(limit=250, offset=50, sort=topgg.SortBy.MONTHLY_VOTES)

            for bot in bots:
                print(bot)

        :param limit: The maximum amount of bots to be returned.
        :type limit: Optional[:py:class:`int`]
        :param offset: The amount of bots to be skipped.
        :type offset: Optional[:py:class:`int`]
        :param sort: The criteria to sort results by. Results will always be descending.
        :type sort: Optional[:class:`.SortBy`]

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Received an unfavorable response from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: The requested bots.
        :rtype: :class:`.BotsData`
        """

        params = {}

        if limit is not None:
            params['limit'] = max(min(limit, 500), 1)

        if offset is not None:
            params['offset'] = max(min(offset, 499), 0)

        if sort is not None:
            if not isinstance(sort, types.SortBy):
                if isinstance(sort, str) and sort in types.SortBy:
                    warnings.warn(
                        'The sort argument now expects a SortBy enum, not a str',
                        DeprecationWarning,
                    )

                    params['sort'] = sort
                else:
                    raise TypeError(
                        f'Expected sort to be a SortBy enum, got {sort.__class__.__name__}.'
                    )
            else:
                params['sort'] = sort.value

        for arg in args:
            warnings.warn(f'Ignored extra argument: {arg!r}', DeprecationWarning)

        for key in kwargs.keys():
            warnings.warn(f'Ignored keyword argument: {key}', DeprecationWarning)

        return types.BotsData(await self.__request('GET', '/bots', params=params))

    async def get_guild_count(self) -> Optional[types.BotStatsData]:
        """
        Fetches your Discord bot's posted statistics.

        Example:

        .. code-block:: python

            stats = await client.get_guild_count()
            server_count = stats.server_count

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Received an unfavorable response from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: The posted statistics.
        :rtype: Optional[:py:class:`.BotStatsData`]
        """

        stats = await self.__request('GET', '/bots/stats')

        return stats and types.BotStatsData(stats)

    @overload
    async def post_guild_count(self, stats: types.StatsWrapper) -> None: ...

    @overload
    async def post_guild_count(
        self,
        *,
        guild_count: Union[int, list[int]],
        shard_count: Optional[int] = None,
        shard_id: Optional[int] = None,
    ) -> None: ...

    async def post_guild_count(
        self, stats: Any = None, *, guild_count: Any = None, **kwargs
    ) -> None:
        """
        Updates the statistics in your Discord bot's Top.gg page.

        Example:

        .. code-block:: python

            await client.post_guild_count(topgg.StatsWrapper(bot.server_count))

        :param stats: The updated statistics.
        :type stats: :class:`.StatsWrapper`
        :param guild_count: The updated server count.
        :type guild_count: Union[:py:class:`int`, list[:py:class:`int`]]

        :exception ValueError: Got an invalid server count.
        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Received an unfavorable response from the API.
        :exception Ratelimited: Ratelimited from sending more requests.
        """

        for key in kwargs.keys():
            warnings.warn(f'Ignored keyword argument: {key}', DeprecationWarning)

        if isinstance(stats, types.StatsWrapper):
            guild_count = stats.server_count

        if not guild_count or guild_count <= 0:
            raise ValueError(f'Got an invalid server count. Got {guild_count!r}.')

        await self.__request('POST', '/bots/stats', body={'server_count': guild_count})

    async def get_weekend_status(self) -> bool:
        """
        Checks if the weekend multiplier is active, where a single vote counts as two.

        Example:

        .. code-block:: python

            is_weekend = await client.get_weekend_status()

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Received an unfavorable response from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: Whether the weekend multiplier is active.
        :rtype: :py:class:`bool`
        """

        response = await self.__request('GET', '/weekend')

        return response['is_weekend']

    async def get_bot_votes(self, page: int = 1) -> list[types.BriefUserData]:
        """
        Fetches your project's recent 100 unique voters.

        Examples:

        .. code-block:: python

            # First page
            voters = await client.get_bot_votes()

            # Subsequent pages
            voters = await client.get_bot_votes(2)

            for voter in voters:
                print(voter)

        :param page: The page number. Each page can only have at most 100 voters. Defaults to 1.
        :type page: :py:class:`int`

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: Received an unfavorable response from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: The requested voters.
        :rtype: list[:class:`.BriefUserData`]
        """

        return [
            types.BriefUserData(data)
            for data in await self.__request(
                'GET', f'/bots/{self.id}/votes', params={'page': max(page, 1)}
            )
        ]

    async def get_user_info(self, user_id: int) -> types.UserData:
        """
        Fetches a Top.gg user from their ID.

        .. deprecated:: 1.5.0
            No longer supported by API v0.

        """

        warnings.warn('get_user_info() is no longer supported', DeprecationWarning)

        raise errors.HTTPException('User not found', 404)

    async def get_user_vote(self, id: int) -> bool:
        """
        Checks if a Top.gg user has voted for your project in the past 12 hours.

        Example:

        .. code-block:: python

            has_voted = await client.get_user_vote(661200758510977084)

        :param id: The user's ID.
        :type id: :py:class:`int`

        :exception ClientStateException: The client is already closed.
        :exception HTTPException: The specified user has not logged in to Top.gg or the client has received other unfavorable responses from the API.
        :exception Ratelimited: Ratelimited from sending more requests.

        :returns: Whether the user has voted in the past 12 hours.
        :rtype: :py:class:`bool`
        """

        response = await self.__request('GET', '/bots/check', params={'userId': id})

        return bool(response['voted'])

    def autopost(self) -> AutoPoster:
        """
        Creates an autoposter instance that automatically updates the statistics in your Discord bot's Top.gg page every few minutes.

        Note that the after you call this method, subsequent calls will always return the same instance.

        .. code-block:: python

            autoposter = client.autopost()

            @autoposter.stats
            def get_stats() -> int:
                return topgg.StatsWrapper(bot.server_count)

            @autoposter.on_success
            def success() -> None:
                print('Successfully posted statistics to the Top.gg API!')

            @autoposter.on_error
            def error(exc: Exception) -> None:
                print(f'Error: {exc!r}')

            autoposter.start()

        :returns: The autoposter instance.
        :rtype: :class:`.AutoPoster`
        """

        if self._autopost is not None:
            return self._autopost

        self._autopost = AutoPoster(self)

        return self._autopost

    async def close(self) -> None:
        """
        Closes the client.

        Example:

        .. code-block:: python

            await client.close()
        """

        if self.__own_session and not self.is_closed:
            await self.__session.close()

    async def __aenter__(self) -> 'DBLClient':
        return self

    async def __aexit__(self, *_, **__) -> None:
        await self.close()
