# This module provides operators to help speed up the modeling workflow in Blender.

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import StringProperty

class RyModel_Mirror(Operator):
    bl_idname = "rymodel.mirror"
    bl_label = "Mirror"
    bl_description = "Applies a mirror modifier to the select object based on the provided axis. Only 1 mirror modifier will be applied per object. If Symmetry is ticked, the modifier will be automatically applied."
    bl_options = {'REGISTER', 'UNDO'}

    axis: StringProperty(default='X')

    def execute(self, context):
        bpy.ops.object.modifier_add(type='MIRROR')
        mirror_modifier = context.active_object.modifiers.get('Mirror')
        if not mirror_modifier:
            mirror_modifier = context.active_object.modifiers.new("Mirror", 'MIRROR')
            mirror_modifier.use_clip = True

        match self.axis:
            case 'X':
                mirror_modifier.use_axis[0] = True
                
            case 'Y':
                mirror_modifier.use_axis[1] = True
                mirror_modifier.use_axis[0] = False
                
            case 'Z':
                mirror_modifier.use_axis[2] = True
                mirror_modifier.use_axis[0] = False

            case 'BISECT_X':
                mirror_modifier.use_axis[0] = True
                mirror_modifier.use_bisect_axis[0] = True

            case 'BISECT_Y':
                mirror_modifier.use_axis[0] = False
                mirror_modifier.use_axis[1] = True
                mirror_modifier.use_bisect_axis[1] = True

            case 'BISECT_Z':
                mirror_modifier.use_axis[0] = False
                mirror_modifier.use_axis[2] = True
                mirror_modifier.use_bisect_axis[2] = True

            case 'FLIP_X':
                mirror_modifier.use_axis[0] = True
                mirror_modifier.use_bisect_flip_axis[0] = True

            case 'FLIP_Y':
                mirror_modifier.use_axis[1] = True
                mirror_modifier.use_axis[0] = False
                mirror_modifier.use_bisect_flip_axis[1] = True

            case 'FLIP_Z':
                mirror_modifier.use_axis[2] = True
                mirror_modifier.use_axis[0] = False
                mirror_modifier.use_bisect_flip_axis[2] = True


        return {'FINISHED'}

class RyModel_ResetOrigin(Operator):
    bl_idname = "rymodel.reset_origin"
    bl_label = "Reset Origin"
    bl_description = "Resets the objects origin to the specified location"
    bl_options = {'REGISTER', 'UNDO'}

    location: StringProperty(default='Y_AXIS')

    def execute(self, context):
        match self.location:
            case 'WORLD_ORIGIN':
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            case 'SELECTED':
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            case 'SURFACE':
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
            case 'VOLUME':
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        return {'FINISHED'}

class RyModel_AutoSharpen(Operator):
    bl_idname = "rymodel.auto_sharpen"
    bl_label = "Auto Sharpen"
    bl_description = "Applies auto smooth, then bevel weights and sharpen by angles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        original_mode = bpy.context.mode

        # Apply autosmooth.
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 1.0472

        # Shade smooth.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.faces_shade_smooth()

        # Apply bevel weights.
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
        bpy.ops.transform.edge_bevelweight(value=0.467186, snap=False)

        # Apply sharpen by angle.
        bpy.ops.mesh.mark_sharp()

        bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}

class RyModel_CleanMesh(Operator):
    bl_idname = "rymodel.clean_mesh"
    bl_label = "Clean Mesh"
    bl_description = "Removes doubles and non-manifold geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #if context.active_object:
        #    if context.active_object.type == 'MESH':

        # Merge double vertices.

        # Clean Non-Manifold geometry.
        return {'FINISHED'}

class RyModel_AddModifier(Operator):
    bl_idname = "rymodel.add_modifier"
    bl_label = "Add Modifier"
    bl_description = "Adds a modifier of the specified type to the active object, then re-organizes the modifier stack"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(default='BEVEL')

    def execute(self, context):
        if context.active_object:
            new_modifier = context.active_object.modifiers.new(str(self.type), self.type)
            new_modifier.show_expanded = False
        return {'FINISHED'}

class RyModel_CopyModifiers(Operator):
    bl_idname = "rymodel.copy_modifiers"
    bl_label = "Copy Modifiers"
    bl_description = "Copies modifiers from the selected object to the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object:
            if len(context.selected_objects) == 2:
                transfer_object = context.selected_objects[1]
                if context.selected_objects[1] == context.active_object:
                    transfer_object = context.selected_objects[0]

                for original_modifier in transfer_object.modifiers:
                    new_modifier = context.active_object.modifiers.new(original_modifier.name, original_modifier.type)
                    match new_modifier.type:
                        case 'BEVEL':
                            new_modifier.affect = original_modifier.affect
                            new_modifier.angle_limit = original_modifier.angle_limit
                            new_modifier.face_strength_mode = original_modifier.face_strength_mode
                            new_modifier.harden_normals = original_modifier.harden_normals
                            new_modifier.invert_vertex_group = original_modifier.invert_vertex_group
                            new_modifier.limit_method = original_modifier.limit_method
                            new_modifier.loop_slide = original_modifier.loop_slide
                            new_modifier.mark_seam = original_modifier.mark_seam
                            new_modifier.material = original_modifier.material
                            new_modifier.miter_inner = original_modifier.miter_inner
                            new_modifier.miter_outer = original_modifier.miter_outer
                            new_modifier.offset_type = original_modifier.offset_type
                            new_modifier.profile = original_modifier.profile
                            new_modifier.profile_type = original_modifier.profile_type
                            new_modifier.segments = original_modifier.segments
                            new_modifier.spread = original_modifier.spread
                            new_modifier.use_clamp_overlap = original_modifier.use_clamp_overlap
                            new_modifier.segments = original_modifier.segments

                        case 'WEIGHTED_NORMAL':
                            new_modifier.weight = original_modifier.weight
                            new_modifier.thresh = original_modifier.thresh

                        #case 'SOLIDIFY':

                        #case 'ARRAY':

                        #case 'RADIAL_ARRAY':

                        #case 'MULTIRES'

                        #case 'REMESH'
                        
                        #case 'SUBSURF'

                        #case 'SHRINKWRAP'

                        #case 'TRIANGULATE'


        return {'FINISHED'}

class RyModel_HSWFModApply(Operator):
    bl_idname = "rymodel.hswf_mod_apply"
    bl_label = "HSWF Mod Apply"
    bl_description = "Applies all modifiers to the object, excluding bevel and weighted normal modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object:
            for modifier in context.active_object.modifiers:
                if modifier.type != 'BEVEL' and modifier.type != 'WEIGHTED_NORMAL':
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
        return {'FINISHED'}

class RyModel_RadialArray(Operator):
    bl_idname = "rymodel.radial_array"
    bl_label = "Radial Array"
    bl_description = "Applies a radial array to the select object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object:
            if not context.active_object.modifiers.get('RadialArray'):
                array_modifier = context.active_object.modifiers.new('RadialArray', 'ARRAY')
            array_modifier.use_object_offset = True
            array_modifier.use_object_offset = True

        return {'FINISHED'}

class RyModel_AddCutter(Operator):
    bl_idname = "rymodel.add_cutter"
    bl_label = "Add Cutter"
    bl_description = "Adds a boolean modifier and a new object of the selected sharp to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    shape: StringProperty(default='CUBE')

    def execute(self, context):
        if not context.active_object:
            self.report({'INFO'}, "No object selected to add a cutter to.")
            return {'FINISHED'}

        if context.active_object.type != 'MESH':
            self.report({'INFO'}, "Can't add a cutter to a non-mesh object.")
            return {'FINISHED'}
        
        if context.active_object.name.startswith("Cutter_"):
            self.report({'INFO'}, "Can't add a cutter to a cutter object.")
            return {'FINISHED'}

        # We'll create the new cutter object at the center of the selected object. Move the 3D cursor there for later.
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)

        # Hide all existing cutters so the user can focus on the one they are adding.
        bpy.ops.rymodel.hide_cutters()

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
        if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
            boolean_modifier.operation = 'DIFFERENCE'
        else:
            boolean_modifier.operation = bpy.context.scene.rymodel_boolean_mode

        # Create a new cutter mesh with a unique name based on the provided cutter type.
        cutter_number = 1
        new_cutter_name = "CutterMesh_{0}".format(cutter_number)
        new_mesh = bpy.data.meshes.get(new_cutter_name)
        while new_mesh != None:
            cutter_number += 1
            new_cutter_name = "CutterMesh_{0}".format(cutter_number)
            new_mesh = bpy.data.meshes.get(new_cutter_name)
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

        # Add the object into the scene.
        cutter_collection.objects.link(new_cutter_object)

        # Select only the new cutter.
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = new_cutter_object
        new_cutter_object.select_set(True)

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
            solidify_modifier.thickness = 0.075

        # Set the location of the cutter.
        new_cutter_object.location = bpy.context.scene.cursor.location
        
        return {'FINISHED'}

class RyModel_HideCutters(Operator):
    bl_idname = "rymodel.hide_cutters"
    bl_label = "Hide Cutters"
    bl_description = "Hides all boolean cutter objects excluding the activly selected one"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.name.startswith("Cutter_"):
                if obj != context.active_object or obj.select_get() == False:
                    obj.hide_viewport = True
        return {'FINISHED'}

class RyModel_ShowCutters(Operator):
    bl_idname = "rymodel.show_cutters"
    bl_label = "Show Cutters"
    bl_description = "Shows all boolean cutter objects for the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.name.startswith("Cutter_"):
                    obj.hide_viewport = False
        return {'FINISHED'}

class RyModel_RemoveUnusedCutters(Operator):
    bl_idname = "rymodel.remove_unused_cutters"
    bl_label = "Remove Unused Cutters"
    bl_description = "Removes all unused cutter objects and all boolean modifiers with no objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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

        return {'FINISHED'}

class RyModel_AutoSeam(Operator):
    bl_idname = "rymodel.auto_seam"
    bl_label = "Auto Seam"
    bl_description = "Marks seams for uv unwrapping for the selected object based on the angle geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}