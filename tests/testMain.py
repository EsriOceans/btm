import os
import unittest
import arcpy
import zipfile

from nose.tools import raises
from tempdir import TempDir

import config
import utils

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
utils.add_local_paths(import_paths)
# now we can import our scripts
from scripts import bpi, standardize_bpi_grids, btm_model, aspect, \
        slope, ruggedness, depth_statistics, classify, surface_area_to_planar_area

class TestBtmDocument(unittest.TestCase):

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(config.base_xml))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(config.base_csv))

    def testMalformedCsvDocumentExsists(self):
        self.assertTrue(os.path.exists(config.malformed_csv))


class TestBtmRaster(unittest.TestCase):
    def testRasterExists(self):
        self.assertTrue(os.path.exists(config.bathy_raster))

class TestBpiScript(unittest.TestCase):

    def testBpiImport(self):
        self.assertTrue('main' in vars(bpi))

    def testBpiRun(self):
        with TempDir() as d:
            bpi_raster = os.path.join(d, 'test_run_bpi.tif')
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                outer_radius=30, out_raster=bpi_raster, bpi_type='broad')
            self.assertTrue(os.path.exists(bpi_raster))

            self.assertAlmostEqual(
                    utils.raster_properties(bpi_raster, "MEAN"), 0.295664335664)
            self.assertAlmostEqual(
                    utils.raster_properties(bpi_raster, "STD"), 1.65611606614)

class TestStandardizeBpiGridsScript(unittest.TestCase):

    def testStdImport(self):
        self.assertTrue('main' in vars(standardize_bpi_grids))

    def testStdRun(self):
        with TempDir() as d:
            in_raster = os.path.join(d, 'test_bpi.tif')
            std_raster = os.path.join(d, 'test_std_bpi.tif')

            # was encountering this: ERROR 000875: Output raster:
            # c:\Users\shau7031\AppData\Local\Temp\tmp8co8nk\FocalSt_bath1's
            # workspace is an invalid output workspace. Force the workspace to temp:
            arcpy.env.scratchWorkspace = d
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                outer_radius=30, out_raster=in_raster, bpi_type='broad')

            self.assertTrue(os.path.exists(in_raster))

            standardize_bpi_grids.main(bpi_raster=in_raster, out_raster=std_raster)
            self.assertTrue(os.path.exists(std_raster))

            self.assertAlmostEqual(
                    utils.raster_properties(std_raster, "MEAN"), 0.671608391608)
            self.assertAlmostEqual(
                    utils.raster_properties(std_raster, "STD"), 99.655593923183)

class TestBpiAspect(unittest.TestCase):

    """
    aspect.main(bathy=None, out_sin_raster=None, out_cos_raster=None)
    """

    def testAspectImport(self):
        self.assertTrue('main' in vars(aspect))

    def testAspectRun(self):
        with TempDir() as d:
            aspect_sin_raster = os.path.join(d, 'test_aspect_sin.tif')
            aspect_cos_raster = os.path.join(d, 'test_aspect_cos.tif')
            arcpy.env.scratchWorkspace = d

            aspect.main(bathy=config.bathy_raster, out_sin_raster=aspect_sin_raster, \
                    out_cos_raster=aspect_cos_raster)

            self.assertTrue(os.path.exists(aspect_sin_raster))
            self.assertTrue(os.path.exists(aspect_cos_raster))

            self.assertAlmostEqual(utils.raster_properties(aspect_sin_raster, "MEAN"), \
                -0.06153140691827335)
            self.assertAlmostEqual(utils.raster_properties(aspect_cos_raster, "MEAN"), \
                0.02073092622177259) 

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

            self.assertAlmostEqual(utils.raster_properties(vrm_raster, "MEAN"), \
                    0.00062628513039036)
            self.assertAlmostEqual(utils.raster_properties(vrm_raster, "STD"), \
                    0.00087457748556755)


class TestSaPa(unittest.TestCase):
    """
    surface_area_to_planar_area.main(in_raster=None, out_raster=None,
        area_raster=None)
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
            self.assertTrue(os.path.exists(surf_raster))

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
                'vardepth': 0.1281792675921596}

            for (stat, mean_value) in mean_depths.items():
                raster = os.path.join(d, stat)
                self.assertTrue(os.path.exists(raster))
                self.assertAlmostEqual(utils.raster_properties(raster, "MEAN"), \
                        mean_value)

class TestRunFullModel(unittest.TestCase):

    def setUp(self):
        self.broad_inner_rad = 10
        self.broad_outer_rad = 30
        self.fine_inner_rad = 5
        self.fine_outer_rad = 10
        self.true_mean = 5.7815384615385
        self.csv_mean = None
        self.xml_mean = None
        self.excel_mean = None
        self.toolbox = None

    def sumFirstClass(self, in_raster):
        # Extract and sum only the first class from the input raster
        #   (raster values of 1).
        remap = arcpy.sa.RemapValue([[1, 1]])
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
                    config.base_csv, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.csv_mean = utils.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.csv_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    @raises(ValueError)
    def testModelExecuteWithMalformedCsv(self):
        with TempDir() as d:
            # raises a ValueError when the malformed line is encountered.
            classify.main(config.malformed_csv, 'null.tif', \
                    'null.tif', 'null.tif', 'null.tif', config.bathy_raster, \
                     os.path.join(d, 'null.tif'))

    def testModelExecuteWithXml(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.base_xml, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.xml_mean = utils.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.xml_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    def testModelExecuteWithExcel(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.base_excel, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.excel_mean = utils.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.excel_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    def testOutputConsistency(self):
        # Test that all three of our classification backends concur on the
        # output, and that results are consistent between the model runs.
        self.assertEqual(self.csv_mean, self.xml_mean)
        self.assertEqual(self.excel_mean, self.xml_mean)

class TestClassifyFgdb(unittest.TestCase):

    def testClassifyWithFgdbLocation(self):
        with TempDir() as d:
            fgdb_name = "classify.gdb"
            fgdb_workspace = os.path.join(d, fgdb_name)
            # create a temporary File Geodatabase location
            arcpy.CreateFileGDB_management(d, fgdb_name)
            self.assertTrue(os.path.exists(fgdb_workspace))
            # TODO: this currently hacks up the path to be a valid name, but should probably
            # instead throw an error and let the user correct the output name.
            classify_raster = os.path.join(fgdb_workspace, 'output_in_fgdb')
            classify.main(config.base_xml, config.broad_std_raster, config.fine_std_raster, \
                    config.slope_raster,  config.bathy_raster, classify_raster)
            # resulting 'fixed' name
            mean = utils.raster_properties(classify_raster, "MEAN")
            self.assertAlmostEqual(mean, 5.78153846153846)


class TestRunFullModelKnownZones(unittest.TestCase):
    def setUp(self):
        self.broad_inner_rad = 1
        self.broad_outer_rad = 5
        self.fine_inner_rad = 1
        self.fine_outer_rad = 3
        self.xml_mean = None
        self.excel_mean = None
        self.toolbox = None
        self.xml_zones = None
        self.excel_zones = None
        self.expected = {1: 433, 2: 6, 3: 2428, 4: 708} # one cell differs from v1.

    def extractRasterAttributeTable(self, raster_path):
        rat = {}
        raster = arcpy.sa.Raster(raster_path)
        self.assertTrue(raster.hasRAT)
        rows = arcpy.SearchCursor(raster, "", "", "Value;Count", "")
        for row in rows:
            rat[row.getValue("Value")] = row.getValue("Count")
        return rat

    def testModelExecuteWithXml(self):
        with TempDir() as d:
            zones_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.zones_xml, zones_output)

            self.assertTrue(os.path.exists(zones_output))
            arcpy.BuildRasterAttributeTable_management(zones_output)

            self.xml_mean = utils.raster_properties(zones_output, "MEAN")
            self.xml_zones = zones_output

            # some asserts here for validation
            rat = self.extractRasterAttributeTable(self.xml_zones)
            for (value, count) in self.expected.items():
                self.assertEqual(count, rat[value])

    def testModelExecuteWithExcel(self):
        with TempDir() as d:
            zones_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(d, config.bathy_raster, self.broad_inner_rad, \
                    self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad, \
                    config.zones_excel, zones_output)

            self.assertTrue(os.path.exists(zones_output))
            arcpy.BuildRasterAttributeTable_management(zones_output)

            self.excel_mean = utils.raster_properties(zones_output, "MEAN")
            self.excel_zones = zones_output
            # some asserts here for validation
            rat = self.extractRasterAttributeTable(self.excel_zones)
            for (value, count) in self.expected.items():
                self.assertEqual(count, rat[value])

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

if __name__ == '__main__':
    unittest.main()
