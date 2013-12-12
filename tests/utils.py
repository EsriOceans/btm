import os
import sys

import arcpy

from config import *

def addLocalPaths(paths):
    for path_part in paths:
        base_path = os.path.join(local_path, path_part)
        abs_path = os.path.abspath(base_path)
        sys.path.insert(0, abs_path)

def raster_properties(input_raster, attribute='MEAN'):
    """ Wrapper for GetRasterProperties_management which does the right thing."""   
    attr_object = arcpy.GetRasterProperties_management(input_raster, attribute)
    return float(attr_object.getOutput(0))
 
