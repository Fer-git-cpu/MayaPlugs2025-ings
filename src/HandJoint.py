import importlib
import MayaUtilities
importlib.reload(MayaUtilities)

from MayaUtilities import MayaWindow
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QSlider, QColorDialog
from PySide6.QtCore import Qt 
from maya.OpenMaya import MVector
import maya.mel as mel
import maya.cmds as mc 
import maya.cmds as cmds

import maya.cmds as cmds

class AutoHandRigBuilder:
    def __init__(self, wrist_joint):
        if not cmds.objExists(wrist_joint) or not cmds.objectType(wrist_joint, isType='joint'):
            raise ValueError("Please select a valid wrist joint.")

        self.wrist_joint = wrist_joint
        self.finger_data = {
            'thumb': [[2, 0, 1], [3, 0, 2], [4, 0, 2.5]],
            'index': [[1, 0, -1], [2, 0, -2], [3, 0, -3]],
            'middle': [[0.5, 0, -1.5], [0.5, 0, -2.5], [0.5, 0, -3.5]],
            'ring': [[-0.5, 0, -1], [-1.5, 0, -2], [-2, 0, -3]],
            'pinky': [[-1, 0, -0.5], [-2, 0, -1.5], [-3, 0, -2.5]],
        }
        self.all_controls = []

    def create_finger_chain(self, offsets, finger_name):
        """Create finger joint chain starting from wrist joint."""
        cmds.select(clear=True)
        base_pos = cmds.xform(self.wrist_joint, q=True, ws=True, t=True)
        joints = []
        for i, offset in enumerate(offsets):
            pos = [base_pos[0] + offset[0], base_pos[1] + offset[1], base_pos[2] + offset[2]]
            jnt = cmds.joint(name=f"{finger_name}_jnt_{i+1}", position=pos)
            joints.append(jnt)
        cmds.select(clear=True)
        return joints

    def create_fk_controls(self, joints):
        """Create FK controls and constrain joints."""
        controls = []
        parent_ctrl = None
        for jnt in joints:
            ctrl = cmds.circle(name=jnt.replace("jnt", "ctrl"), normal=[1, 0, 0], radius=0.5)[0]
            grp = cmds.group(ctrl, name=ctrl + "_grp")
            cmds.delete(cmds.parentConstraint(jnt, grp))
            cmds.orientConstraint(ctrl, jnt, maintainOffset=True)

            if parent_ctrl:
                cmds.parent(grp, parent_ctrl)
            parent_ctrl = ctrl
            controls.append(ctrl)
        return controls

    def build(self):
        rig_grp = cmds.group(empty=True, name="hand_rig_grp")

        
        wrist_ctrl = cmds.circle(name="wrist_ctrl", normal=[1, 0, 0], radius=1.5)[0]
        wrist_grp = cmds.group(wrist_ctrl, name="wrist_ctrl_grp")
        cmds.delete(cmds.parentConstraint(self.wrist_joint, wrist_grp))
        cmds.orientConstraint(wrist_ctrl, self.wrist_joint, maintainOffset=True)
        cmds.parent(wrist_grp, rig_grp)

        
        for finger_name, offsets in self.finger_data.items():
            finger_joints = self.create_finger_chain(offsets, finger_name)
            cmds.parent(finger_joints[0], self.wrist_joint)
            ctrls = self.create_fk_controls(finger_joints)
            self.all_controls.extend(ctrls)

            
            ctrl_grp = ctrls[0] + "_grp"
            cmds.parent(ctrl_grp, wrist_ctrl)

        print("Full FK hand rig created successfully.")


def AutoMakeHandRig():
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("Please select the wrist joint.")
        return
    try:
        rig = AutoHandRigBuilder(selection[0])
        rig.build()
    except Exception as e:
        cmds.warning(str(e))
AutoMakeHandRig()
