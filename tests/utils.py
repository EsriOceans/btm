import os
import sys

local_path = os.path.dirname(__file__)

def addLocalPaths(paths):
    for path_part in paths:
        base_path = os.path.join(local_path, path_part)
        abs_path = os.path.abspath(base_path)
        print "importing " + abs_path
        sys.path.insert(0, abs_path)

