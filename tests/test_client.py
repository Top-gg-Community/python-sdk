from multidict import CIMultiDict
from datetime import datetime
from os import path
import sys

sys.path.insert(0, path.join(path.dirname(path.realpath(__file__)), '..'))


from typing import TYPE_CHECKING
from collections import deque
from time import time
import pytest_asyncio
import pytest

if TYPE_CHECKING:
  from typing import AsyncGenerator


import topgg

from util import _test_attributes, RequestMock


MOCK_TOKEN = '.eyJfdCI6IiIsImlkIjoiMzY0ODA2MDI5ODc2NTU1Nzc2In0=.'
MOCK_LOCALE_MAPPING = {topgg.Locale.ENGLISH: 'test', topgg.Locale.JAPANESE: 'test'}


@pytest_asyncio.fixture
async def client(
  monkeypatch: pytest.MonkeyPatch,
) -> 'AsyncGenerator[topgg.Client, None]':
  client = topgg.Client(MOCK_TOKEN)

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
    test_client = topgg.Client(MOCK_TOKEN)

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
async def test_Client_edit_self_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match=r'^The locale mapping\'s keys must be an instance of Locale\.$'
    ):
      await client.edit_self(headline={'en': 'test'})

    with pytest.raises(
      TypeError, match=r'^The locale mapping\'s keys must be an instance of Locale\.$'
    ):
      await client.edit_self(headline={'en': 'test'}, content=MOCK_LOCALE_MAPPING)

    with pytest.raises(
      TypeError, match=r'^The locale mapping\'s keys must be an instance of Locale\.$'
    ):
      await client.edit_self(content={'en': 'test'})

  with pytest.raises(ValueError, match=r'^headline or content must be specified\.$'):
    await client.edit_self()

  with RequestMock(204, 'No Content') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.edit_self(headline=MOCK_LOCALE_MAPPING, content=MOCK_LOCALE_MAPPING)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_announcement_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError,
      match=r'^The specified title and content must be a string\.$',
    ):
      await client.post_announcement(None, 2)

  with pytest.raises(
    ValueError,
    match=r'^The specified title and content length must be within the accepted ranges\.$',
  ):
    await client.post_announcement('test', 'test')

  with RequestMock(200, 'OK', response='mocks/post_announcement.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    announcement = await client.post_announcement(
      'Version 2.0 Released!',
      'We just released version 2.0 with a bunch of new features and improvements.',
    )

    _test_attributes(announcement)

    request.assert_called_once()


@pytest.mark.asyncio
async def test_Client_post_commands_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError,
      match="^The specified commands is not a list of dicts in the form of Discord API's raw JSON format.$",
    ):
      await client.post_commands(None)

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


@pytest.mark.asyncio
async def test_Client_post_metrics_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError,
      match=r'^The specified metrics has an invalid type\.$',
    ):
      await client.post_metrics('test')

    with pytest.raises(
      TypeError, match=r'^The specified player count must be an integer\.$'
    ):
      await client.post_metrics(topgg.Metrics.roblox_game(None))

  with pytest.raises(
    ValueError,
    match=r'^The specified batch of metrics must not be empty\.$',
  ):
    await client.post_metrics({})

  with pytest.raises(
    TypeError,
    match=r'^The specified server count and\/or shard count must be an integer\.$',
  ):
    await client.post_metrics(topgg.Metrics.discord_bot())

  with pytest.raises(
    TypeError,
    match=r'^The specified member count and\/or online count must be an integer\.$',
  ):
    await client.post_metrics(topgg.Metrics.discord_server())

  with RequestMock(204, 'No Content') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    await client.post_metrics(topgg.Metrics.discord_bot(server_count=1, shard_count=1))
    await client.post_metrics(topgg.Metrics.discord_bot(server_count=1))

    await client.post_metrics(
      topgg.Metrics.discord_server(member_count=1, online_count=1)
    )
    await client.post_metrics(topgg.Metrics.discord_server(member_count=1))

    metrics = topgg.Metrics.roblox_game(1)

    await client.post_metrics(metrics)
    await client.post_metrics({datetime.now(): metrics})

    assert request.call_count == 6


@pytest.mark.asyncio
async def test_Client_get_vote_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match="^The specified user's source and/or ID's type is invalid.$"
    ):
      await client.get_vote(topgg.UserSource.DISCORD, None)

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


@pytest.mark.asyncio
async def test_Client_get_votes_works(
  monkeypatch: pytest.MonkeyPatch,
  client: topgg.Client,
) -> None:
  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match=r'The specified earliest possible date\'s type is invalid.$'
    ):
      await client.get_votes(None)

  with RequestMock(200, 'OK', response='mocks/get_votes.json') as request:
    monkeypatch.setattr('aiohttp.ClientSession.request', request)

    first_page = await client.get_votes(datetime(2026, 1, 1))

    _test_attributes(first_page)

    second_page = await first_page.next()

    _test_attributes(second_page)

    assert request.call_count == 2
