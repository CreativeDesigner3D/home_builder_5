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

A right-click after picking a room (or with its marker selected) puts
the room's commands at the top of the viewport's context menu: its type,
name, floor and ceiling, its views, its cutters, and - for a room no
longer enclosed - removing it.
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
_picked = None          # (level uid, room uid) of the room last clicked

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
    global _busy, _picked
    if _busy:
        return
    context = bpy.context
    obj = getattr(context.view_layer.objects, 'active', None) if context.view_layer else None
    found = room_of(obj)
    if found is None:
        if obj is not None:
            _picked = None      # something else picked: the room menu goes
        return
    _picked = (obj.get(hb_house.LEVEL_KEY), obj.get(hb_house.ROOM_KEY))
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
# The right-click menu
# ---------------------------------------------------------------------------

def menu_room(context):
    """The room a right-click is about - its marker is the active object,
    or it was the last thing clicked and nothing else is selected. None
    otherwise."""
    obj = context.active_object
    key = None
    if obj is not None and obj.get(hb_house.ROOM_KEY) and obj.get(hb_house.LEVEL_KEY):
        key = (obj.get(hb_house.LEVEL_KEY), obj.get(hb_house.ROOM_KEY))
    elif _picked is not None and not context.selected_objects:
        key = _picked
    if key is None:
        return None
    scene = hb_house.house_scene_of(context.scene)
    if scene is None:
        return None
    for level in scene.hb_house.levels:
        if level.uid != key[0]:
            continue
        for room in level.rooms:
            if room.uid == key[1]:
                return room
    return None


def _active(context):
    """(level, room) of the active room, for the commands below."""
    level = hb_house.active_level(context)
    if level is None or not 0 <= level.active_room_index < len(level.rooms):
        return level, None
    return level, level.rooms[level.active_room_index]


def draw_room_items(layout, context):
    """The room's commands, at the top of the context menu. True if drawn.
    Picking the room made it the active one (a menu cannot change data as
    it draws), and the commands act on the active room."""
    if menu_room(context) is None:
        return False
    _level, room = _active(context)
    if room is None:
        return False
    layout.label(text=room.name + ("  (not enclosed)" if room.orphaned else ""), icon='HOME')
    layout.menu(HOME_BUILDER_MT_room_type.bl_idname,
                text="Room Type: " + hb_house.TYPE_LABELS.get(room.room_type, ""))
    layout.operator(HOME_BUILDER_OT_rename_house_room.bl_idname, text="Rename...")
    if not room.orphaned:
        layout.menu(HOME_BUILDER_MT_room_floor.bl_idname)
        layout.prop(room, 'has_ceiling', text="Ceiling")
    layout.separator()
    layout.operator(HOME_BUILDER_OT_room_properties.bl_idname, text="Room Properties",
                    icon='PROPERTIES')
    if not room.orphaned:
        layout.operator("home_builder.open_room_view", text="Open Room View")
        layout.operator("home_builder.walk_through", text="Walk Through")
        layout.separator()
        if room.floor_obj is not None:
            op = layout.operator("home_builder_walls.draw_floor_cutter",
                                 text="Draw Floor Cutter", icon='MOD_BOOLEAN')
            op.surface, op.target = 'FLOOR', room.floor_obj.name
        if room.ceiling_obj is not None:
            op = layout.operator("home_builder_walls.draw_floor_cutter",
                                 text="Draw Ceiling Cutter", icon='MOD_BOOLEAN')
            op.surface, op.target = 'CEILING', room.ceiling_obj.name
    layout.operator("home_builder.select_room", text="Select Marker")
    if room.orphaned:
        layout.operator(HOME_BUILDER_OT_remove_room.bl_idname, icon='TRASH')
    return True


class HOME_BUILDER_MT_room_type(bpy.types.Menu):
    bl_idname = "HOME_BUILDER_MT_room_type"
    bl_label = "Room Type"

    def draw(self, context):
        _level, room = _active(context)
        if room is not None:
            self.layout.props_enum(room, 'room_type')


class HOME_BUILDER_MT_room_floor(bpy.types.Menu):
    bl_idname = "HOME_BUILDER_MT_room_floor"
    bl_label = "Floor"

    def draw(self, context):
        _level, room = _active(context)
        if room is None:
            return
        layout = self.layout
        layout.prop(room, 'floor_auto', text="Use House Default")
        layout.separator()
        layout.props_enum(room, 'floor_finish')


class HOME_BUILDER_OT_rename_house_room(bpy.types.Operator):
    """Give the room a name of your own"""
    bl_idname = "home_builder.rename_house_room"
    bl_label = "Rename Room"
    bl_options = {'UNDO', 'INTERNAL'}

    name: bpy.props.StringProperty(name="Name", options={'SKIP_SAVE'})  # type: ignore

    def invoke(self, context, event):
        _level, room = _active(context)
        if room is None:
            return {'CANCELLED'}
        self.name = room.name
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        self.layout.prop(self, 'name', text="")

    def execute(self, context):
        _level, room = _active(context)
        name = self.name.strip()
        if room is None or not name:
            return {'CANCELLED'}
        room.name = name
        return {'FINISHED'}


class HOME_BUILDER_OT_room_properties(bpy.types.Operator):
    """Open the room on the HOUSE tab's Rooms page"""
    bl_idname = "home_builder.room_properties"
    bl_label = "Room Properties"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        level, room = _active(context)
        if room is None:
            return {'CANCELLED'}
        scene = hb_house.house_scene_of(context.scene)
        open_room(scene, scene.hb_house.active_level_index, level.active_room_index)
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_room(bpy.types.Operator):
    """Remove this room: its walls no longer enclose it"""
    bl_idname = "home_builder.remove_room"
    bl_label = "Remove Room"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        _level, room = _active(context)
        return room is not None and room.orphaned

    def execute(self, context):
        global _picked
        from . import hb_rooms
        level, room = _active(context)
        scene = hb_house.house_scene_of(context.scene)
        uid = level.uid
        if room.marker is not None:
            bpy.data.objects.remove(room.marker, do_unlink=True)
        _picked = None
        # A room whose marker is gone is forgotten on the rebuild
        hb_rooms.rebuild_level(scene, hb_house.get_level(uid))
        _tag_redraw()
        return {'FINISHED'}


classes = (
    HOME_BUILDER_MT_room_type,
    HOME_BUILDER_MT_room_floor,
    HOME_BUILDER_OT_rename_house_room,
    HOME_BUILDER_OT_room_properties,
    HOME_BUILDER_OT_remove_room,
)


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
    for cls in classes:
        bpy.utils.register_class(cls)
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
