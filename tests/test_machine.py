from xstate.machine import Machine

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {"on": {"TIMER": "yellow"}, "entry": [{"type": "enterGreen"}]},
            "yellow": {"on": {"TIMER": "red"}},
            "red": {
                "initial": "walk",
                "states": {
                    "walk": {"on": {"COUNTDOWN": "wait"}},
                    "wait": {"on": {"COUNTDOWN": "stop"}},
                    "stop": {"on": {"TIMEOUT": "timeout"}},
                    "timeout": {"type": "final"},
                },
                "onDone": "green",
            },
        },
    }
)


def test_machine():
    yellow_state = lights.transition(lights.initial_state, "TIMER")

    assert yellow_state.value == "yellow"

    red_state = lights.transition(yellow_state, "TIMER")

    assert red_state.value == {"red": "walk"}


def test_machine_initial_state():

    assert lights.initial_state.value == "green"


def test_final_state():
    red_stop_state = lights.state_from({"red": "stop"})

    red_timeout_state = lights.transition(red_stop_state, "TIMEOUT")

    assert red_timeout_state.value == "green"


fan = Machine(
    {
        "id": "fan",
        "initial": "fanOff",
        "states": {
            "fanOff": {
                "on": {
                    # "POWER": "#fan.fanOn.hist",
                    # "HIGH_POWER": "fanOn.highPowerHist",
                    # "POWER": "fanOn.first",
                    # "HIGH_POWER": "fanOn.third",
                    "POWER": "fanOn",
                    "HIGH_POWER": "fanOn",

                },
            },
            "fanOn": {
                "initial": "first",
                "states": {
                    "first": {"on": {"SWITCH": "second"}},
                    "second": {"on": {"SWITCH": "third"}},
                    "third": {},
                    # "hist": {"type": "history", "history": "shallow"},
                    # "highPowerHist": {"type": "history", "target": "third"},
                },
                "on": {"POWER": "fanOff"},
            },
        },
    }
)


def test_history_state():
    on_state = fan.transition(fan.initial_state, "POWER")

    assert on_state.value == {"fanOn": "first"}

    on_second_state = fan.transition(on_state, "SWITCH")

    assert on_second_state.value == {"fanOn": "second"}

    off_state = fan.transition(on_second_state, "POWER")

    assert off_state.value == "fanOff"

    on_second_state = fan.transition(off_state, "POWER")

    assert on_second_state.value == {"fanOn": "first"}


def test_top_level_final():
    final = Machine(
        {
            "id": "final",
            "initial": "start",
            "states": {
                "start": {"on": {"FINISH": "end"}},
                "end": {"type": "final"},
            },
        }
    )

    end_state = final.transition(final.initial_state, "FINISH")

    assert end_state.value == "end"
