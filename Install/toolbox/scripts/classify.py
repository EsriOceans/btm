# classify.py
# Shaun Walbridge, 2012.10.07

# Import system modules
import sys, arcpy
from arcpy.sa import *

# local imports
from utils import *
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def runCon(lower_bounds, upper_bounds, in_grid, true_val, true_alt=None):
    # debug message:
    #msg("runCon: lb: `%s`  ub: `%s` grid: `%s`  val: `%s`" % (lower_bounds, upper_bounds, in_grid, true_val))
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
        output_dir = os.path.dirname(out_raster)
        msg("Set scratch workspace to %s..." % output_dir)
        arcpy.env.scratchWorkspace = output_dir
        arcpy.env.workspace = output_dir

        # Create the broad-scale Bathymetric Position Index (BPI) raster
        msg_text="Generating the classified grid, based on the provided" +\
            " classes in '{classes}'.".format(classes=classification_file)
        msg(msg_text)
        
        # Read in the BTM Document; the class handles parsing a variety of inputs.
        btm_doc = BtmDocument(classification_file)
        classes = btm_doc.classification()
        msg("Parsing %s document... found %i classes." % (btm_doc.doctype, len(classes)))

        grids = []

        for item in classes:
            cur_class = str(item["Class"])
            msg("Calculating grid for class %s..." % cur_class)
            out_con = ""
            # here come the CONs:
            out_con = runCon(item["Depth_LowerBounds"], item["Depth_UpperBounds"], bathy, cur_class)
            out_con = runCon(item["Slope_LowerBounds"], item["Slope_UpperBounds"], slope, out_con, cur_class)
            out_con = runCon(item["LSB_LowerBounds"], item["LSB_UpperBounds"], bpi_broad, out_con, cur_class)
            out_con = runCon(item["SSB_LowerBounds"], item["SSB_UpperBounds"], bpi_fine, out_con, cur_class)
            grids.append(out_con)

        msg("Creating Benthic Terrain Classification Dataset...")
        merge_grid = grids[0]
        for index in range(1,len(grids)):
             merge_grid = Con(merge_grid, grids[index], merge_grid, ("VALUE = 0"))
        msg("Saving Output to %s" % out_raster)
        merge_grid.save(out_raster)

        msg("Complete.")

    except Exception as e:
        msg(e, mtype='error')

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
