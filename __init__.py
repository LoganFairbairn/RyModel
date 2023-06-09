# Copyright (c) 2021-2023 Logan Fairbairn
# logan-fairbairn@outlook.com
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# This file imports and registers all required modules for this add-on.

import bpy

# Import operators.
from .quick_operators import RyModel_Mirror, RyModel_ResetOrigin, RyModel_AddModifier, RyModel_CopyModifiers, RyModel_AutoSharpen, RyModel_CleanMesh, RyModel_RadialArray, RyModel_CurveToRope, RyModel_Cheshire, RyModel_HSWFModApply, RyModel_AddCutter, RyModel_HideCutters, RyModel_ShowCutters, RyModel_RemoveUnusedCutters, RyModel_Unwrap, RyModel_AutoSeam

# Import user interface.
from .ui_main import RyModel_OT_open_menu, RyModel_OT_open_radial_array_menu, ADDON_VERSION_NUMBER

bl_info = {
    "name": "RyModel",
    "author": "Logan Fairbairn (Ryver)",
    "version": (ADDON_VERSION_NUMBER[0], ADDON_VERSION_NUMBER[1], ADDON_VERSION_NUMBER[2]),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > RyModel",
    "description": "Adds a quick access menu with a collection of batched and commonly used modeling operations.",
    "warning": "",
    "doc_url": "",
    "category": "Modeling",
}

# List of classes to be registered.
classes = (
    # Operators
    RyModel_Mirror,
    RyModel_ResetOrigin,
    RyModel_AddModifier,
    RyModel_CopyModifiers,
    RyModel_AutoSharpen,
    RyModel_CleanMesh,
    RyModel_RadialArray,
    RyModel_CurveToRope, 
    RyModel_Cheshire,
    RyModel_HSWFModApply,
    RyModel_AddCutter,
    RyModel_HideCutters, 
    RyModel_ShowCutters, 
    RyModel_RemoveUnusedCutters,
    RyModel_Unwrap,
    RyModel_AutoSeam,

    # User Interface
    RyModel_OT_open_menu,
    RyModel_OT_open_radial_array_menu
)

addon_keymaps = []

boolean_operations = [
    ("INTERSECT", "Intersect", "", 1),
    ("UNION", "Union", "", 2),
    ("DIFFERENCE", "Difference", "", 3),
    ("SLICE", "Slice", "", 4)
]

def update_boolean_operation(self, context):
    '''Updates the boolean operation for all objects using the selected cutter.'''
    if not context.active_object:
        return
    
    if context.active_object.name.startswith("Cutter_") and context.active_object.type == 'MESH':
        for obj in bpy.data.objects:
            for modifier in obj.modifiers:
                if modifier.type == 'BOOLEAN':
                    if modifier.object == context.active_object:

                        if context.scene.rymodel_boolean_mode == 'SLICE':
                            modifier.operation = 'DIFFERENCE'

                            if not context.active_object.modifiers.get("SliceSolidify"):
                                solidify_modifier = context.active_object.modifiers.new("SliceSolidify", 'SOLIDIFY')
                                solidify_modifier.thickness = 0.075
                        else: 
                            modifier.operation = context.scene.rymodel_boolean_mode

                            # For other boolean operations, remove the solidify modifier from the cutter if it exists.
                            solidify_modifier = context.active_object.modifiers.get("SliceSolidify")
                            if solidify_modifier:
                                context.active_object.modifiers.remove(solidify_modifier)


def register():
    # Register properties, operators and pannels.
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    km.keymap_items.new(RyModel_OT_open_menu.bl_idname, 'D', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append(km)

    bpy.types.Scene.rymodel_boolean_mode = bpy.props.EnumProperty(items=boolean_operations, update=update_boolean_operation)

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    # Remove add-on key mapping.
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
