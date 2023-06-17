# This module contains user preferences for this add-on.

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty

ADDON_NAME = __package__

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=True,
        description="Saves all imported textures to the 'Layers' folder. This helps provided a constant external folder for saving images used in layers which helps keep your files consistent."
    )
    
    def draw(self, context):
        layout = self.layout
        #layout.prop(self, "auto_delete_unused_images")