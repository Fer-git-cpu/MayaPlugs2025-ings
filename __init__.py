import os
import sys

initFilePath = os.path.abspath(__file__)
pluginDir = os.path.dirname(initFilePath)
srcDir = os.path.join(pluginDir, "src")
unrealSDWDir = os.path.join(pluginDir, "vendor", "UnrealSDK")

def AddDirToPath(dir):
    if dir not in sys.path:
        sys.path.append(dir)
        print(f"added {dir} to path")

AddDirToPath(pluginDir)
AddDirToPath(srcDir)
AddDirToPath(unrealSDWDir)