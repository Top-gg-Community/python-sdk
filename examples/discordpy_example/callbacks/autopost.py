import sys

import discord

import topgg


async def on_autopost_success(client: discord.Client = topgg.data(discord.Client)):
    # will be called whenever it successfully posting
    print("Successfully posted!")

    # do whatever with client
    client.dispatch("autopost_success")


async def on_autopost_error(
    exception: Exception, client: discord.Client = topgg.data(discord.Client)
):
    # will be called whenever it failed posting
    print("Failed to post", exception, file=sys.stderr)

    # do whatever with client
    client.dispatch("autopost_error", exception)


async def stats(client: discord.Client = topgg.data(discord.Client)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))
