# -*- coding: utf-8 -*-

"""
Top.gg Python API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Top.gg API.
:copyright: (c) 2021 Assanali Mukhanov & Top.gg
:license: MIT, see LICENSE for more details.
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
