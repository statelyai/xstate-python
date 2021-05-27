# XState for Python

XState for Python - work in progress!

## How to use

```python

from xstate import Machine

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

You can set up your development environment in two different ways. 

### Using [VSCode Remote Containers](https://code.visualstudio.com/docs/remote/containers)

Note this requires VSCode and the Remote Containers extension (which uses Docker containers)

1. [Open the folder in a container](https://code.visualstudio.com/docs/remote/containers#_quick-start-open-an-existing-folder-in-a-container). This will setup your environment with python (including python and pylance extensions), dependencies and download scxml tests.
1. Run `pytest` to run the tests! 👩‍🔬 (or run the `Run tests` task via VSCode)

### Or on local drive

1. Run `python3.7 -m venv .venv` to create a virtual environment
1. Run `source .venv/bin/activate` to go into that virtual environment
1. Run `pip install -r requirements_dev.txt` to install all of the dependencies in `requirements.txt` (which includes `pytest`)
1. Make sure test files are present and up to date by running `git submodule init` (first time) and `git submodule update`
1. Run `pytest` to run the tests! 👩‍🔬 (or run the `Run tests` task via VSCode)

## SCXML

SCXML tests are ran from [the SCION Test Framework](./node_modules/@scion-scxml/test-framework/README.md) module.

## Related Projects

- [finite-state-machine](https://github.com/alysivji/finite-state-machine)
- [Sismic for Python](https://github.com/AlexandreDecan/sismic)
- [Miros](https://github.com/aleph2c/miros)
