# surface_area_to_planar_area.py
# Description: Approach used in BTMv1 for calculating rugosity, based on the
#              difference between surface area and planar area, as described
#              in Jenness, J. 2002. Surface Areas and Ratios from Elevation
#              Grid (surfgrids.avx) extension for ArcView 3.x, v. 1.2.
#              Jenness Enterprises. Available at:
#                http://www.jennessent.com/arcview/surface_areas.htm
# Requirements: Spatial Analyst

# Import system modules
import math
import os
import sys
import arcpy
from arcpy.sa import Raster, Divide, Cos, Times

# local imports
import scripts.utils as utils
import scripts.config as config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")


def compute_edge(raster_1, raster_2, distance):
    r""" Compute edge distance between two rasters, R_1 and R_2, and adjusts
        by the distance from the center cell.

    ..math:
     \frac{\sqrt{(\mathbf{R_1} - \mathbf{R_2})^{2}+d^2}}{2}
    """
    return (((raster_1 - raster_2)**2 + distance**2) ** 0.5) / 2


def triangle_area(side_a, side_b, side_c):
    r""" Compute triangle area.
        pp 11-12, Jenness.

    ..math:
    \mathbf{A} = \frac{a \cdot \sqrt{b^2 - \left (
      \frac{(a^2 + b^2 - c^2)}{2a}\right )^{2}}}{2}
    """
    return \
        ((side_a *
         (side_b**2 - ((side_a**2 + side_b**2 - side_c**2) / (side_a * 2))**2)**0.5)
         / 2)


def main(in_raster=None, out_raster=None, acr_correction=True, area_raster=None):
    """
    A calculation of rugosity, based on the difference between surface
    area and planar area, as described in Jenness, J. 2002. Surface Areas
    and Ratios from Elevation Grid (surfgrids.avx) extension for ArcView 3.x,
    v. 1.2. Jenness Enterprises.

    NOTE: the VRM method implemented in ruggeddness is generally considered
          superior to this method.
    """

    # sanitize acr input
    if isinstance(acr_correction, unicode) and acr_correction.lower() == 'false':
        acr_correction = False

    out_workspace = os.path.dirname(out_raster)
    # make sure workspace exists
    utils.workspace_exists(out_workspace)

    utils.msg("Set scratch workspace to {}...".format(out_workspace))

    # force temporary stats to be computed in our output workspace
    arcpy.env.scratchWorkspace = out_workspace
    arcpy.env.workspace = out_workspace
    pyramid_orig = arcpy.env.pyramid
    arcpy.env.pyramid = "NONE"
    # TODO: currently set to automatically overwrite, expose this as option
    arcpy.env.overwriteOutput = True

    bathy = Raster(in_raster)
    # get the cell size of the input raster; use same calculation as was
    # performed in BTM v1: (mean_x + mean_y) / 2
    cell_size = (bathy.meanCellWidth + bathy.meanCellHeight) / 2.0
    corner_dist = math.sqrt(2 * cell_size ** 2)
    flat_area = cell_size ** 2
    utils.msg("Cell size: {}\nFlat area: {}".format(cell_size, flat_area))

    try:
        # Create a set of shifted grids, with offets n from the origin X:

        #        8 | 7 | 6
        #        --|---|---
        #        5 | X | 4
        #        --|---|---
        #        3 | 2 | 1

        positions = [(1, -1), (0, -1), (-1, -1),
                     (1,  0),          (-1,  0),
                     (1,  1), (0,  1), (-1,  1)]

        corners = (1, 3, 6, 8)      # dist * sqrt(2), as set in corner_dist
        orthogonals = (2, 4, 5, 7)  # von Neumann neighbors, straight dist
        shift_rasts = [None]        # offset to align numbers
        temp_rasts = []

        for (n, pos) in enumerate(positions, start=1):
            utils.msg("Creating Shift Grid {} of 8...".format(n))
            # scale shift grid by cell size
            (x_shift, y_shift) = map(lambda(n): n * cell_size, pos)

            # set explicit path on shift rasters, otherwise suffer
            # inexplicable 999999 errors.
            shift_out = os.path.join(out_workspace, "shift_{}.tif".format(n))
            shift_out = utils.validate_path(shift_out)
            temp_rasts.append(shift_out)
            arcpy.Shift_management(bathy, shift_out, x_shift, y_shift)
            shift_rasts.append(arcpy.sa.Raster(shift_out))

        edge_rasts = [None]
        # calculate triangle length grids

        # edges 1-8: pairs of bathy:shift[n]
        for (n, shift) in enumerate(shift_rasts[1:], start=1):
            utils.msg("Calculating Triangle Edge {} of 16...".format(n))
            # adjust for corners being sqrt(2) from center
            if n in corners:
                dist = corner_dist
            else:
                dist = cell_size
            edge_out = os.path.join(out_workspace, "edge_{}.tif".format(n))
            edge_out = utils.validate_path(edge_out)
            temp_rasts.append(edge_out)
            edge = compute_edge(bathy, shift, dist)
            edge.save(edge_out)
            edge_rasts.append(arcpy.sa.Raster(edge_out))

        # edges 9-16: pairs of adjacent shift grids [see layout above]
        # in BTM_v1, these are labeled A-H
        adjacent_shift = [(1, 2), (2, 3), (1, 4), (3, 5),
                          (6, 4), (5, 8), (6, 7), (7, 8)]
        for (n, pair) in enumerate(adjacent_shift, start=9):
            utils.msg("Calculating Triangle Edge {} of 16...".format(n))
            # the two shift rasters for this iteration
            (i, j) = pair
            edge_out = os.path.join(out_workspace, "edge_{}.tif".format(n))
            edge_out = utils.validate_path(edge_out)
            temp_rasts.append(edge_out)
            edge = compute_edge(shift_rasts[i], shift_rasts[j], cell_size)
            edge.save(edge_out)
            edge_rasts.append(arcpy.sa.Raster(edge_out))

        # areas of each triangle
        areas = []
        for (n, pair) in enumerate(adjacent_shift, start=1):
            utils.msg("Calculating Triangle Area {} of 8...".format(n))
            # the two shift rasters; n has the third side
            (i, j) = pair
            area_out = os.path.join(out_workspace, "area_{}.tif".format(n))
            area_out = utils.validate_path(area_out)
            temp_rasts.append(area_out)

            area = triangle_area(edge_rasts[i], edge_rasts[j], edge_rasts[n+8])
            area.save(area_out)
            areas.append(arcpy.sa.Raster(area_out))

        utils.msg("Summing Triangle Area...")
        arcpy.env.pyramid = pyramid_orig
        arcpy.env.rasterStatistics = "STATISTICS"
        total_area = (areas[0] + areas[1] + areas[2] + areas[3] +
                      areas[4] + areas[5] + areas[6] + areas[7])
        if area_raster:
            save_msg = "Saving Surface Area Raster to " + \
                "{}.".format(area_raster)
            utils.msg(save_msg)
            total_area.save(area_raster)

        if not acr_correction:
            utils.msg("Calculating ratio with uncorrected planar area.")
            area_ratio = total_area / cell_size**2
        else:
            utils.msg("Calculating ratio with slope-corrected planar area.")
            slope_raster = arcpy.sa.Slope(in_raster, "DEGREE", "1")
            planar_area = Divide(float(cell_size**2), Cos(Times(slope_raster, 0.01745)))
            area_ratio = Divide(total_area, planar_area)

        out_raster = utils.validate_path(out_raster)
        save_msg = "Saving Surface Area to Planar Area ratio to " + \
            "{}.".format(out_raster)
        utils.msg(save_msg)
        area_ratio.save(out_raster)

    except Exception as e:
        utils.msg(e, mtype='error')

    try:
        # Delete all intermediate raster data sets
        utils.msg("Deleting intermediate data...")
        for path in temp_rasts:
            arcpy.Delete_management(path)

    except Exception as e:
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    if len(sys.argv) == 3:
        area_param = None
    else:
        area_param = sys.argv[3]
    main(in_raster=sys.argv[1],
         out_raster=sys.argv[2],
         area_raster=area_param)
