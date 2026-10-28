"""The Furnish tool: bath fixtures, lights and furniture placed straight
into a room, without going through a cabinet library.

What it places comes from the Furnish catalog on its TOOL page, and how
it places it from the item's placement:
- WALL: against a wall like a window is placed in one (gaps, typed
  offsets, W for width, placing on until Esc), its back to the face of
  the wall the cursor is on;
- WALL_MOUNT: the same, up the wall at its mounting height (a sconce);
- CEILING: hung from the ceiling over the point under the cursor, in
  whatever room is there;
- FLOOR: standing on the floor at the point under the cursor, R turning
  it a quarter turn (a table, a rug).
Everything comes in built: a fixture modeled, a light with its lights.
"""

import math

import bpy
from bpy_extras import view3d_utils
from mathutils import Matrix, Vector

from .. import hb_house, hb_types
from ..product_libraries.common import appliance_geo
from ..product_libraries.interiors import catalog
from . import doors_windows, tool_session


def _is_light(obj):
    from ..product_libraries.interiors import lighting_geo
    return bool(obj.get(lighting_geo.FIXTURE_KEY))


def _is_furnishing(obj):
    return bool(obj.get('IS_FURNISHING'))


def _to_collection(obj, coll):
    """Move an object and everything under it into one collection."""
    for o in [obj] + list(obj.children_recursive):
        for c in list(o.users_collection):
            if c is not coll:
                c.objects.unlink(o)
        if coll not in o.users_collection:
            coll.objects.link(o)


def _room_at(scene, level, x, y):
    from .. import hb_rooms, hb_wall_graph
    for room in level.rooms:
        if room.orphaned:
            continue
        poly = hb_rooms.room_polygon(scene, level, room)
        if poly and hb_wall_graph.point_in_polygon((x, y), poly):
            return room
    return None


def finish(context, cage_obj):
    """A placed item comes in built: a fixture modeled, a light with its
    lights (in its level's Lights, and its room's), furniture made."""
    if _is_light(cage_obj):
        from ..product_libraries.interiors import lighting_geo
        lighting_geo.build(cage_obj)
        scene = hb_house.house_scene_of(context.scene)
        level = hb_house.active_level(context) if scene is not None else None
        if level is not None:
            hb_house.ensure_level_collections(scene, level)
            _to_collection(cage_obj, hb_house.level_subcollection(level, 'Lights'))
            cage_obj[hb_house.LEVEL_KEY] = level.uid
            # Its middle, from its basis: a cage made a moment ago has a
            # stale matrix_world
            m = cage_obj.matrix_basis if cage_obj.parent is None else \
                cage_obj.parent.matrix_world @ cage_obj.matrix_basis
            p = m @ _centre_local(cage_obj)
            room = _room_at(scene, level, p.x, p.y)
            if room is not None:
                cage_obj['HB_ROOM'] = room.uid
        return
    if _is_furnishing(cage_obj):
        from ..product_libraries.interiors import furniture_geo
        furniture_geo.build(cage_obj)
        scene = hb_house.house_scene_of(context.scene)
        level = hb_house.active_level(context) if scene is not None else None
        if level is not None and cage_obj.parent is None:
            # On the floor: in its level's Products (against a wall, it
            # goes with the wall's level as cabinets do)
            hb_house.ensure_level_collections(scene, level)
            _to_collection(cage_obj, hb_house.level_subcollection(level, 'Products'))
            cage_obj[hb_house.LEVEL_KEY] = level.uid
        return
    opts = appliance_geo.defaults_for(cage_obj)
    opts['model_style'] = 'MODELED'
    appliance_geo.set_opts(cage_obj, opts)
    appliance_geo.build_geometry(cage_obj)


def _model(cage_obj):
    finish(bpy.context, cage_obj)


def face_wall(cage_obj, wall_obj, x, far_side):
    """Stand a fixture against one face of a wall: its left end at x
    along the wall, its back to the reference face (y = 0), or turned
    round onto the thickness face when `far_side`."""
    cage = hb_types.GeoNodeCage(cage_obj)
    width = cage.get_input('Dim X')
    t = hb_types.GeoNodeWall(wall_obj).get_input('Thickness')
    cage_obj.parent = wall_obj
    if far_side:
        cage_obj.location = (x + width, t, cage_obj.location.z)
        cage_obj.rotation_euler = (0.0, 0.0, math.pi)
    else:
        cage_obj.location = (x, 0.0, cage_obj.location.z)
        cage_obj.rotation_euler = (0.0, 0.0, 0.0)


def _centre_local(cage_obj):
    """The middle of a cage's footprint in its own space."""
    c = hb_types.GeoNodeCage(cage_obj)
    w, d = c.get_input('Dim X'), c.get_input('Dim Y')
    mirrored = bool(c.get_input('Mirror Y')) if c.has_input('Mirror Y') else False
    return Vector((w / 2.0, -d / 2.0 if mirrored else d / 2.0, 0.0))


def _ceiling_z_here(x, y):
    """The ceiling over (x, y) outside a house: the underside of a
    ceiling there, else the top of the walls, else the room's Ceiling
    Height."""
    scene = bpy.context.scene
    up = Vector((0.0, 0.0, 1.0))
    best = None
    for obj in scene.objects:
        if not obj.get('IS_CEILING_BP') or obj.type != 'MESH':
            continue
        inv = obj.matrix_world.inverted()
        hit, loc, _n, _i = obj.ray_cast(inv @ Vector((x, y, 0.05)), inv.to_3x3() @ up, distance=100.0)
        if hit:
            z = (obj.matrix_world @ loc).z
            best = z if best is None else min(best, z)
    if best is not None:
        return best
    tops = []
    for obj in scene.objects:
        if obj.get('IS_WALL_BP'):
            w = hb_types.GeoNodeWall(obj)
            try:
                tops.append(obj.matrix_world.translation.z + w.get_input('Height'))
            except Exception:
                pass
    if tops:
        return max(tops)
    return scene.home_builder.ceiling_height


def stand_at(cage_obj, level, x, y, turn=0.0, hang=False):
    """Stand a free item with its footprint's middle at (x, y) on the
    level's floor - or hang it from the ceiling there - turned by `turn`."""
    from .. import hb_rooms
    c = hb_types.GeoNodeCage(cage_obj)
    h = c.get_input('Dim Z')
    cage_obj.parent = None
    rot = Matrix.Rotation(turn, 3, 'Z')
    off = rot @ _centre_local(cage_obj)
    if hang:
        top = hb_rooms.ceiling_z_at(level, x, y) if level is not None else _ceiling_z_here(x, y)
        z = top - h
    else:
        z = level.elevation if level is not None else 0.0
    cage_obj.location = (x - off.x, y - off.y, z)
    cage_obj.rotation_euler = (0.0, 0.0, turn)


def place_item(context, key, wall_obj=None, x=0.0, far_side=False, point=None, turn=0.0):
    """Place a catalog item without the tool, as a click of it would:
    against a wall (`wall_obj`, `x` along it), or for a ceiling or floor
    item at a plan `point`. Returns the new item's cage object."""
    row = catalog.item(key)
    cls = catalog.item_class(key)
    if cls is None or row is None:
        return None
    item = cls()
    item.create()
    obj = item.obj
    placement = row[3]
    if placement in ('WALL', 'WALL_MOUNT'):
        obj.location.z = getattr(cls, 'mount_height', 0.0) if placement == 'WALL_MOUNT' else 0.0
        face_wall(obj, wall_obj, x, far_side)
    else:
        stand_at(obj, hb_house.active_level(context), point[0], point[1], turn, hang=placement == 'CEILING')
    finish(context, obj)
    return obj


def _placement(context):
    row = catalog.item(context.scene.hb_house.furnish_item)
    return row[3] if row else 'WALL'


class HOME_BUILDER_OT_furnish(doors_windows._PlaceWallObjectBase):
    bl_idname = "home_builder.furnish"
    bl_label = "Furnish"
    bl_description = ("Place a bath fixture, a light or furniture: pick it on the TOOL page. "
                      "Against a wall: arrow keys for offset, W for width. On the floor: R turns it")

    OBJECT_NAME = "Fixture"
    OBJECT_LABEL = "fixture"
    TEXT_KIND = None
    BUILD_GEO = False

    # ---- Against a wall (the window's placement) ----

    def create_placed_object(self, context):
        cls = catalog.item_class(context.scene.hb_house.furnish_item) \
            or catalog.item_class(catalog.ITEMS[0][0])
        item = cls()
        item.create()
        self.placed_obj, self.swing_obj = item, None
        self.register_placement_object(item.obj)
        self.create_placement_dimensions()
        self._symbol_key = None
        if not hasattr(self, 'turn'):
            self.turn = 0.0
        self._preview_size = None
        _preview(item.obj)

    def _preview_follows(self):
        """Furniture's preview model, rebuilt when its size is typed."""
        obj = self.placed_obj.obj if self.placed_obj else None
        if obj is None or not _is_furnishing(obj):
            return
        c = hb_types.GeoNodeCage(obj)
        size = tuple(round(c.get_input(n), 5) for n in ('Dim X', 'Dim Y', 'Dim Z'))
        if size != getattr(self, '_preview_size', None):
            self._preview_size = size
            _preview(obj)

    def set_position_free(self):
        """Away from the walls, furniture stands on the floor under the
        cursor, turned as R has turned it."""
        if not (self.placed_obj and self.hit_location and _is_furnishing(self.placed_obj.obj)):
            return super().set_position_free()
        level = hb_house.active_level(bpy.context)
        p = Vector(self.hit_location)
        stand_at(self.placed_obj.obj, level, p.x, p.y, self.turn)
        self.hide_placement_dimensions()

    def _drop_free(self, context):
        """A click away from the walls: the piece stays on the floor there."""
        obj = self.placed_obj.obj
        if obj in self.placement_objects:
            self.placement_objects.remove(obj)
        self.delete_placement_dimensions()
        finish(context, obj)
        self.placed_count += 1
        if self.continuous:
            self.start_next_object(context)
            self.update_header(context)
            return {'RUNNING_MODAL'}
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')
        return {'FINISHED'}

    @tool_session.session_modal
    def _wall_modal(self, context, event):
        """The window's wall placement - with, for furniture, the floor
        away from the walls (R turns it there), and its model shown. In
        the session's wrapper, so a click on the HUD (picking another
        item) and a stop are seen before a click here drops a piece."""
        obj = self.placed_obj.obj if self.placed_obj else None
        free_ok = obj is not None and _is_furnishing(obj) and self.mode == 'WALL'
        if event.type == 'R' and free_ok:
            # Ours, not Blender's rotate; it turns the piece off the walls
            if event.value == 'PRESS' and not self.selected_wall:
                self.turn = (self.turn + math.pi / 2.0) % (2.0 * math.pi)
                self.set_position_free()
            return {'RUNNING_MODAL'}
        if (free_ok and event.type == 'LEFTMOUSE' and event.value == 'PRESS'
                and not self.selected_wall and obj.parent is None and self.hit_location):
            return self._drop_free(context)
        # Its model is out of the way of the cursor's ray while it is
        # snapped, as the cage is
        parts = [c.name for c in obj.children if c.visible_get()] if obj is not None else []
        for name in parts:
            bpy.data.objects[name].hide_set(True)
        # The base's own modal, without its session wrapper: this one's is it
        result = doors_windows._PlaceWallObjectBase.modal.__wrapped__(self, context, event)
        for name in parts:
            part = bpy.data.objects.get(name)
            if part is not None:
                part.hide_set(False)
        if {'RUNNING_MODAL', 'PASS_THROUGH'} & result:
            self._preview_follows()
        return result

    def get_two_point_z_offset(self, context):
        if _placement(context) == 'WALL_MOUNT':
            cls = catalog.item_class(context.scene.hb_house.furnish_item)
            return getattr(cls, 'mount_height', 0.0)
        return 0.0

    def set_position_on_wall(self):
        if not self.placed_obj:
            return
        depth = self.placed_obj.get_input('Dim Y')
        super().set_position_on_wall()
        if not self.selected_wall:
            return
        # The placement keeps the depth the fixture has, not the wall's
        self.placed_obj.set_input('Dim Y', depth)
        wall = self.selected_wall
        t = hb_types.GeoNodeWall(wall).get_input('Thickness')
        local = wall.matrix_world.inverted() @ Vector(self.hit_location)
        face_wall(self.placed_obj.obj, wall, self.placement_x, local.y > t / 2.0)

    def cut_wall(self, wall_obj, cutting_obj):
        # It stands in front of the wall: nothing is cut
        finish(bpy.context, cutting_obj)
        return None

    # ---- Free: on the floor, or from the ceiling ----

    def execute(self, context):
        self.mode = _placement(context)
        if self.mode in ('WALL', 'WALL_MOUNT'):
            return super().execute(context)
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), context.region)
        self.level_uid = hb_house.active_level(context).uid if hb_house.active_level(context) else None
        self.placed_count = 0
        self.turn = 0.0
        self.free_obj = None
        self._new_free(context)
        context.area.header_text_set(
            "Furnish: click to place" + ("   R: turn" if self.mode == 'FLOOR' else "")
            + "   |   Esc / right-click: done")
        tool_session.begin(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _new_free(self, context):
        cls = catalog.item_class(context.scene.hb_house.furnish_item)
        item = cls()
        item.create()
        self.free_obj = item.obj
        self.free_obj.hide_set(True)
        self._shown = False

    def _floor_point(self, context, event):
        level = hb_house.get_level(self.level_uid) if self.level_uid else None
        z = level.elevation if level is not None else 0.0
        rv3d = context.region_data
        if rv3d is None:
            rv3d = next((s.region_3d for s in context.area.spaces if s.type == 'VIEW_3D'), None)
        co = (event.mouse_x - self.region.x, event.mouse_y - self.region.y)
        origin = view3d_utils.region_2d_to_origin_3d(self.region, rv3d, co)
        direction = view3d_utils.region_2d_to_vector_3d(self.region, rv3d, co)
        if abs(direction.z) < 1e-6:
            return None
        t = (z - origin.z) / direction.z
        if t < 0:
            return None
        return origin + direction * t

    def _cleanup_free(self, context):
        obj = getattr(self, 'free_obj', None)
        if obj is not None and obj.name in bpy.data.objects:
            for o in [obj] + list(obj.children_recursive):
                bpy.data.objects.remove(o, do_unlink=True)
        self.free_obj = None
        context.area.header_text_set(None)

    def stop_tool(self, context):
        if getattr(self, 'mode', 'WALL') in ('WALL', 'WALL_MOUNT'):
            return super().stop_tool(context)
        self._cleanup_free(context)
        return {'FINISHED'} if self.placed_count else {'CANCELLED'}

    @tool_session.session_modal
    def _free_modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        level = hb_house.get_level(self.level_uid) if self.level_uid else None
        if event.type == 'R' and self.mode == 'FLOOR':
            # Ours, not Blender's rotate
            if event.value == 'PRESS':
                self.turn = (self.turn + math.pi / 2.0) % (2.0 * math.pi)
                p = self._floor_point(context, event)
                if p is not None and self.free_obj is not None:
                    stand_at(self.free_obj, level, p.x, p.y, self.turn, hang=False)
            return {'RUNNING_MODAL'}
        p = self._floor_point(context, event)
        if p is not None and self.free_obj is not None:
            stand_at(self.free_obj, level, p.x, p.y, self.turn, hang=self.mode == 'CEILING')
            self.free_obj.hide_set(False)
            if not getattr(self, '_shown', False):
                # Its model once it is under the cursor: which way it faces
                self._shown = True
                _preview(self.free_obj)
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if p is None:
                return {'RUNNING_MODAL'}
            obj, self.free_obj = self.free_obj, None
            finish(context, obj)
            self.placed_count += 1
            if tool_session.stays_on(context):
                self._new_free(context)
                return {'RUNNING_MODAL'}
            self._cleanup_free(context)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._cleanup_free(context)
            return {'FINISHED'} if self.placed_count else {'CANCELLED'}
        return {'PASS_THROUGH'}

    def modal(self, context, event):
        if getattr(self, 'mode', 'WALL') in ('WALL', 'WALL_MOUNT'):
            return self._wall_modal(context, event)
        return self._free_modal(context, event)


def _preview(cage_obj):
    """Build a piece of furniture's model on it while it is being placed,
    so which way it faces shows before the click."""
    if _is_furnishing(cage_obj):
        from ..product_libraries.interiors import furniture_geo
        furniture_geo.build(cage_obj)


def _furnish_changed(self, context):
    """Picked from the catalog while placing: place the new one."""
    if tool_session.active_tool() == HOME_BUILDER_OT_furnish.bl_idname:
        tool_session.restart(context)


classes = (
    HOME_BUILDER_OT_furnish,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
