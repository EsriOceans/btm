# utils.py
# Shaun Walbridge, 2012.10.4
"""
A collection of utilities for modifying the environment, logging, and
handling BTM classification dictionaries.
"""

import locale
import sys
import traceback
import os
import csv
from xml.dom.minidom import parse

import arcpy
import config

# register the default locale
locale.setlocale(locale.LC_ALL, '')


def add_local_paths(paths):
    """Add a list of paths to the current import path."""
    for path_part in paths:
        base_path = os.path.join(config.local_path, path_part)
        abs_path = os.path.abspath(base_path)
        sys.path.insert(0, abs_path)


def msg(output, mtype='message'):
    """
    Context-sensitive messages. If running in a geoprocessing context,
    will use the native ArcPy methods, otherwise will send messages
    to standard out. Can handle errors, warnings and messages (default).
    """
    if mtype == 'error':
        exception_message = "{}: {}".format(type(output).__name__, output)
        arcpy_messages = arcpy.GetMessages()
        full_traceback = sys.exc_info()[2]
        tbinfo = traceback.format_tb(full_traceback)[0]
        if config.mode == 'script':
            # print the raw exception
            print exception_message
            # Arcpy and Python stuff, hopefully also helpful
            err_msg = "ArcPy Error: {msg_text}\nPython Error: ${tbinfo}".format(
                msg_text=arcpy_messages, tbinfo=tbinfo)
            print err_msg
        else:
            arcpy.AddError(exception_message)
            arcpy.AddError(arcpy_messages)
            arcpy.AddMessage("Python Error: {tbinfo}".format(tbinfo=tbinfo))
    elif config.mode == 'script':
        print output
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
    attr_obj = arcpy.GetRasterProperties_management(input_raster, attribute)
    attr_val = attr_obj.getOutput(0)
    numeric_attrs = ['MINIMUM', 'MAXIMUM', 'MEAN', 'STD', 'CELLSIZEX', 'CELLSIZEY']

    if config.debug:
        msg(locale.getlocale())

    if attribute in numeric_attrs:
        # convert these to locale independent floating point numbers
        value = locale.atof(attr_val)
    else:
        # leave anything else untouched
        value = attr_val
    return value


# classes
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
        self.filename = filename
        self.doctype = self._doctype()
        self.schema = self._get_schema()

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
        super(BtmXmlDocument, self).__init__()
        self.dom = parse(filename)
        self.node_dict = self.node_to_dict(self.dom)

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

    def get_text_from_node(self, node):
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

    def node_to_dict(self, node):
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
                text = self.get_text_from_node(n)
            except NotTextNodeError:
                if multiple:
                    # append to our list
                    multlist[n.nodeName].append(self.node_to_dict(n))
                    mapped_nodes.update({n.nodeName: multlist[n.nodeName]})
                    continue
                else:
                    # 'normal' node
                    mapped_nodes.update({n.nodeName: self.node_to_dict(n)})
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
        super(BtmExcelDocument, self).__init__()
        self.filename = filename
        self.header = None  # filled in by parse_workbook
        self.workbook = self.parse_workbook(self.filename)

    def name(self):
        return os.path.basename(self.filename)

    def description(self):
        # TODO: implement metadata in Excel?
        return None

    def classification(self):
        in_workbook = self.workbook
        result_rows = []
        for row in in_workbook:
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
            res_row = {'Class': str(int(class_code)),
                       'Zone': zone,
                       'SSB_LowerBounds': broad_lower,
                       'SSB_UpperBounds': broad_upper,
                       'LSB_LowerBounds': fine_lower,
                       'LSB_UpperBounds': fine_upper,
                       'Slope_LowerBounds': slope_lower,
                       'Slope_UpperBounds': slope_upper,
                       'Depth_LowerBounds': depth_lower,
                       'Depth_UpperBounds': depth_upper}
            result_rows.append(res_row)
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
                    result.append([sheet.cell(row, col).value for col in range(10)])
        return result


class BtmCsvDocument(BtmDocument):
    """
    A BTM CSV document. Requires an input CSV file, provides
    access to the formatted rows of the CSV, and header information.
    """
    def __init__(self, filename):
        super(BtmCsvDocument, self).__init__()
        self.filename = filename
        self.header = None  # filled in by parse_csv
        self.csv = self.parse_csv(self.filename)

    def name(self):
        return os.path.basename(self.filename)

    def description(self):
        # TODO: implement metadata in CSV dictionaries?
        return None

    def classification(self):
        in_csv = self.csv
        result_rows = []
        for row in in_csv:
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
            res_row = {
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
            }
            result_rows.append(res_row)
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
                self.header = in_csv.next()
            # everything but the header
            result = [r for r in in_csv]

        return result
