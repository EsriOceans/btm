# standardize_bpi_grids.py
# Description: The Benthic Terrain Modeler (BTM) functions as a toolbox
#              within ArcMap, and relies on a methodology to analyze benthic
#              terrain from input multibeam bathymetry in ESRI's GRID (raster)
#              format. The BTM toolbox contains a set of tools that allow users
#              to create grids of slope, bathymetric position index and
#              rugosity from an input data set.  An integrated XML-based
#              terrain classification dictionary gives users the freedom to
#              create their own classifications and define the relationships
#              that characterize them.
# Requirements: Spatial Analyst
# Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
# Date: 2005
# Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of
# Coastal Zone Management to a Python Script that runs in ArcGIS 10.

# Import system modules
import sys, arcpy
from arcpy.sa import Int, Plus, Divide, Minus, Times

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def main(bpi_raster=None, out_raster=None):
    try:
        # Get raster properties
        message = "Calculating properties of the Bathymetric " + \
                "Position Index (BPI) raster..."
        utils.msg(message)
        utils.msg("raster: {}; output: {}".format(bpi_raster, out_raster))
        bpi_mean = utils.raster_properties(bpi_raster, "MEAN")
        utils.msg("BPI raster mean: {}.".format(bpi_mean))
        bpi_std_dev = utils.raster_properties(bpi_raster, "STD")
        utils.msg("BPI raster standard deviation: {}.".format(bpi_std_dev))

        # Create the standardized Bathymetric Position Index (BPI) raster
        message = "Standardizing the Bathymetric Position Index (BPI) raster..."
        utils.msg(message)
        outRaster = Int(Plus(Times(Divide(
                Minus(bpi_raster, float(bpi_mean)), float(bpi_std_dev)), 100), 0.5))
        outRaster.save(out_raster)

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(bpi_raster=sys.argv[1], out_raster=sys.argv[2])
