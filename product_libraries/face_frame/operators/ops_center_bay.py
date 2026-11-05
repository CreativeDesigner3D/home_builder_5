"""Center a bay over something: an appliance, or a bay of another
cabinet.

Right-click a bay > Center Over..., then click what it should center
over -- a range, a refrigerator, a sink base's bay. The bays either side
of it are resized so its opening's center lands on that thing's
centerline: the ones on its left take the shift (held at their new
widths), the ones on its right give it back (left free, so the widths
always add up). Match Width in the redo panel also gives the bay the
appliance's or bay's width.

The bay needs a bay on each side to move; an end bay can only be moved
by moving the cabinet.
"""

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

from .... import hb_placement
from .. import types_face_frame

MIN_OPENING = 0.0762        # 3": narrowest bay the shift may leave


def _ray(context, event):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None
    coord = (event.mouse_region_x, event.mouse_region_y)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    return origin, direction


def _raycast(context, event):
    ray = _ray(context, event)
    if ray is None:
        return None
    hit, _loc, _n, _i, obj, _m = context.scene.ray_cast(
        context.evaluated_depsgraph_get(), ray[0], ray[1])
    return obj if hit else None


def _cage_dims(obj):
    from .... import hb_types
    try:
        cage = hb_types.GeoNodeCage(obj)
        return tuple(cage.get_input(k) for k in ('Dim X', 'Dim Y', 'Dim Z'))
    except Exception:
        return None


def _ray_box(origin, direction, dims):
    """Distance along the ray (in the cage's own space) to the box from
    its origin to ``dims``, or None. A dim may be negative: cages grow
    toward -Y."""
    t_near, t_far = -1e30, 1e30
    for k in range(3):
        lo, hi = sorted((0.0, dims[k]))
        o, d = origin[k], direction[k]
        if abs(d) < 1e-12:
            if o < lo or o > hi:
                return None
            continue
        t1, t2 = sorted(((lo - o) / d, (hi - o) / d))
        t_near, t_far = max(t_near, t1), min(t_far, t2)
        if t_near > t_far or t_far < 0.0:
            return None
    return max(t_near, 0.0)


def _pick_cage(context, event, cab_root):
    """The appliance or bay whose cage the cursor is over, nearest first,
    drawn or not. With the appliance models turned off there is nothing
    for the scene's ray to hit but the label, so the cages are tried
    themselves."""
    ray = _ray(context, event)
    if ray is None:
        return None
    best, best_t = None, None
    for obj in context.view_layer.objects:
        if not (obj.get('IS_APPLIANCE')
                or obj.get(types_face_frame.TAG_BAY_CAGE)):
            continue
        if target_for(obj, cab_root) is not obj:
            continue
        dims = _cage_dims(obj)
        if not dims or not all(dims):
            continue
        inv = obj.matrix_world.inverted()
        o = inv @ ray[0]
        d = (inv.to_3x3() @ ray[1])
        t = _ray_box(o, d, dims)
        if t is None:
            continue
        # Compare in world units: the cage's scale can differ.
        t_world = (obj.matrix_world @ (o + d * t) - ray[0]).length
        if best_t is None or t_world < best_t:
            best, best_t = obj, t_world
    return best


def _target_under(context, event, cab_root):
    hit = _raycast(context, event)
    target = target_for(hit, cab_root) if hit is not None else None
    return target if target is not None else _pick_cage(
        context, event, cab_root)


def _cage_width(obj):
    from .... import hb_types
    try:
        return hb_types.GeoNodeCage(obj).get_input('Dim X')
    except Exception:
        return None


def target_for(obj, cab_root):
    """What a click on ``obj`` centers over: the appliance or the bay
    (of another cabinet) it belongs to, or None. Parts of the cabinet
    being edited don't count."""
    cur = obj
    while cur is not None:
        if cur == cab_root:
            return None
        if cur.get('IS_APPLIANCE') and _cage_width(cur):
            return cur
        if cur.get(types_face_frame.TAG_BAY_CAGE):
            return cur
        cur = cur.parent
    return None


def target_span(target):
    """(center, width) of ``target`` in world space: the center point
    and the width it would hand a bay."""
    width = _cage_width(target) or 0.0
    center = target.matrix_world @ Vector((width / 2.0, 0.0, 0.0))
    if target.get(types_face_frame.TAG_BAY_CAGE):
        # A bay hands over its opening's width, not its cage's.
        width = target.face_frame_bay.width or width
    return center, width


def _bays(cab_root):
    return sorted(
        [c for c in cab_root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0))


def center_bay(cab_root, bay_index, center_world, match_width=None):
    """Resize the bays of ``cab_root`` so bay ``bay_index``'s opening is
    centered on ``center_world`` (and ``match_width`` wide, when given).
    Returns None on success, else the reason it can't."""
    cp = cab_root.face_frame_cabinet
    bays = _bays(cab_root)
    if not 0 <= bay_index < len(bays):
        return "No such bay"
    if len(bays) < 3 or bay_index in (0, len(bays) - 1):
        return ("The bay needs a bay on each side to move; move the "
                "cabinet to shift an end bay")
    widths = [b.face_frame_bay.width for b in bays]
    mids = [m.width for m in cp.mid_stile_widths]
    if len(mids) < len(bays) - 1:
        return "The cabinet's stiles are out of step with its bays"
    center = (cab_root.matrix_world.inverted() @ center_world).x
    width = match_width if match_width else widths[bay_index]
    start = (cp.left_stile_width + sum(widths[:bay_index])
             + sum(mids[:bay_index]))
    shift = (center - width / 2.0) - start
    left = list(range(bay_index))
    right = list(range(bay_index + 1, len(bays)))
    # The left bays grow by the shift; the right ones give back the shift
    # and any width the bay itself gained, so the total holds.
    give = shift + (width - widths[bay_index])
    new = list(widths)
    for j in left:
        new[j] = widths[j] + shift / len(left)
    for j in right:
        new[j] = widths[j] - give / len(right)
    new[bay_index] = width
    if min(new) < MIN_OPENING:
        return "That would leave a bay narrower than 3\""
    with types_face_frame.suspend_recalc():
        for j, bay_obj in enumerate(bays):
            bp = bay_obj.face_frame_bay
            if j in right:
                bp.unlock_width = False
            else:
                bp.unlock_width = True
                bp.width = new[j]
    return None


class hb_face_frame_OT_center_bay_over(bpy.types.Operator):
    """Center this bay over an appliance or another cabinet's bay: click
    the one to center over. The bays either side make room"""
    bl_idname = "hb_face_frame.center_bay_over"
    bl_label = "Center Bay Over"
    bl_options = {'REGISTER', 'UNDO'}

    bay_index: bpy.props.IntProperty(options={'HIDDEN'})  # type: ignore
    cabinet_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    match_width: bpy.props.BoolProperty(
        name="Match Width",
        description="Also give the bay the width of what it centers over",
        default=False,
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None
                and types_face_frame.find_cabinet_root(obj) is not None)

    def invoke(self, context, event):
        bay = context.active_object
        cab = types_face_frame.find_cabinet_root(bay)
        if cab is None or not bay.get(types_face_frame.TAG_BAY_CAGE):
            self.report({'WARNING'}, "Right-click a bay to center it")
            return {'CANCELLED'}
        self.cabinet_name = cab.name
        self.bay_index = bay.get('hb_bay_index', 0)
        self.target_name = ""
        self._hover = None
        context.window.cursor_set('EYEDROPPER')
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _header(self, context):
        what = (" -- " + self._hover.name) if self._hover is not None else ""
        hb_placement.draw_header_text(
            context, "Center Bay Over: click an appliance or a cabinet's "
            "bay%s   Esc: cancel" % what)

    def _end(self, context):
        context.window.cursor_set('DEFAULT')
        hb_placement.clear_header_text(context)

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        cab = bpy.data.objects.get(self.cabinet_name)
        if cab is None:
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            self._hover = _target_under(context, event, cab)
            self._header(context)
            return {'RUNNING_MODAL'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            target = _target_under(context, event, cab)
            if target is None:
                return {'RUNNING_MODAL'}
            self._end(context)
            self.target_name = target.name
            return self.execute(context)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        cab = bpy.data.objects.get(self.cabinet_name)
        target = bpy.data.objects.get(self.target_name)
        if cab is None or target is None:
            return {'CANCELLED'}
        center, width = target_span(target)
        problem = center_bay(cab, self.bay_index, center,
                             width if self.match_width else None)
        if problem:
            self.report({'WARNING'}, problem)
            return {'CANCELLED'}
        self.report({'INFO'}, "Bay centered over %s" % target.name)
        return {'FINISHED'}


classes = (hb_face_frame_OT_center_bay_over,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
