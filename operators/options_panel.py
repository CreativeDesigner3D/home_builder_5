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
handles).

Another tab can draw its own page with these widgets: ``build_page``
takes a blocks function and that tab's ScrollList, and
``field_blocks`` / ``pool_blocks`` / ``form_blocks`` build the blocks.
A ``section`` block it builds may carry a fourth item, a callable that
folds it, so the page keeps its own fold state.

Field kinds: ``enum`` (a dropdown), ``bool`` (a checkbox), ``distance``
(a value you click into and type, in the placement typing grammar),
``number`` (a plain number typed the same way -- a scale, a count, an
angle in degrees), ``value`` (a labelled value to read, from a callable
given the owner), ``thumb`` (an enum picked from a grid of pictures -- see thumb_picker),
``text`` (a string you click into and type), ``choice`` (a dropdown
with a chip that turns it into typed text, for a value outside the
list), ``locked`` (a distance that follows its source until its padlock
chip is opened), ``native`` (a colour or datablock, edited through Blender's
own field in a popover), ``file`` (a path, chosen in Blender's file
browser and cleared by the chip on its row), ``items`` (a row per item of a
collection, each with a remove chip), ``pick`` (a button opening a menu
of commands worked out as it opens), ``notes`` (lines of text a callable
works out from the context) and ``gap`` (space). A field may carry a dict after its label: ``when``
hides it unless the callable, given the owner, says so; ``thumb`` maps
a choice to its picture.
"""

import bpy

from .. import units
from .. import hb_placement
from ..hb_gpu_draw import (
    draw_rect,
    draw_rect_outline,
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
    draw_polyline,
    arc_points,
    paint_button,
    glyph_rename,
    glyph_delete,
    glyph_plus,
    glyph_chevron,
    glyph_caret,
    paint_field,
    paint_check,
    enum_items,
    enum_label,
    InlineEdit,
    paint_inline_edit,
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
GEAR = 18           # the delete chip on the active style's row
CONFIRM_TEXT = "Delete?"    # what that chip says once clicked
ARROW = 14          # a move up / move down chip on the active row
ARROW_GAP = 2       # between the two chips and the settings button
PLUS_SPAN = 8       # full width of the plus mark, not half
PLUS_GAP = 4        # plus mark to the word NEW
INDENT = 8          # an unfolded section's content, in from its header
CHIP = 18            # a toggle or remove chip at the end of a field row


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


_list = ScrollList(bar_width=4, bar_pad=4, min_rows=3)
# Inline rename, keyed by style index -- the same field the scene
# navigator renames rooms with, so the two lists behave alike. The pool
# being renamed is remembered beside it, since the key alone does not
# say which list the index counts.
_edit = InlineEdit()
_edit_pool = None
# The style whose delete chip has been clicked once, as (pool key,
# index). The chip then reads "Delete?" and the next click on it is the
# one that removes; a click anywhere else in the tab stands it down.
_armed_delete = None
# Inline value typing for a distance field, keyed by (ID, path, prop).
_value_edit = InlineEdit()
_edit_kind = None       # the field kind being typed into


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


# Field kinds a click types into; Tab walks from one to the next.
TYPED_KINDS = ('distance', 'text', 'number')


def _is_angle(owner, prop):
    try:
        p = owner.bl_rna.properties[prop]
        return p.type == 'FLOAT' and p.unit == 'ROTATION'
    except Exception:
        return False


def number_text(owner, prop):
    """A 'number' field's value as it reads: an int as is, an angle in
    degrees, any other float to the property's own precision."""
    import math
    value = getattr(owner, prop, 0) or 0
    if isinstance(value, int):
        return str(value)
    if _is_angle(owner, prop):
        return "%g°" % round(math.degrees(value), 2)
    try:
        digits = max(int(owner.bl_rna.properties[prop].precision), 2)
    except Exception:
        digits = 3
    return "%g" % round(float(value), digits)


def parse_number(text):
    """Typed string -> float, or None. Takes a fraction ("3/8") or a
    whole and a fraction ("2 1/2", "2-1/2"), and ignores a trailing
    degree or inch mark."""
    from fractions import Fraction
    text = text.strip().rstrip('°"').strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        pass
    sign = -1.0 if text.startswith('-') else 1.0
    parts = text.lstrip('-').replace('-', ' ').split()
    try:
        return sign * float(sum(Fraction(p) for p in parts))
    except (ValueError, ZeroDivisionError):
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


def _resolve(id_data, path):
    """The owner an (ID, path) key names. A prop on the ID itself has
    an empty path, which path_resolve does not take."""
    return id_data.path_resolve(path) if path else id_data


def _owner_key(owner, prop):
    try:
        if owner.id_data == owner:
            return (owner, "", prop)        # a prop on the ID itself
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
    """(label, operator, prop, value) from a catalog's (label, operator)
    pair or its four-tuple naming one operator property and its value.
    A dict in the prop slot is the operator's keyword arguments whole."""
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
    setting that belongs to the section but not to any one item.
    `actions_first` puts the commands straight under the list, for a
    pool whose item has more fields than fit on screen.
    `scope` 'scene' reads the group off the open scene instead of the
    main one; `list_label` heads the list; `row_text` says what a row
    shows (the item's name by default); `rename_prop` is what a second
    click on the active row types into, None for no rename; and
    `allow_empty` lets the last item be removed.
    Any operator left None simply leaves that control out.
    """

    def __init__(self, title, props, collection, index, add_op=None,
                 remove_op=None, duplicate_op=None, move_op=None,
                 fields=(), actions=(), scene_fields=(),
                 actions_first=False, scope='main', list_label="Styles",
                 row_text=None, rename_prop='name', allow_empty=False):
        self.title = title
        self.props = props
        self.collection = collection
        self.index = index
        self.add_op = add_op
        self.remove_op = remove_op
        self.duplicate_op = duplicate_op
        self.move_op = move_op
        self.fields = tuple(fields)
        self.actions = tuple(tuple(_norm_action(a) for a in row)
                             for row in actions)
        self.scene_fields = tuple(scene_fields)
        self.actions_first = actions_first
        self.scope = scope
        self.list_label = list_label
        self.row_text = row_text
        self.rename_prop = rename_prop
        self.allow_empty = allow_empty

    @property
    def key(self):
        """What this pool is, for telling two specs of it alike: a
        page's spec is built afresh on every draw."""
        return (self.props, self.collection)

    def owner(self, context):
        if self.scope == 'scene':
            return getattr(context.scene, self.props, None)
        return _main_group(self.props, context)

    def text(self, item):
        """What the item's row says."""
        if self.row_text is not None:
            try:
                return str(self.row_text(item) or "")
            except Exception:
                pass
        return str(getattr(item, 'name', "") or "")

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
        fields=spec.get('fields', ()),
        actions=spec.get('actions', ()),
        scene_fields=spec.get('scene_fields', ()),
        actions_first=spec.get('actions_first', False),
        scope=spec.get('scope', 'main'),
        list_label=spec.get('list_label', "Styles"),
        row_text=spec.get('row_text'),
        rename_prop=spec.get('rename_prop', 'name'),
        allow_empty=spec.get('allow_empty', False),
    )


# ---- Sections ----------------------------------------------------------------
# Which sections are unfolded, keyed by (product tab, draw method) so a
# section left open on one library does not open a same-named one on
# another. Kept in the user's folder for this extension, so the tab
# comes back the way it was left rather than folded shut every session.
# Until something has been saved, the face frame cabinet styles start
# open: that pool is reached for mid-design, so its list should be there
# when the tab is.

_DEFAULT_EXPANDED = (('FACE FRAME', 'draw_cabinet_styles_ui'),)
_STATE_FILE = 'options_panel.json'
_expanded = None        # loaded the first time it is asked for


def _state_path(create=False):
    import os
    addon_pkg = __package__.rsplit('.operators', 1)[0]
    try:
        folder = bpy.utils.extension_path_user(addon_pkg, create=create)
    except Exception:
        folder = bpy.utils.user_resource('CONFIG', path='home_builder_5',
                                         create=create)
    return os.path.join(folder, _STATE_FILE) if folder else None


def _expanded_sections():
    global _expanded
    if _expanded is None:
        import json
        _expanded = set(_DEFAULT_EXPANDED)
        try:
            with open(_state_path(), encoding='utf-8') as fh:
                saved = json.load(fh).get('expanded')
            _expanded = {(str(tab), str(method)) for tab, method in saved}
        except Exception:
            pass        # no file yet, or one that cannot be read
    return _expanded


def _save_expanded():
    import json
    try:
        with open(_state_path(create=True), 'w', encoding='utf-8') as fh:
            json.dump({'expanded': sorted(_expanded_sections())}, fh,
                      indent=1)
    except Exception as ex:
        print('Home Builder: could not save the options layout: %s' % ex)


def _section_key(context, method):
    from . import library_panel
    return (library_panel.active_tab(context), method)


def toggle_section(context, method):
    key = _section_key(context, method)
    expanded = _expanded_sections()
    if key in expanded:
        expanded.discard(key)
    else:
        expanded.add(key)
    _save_expanded()
    _tag()


def section_expanded(context, method):
    return _section_key(context, method) in _expanded_sections()


def _pool_blocks(context, pool):
    """The blocks of one pool: its list, the active item's fields, and
    the commands that act on it."""
    blocks = [('head', (pool.list_label, pool.add_op is not None, pool))]
    active = pool.active_index(context)
    for i, item in enumerate(pool.items(context)):
        blocks.append(('style', (i, pool.text(item), i == active, pool)))
    commands = []
    if pool.actions:
        commands.append(('gap', None))
        for row in pool.actions:
            commands.append(('actions', row))
    if pool.duplicate_op:
        commands.append(('actions',
                         (("Duplicate", pool.duplicate_op, None, None),)))
    if pool.actions_first:
        blocks.extend(commands)
    item = pool.active(context)
    if item is not None and pool.fields:
        blocks.append(('gap', None))
        blocks.extend(_field_blocks(context, pool.fields, item))
    if not pool.actions_first:
        blocks.extend(commands)
    scene_owner = pool.scene_owner(context) if pool.scene_fields else None
    if scene_owner is not None:
        blocks.append(('gap', None))
        blocks.extend(_field_blocks(context, pool.scene_fields, scene_owner))
    return blocks


def _field_blocks(context, fields, owner):
    """Blocks for a run of fields on one owner -- a form's group or a
    pool's active item. ``when`` applies to every kind, so a caption or
    a row of commands can come and go with the values around it."""
    blocks = []
    for field in fields:
        if not _field_shown(field, owner):
            continue
        if field[0] == 'gap':
            blocks.append(('gap', None))
        elif field[0] == 'label':
            blocks.append(('label', field[2]))
        elif field[0] == 'notes':
            # Lines worked out as the section is drawn: the callable is
            # given the context (and the owner, where it asks for it)
            # and returns the text, or nothing.
            try:
                if _field_parts(field)[3].get('owner'):
                    lines = field[1](context, owner) or ()
                else:
                    lines = field[1](context) or ()
            except Exception:
                lines = ()
            blocks.extend(('note', line) for line in lines)
        elif field[0] == 'value':
            # A labelled value to read, worked out by a callable given
            # the owner -- a count, a source, what the thing is.
            try:
                text = field[1](owner)
            except Exception:
                text = None
            if text is not None and text != "":
                blocks.append(('value', (field[2], str(text))))
        elif field[0] == 'actions':
            # A row of commands placed among the fields, so a section
            # can group its commands under the label they belong to.
            blocks.append(('actions', tuple(_norm_action(a) for a in field[1])))
        elif field[0] == 'pick':
            blocks.append(('pick', (field[2], field[1])))
        elif field[0] == 'items':
            blocks.extend(_item_blocks(context, field, owner))
        else:
            blocks.append(('field', (field, owner)))
    return blocks


def _item_blocks(context, field, owner):
    """One row per item of a collection on `owner`: the item's value
    across the row with a remove chip at its end, then whatever fields
    the list says each item carries beneath it."""
    _kind, collection, _label, options = _field_parts(field)
    blocks = []
    remove = options.get('remove')
    extra = options.get('fields')
    for i, item in enumerate(getattr(owner, collection, ()) or ()):
        row = dict(options.get('row') or {})
        row['full'] = True
        if remove is not None:
            op_id, kwargs_fn = remove
            row['remove'] = (op_id, dict(kwargs_fn(i, item)))
        blocks.append(('field', ((options.get('kind', 'text'),
                                  options.get('prop', 'name'), "", row),
                                 item)))
        if extra is not None:
            try:
                more = extra(owner, item) or ()
            except Exception:
                more = ()
            blocks.extend(_field_blocks(context, more, item))
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
    blocks = _field_blocks(context, spec.get('fields', ()), owner)
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


def _block_h(block, s):
    kind = block[0]
    if kind == 'indent':
        return _block_h(block[1], s)
    if kind in ('head', 'section'):
        return SECTION_H * s
    if kind == 'gap':
        return GROUP_GAP * s
    return (ROW_H + ROW_GAP) * s


_last_list_h = 0.0      # the list's height at the last build, for Tab


_page = None            # (blocks function, ScrollList) last built


def _current_page():
    """The page on screen: this tab's own, or one another tab hosts
    through build_page. Tab walks its fields."""
    return _page or (_blocks, _list)


def _typed_fields(context):
    """Every field that is typed into, top to bottom, on screen or
    not: (key, kind, owner, prop, offset from the top, height)."""
    s = scale()
    out, y = [], 0.0
    for block in _current_page()[0](context):
        h = _block_h(block, s)
        inner = block[1] if block[0] == 'indent' else block
        if inner[0] == 'field':
            row = _field_entries(context, inner[1][0], inner[1][1],
                                 0.0, 0.0, 100.0, ROW_H * s, s)[0]
            if (row[1] in TYPED_KINDS
                    and not row[8].get('readonly')):
                out.append((_owner_key(row[4], row[2]), row[1], row[4],
                            row[2], y, h))
        y += h
    return out


def _begin_typing(kind, owner, prop):
    """A distance is typed fresh; text is edited from what is there,
    all of it selected so that typing replaces it."""
    global _edit_kind
    key = _owner_key(owner, prop)
    if key is None:
        return False
    _edit_kind = kind
    if kind == 'text':
        _value_edit.begin(key, str(getattr(owner, prop, "") or ""),
                          select=True)
    else:
        _value_edit.begin(key, '')
    return True


def _begin_neighbour(context, key, step):
    """Move typing to the field after (or before) `key`, scrolling it
    into view. False at either end of the tab."""
    fields = _typed_fields(context)
    keys = [f[0] for f in fields]
    if key not in keys:
        return False
    i = keys.index(key) + step
    if not 0 <= i < len(fields):
        return False
    _key, kind, owner, prop, offset, height = fields[i]
    if not _begin_typing(kind, owner, prop):
        return False
    if _last_list_h > 0:
        _current_page()[1].scroll_into_view(offset, height, _last_list_h)
    return True


def build(rect, context):
    return build_page(rect, context, _blocks, _list)


def build_page(rect, context, blocks_fn, lst):
    """Lay out another tab's page with this tab's widgets.

    `blocks_fn(context)` returns the page as blocks -- field_blocks,
    pool_blocks and form_blocks build them -- and `lst` is that tab's
    own ScrollList, so each page keeps its scroll. paint and hit take
    the entries as they are; scroll_page scrolls them.

    Rows inside `rect`. Entries:

        ('section_row', label, method_name, rect, expanded, toggle)
                      toggle None for a library section, else a callable
        ('value_row', label, text, rect)
        ('styles_head', label, rect, add_rect, pool)   add_rect None on most
        ('style_row', index, name, rect, is_active, gear_rect,
                      up_rect, down_rect, pool)
        ('field_row', kind, prop, label, owner, value, rect, value_rect)
        ('action_btn', label, op_id, prop, value, rect, enabled)
        ('form_row', label, method_name, rect)
        ('styles_clip', clip_rect, track, thumb)
    """
    s = scale()
    x0, bottom, w, h = rect
    row_h = ROW_H * s
    sect_h = SECTION_H * s
    gap = ROW_GAP * s

    global _last_list_h, _page
    _page = (blocks_fn, lst)
    blocks = blocks_fn(context)
    polled = {}

    def _h(block):
        return _block_h(block, s)

    content_h = sum(_h(b) for b in blocks)
    list_h, _scrollable, reserve = lst.measure(content_h, h, row_h)
    _last_list_h = list_h
    lst.clamp(content_h, list_h)
    top = bottom + h
    track, thumb = lst.bar_rects(x0, w, top, list_h, content_h, row_h)
    full_w = w - reserve

    entries = [('styles_clip', (x0, top - list_h, w, list_h), track, thumb)]
    for block, block_top, _bb in lst.visible(blocks, top, top - list_h, _h):
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
            label, method, expanded = payload[:3]
            toggle = payload[3] if len(payload) > 3 else None
            entries.append(('section_row', label, method,
                            (x, block_top - sect_h, row_w, sect_h), expanded,
                            toggle))
        elif kind == 'value':
            label, text = payload
            entries.append(('value_row', label, text,
                            (x, block_top - row_h, row_w, row_h)))
        elif kind == 'label':
            entries.append(('label_row', payload,
                            (x, block_top - row_h, row_w, row_h)))
        elif kind == 'note':
            entries.append(('note_row', payload,
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
            # Delete, on the ACTIVE row only and never for the last
            # style: it removes the style you are on, beside its name,
            # and a pool is not allowed to run empty.
            count = len(pool.items(context))
            gear_rect = None
            right = x + row_w - 2 * s
            if (pool.remove_op and is_active
                    and count > (0 if pool.allow_empty else 1)):
                gear = GEAR * s
                gear_w = gear
                if _armed_delete == (pool.key, i):
                    gear_w = text_width(0, FONT * s, CONFIRM_TEXT) + 12 * s
                gear_rect = (right - gear_w,
                             block_top - row_h + (row_h - gear) / 2.0,
                             gear_w, gear)
                right = gear_rect[0]
            # Move up / move down, on the ACTIVE row only. Order is what
            # the list means -- the first style is the one drawings leave
            # white -- so the control belongs on the row, but two more
            # glyphs on every row would crowd a list that is mostly read.
            # Both slots stay reserved at the ends of the list so the
            # remaining chip does not slide sideways.
            up_rect = down_rect = None
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
                    (x + j * (bw + gap), block_top - row_h, bw, row_h),
                    _can_run(op_id, polled)))
        elif kind == 'field':
            field, owner = payload
            entries.extend(_field_entries(context, field, owner, x,
                                          block_top, row_w, row_h, s))
        elif kind == 'pick':
            label, fn = payload
            entries.append(('pick_btn', label, fn,
                            (x, block_top - row_h, row_w, row_h)))
        elif kind == 'form':
            label, method = payload
            entries.append(('form_row', label, method,
                            (x, block_top - row_h, row_w, row_h)))
    return entries


def _native_value(owner, prop):
    """What a 'native' field's button says: a datablock's name, a file's
    name, or nothing for a colour (which is painted instead)."""
    value = getattr(owner, prop, None)
    if value is None or value == "":
        return "None"
    if isinstance(value, str):
        import os
        return os.path.basename(value.rstrip('/\\')) or value
    name = getattr(value, 'name', None)
    return name if isinstance(name, str) else ""


def _field_entries(context, field, owner, x, top, row_w, row_h, s):
    """The entries of one field row: the field, and the chip at its end
    where it has one. 'choice' and 'locked' resolve here to the kind the
    row is being right now -- a dropdown or typed text, a value that can
    be typed into or only read."""
    fkind, prop, label, options = _field_parts(field)
    options = dict(options)
    chip_prop = glyph = None
    if fkind == 'choice':
        base = options.get('custom') or prop
        chip_prop, glyph = base + '_is_custom', 'text'
        if getattr(owner, chip_prop, False):
            fkind, prop = 'text', base + '_custom'
        else:
            fkind = 'enum'
    elif fkind == 'locked':
        chip_prop, glyph = options.get('unlock'), 'lock'
        fkind = 'distance'
        options['readonly'] = not getattr(owner, chip_prop, False)
    remove = options.get('remove')
    # A file that has been set can be cleared again from its row.
    clear = fkind == 'file' and bool(getattr(owner, prop, ""))
    chip_room = ((CHIP + ARROW_GAP) * s
                 if (chip_prop or remove or clear) else 0.0)
    rect = (x, top - row_h, row_w - chip_room, row_h)
    # The label column is measured on the full row, so a row that gives
    # up room to a chip still lines its value up with its neighbours.
    lw = 0.0 if options.get('full') else row_w * 0.42
    options['frac'] = lw / rect[2] if rect[2] > 0 else 0.0
    value_rect = (x + lw, rect[1] + 2 * s, rect[2] - lw, row_h - 4 * s)
    if fkind == 'bool':
        value = bool(getattr(owner, prop, False))
        value_rect = rect
    elif fkind == 'distance':
        if _value_edit.editing(_owner_key(owner, prop)):
            value = ""      # the edit paints itself over the field
        else:
            value = units.unit_to_string(
                context.scene.unit_settings,
                float(getattr(owner, prop, 0.0) or 0.0))
    elif fkind == 'text':
        if _value_edit.editing(_owner_key(owner, prop)):
            value = ""
        else:
            value = str(getattr(owner, prop, "") or "")
    elif fkind == 'number':
        if _value_edit.editing(_owner_key(owner, prop)):
            value = ""
        else:
            value = number_text(owner, prop)
    elif fkind in ('native', 'file'):
        value = _native_value(owner, prop)
    else:
        value = enum_label(owner, prop)
    out = [('field_row', fkind, prop, label, owner, value, rect, value_rect,
            options)]
    chip = CHIP * s
    chip_rect = (x + row_w - chip, top - row_h + (row_h - chip) / 2.0,
                 chip, chip)
    if chip_prop:
        out.append(('toggle_chip', owner, chip_prop, chip_rect,
                    bool(getattr(owner, chip_prop, False)), glyph))
    elif remove:
        out.append(('op_chip', remove[0], remove[1], chip_rect))
    elif clear:
        out.append(('clear_chip', owner, prop, chip_rect))
    return out


def _glyph_lock(shader, rect, locked, color):
    """A padlock: closed when the value follows its source, its shackle
    swung open when it has been taken over by hand."""
    import math
    x, y, w, h = rect
    bw, bh = w * 0.44, h * 0.30
    bx, by = x + (w - bw) / 2.0, y + h * 0.24
    draw_rect(shader, bx, by, bw, bh, color)
    r = bw * 0.34
    cx = bx + bw / 2.0 + (0.0 if locked else r * 1.1)
    cy = by + bh + h * 0.06
    pts = [(cx - r, by + bh)] + arc_points(cx, cy, r, math.pi, 0.0, 8)
    if locked:
        pts.append((cx + r, by + bh))
    draw_polyline(shader, pts, color)


def _can_run(op_id, cache):
    """Whether the operator's poll passes here and now. Asked once per
    operator per build; an operator that cannot be asked counts as
    runnable, so a mistake here never locks a command away."""
    if op_id not in cache:
        try:
            mod, name = op_id.split('.', 1)
            cache[op_id] = bool(getattr(getattr(bpy.ops, mod), name).poll())
        except Exception:
            cache[op_id] = True
    return cache[op_id]


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
                label, rect, expanded = entry[1], entry[3], entry[4]
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
            elif kind == 'value_row':
                # Read, not edited: the label where a field's is, the
                # value where a field's would be, with no well round it.
                _, label, text, rect = entry
                rx, ry, rw, rh = rect
                lw = rw * 0.42
                draw_text(font_id, rx + 6 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_NORMAL,
                          fit_text(font_id, FONT * s, label, lw - 6 * s))
                draw_text(font_id, rx + lw + 6 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY,
                          fit_text(font_id, FONT * s, text, rw - lw - 12 * s))
            elif kind == 'note_row':
                _, text, rect = entry
                rx, ry, rw, rh = rect
                draw_text(font_id, rx + 8 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_NORMAL,
                          fit_text(font_id, FONT * s, text, rw - 12 * s))
            elif kind == 'styles_head':
                _, label, rect, add_rect, _pool = entry
                _paint_head(shader, font_id, s, mx, my, label, rect, add_rect)
            elif kind == 'style_row':
                (_, _i, name, rect, is_active, gear_rect,
                 up_rect, down_rect, pool) = entry
                arrows = is_active and (up_rect is not None
                                        or down_rect is not None)
                arrow_room = (2 * ARROW + ARROW_GAP) * s if arrows else 0.0
                gear_room = gear_rect[2] if gear_rect is not None else 0.0
                hovered = point_in_rect(mx, my, rect)
                rx, ry, rw, rh = rect
                renaming = (_edit.editing(_i) and _edit_pool is not None
                            and _edit_pool.key == pool.key)
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
                    box = (text_x - 3 * s, ry + 3 * s,
                           field_w + 6 * s, rh - 6 * s)
                    draw_rects(shader, [box], (0.0, 0.0, 0.0, 0.55))
                    paint_inline_edit(shader, font_id, box, FONT * s,
                                      _edit, pad=3 * s)
                    shown = ""
                else:
                    shown = fit_text(font_id, FONT * s, name,
                                     rw - gear_room - arrow_room - 16 * s)
                draw_text(font_id, text_x, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY if (is_active or renaming)
                          else Theme.TEXT_NORMAL, shown)
                if gear_rect is not None and not renaming:
                    g_hot = point_in_rect(mx, my, gear_rect)
                    if _armed_delete == (pool.key, _i):
                        danger = Theme.ACTION_DANGER_BG
                        paint_button(shader, gear_rect, hovered=g_hot,
                                     bg=danger,
                                     hover_bg=danger[:3] + (0.95,))
                        draw_centered_text(font_id, gear_rect, FONT * s,
                                           Theme.TEXT_PRIMARY, CONFIRM_TEXT)
                    else:
                        if g_hot:
                            paint_button(shader, gear_rect, hovered=True)
                        glyph_delete(shader, gear_rect,
                                     Theme.GLYPH_HOVER if g_hot
                                     else Theme.GLYPH)
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
                readonly = options.get('readonly', False)
                hot = point_in_rect(mx, my, value_rect) and not readonly
                frac = options.get('frac', 0.42)
                if fkind == 'bool':
                    paint_check(shader, font_id, rect, FONT * s, label,
                                bool(value), point_in_rect(mx, my, rect))
                elif fkind in TYPED_KINDS:
                    editing = _value_edit.editing(_owner_key(owner, prop))
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, label_frac=frac,
                                caret=False,
                                enabled=(not readonly
                                         or options.get('plain', False)))
                    if editing:
                        # A dark well with the accent round it, so the
                        # accent is free to mean "selected" inside it.
                        draw_rect(shader, *value_rect, (0.0, 0.0, 0.0, 0.55))
                        draw_rect_outline(shader, *value_rect,
                                          Theme.ACCENT_BG)
                        paint_inline_edit(shader, font_id, value_rect,
                                          FONT * s, _value_edit, pad=6 * s)
                elif fkind == 'file':
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, label_frac=frac,
                                caret=False)
                elif fkind == 'native':
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, label_frac=frac,
                                caret=False)
                    color = getattr(owner, prop, None)
                    if (not isinstance(color, str) and color is not None
                            and hasattr(color, '__len__')
                            and len(color) >= 3):
                        vx, vy, vw, vh = value_rect
                        draw_rect(shader, vx + 3 * s, vy + 3 * s,
                                  vw - 6 * s, vh - 6 * s,
                                  (color[0], color[1], color[2], 1.0))
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
                                str(value), hot, label_frac=frac,
                                text_inset=inset)
                    if tex is not None:
                        gpu.state.blend_set('ALPHA')
                        thumb_picker.draw_texture(
                            tex, (vx + 2 * s, vy + 1 * s, vh - 2 * s, vh - 2 * s))
                        shader.bind()
                else:
                    paint_field(shader, font_id, rect, FONT * s, label,
                                str(value), hot, label_frac=frac)
            elif kind == 'toggle_chip':
                _, _owner, _prop, rect, on, glyph = entry
                c_hot = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=c_hot,
                             active=on and glyph == 'text')
                color = Theme.GLYPH_HOVER if (c_hot or on) else Theme.GLYPH
                if glyph == 'lock':
                    _glyph_lock(shader, rect, not on, color)
                else:
                    glyph_rename(shader, rect, color)
            elif kind == 'clear_chip':
                rect = entry[3]
                c_hot = point_in_rect(mx, my, rect)
                if c_hot:
                    paint_button(shader, rect, hovered=True)
                glyph_delete(shader, rect,
                             Theme.GLYPH_HOVER if c_hot else Theme.GLYPH)
            elif kind == 'op_chip':
                _, _op, _kwargs, rect = entry
                c_hot = point_in_rect(mx, my, rect)
                if c_hot:
                    paint_button(shader, rect, hovered=True)
                glyph_delete(shader, rect,
                             Theme.GLYPH_HOVER if c_hot else Theme.GLYPH)
            elif kind == 'pick_btn':
                _, label, _fn, rect = entry
                hovered = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hovered)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_PRIMARY if hovered
                                   else Theme.TEXT_NORMAL, label)
            elif kind == 'action_btn':
                _, label, _op, _prop, _val, rect, enabled = entry
                hovered = enabled and point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hovered)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_DIM if not enabled
                                   else Theme.TEXT_PRIMARY if hovered
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


_pending_action = None  # (operator, kwargs) waiting for the release


def _run_on_release(op_id, kwargs):
    """Run a command button's operator once the click is released. A
    press runs the hit, and an operator that asks first (a confirm, a
    dialog) would otherwise open under a button still held down -- the
    release then lands on it and answers for the user."""
    global _pending_action
    _pending_action = (op_id, dict(kwargs))
    try:
        bpy.ops.home_builder.options_run_action('INVOKE_DEFAULT')
    except Exception as ex:
        _pending_action = None
        print('Home Builder: %s failed: %s' % (op_id, ex))


class home_builder_OT_options_run_action(bpy.types.Operator):
    """Run the command button under the cursor"""
    bl_idname = "home_builder.options_run_action"
    bl_label = "Run Option Command"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self._go()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self._go()
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            global _pending_action
            _pending_action = None
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _go(self):
        global _pending_action
        action, _pending_action = _pending_action, None
        if action is None:
            return {'CANCELLED'}
        _run(action[0], **action[1])
        _tag()
        return {'FINISHED'}


def hit(context, mx, my, entries):
    global _edit_pool, _armed_delete
    # Any click stands a pending delete down; only a second click on the
    # same chip, below, goes through with it.
    armed, _armed_delete = _armed_delete, None
    clip = _clip(entries)
    if clip is not None and not point_in_rect(mx, my, clip[1]):
        return False
    for entry in entries:
        kind = entry[0]
        if kind == 'section_row' and point_in_rect(mx, my, entry[3]):
            if entry[5] is not None:
                # A hosted page folds its own sections.
                try:
                    entry[5]()
                except Exception as ex:
                    print('Home Builder: %s failed: %s' % (entry[1], ex))
                _tag()
            else:
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
            # Delete next: it sits inside the row, so a hit there must
            # not also rename the style underneath it.
            if entry[5] is not None and point_in_rect(mx, my, entry[5]):
                if armed == (pool.key, entry[1]):
                    if pool.remove_op:
                        _run(pool.remove_op)
                else:
                    _armed_delete = (pool.key, entry[1])
                _tag()
                return True
            if point_in_rect(mx, my, entry[3]):
                index = entry[1]
                if pool.active_index(context) != index:
                    pool.set_active(context, index)
                elif pool.rename_prop:
                    # Clicking the style you are already on renames it,
                    # the same second click that renames a room.
                    item = pool.active(context)
                    _edit_pool = pool
                    _edit.begin(index, str(getattr(item, pool.rename_prop,
                                                   "") or ""))
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
            if options.get('readonly'):
                continue
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
            if fkind == 'file' and point_in_rect(mx, my, value_rect):
                open_file_browser(context, owner, prop)
                return True
            if fkind == 'native' and point_in_rect(mx, my, value_rect):
                open_native(context, owner, prop, label, options.get('draw'))
                return True
            if (fkind in TYPED_KINDS
                    and point_in_rect(mx, my, value_rect)):
                if not _begin_typing(fkind, owner, prop):
                    return True
                bpy.ops.home_builder.options_edit_value('INVOKE_DEFAULT')
                _tag()
                return True
        if kind == 'toggle_chip' and point_in_rect(mx, my, entry[3]):
            try:
                setattr(entry[1], entry[2], not getattr(entry[1], entry[2]))
            except Exception as ex:
                print('Home Builder: %s failed: %s' % (entry[2], ex))
            _tag()
            return True
        if kind == 'clear_chip' and point_in_rect(mx, my, entry[3]):
            try:
                setattr(entry[1], entry[2], "")
            except Exception as ex:
                print('Home Builder: %s failed: %s' % (entry[2], ex))
            _tag()
            return True
        if kind == 'op_chip' and point_in_rect(mx, my, entry[3]):
            _run(entry[1], **entry[2])
            _tag()
            return True
        if kind == 'pick_btn' and point_in_rect(mx, my, entry[3]):
            open_pick_menu(context, entry[2], entry[1])
            return True
        if kind == 'action_btn' and point_in_rect(mx, my, entry[5]):
            if not entry[6]:
                return True
            if isinstance(entry[3], dict):
                kwargs = dict(entry[3])
            else:
                kwargs = {entry[3]: entry[4]} if entry[3] else {}
            _run_on_release(entry[2], kwargs)
            _tag()
            return True
        if kind == 'form_row' and point_in_rect(mx, my, entry[3]):
            bpy.ops.home_builder.style_options_popup(
                'INVOKE_DEFAULT', section=entry[2], title=entry[1])
            return True
    return False


def scroll(mx, my, entries, rows):
    return scroll_page(mx, my, entries, rows, _list)


def scroll_page(mx, my, entries, rows, lst):
    clip = _clip(entries)
    if clip is None or not point_in_rect(mx, my, clip[1]):
        return False
    lst.scroll_by(rows, ROW_H * scale())
    _tag()
    return True


# ---- Hosting another tab's page ---------------------------------------------
# What a tab passes build_page: the same blocks this tab is made of.

def field_blocks(context, fields, owner):
    """Blocks for a run of fields on `owner`, in the OPTION_PAGES field
    vocabulary, plus ('value', text_fn, label) for a value to read."""
    return _field_blocks(context, fields, owner)


def pool_blocks(context, spec):
    """Blocks for a 'pool' spec dict, as OPTION_PAGES writes one."""
    return _pool_blocks(context, _pool_from_spec(spec))


def form_blocks(context, spec):
    """Blocks for a 'form' spec dict, as OPTION_PAGES writes one."""
    return _form_blocks(context, spec)


def new_scroll_list():
    """A ScrollList set up the way this tab's own is."""
    return ScrollList(bar_width=4, bar_pad=4, min_rows=3)


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
# What the release opens: the draw function, and whether it goes in a
# menu or a popover. A popover is for the few values no GPU widget here
# can edit -- a colour, a datablock -- drawn as Blender's own
# field so its own picker opens from it.
_popup_draw = None
_popup_kind = 'MENU'
_native_draw = None     # a 'native' field's own draw(layout, owner)
_pick_entries = ()      # [(label, operator, kwargs)] for a pick menu


def _open_popup(title, draw, kind='MENU'):
    global _popup_draw, _popup_kind
    _popup_draw, _popup_kind = draw, kind
    bpy.ops.home_builder.options_open_enum('INVOKE_DEFAULT', title=title)


def _set_target(owner, prop):
    global _menu_target
    _menu_target = _owner_key(owner, prop)
    if _menu_target is None:
        print('Home Builder: cannot open %s' % prop)
        return False
    return True


def open_enum_menu(context, owner, prop, title=""):
    if _set_target(owner, prop):
        _open_popup(title, _draw_enum_menu)


def open_native(context, owner, prop, title="", draw=None):
    global _native_draw
    if _set_target(owner, prop):
        _native_draw = draw
        _open_popup(title, _draw_native, 'POPOVER')


def open_file_browser(context, owner, prop):
    """A path is the one value that does open a Blender window: there
    is no picking a file without a file browser."""
    if _set_target(owner, prop):
        current = getattr(owner, prop, "") or ""
        bpy.ops.home_builder.options_pick_file('INVOKE_DEFAULT',
                                               filepath=current)


def open_pick_menu(context, entries_fn, title=""):
    """A menu of commands worked out as it opens -- what can be added
    to a list depends on what is already in it."""
    global _pick_entries
    try:
        _pick_entries = tuple(entries_fn(context) or ())
    except Exception as ex:
        print('Home Builder: %s failed: %s' % (title, ex))
        _pick_entries = ()
    _open_popup(title, _draw_pick_menu)


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
        wm = context.window_manager
        if _popup_draw is None:
            return {'CANCELLED'}
        if _popup_kind == 'POPOVER':
            wm.popover(_popup_draw, ui_units_x=14)
        else:
            wm.popup_menu(_popup_draw, title=self.title)
        return {'FINISHED'}


def _menu_owner():
    if _menu_target is None:
        return None, None
    id_data, path, prop = _menu_target
    try:
        return _resolve(id_data, path), prop
    except Exception:
        return None, None


MENU_ROWS = 18          # a menu longer than this breaks into columns
MENU_MAX_COLS = 6


def _menu_columns(layout, count):
    """(columns, rows per column) for a menu of `count` entries. A long
    list runs across in columns, read down each one, so the whole of it
    is on screen at once instead of behind a scroll arrow."""
    if count <= MENU_ROWS:
        return [layout.column()], max(count, 1)
    cols = min(-(-count // MENU_ROWS), MENU_MAX_COLS)
    per_col = -(-count // cols)
    row = layout.row()
    return [row.column() for _ in range(cols)], per_col


def _draw_enum_menu(menu, context):
    layout = menu.layout
    owner, prop = _menu_owner()
    if owner is None:
        layout.label(text="Unavailable", icon='ERROR')
        return
    current = getattr(owner, prop, None)
    items = enum_items(owner, prop)
    columns, per_col = _menu_columns(layout, len(items))
    for i, (ident, label) in enumerate(items):
        op = columns[i // per_col].operator(
            'home_builder.options_set_enum', text=label,
            icon='CHECKMARK' if ident == current else 'BLANK1')
        op.value = ident


def _draw_native(popover, context):
    layout = popover.layout
    owner, prop = _menu_owner()
    if owner is None:
        layout.label(text="Unavailable", icon='ERROR')
        return
    if _native_draw is not None:
        _native_draw(layout, owner)
    else:
        layout.prop(owner, prop, text="")


def _draw_pick_menu(menu, context):
    layout = menu.layout
    if not _pick_entries:
        layout.label(text="Nothing more to add")
        return
    columns, per_col = _menu_columns(layout, len(_pick_entries))
    for i, (label, op_id, kwargs) in enumerate(_pick_entries):
        op = columns[i // per_col].operator(op_id, text=label)
        for key, value in kwargs.items():
            setattr(op, key, value)


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


class home_builder_OT_options_pick_file(bpy.types.Operator):
    """Choose the image file for this field"""
    bl_idname = "home_builder.options_pick_file"
    bl_label = "Choose Image"
    bl_options = {'INTERNAL', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_image: bpy.props.BoolProperty(
        default=True, options={'HIDDEN'})  # type: ignore
    filter_folder: bpy.props.BoolProperty(
        default=True, options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        owner, prop = _menu_owner()
        if owner is None:
            return {'CANCELLED'}
        try:
            setattr(owner, prop, self.filepath)
        except Exception as ex:
            self.report({'WARNING'}, str(ex))
            return {'CANCELLED'}
        _tag()
        return {'FINISHED'}


# ---- Typed values -------------------------------------------------------------

def commit_value(context):
    """Write what was typed into the field. A distance is parsed, and an
    empty or unreadable entry leaves it alone; text is taken as typed,
    and may be emptied."""
    key, text = _value_edit.take()
    if key is None:
        return False
    id_data, path, prop = key
    try:
        owner = _resolve(id_data, path)
        is_text = owner.bl_rna.properties[prop].type == 'STRING'
    except Exception:
        return False
    if is_text:
        value = text
    elif _edit_kind == 'number':
        # A 'number' field: a count, a scale, an angle typed in degrees.
        import math
        value = parse_number(text) if text else None
        if value is None:
            return False
        if owner.bl_rna.properties[prop].type == 'INT':
            value = int(round(value))
        elif _is_angle(owner, prop):
            value = math.radians(value)
    else:
        value = parse_distance(text) if text else None
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
    Tab commits and moves to the next typed field (Shift+Tab the one
    before), a click anywhere commits what was typed and ends it. It must never
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
        # Inside the field the mouse edits: a press places the cursor,
        # a drag selects, a double click takes the word.
        if _value_edit.mouse(event, event.mouse_region_x,
                             event.mouse_region_y):
            _tag()
            return {'RUNNING_MODAL'}
        # Navigation stays live so the user can look while typing.
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}
        result = _value_edit.feed(event)
        if result in ('NEXT', 'PREV'):
            # Tab commits and carries on in the next typed field, so a
            # run of sizes is filled without reaching for the mouse.
            key = _value_edit.key
            commit_value(context)
            moved = _begin_neighbour(context, key,
                                     1 if result == 'NEXT' else -1)
            _tag()
            return {'RUNNING_MODAL'} if moved else {'FINISHED'}
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
    prop = pool.rename_prop or 'name'
    if name != getattr(style, prop, None):
        setattr(style, prop, name)
    return style


class home_builder_OT_style_rename(bpy.types.Operator):
    """Rename the item in place in the list.

    A modal only for as long as the user is typing -- it ends on Enter,
    Esc, or a click anywhere. What must never happen is a modal that
    outlives the interaction, because Blender skips autosave while one
    is live. Any list's rows rename through it, so the label names none.
    """
    bl_idname = "home_builder.style_rename"
    bl_label = "Rename List Item"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _edit.active

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        _tag()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _edit_pool
        if _edit.mouse(event, event.mouse_region_x, event.mouse_region_y):
            _tag()
            return {'RUNNING_MODAL'}
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


classes = (home_builder_OT_style_options_popup,
           home_builder_OT_style_rename,
           home_builder_OT_options_open_enum,
           home_builder_OT_options_set_enum,
           home_builder_OT_options_pick_file,
           home_builder_OT_options_edit_value,
           home_builder_OT_options_run_action,)


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
