# https://plantweb.readthedocs.io/#python-api
# https://plantuml.com/state-diagram
from plantweb.render import render

from xstate.machine import Machine

# just a test
simple_machine = Machine(
    {
        "id": "simple",
        "initial": "green",
        "states": {
            "green": {"on": {"JENNY_EVENT": "yellow"}},
            "yellow": {"on": {"NEXT_EVENT": "red"}},
            "red": {"on": {"NEXT_EVENT": "green"}},
        },
    }
)


def state_node_to_viz(state_node):
    result = ""

    if not state_node.parent:
        result += """
@startuml

skinparam state {
    ArrowColor Black
    ArrowThickness 2
    BorderThickness 5
    BorderColor Blue
    BackgroundColor White
}
"""

    if state_node.initial:
        initial_state = state_node.initial.target[0].id
        initial_string = f"[*] --> {initial_state}\n"
        result += initial_string

    transitions = state_node.transitions
    for t in transitions:
        t_string = f"{t.source.id} --> {t.target[0].id} : {t.event}\n"
        result += t_string

    children = state_node.states.values()
    for c in children:
        child_string = state_node_to_viz(c)
        result += child_string

    if not state_node.parent:
        result += "@enduml\n"

    return result


if __name__ == "__main__":
    output = render(
        state_node_to_viz(simple_machine.root),
        engine="plantuml",
        format="svg",
        cacheopts={"use_cache": False},
    )[0]

    file1 = open("test.svg", "w")
    file1.write(output.decode("utf-8"))
    file1.close()
