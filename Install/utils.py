# utils.py

# ported from work done by Jen Boulware at NOAA CSC, October 2011
# 
import os
from xml.dom.minidom import parse

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
        #parent = super(BtmXmlDocument, self).__init__()

        self.dom = parse(filename)
        #self.dom = parse(parent.filename)
        self.node_dict = self.nodeToDic(self.dom)

    def name(self):
        return self.node_dict['ClassDict']['PrjName']

    def description(self):
        return self.node_dict['ClassDict']['PRJDescription']

    def classification(self):
        # XXX: improve this to provide more direct access to the classes
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
    pass

class BtmCsvDocument(BtmDocument):
    pass
