# This module provides operators to help speed up the modeling workflow in Blender.

import bpy
import blf
import gpu
import mathutils
from gpu_extras.batch import batch_for_shader
import bmesh
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty
from . import rylog
import math

#------------------------ HELPERS ------------------------#

def verify_active_mesh(self=None):
    '''Verifies the active (selected) object exists an is a mesh.'''
    if not bpy.context.active_object:
        error_message = "Select a mesh object to perform this operation."
        if self:
            rylog.log_status(error_message, self, 'ERROR')
        else:
            rylog.log(error_message)
        return False
    if bpy.context.active_object.type != 'MESH':
        error_message = "Active object must be a mesh to perform this operation."
        if self:
            rylog.log_status(error_message, self, 'ERROR')
        else:
            rylog.log(error_message)
        return False
    return True

#------------------------ MODELING TOOLS ------------------------#

def update_mirror_x(self, context):
    mirror_modifier = get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
    mirror_modifier.use_axis[0] = context.scene.rymodel_mirror_x

    if context.scene.rymodel_mirror_flip:
        mirror_modifier.use_bisect_flip_axis[0] = context.scene.rymodel_mirror_x

    if context.scene.rymodel_mirror_bisect:
        mirror_modifier.use_bisect_axis[0] = context.scene.rymodel_mirror_x

def update_mirror_y(self, context):
    mirror_modifier = get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
    mirror_modifier.use_axis[1] = context.scene.rymodel_mirror_y

    if context.scene.rymodel_mirror_flip:
        mirror_modifier.use_bisect_flip_axis[1] = context.scene.rymodel_mirror_y

    if context.scene.rymodel_mirror_bisect:
        mirror_modifier.use_bisect_axis[1] = context.scene.rymodel_mirror_y

def update_mirror_z(self, context):
    mirror_modifier = get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
    mirror_modifier.use_axis[2] = context.scene.rymodel_mirror_z

    if context.scene.rymodel_mirror_flip:
        mirror_modifier.use_bisect_flip_axis[2] = context.scene.rymodel_mirror_z

    if context.scene.rymodel_mirror_bisect:
        mirror_modifier.use_bisect_axis[2] = context.scene.rymodel_mirror_z

def update_mirror_flip(self, context):
    mirror_modifier = get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
    if mirror_modifier:
        if mirror_modifier.use_axis[0] == True:
            if context.scene.rymodel_mirror_flip:
                mirror_modifier.use_bisect_flip_axis[0] = True
            else:
                mirror_modifier.use_bisect_flip_axis[0] = False

        if mirror_modifier.use_axis[1] == True:
            if context.scene.rymodel_mirror_flip:
                mirror_modifier.use_bisect_flip_axis[1] = True
            else:
                mirror_modifier.use_bisect_flip_axis[1] = False

        if mirror_modifier.use_axis[2] == True:
            if context.scene.rymodel_mirror_flip:
                mirror_modifier.use_bisect_flip_axis[2] = True
            else:
                mirror_modifier.use_bisect_flip_axis[2] = False

def update_mirror_bisect(self, context):
    mirror_modifier = get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
    if mirror_modifier:
        if mirror_modifier.use_axis[0] == True:
            if context.scene.rymodel_mirror_bisect:
                mirror_modifier.use_bisect_axis[0] = True
            else:
                mirror_modifier.use_bisect_axis[0] = False

        if mirror_modifier.use_axis[1] == True:
            if context.scene.rymodel_mirror_bisect:
                mirror_modifier.use_bisect_axis[1] = True
            else:
                mirror_modifier.use_bisect_axis[1] = False

        if mirror_modifier.use_axis[2] == True:
            if context.scene.rymodel_mirror_bisect:
                mirror_modifier.use_bisect_axis[2] = True
            else:
                mirror_modifier.use_bisect_axis[2] = False

class RyModel_Mirror(Operator):
    bl_idname = "rymodel.mirror"
    bl_label = "Mirror"
    bl_description = "Applies a mirror modifier to the select object based on the provided axis. Only 1 mirror modifier will be applied per object. If Symmetry is ticked, the modifier will be automatically applied."
    bl_options = {'REGISTER', 'UNDO'}

    axis: StringProperty(default='X')

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        bpy.ops.object.modifier_add(type='MIRROR')
        mirror_modifier = context.active_object.modifiers.get('Mirror')
        if not mirror_modifier:
            mirror_modifier = context.active_object.modifiers.new("Mirror", 'MIRROR')
            mirror_modifier.use_clip = True
            mirror_modifier.show_on_cage = True

        match self.axis:
            case 'X':
                mirror_modifier.use_axis[0] = True

                if context.scene.rymodel_mirror_bisect:
                    mirror_modifier.use_bisect_axis[0] = True

                if context.scene.rymodel_mirror_flip:
                    mirror_modifier.use_bisect_flip_axis[0] = True
                
            case 'Y':
                mirror_modifier.use_axis[1] = True
                mirror_modifier.use_axis[0] = False

                if context.scene.rymodel_mirror_bisect:
                    mirror_modifier.use_bisect_axis[1] = True

                if context.scene.rymodel_mirror_flip:
                    mirror_modifier.use_bisect_flip_axis[1] = True
                
            case 'Z':
                mirror_modifier.use_axis[2] = True
                mirror_modifier.use_axis[0] = False

                if context.scene.rymodel_mirror_bisect:
                    mirror_modifier.use_bisect_axis[2] = True
                
                if context.scene.rymodel_mirror_flip:
                    mirror_modifier.use_bisect_flip_axis[2] = True

        # Instantly apply the modifier.
        if context.scene.rymodel_mirror_apply:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.modifier_apply(modifier="Mirror")

        organize_modifier_stack(context.active_object.modifiers)

        return {'FINISHED'}

class RyModel_ResetOrigin(Operator):
    bl_idname = "rymodel.reset_origin"
    bl_label = "Reset Origin"
    bl_description = "Resets the objects origin to the specified location"
    bl_options = {'REGISTER', 'UNDO'}

    location: StringProperty(default='Y_AXIS')

    def execute(self, context):
        original_mode = bpy.context.mode

        match self.location:
            case 'WORLD_ORIGIN':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            case 'SELECTED':
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            case 'SURFACE':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
            case 'VOLUME':
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')

        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        else:
            bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}

class RyModel_AutoSharpen(Operator):
    bl_idname = "rymodel.auto_sharpen"
    bl_label = "Auto Sharpen"
    bl_description = "Applies auto smooth, then bevel weights and sharpen by angles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode

        # Clear all bevel weights.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if bpy.context.active_object.data.has_bevel_weight_edge:
            bpy.ops.mesh.customdata_bevel_weight_edge_clear()

        # Apply autosmooth.
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 1.0472

        # Clear all bevel weights and sharpening.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.mark_sharp(clear=True)

        # Mark bevel weights and sharpening for sharp angles.
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
        bpy.ops.mesh.mark_sharp()
        bpy.ops.transform.edge_bevelweight(value=1.0, snap=False)

        bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}

class RyModel_ExtractFace(Operator):
    bl_idname = "rymodel.extract_face"
    bl_label = "Extract Face"
    bl_description = "Separates the selected faces from the object into a new object, and applied a solidify modifier to the new object for thickess"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        if bpy.context.mode != 'EDIT_MESH':
            return
        
        if not bpy.context.scene.tool_settings.mesh_select_mode[2]:
            return
        
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

        bpy.ops.mesh.separate(type='SELECTED')

        new_object = context.selected_objects[1]
        if context.selected_objects[1] == context.active_object:
            new_object = context.selected_objects[0]

        solidify_modifier = new_object.modifiers.new('Solidify', 'SOLIDIFY')
        solidify_modifier.thickness = 0.1
        solidify_modifier.offset = 1.0
        solidify_modifier.use_even_offset = True

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}

class RyModel_ExtractCurve(Operator):
    bl_idname = "rymodel.extract_curve"
    bl_label = "Extract Curve"
    bl_description = "Separates the selected edges from the object into a new curve, and applies a default amount of bevel width to the new curve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        if bpy.context.mode != 'EDIT_MESH':
            return
        
        if not bpy.context.scene.tool_settings.mesh_select_mode[1]:
            return

        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

        bpy.ops.mesh.separate(type='SELECTED')

        new_object = context.selected_objects[1]
        if context.selected_objects[1] == context.active_object:
            new_object = context.selected_objects[0]

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.context.view_layer.objects.active = new_object

        bpy.ops.object.convert(target='CURVE')
        new_object.data.bevel_depth = 0.1

        return {'FINISHED'}

class RyModel_SelectNgons(Operator):
    bl_idname = "rymodel.select_ngons"
    bl_label = "Select NGons"
    bl_description = "Selects all NGons in the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        bpy.ops.mesh.select_all(action='INVERT')

        return {'FINISHED'}

class RyModel_CleanMesh(Operator):
    bl_idname = "rymodel.clean_mesh"
    bl_label = "Clean Mesh"
    bl_description = "Removes doubles and non-manifold geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}

        # Toggle into edit mode, remember the original mode.
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Remove loose faces.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='FACE')

        # Remove loose edges.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='EDGE')

        # Remove loose vertices.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='VERT')

        # Remove vertex doubles.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        # Toggle back into the original mode.
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        return {'FINISHED'}

def draw_callback_px(self, context):
    # Draw number of point created.
    font_id = 0
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, "Points: {0}".format(len(self.verticies)))


    render_vertices = []

    if len(self.verticies) == 1:
        render_vertices.append(self.verticies[0])
        render_vertices.append((self.mouse_pos[0], self.mouse_pos[1]))
        render_vertices.append((self.mouse_pos[0], self.mouse_pos[1]))

    elif len(self.verticies) == 2:
        render_vertices.append(self.verticies[0])
        render_vertices.append(self.verticies[1])
        render_vertices.append((self.mouse_pos[0], self.mouse_pos[1]))

    else:
        last_tri = []
        last_tri.append((self.verticies[len(self.verticies) - 2]))
        last_tri.append((self.verticies[len(self.verticies) - 1]))
        last_tri.append((self.mouse_pos[0], self.mouse_pos[1]))

        render_vertices = self.verticies + last_tri


    # Draw the shape to the screen.
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    batch = batch_for_shader(shader, 'TRIS', {"pos": render_vertices})
    shader.uniform_float("color", (1.0, 0.0, 0.0, 0.5))
    batch.draw(shader)

    # restore opengl defaults
    gpu.state.blend_set('NONE')

class RyModel_DrawShape(bpy.types.Operator):
    bl_idname = "rymodel.draw_shape"
    bl_label = "Draw Shape"
    bl_description = "Click to create vertices of a shape, which is automatically extruded and filled. If an object is selected, the new shape will be applied as a cutter object"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.mouse_pos = []
            self.mouse_pos.append(event.mouse_region_x)
            self.mouse_pos.append(event.mouse_region_y)

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.verticies.append((event.mouse_region_x, event.mouse_region_y))

                # Append the last triangle.
                if len(self.verticies) > 3:
                    last_tri = []
                    last_tri.append((self.verticies[len(self.verticies) - 3]))
                    last_tri.append((self.verticies[len(self.verticies) - 2]))
                    last_tri.append((self.mouse_pos[0], self.mouse_pos[1]))

                    self.verticies += last_tri

                print("-------------------------------------------")
                print("Mouse clicks: {0}".format(str(self.verticies)))
                print("Added mouse point: {0},{1}".format(self.mouse_pos[0], self.mouse_pos[1]))

        elif event.type == 'SPACE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            self.verticies = []
            self.mouse_pos = [0, 0]

            # Add the start position.
            self.verticies.append((event.mouse_region_x, event.mouse_region_y))
            print("Added mouse start position.")

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class RyModel_MirrorByFace(Operator):
    bl_idname = "rymodel.mirror_by_face"
    bl_label = "Mirror By Face"
    bl_description = "Mirrors the object based on the select"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        if original_mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Must be in edit mode to run the 3D cursor to face operator.")
            return {'FINISHED'}

        original_object = bpy.context.active_object
        original_origin = original_object.location.copy()

        # Must be in face select mode.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        
        # Snap the cursor to the selected face.
        bpy.ops.view3d.snap_cursor_to_selected()
        
        # Set the origin of the object to the face.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        # Duplicate the object and flip it.
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

        # Flip by face angle.
        polgyons = original_object.data.polygons
        normal = original_object.data.polygons[polgyons.active].normal
        up = normal.to_track_quat('X', 'Y')
        polygon_rotation = up.to_euler()

        if polygon_rotation[1] == 0:
            bpy.ops.transform.resize(value=(-1, -1, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

        else:
            bpy.ops.transform.resize(value=(-1, -1, -1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

        # Reset the origin of the original object.
        bpy.context.scene.cursor.location = original_origin
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = original_object
        original_object.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        # Reset to the original mode.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        align_cursor_to_face()

        return {'FINISHED'}

def align_cursor_to_face():
    if not verify_active_mesh():
        return

    cursor = bpy.context.scene.cursor
    obj = bpy.context.active_object
    polgyons = obj.data.polygons

    # Set the 3D cursor to the center of the active face.
    center = obj.data.polygons[polgyons.active].center
    cursor.location = center

    # Set the 3D cursor rotation to the rotation of the selected face.
    normal = obj.data.polygons[polgyons.active].normal
    up = normal.to_track_quat('X', 'Y')

    bpy.ops.object.mode_set(mode='OBJECT')
    cursor.rotation_euler = up.to_euler(cursor.rotation_mode)

class RyModel_3DCursorToFace(Operator):
    bl_idname = "rymodel.3d_cursor_to_face"
    bl_label = "3D Cursor To Face"
    bl_description = "Sets the 3D cursor to the selected face and rotates it to match the face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_cursor_to_face()
        return {'FINISHED'}

#------------------------ MODIFIERS ------------------------#

def get_modifier_of_type(modifiers, modifier_type):
    '''Returns the modififier of the given type if it exists in the modifiers provided.'''
    for modifier in modifiers:
        if modifier.type == modifier_type:
            return modifier
    return None

def get_modifiers_of_type(modifiers, modifier_type):
    '''Returns all modifiers applied to the active (selected) object'''
    modifiers_of_given_type = []
    for modifier in modifiers:
        if modifier.type == modifier_type:
            modifiers_of_given_type.append(modifier)
    return modifiers_of_given_type

def organize_modifier_stack(object_modifiers):
    '''Organizes the modifier stack order.'''

    bevel_modifier = get_modifier_of_type(object_modifiers, 'BEVEL')
    weighted_normal_modifier = get_modifier_of_type(object_modifiers, 'WEIGHTED_NORMAL')
    mirror_modifier = get_modifier_of_type(object_modifiers, 'MIRROR')
    array_modifiers = get_modifiers_of_type(object_modifiers, 'ARRAY')
    solidify_modifier = get_modifier_of_type(object_modifiers, 'SOLIDIFY')
    boolean_modifiers = get_modifiers_of_type(object_modifiers, 'BOOLEAN')
    multires_modifier = get_modifier_of_type(object_modifiers, 'MULTIRES')
    subdivision_modifiers = get_modifiers_of_type(object_modifiers, 'SUBSURF')
    shrinkwrap_modifier = get_modifier_of_type(object_modifiers, 'SHRINKWRAP')
    triangulate_modifier = get_modifier_of_type(object_modifiers, 'TRIANGULATE')

    modifier_index = 0

    if shrinkwrap_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=shrinkwrap_modifier.name, index=modifier_index)
        modifier_index += 1

    if solidify_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=solidify_modifier.name, index=modifier_index)
        modifier_index += 1

    if multires_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=multires_modifier.name, index=modifier_index)
        modifier_index += 1

    for subdivision_modifier in subdivision_modifiers:
        bpy.ops.object.modifier_move_to_index(modifier=subdivision_modifier.name, index=modifier_index)
        modifier_index += 1

    for array_modifier in array_modifiers:
        bpy.ops.object.modifier_move_to_index(modifier=array_modifier.name, index=modifier_index)
        modifier_index += 1

    for boolean_modifier in boolean_modifiers:
        bpy.ops.object.modifier_move_to_index(modifier=boolean_modifier.name, index=modifier_index)
        modifier_index += 1

    if mirror_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=mirror_modifier.name, index=modifier_index)
        modifier_index += 1

    if bevel_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=bevel_modifier.name, index=modifier_index)
        modifier_index += 1

    if weighted_normal_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=weighted_normal_modifier.name, index=modifier_index)
        modifier_index += 1

    if triangulate_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=triangulate_modifier.name, index=modifier_index)
        modifier_index += 1

def add_modifier(modifier_type, self, context):
    if not verify_active_mesh(self):
        return {'FINISHED'}
    
    if not context.active_object.modifiers.get(str(modifier_type)):
        new_modifier = context.active_object.modifiers.new(str(modifier_type), modifier_type)
        new_modifier.show_expanded = False

    organize_modifier_stack(context.active_object.modifiers)
    return new_modifier

class RyModel_AddBevelModifier(Operator):
    bl_idname = "rymodel.add_bevel_modifier"
    bl_label = "Add Bevel Modifier"
    bl_description = "Adds a bevel modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bevel_modifier = add_modifier('BEVEL', self, context)
        bevel_modifier.segments = 6
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddWeightedNormalModifier(Operator):
    bl_idname = "rymodel.add_weighted_normal_modifier"
    bl_label = "Add Weighted Normal Modifier"
    bl_description = "Adds a weighted normal modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        add_modifier('WEIGHTED_NORMAL', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddSolidifyModifier(Operator):
    bl_idname = "rymodel.add_solidify_modifier"
    bl_label = "Add Solidify Modifier"
    bl_description = "Adds a solidify modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SOLIDIFY', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddArrayModifier(Operator):
    bl_idname = "rymodel.add_array_modifier"
    bl_label = "Add Array Modifier"
    bl_description = "Adds an array modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('ARRAY', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddMultiResModifier(Operator):
    bl_idname = "rymodel.add_multires_modifier"
    bl_label = "Add MultiRes Modifier"
    bl_description = "Adds a multi resolution modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('MULTIRES', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddSubdivisionModifier(Operator):
    bl_idname = "rymodel.add_subdivision_modifier"
    bl_label = "Add Subdivision Modifier"
    bl_description = "Adds a subdivision modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SUBSURF', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddShrinkWrapModifier(Operator):
    bl_idname = "rymodel.add_shrinkwrap_modifier"
    bl_label = "Add Shrinkwrap Modifier"
    bl_description = "Adds a shrinkwrap modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SHRINKWRAP', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddTriangulateModifier(Operator):
    bl_idname = "rymodel.add_triangulate_modifier"
    bl_label = "Add Triangulate Modifier"
    bl_description = "Adds a triangulate modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('TRIANGULATE', self, context)
        update_property_range_overrides()
        return {'FINISHED'}

class RyModel_ApplyModifier(Operator):
    bl_idname = "rymodel.apply_modifier"
    bl_label = "Apply Modifier"
    bl_description = "Applies the modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: StringProperty(default="")

    def execute(self, context):
        bpy.ops.object.modifier_apply(modifier=self.modifier_name, report=True)
        if self.modifier_name.startswith("Cutter_"):
            remove_unused_cutters()
        return {'FINISHED'}

#------------------------ CUSTOM MODIFIERS ------------------------#

def remove_circular_array_setup(context):
    circular_array_displacement_modifier = bpy.context.active_object.modifiers.get("CircularArrayDisplacement")
    if circular_array_displacement_modifier:
        bpy.context.active_object.modifiers.remove(circular_array_displacement_modifier)
        
    circular_array_modifier = bpy.context.active_object.modifiers.get("CircularArray")
    offset_object = circular_array_modifier.offset_object
    if offset_object:
        bpy.data.objects.remove(circular_array_modifier.offset_object)
    if circular_array_modifier:
        bpy.context.active_object.modifiers.remove(circular_array_modifier)

def remove_circular_twist_setup(context):
    displace_modifier1 = context.active_object.modifiers.get('CircularTwistDisplacement1')
    array_modifier =  context.active_object.modifiers.get('CircularTwistArray')
    simple_deform_modifier = context.active_object.modifiers.get('CircularTwistDeform')
    displace_modifier2 = context.active_object.modifiers.get('CircularTwistDisplacement2')
    weld_modifier = context.active_object.modifiers.get('CircularTwistWeld')

    if displace_modifier1:
        context.active_object.modifiers.remove(displace_modifier1)

    if array_modifier:
        context.active_object.modifiers.remove(array_modifier)

    if simple_deform_modifier:
        context.active_object.modifiers.remove(simple_deform_modifier)

    if displace_modifier2:
        context.active_object.modifiers.remove(displace_modifier2)

    if weld_modifier:
        context.active_object.modifiers.remove(weld_modifier)

class RyModel_DeleteModifier(Operator):
    bl_idname = "rymodel.delete_modifier"
    bl_label = "Delete Modifier"
    bl_description = "Deletes the modifier from the active (selected) object, then re-organizes the modifier stack"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: StringProperty(default="")

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        match self.modifier_name:
            case 'CIRCULAR_ARRAY':
                remove_circular_array_setup(context)

            case 'CIRCULAR_TWIST':
                remove_circular_twist_setup(context)

            case _:
                modifier = bpy.context.active_object.modifiers.get(self.modifier_name)
                if modifier:
                    bpy.context.active_object.modifiers.remove(modifier)

        remove_unused_cutters()

        return {'FINISHED'}

class RyModel_CopyModifiers(Operator):
    bl_idname = "rymodel.copy_modifiers"
    bl_label = "Copy Modifiers"
    bl_description = "Copies all modifiers from the selected object to the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        for modifier in context.active_object.modifiers:
            bpy.ops.object.modifier_copy_to_selected(modifier=modifier.name)

        return {'FINISHED'}

class RyModel_HSWFModApply(Operator):
    bl_idname = "rymodel.hswf_mod_apply"
    bl_label = "HSWF Mod Apply"
    bl_description = "Applies all modifiers to the object, excluding bevel and weighted normal modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}

        for modifier in context.active_object.modifiers:
            if modifier.type != 'BEVEL' and modifier.type != 'WEIGHTED_NORMAL':
                bpy.ops.object.modifier_apply(modifier=modifier.name)

        return {'FINISHED'}

def update_circular_offset(self, context):
    if not verify_active_mesh():
        return

    displace_modifier = context.active_object.modifiers.get('CircularArrayDisplacement')
    if displace_modifier:
        displace_modifier.strength = context.scene.circular_array_settings.offset

def update_circular_count(self, context):
    if not verify_active_mesh():
        return
    
    array_modifier = context.active_object.modifiers.get('CircularArray')
    array_modifier.count = context.scene.circular_array_settings.count
    empty_object = array_modifier.offset_object
    empty_object.rotation_euler[2] = math.radians(360 / array_modifier.count)

class CircularArraySettings(PropertyGroup):
    offset: FloatProperty(name="Offset", default=2.0, min=0.0, soft_max=5.0, update=update_circular_offset)
    count: IntProperty(name="Count", default=10, min=0, soft_max=100, update=update_circular_count)

class RyModel_CircularArray(Operator):
    bl_idname = "rymodel.circular_array"
    bl_label = "Circular Array"
    bl_description = "Applies a circular array to the active (selected) object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_object = context.active_object
        displace_modifier = context.active_object.modifiers.get('CircularArrayDisplacement')
        array_modifier =  context.active_object.modifiers.get('CircularArray')

        # If either modifier exists, assume there is already a circular array applied to the active object.
        if displace_modifier or array_modifier:
            rylog.log_status("Circular array modifiers already exist on the active object, delete the existing circular array if you want a new one.", self)
            return {'FINISHED'}

        # Add a displacement modifier.
        if not displace_modifier:
            displace_modifier = context.active_object.modifiers.new('CircularArrayDisplacement', 'DISPLACE')
        displace_modifier.strength = 1.0
        displace_modifier.mid_level = 0.0
        displace_modifier.direction = 'X'
        displace_modifier.show_expanded = False

        # Add an array modifer.
        if not array_modifier:
            array_modifier = context.active_object.modifiers.new('CircularArray', 'ARRAY')
        array_modifier.use_relative_offset = False
        array_modifier.use_object_offset = True
        array_modifier.count = 10
        array_modifier.show_expanded = False

        # Add an empty to the array.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        empty_object = context.active_object
        array_modifier.offset_object = empty_object
        empty_object.rotation_euler[2] = math.radians(360 / array_modifier.count)

        # Parent the empty to the array so the objects will move together.
        empty_object.parent = original_object

        # Select the original object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = original_object


        return {'FINISHED'}

class RyModel_2xSubDivision(Operator):
    bl_idname = "rymodel.two_x_subdivision"
    bl_label = "2x Subdivision"
    bl_description = "Adds a 2x subdivision setup. Useful for a subdivision workflow where you don't want to add supporting loops for subdivided edges"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(default='BEVEL')

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        if not context.active_object.modifiers.get('2xSubDivision_1') and not context.active_object.modifiers.get('2xSubDivision_2'):
            subdivision_modifier_1 = context.active_object.modifiers.new('2xSubDivision_1', 'SUBSURF')
            subdivision_modifier_1.levels = 2
            subdivision_modifier_1.subdivision_type = 'SIMPLE'
            subdivision_modifier_2 = context.active_object.modifiers.new('2xSubDivision_2', 'SUBSURF')
            subdivision_modifier_2.levels = 2

        return {'FINISHED'}

def update_circular_twist_count(self, context):
    '''Updates the circular array modifier twist count.'''
    active_object = context.active_object

    array_modifier =  active_object.modifiers.get('CircularTwistArray')
    displace_modifier2 = active_object.modifiers.get('CircularTwistDisplacement2')

    # Update the array modifier count.
    array_modifier.count = context.scene.circular_twist_count


    # Duplicate the object and apply all mods then re-center the origin to get the Y location offset to re-center the object.
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = active_object
    active_object.select_set(True)
    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    temp_obj = bpy.context.active_object

    # Remove the 2nd twist displacement.
    twist_displacement_2 = temp_obj.modifiers.get("CircularTwistDisplacement2")
    if twist_displacement_2:
        temp_obj.modifiers.remove(twist_displacement_2)

    for modifier in temp_obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier.name, report=False)

    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
    y_offset = temp_obj.location[1]
    bpy.ops.object.delete(use_global=False)

    displace_modifier2.strength = y_offset * -1

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = active_object
    active_object.select_set(True)

class RyModel_CircularTwist(Operator):
    bl_idname = "rymodel.circular_twist"
    bl_label = "Circular Twist"
    bl_description = "Bends the active (selected) object in a circle (applies rotation and scale to your object)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        active_object = context.active_object

        # Apply rotation & scale to avoid strange results when applying this modifier.
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # If any modifier exists, assume there is already a circular twist applied to the active object.
        displace_modifier1 = active_object.modifiers.get('CircularTwistDisplacement1')
        array_modifier =  active_object.modifiers.get('CircularTwistArray')
        simple_deform_modifier = active_object.modifiers.get('CircularTwistDeform')
        displace_modifier2 = active_object.modifiers.get('CircularTwistDisplacement2')
        weld_modifier = active_object.modifiers.get('CircularTwistWeld')
        if displace_modifier1 or array_modifier or displace_modifier2:
            rylog.log_status("Circular twist modifiers already exist on the active object, delete the existing circular twist modifiers before adding a new one.", self)
            return {'FINISHED'}

        # Add a displacement modifier.
        displace_modifier = active_object.modifiers.new('CircularTwistDisplacement1', 'DISPLACE')
        displace_modifier.strength = 2.0
        displace_modifier.mid_level = 0.0
        displace_modifier.direction = 'Y'
        displace_modifier.show_in_editmode = False
        displace_modifier.show_expanded = False

        # Add an array modifer.
        array_modifier = active_object.modifiers.new('CircularTwistArray', 'ARRAY')
        array_modifier.use_relative_offset = True
        array_modifier.count = 10
        array_modifier.use_merge_vertices = True
        array_modifier.show_in_editmode = False
        array_modifier.show_expanded = False

        # Add a simple deform modifier.
        simple_deform_modifier = active_object.modifiers.new('CircularTwistDeform', 'SIMPLE_DEFORM')
        simple_deform_modifier.angle = 6.28319
        simple_deform_modifier.deform_method = 'BEND'
        simple_deform_modifier.deform_axis = 'Z'
        simple_deform_modifier.show_in_editmode = False
        simple_deform_modifier.show_expanded = False

        # Duplicate the object and apply all mods then re-center the origin to get the Y location offset to re-center the object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = active_object
        active_object.select_set(True)
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        temp_obj = bpy.context.active_object

        for modifier in temp_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name, report=False)

        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        y_offset = temp_obj.location[1]
        bpy.ops.object.delete(use_global=False)

        # Add a second displacement modifier to re-center the objects mesh around it's origin.
        displacement_modifier_2 = active_object.modifiers.new('CircularTwistDisplacement2', 'DISPLACE')
        displacement_modifier_2.mid_level = 0.0
        displacement_modifier_2.direction = 'Y'
        displacement_modifier_2.show_in_editmode = False
        displacement_modifier_2.show_expanded = False
        displacement_modifier_2.strength = y_offset * -1

        # Add a weld modifier.
        weld_modifier = active_object.modifiers.new('CircularTwistWeld', 'WELD')
        weld_modifier.show_in_editmode = False
        weld_modifier.show_expanded = False

        # Select the original object.
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = active_object
        active_object.select_set(True)

        return {'FINISHED'}

#------------------------ CUTTERS ------------------------#

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
                                solidify_modifier.use_even_offset = True
                                solidify_modifier.thickness = 0.075
                        else: 
                            modifier.operation = context.scene.rymodel_boolean_mode

                            # For other boolean operations, remove the solidify modifier from the cutter if it exists.
                            solidify_modifier = context.active_object.modifiers.get("SliceSolidify")
                            if solidify_modifier:
                                context.active_object.modifiers.remove(solidify_modifier)

def hide_cutters():
    if not verify_active_mesh():
        return
    
    for obj in bpy.data.objects:
        if obj.name.startswith("Cutter_"):
            if obj != bpy.context.active_object or obj.select_get() == False:
                obj.hide_viewport = True

def show_cutters():
    if not verify_active_mesh():
        return

    for obj in bpy.data.objects:
        if obj.name.startswith("Cutter_"):
                obj.hide_viewport = False

def remove_unused_cutters():
    '''Removes all unused cutter objects and all boolean modifiers on all objects that have no object assigned'''
    used_cutter_objects = []
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'BOOLEAN':
                if modifier.object == None:
                    obj.modifiers.remove(modifier)
                else:
                    used_cutter_objects.append(modifier.object)

    for obj in bpy.data.objects:
        if obj.name.startswith("Cutter_"):
            if obj not in used_cutter_objects:
                bpy.data.objects.remove(obj)

class RyModel_AddCutter(Operator):
    bl_idname = "rymodel.add_cutter"
    bl_label = "Add Cutter"
    bl_description = "Adds a boolean modifier and a new object of the selected sharp to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    shape: StringProperty(default='CUBE')

    def execute(self, context):
        # Remove all unused cutters automatically.
        remove_unused_cutters()

        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        if context.active_object.name.startswith("Cutter_"):
            self.report({'INFO'}, "Can't add a cutter to a cutter object.")
            return {'FINISHED'}

        if self.shape == 'SELECTED_OBJECT':
            if len(bpy.context.selected_objects) != 2:
                self.report({'ERROR'}, "Select only the object you wish to use as a cutter and the object you wish to cut."})
                return {'FINISHED'}

        # We'll create the new cutter object at the center of the selected object. Move the 3D cursor there for later.
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        # Hide all existing cutters so the user can focus on the one they are adding.
        hide_cutters()

        # Create a new cutter collection if one does not exist.
        cutter_collection = bpy.data.collections.get("Cutters")
        if not cutter_collection:
            cutter_collection = bpy.data.collections.new("Cutters")
            cutter_collection.color_tag = 'COLOR_01'
            bpy.context.scene.collection.children.link(cutter_collection)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Add a new boolean modifier to the selected object.
        active_object = bpy.context.active_object
        boolean_count = 1
        boolean_mod_name = "Cutter_{0}".format(boolean_count)
        boolean_modifier = active_object.modifiers.get(boolean_mod_name)
        while active_object.modifiers.get(boolean_mod_name) != None:
            boolean_count += 1
            boolean_mod_name = "Cutter_{0}".format(boolean_count)
        boolean_modifier = active_object.modifiers.new(boolean_mod_name, 'BOOLEAN')

        # Adjust boolean settings.
        boolean_modifier.solver = 'FAST'
        boolean_modifier.show_in_editmode = True
        if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
            boolean_modifier.operation = 'DIFFERENCE'
        else:
            boolean_modifier.operation = bpy.context.scene.rymodel_boolean_mode

        # Organize the modifier stack.
        organize_modifier_stack(active_object.modifiers)


        # Get a unique name for the new cutter.
        cutter_number = 1
        new_cutter_name = "Cutter_{0}".format(cutter_number)

        cutter = bpy.data.objects.get(new_cutter_name)
        while cutter != None:
            cutter_number += 1
            new_cutter_name = "Cutter_{0}".format(cutter_number)
            cutter = bpy.data.objects.get(new_cutter_name)

        # Make the selected object into a cutter.
        if self.shape == 'SELECTED_OBJECT':
            new_cutter_object = context.selected_objects[0]
            if new_cutter_object == context.active_object:
                new_cutter_object = context.selected_objects[1]

            new_cutter_object.name = new_cutter_name

        # Create a new cutter mesh with a unique name based on the provided cutter type.
        else:
            new_mesh = bpy.data.meshes.new(new_cutter_name)

            bm = bmesh.new()
            match self.shape:

                case 'CUBE':
                    bmesh.ops.create_cube(bm, size=1.0)

                case 'CYLINDER':
                    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=32, radius1=1, radius2=1, depth=5)

                case 'SPHERE':
                    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1, calc_uvs=False)

                case 'CONE':
                    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=1, radius2=0, depth=3)
            bm.to_mesh(new_mesh)
            bm.free()

            # Create a new object for the cutter.
            cutter_number = 1
            new_cutter_object_name = "Cutter_{0}".format(cutter_number)
            new_cutter_object = bpy.data.objects.get(new_cutter_object_name)
            while new_cutter_object != None:
                cutter_number += 1
                new_cutter_object_name = "Cutter_{0}".format(cutter_number)
                new_cutter_object = bpy.data.objects.get(new_cutter_object_name)
            new_cutter_object = bpy.data.objects.new(new_cutter_object_name, new_mesh)

        # Add the object into the cutter collection.
        cutter_collection.objects.link(new_cutter_object)

        # Select only the new cutter.
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = new_cutter_object
        new_cutter_object.select_set(True)

        # Set the dimensions of the new cutter to be slightly larger than the dimensions of the selected object.
        match self.shape:
            case 'CUBE':
                new_cutter_object.dimensions = active_object.dimensions * 1.2

            case _:
                if self.shape != 'SELECTED_OBJECT':
                    largest_dimension = active_object.dimensions[0]
                    for i in range(1, len(active_object.dimensions)):
                        if active_object.dimensions[i] > largest_dimension:
                            largest_dimension = active_object.dimensions[i]

                    new_cutter_object.dimensions = (largest_dimension, largest_dimension, largest_dimension)

        # Shade smooth.
        bpy.ops.object.shade_smooth(use_auto_smooth=False, auto_smooth_angle=1.0472)

        # Add the object to the boolean modifier.
        boolean_modifier.object = new_cutter_object
        boolean_modifier.show_expanded = False

        # Display the cutter in wireframe.
        new_cutter_object.display_type = 'WIRE'

        # Adjust visibility settings.
        new_cutter_object.hide_render = True

        # For cutters using slice, add a solidify modifier.
        if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
            solidify_modifier = new_cutter_object.modifiers.new("SliceSolidify", 'SOLIDIFY')
            solidify_modifier.use_even_offset = True
            solidify_modifier.thickness = 0.075

        # Parent the cutter to the object.
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        return {'FINISHED'}

class RyModel_ShowCutters(Operator):
    bl_idname = "rymodel.show_cutters"
    bl_label = "Makes all cutter objects visible in the viewport"
    bl_description = "Show Cutters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        show_cutters()
        return {'FINISHED'}

class RyModel_CurveToRope(Operator):
    bl_idname = "rymodel.curve_to_rope"
    bl_label = "Curve To Rope"
    bl_description = "Converts the selected curve to a rope"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(default='BEVEL')

    def execute(self, context):

        return {'FINISHED'}

class RyModel_Cheshire(Operator):
    bl_idname = "rymodel.cheshire"
    bl_label = "Cheshire"
    bl_description = "Cheshire"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        return {'FINISHED'}

class RyModel_Unwrap(Operator):
    bl_idname = "rymodel.unwrap"
    bl_label = "Unwrap"
    bl_description = "Unwraps and packs the selected model using the best unwrapping method available amongst all packing / unwrapping add-ons you have installed in Blender, defaults to vanilla unwrapping and packing if you have no packing / unwrapping add-ons"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')

        addons = context.preferences.addons

        # Use UV Packer if it's installed.
        uv_packer = addons.get("UV-Packer")
        if uv_packer:
            bpy.ops.uvpackeroperator.packbtn()

        # User has no enabled add-ons, using vanilla packing method.
        else:
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            

        bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        return {'FINISHED'}

class RyModel_AutoSeam(Operator):
    bl_idname = "rymodel.auto_seam"
    bl_label = "Auto Seam"
    bl_description = "Marks seams for uv unwrapping for the selected object based on the angle geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}


#------------------------ PROPERTY RANGE OVERRIDES ------------------------#

# The vanilla slider ranges in Blender are in some cases way too large, making ui sliders unusable, these properties override modifier properties to provide better slider ranges.

def update_property_range_overrides():
    '''Updates all property range overrides - call when a new object is selected.'''
    active_object = bpy.context.active_object
    if active_object:
        # Update circular twist count.
        circular_twist_array_mod = active_object.modifiers.get('CircularTwistArray')
        if circular_twist_array_mod:
            bpy.context.scene.circular_twist_count = circular_twist_array_mod.count

        # Update property range overrides.
        bevel_modifier = get_modifier_of_type(active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bpy.context.scene.bevel_modifier_settings.segments = bevel_modifier.segments
            bpy.context.scene.bevel_modifier_settings.width = bevel_modifier.width

        solidify_modifier = get_modifier_of_type(active_object.modifiers, 'SOLIDIFY')
        if solidify_modifier:
            bpy.context.scene.solidify_modifier_settings.thickness = solidify_modifier.thickness

        array_modifier = get_modifier_of_type(active_object.modifiers, 'ARRAY')
        if array_modifier:
            bpy.context.scene.array_modifier_settings.count = array_modifier.count

        # Update curve settings.
        if active_object.type == 'CURVE':
            bpy.context.scene.curve_settings.bevel_depth = active_object.data.bevel_depth
            bpy.context.scene.curve_settings.bevel_resolution = active_object.data.bevel_resolution
            bpy.context.scene.curve_settings.extrude = active_object.data.extrude
            bpy.context.scene.curve_settings.resolution_u = active_object.data.resolution_u

def update_bevel_modifier_segments(self, context):
    if context.active_object:
        bevel_modifier = get_modifier_of_type(context.active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bevel_modifier.segments = context.scene.bevel_modifier_settings.segments

def update_bevel_modifier_width(self, context):
    if context.active_object:
        bevel_modifier = get_modifier_of_type(context.active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bevel_modifier.width = context.scene.bevel_modifier_settings.width

class BevelModifierSettings(PropertyGroup):
    segments: IntProperty(name="Segments", default=6, min=0, soft_max=10, update=update_bevel_modifier_segments)
    width: FloatProperty(name="Width", default=1, min=0, soft_max=10, update=update_bevel_modifier_width)

def update_solidify_thickness(self, context):
    if context.active_object:
        solidify_modifier = get_modifier_of_type(context.active_object.modifiers, 'SOLIDIFY')
        solidify_modifier.thickness = context.scene.solidify_modifier_settings.thickness

class SolidifyModifierSettings(PropertyGroup):
    thickness: FloatProperty(name="Thickness", default=1.0, min=-2.0, soft_max=2.0, update=update_solidify_thickness)

def update_array_modifier_count(self, context):
    if context.active_object:
        array_modifier = get_modifier_of_type(context.active_object.modifiers, 'ARRAY')
        array_modifier.count = context.scene.array_modifier_settings.count

class ArrayModifierSettings(PropertyGroup):
    count: IntProperty(name="Count", default=5, min=0, max=20, update=update_array_modifier_count)

def update_curve_bevel_depth(self, context):
    if context.active_object:
        context.active_object.data.bevel_depth = context.scene.curve_settings.bevel_depth

def update_curve_bevel_resolution(self, context):
    if context.active_object:
        context.active_object.data.bevel_resolution = context.scene.curve_settings.bevel_resolution

def update_curve_extrude(self, context):
    if context.active_object:
        context.active_object.data.extrude = context.scene.curve_settings.extrude

def update_curve_resolution_u(self, context):
    if context.active_object:
        context.active_object.data.resolution_u = context.scene.curve_settings.resolution_u

class CurveSettings(PropertyGroup):
    bevel_depth: FloatProperty(name="Bevel Depth", default=0.5, min=0, soft_max=1, update=update_curve_bevel_depth)
    bevel_resolution: IntProperty(name="Bevel Resolution", default=5, min=0, soft_max=20, update=update_curve_bevel_resolution)
    extrude: FloatProperty(name="Extrude", default=5, min=0, soft_max=3, update=update_curve_extrude)
    resolution_u: IntProperty(name="Resolution U", default=5, min=0, soft_max=12, update=update_curve_resolution_u)