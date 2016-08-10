# ruggedness.py
# Description: This tool measures terrain ruggedness by calculating the
#              vector ruggedness measure (VRM) described in Sappington, J.M.,
#              K.M. Longshore, and D.B. Thompson. 2007. Quantifying Landscape
#              Ruggedness for Animal Habitat Analysis: A Case Study Using
#              Bighorn Sheep in the Mojave Desert. Journal of Wildlife
#              Management. 71(5): 1419 -1426.
# Requirements: Spatial Analyst
# Author: Mark Sappington
# Date: 2/1/2008
# Updated 12/1/2010 by Emily C. Huntley of the Massachusetts Office of
# Coastal Zone Management to run in ArcGIS 10.
# Updated 2012-2014 by Shaun Walbridge to improve performance, use idomatic code.

# Import system modules
import math
import os
import sys

import arcpy
from arcpy.sa import Aspect, Cos, Sin, Slope, Con, NbrRectangle, FocalStatistics

# local imports
from . import utils
from . import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(in_raster=None, neighborhood_size=None, out_raster=None):
    """
    Compute terrain ruggedness, using the vector ruggedness measure (VRM),
    as described in:

        Sappington et al., 2007. Quantifying Landscape Ruggedness for
        Animal Habitat Analysis: A Case Study Using Bighorn Sheep in the
        Mojave Desert. Journal of Wildlife Management. 71(5): 1419 -1426.
    """
    hood_size = int(neighborhood_size)

    # FIXME: expose this as an option per #18
    out_workspace = os.path.dirname(out_raster)
    utils.workspace_exists(out_workspace)
    # force temporary stats to be computed in our output workspace
    arcpy.env.scratchWorkspace = out_workspace
    arcpy.env.workspace = out_workspace

    # TODO expose as config
    pyramid_orig = arcpy.env.pyramid
    arcpy.env.pyramid = "NONE"
    # TODO: currently set to automatically overwrite, expose this as option
    arcpy.env.overwriteOutput = True

    try:
        # Create Slope and Aspect rasters
        utils.msg("Calculating aspect...")
        out_aspect = Aspect(in_raster)
        utils.msg("Calculating slope...")
        out_slope = Slope(in_raster, "DEGREE")

        # Convert Slope and Aspect rasters to radians
        utils.msg("Converting slope and aspect to radians...")
        slope_rad = out_slope * (math.pi / 180)
        aspect_rad = out_aspect * (math.pi / 180)

        # Calculate x, y, and z rasters
        utils.msg("Calculating x, y, and z rasters...")
        xy_raster_calc = Sin(slope_rad)
        z_raster_calc = Cos(slope_rad)
        x_raster_calc = Con(out_aspect == -1, 0, Sin(aspect_rad)) * xy_raster_calc
        y_raster_calc = Con(out_aspect == -1, 0, Cos(aspect_rad)) * xy_raster_calc

        # Calculate sums of x, y, and z rasters for selected neighborhood size
        utils.msg("Calculating sums of x, y, and z rasters in neighborhood...")
        hood = NbrRectangle(hood_size, hood_size, "CELL")
        x_sum_calc = FocalStatistics(x_raster_calc, hood, "SUM", "NODATA")
        y_sum_calc = FocalStatistics(y_raster_calc, hood, "SUM", "NODATA")
        z_sum_calc = FocalStatistics(z_raster_calc, hood, "SUM", "NODATA")

        # Calculate the resultant vector
        utils.msg("Calculating the resultant vector...")
        result_vect = (x_sum_calc**2 + y_sum_calc**2 + z_sum_calc**2)**0.5

        arcpy.env.rasterStatistics = "STATISTICS"
        arcpy.env.pyramid = pyramid_orig
        # Calculate the Ruggedness raster
        utils.msg("Calculating the final ruggedness raster...")
        ruggedness = 1 - (result_vect / hood_size**2)

        out_raster = utils.validate_path(out_raster)
        utils.msg("Saving ruggedness raster to to {}.".format(out_raster))
        ruggedness.save(out_raster)

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         neighborhood_size=sys.argv[2],
         out_raster=sys.argv[3])
