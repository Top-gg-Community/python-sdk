import attr
import hikari


@attr.define(kw_only=True, weakref_slot=False)
class AutoPostSuccess(hikari.Event):
    app: hikari.GatewayBot


@attr.define(kw_only=True, weakref_slot=False)
class AutoPostError(hikari.Event):
    app: hikari.GatewayBot
    exception: Exception
