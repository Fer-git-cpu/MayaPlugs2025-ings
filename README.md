# My Maya Plugins

## Limb Rigger

<img src="./assets/LimbRigger.png" width=400>
<img src="./assets/LimbRigge2.png" width=400>

this plugin rigs any  3 joint limb with ik and fk and ikfk blend.

* support auto joint finding 
* controller size control
* controller color control

# Proxy Generator

This imports all of the other functions that were made previously to create more space and for them to maturally connect to Maya.
* Reloads = saves recent changes in Maya
* MayaUtilities = Imports all functions
* Qt Widgets = Builds UI's in Maya

```python
import importlib
import MayaUtilities
importlib.reload(MayaUtilities)

from MayaUtilities import *
from PySide2.QtWidgets import QLabel, QVBoxLayout, QPushButton
import maya.cmds as mc
```
This class is called ProxyGenerator, is a mesh based on skinning  data and joint influences that is directly connected to Maya.

* self.skin: stores the skin cluster influencing the mesh.
* self.model: stores the name of the selected model (mesh).
* self.jnts: stores joints influencing the skin.
* skin = GetAllConnectionsIn(modelShape, GetUpperStream, IsSkin) #Connects the skin cluster upstream of the model's shape
* jnts = GetAllConnectionsIn(modelShape, GetUpperStream, IsJoint) #Enables all joints influencing  the mesh through skin cluster.
* modelShape = mc.listRelatives(self.model, s=True)[0] #Gets shape node of the model, necessary for connecting to deformation history
* if not IsMesh(model) #if something else is selected that isn't a mesh, an error will appear
* model = mc.ls(sl=True)[0] = First selected object in the Maya Scene
* print(f"found model {self.model} with skin {self.skin} and joins: {self.jnts}") #prints what's found
* for jnt, verts in jntVertDict.items():
    newChunck = self.CreateProxyModelForJntAndVerts(jnt, verts) #Creates a proxy mesh for the part of the mesh of each joint it influences

```python
class ProxyGenerator:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnts = []

    def BuildProxyForSelectedMesh(self):
        model = mc.ls(sl=True)[0]
        if not IsMesh(model):
            print(f"{model} is not a mesh!")
            return
        
        self.model = model
        modelShape = mc.listRelatives(self.model,s=True)[0]
        skin = GetAllConnectionsIn(modelShape, GetUpperStream, IsSkin)
        if not skin:
            print(f"{self.model} is not bound with any joint")
            return
        jnts = GetAllConnectionsIn(modelShape, GetUpperStream, IsJoint)
        if not jnts:
            print(f"{self.model} is not bound with any joint")
            return
        
        self.skin = skin[0]
        self.jnts = jnts
        print(f"found model {self.model} with skin {self.skin} and joins: {self.jnts}")

        jntVertDict = self.GenerateJntVertsDict()
        chuncks = []
        ctrls = []
        for jnt, verts in jntVertDict.items():
            newChunck = self.CreateProxyModelForJntAndVerts(jnt, verts)
```
* faces = mc.polyListComponentConversion(verts, fromVertex=True, toFace=True)
faces = mc.ls(faces, fl=True) #Converts the list of vertices to their associated polygon faces.
* faceNames = set()
for face in faces:
    faceNames.add(face.replace(self.model, "")) #Removes the model prefix from each face name to get just the face indices and stores for compairison
* dup = mc.duplicate(self.model)[0] #Duplicates the full model
* allDupFaces = mc.ls(f"{dup}.f[*]", fl=True)
facesToDelete = []
for dupFace in allDupFaces:
    if dupFace.replace(dup,"") not in faceNames:
        facesToDelete.append(dupFace) #Collects all of the faces on the duplicate.
* mc.delete(facesToDelete) #Deletes all of the faces that weren't in the original face set 
* dupName = self.model + "_" + jnt + "_proxy"
mc.rename(dup, dupName)
return dupName #Renames the remaining model
```python
def CreateProxyModelForJntAndVerts(self, jnt, verts):
        if not verts:
            return None
        
        faces = mc.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        faces = mc.ls(faces, fl=True)

        faceNames = set()
        for face in faces:
            faceNames.add(face.replace(self.model, ""))

        dup = mc.duplicate(self.model)[0]
        allDupFaces = mc.ls(f"{dup}.f[*]", fl=True)
        facesToDelete = []
        for dupFace in allDupFaces:
            if dupFace.replace(dup,"") not in faceNames:
                facesToDelete.append(dupFace)

        mc.delete(facesToDelete)

        dupName = self.model + "_" + jnt + "_proxy"
        mc.rename(dup, dupName)
        return dupName
```
* dict = {}
for jnt in self.jnts:
    dict[jnt] = [] #Creates a key for each joint from the self.jnts list with an empty list.
* verts = mc.ls(f"{self.model}.vtx[*]", fl=True) #Gets all the vertices from the self.model and flattens the list.
* for vert in verts:
    owningJnt = self.GetJntWithMaxInfluence(vert, self.skin)
    dict[owningJnt].append(vert) #Adds the vertex into the joint list in the dictionary.
* return dict #Returns the last dictionary. Key = joint name. Value = list of verticles that influence the joint the most.
```python
 def GenerateJntVertsDict(self):
        dict = {}
        for jnt in self.jnts:
            dict[jnt] = []

        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
        for vert in verts:
            owningJnt = self.GetJntWithMaxInfluence(vert, self.skin)
            dict[owningJnt].append(vert)
        
        return dict

        weights = mc.skinPercent(skin, vert, q=True, v=True)
        jnts = mc.skinPercent(skin, vert, q=True, t=None)
        
        maxWeightIndex = 0
        maxWeight = weights[0]
        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[i]
                maxWeightIndex = i
            return jnts[maxWeightIndex]
```
* class ProxyGeneratorWidget(MayaWindow): #Access UI class that inherits Maya's window.
* def __init__(self):
    super().__init__()
    self.generator = ProxyGenerator() #Calls the parent constructor
* self.masterLayout = QVBoxLayout() #Creats a vertical layout window in Maya when activated
* self.setLayout(self.masterLayout) #Creates the main widget
* self.masterLayout.addWidget(QLabel("Please select the rigged model, and press the build button")) #Creates and added a label with instructions for the user
* buildBtn = QPushButton("Build") #Names the button "Build"
* self.masterLayout.addWidget(buildBtn) #Add a button ladeled "Build"
* buildBtn.clicked.connect(self.generator.BuildProxyForSelectedMesh) #This function does: detects the selected mesh in Maya, iterates over joints and vertices, and creates proxy meshes per joint.
* self.setWindowTitle("Proxy Generator") #Creates the title of the window
* def GetWidgetuniqueName(self):
    return "ProxyGeneratorJL4154151415" #Returns a unique identifier for the UI

```python
class ProxyGeneratorWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.generator = ProxyGenerator()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Please select the rigged model, and press the build button"))
        buildBtn = QPushButton("Build")
        self.masterLayout.addWidget(buildBtn)
        buildBtn.clicked.connect(self.generator.BuildProxyForSelectedMesh)
        self.setWindowTitle("Proxy Generator")

    def GetWidgetuniqueName(self):
        return "ProxyGeneratorJL4154151415"
    
ProxyGeneratorWidget().show()
```