# -*- coding: utf-8 -*-

"""
Top.gg Python API Wrapper
~~~~~~~~~~~~~~~~~~~~~~
A basic wrapper for the top.gg API.
:copyright: (c) 2020 Assanali Mukhanov & top.gg
:license: MIT, see LICENSE for more details.
"""
from collections import namedtuple

__title__ = 'topggpy'
__author__ = 'Assanali Mukhanov'
__license__ = 'MIT'
VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='final', serial=0)

__version__ = f'{version_info.major}.{version_info.minor}.{version_info.micro}'


from .client import DBLClient
from .errors import *
from .http import HTTPClient
from .webhook import WebhookManager
