# -*- coding: utf-8 -*-
# classify.py
# Shaun Walbridge, 2012.10.07

# Import system modules
import os, sys, textwrap, arcpy
from arcpy.sa import Con, Raster

import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

class NoValidClasses(Exception):
    def __init__(self):
        Exception.__init__(self, "No valid output classes found")

def run_con(lower_bounds, upper_bounds, in_grid, true_val, true_alt=None):
    # debug message:
    #utils.msg("run_con: lb: `{}`  ub: `{}` grid: `{}`  val: `{}`, alt: `{}`".format(
    #        lower_bounds, upper_bounds, in_grid, true_val, true_alt))
    out_grid = None
    # if our initial desired output value isn't set, use the backup
    if true_val is None:
        true_val = true_alt
    # calculate our output grid
    if lower_bounds is not None:
        if upper_bounds is not None:
            out_grid_a = Con(in_grid, true_val, 0, "VALUE < {}".format(upper_bounds))
            out_grid = Con(in_grid, out_grid_a, 0, "VALUE > {}".format(lower_bounds))
        else:
            out_grid = Con(in_grid, true_val, 0, "VALUE >= {}".format(lower_bounds))
    elif upper_bounds is not None:
        out_grid = Con(in_grid, true_val, 0, "VALUE <= {}".format(upper_bounds))

    if type(out_grid).__name__ == 'NoneType' and type(true_val) == arcpy.sa.Raster:
        out_grid = true_val

    return out_grid

def main(classification_file, bpi_broad_std, bpi_fine_std, slope, bathy,
    out_raster=None, mode='toolbox'):

    try:
        # set up scratch workspace
        # FIXME: see issue #18
        # CON is very very picky. it generates GRID outputs by default, and the
        # resulting names must not exist. for now, push our temp results
        # to the output folder.
        out_workspace = os.path.dirname(out_raster)
        # make sure workspace exists
        utils.workspace_exists(out_workspace)
        arcpy.env.scratchWorkspace = out_workspace
        arcpy.env.workspace = out_workspace

        arcpy.env.overwriteOutput = True
        # Create the broad-scale Bathymetric Position Index (BPI) raster
        msg_text = "Generating the classified grid, based on the provided" + \
                " classes in '{classes}'.".format(classes=classification_file)
        utils.msg(msg_text)

        # Read in the BTM Document; the class handles parsing a variety of inputs.
        btm_doc = utils.BtmDocument(classification_file)
        classes = btm_doc.classification()
        utils.msg("Parsing {} document... found {} classes.".format(
            btm_doc.doctype, len(classes)))

        grids = []
        for item in classes:
            cur_class = str(item["Class"])
            cur_name = str(item["Zone"])
            utils.msg("Calculating grid for {}...".format(cur_name))
            out_con = None
            # here come the CONs:
            out_con = run_con(item["Depth_LowerBounds"], item["Depth_UpperBounds"], \
                    bathy, cur_class)
            out_con2 = run_con(item["Slope_LowerBounds"], item["Slope_UpperBounds"], \
                    slope, out_con, cur_class)
            out_con3 = run_con(item["LSB_LowerBounds"], item["LSB_UpperBounds"], \
                    bpi_fine_std, out_con2, cur_class)
            out_con4 = run_con(item["SSB_LowerBounds"], item["SSB_UpperBounds"], \
                    bpi_broad_std, out_con3, cur_class)

            if type(out_con4) == arcpy.sa.Raster:
                rast = utils.save_raster(out_con4, "con_{}.tif".format(cur_name))
                grids.append(rast)
            else:
                # fall-through: no valid values detected for this class.
                warn_msg = "WARNING, no valid locations found for class" + \
                        " {}:\n".format(cur_name)
                classifications = {
                        'depth': (item["Depth_LowerBounds"], item["Depth_UpperBounds"]),
                        'slope': (item["Slope_LowerBounds"], item["Slope_UpperBounds"]),
                        'broad': (item["SSB_LowerBounds"], item["SSB_UpperBounds"]), 
                        'fine': (item["LSB_LowerBounds"], item["LSB_UpperBounds"])}
                for (name, vrange) in classifications.items(): 
                    (vmin, vmax) = vrange
                    if vmin or vmax is not None:
                        if vmin is None:
                            vmin = ""
                        if vmax is None:
                            vmax = ""
                        warn_msg += "  {}: {{{}:{}}}\n".format(name, vmin, vmax)

                utils.msg(textwrap.dedent(warn_msg))
        if len(grids) == 0:
            raise NoValidClasses

        utils.msg("Creating Benthic Terrain Classification Dataset...")
        merge_grid = grids[0]
        for i in range(1, len(grids)):
            utils.msg("{} of {}".format(i, len(grids)-1))
            merge_grid = Con(merge_grid, grids[i], merge_grid, "VALUE = 0")

        arcpy.env.rasterStatistics = "STATISTICS"
        utils.msg("Saving Output to {}".format(out_raster))
        merge_grid.save(out_raster)
        utils.msg("Complete.")

        # Delete all intermediate raster data sets
        for grid in grids:
            arcpy.Delete_management(grid.catalogPath)
    except NoValidClasses as e:
        utils.msg(e, mtype='error')
    except Exception as e:
        if type(e) is ValueError:
            raise e
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(
        classification_file=sys.argv[1],
        bpi_broad_std=sys.argv[2],
        bpi_fine_std=sys.argv[3],
        slope=sys.argv[4],
        bathy=sys.argv[5],
        out_raster=sys.argv[6])
