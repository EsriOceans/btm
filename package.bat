@echo off
REM build and ship a new release of the software
REM tools required: git, pandoc, zip, unzip. To install:
REM   choco install -y git pandoc zip unzip
REM then start from within a command prompt session.

REM TODO: make this more generic and less tied to BTM exclusively and to
REM promote reuse for other projects.

REM run the build script build 
echo Building code...
call build

REM tag the resulting version with a new tag
REM TODO: inspect the current tag list to set the version.
REM TODO: update the config.xml
REM the tag version should be named 'v$MAJOR.$MINOR{-$subversion}'. 
REM There is also version parsing code in the python stdlib I believe.
set PROJECT=btm
set VERSION=3.0-final
set RELEASE_BASE=../btm-release
set RELEASE_NAME=%PROJECT%-%VERSION%
set RELEASE_DIR="%RELEASE_BASE%/%RELEASE_NAME%"
set RELEASE_ARCHIVE=%RELEASE_NAME%.zip 

if EXIST %RELEASE_DIR% (
    rmdir /q /s %RELEASE_DIR%
)
mkdir %RELEASE_DIR%

echo Copying resources...
REM copy in our addin compiled with makeaddin.py (run within build.bat)
set closed=n
set /p closed=Is the add-in installed or otherwise closed? (y/N) 
if "%closed%" == "y" (
    copy ..\btm.esriaddin %RELEASE_DIR% > nul
) else (
  echo Can't build add-in when currently in-use.
  exit /b
)

REM export the 'clean repository' to get rid of anything which is git ignored
REM using third-party git-archive-all, otherwise we miss the datatypes submodule
REM NOTE: currently requires install from git:
REM         pip install git+https://github.com/Kentzo/git-archive-all
echo Build Git archive...
git-archive-all tmp.zip
echo Extracting archive...
unzip -q tmp.zip

REM copy in our toolbox elements to the release so it's usable from the 
REM catalog view.
echo Add toolbox to archive...
xcopy tmp\Install\toolbox %RELEASE_DIR% /e /q
rmdir /q /s tmp
del tmp.zip

REM add tutorial and data; skip hidden
echo Add tutorial and tutorial data...
set TUTORIAL_DIR=%RELEASE_DIR%\tutorial
mkdir %TUTORIAL_DIR%
copy ..\btm-tutorial\*.pdf %TUTORIAL_DIR% > nul
xcopy ..\btm-tutorial\sample_data %TUTORIAL_DIR% /q

REM Add readme, plain and HTML
echo Converting documentation to HTML...
copy README.md %RELEASE_DIR%\README.txt > nul
pandoc -t html README.md > %RELEASE_DIR%\README.html

echo Re-creating archive...
REM compress result
set repo_dir=%cd%
cd %RELEASE_BASE%
if EXIST %RELEASE_ARCHIVE% (
    del %RELEASE_ARCHIVE%
)
set RELEASE_ABS=%cd%
zip -qr9 %RELEASE_ARCHIVE% %RELEASE_NAME%
echo Completed build for %RELEASE_NAME%, archive: %RELEASE_ABS%\%RELEASE_ARCHIVE%
REM rename to meet asinine limitation
copy %RELEASE_ARCHIVE% "btm-3.0-beta.zip"
cd %repo_dir%

REM TODO: tag the resulting version with a new tag
REM git tag -a v${VERSION} -m '3.0 release candidate 1'
