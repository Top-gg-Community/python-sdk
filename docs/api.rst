.. currentmodule:: topgg

#############
API Reference
#############

The following section outlines the API of topggpy.

Version Related Info
====================

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are 'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'0.1.0'``.

Client
======

.. autoclass:: DBLClient
    :members:

Event reference
===============

.. function:: on_autopost_success()

    Called when autopost posts server count successfully on Top.gg.

.. function:: on_autopost_error(exception)

    Called when autopost raises an exception during server count posting.

    :param exception: The raised exception object.
    :type exception: Exception

.. function:: on_dbl_vote(data)

    Called when someone votes for your bot on Top.gg.

    :param data: The data model containing bot vote information.
    :type data: :ref:`BotVoteData`

    Example: ::

        @bot.event
        async def on_dbl_vote(data):
            print(data)

.. function:: on_dsl_vote(data)

    Called when someone votes for your server on Top.gg.

    :param data: The data model containing server vote information.
    :type data: :ref:`ServerVoteData`

    Example: ::

        @bot.event
        async def on_dsl_vote(data):
            print(data)

