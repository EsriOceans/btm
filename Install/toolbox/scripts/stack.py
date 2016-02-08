import arcpy
import glob
import os

workspace = r'Z:\data\workspace\depths_multiple'

raster_paths = glob.glob(os.path.join(workspace, 'win*'))
# full paths
raster_paths_full = glob.glob(os.path.join(workspace, 'win*/*.tif'))
# just the step names
step_labels = [os.path.basename(path) for path in raster_paths]

out_stats_raw = "'Mean Depth';'Standard Deviation';'Variance'"
out_stats = out_stats_raw.replace("'", '').split(";")
raster_names = {
    'Mean Depth': "meandepth",
    'Standard Deviation': "stddevdepth",
    'Variance': "vardepth"
}

# create a filegdb for all our outputs
output_gdb = 'stacks.gdb'
gdb_path = os.path.join(workspace, output_gdb)
if not os.path.exists(gdb_path):
    arcpy.CreateFileGDB_management(workspace, output_gdb)

# get a spatial reference from one of our rasters
desc = arcpy.Describe(raster_paths_full[0])
sr = desc.spatialReference

for stat in out_stats:
    # individual raster name for path
    raster_base = raster_names[stat]
    raster_catalog = os.path.join(gdb_path, raster_base)

    # create a container raster catalog
    arcpy.CreateRasterCatalog_management(
        gdb_path, raster_base,
        raster_spatial_reference=sr,
        raster_management_type='UNMANAGED')

    stat_rasters = []
    for path in raster_paths:
        # path includes the window size, zero padded
        print os.path.basename(path)
        window = os.path.basename(path).split("_")[1]

        stat_rasters.append(
            os.path.join(path, "{raster_base}_{window}.tif".format(
                raster_base=raster_base,
                window=window)))

    rasters = ';'.join(stat_rasters)
    arcpy.RasterToGeodatabase_conversion(rasters, raster_catalog)

    arcpy.CalculateDefaultGridIndex_management(raster_catalog)

    # add fake 'date' fields
    arcpy.AddField_management(raster_catalog, 'window', 'DATE')
    arcpy.AddField_management(raster_catalog, 'window_s', 'TEXT')

    fields = ['Name', 'window', 'window_s']
    with arcpy.da.UpdateCursor(raster_catalog, fields) as cursor:
        for row in cursor:
            # we stuff the raster full name in as a hack to get the 
            # true window size. Parse out the size:  win_003.tif -> 003

            win_size = os.path.splitext(row[0])[0].split("_")[1]

            # set output date to 'win_size-01-01'
            row[1] = datetime.date(int(win_size), 1, 1)
            row[2] = '0' + win_size
            cursor.updateRow(row)
