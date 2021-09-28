import pytest


def pytest_func_docstring_summary(request: pytest.FixtureRequest) -> str:
    """Retrieve the Summary line of the tests docstring

    Args:
        request ([type]): a pytest fixture request

    Returns:
        str: the top summary line of the Test Doc String
    """
    return request.node.function.__doc__.split("\n")[0]
