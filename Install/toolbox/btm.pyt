# -*- coding: utf-8 -*-

import contextlib
import os
import string
import sys

import arcpy
from arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# You can ignore/delete this code; these are basic utility functions to
# streamline porting

@contextlib.contextmanager
def script_run_as(filename, args=None):
    oldpath = sys.path[:]
    oldargv = sys.argv[:]
    newdir = os.path.dirname(filename)
    sys.path = oldpath + [newdir]
    sys.argv = [filename] + [arg.valueAsText for arg in (args or [])]
    oldcwd = os.getcwdu()
    os.chdir(newdir)

    try:
        # Actually run
        yield filename
    finally:
        # Restore old settings
        sys.path = oldpath
        sys.argv = oldargv
        os.chdir(oldcwd)

def set_parameter_as_text(params, index, val):
    if (hasattr(params[index].value, 'value')):
        params[index].value.value = val
    else:
        params[index].value = val

# Export of toolbox c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx

class Toolbox(object):
    def __init__(self):
        self.label = u'Benthic Terrain Modeler'
        self.alias = ''
        self.tools = [broadscalebpi, finescalebpi, standardizebpi, slope, zoneclassification, structureclassification, terrainruggedness]

# Tool implementation code

class broadscalebpi(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\broadscalebpi"""
    class ToolValidator:
      """Class for validating a tool's parameter values and controlling
      the behavior of the tool's dialog."""
    
      def __init__(self, parameters):
        """Setup arcpy and the list of tool parameters."""
        self.params = parameters
    
      def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        return
    
      def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
        return
    
      def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def __init__(self):
        self.label = u'1. Build Broad Scale BPI'
        self.description = u'The concept of bathymetric position is central to the benthic\r\nterrain classification process that is utilized by the BTM.\r\nBathymetric Position Index (BPI) is a measure of where a\r\nreferenced location is relative to the locations surrounding it.\r\nBPI is derived from an input bathymetric data set and itself is a modification of the topographic position index (TPI) algorithm that is used in the terrestrial environment. The application of TPI to develop terrain classifications was explored and developed by Andrew Weiss during his study of terrestrial watersheds in Central Oregon (Weiss 2001). These\r\napplications can be carried into the benthic environment\r\nthrough BPI.\r\n\r\nA broad-scale BPI data set allows you to identify larger features within the benthic landscape.'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Input_bathymetric_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_bathymetric_raster'
        param_1.displayName = u'Input bathymetric raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Inner_radius
        param_2 = arcpy.Parameter()
        param_2.name = u'Inner_radius'
        param_2.displayName = u'Inner radius'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.dataType = u'Long'

        # Outer_radius
        param_3 = arcpy.Parameter()
        param_3.name = u'Outer_radius'
        param_3.displayName = u'Outer radius'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.dataType = u'Long'

        # Output_raster
        param_4 = arcpy.Parameter()
        param_4.name = u'Output_raster'
        param_4.displayName = u'Output raster'
        param_4.parameterType = 'Required'
        param_4.direction = 'Output'
        param_4.dataType = u'Raster Dataset'

        return [param_1, param_2, param_3, param_4]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\broad_scale_bpi.py'):
            # broad_scale_bpi.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Check out any necessary licenses
            arcpy.CheckOutExtension("Spatial")
            
            # Script arguments
            Bathy = sys.argv[1]
            BroadInnerRadius = sys.argv[2]
            BroadOuterRadius = sys.argv[3]
            BroadOutRaster = sys.argv[4]
            
            try:
                # Create the broad-scale Bathymetric Position Index (BPI) raster
                messages.AddMessage("Generating the broad-scale Bathymetric Position Index (BPI) raster...")
                outFocalStatistics = FocalStatistics(Bathy, NbrAnnulus(BroadInnerRadius, BroadOuterRadius, "CELL"), "MEAN")
                outRaster = Int(Plus(Minus(Bathy, outFocalStatistics), 0.5))
                outRaster.save(BroadOutRaster)
            
            except:
                # Print error message if an error occurs
                arcpy.GetMessages()
            

class finescalebpi(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\finescalebpi"""
    class ToolValidator:
      """Class for validating a tool's parameter values and controlling
      the behavior of the tool's dialog."""
    
      def __init__(self, parameters):
        """Setup arcpy and the list of tool parameters."""
        self.params = parameters
    
      def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        return
    
      def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
        return
    
      def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def __init__(self):
        self.label = u'2. Build Fine Scale BPI'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Input_bathymetric_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_bathymetric_raster'
        param_1.displayName = u'Input bathymetric raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Inner_radius
        param_2 = arcpy.Parameter()
        param_2.name = u'Inner_radius'
        param_2.displayName = u'Inner radius'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.dataType = u'Long'

        # Outer_radius
        param_3 = arcpy.Parameter()
        param_3.name = u'Outer_radius'
        param_3.displayName = u'Outer radius'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.dataType = u'Long'

        # Output_raster
        param_4 = arcpy.Parameter()
        param_4.name = u'Output_raster'
        param_4.displayName = u'Output raster'
        param_4.parameterType = 'Required'
        param_4.direction = 'Output'
        param_4.dataType = u'Raster Dataset'

        return [param_1, param_2, param_3, param_4]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\fine_scale_bpi.py'):
            # fine_scale_bpi.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Check out any necessary licenses
            arcpy.CheckOutExtension("Spatial")
            
            # Script arguments
            Bathy = sys.argv[1]
            FineInnerRadius = sys.argv[2]
            FineOuterRadius = sys.argv[3]
            FineOutRaster = sys.argv[4]
            
            try:
                # Create the fine-scale Bathymetric Position Index (BPI) raster
                messages.AddMessage("Generating the fine-scale Bathymetric Position Index (BPI) raster...")
                outFocalStatistics = FocalStatistics(Bathy, NbrAnnulus(FineInnerRadius, FineOuterRadius, "CELL"), "MEAN")
                outRaster = Int(Plus(Minus(Bathy, outFocalStatistics), 0.5))
                outRaster.save(FineOutRaster)
            
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()
            

class standardizebpi(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\standardizebpi"""
    def __init__(self):
        self.label = u'3. Standardize BPIs'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Input_BPI_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_BPI_raster'
        param_1.displayName = u'Input BPI raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Output_raster
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_raster'
        param_2.displayName = u'Output raster'
        param_2.parameterType = 'Required'
        param_2.direction = 'Output'
        param_2.dataType = u'Raster Dataset'

        return [param_1, param_2]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\standardize_bpi_grids.py'):
            # standardize_bpi_grids.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Check out any necessary licenses
            arcpy.CheckOutExtension("Spatial")
            
            # Script arguments
            BPIRaster = sys.argv[1]
            OutRaster = sys.argv[2]
            
            try:
                # Get raster properties
                messages.AddMessage("Calculating properties of the Bathymetric Position Index (BPI) raster...")
                result1 = arcpy.GetRasterProperties_management(BPIRaster, "MEAN")
                BPIMean = result1.getOutput(0)
                messages.AddMessage("The mean of the BPI raster is " + str(BPIMean) + ".")
                result2 = arcpy.GetRasterProperties_management(BPIRaster, "STD")
                BPIStdDev = result2.getOutput(0)
                messages.AddMessage("The standard deviation of the BPI raster is " + str(BPIStdDev) + ".")
                
                # Create the standardized Bathymetric Position Index (BPI) raster
                messages.AddMessage("Standardizing the Bathymetric Position Index (BPI) raster...")
                outRaster = Int(Plus(Times(Divide(Minus(BPIRaster, float(BPIMean)), float(BPIStdDev)), 100), 0.5))
                outRaster.save(OutRaster)
            
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()

class slope(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\slope"""
    def __init__(self):
        self.label = u'4. Calculate Slope'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Input_bathymetric_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_bathymetric_raster'
        param_1.displayName = u'Input bathymetric raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Output_raster
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_raster'
        param_2.displayName = u'Output raster'
        param_2.parameterType = 'Required'
        param_2.direction = 'Output'
        param_2.dataType = u'Raster Dataset'

        return [param_1, param_2]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\slope.py'):
            # slope.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Check out any necessary licenses
            arcpy.CheckOutExtension("Spatial")
            
            # Script arguments
            Bathy = sys.argv[1]
            OutRaster = sys.argv[2]
            
            try:
                # Calculate the slope of the bathymetric raster
                messages.AddMessage("Calculating the slope...")
                outSlope = Slope(Bathy, "DEGREE", 1)
                outSlope.save(OutRaster)
            
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()

class zoneclassification(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\zoneclassification"""
    def __init__(self):
        self.label = u'5. Zone Classification Builder'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Standardized_broad-scale_BPI_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Standardized_broad-scale_BPI_raster'
        param_1.displayName = u'Standardized broad-scale BPI raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Slope_raster
        param_2 = arcpy.Parameter()
        param_2.name = u'Slope_raster'
        param_2.displayName = u'Slope raster'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.dataType = u'Raster Layer'

        # Standard_deviation_break
        param_3 = arcpy.Parameter()
        param_3.name = u'Standard_deviation_break'
        param_3.displayName = u'Standard deviation break'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.dataType = u'Double'

        # Slope_value__in_degrees__indicating_a_gentle_slope
        param_4 = arcpy.Parameter()
        param_4.name = u'Slope_value__in_degrees__indicating_a_gentle_slope'
        param_4.displayName = u'Slope value (in degrees) indicating a gentle slope'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.dataType = u'Double'

        # Output_raster
        param_5 = arcpy.Parameter()
        param_5.name = u'Output_raster'
        param_5.displayName = u'Output raster'
        param_5.parameterType = 'Required'
        param_5.direction = 'Output'
        param_5.dataType = u'Raster Dataset'

        return [param_1, param_2, param_3, param_4, param_5]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\zone_classification.py'):
            # zone_classification.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Script arguments
            BPIRaster = sys.argv[1]
            SlopeRaster = sys.argv[2]
            StdDevDiv = sys.argv[3]
            SlopeDiv = sys.argv[4]
            OutRaster = sys.argv[5]
            
            try:
                # Get raster properties
                messages.AddMessage("Calculating properties of the standardized Bathymetric Position Index (BPI) raster...")
                result = arcpy.GetRasterProperties_management(BPIRaster, "STD")
                BPIStdDev = result.getOutput(0)
                messages.AddMessage("The standard deviation of the BPI raster is " + str(BPIStdDev) + ".")
                
                # Create the classified standardized Bathymetric Position Index (BPI) raster
                messages.AddMessage("Classifying the Bathymetric Position Index (BPI) raster...")
                CreDiv = float(StdDevDiv) * float(BPIStdDev)
                DepDiv = -1 * float(StdDevDiv) * float(BPIStdDev)
                outRaster = Con(Raster(BPIRaster) >= float(CreDiv), 1, Con(Raster(BPIRaster) <= float(DepDiv), 2, Con(Raster(SlopeRaster) <= float(SlopeDiv), 3, 4)))
                outRaster.save(OutRaster)
            
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()

class structureclassification(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\structureclassification"""
    def __init__(self):
        self.label = u'6. Structure Classification Builder'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Standardized_broad-scale_BPI_raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Standardized_broad-scale_BPI_raster'
        param_1.displayName = u'Standardized broad-scale BPI raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Broad-scale_BPI_standard_deviation_break
        param_2 = arcpy.Parameter()
        param_2.name = u'Broad-scale_BPI_standard_deviation_break'
        param_2.displayName = u'Broad-scale BPI standard deviation break'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.dataType = u'Double'

        # Standardized_fine-scale_BPI_raster
        param_3 = arcpy.Parameter()
        param_3.name = u'Standardized_fine-scale_BPI_raster'
        param_3.displayName = u'Standardized fine-scale BPI raster'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.dataType = u'Raster Layer'

        # Fine-scale_BPI_standard_deviation_break
        param_4 = arcpy.Parameter()
        param_4.name = u'Fine-scale_BPI_standard_deviation_break'
        param_4.displayName = u'Fine-scale BPI standard deviation break'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.dataType = u'Double'

        # Slope_raster
        param_5 = arcpy.Parameter()
        param_5.name = u'Slope_raster'
        param_5.displayName = u'Slope raster'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.dataType = u'Raster Layer'

        # Slope_value__in_degrees__indicating_a_gentle_slope
        param_6 = arcpy.Parameter()
        param_6.name = u'Slope_value__in_degrees__indicating_a_gentle_slope'
        param_6.displayName = u'Slope value (in degrees) indicating a gentle slope'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.dataType = u'Double'

        # Slope_value__in_degrees__indicating_a_steep_slope
        param_7 = arcpy.Parameter()
        param_7.name = u'Slope_value__in_degrees__indicating_a_steep_slope'
        param_7.displayName = u'Slope value (in degrees) indicating a steep slope'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.dataType = u'Double'

        # Bathymetric_raster
        param_8 = arcpy.Parameter()
        param_8.name = u'Bathymetric_raster'
        param_8.displayName = u'Bathymetric raster'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.dataType = u'Raster Layer'

        # Depth_indicating_break_between_shelf_and_broad_flat
        param_9 = arcpy.Parameter()
        param_9.name = u'Depth_indicating_break_between_shelf_and_broad_flat'
        param_9.displayName = u'Depth indicating break between shelf and broad flat'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.dataType = u'Double'

        # Output_raster
        param_10 = arcpy.Parameter()
        param_10.name = u'Output_raster'
        param_10.displayName = u'Output raster'
        param_10.parameterType = 'Required'
        param_10.direction = 'Output'
        param_10.dataType = u'Raster Dataset'

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9, param_10]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\structure_classification.py'):
            # structure_classification.py
            # Description: The Benthic Terrain Modeler (BTM) functions as a toolbox within ArcMap, and relies
            #              on a methodology to analyze benthic terrain from input multibeam bathymetry in ESRI's
            #              GRID (raster) format. The BTM toolbox contains a set of tools that allow users to
            #              create grids of slope, bathymetric position index and rugosity from an input data set.
            #              An integrated XML-based terrain classification dictionary gives users the freedom to
            #              create their own classifications and define the relationships that characterize them.
            # Requirements: Spatial Analyst 
            # Author: Dawn J. Wright, Emily R. Lundblad, Emily M. Larkin, Ronald W. Rinehart
            # Date: 2005
            # Converted 11/5/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to a Python Script that runs in ArcGIS 10.
            
            # Script arguments
            BroadBPIRaster = sys.argv[1]
            BroadStdDevDiv = sys.argv[2]
            FineBPIRaster = sys.argv[3]
            FineStdDevDiv = sys.argv[4]
            SlopeRaster = sys.argv[5]
            GentleSlopeDiv = sys.argv[6]
            SteepSlopeDiv = sys.argv[7]
            BathyRaster = sys.argv[8]
            DepthDiv = sys.argv[9]
            OutRaster = sys.argv[10]
            
            try:
                # Get raster properties
                messages.AddMessage("Calculating properties of the standardized broad-scale Bathymetric Position Index (BPI) raster...")
                result1 = arcpy.GetRasterProperties_management(BroadBPIRaster, "STD")
                BroadBPIStdDev = result1.getOutput(0)
                messages.AddMessage("The standard deviation of the broad-scale BPI raster is " + str(BroadBPIStdDev) + ".")
                messages.AddMessage("Calculating properties of the standardized fine-scale Bathymetric Position Index (BPI) raster...")
                result2 = arcpy.GetRasterProperties_management(FineBPIRaster, "STD")
                FineBPIStdDev = result2.getOutput(0)
                messages.AddMessage("The standard deviation of the fine-scale BPI raster is " + str(FineBPIStdDev) + ".")
                
                # Create the classified standardized Bathymetric Position Index (BPI) raster
                messages.AddMessage("Classifying the Bathymetric Position Index (BPI) raster...")
                BroadCreDiv = float(BroadStdDevDiv) * float(BroadBPIStdDev)
                BroadDepDiv = -1 * float(BroadStdDevDiv) * float(BroadBPIStdDev)
                FineCreDiv = float(FineStdDevDiv) * float(FineBPIStdDev)
                FineDepDiv = -1 * float(FineStdDevDiv) * float(FineBPIStdDev)
                outRaster = Con(((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv))), 1, # Narrow depression
                                Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)), 2, # Local depression on flat
                                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)), 3, # Lateral midslope depression
                                        Con((Raster(BroadBPIRaster) >= float(BroadCreDiv)) & (Raster(FineBPIRaster) <= float(FineDepDiv)), 4, # Depression on crest
                                            Con((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)), 5, # Broad depression with an open bottom
                                                Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)) & (Raster(BathyRaster) < float(DepthDiv)), 6, # Broad flat
                                                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)) & (Raster(BathyRaster) >= float(DepthDiv)), 7, # Shelf
                                                        Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)) & (Raster(SlopeRaster) <= float(SteepSlopeDiv)), 8, # Open slopes
                                                            Con((Raster(BroadBPIRaster) <= float(BroadDepDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)), 9, # Local crest in depression
                                                                Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)) & (Raster(SlopeRaster) <= float(GentleSlopeDiv)), 10, # Local crest on flat
                                                                    Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(BroadBPIRaster) < float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)) & (Raster(SlopeRaster) > float(GentleSlopeDiv)), 11, # Lateral midslope crest
                                                                        Con((Raster(BroadBPIRaster) >= float(BroadCreDiv)) & (Raster(FineBPIRaster) >= float(FineCreDiv)), 12, # Narrow crest
                                                                            Con((Raster(BroadBPIRaster) > float(BroadDepDiv)) & (Raster(FineBPIRaster) > float(FineDepDiv)) & (Raster(FineBPIRaster) < float(FineCreDiv)) & (Raster(SlopeRaster) > float(SteepSlopeDiv)), 13))))))))))))) # Steep slope
                outRaster.save(OutRaster)
            
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()

class terrainruggedness(object):
    """c:\data\arcgis\addins\btm\toolbox\noaa\BTM.tbx\Ruggedness(VRM)"""
    class ToolValidator:
      """Class for validating a tool's parameter values and controlling
      the behavior of the tool's dialog."""
    
      def __init__(self, parameters):
        """Setup arcpy and the list of tool parameters."""
        self.params = parameters
    
      def initializeParameters(self):
        """Refine the properties of a tool's parameters.  This method is
        called when the tool is opened."""
        return
    
      def updateParameters(self):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parmater
        has been changed."""
        return
    
      def updateMessages(self):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def __init__(self):
        self.label = u'7. Terrain Ruggedness (VRM)'
        self.canRunInBackground = False
    def getParameterInfo(self):
        # Elevation_Raster
        param_1 = arcpy.Parameter()
        param_1.name = u'Elevation_Raster'
        param_1.displayName = u'Elevation Raster'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.dataType = u'Raster Layer'

        # Neighborhood_Size
        param_2 = arcpy.Parameter()
        param_2.name = u'Neighborhood_Size'
        param_2.displayName = u'Neighborhood Size'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.dataType = u'Long'

        # Output_Workspace
        param_3 = arcpy.Parameter()
        param_3.name = u'Output_Workspace'
        param_3.displayName = u'Output Workspace'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.dataType = u'Workspace'

        # Output_Raster
        param_4 = arcpy.Parameter()
        param_4.name = u'Output_Raster'
        param_4.displayName = u'Output Raster'
        param_4.parameterType = 'Required'
        param_4.direction = 'Output'
        param_4.dataType = u'Raster Dataset'

        return [param_1, param_2, param_3, param_4]
    def isLicensed(self):
        return True
    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()
    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()
    def execute(self, parameters, messages):
        with script_run_as(u'c:\\data\\arcgis\\addins\\btm\\toolbox\\noaa\\ruggedness.py'):
            # ruggedness.py
            # Description: This tool measures terrain ruggedness by calculating the vector ruggedness measure
            #              described in Sappington, J.M., K.M. Longshore, and D.B. Thompson. 2007. Quantifying
            #              Landscape Ruggedness for Animal Habitat Analysis: A Case Study Using Bighorn Sheep in
            #              the Mojave Desert. Journal of Wildlife Management. 71(5): 1419 -1426.
            # Requirements: Spatial Analyst 
            # Author: Mark Sappington
            # Date: 2/1/2008
            # Updated 12/1/2010 by Emily C. Huntley of the Massachusetts Office of Coastal Zone Management
            # to run in ArcGIS 10.
           
            # FIXME: validate against http://arcscripts.esri.com/details.asp?dbid=15423
            
            # Check out any necessary licenses
            arcpy.CheckOutExtension("Spatial")
            
            # Script arguments
            InRaster = sys.argv[1]
            Neighborhood_Size = sys.argv[2]
            OutWorkspace = sys.argv[3]
            OutRaster = sys.argv[4]
            
            # Local variables
            AspectRaster = OutWorkspace + "\\aspect"
            SlopeRaster = OutWorkspace + "\\slope"
            SlopeRasterRad = OutWorkspace + "\\sloperad"
            AspectRasterRad = OutWorkspace + "\\aspectrad"
            xRaster = OutWorkspace + "\\x"
            yRaster = OutWorkspace + "\\y"
            zRaster = OutWorkspace + "\\z"
            xyRaster = OutWorkspace + "\\xy"
            xSumRaster = OutWorkspace + "\\xsum"
            ySumRaster = OutWorkspace + "\\ysum"
            zSumRaster = OutWorkspace + "\\zsum"
            ResultRaster = OutWorkspace + "\\result"
            
            try:
                # Create Slope and Aspect rasters
                messages.AddMessage("Calculating aspect...")
                outAspect = Aspect(InRaster)
                outAspect.save(AspectRaster)
                messages.AddMessage("Calculating slope...")
                outSlope = Slope(InRaster, "DEGREE")
                outSlope.save(SlopeRaster)
            
                # Convert Slope and Aspect rasters to radians
                messages.AddMessage("Converting slope and aspect to radians...")
                outTimes1 = Times(SlopeRaster,(3.14/180))
                outTimes1.save(SlopeRasterRad)
                outTimes2 = Times(AspectRaster,(3.14/180))
                outTimes2.save(AspectRasterRad)
            
                # Calculate x, y, and z rasters
                messages.AddMessage("Calculating x, y, and z rasters...")
                outSin = Sin(SlopeRasterRad)
                outSin.save(xyRaster)
                outCos = Cos(SlopeRasterRad)
                outCos.save(zRaster)
                OutRas1 = Times(Con(AspectRaster == -1, 0, Sin(AspectRasterRad)), xyRaster)
                OutRas1.save(xRaster)
                OutRas2 = Times(Con(AspectRaster == -1, 0, Cos(AspectRasterRad)), xyRaster)
                OutRas2.save(yRaster)
                
                # Calculate sums of x, y, and z rasters for selected neighborhood size
                messages.AddMessage("Calculating sums of x, y, and z rasters in selected neighborhood...")
                outFocalStatistics1 = FocalStatistics(xRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
                outFocalStatistics1.save(xSumRaster)
                outFocalStatistics2 = FocalStatistics(yRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
                outFocalStatistics2.save(ySumRaster)
                outFocalStatistics3 = FocalStatistics(zRaster, NbrRectangle(Neighborhood_Size, Neighborhood_Size, "CELL"), "SUM", "NODATA")
                outFocalStatistics3.save(zSumRaster)
            
                # Calculate the resultant vector
                messages.AddMessage("Calculating the resultant vector...")
                OutRas3 = SquareRoot(Square(xSumRaster) + Square(ySumRaster) + Square(zSumRaster))
                OutRas3.save(ResultRaster)
            
                # Calculate the Ruggedness raster
                messages.AddMessage("Calculating the final ruggedness raster...")
                maxValue = int(Neighborhood_Size) * int(Neighborhood_Size)
                OutRas4 = Minus(1, Divide(ResultRaster, maxValue))
                OutRas4.save(OutRaster)
            
                # Delete all intermediate raster data sets
                messages.AddMessage("Deleting intermediate data...")
                arcpy.Delete_management(AspectRaster)
                arcpy.Delete_management(SlopeRaster)
                arcpy.Delete_management(SlopeRasterRad)
                arcpy.Delete_management(AspectRasterRad)
                arcpy.Delete_management(xRaster)
                arcpy.Delete_management(yRaster)
                arcpy.Delete_management(zRaster)
                arcpy.Delete_management(xyRaster)
                arcpy.Delete_management(xSumRaster)
                arcpy.Delete_management(ySumRaster)
                arcpy.Delete_management(zSumRaster)
                arcpy.Delete_management(ResultRaster)
                
            except:
            # Print error message if an error occurs
                arcpy.GetMessages()
