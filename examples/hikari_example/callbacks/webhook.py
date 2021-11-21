import hikari

import topgg


@topgg.endpoint("/dblwebhook", topgg.WebhookType.BOT, "youshallnotpass")
async def endpoint(
    vote_data: topgg.BotVoteData, app: hikari.GatewayBot = topgg.data(hikari.GatewayBot)
):
    # do anything with app here.
    # this function will be called whenever someone votes for your bot.
    raise NotImplementedError
