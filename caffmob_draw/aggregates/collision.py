"""Teste de contato da folha de porta com a cena (feature 003, T051; RN-11a, D-19).

Reaproveita a ideia da verificação de interferência da 001 (`inspection/interference.py`): pré-filtro por caixa e
`BVHTree.overlap`. A folha numa pose é a caixa dela (8 cantos, encolhida 1 mm para não acusar o encosto de fechada).
Os alvos (BVH dos objetos visíveis, fora a folha, o pivô e o módulo do pai) ficam em cache por folha e são descartados
quando qualquer outro objeto muda (`depsgraph_update_post`).
"""

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

from ..inspection import fronts
from . import leaf

SHRINK = 0.001
_SKIP_DISPLAY = {'WIRE', 'BOUNDS'}
_BOX_FACES = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0))
_cache = {}          # nome da folha → lista de (objeto, (lo, hi), BVH ou None)


def _aabb(points):
    return (Vector([min(p[i] for p in points) for i in range(3)]),
            Vector([max(p[i] for p in points) for i in range(3)]))


def _overlap(a, b):
    return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))


def _excluded(obj):
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    names = {obj.name}
    pivot = leaf.pivot_of(obj)
    if pivot is not None:
        names.add(pivot.name)
    names.update(c.name for c in obj.children_recursive)
    if parent is not None:
        root = fronts.module_root_of(parent) or parent
        names.add(root.name)
        names.update(c.name for c in root.children_recursive)
        names.add(parent.name)
    return names


def _targets(obj):
    key = obj.name
    if key in _cache:
        return _cache[key]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    skip = _excluded(obj)
    items = []
    for other in bpy.context.scene.objects:
        if other.name in skip or other.type != 'MESH' or other.display_type in _SKIP_DISPLAY:
            continue
        if other.get('IS_CUTTING_OBJ') or other.get('IS_2D_ANNOTATION') or not other.visible_get():
            continue
        evaluated = other.evaluated_get(depsgraph)
        corners = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
        items.append([other, _aabb(corners), None])
    _cache[key] = items
    return items


def _bvh(item):
    if item[2] is None:
        other = item[0]
        evaluated = other.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            polys = [tuple(p.vertices) for p in mesh.polygons]
            item[2] = BVHTree.FromPolygons(verts, polys) if verts and polys else False
        finally:
            evaluated.to_mesh_clear()
    return item[2] or None


class Tester:
    """`hit(fração)` → objeto atingido ou None, para a varredura de `sweep.py`."""

    def __init__(self, obj):
        self.obj = obj
        self.agg = obj.btm_aggregate
        self.parent_world = self.agg.parent_ref.matrix_world.copy()
        self.base = leaf._base(obj)
        self.local = obj.matrix_basis.copy()          # folha no espaço do pivô (fixo)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        corners = [Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]
        center = sum(corners, Vector()) / 8.0
        self.corners = [c + (center - c).normalized() * SHRINK if (center - c).length > SHRINK else c
                        for c in corners]

    def corners_at(self, fraction):
        matrix = self.parent_world @ leaf.pose_matrix(self.agg, self.base, fraction) @ self.local
        return [matrix @ c for c in self.corners]

    def hit(self, fraction):
        points = self.corners_at(fraction)
        box = _aabb(points)
        candidates = [item for item in _targets(self.obj) if _overlap(box, item[1])]
        if not candidates:
            return None
        tree = BVHTree.FromPolygons(points, _BOX_FACES)
        for item in candidates:
            other = _bvh(item)
            if other is not None and tree.overlap(other):
                return item[0]
        return None


@persistent
def on_depsgraph_update(scene, depsgraph):
    """Descarta o cache quando algo além das folhas e dos pivôs muda."""
    if not _cache:
        return
    own = set()
    for name in _cache:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            own.add(obj.name)
            pivot = leaf.pivot_of(obj)
            if pivot is not None:
                own.add(pivot.name)
    for update in depsgraph.updates:
        if isinstance(update.id, bpy.types.Object) and update.id.original.name not in own:
            _cache.clear()
            return


def register():
    if on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update)


def unregister():
    _cache.clear()
    if on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update)
