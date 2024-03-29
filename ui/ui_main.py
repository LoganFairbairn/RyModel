# This module contains user interface for this add-on.

import bpy
import bpy.utils.previews                   # Imported for custom icons.
from bpy.utils import resource_path
from bpy.types import Operator, Menu
from bpy.props import StringProperty
from ..core import modifiers
from .. import preferences
from pathlib import Path
import os

UI_Y_SCALE = 1.4
MODIFIER_UI_Y_SCALE = 1.2

custom_icons = None


#----------------------------- MODELING TOOL UI -----------------------------#

class MirrorSubMenu(Menu):
    bl_idname = "RYMODEL_MT_mirror_submenu"
    bl_label = "Mirror Submenu"

    def draw(self, context):
        layout = self.layout

        active_object = bpy.context.active_object
        if active_object:
            mirror_modifier = modifiers.get_modifier_of_type(bpy.context.active_object.modifiers, modifier_type='MIRROR')
            if mirror_modifier:
                layout.prop(mirror_modifier, "use_bisect_axis", text="Bisect X", index=0, toggle=True)
                layout.prop(mirror_modifier, "use_bisect_axis", text="Bisect Y", index=1, toggle=True)
                layout.prop(mirror_modifier, "use_bisect_axis", text="Bisect Z", index=2, toggle=True)
                layout.prop(mirror_modifier, "use_bisect_flip_axis", text="Flip Bisect X", index=0, toggle=True)
                layout.prop(mirror_modifier, "use_bisect_flip_axis", text="Flip Bisect Y", index=1, toggle=True)
                layout.prop(mirror_modifier, "use_bisect_flip_axis", text="Flip Bisect Z", index=2, toggle=True)
            else:
                layout.label(text="No mirror modifier applied.")

def load_custom_icons():
    global custom_icons
    custom_icons = bpy.utils.previews.new()

    USER = Path(resource_path('USER'))
    icons_dir =  str(USER / "scripts/addons" / preferences.ADDON_NAME / "icons")
    custom_icons.load('NGON_DRAW', os.path.join(icons_dir, "ngon_draw.png"), 'IMAGE')
    custom_icons.load('CUTTER_INTERSECT', os.path.join(icons_dir, "boolean_intersect.png"), 'IMAGE')
    custom_icons.load('CUTTER_DIFFERENCE', os.path.join(icons_dir, "boolean_difference.png"), 'IMAGE')
    custom_icons.load('CUTTER_SLICE', os.path.join(icons_dir, "boolean_slice.png"), 'IMAGE')
    custom_icons.load('CUTTER_UNION', os.path.join(icons_dir, "boolean_union.png"), 'IMAGE')
    custom_icons.load('2XSUBD', os.path.join(icons_dir, "2xsubd.png"), 'IMAGE')
    custom_icons.load('CIRCULAR_ARRAY', os.path.join(icons_dir, "circular_array.png"), 'IMAGE')
    custom_icons.load('CIRCULAR_TWIST', os.path.join(icons_dir, "circular_twist.png"), 'IMAGE')
    custom_icons.load('INDIVIDUAL_OBJECTS', os.path.join(icons_dir, "individual_objects.png"), 'IMAGE')
    custom_icons.load('BACKUP', os.path.join(icons_dir, "backup.png"), 'IMAGE')
    custom_icons.load('CLEAN', os.path.join(icons_dir, "clean.png"), 'IMAGE')
    custom_icons.load('REAPPLY_SHRINKWRAP', os.path.join(icons_dir, "reapply_shrinkwrap.png"), 'IMAGE')
    return custom_icons

def remove_custom_icons():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)

def draw_mesh_fix_tools(layout):
    '''Draws mesh fix tool operator buttons to the user interface.'''
    split = layout.split(factor=0.2)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row(align=True)
    row.scale_x = 6
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.clean_mesh", text="", icon_value=custom_icons["CLEAN"].icon_id)

    row = second_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.auto_smooth", text="Smooth")
    row.operator("rymodel.auto_sharpen", text="Sharpen")
    row.prop(bpy.context.scene, "auto_sharpen_angle", text="", slider=False)

def draw_contextual_object_menu(layout):
    '''Draws frequently used settings based on context.'''
    active_object = bpy.context.active_object
    match active_object.type:
        case 'MESH':
            draw_mesh_fix_tools(layout)
            draw_boolean_tools(layout)

            boolean_mod = modifiers.get_modifier_of_type(active_object.modifiers, 'BOOLEAN')
            if boolean_mod:
                row = layout.row()
                row.scale_y = UI_Y_SCALE
                row.operator("rymodel.make_booleans_unique", text="Unique Bools")

            if bpy.context.mode == 'EDIT_MESH':
                if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    row = layout.row()
                    row.scale_y = UI_Y_SCALE
                    row.operator("rymodel.extract_curve", text="Extract Curve")
                    
                if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    row = layout.row()
                    row.scale_y = UI_Y_SCALE
                    row.operator("rymodel.extract_face", text="Extract Face")

                    #row = layout.row()
                    #row.scale_y = UI_Y_SCALE
                    #row.operator("rymodel.3d_cursor_to_face", text="3D Cursor To Face")

                    #row = layout.row()
                    #row.scale_y = UI_Y_SCALE
                    #row.operator("rymodel.mirror_by_face", text="Mirror By Face")

        case 'CURVE':

            # Settings
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene.curve_settings, "bevel_depth", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene.curve_settings, "bevel_resolution", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene.curve_settings, "extrude", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene.curve_settings, "resolution_u", slider=True)

            # Curve Array Settings
            row = layout.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.operator("rymodel.delete_curve_array", text="Remove")
            row.operator("rymodel.curve_array_to_mesh", text="To Mesh")

        case 'ARMATURE':
            selected_rig = bpy.context.active_object
            if selected_rig:
                if selected_rig.pose.bones.get('MCH-WGT-chest') and len(selected_rig.pose.bones) > 394:
                    row = layout.row(align=True)
                    row.scale_y = UI_Y_SCALE
                    row.operator("rymodel.prepare_rigify_for_vrchat")

def draw_mirror_tools(layout):
    '''Draws mirror options for this add-on to the user interface.'''
    if bpy.context.active_object:
        split = layout.split(factor=0.25)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        row.label(text="Mirror")

        row = second_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        row.prop(bpy.context.scene, "rymodel_mirror_x", text="X", toggle=True)
        row.prop(bpy.context.scene, "rymodel_mirror_y", text="Y", toggle=True)
        row.prop(bpy.context.scene, "rymodel_mirror_z", text="Z", toggle=True)
        row.menu("RYMODEL_MT_mirror_submenu", text="", icon='DOWNARROW_HLT')

    # Bi-Delete
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.label(text="Bi-Delete")

    row = second_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.delete_vertices_past_axis", text="X")
    op.axis = 'X'
    op = row.operator("rymodel.delete_vertices_past_axis", text="Y")
    op.axis = 'Y'
    op = row.operator("rymodel.delete_vertices_past_axis", text="Z")
    op.axis = 'Z'
    row.prop(bpy.context.scene, "rymodel_flip_bidelete", text="", icon='MOD_MIRROR')

def draw_boolean_tools(layout):
    if bpy.context.active_object.type != 'MESH':
        return
    
    split = layout.split(factor=0.2)
    visibility_column = split.column()
    boolean_column = split.column()

    row = visibility_column.row()
    row.scale_x = 10
    row.scale_y = 2
    row.operator("rymodel.show_boolean_objects", icon='HIDE_OFF', text="")

    row = boolean_column.row(align=True)
    row.scale_x = 10
    row.scale_y = 2
    row.operator("rymodel.add_plane_boolean", text="/")
    row.operator("rymodel.add_cube_boolean", icon='MESH_CUBE', text="")
    row.operator("rymodel.add_cylinder_boolean", icon='MESH_CYLINDER', text="")
    row.operator("rymodel.selected_object_to_boolean", icon='SELECT_SET', text="")
    
    #row.prop_menu_enum(bpy.context.scene, "rymodel_boolean_mode", text='')

def draw_origin_tools(layout):
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Origin")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.set_origin_world_center", text="", icon='WORLD')
    row.operator("rymodel.set_origin_selected", text="", icon='SELECT_INTERSECT')
    row.operator("rymodel.set_origin_center", text="", icon='ANCHOR_CENTER')

def draw_retopology_tools(layout):
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Retopo")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.prepare_manual_retopology", text="Manual Retopo")
    row.operator("rymodel.reapply_shrinkwrap", text="", icon_value=custom_icons["REAPPLY_SHRINKWRAP"].icon_id)
    if bpy.context.scene.retopology_snapping_toggle:
        row.prop(bpy.context.scene, "retopology_snapping_toggle", text="", icon='SNAP_ON')
    else:
        row.prop(bpy.context.scene, "retopology_snapping_toggle", text="", icon='SNAP_OFF')

def draw_lod_options(layout):
    '''Draws level of detail (LOD) operator buttons.'''
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.label(text="Auto LOD")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.auto_generate_lods", text="Auto Generate LOD")

def draw_exporting_options(layout):
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.label(text="Export")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.export", text="", icon='EXPORT')
    row.prop(addon_preferences, "export_selected_objects_individually", text="", icon_value=custom_icons["INDIVIDUAL_OBJECTS"].icon_id)
    row.prop(addon_preferences, "export_template", text="")

def draw_unwrapping_tools(layout):
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Unwrap")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.auto_seam", text="Auto Seam")
    row.operator("rymodel.color_grid", text="Color Grid")

def draw_backup_options(layout):
    '''Draws operators for backing up asset data.'''
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Backup")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.make_backup_object", text="Backup Object", icon_value=custom_icons["BACKUP"].icon_id)

def draw_curve_array_settings(layout):
    '''Draws extra tool operations to the user interface.'''
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Curve")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.array_along_curve", text="Curve Array")
    row.operator("rymodel.deform_array_along_curve", text="Curve Mesh")

def draw_cloth_sim_operators(layout):
    '''Draws cloth simulation operators to the provided layout.'''
    split = layout.split(factor=0.25)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Cloth")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.simulate_cloth", text="", icon='MOD_CLOTH')
    row.operator("rymodel.pin_cloth", text="", icon='PINNED')
    row.operator("rymodel.unpin_cloth", text="", icon='UNPINNED')
    row.operator("rymodel.apply_collision", text="", icon='MOD_PHYSICS')
    #row.menu("OBJECT_MT_cloth_sim_menu", text="", icon='MOD_CLOTH')


#----------------------------- MODIFIER UI -----------------------------#

class ModifierSubMenu(Menu):
    bl_idname = "RYMODEL_MT_modifier_submenu"
    bl_label = "Modifier Submenu"

    def draw(self, context):
        layout = self.layout
        op = layout.operator("rymodel.move_modifier_to_first", text="Move to First")
        op.modifier_name = context.modifier.name
        op = layout.operator("rymodel.move_modifier_to_last", text="Move to Last")
        op.modifier_name = context.modifier.name
        op = layout.operator("rymodel.apply_modifier", text="Apply", icon='ADD')
        op.modifier_name = context.modifier.name
        op = layout.operator("rymodel.move_modifier_up", text="Move Up", icon='TRIA_UP')
        op.modifier_name = context.modifier.name
        op = layout.operator("rymodel.move_modifier_down", text="Move Down", icon='TRIA_DOWN')
        op.modifier_name = context.modifier.name
        op = layout.operator("rymodel.duplicate_modifier", text="Duplicate", icon='DUPLICATE')
        op.modifier_name = context.modifier.name

def draw_modifier_title(layout, name, modifier):
    split = layout.split(factor=0.35)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.alignment = 'LEFT'
    row.label(text="• {0}".format(name))

    row = second_column.row(align=True)
    row.alignment = 'RIGHT'

    if modifier.type == 'BOOLEAN':
        op = row.operator("rymodel.select_boolean", text="", icon='SELECT_SET')
        op.boolean_modifier_name = modifier.name

    op = row.prop(modifier, "show_in_editmode", text="", icon='EDITMODE_HLT')
    op = row.prop(modifier, "show_viewport", text="", icon='RESTRICT_VIEW_ON')
    op = row.prop(modifier, "show_render", text="", icon='RESTRICT_RENDER_ON')

    row.context_pointer_set("modifier", modifier)
    row.menu("RYMODEL_MT_modifier_submenu", text="", icon='DOWNARROW_HLT')

    op = row.operator("rymodel.delete_modifier", text="", icon='X')
    op.modifier_name = modifier.name

def draw_circular_array_properties(layout):
    displace_modifier = bpy.context.active_object.modifiers.get('CircularArrayDisplacement')
    array_modifier =  bpy.context.active_object.modifiers.get('CircularArray')
    if displace_modifier and array_modifier:
        draw_modifier_title(layout, "Circular Array", array_modifier)
        row = layout.row(align=True)
        row.prop(bpy.context.scene.circular_array_settings, "offset", slider=True)
        row = layout.row(align=True)
        row.prop(bpy.context.scene.circular_array_settings, "count", slider=True)

def draw_circular_twist_array(layout):
    displace_modifier1 = bpy.context.active_object.modifiers.get('CircularTwistDisplacement1')
    array_modifier =  bpy.context.active_object.modifiers.get('CircularTwistArray')

    if array_modifier:
        draw_modifier_title(layout, "Circular Twist", array_modifier)

        row = layout.row(align=True)
        row.prop(bpy.context.scene, "circular_twist_count", text="Circular Twist Count", slider=True)

        row = layout.row(align=True)
        row.prop(displace_modifier1, "strength", text="Inner Offset", slider=True)

def draw_modifier_properties(layout):
    '''Draws commonly edited modifier properties based on the selected modifier in the active object.'''
    active_object = bpy.context.active_object
    row = layout.row()
    row.template_modifiers()

    for modifier in active_object.modifiers:
        match modifier.name:
            # Draw properties for custom modifiers.
            case "CircularArrayDisplacement":
                draw_circular_array_properties(layout)

            case "CircularArray":
                continue

            case "CircularTwistArray":
                draw_circular_twist_array(layout)
            
            # Draw commonly used properties for modifiers.
            case _:
                match modifier.type:
                    case 'BEVEL':
                        draw_modifier_title(layout, 'Bevel', modifier)

                        split = layout.split(factor=0.8)
                        first_column = split.column()
                        second_column = split.column()

                        row = first_column.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(bpy.context.scene.bevel_modifier_settings, "segments", text="Edges")
                        row.prop(bpy.context.scene.bevel_modifier_settings, "width", slider=True)

                        row = second_column.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(modifier, "angle_limit", slider=True, text="")

                    case 'WEIGHTED_NORMAL':
                        draw_modifier_title(layout, 'Weighted Normal', modifier)
                        #row = layout.row()
                        #row.prop(modifier, "weight", slider=True)

                    case 'SOLIDIFY':
                        draw_modifier_title(layout, 'Solidify', modifier)
                        row = layout.row(align=True)

                        split = layout.split(factor=0.8)
                        first_column = split.column()
                        second_column = split.column()

                        row = first_column.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(bpy.context.scene.solidify_modifier_settings, "thickness", slider=True)
                        row.prop(modifier, "offset", slider=True)

                        row = second_column.row()
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(modifier, "use_even_offset", toggle=True, text="Even")

                    case 'ARRAY':
                        draw_modifier_title(layout, 'Array', modifier)

                        split = layout.split(factor=0.6)
                        first_column = split.column()
                        second_column = split.column()

                        row = first_column.row()
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(bpy.context.scene.array_modifier_settings, "count", slider=False)

                        row = second_column.row()
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(modifier, "relative_offset_displace", index=0, text="")
                        row.prop(modifier, "relative_offset_displace", index=1, text="")
                        row.prop(modifier, "relative_offset_displace", index=2, text="")

                    case 'MULTIRES':
                        draw_modifier_title(layout, 'Multi-resolution', modifier)
                        row = layout.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.operator("object.multires_subdivide")
                        row.operator("object.multires_higher_levels_delete")

                    case 'SUBSURF':
                        draw_modifier_title(layout, 'Subdivision', modifier)
                        row = layout.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(modifier, "levels")
                        row.prop(modifier, "subdivision_type", text="")

                    case 'SHRINKWRAP':
                        draw_modifier_title(layout, 'Shrinkwrap', modifier)
                        row = layout.row(align=True)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row.prop(modifier, "target")

                    case 'TRIANGULATE':
                        draw_modifier_title(layout, 'Triangulate', modifier)

                    case 'SMOOTH':
                        draw_modifier_title(layout, 'Smooth', modifier)
                        row.scale_y = MODIFIER_UI_Y_SCALE
                        row = layout.row(align=True)
                        row.prop(modifier, "iterations")

                    case 'BOOLEAN':
                        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
                        if not addon_preferences.hide_booleans:
                            draw_modifier_title(layout, 'Boolean', modifier)
                            row = layout.row(align=True)
                            row.scale_y = MODIFIER_UI_Y_SCALE
                        continue

                    case 'MIRROR':
                        draw_modifier_title(layout, 'Mirror', modifier)

def draw_modifiers(layout):
    row = layout.row(align=True)
    row.scale_x = 5
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.add_bevel_modifier", icon='MOD_BEVEL', text="")
    row.operator("rymodel.add_weighted_normal_modifier", icon='MOD_NORMALEDIT', text="")
    row.operator("rymodel.add_solidify_modifier", icon='MOD_SOLIDIFY', text="")
    row.operator("rymodel.add_array_modifier", icon='MOD_ARRAY', text="")
    row.operator("rymodel.circular_array", text="", icon_value=custom_icons["CIRCULAR_ARRAY"].icon_id)
    row.operator("rymodel.circular_twist", text="", icon_value=custom_icons["CIRCULAR_TWIST"].icon_id)

    row = layout.row(align=True)
    row.scale_x = 5
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.add_multires_modifier", icon='MOD_MULTIRES', text="")
    row.operator("rymodel.add_subdivision_modifier", icon='MOD_SUBSURF', text="")
    row.operator("rymodel.two_x_subdivision", text="", icon_value=custom_icons["2XSUBD"].icon_id)
    row.operator("rymodel.add_smooth_modifier", icon='MOD_SMOOTH', text="")
    row.operator("rymodel.add_shrinkwrap_modifier", icon='MOD_SHRINKWRAP', text="")
    row.operator("rymodel.add_triangulate_modifier", icon='MOD_TRIANGULATE', text="")

    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    row = layout.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.prop(addon_preferences, "organize_modifiers", icon='DOCUMENTS', text="")
    row.prop(addon_preferences, "hide_booleans", icon='MOD_BOOLEAN', text="")
    row.operator("rymodel.copy_modifiers", icon='COPYDOWN', text="")
    row.operator("rymodel.hswf_mod_apply", text="Apply All")

    draw_modifier_properties(layout)

class RyModel_OT_open_menu(Operator):
    bl_label = "Open RyModel Menu"
    bl_idname = "rymodel.open_menu"
    bl_description = "Opens the RyModel menu"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=475)

    # Draws the properties in the popup.
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        split = row.split(factor=0.2)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        row.label(text="RyModel 1.0.0")

        split = second_column.split(factor=0.1)
        display_settings_column = split.column()
        tabs_column = split.column()

        row = display_settings_column.row(align=True)
        row.scale_x = UI_Y_SCALE
        row.scale_y = UI_Y_SCALE
        row.prop(bpy.context.space_data.overlay, "show_wireframes", icon='MOD_WIREFRAME', toggle=True, text="")

        row = tabs_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        row.prop_enum(context.scene, "rymodel_ui_tabs", 'MODELLING', text="Modeling")
        row.prop_enum(context.scene, "rymodel_ui_tabs", 'SETTINGS', text="")

        if context.active_object:
            match context.scene.rymodel_ui_tabs:
                case 'MODELLING':
                    split = layout.split(factor=0.5)
                    first_column = split.column()
                    second_column = split.column()

                    # First Column
                    draw_contextual_object_menu(first_column)
                    draw_mirror_tools(first_column)
                    draw_origin_tools(first_column)
                    draw_retopology_tools(first_column)
                    draw_cloth_sim_operators(first_column)
                    draw_curve_array_settings(first_column)
                    draw_unwrapping_tools(first_column)
                    draw_backup_options(first_column)
                    draw_lod_options(first_column)
                    draw_exporting_options(first_column)

                    # Second Column
                    draw_modifiers(second_column)

        else:
            layout.label(text="Select an object to edit.")
