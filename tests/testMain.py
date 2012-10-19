import os
import unittest
import numpy
import arcpy

from utils import *
# import our constants;
# configure test data
# XXX: use .ini files for these instead? used in other 'important' unit tests
from config import *

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
addLocalPaths(import_paths)

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

class TestBtmDocument(unittest.TestCase):
    # XXX this won't automatically get the right thing... how can we fix it?
    import utils

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(xml_doc))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(csv_doc))


if __name__  == '__main__':
    unittest.main()
