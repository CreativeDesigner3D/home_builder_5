"""Viewport glass hatch on glass-panel doors in solid view.

A glass door whose frame profile matches its neighbours reads the same
as a wood-panel door in solid shading: the glass material only shows in
material / rendered view. The drawings mark glass with a 45-degree
corner hatch -- three '/' lines in the panel's top-left and bottom-right
corners -- so a POST_VIEW draw handler paints that same hatch on the
front face of every glass lite in the 3D view.

A door counts when assign_style_to_front stamped IS_PREP_FOR_GLASS (a
glass panel style) or HB_GLASS_CELLS (per-row glass lites). The lite
rectangles come from the door's own bounds and frame widths, in the
front convention: local X runs up the door, -Y across from its left
edge, +Z out of the front face.

The door list and each door's local hatch segments are cached: a scene
walk runs only after a depsgraph update. Each redraw just transforms the
cached segments by the door's current matrix.
"""

import bpy
import gpu
from bpy.app.handlers import persistent
from mathutils import Vector

# ---- Style -------------------------------------------------------------

LINE_COLOR = (0.08, 0.08, 0.08, 1.0)
LINE_WIDTH = 1.5
# Hatch layout, matching the drawings' glass hatch.
HATCH_LINE_LEN = 0.05715       # 2-1/4" nominal line length
HATCH_SPACING = 0.01651        # between lines
HATCH_CORNER_OFFSET = 0.01905  # in from the panel corner
HATCH_LEN_MULT = (0.7, 1.0, 0.75)
# Lift off the front face so the lines win the depth test.
FACE_LIFT = 0.0005

# Fallback frame widths when a door carries neither a frame stamp nor a
# door-style modifier.
_DEFAULT_STILE = 0.0635
_DEFAULT_RAIL = 0.0762

_FRAME_STAMP_KEYS = {
    'Left Stile Width': 'left_stile',
    'Right Stile Width': 'right_stile',
    'Top Rail Width': 'top_rail',
    'Bottom Rail Width': 'bottom_rail',
}
# The 5-piece door node draws its Left / Right stile inputs on the
# opposite visual sides from their names.
_MOD_SOCKET_SWAP = {
    'Left Stile Width': 'Right Stile Width',
    'Right Stile Width': 'Left Stile Width',
}

# ---- Module state -------------------------------------------------------

_draw_handle = None
_shutdown = False
_dirty = True
# [(door object name, [local Vector, ...] as segment pairs)]
_cache = []
_cache_scene = None


def invalidate():
    """Drop the cached door list and redraw the 3D views."""
    global _dirty
    _dirty = True
    wm = getattr(bpy.context, 'window_manager', None)
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


@persistent
def _on_depsgraph_update(scene, depsgraph):
    global _dirty
    _dirty = True


@persistent
def _on_load_post(*_args):
    global _dirty, _cache_scene
    _dirty = True
    _cache_scene = None


# ---- Geometry -------------------------------------------------------------

def _frame_width(door, name, default):
    """A door frame width by visual side: the HB_DOOR_FRAME stamp on
    python-built doors, else the 'Door Style' modifier socket."""
    frame = door.get('HB_DOOR_FRAME')
    if frame is not None:
        val = frame.get(_FRAME_STAMP_KEYS[name])
        if val is not None:
            return val
    socket = _MOD_SOCKET_SWAP.get(name, name)
    for mod in door.modifiers:
        if mod.type != 'NODES' or not mod.node_group:
            continue
        if 'Door Style' not in mod.name:
            continue
        for item in mod.node_group.interface.items_tree:
            if (getattr(item, 'item_type', '') == 'SOCKET'
                    and item.name == socket):
                try:
                    return mod[item.identifier]
                except KeyError:
                    return default
        break
    return default


def _door_lites(door, width, height):
    """(u, v, w, h) glass lites in door-face coords (u across from the
    left edge, v up from the bottom)."""
    flat = door.get('HB_GLASS_CELLS')
    if flat:
        vals = list(flat)
        return [tuple(vals[i:i + 4]) for i in range(0, len(vals) - 3, 4)]
    left = _frame_width(door, 'Left Stile Width', _DEFAULT_STILE)
    right = _frame_width(door, 'Right Stile Width', _DEFAULT_STILE)
    top = _frame_width(door, 'Top Rail Width', _DEFAULT_RAIL)
    bottom = _frame_width(door, 'Bottom Rail Width', _DEFAULT_RAIL)
    return [(left, bottom, width - left - right, height - top - bottom)]


def _hatch_uv(w, h):
    """The drawings' corner hatch inside a w x h lite, as (u, v) pairs."""
    line_len = min(HATCH_LINE_LEN, min(w, h) * 0.45)
    out = []
    for i in range(3):
        ln = line_len * HATCH_LEN_MULT[i]
        # top-left corner
        su = ln + HATCH_CORNER_OFFSET + i * HATCH_SPACING
        sv = h - HATCH_CORNER_OFFSET - i * HATCH_SPACING
        out.append(((su, sv), (su - ln, sv - ln)))
        # bottom-right corner
        su = w - HATCH_CORNER_OFFSET - i * HATCH_SPACING
        sv = ln + HATCH_CORNER_OFFSET + i * HATCH_SPACING
        out.append(((su, sv), (su - ln, sv - ln)))
    return out


def _door_segments(door):
    """Local-space hatch line endpoints for a glass door, flat pairs."""
    bb = door.bound_box
    x0 = min(c[0] for c in bb)
    x1 = max(c[0] for c in bb)
    y0 = min(c[1] for c in bb)
    y1 = max(c[1] for c in bb)
    z_front = max(c[2] for c in bb) + FACE_LIFT
    height = x1 - x0
    width = y1 - y0
    if height <= 0.0 or width <= 0.0:
        return []
    pts = []
    for lu, lv, lw, lh in _door_lites(door, width, height):
        if lw <= 0.0 or lh <= 0.0:
            continue
        for (au, av), (bu, bv) in _hatch_uv(lw, lh):
            for u, v in ((lu + au, lv + av), (lu + bu, lv + bv)):
                pts.append(Vector((x0 + v, y1 - u, z_front)))
    return pts


def _rebuild(scene):
    global _dirty, _cache, _cache_scene
    out = []
    for obj in scene.objects:
        if obj.get('hb_part_role') != 'DOOR':
            continue
        if not (obj.get('IS_PREP_FOR_GLASS') or obj.get('HB_GLASS_CELLS')):
            continue
        pts = _door_segments(obj)
        if pts:
            out.append((obj.name, pts))
    _cache = out
    _cache_scene = scene.name
    _dirty = False


# ---- Gating -------------------------------------------------------------

def _should_draw(context):
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    space = context.space_data
    shading = getattr(space, 'shading', None)
    if shading is None or shading.type != 'SOLID':
        return False
    overlay = getattr(space, 'overlay', None)
    if overlay is not None and not overlay.show_overlays:
        return False
    return True


# ---- Draw handler ---------------------------------------------------------

def _draw():
    """Permanent POST_VIEW callback; a no-op outside solid shading."""
    if _shutdown:
        return
    context = bpy.context
    area = context.area
    region = context.region
    if area is None or area.type != 'VIEW_3D':
        return
    if region is None or region.type != 'WINDOW':
        return
    if not _should_draw(context):
        return
    scene = context.scene
    if _dirty or _cache_scene != scene.name:
        _rebuild(scene)
    if not _cache:
        return
    view_layer = context.view_layer
    coords = []
    for name, pts in _cache:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        try:
            if not obj.visible_get(view_layer=view_layer):
                continue
        except RuntimeError:
            continue
        mw = obj.matrix_world
        coords.extend(mw @ p for p in pts)
    if not coords:
        return

    from gpu_extras.batch import batch_for_shader
    s = 1.0
    try:
        s = context.preferences.system.ui_scale
    except AttributeError:
        pass
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float('viewportSize', (region.width, region.height))
    shader.uniform_float('lineWidth', LINE_WIDTH * s)
    shader.uniform_float('color', LINE_COLOR)
    batch_for_shader(shader, 'LINES', {'pos': coords}).draw(shader)
    gpu.state.blend_set('NONE')
    gpu.state.depth_test_set('NONE')


def register():
    global _draw_handle, _shutdown, _dirty
    _shutdown = False
    _dirty = True
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_VIEW')
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)


def unregister():
    global _draw_handle, _shutdown, _cache
    _shutdown = True
    _cache = []
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
