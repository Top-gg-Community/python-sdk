.. currentmodule:: dbl
.. _whats_new:


What's New
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _vp0p2p1:

v0.2.1
------

* Added webhook
* Removed support for discord.py versions lower than 1.0.0
* Made `get_weekend_status`_ return a boolean value
* Added webhook example in README
* Removed ``post_server_count`` and ``get_server_count``

v0.2
----

* Added ``post_guild_count``
 * Made ``post_server_count`` an alias for ``post_guild_count``
* Added ``get_guild_count``
 * Made ``get_server_count`` an alias for ``get_guild_count``
* Added `get_weekend_status`_
* Removed all parameters from `get_upvote_info`_
* Added limit to `get_bots`_
* Fixed example in README

v0.1.6
------

* Bug fixes & improvements

v0.1.4
------

* Initial ratelimit handling

v0.1.3
------

* Added documentation
* Fixed some minor bugs

v0.1.2
------

Initial release

* Working

    * POSTing server count
    * GET bot info, server count, upvote count, upvote info
    * GET all bots
    * GET specific user info
    * GET widgets (large and small) including custom ones. See `discordbots.org/api/docs`_ for more info.

* Not Working / Implemented

    * Searching for bots via the api

.. _discordbots.org/api/docs: https://discordbots.org/api/docs
.. _get_weekend_status: https://dbl-python-library.rtfd.io/en/latest/api.html#dbl.Client.get_weekend_status
.. _get_bots: https://dbl-python-library.rtfd.io/en/latest/api.html#dbl.Client.get_bots
.. _get_upvote_info: https://dbl-python-library.rtfd.io/en/latest/api.html#dbl.Client.get_upvote_info