"""
The MIT License (MIT)

Copyright (c) 2021 Norizon & Top.gg
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

import asyncio
import datetime
import sys
import traceback
import typing as t

from . import errors

if t.TYPE_CHECKING:
    from .client import DBLClient
    from .types import StatsWrapper


CallbackT = t.Callable[..., t.Any]
StatsCallbackT = t.Callable[[], 'StatsWrapper']


class AutoPoster:
    """
    Automatically update the statistics in your Discord bot's Top.gg page every few minutes.

    Note that you should NOT instantiate this directly unless you know what you're doing. Generally, it's recommended to use the :meth:`.DBLClient.autopost` method instead.

    :param client: The client instance to use.
    :type client: :class:`.DBLClient`
    """

    __slots__ = (
        '_error',
        '_success',
        '_interval',
        '_task',
        'client',
        '_stats',
        '_stopping',
    )

    def __init__(self, client: 'DBLClient') -> None:
        super().__init__()

        self.client = client
        self._interval = 900
        self._error = self._default_error_handler
        self._refresh_state()

    def _default_error_handler(self, exception: Exception) -> None:
        print('Ignoring exception in auto post loop:', file=sys.stderr)

        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )

    @t.overload
    def on_success(self, callback: None) -> t.Callable[[CallbackT], CallbackT]: ...

    @t.overload
    def on_success(self, callback: CallbackT) -> 'AutoPoster': ...

    def on_success(self, callback: t.Any = None) -> t.Union[t.Any, 'AutoPoster']:
        """
        Registers an autopost success callback. The callback can be either sync or async.

        The callback is not required to take in arguments, but you can have injected :obj:`~.data.data`.
        This method can be used as a decorator or a decorator factory.

        .. code-block:: python

            # The following are valid.
            autoposter = client.autopost().on_success(lambda: print('Success!'))


            # Used as decorator, the decorated function will become the AutoPoster object.
            @autoposter.on_success
            def on_success() -> None: ...


            # Used as decorator factory, the decorated function will still be the function itself.
            @autoposter.on_success()
            def on_success() -> None: ...

        :param callback: The autoposter's new success callback.
        :type callback: Any

        :returns: The object itself if ``callback`` is not :py:obj:`None`, otherwise the decorator function.
        :rtype: Union[Any, :class:`.AutoPoster`]
        """

        if callback is not None:
            self._success = callback

            return self

        def decorator(callback: CallbackT) -> CallbackT:
            self._success = callback

            return callback

        return decorator

    @t.overload
    def on_error(self, callback: None) -> t.Callable[[CallbackT], CallbackT]: ...

    @t.overload
    def on_error(self, callback: CallbackT) -> 'AutoPoster': ...

    def on_error(self, callback: t.Any = None) -> t.Union[t.Any, 'AutoPoster']:
        """
        Registers an autopost error callback. The callback can be either sync or async.

        The callback is expected to take in the exception being raised, you can also have injected :obj:`~.data.data`.
        This method can be used as a decorator or a decorator factory.

        Note that if you don't provide an error callback, the default error handler will be called.

        .. code-block:: python

            # The following are valid.
            autoposter = client.autopost().on_error(lambda err: print(f'Error! {err!r}'))


            # Used as decorator, the decorated function will become the AutoPoster object.
            @autoposter.on_error
            def on_error(err: Exception) -> None: ...


            # Used as decorator factory, the decorated function will still be the function itself.
            @autoposter.on_error()
            def on_error(err: Exception) -> None: ...

        :param callback: The autoposter's new error callback.
        :type callback: Any

        :returns: The object itself if ``callback`` is not :py:obj:`None`, otherwise the decorator function.
        :rtype: Union[Any, :class:`.AutoPoster`]
        """
        if callback is not None:
            self._error = callback

            return self

        def decorator(callback: CallbackT) -> CallbackT:
            self._error = callback

            return callback

        return decorator

    @t.overload
    def stats(self, callback: None) -> t.Callable[[StatsCallbackT], StatsCallbackT]: ...

    @t.overload
    def stats(self, callback: StatsCallbackT) -> 'AutoPoster': ...

    def stats(self, callback: t.Any = None) -> t.Union[t.Any, 'AutoPoster']:
        """
        Registers a function that returns an instance of :class:`.StatsWrapper`. The callback can be either sync or async.

        The callback is not required to take in arguments, but you can have injected :obj:`~.data.data`.
        This method can be used as a decorator or a decorator factory.

        .. code-block:: python

            # The following are valid.
            autoposter = client.autopost().stats(lambda: topgg.StatsWrapper(bot.server_count))


            # Used as decorator, the decorated function will become the AutoPoster object.
            @autoposter.stats
            def get_stats() -> topgg.StatsWrapper:
                return topgg.StatsWrapper(bot.server_count)


            # Used as decorator factory, the decorated function will still be the function itself.
            @autoposter.stats()
            def get_stats() -> topgg.StatsWrapper:
                return topgg.StatsWrapper(bot.server_count)

        :param callback: The autoposter's new statistics callback.
        :type callback: Any

        :returns: The object itself if ``callback`` is not :py:obj:`None`, otherwise the decorator function.
        :rtype: Union[Any, :class:`.AutoPoster`]
        """

        if callback is not None:
            self._stats = callback

            return self

        def decorator(callback: StatsCallbackT) -> StatsCallbackT:
            self._stats = callback

            return callback

        return decorator

    @property
    def interval(self) -> float:
        """The interval between posting stats."""

        return self._interval

    @interval.setter
    def interval(self, seconds: t.Union[float, datetime.timedelta]) -> None:
        """Alias of :meth:`.AutoPoster.set_interval`."""

        self.set_interval(seconds)

    def set_interval(self, seconds: t.Union[float, datetime.timedelta]) -> 'AutoPoster':
        """
        Sets the interval between posting stats.

        :param seconds: The interval in seconds.
        :type seconds: Union[:py:class:`float`, :py:class:`~datetime.timedelta`]

        :exception ValueError: The provided interval is less than 900 seconds.

        :returns: The object itself.
        :rtype: :class:`.AutoPoster`
        """

        if isinstance(seconds, datetime.timedelta):
            seconds = seconds.total_seconds()

        if seconds < 900:
            raise ValueError('interval must be greated than 900 seconds.')

        self._interval = seconds

        return self

    @property
    def is_running(self) -> bool:
        """Whether the autoposter is running."""

        return self._task is not None and not self._task.done()

    def _refresh_state(self) -> None:
        self._task = None
        self._stopping = False

    def _fut_done_callback(self, future: 'asyncio.Future') -> None:
        self._refresh_state()

        if future.cancelled():
            return

        future.exception()

    async def _internal_loop(self) -> None:
        try:
            while 1:
                stats = await self.client._invoke_callback(self._stats)

                try:
                    await self.client.post_guild_count(stats)
                except Exception as err:
                    await self.client._invoke_callback(self._error, err)

                    if isinstance(err, errors.HTTPException) and err.code == 401:
                        raise err from None
                else:
                    if on_success := getattr(self, '_success', None):
                        await self.client._invoke_callback(on_success)

                if self._stopping:
                    return

                await asyncio.sleep(self.interval)
        finally:
            self._refresh_state()

    def start(self) -> 'asyncio.Task[None]':
        """
        Starts the autoposter loop.

        Note that this method must be called when the event loop is already running!

        :exception TopGGException: There's no callback provided or the autoposter is already running.

        :returns: The autoposter loop's :class:`~asyncio.Task`.
        :rtype: :class:`~asyncio.Task`.
        """

        if not hasattr(self, '_stats'):
            raise errors.TopGGException(
                'you must provide a callback that returns the stats.'
            )
        elif self.is_running:
            raise errors.TopGGException('The autoposter is already running.')

        self._task = task = asyncio.ensure_future(self._internal_loop())
        task.add_done_callback(self._fut_done_callback)

        return task

    def stop(self) -> None:
        """
        Stops the autoposter loop.

        Not to be confused with :meth:`.AutoPoster.cancel`, which stops the loop immediately instead of waiting for another post before stopping.
        """

        if not self.is_running:
            return

        self._stopping = True

    def cancel(self) -> None:
        """
        Cancels the autoposter loop.

        Not to be confused with :meth:`.AutoPoster.stop`, which waits for another post before stopping instead of stopping the loop immediately.
        """

        if self._task is None:
            return

        self._task.cancel()
        self._refresh_state()
