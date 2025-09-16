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
__version__ = "2.0.0a1"

from .autopost import *
from .client import *
from .data import *
from .errors import *

# can't be added to __all__ since they'd clash with automodule
from .types import *
from .types import BotVoteData, GuildVoteData
from .webhook import *
