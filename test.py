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

        if isinstance(data, list) and data:
            stdout.write('[0] -> ')

            for i, each in enumerate(data):
                if i > 0:
                    stdout.write(
                        f'{" " * indent_level}{obj.__class__.__name__}.{name}[{i}] -> '
                    )

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
    async with topgg.DBLClient(os.getenv('TOPGG_TOKEN')) as tg:
        bot = await tg.get_bot_info(432610292342587392)

        test_attributes(bot)

        await asyncio.sleep(1)
        bots = await tg.get_bots(limit=250, offset=50, sort=topgg.SortBy.MONTHLY_VOTES)

        for b in bots:
            test_attributes(b)

        await asyncio.sleep(1)
        await tg.post_guild_count(topgg.StatsWrapper(2))

        await asyncio.sleep(1)
        posted_stats = await tg.get_guild_count()

        assert posted_stats.server_count == 2
        test_attributes(posted_stats)

        await asyncio.sleep(1)
        voters = await tg.get_bot_votes()

        for voter in voters:
            test_attributes(voter)

        await asyncio.sleep(1)
        is_weekend = await tg.get_weekend_status()

        assert isinstance(is_weekend, bool)

        await asyncio.sleep(1)
        has_voted = await tg.get_user_vote(661200758510977084)

        assert isinstance(has_voted, bool)


if __name__ == '__main__':
    asyncio.run(run())
