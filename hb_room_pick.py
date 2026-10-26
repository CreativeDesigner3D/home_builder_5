"""Click a room in the viewport to open its properties.

A click on a room's floor, ceiling or marker makes that room the active
one on its level and opens it on the HOUSE tab's Rooms page. The floor
and ceiling are made from the room, so a click on them does not leave
them selected -- a G or X afterwards would move or delete a mesh the
next rebuild throws away. The marker is the room itself and stays
selected.

While the HOUSE tab is open on the Rooms page, the room the page shows
is outlined in the viewport, so it is plain which room the fields are
for -- whether it was picked by a click or from the list.
"""
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from . import hb_house
from .hb_gpu_ui import Theme

_msgbus_owner = object()
_busy = False
_draw_handle = None

OUTLINE_WIDTH = 3.0
OUTLINE_LIFT = 0.01          # metres above the floor, so the line is not buried
FILL_ALPHA = 0.18            # the tint over the room; the walls read blue too


# ---------------------------------------------------------------------------
# Finding the room
# ---------------------------------------------------------------------------

def room_of(obj):
    """(level index, room index) for an object made from a room, else None."""
    if obj is None:
        return None
    room_uid = obj.get(hb_house.ROOM_KEY)
    level_uid = obj.get(hb_house.LEVEL_KEY)
    if not room_uid or not level_uid:
        return None
    scene = hb_house.house_scene_of(bpy.context.scene)
    if scene is None:
        return None
    for li, level in enumerate(scene.hb_house.levels):
        if level.uid != level_uid:
            continue
        for ri, room in enumerate(level.rooms):
            if room.uid == room_uid:
                return li, ri
    return None


def open_room(scene, level_index, room_index):
    """Make the room active and show it on the HOUSE tab's Rooms page."""
    from .operators import scene_navigator, house_panel_tab
    house = scene.hb_house
    if house.active_level_index != level_index:
        house.active_level_index = level_index
    level = house.levels[level_index]
    if level.active_room_index != room_index:
        level.active_room_index = room_index
    scene_navigator.set_active_tab(house_panel_tab.TAB_KEY)
    if not scene_navigator.panel_open():
        scene_navigator.open_panel()
    house_panel_tab.set_page('ROOMS')
    _tag_redraw()


# ---------------------------------------------------------------------------
# The click
# ---------------------------------------------------------------------------

def _on_active_changed():
    global _busy
    if _busy:
        return
    context = bpy.context
    obj = getattr(context.view_layer.objects, 'active', None) if context.view_layer else None
    found = room_of(obj)
    if found is None:
        return
    scene = hb_house.house_scene_of(context.scene)
    _busy = True
    try:
        open_room(scene, *found)
        from . import hb_rooms
        if not obj.get(hb_rooms.MARKER_KEY):
            obj.select_set(False)
            context.view_layer.objects.active = None
    except Exception as e:
        print(f"room pick: {e}")
    finally:
        _busy = False


def ensure_subscriptions():
    """(Re)subscribe. msgbus subscriptions do not survive a .blend load,
    so load_post calls this too."""
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        owner=_msgbus_owner, args=(), notify=_on_active_changed)


# ---------------------------------------------------------------------------
# The outline
# ---------------------------------------------------------------------------

def _top_faces(room):
    """(object, polygons) for the top of the room's floor, or of its
    ceiling when it has no floor."""
    obj = room.floor_obj or room.ceiling_obj
    if obj is None or obj.type != 'MESH':
        return None, []
    mesh = obj.data
    top = max((v.co.z for v in mesh.vertices), default=0.0)
    polys = [poly for poly in mesh.polygons
             if abs(poly.normal.z) >= 0.9
             and all(abs(mesh.vertices[i].co.z - top) <= 1e-4 for i in poly.vertices)]
    return obj, polys


def outline_segments(room):
    """World-space line pairs round the top of the room's floor."""
    obj, polys = _top_faces(room)
    if not polys:
        return []
    mesh = obj.data
    m = obj.matrix_world
    uses = {}
    for poly in polys:
        for key in poly.edge_keys:
            uses[key] = uses.get(key, 0) + 1
    lift = Vector((0.0, 0.0, OUTLINE_LIFT))
    coords = []
    for (a, b), n in uses.items():
        if n == 1:
            coords.append(m @ mesh.vertices[a].co + lift)
            coords.append(m @ mesh.vertices[b].co + lift)
    return coords


def fill_triangles(room):
    """World-space triangles over the top of the room's floor."""
    obj, polys = _top_faces(room)
    if not polys:
        return []
    mesh = obj.data
    mesh.calc_loop_triangles()
    keep = {poly.index for poly in polys}
    m = obj.matrix_world
    lift = Vector((0.0, 0.0, OUTLINE_LIFT))
    return [m @ mesh.vertices[i].co + lift
            for tri in mesh.loop_triangles if tri.polygon_index in keep
            for i in tri.vertices]


def shown_room(context):
    """The room the Rooms page shows, while it is on screen, else None."""
    from .operators import scene_navigator, house_panel_tab
    scene = context.scene
    if scene is None or not scene.get(hb_house.HOUSE_SCENE_KEY):
        return None
    if not scene_navigator.panel_open():
        return None
    if scene_navigator.active_tab() != house_panel_tab.TAB_KEY:
        return None
    if house_panel_tab.current_page() != 'ROOMS':
        return None
    level = hb_house.active_level(context)
    if level is None or not level.rooms:
        return None
    return level.rooms[min(max(level.active_room_index, 0), len(level.rooms) - 1)]


def _draw_outline():
    context = bpy.context
    try:
        room = shown_room(context)
    except Exception:
        return
    if room is None:
        return
    coords = outline_segments(room)
    if not coords:
        return
    color = Theme.BTN_ACTIVE_BG[:3]
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    tris = fill_triangles(room)
    if tris:
        fill = gpu.shader.from_builtin('UNIFORM_COLOR')
        fill.uniform_float("color", color + (FILL_ALPHA,))
        batch_for_shader(fill, 'TRIS', {"pos": tris}).draw(fill)
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    region = context.region
    shader.uniform_float("viewportSize", (region.width, region.height))
    shader.uniform_float("lineWidth", OUTLINE_WIDTH)
    shader.uniform_float("color", color + (1.0,))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _tag_redraw():
    wm = bpy.context.window_manager
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def _deferred_setup():
    try:
        ensure_subscriptions()
    except Exception as e:
        print(f"room pick: setup skipped: {e}")
    return None


def register():
    global _draw_handle
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_outline, (), 'WINDOW', 'POST_VIEW')
    # Startup registration runs under a restricted context; subscribe once
    # the main loop is up.
    bpy.app.timers.register(_deferred_setup, first_interval=0.5)


def unregister():
    global _draw_handle
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    if bpy.app.timers.is_registered(_deferred_setup):
        bpy.app.timers.unregister(_deferred_setup)
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
