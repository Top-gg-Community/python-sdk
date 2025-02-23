========
topggpy_
========

|pypi|_ |downloads|_

.. _topggpy: https://pypi.org/project/topggpy/
.. |pypi| image:: https://img.shields.io/pypi/v/topggpy.svg?style=flat-square
.. _pypi: https://pypi.org/project/topggpy/
.. |downloads| image:: https://img.shields.io/pypi/dm/topggpy?style=flat-square
.. _downloads: https://pypi.org/project/topggpy/

The community-maintained Python API wrapper for `Top.gg <https://top.gg/>`_.

Installation
------------

.. code-block:: console

  $ pip install topggpy

Example
-------

.. code-block:: python

  # Import the module.
  import topgg
  
  import asyncio
  import os
  

  async def main() -> None:
  
    # Declare the client. To retrieve your top.gg token, see https://docs.top.gg/docs/API/@reference.
    async with topgg.Client(os.getenv('TOPGG_TOKEN')) as tg:
      # Fetch a bot from its ID.
      bot = await tg.get_bot(432610292342587392)
  
      print(bot)
  
      # Fetch bots that matches the specified query.
      bots = (
        await tg.get_bots()
        .limit(250)
        .skip(50)
        .name('shiro')
        .sort_by_monthly_votes()
        .send()
      )
  
      for b in bots:
        print(b)
  
      # Post your bot's server count to the API. This will update the server count in your bot's Top.gg page.
      await tg.post_server_count(2)
  
      # Fetch your bot's posted server count.
      posted_server_count = await tg.get_server_count()
  
      # Fetch your bot's last 1000 voters.
      voters = await tg.get_voters()
  
      for voter in voters:
        print(voter)
  
      # Check if a user has voted your bot.
      has_voted = await tg.has_voted(661200758510977084)
  
      if has_voted:
        print('This user has voted!')
  
      # Check if the weekend multiplier is active.
      is_weekend = await tg.is_weekend()
  
      if is_weekend:
        print('The weekend multiplier is active!')
  
  
  if __name__ == '__main__':
    
    # See https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    # for more details.
    if os.name == 'nt':
      asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())

.. toctree::
  :maxdepth: 2
  :hidden:

  client
  data
  support-server
  repository
  raw-api-reference