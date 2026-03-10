# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 null8626 & Top.gg

from .project import ProjectType
from .client import BASE_URL


class Widget:
  """A Top.gg widget URL generator."""

  __slots__: tuple[str, ...] = ()

  @staticmethod
  def large(project_type: ProjectType, id: int) -> str:
    """
    Generates a large widget URL.

    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified project type and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError("The specified project type and/or project ID's type is invalid.")

    return f'{BASE_URL}/widgets/large/{project_type._as_widget_path()}/{id}'

  @staticmethod
  def votes(project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying votes.

    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified project type and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError("The specified project type and/or project ID's type is invalid.")

    return f'{BASE_URL}/widgets/small/votes/{project_type._as_widget_path()}/{id}'

  @staticmethod
  def owner(project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying a project's owner.

    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified project type and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError("The specified project type and/or project ID's type is invalid.")

    return f'{BASE_URL}/widgets/small/owner/{project_type._as_widget_path()}/{id}'

  @staticmethod
  def social(project_type: ProjectType, id: int) -> str:
    """
    Generates a small widget URL for displaying social stats.

    :param project_type: The project's type.
    :type project_type: :class:`.ProjectType`
    :param id: The project's ID.
    :type id: :py:class:`int`

    :exception TypeError: The specified project type and/or project ID's type is invalid.

    :returns: The widget URL.
    :rtype: :py:class:`.str`
    """

    if not isinstance(project_type, ProjectType) or not isinstance(id, int):
      raise TypeError("The specified project type and/or project ID's type is invalid.")

    return f'{BASE_URL}/widgets/small/social/{project_type._as_widget_path()}/{id}'
