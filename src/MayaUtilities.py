from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt 
import maya.OpenMayaUI as omui 
import shiboken6
import maya.cmds as mc

def IsMesh(obj):
    shapes = mc.listRelatives(obj, s=True)
    if not shapes:
        return False
    
    for s in shapes:
        if mc.objectType(s)=="mesh":
            return True
        
    return False

def IsSkin(obj):
    return mc.objectType(obj) == "skinCluster"

def IsJoint(obj):
    return mc.objectType(obj) == "joint"

def GetUpperStream(obj):
    return mc.listConnections(obj, s=True, d=False, sh=True)

def GetLowerStream(obj):
    return mc.listConnections(obj, s=False, d=True, sh=True)


def GetAllConnectionsIn(obj, nextFunc, filter = None):
    allFound = set()
    nexts = nextFunc(obj)
    searchDepth = 100
    while nexts and searchDepth > 0:
        searchDepth -= 1
        for next in nexts:
            allFound.add(next)
        
        nexts = nextFunc(nexts)
        if nexts:
            nexts = [x for x in nexts if x not in allFound]
    print(f"found items: {allFound}")
    if not filter:
        return list(allFound)
    
    filtered = []
    for found in allFound:
        if filter(found):
            filtered.append(found)

    return filtered

def GetMayaMainWindow():
    mainWindow = omui.MQtUtil.mainWindow() 
    return shiboken6.wrapInstance(int(mainWindow), QMainWindow) 


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