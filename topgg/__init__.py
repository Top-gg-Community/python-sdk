# -*- coding: utf-8 -*-

"""
Top.gg Python API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Top.gg API.
:copyright: (c) 2021 Assanali Mukhanov & Top.gg
:license: MIT, see LICENSE for more details.
"""

__title__ = "topggpy"
__author__ = "Assanali Mukhanov"
__maintainer__ = "Norizon"
__license__ = "MIT"
__version__ = "2.0.0a"

from .autopost import AutoPoster
from .client import DBLClient
from .data import Data, data
from .errors import *
from .http import HTTPClient
from .types import StatsWrapper, WidgetOptions
from .webhook import WebhookEndpoint, WebhookManager, WebhookType
