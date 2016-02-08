

lyr_with_time = r'Z:\data\arcgis\addins\btm\Install\layers\depth_with_time.lyr'
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

arcpy.mapping.AddLayer(df, arcpy.mapping.Layer(lyr_with_time))

layers = arcpy.mapping.ListLayers(df)

lyr = layers[0] # the lyr file

"""
l.featureLayer: True

l.time shows time props (even though not enabled)

l.time.isTimeEnabled
"""

raster_catalog = r'Z:\data\workspace\depths_multiple\stacks.gdb\meandepth'

# replace the data source with our catalog
# THIS FAILS, why?
# lyr.replaceDataSource(raster_catalog, 'NONE')
lyr.replaceDataSource('Z:\\data\\workspace\\depths_multiple\\stacks.gdb', 'NONE', 'meandepth')

# TODO control time step interval? tried this:

"""
>>> lyr.time.timeStepInterval = arcpy.time.EsriTimeDelta(2.0, 'years')
Runtime error 
Traceback (most recent call last):
      File "<string>", line 1, in <module>
        File "c:\program files (x86)\arcgis\desktop10.3\arcpy\arcpy\arcobjects\_base.py", line 94, in _set
            (attr_name, self.__class__.__name__))
            NameError: The attribute 'timeStepInterval' is not supported on this instance of LayerTime.
"""
