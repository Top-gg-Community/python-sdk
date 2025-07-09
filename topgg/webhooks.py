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

from collections.abc import Awaitable, Callable
from aiohttp import web, ContentTypeError
from typing import Any, Optional, Union
from json import JSONDecodeError
from inspect import isawaitable

from .models import Vote


RawCallback = Callable[[web.Request], Awaitable[web.StreamResponse]]
OnVoteCallback = Callable[[Vote], Any]
OnVoteDecorator = Callable[[OnVoteCallback], RawCallback]


class Webhooks:
  """
  Receive events from the Top.gg servers.

  Example:

  .. code-block:: python

    webhooks = topgg.Webhooks(os.getenv('MY_TOPGG_WEBHOOK_SECRET'), 8080)

  :param auth: The default password to use.
  :type auth: Optional[:py:class:`str`]
  :param port: The default port to use.
  :type port: Optional[:py:class:`int`]
  """

  __slots__ = ('__app', '__server', '__default_auth', '__default_port', '__running')

  def __init__(self, auth: Optional[str] = None, port: Optional[int] = None) -> None:
    self.__app = web.Application()
    self.__server = None
    self.__default_auth = auth
    self.__default_port = port
    self.__running = False

  def __repr__(self) -> str:
    return f'<{__class__.__name__} app={self.__app!r} running={self.running}>'

  def on_vote(
    self,
    route: str,
    auth: Optional[str] = None,
    callback: Optional[OnVoteCallback] = None,
  ) -> Union[OnVoteCallback, OnVoteDecorator]:
    """
    Registers a route that gets called whenever your Discord bot/server receives a vote.

    Example:

    .. code-block:: python

      @webhooks.on_vote('/votes')
      def voted(vote: topgg.Vote) -> None:
        print(f'A user with the ID of {vote.voter_id} has voted us on Top.gg!')

    :param route: The route to use.
    :type route: :py:class:`str`
    :param auth: The password to override and use. Defaults to the default password provided in the constructor call.
    :type auth: Optional[:py:class:`str`]
    :param callback: The callback to override and use. If this is :py:obj:`None`, this method relies on the decorator input.
    :type callback: Optional[:data:`~.webhooks.OnVoteCallback`]

    :exception TypeError: the route argument is not a :py:class:`str` or if the password is not provided.

    :returns: The function itself or a decorated function depending on the argument.
    :rtype: Union[:data:`~.webhooks.OnVoteCallback`, :data:`~.webhooks.OnVoteDecorator`]
    """

    if not isinstance(route, str) or not route:
      raise TypeError('Missing route argument.')

    auth = auth or self.__default_auth

    assert auth is not None, 'Missing password.'

    def decorator(inner_callback: OnVoteCallback) -> RawCallback:
      async def handler(request: web.Request) -> web.Response:
        if request.headers.get('Authorization', '') != auth:
          return web.Response(status=401, text='Unauthorized')

        try:
          vote = Vote(await request.json())
        except (JSONDecodeError, ContentTypeError):
          return web.Response(status=400, text='Bad request')

        response = inner_callback(vote)

        if isawaitable(response):
          await response

        return web.Response(status=204, text='')

      self.__app.router.add_post(route, handler)

      return handler

    if callback is not None:
      decorator(callback)

      return callback

    return decorator

  async def start(self, port: Optional[int] = None) -> None:
    """
    Starts the webhook server.

    Example:

    .. code-block:: python

      await webhooks.start()

    :param port: The port to override and use. Defaults to the default port provided in the constructor call.
    :type port: Optional[:py:class:`int`]

    :exception TypeError: the port is not provided either here or in the constructor call.
    """

    if not self.running:
      port = port or self.__default_port

      assert port is not None, 'Missing port.'

      runner = web.AppRunner(self.__app)
      await runner.setup()

      self.__server = web.TCPSite(runner, '0.0.0.0', port)
      await self.__server.start()

      self.__running = True

  async def close(self) -> None:
    """
    Closes the webhook server.

    Example:

    .. code-block:: python

      await webhooks.close()
    """

    if self.running:
      await self.__server.stop()

      self.__running = False

  @property
  def running(self) -> bool:
    """Whether the webhook server is running."""

    return self.__running

  @property
  def app(self) -> web.Application:
    """The ``aiohttp`` :class:`~aiohttp.web.Application` that this webhook server uses."""

    return self.__app

  async def __aenter__(self) -> 'Webhooks':
    await self.start()

    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
