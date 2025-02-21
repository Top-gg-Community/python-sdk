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
from typing import Optional, Tuple, List
from collections import namedtuple
from base64 import b64decode
from time import time
import asyncio
import json

from .models import Bot, BotQuery, Voter
from .errors import Error, RequestError, Ratelimited
from .ratelimiter import Ratelimiter, RatelimiterManager

BASE_URL = 'https://top.gg/api'
MAXIMUM_DELAY_THRESHOLD = 5.0


class Client:
  """
  The class that lets you interact with the API.

  :param token: The API token to use with the API. To retrieve your topstats.gg API token, see https://docs.top.gg/docs/API/@reference.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :raises TypeError: If ``token`` is not a :py:class:`str`.
  :raises ValueError: If ``token`` is not a valid API token.
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
    if not isinstance(token, str):
      raise TypeError('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(
      timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
    )
    self.__token = token

    try:
      encoded_json = token.split('.')[1]
      encoded_json += '=' * (4 - (len(encoded_json) % 4))

      self.id = int(json.loads(b64decode(encoded_json))['id'])
    except:
      raise ValueError('Got a malformed Top.gg API token.')

    endpoint_ratelimits = namedtuple('EndpointRatelimits', '_global bot')

    self.__ratelimiters = endpoint_ratelimits(
      _global=Ratelimiter(99, 1), bot=Ratelimiter(59, 60)
    )
    self.__ratelimiter_manager = RatelimiterManager(self.__ratelimiters)
    self.__current_ratelimit = None

  async def __request(
    self,
    method: str,
    path: str,
    params: dict = {},
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
      else self.__ratelimiters._global
    )

    status = None
    headers = None
    json = {}

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
          json=json,
          params=params,
        ) as resp:
          status = resp.status
          headers = resp.headers
          json = await resp.json()

          assert 200 <= status <= 299
          return json
      except:
        if status == 404 and treat_404_as_none:
          return
        elif status == 429:
          retry_after = float(headers['Retry-After'])

          if retry_after > MAXIMUM_DELAY_THRESHOLD:
            self.__current_ratelimit = time() + retry_after

            raise Ratelimited(retry_after) from None
          else:
            await asyncio.sleep(retry_after)
        else:
          raise RequestError(json, status) from None

    return await self.__request(method, path)

  async def get_bot(self, id: int) -> Optional[Bot]:
    """
    Fetches a Discord bot from its Discord ID.

    :param id: The requested Discord ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: The requested Discord bot. This can be :py:obj:`None` if the requested Discord bot does not exist.
    :rtype: Optional[:class:`~.models.Bot`]
    """

    bot = await self.__request('GET', f'/bots/{id}')

    return bot and Bot(bot)

  def get_bots(self) -> BotQuery:
    """
    Fetches a list of Discord bots that matches the specified bot query.

    :returns: A :class:`~.models.BotQuery` object, which allows you to configure a Discord bot query before sending it to the API to retrieve a list of Discord bots that matches the specified query.
    :rtype: :class:`~.models.BotQuery`
    """

    return BotQuery(self)

  async def is_weekend(self) -> bool:
    """
    Checks if the weekend multiplier is active.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Whether the weekend multiplier is active or not.
    :rtype: bool
    """

    response = await self.__request('GET', '/weekend', treat_404_as_none=False)

    return response['is_weekend']

  async def get_voters(self) -> List[Voter]:
    """
    Fetches your Discord bot's last 1000 voters.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Your Discord bot's last 1000 voters.
    :rtype: List[:class:`~.models.Voter`]
    """

    voters = await self.__request('GET', f'/bots/{self.id}/votes')
    output = []

    for voter in voters or ():
      output.append(Voter(voter))

    return output

  async def has_voted(self, id: int) -> bool:
    """
    Checks if the specified user has voted your Discord bot.

    :param id: The requested user's Discord ID.
    :type id: :py:class:`int`

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: Whether the specified user has voted your Discord bot.
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
