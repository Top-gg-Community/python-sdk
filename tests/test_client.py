import typing as t

import mock
import pytest
from aiohttp import ClientSession

import topgg
from topgg import errors


@pytest.fixture
def session() -> ClientSession:
    return mock.Mock(ClientSession)


@pytest.fixture
def client() -> topgg.DBLClient:
    client = topgg.DBLClient(token="TOKEN", default_bot_id=1234)
    client.http = mock.Mock(topgg.http.HTTPClient)
    return client


@pytest.mark.asyncio
async def test_HTTPClient_with_external_session(session: ClientSession):
    http = topgg.http.HTTPClient("TOKEN", session=session)
    assert not http._own_session
    await http.close()
    session.close.assert_not_called()


@pytest.mark.asyncio
async def test_HTTPClient_with_no_external_session(session: ClientSession):
    http = topgg.http.HTTPClient("TOKEN")
    http.session = session
    assert http._own_session
    await http.close()
    session.close.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_bot_votes_with_no_default_bot_id():
    client = topgg.DBLClient("TOKEN")
    with pytest.raises(
        errors.ClientException,
        match="you must set default_bot_id when constructing the client.",
    ):
        await client.get_bot_votes()


@pytest.mark.asyncio
async def test_DBLClient_post_guild_count_with_no_args():
    client = topgg.DBLClient("TOKEN", default_bot_id=1234)
    with pytest.raises(TypeError, match="stats or guild_count must be provided."):
        await client.post_guild_count()


@pytest.mark.parametrize(
    "method, kwargs",
    [
        (topgg.DBLClient.get_guild_count, {}),
        (topgg.DBLClient.get_bot_info, {}),
        (
            topgg.DBLClient.generate_widget,
            {
                "options": topgg.types.WidgetOptions(),
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_DBLClient_get_guild_count_with_no_id(
    method: t.Callable, kwargs: t.Dict[str, t.Any]
):
    client = topgg.DBLClient("TOKEN")
    with pytest.raises(
        errors.ClientException, match="bot_id or default_bot_id is unset."
    ):
        await method(client, **kwargs)


@pytest.mark.asyncio
async def test_closed_DBLClient_raises_exception():
    client = topgg.DBLClient("TOKEN")
    assert not client.is_closed
    await client.close()
    assert client.is_closed
    with pytest.raises(errors.ClientException, match="client has been closed."):
        await client.get_weekend_status()


@pytest.mark.asyncio
async def test_DBLClient_get_weekend_status(client: topgg.DBLClient):
    client.http.get_weekend_status = mock.AsyncMock()
    await client.get_weekend_status()
    client.http.get_weekend_status.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_post_guild_count(client: topgg.DBLClient):
    client.http.post_guild_count = mock.AsyncMock()
    await client.post_guild_count(guild_count=123)
    client.http.post_guild_count.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_guild_count(client: topgg.DBLClient):
    client.http.get_guild_count = mock.AsyncMock(return_value={})
    await client.get_guild_count()
    client.http.get_guild_count.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_bot_votes(client: topgg.DBLClient):
    client.http.get_bot_votes = mock.AsyncMock(return_value=[])
    await client.get_bot_votes()
    client.http.get_bot_votes.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_bots(client: topgg.DBLClient):
    client.http.get_bots = mock.AsyncMock(return_value={"results": []})
    await client.get_bots()
    client.http.get_bots.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_user_info(client: topgg.DBLClient):
    client.http.get_user_info = mock.AsyncMock(return_value={})
    await client.get_user_info(1234)
    client.http.get_user_info.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_user_vote(client: topgg.DBLClient):
    client.http.get_user_vote = mock.AsyncMock(return_value={"voted": 1})
    await client.get_user_vote(1234)
    client.http.get_user_vote.assert_called_once()
