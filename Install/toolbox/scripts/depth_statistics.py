# depth_statistics.py: compute depth statistics
# Requirements: Spatial Analyst
# Author: Shaun Walbridge
# Date: 9/1/2012

# Import system modules
import os
import sys
import math
import numpy as np
try:
    import scipy
    from scipy import stats
except ImportError:
    pass    # error generated inline
import arcpy
from arcpy.sa import NbrRectangle, FocalStatistics, Power

# local imports
import scripts.utils as utils
import scripts.config as config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def iqr(in_array, overlap):
    s = in_array.shape
    nbh_list = []
    for r in range(0, (overlap*2)+1):
        for c in range(0, (overlap*2)+1):
            nbh_list.append(in_array[r:(s[0]-(overlap*2)+r),
                                     c:(s[1]-(overlap*2)+c)])
    iqr_array = np.array(nbh_list)
    iqr_array = np.percentile(iqr_array, 75, axis=0) - \
                np.percentile(iqr_array, 25, axis=0)
    return iqr_array


def kurtosis(in_array, overlap):
    s = in_array.shape
    nbh_list = []
    for r in range(0, (overlap*2)+1):
        for c in range(0, (overlap*2)+1):
            nbh_list.append(in_array[r:(s[0]-(overlap*2)+r),
                                     c:(s[1]-(overlap*2)+c)])
    kurt_array = np.array(nbh_list)
    kurt_array = scipy.stats.kurtosis(kurt_array, axis=0)
    return kurt_array


def main(in_raster=None, neighborhood_size=None,
         out_workspace=None, out_stats_raw=None, verbose=True):
    """
    Compute depth statisitcs, averaging values over a defined neighborhood
    of cells. Can compute mean, standard deviation, and variance.
    """
    out_stats = out_stats_raw.replace("'", '').split(";")
    out_stats = list(set(out_stats)-set(['Terrain Ruggedness (VRM)']))
    arcpy.env.rasterStatistics = "STATISTICS"
    arcpy.env.compression = 'LZW'  # compress output rasters

    # convert our data to sets for easy comparison
    mean_set = set(['Mean Depth'])
    std_dev_set = set(['Standard Deviation', 'Variance'])
    iqr_set = set(['Interquartile Range'])
    kurt_set = set(['Kurtosis'])

    # list stats to be computed
    if verbose:
        utils.msg("The following stats will be computed: " +
                  "{}".format(";".join(out_stats)))

    # these two tools both use block processing which requires NetCDF4
    if 'Interquartile Range' in out_stats or 'Kurtosis' in out_stats:
        if not utils.NETCDF4_EXISTS:
            utils.msg("The interquartile range and kurtosis tools require "
                      "the NetCDF4 Python library is installed. NetCDF4 "
                      "is included in ArcGIS 10.3 and later.", "error")
            return

        if 'Kurtosis' in out_stats and not utils.SCIPY_EXISTS:
            utils.msg("The kurtosis calculation requires the SciPy library "
                      "is installed. SciPy is included in ArcGIS 10.4 and "
                      "later versions.", "error")
            return
    try:
        # initialize our neighborhood
        if verbose:
            utils.msg("Calculating neighborhood...")
        neighborhood = NbrRectangle(
            neighborhood_size, neighborhood_size, "CELL")
        n_label = "{:03d}".format(int(neighborhood_size))
        overlap = int((int(neighborhood_size)/2.0)-0.5)

        if mean_set.intersection(out_stats):
            if verbose:
                utils.msg("Calculating mean depth...")
            mean_depth = FocalStatistics(in_raster, neighborhood,
                                         "MEAN", "NODATA")
            mean_raster = os.path.join(out_workspace,
                                       "meandepth_{}.tif".format(n_label))
            if verbose:
                utils.msg("saving mean depth to {}".format(mean_raster))
            arcpy.CopyRaster_management(mean_depth, mean_raster)

        # compute stdev in ths case
        if std_dev_set.intersection(out_stats):
            std_dev = 'Standard Deviation' in out_stats
            if verbose and std_dev:
                utils.msg("Calculating depth standard deviation...")
            std_dev_depth = FocalStatistics(in_raster, neighborhood,
                                            "STD", "NODATA")
            std_dev_raster = os.path.join(out_workspace,
                                          "stddevdepth_{}.tif".format(n_label))
            if verbose and std_dev:
                utils.msg("saving standard deviation depth to \
                          {}".format(std_dev_raster))
            arcpy.CopyRaster_management(std_dev_depth, std_dev_raster)

            # no direct variance focal stat, have to stdev^2
            if 'Variance' in out_stats:
                if verbose:
                    utils.msg("Calculating depth variance...")
                var_depth = Power(std_dev_depth, 2)
                var_raster = os.path.join(out_workspace,
                                          "vardepth_{}.tif".format(n_label))
                if verbose:
                    utils.msg("saving depth variance to {}".format(var_raster))
                arcpy.CopyRaster_management(var_depth, var_raster)
                if not std_dev:
                    arcpy.Delete_management(std_dev_raster)

        if iqr_set.intersection(out_stats):
            if verbose:
                utils.msg("Calculating depth interquartile range...")
            iqr_raster = os.path.join(out_workspace,
                                      "iqrdepth_{}.tif".format(n_label))
            bp = utils.BlockProcessor(in_raster)
            # limit 3D blocks to 10^8 elements (.4GB)
            blocksize = int(math.sqrt((10**8) /
                                      (int(neighborhood_size)**2))**2)
            bp.computeBlockStatistics(iqr, blocksize, iqr_raster, overlap)

        if kurt_set.intersection(out_stats):
            if verbose:
                utils.msg("Calculating depth kurtosis...")
            kurt_raster = os.path.join(out_workspace,
                                       "kurtosisdepth_{}.tif".format(n_label))
            bp = utils.BlockProcessor(in_raster)
            # limit 3D blocks to 10^8 elements (.4GB)
            blocksize = int(math.sqrt((10**8) /
                                      (int(neighborhood_size)**2)) - overlap*2)
            bp.computeBlockStatistics(kurtosis, blocksize,
                                      kurt_raster, overlap)

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         neighborhood_size=sys.argv[2],
         out_workspace=sys.argv[3],
         out_stats_raw=sys.argv[4])
