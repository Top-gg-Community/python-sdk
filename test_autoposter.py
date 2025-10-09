ORIGINAL_INTERVAL_INSTRUCTION = 'await asyncio.sleep(self.interval)'
MODIFIED_INTERVAL_INSTRUCTION = 'await asyncio.sleep(2)'


def replace_autopost_file(former: str, latter: str) -> None:
    autopost_file_contents = None

    with open('./topgg/autopost.py', 'r') as autopost_file:
        autopost_file_contents = autopost_file.read().replace(former, latter)

    with open('./topgg/autopost.py', 'w') as autopost_file:
        autopost_file.write(autopost_file_contents)


replace_autopost_file(ORIGINAL_INTERVAL_INSTRUCTION, MODIFIED_INTERVAL_INSTRUCTION)


import topgg

import asyncio
import os


async def run() -> None:
    try:
        async with topgg.DBLClient(os.getenv('TOPGG_TOKEN')) as tg:
            autoposter = tg.autopost()

            @autoposter.stats
            def get_guild_count() -> int:
                return topgg.StatsWrapper(2)

            @autoposter.on_success
            def success() -> None:
                print('Successfully posted statistics to the Top.gg API!')

            @autoposter.on_error
            def error(exc: Exception) -> None:
                print(f'Error: {exc!r}')

            autoposter.start()

            await asyncio.sleep(15)
    finally:
        replace_autopost_file(
            MODIFIED_INTERVAL_INSTRUCTION, ORIGINAL_INTERVAL_INSTRUCTION
        )


if __name__ == '__main__':
    asyncio.run(run())
