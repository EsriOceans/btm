
echo "on disk"
python bpi.py Z:/data/workspace/bathy5m.tif 1 20 Z:/data/workspace/fizz.tif broad
echo "in mem"
python bpi-inmem.py Z:/data/workspace/bathy5m.tif 1 20 Z:/data/workspace/fizz.tif broad
echo "scipy"
python bpi-scipy.py
