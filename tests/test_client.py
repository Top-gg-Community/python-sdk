import asyncio
from typing import Optional

import mock
import pytest
from aiohttp import ClientSession
from discord import Client
from discord.ext.commands import Bot
from pytest import CaptureFixture
from pytest_mock import MockerFixture

from topgg import DBLClient
from topgg.errors import ClientException, Unauthorized, UnauthorizedDetected


@pytest.fixture
def bot() -> Client:
    bot = mock.Mock(Client)
    bot.loop = asyncio.get_event_loop()
    bot.guilds = []
    bot.is_closed.return_value = False
    return bot


@pytest.fixture
def session() -> ClientSession:
    return mock.Mock(ClientSession)


@pytest.fixture
def exc() -> Exception:
    return Exception("Test Exception")


@pytest.mark.parametrize(
    "autopost, post_shard_count, autopost_interval",
    [
        (True, True, 900),
        (True, False, 900),
        (True, True, None),
        (True, False, None),
        (False, False, None),
        (False, False, 0),
    ],
)
@pytest.mark.asyncio
async def test_DBLClient_validates_constructor_and_passes_for_valid_values(
    bot: Client,
    mocker: MockerFixture,
    autopost: bool,
    post_shard_count: bool,
    autopost_interval: Optional[int],
    session: ClientSession,
) -> None:
    mocker.patch("topgg.DBLClient._auto_post", new_callable=mock.AsyncMock)  # type: ignore
    DBLClient(
        bot,
        "",
        session=session,
        autopost=autopost,
        post_shard_count=post_shard_count,
        autopost_interval=autopost_interval,
    )


@pytest.mark.parametrize(
    "autopost, post_shard_count, autopost_interval",
    [
        (True, True, 0),
        (True, False, 500),
        (False, True, 0),
        (False, True, 900),
        (False, True, None),
        (False, False, 1800),
    ],
)
def test_DBLClient_validates_constructor_and_fails_for_invalid_values(
    bot: Client,
    mocker: MockerFixture,
    autopost: bool,
    post_shard_count: bool,
    autopost_interval: Optional[int],
    session: ClientSession,
) -> None:
    with pytest.raises(ClientException):
        DBLClient(
            bot,
            "",
            session=session,
            autopost=autopost,
            post_shard_count=post_shard_count,
            autopost_interval=autopost_interval,
        )


@pytest.mark.asyncio
async def test_DBLClient_breaks_autopost_loop_on_401(
    bot: Client, mocker: MockerFixture, session: ClientSession
) -> None:
    response = mock.Mock("reason, status")
    response.reason = "Unauthorized"
    response.status = 401

    mocker.patch(
        "topgg.DBLClient.post_guild_count", side_effect=Unauthorized(response, {})
    )
    mocker.patch(
        "topgg.DBLClient._ensure_bot_user",
        new_callable=mock.AsyncMock,  # type: ignore
    )

    obj = DBLClient(bot, "", False, session=session)

    with pytest.raises(Unauthorized):
        await obj._auto_post()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token",
    [None, ""],
    # treat None as str to suppress mypy
)
async def test_HTTPClient_fails_for_no_token(
    bot: Client, token: str, session: ClientSession
) -> None:
    with pytest.raises(UnauthorizedDetected):
        await DBLClient(bot=bot, token=token, session=session).post_guild_count()


@pytest.mark.asyncio
async def test_Client_with_default_autopost_error_handler(
    mocker: MockerFixture,
    capsys: CaptureFixture[str],
    session: ClientSession,
    exc: Exception,
) -> None:
    client = Client()
    mocker.patch("topgg.DBLClient._auto_post", new_callable=mock.AsyncMock)  # type: ignore
    dbl = DBLClient(client, "", True, session=session)
    assert client.on_autopost_error == dbl.on_autopost_error
    await client.on_autopost_error(exc)
    assert "Ignoring exception in auto post loop" in capsys.readouterr().err


@pytest.mark.asyncio
async def test_Client_with_custom_autopost_error_handler(
    mocker: MockerFixture, session: ClientSession, exc: Exception
) -> None:
    client = Client()
    state = False

    @client.event
    async def on_autopost_error(exc: Exception) -> None:
        nonlocal state
        state = True

    mocker.patch("topgg.DBLClient._auto_post", new_callable=mock.AsyncMock)  # type: ignore
    DBLClient(client, "", True, session=session)
    await client.on_autopost_error(exc)
    assert state


@pytest.mark.asyncio
async def test_Bot_with_autopost_error_listener(
    mocker: MockerFixture,
    capsys: CaptureFixture[str],
    session: ClientSession,
    exc: Exception,
) -> None:
    bot = Bot("")
    state = False

    @bot.listen()
    async def on_autopost_error(exc: Exception) -> None:
        nonlocal state
        state = True

    mocker.patch("topgg.DBLClient._auto_post", new_callable=mock.AsyncMock)  # type: ignore
    DBLClient(bot, "", True, session=session)

    # await to make sure all the listeners were run before asserting
    # as <Bot>.dispatch schedules the events and will continue
    # to the assert line without finishing the event callbacks
    await bot.on_autopost_error(exc)
    await on_autopost_error(exc)

    assert "Ignoring exception in auto post loop" not in capsys.readouterr().err
    assert state
