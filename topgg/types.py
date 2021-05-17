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
        data["social"] = SocialData(data["social"])

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
                    break
                elif value.isdigit():
                    value = int(value)
        elif value == "":
            value = None
        data[camel_to_snake(key)] = value
    return data


class DataDict(dict):
    def __init__(self, *args, **kwargs):
        self.__dict__ = parse_dict(kwargs)

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(**data)
        return obj

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]

    def get(self, key):
        return self.__dict__.get(key)

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


class WidgetOptions(DataDict):
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

    def get(self, key):
        if key == "colours":
            key = "colors"
        return super().get(key)


class SocialData(DataDict):
    youtube: str
    reddit: str
    twitter: str
    instagram: str
    github: str


class BotData(DataDict):
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


class UserData(DataDict):
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
    type: str
    user: int
    query: Optional[Dict[str, str]]

    def __init__(self, **kwargs):
        self.__dict__ = parse_vote_dict(kwargs)


class BotVoteData(VoteDataDict):
    bot: int
    is_weekend: bool


class ServerVoteData(VoteDataDict):
    guild: int
