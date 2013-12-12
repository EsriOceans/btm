import os
import unittest
import numpy
import arcpy
import arcgisscripting # our error objects are within this class
import zipfile
from tempdir import TempDir

import utils
import config

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
utils.addLocalPaths(import_paths)

from scripts import bpi, standardize_bpi_grids, btm_model

class TestBtmDocument(unittest.TestCase):

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(config.xml_doc))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(config.csv_doc))

class TestBtmRaster(unittest.TestCase):
    def testRasterExists(self):
        self.assertTrue(os.path.exists(config.bathy_raster))

class TestBpiScript(unittest.TestCase):

    """
    bpi.main( bathy=in_raster, inner_radius=10,
        outer_radius=30, out_raster=out_raster
	    bpi_type='broad')
    """
    def testBpiImport(self):
        self.assertTrue('main' in vars(bpi))

    def testBpiRun(self):
        with TempDir() as d:
            bpi_raster = os.path.join(d, 'test_run_bpi.tif')
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                outer_radius=30, out_raster=bpi_raster, bpi_type='broad')
            self.assertTrue(os.path.exists(bpi_raster))

            arcpy.CalculateStatistics_management(bpi_raster) 
            self.assertAlmostEqual(utils.raster_properties(bpi_raster, "MEAN"), 0.295664335664)
            self.assertAlmostEqual(utils.raster_properties(bpi_raster, "STD"), 1.65611606614)
 
            # clean up
            arcpy.Delete_management(bpi_raster)
            self.assertFalse(os.path.exists(bpi_raster))

class TestStandardizeBpiGridsScript(unittest.TestCase):

    def testStdImport(self):
        self.assertTrue('main' in vars(standardize_bpi_grids))
    
    def testStdRun(self):
        with TempDir() as d:
            in_raster = os.path.join(d, 'test_bpi.tif')
            std_raster = os.path.join(d, 'test_std_bpi.tif')

            # was encountering this: ERROR 000875: Output raster: 
            # c:\Users\shau7031\AppData\Local\Temp\tmp8co8nk\FocalSt_bath1's 
            # workspace is an invalid output workspace. Force the workspace to our temp:
            arcpy.env.scratchWorkspace = d 
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                outer_radius=30, out_raster=in_raster, bpi_type='broad')

            self.assertTrue(os.path.exists(in_raster))

            standardize_bpi_grids.main(bpi_raster=in_raster, out_raster=std_raster)
            self.assertTrue(os.path.exists(std_raster))

            arcpy.CalculateStatistics_management(std_raster) 
            self.assertAlmostEqual(utils.raster_properties(std_raster, "MEAN"), 0.671608391608)
            self.assertAlmostEqual(utils.raster_properties(std_raster, "STD"), 99.655593923183)

            # clean up
            arcpy.Delete_management(in_raster)
            arcpy.Delete_management(std_raster)
            self.assertFalse(os.path.exists(std_raster))

class TestClassifyWizard(unittest.TestCase):

    def testToolboxImport(self):
        self.toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('runfullmodel' in vars(self.toolbox))

    def testWizardImport(self):
        self.assertTrue('main' in vars(btm_model))

    def testModelExecute(self):
        with TempDir() as d:
            workspace = d
            bathy = config.bathy_raster
            broad_inner_radius=10
            broad_outer_radius=30
            fine_inner_radius=5
            fine_outer_radius=10
            classification_dict = config.csv_doc
            model_output = os.path.join(d, 'output_zones.tif')
        
            btm_model.main(workspace, bathy, broad_inner_radius, broad_outer_radius, fine_inner_radius, fine_outer_radius, classification_dict, model_output)

            self.assertTrue(os.path.exists(model_output))

            # do something fancy to count up the number of cells of each class?
            self.assertAlmostEqual(utils.raster_properties(model_output, "MEAN"), \
                    5.45594405594)

            remap = arcpy.sa.RemapValue([[1,1]])
            remappedRaster = arcpy.sa.Reclassify(model_output, "Value", remap, "NODATA")
            remapped_numpy = arcpy.RasterToNumPyArray(remappedRaster)
            del remappedRaster
            self.assertEqual(remapped_numpy.sum(), 88)

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
