import sys

import discord

import topgg


# these functions can be async too!
def on_autopost_success(
    # client: discord.Client = topgg.data(discord.Client)
):
    # will be called whenever it successfully posting
    print("Successfully posted!")

    # do whatever with client
    # you can dispatch your own event for more callbacks
    # client.dispatch("autopost_success")


def on_autopost_error(
    exception: Exception,
    # uncomment this if you want to get access to client
    # client: discord.Client = topgg.data(discord.Client),
):
    # will be called whenever it failed posting
    print("Failed to post", exception, file=sys.stderr)

    # do whatever with client
    # you can dispatch your own event for more callbacks
    # client.dispatch("autopost_error", exception)


def stats(client: discord.Client = topgg.data(discord.Client)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))
