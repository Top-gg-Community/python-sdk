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

__all__ = [
    "TopGGException",
    "ClientException",
    "ClientStateException",
    "HTTPException",
    "Unauthorized",
    "UnauthorizedDetected",
    "Forbidden",
    "NotFound",
    "ServerError",
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


class HTTPException(TopGGException):
    """Exception that's thrown when an HTTP request operation fails.

    Attributes:
        response (:class:`aiohttp.ClientResponse`)
            The response of the failed HTTP request.
        text (str)
            The text of the error. Could be an empty string.
    """

    def __init__(self, response: "ClientResponse", message: Union[dict, str]) -> None:
        self.response = response
        if isinstance(message, dict):
            self.text = message.get("message", "")
            self.code = message.get("code", 0)
        else:
            self.text = message

        fmt = f"{self.response.reason} (status code: {self.response.status})"
        if self.text:
            fmt = f"{fmt}: {self.text}"

        super().__init__(fmt)


class Unauthorized(HTTPException):
    """Exception that's thrown when status code 401 occurs."""


class UnauthorizedDetected(TopGGException):
    """Exception that's thrown when no API Token is provided."""


class Forbidden(HTTPException):
    """Exception that's thrown when status code 403 occurs."""


class NotFound(HTTPException):
    """Exception that's thrown when status code 404 occurs."""


class ServerError(HTTPException):
    """Exception that's thrown when Top.gg returns "Server Error" responses (status codes such as 500 and 503)."""
