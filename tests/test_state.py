"""Tests for  states

Based on : xstate/packages/core/test/state.test.ts

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * xxx - returns ....
    * xxx - the ....
"""
import pytest
from xstate.algorithm import (
    get_configuration_from_js
)
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

import sys
import importlib
# importlib.reload(sys.modules['xstate.state'])

from .utils_for_tests import pytest_func_docstring_summary

#TODO: state `one` transition `TO_TWO_MAYBE` condition function needs to be handled
machine_xstate_js_config ="""{
  initial: 'one',
  states: {
    one: {
      entry: ['enter'],
      on: {
        EXTERNAL: {
          target: 'one',
          internal: false
        },
        INERT: {
          target: 'one',
          internal: true
        },
        INTERNAL: {
          target: 'one',
          internal: true,
          actions: ['doSomething']
        },
        TO_TWO: 'two',
        TO_TWO_MAYBE: {
          target: 'two',
        /*  cond: function maybe() {
            return true;
          }*/
        },
        TO_THREE: 'three',
        FORBIDDEN_EVENT: undefined,
        TO_FINAL: 'success'
      }
    },
    two: {
      initial: 'deep',
      states: {
        deep: {
          initial: 'foo',
          states: {
            foo: {
              on: {
                FOO_EVENT: 'bar',
                FORBIDDEN_EVENT: undefined
              }
            },
            bar: {
              on: {
                BAR_EVENT: 'foo'
              }
            }
          }
        }
      },
      on: {
        DEEP_EVENT: '.'
      }
    },
    three: {
      type: 'parallel',
      states: {
        first: {
          initial: 'p31',
          states: {
            p31: {
              on: { P31: '.' }
            }
          }
        },
        second: {
          initial: 'p32',
          states: {
            p32: {
              on: { P32: '.' }
            }
          }
        }
      },
      on: {
        THREE_EVENT: '.'
      }
    },
    success: {
      type: 'final'
    }
  },
  on: {
    MACHINE_EVENT: '.two'
  }
}"""
xstate_python_config=get_configuration_from_js(machine_xstate_js_config)
# xstate_python_config['id']="test_states"

#TODO:  machine initialization fail on `if config.get("entry")`` in xstate/state_node.py", line 47, in __init__
"""
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/workspaces/xstate-python/xstate/machine.py", line 26, in __init__
    config, machine=self, key=config.get("id", "(machine)"), parent=None
  File "/workspaces/xstate-python/xstate/state_node.py", line 60, in __init__
    for k, v in config.get("states", {}).items()
  File "/workspaces/xstate-python/xstate/state_node.py", line 60, in <dictcomp>
    for k, v in config.get("states", {}).items()
  File "/workspaces/xstate-python/xstate/state_node.py", line 47, in __init__
    if config.get("entry")
  File "/workspaces/xstate-python/xstate/state_node.py", line 46, in <listcomp>
    [self.get_actions(entry_action) for entry_action in config.get("entry")]
  File "/workspaces/xstate-python/xstate/state_node.py", line 28, in get_actions
    return Action(action.get("type"), exec=None, data=action)
AttributeError: 'str' object has no attribute 'get'
"""
# TODO remove Workaround for above issue
del xstate_python_config['states']['one']['on']['INTERNAL']['actions']

# xstate_python_config['states']['one']['on']['INTERNAL']['actions']=['doSomething']
del xstate_python_config['states']['one']['entry']
# xstate_python_config['states']['one']['entry'] =['enter']
machine = Machine(xstate_python_config)






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

class TestState_changed:
    """ describe('State .changed ', () => { 
        describe('.changed', () => {
    """
    @pytest.mark.skip(reason="Not implemented yet")
    def test_not_changed_if_initial_state(self,request):
        """" 1 - should indicate that it is not changed if initial state
        
        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

            it('should indicate that it is not changed if initial state', () => {
            expect(machine.initialState.changed).not.toBeDefined();
            });
        """
        assert machine.initial_state.changed == None, pytest_func_docstring_summary(request)
    @pytest.mark.skip(reason="Not implemented yet")
    def test_external_transitions_with_entry_actions_should_be_changed(self,request):
        """" 2 - states from external transitions with entry actions should be changed

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts
 
            it('states from external transitions with entry actions should be changed', () => {
            const changedState = machine.transition(machine.initialState, 'EXTERNAL');
            expect(changedState.changed).toBe(true);
            });
        """
        changed_state = machine.transition(machine.initial_state, 'EXTERNAL')
        assert changed_state.changed == True , pytest_func_docstring_summary(request)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_not_yet_implemented(self,request):
        """ UNimplemented Tests

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

        #     it('states from internal transitions with no actions should be unchanged', () => {
        #       const changedState = machine.transition(machine.initialState, 'EXTERNAL');
        #       const unchangedState = machine.transition(changedState, 'INERT');
        #       expect(unchangedState.changed).toBe(false);
        #     });

        #     it('states from internal transitions with actions should be changed', () => {
        #       const changedState = machine.transition(machine.initialState, 'INTERNAL');
        #       expect(changedState.changed).toBe(true);
        #     });

        #     it('normal state transitions should be changed (initial state)', () => {
        #       const changedState = machine.transition(machine.initialState, 'TO_TWO');
        #       expect(changedState.changed).toBe(true);
        #     });

        #     it('normal state transitions should be changed', () => {
        #       const twoState = machine.transition(machine.initialState, 'TO_TWO');
        #       const changedState = machine.transition(twoState, 'FOO_EVENT');
        #       expect(changedState.changed).toBe(true);
        #     });

        #     it('normal state transitions with unknown event should be unchanged', () => {
        #       const twoState = machine.transition(machine.initialState, 'TO_TWO');
        #       const changedState = machine.transition(twoState, 'UNKNOWN_EVENT' as any);
        #       expect(changedState.changed).toBe(false);
        #     });

        #     it('should report entering a final state as changed', () => {
        #       const finalMachine = Machine({
        #         id: 'final',
        #         initial: 'one',
        #         states: {
        #           one: {
        #             on: {
        #               DONE: 'two'
        #             }
        #           },

        #           two: {
        #             type: 'final'
        #           }
        #         }
        #       });

        #       const twoState = finalMachine.transition('one', 'DONE');

        #       expect(twoState.changed).toBe(true);
        #     });

        #     it('should report any internal transition assignments as changed', () => {
        #       const assignMachine = Machine<{ count: number }>({
        #         id: 'assign',
        #         initial: 'same',
        #         context: {
        #           count: 0
        #         },
        #         states: {
        #           same: {
        #             on: {
        #               EVENT: {
        #                 actions: assign({ count: (ctx) => ctx.count + 1 })
        #               }
        #             }
        #           }
        #         }
        #       });

        #       const { initialState } = assignMachine;
        #       const changedState = assignMachine.transition(initialState, 'EVENT');
        #       expect(changedState.changed).toBe(true);
        #       expect(initialState.value).toEqual(changedState.value);
        #     });

        #     it('should not escape targetless child state nodes', () => {
        #       interface Ctx {
        #         value: string;
        #       }
        #       type ToggleEvents =
        #         | {
        #             type: 'CHANGE';
        #             value: string;
        #           }
        #         | {
        #             type: 'SAVE';
        #           };
        #       const toggleMachine = Machine<Ctx, ToggleEvents>({
        #         id: 'input',
        #         context: {
        #           value: ''
        #         },
        #         type: 'parallel',
        #         states: {
        #           edit: {
        #             on: {
        #               CHANGE: {
        #                 actions: assign({
        #                   value: (_, e) => {
        #                     return e.value;
        #                   }
        #                 })
        #               }
        #             }
        #           },
        #           validity: {
        #             initial: 'invalid',
        #             states: {
        #               invalid: {},
        #               valid: {}
        #             },
        #             on: {
        #               CHANGE: [
        #                 {
        #                   target: '.valid',
        #                   cond: () => true
        #                 },
        #                 {
        #                   target: '.invalid'
        #                 }
        #               ]
        #             }
        #           }
        #         }
        #       });

        #       const nextState = toggleMachine.transition(toggleMachine.initialState, {
        #         type: 'CHANGE',
        #         value: 'whatever'
        #       });

        #       expect(nextState.changed).toBe(true);
        #       expect(nextState.value).toEqual({
        #         edit: {},
        #         validity: 'valid'
        #       });
        #     });
        #   });

        #   describe('.nextEvents', () => {
        #     it('returns the next possible events for the current state', () => {
        #       expect(machine.initialState.nextEvents.sort()).toEqual([
        #         'EXTERNAL',
        #         'INERT',
        #         'INTERNAL',
        #         'MACHINE_EVENT',
        #         'TO_FINAL',
        #         'TO_THREE',
        #         'TO_TWO',
        #         'TO_TWO_MAYBE'
        #       ]);

        #       expect(
        #         machine.transition(machine.initialState, 'TO_TWO').nextEvents.sort()
        #       ).toEqual(['DEEP_EVENT', 'FOO_EVENT', 'MACHINE_EVENT']);

        #       expect(
        #         machine.transition(machine.initialState, 'TO_THREE').nextEvents.sort()
        #       ).toEqual(['MACHINE_EVENT', 'P31', 'P32', 'THREE_EVENT']);
        #     });

        #     it('returns events when transitioned from StateValue', () => {
        #       const A = machine.transition(machine.initialState, 'TO_THREE');
        #       const B = machine.transition(A.value, 'TO_THREE');

        #       expect(B.nextEvents.sort()).toEqual([
        #         'MACHINE_EVENT',
        #         'P31',
        #         'P32',
        #         'THREE_EVENT'
        #       ]);
        #     });

        #     it('returns no next events if there are none', () => {
        #       const noEventsMachine = Machine({
        #         id: 'no-events',
        #         initial: 'idle',
        #         states: {
        #           idle: {
        #             on: {}
        #           }
        #         }
        #       });

        #       expect(noEventsMachine.initialState.nextEvents).toEqual([]);
        #     });
        #   });

        #   describe('State.create()', () => {
        #     it('should be able to create a state from a JSON config', () => {
        #       const { initialState } = machine;
        #       const jsonInitialState = JSON.parse(JSON.stringify(initialState));

        #       const stateFromConfig = State.create(jsonInitialState) as StateFrom<
        #         typeof machine
        #       >;

        #       expect(machine.transition(stateFromConfig, 'TO_TWO').value).toEqual({
        #         two: { deep: 'foo' }
        #       });
        #     });

        #     it('should preserve state.nextEvents using machine.resolveState', () => {
        #       const { initialState } = machine;
        #       const { nextEvents } = initialState;
        #       const jsonInitialState = JSON.parse(JSON.stringify(initialState));

        #       const stateFromConfig = State.create(jsonInitialState) as StateFrom<
        #         typeof machine
        #       >;

        #       expect(machine.resolveState(stateFromConfig).nextEvents.sort()).toEqual(
        #         nextEvents.sort()
        #       );
        #     });
        #   });

        #   describe('State.inert()', () => {
        #     it('should create an inert instance of the given State', () => {
        #       const { initialState } = machine;

        #       expect(State.inert(initialState, undefined).actions).toEqual([]);
        #     });

        #     it('should create an inert instance of the given stateValue and context', () => {
        #       const { initialState } = machine;
        #       const inertState = State.inert(initialState.value, { foo: 'bar' });

        #       expect(inertState.actions).toEqual([]);
        #       expect(inertState.context).toEqual({ foo: 'bar' });
        #     });

        #     it('should preserve the given State if there are no actions', () => {
        #       const naturallyInertState = State.from('foo');

        #       expect(State.inert(naturallyInertState, undefined)).toEqual(
        #         naturallyInertState
        #       );
        #     });
        #   });

        #   describe('.event', () => {
        #     it('the .event prop should be the event (string) that caused the transition', () => {
        #       const { initialState } = machine;

        #       const nextState = machine.transition(initialState, 'TO_TWO');

        #       expect(nextState.event).toEqual({ type: 'TO_TWO' });
        #     });

        #     it('the .event prop should be the event (object) that caused the transition', () => {
        #       const { initialState } = machine;

        #       const nextState = machine.transition(initialState, {
        #         type: 'TO_TWO',
        #         foo: 'bar'
        #       });

        #       expect(nextState.event).toEqual({ type: 'TO_TWO', foo: 'bar' });
        #     });

        #     it('the ._event prop should be the initial event for the initial state', () => {
        #       const { initialState } = machine;

        #       expect(initialState._event).toEqual(initEvent);
        #     });
        #   });

        #   describe('._event', () => {
        #     it('the ._event prop should be the SCXML event (string) that caused the transition', () => {
        #       const { initialState } = machine;

        #       const nextState = machine.transition(initialState, 'TO_TWO');

        #       expect(nextState._event).toEqual(toSCXMLEvent('TO_TWO'));
        #     });

        #     it('the ._event prop should be the SCXML event (object) that caused the transition', () => {
        #       const { initialState } = machine;

        #       const nextState = machine.transition(initialState, {
        #         type: 'TO_TWO',
        #         foo: 'bar'
        #       });

        #       expect(nextState._event).toEqual(
        #         toSCXMLEvent({ type: 'TO_TWO', foo: 'bar' })
        #       );
        #     });

        #     it('the ._event prop should be the initial SCXML event for the initial state', () => {
        #       const { initialState } = machine;

        #       expect(initialState._event).toEqual(toSCXMLEvent(initEvent));
        #     });

        #     it('the ._event prop should be the SCXML event (SCXML metadata) that caused the transition', () => {
        #       const { initialState } = machine;

        #       const nextState = machine.transition(
        #         initialState,
        #         toSCXMLEvent(
        #           {
        #             type: 'TO_TWO',
        #             foo: 'bar'
        #           },
        #           {
        #             sendid: 'test'
        #           }
        #         )
        #       );

        #       expect(nextState._event).toEqual(
        #         toSCXMLEvent(
        #           { type: 'TO_TWO', foo: 'bar' },
        #           {
        #             sendid: 'test'
        #           }
        #         )
        #       );
        #     });

        #     describe('_sessionid', () => {
        #       it('_sessionid should be null for non-invoked machines', () => {
        #         const testMachine = Machine({
        #           initial: 'active',
        #           states: {
        #             active: {}
        #           }
        #         });

        #         expect(testMachine.initialState._sessionid).toBeNull();
        #       });

        #       it('_sessionid should be the service sessionId for invoked machines', (done) => {
        #         const testMachine = Machine({
        #           initial: 'active',
        #           states: {
        #             active: {
        #               on: {
        #                 TOGGLE: 'inactive'
        #               }
        #             },
        #             inactive: {
        #               type: 'final'
        #             }
        #           }
        #         });

        #         const service = interpret(testMachine);

        #         service
        #           .onTransition((state) => {
        #             expect(state._sessionid).toEqual(service.sessionId);
        #           })
        #           .onDone(() => {
        #             done();
        #           })
        #           .start();

        #         service.send('TOGGLE');
        #       });

        #       it('_sessionid should persist through states (manual)', () => {
        #         const testMachine = Machine({
        #           initial: 'active',
        #           states: {
        #             active: {
        #               on: {
        #                 TOGGLE: 'inactive'
        #               }
        #             },
        #             inactive: {
        #               type: 'final'
        #             }
        #           }
        #         });

        #         const { initialState } = testMachine;

        #         initialState._sessionid = 'somesessionid';

        #         const nextState = testMachine.transition(initialState, 'TOGGLE');

        #         expect(nextState._sessionid).toEqual('somesessionid');
        #       });
        #     });
        #   });
            it('states from external transitions with entry actions should be changed', () => {
            const changedState = machine.transition(machine.initialState, 'EXTERNAL');
            expect(changedState.changed).toBe(true);
            });
        """
        changed_state = machine.transition(machine.initial_state, 'EXTERNAL')
        assert changed_state.changed == True , pytest_func_docstring_summary(request)

class TestState_transitions:
    """ 
    describe('.transitions', () => {
    1 - should have no transitions for the initial state
    2 - should have transitions for the sent event
    3 - should have condition in the transition
    """
    initial_state  = machine.initial_state

    def test_state_transitions_1(self,request):
        """ 1 - should have no transitions for the initial state

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

            it('should have no transitions for the initial state', () => {
              expect(initialState.transitions).toHaveLength(0);
            });

        """
        assert len(self.initial_state.transitions) == 0, pytest_func_docstring_summary(request)

    def test_state_transitions_2(self,request):
        """ 2 - should have transitions for the sent event

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

            it('should have transitions for the sent event', () => {
              expect(
                machine.transition(initialState, 'TO_TWO').transitions
              ).toContainEqual(expect.objectContaining({ eventType: 'TO_TWO' }));
            });
        """
        # xstate_python_config['id']="test_states" # TODO REMOVE ME after debug
        # new_state_transitions = machine.transition(self.initial_state, 'TO_TWO').transitions
        initial_state = machine.initial_state
        new_state = machine.transition(initial_state, 'TO_TWO')
        new_state_transitions = new_state.transitions
    
        # TODO WIP 21w38 not sure if events are supported 
        assert  (
          new_state_transitions != set()
          and all([transition.event=='TO_TWO' for transition in new_state_transitions ])
        ), pytest_func_docstring_summary(request)

    def test_state_transitions_3(self,request):
        """ 3 - should have condition in the transition

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

            it('should have condition in the transition', () => {
              expect(
                machine.transition(initialState, 'TO_TWO_MAYBE').transitions
              ).toContainEqual(
                expect.objectContaining({
                  eventType: 'TO_TWO_MAYBE',
                  cond: expect.objectContaining({ name: 'maybe' })
        """

        new_state_transitions = machine.transition(self.initial_state, 'TO_TWO_MAYBE').transitions
        assert  (new_state_transitions != [] 
            and "'eventType': 'TO_TWO_MAYBE'" in repr(new_state_transitions)
            and "cond" in repr(new_state_transitions)
            and "{ name: 'maybe' }" in repr(new_state_transitions)
        ), pytest_func_docstring_summary(request)

class TestState_State_Protoypes:
    """ Test: describe('State.prototype.matches
        
    """
    initial_state  = machine.initial_state
    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_prototype_matches(self,request):
        """ 1 - should keep reference to state instance after destructuring

      ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts        
            it('should keep reference to state instance after destructuring', () => {
              const { initialState } = machine;
              const { matches } = initialState;
              expect(matches('one')).toBe(true);
            });
        """
        assert (
            'IMPLEMENTED'=='NOT YET'
        ), '1 - should keep reference to state instance after destructuring'

class TestState_State_Protoypes_To_String:
    """ Test: describe('State.prototype.toStrings'
    * 1 - should return all state paths as strings'
    * 2 - should respect `delimiter` option for deeply nested states
    * 3 - should keep reference to state instance after destructuring
    """
    def test_state_prototype_to_strings_1(self,request):
      """ 1 - should return all state paths as strings

      ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

          it('should return all state paths as strings', () => {
            const twoState = machine.transition('one', 'TO_TWO');
            expect(twoState.toStrings()).toEqual(['two', 'two.deep', 'two.deep.foo']);
          });
      """
      two_state = machine.transition('one', 'TO_TWO')
      assert (
          repr(two_state) == "<State {'value': {'two': {'deep': 'foo'}}, 'context': {}, 'actions': []}>" 
          and str(two_state) == repr(['two', 'two.deep', 'two.deep.foo'])
      ), pytest_func_docstring_summary(request)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_prototype_to_strings_2(self,request):
      """ 2 - should respect `delimiter` option for deeply nested states'

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

          it('should respect `delimiter` option for deeply nested states', () => {
            const twoState = machine.transition('one', 'TO_TWO');
            expect(twoState.toStrings(undefined, ':')).toEqual([
              'two',
              'two:deep',
              'two:deep:foo'
            ]);
      """
      two_state = machine.transition('one', 'TO_TWO')
      assert (
          'IMPLEMENTED'=='NOT YET - possibly requires a formatter'
      ),pytest_func_docstring_summary(request)

    def test_state_prototype_to_strings_3(self,request):
      """ 3 - should keep reference to state instance after destructuring

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts

          it('should keep reference to state instance after destructuring', () => {
            const { initialState } = machine;
            const { toStrings } = initialState;

            expect(toStrings()).toEqual(['one']);
      """

      initial_state= machine.initial_state
      #       const { toStrings } = initialState;
      assert (
          repr(initial_state) == "<State {'value': 'one', 'context': {}, 'actions': []}>"
          and str(initial_state) == repr(['one'])
      ), pytest_func_docstring_summary(request)


class TestState_State_Done:
    """ Test: describe('.done', 

        1 - should keep reference to state instance after destructuring
        2 - should show that a machine has reached its final state

    """
    initial_state  = machine.initial_state

    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_done_1(self,request):
        """ 1 - should keep reference to state instance after destructuring

      ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts        
          it('should show that a machine has not reached its final state', () => {
            expect(machine.initialState.done).toBeFalsy();
          });
        """
        assert (
            'IMPLEMENTED'=='NOT YET'
        ), pytest_func_docstring_summary(request)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_done_2(self,request):
        """ 2 - should show that a machine has reached its final state

        ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts        
          it('should show that a machine has reached its final state', () => {
            expect(machine.transition(undefined, 'TO_FINAL').done).toBeTruthy();
          });
        """
        assert (
            'IMPLEMENTED'=='NOT YET'
        ), pytest_func_docstring_summary(request)

class TestState_State_Can:
    """ Test: describe('.can',

    .can is not yet implemented in python
        1 - ???????????????????
        ....
        n -- ?????????????????
    """
    initial_state  = machine.initial_state
    
    @pytest.mark.skip(reason="Not implemented yet")
    def test_state_can_1(self,request):
        """ 1 - should keep reference to state instance after destructuring

      ref: https://github.com/statelyai/xstate/blob/main/packages/core/test/state.test.ts        
        describe('.can', () => {
          it('should return true for a simple event that results in a transition to a different state', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    NEXT: 'b'
                  }
                },
                b: {}
              }
            });

            expect(machine.initialState.can('NEXT')).toBe(true);
          });

          it('should return true for an event object that results in a transition to a different state', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    NEXT: 'b'
                  }
                },
                b: {}
              }
            });

            expect(machine.initialState.can({ type: 'NEXT' })).toBe(true);
          });

          it('should return true for an event object that results in a new action', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    NEXT: {
                      actions: 'newAction'
                    }
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'NEXT' })).toBe(true);
          });

          it('should return true for an event object that results in a context change', () => {
            const machine = createMachine({
              initial: 'a',
              context: { count: 0 },
              states: {
                a: {
                  on: {
                    NEXT: {
                      actions: assign({ count: 1 })
                    }
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'NEXT' })).toBe(true);
          });

          it('should return false for an external self-transition without actions', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    EV: 'a'
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'EV' })).toBe(false);
          });

          it('should return true for an external self-transition with reentry action', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  entry: () => {},
                  on: {
                    EV: 'a'
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'EV' })).toBe(true);
          });

          it('should return true for an external self-transition with transition action', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    EV: {
                      target: 'a',
                      actions: () => {}
                    }
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'EV' })).toBe(true);
          });

          it('should return true for a targetless transition with actions', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    EV: {
                      actions: () => {}
                    }
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'EV' })).toBe(true);
          });

          it('should return false for a forbidden transition', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    EV: undefined
                  }
                }
              }
            });

            expect(machine.initialState.can({ type: 'EV' })).toBe(false);
          });

          it('should return false for an unknown event', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    NEXT: 'b'
                  }
                },
                b: {}
              }
            });

            expect(machine.initialState.can({ type: 'UNKNOWN' })).toBe(false);
          });

          it('should return true when a guarded transition allows the transition', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    CHECK: {
                      target: 'b',
                      cond: () => true
                    }
                  }
                },
                b: {}
              }
            });

            expect(
              machine.initialState.can({
                type: 'CHECK'
              })
            ).toBe(true);
          });

          it('should return false when a guarded transition disallows the transition', () => {
            const machine = createMachine({
              initial: 'a',
              states: {
                a: {
                  on: {
                    CHECK: {
                      target: 'b',
                      cond: () => false
                    }
                  }
                },
                b: {}
              }
            });

            expect(
              machine.initialState.can({
                type: 'CHECK'
              })
            ).toBe(false);
          });

          it('should not spawn actors when determining if an event is accepted', () => {
            let spawned = false;
            const machine = createMachine({
              context: {},
              initial: 'a',
              states: {
                a: {
                  on: {
                    SPAWN: {
                      actions: assign(() => ({
                        ref: spawn(() => {
                          spawned = true;
                        })
                      }))
                    }
                  }
                },
                b: {}
              }
            });

            const service = interpret(machine).start();
            service.state.can('SPAWN');
            expect(spawned).toBe(false);
          });

          it('should return false for states created without a machine', () => {
            const state = State.from('test');

            expect(state.can({ type: 'ANY_EVENT' })).toEqual(false);
          });

          it('should allow errors to propagate', () => {
            const machine = createMachine({
              context: {},
              on: {
                DO_SOMETHING_BAD: {
                  actions: assign(() => {
                    throw new Error('expected error');
                  })
                }
              }
            });

            expect(() => {
              const { initialState } = machine;

              initialState.can('DO_SOMETHING_BAD');
            }).toThrowError(/expected error/);
          });
        });
      });
        """
        assert (
            'IMPLEMENTED'=='NOT YET'
        ), pytest_func_docstring_summary(request)




