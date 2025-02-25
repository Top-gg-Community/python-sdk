ORIGINAL_INTERVAL_INSTRUCTION = 'interval = max(interval or 900.0, 900.0)'
MODIFIED_INTERVAL_INSTRUCTION = 'interval = interval'


def replace_client_file(former: str, latter: str) -> None:
  client_file_contents = None

  with open('./topgg/client.py', 'r') as client_file:
    client_file_contents = client_file.read().replace(former, latter)

  with open('./topgg/client.py', 'w') as client_file:
    client_file.write(client_file_contents)


replace_client_file(ORIGINAL_INTERVAL_INSTRUCTION, MODIFIED_INTERVAL_INSTRUCTION)


import topgg

import asyncio
import os


async def run() -> None:
  try:
    async with topgg.Client(os.getenv('TOPGG_TOKEN')) as tg:

      @tg.autopost_retrieval
      def get_server_count() -> int:
        return 2

      @tg.autopost_success
      def success(server_count: int) -> None:
        print(f'Successfully posted {server_count} servers to the Top.gg API!')

      @tg.autopost_error
      def error(error: topgg.Error) -> None:
        print(f'Error: {error!r}')

      tg.start_autoposter(5.0)

      await asyncio.sleep(15)
  finally:
    replace_client_file(MODIFIED_INTERVAL_INSTRUCTION, ORIGINAL_INTERVAL_INSTRUCTION)


if __name__ == '__main__':
  if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

  asyncio.run(run())
