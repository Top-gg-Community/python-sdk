#####################
Top.gg Python Library
#####################

.. image:: https://img.shields.io/pypi/v/topggpy.svg
   :target: https://pypi.python.org/pypi/topggpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/topggpy.svg
   :target: https://pypi.python.org/pypi/topggpy
   :alt: v1.0.0
.. image:: https://readthedocs.org/projects/topggpy/badge/?version=latest
   :target: https://topggpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

A simple API wrapper for `Top.gg <https://top.gg/>`_ written in Python, supporting discord.py.

Installation
------------

Install via pip (recommended)

.. code:: bash

    pip3 install topggpy

Install from source

.. code:: bash

    pip3 install git+https://github.com/top-gg/python-sdk/

Documentation
-------------

Documentation can be found `here <https://topggpy.rtfd.io>`_

Features
--------

* POST server count
* GET bot info, server count, upvote info
* GET all bots
* GET user info
* GET widgets (large and small) including custom ones. See `docs.top.gg <https://docs.top.gg/>`_ for more info.
* GET weekend status
* Built-in webhook to handle Top.gg votes
* Automated server count posting
* Searching for bots via the API

Additional information
----------------------

* Before using the webhook provided by this library, make sure that you have specified port open.
* Optimal values for port are between 1024 and 49151.
* If you happen to need help implementing topggpy in your bot, feel free to ask in the ``#development`` or ``#api`` channels in our `Discord server <https://discord.gg/EYHTgJX>`_.

Examples
--------

Posting server count manually every 30 minutes:
"""""""""""""""""""""""""""""""""""""""""""""""

.. code:: py

    from discord.ext import tasks

    import topgg

    # This example uses tasks provided by discord.ext to create a task that posts guild count to Top.gg every 30 minutes.

    dbl_token = 'Top.gg token'  # set this to your bot's Top.gg token
    bot.topggpy = topgg.DBLClient(bot, dbl_token)

    @tasks.loop(minutes=30)
    async def update_stats():
        """This function runs every 30 minutes to automatically update your server count."""
        try:
            await bot.topggpy.post_guild_count()
            print(f'Posted server count ({bot.topggpy.guild_count})')
        except Exception as e:
            print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    update_stats.start()

Using webhook:
""""""""""""""

.. code:: py

    import topgg

    # This example uses topggpy's webhook system.
    # The port must be a number between 1024 and 49151.

    bot.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook("/dblwebhook", "password")
    bot.topgg_webhook.run(5000)  # this method can be awaited as well

    @bot.event
    async def on_dbl_vote(data):
        """An event that is called whenever someone votes for the bot on Top.gg."""
        if data["type"] == "test":
            # this is roughly equivalent to
            # return await on_dbl_test(data) in this case
            return bot.dispatch('dbl_test', data)

        print(f"Received a vote:\n{data}")

    @bot.event
    async def on_dbl_test(data):
        """An event that is called whenever someone tests the webhook system for your bot on Top.gg."""
        print(f"Received a test vote:\n{data}")

With autopost:
""""""""""""""

.. code:: py

    import topgg

    # This example uses topggpy's autopost feature to post guild count to Top.gg every 30 minutes
    # as well as the shard count if applicable.

    dbl_token = 'Top.gg token'  # set this to your bot's Top.gg token
    bot.topggpy = topgg.DBLClient(bot, dbl_token, autopost=True, post_shard_count=True)

    @bot.event
    async def on_autopost_success():
        print(f'Posted server count ({bot.topggpy.guild_count}), shard count ({bot.shard_count})')
