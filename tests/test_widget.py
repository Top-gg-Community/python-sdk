import pytest

from topgg import BASE_URL, ProjectType, Widget


@pytest.mark.parametrize('function_name', ('large', 'votes', 'owner', 'social'))
@pytest.mark.parametrize('project_type', iter(ProjectType))
def test_Widget_works(function_name: str, project_type: ProjectType):
  function = getattr(Widget, function_name)

  url = function(project_type, 123456)
  path = 'large' if function_name == 'large' else f'small/{function_name}'

  assert url == f'{BASE_URL}/widgets/{path}/{project_type._as_widget_path()}/123456'

  with pytest.raises(
    TypeError,
    match=r'^The specified project type and/or project ID\'s type is invalid.$',
  ):
    function(project_type, None)
