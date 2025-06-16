from .client import BASE_URL

def large(id: int) -> str:
  """
  Generates a large widget URL.

  :param id: The requested ID.
  :type id: :py:class:`int`

  :returns: The widget URL.
  :rtype: :py:class:`str`
  """

  return f'{BASE_URL}/widgets/large/{id}'