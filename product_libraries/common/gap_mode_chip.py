"""The Move / Width choice shown beside a gap dimension while it is typed.

A typed gap or wall-end dimension (common/wall_run_dims) either slides
the product along its wall or changes its width. The choice only
matters while such a label is being edited, so that is the only time it
shows: a two-part chip drawn just right of the edit field. Clicking a
part picks it, Tab flips it, and the edit carries on either way.

Both cabinet overlays (face frame and frameless dim_edit_overlay) draw
it from their edit branch and ask hit() from their edit modal. Hit
rects are kept in window space so the modal can test event.mouse_x /
mouse_y whichever region it was started from.
"""

import blf
from gpu_extras.batch import batch_for_shader

from . import wall_run_dims

PARTS = (('MOVE', "Move"), ('WIDTH', "Width"))

BG          = (0.13, 0.13, 0.14, 0.90)
ACTIVE_BG   = (0.20, 0.43, 0.70, 0.95)
BORDER      = (1.0, 1.0, 1.0, 0.25)
TEXT        = (0.80, 0.80, 0.80, 1.0)
ACTIVE_TEXT = (1.0, 1.0, 1.0, 1.0)
GAP_PX      = 4
PAD_X       = 6

# [(mode, (x, y, w, h))] in window space, from the last draw.
_hits = []


def clear():
    _hits.clear()


def _rect(shader, rect, bg):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", BORDER)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def draw(shader, scene, region, field_rect, font_size, s):
    """Draw the chip right of ``field_rect`` (region space) and record
    its parts for hit(). Call with the UNIFORM_COLOR shader bound."""
    clear()
    mode = wall_run_dims.edit_mode(scene)
    fx, fy, fw, fh = field_rect
    x = fx + fw + GAP_PX * s
    blf.size(0, font_size)
    for key, text in PARTS:
        tw, _th = blf.dimensions(0, text)
        w = tw + 2 * PAD_X * s
        rect = (x, fy, w, fh)
        active = key == mode
        _rect(shader, rect, ACTIVE_BG if active else BG)
        blf.color(0, *(ACTIVE_TEXT if active else TEXT))
        blf.position(0, x + PAD_X * s, fy + (fh - _th) / 2.0, 0)
        blf.draw(0, text)
        _hits.append((key, (region.x + x, region.y + fy, w, fh)))
        x += w


def hit(mouse_x, mouse_y):
    """The part under a window-space point, or None."""
    for key, (x, y, w, h) in _hits:
        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            return key
    return None


def set_mode(scene, mode):
    scene[wall_run_dims.EDIT_MODE_KEY] = mode
