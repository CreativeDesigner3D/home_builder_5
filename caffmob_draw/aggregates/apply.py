"""Posição do agregado no espaço do pai (feature 003, T042; RN-08, RN-09, D-12).

A posição é sempre recalculada de `u`/`v`/`offset` pelos limites de `limits.py`; o valor ajustado ao limite é gravado
de volta no campo (RN-08). Quando o pai muda de tamanho, o gancho de depsgraph refaz a posição dos agregados dele.
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Vector  # type: ignore

from . import limits, props


def local_box(obj):
    """Caixa do objeto avaliado no espaço local dele (com modificadores)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    corners = [Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def box_in_parent(obj, parent):
    """Caixa alinhada aos eixos do pai que envolve o objeto (cantos do objeto avaliado)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    to_parent = parent.matrix_world.inverted() @ obj.matrix_world
    corners = [to_parent @ Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def parent_box(obj):
    agg = obj.btm_aggregate
    return local_box(agg.parent_ref) if agg.parent_ref is not None else None


def current_box(obj):
    """Caixa do agregado no espaço do pai pela posição atual (`location` + `rest_offset`)."""
    agg = obj.btm_aggregate
    lo = tuple(obj.location[i] + agg.rest_offset[i] for i in range(3))
    return lo, tuple(lo[i] + agg.size[i] for i in range(3))


def _write(obj, name, value):
    """Grava o valor ajustado sem disparar o próprio `update` (guarda de `props`)."""
    key = (obj.name, name)
    props._guard.add(key)
    try:
        setattr(obj.btm_aggregate, name, value)
    finally:
        props._guard.discard(key)


def update_position(obj, sync_cut=True):
    agg = obj.btm_aggregate
    if not agg.is_aggregate or agg.kind == 'LEAF' or agg.parent_ref is None or obj.parent != agg.parent_ref:
        return None
    box_p = parent_box(obj)
    size = tuple(agg.size)
    u, v, offset = limits.clamp(box_p, size, agg.face, agg.u, agg.v, agg.offset)
    for name, value in (('u', u), ('v', v), ('offset', offset)):
        if abs(getattr(agg, name) - value) > 1e-9:
            _write(obj, name, value)
    lo, _hi = limits.box_for(box_p, size, agg.face, u, v, offset)
    target = Vector(tuple(lo[i] - agg.rest_offset[i] for i in range(3)))
    if (obj.location - target).length > 1e-9:
        obj.location = target
    if sync_cut and (agg.perforate or agg.cutter is not None):
        from . import perforate
        perforate.sync(obj)
    return u, v, offset


def aggregates_of(parent):
    return [c for c in parent.children if getattr(c, 'btm_aggregate', None) is not None
            and c.btm_aggregate.is_aggregate and c.btm_aggregate.parent_ref == parent]


_busy = False
_last_parent_box = {}      # pai → última caixa vista; só reposiciona quando o pai muda de tamanho


@persistent
def on_depsgraph_update(scene, depsgraph):
    """Pai com geometria nova (mudou de tamanho): reposiciona os agregados dele dentro dos limites."""
    global _busy
    if _busy:
        return
    _busy = True
    try:
        for update in depsgraph.updates:
            if not update.is_updated_geometry or not isinstance(update.id, bpy.types.Object):
                continue
            original = update.id.original
            children = aggregates_of(original)
            if not children:
                continue
            box = local_box(original)
            key = original.name
            if _last_parent_box.get(key) == box:
                continue
            _last_parent_box[key] = box
            for child in children:
                update_position(child)
    except ReferenceError:
        pass
    finally:
        _busy = False
_last_parent_box = {}      # pai → última caixa vista; só reposiciona quando o pai muda de tamanho


def register():
    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
