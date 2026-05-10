"""
Scene Navigator — GPU-drawn quick scene picker for Home Builder 5.

A modal overlay anchored to the top-center
of the active region. Lists all project scenes grouped by Rooms / Layout
Views / Details, with the parent room shown for each layout view (resolved
via SOURCE_WALL.users_scene). Click a row to switch scenes, click outside
the panel or press Esc / RMB to dismiss.
"""

import bpy
import gpu
import blf
from gpu_extras.batch import batch_for_shader


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


# ---- Layout computation -----------------------------------------------------

def _get_visible_window_bounds(area):
    """Return (x_min, x_max, y_min, y_max) of the WINDOW region's *visible*
    rectangle in WINDOW-local pixel coords — i.e. the area not covered by
    overlapping toolbar / N-panel / header / asset-shelf regions.

    With "Region Overlap" enabled (Blender's default), the WINDOW region
    extends underneath those overlays. POST_PIXEL handlers draw before the
    overlays composite on top, so anything we draw at the raw edges of
    WINDOW gets hidden. This helper returns the bounds we should respect."""
    if area is None:
        return (0, 0, 0, 0)

    win = None
    overlays = []
    for r in area.regions:
        if r.type == 'WINDOW':
            win = r
        elif r.type in {'TOOLS', 'UI', 'HEADER', 'TOOL_HEADER',
                        'ASSET_SHELF', 'ASSET_SHELF_HEADER'}:
            if r.width > 1 and r.height > 1:
                overlays.append(r)
    if win is None:
        return (0, 0, 0, 0)

    x_min, x_max = 0, win.width
    y_min, y_max = 0, win.height

    win_mid_y = win.height / 2.0

    for r in overlays:
        local_x  = r.x - win.x
        local_y  = r.y - win.y
        local_x2 = local_x + r.width
        local_y2 = local_y + r.height

        if r.type == 'TOOLS' and local_x <= 0 < local_x2:
            x_min = max(x_min, local_x2)
        elif r.type == 'UI' and local_x < win.width <= local_x2:
            x_max = min(x_max, local_x)
        elif r.type in {'HEADER', 'TOOL_HEADER', 'ASSET_SHELF_HEADER'}:
            # Classify header as top vs bottom by which half its center sits in.
            # Catches stacked headers (e.g. main HEADER + TOOL_HEADER) where one
            # is inside WINDOW rather than spanning its top edge.
            center_y = (local_y + local_y2) / 2.0
            if center_y > win_mid_y:
                y_max = min(y_max, local_y)
            else:
                y_min = max(y_min, local_y2)
        elif r.type == 'ASSET_SHELF':
            # Asset shelf is typically at the bottom
            if (local_y + local_y2) / 2.0 < win_mid_y:
                y_min = max(y_min, local_y2)

    return (x_min, x_max, y_min, y_max)


def _build_layout(region, area, current_scene_name):
    """Compute panel rect + entry rects from current region size and scenes.

    Returns (panel_rect, entries) where:
      panel_rect = (x, y, w, h) in region pixel space (y is bottom edge)
      entries    = list of tuples:
        ('header', label, color, rect)
        ('row', scene, parent_name_or_None, color, is_current_bool, rect)
    """
    groups = _collect_groups()

    # Total content height
    content_h = 0
    for i, (_, _, scenes, _) in enumerate(groups):
        if i > 0:
            content_h += SECTION_GAP
        content_h += SECTION_HEADER_HEIGHT
        content_h += ROW_HEIGHT * len(scenes)

    panel_w = PANEL_WIDTH
    panel_h = content_h + PANEL_PADDING_Y * 2

    x_min, x_max, y_min, y_max = _get_visible_window_bounds(area)
    visible_w = max(x_max - x_min, panel_w)

    # Center horizontally within the visible window area; anchor to visible top
    panel_x = x_min + (visible_w - panel_w) / 2.0
    panel_top = y_max - PANEL_TOP_MARGIN
    panel_y = panel_top - panel_h

    panel_rect = (panel_x, panel_y, panel_w, panel_h)
    entries = []

    cursor_y = panel_top - PANEL_PADDING_Y
    for i, (label, color, scenes, parent_fn) in enumerate(groups):
        if i > 0:
            cursor_y -= SECTION_GAP

        header_rect = (
            panel_x + PANEL_PADDING_X,
            cursor_y - SECTION_HEADER_HEIGHT,
            panel_w - PANEL_PADDING_X * 2,
            SECTION_HEADER_HEIGHT,
        )
        entries.append(('header', label, color, header_rect))
        cursor_y -= SECTION_HEADER_HEIGHT

        for s in scenes:
            row_rect = (
                panel_x + PANEL_PADDING_X,
                cursor_y - ROW_HEIGHT,
                panel_w - PANEL_PADDING_X * 2,
                ROW_HEIGHT,
            )
            parent = parent_fn(s) if parent_fn else None
            entries.append((
                'row', s, parent, color,
                s.name == current_scene_name, row_rect,
            ))
            cursor_y -= ROW_HEIGHT

    return panel_rect, entries


def _point_in_rect(x, y, rect):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


# ---- GPU drawing primitives -------------------------------------------------

def _draw_rect(shader, x, y, w, h, color):
    shader.uniform_float("color", color)
    verts = [
        (x, y), (x + w, y), (x + w, y + h),
        (x, y), (x + w, y + h), (x, y + h),
    ]
    batch_for_shader(shader, 'TRIS', {"pos": verts}).draw(shader)


def _draw_rect_outline(shader, x, y, w, h, color):
    shader.uniform_float("color", color)
    verts = [
        (x, y), (x + w, y),
        (x + w, y), (x + w, y + h),
        (x + w, y + h), (x, y + h),
        (x, y + h), (x, y),
    ]
    batch_for_shader(shader, 'LINES', {"pos": verts}).draw(shader)


def _draw_text(font_id, x, y, size, color, text):
    blf.size(font_id, size)
    blf.color(font_id, *color)
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)


def _vcenter_baseline(rect, font_id, size):
    """Y baseline that vertically centers a line of text in `rect`."""
    rx, ry, rw, rh = rect
    blf.size(font_id, size)
    text_h = blf.dimensions(font_id, "Aj")[1]
    return ry + (rh - text_h) / 2.0


# ---- Draw callback ----------------------------------------------------------

def draw_scene_navigator(op):
    """GPU draw callback for the scene navigator overlay."""
    if op.region is None or op.entries is None:
        return
    # Only draw in the region this modal was bound to (skip other 3D views)
    if bpy.context.region != op.region:
        return

    panel_rect = op.panel_rect
    entries = op.entries
    mx, my = op.mouse_x, op.mouse_y

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    # Panel background + border
    px, py, pw, ph = panel_rect
    _draw_rect(shader, px, py, pw, ph, PANEL_BG)
    _draw_rect_outline(shader, px, py, pw, ph, PANEL_BORDER)

    font_id = 0

    for entry in entries:
        kind = entry[0]

        if kind == 'header':
            _, label, color, rect = entry
            rx, ry, rw, rh = rect
            baseline = _vcenter_baseline(rect, font_id, HEADER_FONT_SIZE)
            _draw_text(font_id, rx, baseline, HEADER_FONT_SIZE, HEADER_TEXT, label)

        elif kind == 'row':
            _, scene, parent, color, is_current, rect = entry
            rx, ry, rw, rh = rect
            hovered = _point_in_rect(mx, my, rect)

            # Row background
            if is_current:
                _draw_rect(shader, rx, ry, rw, rh, (*color, 0.14))
            elif hovered:
                _draw_rect(shader, rx, ry, rw, rh, ROW_HOVER_BG)

            # Color accent bar
            accent_alpha = 1.0 if is_current else (0.85 if hovered else 0.55)
            _draw_rect(
                shader,
                rx + ACCENT_LEFT_PAD, ry + 4,
                ACCENT_WIDTH, rh - 8,
                (*color, accent_alpha),
            )

            # Text
            text_x = rx + ROW_TEXT_LEFT_PAD
            name_color = TEXT_PRIMARY if is_current else TEXT_NORMAL

            if parent:
                # "Parent · Scene Name" with parent dim and slightly smaller
                baseline = _vcenter_baseline(rect, font_id, ROW_FONT_SIZE)
                blf.size(font_id, PARENT_FONT_SIZE)
                parent_text = parent
                parent_w = blf.dimensions(font_id, parent_text)[0]
                sep = "  ·  "
                sep_w = blf.dimensions(font_id, sep)[0]

                _draw_text(font_id, text_x, baseline,
                           PARENT_FONT_SIZE, TEXT_DIM, parent_text)
                _draw_text(font_id, text_x + parent_w, baseline,
                           PARENT_FONT_SIZE, TEXT_DIM, sep)
                _draw_text(font_id, text_x + parent_w + sep_w, baseline,
                           ROW_FONT_SIZE, name_color, scene.name)
            else:
                baseline = _vcenter_baseline(rect, font_id, ROW_FONT_SIZE)
                _draw_text(font_id, text_x, baseline,
                           ROW_FONT_SIZE, name_color, scene.name)

    gpu.state.blend_set('NONE')


# ---- Modal operator ---------------------------------------------------------

class home_builder_OT_scene_navigator(bpy.types.Operator):
    bl_idname = "home_builder.scene_navigator"
    bl_label = "Scene Navigator"
    bl_description = "Quick switch between rooms, layout views, and details"

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
        # Convert absolute mouse coords into WINDOW-local for hit testing
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
            self.region, self.area, current
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

    def modal(self, context, event):
        if event.type == 'INBETWEEN_MOUSEMOVE':
            return {'RUNNING_MODAL'}

        if event.type == 'MOUSEMOVE':
            self.mouse_x = event.mouse_x - self.region.x
            self.mouse_y = event.mouse_y - self.region.y
            if context.area:
                context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Left click — switch on row hit, otherwise dismiss
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mx = event.mouse_x - self.region.x
            my = event.mouse_y - self.region.y
            for entry in self.entries or ():
                if entry[0] == 'row':
                    _, scene, _parent, _color, _is_current, rect = entry
                    if _point_in_rect(mx, my, rect):
                        self._cleanup(context)
                        if scene.name != context.scene.name:
                            self._switch_to(context, scene.name)
                        return {'FINISHED'}
            self._cleanup(context)
            return {'CANCELLED'}

        # ESC / right-click cancels
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
