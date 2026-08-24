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
    begin_clip,
    end_clip,
    ScrollList,
    scale,
    text_width,
    fit_text,
    draw_centered_text,
    paint_button,
    glyph_plus,
    glyph_chevron,
    InlineEdit,
)

PREFERRED_WIDTH = 300       # unscaled

# ---- Layout (unscaled px) --------------------------------------------------
ROW_H = 22
ROW_GAP = 2
SECTION_H = 20          # tall enough to carry a button on the right
NEW_BTN_H = 16          # the + NEW chip inside a section header
NEW_BTN_PAD = 6         # its gap from the header text and the edge
GROUP_GAP = 8
BTN = 18
PAD = 4
FONT = 10
ACCENT_W = 3
GEAR = 18           # the per-style settings button on a row
PLUS_SPAN = 8       # full width of the plus mark, not half
PLUS_GAP = 4        # plus mark to the word NEW

# Commands that act on the active style. Drawn as buttons rather than
# hidden in a popup: these are the things you DO with a style, and the
# painting ones want to be one click from the list.
#
# Three, not the sidebar's seven. Assign, Update and Reset stay in the
# sidebar, which still has all of them; the style's own settings are
# behind the menu glyph on its row, so a button for them here would be
# a second door onto the same thing. What is left is the three brushes,
# named for what each one paints: the whole cabinet, one part's finish,
# one part's interior.
ACTIONS = (
    (("Paint Cabinet", "hb_face_frame.paint_assign_cabinet_style",
      None, None),
     ("Paint Part", "hb_face_frame.paint_part_material", "brush", "FINISH"),
     ("Paint Interior", "hb_face_frame.paint_part_material",
      "brush", "INTERIOR")),
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
# Inline rename, keyed by style index -- the same field the scene
# navigator renames rooms with, so the two lists behave alike.
_edit = InlineEdit()


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

        ('styles_head', label, rect, add_rect)   add_rect None on most
        ('style_row', index, name, rect, is_active)
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
    # The header carries New rather than a full-width row of its own: it
    # is the one command that makes a list item, so it belongs to the
    # list's caption, not to the stack of commands that act on a style.
    blocks.append(('head', ("Cabinet Styles", True)))
    for i, style in enumerate(styles):
        blocks.append(('style', (i, style.name, i == active)))
    for row in ACTIONS:
        blocks.append(('actions', row))
    blocks.append(('gap', None))
    blocks.append(('head', ("Options", False)))
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
            label, with_add = payload
            head_rect = (x, block_top - sect_h, row_w, sect_h)
            add_rect = None
            if with_add:
                bw = (NEW_BTN_PAD * s + PLUS_SPAN * s + PLUS_GAP * s
                      + text_width(0, FONT * s, "NEW") + NEW_BTN_PAD * s)
                bh = NEW_BTN_H * s
                add_rect = (x + row_w - bw, block_top - sect_h + (sect_h - bh) / 2.0,
                            bw, bh)
            entries.append(('styles_head', label, head_rect, add_rect))
        elif kind == 'style':
            i, name, is_active = payload
            rect = (x, block_top - row_h, row_w, row_h)
            gear = GEAR * s
            gear_rect = (x + row_w - gear - 2 * s,
                         block_top - row_h + (row_h - gear) / 2.0, gear, gear)
            entries.append(('style_row', i, name, rect, is_active,
                            gear_rect))
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

    clipped = clip is not None
    prev = begin_clip(clip[1]) if clipped else None
    try:
        for entry in entries:
            kind = entry[0]
            if kind == 'styles_head':
                _, label, rect, add_rect = entry
                rx, ry, rw, rh = rect
                draw_text(font_id, rx, ry + rh * 0.32, FONT * s,
                          Theme.TEXT_HEADER, label.upper())
                # The rule stops short of the button rather than running
                # under it -- a line crossing a control reads as a
                # mistake.
                rule_w = rw if add_rect is None else add_rect[0] - rx - PAD * s
                draw_rects(shader, [(rx, ry, max(rule_w, 0.0), 1 * s)],
                           Theme.SEPARATOR)
                if add_rect is not None:
                    hot = point_in_rect(mx, my, add_rect)
                    paint_button(shader, add_rect, hovered=hot)
                    ax, ay, aw, ah = add_rect
                    # glyph_plus takes the FULL span, not a half -- half
                    # of it renders as a blob rather than a plus.
                    glyph_plus(shader,
                               ax + (NEW_BTN_PAD + PLUS_SPAN / 2.0) * s,
                               ay + ah / 2.0, PLUS_SPAN * s,
                               Theme.GLYPH_HOVER if hot else Theme.GLYPH)
                    draw_text(font_id,
                              ax + (NEW_BTN_PAD + PLUS_SPAN + PLUS_GAP) * s,
                              ay + ah * 0.26, FONT * s,
                              Theme.TEXT_PRIMARY if hot else Theme.TEXT_NORMAL,
                              "NEW")
            elif kind == 'style_row':
                _, _i, name, rect, is_active, gear_rect = entry
                hovered = point_in_rect(mx, my, rect)
                rx, ry, rw, rh = rect
                renaming = _edit.editing(_i)
                if hovered and not renaming:
                    draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
                if is_active:
                    draw_rects(shader, [(rx, ry + 2 * s, ACCENT_W * s,
                                         rh - 4 * s)], Theme.ACCENT_BG)
                text_x = rx + (ACCENT_W + 8) * s
                if renaming:
                    # The row becomes the field. A caret marks the end of
                    # the text so it reads as editable rather than
                    # selected -- the navigator's rename looks the same.
                    field_w = rw - GEAR * s - 12 * s - (text_x - rx)
                    draw_rects(shader, [(text_x - 3 * s, ry + 3 * s,
                                         field_w + 6 * s, rh - 6 * s)],
                               (0.0, 0.0, 0.0, 0.55))
                    shown = fit_text(font_id, FONT * s, _edit.text + "|",
                                     field_w)
                else:
                    shown = fit_text(font_id, FONT * s, name,
                                     rw - GEAR * s - 16 * s)
                draw_text(font_id, text_x, ry + rh * 0.28, FONT * s,
                          Theme.TEXT_PRIMARY if (is_active or renaming)
                          else Theme.TEXT_NORMAL, shown)
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
            end_clip(prev)
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
                index = entry[1]
                if sp is not None and sp.active_cabinet_style_index != index:
                    sp.active_cabinet_style_index = index
                elif sp is not None:
                    # Clicking the style you are already on renames it,
                    # the same second click that renames a room.
                    _edit.begin(index, entry[2])
                    bpy.ops.home_builder.style_rename('INVOKE_DEFAULT')
                _tag()
                return True
        if kind == 'styles_head' and entry[3] is not None:
            if point_in_rect(mx, my, entry[3]):
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


def commit_rename(context):
    """Apply the typed name to the style being edited.

    Assignment is the whole commit: the name property's update callback
    de-duplicates against the other styles AND re-tags every cabinet
    carrying the old STYLE_NAME, so an assigned cabinet keeps resolving
    after a rename.
    """
    index, name = _edit.take()
    if index is None or not name:
        return None
    styles = cabinet_styles(context)
    if not 0 <= index < len(styles):
        return None
    style = styles[index]
    if name != style.name:
        style.name = name
    return style


class home_builder_OT_style_rename(bpy.types.Operator):
    """Rename the cabinet style in place in the list.

    A modal only for as long as the user is typing -- it ends on Enter,
    Esc, or a click anywhere. What must never happen is a modal that
    outlives the interaction, because Blender skips autosave while one
    is live.
    """
    bl_idname = "home_builder.style_rename"
    bl_label = "Rename Cabinet Style"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return _edit.active

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        _tag()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        result = _edit.feed(event)
        if result == 'COMMIT':
            commit_rename(context)
            _tag()
            return {'FINISHED'}
        if result == 'CANCEL':
            _edit.cancel()
            _tag()
            return {'CANCELLED'}
        # A click anywhere ends the edit, committing what was typed --
        # what a field in a form does when it loses focus.
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'} and event.value == 'PRESS':
            commit_rename(context)
            _tag()
            return {'FINISHED'}
        _tag()
        return {'RUNNING_MODAL'}


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
        if 0 <= self.index < len(styles):
            return styles[self.index]
        # No usable index: the active style, which is the one the panel
        # is showing. Falling back to the first would open a different
        # style from the highlighted one whenever Show Settings is used.
        active = active_style_index(context)
        if not 0 <= active < len(styles):
            active = 0
        return styles[active]

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
           home_builder_OT_cabinet_style_settings,
           home_builder_OT_style_rename,)


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
