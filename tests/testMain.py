import os
import unittest
import numpy
import arcpy
import arcgisscripting # our error objects are within this class
import zipfile

from nose.tools import *
from tempdir import TempDir
import utils
import config

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
utils.addLocalPaths(import_paths)
# now we can import our scripts
from scripts import bpi, standardize_bpi_grids, btm_model, slope, \
        ruggedness, depth_statistics, classify, surface_area_to_planar_area

class TestBtmDocument(unittest.TestCase):

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(config.xml_doc))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(config.csv_doc))

    def testMalformedCsvDocumentExsists(self):
        self.assertTrue(os.path.exists(config.malformed_csv_doc))


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

            #r = arcpy.Raster(bpi_raster)
            #self.assertAlmostEqual(r.mean, 0.295664335664)
            #self.assertAlmostEqual(r.standardDeviation, 1.65611606614)

            arcpy.CalculateStatistics_management(bpi_raster) 
            self.assertAlmostEqual(utils.raster_properties(bpi_raster, "MEAN"), 0.295664335664)
            self.assertAlmostEqual(utils.raster_properties(bpi_raster, "STD"), 1.65611606614)
 
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

class TestBpiSlope(unittest.TestCase):

    """
    slope.main(bathy=None, out_raster=None)
    """
    def testSlopeImport(self):
        self.assertTrue('main' in vars(slope))

    def testSlopeRun(self):
        with TempDir() as d:
            slope_raster = os.path.join(d, 'test_slope.tif')
            arcpy.env.scratchWorkspace = d 
            slope.main(bathy=config.bathy_raster, out_raster=slope_raster)
            self.assertTrue(os.path.exists(slope_raster))
            # doing this causes WindowsError: [Error 32] file used by another process
            #with Rast(slope_raster) as r:
                #self.assertAlmostEqual(r.mean, 3.802105241105673)
                #self.assertAlmostEqual(r.mean, 100)
 
            arcpy.CalculateStatistics_management(slope_raster) 
            self.assertAlmostEqual(utils.raster_properties(slope_raster, "MEAN"), \
                3.802105241105673)

class TestBpiSlope(unittest.TestCase):

    """
    slope.main(bathy=None, out_raster=None)
    """
    def testSlopeImport(self):
        self.assertTrue('main' in vars(slope))

    def testSlopeRun(self):
        with TempDir() as d:
            slope_raster = os.path.join(d, 'test_slope.tif')
            arcpy.env.scratchWorkspace = d 
            slope.main(bathy=config.bathy_raster, out_raster=slope_raster)
            self.assertTrue(os.path.exists(slope_raster))
            # doing this causes WindowsError: [Error 32] file used by another process
            #with Rast(slope_raster) as r:
                #self.assertAlmostEqual(r.mean, 3.802105241105673)
                #self.assertAlmostEqual(r.mean, 100)
 
            arcpy.CalculateStatistics_management(slope_raster) 
            self.assertAlmostEqual(utils.raster_properties(slope_raster, "MEAN"), \
                3.802105241105673)

class TestVrm(unittest.TestCase):
    """
    ruggestness.main(InRaster=None, NeighborhoodSize=None, 
        OutWorkspace=None, OutRaster=None)
    """
    def testVrmImport(self):
        self.assertTrue('main' in vars(ruggedness))

    def testVrmRun(self):
        with TempDir() as d:
            neighborhood = 3 # 3x3 neighborhood
            vrm_raster = os.path.join(d, 'test_vrm.tif')

            arcpy.env.scratchWorkspace = d 
            ruggedness.main(config.bathy_raster, neighborhood, d, \
                    vrm_raster)
            self.assertTrue(os.path.exists(vrm_raster))

            arcpy.CalculateStatistics_management(vrm_raster) 
            self.assertAlmostEqual(utils.raster_properties(vrm_raster, "MEAN"), \
                    0.00062628513039036) 
            self.assertAlmostEqual(utils.raster_properties(vrm_raster, "STD"), \
                    0.00087457748556755)


class TestSaPa(unittest.TestCase):
    """
    surface_area_to_planar_area.main(in_raster=None, out_raster=None, 
        area_raster)
    """
    def testSaPaImport(self):
        self.assertTrue('main' in vars(surface_area_to_planar_area))

    def testSaPaRun(self):
        with TempDir() as d:
            ratio_raster = os.path.join(d, 'test_sapa_ratio.tif')
            surf_raster = os.path.join(d, 'test_surface_area.tif')

            arcpy.env.scratchWorkspace = d 
            surface_area_to_planar_area.main(config.bathy_raster, 
                    ratio_raster, surf_raster)
            self.assertTrue(os.path.exists(ratio_raster))

            arcpy.CalculateStatistics_management(ratio_raster) 
            self.assertAlmostEqual(utils.raster_properties(ratio_raster, "MEAN"), \
               1.0042422342676) 
            self.assertAlmostEqual(utils.raster_properties(ratio_raster, "STD"), \
               0.0058175502835692)

            self.assertAlmostEqual(utils.raster_properties(surf_raster, "MEAN"), \
                25.119343739217)
            self.assertAlmostEqual(utils.raster_properties(surf_raster, "STD"), \
                0.14551573347447)


class TestDepthStatistics(unittest.TestCase):
    """
    depth_statistics.main(in_raster=None, neighborhood_size=None, 
        out_workspace=None, out_stats_raw=None)
    """
    def testDepthStatisticsImport(self):
        self.assertTrue('main' in vars(depth_statistics))

    def testDepthStatisticsRun(self):
        with TempDir() as d:
            neighborhood = 3 # 3x3 neighborhood
            arcpy.env.scratchWorkspace = d 
            out_workspace = d
            stats = "Mean Depth;Variance;Standard Deviation"
            depth_statistics.main(config.bathy_raster, neighborhood, 
                    out_workspace, stats)

            # mean of depth summary rasters
            mean_depths = {
                'meandepth': -20.56248074571827,
                'stdevdepth': 0.2946229406453136,
                'vardepth': 0.1281792675921596 }

            for (stat, mean_value) in mean_depths.items():
                raster = os.path.join(d, stat)
                self.assertTrue(os.path.exists(raster))
                arcpy.CalculateStatistics_management(raster)
                self.assertAlmostEqual(utils.raster_properties(raster, "MEAN"), \
                        mean_value)

class TestRunFullModel(unittest.TestCase):

    def setUp(self):
        self.broad_inner_rad = 10
        self.broad_outer_rad = 30
        self.fine_inner_rad = 5
        self.fine_outer_rad = 10
        self.csv_mean = None
        self.xml_mean = None
    
    def sumFirstClass(self, in_raster):
        # Extract and sum only the first class from the input raster 
        #   (raster values of 1).
        remap = arcpy.sa.RemapValue([[1,1]])
        remappedRaster = arcpy.sa.Reclassify(in_raster, "Value", remap, "NODATA")
        remapped_numpy = arcpy.RasterToNumPyArray(remappedRaster)
        del remappedRaster
        return remapped_numpy.sum() 
    
    def testToolboxImport(self):
        self.toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('runfullmodel' in vars(self.toolbox))

    def testWizardImport(self):
        self.assertTrue('main' in vars(btm_model))

    def testModelExecuteWithCsv(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d 
        
            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.csv_doc, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.csv_mean = utils.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.csv_mean, 5.6517482517483)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    @raises(ValueError)
    def testModelExecuteWithMalformedCsv(self):
        with TempDir() as d:
            # raises a ValueError when the malformed line is encountered.
            classify.main(config.malformed_csv_doc, 'null.tif', \
                    'null.tif', 'null.tif', 'null.tif', config.bathy_raster, \
                     os.path.join(d, 'null.tif'))


    def testModelExecuteWithXml(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d 
        
            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.xml_doc, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.xml_mean = utils.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.xml_mean, 5.6517482517483)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    def testXmlCsvConsistency(self):
        # XML and CSV are two separate classification backends, make sure the
        # results are consistent between the model runs.
        # FIXME: not consistent right now.
        self.assertEqual(self.csv_mean, self.xml_mean)

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
