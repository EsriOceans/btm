# standardize_bpi_grids.py
# Description: The Benthic Terrain Modeler (BTM) functions as a toolbox 
#              within ArcMap, and relies on a methodology to analyze benthic 
#              terrain from input multibeam bathymetry in ESRI's GRID (raster)
#              format. The BTM toolbox contains a set of tools that allow users
#              to create grids of slope, bathymetric position index and 
#              rugosity from an input data set.  An integrated XML-based 
#              terrain classification dictionary gives users the freedom to
#              create their own classifications and define the relationships 
#              that characterize them.
# Requirements: Spatial Analyst 
# Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
# Date: 2005
# Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
# to a Python Script that runs in ArcGIS 10.

# Import system modules
import sys, arcpy
from arcpy.sa import *

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def main(bpi_raster=None, out_raster=None):
    try:
        # Get raster properties
        utils.msg("Calculating properties of the Bathymetric Position Index (BPI) raster...")
        utils.msg("raster: %s; output: %s" % (bpi_raster, out_raster))
        result1 = arcpy.GetRasterProperties_management(bpi_raster, "MEAN")
        BPIMean = result1.getOutput(0)
        utils.msg("The mean of the BPI raster is " + str(BPIMean) + ".")
        result2 = arcpy.GetRasterProperties_management(BPIRaster, "STD")
        BPIStdDev = result2.getOutput(0)
        utils.msg("The standard deviation of the BPI raster is " + str(BPIStdDev) + ".")
        
        # Create the standardized Bathymetric Position Index (BPI) raster
        arcpy.AddMessage("Standardizing the Bathymetric Position Index (BPI) raster...")
        outRaster = Int(Plus(Times(Divide(Minus(BPIRaster, float(BPIMean)), float(BPIStdDev)), 100), 0.5))
        outRaster.save(out_raster)

    except:
        # Print error message if an error occurs
        errors = arcpy.GetMessages()
        utils.msg(errors, mtype='error')


# when executing as a standalone script get parameters from sys
if __name__=='__main__':
    config.mode = 'script'
    main(bpi_raster=sys.argv[1], out_raster=sys.argv[2])
