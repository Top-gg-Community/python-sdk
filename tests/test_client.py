import asyncio

import mock
import pytest
from aiohttp import ClientSession
from discord import Client

from topgg import DBLClient
from topgg.errors import ClientException, Unauthorized, UnauthorizedDetected


@pytest.fixture
async def bot():
    bot = mock.Mock(Client)
    bot.loop = asyncio.get_event_loop()
    bot.guilds = []
    bot.is_closed.return_value = False
    return bot


@pytest.fixture
def session():
    return mock.Mock(ClientSession)


@pytest.mark.parametrize(
    "autopost, post_shard_count, autopost_interval",
    [(True, True, 900), (True, False, 900), (True, True, None), (True, False, None)],
)
@pytest.mark.asyncio
async def test_DBLClient_validates_constructor_and_passes_for_valid_values(
    bot, mocker, autopost, post_shard_count, autopost_interval, session
):
    mocker.patch("topgg.DBLClient._auto_post", return_value=None)
    DBLClient(
        bot,
        None,
        session=session,
        autopost=autopost,
        post_shard_count=post_shard_count,
        autopost_interval=autopost_interval,
    )


@pytest.mark.parametrize(
    "autopost, post_shard_count, autopost_interval",
    [(False, True, 900), (True, True, 0), (True, True, 500)],
)
def test_DBLClient_validates_constructor_and_fails_for_invalid_values(
    bot, mocker, autopost, post_shard_count, autopost_interval, session
):
    with pytest.raises(ClientException):
        DBLClient(
            bot,
            None,
            session=session,
            autopost=autopost,
            post_shard_count=post_shard_count,
            autopost_interval=autopost_interval,
        )


@pytest.mark.asyncio
async def test_DBLClient_autopost_breaks_on_401(bot, mocker, session):
    response = mock.Mock("reason, status")
    response.reason = "Unauthorized"
    response.status = 401

    mocker.patch(
        "topgg.DBLClient.post_guild_count", side_effect=Unauthorized(response, {})
    )
    mocker.patch("topgg.DBLClient._ensure_bot_user", return_value=None)

    obj = DBLClient(bot, None, False, session=session)

    with pytest.raises(Unauthorized):
        await obj._auto_post()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token",
    [None, ""],
)
async def test_HTTPClient_fails_for_no_token(bot, token, session):
    with pytest.raises(UnauthorizedDetected):
        await DBLClient(bot=bot, token=token, session=session).post_guild_count()
