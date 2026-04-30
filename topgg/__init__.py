# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from .webhooks import (
  Listener,
  IntegrationCreateListener,
  IntegrationDeleteListener,
  TestListener,
  VoteCreateListener,
  Webhooks,
)
from .payload import (
  IntegrationCreatePayload,
  IntegrationDeletePayload,
  Payload,
  PayloadType,
  TestPayload,
  VoteCreatePayload,
)
from .user import PaginatedVotes, PartialVote, User, UserSource, Vote
from .project import Locale, PartialProject, Platform, Project, ProjectType
from .client import API_VERSION, BASE_URL, Client
from .errors import Error, Ratelimited, RequestError
from .ratelimiter import Ratelimiter
from .version import VERSION
from .widget import Widget


__title__ = 'topggpy'
__author__ = 'null8626 & Top.gg'
__credits__ = ('null8626', 'Top.gg')
__maintainer__ = 'null8626'
__status__ = 'Production'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024-2026 null8626 & Top.gg'
__version__ = VERSION
__all__ = (
  'API_VERSION',
  'BASE_URL',
  'Client',
  'Error',
  'IntegrationCreateListener',
  'IntegrationCreatePayload',
  'IntegrationDeleteListener',
  'IntegrationDeletePayload',
  'Listener',
  'Locale',
  'PaginatedVotes',
  'PartialProject',
  'PartialVote',
  'Payload',
  'PayloadType',
  'Platform',
  'Project',
  'ProjectType',
  'Ratelimited',
  'Ratelimiter',
  'RequestError',
  'TestListener',
  'TestPayload',
  'User',
  'UserSource',
  'VERSION',
  'Vote',
  'VoteCreateListener',
  'VoteCreatePayload',
  'Webhooks',
  'Widget',
)
