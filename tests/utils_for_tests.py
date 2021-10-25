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
        self._definitions = None
        self.message = message

        return self

    def do(self, **kwargs):
        self._definitions = kwargs
        return self

    def expect(self, operation):
        self.operation = operation
        if isinstance(self.operation, str) and self._definitions is not None:
            for d in self._definitions.keys():
                if str(d) in operation:
                    self.operation = eval(operation, {}, self._definitions)

        return self

    def toEqual(self, test):
        self.result = self.operation == test
        assert (
            self.result
        ), f"{self.message}, test value:{self.operation}, should be:{test}"
        return self
