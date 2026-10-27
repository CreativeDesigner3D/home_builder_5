"""
Home Builder House Projects and Levels

A house project models a whole house in one scene (the house scene),
split into levels stacked by elevation. Walls stay ordinary GeoNodeWalls;
each one is tagged with the level it belongs to and kept in that level's
Walls collection. See docs/house_levels_and_wall_graph.md.

Everything here is inert in a rooms project: level_of() returns '' for
untagged objects, so code that compares levels treats every wall in an
old file as being on the same (unnamed) level.

Usage:
    from . import hb_house

    level = hb_house.active_level(context)      # None outside a house
    if hb_house.same_level(wall_a, wall_b): ...
"""

import math
import re
import uuid

import bpy
import gpu
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from . import hb_project
from . import hb_plan_views
from .units import inch

LEVEL_KEY = 'HB_LEVEL'
HOUSE_SCENE_KEY = 'IS_HOUSE_SCENE'
# A room view is a scene for working on one room: it links its level's
# collections from the house scene, so its walls and cabinets ARE the
# house's (see hb_rooms.open_room_view). Tagged with the level and room.
ROOM_VIEW_KEY = 'IS_ROOM_VIEW'
ROOM_KEY = 'HB_ROOM'

# Sub-collections every level owns. The names mirror
# rooms.organize_room_collections so code that looks for
# "Walls/Products/Lights" by suffix keeps working.
LEVEL_SUBCOLLECTIONS = ('Walls', 'Products', 'Rooms', 'Lights')

GHOST_COLOR = (0.55, 0.55, 0.55, 0.6)


# =============================================================================
# LOOKUPS
# =============================================================================

def is_house_project(context=None):
    project = hb_project.get_project_props(context)
    return project is not None and project.project_kind == 'HOUSE'


def get_house_scene():
    for scene in bpy.data.scenes:
        if scene.get(HOUSE_SCENE_KEY):
            return scene
    return None


def get_house_props():
    scene = get_house_scene()
    return scene.hb_house if scene else None


def is_room_view(scene):
    return scene is not None and bool(scene.get(ROOM_VIEW_KEY))


def house_scene_of(scene):
    """The house scene a scene belongs to: itself, or the house a room
    view was opened from. None outside a house."""
    if scene is None:
        return None
    if scene.get(HOUSE_SCENE_KEY):
        return scene
    if is_room_view(scene):
        return get_house_scene()
    return None


def active_level(context=None):
    """The level being drawn on, or None outside a house project. In the
    house scene that is the active level; in a room view it is the level
    of the room."""
    ctx = context or bpy.context
    scene = getattr(ctx, 'scene', None)
    house_scene = house_scene_of(scene)
    if house_scene is None:
        return None
    if not is_house_project(ctx):
        return None
    if is_room_view(scene):
        return get_level(scene.get(LEVEL_KEY, ''))
    house = house_scene.hb_house
    if not house.levels:
        return None
    index = min(max(house.active_level_index, 0), len(house.levels) - 1)
    return house.levels[index]


def get_level(uid):
    house = get_house_props()
    if house is None or not uid:
        return None
    for level in house.levels:
        if level.uid == uid:
            return level
    return None


def level_of(obj):
    """The level uid an object belongs to: its own tag, or the tag of the
    nearest tagged ancestor (a door's wall, a cabinet's wall). '' when
    nothing in the chain is tagged, which is every object in a rooms
    project."""
    while obj is not None:
        uid = obj.get(LEVEL_KEY)
        if uid:
            return uid
        obj = obj.parent
    return ''


def same_level(obj_a, obj_b):
    return level_of(obj_a) == level_of(obj_b)


def on_active_level(obj, context=None):
    """True when obj is on the level being drawn on. Always True outside a
    house project, so rooms-project behavior is unchanged."""
    level = active_level(context)
    if level is None:
        return True
    return level_of(obj) == level.uid


def level_above(house, level):
    """The lowest level whose elevation is over `level`'s, or None."""
    above = [l for l in house.levels if l.elevation > level.elevation + 1e-6]
    return min(above, key=lambda l: l.elevation) if above else None


def rise_to_level_above(level):
    """From this level's floor to the next level's floor - or one
    floor-to-floor height when nothing is above yet."""
    upper = level_above(level.id_data.hb_house, level)
    if upper is not None:
        return upper.elevation - level.elevation
    return level.floor_to_floor


def level_below(house, level):
    """The highest level whose elevation is under `level`'s, or None."""
    below = [l for l in house.levels if l.elevation < level.elevation - 1e-6]
    if not below:
        return None
    return max(below, key=lambda l: l.elevation)


# =============================================================================
# COLLECTIONS
# =============================================================================

def _house_root_collection(scene):
    root = None
    for col in scene.collection.children:
        if col.get('IS_HOUSE_ROOT'):
            root = col
            break
    if root is None:
        root = bpy.data.collections.new("House")
        root['IS_HOUSE_ROOT'] = True
        scene.collection.children.link(root)
    return root


def ensure_level_collections(scene, level):
    """Create the level's collection and its sub-collections if missing.
    A level's collections always hang off the house scene, whatever scene
    asks."""
    scene = house_scene_of(scene) or scene
    if level.collection is None:
        col = bpy.data.collections.new(level.name)
        col[LEVEL_KEY] = level.uid
        _house_root_collection(scene).children.link(col)
        level.collection = col
    col = level.collection
    for kind in LEVEL_SUBCOLLECTIONS:
        if level_subcollection(level, kind) is None:
            sub = bpy.data.collections.new(f"{level.name} - {kind}")
            sub['HB_LEVEL_PART'] = kind
            col.children.link(sub)
    return col


def level_subcollection(level, kind):
    if level.collection is None:
        return None
    for sub in level.collection.children:
        if sub.get('HB_LEVEL_PART') == kind:
            return sub
    return None


def move_to_collection(obj, col):
    """Make `col` the only collection holding obj."""
    if col is None:
        return
    for other in list(obj.users_collection):
        if other is not col:
            other.objects.unlink(obj)
    if obj.name not in col.objects:
        col.objects.link(obj)


def _rename_level_collections(level):
    col = level.collection
    if col is None:
        return
    col.name = level.name
    for sub in col.children:
        kind = sub.get('HB_LEVEL_PART')
        if kind:
            sub.name = f"{level.name} - {kind}"


# =============================================================================
# PUTTING OBJECTS ON LEVELS
# =============================================================================

def _is_constrained_to_wall(obj):
    """Walls in a drawn run follow the previous wall's end through a
    COPY_LOCATION constraint, so their Z comes from the run's first wall."""
    for con in obj.constraints:
        if con.type == 'COPY_LOCATION' and con.target is not None:
            return True
    return False


def apply_level_z(obj, level):
    if level is None or _is_constrained_to_wall(obj):
        return
    if abs(obj.location.z - level.elevation) > 1e-6:
        obj.location.z = level.elevation


def assign_wall_to_level(wall_obj, level, scene):
    """Tag a wall with the level, set its elevation and move it (and its
    length empty) into the level's Walls collection."""
    ensure_level_collections(scene, level)
    wall_obj[LEVEL_KEY] = level.uid
    apply_level_z(wall_obj, level)
    walls_col = level_subcollection(level, 'Walls')
    move_to_collection(wall_obj, walls_col)
    for child in wall_obj.children:
        if child.get('obj_x'):
            move_to_collection(child, walls_col)


# Objects a scene keeps for itself: never moved onto a level
LOCAL_OBJECT_KEY = 'HB_VIEW_LOCAL'


def _adoptable(obj):
    return obj.type != 'CAMERA' and not obj.get(LOCAL_OBJECT_KEY)


def active_level_of_scene(scene):
    """active_level for a scene that may not be the context's."""
    if is_room_view(scene):
        return get_level(scene.get(LEVEL_KEY, ''))
    if scene is not None and scene.get(HOUSE_SCENE_KEY) and scene.hb_house.levels:
        house = scene.hb_house
        return house.levels[min(max(house.active_level_index, 0), len(house.levels) - 1)]
    return None


def adopt_loose_objects(scene):
    """Move objects sitting in the scene's master collection onto their
    level, so they belong to the house: hiding a level hides them, and a
    cabinet placed in a room view appears in the house and in every other
    view of that level.

    Tools create objects in whatever scene is open, in its master
    collection; this is the one place that sorts them. An object's level
    is the level of the wall it hangs off (doors, cabinets on a wall),
    else the scene's own level (a room view's, or the house's active
    one) for a free-standing object like an island. Walls go to Walls,
    lights to Lights, the rest to Products. Returns how many moved."""
    house_scene = house_scene_of(scene)
    if house_scene is None:
        return 0
    default = active_level_of_scene(scene)
    moved = 0
    for obj in list(scene.collection.objects):
        if not _adoptable(obj):
            continue
        level = get_level(level_of(obj)) or default
        if level is None:
            continue
        ensure_level_collections(house_scene, level)
        if obj.get('IS_WALL_BP'):
            assign_wall_to_level(obj, level, house_scene)
        elif (obj.get('obj_x') and obj.parent is not None
                and obj.parent.get('IS_WALL_BP')):
            move_to_collection(obj, level_subcollection(level, 'Walls'))
        elif obj.type == 'LIGHT':
            move_to_collection(obj, level_subcollection(level, 'Lights'))
        else:
            move_to_collection(obj, level_subcollection(level, 'Products'))
        moved += 1
    return moved


def sort_level_children(scene):
    """The older name, kept for its callers."""
    return adopt_loose_objects(scene)


# Adoption runs after Blender reports a change, deferred to a timer so it
# never edits data inside the depsgraph handler, and held back while any
# tool is running modally - a placement tool still dragging a new cabinet
# around is left alone until it is placed.
_adopt_scheduled = False


def _modal_running():
    wm = bpy.context.window_manager
    if wm is None:
        return False
    for window in wm.windows:
        try:
            if len(window.modal_operators):
                return True
        except AttributeError:
            return False
    return False


def _adopt_timer():
    global _adopt_scheduled
    if _modal_running():
        return 0.5
    _adopt_scheduled = False
    scene = bpy.context.scene
    try:
        if house_scene_of(scene) is not None and is_house_project():
            adopt_loose_objects(scene)
    except Exception as ex:
        print('Home Builder: moving objects onto their level failed: %s' % ex)
    return None


@persistent
def _on_depsgraph_update(scene, depsgraph=None):
    global _adopt_scheduled
    if _adopt_scheduled:
        return
    current = bpy.context.scene
    if house_scene_of(current) is None:
        return
    if not any(_adoptable(o) for o in current.collection.objects):
        return
    _adopt_scheduled = True
    bpy.app.timers.register(_adopt_timer, first_interval=0.0)


def _find_layer_collection(layer_col, col):
    if layer_col.collection == col:
        return layer_col
    for child in layer_col.children:
        found = _find_layer_collection(child, col)
        if found is not None:
            return found
    return None


def apply_level_display(scene):
    """Show every level, or only the active one, per the house setting."""
    house = scene.hb_house
    if not house.levels:
        return
    active = house.levels[min(house.active_level_index, len(house.levels) - 1)]
    only_active = house.level_display == 'ACTIVE'
    for view_layer in scene.view_layers:
        for level in house.levels:
            if level.collection is None:
                continue
            layer_col = _find_layer_collection(view_layer.layer_collection,
                                               level.collection)
            if layer_col is None:
                continue
            hide = only_active and level != active
            if layer_col.hide_viewport != hide:
                layer_col.hide_viewport = hide
    _tag_view3d_redraw()


def _tag_view3d_redraw():
    wm = bpy.context.window_manager
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def walls_on_level(scene, level):
    return [obj for obj in scene.objects
            if obj.get('IS_WALL_BP') and obj.get(LEVEL_KEY) == level.uid]


# =============================================================================
# DRAWING ON A LEVEL
# =============================================================================

def constrain_hit_to_level(op, context):
    """Keep a placement tool's cursor on the active level's floor plane.

    Raycasts hit whatever is under the mouse, which in a house includes
    the levels below and above. A hit on anything that isn't on the
    active level is replaced by the view ray's intersection with the
    level's floor plane, so the tool neither snaps to nor sits on another
    level's geometry."""
    level = active_level(context)
    if level is None:
        return
    hit_obj = getattr(op, 'hit_object', None)
    if hit_obj is not None and level_of(hit_obj) == level.uid:
        return
    region = getattr(op, 'region', None)
    mouse = getattr(op, 'mouse_pos', None)
    if region is None or mouse is None or region.data is None:
        return
    rv3d = region.data
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse)
    co = intersect_line_plane(origin, origin + direction * 1.0e6,
                              Vector((0.0, 0.0, level.elevation)),
                              Vector((0.0, 0.0, 1.0)))
    if co is None:
        return
    op.hit_location = co
    op.hit_object = None
    op.hit_face_index = None


def exterior_wall_height(level):
    """Exterior walls on a level with a level above run up to that level's
    floor, through the floor between them, so the outside of the house is
    one wall. On the top level they stop at the ceiling."""
    if level_above(level.id_data.hb_house, level) is not None:
        return rise_to_level_above(level)
    return level.ceiling_height


def _wall_band(obj):
    """(start, direction, length, thickness) of a wall in plan, or None."""
    from . import hb_types
    wall = hb_types.GeoNodeWall(obj)
    if not wall.has_modifier():
        return None
    m = obj.matrix_world
    rot = m.to_euler().z
    d = Vector((math.cos(rot), math.sin(rot)))
    return (m.translation.xy.copy(), d, wall.get_input('Length'),
            wall.get_input('Thickness'))


def _carries(lower, upper_bands, min_overlap=0.05):
    """True when any wall above sits on this wall: in line with it, over
    its thickness, along some of its length."""
    start, d, length, t = lower
    n = Vector((-d.y, d.x))
    for u_start, u_d, u_len, u_t in upper_bands:
        if abs(d.x * u_d.y - d.y * u_d.x) > 1e-3:
            continue                        # not parallel
        # The upper wall's band across, against this wall's [0, t]
        w0 = (u_start - start).dot(n)
        w1 = w0 + u_t * (n.dot(Vector((-u_d.y, u_d.x))))
        if max(w0, w1) < 0.01 or min(w0, w1) > t - 0.01:
            continue                        # beside it, not on it
        a0 = (u_start - start).dot(d)
        a1 = a0 + u_len * u_d.dot(d)
        if min(max(a0, a1), length) - max(min(a0, a1), 0.0) > min_overlap:
            return True
    return False


def set_exterior_wall_heights(scene, level):
    """Give the level's exterior walls their heights: up to the next
    level's floor where a wall of that level stands on them, so the
    outside of the house is one wall; to the ceiling everywhere else -
    under a balcony, or where the level above is smaller - so nothing
    pokes up past the floor above."""
    from . import hb_types
    house = level.id_data.hb_house
    upper = level_above(house, level)
    upper_bands = []
    if upper is not None:
        for obj in scene.objects:
            if (obj.get('IS_WALL_BP') and obj.get(LEVEL_KEY) == upper.uid
                    and obj.get('WALL_TYPE') not in ('Divider', 'Porch', 'Dormer')):
                band = _wall_band(obj)
                if band is not None:
                    upper_bands.append(band)
    rise = rise_to_level_above(level) if upper is not None else None
    for obj in scene.objects:
        if not (obj.get('IS_WALL_BP') and obj.get(LEVEL_KEY) == level.uid
                and obj.get('WALL_TYPE', 'Exterior') == 'Exterior'):
            continue
        wall = hb_types.GeoNodeWall(obj)
        if not wall.has_modifier():
            continue
        band = _wall_band(obj)
        height = level.ceiling_height
        carried = rise is not None and band is not None and _carries(band, upper_bands)
        if carried:
            height = rise
        from . import hb_roofs
        height = hb_roofs.gable_wall_height(scene, obj, height, carried)
        if abs(wall.get_input('Height') - height) > 1e-6:
            wall.set_input('Height', height)
            obj.update_tag()


def copy_exterior_walls(scene, src, dst, only=None):
    """Copy the exterior walls of level `src` onto level `dst`, joined the
    way they were, so a new level starts from the outline below it - or
    from part of it: `only` names the walls to copy."""
    from . import hb_types
    originals = [o for o in scene.objects
                 if o.get('IS_WALL_BP') and o.get(LEVEL_KEY) == src.uid
                 and o.get('WALL_TYPE', 'Exterior') == 'Exterior'
                 and (only is None or o.name in only)]
    copies = {}
    for old in originals:
        o = hb_types.GeoNodeWall(old)
        if not o.has_modifier():
            continue
        new = hb_types.GeoNodeWall()
        new.create("Wall")
        for name in ('Length', 'Thickness'):
            new.set_input(name, o.get_input(name))
        new.set_input('Height', exterior_wall_height(dst))
        m = old.matrix_world
        new.obj.location = (m.translation.x, m.translation.y, dst.elevation)
        new.obj.rotation_euler.z = m.to_euler().z
        new.obj['WALL_TYPE'] = 'Exterior'
        copies[old] = new
    # Join the copies the way the originals are joined
    for old, new in copies.items():
        for con in old.constraints:
            if con.type == 'COPY_LOCATION' and con.target is not None:
                prev = con.target.parent
                if prev in copies:
                    new.connect_to_wall(copies[prev])
        o_x = hb_types.GeoNodeWall(old).obj_x
        linked = o_x.home_builder.connected_object if o_x else None
        if linked in copies and new.obj_x is not None:
            new.obj_x.home_builder.connected_object = copies[linked].obj
    for new in copies.values():
        assign_wall_to_level(new.obj, dst, scene)
    return len(copies)


def new_wall_height(level, wall_type, scene_props):
    """Height for a new wall on this level: interior walls take the
    level's ceiling height, exterior walls exterior_wall_height, the
    others keep their scene defaults."""
    if wall_type == 'Exterior':
        return exterior_wall_height(level)
    if wall_type == 'Interior':
        return level.ceiling_height
    if wall_type == 'Half':
        return scene_props.half_wall_height
    if wall_type == 'Railing':
        return scene_props.railing_height
    if wall_type in ('Divider', 'Porch'):
        from .operators import walls
        return walls.DIVIDER_HEIGHT
    return scene_props.fake_wall_height


# =============================================================================
# LEVEL-BELOW GHOST OVERLAY
# =============================================================================

_ghost_handle = None


def _wall_footprint(obj):
    """The wall's four plan corners in world XY (square ends - miters are
    not worth drawing in a ghost)."""
    from . import hb_types  # hb_types imports this module
    wall = hb_types.GeoNodeWall(obj)
    if not wall.has_modifier():
        return None
    try:
        length = wall.get_input('Length')
        thickness = wall.get_input('Thickness')
    except Exception:
        return None
    if not length:
        return None
    m = obj.matrix_world
    return [m @ Vector(p) for p in ((0, 0, 0), (length, 0, 0),
                                    (length, thickness, 0), (0, thickness, 0))]


def _draw_level_ghost():
    context = bpy.context
    scene = context.scene
    if scene is None or not scene.get(HOUSE_SCENE_KEY):
        return
    house = scene.hb_house
    if house.level_display != 'ACTIVE' or not house.show_level_below:
        return
    level = active_level(context)
    if level is None:
        return
    below = level_below(house, level)
    if below is None:
        return

    coords = []
    z = level.elevation
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP') or obj.get(LEVEL_KEY) != below.uid:
            continue
        corners = _wall_footprint(obj)
        if not corners:
            continue
        pts = [Vector((c.x, c.y, z)) for c in corners]
        for i in range(4):
            coords.append(pts[i])
            coords.append(pts[(i + 1) % 4])
    if not coords:
        return

    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    region = context.region
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", 1.5)
    shader.uniform_float("color", GHOST_COLOR)
    batch.draw(shader)
    gpu.state.blend_set('NONE')


# =============================================================================
# PROPERTIES
# =============================================================================

def _new_uid():
    return uuid.uuid4().hex[:8]


def _update_level_name(self, context):
    _rename_level_collections(self)


def _move_level_objects(level, dz):
    if level.collection is None or abs(dz) < 1e-9:
        return
    objs = set(level.collection.all_objects)
    for obj in objs:
        # Children ride along with their parent and run walls with the
        # run's first wall; only free objects are moved directly.
        if obj.parent is not None or _is_constrained_to_wall(obj):
            continue
        obj.location.z += dz


def _update_level_elevation(self, context):
    dz = self.elevation - self.applied_elevation
    if abs(dz) < 1e-9:
        return
    _move_level_objects(self, dz)
    self['applied_elevation'] = self.elevation
    # The level below's exterior walls reach this floor
    below = level_below(self.id_data.hb_house, self)
    if below is not None:
        set_exterior_wall_heights(self.id_data, below)


def _update_floor_to_floor(self, context):
    """Changing a level's floor-to-floor height moves every level above
    it by the same amount, so the stack stays closed."""
    dz = self.floor_to_floor - self.applied_floor_to_floor
    self['applied_floor_to_floor'] = self.floor_to_floor
    if abs(dz) < 1e-9:
        return
    house = self.id_data.hb_house
    for level in house.levels:
        if level.elevation > self.elevation + 1e-6:
            level.elevation = level.elevation + dz
    set_exterior_wall_heights(self.id_data, self)


def _update_ceiling_height(self, context):
    level = active_level(context)
    if level is not None and level.uid == self.uid:
        props = self.id_data.home_builder
        if abs(props.ceiling_height - self.ceiling_height) > 1e-9:
            props.ceiling_height = self.ceiling_height
    # The level's walls follow: full-height inside walls to the new
    # ceiling, outside walls to it - or on up to the level above, where
    # it stands on them - and the roofs that sit on them
    from . import hb_types, hb_roofs
    scene = self.id_data
    for obj in scene.objects:
        if (obj.get('IS_WALL_BP') and obj.get(LEVEL_KEY) == self.uid
                and obj.get('WALL_TYPE') == 'Interior'):
            wall = hb_types.GeoNodeWall(obj)
            if wall.has_modifier():
                wall.set_input('Height', self.ceiling_height)
                obj.update_tag()
    set_exterior_wall_heights(scene, self)
    hb_roofs.rebuild_roofs(scene)
    # Rooms without a height of their own follow the level's
    from . import hb_rooms
    hb_rooms.rebuild_level(scene, self)


def _room_label_changed(self, context):
    from . import hb_rooms
    hb_rooms.update_room_label(self)
    # Renamed a garage, or a bath: its floor follows, unless chosen by hand
    if self.floor_auto:
        apply_floor_default(self)


# ---- Room types --------------------------------------------------------------
# What a room is for. It picks the room's floor default (a bath gets tile,
# a garage concrete) and names a room that still has the name it was found
# with. Rooms without one fall back on the words in their name.

ROOM_TYPES = (
    ('NONE', "Unspecified", "No type: the floor follows the room's name"),
    ('BEDROOM', "Bedroom", ""), ('BATH', "Bath", ""), ('KITCHEN', "Kitchen", ""),
    ('LIVING', "Living", ""), ('DINING', "Dining", ""), ('FAMILY', "Family", ""),
    ('GREAT', "Great Room", ""), ('GARAGE', "Garage", ""), ('LAUNDRY', "Laundry", ""),
    ('CLOSET', "Closet", ""), ('PANTRY', "Pantry", ""), ('HALL', "Hall", ""),
    ('ENTRY', "Entry", ""), ('OFFICE', "Office", ""), ('MECHANICAL', "Mechanical", ""),
    ('STORAGE', "Storage", ""), ('PORCH', "Porch", ""), ('PATIO', "Patio", ""),
    ('DECK', "Deck", ""), ('BALCONY', "Balcony", ""),
)
TYPE_LABELS = {key: label for key, label, _d in ROOM_TYPES}
TYPE_KIND = {'BATH': 'wet', 'LAUNDRY': 'wet', 'GARAGE': 'garage',
             'PORCH': 'porch', 'PATIO': 'porch', 'DECK': 'outdoor', 'BALCONY': 'outdoor'}


def _given_name(name):
    """Whether a room's name is one it was given (Room 3, Bedroom 2) and
    not one typed for it, so a new type may rename it."""
    labels = "|".join(re.escape(label) for key, label, _d in ROOM_TYPES if key != 'NONE')
    return re.fullmatch(rf"(Room|Porch|Balcony|{labels})( \d+)?", name) is not None


def type_name(level, room, label):
    """The name a room of this type gets: the label, numbered from 2 when
    another room on the level already has it."""
    used = {r.name for r in level.rooms if r is not room and r.uid != room.uid}
    if label not in used:
        return label
    n = 2
    while f"{label} {n}" in used:
        n += 1
    return f"{label} {n}"


def _room_type_changed(self, context):
    from . import hb_rooms
    if _given_name(self.name):
        level = hb_rooms.level_of_room(self)
        if self.room_type == 'NONE':
            new = hb_rooms._next_room_name(level) if not self.name.startswith("Room") else self.name
        else:
            new = type_name(level, self, TYPE_LABELS[self.room_type])
        if new != self.name:
            self.name = new         # its update relabels and refloors
            return
    if self.floor_auto:
        apply_floor_default(self)


# ---- Floor defaults -------------------------------------------------------------
# A room's floor comes from the house's defaults for its kind, worked out
# from its name, until the user picks one for it by hand.

FLOOR_KINDS = ('room', 'wet', 'garage', 'porch', 'outdoor')
WET_WORDS = ('bath', 'powder', 'laundry', 'mud', 'shower', 'toilet', 'wc', 'lav', 'utility')
GARAGE_WORDS = ('garage', 'carport', 'workshop', 'shop')
PORCH_WORDS = ('porch', 'patio', 'stoop', 'lanai')
OUTDOOR_WORDS = ('deck', 'balcony')
_applying_floor_default = False


def floor_kind(room):
    """Which of the house's floor defaults a room takes, from its type -
    or, with none set, its name (and whether it is a porch or outdoors):
    'room', 'wet', 'garage', 'porch' or 'outdoor' (a deck or balcony)."""
    if room.is_porch:
        return 'porch'
    if room.outdoor:
        return 'outdoor'
    room_type = getattr(room, 'room_type', 'NONE')
    if room_type != 'NONE':
        return TYPE_KIND.get(room_type, 'room')
    name = room.name.lower()
    if any(w in name for w in PORCH_WORDS):
        return 'porch'
    if any(w in name for w in OUTDOOR_WORDS):
        return 'outdoor'
    if any(w in name for w in GARAGE_WORDS):
        return 'garage'
    if any(w in name for w in WET_WORDS):
        return 'wet'
    return 'room'


def floor_default(house, kind):
    """(finish, look) of the house's floor default for a kind of room."""
    from .operators import ops_room_dressing as dressing
    finish = getattr(house, f'floor_{kind}_finish')
    key = f'floor_{kind}_look'
    look = getattr(house, key) if key in house.keys() else dressing.DEFAULT_LOOK.get(finish)
    return finish, look


def apply_floor_default(room):
    """Give a room the house's floor for its kind; from now on it
    follows the defaults (until its floor is chosen by hand)."""
    global _applying_floor_default
    scene = room.id_data
    finish, look = floor_default(scene.hb_house, floor_kind(room))
    _applying_floor_default = True
    try:
        room['floor_auto'] = True
        if room.floor_finish != finish:
            room.floor_finish = finish
        if look and room.floor_look != look and look in [i[0] for i in _floor_look_items_cb(room, None)]:
            room.floor_look = look
    finally:
        _applying_floor_default = False


def apply_floor_defaults(scene, every_room=False):
    """Refloor the rooms that follow the defaults - or every room, which
    then all follow them."""
    for level in scene.hb_house.levels:
        for i in range(len(level.rooms)):
            room = level.rooms[i]
            if room.orphaned:
                continue
            if every_room or room.floor_auto:
                apply_floor_default(room)


def _floor_chosen(room):
    """A floor setting changed: by hand, the room keeps its own floor."""
    if not _applying_floor_default:
        room['floor_auto'] = False


def _room_floor_auto_changed(self, context):
    if self.floor_auto:
        apply_floor_default(self)


def _floor_defaults_changed(self, context):
    apply_floor_defaults(self.id_data)


def _floor_default_finish_changed(kind):
    def changed(self, context):
        key = f'floor_{kind}_look'
        if key in self.keys():
            del self[key]           # the new finish's own default look
        apply_floor_defaults(self.id_data)
    return changed


def _floor_default_looks(kind):
    def items(self, context):
        from .operators import ops_room_dressing as dressing
        finish = getattr(self, f'floor_{kind}_finish')
        looks = dressing.LOOKS.get(finish)
        if not looks:
            return [('NONE', "-", "")]
        if finish not in _floor_look_items:
            _floor_look_items[finish] = [(k, v[0], "") for k, v in looks.items()]
        return _floor_look_items[finish]
    return items


def _room_materials_changed(self, context):
    from . import hb_rooms
    hb_rooms.apply_room_materials(self)


def _room_custom_floor_picked(self, context):
    _floor_chosen(self)
    # Picking a material is choosing the Custom finish
    if self.floor_material is not None and self.floor_finish != 'CUSTOM':
        self['floor_finish'] = _FLOOR_FINISH_INDEX['CUSTOM']
    _room_materials_changed(self, context)


# The same finishes as the Floor tool (ops_room_dressing), per room, plus a
# Custom finish that takes any Blender material.
FLOOR_FINISH_ITEMS = [
    ('NONE', "None", "No finish: the floor keeps whatever material it has"),
    ('WOOD', "Wood Planks", "Staggered hardwood planks with grain"),
    ('TILE', "Tile", "Grid or running-bond tile with grout"),
    ('SOLID', "Solid Color", "Flat colored floor (concrete, paint)"),
    ('CUSTOM', "Custom Material", "Any Blender material"),
    ('DECK', "Deck", "Outdoor deck boards"),
    ('CARPET', "Carpet", "Wall-to-wall cut-pile carpet"),
]
_FLOOR_FINISH_INDEX = {item[0]: i for i, item in enumerate(FLOOR_FINISH_ITEMS)}
_floor_look_items = {}      # finish -> items; Blender needs the strings kept


def _floor_look_items_cb(self, context):
    from .operators import ops_room_dressing as dressing
    looks = dressing.LOOKS.get(self.floor_finish)
    if not looks:
        return [('NONE', "-", "")]
    if self.floor_finish not in _floor_look_items:
        _floor_look_items[self.floor_finish] = [(k, v[0], "") for k, v in looks.items()]
    return _floor_look_items[self.floor_finish]


def _apply_floor_look(room):
    """Copy the chosen look's colours onto the room, as the Floor tool's
    dialog does. Custom keeps the colours that are there."""
    from .operators import ops_room_dressing as dressing
    look = dressing.LOOKS.get(room.floor_finish, {}).get(room.floor_look)
    if not look or look[1] is None:
        return
    room['floor_color'] = look[1]
    if look[2] is not None:
        room['floor_accent'] = look[2]


def _room_floor_finish_changed(self, context):
    from .operators import ops_room_dressing as dressing
    from . import hb_rooms
    _floor_chosen(self)
    if self.floor_finish in dressing.LOOKS:
        # The Floor tool's defaults for the style, stored without their
        # update callbacks so the material is built once, below
        self['floor_size'] = dressing.DEFAULT_SIZE[self.floor_finish]
        self['floor_roughness'] = dressing.DEFAULT_ROUGHNESS[self.floor_finish]
        keys = [item[0] for item in _floor_look_items_cb(self, context)]
        self['floor_look'] = keys.index(dressing.DEFAULT_LOOK[self.floor_finish])
        _apply_floor_look(self)
    hb_rooms.apply_room_materials(self, rebuild_floor=True)


def _room_floor_look_changed(self, context):
    _floor_chosen(self)
    _apply_floor_look(self)
    _room_floor_style_changed(self, context)


def _room_floor_style_changed(self, context):
    from . import hb_rooms
    _floor_chosen(self)
    hb_rooms.apply_room_materials(self, rebuild_floor=True)


def _room_outdoor_changed(self, context):
    """An outdoor room has no ceiling and, unless it has a finish already,
    a deck floor; back indoors it gets its ceiling again."""
    self['has_ceiling'] = not self.outdoor
    if self.floor_auto:
        apply_floor_default(self)           # outdoors: the deck default
    elif self.outdoor and self.floor_finish == 'NONE':
        self.floor_finish = 'DECK'          # builds the deck material
    _room_shape_changed(self, context)      # ceiling off (or back on)


def _room_shape_changed(self, context):
    from . import hb_rooms
    hb_rooms.rebuild_room(self)


def _room_porch_changed(self, context):
    if self.is_porch:
        _room_shape_changed(self, context)


class HB_Room(PropertyGroup):
    """A room on a level. Which area of walls it is comes from where its
    marker sits (see hb_rooms); everything the user chooses for the room
    lives here, so it survives the walls being moved."""

    uid: StringProperty(name="Room ID")  # type: ignore

    name: StringProperty(name="Name", default="Room",
                         update=_room_label_changed)  # type: ignore

    room_type: EnumProperty(
        name="Room Type", items=ROOM_TYPES, default='NONE',
        description="What the room is for: it sets the room's floor default, "
                    "and names a room that still has the name it was found with",
        update=_room_type_changed)  # type: ignore

    marker: PointerProperty(type=bpy.types.Object)  # type: ignore
    floor_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    ceiling_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    label_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    view_scene: PointerProperty(type=bpy.types.Scene)  # type: ignore

    floor_finish: EnumProperty(
        name="Floor Finish", items=FLOOR_FINISH_ITEMS, default='NONE',
        update=_room_floor_finish_changed)  # type: ignore

    floor_look: EnumProperty(
        name="Look", items=_floor_look_items_cb,
        update=_room_floor_look_changed)  # type: ignore

    floor_color: FloatVectorProperty(
        name="Color", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.64, 0.45, 0.27), update=_room_floor_style_changed)  # type: ignore

    floor_accent: FloatVectorProperty(
        name="Accent", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.48, 0.32, 0.18),
        description="Darker plank tone for wood; grout color for tile",
        update=_room_floor_style_changed)  # type: ignore

    floor_size: FloatProperty(
        name="Size", default=0.127, min=0.02, max=2.0, subtype='DISTANCE',
        description="Plank width for wood; tile size for tile",
        update=_room_floor_style_changed)  # type: ignore

    floor_roughness: FloatProperty(
        name="Roughness", default=0.45, min=0.0, max=1.0, subtype='FACTOR',
        description="0 = glossy, 1 = matte",
        update=_room_floor_style_changed)  # type: ignore

    floor_running_bond: BoolProperty(
        name="Running Bond", default=False,
        description="Offset every other row of tile instead of a straight grid",
        update=_room_floor_style_changed)  # type: ignore

    floor_material: PointerProperty(
        name="Floor Material", type=bpy.types.Material,
        description="The material for the Custom floor finish",
        update=_room_custom_floor_picked)  # type: ignore

    ceiling_material: PointerProperty(
        name="Ceiling Material", type=bpy.types.Material,
        update=_room_materials_changed)  # type: ignore

    ceiling_height: FloatProperty(
        name="Ceiling Height",
        description="This room's ceiling height. 0 follows the level's",
        default=0.0, min=0.0, subtype='DISTANCE', precision=4,
        update=_room_shape_changed)  # type: ignore

    has_floor: BoolProperty(name="Floor", default=True,
                            update=_room_shape_changed)  # type: ignore

    has_ceiling: BoolProperty(name="Ceiling", default=True,
                              update=_room_shape_changed)  # type: ignore

    ceiling_style: EnumProperty(
        name="Ceiling Shape",
        items=[('FLAT', "Flat", "A flat ceiling at the room's ceiling height"),
               ('VAULTED', "Vaulted",
                "Follows the roof's underside up from the walls - a sloped or "
                "cathedral ceiling. Needs a roof on the level"),
               ('ATTIC', "Sloped Sides",
                "Flat at the ceiling height, coming down with the roof where it is lower - "
                "an attic or bonus room in the roof, its sides sloping to knee walls")],
        default='FLAT', update=_room_shape_changed)  # type: ignore
    vault_peak: FloatProperty(
        name="Peak Height",
        description=("Where a vaulted ceiling levels off, above the floor. "
                     "0 runs it all the way up under the roof"),
        default=0.0, min=0.0, subtype='DISTANCE', precision=4,
        update=_room_shape_changed)  # type: ignore

    outdoor: BoolProperty(
        name="Outdoor",
        description="A balcony or deck: no ceiling, deck boards for a floor",
        default=False, update=_room_outdoor_changed)  # type: ignore

    floor_auto: BoolProperty(
        name="Use House Default",
        description=("The floor comes from the house's Floor Defaults for this kind of "
                     "room (from its name). Choosing a floor by hand turns this off"),
        default=False, update=_room_floor_auto_changed)  # type: ignore

    # A porch: a room closed by porch edges (see hb_porches)
    is_porch: BoolProperty(
        name="Porch", description="Closed on its open sides by porch edges",
        default=False)  # type: ignore
    post_width: FloatProperty(
        name="Post Width", description="Width of the square porch posts",
        default=inch(6), min=inch(2), subtype='DISTANCE', precision=4,
        update=_room_porch_changed)  # type: ignore
    post_spacing: FloatProperty(
        name="Post Spacing",
        description="Most a porch edge goes between posts; they are spread evenly",
        default=inch(96), min=inch(24), subtype='DISTANCE', precision=4,
        update=_room_porch_changed)  # type: ignore
    beam_depth: FloatProperty(
        name="Beam Depth",
        description="Depth of the beam along the porch edges, under the ceiling. 0 for none",
        default=inch(10), min=0.0, subtype='DISTANCE', precision=4,
        update=_room_porch_changed)  # type: ignore
    floor_drop: FloatProperty(
        name="Step Down", description="How far the porch floor sits below the house floor",
        default=inch(4), min=0.0, subtype='DISTANCE', precision=4,
        update=_room_porch_changed)  # type: ignore
    post_material: PointerProperty(
        name="Post Material", type=bpy.types.Material,
        update=_room_porch_changed)  # type: ignore
    porch_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    porch_roof: EnumProperty(
        name="Porch Roof",
        # A porch isn't always covered - a patio or an open deck - so it
        # gets a roof of its own only when asked for
        items=[('AUTO', "Auto", "A shed roof unless the house's roof or a cross gable already covers the porch"),
               ('SHED', "Shed", "A shed roof from the porch's beam up to the house"),
               ('NONE', "None", "No roof of its own: open, or covered by the house's roof or a cross gable")],
        default='NONE', update=_room_porch_changed)  # type: ignore
    porch_roof_pitch: FloatProperty(
        name="Porch Roof Pitch", description="Rise in 12 of the porch's shed roof",
        default=3.0, min=0.5, max=12.0, precision=2,
        update=_room_porch_changed)  # type: ignore
    porch_roof_obj: PointerProperty(type=bpy.types.Object)  # type: ignore

    # Worked out by hb_rooms on each rebuild
    area: FloatProperty(name="Area", default=0.0)  # type: ignore
    orphaned: BoolProperty(
        name="No Area",
        description="The walls around this room's marker no longer close it in")  # type: ignore


def _roof_changed(self, context):
    from . import hb_roofs
    hb_roofs.rebuild_roof_of(self)


def _roof_piece_changed(self, context):
    """A roof piece's setting changed: rebuild the roof it belongs to."""
    from . import hb_roofs
    path = self.path_from_id()
    roof = self.id_data.path_resolve(path.rsplit('.pieces[', 1)[0])
    hb_roofs.rebuild_roof_of(roof)


class HB_RoofPiece(PropertyGroup):
    """A piece added to a level's roof (see hb_roofs): a cross gable - a
    gable roof of its own over a wing or a porch, running back into the
    main roof - or a shed dormer standing on the roof's slope. Its plan
    rectangle says where: the gable or the dormer's front faces out from
    the main ridge, on the rectangle's edge furthest from it."""

    name: StringProperty(name="Name", default="Roof Piece")  # type: ignore

    kind: EnumProperty(
        name="Kind",
        items=[('GABLE', "Cross Gable",
                "A gable roof of its own, its ridge square to the main ridge, "
                "running back into the main roof with valleys where they meet"),
               ('SHED', "Shed Dormer",
                "A dormer on the roof's slope: a front wall and a shallow "
                "roof sloping back up into the main roof"),
               ('DORMER', "Gable Dormer",
                "A dormer on the roof's slope with a gable roof of its own: a "
                "front wall for a window, and side walls down to the main roof")],
        default='GABLE', update=_roof_piece_changed)  # type: ignore

    x0: FloatProperty(name="Left Edge", subtype='DISTANCE', precision=4,
                      update=_roof_piece_changed)  # type: ignore
    x1: FloatProperty(name="Right Edge", subtype='DISTANCE', precision=4,
                      update=_roof_piece_changed)  # type: ignore
    y0: FloatProperty(name="Front Edge", subtype='DISTANCE', precision=4,
                      update=_roof_piece_changed)  # type: ignore
    y1: FloatProperty(name="Back Edge", subtype='DISTANCE', precision=4,
                      update=_roof_piece_changed)  # type: ignore

    eave_height: FloatProperty(
        name="Eave Height",
        description=("Above the level's floor: where a cross gable's slopes meet its "
                     "walls, or the top of a dormer's front wall"),
        default=inch(120), subtype='DISTANCE', precision=4,
        update=_roof_piece_changed)  # type: ignore

    pitch: FloatProperty(
        name="Pitch", description="Rise in 12",
        default=8.0, min=0.5, max=24.0, precision=2,
        update=_roof_piece_changed)  # type: ignore

    overhang: FloatProperty(
        name="Overhang", description="How far the piece's roof runs past its walls",
        default=inch(12), min=0.0, subtype='DISTANCE', precision=4,
        update=_roof_piece_changed)  # type: ignore

    # A dormer's front: a real wall, so windows go in it with the window
    # tool. Kept (not remade) across rebuilds so its windows stay.
    front_wall: PointerProperty(type=bpy.types.Object)  # type: ignore

    # Made by Fit Roof to Outline, which replaces its own pieces
    auto: BoolProperty(default=False)  # type: ignore


class HB_Roof(PropertyGroup):
    """A level's roof: built over the outside of its exterior walls,
    sitting on top of them or - for a barn or a cape - starting at the
    level's floor so the level is inside it. See hb_roofs."""

    enabled: BoolProperty(name="Roof", default=False,
                          update=_roof_changed)  # type: ignore

    style: EnumProperty(
        name="Style",
        items=[('GABLE', "Gable", "Two slopes meeting at a ridge, gable walls at the ends"),
               ('GAMBREL', "Barn (Gambrel)",
                "A steep lower slope and a shallow upper one on each side, like a barn"),
               ('HIP', "Hip",
                "Slopes on all four sides, meeting at a ridge - or a point on a square house")],
        default='GABLE', update=_roof_changed)  # type: ignore

    rise_through: BoolProperty(
        name="Upper Floor Rises Through",
        description=("The level above stands up through this roof - a smaller upper floor on "
                     "a wider one: the roof stops at its walls and doesn't cut them"),
        default=False, update=_roof_changed)  # type: ignore

    base: EnumProperty(
        name="Sits On",
        items=[('WALLS', "Top of Walls",
                "The roof sits on top of this level's walls"),
               ('FLOOR', "This Level's Floor",
                "The roof starts at this level's floor, so the level is inside it "
                "(a barn, or a cape with dormers)")],
        default='WALLS', update=_roof_changed)  # type: ignore

    eave_height: FloatProperty(
        name="Eave Height",
        description=("Where the underside of the roof meets the outside of the walls: "
                     "above the top of the walls, or above the floor when the roof "
                     "sits on the floor"),
        default=0.0, subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    pitch: FloatProperty(
        name="Pitch",
        description=("Rise in inches for every 12 inches across (12 is 45 degrees). "
                     "On a barn roof, the upper slope"),
        default=12.0, min=0.5, max=60.0, precision=2,
        update=_roof_changed)  # type: ignore

    lower_pitch: FloatProperty(
        name="Lower Pitch",
        description="A barn roof's steep lower slope: rise in 12 (36 is about 72 degrees)",
        default=36.0, min=1.0, max=120.0, precision=2,
        update=_roof_changed)  # type: ignore

    break_height: FloatProperty(
        name="Break Height",
        description=("Where a barn roof's steep slope turns to the shallow one, measured "
                     "like the eave height"),
        default=inch(108), min=0.0, subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    ridge: EnumProperty(
        name="Ridge",
        items=[('AUTO', "Long Way", "Along the longer side of the house"),
               ('X', "Along X", "Ridge runs along X; gables face X"),
               ('Y', "Along Y", "Ridge runs along Y; gables face Y")],
        default='AUTO', update=_roof_changed)  # type: ignore

    eave_overhang: FloatProperty(
        name="Eave Overhang", description="How far the roof runs past the side walls",
        default=inch(12), min=0.0, subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    gable_overhang: FloatProperty(
        name="Gable Overhang", description="How far the roof runs past the gable walls",
        default=inch(12), min=0.0, subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    thickness: FloatProperty(
        name="Roof Thickness", description="From the ceiling side to the shingles",
        default=inch(10), min=inch(1), subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    material: PointerProperty(name="Roof Material", type=bpy.types.Material,
                              update=_roof_changed)  # type: ignore

    # Off unless asked for: a bump-out is as often just the house's shape,
    # and a dormer can be drawn as a roof piece
    dormers: BoolProperty(
        name="Dormers",
        description="Build a dormer over each bump-out in the walls under the roof",
        default=False, update=_roof_changed)  # type: ignore

    dormer_pitch: FloatProperty(
        name="Dormer Pitch", description="Rise in 12 of the dormer roofs",
        default=12.0, min=1.0, max=24.0, precision=2,
        update=_roof_changed)  # type: ignore

    dormer_wall_height: FloatProperty(
        name="Dormer Wall Height",
        description="Height of the dormer side walls, from the floor to the dormer eave",
        default=inch(96), min=inch(24), subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    dormer_overhang: FloatProperty(
        name="Dormer Overhang", description="How far the dormer roofs run past their walls",
        default=inch(6), min=0.0, subtype='DISTANCE', precision=4,
        update=_roof_changed)  # type: ignore

    roof_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    cutter_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    # Dormer pieces: their roofs, and the hidden volumes the Booleans use
    dormer_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    dormer_tops_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    dormer_inside_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    roof_top_obj: PointerProperty(type=bpy.types.Object)  # type: ignore

    # The main roof over part of the house only - the core of an L- or
    # T-shaped house, its wings under cross gables (see Fit Roof to Outline)
    use_extents: BoolProperty(
        name="Custom Footprint",
        description="Build the main roof over a rectangle you set rather than the whole house",
        default=False, update=_roof_changed)  # type: ignore
    ext_x0: FloatProperty(name="Left", subtype='DISTANCE', precision=4,
                          update=_roof_changed)  # type: ignore
    ext_x1: FloatProperty(name="Right", subtype='DISTANCE', precision=4,
                          update=_roof_changed)  # type: ignore
    ext_y0: FloatProperty(name="Front", subtype='DISTANCE', precision=4,
                          update=_roof_changed)  # type: ignore
    ext_y1: FloatProperty(name="Back", subtype='DISTANCE', precision=4,
                          update=_roof_changed)  # type: ignore

    # Pieces added to the roof: cross gables and shed dormers
    pieces: CollectionProperty(type=HB_RoofPiece)  # type: ignore
    active_piece_index: IntProperty(name="Active Roof Piece")  # type: ignore
    gables_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    dormer_walls_obj: PointerProperty(type=bpy.types.Object)  # type: ignore
    rise_obj: PointerProperty(type=bpy.types.Object)  # type: ignore


# The finishes the outside walls can take (see hb_exterior). New ones go
# on the end: a saved choice is its place in the list.
SIDING_FINISHES = [
    ('NONE', "None", "Plain walls"),
    ('BOARD_BATTEN', "Board and Batten", "Vertical boards with battens every 16\""),
    ('LAP', "Lap", "Horizontal lap boards, 6\" to the weather"),
    ('SHINGLE', "Shingles", "Cedar shingles in rows, 7\" to the weather"),
    ('STUCCO', "Stucco", "A lightly textured plaster finish"),
    ('BRICK', "Brick", "Brick in running bond"),
    ('STONE', "Stone", "Rough stone"),
]


def _siding_override(same_as):
    return [('INHERIT', f"Same as {same_as}", f"The {same_as.lower()}'s siding")] + SIDING_FINISHES


def _level_siding_changed(self, context):
    _exterior_changed(self.id_data.hb_house)


def _wall_siding_changed(self, context):
    """A wall's own siding: the same goes on every selected outside wall,
    then the house is refinished."""
    obj = self.id_data
    style = [i[0] for i in _siding_override("Level")].index(self.style)
    for other in (context.selected_objects if context else ()):
        if (other is not obj and other.get('IS_WALL_BP')
                and other.get('WALL_TYPE', 'Exterior') == 'Exterior'):
            other.hb_siding['style'] = style
            other.hb_siding['color'] = tuple(self.color)
    scene = house_scene_of(context.scene if context else bpy.context.scene)
    if scene is not None:
        _exterior_changed(scene.hb_house)


class HB_WallSiding(PropertyGroup):
    """An outside wall's own siding, over its level's and the house's."""
    style: EnumProperty(
        name="Siding", items=_siding_override("Level"), default='INHERIT',
        update=_wall_siding_changed)  # type: ignore
    color: FloatVectorProperty(
        name="Siding Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.92, 0.92, 0.90), update=_wall_siding_changed)  # type: ignore


class HB_Level(PropertyGroup):
    uid: StringProperty(name="Level ID")  # type: ignore

    # This level's outside walls' siding, over the house's
    siding_style: EnumProperty(
        name="Siding", items=_siding_override("House"), default='INHERIT',
        update=_level_siding_changed)  # type: ignore
    siding_color: FloatVectorProperty(
        name="Siding Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.92, 0.92, 0.90), update=_level_siding_changed)  # type: ignore

    name: StringProperty(name="Name", default="Level",
                         update=_update_level_name)  # type: ignore

    elevation: FloatProperty(
        name="Elevation",
        description="Height of this level's floor above Level 1's floor",
        subtype='DISTANCE', precision=4,
        update=_update_level_elevation)  # type: ignore

    # The elevation the level's objects currently sit at, so a change can
    # move them by the difference.
    applied_elevation: FloatProperty(subtype='DISTANCE')  # type: ignore

    floor_to_floor: FloatProperty(
        name="Floor to Floor",
        description="From this level's floor to the next level's floor",
        default=inch(108), min=0.0, subtype='DISTANCE', precision=4,
        update=_update_floor_to_floor)  # type: ignore

    applied_floor_to_floor: FloatProperty(
        default=inch(108), subtype='DISTANCE')  # type: ignore

    floor_thickness: FloatProperty(
        name="Floor Thickness",
        description="Floor structure between this level's ceiling and the next level's floor",
        default=inch(12), min=0.0, subtype='DISTANCE', precision=4)  # type: ignore

    ceiling_height: FloatProperty(
        name="Ceiling Height",
        description="Height of full-height walls drawn on this level",
        default=inch(96), min=0.0, subtype='DISTANCE', precision=4,
        update=_update_ceiling_height)  # type: ignore

    collection: PointerProperty(type=bpy.types.Collection)  # type: ignore

    rooms: CollectionProperty(type=HB_Room)  # type: ignore

    roof: PointerProperty(type=HB_Roof)  # type: ignore

    active_room_index: IntProperty(name="Active Room")  # type: ignore


def _update_active_level(self, context):
    scene = self.id_data
    if not self.levels:
        return
    level = self.levels[min(self.active_level_index, len(self.levels) - 1)]
    props = scene.home_builder
    if abs(props.ceiling_height - level.ceiling_height) > 1e-9:
        props.ceiling_height = level.ceiling_height
    apply_level_display(scene)


def _roofs_shown_changed(house):
    from . import hb_roofs
    hb_roofs.apply_roof_visibility(house.id_data)
    _tag_view3d_redraw()


def _labels_shown_changed(house):
    from . import hb_rooms
    hb_rooms.apply_label_visibility(house.id_data)
    _tag_view3d_redraw()


def _framing_shown_changed(house):
    from . import hb_framing
    scene = house.id_data
    if house.show_framing:
        hb_framing.build(scene)
    else:
        hb_framing.clear(scene)
    _tag_view3d_redraw()


def _framing_changed(house):
    from . import hb_framing
    hb_framing.refresh(house.id_data)
    _tag_view3d_redraw()


def _ceilings_shown_changed(house):
    from . import hb_rooms
    hb_rooms.apply_ceiling_visibility(house.id_data)
    _tag_view3d_redraw()


def _update_level_display(self, context):
    scene = self.id_data
    sort_level_children(scene)
    apply_level_display(scene)


def _exterior_changed(house):
    from . import hb_exterior
    hb_exterior.apply_exterior_finish(house.id_data)


class HB_House_Props(PropertyGroup):
    levels: CollectionProperty(type=HB_Level)  # type: ignore

    tools_stay_on: BoolProperty(
        name="Tools Stay On",
        description="Keep a placement tool running after each wall, door, "
                    "window or obstacle is placed, until Esc or right-click",
        default=True)  # type: ignore

    active_level_index: IntProperty(
        name="Active Level", update=_update_active_level)  # type: ignore

    # Which plan view the switches below match, and a way to set them all
    # at once (see hb_plan_views): read from the switches, never stored.
    plan_view: EnumProperty(
        name="View",
        description="Show the house for what you are doing: each view sets the "
                    "levels, roofs, labels, shading and camera at once",
        items=hb_plan_views.ITEMS,
        get=hb_plan_views.get_plan_view,
        set=hb_plan_views.set_plan_view)  # type: ignore

    level_display: EnumProperty(
        name="Show",
        items=[('ALL', "All Levels", "Show every level"),
               ('ACTIVE', "Active Level", "Show only the level being drawn on")],
        default='ALL',
        update=_update_level_display)  # type: ignore

    show_level_below: BoolProperty(
        name="Ghost Level Below",
        description="Outline the walls of the level below while only the active level is shown",
        default=True,
        update=lambda self, context: _tag_view3d_redraw())  # type: ignore

    # Ceilings are in the way while designing (doors, openings, looking
    # into a room), so they start hidden; they still render.
    # Exterior finish (see hb_exterior)
    siding_style: EnumProperty(
        name="Siding", items=SIDING_FINISHES,
        default='NONE', update=lambda self, context: _exterior_changed(self))  # type: ignore
    siding_color: FloatVectorProperty(
        name="Siding Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.92, 0.92, 0.90),
        update=lambda self, context: _exterior_changed(self))  # type: ignore
    # The gable ends (and the walls the roof pieces make), over the walls'
    gable_siding_style: EnumProperty(
        name="Gable Siding", items=_siding_override("Walls"), default='INHERIT',
        update=lambda self, context: _exterior_changed(self))  # type: ignore
    gable_siding_color: FloatVectorProperty(
        name="Gable Siding Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.92, 0.92, 0.90),
        update=lambda self, context: _exterior_changed(self))  # type: ignore
    siding_geometry: BoolProperty(
        name="Real Geometry",
        description=("Build the battens, lap boards and shingle rows as real geometry "
                     "on the walls, not only in the material. Slower to update"),
        default=False, update=lambda self, context: _exterior_changed(self))  # type: ignore

    base_style: EnumProperty(
        name="Base",
        items=[('NONE', "None", "No masonry base"),
               ('BRICK', "Brick", "A brick base along the bottom of the outside walls"),
               ('STONE', "Stone", "A stone base along the bottom of the outside walls")],
        default='NONE', update=lambda self, context: _exterior_changed(self))  # type: ignore
    base_color: FloatVectorProperty(
        name="Base Color", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.47, 0.22, 0.16),
        update=lambda self, context: _exterior_changed(self))  # type: ignore
    base_height: FloatProperty(
        name="Base Height", description="How high the masonry base comes up the walls",
        default=inch(30), min=0.0, subtype='DISTANCE', precision=4,
        update=lambda self, context: _exterior_changed(self))  # type: ignore

    show_roofs: BoolProperty(
        name="Show Roofs",
        description="Show the roofs in the viewport. Off to see down into the house",
        default=True,
        update=lambda self, context: _roofs_shown_changed(self))  # type: ignore

    # Floor defaults: what a room's floor is until one is chosen for it
    floor_room_finish: EnumProperty(
        name="Rooms", items=[i for i in FLOOR_FINISH_ITEMS if i[0] != 'CUSTOM'], default='WOOD',
        update=_floor_default_finish_changed('room'))  # type: ignore
    floor_room_look: EnumProperty(
        name="Look", items=_floor_default_looks('room'), update=_floor_defaults_changed)  # type: ignore
    floor_wet_finish: EnumProperty(
        name="Baths & Laundry", items=[i for i in FLOOR_FINISH_ITEMS if i[0] != 'CUSTOM'],
        default='TILE', update=_floor_default_finish_changed('wet'))  # type: ignore
    floor_wet_look: EnumProperty(
        name="Look", items=_floor_default_looks('wet'), update=_floor_defaults_changed)  # type: ignore
    floor_garage_finish: EnumProperty(
        name="Garages", items=[i for i in FLOOR_FINISH_ITEMS if i[0] != 'CUSTOM'],
        default='SOLID', update=_floor_default_finish_changed('garage'))  # type: ignore
    floor_garage_look: EnumProperty(
        name="Look", items=_floor_default_looks('garage'), update=_floor_defaults_changed)  # type: ignore
    floor_porch_finish: EnumProperty(
        name="Porches & Patios", items=[i for i in FLOOR_FINISH_ITEMS if i[0] != 'CUSTOM'],
        default='SOLID', update=_floor_default_finish_changed('porch'))  # type: ignore
    floor_porch_look: EnumProperty(
        name="Look", items=_floor_default_looks('porch'), update=_floor_defaults_changed)  # type: ignore
    floor_outdoor_finish: EnumProperty(
        name="Decks & Balconies", items=[i for i in FLOOR_FINISH_ITEMS if i[0] != 'CUSTOM'],
        default='DECK', update=_floor_default_finish_changed('outdoor'))  # type: ignore
    floor_outdoor_look: EnumProperty(
        name="Look", items=_floor_default_looks('outdoor'), update=_floor_defaults_changed)  # type: ignore

    show_room_labels: BoolProperty(
        name="Show Room Labels",
        description="Show each room's name and area on its floor. Walk Through hides them while it runs",
        default=True,
        update=lambda self, context: _labels_shown_changed(self))  # type: ignore

    show_ceilings: BoolProperty(
        name="Show Ceilings",
        description="Show the rooms' ceilings in the viewport. They render either way",
        default=False,
        update=lambda self, context: _ceilings_shown_changed(self))  # type: ignore

    # Framing (see hb_framing): built only while it shows
    show_framing: BoolProperty(
        name="Show Framing",
        description="Build the studs, joists and rafters inside the walls, floors, "
                    "ceilings and roofs, and show the solids as outlines",
        default=False,
        update=lambda self, context: _framing_shown_changed(self))  # type: ignore

    framing_spacing: EnumProperty(
        name="Spacing",
        items=[('16', "16\" on Centre", "Studs and joists 16\" apart"),
               ('24', "24\" on Centre", "Studs and joists 24\" apart")],
        default='16',
        update=lambda self, context: _framing_changed(self))  # type: ignore

    ground_floor: EnumProperty(
        name="Ground Floor",
        items=[('SLAB', "Slab", "The ground level sits on a concrete slab: no floor framing"),
               ('CRAWL', "Crawlspace", "The ground level is framed with joists over a crawlspace")],
        default='SLAB',
        update=lambda self, context: _framing_changed(self))  # type: ignore

    framing_walls: BoolProperty(
        name="Walls", default=True,
        update=lambda self, context: _framing_changed(self))  # type: ignore
    framing_floors: BoolProperty(
        name="Floors", default=True,
        update=lambda self, context: _framing_changed(self))  # type: ignore
    framing_ceilings: BoolProperty(
        name="Ceilings", default=True,
        update=lambda self, context: _framing_changed(self))  # type: ignore
    framing_roofs: BoolProperty(
        name="Roofs", default=True,
        update=lambda self, context: _framing_changed(self))  # type: ignore

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_house = PointerProperty(
            name="Home Builder House", type=cls)

    @classmethod
    def unregister(cls):
        if hasattr(bpy.types.Scene, 'hb_house'):
            del bpy.types.Scene.hb_house


def add_level(scene, name=None):
    """Append a level on top of the stack, sized like the one below it."""
    house = scene.hb_house
    # Read what's needed from the top level before adding: adding to a
    # collection can move its items, and a reference held across the add
    # can point at freed memory
    top = max(house.levels, key=lambda l: l.elevation) if house.levels else None
    if top is not None:
        top_vals = (top.elevation, top.floor_to_floor, top.floor_thickness,
                    top.ceiling_height)
    top = None
    level = house.levels.add()
    level.uid = _new_uid()
    level['name'] = name or f"Level {len(house.levels)}"
    if house.levels and len(house.levels) > 1:
        t_elev, t_ftf, t_thick, t_ceil = top_vals
        elevation = t_elev + t_ftf
        level['floor_to_floor'] = t_ftf
        level['applied_floor_to_floor'] = t_ftf
        level['floor_thickness'] = t_thick
        level['ceiling_height'] = t_ceil
    else:
        elevation = 0.0
        level['ceiling_height'] = scene.home_builder.ceiling_height
        level['floor_to_floor'] = level.ceiling_height + level.floor_thickness
        level['applied_floor_to_floor'] = level.floor_to_floor
    level['elevation'] = elevation
    level['applied_elevation'] = elevation
    ensure_level_collections(scene, level)
    return level


# =============================================================================
# IMPORTING A ROOM AS A LEVEL
# =============================================================================
# A house drawn the older way - each floor its own room scene, put
# together with linked rooms - becomes levels of the house: the room's
# walls, doors and everything on them move into a new level, placed
# where its link put it, so the floors keep lining up exactly.

def importable_room_scenes(house_scene):
    """Room scenes that could become a level of this house."""
    out = []
    for scene in bpy.data.scenes:
        if scene == house_scene or scene.get(HOUSE_SCENE_KEY) or is_room_view(scene):
            continue
        if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW') or scene.get('IS_CROWN_DETAIL'):
            continue
        if any(o.get('IS_WALL_BP') for o in scene.objects):
            out.append(scene)
    return out


def link_offset(house_scene, source_scene):
    """Where the source room sits relative to the house, from the linked
    rooms that put them together: the source's link transform in the
    space of the house's link in the same scene (or the house itself
    when the house isn't linked there). None when nothing links it."""
    for scene in bpy.data.scenes:
        links = [o for o in scene.objects if o.get('IS_LINKED_ROOM')]
        src = [o for o in links if o.get('LINKED_ROOM_SOURCE') == source_scene.name]
        if not src:
            continue
        house = [o for o in links if o.get('LINKED_ROOM_SOURCE') == house_scene.name]
        base = house[0].matrix_world if house else Matrix.Identity(4)
        return base.inverted() @ src[0].matrix_world
    return None


def _source_collections(scene):
    return [scene.collection] + list(scene.collection.children_recursive)


def import_room_as_level(house_scene, source_scene):
    """Move a room scene's objects into a new level of the house. Returns
    (level uid, walls moved). The source scene is left empty."""
    from .operators import walls
    house = house_scene.hb_house
    offset = link_offset(house_scene, source_scene)

    # The level stack, read before adding (never hold a level across add)
    top = max(house.levels, key=lambda l: l.elevation) if house.levels else None
    top_uid = top.uid if top is not None else ''
    top_elev = top.elevation if top is not None else 0.0
    top_ftf = top.floor_to_floor if top is not None else 0.0
    top = None
    if offset is None:
        offset = Matrix.Translation((0.0, 0.0, top_elev + top_ftf if top_uid else 0.0))
    elevation = offset.translation.z

    # The level below reaches up to the new one
    below = get_level(top_uid)
    if below is not None and elevation > below.elevation + 1e-6:
        below['floor_to_floor'] = elevation - below.elevation
        below['applied_floor_to_floor'] = below.floor_to_floor
    below = None

    level = house.levels.add()
    uid = _new_uid()
    level.uid = uid
    level['name'] = source_scene.name
    level['ceiling_height'] = source_scene.home_builder.ceiling_height
    level['floor_to_floor'] = level.ceiling_height + level.floor_thickness
    level['applied_floor_to_floor'] = level.floor_to_floor
    level['elevation'] = elevation
    level['applied_elevation'] = elevation
    ensure_level_collections(house_scene, level)
    level = None

    # Move the room into place. Roots move whole; a wall held to another
    # wall's end by a constraint only turns - the constraint brings it.
    turn = offset.to_euler().z
    objects = list(source_scene.objects)
    for obj in objects:
        if obj.parent is not None:
            continue
        if _is_constrained_to_wall(obj):
            obj.rotation_euler.z += turn
        else:
            # The object's own transform: a scene that hasn't been looked
            # at this session has stale world matrices
            obj.matrix_basis = offset @ obj.matrix_basis

    # Out of the room's collections, into the house; adoption sorts each
    # onto the new level (walls to Walls, lights to Lights, the rest to
    # Products)
    source_cols = _source_collections(source_scene)
    for obj in objects:
        if obj.type == 'CAMERA':
            continue
        for col in list(obj.users_collection):
            if col in source_cols:
                col.objects.unlink(obj)
        if obj.name not in house_scene.collection.objects:
            house_scene.collection.objects.link(obj)
    index = next(i for i, l in enumerate(house.levels) if l.uid == uid)
    house.active_level_index = index
    for obj in objects:
        if obj.get('IS_WALL_BP'):
            obj[LEVEL_KEY] = uid
    adopt_loose_objects(house_scene)
    source_scene['HB_IMPORTED_TO_LEVEL'] = uid

    walls.refresh_wall_junctions(house_scene, uid)
    return uid, sum(1 for o in objects if o.get('IS_WALL_BP'))


# =============================================================================
# OPERATORS
# =============================================================================

class HOME_BUILDER_OT_start_house_project(bpy.types.Operator):
    bl_idname = "home_builder.start_house_project"
    bl_label = "Start House Project"
    bl_description = ("Make this scene the house: draw the whole floor plan here, "
                      "on levels stacked by elevation. Walls already in the scene "
                      "become Level 1")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene is None or scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
            return False
        return not is_house_project(context)

    def execute(self, context):
        scene = context.scene
        project = hb_project.get_project_props(context)
        project.project_kind = 'HOUSE'
        scene[HOUSE_SCENE_KEY] = True
        scene['IS_ROOM_SCENE'] = True

        house = scene.hb_house
        if not house.levels:
            level = add_level(scene, "Level 1")
            house.active_level_index = 0
        else:
            level = house.levels[0]

        moved = 0
        for obj in list(scene.objects):
            if obj.get('IS_WALL_BP') and not obj.get(LEVEL_KEY):
                assign_wall_to_level(obj, level, scene)
                moved += 1
        sort_level_children(scene)
        apply_level_display(scene)
        if moved:
            from . import hb_rooms
            hb_rooms.rebuild_level(scene, level)

        msg = f"Started house project with {level.name}"
        if moved:
            msg += f" ({moved} existing wall(s))"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class HOME_BUILDER_OT_add_level(bpy.types.Operator):
    bl_idname = "home_builder.add_level"
    bl_label = "Add Level"
    bl_description = "Add a level on top of the house"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.scene.get(HOUSE_SCENE_KEY)

    start: EnumProperty(
        name="Start With",
        items=[('FULL', "Full Floor", "The whole outline of the level below, copied up"),
               ('SELECTED', "Over Selected Walls",
                "Only the selected outside walls of the level below, copied up: a "
                "partial floor, like a bonus room over a garage"),
               ('EMPTY', "Empty Level",
                "No walls: draw the level over the outline of the level below")],
        # Not remembered from the last time, or + NEW would stop asking
        default='FULL', options={'SKIP_SAVE'})  # type: ignore

    # Kept for scripts from before Start With: off is an empty level
    copy_exterior: BoolProperty(
        name="Copy Exterior Walls",
        description="Start the new level with the exterior walls of the level below",
        default=True, options={'SKIP_SAVE'})  # type: ignore

    @staticmethod
    def _top(house):
        return max(house.levels, key=lambda l: l.elevation) if house.levels else None

    @staticmethod
    def _selected_walls(context, level):
        return [o.name for o in context.selected_objects
                if level is not None and o.get('IS_WALL_BP') and o.get(LEVEL_KEY) == level.uid
                and o.get('WALL_TYPE', 'Exterior') == 'Exterior']

    def invoke(self, context, event):
        """From the + NEW button: ask how the new level starts."""
        if self.properties.is_property_set('start') or not context.scene.hb_house.levels:
            return self.execute(context)
        top = self._top(context.scene.hb_house)
        picked = len(self._selected_walls(context, top))

        def draw(menu, _context):
            layout = menu.layout
            layout.operator_context = 'EXEC_DEFAULT'
            layout.operator(self.bl_idname, text="Full Floor", icon='MOD_BUILD').start = 'FULL'
            row = layout.row()
            row.enabled = picked > 0
            label = (f"Over Selected Walls ({picked})" if picked
                     else "Over Selected Walls (select outside walls first)")
            row.operator(self.bl_idname, text=label, icon='RESTRICT_SELECT_OFF').start = 'SELECTED'
            layout.operator(self.bl_idname, text="Empty Level", icon='SELECT_SET').start = 'EMPTY'
        context.window_manager.popup_menu(draw, title=f"New Level on {top.name}" if top else "New Level")
        return {'CANCELLED'}

    def execute(self, context):
        scene = context.scene
        house = scene.hb_house
        top = self._top(house)
        start = self.start if self.copy_exterior else 'EMPTY'
        only = self._selected_walls(context, top) if start == 'SELECTED' else None
        if start == 'SELECTED' and not only:
            self.report({'WARNING'}, "Select the outside walls the new level stands on")
            return {'CANCELLED'}
        below_uid = top.uid if top is not None else ''
        level = add_level(scene)
        uid = level.uid
        level = None                # held across nothing below, by uid
        house.active_level_index = len(house.levels) - 1
        below = get_level(below_uid)
        new = get_level(uid)
        copied = 0
        if below is not None:
            # The level below's exterior walls now run up to the new floor
            if start != 'EMPTY':
                copied = copy_exterior_walls(scene, below, new, only=only)
            # The level below's exterior walls run up to the new floor
            # where the new level's walls stand on them
            set_exterior_wall_heights(scene, below)
        if copied:
            from .operators import walls
            walls.refresh_wall_junctions(scene, uid)
        if self.start == 'EMPTY' and below is not None:
            # Chosen from the menu: draw it over the outline of the level below
            house.level_display = 'ACTIVE'
            house.show_level_below = True
        msg = f"Added {new.name}"
        if copied:
            msg += f" with {copied} exterior wall(s) from {below.name}"
        elif start == 'EMPTY':
            msg += ": draw its walls over the outline of the level below"
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_level(bpy.types.Operator):
    bl_idname = "home_builder.remove_level"
    bl_label = "Remove Level"
    bl_description = ("Remove the active level and everything on it - its walls, rooms, "
                      "roof and what is placed on them. Ctrl+Z brings it back")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (scene is not None and scene.get(HOUSE_SCENE_KEY)
                and len(scene.hb_house.levels) > 1)

    def execute(self, context):
        scene = context.scene
        house = scene.hb_house
        index = house.active_level_index
        level = house.levels[index]
        col = level.collection
        name, uid = level.name, level.uid
        walls = sum(1 for o in scene.objects
                    if o.get('IS_WALL_BP') and o.get(LEVEL_KEY) == uid)
        # Its roof and the roof's helpers live outside the level's collection
        from . import hb_roofs
        for piece in level.roof.pieces:
            if piece.front_wall is not None:
                hb_roofs._delete_tree(piece.front_wall)
                piece.front_wall = None
        hb_roofs._remove_roof(level.roof)
        doomed = {o.name for o in scene.objects if o.get(LEVEL_KEY) == uid}
        if col is not None:
            doomed |= {o.name for o in col.all_objects}
        for obj_name in doomed:
            obj = bpy.data.objects.get(obj_name)
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
        level = house.levels[index]
        if col is not None:
            for sub in list(col.children):
                bpy.data.collections.remove(sub)
            bpy.data.collections.remove(col)
        house.levels.remove(index)
        house.active_level_index = max(0, min(index, len(house.levels) - 1))
        # A level that lost the one above stops its exterior walls at
        # its ceiling again
        for level in house.levels:
            set_exterior_wall_heights(scene, level)
        # The roofs below lose what stood on them: their gables and trims follow
        hb_roofs.rebuild_roofs(scene)
        what = f" and its {walls} wall(s)" if walls else ""
        self.report({'INFO'}, f"Removed {name}{what} (Ctrl+Z to bring it back)")
        return {'FINISHED'}


class HOME_BUILDER_OT_import_room_as_level(bpy.types.Operator):
    bl_idname = "home_builder.import_room_as_level"
    bl_label = "Import Room as Level"
    bl_description = ("Make a room scene a level of this house: its walls, doors "
                      "and everything on them move into a new level, placed where "
                      "its linked room puts it")
    bl_options = {'UNDO'}

    scene_name: StringProperty(name="Room")  # type: ignore

    @classmethod
    def poll(cls, context):
        return (context.scene is not None and context.scene.get(HOUSE_SCENE_KEY)
                and is_house_project(context))

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(
            self, event,
            title=f"Import '{self.scene_name}' as a level?",
            message=("Its walls and everything on them move into this house. "
                     f"The '{self.scene_name}' scene is left empty."),
            confirm_text="Import")

    def execute(self, context):
        source = bpy.data.scenes.get(self.scene_name)
        if source is None or source not in importable_room_scenes(context.scene):
            self.report({'WARNING'}, f"'{self.scene_name}' can't be imported")
            return {'CANCELLED'}
        uid, count = import_room_as_level(context.scene, source)
        level = get_level(uid)
        self.report({'INFO'}, f"'{source.name}' is now {level.name} ({count} walls). "
                              f"The empty '{source.name}' scene can be deleted")
        return {'FINISHED'}


class HOME_BUILDER_OT_apply_floor_defaults(bpy.types.Operator):
    bl_idname = "home_builder.apply_floor_defaults"
    bl_label = "Apply Floor Defaults"
    bl_description = ("Give every room the house's default floor for its kind - wood, tile "
                      "in baths, concrete in garages - including rooms floored by hand")
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = house_scene_of(context.scene)
        if scene is None:
            return {'CANCELLED'}
        apply_floor_defaults(scene, every_room=True)
        return {'FINISHED'}


class HOME_BUILDER_OT_set_active_level(bpy.types.Operator):
    bl_idname = "home_builder.set_active_level"
    bl_label = "Set Active Level"
    bl_description = "Draw on this level"
    bl_options = {'UNDO'}

    index: IntProperty()  # type: ignore

    def execute(self, context):
        house = context.scene.hb_house
        if 0 <= self.index < len(house.levels):
            house.active_level_index = self.index
        return {'FINISHED'}


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    HB_WallSiding,
    HB_Room,
    HB_RoofPiece,
    HB_Roof,
    HB_Level,
    HB_House_Props,
    HOME_BUILDER_OT_start_house_project,
    HOME_BUILDER_OT_add_level,
    HOME_BUILDER_OT_remove_level,
    HOME_BUILDER_OT_set_active_level,
    HOME_BUILDER_OT_apply_floor_defaults,
    HOME_BUILDER_OT_import_room_as_level,
)


def register():
    global _ghost_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    HB_House_Props.register()
    bpy.types.Object.hb_siding = PointerProperty(type=HB_WallSiding)
    _ghost_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_level_ghost, (), 'WINDOW', 'POST_VIEW')
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)


def unregister():
    global _ghost_handle
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    if bpy.app.timers.is_registered(_adopt_timer):
        bpy.app.timers.unregister(_adopt_timer)
    if _ghost_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_ghost_handle, 'WINDOW')
        _ghost_handle = None
    HB_House_Props.unregister()
    if hasattr(bpy.types.Object, 'hb_siding'):
        del bpy.types.Object.hb_siding
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
