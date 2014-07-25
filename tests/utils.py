import os
import sys

import arcpy

from config import local_path

def add_local_paths(paths):
    for path_part in paths:
        base_path = os.path.join(local_path, path_part)
        abs_path = os.path.abspath(base_path)
        sys.path.insert(0, abs_path)

class Rast(object):
    def __init__(self, raster=None):
        self.path = raster
        if self.path is not None:
            self.raster = arcpy.sa.Raster(self.path)

    def __del__(self):
        if "name" in self.__dict__:
            self.__exit__(None, None, None)

    def __enter__(self):
        return self.raster

    def dissolve(self):
        if self.raster:
            del self.raster
        self.path = ""

    def __exit__(self, *errstuff):
        return self.dissolve()
