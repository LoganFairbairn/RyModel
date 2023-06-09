import bpy
import datetime

def log(message):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    print("[{0}]: {1}".format(datetime.datetime.now(), message))

def log_status(message, self, type='ERROR'):
    '''Prints the given message to Blender's console window and displays the message in Blender's status bar.'''
    log(message)
    self.report({type}, message)