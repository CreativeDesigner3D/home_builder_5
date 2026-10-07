"""Importar modelo 3D externo (feature 003, T047; RF-11, D-16).

Chama o importador do próprio Blender pelo tipo do arquivo (OBJ, FBX, glTF/GLB). Objetos trazidos por outros addons
(por exemplo, um importador de SketchUp) também podem ser convertidos: a conversão aceita qualquer malha da cena.
"""

import os

import bpy  # type: ignore
from bpy_extras.io_utils import ImportHelper  # type: ignore

FORMATS = {'.obj': ('wm', 'obj_import'), '.fbx': ('import_scene', 'fbx'), '.glb': ('import_scene', 'gltf'),
           '.gltf': ('import_scene', 'gltf')}


class BTM_OT_ImportModel(bpy.types.Operator, ImportHelper):
    """Importa um modelo 3D (OBJ, FBX, glTF/GLB) para converter em agregado ou folha de porta"""
    bl_idname = "caffmob.import_model"
    bl_label = "Importar modelo 3D"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.obj;*.fbx;*.glb;*.gltf", options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        ext = os.path.splitext(self.filepath)[1].lower()
        target = FORMATS.get(ext)
        if target is None:
            self.report({'ERROR'}, f"Formato não suportado: {ext or 'sem extensão'} (use OBJ, FBX, glTF ou GLB)")
            return {'CANCELLED'}
        before = set(bpy.data.objects)
        operator = getattr(getattr(bpy.ops, target[0]), target[1])
        try:
            result = operator(filepath=self.filepath)
        except RuntimeError as exc:
            self.report({'ERROR'}, f"O Blender não conseguiu importar {os.path.basename(self.filepath)}: {exc}")
            return {'CANCELLED'}
        if 'FINISHED' not in result:
            self.report({'ERROR'}, f"Importação cancelada: {os.path.basename(self.filepath)}")
            return {'CANCELLED'}
        new = [obj for obj in bpy.data.objects if obj not in before]
        meshes = [obj for obj in new if obj.type == 'MESH']
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in meshes:
            obj.select_set(True)
        if meshes:
            context.view_layer.objects.active = meshes[0]
        self.report({'INFO'}, f"{len(meshes)} malha(s) importada(s). Selecione o pai por último e use "
                              "\"Converter em agregado\"")
        return {'FINISHED'}


classes = (BTM_OT_ImportModel,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
