"""
The MIT License (MIT)

Copyright (c) 2021 Assanali Mukhanov

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

__all__ = ("WidgetOptions", "StatsWrapper")

import dataclasses
import typing as t
import warnings
from datetime import datetime

KT = t.TypeVar("KT")
VT = t.TypeVar("VT")
Colors = t.Dict[str, int]
Colours = Colors


def camel_to_snake(string: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in string]).lstrip("_")


def parse_vote_dict(d: dict) -> dict:
    data = d.copy()

    if query := data.get("query", "").lstrip("?"):
        query_dict = {k: v for k, v in [pair.split("=") for pair in query.split("&")]}
        data["query"] = DataDict(**query_dict)
    else:
        data["query"] = {}

    if "bot" in data:
        data["bot"] = int(data["bot"])

    elif "guild" in data:
        data["guild"] = int(data["guild"])

    for key, value in data.copy().items():
        if key != (converted_key := camel_to_snake(key)):
            del data[key]
            data[converted_key] = value

    return data


def parse_dict(d: dict) -> dict:
    data = d.copy()

    for key, value in data.copy().items():
        if value == "":
            value = None
        elif "id" in key.lower():
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            else:
                continue

        if key != (converted_key := camel_to_snake(key)):
            del data[key]

        data[converted_key] = value

    return data


def parse_bot_dict(d: dict) -> dict:
    data = parse_dict(d.copy())

    if (date := data.get("date")) and not isinstance(date, datetime):
        data["date"] = datetime.fromisoformat(date.replace("Z", "+00:00"))

    if owners := data.get("owners"):
        data["owners"] = [int(e) for e in owners]

    # TODO: remove this soon
    data.pop("defAvatar", None)
    data.pop("discriminator", None)
    data.pop("guilds", None)
    data.pop("certifiedBot", None)

    for key, value in data.copy().items():
        converted_key = camel_to_snake(key)
        if key != converted_key:
            del data[key]
        data[converted_key] = value

    return data


def parse_user_dict(d: dict) -> dict:
    data = d.copy()

    # TODO: remove this soon
    data.pop("discriminator", None)
    data.pop("certifiedDev", None)

    data["social"] = SocialData(**data.get("social", {}))

    return data


def parse_bot_stats_dict(d: dict) -> dict:
    data = d.copy()

    if "server_count" not in data:
        data["server_count"] = None

    return data


class DataDict(dict, t.MutableMapping[KT, VT]):
    """Base class used to represent received data from the API.

    Every data model subclasses this class.
    """

    def __init__(self, **kwargs: VT) -> None:
        super().__init__(**parse_dict(kwargs))
        self.__dict__ = self


class WidgetOptions(DataDict[str, t.Any]):
    """Model that represents widget options that are passed to Top.gg widget URL generated via
    :meth:`DBLClient.generate_widget`."""

    __slots__: t.Tuple[str, ...] = ()

    id: t.Optional[int]
    """ID of a bot to generate the widget for. Must resolve to an ID of a listed bot when converted to a string."""
    colors: Colors
    """A dictionary consisting of a parameter as a key and HEX color (type `int`) as value. ``color`` will be 
    appended to the key in case it doesn't end with ``color``."""
    noavatar: bool
    """Indicates whether to exclude the bot's avatar from short widgets. Must be of type ``bool``. Defaults to 
    ``False``."""
    format: str
    """Format to apply to the widget. Must be either ``png`` and ``svg``. Defaults to ``png``."""
    type: str
    """Type of a short widget (``status``, ``servers``, ``upvotes``, and ``owner``). For large widget, 
    must be an empty string."""

    def __init__(
        self,
        id: t.Optional[int] = None,
        format: t.Optional[str] = None,
        type: t.Optional[str] = None,
        noavatar: bool = False,
        colors: t.Optional[Colors] = None,
        colours: t.Optional[Colors] = None,
    ):
        super().__init__(
            id=id or None,
            format=format or "png",
            type=type or "",
            noavatar=noavatar or False,
            colors=colors or colours or {},
        )

    @property
    def colours(self) -> Colors:
        return self.colors

    @colours.setter
    def colours(self, value: Colors) -> None:
        self.colors = value

    def __setitem__(self, key: str, value: t.Any) -> None:
        if key == "colours":
            key = "colors"
        super().__setitem__(key, value)

    def __getitem__(self, item: str) -> t.Any:
        if item == "colours":
            item = "colors"
        return super().__getitem__(item)

    def get(self, key: str, default: t.Any = None) -> t.Any:
        """:meta private:"""
        if key == "colours":
            key = "colors"
        return super().get(key, default)


class BotData(DataDict[str, t.Any]):
    """Model that contains information about a listed bot on top.gg. The data this model contains can be found `here
    <https://docs.top.gg/api/bot/#bot-structure>`__."""

    __slots__: t.Tuple[str, ...] = ()

    id: int
    """The ID of the bot."""

    username: str
    """The username of the bot."""

    avatar: t.Optional[str]
    """The avatar hash of the bot."""

    prefix: str
    """The prefix of the bot."""

    shortdesc: str
    """The brief description of the bot."""

    longdesc: t.Optional[str]
    """The long description of the bot."""

    tags: t.List[str]
    """The tags the bot has."""

    website: t.Optional[str]
    """The website of the bot."""

    support: t.Optional[str]
    """The invite code of the bot's support server."""

    github: t.Optional[str]
    """The GitHub URL of the repo of the bot."""

    owners: t.List[int]
    """The IDs of the owners of the bot."""

    invite: t.Optional[str]
    """The invite URL of the bot."""

    date: datetime
    """The time the bot was added."""

    vanity: t.Optional[str]
    """The vanity URL of the bot."""

    points: int
    """The amount of the votes the bot has."""

    monthly_points: int
    """The amount of the votes the bot has this month."""

    donatebotguildid: int
    """The guild ID for the donatebot setup."""

    def __init__(self, **kwargs: t.Any):
        super().__init__(**parse_bot_dict(kwargs))

    @property
    def def_avatar(self) -> t.Optional[str]:
        """DEPRECATED: def_avatar is no longer supported by Top.gg API v0. At the moment, this will always be None."""

        warnings.warn(
            "def_avatar is no longer supported by Top.gg API v0. At the moment, this will always be None.",
            DeprecationWarning,
        )

    @property
    def discriminator(self) -> str:
        """DEPRECATED: Discriminators are no longer supported by Top.gg API v0. At the moment, this will always be '0'."""

        warnings.warn(
            "Discriminators are no longer supported by Top.gg API v0. At the moment, this will always be '0'.",
            DeprecationWarning,
        )
        return "0"

    @property
    def guilds(self) -> t.List[int]:
        """DEPRECATED: Guilds list is no longer supported by Top.gg API v0. At the moment, this will always be an empty list."""

        warnings.warn(
            "Guilds list is no longer supported by Top.gg API v0. At the moment, this will always be an empty list.",
            DeprecationWarning,
        )
        return []

    @property
    def certified_bot(self) -> bool:
        """DEPRECATED: Certified bot is no longer supported by Top.gg API v0. At the moment, this will always be False."""

        warnings.warn(
            "Certified bot is no longer supported by Top.gg API v0. At the moment, this will always be False.",
            DeprecationWarning,
        )
        return False


class BotStatsData(DataDict[str, t.Any]):
    """Model that contains information about a listed bot's guild count."""

    __slots__: t.Tuple[str, ...] = ()

    server_count: t.Optional[int]
    """The amount of servers the bot is in."""

    def __init__(self, **kwargs: t.Any):
        super().__init__(**parse_bot_stats_dict(kwargs))

    @property
    def shards(self) -> t.List[int]:
        """DEPRECATED: Shard-related data is no longer supported by Top.gg API v0. At the moment, this will always return an empty list."""

        warnings.warn(
            "Shard-related data is no longer supported by Top.gg API v0. At the moment, this will always return an empty list.",
            DeprecationWarning,
        )
        return []

    @property
    def shard_count(self) -> t.Optional[int]:
        """DEPRECATED: Shard-related data is no longer supported by Top.gg API v0. At the moment, this will always return None."""

        warnings.warn(
            "Shard-related data is no longer supported by Top.gg API v0. At the moment, this will always return None.",
            DeprecationWarning,
        )


class BriefUserData(DataDict[str, t.Any]):
    """Model that contains brief information about a Top.gg user."""

    __slots__: t.Tuple[str, ...] = ()

    id: int
    """The Discord ID of the user."""
    username: str
    """The Discord username of the user."""
    avatar: str
    """The Discord avatar URL of the user."""

    def __init__(self, **kwargs: t.Any):
        if kwargs["id"].isdigit():
            kwargs["id"] = int(kwargs["id"])
        super().__init__(**kwargs)


class SocialData(DataDict[str, str]):
    """Model that contains social information about a top.gg user."""

    __slots__: t.Tuple[str, ...] = ()

    youtube: str
    """The YouTube channel ID of the user."""
    reddit: str
    """The Reddit username of the user."""
    twitter: str
    """The Twitter username of the user."""
    instagram: str
    """The Instagram username of the user."""
    github: str
    """The GitHub username of the user."""


class UserData(DataDict[str, t.Any]):
    """Model that contains information about a top.gg user. The data this model contains can be found `here
    <https://docs.top.gg/api/user/#structure>`__."""

    __slots__: t.Tuple[str, ...] = ()

    id: int
    """The ID of the user."""

    username: str
    """The username of the user."""

    social: SocialData
    """The social data of the user."""

    color: str
    """The custom hex color of the user."""

    supporter: bool
    """Whether or not the user is a supporter."""

    mod: bool
    """Whether or not the user is a Top.gg mod."""

    web_mod: bool
    """Whether or not the user is a Top.gg web mod."""

    admin: bool
    """Whether or not the user is a Top.gg admin."""

    def __init__(self, **kwargs: t.Any):
        super().__init__(**parse_user_dict(kwargs))

    @property
    def certified_dev(self) -> bool:
        """DEPRECATED: Certified dev is no longer supported by Top.gg API v0. At the moment, this will always be False."""

        warnings.warn(
            "Certified dev is no longer supported by Top.gg API v0. At the moment, this will always be False.",
            DeprecationWarning,
        )
        return False

    @property
    def discriminator(self) -> str:
        """DEPRECATED: Discriminators are no longer supported by Top.gg API v0. At the moment, this will always be '0'."""

        warnings.warn(
            "Discriminators are no longer supported by Top.gg API v0. At the moment, this will always be '0'.",
            DeprecationWarning,
        )
        return "0"


class VoteDataDict(DataDict[str, t.Any]):
    """Base model that represents received information from Top.gg via webhooks."""

    __slots__: t.Tuple[str, ...] = ()

    type: str
    """Type of the action (``upvote`` or ``test``)."""
    user: int
    """ID of the voter."""
    query: DataDict
    """Query parameters in :obj:`.DataDict`."""

    def __init__(self, **kwargs: t.Any):
        super().__init__(**parse_vote_dict(kwargs))


class BotVoteData(VoteDataDict):
    """Model that contains information about a bot vote."""

    __slots__: t.Tuple[str, ...] = ()

    bot: int
    """ID of the bot the user voted for."""
    is_weekend: bool
    """Boolean value indicating whether the action was done on a weekend."""


class GuildVoteData(VoteDataDict):
    """Model that contains information about a guild vote."""

    __slots__: t.Tuple[str, ...] = ()

    guild: int
    """ID of the guild the user voted for."""


ServerVoteData = GuildVoteData


@dataclasses.dataclass
class StatsWrapper:
    guild_count: int
    """The guild count."""

    shard_count: t.Optional[int] = None
    shard_id: t.Optional[int] = None

    def __init__(self, guild_count: int, **kwargs):
        if kwargs.get("shard_count") or kwargs.get("shard_id"):
            warnings.warn("Posting shard-related data no longer has a use by Top.gg API v0.", DeprecationWarning)

        self.guild_count = guild_count
