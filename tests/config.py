# our constants.

import os

local_path = os.path.dirname(__file__)

xml_doc = os.path.abspath(os.path.join(local_path, 'data', 'fagatelebay_zone.xml'))
csv_doc = os.path.abspath(os.path.join(local_path, 'data', 'fagatelebay_zone.csv'))
bathy_raster = os.path.abspath(os.path.join(local_path, 'data', 'bathy5m_clip.tif'))

pyt_file = os.path.abspath(os.path.join(local_path, '..', 'Install', 'toolbox', 'btm.pyt'))
