@echo off
where /q python
IF ERRORLEVEL 1 (
    REM Assume default 10.4 location
    set py="c:\python27\ArcGIS10.4\python"
) ELSE (
    set py="python"
)
where /q nosetests
IF ERRORLEVEL 1 (
   set nose="c:\python27\ArcGIS10.4\Scripts\nosetests"
) ELSE (
   set nose="nosetests"
)
echo Building Add-in
"%py%" ./makeaddin.py
echo Running Tests
%nose% -v
