# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021-2024 Assanali Mukhanov & Top.gg
# SPDX-FileCopyrightText: 2024-2026 null8626 & Top.gg

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from typing import Any


class Error(Exception):
  """The base error class. Extends :py:class:`Exception`."""

  __slots__: tuple[str, ...] = ()


@dataclass(frozen=True, repr=False, slots=True)
class RequestError(Error):
  """Thrown upon HTTP request failure. Extends :class:`~.errors.Error`."""

  data: 'Any'
  """The JSON error data returned from the API."""

  status: int | None
  """The status code returned from the API."""

  def __post_init__(self) -> None:
    super(Error, self).__init__(f'Got {self.status}: {self.data!r}')

  def __repr__(self) -> str:
    return f'<{__class__.__name__} data={self.data!r} status={self.status}>'


@dataclass(frozen=True, repr=False, slots=True)
class Ratelimited(Error):
  """Thrown upon HTTP request failure due to the client being ratelimited. Because of this, the client is not allowed to make requests for a period of time. Extends :class:`~.errors.Error`."""

  retry_after: float
  """How long the client should wait (in seconds) until it can make a request to the API again."""

  def __post_init__(self) -> None:
    super(Error, self).__init__(
      f'The client is blocked by the API. Please try again in {self.retry_after} seconds.'
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} retry_after={self.retry_after}>'
