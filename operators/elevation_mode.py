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

import contextlib
import json
import math
import re

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Euler, Matrix
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from .. import hb_types
from .. import hb_utils
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

# Material Preview and Rendered show the world, not paper: dark ink is
# lost on it, so there the view draws light with a dark halo.
_INK_NAMES = ('LINE', 'TEXT', 'TEXT_READONLY', 'HALO', 'TEXT_HALO',
              'FLOOR_LINE', 'ANNOTATION_LINE', 'INTERIOR_LINE', 'HOVER',
              'HOVER_TEXT')
_INK_LIGHT = {
    'LINE': (0.96, 0.96, 0.96, 1.0),
    'TEXT': (1.0, 1.0, 1.0, 1.0),
    'TEXT_READONLY': (0.90, 0.90, 0.90, 1.0),
    'HALO': (0.0, 0.0, 0.0, 0.55),
    'TEXT_HALO': (0.0, 0.0, 0.0, 0.85),
    'FLOOR_LINE': (0.96, 0.96, 0.96, 0.9),
    'ANNOTATION_LINE': (0.94, 0.94, 0.94, 0.9),
    'INTERIOR_LINE': (0.94, 0.94, 0.94, 0.95),
    'HOVER': (0.45, 0.72, 1.0, 1.0),
    'HOVER_TEXT': (0.45, 0.72, 1.0, 1.0),
}


def _ink_swap(light):
    """Put the light ink in place of the drafting ink; returns what to
    hand back to _ink_restore. Nothing changes when `light` is False."""
    if not light:
        return None
    g = globals()
    saved = {name: g[name] for name in _INK_NAMES}
    g.update(_INK_LIGHT)
    return saved


def _ink_restore(saved):
    if saved:
        globals().update(saved)

FIRST_TIER_PX = 30      # geometry to the first dimension line
TIER_PX = 30            # between stacked dimension lines
EXT_GAP_PX = 5          # extension line stands off the geometry
EXT_OVER_PX = 5         # and runs past the dimension line
TICK_PX = 3.5           # half-length of the tick, a bar across the line
TICK_WIDTH = 1.5        # its weight (the line's is 1)
# A word under a value saying what it measures (OA, OPEN, LEG, CL): set
# small, centred under the value, below the line.
TAG_SCALE = 0.72        # of the value's size
TAG_GAP_PX = 2.5        # value to its tag
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
# A stand-in for the wall that turns the corner at this wall's end,
# built while the elevation is up so its plan and iso show the return.
STUB_TAG = 'HB_ELEVATION_RETURN'
RETURN_MIN = units.inch(36.0)       # how far a return is shown, at least
RETURN_PAST = units.inch(6.0)       # and past the deepest product
RETURN_FOOT = units.inch(1.0)       # a return the iso looks over: its foot
# Walls cut by the plan, and a return wall seen end on in the elevation.
WALL_GRAY = (0.80, 0.80, 0.80, 1.0)
# The wall's own display colour, kept while the elevation shows it white
# (the sheet's wall is paper).
WALL_COLOR_TAG = 'HB_ELEVATION_WALL_COLOR'
WALL_WHITE = (1.0, 1.0, 1.0, 1.0)

# ---- Module state ----------------------------------------------------------

# {'scene', 'wall', 'r3d' (as_pointer), 'view' (saved r3d state),
#  'extra' (names of in-front roots not parented to the wall),
#  'preview' (names the running placement owns), 'fit' (passes left)}
_state = None
_edit = None            # {'index': dim key, 'typed': str, 'owner': id}
_mouse = (-1, -1)
_hover = None           # dim key or bar part under the cursor
_hover_chain = None     # the height string under the cursor (its chain id)
_drag = None            # a height string being dragged sideways
_card_pick = None       # the detail card clicked on (its id)
_card_drag = None       # a detail card being dragged to a new place
_adding = None          # a height string being clicked in
_noting = None          # a note being placed or typed
_picture = None         # the picture page showing in place of a wall
_note_drag = None       # a note (or its leader's tip) being dragged
_gen = 0
_print_scale = None    # set while printing: px -> pt
_print_measure = None  # (text, size) -> width in the face a sheet is set in
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


# ---- Height strings the user moved or added --------------------------------
#
# Kept on the wall, so every view of it (this one, a print, a sheet) lays
# out the same: {'moved': {chain id: sideways offset}, 'hidden': [chain
# id, ...], 'added': [{'x': m along the wall, 'levels': [m off the
# floor, ...]}]}. A rule-made string the user removed is listed in
# 'hidden' (the strings after it close up). A rule-made
# string's offset is in style units (pixels at interface scale 1, the
# unit the tiers are spaced in); an added string stands at a place on
# the wall.

HEIGHTS_PROP = 'HB_ELEVATION_HEIGHTS'


def _chain_id(chain):
    return ':'.join(str(c) for c in chain)


def _heights(wall):
    data = {}
    try:
        raw = wall.get(HEIGHTS_PROP)
        if raw:
            data = json.loads(raw)
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    moved = data.get('moved')
    added = data.get('added')
    hidden = data.get('hidden')
    return {'moved': moved if isinstance(moved, dict) else {},
            'hidden': [str(h) for h in hidden]
            if isinstance(hidden, list) else [],
            'added': [u for u in added if isinstance(u, dict)
                      and len(u.get('levels') or ()) >= 2]
            if isinstance(added, list) else []}


def _set_heights(wall, data):
    if data['moved'] or data['added'] or data.get('hidden'):
        wall[HEIGHTS_PROP] = json.dumps(data)
    elif HEIGHTS_PROP in wall:
        del wall[HEIGHTS_PROP]
    _bump_gen()


# ---- The drawings: every page the project prints ---------------------------
#
# Show Drawings lists the pages as tabs along the top of the view, in
# print order. A page is {'key': str, 'title': str, 'kind': 'WALL' |
# 'PICTURE', 'room': scene name}: a WALL page also names its 'wall' and
# is shown live, dimensioned; a PICTURE page carries 'picture', a
# callable(context) returning the path of an image of the page, shown
# as it is (a page some other add-on draws). A page that can be shown
# either way carries 'swap' (a callable(context) that flips it),
# 'swap_label' for the bar's button and 'slot', the id both forms share.
#
# With no page source the pages are every wall, of every room, that has
# something on it. An add-on that keeps a sheet set registers a source
# and returns its own list.
#
# A room is drawn Full (its walls each on their own page; the plan and
# the iso are pages of their own, where a source supplies them) or
# Compact (each wall with its plan over it and its iso beside it).

MODE_PROP = 'HB_DRAWINGS_MODE'
MODES = ('FULL', 'COMPACT')
MODE_LABELS = {'FULL': "Full", 'COMPACT': "Compact"}
MODE_OPTIONS = ('PLAN', 'ISO')
PICTURE_IMAGE = "HB Drawings Page"
_page_sources = []
_mode_default = [None]
_page_cache = {}


def register_page_source(fn):
    if fn not in _page_sources:
        _page_sources.append(fn)
    _page_cache.clear()


def unregister_page_source(fn):
    if fn in _page_sources:
        _page_sources.remove(fn)
    _page_cache.clear()


def set_mode_default(fn):
    """fn(scene) -> 'FULL' | 'COMPACT' | None: how a room is drawn until
    the user chooses. None clears it."""
    _mode_default[0] = fn
    _page_cache.clear()


def room_mode(scene):
    value = scene.get(MODE_PROP)
    if value in MODES:
        return value
    fn = _mode_default[0]
    if fn is not None:
        try:
            got = fn(scene)
            if got in MODES:
                return got
        except Exception as exc:
            print(f"Drawings mode: {exc}")
    return 'FULL'


def set_room_mode(scene, mode):
    """Draw a room Full or Compact. The plan and iso follow the mode
    again (a wall's own switches for them are dropped)."""
    scene[MODE_PROP] = mode
    group = scene.get(SHOW_PROP)
    if group is not None:
        for key in MODE_OPTIONS:
            if key in group:
                del group[key]
    _page_cache.clear()
    _bump_gen()


def wall_has_products(wall):
    """Something stands on the wall. Read from what hangs under it, so
    it holds for a room that is not on screen."""
    for child in wall.children:
        if _is_product(child) or _is_opening(child):
            return True
        if child.get('IS_CAGE_GROUP') and any(_is_product(c)
                                              for c in child.children):
            return True
    return False


def _room_scenes():
    rooms = [sc for sc in bpy.data.scenes
             if hb_utils.is_room_scene(sc)
             and any(o.get('IS_WALL_BP') for o in sc.objects)]
    rooms.sort(key=lambda sc: (getattr(getattr(sc, 'home_builder', None),
                                       'sort_order', 0), sc.name))
    return rooms


def wall_page(scene, wall, title=None):
    walls = room_walls(scene)
    name = (f"Wall {walls.index(wall) + 1}" if wall in walls else wall.name)
    return {'key': f"WALL:{scene.name}:{wall.name}", 'kind': 'WALL',
            'room': scene.name, 'wall': wall.name,
            'title': title or f"{scene.name} - {name}"}


def _default_pages():
    out = []
    for scene in _room_scenes():
        for wall in room_walls(scene):
            if wall_has_products(wall):
                out.append(wall_page(scene, wall))
    return out


def pages(context=None):
    """The project's pages, in print order."""
    import time
    context = context or bpy.context
    key = (_gen, len(bpy.data.scenes), len(_page_sources),
           int(time.monotonic() / 2.0))
    if _page_cache.get('key') == key:
        return _page_cache['pages']
    found = None
    for fn in list(_page_sources):
        try:
            found = fn(context)
        except Exception as exc:
            print(f"Drawings pages: {exc}")
            found = None
        if found is not None:
            break
    if found is None:
        found = _default_pages()
    found = [p for p in found if p.get('key') and p.get('kind') in (
        'WALL', 'PICTURE')]
    _page_cache.update(key=key, pages=found)
    return found


def current_page_key(context=None):
    if _picture is not None:
        return _picture['key']
    wall = active_wall(context)
    if wall is None:
        return None
    return f"WALL:{(context or bpy.context).scene.name}:{wall.name}"


def current_page(context=None):
    key = current_page_key(context)
    for page in pages(context):
        if page['key'] == key:
            return page
    return None


def swap_page(context):
    """Flip the page on screen to its other form (live wall / picture)."""
    page = current_page(context)
    if page is None or page.get('swap') is None:
        return False
    slot = page.get('slot')
    page['swap'](context)
    _page_cache.clear()
    other = next((p for p in pages(context)
                  if slot is not None and p.get('slot') == slot), None)
    return other is not None and show_page(context, other)


def _page_title(context):
    key = current_page_key(context)
    for page in pages(context):
        if page['key'] == key:
            return page.get('title') or ""
    if _picture is not None:
        return _picture.get('title') or ""
    wall = active_wall(context)
    return wall_page(context.scene, wall)['title'] if wall else ""


def _picture_clear():
    global _picture
    _picture = None
    img = bpy.data.images.get(PICTURE_IMAGE)
    if img is not None:
        try:
            bpy.data.images.remove(img)
        except Exception:
            pass


def show_page(context, page):
    """Bring a page up in the view: a wall of this room or another, or
    a picture page. False when it could not be shown."""
    global _picture
    if page.get('kind') == 'PICTURE':
        if _state is None:
            return False
        fn = page.get('picture')
        try:
            context.window.cursor_set('WAIT')
        except Exception:
            pass
        try:
            path = fn(context) if fn is not None else None
        except Exception as exc:
            print(f"Drawings page '{page.get('title')}': {exc}")
            path = None
        finally:
            try:
                context.window.cursor_set('DEFAULT')
            except Exception:
                pass
        if not path:
            return False
        _picture_clear()
        try:
            img = bpy.data.images.load(path, check_existing=False)
        except Exception as exc:
            print(f"Drawings page '{page.get('title')}': {exc}")
            return False
        img.name = PICTURE_IMAGE
        _picture = {'key': page['key'], 'title': page.get('title') or "",
                    'image': img.name}
        if context.area is not None:
            context.area.tag_redraw()
        return True
    room = bpy.data.scenes.get(page.get('room') or "")
    wall = bpy.data.objects.get(page.get('wall') or "")
    if room is None or wall is None or _frame(wall) is None:
        return False
    _picture_clear()
    keep = _state['view'] if _state is not None else None
    if context.scene != room:
        # Another room: this one goes back the way it was first.
        if _state is not None:
            leave(context)
        try:
            if hb_utils.is_room_scene(context.scene):
                hb_utils.save_view_state(context.scene)
        except Exception:
            pass
        context.window.scene = room
        try:
            if hb_utils.is_room_scene(room):
                hb_utils.restore_view_state(room)
            context.view_layer.update()
        except Exception:
            pass
        keep = None
    return enter(context, wall, keep_view=keep)


TAB_CHARS = 26              # a tab's title is cut to this
TAB_MIN_CHARS = 6


def _tabs_layout(context, area):
    """[(page, rect, label)] of the page tabs along the top."""
    if _state is None:
        return []
    listed = pages(context)
    if len(listed) < 2:
        return []
    s = _s()
    blf.size(0, 11 * s)
    h = 24 * s
    gap = 2 * s
    xmin, xmax, _ymin, ymax = get_visible_window_bounds(area)
    room = max(60.0, xmax - xmin - 24 * s)

    def cut(text, n):
        return text if len(text) <= n else text[:max(1, n - 1)] + "\u2026"

    chars = TAB_CHARS
    while True:
        labels = [cut(p.get('title') or "", chars) for p in listed]
        widths = [blf.dimensions(0, lb)[0] + 16 * s for lb in labels]
        total = sum(widths) + gap * (len(widths) - 1)
        if total <= room or chars <= TAB_MIN_CHARS:
            break
        chars -= 2
    x = (xmin + xmax) / 2.0 - min(total, room) / 2.0
    y = ymax - 14 * s - h
    out = []
    for page, label, w in zip(listed, labels, widths):
        out.append((page, (x, y, w, h), label))
        x += w + gap
    return out


def _draw_tabs(context, area):
    tabs = _tabs_layout(context, area)
    if not tabs:
        return
    s = _s()
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    current = current_page_key(context)
    for page, (x, y, w, h), label in tabs:
        on = page['key'] == current
        hovered = _hover == ('TAB', page['key'])
        bg = (Theme.ACCENT_BG if on else Theme.BTN_HOVER_BG if hovered
              else Theme.BTN_BG)
        draw_round_rect(shader, x, y, w, h, 4 * s, bg)
        blf.size(0, 11 * s)
        tw = blf.dimensions(0, label)[0]
        blf.color(0, *(Theme.TEXT_PRIMARY if on or hovered
                       else Theme.TEXT_NORMAL))
        blf.position(0, x + (w - tw) / 2.0,
                     y + (h - blf.dimensions(0, "Ag")[1]) / 2.0 + 1, 0)
        draw_glyphs(0, label)
        shader.bind()


def _draw_picture(context, area, region):
    """A picture page: the page on white, with the tabs and the bar."""
    s = _s()
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float("color", (*PAPER, 1.0))
    batch_for_shader(shader, 'TRI_FAN', {"pos": (
        (0, 0), (region.width, 0), (region.width, region.height),
        (0, region.height))}).draw(shader)
    img = bpy.data.images.get(_picture['image']) if _picture else None
    if img is not None and img.size[0] > 0 and img.size[1] > 0:
        xmin, xmax, ymin, ymax = get_visible_window_bounds(area)
        pad = 58 * s
        aw = max(40.0, xmax - xmin - 24 * s)
        ah = max(40.0, ymax - ymin - 2 * pad)
        k = min(aw / img.size[0], ah / img.size[1])
        w, h = img.size[0] * k, img.size[1] * k
        x = (xmin + xmax) / 2.0 - w / 2.0
        y = (ymin + ymax) / 2.0 - h / 2.0
        try:
            tex = gpu.texture.from_image(img)
            ish = gpu.shader.from_builtin('IMAGE')
            ish.bind()
            ish.uniform_sampler("image", tex)
            batch_for_shader(ish, 'TRI_FAN', {
                "pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1))}).draw(ish)
        except Exception as exc:
            print(f"Drawings page picture: {exc}")
        _stroke(region, [(x, y), (x + w, y), (x + w, y), (x + w, y + h),
                         (x + w, y + h), (x, y + h), (x, y + h), (x, y)],
                1.0 * s, ANNOTATION_LINE)
    _draw_bar(context, area)
    _draw_tabs(context, area)
    gpu.state.blend_set('NONE')


# ---- Notes typed on the wall ------------------------------------------------
#
# Kept on the wall like the height strings, so the view, its print and
# any sheet read the same: [{'x', 'z': where the note stands (m along
# the wall, m off the floor), 'text': str (may hold newlines), 'turn':
# 0 level | 1 reading up the wall | -1 reading down it, 'tip': [x, z]
# what its leader points at, or None}].

NOTES_PROP = 'HB_ELEVATION_NOTES'


def _user_notes(wall):
    try:
        raw = wall.get(NOTES_PROP)
        data = json.loads(raw) if raw else []
    except Exception:
        data = []
    out = []
    for u in data if isinstance(data, list) else ():
        try:
            tip = u.get('tip')
            out.append({
                'x': float(u['x']), 'z': float(u['z']),
                'text': str(u.get('text', '')),
                'turn': max(-1, min(1, int(u.get('turn', 0)))),
                'tip': [float(tip[0]), float(tip[1])] if tip else None})
        except Exception:
            continue
    return out


def _set_user_notes(wall, notes):
    if notes:
        wall[NOTES_PROP] = json.dumps(notes)
    elif NOTES_PROP in wall:
        del wall[NOTES_PROP]
    _bump_gen()


def _user_note_prims(wall, note, index):
    """A typed note as annotation primitives: its text, and its leader
    with an arrowhead at the tip. A level note with a leader is set
    beside the leader's end, running away from what it points at."""
    fr = _frame(wall)
    if fr is None:
        return []
    F = fr[0]
    R = F.to_3x3()

    def W(x, z):
        return F @ Vector((x, 0.0, z))

    turn = note.get('turn', 0)
    x_axis = R @ (Vector((1.0, 0.0, 0.0)) if turn == 0
                  else Vector((0.0, 0.0, float(turn))))
    text, align = note.get('text', ''), 'CENTER'
    at = W(note['x'], note['z'])
    prims = []
    tip = note.get('tip')
    if tip:
        if turn == 0 and text:
            right = tip[0] <= note['x']
            align = 'LEFT' if right else 'RIGHT'
            text = '\n'.join((' ' + row) if right else (row + ' ')
                             for row in text.splitlines())
        end = W(tip[0], tip[1])
        prims.append({'kind': 'LINES', 'points': [at, end],
                      'heads': [(end, at)], 'user': index})
    prims.append({'kind': 'TEXT', 'origin': at, 'x_axis': x_axis,
                  'text': text, 'align': align, 'user': index})
    return prims


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


def keep_paper():
    """Put the elevation's view back on paper after something else
    restyled the viewport (a scene switched away and back resets a
    room's background and floor). True when an elevation was up."""
    if _state is None:
        return False
    area, _r3d = _find_r3d(_state['r3d'])
    if area is None:
        return False
    space = area.spaces.active
    try:
        space.shading.background_type = 'VIEWPORT'
        space.shading.background_color = PAPER
        for k in PAPER_OVERLAYS:
            setattr(space.overlay, k, False)
    except Exception:
        return False
    area.tag_redraw()
    return True


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
    try:
        # Room for the legend under the elevation.
        bottom += _legend_height(bpy.data.scenes.get(_state['scene']),
                                 wall, s)
    except Exception:
        pass
    avail_w = max(100.0, (xmax - xmin) - 2 * side)
    avail_h = max(100.0, (ymax - ymin) - top - bottom)
    px_per_m = cur_w / length
    # Side views switched on take their room: the plan above the
    # elevation, the iso to its left.
    more_w = more_h = 0.0
    try:
        scene = bpy.data.scenes.get(_state['scene'])
        kinds = _side_on(scene) if scene is not None else []
        if kinds:
            box = _side_box(wall, _items(scene, wall))
            for kind in kinds:
                _C, (l, r, b, t) = _side_camera(F, box, kind)
                if kind == 'PLAN':
                    more_h = (t - b) * px_per_m + (SIDE_GAP_PX + 60) * s
                else:
                    more_w = (r - l) * px_per_m + (SIDE_GAP_PX + 70) * s
    except Exception as exc:
        print("Elevation fit side views:", exc)
    # Detail cards stand to the right, a share of the wall's height each.
    cards_w = 0.0
    try:
        cards_w = _cards_width(bpy.data.scenes.get(_state['scene']), wall,
                               cur_h, cur_h, s)
    except Exception as exc:
        print("Elevation fit detail cards:", exc)
    k = min(avail_w / (cur_w + more_w + cards_w),
            avail_h / (cur_h + more_h))
    # Centre the wall in the space left for it.
    want_x = (xmin + xmax) / 2.0
    want_y = ymin + bottom + avail_h / 2.0
    # The iso stands to the left of the elevation, the plan above it.
    have_x = (p0.x + p1.x) / 2.0 - more_w / 2.0 + cards_w / 2.0
    have_y = (p0.y + p1.y) / 2.0 + more_h / 2.0
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


# ---- Return walls ------------------------------------------------------------

def _return_sides(wall):
    """{'L' | 'R': (thickness, height)} of the walls joined to this
    wall's ends that turn towards the room (an inside corner)."""
    fr = _frame(wall)
    if fr is None:
        return {}
    _F, Fi, length, height = fr
    out = {}
    for key, side, corner in (('L', 'left', 0.0), ('R', 'right', length)):
        try:
            node = hb_types.GeoNodeWall(wall).get_connected_wall(side)
            other = node.obj if node is not None else None
        except Exception:
            other = None
        if other is None or other == wall:
            continue
        dims = _wall_dims(other)
        if dims is None or not dims[0]:
            continue
        mw = other.matrix_world
        ends = [Fi @ mw.translation, Fi @ (mw @ Vector((dims[0], 0.0, 0.0)))]
        far = max(ends, key=lambda q: abs(q.x - corner) + abs(q.y))
        if far.y < -0.1:
            out[key] = (dims[2] or 0.15, dims[1] or height)
    return out


def _return_boxes(wall, items):
    """([(footprint, z0, z1)] in the wall's frame, iso from the left):
    a length of each return wall, and which side the iso looks from so
    a return stands behind the work. A footprint is four (x, y) corners,
    anticlockwise from above, the last two the corner's mitre: the line
    from the inside corner to the outside one, where the return meets
    this wall's own mitred end. With a return at both ends the one
    nearer the iso's viewer is shown by its foot only."""
    sides = _return_sides(wall)
    if not sides:
        return [], False
    _F, Fi, length, _height = _frame(wall)
    dims = _wall_dims(wall)
    thick = dims[2] if dims and dims[2] else 0.15
    front = 0.0
    for it in items:
        if it.preview:
            continue
        try:
            mw = it.obj.matrix_world
            front = min(front, min((Fi @ (mw @ Vector(c))).y
                                   for c in it.obj.bound_box))
        except Exception:
            continue
    y0 = min(-RETURN_MIN, front - RETURN_PAST)
    from_left = 'R' in sides and 'L' not in sides
    boxes = []
    for key, (t, h) in sides.items():
        if key == 'L':
            footprint = ((-t, y0), (0.0, y0), (0.0, 0.0), (-t, thick))
        else:
            footprint = ((length, y0), (length + t, y0),
                         (length + t, thick), (length, 0.0))
        foot = len(sides) == 2 and key == 'R'
        boxes.append((footprint, 0.0, RETURN_FOOT if foot else h))
    return boxes, from_left


_BOX_FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6),
              (1, 2, 6, 5), (3, 0, 4, 7))


# The corners of a return's mitre in _box_corners' order, and the face
# that lies on it (inside the corner: never seen).
_SEAM_CORNERS = frozenset((2, 3, 6, 7))
_SEAM_FACE = (2, 3, 7, 6)


def _box_corners(box):
    footprint, z0, z1 = box
    return ([(x, y, z0) for x, y in footprint]
            + [(x, y, z1) for x, y in footprint])


def _return_seams(boxes):
    """[((x, y), (x, y))] in the wall's frame: the mitre lines where
    the returns meet the wall. Lines along them are not drawn, so the
    corner reads as one wall turning."""
    return [(box[0][2], box[0][3]) for box in boxes]


def _make_stubs(scene, wall, items):
    """Stand-in objects for the return walls, in the wall's frame."""
    boxes, _from_left = _return_boxes(wall, items)
    F = _frame(wall)[0]
    for box in boxes:
        mesh = bpy.data.meshes.new("Elevation Return Wall")
        mesh.from_pydata(_box_corners(box), [], _BOX_FACES)
        mesh.update()
        obj = bpy.data.objects.new("Elevation Return Wall", mesh)
        obj[STUB_TAG] = True
        scene.collection.objects.link(obj)
        obj.matrix_world = F
        obj.color = WALL_GRAY
        obj.hide_select = True
        obj.hide_render = True


def _drop_stubs(scene):
    for obj in [o for o in scene.objects if o.get(STUB_TAG)]:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        try:
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        except Exception:
            pass


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
        if obj.type in {'CAMERA', 'LIGHT'} or obj.get(STUB_TAG):
            continue
        c = _center_local(obj, Fi)
        if c is None:
            continue
        if (0.0 <= c.x <= length and -FRONT_DEPTH <= c.y <= 0.05
                and -0.05 <= c.z <= height + 0.3):
            roots.append(obj)
    return roots


@hb_utils.with_children_index
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
    # Text objects on the wall are not shown as 3D text: the view letters
    # them itself, with its other notes (see _text_object_notes).
    for obj in keep:
        if obj.type != 'FONT' or view_layer.objects.get(obj.name) is None:
            continue
        if obj.hide_get() or obj.hide_viewport:
            continue
        obj.hide_set(True)
        obj[HIDE_TAG] = True
    # The wall reads as paper, the way it does on the sheet.
    try:
        if WALL_COLOR_TAG not in wall:
            wall[WALL_COLOR_TAG] = list(wall.color)
        wall.color = WALL_WHITE
    except Exception:
        pass
    names = [o.name for o in extra]
    try:
        _apply_molding(scene)
    except Exception as exc:
        print(f"Elevation mouldings: {exc}")
    try:
        _make_stubs(scene, wall, _items(scene, wall, names, ()))
    except Exception as exc:
        print(f"Elevation return walls: {exc}")
    return names


def _unisolate(scene):
    try:
        _drop_stubs(scene)
    except Exception as exc:
        print(f"Elevation return walls: {exc}")
    for obj in scene.objects:
        if WALL_COLOR_TAG in obj:
            try:
                obj.color = tuple(obj[WALL_COLOR_TAG])[:4]
            except Exception:
                pass
            del obj[WALL_COLOR_TAG]
        for tag in (HIDE_TAG, MOLDING_HIDE_TAG):
            if obj.get(tag):
                try:
                    obj.hide_set(False)
                except Exception:
                    pass
                del obj[tag]


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
              'preview': set(), 'fit': 3, 'paper': paper}
    _aim(r3d, wall)
    _bump_gen()
    area.tag_redraw()
    return True


def leave(context=None, restore_view=True):
    global _state, _edit, _noting, _note_drag
    if _state is None:
        return
    st, _state, _edit = _state, None, None
    _noting = _note_drag = None
    _picture_clear()
    _side_free()
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
    """The next (or last) page of the drawings."""
    if _state is None:
        return False
    listed = pages(context)
    if len(listed) < 2:
        return False
    current = current_page_key(context)
    i = next((n for n, p in enumerate(listed) if p['key'] == current), None)
    if i is None:
        i = -1 if direction > 0 else 0
    return show_page(context, listed[(i + direction) % len(listed)])


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
        if show_option(scene, 'DECIMAL'):
            # The same sixteenth the fraction would show, as a decimal.
            return f"{n / 16.0:.4f}".rstrip('0').rstrip('.') + '"'
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
    """A value's width in the face it will be drawn in: the interface
    font on screen; on paper the print's own face (or the caller's), so
    a value sits where the layout put it and its paper patch fits it."""
    if _print_scale is not None:
        return (_print_measure or hb_pdf.text_width)(text, size)
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
    # The wall's text objects and whatever notes an add-on supplies.
    ('ANNOTATIONS', "Annotations", True),
    # What stands inside the cabinets (shelves, dividers, roll-outs),
    # drawn through the fronts as dashed lines.
    ('INTERIORS', "Interior Lines", False),
    # Values as decimal inches (25.875") instead of fractions (25 7/8").
    ('DECIMAL', "Decimal Inches", False),
    # The wall from above, over the elevation, and from the front
    # right, beside it: the three views a sheet shows together.
    ('PLAN', "Plan View", False),
    ('ISO', "Iso View", False),
    # Crown, base, light rail and the other moulding runs. Off, they are
    # left out of the elevation and the plan, on screen and in print, so
    # the cabinets read on their own. The iso keeps them: it is the
    # picture of the finished wall.
    ('MOLDING', "Molding", True),
    # The wall's detail cards (a moulding section, a drawer from above),
    # stacked to the right of the elevation. Offered when an add-on
    # supplies cards.
    ('DETAILS', "Details", True),
)


# ---- Annotation sources ------------------------------------------------------------
# Another add-on can hand the elevation notes to draw over the wall
# (labels, callouts, leaders). A source is fn(scene, wall) returning a
# list of primitives in world space:
#   {'kind': 'TEXT', 'origin': Vector, 'x_axis': Vector (reading
#    direction), 'text': str (may hold newlines),
#    'align': 'LEFT' | 'CENTER' | 'RIGHT', 'valign': 'CENTER' (the
#    block is centred on the origin, the default) | 'BOTTOM' (it stands
#    on it) | 'TOP' (it hangs from it)}
#   {'kind': 'LINES', 'points': [Vector, ...]} (pairs, like GPU LINES;
#    'heads': [(tip, from), ...] sets an arrowhead at each tip, pointing
#    away from `from`, at a fixed size on screen)
#   {'kind': 'DIM', 'a': Vector, 'b': Vector, 'at': Vector} (a
#    dimension somebody placed by hand: measured from a to b, its line
#    through `at`. It is drawn as one of the view's own, across or up
#    the wall, whichever the two points are further apart in)
#   {'kind': 'FILL', 'points': [Vector, ...]} (a flat polygon's corners
#    in order, filled in 'color' under everything else: a return wall)
#   {'kind': 'LEGEND', 'rows': [(mark, text), ...]} (what the circled
#    marks on this wall stand for: listed in a box under the elevation)
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
    if key == 'DETAILS':
        return bool(_card_sources)
    return True


# ---- Mouldings ---------------------------------------------------------------------
# The Molding toggle takes the moulding runs out of the elevation and
# the plan. On screen they are hidden for as long as the view is up (and
# shown again when it closes or the toggle goes back on); the plan and
# the print leave them out of what they read. The iso still shows them,
# reading them while they are hidden (_molding_shown).

MOLDING_HIDE_TAG = 'HB_ELEVATION_MOLDING_HIDDEN'
MOLDING_MARKS = ('IS_HB_MOLDING_SWEEP', 'IS_CROWN_MOLDING',
                 'IS_TOE_KICK_MOLDING', 'IS_UPPER_BOTTOM_MOLDING',
                 'IS_FRAMELESS_MOLDING', 'IS_CLOSET_MOLDING')
_molding_tests = []
_molding_cache = {}


def register_molding_test(fn):
    """Another add-on's own mouldings: fn(obj) is True for one."""
    if fn not in _molding_tests:
        _molding_tests.append(fn)
    _bump_gen()


def unregister_molding_test(fn):
    if fn in _molding_tests:
        _molding_tests.remove(fn)
    _bump_gen()


def is_molding(obj):
    if any(obj.get(mark) for mark in MOLDING_MARKS):
        return True
    for fn in _molding_tests:
        try:
            if fn(obj):
                return True
        except Exception:
            continue
    return False


def _molding_names(scene):
    """Names of the scene's mouldings and of everything under them (a
    run's profile), read once per change of the model."""
    key = (_gen, scene.name)
    if _molding_cache.get('key') == key:
        return _molding_cache['names']
    verdict = {}

    def under(obj, depth=0):
        got = verdict.get(obj.name)
        if got is None:
            got = is_molding(obj) or (
                obj.parent is not None and depth < 64
                and under(obj.parent, depth + 1))
            verdict[obj.name] = got
        return got

    names = frozenset(o.name for o in scene.objects if under(o))
    _molding_cache.update(key=key, names=names)
    return names


def _molding_left_out(scene):
    """The names the pictures leave out: the mouldings when the toggle
    is off, nothing when it is on."""
    if show_option(scene, 'MOLDING'):
        return frozenset()
    return _molding_names(scene)


def _apply_molding(scene):
    """Hide the mouldings in the viewport, or show the ones this hid
    again, to match the toggle. Returns how many changed."""
    names = _molding_left_out(scene)
    changed = 0
    for obj in scene.objects:
        try:
            if obj.name in names:
                if obj.hide_get() or obj.hide_viewport:
                    continue
                obj.hide_set(True)
                obj[MOLDING_HIDE_TAG] = True
                changed += 1
            elif obj.get(MOLDING_HIDE_TAG):
                obj.hide_set(False)
                del obj[MOLDING_HIDE_TAG]
                changed += 1
        except Exception:
            continue                    # not in this view layer
    return changed


@contextlib.contextmanager
def _molding_shown(scene, layer):
    """Show the mouldings the toggle hid for as long as it takes to
    read them, then hide them again. Nothing is drawn in between, and
    the model has not changed, so the change count is put back."""
    global _gen
    hid = []
    for obj in scene.objects:
        if not obj.get(MOLDING_HIDE_TAG):
            continue
        try:
            if obj.hide_get(view_layer=layer):
                obj.hide_set(False, view_layer=layer)
                hid.append(obj)
        except Exception:
            continue
    if not hid:
        yield
        return
    gen = _gen
    try:
        layer.update()
        yield
    finally:
        for obj in hid:
            try:
                obj.hide_set(True, view_layer=layer)
            except Exception:
                pass
        layer.update()
        _gen = gen


def _watch_molding(scene):
    """A moulding made again while the toggle is off (a cabinet moved,
    the run rebuilt) comes back shown: hide it, off the draw."""
    if _molding_cache.get('queued'):
        return
    names = _molding_left_out(scene)
    if not names:
        return
    for name in names:
        obj = scene.objects.get(name)
        try:
            loose = obj is not None and not (obj.hide_get()
                                             or obj.hide_viewport)
        except Exception:
            continue
        if loose:
            break
    else:
        return
    _molding_cache['queued'] = True
    scene_name = scene.name

    def settle():
        _molding_cache.pop('queued', None)
        sc = bpy.data.scenes.get(scene_name)
        if sc is not None and _state is not None \
                and _state.get('scene') == scene_name:
            _apply_molding(sc)
        return None

    bpy.app.timers.register(settle, first_interval=0.0)


def _note_world(obj, depth=0):
    """World matrix of a text object the view has hidden: a hidden
    object's own is not kept up to date, its shown parent's is."""
    parent = obj.parent
    if parent is None or depth > 32:
        return obj.matrix_basis.copy()
    if parent.type == 'FONT' and parent.get(HIDE_TAG):
        pw = _note_world(parent, depth + 1)
    else:
        pw = parent.matrix_world
    return pw @ obj.matrix_parent_inverse @ obj.matrix_basis


def _text_object_notes(scene, wall):
    """The text objects standing on the wall (an appliance's name, a
    label on a part) as notes: the view hides the objects and letters
    them in its own style. Text lying flat or facing another way is
    left out."""
    roots = [wall]
    on_screen = _state is not None and _state.get('wall') == wall.name \
        and _print_scale is None
    if _state is not None and _state.get('wall') == wall.name:
        roots += [scene.objects.get(n) for n in _state.get('extra', ())]
    loose = []
    front = -(wall.matrix_world.col[1].xyz.normalized())
    prims = []
    seen = set()
    for root in roots:
        if root is None:
            continue
        for obj in root.children_recursive:
            if obj.type != 'FONT' or obj.name in seen:
                continue
            seen.add(obj.name)
            if scene.objects.get(obj.name) is None:
                continue
            try:
                hidden = obj.hide_viewport or obj.hide_get()
            except Exception:
                continue
            if not hidden:
                # New on the wall, or shown again behind the view's back
                # (an appliance's model switched off and on).
                if on_screen:
                    loose.append(obj.name)
            elif not obj.get(HIDE_TAG):
                continue
            body = obj.data.body.strip()
            if not body:
                continue
            mw = _note_world(obj) if obj.get(HIDE_TAG) else obj.matrix_world
            normal = mw.col[2].xyz
            if normal.length < 1e-9 or normal.normalized().dot(front) < 0.7:
                continue
            xs = [c[0] for c in obj.bound_box]
            ys = [c[1] for c in obj.bound_box]
            align = obj.data.align_x if obj.data.align_x in (
                'LEFT', 'CENTER', 'RIGHT') else 'CENTER'
            x = {'LEFT': min(xs), 'RIGHT': max(xs)}.get(
                align, (min(xs) + max(xs)) / 2.0)
            prims.append({
                'kind': 'TEXT',
                'origin': mw @ Vector((x, (min(ys) + max(ys)) / 2.0, 0.0)),
                'x_axis': mw.col[0].xyz.normalized(),
                'text': body, 'align': align})
    if loose:
        bpy.app.timers.register(lambda: _hide_text_objects(scene.name, loose),
                                first_interval=0.0)
    return prims


def _hide_text_objects(scene_name, names):
    """Off the draw: hide text objects that turned up on the wall while
    its elevation is showing."""
    scene = bpy.data.scenes.get(scene_name)
    if scene is None or _state is None or _state.get('scene') != scene_name:
        return None
    for name in names:
        obj = scene.objects.get(name)
        if obj is None or obj.type != 'FONT':
            continue
        try:
            if obj.hide_get():
                continue
            obj.hide_set(True)
            obj[HIDE_TAG] = True
        except Exception:
            continue
    return None


# A text object and a source's note for it within this of each other say
# the same thing once.
NOTE_SAME = 0.15


_NOTE_NUMBER = re.compile(
    r'(?<![\w./])(\d+ \d+/\d+|\d+/\d+|\d*\.\d+|\d+)"')


def _note_numbers(scene, text):
    """A note's inch values (D-25.5", 4" FLUSH FIN) written the way the
    dimensions are: fractions, or decimals with Decimal Inches on."""
    us = scene.unit_settings
    if us.system != 'IMPERIAL' or us.length_unit == 'FEET' or '"' not in text:
        return text

    def swap(m):
        raw = m.group(1)
        try:
            if '/' in raw:
                whole, _sp, frac = raw.rpartition(' ')
                num, den = frac.split('/')
                inches = (float(whole) if whole else 0.0) \
                    + float(num) / float(den)
            else:
                inches = float(raw)
        except (ValueError, ZeroDivisionError):
            return m.group(0)
        return format_length(scene, units.inch(inches))

    return _NOTE_NUMBER.sub(swap, text)


@hb_utils.with_children_index
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
    try:
        said = [(pr['text'].strip().upper(), pr['origin']) for pr in prims
                if pr.get('kind') == 'TEXT' and pr.get('text')]
        for pr in _text_object_notes(scene, wall):
            text = pr['text'].upper()
            if not any(t == text and (o - pr['origin']).length < NOTE_SAME
                       for t, o in said):
                prims.append(pr)
    except Exception as exc:
        print(f"Elevation annotations: {exc}")
    for i, note in enumerate(_user_notes(wall)):
        prims += _user_note_prims(wall, note, i)
    out = []
    for pr in prims:
        if pr.get('kind') == 'TEXT' and pr.get('text'):
            text = _note_numbers(scene, pr['text'])
            if text != pr['text']:
                pr = dict(pr, text=text)
        out.append(pr)
    prims = out
    _annotation_cache['key'] = key
    _annotation_cache['prims'] = prims
    return prims


ANNOTATION_FONT_SIZE = 10
ANNOTATION_LINE = (0.10, 0.10, 0.12, 0.9)
ARROW_PX = 8.0              # an arrowhead's length on screen
ARROW_HALF_PX = 2.4         # and half its width


def _note_lift(pr, total):
    """How far a note's block is moved up its own height axis so that
    it stands on (BOTTOM) or hangs from (TOP) its origin."""
    return {'BOTTOM': total / 2.0, 'TOP': -total / 2.0}.get(
        pr.get('valign'), 0.0)


def _arrow_heads(prims, P, s):
    """[(colour, [tip, corner, corner])] on screen for the arrowheads
    the LINES primitives ask for."""
    out = []
    for pr in prims:
        if pr.get('kind') != 'LINES':
            continue
        for tip, tail in pr.get('heads', ()):
            a, b = P(tip), P(tail)
            if a is None or b is None:
                continue
            d = Vector((a.x - b.x, a.y - b.y))
            if d.length < 1e-6:
                continue
            d.normalize()
            n = Vector((-d.y, d.x))
            base = Vector((a.x, a.y)) - d * ARROW_PX * s
            out.append((tuple(pr.get('color', ANNOTATION_LINE)),
                        [(a.x, a.y),
                         tuple(base + n * ARROW_HALF_PX * s),
                         tuple(base - n * ARROW_HALF_PX * s)]))
    return out
NOTE_FILL = (0.78, 0.78, 0.78, 1.0)
BUBBLE_FONT_SIZE = 12
BUBBLE_SEGMENTS = 32


def _draw_noting(context, region, rv3d):
    """The note being placed or typed: its leader while it is dragged
    out, its text with a caret while it is typed."""
    n = _noting
    wall = active_wall(context)
    if n is None or wall is None or n.get('x') is None:
        return
    note = {'x': n['x'], 'z': n['z'], 'tip': n.get('tip'),
            'turn': n.get('turn', 0),
            'text': (n['typed'] + '|') if n['stage'] == 'TYPE' else ''}
    prims = [dict(p, color=HOVER) for p in _user_note_prims(wall, note, None)]
    _draw_annotations(context, region, rv3d, prims)


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


def _draw_annotations(context, region, rv3d, prims=None):
    """The wall's notes; or just `prims` (a note being typed)."""
    wall = active_wall(context)
    if wall is None:
        return
    if prims is None:
        if not show_option(context.scene, 'ANNOTATIONS'):
            return
        prims = _annotations(context.scene, wall)
        if _noting is not None and _noting.get('index') is not None:
            # The note being retyped shows as it is typed, not as it was.
            prims = [p for p in prims if p.get('user') != _noting['index']]
    if not prims:
        return
    s = _s()

    def P(v):
        return view3d_utils.location_3d_to_region_2d(region, rv3d, v)

    for pr in prims:
        if pr.get('kind') != 'FILL':
            continue
        pts = [P(v) for v in pr.get('points', ())]
        if len(pts) < 3 or any(p is None for p in pts):
            continue
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", tuple(pr.get('color', NOTE_FILL)))
        batch_for_shader(shader, 'TRI_FAN',
                         {"pos": [(p.x, p.y) for p in pts]}).draw(shader)
        ring = [(p.x, p.y) for p in pts]
        _stroke(region, [q for a, b in zip(ring, ring[1:] + ring[:1])
                         for q in (a, b)], 1.0 * s, ANNOTATION_LINE)
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
    heads = _arrow_heads(prims, P, s)
    if heads:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        for color, tri in heads:
            shader.bind()
            shader.uniform_float("color", color)
            batch_for_shader(shader, 'TRIS', {"pos": tri}).draw(shader)
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
        hot = pr.get('user') is not None and _hover == ('NOTE', pr['user'])
        blf.color(0, *(HOVER_TEXT if hot else pr.get('color', TEXT)))
        blf.enable(0, blf.SHADOW)
        blf.shadow(0, TEXT_HALO_BLUR, *TEXT_HALO)
        blf.shadow_offset(0, 0, 0)
        blf.enable(0, blf.ROTATION)
        blf.rotation(0, ang)
        for i, row in enumerate(rows):
            tw, th = blf.dimensions(0, row)
            align = pr.get('align', 'CENTER')
            dx = {'LEFT': 0.0, 'RIGHT': -tw}.get(align, -tw / 2.0)
            # Rows stack downward from a block centred on the origin
            # (or stood on it, or hung from it).
            dy = total / 2.0 - lh * (i + 1) + (lh - th) / 2.0 \
                + _note_lift(pr, total)
            x = o.x + dx * ca - dy * sa
            y = o.y + dx * sa + dy * ca
            blf.position(0, x, y, 0)
            draw_glyphs(0, row)
        blf.disable(0, blf.ROTATION)
        blf.disable(0, blf.SHADOW)


_show_defaults = {}


def set_show_defaults(values):
    """Another add-on's choice of what a wall shows before the user has
    switched anything: {key: bool} over SHOW_OPTIONS' own defaults. A
    scene's own choices are kept."""
    _show_defaults.clear()
    _show_defaults.update({k: bool(v) for k, v in (values or {}).items()})
    _bump_gen()


def show_option(scene, key):
    default = next((d for k, _l, d in SHOW_OPTIONS if k == key), False)
    default = _show_defaults.get(key, default)
    if key in MODE_OPTIONS:
        # The plan and iso ride with the wall in a Compact room and
        # have pages of their own in a Full one.
        default = room_mode(scene) == 'COMPACT'
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
    if key == 'MOLDING' and _state is not None \
            and _state.get('scene') == scene.name:
        _apply_molding(scene)
    return value


def _height_levels(group, height):
    """The height chain for some products: floor, counter line (the base
    cabinets' top; a dishwasher or range a fraction under it is not a
    level of its own), upper bottoms and tops, tall tops. It stops at
    the highest of them: the space left over it to the ceiling is the
    overall height's to tell."""
    levels = {0.0}
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
    if len(levels) < 2:
        return [0.0, height]
    return _chain(levels, 0.0, max(levels))


# A face frame's own dims stand this far inside its edges, in pixels.
FF_INSET_PX = 16
# A stile starting within this of a row's band stands in that row.
BAND_REACH = units.inch(1.0)

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


_centerline_cache = {}


def _centerlines(scene, wall, length, items):
    key = (_gen, scene.name, wall.name, round(length, 5),
           len(_centerline_sources), tuple(it.obj.name for it in items))
    if _centerline_cache.get('key') != key:
        _centerline_cache['key'] = key
        _centerline_cache['lines'] = _centerlines_now(scene, wall, length,
                                                      items)
    return _centerline_cache['lines']


def _centerlines_now(scene, wall, length, items):
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
    reads blind, stile, opening ... to the cabinet's edge. A tall's
    frame reads in both rows, over its top and under the floor. Each
    row reads the frame where it meets that row: under the floor the
    stiles that stand in the frame's bottom band (a desk's two legs,
    not the stile between the drawers over its knee space), over the
    top the ones in its top band. 'open':
    {(item name, opening start)} the openings left open for a
    refrigerator, which say so under the floor. 'legs': {(item name,
    stile start)} a refrigerator cabinet's end stiles run down to the
    floor as legs. 'drops':
    see _front_drops; a drop's filler stiles stand in the dropped band
    only, so they are not stiles of the frame."""
    out = {'lower': [], 'upper': [], 'columns': [], 'sections': [],
           'drops': [], 'stiles': {}, 'open': set(), 'legs': set()}
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
        row = 'upper' if (it.kind == 'UPPER' or it.tall) else 'lower'

        def row_segs(top):
            """The frame's stile / opening breaks where it meets a row:
            its top band (between the top rail and the next rail down)
            or its bottom band."""
            if top:
                edge = min([b[2] for b in rails if b[3] >= fz1 - MERGE]
                           or [fz1])
                mine = [b for b in verticals if b[3] >= edge - BAND_REACH]
            else:
                edge = max([b[3] for b in rails if b[2] <= fz0 + MERGE]
                           or [fz0])
                mine = [b for b in verticals if b[2] <= edge + BAND_REACH]
            band = _merge([(b[0], b[1]) for b in mine]) or stiles
            xs = _chain([v for a, b in band for v in (a, b)], fx0, fx1)
            return [(a, b, it) for a, b in zip(xs, xs[1:])]

        segs = row_segs(row == 'upper')
        # Which stile each stile segment is, for where its value sits:
        # the frame's left end, its right end, or one between.
        for a, b in stiles:
            out['stiles'][(it.name, round(a, 4), round(b, 4))] = (
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
        blind = [g for g in segs if g[0] < fx0 - MERGE or g[1] > fx1 + MERGE]
        out[row] += segs
        if it.tall and it.kind == 'LOWER':
            low = row_segs(False)
            out['lower'] += ([g for g in blind if g[1] <= fx0 + MERGE] + low
                             + [g for g in blind if g[0] >= fx1 - MERGE])
            segs = segs + low
        if ffc is not None and it.obj.get('CLASS_NAME') == 'RefrigeratorCabinet':
            ends = sorted(stiles)
            if ends and getattr(ffc, 'extend_left_stile_to_floor', False):
                out['legs'].add((it.name, round(ends[0][0], 4)))
            if ends and getattr(ffc, 'extend_right_stile_to_floor', False):
                out['legs'].add((it.name, round(ends[-1][0], 4)))
        # An opening a refrigerator stands in is marked open.
        try:
            for child in it.obj.children_recursive:
                if child.get('SIZE_ROLE') != 'REFRIGERATOR':
                    continue
                box = _wall_box(child, Fi)
                if box is None:
                    continue
                cx = (box[0] + box[1]) / 2.0
                for a, b, _it in segs:
                    if a < cx < b:
                        out['open'].add((it.name, round(a, 4)))
        except Exception:
            pass
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
    sharing a bottom. Each spans the outer edges of its stiles; the
    stile between two sections runs the height of the one that hangs
    lower and counts in that one only, so the sections add up to the
    cabinet. A middle section is left out; the ends are what get
    checked against the cabinets below."""
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

    def bottom(run):
        return min(bottoms[run[0]:run[1] + 1])

    out = []
    for i in (0, len(runs) - 1):
        first, last = runs[i]
        z = bottom(runs[i])
        x0, x1 = cols[first][0], cols[last][1]
        if i == 0 or bottom(runs[i - 1]) > z - MERGE:
            x0 = outer(x0, True)
        if i == len(runs) - 1 or bottom(runs[i + 1]) > z - MERGE:
            x1 = outer(x1, False)
        out.append((it, x0, x1, z))
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


def _face_frame_height_dims(columns, dims, sx, sy, s, moved=None,
                            hidden=(), keep_out=(), scene=None):
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
        # A string on its bay can be dragged along it or removed, like
        # the ones out past the wall's ends.
        chain = ('BAY', it.name, round(c0, 3))
        cid = _chain_id(chain)
        if cid in hidden:
            continue
        x = sx(c0) + inset
        if cid in (moved or {}):
            try:
                x += float(moved[cid]) * s
            except (TypeError, ValueError):
                pass
        elif keep_out and scene is not None:
            # A note in the string's way (the cabinet's depth, down in
            # the kick): the string steps along the bay past it, while
            # there is bay left to step along.
            pad = TEXT_GAP_PX * s
            th = FONT_SIZE * s * 0.75
            spots = []          # (mid height, value width) per value
            for a, b in zip(zs, zs[1:]):
                w = value_runs(format_length(scene, b - a),
                               FONT_SIZE * s, _blf_measure)[1]
                spots.append(((sy(a) + sy(b)) / 2.0, w))
            limit = sx(c1) - inset - max(w for _m, w in spots) - pad
            for _pass in range(3):
                hit = [n for n in keep_out for m, w in spots
                       if n[1] < m + th / 2.0 and n[1] + n[3] > m - th / 2.0
                       and n[0] < x + pad + w and n[0] + n[2] > x - 2 * s]
                if not hit:
                    break
                nx = max(n[0] + n[2] for n in hit) + 4 * s
                if nx > limit:
                    break
                x = nx
        for a, b in zip(zs, zs[1:]):
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': x,
                         'side': 1, 'value': b - a, 'target': None,
                         'item': it, 'w0': a, 'horiz': True,
                         'chain': chain,
                         # Where the string stands off its plain place,
                         # for a drag to start from.
                         'auto': (x - sx(c0) - inset) / max(s, 1e-6),
                         'key': ('FF_H', it.name, round(c0, 4),
                                 round(a, 4))})


_layout_cache = {}


def _layout(context, region, rv3d):
    """Every dimension on screen, its text placed. Shared by draw and
    click so hits cannot drift from pixels."""
    wall = active_wall(context)
    if wall is None or rv3d is None:
        return [], None
    scene = context.scene
    selected = frozenset(o.name for o in context.selected_objects)
    st = _state or {}
    key = (_gen, scene.name, wall.name, region.width, region.height,
           tuple(round(v, 5) for row in rv3d.perspective_matrix for v in row),
           selected, show_option(scene, 'FACE_FRAME'),
           frozenset(st.get('preview', ())), _s(),
           _cards_stamp(scene, wall), wall.get(CARDS_PROP))
    if _layout_cache.get('key') == key:
        return _layout_cache['result']
    _watch_molding(scene)
    result = _layout_wall(scene, wall, region, rv3d, selected=selected,
                          side_views=True)
    _layout_cache['key'] = key
    _layout_cache['result'] = result
    return result


@hb_utils.with_children_index
def _layout_wall(scene, wall, region, rv3d, selected=(), extra=None,
                 preview=None, face_frame=None, side_views=False):
    """_layout for any wall of `scene`, through any view. `extra` and
    `preview` as _items; `face_frame` overrides the scene's Face Frame
    toggle. `side_views` lays out the plan and iso that are switched on
    (where they go, and the plan's depths) as well."""
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

    store = _heights(wall)
    moved = store['moved']
    hidden = set(store['hidden'])
    keep_out = []

    def ext_v(side, pos, z):
        """The extension line of a height string at level z: from the
        wall's end out to the string, or a stub across it when the
        string was dragged in over the wall."""
        ex = sx(wx1) if side > 0 else sx(wx0)
        if (pos - ex) * side > gap:
            dims_ext.append(((ex + side * gap, sy(z)),
                             (pos + side * over, sy(z))))
        else:
            dims_ext.append(((pos - over, sy(z)), (pos + over, sy(z))))

    def add_v(levels, pos, side, group, overall=False, chain=None):
        if pos is None:
            return                      # a string the user removed
        for z in levels:
            ext_v(side, pos, z)
        for a, b in zip(levels, levels[1:]):
            target = _vertical_target(group, a, b,
                                      wall.name if overall else None)
            item = target.pop('item', None) if target else None
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': pos,
                         'side': side, 'value': b - a, 'target': target,
                         'item': item, 'w0': a, 'chain': chain})

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
                             (it.name, round(a, 4), round(b, 4))),
                         'key': ('FF_W', it.name, round(a, 4), side)})
            # Under the floor, beside the opening it describes: over the
            # top it would read as a note on the cabinet above.
            if side < 0 and (it.name, round(a, 4)) in ff_all['open']:
                dims[-1]['tag'] = "OPEN"
            # A stile run down to the floor as a furniture leg.
            if side < 0 and dims[-1]['stile']                     and (it.name, round(a, 4)) in ff_all['legs']:
                dims[-1]['tag'] = "LEG"

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
    dims[-1]['tag'] = "OA"

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

    def v_line(side, segs, chain=None):
        """Screen x of the next vertical chain out on `side`: its values
        sit centred on the line when they fit and beside it, outward,
        when they don't, so it stands clear of the chain inside it. A
        chain the user dragged stands where it was put; the ones after
        it keep their places. None for a chain the user removed, which
        takes no room."""
        if chain is not None and _chain_id(chain) in hidden:
            return None
        w, beside = 0.0, False
        for a, b in segs:
            w = max(w, value_runs(format_length(scene, b - a),
                                  FONT_SIZE * s, _blf_measure)[1])
            if abs(sy(b) - sy(a)) < th + v_clear:
                beside = True
        pos = reach[side] + side * max(w / 2.0 + pad, 0.0)
        reach[side] = pos + side * ((w + 2 * pad) if beside
                                    else (w / 2.0 + pad))
        if chain is not None:
            try:
                pos += float(moved.get(_chain_id(chain), 0.0)) * s
            except (TypeError, ValueError):
                pass
        return pos

    def ff_side(side, edge):
        reach[side] = edge + side * (first - pad)
        ex = sx(wx1) if side > 0 else sx(wx0)
        kicks = set()
        for ti, tr in enumerate(side_tiers[side]):
            segs = []
            for zs, _it in tr:
                for a, b in zip(zs, zs[1:]):
                    if a <= MERGE and b < KICK_MAX and round(b, 4) in kicks:
                        continue
                    segs.append((a, b))
            chain = ('FF', side, ti)
            cursor = v_line(side, segs, chain)
            if cursor is None:
                continue
            for zs, it in tr:
                for z in zs:
                    ext_v(side, cursor, z)
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
                                 'outward': True, 'chain': chain,
                                 'key': ('FF_S', side, round(cursor),
                                         round(a, 4))})

    ff_side(1, right_x)
    ff_side(-1, left_x)

    def pairs(levels):
        return list(zip(levels, levels[1:]))

    # Heights: nearest each wall end, the chain of what stands at that
    # end (a tall there reads as one height, not cut at the counter and
    # upper lines of the cabinets beside it). The levels of the rest of
    # that half follow on a second line, unless the other side of the
    # wall already shows them.
    def end_stack(group, side):
        solid = [it for it in group if not it.shelf and not _is_hood(it)]
        if not solid:
            return []
        end = (min(solid, key=lambda i: i.x0) if side < 0
               else max(solid, key=lambda i: i.x1))
        return [it for it in solid
                if it.x0 < end.x1 - MERGE and it.x1 > end.x0 + MERGE]

    def level_set(levels):
        return {round(z, 3) for z in levels}

    side_levels = {}
    for side, group in ((1, right_group), (-1, left_group)):
        stack = end_stack(group, side)
        side_levels[side] = (stack, _height_levels(stack, height),
                             _height_levels(group, height))
    shown = {1: set(), -1: set()}
    for side, group in ((1, right_group), (-1, left_group)):
        stack, at_end, whole = side_levels[side]
        # A lone height (a tall, a run of bases) still reads, unless it
        # is the wall's own.
        if len(at_end) > 2 or (len(at_end) == 2
                               and abs(at_end[-1] - height) > MERGE):
            chain = ('END', side)
            add_v(at_end, v_line(side, pairs(at_end), chain), side, stack,
                  chain=chain)
            shown[side] |= level_set(at_end)
        if len(whole) > 2 and not level_set(whole) <= shown[side]:
            # The right is laid out first: of the left only its end
            # chain is certain to be drawn.
            other = (level_set(side_levels[-1][1]) if side > 0
                     else shown[1])
            if not level_set(whole) <= other:
                chain = ('HALF', side)
                add_v(whole, v_line(side, pairs(whole), chain), side, group,
                      chain=chain)
                shown[side] |= level_set(whole)
        if side > 0:
            chain = ('WALL', 1)
            add_v([0.0, height], v_line(1, [(0.0, height)], chain), 1, [],
                  overall=True, chain=chain)

    # Left, further out: window and door sills and heads.
    if openings:
        lv = {0.0, height}
        for it in openings:
            lv.update((max(it.z0, 0.0), it.z1))
        lv = _chain(lv, 0.0, max(lv))
        chain = ('OPEN', -1)
        add_v(lv, v_line(-1, pairs(lv), chain), -1, openings, chain=chain)

    # Strings the user clicked in: each at its place on the wall.
    for i, u in enumerate(store['added']):
        try:
            x = float(u.get('x', 0.0))
            lv = sorted({round(float(z), 5) for z in u['levels']})
        except (TypeError, ValueError):
            continue
        if len(lv) < 2:
            continue
        pos = sx(x)
        for z in lv:
            dims_ext.append(((pos - over, sy(z)), (pos + over, sy(z))))
        for a, b in zip(lv, lv[1:]):
            dims.append({'axis': 'V', 'a': sy(a), 'b': sy(b), 'pos': pos,
                         'side': 1, 'value': b - a, 'target': None,
                         'item': None, 'w0': a, 'horiz': True,
                         'chain': ('USER', i),
                         'key': ('USER', i, round(a, 4))})

    # Dimensions somebody placed by hand (a note source hands them
    # over): each where it was put, drawn as one of the view's own.
    if show_option(scene, 'ANNOTATIONS'):
        for i, pr in enumerate(_annotations(scene, wall)):
            if pr.get('kind') != 'DIM':
                continue
            try:
                a, b, at = (fr[1] @ pr[k] for k in ('a', 'b', 'at'))
            except Exception:
                continue
            if abs(b.x - a.x) >= abs(b.z - a.z):
                lo, hi = sorted((a.x, b.x))
                if hi - lo <= MERGE:
                    continue
                pos = sy(at.z)
                for x, z in ((a.x, a.z), (b.x, b.z)):
                    side = 1.0 if pos >= sy(z) else -1.0
                    if abs(pos - sy(z)) > gap + over:
                        dims_ext.append(((sx(x), sy(z) + side * gap),
                                         (sx(x), pos + side * over)))
                    else:
                        dims_ext.append(((sx(x), pos - over),
                                         (sx(x), pos + over)))
                dims.append({'axis': 'H', 'a': sx(lo), 'b': sx(hi),
                             'pos': pos, 'side': 1, 'value': hi - lo,
                             'target': None, 'item': None, 'w0': lo,
                             'key': ('NOTE_D', i)})
            else:
                lo, hi = sorted((a.z, b.z))
                if hi - lo <= MERGE:
                    continue
                pos = sx(at.x)
                for x, z in ((a.x, a.z), (b.x, b.z)):
                    side = 1.0 if pos >= sx(x) else -1.0
                    if abs(pos - sx(x)) > gap + over:
                        dims_ext.append(((sx(x) + side * gap, sy(z)),
                                         (pos + side * over, sy(z))))
                    else:
                        dims_ext.append(((pos - over, sy(z)),
                                         (pos + over, sy(z))))
                dims.append({'axis': 'V', 'a': sy(lo), 'b': sy(hi),
                             'pos': pos, 'side': 1, 'value': hi - lo,
                             'target': None, 'item': None, 'w0': lo,
                             'horiz': True, 'key': ('NOTE_D', i)})

    if ff:
        try:
            keep_out = _note_rects(scene, wall, fr[1], sx, sy, s)
        except Exception as exc:
            print(f"Elevation notes: {exc}")
        _face_frame_height_dims(on_frame, dims, sx, sy, s, moved, hidden,
                                keep_out, scene)

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
                     'item': it, 'w0': lo, 'tag': "CL",
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

    if not keep_out:
        try:
            keep_out = _note_rects(scene, wall, fr[1], sx, sy, s)
        except Exception as exc:
            print(f"Elevation notes: {exc}")
    _place_text(scene, dims, region, dims_ext, keep_out)
    for d in dims:
        if 'key' not in d:
            d['key'] = (d['axis'], round(d['pos'] / max(tier, 1)),
                        round(d['w0'], 4))
    extra = {'ext': dims_ext, 'floor': (sx(0.0), sx(length), floor_y),
             'items': items, 'sx': sx, 'sy': sy, 'ext_n': len(dims_ext),
             'side': {}, 'cards': [], 'notes': [], 'note_tips': []}
    # The typed notes, where a click finds them: each one's text, and
    # the tip of its leader.
    try:
        extra['notes'] = [
            (pr['user'], rect)
            for pr, rect in _note_boxes(scene, wall, fr[1], sx, sy, s)
            if pr.get('user') is not None]
        if show_option(scene, 'ANNOTATIONS'):
            extra['note_tips'] = [
                (i, (sx(u['tip'][0]), sy(u['tip'][1])))
                for i, u in enumerate(_user_notes(wall)) if u['tip']]
    except Exception as exc:
        print(f"Elevation notes: {exc}")
    if side_views:
        try:
            _layout_cards(scene, wall, region, dims, extra, s)
        except Exception as exc:
            print(f"Elevation detail cards: {exc}")
        try:
            _layout_side_views(scene, wall, region, dims, extra, s)
        except Exception as exc:
            print(f"Elevation side views: {exc}")
    return dims, extra


def _rects_overlap(a, b, m=2.0):
    return not (a[0] + a[2] + m <= b[0] or b[0] + b[2] + m <= a[0]
                or a[1] + a[3] + m <= b[1] or b[1] + b[3] + m <= a[1])


def _note_rects(scene, wall, Fi, sx, sy, s):
    """(x, y, w, h) on the sheet of each note lettered on the wall (a
    depth, a finished end, an appliance's name): the values are kept
    off them."""
    return [rect for _pr, rect in _note_boxes(scene, wall, Fi, sx, sy, s)]


def _note_boxes(scene, wall, Fi, sx, sy, s):
    """[(primitive, (x, y, w, h))] for the notes lettered on the wall."""
    if not show_option(scene, 'ANNOTATIONS'):
        return []
    size = ANNOTATION_FONT_SIZE * s
    th = size * 0.75
    lh = th * 1.35
    out = []
    for pr in _annotations(scene, wall):
        if pr.get('kind') != 'TEXT' or not pr.get('text'):
            continue
        o = Fi @ pr['origin']
        ax = Fi.to_3x3() @ pr.get('x_axis', Vector((1.0, 0.0, 0.0)))
        if abs(ax.x) < 1e-3 and abs(ax.z) < 1e-3:
            continue                    # seen edge-on: not drawn
        rows = pr['text'].splitlines()
        tw = max(_blf_measure(row, size) for row in rows)
        tall = lh * len(rows)
        cx, cy = sx(o.x), sy(o.z)
        lift = _note_lift(pr, tall)
        align = pr.get('align', 'CENTER')
        if abs(ax.z) > abs(ax.x):
            # Turned a quarter (a finished end). Reading up the wall its
            # height axis points left; reading down it, right.
            up = (ax.z > 0) == (sy(1.0) > sy(0.0))
            start = {'LEFT': 0.0, 'RIGHT': -tw}.get(align, -tw / 2.0)
            y0 = cy + start if up else cy - start - tw
            x0 = cx - lift if up else cx + lift
            out.append((pr, (x0 - tall / 2.0, y0, tall, tw)))
            continue
        x0 = {'LEFT': cx, 'RIGHT': cx - tw}.get(align, cx - tw / 2.0)
        out.append((pr, (x0, cy + lift - tall / 2.0, tw, tall)))
    return out


def _place_text(scene, dims, region, ext=(), keep_out=()):
    s = _s()
    blf.size(0, FONT_SIZE * s)
    th = blf.dimensions(0, "0123456789\"")[1]
    pad = TEXT_GAP_PX * s
    # A value fits between its ticks with this much clear either side.
    clear = (TICK_PX + 3) * 2 * s
    gap = BREAK_GAP_PX * s
    placed = list(keep_out)     # notes on the wall: values stay off them
    pending = []
    for d in dims:
        if d['axis'] == 'V':
            d['horiz'] = True   # every value reads left to right
        d['text'] = format_length(scene, d['value']) + d.get('suffix', '')
        d.pop('tag_rect', None)
        tw = value_runs(d['text'], FONT_SIZE * s, _blf_measure)[1]
        span = abs(d['b'] - d['a'])
        lo, hi = min(d['a'], d['b']), max(d['a'], d['b'])
        mid = (lo + hi) / 2.0
        n_inline = 1
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
                over_s = d['pos'] + th / 2.0 + 3.0 * s
                under_s = d['pos'] - th / 2.0 - 3.0 * s - th
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
            # A long line whose middle is taken (a note lettered there)
            # carries its value further along, still in the line.
            if inline and (th + clear + 2 * gap) * 3.0 <= span:
                inline += [(d['pos'] - tw / 2.0, lo + span * f - th / 2.0)
                           for f in (0.3, 0.7, 0.15, 0.85)]
            n_inline = len(inline)
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
        pending.append((0 if fits else 1, len(pending), d, rects,
                        n_inline if inline else 0))
    # A value that fits between its ticks has one good spot; it claims
    # it before a neighbour too narrow for its own value spills over.
    # Extension lines run out past every chain inside the one they
    # belong to; a value is kept off them where it has the choice.
    lines = [(min(a[0], b[0]), min(a[1], b[1]),
              max(a[0], b[0]), max(a[1], b[1])) for a, b in ext]
    t = 1.5 * s
    # Values keep this far apart; on paper, where everything is set
    # smaller, so is this.
    apart = 2.0 * min(1.0, s)

    def struck(r):
        x0, y0, x1, y1 = r[0] + t, r[1] + t, r[0] + r[2] - t, r[1] + r[3] - t
        return any(lx0 < x1 and lx1 > x0 and ly0 < y1 and ly1 > y0
                   for lx0, ly0, lx1, ly1 in lines)

    for _order, _i, d, rects, inline in sorted(pending,
                                                key=lambda p: p[:2]):
        free = [r for r in rects
                if not any(_rects_overlap(r, p, apart) for p in placed)]
        if not free:
            # Nowhere clear: on a note rather than on another value.
            free = [r for r in rects
                    if not any(_rects_overlap(r, p, apart)
                               for p in placed[len(keep_out):])]
        chosen = next((r for r in free if not struck(r)),
                      free[0] if free else rects[0])
        d['rect'] = chosen
        d['inline'] = any(chosen is r for r in rects[:inline])
        placed.append(chosen)
        if d.get('tag'):
            # Under the value, clear of the line it sits in or on.
            size = FONT_SIZE * TAG_SCALE * s
            gw = _blf_measure(d['tag'], size)
            x, y, w, h = chosen
            top = min(y, d['pos'] - 1.5 * s) if d['axis'] == 'H' else y
            d['tag_rect'] = (x + w / 2.0 - gw / 2.0,
                             top - TAG_GAP_PX * s - th * TAG_SCALE,
                             gw, th * TAG_SCALE)
            placed.append(d['tag_rect'])


# ---- Drawing -----------------------------------------------------------------------

def _stroke(region, pts, width, color):
    """A line with a dark halo under it, so it reads on any background."""
    hb_dim_style.stroke(region, pts, width, color, _s(), halo=HALO)


def _tick(x, y, s, axis='H'):
    """A short bar across the dimension line at one of its ends."""
    t = TICK_PX * s
    if axis == 'H':
        return [(x, y - t), (x, y + t)]
    return [(x - t, y), (x + t, y)]


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
        ticks = _tick(d['a'], y, s, 'H') + _tick(d['b'], y, s, 'H')
    else:
        x = d['pos']
        line = [p for a, b in spans for p in ((x, a), (x, b))]
        ticks = _tick(x, d['a'], s, 'V') + _tick(x, d['b'], s, 'V')
    return line, ticks


def _text(d, color, s, halo=None, plain=False):
    """A dimension's value at its rect. `plain` sets the text as typed
    (the edit field), with no small fraction."""
    x, y, w, h = d['rect']
    blf.size(0, FONT_SIZE * s)
    blf.color(0, *color)
    blf.enable(0, blf.SHADOW)
    own = halo is None
    if own:
        halo = TEXT_HALO
    blf.shadow(0, TEXT_HALO_BLUR if own else 5, *halo)
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
        if d.get('tag_rect'):
            blf.size(0, FONT_SIZE * TAG_SCALE * s)
            blf.position(0, d['tag_rect'][0], d['tag_rect'][1], 0)
            draw_glyphs(0, d['tag'])
    blf.disable(0, blf.ROTATION)
    blf.disable(0, blf.SHADOW)


def _bar_layout(context, area):
    """[(part, rect, label)] of the drawings bar at the bottom centre.
    A picture page keeps the parts that are not about a wall."""
    wall = active_wall(context)
    if wall is None:
        return []
    s = _s()
    on_wall = _picture is None
    title = _page_title(context) or "Drawings"
    blf.size(0, 12 * s)
    h = 28 * s
    gap = 3 * s

    def wide(label):
        return blf.dimensions(0, label)[0] + 24 * s

    many = len(pages(context)) > 1
    row = []
    if many:
        row.append(('PREV', None, 28 * s))
    row.append(('TITLE', title, blf.dimensions(0, title)[0] + 28 * s))
    if many:
        row.append(('NEXT', None, 28 * s))
    if on_wall:
        row += [('SHOW:' + key, label, h)
                for key, label, _default in SHOW_OPTIONS
                if _option_available(key)]
        row.append(('ADD_V', "+ Height", wide("+ Height")))
        row.append(('ADD_N', "+ Note", wide("+ Note")))
        store = _heights(wall)
        if store['moved'] or store['hidden']:
            row.append(('RESET_V', "Reset Heights", wide("Reset Heights")))
        mode = MODE_LABELS[room_mode(context.scene)]
        row.append(('MODE', mode, wide(mode)))
    shown = current_page(context)
    if shown is not None and shown.get('swap') is not None:
        label = shown.get('swap_label') or "Other View"
        row.append(('SWAP', label, wide(label)))
    row.append(('PRINT', "Print PDF", wide("Print PDF")))
    row.append(('EXIT', "Exit  Esc", wide("Exit  Esc")))
    total = sum(w for _p, _l, w in row) + gap * (len(row) - 1)
    xmin, xmax, ymin, _ymax = get_visible_window_bounds(area)
    x = (xmin + xmax) / 2.0 - total / 2.0
    y = ymin + 18 * s
    parts = []
    for part, label, w in row:
        parts.append((part, (x, y, w, h), label))
        x += w + gap
    return parts


CHIP_OFF = (0.55, 0.55, 0.57, 1.0)     # a toggle's icon while it is off


def _lifted(color, amount=0.18):
    """`color` a step toward white, alpha kept."""
    return tuple(c + (1.0 - c) * amount for c in color[:3]) + tuple(color[3:])


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
        on = on or (part == 'ADD_V' and _adding is not None)
        on = on or (part == 'ADD_N' and _noting is not None)
        if part == 'TITLE':
            bg = Theme.ACCENT_BG
        elif on:
            # A toggle that is on keeps its fill under the cursor (only
            # lifted a little), so hovering never reads as switching off.
            bg = _lifted(Theme.ACCENT_BG) if hovered else Theme.ACCENT_BG
        else:
            bg = Theme.BTN_HOVER_BG if hovered else Theme.BTN_BG
        draw_round_rect(shader, rx, ry, rw, rh, 5 * s, bg)
        glyph = (_SHOW_GLYPHS.get(part[5:]) if part.startswith('SHOW:')
                 else None)
        if glyph is not None:
            glyph(shader, rect, Theme.TEXT_PRIMARY if on
                  else Theme.TEXT_NORMAL if hovered else CHIP_OFF)
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
            if part == 'MODE' and hovered:
                _draw_chip_hint(shader, rect, "Full: each wall on its own "
                                "page.  Compact: plan and iso with the wall")
                shader.bind()
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


def _draw_remove_chip(dims, s):
    """The remove button of the height string under the cursor: a
    round red button with a cross, just above the string."""
    rect = _remove_chip(dims, _hover_chain, s)
    if rect is None:
        return
    x, y, w, h = rect
    over = (x - 3 * s <= _mouse[0] <= x + w + 3 * s
            and y - 3 * s <= _mouse[1] <= y + h + 3 * s)
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    draw_round_rect(shader, x, y, w, h, w / 2.0,
                    (0.92, 0.26, 0.22, 1.0) if over
                    else (0.74, 0.20, 0.18, 0.95))
    m = w * 0.30
    draw_lines(shader, [(x + m, y + m), (x + w - m, y + h - m),
                        (x + m, y + h - m), (x + w - m, y + m)],
               (1.0, 1.0, 1.0, 1.0))


# ---- Plan and iso beside the elevation ---------------------------------------
#
# The elevation is the viewport's own picture of the wall. Its plan and
# iso are the same scene drawn from two more directions into textures
# and set beside it, at the elevation's scale: the plan above it (lined
# up with it, the wall at the top), the iso to its left. They are
# pictures, redrawn when the model or the zoom changes.

SIDE_DIST = 60.0            # m the side views' cameras stand off
SIDE_MARGIN = 0.05          # m of paper kept round what they show
SIDE_GAP_PX = 34            # between the dimensions and a side view
SIDE_MAX_PX = 4096
SIDE_REFRESH = 0.25         # s between redraws while the model changes
ISO_YAW = math.radians(35.0)
ISO_PITCH = math.radians(25.0)
_side_cache = {}


# Clicking the iso turns it to be seen from the other side; kept on the
# wall (1 from the front left, 0 from the front right).
ISO_LEFT_PROP = 'HB_ELEVATION_ISO_LEFT'


def _iso_at(extra, mx, my):
    rect = ((extra or {}).get('side') or {}).get('ISO')
    return rect is not None and point_in_rect(mx, my, rect[:4])


def _side_on(scene):
    return [k for k in ('PLAN', 'ISO') if show_option(scene, k)]


def _side_box(wall, items):
    """(x0, x1, y0, y1, z0, z1, iso from the left) in the wall's frame
    of the wall, what stands on it and the lengths of return wall shown
    at its ends."""
    _F, Fi, length, height = _frame(wall)
    dims = _wall_dims(wall)
    thick = (dims[2] if dims and dims[2] else 0.15)
    box = [0.0, length, 0.0, thick, 0.0, height]
    objs = [wall] + [it.obj for it in items if not it.preview]
    for obj in objs:
        try:
            mw = obj.matrix_world
            pts = [Fi @ (mw @ Vector(c)) for c in obj.bound_box]
        except Exception:
            continue
        box[0] = min(box[0], min(q.x for q in pts))
        box[1] = max(box[1], max(q.x for q in pts))
        box[2] = min(box[2], min(q.y for q in pts))
        box[3] = max(box[3], max(q.y for q in pts))
        box[5] = max(box[5], max(q.z for q in pts))
    from_left = False
    try:
        returns, from_left = _return_boxes(wall, items)
        for footprint, _z0, z1 in returns:
            box[0] = min(box[0], min(q[0] for q in footprint))
            box[1] = max(box[1], max(q[0] for q in footprint))
            box[2] = min(box[2], min(q[1] for q in footprint))
            box[3] = max(box[3], max(q[1] for q in footprint))
            box[5] = max(box[5], z1)
    except Exception as exc:
        print(f"Elevation return walls: {exc}")
    # The side the iso is seen from, when the user turned it round.
    turned = wall.get(ISO_LEFT_PROP)
    if turned is not None:
        from_left = bool(turned)
    return tuple(box) + (from_left,)


def _side_camera(F, box, kind):
    """(camera matrix, (l, r, b, t)) of a side view: an orthographic
    camera's place in the world and the span of what it shows, in its
    own metres. The camera's x runs along the wall in both."""
    x0, x1, y0, y1, z0, z1 = box[:6]
    centre = Vector(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    if kind == 'PLAN':
        R = Matrix.Identity(4)
    else:
        # From the front right, or the front left when the only return
        # wall is on the right (it would stand in front of the work).
        yaw = -ISO_YAW if len(box) > 6 and box[6] else ISO_YAW
        R = (Matrix.Rotation(yaw, 4, 'Z')
             @ Matrix.Rotation(math.pi / 2.0 - ISO_PITCH, 4, 'X'))
    C = (F @ Matrix.Translation(centre) @ R
         @ Matrix.Translation((0.0, 0.0, SIDE_DIST)))
    Ci = C.inverted_safe()
    xs, ys = [], []
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                q = Ci @ (F @ Vector((x, y, z)))
                xs.append(q.x)
                ys.append(q.y)
    m = SIDE_MARGIN
    return C, (min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m)


def _ortho(l, r, b, t, n, f):
    return Matrix(((2.0 / (r - l), 0.0, 0.0, -(r + l) / (r - l)),
                   (0.0, 2.0 / (t - b), 0.0, -(t + b) / (t - b)),
                   (0.0, 0.0, -2.0 / (f - n), -(f + n) / (f - n)),
                   (0.0, 0.0, 0.0, 1.0)))


def _side_rects(scene, wall, dims, extra, s):
    """{kind: (x, y, w, h, camera, span)} in the layout's own units for
    the side views that are switched on."""
    kinds = _side_on(scene) if scene is not None else []
    if not kinds or extra is None:
        return {}
    F, _Fi, length, height = _frame(wall)
    sx, sy = extra['sx'], extra['sy']
    per_m = abs(sx(1.0) - sx(0.0))
    box = _side_box(wall, extra['items'])
    bx0, _bx1, _by0, by1 = _print_bounds(dims, extra, 1.0, length, height)
    gap = SIDE_GAP_PX * s
    out = {}
    for kind in kinds:
        C, (l, r, b, t) = _side_camera(F, box, kind)
        w, h = (r - l) * per_m, (t - b) * per_m
        if kind == 'PLAN':
            # Lined up with the elevation: the camera's x is the wall's.
            x = sx((box[0] + box[1]) / 2.0 + l)
            y = by1 + gap
        else:
            x = bx0 - gap - w
            y = sy(height / 2.0) - h / 2.0
        out[kind] = (x, y, w, h, C, (l, r, b, t))
    return out


PLAN_DEPTH_STEP = units.inch(1.0 / 16.0)


def _layout_side_views(scene, wall, region, dims, extra, s):
    """Place the side views (extra['side']) and dimension the plan: the
    depth of each distinct product depth, once, on the product of that
    depth nearest a wall end -- out past its outer side when nothing
    stands there, else just inside it."""
    rects = _side_rects(scene, wall, dims, extra, s)
    extra['side'] = rects
    plan = rects.get('PLAN')
    if plan is None:
        return
    x, y, _w, _h, _C, (l, _r, b, _t) = plan
    _F, Fi, length, _height = _frame(wall)
    sx = extra['sx']
    per_m = abs(sx(1.0) - sx(0.0))
    items = [it for it in extra['items']
             if not it.preview and it.kind != 'OPENING']
    box = _side_box(wall, extra['items'])
    cx, cy = (box[0] + box[1]) / 2.0, (box[2] + box[3]) / 2.0

    def px(xw):
        return x + (xw - cx - l) * per_m

    def py(yw):
        return y + (yw - cy - b) * per_m

    fronts = {}
    for it in items:
        try:
            mw = it.obj.matrix_world
            fronts[it.name] = min((Fi @ (mw @ Vector(c))).y
                                  for c in it.obj.bound_box)
        except Exception:
            continue
    by_depth = {}
    for it in items:
        front = fronts.get(it.name)
        if front is None or front > -MERGE:
            continue
        by_depth.setdefault(round(-front / PLAN_DEPTH_STEP), []).append(it)
    first = FIRST_TIER_PX * s
    gap = EXT_GAP_PX * s
    over = EXT_OVER_PX * s
    inset = FF_INSET_PX * s
    new = []
    taken = set()
    for _steps, group in sorted(by_depth.items(), reverse=True):
        it = min(group, key=lambda i: min(i.x0, length - i.x1))
        side = -1 if it.x0 <= length - it.x1 else 1
        front = fronts[it.name]
        edge = it.x0 if side < 0 else it.x1
        probe = edge + side * 0.02
        beside = any(o is not it and o.x0 < probe < o.x1
                     and fronts.get(o.name, 0.0) < -MERGE for o in items)
        outside = not beside and (side, 'OUT') not in taken
        if outside:
            taken.add((side, 'OUT'))
            pos = px(edge) + side * first
            for yw in (front, 0.0):
                extra['ext'].append(((px(edge) + side * gap, py(yw)),
                                     (pos + side * over, py(yw))))
        else:
            pos = px(edge) - side * inset
        new.append({'axis': 'V', 'a': py(front), 'b': py(0.0), 'pos': pos,
                    'side': side if outside else -side, 'value': -front,
                    'target': None, 'item': it, 'w0': front, 'horiz': True,
                    'outward': outside, 'key': ('PLAN_D', it.name)})
    # The wall's overall length over the plan, and its name in it.
    wd = _wall_dims(wall)
    thick = wd[2] if wd and wd[2] else 0.15
    pos = py(box[3]) + first
    for xw in (0.0, length):
        extra['ext'].append(((px(xw), py(thick) + gap),
                             (px(xw), pos + over)))
    new.append({'axis': 'H', 'a': px(0.0), 'b': px(length), 'pos': pos,
                'side': 1, 'value': length, 'target': None, 'item': None,
                'w0': 0.0, 'tag': "OA", 'key': ('PLAN_D', 'OA')})
    walls = room_walls(scene)
    if wall in walls:
        extra['plan_notes'] = [((px(length / 2.0), py(thick / 2.0)),
                                f"Wall {walls.index(wall) + 1}")]
    if new:
        _place_text(scene, new, region, ())
        dims.extend(new)


def _side_free():
    for entry in _side_cache.values():
        try:
            entry['off'].free()
        except Exception:
            pass
    _side_cache.clear()
    _side_wanted.clear()
    _side_geo.clear()


def _side_texture(context, area, region, kind, rect):
    """The side view's picture. It is drawn off the draw pass, from a
    timer: the draw asks for one when the model, the shading or the zoom
    has changed and shows the last picture until the new one is in."""
    _x, _y, w, h, C, (l, r, b, t) = rect
    tw = int(max(16, min(SIDE_MAX_PX, round(w))))
    th = int(max(16, min(SIDE_MAX_PX, round(h))))
    entry = _side_cache.get(kind)
    key = (_gen, _state['wall'], area.spaces.active.shading.type,
           tuple(round(v, 4) for v in (l, r, b, t)))
    if entry is not None and entry['key'] == key \
            and 0.8 <= tw / entry['size'][0] <= 1.25:
        return entry['off']
    _side_wanted[kind] = {'area': area, 'region': region, 'C': C.copy(),
                          'span': (l, r, b, t), 'size': (tw, th),
                          'key': key}
    if not _side_wanted.get('queued'):
        import time
        _side_wanted['queued'] = True
        since = time.monotonic() - (entry['at'] if entry else 0.0)
        bpy.app.timers.register(
            _side_render, first_interval=max(0.0, SIDE_REFRESH - since))
    return entry['off'] if entry is not None else None


_side_wanted = {}


SIDE_LINE_PX = 1.3          # a side view's line, in screen pixels
SIDE_SUPER = 2              # drawn this much oversize, shown smoothed
SIDE_LIFT = 0.004           # m a line is lifted off its own face
SIDE_DEPTH = 20.0           # m of depth kept either side of the work
_side_geo = {}


def _side_skip(obj):
    """Not part of the picture: cages, wire boxes, text, and what is
    left out of renders (cutters) other than the return wall stand-ins."""
    return (obj.get('IS_GEONODE_CAGE') or obj.type == 'FONT'
            or obj.display_type in ('WIRE', 'BOUNDS')
            or (obj.hide_render and not obj.get(STUB_TAG)))


def _side_geometry(scene, wall, items):
    """The wall and what stands on it as triangles and edge lines in
    the wall's frame, read once per change of the model: {'tris': n x 3
    array, 'lines': m x 3 array (pairs)}. The edges are where a surface
    folds or ends; with a depth buffer nothing else is needed to draw
    the wall from any side. Cages and selection aids are left out, so
    the pictures look the same in every mode."""
    import numpy as np
    key = (_gen, scene.name, wall.name)
    if _side_geo.get('key') == key:
        return _side_geo
    names = _print_owners(items, scene, molding=True) | {wall.name}
    names |= {o.name for o in scene.objects if o.get(STUB_TAG)}
    # Mouldings switched off are read apart: the iso alone draws them.
    left_out = _molding_left_out(scene)
    Fi = _frame(wall)[1]
    cos_feature = math.cos(PRINT_FEATURE_ANGLE)
    tris, wall_tris, lines = [], [], []
    more_tris, more_lines = [], []
    with _molding_shown(scene, bpy.context.view_layer):
        _side_read(bpy.context.evaluated_depsgraph_get(), wall, names,
                   left_out, Fi, cos_feature, tris, wall_tris, lines,
                   more_tris, more_lines)
    empty = np.zeros((0, 3), np.float32)
    lines = np.concatenate(lines) if lines else empty
    # The mitre where a return meets the wall is not a line of the room.
    try:
        seams = _return_seams(_return_boxes(wall, items)[0])
    except Exception:
        seams = []
    if seams and len(lines):
        a, b = lines[0::2], lines[1::2]
        keep = np.ones(len(a), dtype=bool)
        level = np.abs(a[:, 2] - b[:, 2]) < 0.002
        for (px0, py0), (px1, py1) in seams:
            dx, dy = px1 - px0, py1 - py0
            ln = math.hypot(dx, dy)
            if ln < 1e-6:
                continue
            on = np.ones(len(a), dtype=bool)
            for q in (a, b):
                t = ((q[:, 0] - px0) * dx + (q[:, 1] - py0) * dy) / ln
                off = np.abs((q[:, 0] - px0) * dy
                             - (q[:, 1] - py0) * dx) / ln
                on &= (off < 0.002) & (t > -0.002) & (t < ln + 0.002)
            keep &= ~(on & level)
        lines = np.stack((a[keep], b[keep]), axis=1).reshape(-1, 3)
    tris = np.concatenate(tris).astype(np.float32) if tris else empty
    lines = lines.astype(np.float32)
    all_tris, all_lines = tris, lines
    if more_tris:
        all_tris = np.concatenate([tris] + more_tris).astype(np.float32)
        all_lines = np.concatenate([lines] + more_lines).astype(np.float32)
    _side_geo.clear()
    _side_geo.update(
        key=key, tris=tris, all_tris=all_tris,
        wall_tris=(np.concatenate(wall_tris).astype(np.float32)
                   if wall_tris else empty),
        lines=lines, all_lines=all_lines, dropped=0)
    return _side_geo


def _side_read(dg, wall, names, left_out, Fi, cos_feature, tris, wall_tris,
               lines, more_tris, more_lines):
    import numpy as np
    for inst in dg.object_instances:
        owner = inst.parent if inst.is_instance else inst.object
        if owner is None or owner.original.name not in names:
            continue
        ob = inst.object
        is_wall = (owner.original == wall
                   or bool(owner.original.get(STUB_TAG)))
        if ob.type != 'MESH' or _side_skip(owner.original) \
                or (not inst.is_instance and _side_skip(ob.original)):
            continue
        try:
            mesh = ob.to_mesh()
        except Exception:
            continue
        try:
            nv, npoly, nl, ne = (len(mesh.vertices), len(mesh.polygons),
                                 len(mesh.loops), len(mesh.edges))
            if not npoly:
                continue
            M = np.array(Fi @ inst.matrix_world)
            co = np.empty(nv * 3)
            mesh.vertices.foreach_get('co', co)
            co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
            nrm = np.empty(npoly * 3)
            mesh.polygons.foreach_get('normal', nrm)
            nrm = nrm.reshape(-1, 3) @ np.linalg.inv(M[:3, :3])
            nrm /= np.maximum(np.linalg.norm(nrm, axis=1), 1e-12)[:, None]
            total = np.empty(npoly, dtype=np.int64)
            mesh.polygons.foreach_get('loop_total', total)
            le = np.empty(nl, dtype=np.int64)
            mesh.loops.foreach_get('edge_index', le)
            ev = np.empty(ne * 2, dtype=np.int64)
            mesh.edges.foreach_get('vertices', ev)
            ev = ev.reshape(-1, 2)
            mesh.calc_loop_triangles()
            tv = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
            mesh.loop_triangles.foreach_get('vertices', tv)
        finally:
            ob.to_mesh_clear()
        more = owner.original.name in left_out
        (wall_tris if is_wall else more_tris if more
         else tris).append(co[tv])
        # An edge is drawn where the surface folds past the feature
        # angle or stops (an open border, a seam).
        loop_poly = np.repeat(np.arange(npoly), total)
        count = np.bincount(le, minlength=ne)
        order = np.argsort(le, kind='stable')
        first_at = np.concatenate(([0], np.cumsum(count)[:-1]))
        feature = count != 2
        two = count == 2
        f0 = loop_poly[order[first_at[two]]]
        f1 = loop_poly[order[first_at[two] + 1]]
        feature[two] = (nrm[f0] * nrm[f1]).sum(axis=1) < cos_feature
        (more_lines if more else lines).append(
            co[ev[feature]].reshape(-1, 3))


def _side_draw(off, geo, F, C, span, size, line_px, wall_color=None,
               whole=False):
    """Draw the geometry into the offscreen from the camera C: paper
    faces and inked lines, depth tested. `whole` adds what the plan
    leaves out (mouldings switched off)."""
    geo_tris = geo['all_tris'] if whole else geo['tris']
    geo_lines = geo['all_lines'] if whole else geo['lines']
    l, r, b, t = span
    near, far = SIDE_DIST - SIDE_DEPTH, SIDE_DIST + SIDE_DEPTH
    proj = _ortho(l, r, b, t, near, far)
    # Lines sit a hair nearer than the faces they edge.
    lift = Matrix.Translation((0.0, 0.0, -2.0 * SIDE_LIFT / (far - near)))
    view = C.inverted_safe() @ F
    with off.bind():
        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(*PAPER, 1.0), depth=1.0)
        gpu.state.blend_set('NONE')
        gpu.state.depth_mask_set(True)
        gpu.state.depth_test_set('LESS_EQUAL')
        try:
            with gpu.matrix.push_pop(), gpu.matrix.push_pop_projection():
                gpu.matrix.load_matrix(view)
                gpu.matrix.load_projection_matrix(proj)
                for tris, color in ((geo['wall_tris'],
                                     wall_color or (*PAPER, 1.0)),
                                    (geo_tris, (*PAPER, 1.0))):
                    if not len(tris):
                        continue
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    shader.bind()
                    shader.uniform_float("color", color)
                    batch_for_shader(shader, 'TRIS',
                                     {"pos": tris}).draw(shader)
                if len(geo_lines):
                    gpu.matrix.load_projection_matrix(lift @ proj)
                    shader = gpu.shader.from_builtin(
                        'POLYLINE_UNIFORM_COLOR')
                    shader.bind()
                    shader.uniform_float("viewportSize", size)
                    shader.uniform_float("lineWidth", line_px)
                    shader.uniform_float("color", (*PRINT_EDGE, 1.0))
                    batch_for_shader(shader, 'LINES',
                                     {"pos": geo_lines}).draw(shader)
        finally:
            gpu.state.depth_test_set('NONE')
            gpu.state.depth_mask_set(False)


def _side_render():
    """Draw the side views that were asked for, as line drawings of the
    wall's own geometry."""
    import time
    _side_wanted.pop('queued', None)
    wanted = {k: v for k, v in _side_wanted.items() if k in ('PLAN', 'ISO')}
    _side_wanted.clear()
    if _state is None:
        return None
    scene = bpy.data.scenes.get(_state['scene'])
    wall = bpy.data.objects.get(_state['wall'])
    if scene is None or wall is None or _frame(wall) is None:
        return None
    try:
        geo = _side_geometry(scene, wall, _items(scene, wall))
    except Exception as exc:
        print(f"Elevation side views: {exc}")
        return None
    F = _frame(wall)[0]
    for kind, req in wanted.items():
        try:
            tw, th = req['size']
            ss = SIDE_SUPER if max(tw, th) * SIDE_SUPER <= SIDE_MAX_PX \
                else 1
            size = (tw * ss, th * ss)
            entry = _side_cache.get(kind)
            off = entry['off'] if entry is not None else None
            if off is None or entry.get('tex') != size:
                if off is not None:
                    off.free()
                off = gpu.types.GPUOffScreen(*size)
            # The plan cuts the walls: they read light grey.
            _side_draw(off, geo, F, req['C'], req['span'], size,
                       max(1.0, SIDE_LINE_PX * _s() * ss),
                       WALL_GRAY if kind == 'PLAN' else None,
                       whole=(kind == 'ISO'))
            _side_cache[kind] = {'off': off, 'key': req['key'],
                                 'size': req['size'], 'tex': size,
                                 'at': time.monotonic()}
            req['area'].tag_redraw()
        except Exception as exc:
            print(f"Elevation side view {kind}: {exc}")
    return None


_chrome_cache = {}
CHROME_REFRESH = 0.3        # s the HUD's outline is kept between reads
CHROME_JOIN_PX = 10         # HUD pieces this close count as one block


def _chrome_rects(context, area):
    """The HUD's blocks in this area as a few (x, y, w, h): the pinned
    panel, the selection inspector, the tool palette and the rows of
    buttons. The side views are pictures; they stay under these."""
    import time
    now = time.monotonic()
    key = (area.as_pointer(), area.width, area.height)
    if _chrome_cache.get('key') == key \
            and now - _chrome_cache.get('at', 0.0) < CHROME_REFRESH:
        return _chrome_cache['rects']
    rects = []
    try:
        from . import viewport_hud, room_palette, selection_inspector
        for fn in (viewport_hud.pinned_panel_rect, selection_inspector.rect):
            try:
                rects.append(fn(context, area))
            except Exception:
                pass
        try:
            rects += [r for _w, r in viewport_hud.compute_layout(context,
                                                                 area)]
        except Exception:
            pass
        try:
            if room_palette._palette_active(context):
                rects += [r for _k, _p, r in
                          room_palette.compute_layout(area)]
        except Exception:
            pass
    except Exception as exc:
        print("Elevation side views HUD:", exc)
    j = CHROME_JOIN_PX * _s()
    blocks = []
    for r in rects:
        if r is None or r[2] <= 0 or r[3] <= 0:
            continue
        cur = [r[0], r[1], r[0] + r[2], r[1] + r[3]]
        merged = True
        while merged:
            merged = False
            for other in blocks:
                if (cur[0] - j < other[2] and cur[2] + j > other[0]
                        and cur[1] - j < other[3] and cur[3] + j > other[1]):
                    cur = [min(cur[0], other[0]), min(cur[1], other[1]),
                           max(cur[2], other[2]), max(cur[3], other[3])]
                    blocks.remove(other)
                    merged = True
                    break
        blocks.append(cur)
    out = [(b[0], b[1], b[2] - b[0], b[3] - b[1]) for b in blocks]
    _chrome_cache.update(key=key, at=now, rects=out)
    return out


def _draw_side_views(context, area, region, dims, extra, s):
    wall = active_wall(context)
    if wall is None or extra is None:
        return
    rects = extra.get('side') or {}
    for kind in list(_side_cache):
        if kind not in rects:
            entry = _side_cache.pop(kind)
            try:
                entry['off'].free()
            except Exception:
                pass
    if not rects:
        return
    shader = gpu.shader.from_builtin('IMAGE')
    for kind, rect in rects.items():
        x, y, w, h = rect[:4]
        if w < 8 or h < 8:
            continue
        off = _side_texture(context, area, region, kind, rect)
        if off is None:
            continue
        gpu.state.blend_set('NONE')
        shader.bind()
        shader.uniform_sampler("image", off.texture_color)
        batch_for_shader(shader, 'TRI_FAN', {
            "pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1))}).draw(shader)
    gpu.state.blend_set('ALPHA')
    blf.size(0, ANNOTATION_FONT_SIZE * s)
    blf.color(0, *TEXT)
    for (tx, ty), text in extra.get('plan_notes', ()):
        tw, th = blf.dimensions(0, text)
        blf.position(0, tx - tw / 2.0, ty - th / 2.0, 0)
        draw_glyphs(0, text)


# ---- Detail cards --------------------------------------------------------------
# Another add-on can hand the elevation detail cards to stand beside the
# wall: small drawings of their own (a moulding section, a drawer seen
# from above). A source is fn(scene, wall) returning a list of cards:
#   {'id': str, 'title': str, 'size': (width, height), 'prims': [...],
#    'scale': 1.0 (a card to show larger or smaller than the rest)}
# with the primitives in the card's own flat units, origin bottom left:
#   {'kind': 'LINES', 'points': [(x, y), ...] (pairs), 'width': weight}
#   {'kind': 'TEXT', 'origin': (x, y), 'size': letter size, 'text': str
#    (or 'value': a length, written the way the view writes lengths),
#    'align': 'LEFT' | 'CENTER' | 'RIGHT',
#    'valign': 'TOP' | 'CENTER' | 'BOTTOM', 'angle': radians,
#    'mask': True to clear the card behind the text}
# A card is scaled whole to its place, letters and line weights with it.
# A source may come with stamp(scene, wall): anything that compares
# unequal once its cards have changed, for cards whose drawing can
# change without the room itself changing. A click on a card picks it
# (picked_card()), for whoever shows its settings; a drag moves it to
# another place in the stack, kept with the wall.

_card_sources = []
_card_stamps = {}
_card_cache = {}
CARDS_PROP = 'HB_ELEVATION_CARDS'

CARD_INK = (0.07, 0.07, 0.08, 1.0)
CARD_GAP_PX = 14            # between cards
CARD_ROWS = 3               # cards down the wall's height, on screen
CARD_WIDE = 1.5             # a card is at most this wide, of its height
CARD_PRINT_W = 2.6 * 72.0   # pt a card is wide on paper
CARD_PRINT_TALL = 1.3       # and at most this tall, of that width
CARD_MIN_LINE = 0.8         # px (pt) the lightest line is drawn
CARD_CAP = 0.70             # a capital's height, of the letter size
CARD_LEADING = 1.25


def register_card_source(fn, stamp=None):
    if fn not in _card_sources:
        _card_sources.append(fn)
    if stamp is not None:
        _card_stamps[fn] = stamp
    _bump_gen()


def unregister_card_source(fn):
    if fn in _card_sources:
        _card_sources.remove(fn)
    _card_stamps.pop(fn, None)
    _bump_gen()


def _cards_stamp(scene, wall):
    """What the sources say their cards look like now."""
    if not _card_stamps or scene is None or wall is None \
            or not show_option(scene, 'DETAILS'):
        return None
    out = []
    for fn in list(_card_sources):
        stamp = _card_stamps.get(fn)
        if stamp is None:
            continue
        try:
            out.append(stamp(scene, wall))
        except Exception:
            out.append(None)
    return tuple(out)


def _card_order(wall):
    try:
        order = json.loads(wall.get(CARDS_PROP) or '[]')
        return [str(i) for i in order] if isinstance(order, list) else []
    except Exception:
        return []


def picked_card(context=None):
    """The id of the detail card picked in the elevation on screen, or
    None."""
    if _card_pick is None or _state is None:
        return None
    context = context or bpy.context
    wall = active_wall(context)
    if wall is None or context.scene is None:
        return None
    if any(c.get('id') == _card_pick for c in _cards(context.scene, wall)):
        return _card_pick
    return None


def pick_card(card_id):
    global _card_pick
    _card_pick = card_id
    _redraw_views()


def _redraw_views():
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    except Exception:
        pass


def _cards(scene, wall):
    """The wall's detail cards, from every source; none with the Details
    toggle off."""
    if not _card_sources or scene is None \
            or not show_option(scene, 'DETAILS'):
        return []
    key = (_gen, scene.name, wall.name, len(_card_sources),
           _cards_stamp(scene, wall), wall.get(CARDS_PROP))
    if _card_cache.get('key') == key:
        return _card_cache['cards']
    cards = []
    for fn in list(_card_sources):
        try:
            for card in fn(scene, wall) or ():
                w, h = card.get('size', (0.0, 0.0))
                if w > 1e-6 and h > 1e-6:
                    cards.append(card)
        except Exception as exc:
            print(f"Elevation detail cards: {exc}")
    # The order the cards were dragged into; new ones after.
    order = {cid: i for i, cid in enumerate(_card_order(wall))}
    if order:
        cards = [c for _i, c in sorted(
            enumerate(cards),
            key=lambda ic: (order.get(str(ic[1].get('id')), len(order)),
                            ic[0]))]
    _card_cache['key'] = key
    _card_cache['cards'] = cards
    return cards


def _cards_flow(cards, wall_px, limit, s):
    """Cards flowed top to bottom into columns no taller than `limit`:
    ([(card, x from the first column's left, y down from the top,
    scale, w, h)], total width). On screen a card's height is a share of
    the wall's (`wall_px`), so the cards zoom with the drawing; on paper
    every card is the same width whatever the drawing's scale."""
    gap = CARD_GAP_PX * s
    out = []
    x = y = col_w = 0.0
    for card in cards:
        cw, ch = card['size']
        big = max(0.25, min(4.0, card.get('scale') or 1.0))
        if _print_scale is not None:
            wide = CARD_PRINT_W * big
            k = min(wide / cw, wide * CARD_PRINT_TALL / ch)
        else:
            slot = max(24.0, (wall_px - (CARD_ROWS - 1) * gap) / CARD_ROWS)
            slot *= big
            k = min(slot / ch, slot * CARD_WIDE / cw)
        w, h = cw * k, ch * k
        if y > 0.0 and y + h > limit + 0.5:
            x += col_w + gap
            y = col_w = 0.0
        out.append((card, x, y, k, w, h))
        y += h + gap
        col_w = max(col_w, w)
    return out, (x + col_w if out else 0.0)


def _card_text(scene, pr, ox, oy, k, wide):
    """[(x, y, row, size, angle)] baselines of a card's text, and the
    paper to clear behind it (or None). A level row too long for the
    card (`wide`) in the face it is set in is set smaller to fit."""
    if pr.get('value') is not None:
        text = format_length(scene, pr['value'])
    else:
        # Sizes written into a note follow the view's units too.
        text = _note_numbers(scene, str(pr.get('text') or ''))
    rows = text.splitlines()
    size = pr.get('size', 0.0) * k
    if not rows or size <= 0.0:
        return [], None
    ang = pr.get('angle', 0.0)
    ca, sa = math.cos(ang), math.sin(ang)
    align = pr.get('align', 'LEFT')
    px, py = ox + pr['origin'][0] * k, oy + pr['origin'][1] * k
    if abs(sa) < 1e-3:
        edge = size * 0.8
        room = {'LEFT': ox + wide - px, 'RIGHT': px - ox}.get(
            align, 2.0 * min(px - ox, ox + wide - px)) - edge
        longest = max(_blf_measure(row, size) for row in rows)
        if room > 0.0 and longest > room:
            size *= max(0.35, room / longest)
    cap = size * CARD_CAP
    lead = size * CARD_LEADING
    block = cap + lead * (len(rows) - 1)
    # The first row's baseline, down from the anchor.
    first = {'TOP': -cap, 'BOTTOM': block - cap}.get(
        pr.get('valign', 'BOTTOM'), block / 2.0 - cap)
    out = []
    widest = 0.0
    for i, row in enumerate(rows):
        tw = _blf_measure(row, size)
        widest = max(widest, tw)
        dx = {'LEFT': 0.0, 'RIGHT': -tw}.get(align, -tw / 2.0)
        dy = first - lead * i
        out.append((px + dx * ca - dy * sa, py + dx * sa + dy * ca, row,
                    size, ang))
    mask = None
    if pr.get('mask') and abs(sa) < 1e-3:
        pad = size * 0.18
        mx = px + {'LEFT': 0.0, 'RIGHT': -widest}.get(align, -widest / 2.0)
        mask = (mx - pad, py + first - lead * (len(rows) - 1) - pad,
                widest + 2 * pad, block + 2 * pad)
    return out, mask


def _layout_cards(scene, wall, region, dims, extra, s):
    """Place the wall's cards (extra['cards']) to the right of the
    elevation and everything that dimensions it, ready to draw:
    {'id', 'title', 'rect', 'lines': {width: [points]}, 'texts',
    'masks'} in the layout's own units."""
    extra['cards'] = []
    cards = _cards(scene, wall)
    if not cards:
        return
    _F, _Fi, length, height = _frame(wall)
    sx, sy = extra['sx'], extra['sy']
    _x0, bx1, _y0, _y1 = _print_bounds(dims, extra, 1.0, length, height)
    wall_px = abs(sy(height) - sy(0.0))
    top = sy(height)
    if _print_scale is not None:
        limit = region.height - 2 * PRINT_MARGIN - PRINT_TITLE
    else:
        limit = wall_px
    flow, _total = _cards_flow(cards, wall_px, limit, s)
    if _print_scale is not None:
        # On the page whatever the wall's place on it.
        tall = max(y + h for _c, _x, y, _k, _w, h in flow)
        top = max(top, PRINT_MARGIN + PRINT_TITLE + tall)
        top = min(top, region.height - PRINT_MARGIN)
    left = bx1 + SIDE_GAP_PX * s
    for card, cx, cy, k, w, h in flow:
        ox, oy = left + cx, top - cy - h
        lines = {}
        texts = []
        masks = []
        for pr in card.get('prims', ()):
            kind = pr.get('kind')
            if kind == 'LINES':
                width = max(CARD_MIN_LINE * s, pr.get('width', 0.0) * k)
                width = round(width * 4.0) / 4.0
                out = lines.setdefault(width, [])
                out += [(ox + p[0] * k, oy + p[1] * k)
                        for p in pr.get('points', ())]
            elif kind == 'TEXT':
                rows, mask = _card_text(scene, pr, ox, oy, k, w)
                texts += rows
                if mask is not None:
                    masks.append(mask)
        extra['cards'].append({'id': card.get('id'),
                               'title': card.get('title', ''),
                               'rect': (ox, oy, w, h), 'lines': lines,
                               'texts': texts, 'masks': masks})


def _cards_width(scene, wall, wall_px, limit, s):
    """Room the cards take to the right of the elevation, gap included."""
    cards = _cards(scene, wall)
    if not cards:
        return 0.0
    return _cards_flow(cards, wall_px, limit, s)[1] + SIDE_GAP_PX * s


def _draw_cards(region, extra, s):
    """The cards on screen: always ink on paper, whatever the shading."""
    cards = (extra or {}).get('cards') or ()
    if not cards:
        return
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    for card in cards:
        x, y, w, h = card['rect']
        shader.bind()
        draw_round_rect(shader, x, y, w, h, 0.0, (*PAPER, 1.0))
        for width, pts in card['lines'].items():
            hb_dim_style.polyline(region, pts, width, CARD_INK)
        for mx, my, mw, mh in card['masks']:
            shader.bind()
            draw_round_rect(shader, mx, my, mw, mh, 0.0, (*PAPER, 1.0))
        blf.color(0, *CARD_INK)
        blf.enable(0, blf.ROTATION)
        for tx, ty, text, size, ang in card['texts']:
            if size < 4.0:
                continue                # too small to be letters yet
            blf.size(0, size)
            blf.rotation(0, ang)
            blf.position(0, tx, ty, 0)
            draw_glyphs(0, text)
        blf.rotation(0, 0.0)
        blf.disable(0, blf.ROTATION)
    # The picked card, and one on its way to a new place.
    drag = _card_drag if _card_drag and _card_drag.get('moved') else None
    for card in cards:
        x, y, w, h = card['rect']
        ring = _rect_ring(x, y, w, h)
        if drag is not None and card['id'] == drag.get('over') \
                and card['id'] != drag['id']:
            hb_dim_style.polyline(region, ring, 3.0 * s, HOVER)
        elif card['id'] == _card_pick and drag is None:
            hb_dim_style.polyline(region, ring, 2.0 * s, HOVER)
    if drag is not None:
        for card in cards:
            if card['id'] == drag['id']:
                x, y, w, h = card['rect']
                dx, dy = drag['x'] - drag['mx'], drag['y'] - drag['my']
                shader.bind()
                draw_round_rect(shader, x + dx, y + dy, w, h, 0.0,
                                (HOVER[0], HOVER[1], HOVER[2], 0.12))
                hb_dim_style.polyline(region,
                                      _rect_ring(x + dx, y + dy, w, h),
                                      1.5 * s, HOVER)


def _rect_ring(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y), (x + w, y + h),
            (x + w, y + h), (x, y + h), (x, y + h), (x, y)]


def _card_at(extra, mx, my):
    """The placed card under the cursor, or None."""
    for card in (extra or {}).get('cards') or ():
        x, y, w, h = card['rect']
        if x <= mx <= x + w and y <= my <= y + h:
            return card
    return None


def _card_nearest(extra, mx, my):
    """The placed card a dragged one is dropped on: the one under the
    cursor, else the nearest."""
    cards = (extra or {}).get('cards') or ()
    hit = _card_at(extra, mx, my)
    if hit is not None or not cards:
        return hit

    def away(card):
        x, y, w, h = card['rect']
        return (mx - (x + w / 2.0)) ** 2 + (my - (y + h / 2.0)) ** 2
    return min(cards, key=away)


def _move_card(wall, extra, card_id, onto_id):
    """Put a card in another's place in the stack; the rest close up."""
    ids = [str(c['id']) for c in (extra or {}).get('cards') or ()]
    card_id, onto_id = str(card_id), str(onto_id)
    if card_id not in ids or onto_id not in ids or card_id == onto_id:
        return False
    to = ids.index(onto_id)
    ids.remove(card_id)
    ids.insert(to, card_id)
    wall[CARDS_PROP] = json.dumps(ids)
    _bump_gen()
    return True


def _print_cards(page, extra):
    for card in (extra or {}).get('cards') or ():
        x, y, w, h = card['rect']
        page.fill_color(PAPER)
        page.rect(x, y, w, h, fill=True, stroke=False)
        page.stroke_color(CARD_INK[:3])
        for width, pts in sorted(card['lines'].items()):
            page.line_width(width)
            page.lines(list(zip(pts[0::2], pts[1::2])))
        page.fill_color(PAPER)
        for mx, my, mw, mh in card['masks']:
            page.rect(mx, my, mw, mh, fill=True, stroke=False)
        page.fill_color(CARD_INK[:3])
        for tx, ty, text, size, ang in card['texts']:
            page.text(tx, ty, text, size, angle=ang)


# ---- Legend ------------------------------------------------------------------

LEGEND_TITLE = "LEGEND"
LEGEND_GAP_PX = 22          # under the lowest dimension


def _legend_lines(scene, wall):
    """The legend's lines for a wall, top to bottom; empty with no
    legend (or with the notes switched off)."""
    if not show_option(scene, 'ANNOTATIONS'):
        return []
    rows = []
    for pr in _annotations(scene, wall):
        if pr.get('kind') == 'LEGEND':
            rows += list(pr.get('rows') or ())
    lines = []
    for mark, text in rows:
        parts = _note_numbers(scene, str(text or '')).splitlines() or ['']
        lines.append(f"{mark}   {parts[0]}".rstrip())
        lines += ["       " + extra_line for extra_line in parts[1:]]
    return lines


def _legend_height(scene, wall, s):
    """Room the legend takes under the elevation, gap included."""
    lines = _legend_lines(scene, wall)
    if not lines:
        return 0.0
    size = ANNOTATION_FONT_SIZE * s
    return (len(lines) + 1) * size * 1.5 + 8 * s + LEGEND_GAP_PX * s


def _legend_box(scene, wall, dims, extra, s):
    """(x, y, w, h, [(text, x, baseline y, is title)]) of the legend:
    a box under the elevation's lowest dimension, from the wall's
    start. None with nothing to list."""
    lines = _legend_lines(scene, wall)
    if not lines or extra is None:
        return None
    size = ANNOTATION_FONT_SIZE * s
    lh = size * 1.5
    pad = 6 * s
    _F, _Fi, length, height = _frame(wall)
    _x0, _x1, by0, _y1 = _print_bounds(dims, extra, 1.0, length, height)
    texts = [LEGEND_TITLE] + lines
    w = max(_blf_measure(t, size) for t in texts) + 2 * pad
    h = len(texts) * lh + 8 * s
    x = extra['sx'](0.0)
    y = by0 - LEGEND_GAP_PX * s - h
    out = []
    for i, t in enumerate(texts):
        out.append((t, x + pad, y + h - 4 * s - (i + 1) * lh + lh * 0.3,
                    i == 0))
    return x, y, w, h, out


def _draw_legend(context, region, dims, extra, s):
    wall = active_wall(context)
    if wall is None:
        return
    box = _legend_box(context.scene, wall, dims, extra, s)
    if box is None:
        return
    x, y, w, h, texts = box
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    draw_round_rect(shader, x, y, w, h, 2 * s, (*PAPER, 0.92))
    ring = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    _stroke(region, [q for a, b in zip(ring, ring[1:] + ring[:1])
                     for q in (a, b)], 1.0 * s, ANNOTATION_LINE)
    blf.size(0, ANNOTATION_FONT_SIZE * s)
    for text, tx, ty, _title in texts:
        blf.color(0, *TEXT)
        blf.position(0, tx, ty, 0)
        draw_glyphs(0, text)


def _print_legend(page, scene, wall, dims, extra, ps):
    box = _legend_box(scene, wall, dims, extra, ps)
    if box is None:
        return
    x, y, w, h, texts = box
    page.stroke_color(ANNOTATION_LINE)
    page.line_width(0.75 * ps)
    page.fill_color(PAPER)
    page.rect(x, y, w, h, fill=True, stroke=True)
    page.fill_color(TEXT)
    for text, tx, ty, title in texts:
        page.text(tx, ty, text, ANNOTATION_FONT_SIZE * ps,
                  font=hb_pdf.BOLD if title else hb_pdf.REGULAR)


def _draw_adding(region, extra, s):
    """The height string being clicked in: the level under the cursor
    as a guide across the wall, and the levels picked so far."""
    sx, sy = extra['sx'], extra['sy']
    fx0, fx1, _fy = extra['floor']
    hot = _adding.get('hot')
    if hot is not None:
        _stroke(region, [(fx0 - 24 * s, sy(hot)), (fx1 + 24 * s, sy(hot))],
                1.5 * s, HOVER)
    levels = sorted(_adding['levels'])
    if not levels or _adding.get('x') is None:
        return
    x = sx(_adding['x'])
    t = TICK_PX * s
    pts = []
    for z in levels:
        pts += [(x - t, sy(z)), (x + t, sy(z))]
    if len(levels) > 1:
        pts += [(x, sy(levels[0])), (x, sy(levels[-1]))]
    _stroke(region, pts, 2.0 * s, HOVER)


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
    if _picture is not None:
        def page_paint():
            _draw_picture(context, area, region)
        try:
            from . import viewport_hud
            viewport_hud.paint_clear_of_panel(context, area, page_paint)
        except Exception:
            page_paint()
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
            if (_hover == ('DIM', d['key']) and d['target'] is not None) \
                    or (_hover_chain is not None
                        and d.get('chain') == _hover_chain):
                hot_lines += line
                hot_ticks += ticks
            else:
                normal_lines += line
                normal_ticks += ticks
        _stroke(region, normal_lines, 1.0 * s, LINE)
        _stroke(region, normal_ticks, TICK_WIDTH * s, LINE)
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
            _draw_noting(context, region, rv3d)
        except Exception as exc:
            print(f"Elevation annotations: {exc}")
        if _adding is not None and extra is not None:
            _draw_adding(region, extra, s)
        if _hover_chain is not None and _drag is None and _adding is None:
            _draw_remove_chip(dims, s)
        try:
            _draw_legend(context, region, dims, extra, s)
        except Exception as exc:
            print(f"Elevation legend: {exc}")
        _draw_bar(context, area)
        _draw_tabs(context, area)
        gpu.state.blend_set('NONE')

    ink = None
    try:
        ink = _ink_swap(area.spaces.active.shading.type
                        in {'MATERIAL', 'RENDERED'})
    except Exception:
        pass
    # The side views are pictures: they go down first, and never over
    # the HUD's panels, palette and button rows.
    try:
        if extra is not None and (extra.get('side') or extra.get('cards')):
            from ..hb_gpu_ui import paint_outside_rects

            def pictures():
                _draw_side_views(context, area, region, dims, extra, s)
                _draw_cards(region, extra, s)
            paint_outside_rects(_chrome_rects(context, area), pictures)
            gpu.state.blend_set('NONE')
    except Exception as exc:
        print(f"Elevation side views: {exc}")
    try:
        try:
            from . import viewport_hud
            viewport_hud.paint_clear_of_panel(context, area, paint)
        except Exception:
            paint()
    finally:
        _ink_restore(ink)


# ---- Print -----------------------------------------------------------------------

PRINT_PAPER = {'TABLOID': (17 * 72.0, 11 * 72.0),
               'LETTER': (11 * 72.0, 8.5 * 72.0)}
PRINT_MARGIN = 36.0         # pt round the drawing
PRINT_TITLE = 30.0          # pt strip along the bottom for the title
PRINT_TEXT_SCALE = 0.58     # screen px -> pt for text, tiers and strokes
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
                face_frame=None, measure=None):
    """The dimensions of `wall` laid out on a width x height sheet,
    whether or not an elevation is on screen: (dims, extra) as the view
    draws them, in sheet units with the origin bottom left.

    `view` is wall_view's, or anything with a `perspective_matrix` that
    takes world space to the sheet's -1..1 square. `scale` sizes the
    tiers, ticks and text (1.0 = the view's sizes in sheet units).
    `face_frame` overrides the scene's Face Frame toggle.
    `measure(text, size)` is the width of text in the face the caller
    will set the values in (the print's own face when None)."""
    global _print_scale, _print_measure
    saved = _print_scale, _print_measure
    _print_scale, _print_measure = scale, measure
    try:
        return _layout_wall(scene, wall, _PrintRegion(width, height), view,
                            extra=_front_names(scene, wall), preview=(),
                            face_frame=face_frame)
    finally:
        _print_scale, _print_measure = saved


def _print_layout(scene, wall, region, view, extra=None):
    dims, extra = _layout_wall(scene, wall, region, view, extra=extra,
                               side_views=True)
    return [d for d in dims if d['key'][0] != 'SEL'], extra


def _print_bounds(dims, extra, k, L, H):
    sx, sy = extra['sx'], extra['sy']
    xs = [sx(0.0), sx(L)]
    ys = [sy(0.0), sy(H)]
    for d in dims:
        if d['key'][0] == 'PLAN_D':
            continue                    # the plan's own: placed after
        x, y, w, h = d['rect']
        xs += [x, x + w]
        ys += [y, y + h]
        if d['axis'] == 'H':
            xs += [d['a'], d['b']]
            ys.append(d['pos'])
        else:
            ys += [d['a'], d['b']]
            xs.append(d['pos'])
    for a, b in extra['ext'][:extra.get('ext_n')]:
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
    # The legend hangs under the lowest dimension, at a fixed size.
    legend_h = _legend_height(scene, wall, _s())
    pad_b = extra['sy'](0.0) - y0 + legend_h
    extra_w = (x1 - x0) - k0 * L + _cards_width(scene, wall, 0.0, area_h,
                                                 _s())
    extra_h = (y1 - y0) - k0 * Hw + legend_h
    # Side views scale with the wall; the gap to them does not.
    more_w = more_h = gap_w = gap_h = iso_h = 0.0
    for kind, rect in (extra.get('side') or {}).items():
        l, r, b, t = rect[5]
        if kind == 'PLAN':
            more_h, gap_h = t - b, SIDE_GAP_PX * _s()
        else:
            more_w, gap_w, iso_h = r - l, SIDE_GAP_PX * _s(), t - b
    k = min((area_w - extra_w - gap_w) / (L + more_w),
            (area_h - extra_h - gap_h) / (Hw + more_h))
    if iso_h:
        k = min(k, area_h / iso_h)
    label = None
    for n, text in PRINT_SCALES:
        pt_per_m = 72.0 / 0.0254 / n
        if pt_per_m <= k:
            k, label = pt_per_m, f"{text} = 1'-0\""
            break
    # The iso to the left of the elevation, the plan above it.
    ox = (PRINT_MARGIN + pad_l + gap_w + k * more_w
          + (area_w - (k * (L + more_w) + extra_w + gap_w)) / 2.0)
    oy = (PRINT_MARGIN + PRINT_TITLE + pad_b
          + (area_h - (k * (Hw + more_h) + extra_h + gap_h)) / 2.0)
    return _print_view(Fi, k, ox, oy, W, H), label


# Line work: every face turned to the viewer, painted back to front in
# paper white, with the edges where the surface turns (a silhouette, a
# panel's edge, a profile's break) inked over it.
PRINT_FEATURE_ANGLE = math.radians(20.0)
PRINT_EDGE = (0.0, 0.0, 0.0)
# A part's outline (where it ends against what is behind it) is inked
# heavier than the breaks within its face (a panel's bevel, a profile).
PRINT_EDGE_WIDTH = 0.7
PRINT_DETAIL_WIDTH = 0.3


class _Edges(list):
    """A face's edges, the outlines first: the first `heavy` of them."""
    heavy = 0


def _ink_edges(page, edges):
    """Stroke a face's edges at their weights."""
    n = getattr(edges, 'heavy', len(edges))
    if n:
        page.line_width(PRINT_EDGE_WIDTH)
        page.lines(edges[:n])
    if n < len(edges):
        page.line_width(PRINT_DETAIL_WIDTH)
        page.lines(edges[n:])


def _print_owners(items, scene, molding=False):
    """Names of the objects whose geometry the drawing shows: the
    products and openings on the wall, and everything under them, less
    the mouldings when those are switched off (`molding` keeps them:
    the iso)."""
    names = set()
    for it in items:
        if it.preview:
            continue
        for obj in [it.obj] + list(it.obj.children_recursive):
            names.add(obj.name)
    if molding:
        return names
    return names - _molding_left_out(scene)


def _print_skip(obj):
    """Helpers that are not the product: cages, cutters, wire boxes,
    anything left out of renders, and text (lettered as a note)."""
    return (obj.get('IS_GEONODE_CAGE') or obj.hide_render
            or obj.type == 'FONT'
            or obj.display_type in ('WIRE', 'BOUNDS'))


def _print_faces(context, items, Fi, view, only=None, deep=False,
                 molding=False):
    """[(depth, polygon, edges)] in page points for every face of the
    wall's products that faces the viewer; depth grows into the wall.
    Parts hidden in the viewport (a cutaway, a part toggled off on
    screen) still print, as they do on the sheets: they are shown just
    long enough to be read. `only` narrows it to those object names."""
    if only is None:
        owners = _print_owners(items, context.scene, molding)
    else:
        owners = set(only)
        if not molding:
            owners -= _molding_left_out(context.scene)
    if not owners:
        return []
    shown = []
    layer = context.view_layer
    for name in owners:
        obj = bpy.data.objects.get(name)
        # A moulding run is a curve; one this view hid is read too.
        if obj is None or _print_skip(obj) or not (
                obj.type == 'MESH' or obj.get(MOLDING_HIDE_TAG)):
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
        return _print_faces_now(context, owners, Fi, view, deep)
    finally:
        for obj, hidden, off in shown:
            obj.hide_set(hidden, view_layer=layer)
            obj.hide_viewport = off
        if shown:
            layer.update()


def _print_faces_now(context, owners, Fi, view, deep=False):
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
        detail = np.zeros(ne, dtype=bool)
        detail[two] = fold & ~sil
        px = co[:, 0] * k + ox
        py = co[:, 2] * k + oy
        for f in np.nonzero(facing)[0]:
            s0, n = start[f], total[f]
            vs = lv[s0:s0 + n]
            poly = list(zip(px[vs].tolist(), py[vs].tolist()))
            if deep:
                # With each corner's depth, for a depth-tested drawing.
                poly = [(x, y, d) for (x, y), d
                        in zip(poly, co[vs, 1].tolist())]
            edges, light = _Edges(), []
            for e in le[s0:s0 + n]:
                if feature[e]:
                    i, j = ev[e]
                    if deep:
                        seg = ((px[i], py[i], co[i, 1]),
                               (px[j], py[j], co[j, 1]))
                    else:
                        seg = ((px[i], py[i]), (px[j], py[j]))
                    (light if detail[e] else edges).append(seg)
            edges.heavy = len(edges)
            edges += light
            faces.append((float(co[vs, 1].mean()), poly, edges))
    return faces


INTERIOR_MARKERS = ('IS_FACE_FRAME_INTERIOR_PART',
                    'IS_FRAMELESS_INTERIOR_PART')
INTERIOR_LINE = (0.16, 0.16, 0.20, 0.95)
INTERIOR_DASH_PX = (5.0, 3.5)       # drawn, skipped
PRINT_INTERIOR_WIDTH = 0.35
INTERIOR_REFRESH = 0.6              # s between reads while editing
_interior_cache = {}


@hb_utils.with_children_index
def _interior_names(items):
    """Names of the objects that stand inside the wall's cabinets: the
    interior parts and everything under them."""
    names = set()

    def walk(obj, inside):
        inside = (inside or any(obj.get(m) for m in INTERIOR_MARKERS)
                  or hb_utils.is_hidden_interior_part(obj))
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
    for _depth, poly, edges in faces:
        page.polygon(poly, fill=True, stroke=False)
        if edges:
            _ink_edges(page, edges)
    return True


# Camera space (x right, y up, the camera looking down -z) to the print's
# frame (x right, z up, y growing away from the viewer).
_CAMERA_TO_PRINT = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0),
                           (0, 0, 0, 1)))


class _SidePrintView:
    def __init__(self, k, ox, oy):
        self.k, self.ox, self.oy = k, ox, oy


def _box_faces(M, box, view, deep=False):
    """A box in the wall's frame as _print_faces gives a mesh: its faces
    turned to the viewer. `M` takes the wall's frame to the print's."""
    pts = [M @ Vector(c) for c in _box_corners(box)]
    k, ox, oy = view.k, view.ox, view.oy
    faces = []
    for quad in _BOX_FACES:
        if quad == _SEAM_FACE:
            continue                    # the mitre: inside the corner
        a, b, c = pts[quad[0]], pts[quad[1]], pts[quad[2]]
        if (b - a).cross(c - a).y >= -1e-9:
            continue                    # turned away
        if deep:
            poly = [(pts[i].x * k + ox, pts[i].z * k + oy, pts[i].y)
                    for i in quad]
        else:
            poly = [(pts[i].x * k + ox, pts[i].z * k + oy) for i in quad]
        ring = list(zip(quad, quad[1:] + quad[:1]))
        edges = [(poly[n], poly[(n + 1) % len(poly)])
                 for n, (i, j) in enumerate(ring)
                 if not (i in _SEAM_CORNERS and j in _SEAM_CORNERS
                         and abs(i - j) != 4)]
        faces.append((sum(pts[i].y for i in quad) / 4.0, poly, edges))
    return faces


def _drop_seam_edges(faces, M, view, boxes):
    """Take the edges that lie along a return's mitre (top or bottom)
    out of faces in page points: the wall's own mitred end draws one."""
    k, ox, oy = view.k, view.ox, view.oy
    seams = []
    for box in boxes:
        (ax, ay), (bx, by) = box[0][2], box[0][3]
        for z in (box[1], box[2]):
            p = M @ Vector((ax, ay, z))
            q = M @ Vector((bx, by, z))
            seams.append(((p.x * k + ox, p.z * k + oy),
                          (q.x * k + ox, q.z * k + oy)))
    if not seams:
        return faces

    def on(pt, seam):
        (x0, y0), (x1, y1) = seam
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        if ln < 1e-6:
            return False
        t = ((pt[0] - x0) * dx + (pt[1] - y0) * dy) / ln
        off = abs((pt[0] - x0) * dy - (pt[1] - y0) * dx) / ln
        return off < 0.4 and -0.4 <= t <= ln + 0.4

    out = []
    for face in faces:
        edges = [e for e in face[2]
                 if math.hypot(e[0][0] - e[1][0], e[0][1] - e[1][1]) < 0.3
                 or not any(on(e[0], sm) and on(e[1], sm) for sm in seams)]
        out.append((face[0], face[1], edges) + tuple(face[3:]))
    return out


PRINT_RASTER_DPI = 300
PRINT_RASTER_MAX = 8192
PRINT_RASTER_LIFT = 0.004       # m an edge is lifted off its own face


def _raster_faces(faces, x, y, w, h):
    """(rgb bytes top row first, px wide, px high) of depth-carrying
    faces drawn with a depth buffer: white faces, inked edges, each
    hidden exactly where something stands in front of it. None when
    there is no GPU to draw with (background mode)."""
    if bpy.app.background or not faces or w < 1 or h < 1:
        return None
    import numpy as np
    ss = 2                              # drawn double size, then averaged
    scale = PRINT_RASTER_DPI / 72.0
    scale = min(scale, PRINT_RASTER_MAX / (ss * max(w, h)))
    tw = max(1, int(math.ceil(w * scale))) * ss
    th = max(1, int(math.ceil(h * scale))) * ss
    depths = [q[2] for _d, poly, _e in faces for q in poly]
    d0, d1 = min(depths), max(depths)

    def z(d, lift=0.0):
        return -(d - d0 + 1.0 - lift)

    tris, lines = [], []
    for _depth, poly, edges in faces:
        pts = [(q[0], q[1], z(q[2])) for q in poly]
        for i in range(1, len(pts) - 1):
            tris += [pts[0], pts[i], pts[i + 1]]
        for a, b in edges:
            lines += [(a[0], a[1], z(a[2], PRINT_RASTER_LIFT)),
                      (b[0], b[1], z(b[2], PRINT_RASTER_LIFT))]
    off = gpu.types.GPUOffScreen(tw, th)
    try:
        with off.bind():
            fb = gpu.state.active_framebuffer_get()
            fb.clear(color=(1.0, 1.0, 1.0, 1.0), depth=1.0)
            gpu.state.blend_set('NONE')
            gpu.state.depth_mask_set(True)
            gpu.state.depth_test_set('LESS_EQUAL')
            try:
                with gpu.matrix.push_pop(), gpu.matrix.push_pop_projection():
                    gpu.matrix.load_identity()
                    gpu.matrix.load_projection_matrix(
                        _ortho(x, x + w, y, y + h, 0.5, (d1 - d0) + 2.0))
                    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
                    shader.bind()
                    shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
                    batch_for_shader(shader, 'TRIS',
                                     {"pos": tris}).draw(shader)
                    if lines:
                        shader = gpu.shader.from_builtin(
                            'POLYLINE_UNIFORM_COLOR')
                        shader.bind()
                        shader.uniform_float("viewportSize", (tw, th))
                        shader.uniform_float(
                            "lineWidth",
                            max(1.5, PRINT_EDGE_WIDTH * scale * ss))
                        shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
                        batch_for_shader(shader, 'LINES',
                                         {"pos": lines}).draw(shader)
            finally:
                gpu.state.depth_test_set('NONE')
                gpu.state.depth_mask_set(False)
            buf = fb.read_color(0, 0, tw, th, 4, 0, 'UBYTE')
    finally:
        off.free()
    buf.dimensions = tw * th * 4
    try:
        arr = np.frombuffer(buf, dtype=np.uint8)
    except Exception:
        arr = np.array(buf, dtype=np.uint8)
    arr = arr.reshape(th, tw, 4)[::-1, :, :3].astype(np.float32)
    arr = arr.reshape(th // ss, ss, tw // ss, ss, 3).mean(axis=(1, 3))
    return arr.astype(np.uint8).tobytes(), tw // ss, th // ss


def _print_side_views(page, context, wall, extra):
    """The plan and iso that are switched on, in the places the layout
    gave them. The plan is line work. The iso is drawn with a depth
    buffer and set as a picture, so every part hides what is behind it;
    with no GPU (background mode) it falls back to line work painted
    far to near, which mis-orders some faces at that angle."""
    rects = extra.get('side') or {}
    if not rects:
        return
    plan_names = _print_owners(extra['items'], context.scene)
    iso_names = _print_owners(extra['items'], context.scene, molding=True)
    F = _frame(wall)[0]
    returns, _from_left = _return_boxes(wall, extra['items'])
    sx = extra['sx']
    k = abs(sx(1.0) - sx(0.0))
    for kind, (x, y, w, h, C, (l, _r, b, _t)) in rects.items():
        Fi = _CAMERA_TO_PRINT @ C.inverted_safe()
        view = _SidePrintView(k, x - l * k, y - b * k)
        M = Fi @ F
        iso = kind == 'ISO'
        names = iso_names if iso else plan_names
        if iso:
            try:
                faces = _print_faces(context, extra['items'], Fi, view,
                                     only=names | {wall.name}, deep=True,
                                     molding=True)
                faces = _drop_seam_edges(faces, M, view, returns)
                for rb in returns:
                    faces += _box_faces(M, rb, view, deep=True)
                got = _raster_faces(faces, x, y, w, h)
            except Exception as exc:
                print(f"Elevation print: iso picture: {exc}")
                got = None
            if got is not None:
                rgb, pw, ph = got
                page.image(rgb, pw, ph, x, y, w, h)
                continue
        page.fill_color(PAPER)
        page.stroke_color(PRINT_EDGE)
        page.line_width(PRINT_EDGE_WIDTH)
        # The walls go down first: everything shown stands in front of
        # them, and their faces are too big to sort among the products'.
        back = _print_faces(context, extra['items'], Fi, view,
                            only={wall.name})
        back = _drop_seam_edges(back, M, view, returns)
        for rb in returns:
            back += _box_faces(M, rb, view)
        front = _print_faces(context, extra['items'], Fi, view,
                             only=names, molding=iso) if names else []
        for faces in (back, front):
            # The plan cuts the walls: they read light grey.
            page.fill_color(WALL_GRAY if faces is back and kind == 'PLAN'
                            else PAPER)
            faces.sort(key=lambda f: -f[0])        # far first
            for _depth, poly, edges in faces:
                page.polygon(poly, fill=True, stroke=False)
                if edges:
                    _ink_edges(page, edges)
    # The plan names its wall, in the wall.
    size = ANNOTATION_FONT_SIZE * _s()
    page.fill_color(TEXT)
    for (tx, ty), text in extra.get('plan_notes', ()):
        tw = hb_pdf.text_width(text, size)
        page.text(tx - tw / 2.0, ty - size * 0.35, text, size)


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
                  'width': TICK_WIDTH * ps, 'segments': ticks})
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
            # One ink on paper: which values can be typed over is the
            # screen's to show.
            'color': TEXT,
            'halo': halo, 'rect': (x, y, w, h), 'key': d.get('key')})
        if d.get('tag_rect'):
            gx, gy, gw, gh = d['tag_rect']
            size = fs * TAG_SCALE
            gtw = hb_pdf.text_width(d['tag'], size)
            gx += (gw - gtw) / 2.0
            prims.append({
                'kind': 'TEXT', 'role': 'TAG', 'text': d['tag'], 'x': gx,
                'y': gy, 'size': size, 'angle': 0.0, 'font': 'Helvetica',
                'runs': [(d['tag'], 0.0, 0.0, size)], 'color': TEXT,
                'halo': halo, 'rect': (gx, gy, gtw, gh),
                'key': d.get('key')})
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
    if not show_option(scene, 'ANNOTATIONS'):
        return
    prims = _annotations(scene, wall)

    def P(v):
        return view3d_utils.location_3d_to_region_2d(region, view, v)

    page.line_width(0.5 * ps)
    for pr in prims:
        if pr.get('kind') != 'FILL':
            continue
        pts = [P(v) for v in pr.get('points', ())]
        if len(pts) < 3 or any(p is None for p in pts):
            continue
        page.fill_color(pr.get('color', NOTE_FILL))
        page.stroke_color(ANNOTATION_LINE)
        ring = [(p.x, p.y) for p in pts]
        page.polygon(ring, fill=True, stroke=False)
        page.lines(list(zip(ring, ring[1:] + ring[:1])))
    page.line_width(1.0 * ps)
    for pr in prims:
        if pr.get('kind') != 'LINES':
            continue
        pts = [P(v) for v in pr.get('points', ())]
        segs = [((a.x, a.y), (b.x, b.y)) for a, b in zip(pts[0::2], pts[1::2])
                if a is not None and b is not None]
        page.stroke_color(pr.get('color', ANNOTATION_LINE))
        page.lines(segs)
    for color, tri in _arrow_heads(prims, P, ps):
        page.fill_color(color)
        page.polygon(tri, fill=True, stroke=False)
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
            dy = total / 2.0 - lh * (i + 1) + (lh - th) / 2.0 \
                + _note_lift(pr, total)
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
    if wall is None:
        wall = active_wall(context)
        if wall is None:
            raise RuntimeError("No wall is shown in elevation")
    W, H = PRINT_PAPER.get(paper, PRINT_PAPER['TABLOID'])
    doc = hb_pdf.Document()
    draw_wall(doc.add_page(W, H), context, wall, W, H, text_scale)
    return _print_save(doc, filepath)


def draw_wall(page, context, wall, W, H, text_scale=PRINT_TEXT_SCALE,
              title=True):
    """Draw a wall's printed page onto `page`, W x H points with its
    origin bottom left: anything with hb_pdf.Page's drawing methods, so
    another add-on can set the drawing into a sheet of its own (inside
    its title block, among its other pages). `title` False leaves the
    strip along the bottom empty for the caller's. Returns the drafting
    scale's label ("1/2\" = 1'-0\""), or None when the wall had to be
    fitted off scale."""
    global _print_scale
    scene = context.scene
    front = None            # the elevation on screen knows its own
    if wall != active_wall(context):
        front = _front_names(scene, wall)
    if _frame(wall) is None:
        raise RuntimeError("The wall has no elevation to print")
    _F, Fi, L, Hw = _frame(wall)
    region = _PrintRegion(W, H)
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
        try:
            _print_side_views(page, context, wall, extra)
        except Exception as exc:
            print(f"Elevation print: side views: {exc}")
        _print_dims(page, scene, dims, extra, text_scale)
        try:
            _print_cards(page, extra)
        except Exception as exc:
            print(f"Elevation print: detail cards: {exc}")
        try:
            _print_legend(page, scene, wall, dims, extra, text_scale)
        except Exception as exc:
            print(f"Elevation print: legend: {exc}")
        try:
            _print_annotations(page, scene, wall, region, view, text_scale)
        except Exception as exc:
            print(f"Elevation print: notes: {exc}")
    finally:
        _print_scale = None
    if title:
        _print_title(page, scene, wall, label, W)
    return label


# Another add-on may take over the bar's Print PDF (to print its own
# sheet set round the wall): fn(context, filepath, wall) returning the
# path it wrote, or None to leave this print to the view.
_print_handlers = []


def register_print_handler(fn):
    if fn not in _print_handlers:
        _print_handlers.append(fn)


def unregister_print_handler(fn):
    if fn in _print_handlers:
        _print_handlers.remove(fn)


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
            done = None
            for fn in list(_print_handlers):
                done = fn(context, path, active_wall(context))
                if done:
                    break
            path = done or print_wall(context, path, self.paper,
                                      self.text_scale)
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
    for page, rect, _label in _tabs_layout(context, context.area):
        if point_in_rect(mx, my, rect):
            return ('TAB', page)
    if _picture is not None:
        return None                     # a picture: nothing under it
    dims, extra = _layout(context, context.region, context.region_data)
    p = 4 * _s()
    for d in dims:
        x, y, w, h = d['rect']
        if x - p <= mx <= x + w + p and y - p <= my <= y + h + p:
            return ('DIM', d)
    for index, (x, y, w, h) in (extra or {}).get('notes', ()):
        if x - p <= mx <= x + w + p and y - p <= my <= y + h + p:
            return ('NOTE', index)
    return None


NOTE_TIP_PX = 8


def _note_tip_at(context, mx, my):
    """Index of the typed note whose leader's tip is at a region point."""
    _dims, extra = _layout(context, context.region, context.region_data)
    r = NOTE_TIP_PX * _s()
    for index, (x, y) in (extra or {}).get('note_tips', ()):
        if abs(mx - x) <= r and abs(my - y) <= r:
            return index
    return None


def _wall_point(context, mx, my):
    """(m along the wall, m off the floor) under a region point."""
    _dims, extra = _layout(context, context.region, context.region_data)
    if extra is None:
        return None
    sx, sy = extra['sx'], extra['sy']
    px, pz = sx(1.0) - sx(0.0), sy(1.0) - sy(0.0)
    if abs(px) < 1e-9 or abs(pz) < 1e-9:
        return None
    return (mx - sx(0.0)) / px, (my - sy(0.0)) / pz


REMOVE_CHIP_PX = 18


def _remove_chip(dims, chain, s):
    """(x, y, w, h) of the remove button a pointed-at height string
    shows just above its top end, or None."""
    own = [d for d in dims if d.get('chain') == chain]
    if chain is None or not own:
        return None
    top = max(max(d['a'], d['b']) for d in own)
    size = REMOVE_CHIP_PX * s
    return (own[0]['pos'] - size / 2.0, top + 6 * s, size, size)


def _on_remove_chip(context, mx, my):
    """True over the remove button of the string under the cursor."""
    if _hover_chain is None:
        return False
    dims, _extra = _layout(context, context.region, context.region_data)
    rect = _remove_chip(dims, _hover_chain, _s())
    p = 3 * _s()
    return rect is not None and (rect[0] - p <= mx <= rect[0] + rect[2] + p
                                 and rect[1] - p <= my
                                 <= rect[1] + rect[3] + p)


def _remove_chain(wall, chain):
    """Take a height string off the wall: one that was clicked in is
    deleted, one the rules place is hidden."""
    data = _heights(wall)
    if chain[0] == 'USER':
        if not 0 <= chain[1] < len(data['added']):
            return False
        del data['added'][chain[1]]
    else:
        cid = _chain_id(chain)
        data['moved'].pop(cid, None)
        if cid not in data['hidden']:
            data['hidden'].append(cid)
    _set_heights(wall, data)
    return True


def _hit_chain(context, mx, my, got=None):
    """The height string at a region point: one of its values, its
    line, or the remove button it is showing. None off every string."""
    if _on_remove_chip(context, mx, my):
        return _hover_chain
    if got is not None and got[0] == 'DIM':
        return got[1].get('chain')
    if got is not None:
        return None
    dims, _extra = _layout(context, context.region, context.region_data)
    p = 6 * _s()
    for d in dims:
        if d.get('chain') is None:
            continue
        lo, hi = min(d['a'], d['b']), max(d['a'], d['b'])
        if abs(mx - d['pos']) <= p and lo - p <= my <= hi + p:
            return d['chain']
    return None


def _chain_place(wall, chain):
    """Where a string stands, in the unit it is stored in."""
    data = _heights(wall)
    if chain[0] == 'USER':
        try:
            return float(data['added'][chain[1]].get('x', 0.0))
        except (IndexError, TypeError, ValueError):
            return None
    try:
        return float(data['moved'].get(_chain_id(chain), 0.0))
    except (TypeError, ValueError):
        return 0.0


def _chain_put(wall, chain, value):
    data = _heights(wall)
    if chain[0] == 'USER':
        if not 0 <= chain[1] < len(data['added']):
            return
        data['added'][chain[1]]['x'] = round(value, 5)
    elif abs(value) < 0.5:
        data['moved'].pop(_chain_id(chain), None)
    else:
        data['moved'][_chain_id(chain)] = round(value, 2)
    _set_heights(wall, data)


def _level_candidates(context, wall, x):
    """Heights off the floor a clicked-in string can catch: the floor,
    the wall's top, and the tops, bottoms, kicks and rail lines of the
    products at `x` along the wall (of every product when none stands
    there)."""
    fr = _frame(wall)
    if fr is None:
        return []
    _F, Fi, _length, height = fr
    items = [it for it in _items(context.scene, wall) if not it.preview]
    here = [it for it in items if it.x0 - MERGE <= x <= it.x1 + MERGE]
    use = here or items
    levels = {0.0, height}
    names = set()
    for it in use:
        levels.update((max(it.z0, 0.0), it.z1))
        names.add(it.name)
        k = _kick_height(it)
        if k:
            levels.add(k)
    try:
        with hb_utils.children_index():
            cols = _face_frame_layout(items, Fi)['columns']
        for it, c0, c1, zs in cols:
            if it.name in names and (not here
                                     or c0 - MERGE <= x <= c1 + MERGE):
                levels.update(zs)
    except Exception:
        pass
    return sorted(levels)


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
    """Show the project's drawings: a tab for every page that prints,
    starting on a wall seen face-on and dimensioned. Products you place
    land on the wall shown, until you exit (Esc)"""
    bl_idname = "home_builder.show_elevation"
    bl_label = "Show Drawings"
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
    """Leave the drawings and go back to the room view"""
    bl_idname = "home_builder.exit_elevation"
    bl_label = "Exit Drawings"
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


class home_builder_OT_elevation_pan(bpy.types.Operator):
    """Drag with the middle mouse button to slide the elevation. The
    view stays square to the wall, so there is nothing to orbit"""
    bl_idname = "home_builder.elevation_pan"
    bl_label = "Pan Elevation"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        # Only in the elevation's own view: elsewhere the middle button
        # keeps its usual job.
        return (_state is not None and is_active(context)
                and context.region is not None
                and context.region.type == 'WINDOW'
                and context.region_data is not None
                and context.region_data.as_pointer() == _state['r3d'])

    def invoke(self, context, event):
        try:
            # Blender's own pan takes the drag from here.
            bpy.ops.view3d.move('INVOKE_DEFAULT')
        except Exception:
            return {'PASS_THROUGH'}
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
        global _hover_chain
        got = _hit(context, *_mouse)
        key = None
        if got is not None and got[0] == 'TAB':
            key = ('TAB', got[1]['key'])
        elif got is not None:
            key = (got[0], got[1]) if got[0] in ('BAR', 'NOTE') else (
                ('DIM', got[1]['key']) if got[1]['target'] is not None
                else None)
        chain = None
        if _drag is None and _adding is None and _edit is None \
                and _noting is None and _note_drag is None \
                and _picture is None:
            chain = _hit_chain(context, *_mouse, got=got)
        if chain != _hover_chain:
            # A string that can be dragged shows the sideways cursor.
            try:
                context.window.cursor_set(
                    'MOVE_X' if chain is not None else 'DEFAULT')
            except Exception:
                pass
            _hover_chain = chain
            context.area.tag_redraw()
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
        global _drag, _hover_chain, _note_drag
        if _drag is not None or _adding is not None \
                or _noting is not None or _note_drag is not None:
            return {'PASS_THROUGH'}
        got = _hit(context, mx, my)
        if got is not None and got[0] == 'TAB':
            if got[1]['key'] != current_page_key(context) \
                    or got[1].get('kind') == 'PICTURE':
                if not show_page(context, got[1]):
                    self.report({'WARNING'}, "That page could not be shown")
            if context.area is not None:
                context.area.tag_redraw()
            return {'FINISHED'}
        if _picture is not None and got is None:
            return {'FINISHED'}         # a picture page takes the click
        if got is None or got[0] == 'NOTE':
            # A typed note: drag it (or its leader's tip) to move it, a
            # plain click retypes it.
            wall = active_wall(context)
            tip = _note_tip_at(context, mx, my)
            index = tip if tip is not None else (got[1] if got else None)
            notes = _user_notes(wall) if wall is not None else []
            if index is not None and 0 <= index < len(notes):
                _note_drag = {'index': index, 'mx': mx, 'my': my,
                              'part': 'TIP' if tip is not None else 'TEXT',
                              'was': dict(notes[index]), 'moved': False}
                bpy.ops.home_builder.elevation_drag_note('INVOKE_DEFAULT')
                return {'FINISHED'}
        if _on_remove_chip(context, mx, my):
            wall = active_wall(context)
            if wall is not None and _remove_chain(wall, _hover_chain):
                _hover_chain = None
                try:
                    context.window.cursor_set('DEFAULT')
                    bpy.ops.ed.undo_push(message="Remove Height Dimensions")
                except Exception:
                    pass
                context.area.tag_redraw()
            return {'FINISHED'}
        chain = _hit_chain(context, mx, my, got=got)
        if chain is not None:
            # A press on a height string: drag moves it sideways, a
            # plain click on an editable value still edits it.
            wall = active_wall(context)
            start = _chain_place(wall, chain) if wall is not None else None
            if start is not None and chain[0] == 'BAY'                     and _chain_id(chain) not in _heights(wall)['moved']:
                dims, _extra = _layout(context, context.region,
                                       context.region_data)
                start = next((d['auto'] for d in dims
                              if d.get('chain') == chain and 'auto' in d),
                             start)
            if start is not None:
                _drag = {'chain': chain, 'mx': mx, 'start': start,
                         'moved': False,
                         'dim': got[1] if got is not None else None}
                bpy.ops.home_builder.elevation_drag_height('INVOKE_DEFAULT')
                return {'FINISHED'}
        global _card_drag, _card_pick
        if got is None:
            try:
                _dims, extra = _layout(context, context.region,
                                       context.region_data)
                card = _card_at(extra, mx, my)
            except Exception:
                card = None
            wall = active_wall(context)
            if card is None and wall is not None and _iso_at(extra, mx, my):
                # The iso, seen from the other side.
                wall[ISO_LEFT_PROP] = 0 if _side_box(
                    wall, extra['items'])[6] else 1
                _bump_gen()
                try:
                    bpy.ops.ed.undo_push(message="Turn Iso View")
                except Exception:
                    pass
                context.area.tag_redraw()
                return {'FINISHED'}
            if card is not None:
                _card_drag = {'id': card['id'], 'mx': mx, 'my': my,
                              'x': mx, 'y': my, 'moved': False,
                              'over': None}
                bpy.ops.home_builder.elevation_drag_card('INVOKE_DEFAULT')
                return {'FINISHED'}
            if _card_pick is not None:
                _card_pick = None
                context.area.tag_redraw()
            return {'PASS_THROUGH'}
        if got[0] == 'BAR':
            if got[1] == 'EXIT':
                leave(context)
            elif got[1] == 'ADD_V':
                bpy.ops.home_builder.elevation_add_height('INVOKE_DEFAULT')
            elif got[1] == 'ADD_N':
                bpy.ops.home_builder.elevation_add_note('INVOKE_DEFAULT')
            elif got[1] == 'RESET_V':
                wall = active_wall(context)
                if wall is not None:
                    data = _heights(wall)
                    data['moved'], data['hidden'] = {}, []
                    _set_heights(wall, data)
                    try:
                        bpy.ops.ed.undo_push(message="Reset Heights")
                    except Exception:
                        pass
            elif got[1].startswith('SHOW:'):
                toggle_show_option(context.scene, got[1][5:])
                if got[1][5:] in ('PLAN', 'ISO', 'DETAILS') \
                        and _state is not None:
                    _state['fit'] = 3       # make room for it, or close up
            elif got[1] == 'MODE':
                scene = context.scene
                set_room_mode(scene, 'FULL' if room_mode(scene) == 'COMPACT'
                              else 'COMPACT')
                if _state is not None:
                    _state['fit'] = 3
                try:
                    bpy.ops.ed.undo_push(message="Drawings Mode")
                except Exception:
                    pass
            elif got[1] == 'SWAP':
                if not swap_page(context):
                    self.report({'WARNING'}, "That page could not be shown")
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


class home_builder_OT_elevation_drag_height(bpy.types.Operator):
    """Drag a height string sideways to where it reads best. The move is
    kept with the wall. Esc or right-click puts it back"""
    bl_idname = "home_builder.elevation_drag_height"
    bl_label = "Move Height Dimensions"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        if _drag is None:
            return {'CANCELLED'}
        _drag['owner'] = id(self)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context):
        global _drag
        _drag = None
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        if _drag is None or _drag.get('owner') != id(self):
            return {'CANCELLED'}
        wall = active_wall(context)
        if wall is None:
            self._end(context)
            return {'CANCELLED'}
        chain = _drag['chain']
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            dx = event.mouse_region_x - _drag['mx']
            s = _s()
            if not _drag['moved'] and abs(dx) < 4 * s:
                return {'RUNNING_MODAL'}
            _drag['moved'] = True
            if chain[0] == 'USER':
                _dims, extra = _layout(context, context.region,
                                       context.region_data)
                if extra is None:
                    return {'RUNNING_MODAL'}
                per_m = extra['sx'](1.0) - extra['sx'](0.0)
                if abs(per_m) < 1e-9:
                    return {'RUNNING_MODAL'}
                value = _drag['start'] + dx / per_m
            else:
                value = _drag['start'] + dx / max(s, 1e-6)
            _chain_put(wall, chain, value)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            moved, d = _drag['moved'], _drag.get('dim')
            self._end(context)
            if moved:
                return {'FINISHED'}
            if d is not None and d.get('target') is not None:
                bpy.ops.home_builder.elevation_edit_dim('INVOKE_DEFAULT')
                _edit_begin(d)
            return {'CANCELLED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if _drag['moved']:
                _chain_put(wall, chain, _drag['start'])
            self._end(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class home_builder_OT_elevation_drag_card(bpy.types.Operator):
    """Click a detail card to pick it; drag it onto another to move it
    there in the stack. The order is kept with the wall"""
    bl_idname = "home_builder.elevation_drag_card"
    bl_label = "Move Detail Card"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        if _card_drag is None:
            return {'CANCELLED'}
        _card_drag['owner'] = id(self)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context):
        global _card_drag
        _card_drag = None
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        global _card_pick
        drag = _card_drag
        if drag is None or drag.get('owner') != id(self):
            return {'CANCELLED'}
        wall = active_wall(context)
        if wall is None:
            self._end(context)
            return {'CANCELLED'}
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            drag['x'], drag['y'] = event.mouse_region_x, event.mouse_region_y
            far = max(abs(drag['x'] - drag['mx']), abs(drag['y'] - drag['my']))
            if not drag['moved'] and far < 5 * _s():
                return {'RUNNING_MODAL'}
            drag['moved'] = True
            _dims, extra = _layout(context, context.region,
                                   context.region_data)
            over = _card_nearest(extra, drag['x'], drag['y'])
            drag['over'] = over['id'] if over is not None else None
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            moved, card_id, over = drag['moved'], drag['id'], drag['over']
            self._end(context)
            if not moved:
                # A plain click picks the card, and only the card.
                for obj in list(context.selected_objects):
                    try:
                        obj.select_set(False)
                    except Exception:
                        pass
                try:
                    context.view_layer.objects.active = None
                except Exception:
                    pass
                _card_pick = card_id
                _redraw_views()
                return {'CANCELLED'}
            _dims, extra = _layout(context, context.region,
                                   context.region_data)
            if over is not None and _move_card(wall, extra, card_id, over):
                return {'FINISHED'}
            return {'CANCELLED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class home_builder_OT_elevation_reset_height(bpy.types.Operator):
    """Remove the height string under the cursor. Reset Heights on the
    bar brings back the ones the rules place"""
    bl_idname = "home_builder.elevation_reset_height"
    bl_label = "Remove Height Dimensions"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (is_active(context)
                and (_hover_chain is not None
                     or (_hover is not None and _hover[0] == 'NOTE'))
                and _edit is None and _drag is None and _adding is None
                and _noting is None and _note_drag is None)

    def execute(self, context):
        global _hover_chain, _hover
        wall = active_wall(context)
        if wall is not None and _hover is not None and _hover[0] == 'NOTE':
            # The typed note under the cursor.
            notes = _user_notes(wall)
            if not 0 <= _hover[1] < len(notes):
                return {'CANCELLED'}
            del notes[_hover[1]]
            _set_user_notes(wall, notes)
            _hover = None
            context.area.tag_redraw()
            return {'FINISHED'}
        chain = _hover_chain
        if wall is None or chain is None:
            return {'CANCELLED'}
        if not _remove_chain(wall, chain):
            return {'CANCELLED'}
        _hover_chain = None
        context.area.tag_redraw()
        return {'FINISHED'}


ADD_SNAP_PX = 14


class home_builder_OT_elevation_add_height(bpy.types.Operator):
    """Click the levels to dimension, bottom to top or in any order. The
    string stands where you first click. Enter or right-click finishes,
    Esc cancels"""
    bl_idname = "home_builder.elevation_add_height"
    bl_label = "Add Height Dimensions"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_active(context) and _edit is None and _adding is None

    def invoke(self, context, event):
        global _adding
        _adding = {'x': None, 'levels': [], 'hot': None, 'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        try:
            context.window.cursor_set('CROSSHAIR')
            context.workspace.status_text_set(
                "Add height dimensions: click each level  |  Enter or "
                "right-click to finish  |  Backspace removes the last  |  "
                "Esc to cancel")
        except Exception:
            pass
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _end(self, context):
        global _adding
        _adding = None
        try:
            context.window.cursor_set('DEFAULT')
            context.workspace.status_text_set(None)
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def _snap(self, context, wall, mx, my):
        """(x along the wall, level) under the cursor; level None when
        nothing is near enough to catch."""
        _dims, extra = _layout(context, context.region, context.region_data)
        if extra is None:
            return None, None
        sx, sy = extra['sx'], extra['sy']
        per_m = sx(1.0) - sx(0.0)
        if abs(per_m) < 1e-9:
            return None, None
        x = (mx - sx(0.0)) / per_m
        best, best_d = None, ADD_SNAP_PX * _s()
        for z in _level_candidates(context, wall, x):
            d = abs(sy(z) - my)
            if d < best_d:
                best, best_d = z, d
        return x, best

    def modal(self, context, event):
        if _adding is None or _adding.get('owner') != id(self):
            return {'CANCELLED'}
        wall = active_wall(context)
        if wall is None or context.region is None \
                or context.region_data is None:
            self._end(context)
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'TRACKPADPAN', 'TRACKPADZOOM', 'TIMER'}:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            _x, z = self._snap(context, wall, mx, my)
            if z != _adding['hot']:
                _adding['hot'] = z
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE':
            x, z = self._snap(context, wall, mx, my)
            if z is None:
                return {'RUNNING_MODAL'}
            if _adding['x'] is None:
                _adding['x'] = x
            if all(abs(z - o) > MERGE for o in _adding['levels']):
                _adding['levels'].append(z)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'BACK_SPACE':
            if _adding['levels']:
                _adding['levels'].pop()
                if not _adding['levels']:
                    _adding['x'] = None
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'RET', 'NUMPAD_ENTER', 'RIGHTMOUSE'}:
            levels, x = sorted(_adding['levels']), _adding['x']
            self._end(context)
            if len(levels) < 2 or x is None:
                return {'CANCELLED'}
            data = _heights(wall)
            data['added'].append({'x': round(x, 5),
                                  'levels': [round(z, 5) for z in levels]})
            _set_heights(wall, data)
            return {'FINISHED'}
        if event.type == 'ESC':
            self._end(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


NOTE_DRAG_PX = 6


class home_builder_OT_elevation_add_note(bpy.types.Operator):
    """Click where a note goes, or drag from what it points at to set it
    with a leader. Type it, then Enter. Tab turns it up the wall,
    Shift+Enter starts a new line, Esc cancels"""
    bl_idname = "home_builder.elevation_add_note"
    bl_label = "Add Note"
    bl_options = {'INTERNAL', 'UNDO'}

    index: bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return (is_active(context) and _edit is None and _adding is None
                and _noting is None)

    def invoke(self, context, event):
        global _noting
        wall = active_wall(context)
        if wall is None:
            return {'CANCELLED'}
        if not show_option(context.scene, 'ANNOTATIONS'):
            toggle_show_option(context.scene, 'ANNOTATIONS')
        notes = _user_notes(wall)
        if 0 <= self.index < len(notes):
            u = notes[self.index]
            _noting = {'stage': 'TYPE', 'index': self.index, 'x': u['x'],
                       'z': u['z'], 'tip': u['tip'], 'turn': u['turn'],
                       'typed': u['text'], 'press': None, 'owner': id(self)}
        else:
            _noting = {'stage': 'PLACE', 'index': None, 'x': None, 'z': None,
                       'tip': None, 'turn': 0, 'typed': "", 'press': None,
                       'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        self._prompt(context)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _prompt(self, context):
        try:
            if _noting['stage'] == 'PLACE':
                context.window.cursor_set('CROSSHAIR')
                context.workspace.status_text_set(
                    "Add note: click where it goes, or drag from what it "
                    "points at for a leader  |  Esc to cancel")
            else:
                context.window.cursor_set('TEXT')
                context.workspace.status_text_set(
                    "Type the note  |  Enter to finish  |  Shift+Enter new "
                    "line  |  Tab turns it  |  Del removes it  |  Esc to "
                    "cancel")
        except Exception:
            pass

    def _end(self, context):
        global _noting
        _noting = None
        try:
            context.window.cursor_set('DEFAULT')
            context.workspace.status_text_set(None)
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def _commit(self, context, wall, remove=False):
        n = _noting
        text = "" if remove else n['typed'].strip()
        index = n['index']
        note = {'x': round(n['x'], 5), 'z': round(n['z'], 5), 'text': text,
                'turn': n['turn'],
                'tip': [round(v, 5) for v in n['tip']] if n['tip'] else None}
        self._end(context)
        notes = _user_notes(wall)
        if index is not None and 0 <= index < len(notes):
            if text:
                notes[index] = note
            else:
                del notes[index]        # typed away to nothing
        elif text:
            notes.append(note)
        else:
            return {'CANCELLED'}
        _set_user_notes(wall, notes)
        return {'FINISHED'}

    def modal(self, context, event):
        n = _noting
        if n is None or n.get('owner') != id(self):
            return {'CANCELLED'}
        wall = active_wall(context)
        if wall is None or context.region is None \
                or context.region_data is None:
            self._end(context)
            return {'CANCELLED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'TRACKPADPAN', 'TRACKPADZOOM', 'TIMER'}:
            return {'PASS_THROUGH'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        if n['stage'] == 'PLACE':
            if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
                press = n['press']
                if press is not None:
                    far = max(abs(mx - press[0]), abs(my - press[1]))
                    if far >= NOTE_DRAG_PX * _s():
                        # Dragged out: the press is the leader's tip.
                        at = _wall_point(context, mx, my)
                        if at is not None:
                            n['tip'] = list(press[2])
                            n['x'], n['z'] = at
                            context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                at = _wall_point(context, mx, my)
                if at is not None:
                    n['press'] = (mx, my, at)
                    n['x'], n['z'] = at
                return {'RUNNING_MODAL'}
            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE' \
                    and n['press'] is not None:
                n['stage'], n['press'] = 'TYPE', None
                self._prompt(context)
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
                self._end(context)
                return {'CANCELLED'}
            return {'RUNNING_MODAL'}
        # Typing.
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            return {'RUNNING_MODAL'}
        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            if event.shift or event.ctrl:
                n['typed'] += "\n"
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            return self._commit(context, wall)
        if event.type == 'LEFTMOUSE':
            return self._commit(context, wall)      # a click away keeps it
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'DEL':
            return self._commit(context, wall, remove=True)
        if event.type == 'BACK_SPACE':
            n['typed'] = n['typed'][:-1]
        elif event.type == 'TAB':
            n['turn'] = {0: 1, 1: -1}.get(n['turn'], 0)
        elif event.type == 'V' and (event.ctrl or event.oskey):
            try:
                n['typed'] += context.window_manager.clipboard or ""
            except Exception:
                pass
        else:
            ch = event.unicode
            if ch and ch.isprintable() and not (event.ctrl or event.oskey):
                n['typed'] += ch
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


class home_builder_OT_elevation_drag_note(bpy.types.Operator):
    """Drag a typed note, or the tip of its leader, to a new place. A
    plain click retypes it. Esc or right-click puts it back"""
    bl_idname = "home_builder.elevation_drag_note"
    bl_label = "Move Note"
    bl_options = {'INTERNAL', 'UNDO'}

    def invoke(self, context, event):
        if _note_drag is None:
            return {'CANCELLED'}
        _note_drag['owner'] = id(self)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _end(self, context):
        global _note_drag
        _note_drag = None
        if context.area:
            context.area.tag_redraw()

    def _put(self, wall, note):
        notes = _user_notes(wall)
        if 0 <= _note_drag['index'] < len(notes):
            notes[_note_drag['index']] = note
            _set_user_notes(wall, notes)

    def modal(self, context, event):
        drag = _note_drag
        if drag is None or drag.get('owner') != id(self):
            return {'CANCELLED'}
        wall = active_wall(context)
        if wall is None:
            self._end(context)
            return {'CANCELLED'}
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            mx, my = event.mouse_region_x, event.mouse_region_y
            far = max(abs(mx - drag['mx']), abs(my - drag['my']))
            if not drag['moved'] and far < NOTE_DRAG_PX * _s():
                return {'RUNNING_MODAL'}
            drag['moved'] = True
            a = _wall_point(context, drag['mx'], drag['my'])
            b = _wall_point(context, mx, my)
            if a is None or b is None:
                return {'RUNNING_MODAL'}
            dx, dz = b[0] - a[0], b[1] - a[1]
            note = dict(drag['was'])
            if drag['part'] == 'TIP' and note.get('tip'):
                note['tip'] = [round(note['tip'][0] + dx, 5),
                               round(note['tip'][1] + dz, 5)]
            else:
                note['x'] = round(note['x'] + dx, 5)
                note['z'] = round(note['z'] + dz, 5)
            self._put(wall, note)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            moved, index = drag['moved'], drag['index']
            self._end(context)
            if moved:
                return {'FINISHED'}
            bpy.ops.home_builder.elevation_add_note('INVOKE_DEFAULT',
                                                    index=index)
            return {'CANCELLED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if drag['moved']:
                self._put(wall, dict(drag['was']))
            self._end(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


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


def _glyph_plan(shader, rect, color):
    """A wall seen from above with a cabinet run in front of it."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.56, rh * 0.44
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    t = h * 0.22
    draw_lines(shader, [(x0, y1), (x1, y1), (x0, y1 - t), (x1, y1 - t),
                        (x0, y1), (x0, y1 - t), (x1, y1), (x1, y1 - t),
                        (x0, y1 - t), (x0, y0), (x0, y0), (x0 + w * 0.7, y0),
                        (x0 + w * 0.7, y0), (x0 + w * 0.7, y1 - t)], color)


def _glyph_iso(shader, rect, color):
    """A box seen from a corner."""
    rx, ry, rw, rh = rect
    cx, cy = rx + rw / 2.0, ry + rh / 2.0
    a = min(rw, rh) * 0.24
    top, mid, bot = cy + a, cy + a * 0.45, cy - a
    low = cy - a * 0.45
    pts = [(cx, top), (cx + a, mid), (cx + a, mid), (cx, cy - a * 0.1),
           (cx, cy - a * 0.1), (cx - a, mid), (cx - a, mid), (cx, top),
           (cx - a, mid), (cx - a, low), (cx - a, low), (cx, bot),
           (cx, bot), (cx + a, low), (cx + a, low), (cx + a, mid),
           (cx, cy - a * 0.1), (cx, bot)]
    draw_lines(shader, pts, color)


def _glyph_details(shader, rect, color):
    """A card with a moulding section on it."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.50, rh * 0.50
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    a, b = x0 + w * 0.28, x0 + w * 0.72
    c, d = y0 + h * 0.28, y0 + h * 0.72
    draw_lines(shader, [(x0, y0), (x1, y0), (x1, y0), (x1, y1),
                        (x1, y1), (x0, y1), (x0, y1), (x0, y0),
                        (a, d), (b, d), (a, d), (a, c),
                        (a, c), (b, d)], color)


def _glyph_molding(shader, rect, color):
    """A crown's section: flat top and back, a cove between."""
    rx, ry, rw, rh = rect
    a = min(rw, rh) * 0.46
    x0 = rx + (rw - a) / 2.0
    y0 = ry + (rh - a) / 2.0
    x1, y1 = x0 + a, y0 + a
    lip = a * 0.2
    r = a - lip
    pts = [(x1, y1 - lip)]
    for i in range(1, 7):
        t = math.radians(90.0 * i / 6.0)
        pts.append((x1 - r * math.sin(t), y1 - lip - r + r * math.cos(t)))
    pts += [(x0, y0), (x0, y1), (x1, y1), (x1, y1 - lip)]
    lines = []
    for p, q in zip(pts, pts[1:]):
        lines += [p, q]
    draw_lines(shader, lines, color)


def _glyph_decimal(shader, rect, color):
    """A decimal value, lettered."""
    rx, ry, rw, rh = rect
    text = ".00"
    blf.size(0, rh * 0.42)
    tw = blf.dimensions(0, text)[0]
    th = blf.dimensions(0, "0")[1]
    blf.color(0, *color)
    blf.position(0, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0, 0)
    draw_glyphs(0, text)
    shader.bind()


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
    'DECIMAL': _glyph_decimal,
    'PLAN': _glyph_plan,
    'ISO': _glyph_iso,
    'MOLDING': _glyph_molding,
    'DETAILS': _glyph_details,
}


def _hud_visible(context):
    scene = context.scene
    return (scene is not None and _room_scene(context)
            and any(o.get('IS_WALL_BP') for o in scene.objects))


def _register_hud():
    try:
        from . import viewport_hud
        viewport_hud.register_mode_glyph_toggle(
            'hb_elevation', 'hb_elevation_mode', "Show Drawings",
            "Exit Drawings", glyph=icon_glyph('elevation', _glyph_elevation),
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
    home_builder_OT_elevation_pan,
    home_builder_OT_elevation_hover,
    home_builder_OT_elevation_click,
    home_builder_OT_elevation_edit_dim,
    home_builder_OT_elevation_drag_height,
    home_builder_OT_elevation_drag_card,
    home_builder_OT_elevation_reset_height,
    home_builder_OT_elevation_add_height,
    home_builder_OT_elevation_add_note,
    home_builder_OT_elevation_drag_note,
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
            (home_builder_OT_elevation_pan.bl_idname, 'MIDDLEMOUSE', 'PRESS',
             {'head': True}),
            (home_builder_OT_elevation_reset_height.bl_idname, 'X', 'PRESS',
             {'head': True}),
            (home_builder_OT_elevation_reset_height.bl_idname, 'DEL', 'PRESS',
             {'head': True}),
            (home_builder_OT_elevation_frame.bl_idname, 'HOME', 'PRESS',
             {'head': True})):
        kmi = km.keymap_items.new(idname, key, value, **kw)
        _addon_keymaps.append((km, kmi))
    km_obj = kc.keymaps.new(name='Object Mode', space_type='EMPTY')
    for key in ('X', 'DEL'):
        kmi = km_obj.keymap_items.new(
            home_builder_OT_elevation_reset_height.bl_idname, key, 'PRESS',
            head=True)
        _addon_keymaps.append((km_obj, kmi))
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
