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
    print "runCon: lb: `%s`  ub: `%s` grid: `%s`  val: `%s`" % (lower_bounds, upper_bounds, in_grid, true_val)
    out_grid = ""
    # if our initial desired output value isn't set, use the backup
    if str(true_val) == '':
        true_val = true_alt
    if lower_bounds is not None:
        if upper_bounds is not None:
            out_grid = Con(in_grid, true_val, 0, ("VALUE < " +  upper_bounds) )
            out_grid = Con(in_grid, out_grid, 0, ("VALUE > " +  lower_bounds) )
        else:
            out_grid = Con(in_grid, true_val, 0, ("VALUE >= " +  lower_bounds ) )
    elif upper_bounds is not None:
        out_grid = Con(in_grid, true_val, 0, ("VALUE <= " + upper_bounds) )

    return out_grid

def main(classification_file, bpi_broad, bpi_fine, slope, bathy,
    out_raster=None, mode='toolbox'):

    # set up scratch workspace
    #arcpy.env.scratchWorkspace = "c:\\data\\arcgis\\workspace"
    #arcpy.env.workspace = "c:\\data\\arcgis\\workspace"

    try:
        # Create the broad-scale Bathymetric Position Index (BPI) raster
        msg_text="Generating the classified grid, based on the provided" +\
            " classes in '{classes}'...".format(classes=classification_file)
        msg(msg_text)
        
        # XXX: use utils class to get a BTMDocument object.
        # read in the xml doc
        btm_doc = BtmDocument(classification_file)
        msg("parsing document of type %s..." % btm_doc.doctype)
        classes = btm_doc.classification()
        class_count = len(classes)
        msg("found %i classes" % class_count)

        grids = []
        # XXX just do this with an XML file for this first pass, needs
        # to be generalized to handle CSV/XLS.

        for item in classes:
            out_con = ""
            # here come the CONs:
            out_con = runCon(item["Depth_LowerBounds"], item["Depth_UpperBounds"], \
                    bathy, str(item["Class"]))
            out_con = runCon(item["Slope_LowerBounds"], item["Slope_UpperBounds"], \
                    slope, out_con, str(item["Class"]))
            out_con = runCon(item["LSB_LowerBounds"], item["LSB_UpperBounds"], \
                    bpi_broad, out_con, str(item["Class"]))
            out_con = runCon(item["SSB_LowerBounds"], item["SSB_UpperBounds"], \
                    bpi_fine, out_con, str(item["Class"]))
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
