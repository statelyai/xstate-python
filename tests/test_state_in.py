"""Tests for  statesin

These tests test transitions, some of the tests test the transition guard capabilities
ie only transition if state is in a particular state `in State` 
see https://xstate.js.org/docs/guides/guards.html#in-state-guards

Based on : xstate/packages/core/test/statein.test.ts

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * xxx - returns ....
    * xxx - the ....
"""
# from xstate.algorithm import is_parallel_state
from webbrowser import get
from xstate.machine import Machine
from xstate.algorithm import get_configuration_from_js

# from xstate.state import State
# import {
#   Machine,
#   State,
#   StateFrom,
#   interpret,
#   createMachine,
#   spawn
# } from '../src/index';
# import { initEvent, assign } from '../src/actions';
# import { toSCXMLEvent } from '../src/utils';


import pytest
from .utils_for_tests import JSstyleTest, pytest_func_docstring_summary

machine_xstate_js_config = """{
  type: 'parallel',
  states: {
    a: {
      initial: 'a1',
      states: {
        a1: {
          on: {
            EVENT1: {
              target: 'a2',
              in: 'b.b2'
            },
            EVENT2: {
              target: 'a2',
              in: { b: 'b2' }
            },
            EVENT3: {
              target: 'a2',
              in: '#b_b2'
            }
          }
        },
        a2: {}
      }
    },
    b: {
      initial: 'b1',
      states: {
        b1: {
          on: {
            EVENT: {
              target: 'b2',
              in: 'a.a2'
            }
          }
        },
        b2: {
          id: 'b_b2',
          type: 'parallel',
          states: {
            foo: {
              initial: 'foo1',
              states: {
                foo1: {
                  on: {
                    EVENT_DEEP: { target: 'foo2', in: 'bar.bar1' }
                  }
                },
                foo2: {}
              }
            },
            bar: {
              initial: 'bar1',
              states: {
                bar1: {},
                bar2: {}
              }
            }
          }
        }
      }
    }
  }
}"""

machine = Machine(machine_xstate_js_config)


light_machine_xstate_js_config = """{
  id: 'light',
  initial: 'green',
  states: {
    green: { on: { TIMER: 'yellow' } },
    yellow: { on: { TIMER: 'red' } },
    red: {
      initial: 'walk',
      states: {
        walk: {},
        wait: {},
        stop: {}
      },
      on: {
        TIMER: [
          {
            target: 'green',
            in: { red: 'stop' }
          }
        ]
      }
    }
  }
}"""

light_machine = Machine(light_machine_xstate_js_config)


# type Events =
#   | { type: 'BAR_EVENT' }
#   | { type: 'DEEP_EVENT' }
#   | { type: 'EXTERNAL' }
#   | { type: 'FOO_EVENT' }
#   | { type: 'FORBIDDEN_EVENT' }
#   | { type: 'INERT' }
#   | { type: 'INTERNAL' }
#   | { type: 'MACHINE_EVENT' }
#   | { type: 'P31' }
#   | { type: 'P32' }
#   | { type: 'THREE_EVENT' }
#   | { type: 'TO_THREE' }
#   | { type: 'TO_TWO'; foo: string }
#   | { type: 'TO_TWO_MAYBE' }
#   | { type: 'TO_FINAL' };


class TestStateIn_transition:
    """describe('transition "in" check', () => {"""

    def test_transition_if_string_state_path_matches_current_state_value(self, request):
        """should transition if string state path matches current state value"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
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

    def test_should_transition_if_state_node_id_matches_current_state_value(
        self, request
    ):
        """should transition if state node ID matches current state value"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
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
                "EVENT3",
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

    #   it('should not transition if string state path does not match current state value', () => {
    def test_should_not_transition_if_string_state_path_does_not_match_current_state_value(
        self, request
    ):
        """should not transition if string state path does not match current state value"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            machine.transition(
                get_configuration_from_js(
                    """
                    { 
                      a: 'a1',
                      b: 'b1' 
                    }
                """
                ),
                "EVENT1",
            ).value
        ).toEqual(
            get_configuration_from_js(
                """
                  {
                      a: 'a1',
                      b: 'b1'
                  }
                """
            )
        )

    #   it('should not transition if state value matches current state value', () => {
    def test_should_not_transition_if_state_value_matches_current_state_value(
        self, request
    ):
        """should not transition if state value matches current state value"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
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
                "EVENT2",
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

    #   it('matching should be relative to grandparent (match)', () => {
    def test_matching_should_be_relative_to_grandparent_match(self, request):
        """matching should be relative to grandparent (match)"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            machine.transition(
                get_configuration_from_js(
                    """
                        { 
                          a: 'a1', 
                          b: { 
                            b2: 
                             {
                                foo: 'foo1', 
                                bar: 'bar1'
                              } 
                              } 
                        }
                              
                      """
                ),
                "EVENT_DEEP",
            ).value
        ).toEqual(
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
            )
        )

    #  it('matching should be relative to grandparent (no match)', () => {
    @pytest.mark.skip(reason="Transition Guards, not yet implemented")
    def test_matching_should_be_relative_to_grandparent_no_match(self, request):
        """matching should be relative to grandparent (no match)
            ie. transitioning a state dependent on a relative state
                only transition `foo.foo2` if a relative has current state as `bar.bar1`
        see https://xstate.js.org/docs/guides/guards.html#in-state-guards
        """
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            machine.transition(
                get_configuration_from_js(
                    """
                      { 
                        a: 'a1',
                        b: {
                            b2: 
                            {
                              foo: 'foo1',
                              bar: 'bar2' 
                            } 
                            }
                      }
                    """
                ),
                "EVENT_DEEP",
            ).value
        ).toEqual(
            get_configuration_from_js(
                """      
            {
              a: 'a1',
              b: {
                b2: {
                  foo: 'foo1',
                  bar: 'bar2'
                }
              }
            }
          """
            )
        )

    #   it('should work to forbid events', () => {
    @pytest.mark.skip(reason="Transition Guards, not yet implemented")
    def test_should_work_to_forbid_events(self, request):
        """should work to forbid events
          ie. transitioning a state dependent on being in a particular state
                only transition to `#light.green` if `#light.red` substate is `red.stop`
        see https://xstate.js.org/docs/guides/guards.html#in-state-guards

        """
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).do(
            walkState=light_machine.transition("red.walk", "TIMER")
        ).expect("walkState.value").toEqual({"red": "walk"}).do(
            waitState=light_machine.transition("red.wait", "TIMER")
        ).expect(
            "waitState.value"
        ).toEqual(
            {"red": "wait"}
        ).do(
            stopState=light_machine.transition("red.stop", "TIMER")
        ).expect(
            "stopState.value"
        ).toEqual(
            "green"
        )
