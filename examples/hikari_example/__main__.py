import hikari

import topgg

from .callbacks import autopost, webhook

app = hikari.GatewayBot("TOKEN")
webhook_manager = topgg.WebhookManager().set_data(app).endpoint(webhook.endpoint)
dblclient = topgg.DBLClient("TOPGG_TOKEN").set_data(app)
autoposter: topgg.AutoPoster = (
    dblclient.autopost()
    .on_success(autopost.on_autopost_success)
    .on_error(autopost.on_autopost_error)
    .stats(autopost.stats)
)


@app.listen()
async def on_started(event: hikari.StartedEvent):
    me: hikari.OwnUser = event.app.get_me()
    assert me is not None
    dblclient.default_bot_id = me.id

    # since StartedEvent is a lifetime event
    # this event will only get dispatched once
    autoposter.start()
    await webhook_manager.start(6000)


@app.listen()
async def on_stopping(_: hikari.StoppingEvent):
    await dblclient.close()
    await webhook_manager.close()


app.run()
