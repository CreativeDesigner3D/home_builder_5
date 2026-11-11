"""The Drawer page's picture: a drawer's inside, laid out from above.

Picking a drawer box gave its size, its construction and a list of the
accessories in it; where each one sat, and the way to move it, was in a
dialog. This draws the box instead -- seen from above, its front at the
bottom -- with every modeled accessory where it is: dividers as bars,
silverware dividers, knife blocks and the other inserts as blocks
carrying their code.

Click an accessory to pick it; its settings show under the picture.
Drag a block to place it (From Left / From Front), or a single divider
to move it. Under the picture are the things most often added: a
divider, a silverware divider, a knife block, a spice insert -- one
click each, or a short list where the catalog has several -- and a
roll-out above the drawer.

The data is the drawer's as it always was (the opening's interior
items, each accessory with its render hint), so saved files, pricing
and the drawings do not change. The picture reads the parts the cabinet
built, so it can never show a layout the drawer does not have.
"""

import math

import bpy
from mathutils import Vector

from ... import accessory_registry
from ... import hb_types
from ...hb_gpu_draw import (draw_rect, draw_rect_outline, draw_text,
                            draw_lines)
from ...hb_gpu_ui import Theme, fit_text, text_width
from . import types_face_frame as tff

CANVAS_H = 190          # unscaled px
PAD = 12
DRAG_START_PX = 4       # a press that moves this far is a drag
DRAG_STEP = 0.0015875   # 1/16": the least a drag changes a setting by

WALL_FILL = (0.55, 0.45, 0.32, 1.0)         # the box's own sides
FLOOR_FILL = (0.16, 0.16, 0.17, 1.0)        # inside the box
INSERT_FILL = (0.78, 0.66, 0.48, 0.95)      # an insert's footprint
DIVIDER_FILL = (0.90, 0.80, 0.62, 1.0)
PART_LINE = (0.36, 0.28, 0.18, 1.0)         # an insert's own partitions
PICK_LINE = (0.35, 0.80, 1.00, 1.0)
HOVER_FILL = (1.0, 1.0, 1.0, 0.18)

DRAWER_HOST = 'drawer_accessory'
# What the page offers in one click, by the kind of model the catalog's
# render hint builds: (kind, button label).
QUICK_KINDS = (
    ('DIVIDER', "Divider"),
    ('CUTLERY', "Silverware"),
    ('KNIFE_BLOCK', "Knife Block"),
    ('SPICE', "Spice"),
    ('TRAY', "Tray"),
    ('PEG_BOARD', "Peg Board"),
)

# The accessory picked on the page, per opening (by name): its index in
# the opening's interior items.
_picked = {}
# What a press on an accessory hands the drag it starts.
_pending_drag = None


def _s():
    from ...hb_gpu_ui import scale
    return scale()


def _redraw(context):
    screen = getattr(context, 'screen', None)
    for area in screen.areas if screen else ():
        if area.type == 'VIEW_3D':
            area.tag_redraw()


# ---- What is in the drawer -----------------------------------------------------

def _items(opening):
    props = getattr(opening, 'face_frame_opening', None)
    return props.interior_items if props is not None else ()


def picked_index(opening):
    """The picked accessory's index in the opening's items, or -1."""
    index = _picked.get(opening.name, -1)
    items = _items(opening)
    if 0 <= index < len(items) and items[index].kind == 'ACCESSORY':
        return index
    return -1


def _kind(item):
    return tff.render_hint_kind(getattr(item, 'accessory_render', '')) or ""


class _Drawer:
    """A drawer box read for the picture: its outside, its inside, and
    the footprint of every accessory part in it, in the box's own X
    (across) and Y (front to back)."""

    def __init__(self, box):
        geo = hb_types.GeoNodeObject(box)
        self.dx = abs(geo.get_input('Dim X') or 0.0)
        self.dy = abs(geo.get_input('Dim Y') or 0.0)
        side, front, _floor = tff.FaceFrameCabinet._drawer_box_interior(box)
        self.inner = (side, front, self.dx - side, self.dy - side)
        # item index -> [(x0, y0, x1, y1, is divider)]
        self.parts = {}
        # The inserts' own edges seen from above (their compartments and
        # slots), as [((x, y), (x, y))].
        self.lines = []
        for child in box.children:
            role = child.get('hb_part_role')
            if role not in (tff.PART_ROLE_DRAWER_INSERT,
                            tff.PART_ROLE_DRAWER_DIVIDER):
                continue
            try:
                pts = [child.matrix_local @ Vector(c)
                       for c in child.bound_box]
            except Exception:
                continue
            rect = (min(p.x for p in pts), min(p.y for p in pts),
                    max(p.x for p in pts), max(p.y for p in pts),
                    role == tff.PART_ROLE_DRAWER_DIVIDER)
            index = child.get(tff.DRAWER_ITEM_INDEX, -1)
            self.parts.setdefault(index, []).append(rect)
            if role == tff.PART_ROLE_DRAWER_INSERT:
                self._read_lines(child)

    def _read_lines(self, obj):
        mesh = getattr(obj, 'data', None)
        if mesh is None or not hasattr(mesh, 'edges'):
            return
        ml = obj.matrix_local
        seen = set()
        try:
            co = [ml @ v.co for v in mesh.vertices]
            for edge in mesh.edges:
                a, b = co[edge.vertices[0]], co[edge.vertices[1]]
                p = (round(a.x, 4), round(a.y, 4))
                q = (round(b.x, 4), round(b.y, 4))
                if p == q:
                    continue            # standing up: a point from above
                key = (p, q) if p <= q else (q, p)
                if key not in seen:
                    seen.add(key)
                    self.lines.append(key)
        except Exception:
            return

    def ok(self):
        return self.dx > 1e-4 and self.dy > 1e-4

    def union(self, index):
        rects = self.parts.get(index)
        if not rects:
            return None
        return (min(r[0] for r in rects), min(r[1] for r in rects),
                max(r[2] for r in rects), max(r[3] for r in rects))


class _View:
    """Maps the box's plan into the canvas rect: the front at the
    bottom, the back at the top."""

    def __init__(self, rect, drawer, s):
        rx, ry, rw, rh = rect
        pad = PAD * s
        foot = 14 * s                      # room for the FRONT label
        self.k = min((rw - 2 * pad) / drawer.dx,
                     (rh - 2 * pad - foot) / drawer.dy)
        self.ox = rx + (rw - drawer.dx * self.k) / 2.0
        self.oy = ry + foot + (rh - foot - drawer.dy * self.k) / 2.0

    def rect(self, box, min_px=0.0):
        x0 = self.ox + box[0] * self.k
        y0 = self.oy + box[1] * self.k
        w = (box[2] - box[0]) * self.k
        h = (box[3] - box[1]) * self.k
        if w < min_px:
            x0 -= (min_px - w) / 2.0
            w = min_px
        if h < min_px:
            y0 -= (min_px - h) / 2.0
            h = min_px
        return (x0, y0, w, h)


def _laid(box_name, rect, s):
    box = bpy.data.objects.get(box_name)
    if box is None:
        return None
    try:
        drawer = _Drawer(box)
    except Exception:
        return None
    if not drawer.ok():
        return None
    return drawer, _View(rect, drawer, s)


def _item_at(drawer, view, mx, my, s):
    """The accessory under the cursor (its item index), the smallest
    footprint winning so a divider over a tray can be taken."""
    best = None
    grab = 3 * s
    for index, rects in drawer.parts.items():
        if index < 0:
            continue
        for r in rects:
            x, y, w, h = view.rect(r, min_px=3.0 * s)
            if (x - grab <= mx <= x + w + grab
                    and y - grab <= my <= y + h + grab):
                if best is None or w * h < best[1]:
                    best = (index, w * h)
    return best[0] if best else -1


# ---- The picture ---------------------------------------------------------------

def canvas(box_name, opening_name):
    def paint(shader, font_id, rect, mx, my, s):
        _paint(shader, font_id, rect, mx, my, s, box_name, opening_name)

    def hit(context, rect, mx, my):
        _hit(context, rect, mx, my, box_name, opening_name)
    return {'height': CANVAS_H, 'paint': paint, 'hit': hit}


def _paint(shader, font_id, rect, mx, my, s, box_name, opening_name):
    draw_rect(shader, *rect, Theme.PANEL_BG)
    laid = _laid(box_name, rect, s)
    if laid is None:
        return
    drawer, view = laid
    opening = bpy.data.objects.get(opening_name)
    items = _items(opening) if opening is not None else ()
    draw_rect(shader, *view.rect((0.0, 0.0, drawer.dx, drawer.dy)),
              WALL_FILL)
    draw_rect(shader, *view.rect(drawer.inner), FLOOR_FILL)
    hover = _item_at(drawer, view, mx, my, s)
    picked = picked_index(opening) if opening is not None else -1
    size = 10 * s
    # Blocks first, then the dividers that cross them.
    for dividers in (False, True):
        for index, rects in drawer.parts.items():
            for r in rects:
                if r[4] != dividers:
                    continue
                x, y, w, h = view.rect(r, min_px=3.0 * s)
                draw_rect(shader, x, y, w, h,
                          DIVIDER_FILL if dividers else INSERT_FILL)
                if not dividers:
                    draw_rect_outline(shader, x, y, w, h, WALL_FILL)
                if index == hover and index >= 0:
                    draw_rect(shader, x, y, w, h, HOVER_FILL)
    # The inserts' compartments and slots, as they are built.
    if drawer.lines:
        pts = []
        for (ax, ay), (bx, by) in drawer.lines:
            pts += [(view.ox + ax * view.k, view.oy + ay * view.k),
                    (view.ox + bx * view.k, view.oy + by * view.k)]
        draw_lines(shader, pts, PART_LINE)
    # What each block is, where there is room to say so.
    for index in drawer.parts:
        if not 0 <= index < len(items):
            continue
        if any(r[4] for r in drawer.parts[index]):
            continue
        box = drawer.union(index)
        x, y, w, h = view.rect(box)
        text = items[index].accessory_code or items[index].accessory_label
        if not text or h < size + 4 * s:
            continue
        text = fit_text(font_id, size, text, w - 6 * s)
        if text:
            tw = text_width(font_id, size, text)
            draw_text(font_id, x + (w - tw) / 2.0, y + (h - size) / 2.0,
                      size, (0.10, 0.08, 0.05, 1.0), text)
    if picked in drawer.parts:
        for r in drawer.parts[picked]:
            x, y, w, h = view.rect(r, min_px=3.0 * s)
            draw_rect_outline(shader, x, y, w, h, PICK_LINE)
            draw_rect_outline(shader, x - s, y - s, w + 2 * s, h + 2 * s,
                              PICK_LINE)
    # Which way is out.
    fx, fy, fw, _fh = view.rect((0.0, 0.0, drawer.dx, drawer.dy))
    label = "FRONT"
    draw_text(font_id, fx + (fw - text_width(font_id, size, label)) / 2.0,
              fy - size - 3 * s, size, Theme.TEXT_DIM, label)
    if not any(i >= 0 for i in drawer.parts):
        note = "Empty: add an accessory below"
        draw_text(font_id,
                  fx + (fw - text_width(font_id, 11 * s, note)) / 2.0,
                  view.oy + drawer.dy * view.k / 2.0 - 5 * s, 11 * s,
                  Theme.TEXT_DIM, note)


def _hit(context, rect, mx, my, box_name, opening_name):
    """A press in the picture. A press on an accessory starts a drag,
    which picks it when let go without moving; anywhere else unpicks.
    Either way the release is taken here, so it never reaches the
    viewport behind the panel."""
    from ...operators import options_panel
    global _pending_drag
    s = _s()
    laid = _laid(box_name, rect, s)
    index = -1
    if laid is not None:
        drawer, view = laid
        index = _item_at(drawer, view, mx, my, s)
        if index >= 0:
            _pending_drag = (opening_name, index, view.k,
                             drawer.inner, drawer.union(index),
                             drawer.parts.get(index) or [])
            try:
                bpy.ops.hb_face_frame.drag_drawer_item('INVOKE_DEFAULT')
                return
            except Exception as ex:
                _pending_drag = None
                print('Home Builder: drawer drag failed: %s' % ex)
    options_panel._run_on_release('hb_face_frame.pick_drawer_item',
                                  {'opening_name': opening_name,
                                   'index': index})


# ---- The blocks under the picture ----------------------------------------------

def _catalog():
    """{render kind: [(code, name)]} of the drawer accessories the
    catalog models, in catalog order."""
    out = {}
    for it in accessory_registry.all_items():
        if it.get('host') != DRAWER_HOST:
            continue
        kind = tff.render_hint_kind((it.get('render') or '').upper())
        code = it.get('code')
        if kind and code:
            out.setdefault(kind, []).append((code, it.get('name') or code))
    return out


def _add_entries(opening_name, choices):
    def entries(_context):
        return [("%s  (%s)" % (name, code), 'hb_face_frame.drawer_page_add',
                 {'opening_name': opening_name, 'code': code})
                for code, name in choices]
    return entries


def _quick_add(opening):
    """Rows of one-click adds for the kinds the catalog models. A kind
    with one product adds it; a kind with several opens a short list."""
    catalog = _catalog()
    buttons = []
    for kind, label in QUICK_KINDS:
        choices = catalog.get(kind)
        if not choices:
            continue
        if len(choices) == 1:
            buttons.append(("+ " + label, 'hb_face_frame.drawer_page_add',
                            {'opening_name': opening.name,
                             'code': choices[0][0]}, None))
        else:
            buttons.append(("+ %s..." % label,
                            _add_entries(opening.name, choices), None, None))
    # Everything else the catalog models for a drawer, in one list.
    named = {kind for kind, _label in QUICK_KINDS}
    rest = [choice for kind, choices in catalog.items()
            if kind not in named for choice in choices]
    if rest:
        buttons.append(("+ More...", _add_entries(opening.name, rest),
                        None, None))
    return [('actions', tuple(buttons[i:i + 2]))
            for i in range(0, len(buttons), 2)]


def blocks(context, box, opening):
    """The picture and what goes under it, for one picked drawer box."""
    from ...operators import options_panel
    from . import interior_page
    out = [('canvas', canvas(box.name, opening.name))]
    quick = _quick_add(opening)
    if quick:
        out.append(('label', "Add to this drawer"))
        out.extend(quick)
    props = opening.face_frame_opening
    above = len(getattr(props, 'rollouts_above', ()))
    out.append(('actions', (
        ("+ Rollout Above", 'hb_face_frame.add_rollout_above',
         {'opening_name': opening.name}, None),
        ("Rollouts Above (%d)" % above if above else "Rollouts Above",
         'hb_face_frame.rollout_above_drawer_prompts', None, None))))
    index = picked_index(opening)
    if index >= 0:
        item = props.interior_items[index]
        out.append(('gap', None))
        out.append(('label', item.accessory_label or item.accessory_code
                    or "Accessory"))
        fields = interior_page._item_fields(item, index, opening.name)
        # The first field is the item's type: a drawer accessory stays one.
        out.extend(options_panel.field_blocks(context, fields[1:], item))
        out.append(('actions', (
            ("Remove", 'hb_face_frame.remove_accessory_item',
             {'target_name': opening.name, 'index': index}, None),)))
    elif any(it.kind == 'ACCESSORY' for it in props.interior_items):
        out.append(('note', "Click an accessory in the picture to edit "
                            "it, or drag it to place it."))
    return out


# ---- Commands ------------------------------------------------------------------

class hb_face_frame_OT_pick_drawer_item(bpy.types.Operator):
    """Pick this accessory to edit it"""
    bl_idname = "hb_face_frame.pick_drawer_item"
    bl_label = "Pick Drawer Accessory"
    bl_options = {'INTERNAL'}

    opening_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore
    index: bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        if self.index < 0:
            _picked.pop(self.opening_name, None)
        else:
            _picked[self.opening_name] = self.index
        _redraw(context)
        return {'FINISHED'}


class hb_face_frame_OT_drawer_page_add(bpy.types.Operator):
    """Add this accessory to the drawer and pick it"""
    bl_idname = "hb_face_frame.drawer_page_add"
    bl_label = "Add Drawer Accessory"
    bl_options = {'UNDO', 'INTERNAL'}

    opening_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore
    code: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        opening = bpy.data.objects.get(self.opening_name)
        if opening is None or not self.code:
            return {'CANCELLED'}
        result = bpy.ops.hb_face_frame.drawer_add_accessory(
            opening_name=self.opening_name, code=self.code)
        if 'FINISHED' not in result:
            return {'CANCELLED'}
        _picked[self.opening_name] = len(_items(opening)) - 1
        _redraw(context)
        return {'FINISHED'}


class hb_face_frame_OT_drag_drawer_item(bpy.types.Operator):
    """Drag an accessory to place it in the drawer; let go without
    moving to pick it. Esc or right-click puts it back"""
    bl_idname = "hb_face_frame.drag_drawer_item"
    bl_label = "Move Drawer Accessory"
    bl_options = {'UNDO', 'INTERNAL'}

    def invoke(self, context, event):
        global _pending_drag
        pending, _pending_drag = _pending_drag, None
        if pending is None:
            return {'CANCELLED'}
        (self.opening_name, self.index, self.k, self.inner, self.box,
         rects) = pending
        item = self._item()
        if item is None or self.k <= 0 or self.box is None:
            return {'CANCELLED'}
        self.kind = _kind(item)
        self.saved = (item.insert_offset, item.insert_from_front,
                      item.divider_offset)
        # A single divider that is not held by typed spaces slides along
        # the drawer; several, or spaced ones, are only picked.
        self.movable = True
        if self.kind == 'DIVIDER':
            spaced = any(item.divider_space_unlock[i]
                         for i in range(len(item.divider_space_unlock)))
            self.movable = item.accessory_qty <= 1 and not spaced \
                and len(rects) == 1
            if item.divider_lengthwise:
                self.start = (self.box[0] + self.box[2]) / 2.0 - self.inner[0]
            else:
                self.start = (self.box[1] + self.box[3]) / 2.0 - self.inner[1]
        else:
            self.start = (self.box[0] - self.inner[0],
                          self.box[1] - self.inner[1])
        self.press = (event.mouse_x, event.mouse_y)
        self.dragging = False
        self.last = None
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _item(self):
        opening = bpy.data.objects.get(self.opening_name)
        items = _items(opening) if opening is not None else ()
        if 0 <= self.index < len(items):
            return items[self.index]
        return None

    @staticmethod
    def _step(value):
        return round(value / DRAG_STEP) * DRAG_STEP

    def _move(self, context, dx, dy):
        item = self._item()
        if item is None:
            return
        x0, y0, x1, y1 = self.inner
        if self.kind == 'DIVIDER':
            if item.divider_lengthwise:
                value = min(max(self.start + dx, DRAG_STEP), x1 - x0)
            else:
                value = min(max(self.start + dy, DRAG_STEP), y1 - y0)
            value = self._step(value)
            if value != self.last:
                self.last = value
                item.divider_offset = value
        else:
            w = self.box[2] - self.box[0]
            d = self.box[3] - self.box[1]
            # An offset of zero means "pack it for me": a dragged insert
            # is held where it was put, so it never lands on zero.
            fx = self._step(min(max(self.start[0] + dx, DRAG_STEP),
                                max(x1 - x0 - w, DRAG_STEP)))
            fy = self._step(min(max(self.start[1] + dy, 0.0),
                                max(y1 - y0 - d, 0.0)))
            if (fx, fy) != self.last:
                self.last = (fx, fy)
                item.insert_offset = fx
                item.insert_from_front = fy
        _redraw(context)

    def _restore(self):
        item = self._item()
        if item is None:
            return
        offset, from_front, divider = self.saved
        if self.kind == 'DIVIDER':
            item.divider_offset = divider
        else:
            item.insert_offset = offset
            item.insert_from_front = from_front

    def modal(self, context, event):
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            px = event.mouse_x - self.press[0]
            py = event.mouse_y - self.press[1]
            if not self.dragging:
                if not self.movable \
                        or math.hypot(px, py) < DRAG_START_PX * _s():
                    return {'RUNNING_MODAL'}
                self.dragging = True
            self._move(context, px / self.k, py / self.k)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            _picked[self.opening_name] = self.index
            _redraw(context)
            return {'FINISHED'} if self.dragging else {'CANCELLED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if self.dragging:
                self._restore()
            _redraw(context)
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


classes = (
    hb_face_frame_OT_pick_drawer_item,
    hb_face_frame_OT_drawer_page_add,
    hb_face_frame_OT_drag_drawer_item,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    _picked.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
