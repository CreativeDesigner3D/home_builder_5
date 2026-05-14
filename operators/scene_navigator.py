"""
Scene Navigator -- GPU-drawn quick scene picker for Home Builder 5.

A modal overlay listing project scenes grouped by Rooms / Layout Views /
Details. The panel header shows the current scene; clicking a row switches
scenes. Room rows carry rename and delete buttons, and a New Room button
sits at the bottom -- each of those closes the navigator and opens the
corresponding operator dialog. Click outside / Esc / RMB dismisses.
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


# ---- Layout constants -------------------------------------------------------

PANEL_TOP_MARGIN      = 12      # distance from top of visible window region
PANEL_WIDTH           = 250
PANEL_PADDING_X       = 10
PANEL_PADDING_Y       = 8

ROW_HEIGHT            = 24
SECTION_GAP           = 6
SECTION_HEADER_HEIGHT = 22
ACCENT_WIDTH          = 3
ACCENT_LEFT_PAD       = 6
ROW_TEXT_LEFT_PAD     = ACCENT_LEFT_PAD + ACCENT_WIDTH + 8

PANEL_HEADER_HEIGHT   = 26
ACTION_BTN_SIZE       = 18
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

PANEL_BG       = (0.08, 0.08, 0.08, 0.93)
PANEL_BORDER   = (1.0, 1.0, 1.0, 0.10)

ROW_HOVER_BG   = (1.0, 1.0, 1.0, 0.06)

TEXT_PRIMARY   = (0.95, 0.95, 0.95, 1.0)
TEXT_NORMAL    = (0.78, 0.78, 0.78, 1.0)
TEXT_DIM       = (0.45, 0.45, 0.45, 1.0)
HEADER_TEXT    = (0.55, 0.55, 0.55, 1.0)

ACTION_BG              = (1.0, 1.0, 1.0, 0.07)
ACTION_HOVER_BG        = (1.0, 1.0, 1.0, 0.16)
ACTION_DELETE_HOVER_BG = (0.80, 0.22, 0.20, 0.65)
ACTION_GLYPH           = (0.78, 0.78, 0.78, 1.0)
ACTION_GLYPH_HOVER     = (1.0, 1.0, 1.0, 1.0)
NEW_ROOM_BG            = (0.18, 0.18, 0.20, 1.0)
NEW_ROOM_HOVER_BG      = (0.20, 0.43, 0.70, 1.0)
SEPARATOR_COLOR        = (1.0, 1.0, 1.0, 0.10)


# ---- Scene helpers ----------------------------------------------------------

def _is_room(scene):
    return not scene.get('IS_LAYOUT_VIEW') and not scene.get('IS_DETAIL_VIEW')

def _is_layout(scene):
    return bool(scene.get('IS_LAYOUT_VIEW'))

def _is_detail(scene):
    return bool(scene.get('IS_DETAIL_VIEW'))

def _sort_key(scene):
    so = 0
    if hasattr(scene, 'home_builder'):
        so = getattr(scene.home_builder, 'sort_order', 0) or 0
    return (so, scene.name.lower())

def _parent_room_name(scene):
    """Resolve a layout view's source wall back to the room scene that owns it."""
    sw_name = scene.get('SOURCE_WALL')
    if not sw_name:
        return None
    wall = bpy.data.objects.get(sw_name)
    if not wall:
        return None
    for us in wall.users_scene:
        if _is_room(us):
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

# ---- Glyph helpers ----------------------------------------------------------

def _draw_rename_glyph(shader, rect, color):
    """A small text-field box with a cursor bar -- the rename affordance."""
    rx, ry, rw, rh = rect
    pad = 4
    bx, by = rx + pad, ry + pad
    bw, bh = rw - pad * 2, rh - pad * 2
    _draw_rect_outline(shader, bx, by, bw, bh, color)
    cx = bx + bw / 3.0
    _draw_rect(shader, cx, by + 2, 1.5, bh - 4, color)


def _draw_delete_glyph(shader, rect, color):
    """An X -- the delete affordance."""
    rx, ry, rw, rh = rect
    pad = 5
    x0, y0 = rx + pad, ry + pad
    x1, y1 = rx + rw - pad, ry + rh - pad
    _draw_lines(shader, [(x0, y0), (x1, y1), (x0, y1), (x1, y0)], color)


def _draw_plus_glyph(shader, cx, cy, size, color):
    """A plus sign centered at (cx, cy)."""
    half = size / 2.0
    thick = 1.5
    _draw_rect(shader, cx - half, cy - thick / 2.0, size, thick, color)
    _draw_rect(shader, cx - thick / 2.0, cy - half, thick, size, color)


# ---- Layout computation -----------------------------------------------------

def _build_layout(region, area, current_scene_name,
                  anchor_x=-1.0, anchor_top=-1.0):
    """Compute panel rect + entry rects from current region size and scenes.

    Returns (panel_rect, entries). panel_rect is (x, y, w, h) in region px
    (y is the bottom edge). entries is a list of tuples:
        ('panel_header', current_scene_name, rect)
        ('header', label, color, rect)
        ('row', scene, parent, color, is_current, rect,
                rename_rect_or_None, delete_rect_or_None)
        ('new_room', rect)
    Room rows carry rename/delete sub-rects; other rows carry None.
    """
    groups = _collect_groups()

    content_h = PANEL_HEADER_HEIGHT + SECTION_GAP
    for i, (_, _, scenes, _) in enumerate(groups):
        if i > 0:
            content_h += SECTION_GAP
        content_h += SECTION_HEADER_HEIGHT
        content_h += ROW_HEIGHT * len(scenes)
    content_h += NEW_ROOM_GAP + NEW_ROOM_BTN_HEIGHT

    panel_w = PANEL_WIDTH
    panel_h = content_h + PANEL_PADDING_Y * 2

    x_min, x_max, y_min, y_max = _get_visible_window_bounds(area)
    visible_w = max(x_max - x_min, panel_w)

    if anchor_top >= 0.0:
        # Anchored under a specific button (the viewport HUD trigger);
        # clamp so a wide panel stays on screen.
        panel_x = min(max(anchor_x, x_min), x_max - panel_w)
        panel_top = anchor_top
    else:
        # Center horizontally within the visible window area; anchor to top.
        panel_x = x_min + (visible_w - panel_w) / 2.0
        panel_top = y_max - PANEL_TOP_MARGIN
    panel_y = panel_top - panel_h

    panel_rect = (panel_x, panel_y, panel_w, panel_h)
    content_x = panel_x + PANEL_PADDING_X
    content_w = panel_w - PANEL_PADDING_X * 2
    entries = []

    cursor_y = panel_top - PANEL_PADDING_Y

    ph_rect = (content_x, cursor_y - PANEL_HEADER_HEIGHT,
               content_w, PANEL_HEADER_HEIGHT)
    entries.append(('panel_header', current_scene_name, ph_rect))
    cursor_y -= PANEL_HEADER_HEIGHT + SECTION_GAP

    for i, (label, color, scenes, parent_fn) in enumerate(groups):
        if i > 0:
            cursor_y -= SECTION_GAP
        header_rect = (content_x, cursor_y - SECTION_HEADER_HEIGHT,
                       content_w, SECTION_HEADER_HEIGHT)
        entries.append(('header', label, color, header_rect))
        cursor_y -= SECTION_HEADER_HEIGHT

        for s in scenes:
            row_rect = (content_x, cursor_y - ROW_HEIGHT,
                        content_w, ROW_HEIGHT)
            parent = parent_fn(s) if parent_fn else None
            rename_rect = delete_rect = None
            if _is_room(s):
                by = (cursor_y - ROW_HEIGHT
                      + (ROW_HEIGHT - ACTION_BTN_SIZE) / 2.0)
                dx = (content_x + content_w
                      - ACTION_BTN_RIGHT_PAD - ACTION_BTN_SIZE)
                rnx = dx - ACTION_BTN_GAP - ACTION_BTN_SIZE
                delete_rect = (dx, by, ACTION_BTN_SIZE, ACTION_BTN_SIZE)
                rename_rect = (rnx, by, ACTION_BTN_SIZE, ACTION_BTN_SIZE)
            entries.append((
                'row', s, parent, color,
                s.name == current_scene_name, row_rect,
                rename_rect, delete_rect,
            ))
            cursor_y -= ROW_HEIGHT

    cursor_y -= NEW_ROOM_GAP
    new_room_rect = (content_x, cursor_y - NEW_ROOM_BTN_HEIGHT,
                     content_w, NEW_ROOM_BTN_HEIGHT)
    entries.append(('new_room', new_room_rect))

    return panel_rect, entries


# ---- Draw helpers -----------------------------------------------------------

def _draw_panel_header(shader, font_id, rect, current_name):
    rx, ry, rw, rh = rect
    blf.size(font_id, HEADER_FONT_SIZE)
    label = "CURRENT"
    label_w = blf.dimensions(font_id, label)[0]
    baseline = _vcenter_baseline(rect, font_id, ROW_FONT_SIZE)
    _draw_text(font_id, rx, baseline, HEADER_FONT_SIZE, HEADER_TEXT, label)
    _draw_text(font_id, rx + label_w + 8, baseline, ROW_FONT_SIZE,
               TEXT_PRIMARY, current_name)
    # separator line at the bottom of the header rect
    _draw_rect(shader, rx, ry, rw, 1, SEPARATOR_COLOR)


def _draw_row(shader, font_id, entry, mx, my):
    (_, scene, parent, color, is_current, rect,
     rename_rect, delete_rect) = entry
    rx, ry, rw, rh = rect
    hovered = _point_in_rect(mx, my, rect)

    if is_current:
        _draw_rect(shader, rx, ry, rw, rh, (*color, 0.14))
    elif hovered:
        _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)

    accent_alpha = 1.0 if is_current else (0.85 if hovered else 0.55)
    _draw_rect(shader, rx + ACCENT_LEFT_PAD, ry + 4,
               ACCENT_WIDTH, rh - 8, (*color, accent_alpha))

    text_x = rx + ROW_TEXT_LEFT_PAD
    name_color = TEXT_PRIMARY if is_current else TEXT_NORMAL
    baseline = _vcenter_baseline(rect, font_id, ROW_FONT_SIZE)

    if parent:
        blf.size(font_id, PARENT_FONT_SIZE)
        parent_w = blf.dimensions(font_id, parent)[0]
        sep = "  \u00b7  "
        sep_w = blf.dimensions(font_id, sep)[0]
        _draw_text(font_id, text_x, baseline,
                   PARENT_FONT_SIZE, TEXT_DIM, parent)
        _draw_text(font_id, text_x + parent_w, baseline,
                   PARENT_FONT_SIZE, TEXT_DIM, sep)
        _draw_text(font_id, text_x + parent_w + sep_w, baseline,
                   ROW_FONT_SIZE, name_color, scene.name)
    else:
        _draw_text(font_id, text_x, baseline,
                   ROW_FONT_SIZE, name_color, scene.name)

    if rename_rect is not None:
        r_hover = _point_in_rect(mx, my, rename_rect)
        brx, bry, brw, brh = rename_rect
        _draw_rect(shader, brx, bry, brw, brh,
                   ACTION_HOVER_BG if r_hover else ACTION_BG)
        _draw_rename_glyph(shader, rename_rect,
                           ACTION_GLYPH_HOVER if r_hover else ACTION_GLYPH)
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
    blf.size(font_id, ROW_FONT_SIZE)
    label_w = blf.dimensions(font_id, label)[0]
    plus_size = 10
    group_w = plus_size + 8 + label_w
    gx = rx + (rw - group_w) / 2.0
    cy = ry + rh / 2.0
    _draw_plus_glyph(shader, gx + plus_size / 2.0, cy, plus_size, TEXT_PRIMARY)
    baseline = _vcenter_baseline(rect, font_id, ROW_FONT_SIZE)
    _draw_text(font_id, gx + plus_size + 8, baseline,
               ROW_FONT_SIZE, TEXT_PRIMARY, label)


# ---- Draw callback ----------------------------------------------------------

def draw_scene_navigator(op):
    """GPU draw callback for the scene navigator overlay."""
    if op.region is None or op.entries is None:
        return
    # Only draw in the region this modal was bound to (skip other 3D views)
    if bpy.context.region != op.region:
        return

    mx, my = op.mouse_x, op.mouse_y

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    px, py, pw, ph = op.panel_rect
    _draw_rect(shader, px, py, pw, ph, PANEL_BG)
    _draw_rect_outline(shader, px, py, pw, ph, PANEL_BORDER)

    font_id = 0
    for entry in op.entries:
        kind = entry[0]
        if kind == 'panel_header':
            _draw_panel_header(shader, font_id, entry[2], entry[1])
        elif kind == 'header':
            _, label, color, rect = entry
            rx = rect[0]
            baseline = _vcenter_baseline(rect, font_id, HEADER_FONT_SIZE)
            _draw_text(font_id, rx, baseline, HEADER_FONT_SIZE,
                       HEADER_TEXT, label)
        elif kind == 'row':
            _draw_row(shader, font_id, entry, mx, my)
        elif kind == 'new_room':
            _draw_new_room_button(shader, font_id, entry[1], mx, my)

    gpu.state.blend_set('NONE')


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
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_x - self.region.x
            self.mouse_y = event.mouse_y - self.region.y
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx = event.mouse_x - self.region.x
            my = event.mouse_y - self.region.y
            for entry in self.entries or ():
                kind = entry[0]
                if kind == 'row':
                    (_, scene, _parent, _color, _is_current, rect,
                     rename_rect, delete_rect) = entry
                    if rename_rect and _point_in_rect(mx, my, rename_rect):
                        self._cleanup(context)
                        self._rename_room(context, scene)
                        return {'FINISHED'}
                    if delete_rect and _point_in_rect(mx, my, delete_rect):
                        self._cleanup(context)
                        self._delete_room(context, scene)
                        return {'FINISHED'}
                    if _point_in_rect(mx, my, rect):
                        self._cleanup(context)
                        if scene.name != context.scene.name:
                            self._switch_to(context, scene.name)
                        return {'FINISHED'}
                elif kind == 'new_room':
                    if _point_in_rect(mx, my, entry[1]):
                        self._cleanup(context)
                        self._create_room(context)
                        return {'FINISHED'}
            # nothing hit -- dismiss
            self._cleanup(context)
            return {'CANCELLED'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._cleanup(context)
            return {'CANCELLED'}

        # Swallow everything else so it doesn't leak to the viewport
        return {'RUNNING_MODAL'}


# ---- Registration -----------------------------------------------------------

classes = (
    home_builder_OT_scene_navigator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
