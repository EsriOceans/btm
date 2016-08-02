import arcpy
from arcpy import Raster
from arcpy.sa import Slope, Aspect
import os

import scripts.utils as utils
from scripts.tempdir import TempDir

arcpy.env.overwriteOutput = True

def main(in_raster=None, areaOfInterest=None, saveTINs=None):

    rastName = os.path.splitext(os.path.split(in_raster)[1])[0]
    bathyRaster = Raster(in_raster)
    cellSize = bathyRaster.meanCellHeight

    with TempDir() as d:
        # Check if multipart polygon and convert to singlepart if true
        with arcpy.da.SearchCursor(areaOfInterest, ["SHAPE@"]) as cursor:  
            for row in cursor:  
                geometry = row[0]  
                if geometry.isMultipart == True:
                    utils.msg("Converting multipart geometry to single parts...")
                    singlepart = os.path.join(d,'singlepart.shp')
                    arcpy.MultipartToSinglepart_management(areaOfInterest,singlepart)
                    arcpy.CopyFeatures_management(singlepart,areaOfInterest)

        # Name temporary files
        elevationTIN = os.path.join(d, 'elevationTIN')
        boundaryBuffer = os.path.join(d,'bnd_buf.shp')
        boundaryRaster = os.path.join(d,'bnd_rast.tif')
        boundaryPoints = os.path.join(d,'bnd_pts.shp')
        pobfRaster = os.path.join(d,'pobf_rast.tif')

        # Create elevation TIN
        utils.msg("Creating elevation TIN...")
        arcpy.CalculateStatistics_management(bathyRaster)
        zTolerance = abs((bathyRaster.maximum - bathyRaster.minimum)/10)
        arcpy.RasterTin_3d(bathyRaster, elevationTIN, str(zTolerance))
        arcpy.EditTin_3d(elevationTIN, ["#", "<None>", "<None>",
                                        "hardclip", "false"])
        
        # If more than one polygon in areaOfInterest, split into separate files to process
        splitFiles = [areaOfInterest]
        multiple = False
        if arcpy.GetCount_management(areaOfInterest)>1:
            multiple = True
            arcpy.AddField_management(areaOfInterest, "Name", "TEXT")
            splitFiles = []
            with arcpy.da.UpdateCursor(areaOfInterest, ["FID","Name"]) as cursor:
                for row in cursor:
                    row[1] = "poly_{}".format(row[0])
                    splitFiles.append("in_memory\poly_{}".format(row[0]))
                    cursor.updateRow(row)
            arcpy.Split_analysis(areaOfInterest,areaOfInterest,'Name','in_memory')

        # Calculate ACR for each polygon
        pobfs = []
        i = 0
        for each in splitFiles:
            utils.msg("Calculating ACR Rugosity for Area {} of {}...".format(i+1,len(splitFiles)))

            # Create POBF TIN
            arcpy.Buffer_analysis(each, boundaryBuffer,cellSize,"OUTSIDE_ONLY")
            arcpy.Clip_management(in_raster, '#', boundaryRaster, boundaryBuffer,
                                  '#', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
            arcpy.RasterToPoint_conversion(boundaryRaster, boundaryPoints, 'Value')
            arcpy.GlobalPolynomialInterpolation_ga(boundaryPoints, "grid_code","#",
                                                   pobfRaster, cellSize)
            arcpy.CalculateStatistics_management(pobfRaster)
            pobfTIN = os.path.join(d, 'planarTIN{}'.format(i))
            pobfs.append(pobfTIN)
            zTolerance = abs((int(Raster(pobfRaster).maximum) - int(Raster(pobfRaster).minimum))/10)
            arcpy.RasterTin_3d(pobfRaster, pobfTIN, str(zTolerance))
            arcpy.EditTin_3d(pobfTIN, ["#", "<None>", "<None>", "hardclip", "false"])

            # Calculate Rugosity
            arcpy.PolygonVolume_3d(elevationTIN, each, "<None>", "BELOW", "Volume1", "Surf_Area")
            arcpy.PolygonVolume_3d(pobfTIN, each, "<None>", "BELOW", "Volume2", "Plan_Area")
            arcpy.AddField_management(each, "Rugosity", "DOUBLE")
            arcpy.CalculateField_management(each, "Rugosity", "[Surf_Area] / [Plan_Area]")    
            arcpy.DeleteField_management(each, "Volume2;Volume1;Name")

            # Calculate Slope and Aspect
            arcpy.AddField_management(each, "Slope", "DOUBLE")
            arcpy.AddField_management(each, "Aspect", "DOUBLE")
            pobfSlope = Slope(pobfRaster)
            arcpy.CalculateStatistics_management(pobfSlope)
            pobfAspect = Aspect(pobfRaster)
            arcpy.CalculateStatistics_management(pobfAspect)
            with arcpy.da.UpdateCursor(each,["Slope","Aspect"]) as cursor:
                for rows in cursor:
                    rows[0] = pobfSlope.mean
                    rows[1] = pobfAspect.mean
                    cursor.updateRow(rows)
            i+=1

        # Merge split files and save to input file location
        if multiple:
            arcpy.Merge_management(splitFiles,areaOfInterest)

        # Save TINs if requested
        if saveTINs == 'true':
            utils.msg("Saving elevation and planar TINs to {}...".format(os.path.split(areaOfInterest)[0]))
            arcpy.CopyTin_3d(elevationTIN,
                             os.path.join(os.path.split(areaOfInterest)[0],
                                          '{}_elevationTIN'.format(rastName)))
            for x in range(len(pobfs)):
                arcpy.CopyTin_3d(pobfs[x], os.path.join(os.path.split(areaOfInterest)[0],
                                                       '{}_planarTIN{}'.format(rastName,x)))
