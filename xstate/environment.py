import os
IS_PRODUCTION = True if os.getenv('IS_PRODUCTON',None) else False
WILDCARD = os.getenv('WILDCARD',"*")

NULL_EVENT = ''
STATE_IDENTIFIER = os.getenv('STATE_IDENTIFIER',"#")
