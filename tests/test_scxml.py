import xml.etree.ElementTree as ET
from typing import Optional, Dict, List
import json
import pytest
from xstate.scxml import scxml_to_machine

test_dir = "node_modules/@scion-scxml/test-framework/test"

test_groups: Dict[str, List[str]] = {"actionSend": ["send1"]}

test_files = [
    (f"{test_dir}/{k}/{vv}.scxml", f"{test_dir}/{k}/{vv}.json")
    for k, v in test_groups.items()
    for vv in v
]

@pytest.mark.parametrize("scxml_source,scxml_test_source", test_files)
def test_scxml(scxml_source, scxml_test_source):
    machine = scxml_to_machine(scxml_source)
    state = machine.initial_state

    with open(scxml_test_source) as scxml_test_file:
        scxml_test = json.load(scxml_test_file)

    for event_test in scxml_test.get("events"):
        event_to_send = event_test.get("event")
        event_name = event_to_send.get("name")
        next_configuration = event_test.get("nextConfiguration")

        state = machine.transition(state, event_name)

        assert [sn.key for sn in state.configuration] == next_configuration
