# XState for Python

XState for Python - work in progress!

## How to use

```python

from xstate.machine import Machine

lights = Machine(
    {
        "id": "lights",
        "initial": "green",
        "states": {
            "green": {"on": {"TIMER": "yellow"},},
            "yellow": {"on": {"TIMER": "red"}},
            "red": {"on": {"TIMER": "green"}},
        },
    }
)

state = lights.initial_state # state.value is green

state = lights.transition(state, "TIMER") # state.value is yellow
state = lights.transition(state, "TIMER") # state.value is red
state = lights.transition(state, "TIMER") # state.value is green again
```

More advanced examples in [the "examples" folder](./examples)

## Testing

1. Run `python3.7 -m venv .venv` to create a virtual environment
2. Run `source .venv/bin/activate` to go into that virtual environment
3. Run `pip install -r requirements_dev.txt` to install all of the dependencies in `requirements.txt` (which includes `pytest`)
4. Run `npm i @scion-scxml/test-framework` to download scxml files
5. Run `pytest` to run the tests! 👩‍🔬

## SCXML

SCXML tests are ran from [the SCION Test Framework](./node_modules/@scion-scxml/test-framework/README.md) module.

## Related Projects

- [finite-state-machine](https://github.com/alysivji/finite-state-machine)
- [Sismic for Python](https://github.com/AlexandreDecan/sismic)
- [Miros](https://github.com/aleph2c/miros)
