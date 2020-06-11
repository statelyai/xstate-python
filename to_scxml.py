import xml.etree.ElementTree as ET
from typing import Optional
import json

from xstate.machine import Machine

ns = {"scxml": "http://www.w3.org/2005/07/scxml"}


def convert_scxml(element: ET.Element, parent):
    states = element.findall("scxml:state", namespaces=ns)

    return {
        "id": "machine",
        "initial": element.attrib.get("initial", None),
        "states": accumulate_states(element, parent),
    }


def accumulate_states(element: ET.Element, parent: ET.Element):
    state_els = element.findall("scxml:state", namespaces=ns)
    states = [convert_state(state_el, element) for state_el in state_els]

    states_dict = {}

    for state in states:
        states_dict[state.get("key")] = state

    return states_dict


def convert_state(element: ET.Element, parent: ET.Element):
    parent_id = parent.attrib.get("id", "") if parent else None
    id = element.attrib.get("id")
    transition_els = element.findall("scxml:transition", namespaces=ns)
    transitions = [convert_transition(el, element) for el in transition_els]

    result = {"id": f"{id}", "key": id}

    if len(transitions) > 0:
        transitions_dict = {}

        for t in transitions:
            transitions_dict[t.get("event")] = t

        result["on"] = transitions_dict

    return result


def convert_transition(element: ET.Element, parent: ET.Element):
    event_type = element.attrib.get("event")
    event_target = element.attrib.get("target")

    raise_els = element.findall("scxml:raise", namespaces=ns)

    actions = [convert_raise(raise_el, element) for raise_el in raise_els]

    return {"event": event_type, "target": event_target, "actions": actions}


def convert_raise(element: ET.Element, parent: ET.Element):
    return {"type": "xstate:raise", "event": element.attrib.get("event")}


elements = {"scxml": convert_scxml, "state": convert_state}


def convert(element: ET.Element, parent: Optional[ET.Element] = None):
    _, _, element_tag = element.tag.rpartition("}")  # strip namespace
    result = elements.get(element_tag, lambda _: f"Invalid tag: {element_tag}")

    return result(element, parent)


tree = ET.parse("node_modules/@scion-scxml/test-framework/test/actionSend/send1.scxml")

with open(
    "node_modules/@scion-scxml/test-framework/test/actionSend/send1.json"
) as test_file:
    test = json.load(test_file)

print(test)

root = tree.getroot()
result = convert(root)
machine = Machine(result)

state = machine.initial_state

for event_test in test.get("events"):
    event_to_send = event_test.get("event")
    event_name = event_to_send.get("name")
    next_configuration = event_test.get("nextConfiguration")

    state = machine.transition(state, event_name)

    assert [sn.key for sn in state.configuration] == next_configuration

print(machine.transition(machine.initial_state, "t"))

# for child in root:
#     print(child.tag, child.attrib)
