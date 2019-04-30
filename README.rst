DBL Python Library
==================
.. image:: https://img.shields.io/pypi/v/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: v0.2.1
.. image:: https://readthedocs.org/projects/dblpy/badge/?version=v0.1.6
   :target: http://dblpy.readthedocs.io/en/latest/?badge=v0.1.6
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

Working
-------

* POST server count
* GET bot info, server count, upvote count, upvote info
* GET all bots
* GET user info
* GET widgets (large and small) including custom ones. See `discordbots.org/api/docs`_ for more info.
* GET weekend status
* Webhook

Not Working /  Implemented
--------------------------

* Searching for bots via the api

Additional information
----------------------

Before using the webhook provided by this library, make sure that you have port 5000 open.

Examples
--------

.. code:: py

    import dbl
    import discord
    from discord.ext import commands

    import asyncio
    import logging


    class DiscordBotsOrgAPI(commands.Cog):
        """Handles interactions with the discordbots.org API"""

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token' # set this to your DBL token
            self.dblpy = dbl.Client(self.bot, self.token)
            self.updating = self.bot.loop.create_task(self.update_stats())

        async def update_stats(self):
            """This function runs every 30 minutes to automatically update your server count"""
            await self.bot.wait_until_ready() # this is important, do not touch it
            while self.bot.is_ready():
                logger.info('Attempting to post server count')
                try:
                    await self.dblpy.post_guild_count()
                    logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
                except Exception as e:
                    logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
                await asyncio.sleep(1800)

    def setup(bot):
        global logger
        logger = logging.getLogger('bot')
        bot.add_cog(DiscordBotsOrgAPI(bot))

.. code_webhooks:: py

    import dbl
    import discord
    from discord.ext import commands

    import asyncio
    import logging


    class DiscordBotsOrgAPI(commands.Cog):
        """Handles interactions with the discordbots.org API"""

        def __init__(self, bot):
            self.bot = bot
            self.token = 'dbl_token'  #  set this to your DBL token
            self.dblpy = dbl.Client(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)
            self.updating = self.bot.loop.create_task(self.update_stats())

        async def update_stats(self):
            """This function runs every 30 minutes to automatically update your server count"""
            await self.bot.wait_until_ready() # this is important, do not touch it
            while self.bot.is_ready():
                logger.info('Attempting to post server count')
                try:
                    await self.dblpy.post_guild_count()
                    logger.info('Posted server count ({})'.format(self.dblpy.guild_count()))
                except Exception as e:
                    logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))
                await asyncio.sleep(1800)

        @commands.Cog.listener()
        async def on_dbl_vote(self, data):
            print(data)

    def setup(bot):
        global logger
        logger = logging.getLogger('bot')
        bot.add_cog(DiscordBotsOrgAPI(bot))

.. _discordbots.org: https://discordbots.org/
.. _discordbots.org/api/docs: https://discordbots.org/api/docs
.. _here: http://dblpy.rtfd.io
