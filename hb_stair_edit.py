"""Edit Stairs: shape a placed stair right in the viewport.

The stair is drawn as an outline on the plan - its flights and landing -
with grips to drag:

* The start grip, at the foot, sets the tread depth: drag it back for
  deeper treads (a longer stair), forward for shallower ones. The top
  stays where it arrives. The end grip does the same from the top, the
  foot staying put.
* The side grips set the width, the other side staying where it is.
  A side snaps to a wall face it comes near.
* On an L or U stair the turn grip, in the landing, sets where it turns:
  drag it along the first flight and the landing moves a riser at a
  time. Click it to turn the other way.
* Drag inside the outline to move the stair; it snaps along and against
  the walls, as when it was placed. The round grip behind the foot (or
  R) turns it a quarter turn.

The stair is rebuilt as it is dragged, its stairwell once each drag
ends. Enter keeps it all as one undo step, Esc puts the stair back as
it was. StairEdit holds the editing in plan terms, so it runs without a
viewport; the operator feeds it mouse events and draws it.
"""

import math

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from . import hb_house, hb_stairs, units
from .hb_roof_edit import (View, NAVIGATION, GRIP_PX, PICK_PX, SNAP_PX, _ui_scale,
                           _segments, _square, _diamond, _label)
from .units import inch

MIN_TREAD, MAX_TREAD = inch(8), inch(16)
MIN_WIDTH, MAX_WIDTH = inch(24), inch(96)
TURN_PX = 22.0              # how far behind the foot the turn-it grip sits
CLICK_PX = 4.0              # a press that moves less than this is a click

OUTLINE = (0.95, 0.95, 0.95, 0.9)
LANDING = (0.55, 0.85, 1.0, 0.9)
GRIP_COLORS = {'start': (1.0, 1.0, 1.0, 1.0), 'end': (1.0, 1.0, 1.0, 1.0),
               'left': (1.0, 1.0, 1.0, 1.0), 'right': (1.0, 1.0, 1.0, 1.0),
               'turn': (0.45, 0.8, 1.0, 1.0), 'rotate': (0.45, 1.0, 0.55, 1.0)}
HOVER_COLOR = (1.0, 0.95, 0.2, 1.0)

HINT = ("Edit Stairs: drag the ends for tread depth, the sides for width, the landing for where "
        "it turns (click it to flip), inside to move   R: quarter turn   F: flip turn   "
        "Ctrl: no snapping   Shift: fine   Enter: done   Esc: put it back")


def _snapshot(obj):
    return ({k: obj[k] for k in obj.keys() if k.startswith('STAIR_')},
            obj.location.copy(), obj.rotation_euler.z)


def _restore(obj, snap):
    keys, loc, rot = snap
    for k in [k for k in obj.keys() if k.startswith('STAIR_') and k not in keys]:
        del obj[k]
    for k, value in keys.items():
        obj[k] = value
    obj.location = loc
    obj.rotation_euler.z = rot


class StairEdit:
    """Editing one stair: its outline and grips in the world, and what a
    drag of each does to it."""

    def __init__(self, obj):
        self.name = obj.name
        self.start_state = _snapshot(obj)
        scene = obj.users_scene[0] if obj.users_scene else bpy.context.scene
        level = hb_stairs.level_of(obj)
        uids = {level.uid} if level is not None else {lv.uid for lv in scene.hb_house.levels}
        self.faces = hb_stairs.wall_faces(scene, uids)
        self.drag = None
        self.hover = None
        self.message = ""
        self.label_at = None

    @property
    def obj(self):
        return bpy.data.objects.get(self.name)

    # ---- The stair's frame ------------------------------------------------------------

    def frame(self):
        """(origin xy, rotation 2x2, z) from the stair's own transform -
        not matrix_world, which lags a change just made."""
        obj = self.obj
        return (obj.location.xy.copy(), Matrix.Rotation(obj.rotation_euler.z, 2),
                obj.location.z)

    def to_world(self, p):
        o, R, z = self.frame()
        q = o + R @ Vector((p[0], p[1]))
        return Vector((q.x, q.y, z))

    def to_local(self, p):
        o, R, _z = self.frame()
        return R.transposed() @ (Vector((p[0], p[1])) - o)

    def values(self):
        return hb_stairs.values(self.obj)

    def rects(self, v=None):
        """The flights' and landings' outlines in the stair's own frame,
        each [4 points] - none for a curved or spiral stair."""
        from . import hb_stair_build, hb_stair_shapes as shapes
        v = v or self.values()
        if shapes.is_arc(v):
            return [], []
        flights, landings = hb_stair_build.layout(v)
        out = []
        for f in flights:
            pts = [(0.0, 0.0), (f.W, 0.0), (f.W, f.run), (0.0, f.run)]
            out.append([(f.m @ Vector((x, y, 0.0))).to_2d() for x, y in pts])
        lands = [[Vector((x0, y0)), Vector((x1, y0)), Vector((x1, y1)), Vector((x0, y1))]
                 for x0, y0, x1, y1, _z in landings]
        if not lands and v['type'] in ('L_SHAPE', 'U_SHAPE') and flights:
            # Winders: the turn square at the head of the first flight
            r, W = flights[0].run, v['width']
            lands = [[Vector((0.0, r)), Vector((W, r)), Vector((W, r + W)), Vector((0.0, r + W))]]
        return out, lands

    def grips(self):
        """[(kind, world point)]."""
        from . import hb_stair_shapes as shapes
        v = self.values()
        (s, su), (e, eu) = hb_stairs.ends(v)
        out = []
        arc = shapes.is_arc(v)
        if not arc:
            out.append(('start', self.to_world(s)))
            out.append(('end', self.to_world(e)))
            flights, lands = self.rects(v)
            run1 = (flights[0][2] - flights[0][1]).length if flights else 0.0
            out.append(('left', self.to_world((0.0, run1 / 2.0))))
            out.append(('right', self.to_world((v['width'], run1 / 2.0))))
            if v['type'] in ('L_SHAPE', 'U_SHAPE') and lands:
                c = sum(lands[0], Vector((0.0, 0.0))) / 4.0
                out.append(('turn', self.to_world(c)))
        return out

    def rotate_grip(self, view):
        """The turn-it grip: behind the foot, a fixed distance on screen."""
        v = self.values()
        (s, su), _end = hb_stairs.ends(v)
        a = self.to_world(s)
        b = self.to_world(s - su)
        pa, pb = view.to_2d(a), view.to_2d(b)
        if pa is None or pb is None or (pb - pa).length < 1e-6:
            return None
        q = pa + (pb - pa).normalized() * (TURN_PX * _ui_scale())
        return q

    def inside(self, p):
        """Whether a plan point is on the stair's outline."""
        loc = self.to_local(p)
        flights, lands = self.rects()
        for poly in flights + lands:
            xs, ys = [q.x for q in poly], [q.y for q in poly]
            if min(xs) - 1e-4 <= loc.x <= max(xs) + 1e-4 and min(ys) - 1e-4 <= loc.y <= max(ys) + 1e-4:
                return True
        from . import hb_stair_shapes as shapes
        v = self.values()
        if shapes.is_arc(v):
            # Within the ring the treads turn round
            A = shapes.arc_plan(v)
            c = A.point(0.0, 0.0)
            return (loc - c).length <= A.r_out + 0.05
        return False

    def center(self):
        """The middle of the stair's outline, in its own frame."""
        flights, lands = self.rects()
        pts = [q for poly in flights + lands for q in poly]
        if not pts:
            (s, su), (e, eu) = hb_stairs.ends(self.values())
            return (s + e) / 2.0
        xs, ys = [q.x for q in pts], [q.y for q in pts]
        return Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0))

    # ---- Picking and dragging ---------------------------------------------------------

    def pick(self, view, mx, my):
        s = _ui_scale()
        best, best_d = None, PICK_PX * s
        for kind, p in self.grips():
            q = view.to_2d(p)
            if q is None:
                continue
            d = (q - Vector((mx, my))).length
            if d < best_d:
                best, best_d = kind, d
        q = self.rotate_grip(view)
        if q is not None and (q - Vector((mx, my))).length < best_d:
            best = 'rotate'
        if best is None:
            p = view.on_plane(mx, my, self.frame()[2])
            if p is not None and self.inside(p):
                best = 'move'
        return best

    def hover_at(self, view, mx, my):
        self.hover = self.pick(view, mx, my)

    def press(self, view, mx, my):
        """Take the grip (or the stair) under the cursor. True if there was one."""
        kind = self.pick(view, mx, my)
        if kind is None:
            return False
        p = view.on_plane(mx, my, self.frame()[2])
        if p is None:
            return False
        o, R, _z = self.frame()
        v = self.values()
        (s, su), (e, eu) = hb_stairs.ends(v)
        self.drag = {'kind': kind, 'p0': p.to_2d(), 'px0': Vector((mx, my)), 'moved': False,
                     'state': _snapshot(self.obj), 'v': v, 'o': o, 'R': R,
                     'start': (o + R @ s, R @ su), 'end': (o + R @ e, R @ eu)}
        return True

    def move(self, view, mx, my, ctrl=False, shift=False):
        if self.drag is None:
            self.hover_at(view, mx, my)
            return
        d = self.drag
        if not d['moved'] and (Vector((mx, my)) - d['px0']).length < CLICK_PX * _ui_scale():
            return
        d['moved'] = True
        if d['kind'] == 'rotate':
            return
        p = view.on_plane(mx, my, self.frame()[2])
        if p is None:
            return
        _restore(self.obj, d['state'])
        delta = p.to_2d() - d['p0']
        getattr(self, '_drag_' + d['kind'])(view, p.to_2d(), delta, ctrl, shift)
        self._rebuild_mesh()

    def _step(self, shift, ctrl, coarse=inch(0.25), fine=inch(1 / 16)):
        return 0.0 if ctrl else (fine if shift else coarse)

    def _round(self, value, step):
        return round(value / step) * step if step else value

    def _set_tread(self, T, shift, ctrl):
        T = min(max(self._round(T, self._step(shift, ctrl)), MIN_TREAD), MAX_TREAD)
        self.obj['STAIR_TREAD_DEPTH'] = float(T)
        return T

    def _drag_start(self, view, p, delta, ctrl, shift):
        """The foot moves along the first flight; the top stays put."""
        d = self.drag
        v = d['v']
        run1 = hb_stairs.counts(v)[2]
        back = -(d['R'].transposed() @ delta).y         # drawn back: a longer flight
        T = self._set_tread(v['tread'] * (run1 + back) / max(run1, 1e-6), shift, ctrl)
        nv = hb_stairs.values(self.obj)
        point, up = d['end']
        loc, turn = hb_stairs.placement(nv, 'END', point, up)
        self.obj.location.x, self.obj.location.y = loc
        self.obj.rotation_euler.z = turn
        self.message = f"Tread {units.unit_to_string(bpy.context.scene.unit_settings, T)}"
        self.label_at = self.to_world(hb_stairs.ends(nv)[0][0])

    def _drag_end(self, view, p, delta, ctrl, shift):
        """The top moves along the last flight; the foot stays put."""
        d = self.drag
        v = d['v']
        n, _r, run1, run2 = hb_stairs.counts(v)
        last = run2 if run2 > 0 else run1
        _point, up = d['end']
        more = delta.dot(up)
        T = self._set_tread(v['tread'] * (last + more) / max(last, 1e-6), shift, ctrl)
        self.message = f"Tread {units.unit_to_string(bpy.context.scene.unit_settings, T)}"
        self.label_at = self.to_world(hb_stairs.ends(hb_stairs.values(self.obj))[1][0])

    def _side(self, kind, delta, ctrl, shift):
        d = self.drag
        v = d['v']
        R, o = d['R'], d['o']
        dx = (R.transposed() @ delta).x
        W = v['width'] + (dx if kind == 'right' else -dx)
        # The moving side's line, against a wall face along it
        if not ctrl:
            side_x = W if kind == 'right' else v['width'] - W
            along = R @ Vector((0.0, 1.0))
            base = o + R @ Vector((side_x, 0.0))
            normal = R @ Vector((1.0, 0.0))
            tol = SNAP_PX * _ui_scale() * self._metres_per_px
            best = None
            for a, b in self.faces:
                f = b - a
                if f.length < 1e-6 or abs(f.normalized().cross(along)) > 0.02:
                    continue
                off = (a - base).dot(normal)
                if abs(off) < tol and (best is None or abs(off) < abs(best)):
                    best = off
            if best is not None:
                W += best if kind == 'right' else -best
                ctrl = True                 # on the wall: no rounding
        W = self._round(W, inch(0.25) if shift else (0.0 if ctrl else inch(1)))
        W = min(max(W, MIN_WIDTH), MAX_WIDTH)
        self.obj['STAIR_WIDTH'] = float(W)
        if kind == 'left':
            # The right side stays: the foot's corner moves over
            shift_x = v['width'] - W
            q = o + R @ Vector((shift_x, 0.0))
            self.obj.location.x, self.obj.location.y = q
        self.message = f"Width {units.unit_to_string(bpy.context.scene.unit_settings, W)}"

    def _drag_left(self, view, p, delta, ctrl, shift):
        self._side('left', delta, ctrl, shift)
        self.label_at = self.to_world((0.0, 0.0))

    def _drag_right(self, view, p, delta, ctrl, shift):
        self._side('right', delta, ctrl, shift)
        self.label_at = self.to_world((hb_stairs.values(self.obj)['width'], 0.0))

    def _drag_turn(self, view, p, delta, ctrl, shift):
        """The landing along the first flight, a riser at a time."""
        d = self.drag
        v = d['v']
        R, o = d['R'], d['o']
        y = (R.transposed() @ (p - o)).y - v['width'] / 2.0     # the landing's foot
        steps = max(2, hb_stairs.riser_count(v['rise'], v['max_riser']))
        riser = v['rise'] / steps
        first = min(max(round(y / v['tread']), 1), steps - 1)
        self.obj['STAIR_LANDING_HEIGHT'] = float(first * riser)
        self.message = f"{first} + {steps - first} risers"
        self.label_at = self.to_world((v['width'] / 2.0, first * v['tread'] + v['width'] / 2.0))

    def _drag_move(self, view, p, delta, ctrl, shift):
        """The whole stair: its foot along and against the walls."""
        d = self.drag
        v = d['v']
        point, up = d['start']
        point = point + delta
        if not ctrl:
            point, up, _on_wall = hb_stairs.snap(point, up, v['width'], self.faces)
        loc, turn = hb_stairs.placement(v, 'START', point, up)
        self.obj.location.x, self.obj.location.y = loc
        self.obj.rotation_euler.z = turn
        self.message = ""

    _metres_per_px = 0.01

    def set_view(self, view):
        """The world size of a pixel at the stair, for snapping in pixels."""
        o, _R, z = self.frame()
        self._metres_per_px = max(view.px_size((o.x, o.y, z), 1.0), 1e-5)

    def release(self):
        """End a drag. Returns what it did, for the undo step, or None."""
        d, self.drag = self.drag, None
        if d is None:
            return None
        if not d['moved']:
            if d['kind'] == 'turn':
                return self.flip()
            if d['kind'] == 'rotate':
                return self.quarter_turn()
            return None
        self.message = ""
        self._rebuild()
        return "Edit Stairs"

    def cancel(self):
        """Esc: drop a drag in progress (True), or nothing to drop."""
        if self.drag is None:
            return False
        _restore(self.obj, self.drag['state'])
        self.drag = None
        self.message = ""
        self._rebuild()
        return True

    def put_back(self):
        _restore(self.obj, self.start_state)
        self._rebuild()

    def flip(self):
        v = self.values()
        if v['type'] not in ('L_SHAPE', 'U_SHAPE'):
            return None
        self.obj['STAIR_TURN_DIRECTION'] = 'RIGHT' if v['turn'] == 'LEFT' else 'LEFT'
        self._rebuild()
        return "Flip Stair Turn"

    def quarter_turn(self, sign=1.0):
        """A quarter turn about the stair's middle."""
        obj = self.obj
        c = self.center()
        wc = self.to_world(c).to_2d()
        obj.rotation_euler.z += sign * math.pi / 2.0
        R = Matrix.Rotation(obj.rotation_euler.z, 2)
        q = wc - R @ c
        obj.location.x, obj.location.y = q
        self._rebuild()
        return "Turn Stair"

    def _rebuild_mesh(self):
        from . import hb_stair_build
        try:
            hb_stair_build.build(self.obj)
        except Exception as e:
            print(f"Edit Stairs: {e}")

    def _rebuild(self):
        try:
            hb_stairs.rebuild(self.obj)
        except Exception as e:
            print(f"Edit Stairs: {e}")

    def summary(self):
        """What the stair is now: risers, riser, run - and its two flights."""
        obj = self.obj
        text = hb_stairs.describe(obj, bpy.context.scene.unit_settings)
        v = self.values()
        if v['type'] in ('L_SHAPE', 'U_SHAPE') and not v['winders']:
            a, b, _r = hb_stairs.split_flights(v['rise'], v['max_riser'], v['landing_height'])
            text += f" · {a} + {b}, turns {v['turn'].lower()}"
        return text


# =============================================================================
# DRAWING
# =============================================================================

def _circle(shader, c, r, color):
    pts = [(c.x + r * math.cos(a * math.pi / 8), c.y + r * math.sin(a * math.pi / 8)) for a in range(17)]
    shader.uniform_float("color", (0.05, 0.05, 0.05, 0.9))
    gpu.state.line_width_set(4.0)
    batch_for_shader(shader, 'LINE_STRIP', {"pos": pts}).draw(shader)
    shader.uniform_float("color", color)
    gpu.state.line_width_set(2.0)
    batch_for_shader(shader, 'LINE_STRIP', {"pos": pts[:14]}).draw(shader)
    # An arrowhead at the open end: a quarter turn
    end = Vector(pts[13])
    tip = Vector(pts[14])
    t = (tip - end).normalized() * r * 0.6
    n = Vector((-t.y, t.x))
    batch_for_shader(shader, 'TRIS', {"pos": [end + t, end - n * 0.6, end + n * 0.6]}).draw(shader)
    gpu.state.line_width_set(1.0)


def draw(session, region, rv3d):
    obj = session.obj
    if obj is None:
        return
    view = View.of(region, rv3d)
    session.set_view(view)
    s = _ui_scale()
    z = session.frame()[2]
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    def ring(poly):
        pts = [view.to_2d(session.to_world(q)) for q in poly]
        if None in pts:
            return []
        return [q for i in range(len(pts)) for q in (pts[i], pts[(i + 1) % len(pts)])]

    flights, lands = session.rects()
    _segments(shader, [q for poly in flights for q in ring(poly)], OUTLINE, 2.0)
    _segments(shader, [q for poly in lands for q in ring(poly)], LANDING, 2.0)
    # The way up: a line up the middle of each flight
    for poly in flights:
        a = view.to_2d(session.to_world((poly[0] + poly[1]) / 2.0))
        b = view.to_2d(session.to_world((poly[2] + poly[3]) / 2.0))
        if a is not None and b is not None:
            _segments(shader, [a, b], (0.95, 0.95, 0.95, 0.35), 1.0)
    gpu.state.line_width_set(1.0)

    hot = session.drag['kind'] if session.drag is not None else session.hover
    for kind, p in session.grips():
        q = view.to_2d(p)
        if q is None:
            continue
        color = HOVER_COLOR if hot == kind else GRIP_COLORS[kind]
        size = GRIP_PX * s * (1.25 if hot == kind else 1.0)
        (_diamond if kind == 'turn' else _square)(shader, q, size, color)
    q = session.rotate_grip(view)
    if q is not None:
        _circle(shader, q, GRIP_PX * s * 1.3, HOVER_COLOR if hot == 'rotate' else GRIP_COLORS['rotate'])

    text = session.message or (session.summary() if session.drag is None else "")
    at = session.label_at if session.message else session.to_world(session.center())
    if text and at is not None:
        q = view.to_2d(at)
        if q is not None:
            _label(shader, q, text, s)
    gpu.state.blend_set('NONE')


# =============================================================================
# THE OPERATOR
# =============================================================================

_running = None


def _selected_stair(context):
    for obj in [context.active_object] + list(context.selected_objects):
        stair = hb_stairs.stair_of(obj)
        if stair is not None:
            return stair
    return None


class HOME_BUILDER_STAIRS_OT_edit_stairs(bpy.types.Operator):
    bl_idname = "home_builder_stairs.edit_stairs"
    bl_label = "Edit Stairs"
    bl_description = ("Shape the selected stair in the viewport: drag its ends, sides and "
                      "landing, move it, turn it")

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and (_running is not None or _selected_stair(context) is not None))

    def invoke(self, context, event):
        global _running
        if _running is not None:
            _running.stop = True        # the button again: done
            return {'CANCELLED'}
        stair = _selected_stair(context)
        if stair is None:
            return {'CANCELLED'}
        self.session = StairEdit(stair)
        self.area = context.area
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), None)
        self.stop = False
        _running = self
        self.handle = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_PIXEL')
        context.workspace.status_text_set(HINT)
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

    def _finish(self, context, keep=True):
        global _running
        if _running is self:
            _running = None
        if not keep:
            self.session.put_back()
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        context.workspace.status_text_set(None)
        self.area.tag_redraw()
        if keep:
            try:
                bpy.ops.ed.undo_push(message="Edit Stairs")
            except RuntimeError:
                pass

    def _view(self, context):
        rv3d = context.region_data if context.region == self.region else self.region.data
        return View.of(self.region, rv3d)

    def _in_region(self, event):
        r = self.region
        x, y = event.mouse_x - r.x, event.mouse_y - r.y
        return (0 <= x < r.width and 0 <= y < r.height), x, y

    def modal(self, context, event):
        session = self.session
        if self.stop or session.obj is None:
            self._finish(context)
            return {'FINISHED'}
        inside, mx, my = self._in_region(event)
        self.area.tag_redraw()
        busy = session.drag is not None

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
                return {'PASS_THROUGH'}
            if event.value == 'RELEASE' and busy:
                session.release()
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.value != 'PRESS':
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if session.cancel():
                return {'RUNNING_MODAL'}
            self._finish(context, keep=False)
            return {'CANCELLED'}
        if event.type in {'RET', 'NUMPAD_ENTER'} and not busy:
            self._finish(context)
            return {'FINISHED'}
        if busy:
            return {'PASS_THROUGH'} if event.type in NAVIGATION else {'RUNNING_MODAL'}
        if event.type == 'R':
            session.quarter_turn(-1.0 if event.shift else 1.0)
            return {'RUNNING_MODAL'}
        if event.type == 'F':
            session.flip()
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}


classes = (HOME_BUILDER_STAIRS_OT_edit_stairs,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
