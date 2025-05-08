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
    def __init__(self, wristJoint):
        if not cmds.objExists(wristJoint) or not cmds.objectType(wristJoint, isType='joint'):
            raise ValueError("Please select a valid wrist joint.")

        self.wristJoint = wristJoint
        self.finger_data = {
            'thumb': [[2, 0, 1], [3, 0, 2], [4, 0, 2.5]],
            'index': [[1, 0, -1], [2, 0, -2], [3, 0, -3]],
            'middle': [[0.5, 0, -1.5], [0.5, 0, -2.5], [0.5, 0, -3.5]],
            'ring': [[-0.5, 0, -1], [-1.5, 0, -2], [-2, 0, -3]],
            'pinky': [[-1, 0, -0.5], [-2, 0, -1.5], [-3, 0, -2.5]],
        }
        self.allControls = []

    def makeFingerChain(self, offsets, fingerName):
        cmds.select(clear=True)
        basePosition = cmds.xform(self.wristJoint, q=True, ws=True, t=True)
        joints = []
        for i, offset in enumerate(offsets):
            pos = [basePosition[0] + offset[0], basePosition[1] + offset[1], basePosition[2] + offset[2]]
            jnt = cmds.joint(name=f"{fingerName}_jnt_{i+1}", position=pos)
            joints.append(jnt)
        cmds.select(clear=True)
        return joints

    def create_fk_controls(self, joints):

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
        rigGrp = cmds.group(empty=True, name="hand_rig_grp")

        
        wristCtrl = cmds.circle(name="wris_ctrl", normal=[1, 0, 0], radius=1.5)[0]
        wristGrp = cmds.group(wristCtrl, name="wrist_ctrl_grp")
        cmds.delete(cmds.parentConstraint(self.wristJoint, wristGrp))
        cmds.orientConstraint(wristCtrl, self.wristJoint, maintainOffset=True)
        cmds.parent(wristGrp, rigGrp)

        
        for fingerName, offsets in self.finger_data.items():
            fingerJoints = self.makeFingerChain(offsets, fingerName)
            cmds.parent(fingerJoints[0], self.wristJoint)
            ctrls = self.create_fk_controls(fingerJoints)
            self.allControls.extend(ctrls)

            
            ctrlGrp = ctrls[0] + "_grp"
            cmds.parent(ctrlGrp, wristCtrl)

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
