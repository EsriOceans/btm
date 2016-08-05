import locale
import os
import unittest
import sys
import arcpy
from arcpy import Raster
import zipfile

from nose.tools import raises

import config
import utils

# import our local directory so we can use the internal modules
import_paths = ['../Install/toolbox', '../Install']
utils.add_local_paths(import_paths)

# now we can import our scripts
from scripts import bpi, standardize_bpi_grids, btm_model, aspect, \
    slope, ruggedness, depth_statistics, classify, \
    surface_area_to_planar_area, scale_comparison, utils as su

from scripts.tempdir import TempDir


class TestBtmDocument(unittest.TestCase):
    """ Test our document class."""

    def testXmlDocumentExists(self):
        self.assertTrue(os.path.exists(config.base_xml))

    def testCsvDocumentExists(self):
        self.assertTrue(os.path.exists(config.base_csv))

    def testMalformedCsvDocumentExsists(self):
        self.assertTrue(os.path.exists(config.malformed_csv))

    def testCsvHeaderColumns(self):
        """
        One of the header labels was wrong previously, check that we have
        the elements we expect in the correct positions.
        """

        btm_doc = su.BtmDocument(config.base_csv)
        header = btm_doc.schema.header   # CSV files contain a header element

        expected_header = [
            'Class', 'Zone', 'BroadBPI_Lower', 'BroadBPI_Upper',
            'FineBPI_Lower', 'FineBPI_Upper', 'Slope_Lower', 'Slope_Upper',
            'Depth_Lower', 'Depth_Upper'
        ]

        for (i, label) in enumerate(header):
            self.assertTrue(label in expected_header)
            self.assertTrue(label == expected_header[i])


class TestBtmRaster(unittest.TestCase):
    def testRasterExists(self):
        self.assertTrue(os.path.exists(config.bathy_raster))


# test utilities methods
class TestUtilitiesMethods(unittest.TestCase):

    def setUp(self):
        self.mean = -20.619977607194
        self.std = 2.730680267695
        self.sys_path = sys.path

    def testAlternativeDecimalMark(self):
        """ Test a locale which uses "," as its decimal separator."""
        # NOTE: Windows locales aren't named the same as the `man locale 1`
        # equivalents. For this code to be universal, it'd need to test os.name
        # and convert to the appropriate locale name.
        locale.setlocale(locale.LC_ALL, "german_germany")

        decimal_pt = locale.localeconv()['decimal_point']
        self.assertEqual(decimal_pt, ',')

        lc = locale.getlocale()
        self.assertEqual(lc[0], 'de_DE')
        self.assertEqual(lc[1], 'cp1252')

        # two tests to make sure that radix parsing is happening as expected
        self.assertEqual(locale.atof("-11,00"), -11.0)
        self.assertEqual(locale.atof("-11.000,50"), -11000.5)

    def testRasterProperties(self):
        """ Test the raster properties with a US locale."""
        # force to the US locale for radix tests
        locale.setlocale(locale.LC_ALL, "english_us")
        mean = su.raster_properties(config.bathy_raster, 'MEAN')
        self.assertAlmostEqual(mean, self.mean)

        std = su.raster_properties(config.bathy_raster, 'STD')
        self.assertAlmostEqual(std, self.std)

    def testRasterPropertiesAlternativeDecimalMark(self):
        """ Test a locale which uses "," as its decimal separator."""
        # Windows locales are different than the locale() equivs
        locale.setlocale(locale.LC_ALL, "german_germany")

        # force reload utils after locale is set; otherwise it'll set it
        # internally.
        try:
            reload(su)
        except NameError:
            # py3, assume 3.4+
            import importlib
            importlib.reload(su)

        mean = su.raster_properties(config.bathy_raster, 'MEAN')
        self.assertAlmostEqual(mean, self.mean)

        std = su.raster_properties(config.bathy_raster, 'STD')
        self.assertAlmostEqual(std, self.std)

    def testAddPaths(self):
        """An added path should be the first entry in sys.path,
           and be normalized."""
        # paths relative to 'Install/toolbox/scripts'
        images_dir = "../../../Images"
        su.add_local_paths([images_dir])
        added_path = sys.path[0].lower()
        image_abs_path = os.path.abspath("../Images").lower()
        self.assertEqual(image_abs_path, added_path)

    def tearDown(self):
        # reset locale
        locale.setlocale(locale.LC_ALL, "")
        sys.path = self.sys_path

# test individual scripts
#


class TestBpi(unittest.TestCase):

    def testBpiImport(self):
        self.assertTrue('main' in vars(bpi))

    def testBpiRun(self):
        with TempDir() as d:
            raster_fn = 'test_run_bpi.tif'
            bpi_raster = os.path.join(d, raster_fn)
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                     outer_radius=30, out_raster=bpi_raster, bpi_type='broad')

            self.assertTrue(raster_fn in os.listdir(d))

            self.assertAlmostEqual(
                su.raster_properties(bpi_raster, "MEAN"), 0.295664335664)
            self.assertAlmostEqual(
                su.raster_properties(bpi_raster, "STD"), 1.65611606614)


class TestStandardizeBpiGrids(unittest.TestCase):

    def testStdImport(self):
        self.assertTrue('main' in vars(standardize_bpi_grids))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('standardizebpi' in vars(toolbox))

    def testToolboxRunWithLayers(self):
        """ Test running the tool against the toolbox version
        using Layer files."""
        with TempDir() as d:

            broad_std_raster = os.path.join(d, 'test_broad_std_bpi.tif')
            fine_std_raster = os.path.join(d, 'test_fine_std_bpi.tif')

            arcpy.env.scratchWorkspace = d
            arcpy.ImportToolbox(config.pyt_file)

            mxd = arcpy.mapping.MapDocument(config.bpi_grids_mxd)
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            layers = arcpy.mapping.ListLayers(df)
            layer_names = [l.name for l in layers]

            broad_lyr = layers[layer_names.index('broad_bpi')]
            fine_lyr = layers[layer_names.index('fine_bpi')]

            arcpy.standardizebpi_btm(
                broad_lyr.dataSource, "0", "0", broad_std_raster,
                fine_lyr.dataSource, "0", "0", fine_std_raster)

            self.assertTrue(os.path.exists(broad_std_raster))
            self.assertTrue(os.path.exists(fine_std_raster))

            # Compare to known rasters
            self.assertAlmostEqual(
                su.raster_properties(broad_std_raster, "MEAN"),
                su.raster_properties(config.broad_std_raster, "MEAN"))
            self.assertAlmostEqual(
                su.raster_properties(broad_std_raster, "STD"),
                su.raster_properties(config.broad_std_raster, "STD"))

            self.assertAlmostEqual(
                su.raster_properties(fine_std_raster, "MEAN"),
                su.raster_properties(config.fine_std_raster, "MEAN"))
            self.assertAlmostEqual(
                su.raster_properties(fine_std_raster, "STD"),
                su.raster_properties(config.fine_std_raster, "STD"))

            del layers, df, mxd

    def testStdRun(self):
        with TempDir() as d:
            in_raster = os.path.join(d, 'test_bpi.tif')
            std_raster = os.path.join(d, 'test_std_bpi.tif')

            # was encountering this: ERROR 000875: Output raster:
            # c:\Users\shau7031\AppData\Local\Temp\tmp8co8nk\FocalSt_bath1's
            # workspace is an invalid workspace. Force workspace to temp:
            arcpy.env.scratchWorkspace = d
            bpi.main(bathy=config.bathy_raster, inner_radius=10,
                     outer_radius=30, out_raster=in_raster, bpi_type='broad')

            self.assertTrue(os.path.exists(in_raster))

            standardize_bpi_grids.main(
                bpi_raster=in_raster, out_raster=std_raster)
            self.assertTrue(os.path.exists(std_raster))

            self.assertAlmostEqual(
                su.raster_properties(std_raster, "MEAN"), 0.671608391608)
            self.assertAlmostEqual(
                su.raster_properties(std_raster, "STD"), 99.655593923183)


class TestBpiStatisticalAspect(unittest.TestCase):

    """
    aspect.main(bathy=None, out_sin_raster=None, out_cos_raster=None)
    """

    def testAspectImport(self):
        self.assertTrue('main' in vars(aspect))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('statisticalaspect' in vars(toolbox))

    def testAspectRun(self):
        with TempDir() as d:
            aspect_sin_raster = os.path.join(d, 'test_aspect_sin.tif')
            aspect_cos_raster = os.path.join(d, 'test_aspect_cos.tif')
            arcpy.env.scratchWorkspace = d

            aspect.main(
                bathy=config.bathy_raster,
                out_sin_raster=aspect_sin_raster,
                out_cos_raster=aspect_cos_raster)

            self.assertTrue(os.path.exists(aspect_sin_raster))
            self.assertTrue(os.path.exists(aspect_cos_raster))

            self.assertAlmostEqual(
                su.raster_properties(aspect_sin_raster, "MEAN"),
                -0.06153140691827335)
            self.assertAlmostEqual(
                su.raster_properties(aspect_cos_raster, "MEAN"),
                0.02073092622177259)


class TestBpiSlope(unittest.TestCase):

    """
    slope.main(bathy=None, out_raster=None)
    """
    def testSlopeImport(self):
        self.assertTrue('main' in vars(slope))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('btmslope' in vars(toolbox))

    def testSlopeRun(self):
        with TempDir() as d:
            slope_raster = os.path.join(d, 'test_slope.tif')
            arcpy.env.scratchWorkspace = d
            slope.main(bathy=config.bathy_raster, out_raster=slope_raster)
            self.assertTrue(os.path.exists(slope_raster))

            self.assertAlmostEqual(
                su.raster_properties(slope_raster, "MEAN"), 3.802105241105673)


class TestVrm(unittest.TestCase):
    """
    ruggedness.main(InRaster=None, NeighborhoodSize=None,
        OutRaster=None)
    """
    def testVrmImport(self):
        self.assertTrue('main' in vars(ruggedness))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('terrainruggedness' in vars(toolbox))

    def testVrmRun(self):
        with TempDir() as d:
            neighborhood = 3    # 3x3 neighborhood
            vrm_raster = os.path.join(d, 'test_vrm.tif')

            arcpy.env.scratchWorkspace = d
            ruggedness.main(config.bathy_raster, neighborhood, vrm_raster)
            self.assertTrue(os.path.exists(vrm_raster))

            self.assertAlmostEqual(
                su.raster_properties(vrm_raster, "MEAN"), 0.00062628513039036)
            self.assertAlmostEqual(
                su.raster_properties(vrm_raster, "STD"), 0.00087457748556755)


class TestSaPa(unittest.TestCase):
    """
    surface_area_to_planar_area.main(in_raster=None, out_raster=None,
        acr_correction=False, area_raster=None)
    """
    def testSaPaImport(self):
        self.assertTrue('main' in vars(surface_area_to_planar_area))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('surfacetoplanar' in vars(toolbox))

    def testSaPaRunNoCorrection(self):
        with TempDir() as d:
            ratio_raster = os.path.join(d, 'test_sapa_ratio.tif')
            surf_raster = os.path.join(d, 'test_surface_area.tif')

            arcpy.env.scratchWorkspace = d
            surface_area_to_planar_area.main(
                config.bathy_raster, ratio_raster, False, surf_raster)

            self.assertTrue(os.path.exists(ratio_raster))
            self.assertTrue(os.path.exists(surf_raster))

            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "MEAN"), 1.0042422342676)
            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "STD"), 0.0058175502835692)

            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "MEAN"), 25.119343091857)
            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "STD"), 0.14551573347447)

    def testSaPaRunCorrection(self):
        with TempDir() as d:
            ratio_raster = os.path.join(d, 'test_sapa_ratio.tif')
            surf_raster = os.path.join(d, 'test_surface_area.tif')

            arcpy.env.scratchWorkspace = d
            surface_area_to_planar_area.main(
                config.bathy_raster, ratio_raster, True, surf_raster)

            self.assertTrue(os.path.exists(ratio_raster))
            self.assertTrue(os.path.exists(surf_raster))

            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "MEAN"), 1.000616701751028)
            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "STD"), 0.0008445980914179108)

            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "MEAN"), 25.119343091857)
            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "STD"), 0.14551570953239)

    def testSaPaRunWithFgdbLocation(self):
        with TempDir() as d:
            fgdb_name = "sapa.gdb"
            fgdb_workspace = os.path.join(d, fgdb_name)
            # create a temporary File Geodatabase location
            arcpy.CreateFileGDB_management(d, fgdb_name)
            self.assertTrue(os.path.exists(fgdb_workspace))

            ratio_raster = os.path.join(fgdb_workspace, 'test_sapa_ratio')
            surf_raster = os.path.join(fgdb_workspace, 'test_sapa_area')

            arcpy.env.scratchWorkspace = d
            surface_area_to_planar_area.main(
                config.bathy_raster, ratio_raster, False, surf_raster)

            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "MEAN"), 1.0042422342676)
            self.assertAlmostEqual(
                su.raster_properties(ratio_raster, "STD"), 0.0058175502835692)

            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "MEAN"), 25.119343091857)
            self.assertAlmostEqual(
                su.raster_properties(surf_raster, "STD"), 0.14551573347447)


class TestDepthStatistics(unittest.TestCase):
    """
    depth_statistics.main(in_raster=None, neighborhood_size=None,
        out_workspace=None, out_stats_raw=None)
    """
    def testDepthStatisticsImport(self):
        self.assertTrue('main' in vars(depth_statistics))

    def testToolboxImport(self):
        toolbox = arcpy.ImportToolbox(config.pyt_file)
        self.assertTrue('depthstatistics' in vars(toolbox))

    def testDepthStatisticsRun(self):
        with TempDir() as d:
            neighborhood = 3    # 3x3 neighborhood
            arcpy.env.scratchWorkspace = d
            out_workspace = d
            stats = "Mean Depth;Variance;Standard Deviation"
            depth_statistics.main(
                config.bathy_raster, neighborhood, out_workspace, stats)

            # mean of depth summary rasters
            mean_depths = {
                'meandepth': -20.56248074571827,
                'stddevdepth': 0.2946229406453136,
                'vardepth': 0.1281792675921596
            }

            for (prefix, expected_value) in mean_depths.items():
                raster_path = os.path.join(
                    d, "{0}_{1:03d}.tif".format(prefix, neighborhood))
                self.assertTrue(os.path.exists(raster_path))
                self.assertAlmostEqual(
                    su.raster_properties(raster_path, 'MEAN'), expected_value)


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
        remapped_raster = arcpy.sa.Reclassify(
            in_raster, "Value", remap, "NODATA")
        remapped_numpy = arcpy.RasterToNumPyArray(remapped_raster)
        del remapped_raster
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

            btm_model.main(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad,
                config.base_csv, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.csv_mean = su.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.csv_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    def testModelExecuteWithCsvFromToolbox(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            arcpy.ImportToolbox(config.pyt_file)
            arcpy.runfullmodel_btm(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad,
                config.base_csv, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.csv_mean = su.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.csv_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    @raises(ValueError)
    def testModelExecuteWithMalformedCsv(self):
        with TempDir() as d:
            # raises a ValueError when the malformed line is encountered.
            classify.main(
                config.malformed_csv, 'null.tif',
                'null.tif', 'null.tif', config.bathy_raster,
                os.path.join(d, 'null.tif'))

    def testModelExecuteWithXml(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad,
                config.base_xml, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.xml_mean = su.raster_properties(model_output, "MEAN")
            self.assertAlmostEqual(self.xml_mean, self.true_mean)

            # count up the number of cells in the first class
            self.assertEqual(self.sumFirstClass(model_output), 88)

    def testModelExecuteWithExcel(self):
        with TempDir() as d:
            model_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad,
                config.base_excel, model_output)

            self.assertTrue(os.path.exists(model_output))

            self.excel_mean = su.raster_properties(model_output, "MEAN")
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
            # TODO: this currently hacks up the path to be a valid name,
            # but should probably instead throw an error and let the user
            # correct the output name.
            classify_raster = os.path.join(fgdb_workspace, 'output_in_fgdb')
            classify.main(
                config.base_xml, config.broad_std_raster,
                config.fine_std_raster, config.slope_raster,
                config.bathy_raster, classify_raster)
            # resulting 'fixed' name
            mean = su.raster_properties(classify_raster, "MEAN")
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

        self.expected = {  # one cell differs from v1.
            1: 433,
            2: 6,
            3: 2428,
            4: 708
        }

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

            btm_model.main(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad, self.fine_outer_rad,
                config.zones_xml, zones_output)

            self.assertTrue(os.path.exists(zones_output))
            arcpy.BuildRasterAttributeTable_management(zones_output)

            self.xml_mean = su.raster_properties(zones_output, "MEAN")
            self.xml_zones = zones_output

            # some asserts here for validation
            rat = self.extractRasterAttributeTable(self.xml_zones)
            for (value, count) in self.expected.items():
                self.assertEqual(count, rat[value])

    def testModelExecuteWithExcel(self):
        with TempDir() as d:
            zones_output = os.path.join(d, 'output_zones.tif')
            arcpy.env.scratchWorkspace = d

            btm_model.main(
                d, config.bathy_raster, self.broad_inner_rad,
                self.broad_outer_rad, self.fine_inner_rad,
                self.fine_outer_rad, config.zones_excel, zones_output)

            self.assertTrue(os.path.exists(zones_output))
            arcpy.BuildRasterAttributeTable_management(zones_output)

            self.excel_mean = su.raster_properties(zones_output, "MEAN")
            self.excel_zones = zones_output
            # some asserts here for validation
            rat = self.extractRasterAttributeTable(self.excel_zones)
            for (value, count) in self.expected.items():
                self.assertEqual(count, rat[value])


class TestAddin(unittest.TestCase):
    """ test should be run after a fresh run of makeaddin to
        rebuild the .esriaddin file."""
    def setUp(self):
        self.addin_path = os.path.join(
            config.local_path, '..', '..', 'btm.esriaddin')
        self.addin_zip = zipfile.ZipFile(self.addin_path, 'r')

    def testToolboxIsPresent(self):
        toolbox_path = 'Install/toolbox/btm.pyt'
        self.assertTrue(toolbox_path in self.addin_zip.namelist())

    def testModelNameIsValid(self):
        """
        The signing process changes names to to URL encoded,
        make sure our model remains invariant.
        """
        model_name = 'Install/toolbox/btm_model.tbx'
        self.assertTrue(model_name in self.addin_zip.namelist())

    def testDataTypesModuleIsPresent(self):
        datatype_path = 'Install/toolbox/datatype/datatype.py'
        self.assertTrue(datatype_path in self.addin_zip.namelist())


class TestScaleComparison(unittest.TestCase):
    def setUp(self):
        self.percentile = 75
        self.min_nbhs = 3
        self.max_nbhs = 55

    def testPercentileMakesImage(self):
        with TempDir() as d:
            out_file = os.path.join(d, 'contact_sheet_per.png')
            scale_comparison.main(config.bathy_raster, 'percentile',
                                  self.percentile, self.min_nbhs,
                                  self.max_nbhs, out_file)
            self.assertTrue(os.path.exists(out_file))

    def testMedianMakesImage(self):
        with TempDir() as d:
            out_file = os.path.join(d, 'contact_sheet_med.png')
            scale_comparison.main(config.bathy_raster, 'median', None,
                                  self.min_nbhs, self.max_nbhs, out_file)
            self.assertTrue(os.path.exists(out_file))


class TestMultipleScales(unittest.TestCase):
    def setUp(self):
        self.in_raster = config.bathy_raster
        self.nbh_sizes = '3;13'
        self.metrics = "'Mean Depth';Variance;"\
                       "'Standard Deviation';'Terrain Ruggedness (VRM)';"\
                       "'Interquartile Range';Kurtosis"

    def testResultRastersProduced(self):
        with TempDir() as d:
            arcpy.ImportToolbox(config.pyt_file)
            arcpy.multiplescales_btm(self.in_raster,
                                     self.nbh_sizes, self.metrics, d)

            depth_stats = {
                'meandepth': -20.56248074571827,
                'stddevdepth': 0.2946229406453136,
                'vardepth': 0.1281792675921596,
                'iqrdepth': 0.44891918233769,
                'kurtosisdepth': -0.91233563683704
            }

            for (prefix, expected_value) in depth_stats.items():
                raster_path = os.path.join(
                    d, "{0}_{1:03d}.tif".format(prefix, 3))
                self.assertAlmostEqual(
                    su.raster_properties(raster_path, 'MEAN'), expected_value)

            vrm_raster = os.path.join(d, 'ruggedness_003.tif')
            self.assertAlmostEqual(
                su.raster_properties(vrm_raster, "MEAN"), 0.00062628513039036)
            self.assertAlmostEqual(
                su.raster_properties(vrm_raster, "STD"), 0.00087457748556755)

            rast_names = ['meandepth_003.tif', 'stddevdepth_003.tif',
                          'vardepth_003.tif', 'ruggedness_003.tif',
                          'meandepth_013.tif', 'stddevdepth_013.tif',
                          'vardepth_013.tif', 'ruggedness_013.tif',
                          'iqrdepth_003.tif', 'kurtosisdepth_003.tif',
                          'iqrdepth_013.tif', 'kurtosisdepth_013.tif']

            for each in rast_names:
                file_name = os.path.join(d, each)
                self.assertTrue(os.path.exists(file_name))

    def testLZWCompression(self):
        with TempDir() as d:
            arcpy.ImportToolbox(config.pyt_file)
            arcpy.multiplescales_btm(self.in_raster,
                                     self.nbh_sizes, self.metrics, d)
            rast_names = ['meandepth_003.tif', 'stddevdepth_003.tif',
                          'vardepth_003.tif', 'ruggedness_003.tif',
                          'meandepth_013.tif', 'stddevdepth_013.tif',
                          'vardepth_013.tif', 'ruggedness_013.tif',
                          'iqrdepth_003.tif', 'kurtosisdepth_003.tif',
                          'iqrdepth_013.tif', 'kurtosisdepth_013.tif']
            for each in rast_names:
                file_name = os.path.join(d, each)
                self.assertEqual(str(Raster(file_name).compressionType), 'LZW')


class TestACRModel2(unittest.TestCase):
    def setUp(self):
        self.in_raster = config.bathy_raster
        self.aoi = config.aoi
        self.aoi_multipart = config.aoi_multipart

    def testSinglePartResults(self):
        with TempDir() as d:
            arcpy.ImportToolbox(config.pyt_file)
            testaoi = os.path.join(d, 'testaoi.shp')
            arcpy.CopyFeatures_management(self.aoi, testaoi)
            arcpy.arcchordratio_btm(self.in_raster, testaoi, True)
            planarTIN = os.path.join(d, 'bathy5m_clip_planartin0')
            elevTIN = os.path.join(d, 'bathy5m_clip_elevationtin')
            self.assertTrue(os.path.exists(planarTIN))
            self.assertTrue(os.path.exists(elevTIN))
            self.assertEqual(len(arcpy.Describe(testaoi).fields), 8)
            with arcpy.da.SearchCursor(testaoi, '*') as cursor:
                expected = (0, (358083.9308262255, 4678265.0709908875),
                            0, 19972.5978495, 19917.1775893,
                            1.00278253583, 2.32867335011, 246.842790079)
                result = cursor.next()
                for x in range(2, len(expected)):
                    self.assertAlmostEqual(result[x], expected[x])

    def testMultipartResults(self):
        with TempDir() as d:
            arcpy.ImportToolbox(config.pyt_file)
            testaoi_mp = os.path.join(d, 'testaoi_mp.shp')
            arcpy.CopyFeatures_management(self.aoi_multipart, testaoi_mp)
            arcpy.arcchordratio_btm(self.in_raster, testaoi_mp, False)
            rows = int(arcpy.GetCount_management(testaoi_mp).getOutput(0))
            self.assertEqual(rows, 4)
            self.assertEqual(len(arcpy.Describe(testaoi_mp).fields), 9)
            with arcpy.da.SearchCursor(testaoi_mp, '*') as cursor:
                expected = (0, (358124.62825836154, 4678229.791685243),
                            0, 0, 1238.64248438, 1236.28701996,
                            1.00190527311, 5.3937886264, 225.726428217)
                result = cursor.next()
                for x in range(2, len(expected)):
                    self.assertAlmostEqual(result[x], expected[x])


if __name__ == '__main__':
    unittest.main()
