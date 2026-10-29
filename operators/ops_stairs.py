import bpy
import math
import bmesh
from mathutils import Vector, Matrix
from .. import hb_snap, hb_utils, units
from .. import hb_house, hb_stairs
from . import tool_session


# ---------------------------------------------------------------------------
# Mesh generation helpers
# ---------------------------------------------------------------------------

def add_flight_to_bmesh(bm, num_steps, stair_width, actual_riser, tread_depth, tread_thickness):
    """Add a complete flight of stairs to *bm* at the origin.

    Flight extends in +Y (run), width in +X, rise in +Z.
    Returns a list of all verts created so the caller can transform them.
    """
    created_verts = []
    x0, x1 = 0, stair_width

    for i in range(num_steps):
        z_top = (i + 1) * actual_riser
        z_tread = z_top - tread_thickness
        y_front = i * tread_depth
        y_back = (i + 1) * tread_depth

        # Tread box
        vt = [
            bm.verts.new((x0, y_front, z_tread)),
            bm.verts.new((x1, y_front, z_tread)),
            bm.verts.new((x1, y_back,  z_tread)),
            bm.verts.new((x0, y_back,  z_tread)),
            bm.verts.new((x0, y_front, z_top)),
            bm.verts.new((x1, y_front, z_top)),
            bm.verts.new((x1, y_back,  z_top)),
            bm.verts.new((x0, y_back,  z_top)),
        ]
        bm.faces.new([vt[4], vt[5], vt[6], vt[7]])  # top
        bm.faces.new([vt[3], vt[2], vt[1], vt[0]])  # bottom
        bm.faces.new([vt[0], vt[4], vt[7], vt[3]])  # left
        bm.faces.new([vt[1], vt[2], vt[6], vt[5]])  # right
        bm.faces.new([vt[0], vt[1], vt[5], vt[4]])  # front
        bm.faces.new([vt[3], vt[7], vt[6], vt[2]])  # back
        created_verts.extend(vt)

        # Riser
        z_riser_bottom = i * actual_riser
        z_riser_top = z_tread
        if z_riser_top > z_riser_bottom + 0.001:
            vr = [
                bm.verts.new((x0, y_front, z_riser_bottom)),
                bm.verts.new((x1, y_front, z_riser_bottom)),
                bm.verts.new((x1, y_front, z_riser_top)),
                bm.verts.new((x0, y_front, z_riser_top)),
            ]
            bm.faces.new([vr[0], vr[1], vr[2], vr[3]])
            created_verts.extend(vr)

    total_run = num_steps * tread_depth
    total_rise = num_steps * actual_riser

    # Left stringer profile
    profile = [(0, 0)]
    for i in range(num_steps):
        y = i * tread_depth
        z = (i + 1) * actual_riser
        profile.append((y, z))
        profile.append(((i + 1) * tread_depth, z))
    profile.append((total_run, 0))

    left_verts  = [bm.verts.new((0,           y, z)) for y, z in profile]
    right_verts = [bm.verts.new((stair_width, y, z)) for y, z in profile]
    created_verts.extend(left_verts)
    created_verts.extend(right_verts)

    if len(left_verts) >= 3:
        try:
            bm.faces.new(left_verts)
        except:
            pass
    if len(right_verts) >= 3:
        try:
            bm.faces.new(list(reversed(right_verts)))
        except:
            pass

    # Back wall
    bv = [
        bm.verts.new((0,           total_run, 0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((stair_width, total_run, total_rise)),
        bm.verts.new((0,           total_run, total_rise)),
    ]
    bm.faces.new(bv)
    created_verts.extend(bv)

    # Bottom
    btv = [
        bm.verts.new((0,           0,         0)),
        bm.verts.new((stair_width, 0,         0)),
        bm.verts.new((stair_width, total_run, 0)),
        bm.verts.new((0,           total_run, 0)),
    ]
    bm.faces.new(btv)
    created_verts.extend(btv)

    # Front face (first riser)
    fv = [
        bm.verts.new((0,           0, 0)),
        bm.verts.new((stair_width, 0, 0)),
        bm.verts.new((stair_width, 0, actual_riser)),
        bm.verts.new((0,           0, actual_riser)),
    ]
    bm.faces.new(fv)
    created_verts.extend(fv)

    return created_verts


def add_landing_box(bm, x0, y0, z0, x1, y1, z1):
    """Add an axis-aligned box to *bm*.  Returns created verts."""
    v = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    bm.faces.new([v[4], v[5], v[6], v[7]])  # top
    bm.faces.new([v[3], v[2], v[1], v[0]])  # bottom
    bm.faces.new([v[0], v[4], v[7], v[3]])  # left
    bm.faces.new([v[1], v[2], v[6], v[5]])  # right
    bm.faces.new([v[0], v[1], v[5], v[4]])  # front
    bm.faces.new([v[3], v[7], v[6], v[2]])  # back
    return v


# ---------------------------------------------------------------------------
# Stair type mesh builders
# ---------------------------------------------------------------------------

def create_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness,
                      stair_type='STRAIGHT', turn_direction='LEFT', landing_depth=None,
                      landing_height=None, gap=0):
    """Main dispatch – builds the requested stair type and returns a Mesh."""

    if landing_depth is None:
        landing_depth = stair_width
    if landing_height is None:
        landing_height = total_rise / 2

    if stair_type == 'L_SHAPE':
        return _create_l_stair_mesh(stair_width, total_rise, riser_height,
                                    tread_depth, tread_thickness,
                                    landing_depth, turn_direction, landing_height)
    if stair_type == 'U_SHAPE':
        return _create_u_stair_mesh(stair_width, total_rise, riser_height,
                                    tread_depth, tread_thickness,
                                    landing_depth, turn_direction, landing_height, gap)
    # Default: straight
    return _create_straight_stair_mesh(stair_width, total_rise, riser_height,
                                       tread_depth, tread_thickness)


def split_flights(total_rise, riser_height, landing_height):
    """(steps in flight 1, steps in flight 2, riser): see hb_stairs.
    `riser_height` is the most a riser may be."""
    return hb_stairs.split_flights(total_rise, riser_height, landing_height)


def _create_straight_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness):
    num_steps = hb_stairs.riser_count(total_rise, riser_height)
    actual_riser = total_rise / num_steps

    bm = bmesh.new()
    add_flight_to_bmesh(bm, num_steps, stair_width, actual_riser, tread_depth, tread_thickness)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def _create_l_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness,
                          landing_depth, turn_direction, landing_height):
    """Two flights at 90 degrees connected by a landing platform.

    Flight 1 goes in +Y.  The landing sits at *landing_height*.
    Flight 2 covers the remaining rise (total_rise - landing_height).
    Each flight independently calculates its step count and actual riser.

    LEFT  turn -> flight 2 goes in -X direction.
    RIGHT turn -> flight 2 goes in +X direction.
    """
    steps_flight1, steps_flight2, actual_riser1 = split_flights(
        total_rise, riser_height, landing_height)
    actual_riser2 = actual_riser1
    flight1_rise = steps_flight1 * actual_riser1

    flight1_run = steps_flight1 * tread_depth

    bm = bmesh.new()

    # ---- Flight 1 (at origin, going +Y) ----
    add_flight_to_bmesh(bm, steps_flight1, stair_width, actual_riser1,
                        tread_depth, tread_thickness)

    # ---- Landing ----
    landing_z_bot = flight1_rise - tread_thickness
    landing_z_top = flight1_rise

    # The landing is the square at the turn: flight 2 leaves from its
    # side (it reached past it, under flight 2's first treads)
    lx0 = 0
    lx1 = stair_width

    ly0 = flight1_run
    ly1 = flight1_run + stair_width

    add_landing_box(bm, lx0, ly0, landing_z_bot, lx1, ly1, landing_z_top)

    # ---- Flight 2 (create at origin then transform) ----
    flight2_verts = add_flight_to_bmesh(bm, steps_flight2, stair_width, actual_riser2,
                                        tread_depth, tread_thickness)

    if turn_direction == 'LEFT':
        # Rotate +90 deg around Z  then translate.
        # After rotation: flight runs in -X, width in +Y.
        # We want its front (y=0 before rot -> x=0 after rot) at x = 0,
        # and width (x=0..W before rot -> y=0..W after rot) at y = flight1_run .. flight1_run+W.
        rot = Matrix.Rotation(math.radians(90), 4, 'Z')
        xlate = Matrix.Translation(Vector((0, flight1_run, flight1_rise)))
    else:
        # Rotate -90 deg around Z then translate.
        # After rotation: flight runs in +X, width in -Y.
        # We want: front at x = stair_width, width spanning y = flight1_run .. flight1_run+W
        rot = Matrix.Rotation(math.radians(-90), 4, 'Z')
        xlate = Matrix.Translation(Vector((stair_width, flight1_run + stair_width, flight1_rise)))

    mat = xlate @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=flight2_verts)

    # ---- Finalize ----
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def _create_u_stair_mesh(stair_width, total_rise, riser_height, tread_depth, tread_thickness,
                          landing_depth, turn_direction, landing_height, gap=0):
    """Two flights at 180 degrees connected by a landing platform.

    Flight 1 goes in +Y.  The landing sits at *landing_height*.
    Flight 2 runs parallel in -Y (back toward the start), offset to one side.

    LEFT  turn -> flight 2 is to the left  (-X side).
    RIGHT turn -> flight 2 is to the right (+X side).
    """
    steps_flight1, steps_flight2, actual_riser1 = split_flights(
        total_rise, riser_height, landing_height)
    actual_riser2 = actual_riser1
    flight1_rise = steps_flight1 * actual_riser1

    flight1_run = steps_flight1 * tread_depth

    bm = bmesh.new()

    # ---- Flight 1 (at origin, going +Y) ----
    add_flight_to_bmesh(bm, steps_flight1, stair_width, actual_riser1,
                        tread_depth, tread_thickness)

    # ---- Landing ----
    landing_z_bot = flight1_rise - tread_thickness
    landing_z_top = flight1_rise

    if turn_direction == 'LEFT':
        lx0 = -(stair_width + gap)
        lx1 = stair_width
    else:
        lx0 = 0
        lx1 = stair_width * 2 + gap

    ly0 = flight1_run
    ly1 = flight1_run + landing_depth

    add_landing_box(bm, lx0, ly0, landing_z_bot, lx1, ly1, landing_z_top)

    # ---- Flight 2 (create at origin then rotate 180 deg and translate) ----
    flight2_verts = add_flight_to_bmesh(bm, steps_flight2, stair_width, actual_riser2,
                                        tread_depth, tread_thickness)

    # Rotate 180 deg around Z: (x,y) -> (-x,-y)
    # After rotation: width in [-W, 0], run in [-R2, 0]
    rot = Matrix.Rotation(math.radians(180), 4, 'Z')

    if turn_direction == 'LEFT':
        # Flight 2 sits at x=[-(W+gap), -gap], front at y = ly0
        xlate = Matrix.Translation(Vector((-gap, ly0, flight1_rise)))
    else:
        # Flight 2 sits at x=[W+gap, 2W+gap], front at y = ly0
        xlate = Matrix.Translation(Vector((stair_width * 2 + gap, ly0, flight1_rise)))

    mat = xlate @ rot
    bmesh.ops.transform(bm, matrix=mat, verts=flight2_verts)

    # ---- Finalize ----
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.normal_update()
    mesh = bpy.data.meshes.new('Stairs')
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


# ---------------------------------------------------------------------------
# Rebuild helper
# ---------------------------------------------------------------------------

def rebuild_stair_mesh(obj):
    """The stair's treads, risers and parts from its settings (see
    hb_stair_build)."""
    from .. import hb_stair_build
    hb_stair_build.build(obj)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

DRAG = 0.25         # m; a press moved this far is a drag that sets the direction


class home_builder_stairs_OT_place_stairs(bpy.types.Operator):
    """Place a staircase: it follows the mouse, R turns it, a click puts
    it down where it starts (From Top: where it arrives). Pressing and
    dragging sets the way it climbs instead (From Top: the way down). Its
    risers are counted from the rise between the levels and the Max
    Riser; its sides go against walls they come near."""
    bl_idname = "home_builder_stairs.place_stairs"
    bl_label = "Place Stairs"
    bl_description = "Click to place the stair (R turns it first); press and drag to set the way it climbs"
    bl_options = {'REGISTER', 'UNDO'}

    # Modal state
    preview_obj = None
    region = None
    mouse_pos = None
    hit_location = None
    hit_object = None
    hit_face_index = None
    hit_grid = False
    view_point = None

    def _settings(self, context):
        h = context.scene.hb_house
        return (h.stair_type, h.stair_turn, round(h.stair_width, 5), round(h.stair_max_riser, 5),
                round(h.stair_tread, 5), h.stair_from, h.stair_risers, h.stair_stringer, h.stair_baluster,
                h.stair_railing, h.stair_winders, round(h.stair_radius, 5), round(h.stair_diameter, 5))

    def _levels(self, context):
        """(the level the stair stands on, the one it climbs to, the level
        clicked on, the edge drawn: 'START' or 'END')."""
        here = hb_house.active_level(context)
        if here is None:
            return None, None, None, 'START'
        house = here.id_data.hb_house
        if context.scene.hb_house.stair_from == 'TOP':
            below = hb_house.level_below(house, here)
            if below is not None:
                return below, here, here, 'END'
        return here, hb_house.level_above(house, here), here, 'START'

    def create_preview(self, context):
        h = context.scene.hb_house
        base, _upper, _here, self.anchor = self._levels(context)
        rise = hb_stairs.rise_for(base, context.scene)
        width = h.stair_width
        mesh = create_stair_mesh(width, rise, h.stair_max_riser, h.stair_tread, hb_stairs.TREAD_T,
                                 h.stair_type, h.stair_turn)
        self.preview_obj = bpy.data.objects.new('Stairs', mesh)
        context.scene.collection.objects.link(self.preview_obj)
        obj = self.preview_obj
        obj['IS_STAIR'] = True
        obj['MENU_ID'] = 'HOME_BUILDER_MT_stair_commands'
        obj['STAIR_WIDTH'] = width
        obj['STAIR_TOTAL_RISE'] = rise
        obj['STAIR_RISER_HEIGHT'] = h.stair_max_riser
        obj['STAIR_TREAD_DEPTH'] = h.stair_tread
        obj['STAIR_TREAD_THICKNESS'] = hb_stairs.TREAD_T
        obj['STAIR_TYPE'] = h.stair_type
        obj['STAIR_TURN_DIRECTION'] = h.stair_turn
        obj['STAIR_LANDING_DEPTH'] = width
        obj['STAIR_LANDING_HEIGHT'] = rise / 2
        obj['STAIR_GAP'] = 0.0
        obj['STAIR_AUTO_RISE'] = base is not None
        obj['STAIR_WINDERS'] = h.stair_winders
        obj['STAIR_RADIUS'] = h.stair_radius
        obj['STAIR_DIAMETER'] = h.stair_diameter
        obj['STAIR_RISERS'] = h.stair_risers
        obj['STAIR_STRINGER'] = h.stair_stringer
        obj['STAIR_BALUSTER'] = h.stair_baluster
        obj['STAIR_RAILING'] = h.stair_railing
        obj['HB_STAIR_PREVIEW'] = True
        if base is not None:
            obj[hb_house.LEVEL_KEY] = base.uid
        obj.location.z = base.elevation if base is not None else 0.0
        from .. import hb_stair_build
        old = obj.data
        obj.data = hb_stair_build.stair_mesh(hb_stairs.values(obj), hb_stair_build.construction(obj))
        bpy.data.meshes.remove(old)
        for mat in hb_stair_build.materials(obj)[:2]:
            obj.data.materials.append(mat)
        self._signature = self._settings(context)
        faces_on = [l.uid for l in (base, _upper) if l is not None]
        self.faces = hb_stairs.wall_faces(context.scene, faces_on) if faces_on else \
            hb_stairs.wall_faces(context.scene, [''])

    def _place(self, point, up):
        """Stand the preview with its drawn edge's middle at `point`,
        climbing along `up` there (going down along -up, From Top)."""
        v = hb_stairs.values(self.preview_obj)
        p, u, self.on_wall = hb_stairs.snap(point, up, v['width'], self.faces)
        loc, turn = hb_stairs.placement(v, self.anchor, p, u)
        self.preview_obj.location.x, self.preview_obj.location.y = loc.x, loc.y
        self.preview_obj.rotation_euler = (0.0, 0.0, turn)
        self.point, self.up = p, u

    def _mouse_point(self, context):
        if not self.hit_location:
            return None
        loc = Vector(self.hit_location)
        loc.x = hb_snap.snap_value_to_grid(loc.x)
        loc.y = hb_snap.snap_value_to_grid(loc.y)
        return loc

    def update_preview(self, context):
        if not self.preview_obj:
            return
        if self._settings(context) != self._signature:
            self.rebuild_preview(context)
        p = self._mouse_point(context)
        if self.start is None:
            if p is None:
                self.preview_obj.hide_set(True)
                return
            # Before the first click the stair follows the mouse, its
            # way up the last one drawn (R turns it)
            up = self.dir if self.anchor == 'START' else -self.dir
            self._place(p, up)
        else:
            if p is not None and self.press is not None:
                # Dragged far enough to mean a direction, it follows the drag
                if (Vector((p.x, p.y)) - self.press).length > DRAG:
                    d = Vector((p.x - self.start.x, p.y - self.start.y))
                    if d.length > 1e-6:
                        self.dir = d.normalized()
            up = self.dir if self.anchor == 'START' else -self.dir
            self._place(self.start, up)
        self.preview_obj.hide_set(False)

    def update_header(self, context):
        if not self.preview_obj:
            return
        v = hb_stairs.values(self.preview_obj)
        n, riser, run1, run2 = hb_stairs.counts(v)
        us = context.scene.unit_settings
        step = ("Click to place where it starts" if self.anchor == 'START' else "Click to place where it arrives") \
            if self.start is None else ("Drag the way it climbs, let go to place" if self.anchor == 'START'
                                        else "Drag the way it goes down, let go to place")
        wall = " | against a wall" if getattr(self, 'on_wall', False) else ""
        text = (f"Stairs: {n} risers of {units.unit_to_string(us, riser)}, "
                f"{units.unit_to_string(us, run1 + run2)} run{wall} | {step} | "
                "R turn | T type | D turn side | ESC cancel")
        context.area.header_text_set(text)

    def confirm_placement(self, context):
        if not self.preview_obj:
            return False
        obj = self.preview_obj
        n = hb_stairs.counts(hb_stairs.values(obj))[0]
        self.report({'INFO'}, f"Placed staircase: {n} risers")
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        del obj['HB_STAIR_PREVIEW']
        level = hb_stairs.level_of(obj)
        if level is not None:
            hb_house.ensure_level_collections(context.scene, level)
            coll = hb_house.level_subcollection(level, 'Products')
            if coll is not None and coll not in obj.users_collection:
                for c in list(obj.users_collection):
                    c.objects.unlink(obj)
                coll.objects.link(obj)
        # Its railings and stringers, now its sides' walls are known
        from .. import hb_stair_build
        context.view_layer.update()
        hb_stair_build.build(obj)
        if level is not None:
            from .. import hb_rooms
            hb_rooms.apply_stairwells(context.scene)
            hb_stairs.porches_follow(obj)
        self.preview_obj = None
        return True

    def cleanup(self, context):
        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None
        context.area.header_text_set(None)

    def rebuild_preview(self, context):
        """Make the preview again after its settings changed."""
        if self.preview_obj:
            bpy.data.objects.remove(self.preview_obj, do_unlink=True)
            self.preview_obj = None
        self.create_preview(context)

    def stop_tool(self, context):
        """Asked to stop (another tool picked, Done, another tab): what
        Esc does."""
        self.cleanup(context)
        return {'CANCELLED'}

    @tool_session.session_modal
    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        self.mouse_pos = Vector((
            event.mouse_x - self.region.x,
            event.mouse_y - self.region.y
        ))
        if self.preview_obj:
            self.preview_obj.hide_set(True)
        hb_snap.main(self, event.ctrl, context)
        hb_house.constrain_hit_to_level(self, context)
        self.update_preview(context)
        self.update_header(context)
        h = context.scene.hb_house

        # R - a quarter turn (before the first click)
        if event.type == 'R':
            if event.value == 'PRESS' and self.start is None:
                self.dir = Vector((-self.dir.y, self.dir.x))
            return {'RUNNING_MODAL'}

        # T - the next type
        if event.type == 'T':
            if event.value == 'PRESS':
                cycle = [i[0] for i in hb_stairs.TYPE_ITEMS]
                h.stair_type = cycle[(cycle.index(h.stair_type) + 1) % len(cycle)]
            return {'RUNNING_MODAL'}

        # D - the turn to the other side
        if event.type == 'D':
            if event.value == 'PRESS':
                h.stair_turn = 'RIGHT' if h.stair_turn == 'LEFT' else 'LEFT'
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE':
            p = self._mouse_point(context)
            if event.value == 'PRESS':
                if self.start is None and p is not None:
                    self.start = self.point.to_3d()
                    self.press = Vector((p.x, p.y))
                return {'RUNNING_MODAL'}
            if event.value == 'RELEASE' and self.start is not None:
                # Placed when the button comes up: as it was turned for a
                # click, along the drag for a drag
                if self.confirm_placement(context):
                    self.cleanup(context)
                    return {'FINISHED'}
            return {'RUNNING_MODAL'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            if self.start is not None:
                # Back to picking where it starts
                self.start = None
                return {'RUNNING_MODAL'}
            self.cleanup(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Must be used in 3D viewport")
            return {'CANCELLED'}
        self.region = context.region
        self.preview_obj = None
        self.start = None
        self.press = None
        self.dir = Vector((0.0, 1.0))
        self.point, self.up = Vector((0.0, 0.0)), Vector((0.0, 1.0))
        self.on_wall = False
        self.create_preview(context)
        tool_session.begin(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class home_builder_stairs_OT_stair_prompts(bpy.types.Operator):
    """Edit staircase properties"""
    bl_idname = "home_builder_stairs.stair_prompts"
    bl_label = "Stair Prompts"
    bl_description = "Edit the staircase dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    stair_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ('STRAIGHT', "Straight", "Straight staircase"),
            ('L_SHAPE',  "L-Shaped", "90\u00b0 turn with landing"),
            ('U_SHAPE',  "U-Shaped", "180\u00b0 turn with landing"),
        ],
        default='STRAIGHT',
    )  # type: ignore

    turn_direction: bpy.props.EnumProperty(
        name="Turn Direction",
        items=[
            ('LEFT',  "Left",  "Second flight turns left"),
            ('RIGHT', "Right", "Second flight turns right"),
        ],
        default='LEFT',
    )  # type: ignore

    stair_width: bpy.props.FloatProperty(
        name="Width", subtype='DISTANCE', unit='LENGTH',
        default=0.9144, min=0.3048, precision=5,
    )  # type: ignore

    total_rise: bpy.props.FloatProperty(
        name="Total Rise", subtype='DISTANCE', unit='LENGTH',
        default=2.4384, min=0.3048, precision=5,
    )  # type: ignore

    riser_height: bpy.props.FloatProperty(
        name="Max Riser", subtype='DISTANCE', unit='LENGTH',
        default=0.1905, min=0.1016, max=0.3048, precision=5,
    )  # type: ignore

    tread_depth: bpy.props.FloatProperty(
        name="Tread Depth", subtype='DISTANCE', unit='LENGTH',
        default=0.2667, min=0.1524, precision=5,
    )  # type: ignore

    tread_thickness: bpy.props.FloatProperty(
        name="Tread Thickness", subtype='DISTANCE', unit='LENGTH',
        default=0.0254, min=0.0127, precision=5,
    )  # type: ignore

    landing_depth: bpy.props.FloatProperty(
        name="Landing Depth", subtype='DISTANCE', unit='LENGTH',
        default=0.9144, min=0.3048, precision=5,
    )  # type: ignore

    landing_height: bpy.props.FloatProperty(
        name="Landing Height", subtype='DISTANCE', unit='LENGTH',
        default=1.2192, min=0.1905, precision=5,
        description="Height of the landing platform (splits rise between flights)",
    )  # type: ignore

    gap: bpy.props.FloatProperty(
        name="Gap", subtype='DISTANCE', unit='LENGTH',
        default=0, min=0, precision=5,
        description="Space between the two parallel flights",
    )  # type: ignore

    headroom: bpy.props.FloatProperty(
        name="Headroom", subtype='DISTANCE', unit='LENGTH',
        default=2.032, min=1.5, precision=5,
        description="Clear height over the nosings: the floor above is "
                    "opened wherever it would come lower",
    )  # type: ignore

    guard: bpy.props.BoolProperty(
        name="Guard Rail", default=True,
        description="A rail round the opening in the floor above",
    )  # type: ignore

    guard_height: bpy.props.FloatProperty(
        name="Guard Height", subtype='DISTANCE', unit='LENGTH',
        default=0.9144, min=0.5, precision=5,
    )  # type: ignore

    stair_obj = None

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_STAIR')

    def check(self, context):
        if not self.stair_obj:
            return False
        self.stair_obj['STAIR_WIDTH']           = self.stair_width
        self.stair_obj['STAIR_TOTAL_RISE']      = self.total_rise
        self.stair_obj['STAIR_RISER_HEIGHT']    = self.riser_height
        self.stair_obj['STAIR_TREAD_DEPTH']     = self.tread_depth
        self.stair_obj['STAIR_TREAD_THICKNESS'] = self.tread_thickness
        self.stair_obj['STAIR_TYPE']            = self.stair_type
        self.stair_obj['STAIR_TURN_DIRECTION']  = self.turn_direction
        self.stair_obj['STAIR_LANDING_DEPTH']   = self.landing_depth
        self.stair_obj['STAIR_LANDING_HEIGHT']  = self.landing_height
        self.stair_obj['STAIR_GAP']             = self.gap
        self.stair_obj['STAIR_HEADROOM']        = self.headroom
        self.stair_obj['STAIR_GUARD']           = self.guard
        self.stair_obj['STAIR_GUARD_HEIGHT']    = self.guard_height
        rebuild_stair_mesh(self.stair_obj)
        if self.stair_obj.get(hb_house.LEVEL_KEY):
            from .. import hb_rooms
            hb_rooms.update_stairwell_cutter(self.stair_obj)
        return True

    def invoke(self, context, event):
        self.stair_obj = context.active_object
        if not self.stair_obj or not self.stair_obj.get('IS_STAIR'):
            self.report({'WARNING'}, "Select a staircase first")
            return {'CANCELLED'}
        self.stair_width     = self.stair_obj.get('STAIR_WIDTH',           units.inch(36))
        self.total_rise      = self.stair_obj.get('STAIR_TOTAL_RISE',      units.inch(96))
        self.riser_height    = self.stair_obj.get('STAIR_RISER_HEIGHT',    units.inch(7.5))
        self.tread_depth     = self.stair_obj.get('STAIR_TREAD_DEPTH',     units.inch(10.5))
        self.tread_thickness = self.stair_obj.get('STAIR_TREAD_THICKNESS', units.inch(1))
        self.stair_type      = self.stair_obj.get('STAIR_TYPE',            'STRAIGHT')
        self.turn_direction  = self.stair_obj.get('STAIR_TURN_DIRECTION',  'LEFT')
        self.landing_depth   = self.stair_obj.get('STAIR_LANDING_DEPTH',   self.stair_width)
        self.landing_height  = self.stair_obj.get('STAIR_LANDING_HEIGHT',  self.total_rise / 2)
        self.gap             = self.stair_obj.get('STAIR_GAP',             0)
        self.headroom        = self.stair_obj.get('STAIR_HEADROOM',        units.inch(80))
        self.guard           = bool(self.stair_obj.get('STAIR_GUARD',      True))
        self.guard_height    = self.stair_obj.get('STAIR_GUARD_HEIGHT',    units.inch(36))
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        unit_settings = context.scene.unit_settings
        layout = self.layout

        # Type selector
        box = layout.box()
        box.prop(self, 'stair_type')
        if self.stair_type in ('L_SHAPE', 'U_SHAPE'):
            box.prop(self, 'turn_direction',text="Direction")
            box.prop(self, 'landing_depth')
            box.prop(self, 'landing_height')
            if self.stair_type == 'U_SHAPE':
                box.prop(self, 'gap')

        # Info box
        box = layout.box()
        if self.stair_type in ('L_SHAPE', 'U_SHAPE'):
            steps1, steps2, _riser = split_flights(
                self.total_rise, self.riser_height, self.landing_height)
            box.label(text=f"Flight 1: {steps1} steps", icon='MOD_ARRAY')
            box.label(text=f"Flight 2: {steps2} steps")
            row = box.row()
            row.label(text="Total Steps:")
            row.label(text=str(steps1 + steps2))
        else:
            num_steps = hb_stairs.riser_count(self.total_rise, self.riser_height)
            total_run = num_steps * self.tread_depth
            box.label(text=f"Steps: {num_steps}", icon='MOD_ARRAY')
            row = box.row()
            row.label(text="Total Run:")
            row.label(text=units.unit_to_string(unit_settings, total_run))

        # Dimensions
        box = layout.box()
        box.prop(self, 'stair_width')
        box.prop(self, 'total_rise')
        box.prop(self, 'riser_height')
        box.prop(self, 'tread_depth')
        box.prop(self, 'tread_thickness')

        # The opening in the floor above
        box = layout.box()
        box.prop(self, 'headroom')
        box.prop(self, 'guard')
        if self.guard:
            box.prop(self, 'guard_height')


class home_builder_stairs_OT_delete_stairs(bpy.types.Operator):
    """Delete the selected staircase"""
    bl_idname = "home_builder_stairs.delete_stairs"
    bl_label = "Delete Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.get('IS_STAIR')

    def execute(self, context):
        obj = context.active_object
        if obj and obj.get('IS_STAIR'):
            from .. import cutters, hb_rooms
            cutter = hb_rooms.stairwell_cutter(obj)
            if cutter is not None:
                cutters.remove(cutter)      # and the openings it cut
            for child in list(obj.children_recursive):
                bpy.data.objects.remove(child, do_unlink=True)     # its guard
            level = hb_stairs.level_of(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
            hb_stairs.porches_follow(None, level)          # railings close again
            self.report({'INFO'}, "Staircase deleted")
        return {'FINISHED'}


class HOME_BUILDER_MT_stair_commands(bpy.types.Menu):
    bl_label = "Stair Commands"
    bl_idname = "HOME_BUILDER_MT_stair_commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_stairs.stair_prompts", text="Stair Prompts", icon='PREFERENCES')
        layout.separator()
        layout.operator("home_builder_stairs.delete_stairs", text="Delete Stairs", icon='X')


classes = (
    home_builder_stairs_OT_place_stairs,
    home_builder_stairs_OT_stair_prompts,
    home_builder_stairs_OT_delete_stairs,
    HOME_BUILDER_MT_stair_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
