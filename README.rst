DBL Python Library
==================
.. image:: https://img.shields.io/pypi/v/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: v0.4.0
.. image:: https://readthedocs.org/projects/dblpy/badge/?version=latest
   :target: https://dblpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

A simple API wrapper for `Top.gg <https://top.gg/>`_ written in Python, supporting discord.py.

Installation
------------

Install via pip (recommended)

.. code:: bash

    pip3 install dblpy

Install from source

.. code:: bash

    pip3 install git+https://github.com/top-gg/python-sdk/

Documentation
-------------

Documentation can be found `here <https://dblpy.rtfd.io>`_

Features
--------

* POST server count
* GET bot info, server count, upvote info
* GET all bots
* GET user info
* GET widgets (large and small) including custom ones. See `docs.top.gg <https://docs.top.gg/>`_ for more info.
* GET weekend status
* Built-in webhook to help you handle Top.gg upvotes
* Automated server count posting
* Searching for bots via the API

Additional information
----------------------

* Before using the webhook provided by this library, make sure that you have specified port open.
* ``webhook_port`` should be between 1024 and 49151.
* If you happen to need help implementing topggpy in your bot, feel free to ask in the ``#development`` or ``#api`` channels in our `Discord server <https://discord.gg/EYHTgJX>`_.

Examples
--------

Posting server count manually every 30 minutes:
===============================================

.. code:: py

    from discord.ext import tasks

    import dbl

    # This example uses tasks provided by discord.ext to create a task that posts guild count to Top.gg every 30 minutes.

    dbl_token = 'Top.gg token'  # set this to your bot's Top.gg token
    bot.dblpy = dbl.DBLClient(bot, dbl_token)

    @tasks.loop(minutes=30)
    async def update_stats():
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await bot.dblpy.post_guild_count()
            print(f'Posted server count ({bot.dblpy.guild_count})')
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    update_stats.start()


Using webhook:
==============

.. code:: py

    import dbl

    # This example uses dblpy's webhook system.
    # In order to run the webhook, at least webhook_port argument must be specified (number between 1024 and 49151).

    dbl_token = 'Top.gg token'  # set this to your bot's Top.gg token
    bot.dblpy = dbl.DBLClient(bot, dbl_token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)

    @bot.event
    async def on_dbl_vote(data):
        """An event that is called whenever someone votes for the bot on Top.gg."""
        print(f"Received an upvote:\n{data}")

    @bot.event
    async def on_dbl_test(data):
        """An event that is called whenever someone tests the webhook system for your bot on Top.gg."""
        print(f"Received a test upvote:\n{data}")


With autopost:
==============

.. code:: py

    import dbl

    # This example uses dblpy's autopost feature to post guild count to Top.gg every 30 minutes.

    dbl_token = 'Top.gg token'  # set this to your bot's Top.gg token
    bot.dblpy = dbl.DBLClient(bot, dbl_token, autopost=True)

    @bot.event
    async def on_guild_post():
        print(f'Posted server count ({bot.dblpy.guild_count})')
