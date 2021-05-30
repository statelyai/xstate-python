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

## Developing

You can set up your development environment in two different ways. 

### Using [Remote Containers](https://code.visualstudio.com/docs/remote/containers) (recommended if you use VS Code)

Prerequisites 
* VS Code IDE and [Remote Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

Steps

1. [Open the folder in a container](https://code.visualstudio.com/docs/remote/containers#_quick-start-open-an-existing-folder-in-a-container). This will setup your environment with python (including python and pylance extensions), dependencies and download scxml tests.
1. Run `poetry run pytest --cov` to run the tests! 👩‍🔬 (or run the `Run tests` task via VS Code or using VS Code Test explorer where you can debug as well)

### Or installing the environment on your local drive

Prerequisites 
* [`poetry`](https://python-poetry.org/) for package and dependency management

Steps
1. Run `poetry install` to create a virtual environment
1. Make sure test files are present and up to date by running `git submodule update --init`
1. Run `poetry run pytest --cov` to run the tests! 👩‍🔬 (or run the `Run tests` task via VS Code or using VS Code Test explorer where you can debug as well)

## SCXML

SCXML tests are ran from [the SCION Test Framework](./node_modules/@scion-scxml/test-framework/README.md) module.

## Related Projects

- [finite-state-machine](https://github.com/alysivji/finite-state-machine)
- [Sismic for Python](https://github.com/AlexandreDecan/sismic)
- [Miros](https://github.com/aleph2c/miros)
