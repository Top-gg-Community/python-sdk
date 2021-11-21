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

__all__ = ["WebhookEndpoint", "WebhookManager", "WebhookType"]

import enum
import typing as t

import aiohttp
from aiohttp import web

from topgg.errors import TopGGException

from .data import DataContainerMixin
from .types import BotVoteData, GuildVoteData


class WebhookType(enum.Enum):
    """An enum that represents the type of an endpoint."""

    BOT = enum.auto()
    """Marks the endpoint as a bot webhook."""

    GUILD = enum.auto()
    """Marks the endpoint as a guild webhook."""


class WebhookManager:
    """
    This class is used as a manager for the Top.gg webhook.
    """

    __app: web.Application
    _webserver: web.TCPSite
    _is_closed: bool
    __slots__ = ("__app", "_webserver", "_is_closed")

    def __init__(self) -> None:
        self.__app = web.Application()
        self._is_closed = False

    def endpoint(self, type_: WebhookType) -> "WebhookEndpoint":
        """Helper method that returns a WebhookEndpoint object.

        Parameters
        ----------
        type: WebhookType
            The type of the webhook, either BOT or GUILD

        Returns
        -------
        An instance of WebhookEndpoint: WebhookEndpoint
        """
        if not isinstance(type_, WebhookType):
            raise TypeError("provided type must be of WebhookType enum.")

        return WebhookEndpoint(type_, manager=self)

    async def start(self, port: int) -> None:
        """Runs the webhook.

        Parameters
        ----------
        port: int
            The port to run the webhook on.
        """
        runner = web.AppRunner(self.__app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, "0.0.0.0", port)
        await self._webserver.start()
        self._is_closed = False

    @property
    def app(self) -> web.Application:
        """Returns the internal web application that handles webhook requests.

        Returns
        --------
        :class:`aiohttp.web.Application`
            The internal web application.
        """
        return self.__app

    async def close(self) -> None:
        """Stops the webhook."""
        await self._webserver.stop()
        self._is_closed = True


CallbackT = t.Callable[..., t.Any]


class WebhookEndpoint(DataContainerMixin):
    """
    A helper class to setup webhook endpoint.

    Parameters
    ----------
    type_: WebhookType
        The type of the webhook.
    manager: WebhookManager
        The WebhookManager instance to register the endpoint to.
    """

    __slots__ = ("_callback", "manager", "_auth", "_route", "type")

    def __init__(self, type_: WebhookType, *, manager: WebhookManager) -> None:
        self.type = type_
        self.manager = manager
        self._auth = ""

    def route(self, route_: str) -> "WebhookEndpoint":
        """
        Sets the route of this endpoint.

        Parameters
        ----------
        route_: str
            The route of this endpoint.

        Returns
        -------
        self: WebhookEndpoint
        """
        self._route = route_
        return self

    def auth(self, auth_: str) -> "WebhookEndpoint":
        """
        Sets the auth of this endpoint.

        Parameters
        ----------
        auth_: str
            The auth of this endpoint.

        Returns
        -------
        self: WebhookEndpoint
        """
        self._auth = auth_
        return self

    @t.overload
    def callback(self, callback_: None) -> t.Callable[[CallbackT], CallbackT]:
        ...

    @t.overload
    def callback(self, callback_: CallbackT) -> "WebhookEndpoint":
        ...

    def callback(self, callback_: t.Any = None) -> t.Any:
        """
        Registers a vote callback, called whenever this endpoint receives POST requests.
        The callback can be either sync or async.
        This method can be used as a decorator or a decorator factory.

        Example
        -------
        .. code-block:: python

            import topgg

            webhook_manager = WebhookManager()
            endpoint = (
                webhook_manager
                .endpoint(topgg.WebhookType.BOT)
                .route("/dblwebhook")
                .auth("youshallnotpass")
            )

            # The following are valid.
            endpoint.callback(lambda vote_data: print("Receives a vote!", vote_data))

            # Used as decorator, the decorated function will become the AutoPoster object.
            @endpoint.callback
            def endpoint():
                ...

            # Used as decorator factory, the decorated function will still be the function itself.
            @endpoint.callback()
            def on_vote():
                ...

            endpoint.add_to_manager()
        """
        if callback_ is not None:
            self._callback = callback_
            return self

        return self.callback

    def add_to_manager(self) -> WebhookManager:
        """
        Adds this endpoint to the webhook manager.

        Returns
        -------
        webhook manager: WebhookManager

        Raises
        ------
        :obj:`errors.TopGGException`:
            If the callback / the route was unset.
        """
        if not hasattr(self, "_callback"):
            raise TopGGException(
                "callback was unset, please set it using the callback() method."
            )

        if not hasattr(self, "_route"):
            raise TopGGException(
                "route was unset, please set it using the route() method."
            )

        self.manager.app.router.add_post(self._route, self._handler)
        return self.manager

    async def _handler(self, request: aiohttp.web.Request) -> web.Response:
        auth = request.headers.get("Authorization", "")
        if auth == self._auth:
            data = await request.json()
            await self._invoke_callback(
                self._callback,
                (BotVoteData if self.type is WebhookType.BOT else GuildVoteData)(
                    **data
                ),
            )
            return web.Response(status=200, text="OK")

        return web.Response(status=401, text="Unauthorized")
