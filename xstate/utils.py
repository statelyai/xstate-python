from typing import  Any, Callable, Dict, List, Optional, Set, Tuple, Union



import js2py
# TODO: Work around for import error, don't know why lint unresolved, if import from xstate.algorthim we get import error in `transitions.py`
# Explain : ImportError: cannot import name 'get_configuration_from_js' from 'xstate.algorithm' 
def get_configuration_from_js(config:str) -> dict: 
    """Translates a JS config to a xstate_python configuration dict
    config: str  a valid javascript snippet of an xstate machine
    Example
        get_configuration_from_js(
            config=
            ```
              {
                a: 'a2',
                b: {
                  b2: {
                    foo: 'foo2',
                    bar: 'bar1'
                  }
                }
              }
            ```)
        )
    """
    return js2py.eval_js(f"config = {config.replace(chr(10),'').replace(' ','')}").to_dict()