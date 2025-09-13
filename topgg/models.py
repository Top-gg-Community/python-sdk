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

from datetime import datetime, timezone
from typing import Optional, TypeVar
from urllib import parse
from enum import Enum


T = TypeVar('T')


def truthy_only(value: Optional[T]) -> Optional[T]:
  if value:
    return value


class Vote:
  """A Top.gg vote."""

  __slots__ = ('receiver_id', 'voter_id', 'voted_at', 'expires_at', 'weight')

  receiver_id: int
  """The ID of the project that received a vote."""

  voter_id: int
  """The ID of the Top.gg user who voted."""

  weight: int
  """This vote's weight. 1 during weekdays, 2 during weekends.."""

  voted_at: datetime
  """When the vote was cast."""

  expires_at: datetime
  """When the vote expires and the user is required to vote again."""

  def __init__(self, json: dict, receiver_id: int, voter_id: int):
    self.receiver_id = receiver_id
    self.voter_id = voter_id
    self.weight = json['weight']
    self.voted_at = datetime.fromisoformat(json['created_at'])
    self.expires_at = datetime.fromisoformat(json['expires_at'])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} receiver_id={self.receiver_id} voter_id={self.voter_id} weight={self.weight} voted_at={self.voted_at!r} expires_at={self.expires_at!r}>'

  def __bool__(self) -> bool:
    return self.expired

  @property
  def expired(self) -> bool:
    """Whether this vote is now expired."""

    return datetime.now(tz=timezone.utc) >= self.expires_at


class VoteEvent:
  """A dispatched Top.gg vote event."""

  __slots__ = ('receiver_id', 'voter_id', 'is_test', 'is_weekend', 'query')

  receiver_id: int
  """The ID of the project that received a vote."""

  voter_id: int
  """The ID of the Top.gg user who voted."""

  is_test: bool
  """Whether this vote is just a test done from the page settings."""

  is_weekend: bool
  """Whether the weekend multiplier is active, where a single vote counts as two."""

  query: dict[str, str]
  """Query strings found on the vote page."""

  def __init__(self, json: dict):
    guild = json.get('guild')

    self.receiver_id = int(json.get('bot', guild))
    self.voter_id = int(json['user'])
    self.is_test = json['type'] == 'test'
    self.is_weekend = bool(json.get('isWeekend'))

    if query := json.get('query'):
      self.query = {
        k: v[0] for k, v in parse.parse_qs(parse.urlsplit(query).query).items()
      }
    else:
      self.query = {}

  def __repr__(self) -> str:
    return (
      f'<{__class__.__name__} receiver_id={self.receiver_id} voter_id={self.voter_id}>'
    )


class Voter:
  """A Top.gg voter."""

  __slots__: tuple[str, ...] = ('id', 'username', 'avatar')

  id: int
  """This voter's ID."""

  username: str
  """This voter's username."""

  avatar: str
  """This voter's avatar URL."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.username = json['username']
    self.avatar = json['avatar']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} username={self.username!r}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: 'Voter') -> bool:
    if isinstance(other, __class__):
      return self.id == other.id

    return NotImplemented


class Bot:
  """A Discord bot listed on Top.gg."""

  __slots__: tuple[str, ...] = (
    'id',
    'topgg_id',
    'username',
    'prefix',
    'short_description',
    'long_description',
    'tags',
    'website',
    'github',
    'owners',
    'submitted_at',
    'votes',
    'monthly_votes',
    'support',
    'avatar',
    'invite',
    'vanity',
    'server_count',
    'review_score',
    'review_count',
  )

  id: int
  """This bot's Discord ID."""

  topgg_id: int
  """This bot's Top.gg ID."""

  username: str
  """This bot's username."""

  prefix: str
  """This bot's prefix."""

  short_description: str
  """This bot's short description."""

  long_description: Optional[str]
  """This bot's HTML/Markdown long description."""

  tags: list[str]
  """This bot's tags."""

  website: Optional[str]
  """This bot's website URL."""

  github: Optional[str]
  """This bot's GitHub repository URL."""

  owners: list[int]
  """This bot's owner IDs."""

  submitted_at: datetime
  """This bot's submission date."""

  votes: int
  """The amount of votes this bot has."""

  monthly_votes: int
  """The amount of votes this bot has this month."""

  support: Optional[str]
  """This bot's support URL."""

  avatar: str
  """This bot's avatar URL."""

  invite: Optional[str]
  """This bot's invite URL."""

  vanity: Optional[str]
  """This bot's Top.gg vanity code."""

  server_count: Optional[str]
  """This bot's posted server count."""

  review_score: float
  """This bot's average review score out of 5."""

  review_count: int
  """This bot's review count."""

  def __init__(self, json: dict):
    self.id = int(json['clientid'])
    self.topgg_id = int(json['id'])
    self.username = json['username']
    self.prefix = json['prefix']
    self.short_description = json['shortdesc']
    self.long_description = truthy_only(json.get('longdesc'))
    self.tags = json['tags']
    self.website = truthy_only(json.get('website'))
    self.github = truthy_only(json.get('github'))
    self.owners = [int(id) for id in json['owners']]
    self.submitted_at = datetime.fromisoformat(json['date'].replace('Z', '+00:00'))
    self.votes = json['points']
    self.monthly_votes = json['monthlyPoints']
    self.support = truthy_only(json.get('support'))
    self.avatar = json['avatar']
    self.invite = truthy_only(json.get('invite'))
    self.vanity = truthy_only(json.get('vanity'))
    self.server_count = json.get('server_count')
    self.review_score = json['reviews']['averageScore']
    self.review_count = json['reviews']['count']

  def __repr__(self) -> str:
    return f'<{__class__.__name__} id={self.id} username={self.username!r} votes={self.votes} monthly_votes={self.monthly_votes} server_count={self.server_count}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: 'Bot') -> bool:
    if isinstance(other, __class__):
      return self.id == other.id

    return NotImplemented


class SortBy(Enum):
  """Supported sorting criterias in :meth:`.Client.get_bots`."""

  __slots__: tuple[str, ...] = ()

  ID = 'id'
  """Sorts results based on each bot's ID."""

  SUBMISSION_DATE = 'date'
  """Sorts results based on each bot's submission date."""

  MONTHLY_VOTES = 'monthlyPoints'
  """Sorts results based on each bot's monthly vote count."""


class UserSource(Enum):
  """A user account from an external platform that is linked to a Top.gg user account."""

  DISCORD = 'discord'
  TOPGG = 'topgg'
