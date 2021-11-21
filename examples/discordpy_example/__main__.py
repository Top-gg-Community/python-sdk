import discord

import topgg

from .callbacks import autopost, webhook

client = discord.Client()
webhook_manager = topgg.WebhookManager().set_data(client).endpoint(webhook.endpoint)
dblclient = topgg.DBLClient("TOPGG_TOKEN").set_data(client)
autoposter: topgg.AutoPoster = (
    dblclient.autopost()
    .on_success(autopost.on_autopost_success)
    .on_error(autopost.on_autopost_error)
    .stats(autopost.stats)
)


@client.event
async def on_ready():
    assert client.user is not None
    dblclient.default_bot_id = client.user.id

    # if it's ready, then the event loop's run,
    # hence it's safe starting the autopost here
    if not autoposter.is_running:
        # don't await unless you want to wait the autopost loop to get finished
        autoposter.start()

    # we can also start the webhook here
    if not webhook_manager.is_running:
        await webhook_manager.start(6000)


client.run("TOKEN")
