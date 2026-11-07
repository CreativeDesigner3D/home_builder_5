"""The Interior page: an opening's interior, edited on a picture of it.

Picking a shelf, a roll-out box or any other interior part used to give
the part's size and a few of its menu commands; what the opening held,
and the way to change it, was in a dialog of lists. This page draws the
opening's interior instead -- the regions its fixed shelves and
divisions make, and the parts in each, where they are -- and lists what
the picked region holds below the picture: each item, its type (switch
it there), the few settings that matter for it, and a way to add more.

What the page edits is the region the pick sits in: the region itself,
the region an interior part stands in (parts all parent to the opening,
so that is worked out from where the part is), or the whole opening
when its interior is not split. Clicking a region in the picture picks
it. The data is the interior as it always was -- the opening's or the
region's interior_items -- so saved files, pricing and the drawings do
not change.

It is a page of the face frame card (selected_card), shown for an
interior part, an interior region, or an opening whose Interior page
was opened from its Opening page.
"""

import bpy
from mathutils import Matrix, Vector

from ... import hb_types
from ...hb_gpu_draw import draw_rect, draw_rect_outline, draw_text
from ...hb_gpu_ui import Theme, fit_text
from . import types_face_frame as tff

CANVAS_H = 170          # unscaled px
PAD = 8

# The opening whose Interior page is open from its Opening page (by name)
_shown_for = None
# The pick the item list was last lined up with, so a newly picked part
# selects its item once and a click in the list is not undone
_synced_pick = None

_SHELVES = ('ADJUSTABLE_SHELF', 'GLASS_SHELF', 'HALF_DEPTH_SHELF',
            'QUARTER_DEPTH_SHELF')

PART_FILL = (0.78, 0.66, 0.48, 0.95)        # wood
BAR_FILL = (0.55, 0.45, 0.32, 1.0)          # fixed shelves and divisions
BOX_FILL = (0.70, 0.58, 0.42, 0.85)         # roll-out / drawer boxes
OPENING_FILL = (0.10, 0.10, 0.11, 1.0)
PICK_LINE = (0.35, 0.80, 1.00, 1.0)


# ---- What the page is for ---------------------------------------------------

def is_interior_part(obj):
    return bool(obj is not None and obj.get('IS_FACE_FRAME_INTERIOR_PART'))


def opening_of(obj):
    while obj is not None:
        if obj.get(tff.TAG_OPENING_CAGE):
            return obj
        obj = obj.parent
    return None


def has_tree(opening):
    return any(c.get(tff.TAG_INTERIOR_SPLIT_NODE)
               or c.get(tff.TAG_INTERIOR_REGION) for c in opening.children)


def regions_of(opening):
    return [o for o in opening.children_recursive
            if o.get(tff.TAG_INTERIOR_REGION)]


def showing(opening):
    return opening is not None and opening.name == _shown_for


def show(opening_name):
    global _shown_for
    _shown_for = opening_name or None


def items_props(owner):
    """The property group holding `owner`'s interior_items, or None for
    a split opening (its items are on its regions)."""
    if owner is None:
        return None
    if owner.get(tff.TAG_INTERIOR_REGION):
        return owner.face_frame_interior_region
    if owner.get(tff.TAG_OPENING_CAGE) and not has_tree(owner):
        return owner.face_frame_opening
    return None


def owner_of(pick):
    """The region or opening whose interior the pick belongs to."""
    if pick is None:
        return None
    if pick.get(tff.TAG_INTERIOR_REGION) or pick.get(tff.TAG_OPENING_CAGE):
        return pick
    opening = opening_of(pick)
    if opening is None:
        return None
    if not has_tree(opening):
        return opening
    if pick.get('hb_part_role') in ('INTERIOR_FIXED_SHELF',
                                    'INTERIOR_DIVISION'):
        return opening          # a split itself: no one region
    frame = _Frame(opening)
    box = frame.part_box(pick)
    if box is None:
        return opening
    cx, cz = (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0
    for region in regions_of(opening):
        r = frame.region_box(region)
        if r and r[0] <= cx <= r[2] and r[1] <= cz <= r[3]:
            return region
    return opening


# ---- Geometry, in the opening's front view ----------------------------------

class _Frame:
    """Boxes (x0, z0, x1, z1) in the opening's own X / Z."""

    def __init__(self, opening):
        self.opening = opening

    def _to_opening(self, obj):
        """`obj`'s matrix in the opening's space, from the local
        transforms: the region cages are hidden, and a hidden object's
        matrix_world is not kept current."""
        m = Matrix.Identity(4)
        while obj is not None and obj is not self.opening:
            m = obj.matrix_parent_inverse @ obj.matrix_basis @ m
            obj = obj.parent
        return m if obj is self.opening else None

    def _cage_box(self, obj):
        geo = hb_types.GeoNodeObject(obj)
        try:
            dx, dy, dz = (geo.get_input('Dim X'), geo.get_input('Dim Y'),
                          geo.get_input('Dim Z'))
        except Exception:
            return None
        m = self._to_opening(obj)
        if m is None:
            return None
        pts = [m @ Vector((x, y, z))
               for x in (0.0, dx) for y in (0.0, -dy) for z in (0.0, dz)]
        return _bounds(pts)

    def opening_box(self):
        geo = hb_types.GeoNodeObject(self.opening)
        try:
            dx, dz = geo.get_input('Dim X'), geo.get_input('Dim Z')
        except Exception:
            return None
        return (0.0, 0.0, dx, dz)

    def region_box(self, region):
        return self._cage_box(region)

    def part_box(self, part):
        if part.type not in ('MESH', 'CURVE', 'FONT'):
            return None
        m = self._to_opening(part)
        if m is None:
            return None
        pts = [m @ Vector(c) for c in part.bound_box]
        box = _bounds(pts)
        if box[2] - box[0] < 1e-5 and box[3] - box[1] < 1e-5:
            return None
        return box


def _bounds(pts):
    xs = [p.x for p in pts]
    zs = [p.z for p in pts]
    return (min(xs), min(zs), max(xs), max(zs))


def _interior_parts(opening):
    return [o for o in opening.children_recursive
            if is_interior_part(o) and o.visible_get()]


class _View:
    """Maps the opening's front view into the canvas rect."""

    def __init__(self, rect, box, s):
        rx, ry, rw, rh = rect
        pad = PAD * s
        w = max(box[2] - box[0], 1e-6)
        h = max(box[3] - box[1], 1e-6)
        self.k = min((rw - 2 * pad) / w, (rh - 2 * pad) / h)
        self.ox = rx + (rw - w * self.k) / 2.0 - box[0] * self.k
        self.oy = ry + (rh - h * self.k) / 2.0 - box[1] * self.k

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


# ---- The picture --------------------------------------------------------------

def _canvas(opening_name, owner_name):
    def paint(shader, font_id, rect, mx, my, s):
        _paint(shader, font_id, rect, mx, my, s, opening_name, owner_name)

    def hit(context, rect, mx, my):
        _hit(context, rect, mx, my, opening_name, owner_name)
    return {'height': CANVAS_H, 'paint': paint, 'hit': hit}


def _layout(opening_name, rect, s):
    opening = bpy.data.objects.get(opening_name)
    if opening is None:
        return None
    frame = _Frame(opening)
    obox = frame.opening_box()
    if obox is None:
        return None
    return opening, frame, obox, _View(rect, obox, s)


def _paint(shader, font_id, rect, mx, my, s, opening_name, owner_name):
    draw_rect(shader, *rect, Theme.PANEL_BG)
    laid = _layout(opening_name, rect, s)
    if laid is None:
        return
    opening, frame, obox, view = laid
    orect = view.rect(obox)
    draw_rect(shader, *orect, OPENING_FILL)
    regions = regions_of(opening) if has_tree(opening) else []
    hover = _region_at(frame, view, regions, mx, my)
    for region in regions:
        box = frame.region_box(region)
        if box is None:
            continue
        r = view.rect(box)
        if region is hover:
            draw_rect(shader, *r, Theme.ROW_HOVER_BG)
        draw_rect_outline(shader, *r, Theme.PANEL_BORDER)
    # The parts, where they are: wood shelves, boxes, and the darker
    # fixed shelves and divisions that make the regions.
    for part in _interior_parts(opening):
        box = frame.part_box(part)
        if box is None:
            continue
        role = part.get('hb_part_role', '')
        if role in ('INTERIOR_FIXED_SHELF', 'INTERIOR_DIVISION'):
            color = BAR_FILL
        elif part.get('IS_DRAWER_BOX'):
            color = BOX_FILL
        else:
            color = PART_FILL
        r = view.rect(box, min_px=2.0 * s)
        draw_rect(shader, *r, color)
        if part.get('IS_DRAWER_BOX'):
            draw_rect_outline(shader, *r, BAR_FILL)
    # The region (or the opening) the page is editing.
    owner = bpy.data.objects.get(owner_name) if owner_name else None
    if owner is not None:
        box = (frame.region_box(owner) if owner.get(tff.TAG_INTERIOR_REGION)
               else obox)
        if box is not None:
            x, y, w, h = view.rect(box)
            # Two outlines, a pixel apart, for a line that reads as picked.
            draw_rect_outline(shader, x, y, w, h, PICK_LINE)
            draw_rect_outline(shader, x + s, y + s, w - 2 * s, h - 2 * s,
                              PICK_LINE)
    if regions and (owner is None or not owner.get(tff.TAG_INTERIOR_REGION)):
        text = "Click a region to edit what is in it"
        size = 11 * s
        draw_text(font_id, rect[0] + 6 * s, rect[1] + 5 * s, size,
                  Theme.TEXT_DIM, fit_text(font_id, size, text, rect[2] - 12 * s))


def _region_at(frame, view, regions, mx, my):
    best = None
    for region in regions:
        box = frame.region_box(region)
        if box is None:
            continue
        x, y, w, h = view.rect(box)
        if x <= mx <= x + w and y <= my <= y + h:
            if best is None or w * h < best[1]:
                best = (region, w * h)
    return best[0] if best else None


def _hit(context, rect, mx, my, opening_name, owner_name):
    laid = _layout(opening_name, rect, _s())
    if laid is None:
        return
    opening, frame, _obox, view = laid
    if not has_tree(opening):
        return
    region = _region_at(frame, view, regions_of(opening), mx, my)
    if region is None or region.name == owner_name:
        return
    pick(context, region)


def _s():
    from ...hb_gpu_ui import scale
    return scale()


def pick(context, obj):
    """Make `obj` the pick, so the page follows it."""
    view_layer = context.view_layer
    for o in context.selected_objects:
        try:
            o.select_set(False)
        except RuntimeError:
            pass
    try:
        obj.select_set(True)
    except RuntimeError:
        pass                    # a hidden cage: active is enough
    view_layer.objects.active = obj


# ---- The page -------------------------------------------------------------------

def _kind_items():
    from .props_hb_face_frame import Face_Frame_Interior_Item
    return Face_Frame_Interior_Item.INTERIOR_KIND_ITEMS


def kind_label(kind):
    return next((label for ident, label, _d in _kind_items()
                 if ident == kind), kind.replace('_', ' ').title())


def _summary(it):
    k = it.kind
    if k in _SHELVES:
        return "%d" % it.shelf_qty
    if k == 'ROLLOUT':
        n = len(it.rollout_boxes) or it.qty
        return "%d box%s" % (n, "" if n == 1 else "es")
    if k == 'PULLOUT_SHELF':
        return "%d" % it.qty
    if k == 'TRAY_DIVIDERS':
        return "%d" % it.tray_qty
    if k == 'ACCESSORY':
        return it.accessory_code or it.accessory_label
    return ""


def _item_label(it):
    if it.kind == 'ACCESSORY' and it.accessory_code:
        return it.accessory_label or it.accessory_code
    return kind_label(it.kind)


def _item_fields(it):
    """The few settings that matter for an item, by its type."""
    f = [('enum', 'kind', "Type")]
    k = it.kind
    if k in _SHELVES:
        f += [
            ('bool', 'unlock_shelf_qty', "Set Count"),
            ('number', 'shelf_qty', "Shelves",
             {'when': lambda o: o.unlock_shelf_qty}),
            ('value', lambda o: str(o.shelf_qty), "Shelves",
             {'when': lambda o: not o.unlock_shelf_qty}),
            ('distance', 'shelf_setback', "Setback"),
            ('enum', 'shelf_nosing_style', "Nosing"),
        ]
        if k == 'GLASS_SHELF':
            f.append(('distance', 'glass_thickness', "Glass"))
    elif k == 'PULLOUT_SHELF':
        f += [
            ('bool', 'unlock_qty', "Set Count"),
            ('number', 'qty', "Shelves", {'when': lambda o: o.unlock_qty}),
            ('value', lambda o: str(o.qty), "Shelves",
             {'when': lambda o: not o.unlock_qty}),
        ]
    elif k == 'ROLLOUT':
        f += [
            ('value', lambda o: str(len(o.rollout_boxes) or o.qty), "Boxes"),
            ('bool', 'rollout_bottom_fixed', "Bottom Box Fixed"),
            ('bool', 'hide_rollout_spacers', "Hide Spacer Ladders"),
            ('bool', 'finger_scoop', "Finger Scoop"),
        ]
    elif k == 'TRAY_DIVIDERS':
        f += [
            ('number', 'tray_qty', "Dividers"),
            ('bool', 'tray_remove_shelf', "No Shelf Above"),
        ]
    elif k == 'VANITY_SHELVES':
        f += [
            ('distance', 'vanity_z', "Height"),
            ('distance', 'vanity_length', "Length"),
        ]
    elif k == 'CLOSET_ROD':
        f.append(('distance', 'rod_distance_from_top', "From Top"))
    elif k == 'ACCESSORY':
        if it.accessory_code:
            f += [('value', lambda o: o.accessory_code, "Code"),
                  ('number', 'accessory_qty', "Quantity")]
        else:
            f.append(('text', 'accessory_label', "Text"))
    return tuple(f)


def _add_entries(owner_name):
    def entries(_context):
        out = []
        for ident, label, _d in _kind_items():
            if ident == 'ACCESSORY':
                continue        # Text, below with the catalog
            out.append((label, 'hb_face_frame.add_interior_item',
                        {'kind': ident, 'target_name': owner_name}))
        out.append(("", None, {}))
        out.append(("Text", 'hb_face_frame.add_interior_item',
                    {'kind': 'ACCESSORY', 'target_name': owner_name}))
        out.append(("Catalog Accessory...", 'hb_face_frame.add_interior_accessory',
                    {'target_name': owner_name, 'INVOKE': True}))
        return out
    return entries


def _act(label, op_id, kwargs=None, icon=None):
    return (label, op_id, dict(kwargs or {}), None, 1.0, icon)


def _sync_index(pick_obj, props):
    """A newly picked part selects the item that built it, once."""
    global _synced_pick
    if pick_obj is None or pick_obj.name == _synced_pick:
        return
    _synced_pick = pick_obj.name
    role = str(pick_obj.get('hb_part_role', '') or '')
    if not role or not is_interior_part(pick_obj):
        return
    for i, it in enumerate(props.interior_items):
        if (it.kind == role or role.startswith(it.kind)
                or it.kind.startswith(role.split('_')[0] + '_')):
            props.interior_items_index = i
            return


def blocks(context, item):
    """The Interior page's blocks for a face frame card item."""
    from ...operators import options_panel
    _kind, _root, _bay, opening, pick_obj = item
    if opening is None:
        return []
    owner = owner_of(pick_obj) if pick_obj is not None else opening
    props = items_props(owner)
    out = [('canvas', _canvas(opening.name, owner.name if owner else ""))]
    if props is None:
        out.append(('note', "This interior is split: click a region"))
        out.append(('gap', None))
        out.append(('actions', (
            _act("Opening", 'hb_face_frame.show_interior_page',
                 {'opening_name': ""}, ),
            _act("More Options...", 'hb_face_frame.interior_options',
                 {'opening_name': opening.name}),
        )))
        return out
    _sync_index(pick_obj, props)
    where = "Region" if owner.get(tff.TAG_INTERIOR_REGION) else "Opening"
    out.append(('label', "In this %s" % where.lower()))
    items = props.interior_items
    if len(items) == 0:
        out.append(('note', "Nothing yet -- add something below"))
    for i, it in enumerate(items):
        def click(i=i, props=props):
            props.interior_items_index = i
        out.append(('list_row', {
            'key': ('interior', owner.name, i),
            'text': _item_label(it),
            'summary': _summary(it),
            'active': i == props.interior_items_index,
            'click': click,
            'remove': ('hb_face_frame.remove_interior_item',
                       {'index': i, 'target_name': owner.name}),
            'confirm': False,
        }))
    out.append(('actions', (
        _act("Shelves", 'hb_face_frame.add_interior_item',
             {'kind': 'ADJUSTABLE_SHELF', 'target_name': owner.name}, 'ADD'),
        _act("Roll-outs", 'hb_face_frame.add_interior_item',
             {'kind': 'ROLLOUT', 'target_name': owner.name}, 'ADD'),
        ("Add...", _add_entries(owner.name), None, None),
    )))
    idx = props.interior_items_index
    if 0 <= idx < len(items):
        it = items[idx]
        out.append(('gap', None))
        out.append(('label', _item_label(it)))
        out.extend(options_panel.field_blocks(context, _item_fields(it), it))
    out.append(('gap', None))
    out.append(('actions', (
        _act("Opening", 'hb_face_frame.show_interior_page',
             {'opening_name': ""}),
        _act("More Options...", 'hb_face_frame.interior_options',
             {'opening_name': opening.name}),
    )))
    return out


# ---- Commands ----------------------------------------------------------------

class hb_face_frame_OT_show_interior_page(bpy.types.Operator):
    """Edit this opening's interior on a picture of it"""
    bl_idname = "hb_face_frame.show_interior_page"
    bl_label = "Interior"
    bl_options = {'INTERNAL'}

    opening_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        if self.opening_name:
            opening = bpy.data.objects.get(self.opening_name)
            if opening is None:
                return {'CANCELLED'}
            show(opening.name)
            pick(context, opening)
        else:
            # Back to the Opening page of the opening on show
            active = context.view_layer.objects.active
            opening = opening_of(active) if active is not None else None
            show(None)
            if opening is not None:
                pick(context, opening)
        for area in context.screen.areas if context.screen else ():
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


classes = (hb_face_frame_OT_show_interior_page,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
