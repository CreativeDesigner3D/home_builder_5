"""ISO and ROOM_ISO views: the products seen from above and to one side.

ISO shows one wall and what stands on it, as the Elevation View's own
iso does; ROOM_ISO shows the whole room from the corner that sees the
most of it. The walls are ghosted -- a light outline, never a face -- so
nothing is hidden behind one, and the products are white faces with
their edges inked, each hiding what stands behind it.

With a GPU the view is drawn with a depth buffer and set as a picture;
without one (background mode) it is line work painted far to near.
"""

import math

import bpy
from mathutils import Matrix, Vector

from ..operators import elevation_mode as em
from . import draft, views
from .drawing import Drawing

PITCH = em.ISO_PITCH
YAW = em.ISO_YAW
MARGIN = 0.05               # m kept round what is shown
GHOST = (0.62, 0.62, 0.62)
GHOST_WIDTH = 0.35
EDGE_WIDTH = em.PRINT_EDGE_WIDTH
DETAIL_WIDTH = em.PRINT_DETAIL_WIDTH
RASTER_DPI = 300
RASTER_MAX = 8192


def _camera(F, box, yaw):
    """(camera matrix, (l, r, b, t)) looking at `box` (x0, x1, y0, y1,
    z0, z1 in the frame F) from `yaw` round its front, tipped down."""
    x0, x1, y0, y1, z0, z1 = box[:6]
    centre = Vector(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    R = (Matrix.Rotation(yaw, 4, 'Z')
         @ Matrix.Rotation(math.pi / 2.0 - PITCH, 4, 'X'))
    C = (F @ Matrix.Translation(centre) @ R
         @ Matrix.Translation((0.0, 0.0, em.SIDE_DIST)))
    Ci = C.inverted_safe()
    xs, ys = [], []
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                q = Ci @ (F @ Vector((x, y, z)))
                xs.append(q.x)
                ys.append(q.y)
    return C, (min(xs) - MARGIN, max(xs) + MARGIN,
               min(ys) - MARGIN, max(ys) + MARGIN)


class _View:
    def __init__(self, k, ox, oy):
        self.k, self.ox, self.oy = k, ox, oy


def _faces(context, owners, Fi, view, deep):
    if not owners:
        return []
    return em._print_faces(context, [], Fi, view, only=owners, deep=deep,
                           molding=True)


def _draw(context, C, span, products, walls, width, height):
    """The Drawing of `products` (object names) and the ghosts of
    `walls` seen by camera C, fitted to width x height points."""
    l, r, b, t = span
    k = min(width / (r - l), height / (t - b))
    w, h = (r - l) * k, (t - b) * k
    view = _View(k, -l * k, -b * k)
    Fi = em._CAMERA_TO_PRINT @ C.inverted_safe()
    out = Drawing(w, h)
    deep = not bpy.app.background
    front = _faces(context, products, Fi, view, deep)
    back = _faces(context, walls, Fi, view, deep)
    picture = _raster(front, back, w, h) if deep else None
    if picture is not None:
        rgb, pw, ph = picture
        out.image(rgb, pw, ph, 0.0, 0.0, w, h)
    else:
        if deep:        # drawn for the depth buffer: flatten
            front = [(d, [q[:2] for q in poly],
                      _flat_edges(edges)) for d, poly, edges in front]
            back = [(d, [q[:2] for q in poly],
                     _flat_edges(edges)) for d, poly, edges in back]
        out.stroke_color(GHOST)
        out.line_width(GHOST_WIDTH)
        for _d, _poly, edges in back:
            if edges:
                out.lines(list(edges))
        out.fill_color(em.PAPER)
        out.stroke_color(em.PRINT_EDGE)
        front.sort(key=lambda f: -f[0])            # far first
        for _d, poly, edges in front:
            out.polygon(poly, fill=True, stroke=False)
            if edges:
                em._ink_edges(out, edges)
    out.info = {'k': None, 'scale': None}
    return out


def _flat_edges(edges):
    flat = em._Edges((a[:2], b[:2]) for a, b in edges)
    flat.heavy = getattr(edges, 'heavy', len(edges))
    return flat


def _raster(front, back, w, h):
    """(rgb bytes top row first, px wide, px high) of the products'
    faces drawn with a depth buffer, edges inked, and the walls' edges
    in grey where nothing stands in front of them. None without a GPU."""
    if bpy.app.background or not (front or back) or w < 1 or h < 1:
        return None
    import gpu
    import numpy as np
    from gpu_extras.batch import batch_for_shader
    ss = 2                              # drawn double size, then averaged
    scale = min(RASTER_DPI / 72.0, RASTER_MAX / (ss * max(w, h)))
    tw = max(1, int(math.ceil(w * scale))) * ss
    th = max(1, int(math.ceil(h * scale))) * ss
    depths = [q[2] for _d, poly, _e in front + back for q in poly]
    d0, d1 = min(depths), max(depths)

    def z(d, lift=0.0):
        return -(d - d0 + 1.0 - lift)

    tris = []
    heavy, light, ghost = [], [], []
    for _depth, poly, edges in front:
        pts = [(q[0], q[1], z(q[2])) for q in poly]
        for i in range(1, len(pts) - 1):
            tris += [pts[0], pts[i], pts[i + 1]]
        n = getattr(edges, 'heavy', len(edges))
        for i, (a, c) in enumerate(edges):
            seg = [(a[0], a[1], z(a[2], em.PRINT_RASTER_LIFT)),
                   (c[0], c[1], z(c[2], em.PRINT_RASTER_LIFT))]
            (heavy if i < n else light).extend(seg)
    for _depth, _poly, edges in back:
        for a, c in edges:
            ghost += [(a[0], a[1], z(a[2], em.PRINT_RASTER_LIFT)),
                      (c[0], c[1], z(c[2], em.PRINT_RASTER_LIFT))]
    off = gpu.types.GPUOffScreen(tw, th)
    try:
        with off.bind():
            fb = gpu.state.active_framebuffer_get()
            fb.clear(color=(1.0, 1.0, 1.0, 1.0), depth=1.0)
            gpu.state.blend_set('NONE')
            gpu.state.depth_mask_set(True)
            gpu.state.depth_test_set('LESS_EQUAL')
            try:
                with gpu.matrix.push_pop(), \
                        gpu.matrix.push_pop_projection():
                    gpu.matrix.load_identity()
                    gpu.matrix.load_projection_matrix(
                        em._ortho(0.0, w, 0.0, h, 0.5, (d1 - d0) + 2.0))
                    flat = gpu.shader.from_builtin('UNIFORM_COLOR')
                    if tris:
                        flat.bind()
                        flat.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
                        batch_for_shader(flat, 'TRIS',
                                         {"pos": tris}).draw(flat)
                    line = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
                    for pts, width, colour in (
                            (ghost, GHOST_WIDTH, GHOST),
                            (light, DETAIL_WIDTH, (0.0, 0.0, 0.0)),
                            (heavy, EDGE_WIDTH, (0.0, 0.0, 0.0))):
                        if not pts:
                            continue
                        line.bind()
                        line.uniform_float("viewportSize", (tw, th))
                        line.uniform_float(
                            "lineWidth", max(1.5, width * scale * ss))
                        line.uniform_float("color", (*colour, 1.0))
                        batch_for_shader(line, 'LINES',
                                         {"pos": pts}).draw(line)
            finally:
                gpu.state.depth_test_set('NONE')
                gpu.state.depth_mask_set(False)
            buf = fb.read_color(0, 0, tw, th, 4, 0, 'UBYTE')
    finally:
        off.free()
    buf.dimensions = tw * th * 4
    arr = np.array(buf, dtype=np.uint8)
    arr = arr.reshape(th, tw, 4)[::-1, :, :3].astype(np.float32)
    arr = arr.reshape(th // ss, ss, tw // ss, ss, 3).mean(axis=(1, 3))
    return arr.astype(np.uint8).tobytes(), tw // ss, th // ss


# ---- One wall ------------------------------------------------------------------

def resolve(context, view, width, height):
    wall = views.wall_of(view)
    if wall is None:
        return None
    scene = context.scene
    items = [it for it in views.wall_items(scene, wall)
             if it.kind != 'OPENING']
    if not items:
        return None
    F = em._frame(wall)[0]
    box = em._side_box(wall, items)
    yaw = -YAW if box[6] else YAW
    C, span = _camera(F, box, yaw)
    products = em._print_owners(items, scene, molding=True)
    walls = {wall.name} | _neighbours(scene, wall)
    return _draw(context, C, span, products, walls, width, height)


def _neighbours(scene, wall):
    """The walls that meet `wall` at its ends: ghosted round it."""
    F, _Fi, length, _h = em._frame(wall)
    ends = [F @ Vector((0.0, 0.0, 0.0)), F @ Vector((length, 0.0, 0.0))]
    out = set()
    for other in em.room_walls(scene):
        if other == wall:
            continue
        Fo, _Fio, lo, _ho = em._frame(other)
        for p in (Fo @ Vector((0.0, 0.0, 0.0)),
                  Fo @ Vector((lo, 0.0, 0.0))):
            if any((p - e).length < 0.5 for e in ends):
                out.add(other.name)
    return out


# ---- The whole room ----------------------------------------------------------------

def _room_products(scene):
    names, objs = set(), []
    for wall in em.room_walls(scene):
        items = [it for it in views.wall_items(scene, wall)
                 if it.kind != 'OPENING']
        names |= em._print_owners(items, scene, molding=True)
        objs += [it.obj for it in items]
    on_walls = {o.name for o in objs}
    for obj in scene.objects:
        if (em._is_product(obj) and obj.name not in on_walls
                and em._wall_of(obj) is None and not obj.hide_render
                and obj.parent is None):
            objs.append(obj)
            names |= {obj.name} | {c.name for c in obj.children_recursive}
    return names, objs


def resolve_room(context, view, width, height):
    scene = context.scene
    names, objs = _room_products(scene)
    if not objs:
        return None
    walls = em.room_walls(scene)
    pts = []
    for obj in objs + walls:
        pts += [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    box = (min(p.x for p in pts), max(p.x for p in pts),
           min(p.y for p in pts), max(p.y for p in pts),
           min(p.z for p in pts), max(p.z for p in pts))
    F = Matrix.Identity(4)
    centre = Vector(((box[0] + box[1]) / 2.0, (box[2] + box[3]) / 2.0,
                     0.0))

    def seen(wall, C):
        """How much of the wall's room side faces the camera."""
        Fw, _Fi, length, _h = em._frame(wall)
        inward = -Fw.col[1].xyz.normalized()
        toward = C.col[2].xyz.normalized()
        mid = Fw @ Vector((length / 2.0, 0.0, 0.0))
        if inward.dot(centre - mid.to_3d()) < 0.0:
            inward = -inward                # walls drawn the other way
        return inward.dot(toward), length

    best = None
    for yaw in (YAW, -YAW, math.pi - YAW, math.pi + YAW):
        if view.get('yaw') is not None and abs(yaw - view['yaw']) > 1e-3:
            continue
        C, span = _camera(F, box, yaw)
        score = 0.0
        for wall in walls:
            facing, length = seen(wall, C)
            if facing > 0.0 and any(
                    it.kind != 'OPENING'
                    for it in views.wall_items(scene, wall)):
                score += facing * length
        if best is None or score > best[0] + 1e-6:
            best = (score, yaw, C, span)
    _score, yaw, C, span = best
    back = {w.name for w in walls if seen(w, C)[0] > 0.0}
    drawing = _draw(context, C, span, names, back, width, height)
    drawing.info['yaw'] = yaw
    return drawing


def register():
    views.register_view_kind('ISO', resolve)
    views.register_view_kind('ROOM_ISO', resolve_room)
