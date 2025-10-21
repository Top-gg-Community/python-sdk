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

import enum
import typing as t
from aiohttp import web

from .errors import TopGGException
from .data import DataContainerMixin
from .types import BotVoteData, GuildVoteData

if t.TYPE_CHECKING:
    from aiohttp.web import Request, StreamResponse

T = t.TypeVar("T", bound="WebhookEndpoint")
_HandlerT = t.Callable[["Request"], t.Awaitable["StreamResponse"]]


class WebhookType(enum.Enum):
    """Marks the type of a webhook endpoint."""

    __slots__: tuple[str, ...] = ()

    BOT = enum.auto()
    """Marks the endpoint as a Discord bot webhook."""

    GUILD = enum.auto()
    """Marks the endpoint as a Discord server webhook."""


class WebhookManager(DataContainerMixin):
    """A Top.gg webhook manager."""

    __slots__: tuple[str, ...] = ("__app", "_webserver", "_is_running")

    def __init__(self) -> None:
        super().__init__()

        self.__app = web.Application()
        self._is_running = False

    def __repr__(self) -> str:
        return f"<{__class__.__name__} is_running={self.is_running}>"

    @t.overload
    def endpoint(self, endpoint_: None = None) -> "BoundWebhookEndpoint": ...

    @t.overload
    def endpoint(self, endpoint_: "WebhookEndpoint") -> "WebhookManager": ...

    def endpoint(
        self, endpoint_: t.Optional["WebhookEndpoint"] = None
    ) -> t.Union["WebhookManager", "BoundWebhookEndpoint"]:
        """
        A helper method that returns a :class:`.WebhookEndpoint` object.

        :param endpoint_: The endpoint to add.
        :type endpoint_: Optional[:class:`.WebhookEndpoint`]

        :exception TopGGException: If the endpoint is not :py:obj:`None` and is not an instance of :class:`.WebhookEndpoint`.

        :returns: An instance of :class:`.WebhookManager` if an endpoint was provided, otherwise :class:`.BoundWebhookEndpoint`.
        :rtype: Union[:class:`.WebhookManager`, :class:`.BoundWebhookEndpoint`]
        """

        if endpoint_:
            if not hasattr(endpoint_, "_callback"):
                raise TopGGException("endpoint missing callback.")

            if not hasattr(endpoint_, "_type"):
                raise TopGGException("endpoint missing type.")

            if not hasattr(endpoint_, "_route"):
                raise TopGGException("endpoint missing route.")

            self.app.router.add_post(
                endpoint_._route,
                self._get_handler(
                    endpoint_._type, endpoint_._auth, endpoint_._callback
                ),
            )

            return self

        return BoundWebhookEndpoint(self)

    async def start(self, port: int) -> None:
        """
        Runs the webhook.

        :param port: The port to use.
        :type port: :py:class:`int`
        """

        runner = web.AppRunner(self.__app)
        await runner.setup()

        self._webserver = web.TCPSite(runner, "0.0.0.0", port)
        await self._webserver.start()

        self._is_running = True

    @property
    def is_running(self) -> bool:
        """Whether the webserver is running."""

        return self._is_running

    @property
    def app(self) -> web.Application:
        """The internal :class:`~aiohttp.web.Application` that handles web requests."""

        return self.__app

    async def close(self) -> None:
        """Stops the webhook."""

        await self._webserver.stop()
        self._is_running = False

    def _get_handler(
        self, type_: WebhookType, auth: str, callback: t.Callable[..., t.Any]
    ) -> _HandlerT:
        async def _handler(request: web.Request) -> web.Response:
            if request.headers.get("Authorization", "") != auth:
                return web.Response(status=401, text="Unauthorized")

            data = await request.json()

            await self._invoke_callback(
                callback,
                (BotVoteData if type_ is WebhookType.BOT else GuildVoteData)(data),
            )

            return web.Response(status=204, text="")

        return _handler


CallbackT = t.Callable[..., t.Any]


class WebhookEndpoint:
    """A helper class to setup a Top.gg webhook endpoint."""

    __slots__: tuple[str, ...] = ("_callback", "_auth", "_route", "_type")

    def __init__(self) -> None:
        self._auth = ""

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return self._callback(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{__class__.__name__} type={self._type!r} route={self._route!r}>"

    def type(self: T, type_: WebhookType) -> T:
        """
        Sets the type of this endpoint.

        :param type_: The endpoint's new type.
        :type type_: :class:`.WebhookType`

        :returns: The object itself.
        :rtype: :class:`.WebhookEndpoint`
        """

        self._type = type_

        return self

    def route(self: T, route_: str) -> T:
        """
        Sets the route of this endpoint.

        :param route_: The endpoint's new route.
        :type route_: :py:class:`str`

        :returns: The object itself.
        :rtype: :class:`.WebhookEndpoint`
        """

        self._route = route_

        return self

    def auth(self: T, auth_: str) -> T:
        """
        Sets the password of this endpoint.

        :param auth_: The endpoint's new password.
        :type auth_: :py:class:`str`

        :returns: The object itself.
        :rtype: :class:`.WebhookEndpoint`
        """

        self._auth = auth_

        return self

    @t.overload
    def callback(self, callback_: None) -> t.Callable[[CallbackT], CallbackT]: ...

    @t.overload
    def callback(self: T, callback_: CallbackT) -> T: ...

    def callback(self, callback_: t.Any = None) -> t.Union[t.Any, "WebhookEndpoint"]:
        """
        Registers a vote callback that gets called whenever this endpoint receives POST requests. The callback can be either sync or async.

        This method can be used as a decorator or a decorator factory.

        .. code-block:: python

            webhook_manager = topgg.WebhookManager()

            endpoint = (
                topgg.WebhookEndpoint()
                .type(topgg.WebhookType.BOT)
                .route("/dblwebhook")
                .auth("youshallnotpass")
            )

            # The following are valid.
            endpoint.callback(lambda vote: print(f"Got a vote: {vote!r}"))


            # Used as decorator, the decorated function will become the WebhookEndpoint object.
            @endpoint.callback
            def on_vote(vote: topgg.BotVoteData) -> None: ...


            # Used as decorator factory, the decorated function will still be the function itself.
            @endpoint.callback()
            def on_vote(vote: topgg.BotVoteData) -> None: ...


            webhook_manager.endpoint(endpoint)

            await webhook_manager.start(8080)

        :param callback_: The endpoint's new vote callback.
        :type callback_: Any

        :returns: The object itself if ``callback`` is not :py:obj:`None`, otherwise the object's own callback.
        :rtype: Union[Any, :class:`.WebhookEndpoint`]
        """

        if callback_ is not None:
            self._callback = callback_

            return self

        return self.callback


class BoundWebhookEndpoint(WebhookEndpoint):
    """
    A :class:`.WebhookEndpoint` with a :class:`.WebhookManager` bound to it.

    You can instantiate this object using the :meth:`.WebhookManager.endpoint` method.

    .. code-block:: python

        endpoint = (
            topgg.WebhookManager()
            .endpoint()
            .type(topgg.WebhookType.BOT)
            .route("/dblwebhook")
            .auth("youshallnotpass")
        )

        # The following are valid.
        endpoint.callback(lambda vote: print(f"Got a vote: {vote!r}"))


        # Used as decorator, the decorated function will become the BoundWebhookEndpoint object.
        @endpoint.callback
        def on_vote(vote: topgg.BotVoteData) -> None: ...


        # Used as decorator factory, the decorated function will still be the function itself.
        @endpoint.callback()
        def on_vote(vote: topgg.BotVoteData) -> None: ...


        endpoint.add_to_manager()

        await endpoint.manager.start(8080)

    :param manager: The webhook manager to use.
    :type manager: :class:`.WebhookManager`
    """

    __slots__: tuple[str, ...] = ("manager",)

    def __init__(self, manager: WebhookManager):
        super().__init__()

        self.manager = manager

    def __repr__(self) -> str:
        return f"<{__class__.__name__} manager={self.manager!r}>"

    def add_to_manager(self) -> WebhookManager:
        """
        Adds this endpoint to the webhook manager.

        :exception TopGGException: If the webhook manager is not :py:obj:`None` and is not an instance of :class:`.WebhookEndpoint`.

        :returns: The webhook manager used.
        :rtype: :class:`WebhookManager`
        """

        self.manager.endpoint(self)

        return self.manager


def endpoint(
    route: str, type: WebhookType, auth: str = ""
) -> t.Callable[[t.Callable[..., t.Any]], WebhookEndpoint]:
    """
    A decorator factory for instantiating a :class:`.WebhookEndpoint`.

    .. code-block:: python

        manager = topgg.WebhookManager()


        @topgg.endpoint("/dblwebhook", WebhookType.BOT, "youshallnotpass")
        async def on_vote(vote: topgg.BotVoteData): ...


        manager.endpoint(on_vote)

        await manager.start(8080)

    :param route: The endpoint's route.
    :type route: :py:class:`str`
    :param type: The endpoint's type.
    :type type: :class:`.WebhookType`
    :param auth: The endpoint's password.
    :type auth: :py:class:`str`

    :returns: The actual decorator.
    :rtype: Callable[[Callable[..., Any]], :class:`.WebhookEndpoint`]
    """

    def decorator(func: t.Callable[..., t.Any]) -> WebhookEndpoint:
        return WebhookEndpoint().route(route).type(type).auth(auth).callback(func)

    return decorator
