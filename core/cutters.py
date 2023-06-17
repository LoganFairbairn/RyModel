import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty
import bmesh
from ..core import internal_utils
from ..core import modifiers
from ..core import rylog
import math
import mathutils

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
    if not internal_utils.verify_active_mesh():
        return
    
    for obj in bpy.data.objects:
        if obj.name.startswith("Cutter_"):
            if obj != bpy.context.active_object or obj.select_get() == False:
                obj.hide_viewport = True

def show_cutters():
    if not internal_utils.verify_active_mesh():
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

def create_cutter_collection():
    '''Creates a new collection for cutter objects.'''
    cutter_collection = bpy.data.collections.get("Cutters")
    if not cutter_collection:
        cutter_collection = bpy.data.collections.new("Cutters")
        cutter_collection.color_tag = 'COLOR_01'
        bpy.context.scene.collection.children.link(cutter_collection)
    return cutter_collection

def add_cutter_boolean(obj):
    '''Adds a boolean modifier to setup for a cutter object.'''
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # Add a boolean modifier with a unique name.
    boolean_count = 1
    boolean_mod_name = "Cutter_{0}".format(boolean_count)
    boolean_modifier = obj.modifiers.get(boolean_mod_name)
    while obj.modifiers.get(boolean_mod_name) != None:
        boolean_count += 1
        boolean_mod_name = "Cutter_{0}".format(boolean_count)
    boolean_modifier = obj.modifiers.new(boolean_mod_name, 'BOOLEAN')

    # Adjust booolean settings.
    boolean_modifier.solver = 'FAST'
    boolean_modifier.show_in_editmode = True
    if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
        boolean_modifier.operation = 'DIFFERENCE'
    else:
        boolean_modifier.operation = bpy.context.scene.rymodel_boolean_mode

    boolean_modifier.show_expanded = False

    # Organize the modifier stack since we just added a new modifier.
    modifiers.organize_modifier_stack(obj.modifiers)

    return boolean_modifier

def get_new_cutter_name():
    '''Returns a name for a new cutter object.'''
    cutter_number = 1
    new_cutter_name = "Cutter_{0}".format(cutter_number)
    cutter = bpy.data.objects.get(new_cutter_name)
    while cutter != None:
        cutter_number += 1
        new_cutter_name = "Cutter_{0}".format(cutter_number)
        cutter = bpy.data.objects.get(new_cutter_name)
    return new_cutter_name

def rotate_plane_cutter_to_view(plane_cutter):
    '''Rotates the provided plane cutter to match the obj rotation of the viewport.'''
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
                    plane_cutter.rotation_euler[0] = math.radians(-90)
                case 'BOTTOM':
                    plane_cutter.rotation_euler[0] = math.radians(90)
                case 'LEFT':
                    plane_cutter.rotation_euler[2] = math.radians(-90)
                case 'RIGHT':
                    plane_cutter.rotation_euler[2] = math.radians(90)
                case 'BACK':
                    plane_cutter.rotation_euler[2] = math.radians(180)
            break

class RyModel_AddCutter(Operator):
    bl_idname = "rymodel.add_cutter"
    bl_label = "Add Cutter"
    bl_description = "Adds a boolean modifier to the selected object. Toggles to edit mode. Toggles vertex snapping on. Toggles xray mode on"
    bl_options = {'REGISTER', 'UNDO'}

    shape: StringProperty(default='CUBE')

    def execute(self, context):
        # Remove all unused cutters automatically.
        remove_unused_cutters()

        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        if context.active_object.name.startswith("Cutter_"):
            self.report({'INFO'}, "Can't add a cutter to a cutter object.")
            return {'FINISHED'}

        if self.shape == 'SELECTED_OBJECT':
            if len(bpy.context.selected_objects) != 2:
                self.report({'ERROR'}, "Select only the object you wish to use as a cutter and the object you wish to cut.")
                return {'FINISHED'}
            
        active_object = bpy.context.active_object

        if self.shape == 'SELECTED_OBJECT':
            new_cutter_object = context.selected_objects[0]
            if len(context.selected_objects) >= 2:
                if new_cutter_object == context.active_object:
                    new_cutter_object = context.selected_objects[1]

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        hide_cutters()                                          # Hide all existing cutters so the user can focus on the one they are adding.
        cutter_collection = create_cutter_collection()          # Create a new cutter collection if one does not exist.
        boolean_modifier = add_cutter_boolean(active_object)    # Add a new boolean modifier to the selected object.
        new_cutter_name = get_new_cutter_name()                 # Get a unique name for the new cutter.

        # Make the selected object into a cutter.
        if self.shape == 'SELECTED_OBJECT':

            # If the selected object is already a cutter, just add the cutter to the boolean modifier.
            if new_cutter_object.name.startswith("Cutter_"):
                boolean_modifier.object = new_cutter_object
                return {'FINISHED'}
            new_cutter_object.name = new_cutter_name

        # Create a new cutter mesh with a unique name based on the provided cutter type.
        else:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            match self.shape:
                case 'PLANE':
                    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(1, 1, 1))

                case 'CUBE':
                    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(1, 1, 1))

                case 'CYLINDER':
                    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), scale=(1, 1, 1))

                case 'SPHERE':
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

                case 'CONE':
                    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

                case _:
                    rylog.log("Error: Incorrect shape value provided to the add cutter operator.")

            new_cutter_object = bpy.context.active_object       # The active object is the new cutter object.
            new_cutter_object.name = new_cutter_name

        # Add the object into the only the cutter collection.
        for collection in bpy.data.collections:
            if collection.objects.get(new_cutter_object.name):
                collection.objects.unlink(new_cutter_object)
        cutter_collection.objects.link(new_cutter_object)

        # Ensure only the new cutter object is selected.
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = new_cutter_object
        new_cutter_object.select_set(True)

        # Parent the cutter to the object so the cutters will move with the object they are assigned to.
        if new_cutter_object.parent != active_object:
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        # Set the dimensions of the new cutter to be slightly larger than the dimensions of the selected object.
        match self.shape:
            case 'PLANE':
                new_cutter_object.dimensions = active_object.dimensions * 1.25

            case 'CUBE':
                new_cutter_object.dimensions = active_object.dimensions * 1.25

            case _:
                if self.shape != 'SELECTED_OBJECT':
                    largest_dimension = active_object.dimensions[0]
                    for i in range(1, len(active_object.dimensions)):
                        if active_object.dimensions[i] > largest_dimension:
                            largest_dimension = active_object.dimensions[i]

                    new_cutter_object.dimensions = (largest_dimension, largest_dimension, largest_dimension)

        # Shade smooth.
        bpy.ops.object.shade_smooth(use_auto_smooth=False, auto_smooth_angle=1.0472)

        boolean_modifier.object = new_cutter_object         # Add the cutter object to the boolean modifier.
        new_cutter_object.display_type = 'WIRE'             # Display the cutter in wireframe.
        new_cutter_object.hide_render = True                # Ensure the cutters won't show up in renders.

        # For cutters using slice, add a solidify modifier.
        if bpy.context.scene.rymodel_boolean_mode == 'SLICE':
            solidify_modifier = new_cutter_object.modifiers.new("SliceSolidify", 'SOLIDIFY')
            solidify_modifier.use_even_offset = True
            solidify_modifier.thickness = 0.075

        # Move the new cutter to the center of the selected object, while also accounting for mirror modifiers.
        if self.shape != 'SELECTED_OBJECT':
            new_cutter_object.location = internal_utils.get_object_true_center(active_object)

        # Rotate the new cutter object to match the viewport rotation.
        if self.shape == 'PLANE':
            rotate_plane_cutter_to_view(new_cutter_object)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # For plane cutters, select two vertices so users can instantly start extruding the plane to make a custom shape.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')       # Finishing in vertex mode allows users to quickly grab vertices to re-adjust for the new cutter.
        if self.shape == 'PLANE':
            me = new_cutter_object.data
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
        #bpy.context.space_data.shading.show_xray = True
        bpy.context.scene.tool_settings.snap_elements = {'VERTEX'}

        # Always finish add cutter in edit mode...

        return {'FINISHED'}

class RyModel_SelectCutter(Operator):
    bl_idname = "rymodel.select_cutter"
    bl_label = "Select Cutter"
    bl_description = "Selects the specified cutter"
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
            cutter_object = boolean_modifier.object
            if cutter_object:
                show_cutters()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = cutter_object
                cutter_object.select_set(True)
                hide_cutters()

        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        else:
            bpy.ops.object.mode_set(mode=original_mode, toggle=False)
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
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        return {'FINISHED'}

class RyModel_Unwrap(Operator):
    bl_idname = "rymodel.unwrap"
    bl_label = "Unwrap"
    bl_description = "Unwraps and packs the selected model using the best unwrapping method available amongst all packing / unwrapping add-ons you have installed in Blender, defaults to vanilla unwrapping and packing if you have no packing / unwrapping add-ons"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
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
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        original_mode = bpy.context.mode
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.object.mode_set(mode=original_mode, toggle=False)
        return {'FINISHED'}

