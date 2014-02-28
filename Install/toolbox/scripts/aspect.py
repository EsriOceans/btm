# aspect.py
# Author: Shaun Walbridge
# Date: 2014-02-26

# Import system modules
import arcpy
import math
import sys
from arcpy.sa import Aspect, Sin, Cos

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def main(bathy=None, out_sin_raster=None, out_cos_raster=None):
    try:
        arcpy.env.rasterStatistics = "STATISTICS"
        # Calculate the aspect of the bathymetric raster. "Aspect is expressed in 
        # positive degrees from 0 to 359.9, measured clockwise from north."
        utils.msg("Calculating aspect...")
        aspect = Aspect(bathy)

        # both the sin and cos functions here expect radians, not degrees.
        # convert our Aspect raster into radians, check that the values are in range.
        aspect_rad = aspect * (math.pi / 180)

        # because this statistic is circular (0 and 359.9 are immediately adjacent),
        # we need to transform this into a form which preserves distances between items.
        # trig is the simplest mechanism.
        aspect_sin = Sin(aspect_rad)
        aspect_cos = Cos(aspect_rad)

        out_sin_raster = utils.validate_path(out_sin_raster)
        out_cos_raster = utils.validate_path(out_cos_raster)
        aspect_sin.save(out_sin_raster)
        aspect_cos.save(out_cos_raster)
    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(bathy=sys.argv[1], out_sin_raster=sys.argv[2], out_cos_raster=sys.argv[3])
