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

from typing import Type, Tuple, Iterable
from types import TracebackType
from collections import deque
from time import time
import asyncio


class Ratelimiter:
  __slots__: Tuple[str, ...] = ('__lock', '__max_calls', '__period', '__calls')

  def __init__(
    self,
    max_calls: int,
    period: float = 1.0,
  ):
    self.__calls = deque()
    self.__period = period
    self.__max_calls = max_calls
    self.__lock = asyncio.Lock()

  async def __aenter__(self) -> 'Ratelimiter':
    async with self.__lock:
      if len(self.__calls) >= self.__max_calls:
        until = time() + self.__period - self._timespan

        if (sleep_time := until - time()) > 0:
          await asyncio.sleep(sleep_time)

      return self

  async def __aexit__(
    self,
    _exc_type: Type[BaseException],
    _exc_val: BaseException,
    _exc_tb: TracebackType,
  ) -> None:
    async with self.__lock:
      # Store the last operation timestamp.
      self.__calls.append(time())

      while self._timespan >= self.__period:
        self.__calls.popleft()

  @property
  def _timespan(self) -> float:
    return self.__calls[-1] - self.__calls[0]


class RatelimiterManager:
  __slots__: Tuple[str, ...] = ('__ratelimiters',)

  def __init__(self, ratelimiters: Iterable[Ratelimiter]):
    self.__ratelimiters = ratelimiters

  async def __aenter__(self) -> 'RatelimiterManager':
    for manager in self.__ratelimiters:
      await manager.__aenter__()

    return self

  async def __aexit__(
    self,
    exc_type: Type[BaseException],
    exc_val: BaseException,
    exc_tb: TracebackType,
  ) -> None:
    await asyncio.gather(
      *(manager.__aexit__(exc_type, exc_val, exc_tb) for manager in self.__ratelimiters)
    )
