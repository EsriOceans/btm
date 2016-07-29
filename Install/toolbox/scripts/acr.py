import arcpy
from arcpy import Raster
import os

import scripts.utils as utils
from scripts.tempdir import TempDir

arcpy.env.overwriteOutput = True

def main(in_raster=None, areaOfInterest=None, saveTINs=None):

    with TempDir() as d:

        with arcpy.da.SearchCursor(areaOfInterest, ["SHAPE@"]) as cursor:  
            for row in cursor:  
                geometry = row[0]  
                if geometry.isMultipart == True:
                    utils.msg("Converting multipart geometry to single parts...")
                    singlepart = os.path.join(d,'singlepart.shp')
                    arcpy.MultipartToSinglepart_management(areaOfInterest,singlepart)
                    arcpy.CopyFeatures_management(singlepart,areaOfInterest)
        
        rastName = os.path.splitext(os.path.split(in_raster)[1])[0]
        bathyRaster = Raster(in_raster)
        cellSize = bathyRaster.meanCellHeight
        elevationTIN = os.path.join(d, 'elevationTIN')
        pobfTIN = os.path.join(d, 'planarTIN')
        boundaryBuffer = os.path.join(d,'bnd_buf.shp')
        boundaryRaster = os.path.join(d,'bnd_rast.tif')
        boundaryPoints = os.path.join(d,'bnd_pts.shp')
        pobfRaster = os.path.join(d,'pobf_rast.tif')

        utils.msg("Calculating Arc-Chord Ratio...")
        arcpy.CalculateStatistics_management(bathyRaster)
        zTolerance = abs((bathyRaster.maximum - bathyRaster.minimum)/10)
        arcpy.RasterTin_3d(bathyRaster, elevationTIN, str(zTolerance))
        arcpy.EditTin_3d(elevationTIN, ["#", "<None>", "<None>",
                                        "hardclip", "false"])
        arcpy.Buffer_analysis(areaOfInterest, boundaryBuffer,
                              cellSize,"OUTSIDE_ONLY")
        arcpy.Clip_management(in_raster, '#', boundaryRaster, boundaryBuffer,
                              '#', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
        arcpy.RasterToPoint_conversion(boundaryRaster, boundaryPoints, 'Value')
        arcpy.GlobalPolynomialInterpolation_ga(boundaryPoints, "grid_code","#",
                                               pobfRaster, cellSize)
        arcpy.CalculateStatistics_management(pobfRaster)
        zTolerance = abs((int(Raster(pobfRaster).maximum) - int(Raster(pobfRaster).minimum))/10)
        arcpy.RasterTin_3d(pobfRaster, pobfTIN, str(zTolerance))
        arcpy.EditTin_3d(pobfTIN, ["#", "<None>", "<None>", "hardclip", "false"])
        arcpy.PolygonVolume_3d(elevationTIN, areaOfInterest, "<None>", "BELOW",
                               "Volume1", "contoured")
        arcpy.PolygonVolume_3d(pobfTIN, areaOfInterest, "<None>", "BELOW",
                               "Volume2", "planar")
        arcpy.AddField_management(areaOfInterest, "Rugosity", "DOUBLE")
        arcpy.CalculateField_management(areaOfInterest,"Rugosity",
                                        "[contoured]/ [planar]") 
        arcpy.DeleteField_management(areaOfInterest, "Volume2;Volume1")

        if saveTINs == 'true':
            utils.msg("Saving elevation and planar TINs to {}...".format(os.path.split(areaOfInterest)[0]))
            arcpy.CopyTin_3d(elevationTIN,
                             os.path.join(os.path.split(areaOfInterest)[0],
                                          '{}_elevationTIN'.format(rastName)))
            arcpy.CopyTin_3d(pobfTIN,
                             os.path.join(os.path.split(areaOfInterest)[0],
                                          '{}_planarTIN'.format(rastName)))
