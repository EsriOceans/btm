import os
import sys
import unittest
import numpy
import arcpy

# import our local directory so we can use the internal modules
local_path = os.path.dirname(__file__)
scripts_path = os.path.join(local_path, '..', 'Install/toolbox')
abs_path = os.path.abspath(scripts_path)
sys.path.insert(0, abs_path)

from scripts import *

# configure test data
# XXX: use .ini files for these instead? used in other 'important' unit tests

class TestBpiScript(unittest.TestCase):
    from scripts import bpi
    def testBpiImport(self, method=bpi):
        self.assertRaises(ValueError, method.main(), None)

    def testBpiRun(self):
        pass

class TestStandardizeBpiGridsScript(unittest.TestCase):
    from scripts import standardize_bpi_grids
    def testStdImport(self, method=standardize_bpi_grids):
        pass
    
    def testStdRun(self):
        pass

if __name__  == '__main__':
    unittest.main()
