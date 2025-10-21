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

from .autopost import AutoPoster
from .client import DBLClient
from .data import data, DataContainerMixin
from .errors import (
    ClientException,
    ClientStateException,
    HTTPException,
    TopGGException,
    Ratelimited,
)
from .types import (
    BotData,
    BotsData,
    BotStatsData,
    BotVoteData,
    BriefUserData,
    GuildVoteData,
    ServerVoteData,
    SocialData,
    SortBy,
    StatsWrapper,
    UserData,
    VoteDataDict,
    WidgetOptions,
    WidgetProjectType,
    WidgetType,
)
from .version import VERSION
from .webhook import (
    BoundWebhookEndpoint,
    endpoint,
    WebhookEndpoint,
    WebhookManager,
    WebhookType,
)


__title__ = "topggpy"
__author__ = "null8626 & Top.gg"
__credits__ = ("null8626", "Top.gg")
__maintainer__ = "null8626"
__status__ = "Production"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2021 Assanali Mukhanov & Top.gg; Copyright (c) 2024-2025 null8626 & Top.gg"
__version__ = VERSION
__all__ = (
    "AutoPoster",
    "BotData",
    "BotsData",
    "BotStatsData",
    "BotVoteData",
    "BoundWebhookEndpoint",
    "BriefUserData",
    "ClientException",
    "ClientStateException",
    "data",
    "DataContainerMixin",
    "DBLClient",
    "endpoint",
    "GuildVoteData",
    "HTTPException",
    "Ratelimited",
    "RequestError",
    "ServerVoteData",
    "SocialData",
    "SortBy",
    "StatsWrapper",
    "TopGGException",
    "UserData",
    "VERSION",
    "VoteDataDict",
    "VoteEvent",
    "Voter",
    "WebhookEndpoint",
    "WebhookManager",
    "WebhookType",
    "WidgetOptions",
    "WidgetProjectType",
    "WidgetType",
)
