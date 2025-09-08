from .client import BASE_URL

import enum


class WidgetType(enum.Enum):
  """
  Widget type.
  """

  DISCORD_BOT = 'discord/bot'
  DISCORD_SERVER = 'discord/server'


def large(type: WidgetType, id: int) -> str:
  """
  Generates a large widget URL.

  Example:

  .. code-block:: python

    widget_url = topgg.widget.large(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/v1/widgets/large/{type.value}/{id}'


def votes(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying votes.

  Example:

  .. code-block:: python

    widget_url = topgg.widget.votes(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/v1/widgets/small/votes/{type.value}/{id}'


def owner(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying a project's owner.

  Example:

  .. code-block:: python

    widget_url = topgg.widget.owner(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/v1/widgets/small/owner/{type.value}/{id}'


def social(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying social stats.

  Example:

  .. code-block:: python

    widget_url = topgg.widget.social(topgg.WidgetType.DISCORD_BOT, 574652751745777665)

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/v1/widgets/small/social/{type.value}/{id}'
