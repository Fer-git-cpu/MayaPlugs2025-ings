import sys 

prjPath = "D:/TechnicalDirection/ScriptsCode/MayaPlugs2025/src"
moduleDir = "D:/TechnicalDirection/ScriptsCode"

if prjPath not in sys.path:
    sys.path.append(prjPath)

if moduleDir not in sys.path:
    sys.path.append(moduleDir)