import os
import sys

# ArcGIS specific imports
import arcpy
import arcpy.sa as sa
import pythonaddins

# enable local imports
local_path = os.path.dirname(__file__)
sys.path.insert(0, local_path)

# FIXME: check if this is the best approach; alt is to look up system install dir and load that TBX.
custom_toolbox = os.path.join(local_path, "toolboxes", "custom.tbx")

# FIXME: add in checks for spatial analyst license.
# a wrapper around:
# arcpy.CheckOutExtension("spatial")
# which should get initialized, throw an error if it isn't available notifying them
# that MOST functions [e.g. slope] won't work without it.

""" Run all steps (wizard) """
class ButtonRunBTMSteps(object):
    """Implementation for runBTMSteps.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class RunBTMSteps(object):
    """Implementation for RunBTMSteps.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        pass
    def onDblClick(self):
        pass
    def onKeyDown(self, keycode, shift):
        pass
    def onKeyUp(self, keycode, shift):
        pass
    def deactivate(self):
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        pass

""" classification functions"""
class classifyBenthicTerrain(object):
    """Implementation for classifyBenthicTerrain.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass


""" BPI specific functions """
class calculateBroadBPI(object):
    """Implementation for caculateBroadBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class calculateFineBPI(object):
    """Implementation for caculateFineBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

class standarizeBPI(object):
    """Implementation for standarizeBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

""" Geomorphometry Functions """

#
# Convienience functions pulled in from spatial analyst
#


class calculateSlope(object):
    """Implementation for calculateSlope.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        sa.Slope()
        pass

# arcpy.sa.Curvature() [can produce plan AND profile curvature through this one tool].
class calculateCurvature(object):
    """Implementation for calculateCurvature.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

# arcpy.sa.Aspect()
class calculateAspect(object):
    """Implementation for calculateAspect.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass

#- mean water depth 
#    + [sum(depth) / n cells] 
#    + arcpy.sa.Focal()
#- std dev. water depth
#    + stddev = sqrt(variance)
#    + arcpy.sa.Focal()
class calculateDepthStatistics(object):
    """Implementation for calculateDepthStatistics.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.MessageBox("This method is not yet implemented. should compute focal statistics [mean, stddev] on raster.", "Unable to calculate Depth Statistics")

#
# New geomorphometry functions
#
class calculateRugosity(object):
    """Implementation for calculateRugosity.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pass
