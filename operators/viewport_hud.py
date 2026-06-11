"""Persistent GPU-drawn control HUD for the 3D viewport.

When the `use_viewport_hud` addon preference is enabled, draws controls
along the top of every 3D viewport: a left-anchored scene-navigator
trigger (just past the toolbar) and a centered selection-mode picker for
the active product library.
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
    draw_text,
    point_in_rect,
)
# Sibling module -- safe to import at load (scene_navigator imports viewport_hud
# only lazily, inside its pin-toggle handler, so there's no import cycle).
from . import scene_navigator

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

BTN_BG          = (0.13, 0.13, 0.14, 0.95)
BTN_HOVER_BG    = (0.25, 0.25, 0.27, 0.96)
BTN_ACTIVE_BG   = (0.20, 0.43, 0.70, 0.98)
BTN_BORDER      = (1.0, 1.0, 1.0, 0.14)
GLYPH_COLOR     = (0.92, 0.92, 0.92, 1.0)
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


# ---- Widgets ----------------------------------------------------------------

def _draw_centered_text(font_id, rect, size, color, text):
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    tw, th = blf.dimensions(font_id, text)
    draw_text(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0,
              size, color, text)


class _NavButton:
    """Shows the active scene and opens the scene navigator. Always visible."""

    @property
    def width(self):
        # Sized to the current scene name so it doubles as a status display.
        blf.size(0, FONT_SIZE)
        text_w = blf.dimensions(0, bpy.context.scene.name)[0]
        return int(NAV_TEXT_LEFT + text_w + NAV_PAD_RIGHT)

    def visible(self, context):
        return True

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        draw_rect(shader, rx, ry, rw, rh,
                  BTN_HOVER_BG if hovered else BTN_BG)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        # Hamburger glyph -- three stacked bars, left-aligned. blf can't
        # render Blender's icon set in a GPU pass, so it's drawn by hand.
        bar_w = 12
        bar_h = 2
        gap = 3
        gx = rx + 9
        total = bar_h * 3 + gap * 2
        gy = ry + (rh - total) / 2.0
        for i in range(3):
            draw_rect(shader, gx, gy + i * (bar_h + gap), bar_w, bar_h,
                      GLYPH_COLOR)
        # Current scene name -- shows the active scene at a glance and is
        # itself the target that opens the navigator.
        name = context.scene.name
        blf.size(font_id, FONT_SIZE)
        label_h = blf.dimensions(font_id, name)[1]
        draw_text(font_id, rx + NAV_TEXT_LEFT, ry + (rh - label_h) / 2.0,
                  FONT_SIZE, TEXT_NORMAL, name)

    def on_click(self, context, area, region):
        # When pinned, the persistent HUD already draws the navigator panel,
        # so the button is a no-op (the header pin glyph un-pins). Otherwise
        # open the transient drop-down modal anchored just below this button.
        if scene_navigator.is_pinned():
            return
        anchor_x = anchor_top = -1.0
        for widget, rect in compute_layout(context, area):
            if widget is self:
                anchor_x = rect[0]
                anchor_top = rect[1] - 6
                break
        try:
            with context.temp_override(area=area, region=region):
                bpy.ops.home_builder.scene_navigator(
                    'INVOKE_DEFAULT', anchor_x=anchor_x, anchor_top=anchor_top)
        except Exception:
            pass


class _ModeButton:
    """One selection-mode pick. Sets the scene enum on click; the enum's
    own update callback drives the highlight toggle. A _SelectionWiring
    supplies the per-product props (scene group, enum, optional master
    enable bool), so one class serves both the face frame and frameless
    pickers."""
    width = MODE_BTN_WIDTH

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
        _draw_centered_text(font_id, rect, FONT_SIZE, color, self.label)

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
        blf.size(0, FONT_SIZE)
        w_enable = blf.dimensions(0, self.enable_label)[0]
        w_disable = blf.dimensions(0, self.disable_label)[0]
        return int(max(w_enable, w_disable)) + 24  # text + horizontal pad

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
        _draw_centered_text(font_id, rect, FONT_SIZE, color, self._label())

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
_NAV_BUTTON = _NavButton()
# Face frame (6 modes) and frameless (5 -- no Face Frame) buttons share one
# group. Each self-gates on its product tab via visible(), so compute_layout
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
]

_GRAB_CABINET_BUTTON = _ModalToggleButton(
    'hb_face_frame.grab_cabinet', 'Cabinets',
    enable_label="Enable Grab Cabinet",
    disable_label="Disable Grab Cabinet",
)
_GRAB_FACE_FRAME_BUTTON = _ModalToggleButton(
    'hb_face_frame.grab_face_frame', 'Face Frame',
    enable_label="Enable Grab Face Frame",
    disable_label="Disable Grab Face Frame",
)
_OPEN_DOOR_BUTTON = _ModalToggleButton(
    'hb_face_frame.open_mode', 'Parts',
    enable_label="Enable Open Door Mode",
    disable_label="Disable Open Door Mode",
)
_MODAL_TOGGLE_BUTTONS = [
    _GRAB_CABINET_BUTTON, _GRAB_FACE_FRAME_BUTTON, _OPEN_DOOR_BUTTON,
]


def _rows():
    """Centered HUD rows, top to bottom. Each row is a list of widget groups;
    groups are separated by GROUP_GAP, widgets within a group by BTN_GAP, and
    the whole row is centered along the top of the viewport.

    The scene-navigator button is NOT in these rows -- compute_layout places
    it separately, left-anchored just past the toolbar.

    The first row holds the selection-mode picker; the second holds the grab
    toggles. The toggles' visible() checks gate on selection mode and
    modal-active state, so that row contains at most one rendered button at a
    time (or zero, in which case compute_layout skips the row entirely)."""
    return [
        [_MODE_BUTTONS],
        [_MODAL_TOGGLE_BUTTONS],
    ]


def compute_layout(context, area):
    """Return [(widget, rect), ...] for every currently-visible widget, in
    WINDOW-local pixel coords. Shared by the draw handler and the click
    listener so their rects cannot drift apart."""
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    visible_w = x_max - x_min
    placed = []
    top_y = y_max - HUD_MARGIN_Y - BTN_HEIGHT

    # The scene-navigator button is left-anchored just past the toolbar,
    # not part of the centered rows -- a fixed spot makes it easy to find
    # and its panel opens directly below it.
    if _NAV_BUTTON.visible(context):
        placed.append((_NAV_BUTTON, (x_min + HUD_MARGIN_X, top_y,
                                     _NAV_BUTTON.width, BTN_HEIGHT)))

    cursor_y = top_y
    for row in _rows():
        groups = [[w for w in g if w.visible(context)] for g in row]
        groups = [g for g in groups if g]
        if not groups:
            continue
        row_w = GROUP_GAP * (len(groups) - 1)
        for g in groups:
            row_w += sum(w.width for w in g) + BTN_GAP * (len(g) - 1)
        cursor_x = x_min + (visible_w - row_w) / 2.0
        for gi, group in enumerate(groups):
            if gi > 0:
                cursor_x += GROUP_GAP
            for wi, w in enumerate(group):
                if wi > 0:
                    cursor_x += BTN_GAP
                placed.append((w, (cursor_x, cursor_y, w.width, BTN_HEIGHT)))
                cursor_x += w.width
        cursor_y -= BTN_HEIGHT + ROW_GAP
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
    if scene_navigator.is_pinned():
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region is not None:
            ax, atop = _nav_anchor(context, area)
            layout = scene_navigator.build_pinned_layout(
                context, area, region, ax, atop)
            if layout and point_in_rect(region_x, region_y, layout[0]):
                return True
    return False


# ---- Draw handler -----------------------------------------------------------

def _nav_anchor(context, area):
    """(x, top) just under the HUD nav button, for placing the pinned
    navigator panel. (-1, -1) when the nav button isn't currently laid out."""
    for widget, rect in compute_layout(context, area):
        if isinstance(widget, _NavButton):
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
    if scene_navigator.is_pinned():
        ax = atop = -1.0
        for widget, rect in placed:
            if isinstance(widget, _NavButton):
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

        # Pinned navigator panel gets first crack at the press; a hit
        # inside its rect is consumed, a miss falls through to widgets.
        if scene_navigator.is_pinned():
            ax, atop = _nav_anchor(context, area)
            layout = scene_navigator.build_pinned_layout(
                context, area, region, ax, atop)
            if layout and point_in_rect(mx, my, layout[0]):
                scene_navigator.handle_navigator_click(
                    context, mx, my, layout[1])
                area.tag_redraw()
                return {'FINISHED'}

        for widget, rect in compute_layout(context, area):
            if point_in_rect(mx, my, rect):
                widget.on_click(context, area, region)
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
        if hover_key != _last_hover_key or scene_navigator.is_pinned():
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
