from __future__ import (
    annotations,
)  #  PEP 563:__future__.annotations will become the default in Python 3.11

import os

IS_PRODUCTION = True if os.getenv("IS_PRODUCTON", None) else False
WILDCARD = os.getenv("WILDCARD", "*")

NULL_EVENT = ""
STATE_IDENTIFIER = os.getenv("STATE_IDENTIFIER", "#")
