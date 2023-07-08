import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import EnumProperty
from ..core import internal_utils

FRAME_END = 50

VERTEX_DENSITY = [
    ("LOW", "Low", ""),
    ("MEDIUM", "Medium", ""),
    ("HIGH", "High", ""),
]

class ClothSimSettings(PropertyGroup):
    vertex_density: EnumProperty(items=VERTEX_DENSITY, name="Segments", default='MEDIUM')

class RyModel_ApplyCollision(Operator):
    bl_idname = "rymodel.apply_collision"
    bl_label = "Apply Collision"
    bl_description = "Applies collision with generally better settings to the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        # Apply the cloth modifier and adjust settings.
        active_object = context.active_object
        collision_modifier = active_object.modifiers.new('RyCollision', "COLLISION")
        collision_modifier.thickness_outer = 0.001

        return {'FINISHED'}


class RyModel_SimulateCloth(Operator):
    bl_idname = "rymodel.simulate_cloth"
    bl_label = "Simulate Cloth"
    bl_description = "Adds a cloth simulation modifier to the selected object with settings ideal for cloth simulation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        # Reset the timeline head so the object doesn't dissapear offscreen due to incorrect simulation buffer data.
        context.scene.frame_current = 0
        context.scene.frame_start = 1
        context.scene.frame_end = FRAME_END
        
        # Apply the cloth modifier and adjust settings.
        active_object = context.active_object
        if not active_object.modifiers.get("RyCloth"):
            cloth_modifier = active_object.modifiers.new("RyCloth", "CLOTH")
            cloth_modifier.settings.quality = 10
            cloth_modifier.settings.use_sewing_springs = True
            cloth_modifier.settings.shrink_min = -0.2
            cloth_modifier.collision_settings.use_self_collision = True
            cloth_modifier.collision_settings.collision_quality = 15
            cloth_modifier.collision_settings.self_distance_min = 0.002
            cloth_modifier.collision_settings.distance_min = 0.001
            cloth_modifier.point_cache.frame_end = FRAME_END

        # Run the simulation by playing the timeline.
        bpy.ops.screen.animation_play()

        return {'FINISHED'}

def pin_cloth(weight):
    original_mode = bpy.context.mode
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    active_object = bpy.context.active_object

    pinned_vertices = active_object.vertex_groups.get("Pinned")
    if not pinned_vertices:
        pinned_vertices = active_object.vertex_groups.new(name="Pinned")

    # Add the vertex group to the pinned group in the cloth modifier.
    cloth_modifier = active_object.modifiers.get('RyCloth')
    if cloth_modifier.settings.vertex_group_mass != 'Pinned':
        cloth_modifier.settings.vertex_group_mass = 'Pinned'

    # Add selected vertices to the pinned vertex group.
    selected_vertices = list(filter(lambda v: v.select, active_object.data.vertices))
    selected_vertex_indicies = [0] * len(selected_vertices)
    for i,v in enumerate(selected_vertices):
        selected_vertex_indicies[i] = v.index
    pinned_vertices.add(selected_vertex_indicies, weight, type='REPLACE')

    internal_utils.set_object_interaction_mode(original_mode)

class RyModel_PinCloth(Operator):
    bl_idname = "rymodel.pin_cloth"
    bl_label = "Pin Cloth"
    bl_description = "Pins selected vertices so they are not effected by the cloth simulation (creates a vertex group for them if one does not already exist)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        pin_cloth(weight=1.0)

        return {'FINISHED'}
    
class RyModel_UnPinCloth(Operator):
    bl_idname = "rymodel.unpin_cloth"
    bl_label = "Unpin Cloth"
    bl_description = "Unpins selected vertices so they are effected by the cloth simulation (creates a vertex group for them if one does not already exist)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not internal_utils.verify_active_mesh(self):
            return {'FINISHED'}
        
        pin_cloth(weight=0.0)

        return {'FINISHED'}
    
class ClothSimMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_cloth_sim_menu"
    bl_label = "Cloth Sim Menu"

    def draw(self, context):
        layout = self.layout

        cloth_sim_settings = context.scene.rymodel_cloth_sim_settings
        layout.props_enum(cloth_sim_settings, "vertex_density")