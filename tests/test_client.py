from multidict import CIMultiDict
from datetime import datetime
from os import getenv, path
import sys

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from typing import AsyncGenerator, TYPE_CHECKING
from collections import deque
from time import time
import pytest_asyncio
import pytest

import topgg

from util import _test_attributes, RequestMock


@pytest_asyncio.fixture
async def client(
  monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[topgg.Client, None]:
  token = getenv('TOPGG_TOKEN')

  if TYPE_CHECKING:
    assert token is not None, 'Missing Top.gg API token'

  client = topgg.Client(token)

  monkeypatch.setattr(topgg.Ratelimiter, '_calls', deque([time()]))

  yield client
  await client.close()


def test_Client_attributes_work(client: topgg.Client) -> None:
  _test_attributes(client)


@pytest.mark.asyncio
async def test_Client_basic_error_handling_works() -> None:
  if not TYPE_CHECKING:
    with pytest.raises(TypeError, match='^An API token is required to use this API.$'):
      async with topgg.Client(None):
        pass

  with pytest.raises(ValueError, match='^An API token is required to use this API.$'):
    async with topgg.Client(''):
      pass

  with pytest.raises(topgg.Error, match='^Client session is already closed.$'):
    token = getenv('TOPGG_TOKEN')

    if TYPE_CHECKING:
      assert token is not None, 'Missing Top.gg API token'

    test_client = topgg.Client(token)

    await test_client.close()
    await test_client.get_self()


@pytest.mark.asyncio
async def test_Client_request_error_handling_works(
  monkeypatch: pytest.MonkeyPatch, client: topgg.Client
) -> None:
  with RequestMock(404, 'Not Found', response='mocks/404.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(topgg.RequestError, match='^Got 404: ') as raises:
      await client.get_self()

    _test_attributes(raises.value)

    request.assert_called_once()

  with RequestMock(
    429, 'Ratelimited', response={}, headers=CIMultiDict({'Retry-After': '6000'})
  ) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    for _ in range(2):
      with pytest.raises(
        topgg.Ratelimited,
        match='^The client is blocked by the API. Please try again in ',
      ) as raises:
        await client.get_self()

      _test_attributes(raises.value)
      assert 0 <= (6000.0 - raises.value.retry_after) < 0.01

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_get_self_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_self.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    project = await client.get_self()

    _test_attributes(project)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_commands_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(204, 'No Content') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.post_commands(
      [
        {
          'id': '1',
          'type': 1,
          'application_id': '1',
          'name': 'test',
          'description': 'command description',
          'default_member_permissions': '',
          'version': '1',
        }
      ]
    )

    request.assert_called_once()

  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError,
      match="^The specified commands is not a list of dicts in the form of Discord API's raw JSON format.$",
    ):
      await client.post_commands(None)


@pytest.mark.asyncio
async def test_Client_get_vote_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_vote.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    vote = await client.get_vote(topgg.UserSource.DISCORD, 661200758510977084)

    _test_attributes(vote)

    vote = await client.get_vote(topgg.UserSource.TOPGG, 8226924471638491136)

    _test_attributes(vote)

    assert request.call_count == 2

  with RequestMock(404, 'Not Found', response='mocks/404.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    vote = await client.get_vote(topgg.UserSource.DISCORD, 661200758510977084)

    assert vote is None

    request.assert_called_once()

  with RequestMock(400, 'Bad Request', response={}) as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    with pytest.raises(topgg.RequestError, match='^Got 400: ') as raises:
      await client.get_vote(topgg.UserSource.DISCORD, 661200758510977084)

    _test_attributes(raises.value)
    request.assert_called_once()

  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match="^The specified user's source and/or ID's type is invalid.$"
    ):
      await client.get_vote(topgg.UserSource.DISCORD, None)


@pytest.mark.asyncio
async def test_Client_get_votes_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  with RequestMock(200, 'OK', response='mocks/get_votes.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    first_page = await client.get_votes(datetime(2026, 1, 1))

    _test_attributes(first_page)

    second_page = await first_page.next()

    _test_attributes(second_page)

    assert request.call_count == 2

  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match=r'The specified earliest possible date\'s type is invalid.$'
    ):
      await client.get_votes(None)
