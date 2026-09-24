"""A larger editor window for one item of an Options pool.

The Options panel is narrow and lists one item's settings in a single
long column. An editor spec names what goes in a bigger window instead:
a header saying what the item is, its settings in sections picked from
tabs down the left, and the commands that act on it along the bottom.
The fields are the Options panel's own -- laid out, painted and hit by
the same code -- so a field behaves the same in either place.

Like the thumbnail picker it hangs beside the tool strip and is a modal
only while it is open (Blender skips autosave while a modal runs). Esc,
right-click, the close button or a click outside it closes it.

A catalog declares editors in OPTION_EDITORS:

    {key: {'owner':    fn(context) -> the item being edited, or None,
           'header':   fn(context, item) -> {'title', 'lines', 'swatch'},
           'sections': ((label, fields), ...),
           'footer':   ((label, operator[, prop, value]), ...)}}
"""

import bpy
import gpu

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    draw_rect,
    draw_rect_outline,
    draw_text,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    scale,
    fit_text,
    paint_frame,
    paint_button,
    draw_centered_text,
    glyph_delete,
)

# ---- Layout (unscaled px) ----------------------------------------------------
WIDTH = 580
MAX_H = 620
PAD = 10
HEADER_H = 46
TAB_W = 116
TAB_H = 24
TAB_GAP = 2
FOOTER_H = 24
CLOSE = 18
FONT = 10
GAP_FROM_STRIP = 10

_state = None       # {'key', 'section', 'mouse', 'list'} while open


def open_editor(context, key, section=0):
    """Open the editor the active library names `key`."""
    global _state
    spec = _spec(context, key)
    if spec is None or _owner(context, spec) is None:
        return False
    from . import options_panel
    if _state is not None:
        _state.update(key=key, section=section)
        _tag()
        return True
    _state = {'key': key, 'section': section, 'mouse': (0.0, 0.0),
              'list': options_panel.new_scroll_list()}
    bpy.ops.home_builder.style_editor('INVOKE_DEFAULT')
    return True


def is_open():
    return _state is not None


def _spec(context, key):
    from . import library_panel
    cat = library_panel.active_catalog(context)
    return dict(getattr(cat, 'OPTION_EDITORS', None) or {}).get(key) \
        if cat else None


def _owner(context, spec):
    try:
        return spec['owner'](context)
    except Exception:
        return None


# ---- Geometry -------------------------------------------------------------------

def _layout(context, area):
    """The window's rects, or None: panel, header, close, tabs, the
    fields' rect and the footer buttons."""
    if _state is None:
        return None
    spec = _spec(context, _state['key'])
    if spec is None:
        return None
    from .thumb_picker import _strip_right_edge
    s = scale()
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    pad = PAD * s
    width = WIDTH * s
    try:
        from . import viewport_hud
        _ax, top = viewport_hud.nav_anchor(context, area)
    except Exception:
        top = -1.0
    if top < 0:
        top = y_max - 12 * s
    x = _strip_right_edge(context, area) + GAP_FROM_STRIP * s
    x = max(x_min + 4 * s, min(x, x_max - width - 4 * s))
    height = min(MAX_H * s, top - y_min - 12 * s)
    panel = (x, top - height, width, height)

    header = (x + pad, top - pad - HEADER_H * s, width - 2 * pad,
              HEADER_H * s)
    close = (x + width - pad - CLOSE * s, top - pad - CLOSE * s,
             CLOSE * s, CLOSE * s)
    footer_y = panel[1] + pad
    body_top = header[1] - 8 * s
    body_bottom = footer_y + FOOTER_H * s + 8 * s

    tabs = []
    for i, (label, _fields) in enumerate(spec['sections']):
        ty = body_top - (i + 1) * TAB_H * s - i * TAB_GAP * s
        tabs.append((i, label, (x + pad, ty, TAB_W * s, TAB_H * s)))
    fx = x + pad + TAB_W * s + 12 * s
    fields = (fx, body_bottom, x + width - pad - fx, body_top - body_bottom)

    buttons = []
    footer = spec.get('footer', ())
    if footer:
        gap = 4 * s
        bw = (width - 2 * pad - gap * (len(footer) - 1)) / len(footer)
        for j, action in enumerate(footer):
            buttons.append((action, (x + pad + j * (bw + gap), footer_y,
                                     bw, FOOTER_H * s)))
    return {'panel': panel, 'header': header, 'close': close,
            'tabs': tabs, 'fields': fields, 'buttons': buttons,
            'spec': spec, 'body': (body_bottom, body_top)}


def _entries(context, lay):
    """The fields of the open section, laid out by the Options panel."""
    from . import options_panel
    spec = lay['spec']
    owner = _owner(context, spec)
    sections = spec['sections']
    if owner is None or not sections:
        return []
    i = min(max(_state['section'], 0), len(sections) - 1)
    fields = sections[i][1]
    return options_panel.build_page(
        lay['fields'], context,
        lambda ctx: options_panel.field_blocks(ctx, fields, owner),
        _state['list'])


# ---- Draw ---------------------------------------------------------------------

def _draw():
    if _state is None:
        return
    context = bpy.context
    area, region = context.area, context.region
    if area is None or area.type != 'VIEW_3D' or region is None \
            or region.type != 'WINDOW':
        return
    lay = _layout(context, area)
    if lay is None:
        return
    from . import options_panel
    s = scale()
    mx, my = _state['mouse']
    font_id = 0
    spec = lay['spec']
    owner = _owner(context, spec)

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    # Solid, not the panel's see-through wash: a window this size over
    # a busy model has to read on its own.
    paint_frame(shader, lay['panel'], bg=Theme.PANEL_BG[:3] + (1.0,))

    # Header: what is being edited.
    try:
        info = spec['header'](context, owner) or {} if owner else {}
    except Exception:
        info = {}
    hx, hy, hw, hh = lay['header']
    text_x = hx
    swatch = info.get('swatch')
    if swatch is not None:
        sw = hh - 10 * s
        draw_rect(shader, hx, hy + 5 * s, sw, sw,
                  (swatch[0], swatch[1], swatch[2], 1.0))
        draw_rect_outline(shader, hx, hy + 5 * s, sw, sw, Theme.BTN_BORDER)
        text_x += sw + 10 * s
    avail = lay['close'][0] - 8 * s - text_x
    draw_text(font_id, text_x, hy + hh - 16 * s, (FONT + 3) * s,
              Theme.TEXT_PRIMARY,
              fit_text(font_id, (FONT + 3) * s,
                       str(info.get('title') or ""), avail))
    for k, line in enumerate([str(x) for x in (info.get('lines') or ())
                              if x][:2]):
        draw_text(font_id, text_x, hy + hh - 30 * s - k * 13 * s, FONT * s,
                  Theme.TEXT_NORMAL if k == 0 else Theme.TEXT_HEADER,
                  fit_text(font_id, FONT * s, line, avail))
    c_hot = point_in_rect(mx, my, lay['close'])
    if c_hot:
        paint_button(shader, lay['close'], hovered=True)
    glyph_delete(shader, lay['close'],
                 Theme.GLYPH_HOVER if c_hot else Theme.GLYPH)
    draw_rect(shader, hx, hy - 4 * s, hw, 1 * s, Theme.SEPARATOR)

    # Section tabs.
    for i, label, rect in lay['tabs']:
        active = i == _state['section']
        hot = point_in_rect(mx, my, rect)
        if active:
            draw_rect(shader, *rect, Theme.BTN_HOVER_BG)
            draw_rect(shader, rect[0], rect[1] + 3 * s, 3 * s,
                      rect[3] - 6 * s, Theme.ACCENT_BG)
        elif hot:
            draw_rect(shader, *rect, Theme.ROW_HOVER_BG)
        draw_text(font_id, rect[0] + 12 * s, rect[1] + rect[3] * 0.3,
                  (FONT + 1) * s,
                  Theme.TEXT_PRIMARY if (active or hot) else Theme.TEXT_NORMAL,
                  fit_text(font_id, (FONT + 1) * s, label, rect[2] - 16 * s))
    fx = lay['fields'][0] - 6 * s
    body_bottom, body_top = lay['body']
    draw_rect(shader, fx, body_bottom, 1 * s, body_top - body_bottom,
              Theme.SEPARATOR)

    # Footer commands.
    for (label, *_rest), rect in lay['buttons']:
        hot = point_in_rect(mx, my, rect)
        paint_button(shader, rect, hovered=hot)
        draw_centered_text(font_id, rect, FONT * s,
                           Theme.TEXT_PRIMARY if hot else Theme.TEXT_NORMAL,
                           fit_text(font_id, FONT * s, label, rect[2] - 8 * s))

    # The section's fields, by the Options panel's own painter (which
    # also shows a cut name in full on hover).
    options_panel.paint(_entries(context, lay), mx, my)
    gpu.state.blend_set('NONE')


# ---- Modal ----------------------------------------------------------------------

class home_builder_OT_style_editor(bpy.types.Operator):
    """Edit a style in a larger window"""
    bl_idname = "home_builder.style_editor"
    bl_label = "Edit Style"
    bl_options = {'INTERNAL'}

    _handle = None

    def invoke(self, context, event):
        if _state is None or context.area is None:
            return {'CANCELLED'}
        self._area = context.area
        # The press that opened the window is still down; its release
        # must not land on whatever is under it.
        self._armed = event.value == 'RELEASE'
        _state['mouse'] = (event.mouse_region_x, event.mouse_region_y)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        _tag()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        self._close()

    def _close(self):
        global _state
        if self._handle is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle,
                                                          'WINDOW')
            except Exception:
                pass
            self._handle = None
        _state = None
        _tag()

    def modal(self, context, event):
        try:
            return self._modal(context, event)
        except Exception as ex:
            print("Home Builder: style editor closed: %s" % ex)
            self._close()
            return {'CANCELLED'}

    def _modal(self, context, event):
        from . import options_panel
        if _state is None:
            self._close()
            return {'CANCELLED'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        _state['mouse'] = (mx, my)
        lay = _layout(context, self._area)
        if lay is None or _owner(context, lay['spec']) is None:
            # The item went away (deleted, another library): nothing
            # left to edit.
            self._close()
            return {'CANCELLED', 'PASS_THROUGH'}
        panel = lay['panel']

        if event.type == 'MOUSEMOVE':
            _tag()
            return {'RUNNING_MODAL'}
        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if point_in_rect(mx, my, panel):
                rows = -2 if event.type == 'WHEELUPMOUSE' else 2
                options_panel.scroll_page(mx, my, _entries(context, lay),
                                          rows, _state['list'])
                _tag()
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}
        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._close()
            return {'CANCELLED'}
        # Undo and the other shortcuts still reach Blender.
        if event.ctrl or event.oskey:
            return {'PASS_THROUGH'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                self._armed = True
                return {'RUNNING_MODAL'}
            if event.value != 'PRESS' or not self._armed:
                return {'RUNNING_MODAL'}
            if point_in_rect(mx, my, lay['close']):
                self._close()
                return {'FINISHED'}
            for i, _label, rect in lay['tabs']:
                if point_in_rect(mx, my, rect):
                    if _state['section'] != i:
                        _state['section'] = i
                        _state['list'].offset = 0.0
                    _tag()
                    return {'RUNNING_MODAL'}
            for action, rect in lay['buttons']:
                if point_in_rect(mx, my, rect):
                    # A brush or a pick in the viewport: out of the way.
                    self._close()
                    label, op_id = action[0], action[1]
                    kwargs = ({action[2]: action[3]}
                              if len(action) > 3 and action[2] else {})
                    options_panel._run_on_release(op_id, kwargs)
                    return {'FINISHED'}
            entries = _entries(context, lay)
            # A picture that opens a style manager: that lives in the
            # Options panel, so this window steps aside for it.
            for entry in entries:
                if (entry[0] == 'picture_tile'
                        and point_in_rect(mx, my, entry[2])):
                    self._close()
                    options_panel.hit(context, mx, my, entries)
                    return {'FINISHED'}
            if options_panel.hit(context, mx, my, entries):
                _tag()
                return {'RUNNING_MODAL'}
            if point_in_rect(mx, my, panel):
                return {'RUNNING_MODAL'}
            # Clicked away: close, and let the press go on to whatever
            # it landed on.
            self._close()
            return {'CANCELLED', 'PASS_THROUGH'}

        # A stray key must not fire a viewport shortcut under the window.
        return {'RUNNING_MODAL'}


class home_builder_OT_style_editor_open(bpy.types.Operator):
    """Open this style in the larger editor"""
    bl_idname = "home_builder.style_editor_open"
    bl_label = "Edit Style"
    bl_options = {'INTERNAL'}

    key: bpy.props.StringProperty()  # type: ignore
    section: bpy.props.IntProperty(default=0)  # type: ignore

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        return ({'FINISHED'} if open_editor(context, self.key, self.section)
                else {'CANCELLED'})


def _tag():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


classes = (home_builder_OT_style_editor,
           home_builder_OT_style_editor_open)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _state
    _state = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
