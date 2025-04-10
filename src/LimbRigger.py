from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget, QSlider 
from PySide2.QtCore import Qt 
from maya.OpenMaya import MVector
import maya.OpenMayaUI as omui 
import maya.mel as mel
import shiboken2 

def GetMayaMainWindow():
    mainWindow = omui.MQtUtil.mainWindow() 
    return shiboken2.wrapInstance(int(mainWindow), QMainWindow) 


def DeleteWidgetWithNAme(name):
    for widget in GetMayaMainWindow().findChildren(QWidget, name):
        widget.deleteLater()

class MayaWindow(QWidget):
    def __init__(self): 
        super().__init__(parent = GetMayaMainWindow())
        DeleteWidgetWithNAme(self.GetWidgetuniqueName())
        self.setWindowFlags(Qt.WindowType.Window)
        self.setObjectName(self.GetWidgetuniqueName())
    
    def GetWidgetuniqueName(self):
        return "dsfsdfssfsfsfsfsfsfsfsfsfs" 
    
import maya.cmds as mc 
class LimbRigger: 
    def __init__(self): 
        self.root = "" 
        self.mid = "" 
        self.end = "" 
        self.controllerSize = 5 
    def FindJointBasedOnSelection(self): 
        try:

            self.root = mc.ls(sl=True, type="joint")[0] 
            self.mid = mc.listRelatives(self.root, c=True, type="joint")[0] 
            self.end = mc.listRelatives(self.mid, c=True, type="joint")[0] 
        except Exception as e: #Will catch an error
            raise Exception("Wrong Selection, please select the first joint of the limb") 

    def CreateFKControllerForJoint(self, jntName): 
        ctrlName = "ac_l_fk_" + jntName 
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(name = ctrlName, radius = self.controllerSize, normal = (1,0,0))
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName
    
    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p 0.5 -0.5 -0.5 -p 0.5 -0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 ;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply=True)
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName
    
    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p -12.019173 0 -1.950598 -p -12.051289 0 0.0406298 -p -14.010401 0 0.0245715 -p -14.010401 0 2.031858 -p -11.987056 0 2.063974 -p -11.938881 0 4.055202 -p -9.899479 0 4.007027 -p -9.995828 0 2.031858 -p -7.956426 0 2.063974 -p -7.940367 0 0.0727464 -p -9.963712 0 0.00851321 -p -9.963712 0 -1.998773 -p -12.035231 0 -1.918481 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;")
        grpName = name + "_grp"
        mc.group(name, n = grpName)
        return name, grpName

    def GetObjectLocation(self, objectName):
        x, y, z = mc.xform(objectName, q=True, ws=True, t=True)
        return MVector(x, y, z)

    def PrintMVector(self, vector):
        print(f"<{vector.x}, {vector.y}, {vector.z}>")

    def RigLimb(self): 
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        self.PrintMVector(rootJntLoc)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sol="ikRPsolver", sj=self.root, ee=self.end)

        poleVectorLocationVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVector = MVector(poleVectorLocationVals[0], poleVectorLocationVals[1], poleVectorLocationVals[2])
        poleVector.normalize()

        endJntLoc = self.GetObjectLocation(self.end)
        rootToEndVector = endJntLoc - rootJntLoc

        poleVectorCtrlLoc = rootJntLoc + rootToEndVector /2 + poleVector * rootToEndVector.length()
        poleVectorCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n=poleVectorCtrl)
        poleVectorCtrlGrp = poleVectorCtrl + "_grp"
        mc.group(poleVectorCtrl, n=poleVectorCtrlGrp)
        mc.setAttr(poleVectorCtrlGrp+".t", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, typ="double3")

        mc.poleVectorConstraint(poleVectorCtrl, ikHandleName)

        ikfkBlendCtrl = "ac_ikfk_blend_" + self.root
        ikfkBlendCtrl, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrl)
        mc.setAttr(ikfkBlendCtrlGrp+".t", rootJntLoc.x*2, rootJntLoc.y, rootJntLoc.z*2, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttrName, min = 0, max = 1, l=True)
        ikfkBlendAttr = ikfkBlendCtrl + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikfkBlendAttrName}.ikBlend={ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v={poleVectorCtrlGrp}.v={ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

        topGrpName = f"{self.root}_rig_grp"
        mc.group([rootCtrlGrp, ikEndCtrlGrp, poleVectorCtrlGrp, ikfkBlendCtrlGrp], n=topGrpName)
        mc.parent(ikHandleName, ikEndCtrl)

class LimbRiggerWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limb Rigger")

        
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        toolTipLabel = QLabel("Select the first joint of the limb, and press the auto to find button")
        self.masterLayout.addWidget(toolTipLabel)

        self.jntsListLineEdit = QLineEdit()
        self.masterLayout.addWidget(self.jntsListLineEdit)
        self.jntsListLineEdit.setEnabled(False)
        autoFindJntBtn = QPushButton("Auto Find")
        autoFindJntBtn.clicked.connect(self.AutoFindJntBtnClicked)
        self.masterLayout.addWidget(autoFindJntBtn)

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrlSizeSliderChanged)

        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLabel)
        self.masterLayout.addLayout(ctrlSizeLayout)

        rigLimbBtn = QPushButton("Rig Limb")
        rigLimbBtn.clicked.connect(lambda : self.rigger.RigLimb())
        self.masterLayout.addWidget(rigLimbBtn)

    def CtrlSizeSliderChanged(self, newValue):
        self.ctrlSizeLabel.setText(f"{newValue}")
        self.rigger.controllerSize = newValue

    def AutoFindJntBtnClicked(self):
        try: 
            self.rigger.FindJointBasedOnSelection()
            self.jntsListLineEdit.setText(f"{self.rigger.root},{self.rigger.mid},{self.rigger.end}")
        except Exception as e:
            QMessageBox.critical(self, "error", f"{e}")

import maya.cmds as cmds

def ApplyColorController(ColorIndex):
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("Please select a controller.")
        return

    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not shapes:
            continue
        for shape in shapes:
            if cmds.objectType(shape) == 'nurbsCurve':
                cmds.setAttr(shape + ".overrideEnabled", 1)
                cmds.setAttr(shape + ".overrideColor", ColorIndex)

def ShowColorPickUI():
    if cmds.window("colorPickerWin", exists=True):
        cmds.deleteUI("colorPickerWin")

    window = cmds.window("colorPickerWin", title="Controller Color Picker", widthHeight=(200, 300))
    cmds.columnLayout(adjustableColumn=True)

    
    for i in range(32):
        cmds.button(label="Color " + str(i), backgroundColor=IndexToRgb(i), command=lambda x, idx=i: ApplyColorController(idx))
        cmds.showWindow(window)

def IndexToRgb(index):
    
    colorTable = [
        (360.0, 0.0, 0.0), (0.247, 0.247, 0.247), (0.608, 0.608, 0.608),
        (0.784, 0.0, 0.0), (0.0, 0.6, 0.165), (0.0, 0.0, 0.6),
        (0.541, 0.282, 0.2), (0.6, 0.188, 0.376), (0.251, 0.251, 0.251),
        (0.0, 1.0, 0.0), (0.0, 0.25, 0.6), (1.0, 1.0, 0.0), (0.0, 1.0, 1.0),
        (1.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]
    
    return colorTable[index] if index < len(colorTable) else (0.0, 0.0, 0.0)

limbRiggerWidget = LimbRiggerWidget()
limbRiggerWidget.show()

GetMayaMainWindow()
ShowColorPickUI()