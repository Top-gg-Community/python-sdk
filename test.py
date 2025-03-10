import topgg

from sys import stdout
import asyncio
import os

INDENTATION = 2


def is_local(data: object) -> bool:
  return getattr(data, '__module__', '').startswith('topgg')


def _test_attributes(obj: object, indent_level: int) -> None:
  for name in getattr(obj.__class__, '__slots__', ()):
    stdout.write(f'{" " * indent_level}{obj.__class__.__name__}.{name}')
    data = getattr(obj, name)

    if isinstance(data, list):
      stdout.write('[0] -> ')

      for i, each in enumerate(data):
        if i > 0:
          stdout.write(f'{" " * indent_level}{obj.__class__.__name__}.{name}[{i}] -> ')

        print(repr(each))
        _test_attributes(each, indent_level + INDENTATION)

      continue

    print(f' -> {data!r}')

    if is_local(data):
      _test_attributes(data, indent_level + INDENTATION)


def test_attributes(obj: object) -> None:
  print(f'{obj!r} -> ')
  _test_attributes(obj, INDENTATION)


async def run() -> None:
  async with topgg.Client(os.getenv('TOPGG_TOKEN')) as tg:
    #bot = await tg.get_bot(432610292342587392)

    #test_attributes(bot)

    #await asyncio.sleep(1)
    bots = await tg.get_bots(
      limit=250,
      offset=50,
      username='Shiro',
      sort_by=topgg.SortBy.MONTHLY_VOTES
    )

    for b in bots:
      test_attributes(b)

    await asyncio.sleep(1)
    await tg.post_server_count(2)

    await asyncio.sleep(1)
    posted_server_count = await tg.get_server_count()

    assert posted_server_count == 2

    await asyncio.sleep(1)
    voters = await tg.get_voters()

    for voter in voters:
      test_attributes(voter)

    await asyncio.sleep(1)
    has_voted = await tg.has_voted(661200758510977084)

    assert isinstance(has_voted, bool)

    await asyncio.sleep(1)
    is_weekend = await tg.is_weekend()

    assert isinstance(is_weekend, bool)


if __name__ == '__main__':
  if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

  asyncio.run(run())
