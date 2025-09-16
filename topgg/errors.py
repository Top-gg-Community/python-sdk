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

__all__ = [
    "TopGGException",
    "ClientException",
    "ClientStateException",
    "Ratelimited",
    "HTTPException",
]

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse


class TopGGException(Exception):
    """Base exception class for topggpy.

    Ideally speaking, this could be caught to handle any exceptions thrown from this library.
    """


class ClientException(TopGGException):
    """Exception that's thrown when an operation in the :class:`~.DBLClient` fails.

    These are usually for exceptions that happened due to user input.
    """


class ClientStateException(ClientException):
    """Exception that's thrown when an operation happens in a closed :obj:`~.DBLClient` instance."""


class Ratelimited(TopGGException):
    """Exception that's thrown when the client is ratelimited."""
  
    __slots__: tuple[str, ...] = ('retry_after',)
  
    retry_after: float
    """How long the client should wait in seconds before it could send requests again without receiving a 429."""
  
    def __init__(self, retry_after: float):
        self.retry_after = retry_after
  
        super().__init__(
            f'Blocked from sending more requests, try again in {retry_after} seconds.'
        )


class HTTPException(TopGGException):
    """Exception that's thrown when an HTTP request operation fails.

    Attributes:
        response (:class:`aiohttp.ClientResponse`)
            The response of the failed HTTP request.
        text (str)
            The text of the error. Could be an empty string.
        code (int)
            The response status code.
    """

    __slots__ = ("response", "text", "code")

    def __init__(self, response: "ClientResponse", message: Union[dict, str]) -> None:
        self.response = response
        self.code = response.status
        self.text = message.get("message", message.get("detail", "")) if isinstance(message, dict) else message

        fmt = f"{self.response.reason} (status code: {self.response.status})"

        if self.text:
            fmt = f"{fmt}: {self.text}"

        super().__init__(fmt)

