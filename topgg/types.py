from datetime import datetime
from typing import Dict, List, Optional

Colors = Dict[str, int]
Colours = Colors


def camel_to_snake(string: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in string]).lstrip("_")


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
        kwargs = parse_dict(kwargs)
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(**parse_dict(data))
        return obj

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        setattr(self, key, value)

    def __getitem__(self, item):
        return dict.__getitem__(self, item)

    def get(self, key):
        return dict.get(self, key)


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
        dict.__setitem__(self, key, value)
        setattr(self, key, value)

    def __getitem__(self, item):
        if item == "colours":
            item = "colors"
        return dict.__getitem__(self, item)

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
