"""Dimensions drawn while something is being placed.

The prior library drew a dimension from the floor up to whatever was
being dropped and another from it to the top of the opening, so a
person could see where the thing had landed without letting go of it.
This does the same, in screen space: the ends are 3D points and the
line, its ticks and its figure are drawn over the viewport, so nothing
is created in the file and nothing has to be cleaned up if a placement
is cancelled.

Only a placement operator uses this. It draws nothing at all until
show() is called and stops the moment hide() is.
"""
import blf
import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader

from ... import units

LINE_COLOR = (0.95, 0.75, 0.15, 1.0)
SNAP_COLOR = (0.35, 0.9, 0.4, 1.0)
TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
SHADOW = (0.0, 0.0, 0.0, 0.85)
FONT_SIZE = 13
TICK = 7.0

_handle = None
_entries = []


def show(entries):
    """Draw these dimensions until told otherwise.

    Each entry is (start, end, text, snapped) - two world points, the
    figure to write by the line, and whether this one is up against
    something, which colours it."""
    global _handle, _entries
    _entries = list(entries)
    if _handle is None:
        _handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw, (), 'WINDOW', 'POST_PIXEL')


def hide():
    """Stop drawing and let go of the handler."""
    global _handle, _entries
    _entries = []
    if _handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        except Exception:
            pass
        _handle = None


def unregister():
    """Extension teardown: a handler left behind here would outlive
    the module it draws from and could never be removed again."""
    hide()


def label_for(value):
    """A distance written the way the rest of the library writes one -
    in the room's own units, rounded the way a cabinet is."""
    try:
        return units.unit_to_string(
            bpy.context.scene.unit_settings, value)
    except Exception:
        return '%g"' % round(value / 0.0254, 3)


def _line(shader, points, color):
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES', {"pos": points}).draw(shader)


def _text(x, y, size, text):
    # Drawn twice, dark then light, so it stays readable over both a
    # pale panel and a dark opening.
    blf.size(0, size)
    w, h = blf.dimensions(0, text)
    blf.color(0, *SHADOW)
    blf.position(0, x - w / 2.0 + 1, y - h / 2.0 - 1, 0)
    blf.draw(0, text)
    blf.color(0, *TEXT_COLOR)
    blf.position(0, x - w / 2.0, y - h / 2.0, 0)
    blf.draw(0, text)


def _draw():
    """POST_PIXEL callback. Guarded throughout - a drawing error must
    never spill into the viewport or stop a placement."""
    if not _entries:
        return
    try:
        context = bpy.context
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return
        if context.area is None or context.area.type != 'VIEW_3D':
            return
        scale = 1.0
        try:
            scale = context.preferences.system.ui_scale
        except AttributeError:
            pass
        size = FONT_SIZE * scale
        tick = TICK * scale
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        try:
            shader = gpu.shader.from_builtin('UNIFORM_COLOR')
            shader.bind()
            for start, end, text, snapped in _entries:
                a = view3d_utils.location_3d_to_region_2d(region, rv3d,
                                                          start)
                b = view3d_utils.location_3d_to_region_2d(region, rv3d,
                                                          end)
                if a is None or b is None:
                    continue
                color = SNAP_COLOR if snapped else LINE_COLOR
                dx, dy = b.x - a.x, b.y - a.y
                length = (dx * dx + dy * dy) ** 0.5
                if length < 1.0:
                    continue
                # ticks square to the line, so it reads as a dimension
                nx, ny = -dy / length * tick, dx / length * tick
                _line(shader, [(a.x, a.y), (b.x, b.y)], color)
                _line(shader,
                      [(a.x - nx, a.y - ny), (a.x + nx, a.y + ny)],
                      color)
                _line(shader,
                      [(b.x - nx, b.y - ny), (b.x + nx, b.y + ny)],
                      color)
                _text((a.x + b.x) / 2.0 + nx * 2.4,
                      (a.y + b.y) / 2.0 + ny * 2.4, size, text)
        finally:
            # Whatever happens per entry, the state this drew with
            # must not leak into whoever draws next.
            gpu.state.line_width_set(1.0)
            gpu.state.blend_set('NONE')
    except Exception:
        pass
