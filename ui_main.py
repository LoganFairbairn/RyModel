# This module contains user interface for this add-on.

import bpy
import bpy.utils.previews                   # Imported for custom icons.
from bpy.types import Menu, Operator
import os

ADDON_VERSION_NUMBER = (0, 1, 0)
UI_Y_SCALE = 1.4

custom_icons = None

def load_custom_icons():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    addon_path =  os.path.dirname(__file__)
    icons_dir = os.path.join(addon_path, "icons")
    custom_icons.load('NGON_DRAW', os.path.join(icons_dir, "ngon_draw.png"), 'IMAGE')
    custom_icons.load('CUTTER_INTERSECT', os.path.join(icons_dir, "cutter_intersect.png"), 'IMAGE')
    custom_icons.load('CUTTER_DIFFERENCE', os.path.join(icons_dir, "cutter_difference.png"), 'IMAGE')
    custom_icons.load('CUTTER_SLICE', os.path.join(icons_dir, "cutter_slice.png"), 'IMAGE')
    custom_icons.load('CUTTER_UNION', os.path.join(icons_dir, "cutter_union.png"), 'IMAGE')
    custom_icons.load('2XSUBD', os.path.join(icons_dir, "2xsubd.png"), 'IMAGE')
    custom_icons.load('CIRCULAR_ARRAY', os.path.join(icons_dir, "circular_array.png"), 'IMAGE')
    custom_icons.load('CIRCULAR_TWIST', os.path.join(icons_dir, "circular_twist.png"), 'IMAGE')
    return custom_icons

def remove_custom_icons():
    global custom_icons
    bpy.utils.previews.remove(custom_icons)

def draw_contextual_object_menu(layout):
    active_object = bpy.context.active_object
    match active_object.type:
        case 'MESH':
            if bpy.context.mode == 'EDIT_MESH':
                if bpy.context.scene.tool_settings.mesh_select_mode[1]:
                    row = layout.row()
                    row.scale_y = UI_Y_SCALE
                    row.operator("rymodel.extract_curve", text="Extract Curve")
                    
                if bpy.context.scene.tool_settings.mesh_select_mode[2]:
                    row = layout.row()
                    row.scale_y = UI_Y_SCALE
                    row.operator("rymodel.extract_face", text="Extract Face")

            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.operator("rymodel.auto_sharpen", text="Sharpen")


        case 'CURVE':
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(active_object.data, "bevel_depth", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(active_object.data, "bevel_resolution", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(active_object.data, "extrude", slider=True)
            row = layout.row()
            row.scale_y = UI_Y_SCALE
            row.prop(active_object.data, "resolution_u", slider=True)

def draw_mirror_tools(layout):
    '''Draws mirror options for this add-on to the user interface.'''
    row = layout.row()
    row.label(text="Mirror")

    # Check if a mirror modifier exists on the mesh.
    no_mirror_mod = True
    if bpy.context.active_object:
        mirror_modifier = bpy.context.active_object.modifiers.get('Mirror')
        if mirror_modifier:
            no_mirror_mod = False
            row = layout.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene, "rymodel_mirror_x", text="X", toggle=True)
            row.prop(bpy.context.scene, "rymodel_mirror_y", text="Y", toggle=True)
            row.prop(bpy.context.scene, "rymodel_mirror_z", text="Z", toggle=True)
        
            row = layout.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.prop(bpy.context.scene, "rymodel_mirror_bisect", toggle=True, text="Bisect")
            row.prop(bpy.context.scene, "rymodel_mirror_flip", toggle=True, text="Flip")
            row.prop(bpy.context.scene, "rymodel_mirror_apply", toggle=True, text="Apply")

    if not bpy.context.active_object or no_mirror_mod:
        row = layout.row(align=True)
        row.scale_y = UI_Y_SCALE
        op = row.operator("rymodel.mirror", text="X")
        op.axis = 'X'
        op = row.operator("rymodel.mirror", text="Y")
        op.axis = 'Y'
        op = row.operator("rymodel.mirror", text="Z")
        op.axis = 'Z'

        row = layout.row(align=True)
        row.scale_y = UI_Y_SCALE
        row.prop(bpy.context.scene, "rymodel_mirror_bisect", toggle=True, text="Bisect")
        row.prop(bpy.context.scene, "rymodel_mirror_flip", toggle=True, text="Flip")
        row.prop(bpy.context.scene, "rymodel_mirror_apply", toggle=True, text="Apply")

def draw_cutter_tools(layout):
    if bpy.context.active_object.type != 'MESH':
        return

    row = layout.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Cutters")

    split = layout.split(factor=0.2)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row(align=True)
    row.scale_x = 2
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.show_cutters", icon='HIDE_OFF', text="")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.add_cutter", icon='MESH_CUBE', text="")
    op.shape = 'CUBE'
    op = row.operator("rymodel.add_cutter", icon='MESH_CYLINDER', text="")
    op.shape = 'CYLINDER'
    op = row.operator("rymodel.add_cutter", icon='SPHERE', text="")
    op.shape = 'SPHERE'
    op = row.operator("rymodel.add_cutter", icon='MESH_CONE', text="")
    op.shape = 'CONE'
    op = row.operator("rymodel.add_cutter", icon='SELECT_SET', text="")
    op.shape = 'CONE'
    #op = row.operator("rymodel.add_cutter", icon_value=custom_icons["NGON_DRAW"].icon_id, text="")
    #op.shape = 'CONE'

    row = layout.row(align=True)
    row.scale_x = 10
    row.scale_y = 2
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'INTERSECT', text="")
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'UNION', text="")
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'DIFFERENCE', text="")
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'SLICE', text="")

def draw_origin_tools(layout):
    row = layout.row()
    row.label(text="Origin")

    row = layout.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.reset_origin", text="", icon='WORLD')
    op.location = 'WORLD_ORIGIN'
    op = row.operator("rymodel.reset_origin", text="", icon='SELECT_INTERSECT')
    op.location = 'SELECTED'
    op = row.operator("rymodel.reset_origin", text="", icon='SURFACE_NCYLINDER')
    op.location = 'SURFACE'
    op = row.operator("rymodel.reset_origin", text="", icon='VOLUME_DATA')
    op.location = 'VOLUME'

def draw_mesh_operators(layout):
    '''Draws operations for quickly adjusting elements for the active (selected) mesh.'''
    if bpy.context.active_object.type != 'MESH':
        return

    row = layout.row()
    row.label(text="Mesh Tools")

    row = layout.row(align=True)
    row.scale_y =UI_Y_SCALE
    row.operator("rymodel.clean_mesh")

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.select_ngons")

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.auto_seam")

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.unwrap")

def draw_extras(layout):
    '''Draws extra tool operations to the user interface.'''
    layout.label(text="Extras:")
    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.curve_to_rope")
    row.operator("rymodel.cheshire")

def draw_modifier_title(layout, name, delete_name):
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.alignment = 'LEFT'
    row.label(text=name)

    row = second_column.row()
    row.scale_y = UI_Y_SCALE
    row.alignment = 'RIGHT'
    row.label(text="••••••••••••••••••••••")

    op = row.operator("rymodel.delete_modifier", text="", icon='TRASH')
    op.modifier_name = delete_name

def draw_circular_array_properties(layout):
    displace_modifier = bpy.context.active_object.modifiers.get('CircularArrayDisplacement')
    array_modifier =  bpy.context.active_object.modifiers.get('CircularArray')
    if displace_modifier and array_modifier:
        draw_modifier_title(layout, "Circular Array", "CIRCULAR_ARRAY")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.circular_array_settings, "offset", slider=True)
        row = layout.row(align=True)
        row.prop(bpy.context.scene.circular_array_settings, "count", slider=True)

def draw_circular_twist_array(layout):
    displace_modifier1 = bpy.context.active_object.modifiers.get('CircularTwistDisplacement1')
    array_modifier =  bpy.context.active_object.modifiers.get('CircularTwistArray')

    if array_modifier:
        draw_modifier_title(layout, "Circular Twist", "CIRCULAR_TWIST")

        row = layout.row(align=True)
        row.prop(bpy.context.scene, "circular_twist_count", text="Circular Twist Count", slider=True)

        row = layout.row(align=True)
        row.prop(displace_modifier1, "strength", text="Inner Offset", slider=True)

def draw_modifier_properties(layout):
    '''Draws commonly edited modifier properties based on the selected modifier in the active object.'''
    active_object = bpy.context.active_object
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
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row()
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "segments", slider=True)
                        row = layout.row()
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "width", slider=True)
                        row = layout.row()
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "limit_method", slider=True)

                    case 'WEIGHTED_NORMAL':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row()
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "weight", slider=True)

                    case 'SOLIDIFY':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "thickness", slider=True)
                        row.prop(modifier, "use_even_offset", toggle=True)

                    case 'ARRAY':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row()
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "count", slider=True)
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE
                        row.label(text="Relative Offset")
                        row.prop(modifier, "relative_offset_displace", index=0, text="")
                        row.prop(modifier, "relative_offset_displace", index=1, text="")
                        row.prop(modifier, "relative_offset_displace", index=2, text="")

                    case 'MULTIRES':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row()
                        row.operator("object.multires_subdivide")
                        row.operator("object.multires_higher_levels_delete")

                    case 'SUBSURF':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "levels")
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE
                        row.prop_enum(modifier, "subdivision_type", 'CATMULL_CLARK')
                        row.prop_enum(modifier, "subdivision_type", 'SIMPLE')

                    case 'SHRINKWRAP':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE
                        row.prop(modifier, "target")

                    case 'TRIANGULATE':
                        draw_modifier_title(layout, modifier.name, modifier.name)
                        row = layout.row(align=True)
                        row.scale_y = UI_Y_SCALE

                    case 'BOOLEAN':
                        if bpy.context.scene.show_cutter_ui:
                            draw_modifier_title(layout, modifier.name, modifier.name)
                            row = layout.row(align=True)
                            row.scale_y = UI_Y_SCALE
                            row.label(text="Solver ")
                            row.prop_enum(modifier, "solver", 'FAST')
                            row.prop_enum(modifier, "solver", 'EXACT')

        if bpy.context.scene.show_cutter_ui and modifier.type != 'MIRROR':
            row = layout.row()
            row.separator()
            row = layout.row()
            row.separator()

def draw_modifiers(layout):
    split = layout.split(factor=0.75)
    first_column = split.column()
    second_column = split.column()

    row = layout.row(align=True)
    row.scale_x = 5
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.add_modifier", icon='MOD_BEVEL', text="")
    op.type = 'BEVEL'
    op = row.operator("rymodel.add_modifier", icon='MOD_NORMALEDIT', text="")
    op.type = 'WEIGHTED_NORMAL'
    op = row.operator("rymodel.add_modifier", icon='MOD_SOLIDIFY', text="")
    op.type = 'SOLIDIFY'
    op = row.operator("rymodel.add_modifier", icon='MOD_ARRAY', text="")
    op.type = 'ARRAY'
    row.operator("rymodel.circular_array", text="", icon_value=custom_icons["CIRCULAR_ARRAY"].icon_id)
    row.operator("rymodel.circular_twist", text="", icon_value=custom_icons["CIRCULAR_TWIST"].icon_id)

    row = layout.row(align=True)
    row.scale_x = 5
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.add_modifier", icon='MOD_MULTIRES', text="")
    op.type = 'MULTIRES'
    op = row.operator("rymodel.add_modifier", icon='MOD_SUBSURF', text="")
    op.type = 'SUBSURF'
    row.operator("rymodel.two_x_subdivision", text="", icon_value=custom_icons["2XSUBD"].icon_id)
    op = row.operator("rymodel.add_modifier", icon='MOD_SHRINKWRAP', text="")
    op.type = 'SHRINKWRAP'
    op = row.operator("rymodel.add_modifier", icon='MOD_TRIANGULATE', text="")
    op.type = 'TRIANGULATE'

    split = layout.split(factor=0.75)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Modifiers")

    row = second_column.row(align=True)
    row.scale_x = 4
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.copy_modifiers", icon='COPYDOWN', text="")
    row.operator("rymodel.hswf_mod_apply", icon='MODIFIER', text="+")

    draw_modifier_properties(layout)

def draw_display_options(layout):
    row = layout.row()
    row.label(text="Display")

    row = layout.row()
    row.scale_y = UI_Y_SCALE
    row.prop(bpy.context.space_data.overlay, "show_wireframes", toggle=True)

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
        layout.label(text="RyModel {0}.{1}.{2}".format(str(ADDON_VERSION_NUMBER[0]), str(ADDON_VERSION_NUMBER[1]), str(ADDON_VERSION_NUMBER[2])))

        split = layout.split(factor=0.35)
        first_column = split.column()
        second_column = split.column()

        if context.active_object:
            draw_contextual_object_menu(first_column)
            draw_cutter_tools(first_column)
            draw_mirror_tools(first_column)
            draw_origin_tools(first_column)
            draw_display_options(first_column)
            draw_mesh_operators(first_column)
            draw_modifiers(second_column)

        else:
            layout.label(text="Select an object to edit.")
