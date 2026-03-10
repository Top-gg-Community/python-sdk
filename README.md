# Top.gg Python SDK

> For more information, see the documentation here: <https://topggpy.rtfd.io>.

The community-maintained Python SDK for Top.gg.

## Chapters

- [Installation](#installation)
- [Setting up](#setting-up)
- [Usage](#usage)
  - [Getting your project's information](#getting-your-projects-information)
  - [Getting your project's vote information of a user](#getting-your-projects-vote-information-of-a-user)
  - [Getting a cursor-based paginated list of votes for your project](#getting-a-cursor-based-paginated-list-of-votes-for-your-project)
  - [Posting your bot's application commands list](#posting-your-bots-application-commands-list)
  - [Generating widget URLs](#generating-widget-urls)
  - [Webhooks](#webhooks)

## Installation

```sh
$ pip install topggpy
```

## Setting up

```py
import topgg

import os


token = os.getenv('TOPGG_TOKEN')
assert token is not None, 'Missing TOPGG_TOKEN environment variable.'

client = topgg.Client(token)
```

## Usage

### Getting your project's information

```py
project = await client.get_self()
```

### Getting your project's vote information of a user

#### Discord ID

```py
vote = await client.get_vote(topgg.UserSource.DISCORD, 661200758510977084)
```

#### Top.gg ID

```py
vote = await client.get_vote(topgg.UserSource.TOPGG, 8226924471638491136)
```

### Getting a cursor-based paginated list of votes for your project

```py
from datetime import datetime


first_page = await client.get_votes(datetime(2026, 1, 1))

for vote in first_page:
  print(vote)

second_page = await first_page.next()

for vote in second_page:
  print(vote)

third_page = await second_page.next()
```

### Posting your bot's application commands list

#### Discord.py

```py
commands = [command.to_dict() for command in await bot.tree.fetch_commands()]

await client.post_commands(commands)
```

#### Raw

```py
# Array of application commands that
# can be serialized to Discord API's raw JSON format.
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
```

### Generating widget URLs

#### Large

```py
widget_url = topgg.Widget.large(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)
```

#### Votes

```py
widget_url = topgg.Widget.votes(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)
```

#### Owner

```py
widget_url = topgg.Widget.owner(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)
```

#### Social

```py
widget_url = topgg.Widget.social(topgg.Platform.DISCORD, topgg.ProjectType.BOT, 1026525568344264724)
```

### Webhooks

With express:

```py
import topgg

from aiohttp import web
import os


secret = os.getenv('TOPGG_WEBHOOK_SECRET')
assert secret is not None, 'Missing TOPGG_WEBHOOK_SECRET environment variable.'

# POST /webhook
webhooks = topgg.Webhooks('/webhook', secret)

@webhooks.on(topgg.PayloadType.TEST)
async def test_listener(payload: topgg.TestPayload, trace: str) -> web.Response:
  print(payload)

  return web.Response(status=204)

await webhooks.start()
```