"""Marca o plano de corte como desatualizado quando um módulo do projeto muda (T038).

Handler `depsgraph_update_post` (`@persistent`): se a geometria ou a posição de um objeto pertencente a um módulo
com `btm_uid` mudou depois do cálculo, liga `btm_settings.cut_plan_stale`. Só escreve uma vez (enquanto já estiver
desatualizado não faz nada) e não roda se ainda não houver plano calculado.
"""

import bpy
from bpy.app.handlers import persistent

UID_PROP = 'btm_uid'
PLAN_PROP = 'btm_nesting_sheets_count'


def _belongs_to_module(obj):
    current = obj
    while current is not None:
        if current.get(UID_PROP):
            return True
        current = current.parent
    return False


@persistent
def depsgraph_update_post(scene, depsgraph):
    settings = getattr(scene, 'btm_settings', None)
    if settings is None or settings.cut_plan_stale or PLAN_PROP not in scene:
        return
    for update in depsgraph.updates:
        if not (update.is_updated_geometry or update.is_updated_transform):
            continue
        obj = update.id.original if update.id is not None else None
        if isinstance(obj, bpy.types.Object) and _belongs_to_module(obj):
            settings.cut_plan_stale = True
            return


def register():
    if depsgraph_update_post not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)


def unregister():
    if depsgraph_update_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)
