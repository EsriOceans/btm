import os
import unittest
import numpy
import arcpy
import arcgisscripting # our error objects are within this class
import zipfile

import utils
# import our constants;
# configure test data
import config
# FIXME: use .ini files for these instead? used in other 'important' unit tests

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
utils.addLocalPaths(import_paths)

# create a temporary directory for analysis steps

class TestBtmDocument(unittest.TestCase):

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(config.xml_doc))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(config.csv_doc))

class TestBtmRaster(unittest.TestCase):
    def testRasterExists(self):
        self.assertTrue(os.path.exists(config.bathy_raster))

class TestBpiScript(unittest.TestCase):
    from scripts import bpi

    """
    bpi.main( bathy=in_raster, inner_radius=10,
        outer_radius=30, out_raster=out_raster
	    bpi_type='broad')
    """
    def testBpiImport(self, method=bpi):
        self.assertTrue('main' in vars(method))

    def testBpiRun(self, method=bpi):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        output_raster = os.path.join(base_dir, 'data', 'test_run_bpi.tif')
        method.main(bathy=bathy_raster, inner_radius=10,
            outer_radius=30, out_raster=output_raster, bpi_type='broad')
        self.assertTrue(os.path.exists(output_raster))
        # clean up
        arcpy.Delete_management(output_raster)
        self.assertFalse(os.path.exists(output_raster))

class TestStandardizeBpiGridsScript(unittest.TestCase):
    from scripts import standardize_bpi_grids
    def testStdImport(self, method=standardize_bpi_grids):
        self.assertTrue('main' in vars(method))
    
    def testStdRun(self):
        pass

class TestClassifyWizard(unittest.TestCase):
    def testToolboxImport(self):
        self.toolbox = arcpy.ImportToolbox(tbx_file)
        self.assertTrue('BtmModel' in vars(self.toolbox))

    def testModelExecute(self):
        try:
            model_run = self.toolbox('BtmModel')
        except Exception as e:
            self.assertTrue(e, arcgisscripting.ExecuteError)

    # TODO: test the classify wizard works with valid inputs
    """ parameters:
         - workspace
         - bathy
         - broad_bpi inner radius
         - broad_bpi outer radius
         - fine_bpi inner radius
         - fine_bpi outer radius
         - classification dict
         - output zones [raster result]
    """

# this test should be run after a fresh run of makeaddin to rebuild the .esriaddin file.
class TestAddin(unittest.TestCase):
    def setUp(self):
        self.addin_path = os.sep.join([config.local_path, '..', '..', 'btm.esriaddin'])
        self.addin_zip = zipfile.ZipFile(self.addin_path, 'r')

    def testToolboxIsPresent(self):
        toolbox_path = 'Install/toolbox/btm.pyt' 
        self.assertTrue(toolbox_path in self.addin_zip.namelist())

    def testModelNameIsValid(self):
        """ the signing process changes names to to URL encoded; make sure
         our model remains invariant."""
        model_name = 'Install/toolbox/btm_model.tbx' 
        self.assertTrue(model_name in self.addin_zip.namelist())

if __name__  == '__main__':
    unittest.main()
