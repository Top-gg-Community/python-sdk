from datetime import datetime
from typing import Dict, List, Optional

Colors = Dict[str, int]
Colours = Colors


def camel_to_snake(string: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in string]).lstrip("_")


def parse_vote_dict(d: dict) -> dict:
    data = d.copy()

    query = data.get("query", "").lstrip("?")
    if query:
        query_dict = {k: v for k, v in [pair.split("=") for pair in query.split("&")]}
        data["query"] = DataDict(**query_dict)

    if "bot" in data:
        data["bot"] = int(data["bot"])

    elif "guild" in data:
        data["guild"] = int(data["guild"])

    for key, value in data.copy().items():
        converted_key = camel_to_snake(key)
        if key != converted_key:
            del data[key]
            data[converted_key] = value

    return data


def parse_dict(d: dict) -> dict:
    data = d.copy()

    if data.get("social"):
        data["social"] = SocialData(**data["social"])

    if data.get("date") and not isinstance(data["date"], datetime):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ")

    if data.get("owners"):
        data["owners"] = [int(e) for e in data["owners"]]
    if data.get("guilds"):
        data["guilds"] = [int(e) for e in data["guilds"]]

    for key, value in data.copy().items():
        del data[key]
        if "id" in key.lower():
            if value == "":
                value = None
            else:
                if isinstance(value, int):
                    continue
                elif value.isdigit():
                    value = int(value)
        elif value == "":
            value = None
        data[camel_to_snake(key)] = value
    return data


def parse_bot_stats_dict(d: dict) -> dict:
    data = d.copy()
    if "server_count" not in data:
        data["server_count"] = None
    if "shards" not in data:
        data["shards"] = []
    if "shard_count" not in data:
        data["shard_count"] = None

    return data


class DataDict(dict):
    """Base class used to represent received data from the API.

    Every data model subclasses this class.
    """

    def __init__(self, **kwargs):
        super().__init__(**parse_dict(kwargs))
        self.__dict__ = self


class WidgetOptions(DataDict):
    """Model that represents widget options that are passed to Top.gg widget URL generated via
    :meth:`DBLClient.generate_widget`."""

    id: Optional[int]
    colors: Colors
    noavatar: bool
    format: str
    type: str

    def __init__(
        self,
        id: Optional[int] = None,
        format: str = None,
        type: str = None,
        noavatar: bool = False,
        colors: Colors = None,
        colours: Colors = None,
    ):
        super().__init__(
            id=id or None,
            format=format or "png",
            type=type or "",
            noavatar=noavatar or False,
            colors=colors or colours or {},
        )

    @property
    def colours(self) -> Colours:
        return self.colors

    @colours.setter
    def colours(self, value):
        self.colors = value

    def __setitem__(self, key, value):
        if key == "colours":
            key = "colors"
        super().__setitem__(key, value)

    def __getitem__(self, item):
        if item == "colours":
            item = "colors"
        return super().__getitem__(item)

    def get(self, key, default=None):
        if key == "colours":
            key = "colors"
        return super().get(key, default)


class BotData(DataDict):
    """Model that contains information about a listed bot on top.gg. The data this model contains can be found `here
    <https://docs.top.gg/api/bot/#bot-structure>`__."""

    id: int
    username: str
    discriminator: str
    avatar: Optional[str]
    def_avatar: str
    prefix: str
    shortdesc: str
    longdesc: Optional[str]
    tags: List[str]
    website: Optional[str]
    support: Optional[str]
    github: Optional[str]
    owners: List[int]
    guilds: List[int]
    invite: Optional[str]
    date: datetime
    certified_bot: bool
    vanity: Optional[str]
    points: int
    monthly_points: int
    donatebotguildid: int


class BotStatsData(DataDict):
    server_count: Optional[int]
    """The amount of servers the bot is in."""
    shards: List[str]
    """The amount of servers the bot is in per shard."""
    shard_count: Optional[int]
    """The amount of shards a bot has."""

    def __init__(self, **kwargs):
        super().__init__(**parse_bot_stats_dict(kwargs))
        self.__dict__ = self


class SocialData(DataDict):
    """Model that contains social information about a top.gg user."""

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


class UserData(DataDict):
    """Model that contains information about a top.gg user. The data this model contains can be found `here
    <https://docs.top.gg/api/user/#structure>`__."""

    id: int
    username: str
    discriminator: str
    social: SocialData
    color: str
    supporter: bool
    certified_dev: bool
    mod: bool
    web_mod: bool
    admin: bool


class VoteDataDict(DataDict):
    """Model that contains information about an incoming vote from top.gg."""

    type: str
    user: int
    query: Optional[Dict[str, str]]

    def __init__(self, **kwargs):
        super().__init__(**parse_vote_dict(kwargs))
        self.__dict__ = self


class BotVoteData(VoteDataDict):
    """Model that contains information about a bot vote. The data this model contains can be found `here
    <https://docs.top.gg/resources/webhooks/#bot-webhooks>`__."""

    bot: int
    is_weekend: bool


class ServerVoteData(VoteDataDict):
    """Model that contains information about a server vote. The data this model contains can be found `here
    <https://docs.top.gg/resources/webhooks/#server-webhooks>`__."""

    guild: int
