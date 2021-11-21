import attr
import hikari


@attr.define(kw_only=True, weakref_slot=False)
class AutoPostSuccessEvent(hikari.Event):
    app: hikari.GatewayBot


@attr.define(kw_only=True, weakref_slot=False)
class AutoPostErrorEvent(hikari.Event):
    app: hikari.GatewayBot
    exception: Exception
