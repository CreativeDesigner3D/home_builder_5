"""STYLES tab for the viewport panel -- the Face Frame library's Options.

The Options tab holds seven sections, and they are two different shapes:

* **Lists** -- Cabinet Styles and Door & Drawer Front Styles are named
  collections you pick from, add to and assign. A GPU panel is good at
  those: rows, hover, a click that means something.
* **Forms** -- Finished Ends, Pulls, Drawer Boxes, Countertops and
  Molding are property sheets: enums, unit fields, checkboxes. A GPU
  panel is *bad* at those. Reimplementing a slider means reimplementing
  drag, type-in, unit parsing, tooltips and undo, and getting all five
  slightly wrong.

So the forms are not reimplemented. Each is a row that opens a native
popup which calls the sidebar's own ``draw_*_ui(layout, context)``
method -- the identical UI, with every property behaving exactly as it
does in the sidebar, and no second copy to maintain. Those methods
already take a layout, so this costs nothing.

Cabinet Styles is drawn here as a real list because it is the one you
reach for mid-design: pick a style, assign it to what is selected.
"""

import bpy

from ..hb_gpu_draw import (
    draw_rect,
    draw_rects,
    draw_text,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    ScrollList,
    scale,
    text_width,
    fit_text,
    draw_centered_text,
    paint_button,
    glyph_plus,
    glyph_chevron,
)

PREFERRED_WIDTH = 300       # unscaled

# ---- Layout (unscaled px) --------------------------------------------------
ROW_H = 22
ROW_GAP = 2
SECTION_H = 18
GROUP_GAP = 8
BTN = 18
PAD = 4
FONT = 10
ACCENT_W = 3
GEAR = 18           # the per-style settings button on a row

# Commands that act on the active style. Drawn as buttons rather than
# hidden in a popup: these are the things you DO with a style, and the
# painting ones especially want to be one click from the list.
ACTIONS = (
    (("Assign", "hb_face_frame.assign_style_to_selected_cabinets", None, None),
     ("Paint", "hb_face_frame.paint_assign_cabinet_style", None, None),
     ("Update", "hb_face_frame.update_cabinets_from_style", None, None)),
    # Part paint stamps the style's finish or interior onto one part;
    # Reset returns it to the material its role implies.
    (("Finish", "hb_face_frame.paint_part_material", "brush", "FINISH"),
     ("Interior", "hb_face_frame.paint_part_material", "brush", "INTERIOR"),
     ("Reset", "hb_face_frame.paint_part_material", "brush", "RESET")),
)

# The five form-shaped sections, as (label, draw-method name).
FORM_SECTIONS = (
    ("Door & Drawer Front Styles", 'draw_door_styles_ui'),
    ("Finished Ends and Backs", 'draw_finished_ends_ui'),
    ("Pulls", 'draw_pulls_ui'),
    ("Drawer Boxes", 'draw_drawer_box_ui'),
    ("Countertops", 'draw_countertop_ui'),
    ("Molding", 'draw_molding_ui'),
)

_list = ScrollList(bar_width=4, bar_pad=4, min_rows=3)


# ---- Data ------------------------------------------------------------------

def _style_props(context):
    """The project-global style pool (it lives on the main scene)."""
    try:
        from ..product_libraries.face_frame.props_hb_face_frame import (
            get_style_props)
        return get_style_props(context)
    except Exception:
        return None


def cabinet_styles(context):
    sp = _style_props(context)
    return list(getattr(sp, 'cabinet_styles', ()) or ()) if sp else []


def active_style_index(context):
    sp = _style_props(context)
    return int(getattr(sp, 'active_cabinet_style_index', -1) or 0) if sp else -1


# ---- Provider interface ----------------------------------------------------

def build(rect, context):
    """Rows inside `rect`. Entries:

        ('styles_head', label, rect)
        ('style_row', index, name, rect, is_active)
        ('styles_add', rect)
        ('form_row', label, method_name, rect)
        ('styles_clip', clip_rect, track, thumb)
    """
    s = scale()
    x, bottom, w, h = rect
    row_h = ROW_H * s
    sect_h = SECTION_H * s
    gap = ROW_GAP * s

    styles = cabinet_styles(context)
    active = active_style_index(context)

    blocks = []
    blocks.append(('head', "Cabinet Styles"))
    for i, style in enumerate(styles):
        blocks.append(('style', (i, style.name, i == active)))
    blocks.append(('add', None))
    for row in ACTIONS:
        blocks.append(('actions', row))
    blocks.append(('gap', None))
    blocks.append(('head', "Options"))
    for label, method in FORM_SECTIONS:
        blocks.append(('form', (label, method)))

    def _h(block):
        kind = block[0]
        if kind == 'head':
            return sect_h
        if kind == 'gap':
            return GROUP_GAP * s
        return row_h + gap

    content_h = sum(_h(b) for b in blocks)
    list_h, _scrollable, reserve = _list.measure(content_h, h, row_h)
    _list.clamp(content_h, list_h)
    top = bottom + h
    track, thumb = _list.bar_rects(x, w, top, list_h, content_h, row_h)
    row_w = w - reserve

    entries = [('styles_clip', (x, top - list_h, w, list_h), track, thumb)]
    for block, block_top, _bb in _list.visible(blocks, top, top - list_h, _h):
        kind, payload = block
        if kind == 'gap':
            continue
        if kind == 'head':
            entries.append(('styles_head', payload,
                            (x, block_top - sect_h, row_w, sect_h)))
        elif kind == 'style':
            i, name, is_active = payload
            rect = (x, block_top - row_h, row_w, row_h)
            gear = GEAR * s
            gear_rect = (x + row_w - gear - 2 * s,
                         block_top - row_h + (row_h - gear) / 2.0, gear, gear)
            entries.append(('style_row', i, name, rect, is_active,
                            gear_rect))
        elif kind == 'add':
            entries.append(('styles_add',
                            (x, block_top - row_h, row_w, row_h)))
        elif kind == 'actions':
            n = len(payload)
            bw = (row_w - gap * (n - 1)) / n
            for j, (label, op_id, prop, value) in enumerate(payload):
                entries.append((
                    'action_btn', label, op_id, prop, value,
                    (x + j * (bw + gap), block_top - row_h, bw, row_h)))
        elif kind == 'form':
            label, method = payload
            entries.append(('form_row', label, method,
                            (x, block_top - row_h, row_w, row_h)))
    return entries


def _clip(entries):
    for entry in entries or ():
        if entry[0] == 'styles_clip':
            return entry
    return None


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

    # scissor_set only sets the BOX; the test has to be switched on
    # or the box is ignored and rows draw outside the panel.
    prev = gpu.state.scissor_get()
    clipped = clip is not None
    if clipped:
        cx, cy, cw, ch = clip[1]
        gpu.state.scissor_test_set(True)
        gpu.state.scissor_set(int(prev[0] + cx), int(prev[1] + cy),
                              max(int(cw), 0), max(int(ch), 0))
    try:
        for entry in entries:
            kind = entry[0]
            if kind == 'styles_head':
                _, label, rect = entry
                rx, ry, rw, rh = rect
                draw_text(font_id, rx, ry + rh * 0.3, FONT * s,
                          Theme.TEXT_HEADER, label.upper())
                draw_rects(shader, [(rx, ry, rw, 1 * s)], Theme.SEPARATOR)
            elif kind == 'style_row':
                _, _i, name, rect, is_active, gear_rect = entry
                hovered = point_in_rect(mx, my, rect)
                rx, ry, rw, rh = rect
                if hovered:
                    draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
                if is_active:
                    draw_rects(shader, [(rx, ry + 2 * s, ACCENT_W * s,
                                         rh - 4 * s)], Theme.ACCENT_BG)
                draw_text(font_id, rx + (ACCENT_W + 8) * s,
                          ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY if is_active
                          else Theme.TEXT_NORMAL,
                          fit_text(font_id, FONT * s, name,
                                   rw - GEAR * s - 16 * s))
                # Settings glyph: three bars, matching the library's.
                gx, gy, gw, gh = gear_rect
                g_hot = point_in_rect(mx, my, gear_rect)
                if g_hot:
                    paint_button(shader, gear_rect, hovered=True)
                for k in range(3):
                    draw_rects(shader, [(gx + 4 * s,
                                         gy + gh * (0.32 + k * 0.18),
                                         gw - 8 * s, 1.4 * s)],
                               Theme.GLYPH_HOVER if g_hot else Theme.GLYPH)
            elif kind == 'styles_add':
                _, rect = entry
                hovered = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hovered)
                rx, ry, rw, rh = rect
                glyph_plus(shader, rx + 12 * s, ry + rh / 2.0, 8 * s,
                           Theme.GLYPH)
                draw_text(font_id, rx + 24 * s, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_NORMAL, "New Cabinet Style")
            elif kind == 'action_btn':
                _, label, _op, _prop, _val, rect = entry
                hovered = point_in_rect(mx, my, rect)
                paint_button(shader, rect, hovered=hovered)
                draw_centered_text(font_id, rect, FONT * s,
                                   Theme.TEXT_PRIMARY if hovered
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
            gpu.state.scissor_set(*prev)
            gpu.state.scissor_test_set(False)
    gpu.state.blend_set('NONE')


def hit(context, mx, my, entries):
    clip = _clip(entries)
    if clip is not None and not point_in_rect(mx, my, clip[1]):
        return False
    for entry in entries:
        kind = entry[0]
        if kind == 'style_row':
            # Gear first: it sits inside the row, so a hit there must
            # not also re-activate the style underneath it.
            if point_in_rect(mx, my, entry[5]):
                bpy.ops.home_builder.cabinet_style_settings(
                    'INVOKE_DEFAULT', index=entry[1])
                return True
            if point_in_rect(mx, my, entry[3]):
                sp = _style_props(context)
                if sp is not None:
                    sp.active_cabinet_style_index = entry[1]
                _tag()
                return True
        if kind == 'styles_add' and point_in_rect(mx, my, entry[1]):
            try:
                bpy.ops.hb_face_frame.add_cabinet_style()
            except Exception:
                pass
            _tag()
            return True
        if kind == 'action_btn' and point_in_rect(mx, my, entry[5]):
            mod, name = entry[2].split('.', 1)
            kwargs = {entry[3]: entry[4]} if entry[3] else {}
            try:
                getattr(getattr(bpy.ops, mod), name)('INVOKE_DEFAULT',
                                                     **kwargs)
            except Exception as ex:
                print('Home Builder: %s failed: %s' % (entry[2], ex))
            _tag()
            return True
        if kind == 'form_row' and point_in_rect(mx, my, entry[3]):
            bpy.ops.home_builder.style_options_popup(
                'INVOKE_DEFAULT', section=entry[2], title=entry[1])
            return True
    return False


def scroll(mx, my, entries, rows):
    clip = _clip(entries)
    if clip is None or not point_in_rect(mx, my, clip[1]):
        return False
    _list.scroll_by(rows, ROW_H * scale())
    _tag()
    return True


def _tag():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


# ---- The popup that reuses the sidebar's own UI ----------------------------

class home_builder_OT_style_options_popup(bpy.types.Operator):
    """Open one of the Face Frame library's Options sections"""
    bl_idname = "home_builder.style_options_popup"
    bl_label = "Style Options"

    section: bpy.props.StringProperty()  # type: ignore
    title: bpy.props.StringProperty()  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.title)
        props = getattr(context.scene, 'hb_face_frame', None)
        method = getattr(props, self.section, None) if props else None
        if method is None:
            layout.label(text="This section is unavailable.", icon='ERROR')
            return
        # The sidebar's own draw method, called verbatim. Every property
        # behaves exactly as it does there, because it IS there.
        method(layout, context)

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_cabinet_style_settings(bpy.types.Operator):
    """Settings for this cabinet style: name, wood, finish, overlay,
    fronts and edge profiles"""
    bl_idname = "home_builder.cabinet_style_settings"
    bl_label = "Cabinet Style"

    index: bpy.props.IntProperty(default=-1)  # type: ignore

    def _style(self, context):
        sp = _style_props(context)
        styles = getattr(sp, 'cabinet_styles', None) if sp else None
        if not styles:
            return None
        i = self.index if 0 <= self.index < len(styles) else 0
        return styles[i]

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        style = self._style(context)
        if style is None:
            layout.label(text="No cabinet styles defined.", icon='INFO')
            return
        # The sidebar's own per-style form, verbatim. It opens with the
        # Style Name field, so this is also how a style gets renamed.
        style.draw_cabinet_style_ui(layout, context)

    def execute(self, context):
        return {'FINISHED'}


classes = (home_builder_OT_style_options_popup,
           home_builder_OT_cabinet_style_settings,)


def register():
    import sys
    for cls in classes:
        bpy.utils.register_class(cls)
    from . import scene_navigator
    scene_navigator.register_provider(scene_navigator.TAB_STYLES,
                                      sys.modules[__name__])


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
