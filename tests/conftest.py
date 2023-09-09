import pytest


@pytest.fixture
def with_plt(request):
    return request.config.getoption("--plots")
