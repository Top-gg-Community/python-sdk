import logging
import sys

import hikari

import topgg

from ..events.autopost import AutoPostErrorEvent, AutoPostSuccessEvent

_LOGGER = logging.getLogger("callbacks.autopost")


async def on_autopost_success(
    app: hikari.GatewayBot = topgg.data(hikari.GatewayBot),
):
    # will be called whenever it successfully posting
    _LOGGER.info("Successfully posted!")

    # do whatever with app
    app.dispatch(AutoPostSuccessEvent(app=app))


async def on_autopost_error(
    exception: Exception, app: hikari.GatewayBot = topgg.data(hikari.GatewayBot)
):
    # will be called whenever it failed posting
    _LOGGER.error("Failed to post...", exc_info=exception)

    # do whatever with app
    app.dispatch(AutoPostErrorEvent(app=app, exception=exception))


async def stats(app: hikari.GatewayBot = topgg.data(hikari.GatewayBot)):
    return topgg.StatsWrapper(guild_count=len(app.cache.get_guilds_view()))
