"""Place Beam, Place Post, and editing a placed member (hb_members)."""

import math

import bpy
from mathutils import Vector

from .. import hb_house, hb_members, hb_snap, units
from . import tool_session

SNAP_RADIUS = 0.15          # m: how close the cursor must be to snap to a point
FACE_SNAP = 0.12            # m: to a wall face
SQUARE_WITHIN = math.radians(5.0)


def _snap_points(scene, level):
    """Points a member end snaps to: wall corners, post centres, beam ends."""
    from . import walls
    pts = []
    for obj in scene.objects:
        if obj.get('IS_WALL_BP') and hb_house.level_of(obj) == level.uid:
            pts += [Vector((p.x, p.y)) for _e, _f, p in walls.wall_plan_corners(obj)]
    for m in hb_members.members_of(scene, level):
        if m.get('MEMBER_KIND') == 'POST':
            pts.append(m.location.to_2d())
        else:
            mw = m.matrix_world
            pts += [(mw @ Vector((0.0, 0.0, 0.0))).to_2d(),
                    (mw @ Vector((float(m['MEMBER_LENGTH']), 0.0, 0.0))).to_2d()]
    return pts


def _wall_faces(scene, level):
    """Each wall's two long faces on a level as (start, end) plan points."""
    from . import walls
    out = []
    _objs, segs = walls.level_wall_segs(scene, level.uid)
    for seg in segs:
        if seg.thickness <= 0.0:
            continue
        for w in (0.0, seg.thickness):
            a = Vector(seg.face_point(w))
            out.append((a, a + Vector(seg.dir) * seg.length))
    return out


def snap_plan_point(scene, level, p, start=None):
    """The point a click at plan point p means: a wall corner, post or
    beam end close by, else the nearest wall face close by, else the grid;
    square to the axes from `start` when nearly so. (point, what)."""
    p = Vector((p[0], p[1]))
    best = None
    for q in _snap_points(scene, level):
        d = (q - p).length
        if d < SNAP_RADIUS and (best is None or d < best[0]):
            best = (d, q)
    if best is not None:
        return best[1], "point"
    for a, b in _wall_faces(scene, level):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
        q = a + ab * t
        d = (q - p).length
        if d < FACE_SNAP and (best is None or d < best[0]):
            best = (d, q)
    if best is not None:
        q = best[1]
        if start is not None:
            # Along the face, square to the start when nearly so
            v = q - start
            ang = math.atan2(v.y, v.x)
            for k in range(4):
                axis = k * math.pi / 2
                if abs(math.atan2(math.sin(ang - axis), math.cos(ang - axis))) < SQUARE_WITHIN:
                    d = Vector((math.cos(axis), math.sin(axis)))
                    hit = start + d * v.dot(d)
                    if (hit - q).length < FACE_SNAP * 2:
                        q = hit
                    break
        return q, "wall"
    q = Vector((hb_snap.snap_value_to_grid(p.x), hb_snap.snap_value_to_grid(p.y)))
    if start is not None:
        v = q - start
        ang = math.atan2(v.y, v.x)
        for k in range(4):
            axis = k * math.pi / 2
            if abs(math.atan2(math.sin(ang - axis), math.cos(ang - axis))) < SQUARE_WITHIN:
                d = Vector((math.cos(axis), math.sin(axis)))
                q = start + d * v.dot(d)
                break
    return q, "grid"


def set_beam_ends(obj, level, a, b):
    """Put a beam between plan points a and b at its position's height."""
    v = Vector((b[0] - a[0], b[1] - a[1]))
    length = max(v.length, 0.01)
    obj['MEMBER_LENGTH'] = length
    obj.location = (a[0], a[1], hb_members.beam_top(
        level, a, b, obj.get('MEMBER_POSITION', 'DROPPED'), float(obj['MEMBER_D'])))
    obj.rotation_euler = (0.0, 0.0, math.atan2(v.y, v.x))
    hb_members.rebuild(obj)


class _PlaceMember:
    """What the two placement tools share: the cursor on the level, the
    session, the header."""
    region = None
    mouse_pos = None
    hit_location = None
    hit_object = None
    hit_face_index = None
    hit_grid = False
    view_point = None

    def _cursor(self, context, event):
        self.mouse_pos = Vector((event.mouse_x - self.region.x, event.mouse_y - self.region.y))
        hb_snap.main(self, event.ctrl, context)
        hb_house.constrain_hit_to_level(self, context)
        return self.hit_location

    def stop_tool(self, context):
        self.cleanup(context)
        return {'CANCELLED'}


class HOME_BUILDER_OT_place_beam(bpy.types.Operator, _PlaceMember):
    """Click both ends of a beam: it snaps to wall corners and faces, posts and other beams' ends"""
    bl_idname = "home_builder.place_beam"
    bl_label = "Place Beam"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_house.active_level(context) is not None and context.area is not None \
            and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), context.region)
        self.start = None
        self.beam = None
        self.placed = 0
        self.level_uid = hb_house.active_level(context).uid
        self._header(context, None)
        tool_session.begin(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _level(self):
        return hb_house.get_level(self.level_uid)

    def _header(self, context, length):
        if self.start is None:
            text = "Place Beam: click its first end"
        else:
            text = ("Place Beam: click its other end   "
                    + units.unit_to_string(context.scene.unit_settings, length or 0.0))
        context.area.header_text_set(text + "   |   Esc / right-click: done")

    def cleanup(self, context):
        if self.beam is not None and self.beam.name in bpy.data.objects:
            mesh = self.beam.data
            bpy.data.objects.remove(self.beam, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        self.beam = None
        context.area.header_text_set(None)

    @tool_session.session_modal
    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        level = self._level()
        if level is None:
            self.cleanup(context)
            return {'CANCELLED'}
        if self.beam is not None:
            self.beam.hide_set(True)        # out of the way of the cursor's ray
        hit = self._cursor(context, event)
        if self.beam is not None:
            self.beam.hide_set(False)
        point = None
        if hit is not None:
            point, _what = snap_plan_point(context.scene, level, Vector(hit).to_2d(), self.start)
        if self.start is not None and point is not None:
            if self.beam is None:
                self.beam = hb_members.add_beam(context.scene, level, self.start,
                                                self.start + Vector((0.1, 0.0)))
            set_beam_ends(self.beam, level, self.start, point)
            self._header(context, (point - self.start).length)

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and point is not None:
            if self.start is None:
                self.start = point
                self._header(context, 0.0)
                return {'RUNNING_MODAL'}
            if (point - self.start).length < 0.05 or self.beam is None:
                return {'RUNNING_MODAL'}
            house = context.scene.hb_house
            if house.beam_end_posts:
                hb_members.add_end_posts(context.scene, level, self.beam, house)
            hb_members.refresh_posts(context.scene, level)
            self.placed += 1
            beam, self.beam = self.beam, None
            warn = hb_members.span_warning(beam)
            if warn:
                self.report({'WARNING'}, warn)
            self.start = None
            if tool_session.stays_on(context):
                self._header(context, None)
                return {'RUNNING_MODAL'}
            self.cleanup(context)
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cleanup(context)
            return {'FINISHED'} if self.placed else {'CANCELLED'}
        return {'PASS_THROUGH'} if event.type not in {'LEFTMOUSE'} else {'RUNNING_MODAL'}


class HOME_BUILDER_OT_place_post(bpy.types.Operator, _PlaceMember):
    """Click where a post stands: it runs up to the beam over it, or to the ceiling"""
    bl_idname = "home_builder.place_post"
    bl_label = "Place Post"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return hb_house.active_level(context) is not None and context.area is not None \
            and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        self.region = next((r for r in context.area.regions if r.type == 'WINDOW'), context.region)
        self.placed = 0
        self.level_uid = hb_house.active_level(context).uid
        context.area.header_text_set("Place Post: click where it stands   |   Esc / right-click: done")
        tool_session.begin(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cleanup(self, context):
        context.area.header_text_set(None)

    @tool_session.session_modal
    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}
        level = hb_house.get_level(self.level_uid)
        if level is None:
            self.cleanup(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hit = self._cursor(context, event)
            if hit is None:
                return {'RUNNING_MODAL'}
            point, _what = snap_plan_point(context.scene, level, Vector(hit).to_2d())
            hb_members.add_post(context.scene, level, point)
            self.placed += 1
            if tool_session.stays_on(context):
                return {'RUNNING_MODAL'}
            self.cleanup(context)
            return {'FINISHED'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self.cleanup(context)
            return {'FINISHED'} if self.placed else {'CANCELLED'}
        return {'PASS_THROUGH'}


class HOME_BUILDER_OT_member_prompts(bpy.types.Operator):
    """Change the selected beam's or post's size and material"""
    bl_idname = "home_builder.member_prompts"
    bl_label = "Beam / Post"
    bl_options = {'REGISTER', 'UNDO'}

    material: bpy.props.EnumProperty(name="Material", items=[
        ('LUMBER', "Lumber", ""), ('LVL', "LVL", ""), ('GLULAM', "Glulam", ""),
        ('STEEL', "Steel", "")])  # type: ignore
    width: bpy.props.FloatProperty(name="Width", subtype='DISTANCE', min=0.02, precision=4)  # type: ignore
    depth: bpy.props.FloatProperty(name="Depth", subtype='DISTANCE', min=0.02, precision=4)  # type: ignore
    plies: bpy.props.IntProperty(name="Plies", min=1, max=5)  # type: ignore
    position: bpy.props.EnumProperty(name="Position", items=[
        ('DROPPED', "Dropped", "Hanging below the ceiling"),
        ('FLUSH', "Flush", "Up in the ceiling framing")])  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get(hb_members.MEMBER_KEY)

    def invoke(self, context, event):
        obj = context.active_object
        self.material = obj.get('MEMBER_MATERIAL', 'LUMBER')
        self.width = float(obj['MEMBER_W'])
        self.depth = float(obj['MEMBER_D'])
        self.plies = int(obj.get('MEMBER_PLIES', 1))
        self.position = obj.get('MEMBER_POSITION', 'DROPPED')
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, 'material')
        beam = obj.get('MEMBER_KIND') == 'BEAM'
        if beam and self.material in ('LUMBER', 'LVL'):
            layout.prop(self, 'plies')
        layout.prop(self, 'depth')
        layout.prop(self, 'width')
        if beam:
            layout.prop(self, 'position')
            warn = hb_members.span_warning(obj)
            if warn:
                layout.label(text=warn, icon='ERROR')

    def execute(self, context):
        obj = context.active_object
        level = hb_house.get_level(obj.get(hb_house.LEVEL_KEY, ''))
        obj['MEMBER_MATERIAL'] = self.material
        obj['MEMBER_W'] = self.width
        obj['MEMBER_D'] = self.depth
        obj['MEMBER_PLIES'] = self.plies
        if obj.get('MEMBER_KIND') == 'BEAM' and level is not None:
            obj['MEMBER_POSITION'] = self.position
            m = obj.matrix_world
            a = (m @ Vector((0.0, 0.0, 0.0))).to_2d()
            b = (m @ Vector((float(obj['MEMBER_LENGTH']), 0.0, 0.0))).to_2d()
            set_beam_ends(obj, level, a, b)
        else:
            hb_members.rebuild(obj)
        if level is not None:
            hb_members.refresh_posts(context.scene, level)
        return {'FINISHED'}


class HOME_BUILDER_OT_delete_member(bpy.types.Operator):
    """Delete the selected beams and posts"""
    bl_idname = "home_builder.delete_member"
    bl_label = "Delete"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(o.get(hb_members.MEMBER_KEY) for o in context.selected_objects)

    def execute(self, context):
        levels = set()
        for obj in [o for o in context.selected_objects if o.get(hb_members.MEMBER_KEY)]:
            levels.add(obj.get(hb_house.LEVEL_KEY, ''))
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh is not None and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        for uid in levels:
            level = hb_house.get_level(uid)
            if level is not None:
                hb_members.refresh_posts(context.scene, level)
        return {'FINISHED'}


class HOME_BUILDER_MT_member_commands(bpy.types.Menu):
    bl_label = "Beam / Post"
    bl_idname = hb_members.MENU_ID

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder.member_prompts", text="Size and Material", icon='PREFERENCES')
        layout.separator()
        layout.operator("home_builder.delete_member", text="Delete", icon='X')


classes = (
    HOME_BUILDER_OT_place_beam,
    HOME_BUILDER_OT_place_post,
    HOME_BUILDER_OT_member_prompts,
    HOME_BUILDER_OT_delete_member,
    HOME_BUILDER_MT_member_commands,
)

register, unregister = bpy.utils.register_classes_factory(classes)
