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

from typing import Optional


class TopGGException(Exception):
    """An error coming from this SDK. Extends :py:class:`Exception`."""

    __slots__: tuple[str, ...] = ()


class ClientException(TopGGException):
    """An operation failure in :class:`.DBLClient`. Extends :class:`.TopGGException`."""

    __slots__: tuple[str, ...] = ()


class ClientStateException(ClientException):
    """Attempted operation in a closed :class:`.DBLClient` instance. Extends :class:`.ClientException`."""

    __slots__: tuple[str, ...] = ()


class HTTPException(TopGGException):
    """HTTP request failure. Extends :class:`.TopGGException`."""

    __slots__: tuple[str, ...] = ('message', 'code')

    message: Optional[str]
    """The message returned from the API."""

    code: Optional[int]
    """The status code returned from the API."""

    def __init__(self, message: Optional[str], code: Optional[int]):
        self.message = message
        self.code = code

        super().__init__(f'Got {code}: {message!r}')

    def __repr__(self) -> str:
        return f'<{__class__.__name__} message={self.message!r} code={self.code}>'


class Ratelimited(HTTPException):
    """Ratelimited from sending more requests. Extends :class:`.HTTPException`."""

    __slots__: tuple[str, ...] = ('retry_after',)

    retry_after: float
    """How long the client should wait in seconds before it could send requests again without receiving a 429."""

    def __init__(self, retry_after: float):
        super().__init__(
            f'Blocked from sending more requests, try again in {retry_after} seconds.',
            429,
        )

        self.retry_after = retry_after

    def __repr__(self) -> str:
        return f'<{__class__.__name__} retry_after={self.retry_after}>'
