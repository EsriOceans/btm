# ruggedness.py
# Description: This tool measures terrain ruggedness by calculating the 
#              vector ruggedness measure (VRM) described in Sappington, J.M.,
#              K.M. Longshore, and D.B. Thompson. 2007. Quantifying Landscape 
#              Ruggedness for Animal Habitat Analysis: A Case Study Using 
#              Bighorn Sheep in the Mojave Desert. Journal of Wildlife 
#              Management. 71(5): 1419 -1426.
# Requirements: Spatial Analyst 
# Author: Mark Sappington
# Date: 2/1/2008
# Updated 12/1/2010 by Emily C. Huntley of the Massachusetts Office of 
# Coastal Zone Management to run in ArcGIS 10.

# Import system modules
import sys, string, os, arcpy
from arcpy.sa import *

# local imports
import utils
import config

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

def main(InRaster=None, NeighborhoodSize=None, OutWorkspace=None, OutRaster=None):
    # Local variables
    AspectRaster = OutWorkspace + "\\aspect"
    SlopeRaster = OutWorkspace + "\\slope"
    SlopeRasterRad = OutWorkspace + "\\sloperad"
    AspectRasterRad = OutWorkspace + "\\aspectrad"
    xRaster = OutWorkspace + "\\x"
    yRaster = OutWorkspace + "\\y"
    zRaster = OutWorkspace + "\\z"
    xyRaster = OutWorkspace + "\\xy"
    xSumRaster = OutWorkspace + "\\xsum"
    ySumRaster = OutWorkspace + "\\ysum"
    zSumRaster = OutWorkspace + "\\zsum"
    ResultRaster = OutWorkspace + "\\result"

    try:
        # Create Slope and Aspect rasters
        arcpy.AddMessage("Calculating aspect...")
        outAspect = Aspect(InRaster)
        outAspect.save(AspectRaster)
        arcpy.AddMessage("Calculating slope...")
        outSlope = Slope(InRaster, "DEGREE")
        outSlope.save(SlopeRaster)

        # Convert Slope and Aspect rasters to radians
        arcpy.AddMessage("Converting slope and aspect to radians...")
        outTimes1 = Times(SlopeRaster,(3.14/180))
        outTimes1.save(SlopeRasterRad)
        outTimes2 = Times(AspectRaster,(3.14/180))
        outTimes2.save(AspectRasterRad)

        # Calculate x, y, and z rasters
        arcpy.AddMessage("Calculating x, y, and z rasters...")
        outSin = Sin(SlopeRasterRad)
        outSin.save(xyRaster)
        outCos = Cos(SlopeRasterRad)
        outCos.save(zRaster)
        OutRas1 = Times(Con(AspectRaster == -1, 0, Sin(AspectRasterRad)), xyRaster)
        OutRas1.save(xRaster)
        OutRas2 = Times(Con(AspectRaster == -1, 0, Cos(AspectRasterRad)), xyRaster)
        OutRas2.save(yRaster)
        
        # Calculate sums of x, y, and z rasters for selected neighborhood size
        arcpy.AddMessage("Calculating sums of x, y, and z rasters in selected neighborhood...")
        outFocalStatistics1 = FocalStatistics(xRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
        outFocalStatistics1.save(xSumRaster)
        outFocalStatistics2 = FocalStatistics(yRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
        outFocalStatistics2.save(ySumRaster)
        outFocalStatistics3 = FocalStatistics(zRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
        outFocalStatistics3.save(zSumRaster)

        # Calculate the resultant vector
        arcpy.AddMessage("Calculating the resultant vector...")
        OutRas3 = SquareRoot(Square(xSumRaster) + Square(ySumRaster) + Square(zSumRaster))
        OutRas3.save(ResultRaster)

        # Calculate the Ruggedness raster
        arcpy.AddMessage("Calculating the final ruggedness raster...")
        maxValue = int(Neighborhood_Size) * int(Neighborhood_Size)
        OutRas4 = Minus(1, Divide(ResultRaster, maxValue))
        OutRas4.save(OutRaster)

        # Delete all intermediate raster data sets
        arcpy.AddMessage("Deleting intermediate data...")
        arcpy.Delete_management(AspectRaster)
        arcpy.Delete_management(SlopeRaster)
        arcpy.Delete_management(SlopeRasterRad)
        arcpy.Delete_management(AspectRasterRad)
        arcpy.Delete_management(xRaster)
        arcpy.Delete_management(yRaster)
        arcpy.Delete_management(zRaster)
        arcpy.Delete_management(xyRaster)
        arcpy.Delete_management(xSumRaster)
        arcpy.Delete_management(ySumRaster)
        arcpy.Delete_management(zSumRaster)
        arcpy.Delete_management(ResultRaster)
        
    except Exception as e:
        # Print error message if an error occurs
        #errors = arcpy.GetMessages()
        #print "from except: " + e.message 
        utils.msg(e, mtype='error')

# when executing as a standalone script get parameters from sys
if __name__=='__main__':
    config.mode = 'script'
    main(InRaster=sys.argv[1], NeighborhoodSize=sys.argv[2], 
            OutWorkspace=sys.argv[3], OutRaster=sys.argv[4])
