import mock
import pytest

import topgg


MOCK_TOKEN = ".eyJfdCI6IiIsImlkIjoiMzY0ODA2MDI5ODc2NTU1Nzc2In0=."


@pytest.mark.asyncio
async def test_DBLClient_post_guild_count_with_no_args():
    client = topgg.DBLClient(MOCK_TOKEN)
    with pytest.raises(TypeError, match="stats or guild_count must be provided."):
        await client.post_guild_count()


@pytest.mark.asyncio
async def test_DBLClient_get_weekend_status(monkeypatch):
    client = topgg.DBLClient(MOCK_TOKEN)
    monkeypatch.setattr("topgg.DBLClient._DBLClient__request", mock.AsyncMock())
    await client.get_weekend_status()
    client._DBLClient__request.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_post_guild_count(monkeypatch):
    client = topgg.DBLClient(MOCK_TOKEN)
    monkeypatch.setattr("topgg.DBLClient._DBLClient__request", mock.AsyncMock())
    await client.post_guild_count(guild_count=123)
    client._DBLClient__request.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_guild_count(monkeypatch):
    client = topgg.DBLClient(MOCK_TOKEN)
    monkeypatch.setattr("topgg.DBLClient._DBLClient__request", mock.AsyncMock(return_value={}))
    await client.get_guild_count()
    client._DBLClient__request.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_bot_votes(monkeypatch):
    client = topgg.DBLClient(MOCK_TOKEN)
    monkeypatch.setattr("topgg.DBLClient._DBLClient__request", mock.AsyncMock(return_value=[]))
    await client.get_bot_votes()
    client._DBLClient__request.assert_called_once()


@pytest.mark.asyncio
async def test_DBLClient_get_user_vote(monkeypatch):
    client = topgg.DBLClient(MOCK_TOKEN)
    monkeypatch.setattr("topgg.DBLClient._DBLClient__request", mock.AsyncMock(return_value={"voted": 1}))
    await client.get_user_vote(1234)
    client._DBLClient__request.assert_called_once()
