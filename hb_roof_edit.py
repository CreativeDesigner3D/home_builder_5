"""Edit Roof: shape a level's roof right in the viewport.

The roof and each of its pieces (cross gables, shed dormers - see
hb_roofs) are drawn as outlines on the plan, with grips to drag:

* Edge grips at the middle of each side move that side. They snap to
  the faces of the level's walls and to the other outlines' edges (hold
  Ctrl to place freely). Dragging the main roof's edges gives it a
  custom footprint.
* Drag inside a piece to move it whole.
* The pitch grip on a ridge raises or lowers it: the pitch, in whole
  steps of 12 (Shift for quarter steps).
* Eave grips set where a piece's slopes meet its walls - or a shed
  dormer's front wall height - and how far the main roof's eaves sit
  above its walls.
* G, D or A draws a new cross gable, shed dormer or gable dormer (a
  dormer is drawn on the roof's slope): click two opposite
  corners on the plan, or drag from one to the other. Two clicks along
  one wall make the piece's front that wide, running back to the main
  ridge.

While a grip is dragged only the outlines move; the roof is rebuilt once
on release, as its own undo step. EditSession holds all of it in plan
and screen terms, so it runs without a viewport; the operator feeds it
mouse events and draws it.
"""

import math

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from . import hb_house, hb_roofs, units

GRIP_PX = 6.0               # half the size of a grip, times the UI scale
PICK_PX = 12.0              # how near the cursor must be to take a grip
SNAP_PX = 12.0              # how near an edge comes before it snaps
MIN_SIZE = 0.3              # a piece or footprint is at least this wide
FONT_SIZE = 12.0

MAIN_COLOR = (0.95, 0.95, 0.95, 0.9)
PIECE_COLOR = (1.0, 0.6, 0.2, 0.9)
ACTIVE_COLOR = (1.0, 0.85, 0.35, 1.0)
RIDGE_COLOR = (0.55, 0.85, 1.0, 0.85)
DRAW_COLOR = (0.45, 1.0, 0.55, 1.0)
GRIP_COLORS = {'edge': (1.0, 1.0, 1.0, 1.0), 'pitch': (0.45, 0.8, 1.0, 1.0),
               'eave': (0.45, 1.0, 0.55, 1.0)}
HOVER_COLOR = (1.0, 0.95, 0.2, 1.0)
LABEL_BG = (0.08, 0.08, 0.08, 0.85)

HINT = ("Edit Roof: drag grips or pieces   G: draw cross gable   D: draw shed dormer   "
        "A: draw gable dormer   R: turn ridge   X: remove piece   Ctrl: no snapping   "
        "Shift: fine   Enter / Esc: done")

PIECE_WORDS = {'GABLE': "cross gable", 'SHED': "shed dormer", 'DORMER': "gable dormer"}
DRAWN = {'GABLE': "Draw Cross Gable", 'SHED': "Draw Shed Dormer", 'DORMER': "Draw Gable Dormer"}

# Viewport navigation passes through even mid-drawing
NAVIGATION = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE',
              'WHEELOUTMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'NDOF_MOTION'}

SIDES = ('x0', 'y0', 'x1', 'y1')


# =============================================================================
# VIEW: BETWEEN THE PLAN AND THE SCREEN
# =============================================================================

class View:
    """A viewport's projection: 3D points to region pixels, and the ray
    under a pixel. Made from a region and its view (View.of), or any
    perspective matrix."""

    def __init__(self, matrix, width, height):
        self.m = matrix.copy()
        self.inv = matrix.inverted()
        self.w, self.h = width, height

    @classmethod
    def of(cls, region, rv3d):
        return cls(rv3d.perspective_matrix, region.width, region.height)

    def to_2d(self, p):
        v = self.m @ Vector((p[0], p[1], p[2], 1.0))
        if v.w <= 1e-6:
            return None                 # behind the eye
        return Vector(((v.x / v.w * 0.5 + 0.5) * self.w, (v.y / v.w * 0.5 + 0.5) * self.h))

    def ray(self, mx, my):
        x, y = mx / self.w * 2.0 - 1.0, my / self.h * 2.0 - 1.0
        a = self.inv @ Vector((x, y, -1.0, 1.0))
        b = self.inv @ Vector((x, y, 1.0, 1.0))
        a, b = a.xyz / a.w, b.xyz / b.w
        return a, (b - a).normalized()

    def on_plane(self, mx, my, z):
        """Where the ray under a pixel meets the level plane at z."""
        o, d = self.ray(mx, my)
        if abs(d.z) < 1e-9:
            return None
        t = (z - o.z) / d.z
        return o + d * t if t > 0 else None

    def on_vertical(self, mx, my, point):
        """Height on the vertical line through point nearest the ray
        under a pixel, or None looking straight along it."""
        o, d = self.ray(mx, my)
        w0 = Vector(point) - o
        b = d.z                         # line direction (0, 0, 1) . d
        denom = 1.0 - b * b
        if denom < 1e-4:
            return None
        s = (b * d.dot(w0) - w0.z) / denom
        return point[2] + s

    def px_size(self, p, px):
        """World length of px pixels at point p on its level plane."""
        a = self.to_2d(p)
        if a is None:
            return 0.0
        q = self.on_plane(a.x + px, a.y, p[2])
        return (q - Vector(p)).length if q is not None else 0.0


# =============================================================================
# THE ROOF'S OUTLINES AND GRIPS
# =============================================================================

def _imperial(scene):
    return scene.unit_settings.system != 'METRIC'


def round_length(scene, value, fine=False):
    """A length rounded the way a drag lands: whole inches (quarter with
    fine) or centimetres (millimetres)."""
    step = (units.inch(0.25) if fine else units.inch(1)) if _imperial(scene) else (0.001 if fine else 0.01)
    return round(value / step) * step


def format_length(scene, value):
    if not _imperial(scene):
        return units.unit_to_string(scene.unit_settings, value)
    inches = round(units.meter_to_inch(abs(value)) * 4) / 4
    feet, rest = divmod(inches, 12)
    sign = "-" if value < 0 else ""
    if feet:
        return f"{sign}{int(feet)}' {units.format_number(rest)}\""
    return f"{sign}{units.format_number(rest)}\""


def main_rect(frame):
    """The main roof's plan rectangle (x0, y0, x1, y1): the walls' outline
    or its custom footprint."""
    if frame['along_x']:
        return (frame['v0'], frame['u0'], frame['v1'], frame['u1'])
    return (frame['u0'], frame['v0'], frame['u1'], frame['v1'])


def _ring(rect, z):
    x0, y0, x1, y1 = rect
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def _edge_mid(rect, side, z):
    x0, y0, x1, y1 = rect
    if side in ('x0', 'x1'):
        return Vector((rect[SIDES.index(side)], (y0 + y1) / 2.0, z))
    return Vector(((x0 + x1) / 2.0, rect[SIDES.index(side)], z))


def piece_rect(piece):
    return (piece.x0, piece.y0, piece.x1, piece.y1)


def outlines(scene, level):
    """What Edit Roof draws and grips, or None without a roof:
    {'frame', 'main': {...}, 'pieces': [{...}]}. Each outline has its
    'rect' and plan height 'z', 'lines' (3D segments: the ring, ridges,
    gable rakes) and 'grips' [(kind, side, point)]."""
    roof = level.roof
    frame = hb_roofs.roof_frame(scene, level) if roof.enabled else None
    if frame is None:
        return None
    w = lambda u, v, z: Vector(hb_roofs._world(frame, u, v, z))
    plate = frame['plate']
    rect = main_rect(frame)
    u0, u1, v0, v1, uc = frame['u0'], frame['u1'], frame['v0'], frame['v1'], frame['uc']
    vc = (v0 + v1) / 2.0
    ring = _ring(rect, plate)
    lines = [(ring[i], ring[(i + 1) % 4]) for i in range(4)]
    ridges = []
    grips = [('edge', s, _edge_mid(rect, s, plate)) for s in SIDES]
    if roof.style == 'HIP':
        h = frame['half']
        ra, rb = (v0 + h, v1 - h) if v1 - v0 >= 2 * h else (vc, vc)
        zr = plate + (h if v1 - v0 >= 2 * h else (v1 - v0) / 2.0) * frame['p']
        r0, r1 = w(uc, ra, zr), w(uc, rb, zr)
        ridges.append((r0, r1))
        for (cu, cv), r in (((u0, v0), r0), ((u1, v0), r0), ((u0, v1), r1), ((u1, v1), r1)):
            ridges.append((w(cu, cv, plate), r))
        grips.append(('pitch', None, (r0 + r1) / 2.0))
    elif frame.get('ends'):
        # A roof with sloped ends: the lines it folds along
        ridges.extend((w(*a), w(*b)) for a, b in hb_roofs.end_surface_edges(frame))
    else:
        under = frame['under']
        ridges.append((w(uc, v0, frame['ridge_z']), w(uc, v1, frame['ridge_z'])))
        for v in (v0, v1):
            ridges.extend((w(a, v, za), w(b, v, zb)) for (a, za), (b, zb) in zip(under, under[1:]))
        if roof.style == 'GABLE':
            grips.append(('pitch', None, w(uc, vc, frame['ridge_z'])))
    # At a front corner: the middle of the front is the edge grip's
    grips.append(('eave', None, w(u0, v0, plate)))
    main = {'rect': rect, 'z': plate, 'lines': lines, 'ridges': ridges, 'grips': grips,
            'label': "Roof"}

    cross, sheds = hb_roofs.piece_dormers(frame, roof, level)
    described = {d['index']: d for d in cross + sheds}
    pieces = []
    for index, piece in enumerate(roof.pieces):
        z = level.elevation + piece.eave_height
        prect = piece_rect(piece)
        ring = _ring(prect, z)
        out = {'rect': prect, 'z': z, 'lines': [(ring[i], ring[(i + 1) % 4]) for i in range(4)],
               'ridges': [], 'grips': [('edge', s, _edge_mid(prect, s, z)) for s in SIDES],
               'label': piece.name}
        d = described.get(index)
        if d is not None:
            front, back = d['u_front'], (min if d['sign'] > 0 else max)(
                (piece.y0, piece.y1) if frame['along_x'] else (piece.x0, piece.x1))
            if piece.kind in ('GABLE', 'DORMER'):
                pvc, _half, _p, pplate, ridge = hb_roofs.dormer_dims(d, roof)
                top = w(front, pvc, ridge)
                out['ridges'] = [(top, w(back, pvc, ridge)),
                                 (w(front, d['v0'], pplate), top), (w(front, d['v1'], pplate), top)]
                # The pitch grip sits back along the ridge: at its front end
                # it would hide the front edge's grip, seen from above
                along = front + (back - front) * 0.3
                out['grips'] += [('pitch', None, w(along, pvc, ridge)),
                                 ('eave', None, w(front, d['v0'], pplate))]
            else:
                out['grips'].append(('eave', None, w(front, d['v0'], d['plate'])))
        pieces.append(out)
    return {'frame': frame, 'main': main, 'pieces': pieces}


def snap_lines(scene, level, out, skip=None):
    """Plan lines an edge snaps to: ({x values}, {y values}) of the
    level's wall faces and the other outlines' edges."""
    from .operators import walls
    xs, ys = set(), set()
    for obj in scene.objects:
        if (obj.get('IS_WALL_BP') and obj.get(hb_house.LEVEL_KEY) == level.uid
                and obj.get('WALL_TYPE') != 'Divider'):
            for _end, _face, p in walls.wall_plan_corners(obj):
                xs.add(round(p.x, 5))
                ys.add(round(p.y, 5))
    targets = [(-1, out['main'])] + list(enumerate(out['pieces']))
    for i, o in targets:
        if i == skip:
            continue
        x0, y0, x1, y1 = o['rect']
        xs.update((x0, x1))
        ys.update((y0, y1))
    return xs, ys


def _nearest(value, candidates, tol):
    best = None
    for c in candidates:
        if abs(c - value) <= tol and (best is None or abs(c - value) < abs(best - value)):
            best = c
    return best


# =============================================================================
# THE SESSION
# =============================================================================

class EditSession:
    """Edit Roof's state for the active level: what the cursor is over,
    and the drag or drawing under way. Feed it region-pixel positions
    with a View; it writes the roof and rebuilds it on release."""

    def __init__(self, scene):
        self.scene = hb_house.house_scene_of(scene) or scene
        self.hover = None           # (target, kind, side) - target -1 is the main roof
        self.drag = None
        self.draw_kind = None       # 'GABLE' / 'SHED' / 'DORMER' while drawing a piece
        self.drawing = None         # (start, end) plan points of the rectangle drawn
        self.corner = None          # where the first corner would go, before the click
        self.second_click = False   # the drawing's end was clicked (not dragged to)
        self.warning = ""           # why the last drawing made nothing
        self.message = ""           # what the last drag shows: a size, a pitch...
        self.label_at = None

    # ---- what is under the cursor ------------------------------------------------

    def level(self):
        return hb_house.active_level_of_scene(self.scene)

    def outlines(self):
        level = self.level()
        return outlines(self.scene, level) if level is not None else None

    def pick(self, view, mx, my):
        """(target, kind, side) under the cursor, or None: the nearest grip,
        else the piece whose outline it is inside."""
        out = self.outlines()
        if out is None:
            return None
        s = _ui_scale()
        best, best_d = None, PICK_PX * s
        targets = [(-1, out['main'])] + list(enumerate(out['pieces']))
        for target, o in targets:
            for kind, side, p in o['grips']:
                q = view.to_2d(p)
                if q is None:
                    continue
                d = (q - Vector((mx, my))).length
                # Height grips sit on top of edge grips at the ends: they win ties
                if d < best_d or (d <= best_d + 0.5 and best is not None and best[1] == 'edge' and kind != 'edge'):
                    best, best_d = (target, kind, side), d
        if best is not None:
            return best
        active = self.level().roof.active_piece_index
        inside = []
        for target, o in enumerate(out['pieces']):
            p = view.on_plane(mx, my, o['z'])
            if p is None:
                continue
            x0, y0, x1, y1 = o['rect']
            if min(x0, x1) <= p.x <= max(x0, x1) and min(y0, y1) <= p.y <= max(y0, y1):
                inside.append((target != active, abs(x1 - x0) * abs(y1 - y0), target))
        if inside:
            return (min(inside)[2], 'move', None)
        return None

    # ---- dragging ------------------------------------------------------------------

    def _owner(self, target):
        roof = self.level().roof
        return roof if target < 0 else roof.pieces[target]

    def _snapshot(self, target):
        owner = self._owner(target)
        keys = (('use_extents', 'ext_x0', 'ext_x1', 'ext_y0', 'ext_y1', 'pitch', 'eave_height')
                if target < 0 else SIDES + ('pitch', 'eave_height'))
        return {k: getattr(owner, k) for k in keys}

    def press(self, view, mx, my):
        """A click: start drawing, or take what is under the cursor. True
        when it took the click."""
        level = self.level()
        if level is None or not level.roof.enabled:
            return False
        if self.draw_kind is not None:
            out = self.outlines()
            if out is None:
                return False
            p = self._draw_point(view, mx, my, out)
            if p is None:
                return False
            p = self._snap_point(view, p, out, ctrl=False)
            if self.drawing is None:
                self.drawing = (p, p)
                self.second_click = False
                self.warning = ""
            else:
                # The opposite corner's click: finished on its release
                self.drawing = (self.drawing[0], p)
                self.second_click = True
            return True
        hit = self.pick(view, mx, my)
        if hit is None:
            return False
        target, kind, side = hit
        if target >= 0:
            level.roof.active_piece_index = target
        out = self.outlines()
        o = out['main'] if target < 0 else out['pieces'][target]
        point = next((p for k, s, p in o['grips'] if k == kind and s == side), None)
        grab = view.on_plane(mx, my, o['z'])
        self.drag = {'target': target, 'kind': kind, 'side': side, 'point': point,
                     'grab': grab, 'rect': o['rect'], 'z': o['z'],
                     'start': self._snapshot(target), 'moved': False}
        return True

    def piece_word(self):
        return PIECE_WORDS.get(self.draw_kind, "cross gable")

    def _draw_point(self, view, mx, my, out):
        """Where the cursor is on the plan while drawing: on the main
        roof's slope for a dormer (it stands on the roof), else on the
        level of the walls' tops."""
        if self.draw_kind in ('SHED', 'DORMER'):
            p = self._on_roof(view, mx, my, out)
            if p is not None:
                return p
        return view.on_plane(mx, my, out['main']['z'])

    def _surface_z(self, out, x, y):
        frame = out['frame']
        u, v = hb_roofs._uv(frame, (x, y))
        return hb_roofs.roof_top_z_at(frame, self.level().roof, u, v)

    def _on_roof(self, view, mx, my, out):
        """Where the ray under the cursor meets the main roof's top, or
        None off it."""
        frame = out['frame']
        rect = out['main']['rect']
        o, d = view.ray(mx, my)
        if abs(d.z) < 1e-6:
            return None
        hi, lo = frame['ridge_z'] + 3.0, frame['plate'] - 3.0
        t0, t1 = (hi - o.z) / d.z, (lo - o.z) / d.z
        if t1 < t0:
            t0, t1 = t1, t0
        t0 = max(t0, 0.0)
        above = lambda t: (o + d * t).z - self._surface_z(out, (o + d * t).x, (o + d * t).y)
        steps = 64
        prev_t, prev = t0, above(t0)
        for i in range(1, steps + 1):
            t = t0 + (t1 - t0) * i / steps
            cur = above(t)
            if (prev > 0) != (cur > 0):
                a, b = prev_t, t
                for _ in range(30):
                    m = (a + b) / 2.0
                    if (above(m) > 0) == (prev > 0):
                        a = m
                    else:
                        b = m
                p = o + d * ((a + b) / 2.0)
                x0, y0, x1, y1 = rect
                if min(x0, x1) - 0.5 <= p.x <= max(x0, x1) + 0.5 and min(y0, y1) - 0.5 <= p.y <= max(y0, y1) + 0.5:
                    return p
                return None
            prev_t, prev = t, cur
        return None

    def drawing_ring(self):
        """The rectangle being drawn, its corners on the roof's slope for a
        dormer."""
        a, b = self.drawing
        ring = _ring((a.x, a.y, b.x, b.y), a.z)
        if self.draw_kind in ('SHED', 'DORMER'):
            out = self.outlines()
            if out is not None:
                ring = [Vector((x, y, self._surface_z(out, x, y))) for x, y, _z in ring]
        return ring

    def prompt(self):
        """The status bar's line: what a click does now."""
        if self.draw_kind is None:
            return HINT
        if self.drawing is None:
            lead = f"{self.warning}   " if self.warning else ""
            return (f"{lead}New {self.piece_word()}: click its first corner (or drag from it to "
                    f"the opposite corner)   Ctrl: no snapping   Esc: stop")
        return f"New {self.piece_word()}: click the opposite corner   Ctrl: no snapping   Esc: stop"

    def move(self, view, mx, my, ctrl=False, shift=False):
        if self.draw_kind is not None and self.drawing is None:
            # Waiting for the first corner: show where it would snap
            out = self.outlines()
            p = self._draw_point(view, mx, my, out) if out else None
            if p is not None:
                self.corner = self._snap_point(view, p, out, ctrl)
                self.message = self.warning or f"New {self.piece_word()}: click the first corner"
                self.label_at = self.corner
            return
        if self.drawing is not None:
            out = self.outlines()
            p = self._draw_point(view, mx, my, out) if out else None
            if p is not None:
                p = self._snap_point(view, p, out, ctrl)
                self.drawing = (self.drawing[0], p)
                a, b = self.drawing
                self.message = (f"{format_length(self.scene, abs(b.x - a.x))} x "
                                f"{format_length(self.scene, abs(b.y - a.y))}")
                self.label_at = b
            return
        if self.drag is None:
            self.hover = self.pick(view, mx, my)
            return
        dr = self.drag
        dr['moved'] = True
        kind = dr['kind']
        if kind == 'edge':
            self._drag_edge(view, mx, my, ctrl, shift)
        elif kind == 'move':
            self._drag_move(view, mx, my, ctrl, shift)
        elif kind == 'pitch':
            self._drag_pitch(view, mx, my, shift)
        elif kind == 'eave':
            self._drag_eave(view, mx, my, ctrl, shift)

    def _tol(self, view, point):
        return view.px_size(point, SNAP_PX * _ui_scale())

    def _snap_value(self, view, value, axis, point, ctrl, shift, skip):
        if not ctrl:
            xs, ys = snap_lines(self.scene, self.level(), self.outlines(), skip=skip)
            hit = _nearest(value, xs if axis == 'x' else ys, self._tol(view, point))
            if hit is not None:
                return hit
        return round_length(self.scene, value, shift)

    def _snap_point(self, view, p, out, ctrl):
        if ctrl:
            return Vector((round_length(self.scene, p.x), round_length(self.scene, p.y), p.z))
        xs, ys = snap_lines(self.scene, self.level(), out)
        tol = self._tol(view, p)
        x, y = _nearest(p.x, xs, tol), _nearest(p.y, ys, tol)
        return Vector((x if x is not None else round_length(self.scene, p.x),
                       y if y is not None else round_length(self.scene, p.y), p.z))

    def _write_rect(self, target, rect):
        level = self.level()
        if target < 0:
            roof = level.roof
            roof['use_extents'] = True
            for side, value in zip(SIDES, rect):
                roof['ext_' + side] = value
        else:
            piece = level.roof.pieces[target]
            for side, value in zip(SIDES, rect):
                piece[side] = value

    def _size_message(self, rect, at):
        x0, y0, x1, y1 = rect
        self.message = (f"{format_length(self.scene, abs(x1 - x0))} x "
                        f"{format_length(self.scene, abs(y1 - y0))}")
        self.label_at = at

    def _drag_edge(self, view, mx, my, ctrl, shift):
        dr = self.drag
        p = view.on_plane(mx, my, dr['z'])
        if p is None:
            return
        side = dr['side']
        axis = side[0]
        i = SIDES.index(side)
        rect = list(dr['rect'])
        value = self._snap_value(view, p.x if axis == 'x' else p.y, axis, p, ctrl, shift,
                                 dr['target'])
        other = rect[(i + 2) % 4]
        # Keep the sides apart (whichever way round they are stored)
        if rect[i] >= other:
            value = max(value, other + MIN_SIZE)
        else:
            value = min(value, other - MIN_SIZE)
        rect[i] = value
        self._write_rect(dr['target'], rect)
        self._size_message(rect, _edge_mid(rect, side, dr['z']))

    def _drag_move(self, view, mx, my, ctrl, shift):
        dr = self.drag
        p = view.on_plane(mx, my, dr['z'])
        if p is None or dr['grab'] is None:
            return
        dx, dy = p.x - dr['grab'].x, p.y - dr['grab'].y
        x0, y0, x1, y1 = dr['rect']
        moved = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
        if ctrl:
            dx = round_length(self.scene, dx, shift)
            dy = round_length(self.scene, dy, shift)
        else:
            xs, ys = snap_lines(self.scene, self.level(), self.outlines(), skip=dr['target'])
            tol = self._tol(view, p)
            for axis, cands in (('x', xs), ('y', ys)):
                lo, hi = (moved[0], moved[2]) if axis == 'x' else (moved[1], moved[3])
                fixes = [c - e for e in (lo, hi) for c in [_nearest(e, cands, tol)] if c is not None]
                fix = min(fixes, key=abs) if fixes else None
                if axis == 'x':
                    dx = dx + fix if fix is not None else round_length(self.scene, dx, shift)
                else:
                    dy = dy + fix if fix is not None else round_length(self.scene, dy, shift)
        rect = (x0 + dx, y0 + dy, x1 + dx, y1 + dy)
        self._write_rect(dr['target'], rect)
        self.message = self._owner(dr['target']).name
        self.label_at = Vector(((rect[0] + rect[2]) / 2.0, (rect[1] + rect[3]) / 2.0, dr['z']))

    def _drag_pitch(self, view, mx, my, shift):
        dr = self.drag
        z = view.on_vertical(mx, my, dr['point'])
        if z is None:
            return
        level = self.level()
        frame = hb_roofs.roof_frame(self.scene, level)
        if dr['target'] < 0:
            plate, half = frame['plate'], frame['half']
        else:
            piece = level.roof.pieces[dr['target']]
            sides = (piece.x0, piece.x1) if frame['along_x'] else (piece.y0, piece.y1)
            plate = level.elevation + piece.eave_height
            half = abs(sides[1] - sides[0]) / 2.0
        if half < 1e-6:
            return
        step = 0.25 if shift else 1.0
        pitch = round((z - plate) / half * 12.0 / step) * step
        pitch = min(max(pitch, 1.0), 24.0)
        self._owner(dr['target'])['pitch'] = pitch
        self.message = f"{units.format_number(pitch)} in 12"
        self.label_at = Vector(dr['point'])

    def _drag_eave(self, view, mx, my, ctrl, shift):
        dr = self.drag
        z = view.on_vertical(mx, my, dr['point'])
        if z is None:
            return
        level = self.level()
        if dr['target'] < 0:
            frame = hb_roofs.roof_frame(self.scene, level)
            base = frame['base']
            value = round_length(self.scene, z - base, shift)
            if not ctrl and abs(z - base) < units.inch(2):
                value = 0.0             # down on the walls
            level.roof['eave_height'] = value
            self.message = f"Eaves {format_length(self.scene, value)} above the walls"
        else:
            piece = level.roof.pieces[dr['target']]
            value = round_length(self.scene, z - level.elevation, shift)
            wall = hb_house.exterior_wall_height(level)
            if not ctrl and piece.kind == 'GABLE' and abs(value - wall) < units.inch(2):
                value = wall            # onto the tops of the walls
            value = max(value, MIN_SIZE)
            piece['eave_height'] = value
            what = "Front wall" if piece.kind in ('SHED', 'DORMER') else "Eaves"
            self.message = f"{what} {format_length(self.scene, value)}"
        p = Vector(dr['point'])
        self.label_at = Vector((p.x, p.y, z))

    def release(self):
        """Let go: finish the drawing or the drag and rebuild the roof.
        Returns what changed, or None."""
        level = self.level()
        if self.drawing is not None:
            a, b = self.drawing
            wide, deep = abs(b.x - a.x) >= MIN_SIZE, abs(b.y - a.y) >= MIN_SIZE
            if not (wide and deep) and not self.second_click:
                return None             # a click, not a drag: wait for the opposite corner
            kind = self.draw_kind
            self.drawing = None
            self.second_click = False
            self.message = ""
            if wide and deep:
                rect = (a.x, a.y, b.x, b.y)
            elif wide or deep:
                rect = self.front_line_rect(a, b)
                if rect is None:
                    self.warning = (f"A {self.piece_word()} faces out from the ridge: click along "
                                    f"a wall that runs the same way as the ridge.")
                    return None
            else:
                self.warning = "Those clicks were in one spot."
                return None
            self.draw_kind = self.corner = None
            self.warning = ""
            hb_roofs.add_piece(self.scene, level, kind, rect, fit_shed=False)
            return DRAWN[kind]
        dr, self.drag = self.drag, None
        self.message = ""
        if dr is None or not dr['moved']:
            return None
        hb_roofs.rebuild_roof(self.scene, level)
        return {'edge': "Move Roof Edge", 'move': "Move Roof Piece",
                'pitch': "Change Roof Pitch", 'eave': "Change Eave Height"}[dr['kind']]

    def front_line_rect(self, a, b):
        """Two clicks along one wall: a piece that wide, its front on that
        line and running back to the main ridge - or None when the line
        runs across the ridge (a piece faces out from it)."""
        frame = hb_roofs.roof_frame(self.scene, self.level())
        if frame is None:
            return None
        if frame['along_x']:
            (v0, v1), u = (a.x, b.x), (a.y + b.y) / 2.0
        else:
            (v0, v1), u = (a.y, b.y), (a.x + b.x) / 2.0
        if abs(v1 - v0) < MIN_SIZE or abs(u - frame['uc']) < MIN_SIZE:
            return None
        back = frame['uc']
        if frame['along_x']:
            return (v0, u, v1, back)
        return (u, v0, back, v1)

    def cancel(self):
        """Esc mid-drag: put it back as it was. True when something was
        under way."""
        if self.drawing is not None or self.draw_kind is not None:
            self.drawing = self.draw_kind = self.corner = None
            self.second_click = False
            self.message = self.warning = ""
            return True
        if self.drag is None:
            return False
        dr, self.drag = self.drag, None
        owner = self._owner(dr['target'])
        for k, v in dr['start'].items():
            owner[k] = v
        self.message = ""
        return True

    # ---- keys ----------------------------------------------------------------------

    def start_drawing(self, kind):
        self.cancel()
        self.draw_kind = kind

    def remove_active(self):
        level = self.level()
        roof = level.roof
        if not 0 <= roof.active_piece_index < len(roof.pieces):
            return False
        front = roof.pieces[roof.active_piece_index].front_wall
        if front is not None:
            hb_roofs._delete_tree(front)
        roof.pieces.remove(roof.active_piece_index)
        roof.active_piece_index = max(0, min(roof.active_piece_index, len(roof.pieces) - 1))
        hb_roofs.rebuild_roof(self.scene, level)
        return True

    def turn_ridge(self):
        level = self.level()
        frame = hb_roofs.roof_frame(self.scene, level)
        if frame is None:
            return False
        level.roof.ridge = 'Y' if frame['along_x'] else 'X'
        return True


# =============================================================================
# DRAWING
# =============================================================================

def _ui_scale():
    try:
        return bpy.context.preferences.system.ui_scale
    except AttributeError:
        return 1.0


def _segments(shader, pts, color, width):
    if not pts:
        return
    gpu.state.line_width_set(width)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)


def _square(shader, c, r, color):
    x, y = c
    shader.uniform_float("color", (0.05, 0.05, 0.05, 0.9))
    batch_for_shader(shader, 'TRI_FAN', {"pos": [(x - r - 1, y - r - 1), (x + r + 1, y - r - 1),
                                                 (x + r + 1, y + r + 1), (x - r - 1, y + r + 1)]}).draw(shader)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'TRI_FAN', {"pos": [(x - r, y - r), (x + r, y - r),
                                                 (x + r, y + r), (x - r, y + r)]}).draw(shader)


def _diamond(shader, c, r, color):
    x, y = c
    r = r * 1.35
    shader.uniform_float("color", (0.05, 0.05, 0.05, 0.9))
    batch_for_shader(shader, 'TRI_FAN', {"pos": [(x, y - r - 1.5), (x + r + 1.5, y),
                                                 (x, y + r + 1.5), (x - r - 1.5, y)]}).draw(shader)
    shader.uniform_float("color", color)
    batch_for_shader(shader, 'TRI_FAN', {"pos": [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]}).draw(shader)


def _label(shader, at, text, s):
    blf.size(0, FONT_SIZE * s)
    tw, th = blf.dimensions(0, text)
    pad = 4 * s
    x, y = at.x + 10 * s, at.y + 10 * s
    shader.uniform_float("color", LABEL_BG)
    batch_for_shader(shader, 'TRI_FAN', {"pos": [(x - pad, y - pad), (x + tw + pad, y - pad),
                                                 (x + tw + pad, y + th + pad),
                                                 (x - pad, y + th + pad)]}).draw(shader)
    blf.position(0, x, y, 0)
    blf.color(0, 1.0, 1.0, 1.0, 1.0)
    blf.draw(0, text)


def draw(session, region, rv3d):
    """Draw the outlines, grips and the drag's readout over the viewport."""
    out = session.outlines()
    if out is None:
        return
    view = View.of(region, rv3d)
    s = _ui_scale()
    flat = lambda segs: [q for a, b in segs for q in (view.to_2d(a), view.to_2d(b))
                         if None not in (view.to_2d(a), view.to_2d(b))]
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    level = session.level()
    active = level.roof.active_piece_index
    _segments(shader, flat(out['main']['ridges']), RIDGE_COLOR, 1.5)
    _segments(shader, flat(out['main']['lines']), MAIN_COLOR, 2.0)
    for i, o in enumerate(out['pieces']):
        _segments(shader, flat(o['ridges']), RIDGE_COLOR, 1.5)
        _segments(shader, flat(o['lines']), ACTIVE_COLOR if i == active else PIECE_COLOR,
                  3.0 if i == active else 2.0)
    marks = []
    if session.drawing is not None:
        a, b = session.drawing
        ring = session.drawing_ring()
        _segments(shader, flat([(ring[i], ring[(i + 1) % 4]) for i in range(4)]), DRAW_COLOR, 2.5)
        marks = [a, b]
    elif session.draw_kind is not None and session.corner is not None:
        marks = [session.corner]
    gpu.state.line_width_set(1.0)
    # The corners being drawn: a cross where each one snaps
    for m in marks:
        q = view.to_2d(m)
        if q is None:
            continue
        r = GRIP_PX * s * 2.2
        _segments(shader, [(q.x - r, q.y), (q.x + r, q.y), (q.x, q.y - r), (q.x, q.y + r)],
                  DRAW_COLOR, 2.0)
        _diamond(shader, q, GRIP_PX * s * 0.8, DRAW_COLOR)
    gpu.state.line_width_set(1.0)

    # Grips: squares for edges, diamonds for heights
    hover = session.hover if session.drag is None else (
        session.drag['target'], session.drag['kind'], session.drag['side'])
    for target, o in [(-1, out['main'])] + list(enumerate(out['pieces'])):
        for kind, side, p in o['grips']:
            q = view.to_2d(p)
            if q is None:
                continue
            hot = hover == (target, kind, side)
            color = HOVER_COLOR if hot else GRIP_COLORS[kind]
            (_square if kind == 'edge' else _diamond)(shader, q, GRIP_PX * s * (1.25 if hot else 1.0), color)
        # Each piece's name at its middle
        if target >= 0:
            x0, y0, x1, y1 = o['rect']
            q = view.to_2d(((x0 + x1) / 2.0, (y0 + y1) / 2.0, o['z']))
            if q is not None:
                blf.size(0, FONT_SIZE * s * 0.9)
                tw, _th = blf.dimensions(0, o['label'])
                blf.position(0, q.x - tw / 2.0, q.y, 0)
                c = ACTIVE_COLOR if target == active else PIECE_COLOR
                blf.color(0, *c)
                blf.draw(0, o['label'])
    if session.message and session.label_at is not None:
        q = view.to_2d(session.label_at)
        if q is not None:
            _label(shader, q, session.message, s)
    gpu.state.blend_set('NONE')


# =============================================================================
# THE OPERATOR
# =============================================================================

_running = None             # the Edit Roof running, if one is


class HOME_BUILDER_OT_edit_roof(bpy.types.Operator):
    bl_idname = "home_builder.edit_roof"
    bl_label = "Edit Roof"
    bl_description = ("Shape the active level's roof in the viewport: drag its edges, "
                      "ridges and eaves, move its pieces and draw new ones")

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and hb_house.active_level(context) is not None)

    def invoke(self, context, event):
        global _running
        if _running is not None:
            # Already on: the button turns it off
            _running.stop = True
            return {'CANCELLED'}
        level = hb_house.active_level(context)
        if not level.roof.enabled:
            level.roof.enabled = True
            self.report({'INFO'}, "Roof turned on for this level")
        self.session = EditSession(context.scene)
        self.area = context.area
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), None)
        self.window = context.window
        self.stop = False
        _running = self
        self.crosshair = False
        self.status = None
        self.handle = bpy.types.SpaceView3D.draw_handler_add(
            self._draw, (), 'WINDOW', 'POST_PIXEL')
        self._sync(context)
        context.window_manager.modal_handler_add(self)
        self.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _draw(self):
        context = bpy.context
        if context.area != self.area or context.region_data is None:
            return
        try:
            draw(self.session, context.region, context.region_data)
        except ReferenceError:
            pass

    def _sync(self, context):
        """The cursor and status bar follow what a click does: a crosshair
        and drawing prompts while drawing a piece."""
        drawing = self.session.draw_kind is not None
        if drawing != self.crosshair and self.window is not None:
            if drawing:
                self.window.cursor_modal_set('CROSSHAIR')
            else:
                self.window.cursor_modal_restore()
            self.crosshair = drawing
        text = self.session.prompt()
        if text != self.status:
            context.workspace.status_text_set(text)
            self.status = text

    def _finish(self, context):
        global _running
        if _running is self:
            _running = None
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        if self.crosshair and self.window is not None:
            self.window.cursor_modal_restore()
        context.workspace.status_text_set(None)
        self.area.tag_redraw()

    def _view(self, context):
        rv3d = context.region_data if context.region == self.region else self.region.data
        return View.of(self.region, rv3d)

    def _in_region(self, event):
        r = self.region
        x, y = event.mouse_x - r.x, event.mouse_y - r.y
        return (0 <= x < r.width and 0 <= y < r.height), x, y

    @staticmethod
    def _push_undo(message):
        try:
            bpy.ops.ed.undo_push(message=message)
        except RuntimeError:
            pass

    def modal(self, context, event):
        if self.stop:
            self.session.cancel()
            self._finish(context)
            return {'FINISHED'}
        result = self._handle(context, event)
        if 'FINISHED' not in result:
            self._sync(context)
        return result

    def _handle(self, context, event):
        session = self.session
        inside, mx, my = self._in_region(event)
        self.area.tag_redraw()
        busy = session.drag is not None or session.drawing is not None

        if event.type == 'MOUSEMOVE':
            if inside or busy:
                session.move(self._view(context), mx, my, event.ctrl, event.shift)
            return {'RUNNING_MODAL'} if busy else {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if not inside:
                    return {'PASS_THROUGH'}
                from .operators import viewport_hud
                if viewport_hud.click_hits_widget(context, self.area, mx, my):
                    return {'PASS_THROUGH'}
                if session.press(self._view(context), mx, my):
                    return {'RUNNING_MODAL'}
                return {'RUNNING_MODAL'} if session.draw_kind else {'PASS_THROUGH'}
            if event.value == 'RELEASE' and busy:
                done = session.release()
                if done:
                    self._push_undo(done)
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.value != 'PRESS':
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if session.cancel():
                return {'RUNNING_MODAL'}
            self._finish(context)
            return {'FINISHED'}
        if event.type in {'RET', 'NUMPAD_ENTER'} and not busy:
            self._finish(context)
            return {'FINISHED'}
        if busy:
            return {'PASS_THROUGH'} if event.type in NAVIGATION else {'RUNNING_MODAL'}
        if event.type == 'G':
            session.start_drawing('GABLE')
            return {'RUNNING_MODAL'}
        if event.type == 'D':
            session.start_drawing('SHED')
            return {'RUNNING_MODAL'}
        if event.type == 'A':
            session.start_drawing('DORMER')
            return {'RUNNING_MODAL'}
        if event.type == 'R':
            if session.turn_ridge():
                self._push_undo("Turn Ridge")
            return {'RUNNING_MODAL'}
        if event.type in {'X', 'DEL'}:
            if session.remove_active():
                self._push_undo("Remove Roof Piece")
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}


classes = (HOME_BUILDER_OT_edit_roof,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
