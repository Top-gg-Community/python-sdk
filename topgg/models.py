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
from enum import Enum


T = TypeVar('T')


def truthy_only(value: Optional[T]) -> Optional[T]:
  if value:
    return value


def timestamp_from_id(id: int) -> datetime:
  return datetime.fromtimestamp(((id >> 22) + 1420070400000) // 1000, tz=timezone.utc)


class Voter:
  """A Top.gg voter."""

  __slots__: tuple[str, ...] = ('id', 'username', 'avatar')

  id: int
  """This voter's Discord ID."""

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

  @property
  def created_at(self) -> datetime:
    """This voter's creation date."""

    return timestamp_from_id(self.id)


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
    'url',
    'invite',
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
  """This bot's long description. This can contain HTML and/or Markdown."""

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

  url: str
  """This bot's Top.gg page URL."""

  invite: Optional[str]
  """This bot's invite URL."""

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
    self.url = f'https://top.gg/bot/{json.get("vanity") or self.topgg_id}'
    self.invite = truthy_only(json.get('invite'))
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

  @property
  def created_at(self) -> datetime:
    """This bot's creation date."""

    return timestamp_from_id(self.id)


class SortBy(Enum):
  """Supported sorting criterias in :meth:`.Client.get_bots`."""

  __slots__: tuple[str, ...] = ()

  ID = 'id'
  """Sorts results based on each bot's ID."""

  SUBMISSION_DATE = 'date'
  """Sorts results based on each bot's submission date."""

  MONTHLY_VOTES = 'monthlyPoints'
  """Sorts results based on each bot's monthly vote count."""
