# -*- coding: utf-8 -*-

"""
DBL Python API Wrapper
~~~~~~~~~~~~~~~~~~~
A basic wrapper for the discordbots.org API.
:copyright: (c) 2018 Francis Taylor & discordbots.org
:license: MIT, see LICENSE for more details.
"""

__title__ = 'dblpy'
__author__ = 'Francis Taylor'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018 Francis Taylor'
__version__ = '0.1.2'

from .client import Client
from .http import HTTPClient

from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=1, micro=2, releaselevel='final', serial=0)
