# depth_statistics_multiple.py
# Compute depth statistics at multiple scales
# Requirements: Spatial Analyst
# Author: Shaun Walbridge
# Date: 2015.04.01

# Import system modules
import os
import sys

import arcpy

# local imports
import scripts.utils as utils
import scripts.config as config
import scripts.depth_statistics as depth_statistics

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def main(in_raster=None, neighborhood_min=None, neighborhood_max=None,
         out_workspace=None, out_stats_raw=None):
    """
    Compute depth statisitcs, averaging values over a defined neighborhood
    of cells. Can compute mean, standard deviation, and variance.
    """
    arcpy.env.rasterStatistics = "STATISTICS"

    out_stats = out_stats_raw.replace("'", '').split(";")
    stat_rasters = {
        'Mean Depth': "meandepth",
        'Standard Deviation': "stddevdepth",
        'Variance': "vardepth"
    }

    # we want to compute the raster stats for each scale in the range we're given.
    # requirements: must be odd, minimum 3x3.
    n_min = int(neighborhood_min)
    n_max = int(neighborhood_max)

    input_err = None
    if n_min < 3:
        input_err = True
        err_msg = "Minimum window size is 3"
    if n_max <= n_min:
        input_err = True
        err_msg = "Maximum window size must be greater than minimum."
    if input_err:
        utils.msg(err_msg, mtype='error')
        sys.exit()

    # use an in-memory raster object for the input raster
    # NOTE: this may fail with lager rasters
    raster_init = arcpy.Raster(in_raster)
    raster_loc = "in_memory\\in_raster"
    try:
        raster_init.save(raster_loc)
    except:
        raster_loc = in_raster

    try:
        # TODO look at using in-mem outputs & doing this with numpy
        for window in range(n_min, n_max+1, 2):
            utils.msg("Computing depth statistics for {}x{} window".format(
                window, window))

            # run the calculation for the given depth window
            output_dir = os.path.join(out_workspace, "win_{0:03d}".format(window))
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            depth_statistics.main(
                in_raster=raster_loc,
                neighborhood_size=window,
                out_workspace=output_dir,
                out_stats_raw=out_stats_raw,
                verbose=True)

            # TODO for each of the rasters calculated, do:

        # Now, convert these into a TIME CUBE *queue spooky music*
        # XXX FIXME
        for raster_label in out_stats:
            stat_raster = stat_rasters[raster_label]

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         neighborhood_min=sys.argv[2],
         neighborhood_max=sys.argv[3],
         out_workspace=sys.argv[4],
         out_stats_raw=sys.argv[5])
