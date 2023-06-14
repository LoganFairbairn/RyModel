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
from bpy.app.handlers import persistent


# Import operators.
from .quick_operators import *

# Import user interface.
from .ui_main import *

bl_info = {
    "name": "RyModel",
    "author": "Logan Fairbairn (Ryver)",
    "version": (1, 0, 0),
    "blender": (3, 5, 1),
    "location": "View3D > Sidebar > RyModel",
    "description": "Adds a quick access menu with a collection of batched and commonly used modeling operations.",
    "warning": "",
    "doc_url": "",
    "category": "Modeling",
}

# List of classes to be registered.
classes = (
    # Modeling
    RyModel_AutoSharpen,
    RyModel_ExtractFace,
    RyModel_ExtractCurve,
    RyModel_3DCursorToFace,
    RyModel_CleanMesh,
    RyModel_SelectNgons,
    RyModel_DrawShape,

    # Origin Adjustments / Centering
    RyModel_ResetOrigin,
    RyModel_CenterAxis,

    # Mirroring
    RyModel_DeleteVerticesPastAxis,
    RyModel_MirrorByFace,

    # Modifiers
    RyModel_AddBevelModifier,
    RyModel_AddWeightedNormalModifier,
    RyModel_AddSolidifyModifier,
    RyModel_AddArrayModifier,
    RyModel_AddMultiResModifier,
    RyModel_AddSubdivisionModifier,
    RyModel_AddShrinkWrapModifier,
    RyModel_AddTriangulateModifier,
    RyModel_ApplyModifier,
    RyModel_DeleteModifier,
    RyModel_CopyModifiers,
    CircularArraySettings,
    RyModel_CircularArray,
    RyModel_CircularTwist,
    RyModel_2xSubDivision,
    RyModel_CurveToRope, 
    RyModel_Cheshire,
    RyModel_HSWFModApply,

    # Cutters
    RyModel_AddCutter,
    RyModel_SelectCutter,
    RyModel_ShowCutters,

    # Unwrapping
    RyModel_Unwrap,
    RyModel_AutoSeam,

    # Property Range Overrides
    BevelModifierSettings,
    SolidifyModifierSettings,
    ArrayModifierSettings,
    CurveSettings,

    # User Interface
    RyModel_OT_open_menu
)

def on_active_object_changed():
    '''Performs updates when the active object is changed.'''
    active_object = bpy.context.active_object
    if active_object:
        # Update cutter visibility.
        if active_object.type == 'MESH':
            hide_cutters()

        update_property_range_overrides()

    update_mirror_properties()

# Mark load handlers as persistent so they are not freed when loading a new blend file.
@persistent
def load_handler(dummy):
    # Subscribe to the active object.
    subscribe_to = bpy.types.LayerObjects, "active"
    bpy.types.Scene.matlayer_object_selection_updater = object()
    bpy.msgbus.subscribe_rna(key=subscribe_to, owner=bpy.types.Scene.matlayer_object_selection_updater, args=(), notify=on_active_object_changed)

# Run startup functions when a new blend file is loaded.
bpy.app.handlers.load_post.append(load_handler)

addon_keymaps = []

def register():
    # Import custom icons.
    custom_icons = load_custom_icons()

    # Register classes.
    for cls in classes:
        bpy.utils.register_class(cls)

    # Assign keymapping for opening the add-on menu.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(RyModel_OT_open_menu.bl_idname, type='D', value='PRESS', ctrl=False)
        addon_keymaps.append((km, kmi))

        #km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        #kmi = km.keymap_items.new(RyModel_DrawShape.bl_idname, type='D', value='PRESS', ctrl=True)
        #addon_keymaps.append((km, kmi))


    CUTTER_MODE = [
        ("INTERSECT", "Intersect", "Cutters will cut everything from the object excluding geometry that intersects with the cutter", custom_icons["CUTTER_INTERSECT"].icon_id, 1),
        ("UNION", "Union", "Cutters will merge with the original objects geometry", custom_icons["CUTTER_UNION"].icon_id, 2),
        ("DIFFERENCE", "Difference", "Cutters will remove geometry that intersects with the cutter", custom_icons["CUTTER_DIFFERENCE"].icon_id, 3),
        ("SLICE", "Slice", "Cutters will slice where the cutter and original geometry intersect", custom_icons["CUTTER_SLICE"].icon_id, 4)
    ]
    bpy.types.Scene.rymodel_boolean_mode = bpy.props.EnumProperty(items=CUTTER_MODE, name="Cutter Mode", default='DIFFERENCE', update=update_boolean_operation)

    # Mirror settings.
    bpy.types.Scene.rymodel_update_mirroring = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.rymodel_mirror_x = bpy.props.BoolProperty(default=True, description="Mirrors the object on the X axis", update=update_mirror_x)
    bpy.types.Scene.rymodel_mirror_y = bpy.props.BoolProperty(default=True, description="Mirrors the object on the Y axis", update=update_mirror_y)
    bpy.types.Scene.rymodel_mirror_z = bpy.props.BoolProperty(default=True, description="Mirrors the object on the Z axis", update=update_mirror_z)

    # Custom Modifier Settings
    bpy.types.Scene.circular_array_settings = bpy.props.PointerProperty(type=CircularArraySettings)
    bpy.types.Scene.circular_twist_count = bpy.props.IntProperty(default=10, min=0, soft_max=30, update=update_circular_twist_count)

    # Property Range Overrides
    bpy.types.Scene.bevel_modifier_settings = bpy.props.PointerProperty(type=BevelModifierSettings)
    bpy.types.Scene.solidify_modifier_settings = bpy.props.PointerProperty(type=SolidifyModifierSettings)
    bpy.types.Scene.array_modifier_settings = bpy.props.PointerProperty(type=ArrayModifierSettings)
    bpy.types.Scene.curve_settings = bpy.props.PointerProperty(type=CurveSettings)

    # UI Toggles
    bpy.types.Scene.show_cutter_ui = bpy.props.BoolProperty(default=False)

def unregister():
    # Remove custom icons.
    remove_custom_icons()

    # Remove add-on key mapping.
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
