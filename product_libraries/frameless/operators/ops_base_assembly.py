"""Base assemblies: the ladder bases that carry runs of cabinets.

A base and tall cabinet set to the Ladder Style toe kick stands on plain
sides with the toe kick space left open under it. What fills that space
belongs to the run rather than to the cabinet: one base carries every
cabinet of a straight stretch. So the bases are built from the room the
way countertops are -- Add Base Assemblies reads the cabinets, works out
the stretches and stands a types_products.BaseAssembly under each.

A stretch is cabinets that share a parent (a wall, a cabinet group, or
the floor) and a facing, touch end to end, and agree on their back line,
depth, floor height and toe kick. Anything else between two cabinets --
a range, a dishwasher, a change of depth -- ends one stretch and starts
the next, and a stretch longer than MAX_LENGTH is cut at a cabinet joint.
An end that nothing stands against is an exposed end: the base steps
back from it by the toe kick setback, the way it does from the front.
"""
import bpy
import math
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_line_plane

from .. import types_products
from ...common import countertop_common
from .... import hb_types, hb_utils, units

LADDER_STYLE = 1                    # index in the Toe Kick Type prompt
MAX_LENGTH = units.inch(96.0)       # longest single base
JOIN_GAP = units.inch(0.25)         # cabinets this close are end to end
ALIGN_TOL = units.inch(0.0625)      # same back line / depth / floor
WALL_END_REACH = units.inch(2.0)    # a corner filler's worth of wall end

MEMBERS_KEY = 'BASE_ASSEMBLY_MEMBERS'
# Set once a base has been placed or resized by hand: Add Base
# Assemblies then leaves it, and the cabinets standing on it, as they are.
EDITED_KEY = 'BASE_ASSEMBLY_EDITED'

# What can stand against the end of a run and close it.
NEIGHBOR_MARKERS = ('IS_FRAMELESS_CABINET_CAGE', 'IS_FRAMELESS_PRODUCT_CAGE',
                    'IS_FACE_FRAME_CABINET_CAGE', 'IS_APPLIANCE')


# ---------------------------------------------------------------------------
# Reading the room
# ---------------------------------------------------------------------------

def wants_base_assembly(obj):
    """A straight base or tall cabinet on the Ladder Style toe kick.
    Corner cabinets keep their own base: theirs is not a straight one."""
    return (bool(obj.get('IS_FRAMELESS_CABINET_CAGE'))
            and obj.get('CABINET_TYPE') in ('BASE', 'TALL')
            and 'CORNER_TYPE' not in obj
            and int(obj.get('Toe Kick Type', -1)) == LADDER_STYLE)


def _cabinet_root(obj):
    while obj is not None:
        if obj.get('IS_FRAMELESS_CABINET_CAGE'):
            return obj
        obj = obj.parent
    return None


def gather_cabinets(context, selected_only=False):
    if not selected_only:
        return [o for o in context.scene.objects if wants_base_assembly(o)]
    picked = []
    for obj in context.selected_objects:
        root = _cabinet_root(obj)
        if root is not None and wants_base_assembly(root) and root not in picked:
            picked.append(root)
    return picked


def _facing(obj):
    """World heading in whole degrees, so cabinets that face the same
    way share a key whatever order they were placed in."""
    return round(math.degrees(obj.matrix_world.to_euler().z)) % 360


def _frame(obj):
    """The cabinet's world frame without its scale."""
    loc, rot, _scale = obj.matrix_world.decompose()
    return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()


class _Member:
    """One cabinet measured in its stretch's frame: X along the run, the
    back of the cabinet at ``y``, the body running towards -Y."""

    def __init__(self, obj, to_frame):
        cage = hb_types.GeoNodeCage(obj)
        origin = to_frame @ obj.matrix_world.translation
        self.obj = obj
        self.x0 = origin.x
        self.x1 = origin.x + cage.get_input('Dim X')
        self.y = origin.y
        self.z = origin.z
        self.depth = cage.get_input('Dim Y')
        self.kick_height = float(obj.get('Toe Kick Height', 0.0))
        # Negative for a flush toe kick: the base comes forward under
        # the fronts.
        from .. import solver_frameless
        self.kick_setback = solver_frameless.kick_front_setback(obj)

    def continues(self, other):
        """True when ``other`` carries straight on from this cabinet."""
        return (abs(other.x0 - self.x1) <= JOIN_GAP
                and abs(other.y - self.y) <= ALIGN_TOL
                and abs(other.z - self.z) <= ALIGN_TOL
                and abs(other.depth - self.depth) <= ALIGN_TOL
                and abs(other.kick_height - self.kick_height) <= ALIGN_TOL
                and abs(other.kick_setback - self.kick_setback) <= ALIGN_TOL)


def _cut_to_length(members):
    """Split one stretch at cabinet joints so no base passes MAX_LENGTH.
    A single cabinet longer than that keeps a base of its own."""
    pieces, current = [], []
    for member in members:
        if current and member.x1 - current[0].x0 > MAX_LENGTH:
            pieces.append(current)
            current = []
        current.append(member)
    if current:
        pieces.append(current)
    return pieces


def build_stretches(cabinets):
    """[(frame, [members])]: the cabinets sorted into the stretches that
    each get one base. ``frame`` is the world matrix the members were
    measured in."""
    keyed = {}
    for cab in cabinets:
        keyed.setdefault((cab.parent, _facing(cab)), []).append(cab)

    stretches = []
    for group in keyed.values():
        frame = _frame(group[0])
        to_frame = frame.inverted()
        members = sorted((_Member(c, to_frame) for c in group),
                         key=lambda m: m.x0)
        current = []
        for member in members:
            if current and not current[-1].continues(member):
                stretches.extend((frame, p) for p in _cut_to_length(current))
                current = []
            current.append(member)
        if current:
            stretches.extend((frame, p) for p in _cut_to_length(current))
    return stretches


# ---------------------------------------------------------------------------
# Exposed ends
# ---------------------------------------------------------------------------

def _wall_closes(parent, frame, x, kick_height):
    """True when the stretch end at frame-x ``x`` runs into the end of
    its wall where another wall carries on: an inside or outside corner
    either way, there is no open end to step back from."""
    if parent is None or not parent.get('IS_WALL_BP'):
        return False
    wall = hb_types.GeoNodeWall(parent)
    wall_x = (parent.matrix_world.inverted()
              @ (frame @ Vector((x, 0.0, kick_height)))).x
    if wall_x <= WALL_END_REACH:
        return bool(wall.get_connected_wall(direction='left',
                                            include_loop_seam=True))
    if wall_x >= wall.get_input('Length') - WALL_END_REACH:
        return bool(wall.get_connected_wall(direction='right',
                                            include_loop_seam=True))
    return False


def _neighbor_boxes(context, frame, members):
    """Frame-space (x0, x1, y0, y1) of everything that could stand
    against this stretch: cabinets, products and appliances on the
    floor, other than the stretch's own cabinets."""
    own = {m.obj for m in members}
    to_frame = frame.inverted()
    floor = members[0].z
    top = floor + members[0].kick_height
    boxes = []
    for obj in context.scene.objects:
        if obj in own or obj.get('IS_BASE_ASSEMBLY'):
            continue
        if not any(obj.get(marker) for marker in NEIGHBOR_MARKERS):
            continue
        if obj.get('IS_CABINET_APPLIANCE'):
            continue            # a sink or oven inside a cabinet
        try:
            points = [to_frame @ p for p in countertop_common.footprint(obj)]
        except Exception:
            continue
        if not (points[0].z < top + ALIGN_TOL and points[0].z > floor - units.inch(1.0)):
            continue            # an upper, or something on another floor
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
    return boxes


def exposed_ends(context, frame, members):
    """(left, right): whether each end of the stretch stands open."""
    first, last = members[0], members[-1]
    y_back, y_front = first.y, first.y - first.depth
    boxes = _neighbor_boxes(context, frame, members)

    def closed(x, side):
        if _wall_closes(first.obj.parent, frame, x, first.kick_height):
            return True
        for bx0, bx1, by0, by1 in boxes:
            if by1 <= y_front + ALIGN_TOL or by0 >= y_back - ALIGN_TOL:
                continue        # beside the run, not in line with it
            edge = bx1 if side == 'left' else bx0
            if abs(edge - x) <= JOIN_GAP:
                return True
            if bx0 < x - JOIN_GAP and bx1 > x + JOIN_GAP:
                return True     # a corner cabinet lying across the end
        return False

    return not closed(first.x0, 'left'), not closed(last.x1, 'right')


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

def create_base_assembly(context, frame, members):
    first, last = members[0], members[-1]
    open_left, open_right = exposed_ends(context, frame, members)
    setback = first.kick_setback
    # A flush kick runs out to an exposed end rather than stepping back.
    end_setback = max(setback, 0.0)
    x0 = first.x0 + (end_setback if open_left else 0.0)
    x1 = last.x1 - (end_setback if open_right else 0.0)
    if x1 - x0 <= 0.0 or first.kick_height <= 0.0:
        return None

    base = types_products.BaseAssembly()
    base.width = x1 - x0
    base.depth = first.depth - setback
    base.height = first.kick_height
    base.create('Base Assembly')
    obj = base.obj
    obj[MEMBERS_KEY] = [m.obj.name for m in members]

    # On a wall or in a cabinet group the base belongs to that; a lone
    # island's base goes with its first cabinet.
    parent = first.obj.parent or first.obj
    world = frame @ Matrix.Translation(Vector((x0, first.y, first.z)))
    local = parent.matrix_world.inverted() @ world
    obj.parent = parent
    obj.matrix_parent_inverse.identity()
    obj.location = local.to_translation()
    obj.rotation_euler = local.to_euler()
    return obj


def stands_on(cabinet, base):
    """True when the middle of the cabinet's footprint is over the base.
    Read from where things are rather than from the base's member list:
    a base placed by hand has none, and cabinets get renamed."""
    cage = hb_types.GeoNodeCage(cabinet)
    middle = cabinet.matrix_world @ Vector((cage.get_input('Dim X') / 2.0,
                                            -cage.get_input('Dim Y') / 2.0, 0.0))
    local = base.matrix_world.inverted() @ middle
    dim_x, dim_y, dim_z = _dims_of(base)
    return (0.0 <= local.x <= dim_x and -dim_y <= local.y <= 0.0
            and abs(local.z) <= dim_z + ALIGN_TOL)


def remove_base_assemblies(objs):
    removed = 0
    for obj in objs:
        for child in list(obj.children_recursive):
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(obj, do_unlink=True)
        removed += 1
    return removed


def _all_base_assemblies(scene):
    return [o for o in scene.objects if o.get('IS_BASE_ASSEMBLY')]


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class hb_frameless_OT_add_base_assemblies(bpy.types.Operator):
    bl_idname = "hb_frameless.add_base_assemblies"
    bl_label = "Add Base Assemblies"
    bl_description = ("Stand a base assembly under each run of base and tall "
                      "cabinets set to the Ladder Style toe kick")
    bl_options = {'REGISTER', 'UNDO'}

    selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Only build bases under the selected cabinets",
        default=False
    )  # type: ignore

    def execute(self, context):
        cabinets = gather_cabinets(context, self.selected_only)
        if not cabinets:
            self.report({'WARNING'},
                        "No Ladder Style base or tall cabinets "
                        + ("selected" if self.selected_only else "found"))
            return {'CANCELLED'}

        # Rebuilding replaces the bases these cabinets already stand on.
        # Over the whole room a base resized by hand is kept, with its
        # cabinets; picking its cabinets out asks for it to be refitted.
        names = {c.name for c in cabinets}
        existing = _all_base_assemblies(context.scene)
        if self.selected_only:
            kept = []
            stale = [o for o in existing
                     if names.intersection(o.get(MEMBERS_KEY) or ())]
        else:
            kept = [o for o in existing if o.get(EDITED_KEY)]
            stale = [o for o in existing if not o.get(EDITED_KEY)]
        cabinets = [c for c in cabinets
                    if not any(stands_on(c, base) for base in kept)]
        remove_base_assemblies(stale)

        created = []
        for frame, members in build_stretches(cabinets):
            obj = create_base_assembly(context, frame, members)
            if obj is not None:
                created.append(obj)

        for obj in created:
            bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=obj.name)
            hb_utils.run_calc_fix(context, obj)
            bpy.ops.hb_frameless.toggle_mode(search_obj_name=obj.name)

        message = f"Created {len(created)} base assembly(s)"
        if kept:
            message += f", kept {len(kept)} edited"
        self.report({'INFO'}, message)
        return {'FINISHED'}


class hb_frameless_OT_remove_base_assemblies(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_base_assemblies"
    bl_label = "Remove Base Assemblies"
    bl_description = "Remove every base assembly from the room"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removed = remove_base_assemblies(_all_base_assemblies(context.scene))
        self.report({'INFO'}, f"Removed {removed} base assembly(s)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Editing in the viewport
# ---------------------------------------------------------------------------
#
# A base stands inside its cabinets' cages, so it cannot be clicked in
# any selection mode. The edit tool does not need it to be: it outlines
# every base in the room and takes the mouse itself, the way the
# backsplash and countertop editors do. Hover an edge to light it up;
# drag it, or click it and type the size it should come to.

MIN_BASE_SPAN = units.inch(2.0)
FINE_SNAP = units.inch(1.0 / 16.0)
COARSE_SNAP = units.inch(1.0)
CLICK_PX = 4.0

_TYPED_CHARS = set("0123456789.-/ '\"")
_NAV_EVENTS = {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
               'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'NDOF_MOTION'}


def _world_of(obj):
    """The base's world matrix from its own location and rotation, not
    matrix_world: that lags a drag until the next depsgraph update."""
    local = Matrix.LocRotScale(obj.location, obj.rotation_euler, None)
    if obj.parent is None:
        return local
    return obj.parent.matrix_world @ obj.matrix_parent_inverse @ local


def _dims_of(obj):
    cage = hb_types.GeoNodeCage(obj)
    return (cage.get_input('Dim X'), cage.get_input('Dim Y'),
            cage.get_input('Dim Z'))


class hb_frameless_OT_edit_base_assemblies(bpy.types.Operator):
    bl_idname = "hb_frameless.edit_base_assemblies"
    bl_label = "Edit Base Assemblies"
    bl_description = ("Drag the edges of the base assemblies in the viewport, "
                      "or click an edge and type its size")
    bl_options = {'REGISTER', 'UNDO'}

    _draw_handle = None

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    # -- state ---------------------------------------------------------
    def _rebuild_handles(self):
        """One handle per edge of every base, drawn on the top of the
        base so the four edges read as its plan."""
        self.handles = []
        for obj in self.bases:
            dim_x, dim_y, dim_z = _dims_of(obj)
            world = _world_of(obj)
            corners = [world @ Vector((x, y, dim_z)) for x, y in
                       ((0.0, 0.0), (dim_x, 0.0), (dim_x, -dim_y), (0.0, -dim_y))]
            for kind, i, j in (('BACK', 0, 1), ('RIGHT', 1, 2),
                               ('FRONT', 2, 3), ('LEFT', 3, 0)):
                self.handles.append({
                    'kind': kind, 'obj': obj,
                    'a': corners[i], 'b': corners[j],
                    'world': (corners[i] + corners[j]) / 2.0})

    def _mouse(self, event):
        """The mouse in the 3D view's own region, wherever the command
        was started from."""
        return (event.mouse_x - self.region.x, event.mouse_y - self.region.y)

    @staticmethod
    def _distance_to_edge(p, a, b):
        ab = b - a
        length_sq = ab.length_squared
        if length_sq < 1e-9:
            return (p - a).length
        t = max(0.0, min(1.0, (p - a).dot(ab) / length_sq))
        return (p - (a + ab * t)).length

    def _pick(self, event):
        mouse = Vector(self._mouse(event))
        best, best_d = None, self.ui.PICK_PX
        for i, handle in enumerate(self.handles):
            a = view3d_utils.location_3d_to_region_2d(
                self.region, self.rv3d, handle['a'])
            b = view3d_utils.location_3d_to_region_2d(
                self.region, self.rv3d, handle['b'])
            if a is None or b is None:
                continue
            d = self._distance_to_edge(mouse, a, b)
            if d < best_d:
                best, best_d = i, d
        return best

    def _measure(self, index):
        """The size the edge at ``index`` sets: the length for an end,
        the depth for the front or back."""
        handle = self.handles[index]
        dim_x, dim_y, _dim_z = _dims_of(handle['obj'])
        return dim_x if handle['kind'] in ('LEFT', 'RIGHT') else dim_y

    def _readout_for(self, context, index):
        if index is None or not (0 <= index < len(self.handles)):
            return ""
        if self.drag is not None and self.typed:
            return self.typed
        return units.unit_to_string(context.scene.unit_settings,
                                    self._measure(index))

    def _set_cursor(self, context):
        kind = None
        if self.hover is not None and 0 <= self.hover < len(self.handles):
            kind = self.handles[self.hover]['kind']
        context.window.cursor_modal_set(
            'SCROLL_XY' if kind is not None else 'DEFAULT')

    # -- dragging ------------------------------------------------------
    def _begin_drag(self, event, index):
        obj = self.handles[index]['obj']
        self.drag = index
        self.hover = index
        self.typed = ""
        self.moved = False
        self.grab = False
        self.press_mouse = self._mouse(event)
        # Everything is measured from where the drag started, so moving
        # the base's own origin (its left or back edge) cannot feed back.
        self.start = {'world': _world_of(obj), 'dims': _dims_of(obj),
                      'location': obj.location.copy()}

    def _start_point(self, event):
        """The mouse on the plane of the base's top, in the frame the
        base had when the drag began."""
        co = self._mouse(event)
        origin = view3d_utils.region_2d_to_origin_3d(self.region, self.rv3d, co)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, self.rv3d, co)
        world = self.start['world']
        dim_z = self.start['dims'][2]
        point = world @ Vector((0.0, 0.0, dim_z))
        normal = (world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
        hit = intersect_line_plane(origin, origin + direction * 1000.0,
                                   point, normal)
        if hit is None:
            hit = view3d_utils.region_2d_to_location_3d(
                self.region, self.rv3d, co, self.handles[self.drag]['world'])
        return world.inverted() @ hit

    def _apply_drag(self, context, event, typed_value=None):
        handle = self.handles[self.drag]
        obj, kind = handle['obj'], handle['kind']
        dim_x, dim_y, _dim_z = self.start['dims']
        step = COARSE_SNAP if event.ctrl else FINE_SNAP

        def snapped(value):
            return round(value / step) * step

        # The new size along the edge's axis; the opposite edge holds.
        if typed_value is not None:
            size = typed_value
        else:
            local = self._start_point(event)
            size = {'RIGHT': local.x, 'LEFT': dim_x - local.x,
                    'FRONT': -local.y, 'BACK': dim_y + local.y}[kind]
            size = snapped(size)
        size = max(size, MIN_BASE_SPAN)

        shift = Vector((0.0, 0.0, 0.0))
        cage = hb_types.GeoNodeCage(obj)
        if kind in ('LEFT', 'RIGHT'):
            cage.set_input('Dim X', size)
            if kind == 'LEFT':
                shift.x = dim_x - size
        else:
            cage.set_input('Dim Y', size)
            if kind == 'BACK':
                shift.y = -(dim_y - size)
        obj.location = (self.start['location']
                        + obj.rotation_euler.to_matrix() @ shift)
        obj[EDITED_KEY] = True
        types_products.recalculate_product(obj)
        self._rebuild_handles()
        self.readout = self._readout_for(context, self.drag)

    def _end_drag(self, context, revert=False):
        if revert:
            self._restore(self.handles[self.drag]['obj'], {
                'location': self.start['location'],
                'dims': self.start['dims'],
                'edited': self.undo[self.handles[self.drag]['obj'].name]['edited']})
            self._rebuild_handles()
        self.drag = None
        self.grab = False
        self.typed = ""
        self.readout = ""
        self.area.tag_redraw()

    @staticmethod
    def _restore(obj, state):
        cage = hb_types.GeoNodeCage(obj)
        cage.set_input('Dim X', state['dims'][0])
        cage.set_input('Dim Y', state['dims'][1])
        obj.location = state['location']
        if state['edited']:
            obj[EDITED_KEY] = True
        elif EDITED_KEY in obj:
            del obj[EDITED_KEY]
        types_products.recalculate_product(obj)

    # -- modal ---------------------------------------------------------
    def invoke(self, context, event):
        from ....operators import ops_surfaces
        self.ui = ops_surfaces
        self.bases = _all_base_assemblies(context.scene)
        if not self.bases:
            self.report({'WARNING'}, "No base assemblies to edit -- add them first")
            return {'CANCELLED'}

        # The command can be started from the sidebar or the OPTIONS
        # page; the edges are drawn and picked in the view itself.
        self.area = context.area
        self.region = next(r for r in context.area.regions if r.type == 'WINDOW')
        self.rv3d = context.area.spaces.active.region_3d
        self.hover = None
        self.drag = None
        self.grab = False
        self.moved = False
        self.typed = ""
        self.readout = ""
        self.outline_world = []
        self.undo = {o.name: {'location': o.location.copy(), 'dims': _dims_of(o),
                              'edited': bool(o.get(EDITED_KEY))}
                     for o in self.bases}
        self._rebuild_handles()

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            ops_surfaces._draw_edit, (self,), 'WINDOW', 'POST_PIXEL')
        context.workspace.status_text_set(
            "Drag an edge, or click it and type a size   |   "
            "Ctrl: snap to the inch   |   Enter: done   |   Esc: cancel")
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in _NAV_EVENTS and self.drag is None:
            self._rebuild_handles()
            return {'PASS_THROUGH'}

        if self.drag is not None:
            return self._modal_drag(context, event)

        if event.type == 'MOUSEMOVE':
            self.hover = self._pick(event)
            self.readout = self._readout_for(context, self.hover)
            self._set_cursor(context)
            self.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            picked = self._pick(event)
            if picked is None:
                return self._finish(context)
            self._begin_drag(event, picked)
            self.readout = self._readout_for(context, picked)
            self.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            return self._finish(context)

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            for obj in self.bases:
                self._restore(obj, self.undo[obj.name])
            return self._finish(context, cancelled=True)

        return {'RUNNING_MODAL'}

    def _modal_drag(self, context, event):
        """An edge is held (mouse down) or picked up (clicked, following
        the mouse until the next click). Either way a typed size wins
        over the mouse and Enter commits it."""
        typed_value = (self.ui._parse_length(context, self.typed)
                       if self.typed else None)

        if event.type == 'MOUSEMOVE':
            if not self.moved:
                mx, my = self._mouse(event)
                if math.hypot(mx - self.press_mouse[0],
                              my - self.press_mouse[1]) < CLICK_PX:
                    return {'RUNNING_MODAL'}
                self.moved = True
            self._apply_drag(context, event, typed_value)
            self.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE' and not self.grab:
                if self.moved:
                    self._end_drag(context)
                else:
                    self.grab = True    # a click: carry it to a second click
            elif event.value == 'PRESS' and self.grab:
                self._end_drag(context)
            return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end_drag(context, revert=True)
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if typed_value is not None:
                self._apply_drag(context, event, typed_value)
            self._end_drag(context)
            return {'RUNNING_MODAL'}

        if event.value == 'PRESS' and (event.type == 'BACK_SPACE' or (
                event.unicode and event.unicode in _TYPED_CHARS)):
            if event.type == 'BACK_SPACE':
                self.typed = self.typed[:-1]
            else:
                self.typed += event.unicode
            self.moved = True
            value = self.ui._parse_length(context, self.typed) if self.typed else None
            if value is not None:
                self._apply_drag(context, event, value)
            self.readout = self._readout_for(context, self.drag)
            self.area.tag_redraw()
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def _finish(self, context, cancelled=False):
        if self._draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None
        context.workspace.status_text_set(None)
        context.window.cursor_modal_restore()
        self.area.tag_redraw()
        return {'CANCELLED'} if cancelled else {'FINISHED'}


classes = (
    hb_frameless_OT_add_base_assemblies,
    hb_frameless_OT_remove_base_assemblies,
    hb_frameless_OT_edit_base_assemblies,
)

register, unregister = bpy.utils.register_classes_factory(classes)
