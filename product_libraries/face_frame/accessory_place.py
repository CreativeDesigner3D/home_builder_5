"""Accessories in the viewport panel, and the Drawer page.

The Options tab's Accessories section browses every catalog accessory,
cabinets and drawers alike: a search field, the catalog's sections, a
section's items. With openings or drawers selected, clicking one adds
it to them; with nothing selected it starts placing -- the opening
under the cursor lights up green when the accessory fits it and red
(with the reason) when it does not, and each click adds one, until Esc.

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

# ---- What an accessory goes on ----------------------------------------------

def target_for(obj):
    """The interior region or opening cage owning ``obj`` (itself
    included), or None. On a frameless cabinet: the drawer opening, or
    the door / open opening (or division section) that keeps catalog
    accessories."""
    cur = obj
    while cur is not None:
        if (cur.get(types_face_frame.TAG_INTERIOR_REGION)
                or cur.get(types_face_frame.TAG_OPENING_CAGE)):
            return cur
        cur = cur.parent
    if obj is None:
        return None
    fl = _frameless_items()
    if fl is None:
        return None
    drawer = fl.drawer_opening_for(obj)
    if drawer is not None:
        return drawer
    return fl.accessory_host(obj)


# ---- Frameless targets --------------------------------------------------------
# Frameless openings keep catalog accessories on the opening cage (drawers
# and pullouts on the drawer opening, the rest on the door / open opening
# or division section), as the frameless right-click menus add them. The
# panel browser and placing go through the same functions.

_FRAMELESS_DRAWER_HOST = 'drawer_accessory'


def _frameless_items():
    try:
        from ..frameless import interior_items
    except Exception:
        return None
    return interior_items


def _is_frameless(target):
    return bool(target is not None and (
        target.get('IS_FRAMELESS_OPENING_CAGE')
        or target.get('IS_FRAMELESS_INTERIOR_SECTION')
        or target.get('IS_FRAMELESS_BAY_CAGE')))


def _is_frameless_drawer(target):
    fl = _frameless_items()
    return fl is not None and fl.drawer_opening_for(target) is target


def _target_hosts(target):
    """Catalog host keys ``target`` takes."""
    if _is_frameless(target):
        if _is_frameless_drawer(target):
            return {_FRAMELESS_DRAWER_HOST}
        return set(_frameless_items().accessory_hosts_for(target))
    return ops_cabinet._valid_accessory_hosts(target)


def _check_fit_frameless(target, item):
    host = item.get('host')
    if host not in _target_hosts(target):
        return False, ("Doesn't go in a drawer"
                       if _is_frameless_drawer(target)
                       else "Doesn't go in this opening")
    mw = item.get('min_opening_w')
    if mw:
        from ..frameless import solver_frameless
        ow = meter_to_inch(solver_frameless.cage_dims(target)[0])
        if ow + 1e-6 < mw:
            return False, 'Opening is %g" wide, needs %g"' % (
                round(ow, 3), mw)
    return True, ""


def apply_to_target(op, context, target, code, item):
    """Add catalog accessory ``code`` to ``target``; {'FINISHED'} when
    it went on."""
    if not _is_frameless(target):
        return ops_cabinet._apply_accessory_choice(
            op, context, target, code, item, 0.0)
    fl = _frameless_items()
    if _is_frameless_drawer(target):
        if fl.add_drawer_accessory(target, code) is None:
            return {'CANCELLED'}
        from ... import hb_utils
        hb_utils.run_calc_fix(context, target)
        return {'FINISHED'}
    if fl.add_opening_accessory(target, code) is None:
        return {'CANCELLED'}
    return {'FINISHED'}


def _front_word(front):
    return {'DRAWER_FRONT': "drawer", 'DOOR': "door",
            'PULLOUT': "pull-out", 'TILT_OUT': "tilt-out"}.get(
                front, (front or "this").lower().replace('_', ' '))


def check_fit(target, item):
    """(fits, why) for catalog ``item`` going on ``target`` (an opening
    cage or interior region)."""
    if target is None:
        return False, "Point at an opening or a drawer"
    if _is_frameless(target):
        return _check_fit_frameless(target, item)
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
        valid |= _target_hosts(t)
    return valid


# ---- Browsing, in the viewport panel --------------------------------------
# The Options tab's Accessories section and the Drawer page's Add
# Accessory fold lay the catalog out with this: a search field, the
# catalog's sections as rows, a section's items under it. The search and
# the open section are the window manager's, so both places agree.

def _go_section(name):
    def go():
        bpy.context.window_manager.hb_accessory_section = name
    return go


def _clear_search():
    bpy.context.window_manager.hb_accessory_search = ""


def _item_row(key, it, targets, names):
    code = it.get('code')
    mw = it.get('min_opening_w')
    summary = code if not mw else '%s  %g"' % (code, mw)
    dim = bool(targets) and not any(check_fit(t, it)[0] for t in targets)
    return ('list_row', {
        'key': '%s:item:%s' % (key, code),
        'text': it.get('name', code),
        'summary': summary,
        'dim': dim,
        'click': ('hb_face_frame.apply_accessory',
                  {'code': code, 'target_names': names}),
    })


def browse_blocks(context, key, targets=None):
    """The catalog as panel blocks. ``targets`` are the openings a click
    adds to (the selection's when not given); with none, a click starts
    placing."""
    from ...operators import options_panel
    wm = context.window_manager
    if targets is None:
        targets = _selected_targets(context)
    names = "\n".join(t.name for t in targets)
    valid = _valid_hosts(targets)
    items = [it for it in accessory_registry.all_items()
             if it.get('code') and it.get('host') in valid]
    out = []
    if not accessory_registry.available(*ops_cabinet._ALL_ACCESSORY_HOSTS):
        return [('note', "No accessory catalog is loaded.")]
    if targets:
        out.append(('hint', "Click one to add it to the %d selected." %
                    len(targets)))
    else:
        out.append(('hint', "Click one, then click where it goes."))
    out.extend(options_panel.field_blocks(
        context, (('text', 'hb_accessory_search', "Search"),), wm))
    tokens = wm.hb_accessory_search.lower().split()
    if tokens:
        found = [it for it in items if all(
            tok in " ".join((it.get('name', ''), it.get('section', ''),
                             it.get('group', ''), it.get('code', ''))).lower()
            for tok in tokens)]
        out.append(('list_row', {'key': key + ':clear',
                                 'text': "\u2039  Clear Search",
                                 'summary': "%d found" % len(found),
                                 'click': _clear_search}))
        for it in found[:60]:
            out.append(_item_row(key, it, targets, names))
        if len(found) > 60:
            out.append(('note', "Showing 60: narrow the search."))
        if not found:
            out.append(('note', "Nothing matches."))
        return out
    sections = [s for s in accessory_registry.sections()
                if any(it.get('section') == s for it in items)]
    section = wm.hb_accessory_section
    if section not in sections and len(sections) == 1:
        section = sections[0]
    if section in sections:
        if len(sections) > 1:
            out.append(('list_row', {'key': key + ':back',
                                     'text': "\u2039  All Sections",
                                     'summary': section,
                                     'click': _go_section("")}))
        # Each group once, under its heading, in catalog order.
        groups = {}
        for it in items:
            if it.get('section') == section:
                groups.setdefault(it.get('group') or "", []).append(it)
        for group, members in groups.items():
            if group and len(groups) > 1:
                out.append(('label', group))
            out.extend(_item_row(key, it, targets, names) for it in members)
        return out
    for sec in sections:
        count = sum(1 for it in items if it.get('section') == sec)
        out.append(('list_row', {'key': '%s:sec:%s' % (key, sec),
                                 'text': sec, 'summary': str(count),
                                 'click': _go_section(sec)}))
    if not sections:
        out.append(('note', "Nothing in the catalog fits the selection."))
    return out


class hb_face_frame_OT_apply_accessory(bpy.types.Operator):
    """Add this accessory to the selected openings and drawers, or with
    nothing selected, click openings to place it"""
    bl_idname = "hb_face_frame.apply_accessory"
    bl_label = "Add Accessory"
    bl_options = {'REGISTER', 'UNDO'}

    code: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    target_names: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        item = accessory_registry.find(self.code)
        if item is None:
            return {'CANCELLED'}
        targets = [o for o in (bpy.data.objects.get(n)
                               for n in self.target_names.split('\n') if n)
                   if o is not None]
        if not targets:
            _start_placing(context, self.code)
            return {'CANCELLED'}     # each placed one is its own undo step
        added, skipped = 0, []
        for t in targets:
            ok, why = check_fit(t, item)
            if not ok:
                skipped.append(why)
                continue
            if apply_to_target(
                    self, context, t, self.code, item) == {'FINISHED'}:
                added += 1
        msg = "Added %s to %d" % (item.get('name', self.code), added)
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
            if apply_to_target(
                    self, context, target, self.code,
                    self.item) == {'FINISHED'}:
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
        open_ = _add_open[0]
        out.append(('section', (label, 'hb_drawer_add_accessory', open_,
                                _toggle_add)))
        if open_:
            out.extend(('indent', b) for b in
                       browse_blocks(context, 'drawer', openings))
    return out


# The Drawer page's Add Accessory fold, open or not.
_add_open = [False]


def _toggle_add():
    _add_open[0] = not _add_open[0]


# ---- Registration -----------------------------------------------------------

classes = (
    hb_face_frame_OT_apply_accessory,
    hb_face_frame_OT_place_accessory,
    hb_face_frame_OT_set_drawer_option,
    hb_face_frame_OT_remove_accessory_item,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.types.WindowManager
    wm.hb_accessory_search = bpy.props.StringProperty(
        name="Search", description="Find accessories by name, section, "
        "group or code")
    wm.hb_accessory_section = bpy.props.StringProperty(
        name="Section", description="The catalog section being browsed")


def unregister():
    _remove_handles()
    for name in ('hb_accessory_search', 'hb_accessory_section'):
        if hasattr(bpy.types.WindowManager, name):
            delattr(bpy.types.WindowManager, name)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
