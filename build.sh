#!/usr/bin/bash
echo "building addin..."
python ./makeaddin.py
echo "signing addin..."
"/c/Program Files (x86)/Common Files/ArcGIS/bin/ESRISignAddin.exe" c:\\data\\arcgis\\addins\\btm.esriaddin /c:c:\\data\\arcgis\\addins\\cert.cer
echo "Would you like to run the test suite? y/N"
read input

if [ "$input" == "y" ]; then
  echo "executing tests..."
  python tests/testMain.py
else
  echo "skipping tests."
fi

echo "Would you like to install the add-in? y/N"
read input

if [ "$input" == "y" ]; then
  start ../btm.esriaddin
else
  echo 'skipping installation.'
fi
