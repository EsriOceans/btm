import arcpy
from arcpy import Raster
from arcpy.sa import Slope, Aspect
import numpy as np
import os

import scripts.utils as utils
from scripts.tempdir import TempDir

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("GeoStats")


def main(in_raster=None, areaOfInterest=None, saveTINs=False, workspace=None):

    if isinstance(saveTINs, unicode) and saveTINs.lower() == 'false':
        saveTINs = False
    if isinstance(saveTINs, unicode) and saveTINs.lower() == 'true':
        saveTINs = True

    rastName = os.path.splitext(os.path.split(in_raster)[1])[0]
    bathyRaster = Raster(in_raster)
    cellSize = bathyRaster.meanCellHeight

    with TempDir() as d:
        # Check if multipart polygon and convert to singlepart if true
        with arcpy.da.SearchCursor(areaOfInterest, ["SHAPE@"]) as cursor:
            for row in cursor:
                geometry = row[0]
                if geometry.isMultipart is True:
                    utils.msg("Converting multipart geometry"
                              "to single parts...")
                    singlepart = os.path.join(d, 'singlepart.shp')
                    arcpy.MultipartToSinglepart_management(areaOfInterest,
                                                           singlepart)
                    arcpy.CopyFeatures_management(singlepart, areaOfInterest)

        # Name temporary files
        elevationTIN = os.path.join(d, 'elevationTIN')
        boundaryBuffer = os.path.join(d, 'bnd_buf.shp')
        boundaryRaster = os.path.join(d, 'bnd_rast.tif')
        boundaryPoints = os.path.join(d, 'bnd_pts.shp')
        pobfRaster = os.path.join(d, 'pobf_rast.tif')

        # Create elevation TIN
        utils.msg("Creating elevation TIN...")
        arcpy.CalculateStatistics_management(bathyRaster)
        zTolerance = abs((bathyRaster.maximum - bathyRaster.minimum)/10)
        arcpy.RasterTin_3d(bathyRaster, elevationTIN, str(zTolerance))
        arcpy.EditTin_3d(elevationTIN, ["#", "<None>", "<None>",
                                        "hardclip", "false"])

        # If more than one polygon in areaOfInterest,
        # split into separate files to process
        splitFiles = [areaOfInterest]
        multiple = False
        if arcpy.GetCount_management(areaOfInterest) > 1:
            multiple = True
            arcpy.AddField_management(areaOfInterest, "Name", "TEXT")
            splitFiles = []
            with arcpy.da.UpdateCursor(areaOfInterest,
                                       ["FID", "Name"]) as cursor:
                for row in cursor:
                    row[1] = "poly_{}".format(row[0])
                    splitFiles.append("in_memory\poly_{}".format(row[0]))
                    cursor.updateRow(row)
            arcpy.Split_analysis(areaOfInterest, areaOfInterest,
                                 'Name', 'in_memory')

        # Calculate ACR for each polygon
        pobfs = []
        i = 0
        for each in splitFiles:
            utils.msg("Calculating ACR Rugosity for Area "
                      "{} of {}...".format(i+1, len(splitFiles)))
            # Create POBF TIN
            arcpy.Buffer_analysis(each, boundaryBuffer,
                                  cellSize, "OUTSIDE_ONLY")
            arcpy.Clip_management(in_raster, '#', boundaryRaster,
                                  boundaryBuffer, '#',
                                  'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
            arcpy.RasterToPoint_conversion(boundaryRaster,
                                           boundaryPoints, 'Value')
            arcpy.GlobalPolynomialInterpolation_ga(boundaryPoints, "grid_code",
                                                   "#", pobfRaster, cellSize)
            arcpy.CalculateStatistics_management(pobfRaster)
            pobfTIN = os.path.join(d, 'planarTIN{}'.format(i))
            pobfs.append(pobfTIN)
            zTolerance = abs((int(Raster(pobfRaster).maximum) -
                              int(Raster(pobfRaster).minimum))/10)
            arcpy.RasterTin_3d(pobfRaster, pobfTIN, str(zTolerance))
            arcpy.EditTin_3d(pobfTIN, ["#", "<None>", "<None>",
                                       "hardclip", "false"])
            # Calculate Rugosity
            arcpy.PolygonVolume_3d(elevationTIN, each, "<None>",
                                   "BELOW", "Volume1", "Surf_Area")
            arcpy.PolygonVolume_3d(pobfTIN, each, "<None>",
                                   "BELOW", "Volume2", "Plan_Area")
            arcpy.AddField_management(each, "Rugosity", "DOUBLE")
            arcpy.CalculateField_management(each, "Rugosity",
                                            "[Surf_Area] / [Plan_Area]")
            arcpy.DeleteField_management(each, "Volume2;Volume1;Name")
            # Calculate Slope and Aspect
            arcpy.AddField_management(each, "Slope", "DOUBLE")
            arcpy.AddField_management(each, "Aspect", "DOUBLE")
            pobfXSize = Raster(pobfRaster).meanCellWidth
            pobfYSize = Raster(pobfRaster).meanCellHeight
            pobfArray = arcpy.RasterToNumPyArray(pobfRaster,
                                                 None, 3, 3)
            dz_dx = ((pobfArray[0, 2] + 2 * pobfArray[1, 2] +
                      pobfArray[2, 2]) -
                     (pobfArray[0, 0] + 2 * pobfArray[1, 0] +
                      pobfArray[2, 0])) / (8.0 * pobfYSize)
            dz_dy = ((pobfArray[2, 0] + 2 * pobfArray[2, 1] +
                      pobfArray[2, 2]) -
                     (pobfArray[0, 0] + 2 * pobfArray[0, 1] +
                      pobfArray[0, 2])) / (8.0 * pobfYSize)
            raw_aspect = (180 / np.pi) * np.arctan2(dz_dy, -dz_dx)
            if np.equal(dz_dy, dz_dx) and np.equal(dz_dy, 0):
                aspect = -1
            else:
                if np.equal(raw_aspect, 0):
                    aspect = 90
                elif np.equal(raw_aspect, 90):
                    aspect = 0
                elif raw_aspect > 90:
                    aspect = 360.0 - raw_aspect + 90
                else:
                    aspect = 90.0 - raw_aspect
            with arcpy.da.UpdateCursor(each, ["Slope", "Aspect"]) as cursor:
                for rows in cursor:
                    rows[0] = np.arctan(np.sqrt(dz_dx**2 +
                                                dz_dy**2))*(180/np.pi)
                    rows[1] = aspect
                    cursor.updateRow(rows)
            i += 1

        # Merge split files and save to input file location
        if multiple:
            arcpy.Merge_management(splitFiles, areaOfInterest)

        # Save TINs if requested
        if saveTINs:
            if workspace == None:
                out_dir = os.path.split(areaOfInterest)[0]
            else:
                out_dir = workspace
            utils.msg("Saving elevation and planar TINs to "
                      "{}...".format(out_dir))
            arcpy.CopyTin_3d(elevationTIN,
                             os.path.join(out_dir,
                                          '{}_elevationTIN'.format(rastName)))
            for x in range(len(pobfs)):
                name = os.path.join(out_dir,
                                    '{}_planarTIN{}'.format(rastName, x))
                arcpy.CopyTin_3d(pobfs[x], name)
