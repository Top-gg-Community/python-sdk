import pytest

from topgg import BASE_URL, Platform, ProjectType, Widget


@pytest.mark.parametrize('function_name', ('large', 'votes', 'owner', 'social'))
@pytest.mark.parametrize('platform', iter(Platform))
@pytest.mark.parametrize('project_type', iter(ProjectType))
def test_Widget_works(
  function_name: str, platform: Platform, project_type: ProjectType
):
  function = getattr(Widget, function_name)

  url = function(platform, project_type, 123456)
  path = 'large' if function_name == 'large' else f'small/{function_name}'

  assert (
    url == f'{BASE_URL}/widgets/{path}/{platform.value}/{project_type.value}/123456'
  )

  with pytest.raises(
    TypeError,
    match=r'^The specified platform, project type, and/or project ID\'s type is invalid.$',
  ):
    function(platform, project_type, None)
