# package.py: update version information.
# -*- coding: utf-8 -*-

import os
import sys

import datetime
import dateutil.parser
import xml.etree.ElementTree as et

# specify the XML namespace
XMLNS = "http://schemas.esri.com/Desktop/AddIns"


class CommentedTreeBuilder(et.XMLTreeBuilder):
    """Retain comments when manipulating the XML."""
    def __init__(self, html=0, target=None):
        et.XMLTreeBuilder.__init__(self, html, target)
        self._parser.CommentHandler = self.handle_comment

    def handle_comment(self, data):
        self._target.start(et.Comment, {})
        self._target.data(data)
        self._target.end(et.Comment)


def ns_find(root, element):
    ns_string = '{{{0}}}{1}'.format(XMLNS, element)
    return root.find(ns_string)


def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

if len(sys.argv) < 2:
    print "Update package configuration\nUsage: {0} <version>".format(sys.argv[0])
    sys.exit()
else:
    update_version = sys.argv[1]

# config.xml, at the root level of the project contains settings for the add-in.
xml_path = "config.xml"
config_file = os.path.join(xml_path)

tree = et.parse(config_file, parser=CommentedTreeBuilder())
root = tree.getroot()

software_version = ns_find(root, 'Version')
release_date = ns_find(root, 'Date')

print software_version.text
print release_date.text

today = datetime.date.today()
parsed_date = dateutil.parser.parse(release_date.text).date()

# update attributes
release_date.text = today.strftime("%m/%d/%Y")
software_version.text = update_version

# register our namespace so we have a valid output namespace
et.register_namespace('', XMLNS)
root.attrib = {'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"}

"""
tree.write(xml_path, default_namespace=XMLNS)
indent(root)

print et.dump(root)
"""

tree.write(xml_path, pretty_print=True)

"""
                mod_time = esri.find('ModTime')
                if mod_date is not None:
                    esri.remove(mod_date)
                if mod_time is not None:
                    esri.remove(mod_time)
                tree.write(xml_path)
"""
