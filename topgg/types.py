from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")
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
    else:
        data["query"] = {}

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

    for key, value in data.copy().items():
        if "id" in key.lower():
            if value == "":
                value = None
            else:
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                else:
                    continue
        elif value == "":
            value = None

        converted_key = camel_to_snake(key)
        if key != converted_key:
            del data[key]
        data[converted_key] = value

    return data


def parse_bot_dict(d: dict) -> dict:
    data = parse_dict(d.copy())

    if data.get("date") and not isinstance(data["date"], datetime):
        data["date"] = datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S.%fZ")

    if data.get("owners"):
        data["owners"] = [int(e) for e in data["owners"]]
    if data.get("guilds"):
        data["guilds"] = [int(e) for e in data["guilds"]]

    for key, value in data.copy().items():
        converted_key = camel_to_snake(key)
        if key != converted_key:
            del data[key]
        data[converted_key] = value

    return data


def parse_user_dict(d: dict) -> dict:
    data = d.copy()

    data["social"] = SocialData(**data.get("social", {}))

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


class DataDict(dict, MutableMapping[KT, VT]):
    """Base class used to represent received data from the API.

    Every data model subclasses this class.
    """

    def __init__(self, **kwargs: VT) -> None:
        super().__init__(**parse_dict(kwargs))
        self.__dict__ = self


class WidgetOptions(DataDict[str, Any]):
    """Model that represents widget options that are passed to Top.gg widget URL generated via
    :meth:`DBLClient.generate_widget`."""

    id: Optional[int]
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
    """Type of a short widget (``status``, ``servers``, ``library``, ``upvotes``, and ``owner``). For large widget, 
    must be an empty string."""

    def __init__(
        self,
        id: Optional[int] = None,
        format: Optional[str] = None,
        type: Optional[str] = None,
        noavatar: bool = False,
        colors: Optional[Colors] = None,
        colours: Optional[Colors] = None,
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

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "colours":
            key = "colors"
        super().__setitem__(key, value)

    def __getitem__(self, item: str) -> Any:
        if item == "colours":
            item = "colors"
        return super().__getitem__(item)

    def get(self, key: str, default: Any = None) -> Any:
        """:meta private:"""
        if key == "colours":
            key = "colors"
        return super().get(key, default)


class BotData(DataDict[str, Any]):
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

    def __init__(self, **kwargs: Any):
        super().__init__(**parse_bot_dict(kwargs))


class BotStatsData(DataDict[str, Any]):
    """Model that contains information about a listed bot's guild and shard count."""

    server_count: Optional[int]
    """The amount of servers the bot is in."""
    shards: List[int]
    """The amount of servers the bot is in per shard."""
    shard_count: Optional[int]
    """The amount of shards a bot has."""

    def __init__(self, **kwargs: Any):
        super().__init__(**parse_bot_stats_dict(kwargs))


class BriefUserData(DataDict[str, Any]):
    """Model that contains brief information about a Top.gg user."""

    id: int
    """The Discord ID of the user."""
    username: str
    """The Discord username of the user."""
    avatar: str
    """The Discord avatar URL of the user."""

    def __init__(self, **kwargs: Any):
        if kwargs["id"].isdigit():
            kwargs["id"] = int(kwargs["id"])
        super().__init__(**kwargs)


class SocialData(DataDict[str, str]):
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


class UserData(DataDict[str, Any]):
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

    def __init__(self, **kwargs: Any):
        super().__init__(**parse_user_dict(kwargs))


class VoteDataDict(DataDict[str, Any]):
    """Base model that represents received information from Top.gg via webhooks."""

    type: str
    """Type of the action (``upvote`` or ``test``)."""
    user: int
    """ID of the voter."""
    query: DataDict
    """Query parameters in :ref:`DataDict`."""

    def __init__(self, **kwargs: Any):
        super().__init__(**parse_vote_dict(kwargs))


class BotVoteData(VoteDataDict):
    """Model that contains information about a bot vote."""

    bot: int
    """ID of the bot the user voted for."""
    is_weekend: bool
    """Boolean value indicating whether the action was done on a weekend."""


class ServerVoteData(VoteDataDict):
    """Model that contains information about a server vote."""

    guild: int
    """ID of the guild the user voted for."""
