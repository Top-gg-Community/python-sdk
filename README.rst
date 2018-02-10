DBL Python Library
==================
.. image:: https://img.shields.io/pypi/v/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: View on PyPi
.. image:: https://img.shields.io/pypi/pyversions/dblpy.svg
   :target: https://pypi.python.org/pypi/dblpy
   :alt: v0.1.3
.. image:: https://readthedocs.org/projects/dblpy/badge/?version=latest
   :target: http://dblpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


A simple API wrapper for `discordbots.org`_ written in Python

Installation
------------

Install via pip (recommended)

.. code:: bash

    pip install dblpy

Install from source

.. code:: bash

    git clone https://github.com/DiscordBotList/DBL-Python-Library
    cd DBL-Python-Library
    pip install -R requirements.txt

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

Not Working /  Implemented
--------------------------

* Searching for bots via the api

Example
-------

.. code:: py

    import dblpy
    from dblpy import Client
    import asyncio
    import aiohttp
    import json

    dbl = dblpy.Client()

    botid = 264811613708746752  # your bots user id (client id on newer bots)
    token = 'abcxyz'            # DBL Bot Token. Obtainable from https://discordbots.org/api

    class Example:
        def __init__(bot):
            bot = bot
            session = aiohttp.ClientSession(loop=bot.loop)

        async def poststats():
            await dblpy.post_server_count(botid, dbltoken, 65)

        async def getstats():
            resp = await dblpy.get_server_count(botid)
            print(json.dumps(resp))


.. _discordbots.org: https://discordbots.org/
.. _discordbots.org/api/docs: https://discordbots.org/api/docs
.. _here: http://dblpy.rtfd.io
