"""PANELS tab -- the appliance panel layout, edited on a picture of it.

A panelled appliance is a run of faces: doors, drawer fronts and fixed
panels, in columns, each with a size it either holds or shares. The
dialog listed them as rows of numbers and locks, which reads as a form
about a fridge rather than as the fridge -- you had to hold the layout
in your head to work out which row was the face you meant.

This tab draws the front instead. Every face is where it will be, at
the size it will be; clicking one selects it, and what is below the
picture acts on THAT face: what it is, what it is called, how tall,
its backer, and the commands that change the shape of the run --
splitting it, moving it, removing it, adding a column.

Two ideas carry most of the clarity:

* **Typing a size holds it.** The model shares whatever is left over
  between the faces that have no size of their own, which is what makes
  a run add up. That was a padlock per row to reason about. Here, a
  size you type is a size you want, so it holds itself; the chip beside
  it says Fill, and gives it back to the sharing.
* **Split, rather than add.** A face is cut in two where you are
  looking, instead of a face being appended to a column and then moved.

The tab appears whenever a panel-ready appliance is selected and is the
way the Appliance Panels command opens while the viewport panel is on;
the dialog stays for anyone running without it.

Pattern, as with the other hosted tabs: this is a provider for the
scene navigator (build / paint / hit / scroll), so the panel owns the
chrome and the keymap, and nothing here is a persistent modal -- the
one modal is the few seconds a value is being typed.
"""

import sys

import bpy
import gpu

from .. import hb_types
from .. import units
from ..hb_gpu_draw import (
    draw_rect,
    draw_rects,
    draw_rect_outline,
    draw_rect_outlines,
    draw_text,
    draw_lines,
    point_in_rect,
    vcenter_baseline,
)
from ..hb_gpu_ui import (
    Theme,
    scale,
    fit_text,
    begin_clip,
    end_clip,
    paint_button,
    paint_field,
    paint_check,
    paint_inline_edit,
    draw_centered_text,
    InlineEdit,
    ScrollList,
    enum_label,
)
from ..product_libraries.face_frame import appliance_panels as ap

PREFERRED_WIDTH = 300       # unscaled

TAB_KEY = 'PANELS'
TAB_LABEL = 'PANELS'
# After the built-in three (Rooms 0, Library 10, Options 20): it is the
# tab you want while an appliance is selected, not the one you start on.
TAB_ORDER = 25

# The appliances that take panels -- the same set the panel operator polls
# on, so the tab and the command cannot disagree about what is panelable.
PANEL_APPLIANCES = {'DISHWASHER', 'REFRIGERATOR', 'UNDER_COUNTER'}

# ---- Layout (unscaled px) ---------------------------------------------------
ROW_H       = 22
ROW_GAP     = 4
GROUP_GAP   = 9
HEAD_H      = 18
BTN_H       = 22
BTN_GAP     = 4
CHIP_W      = 34
ELEV_GAP    = 8
ELEV_MIN_H  = 110
ELEV_MAX_FRAC = 0.46        # of the body height, so the fields keep room
FACE_MIN_LABEL_H = 26       # a face shorter than this carries no text
FONT        = 12
SMALL       = 10

# ---- Colors -----------------------------------------------------------------
# The elevation is the one thing here that is a picture rather than
# chrome, so it has a palette of its own: a dark well, faces that read
# as parts, and rails in the one warm color.
ELEV_BG     = (0.11, 0.11, 0.12, 1.0)
ELEV_BORDER = (1.0, 1.0, 1.0, 0.16)
KICK_BG     = (0.07, 0.07, 0.08, 1.0)
FACE_BG     = (0.27, 0.27, 0.29, 1.0)
FACE_HOVER  = (0.35, 0.35, 0.37, 1.0)
FACE_SEL    = (0.20, 0.43, 0.70, 1.0)
FACE_BORDER = (0.0, 0.0, 0.0, 0.55)
FACE_MARK   = (0.72, 0.72, 0.74, 1.0)
FACE_TEXT   = (0.93, 0.93, 0.93, 1.0)
FACE_SUB    = (0.72, 0.72, 0.74, 1.0)
RAIL_BG     = (0.46, 0.38, 0.27, 1.0)

_list = ScrollList(bar_width=4, bar_pad=4, min_rows=3)

# Which face is selected, per appliance, so switching between two
# fridges comes back to what you were editing on each.
_selected = {}

# The solve the current build ran, so the rows below the picture read
# the sizes off the same pass that drew it instead of solving again per
# field. Rebuilt every build; never read without checking the name.
_solved = {'name': None, 'faces': {}}

# Whether the layout picker is showing its grid. One tab, one
# appliance at a time, so one flag.
_grid_open = False

# The field being typed into, and what it writes to. The target is a
# key rather than the property group: a group is a temporary wrapper
# that must not be held across a modal.
_edit = InlineEdit()
_edit_key = None


# ---- The appliance ----------------------------------------------------------

def target(context=None):
    """The appliance this tab edits: the selected object's appliance
    root, when that appliance takes panels. None otherwise -- which is
    also what hides the tab."""
    from .. import hb_utils
    if context is None:
        context = bpy.context
    obj = getattr(context, 'object', None)
    if obj is None:
        return None
    try:
        bp = hb_utils.get_appliance_bp(obj)
    except Exception:
        return None
    if bp is None or bp.get('APPLIANCE_TYPE') not in PANEL_APPLIANCES:
        return None
    return bp


def available(scene):
    """The tab shows only while a panel-ready appliance is selected in a
    room -- a 2D sheet or a detail card cannot build anything."""
    from . import scene_navigator
    if not scene_navigator.is_room(scene):
        return False
    return target(bpy.context) is not None


def _props(bp):
    return bp.appliance_panels


def _cage(bp):
    """(width, height) of the appliance front, in metres."""
    cage = hb_types.GeoNodeCage(bp)
    return (cage.get_input('Dim X') or 0.0, cage.get_input('Dim Z') or 0.0)


def default_config(bp):
    items = ap.CONFIG_ITEMS.get(bp.get('APPLIANCE_TYPE'), ap.DEFAULT_CONFIG_ITEMS)
    return items[0][0] if items else 'SINGLE'


def selected_index(bp):
    """The selected face, clamped to what the run still has."""
    props = _props(bp)
    n = len(props.sections)
    if not n:
        return -1
    i = _selected.get(bp.name, 0)
    return min(max(int(i), 0), n - 1)


def select(bp, index):
    _selected[bp.name] = max(0, int(index))


def _set_grid(open_):
    """Show or hide the layout grid. Scrolled back to the top when it
    opens, so the tiles are where the row that opened them is."""
    global _grid_open
    _grid_open = bool(open_)
    if _grid_open:
        _list.offset = 0.0


def _fmt(value):
    """A size the way the rest of the add-on writes one."""
    scene = bpy.context.scene
    try:
        return units.unit_to_string(scene.unit_settings, value)
    except Exception:
        return "%.3f\"" % units.meter_to_inch(value)


def _kind_label(section):
    return enum_label(section, 'kind')


def pull_side(props, section):
    """Which edge a door's pull sits on -- the opening edge, away from
    its hinge. Follows the appliance model's own convention: a pair of
    doors hinges on the outside so the pulls meet in the middle, and a
    lone door hinges on the right."""
    if getattr(section, 'kind', '') != 'DOOR':
        return 'R'
    column = getattr(section, 'column', -1)
    ncol = len(props.columns)
    if column < 0 or ncol <= 1:
        return 'L'
    return 'L' if column == ncol - 1 else 'R'


def _face_place(props, index):
    """Where a face sits, in words -- empty when the run is one column
    and there is nothing to say about where it is."""
    sec = props.sections[index]
    if sec.column < 0:
        return "Full width"
    if len(props.columns) <= 1:
        return ""
    return "Column %d" % (sec.column + 1)


# ---- Blocks -----------------------------------------------------------------
# The scrolling half of the tab is a list of blocks, each one row high
# unless it says otherwise. Laid out after they are counted, so the
# scrollbar knows the content height before anything is positioned.

def _blocks(context, bp):
    props = _props(bp)
    index = selected_index(bp)
    out = []
    if index < 0:
        return out
    sec = props.sections[index]

    # The layout comes first: it is what the run IS, and picking one
    # replaces everything below it.
    out.append(('pick', ('CONFIG', "Layout", _config_label(bp, props))))
    if _grid_open:
        out.append(('grid', _preset_items(bp)))

    place = _face_place(props, index)
    out.append(('head', "%s (%s)" % (_kind_label(sec), place) if place
                else _kind_label(sec)))
    out.append(('kind', index))
    out.append(('field', (('sec', index, 'label'), "Name", 'TEXT')))
    out.append(('field', (('sec', index, 'height'), "Height", 'SIZE')))
    out.append(('field', (('sec', index, 'backer'), "Backer", 'MENU')))
    out.append(('face_cmds', index))

    if sec.column >= 0 and len(props.columns) > 1:
        out.append(('gap', None))
        out.append(('field', (('col', sec.column, 'width'),
                              "Column %d" % (sec.column + 1), 'SIZE')))

    if sec.spec_note:
        out.append(('note', sec.spec_note))

    out.append(('gap', None))
    out.append(('head', "Run"))
    out.append(('run_cmds', None))
    if bp.get('APPLIANCE_TYPE') in ap.KICK_APPLIANCE_TYPES:
        out.append(('field', (('run', 0, 'toe_kick'), "Toe Kick", 'SIZE')))
    # The gaps, one row each and in the order they read on the model:
    # around the outside, then between the columns and between the faces
    # stacked in them. An edge with no size of its own follows Edge Gap,
    # so its row shows what it currently measures and its chip gives the
    # size back.
    out.append(('field', (('run', 0, 'reveal_top'), "Gap Top", 'SIZE')))
    out.append(('field', (('run', 0, 'reveal_bottom'), "Gap Bottom", 'SIZE')))
    out.append(('field', (('run', 0, 'reveal_left'), "Gap Left", 'SIZE')))
    out.append(('field', (('run', 0, 'reveal_right'), "Gap Right", 'SIZE')))
    out.append(('field', (('run', 0, 'column_gap'), "Between Columns", 'SIZE')))
    out.append(('field', (('run', 0, 'section_gap'), "Between Faces", 'SIZE')))
    # One backer type for the whole run: they are nearly always the
    # same, so this sets every panel and clears any face that had been
    # given its own. A single face can still differ afterwards, from
    # its own Backer row.
    out.append(('pick', ('BACKER', "Backers", enum_label(props, 'panel_type'))))
    out.append(('field', (('run', 0, 'backer_reveal'), "Backer Edge", 'SIZE')))

    out.append(('field', (('run', 0, 'install_type'), "Install", 'MENU')))

    out.append(('gap', None))
    out.append(('head', "Inset Rails"))
    out.append(('rails', None))
    if props.has_rails():
        out.append(('field', (('run', 0, 'rail_width'), "Rail Width", 'SIZE')))

    # Starting over comes last: a preset or a manufacturer's guide
    # REPLACES the layout above, so it is not what the tab opens on.
    out.append(('gap', None))
    out.append(('head', "Manufacturer"))
    provider = _spec_provider()
    if provider is not None:
        out.append(('pick', ('MFR', "Make", props.manufacturer or "Manual")))
        if props.manufacturer:
            out.append(('pick', ('MODEL', "Model", props.model or "(pick)")))
        if props.weight_max_lb:
            out.append(('note', "Max panel weight %g lb" % props.weight_max_lb))
    return out


def _spec_provider():
    """The manufacturer panel-guide catalog, when the host app has
    registered one (none ships here)."""
    from .. import appliance_spec_registry
    try:
        return appliance_spec_registry.get_provider()
    except Exception:
        return None


def _config_label(bp, props):
    """The preset the run came from, by its button name."""
    items = ap.CONFIG_ITEMS.get(bp.get('APPLIANCE_TYPE'), ap.DEFAULT_CONFIG_ITEMS)
    for item in items:
        if item[0] == props.config:
            return item[1]
    return "Custom" if props.config == ap.CUSTOM_CONFIG else "Single"


def _block_h(block, s):
    kind = block[0]
    if kind == 'gap':
        return GROUP_GAP * s
    if kind == 'head':
        return (HEAD_H + ROW_GAP) * s
    if kind == 'face_cmds':
        return (BTN_H + ROW_GAP) * s
    if kind == 'run_cmds':
        return (BTN_H + ROW_GAP) * 2 * s
    if kind == 'grid':
        rows = _grid_rows(len(block[1]))
        return rows * (GRID_CELL_H + GRID_PAD) * s + ROW_GAP * s
    return (ROW_H + ROW_GAP) * s


# ---- Build ------------------------------------------------------------------

def build(rect, context):
    """Entries inside `rect`. Every entry is (kind, rect, ...):

        ('note',   rect, text)
        ('elev',   rect)                    the well, and a click sink
        ('kick',   rect)
        ('face',   rect, index, name, size) a face in the elevation
        ('rail',   rect)
        ('clip',   rect, track, thumb)      the scrolling half
        ('head',   rect, label)
        ('seg',    rect, index, value, label, active)
        ('field',  rect, key, label, value, value_rect, chip_rect, mode,
                   label_frac)
        ('btn',    rect, action, label, enabled, index)
        ('check',  rect, action, label, checked)
    """
    s = scale()
    x0, bottom, w, h = rect
    top = bottom + h
    bp = target(context)
    if bp is None:
        return [('note', (x0, top - ROW_H * s, w, ROW_H * s),
                 "Select an appliance.")]
    props = _props(bp)
    if not props.sections:
        return _build_empty(x0, top, w, s)

    entries = []
    dim_x, dim_z = _cage(bp)
    elev_h = 0.0
    if dim_x > 0 and dim_z > 0:
        elev_h = min(w * (dim_z / dim_x), h * ELEV_MAX_FRAC)
        elev_h = max(elev_h, min(ELEV_MIN_H * s, h * ELEV_MAX_FRAC))
        entries.extend(_elevation(bp, props, dim_x, dim_z,
                                  (x0, top - elev_h, w, elev_h), s))
        elev_h += ELEV_GAP * s

    # The fields scroll under the picture, which stays put: the point of
    # the picture is to be looked at while the fields are used.
    body_top = top - elev_h
    body_h = max(ROW_H * s, body_top - bottom)
    blocks = _blocks(context, bp)

    def _h(block):
        return _block_h(block, s)

    content_h = sum(_h(b) for b in blocks)
    list_h, _scrollable, reserve = _list.measure(content_h, body_h, ROW_H * s)
    _list.clamp(content_h, list_h)
    track, thumb = _list.bar_rects(x0, w, body_top, list_h, content_h, ROW_H * s)
    entries.append(('clip', (x0, body_top - list_h, w, list_h), track, thumb))
    row_w = w - reserve
    for block, b_top, _b_bottom in _list.visible(blocks, body_top,
                                                 body_top - list_h, _h):
        entries.extend(_block_entries(context, bp, block, x0, b_top, row_w, s))
    return entries


def _build_empty(x0, top, w, s):
    """Nothing built yet: say what the command does, and offer it."""
    y = top - (ROW_H + ROW_GAP) * s
    entries = [('note', (x0, y, w, ROW_H * s),
                "This appliance has no panels yet.")]
    y -= (BTN_H + ROW_GAP) * s
    entries.append(('btn', (x0, y, w, BTN_H * s), 'ADD_PANELS',
                    "Build Panels", True, -1))
    y -= (ROW_H + ROW_GAP) * s
    entries.append(('note', (x0, y, w, ROW_H * s),
                    "Doors and drawer fronts in the cabinet style."))
    return entries


def _elevation(bp, props, dim_x, dim_z, rect, s):
    """The appliance front, to scale, inside `rect`."""
    x0, y0, w, h = rect
    faces, _backers, rails = ap.solve(props, dim_x, dim_z)
    _solved['name'], _solved['faces'] = bp.name, faces
    px = min(w / dim_x, h / dim_z)          # px per metre
    fw, fh = dim_x * px, dim_z * px
    fx = x0 + (w - fw) / 2.0
    fy = y0 + (h - fh) / 2.0
    entries = [('elev', (fx, fy, fw, fh))]

    if props.toe_kick > 0.0:
        entries.append(('kick', (fx, fy, fw, props.toe_kick * px)))

    def _rect_of(box):
        bx0, bx1, bz0, bz1 = box[:4]
        return (fx + bx0 * px, fy + bz0 * px,
                (bx1 - bx0) * px, (bz1 - bz0) * px)

    for i in sorted(faces):
        sec = props.sections[i]
        r = _rect_of(faces[i])
        size = "%s x %s" % (_fmt(faces[i][1] - faces[i][0]),
                            _fmt(faces[i][3] - faces[i][2]))
        entries.append(('face', r, i, sec.label, size))
    for rail in rails:
        entries.append(('rail', _rect_of(rail)))
    return entries


def _block_entries(context, bp, block, x0, top, w, s):
    """One block, positioned. `top` is its top edge."""
    kind, payload = block
    props = _props(bp)
    if kind == 'gap':
        return []
    if kind == 'head':
        return [('head', (x0, top - HEAD_H * s, w, HEAD_H * s), payload)]
    if kind == 'kind':
        return _seg_entries(props, payload, x0, top, w, s)
    if kind == 'field':
        return _field_entries(bp, payload, x0, top, w, s)
    if kind == 'pick':
        return _pick_entries(payload, x0, top, w, s)
    if kind == 'grid':
        return _grid_entries(bp, payload, x0, top, w, s)
    if kind == 'note':
        return [('note', (x0, top - ROW_H * s, w, ROW_H * s), payload)]
    if kind == 'face_cmds':
        return _face_cmd_entries(props, payload, x0, top, w, s)
    if kind == 'run_cmds':
        return _run_cmd_entries(props, x0, top, w, s)
    if kind == 'rails':
        return _rail_entries(props, x0, top, w, s)
    return []


def _row_rects(x0, top, w, s, count, height, gaps=None):
    """`count` buttons filling the width, evenly, on one row."""
    gap = BTN_GAP * s
    each = (w - gap * (count - 1)) / count
    y = top - height
    return [(x0 + i * (each + gap), y, each, height) for i in range(count)]


def _seg_entries(props, index, x0, top, w, s):
    """What the face is: three buttons, the current one pressed. A
    segmented row rather than a dropdown -- there are only three, and
    seeing them all is the point."""
    sec = props.sections[index]
    rects = _row_rects(x0, top, w, s, len(ap.SECTION_KIND_ITEMS), ROW_H * s)
    out = []
    for r, item in zip(rects, ap.SECTION_KIND_ITEMS):
        out.append(('seg', r, index, item[0], item[1], sec.kind == item[0]))
    return out


def _field_entries(bp, payload, x0, top, w, s):
    """A labelled value: typed into, or a dropdown. A size that holds
    itself carries a chip that gives it back to the sharing.

    The label column is measured on the FULL row, so a row that gives up
    room to a chip still lines its value up with the rows that don't."""
    key, label, mode = payload
    owner, prop = _resolve(bp, key)
    if owner is None:
        return []
    row_h = ROW_H * s
    held_prop = _hold_prop(prop)
    gap_auto = prop in AUTO_GAP_PROPS
    own_gap = gap_auto and getattr(owner, prop, -1.0) >= 0.0
    chip_room = ((CHIP_W + BTN_GAP) * s
                 if (mode == 'SIZE' and (held_prop or own_gap)) else 0.0)
    rect = (x0, top - row_h, w - chip_room, row_h)
    chip_rect = None
    if chip_room:
        chip_rect = (x0 + w - CHIP_W * s, rect[1] + 2 * s,
                     CHIP_W * s, row_h - 4 * s)
    if mode == 'SIZE' and gap_auto:
        value = _fmt(_gap_value(_props(bp), prop))
    elif mode == 'SIZE':
        held = bool(getattr(owner, held_prop, False)) if held_prop else True
        value = _fmt(getattr(owner, prop, 0.0)) if held else _solved_text(bp, key)
    elif mode == 'MENU':
        value = enum_label(owner, prop)
    else:
        value = str(getattr(owner, prop, "") or "")
    label_w = w * 0.42
    frac = label_w / rect[2] if rect[2] > 0 else 0.42
    value_rect = (x0 + label_w, rect[1] + 2 * s,
                  rect[2] - label_w, row_h - 4 * s)
    return [('field', rect, key, label, value, value_rect, chip_rect, mode,
             frac)]


# ---- The layout grid ---------------------------------------------------------
# A preset is a shape, so it is picked from pictures of the shapes -- the
# same idea as picking a handle from the handles. The pictures are drawn
# from the solver rather than loaded: a preset's tile is laid out by the
# code that lays out the real run, so the two cannot disagree, and there
# are no thumbnails to keep up to date as the presets change.

GRID_COLS = 2
GRID_CELL_H = 118       # unscaled: the picture, plus its name under it
GRID_LABEL_H = 16
GRID_PAD = 4


def _preset_items(bp):
    """[(config, label)] this appliance can be laid out as, Custom
    excluded -- it is what a run BECOMES, never what it is set to."""
    items = ap.CONFIG_ITEMS.get(bp.get('APPLIANCE_TYPE'), ap.DEFAULT_CONFIG_ITEMS)
    return [(item[0], item[1]) for item in items if item[0] != ap.CUSTOM_CONFIG]


def _grid_rows(count):
    return max(1, (count + GRID_COLS - 1) // GRID_COLS)


def _grid_entries(bp, items, x0, top, w, s):
    """A cell per preset: its faces drawn to scale inside the tile."""
    props = _props(bp)
    dim_x, dim_z = _cage(bp)
    if dim_x <= 0 or dim_z <= 0:
        return []
    cell_w = (w - GRID_PAD * s * (GRID_COLS - 1)) / GRID_COLS
    cell_h = GRID_CELL_H * s
    out = []
    for i, (config, label) in enumerate(items):
        row, col = divmod(i, GRID_COLS)
        cx = x0 + col * (cell_w + GRID_PAD * s)
        cy = top - (row + 1) * cell_h - row * GRID_PAD * s
        cell = (cx, cy, cell_w, cell_h)
        # The picture sits above the name, at the appliance's own shape.
        pic = (cx + GRID_PAD * s, cy + GRID_LABEL_H * s,
               cell_w - 2 * GRID_PAD * s,
               cell_h - (GRID_LABEL_H + GRID_PAD) * s)
        sections, faces = ap.preview_faces(config, dim_x, dim_z, props)
        px = min(pic[2] / dim_x, pic[3] / dim_z)
        fw, fh = dim_x * px, dim_z * px
        fx = pic[0] + (pic[2] - fw) / 2.0
        fy = pic[1] + (pic[3] - fh) / 2.0
        preview = ap._PreviewProps(config, props)
        tiles = []
        for index, box in faces.items():
            section = sections[index] if index < len(sections) else None
            kind = section.kind if section is not None else 'DOOR'
            side = pull_side(preview, section) if section is not None else 'R'
            tiles.append(((fx + box[0] * px, fy + box[2] * px,
                           (box[1] - box[0]) * px, (box[3] - box[2]) * px),
                          kind, side))
        out.append(('preset', cell, config, label,
                    props.config == config, (fx, fy, fw, fh), tiles))
    return out


def _pick_entries(payload, x0, top, w, s):
    """A value that opens a list worked out as it opens -- the presets
    for this appliance, the makes in the catalog, that make's models.
    None of the three is an enum on the model, so none is a dropdown."""
    which, label, value = payload
    row_h = ROW_H * s
    rect = (x0, top - row_h, w, row_h)
    label_w = w * 0.42
    value_rect = (x0 + label_w, rect[1] + 2 * s, w - label_w, row_h - 4 * s)
    return [('pick', rect, which, label, value, value_rect)]


def _solved_value(bp, key):
    """What a size that shares currently works out to, in metres, from
    the solve this build already ran. None when it has no face."""
    props = _props(bp)
    faces = _solved['faces'] if _solved['name'] == bp.name else None
    if faces is None:
        dim_x, dim_z = _cage(bp)
        if dim_x <= 0 or dim_z <= 0:
            return None
        faces = ap.solve(props, dim_x, dim_z)[0]
    kind, idx, prop = key
    if kind == 'sec':
        box = faces.get(idx)
        if box is None:
            return None
        return (box[3] - box[2]) if prop == 'height' else (box[1] - box[0])
    if kind == 'col':
        for i, sec in enumerate(props.sections):
            if sec.column == idx and i in faces:
                return faces[i][1] - faces[i][0]
    return None


def _solved_text(bp, key):
    """The same, in words -- a face that shares still says how big it
    is, so the picture and the row agree."""
    value = _solved_value(bp, key)
    return _fmt(value) if value is not None else "shared"


def _face_cmd_entries(props, index, x0, top, w, s):
    sec = props.sections[index]
    peers = ap.peer_indices(props, index)
    pos = peers.index(index) if index in peers else 0
    removable = len(props.sections) > 1 and (sec.column < 0 or len(peers) > 1)
    rects = _row_rects(x0, top, w, s, 4, BTN_H * s)
    return [
        ('btn', rects[0], 'SPLIT', "Split", True, index),
        ('btn', rects[1], 'UP', "Up", pos + 1 < len(peers), index),
        ('btn', rects[2], 'DOWN', "Down", pos > 0, index),
        ('btn', rects[3], 'REMOVE', "Remove", removable, index),
    ]


def _run_cmd_entries(props, x0, top, w, s):
    """Two rows: what the run is made of sideways, then the faces that
    cross every column."""
    top_row = _row_rects(x0, top, w, s, 2, BTN_H * s)
    low = top - (BTN_H + ROW_GAP) * s
    low_row = _row_rects(x0, low, w, s, 2, BTN_H * s)
    return [
        ('btn', top_row[0], 'ADD_COLUMN', "Add Column",
         len(props.columns) < ap.MAX_COLUMNS, -1),
        ('btn', top_row[1], 'REMOVE_COLUMN', "Remove Column",
         len(props.columns) > 1, -1),
        ('btn', low_row[0], 'ADD_BANNER_TOP', "Full Face Above", True, -1),
        ('btn', low_row[1], 'ADD_BANNER_BOTTOM', "Full Face Below", True, -1),
    ]


def _rail_entries(props, x0, top, w, s):
    rects = _row_rects(x0, top, w, s, 3, ROW_H * s)
    return [
        ('check', rects[0], 'RAIL_TOP', "Top", props.rail_top),
        ('check', rects[1], 'RAIL_BOTTOM', "Bottom", props.rail_bottom),
        ('check', rects[2], 'RAIL_BETWEEN', "Between", props.rail_between),
    ]


# ---- Values -----------------------------------------------------------------

def _resolve(bp, key):
    """(owner, prop) for a field key. Resolved from the key every time
    rather than held: a property group is a wrapper around a lookup,
    and the list it indexes into changes under the tab."""
    kind, index, prop = key
    props = _props(bp)
    try:
        if kind == 'sec':
            return props.sections[index], prop
        if kind == 'col':
            return props.columns[index], prop
        return props, prop
    except (IndexError, KeyError):
        return None, None


# The gaps that can either carry their own size or follow the run's
# single one. -1 in the model means "following", which is never a size
# to show: the row shows what the gap measures, and its chip gives the
# size back.
AUTO_GAP_PROPS = {'reveal_top', 'reveal_bottom', 'reveal_left',
                  'reveal_right', 'column_gap'}


def _gap_value(props, prop):
    """What one of those gaps measures now."""
    if prop == 'column_gap':
        return ap.column_gap(props)
    return ap.reveal(props, prop.split('_', 1)[1])


def _hold_prop(prop):
    """The flag that says a size is held, for the sizes that have one."""
    return {
        'height': 'height_hold',
        'width': 'width_hold',
        'z_bottom': 'z_hold',
        'backer_width': 'backer_width_hold',
        'backer_height': 'backer_height_hold',
    }.get(prop)


def parse_distance(text):
    """Typed text -> metres. The placement tools' grammar, so "3/4",
    "1 1/2" and "2'6" mean here what they mean everywhere else."""
    from . import options_panel
    return options_panel.parse_distance(text)


# ---- Paint ------------------------------------------------------------------

def _clip(entries):
    for entry in entries:
        if entry[0] == 'clip':
            return entry
    return None


def paint(entries, mx, my):
    s = scale()
    font_id = 0
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    # Resolved once for the whole pass: every face and every held size
    # would otherwise walk back up to the appliance for itself.
    bp = target()
    selected = selected_index(bp) if bp is not None else -1

    # The picture first, unclipped: it sits above the scrolling half.
    for entry in entries:
        kind = entry[0]
        if kind == 'elev':
            draw_rect(shader, *entry[1], ELEV_BG)
            draw_rect_outline(shader, *entry[1], ELEV_BORDER)
        elif kind == 'kick':
            draw_rect(shader, *entry[1], KICK_BG)
        elif kind == 'face':
            _paint_face(shader, font_id, entry, mx, my, s, bp, selected)
        elif kind == 'rail':
            draw_rect(shader, *entry[1], RAIL_BG)
            draw_rect_outline(shader, *entry[1], FACE_BORDER)

    clip = _clip(entries)
    if clip is not None:
        if clip[2] is not None:
            draw_rect(shader, *clip[2], Theme.SCROLLBAR_TRACK)
            draw_rect(shader, *clip[3], Theme.SCROLLBAR_THUMB)
        prev = begin_clip(clip[1])
    else:
        prev = None
    try:
        for entry in entries:
            kind = entry[0]
            if kind == 'head':
                _, rect, label = entry
                draw_text(font_id, rect[0], rect[1] + 4 * s, SMALL * s,
                          Theme.TEXT_HEADER,
                          fit_text(font_id, SMALL * s, label.upper(), rect[2]))
                draw_rects(shader, [(rect[0], rect[1], rect[2], 1 * s)],
                           Theme.SEPARATOR)
            elif kind == 'note':
                _, rect, text = entry
                draw_text(font_id, rect[0], vcenter_baseline(rect, font_id,
                                                             FONT * s),
                          FONT * s, Theme.TEXT_DIM,
                          fit_text(font_id, FONT * s, text, rect[2]))
            elif kind == 'seg':
                _, rect, _index, _value, label, active = entry
                hot = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hot, active=active)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_PRIMARY if (active or hot)
                                   else Theme.TEXT_NORMAL, label)
            elif kind == 'btn':
                _, rect, _action, label, enabled, _index = entry
                hot = enabled and point_in_rect(mx, my, rect)
                if enabled:
                    paint_button(shader, rect, hovered=hot)
                else:
                    draw_rect_outline(shader, *rect, Theme.PANEL_BORDER)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_PRIMARY if hot
                                   else Theme.TEXT_NORMAL if enabled
                                   else Theme.TEXT_DIM, label)
            elif kind == 'check':
                _, rect, _action, label, checked = entry
                paint_check(shader, font_id, rect, FONT * s, label, checked,
                            point_in_rect(mx, my, rect), pad=3.0)
            elif kind == 'field':
                _paint_field(shader, font_id, entry, mx, my, s, bp)
            elif kind == 'preset':
                _paint_preset(shader, font_id, entry, mx, my, s)
            elif kind == 'pick':
                _, rect, _which, label, value, value_rect = entry
                paint_field(shader, font_id, rect, FONT * s, label, value,
                            point_in_rect(mx, my, value_rect))
    finally:
        if prev is not None:
            end_clip(prev)
    gpu.state.blend_set('NONE')


def _paint_face(shader, font_id, entry, mx, my, s, bp, selected_i):
    """A face in the elevation: filled, marked with what it is, and
    labelled when there is room for the text."""
    _, rect, index, label, size = entry
    selected = index == selected_i
    hot = point_in_rect(mx, my, rect)
    color = FACE_SEL if selected else FACE_HOVER if hot else FACE_BG
    draw_rect(shader, *rect, color)
    draw_rect_outline(shader, *rect, FACE_BORDER)
    if selected:
        draw_rect_outline(shader, rect[0] + 1 * s, rect[1] + 1 * s,
                          rect[2] - 2 * s, rect[3] - 2 * s, Theme.GLYPH_HOVER)
    props = _props(bp) if bp is not None else None
    if props is not None and 0 <= index < len(props.sections):
        section = props.sections[index]
        _paint_face_mark(shader, rect, section.kind, s,
                         pull_side(props, section))
    if rect[3] < FACE_MIN_LABEL_H * s:
        return
    x, y, w, h = rect
    pad = 4 * s
    name = fit_text(font_id, SMALL * s, label, w - 2 * pad)
    draw_text(font_id, x + pad, y + h - (SMALL + 4) * s, SMALL * s,
              FACE_TEXT, name)
    if h >= (FACE_MIN_LABEL_H + 12) * s:
        draw_text(font_id, x + pad, y + pad, SMALL * s, FACE_SUB,
                  fit_text(font_id, SMALL * s, size, w - 2 * pad))


def _paint_face_mark(shader, rect, kind, s, side='R'):
    """The mark that says door, drawer or fixed panel at a glance: a
    pull on the door's opening edge, a pull across the middle, or a
    cross."""
    x, y, w, h = rect
    if w < 14 * s or h < 14 * s:
        return
    if kind == 'DOOR':
        px = (x + 7 * s) if side == 'L' else (x + w - 7 * s)
        half = min(h * 0.18, 14 * s)
        cy = y + h / 2.0
        draw_lines(shader, [(px, cy - half), (px, cy + half)], FACE_MARK)
    elif kind == 'DRAWER':
        half = min(w * 0.22, 18 * s)
        cx, cy = x + w / 2.0, y + h / 2.0
        draw_lines(shader, [(cx - half, cy), (cx + half, cy)], FACE_MARK)
    else:
        i = 6 * s
        draw_lines(shader, [(x + i, y + i), (x + w - i, y + h - i),
                            (x + i, y + h - i), (x + w - i, y + i)],
                   (1.0, 1.0, 1.0, 0.18))


def _paint_preset(shader, font_id, entry, mx, my, s):
    """One layout tile: the shape it builds, drawn small, with its name
    under it. The current layout reads as pressed."""
    _, cell, _config, label, active, well, tiles = entry
    hot = point_in_rect(mx, my, cell)
    paint_button(shader, cell, hovered=hot, active=active)
    draw_rect(shader, *well, ELEV_BG)
    draw_rect_outline(shader, *well, ELEV_BORDER)
    fills = [rect for rect, _kind, _side in tiles]
    if fills:
        draw_rects(shader, fills, FACE_SEL if active else FACE_BG)
        draw_rect_outlines(shader, fills, FACE_BORDER)
    for rect, kind, side in tiles:
        _paint_face_mark(shader, rect, kind, s, side)
    label_rect = (cell[0], cell[1], cell[2], GRID_LABEL_H * s)
    draw_centered_text(font_id, label_rect, SMALL * s,
                       Theme.TEXT_PRIMARY if (hot or active)
                       else Theme.TEXT_NORMAL,
                       fit_text(font_id, SMALL * s, label, cell[2] - 6 * s))


def _paint_field(shader, font_id, entry, mx, my, s, bp):
    _, rect, key, label, value, value_rect, chip_rect, mode, frac = entry
    editing = _edit.editing(key)
    paint_field(shader, font_id, rect, FONT * s, label,
                "" if editing else value,
                point_in_rect(mx, my, value_rect) and not editing,
                label_frac=frac, caret=(mode == 'MENU'), active=editing)
    if editing:
        paint_inline_edit(shader, font_id, value_rect, FONT * s, _edit,
                          pad=6.0 * s)
    if chip_rect is not None:
        # A gap that carries its own size says Auto (follow the run's
        # again). A held face size says Fill (give it back to the
        # sharing); a shared one says Hold (keep what it measures now).
        gap = key[2] in AUTO_GAP_PROPS
        held = True if gap else _is_held(bp, key)
        hot = point_in_rect(mx, my, chip_rect)
        paint_button(shader, chip_rect, hovered=hot, active=held)
        draw_centered_text(font_id, chip_rect, SMALL * s,
                           Theme.TEXT_PRIMARY if (hot or held)
                           else Theme.TEXT_NORMAL,
                           "Auto" if gap else "Fill" if held else "Hold")


def _is_held(bp, key):
    if bp is None:
        return False
    owner, prop = _resolve(bp, key)
    hold = _hold_prop(prop) if owner is not None else None
    return bool(hold and getattr(owner, hold, False))


# ---- Clicks -----------------------------------------------------------------

def hit(context, mx, my, entries):
    bp = target(context)
    if bp is None:
        return False
    # A face is in the picture, which is above the clip, so it is
    # tested before anything the scrolling half claims.
    for entry in entries:
        if entry[0] == 'face' and point_in_rect(mx, my, entry[1]):
            select(bp, entry[2])
            _cancel_edit()
            tag_redraw()
            return True
    clip = _clip(entries)
    if clip is not None and not point_in_rect(mx, my, clip[1]):
        return False        # the panel swallows it; nothing here wants it
    for entry in entries:
        kind = entry[0]
        if kind == 'btn' and point_in_rect(mx, my, entry[1]):
            if entry[4]:
                _run(entry[2], index=entry[5])
            return True
        if kind == 'seg' and point_in_rect(mx, my, entry[1]):
            _run('KIND', index=entry[2], value=entry[3])
            return True
        if kind == 'check' and point_in_rect(mx, my, entry[1]):
            _run(entry[2])
            return True
        if kind == 'preset' and point_in_rect(mx, my, entry[1]):
            _set_grid(False)
            _run('CONFIG', value=entry[2])
            return True
        if kind == 'pick' and point_in_rect(mx, my, entry[5]):
            if entry[2] == 'CONFIG':
                # The layout is picked from the grid of shapes, not a
                # list of their names.
                _set_grid(not _grid_open)
            else:
                _open_pick(context, bp, entry[2], entry[3])
            return True
        if kind == 'field':
            (_, _rect, key, _label, _value, value_rect, chip_rect, mode,
             _frac) = entry
            if chip_rect is not None and point_in_rect(mx, my, chip_rect):
                _run('GAP_AUTO' if key[2] in AUTO_GAP_PROPS else 'HOLD',
                     index=0, value=_key_str(key))
                return True
            if point_in_rect(mx, my, value_rect):
                if mode == 'MENU':
                    _open_menu(context, bp, key, _label)
                else:
                    _begin_edit(bp, key, mode)
                return True
    return False


def _open_pick(context, bp, which, label):
    """The list behind Layout / Make / Model, worked out as it opens."""
    from . import options_panel
    op = home_builder_OT_appliance_panel_edit.bl_idname

    def _entries(_context):
        props = _props(bp)
        if which == 'CONFIG':
            items = ap.CONFIG_ITEMS.get(bp.get('APPLIANCE_TYPE'),
                                        ap.DEFAULT_CONFIG_ITEMS)
            return [(item[1], op, {'action': 'CONFIG', 'value': item[0]})
                    for item in items if item[0] != ap.CUSTOM_CONFIG]
        if which == 'BACKER':
            return [(item[1], op, {'action': 'BACKER_ALL', 'value': item[0]})
                    for item in ap.PANEL_TYPE_ITEMS]
        provider = _spec_provider()
        if provider is None:
            return []
        if which == 'MFR':
            rows = [("Manual", op, {'action': 'MFR', 'value': ""})]
            rows += [(m, op, {'action': 'MFR', 'value': m})
                     for m in provider.manufacturers()]
            return rows
        return [(d['model'], op, {'action': 'SPEC', 'value': d['model']})
                for d in provider.models(props.manufacturer)]

    options_panel.open_pick_menu(context, _entries, label)


def _open_menu(context, bp, key, label):
    """A dropdown is the panel's own enum picker, opened on the section
    or the run: a native menu, which dismisses and takes the keyboard
    the way every other menu in Blender does."""
    from . import options_panel
    owner, prop = _resolve(bp, key)
    if owner is not None:
        options_panel.open_enum_menu(context, owner, prop, label)


def _begin_edit(bp, key, mode):
    """Click into a value and type it. A size starts empty (a size is
    typed fresh); a name starts selected, so typing replaces it."""
    global _edit_key
    owner, prop = _resolve(bp, key)
    if owner is None:
        return
    _edit_key = key
    if mode == 'TEXT':
        _edit.begin(key, str(getattr(owner, prop, "") or ""), select=True)
    else:
        _edit.begin(key, '')
    try:
        bpy.ops.home_builder.appliance_panel_edit_value('INVOKE_DEFAULT')
    except Exception as ex:
        print('Home Builder: panel value edit failed: %s' % ex)
        _cancel_edit()
    tag_redraw()


def _cancel_edit():
    global _edit_key
    _edit.cancel()
    _edit_key = None


def commit_edit(context):
    """Write what was typed. A size that is typed is a size that is
    wanted, so it holds itself -- the run shares what is left between
    the faces that have none."""
    global _edit_key
    key, text = _edit_key, _edit.text
    _edit.cancel()
    _edit_key = None
    bp = target(context)
    if bp is None or key is None:
        return
    _run('SET', index=0, value="%s|%s" % (_key_str(key), text))


def _key_str(key):
    return "%s:%s:%s" % key


def _key_from_str(text):
    kind, index, prop = text.split(':', 2)
    return (kind, int(index), prop)


def scroll(mx, my, entries, rows):
    clip = _clip(entries)
    if clip is None or not point_in_rect(mx, my, clip[1]):
        return False
    _list.scroll_by(rows, ROW_H * scale())
    tag_redraw()
    return True


def _run(action, index=-1, value=""):
    try:
        bpy.ops.home_builder.appliance_panel_edit(
            'INVOKE_DEFAULT', action=action, index=index, value=value)
    except Exception as ex:
        print('Home Builder: panel %s failed: %s' % (action, ex))


def tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---- Operators --------------------------------------------------------------

class home_builder_OT_appliance_panel_edit(bpy.types.Operator):
    """Change the appliance's panel layout"""
    bl_idname = "home_builder.appliance_panel_edit"
    bl_label = "Edit Appliance Panels"
    # One operator for every command the tab runs, so each is its own
    # undo step -- the panel's click handler is not.
    bl_options = {'INTERNAL', 'UNDO'}

    action: bpy.props.StringProperty()  # type: ignore
    index: bpy.props.IntProperty(default=-1)  # type: ignore
    value: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return target(context) is not None

    def execute(self, context):
        bp = target(context)
        props = bp.appliance_panels
        act = self.action
        index = self.index if self.index >= 0 else selected_index(bp)

        if act == 'ADD_PANELS':
            ap.seed_from_legacy(bp)
            if not props.sections:
                ap.seed_preset(bp, default_config(bp), keep_options=False)
            ap.rebuild(bp)
            select(bp, 0)
        elif act == 'SPLIT':
            new = ap.split_section(bp, index, self._solved_height(bp, index))
            if new >= 0:
                select(bp, new)
        elif act == 'REMOVE':
            if ap.remove_section(bp, index):
                select(bp, max(0, index - 1))
            else:
                self.report({'INFO'}, "A column keeps its last face - remove "
                                      "the column instead")
        elif act in ('UP', 'DOWN'):
            peers = ap.peer_indices(props, index)
            if ap.move_section(bp, index, 1 if act == 'UP' else -1):
                pos = peers.index(index) + (1 if act == 'UP' else -1)
                select(bp, peers[pos])
        elif act == 'ADD_COLUMN':
            ci = ap.add_column(bp)
            if ci < 0:
                self.report({'INFO'}, "Panels are limited to %d columns"
                            % ap.MAX_COLUMNS)
            else:
                select(bp, next((i for i, s in enumerate(props.sections)
                                 if s.column == ci), 0))
        elif act == 'REMOVE_COLUMN':
            column = props.sections[index].column if index < len(props.sections) else -1
            if column < 0 or not ap.remove_column(bp, column):
                self.report({'INFO'}, "The last column can't be removed")
            else:
                select(bp, 0)
        elif act in ('ADD_BANNER_TOP', 'ADD_BANNER_BOTTOM'):
            where = 'TOP' if act.endswith('TOP') else 'BOTTOM'
            kind = 'PANEL' if where == 'TOP' else 'DRAWER'
            new = ap.add_section(bp, -1, kind, where)
            if new >= 0:
                select(bp, new)
        elif act == 'KIND':
            if 0 <= index < len(props.sections):
                props.sections[index].kind = self.value
        elif act in ('RAIL_TOP', 'RAIL_BOTTOM', 'RAIL_BETWEEN'):
            prop = act.lower()
            setattr(props, prop, not getattr(props, prop))
        elif act == 'CONFIG':
            ap.seed_preset(bp, self.value, keep_options=True)
            ap.rebuild(bp)
            select(bp, 0)
        elif act == 'MFR':
            props.manufacturer = self.value
            props.model = ""
        elif act == 'SPEC':
            self._apply_spec(context, bp)
        elif act == 'BACKER_ALL':
            props.panel_type = self.value
            for section in props.sections:
                if section.backer != 'DEFAULT':
                    section.backer = 'DEFAULT'
        elif act == 'GAP_AUTO':
            owner, prop = _resolve(bp, _key_from_str(self.value))
            if owner is not None and prop in AUTO_GAP_PROPS:
                setattr(owner, prop, -1.0)
        elif act == 'HOLD':
            self._toggle_hold(bp)
        elif act == 'SET':
            self._set_value(bp)
        else:
            return {'CANCELLED'}
        tag_redraw()
        return {'FINISHED'}

    # -- helpers ----------------------------------------------------------

    def _solved_height(self, bp, index):
        """What the face measures now, so the two halves start where the
        one was rather than at a default."""
        dim_x, dim_z = _cage(bp)
        if dim_x <= 0 or dim_z <= 0:
            return None
        faces, _b, _r = ap.solve(bp.appliance_panels, dim_x, dim_z)
        box = faces.get(index)
        return (box[3] - box[2]) if box else None

    def _apply_spec(self, context, bp):
        """Fill the run from a manufacturer's panel guide -- every face
        and backer at the size the maker publishes, held.

        The guide's own layout is seeded FIRST where it names one: the
        sizes are filled into the faces that are there, so the shape has
        to be the guide's shape before they can land on it.
        """
        import json
        provider = _spec_provider()
        if provider is None:
            return
        props = bp.appliance_panels
        try:
            spec = provider.resolve(props.manufacturer, self.value)
        except Exception as ex:
            print('Home Builder: appliance spec resolve failed: %s' % ex)
            self.report({'WARNING'}, "That panel guide could not be read")
            return
        cfg = spec.get('operator_config')
        if cfg:
            ap.seed_preset(bp, cfg, keep_options=True)
        notes = ap.apply_spec(bp, spec) or []
        bp['APPLIANCE_PANEL_SPEC'] = json.dumps({
            'manufacturer': spec.get('manufacturer'),
            'model': spec.get('model'),
            'weight_max_lb': spec.get('weight_max_lb'),
            'panel_thickness': spec.get('panel_thickness'),
            'panels': spec.get('panels'),
            'flags': spec.get('flags'),
            'source_url': spec.get('source_url'),
        })
        ap.rebuild(bp)
        select(bp, 0)
        for note in notes[:2]:
            self.report({'WARNING'}, note)

    def _toggle_hold(self, bp):
        """Fill / Hold: a size gives itself back to the sharing, or
        keeps what it measures right now -- so holding a size never
        moves the face it is holding."""
        key = _key_from_str(self.value)
        owner, prop = _resolve(bp, key)
        hold = _hold_prop(prop) if owner is not None else None
        if not hold:
            return
        if getattr(owner, hold):
            setattr(owner, hold, False)
            return
        current = _solved_value(bp, key)
        if current:
            setattr(owner, prop, current)
        setattr(owner, hold, True)

    def _set_value(self, bp):
        key_str, _, text = self.value.partition('|')
        key = _key_from_str(key_str)
        owner, prop = _resolve(bp, key)
        if owner is None:
            return
        if isinstance(getattr(owner, prop, None), str):
            if text:
                setattr(owner, prop, text)
            return
        metres = parse_distance(text)
        if metres is None:
            return
        try:
            setattr(owner, prop, metres)
        except Exception as ex:
            print('Home Builder: %s not set: %s' % (prop, ex))
            return
        hold = _hold_prop(prop)
        if hold:
            setattr(owner, hold, True)


class home_builder_OT_appliance_panel_edit_value(bpy.types.Operator):
    """Type a value into the panel field.

    Modal only while the typing lasts -- Enter commits, Esc cancels, a
    click anywhere commits -- because Blender skips autosave for as long
    as any modal is running. The sibling of the Options tab's field
    editor; the grammar itself is in InlineEdit, shared with it.
    """
    bl_idname = "home_builder.appliance_panel_edit_value"
    bl_label = "Edit Panel Value"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _edit.active

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if _edit.mouse(event, event.mouse_region_x, event.mouse_region_y):
            tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}
        result = _edit.feed(event)
        if result in ('COMMIT', 'NEXT', 'PREV'):
            commit_edit(context)
            tag_redraw()
            return {'FINISHED'}
        if result == 'CANCEL':
            _cancel_edit()
            tag_redraw()
            return {'CANCELLED'}
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS':
            commit_edit(context)
            tag_redraw()
            return {'FINISHED'}
        tag_redraw()
        return {'RUNNING_MODAL'}


classes = (
    home_builder_OT_appliance_panel_edit,
    home_builder_OT_appliance_panel_edit_value,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    from . import scene_navigator
    scene_navigator.register_tab(TAB_KEY, sys.modules[__name__],
                                 label=TAB_LABEL, order=TAB_ORDER,
                                 available=available)


def unregister():
    from . import scene_navigator
    try:
        scene_navigator.unregister_tab(TAB_KEY)
    except Exception:
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
