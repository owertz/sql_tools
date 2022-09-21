from enum import Enum

__author__ = 'OWE'

"""
This file contains a set of data usefull for all the modules.


TODO
----
Legend
[ n ]: n-th task in the TODO list
[ . ]: task in progress.
[ * ]: task implemented.

Content
[  ] ...
      
FIXME
-----
-
"""

class OperatingSystem(Enum):
    LINUX = "linux"
    MACOS = "darwin"
    WINDOWS = "win32"