"""Wall elevation mode: work on one wall face-on, dimensioned like a drawing.

Show Elevation turns the room view into an elevation of one wall. The
wall and what stands in front of it stay on screen, everything else is
hidden, the view goes orthographic square to the wall with its rotation
locked, and the wall is dimensioned the way an elevation sheet is:

- below the floor line, a chain of the floor-standing products and the
  gaps between them, then the overall wall length;
- above the wall, a chain of the uppers and talls, and one of the
  windows and doors;
- on the right, a height chain (counter, upper bottom, upper top, wall
  height) with the overall height outside it; on the left, the window
  and door sill / head heights. With Heights Both Sides on (the bar's
  toggle), each side's height chain dims the products on its half of
  the wall, so a tall at one end and uppers at the other both read;
- with Face Frame on, each face frame cabinet's stiles and openings
  across its top and its rails and openings up each opening column.

Dimensions are drawn the way a drafter draws them: extension lines that
stand off the work, a dimension line, a 45 degree architectural tick at
each end and the value sitting on the line (vertical values read from
the right). Tiers stand off the model in SCREEN pixels, so they stay
the same distance from the work at any zoom, and a value too wide for
its space steps outside its extension lines instead of crossing them.

A width or gap can be clicked and typed, same grammar as placement
(inches, fractions, feet'inches"): a product's width resizes it, a gap
moves the product beside it (the selected one when one is, else the
one to the right of the gap). Heights work the same way up the side
chains (see _vertical_target): a segment that is products' own height
resizes them, a gap moves the hanging products beside it, the overall
height is the wall's. A selected product also shows its own height.
The overall length is read-only.

While an elevation is up, placement is locked to that wall
(constrain_snap(), called from PlacementMixin.update_snap): wherever the
cursor is, a product lands on this wall. The view's own placement
preview is dimensioned live, so a cabinet being placed shows its gaps
to its neighbours as it moves.

Leave with Esc, the Exit button on the elevation bar, or the HUD View
toggle; Left / Right arrows (or the bar's arrows) step to the next wall
of the room without leaving. Exiting puts back exactly what it hid (by
an id-prop tag, so a save made mid-elevation is cleaned up on load) and
the view the room had before.
"""

import math

import bpy
import blf
import gpu
from mathutils import Vector, Euler
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from .. import hb_types
from .. import units
from .. import hb_dim_style
from ..hb_icons import icon_glyph
from ..hb_gpu_draw import (get_visible_window_bounds, draw_round_rect,
                           draw_soft_shadow, draw_glyphs, draw_lines,
                           point_in_rect)
from ..hb_gpu_ui import Theme, scale as _ui_scale

# ---- Style ---------------------------------------------------------------

FONT_SIZE = 12
LINE = (0.93, 0.93, 0.93, 0.92)
TEXT = (1.0, 1.0, 1.0, 1.0)
TEXT_READONLY = (0.86, 0.86, 0.86, 1.0)
HOVER = (0.45, 0.72, 1.0, 1.0)
HOVER_TEXT = (0.80, 0.91, 1.0, 1.0)   # reads on a light face too
EDIT_BG = Theme.ACCENT_BG
FLOOR_LINE = (0.93, 0.93, 0.93, 0.85)
PREVIEW = (1.0, 0.62, 0.20, 1.0)

FIRST_TIER_PX = 30      # geometry to the first dimension line
TIER_PX = 30            # between stacked dimension lines
EXT_GAP_PX = 5          # extension line stands off the geometry
EXT_OVER_PX = 5         # and runs past the dimension line
TICK_PX = 4.5           # half-length of the 45 degree tick, per axis
TEXT_GAP_PX = 4         # value above its line

# Products below this off the floor are floor standing (bases, talls,
# appliances); anything higher hangs (uppers, hoods).
FLOOR_STANDING_Z = units.inch(12.0)
# A floor-standing product this tall also joins the upper chain.
TALL_Z = units.inch(60.0)
# Chain breaks and levels closer than this merge.
MERGE = units.inch(1.0 / 32.0)
# What counts as standing in front of the wall: its centre at most this
# far out from the wall face (and not behind it).
FRONT_DEPTH = 1.0

PRODUCT_MARKERS = (
    'IS_FACE_FRAME_CABINET_CAGE', 'IS_FRAMELESS_CABINET_CAGE',
    'IS_APPLIANCE', 'IS_CLOSET_STARTER_CAGE', 'IS_VOIDED_CORNER',
    'IS_OBSTACLE')
OPENING_MARKERS = ('IS_WINDOW_BP', 'IS_ENTRY_DOOR_BP')

HIDE_TAG = 'HB_ELEVATION_HIDDEN'

# ---- Module state ----------------------------------------------------------

# {'scene', 'wall', 'r3d' (as_pointer), 'view' (saved r3d state),
#  'extra' (names of in-front roots not parented to the wall),
#  'preview' (names the running placement owns), 'fit' (passes left)}
_state = None
_edit = None            # {'index': dim key, 'typed': str, 'owner': id}
_mouse = (-1, -1)
_hover = None           # dim key or bar part under the cursor
_gen = 0
_item_cache = {}
_draw_handle = None
_addon_keymaps = []


def _s():
    try:
        return _ui_scale()
    except Exception:
        return 1.0


@bpy.app.handlers.persistent
def _bump_gen(*_args):
    global _gen
    _gen += 1


# ---- Wall frame ------------------------------------------------------------

def _wall_dims(wall_obj):
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return None
    try:
        return (wall.get_input('Length'), wall.get_input('Height'),
                wall.get_input('Thickness'))
    except Exception:
        return None


def _frame(wall_obj):
    """(F, F inverse, length, height): the frame the wall's elevation
    sheet is built in -- x runs 0..length left to right as the viewer sees it,
    z up, -y towards the viewer, y = 0 the face the product hangs on."""
    dims = _wall_dims(wall_obj)
    if dims is None:
        return None
    from .. import hb_layouts
    length, height, thickness = dims
    F = hb_layouts.wall_view_frame(wall_obj, length, thickness)
    return F, F.inverted_safe(), length, height


def _wall_of(obj):
    while obj is not None:
        if obj.get('IS_WALL_BP'):
            return obj
        obj = obj.parent
    return None


def room_walls(scene):
    """The room's straight walls, in drawing order where they chain."""
    walls = [o for o in scene.objects if o.get('IS_WALL_BP')
             and _wall_dims(o) is not None and not hb_types.is_curved_wall(o)]
    if not walls:
        return []
    by_name = {w.name: w for w in walls}

    def nxt(w):
        try:
            node = hb_types.GeoNodeWall(w).get_connected_wall('right')
        except Exception:
            return None
        return node.obj if node is not None else None

    def prv(w):
        try:
            node = hb_types.GeoNodeWall(w).get_connected_wall('left')
        except Exception:
            return None
        return node.obj if node is not None else None

    ordered, seen = [], set()
    for start in sorted(walls, key=lambda w: w.name):
        if start.name in seen:
            continue
        # Walk back to the head of this chain (a closed loop stops where
        # it started).
        head, guard = start, 0
        while guard < len(walls):
            p = prv(head)
            if p is None or p.name not in by_name or p == start:
                break
            head, guard = p, guard + 1
        w, guard = head, 0
        while w is not None and w.name not in seen and guard <= len(walls):
            seen.add(w.name)
            ordered.append(w)
            w, guard = nxt(w), guard + 1
            if w is not None and w.name not in by_name:
                w = None
    return ordered


def active_wall(context=None):
    """The wall an elevation is showing in this scene, or None."""
    if _state is None:
        return None
    scene = (context or bpy.context).scene
    if scene is None or scene.name != _state['scene']:
        return None
    return bpy.data.objects.get(_state['wall'])


def is_active(context=None):
    return active_wall(context) is not None


# ---- View ------------------------------------------------------------------

def _find_r3d(pointer):
    wm = bpy.context.window_manager
    for win in wm.windows:
        for area in win.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            space = area.spaces.active
            r3d = getattr(space, 'region_3d', None)
            if r3d is not None and r3d.as_pointer() == pointer:
                return area, r3d
    return None, None


def _save_view(r3d):
    return {
        'location': r3d.view_location.copy(),
        'rotation': r3d.view_rotation.copy(),
        'distance': r3d.view_distance,
        'perspective': r3d.view_perspective,
        'lock_rotation': r3d.lock_rotation,
        'side_view': getattr(r3d, 'is_orthographic_side_view', False),
    }


def _restore_view(r3d, view):
    r3d.lock_rotation = view['lock_rotation']
    r3d.view_rotation = view['rotation']
    r3d.view_location = view['location']
    r3d.view_distance = view['distance']
    r3d.view_perspective = view['perspective']
    try:
        r3d.is_orthographic_side_view = view['side_view']
    except Exception:
        pass


def _aim(r3d, wall_obj):
    fr = _frame(wall_obj)
    if fr is None:
        return
    F, _Fi, length, height = fr
    rot = F.to_3x3().normalized().to_quaternion()
    r3d.lock_rotation = False
    r3d.view_perspective = 'ORTHO'
    r3d.view_rotation = rot @ Euler((math.pi / 2.0, 0.0, 0.0)).to_quaternion()
    r3d.view_location = F @ Vector((length / 2.0, 0.0, height / 2.0))
    # A first guess; the draw pass measures and refits (see _fit_step).
    r3d.view_distance = max(length, height) * 1.6
    try:
        r3d.is_orthographic_side_view = True
    except Exception:
        pass
    # Orbit becomes pan: the elevation stays square to the wall.
    r3d.lock_rotation = True


def _clear_of_hud(area, xmin, xmax):
    """The visible span narrowed to what the HUD leaves open: the pinned
    panel and the room tool palette on the left, the selection inspector
    on the right. The left window chain would otherwise sit under them."""
    context = bpy.context
    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    try:
        with context.temp_override(area=area, region=region):
            from . import viewport_hud, room_palette, selection_inspector
            ctx = bpy.context
            xmin = max(xmin, viewport_hud.left_inset(ctx, area))
            if room_palette._palette_active(ctx):
                rows = room_palette.compute_layout(area)
                if rows:
                    xmin = max(xmin, max(r[0] + r[2] for _k, _p, r in rows))
            box = selection_inspector.rect(ctx, area)
            if box is not None and box[0] > (xmin + xmax) / 2.0:
                xmax = min(xmax, box[0])
    except Exception as exc:
        print("Elevation fit HUD span:", exc)
    return xmin, xmax


def _fit_step(area, region, r3d):
    """Measure the wall on screen and scale / centre it into the visible
    region with room for the dimensions. Runs from a timer the draw
    handler queues (the projection is only current after a draw)."""
    if _state is None:
        return
    wall = bpy.data.objects.get(_state['wall'])
    fr = _frame(wall) if wall else None
    if fr is None:
        _state['fit'] = 0
        return
    F, _Fi, length, height = fr
    p0 = view3d_utils.location_3d_to_region_2d(
        region, r3d, F @ Vector((0.0, 0.0, 0.0)))
    p1 = view3d_utils.location_3d_to_region_2d(
        region, r3d, F @ Vector((length, 0.0, height)))
    if p0 is None or p1 is None:
        _state['fit'] = 0
        return
    cur_w, cur_h = abs(p1.x - p0.x), abs(p1.y - p0.y)
    if cur_w < 1 or cur_h < 1:
        _state['fit'] = 0
        return
    s = _s()
    xmin, xmax, ymin, ymax = get_visible_window_bounds(area)
    xmin, xmax = _clear_of_hud(area, xmin, xmax)
    # Room for two dimension tiers each side, the HUD rows above and the
    # elevation bar below.
    side = 120 * s
    top = 150 * s
    bottom = 130 * s
    avail_w = max(100.0, (xmax - xmin) - 2 * side)
    avail_h = max(100.0, (ymax - ymin) - top - bottom)
    k = min(avail_w / cur_w, avail_h / cur_h)
    px_per_m = cur_w / length
    # Centre the wall in the space left for it.
    want_x = (xmin + xmax) / 2.0
    want_y = ymin + bottom + avail_h / 2.0
    have_x = (p0.x + p1.x) / 2.0
    have_y = (p0.y + p1.y) / 2.0
    dx = (have_x - want_x) / px_per_m
    dz = (have_y - want_y) / px_per_m
    axis_x = F.to_3x3().normalized() @ Vector((1.0, 0.0, 0.0))
    r3d.view_location = (r3d.view_location + axis_x * dx
                         + Vector((0.0, 0.0, dz)))
    # Scaling the distance scales about the view centre, so centre first.
    r3d.view_distance = r3d.view_distance / k
    _state['fit'] -= 1
    area.tag_redraw()


def _queue_fit(area, region, r3d):
    ptr = r3d.as_pointer()

    def run():
        a, r = _find_r3d(ptr)
        if a is None:
            return None
        for reg in a.regions:
            if reg.type == 'WINDOW':
                try:
                    _fit_step(a, reg, r)
                except Exception as exc:
                    print("Elevation fit:", exc)
                    if _state is not None:
                        _state['fit'] = 0
                break
        return None
    bpy.app.timers.register(run, first_interval=0.0)


# ---- Isolation ---------------------------------------------------------------

def _center_local(obj, Fi):
    try:
        mw = obj.matrix_world
        pts = [Fi @ (mw @ Vector(c)) for c in obj.bound_box]
    except Exception:
        return None
    return sum(pts, Vector()) / 8.0


def _in_front_roots(scene, wall, Fi, length, height):
    """Roots that stand in front of the wall without being parented to
    it -- a countertop, an island end, a corner cabinet off the next wall
    that shows in this one's elevation."""
    roots = []
    for obj in scene.objects:
        if obj == wall or obj.get('IS_WALL_BP') or obj.get('obj_x'):
            continue
        parent = obj.parent
        if parent is not None and not parent.get('IS_WALL_BP'):
            continue
        if parent == wall:
            continue
        if obj.type in {'CAMERA', 'LIGHT'}:
            continue
        c = _center_local(obj, Fi)
        if c is None:
            continue
        if (0.0 <= c.x <= length and -FRONT_DEPTH <= c.y <= 0.05
                and -0.05 <= c.z <= height + 0.3):
            roots.append(obj)
    return roots


def _isolate(context, wall):
    fr = _frame(wall)
    _F, Fi, length, height = fr
    scene = context.scene
    extra = _in_front_roots(scene, wall, Fi, length, height)
    keep = {wall}
    keep.update(wall.children_recursive)
    for root in extra:
        keep.add(root)
        keep.update(root.children_recursive)
    view_layer = context.view_layer
    for obj in scene.objects:
        if obj in keep or obj.type in {'CAMERA', 'LIGHT'}:
            continue
        if view_layer.objects.get(obj.name) is None:
            continue
        if obj.hide_get() or obj.hide_viewport:
            continue
        obj.hide_set(True)
        obj[HIDE_TAG] = True
    return [o.name for o in extra]


def _unisolate(scene):
    for obj in scene.objects:
        if obj.get(HIDE_TAG):
            try:
                obj.hide_set(False)
            except Exception:
                pass
            del obj[HIDE_TAG]


# ---- Enter / exit ------------------------------------------------------------

def pick_wall(context):
    """The wall to show: the selection's, else the one the view faces."""
    obj = context.active_object
    wall = _wall_of(obj)
    if wall is None:
        for o in context.selected_objects:
            wall = _wall_of(o)
            if wall is not None:
                break
    walls = room_walls(context.scene)
    if wall is not None and wall in walls:
        return wall
    rv3d = getattr(context, 'region_data', None)
    if rv3d is None or not walls:
        return walls[0] if walls else None
    view_dir = rv3d.view_rotation @ Vector((0.0, 0.0, -1.0))
    view_dir.z = 0.0
    centre = rv3d.view_location
    best, best_score = None, None
    for w in walls:
        fr = _frame(w)
        if fr is None:
            continue
        F, _Fi, length, height = fr
        facing = F.to_3x3().normalized() @ Vector((0.0, 1.0, 0.0))
        dot = (view_dir.normalized().dot(facing)
               if view_dir.length > 1e-6 else 0.0)
        mid = F @ Vector((length / 2.0, 0.0, 0.0))
        dist = (Vector((mid.x - centre.x, mid.y - centre.y))).length
        score = dot * 3.0 - dist * 0.2
        if best_score is None or score > best_score:
            best, best_score = w, score
    return best


def enter(context, wall, keep_view=None):
    """Show ``wall`` in elevation in the context's 3D view."""
    global _state
    area = context.area
    if area is None or area.type != 'VIEW_3D':
        return False
    r3d = area.spaces.active.region_3d
    if _frame(wall) is None:
        return False
    saved = keep_view if keep_view is not None else _save_view(r3d)
    if _state is not None:
        scene = bpy.data.scenes.get(_state['scene'])
        if scene is not None:
            _unisolate(scene)
    extra = _isolate(context, wall)
    _state = {'scene': context.scene.name, 'wall': wall.name,
              'r3d': r3d.as_pointer(), 'view': saved, 'extra': extra,
              'preview': set(), 'fit': 2}
    _aim(r3d, wall)
    _bump_gen()
    area.tag_redraw()
    return True


def leave(context=None, restore_view=True):
    global _state, _edit
    if _state is None:
        return
    st, _state, _edit = _state, None, None
    scene = bpy.data.scenes.get(st['scene'])
    if scene is not None:
        _unisolate(scene)
    area, r3d = _find_r3d(st['r3d'])
    if r3d is not None:
        if restore_view:
            _restore_view(r3d, st['view'])
        else:
            r3d.lock_rotation = st['view']['lock_rotation']
        area.tag_redraw()


def step(context, direction):
    wall = active_wall(context)
    if wall is None:
        return False
    walls = room_walls(context.scene)
    if len(walls) < 2 or wall not in walls:
        return False
    i = (walls.index(wall) + direction) % len(walls)
    return enter(context, walls[i], keep_view=_state['view'])


# ---- Placement lock ------------------------------------------------------------

def constrain_snap(op, context):
    """Called by PlacementMixin.update_snap: in an elevation, every hit
    lands on the elevation's wall. A hit on the wall or something on it
    is kept (cabinet-to-cabinet snapping still works); anything else --
    empty space, a hidden floor -- becomes the point on the wall's face
    under the cursor."""
    if _state is None:
        return
    wall = active_wall(context)
    if wall is None:
        return
    names = set()
    for obj in (getattr(op, 'placement_objects', None) or ()):
        try:
            names.add(obj.name)
        except Exception:
            pass
    cage = getattr(op, '_preview_cage', None)
    cage_obj = getattr(cage, 'obj', None)
    if cage_obj is not None:
        try:
            names.add(cage_obj.name)
        except Exception:
            pass
    _state['preview'] = names

    hit = getattr(op, 'hit_object', None)
    if hit is not None and _wall_of(hit) == wall \
            and getattr(op, 'hit_location', None) is not None:
        return
    region = getattr(op, 'region', None)
    rv3d = getattr(region, 'data', None) if region is not None else None
    mouse = getattr(op, 'mouse_pos', None)
    if rv3d is None or mouse is None:
        return
    fr = _frame(wall)
    if fr is None:
        return
    F, Fi, length, height = fr
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse)
    normal = F.to_3x3().normalized() @ Vector((0.0, 1.0, 0.0))
    p = intersect_line_plane(origin, origin + direction * 1000.0,
                             F.translation, normal)
    if p is None:
        return
    local = Fi @ p
    local.x = min(max(local.x, 0.0), length)
    local.z = min(max(local.z, 0.0), height)
    # A hair off the face, on the viewer's side, so a side test reads it
    # as this face.
    local.y = -0.001
    op.hit_object = wall
    op.hit_location = F @ local
    if hasattr(op, 'curved_wall_hit'):
        op.curved_wall_hit = None


# ---- What is on the wall -----------------------------------------------------------

class _Item:
    __slots__ = ('obj', 'name', 'x0', 'x1', 'z0', 'z1', 'kind', 'tall',
                 'movable', 'width_edit', 'preview')


def _is_product(obj):
    return any(obj.get(m) for m in PRODUCT_MARKERS)


def _is_opening(obj):
    return any(obj.get(m) for m in OPENING_MARKERS)


def _width_editor(obj):
    if obj.get('IS_FACE_FRAME_CABINET_CAGE') or obj.get(
            'IS_FRAMELESS_CABINET_CAGE') or obj.get('IS_APPLIANCE'):
        return True
    return False


def _height_editor(obj):
    return _width_editor(obj) or _is_opening(obj)


def _make_item(obj, Fi, wall, preview=False):
    try:
        mw = obj.matrix_world
        pts = [Fi @ (mw @ Vector(c)) for c in obj.bound_box]
    except Exception:
        return None
    xs = [p.x for p in pts]
    zs = [p.z for p in pts]
    if max(xs) - min(xs) < MERGE or max(zs) - min(zs) < MERGE:
        return None
    it = _Item()
    it.obj, it.name = obj, obj.name
    it.x0, it.x1, it.z0, it.z1 = min(xs), max(xs), min(zs), max(zs)
    it.preview = preview
    if _is_opening(obj):
        it.kind = 'OPENING'
    elif it.z0 < FLOOR_STANDING_Z:
        it.kind = 'LOWER'
    else:
        it.kind = 'UPPER'
    it.tall = it.kind == 'LOWER' and it.z1 > TALL_Z
    # Square to the wall and hung straight off it: a typed gap can slide
    # it, a typed width can resize it.
    try:
        rel = (wall.matrix_world.inverted_safe() @ mw).to_euler()
        square = abs(math.sin(rel.z)) < 0.02
    except Exception:
        square = False
    it.movable = (not preview) and obj.parent == wall and square
    it.width_edit = it.movable and _width_editor(obj)
    return it


def _items(scene, wall):
    key = (_gen, wall.name, frozenset(_state.get('preview', ())))
    hit = _item_cache.get('key')
    if hit == key:
        return _item_cache['items']
    fr = _frame(wall)
    items = []
    if fr is not None:
        _F, Fi, length, _height = fr
        roots = list(wall.children)
        for name in _state.get('extra', ()):
            obj = bpy.data.objects.get(name)
            if obj is not None:
                roots.append(obj)
        cands = []
        for obj in roots:
            if obj.get('IS_CAGE_GROUP'):
                cands.extend(c for c in obj.children if _is_product(c))
            elif _is_product(obj) or _is_opening(obj):
                cands.append(obj)
        preview = set(_state.get('preview', ()))
        for obj in cands:
            if obj.name in preview:
                continue
            try:
                if not obj.visible_get() and not obj.display_type == 'WIRE' \
                        and obj.hide_get():
                    continue
            except Exception:
                continue
            it = _make_item(obj, Fi, wall)
            if it is not None and it.x1 > 0.0 and it.x0 < length:
                items.append(it)
        for name in preview:
            obj = bpy.data.objects.get(name)
            if obj is None or obj.get('IS_WALL_BP'):
                continue
            if not (obj.get('HB_CURRENT_DRAW_OBJ') or _is_product(obj)
                    or _is_opening(obj)):
                continue
            if obj.parent is not None and obj.parent.name in preview:
                continue
            it = _make_item(obj, Fi, wall, preview=True)
            if it is not None and it.x1 > 0.0 and it.x0 < length:
                items.append(it)
    _item_cache['key'] = key
    _item_cache['items'] = items
    return items


# ---- Text ----------------------------------------------------------------------

def format_length(scene, value):
    us = scene.unit_settings
    if us.system == 'IMPERIAL' and us.length_unit != 'FEET':
        n = int(round(units.meter_to_inch(value) * 16.0))
        neg = n < 0
        n = abs(n)
        whole, rem = divmod(n, 16)
        den = 16
        while rem and rem % 2 == 0:
            rem //= 2
            den //= 2
        if rem and whole:
            txt = f'{whole} {rem}/{den}"'
        elif rem:
            txt = f'{rem}/{den}"'
        else:
            txt = f'{whole}"'
        return ('-' + txt) if neg else txt
    return units.unit_to_string(us, value)


# ---- Dimension layout ------------------------------------------------------------
# A dim: dict(axis 'H'|'V', a, b (screen coords along the axis),
#   pos (the line's other coord), ext ((p, q) screen segments),
#   value, text, rect, target, item, key)

def _chain(edges, lo, hi):
    """Sorted unique break points in [lo, hi] (ends included)."""
    pts = sorted({min(max(e, lo), hi) for e in edges} | {lo, hi})
    out = []
    for p in pts:
        if not out or p - out[-1] > MERGE:
            out.append(p)
        else:
            out[-1] = max(out[-1], p) if p == hi else out[-1]
    return out


def _segment_target(items, x0, x1, selected):
    """What a typed value on the chain segment x0..x1 changes."""
    for it in items:
        if abs(it.x0 - x0) <= MERGE and abs(it.x1 - x1) <= MERGE:
            if it.width_edit:
                return {'mode': 'WIDTH', 'obj': it.name}
            return None
    # A gap: the item ending at x0 (left) and starting at x1 (right).
    covered = any(it.x0 < x1 - MERGE and it.x1 > x0 + MERGE for it in items)
    if covered:
        return None
    left = [it for it in items if abs(it.x1 - x0) <= MERGE]
    right = [it for it in items if abs(it.x0 - x1) <= MERGE]
    left = left[0] if len(left) == 1 else None
    right = right[0] if len(right) == 1 else None
    pick, sign = None, 0
    if right is not None and right.name in selected and right.movable:
        pick, sign = right, 1
    elif left is not None and left.name in selected and left.movable:
        pick, sign = left, -1
    elif right is not None and right.movable:
        pick, sign = right, 1
    elif left is not None and left.movable:
        pick, sign = left, -1
    if pick is None:
        return None
    return {'mode': 'GAP', 'obj': pick.name, 'sign': sign}


def _vertical_target(group, a, b, wall_name=None):
    """What a typed value on the height segment a..b changes.

    A segment that is exactly some products' height resizes them (their
    bottoms stay put). A gap moves the hanging products beside it: the
    ones sitting on its top line move to keep the gap as typed, else the
    ones hanging from its bottom line. Floor-standing products are never
    lifted, but a tall whose top is on that bottom line grows or shrinks
    with it, so the clearance above uppers and talls is one number. ``wall_name`` marks the overall height, which is the wall's."""
    if wall_name is not None:
        return {'mode': 'WALL_H', 'obj': wall_name}
    spans = [it for it in group if not it.preview
             and abs(it.z0 - a) <= MERGE and abs(it.z1 - b) <= MERGE
             and _height_editor(it.obj)]
    if spans:
        return {'mode': 'HEIGHT', 'objs': [it.name for it in spans],
                'item': spans[0]}

    def hangs(it):
        return it.kind in ('UPPER', 'OPENING') and it.movable

    above = [it for it in group if hangs(it) and abs(it.z0 - b) <= MERGE]
    if above:
        return {'mode': 'LIFT', 'objs': [it.name for it in above], 'sign': 1}
    below = [it for it in group if hangs(it) and abs(it.z1 - a) <= MERGE]
    talls = [it for it in group if it.tall and not hangs(it)
             and not it.preview and abs(it.z1 - a) <= MERGE
             and _height_editor(it.obj)]
    if below or talls:
        return {'mode': 'LIFT', 'objs': [it.name for it in below],
                'grow': [(it.name, it.z1 - it.z0) for it in talls],
                'sign': -1}
    return None


# ---- What the view shows -----------------------------------------------------------
# Toggled from the elevation bar, kept on the scene so a file reopens
# showing what it was left showing.

SHOW_PROP = 'HB_ELEVATION_SHOW'
SHOW_OPTIONS = (
    # (key, bar label, default)
    ('BOTH_HEIGHTS', "Heights Both Sides", True),
    ('FACE_FRAME', "Face Frame", False),
)


def show_option(scene, key):
    default = next((d for k, _l, d in SHOW_OPTIONS if k == key), False)
    try:
        group = scene.get(SHOW_PROP)
        if group is not None and key in group:
            return bool(group[key])
    except Exception:
        pass
    return default


def toggle_show_option(scene, key):
    value = not show_option(scene, key)
    group = scene.get(SHOW_PROP)
    if group is None:
        scene[SHOW_PROP] = {}
        group = scene[SHOW_PROP]
    group[key] = value
    _bump_gen()
    return value


def _height_levels(group, height):
    """The height chain for some products: floor, counter line (the base
    cabinets' top; a dishwasher or range a fraction under it is not a
    level of its own), upper bottoms and tops, tall tops, wall height."""
    levels = {0.0, height}
    lows = [it for it in group if it.kind == 'LOWER' and not it.tall]
    base_tops = [it.z1 for it in lows if not it.obj.get('IS_APPLIANCE')] \
        or [it.z1 for it in lows]
    if base_tops:
        levels.add(max(base_tops))
    for it in group:
        if it.kind == 'UPPER':
            levels.update((it.z0, it.z1))
        elif it.tall:
            levels.add(it.z1)
    return _chain(levels, 0.0, max(levels))


# A face frame's own dims stand this far inside its edges, in pixels.
FF_INSET_PX = 16
# A face frame narrower than this on screen gets no dims of its own.
FF_MIN_PX = 70


def _merge(spans):
    out = []
    for a, b in sorted(spans):
        if out and a <= out[-1][1] + MERGE:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _face_frame_boxes(cabinet, Fi):
    """(x0, x1, z0, z1) in the wall frame of each built face frame member
    of a face frame cabinet (stiles, rails, mid stiles and rails)."""
    try:
        from ..product_libraries.face_frame import dim_edit_overlay as ffo
        parts = list(ffo._iter_face_frame_parts(cabinet))
    except Exception:
        return []
    boxes = []
    for part in parts:
        try:
            mw = part.matrix_world
            pts = [Fi @ (mw @ Vector(c)) for c in part.bound_box]
        except Exception:
            continue
        xs = [p.x for p in pts]
        zs = [p.z for p in pts]
        if max(xs) - min(xs) < MERGE or max(zs) - min(zs) < MERGE:
            continue
        boxes.append((min(xs), max(xs), min(zs), max(zs)))
    return boxes


def _face_frame_dims(items, dims, sx, sy, s, Fi):
    """Each face frame cabinet's frame, dimensioned on its face: across
    the top, the stiles and the openings between them; up each opening
    column, the rails and the openings between them. Read only (a frame
    member is sized from its own labels or the cabinet's dialog)."""
    inset = FF_INSET_PX * s
    for it in items:
        if it.preview or not it.obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            continue
        if abs(sx(it.x1) - sx(it.x0)) < FF_MIN_PX * s:
            continue
        boxes = _face_frame_boxes(it.obj, Fi)
        if not boxes:
            continue
        fx0 = min(b[0] for b in boxes)
        fx1 = max(b[1] for b in boxes)
        fz0 = min(b[2] for b in boxes)
        fz1 = max(b[3] for b in boxes)
        verticals = [b for b in boxes if (b[3] - b[2]) > (b[1] - b[0])]
        rails = [b for b in boxes if (b[3] - b[2]) <= (b[1] - b[0])]
        stiles = _merge([(b[0], b[1]) for b in verticals])
        # Across the top: stile, opening, stile ...
        xs = _chain([v for a, b in stiles for v in (a, b)], fx0, fx1)
        y = sy(fz1) - inset
        for a, b in zip(xs, xs[1:]):
            dims.append({'axis': 'H', 'a': sx(a), 'b': sx(b), 'pos': y,
                         'side': -1, 'value': b - a, 'target': None,
                         'item': it, 'w0': a,
                         'key': ('FF_W', it.name, round(a, 4))})
        # Up each opening column: rail, opening, rail ...
        cols = []
        prev = fx0
        for a, b in stiles:
            if a - prev > MERGE:
                cols.append((prev, a))
            prev = max(prev, b)
        if fx1 - prev > MERGE:
            cols.append((prev, fx1))
        for c0, c1 in cols:
            if abs(sx(c1) - sx(c0)) < 2 * inset:
                continue
            mid = (c0 + c1) / 2.0
            spans = _merge([(b[2], b[3]) for b in rails
                            if b[0] <= mid <= b[1]])
            zs = _chain([v for a, b in spans for v in (a, b)], fz0, fz1)
            if len(zs) < 3:
                continue
            x = sx(c0) + inset
            for a, b in zip(zs, zs[1:]):
                dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': x,
                             'side': 1, 'value': b - a, 'target': None,
                             'item': it, 'w0': a,
                             'key': ('FF_H', it.name, round(c0, 4),
                                     round(a, 4))})


def _layout(context, region, rv3d):
    """Every dimension on screen, its text placed. Shared by draw and
    click so hits cannot drift from pixels."""
    wall = active_wall(context)
    if wall is None or rv3d is None:
        return [], None
    fr = _frame(wall)
    if fr is None:
        return [], None
    F, _Fi, length, height = fr
    scene = context.scene
    s = _s()
    items = _items(scene, wall)
    selected = {o.name for o in context.selected_objects}

    def P(x, z):
        p = view3d_utils.location_3d_to_region_2d(
            region, rv3d, F @ Vector((x, 0.0, z)))
        return p if p is not None else Vector((0.0, 0.0))

    o = P(0.0, 0.0)
    e = P(length, height)
    if abs(e.x - o.x) < 20 or abs(e.y - o.y) < 20:
        return [], None
    px = (e.x - o.x) / length          # screen px per metre (signed)

    def sx(x):
        return o.x + x * px

    def sy(z):
        return o.y + z * (e.y - o.y) / height

    # The wall's own outline runs past 0..length at a mitred corner;
    # tiers stand off what is actually drawn.
    wx0, wx1 = 0.0, length
    try:
        mw = wall.matrix_world
        Fi = fr[1]
        xs = [(Fi @ (mw @ Vector(c))).x for c in wall.bound_box]
        wx0, wx1 = min(min(xs), 0.0), max(max(xs), length)
    except Exception:
        pass
    first = FIRST_TIER_PX * s
    tier = TIER_PX * s
    gap = EXT_GAP_PX * s
    over = EXT_OVER_PX * s
    dims = []

    def add_h(points, pos, from_y, side, value_items, read_only=False,
              item_of=None):
        """A horizontal chain at screen y ``pos``. ``from_y(x)`` is the
        geometry edge an extension line at x stands off; ``side`` -1
        below the work, +1 above it."""
        for x in points:
            fy = from_y(x)
            dims_ext.append(((sx(x), fy + side * gap),
                             (sx(x), pos + side * over)))
        for a, b in zip(points, points[1:]):
            target = None if read_only else _segment_target(
                value_items, a, b, selected)
            item = item_of(a, b) if item_of else None
            dims.append({'axis': 'H', 'a': sx(a), 'b': sx(b), 'pos': pos,
                         'side': side, 'value': b - a, 'target': target,
                         'item': item, 'w0': a})

    def add_v(levels, pos, side, group, overall=False):
        for z in levels:
            ex = sx(wx1) if side > 0 else sx(wx0)
            dims_ext.append(((ex + side * gap, sy(z)),
                             (pos + side * over, sy(z))))
        for a, b in zip(levels, levels[1:]):
            target = _vertical_target(group, a, b,
                                      wall.name if overall else None)
            item = target.pop('item', None) if target else None
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': pos,
                         'side': side, 'value': b - a, 'target': target,
                         'item': item, 'w0': a})

    dims_ext = []
    lower = [it for it in items if it.kind == 'LOWER']
    upper = [it for it in items if it.kind == 'UPPER' or it.tall]
    openings = [it for it in items if it.kind == 'OPENING']

    def item_between(group):
        def f(a, b):
            for it in group:
                if abs(it.x0 - a) <= MERGE and abs(it.x1 - b) <= MERGE:
                    return it
            return None
        return f

    floor_y = sy(0.0)
    # Below the floor: the floor-standing run, then the overall length.
    t = 0
    if lower:
        pts = _chain([v for it in lower for v in (it.x0, it.x1)], 0.0, length)
        add_h(pts, floor_y - first, lambda x: floor_y, -1, lower,
              item_of=item_between(lower))
        t += 1
    add_h([0.0, length], floor_y - first - t * tier, lambda x: floor_y, -1,
          [], read_only=True)

    # Above the wall: uppers and talls, then windows and doors.
    top_z = max([height] + [it.z1 for it in items])
    top_y = sy(top_z)
    t = 0
    for group in (upper, openings):
        if not group:
            continue
        pts = _chain([v for it in group for v in (it.x0, it.x1)], 0.0, length)

        def from_top(x, group=group):
            zs = [it.z1 for it in group
                  if abs(it.x0 - x) <= MERGE or abs(it.x1 - x) <= MERGE]
            return sy(max(zs)) if zs else sy(height)
        add_h(pts, top_y + first + t * tier, from_top, 1, group,
              item_of=item_between(group))
        t += 1

    # Right: the height chain, then the overall height. With heights on
    # both sides, each side dims the products on its half of the wall,
    # so a tall at the left end and uppers at the right each read on
    # their own side.
    products = [it for it in items if it.kind != 'OPENING']
    both = show_option(scene, 'BOTH_HEIGHTS')
    if both:
        mid = length / 2.0
        left_group = [it for it in products if (it.x0 + it.x1) / 2.0 < mid]
        right_group = [it for it in products if (it.x0 + it.x1) / 2.0 >= mid]
    else:
        left_group, right_group = [], products
    right_x = sx(max([wx1] + [it.x1 for it in items]))
    left_x = sx(min([wx0] + [it.x0 for it in items]))
    t = 0
    levels = _height_levels(right_group, height)
    if len(levels) > 2:
        add_v(levels, right_x + first, 1, right_group)
        t += 1
    add_v([0.0, height], right_x + first + t * tier, 1, [], overall=True)

    # Left: the left half's height chain, then window and door sills
    # and heads.
    t = 0
    levels = _height_levels(left_group, height)
    if len(levels) > 2:
        add_v(levels, left_x - first, -1, left_group)
        t += 1
    if openings:
        lv = {0.0, height}
        for it in openings:
            lv.update((max(it.z0, 0.0), it.z1))
        add_v(_chain(lv, 0.0, max(lv)), left_x - first - t * tier, -1,
              openings)

    if show_option(scene, 'FACE_FRAME'):
        _face_frame_dims(items, dims, sx, sy, s, fr[1])

    # A selected product carries its own height, just inside its right
    # edge, so a tall or an odd-height cabinet can be sized here too.
    inset = 14 * s
    for it in items:
        if it.name not in selected or it.preview \
                or not _height_editor(it.obj):
            continue
        if sx(it.x1) - sx(it.x0) < 3 * inset:
            continue
        dims.append({'axis': 'V', 'a': sy(it.z0), 'b': sy(it.z1),
                     'pos': sx(it.x1) - inset, 'side': 1,
                     'value': it.z1 - it.z0,
                     'target': {'mode': 'HEIGHT', 'objs': [it.name]},
                     'item': it, 'w0': it.z0, 'key': ('SEL', it.name)})

    _place_text(scene, dims, region)
    for d in dims:
        if 'key' not in d:
            d['key'] = (d['axis'], round(d['pos'] / max(tier, 1)),
                        round(d['w0'], 4))
    extra = {'ext': dims_ext, 'floor': (sx(0.0), sx(length), floor_y),
             'items': items, 'sx': sx, 'sy': sy}
    return dims, extra


def _rects_overlap(a, b, m=2.0):
    return not (a[0] + a[2] + m <= b[0] or b[0] + b[2] + m <= a[0]
                or a[1] + a[3] + m <= b[1] or b[1] + b[3] + m <= a[1])


def _place_text(scene, dims, region):
    s = _s()
    blf.size(0, FONT_SIZE * s)
    th = blf.dimensions(0, "0123456789\"")[1]
    pad = TEXT_GAP_PX * s
    # A value fits between its ticks with this much clear either side.
    clear = (TICK_PX + 3) * 2 * s
    placed = []
    for d in dims:
        d['text'] = format_length(scene, d['value'])
        tw = blf.dimensions(0, d['text'])[0]
        span = abs(d['b'] - d['a'])
        lo, hi = min(d['a'], d['b']), max(d['a'], d['b'])
        mid = (lo + hi) / 2.0
        if d['axis'] == 'H':
            base = d['pos'] + pad
            cands = []
            if tw + clear <= span:
                cands.append((mid - tw / 2.0, base))
            cands += [(hi + 4 * s, base), (lo - 4 * s - tw, base),
                      (mid - tw / 2.0,
                       d['pos'] - pad - th if d['side'] < 0
                       else base + th + pad)]
            rects = [(x, y, tw, th) for x, y in cands]
        else:
            # Rotated a quarter turn: the value reads up the line from
            # its outer side, so it occupies th wide x tw tall.
            x_text = d['pos'] - pad if d['side'] > 0 else d['pos'] - pad
            cands = []
            if tw + clear <= span:
                cands.append((x_text - th, mid - tw / 2.0))
            cands += [(x_text - th, hi + 4 * s), (x_text - th, lo - 4 * s - tw)]
            rects = [(x, y, th, tw) for x, y in cands]
        chosen = rects[0]
        for r in rects:
            if not any(_rects_overlap(r, p) for p in placed):
                chosen = r
                break
        d['rect'] = chosen
        placed.append(chosen)


# ---- Drawing -----------------------------------------------------------------------

def _stroke(region, pts, width, color):
    """A line with a dark halo under it, so it reads on any background."""
    hb_dim_style.stroke(region, pts, width, color, _s())


def _tick(x, y, s):
    t = TICK_PX * s
    return [(x - t, y - t), (x + t, y + t)]


def _dim_lines(d, s):
    if d['axis'] == 'H':
        y = d['pos']
        line = [(d['a'], y), (d['b'], y)]
        ticks = _tick(d['a'], y, s) + _tick(d['b'], y, s)
    else:
        x = d['pos']
        line = [(x, d['a']), (x, d['b'])]
        ticks = _tick(x, d['a'], s) + _tick(x, d['b'], s)
    return line, ticks


def _text(d, color, s):
    x, y, w, h = d['rect']
    blf.size(0, FONT_SIZE * s)
    blf.color(0, *color)
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, 5, 0.0, 0.0, 0.0, 0.9)
    blf.shadow_offset(0, 0, 0)
    if d['axis'] == 'V':
        blf.enable(0, blf.ROTATION)
        blf.rotation(0, math.pi / 2.0)
        blf.position(0, x + w, y, 0)
    else:
        blf.position(0, x, y, 0)
    draw_glyphs(0, d['text'])
    blf.disable(0, blf.ROTATION)
    blf.disable(0, blf.SHADOW)


def _bar_layout(context, area):
    """[(part, rect, label)] of the elevation bar at the bottom centre."""
    wall = active_wall(context)
    if wall is None:
        return []
    s = _s()
    walls = room_walls(context.scene)
    idx = walls.index(wall) + 1 if wall in walls else 0
    title = f"Elevation  ·  Wall {idx} of {len(walls)}" if idx \
        else f"Elevation  ·  {wall.name}"
    blf.size(0, 12 * s)
    h = 28 * s
    arrow_w = 28 * s
    title_w = blf.dimensions(0, title)[0] + 28 * s
    exit_label = "Exit  Esc"
    exit_w = blf.dimensions(0, exit_label)[0] + 24 * s
    gap = 3 * s
    many = len(walls) > 1
    chips = [('SHOW:' + key, label, blf.dimensions(0, label)[0] + 24 * s)
             for key, label, _default in SHOW_OPTIONS]
    total = title_w + exit_w + gap + (2 * (arrow_w + gap) if many else 0)         + sum(w + gap for _p, _l, w in chips)
    xmin, xmax, ymin, _ymax = get_visible_window_bounds(area)
    x = (xmin + xmax) / 2.0 - total / 2.0
    y = ymin + 18 * s
    parts = []
    if many:
        parts.append(('PREV', (x, y, arrow_w, h), None))
        x += arrow_w + gap
    parts.append(('TITLE', (x, y, title_w, h), title))
    x += title_w + gap
    if many:
        parts.append(('NEXT', (x, y, arrow_w, h), None))
        x += arrow_w + gap
    for part, label, w in chips:
        parts.append((part, (x, y, w, h), label))
        x += w + gap
    parts.append(('EXIT', (x, y, exit_w, h), exit_label))
    return parts


def _draw_bar(context, area):
    parts = _bar_layout(context, area)
    if not parts:
        return
    s = _s()
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    x0 = parts[0][1][0]
    x1 = parts[-1][1][0] + parts[-1][1][2]
    y, h = parts[0][1][1], parts[0][1][3]
    draw_soft_shadow(shader, x0, y, x1 - x0, h, 6 * s)
    for part, rect, label in parts:
        rx, ry, rw, rh = rect
        hovered = _hover == ('BAR', part)
        on = part.startswith('SHOW:') and show_option(context.scene,
                                                      part[5:])
        if part == 'TITLE':
            bg = Theme.ACCENT_BG
        elif on:
            bg = Theme.BTN_HOVER_BG if hovered else Theme.ACCENT_BG
        else:
            bg = Theme.BTN_HOVER_BG if hovered else Theme.BTN_BG
        draw_round_rect(shader, rx, ry, rw, rh, 5 * s, bg)
        if part in ('PREV', 'NEXT'):
            cx, cy = rx + rw / 2.0, ry + rh / 2.0
            a = 4 * s
            d = -1 if part == 'PREV' else 1
            draw_lines(shader, [(cx - d * a * 0.6, cy + a), (cx + d * a * 0.6, cy),
                                (cx + d * a * 0.6, cy), (cx - d * a * 0.6, cy - a)],
                       Theme.GLYPH_HOVER if hovered else Theme.GLYPH)
        else:
            blf.size(0, 12 * s)
            tw, th = blf.dimensions(0, label)
            blf.color(0, *(Theme.TEXT_PRIMARY if part == 'TITLE' or hovered
                           or on else Theme.TEXT_NORMAL))
            blf.position(0, rx + (rw - tw) / 2.0,
                         ry + (rh - blf.dimensions(0, "Ag")[1]) / 2.0 + 1, 0)
            draw_glyphs(0, label)


def _draw():
    if _state is None:
        return
    context = bpy.context
    area, region = context.area, context.region
    if area is None or area.type != 'VIEW_3D' or region is None \
            or region.type != 'WINDOW':
        return
    rv3d = context.region_data
    if rv3d is None or rv3d.as_pointer() != _state['r3d']:
        return
    if context.scene is None or context.scene.name != _state['scene']:
        # The room was switched under the elevation: put everything back
        # (the room switch already set its own view).
        bpy.app.timers.register(lambda: leave(restore_view=False),
                                first_interval=0.0)
        return
    if _state.get('fit', 0) > 0 and not _state.get('fit_queued'):
        _state['fit_queued'] = True

        def done():
            if _state is not None:
                _state['fit_queued'] = False
        _queue_fit(area, region, rv3d)
        bpy.app.timers.register(done, first_interval=0.02)

    dims, extra = _layout(context, region, rv3d)
    s = _s()

    def paint():
        gpu.state.blend_set('ALPHA')
        if extra is not None:
            fx0, fx1, fy = extra['floor']
            _stroke(region, [(fx0 - 24 * s, fy), (fx1 + 24 * s, fy)],
                    2.0 * s, FLOOR_LINE)
            # The product a hovered value measures, outlined.
            sx, sy = extra['sx'], extra['sy']
            outlines = []
            hot = []
            for it in extra['items']:
                r = (sx(it.x0), sy(it.z0), sx(it.x1), sy(it.z1))
                quad = [(r[0], r[1]), (r[2], r[1]), (r[2], r[1]), (r[2], r[3]),
                        (r[2], r[3]), (r[0], r[3]), (r[0], r[3]), (r[0], r[1])]
                if it.preview:
                    outlines += quad
                for d in dims:
                    if d.get('item') is it and _hover == ('DIM', d['key']):
                        hot += quad
            if outlines:
                _stroke(region, outlines, 1.5 * s, PREVIEW)
            if hot:
                _stroke(region, hot, 2.0 * s, HOVER)
            _stroke(region, [p for seg in extra['ext'] for p in seg],
                    1.0 * s, LINE)
        normal_lines, normal_ticks = [], []
        hot_lines, hot_ticks = [], []
        for d in dims:
            line, ticks = _dim_lines(d, s)
            if _hover == ('DIM', d['key']) and d['target'] is not None:
                hot_lines += line
                hot_ticks += ticks
            else:
                normal_lines += line
                normal_ticks += ticks
        _stroke(region, normal_lines, 1.0 * s, LINE)
        _stroke(region, normal_ticks, 2.0 * s, LINE)
        _stroke(region, hot_lines, 1.5 * s, HOVER)
        _stroke(region, hot_ticks, 2.5 * s, HOVER)
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        for d in dims:
            editing = _edit is not None and _edit['key'] == d['key']
            if editing:
                typed = _edit['typed']
                shown = dict(d)
                shown['text'] = (typed + "|") if typed else d['text']
                blf.size(0, FONT_SIZE * s)
                tw = blf.dimensions(0, shown['text'])[0]
                x, y, w, h = d['rect']
                if d['axis'] == 'H':
                    rect = (x + w / 2.0 - tw / 2.0, y, tw, h)
                else:
                    rect = (x, y + h / 2.0 - tw / 2.0, w, tw)
                shown['rect'] = rect
                shader.bind()
                p = 3 * s
                draw_round_rect(shader, rect[0] - p, rect[1] - p,
                                rect[2] + 2 * p, rect[3] + 2 * p, 3 * s,
                                EDIT_BG)
                _text(shown, TEXT, s)
                continue
            hot = _hover == ('DIM', d['key']) and d['target'] is not None
            color = HOVER_TEXT if hot else (TEXT if d['target'] is not None
                                       else TEXT_READONLY)
            _text(d, color, s)
        _draw_bar(context, area)
        gpu.state.blend_set('NONE')

    try:
        from . import viewport_hud
        viewport_hud.paint_clear_of_panel(context, area, paint)
    except Exception:
        paint()


# ---- Hit testing -----------------------------------------------------------------

def _hit(context, mx, my):
    """('BAR', part) | ('DIM', dim) | None at a region point."""
    for part, rect, _label in _bar_layout(context, context.area):
        if part != 'TITLE' and point_in_rect(mx, my, rect):
            return ('BAR', part)
    dims, _extra = _layout(context, context.region, context.region_data)
    p = 4 * _s()
    for d in dims:
        x, y, w, h = d['rect']
        if x - p <= mx <= x + w + p and y - p <= my <= y + h + p:
            return ('DIM', d)
    return None


# ---- Commit ------------------------------------------------------------------------

def _set_appliance_height(appliance, height):
    """The width path's twin (wall_run_dims.set_appliance_width)."""
    from ..product_libraries.common import appliance_geo
    cage = hb_types.GeoNodeCage(appliance)
    cage.set_input('Dim Z', height)
    if appliance.get(appliance_geo.CABINET_APPLIANCE_FLAG):
        appliance[appliance_geo.SIZE_OWNED_FLAG] = True
    if appliance_geo.supports_panels(appliance) \
            and appliance_geo.is_panel_ready(appliance):
        panels = appliance_geo._panels_module()
        if panels is not None:
            panels.rebuild(appliance)
    if appliance_geo.appliance_type(appliance) == 'HOOD':
        appliance_geo.build_geometry(appliance)


def _set_height(context, obj, value):
    if obj.get('IS_APPLIANCE'):
        _set_appliance_height(obj, value)
        return True
    if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
        from ..product_libraries.face_frame import dim_edit_overlay as ff
        return ff._commit(obj, 'CAB_H', value) is not False
    if obj.get('IS_FRAMELESS_CABINET_CAGE'):
        from ..product_libraries.frameless import dim_edit_overlay as fl
        return fl._commit(context, obj, 'CAB_H', value) is not False
    if _is_opening(obj):
        from . import room_dim_overlay
        return room_dim_overlay._commit(obj, 'CAGE_H', value)
    return False


def _commit_vertical(context, target, current, value):
    mode = target['mode']
    if mode == 'WALL_H':
        wall = bpy.data.objects.get(target['obj'])
        if wall is None or value < units.inch(6.0):
            return False
        from . import room_dim_overlay
        return room_dim_overlay._commit(wall, 'WALL_H', value)
    objs = [o for o in (bpy.data.objects.get(n) for n in target['objs'])
            if o is not None]
    grow = [(o, h) for o, h in ((bpy.data.objects.get(n), h)
                                for n, h in target.get('grow', ()))
            if o is not None]
    if not objs and not grow:
        return False
    if mode == 'HEIGHT':
        if value < units.inch(1.0):
            return False
        done = False
        for obj in objs:
            done = _set_height(context, obj, value) or done
        return done
    # LIFT: slide the hanging products up or down by the change, never
    # through the floor.
    if value < 0.0:
        return False
    delta = (value - current) * target['sign']
    if any(o.location.z + delta < 0.0 for o in objs):
        return False
    if any(h + delta < units.inch(1.0) for _o, h in grow):
        return False
    for obj, h in grow:
        _set_height(context, obj, h + delta)
    for obj in objs:
        obj.location.z += delta
        if _is_opening(obj):
            from ..product_libraries.common import door_window_geo
            door_window_geo.build_geometry(obj)
    return True


def _commit(context, target, current, value):
    if target['mode'] in ('HEIGHT', 'LIFT', 'WALL_H'):
        return _commit_vertical(context, target, current, value)
    obj = bpy.data.objects.get(target['obj'])
    if obj is None:
        return False
    if target['mode'] == 'WIDTH':
        if value <= units.inch(1.0):
            return False
        if obj.get('IS_APPLIANCE'):
            from ..product_libraries.common import wall_run_dims
            wall_run_dims.set_appliance_width(obj, value)
            return True
        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            from ..product_libraries.face_frame import dim_edit_overlay as ff
            return ff._commit(obj, 'CAB_W', value) is not False
        if obj.get('IS_FRAMELESS_CABINET_CAGE'):
            # As Grab does it: a butted neighbor takes up the change.
            from ..product_libraries.frameless.operators import (
                op_grab_frameless)
            return op_grab_frameless.resize_in_run(context, obj, value)
        return False
    # A gap: slide the product along the wall by the change.
    if value < 0.0:
        return False
    wall = obj.parent
    fr = _frame(wall) if wall is not None else None
    if fr is None:
        return False
    F = fr[0]
    delta = (value - current) * target['sign']
    world_dir = F.to_3x3().normalized() @ Vector((delta, 0.0, 0.0))
    local = wall.matrix_world.to_3x3().normalized().inverted() @ world_dir
    obj.location = obj.location + local
    return True


# ---- Operators ------------------------------------------------------------------

def _room_scene(context):
    scene = context.scene
    return (scene is not None and not scene.get('IS_LAYOUT_VIEW')
            and not scene.get('IS_DETAIL_VIEW'))


class home_builder_OT_show_elevation(bpy.types.Operator):
    """Look at a wall face-on, dimensioned like an elevation drawing.
    Everything else is hidden and products you place land on this wall
    until you exit (Esc)"""
    bl_idname = "home_builder.show_elevation"
    bl_label = "Show Elevation"
    bl_options = {'REGISTER'}

    wall_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and _room_scene(context)
                and any(o.get('IS_WALL_BP') for o in context.scene.objects))

    def execute(self, context):
        wall = (bpy.data.objects.get(self.wall_name) if self.wall_name
                else pick_wall(context))
        if wall is None or not wall.get('IS_WALL_BP'):
            self.report({'WARNING'}, "No wall to show")
            return {'CANCELLED'}
        if hb_types.is_curved_wall(wall):
            self.report({'WARNING'}, "Curved walls have no elevation yet")
            return {'CANCELLED'}
        keep = _state['view'] if _state is not None else None
        if not enter(context, wall, keep_view=keep):
            return {'CANCELLED'}
        return {'FINISHED'}


class home_builder_OT_exit_elevation(bpy.types.Operator):
    """Leave the elevation and go back to the room view"""
    bl_idname = "home_builder.exit_elevation"
    bl_label = "Exit Elevation"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return is_active(context) and _edit is None

    def execute(self, context):
        leave(context)
        return {'FINISHED'}


class home_builder_OT_elevation_step(bpy.types.Operator):
    """Show the next / previous wall of the room in elevation"""
    bl_idname = "home_builder.elevation_step"
    bl_label = "Next Wall Elevation"
    bl_options = {'REGISTER'}

    direction: bpy.props.IntProperty(default=1)  # type: ignore

    @classmethod
    def poll(cls, context):
        return is_active(context) and _edit is None

    def execute(self, context):
        step(context, 1 if self.direction >= 0 else -1)
        return {'FINISHED'}


class home_builder_OT_elevation_frame(bpy.types.Operator):
    """Fit the elevation back into the view"""
    bl_idname = "home_builder.elevation_frame"
    bl_label = "Frame Elevation"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return is_active(context)

    def execute(self, context):
        wall = active_wall(context)
        r3d = context.area.spaces.active.region_3d
        _aim(r3d, wall)
        _state['fit'] = 2
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_elevation_hover(bpy.types.Operator):
    bl_idname = "home_builder.elevation_hover"
    bl_label = "Elevation Hover"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (_state is not None and context.region is not None
                and context.region.type == 'WINDOW' and is_active(context))

    def invoke(self, context, event):
        global _hover, _mouse
        _mouse = (event.mouse_region_x, event.mouse_region_y)
        got = _hit(context, *_mouse)
        key = None
        if got is not None:
            key = (got[0], got[1]) if got[0] == 'BAR' else (
                ('DIM', got[1]['key']) if got[1]['target'] is not None
                else None)
        if key != _hover:
            _hover = key
            context.area.tag_redraw()
        return {'PASS_THROUGH'}


class home_builder_OT_elevation_click(bpy.types.Operator):
    """A press on the elevation bar or an editable value; anything else
    passes through to selection and tools."""
    bl_idname = "home_builder.elevation_click"
    bl_label = "Elevation Click"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (context.region is not None
                and context.region.type == 'WINDOW' and is_active(context))

    def invoke(self, context, event):
        if _edit is not None:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        try:
            from . import viewport_hud
            if viewport_hud.click_hits_widget(context, context.area, mx, my):
                return {'PASS_THROUGH'}
        except Exception:
            pass
        got = _hit(context, mx, my)
        if got is None:
            return {'PASS_THROUGH'}
        if got[0] == 'BAR':
            if got[1] == 'EXIT':
                leave(context)
            elif got[1].startswith('SHOW:'):
                toggle_show_option(context.scene, got[1][5:])
            else:
                step(context, -1 if got[1] == 'PREV' else 1)
            context.area.tag_redraw()
            return {'FINISHED'}
        d = got[1]
        if d['target'] is None:
            return {'PASS_THROUGH'}
        bpy.ops.home_builder.elevation_edit_dim('INVOKE_DEFAULT')
        _edit_begin(d)
        return {'FINISHED'}


def _edit_begin(d):
    global _edit
    if _edit is not None:
        _edit.update({'key': d['key'], 'target': d['target'],
                      'value': d['value'], 'typed': ""})


_INPUT_CHARS = set("0123456789./-+'\" ")


class home_builder_OT_elevation_edit_dim(bpy.types.Operator):
    """Type a new size for the clicked width or gap. Enter commits, Esc /
    right-click / click-away cancels."""
    bl_idname = "home_builder.elevation_edit_dim"
    bl_label = "Edit Elevation Dimension"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        global _edit
        _edit = {'key': None, 'target': None, 'value': 0.0, 'typed': "",
                 'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('TEXT')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        global _edit
        _edit = None
        try:
            context.window.cursor_set('DEFAULT')
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        if _edit is None or _edit.get('owner') != id(self):
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER',
                          'TRACKPADPAN', 'TRACKPADZOOM'}:
            return {'PASS_THROUGH'}
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            typed = _edit['typed']
            target, current = _edit['target'], _edit['value']
            if not typed or target is None:
                self._finish(context)
                return {'CANCELLED'}
            from ..product_libraries.face_frame import dim_edit_overlay as ff
            value = ff.parse_distance(typed)
            self._finish(context)
            if value is None or not _commit(context, target, current, value):
                self.report({'WARNING'}, f"Could not set '{typed}'")
                return {'CANCELLED'}
            _bump_gen()
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE', 'LEFTMOUSE'}:
            self._finish(context)
            return {'CANCELLED'}
        if event.type == 'BACK_SPACE':
            _edit['typed'] = _edit['typed'][:-1]
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        ch = event.unicode
        if ch == '=':
            ch = '+'
        if ch and ch in _INPUT_CHARS:
            _edit['typed'] += ch
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}


# ---- HUD toggle -------------------------------------------------------------------

def _prop_get(_self):
    try:
        return is_active(bpy.context)
    except Exception:
        return False


def _prop_set(_self, value):
    context = bpy.context
    if not value:
        leave(context)
        return
    if is_active(context):
        return
    try:
        bpy.ops.home_builder.show_elevation()
    except Exception as exc:
        print("Show Elevation:", exc)


def _glyph_elevation(shader, rect, color):
    """A wall face with two cabinets on it and a dimension under them."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.56, rh * 0.50
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0 + rh * 0.06
    x1, y1 = x0 + w, y0 + h
    m = x0 + w * 0.5
    ch = h * 0.45
    pts = [(x0, y0), (x1, y0),                       # floor
           (x0, y0), (x0, y0 + ch), (x0, y0 + ch), (x1, y0 + ch),
           (x1, y0 + ch), (x1, y0), (m, y0), (m, y0 + ch),
           (x0, y1), (x0 + w * 0.42, y1), (x0, y1), (x0, y1 - h * 0.25),
           (x0 + w * 0.42, y1), (x0 + w * 0.42, y1 - h * 0.25),
           (x0, y1 - h * 0.25), (x0 + w * 0.42, y1 - h * 0.25)]
    dy = y0 - rh * 0.14
    t = rh * 0.06
    pts += [(x0, dy), (x1, dy), (x0 - t, dy - t), (x0 + t, dy + t),
            (x1 - t, dy - t), (x1 + t, dy + t)]
    draw_lines(shader, pts, color)


def _hud_visible(context):
    scene = context.scene
    return (scene is not None and _room_scene(context)
            and any(o.get('IS_WALL_BP') for o in scene.objects))


def _register_hud():
    try:
        from . import viewport_hud
        viewport_hud.register_mode_glyph_toggle(
            'hb_elevation', 'hb_elevation_mode', "Show Elevation",
            "Exit Elevation", glyph=icon_glyph('elevation', _glyph_elevation),
            ui_visible=_hud_visible, order=40)
    except Exception as exc:
        print("Elevation HUD toggle skipped:", exc)


def _unregister_hud():
    try:
        from . import viewport_hud
        viewport_hud.unregister_mode_glyph_toggle('hb_elevation')
    except Exception:
        pass


# ---- Suppression of the per-cabinet labels ------------------------------------------

def hides_cabinet_labels(context):
    """The Cabinets-mode size labels and room dims stand down while an
    elevation dimensions the wall itself."""
    try:
        return is_active(context)
    except Exception:
        return False


# ---- Lifecycle -----------------------------------------------------------------------

@bpy.app.handlers.persistent
def _on_load(*_args):
    """A file saved mid-elevation comes back with everything shown."""
    global _state, _edit
    _state, _edit = None, None
    for scene in bpy.data.scenes:
        _unisolate(scene)


classes = (
    home_builder_OT_show_elevation,
    home_builder_OT_exit_elevation,
    home_builder_OT_elevation_step,
    home_builder_OT_elevation_frame,
    home_builder_OT_elevation_hover,
    home_builder_OT_elevation_click,
    home_builder_OT_elevation_edit_dim,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for idname, key, value, kw in (
            (home_builder_OT_elevation_click.bl_idname, 'LEFTMOUSE', 'PRESS',
             {'any': True, 'head': True}),
            (home_builder_OT_elevation_hover.bl_idname, 'MOUSEMOVE', 'ANY',
             {'any': True, 'head': True}),
            (home_builder_OT_exit_elevation.bl_idname, 'ESC', 'PRESS', {}),
            (home_builder_OT_elevation_frame.bl_idname, 'HOME', 'PRESS',
             {'head': True})):
        kmi = km.keymap_items.new(idname, key, value, **kw)
        _addon_keymaps.append((km, kmi))
    for key, direction in (('LEFT_ARROW', -1), ('RIGHT_ARROW', 1)):
        kmi = km.keymap_items.new(home_builder_OT_elevation_step.bl_idname,
                                  key, 'PRESS', head=True)
        kmi.properties.direction = direction
        _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    global _draw_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.hb_elevation_mode = bpy.props.BoolProperty(
        name="Elevation", description="Show the wall in elevation",
        get=_prop_get, set=_prop_set, options={'SKIP_SAVE'})
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    for handlers in (bpy.app.handlers.depsgraph_update_post,
                     bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        if _bump_gen not in handlers:
            handlers.append(_bump_gen)
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)
    _register_keymaps()
    _register_hud()


def unregister():
    global _draw_handle
    try:
        leave(restore_view=True)
    except Exception:
        pass
    _unregister_hud()
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for handlers in (bpy.app.handlers.depsgraph_update_post,
                     bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        if _bump_gen in handlers:
            handlers.remove(_bump_gen)
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
    try:
        del bpy.types.WindowManager.hb_elevation_mode
    except Exception:
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
