.. currentmodule:: topgg

API Reference
=============

The following section outlines the API of topggpy.

Version Related Info
--------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are 'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'0.1.0'``.

Client
------

.. autoclass:: DBLClient
    :members:

Event reference
---------------

.. function:: on_autopost_success()

    Called when autopost posts server count successfully on Top.gg.

.. function:: on_autopost_error(exception)

    Called when autopost raises an exception during server count posting.

    :param exception: The raised exception object.

.. function:: on_dbl_vote(data)
              on_dsl_vote(data)

    Called when someone votes for your bot on Top.gg.

    :param data: The data with vote info returned in dict object.

    Example: ::

        @bot.event
        async def on_dbl_vote(data):
            print(data)

    The returned data can be found `in Top.gg docs <https://docs.top.gg/resources/webhooks/#bot-webhooks>`_.

Widgets
-------

.. General information about Top.gg widgets can be in `Top.gg docs`_.

In topggpy, :class:`DBLClient` has a :meth:`DBLClient.generate_widget` method that takes an ``options`` dictionary as a parameter.

All available values for each key:
    * ``bot_id``: ID of a bot to generate widget for. Must resolve to an ID of a listed bot when converted to a string;
    * ``format``: must be either ``png`` and ``svg``. Defaults to ``png``;
    * ``type``: used for short widgets (``). For large widget, must be an empty string;
    * ``noavatar``: indicates whether to exclude bot avatar from short widgets. Must be of type ``bool``;
    * ``colors``: a dictionary consisting of a parameter as a key and HEX color as value. ``color`` will be appended to the key in case ``key.endswith("color")`` returns False.

Example: ::

    print(await self.topggpy.generate_widget({
        "id": 270904126974590976,
        format: "svg",
        colors: {
            "username": 0xFFFFFF,
            "top": 0x000000
            }
        }))

Webhooks
--------

.. attention::

    In order for webhooks to work, the port you provide to :meth:`WebhookManager.run` must be accessible, meaning your firewall must allow incoming requests to it.

.. note::

    :class:`WebhookManager` exposes the internal webserver instance via the :attr:`WebhookManager.webserver` property as well as helper methods.

.. autoclass:: WebhookManager
    :members:

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
