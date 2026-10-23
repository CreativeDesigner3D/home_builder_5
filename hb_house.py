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

import uuid

import bpy
import gpu
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import PropertyGroup
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.geometry import intersect_line_plane
from bpy_extras import view3d_utils

from . import hb_project
from .units import inch

LEVEL_KEY = 'HB_LEVEL'
HOUSE_SCENE_KEY = 'IS_HOUSE_SCENE'

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


def active_level(context=None):
    """The level being drawn on, or None outside a house project or when
    the current scene is not the house scene."""
    ctx = context or bpy.context
    scene = getattr(ctx, 'scene', None)
    if scene is None or not scene.get(HOUSE_SCENE_KEY):
        return None
    if not is_house_project(ctx):
        return None
    house = scene.hb_house
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
    """Create the level's collection and its sub-collections if missing."""
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


def sort_level_children(scene):
    """Move objects hanging off level walls (doors, windows, cabinets on a
    wall...) out of the scene's master collection into their level, so
    hiding a level hides them too. Tools still create objects in the
    master collection until they are taught about levels; this keeps the
    house tidy in the meantime."""
    house = scene.hb_house
    for obj in list(scene.collection.objects):
        if obj.get(LEVEL_KEY) and obj.get('IS_WALL_BP'):
            level = get_level(obj[LEVEL_KEY])
            if level is not None:
                assign_wall_to_level(obj, level, scene)
            continue
        uid = level_of(obj.parent) if obj.parent else ''
        if not uid:
            continue
        level = get_level(uid)
        if level is None:
            continue
        ensure_level_collections(scene, level)
        move_to_collection(obj, level_subcollection(level, 'Products'))
    return house


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


def new_wall_height(level, wall_type, scene_props):
    """Height for a new wall on this level: full-height types take the
    level's ceiling height, the others keep their scene defaults."""
    if wall_type in {'Exterior', 'Interior'}:
        return level.ceiling_height
    if wall_type == 'Half':
        return scene_props.half_wall_height
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


def _update_ceiling_height(self, context):
    level = active_level(context)
    if level is not None and level.uid == self.uid:
        props = self.id_data.home_builder
        if abs(props.ceiling_height - self.ceiling_height) > 1e-9:
            props.ceiling_height = self.ceiling_height


class HB_Level(PropertyGroup):
    uid: StringProperty(name="Level ID")  # type: ignore

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


def _update_active_level(self, context):
    scene = self.id_data
    if not self.levels:
        return
    level = self.levels[min(self.active_level_index, len(self.levels) - 1)]
    props = scene.home_builder
    if abs(props.ceiling_height - level.ceiling_height) > 1e-9:
        props.ceiling_height = level.ceiling_height
    apply_level_display(scene)


def _update_level_display(self, context):
    scene = self.id_data
    sort_level_children(scene)
    apply_level_display(scene)


class HB_House_Props(PropertyGroup):
    levels: CollectionProperty(type=HB_Level)  # type: ignore

    active_level_index: IntProperty(
        name="Active Level", update=_update_active_level)  # type: ignore

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
    top = max(house.levels, key=lambda l: l.elevation) if house.levels else None
    level = house.levels.add()
    level.uid = _new_uid()
    level['name'] = name or f"Level {len(house.levels)}"
    if top is not None:
        elevation = top.elevation + top.floor_to_floor
        level['floor_to_floor'] = top.floor_to_floor
        level['applied_floor_to_floor'] = top.floor_to_floor
        level['floor_thickness'] = top.floor_thickness
        level['ceiling_height'] = top.ceiling_height
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

    def execute(self, context):
        scene = context.scene
        house = scene.hb_house
        level = add_level(scene)
        house.active_level_index = len(house.levels) - 1
        self.report({'INFO'}, f"Added {level.name}")
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_level(bpy.types.Operator):
    bl_idname = "home_builder.remove_level"
    bl_label = "Remove Level"
    bl_description = "Remove the active level. Only an empty level can be removed"
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
        if col is not None and len(col.all_objects) > 0:
            self.report({'WARNING'},
                        f"{level.name} still has {len(col.all_objects)} object(s). "
                        "Delete them first")
            return {'CANCELLED'}
        name = level.name
        if col is not None:
            for sub in list(col.children):
                bpy.data.collections.remove(sub)
            bpy.data.collections.remove(col)
        house.levels.remove(index)
        house.active_level_index = max(0, min(index, len(house.levels) - 1))
        self.report({'INFO'}, f"Removed {name}")
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
    HB_Level,
    HB_House_Props,
    HOME_BUILDER_OT_start_house_project,
    HOME_BUILDER_OT_add_level,
    HOME_BUILDER_OT_remove_level,
    HOME_BUILDER_OT_set_active_level,
)


def register():
    global _ghost_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    HB_House_Props.register()
    _ghost_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_level_ghost, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global _ghost_handle
    if _ghost_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_ghost_handle, 'WINDOW')
        _ghost_handle = None
    HB_House_Props.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
