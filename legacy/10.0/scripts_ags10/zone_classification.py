# zone_classification.py
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
BPIRaster = sys.argv[1]
SlopeRaster = sys.argv[2]
StdDevDiv = sys.argv[3]
SlopeDiv = sys.argv[4]
OutRaster = sys.argv[5]

try:
    # Get raster properties
    arcpy.AddMessage("Calculating properties of the standardized Bathymetric Position Index (BPI) raster...")
    result = arcpy.GetRasterProperties_management(BPIRaster, "STD")
    BPIStdDev = result.getOutput(0)
    arcpy.AddMessage("The standard deviation of the BPI raster is " + str(BPIStdDev) + ".")
    
    # Create the classified standardized Bathymetric Position Index (BPI) raster
    arcpy.AddMessage("Classifying the Bathymetric Position Index (BPI) raster...")
    CreDiv = float(StdDevDiv) * float(BPIStdDev)
    DepDiv = -1 * float(StdDevDiv) * float(BPIStdDev)
    outRaster = Con(Raster(BPIRaster) >= float(CreDiv), 1, Con(Raster(BPIRaster) <= float(DepDiv), 2, Con(Raster(SlopeRaster) <= float(SlopeDiv), 3, 4)))
    outRaster.save(OutRaster)

except:
# Print error message if an error occurs
    arcpy.GetMessages()