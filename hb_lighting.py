"""Lighting in a house's rooms: the light fixtures the Furnish tool places
(product_libraries/interiors), and the room commands that place many at
once - a grid of recessed cans, a centre fixture for the kind of room -
or take them out again, with the house's switches for all of them.
"""

import math

import bpy
from mathutils import Vector

from . import hb_house, hb_types

GRID_SPACING = 1.83         # 6' between cans
GRID_EDGE = 0.6             # 2' in from the walls
GRID_KEY = 'HB_LIGHT_GRID'  # on a can a room's grid laid: the room's uid


def _lg():
    from .product_libraries.interiors import lighting_geo
    return lighting_geo


def is_fixture(obj):
    return obj is not None and bool(obj.get(_lg().FIXTURE_KEY))


def fixture_of(obj):
    while obj is not None:
        if is_fixture(obj):
            return obj
        obj = obj.parent
    return None


def _centre(cage):
    """A fixture's plan centre, good on one made a moment ago."""
    from .operators import ops_furnish
    c = ops_furnish._centre_local(cage)
    m = cage.matrix_basis if cage.parent is None else cage.parent.matrix_world @ cage.matrix_basis
    p = m @ c
    return p.x, p.y


def room_fixtures(scene, level, room):
    """The fixtures in a room: on its level, their middles in its outline."""
    from . import hb_rooms, hb_wall_graph
    poly = hb_rooms.room_polygon(scene, level, room)
    if not poly:
        return []
    out = []
    for obj in scene.objects:
        if is_fixture(obj) and obj.get(hb_house.LEVEL_KEY) == level.uid:
            if hb_wall_graph.point_in_polygon(_centre(obj), poly):
                out.append(obj)
    return out


def grid_points(polygon, spacing=GRID_SPACING, edge=GRID_EDGE):
    """Where a grid of cans goes in a room: evenly over its box, in from
    the walls by `edge`, no further apart than `spacing`, those that fall
    in the room's outline (the rule Add Room Lights has used)."""
    from . import hb_wall_graph
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    uw, ud = (x1 - x0) - 2 * edge, (y1 - y0) - 2 * edge
    nx = max(1, int(uw / spacing) + 1) if uw > 0 else 1
    ny = max(1, int(ud / spacing) + 1) if ud > 0 else 1
    out = []
    for i in range(nx):
        x = (x0 + x1) / 2.0 if nx == 1 else x0 + edge + i * uw / (nx - 1)
        for j in range(ny):
            y = (y0 + y1) / 2.0 if ny == 1 else y0 + edge + j * ud / (ny - 1)
            if hb_wall_graph.point_in_polygon((x, y), polygon):
                out.append((x, y))
    return out


def centre_kind(room):
    """The fixture a room's centre takes: by its type, else its name."""
    t = room.room_type
    name = room.name.lower()
    if t == 'DINING' or 'dining' in name:
        return 'CHANDELIER'
    if t in ('BEDROOM', 'GREAT', 'FAMILY', 'LIVING') or any(w in name for w in ('bed', 'living', 'family', 'great')):
        return 'CEILING_FAN'
    return 'FLUSH_MOUNT'


def _place(context, key, x, y):
    from .operators import ops_furnish
    return ops_furnish.place_item(context, key, point=(x, y))


def grid_fixtures(scene, level, room):
    """The cans of a room's grid: those its grid laid, or, in a room
    whose grid came before they were marked, its recessed cans."""
    fixtures = room_fixtures(scene, level, room)
    mine = [f for f in fixtures if f.get(GRID_KEY) == room.uid]
    if mine:
        return mine
    return [f for f in fixtures if f.get(_lg().KIND_KEY) == 'RECESSED' and not f.get(GRID_KEY)]


def add_recessed_grid(context, level, room, spacing=None, edge=None):
    """Lay a room's grid of cans at its Spacing and From Walls, in place
    of the grid it had (whose cans' brightness and colour the new ones
    keep)."""
    from . import hb_rooms
    scene = hb_house.house_scene_of(context.scene)
    poly = hb_rooms.room_polygon(scene, level, room)
    if not poly:
        return []
    spacing = room.light_spacing if spacing is None else spacing
    edge = room.light_from_walls if edge is None else edge
    keep = {}
    for old in grid_fixtures(scene, level, room):
        for key in (_lg().LUMENS_KEY, _lg().KELVIN_KEY):
            if key in old:
                keep.setdefault(key, old[key])
        delete_fixture(old)
    made = []
    for x, y in grid_points(poly, spacing, edge):
        cage = _place(context, 'RECESSED', x, y)
        if cage is None:
            continue
        cage[GRID_KEY] = room.uid
        if keep:
            for key, value in keep.items():
                cage[key] = value
            _lg().build(cage)
        made.append(cage)
    return made


def level_of(scene, room):
    return next((l for l in scene.hb_house.levels if room in list(l.rooms)), None) if scene else None


def grid_changed(room, context):
    """A room's Spacing or From Walls changed: its grid, if it has one,
    laid again."""
    scene = hb_house.house_scene_of(context.scene)
    level = level_of(scene, room)
    if level is not None and grid_fixtures(scene, level, room):
        add_recessed_grid(context, level, room)


# ---- Blender's light objects in the viewport --------------------------------------

def _views():
    wm = bpy.context.window_manager
    for window in wm.windows if wm else ():
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                yield area.spaces.active


def light_objects_shown(_self=None):
    """Whether the viewport draws Blender's light objects (its Extras
    overlay: lights, cameras and empties)."""
    return next((v.overlay.show_extras for v in _views()), True)


def show_light_objects(_self, value):
    for v in _views():
        v.overlay.show_extras = bool(value)


def add_centre_fixture(context, level, room):
    from . import hb_rooms, hb_wall_graph
    scene = hb_house.house_scene_of(context.scene)
    poly = hb_rooms.room_polygon(scene, level, room)
    if not poly:
        return None
    x, y = hb_wall_graph.interior_point(poly)
    return _place(context, centre_kind(room), x, y)


def delete_fixture(cage):
    for o in [cage] + list(cage.children_recursive):
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if isinstance(data, bpy.types.Mesh) and data.users == 0:
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Light) and data.users == 0:
            bpy.data.lights.remove(data)


def remove_room_lights(context, level, room):
    scene = hb_house.house_scene_of(context.scene)
    gone = room_fixtures(scene, level, room)
    for cage in gone:
        delete_fixture(cage)
    return len(gone)


def room_summary(context, room):
    """'4 fixtures, 3,200 lm' for a room, or ''."""
    scene = hb_house.house_scene_of(context.scene)
    level = next((l for l in scene.hb_house.levels if room in list(l.rooms)), None) if scene else None
    if level is None:
        return ""
    fixtures = room_fixtures(scene, level, room)
    if not fixtures:
        return "No fixtures"
    lumens = sum(float(f.get(_lg().LUMENS_KEY, 0.0)) for f in fixtures)
    return f"{len(fixtures)} fixture{'s' if len(fixtures) != 1 else ''}, {lumens:,.0f} lm"


# ---- A fixture's own settings ---------------------------------------------------------

def _fixture_prop(key, cast=float):
    def get(self):
        return cast(self.id_data.get(key, 0))

    def set(self, value):
        self.id_data[key] = cast(value)
        _lg().build(self.id_data)
    return get, set


def _cage_dim(name):
    def get(self):
        c = hb_types.GeoNodeCage(self.id_data)
        return c.get_input(name) if c.has_modifier() else 0.0

    def set(self, value):
        hb_types.GeoNodeCage(self.id_data).set_input(name, value)
        _lg().build(self.id_data)
    return get, set


_lumens = _fixture_prop('FIXTURE_LUMENS')
_kelvin = _fixture_prop('FIXTURE_KELVIN')
_width = _cage_dim('Dim X')
_depth = _cage_dim('Dim Y')
_height = _cage_dim('Dim Z')


class HB_LightFixture(bpy.types.PropertyGroup):
    """A light fixture's settings, read from and written to its cage."""
    lumens: bpy.props.FloatProperty(name="Lumens", min=50.0, max=20000.0, precision=0,
                                    get=_lumens[0], set=_lumens[1])  # type: ignore
    kelvin: bpy.props.FloatProperty(name="Color Temperature (K)", min=1800.0, max=6500.0, precision=0,
                                    get=_kelvin[0], set=_kelvin[1])  # type: ignore
    width: bpy.props.FloatProperty(name="Width", min=0.05, max=3.0, subtype='DISTANCE', precision=4,
                                   get=_width[0], set=_width[1])  # type: ignore
    depth: bpy.props.FloatProperty(name="Depth", min=0.05, max=3.0, subtype='DISTANCE', precision=4,
                                   get=_depth[0], set=_depth[1])  # type: ignore
    height: bpy.props.FloatProperty(name="Height (Drop)", min=0.02, max=2.0, subtype='DISTANCE',
                                    precision=4, get=_height[0], set=_height[1])  # type: ignore


def house_switches_changed(self, context):
    _lg().apply_house_switches()


# ---- Operators -------------------------------------------------------------------------

def _active_room(context):
    level = hb_house.active_level(context)
    if level is None or not (0 <= level.active_room_index < len(level.rooms)):
        return None, None
    return level, level.rooms[level.active_room_index]


class HOME_BUILDER_OT_add_recessed_grid(bpy.types.Operator):
    bl_idname = "home_builder.add_recessed_grid"
    bl_label = "Add Recessed Grid"
    bl_description = ("Recessed cans over the active room at its Spacing and From Walls, "
                      "in place of the grid it has")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_room(context)[1] is not None

    def execute(self, context):
        level, room = _active_room(context)
        made = add_recessed_grid(context, level, room)
        self.report({'INFO'}, f"{len(made)} recessed cans in {room.name}")
        return {'FINISHED'}


class HOME_BUILDER_OT_add_centre_fixture(bpy.types.Operator):
    bl_idname = "home_builder.add_center_fixture"
    bl_label = "Add Center Fixture"
    bl_description = ("A fixture in the middle of the active room: a chandelier in a dining "
                      "room, a fan in a bedroom or living room, a flush mount elsewhere")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_room(context)[1] is not None

    def execute(self, context):
        level, room = _active_room(context)
        add_centre_fixture(context, level, room)
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_room_lights(bpy.types.Operator):
    bl_idname = "home_builder.remove_room_lights"
    bl_label = "Remove Room Lights"
    bl_description = "Take every light fixture out of the active room"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return _active_room(context)[1] is not None

    def execute(self, context):
        level, room = _active_room(context)
        n = remove_room_lights(context, level, room)
        self.report({'INFO'}, f"Removed {n} fixture{'s' if n != 1 else ''}")
        return {'FINISHED'}


class HOME_BUILDER_OT_delete_light_fixture(bpy.types.Operator):
    bl_idname = "home_builder.delete_light_fixture"
    bl_label = "Delete Light"
    bl_description = "Delete the light fixture and its lights"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return fixture_of(context.active_object) is not None

    def execute(self, context):
        delete_fixture(fixture_of(context.active_object))
        return {'FINISHED'}


class HOME_BUILDER_MT_light_fixture_commands(bpy.types.Menu):
    bl_label = "Light Fixture"
    bl_idname = "HOME_BUILDER_MT_light_fixture_commands"

    def draw(self, context):
        self.layout.operator("home_builder.delete_light_fixture", icon='X')


classes = (
    HB_LightFixture,
    HOME_BUILDER_OT_add_recessed_grid,
    HOME_BUILDER_OT_add_centre_fixture,
    HOME_BUILDER_OT_remove_room_lights,
    HOME_BUILDER_OT_delete_light_fixture,
    HOME_BUILDER_MT_light_fixture_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_light = bpy.props.PointerProperty(type=HB_LightFixture)


def unregister():
    if hasattr(bpy.types.Object, 'hb_light'):
        del bpy.types.Object.hb_light
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
