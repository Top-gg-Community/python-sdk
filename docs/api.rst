.. currentmodule:: dbl

API Reference
===============

The following section outlines the API of dblpy.

Version Related Info
---------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to `sys.version_info`_.

    Just like `sys.version_info`_ the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

    .. _sys.version_info: https://docs.python.org/3.6/library/sys.html#sys.version_info

.. data:: __version__

    A string representation of the version. e.g. ``'0.1.0-alpha0'``.

Client
------

.. autoclass:: DBLClient
    :members:

Event reference
---------------

.. function:: on_guild_post()

    Called when guild count is posted on discordbots.org

.. function:: on_dbl_vote(data)

    Called when someone votes for your bot on discordbots.org

    :param data: The data with vote info returned in dict object

    Example: ::

        @bot.event
        async def on_dbl_vote(data):
            print(data)

    The data returned can be found `here`_

    .. _here: https://discordbots.org/api/docs#webhooks

.. function:: on_dbl_test(data)

    Called when someone tests webhook system for your bot on discordbots.org

    :param data: The data with test info returned in dict object

    Example: ::

        @bot.event
        async def on_dbl_test(data):
            print(data)

    The data returned can be found `here`_

    .. _here: https://discordbots.org/api/docs#webhooks

Exceptions
----------

The following exceptions are thrown by the library.

.. autoexception:: DBLException

.. autoexception:: UnauthorizedDetected

.. autoexception:: InvalidAuthorization

.. autoexception:: ClientException

.. autoexception:: HTTPException
    :members:

.. autoexception:: Unauthorized

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: InvalidArgument

.. autoexception:: ConnectionClosed
