import arcpy
import numpy
import scipy.ndimage as nd
import time
from matplotlib import pyplot as plt

t0 = time.time()
ras = "Z:/data/workspace/bathy5m.tif"
arcpy.env.overwriteOutput = True

r = arcpy.RasterToNumPyArray(ras, "", 200, 200, 0) # last is nodata value

fig = plt.figure(figsize=(10, 10))
#fig.tight_layout()
#gs = matplotlib.gridspec.GridSpec(4, 4)

std = numpy.divide(numpy.subtract(r, r.mean()), r.std())
med = nd.median_filter(std, 10)
plt.imshow(std, interpolation='nearest')

#rr = arcpy.NumPyArrayToRaster(med)
#rr.save("Z:/data/workspace/fizzbo.tif")

plt.colorbar()
plt.savefig("std.png", bbox_inches='tight')

print "scipy time: %.2f" % (time.time() - t0)

#outRaster = Int(Plus(Times(Divide(
#                Minus(bpi_raster, float(bpi_mean)), float(bpi_std_dev)), 100), 0.5))
