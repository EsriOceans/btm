#!/bin/env bash

# build and ship a new release of the software
# tools required: bash, pandoc, zip

# TODO: make this more generic and less tied to BTM exclusively and to
# promote reuse for other projects.

# run the build script build 
echo "building code..."
./build.sh 

# tag the resulting version with a new tag
# TODO: inspect the current tag list to set the version.
# TODO: update the config.xml
# the tag version should be named 'v$MAJOR.$MINOR{-$subversion}'. 
# There is also version parsing code in the python stdlib I believe.
PROJECT='btm'
VERSION='3.0-rc-2'
RELEASE_BASE='../btm-release'
RELEASE_NAME="${PROJECT}-${VERSION}"
RELEASE_DIR="${RELEASE_BASE}/${RELEASE_NAME}"
RELEASE_ARCHIVE=${RELEASE_NAME}.zip 

if [ -d "${RELEASE_DIR}" ]; then
    rm -rf "${RELEASE_DIR}"
fi
mkdir ${RELEASE_DIR}

echo "copying resources..."
# copy in our addin compiled with makeaddin.py (run within build.sh)
echo "is the add-in installed or otherwise closed? (y/N)" 
read input

if [ "$input" == "y" ]; then
    cp ../btm.esriaddin ${RELEASE_DIR}/
else
  echo "can't build add-in when currently in-use."
  exit
fi

# copy in our toolbox elements to the release so it's usable from the 
# catalog view.
cp -Rp Install/toolbox ${RELEASE_DIR}/

# add tutorial and data; skip hidden
TUTORIAL_DIR=${RELEASE_DIR}/tutorial
mkdir ${TUTORIAL_DIR}
cp -p ../btm-tutorial/*.pdf ${TUTORIAL_DIR}/
cp -Rp ../btm-tutorial/sample_data ${TUTORIAL_DIR}/

# add readme, plain and HTML
cp README.md ${RELEASE_DIR}/README.txt
pandoc -t html README.md > ${RELEASE_DIR}/README.html

echo "creating archive..."
# compress result
repo_dir=`pwd`
cd ${RELEASE_BASE}
if [ -e "${RELEASE_ARCHIVE}" ]; then
    rm ${RELEASE_ARCHIVE}
fi
RELEASE_ABS=`pwd`
zip -qr9 ${RELEASE_ARCHIVE} ${RELEASE_NAME}
echo "completed build for ${RELEASE_NAME}, archive: ${RELEASE_ABS}/${RELEASE_ARCHIVE}"
# rename to meet asinine limitation
cp ${RELEASE_ARCHIVE} "btm-3.0-beta.zip"
cd ${repo_dir}

# TODO: tag the resulting version with a new tag
# git tag -a v${VERSION} -m '3.0 release candidate 1'


