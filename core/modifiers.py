import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import IntProperty, FloatProperty, StringProperty
from ..core import property_range_overrides
from . import booleans
from ..core import modeling_tools
from ..core import internal_utils
from ..core import rylog
import math

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

    for boolean_modifier in boolean_modifiers:
        bpy.ops.object.modifier_move_to_index(modifier=boolean_modifier.name, index=modifier_index)
        modifier_index += 1

    if mirror_modifier:
        bpy.ops.object.modifier_move_to_index(modifier=mirror_modifier.name, index=modifier_index)
        modifier_index += 1

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
    if not internal_utils.verify_active_mesh(self):
        return {'FINISHED'}
    
    modifier_name = modifier_type.replace('_', ' ')
    new_modifier = context.active_object.modifiers.get(modifier_name)
    if not new_modifier:
        new_modifier = context.active_object.modifiers.new(modifier_type, modifier_type)
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
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddWeightedNormalModifier(Operator):
    bl_idname = "rymodel.add_weighted_normal_modifier"
    bl_label = "Add Weighted Normal Modifier"
    bl_description = "Adds a weighted normal modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        add_modifier('WEIGHTED_NORMAL', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddSolidifyModifier(Operator):
    bl_idname = "rymodel.add_solidify_modifier"
    bl_label = "Add Solidify Modifier"
    bl_description = "Adds a solidify modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SOLIDIFY', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddArrayModifier(Operator):
    bl_idname = "rymodel.add_array_modifier"
    bl_label = "Add Array Modifier"
    bl_description = "Adds an array modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('ARRAY', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddMultiResModifier(Operator):
    bl_idname = "rymodel.add_multires_modifier"
    bl_label = "Add MultiRes Modifier"
    bl_description = "Adds a multi resolution modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('MULTIRES', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddSubdivisionModifier(Operator):
    bl_idname = "rymodel.add_subdivision_modifier"
    bl_label = "Add Subdivision Modifier"
    bl_description = "Adds a subdivision modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SUBSURF', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddShrinkWrapModifier(Operator):
    bl_idname = "rymodel.add_shrinkwrap_modifier"
    bl_label = "Add Shrinkwrap Modifier"
    bl_description = "Adds a shrinkwrap modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('SHRINKWRAP', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_AddTriangulateModifier(Operator):
    bl_idname = "rymodel.add_triangulate_modifier"
    bl_label = "Add Triangulate Modifier"
    bl_description = "Adds a triangulate modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_modifier('TRIANGULATE', self, context)
        property_range_overrides.update_property_range_overrides()
        return {'FINISHED'}

class RyModel_ApplyModifier(Operator):
    bl_idname = "rymodel.apply_modifier"
    bl_label = "Apply Modifier"
    bl_description = "Applies the modifier to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    modifier_name: StringProperty(default="")

    def execute(self, context):
        bpy.ops.object.modifier_apply(modifier=self.modifier_name, report=True)
        if self.modifier_name.startswith("BoolObj_"):
            booleans.remove_unused_booleans()
        
        property_range_overrides.update_mirror_properties()      # Update mirror properties in case a mirror modifier was applied.
        return {'FINISHED'}

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
        if not internal_utils.verify_active_mesh(self):
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

        booleans.remove_unused_booleans()

        return {'FINISHED'}

class RyModel_CopyModifiers(Operator):
    bl_idname = "rymodel.copy_modifiers"
    bl_label = "Copy Modifiers"
    bl_description = "Copies all modifiers from the selected object to the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
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
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}

        for modifier in context.active_object.modifiers:
            match modifier.type:
                case 'BEVEL':
                    continue
                case 'WEIGHTED_NORMAL':
                    continue
                case _:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

        modeling_tools.update_mirror_properties()
        booleans.remove_unused_booleans()
        
        return {'FINISHED'}

def update_circular_offset(self, context):
    if not internal_utils.verify_active_mesh():
        return

    displace_modifier = context.active_object.modifiers.get('CircularArrayDisplacement')
    if displace_modifier:
        displace_modifier.strength = context.scene.circular_array_settings.offset

def update_circular_count(self, context):
    if not internal_utils.verify_active_mesh():
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
        if not internal_utils.verify_active_mesh(self):
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
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        if not context.active_object.modifiers.get('2xSubDivision_1') and not context.active_object.modifiers.get('2xSubDivision_2'):
            subdivision_modifier_1 = context.active_object.modifiers.new('2xSubDivision_1', 'SUBSURF')
            subdivision_modifier_1.levels = 2
            subdivision_modifier_1.subdivision_type = 'SIMPLE'
            subdivision_modifier_2 = context.active_object.modifiers.new('2xSubDivision_2', 'SUBSURF')
            subdivision_modifier_2.levels = 2

        return {'FINISHED'}


#------------------------ CUSTOM MODIFIERS ------------------------#

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
        if not internal_utils.verify_active_mesh(self):
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
