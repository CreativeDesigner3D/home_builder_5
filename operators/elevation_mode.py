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
  and door sill / head heights. Each side's height chain dims the
  products on its half of the wall, so a tall at one end and uppers at
  the other both read;
- with Face Frame on, the face frames' stiles and openings as the
  chain nearest the work (below the floor for floor-standing cabinets,
  above the wall for uppers and talls), and the rails and openings of
  each distinct opening column as height chains out past the wall's
  ends, nearest the work (on the frame when the sides are full);
- with Annotations on, the notes an add-on supplies for the wall
  (register_annotation_source), drawn in the view's own style.

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

While it is up the view's background is white, like the sheet, and the
dims and notes are drawn in drafting ink; leaving puts the view's own
background back.

Leave with Esc, the Exit button on the elevation bar, or the HUD View
toggle; Left / Right arrows (or the bar's arrows) step to the next wall
of the room without leaving. Exiting puts back exactly what it hid (by
an id-prop tag, so a save made mid-elevation is cleaned up on load) and
the view the room had before.
"""

import math
import re

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Euler
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from .. import hb_types
from .. import units
from .. import hb_dim_style
from .. import hb_pdf
from ..hb_icons import icon_glyph
from ..hb_gpu_draw import (get_visible_window_bounds, draw_round_rect,
                           draw_soft_shadow, draw_glyphs, draw_lines,
                           point_in_rect)
from ..hb_gpu_ui import Theme, scale as _ui_scale

# ---- Style ---------------------------------------------------------------

FONT_SIZE = 12
# Drafting ink, as on the elevation sheets: dark lines and values with a
# white halo, so they read on a white wall and on the dark viewport.
LINE = (0.07, 0.07, 0.08, 1.0)
TEXT = (0.0, 0.0, 0.0, 1.0)
TEXT_READONLY = (0.20, 0.20, 0.22, 1.0)
# Kept faint and tight: a strong halo glows on the grey viewport.
HALO = (1.0, 1.0, 1.0, 0.45)
TEXT_HALO = (1.0, 1.0, 1.0, 0.7)
TEXT_HALO_BLUR = 3
HOVER = (0.05, 0.38, 0.85, 1.0)
HOVER_TEXT = (0.05, 0.38, 0.85, 1.0)
EDIT_BG = Theme.ACCENT_BG
EDIT_TEXT = (1.0, 1.0, 1.0, 1.0)
EDIT_HALO = (0.0, 0.0, 0.0, 0.6)
FLOOR_LINE = (0.07, 0.07, 0.08, 0.9)
PREVIEW = (1.0, 0.62, 0.20, 1.0)

FIRST_TIER_PX = 30      # geometry to the first dimension line
TIER_PX = 30            # between stacked dimension lines
EXT_GAP_PX = 5          # extension line stands off the geometry
EXT_OVER_PX = 5         # and runs past the dimension line
TICK_PX = 4.5           # half-length of the 45 degree tick, per axis
TEXT_GAP_PX = 4         # value above its line
BREAK_GAP_PX = 4        # line stops this short of a value set in it

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
_print_scale = None    # set while printing: px -> pt
_item_cache = {}
_draw_handle = None
_addon_keymaps = []


def _s():
    if _print_scale is not None:
        return _print_scale
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


# While an elevation is up its view is paper: a white background, so the
# drawing-ink dims and notes read the way they do on the sheet. Solid and
# Wireframe shading honour it (Material Preview / Rendered show the world).
PAPER = (1.0, 1.0, 1.0)
# Where the view's own background is kept while it shows paper, so a
# file saved mid-elevation gets it back on load.
PAPER_PROP = 'HB_ELEVATION_BACKGROUND'
# The grid, floor and axis lines are off on paper: they are not part of
# the drawing.
PAPER_OVERLAYS = ('show_ortho_grid', 'show_floor', 'show_axis_x',
                  'show_axis_y', 'show_axis_z')


def _paper_on(space, scene):
    """Turn the view to paper; returns what it had."""
    sh = space.shading
    ov = space.overlay
    saved = {'type': sh.background_type,
             'color': tuple(sh.background_color),
             'overlays': {k: bool(getattr(ov, k)) for k in PAPER_OVERLAYS}}
    try:
        scene[PAPER_PROP] = {'type': saved['type'],
                             'color': list(saved['color']),
                             'overlays': dict(saved['overlays'])}
    except Exception:
        pass
    sh.background_type = 'VIEWPORT'
    sh.background_color = PAPER
    for k in PAPER_OVERLAYS:
        setattr(ov, k, False)
    return saved


def _paper_off(space, saved, scene=None):
    if saved is None:
        return
    sh = space.shading
    try:
        sh.background_color = saved['color']
        sh.background_type = saved['type']
        for k, v in (saved.get('overlays') or {}).items():
            if k in PAPER_OVERLAYS:
                setattr(space.overlay, k, bool(v))
    except Exception:
        pass
    if scene is not None and PAPER_PROP in scene:
        del scene[PAPER_PROP]


def _paper_restore_on_load():
    """Views left on paper by a save mid-elevation get their own
    background back."""
    saved = None
    for scene in bpy.data.scenes:
        if PAPER_PROP in scene:
            group = scene[PAPER_PROP]
            saved = {'type': group.get('type', 'THEME'),
                     'color': tuple(group.get('color', (0.05,) * 3))}
            shown = group.get('overlays')
            if shown is not None:
                saved['overlays'] = {k: bool(shown.get(k, True))
                                     for k in PAPER_OVERLAYS}
            del scene[PAPER_PROP]
    if saved is None:
        return
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            sh = area.spaces.active.shading
            if sh.background_type == 'VIEWPORT' and all(
                    abs(c - p) < 1e-4 for c, p in
                    zip(sh.background_color, PAPER)):
                _paper_off(area.spaces.active, saved)


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
    paper = None
    if _state is not None:
        # Stepping to another wall keeps the background it saved first.
        paper = _state.get('paper')
        scene = bpy.data.scenes.get(_state['scene'])
        if scene is not None:
            _unisolate(scene)
    if paper is None:
        paper = _paper_on(area.spaces.active, context.scene)
    extra = _isolate(context, wall)
    _state = {'scene': context.scene.name, 'wall': wall.name,
              'r3d': r3d.as_pointer(), 'view': saved, 'extra': extra,
              'preview': set(), 'fit': 2, 'paper': paper}
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
    if area is not None:
        _paper_off(area.spaces.active, st.get('paper'), scene)
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
                 'movable', 'width_edit', 'preview', 'shelf')


def _is_floating_shelf(obj):
    return bool(obj.get('IS_FLOATING_SHELF')
                or (obj.get('IS_FRAMELESS_PRODUCT_CAGE')
                    and obj.get('PART_TYPE') == 'FLOATING_SHELF'))


def _is_product(obj):
    return any(obj.get(m) for m in PRODUCT_MARKERS) or _is_floating_shelf(obj)


def _is_opening(obj):
    return any(obj.get(m) for m in OPENING_MARKERS)


def _width_editor(obj):
    if obj.get('IS_FACE_FRAME_CABINET_CAGE') or obj.get(
            'IS_FRAMELESS_CABINET_CAGE') or obj.get('IS_APPLIANCE'):
        return True
    return False


def _height_editor(obj):
    return _width_editor(obj) or _is_opening(obj)


def _corner_footprint(obj):
    """The full box of a pie cut / diagonal corner cabinet in its own
    frame, from its cage size: the cage mesh itself is only the notch in
    the corner, so its bounds miss most of the cabinet."""
    ffc = getattr(obj, 'face_frame_cabinet', None)
    if ffc is None or getattr(ffc, 'corner_type', 'NONE') not in (
            'PIE_CUT', 'DIAGONAL'):
        return None
    try:
        cage = hb_types.GeoNodeCage(obj)
        dx, dy, dz = (cage.get_input(k) or 0.0
                      for k in ('Dim X', 'Dim Y', 'Dim Z'))
        mirror_y = bool(cage.get_input('Mirror Y'))
    except Exception:
        return None
    if dx <= 0.0 or dy <= 0.0 or dz <= 0.0:
        return None
    y0, y1 = (-dy, 0.0) if mirror_y else (0.0, dy)
    return [Vector((x, y, z)) for x in (0.0, dx) for y in (y0, y1)
            for z in (0.0, dz)]


def _end_on_from_other_wall(obj, wall):
    """A product on the next wall seen end-on at the corner: its span
    here is its depth, which says nothing about this wall's run. A corner
    cabinet is the exception -- its depth here is what gets measured."""
    host = obj.parent
    while host is not None and not host.get('IS_WALL_BP'):
        host = host.parent
    if host is None or host == wall or not _is_product(obj) \
            or _corner_footprint(obj) is not None:
        return False
    try:
        rel = (wall.matrix_world.inverted_safe() @ obj.matrix_world).to_euler()
    except Exception:
        return False
    return abs(math.cos(rel.z)) < 0.1


def _make_item(obj, Fi, wall, preview=False):
    try:
        mw = obj.matrix_world
        box = _corner_footprint(obj) or [Vector(c) for c in obj.bound_box]
        pts = [Fi @ (mw @ c) for c in box]
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
    it.shelf = _is_floating_shelf(obj)
    if _is_opening(obj):
        it.kind = 'OPENING'
    elif it.z0 < FLOOR_STANDING_Z and not it.shelf:
        it.kind = 'LOWER'
    else:
        # A floating shelf hangs on the wall, however low.
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


def _drop_contents(items):
    """Obstacles standing wholly inside a cabinet or closet (a shoe box
    on a shelf) are its contents, not a feature of the wall: they would
    only chop the chains into slivers."""
    hosts = [it for it in items if not it.obj.get('IS_OBSTACLE')
             and it.kind != 'OPENING']

    def inside(it, h):
        return (h.x0 - MERGE <= it.x0 and it.x1 <= h.x1 + MERGE
                and h.z0 - MERGE <= it.z0 and it.z1 <= h.z1 + MERGE)
    return [it for it in items if not (it.obj.get('IS_OBSTACLE')
                                       and any(inside(it, h) for h in hosts))]


# ---- Closets -------------------------------------------------------------------

def _closet_bays(it, Fi, wall):
    """(x0, x1) of each bay of a closet run, along the wall. A corner L
    unit has no bays: it is one opening, measured on its own wall only
    (the wall it turns onto sees its side)."""
    obj = it.obj
    if not obj.get('IS_CLOSET_STARTER_CAGE'):
        return []
    if str(obj.get('CLASS_NAME', '')).startswith('LShelf'):
        return [(it.x0, it.x1)] if obj.parent == wall else []
    spans = []
    for bay in obj.children:
        if not bay.get('IS_CLOSET_BAY_CAGE'):
            continue
        box = _wall_box(bay, Fi)
        if box is not None and box[1] - box[0] > MERGE:
            spans.append((box[0], box[1]))
    return sorted(spans)


def _closet_panel_heights(it, Fi):
    """(z0, z1) of each distinct panel height in a closet run (the same
    height once), as the sheets dimension them."""
    obj = it.obj
    if not obj.get('IS_CLOSET_STARTER_CAGE'):
        return []
    # From the panel's own Length, not its mesh: a panel hidden in the
    # viewport still prints on the sheet.
    seen, out = set(), []
    for part in obj.children:
        if (part.get('hb_part_role') != 'CLOSET_PANEL' or part.hide_render
                or part.get('hb_panel_off') or part.get('hb_preview')):
            continue
        try:
            length = hb_types.GeoNodeCutpart(part).get_input('Length') or 0.0
        except Exception:
            length = 0.0
        if length <= MERGE:
            continue
        k = round(length / 0.0015875)   # 1/16 in
        if k in seen:
            continue
        seen.add(k)
        base = Vector((part.location.x, 0.0, part.location.z))
        z0 = (Fi @ (obj.matrix_world @ base)).z
        out.append((z0, z0 + length))
    return out


def _items(scene, wall, extra=None, preview=None):
    """The products and openings that show on `wall`. `extra` (names of
    roots standing in front of it) and `preview` default to the
    elevation on screen."""
    st = _state or {}
    if extra is None:
        extra = st.get('extra', ())
    if preview is None:
        preview = st.get('preview', ())
    key = (_gen, wall.name, frozenset(preview), frozenset(extra))
    hit = _item_cache.get('key')
    if hit == key:
        return _item_cache['items']
    fr = _frame(wall)
    items = []
    if fr is not None:
        _F, Fi, length, _height = fr
        roots = list(wall.children)
        for name in extra:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                roots.append(obj)
        cands = []
        for obj in roots:
            if obj.get('IS_CAGE_GROUP'):
                cands.extend(c for c in obj.children if _is_product(c))
            elif _is_product(obj) or _is_opening(obj):
                cands.append(obj)
        preview = set(preview)
        for obj in cands:
            if obj.name in preview:
                continue
            try:
                if not obj.visible_get() and not obj.display_type == 'WIRE' \
                        and obj.hide_get():
                    continue
            except Exception:
                continue
            if _end_on_from_other_wall(obj, wall):
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
        items = _drop_contents(items)
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


# A value's fraction is set small and on the diagonal, the way it is
# lettered by hand: 37 1/2" takes little more room than 37".
FRACTION_SCALE = 0.62       # numerator and denominator, of the value's size
FRACTION_SLASH = 0.80       # the slash between them
FRACTION_RISE = 0.30        # the numerator's lift, of the value's size
FRACTION_GAP = 0.10         # whole number to fraction
FRACTION_TUCK = 0.04        # the slash tucks in under / over its figures
_FRACTION = re.compile(r'^(-?\d+)?\s*(\d+)/(\d+)(.*)$', re.S)


def value_runs(text, size, measure):
    """A value as the pieces to set it in: ([(string, x, y, size)],
    width), x and y from the start of the baseline. `measure(string,
    size)` is the width of a string in the face it will be set in, so
    any drawer can lay a value out in its own font. A value with no
    fraction is one piece."""
    m = _FRACTION.match(text)
    if m is None:
        return [(text, 0.0, 0.0, size)], measure(text, size)
    whole, num, den, tail = m.groups()
    small = size * FRACTION_SCALE
    slash = size * FRACTION_SLASH
    tuck = size * FRACTION_TUCK
    runs, x = [], 0.0
    if whole:
        runs.append((whole, 0.0, 0.0, size))
        x = measure(whole, size) + size * FRACTION_GAP
    runs.append((num, x, size * FRACTION_RISE, small))
    x += measure(num, small) - tuck
    runs.append(('/', x, 0.0, slash))
    x += measure('/', slash) - tuck
    runs.append((den, x, 0.0, small))
    x += measure(den, small)
    if tail:
        runs.append((tail, x, 0.0, size))
        x += measure(tail, size)
    return runs, x


def _blf_measure(text, size):
    blf.size(0, size)
    return blf.dimensions(0, text)[0]


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
    # (key, bar label, default) -- the label is the chip's hover hint
    ('FACE_FRAME', "Face Frame", False),
    # Only offered while some add-on supplies annotations.
    ('ANNOTATIONS', "Annotations", True),
    # What stands inside the cabinets (shelves, dividers, roll-outs),
    # drawn through the fronts as dashed lines.
    ('INTERIORS', "Interior Lines", False),
)


# ---- Annotation sources ------------------------------------------------------------
# Another add-on can hand the elevation notes to draw over the wall
# (labels, callouts, leaders). A source is fn(scene, wall) returning a
# list of primitives in world space:
#   {'kind': 'TEXT', 'origin': Vector, 'x_axis': Vector (reading
#    direction), 'text': str (may hold newlines),
#    'align': 'LEFT' | 'CENTER' | 'RIGHT'}
#   {'kind': 'LINES', 'points': [Vector, ...]} (pairs, like GPU LINES)
#   {'kind': 'BUBBLE', 'origin': Vector, 'text': str} (a circled mark,
#    the ring sized to the text on screen)
# Any primitive may carry 'color' (RGBA) to stand out from the ink.
# The view draws them in its own style, at a fixed screen size.

_annotation_sources = []
_annotation_cache = {}


def register_annotation_source(fn):
    if fn not in _annotation_sources:
        _annotation_sources.append(fn)
    _bump_gen()


def unregister_annotation_source(fn):
    if fn in _annotation_sources:
        _annotation_sources.remove(fn)
    _bump_gen()


def _option_available(key):
    if key == 'ANNOTATIONS':
        return bool(_annotation_sources)
    return True


def _annotations(scene, wall):
    key = (_gen, scene.name, wall.name, len(_annotation_sources))
    if _annotation_cache.get('key') == key:
        return _annotation_cache['prims']
    prims = []
    for fn in list(_annotation_sources):
        try:
            prims.extend(fn(scene, wall) or ())
        except Exception as exc:
            print(f"Elevation annotations: {exc}")
    _annotation_cache['key'] = key
    _annotation_cache['prims'] = prims
    return prims


ANNOTATION_FONT_SIZE = 11
ANNOTATION_LINE = (0.10, 0.10, 0.12, 0.9)
BUBBLE_FONT_SIZE = 12
BUBBLE_SEGMENTS = 32


def _bubble_rings(prims, P, s):
    """[(centre, radius, text, color)] on screen for the BUBBLE marks."""
    blf.size(0, BUBBLE_FONT_SIZE * s)
    out = []
    for pr in prims:
        if pr.get('kind') != 'BUBBLE' or not pr.get('text'):
            continue
        o = P(pr['origin'])
        if o is None:
            continue
        tw, th = blf.dimensions(0, pr['text'])
        r = max(tw, th) / 2.0 + 5 * s
        out.append((o, r, pr['text'], pr.get('color', TEXT)))
    return out


def _draw_bubbles(region, prims, P, s):
    rings = _bubble_rings(prims, P, s)
    if not rings:
        return
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    by_color = {}
    for o, r, _text, color in rings:
        # A paper disc under the ring keeps the mark readable over the
        # line work it sits on.
        ring = [(o.x + r * math.cos(2 * math.pi * i / BUBBLE_SEGMENTS),
                 o.y + r * math.sin(2 * math.pi * i / BUBBLE_SEGMENTS))
                for i in range(BUBBLE_SEGMENTS)]
        batch = batch_for_shader(shader, 'TRI_FAN',
                                 {"pos": [(o.x, o.y)] + ring + [ring[0]]})
        shader.bind()
        shader.uniform_float("color", (*PAPER, 1.0))
        batch.draw(shader)
        seg = by_color.setdefault(tuple(color), [])
        for a, b in zip(ring, ring[1:] + ring[:1]):
            seg += [a, b]
    for color, seg in by_color.items():
        _stroke(region, seg, 1.5 * s, color)
    blf.size(0, BUBBLE_FONT_SIZE * s)
    for o, _r, text, color in rings:
        tw, th = blf.dimensions(0, text)
        blf.color(0, *color)
        blf.position(0, o.x - tw / 2.0, o.y - th / 2.0, 0)
        draw_glyphs(0, text)


def _draw_annotations(context, region, rv3d):
    wall = active_wall(context)
    if wall is None or not show_option(context.scene, 'ANNOTATIONS')             or not _annotation_sources:
        return
    prims = _annotations(context.scene, wall)
    if not prims:
        return
    s = _s()

    def P(v):
        return view3d_utils.location_3d_to_region_2d(region, rv3d, v)

    lines = {}
    for pr in prims:
        if pr.get('kind') != 'LINES':
            continue
        pts = [P(v) for v in pr.get('points', ())]
        out = lines.setdefault(tuple(pr.get('color', ANNOTATION_LINE)), [])
        for a, b in zip(pts[0::2], pts[1::2]):
            if a is not None and b is not None:
                out += [(a.x, a.y), (b.x, b.y)]
    for color, pts in lines.items():
        if pts:
            _stroke(region, pts, 1.0 * s, color)
    _draw_bubbles(region, prims, P, s)
    blf.size(0, ANNOTATION_FONT_SIZE * s)
    lh = blf.dimensions(0, "Ag")[1] * 1.35
    for pr in prims:
        if pr.get('kind') != 'TEXT' or not pr.get('text'):
            continue
        o = P(pr['origin'])
        if o is None:
            continue
        tip = P(pr['origin'] + pr.get('x_axis', Vector((1, 0, 0))) * 0.1)
        # Text that reads straight out of the screen belongs to a face
        # seen edge-on here (the side of a panel): it is not drawn.
        if tip is None or (tip - o).length < 0.5:
            continue
        ang = math.atan2(tip.y - o.y, tip.x - o.x)
        # Read left to right or bottom to top, never upside down.
        if ang > math.pi / 2 + 1e-3 or ang < -math.pi / 2 - 1e-3:
            ang += math.pi
            ang = math.atan2(math.sin(ang), math.cos(ang))
        rows = pr['text'].splitlines()
        ca, sa = math.cos(ang), math.sin(ang)
        total = lh * len(rows)
        blf.color(0, *pr.get('color', TEXT))
        blf.enable(0, blf.SHADOW)
        blf.shadow(0, TEXT_HALO_BLUR, *TEXT_HALO)
        blf.shadow_offset(0, 0, 0)
        blf.enable(0, blf.ROTATION)
        blf.rotation(0, ang)
        for i, row in enumerate(rows):
            tw, th = blf.dimensions(0, row)
            align = pr.get('align', 'CENTER')
            dx = {'LEFT': 0.0, 'RIGHT': -tw}.get(align, -tw / 2.0)
            # Rows stack downward from a block centred on the origin.
            dy = total / 2.0 - lh * (i + 1) + (lh - th) / 2.0
            x = o.x + dx * ca - dy * sa
            y = o.y + dx * sa + dy * ca
            blf.position(0, x, y, 0)
            draw_glyphs(0, row)
        blf.disable(0, blf.ROTATION)
        blf.disable(0, blf.SHADOW)


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
    # Floating shelves and range hoods carry their own dims.
    group = [it for it in group if not it.shelf and not _is_hood(it)]
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

# A recess under a floor-standing cabinet taller than this is not a kick.
KICK_MAX = 0.3


def _kick_height(it):
    """The toe kick under a floor-standing cabinet, or 0.0 (an upper,
    an appliance, a flush kick that runs the front to the floor)."""
    obj = it.obj
    if it.kind != 'LOWER' or it.shelf or it.preview \
            or obj.get('IS_APPLIANCE'):
        return 0.0
    value = 0.0
    try:
        if obj.get('IS_FRAMELESS_CABINET_CAGE'):
            value = float(obj.get('Toe Kick Height') or 0.0)
        elif obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            ffc = getattr(obj, 'face_frame_cabinet', None)
            if ffc is not None and getattr(ffc, 'toe_kick_type', '') != 'FLUSH':
                value = float(getattr(ffc, 'toe_kick_height', 0.0) or 0.0)
    except Exception:
        return 0.0
    return value if MERGE < value < KICK_MAX else 0.0


def _shelf_stacks(items):
    """Floating shelves in stacks (shelves whose spans along the wall
    overlap), each stack bottom to top."""
    stacks = []
    for it in sorted((i for i in items if i.shelf and not i.preview),
                     key=lambda i: i.x0):
        for st in stacks:
            if it.x0 < max(o.x1 for o in st) - MERGE \
                    and it.x1 > min(o.x0 for o in st) + MERGE:
                st.append(it)
                break
        else:
            stacks.append([it])
    for st in stacks:
        st.sort(key=lambda i: i.z0)
    return stacks


# ---- Centerline sources ------------------------------------------------------------
# Where a wall's sinks and ranges centre, measured from a wall end. A
# source is fn(scene, wall, length) returning [{'x': along the wall,
# 'from_x': the end (or stop) it measures from, 'obj': the fixture's
# object name}], or None to leave it to the next source. With no source
# answering, sinks, ranges and cooktops measure from the nearer end.

_centerline_sources = []


def register_centerline_source(fn):
    if fn not in _centerline_sources:
        _centerline_sources.append(fn)
    _bump_gen()


def unregister_centerline_source(fn):
    if fn in _centerline_sources:
        _centerline_sources.remove(fn)
    _bump_gen()


CENTERLINE_APPLIANCES = ('RANGE', 'COOKTOP', 'SINK')


def _centerlines(scene, wall, length, items):
    for fn in list(_centerline_sources):
        try:
            got = fn(scene, wall, length)
        except Exception as exc:
            print(f"Elevation centerlines: {exc}")
            continue
        if got is not None:
            return got
    out = []
    for it in items:
        if it.kind != 'LOWER' or it.preview:
            continue
        obj = it.obj
        if obj.get('APPLIANCE_TYPE') not in CENTERLINE_APPLIANCES \
                and 'Sink' not in str(obj.get('CLASS_NAME', '')):
            continue
        x = (it.x0 + it.x1) / 2.0
        out.append({'x': x, 'from_x': 0.0 if x <= length - x else length,
                    'obj': obj.name})
    return out


def _merge(spans):
    out = []
    for a, b in sorted(spans):
        if out and a <= out[-1][1] + MERGE:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


_ff_box_cache = {}


def _face_frame_boxes(cabinet, Fi):
    """(x0, x1, z0, z1) in the wall frame of each built face frame member
    of a face frame cabinet (stiles, rails, mid stiles and rails). Kept
    until the scene next changes: the view asks every redraw."""
    key = (_gen, cabinet.name, tuple(round(v, 6) for row in Fi for v in row))
    hit = _ff_box_cache.get(key)
    if hit is None:
        if len(_ff_box_cache) > 256 or any(k[0] != _gen
                                           for k in _ff_box_cache):
            _ff_box_cache.clear()
        hit = _ff_box_cache[key] = _face_frame_boxes_now(cabinet, Fi)
    return hit


def _face_frame_boxes_now(cabinet, Fi):
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
        boxes.append((min(xs), max(xs), min(zs), max(zs), part))
    return boxes


def _wall_box(obj, Fi):
    """(x0, x1, z0, z1) of an object's bounds in the wall frame."""
    try:
        mw = obj.matrix_world
        pts = [Fi @ (mw @ Vector(c)) for c in obj.bound_box]
    except Exception:
        return None
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


def _front_drops(it, cols, fillers, Fi):
    """[(item, c0, c1, clear0, clear1, z_bot, z_top)] for each bay of a
    face frame cabinet whose front (top rail and stretcher) is dropped
    for a sink or cooktop: the bay's opening c0..c1, the clear width
    between its drop fillers, and the dropped band."""
    out = []
    for bay in it.obj.children:
        ffb = getattr(bay, 'face_frame_bay', None)
        if not bay.get('IS_FACE_FRAME_BAY_CAGE') or ffb is None:
            continue
        drop = getattr(ffb, 'front_drop', 0.0) or 0.0
        if drop <= MERGE:
            continue
        box = _wall_box(bay, Fi)
        if box is None:
            continue
        col = next(((c0, c1) for c0, c1 in cols
                    if box[0] - MERGE <= (c0 + c1) / 2.0 <= box[1] + MERGE),
                   None)
        if col is None:
            continue
        c0, c1 = col
        z_top = it.z0 + ffb.height
        mine = [b for b, part in fillers
                if part.get('hb_segment_start_bay') == bay.get('hb_bay_index')
                and c0 - MERGE <= (b[0] + b[1]) / 2.0 <= c1 + MERGE]
        mid = (c0 + c1) / 2.0
        clear0 = max([b[1] for b in mine if (b[0] + b[1]) / 2.0 < mid]
                     or [c0])
        clear1 = min([b[0] for b in mine if (b[0] + b[1]) / 2.0 >= mid]
                     or [c1])
        out.append((it, c0, c1, clear0, clear1, z_top - drop, z_top))
    return out


def _is_hood(it):
    return it.kind == 'UPPER' and it.obj.get('APPLIANCE_TYPE') == 'HOOD'


def _face_frame_layout(items, Fi):
    """Each face frame cabinet's frame, measured: {'lower': [(a, b, item)]
    the stile / opening segments of the floor-standing frames, 'upper':
    the same for uppers and talls, 'columns': [(item, x0, x1, zs)] the
    rail / opening breaks up each opening column, 'sections': [(item,
    x0, x1, z)] the end sections of an upper whose bays step, each
    across its stiles' outer edges, z its bottom}. A blind cabinet's
    hidden blind strip leads (or ends) its row's segments, so the chain
    reads blind, stile, opening ... to the cabinet's edge. 'drops':
    see _front_drops; a drop's filler stiles stand in the dropped band
    only, so they are not stiles of the frame."""
    out = {'lower': [], 'upper': [], 'columns': [], 'sections': [],
           'drops': [], 'stiles': {}}
    for it in items:
        if it.preview or it.shelf \
                or not it.obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            continue
        boxes = _face_frame_boxes(it.obj, Fi)
        fillers = [(b, b[4]) for b in boxes
                   if b[4].get('hb_part_role') == 'FRONT_DROP_FILLER']
        boxes = [b for b in boxes
                 if b[4].get('hb_part_role') != 'FRONT_DROP_FILLER']
        if not boxes:
            continue
        fx0 = min(b[0] for b in boxes)
        fx1 = max(b[1] for b in boxes)
        fz0 = min(b[2] for b in boxes)
        fz1 = max(b[3] for b in boxes)
        verticals = [b for b in boxes if (b[3] - b[2]) > (b[1] - b[0])]
        rails = [b for b in boxes if (b[3] - b[2]) <= (b[1] - b[0])]
        stiles = _merge([(b[0], b[1]) for b in verticals])
        xs = _chain([v for a, b in stiles for v in (a, b)], fx0, fx1)
        row = 'upper' if (it.kind == 'UPPER' or it.tall) else 'lower'
        segs = [(a, b, it) for a, b in zip(xs, xs[1:])]
        # Which stile each stile segment is, for where its value sits:
        # the frame's left end, its right end, or one between.
        for a, b in stiles:
            out['stiles'][(it.name, round(a, 4))] = (
                'L' if abs(a - fx0) <= MERGE
                else 'R' if abs(b - fx1) <= MERGE else 'M')
        ffc = getattr(it.obj, 'face_frame_cabinet', None)
        if ffc is not None and (getattr(ffc, 'blind_left', False)
                                or getattr(ffc, 'blind_right', False)):
            # The frame stops short of the cage on the blind side.
            if fx0 - it.x0 > MERGE:
                segs.insert(0, (it.x0, fx0, it))
            if it.x1 - fx1 > MERGE:
                segs.append((fx1, it.x1, it))
        out[row] += segs
        # A frame standing on a kick: its column chains start at the
        # floor, so the kick reads with the rails above it.
        kick = it.kind == 'LOWER' and MERGE < fz0 < KICK_MAX
        cols = []
        prev = fx0
        for a, b in stiles:
            if a - prev > MERGE:
                cols.append((prev, a))
            prev = max(prev, b)
        if fx1 - prev > MERGE:
            cols.append((prev, fx1))
        bottoms = []
        for c0, c1 in cols:
            mid = (c0 + c1) / 2.0
            spans = _merge([(b[2], b[3]) for b in rails
                            if b[0] <= mid <= b[1]])
            bottoms.append(spans[0][0] if spans else fz0)
            zs = _chain([v for a, b in spans for v in (a, b)], fz0, fz1)
            if kick:
                zs = [0.0] + zs
            if len(zs) >= 3:
                out['columns'].append((it, c0, c1, zs))
        if it.kind == 'UPPER' and len(cols) >= 2:
            out['sections'] += _upper_sections(it, cols, bottoms, stiles)
        if it.kind == 'LOWER':
            out['drops'] += _front_drops(it, cols, fillers, Fi)
    return out


def _upper_sections(it, cols, bottoms, stiles):
    """The two end sections of an upper whose openings step up (over an
    appliance) or down (to the counter): runs of neighbouring openings
    sharing a bottom. Each spans the outer edges of the stiles either
    side of it, a mid stile counting in both sections it bounds, the
    way a field measurer reads each section. A middle section is left
    out; the ends are what get checked against the cabinets below."""
    runs = []
    for i, z in enumerate(bottoms):
        if runs and abs(z - bottoms[runs[-1][0]]) <= MERGE:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    if len(runs) < 2:
        return []

    def outer(x, left):
        for a, b in stiles:
            if left and abs(b - x) <= MERGE:
                return a
            if not left and abs(a - x) <= MERGE:
                return b
        return x

    out = []
    for first, last in (runs[0], runs[-1]):
        x0 = outer(cols[first][0], True)
        x1 = outer(cols[last][1], False)
        out.append((it, x0, x1, min(bottoms[first:last + 1])))
    return out


# Face frame height chains each side of the wall may take, as lines.
FF_SIDE_TIERS = 1


def _pack_face_frame_sides(columns, length):
    """({1: tiers, -1: tiers}, columns left on the frame). Columns with
    the same rail breaks (same heights off the floor) make one chain.
    Each side holds one line, and the cabinet standing at that end of
    the wall has first call on it: chains go out nearest end first,
    the more shared ahead on a tie, to the side they stand nearest,
    else the other side. A tier is a list of (zs, item) whose height
    ranges don't overlap, so an upper's chain and a base's share the
    line. A second line out there would read as belonging to the end
    cabinet, so a chain that finds no room is dimensioned on its own
    bay instead."""
    groups = {}
    for col in columns:
        groups.setdefault(tuple(round(z, 4) for z in col[3]), []).append(col)

    def nearest(cols):
        """(distance to a wall end, that side, the column)."""
        ends = [(c[1], -1, c) for c in cols]
        ends += [(length - c[2], 1, c) for c in cols]
        return min(ends, key=lambda t: t[0])

    def order(kv):
        return (round(nearest(kv[1])[0], 3), -len(kv[1]))

    tiers = {1: [], -1: []}
    left = []
    for _sig, cols in sorted(groups.items(), key=order):
        zs = cols[0][3]
        _dist, pref, col = nearest(cols)
        owner = col[0]
        placed = False
        for side in (pref, -pref):
            for tr in tiers[side]:
                if all(zs[-1] <= o[0] + MERGE or zs[0] >= o[-1] - MERGE
                       for o, _it in tr):
                    tr.append((zs, owner))
                    placed = True
                    break
            if not placed and len(tiers[side]) < FF_SIDE_TIERS:
                tiers[side].append([(zs, owner)])
                placed = True
            if placed:
                break
        if not placed:
            left.extend(cols)
    return tiers, left


def _face_frame_height_dims(columns, dims, sx, sy, s):
    """Rails and openings up each opening column, on the frame. A column
    whose breaks repeat one already dimensioned (the next door of a
    run, the other bay of a cabinet) is not dimensioned again. Values
    read horizontally, beside their line, the way the sheets show
    them."""
    inset = FF_INSET_PX * s
    done = set()
    for it, c0, c1, zs in sorted(columns, key=lambda c: c[1]):
        sig = tuple(round(z, 4) for z in zs)
        if sig in done:
            continue
        if abs(sx(c1) - sx(c0)) < 2 * inset:
            continue
        done.add(sig)
        x = sx(c0) + inset
        for a, b in zip(zs, zs[1:]):
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': x,
                         'side': 1, 'value': b - a, 'target': None,
                         'item': it, 'w0': a, 'horiz': True,
                         'key': ('FF_H', it.name, round(c0, 4),
                                 round(a, 4))})


def _layout(context, region, rv3d):
    """Every dimension on screen, its text placed. Shared by draw and
    click so hits cannot drift from pixels."""
    wall = active_wall(context)
    if wall is None:
        return [], None
    return _layout_wall(context.scene, wall, region, rv3d,
                        selected={o.name for o in context.selected_objects})


def _layout_wall(scene, wall, region, rv3d, selected=(), extra=None,
                 preview=None, face_frame=None):
    """_layout for any wall of `scene`, through any view. `extra` and
    `preview` as _items; `face_frame` overrides the scene's Face Frame
    toggle."""
    if rv3d is None:
        return [], None
    fr = _frame(wall)
    if fr is None:
        return [], None
    F, _Fi, length, height = fr
    s = _s()
    items = _items(scene, wall, extra, preview)
    if face_frame is None:
        face_frame = show_option(scene, 'FACE_FRAME')

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
    # Measured always (a stepped upper's sections show either way); the
    # frame's own chains only with Face Frame on.
    ff_all = _face_frame_layout(items, fr[1])
    ff = ff_all if face_frame else None

    def add_ff_widths(segs, pos, from_y, side):
        """A face frame chain: stile, opening, stile ... of each face
        frame in the row, read only."""
        ends = set()
        for a, b, it in segs:
            for x in (a, b):
                k = round(x, 4)
                if k in ends:
                    continue
                ends.add(k)
                fy = from_y(x)
                dims_ext.append(((sx(x), fy + side * gap),
                                 (sx(x), pos + side * over)))
            dims.append({'axis': 'H', 'a': sx(a), 'b': sx(b), 'pos': pos,
                         'side': side, 'value': b - a, 'target': None,
                         'item': it, 'w0': a,
                         'stile': ff_all['stiles'].get(
                             (it.name, round(a, 4))),
                         'key': ('FF_W', it.name, round(a, 4))})

    # Below the floor: the face frames' stiles and openings, the
    # floor-standing run, then the overall length.
    # Closet bays read in the same row, nearest the work: each bay on
    # its own (the panels between them are not dimensioned), below the
    # floor for a floor run, above the wall for a hanging one.
    closet_low, closet_up = [], []
    for it in items:
        row = closet_low if it.z0 < KICK_MAX else closet_up
        row += [(a, b, it) for a, b in _closet_bays(it, fr[1], wall)]
    t = 0
    detail = (ff['lower'] if ff else []) + closet_low
    if detail:
        add_ff_widths(detail, floor_y - first, lambda x: floor_y, -1)
        t += 1
    if lower:
        pts = _chain([v for it in lower for v in (it.x0, it.x1)], 0.0, length)
        add_h(pts, floor_y - first - t * tier, lambda x: floor_y, -1, lower,
              item_of=item_between(lower))
        t += 1
    add_h([0.0, length], floor_y - first - t * tier, lambda x: floor_y, -1,
          [], read_only=True)

    # Above the wall: uppers and talls, then windows and doors.
    top_z = max([height] + [it.z1 for it in items])
    top_y = sy(top_z)
    t = 0
    detail = (ff['upper'] if ff else []) + closet_up
    if detail:
        def from_ff_top(x, detail=detail):
            zs = [it.z1 for _a, _b, it in detail
                  if it.x0 - MERGE <= x <= it.x1 + MERGE]
            return sy(max(zs)) if zs else sy(height)
        add_ff_widths(detail, top_y + first, from_ff_top, 1)
        t += 1
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
    mid = length / 2.0
    left_group = [it for it in products if (it.x0 + it.x1) / 2.0 < mid]
    right_group = [it for it in products if (it.x0 + it.x1) / 2.0 >= mid]
    right_x = sx(max([wx1] + [it.x1 for it in items]))
    left_x = sx(min([wx0] + [it.x0 for it in items]))

    # Face frame rails and openings stand out past the wall's ends,
    # nearest the work: one chain per distinct column set-up, on the
    # side of the wall its cabinets are on, chains at different heights
    # sharing a line. What doesn't fit stays on the frame.
    side_tiers, on_frame = (_pack_face_frame_sides(ff['columns'], length)
                            if ff else ({1: [], -1: []}, []))
    # Toe kicks the face frame chains don't already carry: one per
    # distinct kick on each half, sharing a line with a chain clear of
    # the floor, else on a line of its own nearest the wall.
    covered = {id(c[0]) for c in ff['columns']} if ff else set()
    for side, group in ((-1, left_group), (1, right_group)):
        seen = set()
        for it in sorted(group, key=lambda i: i.x0):
            k = 0.0 if id(it) in covered else _kick_height(it)
            if not k or round(k, 4) in seen:
                continue
            seen.add(round(k, 4))
            zs = [0.0, k]
            for tr in side_tiers[side]:
                if all(k <= o[0] + MERGE for o, _it in tr):
                    tr.append((zs, it))
                    break
            else:
                side_tiers[side].insert(0, [(zs, it)])

    # Closet panels: each distinct panel height once per side, out past
    # the wall's end on the side its run stands on, sharing a line with
    # a chain it clears, else on a line of its own.
    for side, group in ((-1, left_group), (1, right_group)):
        seen = set()
        for it in sorted(group, key=lambda i: i.x0):
            for z0, z1 in _closet_panel_heights(it, fr[1]):
                k = round((z1 - z0) / 0.0015875)
                if k in seen:
                    continue
                seen.add(k)
                zs = [z0, z1]
                for tr in side_tiers[side]:
                    if all(z1 <= o[0] + MERGE or z0 >= o[-1] - MERGE
                           for o, _it in tr):
                        tr.append((zs, it))
                        break
                else:
                    side_tiers[side].append([(zs, it)])

    pad = TEXT_GAP_PX * s
    blf.size(0, FONT_SIZE * s)
    th = blf.dimensions(0, "0123456789\"")[1]

    v_clear = (TICK_PX + 3) * 2 * s + 2 * BREAK_GAP_PX * s
    reach = {}

    def v_line(side, segs):
        """Screen x of the next vertical chain out on `side`: its values
        sit centred on the line when they fit and beside it, outward,
        when they don't, so it stands clear of the chain inside it."""
        w, beside = 0.0, False
        for a, b in segs:
            w = max(w, value_runs(format_length(scene, b - a),
                                  FONT_SIZE * s, _blf_measure)[1])
            if abs(sy(b) - sy(a)) < th + v_clear:
                beside = True
        pos = reach[side] + side * max(w / 2.0 + pad, 0.0)
        reach[side] = pos + side * ((w + 2 * pad) if beside
                                    else (w / 2.0 + pad))
        return pos

    def ff_side(side, edge):
        reach[side] = edge + side * (first - pad)
        ex = sx(wx1) if side > 0 else sx(wx0)
        kicks = set()
        for tr in side_tiers[side]:
            segs = []
            for zs, _it in tr:
                for a, b in zip(zs, zs[1:]):
                    if a <= MERGE and b < KICK_MAX and round(b, 4) in kicks:
                        continue
                    segs.append((a, b))
            cursor = v_line(side, segs)
            for zs, it in tr:
                for z in zs:
                    dims_ext.append(((ex + side * gap, sy(z)),
                                     (cursor + side * over, sy(z))))
                for a, b in zip(zs, zs[1:]):
                    if a <= MERGE and b < KICK_MAX:
                        # One kick per side: the next chain out starts
                        # its values at the kick's top.
                        if round(b, 4) in kicks:
                            continue
                        kicks.add(round(b, 4))
                    dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b),
                                 'pos': cursor, 'side': side,
                                 'value': b - a, 'target': None,
                                 'item': it, 'w0': a, 'horiz': True,
                                 'outward': True,
                                 'key': ('FF_S', side, round(cursor),
                                         round(a, 4))})

    ff_side(1, right_x)
    ff_side(-1, left_x)

    def pairs(levels):
        return list(zip(levels, levels[1:]))

    levels = _height_levels(right_group, height)
    if len(levels) > 2:
        add_v(levels, v_line(1, pairs(levels)), 1, right_group)
    add_v([0.0, height], v_line(1, [(0.0, height)]), 1, [], overall=True)

    # Left: the left half's height chain, then window and door sills
    # and heads.
    levels = _height_levels(left_group, height)
    if len(levels) > 2:
        add_v(levels, v_line(-1, pairs(levels)), -1, left_group)
    if openings:
        lv = {0.0, height}
        for it in openings:
            lv.update((max(it.z0, 0.0), it.z1))
        lv = _chain(lv, 0.0, max(lv))
        add_v(lv, v_line(-1, pairs(lv)), -1, openings)

    if ff:
        _face_frame_height_dims(on_frame, dims, sx, sy, s)

    # A stepped upper: the overall width of each end section, just
    # under it, so a raised section reads against what stands below.
    for it, x0, x1, z in ff_all['sections']:
        pos = sy(z) - first
        for x in (x0, x1):
            dims_ext.append(((sx(x), sy(z) - gap), (sx(x), pos - over)))
        dims.append({'axis': 'H', 'a': sx(x0), 'b': sx(x1), 'pos': pos,
                     'side': -1, 'value': x1 - x0, 'target': None,
                     'item': it, 'w0': x0,
                     'key': ('SECTION', it.name, round(x0, 4))})

    # A sink or cooktop front drop: the drop down the middle of the
    # clear band, always; with Face Frame on, the drop fillers and the
    # clear width between them just above the bay.
    cl_rows = []
    for it, c0, c1, clear0, clear1, z_bot, z_top in ff_all['drops']:
        dims.append({'axis': 'V', 'a': sy(z_bot), 'b': sy(z_top),
                     'pos': sx((clear0 + clear1) / 2.0), 'side': 1,
                     'value': z_top - z_bot, 'target': None, 'item': it,
                     'w0': z_bot, 'horiz': True,
                     'key': ('DROP', it.name, round(c0, 4))})
        if ff is None or (clear0 - c0 <= MERGE and c1 - clear1 <= MERGE):
            continue
        pos = sy(z_top) + first
        pts = _chain([c0, clear0, clear1, c1], c0, c1)
        for x in pts:
            dims_ext.append(((sx(x), sy(z_top) + gap), (sx(x), pos + over)))
        for a, b in zip(pts, pts[1:]):
            dims.append({'axis': 'H', 'a': sx(a), 'b': sx(b), 'pos': pos,
                         'side': 1, 'value': b - a, 'target': None,
                         'item': it, 'w0': a,
                         'key': ('DROP_W', it.name, round(a, 4))})
        # The CL over this fixture steps up past the filler chain.
        cl_rows.append((0, it.z1, c0, c1))

    # A range hood: its height on its open side (the side no upper
    # butts), else down its middle. Its width rides the upper chain.
    uppers = [u for u in items if u.kind == 'UPPER' and not _is_hood(u)]
    for it in items:
        if not _is_hood(it) or it.preview:
            continue

        def butts(x):
            return any(u.x0 - MERGE <= x <= u.x1 + MERGE
                       and u.z0 < it.z1 and u.z1 > it.z0 for u in uppers)
        if not butts(it.x1):
            pos, side = sx(it.x1) + first, 1
        elif not butts(it.x0):
            pos, side = sx(it.x0) - first, -1
        else:
            pos, side = sx((it.x0 + it.x1) / 2.0), 1
        for z in (it.z0, it.z1):
            edge = sx(it.x1) if side > 0 else sx(it.x0)
            if abs(pos - edge) > first / 2.0:
                dims_ext.append(((edge + side * gap, sy(z)),
                                 (pos + side * over, sy(z))))
        dims.append({'axis': 'V', 'a': sy(it.z0), 'b': sy(it.z1),
                     'pos': pos, 'side': side, 'value': it.z1 - it.z0,
                     'target': None, 'item': it, 'w0': it.z0,
                     'horiz': True, 'outward': True,
                     'key': ('HOOD', it.name)})

    # Sink and range centerlines, from the wall end they measure off,
    # just above the fixture. Lines that would overlap step up.
    by_name = {it.name: it for it in items}
    counter = max([it.z1 for it in lower if not it.tall] or [0.0])
    for cl in sorted(_centerlines(scene, wall, length, items),
                     key=lambda c: abs(c['x'] - c['from_x'])):
        x, x_end = cl['x'], cl['from_x']
        if abs(x - x_end) <= MERGE:
            continue
        it = by_name.get(cl.get('obj'))
        top = it.z1 if it is not None else counter
        lo, hi = min(x, x_end), max(x, x_end)
        row = 0
        while any(r == row and abs(z - top) <= MERGE
                  and lo < h - MERGE and hi > l + MERGE
                  for r, z, l, h in cl_rows):
            row += 1
        cl_rows.append((row, top, lo, hi))
        pos = sy(top) + first + row * tier
        dims_ext.append(((sx(x), sy(top) + gap), (sx(x), pos + over)))
        dims_ext.append(((sx(x_end), pos - 2 * over),
                         (sx(x_end), pos + over)))
        dims.append({'axis': 'H', 'a': sx(x_end), 'b': sx(x), 'pos': pos,
                     'side': 1, 'value': hi - lo, 'target': None,
                     'item': it, 'w0': lo, 'suffix': " CL",
                     'key': ('CL', cl.get('obj'), round(x, 4))})

    # Floating shelves: per stack, floor to the lowest shelf, then each
    # shelf and the clear gap above it, inside the stack's right end.
    for st in _shelf_stacks(items):
        zs = _chain([0.0] + [z for it in st for z in (it.z0, it.z1)],
                    0.0, max(it.z1 for it in st))
        x = sx(max(it.x1 for it in st)) - FF_INSET_PX * s
        for a, b in zip(zs, zs[1:]):
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': x,
                         'side': -1, 'value': b - a, 'target': None,
                         'item': st[0], 'w0': a, 'horiz': True,
                         'outward': True,
                         'key': ('SHELF', st[0].name, round(a, 4))})

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

    _place_text(scene, dims, region, dims_ext)
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


def _place_text(scene, dims, region, ext=()):
    s = _s()
    blf.size(0, FONT_SIZE * s)
    th = blf.dimensions(0, "0123456789\"")[1]
    pad = TEXT_GAP_PX * s
    # A value fits between its ticks with this much clear either side.
    clear = (TICK_PX + 3) * 2 * s
    gap = BREAK_GAP_PX * s
    placed = []
    pending = []
    for d in dims:
        if d['axis'] == 'V':
            d['horiz'] = True   # every value reads left to right
        d['text'] = format_length(scene, d['value']) + d.get('suffix', '')
        tw = value_runs(d['text'], FONT_SIZE * s, _blf_measure)[1]
        span = abs(d['b'] - d['a'])
        lo, hi = min(d['a'], d['b']), max(d['a'], d['b'])
        mid = (lo + hi) / 2.0
        if d['axis'] == 'H':
            base = d['pos'] + pad
            cands = []
            if tw + clear + 2 * gap <= span:
                # Long enough: the value sits in a break in the line.
                cands.append((mid - tw / 2.0, d['pos'] - th / 2.0))
            if tw + clear <= span:
                cands.append((mid - tw / 2.0, base))
            under = d['pos'] - pad - th
            # A stile too narrow for its value: an end stile's value
            # steps in over its own cabinet (the left stile's to the
            # right, the right stile's to the left), and a stile
            # between two openings carries its value straight above it.
            # They sit on the line's open side, away from the work: over
            # the line in the row above the wall, under it in the row
            # below the floor (where the extension lines come down to
            # the line and would run through a value set over it). They
            # stand a little further off the line than other values,
            # clear of an opening's value set in the line beside them,
            # so the two never crowd each other out.
            stile = d.get('stile')
            if stile:
                over_s = d['pos'] + th / 2.0 + 3.0
                under_s = d['pos'] - th / 2.0 - 3.0 - th
                near, far = ((over_s, under_s) if d['side'] > 0
                             else (under_s, over_s))
                centred = [(mid - tw / 2.0, near), (mid - tw / 2.0, far)]
                if stile == 'L':
                    cands += [(hi + 4 * s, near)] + centred
                elif stile == 'R':
                    cands += [(lo - 4 * s - tw, near)] + centred
                else:
                    cands += centred
            cands += [(hi + 4 * s, base), (lo - 4 * s - tw, base),
                      (mid - tw / 2.0,
                       under if d['side'] < 0 else base + th + pad),
                      # Last resorts: past either end on the line's
                      # other side, then a second row.
                      (hi + 4 * s, under), (lo - 4 * s - tw, under),
                      (mid - tw / 2.0,
                       base + th + pad if d['side'] < 0
                       else under)]
            rects = [(x, y, tw, th) for x, y in cands]
        elif d.get('horiz'):
            # Read horizontally beside the line, as the sheets do: to its
            # right at mid height, else left, else past its ends.
            x_r = d['pos'] + pad
            x_l = d['pos'] - pad - tw
            # Tall enough: centred in a break in the line.
            inline = ([(d['pos'] - tw / 2.0, mid - th / 2.0)]
                      if th + clear + 2 * gap <= span else [])
            if d.get('outward'):
                # Out past the wall: the value stays on the open side.
                xo = x_r if d['side'] > 0 else x_l
                # A crowded run then steps to the side towards the
                # wall rather than set one value on another.
                xi = x_l if d['side'] > 0 else x_r
                cands = inline + [(xo, mid - th / 2.0), (xo, hi + 2 * s),
                                  (xo, lo - 2 * s - th),
                                  (xi, mid - th / 2.0),
                                  (xo, hi + 4 * s + th),
                                  (xo, lo - 4 * s - 2 * th),
                                  (xi, hi + 2 * s), (xi, lo - 2 * s - th)]
            else:
                cands = inline + [(x_r, mid - th / 2.0),
                                  (x_l, mid - th / 2.0),
                                  (x_r, hi + 2 * s), (x_r, lo - 2 * s - th),
                                  (x_l, hi + 2 * s), (x_l, lo - 2 * s - th)]
            rects = [(x, y, tw, th) for x, y in cands]
        else:
            # Rotated a quarter turn: the value reads up the line from
            # its outer side, so it occupies th wide x tw tall.
            x_text = d['pos'] - pad if d['side'] > 0 else d['pos'] - pad
            cands = []
            if tw + clear + 2 * gap <= span:
                cands.append((d['pos'] - th / 2.0, mid - tw / 2.0))
            if tw + clear <= span:
                cands.append((x_text - th, mid - tw / 2.0))
            cands += [(x_text - th, hi + 4 * s), (x_text - th, lo - 4 * s - tw)]
            rects = [(x, y, th, tw) for x, y in cands]
        fits = d.get('horiz') or tw + clear <= span
        need = tw if d['axis'] == 'H' else th
        inline = need + clear + 2 * gap <= span
        pending.append((0 if fits else 1, len(pending), d, rects, inline))
    # A value that fits between its ticks has one good spot; it claims
    # it before a neighbour too narrow for its own value spills over.
    # Extension lines run out past every chain inside the one they
    # belong to; a value is kept off them where it has the choice.
    lines = [(min(a[0], b[0]), min(a[1], b[1]),
              max(a[0], b[0]), max(a[1], b[1])) for a, b in ext]
    t = 1.5 * s

    def struck(r):
        x0, y0, x1, y1 = r[0] + t, r[1] + t, r[0] + r[2] - t, r[1] + r[3] - t
        return any(lx0 < x1 and lx1 > x0 and ly0 < y1 and ly1 > y0
                   for lx0, ly0, lx1, ly1 in lines)

    for _order, _i, d, rects, inline in sorted(pending,
                                                key=lambda p: p[:2]):
        free = [r for r in rects
                if not any(_rects_overlap(r, p) for p in placed)]
        chosen = next((r for r in free if not struck(r)),
                      free[0] if free else rects[0])
        d['rect'] = chosen
        d['inline'] = inline and chosen is rects[0]
        placed.append(chosen)


# ---- Drawing -----------------------------------------------------------------------

def _stroke(region, pts, width, color):
    """A line with a dark halo under it, so it reads on any background."""
    hb_dim_style.stroke(region, pts, width, color, _s(), halo=HALO)


def _tick(x, y, s):
    t = TICK_PX * s
    return [(x - t, y - t), (x + t, y + t)]


def _dim_lines(d, s):
    """(line, ticks) as point pairs; a value set in the line breaks
    it."""
    lo, hi = min(d['a'], d['b']), max(d['a'], d['b'])
    spans = [(lo, hi)]
    if d.get('inline') and d.get('rect'):
        x, y, w, h = d['rect']
        t0, t1 = (x, x + w) if d['axis'] == 'H' else (y, y + h)
        g = BREAK_GAP_PX * s
        spans = [(lo, t0 - g), (t1 + g, hi)]
    if d['axis'] == 'H':
        y = d['pos']
        line = [p for a, b in spans for p in ((a, y), (b, y))]
        ticks = _tick(d['a'], y, s) + _tick(d['b'], y, s)
    else:
        x = d['pos']
        line = [p for a, b in spans for p in ((x, a), (x, b))]
        ticks = _tick(x, d['a'], s) + _tick(x, d['b'], s)
    return line, ticks


def _text(d, color, s, halo=TEXT_HALO, plain=False):
    """A dimension's value at its rect. `plain` sets the text as typed
    (the edit field), with no small fraction."""
    x, y, w, h = d['rect']
    blf.size(0, FONT_SIZE * s)
    blf.color(0, *color)
    blf.enable(0, blf.SHADOW)
    blf.shadow(0, TEXT_HALO_BLUR if halo is TEXT_HALO else 5, *halo)
    blf.shadow_offset(0, 0, 0)
    if d['axis'] == 'V' and not d.get('horiz'):
        blf.enable(0, blf.ROTATION)
        blf.rotation(0, math.pi / 2.0)
        blf.position(0, x + w, y, 0)
        draw_glyphs(0, d['text'])
    elif plain:
        blf.position(0, x, y, 0)
        draw_glyphs(0, d['text'])
    else:
        runs, _width = value_runs(d['text'], FONT_SIZE * s, _blf_measure)
        for text, dx, dy, size in runs:
            blf.size(0, size)
            blf.position(0, x + dx, y + dy, 0)
            draw_glyphs(0, text)
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
    print_label = "Print PDF"
    print_w = blf.dimensions(0, print_label)[0] + 24 * s
    gap = 3 * s
    many = len(walls) > 1
    chips = [('SHOW:' + key, label, h)
             for key, label, _default in SHOW_OPTIONS
             if _option_available(key)]
    total = title_w + exit_w + gap + (2 * (arrow_w + gap) if many else 0)         + sum(w + gap for _p, _l, w in chips) + print_w + gap
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
    parts.append(('PRINT', (x, y, print_w, h), print_label))
    x += print_w + gap
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
        glyph = (_SHOW_GLYPHS.get(part[5:]) if part.startswith('SHOW:')
                 else None)
        if glyph is not None:
            glyph(shader, rect, Theme.TEXT_PRIMARY if hovered or on
                  else Theme.TEXT_NORMAL)
            shader.bind()
            if hovered:
                _draw_chip_hint(shader, rect, label)
        elif part in ('PREV', 'NEXT'):
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


def _draw_chip_hint(shader, rect, label):
    """The icon chip's name, in a small tag above it."""
    s = _s()
    rx, ry, rw, rh = rect
    blf.size(0, 11 * s)
    tw = blf.dimensions(0, label)[0]
    th = blf.dimensions(0, "Ag")[1]
    w, h = tw + 14 * s, th + 10 * s
    x = rx + (rw - w) / 2.0
    y = ry + rh + 6 * s
    draw_soft_shadow(shader, x, y, w, h, 4 * s)
    draw_round_rect(shader, x, y, w, h, 4 * s, Theme.BTN_BG)
    blf.color(0, *Theme.TEXT_PRIMARY)
    blf.position(0, x + 7 * s, y + (h - th) / 2.0 + 1, 0)
    draw_glyphs(0, label)


def _draw():
    if _state is None or _print_scale is not None:
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
            try:
                _draw_interiors(context, region, extra, s)
            except Exception as exc:
                print(f"Elevation interior lines: {exc}")
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
                _text(shown, EDIT_TEXT, s, EDIT_HALO, plain=True)
                continue
            hot = _hover == ('DIM', d['key']) and d['target'] is not None
            color = HOVER_TEXT if hot else (TEXT if d['target'] is not None
                                       else TEXT_READONLY)
            _text(d, color, s)
        try:
            _draw_annotations(context, region, rv3d)
        except Exception as exc:
            print(f"Elevation annotations: {exc}")
        _draw_bar(context, area)
        gpu.state.blend_set('NONE')

    try:
        from . import viewport_hud
        viewport_hud.paint_clear_of_panel(context, area, paint)
    except Exception:
        paint()


# ---- Print -----------------------------------------------------------------------

PRINT_PAPER = {'TABLOID': (17 * 72.0, 11 * 72.0),
               'LETTER': (11 * 72.0, 8.5 * 72.0)}
PRINT_MARGIN = 36.0         # pt round the drawing
PRINT_TITLE = 30.0          # pt strip along the bottom for the title
PRINT_TEXT_SCALE = 0.75     # screen px -> pt for text, tiers and strokes
# Drafting scales, 1:n, and how each is written (inches to the foot).
PRINT_SCALES = ((8, '1 1/2"'), (12, '1"'), (16, '3/4"'), (24, '1/2"'),
                (32, '3/8"'), (48, '1/4"'), (64, '3/16"'), (96, '1/8"'),
                (128, '3/32"'))
PRINT_OUTLINE = (0.55, 0.55, 0.58)
_PRINT_DEPTH = 20.0         # m the print camera stands in front of the wall


class _PrintRegion:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class _PrintView:
    """What _layout and the projection helpers read off a region's view."""
    is_perspective = False
    view_perspective = 'ORTHO'

    def __init__(self, view, proj):
        self.view_matrix = view
        self.window_matrix = proj
        self.perspective_matrix = proj @ view


def _print_view(Fi, k, ox, oy, W, H):
    """An orthographic view square onto the wall: k pt to the metre, the
    wall's start at (ox, oy) on a W x H pt page."""
    from mathutils import Matrix
    d = _PRINT_DEPTH
    # Wall frame (x along, y into the wall, z up) to camera space.
    look = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, -d),
                   (0, 0, 0, 1)))
    far = 2.0 * d
    proj = Matrix(((2 * k / W, 0, 0, 2 * ox / W - 1),
                   (0, 2 * k / H, 0, 2 * oy / H - 1),
                   (0, 0, -2 / far, -1),
                   (0, 0, 0, 1)))
    view = _PrintView(look @ Fi, proj)
    view.k, view.ox, view.oy = k, ox, oy
    return view


def _front_names(scene, wall):
    """Names of the roots standing in front of `wall` (_items' extra)."""
    fr = _frame(wall)
    if fr is None:
        return []
    _F, Fi, length, height = fr
    return [o.name for o in _in_front_roots(scene, wall, Fi, length, height)]


def wall_view(wall, k, ox, oy, width, height):
    """An orthographic view square onto `wall` for layout_wall: k units
    to the metre, the wall's start at (ox, oy) on a width x height sheet
    with its origin bottom left. None for a wall without a frame."""
    fr = _frame(wall)
    if fr is None:
        return None
    return _print_view(fr[1], k, ox, oy, width, height)


def layout_wall(scene, wall, view, width, height, scale=1.0,
                face_frame=None):
    """The dimensions of `wall` laid out on a width x height sheet,
    whether or not an elevation is on screen: (dims, extra) as the view
    draws them, in sheet units with the origin bottom left.

    `view` is wall_view's, or anything with a `perspective_matrix` that
    takes world space to the sheet's -1..1 square. `scale` sizes the
    tiers, ticks and text (1.0 = the view's sizes in sheet units).
    `face_frame` overrides the scene's Face Frame toggle."""
    global _print_scale
    saved = _print_scale
    _print_scale = scale
    try:
        return _layout_wall(scene, wall, _PrintRegion(width, height), view,
                            extra=_front_names(scene, wall), preview=(),
                            face_frame=face_frame)
    finally:
        _print_scale = saved


def _print_layout(scene, wall, region, view, extra=None):
    dims, extra = _layout_wall(scene, wall, region, view, extra=extra)
    return [d for d in dims if d['key'][0] != 'SEL'], extra


def _print_bounds(dims, extra, k, L, H):
    sx, sy = extra['sx'], extra['sy']
    xs = [sx(0.0), sx(L)]
    ys = [sy(0.0), sy(H)]
    for d in dims:
        x, y, w, h = d['rect']
        xs += [x, x + w]
        ys += [y, y + h]
        if d['axis'] == 'H':
            xs += [d['a'], d['b']]
            ys.append(d['pos'])
        else:
            ys += [d['a'], d['b']]
            xs.append(d['pos'])
    for a, b in extra['ext']:
        xs += [a[0], b[0]]
        ys += [a[1], b[1]]
    return min(xs), max(xs), min(ys), max(ys)


def layout_pads(wall, dims, extra):
    """How far layout_wall's dimensions reach past the wall's own
    rectangle, in sheet units: (left, right, bottom, top). They are set
    by the tiers and the values, not by where the wall sits on the
    sheet, so a sheet can be sized and the wall placed from them."""
    fr = _frame(wall)
    if fr is None or extra is None:
        return 0.0, 0.0, 0.0, 0.0
    _F, _Fi, length, height = fr
    x0, x1, y0, y1 = _print_bounds(dims, extra, None, length, height)
    sx, sy = extra['sx'], extra['sy']
    return (sx(0.0) - x0, x1 - sx(length), sy(0.0) - y0, y1 - sy(height))


def _print_fit(scene, wall, W, H, extra=None):
    """(view, scale label) that fits the wall and every dimension on the
    page at the largest drafting scale that will go."""
    _F, Fi, L, Hw = _frame(wall)
    region = _PrintRegion(W, H)
    area_w = W - 2 * PRINT_MARGIN
    area_h = H - 2 * PRINT_MARGIN - PRINT_TITLE
    k0 = 0.5 * min(area_w / L, area_h / Hw)
    view = _print_view(Fi, k0, PRINT_MARGIN, PRINT_MARGIN + PRINT_TITLE,
                       W, H)
    front = extra
    dims, extra = _print_layout(scene, wall, region, view, front)
    x0, x1, y0, y1 = _print_bounds(dims, extra, k0, L, Hw)
    # The dimension tiers keep their size in pt whatever the scale.
    pad_l = extra['sx'](0.0) - x0
    pad_b = extra['sy'](0.0) - y0
    extra_w = (x1 - x0) - k0 * L
    extra_h = (y1 - y0) - k0 * Hw
    k = min((area_w - extra_w) / L, (area_h - extra_h) / Hw)
    label = None
    for n, text in PRINT_SCALES:
        pt_per_m = 72.0 / 0.0254 / n
        if pt_per_m <= k:
            k, label = pt_per_m, f"{text} = 1'-0\""
            break
    ox = PRINT_MARGIN + (area_w - (k * L + extra_w)) / 2.0 + pad_l
    oy = (PRINT_MARGIN + PRINT_TITLE
          + (area_h - (k * Hw + extra_h)) / 2.0 + pad_b)
    return _print_view(Fi, k, ox, oy, W, H), label


# Line work: every face turned to the viewer, painted back to front in
# paper white, with the edges where the surface turns (a silhouette, a
# panel's edge, a profile's break) inked over it.
PRINT_FEATURE_ANGLE = math.radians(20.0)
PRINT_EDGE = (0.0, 0.0, 0.0)
PRINT_EDGE_WIDTH = 0.45


def _print_owners(items):
    """Names of the objects whose geometry the drawing shows: the
    products and openings on the wall, and everything under them."""
    names = set()
    for it in items:
        if it.preview:
            continue
        for obj in [it.obj] + list(it.obj.children_recursive):
            names.add(obj.name)
    return names


def _print_skip(obj):
    """Helpers that are not the product: cages, cutters, wire boxes, and
    anything left out of renders."""
    return (obj.get('IS_GEONODE_CAGE') or obj.hide_render
            or obj.display_type in ('WIRE', 'BOUNDS'))


def _print_faces(context, items, Fi, view, only=None):
    """[(depth, polygon, edges)] in page points for every face of the
    wall's products that faces the viewer; depth grows into the wall.
    Parts hidden in the viewport (a cutaway, a part toggled off on
    screen) still print, as they do on the sheets: they are shown just
    long enough to be read. `only` narrows it to those object names."""
    owners = _print_owners(items) if only is None else set(only)
    if not owners:
        return []
    shown = []
    layer = context.view_layer
    for name in owners:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH' or _print_skip(obj):
            continue
        try:
            hidden = obj.hide_get(view_layer=layer)
        except Exception:
            continue                    # not in this view layer
        if hidden or obj.hide_viewport:
            shown.append((obj, hidden, obj.hide_viewport))
            obj.hide_viewport = False
            obj.hide_set(False, view_layer=layer)
    try:
        if shown:
            layer.update()
        return _print_faces_now(context, owners, Fi, view)
    finally:
        for obj, hidden, off in shown:
            obj.hide_set(hidden, view_layer=layer)
            obj.hide_viewport = off
        if shown:
            layer.update()


def _print_faces_now(context, owners, Fi, view):
    import numpy as np
    k, ox, oy = view.k, view.ox, view.oy
    cos_feature = math.cos(PRINT_FEATURE_ANGLE)
    dg = context.evaluated_depsgraph_get()
    faces = []
    for inst in dg.object_instances:
        owner = inst.parent if inst.is_instance else inst.object
        if owner is None or owner.original.name not in owners:
            continue
        ob = inst.object
        if ob.type != 'MESH' or _print_skip(owner.original) \
                or (not inst.is_instance and _print_skip(ob.original)):
            continue
        try:
            mesh = ob.to_mesh()
        except Exception:
            continue
        try:
            nv, np_, nl = len(mesh.vertices), len(mesh.polygons), \
                len(mesh.loops)
            if not np_:
                continue
            M = np.array(Fi @ inst.matrix_world)
            co = np.empty(nv * 3)
            mesh.vertices.foreach_get('co', co)
            co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
            nrm = np.empty(np_ * 3)
            mesh.polygons.foreach_get('normal', nrm)
            nmat = np.linalg.inv(M[:3, :3]).T
            nrm = nrm.reshape(-1, 3) @ nmat.T
            nrm /= np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)[:, None]
            start = np.empty(np_, dtype=np.int64)
            total = np.empty(np_, dtype=np.int64)
            mesh.polygons.foreach_get('loop_start', start)
            mesh.polygons.foreach_get('loop_total', total)
            lv = np.empty(nl, dtype=np.int64)
            le = np.empty(nl, dtype=np.int64)
            mesh.loops.foreach_get('vertex_index', lv)
            mesh.loops.foreach_get('edge_index', le)
            ne = len(mesh.edges)
            ev = np.empty(ne * 2, dtype=np.int64)
            mesh.edges.foreach_get('vertices', ev)
            ev = ev.reshape(-1, 2)
        finally:
            ob.to_mesh_clear()
        facing = nrm[:, 1] < -1e-4
        if not facing.any():
            continue
        # The faces either side of each edge: an edge is drawn where the
        # surface folds past the feature angle, at a silhouette (one side
        # faces away), or along an open border.
        loop_poly = np.repeat(np.arange(np_), total)
        count = np.bincount(le, minlength=ne)
        order = np.argsort(le, kind='stable')
        first_at = np.concatenate(([0], np.cumsum(count)[:-1]))
        f0 = np.full(ne, -1)
        f1 = np.full(ne, -1)
        has = count > 0
        f0[has] = loop_poly[order[first_at[has]]]
        two = count == 2
        f1[two] = loop_poly[order[first_at[two] + 1]]
        feature = count != 2
        a, b = f0[two], f1[two]
        fold = (nrm[a] * nrm[b]).sum(axis=1) < cos_feature
        sil = facing[a] != facing[b]
        feature[two] = fold | sil
        px = co[:, 0] * k + ox
        py = co[:, 2] * k + oy
        for f in np.nonzero(facing)[0]:
            s0, n = start[f], total[f]
            vs = lv[s0:s0 + n]
            poly = list(zip(px[vs].tolist(), py[vs].tolist()))
            edges = []
            for e in le[s0:s0 + n]:
                if feature[e]:
                    i, j = ev[e]
                    edges.append(((px[i], py[i]), (px[j], py[j])))
            faces.append((float(co[vs, 1].mean()), poly, edges))
    return faces


INTERIOR_MARKERS = ('IS_FACE_FRAME_INTERIOR_PART',
                    'IS_FRAMELESS_INTERIOR_PART')
INTERIOR_LINE = (0.16, 0.16, 0.20, 0.95)
INTERIOR_DASH_PX = (5.0, 3.5)       # drawn, skipped
PRINT_INTERIOR_WIDTH = 0.35
INTERIOR_REFRESH = 0.6              # s between reads while editing
_interior_cache = {}


def _interior_names(items):
    """Names of the objects that stand inside the wall's cabinets: the
    interior parts and everything under them."""
    names = set()

    def walk(obj, inside):
        inside = inside or any(obj.get(m) for m in INTERIOR_MARKERS)
        if inside:
            names.add(obj.name)
        for child in obj.children:
            walk(child, inside)

    for it in items:
        if not it.preview:
            walk(it.obj, False)
    return names


def _edge_set(faces):
    """The faces' edges, each once."""
    seen = set()
    out = []
    for _depth, _poly, edges in faces:
        for p, q in edges:
            a = (round(float(p[0]), 4), round(float(p[1]), 4))
            b = (round(float(q[0]), 4), round(float(q[1]), 4))
            if a == b:
                continue
            key = (a, b) if a <= b else (b, a)
            if key not in seen:
                seen.add(key)
                out.append(key)
    return out


class _WallUnits:
    """A view that leaves points in the wall's own metres."""
    k, ox, oy = 1.0, 0.0, 0.0


def _interior_edges(context, wall, items):
    """[((x, z), (x, z))] along the wall, in metres, for the edges of
    what stands inside its cabinets. Read from the parts as they are
    shown: nothing is unhidden here, this runs while drawing."""
    import time
    key = (_gen, context.scene.name, wall.name)
    if _interior_cache.get('key') == key:
        return _interior_cache['edges']
    now = time.monotonic()
    if (_interior_cache.get('key', (None,))[1:] == key[1:]
            and now - _interior_cache.get('at', 0.0) < INTERIOR_REFRESH):
        # Mid-edit the model changes every frame: the last read stands
        # until things settle, then one redraw brings it up to date.
        if not _interior_cache.get('queued'):
            _interior_cache['queued'] = True
            area = context.area

            def refresh():
                _interior_cache['queued'] = False
                try:
                    area.tag_redraw()
                except Exception:
                    pass
            bpy.app.timers.register(refresh, first_interval=INTERIOR_REFRESH)
        return _interior_cache['edges']
    edges = []
    names = _interior_names(items)
    fr = _frame(wall)
    if names and fr is not None:
        try:
            edges = _edge_set(_print_faces_now(context, names, fr[1],
                                               _WallUnits))
        except Exception as exc:
            print(f"Elevation interior lines: {exc}")
    _interior_cache.clear()
    _interior_cache.update(key=key, edges=edges, at=time.monotonic())
    return edges


def _dashes(a, b, on, off):
    """The drawn pieces of a..b as a flat [p, q, p, q, ...]."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return []
    ux, uy = dx / length, dy / length
    out = []
    t = 0.0
    while t < length:
        e = min(t + on, length)
        out += [(a[0] + ux * t, a[1] + uy * t),
                (a[0] + ux * e, a[1] + uy * e)]
        t += on + off
    return out


def _draw_interiors(context, region, extra, s):
    wall = active_wall(context)
    if wall is None or not show_option(context.scene, 'INTERIORS'):
        return
    edges = _interior_edges(context, wall, extra['items'])
    if not edges:
        return
    sx, sy = extra['sx'], extra['sy']
    view_key = (_interior_cache['key'], round(sx(0.0), 2), round(sx(1.0), 2),
                round(sy(0.0), 2), round(sy(1.0), 2), s)
    if _interior_cache.get('view') != view_key:
        on, off = INTERIOR_DASH_PX[0] * s, INTERIOR_DASH_PX[1] * s
        w, h = region.width, region.height
        pts = []
        for (x0, z0), (x1, z1) in edges:
            a = (sx(x0), sy(z0))
            b = (sx(x1), sy(z1))
            if (max(a[0], b[0]) < 0 or min(a[0], b[0]) > w
                    or max(a[1], b[1]) < 0 or min(a[1], b[1]) > h):
                continue
            pts += _dashes(a, b, on, off)
        _interior_cache['view'] = view_key
        _interior_cache['pts'] = pts
    pts = _interior_cache['pts']
    if not pts:
        return
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", max(1.0, 1.0 * s))
    shader.uniform_float("color", INTERIOR_LINE)
    batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)


def _print_interiors(page, context, scene, extra, Fi, view, ps):
    """The Interior Lines toggle on paper: what stands inside the
    cabinets, dashed over the fronts."""
    if not show_option(scene, 'INTERIORS'):
        return
    names = _interior_names(extra['items'])
    if not names:
        return
    edges = _edge_set(_print_faces(context, extra['items'], Fi, view,
                                   only=names))
    if not edges:
        return
    page.push()
    page.stroke_color(PRINT_EDGE)
    page.line_width(PRINT_INTERIOR_WIDTH)
    page.dash(INTERIOR_DASH_PX[0] * ps, INTERIOR_DASH_PX[1] * ps)
    page.lines(edges)
    page.pop()


def _print_linework(page, context, extra, Fi, view, L, H):
    """The wall's products as line work. False when there was nothing to
    draw (the caller falls back to outlines)."""
    faces = _print_faces(context, extra['items'], Fi, view)
    sx, sy = extra['sx'], extra['sy']
    page.stroke_color(PRINT_OUTLINE)
    page.line_width(0.5)
    page.rect(sx(0.0), sy(0.0), sx(L) - sx(0.0), sy(H) - sy(0.0))
    if not faces:
        return False
    faces.sort(key=lambda f: -f[0])        # far first
    page.fill_color(PAPER)
    page.stroke_color(PRINT_EDGE)
    page.line_width(PRINT_EDGE_WIDTH)
    for _depth, poly, edges in faces:
        page.polygon(poly, fill=True, stroke=False)
        if edges:
            page.lines(edges)
    return True


def _print_outlines(page, extra, Fi, L, H):
    """Boxes for the products when there is no geometry to draw."""
    sx, sy = extra['sx'], extra['sy']
    page.stroke_color(PRINT_OUTLINE)
    page.line_width(0.5)
    page.rect(sx(0.0), sy(0.0), sx(L) - sx(0.0), sy(H) - sy(0.0))
    for it in extra['items']:
        page.rect(sx(it.x0), sy(it.z0), sx(it.x1) - sx(it.x0),
                  sy(it.z1) - sy(it.z0))
        for x0, x1, z0, z1, *_rest in _face_frame_boxes(it.obj, Fi):
            page.rect(sx(x0), sy(z0), sx(x1) - sx(x0), sy(z1) - sy(z0))


PRINT_MASK_PAD = 1.5        # px of paper kept clear round a value


def _print_text_halo(ps):
    return (PAPER, 2.5 * ps)


def dim_primitives(dims, extra, scale=1.0):
    """layout_wall's result as finished drawing primitives, in the order
    to draw them, in the layout's sheet units (origin bottom left):

    {'kind': 'LINES', 'role': 'FLOOR' | 'EXT' | 'DIM' | 'TICK',
     'segments': [((x, y), (x, y)), ...], 'width', 'color'}
    {'kind': 'MASK', 'rect': (x, y, w, h), 'color'} to fill, no stroke
    {'kind': 'TEXT', 'text', 'x', 'y' (baseline start), 'size', 'angle',
     'font': 'Helvetica', 'color', 'halo': (colour, width),
     'rect': the value's (x, y, w, h), 'key': its dimension's}

    `scale` is the one the layout was made with. A TEXT's 'runs' are its
    pieces, [(string, dx, dy, size)] from (x, y): a fraction is set
    small, so a value is drawn piece by piece and not as `text`. x and
    the runs are Helvetica's; set in another face, lay the value out
    again with value_runs and centre it in `rect`."""
    if extra is None:
        return []
    ps = scale
    fx0, fx1, fy = extra['floor']
    prims = [
        {'kind': 'LINES', 'role': 'FLOOR', 'color': FLOOR_LINE,
         'width': 2.0 * ps,
         'segments': [((fx0 - 24 * ps, fy), (fx1 + 24 * ps, fy))]},
        {'kind': 'LINES', 'role': 'EXT', 'color': LINE, 'width': 1.0 * ps,
         'segments': list(extra['ext'])}]
    # Paper behind each value, over the extension lines and the drawing
    # but under the dimension lines and ticks: whatever runs behind a
    # value breaks round it, the way its own line does.
    mp = PRINT_MASK_PAD * ps
    for d in dims:
        x, y, w, h = d['rect']
        prims.append({'kind': 'MASK', 'color': PAPER,
                      'rect': (x - mp, y - mp, w + 2 * mp, h + 2 * mp)})
    lines, ticks = [], []
    for d in dims:
        line, tk = _dim_lines(d, ps)
        lines += list(zip(line[0::2], line[1::2]))
        ticks += list(zip(tk[0::2], tk[1::2]))
    prims.append({'kind': 'LINES', 'role': 'DIM', 'color': LINE,
                  'width': 1.0 * ps, 'segments': lines})
    prims.append({'kind': 'LINES', 'role': 'TICK', 'color': LINE,
                  'width': 2.0 * ps, 'segments': ticks})
    fs = FONT_SIZE * ps
    halo = _print_text_halo(ps)
    for d in dims:
        x, y, w, h = d['rect']
        if d['axis'] == 'V' and not d.get('horiz'):
            tw = hb_pdf.text_width(d['text'], fs)
            tx, ty, angle = x + w, y + (h - tw) / 2.0, math.pi / 2.0
            runs = [(d['text'], 0.0, 0.0, fs)]
        else:
            runs, tw = value_runs(d['text'], fs, hb_pdf.text_width)
            tx, ty, angle = x + (w - tw) / 2.0, y, 0.0
        prims.append({
            'kind': 'TEXT', 'text': d['text'], 'x': tx, 'y': ty,
            'size': fs, 'angle': angle, 'font': 'Helvetica',
            'runs': runs,
            'color': TEXT if d['target'] is not None else TEXT_READONLY,
            'halo': halo, 'rect': (x, y, w, h), 'key': d.get('key')})
    return prims


def _print_dims(page, scene, dims, extra, ps):
    color = width = None
    for pr in dim_primitives(dims, extra, ps):
        if pr['kind'] == 'LINES':
            if pr['color'] != color:
                color = pr['color']
                page.stroke_color(color)
            if pr['width'] != width:
                width = pr['width']
                page.line_width(width)
            page.lines(pr['segments'])
        elif pr['kind'] == 'MASK':
            page.fill_color(pr['color'])
            page.rect(*pr['rect'], fill=True, stroke=False)
        elif pr['angle']:
            page.fill_color(pr['color'])
            page.text(pr['x'], pr['y'], pr['text'], pr['size'],
                      angle=pr['angle'], halo=pr['halo'])
        else:
            # Every piece's halo first, so one piece's halo cannot eat
            # into the piece beside it.
            page.fill_color(pr['color'])
            for halo in (pr['halo'], None):
                for text, dx, dy, size in pr['runs']:
                    page.text(pr['x'] + dx, pr['y'] + dy, text, size,
                              halo=halo)


def _print_annotations(page, scene, wall, region, view, ps):
    if not show_option(scene, 'ANNOTATIONS') or not _annotation_sources:
        return
    prims = _annotations(scene, wall)

    def P(v):
        return view3d_utils.location_3d_to_region_2d(region, view, v)

    page.line_width(1.0 * ps)
    for pr in prims:
        if pr.get('kind') != 'LINES':
            continue
        pts = [P(v) for v in pr.get('points', ())]
        segs = [((a.x, a.y), (b.x, b.y)) for a, b in zip(pts[0::2], pts[1::2])
                if a is not None and b is not None]
        page.stroke_color(pr.get('color', ANNOTATION_LINE))
        page.lines(segs)
    halo = _print_text_halo(ps)
    bfs = BUBBLE_FONT_SIZE * ps
    blf.size(0, bfs)
    for pr in prims:
        if pr.get('kind') != 'BUBBLE' or not pr.get('text'):
            continue
        o = P(pr['origin'])
        if o is None:
            continue
        color = pr.get('color', TEXT)
        tw = hb_pdf.text_width(pr['text'], bfs)
        th = blf.dimensions(0, pr['text'])[1]
        r = max(tw, th) / 2.0 + 5 * ps
        page.fill_color(PAPER)
        page.stroke_color(color)
        page.line_width(1.5 * ps)
        page.circle(o.x, o.y, r, fill=True, stroke=True)
        page.fill_color(color)
        page.text(o.x - tw / 2.0, o.y - th / 2.0, pr['text'], bfs)
    afs = ANNOTATION_FONT_SIZE * ps
    blf.size(0, afs)
    lh = blf.dimensions(0, "Ag")[1] * 1.35
    for pr in prims:
        if pr.get('kind') != 'TEXT' or not pr.get('text'):
            continue
        o = P(pr['origin'])
        if o is None:
            continue
        tip = P(pr['origin'] + pr.get('x_axis', Vector((1, 0, 0))) * 0.1)
        if tip is None or (tip - o).length < 0.5:
            continue
        ang = math.atan2(tip.y - o.y, tip.x - o.x)
        if ang > math.pi / 2 + 1e-3 or ang < -math.pi / 2 - 1e-3:
            ang += math.pi
            ang = math.atan2(math.sin(ang), math.cos(ang))
        rows = pr['text'].splitlines()
        ca, sa = math.cos(ang), math.sin(ang)
        total = lh * len(rows)
        page.fill_color(pr.get('color', TEXT))
        for i, row in enumerate(rows):
            tw = hb_pdf.text_width(row, afs)
            th = blf.dimensions(0, row)[1]
            align = pr.get('align', 'CENTER')
            dx = {'LEFT': 0.0, 'RIGHT': -tw}.get(align, -tw / 2.0)
            dy = total / 2.0 - lh * (i + 1) + (lh - th) / 2.0
            page.text(o.x + dx * ca - dy * sa, o.y + dx * sa + dy * ca, row,
                      afs, angle=ang, halo=halo)


def _print_title(page, scene, wall, label, W):
    walls = room_walls(scene)
    idx = walls.index(wall) + 1 if wall in walls else 0
    name = f"Wall {idx} of {len(walls)}" if idx else wall.name
    y = PRINT_MARGIN
    page.stroke_color(PRINT_OUTLINE)
    page.line_width(0.5)
    page.lines([((PRINT_MARGIN, y + 18), (W - PRINT_MARGIN, y + 18))])
    page.fill_color(TEXT)
    page.text(PRINT_MARGIN, y + 4, f"{scene.name}  -  {name}", 11,
              font=hb_pdf.BOLD)
    import datetime
    right = (f"Scale {label}" if label else "Not to scale") \
        + "    " + datetime.date.today().strftime("%b %d, %Y")
    page.text(W - PRINT_MARGIN - hb_pdf.text_width(right, 9), y + 4,
              right, 9)


def print_wall(context, filepath, paper='TABLOID',
               text_scale=PRINT_TEXT_SCALE, wall=None):
    """Write a wall to `filepath` as a one-page PDF: the products' line
    work at a drafting scale with the view's dimensions and notes over
    it, all as vectors. The wall on screen, or `wall` of the context's
    scene with no elevation showing. Returns the path written."""
    global _print_scale
    scene = context.scene
    front = None            # the elevation on screen knows its own
    if wall is None:
        wall = active_wall(context)
        if wall is None:
            raise RuntimeError("No wall is shown in elevation")
    elif wall != active_wall(context):
        front = _front_names(scene, wall)
    if _frame(wall) is None:
        raise RuntimeError("The wall has no elevation to print")
    W, H = PRINT_PAPER.get(paper, PRINT_PAPER['TABLOID'])
    _F, Fi, L, Hw = _frame(wall)
    region = _PrintRegion(W, H)
    doc = hb_pdf.Document()
    page = doc.add_page(W, H)
    _print_scale = text_scale
    try:
        view, label = _print_fit(scene, wall, W, H, front)
        dims, extra = _print_layout(scene, wall, region, view, front)
        if not _print_linework(page, context, extra, Fi, view, L, Hw):
            _print_outlines(page, extra, Fi, L, Hw)
        try:
            _print_interiors(page, context, scene, extra, Fi, view,
                             text_scale)
        except Exception as exc:
            print(f"Elevation print: interior lines: {exc}")
        _print_dims(page, scene, dims, extra, text_scale)
        try:
            _print_annotations(page, scene, wall, region, view, text_scale)
        except Exception as exc:
            print(f"Elevation print: notes: {exc}")
    finally:
        _print_scale = None
    _print_title(page, scene, wall, label, W)
    return _print_save(doc, filepath)


def _print_save(doc, filepath):
    """Save, and if the file is open in a viewer that locks it, beside it
    under the next free name."""
    import os
    root, ext = os.path.splitext(filepath)
    for n in range(0, 20):
        path = filepath if n == 0 else f"{root} ({n + 1}){ext}"
        try:
            doc.save(path)
            return path
        except PermissionError:
            continue
    raise PermissionError(f"Could not write {filepath}")


def _print_default_path(context):
    import os
    import re
    import tempfile
    scene = context.scene
    wall = active_wall(context)
    walls = room_walls(scene)
    tag = (f"Wall {walls.index(wall) + 1}" if wall in walls
           else (wall.name if wall else "Wall"))
    stem = re.sub(r'[\\/:*?"<>|]+', '_', f"{scene.name} - {tag} elevation")
    if bpy.data.filepath:
        folder = os.path.dirname(bpy.data.filepath)
    else:
        folder = tempfile.gettempdir()
    return os.path.join(folder, stem + ".pdf")


class home_builder_OT_elevation_print(bpy.types.Operator):
    """Print the wall on screen to a PDF at a drafting scale, with the
    dimensions and notes the view shows"""
    bl_idname = "home_builder.elevation_print"
    bl_label = "Print Elevation PDF"

    filepath: bpy.props.StringProperty(
        name="File", subtype='FILE_PATH', default="",
        description="Where to write the PDF (blank: beside the .blend)")
    paper: bpy.props.EnumProperty(
        name="Paper", default='TABLOID',
        items=(('TABLOID', "Tabloid 17 x 11", ""),
               ('LETTER', "Letter 11 x 8.5", "")))
    text_scale: bpy.props.FloatProperty(
        name="Text Size", default=PRINT_TEXT_SCALE, min=0.3, max=2.0,
        description="Text, spacing and line weight on paper, against "
                    "the screen")
    open_file: bpy.props.BoolProperty(
        name="Open", default=True, description="Open the PDF when written")

    @classmethod
    def poll(cls, context):
        return is_active(context)

    def execute(self, context):
        path = bpy.path.abspath(self.filepath) if self.filepath \
            else _print_default_path(context)
        try:
            path = print_wall(context, path, self.paper, self.text_scale)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not print: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Printed {path}")
        if self.open_file and not bpy.app.background:
            try:
                bpy.ops.wm.path_open(filepath=path)
            except Exception:
                pass
        return {'FINISHED'}


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
            elif got[1] == 'PRINT':
                bpy.ops.home_builder.elevation_print()
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


def _glyph_face_frame(shader, rect, color):
    """A face frame: outer stiles and rails around two openings."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.5, rh * 0.5
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    t = w * 0.16
    m = (x0 + x1) / 2.0
    box = lambda a, b, c, d: [(a, b), (c, b), (c, b), (c, d),
                              (c, d), (a, d), (a, d), (a, b)]
    draw_lines(shader, box(x0, y0, x1, y1)
               + box(x0 + t, y0 + t, m - t / 2.0, y1 - t)
               + box(m + t / 2.0, y0 + t, x1 - t, y1 - t), color)


def _glyph_annotation(shader, rect, color):
    """A note: a leader to a dot, with text lines beside it."""
    rx, ry, rw, rh = rect
    cx, cy = rx + rw / 2.0, ry + rh / 2.0
    a = min(rw, rh) * 0.26
    d = a * 0.12
    pts = [(cx - a, cy - a), (cx - a * 0.2, cy + a * 0.2),
           (cx - a * 0.2, cy + a * 0.2), (cx + a, cy + a * 0.2),
           (cx - a * 0.05, cy + a * 0.6), (cx + a, cy + a * 0.6),
           (cx - a * 0.05, cy - a * 0.2), (cx + a * 0.6, cy - a * 0.2)]
    pts += [(cx - a - d, cy - a - d), (cx - a + d, cy - a + d),
            (cx - a - d, cy - a + d), (cx - a + d, cy - a - d)]
    draw_lines(shader, pts, color)


def _glyph_interiors(shader, rect, color):
    """A cabinet box with two dashed shelves across it."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.46, rh * 0.52
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    pts = [(x0, y0), (x1, y0), (x1, y0), (x1, y1),
           (x1, y1), (x0, y1), (x0, y1), (x0, y0)]
    dash = w / 5.0
    for y in (y0 + h / 3.0, y0 + 2.0 * h / 3.0):
        for i in (0, 2, 4):
            pts += [(x0 + i * dash, y), (x0 + (i + 1) * dash, y)]
    draw_lines(shader, pts, color)


_SHOW_GLYPHS = {
    'FACE_FRAME': icon_glyph('cab_face_frame', _glyph_face_frame),
    'ANNOTATIONS': icon_glyph('pencil', _glyph_annotation),
    'INTERIORS': _glyph_interiors,
}


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
    try:
        _paper_restore_on_load()
    except Exception:
        pass


classes = (
    home_builder_OT_show_elevation,
    home_builder_OT_exit_elevation,
    home_builder_OT_elevation_step,
    home_builder_OT_elevation_frame,
    home_builder_OT_elevation_hover,
    home_builder_OT_elevation_click,
    home_builder_OT_elevation_edit_dim,
    home_builder_OT_elevation_print,
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
