import os
import sys

# ArcGIS specific imports
import pythonaddins

# enable local imports
local_path = os.path.abspath(os.path.dirname(__file__))
btm_toolbox = os.path.join(local_path, "toolbox", "btm.pyt")


class DevNull:
    """
    Ignore exceptions with this class. Our workaround for current limiations
    in pythonaddins.GPToolDialog.
    """
    def write(self, msg):
        pass


def tool_dialog(toolbox, tool=None):
    """Error-handling wrapper around pythonaddins.GPToolDialog."""
    # FIXME: either have to supress stderr here or always get an error.
    # Contacted internal resources to figure out what's going on.
    # This is NIM089253 / CR245605
    try:
        err_default = sys.stderr
        sys.stderr = DevNull()
        if not tool:
            # assume that we're calling into a standard namespaced tool
            pythonaddins.GPToolDialog(toolbox)
        else:
            pythonaddins.GPToolDialog(toolbox, tool)
        sys.stderr = err_default
    except:
        print("recieved exception when trying to run GPToolDialog("
              "{toolbox}, {tool}))".format(toolbox=toolbox, tool=tool))
    return None


class ButtonRunBTMSteps(object):
    """Run all steps (wizard)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'runfullmodel')
        # TODO: trying to call multiple tools kills ArcMap.
        # adding a sleep() just slows down the train wreck. Not yet sure
        # of the best approach to actually get this to work.
        # tool_dialog(btm_toolbox, 'finescalebpi')
        # tool_dialog(btm_toolbox, 'standardizebpi')
        # update: this bug is documented in NIM085804; no current plans to fix it.
        #         Only one call is possible from an onClick event.


class RunBTMSteps(object):
    """Implementation for RunBTMSteps.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        # Can set to 'Line', 'Circle' or 'Rectangle' for
        # interactive shape drawing
        self.shape = "NONE"

    def onClick(self):
        tool_dialog(btm_toolbox, 'runfullmodel')


class setWorkspace(object):
    """Allow user to choose a workspace to use with the application."""
    def __init__(self):
        self.enabled = True

    def onClick(self):
        tool_dialog(btm_toolbox, 'setworkspace')

"""Classification functions"""


class classifyBenthicTerrain(object):
    """Implementation for classifyBenthicTerrain.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'classifyterrain')

#
# BPI specific functions


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

#
# Geomorphology convienience functions pulled in from spatial analyst


class calculateCurvature(object):
    """
    Implementation of arcpy.sa.Curvature(): can produce plan AND profile
    curvature through this one tool.
    """
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog('Curvature_sa')


class calculateAspect(object):
    """Wrapper for Aspect() from Spatial Analyst"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog('Aspect_sa')


class calculateStatisticalAspect(object):
    """
    Computes the trignometric identities for the circular variable aspect.
    """
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, "statisticalaspect")


class calculateDepthStatistics(object):
    """
    Depth statistics computes:
        - variance in depth
        - mean water depth
            + [sum(depth) / n cells]
            + arcpy.sa.Focal()
        - std dev. water depth
            + stddev = sqrt(variance)
            + arcpy.sa.Focal()
    """
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'depthstatistics')
        # TODO: handle adding the statistics to the current map when run


#
# New geomorphometry functions
class calculateArcChordRatio(object):
    """Implementation for arcChordRatio.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'arcchordratio')


class calculateSaPa(object):
    """Implementation for calculateSaPa.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'surfacetoplanar')


class calculateTerrainRuggedness(object):
    """Implementation for calculateTerrainRuggedness.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'terrainruggedness')


class calculateSlope(object):
    """Executes Slope() from Spatial Analyst, with units set to degrees."""
    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool_dialog(btm_toolbox, 'btmslope')


# multi-scale analysis menu
class calculateMetricsMultipleScales(object):
    """Batch generator for depth statistics that takes an input range of
       scales for analysis."""
    def __init__(self):
        self.enabled = True

    def onClick(self):
        tool_dialog(btm_toolbox, 'multiplescales')


class calculateScaleComparison(object):
    """Compare a dataset at multiple scales, using a variety of metrics."""
    def __init__(self):
        self.enabled = True

    def onClick(self):
        tool_dialog(btm_toolbox, 'scalecomparison')
