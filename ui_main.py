# This module contains user interface for this add-on.

import bpy
from bpy.types import Menu, Operator

ADDON_VERSION_NUMBER = (0, 1, 0)
UI_Y_SCALE = 1.4


def draw_contextual_object_menu(layout):
    active_object = bpy.context.active_object
    if active_object:
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
            row.prop(mirror_modifier, "use_axis", index=0, text="X", toggle=True)
            row.prop(mirror_modifier, "use_axis", index=1, text="Y", toggle=True)
            row.prop(mirror_modifier, "use_axis", index=2, text="Z", toggle=True)
        
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
    if not bpy.context.active_object:
        return
    
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
    if bpy.context.scene.rymodel_hide_cutters:
        row.prop(bpy.context.scene, "rymodel_hide_cutters", text="", toggle=True, icon='HIDE_OFF')
    else:
        row.prop(bpy.context.scene, "rymodel_hide_cutters", text="", toggle=True, icon='HIDE_ON')

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
    op = row.operator("rymodel.add_cutter", text="C")
    op.shape = 'CONE'

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'INTERSECT')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'UNION')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'DIFFERENCE')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'SLICE')

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
    if not bpy.context.active_object:
        return
    
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
    split = layout.split(factor=0.333)
    first_column = split.column()
    second_column = split.column()
    third_column = split.column()

    row = first_column.row()
    row.scale_y = UI_Y_SCALE
    row.alignment = 'LEFT'
    row.label(text="•••••••••")

    row = second_column.row()
    row.scale_y = UI_Y_SCALE
    row.alignment = 'CENTER'
    row.label(text=name)

    row = third_column.row()
    row.scale_y = UI_Y_SCALE
    row.alignment = 'RIGHT'
    row.label(text="•••••••••")

    op = row.operator("rymodel.delete_modifier", text="", icon='TRASH')
    op.modifier_name = delete_name

def draw_radial_array_properties(layout):
    displace_modifier = bpy.context.active_object.modifiers.get('RadialArrayDisplacement')
    array_modifier =  bpy.context.active_object.modifiers.get('RadialArray')
    if displace_modifier and array_modifier:
        draw_modifier_title(layout, "Radial Array", "Radial Array")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.radial_array_settings, "offset", slider=True)
        row = layout.row(align=True)
        row.prop(bpy.context.scene.radial_array_settings, "count", slider=True)

def draw_modifier_properties(layout):
    '''Draws commonly edited modifier properties based on the selected modifier in the active object.'''
    active_object = bpy.context.active_object
    if active_object:
        for modifier in active_object.modifiers:
            match modifier.name:
                # Draw properties for custom modifiers.
                case "RadialArrayDisplacement":
                    draw_radial_array_properties(layout)

                case "RadialArray":
                    continue
                
                # Draw commonly used properties for modifiers.
                case _:
                    draw_modifier_title(layout, modifier.name, modifier.name)

                    match modifier.type:
                        case 'BEVEL':
                            row = layout.row()
                            row.prop(modifier, "segments", slider=True)
                            row = layout.row()
                            row.prop(modifier, "width", slider=True)
                            row = layout.row()
                            row.prop(modifier, "limit_method", slider=True)

                        case 'WEIGHTED_NORMAL':
                            row = layout.row()
                            row.prop(modifier, "weight", slider=True)

                        case 'SOLIDIFY':
                            row = layout.row()
                            row.prop(modifier, "thickness", slider=True)
                            row = layout.row()
                            row.prop(modifier, "use_even_offset", toggle=True)

                        case 'ARRAY':
                            row = layout.row()
                            row.prop(modifier, "count", slider=True)
                            row = layout.row()
                            row.label(text="Relative Offset")
                            row = layout.row(align=True)
                            row.prop(modifier, "relative_offset_displace", index=0, text="")
                            row.prop(modifier, "relative_offset_displace", index=1, text="")
                            row.prop(modifier, "relative_offset_displace", index=2, text="")

                        case 'MULTIRES':
                            row = layout.row()
                            row.operator("object.multires_subdivide")
                            row.operator("object.multires_higher_levels_delete")

                        case 'SUBSURF':
                            row = layout.row(align=True)
                            row.prop(modifier, "levels")
                            row = layout.row(align=True)
                            row.prop_enum(modifier, "subdivision_type", 'CATMULL_CLARK')
                            row.prop_enum(modifier, "subdivision_type", 'SIMPLE')

                        case 'SHRINKWRAP':
                            row = layout.row(align=True)
                            row.prop(modifier, "target")

                        case 'TRIANGULATE':
                            row = layout.row(align=True)

                        case 'BOOLEAN':
                            row = layout.row(align=True)
                            row.label(text="Solver ")
                            row.prop_enum(modifier, "solver", 'FAST')
                            row.prop_enum(modifier, "solver", 'EXACT')

            row = layout.row()
            row.separator()
            row = layout.row()
            row.separator()

def draw_modifiers(layout):
    split = layout.split(factor=0.75)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.add_modifier", icon='MOD_BEVEL', text=" ")
    op.type = 'BEVEL'
    op = row.operator("rymodel.add_modifier", icon='MOD_NORMALEDIT', text=" ")
    op.type = 'WEIGHTED_NORMAL'
    op = row.operator("rymodel.add_modifier", icon='MOD_SOLIDIFY', text=" ")
    op.type = 'SOLIDIFY'
    op = row.operator("rymodel.add_modifier", icon='MOD_ARRAY', text=" ")
    op.type = 'ARRAY'
    row.operator("rymodel.radial_array", icon='SURFACE_NCIRCLE', text=" ")
    op = row.operator("rymodel.add_modifier", icon='MOD_MULTIRES', text=" ")
    op.type = 'MULTIRES'
    op = row.operator("rymodel.add_modifier", icon='MOD_SUBSURF', text=" ")
    op.type = 'SUBSURF'
    row.operator("rymodel.two_x_subdivision", text="2x")
    op = row.operator("rymodel.add_modifier", icon='MOD_SHRINKWRAP', text=" ")
    op.type = 'SHRINKWRAP'
    op = row.operator("rymodel.add_modifier", icon='MOD_TRIANGULATE', text=" ")
    op.type = 'TRIANGULATE'

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

        # Mesh Tools
        draw_contextual_object_menu(first_column)
        draw_cutter_tools(first_column)
        draw_mirror_tools(first_column)
        draw_origin_tools(first_column)
        draw_display_options(first_column)
        draw_mesh_operators(first_column)

        # Modifiers
        draw_modifiers(second_column)
