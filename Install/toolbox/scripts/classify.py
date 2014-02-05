# -*- coding: utf-8 -*-
# classify.py
# Shaun Walbridge, 2012.10.07

# Import system modules
import os, sys, textwrap, arcpy
from arcpy.sa import *

import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def runCon(lower_bounds, upper_bounds, in_grid, true_val, true_alt=None):
    # debug message:
    #utils.msg("runCon: lb: `%s`  ub: `%s` grid: `%s`  val: `%s`" % (lower_bounds, upper_bounds, in_grid, true_val))
    out_grid = ""
    # if our initial desired output value isn't set, use the backup
    if str(true_val) == '':
        true_val = true_alt
    # if we're getting a string back, treat it as an integer.
    if isinstance(true_val, str):
        # if it's a blank one, set our val to None
        if true_val == '':
            true_val = None
        else:
            true_val = float(true_val)
    # calculate our output grid
    if lower_bounds is not None:
        if upper_bounds is not None:
            out_grid = Con((Raster(in_grid) > float(lower_bounds)) & (Raster(in_grid) < float(upper_bounds)), true_val, 0)
        else:
            out_grid = Con(Raster(in_grid) >= float(lower_bounds), true_val, 0)
    elif upper_bounds is not None:
        out_grid = Con(Raster(in_grid) <= float(upper_bounds), true_val, 0)
    return out_grid

def main(classification_file, bpi_broad, bpi_fine, slope, bathy,
    out_raster=None, mode='toolbox'):

    try:
        # set up scratch workspace
        # FIXME: see issue #18
        # CON is very very picky. it generates GRID outputs by default, and the
        # resulting names must not exist. for now, push our temp results
        # to the output folder.
        out_workspace = os.path.dirname(out_raster)
        # make sure workspace exists
        utils.workspaceExists(out_workspace)
        utils.msg("Set scratch workspace to %s..." % out_workspace)
        arcpy.env.scratchWorkspace = out_workspace
        arcpy.env.workspace = out_workspace

        arcpy.env.overwriteOutput = True
        # Create the broad-scale Bathymetric Position Index (BPI) raster
        msg_text="Generating the classified grid, based on the provided" +\
            " classes in '{classes}'.".format(classes=classification_file)
        utils.msg(msg_text)
        
        # Read in the BTM Document; the class handles parsing a variety of inputs.
        btm_doc = utils.BtmDocument(classification_file)
        classes = btm_doc.classification()
        utils.msg("Parsing %s document... found %i classes." % (btm_doc.doctype, len(classes)))

        grids = []
        for item in classes:
            cur_class = str(item["Class"])
            cur_name = str(item["Zone"])
            utils.msg("Calculating grid for %s..." % cur_name)
            out_con = ""
            # here come the CONs:
            out_con = runCon(item["Depth_LowerBounds"], item["Depth_UpperBounds"], \
                    bathy, cur_class)
            out_con = runCon(item["Slope_LowerBounds"], item["Slope_UpperBounds"], \
                    slope, out_con, cur_class)
            out_con = runCon(item["LSB_LowerBounds"], item["LSB_UpperBounds"], \
                    bpi_broad, out_con, cur_class)
            out_con = runCon(item["SSB_LowerBounds"], item["SSB_UpperBounds"], \
                    bpi_fine, out_con, cur_class)
            if type(out_con) == arcpy.sa.Raster:
                rast = utils.saveRaster(out_con, "con_{}.tif".format(cur_name))
                grids.append(rast)
            else:
                # fall-through: no valid values detected for this class.
                warn_msg = """\
                        WARNING: no valid locations found for class {}:
                          depth:     ({}本})
                          slope:     ({}本}) 
                          broad BPI: ({}本}) 
                          fine BPI:  ({}本})""".format(\
                                cur_name, item["Depth_LowerBounds"],
                                item["Depth_UpperBounds"], item["Slope_LowerBounds"],
                                item["Slope_UpperBounds"], item["LSB_LowerBounds"],
                                item["LSB_UpperBounds"], item["SSB_LowerBounds"],
                                item["SSB_UpperBounds"])
                utils.msg(textwrap.dedent(warn_msg))

        utils.msg("Creating Benthic Terrain Classification Dataset...")
        merge_grid = grids[0]
        for i in range(1, len(grids)):
            utils.msg("{} of {}".format(i, len(grids)-1))
            merge_grid = Con(merge_grid, grids[i], merge_grid, "VALUE = 0")
        utils.msg("Saving Output to %s" % out_raster)
        merge_grid.save(out_raster)

        utils.msg("Complete.")

        # Delete all intermediate raster data sets
        arcpy.AddMessage("Deleting intermediate data...")
        paths = []
        for grid in grids:
            arcpy.Delete_management(grid.catalogPath)
 
    except Exception as e:
        if type(e) is ValueError:
            raise e
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__=='__main__':
    config.mode = 'script'
    main(
        classification_file=sys.argv[1],
        bpi_broad=sys.argv[2],
        bpi_fine=sys.argv[3],
        slope=sys.argv[4],
        bathy=sys.argv[5],
        out_raster=sys.argv[6])
