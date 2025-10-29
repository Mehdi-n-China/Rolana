
"""
This module contains a single variable that’s imported every time
you manually invoke a special function, like manual overrides.
Manual overrides are dangerous as hell and should only be used
if you’re absolutely sure you know what you’re doing.

There are 4 levels of authority:

Level 0 — Baby mode:
    You can’t override anything. The node handles itself.
    This is the default and recommended level. If you don’t
    know exactly what’s going on, stay here.

Level 1 — Admin:
    You can do basic manual actions like banning/unbanning or
    tweaking local limits. Mostly safe if you’re not dumb about it.

Level 2 — Root:
    You can directly mess with the database, push raw commands,
    or talk to internal modules. Dangerous, but still manageable
    if you know your system well.

Level 3 - please don’t:
    Unlimited control. You can override literally everything,
    dump private keys, send unformatted messages to peers,
    or just blow the whole thing up. If you’re here,
    you either know EXACTLY what you’re doing or you’ve lost it.
"""


AUTHORITY_LEVEL: int = 1

if AUTHORITY_LEVEL not in (1,2,3,4,5):
    AUTHORITY_LEVEL = 1 # stops accidental bad values