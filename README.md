# Top.gg Python SDK

The community-maintained Python library for Top.gg.

## Installation

```sh
$ pip install topggpy
```

## Setting up

### Automatic cleanup

```py
import topgg

import os

async with topgg.Client(os.getenv('TOPGG_TOKEN')) as client:
  # ...
```

### Manual cleanup

```py
import topgg

import os

client = topgg.Client(os.getenv('TOPGG_TOKEN'))

# ...

await client.close()
```

## Usage

### Getting a bot

```py
bot = await client.get_bot(432610292342587392)
```

### Getting several bots

#### With defaults

```py
bots = await client.get_bots()

for bot in bots:
  print(bot)
```

#### With explicit arguments

```py
bots = await client.get_bots(limit=250, offset=50, sort_by=topgg.SortBy.MONTHLY_VOTES)

for bot in bots:
  print(bot)
```

### Getting your bot's voters

#### First page

```py
voters = await client.get_voters()

for voter in voters:
  print(voter)
```

#### Subsequent pages

```py
voters = await client.get_voters(2)

for voter in voters:
  print(voter)
```

### Check if a user has voted for your bot

```py
has_voted = await client.has_voted(661200758510977084)
```

### Getting your bot's server count

```py
posted_server_count = await client.get_server_count()
```

### Posting your bot's server count

```py
await client.post_server_count(bot.server_count)
```

### Automatically posting your bot's server count every few minutes

```py
@client.autopost_retrieval
def get_server_count() -> int:
  return bot.server_count

@client.autopost_success
def success(server_count: int) -> None:
  print(f'Successfully posted {server_count} servers to the API!')

@client.autopost_error
def error(error: topgg.Error) -> None:
  print(f'Error: {error!r}')

client.start_autoposter()

# ...

client.stop_autoposter() # Optional
```

### Checking if the weekend vote multiplier is active

```py
is_weekend = await client.is_weekend()
```

### Generating widget URLs

#### Large

```py
widget_url = topgg.widget.large(topgg.WidgetType.DISCORD_BOT, 574652751745777665)
```

#### Votes

```py
widget_url = topgg.widget.votes(topgg.WidgetType.DISCORD_BOT, 574652751745777665)
```

#### Owner

```py
widget_url = topgg.widget.owner(topgg.WidgetType.DISCORD_BOT, 574652751745777665)
```

#### Social

```py
widget_url = topgg.widget.social(topgg.WidgetType.DISCORD_BOT, 574652751745777665)
```

### Webhooks

#### Being notified whenever someone voted for your bot

```py
import topgg

import asyncio
import os

port = 8080
secret = os.getenv('MY_TOPGG_WEBHOOK_SECRET')

webhooks = topgg.Webhooks(secret, port)

@webhooks.on_vote('/votes')
def voted(vote: topgg.Vote) -> None:
  print(f'A user with the ID of {vote.voter_id} has voted us on Top.gg!')

async def main() -> None:
  await webhooks.start() # Starts the server
  await asyncio.Event().wait() # Keeps the server alive through indefinite blocking

if __name__ == '__main__':
  asyncio.run(main())
```