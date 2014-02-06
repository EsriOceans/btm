# bpi.py
# Description: The Benthic Terrain Modeler (BTM) functions as a toolbox
#              within ArcMap, and relies on a methodology to analyze benthic
#              terrain from input multibeam bathymetry in ESRI's GRID (raster)
#              format. The BTM toolbox contains a set of tools that allow
#              users to create grids of slope, bathymetric position index and
#              rugosity from an input data set.
#
#              An integrated XML-based terrain classification dictionary gives
#              users the freedom to create their own classifications and
#              definethe relationships that characterize them.
# Requirements: Spatial Analyst
# Authors: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
# Date: 2005
# Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal
# Zone Management to an ArcGIS 10 Python Script.
# Converted 9/6/2012 by Shaun Walbridge to a script that can be run from either
# a Python addin GUI, as a standard python script or from a toolbox.

import sys

import arcpy
from arcpy.sa import NbrAnnulus, Int, Plus, Minus, FocalStatistics

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def main(bathy=None, inner_radius=None, outer_radius=None,
    out_raster=None, bpi_type='broad', mode='toolbox'):

    try:
        # Create the broad-scale Bathymetric Position Index (BPI) raster
        msg = "Generating the {bpi_type}-scale ".format(bpi_type=bpi_type) + \
                "Bathymetric Position Index (BPI) raster..."
        utils.msg(msg)
        utils.msg("Calculating neighborhood...")
        neighborhood = NbrAnnulus(inner_radius, outer_radius, "CELL")
        utils.msg("Calculating FocalStatistics for {}...".format(bathy))
        out_focal_statistics = FocalStatistics(bathy, neighborhood, "MEAN")
        outRaster = Int(Plus(Minus(bathy, out_focal_statistics), 0.5))
        outRaster.save(out_raster)
        utils.msg("Saved output as {}".format(out_raster))
    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(
        bathy=sys.argv[1],
        inner_radius=sys.argv[2],
        outer_radius=sys.argv[3],
        out_raster=sys.argv[4],
        bpi_type=sys.argv[5])
