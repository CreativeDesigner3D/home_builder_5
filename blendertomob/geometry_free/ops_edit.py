"""Edição da geometria livre (T033; RF-12, RF-15).

As medidas, a forma, a fabricação e o material são editados na janela de propriedades (`ui/object_properties.py`,
grupo "Geometria"), direto em `btm_geometry`. Aqui ficam as ações, todas com desfazer:
- Duplicar: cópia com malha própria, ao lado (+X local);
- Espelhar: passa a peça para o outro lado do ponto de origem no X local (a origem continua no mesmo lugar);
- Excluir: remove a geometria.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from . import mesh


def _active_geometry(context):
    obj = context.active_object
    return obj if mesh.is_geometry(obj) else None


class _GeometryAction:
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and _active_geometry(context) is not None


class BTM_OT_GeometryDuplicate(_GeometryAction, bpy.types.Operator):
    """Duplica a geometria ao lado da original"""
    bl_idname = "btm.geometry_duplicate"
    bl_label = "Duplicar Geometria"

    def execute(self, context):
        obj = _active_geometry(context)
        copy = obj.copy()
        copy.data = obj.data.copy()
        for collection in obj.users_collection:
            collection.objects.link(copy)
        x = mesh.size(*(getattr(obj.btm_geometry, k) for k in ('kind', 'plane', 'width', 'depth', 'height',
                                                                   'thickness')))[0]
        copy.matrix_world = obj.matrix_world.copy()
        copy.location = obj.matrix_world @ Vector((x, 0.0, 0.0))
        if 'btm_uid' in copy:
            del copy['btm_uid']
        obj.select_set(False)
        copy.select_set(True)
        context.view_layer.objects.active = copy
        return {'FINISHED'}


class BTM_OT_GeometryMirror(_GeometryAction, bpy.types.Operator):
    """Passa a geometria para o outro lado do ponto de origem (X local)"""
    bl_idname = "btm.geometry_mirror"
    bl_label = "Espelhar Geometria"

    def execute(self, context):
        obj = _active_geometry(context)
        x = mesh.size(*(getattr(obj.btm_geometry, k) for k in ('kind', 'plane', 'width', 'depth', 'height',
                                                                   'thickness')))[0]
        offset = obj.matrix_world.to_3x3() @ Vector((x, 0.0, 0.0))
        if obj.get('btm_mirrored'):
            obj.location += offset
            del obj['btm_mirrored']
        else:
            obj.location -= offset
            obj['btm_mirrored'] = True
        return {'FINISHED'}


class BTM_OT_GeometryDelete(_GeometryAction, bpy.types.Operator):
    """Exclui a geometria"""
    bl_idname = "btm.geometry_delete"
    bl_label = "Excluir Geometria"

    def execute(self, context):
        obj = _active_geometry(context)
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data.users == 0:
            bpy.data.meshes.remove(data)
        return {'FINISHED'}


classes = (BTM_OT_GeometryDuplicate, BTM_OT_GeometryMirror, BTM_OT_GeometryDelete)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
