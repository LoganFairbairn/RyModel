# This module provides operators to help speed up the modeling workflow in Blender.

import bpy
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

        match self.axis:
            case 'X':
                mirror_modifier.use_axis[0] = True
                
            case 'Y':
                mirror_modifier.use_axis[1] = True
                mirror_modifier.use_axis[0] = False
                
            case 'Z':
                mirror_modifier.use_axis[2] = True
                mirror_modifier.use_axis[0] = False


        organize_modifier_stack(context.active_object.modifiers)

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
        return {'FINISHED'}

class RyModel_CleanMesh(Operator):
    bl_idname = "rymodel.clean_mesh"
    bl_label = "Clean Mesh"
    bl_description = "Removes doubles and non-manifold geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}

        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # Remove non-manifold geometry.
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.delete(type='VERT')

        # Remove doubles.
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()

        bpy.ops.object.mode_set(mode=original_mode, toggle=False)

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
    solidify_modifier = get_modifier_of_type(object_modifiers, 'SOLIDIFY')
    boolean_modifiers = get_modifiers_of_type(object_modifiers, 'BOOLEAN')

    modifier_index = 0

    if solidify_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=solidify_modifier.name, index=modifier_index)
        modifier_index += 1

    if mirror_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=mirror_modifier.name, index=modifier_index)
        modifier_index += 1

    if len(boolean_modifiers) > 0:
        for boolean_modifier in boolean_modifiers:
            bpy.ops.object.modifier_move_to_index(modifier=boolean_modifier.name, index=modifier_index)
            modifier_index += 1

    if weighted_normal_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=weighted_normal_modifier.name, index=len(object_modifiers) - 1)

    if bevel_modifier:
        if weighted_normal_modifier:
            bpy.ops.object.modifier_move_to_index(modifier=bevel_modifier.name, index=len(object_modifiers) - 2)
        else:
            bpy.ops.object.modifier_move_to_index(modifier=bevel_modifier.name, index=len(object_modifiers) - 1)

class RyModel_AddModifier(Operator):
    bl_idname = "rymodel.add_modifier"
    bl_label = "Add Modifier"
    bl_description = "Adds a modifier of the specified type to the active object, then re-organizes the modifier stack"
    bl_options = {'REGISTER', 'UNDO'}

    type: StringProperty(default='BEVEL')

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        if not context.active_object.modifiers.get(str(self.type)):
            new_modifier = context.active_object.modifiers.new(str(self.type), self.type)

        organize_modifier_stack(context.active_object.modifiers)

        return {'FINISHED'}

class RyModel_DeleteModifier(Operator):
    bl_idname = "rymodel.delete_modifier"
    bl_label = "Delete Modifier"
    bl_description = "Deletes the modifier from the active (selected) object, then re-organizes the modifier stack"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: StringProperty(default="")

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
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

def update_radial_offset(self, context):
    if not verify_active_mesh():
        return

    displace_modifier = context.active_object.modifiers.get('RadialArrayDisplacement')
    if displace_modifier:
        displace_modifier.strength = context.scene.radial_array_settings.offset

def update_radial_count(self, context):
    if not verify_active_mesh():
        return
    
    array_modifier = context.active_object.modifiers.get('RadialArray')
    array_modifier.count = context.scene.radial_array_settings.count
    empty_object = array_modifier.offset_object
    empty_object.rotation_euler[2] = math.radians(360 / array_modifier.count)

class RadialArraySettings(PropertyGroup):
    offset: FloatProperty(name="Offset", default=2.0, min=0.0, soft_max=5.0, update=update_radial_offset)
    count: IntProperty(name="Count", default=10, min=0, soft_max=100, update=update_radial_count)

class RyModel_RadialArray(Operator):
    bl_idname = "rymodel.radial_array"
    bl_label = "Radial Array"
    bl_description = "Applies a radial array to the active (selected) object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_object = context.active_object
        displace_modifier = context.active_object.modifiers.get('RadialArrayDisplacement')
        array_modifier =  context.active_object.modifiers.get('RadialArray')

        # If either modifier exists, assume there is already a radial array applied to the active object.
        if displace_modifier or array_modifier:
            rylog.log_status("Radial array modifiers already exist on the active object, delete the existing radial array if you want a new one.", self)
            return {'FINISHED'}

        # Add a displacement modifier.
        if not displace_modifier:
            displace_modifier = context.active_object.modifiers.new('RadialArrayDisplacement', 'DISPLACE')
        displace_modifier.strength = 1.0
        displace_modifier.mid_level = 0.0
        displace_modifier.direction = 'X'
        displace_modifier.show_expanded = False

        # Add an array modifer.
        if not array_modifier:
            array_modifier = context.active_object.modifiers.new('RadialArray', 'ARRAY')
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

class RyModel_RemoveRadialArray(Operator):
    bl_idname = "rymodel.remove_radial_array"
    bl_label = "Remove Radial Array"
    bl_description = "Removes a radial array setup (created with this add-on) from the active object if one exists"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not verify_active_mesh(self):
            return {'FINISHED'}
        
        original_object = context.active_object
        displace_modifier = context.active_object.modifiers.get('RadialArrayDisplacement')
        array_modifier =  context.active_object.modifiers.get('RadialArray')

        if displace_modifier:
            original_object.modifiers.remove(displace_modifier)

        if array_modifier:
            original_object.modifiers.remove(array_modifier)

        

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

#------------------------ CUTTERS ------------------------#

CUTTER_MODE = [
    ("INTERSECT", "Intersect", "", 1),
    ("UNION", "Union", "", 2),
    ("DIFFERENCE", "Difference", "", 3),
    ("SLICE", "Slice", "", 4)
]

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
        if not verify_active_mesh(self):
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
        if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
            boolean_modifier.operation = 'DIFFERENCE'
        else:
            boolean_modifier.operation = bpy.context.scene.rymodel_boolean_mode

        # Organize the modifier stack.
        organize_modifier_stack(active_object.modifiers)

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
            solidify_modifier.use_even_offset = True
            solidify_modifier.thickness = 0.075

        # Set the location of the cutter.
        new_cutter_object.location = bpy.context.scene.cursor.location

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
        
        addons = context.preferences.addons

        # Use UV Packer if it's installed.
        uv_packer = addons.get("UV-Packer")
        if uv_packer:
            bpy.ops.uvpackeroperator.packbtn()

        # User has no enabled add-ons, using vanilla packing method.
        else:
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            
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