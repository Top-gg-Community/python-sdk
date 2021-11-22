import logging

import hikari

import topgg

# from ..events.autopost import AutoPostErrorEvent, AutoPostSuccessEvent

_LOGGER = logging.getLogger("callbacks.autopost")

# these functions can be async too!
def on_autopost_success(
    # uncomment this if you want to get access to app
    # app: hikari.GatewayBot = topgg.data(hikari.GatewayBot),
):
    # will be called whenever it successfully posting
    _LOGGER.info("Successfully posted!")

    # do whatever with app
    # you can dispatch your own event for more callbacks
    # app.dispatch(AutoPostSuccessEvent(app=app))


def on_autopost_error(
    exception: Exception,
    # uncomment this if you want to get access to app
    # app: hikari.GatewayBot = topgg.data(hikari.GatewayBot),
):
    # will be called whenever it failed posting
    _LOGGER.error("Failed to post...", exc_info=exception)

    # do whatever with app
    # you can dispatch your own event for more callbacks
    # app.dispatch(AutoPostErrorEvent(app=app, exception=exception))


def stats(app: hikari.GatewayBot = topgg.data(hikari.GatewayBot)):
    return topgg.StatsWrapper(
        guild_count=len(app.cache.get_guilds_view()), shard_count=app.shard_count
    )
