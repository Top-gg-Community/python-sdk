import aiohttp
import mock
import pytest
from discord import Client

from topgg import WebhookManager


def test_WebhookManager_routes():
    obj = (
        WebhookManager(mock.Mock(Client))
        .dbl_webhook("dbl", None)
        .dsl_webhook("dsl", None)
    )
    assert len(obj._webhooks) == 2


auth = "youshallnotpass"


@pytest.fixture
def webhook_manager():
    return WebhookManager(Client()).dbl_webhook("/dbl", auth)


@pytest.mark.asyncio
async def test_WebhookManager_run_method(webhook_manager):
    task = webhook_manager.run(5000)

    try:
        if not task.done():
            assert await task is None

        assert hasattr(webhook_manager, "_webserver")
    finally:
        await webhook_manager.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, result, state",
    [({"authorization": auth}, 200, True), ({}, 401, False)],
)
async def test_WebhookManager_validates_auth(webhook_manager, headers, result, state):
    await webhook_manager.run(5000)

    _state = False

    @webhook_manager.bot.event
    async def on_dbl_vote(data):
        nonlocal _state
        _state = True

    try:
        async with aiohttp.request(
            "POST", "http://localhost:5000/dbl", headers=headers, json={}
        ) as r:
            assert r.status == result

        assert _state is state
    finally:
        await webhook_manager.close()
