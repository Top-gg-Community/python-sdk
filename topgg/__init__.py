# -*- coding: utf-8 -*-

"""
Top.gg Python API Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the Top.gg API.
:copyright: (c) 2021 Assanali Mukhanov & Top.gg
:license: MIT, see LICENSE for more details.
"""

from collections import namedtuple

__title__ = 'topggpy'
__author__ = 'Assanali Mukhanov'
__license__ = 'MIT'
VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=1, minor=0, micro=1, releaselevel='final', serial=0)

__version__ = f'{version_info.major}.{version_info.minor}.{version_info.micro}'

from .client import DBLClient
from .http import HTTPClient
from .errors import *
from .webhook import WebhookManager
