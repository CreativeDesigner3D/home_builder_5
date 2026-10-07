"""Marca o plano de corte como desatualizado quando um módulo do projeto muda (T038).

Handler `depsgraph_update_post` (`@persistent`): se a geometria ou a posição de um objeto pertencente a um módulo
com `btm_uid` mudou depois do cálculo, liga `btm_settings.cut_plan_stale`. Só escreve uma vez (enquanto já estiver
desatualizado não faz nada) e não roda se ainda não houver plano calculado.

Abrir portas e gavetas não muda nenhuma peça (T070, D-31): mudanças em frentes, pivôs e no que elas carregam
(puxador, caixa de gaveta) são ignoradas, assim como tudo enquanto o modo de inspeção anima. No face frame, gravar a
abertura recalcula o gabinete inteiro; o adaptador avisa com `skip_next_update()` e a próxima rodada é ignorada.
"""

import bpy
from bpy.app.handlers import persistent

UID_PROP = 'btm_uid'
PLAN_PROP = 'btm_nesting_sheets_count'

FRONT_TAGS = ('IS_CABINET_FRONT', 'IS_DOOR_FRONT', 'IS_DRAWER_FRONT', 'IS_PULLOUT_FRONT')
FRONT_ROLES = frozenset({
    'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'TILT_OUT', 'FRONT_PIVOT',            # face frame
    'CLOSET_DOOR_FRONT', 'CLOSET_DRAWER_FRONT', 'CLOSET_DRAWER_BOX',              # closets
})
BTM_FRONT_SUFFIXES = ('_Door_L', '_Door_R', '_Door_Flip', '_Controller')         # módulo rápido

_skip_next = [False]


def skip_next_update():
    """A próxima rodada do depsgraph vem de uma abertura de frente (recálculo do face frame): não marcar."""
    _skip_next[0] = True


def _is_front_part(obj):
    """True se `obj` é uma frente (ou pivô) ou está pendurado numa, até a raiz do módulo."""
    current = obj
    while current is not None and not current.get(UID_PROP):
        if any(current.get(tag) for tag in FRONT_TAGS) or current.get('hb_part_role') in FRONT_ROLES:
            return True
        if current.name.endswith(BTM_FRONT_SUFFIXES):
            return True
        current = current.parent
    return False


def _inspection_running():
    from ..inspection import ops_inspect
    return ops_inspect.inspection_running()


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
        _skip_next[0] = False
        return
    if _skip_next[0]:
        _skip_next[0] = False
        return
    if _inspection_running():
        return
    for update in depsgraph.updates:
        if not (update.is_updated_geometry or update.is_updated_transform):
            continue
        obj = update.id.original if update.id is not None else None
        if isinstance(obj, bpy.types.Object) and _belongs_to_module(obj) and not _is_front_part(obj):
            settings.cut_plan_stale = True
            return


def register():
    if depsgraph_update_post not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)


def unregister():
    if depsgraph_update_post in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)
