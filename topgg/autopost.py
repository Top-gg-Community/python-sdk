# The MIT License (MIT)

# Copyright (c) 2021 Norizon

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

__all__ = ["AutoPoster"]

import asyncio
import datetime
import sys
import traceback
import typing as t

from topgg import errors

from .data import DataContainerMixin
from .types import StatsWrapper

if t.TYPE_CHECKING:
    from .client import DBLClient

CallbackT = t.Callable[..., t.Any]
StatsCallbackT = t.Callable[[], StatsWrapper]


class AutoPoster(DataContainerMixin):
    __slots__ = (
        "_error",
        "_success",
        "_interval",
        "_task",
        "client",
        "_stats",
        "_stopping",
    )

    _success: CallbackT
    _stats: CallbackT
    _interval: float

    def __init__(self, client: "DBLClient") -> None:
        super().__init__()
        self.client = client
        self._data = {**client._data, type(self): self}
        self._interval: float = 900
        self._task: t.Optional["asyncio.Task[None]"] = None
        self._stopping = False
        self._error = self._default_error_handler

    def _default_error_handler(self, exception: Exception) -> None:
        print("Ignoring exception in auto post loop:", file=sys.stderr)
        traceback.print_exception(
            type(exception), exception, exception.__traceback__, file=sys.stderr
        )

    @t.overload
    def on_success(self, callback: None) -> t.Callable[[CallbackT], CallbackT]:
        ...

    @t.overload
    def on_success(self, callback: CallbackT) -> "AutoPoster":
        ...

    def on_success(self, callback: t.Any = None) -> t.Any:
        if callback is not None:
            self._success = callback
            return self

        return self.on_success

    @t.overload
    def on_error(self, callback: None) -> t.Callable[[CallbackT], CallbackT]:
        ...

    @t.overload
    def on_error(self, callback: CallbackT) -> "AutoPoster":
        ...

    def on_error(self, callback: t.Any = None) -> t.Any:
        if callback is not None:
            self._error = callback  # type: ignore
            return self

        return self.on_error

    @t.overload
    def stats(self, callback: None) -> t.Callable[[StatsCallbackT], StatsCallbackT]:
        ...

    @t.overload
    def stats(self, callback: StatsCallbackT) -> "AutoPoster":
        ...

    def stats(self, callback: t.Any = None) -> t.Any:
        if callback is not None:
            self._stats = callback
            return self

        return self.stats

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, seconds: t.Union[float, datetime.timedelta]) -> None:
        self.set_interval(seconds)

    def set_interval(self, seconds: t.Union[float, datetime.timedelta]) -> "AutoPoster":
        if isinstance(seconds, datetime.timedelta):
            seconds = seconds.total_seconds()

        if seconds < 900:
            raise ValueError("interval must be greated than 900 seconds.")

        self._interval = seconds
        return self

    @property
    def is_running(self) -> bool:
        return self._task is not None and self._task.done()

    async def _internal_loop(self) -> None:
        try:
            while 1:
                stats = await self._invoke_callback(self._stats)
                try:
                    await self.client.post_guild_count(stats)
                except Exception as err:
                    await self._invoke_callback(self._error, err)
                    if isinstance(err, errors.Unauthorized):
                        raise err from None
                else:
                    on_success = getattr(self, "_success", None)
                    if on_success:
                        await self._invoke_callback(on_success)

                if self._stopping:
                    self._stopping = False
                    return None

                await asyncio.sleep(self.interval)
        finally:
            self._task = None

    def start(self) -> "asyncio.Task[None]":
        if not hasattr(self, "_stats"):
            raise errors.TopGGException(
                "you must provide a callback that returns the stats."
            )

        if self._task:
            raise errors.TopGGException("the autopost is already running.")

        self._task = task = asyncio.ensure_future(self._internal_loop())
        return task

    def stop(self) -> None:
        self._stopping = True
        return None

    def cancel(self) -> None:
        if self._task is None:
            return

        self._task.cancel()
        self._task = None
        return None
