"""Tests for  history

Based on : xstate/packages/core/test/history.test.ts
These tests test history 

These tests use either machines coded as python `dict` 
or accept strings representing xstate javascript/typescript which are
then converted to a python `dict` by the module `js2py`

The following tests exist
    * xxx - returns ....
    * xxx - the ....
"""
import pytest


from .utils_for_tests import JSstyleTest, pytest_func_docstring_summary

from xstate.algorithm import get_configuration_from_js

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


history_machine_xstate_js_config = """{
    key: 'history',
    initial: 'off',
    states: {
      off: {
        on: { POWER: 'on.hist', H_POWER: 'on.H' }
      },
      on: {
        initial: 'first',
        states: {
          first: {
            on: { SWITCH: 'second' }
          },
          second: {
            on: { SWITCH: 'third' }
          },
          third: {},
          H: {
            type: 'history'
          },
          hist: {
            type: 'history',
            history: 'shallow'
          }
        },
        on: {
          POWER: 'off',
          H_POWER: 'off'
        }
      }
    }
  }"""
xstate_python_config = get_configuration_from_js(history_machine_xstate_js_config)

# Example of tweaking model for test development
# del xstate_python_config['states']['one']['on']['INTERNAL']['actions']

# xstate_python_config['states']['one']['on']['INTERNAL']['actions']=['doSomething']
# del xstate_python_config['states']['one']['entry']
# xstate_python_config['states']['one']['entry'] =['enter']
history_machine = Machine(xstate_python_config)


"""
import { Machine, createMachine, interpret } from '../src/index';

describe('history states', () => {
  const historyMachine = createMachine({
    key: 'history',
    initial: 'off',
    states: {
      off: {
        on: { POWER: 'on.hist', H_POWER: 'on.H' }
      },
      on: {
        initial: 'first',
        states: {
          first: {
            on: { SWITCH: 'second' }
          },
          second: {
            on: { SWITCH: 'third' }
          },
          third: {},
          H: {
            type: 'history'
          },
          hist: {
            type: 'history',
            history: 'shallow'
          }
        },
        on: {
          POWER: 'off',
          H_POWER: 'off'
        }
      }
    }
  });
"""


class TestHistoryInitial:
    """An initial set of unit tests of History capability"""

    def test_history_should_go_to_the_most_recently_visited_state(self, request):
        """should go to the most recently visited state"""
        # it('should go to the most recently visited state', () => {
        def test_procedure():
            #   const onSecondState = historyMachine.transition('on', 'SWITCH');
            #   const offState = historyMachine.transition(onSecondState, 'POWER');
            on_second_state = history_machine.transition("on", "SWITCH")
            off_state = history_machine.transition(on_second_state, "POWER")
            #   expect(historyMachine.transition(offState, 'POWER').value).toEqual({
            return history_machine.transition(off_state, "POWER").value

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure()
        ).toEqual(
            #   expect(historyMachine.transition(offState, 'POWER').value).toEqual({
            #     on: 'second'
            {"on": "second"}
        )
        # """

        #   it('should go to the most recently visited state', () => {
        #     const onSecondState = historyMachine.transition('on', 'SWITCH');
        #     const offState = historyMachine.transition(onSecondState, 'POWER');

        #     expect(historyMachine.transition(offState, 'POWER').value).toEqual({
        #       on: 'second'
        #     });
        #   });
        # """

    def test_history_should_go_to_the_most_recently_visited_state_explicit(
        self, request
    ):
        """should go to the most recently visited state (explicit)"""

        def test_procedure():
            on_second_state = history_machine.transition("on", "SWITCH")
            off_state = history_machine.transition(on_second_state, "H_POWER")
            return history_machine.transition(off_state, "H_POWER").value

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure()
        ).toEqual(
            #   expect(historyMachine.transition(offState, 'POWER').value).toEqual({
            #     on: 'second'
            {"on": "second"}
        )

        # it('should go to the most recently visited state (explicit)', () => {
        #   const onSecondState = historyMachine.transition('on', 'SWITCH');
        #   const offState = historyMachine.transition(onSecondState, 'H_POWER');

        #   expect(historyMachine.transition(offState, 'H_POWER').value).toEqual({
        #     on: 'second'
        #   });
        # });

    def test_history_should_go_to_the_initial_state_when_no_history_present(
        self, request
    ):
        """should go to the initial state when no history present"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            history_machine.transition("off", "POWER").value
        ).toEqual({"on": "first"})

        # it('should go to the initial state when no history present', () => {
        #   expect(historyMachine.transition('off', 'POWER').value).toEqual({
        #     on: 'first'
        #   });
        # });

    def test_history_should_go_to_the_initial_state_when_no_history_present_explicit(
        self, request
    ):
        """should go to the initial state when no history present (explicit)"""
        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            history_machine.transition("off", "H_POWER").value
        ).toEqual({"on": "first"})

        # it('should go to the initial state when no history present (explicit)', () => {
        #   expect(historyMachine.transition('off', 'H_POWER').value).toEqual({
        #     on: 'first'
        #   });
        # });

    def test_history_should_dispose_of_previous_histories(self, request):
        """should dispose of previous histories"""

        def test_procedure():

            onSecondState = history_machine.transition("on", "SWITCH")
            offState = history_machine.transition(onSecondState, "H_POWER")
            onState = history_machine.transition(offState, "H_POWER")
            nextState = history_machine.transition(onState, "H_POWER")
            test_result = nextState.history.history is None
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure()
        ).toEqual(True)

    # it('should dispose of previous histories', () => {
    #   const onSecondState = historyMachine.transition('on', 'SWITCH');
    #   const offState = historyMachine.transition(onSecondState, 'H_POWER');
    #   const onState = historyMachine.transition(offState, 'H_POWER');
    #   const nextState = historyMachine.transition(onState, 'H_POWER');
    #   expect(nextState.history!.history).not.toBeDefined();
    # });
    @pytest.mark.skip(reason="Eventless Transition `Always`, not yet implemented")
    def test_history_should_go_to_the_most_recently_visited_state_by_a_transient_transition_non_interpreter(
        self, request
    ):
        """should go to the most recently visited state by a transient transition

        The on event `DESTROY` the state `destroy` should automatically ie `always` proceed to `idle.absent`
        """

        def test_procedure():
            machine = Machine(
                """
            {
              initial: 'idle',
              states: {
                idle: {
                  id: 'idle',
                  initial: 'absent',
                  states: {
                    absent: {
                      on: {
                        DEPLOY: '#deploy'
                      }
                    },
                    present: {
                      on: {
                        DEPLOY: '#deploy',
                        DESTROY: '#destroy'
                      }
                    },
                    hist: {
                      type: 'history'
                    }
                  }
                },
                deploy: {
                  id: 'deploy',
                  on: {
                    SUCCESS: 'idle.present',
                    FAILURE: 'idle.hist'
                  }
                },
                destroy: {
                  id: 'destroy',
                  always: [{ target: 'idle.absent' }]
                }
              }
            }          
            """
            )
            initial_state = machine.initial_state
            # service.send('DEPLOY');
            next_state = machine.transition(initial_state, "DEPLOY")
            # service.send('SUCCESS');
            next_state = machine.transition(next_state, "SUCCESS")
            # service.send('DESTROY');
            next_state = machine.transition(next_state, "DESTROY")
            # service.send('DEPLOY');
            next_state = machine.transition(next_state, "DEPLOY")
            # service.send('FAILURE');
            next_state = machine.transition(next_state, "FAILURE")
            test_result = next_state.state.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure()
        ).toEqual({"idle": "absent"})

    @pytest.mark.skip(reason="interpreter, not yet implemented")
    def test_history_should_go_to_the_most_recently_visited_state_by_a_transient_transition(
        self, request
    ):
        """should go to the most recently visited state by a transient transition"""

        def test_procedure():
            machine = Machine(
                """
            {
              initial: 'idle',
              states: {
                idle: {
                  id: 'idle',
                  initial: 'absent',
                  states: {
                    absent: {
                      on: {
                        DEPLOY: '#deploy'
                      }
                    },
                    present: {
                      on: {
                        DEPLOY: '#deploy',
                        DESTROY: '#destroy'
                      }
                    },
                    hist: {
                      type: 'history'
                    }
                  }
                },
                deploy: {
                  id: 'deploy',
                  on: {
                    SUCCESS: 'idle.present',
                    FAILURE: 'idle.hist'
                  }
                },
                destroy: {
                  id: 'destroy',
                  always: [{ target: 'idle.absent' }]
                }
              }
            }          
            """
            )
            service = interpret(machine).start()

            service.send("DEPLOY")
            service.send("SUCCESS")
            service.send("DESTROY")
            service.send("DEPLOY")
            service.send("FAILURE")
            test_result = service.state.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure()
        ).toEqual({"idle": "absent"})
        # XStateJS
        #   it('should go to the most recently visited state by a transient transition', () => {
        """       
        #     const machine = createMachine({
                      #       initial: 'idle',
                      #       states: {
                      #         idle: {
                      #           id: 'idle',
                      #           initial: 'absent',
                      #           states: {
                      #             absent: {
                      #               on: {
                      #                 DEPLOY: '#deploy'
                      #               }
                      #             },
                      #             present: {
                      #               on: {
                      #                 DEPLOY: '#deploy',
                      #                 DESTROY: '#destroy'
                      #               }
                      #             },
                      #             hist: {
                      #               type: 'history'
                      #             }
                      #           }
                      #         },
                      #         deploy: {
                      #           id: 'deploy',
                      #           on: {
                      #             SUCCESS: 'idle.present',
                      #             FAILURE: 'idle.hist'
                      #           }
                      #         },
                      #         destroy: {
                      #           id: 'destroy',
                      #           always: [{ target: 'idle.absent' }]
                      #         }
                      #       }
                      #     });

                    #     const service = interpret(machine).start();

                    #     service.send('DEPLOY');
                    #     service.send('SUCCESS');
                    #     service.send('DESTROY');
                    #     service.send('DEPLOY');
                    #     service.send('FAILURE');

                    #     expect(service.state.value).toEqual({ idle: 'absent' });
                    #   });
                    # });
        """


class TestHistoryDeepStates:
    """A set of unit tests of Deep History States"""

    history_machine = Machine(
        """
        { 
          key: 'history',
          initial: 'off',
          states: {
            off: {
              on: {
                POWER: 'on.history',
                DEEP_POWER: 'on.deepHistory'
              }
            },
            on: {
              initial: 'first',
              states: {
                first: {
                  on: { SWITCH: 'second' }
                },
                second: {
                  initial: 'A',
                  states: {
                    A: {
                      on: { INNER: 'B' }
                    },
                    B: {
                      initial: 'P',
                      states: {
                        P: {
                          on: { INNER: 'Q' }
                        },
                        Q: {}
                      }
                    }
                  }
                },
                history: { history: 'shallow' },
                deepHistory: {type: 'history',
                  history: 'deep'
                }
              },
              on: {
                POWER: 'off'
              }
            }
          }
        }        
      """
    )
    # XStateJS
    # describe('deep history states', () => {
    #   const historyMachine = Machine({
    #     key: 'history',
    #     initial: 'off',
    #     states: {
    #       off: {
    #         on: {
    #           POWER: 'on.history',
    #           DEEP_POWER: 'on.deepHistory'
    #         }
    #       },
    #       on: {
    #         initial: 'first',
    #         states: {
    #           first: {
    #             on: { SWITCH: 'second' }
    #           },
    #           second: {
    #             initial: 'A',
    #             states: {
    #               A: {
    #                 on: { INNER: 'B' }
    #               },
    #               B: {
    #                 initial: 'P',
    #                 states: {
    #                   P: {
    #                     on: { INNER: 'Q' }
    #                   },
    #                   Q: {}
    #                 }
    #               }
    #             }
    #           },
    #           history: { history: 'shallow' },
    #           deepHistory: {
    #             history: 'deep'
    #           }
    #         },
    #         on: {
    #           POWER: 'off'
    #         }
    #       }
    #     }
    #   });


class TestHistoryDeepStatesHistory:
    # on.first -> on.second.A
    state2A = TestHistoryDeepStates().history_machine.transition(
        # { 'on': 'first' },
        "on.first",
        "SWITCH",
    )
    # on.second.A -> on.second.B.P
    state2BP = TestHistoryDeepStates().history_machine.transition(state2A, "INNER")
    # on.second.B.P -> on.second.B.Q
    state2BQ = TestHistoryDeepStates().history_machine.transition(state2BP, "INNER")

    assert state2BP.history_value.states["on"].current == {
        "second": {"B": "P"}
    }, "state2BP should stay at 2BP and not be affected by 2BP->2BQ"
    # XStateJS
    #   describe('history', () => {
    #   // on.first -> on.second.A
    #   const state2A = historyMachine.transition({ on: 'first' }, 'SWITCH');
    #   // on.second.A -> on.second.B.P
    #   const state2BP = historyMachine.transition(state2A, 'INNER');
    #   // on.second.B.P -> on.second.B.Q
    #   const state2BQ = historyMachine.transition(state2BP, 'INNER');

    # @pytest.mark.skip(reason="")
    def test_history_should_go_to_the_shallow_history(self, request):
        """should go to the shallow history"""

        def test_procedure(self):
            # on.second.B.P -> off
            stateOff = TestHistoryDeepStates.history_machine.transition(
                self.state2BP, "POWER"
            )
            test_result = TestHistoryDeepStates.history_machine.transition(
                stateOff, "POWER"
            ).value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"second": "A"}})
        # XStateJS
        # it('should go to the shallow history', () => {
        #   // on.second.B.P -> off
        #   const stateOff = historyMachine.transition(state2BP, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'POWER').value).toEqual({
        #     on: { second: 'A' }

    # @pytest.mark.skip(reason="")
    def test_history_should_go_to_the_deep_history_explicit(self, request):
        """should go to the deep history (explicit)"""

        def test_procedure(self):
            # on.second.B.P -> off
            stateOff = TestHistoryDeepStates.history_machine.transition(
                self.state2BP, "POWER"
            )
            test_result = TestHistoryDeepStates.history_machine.transition(
                stateOff, "DEEP_POWER"
            ).value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"second": {"B": "P"}}})
        # XStateJS
        # it('should go to the deep history (explicit)', () => {
        #   // on.second.B.P -> off
        #   const stateOff = historyMachine.transition(state2BP, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'DEEP_POWER').value).toEqual({
        #     on: { second: { B: 'P' } }

    # @pytest.mark.skip(reason="")
    def test_history_should_go_to_the_deepest_history(self, request):
        """should go to the deepest history"""

        def test_procedure(self):
            # on.second.B.Q -> off
            stateOff = TestHistoryDeepStates.history_machine.transition(
                self.state2BQ, "POWER"
            )
            test_result = TestHistoryDeepStates.history_machine.transition(
                stateOff, "DEEP_POWER"
            ).value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"second": {"B": "Q"}}})
        # XStateJS
        # it('should go to the deepest history', () => {
        #   // on.second.B.Q -> off
        #   const stateOff = historyMachine.transition(state2BQ, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'DEEP_POWER').value).toEqual({
        #     on: { second: { B: 'Q' } }


class TestParallelHistoryStates:
    """A set of unit tests for Parallel History States"""

    history_machine = Machine(
        """
        { 
          key: 'parallelhistory',
          initial: 'off',
          states: {
            off: {
              on: {
                SWITCH: 'on', /* go to the initial states */
                POWER: 'on.hist',
                DEEP_POWER: 'on.deepHistory',
                PARALLEL_HISTORY: [{ target: ['on.A.hist', 'on.K.hist'] }],
                PARALLEL_SOME_HISTORY: [{ target: ['on.A.C', 'on.K.hist'] }],
                PARALLEL_DEEP_HISTORY: [
                  { target: ['on.A.deepHistory', 'on.K.deepHistory'] }
                ]
              }
            },
            on: {
              type: 'parallel',
              states: {
                A: {
                  initial: 'B',
                  states: {
                    B: {
                      on: { INNER_A: 'C' }
                    },
                    C: {
                      initial: 'D',
                      states: {
                        D: {
                          on: { INNER_A: 'E' }
                        },
                        E: {}
                      }
                    },
                    hist: { history: true },
                    deepHistory: {
                      history: 'deep'
                    }
                  }
                },
                K: {
                  initial: 'L',
                  states: {
                    L: {
                      on: { INNER_K: 'M' }
                    },
                    M: {
                      initial: 'N',
                      states: {
                        N: {
                          on: { INNER_K: 'O' }
                        },
                        O: {}
                      }
                    },
                    hist: { history: true },
                    deepHistory: {
                      history: 'deep'
                    }
                  }
                },
                hist: {
                  history: true
                },
                shallowHistory: {
                  history: 'shallow'
                },
                deepHistory: {
                  history: 'deep'
                }
              },
              on: {
                POWER: 'off'
              }
            }
          }
        }        
      """
    )
    # XStateJS
    # describe('parallel history states', () => {
    #   const historyMachine = Machine({
    #     key: 'parallelhistory',
    #     initial: 'off',
    #     states: {
    #       off: {
    #         on: {
    #           SWITCH: 'on', // go to the initial states
    #           POWER: 'on.hist',
    #           DEEP_POWER: 'on.deepHistory',
    #           PARALLEL_HISTORY: [{ target: ['on.A.hist', 'on.K.hist'] }],
    #           PARALLEL_SOME_HISTORY: [{ target: ['on.A.C', 'on.K.hist'] }],
    #           PARALLEL_DEEP_HISTORY: [
    #             { target: ['on.A.deepHistory', 'on.K.deepHistory'] }
    #           ]
    #         }
    #       },
    #       on: {
    #         #type: 'parallel',
    #         states: {
    #           A: {
    #             initial: 'B',
    #             states: {
    #               B: {
    #                 on: { INNER_A: 'C' }
    #               },
    #               C: {
    #                 initial: 'D',
    #                 states: {
    #                   D: {
    #                     on: { INNER_A: 'E' }
    #                   },
    #                   E: {}
    #                 }
    #               },
    #               hist: { history: true },
    #               deepHistory: {
    #                 history: 'deep'
    #               }
    #             }
    #           },
    #           K: {
    #             initial: 'L',
    #             states: {
    #               L: {
    #                 on: { INNER_K: 'M' }
    #               },
    #               M: {
    #                 initial: 'N',
    #                 states: {
    #                   N: {
    #                     on: { INNER_K: 'O' }
    #                   },
    #                   O: {}
    #                 }
    #               },
    #               hist: { history: true },
    #               deepHistory: {
    #                 history: 'deep'
    #               }
    #             }
    #           },
    #           hist: {
    #             history: true
    #           },
    #           shallowHistory: {
    #             history: 'shallow'
    #           },
    #           deepHistory: {
    #             history: 'deep'
    #           }
    #         },
    #         on: {
    #           POWER: 'off'
    #         }
    #       }
    #     }
    #   });


class TestParallelHistoryStatesHistory:

    # on.first -> on.second.A
    stateABKL = TestParallelHistoryStates().history_machine.transition(
        TestParallelHistoryStates().history_machine.initial_state, "SWITCH"
    )
    # INNER_A twice
    stateACDKL = TestParallelHistoryStates().history_machine.transition(
        stateABKL, "INNER_A"
    )
    stateACEKL = TestParallelHistoryStates().history_machine.transition(
        stateACDKL, "INNER_A"
    )

    #  INNER_K twice
    stateACEKMN = TestParallelHistoryStates().history_machine.transition(
        stateACEKL, "INNER_K"
    )
    stateACEKMO = TestParallelHistoryStates().history_machine.transition(
        stateACEKMN, "INNER_K"
    )

    # XStateJS
    # describe('history', () => {
    #   // on.first -> on.second.A
    #   const stateABKL = historyMachine.transition(
    #     historyMachine.initialState,
    #     'SWITCH'
    #   );
    #   // INNER_A twice
    #   const stateACDKL = historyMachine.transition(stateABKL, 'INNER_A');
    #   const stateACEKL = historyMachine.transition(stateACDKL, 'INNER_A');

    #   // INNER_K twice
    #   const stateACEKMN = historyMachine.transition(stateACEKL, 'INNER_K');
    #   const stateACEKMO = historyMachine.transition(stateACEKMN, 'INNER_K');

    # @pytest.mark.skip(reason="")
    def test_should_ignore_parallel_state_history(self, request):
        """should ignore parallel state history"""

        def test_procedure(self):
            # on.second.B.P -> off

            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACDKL, "POWER"
            )
            test_result = (
                TestParallelHistoryStates()
                .history_machine.transition(stateOff, "POWER")
                .value
            )

            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": "B", "K": "L"}})
        # XStateJS
        # it('should ignore parallel state history', () => {
        #   const stateOff = historyMachine.transition(stateACDKL, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'POWER').value).toEqual({
        #     on: { A: 'B', K: 'L' }
        #   });
        # });

    # @pytest.mark.skip(reason="")
    def test_should_remember_first_level_state_history(self, request):
        """should remember first level state history"""

        def test_procedure(self):
            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACDKL, "POWER"
            )
            transition_result = TestParallelHistoryStates().history_machine.transition(
                stateOff, "DEEP_POWER"
            )
            test_result = transition_result.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": {"C": "D"}, "K": "L"}})
        # XStateJS
        # it('should remember first level state history', () => {
        #   const stateOff = historyMachine.transition(stateACDKL, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'DEEP_POWER').value).toEqual({
        #     on: { A: { C: 'D' }, K: 'L' }
        #   });
        # });

    # @pytest.mark.skip(reason="")
    def test_should_re_enter_each_regions_of_parallel_state_correctly(self, request):
        """should re-enter each regions of parallel state correctly"""

        def test_procedure(self):
            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACEKMO, "POWER"
            )
            transition_result = TestParallelHistoryStates().history_machine.transition(
                stateOff, "DEEP_POWER"
            )
            test_result = transition_result.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": {"C": "E"}, "K": {"M": "O"}}})
        # XStateJS
        # it('should re-enter each regions of parallel state correctly', () => {
        #   const stateOff = historyMachine.transition(stateACEKMO, 'POWER');
        #   expect(historyMachine.transition(stateOff, 'DEEP_POWER').value).toEqual({
        #     on: { A: { C: 'E' }, K: { M: 'O' } }
        #   });
        # });

    def test_should_re_enter_multiple_history_states(self, request):
        """should re-enter multiple history states"""

        def test_procedure(self):
            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACEKMO, "POWER"
            )
            transition_result = TestParallelHistoryStates().history_machine.transition(
                stateOff, "PARALLEL_HISTORY"
            )
            test_result = transition_result.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": {"C": "D"}, "K": {"M": "N"}}})
        # XStateJS
        # it('should re-enter multiple history states', () => {
        #   const stateOff = historyMachine.transition(stateACEKMO, 'POWER');
        #   expect(
        #     historyMachine.transition(stateOff, 'PARALLEL_HISTORY').value
        #   ).toEqual({
        #     on: { A: { C: 'D' }, K: { M: 'N' } }
        #   });
        # });

    def test_should_re_enter_a_parallel_with_partial_history(self, request):
        """should re-enter a parallel with partial history"""

        def test_procedure(self):
            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACEKMO, "POWER"
            )
            transition_result = TestParallelHistoryStates().history_machine.transition(
                stateOff, "PARALLEL_SOME_HISTORY"
            )
            test_result = transition_result.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": {"C": "D"}, "K": {"M": "N"}}})
        # XStateJS
        # it('should re-enter a parallel with partial history', () => {
        #   const stateOff = historyMachine.transition(stateACEKMO, 'POWER');
        #   expect(
        #     historyMachine.transition(stateOff, 'PARALLEL_SOME_HISTORY').value
        #   ).toEqual({
        #     on: { A: { C: 'D' }, K: { M: 'N' } }
        #   });
        # });

    def test_should_re_enter_a_parallel_with_full_history(self, request):
        """should re-enter a parallel with full history"""

        def test_procedure(self):
            stateOff = TestParallelHistoryStates().history_machine.transition(
                self.stateACEKMO, "POWER"
            )
            transition_result = TestParallelHistoryStates().history_machine.transition(
                stateOff, "PARALLEL_DEEP_HISTORY"
            )
            test_result = transition_result.value
            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"on": {"A": {"C": "E"}, "K": {"M": "O"}}})
        # XStateJS
        # it('should re-enter a parallel with full history', () => {
        #   const stateOff = historyMachine.transition(stateACEKMO, 'POWER');
        #   expect(
        #     historyMachine.transition(stateOff, 'PARALLEL_DEEP_HISTORY').value
        #   ).toEqual({
        #     on: { A: { C: 'E' }, K: { M: 'O' } }
        #   });
        # });


class TestTransientHistory:

    transientMachine = Machine(
        # TODO: uncomment `always` when implemented
        """
    {
      initial: 'A',
      states: {
        A: {
          on: { EVENT: 'B' }
        },
        B: {
          /* eventless transition 
          always: 'C'*/
        },
        C: {}
      }
    }
    """
    )

    # const transientMachine = Machine({
    #   initial: 'A',
    #   states: {
    #     A: {
    #       on: { EVENT: 'B' }
    #     },
    #     B: {
    #       // eventless transition
    #       always: 'C'
    #     },
    #     C: {}
    #   }
    # });

    @pytest.mark.skip(reason="Transient `always` not implemented yet")
    def test_should_have_history_on_transient_transitions(self, request):
        """should have history on transient transitions"""

        def test_procedure(self):
            nextState = self.transientMachine.transition("A", "EVENT")
            test_result = nextState.value == "C" and nextState.history is not None

            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual(True)
        # XStateJS
        #   it('should have history on transient transitions', () => {
        #     const nextState = transientMachine.transition('A', 'EVENT');
        #     expect(nextState.value).toEqual('C');
        #     expect(nextState.history).toBeDefined();
        #   });
        # });


class TestInternalTransitionWithHistory:

    machine = Machine(
        """
      {
        key: 'test',
        initial: 'first',
        states: {
          first: {
            initial: 'foo',
            states: {
              foo: {}
            },
            on: {
              NEXT: 'second.other'
            }
          },
          second: {
            initial: 'nested',
            states: {
              nested: {},
              other: {},
              hist: {
                history: true
              }
            },
            on: {
              NEXT: [
                {
                  target: '.hist'
                }
              ]
            }
          }
        }
      }
    """
    )

    # @pytest.mark.skip(reason="")
    def test_should_transition_internally_to_the_most_recently_visited_state(
        self, request
    ):
        """should transition internally to the most recently visited state"""

        def test_procedure(self):
            state2 = self.machine.transition(self.machine.root.initial, "NEXT")
            state3 = self.machine.transition(state2, "NEXT")
            test_result = state3.value

            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"second": "other"})
        # XStateJS
        #   it('should transition internally to the most recently visited state', () => {
        #     // {
        #     //   $current: 'first',
        #     //   first: undefined,
        #     //   second: {
        #     //     $current: 'nested',
        #     //     nested: undefined,
        #     //     other: undefined
        #     //   }
        #     // }
        #     const state2 = machine.transition(machine.initialState, 'NEXT');
        #     // {
        #     //   $current: 'second',
        #     //   first: undefined,
        #     //   second: {
        #     //     $current: 'other',
        #     //     nested: undefined,
        #     //     other: undefined
        #     //   }
        #     // }
        #     const state3 = machine.transition(state2, 'NEXT');
        #     // {
        #     //   $current: 'second',
        #     //   first: undefined,
        #     //   second: {
        #     //     $current: 'other',
        #     //     nested: undefined,
        #     //     other: undefined
        #     //   }
        #     // }

        #     expect(state3.value).toEqual({ second: 'other' });
        #   });
        # });


class TestMultistageHistoryStates:

    pcWithTurboButtonMachine = Machine(
        """
      {
        key: 'pc-with-turbo-button',
        initial: 'off',
        states: {
          off: {
            on: { POWER: 'starting' }
          },
          starting: {
            on: { STARTED: 'running.H' }
          },
          running: {
            initial: 'normal',
            states: {
              normal: {
                on: { SWITCH_TURBO: 'turbo' }
              },
              turbo: {
                on: { SWITCH_TURBO: 'normal' }
              },
              H: {
                history: true
              }
            },
            on: {
              POWER: 'off'
            }
          }
        }
      }
    """
    )

    # @pytest.mark.skip(reason="")
    def test_should_go_to_the_most_recently_visited_state(self, request):
        """should go to the most recently visited state"""

        def test_procedure(self):
            onTurboState = self.pcWithTurboButtonMachine.transition(
                "running", "SWITCH_TURBO"
            )
            offState = self.pcWithTurboButtonMachine.transition(onTurboState, "POWER")
            loadingState = self.pcWithTurboButtonMachine.transition(offState, "POWER")
            finalState = self.pcWithTurboButtonMachine.transition(
                loadingState, "STARTED"
            )
            test_result = finalState.value

            return test_result

        test = JSstyleTest()
        test.it(pytest_func_docstring_summary(request)).expect(
            test_procedure(self)
        ).toEqual({"running": "turbo"})
        # XStateJS
        #   it('should go to the most recently visited state', () => {
        #     const onTurboState = pcWithTurboButtonMachine.transition(
        #       'running',
        #       'SWITCH_TURBO'
        #     );
        #     const offState = pcWithTurboButtonMachine.transition(onTurboState, 'POWER');
        #     const loadingState = pcWithTurboButtonMachine.transition(offState, 'POWER');

        #     expect(
        #       pcWithTurboButtonMachine.transition(loadingState, 'STARTED').value
        #     ).toEqual({ running: 'turbo' });
        #   });
        # });
