"""Folha 3D das portas de ambiente na cena (T044; D-20, M-09).

A porta do Home Builder 5 (`IS_ENTRY_DOOR_BP`) é uma gaiola de recorte com o símbolo 2D `GeoNodeDoorSwing` como filho.
`ensure_leaves(porta)` cria (no primeiro uso) ou atualiza, como filhos da porta:
- um pivô (Empty, `btm_room_door_pivot` = `'L'`/`'R'`) na dobradiça; a rotação Z dele é a abertura;
- a folha (malha, `btm_room_door_leaf`), filha do pivô, com largura × `Door Thickness` × altura da porta.
O lado e o sentido vêm de `room_door_math.leaves` com `Is Left`/`Is Double`/`Swing Inside` do símbolo. A malha é
refeita a cada chamada (porta redimensionada continua certa); se o tipo de abertura mudou, os pivôs são recriados.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from .. import hb_types
from . import room_door_math

DOOR_TAG = 'IS_ENTRY_DOOR_BP'
PIVOT_TAG = 'btm_room_door_pivot'
LEAF_TAG = 'btm_room_door_leaf'


def swing_of(door):
    """Símbolo de abertura (`GeoNodeDoorSwing`) da porta, ou None (vão aberto sem folha)."""
    for child in door.children:
        geo = hb_types.GeoNodeObject(child)
        if child.get('IS_2D_ANNOTATION') and geo.has_modifier() and geo.has_input('Swing Inside'):
            return geo
    return None


def is_room_door(obj):
    return obj is not None and bool(obj.get(DOOR_TAG)) and swing_of(obj) is not None


def pivots_of(door):
    return sorted((c for c in door.children if c.get(PIVOT_TAG)), key=lambda c: str(c[PIVOT_TAG]))


def leaf_specs(door):
    cage = hb_types.GeoNodeObject(door)
    swing = swing_of(door)
    return room_door_math.leaves(
        cage.get_input('Dim X'), cage.get_input('Dim Y'), cage.get_input('Dim Z'),
        bool(swing.get_input('Is Left')), bool(swing.get_input('Is Double')), bool(swing.get_input('Swing Inside')),
        swing.get_input('Door Thickness') or 0.035)


def _remove(obj):
    for child in list(obj.children_recursive) + [obj]:
        data = child.data if child.type == 'MESH' else None
        bpy.data.objects.remove(child, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


def _build_mesh(mesh, leaf):
    bm = bmesh.new()
    verts = {c: bm.verts.new(c) for c in room_door_math.leaf_corners(leaf)}
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm, input=list(verts.values()))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def ensure_leaves(door):
    """[(Leaf, pivô)] da porta, criando ou atualizando pivôs e folhas."""
    specs = leaf_specs(door)
    pivots = pivots_of(door)
    if [str(p[PIVOT_TAG]) for p in pivots] != sorted(s.side for s in specs):
        for pivot in pivots:
            _remove(pivot)
        pivots = []
    by_side = {str(p[PIVOT_TAG]): p for p in pivots}
    result = []
    for spec in specs:
        pivot = by_side.get(spec.side)
        if pivot is None:
            pivot = bpy.data.objects.new(f"{door.name}_Pivo_{spec.side}", None)
            pivot.empty_display_size = 0.05
            pivot[PIVOT_TAG] = spec.side
            for collection in door.users_collection:
                collection.objects.link(pivot)
            pivot.parent = door
        pivot.location = (spec.hinge_x, spec.hinge_y, 0.0)
        leaf = next((c for c in pivot.children if c.get(LEAF_TAG)), None)
        if leaf is None:
            leaf = bpy.data.objects.new(f"{door.name}_Folha_{spec.side}", bpy.data.meshes.new(f"{door.name}_Folha"))
            leaf[LEAF_TAG] = True
            for collection in door.users_collection:
                collection.objects.link(leaf)
            leaf.parent = pivot
        _build_mesh(leaf.data, spec)
        result.append((spec, pivot))
    return result
