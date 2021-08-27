# -*- coding: utf-8 -*-

"""
Top.gg Python API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Top.gg API.
:copyright: (c) 2021 Assanali Mukhanov & Top.gg
:license: MIT, see LICENSE for more details.
"""

from collections import namedtuple

__title__ = "topggpy"
__author__ = "Assanali Mukhanov"
__license__ = "MIT"
__version__ = "1.4.0"

VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
major, minor, micro = (int(i) for i in __version__.split("."))
version_info = VersionInfo(
    major=major, minor=minor, micro=micro, releaselevel="final", serial=0
)

from .client import DBLClient
from .errors import *
from .http import HTTPClient
from .types import WidgetOptions
from .webhook import WebhookManager
