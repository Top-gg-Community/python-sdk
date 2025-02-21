"""
The MIT License (MIT)

Copyright (c) 2021 Assanali Mukhanov & Top.gg
Copyright (c) 2024-2025 null8626 & Top.gg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, List, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import quote


def truthy_only(value: Optional[Any], default: Any = None) -> Optional[Any]:
  if value:
    return value

  return default


class Voter:
  __slots__: Tuple[str, ...] = ('id', 'name', 'avatar')

  id: int
  """This voter's user ID."""

  name: str
  """This voter's username."""

  avatar: str
  """This voter's avatar URL. Its format will either be PNG or GIF if animated."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['username']

    if avatar_hash := json.get('avatar'):
      ext = 'gif' if avatar_hash.startswith('a_') else 'png'
      self.avatar = (
        f'https://cdn.discordapp.com/avatars/{self.id}/{avatar_hash}.{ext}?size=1024'
      )
    else:
      self.avatar = f'https://cdn.discordapp.com/embed/avatars/{(self.id >> 2) % 6}.png'

  @property
  def created_at(self) -> datetime:
    """This voter's creation date."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )


class Bot:
  __slots__: Tuple[str, ...] = (
    'id',
    'topgg_id',
    'name',
    'prefix',
    'short_description',
    'long_description',
    'tags',
    'website',
    'github',
    'owners',
    'banner_url',
    'approved_at',
    'votes',
    'monthly_votes',
    'support',
    'avatar',
    'url',
  )

  id: int
  """This bot's application ID."""

  topgg_id: int
  """This bot's Top.gg user ID."""

  name: str
  """This bot's username."""

  prefix: str
  """This bot's prefix."""

  short_description: str
  """This bot's short description."""

  long_description: Optional[str]
  """This bot's long description. This can contain HTML and/or Markdown."""

  tags: List[str]
  """This bot's tags."""

  website: Optional[str]
  """This bot's website URL."""

  github: Optional[str]
  """This bot's GitHub repository URL."""

  owners: List[int]
  """A list of this bot's owners IDs."""

  banner_url: Optional[str]
  """This bot's banner URL."""

  approved_at: datetime
  """The date when this bot was approved on Top.gg."""

  votes: int
  """The amount of votes this bot has."""

  monthly_votes: int
  """The amount of votes this bot has this month."""

  support: Optional[str]
  """This bot's support server invite URL."""

  avatar: str
  """This bot's avatar URL. Its format will either be PNG or GIF if animated."""

  url: str
  """The URL of this bot's page."""

  def __init__(self, json: dict):
    self.id = int(json['clientid'])
    self.topgg_id = int(json['id'])
    self.name = json['username']
    self.prefix = json['prefix']
    self.short_description = json['shortdesc']
    self.long_description = truthy_only(json.get('longdesc'))
    self.tags = json.get('tags') or []
    self.website = truthy_only(json.get('website'))
    self.github = truthy_only(json.get('github'))
    self.owners = [int(id) for id in json.get('owners') or []]
    self.banner_url = truthy_only(json.get('bannerUrl'))
    self.approved_at = datetime.fromisoformat(json['date'].replace('Z', '+00:00'))
    self.votes = json['points']
    self.monthly_votes = json['monthlyPoints']

    if support := json.get('support'):
      self.support = f'https://discord.com/invite/{support}'
    else:
      self.support = None

    if avatar_hash := json.get('avatar'):
      ext = 'gif' if avatar_hash.startswith('a_') else 'png'
      self.avatar = (
        f'https://cdn.discordapp.com/avatars/{self.id}/{avatar_hash}.{ext}?size=1024'
      )
    else:
      self.avatar = f'https://cdn.discordapp.com/embed/avatars/{(self.id >> 2) % 6}.png'

    self.url = f'https://top.gg/bot/{json.get("support") or self.id}'

  @property
  def created_at(self) -> datetime:
    """This bot's creation date."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )


class BotQuery:
  __slots__: Tuple[str, ...] = ('__client', '__params', '__search', '__sort')

  def __init__(self, client: object):
    self.__client = client
    self.__params = {}
    self.__search = {}
    self.__sort = None

  def sort_by_id(self) -> 'BotQuery':
    """
    Sorts results based on each Discord bot's ID.

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__sort = 'id'

    return self

  def sort_by_approval_date(self) -> 'BotQuery':
    """
    Sorts results based on each Discord bot's approval date.

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__sort = 'date'

    return self

  def sort_by_monthly_votes(self) -> 'BotQuery':
    """
    Sorts results based on each Discord bot's monthly vote count.

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__sort = 'monthlyPoints'

    return self

  def limit(self, limit: int) -> 'BotQuery':
    """
    Sets the maximum amount of bots to be queried.

    :param id: The maximum amount of bots to be queried. This cannot be more than 500.
    :type id: :py:class:`int`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__params['limit'] = max(min(limit, 500), 1)

    return self

  def skip(self, skip: int) -> 'BotQuery':
    """
    Sets the amount of bots to be skipped during the query.

    :param id: The amount of bots to be skipped during the query. This cannot be more than 499.
    :type id: :py:class:`int`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__params['skip'] = max(min(skip, 499), 0)

    return self

  def name(self, name: str) -> 'BotQuery':
    """
    Queries only Discord bots that has this username.

    :param id: The specified username.
    :type id: :py:class:`str`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__search['username'] = name

    return self

  def prefix(self, prefix: str) -> 'BotQuery':
    """
    Queries only Discord bots that has this prefix.

    :param id: The specified prefix.
    :type id: :py:class:`str`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__search['prefix'] = prefix

    return self

  def votes(self, votes: int) -> 'BotQuery':
    """
    Queries only Discord bots that has this vote count.

    :param id: The specified vote count.
    :type id: :py:class:`int`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__search['points'] = max(votes, 0)

    return self

  def monthly_votes(self, monthly_votes: int) -> 'BotQuery':
    """
    Queries only Discord bots that has this monthly vote count.

    :param id: The specified monthly vote count.
    :type id: :py:class:`int`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__search['monthlyPoints'] = max(monthly_votes, 0)

    return self

  def vanity(self, vanity: str) -> 'BotQuery':
    """
    Queries only Discord bots that has this Top.gg vanity URL.

    :param id: The specified Top.gg vanity URL (without the preceeding https://top.gg/).
    :type id: :py:class:`str`

    :returns: The same object. This allows this object to have chained method calls.
    :rtype: :class:`~.models.BotQuery`
    """

    self.__search['vanity'] = vanity

    return self

  async def send(self) -> List[Bot]:
    """
    Sends the query to the API and returns a list of matching Discord bots.

    :exception Error: If the :class:`~aiohttp.ClientSession` used by the client is already closed.
    :exception RequestError: If the client received a non-favorable response from the API.
    :exception Ratelimited: If the client got blocked by the API for an hour because it exceeded its ratelimits.

    :returns: A list of matching discord bots.
    :rtype: List[:class:`~.models.Bot`]
    """

    params = self.__params.copy()
    params['search'] = [f'{k}%3A%20{quote(v)}' for k, v in self.__search.values()].join(
      '%20'
    )

    if self.__sort:
      params['sort'] = self.__sort

    bots = await self.__client.__request('GET', '/bots', params=params)
    output = []

    if bots:
      for b in bots.get('results', ()):
        output.append(Bot(b))

    return output
