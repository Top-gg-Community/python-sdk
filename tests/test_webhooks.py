from collections.abc import AsyncGenerator, Callable
from aiohttp import test_utils, web
from typing import TYPE_CHECKING
from functools import cache
from hashlib import sha256
from os.path import join
from time import time
import pytest_asyncio
import pytest
import hmac

import topgg

from util import _test_attributes, CURRENT_DIR


MOCK_SECRET = 'testsecret1234'
MOCK_TRACE = 'trace'
WebhooksFixture = tuple[topgg.Webhooks, test_utils.TestClient]
WebhooksSignatureFixture = Callable[[str], tuple[str, str]]


@pytest_asyncio.fixture
async def webhooks() -> AsyncGenerator[WebhooksFixture, None]:
  app = test_utils.TestClient(test_utils.TestServer(web.Application()))
  webhooks = topgg.Webhooks('/webhook', MOCK_SECRET, app=app)

  for payload_type in topgg.PayloadType:

    @webhooks.on(payload_type)
    async def handler(payload: topgg.Payload, trace: str) -> web.Response:
      _test_attributes(payload)
      assert trace == MOCK_TRACE

      return web.Response(text='Test works')

  yield webhooks, app
  await webhooks.close()


@pytest.fixture
def webhook_signature() -> WebhooksSignatureFixture:
  t = str(int(time()))

  def generate_webhook_signature(body: str) -> tuple[str, str]:
    return t, hmac.new(
      MOCK_SECRET.encode('utf-8'),
      f'{t}.{body}'.encode('utf-8'),
      sha256,
    ).hexdigest()

  return generate_webhook_signature


@pytest.mark.asyncio
async def test_Webhooks_error_handling_works(
  webhooks: WebhooksFixture,
  webhook_signature: WebhooksSignatureFixture,
) -> None:
  wh, client = webhooks

  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError,
      match='^The specified secret, route, and/or host must be a valid string.$',
    ):
      topgg.Webhooks(None, None)

    with pytest.raises(TypeError, match='^The specified port must be an integer.$'):
      topgg.Webhooks('foo', MOCK_SECRET, port='')

    with pytest.raises(TypeError, match='^The specified timeout must be a float.$'):
      topgg.Webhooks('foo', MOCK_SECRET, timeout=1)

  with pytest.raises(
    ValueError, match=r'^The specified secret, route, and/or host must not be empty.$'
  ):
    topgg.Webhooks('', '')

  _test_attributes(wh)

  if not TYPE_CHECKING:
    with pytest.raises(
      TypeError, match=r'^The specified secret must be a valid string.$'
    ):
      wh.secret = 5

    with pytest.raises(TypeError, match="^The specified payload's type is invalid.$"):
      wh.on(None)

    with pytest.raises(
      TypeError, match='^The specified webhook listener must be a coroutine function.$'
    ):

      @wh.on(topgg.PayloadType.TEST)
      def test():
        pass

  with pytest.raises(ValueError, match=r'^The specified secret must not be empty.$'):
    wh.secret = ''

  await wh.start()

  with open(
    join(CURRENT_DIR, 'mocks/test_payload.json'), 'r', encoding='utf-8'
  ) as payload_file:
    payload = payload_file.read()

    response = await client.post(
      '/webhook',
      data=payload,
      headers={
        'Content-Type': 'application/json',
        'x-topgg-signature': '',
        'x-topgg-trace': MOCK_TRACE,
      },
    )

    assert response.status == 401
    assert (await response.json()).get('error') == 'Missing required headers'

    t, signature = webhook_signature(payload)

    response = await client.post(
      '/webhook',
      data=payload,
      headers={
        'Content-Type': 'application/json',
        'x-topgg-signature': f't={t},{topgg.API_VERSION}={signature}f',
        'x-topgg-trace': MOCK_TRACE,
      },
    )

    assert response.status == 403
    assert (await response.json()).get('error') == 'Invalid signature'

    response = await client.post(
      '/webhook',
      data='',
      headers={'Content-Length': '2', 'Content-Type': 'application/json'},
    )

    assert response.status == 408
    assert (await response.json()).get('error') == 'Request timed out'


@cache
async def start_webhooks(webhooks: topgg.Webhooks):
  await webhooks.start()


@pytest.mark.parametrize('payload_type', iter(topgg.PayloadType))
@pytest.mark.asyncio
async def test_Webhooks_payloads_work(
  webhooks: WebhooksFixture,
  webhook_signature: WebhooksSignatureFixture,
  payload_type: topgg.PayloadType,
) -> None:
  wh, client = webhooks

  await start_webhooks(wh)

  with open(
    join(CURRENT_DIR, f'mocks/{payload_type.name.lower()}_payload.json'),
    'r',
    encoding='utf-8',
  ) as payload_file:
    payload = payload_file.read()
    t, signature = webhook_signature(payload)

    response = await client.post(
      '/webhook',
      data=payload,
      headers={
        'Content-Type': 'application/json',
        'x-topgg-signature': f't={t},{topgg.API_VERSION}={signature}',
        'x-topgg-trace': MOCK_TRACE,
      },
    )

    assert (await response.text()) == 'Test works'
