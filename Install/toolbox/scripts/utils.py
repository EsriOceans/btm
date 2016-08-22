# utils.py
# Shaun Walbridge, 2012.10.4
"""
A collection of utilities for modifying the environment, logging, and
handling BTM classification dictionaries.
"""

from __future__ import absolute_import
import locale
import sys
import json
import numpy as np
import traceback
import os
import csv
import math
from xml.dom.minidom import parse
try:
    from netCDF4 import Dataset
    NETCDF4_EXISTS = True
except ImportError:
    NETCDF4_EXISTS = False
try:
    import scipy
    SCIPY_EXISTS = True
except ImportError:
    SCIPY_EXISTS = False

import arcpy
from arcpy import Raster
from . import config

from .tempdir import TempDir

# register the default locale
locale.setlocale(locale.LC_ALL, '')

# What kinds of inputs can we expect to compute statistics on?
# TODO add Mosaic Dataset, Mosaic Layer
VALID_RASTER_TYPES = ['RasterDataset', 'RasterLayer']


def msg(output, mtype='message'):
    """
    Context-sensitive messages. If running in a geoprocessing context,
    will use the native ArcPy methods, otherwise will send messages
    to standard out. Can handle errors, warnings and messages (default).
    """
    if mtype == 'error':
        output_type = type(output).__name__
        if output_type == 'str':
            exception_message = output
        else:
            exception_message = "{}: {}".format(type(output).__name__, output)
        arcpy_messages = arcpy.GetMessages()
        full_traceback = sys.exc_info()[2]
        if full_traceback:
            tbinfo = "".join(traceback.format_tb(full_traceback))
        else:
            tbinfo = '(None)'
        if config.mode == 'script':
            # print the raw exception
            print(exception_message)
            # Arcpy and Python stuff, hopefully also helpful
            err_msg = "ArcPy Error: {msg_text}\nPython Error: ${tbinfo}".format(
                msg_text=arcpy_messages, tbinfo=tbinfo)
            print(err_msg)
        else:
            arcpy.AddError(exception_message)
            arcpy.AddError(arcpy_messages)
            arcpy.AddMessage("Python Error: {tbinfo}".format(tbinfo=tbinfo))
    elif config.mode == 'script':
        print(output)
    else:
        if mtype == 'message':
            arcpy.AddMessage(output)
        elif mtype == 'warning':
            arcpy.AddWarning(output)


def workspace_exists(directory):
    """
    Ensure workspace exists.

    Arguments:
        directory -- path to test for existence.

    Returns:
        boolean for existence.
    """
    if os.path.isdir(directory):
        exists = True
    else:
        exists = False
        err_msg = "Output `{}` workspace doesn't exist".format(directory)
        msg(err_msg, mtype='error')
    return exists


def validate_path(path):
    """
    If our path contains a DB name, make sure we have a valid DB name
    and not a standard file name.
    """
    dirname, file_name = os.path.split(path)
    file_base = os.path.splitext(file_name)[0]
    if dirname == '':
        # a relative path only, relying on the workspace
        dirname = arcpy.env.workspace
    path_ext = os.path.splitext(dirname)[1].lower()
    if path_ext in ['.mdb', '.gdb', '.sde']:
        # we're working in a database
        file_name = arcpy.ValidateTableName(file_base)
        if file_name != file_base:
            msg("Warning: renamed output table to {}".format(file_name))
    validated_path = os.path.join(dirname, file_name)
    return validated_path


def save_raster(raster, path):
    """Save input raster object to path, and return raster reference."""
    path = validate_path(path)
    raster.save(path)
    return arcpy.sa.Raster(path)


def raster_properties(input_raster, attribute='MEAN'):
    """ Wrapper for GetRasterProperties_management which does the right thing."""

    input_raster_path = None
    if input_raster is not None:
        try:
            raster_desc = arcpy.Describe(input_raster)
            if config.debug:
                msg("raster type: {}\n".format(raster_desc.dataType))
            if raster_desc.dataType in VALID_RASTER_TYPES:
                input_raster_path = raster_desc.catalogPath
                if config.debug:
                    msg("raster path {}\n".format(input_raster_path))
        except:
            value = None

    if input_raster_path:
        # make sure statistics exist, set them if they don't.
        arcpy.CalculateStatistics_management(
            input_raster_path, "1", "1", "#", "SKIP_EXISTING")

        attr_obj = arcpy.GetRasterProperties_management(
            input_raster_path, attribute)
        """
        if config.debug:
            with open("C:\\temp\\btm.log", 'w') as f:
                f.write("{}:{}\n".format(input_raster_path, attribute))
                f.write("{}\n".format(attr_obj))
                f.write("{}\n".format(locale.getlocale()))
                pr = str(attr_obj.getOutput(0))
                f.write("{}\n".format(pr))
                try:
                    f.write("{}\n".format(locale.atof(pr)))
                except:
                    f.write("atof caused exception.")
        """
        attr_val = attr_obj.getOutput(0)
        numeric_attrs = ['MINIMUM', 'MAXIMUM', 'MEAN',
                         'STD', 'CELLSIZEX', 'CELLSIZEY']
        if config.debug:
            msg(locale.getlocale())

        if attribute.upper() in numeric_attrs:
            # convert these to locale independent floating point numbers

            if sys.version_info < (3, 0):
                # py2 locale.* doesn't actually support Unicode. convert.
                attr_val = str(attr_val)

            value = locale.atof(attr_val)

        else:
            # leave anything else untouched
            value = attr_val
    if config.debug:
        msg("final raster value: {}\n".format(value))

    return value


def arcgis_platform():
    """ ArcGIS platform details used internally."""
    info = arcpy.GetInstallInfo()
    install_dir = info['InstallDir']
    arc_version = info['Version']
    if info['ProductName'] == 'ArcGISPro':
        product = 'Pro'
    else:
        # there are other levels, but this is a PYT run from toolbox,
        # so unlikely to be a non-ArcMap context
        product = 'Desktop'
    return (install_dir, arc_version, product)


# classes
class Workspace(object):
    """Create a workspace location that can be modified with the 'set workspace'
    tool, and allows us to use a consistent location for our results. Currently,
    a JSON file which just stores one value, but laid out to allow later refactoring
    to support a full set of configuration settings."""

    # TODO: this is a placeholder class, it doesn't take advantage of the
    #       utility of JSON, and requries syncing state from disk on every access.

    def __init__(self, data=None):
        if data and isinstance(data, dict):
            self.data = data

    @property
    def file_path(self):
        # Place output into 'toolbox' directory. This should work on both
        # the add-in and the toolbox versions.
        base_path = os.path.abspath(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, 'workspace.json')

    @property
    def path(self):
        """ Path of the workspace."""
        ws_path = None
        d = self.data
        if d and "workspace" in d:
            ws_path = d["workspace"]
        return ws_path

    @path.setter
    def path(self, val):
        current = self.data
        if current:
            current["workspace"] = val
        else:
            current = {'workspace': val}
        self.data = current

    @property
    def exists(self):
        status = False
        if self.path and os.path.exists(self.path):
            status = True
        return status

    @property
    def is_gdb(self):
        gdb = False
        path = self.path
        if path and '.gdb' in path.lower():
            gdb = True
        return gdb

    @property
    def data(self):
        d = None
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                try:
                    d = json.load(f)
                except ValueError:
                    # no valid JSON
                    pass
        return d

    @data.setter
    def data(self, val):
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except:
                # delete failed, cowardly pass
                pass

        with open(self.file_path, 'w') as f:
            json.dump(val, f)

    def default_filename(self, input_name):
        name = None
        if self.exists:
            if self.is_gdb:
                # remove any file extension for GDB outputs
                input_name = os.path.splitext(input_name)[0]
            name = os.path.join(self.path, input_name)
        return name


class BlockProcessor:

    def __init__(self, fileIn):
        self.fileIn = Raster(fileIn)
        self.width = self.fileIn.width
        self.height = self.fileIn.height
        self.noData = self.fileIn.noDataValue
        arcpy.env.outputCoordinateSystem = self.fileIn
        arcpy.env.overwriteOutput = True

    def computeBlockStatistics(self, func, blockSize, outRast, overlap=0):
        # immediately fail if we don't have a netCDF4 backend available:
        if not NETCDF4_EXISTS:
            return None

        total_blocks = int(math.ceil(float(self.width) / blockSize) *
                           math.ceil(float(self.height) / blockSize))
        verbose = total_blocks > 1
        if verbose:
            msg("Beginning block analysis...")
        with TempDir() as d:
            # generate random integers to prevent decimal place in name
            # use sampling without replacement to preclude collision
            rands = np.random.choice(2**16, size=2, replace=False)

            inNetCDF = os.path.join(d, '{}.nc'.format(rands[0]))
            arcpy.RasterToNetCDF_md(self.fileIn, inNetCDF, r"Band1")
            inFile = Dataset(inNetCDF, mode="a")
            inDepth = inFile.variables['Band1']

            outNetCDF = os.path.join(d, '{}.nc'.format(rands[1]))
            arcpy.RasterToNetCDF_md(self.fileIn, outNetCDF, r"Band1")
            outFile = Dataset(outNetCDF, mode="a")
            outDepth = outFile.variables['Band1']
            # Initialize entire output matrix to the No Data value --
            # the blocking code will write out the blocks which it
            # processes, setting these cells as it goes along. Doing this
            # avoids problems with the edge cells (issue #128).
            outDepth[:, :] = np.ones((self.width, self.height)) * self.noData

            bnum = 0
            x = 0
            while x < self.width:
                y = 0
                while y < self.height:
                    if verbose:
                        msg("Processing block {} of {} in {}..."
                            .format(bnum+1, total_blocks, self.fileIn.name))
                    ncols = blockSize + overlap*2
                    nrows = blockSize + overlap*2
                    if (x+ncols) >= self.width:
                        ncols = self.width - x
                    if (y+nrows) >= self.height:
                        nrows = self.height - y
                    syh = y + nrows
                    sxh = x + ncols
                    iyl = y + overlap
                    iyh = y + nrows - overlap
                    ixl = x + overlap
                    ixh = x + ncols - overlap
                    block = inDepth[y:syh, x:sxh]
                    block = func(block, overlap)
                    outDepth[iyl:iyh, ixl:ixh] = block
                    bnum += 1
                    y += blockSize
                x += blockSize

            outFile.close()
            inFile.close()

            msg("Creating result raster layer...")
            layerName = os.path.splitext(os.path.split(outRast)[1])[0]

            arcpy.MakeNetCDFRasterLayer_md(outNetCDF, 'Band1',
                                           'x', 'y', layerName)
            msg("Saving result layer to {}...".format(outRast))
            arcpy.CopyRaster_management(layerName, outRast)


class NotTextNodeError(Exception):
    """Override default handling of 'not text' by minidom."""
    def __init__(self):
        pass


class BtmDocument(object):
    """
    A wrapper class for handling any kind of BTM Classification file.
    The actual parsing happens in other classes, but this way we can keep
    a consistent method to access the data regardless of the input file type.
    """
    def __init__(self, filename):
        self._filename = filename
        self._doctype = self._doctype()
        self._schema = self._get_schema()

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = val

    @property
    def doctype(self):
        return self._doctype

    @property
    def schema(self):
        return self._schema

    def _doctype(self):
        """Map of 'known' extensions to filetypes."""
        # don't bother with a more formal mimetyping for now.
        known_types = {
            '.csv': 'CSV',
            '.xls': 'Excel',
            '.xlsx': 'Excel',
            '.xml': 'XML'
        }
        ext = os.path.splitext(self.filename)[1].lower()
        if ext in known_types:
            dtype = known_types[ext]
        else:
            raise TypeError("Invalid document type for {}".format(self.filename))
        return dtype

    def _get_schema(self):
        """Map file types to their respective classes."""
        schema_map = {
            'CSV': 'BtmCsvDocument',
            'Excel': 'BtmExcelDocument',
            'XML': 'BtmXmlDocument'
        }
        if self.doctype in schema_map:
            schema_name = schema_map[self.doctype]
        # do some introspection to pull in the class, based on the document
        # type provided.
        schema = globals()[schema_name]
        return schema(self.filename)

    # push up methods contained within our subclasses
    def name(self):
        """Project name"""
        return self.schema.name()

    def description(self):
        """Project description"""
        return self.schema.description()

    def classification(self):
        """Classification dictionary"""
        return self.schema.classification()


class BtmXmlDocument(BtmDocument):
    """
    Create an XML class for storing document attributes. Code ported
    from earlier work done by Jen Boulware / NOAA CSC, Oct 2011.
    """
    def __init__(self, filename):
        self._dom = parse(filename)
        self._node_dict = self._node_to_dict(self.dom)

    @property
    def dom(self):
        return self._dom

    @property
    def node_dict(self):
        return self._node_dict

    def name(self):
        return self.node_dict['ClassDict']['PrjName']

    def description(self):
        return self.node_dict['ClassDict']['PRJDescription']

    def classification(self):
        # TODO: improve this to provide more direct access to the classes
        # currently returns a list of dictionaries, each one with a key:val pair;
        # would be useful to just have a header row, and map the names
        # from the header
        return self.node_dict['ClassDict']['Classifications']['ClassRec']

    def _get_text_from_node(self, node):
        """ Scans through all children of node and gathers the text."""
        text = ""
        empty_node = node.hasChildNodes()
        if empty_node:
            for n in node.childNodes:
                if n.nodeType == n.TEXT_NODE:
                    text += n.nodeValue
                else:
                    raise NotTextNodeError
        else:
            text = None
        return text

    def _node_to_dict(self, node):
        """ Map node elements to a dictionary of actual values."""
        mapped_nodes = {}
        # holds temporary lists where there are multiple children
        multlist = {}
        multiple = 0
        for n in node.childNodes:
            if n.nodeType != n.ELEMENT_NODE:
                continue
            # find out if there are multiple records
            if len(node.getElementsByTagName(n.nodeName)) > 1:
                multiple = 1
                # and set up the list to hold the values
                if n.nodeName not in multlist:
                    multlist[n.nodeName] = []
            try:
                # text node
                text = self._get_text_from_node(n)
            except NotTextNodeError:
                if multiple:
                    # append to our list
                    multlist[n.nodeName].append(self._node_to_dict(n))
                    mapped_nodes.update({n.nodeName: multlist[n.nodeName]})
                    continue
                else:
                    # 'normal' node
                    mapped_nodes.update({n.nodeName: self._node_to_dict(n)})
                    continue
            # text node
            if multiple:
                multlist[n.nodeName].append(text)
                mapped_nodes.update({n.nodeName: multlist[n.nodeName]})
            else:
                mapped_nodes.update({n.nodeName: text})
        return mapped_nodes


class BtmExcelDocument(BtmDocument):
    """
    A BTM Excel document. Requires an input Excel spreadsheet, provides
    access to the formatted rows of the workbook, and header information.
    Assumes the data we're interested in is in the first workbook.
    """
    # TODO: FORCE A TEST FOR ARCGIS 10.2 INSTALLATION

    def __init__(self, filename):
        self.filename = filename
        self.header = None  # filled in by parse_workbook
        self.workbook = self.parse_workbook(self.filename)

    def name(self):
        return os.path.basename(self.filename)

    def description(self):
        # TODO: implement metadata in Excel?
        return None

    def classification(self):
        result_rows = []
        for row in self.workbook:
            # replace empty strings with Nones
            row_clean = [None if x == '' else x for x in row]

            if len(row_clean) != 10:
                message = ("Encountered malformed row which requires ",
                           "correction: \"{}\"".format(",".join(row)))
                raise ValueError(message)
            # don't parse the header, assume columns are in expected order.
            (class_code, zone, broad_lower, broad_upper, fine_lower, fine_upper,
             slope_lower, slope_upper, depth_lower, depth_upper) = row_clean

            # for now: fake the format used by the XML documents.
            result_rows.append({
                'Class': str(int(class_code)),
                'Zone': zone,
                'SSB_LowerBounds': broad_lower,
                'SSB_UpperBounds': broad_upper,
                'LSB_LowerBounds': fine_lower,
                'LSB_UpperBounds': fine_upper,
                'Slope_LowerBounds': slope_lower,
                'Slope_UpperBounds': slope_upper,
                'Depth_LowerBounds': depth_lower,
                'Depth_UpperBounds': depth_upper
            })
        return result_rows

    def parse_workbook(self, filename):
        """
        Parse an Excel workbook into a datatable useable
        by the classification tools.
        """
        result = []
        try:
            import xlrd
        except ImportError:
            err_msg = ("Reading Excel files requires the `xlrd` library, ",
                       "which is included in ArcGIS 10.2+. If you'd like ",
                       "Excel support in ArcGIS 10.1, please install the ",
                       "Python library `xlrd` manually.")
            raise Exception(err_msg)

        with xlrd.open_workbook(filename) as workbook:
            # assume data is in the first sheet
            sheet = workbook.sheet_by_index(0)

            # FIXME: assume all column labels are fixed
            self.header = [
                'Class', 'Zone', 'bpi_broad_lower', 'bpi_broad_upper',
                'bpi_fine_lower', 'bpi_fine_upper', 'slope_lower',
                'slope_upper', 'depth_lower', 'depth_upper'
            ]
            for row in range(2, sheet.nrows):
                cell = sheet.cell(row, 0)
                # an empty row terminates the set
                if cell.value in ["", None]:
                    break
                # we have an expected row of classes.
                else:
                    result.append(
                        [sheet.cell(row, col).value for col in range(10)])
        return result


class BtmCsvDocument(BtmDocument):
    """
    A BTM CSV document. Requires an input CSV file, provides
    access to the formatted rows of the CSV, and header information.
    """
    def __init__(self, filename):
        self.filename = filename
        self.header = None  # filled in by parse_csv
        self.csv = self.parse_csv(self.filename)

    def name(self):
        return os.path.basename(self.filename)

    def description(self):
        # TODO: implement metadata in CSV dictionaries?
        return None

    def classification(self):
        result_rows = []
        for row in self.csv:
            # replace empty strings with Nones
            row_clean = [None if x == '' else x for x in row]

            if len(row_clean) != 10:
                message = ("Encountered malformed row which requires ",
                           "correction: \"{}\"".format(",".join(row)))
                raise ValueError(message)
            # don't parse the header, assume columns are in expected order.
            (class_code, zone, broad_lower, broad_upper, fine_lower, fine_upper,
             slope_lower, slope_upper, depth_lower, depth_upper) = row_clean

            # for now: fake the format used by the XML documents.
            result_rows.append({
                'Class': class_code,
                'Zone': zone,
                'SSB_LowerBounds': broad_lower,
                'SSB_UpperBounds': broad_upper,
                'LSB_LowerBounds': fine_lower,
                'LSB_UpperBounds': fine_upper,
                'Slope_LowerBounds': slope_lower,
                'Slope_UpperBounds': slope_upper,
                'Depth_LowerBounds': depth_lower,
                'Depth_UpperBounds': depth_upper
            })
        return result_rows

    def parse_csv(self, filename):
        """
        Use csv.Sniffer() to determine the type of CSV we're reading,
        return a list of rows based on the detected CSV dialect.
        """
        result = None

        with open(filename, 'r') as csv_f:
            # Use the sniffer to figure out what kind of input we're getting
            sample = csv_f.read(1024)
            csv_f.seek(0)
            sniff_obj = csv.Sniffer()
            try:
                dialect = sniff_obj.sniff(sample)
                has_header = sniff_obj.has_header(sample)
            except csv.Error:
                # If the CSV is malformed (e.g. a missing ',' in a row),
                # this error can be raised. In that case, we shouldn't
                # give up, but instead just set the default dialect and
                # assume a header.
                dialect = "excel"
                has_header = True

            # read in CSV, respecting the detected dialect
            in_csv = csv.reader(csv_f, dialect)
            if has_header:
                self.header = next(in_csv)
            # everything but the header
            result = [r for r in in_csv]

        return result
