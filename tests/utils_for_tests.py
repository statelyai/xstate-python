import pytest


def pytest_func_docstring_summary(request: pytest.FixtureRequest) -> str:
    """Retrieve the Summary line of the tests docstring

    Args:
        request ([type]): a pytest fixture request

    Returns:
        str: the top summary line of the Test Doc String
    """
    return request.node.function.__doc__.split("\n")[0]


class JSstyleTest:
    '''Implements a functional JS style test

    example:
    ```
          test = JSstyleTest()
          test.it(
              "should transition if string state path matches current state value"
          ).expect(
              machine.transition(
                  get_configuration_from_js(
                      """
                      {
                          a: 'a1',
                          b: {
                            b2: {
                              foo: 'foo2',
                              bar: 'bar1'
                            }
                          }
                        }
                  """
                  ),
                  "EVENT1",
              ).value
          ).toEqual(
              get_configuration_from_js(
                """
                  {
                    a: 'a2',
                    b: {
                      b2: {
                        foo: 'foo2',
                        bar: 'bar1'
                      }
                    }
                  }
                """
              )
          )

    ```
    '''

    def __init__(self):
        pass

    def it(self, message):
        self.message = message
        return self

    def expect(self, operation):
        self.operation = operation
        return self

    def toEqual(self, test):
        self.result = self.operation == test
        assert self.result, self.message
        return self
