DBL Python Library
==================
.. image:: https://img.shields.io/pypi/v/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: v0.3.3
.. image:: https://readthedocs.org/projects/dblpy/badge/?version=latest
   :target: https://dblpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

A simple API wrapper for `top.gg`_ written in Python

Installation
------------

Install via pip (recommended)

.. code:: bash

    pip install dblpy

Install from source

.. code:: bash

    pip install git+https://github.com/top-gg/DBL-Python-Library

Documentation
-------------

Documentation can be found `here`_

Features
--------

* POST server count
* GET bot info, server count, upvote info
* GET all bots
* GET user info
* GET widgets (large and small) including custom ones. See `top.gg/api/docs`_ for more info.
* GET weekend status
* Built-in webhook to help you handle top.gg upvotes
* Automated server count posting
* Searching for bots via the API

Additional information
----------------------

* Before using the webhook provided by this library, make sure that you have specified port open.
* ``webhook_port`` must be between 1024 and 49151.
* Below examples are to be used as discord.py cogs. If you need help adding them to your bot, feel free to ask in the ``#development`` channel in our `Discord server`_.

Examples
--------

Posting server count manually:

.. code:: py

    from discord.ext import commands, tasks

    import dbl


    class TopGG(commands.Cog):
        """
        This example uses tasks provided by discord.ext to create a task that posts guild count to top.gg every 30 minutes.
        """

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token'  # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token)
            self.update_stats.start()

        def cog_unload(self):
            self.update_stats.cancel()

        @tasks.loop(minutes=30)
        async def update_stats(self):
            """This function runs every 30 minutes to automatically update your server count."""
            await self.bot.wait_until_ready()
            try:
                server_count = len(self.bot.guilds)
                await self.dblpy.post_guild_count(server_count)
                print('Posted server count ({})'.format(server_count))
            except Exception as e:
                print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))


    def setup(bot):
        bot.add_cog(TopGG(bot))


Using webhook:

.. code:: py

    from discord.ext import commands

    import dbl


    class TopGG(commands.Cog):
        """
        This example uses dblpy's webhook system.
        In order to run the webhook, at least webhook_port must be specified (number between 1024 and 49151).
        """

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token'  # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)

        @commands.Cog.listener()
        async def on_dbl_vote(self, data):
            """An event that is called whenever someone votes for the bot on top.gg."""
            print("Received an upvote:", "\n", data, sep="")

        @commands.Cog.listener()
        async def on_dbl_test(self, data):
            """An event that is called whenever someone tests the webhook system for your bot on top.gg."""
            print("Received a test upvote:", "\n", data, sep="")


    def setup(bot):
        bot.add_cog(TopGG(bot))


With autopost:

.. code:: py

    from discord.ext import commands

    import dbl


    class TopGG(commands.Cog):
        """
        This example uses dblpy's autopost feature to post guild count to top.gg every 30 minutes.
        """

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token'  # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)  # Autopost will post your guild count every 30 minutes

        @commands.Cog.listener()
        async def on_guild_post(self):
            print("Server count posted successfully")


    def setup(bot):
        bot.add_cog(TopGG(bot))


.. _top.gg: https://top.gg/
.. _top.gg/api/docs: https://top.gg/api/docs
.. _here: https://dblpy.rtfd.io
.. _Discord server: https://discord.gg/EYHTgJX