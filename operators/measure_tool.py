"""Measuring in the viewport.

Blender's own Measure is a workspace tool, so reaching for it costs you
whatever tool you were holding, and the rulers it leaves behind live in
an annotation layer that accumulates quietly. Neither suits someone who
measures constantly while laying out a room.

This is a bounded modal instead. You pick it up, take as many
measurements as you like, and drop it with Esc -- your tool is never
swapped out, and nothing about the operator outlives it. It is a real
modal with an end, not an always-on listener, so autosave keeps running.

**Nothing here is written to the file.** A measurement is a few world
points in a module-level list, painted by a draw handler. It cannot
dirty the blend, cannot be caught up in undo, and cannot turn up in a
render or on a drawing. The cost is that measurements do not survive
reopening the file, which is the right trade for something you take to
answer a question. They stay on screen until cleared so you can set
several, orbit, and look at them together.

Three modes, cycled with Tab:

``LINEAR``   two points, straight-line distance.
``ANGULAR``  a corner then two arms, in degrees.
``QUICK``    two points, read as their X, Y and Z distances at once,
             kept like any other measurement. Q switches to it and back
             from inside the tool, and Alt+M starts the tool in it.

Switching modes (Tab, Q) keeps a point already placed, so you can click
the first point and then decide how to read it.

Snapping comes from `hb_snap_engine`, so it follows the same magnet
menu as everything else, and Ctrl inverts it exactly as it does in
Blender. X, Y and Z lock the measurement to that world axis.

Lengths read rounded the way the rest of the model does (the nearest
sixteenth in inches). E switches every measurement on screen to the
unrounded value and back, for checking a figure against a drawing.

There was a third mode that took two objects and reported the clear
distance between them. It was dropped: picking two points is direct
enough that resolving objects, their parts and their axes only added
something else to understand.
"""

import math

import bpy
import blf
import gpu
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from .. import hb_snap_engine, hb_snap, units
from ..hb_gpu_draw import draw_lines, draw_text, draw_rect
from ..hb_gpu_ui import (
    scale,
    Theme,
    draw_polyline,
    draw_arrow_head,
    arc_points,
    circle_points,
    text_width,
)


MODES = ('LINEAR', 'ANGULAR', 'QUICK')
MODE_LABELS = {
    'LINEAR': "Distance",
    'ANGULAR': "Angle",
    'QUICK': "Quick XYZ",
}
# How many points each mode collects before it has a measurement.
MODE_POINTS = {'LINEAR': 2, 'ANGULAR': 3, 'QUICK': 2}

AXES = ('X', 'Y', 'Z')


class MeasureTheme:
    """Amber, so a measurement never reads as a dimension on a drawing."""

    LINE = (1.00, 0.72, 0.20, 1.00)
    LINE_PENDING = (1.00, 0.72, 0.20, 0.65)
    LINE_HOVER = (1.00, 0.35, 0.25, 1.00)
    CHIP_BG = (0.08, 0.08, 0.08, 0.90)
    CHIP_TEXT = (1.00, 0.85, 0.55, 1.00)
    SNAP = (0.35, 0.85, 1.00, 1.00)
    AXIS = {'X': (1.0, 0.35, 0.35, 0.8),
            'Y': (0.45, 0.9, 0.35, 0.8),
            'Z': (0.4, 0.55, 1.0, 0.8)}


ARROW = 7           # unscaled px, dimension arrow barb
CHIP_PAD = 5
FONT_SIZE = 12
SNAP_MARK = 6
PICK_RADIUS = 10    # unscaled px, how close the cursor must be to pick one


# ---- Store ------------------------------------------------------------------
# World-space, per scene, never saved. A rename orphans a measurement,
# which is acceptable for something this short-lived.

class Measurement:

    __slots__ = ('kind', 'points', 'scene', 'value', 'label')

    def __init__(self, kind, points, scene, value, label):
        self.kind = kind
        self.points = [p.copy() for p in points]
        self.scene = scene
        self.value = value      # metres, or degrees for ANGULAR
        self.label = label

    def __repr__(self):
        return f"<Measurement {self.kind} {self.label}>"


_measurements = []


def measurements_for(scene):
    name = scene.name
    return [m for m in _measurements if m.scene == name]


def measurement_count(scene):
    name = scene.name
    return sum(1 for m in _measurements if m.scene == name)


def add_measurement(m):
    _measurements.append(m)


def pop_measurement(scene):
    """Drop the newest measurement in this scene."""
    name = scene.name
    for i in range(len(_measurements) - 1, -1, -1):
        if _measurements[i].scene == name:
            del _measurements[i]
            return True
    return False


def remove_measurement(m):
    """Drop one measurement; False when it was already gone."""
    for i, other in enumerate(_measurements):
        if other is m:
            del _measurements[i]
            return True
    return False


def _segment_distance(p, a, b):
    ab = b - a
    length_sq = ab.length_squared
    if length_sq < 1e-9:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / length_sq))
    return (p - (a + ab * t)).length


def measurement_at(scene, region, rv3d, mouse, radius):
    """The measurement in this scene whose line passes nearest the mouse
    (region pixels), within ``radius``; None when nothing is that close."""
    cursor = Vector(mouse)
    best, best_d = None, radius
    for m in measurements_for(scene):
        pts = [_project(region, rv3d, p) for p in m.points]
        if any(p is None for p in pts):
            continue
        pts = [Vector((p.x, p.y)) for p in pts]
        if m.kind == 'ANGULAR':
            segs = [(pts[0], pts[1]), (pts[0], pts[2])]
        elif m.kind == 'XYZ':
            segs = [(pts[0], pts[1])] + [
                (Vector((a.x, a.y)), Vector((b.x, b.y)))
                for a, b in _xyz_legs_2d(region, rv3d, m.points[0], m.points[1])]
        else:
            segs = [(pts[0], pts[1])]
        d = min(_segment_distance(cursor, a, b) for a, b in segs)
        if d <= best_d:
            best, best_d = m, d
    return best


def clear_measurements(scene=None):
    """Clear this scene's measurements, or every one when scene is None."""
    global _measurements
    if scene is None:
        _measurements = []
    else:
        name = scene.name
        _measurements = [m for m in _measurements if m.scene != name]


# ---- Labels -----------------------------------------------------------------

def exact_values(context):
    return bool(getattr(context.window_manager, 'hb_measure_exact', False))


def _trimmed(value, places):
    text = f"{value:.{places}f}".rstrip('0').rstrip('.')
    return "0" if text in ("", "-0") else text


def exact_length_label(unit_settings, metres):
    """The length without the model's display rounding. Converted from
    the exact factors: the shared helpers carry a rounded one, which
    shows in the fourth place on a long measurement."""
    if unit_settings.system == 'METRIC':
        if unit_settings.length_unit == 'METERS':
            return _trimmed(metres, 5) + "m"
        return _trimmed(units.meter_to_millimeter(metres), 3) + "mm"
    if unit_settings.system == 'IMPERIAL':
        if unit_settings.length_unit == 'FEET':
            return _trimmed(metres / 0.3048, 4) + "'"
        return _trimmed(metres / 0.0254, 4) + '"'
    return _trimmed(metres, 5)


def length_label(context, metres):
    if exact_values(context):
        return exact_length_label(context.scene.unit_settings, metres)
    return units.unit_to_string(context.scene.unit_settings, metres)


def angle_label(degrees, exact=False):
    return f"{_trimmed(degrees, 3 if exact else 1)}°"


def xyz_parts(a, b):
    """The world X, Y and Z distances from a to b, unsigned."""
    d = b - a
    return [(axis, abs(d[i])) for i, axis in enumerate(AXES)]


def xyz_label(context, a, b):
    """'X 1/8"  Y 22"  Z 1/2"' for a quick reading."""
    return "  ".join(f"{axis} {length_label(context, v)}"
                     for axis, v in xyz_parts(a, b))


def measurement_label(context, m):
    """A committed measurement's text under the current rounding choice."""
    if m.kind == 'ANGULAR':
        return angle_label(m.value, exact_values(context))
    if m.kind == 'XYZ':
        return quick_label(context, m.points[0], m.points[1])
    return length_label(context, m.value)


def quick_label(context, a, b):
    """The X, Y and Z distances, then the straight-line one in brackets."""
    return f"{xyz_label(context, a, b)}  ({length_label(context, (b - a).length)})"


# ---- Geometry ---------------------------------------------------------------

def constrain_to_axis(point, anchor, axis):
    """Project `point` onto the world `axis` line through `anchor`.

    World axes, always. Locking to the axes of whatever happened to be
    under the cursor made pressing X do something different depending on
    which cabinet you had snapped to -- and on a cabinet turned to an
    angled wall, X was not X. A key named after an axis has to mean that
    axis.
    """
    index = AXES.index(axis)
    out = anchor.copy()
    out[index] = point[index]
    return out


# ---- Drawing ----------------------------------------------------------------

def _project(region, rv3d, point):
    return view3d_utils.location_3d_to_region_2d(region, rv3d, point)


def _chip(shader, font_id, x, y, text, s):
    """Value plate, centred on (x, y)."""
    size = int(FONT_SIZE * s)
    blf.size(font_id, size)
    w = text_width(font_id, size, text)
    h = blf.dimensions(font_id, text)[1]
    pad = CHIP_PAD * s
    draw_rect(shader, x - w * 0.5 - pad, y - h * 0.5 - pad,
              w + pad * 2, h + pad * 2, MeasureTheme.CHIP_BG)
    draw_text(font_id, x - w * 0.5, y - h * 0.5, size,
              MeasureTheme.CHIP_TEXT, text)


def _draw_span(shader, font_id, a, b, text, s, color):
    """A dimension line between two projected points, with its value."""
    draw_lines(shader, [(a.x, a.y), (b.x, b.y)], color)
    direction = Vector((b.x - a.x, b.y - a.y))
    if direction.length > 1.0:
        direction.normalize()
        size = ARROW * s
        draw_arrow_head(shader, (a.x, a.y), (-direction.x, -direction.y), size, color)
        draw_arrow_head(shader, (b.x, b.y), (direction.x, direction.y), size, color)
    if text:
        _chip(shader, font_id, (a.x + b.x) * 0.5, (a.y + b.y) * 0.5, text, s)


def _draw_angle(shader, font_id, corner, arm_a, arm_b, text, s, color):
    """Two arms from a corner, with an arc and the angle between them."""
    draw_lines(shader, [(corner.x, corner.y), (arm_a.x, arm_a.y),
                        (corner.x, corner.y), (arm_b.x, arm_b.y)], color)
    va = Vector((arm_a.x - corner.x, arm_a.y - corner.y))
    vb = Vector((arm_b.x - corner.x, arm_b.y - corner.y))
    if va.length < 1.0 or vb.length < 1.0:
        return
    radius = min(va.length, vb.length) * 0.35
    start = math.atan2(va.y, va.x)
    end = math.atan2(vb.y, vb.x)
    # Sweep the short way round, so the arc marks the angle being read.
    while end - start > math.pi:
        end -= 2.0 * math.pi
    while start - end > math.pi:
        end += 2.0 * math.pi
    draw_polyline(shader, arc_points(corner.x, corner.y, radius, start, end, 24), color)
    if text:
        mid = (start + end) * 0.5
        _chip(shader, font_id,
              corner.x + math.cos(mid) * (radius + 18 * s),
              corner.y + math.sin(mid) * (radius + 18 * s), text, s)


def _xyz_legs_2d(region, rv3d, a, b):
    """The projected world-axis legs from a to b, zero-length ones left out."""
    out = []
    corner = a.copy()
    for i in range(3):
        nxt = corner.copy()
        nxt[i] = b[i]
        if abs(b[i] - a[i]) > 1e-6:
            q0, q1 = _project(region, rv3d, corner), _project(region, rv3d, nxt)
            if q0 is not None and q1 is not None:
                out.append((q0, q1))
        corner = nxt
    return out


def _draw_xyz(shader, font_id, region, rv3d, a, b, s, line_color=None, leg_color=None):
    """A quick reading: the straight line a to b, then the three world-axis
    legs that make it up, each in its axis colour with its own value.
    A leg with no length is left out so a square-on pick reads cleanly.
    ``leg_color`` paints every leg one colour (a hovered, kept reading)."""
    pa, pb = _project(region, rv3d, a), _project(region, rv3d, b)
    if pa is None or pb is None:
        return
    draw_lines(shader, [(pa.x, pa.y), (pb.x, pb.y)],
               line_color or MeasureTheme.LINE_PENDING)
    context = bpy.context
    corner = a.copy()
    tiny = 1e-6
    for i, axis in enumerate(AXES):
        nxt = corner.copy()
        nxt[i] = b[i]
        length = abs(b[i] - a[i])
        if length > tiny:
            p0 = _project(region, rv3d, corner)
            p1 = _project(region, rv3d, nxt)
            if p0 is not None and p1 is not None:
                draw_lines(shader, [(p0.x, p0.y), (p1.x, p1.y)],
                           leg_color or MeasureTheme.AXIS[axis])
                _chip(shader, font_id, (p0.x + p1.x) * 0.5, (p0.y + p1.y) * 0.5,
                      f"{axis} {length_label(context, length)}", s)
        corner = nxt


def _draw_snap_marker(shader, kind, x, y, s):
    """Blender shows what it caught; so does this."""
    r = SNAP_MARK * s
    color = MeasureTheme.SNAP
    if kind == 'VERTEX':
        draw_polyline(shader, [(x - r, y - r), (x + r, y - r),
                               (x + r, y + r), (x - r, y + r)], color, closed=True)
    elif kind == 'EDGE_MIDPOINT':
        draw_polyline(shader, [(x - r, y - r), (x + r, y - r), (x, y + r)],
                      color, closed=True)
    elif kind == 'EDGE':
        draw_polyline(shader, [(x, y - r), (x + r, y), (x, y + r), (x - r, y)],
                      color, closed=True)
    else:
        draw_polyline(shader, circle_points(x, y, r, 16), color, closed=True)


def _draw_measurement(shader, font_id, region, rv3d, m, s, color):
    points = [_project(region, rv3d, p) for p in m.points]
    if any(p is None for p in points):
        return
    # Read from the stored value, so the rounding switch reaches the
    # measurements already on screen.
    if m.kind == 'XYZ':
        hovered = color is MeasureTheme.LINE_HOVER
        _draw_xyz(shader, font_id, region, rv3d, m.points[0], m.points[1], s,
                  line_color=color, leg_color=color if hovered else None)
        return
    label = measurement_label(bpy.context, m)
    if m.kind == 'ANGULAR':
        _draw_angle(shader, font_id, points[0], points[1], points[2],
                    label, s, color)
    else:
        _draw_span(shader, font_id, points[0], points[1], label, s, color)


# The running operator, so one handler can paint both the committed
# measurements and whatever is being pointed at right now.
_active = None
_draw_handle = None


def _draw():
    context = bpy.context
    scene = context.scene
    region = context.region
    if region is None or scene is None:
        return
    pending = _active if (_active is not None and _active.scene_name == scene.name) else None
    committed = measurements_for(scene)
    if not committed and pending is None:
        return                                  # idle costs nothing
    rv3d = context.space_data.region_3d if context.space_data else None
    if rv3d is None:
        return

    s = scale()
    font_id = 0
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(2.0)
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    hovered = getattr(_active, 'hover', None) if _active is not None else None
    try:
        for m in committed:
            _draw_measurement(shader, font_id, region, rv3d, m, s,
                              MeasureTheme.LINE_HOVER if m is hovered
                              else MeasureTheme.LINE)
        if pending is not None:
            pending.draw_pending(shader, font_id, region, rv3d, s)
    finally:
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set('NONE')


def tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---- The tool ---------------------------------------------------------------

class home_builder_OT_measure(bpy.types.Operator):
    bl_idname = "home_builder.measure"
    bl_label = "Measure"
    bl_description = ("Measure distances and angles in the viewport. "
                      "Measurements stay on screen until cleared")
    # No bpy.data is written, so there is nothing for undo to hold.
    bl_options = {'REGISTER'}

    quick: bpy.props.BoolProperty(
        name="Quick XYZ",
        description=("Start in Quick XYZ: read the X, Y and Z distances "
                     "between two points without leaving a measurement behind"),
        default=False,
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        global _active
        self.scene_name = context.scene.name
        self.mode = 'QUICK' if self.quick else context.window_manager.hb_measure_mode
        self.prev_mode = 'LINEAR'
        self.points = []
        self.hit = None
        self.cursor = None
        self.axis = None
        self.snap_on = True
        self.last_label = ""
        self.hover = None
        _active = self
        context.window_manager.modal_handler_add(self)
        self._update_header(context)
        tag_redraw()
        return {'RUNNING_MODAL'}

    # -- state -------------------------------------------------------------

    def _needed(self):
        return MODE_POINTS[self.mode]

    def _elements(self, context):
        elements = hb_snap_engine.elements_from_tool_settings(context.scene)
        # An empty magnet menu would leave the tool unable to catch
        # anything, which reads as broken rather than as a setting.
        return elements or hb_snap_engine.PRIORITY

    def _update_header(self, context):
        bits = [MODE_LABELS[self.mode]]
        if self.mode == 'ANGULAR':
            bits.append(("Click the corner", "Click the first arm",
                         "Click the second arm")[min(len(self.points), 2)])
        else:
            bits.append("Click the first point" if not self.points
                        else "Click the second point")
        if self.axis:
            bits.append(f"[{self.axis}]")
        if self.hit is not None:
            bits.append(f"[{self.hit.kind.replace('_', ' ').title()}]")
        elif not self.snap_on:
            bits.append("[No Snap]")
        if self.mode == 'QUICK' and self.points and self.cursor is not None:
            bits.append(quick_label(context, self.points[0], self.cursor))
        elif self.hover is not None:
            bits.append(f"[{self.hover.label}: Delete removes it]")
        elif self.last_label:
            bits.append(f"= {self.last_label}")
        if exact_values(context):
            bits.append("[Exact]")
        bits.append("Tab: mode | Q: quick XYZ | X/Y/Z: axis | E: exact | "
                    "Ctrl: snap | Backspace: undo | Del: remove hovered | "
                    "Right-click: drop reading | Esc: done")
        context.area.header_text_set("  ".join(b for b in bits if b))

    # -- points ------------------------------------------------------------

    def _region(self, context, event):
        region = context.region
        rv3d = context.space_data.region_3d if context.space_data else None
        if region is None or rv3d is None:
            return None, None, None
        return region, rv3d, (event.mouse_region_x, event.mouse_region_y)

    def _free_point(self, region, rv3d, mouse):
        """Where the cursor is pointing when nothing snapped.

        Anchored on the plane of the last point so a second click stays in
        the same plane as the first; before that, on the floor, falling
        back to a view-facing plane when the floor is edge-on and the
        intersection would fly off.
        """
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse)
        if self.points:
            normal = rv3d.view_rotation @ Vector((0.0, 0.0, 1.0))
            anchor = self.points[-1]
        else:
            normal = Vector((0.0, 0.0, 1.0))
            anchor = Vector((0.0, 0.0, 0.0))
        point = intersect_line_plane(origin, origin + direction, anchor, normal)
        if point is None or (point - origin).length > 1000.0:
            normal = rv3d.view_rotation @ Vector((0.0, 0.0, 1.0))
            point = intersect_line_plane(origin, origin + direction, anchor, normal)
        return point

    def _sample(self, context, event):
        region, rv3d, mouse = self._region(context, event)
        if region is None:
            return
        engine = hb_snap_engine.engine()
        # Ctrl inverts snapping, the way it does everywhere else.
        want_snap = self.snap_on != event.ctrl
        self.hit = (engine.snap(context, region, rv3d, mouse,
                                elements=self._elements(context))
                    if want_snap else None)
        point = self.hit.location.copy() if self.hit else self._free_point(
            region, rv3d, mouse)
        if point is None:
            self.cursor = None
            return
        if self.axis and self.points:
            point = constrain_to_axis(point, self.points[0], self.axis)
        self.cursor = point

    def _pick_hover(self, context, event):
        """The finished measurement under the cursor, while nothing is
        half-placed, so Delete can take out just that one."""
        self.hover = None
        if self.points:
            return
        region, rv3d, mouse = self._region(context, event)
        if region is None:
            return
        self.hover = measurement_at(context.scene, region, rv3d, mouse,
                                    PICK_RADIUS * scale())

    # -- committing --------------------------------------------------------

    def _commit_linear(self, context):
        a, b = self.points[0], self.points[1]
        value = (b - a).length
        label = length_label(context, value)
        add_measurement(Measurement('LINEAR', [a, b], self.scene_name,
                                    value, label))
        return label

    def _commit_angular(self, context):
        corner, arm_a, arm_b = self.points
        va = arm_a - corner
        vb = arm_b - corner
        if va.length < 1e-6 or vb.length < 1e-6:
            return None
        degrees = math.degrees(va.angle(vb))
        label = angle_label(degrees, exact_values(context))
        add_measurement(Measurement('ANGULAR', [corner, arm_a, arm_b],
                                    self.scene_name, degrees, label))
        return label

    def _commit_quick(self, context):
        a, b = self.points[0], self.points[1]
        label = quick_label(context, a, b)
        add_measurement(Measurement('XYZ', [a, b], self.scene_name,
                                    (b - a).length, label))
        return label

    def _place(self, context, event):
        if self.cursor is None:
            return
        self.points.append(self.cursor.copy())
        if len(self.points) < self._needed():
            return
        if self.mode == 'ANGULAR':
            label = self._commit_angular(context)
        elif self.mode == 'QUICK':
            label = self._commit_quick(context)
        else:
            label = self._commit_linear(context)
        self._reset_pending(label)

    def _set_mode(self, context, mode):
        """Switch how the points are read. A point already placed stays,
        so a first click can be read either way; only what the new mode
        could not use yet is dropped (it always needs one more click)."""
        self.mode = mode
        self.last_label = ""
        del self.points[max(0, MODE_POINTS[mode] - 1):]
        self._update_header(context)
        tag_redraw()

    def _reset_pending(self, label):
        if label:
            self.last_label = label
        self.points = []
        self.axis = None

    # -- pending overlay ---------------------------------------------------

    def draw_pending(self, shader, font_id, region, rv3d, s):
        """What is being pointed at right now, drawn dimmer than the rest."""
        color = MeasureTheme.LINE_PENDING
        placed = [_project(region, rv3d, p) for p in self.points]
        live = _project(region, rv3d, self.cursor) if self.cursor else None

        if self.mode == 'QUICK':
            if self.points and self.cursor is not None:
                _draw_xyz(shader, font_id, region, rv3d,
                          self.points[0], self.cursor, s)
            for p in placed:
                if p is not None:
                    _draw_snap_marker(shader, 'VERTEX', p.x, p.y, s)
            if self.hit is not None and live is not None:
                _draw_snap_marker(shader, self.hit.kind, live.x, live.y, s)
            return

        if self.axis and placed and placed[0] is not None and live is not None:
            draw_lines(shader, [(placed[0].x, placed[0].y), (live.x, live.y)],
                       MeasureTheme.AXIS.get(self.axis, color))

        if self.mode == 'ANGULAR' and len(placed) == 2 and live is not None:
            if all(p is not None for p in placed):
                va = self.points[1] - self.points[0]
                vb = self.cursor - self.points[0]
                text = (angle_label(math.degrees(va.angle(vb)),
                                    exact_values(bpy.context))
                        if va.length > 1e-6 and vb.length > 1e-6 else "")
                _draw_angle(shader, font_id, placed[0], placed[1], live,
                            text, s, color)
        elif len(placed) >= 1 and live is not None:
            if placed[0] is not None:
                anchor = placed[-1] if self.mode == 'ANGULAR' else placed[0]
                text = ""
                if self.mode == 'LINEAR':
                    text = length_label(bpy.context,
                                        (self.cursor - self.points[0]).length)
                _draw_span(shader, font_id, anchor, live, text, s, color)

        for p in placed:
            if p is not None:
                _draw_snap_marker(shader, 'VERTEX', p.x, p.y, s)
        if self.hit is not None and live is not None:
            _draw_snap_marker(shader, self.hit.kind, live.x, live.y, s)

    # -- modal -------------------------------------------------------------

    def modal(self, context, event):
        if hb_snap.event_is_pass_through(event):
            tag_redraw()
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            self._sample(context, event)
            self._pick_hover(context, event)
            self._update_header(context)
            tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._sample(context, event)
            self._place(context, event)
            self._update_header(context)
            tag_redraw()
            return {'RUNNING_MODAL'}

        if event.value == 'PRESS':
            if event.type == 'TAB':
                index = MODES.index(self.mode)
                mode = MODES[(index + 1) % len(MODES)]
                context.window_manager.hb_measure_mode = mode
                self._set_mode(context, mode)
                return {'RUNNING_MODAL'}

            if event.type == 'Q':
                # In and out of Quick XYZ, back to whichever mode you
                # were in; not remembered as the mode to start in.
                if self.mode == 'QUICK':
                    self._set_mode(context, self.prev_mode)
                else:
                    self.prev_mode = self.mode
                    self._set_mode(context, 'QUICK')
                return {'RUNNING_MODAL'}

            if event.type in AXES:
                self.axis = None if self.axis == event.type else event.type
                self._sample(context, event)
                self._update_header(context)
                tag_redraw()
                return {'RUNNING_MODAL'}

            if event.type == 'E' and not event.ctrl:
                wm = context.window_manager
                wm.hb_measure_exact = not wm.hb_measure_exact
                last = measurements_for(context.scene)
                if self.last_label and last:
                    self.last_label = measurement_label(context, last[-1])
                self._update_header(context)
                tag_redraw()
                return {'RUNNING_MODAL'}

            if event.type == 'C' and event.ctrl:
                if self.last_label:
                    context.window_manager.clipboard = self.last_label
                    self.report({'INFO'}, f"Copied {self.last_label}")
                return {'RUNNING_MODAL'}

            if event.type == 'DEL':
                if self.hover is not None:
                    remove_measurement(self.hover)
                    self.hover = None
                    self._pick_hover(context, event)
                self._update_header(context)
                tag_redraw()
                return {'RUNNING_MODAL'}

            if event.type == 'BACK_SPACE':
                # Whatever is half-placed first, then the last finished one.
                if self.points:
                    self._reset_pending(None)
                else:
                    pop_measurement(context.scene)
                self._update_header(context)
                tag_redraw()
                return {'RUNNING_MODAL'}

            if event.type == 'RIGHTMOUSE' and self.points:
                # Drop the half-placed reading and stay in the tool, so
                # the next pair of clicks reads again. A quick reading
                # stays in the header until the next one starts.
                label = None
                if self.mode == 'QUICK' and self.cursor is not None:
                    label = quick_label(context, self.points[0], self.cursor)
                self._reset_pending(label)
                self._sample(context, event)
                self._update_header(context)
                tag_redraw()
                return {'RUNNING_MODAL'}

            if event.type in {'ESC', 'RIGHTMOUSE'}:
                return self._finish(context)

        return {'RUNNING_MODAL'}

    def _finish(self, context):
        global _active
        _active = None
        if context.area is not None:
            context.area.header_text_set(None)
        tag_redraw()
        return {'FINISHED'}

    def cancel(self, context):
        self._finish(context)


class home_builder_OT_measure_clear(bpy.types.Operator):
    bl_idname = "home_builder.measure_clear"
    bl_label = "Clear Measurements"
    bl_description = "Remove every measurement from this room"
    bl_options = {'REGISTER'}

    all_scenes: bpy.props.BoolProperty(name="Every Room", default=False)

    def execute(self, context):
        clear_measurements(None if self.all_scenes else context.scene)
        tag_redraw()
        return {'FINISHED'}


# ---- Options form -----------------------------------------------------------

MEASURE_OPTIONS = 'measure_options'


def draw_measure_options(layout, context):
    wm = context.window_manager
    col = layout.column(align=True)
    col.label(text="Start In")
    col.prop(wm, 'hb_measure_mode', text="")

    col = layout.column(align=True)
    col.prop(wm, 'hb_measure_exact')

    col = layout.column(align=True)
    col.separator()
    count = measurement_count(context.scene)
    row = col.row()
    row.enabled = count > 0
    row.operator('home_builder.measure_clear',
                 text=(f"Clear {count} Measurement{'s' if count != 1 else ''}"
                       if count else "Clear Measurements"),
                 icon='TRASH')

    col.separator()
    box = col.box()
    box.label(text="Snapping follows the magnet menu", icon='SNAP_ON')
    box.label(text="Hold Ctrl to invert it while measuring")
    box.label(text="Alt+M or Q: Quick XYZ (X, Y and Z at once)")
    box.label(text="Q or Tab keeps a point already placed")


# ---- Registration -----------------------------------------------------------

classes = (
    home_builder_OT_measure,
    home_builder_OT_measure_clear,
)


@bpy.app.handlers.persistent
def _clear_on_load(*args):
    clear_measurements(None)


# Alt+M starts the tool in Quick XYZ. Alt+M is free in the 3D View and
# Object Mode keymaps, and sits next to the M of Measure.
_addon_keymaps = []


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(home_builder_OT_measure.bl_idname, 'M', 'PRESS',
                              alt=True)
    kmi.properties.quick = True
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    bpy.types.WindowManager.hb_measure_mode = bpy.props.EnumProperty(
        name="Measure Mode",
        items=[('LINEAR', "Distance", "Straight-line distance between two points"),
               ('ANGULAR', "Angle", "Angle at a corner between two arms"),
               ('QUICK', "Quick XYZ",
                "X, Y and Z distances between two points, nothing left behind")],
        default='LINEAR')
    bpy.types.WindowManager.hb_measure_exact = bpy.props.BoolProperty(
        name="Exact Values",
        description=("Show measurements unrounded instead of to the "
                     "nearest sixteenth. Press E while measuring to switch"),
        default=False,
        update=lambda self, context: tag_redraw())
    for cls in classes:
        bpy.utils.register_class(cls)
    _register_keymaps()

    global _draw_handle
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')

    if _clear_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_clear_on_load)

    from . import room_palette
    room_palette.register_tool_options(MEASURE_OPTIONS, draw_measure_options)
    room_palette.register_tool_badge('home_builder.measure',
                                     lambda scene: measurement_count(scene))


def unregister():
    global _draw_handle, _active
    _active = None
    clear_measurements(None)
    _unregister_keymaps()

    from . import room_palette
    room_palette.unregister_tool_options(MEASURE_OPTIONS)
    room_palette.unregister_tool_badge('home_builder.measure')

    if _clear_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_clear_on_load)

    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    del bpy.types.WindowManager.hb_measure_mode
    del bpy.types.WindowManager.hb_measure_exact
