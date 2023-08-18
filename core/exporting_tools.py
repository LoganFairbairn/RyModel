import bpy
from bpy.types import Operator
import os
from .. import preferences
from ..core import modifiers
from ..core import internal_utils
from ..core import rylog


def export_by_template(template_name, export_path, self):
    '''Exports the provided object using settings defined for the provided template name'''
    match template_name:
        case 'FBX':
            export_filepath = export_path + ".fbx"
            bpy.ops.export_scene.fbx(
                filepath=export_filepath,
                check_existing=False, 
                filter_glob='*.fbx', 
                use_selection=True, 
                use_visible=False, 
                use_active_collection=False,
                global_scale=1.0, 
                apply_unit_scale=True, 
                apply_scale_options='FBX_SCALE_NONE', 
                use_space_transform=True, 
                bake_space_transform=False, 
                object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, 
                use_mesh_modifiers=True, 
                use_mesh_modifiers_render=True, 
                mesh_smooth_type='OFF',
                colors_type='SRGB', 
                prioritize_active_color=False, 
                use_subsurf=False, 
                use_mesh_edges=False, 
                use_tspace=False, 
                use_triangles=False, 
                use_custom_props=False, 
                add_leaf_bones=True, 
                primary_bone_axis='Y', 
                secondary_bone_axis='X', 
                use_armature_deform_only=False, 
                armature_nodetype='NULL', 
                bake_anim=True, 
                bake_anim_use_all_bones=True, 
                bake_anim_use_nla_strips=True, 
                bake_anim_use_all_actions=True, 
                bake_anim_force_startend_keying=True, 
                bake_anim_step=1.0, bake_anim_simplify_factor=1.0, 
                path_mode='AUTO', 
                embed_textures=False,
                batch_mode='OFF', 
                use_batch_own_dir=True, 
                use_metadata=True, 
                axis_forward='-Z',
                axis_up='Y'
            )

        case 'OBJ':
            export_filepath = export_path + ".obj"
            bpy.ops.export_scene.obj(
                filepath=export_filepath, 
                check_existing=False, 
                filter_glob='*.obj;*.mtl', 
                use_selection=False, 
                use_animation=False, 
                use_mesh_modifiers=True, 
                use_edges=True, 
                use_smooth_groups=False, 
                use_smooth_groups_bitflags=False, 
                use_normals=True, use_uvs=True, 
                use_materials=True, use_triangles=False, 
                use_nurbs=False, 
                use_vertex_groups=False,
                use_blen_objects=True, 
                group_by_object=False, 
                group_by_material=False, 
                keep_vertex_order=False, 
                global_scale=1.0, 
                path_mode='AUTO', 
                axis_forward='-Z', 
                axis_up='Y'
            )

        case 'UNITY_FBX':
            export_filepath = export_path + ".fbx"
            bpy.ops.export_scene.fbx(
                filepath=export_filepath, 
                check_existing=False, 
                filter_glob='*.fbx', 
                use_selection=True, 
                use_visible=False, 
                use_active_collection=False, 
                global_scale=1.0, 
                apply_unit_scale=True, 
                apply_scale_options='FBX_SCALE_NONE', 
                use_space_transform=True, 
                bake_space_transform=False, 
                object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'}, 
                use_mesh_modifiers=True, 
                use_mesh_modifiers_render=True, 
                mesh_smooth_type='FACE', 
                colors_type='SRGB', 
                prioritize_active_color=False, 
                use_subsurf=False, 
                use_mesh_edges=False, 
                use_tspace=False, 
                use_triangles=False, 
                use_custom_props=False, 
                add_leaf_bones=True, 
                primary_bone_axis='Y', 
                secondary_bone_axis='X', 
                use_armature_deform_only=False, 
                armature_nodetype='NULL', 
                bake_anim=True, 
                bake_anim_use_all_bones=True, 
                bake_anim_use_nla_strips=True, 
                bake_anim_use_all_actions=True, 
                bake_anim_force_startend_keying=True, 
                bake_anim_step=1.0, bake_anim_simplify_factor=1.0, 
                path_mode='AUTO', 
                embed_textures=False, 
                batch_mode='OFF', 
                use_batch_own_dir=True, 
                use_metadata=True, 
                axis_forward='X',
                axis_up='Y'
            )

    rylog.log_status("Exported selected objects to: {0}".format(export_filepath), self, 'INFO')


class RyModel_Export(Operator):
    bl_idname = "rymodel.export"
    bl_label = "Export"
    bl_description = "Automatically exports selected objects to a path next to the open blend file. This operator requries the blend file to be saved"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Export based on the selected export template.
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        active_object = bpy.context.active_object
        if not active_object:
            rylog.log_status("No active object to export.", self, 'ERROR')
            return {'FINISHED'}

        open_blend_path = bpy.data.filepath
        if open_blend_path == "":
            rylog.log_status("The blend file must be saved to export models relative to the blend files path.", self, 'ERROR')
            return {'FINISHED'}
        directory = os.path.dirname(open_blend_path)

        # Apply a triangulate modifier to the object being exported, if one does not exist already.
        for obj in selected_objects:
            modifiers.get_modifier_of_type(obj.modifiers, '')

        # Export all selected objects as individual files (use the name of each object as the filename).
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        if addon_preferences.export_selected_objects_individually:
            selected_objects = bpy.context.selected_objects
            
            # Select 1 object at a time for export as individual files.
            for obj in selected_objects:
                internal_utils.select_only(obj)
                export_path = os.path.join(directory, obj.name)
                export_by_template(addon_preferences.export_template, export_path, self)
            
        # Export all selected objects as a single file (use the name of the active object as the filename).
        else:
            export_path = os.path.join(directory, active_object.name)
            export_by_template(addon_preferences.export_template, export_path, self)

        return {'FINISHED'}