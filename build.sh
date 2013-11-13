#!/usr/bin/bash
echo "building Addin..."
python ./makeaddin.py
echo "signing Addin..."
"/c/Program Files (x86)/Common Files/ArcGIS/bin/ESRISignAddin.exe" c:\\data\\arcgis\\addins\\btm.esriaddin /c:c:\\data\\arcgis\\addins\\cert.cer
echo "executing tests..."
python tests/testMain.py
echo "If tests passed, type 'y'; to install addin."
read input

if [ "$input" == "y" ]; then
  start ../btm.esriaddin
else
  echo 'skipping installation.'
fi
