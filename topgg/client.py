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

from aiohttp import ClientSession, ClientTimeout
from typing import Optional, Tuple, Iterable
from collections import namedtuple
from base64 import b64decode
from asyncio import sleep
from json import loads
from time import time

from .models import Bot, BotQuery, Voter
from .errors import Error, RequestError, Ratelimited
from .ratelimiter import Ratelimiter, RatelimiterManager

BASE_URL = 'https://top.gg/api'
MAXIMUM_DELAY_THRESHOLD = 5.0


class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API. To retrieve your API token, see https://docs.top.gg/docs/API/@reference.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :exception TypeError: If ``token`` is not a :py:class:`str`.
  :exception ValueError: If ``token`` is not a valid API token.
  """

  __slots__: Tuple[str, ...] = (
    '__own_session',
    '__session',
    '__token',
    '__ratelimiters',
    '__ratelimiter_manager',
    '__current_ratelimit',
    'id',
  )

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not isinstance(token, str) or not token:
      raise TypeError('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(
      timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
    )
    self.__token = token

    try:
      encoded_json = token.split('.')[1]
      encoded_json += '=' * (4 - (len(encoded_json) % 4))

      self.id = int(loads(b64decode(encoded_json))['id'])
    except:
      raise ValueError('Got a malformed Top.gg API token.')

    endpoint_ratelimits = namedtuple('EndpointRatelimits', 'global_ bot')

    self.__ratelimiters = endpoint_ratelimits(
      global_=Ratelimiter(99, 1), bot=Ratelimiter(59, 60)
    )
    self.__ratelimiter_manager = RatelimiterManager(self.__ratelimiters)
    self.__current_ratelimit = None

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __request(
    self,
    method: str,
    path: str,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
    treat_404_as_none: bool = True,
  ) -> Optional[dict]:
    if self.__session.closed:
      raise Error('Client session is already closed.')

    if self.__current_ratelimit is not None:
      current_time = time()

      if current_time < self.__current_ratelimit:
        raise Ratelimited(self.__current_ratelimit - current_time)
      else:
        self.__current_ratelimit = None

    ratelimiter = (
      self.__ratelimiter_manager
      if path.startswith('/bots')
      else self.__ratelimiters.global_
    )

    kwargs = {}

    if json:
      kwargs['json'] = json

    if params:
      kwargs['params'] = params

    status = None
    retry_after = None
    json = None

    async with ratelimiter:
      try:
        async with self.__session.request(
          method,
          BASE_URL + path,
          headers={
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            'User-Agent': 'topggpy (https://github.com/top-gg-community/python-sdk 3.0.0) Python/',
          },
          **kwargs,
        ) as resp:
          status = resp.status
          retry_after = float(resp.headers.get('Retry-After', 0))

          try:
            json = await resp.json()
          except:
            pass

          resp.raise_for_status()

          return json
      except:
        if status == 404 and treat_404_as_none:
          return
        elif status == 429:
          if retry_after > MAXIMUM_DELAY_THRESHOLD:
            self.__current_ratelimit = time() + retry_after

            raise Ratelimited(retry_after) from None

          await sleep(retry_after)

          return await self.__request(method, path)

        raise RequestError(json and json.get('message'), status) from None

  async def get_bot(self, id: int) -> Optional[Bot]:
    """
    Fetches a Discord bot from its ID.

    :param id: The requested ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: The requested bot. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:class:`~.models.Bot`]
    """

    bot = await self.__request('GET', f'/bots/{id}')

    return bot and Bot(bot)

  def get_bots(self) -> BotQuery:
    """
    Fetches and yields Discord bots that matches the specified query.

    :returns: A :class:`~.models.BotQuery` object, which allows you to configure a query before sending it to the API.
    :rtype: :class:`~.models.BotQuery`
    """

    return BotQuery(self)

  async def get_server_count(self) -> Optional[int]:
    """
    Fetches your Discord bot's posted server count.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: The posted server count. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:py:class:`int`]
    """

    stats = await self.__request('GET', f'/bots/{self.id}/stats')

    return stats and stats.get('server_count')

  async def post_server_count(self, new_server_count: int):
    """
    Posts your Discord bot's server count to the API. This will update the server count in your bot's Top.gg page.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.
    """

    await self.__request(
      'POST', f'/bots/{self.id}/stats', json={'server_count': new_server_count}
    )

  async def is_weekend(self) -> bool:
    """
    Checks if the weekend multiplier is active.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Whether the weekend multiplier is active.
    :rtype: bool
    """

    response = await self.__request('GET', '/weekend', treat_404_as_none=False)

    return response['is_weekend']

  async def get_voters(self) -> Iterable[Voter]:
    """
    Fetches and yields your Discord bot's last 1000 voters.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Your bot's last 1000 voters.
    :rtype: Iterable[:class:`~.models.Voter`]
    """

    voters = await self.__request('GET', f'/bots/{self.id}/votes')

    return map(Voter, voters or ())

  async def has_voted(self, id: int) -> bool:
    """
    Checks if the specified Discord user has voted your Discord bot.

    :param id: The requested user's ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Whether the specified user has voted your bot.
    :rtype: bool
    """

    response = await self.__request(
      'GET', f'/bots/{self.id}/check?userId={id}', treat_404_as_none=False
    )

    return bool(response['voted'])

  async def close(self) -> None:
    """Closes the :class:`~.client.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
