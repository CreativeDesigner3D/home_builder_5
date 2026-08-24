"""Persistent GPU-drawn control HUD for the 3D viewport.

When the `use_viewport_hud` addon preference is enabled, draws controls
along the top of every 3D viewport: a left-anchored scene-navigator
trigger (just past the toolbar; it moves into the centered row when the
viewport's overlay text occupies that corner) and a centered
selection-mode picker for the active product library.
A permanent draw handler renders the strip; addon keymap entries route
clicks and hover moves on widget rects to their actions while passing
every other event through. No persistent modal operator is used --
Blender skips autosave while ANY modal operator is running, so the old
always-on listener silently disabled autosave for the whole session.

Widgets are intentionally thin -- they read and write the per-product
selection-mode properties, which already own their update callbacks, so
the HUD contributes presentation and hit-testing only, never selection
logic.
"""

import bpy
import gpu
import blf
from collections import namedtuple

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    draw_rect,
    draw_rect_outline,
    draw_lines,
    draw_text,
    point_in_rect,
)
# Shared widget layer -- the same UI scale and palette the scene
# navigator draws with, so the two surfaces cannot drift apart.
from ..hb_gpu_ui import Theme, scale as _s, draw_arrow_head
# Sibling module -- safe to import at load (scene_navigator imports viewport_hud
# only lazily, inside its pin-toggle handler, so there's no import cycle).
from . import scene_navigator
from . import layout_lock

# operators/ sits one level below the addon root; the AddonPreferences
# bl_idname is the root package name.
_ADDON_PKG = __package__.rsplit(".", 1)[0]


# ---- Module state -----------------------------------------------------------

_draw_handle = None        # permanent SpaceView3D draw handler
_hud_shutdown = False      # set by unregister(); gates the draw + keymap ops
_mouse = (-1, -1)          # last cursor pos, region-local
_mouse_region = None       # region _mouse was measured in (hover is per-region)
_last_hover_key = None     # layout index of the widget under the cursor
_addon_keymaps = []        # [(keymap, keymap_item), ...] for cleanup


# ---- Layout + style ---------------------------------------------------------

HUD_MARGIN_Y    = 12
HUD_MARGIN_X    = 8      # nav button inset from the left (toolbar) edge
BTN_HEIGHT      = 24
BTN_GAP         = 4
ROW_GAP         = 6
NAV_TEXT_LEFT   = 29     # glyph + gap; where the nav-button label begins
NAV_PAD_RIGHT   = 10
MODE_BTN_WIDTH  = 78
GROUP_GAP       = 24
FONT_SIZE       = 11

BTN_BG          = Theme.BTN_BG
BTN_HOVER_BG    = Theme.BTN_HOVER_BG
BTN_ACTIVE_BG   = Theme.BTN_ACTIVE_BG
BTN_BORDER      = Theme.BTN_BORDER
GLYPH_COLOR     = Theme.GLYPH_STRONG
TEXT_NORMAL     = (0.90, 0.90, 0.90, 1.0)
TEXT_ACTIVE     = (1.0, 1.0, 1.0, 1.0)


# ---- Context helpers --------------------------------------------------------

def _get_prefs():
    try:
        return bpy.context.preferences.addons[_ADDON_PKG].preferences
    except (KeyError, AttributeError):
        return None


def _hud_enabled():
    p = _get_prefs()
    return bool(p and getattr(p, "use_viewport_hud", False))


def _product_ui_visible(context, product_tab):
    """Selection-mode widgets show only on the matching product tab and
    only in a real room scene -- mirrors the sidebar panels' gating."""
    scene = context.scene
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    hb = getattr(scene, 'home_builder', None)
    return getattr(hb, 'product_tab', 'FRAMELESS') == product_tab


def _face_frame_ui_visible(context):
    return _product_ui_visible(context, 'FACE FRAME')


def _frameless_ui_visible(context):
    return _product_ui_visible(context, 'FRAMELESS')


def _closet_ui_visible(context):
    return _product_ui_visible(context, 'CLOSET')


# Per-product wiring for the selection-mode picker. enabled_attr is the
# product's master enable bool, or None when it has none -- frameless has
# no such bool and treats the 'Parts' pick as the neutral state instead.
_SelectionWiring = namedtuple(
    '_SelectionWiring',
    ['scene_attr', 'enum_attr', 'enabled_attr', 'ui_visible'])

_FF_SELECTION = _SelectionWiring(
    'hb_face_frame', 'face_frame_selection_mode',
    'face_frame_selection_mode_enabled', _face_frame_ui_visible)
_FL_SELECTION = _SelectionWiring(
    'hb_frameless', 'frameless_selection_mode',
    None, _frameless_ui_visible)
_CL_SELECTION = _SelectionWiring(
    'hb_closets', 'closet_selection_mode',
    'closet_selection_mode_enabled', _closet_ui_visible)


# ---- Widgets ----------------------------------------------------------------

def _draw_centered_text(font_id, rect, size, color, text):
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    tw, th = blf.dimensions(font_id, text)
    draw_text(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0,
              size, color, text)


class _PanelTabButton:
    """One of the ROOMS / LIBRARY / STYLES tabs at the top-left.

    These replace the old single button that showed the scene name. That
    button told you where you were but hid where you could go: the
    library and the styles were a click and a tab away, behind a label
    that looked like a status readout. Three tabs say what is there.

    Clicking a tab opens the panel on it. Clicking the tab that is
    already showing closes the panel again, so the same button both
    opens and dismisses -- and the panel can still be pinned from its
    own header once open.
    """

    def __init__(self, tab):
        self.tab = tab

    @property
    def width(self):
        s = _s()
        blf.size(0, FONT_SIZE * s)
        return int(blf.dimensions(0, self.tab)[0] + 22 * s)

    def visible(self, context):
        # A tab that means nothing here is not shown at all -- better
        # than a tab that opens to a panel with nothing to do.
        return scene_navigator.tab_available(self.tab, context.scene)

    def _showing(self):
        """True when the panel is open on this tab."""
        return (scene_navigator.panel_open()
                and scene_navigator.active_tab() == self.tab)

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        s = _s()
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        active = self._showing()
        bg = (BTN_ACTIVE_BG if active
              else (BTN_HOVER_BG if hovered else BTN_BG))
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        font_sz = FONT_SIZE * s
        blf.size(font_id, font_sz)
        tw, th = blf.dimensions(font_id, self.tab)
        draw_text(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0,
                  font_sz, TEXT_ACTIVE if active else TEXT_NORMAL, self.tab)

    def on_click(self, context, area, region):
        if self._showing():
            # Clicking the showing tab dismisses the panel, pinned or not.
            scene_navigator.set_pinned(False)
            scene_navigator.close_panel()
            return
        scene_navigator.set_active_tab(self.tab)
        if scene_navigator.panel_open():
            return                      # already up; just switched tabs
        anchor_x, anchor_top = _nav_anchor(context, area)
        scene_navigator.open_panel(anchor_x, anchor_top)

class _ModeButton:
    """One selection-mode pick. Sets the scene enum on click; the enum's
    own update callback drives the highlight toggle. A _SelectionWiring
    supplies the per-product props (scene group, enum, optional master
    enable bool), so one class serves both the face frame and frameless
    pickers."""

    @property
    def width(self):
        return int(MODE_BTN_WIDTH * _s())

    def __init__(self, wiring, mode_value, label):
        self.wiring = wiring
        self.mode_value = mode_value
        self.label = label

    def _props(self, context):
        return getattr(context.scene, self.wiring.scene_attr)

    def _is_active(self, props):
        # Products without an enable bool (frameless) are always "on";
        # active state is then purely whether this mode is selected.
        enabled_attr = self.wiring.enabled_attr
        if enabled_attr and not getattr(props, enabled_attr):
            return False
        return getattr(props, self.wiring.enum_attr) == self.mode_value

    def visible(self, context):
        return self.wiring.ui_visible(context)

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        is_active = self._is_active(self._props(context))
        hovered = point_in_rect(mouse[0], mouse[1], rect)

        if is_active:
            bg = BTN_ACTIVE_BG
        elif hovered:
            bg = BTN_HOVER_BG
        else:
            bg = BTN_BG
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)

        color = TEXT_ACTIVE if is_active else TEXT_NORMAL
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(), color, self.label)

    def on_click(self, context, area, region):
        props = self._props(context)
        # Face frame keeps a master enable bool -- picking a mode in the
        # HUD also flips it on. Frameless has none (enabled_attr is None);
        # picking a mode is the only state, with 'Parts' as the neutral
        # pick that clears highlighting.
        enabled_attr = self.wiring.enabled_attr
        if enabled_attr and not getattr(props, enabled_attr):
            setattr(props, enabled_attr, True)
        setattr(props, self.wiring.enum_attr, self.mode_value)


class _ModalToggleButton:
    """HUD button that starts or stops a HUD-controllable modal operator.

    Visibility is mode-driven: the cabinet grab pairs with the 'Cabinets'
    selection mode, the face-frame grab with 'Face Frame', the open-door
    mode with 'Parts'. A running modal also forces visibility regardless
    of the current mode, so the user can always reach the Disable button
    even after nudging the selection mode mid-session.

    Label flips Enable -> Disable while the matching modal runs; on_click
    either invokes the operator (Enable path) or asks the running modal
    to commit and exit via request_exit_active_modal (Disable path).
    Width is sized to the longer of the two labels so the button
    geometry doesn't jitter when state changes.
    """

    def __init__(self, op_idname, mode_value, enable_label, disable_label):
        self.op_idname = op_idname  # e.g. "hb_face_frame.grab_cabinet"
        self.mode_value = mode_value
        self.enable_label = enable_label
        self.disable_label = disable_label

    # ---- internal helpers ----

    def _is_my_modal_active(self):
        return active_modal_idname() == self.op_idname

    def _label(self):
        return (self.disable_label if self._is_my_modal_active()
                else self.enable_label)

    # ---- widget protocol ----

    @property
    def width(self):
        # Size to the longer of the two possible labels so the rect
        # doesn't shift width when state flips.
        s = _s()
        blf.size(0, FONT_SIZE * s)
        w_enable = blf.dimensions(0, self.enable_label)[0]
        w_disable = blf.dimensions(0, self.disable_label)[0]
        return int(max(w_enable, w_disable) + 24 * s)  # text + horizontal pad

    def visible(self, context):
        if not _face_frame_ui_visible(context):
            return False
        ff = context.scene.hb_face_frame
        in_my_mode = (ff.face_frame_selection_mode_enabled
                      and ff.face_frame_selection_mode == self.mode_value)
        # Stay visible while our modal runs even if the user has nudged
        # the selection mode; otherwise the exit button would vanish
        # and the user would be forced to Esc out.
        return in_my_mode or self._is_my_modal_active()

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        active = self._is_my_modal_active()
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        if active:
            bg = BTN_ACTIVE_BG
        elif hovered:
            bg = BTN_HOVER_BG
        else:
            bg = BTN_BG
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        color = TEXT_ACTIVE if active else TEXT_NORMAL
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(), color, self._label())

    def on_click(self, context, area, region):
        if active_modal_idname() == self.op_idname:
            request_exit_active_modal(context)
            return
        # Enable path: invoke the modal under a viewport override.
        ns, name = self.op_idname.split('.')
        try:
            with context.temp_override(area=area, region=region):
                getattr(getattr(bpy.ops, ns), name)('INVOKE_DEFAULT')
        except Exception:
            pass


# Widget instances. Mode values must match the EnumProperty items on
# Face_Frame_Scene_Props.face_frame_selection_mode.
_TAB_BUTTONS = tuple(_PanelTabButton(t) for t in scene_navigator.TABS)
# Face frame (6 modes), frameless (5 -- no Face Frame), and closets (4)
# buttons share one group. Each self-gates on its product tab via visible(), so compute_layout
# renders only the active product's set; the tabs are mutually exclusive so
# the two never appear together.
_MODE_BUTTONS = [
    _ModeButton(_FF_SELECTION, 'Cabinets', "Cabinets"),
    _ModeButton(_FF_SELECTION, 'Bays', "Bays"),
    _ModeButton(_FF_SELECTION, 'Openings', "Openings"),
    _ModeButton(_FF_SELECTION, 'Face Frame', "Face Frame"),
    _ModeButton(_FF_SELECTION, 'Interiors', "Interiors"),
    _ModeButton(_FF_SELECTION, 'Parts', "Parts"),
    _ModeButton(_FL_SELECTION, 'Cabinets', "Cabinets"),
    _ModeButton(_FL_SELECTION, 'Bays', "Bays"),
    _ModeButton(_FL_SELECTION, 'Openings', "Openings"),
    _ModeButton(_FL_SELECTION, 'Interiors', "Interiors"),
    _ModeButton(_FL_SELECTION, 'Parts', "Parts"),
    _ModeButton(_CL_SELECTION, 'Starters', "Starters"),
    _ModeButton(_CL_SELECTION, 'Bays', "Bays"),
    _ModeButton(_CL_SELECTION, 'Openings', "Openings"),
    _ModeButton(_CL_SELECTION, 'Parts', "Parts"),
]

class _GrabPill:
    """One Grab toggle for every face-frame selection mode.

    There were four of these, one per mode, and the user had to keep
    the grab they started matched to the mode they were in. The mode
    already says what you are working on, so it can say what is
    draggable: this starts a single grab whose boundaries follow the
    mode, and it sits at the end of the mode row because that is what
    it modifies.

    Drawn as a square icon rather than a word: it is a state you
    leave on, not a command you fire, and a four-way arrow says
    "drag things" without spending the width of a label.
    """

    OP = 'hb_face_frame.grab'

    @property
    def width(self):
        return int(BTN_HEIGHT * _s())        # square

    def visible(self, context):
        if not _face_frame_ui_visible(context):
            return False
        if active_modal_idname() == self.OP:
            return True          # always offer the way out
        try:
            from ..product_libraries.face_frame.operators import (
                op_modify_cabinet)
            return op_modify_cabinet.mode_is_grabbable(context.scene)
        except Exception:
            return False

    def _active(self):
        return active_modal_idname() == self.OP

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        s = _s()
        active = self._active()
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        bg = (BTN_ACTIVE_BG if active
              else (BTN_HOVER_BG if hovered else BTN_BG))
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        # Four-way arrow: the mark for 'this drags things'.
        col = TEXT_ACTIVE if active else TEXT_NORMAL
        cx, cy = rx + rw / 2.0, ry + rh / 2.0
        arm = min(rw, rh) * 0.30
        head = arm * 0.55
        draw_lines(shader, [(cx - arm, cy), (cx + arm, cy),
                            (cx, cy - arm), (cx, cy + arm)], col)
        for tip, direction in (((cx + arm, cy), (1.0, 0.0)),
                               ((cx - arm, cy), (-1.0, 0.0)),
                               ((cx, cy + arm), (0.0, 1.0)),
                               ((cx, cy - arm), (0.0, -1.0))):
            draw_arrow_head(shader, tip, direction, head, col)

    def on_click(self, context, area, region):
        if self._active():
            request_exit_active_modal(context)
            return
        try:
            with context.temp_override(area=area, region=region):
                bpy.ops.hb_face_frame.grab('INVOKE_DEFAULT')
        except Exception:
            pass


class _SizesButton:
    """Cycles the dimension-label scope: All -> Selected -> Off.

    It used to draw itself, in the overlay module, from a private copy
    of this file's layout constants and a guess at which HUD row was
    free. That guess went stale the moment the grab buttons left row
    two. It is a HUD widget now, sitting beside Grab because both
    modify what the selection mode shows you.
    """

    SCOPES = ('ALL', 'SELECTED', 'OFF')

    def _scope(self, context):
        props = getattr(context.scene, 'hb_face_frame', None)
        return getattr(props, 'selection_mode_sizes_scope', 'OFF') if props else 'OFF'

    def _label(self, context):
        scope = self._scope(context)
        if scope == 'ALL':
            return 'Sizes: All'
        if scope == 'SELECTED':
            return 'Sizes: Sel'
        return 'Sizes'

    @property
    def width(self):
        s = _s()
        blf.size(0, FONT_SIZE * s)
        # Sized to the longest label so the row does not jitter as the
        # scope cycles.
        return int(blf.dimensions(0, 'Sizes: Sel')[0] + 24 * s)

    def visible(self, context):
        return _face_frame_ui_visible(context)

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        on = self._scope(context) != 'OFF'
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        bg = (BTN_ACTIVE_BG if on else (BTN_HOVER_BG if hovered else BTN_BG))
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(),
                            TEXT_ACTIVE if on else TEXT_NORMAL,
                            self._label(context))

    def on_click(self, context, area, region):
        props = getattr(context.scene, 'hb_face_frame', None)
        if props is None:
            return
        nxt = {'ALL': 'SELECTED', 'SELECTED': 'OFF'}.get(
            self._scope(context), 'ALL')
        props.selection_mode_sizes_scope = nxt


_SIZES_BUTTON = _SizesButton()
_GRAB_PILL = _GrabPill()
_OPEN_DOOR_BUTTON = _ModalToggleButton(
    'hb_face_frame.open_mode', 'Parts',
    enable_label="Enable Open Door Mode",
    disable_label="Disable Open Door Mode",
)
_MODAL_TOGGLE_BUTTONS = [
    _OPEN_DOOR_BUTTON,
]


class _SceneToggleButton:
    """HUD button bound to a boolean property.

    Reads and writes the property directly, so its update callback owns
    the real work and the HUD stays presentation-only -- the same split
    the selection-mode picker uses. ``ui_visible`` gates which scenes show
    it; ``width_px`` sizes the button so a row of these does not jitter
    as state changes.

    ``owner`` picks what the property hangs off. Scene is the default,
    but a toggle that is a way of LOOKING rather than part of the job
    generally lives on the WindowManager, and the HUD should be able to
    show either without caring which.
    """

    def __init__(self, prop_name, label, ui_visible, width_px=112,
                 owner='SCENE'):
        self.prop_name = prop_name
        self.label = label
        self.ui_visible = ui_visible
        self.width_px = width_px
        self.owner = owner

    def _host(self, context):
        if self.owner == 'WINDOW_MANAGER':
            return context.window_manager
        return context.scene

    @property
    def width(self):
        return int(self.width_px * _s())

    def _is_active(self, context):
        return bool(getattr(self._host(context), self.prop_name, False))

    def visible(self, context):
        return self.ui_visible(context)

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        is_active = self._is_active(context)
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        if is_active:
            bg = BTN_ACTIVE_BG
        elif hovered:
            bg = BTN_HOVER_BG
        else:
            bg = BTN_BG
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        color = TEXT_ACTIVE if is_active else TEXT_NORMAL
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(), color,
                            self.label)

    def on_click(self, context, area, region):
        host = self._host(context)
        setattr(host, self.prop_name,
                not getattr(host, self.prop_name, False))


def _layout_view_visible(context):
    """Sheet-only widgets: the mirror image of _product_ui_visible."""
    return bool(context.scene and context.scene.get('IS_LAYOUT_VIEW'))


# Sheet controls, shown only on a layout view.
_LOCK_MODEL_BUTTON = _SceneToggleButton(
    layout_lock.LOCK_PROP, "Lock 3D Model", _layout_view_visible)
_BUILTIN_SHEET_BUTTONS = [(0, "lock_model", _LOCK_MODEL_BUTTON)]

# Contributed sheet toggles. Whoever owns a sheet-level option can add
# it beside the built-in ones without this module depending on them;
# with nothing registered the row is exactly as it was.
_extra_sheet_buttons = []      # (order, key, widget)


def register_sheet_toggle(key, prop_name, label, owner="SCENE",
                          width_px=112, order=100):
    """Add a boolean toggle to the layout-view HUD row.

    `owner` is SCENE or WINDOW_MANAGER -- whichever the property
    actually hangs off. Re-registering a key replaces it, so a
    reloaded add-on cannot stack duplicates.
    """
    unregister_sheet_toggle(key)
    widget = _SceneToggleButton(prop_name, label, _layout_view_visible,
                                width_px=width_px, owner=owner)
    _extra_sheet_buttons.append((order, key, widget))
    _extra_sheet_buttons.sort(key=lambda b: (b[0], b[1]))


def unregister_sheet_toggle(key):
    for i, entry in enumerate(list(_extra_sheet_buttons)):
        if entry[1] == key:
            del _extra_sheet_buttons[i]
            return


def _layout_view_buttons():
    rows = _BUILTIN_SHEET_BUTTONS + _extra_sheet_buttons
    return [b[2] for b in sorted(rows, key=lambda b: (b[0], b[1]))]


def _rows():
    """Centered HUD rows, top to bottom. Each row is a list of widget groups;
    groups are separated by GROUP_GAP, widgets within a group by BTN_GAP, and
    the whole row is centered along the top of the viewport.

    The scene-navigator button is NOT in these rows -- compute_layout places
    it separately, left-anchored just past the toolbar.

    The first row holds the selection-mode picker; the second holds the grab
    toggles; the third holds the sheet controls, which show only on a
    layout view (where the first two rows are empty, so it draws at the
    top). The toggles' visible() checks gate on selection mode and
    modal-active state, so that row contains at most one rendered button at a
    time (or zero, in which case compute_layout skips the row entirely)."""
    return [
        [_MODE_BUTTONS, [_GRAB_PILL, _SIZES_BUTTON]],
        [_MODAL_TOGGLE_BUTTONS],
        [_layout_view_buttons()],
    ]


def _corner_has_overlay_text(area):
    """True when Blender draws its own text block (General Info,
    Statistics, Performance) in this viewport's top-left corner -- the spot
    the nav button normally occupies."""
    space = area.spaces.active if area is not None else None
    overlay = getattr(space, "overlay", None)
    if overlay is None or not overlay.show_overlays:
        return False
    return bool(overlay.show_text or overlay.show_stats
                or getattr(overlay, "show_performance", False))


def compute_layout(context, area):
    """Return [(widget, rect), ...] for every currently-visible widget, in
    WINDOW-local pixel coords. Shared by the draw handler and the click
    listener so their rects cannot drift apart."""
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    visible_w = x_max - x_min
    s = _s()
    margin_y = HUD_MARGIN_Y * s
    margin_x = HUD_MARGIN_X * s
    btn_h = BTN_HEIGHT * s
    group_gap = GROUP_GAP * s
    btn_gap = BTN_GAP * s
    row_gap = ROW_GAP * s
    placed = []
    top_y = y_max - margin_y - btn_h

    # The panel tabs are left-anchored just past the toolbar, not part of
    # the centered rows -- a fixed spot makes them easy to find and the
    # panel opens directly below them. When the viewport's overlay text is
    # on, that corner belongs to Blender, so they yield and join the first
    # centered row as its leftmost group instead.
    rows = _rows()
    # The centered rows filter on visible(); this left-anchored strip
    # has to do it too, or a tab that does not apply here still gets a
    # button.
    tab_buttons = [b for b in _TAB_BUTTONS if b.visible(context)]
    if _corner_has_overlay_text(area):
        rows = [[tab_buttons] + rows[0]] + rows[1:]
    else:
        tab_x = x_min + margin_x
        for tab_btn in tab_buttons:
            placed.append((tab_btn, (tab_x, top_y, tab_btn.width, btn_h)))
            tab_x += tab_btn.width + btn_gap

    cursor_y = top_y
    for row in rows:
        groups = [[w for w in g if w.visible(context)] for g in row]
        groups = [g for g in groups if g]
        if not groups:
            continue
        row_w = group_gap * (len(groups) - 1)
        for g in groups:
            row_w += sum(w.width for w in g) + btn_gap * (len(g) - 1)
        cursor_x = x_min + (visible_w - row_w) / 2.0
        for gi, group in enumerate(groups):
            if gi > 0:
                cursor_x += group_gap
            for wi, w in enumerate(group):
                if wi > 0:
                    cursor_x += btn_gap
                placed.append((w, (cursor_x, cursor_y, w.width, btn_h)))
                cursor_x += w.width
        cursor_y -= btn_h + row_gap
    return placed


# ---- Active modal registry --------------------------------------------------
# Modal operators opt in by calling register_active_modal(self) in their
# invoke and unregister_active_modal(self) in their teardown. The HUD's
# toggle buttons read this to decide whether to show Enable or Disable,
# and request_exit_active_modal pokes the running instance via an
# _exit_requested flag plus a wake-up timer so the modal sees it on the
# next event tick rather than waiting for user input.

_active_modal = None


def register_active_modal(modal_inst):
    """Register a modal operator instance as the current HUD-controllable
    modal. Single-modal-at-a-time assumption - the previous registration
    is replaced silently."""
    global _active_modal
    _active_modal = modal_inst


def unregister_active_modal(modal_inst):
    """Clear the registry if it's still pointing at modal_inst. No-op if
    another modal has since claimed the slot, so late teardowns can't
    stomp on a successor."""
    global _active_modal
    if _active_modal is modal_inst:
        _active_modal = None


def active_modal_idname():
    """bl_idname of the registered modal, or None.

    Read it off the class, not the instance. Blender's RNA layer on an
    Operator instance returns bl_idname as the UPPERCASE_OT form, while
    the class attribute holds the dotted Python-callable form which is
    what callers compare against."""
    return type(_active_modal).bl_idname if _active_modal else None


def request_exit_active_modal(context):
    """Signal the registered modal to commit/finish and tear down. Sets
    an _exit_requested flag the modal checks at the top of modal(), and
    adds a 1ms event_timer so the next iteration runs immediately rather
    than waiting for the user to nudge the mouse. Returns True if a
    modal was registered."""
    global _active_modal
    if _active_modal is None:
        return False
    _active_modal._exit_requested = True
    try:
        _active_modal._exit_timer = (
            context.window_manager.event_timer_add(
                0.001, window=context.window)
        )
    except Exception:
        _active_modal._exit_timer = None
    return True


def click_hits_widget(context, area, region_x, region_y):
    """True if (region_x, region_y) sits inside any currently-visible HUD
    widget hit-rect. Lets external modal operators (like the grab modals)
    pass clicks through instead of consuming them, so HUD buttons remain
    clickable while a modal is running."""
    if not _hud_enabled() or area is None:
        return False
    for _widget, rect in compute_layout(context, area):
        if point_in_rect(region_x, region_y, rect):
            return True
    # The pinned navigator panel is HUD surface too, so external modals
    # (grab / placement) pass its clicks through rather than consuming them.
    if scene_navigator.panel_open():
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region is not None:
            ax, atop = _nav_anchor(context, area)
            layout = scene_navigator.build_pinned_layout(
                context, area, region, ax, atop)
            if layout and point_in_rect(region_x, region_y, layout[0]):
                return True
    return False


def pinned_panel_rect(context, area):
    """The pinned scene navigator's panel rect, or None when nothing is
    pinned there.

    The navigator is HUD surface: it hangs off the nav button at the
    top-left and stays put while the user works. Anything else that
    anchors to that corner -- the room and draft tool palettes -- has to
    ask where it is and step aside, because a GPU overlay has no layout
    engine to do it for them.
    """
    if area is None or _hud_shutdown or not _hud_enabled():
        return None
    if not scene_navigator.panel_open():
        return None
    region = next((r for r in area.regions if r.type == 'WINDOW'), None)
    if region is None:
        return None
    ax, atop = _nav_anchor(context, area)
    layout = scene_navigator.build_pinned_layout(context, area, region,
                                                 ax, atop)
    return layout[0] if layout else None


# ---- Draw handler -----------------------------------------------------------

def _nav_anchor(context, area):
    """(x, top) just under the tab strip, for placing the panel.

    Anchored to the FIRST tab, not the active one. Hanging it under
    whichever tab was selected slid the whole panel sideways as you
    switched, and dragged the tool palette along with it. The strip is
    one control; the panel belongs under its left edge.

    (-1, -1) when the tabs are not currently laid out.
    """
    for widget, rect in compute_layout(context, area):
        if isinstance(widget, _PanelTabButton):
            return rect[0], rect[1] - 6
    return -1.0, -1.0


def _draw_hud():
    """Permanent POST_PIXEL callback -- runs once per 3D viewport WINDOW
    region. Cheap no-op when the HUD preference is off."""
    if _hud_shutdown or not _hud_enabled():
        return
    context = bpy.context
    area = context.area
    region = context.region
    if area is None or area.type != 'VIEW_3D':
        return
    if region is None or region.type != 'WINDOW':
        return

    placed = compute_layout(context, area)
    if not placed:
        return

    # Hover state is only meaningful for the region the cursor is in.
    mouse = _mouse if _mouse_region == region else (-1, -1)

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    font_id = 0
    for widget, rect in placed:
        widget.draw(shader, font_id, rect, context, mouse)
    gpu.state.blend_set('NONE')

    # Pinned scene navigator: drawn by THIS permanent handler (not the
    # transient modal) so it persists while the user designs. Anchored under
    # the nav button using the layout we just computed.
    if scene_navigator.panel_open():
        ax = atop = -1.0
        for widget, rect in placed:
            if isinstance(widget, _PanelTabButton):
                ax, atop = rect[0], rect[1] - 6
                break
        layout = scene_navigator.build_pinned_layout(
            context, area, region, ax, atop)
        if layout:
            scene_navigator.paint_navigator(
                layout[0], layout[1], mouse[0], mouse[1])


# ---- Click + hover routing (addon keymap) -----------------------------------
# Replaces the old persistent modal listener. Blender's autosave timer skips
# the save and merely reschedules whenever ANY modal operator handler is
# live (wm_files.cc), so an always-running listener disabled autosave for
# the entire session. The HUD now hooks LEFTMOUSE / MOUSEMOVE through addon
# keymap entries instead: each event invokes a short-lived operator that
# either handles the hit and finishes or returns PASS_THROUGH immediately.
# Nothing persists in the modal handler list, so autosave runs normally.


def _hud_event_poll(context):
    """Shared poll for the keymap operators: HUD on, real viewport region.
    A failed poll lets the event continue down the keymap untouched."""
    return (not _hud_shutdown
            and _hud_enabled()
            and context.area is not None
            and context.area.type == 'VIEW_3D'
            and context.region is not None
            and context.region.type == 'WINDOW')


class home_builder_OT_hud_click(bpy.types.Operator):
    """Routes a viewport left-press to HUD widgets. A press landing on the
    pinned navigator panel or a widget rect is handled and consumed; any
    other press passes through, so selection, gizmos, tools and other
    modals behave exactly as before."""
    bl_idname = "home_builder.hud_click"
    bl_label = "Home Builder HUD Click"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _hud_event_poll(context)

    def invoke(self, context, event):
        area = context.area
        region = context.region
        mx, my = event.mouse_region_x, event.mouse_region_y

        # The panel gets first crack at the press; a hit inside its rect
        # is consumed, a miss falls through to the widgets below.
        if scene_navigator.panel_open():
            ax, atop = _nav_anchor(context, area)
            layout = scene_navigator.build_pinned_layout(
                context, area, region, ax, atop)
            if layout and point_in_rect(mx, my, layout[0]):
                scene_navigator.handle_navigator_click(
                    context, mx, my, layout[1])
                area.tag_redraw()
                return {'FINISHED'}
            # Clicked away. An unpinned panel behaves like a menu and
            # closes, but the click still reaches the viewport -- so the
            # same press that dismisses it can also select something.
            if layout and not scene_navigator.is_pinned():
                on_tab = any(
                    point_in_rect(mx, my, rect)
                    for widget, rect in compute_layout(context, area)
                    if isinstance(widget, _PanelTabButton))
                if not on_tab:
                    scene_navigator.close_panel()
                    area.tag_redraw()

        for widget, rect in compute_layout(context, area):
            if point_in_rect(mx, my, rect):
                widget.on_click(context, area, region)
                area.tag_redraw()
                return {'FINISHED'}
        return {'PASS_THROUGH'}


class home_builder_OT_hud_scroll(bpy.types.Operator):
    """Routes a wheel notch over the pinned navigator's list to its scroll;
    anywhere else the wheel passes through to the viewport as usual."""
    bl_idname = "home_builder.hud_scroll"
    bl_label = "Home Builder HUD Scroll"
    bl_options = {'INTERNAL'}

    rows: bpy.props.IntProperty(default=1)  # type: ignore

    @classmethod
    def poll(cls, context):
        return _hud_event_poll(context) and scene_navigator.panel_open()

    def invoke(self, context, event):
        area = context.area
        ax, atop = _nav_anchor(context, area)
        layout = scene_navigator.build_pinned_layout(
            context, area, context.region, ax, atop)
        if layout and scene_navigator.handle_navigator_scroll(
                context, event.mouse_region_x, event.mouse_region_y,
                layout[1], self.rows):
            area.tag_redraw()
            return {'FINISHED'}
        return {'PASS_THROUGH'}


class home_builder_OT_hud_hover(bpy.types.Operator):
    """Tracks the cursor for HUD hover highlights. Stores the region-local
    mouse position for the draw handler and tags a redraw only when the
    hovered widget changes (or while the pinned navigator is open, which
    paints its own internal hover) -- cheaper than the old listener, which
    redrew the viewport on every mouse move."""
    bl_idname = "home_builder.hud_hover"
    bl_label = "Home Builder HUD Hover"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _hud_event_poll(context)

    def invoke(self, context, event):
        global _mouse, _mouse_region, _last_hover_key
        _mouse = (event.mouse_region_x, event.mouse_region_y)
        _mouse_region = context.region

        hover_key = None
        for i, (_widget, rect) in enumerate(
                compute_layout(context, context.area)):
            if point_in_rect(_mouse[0], _mouse[1], rect):
                hover_key = i
                break
        if hover_key != _last_hover_key or scene_navigator.panel_open():
            _last_hover_key = hover_key
            context.area.tag_redraw()
        return {'PASS_THROUGH'}


# ---- Lifecycle --------------------------------------------------------------

def _register_keymaps():
    """Hook the HUD operators into the addon keyconfig. `any=True` matches
    regardless of modifier state, mirroring the old listener which consumed
    widget presses with any modifiers held. No-op in background mode."""
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        home_builder_OT_hud_click.bl_idname, 'LEFTMOUSE', 'PRESS',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(
        home_builder_OT_hud_hover.bl_idname, 'MOUSEMOVE', 'ANY',
        any=True, head=True)
    _addon_keymaps.append((km, kmi))
    step = scene_navigator.SCROLL_STEP_ROWS
    for ev_type, rows in (('WHEELUPMOUSE', -step), ('WHEELDOWNMOUSE', step)):
        kmi = km.keymap_items.new(
            home_builder_OT_hud_scroll.bl_idname, ev_type, 'PRESS',
            any=True, head=True)
        kmi.properties.rows = rows
        _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def ensure_listener():
    """Kept for API compatibility -- the load_post handler used to re-arm
    the modal listener here. Keymap entries survive .blend loads, so there
    is nothing to re-arm anymore."""
    return


classes = (
    home_builder_OT_hud_click,
    home_builder_OT_hud_scroll,
    home_builder_OT_hud_hover,
)


def register():
    global _draw_handle, _hud_shutdown
    _hud_shutdown = False
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_hud, (), 'WINDOW', 'POST_PIXEL')
    _register_keymaps()


def unregister():
    global _draw_handle, _hud_shutdown
    _hud_shutdown = True
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
