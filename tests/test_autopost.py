import mock
import pytest
from aiohttp import ClientSession
from pytest_mock import MockerFixture

from topgg import DBLClient, StatsWrapper
from topgg.errors import Unauthorized


@pytest.fixture
def session() -> ClientSession:
    return mock.Mock(ClientSession)


@pytest.mark.asyncio
async def test_DBLClient_breaks_autopost_loop_on_401(
    mocker: MockerFixture, session: ClientSession
) -> None:
    response = mock.Mock("reason, status")
    response.reason = "Unauthorized"
    response.status = 401

    mocker.patch(
        "topgg.DBLClient.post_guild_count", side_effect=Unauthorized(response, {})
    )

    autopost = (
        DBLClient("", session=session)
        .autopost()
        .stats(lambda: StatsWrapper(guild_count=10))
    )

    with pytest.raises(Unauthorized):
        await autopost.start()
