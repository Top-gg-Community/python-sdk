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
from collections.abc import Iterable, Callable, Coroutine
from typing import Any, Optional, Union
from collections import namedtuple
from inspect import isawaitable
from base64 import b64decode
from time import time
import binascii
import asyncio
import json

from .ratelimiter import Ratelimiter, Ratelimiters
from .errors import Error, RequestError, Ratelimited
from .models import Bot, SortBy, Voter
from .version import VERSION


BASE_URL = 'https://top.gg/api/v1'
MAXIMUM_DELAY_THRESHOLD = 5.0


AutopostRetrievalCallback = Callable[[], Union[int, Coroutine[None, None, int]]]
AutopostRetrievalDecorator = Callable[
  [AutopostRetrievalCallback], AutopostRetrievalCallback
]

AutopostSuccessCallback = Callable[[int], Any]
AutopostSuccessDecorator = Callable[[AutopostSuccessCallback], AutopostSuccessCallback]

AutopostErrorCallback = Callable[[Error], Any]
AutopostErrorDecorator = Callable[[AutopostErrorCallback], AutopostErrorCallback]


class Client:
  """
  Interact with the API's endpoints.

  :param token: The API token to use. To retrieve it, see https://github.com/top-gg/rust-sdk/assets/60427892/d2df5bd3-bc48-464c-b878-a04121727bff.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :exception TypeError: ``token`` is not a :py:class:`str` or is empty.
  :exception ValueError: ``token`` is not a valid API token.
  """

  id: int
  """This bot's ID."""

  __slots__: tuple[str, ...] = (
    '__own_session',
    '__session',
    '__token',
    '__ratelimiter',
    '__ratelimiters',
    '__current_ratelimit',
    '__autopost_task',
    '__autopost_retrieval_callback',
    '__autopost_success_callbacks',
    '__autopost_error_callbacks',
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

      self.id = int(json.loads(b64decode(encoded_json))['id'])
    except (IndexError, ValueError, binascii.Error, json.decoder.JSONDecodeError):
      raise ValueError('Got a malformed API token.')

    endpoint_ratelimits = namedtuple('EndpointRatelimits', 'global_ bot')

    self.__ratelimiter = endpoint_ratelimits(
      global_=Ratelimiter(99, 1), bot=Ratelimiter(59, 60)
    )
    self.__ratelimiters = Ratelimiters(self.__ratelimiter)
    self.__current_ratelimit = None

    self.__autopost_task = None
    self.__autopost_retrieval_callback = None
    self.__autopost_success_callbacks = set()
    self.__autopost_error_callbacks = set()

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  def __int__(self) -> int:
    return self.id

  async def __request(
    self,
    method: str,
    path: str,
    params: Optional[dict] = None,
    body: Optional[dict] = None,
  ) -> dict:
    if self.__session.closed:
      raise Error('Client session is already closed.')

    if self.__current_ratelimit is not None:
      current_time = time()

      if current_time < self.__current_ratelimit:
        raise Ratelimited(self.__current_ratelimit - current_time)
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

    status = None
    retry_after = None
    output = None

    async with ratelimiter:
      try:
        async with self.__session.request(
          method,
          BASE_URL + path,
          headers={
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            'User-Agent': f'topggpy (https://github.com/top-gg-community/python-sdk {VERSION}) Python/',
          },
          **kwargs,
        ) as resp:
          status = resp.status
          retry_after = float(resp.headers.get('Retry-After', 0))

          if 'application/json' in resp.headers['Content-Type']:
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

            raise Ratelimited(retry_after) from None

          await asyncio.sleep(retry_after)

          return await self.__request(method, path)

        raise RequestError(output and output.get('message'), status) from None

  async def get_bot(self, id: int) -> Bot:
    """
    Fetches a Discord bot from its ID.

    :param id: The requested ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: Such query does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested bot.
    :rtype: :class:`.Bot`
    """

    return Bot(await self.__request('GET', f'/bots/{id}'))

  async def get_bots(
    self,
    *,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: Optional[SortBy] = None,
  ) -> Iterable[Bot]:
    """
    Fetches and yields Discord bots that matches the specified query.

    :param limit: The maximum amount of bots to be queried.
    :type limit: Optional[:py:class:`int`]
    :param offset: The amount of bots to be skipped.
    :type offset: Optional[:py:class:`int`]
    :param sort_by: Sorts results based on a specific criteria. Results will always be descending.
    :type sort_by: Optional[:class:`.SortBy`]

    :exception Error: The client is already closed.
    :exception RequestError: Received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: A generator of matching bots.
    :rtype: Iterable[:class:`.Bot`]
    """

    params = {}

    if limit is not None:
      params['limit'] = max(min(limit, 500), 1)

    if offset is not None:
      params['offset'] = max(min(offset, 499), 0)

    if sort_by is not None:
      if not isinstance(sort_by, SortBy):
        raise TypeError(
          f'Expected sort_by to be a SortBy enum, got {sort_by.__class__.__name__}.'
        )

      params['sort'] = sort_by.value

    bots = await self.__request('GET', '/bots', params=params)

    return map(Bot, bots.get('results', ()))

  async def get_server_count(self) -> Optional[int]:
    """
    Fetches your Discord bot's posted server count.

    :exception Error: The client is already closed.
    :exception RequestError: Received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The posted server count. This can be :py:obj:`None` if it does not exist.
    :rtype: Optional[:py:class:`int`]
    """

    stats = await self.__request('GET', '/bots/stats')

    return stats.get('server_count')

  async def post_server_count(self, new_server_count: int) -> None:
    """
    Posts your Discord bot's server count to the API. This will update the server count in your bot's Top.gg page.

    :param new_server_count: The new server count to post. This cannot be zero.
    :type new_server_count: :py:class:`int`

    :exception ValueError: The new_server_count argument is zero or lower.
    :exception Error: The client is already closed.
    :exception RequestError: Received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.
    """

    if new_server_count <= 0:
      raise ValueError(
        f'Posted server count cannot be zero or lower, got {new_server_count}.'
      )

    await self.__request('POST', '/bots/stats', body={'server_count': new_server_count})

  async def is_weekend(self) -> bool:
    """
    Checks if the weekend multiplier is active, where a single vote counts as two.

    :exception Error: The client is already closed.
    :exception RequestError: Received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: Whether the weekend multiplier is active.
    :rtype: :py:class:`bool`
    """

    response = await self.__request('GET', '/weekend')

    return response['is_weekend']

  async def get_voters(self, page: int = 1) -> Iterable[Voter]:
    """
    Fetches and yields your Discord bot's recent 100 unique voters.

    :param page: The page number. Each page can only have at most 100 voters. Defaults to 1.
    :type page: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: Received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: A generator of your bot's recent unique voters.
    :rtype: Iterable[:class:`.Voter`]
    """

    return map(
      Voter,
      await self.__request(
        'GET', f'/bots/{self.id}/votes', params={'page': max(page, 1)}
      ),
    )

  async def has_voted(self, id: int) -> bool:
    """
    Checks if the specified Discord user has voted your Discord bot.

    :param id: The requested user's ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The specified user has not logged in to Top.gg or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: Whether the specified user has voted your bot.
    :rtype: :py:class:`bool`
    """

    response = await self.__request('GET', '/bots/check', params={'userId': id})

    return bool(response['voted'])

  async def __autopost_loop(self, interval: Optional[float]) -> None:
    # The following line should not be changed, as it could affect test_autoposter.py.
    interval = max(interval or 900.0, 900.0)

    while True:
      try:
        server_count = self.__autopost_retrieval_callback()

        if isawaitable(server_count):
          server_count = await server_count

        await self.post_server_count(server_count)

        for success_callback in self.__autopost_success_callbacks:
          success_callback_result = success_callback(server_count)

          if isawaitable(success_callback_result):
            await success_callback_result

        await asyncio.sleep(interval)
      except Exception as err:
        if isinstance(err, Error):
          for error_callback in self.__autopost_error_callbacks:
            error_callback_result = error_callback(err)

            if isawaitable(error_callback_result):
              await error_callback_result
        elif isinstance(err, asyncio.CancelledError):
          return
        else:
          raise

  def autopost_retrieval(
    self, callback: Optional[AutopostRetrievalCallback] = None
  ) -> Union[AutopostRetrievalCallback, AutopostRetrievalDecorator]:
    """
    Registers an autopost server count retrieval callback. This callback is required for autoposting.

    :param callback: The autopost server count retrieval callback. This can be asynchronous or synchronous, as long as it eventually returns an :py:class:`int`.
    :type callback: Optional[:data:`~.client.AutopostRetrievalCallback`]

    :returns: The function itself or a decorated function depending on the argument.
    :rtype: Union[:data:`~.client.AutopostRetrievalCallback`, :data:`~.client.AutopostRetrievalDecorator`]
    """

    def decorator(callback: AutopostRetrievalCallback) -> AutopostRetrievalCallback:
      self.__autopost_retrieval_callback = callback

      return callback

    if callback is not None:
      decorator(callback)

      return callback

    return decorator

  def autopost_success(
    self, callback: Optional[AutopostSuccessCallback] = None
  ) -> Union[AutopostSuccessCallback, AutopostSuccessDecorator]:
    """
    Adds an autopost on success callback. Several callbacks are possible.

    :param callback: The autopost on success callback. This can be asynchronous or synchronous, as long as it accepts a :py:class:`int` argument for the posted server count.
    :type callback: Optional[:data:`~.client.AutopostSuccessCallback`]

    :returns: The function itself or a decorated function depending on the argument.
    :rtype: Union[:data:`~.client.AutopostSuccessCallback`, :data:`~.client.AutopostSuccessDecorator`]
    """

    def decorator(callback: AutopostSuccessCallback) -> AutopostSuccessCallback:
      self.__autopost_success_callbacks.add(callback)

      return callback

    if callback is not None:
      decorator(callback)

      return self

    return decorator

  def autopost_error(
    self, callback: Optional[AutopostErrorCallback] = None
  ) -> Union[AutopostErrorCallback, AutopostErrorDecorator]:
    """
    Adds an autopost on error handler. Several callbacks are possible.

    :param callback: The autopost on error handler. This can be asynchronous or synchronous, as long as it accepts an :class:`.Error` argument for the request exception.
    :type callback: Optional[:data:`~.client.AutopostErrorCallback`]

    :returns: The function itself or a decorated function depending on the argument.
    :rtype: Union[:data:`~.client.AutopostErrorCallback`, :data:`~.client.AutopostErrorDecorator`]
    """

    def decorator(callback: AutopostErrorCallback) -> AutopostErrorCallback:
      self.__autopost_error_callbacks.add(callback)

      return callback

    if callback is not None:
      decorator(callback)

      return self

    return decorator

  @property
  def autoposter_running(self) -> bool:
    """Whether the autoposter is running."""

    return self.__autopost_task is not None

  def start_autoposter(self, interval: Optional[float] = None) -> None:
    """
    Starts the autoposter. Has no effect if the autoposter is already running.

    :param interval: The interval between posting in seconds. Defaults to 15 minutes.
    :type interval: Optional[:py:class:`float`]

    :exception TypeError: The server count retrieval callback does not exist.
    """

    if not self.autoposter_running:
      if self.__autopost_retrieval_callback is None:
        raise TypeError('Missing autopost_retrieval callback.')

      self.__autopost_task = asyncio.create_task(self.__autopost_loop(interval))

  def stop_autoposter(self) -> None:
    """
    Stops the autoposter. Has no effect if the autoposter is already stopped.
    """

    if self.autoposter_running:
      self.__autopost_task.cancel()
      self.__autopost_task = None

  async def close(self) -> None:
    """Closes the client. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    self.stop_autoposter()

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
