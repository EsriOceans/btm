import sys
import traceback

import arcpy
import config

def msg(output_msg, mtype='message'):
    if mtype == 'error':
        arcpy_messages = arcpy.GetMessages()
        # output_msg came from the exception, pull out just message, 
        # add context from ArcPy.
        error_text = output_msg.message + arcpy_messages

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        if config.mode == 'script':
            err_msg = "ArcPy Error: {msg_text}\nPython Error: ${tbinfo}".format(
                msg_text=error_text, tbinfo=tbinfo)
            print err_msg
        else:
            arcpy.AddError(error_text)
            arcpy.AddMessage("Python Error: ${tbinfo}".format(tbinfo=tbinfo))
    elif config.mode == 'script':
        print output_msg
    else:
        if mtype == 'message':
            arcpy.AddMessage(output_msg)
        elif mtype == 'warning':
            arcpy.AddWarning(output_msg)
