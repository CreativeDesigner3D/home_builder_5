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

from . import hb_house, hb_utils, hb_wall_graph, hb_porches
from .units import inch

ROOM_KEY = 'HB_ROOM'
MARKER_KEY = 'IS_ROOM_MARKER'
GENERATED_KEY = 'IS_ROOM_GENERATED'

FLOOR_THICKNESS = 0.01          # thin slab, so floor cutters have volume to cut
SLAB_CLEARANCE = 0.003          # between a floor's underside and the ceiling below
LABEL_SIZE = inch(8)
# A marker a wall has been drawn over is this close to the rooms beside it
# (half a wall plus some room): it takes the nearest free one.
ADOPT_DISTANCE = 0.5


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
    top = -room.floor_drop if room.is_porch else 0.0     # a porch steps down
    mesh = _slab_mesh(f"Floor - {room.name}", polygon, top,
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


VAULT_GAP = 0.01        # a vaulted ceiling sits this far under the roof


def vault_frame(scene, level, room):
    """The roof a vaulted or sloped-sides ceiling follows - its level's
    own, or a roof below that the level is inside (a bonus room in the
    roof) - or None for a flat ceiling."""
    if room.ceiling_style not in ('VAULTED', 'ATTIC'):
        return None
    from . import hb_roofs
    frames = []
    if level.roof.enabled:
        frames.append(hb_roofs.roof_frame(scene, level))
    for other in scene.hb_house.levels:
        if other.roof.enabled and other.uid != level.uid:
            frame = hb_roofs.roof_frame(scene, other)
            if frame is not None and level.uid in {l.uid for l in hb_roofs._levels_under(scene, frame)}:
                frames.append(frame)
    # The roof actually over the room: a roof over part of the house, or
    # a wing's roof on the level above, may not be its level's own
    m = room.marker.location if room.marker is not None else None
    for frame in frames:
        if frame is None:
            continue
        if m is None:
            return frame
        u, v = hb_roofs._uv(frame, (m.x, m.y))
        if frame['u0'] <= u <= frame['u1'] and frame['v0'] <= v <= frame['v1']:
            return frame
    return None


def vault_z(frame, room, level, u, v):
    """Height of a vaulted ceiling above the floor at (u, v): under the
    roof, no lower than the room's flat ceiling, no higher than its peak."""
    from . import hb_roofs
    z = hb_roofs.under_z_at(frame, u, v) - level.elevation - VAULT_GAP
    if room.ceiling_style == 'ATTIC':
        # Flat, but down with the roof where the roof is lower
        return max(min(z, room_height(room, level)), 0.05)
    if room.vault_peak > 0:
        z = min(z, room.vault_peak)
    return max(z, room_height(room, level))


def _vault_mesh(name, polygon, room, level, frame):
    """A ceiling following the roof's underside over the room's outline:
    the outline cut where the roof (or the peak) changes slope and each
    piece lifted to it, with a drop all round down to the room's flat
    height - hidden in its walls, and closing the step where it meets a
    flat ceiling across a room divider."""
    from . import hb_roofs
    along_x = frame['along_x']
    flat = room_height(room, level)
    base = level.elevation
    breaks = [u for u, _z in frame['under']]
    level_off = room.vault_peak if room.ceiling_style == 'VAULTED' else room_height(room, level)
    if level_off > 0:
        target = base + VAULT_GAP + level_off
        pts = frame['under']
        for (a, za), (b, zb) in zip(pts, pts[1:]):
            if (za - target) * (zb - target) < 0:
                breaks.append(a + (b - a) * (target - za) / (zb - za))
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, 0.0)) for x, y in polygon]
    bm.faces.new(verts)
    # Cut where the slope changes: across the ridge, and under a hip also
    # along its hip lines and at the same heights on its ends
    cuts = [((u, 0.0), (1.0, 0.0)) for u in breaks]
    if frame.get('style') == 'HIP':
        u0, u1, v0, v1 = frame['u0'], frame['u1'], frame['v0'], frame['v1']
        for u in breaks:
            d = min(u - u0, u1 - u)
            if d > 1e-6:
                cuts += [((0.0, v0 + d), (0.0, 1.0)), ((0.0, v1 - d), (0.0, 1.0))]
        cuts += [((u0, v0), (1.0, -1.0)), ((u1, v0), (1.0, 1.0)),
                 ((u0, v1), (1.0, 1.0)), ((u1, v1), (1.0, -1.0))]
    for (cu, cv), (nu, nv) in cuts:
        co = hb_roofs._world(frame, cu, cv, 0.0)
        no = hb_roofs._world(frame, nu, nv, 0.0)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=co, plane_no=no)
    for v in bm.verts:
        u, w = hb_roofs._uv(frame, (v.co.x, v.co.y))
        v.co.z = vault_z(frame, room, level, u, w)
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z > 0:
            f.normal_flip()
    # The drop round the edge, down to the flat height (a vault rises
    # above it; sloped sides come down to their walls instead)
    bottoms = {}
    edges = [e for e in bm.edges if len(e.link_faces) == 1] if room.ceiling_style == 'VAULTED' else []
    for e in edges:
        a, b = e.verts
        if a.co.z - flat < 1e-4 and b.co.z - flat < 1e-4:
            continue
        for v in (a, b):
            if v not in bottoms:
                bottoms[v] = bm.verts.new((v.co.x, v.co.y, flat))
        if a.co.z - flat < 1e-4:
            bm.faces.new((a, b, bottoms[b]))
        elif b.co.z - flat < 1e-4:
            bm.faces.new((a, b, bottoms[a]))
        else:
            bm.faces.new((a, b, bottoms[b], bottoms[a]))
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co.x, loop.vert.co.y + loop.vert.co.z)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def _build_ceiling(scene, level, room, polygon):
    if not room.has_ceiling:
        _remove(room.ceiling_obj)
        room.ceiling_obj = None
        return
    frame = vault_frame(scene, level, room)
    if frame is not None:
        mesh = _vault_mesh(f"Ceiling - {room.name}", polygon, room, level, frame)
    else:
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


def ceiling_z_at(level, x, y):
    """The height of the ceiling over (x, y) on a level: the underside of
    the ceiling of the room there, flat or vaulted, or the level's ceiling
    height where there is no room."""
    up = Vector((0.0, 0.0, 1.0))
    best = None
    for room in level.rooms:
        obj = room.ceiling_obj
        if obj is None or obj.type != 'MESH' or room.orphaned:
            continue
        inv = obj.matrix_world.inverted()
        start = inv @ Vector((x, y, level.elevation + 0.05))
        hit, loc, _n, _i = obj.ray_cast(start, inv.to_3x3() @ up, distance=100.0)
        if hit:
            z = (obj.matrix_world @ loc).z
            if best is None or z < best:
                best = z
    return best if best is not None else level.elevation + level.ceiling_height


def _new_marker(scene, level, room, point):
    marker = _generated(scene, level, room, f"Room - {room.name}", None,
                        (MARKER_KEY,))
    del marker[GENERATED_KEY]       # the marker is the room, not made from it
    marker.empty_display_type = 'PLAIN_AXES'
    marker.empty_display_size = 0.15
    marker.hide_render = True
    marker.location = (point[0], point[1], level.elevation)
    return marker


def label_point(poly):
    """Where a room's label goes: the middle of the room's outline - its
    centroid, unless that sits off in one wing of an L, when the point
    deepest inside it."""
    pole = None
    best = -1.0
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    steps = 32
    for i in range(1, steps):
        for j in range(1, steps):
            p = (min(xs) + (max(xs) - min(xs)) * i / steps,
                 min(ys) + (max(ys) - min(ys)) * j / steps)
            if not hb_wall_graph.point_in_polygon(p, poly):
                continue
            d = hb_wall_graph._dist_to_edges(p, poly)
            if d > best:
                pole, best = p, d
    c = hb_wall_graph.interior_point(poly)
    if pole is None:
        return c
    if (hb_wall_graph.point_in_polygon(c, poly)
            and hb_wall_graph._dist_to_edges(c, poly) >= 0.7 * best):
        return c
    return pole


def update_room_label(room, poly=None):
    """The room's name and area for its label, and (given its outline)
    where the label goes. The label is drawn over the viewport (see
    draw_room_labels); a text object from an older file is removed."""
    marker = room.marker
    if marker is None:
        return
    marker.name = f"Room - {room.name}"
    if room.view_scene is not None and room.view_scene.name != room.name:
        room.view_scene.name = room.name
    if room.label_obj is not None:
        _remove(room.label_obj)
        room.label_obj = None
    if poly:
        room['label_xy'] = label_point(poly)
    scene = room.id_data
    marker.hide_viewport = not scene.hb_house.show_room_labels      # the marker goes with it
    marker.show_in_front = scene.hb_house.show_ceilings
    _tag_redraw()


def refresh_labels(scene):
    """Place the labels of a file's rooms that have no place yet, and
    remove the text objects older files drew them with."""
    from .operators import walls
    for level in scene.hb_house.levels:
        rooms = [r for r in level.rooms
                 if r.marker is not None and (r.label_obj is not None or 'label_xy' not in r)]
        if not rooms:
            continue
        _objs, segs = walls.level_wall_segs(scene, level.uid)
        areas = hb_wall_graph.find_rooms(segs)
        for room in rooms:
            p = room.marker.location
            poly = next((a.polygon for a in areas
                         if hb_wall_graph.point_in_polygon((p.x, p.y), a.polygon)), None)
            update_room_label(room, poly)


def _tag_redraw():
    wm = bpy.context.window_manager
    for window in getattr(wm, 'windows', ()):
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# =============================================================================
# ROOM LABELS
# =============================================================================
# Drawn over the viewport in the annotation font (Calibri where there is
# one), like the dimension labels, rather than as text objects: crisp at
# any zoom. Sized as LABEL_SIZE on the floor, within readable limits, and
# shown while looking down on the plan.

LABEL_PX_MIN = 10
LABEL_PX_MAX = 26
LABEL_TEXT = (0.08, 0.08, 0.08, 1.0)
LABEL_HALO = (1.0, 1.0, 1.0, 0.85)
LOOKING_DOWN = 0.7          # how steeply the view must look down for labels

_label_fonts = None         # (regular, bold) blf font ids
_label_handle = None


def _fonts():
    global _label_fonts
    if _label_fonts is None:
        import blf
        from . import hb_details
        regular = bold = 0
        try:
            path = hb_details._find_calibri()
            if path:
                regular = bold = blf.load(path)
                b = hb_details._find_bold_sibling(path)
                if b:
                    bold = blf.load(b)
        except Exception:
            regular = bold = 0
        _label_fonts = (regular, bold)
    return _label_fonts


def _labels_to_draw(context):
    """(room, level) for the labels to show: rooms whose markers are shown,
    on the highest level showing, unless its roof covers it."""
    scene = hb_house.house_scene_of(context.scene) or context.scene
    house = getattr(scene, 'hb_house', None)
    if house is None or not house.show_room_labels:
        return []
    layer = context.view_layer
    shown = []
    for level in house.levels:
        rooms = []
        for room in level.rooms:
            m = room.marker
            if m is None:
                continue
            try:
                if not m.visible_get(view_layer=layer):
                    continue
            except (RuntimeError, ReferenceError):
                continue
            rooms.append(room)
        if rooms:
            shown.append((level, rooms))
    if not shown:
        return []
    level, rooms = max(shown, key=lambda lr: lr[0].elevation)
    roof = level.roof.roof_obj if level.roof.enabled else None
    if roof is not None:
        try:
            if roof.visible_get(view_layer=layer) and roof.display_type != 'WIRE':
                return []
        except (RuntimeError, ReferenceError):
            pass
    return [(room, level) for room in rooms]


def draw_room_labels():
    import blf
    from bpy_extras import view3d_utils
    context = bpy.context
    region, r3d = context.region, context.region_data
    if region is None or r3d is None:
        return
    look = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))
    if look.z > -LOOKING_DOWN:
        return
    try:
        labels = _labels_to_draw(context)
    except Exception:
        return
    if not labels:
        return
    regular, bold = _fonts()
    right = r3d.view_rotation @ Vector((1.0, 0.0, 0.0))
    for room, level in labels:
        if room.orphaned or 'label_xy' not in room:
            x, y = room.marker.location.x, room.marker.location.y
        else:
            x, y = room['label_xy']
        p = Vector((x, y, level.elevation))
        a = view3d_utils.location_3d_to_region_2d(region, r3d, p)
        b = view3d_utils.location_3d_to_region_2d(region, r3d, p + right)
        if a is None or b is None:
            continue
        size = max(LABEL_PX_MIN, min(LABEL_PX_MAX, LABEL_SIZE * (b - a).length))
        lines = [(bold, size, room.name.upper()),
                 (regular, size * 0.8, "(not enclosed)" if room.orphaned
                  else area_text(room.id_data, room.area))]
        heights = []
        for font, sz, _text in lines:
            blf.size(font, sz)
            heights.append(blf.dimensions(font, "Hg")[1])
        gap = size * 0.25
        top = a.y + (sum(heights) + gap) / 2.0
        for (font, sz, text), h in zip(lines, heights):
            blf.size(font, sz)
            w = blf.dimensions(font, text)[0]
            top -= h
            blf.position(font, a.x - w / 2.0, top, 0)
            blf.color(font, *LABEL_TEXT)
            blf.enable(font, blf.SHADOW)
            blf.shadow(font, 5, *LABEL_HALO)
            blf.shadow_offset(font, 0, 0)
            blf.draw(font, text)
            blf.disable(font, blf.SHADOW)
            top -= gap


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


def apply_label_visibility(scene, hide_markers=False):
    """Show or hide the rooms' labels and their markers per the house's
    Show Room Labels switch; `hide_markers` hides the markers whatever it
    says (Walk Through)."""
    hide = not scene.hb_house.show_room_labels
    for level in scene.hb_house.levels:
        for room in level.rooms:
            if room.label_obj is not None:
                room.label_obj.hide_viewport = hide
            if room.marker is not None:
                room.marker.hide_viewport = hide_markers or hide


def apply_ceiling_visibility(scene):
    """Show or hide every room ceiling in the viewport, per the house's
    Show Ceilings switch. Hidden ceilings still render, and the viewport
    can't pick or snap to them, so they stay out of the way of doors."""
    hide = not scene.hb_house.show_ceilings
    for level in scene.hb_house.levels:
        for room in level.rooms:
            if room.ceiling_obj is not None:
                room.ceiling_obj.hide_viewport = hide
            # Labels only need to draw through the ceilings when they show
            for obj in (room.label_obj, room.marker):
                if obj is not None:
                    obj.show_in_front = not hide


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


VAULT_BASE_KEY = 'HB_VAULT_BASE'    # a raised wall's height before it was raised


def _raise_vault_walls(scene, level, polygons):
    """Interior walls round a vaulted room rise to its ceiling's peak, so
    the vault meets them; the roof's trim cuts them to its underside.
    Walls no longer round one go back to the height they had."""
    from . import hb_types
    from .operators import walls
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    by_id = {s.id: s for s in segs}
    want = {}
    for i, polygon in polygons.items():
        room = level.rooms[i]
        # Only a vault rises above the walls; sloped sides come down to them
        frame = (vault_frame(scene, level, room)
                 if room.has_ceiling and room.ceiling_style == 'VAULTED' else None)
        if frame is None:
            continue
        top = room.vault_peak if room.vault_peak > 0 else frame['ridge_z'] - level.elevation
        n = len(polygon)
        for j in range(n):
            a, b = polygon[j], polygon[(j + 1) % n]
            mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
            for s in segs:
                if (s.wall_type == 'Interior'
                        and hb_porches._dist_to_band(mid, s) < hb_porches.ON_EDGE):
                    want[s.id] = max(want.get(s.id, 0.0), top + 0.05)
    for name, seg in by_id.items():
        obj = scene.objects[name]
        wall = hb_types.GeoNodeWall(obj)
        if name in want:
            if VAULT_BASE_KEY not in obj:
                obj[VAULT_BASE_KEY] = wall.get_input('Height')
            wall.set_input('Height', max(want[name], obj[VAULT_BASE_KEY]))
            obj.update_tag()
        elif VAULT_BASE_KEY in obj:
            wall.set_input('Height', obj[VAULT_BASE_KEY])
            del obj[VAULT_BASE_KEY]
            obj.update_tag()


PORCH_CEILING = inch(108)       # a new porch's ceiling, if the level's is higher


def _make_porch(room, level):
    """A room that porch edges close: outdoors, a concrete floor a step
    down and a ceiling of its own - set without the update callbacks, the
    rebuild that follows builds it."""
    from .operators import ops_room_dressing as dressing
    room['outdoor'] = True
    room['has_ceiling'] = True
    if level.ceiling_height > PORCH_CEILING:
        room['ceiling_height'] = PORCH_CEILING
    room['floor_finish'] = hb_house._FLOOR_FINISH_INDEX['SOLID']
    room['floor_size'] = dressing.DEFAULT_SIZE['SOLID']
    room['floor_roughness'] = dressing.DEFAULT_ROUGHNESS['SOLID']
    keys = [item[0] for item in hb_house._floor_look_items_cb(room, bpy.context)]
    room['floor_look'] = keys.index(dressing.DEFAULT_LOOK['SOLID'])
    hb_house._apply_floor_look(room)
    room_floor_material(room, rebuild=True)


def _forget_room(level, index):
    room = level.rooms[index]
    for obj in (room.label_obj, room.floor_obj, room.ceiling_obj, room.porch_obj,
                room.porch_roof_obj):
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

    # A wall drawn across a room can land right on its marker, which then
    # sits in no area though the room has only been split. Such a room
    # takes the nearest free area beside its marker (the larger, on a tie)
    # and its marker moves into it, so the room keeps its name and finishes
    # for one part and the rest become new rooms. A marker far from any
    # free area stays not enclosed: its walls are open, not split.
    for i, room in enumerate(level.rooms):
        if not room.orphaned:
            continue
        p = (room.marker.location.x, room.marker.location.y)
        best = None
        for k, a in enumerate(areas):
            if k in claimed:
                continue
            d = hb_wall_graph._dist_to_edges(p, a.polygon)
            if d <= ADOPT_DISTANCE and (best is None or (d, -a.area) < best[0]):
                best = ((d, -a.area), k)
        if best is None:
            continue
        k = best[1]
        room.orphaned = False
        claimed[k] = i
        x, y = hb_wall_graph.interior_point(areas[k].polygon)
        room.marker.location.x, room.marker.location.y = x, y

    # An area nobody claims is a new room
    from .hb_house import _new_uid
    new_rooms = []
    for k, area in enumerate(areas):
        if k in claimed:
            continue
        room = level.rooms.add()
        room.uid = _new_uid()
        balcony = 'Railing' in area.wall_types
        porch = hb_porches.is_porch_area(area)
        room['name'] = _next_room_name(
            level, "Porch" if porch else "Balcony" if balcony else "Room")
        if porch:
            room['is_porch'] = True
            _make_porch(room, level)
        elif balcony:
            _make_outdoor(room)
        room.marker = _new_marker(scene, level, room,
                                  hb_wall_graph.interior_point(area.polygon))
        claimed[k] = len(level.rooms) - 1
        new_rooms.append(claimed[k])

    for k, i in claimed.items():
        room = level.rooms[i]
        area = areas[k]
        room.area = area.area
        room.marker.location.z = level.elevation
        # Porch edges drawn round an existing room make it a porch
        porch = hb_porches.is_porch_area(area)
        if porch and not room.is_porch:
            room['is_porch'] = True
            _make_porch(room, level)
        elif not porch and room.is_porch:
            room['is_porch'] = False
        _build_floor(scene, level, room, area.floor)
        _build_ceiling(scene, level, room, area.polygon)
        if room.is_porch:
            hb_porches.build_porch(scene, level, room, area.polygon, segs,
                                   room_floor_material(room))
        elif room.porch_obj is not None:
            hb_porches.remove_porch(room)
        update_room_label(room, area.polygon)
    # New rooms take the house's floor for their kind
    for i in new_rooms:
        hb_house.apply_floor_default(level.rooms[i])
    _raise_vault_walls(scene, level, {i: areas[k].polygon for k, i in claimed.items()})
    for room in level.rooms:
        if room.orphaned:
            _remove(room.floor_obj)
            _remove(room.ceiling_obj)
            hb_porches.remove_porch(room)
            room.floor_obj = room.ceiling_obj = None
            room.area = 0.0
            update_room_label(room)
    # New floors and ceilings need their stairwell openings, and new
    # ceilings under a roof its trim
    apply_stairwells(scene)
    from . import hb_roofs
    hb_roofs.apply_trims(scene)
    return len(claimed)


def rebuild_room(room):
    """A room's own settings changed: rebuild its level (cheap, and the
    only way to get its outline). A porch's height also shapes the roof
    over it (see hb_roofs: the gable carried across it)."""
    rebuild_level(room.id_data, level_of_room(room))
    if room.is_porch:
        from . import hb_roofs
        hb_roofs.rebuild_roofs(room.id_data)


def _refresh_framing(scene):
    from . import hb_framing
    hb_framing.refresh(scene)


def rebuild_after_walls(scene, level_uid=None):
    """Called after walls are edited. Only a house (or a room view of one)
    has rooms."""
    scene = hb_house.house_scene_of(scene)
    if scene is None:
        return
    if not hb_house.is_house_project():
        return
    from . import hb_framing
    house = scene.hb_house
    with hb_framing.held():
        for level in house.levels:
            if level_uid is None or level.uid == level_uid:
                rebuild_level(scene, level)
                # Walls on this level decide how high the exterior walls of
                # the level below run, and its own walls follow the level above
                below = hb_house.level_below(house, level)
                if below is not None:
                    hb_house.set_exterior_wall_heights(scene, below)
                hb_house.set_exterior_wall_heights(scene, level)
        # Roofs follow the walls they sit on and trim the walls under them
        from . import hb_roofs
        hb_roofs.rebuild_roofs(scene)
        # New walls take the house's siding, and the base follows the walls
        from . import hb_exterior
        hb_exterior.apply_exterior_finish(scene)
    # The framing follows all of it
    _refresh_framing(scene)


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


HEADROOM = inch(80)             # clear height over the stair's nosings
GUARD_HEIGHT = inch(36)
GUARD_POST = inch(3.5)
GUARD_POST_SPACING = inch(72)   # at most, between posts along a side
GUARD_RAIL_W = inch(2.5)
GUARD_RAIL_T = inch(1.5)
GUARD_BOTTOM_RAIL = inch(3.0)   # its bottom, above the floor
GUARD_BALUSTER = inch(0.75)
GUARD_BALUSTER_GAP = inch(3.75) # under the 4" sphere a guard must stop
STAIR_GUARD_KEY = 'IS_STAIR_GUARD'


def stair_guard(stair):
    for child in stair.children:
        if child.get(STAIR_GUARD_KEY):
            return child
    return None


def _upper_floor_underside(stair, level):
    """Height of the underside of the floor the stair climbs through, in
    the stair's own space; None with no level above."""
    upper = level_above(level.id_data.hb_house, level)
    if upper is None:
        return None
    rise = float(stair.get('STAIR_TOTAL_RISE', stair_rise(level)))
    return rise - floor_slab_thickness(upper)


def stair_opening_rects(stair, level):
    """The treads and landings that need the floor above opened for
    headroom: their plan rectangles (x0, y0, x1, y1) in the stair's own
    space - those whose top comes within the headroom of the underside of
    the floor above. Empty with no level above."""
    under = _upper_floor_underside(stair, level)
    if under is None or stair.data is None:
        return []
    headroom = float(stair.get('STAIR_HEADROOM', HEADROOM))
    mesh = stair.data
    rects = []
    for poly in mesh.polygons:
        if poly.normal.z < 0.9:
            continue                # treads' and landings' tops only
        co = [mesh.vertices[i].co for i in poly.vertices]
        z = max(c.z for c in co)
        if z + headroom <= under:
            continue                # headroom to spare under the floor
        rects.append((min(c.x for c in co), min(c.y for c in co),
                      max(c.x for c in co), max(c.y for c in co)))
    return rects


def stair_opening(stair, level):
    """(cells, edges) of the stair's opening in its own space: the union of
    the treads that need headroom as cells, and its outline as edges
    (start, end, outward normal). Empty with no level above."""
    from . import hb_structure_geom as geom
    rects = stair_opening_rects(stair, level)
    return geom.rect_union_cells(rects), geom.rect_union_edges(rects)


def stairwell_openings(scene, level):
    """The stair openings through a level's floor, from the stairs on the
    level below: [(cells, edges)] in world XY - cells as 4-point polygons,
    edges as (start, end, outward normal)."""
    house = scene.hb_house
    below = hb_house.level_below(house, level)
    if below is None:
        return []
    out = []
    for stair in _stairs_on(scene, below):
        cells, edges = stair_opening(stair, below)
        if not cells:
            continue
        m = stair.matrix_world
        rot = m.to_3x3()
        w = lambda x, y: (m @ Vector((x, y, 0.0))).to_2d()
        out.append((
            [[tuple(w(x0, y0)), tuple(w(x1, y0)), tuple(w(x1, y1)), tuple(w(x0, y1))]
             for x0, y0, x1, y1 in cells],
            [(tuple(w(*a)), tuple(w(*b)), tuple((rot @ Vector((n[0], n[1], 0.0))).to_2d()))
             for a, b, n in edges]))
    return out


def update_stairwell_cutter(stair):
    """Fit the stair's cutter to the opening it needs, and its guard round
    that opening on the floor above, making them the first time. The
    opening is the treads that need headroom under the floor above; with
    no level above, the stair's whole footprint."""
    level = hb_house.get_level(stair.get(hb_house.LEVEL_KEY, ''))
    if level is None or stair.data is None or not stair.data.vertices:
        return None
    rise = float(stair.get('STAIR_TOTAL_RISE', stair_rise(level)))
    z0 = min(level.ceiling_height, rise) - STAIRWELL_REACH
    z1 = rise + STAIRWELL_REACH
    cells, edges = stair_opening(stair, level)
    if not cells:
        xs = [v.co.x for v in stair.data.vertices]
        ys = [v.co.y for v in stair.data.vertices]
        cells = [(min(xs), min(ys), max(xs), max(ys))]
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
    # One closed solid over the cells: they share whole edges, so welding
    # them, with a side wall per cell side on the outline, leaves no faces
    # inside and no gaps
    bm = bmesh.new()
    for x0, y0, x1, y1 in cells:
        for z, flip in ((z0, True), (z1, False)):
            vs = [bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)),
                  bm.verts.new((x1, y1, z)), bm.verts.new((x0, y1, z))]
            bm.faces.new(list(reversed(vs)) if flip else vs)
    from . import hb_structure_geom as geom
    for (ax, ay), (bx, by), n in geom.rect_union_edges(cells, merge=False):
        # Wound to face outward
        if (bx - ax) * n[1] - (by - ay) * n[0] > 0:
            ax, ay, bx, by = bx, by, ax, ay
        bm.faces.new((bm.verts.new((ax, ay, z0)), bm.verts.new((bx, by, z0)),
                      bm.verts.new((bx, by, z1)), bm.verts.new((ax, ay, z1))))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(cutter.data)
    bm.free()
    cutter.data.update()
    update_stair_guard(stair, level, edges)
    return cutter


def _guard_material():
    mat = bpy.data.materials.get("Stair Guard")
    if mat is None:
        mat = bpy.data.materials.new("Stair Guard")
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (0.86, 0.85, 0.82, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.4
        mat.diffuse_color = (0.86, 0.85, 0.82, 1.0)
    return mat


def _guard_edges(stair, level, edges):
    """The opening's edges a guard goes along: not the one the top flight
    arrives over, nor one running along a wall of the floor above."""
    mesh = stair.data
    tops = sorted(((max(mesh.vertices[i].co.z for i in p.vertices), p)
                   for p in mesh.polygons if p.normal.z > 0.9), key=lambda t: t[0])
    arrive = None
    if len(tops) >= 2:
        top, below = tops[-1][1], tops[-2][1]
        c1, c0 = top.center, below.center
        d = (c1 - c0).to_2d()
        co = [mesh.vertices[i].co for i in top.vertices]
        if abs(d.x) >= abs(d.y):
            arrive = ((1, 0) if d.x > 0 else (-1, 0),
                      max(c.x for c in co) if d.x > 0 else min(c.x for c in co))
        else:
            arrive = ((0, 1) if d.y > 0 else (0, -1),
                      max(c.y for c in co) if d.y > 0 else min(c.y for c in co))
    from .operators import walls
    upper = level_above(level.id_data.hb_house, level)
    scene = hb_house.house_scene_of(stair.users_scene[0]) if stair.users_scene else None
    segs = walls.level_wall_segs(scene, upper.uid)[1] if (scene and upper) else []
    m = stair.matrix_world
    kept = []
    for a, b, n in edges:
        if arrive is not None and n == arrive[0]:
            c = a[0] if n[0] != 0 else a[1]
            if abs(c - arrive[1]) < 1e-4:
                continue            # where the top flight comes up
        mid = (m @ Vector(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, 0.0))).to_2d()
        against_wall = False
        for seg in segs:
            if seg.thickness <= 0.0:
                continue
            rel = (mid.x - seg.start[0], mid.y - seg.start[1])
            along = rel[0] * seg.dir[0] + rel[1] * seg.dir[1]
            off = rel[0] * seg.normal[0] + rel[1] * seg.normal[1]
            if -0.05 <= along <= seg.length + 0.05 and -0.05 <= off <= seg.thickness + 0.05:
                against_wall = True
                break
        if not against_wall:
            kept.append((a, b, n))
    return kept


def update_stair_guard(stair, level, edges=None):
    """Posts, rails and balusters round the stair's opening on the floor
    above, along the edges a person could step off - rebuilt from the
    stair, removed when it has none or its Guard is off."""
    guard = stair_guard(stair)
    if edges is None:
        edges = stair_opening(stair, level)[1]
    rise = float(stair.get('STAIR_TOTAL_RISE', stair_rise(level)))
    kept = _guard_edges(stair, level, edges) if edges and stair.get('STAIR_GUARD', True) else []
    if not kept:
        _remove(guard)
        return None
    height = float(stair.get('STAIR_GUARD_HEIGHT', GUARD_HEIGHT))
    bm = bmesh.new()

    def box(cx, cy, z0, z1, along, w, t):
        """A box centred on (cx, cy), `w` long along unit `along`, `t`
        across, from z0 to z1."""
        ax = Vector((along[0], along[1], 0.0)) * (w / 2.0)
        ac = Vector((-along[1], along[0], 0.0)) * (t / 2.0)
        c = Vector((cx, cy, 0.0))
        ring = [c - ax - ac, c + ax - ac, c + ax + ac, c - ax + ac]
        bottom = [bm.verts.new((p.x, p.y, z0)) for p in ring]
        top = [bm.verts.new((p.x, p.y, z1)) for p in ring]
        bm.faces.new(list(reversed(bottom)))
        bm.faces.new(top)
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((bottom[i], bottom[j], top[j], top[i]))

    posts = set()
    rail_top = rise + height
    for a, b, n in kept:
        # Stand just off the opening, on the floor
        off = (n[0] * GUARD_POST / 2.0, n[1] * GUARD_POST / 2.0)
        ax, ay = a[0] + off[0], a[1] + off[1]
        bx, by = b[0] + off[0], b[1] + off[1]
        length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        if length < 1e-4:
            continue
        u = ((bx - ax) / length, (by - ay) / length)
        count = max(1, int(-(-length // GUARD_POST_SPACING)))
        for k in range(count + 1):
            t = length * k / count
            posts.add((round(ax + u[0] * t, 5), round(ay + u[1] * t, 5)))
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        box(mx, my, rail_top - GUARD_RAIL_T, rail_top, u, length, GUARD_RAIL_W)
        box(mx, my, rise + GUARD_BOTTOM_RAIL, rise + GUARD_BOTTOM_RAIL + GUARD_RAIL_T,
            u, length, GUARD_RAIL_T)
        pitch = GUARD_BALUSTER + GUARD_BALUSTER_GAP
        n_bal = int((length - GUARD_POST) // pitch)
        if n_bal > 0:
            start = (length - (n_bal - 1) * pitch) / 2.0
            for k in range(n_bal):
                t = start + k * pitch
                box(ax + u[0] * t, ay + u[1] * t, rise + GUARD_BOTTOM_RAIL + GUARD_RAIL_T,
                    rail_top - GUARD_RAIL_T, u, GUARD_BALUSTER, GUARD_BALUSTER)
    for x, y in posts:
        box(x, y, rise, rail_top + inch(2.0), (1.0, 0.0), GUARD_POST, GUARD_POST)

    if guard is None:
        guard = hb_utils.new_object("Stair Guard", bpy.data.meshes.new("Stair Guard"))
        for col in stair.users_collection:
            col.objects.link(guard)
        guard.parent = stair
        guard.matrix_parent_inverse.identity()
        guard[STAIR_GUARD_KEY] = True
    bm.to_mesh(guard.data)
    bm.free()
    guard.data.materials.clear()
    guard.data.materials.append(_guard_material())
    guard.data.update()
    return guard


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


def room_area(scene, level, room):
    """The hb_wall_graph.RoomArea a room's marker sits in, or None."""
    from .operators import walls
    if room.marker is None:
        return None
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    p = room.marker.location
    return next((a for a in hb_wall_graph.find_rooms(segs)
                 if hb_wall_graph.point_in_polygon((p.x, p.y), a.polygon)), None)


def room_polygon(scene, level, room):
    """The outline of the area a room's marker sits in, or None."""
    area = room_area(scene, level, room)
    return area.polygon if area is not None else None


def room_faces(scene, level, room):
    """The wall faces that look into a room: [(wall object, side, t0,
    t1)], side 'REF' (the wall's local y = 0 face) or 'FAR' (its
    thickness face), t0..t1 the stretch along the wall the room sees."""
    area = room_area(scene, level, room)
    if area is None:
        return []
    return [(scene.objects[name], side, t0, t1)
            for name, side, t0, t1 in area.faces if name in scene.objects]


ISOLATE_MARGIN = 0.15       # how far past a room's outline its things may reach


def _keeps(obj, room, poly):
    """Does a room's own view show this object (a top-level one)?"""
    if obj.get(ROOM_KEY) is not None:
        return obj.get(ROOM_KEY) == room.uid         # its floor, not the next room's
    m = obj.matrix_world
    if obj.get('IS_WALL_BP'):
        from . import hb_types
        wall = hb_types.GeoNodeWall(obj)
        length = wall.get_input('Length') or 0.0
        thick = wall.get_input('Thickness') or 0.0
        if length <= 0.0:
            return False
        # A wall round the room runs along its outline for some way
        near = 0
        for k in range(1, 10):
            q = m @ Vector((length * k / 10.0, thick / 2.0, 0.0))
            if hb_wall_graph._dist_to_edges((q.x, q.y), poly) <= thick + 0.05:
                near += 1
        return near >= 2
    pts = [m @ Vector(c) for c in obj.bound_box]
    c = sum(pts, Vector()) / 8.0
    return (hb_wall_graph.point_in_polygon((c.x, c.y), poly)
            or hb_wall_graph._dist_to_edges((c.x, c.y), poly) <= ISOLATE_MARGIN)


def isolate_room(view, room):
    """In a room's own view, hide what isn't in the room: the other rooms'
    floors and labels, the walls that don't bound it and the cabinets and
    lights beyond them. Hidden in the view's own view layer only, so the
    house scene shows everything as before; things added in the view
    show as usual."""
    scene = room.id_data
    level = level_of_room(room)
    poly = room_polygon(scene, level, room)
    if poly is None or not view.view_layers:
        return
    layer = view.view_layers[0]
    roots = {}
    for obj in view.objects:
        root = obj
        while root.parent is not None:
            root = root.parent
        if root.name not in roots:
            roots[root.name] = _keeps(root, room, poly)
        try:
            obj.hide_set(not roots[root.name], view_layer=layer)
        except RuntimeError:
            pass                # not in that view layer


def open_room_view(context, room):
    """Switch to the room's view scene, making it the first time."""
    from . import hb_utils
    house_scene = room.id_data
    level = level_of_room(room)
    view = room.view_scene
    if view is not None and view.name in bpy.data.scenes:
        isolate_room(view, room)        # the walls may have changed since
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
    isolate_room(view, room)

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
        marker.hide_viewport = False        # shown to move, with the labels off too
        marker.select_set(True)
        context.view_layer.objects.active = marker
        return {'FINISHED'}


class HOME_BUILDER_OT_open_room_view(bpy.types.Operator):
    bl_idname = "home_builder.open_room_view"
    bl_label = "Open Room View"
    bl_description = ("Work on the active room on its own: a view of just "
                      "the room, its walls and what's in it, with the usual "
                      "cabinet and layout tools. Its walls and cabinets are "
                      "the house's: changes show in the house")
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
    global _label_handle
    for cls in classes:
        bpy.utils.register_class(cls)
    _label_handle = bpy.types.SpaceView3D.draw_handler_add(
        draw_room_labels, (), 'WINDOW', 'POST_PIXEL')


def unregister():
    global _label_handle, _label_fonts
    if _label_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_label_handle, 'WINDOW')
        _label_handle = None
    _label_fonts = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
