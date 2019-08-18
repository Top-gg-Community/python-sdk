.. currentmodule:: dbl
.. _whats_new:


What's New
==========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _changelog:

v0.3.1
------
* Added ``on_guild_post``, an event that is called when autoposter successfully posts guild count
* Renamed ``get_upvote_info`` to ``get_bot_upvotes``
* Added ``get_user_vote``

v0.3.0
------
* :class:`DBLClient` now has ``autopost`` kwarg that will post server count automatically every 30 minutes
* Fixed code 403 errors
* Added ``on_dbl_vote``, an event that is called when you test your webhook
* Added ``on_dbl_test``, an event that is called when someone tests your webhook

v0.2.1
------

* Added webhook
* Removed support for discord.py versions lower than 1.0.0
* Made :meth:`DBLClient.get_weekend_status` return a boolean value
* Added webhook example in README
* Removed ``post_server_count`` and ``get_server_count``

v0.2
----

* Added ``post_guild_count``
 * Made ``post_server_count`` an alias for ``post_guild_count``
* Added ``get_guild_count``
 * Made ``get_server_count`` an alias for ``get_guild_count``
* Added :meth:`DBLClient.get_weekend_status`
* Removed all parameters from :meth:`DBLClient.get_upvote_info`
* Added limit to :meth:`DBLClient.get_bots`
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