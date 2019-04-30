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

.. note::

    All of the following functions return their data as a JSON object (except widget generation)!

.. warning::

    `bot.wait_until_ready`_ method must be called before using this library!

    .. _bot.wait_until_ready: https://discordpy.readthedocs.io/en/latest/api.html#discord.Client.wait_until_ready

.. autoclass:: Client
    :members:

Exceptions
----------

The following exceptions are thrown by the library.

.. autoexception:: DBLException

.. autoexception:: UnauthorizedDetected

.. autoexception:: ClientException

.. autoexception:: HTTPException
    :members:

.. autoexception:: Unauthorized

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: InvalidArgument

.. autoexception:: ConnectionClosed
