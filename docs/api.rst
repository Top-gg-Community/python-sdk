.. currentmodule:: dbl

API Reference
===============

The following section outlines the API of topggpy.

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

    Called when guild count is posted on top.gg

.. function:: on_dbl_vote(data)

    Called when someone votes for your bot on top.gg

    :param data: The data with vote info returned in dict object

    Example: ::

        @bot.event
        async def on_dbl_vote(data):
            print(data)

    The returned data can be found `here`_.

    .. _here: https://docs.top.gg/webhooks

Widgets
-------

.. note:: General information about top.gg widgets can be in `top.gg docs`_.

In topggpy, :class:`DBLClient` has a :meth:`DBLClient.generate_widget` method that takes an ``options`` dictionary as a parameter.

All available values for each key:
    * ``bot_id``: ID of a bot to generate widget for. Must resolve to an ID of a valid bot when converted to a string;
    * ``format``: must be either ``png`` and ``svg``. Defaults to ``png``;
    * ``type``: used for short widgets (``). For large widget, must be an empty string;
    * ``noavatar``: indicates whether to exclude bot avatar from short widgets. Must be of type ``bool``;
    * ``colors``: a dictionary consisting of a parameter as a key and HEX color as value. ``color`` will be appended to the key in case ``key.endswith("color")`` returns False. All available fields are mentioned in `top.gg docs`_.

Example: ::

    print(await self.topggpy.generate_widget({
        "id": 270904126974590976,
        format: "svg",
        colors: {
            "username": 0xFFFFFF,
            "top": 0x000000
            }
        }))

.. _top.gg docs: https://top.gg/api/docs#widgets

Exceptions
----------

The following exceptions are thrown by the library.

.. autoexception:: TopGGException

.. autoexception:: UnauthorizedDetected

.. autoexception:: ClientException

.. autoexception:: HTTPException
    :members:

.. autoexception:: Unauthorized

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: ServerError
