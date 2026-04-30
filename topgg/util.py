# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from typing import TYPE_CHECKING
from datetime import datetime
from sys import version_info

if TYPE_CHECKING:
  from typing import Any

from .locale import Locale


if version_info.major == 3 and version_info.minor <= 10:  # pragma: nocover
  from re import compile

  TIMESTAMP_MILLISECOND_FIX_REGEX = compile(r'\.(\d{4,})')
  TIMESTAMP_MILLISECOND_FIX_TRIMMER = lambda match: f'.{match.group(1)[:3]}'


def parse_timestamp(timestamp: str) -> datetime:
  """Parses an ISO format timestamp to a Python datetime instance."""

  if version_info.major == 3 and version_info.minor <= 10:  # pragma: nocover
    timestamp = TIMESTAMP_MILLISECOND_FIX_REGEX.sub(
      TIMESTAMP_MILLISECOND_FIX_TRIMMER, timestamp
    )

  return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


def safe_dict(**kwargs: 'Any') -> dict:
  """Creates a new dictionary from a set of keyword arguments where None properties are not included."""

  return {key: value for key, value in kwargs.items() if value is not None}


def insert_locale_mapping(name: str, mapping: dict[Locale, str], output: dict) -> None:
  """Inserts a locale mapping to a dictionary."""

  output[name] = {}

  for locale, value in mapping.items():
    if not isinstance(locale, Locale):
      raise TypeError("The locale mapping's keys must be an instance of Locale.")

    output[name][locale.value] = value
