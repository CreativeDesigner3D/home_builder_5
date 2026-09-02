"""Persistent GPU-drawn control HUD for the 3D viewport.

When the `use_viewport_hud` addon preference is enabled, draws controls
along the top of every 3D viewport: a left-anchored scene-navigator
trigger (just past the toolbar; it moves into the centered row when the
viewport's overlay text occupies that corner), a centered
selection-mode picker for the active product library, and a
right-anchored strip of Blender's own viewport controls -- box select,
move, rotate and View All -- beside the navigation gizmo.
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

import math

import bpy
import gpu
import blf
from collections import namedtuple

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    navigation_gizmo_reserve,
    draw_rect,
    draw_rect_outline,
    draw_lines,
    draw_text,
    point_in_rect,
)
# Shared widget layer -- the same UI scale and palette the scene
# navigator draws with, so the two surfaces cannot drift apart.
from ..hb_gpu_ui import (Theme, scale as _s, draw_arrow_head,
                         arc_points, draw_polyline, fit_text)
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
_last_room = None          # name of the last room scene the HUD drew in
_room_views = {}           # room name -> how that room was last being looked at
_room_views_file = None    # the file _room_views was filled from


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

def _glyph_open_door(shader, rect, color):
    """A door swung open on its hinge, with the arc it travels.

    The plan door symbol, which is how a swing is drawn everywhere else
    on a drawing. The leaf is a panel rather than a single line -- at
    this size a line plus an arc reads as a wedge, not a door -- and it
    is left part way open rather than at the ninety degrees the room
    palette's Door tool uses, so the two marks stay distinguishable.
    """
    rx, ry, rw, rh = rect
    r = min(rw, rh) * 0.56
    # Hinge at the low-left of the mark; everything sweeps up and right
    # from it, so centring the r-square centres the symbol.
    hx = rx + (rw - r) / 2.0
    hy = ry + (rh - r) / 2.0
    # The opening the door sits in: closed, the leaf would lie along this.
    draw_lines(shader, [(hx, hy), (hx + r, hy)], color)
    ang = math.radians(58.0)
    ca, sa = math.cos(ang), math.sin(ang)
    leaf = r * 0.94
    thick = r * 0.17
    tip = (hx + leaf * ca, hy + leaf * sa)
    nx, ny = -sa * thick, ca * thick
    draw_polyline(shader,
                  [(hx, hy), tip, (tip[0] + nx, tip[1] + ny),
                   (hx + nx, hy + ny)],
                  color, closed=True)
    draw_polyline(shader, arc_points(hx, hy, leaf, ang, 0.0, 10), color)


def _dashes(pts, ax, ay, bx, by, count):
    """Append `count` dashes spanning (ax, ay) -> (bx, by) into `pts`."""
    steps = count * 2 - 1
    dx = (bx - ax) / steps
    dy = (by - ay) / steps
    for i in range(0, steps, 2):
        pts.append((ax + dx * i, ay + dy * i))
        pts.append((ax + dx * (i + 1), ay + dy * (i + 1)))


def _glyph_drawing_lines(shader, rect, color):
    """A drawn panel with its hidden line: solid outline, dashed middle.

    The mark for a line-work overlay -- the two line kinds a technical
    drawing is made of, in one square. Default glyph for mode-row
    toggles registered by a line engine.
    """
    rx, ry, rw, rh = rect
    r = min(rw, rh) * 0.56
    x0 = rx + (rw - r) / 2.0
    y0 = ry + (rh - r) / 2.0
    draw_polyline(shader,
                  [(x0, y0), (x0 + r, y0), (x0 + r, y0 + r), (x0, y0 + r)],
                  color, closed=True)
    pts = []
    _dashes(pts, x0 + r * 0.14, y0 + r * 0.5, x0 + r * 0.86, y0 + r * 0.5, 3)
    draw_lines(shader, pts, color)


def _glyph_select_box(shader, rect, color):
    """A dashed rectangle -- the mark Blender itself puts on this tool,
    so the button looks like the thing it switches to."""
    rx, ry, rw, rh = rect
    w, h = rw * 0.46, rh * 0.46
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    pts = []
    _dashes(pts, x0, y0, x1, y0, 3)
    _dashes(pts, x0, y1, x1, y1, 3)
    _dashes(pts, x0, y0, x0, y1, 3)
    _dashes(pts, x1, y0, x1, y1, 3)
    draw_lines(shader, pts, color)


def _glyph_move(shader, rect, color):
    """Two arrows off one corner -- one up, one right.

    Not the four-way cross: the Move pill on the selection row already
    wears that, and two buttons meaning different things must not carry
    the same mark. This is the move gizmo's own shape, an axis pair,
    which says translate just as plainly.
    """
    rx, ry, rw, rh = rect
    arm = min(rw, rh) * 0.30
    head = arm * 0.52
    # The mark spans two arms from its corner, so the corner sits one
    # arm below and left of centre for the whole of it to be centred.
    ox = rx + rw / 2.0 - arm
    oy = ry + rh / 2.0 - arm
    right = (ox + arm * 2.0, oy)
    up = (ox, oy + arm * 2.0)
    draw_lines(shader, [(ox, oy), right, (ox, oy), up], color)
    draw_arrow_head(shader, right, (1.0, 0.0), head, color)
    draw_arrow_head(shader, up, (0.0, 1.0), head, color)


def _glyph_rotate(shader, rect, color):
    """An arc with a head on it -- a turn, part way through."""
    rx, ry, rw, rh = rect
    r = min(rw, rh) * 0.28
    cx, cy = rx + rw / 2.0, ry + rh / 2.0
    start, end = math.radians(-45.0), math.radians(225.0)
    pts = arc_points(cx, cy, r, start, end, 16)
    draw_polyline(shader, pts, color)
    # Head at the far end, swung along the tangent so it reads as travel
    # around the circle rather than away from it.
    draw_arrow_head(shader, pts[-1],
                    (-math.sin(end), math.cos(end)), r * 0.62, color)


def _glyph_view_all(shader, rect, color):
    """Four corner brackets -- a frame being fitted around everything.

    A viewfinder rather than an arrow: this button changes where you are
    looking, and every arrow in this strip already means move something.
    """
    rx, ry, rw, rh = rect
    w, h = rw * 0.52, rh * 0.52
    x0 = rx + (rw - w) / 2.0
    y0 = ry + (rh - h) / 2.0
    x1, y1 = x0 + w, y0 + h
    arm = min(w, h) * 0.34
    pts = []
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                           (x0, y1, 1, -1), (x1, y1, -1, -1)):
        pts += [(cx, cy), (cx + arm * sx, cy),
                (cx, cy), (cx, cy + arm * sy)]
    draw_lines(shader, pts, color)


def _draw_centered_text(font_id, rect, size, color, text):
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    tw, th = blf.dimensions(font_id, text)
    draw_text(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0,
              size, color, text)


def _region_3d(area):
    """The orbit state of a 3D area's main region, or None."""
    space = area.spaces.active if area is not None else None
    return getattr(space, "region_3d", None)


def _remember_room(scene, area):
    """Note the room we are in and how it is being looked at, so leaving
    it can be undone.

    Recorded from compute_layout rather than from a scene-change
    handler: the HUD is laid out every time a viewport draws, so by the
    time anything can take you out of a room, the room you were in has
    already been seen. No handler to register, nothing to keep in sync.

    The view is kept alongside the name because orbit state belongs to
    the VIEWPORT, not the scene, so it does not travel with a scene
    switch. Without it, going back to a room leaves you looking from
    wherever the sheet or card you just left had put the view.
    """
    global _last_room, _room_views_file
    # Views are remembered by room NAME, and names repeat across files, so
    # a cache carried into another file would restore a view from the
    # wrong one. Dropping it here needs no load handler for the same
    # reason the rest of this does: a viewport draws before anything can
    # be clicked, so the cache is always current by the time it is read.
    if _room_views_file != bpy.data.filepath:
        _room_views.clear()
        _room_views_file = bpy.data.filepath
    if not scene_navigator.is_room(scene):
        return
    _last_room = scene.name
    rv3d = _region_3d(area)
    if rv3d is not None:
        _room_views[scene.name] = (
            tuple(rv3d.view_location),
            tuple(rv3d.view_rotation),
            float(rv3d.view_distance),
            rv3d.view_perspective,
        )


def _restore_room_view(room, area):
    """Put the viewport back the way this room was left.

    A no-op for a room the HUD has not drawn in yet -- opening a file
    straight onto a sheet is the case -- which leaves the view alone
    rather than guessing at one.
    """
    view = _room_views.get(room.name)
    rv3d = _region_3d(area)
    if view is None or rv3d is None:
        return
    loc, rot, dist, persp = view
    # Projection first: a camera view locks the orbit fields, so there is
    # nothing to push into them.
    rv3d.view_perspective = persp
    if persp != 'CAMERA':
        rv3d.view_location = loc
        rv3d.view_rotation = rot
        rv3d.view_distance = dist


def _room_to_return_to(context):
    """The room scene a Back press should go to, or None when there is
    nothing to go back to (we are in a room already, or the file has no
    rooms at all).

    Falls back to the first room in navigator order when nothing has
    been remembered -- opening a file straight onto a detail card is the
    case, and naming a room on the button beats offering no way out.
    """
    scene = context.scene
    if scene is None or scene_navigator.is_room(scene):
        return None
    remembered = bpy.data.scenes.get(_last_room) if _last_room else None
    if scene_navigator.is_room(remembered):
        return remembered
    rooms = [s for s in bpy.data.scenes if scene_navigator.is_room(s)]
    rooms.sort(key=scene_navigator.sort_key)
    return rooms[0] if rooms else None


class _BackToRoomButton:
    """Leave a detail card or a layout sheet for the room you came from.

    Getting into a detail is one click from the toolbar; getting out was
    a trip through the Rooms tab to find a scene you never chose to
    leave. This is the way back, sitting after the panel tabs, and it
    names the room so it is a destination rather than a guess.
    """

    MAX_LABEL = 108        # unscaled; a long room name is elided, not obeyed

    def _label(self, context):
        room = _room_to_return_to(context)
        return room.name if room is not None else ""

    @property
    def width(self):
        s = _s()
        blf.size(0, FONT_SIZE * s)
        text = fit_text(0, FONT_SIZE * s, self._label(bpy.context),
                        self.MAX_LABEL * s)
        return int(blf.dimensions(0, text)[0] + 34 * s)   # arrow + padding

    def visible(self, context):
        return _room_to_return_to(context) is not None

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        s = _s()
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        draw_rect(shader, rx, ry, rw, rh, BTN_HOVER_BG if hovered else BTN_BG)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        color = TEXT_ACTIVE if hovered else TEXT_NORMAL
        # Arrow first, then the room name: the mark says what the button
        # does, the name says where it lands.
        cy = ry + rh / 2.0
        ax = rx + 9 * s
        arm = 7 * s
        draw_lines(shader, [(ax, cy), (ax + arm * 1.6, cy)], color)
        draw_arrow_head(shader, (ax, cy), (-1.0, 0.0), arm * 0.75, color)
        size = FONT_SIZE * s
        blf.size(font_id, size)
        text = fit_text(font_id, size, self._label(context),
                        self.MAX_LABEL * s)
        th = blf.dimensions(font_id, text)[1]
        draw_text(font_id, ax + arm * 1.6 + 7 * s, cy - th / 2.0,
                  size, color, text)

    def on_click(self, context, area, region):
        room = _room_to_return_to(context)
        if room is None:
            return
        context.window.scene = room
        _restore_room_view(room, area)


_BACK_BUTTON = _BackToRoomButton()


class _PanelTabButton:
    """One of the panel tabs at the top-left -- the built-in ROOMS /
    LIBRARY / OPTIONS, or one an add-on contributed.

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
    def label(self):
        """What the button says. A tab key has to be stable and unique;
        that makes it a poor caption, so a contributed tab supplies its
        own. Built-in keys read fine as their own labels."""
        return scene_navigator.tab_label(self.tab)

    @property
    def width(self):
        s = _s()
        blf.size(0, FONT_SIZE * s)
        return int(blf.dimensions(0, self.label)[0] + 22 * s)

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
        label = self.label
        tw, th = blf.dimensions(font_id, label)
        draw_text(font_id, rx + (rw - tw) / 2.0, ry + (rh - th) / 2.0,
                  font_sz, TEXT_ACTIVE if active else TEXT_NORMAL, label)

    def on_click(self, context, area, region):
        if self._showing():
            # The tab that opened the panel is what closes it again --
            # nothing the panel itself does dismisses it.
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

    Pass a `glyph` to draw it as a square icon instead. A toggle that
    rides in the selection-mode row has to earn its width there, and a
    state you leave on is a mark, not a sentence -- the same reasoning
    the Grab pill follows. The Enable / Disable wording is not lost: it
    becomes the hover label.
    """

    def __init__(self, op_idname, mode_value, enable_label, disable_label,
                 glyph=None):
        self.op_idname = op_idname  # e.g. "hb_face_frame.grab_cabinet"
        self.mode_value = mode_value
        self.enable_label = enable_label
        self.disable_label = disable_label
        self.glyph = glyph

    # ---- internal helpers ----

    def _is_my_modal_active(self):
        return active_modal_idname() == self.op_idname

    def _label(self):
        return (self.disable_label if self._is_my_modal_active()
                else self.enable_label)

    def hover_label(self):
        """What the icon would say if it had the room to say it."""
        return self._label() if self.glyph is not None else None

    # ---- widget protocol ----

    @property
    def width(self):
        if self.glyph is not None:
            return int(BTN_HEIGHT * _s())      # square
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
        if self.glyph is not None:
            self.glyph(shader, rect, color)
            return
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(), color,
                            self._label())

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
def _tab_buttons():
    """The tab strip, rebuilt from the navigator's current tab list.

    Not a module constant: a tab may be registered by another add-on
    after this module is imported, and a tuple built at import time
    would never show it. The widgets are stateless -- hover is tracked
    by layout index, not identity -- so rebuilding them costs nothing.
    """
    return tuple(_PanelTabButton(t) for t in scene_navigator.tabs())
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

    def hover_label(self):
        return "Stop Moving" if self._active() else "Move"

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
    glyph=_glyph_open_door,
)


# ---- View strip -------------------------------------------------------------
# Blender's own viewport controls, kept apart from everything else the
# HUD draws. The centred rows are about the product: what is selected,
# what a drag moves, what the sizes show. Box select, move, rotate and
# View All are about the viewport -- how you point at the model and
# where you are looking from. They are also not tools in the sense the
# room palette uses the word, where every button makes something; these
# make nothing.
#
# So they get a strip of their own at the top right, beside the
# navigation gizmo, which is the other control of the same kind. Being
# anchored to that corner they hold still while the centred rows grow
# and shrink under the selection mode.


def _active_tool_id(context):
    """idname of the workspace tool in force here, or None.

    The active tool is per space type AND mode, so it has to be asked
    for by mode rather than read off the workspace.
    """
    try:
        ref = context.workspace.tools.from_space_view3d_mode(
            context.mode, create=False)
    except Exception:
        return None
    return getattr(ref, 'idname', None)


def _with_hotkey(label, hotkey):
    """Hover text for a button that also answers to a key.

    The keys are the stock ones; a remapped keymap would make the chip
    lie, so only buttons whose key we ship are given one.
    """
    return "%s (%s)" % (label, hotkey) if hotkey else label


class _ViewportToolButton:
    """One of Blender's viewport tools as a HUD button.

    Sets the active tool on click and highlights while that tool is the
    one in force, so the three of them read as the radio group they are.
    Switching is all it does -- the tool itself is Blender's.
    """

    def __init__(self, tool_id, label, glyph, hotkey=None):
        self.tool_id = tool_id
        self.label = label
        self.glyph = glyph
        self.hotkey = hotkey

    @property
    def width(self):
        return int(BTN_HEIGHT * _s())        # square

    def hover_label(self):
        return _with_hotkey(self.label, self.hotkey)

    def visible(self, context):
        # Always: every scene the HUD draws in is a viewport. The
        # product rows come and go with what a scene is for; these do
        # not, and a control that moves house is a control you hunt for.
        return True

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        active = _active_tool_id(context) == self.tool_id
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        bg = (BTN_ACTIVE_BG if active
              else (BTN_HOVER_BG if hovered else BTN_BG))
        draw_rect(shader, rx, ry, rw, rh, bg)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        self.glyph(shader, rect, TEXT_ACTIVE if active else TEXT_NORMAL)

    def on_click(self, context, area, region):
        try:
            with context.temp_override(area=area, region=region):
                bpy.ops.wm.tool_set_by_id(name=self.tool_id)
        except Exception:
            pass


class _IconCommandButton:
    """Square glyph button that fires an operator and is done.

    The sheet row's command button is this with a word on it; on a strip
    where every button is an icon the name arrives on hover instead.
    """

    def __init__(self, op_idname, label, glyph, hotkey=None):
        self.op_idname = op_idname
        self.label = label
        self.glyph = glyph
        self.hotkey = hotkey

    @property
    def width(self):
        return int(BTN_HEIGHT * _s())

    def hover_label(self):
        return _with_hotkey(self.label, self.hotkey)

    def visible(self, context):
        return True

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        draw_rect(shader, rx, ry, rw, rh, BTN_HOVER_BG if hovered else BTN_BG)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        self.glyph(shader, rect, TEXT_ACTIVE if hovered else TEXT_NORMAL)

    def on_click(self, context, area, region):
        ns, name = self.op_idname.split('.')
        try:
            with context.temp_override(area=area, region=region):
                getattr(getattr(bpy.ops, ns), name)('INVOKE_DEFAULT')
        except Exception:
            pass


_VIEW_TOOL_BUTTONS = [
    _ViewportToolButton('builtin.select_box', "Box Select",
                        _glyph_select_box),
    _ViewportToolButton('builtin.move', "Move", _glyph_move, hotkey="G"),
    _ViewportToolButton('builtin.rotate', "Rotate", _glyph_rotate,
                        hotkey="R"),
]
# What the Home key does, on a button. Framing the model back up is the
# navigation move that is hardest to do by hand, and the keyboard is a
# long way from a mouse that is already on the model.
_VIEW_ALL_BUTTON = _IconCommandButton(
    'view3d.view_all', "View All", _glyph_view_all, hotkey="HOME")


def _view_strip():
    """The right-anchored groups: what a drag does, then where you are
    looking. Two groups rather than one -- the tools are a state you
    leave set, View All is a button you press and it is over."""
    return [_VIEW_TOOL_BUTTONS, [_VIEW_ALL_BUTTON]]


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


class _GlyphToggleButton:
    """Square glyph toggle bound to a boolean property.

    The mode-row cousin of _SceneToggleButton: a way of LOOKING that
    rides beside Move / Open Doors / Sizes, so it draws as an icon (a
    state you leave on is a mark, not a sentence) with the wording as
    its hover label. Reads and writes the property directly; the
    property's update callback owns the real work.
    """

    def __init__(self, prop_name, glyph, show_label, hide_label,
                 ui_visible=None, owner='WINDOW_MANAGER'):
        self.prop_name = prop_name
        self.glyph = glyph
        self.show_label = show_label
        self.hide_label = hide_label
        self.ui_visible = ui_visible
        self.owner = owner

    def _host(self, context):
        if self.owner == 'WINDOW_MANAGER':
            return context.window_manager
        return context.scene

    def _is_active(self, context):
        return bool(getattr(self._host(context), self.prop_name, False))

    @property
    def width(self):
        return int(BTN_HEIGHT * _s())          # square

    def hover_label(self):
        try:
            active = bool(getattr(self._host(bpy.context), self.prop_name,
                                  False))
        except Exception:
            active = False
        return self.hide_label if active else self.show_label

    def visible(self, context):
        if not hasattr(self._host(context), self.prop_name):
            return False
        if self.ui_visible is None:
            return True
        try:
            return bool(self.ui_visible(context))
        except Exception:
            return False

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
        self.glyph(shader, rect, color)

    def on_click(self, context, area, region):
        host = self._host(context)
        setattr(host, self.prop_name,
                not getattr(host, self.prop_name, False))


class _SheetCommandButton:
    """HUD button on the sheet row that fires an operator.

    Same box as the toggles beside it, but it has no on state: it is
    pressed, it does its thing. ``available`` is the owner's own test
    for whether the command applies right now -- it is called every
    draw, so it must be cheap, and anything it raises hides the button
    rather than breaking the row.
    """

    def __init__(self, op_idname, label, ui_visible, available=None,
                 width_px=112):
        self.op_idname = op_idname
        self.label = label
        self.ui_visible = ui_visible
        self.available = available
        self.width_px = width_px

    @property
    def width(self):
        return int(self.width_px * _s())

    def visible(self, context):
        if not self.ui_visible(context):
            return False
        if self.available is None:
            return True
        try:
            return bool(self.available(context))
        except Exception:
            return False

    def draw(self, shader, font_id, rect, context, mouse):
        rx, ry, rw, rh = rect
        hovered = point_in_rect(mouse[0], mouse[1], rect)
        draw_rect(shader, rx, ry, rw, rh, BTN_HOVER_BG if hovered else BTN_BG)
        draw_rect_outline(shader, rx, ry, rw, rh, BTN_BORDER)
        _draw_centered_text(font_id, rect, FONT_SIZE * _s(),
                            TEXT_ACTIVE if hovered else TEXT_NORMAL,
                            self.label)

    def on_click(self, context, area, region):
        ns, name = self.op_idname.split('.')
        try:
            with context.temp_override(area=area, region=region):
                getattr(getattr(bpy.ops, ns), name)('INVOKE_DEFAULT')
        except Exception:
            pass


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
    _drop_sheet_button(key)
    widget = _SceneToggleButton(prop_name, label, _layout_view_visible,
                                width_px=width_px, owner=owner)
    _add_sheet_button(order, key, widget)


def register_sheet_command(key, label, op_idname, available=None,
                           width_px=112, order=100):
    """Add an operator button to the layout-view HUD row.

    The row's other entries are toggles -- state you leave on. A
    command is the other kind of thing a sheet needs: it opens or does
    something. `available` is an optional callable(context) the owner
    supplies to hide the button when it would have nothing to show, so
    the row never carries one that opens an empty list.

    Shares the toggle registry, so the two kinds order among each
    other and one key means one button whichever it is.
    """
    _drop_sheet_button(key)
    widget = _SheetCommandButton(op_idname, label, _layout_view_visible,
                                 available=available, width_px=width_px)
    _add_sheet_button(order, key, widget)


def unregister_sheet_toggle(key):
    _drop_sheet_button(key)


def unregister_sheet_command(key):
    _drop_sheet_button(key)


# Same idea for the selection-mode row's control group (Move / Open
# Doors / Sizes): other add-ons can put a way-of-looking toggle beside
# them without this module depending on them.
_extra_mode_widgets = []       # (order, key, widget)


def register_mode_glyph_toggle(key, prop_name, show_label, hide_label,
                               glyph=None, owner='WINDOW_MANAGER',
                               ui_visible=None, order=100):
    """Add a square glyph toggle to the mode row's control group.

    ``glyph`` is a callable(shader, rect, color); None uses the
    drawing-lines mark. ``ui_visible`` optionally gates which scenes
    show it. Re-registering a key replaces it, so a reloaded add-on
    cannot stack duplicates.
    """
    unregister_mode_glyph_toggle(key)
    widget = _GlyphToggleButton(
        prop_name, glyph or _glyph_drawing_lines, show_label, hide_label,
        ui_visible=ui_visible, owner=owner)
    _extra_mode_widgets.append((order, key, widget))
    _extra_mode_widgets.sort(key=lambda b: (b[0], b[1]))


def unregister_mode_glyph_toggle(key):
    for i, entry in enumerate(list(_extra_mode_widgets)):
        if entry[1] == key:
            del _extra_mode_widgets[i]
            return


def _mode_extra_widgets():
    return [b[2] for b in _extra_mode_widgets]


def _add_sheet_button(order, key, widget):
    _extra_sheet_buttons.append((order, key, widget))
    _extra_sheet_buttons.sort(key=lambda b: (b[0], b[1]))


def _drop_sheet_button(key):
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

    The first row holds the selection-mode picker and, in a group of its
    own, the controls that modify what the current mode does: Move, Open
    Doors and the Sizes scope. Open Doors had a row to itself, which put
    a lone button under the picker; it belongs beside the other two
    because it is the same kind of thing -- a way of working on what the
    mode has selected. Each self-gates on selection mode and
    modal-active state via visible(), so the group is usually one or two
    buttons wide.

    The second row holds the sheet controls, which show only on a layout
    view (where the first row is empty, so it draws at the top)."""
    return [
        [_MODE_BUTTONS,
         [_GRAB_PILL, _OPEN_DOOR_BUTTON, _SIZES_BUTTON]
         + _mode_extra_widgets()],
        [_layout_view_buttons()],
    ]


def _stats_rows(context):
    """Rows the Statistics overlay draws, per Blender's ED_info_draw_stats.

    With nothing selected it lists scene totals (five rows) or a lone
    Objects row for an empty scene; with a selection it is the Objects
    row plus whatever the active object's type and mode add."""
    any_objects = len(context.view_layer.objects) > 0
    any_selected = bool(context.selected_objects)
    mode = context.mode
    if not any_selected:
        if any_objects:
            return 5
        return 0 if mode in {'SCULPT', 'SCULPT_CURVES'} else 1
    rows = 1
    ob = context.active_object
    if ob is None:
        return rows
    if ob.type == 'GREASEPENCIL':
        rows += 4
    elif ob.mode == 'EDIT':
        rows += {'MESH': 4, 'ARMATURE': 2, 'POINTCLOUD': 1, 'CURVE': 2,
                 'SURFACE': 2, 'CURVES': 2, 'FONT': 0}.get(ob.type, 1)
    elif ob.mode == 'SCULPT':
        rows += 2
    elif ob.mode == 'SCULPT_CURVES':
        rows += 1
    elif ob.mode == 'POSE':
        rows += 1
    elif ob.type == 'LIGHT':
        rows += 1
    elif ob.mode == 'OBJECT' and ob.type in {'MESH', 'FONT'}:
        rows += 4
    return rows


def _overlay_text_height(context, area):
    """Height, in WINDOW pixels down from the top of the visible region,
    of the text block Blender draws in this viewport's top-left corner
    (General Info, Performance, Statistics). 0 when nothing is drawn
    there.

    Mirrors view3d_draw_region_info: the block starts 0.1 widget units
    down, every line is the widget font size x UI scale x 1.6,
    Performance leads with a blank line and Statistics with 0.6 of one.
    General Info is one line each for the view name and the active
    object, plus the grid unit on an axis-aligned ortho view."""
    space = area.spaces.active if area is not None else None
    overlay = getattr(space, "overlay", None)
    if overlay is None or not overlay.show_overlays:
        return 0.0
    prefs = context.preferences
    ui_scale = _s()
    try:
        points = prefs.ui_styles[0].widget.points
    except (AttributeError, IndexError):
        points = 11.0
    line_h = points * ui_scale * 1.6
    widget_unit = round(18.0 * ui_scale) + 2
    lines = 0.0
    if overlay.show_text:
        view = prefs.view
        if view.show_view_name or view.show_playback_fps:
            lines += 1
        if view.show_object_info:
            lines += 1
        rv3d = getattr(space, "region_3d", None)
        if (rv3d is not None and not rv3d.is_perspective
                and rv3d.is_orthographic_side_view
                and (overlay.show_floor or overlay.show_axis_x
                     or overlay.show_axis_y or overlay.show_axis_z)):
            lines += 1
    if getattr(overlay, "show_performance", False):
        lines += 4
    if overlay.show_stats:
        lines += 0.6 + _stats_rows(context)
    if lines <= 0.0:
        return 0.0
    return 0.1 * widget_unit + lines * line_h


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
    # on, the top of that corner belongs to Blender, so the strip keeps
    # its left edge and drops in under the text block. (It used to join
    # the centered row instead, which slid the panel to mid-viewport.)
    _remember_room(context.scene, area)
    rows = _rows()
    # The centered rows filter on visible(); this left-anchored strip
    # has to do it too, or a tab that does not apply here still gets a
    # button.
    tab_buttons = [b for b in _tab_buttons() if b.visible(context)]
    # Back TRAILS the tabs. It comes and goes with where you are, and
    # leading the strip meant every tab slid sideways as it appeared --
    # the one part of the interface that should hold still while you move
    # around. Behind the tabs it costs the tabs nothing.
    if _BACK_BUTTON.visible(context):
        tab_buttons = tab_buttons + [_BACK_BUTTON]
    tab_top = top_y
    text_h = _overlay_text_height(context, area)
    if text_h > 0.0:
        # text_h ends at the last baseline; the margin clears descenders.
        tab_top = min(top_y, y_max - text_h - margin_y - btn_h)
    tab_x = x_min + margin_x
    for tab_btn in tab_buttons:
        placed.append((tab_btn, (tab_x, tab_top, tab_btn.width, btn_h)))
        tab_x += tab_btn.width + btn_gap

    # Blender's own viewport controls, right-anchored on that same top
    # row. Inset past the navigation gizmo: the gizmo is drawn INTO the
    # window region rather than being a region of its own, so nothing
    # reports its extent and a strip in that corner would land on it.
    strip_groups = [[w for w in g if w.visible(context)]
                    for g in _view_strip()]
    strip_groups = [g for g in strip_groups if g]
    if strip_groups:
        strip_w = group_gap * (len(strip_groups) - 1)
        for g in strip_groups:
            strip_w += sum(w.width for w in g) + btn_gap * (len(g) - 1)
        strip_x = (x_max - margin_x
                   - navigation_gizmo_reserve(area)[0] - strip_w)
        for gi, group in enumerate(strip_groups):
            if gi > 0:
                strip_x += group_gap
            for wi, w in enumerate(group):
                if wi > 0:
                    strip_x += btn_gap
                placed.append((w, (strip_x, top_y, w.width, btn_h)))
                strip_x += w.width

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
            layout = scene_navigator.build_hosted_layout(
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
    layout = scene_navigator.build_hosted_layout(context, area, region,
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


def _draw_hover_chip(shader, font_id, rect, area, text):
    """Name the icon button under the cursor.

    A word costs a button its place in a row; an icon costs the user a
    guess. The chip pays for the icon by naming it on hover, drawn
    below the button so it never covers the row it belongs to.
    """
    s = _s()
    size = FONT_SIZE * s
    blf.size(font_id, size)
    tw, th = blf.dimensions(font_id, text)
    pad_x, pad_y = 7 * s, 4 * s
    cw = tw + pad_x * 2
    ch = th + pad_y * 2
    rx, ry, rw, _rh = rect
    cx = rx + (rw - cw) / 2.0
    # Clamped, so a chip on the button at the end of a row does not hang
    # half off the side of the viewport.
    x_min, x_max, _y_min, _y_max = get_visible_window_bounds(area)
    cx = max(x_min + 4 * s, min(cx, x_max - cw - 4 * s))
    cy = ry - ch - 5 * s
    draw_rect(shader, cx, cy, cw, ch, Theme.PANEL_BG)
    draw_rect_outline(shader, cx, cy, cw, ch, BTN_BORDER)
    draw_text(font_id, cx + pad_x, cy + pad_y, size, TEXT_ACTIVE, text)


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
    # After the row, so the chip sits over its neighbours rather than
    # under whichever button is drawn next.
    for widget, rect in placed:
        fn = getattr(widget, 'hover_label', None)
        if fn is None or not point_in_rect(mouse[0], mouse[1], rect):
            continue
        text = fn()
        if text:
            _draw_hover_chip(shader, font_id, rect, area, text)
        break
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
        layout = scene_navigator.build_hosted_layout(
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
            layout = scene_navigator.build_hosted_layout(
                context, area, region, ax, atop)
            if layout and point_in_rect(mx, my, layout[0]):
                hit = scene_navigator.hit_test(mx, my, layout[1])
                if hit is not None and hit[0] == 'row':
                    # A row press holds the mouse: released in place it
                    # is the ordinary click (switch / rename), dragged
                    # past the threshold it picks the row up to reorder
                    # its section. The modal lives only press-to-release,
                    # so nothing persistent is added to the handler list.
                    self._area = area
                    self._region = region
                    self._anchor = (ax, atop)
                    self._press = (mx, my)
                    scene_navigator.press_row(hit[1], my)
                    context.window_manager.modal_handler_add(self)
                    return {'RUNNING_MODAL'}
                scene_navigator.handle_navigator_click(
                    context, mx, my, layout[1])
                area.tag_redraw()
                return {'FINISHED'}
            # Clicked away: the panel stays up and the press carries on
            # to the viewport, so designing never has to reopen it.

        for widget, rect in compute_layout(context, area):
            if point_in_rect(mx, my, rect):
                widget.on_click(context, area, region)
                area.tag_redraw()
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def _entries(self, context):
        layout = scene_navigator.build_hosted_layout(
            context, self._area, self._region,
            self._anchor[0], self._anchor[1])
        return layout[1] if layout else None

    def modal(self, context, event):
        mx, my = event.mouse_region_x, event.mouse_region_y

        if event.type == 'MOUSEMOVE':
            entries = self._entries(context)
            if entries is not None:
                scene_navigator.drag_update(my, entries)
            self._area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # The list keeps scrolling under a held row, so a long
            # section can be reordered end to end.
            step = scene_navigator.SCROLL_STEP_ROWS
            scene_navigator.scroll_by(
                -step if event.type == 'WHEELUPMOUSE' else step)
            entries = self._entries(context)
            if entries is not None:
                scene_navigator.drag_update(my, entries)
            self._area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if scene_navigator.drag_active():
                scene_navigator.commit_drag()
            else:
                scene_navigator.cancel_drag()
                entries = self._entries(context)
                if entries is not None:
                    scene_navigator.handle_navigator_click(
                        context, mx, my, entries)
            self._area.tag_redraw()
            return {'FINISHED'}

        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            scene_navigator.cancel_drag()
            self._area.tag_redraw()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


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
        layout = scene_navigator.build_hosted_layout(
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
