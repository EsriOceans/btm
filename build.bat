@echo off
set addin_path="Z:\data\arcgis\addins\btm.esriaddin"
set cert_path="Z:\data\arcgis\addins\cert_2016.cer"
where /q python
IF ERRORLEVEL 1 (
    REM Assume default 10.4 location
    set py="c:\python27\ArcGIS10.4\python"
) ELSE (
    set py="python"
)
echo Building addin...
"%py%" makeaddin.py
echo Signing addin...
"c:\Program Files (x86)\Common Files\ArcGIS\bin\ESRISignAddin.exe" "%addin_path%" /c:"%cert_path%"
set runTest=n
set /p runTest=Would you like to run the test suite? y/N: 

if "%runTest%" == "y" GOTO runtests
echo Skipping tests.
GOTO install

:runtests
echo Executing tests...
"%py%" tests/testMain.py
GOTO install

:install
set install=n
set /p install=Would you like to install the add-in? y/N:
if "%install%" == "y" GOTO installAddin
echo Skipping installation.
GOTO end

:installAddin
start ../btm.esriaddin
:end
