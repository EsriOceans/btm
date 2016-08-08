# aspect.py
# Author: Shaun Walbridge
# Date: 2014-02-26

# Import system modules
import arcpy
import math
import sys
from arcpy.sa import Aspect, Sin, Cos

# local imports
import scripts.utils as utils
import scripts.config as config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(bathy=None, out_sin_raster=None, out_cos_raster=None):
    """
    Calculate the statistical aspect of a raster, which
    computes the sin(aspect) and cos(aspect). By using these two
    variables, aspect can be accounted for as a continuous circular
    variable. Because aspect is circular (0 and 359.9 are immediately
    adjacent), this trigonometric transformation preserves distances
    between elements and is the simplest transformation mechanism.
    """

    try:
        arcpy.env.compression = "LZW"
        arcpy.env.rasterStatistics = "STATISTICS"
        # Calculate the aspect of the bathymetric raster. "Aspect is expressed
        # in positive degrees from 0 to 359.9, measured clockwise from north."
        utils.msg("Calculating aspect...")
        aspect = Aspect(bathy)

        # Both the sin and cos functions here expect radians, not degrees.
        # convert our Aspect raster into radians, check that the values
        # are in range.
        aspect_rad = aspect * (math.pi / 180)

        aspect_sin = Sin(aspect_rad)
        aspect_cos = Cos(aspect_rad)

        out_sin_raster = utils.validate_path(out_sin_raster)
        out_cos_raster = utils.validate_path(out_cos_raster)
        arcpy.CopyRaster_management(aspect_sin, out_sin_raster)
        arcpy.CopyRaster_management(aspect_cos, out_cos_raster)
    except Exception as e:
        utils.msg(e, mtype='error')

# When executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(bathy=sys.argv[1],
         out_sin_raster=sys.argv[2],
         out_cos_raster=sys.argv[3])
