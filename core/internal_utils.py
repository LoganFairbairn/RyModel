# This module contains misc utility functions (used for in-code use only, as opposed to utility operators available in the add-on user interface) for this add-on.

import bpy
import mathutils
from ..core import modifiers
from ..core import rylog

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

def get_object_true_center(obj):
    '''Returns the center point of the object accounting for applied mirror modifiers.'''

    # Get the center of the object based on the average of vertices.
    x, y, z = [ sum( [v.co[i] for v in obj.data.vertices] ) for i in range(3)]
    count = float(len(obj.data.vertices))
    center = obj.matrix_world @ (mathutils.Vector( (x, y, z ) ) / count)

    # Center axis values for mirror modifiers
    mirror_modifier = modifiers.get_modifier_of_type(obj.modifiers, 'MIRROR')
    if mirror_modifier:
        if mirror_modifier.use_axis[0]:
            center[0] = 0
        if mirror_modifier.use_axis[1]:
            center[1] = 0
        if mirror_modifier.use_axis[2]:
            center[2] = 0
    return center

def select_only(obj):
    '''Ensures only the provided object is selected.'''
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    bpy.ops.object.select_all(action='DESELECT')

    if bpy.context.view_layer.objects.get(obj.name):
        bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

def duplicate_object(obj):
    '''Duplicates the provided object.'''
    copy = obj.copy()
    mesh_copy = copy.data.copy()
    copy.data = mesh_copy
    return copy

def add_object_to_collection(collection_name, obj, color_tag='COLOR_01', unlink_from_other_collections=False):
    '''Adds the provided object to a scene collection. Creates a new collection if one doesn't exist.'''

    # Create the collection if it does not exist.
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        collection = bpy.data.collections.new(collection_name)
        collection.color_tag = color_tag
        bpy.context.scene.collection.children.link(collection)

    # Unlink the object from all other collections.
    if unlink_from_other_collections:
        for c in bpy.data.collections:
            if c.objects.get(obj.name):
                c.objects.unlink(obj)

    # Add the object to the collection.
    collection.objects.link(obj)

    return collection
