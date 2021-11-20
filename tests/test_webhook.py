import typing as t

import aiohttp
import pytest

from topgg import WebhookManager, WebhookType
from topgg.types import BotVoteData, ServerVoteData

auth = "youshallnotpass"


@pytest.fixture
def webhook_manager() -> WebhookManager:
    return (
        WebhookManager()
        .endpoint(WebhookType.BOT)
        .auth(auth)
        .route("/dbl")
        .callback(print)
        .add_to_manager()
        .endpoint(WebhookType.GUILD)
        .auth(auth)
        .route("/dsl")
        .callback(print)
        .add_to_manager()
    )


def test_WebhookManager_routes(webhook_manager: WebhookManager) -> None:
    assert len(webhook_manager.app.router.routes()) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, result, state",
    [({"authorization": auth}, 200, True), ({}, 401, False)],
)
async def test_WebhookManager_validates_auth(
    webhook_manager: WebhookManager, headers: t.Dict[str, str], result: int, state: bool
) -> None:
    await webhook_manager.start(5000)

    try:
        for path in ("dbl", "dsl"):
            async with aiohttp.request(
                "POST", f"http://localhost:5000/{path}", headers=headers, json={}
            ) as r:
                assert r.status == result
    finally:
        await webhook_manager.close()
