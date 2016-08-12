import arcpy
import numpy as np
import sys
import scripts.config as config
import scripts.utils as utils
from matplotlib import pyplot as plt

if not utils.SCIPY_EXISTS:
    utils.msg("This tool requires the SciPy module to be " +
              "installed. SciPy is included in ArcGIS 10.4 " +
              "and later versions.", "error")
    sys.exit()
else:
    import scipy.ndimage as nd


def main(in_raster=None, img_filter=None, percentile=None,
         min_nbhs=None, max_nbhs=None, out_file=True):

    r = arcpy.RasterToNumPyArray(in_raster, "", 200, 200, 0)
    if r.ndim > 2:
        r = np.squeeze(r[0, :, :])
    min_nbhs = int(min_nbhs)
    max_nbhs = int(max_nbhs)

    fig = plt.figure(figsize=(10, 10))
    i = 0
    # cast with astype instead of using dtype= for Numpy 1.7 compat
    sizes = np.linspace(min_nbhs, max_nbhs, num=25, endpoint=True,
                        retstep=False).astype('uint32')
    for size in sizes:
        utils.msg("Processing neighborhood size {}".format(size))
        perc = ""
        if percentile is not None:
            perc = "{},".format(percentile)
        filterexec = "nd.{}_filter(r,{}{})".format(img_filter.lower(), perc, size)
        med = eval(filterexec)

        a = fig.add_subplot(5, 5, i+1)
        plt.imshow(med, interpolation='nearest')
        a.set_title('{}x{}'.format(size, size), fontsize=8)
        plt.axis('off')
        plt.subplots_adjust(hspace=0.01, wspace=0.09)
        i += 1

    plt.savefig(out_file, bbox_inches='tight')
    return


# when executing as a standalone script get parameters from sys
if __name__ == '__main__':
    config.mode = 'script'
    main(in_raster=sys.argv[1],
         img_filter=sys.argv[2],
         percentile=sys.argv[3],
         min_nbhs=sys.argv[4],
         max_nbhs=sys.argv[5],
         out_file=sys.argv[6])
