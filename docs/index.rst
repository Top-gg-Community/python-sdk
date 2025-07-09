Top.gg Python SDK
=================

The community-maintained Python library for Top.gg.

Installation
------------

.. code-block:: shell

   $ pip install topggpy

Setting up
----------

Implicit cleanup
~~~~~~~~~~~~~~~~

.. code-block:: python

   import topgg

   import os


   async with topgg.Client(os.getenv('TOPGG_TOKEN')) as client:
     # ...

Explicit cleanup
~~~~~~~~~~~~~~~~

.. code-block:: python

   import topgg

   import os


   client = topgg.Client(os.getenv('TOPGG_TOKEN'))

   # ...

   await client.close()

Usage
-----

Getting a bot
~~~~~~~~~~~~~

.. code-block:: python

   bot = await client.get_bot(432610292342587392)

Getting several bots
~~~~~~~~~~~~~~~~~~~~

With defaults
^^^^^^^^^^^^^

.. code-block:: python

   bots = await client.get_bots()

   for bot in bots:
     print(bot)

With explicit arguments
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   bots = await client.get_bots(limit=250, offset=50, sort_by=topgg.SortBy.MONTHLY_VOTES)

   for bot in bots:
     print(bot)

Getting your bot's voters
~~~~~~~~~~~~~~~~~~~~~~~~~

First page
^^^^^^^^^^

.. code-block:: python

   voters = await client.get_voters()

   for voter in voters:
     print(voter)

Subsequent pages
^^^^^^^^^^^^^^^^

.. code-block:: python

   voters = await client.get_voters(2)

   for voter in voters:
     print(voter)

Check if a user has voted for your bot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   has_voted = await client.has_voted(661200758510977084)

Getting your bot's server count
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   posted_server_count = await client.get_server_count()

Posting your bot's server count
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   await client.post_server_count(bot.server_count)

Automatically posting your bot's server count every few minutes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @client.autopost_retrieval
   def get_server_count() -> int:
     return bot.server_count

   @client.autopost_success
   def success(server_count: int) -> None:
     print(f'Successfully posted {server_count} servers to Top.gg!')

   @client.autopost_error
   def error(error: topgg.Error) -> None:
     print(f'Error: {error!r}')

   client.start_autoposter()

   # ...

   client.stop_autoposter() # Optional

Checking if the weekend vote multiplier is active
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   is_weekend = await client.is_weekend()

Generating widget URLs
~~~~~~~~~~~~~~~~~~~~~~

Large
^^^^^

.. code-block:: python

   widget_url = topgg.widget.large(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

Votes
^^^^^

.. code-block:: python

   widget_url = topgg.widget.votes(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

Owner
^^^^^

.. code-block:: python

   widget_url = topgg.widget.owner(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

Social
^^^^^^

.. code-block:: python

   widget_url = topgg.widget.social(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

Webhooks
~~~~~~~~

Being notified whenever someone voted for your bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import topgg

   import asyncio
   import os


   webhooks = topgg.Webhooks(os.getenv('MY_TOPGG_WEBHOOK_SECRET'), 8080)

   @webhooks.on_vote('/votes')
   def voted(vote: topgg.Vote) -> None:
     print(f'A user with the ID of {vote.voter_id} has voted us on Top.gg!')

   async def main() -> None:
     await webhooks.start() # Starts the server
     await asyncio.Event().wait() # Keeps the server alive through indefinite blocking

   if __name__ == '__main__':
     asyncio.run(main())

.. toctree::
  :maxdepth: 2
  :hidden:

  client
  data
  webhooks
  support-server
  repository
  raw-api-reference