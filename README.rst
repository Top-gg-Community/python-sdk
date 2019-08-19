DBL Python Library
==================
.. image:: https://img.shields.io/pypi/v/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: v0.3.1
.. image:: https://readthedocs.org/projects/dblpy/badge/?version=latest
   :target: https://dblpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

A simple API wrapper for `discordbots.org`_ written in Python

Installation
------------

Install via pip (recommended)

.. code:: bash

    pip install dblpy

Install from source

.. code:: bash

    pip install git+https://github.com/DiscordBotList/DBL-Python-Library

Documentation
-------------

Documentation can be found `here`_

Features
-------

* POST server count
* GET bot info, server count, upvote info
* GET all bots
* GET user info
* GET widgets (large and small) including custom ones. See `discordbots.org/api/docs`_ for more info.
* GET weekend status
* Built-in webhook to help you handle DBL upvotes
* Automated server count posting
* Searching for bots via the API

Additional information
----------------------

* Before using the webhook provided by this library, make sure that you have specified port open.
* ``webhook_port`` must be greater between 1024 and 49151.

Examples
--------

Without webhook:

.. code:: py

    import dbl
    import discord
    from discord.ext import commands, tasks

    import asyncio
    import logging


    class DBLAPI(commands.Cog):
        """Handles interactions with the discordbots.org API"""

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token' # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token)

        # The decorator below will work only on discord.py 1.1.0+
        # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats())

        @tasks.loop(minutes=30.0)
        async def update_stats(self):
            """This function runs every 30 minutes to automatically update your server count"""
            logger.info('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
            except Exception as e:
                logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

            # if you are not using the tasks extension, put the line below

            await asyncio.sleep(1800)

    def setup(bot):
        global logger
        logger = logging.getLogger('bot')
        bot.add_cog(DBLAPI(bot))

With webhook:

.. code:: py

    import dbl
    import discord
    from discord.ext import commands, tasks

    import asyncio
    import logging


    class DBLAPI(commands.Cog):
        """Handles interactions with the discordbots.org API"""

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token' # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)

        # The decorator below will work only on discord.py 1.1.0+
        # In case your discord.py version is below that, you can use self.bot.loop.create_task(self.update_stats())

        @tasks.loop(minutes=30.0)
        async def update_stats(self):
            """This function runs every 30 minutes to automatically update your server count"""
            logger.info('Attempting to post server count')
            try:
                await self.dblpy.post_guild_count()
                logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
            except Exception as e:
                logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

            # if you are not using the tasks extension, put the line below

            await asyncio.sleep(1800)

        @commands.Cog.listener()
        async def on_dbl_vote(self, data):
            logger.info('Received an upvote')
            print(data)

    def setup(bot):
        global logger
        logger = logging.getLogger('bot')
        bot.add_cog(DBLAPI(bot))

With autopost:

.. code:: py

    import dbl
    import discord
    from discord.ext import commands


    class DBLAPI(commands.Cog):
        """Handles interactions with the discordbots.org API"""

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token' # set this to your DBL token
            self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True) # Autopost will post your guild count every 30 minutes

        async def on_guild_post():
            print("Server count posted successfully")

    def setup(bot):
        bot.add_cog(DBLAPI(bot))

.. _discordbots.org: https://discordbots.org/
.. _discordbots.org/api/docs: https://discordbots.org/api/docs
.. _here: https://dblpy.rtfd.io
