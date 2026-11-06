"""Accessories from the tool strip, and the Drawer page.

One browser for every catalog accessory, cabinets and drawers alike: a
search box and a section dropdown over a single list. With openings or
drawers selected, OK adds the pick to them; with nothing selected it
starts placing -- the opening under the cursor lights up green when the
accessory fits it and red (with the reason) when it does not, and each
click adds one, until Esc.

The catalog is the host application's (accessory_registry); what fits
where is the opening accessory dialog's own rules (ops_cabinet), so the
three ways in agree.

The selection inspector's Drawer page (selected_card) lives here too:
a picked drawer box's construction, slides, commands and the
accessories in its drawer.
"""

import bpy
import gpu
import blf
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ... import accessory_registry
from ...units import meter_to_inch
from . import types_face_frame
from .operators import ops_cabinet

DRAWER_BOX_MENU = 'HOME_BUILDER_MT_face_frame_drawer_box_commands'
TOOL_KEY = 'hb_face_frame_accessories'

# Enum item lists must stay alive at module scope.
_section_items = []


# ---- What an accessory goes on ----------------------------------------------

def target_for(obj):
    """The interior region or opening cage owning ``obj`` (itself
    included), or None."""
    cur = obj
    while cur is not None:
        if (cur.get(types_face_frame.TAG_INTERIOR_REGION)
                or cur.get(types_face_frame.TAG_OPENING_CAGE)):
            return cur
        cur = cur.parent
    return None


def _front_word(front):
    return {'DRAWER_FRONT': "drawer", 'DOOR': "door",
            'PULLOUT': "pull-out", 'TILT_OUT': "tilt-out"}.get(
                front, (front or "this").lower().replace('_', ' '))


def check_fit(target, item):
    """(fits, why) for catalog ``item`` going on ``target`` (an opening
    cage or interior region)."""
    if target is None:
        return False, "Point at an opening or a drawer"
    host = item.get('host')
    if host not in ops_cabinet._valid_accessory_hosts(target):
        opening = ops_cabinet._find_owning_opening(target)
        front = (opening.face_frame_opening.front_type
                 if opening is not None else '')
        return False, "Doesn't go in a %s opening" % _front_word(front)
    region = target.get(types_face_frame.TAG_INTERIOR_REGION)
    if host != ops_cabinet._ACCESSORY_PULLOUT_HOST or region:
        if ops_cabinet._interior_items_target(target) is None:
            return False, "Divided opening: point at one section"
    mw = item.get('min_opening_w')
    ow = ops_cabinet._opening_width_in(target)
    if mw and ow is not None and ow + 1e-6 < mw:
        return False, 'Opening is %g" wide, needs %g"' % (round(ow, 3), mw)
    return True, ""


def _selected_targets(context):
    """Openings and regions the selection stands for, in order, once
    each. Reads the selection from before a tool-strip press."""
    names = None
    try:
        from ...operators import room_palette
        snap = room_palette.selection_before_press()
        if snap is not None:
            names = snap[0]
    except Exception:
        names = None
    objs = ([bpy.data.objects.get(n) for n in names] if names is not None
            else list(context.selected_objects))
    out = []
    for obj in objs:
        t = target_for(obj) if obj is not None else None
        if t is not None and t not in out:
            out.append(t)
    return out


def _valid_hosts(targets):
    if not targets:
        return set(ops_cabinet._ALL_ACCESSORY_HOSTS)
    valid = set()
    for t in targets:
        valid |= ops_cabinet._valid_accessory_hosts(t)
    return valid


# ---- The browser --------------------------------------------------------------

def _targets(op):
    return [o for o in (bpy.data.objects.get(n)
                        for n in op.target_names.split('\n') if n)
            if o is not None]


def _section_enum(self, context):
    _section_items.clear()
    _section_items.append(('ALL', "All Sections", "Every section"))
    valid = _valid_hosts(_targets(self))
    for sec in accessory_registry.sections():
        if any(it.get('host') in valid for it in accessory_registry.all_items()
               if it.get('section') == sec):
            _section_items.append((sec, sec, sec))
    return _section_items


def _populate(op):
    op.matches.clear()
    valid = _valid_hosts(_targets(op))
    tokens = op.filter_text.lower().split()
    section = op.section_filter
    for it in accessory_registry.all_items():
        code = it.get('code')
        if not code or it.get('host') not in valid:
            continue
        name = it.get('name', code)
        sec = it.get('section', '')
        grp = it.get('group', '')
        if section not in ('', 'ALL') and sec != section:
            continue
        if tokens:
            hay = " ".join((name, sec, grp, code)).lower()
            if not all(tok in hay for tok in tokens):
                continue
        row = op.matches.add()
        row.code = code
        row.name = name
        row.section = sec
        row.group = grp
        row.render_kind = ops_cabinet._geometry_kind(it)
        mw = it.get('min_opening_w')
        row.label = name if mw is None else "%s  (min %g\")" % (name, mw)
    op.active_index = min(op.active_index, max(0, len(op.matches) - 1))


def _search_update(self, context):
    _populate(self)


class hb_face_frame_OT_accessory_browser(bpy.types.Operator):
    """Browse every accessory: add the pick to the selected openings and
    drawers, or with nothing selected, click to place it"""
    bl_idname = "hb_face_frame.accessory_browser"
    bl_label = "Accessories"
    bl_options = {'REGISTER', 'UNDO'}

    target_names: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    filter_text: bpy.props.StringProperty(
        name="Search", options={'TEXTEDIT_UPDATE', 'SKIP_SAVE'},
        description="Filter by name, section, group or code",
        update=_search_update)  # type: ignore
    section_filter: bpy.props.EnumProperty(
        name="Section", items=_section_enum, update=_search_update,
        options={'SKIP_SAVE'})  # type: ignore
    matches: bpy.props.CollectionProperty(type=ops_cabinet.AccessorySearchRow)  # type: ignore
    active_index: bpy.props.IntProperty(default=0, options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return accessory_registry.available(*ops_cabinet._ALL_ACCESSORY_HOSTS)

    def _picked(self):
        if not len(self.matches):
            return None, None
        row = self.matches[max(0, min(self.active_index,
                                      len(self.matches) - 1))]
        return row.code, accessory_registry.find(row.code)

    def invoke(self, context, event):
        if not self.target_names:
            self.target_names = "\n".join(
                t.name for t in _selected_targets(context))
        _populate(self)
        n = len(_targets(self))
        return context.window_manager.invoke_props_dialog(
            self, width=560,
            confirm_text=("Add to %d Selected" % n) if n else "Place")

    def check(self, context):
        _populate(self)
        return True

    def draw(self, context):
        layout = self.layout
        targets = _targets(self)
        if targets:
            layout.label(text="Adds to the %d selected opening%s" % (
                len(targets), "" if len(targets) == 1 else "s"), icon='INFO')
        else:
            layout.label(text="Pick one, then click the openings and "
                              "drawers to add it to", icon='INFO')
        head = layout.row(align=True)
        head.prop(self, "filter_text", text="", icon='VIEWZOOM')
        head.prop(self, "section_filter", text="")
        if not len(self.matches):
            layout.label(text="Nothing matches", icon='INFO')
            return
        layout.template_list("HB_UL_face_frame_accessory_search", "",
                             self, "matches", self, "active_index", rows=12)
        code, item = self._picked()
        if item is None:
            return
        box = layout.box()
        box.label(text="%s  (%s)" % (item.get('name', code), code))
        if ops_cabinet._geometry_kind(item):
            box.label(text="Modeled in the cabinet", icon='MESH_GRID')
        else:
            box.label(text="Called out on the drawings; not shown in 3D",
                      icon='DOT')
        mw = item.get('min_opening_w')
        if mw:
            box.label(text="Minimum opening width: %g\"" % mw)
        for t in targets:
            ok, why = check_fit(t, item)
            if not ok:
                box.label(text="%s: %s" % (t.name, why), icon='ERROR')

    def execute(self, context):
        if not len(self.matches):
            _populate(self)         # run without the dialog
        code, item = self._picked()
        if item is None:
            return {'CANCELLED'}
        targets = _targets(self)
        if not targets:
            _start_placing(context, code)
            return {'FINISHED'}
        added, skipped = 0, []
        for t in targets:
            ok, why = check_fit(t, item)
            if not ok:
                skipped.append(why)
                continue
            if ops_cabinet._apply_accessory_choice(
                    self, context, t, code, item, 0.0) == {'FINISHED'}:
                added += 1
        msg = "Added %s to %d" % (item.get('name', code), added)
        if skipped:
            msg += "; %d skipped (%s)" % (len(skipped), skipped[0])
        self.report({'WARNING'} if skipped else {'INFO'}, msg)
        return {'FINISHED'} if added else {'CANCELLED'}


def _start_placing(context, code):
    area = context.area
    if area is None or area.type != 'VIEW_3D':
        area = next((a for a in context.window.screen.areas
                     if a.type == 'VIEW_3D'), None)
    if area is None:
        return
    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    with context.temp_override(area=area, region=region):
        bpy.ops.hb_face_frame.place_accessory('INVOKE_DEFAULT', code=code)


# ---- Placing ----------------------------------------------------------------

_hover = {'target': None, 'ok': False, 'why': "", 'mouse': (0, 0),
          'name': ""}
_handles = []


def _hit(context, event):
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return None
    coord = (event.mouse_region_x, event.mouse_region_y)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    depsgraph = context.evaluated_depsgraph_get()
    # Walls, bay cages and the like are passed through to whatever
    # opening sits behind them.
    for _ in range(16):
        hit, loc, _n, _i, obj, _m = context.scene.ray_cast(
            depsgraph, origin, direction)
        if not hit or obj is None:
            return None
        target = target_for(obj.original)
        if target is not None:
            return target
        origin = loc + direction * 1e-4
    return None


def _box_lines(obj):
    try:
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        corners = [ev.matrix_world @ Vector(c) for c in ev.bound_box]
    except Exception:
        return []
    edges = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7),
             (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))
    return [tuple(corners[i]) for e in edges for i in e]


def _draw_3d():
    target = _hover['target']
    if target is None:
        return
    try:
        lines = _box_lines(target)
    except ReferenceError:
        return
    if not lines:
        return
    color = (0.25, 0.85, 0.4, 1.0) if _hover['ok'] else (0.95, 0.3, 0.3, 1.0)
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": lines})
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    shader.bind()
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    shader.uniform_float("lineWidth", 3.0)
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _draw_2d():
    x, y = _hover['mouse']
    font = 0
    size = 13 * bpy.context.preferences.system.ui_scale
    blf.size(font, size)
    lines = [(_hover['name'], (1, 1, 1, 1))]
    if _hover['target'] is not None:
        if _hover['ok']:
            lines.append(("Click to add", (0.45, 0.95, 0.55, 1)))
        else:
            lines.append((_hover['why'], (1.0, 0.45, 0.45, 1)))
    else:
        lines.append(("Point at an opening or a drawer",
                      (0.8, 0.8, 0.8, 1)))
    lines.append(("Esc or right-click to finish", (0.7, 0.7, 0.7, 1)))
    for i, (text, color) in enumerate(lines):
        blf.position(font, x + 18, y - 18 - i * size * 1.35, 0)
        blf.color(font, *color)
        blf.draw(font, text)


def _remove_handles():
    for space, handle in _handles:
        try:
            space.draw_handler_remove(handle, 'WINDOW')
        except Exception:
            pass
    _handles.clear()
    _hover['target'] = None


class hb_face_frame_OT_place_accessory(bpy.types.Operator):
    """Click openings and drawers to add the accessory to them"""
    bl_idname = "hb_face_frame.place_accessory"
    bl_label = "Place Accessory"
    bl_options = {'REGISTER'}

    code: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        self.item = accessory_registry.find(self.code)
        if self.item is None or context.area is None \
                or context.area.type != 'VIEW_3D':
            return {'CANCELLED'}
        _remove_handles()
        _hover['name'] = "%s  (%s)" % (self.item.get('name', self.code),
                                       self.code)
        _hover['mouse'] = (event.mouse_region_x, event.mouse_region_y)
        _handles.append((bpy.types.SpaceView3D,
                         bpy.types.SpaceView3D.draw_handler_add(
                             _draw_3d, (), 'WINDOW', 'POST_VIEW')))
        _handles.append((bpy.types.SpaceView3D,
                         bpy.types.SpaceView3D.draw_handler_add(
                             _draw_2d, (), 'WINDOW', 'POST_PIXEL')))
        self.added = 0
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _update(self, context, event):
        _hover['mouse'] = (event.mouse_region_x, event.mouse_region_y)
        target = _hit(context, event)
        _hover['target'] = target
        if target is not None:
            _hover['ok'], _hover['why'] = check_fit(target, self.item)
        context.area.tag_redraw()

    def _finish(self, context):
        _remove_handles()
        if context.area is not None:
            context.area.tag_redraw()
        if self.added:
            self.report({'INFO'}, "Added %s to %d" % (
                self.item.get('name', self.code), self.added))
        return {'FINISHED'}

    def modal(self, context, event):
        if context.area is None:
            return self._finish(context)
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._finish(context)
        if event.type == 'MOUSEMOVE':
            self._update(context, event)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self._update(context, event)
            target = _hover['target']
            if target is None:
                return {'RUNNING_MODAL'}
            if not _hover['ok']:
                self.report({'WARNING'}, _hover['why'])
                return {'RUNNING_MODAL'}
            if ops_cabinet._apply_accessory_choice(
                    self, context, target, self.code, self.item,
                    0.0) == {'FINISHED'}:
                self.added += 1
                bpy.ops.ed.undo_push(message="Add Accessory")
            self._update(context, event)
            return {'RUNNING_MODAL'}
        # Orbit, pan and zoom keep working while placing.
        return {'PASS_THROUGH'}


# ---- The Drawer page's commands --------------------------------------------

class hb_face_frame_OT_set_drawer_option(bpy.types.Operator):
    """Set the drawer box construction or slides of every listed opening"""
    bl_idname = "hb_face_frame.set_drawer_option"
    bl_label = "Set Drawer Option"
    bl_options = {'UNDO', 'INTERNAL'}

    kind: bpy.props.EnumProperty(items=(('CONSTRUCTION', "Construction", ""),
                                        ('SLIDES', "Slides", "")))  # type: ignore
    code: bpy.props.StringProperty()  # type: ignore
    opening_names: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        setter = (ops_cabinet._set_opening_construction
                  if self.kind == 'CONSTRUCTION'
                  else ops_cabinet._set_opening_slides)
        done = 0
        for name in self.opening_names.split('\n'):
            opening = bpy.data.objects.get(name)
            if opening is not None:
                setter(opening, self.code)
                done += 1
        return {'FINISHED'} if done else {'CANCELLED'}


class hb_face_frame_OT_remove_accessory_item(bpy.types.Operator):
    """Remove this accessory"""
    bl_idname = "hb_face_frame.remove_accessory_item"
    bl_label = "Remove Accessory"
    bl_options = {'UNDO', 'INTERNAL'}

    target_name: bpy.props.StringProperty()  # type: ignore
    index: bpy.props.IntProperty(default=-1)  # type: ignore

    def execute(self, context):
        target = bpy.data.objects.get(self.target_name)
        props = ops_cabinet._interior_items_target(target)
        if props is None or not 0 <= self.index < len(props.interior_items):
            return {'CANCELLED'}
        if props.interior_items[self.index].kind != 'ACCESSORY':
            return {'CANCELLED'}
        props.interior_items.remove(self.index)
        props.interior_items_index = min(props.interior_items_index,
                                         len(props.interior_items) - 1)
        root = types_face_frame.find_cabinet_root(target)
        if root is not None:
            types_face_frame.recalculate_face_frame_cabinet(root)
        return {'FINISHED'}


def is_drawer_box(obj):
    from ...operators import generic_page
    return obj is not None and generic_page.menu_id(obj) == DRAWER_BOX_MENU


def picked_drawer_boxes(context, part_obj):
    """The drawer boxes the page acts on: every selected one, the active
    first."""
    boxes = [part_obj]
    for obj in context.selected_objects:
        if obj not in boxes and is_drawer_box(obj):
            boxes.append(obj)
    return boxes


def _option_pick(kind, title, options, label_fn, openings):
    names = "\n".join(o.name for o in openings)
    prop = ('drawer_box_construction' if kind == 'CONSTRUCTION'
            else 'drawer_slides')
    values = {getattr(o.face_frame_opening, prop, '') for o in openings}
    if len(values) > 1:
        current = "Mixed"
    else:
        value = next(iter(values), '')
        current = (label_fn(value) if value
                   and value != ops_cabinet.DRAWER_BOX_CONSTRUCTION_DEFAULT
                   else "Project Default")

    def entries(_context):
        out = [("Project Default", 'hb_face_frame.set_drawer_option',
                 {'kind': kind, 'code': ops_cabinet.DRAWER_BOX_CONSTRUCTION_DEFAULT,
                  'opening_names': names})]
        out += [(name, 'hb_face_frame.set_drawer_option',
                 {'kind': kind, 'code': code, 'opening_names': names})
                for code, name in options]
        return out
    return ('pick', ("%s: %s" % (title, current), entries))


def drawer_blocks(context, part_obj):
    """The Drawer page under the style: size, construction and slides,
    the drawer commands, and what is in the drawer."""
    from ...operators import generic_page
    boxes = picked_drawer_boxes(context, part_obj)
    openings = []
    for box in boxes:
        opening = ops_cabinet._find_owning_opening(box)
        if opening is not None and opening not in openings:
            openings.append(opening)
    out = []
    if len(boxes) == 1:
        size = generic_page._size_text(context, part_obj)
        if size:
            out.append(('value', ("Size (W x D x H)", size)))
    if openings:
        options = ops_cabinet.drawer_box_construction_options()
        if options:
            out.append(_option_pick(
                'CONSTRUCTION', "Construction", options,
                ops_cabinet.drawer_box_construction_label, openings))
        options = ops_cabinet.drawer_slides_options()
        if options:
            out.append(_option_pick(
                'SLIDES', "Slides", options,
                ops_cabinet.drawer_slides_label, openings))
    if len(boxes) == 1:
        out.append(('gap', None))
        out.append(('actions', (
            ("Drawer Interior", 'hb_face_frame.drawer_interior', None, None),
            ("Open / Close", 'hb_face_frame.toggle_front_open', None, None))))
        out.append(('actions', (
            ("Box Size", 'hb_face_frame.drawer_box_prompts', None, None),
            ("Rollout Above", 'hb_face_frame.rollout_above_drawer_prompts',
             None, None))))

    out.append(('gap', None))
    out.append(('label', "Accessories"))
    rows = 0
    for opening in openings:
        props = ops_cabinet._interior_items_target(opening)
        if props is None:
            continue
        for index, item in enumerate(props.interior_items):
            if item.kind != 'ACCESSORY':
                continue
            text = item.accessory_label or item.accessory_code
            if len(openings) > 1:
                text = "%s  (%s)" % (text, opening.name)
            out.append(('list_row', {
                'key': 'acc:%s:%d' % (opening.name, index),
                'text': text,
                'summary': item.accessory_code,
                'remove': ('hb_face_frame.remove_accessory_item',
                           {'target_name': opening.name, 'index': index}),
                'remove_tip': "Remove Accessory",
                'confirm': False,
            }))
            rows += 1
    if not rows:
        out.append(('note', "None in %s." % (
            "this drawer" if len(openings) <= 1 else "these drawers")))
    if accessory_registry.available(*ops_cabinet._ALL_ACCESSORY_HOSTS):
        label = ("Add Accessory" if len(openings) <= 1
                 else "Add Accessory to %d Drawers" % len(openings))
        out.append(('actions', ((label, 'hb_face_frame.accessory_browser',
                                 {'target_names': "\n".join(
                                     o.name for o in openings)}, None),)))
    return out


# ---- Registration -----------------------------------------------------------

classes = (
    hb_face_frame_OT_accessory_browser,
    hb_face_frame_OT_place_accessory,
    hb_face_frame_OT_set_drawer_option,
    hb_face_frame_OT_remove_accessory_item,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    try:
        from ...operators import room_palette
        from ...hb_icons import icon_glyph
        glyph = icon_glyph('cab_accessories', room_palette._g_furnish,
                           size=16)
        room_palette.register_tool(
            TOOL_KEY, "Accessories", glyph,
            hb_face_frame_OT_accessory_browser.bl_idname, group=2,
            order=1000)
    except Exception as ex:
        print("Home Builder: no Accessories tool: %s" % ex)


def unregister():
    _remove_handles()
    try:
        from ...operators import room_palette
        room_palette.unregister_tool(TOOL_KEY)
    except Exception:
        pass
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
