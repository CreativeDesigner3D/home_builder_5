"""Shared GPU drawing helpers for Home Builder viewport overlays.

Region-bounds math and low-level rect/text primitives used by the scene
navigator overlay and the viewport HUD. Kept here so both draw paths share
one implementation rather than carrying private copies that can drift.
"""

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader


# Zoom, pan, camera and the perspective/ortho toggle.
_NAV_MINI_BUTTONS = 4


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


def navigation_gizmo_reserve(area):
    """(width, height) of the top-right block Blender's navigation
    gizmo occupies, in WINDOW-local pixels. (0, 0) when it is hidden.

    get_visible_window_bounds handles overlapping REGIONS, but the
    navigate gizmo is not a region -- it is drawn into the WINDOW
    region itself, so nothing reports it and an overlay anchored to the
    top-right corner lands straight on top of it.

    Blender does not expose the cluster's extent either, so this is
    derived from what it does draw: the axis ball is
    ``gizmo_size_navigate_v3d`` across, and beneath it sits a column of
    mini buttons (zoom, pan, camera, and the perspective/ortho toggle)
    each a little under half the ball's size. Erring large is the safe
    direction -- overlapping the gizmo is worse than leaving a gap.
    """
    space = getattr(area, 'spaces', None)
    space = getattr(space, 'active', None) if space else None
    if space is None or space.type != 'VIEW_3D':
        return (0.0, 0.0)
    if not (getattr(space, 'show_gizmo', False)
            and getattr(space, 'show_gizmo_navigate', False)):
        return (0.0, 0.0)
    try:
        prefs = bpy.context.preferences
        ball = prefs.view.gizmo_size_navigate_v3d * prefs.system.ui_scale
    except AttributeError:
        ball = 80.0
    mini = ball * 0.42
    return (ball + mini * 0.5, ball + mini * _NAV_MINI_BUTTONS + mini * 0.5)


def draw_rects(shader, rects, color):
    """Fill many rectangles in ONE batch.

    Each batch_for_shader call builds a GPU buffer, so a grid that
    fills its tiles one at a time pays per tile: the library panel
    measured 4.5 ms for 33 tiles across 99 batches, and collapsing the
    chrome to two batches took most of that back. Use this whenever the
    rectangle count scales with the data.
    """
    verts = []
    for x, y, w, h in rects:
        verts.extend(((x, y), (x + w, y), (x + w, y + h),
                      (x, y), (x + w, y + h), (x, y + h)))
    if not verts:
        return
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'TRIS', {"pos": verts}).draw(shader)


def draw_rect_outlines(shader, rects, color):
    """Outline many rectangles in ONE batch (see draw_rects)."""
    verts = []
    for x, y, w, h in rects:
        verts.extend(((x, y), (x + w, y),
                      (x + w, y), (x + w, y + h),
                      (x + w, y + h), (x, y + h),
                      (x, y + h), (x, y)))
    if not verts:
        return
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES', {"pos": verts}).draw(shader)


def draw_glyphs(font_id, text):
    """blf.draw, with the GPU blend state put back the way it was.

    blf sets its own blend mode and does NOT restore it, so everything
    drawn after a label in the same callback loses alpha: a border at 14%
    white came out solid white, a 95% panel fill came out opaque. It read
    as the first item in a strip being styled differently from the rest,
    because the first one is the only one drawn before any text.

    Every label in this UI goes through here so no caller has to know
    that.
    """
    previous = gpu.state.blend_get()
    blf.draw(font_id, text)
    gpu.state.blend_set(previous)


def draw_text(font_id, x, y, size, color, text):
    """Draw a single line of text at a baseline position."""
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    draw_glyphs(font_id, text)


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
