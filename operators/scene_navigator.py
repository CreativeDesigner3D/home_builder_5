"""
Scene Navigator -- GPU-drawn quick scene picker for Home Builder 5.

A modal overlay listing project scenes grouped by Rooms / Layout Views /
Details. The panel header shows the current scene and carries a pin
toggle; clicking a row switches scenes. When pinned, the navigator stays
open after a switch so several scenes can be picked in a row -- otherwise
it closes on the first pick. Room rows carry rename and delete buttons,
and a New Room button sits at the bottom -- each of those closes the
navigator and opens the corresponding operator dialog. Click outside /
Esc / RMB dismisses.

The panel sizes itself to its longest name (within limits; longer names are
ellipsized), its list is clamped to the viewport and scrolls with the mouse
wheel, and section headers click to collapse.
"""

import bpy
import gpu
import blf

from ..hb_gpu_draw import (
    get_visible_window_bounds as _get_visible_window_bounds,
    draw_rect as _draw_rect,
    draw_rect_outline as _draw_rect_outline,
    draw_lines as _draw_lines,
    draw_text as _draw_text,
    vcenter_baseline as _vcenter_baseline,
    point_in_rect as _point_in_rect,
)
# Widget layer: UI scale, text fitting, the glyph set, the panel/button
# paint idioms and the scrolling-list arithmetic. Everything here that is
# not about SCENES lives there, so the next viewport panel starts from it
# instead of copying this file.
from ..hb_gpu_ui import (
    Theme,
    paint_button as _paint_button,
    draw_centered_text as _draw_centered_text,
    ScrollList,
    scale as _s,
    text_width as _text_w,
    fit_text as _fit_text,
    panel_box as _panel_box,
    paint_frame as _paint_frame,
    glyph_delete as _draw_delete_glyph,
    glyph_plus as _draw_plus_glyph,
    glyph_pin as _draw_pin_glyph,
    glyph_chevron as _draw_chevron,
    begin_clip as _begin_clip,
    end_clip as _end_clip,
    InlineEdit as _InlineEdit,
)


# ---- Layout constants -------------------------------------------------------
# All in unscaled pixels -- every one is multiplied by _s() at use, so the
# panel tracks Blender's UI scale instead of shrinking on high-DPI screens.

PANEL_TOP_MARGIN      = 12      # distance from top of visible window region
PANEL_BOTTOM_MARGIN   = 12      # the panel never reaches closer to the bottom
PANEL_MIN_WIDTH       = 250     # floor for the fixed width (see panel_width)
PANEL_MAX_WIDTH       = 440     # ceiling, so a wide tab can't take the viewport
PANEL_PADDING_X       = 10
PANEL_PADDING_Y       = 8

ROW_HEIGHT            = 24
SECTION_GAP           = 6
SECTION_HEADER_HEIGHT = 22
SECTION_CHEVRON_W     = 12      # collapse chevron column ahead of the label
ACCENT_WIDTH          = 3
ACCENT_LEFT_PAD       = 6
ROW_TEXT_LEFT_PAD     = ACCENT_LEFT_PAD + ACCENT_WIDTH + 8
ROW_TEXT_RIGHT_PAD    = 8       # gap kept between text and the row's right edge
PARENT_MIN_NAME_W     = 60      # drop the parent prefix if the name gets narrower

LIST_MIN_ROWS         = 3       # scrolling list never shrinks below this
SCROLL_STEP_ROWS      = 2       # rows per wheel notch
SCROLLBAR_WIDTH       = 4
SCROLLBAR_PAD         = 4

PANEL_HEADER_HEIGHT   = 26

ACTION_BTN_SIZE       = 18
PIN_BTN_WIDTH         = 30      # fits the word PIN
ACTION_BTN_GAP        = 4
ACTION_BTN_RIGHT_PAD  = 5
NEW_ROOM_BTN_HEIGHT   = 26
NEW_ROOM_GAP          = 8

ROW_FONT_SIZE         = 12
HEADER_FONT_SIZE      = 10
PARENT_FONT_SIZE      = 11

# ---- Colors -----------------------------------------------------------------

COLOR_ROOMS    = (0.59, 0.77, 0.35)
COLOR_LAYOUTS  = (0.52, 0.72, 0.92)
COLOR_DETAILS  = (0.94, 0.62, 0.15)

# Panel chrome comes from the shared palette; only the three section
# accents above are this panel's own.
PANEL_BG       = Theme.PANEL_BG
PANEL_BORDER   = Theme.PANEL_BORDER

ROW_HOVER_BG   = Theme.ROW_HOVER_BG

TEXT_PRIMARY   = Theme.TEXT_PRIMARY
TEXT_NORMAL    = Theme.TEXT_NORMAL
TEXT_DIM       = Theme.TEXT_DIM
HEADER_TEXT    = Theme.TEXT_HEADER

ACTION_BG              = Theme.ACTION_BG
ACTION_HOVER_BG        = Theme.ACTION_HOVER_BG
ACTION_DELETE_HOVER_BG = Theme.ACTION_DANGER_BG
ACTION_GLYPH           = Theme.GLYPH
ACTION_GLYPH_HOVER     = Theme.GLYPH_HOVER
NEW_ROOM_BG            = Theme.NEUTRAL_BG
NEW_ROOM_HOVER_BG      = Theme.ACCENT_BG
SEPARATOR_COLOR        = Theme.SEPARATOR

PIN_GLYPH              = Theme.GLYPH
PIN_GLYPH_ACTIVE       = Theme.GLYPH_HOVER
PIN_ACTIVE_BG          = Theme.ACCENT_BG

SCROLLBAR_TRACK        = Theme.SCROLLBAR_TRACK
SCROLLBAR_THUMB        = Theme.SCROLLBAR_THUMB


# ---- Module state -----------------------------------------------------------

# When pinned, the navigator stays open after a scene is picked so several
# scenes can be switched in a row. Clicking away (or Esc) still closes it.
# Sticky for the session -- a module global, intentionally not per-instance.
_pinned = False

# Whether the panel is showing at all. Pinning is a separate question:
# an OPEN panel is usable -- browse the library, pick a style -- but any
# action that does something to the scene closes it again, the way a
# menu does. PINNED means it survives those actions and stays up while
# you work. Both states are painted by the persistent HUD; neither runs
# a modal, so autosave keeps working (see viewport_hud).
_open = False

# Inline rename: the scene being renamed and the text so far. A room is
# renamed in place in the list rather than through a dialog -- the name
# is right there, and a modal popping over the viewport to change one
# string is a lot of ceremony. Held here so the painter can draw the
# field and the caret; the modal operator below owns the keystrokes.
# The inline rename field. The buffer and typing grammar live in the
# widget layer now; what stays here is which scene is being renamed and
# what renaming one means.
_edit = _InlineEdit()

# The section list's scroll state + scrollbar geometry. Sticky for the
# session, the way a real scrollbar behaves. _build_layout clamps it and
# nudges it so the current scene's row is in view whenever the current
# scene changes -- otherwise the user's own scrolling wins.
_list = ScrollList(bar_width=SCROLLBAR_WIDTH, bar_pad=SCROLLBAR_PAD,
                   min_rows=LIST_MIN_ROWS)
_last_current = None

# Section labels the user has collapsed (sticky for the session). Switching
# into a scene re-expands the section that contains it.
_collapsed = set()

# ---- Tabs -------------------------------------------------------------------
# The panel is a shell: it owns the frame, the header, the pin and the tab
# strip, and hands its body to whichever tab is active. Only one body is
# ever built or painted, so an inactive tab costs nothing.
#
# A provider is a module exposing:
#     build(content_rect, context) -> entries      (its own tuple shapes)
#     paint(entries, mx, my)
#     hit(context, mx, my, entries) -> bool        True = click consumed
#     scroll(mx, my, entries, rows) -> bool        True = wheel consumed
# ROOMS is built inline below; the other two delegate.

TAB_ROOMS = 'ROOMS'
TAB_LIBRARY = 'LIBRARY'
TAB_STYLES = 'STYLES'
TABS = (TAB_ROOMS, TAB_LIBRARY, TAB_STYLES)     # the built-in tabs

_active_tab = TAB_ROOMS

# Contributed tabs. An add-on built on this one may have a whole area of
# its own -- a job, a report, a set of documents -- that belongs beside
# these rather than crammed into one of them. It registers a tab here and
# supplies the provider that draws the body, so this module hosts it
# without knowing what it is. With nothing registered the panel is
# exactly the three tabs it was.
_extra_tabs = []         # (order, key, label, available_fn)


def register_tab(key, module, label=None, order=100, available=None):
    """Add a tab and the provider that draws it.

    `label` is what the tab button says (the key, if omitted) -- a key
    has to be stable and unique, and those make poor button text.
    `available` is an optional callable(scene) deciding where the tab
    applies, the same judgement `tab_available` makes for the built-ins.
    Sorted by (order, key); built-ins take an implicit order from their
    position, spaced so a contribution can land between two of them.
    Re-registering a key replaces it, so a reloaded add-on cannot stack
    duplicates.
    """
    unregister_tab(key)
    _extra_tabs.append((order, key, label or key, available))
    _extra_tabs.sort(key=lambda t: (t[0], t[1]))
    _providers[key] = module


def unregister_tab(key):
    global _active_tab
    for i, tab in enumerate(list(_extra_tabs)):
        if tab[1] == key:
            del _extra_tabs[i]
            _providers.pop(key, None)
            if _active_tab == key:
                _active_tab = TAB_ROOMS
            return


def tabs():
    """Every tab, built-in and contributed, in display order."""
    rows = [(i * 10, t) for i, t in enumerate(TABS)]
    rows.extend((t[0], t[1]) for t in _extra_tabs)
    rows.sort(key=lambda row: (row[0], row[1]))
    return tuple(row[1] for row in rows)


def tab_label(tab):
    for _order, key, label, _available in _extra_tabs:
        if key == tab:
            return label
    return tab


def tab_available(tab, scene=None):
    """Whether a tab makes sense for this scene.

    The library places cabinets, which a 2D sheet cannot do, so it is
    hidden there rather than offering a grid whose every click would
    be a no-op. A contributed tab answers for itself.
    """
    if scene is None:
        scene = bpy.context.scene
    for _order, key, _label, available in _extra_tabs:
        if key == tab:
            if available is None:
                return True
            try:
                return bool(available(scene))
            except Exception:
                return False        # never let a contribution break the HUD
    if tab == TAB_LIBRARY:
        return not (scene and scene.get('IS_LAYOUT_VIEW'))
    return True


def available_tabs(scene=None):
    return tuple(t for t in tabs() if tab_available(t, scene))


def resolve_active_tab(scene=None):
    """The active tab, falling back when it is not available here.

    Called on every layout and paint, so switching to a sheet while the
    library is showing lands on Rooms instead of a blank panel. The
    membership test covers a contributed tab that has since gone away
    with its add-on -- otherwise the panel would open on a tab that no
    longer has a provider, and draw nothing at all.
    """
    global _active_tab
    if _active_tab not in tabs() or not tab_available(_active_tab, scene):
        _active_tab = TAB_ROOMS
    return _active_tab
_providers = {}          # tab key -> provider module


# Room actions: extra buttons on the ROOMS tab, contributed by whoever
# owns the command. Downstream add-ons have room-level commands worth
# reaching from here, and this module must not depend on any of them.
# They register themselves at startup; nothing here learns their names.
_room_actions = []       # (order, key, label, operator, kwargs)


def register_room_action(key, label, operator, kwargs=None, order=100):
    """Add a button to the ROOMS tab. Re-registering a key replaces it,
    so a reloaded add-on does not stack duplicates."""
    unregister_room_action(key)
    _room_actions.append((order, key, label, operator, dict(kwargs or {})))
    _room_actions.sort(key=lambda a: (a[0], a[2]))


def unregister_room_action(key):
    for i, action in enumerate(list(_room_actions)):
        if action[1] == key:
            del _room_actions[i]
            return


def room_actions():
    return tuple(_room_actions)


def register_provider(tab, module):
    """Wire a body provider for a tab. Called at addon registration so
    this module needs no import of (and no dependency on) the panels it
    hosts."""
    _providers[tab] = module


def panel_width(s=1.0):
    """The panel's width, in pixels at UI scale `s`.

    One width for every tab, on purpose. Sizing each tab to its own
    content made the panel jump wider or narrower as you switched, and
    the tool palette -- which sits to its right -- jumped with it. A
    constant width keeps both still, so the tabs feel like pages of one
    panel rather than three panels sharing a corner.

    The number is still derived rather than picked: the widest thing
    any tab asks for, floored at the panel minimum.
    """
    want = [PANEL_MIN_WIDTH]
    for provider in _providers.values():
        want.append(getattr(provider, 'PREFERRED_WIDTH', PANEL_MIN_WIDTH))
    return max(want) * s


def active_tab():
    return resolve_active_tab()


def set_active_tab(tab):
    global _active_tab
    if tab in tabs():
        _active_tab = tab


# ---- Scale ------------------------------------------------------------------

# ---- Scene helpers ----------------------------------------------------------

def _is_room(scene):
    return not scene.get('IS_LAYOUT_VIEW') and not scene.get('IS_DETAIL_VIEW')

def is_room(scene):
    """A 3D room scene -- not a 2D layout sheet, not a detail card.

    The public form of the test this module groups scenes by, so a
    caller that needs to ask the same question (the HUD's Back button,
    say) agrees with the navigator by construction rather than by
    keeping its own copy of the two flags.
    """
    return scene is not None and _is_room(scene)


def _is_layout(scene):
    return bool(scene.get('IS_LAYOUT_VIEW'))

def _is_detail(scene):
    return bool(scene.get('IS_DETAIL_VIEW'))

def _sort_key(scene):
    so = 0
    if hasattr(scene, 'home_builder'):
        so = getattr(scene.home_builder, 'sort_order', 0) or 0
    return (so, scene.name.lower())

def sort_key(scene):
    """Public form of the order the navigator lists scenes in."""
    return _sort_key(scene)


def _parent_room_name(scene):
    """Resolve a layout view's source wall back to the room scene that owns it.

    Returns None when the layout view's own name already leads with that
    room name -- shown as a parent prefix it would just duplicate the room
    name the row already displays."""
    sw_name = scene.get('SOURCE_WALL')
    if not sw_name:
        return None
    wall = bpy.data.objects.get(sw_name)
    if not wall:
        return None
    for us in wall.users_scene:
        if _is_room(us):
            if scene.name.lower().startswith(us.name.lower()):
                return None
            return us.name
    return None

def _collect_groups():
    """Return list of (label, color, sorted_scenes, parent_fn) for non-empty sections."""
    rooms, layouts, details = [], [], []
    for s in bpy.data.scenes:
        if _is_layout(s):
            layouts.append(s)
        elif _is_detail(s):
            details.append(s)
        else:
            rooms.append(s)
    rooms.sort(key=_sort_key)
    layouts.sort(key=_sort_key)
    details.sort(key=_sort_key)
    raw = [
        ('ROOMS',        COLOR_ROOMS,   rooms,   None),
        ('LAYOUT VIEWS', COLOR_LAYOUTS, layouts, _parent_room_name),
        ('DETAILS',      COLOR_DETAILS, details, None),
    ]
    return [g for g in raw if g[2]]

# ---- Layout computation -----------------------------------------------------

def _build_layout(region, area, current_scene_name,
                  anchor_x=-1.0, anchor_top=-1.0):
    """Compute panel rect + entry rects from current region size and scenes.

    The panel is as wide as its longest row (clamped to MIN/MAX and the
    viewport); the section list is clamped to the viewport height and
    scrolls -- rows scrolled out of the clip rect are omitted, partially
    visible ones are kept (the painter clips them, hit-testing checks the
    clip rect). Collapsed sections contribute only their header.

    Returns (panel_rect, entries). panel_rect is (x, y, w, h) in region px
    (y is the bottom edge). entries is a list of tuples:
        ('panel_header', current_scene_name, rect, pin_rect)
        ('list', clip_rect, track_rect_or_None, thumb_rect_or_None)
        ('header', label, color, rect, collapsed, count)
        ('row', scene, parent, color, is_current, rect,
                delete_rect_or_None)
        ('new_room', rect)
    Room rows carry rename/delete sub-rects; other rows carry None.
    """
    global _last_current
    groups = _collect_groups()

    s = _s()
    panel_hdr_h = PANEL_HEADER_HEIGHT * s
    section_gap = SECTION_GAP * s
    section_hdr_h = SECTION_HEADER_HEIGHT * s
    row_h = ROW_HEIGHT * s
    new_room_gap = NEW_ROOM_GAP * s
    new_room_h = NEW_ROOM_BTN_HEIGHT * s
    pad_x = PANEL_PADDING_X * s
    pad_y = PANEL_PADDING_Y * s
    btn = ACTION_BTN_SIZE * s
    btn_gap = ACTION_BTN_GAP * s
    btn_right_pad = ACTION_BTN_RIGHT_PAD * s
    row_font = ROW_FONT_SIZE * s
    parent_font = PARENT_FONT_SIZE * s
    hdr_font = HEADER_FONT_SIZE * s
    font_id = 0

    # A scene switch re-expands its section and re-targets the scroll.
    current_changed = current_scene_name != _last_current
    _last_current = current_scene_name
    if current_changed:
        for label, _c, scenes, _p in groups:
            if any(sc.name == current_scene_name for sc in scenes):
                _collapsed.discard(label)

    # ---- Flatten the list into items + measure the widest row ----------
    # items: (kind, payload, height, needed_w) in display order.
    room_reserve = btn_right_pad + btn + 6 * s
    plain_reserve = ROW_TEXT_RIGHT_PAD * s
    text_left = ROW_TEXT_LEFT_PAD * s
    items = []
    for i, (label, color, scenes, parent_fn) in enumerate(groups):
        collapsed = label in _collapsed
        if i > 0:
            items.append(('gap', None, section_gap, 0.0))
        hdr_w = (SECTION_CHEVRON_W * s + _text_w(font_id, hdr_font, label)
                 + (_text_w(font_id, hdr_font, f"  {len(scenes)}")
                    if collapsed else 0.0))
        items.append(('header', (label, color, collapsed, len(scenes)),
                      section_hdr_h, hdr_w))
        if collapsed:
            continue
        for sc in scenes:
            parent = parent_fn(sc) if parent_fn else None
            tw = _text_w(font_id, row_font, sc.name)
            if parent:
                tw += _text_w(font_id, parent_font, parent + "  ·  ")
            reserve = room_reserve if _is_room(sc) else plain_reserve
            items.append(('row', (sc, parent, color), row_h,
                          text_left + tw + reserve))
    list_h_full = sum(it[2] for it in items)

    # ---- Panel geometry --------------------------------------------------
    bounds = _get_visible_window_bounds(area)
    y_min, y_max = bounds[2], bounds[3]
    margin = PANEL_TOP_MARGIN * s
    panel_top = anchor_top if anchor_top >= 0.0 else y_max - margin

    action_rows = (len(_room_actions) + 2) // 3     # three per row
    actions_h = action_rows * (new_room_h + 3 * s)
    fixed_h = (pad_y * 2 + panel_hdr_h + section_gap
               + actions_h
               + new_room_gap + new_room_h)
    tab = resolve_active_tab()
    is_rooms = tab == TAB_ROOMS
    avail_h = panel_top - (y_min + PANEL_BOTTOM_MARGIN * s)
    if is_rooms:
        max_list_h = avail_h - fixed_h
        list_h, scrollable, sb_reserve = _list.measure(
            list_h_full, max_list_h, row_h)
        panel_h = fixed_h + list_h
    else:
        # A hosted body takes the height it can get; the provider scrolls
        # its own content inside the rect it is handed.
        list_h, scrollable, sb_reserve = 0.0, False, 0.0
        panel_h = avail_h

    hdr_needed = (_text_w(font_id, hdr_font, "CURRENT") + 8 * s
                  + _text_w(font_id, row_font, current_scene_name)
                  + 8 * s + btn + btn_right_pad)
    # Fixed width, whichever tab is showing -- see panel_width().
    # hdr_needed and the per-row widths still drive text fitting; they
    # just no longer drive the panel's size.
    _ = hdr_needed
    needed_w = panel_width(s)
    # Anchored under a specific button (the viewport HUD trigger) or
    # centred in the visible window area; either way clamped on screen.
    panel_rect = _panel_box(bounds, needed_w, panel_h,
                            PANEL_MIN_WIDTH * s, PANEL_MAX_WIDTH * s,
                            margin, anchor_x, anchor_top)
    panel_x, panel_y, panel_w, _panel_h = panel_rect
    content_x = panel_x + pad_x
    content_w = panel_w - pad_x * 2
    entries = []

    # ---- Panel header ----------------------------------------------------
    cursor_y = panel_top - pad_y
    ph_rect = (content_x, cursor_y - panel_hdr_h, content_w, panel_hdr_h)
    pin_w = PIN_BTN_WIDTH * s
    pin_y = ph_rect[1] + (panel_hdr_h - btn) / 2.0
    pin_x = content_x + content_w - btn_right_pad - pin_w
    pin_rect = (pin_x, pin_y, pin_w, btn)
    entries.append(('panel_header', current_scene_name, ph_rect, pin_rect))
    cursor_y -= panel_hdr_h + section_gap


    if not is_rooms:
        # Hosted tab: hand the remaining space to its provider and let
        # it own everything below the strip -- its own scroll, its own
        # entry shapes, its own hit-testing.
        body_rect = (content_x, panel_y + pad_y, content_w,
                     cursor_y - (panel_y + pad_y))
        provider = _providers.get(tab)
        if provider is not None:
            entries.append(('body', tab, body_rect))
            try:
                entries.extend(provider.build(body_rect, bpy.context))
            except Exception as ex:      # a broken tab must not kill the panel
                print('Home Builder: %s tab failed to build: %s'
                      % (tab, ex))
        return panel_rect, entries
    # ---- Scrolling list --------------------------------------------------
    list_top = cursor_y
    list_bottom = list_top - list_h
    row_w = content_w - sb_reserve
    track_rect = thumb_rect = None
    if scrollable:
        # Bring the current scene's row into view on a scene switch.
        if current_changed:
            off = 0.0
            for kind, payload, h, _w in items:
                if kind == 'row' and payload[0].name == current_scene_name:
                    _list.scroll_into_view(off, h, list_h)
                    break
                off += h
        _list.clamp(list_h_full, list_h)
        track_rect, thumb_rect = _list.bar_rects(
            content_x, content_w, list_top, list_h, list_h_full, row_h)
    else:
        _list.offset = 0.0
    clip_rect = (content_x, list_bottom, content_w, list_h)
    entries.append(('list', clip_rect, track_rect, thumb_rect))

    for item, item_top, item_bot in _list.visible(
            items, list_top, list_bottom, lambda it: it[2]):
        kind, payload, h, _w = item
        if kind == 'gap':
            continue
        if kind == 'header':
            label, color, collapsed, count = payload
            entries.append(('header', label, color,
                            (content_x, item_bot, row_w, h),
                            collapsed, count))
        else:
            sc, parent, color = payload
            row_rect = (content_x, item_bot, row_w, h)
            delete_rect = None
            if _is_room(sc):
                # No rename button: clicking the name renames it, so a
                # separate control would be a second way to do one thing.
                by = item_bot + (h - btn) / 2.0
                dx = content_x + row_w - btn_right_pad - btn
                delete_rect = (dx, by, btn, btn)
            entries.append((
                'row', sc, parent, color,
                sc.name == current_scene_name, row_rect,
                delete_rect,
            ))

    # ---- Room actions + New Room ------------------------------------------
    cursor_y = list_bottom - new_room_gap
    if _room_actions:
        gap_x = 3 * s
        for start in range(0, len(_room_actions), 3):
            row = _room_actions[start:start + 3]
            bw = (content_w - gap_x * (len(row) - 1)) / len(row)
            for j, (_o, key, label, operator, kwargs) in enumerate(row):
                entries.append((
                    'room_action', key, label, operator, kwargs,
                    (content_x + j * (bw + gap_x), cursor_y - new_room_h,
                     bw, new_room_h)))
            cursor_y -= new_room_h + gap_x
    new_room_rect = (content_x, cursor_y - new_room_h, content_w, new_room_h)
    entries.append(('new_room', new_room_rect))

    return panel_rect, entries


def _list_clip(entries):
    for entry in entries or ():
        if entry[0] == 'list':
            return entry[1]
    return None


def scroll_by(rows):
    """Scroll the list by ``rows`` row-heights (positive = down). The next
    _build_layout clamps it."""
    _list.scroll_by(rows, ROW_HEIGHT * _s())


def is_scrollable(entries):
    for entry in entries or ():
        if entry[0] == 'list':
            return entry[2] is not None
    return False


def hit_test(mx, my, entries):
    """Resolve a point against navigator entries.

    Returns (kind, payload) or None:
        ('pin', None)          panel-header pin toggle
        ('section', label)     section header (collapse / expand)
        ('delete', scene) / ('row', scene)
        ('new_room', None)
    List entries scrolled partly out of the clip rect only hit on their
    visible part. Shared by the modal and the pinned/HUD click path so the
    two can't disagree.
    """
    clip = _list_clip(entries)
    for entry in entries or ():
        kind = entry[0]

        if kind == 'panel_header':
            if _point_in_rect(mx, my, entry[3]):
                return ('pin', None)
        elif kind == 'header':
            if clip and not _point_in_rect(mx, my, clip):
                continue
            if _point_in_rect(mx, my, entry[3]):
                return ('section', entry[1])
        elif kind == 'row':
            if clip and not _point_in_rect(mx, my, clip):
                continue
            (_, scene, _parent, _color, _is_current, rect,
             delete_rect) = entry
            if delete_rect and _point_in_rect(mx, my, delete_rect):
                return ('delete', scene)
            if _point_in_rect(mx, my, rect):
                return ('row', scene)
        elif kind == 'room_action':
            if _point_in_rect(mx, my, entry[5]):
                return ('room_action', entry)
        elif kind == 'new_room':
            if _point_in_rect(mx, my, entry[1]):
                return ('new_room', None)
    return None


def editing_scene():
    return _edit.key


def begin_rename(scene):
    _edit.begin(scene.name, scene.name)


def cancel_rename():
    _edit.cancel()


def edit_text():
    return _edit.text


def edit_key(event):
    """Feed one key event to the inline field. Returns 'COMMIT',
    'CANCEL' or None (still editing)."""
    return _edit.feed(event)


def commit_rename():
    """Apply the typed name. Returns the scene renamed, or None."""
    key, name = _edit.take()
    scene = bpy.data.scenes.get(key) if key else None
    if scene is None or not name or name == scene.name:
        return None
    try:
        bpy.ops.home_builder.rename_room(scene_name=scene.name,
                                         new_name=name)
    except Exception:
        scene.name = name
    return scene


def toggle_section(label):
    if label in _collapsed:
        _collapsed.discard(label)
    else:
        _collapsed.add(label)


# ---- Draw helpers -----------------------------------------------------------

def _draw_panel_header(shader, font_id, rect, current_name, pin_rect, mx, my):
    rx, ry, rw, rh = rect
    s = _s()
    hdr_font = HEADER_FONT_SIZE * s
    row_font = ROW_FONT_SIZE * s
    blf.size(font_id, hdr_font)
    label = "CURRENT"
    label_w = blf.dimensions(font_id, label)[0]
    baseline = _vcenter_baseline(rect, font_id, row_font)
    _draw_text(font_id, rx, baseline, hdr_font, HEADER_TEXT, label)
    name_x = rx + label_w + 8 * s
    name_w = pin_rect[0] - 8 * s - name_x
    _draw_text(font_id, name_x, baseline, row_font, TEXT_PRIMARY,
               _fit_text(font_id, row_font, current_name, name_w))
    # separator line at the bottom of the header rect
    _draw_rect(shader, rx, ry, rw, max(1.0, s), SEPARATOR_COLOR)
    # pin toggle -- when lit, the navigator stays open across scene picks
    px, py, pw, ph = pin_rect
    hovered = _point_in_rect(mx, my, pin_rect)
    if _pinned:
        bg = PIN_ACTIVE_BG
    elif hovered:
        bg = ACTION_HOVER_BG
    else:
        bg = ACTION_BG
    _draw_rect(shader, px, py, pw, ph, bg)
    # A word, not a thumbtack. At this size a drawn pin is a smudge,
    # and PIN is unambiguous where an icon has to be learned.
    _draw_centered_text(font_id, pin_rect, HEADER_FONT_SIZE * s,
                        TEXT_PRIMARY if (_pinned or hovered)
                        else TEXT_NORMAL, 'PIN')


def _draw_row(shader, font_id, entry, mx, my):
    (_, scene, parent, color, is_current, rect, delete_rect) = entry
    rx, ry, rw, rh = rect
    hovered = _point_in_rect(mx, my, rect)

    if is_current:
        _draw_rect(shader, rx, ry, rw, rh, (*color, 0.14))
    elif hovered:
        _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)

    s = _s()
    row_font = ROW_FONT_SIZE * s
    parent_font = PARENT_FONT_SIZE * s

    accent_alpha = 1.0 if is_current else (0.85 if hovered else 0.55)
    _draw_rect(shader, rx + ACCENT_LEFT_PAD * s, ry + 4 * s,
               ACCENT_WIDTH * s, rh - 8 * s, (*color, accent_alpha))

    text_x = rx + ROW_TEXT_LEFT_PAD * s
    name_color = TEXT_PRIMARY if is_current else TEXT_NORMAL
    baseline = _vcenter_baseline(rect, font_id, row_font)

    # Being renamed: the row becomes the field. A caret marks the
    # end of the text so it reads as editable rather than selected.
    if _edit.editing(scene.name):
        field_w = rx + rw - ROW_TEXT_RIGHT_PAD * s - text_x
        _draw_rect(shader, text_x - 3 * s, ry + 3 * s,
                   field_w + 6 * s, rh - 6 * s, (0.0, 0.0, 0.0, 0.55))
        _draw_rect_outline(shader, text_x - 3 * s, ry + 3 * s,
                           field_w + 6 * s, rh - 6 * s, PIN_ACTIVE_BG)
        shown = _fit_text(font_id, row_font, _edit.text, field_w - 6 * s)
        _draw_text(font_id, text_x, baseline, row_font,
                   TEXT_PRIMARY, shown)
        caret_x = text_x + _text_w(font_id, row_font, shown) + 1 * s
        _draw_rect(shader, caret_x, ry + 5 * s, 1.5 * s, rh - 10 * s,
                   TEXT_PRIMARY)
        return

    # Text must stop short of the action buttons (room rows) or the row's
    # right edge; the parent prefix is dropped first, then the name is
    # ellipsized, so long names never run under the buttons or the border.
    if delete_rect is not None:
        avail = delete_rect[0] - 6 * s - text_x
    else:
        avail = rx + rw - ROW_TEXT_RIGHT_PAD * s - text_x

    if parent:
        blf.size(font_id, parent_font)
        parent_w = blf.dimensions(font_id, parent)[0]
        sep = "  \u00b7  "
        sep_w = blf.dimensions(font_id, sep)[0]
        if parent_w + sep_w + PARENT_MIN_NAME_W * s > avail:
            parent = None
    if parent:
        _draw_text(font_id, text_x, baseline,
                   parent_font, TEXT_DIM, parent)
        _draw_text(font_id, text_x + parent_w, baseline,
                   parent_font, TEXT_DIM, sep)
        name = _fit_text(font_id, row_font, scene.name,
                         avail - parent_w - sep_w)
        _draw_text(font_id, text_x + parent_w + sep_w, baseline,
                   row_font, name_color, name)
    else:
        name = _fit_text(font_id, row_font, scene.name, avail)
        _draw_text(font_id, text_x, baseline, row_font, name_color, name)

    if delete_rect is not None:
        d_hover = _point_in_rect(mx, my, delete_rect)
        bdx, bdy, bdw, bdh = delete_rect
        _draw_rect(shader, bdx, bdy, bdw, bdh,
                   ACTION_DELETE_HOVER_BG if d_hover else ACTION_BG)
        _draw_delete_glyph(shader, delete_rect,
                           ACTION_GLYPH_HOVER if d_hover else ACTION_GLYPH)


def _draw_new_room_button(shader, font_id, rect, mx, my):
    rx, ry, rw, rh = rect
    hovered = _point_in_rect(mx, my, rect)
    _draw_rect(shader, rx, ry, rw, rh,
               NEW_ROOM_HOVER_BG if hovered else NEW_ROOM_BG)
    _draw_rect_outline(shader, rx, ry, rw, rh, PANEL_BORDER)
    label = "New Room"
    s = _s()
    row_font = ROW_FONT_SIZE * s
    blf.size(font_id, row_font)
    label_w = blf.dimensions(font_id, label)[0]
    plus_size = 10 * s
    gap = 8 * s
    group_w = plus_size + gap + label_w
    gx = rx + (rw - group_w) / 2.0
    cy = ry + rh / 2.0
    _draw_plus_glyph(shader, gx + plus_size / 2.0, cy, plus_size, TEXT_PRIMARY)
    baseline = _vcenter_baseline(rect, font_id, row_font)
    _draw_text(font_id, gx + plus_size + gap, baseline,
               row_font, TEXT_PRIMARY, label)


# ---- Draw callback ----------------------------------------------------------

def paint_navigator(panel_rect, entries, mx, my):
    """Stateless GPU paint of the navigator panel.

    Factored out of the modal draw callback so the persistent viewport HUD
    can render the SAME panel when the navigator is pinned -- the HUD owns a
    permanent draw handler that survives designing, where the modal's own
    handler does not.
    """
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    px, py, pw, ph = panel_rect
    _paint_frame(shader, panel_rect, PANEL_BG, PANEL_BORDER)

    font_id = 0
    s = _s()
    # The list is scissor-clipped so partially scrolled rows cut off cleanly
    # at the list edges.
    clip = _list_clip(entries)
    saved_scissor = _begin_clip(clip) if clip is not None else None

    # Hover inside the list only counts on the visible part of the clip.
    if clip is not None and not _point_in_rect(mx, my, clip):
        lmx = lmy = -1.0
    else:
        lmx, lmy = mx, my

    for entry in entries:
        kind = entry[0]
        if kind == 'header':
            _, label, color, rect, collapsed, count = entry
            rx, ry, rw, rh = rect
            hdr_font = HEADER_FONT_SIZE * s
            hovered = _point_in_rect(lmx, lmy, rect)
            if hovered:
                _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)
            baseline = _vcenter_baseline(rect, font_id, hdr_font)
            chev = SECTION_CHEVRON_W * s
            _draw_chevron(shader, rx + chev / 2.0 - 1 * s, ry + rh / 2.0,
                          6 * s, collapsed,
                          TEXT_NORMAL if hovered else HEADER_TEXT)
            _draw_text(font_id, rx + chev, baseline, hdr_font,
                       TEXT_NORMAL if hovered else HEADER_TEXT, label)
            if collapsed:
                lw = _text_w(font_id, hdr_font, label)
                _draw_text(font_id, rx + chev + lw, baseline, hdr_font,
                           TEXT_DIM, f"  {count}")
        elif kind == 'row':
            _draw_row(shader, font_id, entry, lmx, lmy)

    if saved_scissor is not None:
        _end_clip(saved_scissor)

    for entry in entries:
        kind = entry[0]

        if kind == 'body':
            provider = _providers.get(entry[1])
            if provider is not None:
                try:
                    provider.paint(entries, mx, my)
                except Exception as ex:
                    print('Home Builder: %s tab failed to paint: %s'
                          % (entry[1], ex))
            break            # the provider owns everything below the strip
        if kind == 'panel_header':
            _draw_panel_header(shader, font_id, entry[2], entry[1],
                               entry[3], mx, my)
        elif kind == 'list':
            _, _clip, track, thumb = entry
            if track is not None:
                _draw_rect(shader, *track, SCROLLBAR_TRACK)
                _draw_rect(shader, *thumb, SCROLLBAR_THUMB)
        elif kind == 'room_action':
            _paint_button(shader, entry[5],
                          hovered=_point_in_rect(mx, my, entry[5]))
            _draw_centered_text(font_id, entry[5], HEADER_FONT_SIZE * s,
                                TEXT_NORMAL, entry[2])
        elif kind == 'new_room':
            _draw_new_room_button(shader, font_id, entry[1], mx, my)

    gpu.state.blend_set('NONE')


def draw_scene_navigator(op):
    """GPU draw callback for the transient (unpinned) scene-navigator modal."""
    if op.region is None or op.entries is None:
        return
    # Only draw in the region this modal was bound to (skip other 3D views)
    if bpy.context.region != op.region:
        return
    paint_navigator(op.panel_rect, op.entries, op.mouse_x, op.mouse_y)


# ---- Persistent-HUD interface ----------------------------------------------
# Let the always-on viewport HUD host the navigator while it's pinned, instead
# of the transient modal below. The HUD calls build_pinned_layout() +
# paint_navigator() each redraw, and handle_navigator_click() on a press.

def is_pinned():
    return _pinned


def panel_open():
    return _open or _pinned


def open_panel(anchor_x=-1.0, anchor_top=-1.0):
    global _open
    _open = True


def close_panel():
    """Hide the panel. Leaves the pin alone -- re-opening returns to
    whatever the user had pinned before."""
    global _open
    _open = False


def dismiss_after_action():
    """Close an unpinned panel once it has done something. Pinned
    panels stay: that is what the pin is for."""
    if not _pinned:
        close_panel()


def set_pinned(value):
    global _pinned, _open
    _pinned = bool(value)
    if _pinned:
        _open = True


def build_pinned_layout(context, area, region, anchor_x=-1.0, anchor_top=-1.0):
    """Return (panel_rect, entries) for the HUD-hosted panel, else None.

    None when the panel is closed or the geometry can't be built.
    Anchored under the active tab button via anchor_x / anchor_top.
    """
    if not panel_open() or region is None or area is None:
        return None
    return _build_layout(region, area, context.scene.name, anchor_x, anchor_top)


def handle_navigator_click(context, mx, my, entries):
    """Dispatch a left-press against pinned-navigator entries.

    Stateless mirror of the modal's hit-testing. Returns True if a navigator
    element was hit (caller consumes the click), False on a miss (caller
    passes it through so the viewport stays interactive while pinned). Hits
    never close the panel -- it's pinned; only the header pin glyph un-pins.
    """
    global _pinned
    hit = hit_test(mx, my, entries)
    if hit is None:
        # Not a shell element. On a hosted tab the body owns the rest of
        # the panel, so give it the click before passing anything through.
        return _delegate_click(context, mx, my, entries)
    kind, scene = hit

    try:
        if kind == 'pin':
            # The glyph toggles the pin now; it no longer hides the
            # panel. Dismissing is the tab button's job.
            set_pinned(not _pinned)
        elif kind == 'section':
            toggle_section(scene)

        elif kind == 'delete':
            bpy.ops.home_builder.delete_room(
                'INVOKE_DEFAULT', scene_name=scene.name)
        elif kind == 'row':
            if scene.name != context.scene.name:
                bpy.ops.home_builder_layouts.go_to_layout_view(
                    scene_name=scene.name)
                dismiss_after_action()
            elif _is_room(scene):
                # Already here: clicking your own room's name
                # edits it, since switching would do nothing.
                begin_rename(scene)
                bpy.ops.home_builder.navigator_rename(
                    'INVOKE_DEFAULT')
        elif kind == 'room_action':
            _, _key, _label, operator, kwargs, _rect = scene
            mod, name = operator.split('.', 1)
            try:
                getattr(getattr(bpy.ops, mod), name)('INVOKE_DEFAULT',
                                                     **kwargs)
            except Exception as ex:
                print('Home Builder: room action %s failed: %s'
                      % (operator, ex))
            dismiss_after_action()
        elif kind == 'new_room':
            bpy.ops.home_builder.create_room('INVOKE_DEFAULT')
    except Exception:
        pass
    return True


def _body_entry(entries):
    for entry in entries or ():
        if entry[0] == 'body':
            return entry
    return None


def _delegate_click(context, mx, my, entries):
    """Offer a click to the active tab's provider. True = consumed."""
    body = _body_entry(entries)
    if body is None:
        return False
    provider = _providers.get(body[1])
    if provider is None:
        return False
    try:
        if provider.hit(context, mx, my, entries):
            return True
    except Exception as ex:
        print('Home Builder: %s tab failed on click: %s' % (body[1], ex))
    # Clicks anywhere over a hosted body are still swallowed -- letting
    # them through would select or place through the panel.
    return _point_in_rect(mx, my, body[2])


def handle_navigator_scroll(context, mx, my, entries, rows):
    """Wheel over the pinned navigator: scroll its list. Returns True when
    consumed (cursor over a scrollable list), False to pass through."""
    body = _body_entry(entries)
    if body is not None:
        provider = _providers.get(body[1])
        if provider is not None:
            try:
                return bool(provider.scroll(mx, my, entries, rows))
            except Exception:
                return False
        return False
    if not is_scrollable(entries):
        return False
    clip = _list_clip(entries)
    if clip is None or not _point_in_rect(mx, my, clip):
        return False
    scroll_by(rows)
    return True


# ---- Modal operator ---------------------------------------------------------

class home_builder_OT_scene_navigator(bpy.types.Operator):
    bl_idname = "home_builder.scene_navigator"
    bl_label = "Scene Navigator"
    bl_description = "Quick switch between rooms, layout views, and details"

    # Optional anchor (WINDOW-local px). When set, the panel is placed with
    # its top-left here instead of centered at the top -- used by the
    # viewport HUD to drop the panel directly under its trigger button.
    anchor_x: bpy.props.FloatProperty(default=-1.0)  # type: ignore
    anchor_top: bpy.props.FloatProperty(default=-1.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        # The click may have come from a sidebar button (UI region) rather
        # than the viewport itself, so explicitly resolve the 3D viewport's
        # WINDOW region. All coords below are kept WINDOW-local.
        if context.area is None or context.area.type != 'VIEW_3D':
            return {'CANCELLED'}

        window_region = None
        for r in context.area.regions:
            if r.type == 'WINDOW':
                window_region = r
                break
        if window_region is None:
            return {'CANCELLED'}

        self.region = window_region
        self.area = context.area
        self.mouse_x = event.mouse_x - window_region.x
        self.mouse_y = event.mouse_y - window_region.y
        self.entries = None
        self.panel_rect = (0, 0, 0, 0)
        self._draw_handle = None

        self._rebuild_layout(context)

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_scene_navigator, (self,), 'WINDOW', 'POST_PIXEL'
        )
        context.window_manager.modal_handler_add(self)
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _rebuild_layout(self, context):
        current = context.scene.name
        self.panel_rect, self.entries = _build_layout(
            self.region, self.area, current, self.anchor_x, self.anchor_top
        )

    def _cleanup(self, context):
        if self._draw_handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(
                    self._draw_handle, 'WINDOW'
                )
            except Exception:
                pass
            self._draw_handle = None
        if context.area:
            context.area.tag_redraw()

    def _switch_to(self, context, scene_name):
        try:
            bpy.ops.home_builder_layouts.go_to_layout_view(scene_name=scene_name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not switch to {scene_name}: {e}")

    def _create_room(self, context):
        try:
            bpy.ops.home_builder.create_room('INVOKE_DEFAULT')
        except Exception as e:
            self.report({'WARNING'}, f"Could not create room: {e}")

    def _rename_room(self, context, scene):
        # temp_override(scene=...) so rename_room's poll and invoke see the
        # target room; execute targets it explicitly via scene_name.
        try:
            with context.temp_override(scene=scene):
                bpy.ops.home_builder.rename_room(
                    'INVOKE_DEFAULT', scene_name=scene.name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not rename {scene.name}: {e}")

    def _delete_room(self, context, scene):
        try:
            bpy.ops.home_builder.delete_room(
                'INVOKE_DEFAULT', scene_name=scene.name)
        except Exception as e:
            self.report({'WARNING'}, f"Could not delete {scene.name}: {e}")

    def modal(self, context, event):
        global _pinned
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_x - self.region.x
            self.mouse_y = event.mouse_y - self.region.y
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} \
                and event.value == 'PRESS':
            if is_scrollable(self.entries):
                scroll_by(-SCROLL_STEP_ROWS if event.type == 'WHEELUPMOUSE'
                          else SCROLL_STEP_ROWS)
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx = event.mouse_x - self.region.x
            my = event.mouse_y - self.region.y
            hit = hit_test(mx, my, self.entries)
            if hit is None:
                # nothing hit -- dismiss
                self._cleanup(context)
                return {'CANCELLED'}
            kind, scene = hit
            if kind == 'pin':
                _pinned = not _pinned
                if _pinned:
                    # Hand the navigator to the persistent viewport HUD,
                    # which draws + routes it while you design. Close this
                    # transient modal so it isn't drawn twice. If the HUD is
                    # disabled there's nothing to hand off to -- fall back
                    # to the old in-modal pinned behavior (stay open across
                    # picks).
                    from . import viewport_hud
                    if viewport_hud._hud_enabled():
                        self._cleanup(context)
                        return {'FINISHED'}
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}
            if kind == 'section':
                toggle_section(scene)
                self._rebuild_layout(context)
                if context.area:
                    context.area.tag_redraw()
                return {'RUNNING_MODAL'}

            if kind == 'delete':
                self._cleanup(context)
                self._delete_room(context, scene)
                return {'FINISHED'}
            if kind == 'row':
                # Pinned: switch but keep the navigator open so the user
                # can pick another scene. Unpinned: switch and close --
                # the original behavior.
                if _pinned:
                    if scene.name != context.scene.name:
                        self._switch_to(context, scene.name)
                        self._rebuild_layout(context)
                        if context.area:
                            context.area.tag_redraw()
                    return {'RUNNING_MODAL'}
                self._cleanup(context)
                if scene.name != context.scene.name:
                    self._switch_to(context, scene.name)
                return {'FINISHED'}
            if kind == 'new_room':
                self._cleanup(context)
                self._create_room(context)
                return {'FINISHED'}
            return {'RUNNING_MODAL'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._cleanup(context)
            return {'CANCELLED'}

        # Swallow everything else so it doesn't leak to the viewport
        return {'RUNNING_MODAL'}


class home_builder_OT_navigator_rename(bpy.types.Operator):
    """Rename the room in place in the navigator list.

    A modal only for as long as the user is typing -- it ends on Enter
    or Esc. That is the transient shape the panel itself used to have;
    what must never happen is a modal that outlives the interaction,
    because Blender skips autosave while one is live.
    """
    bl_idname = "home_builder.navigator_rename"
    bl_label = "Rename Room"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return editing_scene() is not None

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        _tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        result = edit_key(event)
        if result == 'COMMIT':
            commit_rename()
            _tag_redraw()
            return {'FINISHED'}
        if result == 'CANCEL':
            cancel_rename()
            _tag_redraw()
            return {'CANCELLED'}
        # A click anywhere ends the edit, committing what was typed --
        # the same thing a field in a form does when it loses focus.
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS':
            commit_rename()
            _tag_redraw()
            return {'FINISHED'}
        _tag_redraw()
        return {'RUNNING_MODAL'}


def _tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---- Registration -----------------------------------------------------------

classes = (
    home_builder_OT_scene_navigator,
    home_builder_OT_navigator_rename,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Linking another room's geometry into this one, and the options for
    # how: which of its walls / lights / products come across, what
    # colour it draws in, whether it shows at all. A form -- there is a
    # colour picker in it -- so it opens as a native dialog showing the
    # sidebar's own block rather than being drawn again in GPU.
    register_room_action('linked_rooms', "Linked Rooms",
                         'home_builder.tool_options',
                         {'section': 'draw_linked_rooms',
                          'title': "Linked Rooms"},
                         order=10)


def unregister():
    unregister_room_action('linked_rooms')
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
