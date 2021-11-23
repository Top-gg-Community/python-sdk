import mock
import pytest
from aiohttp import ClientSession

import topgg


@pytest.fixture
def session() -> ClientSession:
    return mock.Mock(ClientSession)


@pytest.mark.asyncio
async def test_HTTPClient_with_external_session(session: ClientSession):
    http = topgg.http.HTTPClient("TOKEN", session=session)
    assert not http._own_session
    await http.close()
    session.close.assert_not_called()


@pytest.mark.asyncio
async def test_HTTPClient_with_external_session(session: ClientSession):
    http = topgg.http.HTTPClient("TOKEN")
    http.session = session
    assert http._own_session
    await http.close()
    session.close.assert_called_once()
