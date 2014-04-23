import arcpy
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


for i in xrange(25):
    size = (i+1) * 3
    print "running {}".format(size)
    med = nd.median_filter(r, size)
   
    #rm = med - prev
    a = fig.add_subplot(5, 5,i+1)
    plt.imshow(med, interpolation='nearest')
    a.set_title('{}x{}'.format(size, size))
    plt.axis('off')
    plt.subplots_adjust(hspace = 0.1)
    prev = med
#fig.tight_layout()
#plt.colorbar()

#rr = arcpy.NumPyArrayToRaster(med)
#rr.save("Z:/data/workspace/fizzbo.tif")


plt.savefig("btm-scale-compare.png", bbox_inches='tight')
print "scipy time: %.2f" % (time.time() - t0)

#outRaster = Int(Plus(Times(Divide(
#                Minus(bpi_raster, float(bpi_mean)), float(bpi_std_dev)), 100), 0.5))
 
# ((r - r.mean()) / r.std()) * 100
