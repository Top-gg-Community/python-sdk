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

import dataclasses
import typing as t
import warnings

from datetime import datetime
from enum import Enum


T = t.TypeVar('T')


def truthy_only(value: t.Optional[T]) -> t.Optional[T]:
    if value:
        return value


class WidgetProjectType(Enum):
    """A Top.gg widget's project type."""

    __slots__: tuple[str, ...] = ()

    DISCORD_BOT = 'discord/bot'
    DISCORD_SERVER = 'discord/server'


class WidgetType(Enum):
    """A Top.gg widget's type."""

    __slots__: tuple[str, ...] = ()

    LARGE = 'large'
    VOTES = 'votes'
    OWNER = 'owner'
    SOCIAL = 'social'


class WidgetOptions:
    """Top.gg widget creation options."""

    __slots__: tuple[str, ...] = ('id', 'project_type', 'type')

    id: int
    """This widget's project ID."""

    project_type: WidgetProjectType
    """This widget's project type."""

    type: WidgetType
    """This widget's type."""

    def __init__(
        self,
        id: int,
        project_type: WidgetProjectType,
        type: WidgetType,
        *args,
        **kwargs,
    ):
        self.id = id
        self.project_type = project_type
        self.type = type

        for arg in args:
            warnings.warn(f'Ignored extra argument: {arg!r}', DeprecationWarning)

        for key in kwargs.keys():
            warnings.warn(f'Ignored keyword argument: {key}', DeprecationWarning)

    def __repr__(self) -> str:
        return f'<{__class__.__name__} id={self.id} project_type={self.project_type!r} type={self.type!r}>'


class BotData:
    """A Discord bot listed on Top.gg."""

    __slots__: tuple[str, ...] = (
        'id',
        'topgg_id',
        'username',
        'discriminator',
        'avatar',
        'def_avatar',
        'prefix',
        'shortdesc',
        'longdesc',
        'tags',
        'website',
        'support',
        'github',
        'owners',
        'guilds',
        'invite',
        'date',
        'certified_bot',
        'vanity',
        'points',
        'monthly_points',
        'donatebotguildid',
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

    discriminator: str
    """This bot's discriminator."""

    avatar: str
    """This bot's avatar URL."""

    def_avatar: str
    """This bot's default avatar hash."""

    prefix: str
    """This bot's prefix."""

    shortdesc: str
    """This bot's short description."""

    longdesc: t.Optional[str]
    """This bot's HTML/Markdown long description."""

    tags: list[str]
    """This bot's tags."""

    website: t.Optional[str]
    """This bot's website URL."""

    support: t.Optional[str]
    """This bot's support URL."""

    github: t.Optional[str]
    """This bot's GitHub repository URL."""

    owners: list[int]
    """This bot's owner IDs."""

    guilds: list[int]
    """This bot's list of servers."""

    invite: t.Optional[str]
    """This bot's invite URL."""

    date: datetime
    """This bot's submission date."""

    certified_bot: bool
    """Whether this bot is certified."""

    vanity: t.Optional[str]
    """This bot's Top.gg vanity code."""

    points: int
    """The amount of votes this bot has."""

    monthly_points: int
    """The amount of votes this bot has this month."""

    donatebotguildid: int
    """This bot's donatebot setup server ID."""

    server_count: t.Optional[str]
    """This bot's posted server count."""

    review_score: float
    """This bot's average review score out of 5."""

    review_count: int
    """This bot's review count."""

    def __init__(self, json: dict):
        self.id = int(json['clientid'])
        self.topgg_id = int(json['id'])
        self.username = json['username']
        self.discriminator = '0'
        self.avatar = json['avatar']
        self.def_avatar = ''
        self.prefix = json['prefix']
        self.shortdesc = json['shortdesc']
        self.longdesc = truthy_only(json.get('longdesc'))
        self.tags = json['tags']
        self.website = truthy_only(json.get('website'))
        self.support = truthy_only(json.get('support'))
        self.github = truthy_only(json.get('github'))
        self.owners = [int(id) for id in json['owners']]
        self.guilds = []
        self.invite = truthy_only(json.get('invite'))
        self.date = datetime.fromisoformat(json['date'].replace('Z', '+00:00'))
        self.certified_bot = False
        self.vanity = truthy_only(json.get('vanity'))
        self.points = json['points']
        self.monthly_points = json['monthlyPoints']
        self.donatebotguildid = 0
        self.server_count = json.get('server_count')
        self.review_score = json['reviews']['averageScore']
        self.review_count = json['reviews']['count']

    def __repr__(self) -> str:
        return f'<{__class__.__name__} id={self.id} username={self.username!r} points={self.points} monthly_points={self.monthly_points} server_count={self.server_count}>'

    def __int__(self) -> int:
        return self.id

    def __eq__(self, other: 'BotData') -> bool:
        if isinstance(other, __class__):
            return self.id == other.id

        return NotImplemented


class BotsData:
    """A list of Discord bot's listed on Top.gg."""

    __slots__: tuple[str, ...] = ('results', 'limit', 'offset', 'count', 'total')

    results: list[BotData]
    """The list of bots returned."""

    limit: int
    """The maximum amount of bots returned."""

    offset: int
    """The amount of bots skipped."""

    count: int
    """The amount of bots returned. Akin to len(results)."""

    total: int
    """The amount of bots that matches the specified query. May be equal or greater than count or len(results)."""

    def __init__(self, json: dict):
        self.results = [BotData(bot) for bot in json['results']]
        self.limit = json['limit']
        self.offset = json['offset']
        self.count = json['count']
        self.total = json['total']

    def __repr__(self) -> str:
        return f'<{__class__.__name__} results={self.results!r} count={self.count} total={self.total}>'

    def __iter__(self) -> t.Iterable[BotData]:
        return iter(self.results)

    def __len__(self) -> int:
        return self.count


class BotStatsData:
    """A Discord bot's statistics."""

    __slots__: tuple[str, ...] = ('server_count', 'shards', 'shard_count')

    server_count: t.Optional[int]
    """The amount of servers the bot is in."""

    shards: list[int]
    """The amount of servers the bot is in per shard."""

    shard_count: t.Optional[int]
    """The amount of shards the bot has."""

    def __init__(self, json: dict):
        self.server_count = json.get('server_count')
        self.shards = []
        self.shard_count = None

    def __repr__(self) -> str:
        return f'<{__class__.__name__} server_count={self.server_count}>'

    def __int__(self) -> int:
        return self.server_count

    def __eq__(self, other: 'BotStatsData') -> bool:
        if isinstance(other, __class__):
            return self.server_count == other.server_count

        return NotImplemented


class BriefUserData:
    """A Top.gg user's brief information."""

    __slots__: tuple[str, ...] = ('id', 'username', 'avatar')

    id: int
    """This user's ID."""

    username: str
    """This user's username."""

    avatar: str
    """This user's avatar URL."""

    def __init__(self, json: dict):
        self.id = int(json['id'])
        self.username = json['username']
        self.avatar = json['avatar']

    def __repr__(self) -> str:
        return f'<{__class__.__name__} id={self.id} username={self.username!r}>'

    def __int__(self) -> int:
        return self.id

    def __eq__(self, other: 'BriefUserData') -> bool:
        if isinstance(other, __class__):
            return self.id == other.id

        return NotImplemented


class SocialData:
    """A Top.gg user's socials."""

    __slots__: tuple[str, ...] = ('youtube', 'reddit', 'twitter', 'instagram', 'github')

    youtube: str
    """This user's YouTube channel."""

    reddit: str
    """This user's Reddit username."""

    twitter: str
    """This user's Twitter username."""

    instagram: str
    """This user's Instagram username."""

    github: str
    """This user's GitHub username."""


class UserData:
    """A Top.gg user."""

    __slots__: tuple[str, ...] = (
        'id',
        'username',
        'discriminator',
        'social',
        'color',
        'supporter',
        'certified_dev',
        'mod',
        'web_mod',
        'admin',
    )

    id: int
    """This user's ID."""

    username: str
    """This user's username."""

    discriminator: str
    """This user's discriminator."""

    social: SocialData
    """This user's social links."""

    color: str
    """This user's profile color."""

    supporter: bool
    """Whether this user is a Top.gg supporter."""

    certified_dev: bool
    """Whether this user is a Top.gg certified developer."""

    mod: bool
    """Whether this user is a Top.gg moderator."""

    web_mod: bool
    """Whether this user is a Top.gg website moderator."""

    admin: bool
    """Whether this user is a Top.gg website administrator."""


class SortBy(Enum):
    """Supported sorting criterias in :meth:`.DBLClient.get_bots`."""

    __slots__: tuple[str, ...] = ()

    ID = 'id'
    """Sorts results based on each bot's ID."""

    SUBMISSION_DATE = 'date'
    """Sorts results based on each bot's submission date."""

    MONTHLY_VOTES = 'monthlyPoints'
    """Sorts results based on each bot's monthly vote count."""


class VoteDataDict:
    """A dispatched Top.gg project vote event."""

    __slots__: tuple[str, ...] = ('type', 'user', 'query')

    type: str
    """Vote event type. ``upvote`` (invoked from the vote page by a user) or ``test`` (invoked explicitly by the developer for testing.)"""

    user: int
    """The ID of the user who voted."""

    query: t.Optional[str]
    """Query strings found on the vote page."""

    def __init__(self, json: dict):
        self.type = json['type']
        self.user = int(json['user'])
        self.query = json.get('query')

    def __repr__(self) -> str:
        return f'<{__class__.__name__} type={self.type!r} user={self.user}>'


class BotVoteData(VoteDataDict):
    """A dispatched Top.gg Discord bot vote event. Extends :class:`.VoteDataDict`."""

    __slots__: tuple[str, ...] = ('bot', 'is_weekend')

    bot: int
    """The ID of the bot that received a vote."""

    is_weekend: bool
    """Whether the weekend multiplier is active or not, meaning a single vote counts as two."""

    def __init__(self, json: dict):
        super().__init__(json)

        self.bot = int(json['bot'])
        self.is_weekend = json['isWeekend']

    def __repr__(self) -> str:
        return f'<{__class__.__name__} type={self.type!r} user={self.user} is_weekend={self.is_weekend}>'


class GuildVoteData(VoteDataDict):
    """ "A dispatched Top.gg Discord server vote event. Extends :class:`.VoteDataDict`."""

    __slots__: tuple[str, ...] = ('guild',)

    guild: int
    """The ID of the server that received a vote."""

    def __init__(self, json: dict):
        super().__init__(json)

        self.guild = int(json['guild'])


ServerVoteData = GuildVoteData


@dataclasses.dataclass
class StatsWrapper:
    server_count: t.Optional[int]
    """The amount of servers the bot is in."""

    shard_count: t.Optional[int] = None
    """The amount of shards the bot has."""

    shard_id: t.Optional[int] = None
    """The shard ID the guild count belongs to."""
