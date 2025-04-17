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
*Reloads = saves recent changes in Maya
*MayaUtilities = Imports all functions
*Qt Widgets = Builds UI's in Maya

```python
import importlib
import MayaUtilities
importlib.reload(MayaUtilities)

from MayaUtilities import *
from PySide2.QtWidgets import QLabel, QVBoxLayout, QPushButton
import maya.cmds as mc
```