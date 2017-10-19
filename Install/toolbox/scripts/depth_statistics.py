# depth_statistics.py: compute depth statistics
# Requirements: Spatial Analyst
# Author: Shaun Walbridge
# Date: 9/1/2012

# Import system modules
from __future__ import absolute_import
import os
import sys
import numpy as np
try:
    import scipy.stats
except ImportError:
    pass    # error generated inline
import arcpy
from arcpy.sa import NbrRectangle, FocalStatistics, Power

# local imports
from . import utils
from . import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def iqr(in_array, overlap):
    s = in_array.shape
    nbh_list = []
    for r in range(0, (overlap * 2) + 1):
        for c in range(0, (overlap * 2) + 1):
            nbh_list.append(in_array[r:(s[0] - (overlap * 2) + r),
                                     c:(s[1] - (overlap * 2) + c)])
    iqr_array = np.array(nbh_list)
    iqr_array = (np.percentile(iqr_array, 75, axis=0) -
                 np.percentile(iqr_array, 25, axis=0))
    return iqr_array


def kurtosis(in_array, overlap):
    s = in_array.shape
    nbh_list = []
    for r in range(0, (overlap * 2) + 1):
        for c in range(0, (overlap * 2) + 1):
            nbh_list.append(in_array[r:(s[0] - (overlap * 2) + r),
                                     c:(s[1] - (overlap * 2) + c)])
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
    out_stats = list(set(out_stats) - set(['Terrain Ruggedness (VRM)']))
    arcpy.env.rasterStatistics = "STATISTICS"
    arcpy.env.compression = 'LZW'  # compress output rasters

    # neighborhood is integer
    n_size = int(neighborhood_size)

    # convert our data to sets for easy comparison
    mean_set = set(['Mean Depth'])
    std_dev_set = set(['Standard Deviation', 'Variance'])
    diff_mean_set = set(['Difference to Mean'])
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

    ws = arcpy.Describe(out_workspace)
    ws_type = set([ws.workspaceType])
    db_types = ['LocalDatabase', 'RemoteDatabase']
    if ws_type.intersection(db_types):
        ext = ""
    else:
        ext = ".tif"
    in_base = os.path.splitext(os.path.basename(in_raster))[0]

    utils.workspace_exists(out_workspace)
    # set geoprocessing environments
    arcpy.env.scratchWorkspace = out_workspace
    arcpy.env.workspace = out_workspace

    try:
        # initialize our neighborhood
        if verbose:
            utils.msg("Calculating neighborhood...")
        neighborhood = NbrRectangle(n_size, n_size, "CELL")
        n_label = "{:03d}".format(n_size)
        overlap = int((n_size / 2.0) - 0.5)

        if mean_set.intersection(out_stats):
            if verbose:
                utils.msg("Calculating mean depth...")
            mean_depth = FocalStatistics(in_raster, neighborhood,
                                         "MEAN", "NODATA")
            mean_raster = os.path.join(out_workspace,
                                       "{}_mean_{}{}"
                                       .format(in_base, n_label, ext))
            if verbose:
                utils.msg("saving mean depth to {}".format(mean_raster))
            arcpy.CopyRaster_management(mean_depth, mean_raster)

            if diff_mean_set.intersection(out_stats):
                if verbose:
                    utils.msg("Calculating relative difference to mean...")
                range_depth = FocalStatistics(in_raster, neighborhood,
                                              "RANGE", "NODATA")

                mean_diff = -(mean_depth - in_raster) / range_depth
                mean_diff_raster = os.path.join(out_workspace,
                                                "{}_mean_diff_{}{}"
                                                .format(in_base, n_label, ext))

                if verbose:
                    utils.msg("saving relative different to mean to {}".format(
                        mean_diff_raster))
                arcpy.CopyRaster_management(mean_diff, mean_diff_raster)

        # compute stdev in ths case
        if std_dev_set.intersection(out_stats):
            std_dev = 'Standard Deviation' in out_stats
            if verbose and std_dev:
                utils.msg("Calculating depth standard deviation...")
            std_dev_depth = FocalStatistics(in_raster, neighborhood,
                                            "STD", "NODATA")
            std_dev_raster = os.path.join(out_workspace,
                                          "{}_sdev_{}{}"
                                          .format(in_base, n_label, ext))
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
                                          "{}_var_{}{}"
                                          .format(in_base, n_label, ext))
                if verbose:
                    utils.msg("saving depth variance to {}".format(var_raster))
                arcpy.CopyRaster_management(var_depth, var_raster)
                if not std_dev:
                    arcpy.Delete_management(std_dev_raster)

        # limit 3D blocksize to 10^8 elements (.4GB) on 32-bit, 10^10 on 64-bit
        if utils.ARCH == '32-bit':
            limit = 10**8
        else:
            limit = 10**10

        blocksize = int(np.sqrt((limit) / (n_size**2)) - overlap * 2)
        # define numpy-based calculations
        np_sets = ((iqr_set, "interquartile range", "iqr", iqr),
                   (kurt_set, "kurtosis", "kurt", kurtosis))

        for np_set in np_sets:
            (in_set, label, out_label, funct) = np_set
            if in_set.intersection(out_stats):
                if verbose:
                    utils.msg("Calculating depth {}...".format(label))

                file_name = "{}_{}_{}{}".format(in_base, out_label, n_label, ext)
                out_raster = os.path.join(out_workspace, file_name)
                bp = utils.BlockProcessor(in_raster)
                bp.computeBlockStatistics(funct, blocksize, out_raster, overlap)

    except Exception as e:
        utils.msg(e, mtype='error')


# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         neighborhood_size=sys.argv[2],
         out_workspace=sys.argv[3],
         out_stats_raw=sys.argv[4])
