"""Screen-space snapping across everything visible in the scene.

Blender's own snapping lives in C (``ED_transform_snap_object_*``) and is
not reachable from Python, so this reproduces it rather than calls it.
Two things give Blender's snapping its feel, and both are copied here on
purpose:

* Candidates come from **everything on screen**, not from whichever
  polygon the cursor happens to sit on. A cabinet corner standing against
  empty space snaps as readily as one over a surface. The older
  `hb_snap.snap_to_object` could only offer the vertices of the polygon
  under the mouse, which is why corners against open air felt like a coin
  flip.
* Elements are ranked by **kind before distance** -- a vertex inside the
  radius beats an edge that is nearer in pixels. That ordering, not the
  geometry maths, is what makes a corner feel sticky.

Cost is kept down by splitting the work by what actually invalidates it,
so the part that runs on every mouse move is only comparisons:

===================  ==================================================
geometry changes     rebuild flat world-space arrays for the whole scene
view changes         project every vertex once, precompute edge terms
mouse moves          box-test, then argmin over the few survivors
===================  ==================================================

Measured on a 66 object / 8004 vertex / 19020 edge room at 1920x971:
4.9 ms rebuild, 1.2 ms per view change, 0.11 ms per mouse move. The
whole-scene approach is affordable because cabinet parts are individual
low-poly objects -- a panel is eight vertices -- so there is no need for
the per-object bounding-box broad phase this would otherwise want.
"""

import bpy
import numpy as np
from mathutils import Vector
from bpy_extras import view3d_utils


# Element kinds, in the order they win. A hit of an earlier kind beats a
# later one anywhere inside the radius, however much closer the later one
# is; see the module docstring.
PRIORITY = ('VERTEX', 'EDGE_MIDPOINT', 'EDGE', 'FACE')

# Pixel radius the cursor searches. Blender's default snap threshold is
# 10px for transform; a measuring tool is aimed by eye rather than by
# dragging an existing element, so it wants a slightly wider catch.
DEFAULT_RADIUS = 20.0

# The object currently being drawn, which must never snap to itself.
DRAW_MARKER = 'HB_CURRENT_DRAW_OBJ'

# Display modes that mean "this object is a stand-in".
HELPER_DISPLAY = {'WIRE', 'BOUNDS'}

_BEHIND = 1.0e9         # sentinel screen coord for vertices behind the camera


def is_cage(obj):
    """True where the object is tagged as a cage of any kind.

    Matched by shape rather than against a list: there are nineteen
    distinct ``*_CAGE`` markers in the add-on and more arrive with each
    product type, so a list here would silently fall behind.
    """
    for key in obj.keys():
        if key == 'IS_CAGE' or key.endswith('_CAGE'):
            return True
    return False


def is_snappable(obj):
    """True for objects worth offering as snap targets.

    Cages are decided separately, in `SnapEngine._build_geometry`, because
    the question needs the rest of the scene -- see `_containers`.
    """
    if obj.type != 'MESH':
        return False
    if obj.display_type in HELPER_DISPLAY:
        return False
    return DRAW_MARKER not in obj


def elements_from_tool_settings(scene):
    """Blender's own snap element set, translated to this module's kinds.

    Reading the scene's settings rather than keeping our own means the
    magnet menu in the header governs this snapping too -- it is not
    merely *like* Blender's, it obeys the same switches.
    """
    snap = set(scene.tool_settings.snap_elements)
    out = set()
    if 'VERTEX' in snap:
        out.add('VERTEX')
    if 'EDGE_MIDPOINT' in snap:
        out.add('EDGE_MIDPOINT')
    if 'EDGE' in snap or 'EDGE_PERPENDICULAR' in snap:
        out.add('EDGE')
    if snap & {'FACE', 'FACE_PROJECT', 'FACE_NEAREST'}:
        out.add('FACE')
    return out


class SnapHit:
    """Where a snap landed, and on what."""

    __slots__ = ('location', 'kind', 'object_name', 'distance')

    def __init__(self, location, kind, object_name, distance):
        self.location = location        # world-space Vector
        self.kind = kind                # one of PRIORITY
        self.object_name = object_name  # str or None
        self.distance = distance        # pixels from the cursor

    @property
    def object(self):
        """The object, or None if it has since been deleted.

        Resolved by name on demand rather than held: the cache can outlive
        an object by a frame, and a stale reference raises ReferenceError
        from inside a draw callback, which kills the whole overlay
        silently.
        """
        return bpy.data.objects.get(self.object_name) if self.object_name else None

    def __repr__(self):
        return (f"<SnapHit {self.kind} on {self.object_name} "
                f"at {self.distance:.1f}px>")


class SnapEngine:
    """Snap queries against the visible scene, with staged caches."""

    def __init__(self, radius=DEFAULT_RADIUS):
        self.radius = radius
        self._geo_dirty = True
        self._view_key = None
        self._scene_name = None
        self._clear_geometry()

    # -- cache lifecycle ---------------------------------------------------

    def _clear_geometry(self):
        self._objects = []      # index -> object name
        self._world = None      # (N, 3) world-space vertices
        self._vert_obj = None   # (N,)   index into _objects
        self._edges = None      # (M, 2) indices into _world
        self._suppressed = set()  # cages standing in front of their own parts
        self._clear_view()

    def _clear_view(self):
        self._view_key = None
        self._screen = None     # (N, 2) projected vertices
        self._edge_a = None     # (M, 2) projected first endpoint
        self._edge_ab = None    # (M, 2) edge vector in screen space
        self._edge_den = None   # (M,)   |ab|^2, clamped away from zero
        self._edge_mid = None   # (M, 2) projected midpoint
        self._edge_min = None   # (M, 2) screen bounding box of the edge
        self._edge_max = None

    def invalidate(self):
        """Geometry changed; drop the cached arrays."""
        self._geo_dirty = True

    # -- geometry ----------------------------------------------------------

    @staticmethod
    def _containers(candidates):
        """Names of objects that have real geometry somewhere below them.

        This is what separates a cage worth ignoring from one worth
        snapping to. A cabinet cage is an eight-vertex box around parts
        that are themselves objects, so the box is a container and the
        parts are the model -- snapping to the box lands you on the
        carcass cavity rather than on the finished end you were aiming
        at. An appliance cage has no such children: the box IS the
        dishwasher, and dropping it would make appliances unmeasurable.

        Ancestors rather than direct parents, so an intermediate empty
        does not hide the geometry from the test.
        """
        out = set()
        for obj in candidates:
            parent = obj.parent
            while parent is not None and parent.name not in out:
                out.add(parent.name)
                parent = parent.parent
        return out

    def _build_geometry(self, context):
        """Flatten every snappable object into one set of arrays.

        One array for the scene rather than one per object: the per-object
        Python loop was an order of magnitude more expensive than the
        arithmetic it was wrapping (2.0 ms against 0.19 ms for the same
        8004 vertices).
        """
        scene = context.scene
        depsgraph = context.evaluated_depsgraph_get()
        view_layer = context.view_layer

        candidates = [obj for obj in scene.objects
                      if is_snappable(obj) and obj.visible_get(view_layer=view_layer)]
        containers = self._containers(candidates)
        suppressed = {obj.name for obj in candidates
                      if obj.name in containers and is_cage(obj)}

        worlds, edges, vert_obj, names = [], [], [], []
        base = 0
        for obj in candidates:
            if obj.name in suppressed:
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.data
            count = len(mesh.vertices)
            if not count:
                continue

            co = np.empty(count * 3, dtype=np.float32)
            mesh.vertices.foreach_get('co', co)
            matrix = np.array(evaluated.matrix_world, dtype=np.float32)
            worlds.append(co.reshape(count, 3) @ matrix[:3, :3].T + matrix[:3, 3])
            vert_obj.append(np.full(count, len(names), dtype=np.int32))

            edge_count = len(mesh.edges)
            if edge_count:
                ed = np.empty(edge_count * 2, dtype=np.int32)
                mesh.edges.foreach_get('vertices', ed)
                edges.append(ed.reshape(edge_count, 2) + base)

            names.append(obj.name)
            base += count

        self._objects = names
        self._world = np.concatenate(worlds) if worlds else np.zeros((0, 3), np.float32)
        self._vert_obj = (np.concatenate(vert_obj) if vert_obj
                          else np.zeros(0, np.int32))
        self._edges = np.concatenate(edges) if edges else np.zeros((0, 2), np.int32)
        self._suppressed = suppressed
        self._geo_dirty = False
        self._scene_name = scene.name
        self._clear_view()

    # -- projection --------------------------------------------------------

    def _build_view(self, region, rv3d):
        """Project every vertex and precompute everything an edge test needs.

        All of this depends only on the view, so it is paid once per orbit
        rather than once per mouse move. What is left for the mouse is a
        box comparison and an argmin.
        """
        world = self._world
        count = world.shape[0]
        if not count:
            self._screen = np.zeros((0, 2), np.float32)
            self._edge_a = self._edge_ab = self._edge_mid = np.zeros((0, 2), np.float32)
            self._edge_min = self._edge_max = np.zeros((0, 2), np.float32)
            self._edge_den = np.zeros(0, np.float32)
            return

        matrix = np.array(rv3d.perspective_matrix, dtype=np.float32)
        hom = np.empty((count, 4), dtype=np.float32)
        hom[:, :3] = world
        hom[:, 3] = 1.0
        clip = hom @ matrix.T
        w = clip[:, 3]
        behind = w <= 1.0e-6
        safe = np.where(behind, 1.0, w)
        screen = np.stack((
            (clip[:, 0] / safe * 0.5 + 0.5) * region.width,
            (clip[:, 1] / safe * 0.5 + 0.5) * region.height,
        ), axis=1)
        # Push anything behind the camera out of reach instead of masking it
        # at every query -- it fails the box test like any distant vertex.
        screen[behind] = _BEHIND
        self._screen = screen

        e = self._edges
        if e.shape[0]:
            a = screen[e[:, 0]]
            b = screen[e[:, 1]]
            ab = b - a
            den = np.einsum('ij,ij->i', ab, ab)
            self._edge_a = a
            self._edge_ab = ab
            self._edge_den = np.where(den > 1.0e-9, den, 1.0)
            self._edge_mid = (a + b) * 0.5
            self._edge_min = np.minimum(a, b)
            self._edge_max = np.maximum(a, b)
        else:
            self._edge_a = self._edge_ab = self._edge_mid = np.zeros((0, 2), np.float32)
            self._edge_min = self._edge_max = np.zeros((0, 2), np.float32)
            self._edge_den = np.zeros(0, np.float32)

    def _ensure(self, context, region, rv3d):
        if self._geo_dirty or context.scene.name != self._scene_name:
            self._build_geometry(context)
        key = (tuple(rv3d.perspective_matrix[0]), tuple(rv3d.perspective_matrix[1]),
               tuple(rv3d.perspective_matrix[2]), tuple(rv3d.perspective_matrix[3]),
               region.width, region.height)
        if key != self._view_key:
            self._build_view(region, rv3d)
            self._view_key = key

    # -- queries -----------------------------------------------------------

    def snap(self, context, region, rv3d, mouse, elements=None, exclude=()):
        """Best snap for a cursor at `mouse`, or None.

        `mouse` is region-relative pixels. `elements` defaults to every
        kind; pass the result of `elements_from_tool_settings` to follow
        the header's magnet menu instead. `exclude` is object names to
        ignore -- the object being drawn, typically.
        """
        if elements is None:
            elements = PRIORITY
        self._ensure(context, region, rv3d)

        mx, my = float(mouse[0]), float(mouse[1])
        radius = self.radius
        skip = self._excluded_verts(exclude)

        found = {}
        if 'VERTEX' in elements:
            found['VERTEX'] = self._snap_vertex(mx, my, radius, skip)
        if {'EDGE', 'EDGE_MIDPOINT'} & set(elements):
            self._snap_edges(mx, my, radius, elements, skip, found)

        for kind in PRIORITY:
            hit = found.get(kind)
            if hit is not None:
                return hit
        if 'FACE' in elements:
            return self.ray_hit(context, region, rv3d, mouse, exclude)
        return None

    def _excluded_verts(self, exclude):
        """Boolean vertex mask for excluded objects, or None."""
        if not exclude:
            return None
        ids = [i for i, name in enumerate(self._objects) if name in exclude]
        if not ids:
            return None
        return np.isin(self._vert_obj, np.array(ids, dtype=np.int32))

    def _name_for(self, vert_index):
        oid = int(self._vert_obj[vert_index])
        return self._objects[oid] if 0 <= oid < len(self._objects) else None

    def _snap_vertex(self, mx, my, radius, skip):
        screen = self._screen
        if not screen.shape[0]:
            return None
        inside = ((screen[:, 0] > mx - radius) & (screen[:, 0] < mx + radius) &
                  (screen[:, 1] > my - radius) & (screen[:, 1] < my + radius))
        if skip is not None:
            inside &= ~skip
        idx = np.flatnonzero(inside)
        if not idx.size:
            return None
        d = np.linalg.norm(screen[idx] - (mx, my), axis=1)
        k = int(np.argmin(d))
        if d[k] >= radius:
            return None
        vi = int(idx[k])
        return SnapHit(Vector(self._world[vi].tolist()), 'VERTEX',
                       self._name_for(vi), float(d[k]))

    def _snap_edges(self, mx, my, radius, elements, skip, found):
        """Edge midpoint and perpendicular, from one shared candidate set.

        Edges are culled by their screen bounding box rather than by how
        near their endpoints are: a long wall edge crossing the cursor has
        both ends far off screen, and it is exactly the edge you want.
        """
        e = self._edges
        if not e.shape[0]:
            return
        hit = ((self._edge_min[:, 0] <= mx + radius) &
               (self._edge_max[:, 0] >= mx - radius) &
               (self._edge_min[:, 1] <= my + radius) &
               (self._edge_max[:, 1] >= my - radius))
        if skip is not None:
            hit &= ~(skip[e[:, 0]] | skip[e[:, 1]])
        idx = np.flatnonzero(hit)
        if not idx.size:
            return

        world = self._world
        if 'EDGE_MIDPOINT' in elements:
            d = np.linalg.norm(self._edge_mid[idx] - (mx, my), axis=1)
            k = int(np.argmin(d))
            if d[k] < radius:
                edge = e[idx[k]]
                mid = (world[edge[0]] + world[edge[1]]) * 0.5
                found['EDGE_MIDPOINT'] = SnapHit(
                    Vector(mid.tolist()), 'EDGE_MIDPOINT',
                    self._name_for(int(edge[0])), float(d[k]))

        if 'EDGE' in elements:
            a = self._edge_a[idx]
            ab = self._edge_ab[idx]
            t = np.clip(np.einsum('ij,ij->i', (mx, my) - a, ab) / self._edge_den[idx],
                        0.0, 1.0)
            d = np.linalg.norm(a + t[:, None] * ab - (mx, my), axis=1)
            k = int(np.argmin(d))
            if d[k] < radius:
                edge = e[idx[k]]
                v0 = world[edge[0]]
                loc = v0 + float(t[k]) * (world[edge[1]] - v0)
                found['EDGE'] = SnapHit(
                    Vector(loc.tolist()), 'EDGE',
                    self._name_for(int(edge[0])), float(d[k]))

    def ray_hit(self, context, region, rv3d, mouse, exclude=()):
        """Surface hit under the cursor -- the fallback when nothing snaps.

        Cages are refused here too. A cabinet cage is a solid box standing
        in front of the parts it contains, so a ray reaches it first and
        every face snap inside a cabinet would land on the envelope.
        """
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse)
        result, location, _normal, _index, obj, _matrix = context.scene.ray_cast(
            context.evaluated_depsgraph_get(), origin, direction)
        if not result or obj is None:
            return None
        if obj.name in exclude or obj.name in self._suppressed:
            return None
        if not is_snappable(obj):
            return None
        return SnapHit(location.copy(), 'FACE', obj.name, 0.0)


# One engine for the add-on: the caches are keyed on the scene and the
# view, so every tool can share them and a second tool costs nothing.
_engine = None


def engine():
    global _engine
    if _engine is None:
        _engine = SnapEngine()
    return _engine


@bpy.app.handlers.persistent
def _invalidate_on_update(scene, depsgraph):
    if _engine is not None:
        _engine.invalidate()


@bpy.app.handlers.persistent
def _invalidate_on_load(*args):
    if _engine is not None:
        _engine.invalidate()


def register():
    if _invalidate_on_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_invalidate_on_update)
    if _invalidate_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_invalidate_on_load)


def unregister():
    if _invalidate_on_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_invalidate_on_update)
    if _invalidate_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_invalidate_on_load)
