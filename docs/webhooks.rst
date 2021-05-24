.. currentmodule:: topgg

########
Webhooks
########

.. attention::

    In order for webhooks to work, the port you provide to :meth:`WebhookManager.run` must be accessible, meaning your firewall must allow incoming requests to it.

.. note::

    :class:`WebhookManager` exposes the internal webserver instance via the :attr:`WebhookManager.webserver` property.

WebhookManager
==============

.. autoclass:: WebhookManager
    :members:

Examples
========

Helper methods:
"""""""""""""""

.. code:: py

    import discord
    import topgg


    bot = discord.Client(...)  # Initialize a discord.py client
    # WebhookManager helper methods allow method chaining, therefore the lines below are valid
    bot.topgg_webhook = topgg.WebhookManager(bot)\
                        .dbl_webhook("/dbl", "dbl_auth")\
                        .dsl_webhook("/dsl", "dsl_auth")


Via the :attr:`webserver <WebhookManager.webserver>` property:
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

You can utilize the internal :class:`aiohttp.web.Application` via the :attr:`WebhookManager.webserver` property to add custom routes manually.

.. code:: py

    import discord
    import topgg
    from aiohttp import web

    dbl_auth = "Your DBL Authorization key"  # Leave empty to allow all requests

    bot = discord.Client(...)  # Initialize a discord.py client

    async def bot_vote_handler(request):
        auth = request.headers.get("Authorization", "")  # Default value will be empty string to allow all requests
        if auth == dbl_auth:
            # Process the vote and return response code 2xx
            return web.Response(status=200, text="OK")
        # Return code 401 if authorization fails
        # 4xx response codes tell Top.gg services not to retry the request
        return web.Response(status=401, text="Authorization failed")

    bot.topgg_webhook = topgg.WebhookManager(bot)
    bot.topgg_webhook.webserver.router.add_post(path="/dbl", handler=bot_vote_handler)
