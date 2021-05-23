.. currentmodule:: topgg

Webhooks
========

.. attention::

    In order for webhooks to work, the port you provide to :meth:`WebhookManager.run` must be accessible, meaning your firewall must allow incoming requests to it.

.. note::

    :class:`WebhookManager` exposes the internal webserver instance via the :attr:`WebhookManager.webserver` property.

.. autoclass:: WebhookManager
    :members:

Example: ::

    bot = discord.Client(...)  # Initialize a discord.py client
    bot.topgg_webhook = topgg.WebhookManager(bot)
