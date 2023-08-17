import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty
import bmesh
from ..core import internal_utils
from ..core import modifiers
from ..core import rylog
import numpy as np
import math

def update_boolean_operation(self, context):
    '''Updates the boolean operation for all objects using the selected boolean.'''
    if not context.active_object:
        return
    
    if context.active_object.name.startswith("BoolObj_") and context.active_object.type == 'MESH':
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

                            # For other boolean operations, remove the solidify modifier from the boolean if it exists.
                            solidify_modifier = context.active_object.modifiers.get("SliceSolidify")
                            if solidify_modifier:
                                context.active_object.modifiers.remove(solidify_modifier)

def hide_booleans():
    '''Hides all booleans excluding the one being selected.'''
    if not internal_utils.verify_active_mesh():
        return
    
    for obj in bpy.data.objects:
        if obj.name.startswith("Boolean_"):
            if obj != bpy.context.active_object or obj.select_get() == False:
                obj.hide_viewport = True

def show_boolean_objects():
    if not internal_utils.verify_active_mesh():
        return

    for obj in bpy.data.objects:
        if obj.name.startswith("Boolean_"):
                obj.hide_viewport = False

def remove_unused_booleans():
    '''Removes all unused boolean objects and all boolean modifiers on all objects that have no object assigned.'''
    used_boolean_objects = []
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == 'BOOLEAN':
                if modifier.object == None:
                    obj.modifiers.remove(modifier)
                else:
                    used_boolean_objects.append(modifier.object)

    for obj in bpy.data.objects:
        if obj.name.startswith("Boolean_"):
            if obj not in used_boolean_objects:
                bpy.data.objects.remove(obj)

def add_boolean_mod(obj):
    '''Adds a boolean modifier to the provided object.'''
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # Add a boolean modifier with a unique name.
    boolean_count = 1
    boolean_mod_name = "Boolean_{0}".format(boolean_count)
    boolean_modifier = obj.modifiers.get(boolean_mod_name)
    while obj.modifiers.get(boolean_mod_name) != None:
        boolean_count += 1
        boolean_mod_name = "Boolean_{0}".format(boolean_count)
    boolean_modifier = obj.modifiers.new(boolean_mod_name, 'BOOLEAN')

    # Adjust boolean settings.
    boolean_modifier.solver = 'FAST'
    boolean_modifier.show_in_editmode = True
    boolean_modifier.show_expanded = False
    if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
        boolean_modifier.operation = 'DIFFERENCE'
    else:
        boolean_modifier.operation = bpy.context.scene.rymodel_boolean_mode

    # Organize the modifier stack since we just added a new modifier.
    modifiers.organize_modifier_stack(obj.modifiers)

    return boolean_modifier

def add_boolean_mods_to_selected():
    '''Adds a boolean modifier to all selected objects.'''
    boolean_modifiers = []
    for obj in bpy.context.selected_objects:
        boolean_modifier = add_boolean_mod(obj)
        boolean_modifiers.append(boolean_modifier)
    return boolean_modifiers

def get_new_boolean_name():
    '''Returns a unique, indexed name for a new boolean object.'''
    boolean_number = 1
    new_boolean_name = "Boolean_{0}".format(boolean_number)
    boolean = bpy.data.objects.get(new_boolean_name)
    while boolean != None:
        boolean_number += 1
        new_boolean_name = "Boolean_{0}".format(boolean_number)
        boolean = bpy.data.objects.get(new_boolean_name)
    return new_boolean_name

def create_new_boolean_shape(shape):
    '''Create a new boolean object from the provided shape.'''
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)        # Must be ran in object mode.

    new_boolean_name = get_new_boolean_name()

    match shape:
        case 'PLANE':
            bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(1, 1, 1))

        case 'CUBE':
            bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(0.5, 0.5, 0.5))

        case 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(1, 1, 1))

        case 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        case 'CONE':
            bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        case _:
            rylog.log("Error: Invalid shape value provided to the add boolean operator.")

    new_boolean_object = bpy.context.active_object                                  # The active object is the new boolean object.
    new_boolean_object.name = new_boolean_name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)       # Ensure scale is applied by default.
    return new_boolean_object

def setup_new_boolean(new_boolean_object, active_object, boolean_modifiers, set_location=True):
    '''Adjust boolean settings, and sets location so a newly created boolean object is setup in an ideal fashion for adjustment.'''

    # Add the boolean object to the boolean modifier and apply boolean settings.
    for boolean_modifier in boolean_modifiers:
        boolean_modifier.object = new_boolean_object
    internal_utils.select_only(new_boolean_object)
    mesh = new_boolean_object.data
    for f in mesh.polygons:
        f.use_smooth = True
    mesh.use_auto_smooth = True
    mesh.auto_smooth_angle = 1.0472
    new_boolean_object.display_type = 'WIRE'
    new_boolean_object.hide_render = True

    # For booleans using slice, add a solidify modifier.
    if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
        solidify_modifier = new_boolean_object.modifiers.new("SliceSolidify", 'SOLIDIFY')
        solidify_modifier.use_even_offset = True
        solidify_modifier.thickness = 0.075

    # Move the new boolean to the center of the active object (while also accounting for mirror modifiers).
    if set_location:
        new_boolean_object.location = internal_utils.get_object_true_center(active_object)

    # Parent the boolean to the active object so the booleans will move with the object they are assigned to.
    if new_boolean_object.parent != active_object:
        new_boolean_object.parent = active_object
        new_boolean_object.matrix_parent_inverse = active_object.matrix_world.inverted()

    # All new booleans should go in their own scene collection.
    internal_utils.add_object_to_collection('Booleans', new_boolean_object, color_tag='COLOR_01', unlink_from_other_collections=True)

def optimize_new_boolean_dimensions(shape, new_boolean_object, original_object_dimensions):
    '''Attempts to create new boolean objects with optimal dimensions so booleans cut through all the way through objects by default.'''
    match shape:
        case 'PLANE':
            new_boolean_object.dimensions = np.array(original_object_dimensions) * 1.25

        case 'CUBE':
            new_boolean_object.dimensions = np.array(original_object_dimensions) * 1.25

        case _:
            if shape != 'SELECTED_OBJECT':
                largest_dimension = original_object_dimensions[0]
                for i in range(1, len(original_object_dimensions)):
                    if original_object_dimensions[i] > largest_dimension:
                        largest_dimension = original_object_dimensions[i]
                new_boolean_object.dimensions = (largest_dimension, largest_dimension, largest_dimension)

def rotate_plane_boolean_to_view(plane_boolean):
    '''Rotates the provided plane boolean to match the obj rotation of the viewport.'''
    # Assumes that there is only 1 3D view.
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            r3d = area.spaces.active.region_3d
            view_matrix = r3d.view_matrix
            r = lambda x: round(x, 2)
            view_rot = view_matrix.to_euler()
            orientation_dict = {(0.0, 0.0, 0.0) : 'TOP',
                                (r(math.pi), 0.0, 0.0) : 'BOTTOM',
                                (r(-math.pi/2), 0.0, 0.0) : 'FRONT',
                                (r(math.pi/2), 0.0, r(-math.pi)) : 'BACK',
                                (r(-math.pi/2), r(math.pi/2), 0.0) : 'LEFT',
                                (r(-math.pi/2), r(-math.pi/2), 0.0) : 'RIGHT'}
            orientation = orientation_dict.get(tuple(map(r, view_rot)), 'USER')

            match orientation:
                case 'TOP':
                    plane_boolean.rotation_euler[0] = math.radians(-90)
                case 'BOTTOM':
                    plane_boolean.rotation_euler[0] = math.radians(90)
                case 'LEFT':
                    plane_boolean.rotation_euler[2] = math.radians(-90)
                case 'RIGHT':
                    plane_boolean.rotation_euler[2] = math.radians(90)
                case 'BACK':
                    plane_boolean.rotation_euler[2] = math.radians(180)
            break

def setup_plane_boolean(new_boolean_object):
    '''Applies settings and adjusts modes the be optimal for adjusting a plane boolean.'''
    # Rotate the new boolean object to match the viewport rotation.
    rotate_plane_boolean_to_view(new_boolean_object)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # Select two vertices so users can instantly start extruding them to make a custom shape.
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')       # Finishing in vertex mode allows users to quickly grab vertices to re-adjust for the new boolean.

    me = new_boolean_object.data
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        f.select = False

    for edge in bm.edges:
        edge.select = False
    bm.edges.ensure_lookup_table()
    bm.edges[2].select = True

    for v in bm.verts:
        v.select = False
    bm.verts.ensure_lookup_table()
    bm.verts[1].select = True
    bm.verts[3].select = True

    # Finish in xray mode so users can quickly grab vertices through the mesh.
    bpy.context.space_data.shading.show_xray = True
    bpy.context.scene.tool_settings.snap_elements = {'VERTEX'}

def add_new_boolean_shape(self, shape):
    '''Creates and sets up a new boolean object of the provided shape.'''
    remove_unused_booleans()

    # Don't run if the active object isn't a mesh.
    if not internal_utils.verify_active_mesh(self):
        return {'FINISHED'}
    
    # Must be in object mode to add booleans.
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    
    # Apply scale before adding a new boolean object (otherwise booleans will be created with incorrect sizes).
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    active_object = bpy.context.active_object
    original_object_dimensions = [active_object.dimensions[0], active_object.dimensions[1], active_object.dimensions[2]]
    hide_booleans()
    boolean_modifiers = add_boolean_mods_to_selected()
    new_boolean_object = create_new_boolean_shape(shape)
    setup_new_boolean(new_boolean_object, active_object, boolean_modifiers)
    optimize_new_boolean_dimensions(shape, new_boolean_object, original_object_dimensions)

    # Plane booleans leave the user in edit mode, with a special setup to allow them to quickly extrude edges of the plane to cut through the object.
    if shape == 'PLANE':
        setup_plane_boolean(new_boolean_object)
    else:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

class RyModel_AddPlaneBoolean(Operator):
    bl_idname = "rymodel.add_plane_boolean"
    bl_label = "Add Plane Boolean"
    bl_description = "Adds a boolean modifier to the selected object with a plane mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_new_boolean_shape(self, 'PLANE')
        return {'FINISHED'}

class RyModel_AddCubeBoolean(Operator):
    bl_idname = "rymodel.add_cube_boolean"
    bl_label = "Add Cube Boolean"
    bl_description = "Adds a boolean modifier to the selected object with a cube mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_new_boolean_shape(self, 'CUBE')
        return {'FINISHED'}

class RyModel_AddCylinderBoolean(Operator):
    bl_idname = "rymodel.add_cylinder_boolean"
    bl_label = "Add Cylinder Boolean"
    bl_description = "Adds a boolean modifier to the selected object with a cylinder mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_new_boolean_shape(self, 'CYLINDER')
        return {'FINISHED'}

class RyModel_AddSphereBoolean(Operator):
    bl_idname = "rymodel.add_sphere_boolean"
    bl_label = "Add Sphere Boolean"
    bl_description = "Adds a boolean modifier to the selected object with a sphere mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_new_boolean_shape(self, 'SPHERE')
        return {'FINISHED'}

class RyModel_AddConeBoolean(Operator):
    bl_idname = "rymodel.add_cone_boolean"
    bl_label = "Add Cone Boolean"
    bl_description = "Adds a boolean modifier to the selected object with a cone mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        add_new_boolean_shape(self, 'CONE')
        return {'FINISHED'}

class RyModel_SelectedObjectToBoolean(Operator):
    bl_idname = "rymodel.selected_object_to_boolean"
    bl_label = "Selected Object to Boolean"
    bl_description = "Converts the selected object into a boolean object and applies a new boolean modifier to the active object. Select the object(s) you wish to boolean, then the boolean object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        remove_unused_booleans()

        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}

        new_boolean_object = bpy.context.active_object      # New boolean object is the active object.
        hide_booleans()

        # Only select 2 objects for this operator.
        if len(context.selected_objects) < 2:
            self.report({'ERROR'}, "Select all objects you wish to cut, then select the cutter you wish to use.")
            return {'FINISHED'}

        # Select the parent object, while ensuring it's not the active object.
        parent_object = context.selected_objects[0]
        if len(context.selected_objects) >= 2:
            if parent_object == context.active_object:
                parent_object = context.selected_objects[1]

        # If the selected object is already a boolean, add it to the boolean modifier.
        if new_boolean_object.name.startswith("Boolean_"):
            boolean_modifiers = []
            for obj in context.selected_objects:
                if obj != new_boolean_object:
                    new_bool_mod = add_boolean_mod(obj)
                    boolean_modifiers.append(new_bool_mod)
                    
            for boolean_modifier in boolean_modifiers:
                boolean_modifier.object = new_boolean_object
            return {'FINISHED'}

        # Convert the selected object into a boolean
        else:
            boolean_modifiers = []
            for obj in context.selected_objects:
                if obj != new_boolean_object:
                    new_bool_mod = add_boolean_mod(obj)
                    boolean_modifiers.append(new_bool_mod)

            new_boolean_object.name = get_new_boolean_name()
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            internal_utils.select_only(new_boolean_object)
            setup_new_boolean(new_boolean_object, parent_object, boolean_modifiers, set_location=False)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)    # Finish in object mode.
        return {'FINISHED'}

def make_booleans_unique(obj, new_parent=None):
    '''Duplicates all boolean objects for the provided object.'''
    show_boolean_objects()
    boolean_modifiers = modifiers.get_modifiers_of_type(obj.modifiers, 'BOOLEAN')
    for boolean_modifier in boolean_modifiers:
        boolean_obj = boolean_modifier.object
        if boolean_obj:
            # Only duplicate the object if it's used elsewhere.
            used_elsewhere = False
            for o in bpy.data.objects:
                if o != obj:
                    bmods = modifiers.get_modifiers_of_type(o.modifiers, 'BOOLEAN')
                    for mod in bmods:
                        if mod.object == boolean_obj:
                            used_elsewhere = True

            if used_elsewhere:
                duplicated_boolean_obj = internal_utils.duplicate_object(boolean_obj)
                duplicated_boolean_obj.name = get_new_boolean_name()
                boolean_modifier.object = duplicated_boolean_obj
                boolean_modifier.name = duplicated_boolean_obj.name
                internal_utils.add_object_to_collection('Booleans', duplicated_boolean_obj, unlink_from_other_collections=True)

                # Parent the boolean to a new object if one is provided.
                if new_parent:
                    duplicated_boolean_obj.parent = new_parent
                    duplicated_boolean_obj.matrix_parent_inverse = new_parent.matrix_world.inverted()

class RyModel_MakeBooleansUnique(Operator):
    bl_idname = "rymodel.make_booleans_unique"
    bl_label = "Make Booleans Unique"
    bl_description = "Makes duplicate versions of boolean objects for the selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_object = context.active_object
        make_booleans_unique(active_object, new_parent=active_object)
        return {'FINISHED'}

class RyModel_MakeBackupObject(Operator):
    bl_idname = "rymodel.make_backup_object"
    bl_label = "Make Backup Object"
    bl_description = "Duplicate all selected objects and stores them in a backup collection, then makes copies of all boolean objects used on those objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            backup_obj = internal_utils.duplicate_object(obj)
            backup_obj.name = "Backup_" + obj.name
            collection = internal_utils.add_object_to_collection('Backups', backup_obj, 'COLOR_05', unlink_from_other_collections=True)

            # Exclude the collection from the viewlayer.
            for vl in context.scene.view_layers:
                for lc in vl.layer_collection.children:
                    if lc.name == collection.name:
                        lc.exclude = True

            # If the backup object is a mesh, also backup any applied boolean objects.
            if backup_obj.type == 'MESH':
                make_booleans_unique(backup_obj, new_parent=backup_obj)
        return {'FINISHED'}

class RyModel_SelectBoolObject(Operator):
    bl_idname = "rymodel.select_boolean"
    bl_label = "Select Boolean"
    bl_description = "Selects the specified boolean"
    bl_options = {'REGISTER', 'UNDO'}

    boolean_modifier_name: StringProperty(name="")

    def execute(self, context):
        if not internal_utils.verify_active_mesh():
            return
    
        original_mode = bpy.context.mode
        active_object = bpy.context.active_object
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        boolean_modifier = active_object.modifiers.get(self.boolean_modifier_name)
        if boolean_modifier:
            boolean_object = boolean_modifier.object
            if boolean_object:
                show_boolean_objects()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = boolean_object
                boolean_object.select_set(True)
                hide_booleans()

        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        else:
            bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}

class RyModel_ShowBooleanObjects(Operator):
    bl_idname = "rymodel.show_boolean_objects"
    bl_label = "Makes all boolean objects visible in the viewport"
    bl_description = "Show Boolean Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        show_boolean_objects()
        return {'FINISHED'}


