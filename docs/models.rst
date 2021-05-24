.. currentmodule:: topgg.types

###########
Data models
###########

This section explains data models used in topggpy to represent data received from Top.gg.

.. note::
    All listed models subclass :obj:`py:dict` and allow retrieving data via attributes *and* keys (i.e., both ``response['id']`` and ``response.id`` are valid).

DataDict
========

.. autoclass:: DataDict
    :members:
    :show-inheritance:

BotData
=======

.. autoclass:: BotData
    :members:
    :show-inheritance:

UserData
========

.. autoclass:: UserData
    :members:
    :show-inheritance:

SocialData
==========

.. autoclass:: SocialData
    :members:
    :show-inheritance:

BriefUserData
=============

.. autoclass:: BriefUserData
    :members:
    :show-inheritance:

BotStatsData
============

.. autoclass:: BotStatsData
    :members:
    :show-inheritance:

VoteDataDict
============

.. autoclass:: VoteDataDict
    :members:
    :show-inheritance:

BotVoteData
===========

.. autoclass:: BotVoteData
    :members:
    :show-inheritance:

ServerVoteData
==============

.. autoclass:: ServerVoteData
    :members:
    :show-inheritance:

WidgetOptions
=============

.. autoclass:: WidgetOptions
    :members:
    :show-inheritance:
