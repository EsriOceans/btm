# broad_scale_bpi.py
# Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
#              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
#              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
#              create grids of slope, bathymetric position index and rugosity from an input data set.
#              An integrated XML-based terrain classification dictionary gives users the freedom to
#              create their own classifications and define the relationships that characterize them.
# Requirements: Spatial Analyst 
# Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
# Date: 2005
# Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
# to a Python Script that runs in ArcGIS 10.

# Import system modules
import sys, arcpy
from arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Script arguments
Bathy = sys.argv[1]
BroadInnerRadius = sys.argv[2]
BroadOuterRadius = sys.argv[3]
BroadOutRaster = sys.argv[4]

try:
    # Create the broad-scale Bathymetric Position Index (BPI) raster
    arcpy.AddMessage("Generating the broad-scale Bathymetric Position Index (BPI) raster...")
    outFocalStatistics = FocalStatistics(Bathy, NbrAnnulus(BroadInnerRadius, BroadOuterRadius, "CELL"), "MEAN")
    outRaster = Int(Plus(Minus(Bathy, outFocalStatistics), 0.5))
    outRaster.save(BroadOutRaster)

except:
    # Print error message if an error occurs
    arcpy.GetMessages()
