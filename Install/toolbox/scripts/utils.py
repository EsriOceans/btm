# utils.py
# Shaun Walbridge, 2012.10.4

# XML work ported from work done by Jen Boulware at NOAA CSC, October 2011

import sys
import traceback
import os
import csv
from xml.dom.minidom import parse

import arcpy
import config

def addLocalPaths(paths):
    for path_part in paths:
        base_path = os.path.join(local_path, path_part)
        abs_path = os.path.abspath(base_path)
        sys.path.insert(0, abs_path)

def msg(output_msg, mtype='message'):
    if mtype == 'error':
        arcpy_messages = arcpy.GetMessages()
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        if config.mode == 'script':
            # print the raw exception
            print output_msg
            # Arcpy and Python stuff, hopefully also helpful
            err_msg = "ArcPy Error: {msg_text}\nPython Error: ${tbinfo}".format(
                msg_text=arcpy_messages, tbinfo=tbinfo)
        else:
            arcpy.AddError(output_msg)
            arcpy.AddError(arcpy_messages)
            arcpy.AddMessage("Python Error: ${tbinfo}".format(tbinfo=tbinfo))
    elif config.mode == 'script':
        print output_msg
    else:
        if mtype == 'message':
            arcpy.AddMessage(output_msg)
        elif mtype == 'warning':
            arcpy.AddWarning(output_msg)

# override default handling of the XML DOM
class NotTextNodeError:
    pass

class BtmDocument(object):
    """ A wrapper class for handling any kind of BTM Classification file.
    The actual parsing happens in other classes, but this way we can keep
    a consistent method to access the data regardless of the input file type.
    """
    def __init__(self, filename):
        self.filename = filename
        self.doctype = self._doctype()
        self.schema = self._get_schema()

    def _doctype(self):
        # map of 'known' extensions to filetypes. don't bother with
        # a more formal mimetyping for now.
        known_types = {
            '.csv' : 'CSV',
            '.xls' : 'Excel',
            '.xlsx': 'Excel',
            '.xml': 'XML'
        }
        ext = os.path.splitext(self.filename)[1].lower()
        if known_types.has_key(ext):
            dtype = known_types[ext]
        else:
            raise UnknownType
        return dtype

    def _get_schema(self):
        """ map file types to their respective classes. """
        schema_map = {
            'CSV' : 'BtmCsvDocument',
            'Excel' : 'BtmExcelDocument',
            'XML' : 'BtmXmlDocument'
        }
        if schema_map.has_key(self.doctype):
            schema_name = schema_map[self.doctype]
        # do some introspection to pull in the class, based on the document
        # type provided.
        schema = globals()[schema_name]
        return schema(self.filename)

    # push up methods contained within our subclasses
    def name(self):
        return self.schema.name()

    def description(self):
        return self.schema.description()

    def classification(self):
        return self.schema.classification()


# override default handling of 'not text' by minidom
class NotTextNodeError:
    pass

class BtmXmlDocument(BtmDocument):
    def __init__(self, filename):
        self.dom = parse(filename)
        self.node_dict = self.nodeToDic(self.dom)

    def name(self):
        return self.node_dict['ClassDict']['PrjName']

    def description(self):
        return self.node_dict['ClassDict']['PRJDescription']

    def classification(self):
        # XXX: improve this to provide more direct access to the classes
        # currently returns a list of dictionaries, each one with a key:val pair;
        # would be useful to just have a header row, and map the names
        # from the header
        return self.node_dict['ClassDict']['Classifications']['ClassRec']

    def getTextFromNode(self, node):
        """
        scans through all children of node and gathers the
        text. 
        """
        t = ""
        emptyNode = node.hasChildNodes()
        if emptyNode:
            for n in node.childNodes:
                if n.nodeType == n.TEXT_NODE:
                    t += n.nodeValue
                else:
                    raise NotTextNodeError
        else:
            t = None
        return t

    def nodeToDic(self, node):
        dic = {}
        multlist = {} # holds temporary lists where there are multiple children
        multiple = 0
        for n in node.childNodes:
            if n.nodeType != n.ELEMENT_NODE:
                continue
            # find out if there are multiple records
            if len(node.getElementsByTagName(n.nodeName)) > 1:
                multiple = 1
                # and set up the list to hold the values
                if not multlist.has_key(n.nodeName):
                    multlist[n.nodeName] = []
            try:
                # text node
                text = self.getTextFromNode(n)
            except NotTextNodeError:
                if multiple:
                    # append to our list
                    multlist[n.nodeName].append(self.nodeToDic(n))
                    dic.update({n.nodeName:multlist[n.nodeName]})
                    continue
                else:
                    # 'normal' node
                    dic.update({n.nodeName:self.nodeToDic(n)})
                    continue
            # text node
            if multiple:
                multlist[n.nodeName].append(text)
                dic.update({n.nodeName:multlist[n.nodeName]})
            else:
                dic.update({n.nodeName:text})
        return dic

class BtmExcelDocument(BtmDocument):
    # reuse existing implementation in parsepy.py
    # TODO: fix for 3.1: https://github.com/EsriOceans/btm/issues/28
    pass

class BtmCsvDocument(BtmDocument):
    def __init__(self, filename):
        self.filename = filename
        self.header = None # filled in by parse_csv
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
                    
            # don't parse the header, assume columns are in expected order.
            (class_code, zone, broad_lower, broad_upper, fine_lower, fine_upper, \
            slope_lower, slope_upper, depth_lower, depth_upper) = row_clean
           
            # for now: fake the format used by the XML documents.
            res_row = {'Class': class_code, 
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

    def parse_csv(self, filename):
        result = None
        with open(filename, 'r') as f:
            # Use the sniffer to figure out what kind of input we're getting
            sample = f.read(1024)
            f.seek(0)
            sniff_obj = csv.Sniffer()
            dialect = sniff_obj.sniff(sample)
            has_header = sniff_obj.has_header(sample)

            # read in CSV, respecting the detected dialect
            in_csv = csv.reader(f, dialect)

            if has_header:
                self.header = in_csv.next()

            # everything but the header
            result = [r for r in in_csv]
        return result
