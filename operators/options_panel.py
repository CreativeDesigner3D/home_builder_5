"""OPTIONS tab for the viewport panel -- the active library's settings.

Every product library keeps its settings as ``draw_*_ui(layout,
context)`` methods on its own scene property group, and each names the
ones worth reaching for as ``OPTION_FORMS`` on its catalog. This tab
lists whichever library the scene is set to, so switching library
switches what the tab offers -- the same way the browser beside it
switches what it places.

A section is reached one of two ways:

* **Pages** -- a catalog can name a section in ``OPTION_PAGES``, and
  then its row is a header that folds open in place, the way the
  library's category headers do: the section's list, fields and
  commands unfold beneath it as GPU widgets, and a second click folds
  them away. Nothing replaces the tab, so nothing has to be backed out
  of. A dropdown is a value button that pops a native menu at the
  cursor; a checkbox is a row that flips a bool. Nothing opens a
  dialog.
* **Forms** -- a section without a page is a row opening a native popup
  that calls the library's own draw method: the sidebar's UI, verbatim.
  This is the fallback while the pages are built out section by
  section.

A ``pool`` page is a named list you pick from, add to and assign (the
cabinet styles), with the active item's fields and commands below it.
A ``form`` page is fields on the library's own property group (the
handles). The face frame library draws its pool at the root of the tab
instead of under a header, because that pool is reached for mid-design;
the drawing code is the same either way.

Field kinds: ``enum`` (a dropdown), ``bool`` (a checkbox), ``distance``
(a value you click into and type, in the placement typing grammar),
``thumb`` (an enum picked from a grid of pictures -- see thumb_picker)
and ``gap`` (space). A field may carry a dict after its label: ``when``
hides it unless the callable, given the owner, says so; ``thumb`` maps
a choice to its picture.
"""

import bpy

from .. import units
from .. import hb_placement
from ..hb_gpu_draw import (
    draw_rect,
    draw_rects,
    draw_text,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    begin_clip,
    end_clip,
    ScrollList,
    scale,
    text_width,
    fit_text,
    draw_centered_text,
    paint_button,
    glyph_plus,
    glyph_chevron,
    glyph_caret,
    paint_field,
    paint_check,
    enum_items,
    enum_label,
    InlineEdit,
)

PREFERRED_WIDTH = 300       # unscaled

# ---- Layout (unscaled px) --------------------------------------------------
ROW_H = 22
ROW_GAP = 2
SECTION_H = 20          # tall enough to carry a button on the right
NEW_BTN_H = 16          # the + NEW chip inside a section header
NEW_BTN_PAD = 6         # its gap from the header text and the edge
GROUP_GAP = 8
BTN = 18
PAD = 4
FONT = 10
ACCENT_W = 3
GEAR = 18           # the per-style settings button on a row
ARROW = 14          # a move up / move down chip on the active row
ARROW_GAP = 2       # between the two chips and the settings button
PLUS_SPAN = 8       # full width of the plus mark, not half
PLUS_GAP = 4        # plus mark to the word NEW
INDENT = 8          # an unfolded section's content, in from its header

# Commands that act on the active face frame style. Drawn as buttons
# rather than hidden in a popup: these are the things you DO with a
# style, and the painting ones want to be one click from the list.
#
# Three, not the sidebar's seven. Assign, Update and Reset stay in the
# sidebar, which still has all of them; the style's own settings are
# behind the menu glyph on its row, so a button for them here would be
# a second door onto the same thing. What is left is the three brushes,
# named for what each one paints: the whole cabinet, one part's finish,
# one part's interior.
ACTIONS = (
    (("Paint Cabinet", "hb_face_frame.paint_assign_cabinet_style",
      None, None),
     ("Paint Part", "hb_face_frame.paint_part_material", "brush", "FINISH"),
     ("Paint Interior", "hb_face_frame.paint_part_material",
      "brush", "INTERIOR")),
)


def form_sections(context):
    """((label, draw method name), ...) for the library the scene is set
    to -- the catalog's OPTION_FORMS, empty for a library that names
    none."""
    from . import library_panel
    cat = library_panel.active_catalog(context)
    return tuple(getattr(cat, 'OPTION_FORMS', ()) or ()) if cat else ()


def page_specs(context):
    """{draw method name: page spec} for the active library -- the
    catalog's OPTION_PAGES, empty for a library that names none."""
    from . import library_panel
    cat = library_panel.active_catalog(context)
    return dict(getattr(cat, 'OPTION_PAGES', None) or {}) if cat else {}


def has_style_list(context):
    """Whether this library's style pool is drawn at the tab's root.
    Only the face frame library's is; the others reach theirs through a
    page or a form row like any other setting."""
    from . import library_panel
    return library_panel.active_tab(context) == 'FACE FRAME'


_list = ScrollList(bar_width=4, bar_pad=4, min_rows=3)
# Inline rename, keyed by style index -- the same field the scene
# navigator renames rooms with, so the two lists behave alike. The pool
# being renamed is remembered beside it, since the key alone does not
# say which list the index counts.
_edit = InlineEdit()
_edit_pool = None
# Inline value typing for a distance field, keyed by (ID, path, prop).
_value_edit = InlineEdit()


# ---- Typed-distance parsing (borrowed from PlacementMixin) --------------
# The same grammar the placement tools and the size labels accept:
# inches, fractions, feet'inches". Lent to a holder class so the parser
# comes without the placement state machine.

class _DistanceParser:
    parse_typed_distance = hb_placement.PlacementMixin.parse_typed_distance
    _parse_feet_inches = hb_placement.PlacementMixin._parse_feet_inches
    _extract_number = hb_placement.PlacementMixin._extract_number
    _number_to_scene_units = hb_placement.PlacementMixin._number_to_scene_units
    typed_value = ""


_parser = _DistanceParser()


def parse_distance(text):
    """Typed string -> metres, or None."""
    try:
        return _parser.parse_typed_distance(text)
    except Exception:
        return None


def _field_parts(field):
    """(kind, prop, label, options) from a field tuple, options being the
    optional trailing dict."""
    kind, prop, label = field[0], field[1], field[2]
    options = field[3] if len(field) > 3 and isinstance(field[3], dict) else {}
    return kind, prop, label, options


def _field_shown(field, owner):
    when = _field_parts(field)[3].get('when')
    if when is None:
        return True
    try:
        return bool(when(owner))
    except Exception:
        return True


def _owner_key(owner, prop):
    try:
        return (owner.id_data, owner.path_from_id(), prop)
    except Exception:
        return None


# ---- Pools -------------------------------------------------------------------

def _main_group(name, context):
    """A property group on the MAIN scene. Style pools are project-
    global -- every room sees the same set -- so they live there rather
    than on whichever room is open."""
    from .. import hb_project
    try:
        main = hb_project.get_main_scene(context)
    except TypeError:
        main = hb_project.get_main_scene()
    if main is None:
        main = context.scene
    return getattr(main, name, None)


def _norm_action(action):
    """(label, operator, prop, value) from either the four-tuple the
    face frame actions use or a catalog's (label, operator) pair."""
    if len(action) >= 4:
        return tuple(action[:4])
    label, op = action[0], action[1]
    return (label, op, None, None)


class PoolSpec:
    """A named pool: what it is called, where it lives, what acts on it.

    `props` is the name of the scene property group holding the
    collection; `fields` are (kind, property, label) drawn for the
    active item; `actions` are rows of commands; `scene_fields` are
    fields of the same shape on the ROOM's copy of the group -- a
    setting that belongs to the section but not to any one item. Any
    operator left None simply leaves that control out.
    """

    def __init__(self, title, props, collection, index, add_op=None,
                 remove_op=None, duplicate_op=None, move_op=None,
                 settings_op=None, fields=(), actions=(), scene_fields=()):
        self.title = title
        self.props = props
        self.collection = collection
        self.index = index
        self.add_op = add_op
        self.remove_op = remove_op
        self.duplicate_op = duplicate_op
        self.move_op = move_op
        self.settings_op = settings_op
        self.fields = tuple(fields)
        self.actions = tuple(tuple(_norm_action(a) for a in row)
                             for row in actions)
        self.scene_fields = tuple(scene_fields)

    def owner(self, context):
        return _main_group(self.props, context)

    def scene_owner(self, context):
        """The room's own copy of the group, for scene_fields."""
        return getattr(context.scene, self.props, None)

    def items(self, context):
        owner = self.owner(context)
        return list(getattr(owner, self.collection, ()) or ()) if owner else []

    def active_index(self, context):
        owner = self.owner(context)
        return int(getattr(owner, self.index, -1) or 0) if owner else -1

    def set_active(self, context, i):
        owner = self.owner(context)
        if owner is not None and getattr(owner, self.index, None) != i:
            setattr(owner, self.index, i)

    def active(self, context):
        items = self.items(context)
        i = self.active_index(context)
        return items[i] if 0 <= i < len(items) else None


def _pool_from_spec(spec):
    return PoolSpec(
        title=spec.get('title', "Styles"),
        props=spec['props'],
        collection=spec['collection'],
        index=spec['index'],
        add_op=spec.get('add_op'),
        remove_op=spec.get('remove_op'),
        duplicate_op=spec.get('duplicate_op'),
        move_op=spec.get('move_op'),
        settings_op=spec.get('settings_op'),
        fields=spec.get('fields', ()),
        actions=spec.get('actions', ()),
        scene_fields=spec.get('scene_fields', ()),
    )


# The face frame pool, drawn at the root of the tab. Its per-style
# settings are behind the glyph on each row (a dialog, until that
# library gets a page of its own).
FF_POOL = PoolSpec(
    title="Cabinet Styles",
    props='hb_face_frame',
    collection='cabinet_styles',
    index='active_cabinet_style_index',
    add_op='hb_face_frame.add_cabinet_style',
    move_op='hb_face_frame.move_cabinet_style',
    settings_op='home_builder.cabinet_style_settings',
    actions=ACTIONS,
)


def _style_props(context):
    """The face frame style pool (it lives on the main scene)."""
    return FF_POOL.owner(context)


def cabinet_styles(context):
    return FF_POOL.items(context)


def active_style_index(context):
    return FF_POOL.active_index(context)


# ---- Sections ----------------------------------------------------------------
# Which sections are unfolded, keyed by (product tab, draw method) so a
# section left open on one library does not open a same-named one on
# another. Session state, like the library grid's folded categories.

_expanded = set()


def _section_key(context, method):
    from . import library_panel
    return (library_panel.active_tab(context), method)


def toggle_section(context, method):
    key = _section_key(context, method)
    if key in _expanded:
        _expanded.discard(key)
    else:
        _expanded.add(key)
    _tag()


def section_expanded(context, method):
    return _section_key(context, method) in _expanded


def _pool_blocks(context, pool):
    """The blocks of one pool: its list, the active item's fields, and
    the commands that act on it."""
    blocks = [('head', ("Styles", pool.add_op is not None, pool))]
    active = pool.active_index(context)
    for i, item in enumerate(pool.items(context)):
        blocks.append(('style', (i, item.name, i == active, pool)))
    item = pool.active(context)
    if item is not None and pool.fields:
        blocks.append(('gap', None))
        for field in pool.fields:
            blocks.append(('field', (field, item)))
    if pool.actions:
        blocks.append(('gap', None))
        for row in pool.actions:
            blocks.append(('actions', row))
    edit_row = [(label, op, None, None)
                for label, op in (("Duplicate", pool.duplicate_op),
                                  ("Delete", pool.remove_op))
                if op]
    if edit_row:
        blocks.append(('actions', tuple(edit_row)))
    scene_owner = pool.scene_owner(context) if pool.scene_fields else None
    if scene_owner is not None:
        blocks.append(('gap', None))
        for field in pool.scene_fields:
            blocks.append(('field', (field, scene_owner)))
    return blocks


def _form_blocks(context, spec):
    """The blocks of one form: its fields on the library's group, and
    the commands under them."""
    group = spec.get('props')
    if spec.get('scope', 'main') == 'scene':
        owner = getattr(context.scene, group, None)
    else:
        owner = _main_group(group, context)
    if owner is None:
        return []
    blocks = []
    for field in spec.get('fields', ()):
        if field[0] == 'gap':
            blocks.append(('gap', None))
            continue
        if field[0] == 'label':
            blocks.append(('label', field[2]))
            continue
        if field[0] == 'actions':
            # A row of commands placed among the fields, so a form can
            # group its commands under the label they belong to.
            blocks.append(('actions', tuple(_norm_action(a) for a in field[1])))
            continue
        if _field_shown(field, owner):
            blocks.append(('field', (field, owner)))
    actions = spec.get('actions', ())
    if actions:
        blocks.append(('gap', None))
        for row in actions:
            blocks.append(('actions', tuple(_norm_action(a) for a in row)))
    return blocks


# ---- Provider interface ----------------------------------------------------

def _blocks(context):
    """The tab's content as (kind, payload) blocks, top to bottom."""
    blocks = []
    if has_style_list(context):
        # The header carries New rather than a full-width row of its own:
        # it is the one command that makes a list item, so it belongs to
        # the list's caption, not to the stack of commands that act on a
        # style.
        blocks.append(('head', ("Cabinet Styles", True, FF_POOL)))
        active = FF_POOL.active_index(context)
        for i, style in enumerate(FF_POOL.items(context)):
            blocks.append(('style', (i, style.name, i == active, FF_POOL)))
        for row in FF_POOL.actions:
            blocks.append(('actions', row))
        blocks.append(('gap', None))
    blocks.append(('head', ("Options", False, None)))
    pages = page_specs(context)
    for label, method in form_sections(context):
        spec = pages.get(method)
        kind = spec.get('kind') if spec else None
        if kind not in ('pool', 'form'):
            blocks.append(('form', (label, method)))
            continue
        expanded = section_expanded(context, method)
        blocks.append(('section', (label, method, expanded)))
        if expanded:
            if kind == 'pool':
                inner = _pool_blocks(context, _pool_from_spec(spec))
            else:
                inner = _form_blocks(context, spec)
            blocks.extend(('indent', b) for b in inner)
            blocks.append(('gap', None))
    return blocks


def build(rect, context):
    """Rows inside `rect`. Entries:

        ('section_row', label, method_name, rect, expanded)
        ('styles_head', label, rect, add_rect, pool)   add_rect None on most
        ('style_row', index, name, rect, is_active, gear_rect,
                      up_rect, down_rect, pool)
        ('field_row', kind, prop, label, owner, value, rect, value_rect)
        ('action_btn', label, op_id, prop, value, rect)
        ('form_row', label, method_name, rect)
        ('styles_clip', clip_rect, track, thumb)
    """
    s = scale()
    x0, bottom, w, h = rect
    row_h = ROW_H * s
    sect_h = SECTION_H * s
    gap = ROW_GAP * s

    blocks = _blocks(context)

    def _h(block):
        kind = block[0]
        if kind == 'indent':
            return _h(block[1])
        if kind in ('head', 'section'):
            return sect_h
        if kind == 'gap':
            return GROUP_GAP * s
        return row_h + gap

    content_h = sum(_h(b) for b in blocks)
    list_h, _scrollable, reserve = _list.measure(content_h, h, row_h)
    _list.clamp(content_h, list_h)
    top = bottom + h
    track, thumb = _list.bar_rects(x0, w, top, list_h, content_h, row_h)
    full_w = w - reserve

    entries = [('styles_clip', (x0, top - list_h, w, list_h), track, thumb)]
    for block, block_top, _bb in _list.visible(blocks, top, top - list_h, _h):
        kind, payload = block
        # Content under an unfolded section steps in from its header,
        # so the eye can tell what belongs to it.
        x, row_w = x0, full_w
        if kind == 'indent':
            kind, payload = payload
            x, row_w = x0 + INDENT * s, full_w - INDENT * s
        if kind == 'gap':
            continue
        if kind == 'section':
            label, method, expanded = payload
            entries.append(('section_row', label, method,
                            (x, block_top - sect_h, row_w, sect_h), expanded))
        elif kind == 'label':
            entries.append(('label_row', payload,
                            (x, block_top - row_h, row_w, row_h)))
        elif kind == 'head':
            label, with_add, pool = payload
            head_rect = (x, block_top - sect_h, row_w, sect_h)
            add_rect = None
            if with_add:
                bw = (NEW_BTN_PAD * s + PLUS_SPAN * s + PLUS_GAP * s
                      + text_width(0, FONT * s, "NEW") + NEW_BTN_PAD * s)
                bh = NEW_BTN_H * s
                add_rect = (x + row_w - bw, block_top - sect_h + (sect_h - bh) / 2.0,
                            bw, bh)
            entries.append(('styles_head', label, head_rect, add_rect, pool))
        elif kind == 'style':
            i, name, is_active, pool = payload
            rect = (x, block_top - row_h, row_w, row_h)
            gear_rect = None
            right = x + row_w - 2 * s
            if pool.settings_op:
                gear = GEAR * s
                gear_rect = (right - gear,
                             block_top - row_h + (row_h - gear) / 2.0,
                             gear, gear)
                right = gear_rect[0]
            # Move up / move down, on the ACTIVE row only. Order is what
            # the list means -- the first style is the one drawings leave
            # white -- so the control belongs on the row, but two more
            # glyphs on every row would crowd a list that is mostly read.
            # Both slots stay reserved at the ends of the list so the
            # remaining chip does not slide sideways.
            up_rect = down_rect = None
            count = len(pool.items(context))
            if pool.move_op and is_active and count > 1:
                aw = ARROW * s
                ay = block_top - row_h + (row_h - aw) / 2.0
                dx = right - ARROW_GAP * s - aw
                if i > 0:
                    up_rect = (dx - aw, ay, aw, aw)
                if i < count - 1:
                    down_rect = (dx, ay, aw, aw)
            entries.append(('style_row', i, name, rect, is_active,
                            gear_rect, up_rect, down_rect, pool))
        elif kind == 'actions':
            n = len(payload)
            bw = (row_w - gap * (n - 1)) / n
            for j, (label, op_id, prop, value) in enumerate(payload):
                entries.append((
                    'action_btn', label, op_id, prop, value,
                    (x + j * (bw + gap), block_top - row_h, bw, row_h)))
        elif kind == 'field':
            field, owner = payload
            fkind, prop, label, options = _field_parts(field)
            rect = (x, block_top - row_h, row_w, row_h)
            lw = row_w * 0.42
            value_rect = (x + lw, rect[1] + 2 * s, row_w - lw,
                          row_h - 4 * s)
            if fkind == 'bool':
                value = bool(getattr(owner, prop, False))
                value_rect = rect
            elif fkind == 'distance':
                key = _owner_key(owner, prop)
                if _value_edit.editing(key):
                    value = _value_edit.text + "|"
                else:
                    value = units.unit_to_string(
                        context.scene.unit_settings,
                        float(getattr(owner, prop, 0.0) or 0.0))
            else:
                value = enum_label(owner, prop)
            entries.append(('field_row', fkind, prop, label, owner, value,
                            rect, value_rect, options))
        elif kind == 'form':
            label, method = payload
            entries.append(('form_row', label, method,
                            (x, block_top - row_h, row_w, row_h)))
    return entries


def _clip(entries):
    for entry in entries or ():
        if entry[0] == 'styles_clip':
            return entry
    return None


def _paint_head(shader, font_id, s, mx, my, label, rect, add_rect):
    rx, ry, rw, rh = rect
    draw_text(font_id, rx, ry + rh * 0.32, FONT * s,
              Theme.TEXT_HEADER, label.upper())
    # The rule stops short of the button rather than running under
    # it -- a line crossing a control reads as a mistake.
    rule_w = rw if add_rect is None else add_rect[0] - rx - PAD * s
    draw_rects(shader, [(rx, ry, max(rule_w, 0.0), 1 * s)],
               Theme.SEPARATOR)
    if add_rect is not None:
        hot = point_in_rect(mx, my, add_rect)
        paint_button(shader, add_rect, hovered=hot)
        ax, ay, aw, ah = add_rect
        # glyph_plus takes the FULL span, not a half -- half of it
        # renders as a blob rather than a plus.
        glyph_plus(shader,
                   ax + (NEW_BTN_PAD + PLUS_SPAN / 2.0) * s,
                   ay + ah / 2.0, PLUS_SPAN * s,
                   Theme.GLYPH_HOVER if hot else Theme.GLYPH)
        draw_text(font_id,
                  ax + (NEW_BTN_PAD + PLUS_SPAN + PLUS_GAP) * s,
                  ay + ah * 0.26, FONT * s,
                  Theme.TEXT_PRIMARY if hot else Theme.TEXT_NORMAL,
                  "NEW")


def paint(entries, mx, my):
    import gpu
    s = scale()
    font_id = 0
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    clip = _clip(entries)
    if clip is not None and clip[2] is not None:
        draw_rect(shader, *clip[2], Theme.SCROLLBAR_TRACK)
        draw_rect(shader, *clip[3], Theme.SCROLLBAR_THUMB)

    clipped = clip is not None
    prev = begin_clip(clip[1]) if clipped else None
    try:
        for entry in entries:
            kind = entry[0]
            if kind == 'section_row':
                # A header that folds: the library's category headers,
                # so the two panels fold the same way. Chevron on the
                # left pointing right when folded, down when open.
                _, label, _method, rect, expanded = entry
                rx, ry, rw, rh = rect
                hot = point_in_rect(mx, my, rect)
                if hot:
                    draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
                glyph_chevron(shader, rx + 6 * s, ry + rh / 2.0, 7 * s,
                              not expanded,
                              Theme.GLYPH_HOVER if hot else Theme.GLYPH)
                draw_text(font_id, rx + 16 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY if (expanded or hot)
                          else Theme.TEXT_NORMAL,
                          fit_text(font_id, FONT * s, label, rw - 20 * s))
                draw_rects(shader, [(rx, ry, rw, 1 * s)], Theme.SEPARATOR)
            elif kind == 'label_row':
                # A caption inside a form: the small header style, so it
                # reads as a group name and not as a value.
                _, label, rect = entry
                rx, ry, rw, rh = rect
                draw_text(font_id, rx + 8 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_HEADER, label.upper())
            elif kind == 'styles_head':
                _, label, rect, add_rect, _pool = entry
                _paint_head(shader, font_id, s, mx, my, label, rect, add_rect)
            elif kind == 'style_row':
                (_, _i, name, rect, is_active, gear_rect,
                 up_rect, down_rect, pool) = entry
                arrows = is_active and (up_rect is not None
                                        or down_rect is not None)
                arrow_room = (2 * ARROW + ARROW_GAP) * s if arrows else 0.0
                gear_room = GEAR * s if gear_rect is not None else 0.0
                hovered = point_in_rect(mx, my, rect)
                rx, ry, rw, rh = rect
                renaming = _edit.editing(_i) and _edit_pool is pool
                if hovered and not renaming:
                    draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
                if is_active:
                    draw_rects(shader, [(rx, ry + 2 * s, ACCENT_W * s,
                                         rh - 4 * s)], Theme.ACCENT_BG)
                text_x = rx + (ACCENT_W + 8) * s
                if renaming:
                    # The row becomes the field. A caret marks the end of
                    # the text so it reads as editable rather than
                    # selected -- the navigator's rename looks the same.
                    field_w = (rw - gear_room - arrow_room - 12 * s
                               - (text_x - rx))
                    draw_rects(shader, [(text_x - 3 * s, ry + 3 * s,
                                         field_w + 6 * s, rh - 6 * s)],
                               (0.0, 0.0, 0.0, 0.55))
                    shown = fit_text(font_id, FONT * s, _edit.text + "|",
                                     field_w)
                else:
                    shown = fit_text(font_id, FONT * s, name,
                                     rw - gear_room - arrow_room - 16 * s)
                draw_text(font_id, text_x, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY if (is_active or renaming)
                          else Theme.TEXT_NORMAL, shown)
                if gear_rect is not None:
                    # Settings glyph: three bars, matching the library's.
                    gx, gy, gw, gh = gear_rect
                    g_hot = point_in_rect(mx, my, gear_rect)
                    if g_hot:
                        paint_button(shader, gear_rect, hovered=True)
                    for k in range(3):
                        draw_rects(shader, [(gx + 4 * s,
                                             gy + gh * (0.32 + k * 0.18),
                                             gw - 8 * s, 1.4 * s)],
                                   Theme.GLYPH_HOVER if g_hot else Theme.GLYPH)
                for a_rect, up in ((up_rect, True), (down_rect, False)):
                    if a_rect is None:
                        continue
                    a_hot = point_in_rect(mx, my, a_rect)
                    if a_hot:
                        paint_button(shader, a_rect, hovered=True)
                    ax, ay, aw, ah = a_rect
                    glyph_caret(shader, ax + aw / 2.0, ay + ah / 2.0,
                                7 * s, up,
                                Theme.GLYPH_HOVER if a_hot else Theme.GLYPH)
            elif kind == 'field_row':
                (_, fkind, prop, label, owner, value, rect, value_rect,
                 options) = entry
                hot = point_in_rect(mx, my, value_rect)
                if fkind == 'bool':
                    paint_check(shader, font_id, rect, FONT * s, label,
                                bool(value), point_in_rect(mx, my, rect))
                elif fkind == 'distance':
                    editing = _value_edit.editing(_owner_key(owner, prop))
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, caret=False, active=editing)
                elif fkind == 'thumb':
                    # The current pick's picture rides in the button,
                    # in front of its name.
                    from . import thumb_picker
                    thumb_fn = options.get('thumb')
                    png = None
                    if thumb_fn is not None:
                        try:
                            png = thumb_fn(getattr(owner, prop, ''))
                        except Exception:
                            png = None
                    tex = thumb_picker.texture(png) if png else None
                    vx, vy, vw, vh = value_rect
                    inset = (vh + 4 * s) if tex is not None else 0.0
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, text_inset=inset)
                    if tex is not None:
                        gpu.state.blend_set('ALPHA')
                        thumb_picker.draw_texture(
                            tex, (vx + 2 * s, vy + 1 * s, vh - 2 * s, vh - 2 * s))
                        shader.bind()
                else:
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot)
            elif kind == 'action_btn':
                _, label, _op, _prop, _val, rect = entry
                hovered = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hovered)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_PRIMARY if hovered
                                   else Theme.TEXT_NORMAL, label)
            elif kind == 'form_row':
                _, label, _method, rect = entry
                hovered = point_in_rect(mx, my, rect)
                if hovered:
                    draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
                rx, ry, rw, rh = rect
                draw_text(font_id, rx + 8 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_NORMAL,
                          fit_text(font_id, FONT * s, label, rw - 30 * s))
                # Chevron pointing right: this opens something.
                glyph_chevron(shader, rx + rw - 12 * s, ry + rh / 2.0,
                              7 * s, True, Theme.GLYPH)
    finally:
        if clipped:
            end_clip(prev)
    gpu.state.blend_set('NONE')


def _run(op_id, **kwargs):
    mod, name = op_id.split('.', 1)
    try:
        getattr(getattr(bpy.ops, mod), name)('INVOKE_DEFAULT', **kwargs)
    except Exception as ex:
        print('Home Builder: %s failed: %s' % (op_id, ex))


def hit(context, mx, my, entries):
    global _edit_pool
    clip = _clip(entries)
    if clip is not None and not point_in_rect(mx, my, clip[1]):
        return False
    for entry in entries:
        kind = entry[0]
        if kind == 'section_row' and point_in_rect(mx, my, entry[3]):
            toggle_section(context, entry[2])
            return True
        if kind == 'style_row':
            pool = entry[8]
            # The chips inside the row come first: a hit on one must not
            # also re-activate (or rename) the style underneath it. The
            # move operator acts on the active style, which is the only
            # row that carries the chips.
            for a_rect, direction in ((entry[6], 'UP'), (entry[7], 'DOWN')):
                if a_rect is not None and point_in_rect(mx, my, a_rect):
                    if pool.move_op:
                        _run(pool.move_op, direction=direction)
                    _tag()
                    return True
            # Gear next: it sits inside the row, so a hit there must
            # not also re-activate the style underneath it.
            if entry[5] is not None and point_in_rect(mx, my, entry[5]):
                if pool.settings_op:
                    _run(pool.settings_op, index=entry[1])
                return True
            if point_in_rect(mx, my, entry[3]):
                index = entry[1]
                if pool.active_index(context) != index:
                    pool.set_active(context, index)
                else:
                    # Clicking the style you are already on renames it,
                    # the same second click that renames a room.
                    _edit_pool = pool
                    _edit.begin(index, entry[2])
                    bpy.ops.home_builder.style_rename('INVOKE_DEFAULT')
                _tag()
                return True
        if kind == 'styles_head' and entry[3] is not None:
            if point_in_rect(mx, my, entry[3]):
                pool = entry[4]
                if pool is not None and pool.add_op:
                    _run(pool.add_op)
                _tag()
                return True
        if kind == 'field_row':
            (_, fkind, prop, label, owner, _value, rect, value_rect,
             options) = entry
            if fkind == 'bool' and point_in_rect(mx, my, rect):
                try:
                    setattr(owner, prop, not getattr(owner, prop))
                except Exception as ex:
                    print('Home Builder: %s failed: %s' % (prop, ex))
                _tag()
                return True
            if fkind == 'enum' and point_in_rect(mx, my, value_rect):
                open_enum_menu(context, owner, prop, label)
                return True
            if fkind == 'thumb' and point_in_rect(mx, my, value_rect):
                from . import thumb_picker
                thumb_fn = options.get('thumb')
                items = []
                for ident, item_label in enum_items(owner, prop):
                    png = None
                    if thumb_fn is not None:
                        try:
                            png = thumb_fn(ident)
                        except Exception:
                            png = None
                    items.append((ident, item_label, png))
                thumb_picker.open_picker(context, owner, prop, items, label)
                return True
            if fkind == 'distance' and point_in_rect(mx, my, value_rect):
                key = _owner_key(owner, prop)
                if key is None:
                    return True
                _value_edit.begin(key, '')
                bpy.ops.home_builder.options_edit_value('INVOKE_DEFAULT')
                _tag()
                return True
        if kind == 'action_btn' and point_in_rect(mx, my, entry[5]):
            kwargs = {entry[3]: entry[4]} if entry[3] else {}
            _run(entry[2], **kwargs)
            _tag()
            return True
        if kind == 'form_row' and point_in_rect(mx, my, entry[3]):
            bpy.ops.home_builder.style_options_popup(
                'INVOKE_DEFAULT', section=entry[2], title=entry[1])
            return True
    return False


def scroll(mx, my, entries, rows):
    clip = _clip(entries)
    if clip is None or not point_in_rect(mx, my, clip[1]):
        return False
    _list.scroll_by(rows, ROW_H * scale())
    _tag()
    return True


def _tag():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---- Dropdowns ----------------------------------------------------------------
# A field's value button pops a native menu at the cursor listing the
# enum's items. Native rather than GPU-drawn on purpose: it dismisses,
# scrolls and takes the keyboard exactly as every other Blender menu
# does, and the panel has nothing to reimplement. The target is kept as
# (ID, path) rather than the property group itself, which is a
# temporary wrapper that must not be held across the menu's lifetime.

_menu_target = None     # (id_data, path_from_id, prop)


def open_enum_menu(context, owner, prop, title=""):
    global _menu_target
    try:
        _menu_target = (owner.id_data, owner.path_from_id(), prop)
    except Exception as ex:
        print('Home Builder: cannot open %s: %s' % (prop, ex))
        return
    bpy.ops.home_builder.options_open_enum('INVOKE_DEFAULT', title=title)


class home_builder_OT_options_open_enum(bpy.types.Operator):
    """Open the picker for the value button under the cursor"""
    bl_idname = "home_builder.options_open_enum"
    bl_label = "Open Option"
    bl_options = {'INTERNAL'}

    title: bpy.props.StringProperty()  # type: ignore

    def invoke(self, context, event):
        # The press that hit the button is still down. A menu opened
        # now would receive that same click's release and close on it,
        # so the user had to hold the button to keep the menu up. Wait
        # for the release, then open -- a click, not a hold.
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self._open(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self._open(context)
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _open(self, context):
        context.window_manager.popup_menu(_draw_enum_menu, title=self.title)
        return {'FINISHED'}


def _menu_owner():
    if _menu_target is None:
        return None, None
    id_data, path, prop = _menu_target
    try:
        return id_data.path_resolve(path), prop
    except Exception:
        return None, None


def _draw_enum_menu(menu, context):
    layout = menu.layout
    owner, prop = _menu_owner()
    if owner is None:
        layout.label(text="Unavailable", icon='ERROR')
        return
    current = getattr(owner, prop, None)
    for ident, label in enum_items(owner, prop):
        op = layout.operator('home_builder.options_set_enum', text=label,
                             icon='CHECKMARK' if ident == current else 'BLANK1')
        op.value = ident


class home_builder_OT_options_set_enum(bpy.types.Operator):
    """Pick this value"""
    bl_idname = "home_builder.options_set_enum"
    bl_label = "Set Option"
    bl_options = {'INTERNAL', 'UNDO'}

    value: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        owner, prop = _menu_owner()
        if owner is None:
            return {'CANCELLED'}
        try:
            setattr(owner, prop, self.value)
        except Exception as ex:
            self.report({'WARNING'}, str(ex))
            return {'CANCELLED'}
        _tag()
        return {'FINISHED'}


# ---- Typed values -------------------------------------------------------------

def commit_value(context):
    """Parse what was typed into the distance field and write it. An
    empty or unreadable entry leaves the value alone."""
    key, text = _value_edit.take()
    if key is None or not text:
        return False
    id_data, path, prop = key
    try:
        owner = id_data.path_resolve(path)
    except Exception:
        return False
    value = parse_distance(text)
    if value is None:
        return False
    try:
        setattr(owner, prop, value)
    except Exception as ex:
        print('Home Builder: %s failed: %s' % (prop, ex))
        return False
    return True


class home_builder_OT_options_edit_value(bpy.types.Operator):
    """Type a new value into the field.

    A modal only while the user is typing: Enter commits, Esc cancels,
    a click anywhere commits what was typed and ends it. It must never
    outlive the interaction, because Blender skips autosave while a
    modal is live.
    """
    bl_idname = "home_builder.options_edit_value"
    bl_label = "Edit Value"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _value_edit.active

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        _tag()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # Navigation stays live so the user can look while typing.
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}
        result = _value_edit.feed(event)
        if result == 'COMMIT':
            commit_value(context)
            _tag()
            return {'FINISHED'}
        if result == 'CANCEL':
            _value_edit.cancel()
            _tag()
            return {'CANCELLED'}
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS':
            commit_value(context)
            _tag()
            return {'FINISHED'}
        _tag()
        return {'RUNNING_MODAL'}


# ---- The popup that reuses the sidebar's own UI ----------------------------

class home_builder_OT_style_options_popup(bpy.types.Operator):
    """Open one of the active library's Options sections"""
    bl_idname = "home_builder.style_options_popup"
    bl_label = "Options"

    section: bpy.props.StringProperty()  # type: ignore
    title: bpy.props.StringProperty()  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.title)
        from . import library_panel
        method = library_panel.library_form(self.section, context)
        if method is None:
            layout.label(text="This section is unavailable.", icon='ERROR')
            return
        # The sidebar's own draw method, called verbatim. Every property
        # behaves exactly as it does there, because it IS there.
        method(layout, context)

    def execute(self, context):
        return {'FINISHED'}


def commit_rename(context):
    """Apply the typed name to the style being edited.

    Assignment is the whole commit: the name property's update callback
    de-duplicates against the other styles AND re-tags every cabinet
    carrying the old STYLE_NAME, so an assigned cabinet keeps resolving
    after a rename.
    """
    global _edit_pool
    index, name = _edit.take()
    pool, _edit_pool = _edit_pool, None
    if index is None or not name or pool is None:
        return None
    styles = pool.items(context)
    if not 0 <= index < len(styles):
        return None
    style = styles[index]
    if name != style.name:
        style.name = name
    return style


class home_builder_OT_style_rename(bpy.types.Operator):
    """Rename the cabinet style in place in the list.

    A modal only for as long as the user is typing -- it ends on Enter,
    Esc, or a click anywhere. What must never happen is a modal that
    outlives the interaction, because Blender skips autosave while one
    is live.
    """
    bl_idname = "home_builder.style_rename"
    bl_label = "Rename Cabinet Style"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _edit.active

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        _tag()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _edit_pool
        result = _edit.feed(event)
        if result == 'COMMIT':
            commit_rename(context)
            _tag()
            return {'FINISHED'}
        if result == 'CANCEL':
            _edit.cancel()
            _edit_pool = None
            _tag()
            return {'CANCELLED'}
        # A click anywhere ends the edit, committing what was typed --
        # what a field in a form does when it loses focus.
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS':
            commit_rename(context)
            _tag()
            return {'FINISHED'}
        _tag()
        return {'RUNNING_MODAL'}


class home_builder_OT_cabinet_style_settings(bpy.types.Operator):
    """Settings for this cabinet style: name, wood, finish, overlay,
    fronts and edge profiles"""
    bl_idname = "home_builder.cabinet_style_settings"
    bl_label = "Cabinet Style"

    index: bpy.props.IntProperty(default=-1)  # type: ignore

    def _index(self, context):
        """Index of the style this dialog is showing, or -1."""
        styles = cabinet_styles(context)
        if not styles:
            return -1
        if 0 <= self.index < len(styles):
            return self.index
        active = active_style_index(context)
        return active if 0 <= active < len(styles) else 0

    def _style(self, context):
        styles = cabinet_styles(context)
        if not styles:
            return None
        if 0 <= self.index < len(styles):
            return styles[self.index]
        # No usable index: the active style, which is the one the panel
        # is showing. Falling back to the first would open a different
        # style from the highlighted one whenever Show Settings is used.
        active = active_style_index(context)
        if not 0 <= active < len(styles):
            active = 0
        return styles[active]

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        style = self._style(context)
        if style is None:
            layout.label(text="No cabinet styles defined.", icon='INFO')
            return
        # The sidebar's own per-style form, verbatim. It opens with the
        # Style Name field, so this is also how a style gets renamed.
        style.draw_cabinet_style_ui(layout, context)
        # Delete lives here rather than as a third chip on the row: the
        # row already carries the gear and the move arrows, and removing
        # a style is not something to put one stray click away.
        styles = cabinet_styles(context)
        layout.separator()
        row = layout.row()
        row.enabled = bool(styles) and len(styles) > 1
        op = row.operator("hb_face_frame.remove_cabinet_style",
                          text="Delete Style", icon='TRASH')
        op.index = self._index(context)

    def execute(self, context):
        return {'FINISHED'}


classes = (home_builder_OT_style_options_popup,
           home_builder_OT_cabinet_style_settings,
           home_builder_OT_style_rename,
           home_builder_OT_options_open_enum,
           home_builder_OT_options_set_enum,
           home_builder_OT_options_edit_value,)


def register():
    import sys
    for cls in classes:
        bpy.utils.register_class(cls)
    from . import scene_navigator
    scene_navigator.register_provider(scene_navigator.TAB_OPTIONS,
                                      sys.modules[__name__])


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
