# our constants.

import os

local_path = os.path.dirname(__file__)
data_path = os.path.join(local_path, 'data')

xml_doc = os.path.abspath(os.path.join(data_path, 'fagatelebay_zone.xml'))
csv_doc = os.path.abspath(os.path.join(data_path, 'fagatelebay_zone.csv'))
malformed_csv_doc = os.path.abspath(os.path.join(data_path, 'missing_comma_zone.csv'))
bathy_raster = os.path.abspath(os.path.join(data_path, 'bathy5m_clip.tif'))

pyt_file = os.path.abspath(os.path.join(local_path, '..', 'Install', 'toolbox', 'btm.pyt'))
