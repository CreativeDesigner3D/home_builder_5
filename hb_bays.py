"""Bay, bow and box windows.

A bay is placed on an outside wall like a window: a GeoNodeCage
parented to the host wall, tagged IS_BAY_BP, cutting the host from the
bay's floor (or seat) up to its head; the host wall stays one wall. Its
settings are Object.hb_bay. From them each rebuild makes:

- the bay's walls, one per side of its outline (hb_bay_geom): real
  GeoNodeWalls of type 'Bay', thickness inward, their corners mitred and
  their ends cut to the host's face. They are kept and moved, not
  remade, so windows the user adds to them stay;
- a window in each side, made by the bay and fitted to it;
- a floor (or a seat with a sided underside), and a ceiling;
- a small hip or shed roof, its host side against the wall.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from . import hb_bay_geom, hb_house, hb_types, hb_utils
from .units import inch

BAY_KEY = 'IS_BAY_BP'
BAY_UID = 'HB_BAY_UID'
BAY_SEG = 'HB_BAY_SEG'
BAY_WINDOW = 'HB_BAY_WINDOW'
PART_KEY = 'IS_BAY_PART'
WALL_TYPE = 'Bay'
MENU_ID = "HOME_BUILDER_MT_bay_window_commands"

HEADER = inch(10)               # the bay's walls above its windows' heads
SKIRT = inch(14)                # a seat bay's walls run this far below the seat
MULL = inch(2)                  # a window stops this far short of its side's corners
MIN_WINDOW = 0.2
MAX_WALL = inch(6)              # the bay's walls are no thicker than this
SEAT_T = inch(1.5)
CEILING_T = inch(0.5)
UNDERSIDE_T = inch(1.5)
OVERHANG = inch(6)
ROOF_T = inch(5)

KIND_ITEMS = [
    ('BAY', "Bay", "Angled sides and a front parallel to the wall"),
    ('BOW', "Bow", "A curve of narrow sides"),
    ('BOX', "Box", "Square sides"),
]
BASE_ITEMS = [
    ('FLOOR', "Floor", "The bay comes down to the floor"),
    ('SEAT', "Seat", "The bay stands out above the floor, a seat inside it"),
]
ROOF_ITEMS = [
    ('HIP', "Hip", "Slopes on every side away from the wall"),
    ('SHED', "Shed", "One slope down from the wall"),
    ('NONE', "None", "No roof of its own (under the eaves, or a floor above)"),
]


# ---- Where everything is -------------------------------------------------------------

def is_bay(obj):
    return obj is not None and bool(obj.get(BAY_KEY))


def bay_of(obj):
    """The bay an object is, belongs to or stands in; None otherwise."""
    while obj is not None:
        if is_bay(obj):
            return obj
        uid = obj.get(BAY_UID)
        if uid:
            return next((o for o in bpy.data.objects if is_bay(o) and o.hb_bay.uid == uid), None)
        obj = obj.parent
    return None


def _cage_matrix(cage):
    if cage.parent is not None:
        return cage.parent.matrix_world @ cage.matrix_parent_inverse @ cage.matrix_basis
    return cage.matrix_basis.copy()


def _level(cage):
    host = cage.parent
    uid = host.get(hb_house.LEVEL_KEY, '') if host is not None else ''
    return hb_house.get_level(uid) if uid else None


class Frame:
    """The bay's own plan coordinates (x along the host from the bay's
    left end, o out from the host's outdoor face) in world space, and its
    heights above the level's floor."""

    def __init__(self, cage):
        from . import hb_exterior
        bay = cage.hb_bay
        c = hb_types.GeoNodeCage(cage)
        self.W = c.get_input('Dim X')
        self.T = c.get_input('Dim Y')
        host = cage.parent
        side = hb_exterior.outdoor_side(host) if host is not None else None
        self.sgn = -1.0 if side == 'REF' else 1.0
        self.face = 0.0 if side == 'REF' else self.T
        # Without the cage's own z: heights are the level's
        m = _cage_matrix(cage)
        m.translation.z -= cage.location.z
        self.m = m
        level = _level(cage)
        self.elev = level.elevation if level is not None else (host.matrix_world.translation.z if host else 0.0)
        self.head = bay.head_height
        self.top = bay.head_height + HEADER
        if bay.base == 'SEAT':
            self.base = bay.seat_height
            self.bottom = max(bay.seat_height - SKIRT, 0.05)
        else:
            self.base = self.bottom = 0.0
        self.tw = min(self.T, MAX_WALL)
        self.pts = hb_bay_geom.bay_plan(bay.kind, self.W, bay.projection,
                                        math.radians(bay.side_angle), bay.segments)
        self.inner = hb_bay_geom.offset(self.pts, self.tw)

    def xy(self, x, o):
        p = self.m @ Vector((x, self.face + self.sgn * o, 0.0))
        return Vector((p.x, p.y))

    def at(self, x, o, z):
        """A world point at height z above the level's floor."""
        p = self.xy(x, o)
        return Vector((p.x, p.y, self.elev + z))


# ---- Building ---------------------------------------------------------------------------

def _delete_tree(obj):
    """An object, everything under it, and the Booleans that cut with them."""
    if obj is None or obj.name not in bpy.data.objects:
        return
    doomed = [obj] + list(obj.children_recursive)
    names = {o.name for o in doomed}
    for other in bpy.data.objects:
        for mod in list(getattr(other, 'modifiers', ())):
            if mod.type == 'BOOLEAN' and mod.object is not None and mod.object.name in names:
                other.modifiers.remove(mod)
    for o in reversed(doomed):
        data = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


def bay_walls(cage):
    uid = cage.hb_bay.uid
    return sorted((o for o in bpy.data.objects if o.get('IS_WALL_BP') and o.get(BAY_UID) == uid),
                  key=lambda o: o.get(BAY_SEG, 0))


def _parts(cage, tag):
    uid = cage.hb_bay.uid
    return next((o for o in bpy.data.objects if o.get(PART_KEY) == tag and o.get(BAY_UID) == uid), None)


def _wall_ends(F, i):
    """(start, direction, length, left angle, right angle) of side i's
    wall: from its outline corners, the thickness to its left (inward),
    its inside face cut where it meets the next side's or the host's."""
    A, B = F.xy(*F.pts[i]), F.xy(*F.pts[i + 1])
    QA, QB = F.xy(*F.inner[i]), F.xy(*F.inner[i + 1])
    u = (B - A).normalized()
    n = Vector((-u.y, u.x))
    if ((QA + QB) / 2.0 - (A + B) / 2.0).dot(n) < 0.0:
        A, B, QA, QB = B, A, QB, QA
        u, n = -u, -n
    t = F.tw
    s_a = (QA - (A + n * t)).dot(u)
    s_b = (QB - (B + n * t)).dot(u)
    return A, u, (B - A).length, math.atan2(s_a, t), math.atan2(s_b, t), s_a, s_b


def _place_walls(scene, cage, F, level):
    from . import hb_roofs
    uid = cage.hb_bay.uid
    have = {w.get(BAY_SEG, -1): w for w in bay_walls(cage)}
    n = len(F.pts) - 1
    walls = []
    for i in range(n):
        A, u, length, la, ra, s_a, s_b = _wall_ends(F, i)
        obj = have.pop(i, None)
        if obj is None:
            wall = hb_types.GeoNodeWall()
            wall.create("Bay Wall")
            obj = wall.obj
            obj['WALL_TYPE'] = WALL_TYPE
            obj[BAY_UID] = uid
            obj[BAY_SEG] = i
            if level is not None:
                hb_house.assign_wall_to_level(obj, level, scene)
        wall = hb_types.GeoNodeWall(obj)
        wall.set_input('Length', length)
        wall.set_input('Thickness', F.tw)
        wall.set_input('Height', F.top - F.bottom)
        wall.set_input('Left Angle', la)
        wall.set_input('Right Angle', ra)
        if wall.has_input('Left Extension'):
            wall.set_input('Left Extension', 0.0)
            wall.set_input('Right Extension', 0.0)
        obj.location = (A.x, A.y, F.elev + F.bottom)
        obj.rotation_euler = (0.0, 0.0, math.atan2(u.y, u.x))
        if level is not None:
            hb_roofs._wall_inputs_like(scene, level, obj)
        obj.update_tag()
        walls.append((obj, length, s_a, s_b))
    for obj in have.values():
        _delete_tree(obj)
    return walls


def _fit_windows(context, cage, F, walls):
    """A window in each side, as wide as the side allows, sill to head."""
    from .operators import doors_windows
    from .product_libraries.common import door_window_geo
    bay = cage.hb_bay
    sill = (bay.seat_height + SEAT_T + inch(1)) if bay.base == 'SEAT' else bay.sill_height
    height = F.head - sill
    for i, (wall_obj, length, s_a, s_b) in enumerate(walls):
        lo = max(0.0, s_a) + MULL
        hi = min(length, length + s_b) - MULL
        width = hi - lo
        win = next((c for c in wall_obj.children if c.get(BAY_WINDOW)), None)
        if width < MIN_WINDOW or height < MIN_WINDOW:
            _delete_tree(win)
            continue
        z = sill - F.bottom
        if win is None:
            win = doors_windows.place_wall_object(context, wall_obj, 'WINDOW', lo, width=width,
                                                  height=height, z=z)
            win[BAY_WINDOW] = True
            win[BAY_UID] = bay.uid
            continue
        c = hb_types.GeoNodeCage(win)
        c.set_input('Dim X', width)
        c.set_input('Dim Z', height)
        c.set_input('Dim Y', F.tw)
        win.location = (lo, 0.0, z)
        door_window_geo.build_geometry(win)


def _prism(bm, pts, z0, z1, mat):
    if z1 - z0 <= 1e-6 or len(pts) < 3:
        return
    b = [bm.verts.new((p.x, p.y, z0)) for p in pts]
    t = [bm.verts.new((p.x, p.y, z1)) for p in pts]
    bm.faces.new(b).material_index = mat
    bm.faces.new(t).material_index = mat
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((b[i], b[j], t[j], t[i])).material_index = mat


def _put(scene, level, cage, tag, name, mesh):
    obj = _parts(cage, tag)
    if mesh is None:
        _delete_tree(obj)
        return None
    if obj is None:
        obj = hb_utils.new_object(name, mesh)
        if level is not None:
            hb_house.ensure_level_collections(scene, level)
            hb_house.level_subcollection(level, 'Walls').objects.link(obj)
            obj[hb_house.LEVEL_KEY] = level.uid
        else:
            scene.collection.objects.link(obj)
        obj[PART_KEY] = tag
        obj[BAY_UID] = cage.hb_bay.uid
        obj['MENU_ID'] = MENU_ID
    else:
        old = obj.data
        obj.data = mesh
        if old is not None and old.users == 0:
            bpy.data.meshes.remove(old)
    return obj


def _host_floor_material(scene, level):
    from . import hb_rooms
    for room in (level.rooms if level is not None else ()):
        if room.floor_obj is not None and room.floor_obj.data.materials:
            return room.floor_obj.data.materials[0]
    from .product_libraries.common import door_window_geo
    return door_window_geo._material("HB Bay Floor", (0.55, 0.42, 0.30))


def _build_parts(scene, cage, F, level):
    """Floor or seat and underside, and the ceiling: over the inside of
    the bay and the host wall's opening."""
    from . import hb_exterior, hb_rooms
    from .product_libraries.common import door_window_geo
    bay = cage.hb_bay
    inside = [F.xy(x, o) for x, o in F.inner]
    inside += [F.xy(F.inner[-1][0], -F.T), F.xy(F.inner[0][0], -F.T)]
    bm = bmesh.new()
    e = F.elev
    if bay.base == 'FLOOR':
        slab = hb_rooms.floor_slab_thickness(level) if level is not None else 0.05
        _prism(bm, inside, e - slab, e, 0)
    else:
        _prism(bm, inside, e + F.base, e + F.base + SEAT_T, 1)
        outline = [F.xy(x, o) for x, o in F.pts]
        _prism(bm, outline, e + F.bottom - UNDERSIDE_T, e + F.bottom, 2)
    _prism(bm, inside, e + F.top - CEILING_T, e + F.top, 1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("Bay")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(_host_floor_material(scene, level))
    mesh.materials.append(door_window_geo._trim_material())
    mesh.materials.append(hb_exterior.trim_material())
    _put(scene, level, cage, 'PARTS', f"{cage.name} Inside", mesh)


def _build_roof(scene, cage, F, level):
    """A hip or shed over the bay, from its walls' tops out past them by
    the overhang, its host side against the wall."""
    from . import hb_roofs
    bay = cage.hb_bay
    if bay.roof == 'NONE':
        _put(scene, level, cage, 'ROOF', "", None)
        return
    p = bay.roof_pitch / 12.0
    plate = F.elev + F.top
    tv = ROOF_T / math.cos(math.atan(p))
    poly = hb_bay_geom.offset(F.pts, -OVERHANG)
    if bay.roof == 'HIP':
        facets = [f for f, _i in hb_bay_geom.hip_facets(F.pts, poly, p)]
        rise = lambda q: hb_bay_geom.hip_height(F.pts, p, q)
    else:
        depth = max(o for _x, o in F.pts)
        facets = [poly if hb_bay_geom.area(poly) > 0 else list(reversed(poly))]
        rise = lambda q: p * (depth - q[1])
    edges = {}
    key = lambda q: (round(q[0], 6), round(q[1], 6))
    for f in facets:
        for a, b in zip(f, f[1:] + f[:1]):
            k = tuple(sorted((key(a), key(b))))
            edges[k] = edges.get(k, 0) + 1
    faces = []
    for f in facets:
        bottom = [F.at(q[0], q[1], 0.0) for q in f]
        for v, q in zip(bottom, f):
            v.z = plate + rise(q)
        top = [v + Vector((0.0, 0.0, tv)) for v in bottom]
        faces.append(list(reversed(bottom)))
        faces.append(top)
        for k in range(len(f)):
            j = (k + 1) % len(f)
            if edges[tuple(sorted((key(f[k]), key(f[j]))))] == 1:
                faces.append((bottom[k], bottom[j], top[j], top[k]))
    mesh = hb_roofs._solid("Bay Roof", faces)
    roof = level.roof if level is not None else None
    mesh.materials.append((roof.material if roof is not None else None) or hb_roofs._shingles())
    obj = _put(scene, level, cage, 'ROOF', f"{cage.name} Roof", mesh)
    obj.color = tuple(mesh.materials[0].diffuse_color)


def _cut_host(cage, F):
    from .operators import doors_windows
    c = hb_types.GeoNodeCage(cage)
    cage.location.z = F.base
    c.set_input('Dim Z', F.top - F.base)
    if cage.parent is not None:
        doors_windows.cut_wall(cage.parent, cage)
    cage.hide_render = True


def rebuild(cage, context=None):
    """Make or move everything a bay is from its settings."""
    if not is_bay(cage) or cage.parent is None:
        return
    context = context or bpy.context
    scene = hb_house.house_scene_of(context.scene) or context.scene
    if not hb_types.GeoNodeCage(cage).has_modifier():
        return
    if not cage.hb_bay.uid:
        cage.hb_bay.uid = hb_house._new_uid()
    level = _level(cage)
    F = Frame(cage)
    _cut_host(cage, F)
    walls = _place_walls(scene, cage, F, level)
    context.view_layer.update()
    _fit_windows(context, cage, F, walls)
    _build_parts(scene, cage, F, level)
    _build_roof(scene, cage, F, level)


def bays(scene):
    return [o for o in scene.objects if is_bay(o)]


def rebuild_all(scene):
    """Every bay to its host wall as it is now (after walls change)."""
    for cage in bays(scene):
        rebuild(cage)


def changed(cage):
    rebuild(cage)
    scene = hb_house.house_scene_of(bpy.context.scene)
    if scene is not None:
        from . import hb_exterior
        hb_exterior.apply_exterior_finish(scene)


def place(context, cage):
    """A bay just dropped on a wall: it takes the tool's settings."""
    house = context.scene.hb_house
    cage[BAY_KEY] = True
    cage['MENU_ID'] = MENU_ID
    b = cage.hb_bay
    b['uid'] = hb_house._new_uid()
    b['kind'] = [i[0] for i in KIND_ITEMS].index(house.bay_kind)
    b['projection'] = house.bay_projection
    b['side_angle'] = house.bay_side_angle
    b['segments'] = house.bay_segments
    b['base'] = [i[0] for i in BASE_ITEMS].index(house.bay_base)
    b['seat_height'] = house.bay_seat_height
    b['head_height'] = house.bay_head_height
    b['roof'] = [i[0] for i in ROOF_ITEMS].index(house.bay_roof)
    b['roof_pitch'] = house.bay_roof_pitch
    changed(cage)


def delete(cage):
    """Take a bay out: its walls and their windows, inside, roof and cut."""
    uid = cage.hb_bay.uid
    for obj in [o for o in bpy.data.objects if o.get(BAY_UID) == uid and o.parent is None]:
        _delete_tree(obj)
    for obj in [o for o in bpy.data.objects if o.get(BAY_UID) == uid]:
        _delete_tree(obj)
    _delete_tree(cage)


def warning(cage):
    """What's wrong with the bay, or ''."""
    from . import hb_roofs
    scene = hb_house.house_scene_of(bpy.context.scene)
    level = _level(cage)
    bay = cage.hb_bay
    if scene is None or level is None or bay.roof == 'NONE':
        return ""
    F = Frame(cage)
    p = bay.roof_pitch / 12.0
    depth = max(o for _x, o in F.pts)
    top = F.elev + F.top + p * (depth if bay.roof == 'SHED' else
                                hb_bay_geom.hip_height(F.pts, p, (F.W / 2.0, 0.0)))
    point = F.xy(F.W / 2.0, 0.05)
    for lv in scene.hb_house.levels:
        frame = hb_roofs.roof_frame(scene, lv) if lv.roof.enabled else None
        if frame is None:
            continue
        u, v = hb_roofs._uv(frame, (point.x, point.y))
        if frame['u0'] - lv.roof.eave_overhang <= u <= frame['u1'] + lv.roof.eave_overhang \
                and frame['v0'] - 1.0 <= v <= frame['v1'] + 1.0:
            if top > hb_roofs.under_z_at(frame, min(max(u, frame['u0']), frame['u1']), v):
                return "Runs into the eaves: lower the head or set Roof to None"
    return ""


# ---- Settings ----------------------------------------------------------------------------

def _settings_changed(self, context):
    changed(self.id_data)


def _get_width(self):
    c = hb_types.GeoNodeCage(self.id_data)
    return c.get_input('Dim X') if c.has_modifier() else 0.0


def _set_width(self, value):
    hb_types.GeoNodeCage(self.id_data).set_input('Dim X', value)
    changed(self.id_data)


class HB_Bay(bpy.types.PropertyGroup):
    """A bay, bow or box window's settings (see hb_bays)."""
    uid: bpy.props.StringProperty(name="Bay ID")  # type: ignore
    kind: bpy.props.EnumProperty(name="Kind", items=KIND_ITEMS, default='BAY',
                                 update=_settings_changed)  # type: ignore
    width: bpy.props.FloatProperty(
        name="Width", description="Along the wall", min=0.6, max=8.0,
        subtype='DISTANCE', precision=4, get=_get_width, set=_set_width)  # type: ignore
    projection: bpy.props.FloatProperty(
        name="Projection", description="How far it stands out from the wall",
        default=inch(24), min=inch(8), max=inch(72), subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore
    side_angle: bpy.props.FloatProperty(
        name="Side Angle", description="A bay's sides, in degrees to the wall",
        default=45.0, min=20.0, max=80.0, update=_settings_changed)  # type: ignore
    segments: bpy.props.IntProperty(
        name="Segments", description="A bow's sides", default=5, min=3, max=9,
        update=_settings_changed)  # type: ignore
    base: bpy.props.EnumProperty(name="Base", items=BASE_ITEMS, default='FLOOR',
                                 update=_settings_changed)  # type: ignore
    seat_height: bpy.props.FloatProperty(
        name="Seat Height", default=inch(18), min=inch(10), max=inch(42),
        subtype='DISTANCE', precision=4, update=_settings_changed)  # type: ignore
    sill_height: bpy.props.FloatProperty(
        name="Sill Height", description="The windows' sills, above the floor",
        default=inch(18), min=0.0, max=inch(48), subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore
    head_height: bpy.props.FloatProperty(
        name="Head Height", description="The windows' heads, above the floor",
        default=inch(80), min=inch(48), max=inch(120), subtype='DISTANCE', precision=4,
        update=_settings_changed)  # type: ignore
    roof: bpy.props.EnumProperty(name="Roof", items=ROOF_ITEMS, default='HIP',
                                 update=_settings_changed)  # type: ignore
    roof_pitch: bpy.props.FloatProperty(
        name="Roof Pitch", description="Rise in 12", default=6.0, min=1.0, max=18.0,
        precision=2, update=_settings_changed)  # type: ignore


# ---- Operators ------------------------------------------------------------------------------

class HOME_BUILDER_OT_delete_bay_window(bpy.types.Operator):
    bl_idname = "home_builder.delete_bay_window"
    bl_label = "Delete Bay Window"
    bl_description = "Delete the bay with its walls, windows, inside and roof"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bay_of(context.active_object) is not None

    def execute(self, context):
        delete(bay_of(context.active_object))
        return {'FINISHED'}


class HOME_BUILDER_MT_bay_window_commands(bpy.types.Menu):
    bl_label = "Bay Window"
    bl_idname = MENU_ID

    def draw(self, context):
        self.layout.operator("home_builder.delete_bay_window", icon='X')


classes = (
    HB_Bay,
    HOME_BUILDER_OT_delete_bay_window,
    HOME_BUILDER_MT_bay_window_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_bay = bpy.props.PointerProperty(type=HB_Bay)


def unregister():
    if hasattr(bpy.types.Object, 'hb_bay'):
        del bpy.types.Object.hb_bay
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
