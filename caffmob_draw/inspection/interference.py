"""Interferência do envelope de abertura (T061, T062; D-29, RF-091).

Envelope: a frente é levada pose a pose de fechada até o máximo (articuladas a cada 15°; gavetas fechada e aberta).
Em cada pose, os cantos das caixas dos objetos da frente são lidos no mundo; cada par de poses consecutivas vira um
casco convexo (cobre a varredura entre elas), encolhido 1 mm para que encostar não conte como bater. A pose original
é restaurada no fim (só `apply`, sem gravar estado).

Detecção: pré-filtro por caixas alinhadas (AABB) e teste fino com `BVHTree.overlap` contra as malhas avaliadas dos
outros objetos visíveis. O próprio módulo da frente fica de fora (inclui as frentes vizinhas do mesmo vão).
"""

import bmesh  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

from . import fronts

STEP_DEGREES = 15.0
TOLERANCE = 0.001   # m
_SKIP_DISPLAY = {'WIRE', 'BOUNDS'}


def _world_corners(objects, depsgraph):
    points = []
    for obj in objects:
        try:
            evaluated = obj.evaluated_get(depsgraph)
        except ReferenceError:
            continue
        if obj.hide_viewport or not obj.visible_get():
            continue
        matrix = evaluated.matrix_world
        points.extend(matrix @ Vector(corner) for corner in evaluated.bound_box)
    return points


def _samples(front):
    if not front.hinged:
        return [0.0, 1.0]
    values, value = [], 0.0
    while value < front.max_value:
        values.append(value)
        value += STEP_DEGREES
    values.append(front.max_value)
    return values


def _shrink(points, tolerance):
    center = sum(points, Vector()) / len(points)
    shrunk = []
    for point in points:
        offset = center - point
        shrunk.append(point + offset.normalized() * min(tolerance, offset.length * 0.5)
                      if offset.length > 1e-9 else point.copy())
    return shrunk


def envelope_hulls(front, context):
    """Lista de nuvens de pontos (mundo), uma por par de poses consecutivas."""
    original = front.get()
    poses = []
    view_layer = context.view_layer
    try:
        for value in _samples(front):
            front.apply(value)
            view_layer.update()
            corners = _world_corners(front.objects(), context.evaluated_depsgraph_get())
            if corners:
                poses.append(corners)
    finally:
        front.apply(original)
        view_layer.update()
    return [_shrink(poses[i] + poses[i + 1], TOLERANCE) for i in range(len(poses) - 1)]


def _hull_bmesh(hulls):
    """BMesh com um casco convexo por nuvem de pontos e, para cada casco, seus planos (ponto, normal para fora)."""
    bm = bmesh.new()
    planes = []
    for points in hulls:
        verts = [bm.verts.new(p) for p in points]
        result = bmesh.ops.convex_hull(bm, input=verts)
        unused = list({v for v in result.get('geom_interior', []) + result.get('geom_unused', [])
                       if isinstance(v, bmesh.types.BMVert)})
        if unused:
            bmesh.ops.delete(bm, geom=unused, context='VERTS')
        faces = [f for f in result.get('geom', []) if isinstance(f, bmesh.types.BMFace) and f.is_valid]
        if faces:
            center = sum(points, Vector()) / len(points)
            hull_planes = []
            for face in faces:
                face.normal_update()
                origin = face.calc_center_median()
                normal = face.normal.copy()
                if normal.dot(origin - center) < 0.0:
                    normal.negate()
                hull_planes.append((origin, normal))
            planes.append(hull_planes)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm, planes


def _inside(point, hull_planes):
    return all((point - origin).dot(normal) <= 0.0 for origin, normal in hull_planes)


def _aabb(points):
    return (Vector([min(p[i] for p in points) for i in range(3)]),
            Vector([max(p[i] for p in points) for i in range(3)]))


def _aabb_overlap(a, b):
    return all(a[0][i] <= b[1][i] and b[0][i] <= a[1][i] for i in range(3))


class _Targets:
    """Objetos que podem ser atingidos, com AABB pré-calculada e BVH sob demanda."""

    def __init__(self, scene, depsgraph):
        self.depsgraph = depsgraph
        self.items = []
        self._bvh = {}
        self._verts = {}
        for obj in scene.objects:
            if obj.type not in {'MESH', 'CURVE'} or obj.display_type in _SKIP_DISPLAY:
                continue
            if obj.hide_viewport or not obj.visible_get() or obj.get('IS_2D_ANNOTATION'):
                continue
            evaluated = obj.evaluated_get(depsgraph)
            corners = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
            self.items.append((obj, _aabb(corners), fronts.module_root_of(obj)))

    def bvh(self, obj):
        key = obj.as_pointer()
        if key not in self._bvh:
            evaluated = obj.evaluated_get(self.depsgraph)
            tree = None
            try:
                mesh = evaluated.to_mesh()
            except RuntimeError:
                mesh = None
            if mesh is not None:
                matrix = evaluated.matrix_world
                verts = [matrix @ v.co for v in mesh.vertices]
                polys = [tuple(p.vertices) for p in mesh.polygons]
                if verts and polys:
                    tree = BVHTree.FromPolygons(verts, polys)
                    step = max(1, len(verts) // 2000)   # amostra para o teste de contenção
                    self._verts[key] = verts[::step]
                evaluated.to_mesh_clear()
            self._bvh[key] = tree
        return self._bvh[key]

    def sample_points(self, obj):
        self.bvh(obj)
        return self._verts.get(obj.as_pointer(), [])


def check_fronts(context, front_list):
    """Verifica as frentes e devolve (resultados, nº de frentes verificadas).

    Cada resultado: dict com `front`, `module`, `hit`, `location` (mundo) e `kind`.
    """
    results = []
    checked = 0
    hulls_by_front = []
    for front in front_list:
        if not front.is_valid() or not front.can_sweep():
            continue
        hulls = envelope_hulls(front, context)
        if hulls:
            hulls_by_front.append((front, hulls))
    targets = _Targets(context.scene, context.evaluated_depsgraph_get())
    for front, hulls in hulls_by_front:
        checked += 1
        own = set(o.as_pointer() for o in front.objects())
        box = _aabb([p for hull in hulls for p in hull])
        candidates = [(obj, aabb) for obj, aabb, root in targets.items
                      if root != front.module_root and obj.as_pointer() not in own and _aabb_overlap(box, aabb)]
        if not candidates:
            continue
        bm, planes = _hull_bmesh(hulls)
        try:
            envelope = BVHTree.FromBMesh(bm)
            for obj, _aabb_box in candidates:
                tree = targets.bvh(obj)
                if tree is None:
                    continue
                # Superfícies que se cruzam, ou o objeto (pequeno) inteiro dentro de um casco.
                pairs = envelope.overlap(tree)
                if pairs:
                    centers = [bm.faces[i].calc_center_median() for i, _j in pairs[:32] if i < len(bm.faces)]
                else:
                    centers = [p for p in targets.sample_points(obj)
                               if any(_inside(p, hull_planes) for hull_planes in planes)][:32]
                if not centers:
                    continue
                location = sum(centers, Vector()) / len(centers)
                results.append({'front': front, 'module': front.module_root.name, 'hit': obj,
                                'location': location, 'kind': front.kind})
        finally:
            bm.free()
    return results, checked


def store_results(window_manager, results, checked):
    state = window_manager.btm_inspection
    state.interferences.clear()
    for item in results:
        entry = state.interferences.add()
        entry.front_name = item['front'].obj.name
        entry.module_name = item['module']
        entry.hit_name = item['hit'].name
        entry.location = item['location']
        entry.kind = item['kind']
    state.interference_index = 0
    state.checked_fronts = checked

