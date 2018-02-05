DBL Python Library
==================

A simple API wrapper for `discordbots.org`_ written in Python

Installation
------------

Install via pip (recommended) [NOT WORKING YET]

.. code:: bash

    pip install dblpy

Install from source

.. code:: bash

    git clone https://github.com/DiscordBotList/DBL-Python-Library
    cd DBL-Python-Library
    pip install -R requirements.txt

Example
-------

.. code:: py

    from dbl import Client as dbl
    import asyncio
    import aiohttp

    botid = 264811613708746752  # your bots user id (client id on newer bots)
    token = 'abcxyz'            # obtainable from https://discordbots.org/api

    resp = await dbl().post_server_count(botid, token, 23)
    print(resp)

.. _discordbots.org: https://discordbots.org/
