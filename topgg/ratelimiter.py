# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg


from dataclasses import dataclass
from collections import deque
from time import time
import asyncio
import typing

if typing.TYPE_CHECKING:
  from types import TracebackType


@dataclass(repr=False, slots=True)
class Ratelimiter:
  """Handles ratelimits for a specific endpoint."""

  _max_calls: int
  _period: float = 1.0
  _calls: deque[float] = deque()
  _lock: asyncio.Lock = asyncio.Lock()

  async def __aenter__(self) -> 'Ratelimiter':
    """Delays the request to this endpoint if it could lead to a ratelimit."""

    async with self._lock:
      if len(self._calls) >= self._max_calls:
        until = time() + self._period - self._timespan

        if (sleep_time := until - time()) > 0:
          await asyncio.sleep(sleep_time)

      return self

  async def __aexit__(
    self,
    _exc_type: type[BaseException],
    _exc_val: BaseException,
    _exc_tb: 'TracebackType',
  ) -> None:
    """Stores the previous request's timestamp."""

    async with self._lock:
      self._calls.append(time())

      while self._timespan >= self._period:
        self._calls.popleft()

  @property
  def _timespan(self) -> float:
    """The timespan between the first call and last call."""

    return self._calls[-1] - self._calls[0]
