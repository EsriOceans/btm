# depth_statistics.py: compute depth statistics
# Requirements: Spatial Analyst
# Author: Shaun Walbridge
# Date: 9/1/2012

# Import system modules
import os
import sys

import arcpy
from arcpy.sa import NbrRectangle, FocalStatistics, Power

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(in_raster=None, neighborhood_size=None,
         out_workspace=None, out_stats_raw=None):
    """
    Compute depth statisitcs, averaging values over a defined neighborhood
    of cells. Can compute mean, standard deviation, and variance.
    """
    out_stats = out_stats_raw.replace("'", '').split(";")
    arcpy.env.rasterStatistics = "STATISTICS"

    # convert our data to sets for easy comparison
    mean_set = set(['Mean Depth'])
    std_dev_set = set(['Standard Deviation', 'Variance'])

    # list stats to be computed
    stats_msg = ("The following stats will be computed: "
                 "{}".format(";".join(out_stats)))
    utils.msg(stats_msg)

    try:
        # initialize our neighborhood
        utils.msg("Calculating neighborhood...")
        neighborhood = NbrRectangle(
            neighborhood_size, neighborhood_size, "CELL")

        if mean_set.intersection(out_stats):
            utils.msg("Calculating mean depth...")
            mean_depth = FocalStatistics(in_raster, neighborhood, "MEAN", "NODATA")
            mean_raster = os.path.join(out_workspace, "meandepth")
            utils.msg("saving mean depth to {}".format(mean_raster))
            mean_depth.save(mean_raster)

        # compute stdev in ths case
        if std_dev_set.intersection(out_stats):
            utils.msg("Calculating depth standard deviation...")
            std_dev_depth = FocalStatistics(in_raster, neighborhood, "STD", "NODATA")
            std_dev_raster = os.path.join(out_workspace, "stdevdepth")
            utils.msg("saving standard deviation depth to {}".format(std_dev_raster))
            std_dev_depth.save(std_dev_raster)

            # no direct variance focal stat, have to stdev^2
            if 'Variance' in out_stats:
                utils.msg("Calculating depth variance...")
                var_depth = Power(std_dev_depth, 2)
                var_raster = os.path.join(out_workspace, "vardepth")
                utils.msg("saving depth variance to {}".format(var_raster))
                var_depth.save(var_raster)

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         neighborhood_size=sys.argv[2],
         out_workspace=sys.argv[3],
         out_stats_raw=sys.argv[4])
