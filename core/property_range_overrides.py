# The vanilla slider ranges in Blender are in some cases way too large, making ui sliders unusable, these properties override modifier properties to provide better slider ranges.

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, FloatProperty
from ..core import modifiers

def update_property_range_overrides():
    '''Updates all property range overrides - call when a new object is selected.'''
    active_object = bpy.context.active_object
    if active_object:
        # Update circular twist count.
        circular_twist_array_mod = active_object.modifiers.get('CircularTwistArray')
        if circular_twist_array_mod:
            bpy.context.scene.circular_twist_count = circular_twist_array_mod.count

        # Update property range overrides.
        bevel_modifier = modifiers.get_modifier_of_type(active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bpy.context.scene.bevel_modifier_settings.segments = bevel_modifier.segments
            bpy.context.scene.bevel_modifier_settings.width = bevel_modifier.width

        solidify_modifier = modifiers.get_modifier_of_type(active_object.modifiers, 'SOLIDIFY')
        if solidify_modifier:
            bpy.context.scene.solidify_modifier_settings.thickness = solidify_modifier.thickness

        array_modifier = modifiers.get_modifier_of_type(active_object.modifiers, 'ARRAY')
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
        bevel_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bevel_modifier.segments = context.scene.bevel_modifier_settings.segments

def update_bevel_modifier_width(self, context):
    if context.active_object:
        bevel_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'BEVEL')
        if bevel_modifier:
            bevel_modifier.width = context.scene.bevel_modifier_settings.width

class BevelModifierSettings(PropertyGroup):
    segments: IntProperty(name="Segments", default=6, min=0, soft_max=10, update=update_bevel_modifier_segments)
    width: FloatProperty(name="Width", default=1, min=0, soft_max=1, update=update_bevel_modifier_width)

def update_solidify_thickness(self, context):
    if context.active_object:
        solidify_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'SOLIDIFY')
        solidify_modifier.thickness = context.scene.solidify_modifier_settings.thickness

class SolidifyModifierSettings(PropertyGroup):
    thickness: FloatProperty(name="Thickness", default=1.0, min=-2.0, soft_max=2.0, update=update_solidify_thickness)

def update_array_modifier_count(self, context):
    if context.active_object:
        array_modifier = modifiers.get_modifier_of_type(context.active_object.modifiers, 'ARRAY')
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