# This module contains user preferences for this add-on.

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty

ADDON_NAME = __package__

EXPORTING_TEMPLATE = [
    ("FBX", "fbx", "Exports selected objects as fbx files", '', 0),
    ("OBJ", "obj", "Exports selected objects as obj files", '', 0),
    ("UNITY_FBX", "Unity (fbx)", "Exports selected objects as fbx files specifically for the Unity game engine", '', 1),
]

class AddonPreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    save_imported_textures: BoolProperty(
        name="Save Imported Textures", 
        default=True,
        description="Saves all imported textures to the 'Layers' folder. This helps provided a constant external folder for saving images used in layers which helps keep your files consistent."
    )

    export_template: EnumProperty(
        items=EXPORTING_TEMPLATE,
        default='FBX',
        name="Exporting Template"
    )

    export_selected_objects_individually: BoolProperty(
        name="Export Selected Objects Individually",
        default=False,
        description="If true, all selected objects will be exported as individual files when using the export button in this add-on"
    )

    def draw(self, context):
        layout = self.layout
        #layout.prop(self, "auto_delete_unused_images")