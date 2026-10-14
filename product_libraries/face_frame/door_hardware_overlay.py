"""Viewport letter marks for doors carrying hardware callouts.

Set Door Hardware (and the style editor's hardware brush) stamps
restrictor clips / touch latches / finger rout on individual doors, and
the 2D drawings letter those doors RC / TL / FR. Nothing in the model
said which doors were stamped, so a POST_PIXEL draw handler paints the
same letter codes over the centre of each stamped door in the 3D view.

The rule is the drawings' rule: only the per-door stamps count (read
through props_hb_face_frame.front_door_hw, which also honours the
opening-wide stamps of older files). The door style's checkboxes only
declare the option for the job, so they mark nothing here either.

The stamped-door list is cached: a scene walk runs only after a
depsgraph update or an explicit invalidate() from the operators that
write the stamps (custom-property writes don't always reach the
depsgraph). Each redraw only projects the cached doors.
"""

import bpy
import blf
import gpu
from bpy.app.handlers import persistent
from bpy_extras import view3d_utils
from mathutils import Vector

# ---- Style -------------------------------------------------------------

FONT_SIZE    = 11
PAD_X        = 4
PAD_Y        = 3
LABEL_BG     = (0.98, 0.97, 0.90, 0.92)
LABEL_BORDER = (0.10, 0.10, 0.10, 0.85)
TEXT_COLOR   = (0.08, 0.08, 0.08, 1.0)

# ---- Module state -------------------------------------------------------

_draw_handle = None
_shutdown = False
_dirty = True
# [(door object name, 'RC/TL')] for the scene last walked.
_cache = []
_cache_scene = None


def invalidate():
    """Drop the cached door list and redraw the 3D views. Called by the
    operators that write hardware stamps."""
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


def _codes_for(front, store):
    from . import props_hb_face_frame as _props
    hw = _props.front_door_hw(front, store)
    return "/".join(code for code, _key in _props.DOOR_HW_KEYS if hw[code])


def _rebuild(scene):
    """Walk the scene's opening cages that carry a hardware stamp and
    collect the doors under them that resolve to at least one code."""
    global _dirty, _cache, _cache_scene
    from . import props_hb_face_frame as _props
    prefix = _props.DOOR_HW_SET_KEY
    out = []
    for opening in scene.objects:
        if not opening.get('IS_FACE_FRAME_OPENING_CAGE'):
            continue
        if not any(k.startswith(prefix) for k in opening.keys()):
            continue
        for obj in opening.children_recursive:
            if obj.get('hb_part_role') != 'DOOR':
                continue
            codes = _codes_for(obj, opening)
            if codes:
                out.append((obj.name, codes))
    _cache = out
    _cache_scene = scene.name
    _dirty = False


# ---- Gating -------------------------------------------------------------

def _should_draw(context):
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    hb = getattr(scene, 'home_builder', None)
    if getattr(hb, 'product_tab', '') != 'FACE FRAME':
        return False
    space = context.space_data
    overlay = getattr(space, 'overlay', None)
    if overlay is not None and not overlay.show_overlays:
        return False
    return True


# ---- Draw handler ---------------------------------------------------------

def _door_centre(obj):
    """World-space centre of the door's evaluated bounds."""
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return sum(corners, Vector()) / 8.0


def _draw_rect(shader, rect):
    from gpu_extras.batch import batch_for_shader
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    shader.uniform_float("color", LABEL_BG)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def _draw():
    """Permanent POST_PIXEL callback; a no-op off the face frame tab."""
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
    rv3d = context.region_data
    view_layer = context.view_layer

    s = 1.0
    try:
        s = context.preferences.system.ui_scale
    except AttributeError:
        pass
    font_sz = FONT_SIZE * s
    blf.size(0, font_sz)

    labels = []
    for name, codes in _cache:
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        try:
            if not obj.visible_get(view_layer=view_layer):
                continue
        except RuntimeError:
            continue
        p = view3d_utils.location_3d_to_region_2d(
            region, rv3d, _door_centre(obj))
        if p is None:
            continue
        tw, th = blf.dimensions(0, codes)
        w = tw + 2 * PAD_X * s
        h = th + 2 * PAD_Y * s
        labels.append(((p.x - w / 2.0, p.y - h / 2.0, w, h), codes))
    if not labels:
        return

    def _paint():
        gpu.state.blend_set('ALPHA')
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        shader.bind()
        for rect, text in labels:
            _draw_rect(shader, rect)
            blf.size(0, font_sz)
            blf.color(0, *TEXT_COLOR)
            blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
            blf.draw(0, text)
        gpu.state.blend_set('NONE')

    from ...operators import viewport_hud
    viewport_hud.paint_clear_of_panel(context, area, _paint)


def register():
    global _draw_handle, _shutdown, _dirty
    _shutdown = False
    _dirty = True
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
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
