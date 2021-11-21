import discord

import topgg


@topgg.endpoint("/dblwebhook", topgg.WebhookType.BOT, "youshallnotpass")
async def endpoint(
    vote_data: topgg.BotVoteData, client: discord.Client = topgg.data(discord.Client)
):
    # do anything with client here.
    # this function will be called whenever someone votes for your bot.
    raise NotImplementedError
