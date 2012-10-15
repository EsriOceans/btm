# structure_classification.py
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
BroadBPIRaster = sys.argv[1]
BroadStdDevDiv = sys.argv[2]
FineBPIRaster = sys.argv[3]
FineStdDevDiv = sys.argv[4]
SlopeRaster = sys.argv[5]
GentleSlopeDiv = sys.argv[6]
SteepSlopeDiv = sys.argv[7]
BathyRaster = sys.argv[8]
DepthDiv = sys.argv[9]
OutRaster = sys.argv[10]

try:
    # Get raster properties
    arcpy.AddMessage("Calculating properties of the standardized broad-scale Bathymetric Position Index (BPI) raster...")
    result1 = arcpy.GetRasterProperties_management(BroadBPIRaster, "STD")
    BroadBPIStdDev = result1.getOutput(0)
    arcpy.AddMessage("The standard deviation of the broad-scale BPI raster is " + str(BroadBPIStdDev) + ".")
    arcpy.AddMessage("Calculating properties of the standardized fine-scale Bathymetric Position Index (BPI) raster...")
    result2 = arcpy.GetRasterProperties_management(FineBPIRaster, "STD")
    FineBPIStdDev = result2.getOutput(0)
    arcpy.AddMessage("The standard deviation of the fine-scale BPI raster is " + str(FineBPIStdDev) + ".")
    
    # Create the classified standardized Bathymetric Position Index (BPI) raster
    arcpy.AddMessage("Classifying the Bathymetric Position Index (BPI) raster...")
    BroadCreDiv = float(BroadStdDevDiv) * float(BroadBPIStdDev)
    BroadDepDiv = -1 * float(BroadStdDevDiv) * float(BroadBPIStdDev)
    FineCreDiv = float(FineStdDevDiv) * float(FineBPIStdDev)
    FineDepDiv = -1 * float(FineStdDevDiv) * float(FineBPIStdDev)
    outRaster = Con(((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv))), 1, # Narrow depression
                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)), 2, # Local depression on flat
                        Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)), 3, # Lateral midslope depression
                            Con((Raster(BroadBPIRaster) >= float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)), 4, # Depression on crest
                                Con((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)), 5, # Broad depression with an open bottom
                                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)) & (Raster(BathyRaster) < float(DepthDiv)), 6, # Broad flat
                                        Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)) & (Raster(BathyRaster) >= float(DepthDiv)), 7, # Shelf
                                            Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)) & (Raster(SlopeRaster) <= float(SteepSlopeDiv)), 8, # Open slopes
                                                Con((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)), 9, # Local crest in depression
                                                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)), 10, # Local crest on flat
                                                        Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)), 11, # Lateral midslope crest
                                                            Con((Raster(BroadBPIRaster) >= float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)), 12, # Narrow crest
                                                                Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) > float(SteepSlopeDiv)), 13))))))))))))) # Steep slope
    outRaster.save(OutRaster)

except:
# Print error message if an error occurs
    arcpy.GetMessages()