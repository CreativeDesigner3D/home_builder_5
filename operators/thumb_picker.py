"""A thumbnail picker for the viewport panel.

A field whose choices are pictures -- the handles -- is picked from a
grid of them, not a list of their names. Clicking the field opens this
picker: a panel of tiles that hangs beside the tool strip, to the right
of the OPTIONS panel, for exactly as long as it takes to pick one. A
click on a tile sets the field and closes it; a click anywhere else,
Esc or right-click closes it with nothing changed.

It is a modal only for the picker's lifetime, on purpose: Blender skips
autosave while a modal runs, so the picker must never outlive the
choice. The tiles are painted by a POST_PIXEL handler the modal adds
and removes.

The textures are decoded once per picture and kept for the session,
shared with the panel that shows the current pick beside its field --
one cache, so opening the picker costs nothing the second time.
"""

import os

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..hb_gpu_draw import (
    get_visible_window_bounds,
    draw_rect,
    draw_rect_outline,
    draw_text,
    point_in_rect,
)
from ..hb_gpu_ui import (
    Theme,
    begin_clip,
    end_clip,
    scale,
    fit_text,
    paint_frame,
    paint_button,
    draw_centered_text,
)

# ---- Layout (unscaled px) ----------------------------------------------------
TILE = 72           # picture square
LABEL_H = 14        # the name under it
TILE_GAP = 6
COLS = 4
PAD = 8
HEADER_H = 20
FONT = 10
GAP_FROM_STRIP = 10   # between the tool strip and the picker
THUMB_PX = 128        # decoded picture size; the tiles never draw bigger

# ---- Texture cache ------------------------------------------------------------

_textures = {}      # path -> GPUTexture or None (None = failed / missing)


def texture(path):
    """The decoded picture for `path`, loading it on first use, or None
    when there is no picture. Safe to call from a draw handler only
    when the path is already cached -- decode from the modal / the
    panel's build step, not from paint."""
    if not path:
        return None
    if path in _textures:
        return _textures[path]
    _textures[path] = _load(path)
    return _textures[path]


def _load(path):
    if not os.path.exists(path):
        return None
    img = None
    try:
        img = bpy.data.images.load(path, check_existing=False)
        # Display-referred PNGs: Non-Color keeps the bytes as authored so
        # a POST_PIXEL draw shows them without a second colour transform
        # (the library grid learned this the hard way).
        try:
            img.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass
        img.scale(THUMB_PX, THUMB_PX)
        return gpu.texture.from_image(img)
    except Exception:
        return None
    finally:
        if img is not None:
            try:
                bpy.data.images.remove(img)
            except Exception:
                pass


def drop_textures():
    _textures.clear()


def draw_texture(tex, rect):
    shader = gpu.shader.from_builtin('IMAGE')
    x, y, w, h = rect
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {"pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
         "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1))})
    shader.bind()
    shader.uniform_sampler("image", tex)
    batch.draw(shader)


# ---- Picker state -------------------------------------------------------------

_state = None
# {'target': (id_data, path, prop), 'items': [(ident, label, png)],
#  'title': str, 'current': ident, 'scroll': float, 'mouse': (x, y)}


def _target_owner():
    if _state is None:
        return None
    id_data, path, _prop = _state['target']
    try:
        return id_data.path_resolve(path)
    except Exception:
        return None


def open_picker(context, owner, prop, items, title=""):
    """Show the picker for `prop` on `owner`. `items` are
    (identifier, label, picture path or None)."""
    global _state
    try:
        target = (owner.id_data, owner.path_from_id(), prop)
    except Exception as ex:
        print('Home Builder: cannot open picker for %s: %s' % (prop, ex))
        return
    for _ident, _label, png in items:
        texture(png)       # decode now, outside the draw handler
    _state = {
        'target': target,
        'items': list(items),
        'title': title,
        'current': getattr(owner, prop, None),
        'scroll': 0.0,
        'mouse': (-1.0, -1.0),
    }
    bpy.ops.home_builder.thumb_picker('INVOKE_DEFAULT')


def is_open():
    return _state is not None


# ---- Geometry -------------------------------------------------------------------

def _strip_right_edge(context, area):
    """Where the tool strip ends: the picker hangs just past it. Falls
    back to the pinned panel's edge, then the region's left margin."""
    s = scale()
    right = None
    try:
        from . import room_palette
        rows = room_palette.compute_layout(area)
        if rows:
            right = max(r[2][0] + r[2][2] for r in rows)
    except Exception:
        right = None
    if right is None:
        try:
            from . import viewport_hud
            panel = viewport_hud.pinned_panel_rect(context, area)
            if panel is not None:
                right = panel[0] + panel[2]
        except Exception:
            right = None
    if right is None:
        right = get_visible_window_bounds(area)[0] + 8 * s
    return right


def _layout(context, area):
    """(panel_rect, header_rect, tiles) with tiles as
    [(index, tile_rect, img_rect, label_rect)] for what is on screen."""
    if _state is None:
        return None
    s = scale()
    x_min, x_max, y_min, y_max = get_visible_window_bounds(area)
    tile = TILE * s
    label_h = LABEL_H * s
    gap = TILE_GAP * s
    pad = PAD * s
    cols = COLS
    items = _state['items']
    rows = (len(items) + cols - 1) // cols
    cell_h = tile + label_h + gap
    content_h = rows * cell_h - gap
    header_h = HEADER_H * s
    width = pad * 2 + cols * tile + (cols - 1) * gap

    try:
        from . import viewport_hud
        _ax, top = viewport_hud.nav_anchor(context, area)
    except Exception:
        top = -1.0
    if top < 0:
        top = y_max - 12 * s
    x = _strip_right_edge(context, area) + GAP_FROM_STRIP * s
    x = min(x, x_max - width - 4 * s)
    max_h = top - y_min - 12 * s
    # The gap is the one under the header, which the grid starts below.
    height = min(pad * 2 + header_h + gap + content_h, max_h)
    panel = (x, top - height, width, height)

    header = (x + pad, top - pad - header_h, width - pad * 2, header_h)
    grid_top = header[1] - gap
    grid_bottom = panel[1] + pad
    list_h = grid_top - grid_bottom
    max_scroll = max(content_h - list_h, 0.0)
    _state['scroll'] = min(max(_state['scroll'], 0.0), max_scroll)

    tiles = []
    for i, _item in enumerate(items):
        r, c = divmod(i, cols)
        tx = x + pad + c * (tile + gap)
        cell_top = grid_top + _state['scroll'] - r * cell_h
        cell_bottom = cell_top - tile - label_h
        if cell_top < grid_bottom or cell_bottom > grid_top:
            continue
        tile_rect = (tx, cell_bottom, tile, tile + label_h)
        img_rect = (tx, cell_bottom + label_h, tile, tile)
        label_rect = (tx, cell_bottom, tile, label_h)
        tiles.append((i, tile_rect, img_rect, label_rect))
    return panel, header, tiles, (x + pad, grid_bottom, width - pad * 2, list_h)


# ---- Draw ---------------------------------------------------------------------

def _draw():
    if _state is None:
        return
    context = bpy.context
    area, region = context.area, context.region
    if area is None or area.type != 'VIEW_3D' or region is None \
            or region.type != 'WINDOW':
        return
    layout = _layout(context, area)
    if layout is None:
        return
    panel, header, tiles, clip = layout
    s = scale()
    mx, my = _state['mouse']
    font_id = 0

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    paint_frame(shader, panel)
    hx, hy, hw, hh = header
    draw_text(font_id, hx, hy + hh * 0.3, FONT * s, Theme.TEXT_HEADER,
              (_state['title'] or "Pick").upper())
    draw_rect(shader, hx, hy, hw, 1 * s, Theme.SEPARATOR)

    # Scissor the grid so a scrolled row cuts off under the header.
    prev = begin_clip(clip)
    try:
        items = _state['items']
        for i, tile_rect, img_rect, label_rect in tiles:
            ident, label, png = items[i]
            hovered = point_in_rect(mx, my, tile_rect)
            current = ident == _state['current']
            paint_button(shader, tile_rect, hovered=hovered, active=current)
            tex = _textures.get(png) if png else None
            if tex is not None:
                gpu.state.blend_set('ALPHA')
                ix, iy, iw, ih = img_rect
                inset = 4 * s
                draw_texture(tex, (ix + inset, iy + inset,
                                   iw - 2 * inset, ih - 2 * inset))
                shader.bind()
            else:
                # No picture (None / Custom): the name is the tile, and
                # is not repeated underneath.
                draw_centered_text(font_id, tile_rect, FONT * s,
                                   Theme.TEXT_PRIMARY if (hovered or current)
                                   else Theme.TEXT_NORMAL,
                                   fit_text(font_id, FONT * s, label,
                                            tile_rect[2] - 6 * s))
                continue
            draw_centered_text(font_id, label_rect, (FONT - 1) * s,
                               Theme.TEXT_PRIMARY if (hovered or current)
                               else Theme.TEXT_DIM,
                               fit_text(font_id, (FONT - 1) * s, label,
                                        label_rect[2] - 4 * s))
    finally:
        end_clip(prev)
    gpu.state.blend_set('NONE')


# ---- Modal ----------------------------------------------------------------------

class home_builder_OT_thumb_picker(bpy.types.Operator):
    """Pick from a grid of pictures"""
    bl_idname = "home_builder.thumb_picker"
    bl_label = "Pick"
    bl_options = {'INTERNAL', 'UNDO'}

    _handle = None

    def invoke(self, context, event):
        global _state
        if _state is None or context.area is None:
            return {'CANCELLED'}
        self._area = context.area
        # The press that opened the picker is still down; its release
        # must not count as a click on whatever tile lands under it.
        self._armed = event.value == 'RELEASE'
        _state['mouse'] = (event.mouse_region_x, event.mouse_region_y)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw, (), 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        self._area.tag_redraw()
        return {'RUNNING_MODAL'}

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
        try:
            self._area.tag_redraw()
        except Exception:
            pass

    def modal(self, context, event):
        if _state is None:
            self._close()
            return {'CANCELLED'}
        mx, my = event.mouse_region_x, event.mouse_region_y
        _state['mouse'] = (mx, my)

        if event.type == 'MOUSEMOVE':
            self._area.tag_redraw()
            return {'RUNNING_MODAL'}

        layout = _layout(context, self._area)
        panel = layout[0] if layout else None

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if panel is not None and point_in_rect(mx, my, panel):
                step = (TILE + LABEL_H + TILE_GAP) * scale()
                _state['scroll'] += (-step if event.type == 'WHEELUPMOUSE'
                                     else step)
                self._area.tag_redraw()
                return {'RUNNING_MODAL'}
            return {'PASS_THROUGH'}

        if event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self._close()
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'RELEASE':
                self._armed = True
                return {'RUNNING_MODAL'}
            if not self._armed:
                return {'RUNNING_MODAL'}
            if layout is not None:
                _panel, _header, tiles, _clip = layout
                for i, tile_rect, _img, _label in tiles:
                    if point_in_rect(mx, my, tile_rect):
                        owner = _target_owner()
                        prop = _state['target'][2]
                        ident = _state['items'][i][0]
                        self._close()
                        if owner is not None:
                            try:
                                setattr(owner, prop, ident)
                            except Exception as ex:
                                self.report({'WARNING'}, str(ex))
                                return {'CANCELLED'}
                        _tag()
                        return {'FINISHED'}
            if panel is not None and point_in_rect(mx, my, panel):
                return {'RUNNING_MODAL'}
            # Clicked away: close, and let the press go on to whatever
            # it landed on -- the panel, the viewport.
            self._close()
            return {'CANCELLED', 'PASS_THROUGH'}

        # Everything else stays with the picker, so a stray key does
        # not fire a viewport shortcut under it.
        return {'RUNNING_MODAL'}


def _tag():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


classes = (home_builder_OT_thumb_picker,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _state
    _state = None
    drop_textures()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
