# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from collections.abc import Awaitable, Callable
from inspect import iscoroutinefunction
from aiohttp import test_utils, web
from typing import Any, TypeAlias
from hashlib import sha256
import warnings
import hmac
import json

from .payload import (
  IntegrationCreatePayload,
  IntegrationDeletePayload,
  TestPayload,
  PayloadType,
  VoteCreatePayload,
)
from .client import API_VERSION


IntegrationCreateListener: TypeAlias = Callable[
  [IntegrationCreatePayload, str], Awaitable[web.Response]
]
"""Fires when a user has connected to your webhook integration."""

IntegrationDeleteListener: TypeAlias = Callable[
  [IntegrationDeletePayload, str], Awaitable[web.Response | None]
]
"""Fires when a user has disconnected from your webhook integration."""

TestListener: TypeAlias = Callable[[TestPayload, str], Awaitable[web.Response | None]]
"""Fires upon sent test from the project dashboard."""

VoteCreateListener: TypeAlias = Callable[
  [VoteCreatePayload, str], Awaitable[web.Response | None]
]
"""Fires when a user votes for your project."""

Listener: TypeAlias = (
  IntegrationCreateListener
  | IntegrationDeleteListener
  | TestListener
  | VoteCreateListener
)
"""All possible webhook listeners."""


class Webhooks:
  """
  A Top.gg webhook manager.

  :param route: The route for receiving all webhook payloads.
  :type route: :py:class:`str`
  :param secret: The webhook secret to use to authorize external requests.
  :type secret: :py:class:`str`
  :param host: The web server host to use. Defaults to '0.0.0.0'.
  :type host: :py:class:`str`
  :param port: The web server port to use. Defaults to 8080.
  :type port: :py:class:`int`
  :param app: The :class:`~aiohttp.web.Application` instance to use. Defaults to creating one with default configurations.
  :type app: :class:`~aiohttp.web.Application` | :class:`~aiohttp.test_utils.TestClient` | :py:obj:`None`

  :exception TypeError: One or more specified arguments has an invalid type.
  :exception ValueError: One or more specified arguments is empty.
  :exception UnicodeEncodeError: The specified secret is not valid UTF-8.
  """

  __slots__: tuple[str, ...] = (
    '__route',
    '__host',
    '__port',
    '__secret',
    '__app',
    '__web_server',
    '__is_running',
    '__listeners',
  )

  __route: str
  __host: str
  __port: int
  __secret: bytes
  __app: web.Application | test_utils.TestClient
  __web_server: web.TCPSite | None
  __is_running: bool
  __listeners: dict[PayloadType, list[Listener]]

  def __init__(
    self,
    route: str,
    secret: str,
    *,
    host: str = '0.0.0.0',
    port: int = 8080,
    app: web.Application | test_utils.TestClient | None = None,
  ):
    if (
      not isinstance(secret, str)
      or not isinstance(route, str)
      or not isinstance(host, str)
    ):
      raise TypeError(
        'The specified secret, route, and/or host must be a valid string.'
      )
    elif not secret or not route or not host:
      raise ValueError('The specified secret, route, and/or host must not be empty.')
    elif port is not None and not isinstance(port, int):
      raise TypeError('The specified port must be an integer.')

    self.__route = route
    self.__host = host
    self.__port = port
    self.secret = secret
    self.__app = app or web.Application()
    self.__web_server = None
    self.__is_running = False
    self.__listeners = {}

  def __repr__(self) -> str:
    return f'<{__class__.__name__} route={self.__route!r} host={self.__host!r} port={self.__port} is_running={self.is_running}>'

  @property
  def secret(self) -> str:
    """The secret to use to authorize external requests."""

    return self.__secret.decode('utf-8')

  @secret.setter
  def secret(self, new_secret: str):
    """
    Sets the webhook secret to use to authorize external requests.

    :param new_secret: The new webhook secret to use to authorize external requests.
    :type new_secret: :py:class:`str`

    :exception TypeError: The specified secret's type is invalid.
    :exception ValueError: The specified secret is empty.
    :exception UnicodeEncodeError: The specified secret is not valid UTF-8.
    """

    if not isinstance(new_secret, str):
      raise TypeError('The specified secret must be a valid string.')
    elif not new_secret:
      raise ValueError('The specified secret must not be empty.')

    self.__secret = new_secret.encode('utf-8')

  def on(self, payload_type: PayloadType) -> 'Callable[[Listener], Listener]':
    """
    Adds a listener that gets fired upon receiving a specified payload type.

    :param payload_type: The corresponding webhook payload type.
    :type payload_type: :class:`.PayloadType`

    :exception TypeError: The specified payload type and/or listener's type is invalid.
    :exception UnicodeDecodeError: The specified secret is not valid UTF-8.

    :returns: A decorator of the specified listener.
    :rtype: Callable[[:data:`.Listener`], :data:`.Listener`]
    """

    if not isinstance(payload_type, PayloadType):
      raise TypeError("The specified payload's type is invalid.")

    def decorator(listener: Listener) -> Listener:
      if not iscoroutinefunction(listener):
        raise TypeError('The specified webhook listener must be a coroutine function.')

      if payload_type in self.__listeners:  # pragma: nocover
        self.__listeners[payload_type].append(listener)
      else:
        self.__listeners[payload_type] = [listener]

      return listener

    return decorator

  @property
  def is_running(self) -> bool:
    """Whether the web server is running."""

    return self.__is_running

  async def start(self):
    """Tries to start the web server. Has no effect if the web server is already running."""

    if self.is_running:  # pragma: nocover
      return
    elif not len(self.__listeners):  # pragma: nocover
      warnings.warn('No listeners are registered.', RuntimeWarning)

    async def handler(request: web.Request) -> web.Response:
      body = None
      payload_type = None
      payload: Any = None

      try:
        assert request.body_exists and request.has_body and request.can_read_body

        body = await request.text()
        json_body = json.loads(body)

        payload_type = PayloadType(json_body['type'])
        payload = payload_type._deserialize(json_body['data'])
      except (KeyError, ValueError):
        return web.json_response({'error': 'Invalid request body'}, status=422)
      except web.HTTPRequestEntityTooLarge:  # pragma: nocover
        return web.json_response({'error': 'Request body too large'}, status=413)
      except Exception:
        return web.json_response({'error': 'Unable to parse request body'}, status=400)

      signature = request.headers.get('x-topgg-signature')
      trace = request.headers.get('x-topgg-trace')

      if not signature or not trace:
        return web.json_response({'error': 'Missing signature'}, status=401)

      fail_status = 400

      try:
        signature = {
          key: value
          for key, value in map(lambda part: part.split('='), signature.split(','))
        }

        fail_status = 422

        t = signature['t']
        signature = signature[API_VERSION]

        assert t and signature

        fail_status = 400

        hm = hmac.new(self.__secret, f'{t}.{body}'.encode('utf-8'), digestmod=sha256)

        fail_status = 403

        assert hm.hexdigest() == signature
      except RuntimeError:  # pragma: nocover
        return web.json_response({'error': 'Internal Server Error'}, status=500)
      except Exception:
        return web.json_response({'error': 'Invalid signature'}, status=fail_status)

      response = None

      for listener in self.__listeners.get(payload_type, ()):
        response = (await listener(payload, trace)) or response

      return response or web.Response(status=204)

    if isinstance(self.__app, web.Application):  # pragma: nocover
      self.__app.router.add_post(self.__route, handler)

      runner = web.AppRunner(self.__app)

      await runner.setup()

      self.__web_server = web.TCPSite(runner, self.__host, self.__port)

      await self.__web_server.start()
    else:
      self.__app.app.router.add_post(self.__route, handler)

      await self.__app.start_server()

    self.__is_running = True

  async def close(self) -> None:
    """Stops the web server."""

    if self.is_running:
      if self.__web_server is not None:  # pragma: nocover
        await self.__web_server.stop()

      if isinstance(self.__app, test_utils.TestClient):
        await self.__app.close()

      self.__is_running = False
