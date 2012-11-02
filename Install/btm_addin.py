import os
import sys

# ArcGIS specific imports
import arcpy
import arcpy.sa as sa
import pythonaddins

# enable local imports
local_path = os.path.dirname(__file__)

# only our custom model which can't be embedded in a Python toolbox.
model_toolbox = os.path.join(local_path, "toolbox", "btm model.tbx")
btm_toolbox = os.path.join(local_path, "toolbox", "btm.pyt")

# FIXME: add in checks for spatial analyst license.
# a wrapper around:
# arcpy.CheckOutExtension("spatial")
# which should get initialized, throw an error if it isn't available notifying them
# that MOST functions [e.g. slope] won't work without it.

def tool_dialog(toolbox, tool):
    """Error-handling wrapper around pythonaddins.GPToolDialog."""
    result = None
    try:
        result = pythonaddins.GPToolDialog(toolbox, tool)
        # FIXME: this is a hack to prevent:
        # TypeError: GPToolDialog() takes at most 1 argument (2 given)
        print '', 
    except TypeError:
        print "recieved TypeError when trying to run GPToolDialog(" + \
            "{toolbox}, {tool}))".format(toolbox=toolbox, tool=tool)
    # don't return anything. this prevents:
    #   TypeError: GPToolDialog() takes at most 1 argument (2 given)
    return result

""" Run all steps (wizard) """
class ButtonRunBTMSteps(object):
    """Implementation for runBTMSteps.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(model_toolbox, 'BtmModel')
        # XXX: trying to call multiple tools just kills ArcMap.
        # adding a sleep() just slows down the train wreck. Not yet sure
        # of the best approach to actually get this to work.
        # Still broken after SP1, so it may take till SP2 before a fix
        # is available.
        #tool_dialog(btm_toolbox, 'finescalebpi')
        #tool_dialog(btm_toolbox, 'standardizebpi')

class RunBTMSteps(object):
    """Implementation for RunBTMSteps.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing
    def onClick(self):
        pythonaddins.GPToolDialog(model_toolbox, 'BtmModel')
 
""" classification functions"""
class classifyBenthicTerrain(object):
    """Implementation for classifyBenthicTerrain.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'zoneclassification')


""" BPI specific functions """
class calculateBroadBPI(object):
    """Implementation for caculateBroadBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'broadscalebpi')

class calculateFineBPI(object):
    """Implementation for caculateFineBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'finescalebpi')

class standarizeBPI(object):
    """Implementation for standarizeBPI.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'standardizebpi')

""" Geomorphometry Functions """

#
# Convienience functions pulled in from spatial analyst
#


# arcpy.sa.Curvature() [can produce plan AND profile curvature through this one tool].
class calculateCurvature(object):
    """Implementation for calculateCurvature.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog("Spatial Analyst Tools", 'Curvature')

# arcpy.sa.Aspect()
class calculateAspect(object):
    """Implementation for calculateAspect.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        # TODO: replace this with a custom tool that breaks
        # this result down into two data dimensions via basic trig.
        # See https://github.com/EsriOceans/btm/issues/10
        tool_dialog("Spatial Analyst Tools", 'Aspect')

#- variance in depth
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
        tool_dialog(btm_toolbox, 'depthstatistics')

        # XXX: handle adding the statistics to the current map when run


# New geomorphometry functions
#

#class calculateRugosity(object):
#    """Implementation for calculateRugosity.button (Button)"""
#    def __init__(self):
#        self.enabled = True
#        self.checked = False
#    def onClick(self):
#        tool_dialog(btm_toolbox, 'rugosity')

class calculateTerrainRuggedness(object):
    """Implementation for calculateTerrainRuggedness.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'terrainruggedness')

# wrapped with parameters set
class calculateSlope(object):
    """Implementation for calculateSlope.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        tool_dialog(btm_toolbox, 'btmslope')
