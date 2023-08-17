import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty
import blf
import gpu
import bmesh
from gpu_extras.batch import batch_for_shader
from ..core import modifiers
from ..core import internal_utils
from ..core import rylog

def update_mirror_x(self, context):
    if bpy.context.scene.rymodel_update_mirroring:
        mirror_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
        if context.scene.rymodel_mirror_x:
            if mirror_modifier == None:
                mirror_modifier = add_mirror_modifier('X')
        mirror_modifier.use_axis[0] = context.scene.rymodel_mirror_x

def update_mirror_y(self, context):
    if bpy.context.scene.rymodel_update_mirroring:
        mirror_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
        if context.scene.rymodel_mirror_y:
            if mirror_modifier == None:
                mirror_modifier = add_mirror_modifier('Y')
        mirror_modifier.use_axis[1] = context.scene.rymodel_mirror_y

def update_mirror_z(self, context):
    if bpy.context.scene.rymodel_update_mirroring:
        mirror_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
        if context.scene.rymodel_mirror_z:
            if mirror_modifier == None:
                mirror_modifier = add_mirror_modifier('Z')
        mirror_modifier.use_axis[2] = context.scene.rymodel_mirror_z

def update_mirror_properties():
    bpy.context.scene.rymodel_update_mirroring = False
    active_object = bpy.context.active_object
    if active_object:
        mirror_modifier = modifiers.get_modifier_of_type(active_object.modifiers, 'MIRROR')
        if mirror_modifier:
            bpy.context.scene.rymodel_mirror_x = mirror_modifier.use_axis[0]
            bpy.context.scene.rymodel_mirror_y = mirror_modifier.use_axis[1]
            bpy.context.scene.rymodel_mirror_z = mirror_modifier.use_axis[2]

        else:
            bpy.context.scene.rymodel_mirror_x = 0
            bpy.context.scene.rymodel_mirror_y = 0
            bpy.context.scene.rymodel_mirror_z = 0

    else:
        bpy.context.scene.rymodel_mirror_x = 0
        bpy.context.scene.rymodel_mirror_y = 0
        bpy.context.scene.rymodel_mirror_z = 0
    bpy.context.scene.rymodel_update_mirroring = True

def update_mirror_flip(self, context):
    mirror_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
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
    mirror_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'MIRROR')
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

def delete_vertices_past_axis(mesh_object, axis, flip_axis=False, bisect=True):
    '''Bisects the given object along the given axis, then deletes all vertices past the selected axis.'''

    # Bisect the mesh based on the provided axis.
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')
    match axis:
        case 'X':
            bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.000001, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)
            
        case 'Y':
            bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 1.0, 0.0), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.000001, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)
            
        case 'Z':
            bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 0.0, 1.0), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.000001, xstart=0, xend=0, ystart=0, yend=0, flip=False, cursor=5)

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.modifier_apply(modifier="Mirror")

    # Delete all vertices past the provided axis.
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    me = mesh_object.data

    bm = bmesh.from_edit_mesh(me)

    delete_verts = []
    axis_index = 0
    match axis:
        case 'X':
            axis_index = 0
        case 'Y':
            axis_index = 1
        case 'Z':
            axis_index = 2
        case _:
            rylog.log("Error: Invalid axis provided to delete_past_axis.")

    # 0 causes floating point errors occasionally so we'll use 0.0001.
    if flip_axis:
        for vert in bm.verts:
            if vert.co[axis_index] < -0.0001:
                delete_verts.append(vert)
    else:
        for vert in bm.verts:
            if vert.co[axis_index] > 0.0001:
                delete_verts.append(vert)

    bmesh.ops.delete(bm, geom=delete_verts, context='VERTS') 
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # Make sure to update ui mirror properties.
    update_mirror_properties()

class RyModel_DeleteVerticesPastAxis(Operator):
    bl_idname = "rymodel.delete_vertices_past_axis"
    bl_label = "Delete Vertices Past Axis"
    bl_description = "Deletes all vertices past the provided axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: StringProperty(default='X')

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        delete_vertices_past_axis(context.active_object, self.axis, bpy.context.scene.rymodel_flip_bidelete, bpy.context.scene.rymodel_bidelete_bisect)
        
        return {'FINISHED'}

def add_mirror_modifier(axis):
    active_object = bpy.context.active_object

    # Add a mirror modifier if one doesn't exist.
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.modifier_add(type='MIRROR')
    mirror_modifier = modifiers.get_modifier_of_type(active_object.modifiers, 'MIRROR')
    if not mirror_modifier:
        mirror_modifier = active_object.modifiers.new("Mirror", 'MIRROR')
    mirror_modifier.use_clip = True
    mirror_modifier.show_on_cage = True

    match axis:
        case 'X':
            mirror_modifier.use_axis[0] = True
            
        case 'Y':
            mirror_modifier.use_axis[1] = True
            mirror_modifier.use_axis[0] = False
            
        case 'Z':
            mirror_modifier.use_axis[2] = True
            mirror_modifier.use_axis[0] = False

    modifiers.organize_modifier_stack(active_object.modifiers)

    return mirror_modifier

def set_object_origin(location, self):
    original_mode = bpy.context.mode

    active_object = bpy.context.active_object
    if active_object:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        match location:
            case 'WORLD_ORIGIN':
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

            case 'SELECTED':
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

            case 'TRUE_CENTER':
                center = internal_utils.get_object_true_center(active_object)
                bpy.context.scene.cursor.location = center
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        internal_utils.set_object_interaction_mode(original_mode)

    else:
        self.report({'ERROR'}, "No active object, select an object to reset it's origin.")

class RyModel_SetOriginWorld(Operator):
    bl_idname = "rymodel.set_origin_world_center"
    bl_label = "Set Origin World Center"
    bl_description = "Sets the selected objects origin to the world center"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_object_origin('WORLD_ORIGIN', self)
        return {'FINISHED'}

class RyModel_SetOriginSelected(Operator):
    bl_idname = "rymodel.set_origin_selected"
    bl_label = "Set Origin Selected"
    bl_description = "Sets the selected objects origin to the selected element"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_object_origin('SELECTED', self)
        return {'FINISHED'}

class RyModel_SetOriginCenter(Operator):
    bl_idname = "rymodel.set_origin_center"
    bl_label = "Set Origin Center"
    bl_description = "Sets the selected objects origin to the center"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_object_origin('TRUE_CENTER', self)
        return {'FINISHED'}

class RyModel_CenterAxis(Operator):
    bl_idname = "rymodel.center_axis"
    bl_label = "Center Axis"
    bl_description = "Centers the selected object on the provided axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: StringProperty(default='X')

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        match self.axis:
            case 'X':
                bpy.context.active_object.location[0] = 0.0
            case 'Y':
                bpy.context.active_object.location[1] = 0.0
            case 'Z':
                bpy.context.active_object.location[2] = 0.0
            case _:
                rylog.log("Error: Invalid axis provided for center axis operator.")

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_AutoSharpen(Operator):
    bl_idname = "rymodel.auto_sharpen"
    bl_label = "Auto Sharpen"
    bl_description = "Applies auto smooth, then bevel weights and sharpen by angles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
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
        bpy.ops.mesh.edges_select_sharp(sharpness=context.scene.auto_sharpen_angle)
        bpy.ops.mesh.mark_sharp()
        bpy.ops.transform.edge_bevelweight(value=1.0, snap=False)

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_AutoSmooth(Operator):
    bl_idname = "rymodel.auto_smooth"
    bl_label = "Auto Smooth"
    bl_description = "Applies auto smooth and clears all bevel weights and sharpening"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode

        # Clear all bevel weights.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        if bpy.context.active_object.data.has_bevel_weight_edge:
            bpy.ops.mesh.customdata_bevel_weight_edge_clear()

        # Apply autosmooth.
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 3.14159

        # Clear all bevel weights and sharpening.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.mark_sharp(clear=True)

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_ExtractFace(Operator):
    bl_idname = "rymodel.extract_face"
    bl_label = "Extract Face"
    bl_description = "Separates the selected faces from the object into a new object, and applied a solidify modifier to the new object for thickess"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        if bpy.context.mode != 'EDIT_MESH':
            return
        
        if not bpy.context.scene.tool_settings.mesh_select_mode[2]:
            return
        
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

        bpy.ops.mesh.separate(type='SELECTED')

        new_object = context.selected_objects[0]
        if len(context.selected_objects) > 1:
            if context.selected_objects[0] == new_object:
                new_object = context.selected_objects[1]

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
        if not internal_utils.verify_active_mesh(self):
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
        if not internal_utils.verify_active_mesh(self):
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
    bl_description = "Applies rotation and scale, removes vertex doubles, loose geometry, and recalculates face and vertex normals to point outside"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}

        # Toggle into edit mode, remember the original mode.
        original_mode = bpy.context.mode

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Remove loose faces.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.delete(type='FACE')

        # Re-calculate outside.
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

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
        internal_utils.set_object_interaction_mode(original_mode)

        return {'FINISHED'}

class RyModel_FillNonManifold(Operator):
    bl_idname = "rymodel.fill_non_manifold"
    bl_label = "Fill Non-Manifold"
    bl_description = "Fills non-manifold geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.edge_face_add()
        internal_utils.set_object_interaction_mode(original_mode)
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

class RyModel_DrawShape(Operator):
    bl_idname = "rymodel.draw_shape"
    bl_label = "Draw Shape"
    bl_description = "Click to create vertices of a shape, which is automatically extruded and filled. If an object is selected, the new shape will be applied as a boolean object"

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
        if not internal_utils.verify_active_mesh(self):
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
        internal_utils.set_object_interaction_mode(original_mode)

        align_cursor_to_face()

        return {'FINISHED'}

def align_cursor_to_face():
    if not internal_utils.verify_active_mesh():
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

class RyModel_AutoSeam(Operator):
    bl_idname = "rymodel.auto_seam"
    bl_label = "Auto Seam"
    bl_description = "Marks seams for uv unwrapping for the selected object based on the angle geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_ColorGrid(Operator):
    bl_idname = "rymodel.color_grid"
    bl_label = "Color Grid"
    bl_description = "Removes all materials from the selected objects and applies a material with a color grid ideal for viewing UV unwrapping quality"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}

        # Must be in object mode.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # Create a new material.
        color_grid_material = bpy.data.materials.get('ColorGrid')
        if not color_grid_material:
            color_grid_material = bpy.data.materials.new(name='ColorGrid')
            color_grid_material.use_nodes = True

        # Create a new color grid texture.
        color_grid_image = bpy.data.images.get('ColorGrid')
        if color_grid_image:
            bpy.data.images.remove(color_grid_image)
        bpy.ops.image.new(name='ColorGrid', width=2048, height=2048, color=(0.0, 0.0, 0.0, 1.0), alpha=False, generated_type='COLOR_GRID', float=False, use_stereo_3d=False, tiled=False)
        color_grid_image = bpy.data.images.get('ColorGrid')

        # Assign the color grid texture to the image shader node and connect it to the principled bsdf.
        principled_bsdf = color_grid_material.node_tree.nodes.get("Principled BSDF")
        image_node = color_grid_material.node_tree.nodes.new('ShaderNodeTexImage')
        image_node.image = color_grid_image
        image_node.location = (-300, 300)
        color_grid_material.node_tree.links.new(image_node.outputs[0], principled_bsdf.inputs[0])
        
        # Assign the new color grid material to all selected objects.
        for obj in bpy.context.selected_objects:
            obj.active_material_index = 0
            for i in range(len(obj.material_slots)):
                obj.material_slots[i].material = color_grid_material

        return {'FINISHED'}

class RyModel_DeformArrayAlongCurve(Operator):
    bl_idname = "rymodel.deform_array_along_curve"
    bl_label = "Deform Array Along Curve"
    bl_description = "Arrays the selected mesh along a curve object, in addition to deforming the object so mesh instances weld together"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        original_object = context.active_object

        # TODO: Verify only 1 object is selected.

        # Apply modifiers.
        array_mod = modifiers.add_modifier('ARRAY', self, context)
        array_mod.relative_offset_displace = (0, 0, 1)
        array_mod.fit_type = 'FIT_CURVE'
        modifiers.add_modifier('WELD', self, context)
        curve_mod = modifiers.add_modifier('CURVE', self, context)
        curve_mod.deform_axis = 'POS_Z'

        # Create a new curve object at the location of the original object.
        curve_start_location = original_object.location
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False, align='WORLD', location=curve_start_location, scale=(1, 1, 1))
        new_curve_object = context.active_object
        new_curve_object.show_in_front = True
        curve_mod.object = new_curve_object
        array_mod.curve = new_curve_object

        # Parent the original object to the curve. Note: I've used ops here because matrix inverting seemed to not work.
        bpy.ops.object.select_all(action='DESELECT')
        original_object.select_set(True)
        new_curve_object.select_set(True)
        bpy.context.view_layer.objects.active = new_curve_object
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Make the original object not selectable so the users don't accidentally select it while attempting to select the curve.
        original_object.hide_select = True

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_ArrayAlongCurve(Operator):
    bl_idname = "rymodel.array_along_curve"
    bl_label = "Array Along Curve"
    bl_description = "Arrays the selected mesh along a curve object, without deforming the object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        original_object = context.active_object

        # TODO: Verify only 1 object is selected.


        # Create a new curve object at the location of the original object.
        curve_start_location = original_object.location
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False, align='WORLD', location=curve_start_location, scale=(1, 1, 1))
        new_curve_object = context.active_object
        new_curve_object.show_in_front = True

        # Add a plane object to array along.
        plane_start_location = original_object.location
        bpy.ops.mesh.primitive_plane_add(size=0.001, enter_editmode=False, align='WORLD', location=plane_start_location, scale=(1, 1, 1))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        new_plane_object = context.active_object
        array_mod = modifiers.add_modifier('ARRAY', self, context)
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0.15, 0, 0)
        array_mod.fit_type = 'FIT_CURVE'
        curve_mod = modifiers.add_modifier('CURVE', self, context)
        curve_mod.deform_axis = 'POS_X'
        curve_mod.object = new_curve_object
        array_mod.curve = new_curve_object
        
        # Parent the original object to the plane. Note: I've used ops here because matrix inverting seemed to not work.
        bpy.ops.object.select_all(action='DESELECT')
        original_object.select_set(True)
        new_plane_object.select_set(True)
        bpy.context.view_layer.objects.active = new_plane_object
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        new_plane_object.instance_type = 'FACES'

        # Parent the plane object to the curve.
        bpy.ops.object.select_all(action='DESELECT')
        new_plane_object.select_set(True)
        new_curve_object.select_set(True)
        bpy.context.view_layer.objects.active = new_curve_object
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Make the plane object not selectable so the users don't accidentally select it while attempting to select the curve.
        new_plane_object.hide_select = True

        original_object.hide_set(True)

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_DeleteCurveArray(Operator):
    bl_idname = "rymodel.delete_curve_array"
    bl_label = "Delete Curve Array"
    bl_description = "Deletes the curve array effect applied to the selected curve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        original_object = context.active_object

        if original_object.type != 'CURVE':
            rylog.log_status("Selected object must be a curve to perform this operation.")
            return {'FINISHED'}

        # Unparent all child objects of the curve.
        for obj in original_object.children:
            bpy.ops.object.select_all(action='DESELECT')
            obj.hide_select = False
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            # Unparent child objects for this child object.
            for child_obj in obj.children:
                bpy.ops.object.select_all(action='DESELECT')
                child_obj.hide_select = False
                child_obj.select_set(True)
                bpy.context.view_layer.objects.active = child_obj
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            # If child objects of a child object existed, then this is a curve array effect, delete the array mesh.
            if len(obj.children) != 0:
                original_mesh_obj = obj.children[0]

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.delete()

            else:
                original_mesh_obj = obj

        # Delete the curve.
        bpy.ops.object.select_all(action='DESELECT')
        original_object.select_set(True)
        bpy.context.view_layer.objects.active = original_object
        bpy.ops.object.delete()

        # Select the original mesh object used in the curve array effect.
        bpy.ops.object.select_all(action='DESELECT')
        original_mesh_obj.hide_set(False)
        original_mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = original_mesh_obj  
        
        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}

class RyModel_CurveArrayToMesh(Operator):
    bl_idname = "rymodel.curve_array_to_mesh"
    bl_label = "Curve Array to Mesh"
    bl_description = "Converts the selected curve array to a mesh and cleans up objects if they exist"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        original_object = context.active_object
        if original_object.type != 'CURVE':
            rylog.log_status("Selected object must be a curve to perform this operation.")
            return {'FINISHED'}

        # Convert the curve array to a mesh.
        child_object = original_object.children[0]
        if len(child_object.children) != 0:
            original_mesh_obj = child_object.children[0]
            bpy.ops.object.select_all(action='DESELECT')
            original_mesh_obj.hide_select = False
            original_mesh_obj.hide_set(False)
            original_mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_mesh_obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.convert(target='MESH')

            # Delete the plane mesh used for the curve array.
            bpy.ops.object.select_all(action='DESELECT')
            child_object.select_set(True)
            bpy.context.view_layer.objects.active = child_object
            bpy.ops.object.delete()

        else:
            original_mesh_obj = original_object.children[0]
            bpy.ops.object.select_all(action='DESELECT')
            original_mesh_obj.hide_select = False
            original_mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = original_mesh_obj
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.convert(target='MESH')

        # Delete the curve.
        bpy.ops.object.select_all(action='DESELECT')
        original_object.select_set(True)
        bpy.context.view_layer.objects.active = original_object
        bpy.ops.object.delete()

        # Select the original mesh object used in the curve array effect.
        bpy.ops.object.select_all(action='DESELECT')
        original_mesh_obj.hide_set(False)
        original_mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = original_mesh_obj  

        internal_utils.set_object_interaction_mode(original_mode)
        return {'FINISHED'}
