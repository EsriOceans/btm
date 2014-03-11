Benthic Terrain Modeler
=======================

A set of tools useful in the analysis of benthic terrain. Includes tools for geomorphology and classification. 

Requirements
------------

ArcGIS 10.1 or greater. ArcGIS 10.0 is also supported, but only as a toolbox, as the Python Add-in was introduced at 10.1. Spatial Analyst Extension.

Installation
------------

The current release of the Add-in, Toolbox and demonstration data is [available on ArcGIS Online](http://www.arcgis.com/home/item.html?id=b0d0be66fd33440d97e8c83d220e7926)

Steps:
- Unzip the BTM zip file to your desired location.
- Close any existing ArcMap sessions.
- Double-click the btm.esriaddin file in your workspace, which will install both the graphical user interface and the toolbox into ArcGIS. 
- In addition to the user interface, you can also add the tools to ArcToolbox. Open the ArcToolbox window and pin it to the display. Right-click on the ArcToolbox top folder in the window and select Add Toolbox. Navigate to where you unzipped BTM and add the file btm.pyt.
- To view important documentation on each script right-click on that script in the BTM toolset and select Item Description as well as Properties. 
- Click on the Add Data button in ArcMap and proceed to add your bathymetry data to your ArcMap session. You may now run the BTM tools on your data.

![Installation](https://raw.github.com/EsriOceans/btm/master/resources/btm-install.gif)

To get the latest source, clone this repository, and run `makeaddin.py` to create an installable `btm.esriaddin`.

Using
-----

Install the Python Add-in `btm.esriaddin`, to access the graphical tools. The Python toolbox can be added by navigating to a path containing `btm.pyt`. All of the tools also support being run directly from the command-line (here btm is installed to the users directory in 'btm'):

    cd %HOME%\btm\Install\toolbox\scripts
    python bpi.py e:\\bathy5m 5 10 e:\\bpi_fine

Testing
-------

[Nose](https://nose.readthedocs.org/en/latest/) tests are included which perform basic checks. To run, first install nose:
    
    $ pip install nose

Then, run nose from the top-level directory:

    $ nosetests

Citing
------

We ask that you use the following citation for this software:

Wright, D.J., Pendleton, M., Boulware, J., Walbridge, S., Gerlt, B., Eslinger, D., Sampson, D., and Huntley, E. 2012. ArcGIS Benthic Terrain Modeler (BTM), v. 3.0, Environmental Systems Research Institute, NOAA Coastal Services Center, Massachusetts Office of Coastal Zone Management. Available online at [http://esriurl.com/5754](http://esriurl.com/5754).
