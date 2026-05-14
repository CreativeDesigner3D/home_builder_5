"""Shared GPU drawing helpers for Home Builder viewport overlays.

Region-bounds math and low-level rect/text primitives used by the scene
navigator overlay and the viewport HUD. Kept here so both draw paths share
one implementation rather than carrying private copies that can drift.
"""

import blf
from gpu_extras.batch import batch_for_shader


def get_visible_window_bounds(area):
    """Return (x_min, x_max, y_min, y_max) of the WINDOW region's *visible*
    rectangle in WINDOW-local pixel coords -- i.e. the area not covered by
    overlapping toolbar / N-panel / header / asset-shelf regions.

    With "Region Overlap" enabled (Blender's default), the WINDOW region
    extends underneath those overlays. POST_PIXEL handlers draw before the
    overlays composite on top, so anything drawn at the raw edges of WINDOW
    gets hidden. This returns the bounds we should respect."""
    if area is None:
        return (0, 0, 0, 0)

    win = None
    overlays = []
    for r in area.regions:
        if r.type == 'WINDOW':
            win = r
        elif r.type in {'TOOLS', 'UI', 'HEADER', 'TOOL_HEADER',
                        'ASSET_SHELF', 'ASSET_SHELF_HEADER'}:
            if r.width > 1 and r.height > 1:
                overlays.append(r)
    if win is None:
        return (0, 0, 0, 0)

    x_min, x_max = 0, win.width
    y_min, y_max = 0, win.height
    win_mid_y = win.height / 2.0

    for r in overlays:
        local_x = r.x - win.x
        local_y = r.y - win.y
        local_x2 = local_x + r.width
        local_y2 = local_y + r.height

        if r.type == 'TOOLS' and local_x <= 0 < local_x2:
            x_min = max(x_min, local_x2)
        elif r.type == 'UI' and local_x < win.width <= local_x2:
            x_max = min(x_max, local_x)
        elif r.type in {'HEADER', 'TOOL_HEADER', 'ASSET_SHELF_HEADER'}:
            # Classify header as top vs bottom by which half its center sits
            # in -- catches stacked headers where one is inside WINDOW rather
            # than spanning its top edge.
            center_y = (local_y + local_y2) / 2.0
            if center_y > win_mid_y:
                y_max = min(y_max, local_y)
            else:
                y_min = max(y_min, local_y2)
        elif r.type == 'ASSET_SHELF':
            if (local_y + local_y2) / 2.0 < win_mid_y:
                y_min = max(y_min, local_y2)

    return (x_min, x_max, y_min, y_max)


def draw_rect(shader, x, y, w, h, color):
    """Filled rectangle via two triangles."""
    shader.uniform_float("color", color)
    verts = [
        (x, y), (x + w, y), (x + w, y + h),
        (x, y), (x + w, y + h), (x, y + h),
    ]
    batch_for_shader(shader, 'TRIS', {"pos": verts}).draw(shader)


def draw_rect_outline(shader, x, y, w, h, color):
    """Rectangle border via line segments."""
    shader.uniform_float("color", color)
    verts = [
        (x, y), (x + w, y),
        (x + w, y), (x + w, y + h),
        (x + w, y + h), (x, y + h),
        (x, y + h), (x, y),
    ]
    batch_for_shader(shader, 'LINES', {"pos": verts}).draw(shader)


def draw_text(font_id, x, y, size, color, text):
    """Draw a single line of text at a baseline position."""
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def vcenter_baseline(rect, font_id, size):
    """Y baseline that vertically centers a line of text in `rect`."""
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    text_h = blf.dimensions(font_id, "Aj")[1]
    return ry + (rh - text_h) / 2.0


def point_in_rect(x, y, rect):
    """True if (x, y) falls inside rect (x, y, w, h)."""
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


def draw_lines(shader, points, color):
    """Draw line segments. `points` is a flat list of (x, y) pairs consumed
    two at a time as segment endpoints."""
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES', {"pos": points}).draw(shader)
