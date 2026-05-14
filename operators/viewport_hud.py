"""Persistent GPU-drawn control HUD for the 3D viewport.

When the `use_viewport_hud` addon preference is enabled, draws a small
control strip in the top-left of every 3D viewport: a scene-navigator
trigger plus the face frame selection-mode picker. A permanent draw
handler renders the strip; a persistent modal listener routes clicks on
widget rects to their actions while passing every other event through.

Widgets are intentionally thin -- they read and write properties that
already own their update callbacks (face_frame_selection_mode and its
master enable bool), so the HUD contributes presentation and hit-testing
only, never selection logic.
"""

import bpy
import gpu
import blf

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    draw_rect,
    draw_rect_outline,
    draw_text,
    point_in_rect,
)

# operators/ sits one level below the addon root; the AddonPreferences
# bl_idname is the root package name.
_ADDON_PKG = __package__.rsplit(".", 1)[0]


# ---- Module state -----------------------------------------------------------

_draw_handle = None        # permanent SpaceView3D draw handler
_hud_shutdown = False      # set by unregister(); listener exits on next event
_generation = 0            # bumped each register() to retire stale listeners
_active_gen = None         # generation of the currently live listener
_mouse = (-1, -1)          # last cursor pos, region-local
_mouse_region = None       # region _mouse was measured in (hover is per-region)


# ---- Layout + style ---------------------------------------------------------

HUD_MARGIN_Y    = 12
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


def _face_frame_ui_visible(context):
    """Selection-mode widgets show only on the face frame product tab and
    only in a real room scene -- mirrors the sidebar panel's gating."""
    scene = context.scene
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    hb = getattr(scene, 'home_builder', None)
    return getattr(hb, 'product_tab', 'FRAMELESS') == 'FACE FRAME'


def _viewport_under_cursor(context, event):
    """Resolve the VIEW_3D area + WINDOW region under the cursor from
    absolute event coords. A window-level modal cannot trust context.area,
    and hit-testing the layout directly also lets the HUD work across every
    viewport in the window. Returns (area, region) or (None, None)."""
    win = context.window
    if win is None:
        return (None, None)
    mx, my = event.mouse_x, event.mouse_y
    for area in win.screen.areas:
        if area.type != 'VIEW_3D':
            continue
        for region in area.regions:
            if region.type == 'WINDOW' and (
                    region.x <= mx < region.x + region.width and
                    region.y <= my < region.y + region.height):
                return (area, region)
    return (None, None)


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
        # Anchor the navigator panel just below this button.
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
    """One face frame selection-mode pick. Sets the scene enum on click;
    the enum's own update callback drives the highlight toggle."""
    width = MODE_BTN_WIDTH

    def __init__(self, mode_value, label):
        self.mode_value = mode_value
        self.label = label

    def visible(self, context):
        return _face_frame_ui_visible(context)

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        ff = context.scene.hb_face_frame
        is_active = (ff.face_frame_selection_mode_enabled
                     and ff.face_frame_selection_mode == self.mode_value)
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
        ff = context.scene.hb_face_frame
        # No separate enable toggle in the HUD -- picking any mode turns
        # selection mode on if it was off; Parts mode is the practical
        # "neutral" state.
        if not ff.face_frame_selection_mode_enabled:
            ff.face_frame_selection_mode_enabled = True
        ff.face_frame_selection_mode = self.mode_value


# Widget instances. Mode values must match the EnumProperty items on
# Face_Frame_Scene_Props.face_frame_selection_mode.
_NAV_BUTTON = _NavButton()
_MODE_BUTTONS = [
    _ModeButton('Cabinets', "Cabinets"),
    _ModeButton('Bays', "Bays"),
    _ModeButton('Openings', "Openings"),
    _ModeButton('Face Frame', "Face Frame"),
    _ModeButton('Interiors', "Interiors"),
    _ModeButton('Parts', "Parts"),
]


def _rows():
    """HUD rows, top to bottom. Each row is a list of widget groups; groups
    are separated by GROUP_GAP, widgets within a group by BTN_GAP, and the
    whole row is centered along the top of the viewport."""
    return [
        [[_NAV_BUTTON], _MODE_BUTTONS],
    ]


def compute_layout(context, area):
    """Return [(widget, rect), ...] for every currently-visible widget, in
    WINDOW-local pixel coords. Shared by the draw handler and the click
    listener so their rects cannot drift apart."""
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    visible_w = x_max - x_min
    placed = []
    cursor_y = y_max - HUD_MARGIN_Y - BTN_HEIGHT
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


# ---- Draw handler -----------------------------------------------------------

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


# ---- Click listener ---------------------------------------------------------

class home_builder_OT_viewport_hud_listener(bpy.types.Operator):
    """Background modal that routes viewport clicks to HUD widgets. Passes
    every event through except a left-press landing on a widget rect, so it
    never interferes with viewport navigation, gizmos, or other modals."""
    bl_idname = "home_builder.viewport_hud_listener"
    bl_label = "Home Builder Viewport HUD Listener"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        global _active_gen
        # One live listener per generation; a stale one retires itself below.
        if _active_gen == _generation:
            return {'CANCELLED'}
        self._gen = _generation
        _active_gen = _generation
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _active_gen

        # Retire on shutdown or when a newer generation has taken over.
        if _hud_shutdown or self._gen != _generation:
            if _active_gen == self._gen:
                _active_gen = None
            return {'CANCELLED'}

        # Stay alive but inert while the HUD preference is off, so toggling
        # it back on does not require a re-arm.
        if not _hud_enabled():
            return {'PASS_THROUGH'}

        # context.area / context.region are unreliable for a window-level
        # modal, so resolve the viewport under the cursor from absolute
        # event coords instead.
        area, region = _viewport_under_cursor(context, event)
        in_viewport = area is not None and region is not None

        if event.type == 'MOUSEMOVE':
            if in_viewport:
                global _mouse, _mouse_region
                _mouse = (event.mouse_x - region.x, event.mouse_y - region.y)
                _mouse_region = region
                area.tag_redraw()
            return {'PASS_THROUGH'}

        if (event.type == 'LEFTMOUSE' and event.value == 'PRESS'
                and in_viewport):
            mx = event.mouse_x - region.x
            my = event.mouse_y - region.y
            for widget, rect in compute_layout(context, area):
                if point_in_rect(mx, my, rect):
                    widget.on_click(context, area, region)
                    area.tag_redraw()
                    return {'RUNNING_MODAL'}  # consume -- keep it off the viewport
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}


# ---- Lifecycle --------------------------------------------------------------

def _start_listener():
    """Timer callback: ensure a listener for the current generation is live.
    Retries shortly if no usable window exists yet (e.g. right at startup).
    Returns None to unregister the timer once satisfied.

    The modal must be invoked under a window override -- a modal operator
    started from a timer with no window in context is added to nothing and
    never receives events."""
    if _hud_shutdown:
        return None
    if _active_gen == _generation:
        return None
    wm = bpy.context.window_manager
    window = wm.windows[0] if (wm and wm.windows) else None
    if window is None:
        return 0.5
    try:
        with bpy.context.temp_override(window=window):
            bpy.ops.home_builder.viewport_hud_listener('INVOKE_DEFAULT')
    except Exception:
        return 0.5
    return None


def ensure_listener():
    """Re-arm the click listener. Called on file load -- modal operators do
    not survive a .blend load, so the listener must be restarted."""
    if _hud_shutdown:
        return
    if not bpy.app.timers.is_registered(_start_listener):
        bpy.app.timers.register(_start_listener, first_interval=0.1)


classes = (
    home_builder_OT_viewport_hud_listener,
)


def register():
    global _draw_handle, _hud_shutdown, _generation
    _hud_shutdown = False
    _generation += 1
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw_hud, (), 'WINDOW', 'POST_PIXEL')
    # Cannot invoke a modal during register(); defer the first start.
    bpy.app.timers.register(_start_listener, first_interval=0.1)


def unregister():
    global _draw_handle, _hud_shutdown, _active_gen
    # Flip the flag first so the live listener retires on its next event.
    _hud_shutdown = True
    _active_gen = None
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    if bpy.app.timers.is_registered(_start_listener):
        try:
            bpy.app.timers.unregister(_start_listener)
        except Exception:
            pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
