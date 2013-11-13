import os
import sys

from config import *

def addLocalPaths(paths):
    for path_part in paths:
        base_path = os.path.join(local_path, path_part)
        abs_path = os.path.abspath(base_path)
        sys.path.insert(0, abs_path)
