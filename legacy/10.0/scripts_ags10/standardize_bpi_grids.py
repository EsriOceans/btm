# standardize_bpi_grids.py
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
OutRaster = sys.argv[2]

try:
    # Get raster properties
    arcpy.AddMessage("Calculating properties of the Bathymetric Position Index (BPI) raster...")
    result1 = arcpy.GetRasterProperties_management(BPIRaster, "MEAN")
    BPIMean = result1.getOutput(0)
    arcpy.AddMessage("The mean of the BPI raster is " + str(BPIMean) + ".")
    result2 = arcpy.GetRasterProperties_management(BPIRaster, "STD")
    BPIStdDev = result2.getOutput(0)
    arcpy.AddMessage("The standard deviation of the BPI raster is " + str(BPIStdDev) + ".")
    
    # Create the standardized Bathymetric Position Index (BPI) raster
    arcpy.AddMessage("Standardizing the Bathymetric Position Index (BPI) raster...")
    outRaster = Int(Plus(Times(Divide(Minus(BPIRaster, float(BPIMean)), float(BPIStdDev)), 100), 0.5))
    outRaster.save(OutRaster)

except:
# Print error message if an error occurs
    arcpy.GetMessages()