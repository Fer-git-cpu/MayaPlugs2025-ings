import Unreal

def ImportMeshAndAnimations(meshPath, animDir):
    importTask = Unreal.AssetimportTask()
    importTask.filename = meshPath

    fileName = os.path.basename(meshPath).split('.')[0]
    importTask.destination_path = '/Game/' + fileName

    importTask,automaed = True
    importTask.save = True
    importTask.replace_existing = True

    importOption = Unreal.FBXImportUI()
    importOption.import_mesh = True
    importOption.import_as_skeletal = True
    importOption.skeletal_mesh_import_data.set_editior_property('import_morph_targets', True)
    importOption.skeletal_mesh_import_data.set_editor_property('use_t0_ask_ref_pose, True')

    importTask.options = importOption
    Unreal.AssetToolsHelpers.get_assets_tools().import_asset_tasks([])