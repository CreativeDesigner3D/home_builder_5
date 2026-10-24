"""
Home Builder Rooms

Rooms in a house project: every closed area of walls on a level, found
by hb_wall_graph.find_rooms, with a floor, a ceiling and a label made
for it. See docs/house_levels_and_wall_graph.md, section 6.

A room's identity is its marker - an empty sitting inside the room.
Whichever area contains the marker is that room, so a room keeps its
name, finishes and ceiling height when the walls around it move. An
area with no marker gets a new room; two markers in one area (a wall
was taken out) keep the older room and leave the other without an area
rather than deleting what the user set on it.

Rooms are rebuilt after every wall edit on the level (walls.py calls
rebuild_after_walls) and by the Rebuild Rooms command. The floor,
ceiling and label are replaced on each rebuild, never edited; anything
worth keeping lives on the room (HB_Room in hb_house).
"""

import bpy
import bmesh
from mathutils import Vector

from . import hb_house, hb_utils, hb_wall_graph
from .units import inch

ROOM_KEY = 'HB_ROOM'
MARKER_KEY = 'IS_ROOM_MARKER'
GENERATED_KEY = 'IS_ROOM_GENERATED'

FLOOR_THICKNESS = 0.01          # thin slab, so floor cutters have volume to cut
SLAB_CLEARANCE = 0.003          # between a floor's underside and the ceiling below
LABEL_SIZE = inch(8)
LABEL_LIFT = 0.02               # label just above the floor
LABEL_COLOR = (0.03, 0.03, 0.03, 1.0)
LABEL_MATERIAL = "HB Room Label"


# =============================================================================
# LOOKUPS
# =============================================================================

def level_of_room(room):
    """The HB_Level holding a room ('hb_house.levels[i].rooms[j]')."""
    path = room.path_from_id()
    level_path = path[:path.rindex('.rooms[')]
    return room.id_data.path_resolve(level_path)


def room_height(room, level):
    return room.ceiling_height if room.ceiling_height > 0 else level.ceiling_height


def area_text(scene, area):
    if scene.unit_settings.system == 'IMPERIAL':
        return f"{area * 10.7639:.0f} sq ft"
    return f"{area:.1f} m²"


# =============================================================================
# GEOMETRY
# =============================================================================

def _slab_mesh(name, polygon, z, thickness=0.0, facing_down=False):
    """An n-gon over the room's outline at height z, extruded down by
    `thickness` when given. Planar UVs in metres, like the wall floors."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for x, y in polygon]
    face = bm.faces.new(verts)
    bm.normal_update()
    if (face.normal.z < 0) != facing_down:
        face.normal_flip()
    if thickness > 0:
        res = bmesh.ops.extrude_face_region(bm, geom=[face])
        moved = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=moved, vec=Vector((0, 0, -thickness)))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x, loop.vert.co.y)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _swap_mesh(obj, mesh, material):
    """Give obj a new mesh, keeping the materials the old one had (a floor
    finish picked with the Floor tool) unless the room names one."""
    old = obj.data
    if material is not None:
        mesh.materials.append(material)
    elif old is not None:
        for mat in old.materials:
            mesh.materials.append(mat)
    obj.data = mesh
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)


def _generated(scene, level, room, name, data, tags):
    col = hb_house.level_subcollection(level, 'Rooms')
    obj = hb_utils.new_object(name, data)
    col.objects.link(obj)
    obj[hb_house.LEVEL_KEY] = level.uid
    obj[ROOM_KEY] = room.uid
    obj[GENERATED_KEY] = True
    for tag in tags:
        obj[tag] = True
    return obj


def _remove(obj):
    if obj is None:
        return
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and data.users == 0:
        if isinstance(data, bpy.types.Mesh):
            bpy.data.meshes.remove(data)
        elif isinstance(data, bpy.types.Curve):
            bpy.data.curves.remove(data)


def _build_floor(scene, level, room, polygon):
    if not room.has_floor:
        _remove(room.floor_obj)
        room.floor_obj = None
        return
    # Meshes are built level-relative and the object carries the level's
    # elevation, so moving the level (which moves free objects) and
    # rebuilding agree
    mesh = _slab_mesh(f"Floor - {room.name}", polygon, 0.0,
                      thickness=floor_slab_thickness(level))
    floor_mat = room_floor_material(room)
    if room.floor_obj is None:
        if floor_mat is not None:
            mesh.materials.append(floor_mat)
        room.floor_obj = _generated(scene, level, room, f"Floor - {room.name}",
                                    mesh, ('IS_FLOOR_BP',))
    else:
        _swap_mesh(room.floor_obj, mesh, floor_mat)
        room.floor_obj.name = f"Floor - {room.name}"
    room.floor_obj.location = (0.0, 0.0, level.elevation)


def _build_ceiling(scene, level, room, polygon):
    if not room.has_ceiling:
        _remove(room.ceiling_obj)
        room.ceiling_obj = None
        return
    mesh = _slab_mesh(f"Ceiling - {room.name}", polygon, room_height(room, level),
                      facing_down=True)
    if room.ceiling_obj is None:
        if room.ceiling_material is not None:
            mesh.materials.append(room.ceiling_material)
        room.ceiling_obj = _generated(scene, level, room, f"Ceiling - {room.name}",
                                      mesh, ('IS_CEILING_BP',))
    else:
        _swap_mesh(room.ceiling_obj, mesh, room.ceiling_material)
        room.ceiling_obj.name = f"Ceiling - {room.name}"
    room.ceiling_obj.location = (0.0, 0.0, level.elevation)
    room.ceiling_obj.hide_viewport = not scene.hb_house.show_ceilings


def _new_marker(scene, level, room, point):
    marker = _generated(scene, level, room, f"Room - {room.name}", None,
                        (MARKER_KEY,))
    del marker[GENERATED_KEY]       # the marker is the room, not made from it
    marker.empty_display_type = 'PLAIN_AXES'
    marker.empty_display_size = 0.15
    marker.hide_render = True
    marker.location = (point[0], point[1], level.elevation)
    return marker


def _label_material():
    """Dark, so a label reads against a white floor or ceiling in solid
    shading (which colours by the material's viewport colour)."""
    mat = bpy.data.materials.get(LABEL_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(LABEL_MATERIAL)
        mat.diffuse_color = LABEL_COLOR
    return mat


def update_room_label(room):
    """Write the room's name and area onto its label (made if missing)."""
    marker = room.marker
    if marker is None:
        return
    scene = room.id_data
    level = level_of_room(room)
    marker.name = f"Room - {room.name}"
    if room.view_scene is not None and room.view_scene.name != room.name:
        room.view_scene.name = room.name
    lines = [room.name.upper()]
    lines.append("(not enclosed)" if room.orphaned else area_text(scene, room.area))
    label = room.label_obj
    if label is None:
        curve = bpy.data.curves.new(f"Room Label - {room.name}", 'FONT')
        curve.size = LABEL_SIZE
        curve.align_x = 'CENTER'
        curve.align_y = 'CENTER'
        label = _generated(scene, level, room, f"Room Label - {room.name}",
                           curve, ('IS_ROOM_LABEL_3D',))
        label.hide_render = True
        label.parent = marker
        label.location = (0.0, 0.0, LABEL_LIFT)
        label.hide_select = True
        room.label_obj = label
    label.data.body = "\n".join(lines)
    label.name = f"Room Label - {room.name}"
    # Drawn in front of everything, so the ceiling over a closed room
    # doesn't hide it in plan
    label.show_in_front = True
    marker.show_in_front = True
    label.color = LABEL_COLOR
    if not label.data.materials:
        label.data.materials.append(_label_material())


def room_floor_material(room, rebuild=False):
    """The material the room's floor finish calls for, or None for no
    finish (the floor keeps what it has - a Floor tool material, say).

    Wood, tile and solid finishes are built from shader nodes by the
    Floor tool's builder into a material of the room's own, found again
    by the room's id. Building is only redone when asked (a finish
    setting changed) or when the material is missing, not on every wall
    edit."""
    finish = room.floor_finish
    if finish == 'CUSTOM':
        return room.floor_material
    if finish == 'NONE':
        return None
    builder = 'WOOD' if finish == 'DECK' else finish    # deck boards are planks
    mat = next((m for m in bpy.data.materials
                if m.get('HB_ROOM_FLOOR') == room.uid), None)
    if mat is not None and not rebuild:
        return mat
    if mat is None:
        mat = bpy.data.materials.new(f"{room.name} Floor")
        mat['HB_ROOM_FLOOR'] = room.uid
    from .operators import ops_room_dressing as dressing
    dressing.build_floor_material(
        builder, tuple(room.floor_color),
        tuple(room.floor_accent) if builder != 'SOLID' else None,
        room.floor_size, room.floor_roughness, room.floor_running_bond,
        mat=mat)
    return mat


def apply_ceiling_visibility(scene):
    """Show or hide every room ceiling in the viewport, per the house's
    Show Ceilings switch. Hidden ceilings still render, and the viewport
    can't pick or snap to them, so they stay out of the way of doors."""
    hide = not scene.hb_house.show_ceilings
    for level in scene.hb_house.levels:
        for room in level.rooms:
            if room.ceiling_obj is not None:
                room.ceiling_obj.hide_viewport = hide


def apply_room_materials(room, rebuild_floor=False):
    """Put the room's floor finish and ceiling material on its floor and
    ceiling."""
    floor_mat = room_floor_material(room, rebuild=rebuild_floor)
    for obj, mat in ((room.floor_obj, floor_mat),
                     (room.ceiling_obj, room.ceiling_material)):
        if obj is None or obj.data is None or mat is None:
            continue
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)


# =============================================================================
# REBUILD
# =============================================================================

def _next_room_name(level, base="Room"):
    used = {room.name for room in level.rooms}
    n = 1
    while f"{base} {n}" in used:
        n += 1
    return f"{base} {n}"


def _make_outdoor(room):
    """A new room a railing runs round: a balcony. No ceiling, deck boards,
    set without the update callbacks - the rebuild that follows builds it."""
    from .operators import ops_room_dressing as dressing
    room['outdoor'] = True
    room['has_ceiling'] = False
    room['floor_finish'] = hb_house._FLOOR_FINISH_INDEX['DECK']
    room['floor_size'] = dressing.DEFAULT_SIZE['DECK']
    room['floor_roughness'] = dressing.DEFAULT_ROUGHNESS['DECK']
    keys = [item[0] for item in hb_house._floor_look_items_cb(room, bpy.context)]
    room['floor_look'] = keys.index(dressing.DEFAULT_LOOK['DECK'])
    hb_house._apply_floor_look(room)
    room_floor_material(room, rebuild=True)


def _forget_room(level, index):
    room = level.rooms[index]
    for obj in (room.label_obj, room.floor_obj, room.ceiling_obj):
        _remove(obj)
    level.rooms.remove(index)


def rebuild_level(scene, level):
    """Find the rooms on a level and remake their floors, ceilings and
    labels. Returns the number of enclosed rooms. `scene` may be a room
    view; the house scene is what gets rebuilt."""
    scene = hb_house.house_scene_of(scene)
    if scene is None or level is None:
        return 0
    from .operators import walls
    hb_house.ensure_level_collections(scene, level)
    walls._update_scene(scene)
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    areas = hb_wall_graph.find_rooms(segs)

    # A room whose marker was deleted is gone
    for i in reversed(range(len(level.rooms))):
        marker = level.rooms[i].marker
        if marker is None or marker.name not in scene.objects:
            _forget_room(level, i)

    # Each marker claims the area it sits in, oldest room first. Rooms are
    # held by index, never by reference: adding to a collection moves its
    # items in memory, and writing through a reference taken before the
    # add crashes Blender.
    claimed = {}                # area index -> room index
    for i, room in enumerate(level.rooms):
        p = room.marker.location
        hit = next((k for k, a in enumerate(areas)
                    if hb_wall_graph.point_in_polygon((p.x, p.y), a.polygon)), None)
        if hit is None or hit in claimed:
            room.orphaned = True
            continue
        room.orphaned = False
        claimed[hit] = i

    # An area nobody claims is a new room
    from .hb_house import _new_uid
    for k, area in enumerate(areas):
        if k in claimed:
            continue
        room = level.rooms.add()
        room.uid = _new_uid()
        balcony = 'Railing' in area.wall_types
        room['name'] = _next_room_name(level, "Balcony" if balcony else "Room")
        if balcony:
            _make_outdoor(room)
        room.marker = _new_marker(scene, level, room,
                                  hb_wall_graph.interior_point(area.polygon))
        claimed[k] = len(level.rooms) - 1

    for k, i in claimed.items():
        room = level.rooms[i]
        area = areas[k]
        room.area = area.area
        room.marker.location.z = level.elevation
        _build_floor(scene, level, room, area.floor)
        _build_ceiling(scene, level, room, area.polygon)
        update_room_label(room)
    for room in level.rooms:
        if room.orphaned:
            _remove(room.floor_obj)
            _remove(room.ceiling_obj)
            room.floor_obj = room.ceiling_obj = None
            room.area = 0.0
            update_room_label(room)
    # New floors and ceilings need their stairwell openings
    apply_stairwells(scene)
    return len(claimed)


def rebuild_room(room):
    """A room's own settings changed: rebuild its level (cheap, and the
    only way to get its outline)."""
    rebuild_level(room.id_data, level_of_room(room))


def rebuild_after_walls(scene, level_uid=None):
    """Called after walls are edited. Only a house (or a room view of one)
    has rooms."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    if not hb_house.is_house_project():
        return
    house = scene.hb_house
    for level in house.levels:
        if level_uid is None or level.uid == level_uid:
            rebuild_level(scene, level)
            # Walls on this level decide how high the exterior walls of
            # the level below run, and its own walls follow the level above
            below = hb_house.level_below(house, level)
            if below is not None:
                hb_house.set_exterior_wall_heights(scene, below)
            hb_house.set_exterior_wall_heights(scene, level)


# =============================================================================
# STAIRWELLS
# =============================================================================
# Stairs on a house level rise to the level above. Each one carries a
# stairwell cutter - a box over its footprint, parented to it so it moves
# with it - and a Boolean on every room floor of the level above and every
# room ceiling of its own level cuts the opening it climbs through.

STAIRWELL_KEY = 'IS_STAIRWELL_CUTTER'
STAIRWELL_REACH = 0.05      # past the surfaces it cuts


level_above = hb_house.level_above


def stair_rise(level):
    """How far stairs on `level` climb: to the next level's floor."""
    return hb_house.rise_to_level_above(level)


def floor_slab_thickness(level):
    """A floor fills the space down to the ceiling of the level below it,
    so from below or outside there is one solid floor between levels. On
    the ground level it is a thin slab."""
    house = level.id_data.hb_house
    below = hb_house.level_below(house, level)
    if below is None:
        return FLOOR_THICKNESS
    gap = level.elevation - (below.elevation + below.ceiling_height)
    # Stop just short of the ceiling below: two faces at one height
    # flicker against each other (z-fighting)
    return max(gap - SLAB_CLEARANCE, FLOOR_THICKNESS)


def stairwell_cutter(stair):
    for child in stair.children:
        if child.get(STAIRWELL_KEY):
            return child
    return None


def update_stairwell_cutter(stair):
    """Fit the stair's cutter to its footprint and to the floor it climbs
    through, making it the first time."""
    level = hb_house.get_level(stair.get(hb_house.LEVEL_KEY, ''))
    if level is None or stair.data is None or not stair.data.vertices:
        return None
    xs = [v.co.x for v in stair.data.vertices]
    ys = [v.co.y for v in stair.data.vertices]
    rise = float(stair.get('STAIR_TOTAL_RISE', stair_rise(level)))
    z0 = min(level.ceiling_height, rise) - STAIRWELL_REACH
    z1 = rise + STAIRWELL_REACH
    cutter = stairwell_cutter(stair)
    if cutter is None:
        cutter = hb_utils.new_object("Stairwell", bpy.data.meshes.new("Stairwell"))
        for col in stair.users_collection:
            col.objects.link(cutter)
        cutter.parent = stair
        cutter.matrix_parent_inverse.identity()
        cutter[STAIRWELL_KEY] = True
        cutter['IS_CUTTING_OBJ'] = True
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
    # Out of the viewport entirely: its Boolean still cuts, but walk
    # mode's gravity and the snapping rays go straight through the
    # opening instead of landing on an invisible box
    cutter.hide_viewport = True
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = min(xs) if v.co.x < 0 else max(xs)
        v.co.y = min(ys) if v.co.y < 0 else max(ys)
        v.co.z = z0 if v.co.z < 0 else z1
    bm.to_mesh(cutter.data)
    bm.free()
    cutter.data.update()
    return cutter


def _stairs_on(scene, level):
    return [o for o in scene.objects
            if o.get('IS_STAIR') and o.get(hb_house.LEVEL_KEY) == level.uid]


def _set_boolean(host, cutter):
    name = f"Stairwell - {cutter.parent.name}"
    mod = host.modifiers.get(name)
    if mod is None:
        mod = host.modifiers.new(name=name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        # Ceilings are single sheets: tell the exact solver to expect holes
        mod.use_hole_tolerant = True
    mod.object = cutter


def _drop_stale_stairwells(obj, keep):
    for mod in list(obj.modifiers):
        if (mod.type == 'BOOLEAN' and mod.name.startswith("Stairwell - ")
                and (mod.object is None or mod.object not in keep)):
            obj.modifiers.remove(mod)


def apply_stairwells(scene):
    """Cut every stair's opening: the room floors of the level above it
    and the room ceilings of its own level."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    house = scene.hb_house
    cuts = {}               # host object -> {cutters}
    for level in house.levels:
        for room in level.rooms:
            for obj in (room.floor_obj, room.ceiling_obj):
                if obj is not None:
                    cuts.setdefault(obj, set())
    for level in house.levels:
        upper = level_above(house, level)
        for stair in _stairs_on(scene, level):
            cutter = update_stairwell_cutter(stair)
            if cutter is None:
                continue
            hosts = [r.ceiling_obj for r in level.rooms if r.ceiling_obj]
            if upper is not None:
                hosts += [r.floor_obj for r in upper.rooms if r.floor_obj]
            for host in hosts:
                cuts.setdefault(host, set()).add(cutter)
    for host, cutters in cuts.items():
        _drop_stale_stairwells(host, cutters)
        for cutter in cutters:
            _set_boolean(host, cutter)


# =============================================================================
# ROOM VIEWS
# =============================================================================
# A room view is a scene for working on one room with the usual tools. It
# links its level's collections (walls, products, rooms, lights) straight
# from the house scene - real links, not instances - so the walls and
# cabinets in it ARE the house's: anything placed here shows in the house
# and in every other view of the level, and every tool that looks at
# scene.objects finds real walls. Objects tools create here land in the
# view's master collection and hb_house.adopt_loose_objects moves them
# onto the level.

def _copy_view_settings(src, dst, room, level):
    dst.unit_settings.system = src.unit_settings.system
    dst.unit_settings.scale_length = src.unit_settings.scale_length
    dst.unit_settings.length_unit = src.unit_settings.length_unit
    dst.world = src.world
    dst.home_builder.product_tab = src.home_builder.product_tab
    dst.home_builder.ceiling_height = room_height(room, level)
    try:
        dst.hb_face_frame.top_drawer_opening_height = (
            src.hb_face_frame.top_drawer_opening_height)
    except Exception:
        pass
    if not src.home_builder.show_appliance_models:
        dst.home_builder['show_appliance_models'] = False


def _copy_tool_settings(src, dst):
    a, b = src.tool_settings, dst.tool_settings
    for prop in ('use_snap', 'snap_target', 'use_snap_grid_absolute',
                 'use_snap_align_rotation', 'use_snap_backface_culling'):
        try:
            setattr(b, prop, getattr(a, prop))
        except Exception:
            pass
    try:
        b.snap_elements = set(a.snap_elements)
    except Exception:
        pass


def _frame_room(context, room, level):
    """Look straight down on the room, zoomed to fit it."""
    from . import hb_utils
    obj = room.floor_obj or room.marker
    if obj is None:
        return
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    size = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    hb_utils.set_plan_view()
    for area in context.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        r3d = area.spaces.active.region_3d
        r3d.view_location = Vector(((min(xs) + max(xs)) / 2.0,
                                    (min(ys) + max(ys)) / 2.0,
                                    level.elevation))
        r3d.view_distance = size * 1.4


def open_room_view(context, room):
    """Switch to the room's view scene, making it the first time."""
    from . import hb_utils
    house_scene = room.id_data
    level = level_of_room(room)
    view = room.view_scene
    if view is not None and view.name in bpy.data.scenes:
        bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=view.name)
        return view

    view = bpy.data.scenes.new(room.name)
    view['IS_ROOM_SCENE'] = True
    view[hb_house.ROOM_VIEW_KEY] = True
    view[hb_house.LEVEL_KEY] = level.uid
    view[hb_house.ROOM_KEY] = room.uid
    hb_house.ensure_level_collections(house_scene, level)
    for kind in hb_house.LEVEL_SUBCOLLECTIONS:
        sub = hb_house.level_subcollection(level, kind)
        if sub is not None and sub.name not in view.collection.children:
            view.collection.children.link(sub)
    _copy_view_settings(house_scene, view, room, level)
    room.view_scene = view

    if context.window is None:
        return view             # no window to switch (background mode)
    current = context.scene
    if hb_utils.is_room_scene(current):
        hb_utils.save_view_state(current)
    context.window.scene = view
    _copy_tool_settings(house_scene, view)
    _frame_room(context, room, level)
    hb_utils.save_view_state(view)
    return view


# =============================================================================
# OPERATORS
# =============================================================================

class HOME_BUILDER_OT_rebuild_rooms(bpy.types.Operator):
    bl_idname = "home_builder.rebuild_rooms"
    bl_label = "Rebuild Rooms"
    bl_description = ("Find the rooms on the active level again and remake their "
                      "floors, ceilings and labels. Use after moving a room marker")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_house.active_level(context) is not None

    def execute(self, context):
        level = hb_house.active_level(context)
        count = rebuild_level(context.scene, level)
        self.report({'INFO'}, f"{level.name}: {count} room(s)")
        return {'FINISHED'}


class HOME_BUILDER_OT_select_room(bpy.types.Operator):
    bl_idname = "home_builder.select_room"
    bl_label = "Select Room Marker"
    bl_description = "Select the active room's marker, to move it into another area"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        return level is not None and 0 <= level.active_room_index < len(level.rooms)

    def execute(self, context):
        level = hb_house.active_level(context)
        marker = level.rooms[level.active_room_index].marker
        if marker is None:
            return {'CANCELLED'}
        for obj in context.selected_objects:
            obj.select_set(False)
        marker.select_set(True)
        context.view_layer.objects.active = marker
        return {'FINISHED'}


class HOME_BUILDER_OT_open_room_view(bpy.types.Operator):
    bl_idname = "home_builder.open_room_view"
    bl_label = "Open Room View"
    bl_description = ("Work on the active room in a view of its own, with the "
                      "usual cabinet and layout tools. Its walls and cabinets "
                      "are the house's: changes show in the house")
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        level = hb_house.active_level(context)
        if level is None or not 0 <= level.active_room_index < len(level.rooms):
            return False
        return not level.rooms[level.active_room_index].orphaned

    def execute(self, context):
        level = hb_house.active_level(context)
        room = level.rooms[level.active_room_index]
        open_room_view(context, room)
        return {'FINISHED'}


class HOME_BUILDER_OT_go_to_house(bpy.types.Operator):
    bl_idname = "home_builder.go_to_house"
    bl_label = "Go to House"
    bl_description = "Back to the house scene"

    @classmethod
    def poll(cls, context):
        return (hb_house.is_room_view(context.scene)
                and hb_house.get_house_scene() is not None)

    def execute(self, context):
        bpy.ops.home_builder_layouts.go_to_layout_view(
            scene_name=hb_house.get_house_scene().name)
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_rebuild_rooms,
    HOME_BUILDER_OT_select_room,
    HOME_BUILDER_OT_open_room_view,
    HOME_BUILDER_OT_go_to_house,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
