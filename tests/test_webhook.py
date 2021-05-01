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


@pytest.mark.asyncio
async def test_WebhookManager_auth_validates():
    auth = "youshallnotpass"
    obj = WebhookManager(mock.Mock(Client)).dbl_webhook("/dbl", auth)

    await obj.run(5000)

    async with aiohttp.ClientSession() as session:
        assert (
            await session.post(
                "http://localhost:5000/dbl", headers={"authorization": auth}, json={}
            )
        ).status == 200
        assert (await session.post("http://localhost:5000/dbl", json={})).status == 401

    await obj._webserver.stop()
