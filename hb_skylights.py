"""Skylights on a level's main roof.

A skylight is stored as a plan point (its centre) and a size, so it keeps
its place when the roof's pitch or overhangs change. Each rebuild sets it
on the roof's top surface there, square to the slope: a unit (curb,
frame and glass), a box through the slab added to the roof's openings
cutter (one per roof, cut from the main roof by one Boolean), and below,
in the room under it, a cut in the ceiling and - under a flat ceiling - a
light shaft down to it.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import hb_house, hb_utils
from .operators import tool_session
from .units import inch

SKYLIGHT_KEY = 'IS_SKYLIGHT'
SHAFT_KEY = 'IS_SKYLIGHT_SHAFT'
OPENINGS_CUT = "Openings"           # the Boolean on the main roof
CEILING_CUT = "Skylights - "        # and on the ceilings under them, + level name
CURB_HEIGHT = inch(5.5)             # a curb-mounted unit stands on a 2x6 curb
CURB_WIDTH = inch(1.5)
FRAME_HEIGHT = inch(2.5)
FRAME_WIDTH = inch(1.75)
FRAME_LIP = inch(0.75)              # the frame past the curb's outside
DECK_HEIGHT = inch(3.0)             # a deck-mounted unit's frame, off the roof
GLASS_DROP = inch(0.5)              # the glass, under the frame's top
SINK = 0.02                         # the unit starts this far into the roof
CUT_ABOVE = 0.3                     # the opening's box, past the roof's top
SHAFT_COLOR = (0.92, 0.92, 0.90)
EDGE_ANGLE = 2.0                    # degrees: a corner's slope this different crosses an edge


# ---- Where a skylight sits --------------------------------------------------------

def _top_z(frame, roof, x, y):
    from . import hb_roofs
    u, v = hb_roofs._uv(frame, (x, y))
    return hb_roofs.roof_top_z_at(frame, roof, u, v)


def _normal(frame, roof, x, y, h=1e-3):
    """The roof top's normal at (x, y)."""
    gx = (_top_z(frame, roof, x + h, y) - _top_z(frame, roof, x - h, y)) / (2.0 * h)
    gy = (_top_z(frame, roof, x, y + h) - _top_z(frame, roof, x, y - h)) / (2.0 * h)
    return Vector((-gx, -gy, 1.0)).normalized()


def pose(frame, roof, sk):
    """(matrix, crosses): the skylight's place on the roof - x across the
    slope, y up it, z out of it, its origin on the top surface at its
    centre - and True when it reaches over a ridge, hip or valley."""
    x, y = sk.x, sk.y
    n = _normal(frame, roof, x, y)
    t = Vector((0.0, 0.0, 1.0)).cross(n)
    if t.length < 1e-6:
        t = Vector((1.0, 0.0, 0.0))     # a flat roof: square to the axes
    t.normalize()
    s = n.cross(t).normalized()
    origin = Vector((x, y, _top_z(frame, roof, x, y)))
    m = Matrix.Identity(4)
    for i in range(3):
        m[i][0], m[i][1], m[i][2], m[i][3] = t[i], s[i], n[i], origin[i]
    crosses = False
    for cx in (-0.5, 0.5):
        for cy in (-0.5, 0.5):
            p = origin + t * (cx * sk.width) + s * (cy * sk.length)
            nc = _normal(frame, roof, p.x, p.y)
            if math.degrees(n.angle(nc, 0.0)) > EDGE_ANGLE:
                crosses = True
    return m, crosses


def warning(scene, level, sk):
    """What's wrong with where a skylight is, or ''."""
    from . import hb_roofs
    frame = hb_roofs.roof_frame(scene, level) if level.roof.enabled else None
    if frame is None:
        return "No roof here"
    u, v = hb_roofs._uv(frame, (sk.x, sk.y))
    if not (frame['u0'] <= u <= frame['u1'] and frame['v0'] <= v <= frame['v1']):
        return "Off the roof"
    return "Crosses a roof edge" if pose(frame, level.roof, sk)[1] else ""


# ---- Meshes ------------------------------------------------------------------------

def _box(bm, x0, x1, y0, y1, z0, z1, m, mat_index=0):
    if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9 or z1 - z0 <= 1e-9:
        return
    vs = [bm.verts.new(m @ Vector(p)) for p in
          ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
           (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        face = bm.faces.new([vs[i] for i in f])
        face.material_index = mat_index


def _ring(bm, w, l, inner, outer, z0, z1, m, mat_index=0):
    """A rectangular ring round the w x l opening, from `inner` to `outer`
    past its edges."""
    hw, hl = w / 2.0, l / 2.0
    _box(bm, -hw - outer, hw + outer, -hl - outer, -hl - inner, z0, z1, m, mat_index)
    _box(bm, -hw - outer, hw + outer, hl + inner, hl + outer, z0, z1, m, mat_index)
    _box(bm, -hw - outer, -hw - inner, -hl - inner, hl + inner, z0, z1, m, mat_index)
    _box(bm, hw + inner, hw + outer, -hl - inner, hl + inner, z0, z1, m, mat_index)


def unit_mesh(sk, name="Skylight"):
    """The unit in its own space (see pose): a curb on the roof for a
    curb-mounted one, the frame, and the glass."""
    from .product_libraries.common import door_window_geo
    w, l = sk.width, sk.length
    bm = bmesh.new()
    m = Matrix.Identity(4)
    if sk.curb == 'CURB':
        _ring(bm, w, l, 0.0, CURB_WIDTH, -SINK, CURB_HEIGHT, m, 0)
        z0, outer = CURB_HEIGHT, CURB_WIDTH + FRAME_LIP
    else:
        z0, outer = -SINK, FRAME_WIDTH
    top = z0 + (FRAME_HEIGHT if sk.curb == 'CURB' else DECK_HEIGHT + SINK)
    _ring(bm, w, l, -FRAME_WIDTH * 0.5, outer, z0, top, m, 1)
    hw, hl = w / 2.0 - FRAME_WIDTH * 0.5, l / 2.0 - FRAME_WIDTH * 0.5
    _box(bm, -hw, hw, -hl, hl, top - GLASS_DROP - inch(0.25), top - GLASS_DROP, m, 2)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    flashing = bpy.data.materials.get("HB Skylight Curb") or door_window_geo._material(
        "HB Skylight Curb", (0.25, 0.25, 0.24), roughness=0.6)
    frame_mat = door_window_geo._material("HB Skylight Frame", (0.18, 0.17, 0.16), roughness=0.4)
    for mat in (flashing, frame_mat, door_window_geo._glass_material()):
        mesh.materials.append(mat)
    return mesh


def _cut_box(bm, sk, m, depth):
    """The opening through the slab: the skylight's size, from above the
    roof's top down past its underside, square to the slope."""
    hw, hl = sk.width / 2.0, sk.length / 2.0
    _box(bm, -hw, hw, -hl, hl, -depth, CUT_ABOVE, m)


def underside_corners(sk, m, thickness):
    """The opening's corners on the roof's underside, in world space."""
    n = Vector((m[0][2], m[1][2], m[2][2]))
    hw, hl = sk.width / 2.0, sk.length / 2.0
    return [m @ Vector((x, y, 0.0)) - n * thickness
            for x, y in ((-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl))]


# ---- What is under it ----------------------------------------------------------------

def room_under(scene, frame, x, y):
    """(level, room) the skylight lights: the highest room under the roof
    whose outline holds its centre, or (None, None)."""
    from . import hb_roofs, hb_rooms, hb_wall_graph
    best = (None, None)
    for lv in sorted(hb_roofs._levels_under(scene, frame), key=lambda l: l.elevation):
        for room in lv.rooms:
            if room.orphaned or room.is_porch or room.ceiling_obj is None:
                continue
            poly = hb_rooms.room_polygon(scene, lv, room)
            if poly and hb_wall_graph.point_in_polygon((x, y), poly):
                best = (lv, room)
    return best


def _shaft_mesh(corners, ceiling_z):
    """A plumb light shaft from the opening's underside down to the ceiling."""
    bm = bmesh.new()
    top = [bm.verts.new(c) for c in corners]
    bottom = [bm.verts.new((c.x, c.y, ceiling_z)) for c in corners]
    for i in range(4):
        j = (i + 1) % 4
        if top[i].co.z - ceiling_z > 1e-3 or top[j].co.z - ceiling_z > 1e-3:
            bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Skylight Shaft")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _shaft_material():
    from .product_libraries.common import door_window_geo
    return door_window_geo._material("HB Skylight Shaft", SHAFT_COLOR, roughness=0.8)


# ---- Building ---------------------------------------------------------------------

def _delete(obj):
    if obj is None or obj.name not in bpy.data.objects:
        return
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def _put(scene, level, current, name, mesh, tag):
    """A visible part kept on the level: made, refilled or removed."""
    if mesh is None:
        _delete(current)
        return None
    if current is None or current.name not in bpy.data.objects:
        obj = hb_utils.new_object(name, mesh)
        hb_house.level_subcollection(level, 'Rooms').objects.link(obj)
        obj[tag] = True
        obj[hb_house.LEVEL_KEY] = level.uid
        return obj
    old = current.data
    current.data = mesh
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    return current


def clear(roof):
    """Take a roof's skylights off it (their settings stay)."""
    for sk in roof.skylights:
        _delete(sk.unit_obj)
        _delete(sk.shaft_obj)
        sk.unit_obj = None
        sk.shaft_obj = None


def rebuild(scene, level, frame=None):
    """Set a level's skylights on its roof: units, the openings cut in the
    main roof, shafts and ceiling cuts below."""
    from . import hb_roofs
    scene = hb_house.house_scene_of(scene)
    roof = level.roof
    if frame is None and roof.enabled:
        frame = hb_roofs.roof_frame(scene, level)
    if frame is None or roof.roof_obj is None:
        clear(roof)
        hb_roofs._helper(scene, roof, 'openings_obj', "", None, hb_roofs.ROOF_CUTTER_KEY)
        hb_roofs._helper(scene, roof, 'skylight_cut_obj', "", None, hb_roofs.ROOF_CUTTER_KEY)
        apply_ceiling_cuts(scene)
        return
    hb_house.ensure_level_collections(scene, level)
    cut_bm, ceil_bm = bmesh.new(), bmesh.new()
    depth = roof.thickness + CUT_ABOVE
    for i in range(len(roof.skylights)):
        sk = roof.skylights[i]
        u, v = hb_roofs._uv(frame, (sk.x, sk.y))
        if not (frame['u0'] <= u <= frame['u1'] and frame['v0'] <= v <= frame['v1']):
            _delete(sk.unit_obj)
            _delete(sk.shaft_obj)
            sk.unit_obj = sk.shaft_obj = None
            continue
        m, _crosses = pose(frame, roof, sk)
        unit = _put(scene, level, sk.unit_obj, sk.name, unit_mesh(sk, sk.name), SKYLIGHT_KEY)
        unit.matrix_world = m
        unit[hb_roofs.ROOF_KEY] = True
        sk.unit_obj = unit
        _cut_box(cut_bm, sk, m, depth)
        corners = underside_corners(sk, m, roof.thickness)
        lv, room = room_under(scene, frame, sk.x, sk.y)
        shaft = None
        if room is not None:
            from . import hb_rooms
            ceiling_z = lv.elevation + hb_rooms.room_height(room, lv)
            if room.ceiling_style != 'VAULTED' and sk.shaft == 'AUTO' \
                    and max(c.z for c in corners) > ceiling_z + 0.01:
                shaft = _shaft_mesh(corners, ceiling_z)
                shaft.materials.append(_shaft_material())
            # The ceiling opened plumb under the opening, whatever its shape
            z0, z1 = lv.elevation + 0.05, max(c.z for c in corners) + 0.05
            vs = [ceil_bm.verts.new((c.x, c.y, z)) for z in (z0, z1) for c in corners]
            for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
                ceil_bm.faces.new([vs[k] for k in f])
        sk = roof.skylights[i]
        sk.shaft_obj = _put(scene, level, sk.shaft_obj, sk.name + " Shaft", shaft, SHAFT_KEY)
    for bm, attr, name in ((cut_bm, 'openings_obj', f"Roof Openings - {level.name}"),
                           (ceil_bm, 'skylight_cut_obj', f"Skylight Ceiling Cuts - {level.name}")):
        mesh = None
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            mesh = bpy.data.meshes.new(name)
            bm.to_mesh(mesh)
        bm.free()
        hb_roofs._helper(scene, roof, attr, name, mesh, hb_roofs.ROOF_CUTTER_KEY)
    hb_roofs._set_boolean(roof.roof_obj, OPENINGS_CUT, roof.openings_obj)
    apply_ceiling_cuts(scene)


def apply_ceiling_cuts(scene):
    """Open every ceiling under a skylight with its roof's ceiling cuts;
    take cuts off ceilings no skylight is over any more."""
    from . import hb_roofs, hb_rooms
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    wanted = {}
    for level in scene.hb_house.levels:
        roof = level.roof
        cutter = roof.skylight_cut_obj
        if cutter is None or not roof.enabled:
            continue
        frame = hb_roofs.roof_frame(scene, level)
        if frame is None:
            continue
        for sk in roof.skylights:
            _lv, room = room_under(scene, frame, sk.x, sk.y)
            if room is not None:
                wanted.setdefault(room.ceiling_obj, {})[CEILING_CUT + level.name] = cutter
    for level in scene.hb_house.levels:
        for room in level.rooms:
            obj = room.ceiling_obj
            if obj is None:
                continue
            keep = wanted.get(obj, {})
            for mod in list(obj.modifiers):
                if mod.type == 'BOOLEAN' and mod.name.startswith(CEILING_CUT) and mod.name not in keep:
                    obj.modifiers.remove(mod)
            for name, cutter in keep.items():
                hb_roofs._set_boolean(obj, name, cutter, True)


def rebuild_of(sk_owner_roof):
    from . import hb_roofs
    level = hb_roofs.level_of_roof(sk_owner_roof)
    scene = hb_house.house_scene_of(bpy.context.scene)
    if level is not None and scene is not None:
        rebuild(scene, level)


def add_skylight(scene, level, x, y, width=None, length=None, curb=None, shaft=None):
    """A new skylight on the level's roof, centred at (x, y)."""
    house = scene.hb_house
    roof = level.roof
    index = len(roof.skylights)
    sk = roof.skylights.add()
    sk.uid = hb_house._new_uid()
    sk.name = f"Skylight {index + 1}"
    sk['x'], sk['y'] = x, y
    sk['width'] = width if width is not None else house.skylight_width
    sk['length'] = length if length is not None else house.skylight_length
    sk.curb = curb or house.skylight_curb
    sk.shaft = shaft or house.skylight_shaft
    roof = hb_house.get_level(level.uid).roof
    roof.active_skylight_index = index
    rebuild(scene, hb_house.get_level(level.uid))
    return index


# ---- Operators ------------------------------------------------------------------------

class HOME_BUILDER_OT_place_skylight(bpy.types.Operator):
    """Click on the roof where a skylight goes: it lies on the slope there"""
    bl_idname = "home_builder.place_skylight"
    bl_label = "Place Skylight"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        return (level is not None and level.roof.enabled and level.roof.roof_obj is not None
                and context.area is not None and context.area.type == 'VIEW_3D')

    def invoke(self, context, event):
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), context.region)
        self.level_uid = hb_house.active_level(context).uid
        self.placed = 0
        self.preview = None
        context.area.header_text_set("Place Skylight: click on the roof   |   Esc / right-click: done")
        tool_session.begin(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _hit(self, context, event):
        """Where the ray under the cursor meets the level's main roof."""
        from bpy_extras import view3d_utils
        from . import hb_roofs
        rv3d = context.region_data
        if rv3d is None:
            for space in context.area.spaces:
                if space.type == 'VIEW_3D':
                    rv3d = space.region_3d
        co = (event.mouse_x - self.region.x, event.mouse_y - self.region.y)
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, co)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, co)
        level = hb_house.get_level(self.level_uid)
        roof_obj = level.roof.roof_obj
        if roof_obj is None:
            return None
        dg = context.evaluated_depsgraph_get()
        from mathutils.bvhtree import BVHTree
        tree = BVHTree.FromObject(roof_obj, dg)
        m = roof_obj.matrix_world
        inv = m.inverted()
        hit = tree.ray_cast(inv @ origin, (inv.to_3x3() @ direction).normalized())
        return None if hit[0] is None else m @ hit[0]

    def _show(self, context, point):
        from . import hb_roofs
        level = hb_house.get_level(self.level_uid)
        frame = hb_roofs.roof_frame(context.scene, level)
        if point is None or frame is None:
            if self.preview is not None:
                self.preview.hide_set(True)
            return

        class _Probe:
            pass
        sk = _Probe()
        house = context.scene.hb_house
        sk.x, sk.y, sk.width, sk.length = point.x, point.y, house.skylight_width, house.skylight_length
        sk.curb = house.skylight_curb
        m, _crosses = pose(frame, level.roof, sk)
        mesh = unit_mesh(sk, "Skylight Preview")
        if self.preview is None:
            self.preview = hb_utils.new_object("Skylight Preview", mesh)
            context.scene.collection.objects.link(self.preview)
            self.preview.display_type = 'WIRE'
            self.preview.hide_select = True
        else:
            old = self.preview.data
            self.preview.data = mesh
            if old.users == 0:
                bpy.data.meshes.remove(old)
        self.preview.hide_set(False)
        self.preview.matrix_world = m

    def cleanup(self, context):
        _delete(self.preview)
        self.preview = None
        context.area.header_text_set(None)

    def stop_tool(self, context):
        self.cleanup(context)
        return {'CANCELLED'}

    @tool_session.session_modal
    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        level = hb_house.get_level(self.level_uid)
        if level is None or not level.roof.enabled:
            self.cleanup(context)
            return {'CANCELLED'}
        if self.preview is not None:
            self.preview.hide_set(True)
        point = self._hit(context, event)
        self._show(context, point)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if point is None:
                return {'RUNNING_MODAL'}
            add_skylight(context.scene, level, point.x, point.y)
            self.placed += 1
            if tool_session.stays_on(context):
                return {'RUNNING_MODAL'}
            self.cleanup(context)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cleanup(context)
            return {'FINISHED'} if self.placed else {'CANCELLED'}
        return {'PASS_THROUGH'}


class HOME_BUILDER_OT_remove_skylight(bpy.types.Operator):
    bl_idname = "home_builder.remove_skylight"
    bl_label = "Remove Skylight"
    bl_description = "Remove the active skylight from the level's roof"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        return level is not None and 0 <= level.roof.active_skylight_index < len(level.roof.skylights)

    def execute(self, context):
        level = hb_house.active_level(context)
        roof = level.roof
        sk = roof.skylights[roof.active_skylight_index]
        _delete(sk.unit_obj)
        _delete(sk.shaft_obj)
        roof.skylights.remove(roof.active_skylight_index)
        roof.active_skylight_index = max(0, min(roof.active_skylight_index, len(roof.skylights) - 1))
        rebuild(context.scene, hb_house.get_level(level.uid))
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_place_skylight,
    HOME_BUILDER_OT_remove_skylight,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
