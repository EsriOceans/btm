# slope.py
# Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within
#              ArcMap, and relies on a methodology to analyze benthic terrain
#              from input multibeam bathymetry in ESRI's GRID (raster) format.
#              The BTM toolbox contains a set of tools that allow users to
#              create grids of slope, bathymetric position index and rugosity
#              from an input data set.  An integrated XML-based terrain
#              classification dictionary gives users the freedom to create
#              their own classifications and define the relationships that
#              characterize them.
# Requirements: Spatial Analyst
# Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
# Date: 2005
# Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of
# Coastal Zone Management to a Python Script that runs in ArcGIS 10.

# Import system modules
import sys

import arcpy
from arcpy.sa import Slope

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(bathy=None, out_raster=None):
    """Compute raster slope in degrees."""

    try:
        arcpy.env.rasterStatistics = "STATISTICS"
        # Calculate the slope of the bathymetric raster
        utils.msg("Calculating the slope...")
        out_slope = Slope(bathy, "DEGREE", 1)
        out_raster = utils.validate_path(out_raster)
        out_slope.save(out_raster)
    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(bathy=sys.argv[1], out_raster=sys.argv[2])
