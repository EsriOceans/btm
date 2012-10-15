# Author: Jen Boulware
# Date: October 2011
# Purpose: Generate a position index grid (focal mean)
# Requirements: Spatial Analyst Extension

# Import the cscCommonScript utility module which, in turn,  imports the 
#  standard library modules and imports arcpy
#EXPECTS 3 PARAMETERS, input bathy and output grid and neighborhood
# If running in PythonWin use C:\arcgis\data\BTM_Data\crml_bth C:\arcgis\data\mypig3 Annulus 1 3 CELL

import arcpy,sys, traceback
from arcpy.sa import * 
import cscCommonScript 


class LicenseError(Exception):
    pass

class InvalidParams(Exception):
    pass


cscCommonScript.getLogFile()

cscCommonScript.AddPrintMessage("CreatePosIndexGrid start", 0)  
# Start traceback Try-Except statement:
try:
    cscCommonScript.AddPrintMessage("Checking parameter count", 0) 
    if (cscCommonScript.checkPassedParamCount(3) == 1):
        raise InvalidParams
    
    #call our common licence check function- returns true if bad which bails the app
    
    cscCommonScript.AddPrintMessage("Getting Spatial Analyst License", 0) 
    if (cscCommonScript.checkSpatialLic() == 1):
        raise LicenseError

    arcpy.env.overwriteOutput = True 
        
    #Input bathy dataset
    inBathy = arcpy.GetParameterAsText(0)
    # Output BPI dataset
    outBPI = arcpy.GetParameterAsText(1)    
    # Focalmean analysis neighborhood settings 
    neighborhood = arcpy.GetParameterAsText(2)
    # Focalmean analysis stats type settings 
    statType ="MEAN" #arcpy.GetParameterAsText(4)
    # Focalmean analysis no data settings 
    noData = "DATA" #arcpy.GetParameterAsText(5)
        
    cscCommonScript.AddPrintMessage("Running Neighborhood Stats", 0)

    # Execute FocalStatistics
    outFocalStatistics = FocalStatistics(inBathy, neighborhood, statType,noData)
    
    cscCommonScript.AddPrintMessage("Processing Neighborhood Stats Output", 0)
    outTempBPI = Int(Plus((Minus(inBathy,outFocalStatistics)),.5))

    cscCommonScript.AddPrintMessage("Saving Output", 0)
    # Save the output 
    outTempBPI.save(outBPI)

except LicenseError:
    cscCommonScript.AddPrintMessage("Spatial Analyst license is unavailable", 2)     

except InvalidParams:
    cscCommonScript.AddPrintMessage("Please enter the necessary parameters", 2)  

except:
    cscCommonScript.AddPrintMessage("Uh-oh something went wrong", 2)  
    
    # Get the traceback object
    #
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    #
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + \
            "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    # Return python error messages for use in script tool or Python Window
    #
    cscCommonScript.AddPrintMessage(pymsg,3)
    cscCommonScript.AddPrintMessage(msgs,3)

    # Print Python error messages for use in Python / Python Window
    #
    print pymsg + "\n"
    print msgs

finally:
    # Check in the Spatial Analyst extension 
    arcpy.CheckInExtension("Spatial")
    
    cscCommonScript.closeLogFile()

   