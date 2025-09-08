# Top.gg Python SDK

The community-maintained Python library for Top.gg.

## Chapters

- [Installation](#installation)
- [Setting up](#setting-up)
- [Usage](#usage)
  - [Getting a bot](#getting-a-bot)
  - [Getting several bots](#getting-several-bots)
  - [Getting your project's voters](#getting-your-projects-voters)
  - [Getting your project's vote information of a user](#getting-your-projects-vote-information-of-a-user)
  - [Getting your bot's server count](#getting-your-bots-server-count)
  - [Posting your bot's server count](#posting-your-bots-server-count)
  - [Posting your bot's application commands list](#posting-your-bots-application-commands-list)
  - [Automatically posting your bot's server count every few minutes](#automatically-posting-your-bots-server-count-every-few-minutes)
  - [Checking if the weekend vote multiplier is active](#checking-if-the-weekend-vote-multiplier-is-active)
  - [Generating widget URLs](#generating-widget-urls)
  - [Webhooks](#webhooks)
    - [Being notified whenever someone voted for your project](#being-notified-whenever-someone-voted-for-your-project)

## Installation

```sh
$ pip install topggpy
```

## Setting up

### Implicit cleanup

```py
import topgg

import os

async with topgg.Client(os.getenv('TOPGG_TOKEN')) as client:
  # ...
```

### Explicit cleanup

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

### Getting your project's voters

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

### Getting your project's vote information of a user

#### Discord ID

```py
vote = await client.get_vote(661200758510977084)

if vote:
  print(f'User has voted: {vote!r}')
```

#### Top.gg ID

```py
vote = await client.get_vote(8226924471638491136, source=topgg.UserSource.TOPGG)

if vote:
  print(f'User has voted: {vote!r}')
```

### Getting your bot's server count

```py
posted_server_count = await client.get_bot_server_count()
```

### Posting your bot's server count

```py
await client.post_bot_server_count(bot.server_count)
```

### Posting your bot's application commands list

#### Discord.py/Pycord/Nextcord/Disnake

```py
app_id = bot.user.id
commands = await bot.http.get_global_commands(app_id)

await client.post_bot_commands(commands)
```

#### Hikari

```py
app_id = ...
commands = await bot.rest.request('GET', f'/applications/{app_id}/commands')

await client.post_bot_commands(commands)
```

#### Discord.http

```py
http = discordhttp.HTTP(f'BOT {os.getenv("BOT_TOKEN")}')
app_id = ...
commands = await http.get(f'/applications/{app_id}/commands')

await client.post_bot_commands(commands)
```

### Automatically posting your bot's server count every few minutes

```py
@client.bot_autopost_retrieval
def get_server_count() -> int:
  return bot.server_count

@client.bot_autopost_success
def success(server_count: int) -> None:
  print(f'Successfully posted {server_count} servers to Top.gg!')

@client.bot_autopost_error
def error(error: topgg.Error) -> None:
  print(f'Error: {error!r}')

client.start_bot_autoposter()

# ...

client.stop_bot_autoposter() # Optional
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

#### Being notified whenever someone voted for your project

```py
import topgg

import asyncio
import os

webhooks = topgg.Webhooks(os.getenv('MY_TOPGG_WEBHOOK_SECRET'), 8080)

@webhooks.on_vote('/votes')
def voted(vote: topgg.VoteEvent) -> None:
  print(f'A user with the ID of {vote.voter_id} has voted us on Top.gg!')

async def main() -> None:
  await webhooks.start() # Starts the server
  await asyncio.Event().wait() # Keeps the server alive through indefinite blocking

if __name__ == '__main__':
  asyncio.run(main())
```