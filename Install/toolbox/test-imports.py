import os
import math
import sys
import re
import tempfile
import textwrap

import arcpy

import xml.etree.cElementTree as et
import glob

# import our datatype conversion submodule
from datatype import datatype
dt = datatype.DataType()

# import our local directory so we can import internal modules
local_path = os.path.abspath(os.path.dirname(__file__))
print local_path
sys.path.insert(0, local_path)

print sys.path

from scripts import bpi

print dir(bpi)
