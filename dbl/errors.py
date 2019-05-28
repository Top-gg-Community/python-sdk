# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2019 Assanali Mukhanov

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


class DBLException(Exception):
    """Base exception class for dblpy

    Ideally speaking, this could be caught to handle any exceptions thrown from this library.
    """
    pass


class ClientException(DBLException):
    """Exception that's thrown when an operation in the :class:`Client` fails.

    These are usually for exceptions that happened due to user input.
    """
    pass


class HTTPException(DBLException):
    """Exception that's thrown when an HTTP request operation fails.

    .. _aiohttp.ClientResponse: http://aiohttp.readthedocs.org/en/stable/client_reference.html#aiohttp.ClientResponse


    Attributes
    -----------
    response
        The response of the failed HTTP request. This is an
        instance of `aiohttp.ClientResponse`_.
    text: str
        The text of the error. Could be an empty string.
    """

    def __init__(self, response, message):
        self.response = response
        if isinstance(message, dict):
            self.text = message.get('message', '')
            self.code = message.get('code', 0)
        else:
            self.text = message

        fmt = '{0.reason} (status code: {0.status})'
        if self.text:
            fmt = fmt + ': {1}'

        super().__init__(fmt.format(self.response, self.text))


class Unauthorized(HTTPException):
    """Exception that's thrown for when status code 401 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class UnauthorizedDetected(DBLException):
    """Exception that's thrown when no API Token is provided

    Subclass of :exc:`DBLException`
    """
    pass


class Forbidden(HTTPException):
    """Exception that's thrown for when status code 403 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class NotFound(HTTPException):
    """Exception that's thrown for when status code 404 occurs.

    Subclass of :exc:`HTTPException`
    """
    pass


class InvalidArgument(ClientException):
    """Exception that's thrown when an argument to a function
    is invalid some way (e.g. wrong value or wrong type).

    This could be considered the analogous of ``ValueError`` and
    ``TypeError`` except derived from :exc:`ClientException` and thus
    :exc:`DBLException`.
    """
    pass


class ConnectionClosed(ClientException):
    """Exception that's thrown when the gateway connection is
    closed for reasons that could not be handled internally.

    Attributes
    -----------
    code : int
        The close code of the websocket.
    reason : str
        The reason provided for the closure.
    """

    def __init__(self, original):
        # This exception is just the same exception except
        # reconfigured to subclass ClientException for users
        self.code = original.code
        self.reason = original.reason
        super().__init__(str(original))
