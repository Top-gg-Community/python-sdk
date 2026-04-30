from datetime import datetime
from sys import version_info


if version_info.major == 3 and version_info.minor <= 10:
  from re import compile

  TIMESTAMP_MILLISECOND_FIX_REGEX = compile(r'\.(\d+)')
  TIMESTAMP_MILLISECOND_FIX_TRIMMER = lambda match: match.group(1)[:3]


def parse_timestamp(timestamp: str) -> datetime:
  """Parses an ISO format timestamp to a Python datetime instance."""

  if version_info.major == 3 and version_info.minor <= 10:
    timestamp = TIMESTAMP_MILLISECOND_FIX_REGEX.sub(
      TIMESTAMP_MILLISECOND_FIX_TRIMMER, timestamp
    )

  return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
