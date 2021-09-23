"""Tests for  statesin

Based on : xstate/packages/core/test/statein.test.ts

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * xxx - returns ....
    * xxx - the ....
"""
# from xstate.algorithm import is_parallel_state
from xstate.machine import Machine
from xstate.state import State
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

#TODO REMOVE after main debug effort
import sys
import importlib
# importlib.reload(sys.modules['xstate.state'])




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
# light_machine_xstate_python_config=machine_config_translate(light_machine_xstate_js_config)
# light_machine_xstate_python_config['id']="test_statesin_light"
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

class TestStatein_transition:
    """  describe('transition "in" check', () => {
    """

    def test_set_one(self):
        """
          'should transition if string state path matches current state value'

          
          #   it('should transition if string state path matches current state value', () => {
          #     expect(
          #       machine.transition(
          #         {
          #           a: 'a1',
          #           b: {
          #             b2: {
          #               foo: 'foo2',
          #               bar: 'bar1'
          #             }
          #           }
          #         },
          #         'EVENT1'
          #       ).value
          #     ).toEqual({
          #       a: 'a2',
          #       b: {
          #         b2: {
          #           foo: 'foo2',
          #           bar: 'bar1'
          #         }
          #       }
          #     });
          #   });
        """
        new_state =  machine.transition("""
            {
              a: 'a1',
              b: {
                b2: {
                  foo: 'foo2',
                  bar: 'bar1'
                }
              }
            }
          """,'EVENT1')

        assert True, 'should transition if string state path matches current state value'



 


# describe('transition "in" check', () => {
#   it('should transition if string state path matches current state value', () => {
#     expect(
#       machine.transition(
#         {
#           a: 'a1',
#           b: {
#             b2: {
#               foo: 'foo2',
#               bar: 'bar1'
#             }
#           }
#         },
#         'EVENT1'
#       ).value
#     ).toEqual({
#       a: 'a2',
#       b: {
#         b2: {
#           foo: 'foo2',
#           bar: 'bar1'
#         }
#       }
#     });
#   });

#   it('should transition if state node ID matches current state value', () => {
#     expect(
#       machine.transition(
#         {
#           a: 'a1',
#           b: {
#             b2: {
#               foo: 'foo2',
#               bar: 'bar1'
#             }
#           }
#         },
#         'EVENT3'
#       ).value
#     ).toEqual({
#       a: 'a2',
#       b: {
#         b2: {
#           foo: 'foo2',
#           bar: 'bar1'
#         }
#       }
#     });
#   });

#   it('should not transition if string state path does not match current state value', () => {
#     expect(machine.transition({ a: 'a1', b: 'b1' }, 'EVENT1').value).toEqual({
#       a: 'a1',
#       b: 'b1'
#     });
#   });

#   it('should not transition if state value matches current state value', () => {
#     expect(
#       machine.transition(
#         {
#           a: 'a1',
#           b: {
#             b2: {
#               foo: 'foo2',
#               bar: 'bar1'
#             }
#           }
#         },
#         'EVENT2'
#       ).value
#     ).toEqual({
#       a: 'a2',
#       b: {
#         b2: {
#           foo: 'foo2',
#           bar: 'bar1'
#         }
#       }
#     });
#   });

#   it('matching should be relative to grandparent (match)', () => {
#     expect(
#       machine.transition(
#         { a: 'a1', b: { b2: { foo: 'foo1', bar: 'bar1' } } },
#         'EVENT_DEEP'
#       ).value
#     ).toEqual({
#       a: 'a1',
#       b: {
#         b2: {
#           foo: 'foo2',
#           bar: 'bar1'
#         }
#       }
#     });
#   });

#   it('matching should be relative to grandparent (no match)', () => {
#     expect(
#       machine.transition(
#         { a: 'a1', b: { b2: { foo: 'foo1', bar: 'bar2' } } },
#         'EVENT_DEEP'
#       ).value
#     ).toEqual({
#       a: 'a1',
#       b: {
#         b2: {
#           foo: 'foo1',
#           bar: 'bar2'
#         }
#       }
#     });
#   });

#   it('should work to forbid events', () => {
#     const walkState = lightMachine.transition('red.walk', 'TIMER');

#     expect(walkState.value).toEqual({ red: 'walk' });

#     const waitState = lightMachine.transition('red.wait', 'TIMER');

#     expect(waitState.value).toEqual({ red: 'wait' });

#     const stopState = lightMachine.transition('red.stop', 'TIMER');

#     expect(stopState.value).toEqual('green');
#   });
# });
