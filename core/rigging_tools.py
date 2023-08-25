import bpy
from bpy.types import Operator
from ..core import rylog

class RyModel_PrepareRigifyForVRChat(Operator):
    bl_idname = "rymodel.prepare_rigify_for_vrchat"
    bl_label = "Rigify To VRChat"
    bl_description = "Converts a standard Rigify rig (already generated) to be imported into Unity as a humanoid model and is compatible with VRChat. This is done by automatically removing, and re-parenting bones so they rig matches the Unity humanoid skeleton. Bone constraints are also applied to shoulder bones so their control bones work in Blender"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rigify_rig_object = bpy.context.active_object
        rig = rigify_rig_object.data

        # Check that the selected rig is a rigify rig (we'll check by looking for an existing 'MCH-WGT-chest' bone).
        if not rigify_rig_object.pose.bones.get('MCH-WGT-chest'):
            rylog.log_status("The selected rig is not a standard Rigify rig. This operator should only be used on standard un-edited Rigify rigs.", self)
            return {'FINISHED'}
        
        # Check that the number of bones is greater than the number of bones after a standard Rigify rig is converted to be compatible with Unity / VRChat.
        if len(rigify_rig_object.pose.bones) <= 394:
            rylog.log_status("The selected rig is not a standard Rigify rig, or has already been converted to a Unity / VRChat compatible rig.", self)
            return {'FINISHED'}

        # Breast and pelvis bones aren't part of the Unity humanoid skeleton, make sure they are not marked as deform bones. They can still be imported and used as dynamic bones in Unity.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        set_non_deform_bones = ['DEF-breast.L', 'DEF-breast.R', 'DEF-pelvis.L', 'DEF-pelvis.R']
        for bone_name in set_non_deform_bones:
            bone = rig.bones.get(bone_name)
            if bone:
                bone.use_deform = False

        # Adjust the parent and tail of select bones.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        rig.edit_bones['DEF-thigh.L'].parent = rig.edit_bones['DEF-spine']
        rig.edit_bones['DEF-thigh.R'].parent = rig.edit_bones['DEF-spine']
        rig.edit_bones['DEF-upper_arm.L'].parent = rig.edit_bones['DEF-shoulder.L']
        rig.edit_bones['DEF-upper_arm.R'].parent = rig.edit_bones['DEF-shoulder.R']
        rig.edit_bones['DEF-upper_arm.L'].tail = rig.edit_bones['DEF-upper_arm.L.001'].tail
        rig.edit_bones['DEF-forearm.L'].tail = rig.edit_bones['DEF-forearm.L.001'].tail
        rig.edit_bones['DEF-forearm.L'].parent = rig.edit_bones['DEF-upper_arm.L.001'].parent
        rig.edit_bones['DEF-hand.L'].parent = rig.edit_bones['DEF-forearm.L.001'].parent
        rig.edit_bones['DEF-upper_arm.R'].tail = rig.edit_bones['DEF-upper_arm.R.001'].tail
        rig.edit_bones['DEF-forearm.R'].tail = rig.edit_bones['DEF-forearm.R.001'].tail
        rig.edit_bones['DEF-forearm.R'].parent = rig.edit_bones['DEF-upper_arm.R.001'].parent
        rig.edit_bones['DEF-hand.R'].parent = rig.edit_bones['DEF-forearm.R.001'].parent
        rig.edit_bones['DEF-thigh.L'].tail = rig.edit_bones['DEF-thigh.L.001'].tail
        rig.edit_bones['DEF-shin.L'].tail = rig.edit_bones['DEF-shin.L.001'].tail
        rig.edit_bones['DEF-shin.L'].parent = rig.edit_bones['DEF-thigh.L.001'].parent
        rig.edit_bones['DEF-foot.L'].parent = rig.edit_bones['DEF-shin.L.001'].parent
        rig.edit_bones['DEF-thigh.R'].tail = rig.edit_bones['DEF-thigh.R.001'].tail
        rig.edit_bones['DEF-shin.R'].tail = rig.edit_bones['DEF-shin.R.001'].tail
        rig.edit_bones['DEF-shin.R'].parent = rig.edit_bones['DEF-thigh.R.001'].parent
        rig.edit_bones['DEF-foot.R'].parent = rig.edit_bones['DEF-shin.R.001'].parent
        rig.edit_bones['DEF-shoulder.L'].parent = rig.edit_bones['DEF-spine.003']
        rig.edit_bones['DEF-shoulder.R'].parent = rig.edit_bones['DEF-spine.003']

        # Remove select bones from the Rigify rig if they exist.
        remove_bones = ['DEF-pelvis.L', 'DEF-pelvis.R', 'DEF-breast.L', 'DEF-breast.R', 'DEF-thigh.L.001', 'DEF-shin.L.001', 'DEF-thigh.R.001', 'DEF-shin.R.001', 'DEF-upper_arm.R.001', 'DEF-forearm.R.001', 'DEF-upper_arm.L.001', 'DEF-forearm.L.001']
        for bone_name in remove_bones:
            bone = rig.edit_bones.get(bone_name)
            if bone:
                rig.edit_bones.remove(bone)

        # Rename select bones to match their new position within the armature.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        spine_6_bone = rigify_rig_object.pose.bones.get('DEF-spine.006')
        spine_6_bone.name = 'DEF-head'

        spine_5_bone = rigify_rig_object.pose.bones.get('DEF-spine.005')
        spine_5_bone.name = 'DEF-neck'

        # Remove the second neck bone.
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.armature.select_all(action='DESELECT')
        rig.edit_bones.remove(rig.edit_bones['DEF-spine.004'])
        rig.edit_bones['DEF-neck'].use_connect = True

        # Repair the Rigify rig shoulders by adding copy rotation constraints to the shoulders.
        left_shoulder_copy_rotation_contraint = rigify_rig_object.pose.bones.get('DEF-shoulder.L').constraints.new('COPY_ROTATION')
        left_shoulder_copy_rotation_contraint.target = rigify_rig_object
        left_shoulder_copy_rotation_contraint.subtarget = 'ORG-shoulder.L'
        right_shoulder_copy_rotation_contraint = rigify_rig_object.pose.bones.get('DEF-shoulder.R').constraints.new('COPY_ROTATION')
        right_shoulder_copy_rotation_contraint.target = rigify_rig_object
        right_shoulder_copy_rotation_contraint.subtarget = 'ORG-shoulder.R'

        # Turn off IK Stretch, and rubber tweak by default.
        rigify_rig_object.pose.bones["upper_arm_parent.L"]["IK_Stretch"] = 0
        rigify_rig_object.pose.bones["upper_arm_tweak.L.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["forearm_tweak.L.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["upper_arm_parent.R"]["IK_Stretch"] = 0
        rigify_rig_object.pose.bones["upper_arm_tweak.R.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["forearm_tweak.R"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["forearm_tweak.R.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["thigh_parent.L"]["IK_Stretch"] = 0
        rigify_rig_object.pose.bones["thigh_tweak.L.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["shin_tweak.L"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["shin_tweak.L.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["thigh_parent.R"]["IK_Stretch"] = 0
        rigify_rig_object.pose.bones["thigh_tweak.R.001"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["shin_tweak.R"]["rubber_tweak"] = 0
        rigify_rig_object.pose.bones["shin_tweak.R.001"]["rubber_tweak"] = 0

        # Let the user know the rig is now compatible with Unity, and finish in object mode.
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        rylog.log_status("Rigify is now compatible with Unity Humanoid / VRChat! Make sure you export the rig with only deform bones!", self, type='INFO')
        return{'FINISHED'}