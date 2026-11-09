"""The frameless Interior page: an opening's interior, edited on a picture.

The face frame library's Interior page, for frameless cabinets. The
picture draws the opening's interior: the sections its fixed shelves and
divisions make, and the shelves and boxes in each, where they are.
Clicking a section picks it; dragging a fixed shelf or a division moves
it, and clicking one picks it. Below the picture is what the pick holds
and the way to change it: the section's interior type and settings, Add
Fixed Shelf / Add Division to split it, and Remove to join it back. A
picked fixed shelf or division shows where it sits (From Bottom / From
Left), the space on each side and whether that space holds its size.

The data is the interior as the frameless library always built it: a
fixed shelf is a splitter whose sections stack, a division one whose
sections sit side by side, and the section sizes are the splitter's
calculator prompts -- so saved files, the drawings and pricing do not
change.

Section cages are hidden, and Blender's viewport has no active object
while a hidden one is active, so a visible object (the anchor) stays the
pick while the page is on a section; picking anything else ends it.
"""

import bpy
from mathutils import Matrix, Vector

from ... import hb_types, hb_utils, units
from ...hb_gpu_draw import draw_rect, draw_rect_outline, draw_text
from ...hb_gpu_ui import Theme, fit_text

CANVAS_H = 170          # unscaled px
PAD = 8
BAR_HIT_PX = 5          # unscaled: how near a bar a press takes it
MIN_SECTION = 0.0508    # 2": the least a drag leaves either side

TAG_OPENING = 'IS_FRAMELESS_OPENING_CAGE'
TAG_BAY = 'IS_FRAMELESS_BAY_CAGE'
TAG_INTERIOR = 'IS_FRAMELESS_INTERIOR_CAGE'
TAG_SECTION = 'IS_FRAMELESS_INTERIOR_SECTION'
TAG_FIXED_SHELF = 'IS_FRAMELESS_INTERIOR_SPLITTER_VERTICAL'    # sections stack
TAG_DIVISION = 'IS_FRAMELESS_INTERIOR_SPLITTER_HORIZONTAL'     # side by side

SPLIT_SCHEMA = 'FL_INTERIOR_SPLIT'

PART_FILL = (0.78, 0.66, 0.48, 0.95)        # wood
BAR_FILL = (0.55, 0.45, 0.32, 1.0)          # fixed shelves and divisions
BOX_FILL = (0.70, 0.58, 0.42, 0.85)         # roll-out / drawer boxes
OPENING_FILL = (0.10, 0.10, 0.11, 1.0)
PICK_LINE = (0.35, 0.80, 1.00, 1.0)
BAR_HOVER = (1.0, 1.0, 1.0, 0.45)

# (anchor, host, section) names while the page is on a section (or on
# the whole interior: section "") in place of the active object
_focus = None
# (splitter name, bar index, axis, px per metre) for the drag a press on
# a bar starts
_pending_drag = None


# ---- The tree ----------------------------------------------------------------

def _solve(obj):
    """Rebuild the cabinet `obj` is in."""
    root = hb_utils.get_cabinet_bp(obj)
    hb_utils.run_calc_fix(bpy.context, root or obj)


def _sf():
    from . import solver_frameless
    return solver_frameless


def is_splitter(obj):
    return bool(obj is not None and (obj.get(TAG_FIXED_SHELF)
                                     or obj.get(TAG_DIVISION)))


def axis_of(splitter):
    """'H' for a fixed shelf (a horizontal board), 'V' for a division."""
    return 'H' if splitter.get(TAG_FIXED_SHELF) else 'V'


def split_label(splitter):
    return "Fixed Shelf" if axis_of(splitter) == 'H' else "Division"


def host_of(obj):
    """The opening (or bay) whose interior `obj` is or is in, or None."""
    while obj is not None:
        if obj.get(TAG_OPENING) or obj.get(TAG_BAY):
            return obj
        obj = obj.parent
    return None


def top_interior(host):
    if host is None:
        return None
    return next((c for c in host.children if c.get(TAG_INTERIOR)), None)


def has_splits(host):
    return is_splitter(top_interior(host))


def section_of(obj):
    """The section `obj` is or sits in, or None."""
    while obj is not None and not (obj.get(TAG_OPENING) or obj.get(TAG_BAY)):
        if obj.get(TAG_SECTION):
            return obj
        obj = obj.parent
    return None


def sections_of(splitter):
    return sorted((c for c in splitter.children if c.get(TAG_SECTION)),
                  key=lambda c: c.get('hb_split_index', 0))


def interior_in(target):
    """The interior a section (or host) holds, or None."""
    return next((c for c in target.children if c.get(TAG_INTERIOR)), None)


def is_bar_part(obj):
    """A fixed shelf or division board."""
    return bool(obj is not None and obj.get('hb_part_role') == 'SPLITTER'
                and is_splitter(obj.parent))


def bar_index(part):
    try:
        return int(part.get('hb_split_index', 0))
    except (TypeError, ValueError):
        return 0


def bar_part(splitter, index):
    return _sf().split_parts(splitter).get(('SPLITTER', index))


def _regions(host):
    top = top_interior(host)
    if top is None:
        return []
    return [o for o in top.children_recursive if o.get(TAG_SECTION)]


def _splitters(host):
    top = top_interior(host)
    if top is None:
        return []
    out = [top] if is_splitter(top) else []
    out += [o for o in top.children_recursive if is_splitter(o)]
    return out


# ---- Where things are -----------------------------------------------------------

class _Frame:
    """Boxes (x0, z0, x1, z1) in the host's own X / Z."""

    def __init__(self, host):
        self.host = host

    def _to_host(self, obj):
        """`obj`'s matrix in the host's space, from the local transforms:
        section cages are hidden, and a hidden object's matrix_world is
        not kept current."""
        m = Matrix.Identity(4)
        while obj is not None and obj is not self.host:
            m = obj.matrix_parent_inverse @ obj.matrix_basis @ m
            obj = obj.parent
        return m if obj is self.host else None

    def cage_box(self, obj):
        geo = hb_types.GeoNodeObject(obj)
        try:
            dx, dy, dz = (geo.get_input('Dim X'), geo.get_input('Dim Y'),
                          geo.get_input('Dim Z'))
        except Exception:
            return None
        m = self._to_host(obj)
        if m is None:
            return None
        return _bounds([m @ Vector((x, y, z)) for x in (0.0, dx)
                        for y in (0.0, -dy) for z in (0.0, dz)])

    def interior_box(self):
        top = top_interior(self.host)
        box = self.cage_box(top) if top is not None else None
        if box is None:
            geo = hb_types.GeoNodeObject(self.host)
            try:
                box = (0.0, 0.0, geo.get_input('Dim X'), geo.get_input('Dim Z'))
            except Exception:
                return None
        return box

    def part_box(self, part):
        if part.type not in ('MESH', 'CURVE', 'FONT'):
            return None
        m = self._to_host(part)
        if m is None:
            return None
        box = _bounds([m @ Vector(c) for c in part.bound_box])
        if box[2] - box[0] < 1e-5 and box[3] - box[1] < 1e-5:
            return None
        return box


def _bounds(pts):
    xs = [p.x for p in pts]
    zs = [p.z for p in pts]
    return (min(xs), min(zs), max(xs), max(zs))


def splits_of(host, frame=None):
    """Every fixed shelf and division in the host's interior, as dicts:
    splitter, index (the board between sections index and index + 1),
    axis, bar (the board's box) and part (the board, or None)."""
    frame = frame or _Frame(host)
    out = []
    for splitter in _splitters(host):
        secs = sections_of(splitter)
        boxes = [frame.cage_box(s) for s in secs]
        axis = axis_of(splitter)
        for i in range(1, len(secs)):
            part = bar_part(splitter, i)
            bar = frame.part_box(part) if part is not None else None
            a, b = boxes[i - 1], boxes[i]
            if bar is None and a is not None and b is not None:
                # No board built (or none yet): the gap between the two.
                bar = ((a[0], b[3], a[2], a[1]) if axis == 'H'
                       else (a[2], a[1], b[0], a[3]))
            if bar is None:
                continue
            out.append({'splitter': splitter, 'index': i, 'axis': axis,
                        'bar': bar, 'part': part})
    return out


def _entry(splitter, index):
    host = host_of(splitter)
    if host is None:
        return None
    return next((sp for sp in splits_of(host)
                 if sp['splitter'] == splitter and sp['index'] == index), None)


def split_position(splitter, index):
    """A fixed shelf's bottom from the interior's bottom, or a division's
    left face from the interior's left side."""
    sp = _entry(splitter, index)
    if sp is None:
        return 0.0
    box = _Frame(host_of(splitter)).interior_box()
    if sp['axis'] == 'H':
        return sp['bar'][1] - box[1]
    return sp['bar'][0] - box[0]


def _sizes(splitter, index):
    """The calculator prompts of the sections either side of the board,
    and their sizes now."""
    calc = _sf().splitter_calculator(splitter)
    if calc is None or index < 1 or index >= len(calc.prompts):
        return None
    pa, pb = calc.prompts[index - 1], calc.prompts[index]
    return pa, pb, float(pa.distance_value), float(pb.distance_value)


def move_bar(splitter, index, delta, start=None):
    """Move the board between sections index and index + 1 by `delta`:
    up for a fixed shelf, right for a division. The two sections share
    the space they had. With two sections the one below (or left) holds
    its size and the other takes the rest, so the board stays put when
    the cabinet is resized."""
    found = _sizes(splitter, index)
    if found is None:
        return
    pa, pb, sa, sb = found
    if start is not None:
        sa, sb = start
    total = sa + sb
    if axis_of(splitter) == 'H':
        # Sections run top down: the upper gives what the board rises.
        new_a = sa - delta
    else:
        new_a = sa + delta
    lo = min(MIN_SECTION, total / 2.0)
    new_a = max(lo, min(total - lo, new_a))
    new_b = total - new_a
    calc = _sf().splitter_calculator(splitter)
    if len(calc.prompts) == 2:
        held, free, value = ((pb, pa, new_b) if axis_of(splitter) == 'H'
                             else (pa, pb, new_a))
        free.equal = True
        held.equal = False
        held.distance_value = value
    else:
        pa.equal = pb.equal = False
        pa.distance_value = new_a
        pb.distance_value = new_b
    _solve(splitter)


def set_split_position(splitter, index, value):
    move_bar(splitter, index, value - split_position(splitter, index))


# ---- The picture ---------------------------------------------------------------

class _View:
    """Maps the interior's front view into the canvas rect."""

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


def _is_cage(obj):
    return any(obj.get(t) for t in (TAG_INTERIOR, TAG_SECTION, TAG_OPENING,
                                    TAG_BAY)) or obj.display_type == 'WIRE'


def _parts(host):
    top = top_interior(host)
    if top is None:
        return []
    out = []
    for o in top.children_recursive:
        try:
            if o.type == 'MESH' and not _is_cage(o) and o.visible_get():
                out.append(o)
        except ReferenceError:
            pass
    return out


def _s():
    from ...hb_gpu_ui import scale
    return scale()


def _layout(host_name, rect, s):
    host = bpy.data.objects.get(host_name)
    if host is None:
        return None
    frame = _Frame(host)
    ibox = frame.interior_box()
    if ibox is None:
        return None
    return host, frame, ibox, _View(rect, ibox, s)


def _bar_at(splits, view, mx, my, s):
    best = None
    tol = BAR_HIT_PX * s
    for sp in splits:
        x, y, w, h = view.rect(sp['bar'])
        if x - tol <= mx <= x + w + tol and y - tol <= my <= y + h + tol:
            d = (abs(mx - (x + w / 2.0)) if sp['axis'] == 'V'
                 else abs(my - (y + h / 2.0)))
            if best is None or d < best[0]:
                best = (d, sp)
    return best[1] if best else None


def _region_at(frame, view, regions, mx, my):
    best = None
    for region in regions:
        box = frame.cage_box(region)
        if box is None:
            continue
        x, y, w, h = view.rect(box)
        if x <= mx <= x + w and y <= my <= y + h:
            if best is None or w * h < best[1]:
                best = (region, w * h)
    return best[0] if best else None


def canvas(host_name, section_name="", bar=None):
    """The picture's block payload. `bar` is (splitter name, index) of a
    picked fixed shelf or division."""
    def paint(shader, font_id, rect, mx, my, s):
        _paint(shader, font_id, rect, mx, my, s, host_name, section_name, bar)

    def hit(context, rect, mx, my):
        _hit(context, rect, mx, my, host_name, section_name)
    return {'height': CANVAS_H, 'paint': paint, 'hit': hit}


def _paint(shader, font_id, rect, mx, my, s, host_name, section_name, bar):
    draw_rect(shader, *rect, Theme.PANEL_BG)
    laid = _layout(host_name, rect, s)
    if laid is None:
        return
    host, frame, ibox, view = laid
    draw_rect(shader, *view.rect(ibox), OPENING_FILL)
    regions = _regions(host)
    splits = splits_of(host, frame)
    bar_hover = _bar_at(splits, view, mx, my, s)
    hover = (None if bar_hover is not None
             else _region_at(frame, view, regions, mx, my))
    for region in regions:
        box = frame.cage_box(region)
        if box is None:
            continue
        r = view.rect(box)
        if region is hover:
            draw_rect(shader, *r, Theme.ROW_HOVER_BG)
        draw_rect_outline(shader, *r, Theme.PANEL_BORDER)
    for part in _parts(host):
        box = frame.part_box(part)
        if box is None:
            continue
        if is_bar_part(part):
            color = BAR_FILL
        elif part.get('IS_DRAWER_BOX'):
            color = BOX_FILL
        else:
            color = PART_FILL
        r = view.rect(box, min_px=2.0 * s)
        draw_rect(shader, *r, color)
        if part.get('IS_DRAWER_BOX'):
            draw_rect_outline(shader, *r, BAR_FILL)
    picked = None
    for sp in splits:
        r = view.rect(sp['bar'], min_px=3.0 * s)
        if sp is bar_hover:
            draw_rect(shader, *r, BAR_HOVER)
        elif sp['part'] is None:
            draw_rect(shader, *r, Theme.PANEL_BORDER)
        if bar and sp['splitter'].name == bar[0] and sp['index'] == bar[1]:
            picked = sp
    if picked is not None:
        x, y, w, h = view.rect(picked['bar'], min_px=4.0 * s)
        draw_rect_outline(shader, x, y, w, h, PICK_LINE)
        draw_rect_outline(shader, x - s, y - s, w + 2 * s, h + 2 * s, PICK_LINE)
        _paint_position(font_id, rect, picked, x, y, w, h, s)
    section = bpy.data.objects.get(section_name) if section_name else None
    if picked is None:
        box = frame.cage_box(section) if section is not None else ibox
        if box is not None:
            x, y, w, h = view.rect(box)
            draw_rect_outline(shader, x, y, w, h, PICK_LINE)
            draw_rect_outline(shader, x + s, y + s, w - 2 * s, h - 2 * s,
                              PICK_LINE)
    if regions and picked is None and section is None:
        text = "Click a section, or drag a shelf or division"
        size = 11 * s
        draw_text(font_id, rect[0] + 6 * s, rect[1] + 5 * s, size,
                  Theme.TEXT_DIM, fit_text(font_id, size, text, rect[2] - 12 * s))


def _paint_position(font_id, rect, picked, x, y, w, h, s):
    try:
        us = bpy.context.scene.unit_settings
        text = units.unit_to_string(
            us, split_position(picked['splitter'], picked['index']))
    except Exception:
        return
    size = 11 * s
    if picked['axis'] == 'H':
        tx, ty = x + 6 * s, y + h + 4 * s
    else:
        tx, ty = x + w + 5 * s, y + 6 * s
    tx = min(tx, rect[0] + rect[2] - 60 * s)
    ty = min(ty, rect[1] + rect[3] - size - 2 * s)
    draw_text(font_id, tx, ty, size, PICK_LINE, text)


def _hit(context, rect, mx, my, host_name, section_name):
    """A press in the picture. What it does waits for the release, as
    the panel's buttons do, so the release never reaches the viewport
    behind and click-selects whatever is under the panel."""
    from ...operators import options_panel
    global _pending_drag
    laid = _layout(host_name, rect, _s())
    target = ""
    if laid is not None:
        host, frame, _ibox, view = laid
        bar = _bar_at(splits_of(host, frame), view, mx, my, _s())
        if bar is not None:
            # Drag it to move it; let go without moving to pick it.
            _pending_drag = (bar['splitter'].name, bar['index'], bar['axis'],
                             view.k)
            try:
                bpy.ops.hb_frameless.drag_interior_split('INVOKE_DEFAULT')
                return
            except Exception as ex:
                _pending_drag = None
                print('Home Builder: split drag failed: %s' % ex)
        region = _region_at(frame, view, _regions(host), mx, my)
        if region is not None and region.name != section_name:
            target = region.name
    options_panel._run_on_release('hb_frameless.pick_interior_section',
                                  {'name': target})


# ---- What the page is on -----------------------------------------------------

def _visible(context, obj):
    try:
        return (obj is not None
                and context.view_layer.objects.get(obj.name) is not None
                and obj.visible_get())
    except ReferenceError:
        return False


def _anchor(context, host):
    """A visible object to stay the pick while the page is on a hidden
    section: the pick already made when it is in this host, else the
    host, a part in it, or its bay."""
    active = context.view_layer.objects.active
    if _visible(context, active) and (active is host or host_of(active) is host):
        return active
    candidates = [host] + _parts(host) + list(host.children_recursive)
    candidates.append(host.parent)
    return next((o for o in candidates if _visible(context, o)), None)


def pick(context, obj):
    """Make `obj` the pick, so the page follows it."""
    global _focus
    _focus = None
    for o in context.selected_objects:
        try:
            o.select_set(False)
        except RuntimeError:
            pass
    try:
        obj.select_set(True)
    except RuntimeError:
        pass
    context.view_layer.objects.active = obj


def focus(context, host, section=None):
    """Put the page on `section` of `host`'s interior (None: the whole
    interior) without making a hidden cage active."""
    global _focus
    anchor = _anchor(context, host)
    if anchor is None:
        pick(context, section or host)
        return
    pick(context, anchor)
    _focus = (anchor.name, host.name, section.name if section is not None else "")


def focused(context):
    """(host, section or None) the page is on in place of the active
    object, or None when the focus is gone."""
    global _focus
    if not _focus:
        return None
    anchor, host_name, section_name = _focus
    active = context.view_layer.objects.active
    host = bpy.data.objects.get(host_name)
    if active is None or active.name != anchor or host is None:
        _focus = None
        return None
    section = bpy.data.objects.get(section_name) if section_name else None
    if section is not None and host_of(section) is not host:
        section = None          # joined or gone: the whole interior
    return host, section


def clear_focus():
    global _focus
    _focus = None


# ---- The page -------------------------------------------------------------------

def _act(label, op_id, kwargs=None, icon=None):
    return (label, op_id, dict(kwargs or {}), None, 1.0, icon)


def _cmd(label, target, cmd, kind='', icon=None):
    return _act(label, 'hb_frameless.interior_page_cmd',
                {'target_name': target.name, 'cmd': cmd, 'kind': kind or 'NONE'},
                icon)


def _type_entries(target_name):
    from ...operators import generic_page

    def entries(_context):
        return [(label, 'hb_frameless.interior_page_cmd',
                 {'target_name': target_name, 'cmd': 'TYPE', 'kind': ident})
                for ident, label in generic_page._enum_items(
                    'hb_frameless.change_interior_type', 'interior_type')]
    return entries


def _register_schema():
    from ...operators import prop_proxy as P

    def found(obj):
        return obj.parent, bar_index(obj)

    def pos_get(obj):
        return split_position(*found(obj))

    def pos_set(obj, value):
        set_split_position(*found(obj), float(value))

    def size_get(side):
        def get(obj):
            s = _sizes(*found(obj))
            return s[2 + side] if s else 0.0
        return get

    def size_set(side):
        def set(obj, value):
            s = _sizes(*found(obj))
            if s is None:
                return
            now = s[2 + side]
            # Growing the upper / left side moves the board down / right.
            sign = 1.0 if (axis_of(obj.parent) == 'V') == (side == 0) else -1.0
            move_bar(obj.parent, bar_index(obj), sign * (float(value) - now))
        return set

    def hold_get(side):
        def get(obj):
            s = _sizes(*found(obj))
            return bool(s and not s[side].equal)
        return get

    def hold_set(side):
        def set(obj, value):
            s = _sizes(*found(obj))
            if s is not None:
                s[side].equal = not bool(value)
                _solve(obj.parent)
        return set

    def thick_get(obj):
        return float(obj.parent.get('Material Thickness', 0.0))

    def thick_set(obj, value):
        obj.parent['Material Thickness'] = float(value)
        _solve(obj.parent)

    P.register(SPLIT_SCHEMA, {
        'position': P.computed(pos_get, pos_set, unit='LENGTH', precision=4),
        'space_a': P.computed(size_get(0), size_set(0), unit='LENGTH', precision=4),
        'space_b': P.computed(size_get(1), size_set(1), unit='LENGTH', precision=4),
        'hold_a': P.computed(hold_get(0), hold_set(0), type='BOOLEAN'),
        'hold_b': P.computed(hold_get(1), hold_set(1), type='BOOLEAN'),
        'thickness': P.computed(thick_get, thick_set, unit='LENGTH', precision=4),
    })


def _bar_blocks(context, part):
    from ...operators import options_panel, prop_proxy
    splitter, index = part.parent, bar_index(part)
    is_h = axis_of(splitter) == 'H'
    names = ("Above", "Below") if is_h else ("Left", "Right")
    out = [('label', split_label(splitter))]
    out.extend(options_panel.field_blocks(context, (
        ('distance', 'position', "From Bottom" if is_h else "From Left"),
        ('distance', 'space_a', "Space %s" % names[0]),
        ('bool', 'hold_a', "Hold Space %s" % names[0]),
        ('distance', 'space_b', "Space %s" % names[1]),
        ('bool', 'hold_b', "Hold Space %s" % names[1]),
        ('distance', 'thickness', "Thickness"),
    ), prop_proxy.owner(part, SPLIT_SCHEMA)))
    out.append(('note', "Drag it in the picture to move it"))
    secs = sections_of(splitter)
    row = []
    if len(secs) >= 2:
        row.append(_cmd("Remove %s" % split_label(splitter), secs[index - 1],
                        'REMOVE', icon='delete'))
    for sec, name in zip(secs[index - 1:index + 1], names):
        row.append(_act("Space %s" % name, 'hb_frameless.pick_interior_section',
                        {'name': sec.name}))
    out.append(('actions', tuple(row)))
    return out


def _target_blocks(context, host, target):
    """The section (or the whole interior) the page is on: what it holds,
    its type, its settings, and splitting it."""
    from ...operators import generic_page
    from . import selected_card
    inner = interior_in(target)
    where = "section" if target.get(TAG_SECTION) else "interior"
    out = [('value', ("In this %s" % where, selected_card._interior_summary(inner)))]
    out.append(('actions', (
        ("Change Interior  ›", _type_entries(target.name), None, None, 1.0, None),)))
    if inner is not None and not is_splitter(inner):
        out.extend(generic_page.prompt_blocks(
            context, inner, 'fl_interior_prompts', "Interior Settings"))
    out.append(('gap', None))
    out.append(('label', "Split this %s" % where))
    row = [_cmd("Fixed Shelf", target, 'SPLIT', 'FIXED_SHELF', icon='cab_split_h'),
           _cmd("Division", target, 'SPLIT', 'DIVISION', icon='cab_split_v')]
    if target.get(TAG_SECTION) and is_splitter(target.parent):
        row.append(_cmd("Remove %s" % split_label(target.parent), target,
                        'REMOVE', icon='delete'))
    out.append(('actions', tuple(row)))
    return out


def page_target(pick_obj, host):
    """What a pick edits: a board (its part), a section, or the host."""
    if pick_obj is None:
        return host
    if is_bar_part(pick_obj):
        return pick_obj
    return section_of(pick_obj) or host


def blocks(context, host, pick_obj):
    """The Interior page's blocks: the picture, then the pick's page.
    `pick_obj` is a part in the interior, a section, or None for the
    whole interior."""
    target = page_target(pick_obj, host)
    bar = (target.parent.name, bar_index(target)) if is_bar_part(target) else None
    section = target if target.get(TAG_SECTION) else None
    out = [('canvas', canvas(host.name, section.name if section else "", bar))]
    if bar is not None:
        out.extend(_bar_blocks(context, target))
    elif section is None and has_splits(host):
        out.append(('note', "This interior is split: click a section"))
    else:
        out.extend(_target_blocks(context, host, target))
    out.append(('gap', None))
    row = [_act("Opening", 'hb_frameless.show_interior_page',
                {'opening_name': ""})]
    out.append(('actions', tuple(row)))
    return out


# ---- Commands --------------------------------------------------------------------

def _redraw(context):
    screen = getattr(context, 'screen', None)
    for area in screen.areas if screen else ():
        if area.type == 'VIEW_3D':
            area.tag_redraw()


class hb_frameless_OT_show_interior_page(bpy.types.Operator):
    """Edit this opening's interior on a picture of it"""
    bl_idname = "hb_frameless.show_interior_page"
    bl_label = "Edit Interior"
    bl_options = {'INTERNAL'}

    opening_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        if self.opening_name:
            host = bpy.data.objects.get(self.opening_name)
            if host is None:
                return {'CANCELLED'}
            focus(context, host)
        else:
            # Back to the Opening page
            found = focused(context)
            active = context.view_layer.objects.active
            host = found[0] if found else host_of(active)
            clear_focus()
            if host is not None and _visible(context, host):
                pick(context, host)
            elif host is not None:
                bpy.ops.hb_frameless.select_level(name=host.name, level='Openings')
        _redraw(context)
        return {'FINISHED'}


class hb_frameless_OT_pick_interior_section(bpy.types.Operator):
    """Pick this section of the interior"""
    bl_idname = "hb_frameless.pick_interior_section"
    bl_label = "Pick Section"
    bl_options = {'INTERNAL'}

    name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.name) if self.name else None
        if obj is None:
            return {'CANCELLED'}     # a press on nothing: just taken
        host = host_of(obj)
        if obj.get(TAG_SECTION) and host is not None:
            focus(context, host, obj)
        else:
            pick(context, obj)
        _redraw(context)
        return {'FINISHED'}


class hb_frameless_OT_interior_page_cmd(bpy.types.Operator):
    """Split this section with a fixed shelf or a division, take its
    split out, or change what it holds"""
    bl_idname = "hb_frameless.interior_page_cmd"
    bl_label = "Change Interior"
    bl_options = {'UNDO', 'INTERNAL'}

    target_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})  # type: ignore
    cmd: bpy.props.EnumProperty(items=(('SPLIT', "Split", ""),
                                       ('REMOVE', "Remove", ""),
                                       ('TYPE', "Type", "")),
                                options={'SKIP_SAVE'})  # type: ignore
    kind: bpy.props.StringProperty(default="NONE", options={'SKIP_SAVE'})  # type: ignore

    def execute(self, context):
        from .operators import ops_interior
        target = bpy.data.objects.get(self.target_name)
        host = host_of(target) if target is not None else None
        if host is None:
            self.report({'WARNING'}, "Pick an opening or section first")
            return {'CANCELLED'}
        keep = section_of(target)
        if self.cmd == 'SPLIT':
            if self.kind not in ops_interior.SPLIT_KINDS:
                return {'CANCELLED'}
            inner = interior_in(target)
            if inner is not None and is_splitter(inner):
                self.report({'WARNING'}, "Pick a section to split")
                return {'CANCELLED'}
            if inner is not None:
                splitter = ops_interior.split_interior(context, inner, self.kind)
            else:
                splitter = ops_interior.split_host(context, target, self.kind)
            secs = sections_of(splitter) if splitter is not None else []
            # The new lower or left side
            if secs:
                keep = secs[-1] if self.kind == 'FIXED_SHELF' else secs[0]
        elif self.cmd == 'REMOVE':
            if target.get(TAG_SECTION) is None or not is_splitter(target.parent):
                return {'CANCELLED'}
            outer = target.parent.parent
            ops_interior.remove_interior_split(context, target)
            keep = outer if outer is not None and outer.get(TAG_SECTION) else None
        else:
            with context.temp_override(object=target, active_object=target,
                                       selected_objects=[target]):
                result = bpy.ops.hb_frameless.change_interior_type(
                    'EXEC_DEFAULT', interior_type=self.kind)
            if 'FINISHED' not in result:
                return {'CANCELLED'}
            keep = target if target.get(TAG_SECTION) else None
        focus(context, host, keep if keep is not None and keep.name in bpy.data.objects
              else None)
        _redraw(context)
        return {'FINISHED'}


class hb_frameless_OT_drag_interior_split(bpy.types.Operator):
    """Drag a fixed shelf or division to move it; let go without moving
    to pick it. Esc or right-click puts it back"""
    bl_idname = "hb_frameless.drag_interior_split"
    bl_label = "Move Interior Split"
    bl_options = {'UNDO', 'INTERNAL'}

    def invoke(self, context, event):
        global _pending_drag
        pending, _pending_drag = _pending_drag, None
        if pending is None:
            return {'CANCELLED'}
        self.splitter_name, self.index, self.axis, self.k = pending
        splitter = bpy.data.objects.get(self.splitter_name)
        found = _sizes(splitter, self.index) if splitter is not None else None
        if found is None or self.k <= 0:
            return {'CANCELLED'}
        self.start = (found[2], found[3])
        self.start_equal = (found[0].equal, found[1].equal)
        self.press = (event.mouse_x, event.mouse_y)
        self.dragging = False
        self.cancelled = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def restore(self):
        splitter = bpy.data.objects.get(self.splitter_name)
        found = _sizes(splitter, self.index) if splitter is not None else None
        if found is None:
            return
        for p, size, eq in zip(found[:2], self.start, self.start_equal):
            p.equal = eq
            p.distance_value = size
        _solve(splitter)

    def modal(self, context, event):
        if self.cancelled:
            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                return {'CANCELLED'}
            return {'RUNNING_MODAL'}
        if event.type in {'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE'}:
            dx = event.mouse_x - self.press[0]
            dy = event.mouse_y - self.press[1]
            delta = dx if self.axis == 'V' else dy
            if not self.dragging:
                if abs(delta) < 3:
                    return {'RUNNING_MODAL'}
                self.dragging = True
            splitter = bpy.data.objects.get(self.splitter_name)
            if splitter is not None:
                move_bar(splitter, self.index, delta / self.k, start=self.start)
                _redraw(context)
            return {'RUNNING_MODAL'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if not self.dragging:
                splitter = bpy.data.objects.get(self.splitter_name)
                part = bar_part(splitter, self.index) if splitter else None
                if part is not None and _visible(context, part):
                    pick(context, part)
                _redraw(context)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            if self.dragging:
                self.restore()
            _redraw(context)
            self.cancelled = True
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}


classes = (hb_frameless_OT_show_interior_page,
           hb_frameless_OT_pick_interior_section,
           hb_frameless_OT_interior_page_cmd,
           hb_frameless_OT_drag_interior_split)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    _register_schema()


def unregister():
    global _focus
    _focus = None
    try:
        from ...operators import prop_proxy
        prop_proxy.unregister(SPLIT_SCHEMA)
    except Exception:
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
