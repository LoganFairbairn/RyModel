# This module contains user interface for this add-on.

import bpy
from bpy.types import Menu, Operator

ADDON_VERSION_NUMBER = (0, 1, 0)
UI_Y_SCALE = 1.4

def draw_mesh_tools(layout):
    '''Draws additional mesh tools'''
    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.auto_sharpen", icon='SHARPCURVE')
    row.operator("rymodel.clean_mesh", icon='MESH_DATA')

def draw_mirror_options(context, layout):
    '''Draws mirror options for this add-on to the user interface.'''

    split = layout.split(factor=0.15)
    first_column = split.column()
    second_column = split.column()

    # Check if a mirror modifier exists on the mesh.
    no_mirror_mod = True
    if context.active_object:
        mirror_modifier = context.active_object.modifiers.get('Mirror')
        if mirror_modifier:
            no_mirror_mod = False
            row = first_column.row(align=True)
            row.label(text="Mirror")
            row.scale_y = UI_Y_SCALE
            row = second_column.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.prop(mirror_modifier, "use_axis", index=0, text="X", toggle=True)
            row.prop(mirror_modifier, "use_axis", index=1, text="Y", toggle=True)
            row.prop(mirror_modifier, "use_axis", index=2, text="Z", toggle=True)
            row = first_column.row(align=True)
            row.label(text="Bisect")
            row.scale_y = UI_Y_SCALE
            row = second_column.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.prop(mirror_modifier, "use_bisect_axis", index=0, text="X", toggle=True)
            row.prop(mirror_modifier, "use_bisect_axis", index=1, text="Y", toggle=True)
            row.prop(mirror_modifier, "use_bisect_axis", index=2, text="Z", toggle=True)
            row = first_column.row(align=True)
            row.label(text="Flip")
            row.scale_y = UI_Y_SCALE
            row = second_column.row(align=True)
            row.scale_y = UI_Y_SCALE
            row.prop(mirror_modifier, "use_bisect_flip_axis", index=0, text="X", toggle=True)
            row.prop(mirror_modifier, "use_bisect_flip_axis", index=1, text="Y", toggle=True)
            row.prop(mirror_modifier, "use_bisect_flip_axis", index=2, text="Z", toggle=True)

    if not context.active_object or no_mirror_mod:
        row = first_column.row(align=True)
        row.label(text="Axis")
        row.scale_y = UI_Y_SCALE
        row = second_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        op = row.operator("rymodel.mirror", text="X")
        op.axis = 'X'
        op = row.operator("rymodel.mirror", text="Y")
        op.axis = 'Y'
        op = row.operator("rymodel.mirror", text="Z")
        op.axis = 'Z'

        row = first_column.row(align=True)
        row.label(text="Bisect")
        row.scale_y = UI_Y_SCALE
        row = second_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        op = row.operator("rymodel.mirror", text="X")
        op.axis = 'BISECT_X'
        op = row.operator("rymodel.mirror", text="Y")
        op.axis = 'BISECT_Y'
        op = row.operator("rymodel.mirror", text="Z")
        op.axis = 'BISECT_Z'

        row = first_column.row(align=True)
        row.label(text="Flip")
        row.scale_y = UI_Y_SCALE
        row = second_column.row(align=True)
        row.scale_y = UI_Y_SCALE
        op = row.operator("rymodel.mirror", text="X")
        op.axis = 'FLIP_X'
        op = row.operator("rymodel.mirror", text="Y")
        op.axis = 'FLIP_Y'
        op = row.operator("rymodel.mirror", text="Z")
        op.axis = 'FLIP_Z'

def draw_origin_options(layout):
    split = layout.split(factor=0.15)
    first_column = split.column()
    second_column = split.column()

    row = first_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.label(text="Origin")

    row = second_column.row(align=True)
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.reset_origin", text="World")
    op.location = 'WORLD_ORIGIN'
    op = row.operator("rymodel.reset_origin", text="Selected")
    op.location = 'SELECTED'
    op = row.operator("rymodel.reset_origin", text="Surface")
    op.location = 'SURFACE'
    op = row.operator("rymodel.reset_origin", text="Volume")
    op.location = 'VOLUME'

def draw_modifiers(layout):
    row = layout.row()
    row.scale_y = UI_Y_SCALE
    row.label(text="Modifiers:")

    row = layout.row(align=True)
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
    op = row.operator("rymodel.add_modifier", icon='MOD_REMESH', text=" ")
    op.type = 'REMESH'
    op = row.operator("rymodel.add_modifier", icon='MOD_SUBSURF', text=" ")
    op.type = 'SUBSURF'
    op = row.operator("rymodel.add_modifier", icon='MOD_SHRINKWRAP', text=" ")
    op.type = 'SHRINKWRAP'
    op = row.operator("rymodel.add_modifier", icon='MOD_TRIANGULATE', text=" ")
    op.type = 'TRIANGULATE'

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.hswf_mod_apply", icon='MODIFIER', text="HSFW Apply")
    row.operator("rymodel.copy_modifiers")
    
def draw_cutters(layout):
    row = layout.row(align=True)
    row.label(text="Cutters: ")

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.hide_cutters", icon='HIDE_ON', text="Hide")
    row.operator("rymodel.show_cutters", icon='HIDE_OFF', text="Show")
    row.operator("rymodel.remove_unused_cutters", icon='TRASH', text="")

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'INTERSECT')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'UNION')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'DIFFERENCE')
    row.prop_enum(bpy.context.scene, "rymodel_boolean_mode", 'SLICE')

    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    op = row.operator("rymodel.add_cutter", icon='MESH_CUBE', text=" ")
    op.shape = 'CUBE'
    op = row.operator("rymodel.add_cutter", icon='MESH_CYLINDER', text=" ")
    op.shape = 'CYLINDER'
    op = row.operator("rymodel.add_cutter", icon='SPHERE', text=" ")
    op.shape = 'SPHERE'
    op = row.operator("rymodel.add_cutter", icon='MESH_CONE', text=" ")
    op.shape = 'CONE'

def draw_unwrapping_options(layout):
    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.label(text="Unwrapping:")
    row.operator("rymodel.auto_seam", icon='UV_EDGESEL')
    row.operator("rymodel.unwrap", icon='UV')

def draw_viewport_display(layout):
    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.label(text="Viewport Displays:")
    row.prop(bpy.context.space_data.overlay, "show_wireframes", toggle=True)
    row.prop(bpy.context.space_data.shading, "show_cavity", toggle=True)

def draw_extras(layout):
    '''Draws extra tool operations to the user interface.'''
    layout.label(text="Extras:")
    row = layout.row(align=True)
    row.scale_y = UI_Y_SCALE
    row.operator("rymodel.curve_to_rope")
    row.operator("rymodel.cheshire")

class RyModel_OT_open_menu(Operator):
    bl_label = "Open RyModel Menu"
    bl_idname = "rymodel.open_menu"
    bl_description = "Opens the RyModel menu"

    # Runs when the add layer button in the popup is clicked.
    def execute(self, context):
        return {'FINISHED'}

    # Opens the popup when the add layer button is clicked.
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)

    # Draws the properties in the popup.
    def draw(self, context):
        
        layout = self.layout
        layout.label(text="RyModel {0}.{1}.{2}".format(str(ADDON_VERSION_NUMBER[0]), str(ADDON_VERSION_NUMBER[1]), str(ADDON_VERSION_NUMBER[2])))

        draw_mesh_tools(layout)
        draw_cutters(layout)
        draw_modifiers(layout)
        draw_mirror_options(context, layout)
        draw_origin_options(layout)
        #draw_extras(layout)
        draw_unwrapping_options(layout)
        draw_viewport_display(layout)
