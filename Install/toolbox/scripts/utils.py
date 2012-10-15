import sys
import traceback

import arcpy
import config

def msg(msg_text, mtype='message'):
    if mtype == 'error':
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        if config.mode == 'script':
            err_msg = "ArcPy Error: {msg_text}\nPython Error: ${tbinfo}".format(
                msg_text=msg_text, tbinfo=tbinfo)
            print err_msg
        else:
            arcpy.AddMessage("Error encountered!")
            arcpy.AddMessage("Python Error: ${tbinfo}".format(tbinfo=tbinfo))
            arcpy.AddError(msg_text)
    elif config.mode == 'script':
        print msg_text
    else:
        if mtype == 'message':
            arcpy.AddMessage(msg_text)
        elif mtype == 'warning':
            arcpy.AddWarning(msg_text)
