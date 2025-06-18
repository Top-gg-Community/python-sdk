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

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/widgets/large/{type.value}/{id}'


def votes(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying votes.

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/widgets/small/votes/{type.value}/{id}'


def owner(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying an entity's owner.

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/widgets/small/owner/{type.value}/{id}'


def social(type: WidgetType, id: int) -> str:
  """
  Generates a small widget URL for displaying social stats.

  :param type: The widget type.
  :type type: :class:`.WidgetType`
  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/widgets/small/social/{type.value}/{id}'
