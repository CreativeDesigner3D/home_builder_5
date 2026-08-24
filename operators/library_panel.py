"""GPU-drawn library browser for the 3D viewport.

A scrolling thumbnail grid of the face-frame product library, painted
down the right of the viewport, so placing a cabinet does not mean crossing to the sidebar and
back. Clicking a tile runs ``hb_face_frame.draw_cabinet`` -- the same operator
the sidebar's library buttons fire -- so there is no per-product logic
here and the sidebar keeps working unchanged.

Products come from ``library_catalog``, the same data the sidebar
renders, so the two browsers cannot drift. Category and search are this
panel's own (the sidebar has neither); both are buttons that open a
native popup, because a GPU panel is the wrong place to reimplement a
text field.

Thumbnails
----------
Preview ``icon_id`` values (what the sidebar draws) cannot be blitted
from a draw handler, so this uploads the PNGs itself. Measured costs
drove three decisions:

* **Upload downscaled.** A native 540px thumbnail costs ~1 MB of VRAM;
  at THUMB_PX it is ~144 KB, which keeps a 1000-item library well under
  150 MB instead of near a gigabyte.
* **Free the image immediately.** A GPUTexture owns its data, so the
  bpy.data.images entry can go the moment the upload is done -- the
  CPU-side cost drops to zero and nothing dangles if the datablock is
  removed later.
* **Load off the draw path.** Decoding a PNG costs ~4.6 ms and creating
  an image is a write to bpy.data, which must never happen inside a
  draw callback. The draw handler only RECORDS which thumbnails it
  wanted; a timer loads a few per tick and asks for a redraw, so the
  grid fills in progressively instead of stalling the viewport.

Drawing cost is ~0.04 ms per visible tile and flat in library size, so
the grid only ever paints the rows inside its clip rect.

Pattern, as with the other viewport chrome: a permanent POST_PIXEL draw
handler plus addon keymap entries that hit-test and pass every other
event through. NEVER a persistent modal operator -- Blender skips
autosave for as long as one is running.
"""

import sys
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ..hb_gpu_draw import (
    get_visible_window_bounds,
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
    glyph_chevron,
)
from ..product_libraries.face_frame import library_catalog

_ADDON_PKG = __package__.rsplit(".", 1)[0]

# ---- Thumbnails ------------------------------------------------------------
THUMB_PX = 192          # upload size; see the module docstring
LOADS_PER_TICK = 3      # ~4.6 ms each -- keeps a tick well under a frame
TICK_INTERVAL = 0.05

# ---- Layout (unscaled px) --------------------------------------------------
MARGIN = 12
PANEL_W = 244
# Tiles are SIZED FROM the panel, not fixed: a constant tile left
# whatever did not divide evenly as dead space down the right,
# and changing the column count meant re-picking the constant.
# Set COLS and the grid fills the width.
TILE_GAP = 6
LABEL_H = 13
MIN_TILE = 44       # below this the panel is too short to bother drawing
COLS = 4
PAD_X = 10
PAD_Y = 8
HEADER_H = 22
HDR_BTN = 20        # the Auto Join pill and the sizes button
FILTER_H = 20
SECTION_H = 21      # taller, to carry FONT_SECTION
FOOTER_H = 18
FONT_TITLE = 11
FONT_LABEL = 9
FONT_SECTION = 11   # category headers: they organise the whole grid,
                    # so they should not be smaller than the tile labels
SCROLL_STEP_ROWS = 1

# ---- Module state ----------------------------------------------------------
_shutdown = False
_collapsed = set()       # section keys the user folded away
_list = ScrollList(bar_width=4, bar_pad=4, min_rows=2)

_textures = {}           # cabinet_name -> GPUTexture, or None if it failed
_wanted = []             # names the draw pass asked for, most recent first
_timer_running = False


# ---- Catalog filtering -----------------------------------------------------

def _wm():
    return bpy.context.window_manager


def current_query():
    return getattr(_wm(), 'hb_library_search', '') or ''


def current_category():
    return getattr(_wm(), 'hb_library_category', 'ALL') or 'ALL'


def face_frame_props(context):
    """The scene's face-frame settings, or None."""
    return getattr(context.scene, 'hb_face_frame', None)


def auto_join_on(context):
    props = face_frame_props(context)
    return bool(getattr(props, 'auto_join_cabinets', False)) if props else False


def visible_products():
    """Products passing the category + search filters."""
    return library_catalog.search_products(current_query(), current_category())


def category_label():
    key = current_category()
    for ident, label, _desc in library_catalog.category_items():
        if ident == key:
            return label
    return "All Categories"

# ---- Texture cache ---------------------------------------------------------

def _want(cabinet_name):
    """Note that a tile wanted this thumbnail. Called from draw, so it
    must not touch bpy.data -- the timer does the loading."""
    if cabinet_name in _textures or cabinet_name in _wanted:
        return
    _wanted.append(cabinet_name)


def _load_one(cabinet_name):
    """Decode a product thumbnail into a GPUTexture, or None."""
    path = library_catalog.thumbnail_path(cabinet_name)
    if not path:
        return None
    img = None
    try:
        img = bpy.data.images.load(path, check_existing=False)
        # These PNGs are already display-referred. Left as sRGB,
        # from_image returns an SRGB8_A8 texture, so sampling decodes
        # it to linear -- and a POST_PIXEL overlay draws that out
        # with no re-encode, which is why every thumbnail came out
        # muddy. Non-Color yields RGBA8 with byte-identical data and
        # no decode, at the same 4 bytes per pixel.
        try:
            img.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass
        img.scale(THUMB_PX, THUMB_PX)
        return gpu.texture.from_image(img)
    except Exception:
        return None
    finally:
        # The texture owns its data, so the image can go straight away.
        if img is not None:
            try:
                bpy.data.images.remove(img)
            except Exception:
                pass

def _tick():
    """Timer: drain a few thumbnail requests per tick."""
    global _timer_running
    if _shutdown:
        _timer_running = False
        return None
    if not _wanted:
        _timer_running = False
        return None
    for _ in range(LOADS_PER_TICK):
        if not _wanted:
            break
        name = _wanted.pop()
        if name not in _textures:
            _textures[name] = _load_one(name)
    tag_redraw()
    return TICK_INTERVAL


def _ensure_timer():
    global _timer_running
    if _timer_running or _shutdown or not _wanted:
        return
    _timer_running = True
    bpy.app.timers.register(_tick, first_interval=0.0)


def _drop_textures():
    _textures.clear()
    _wanted.clear()
    _labels.clear()


# ---- Layout ----------------------------------------------------------------

def _tile_metrics(panel_w, s):
    """(tile, gap, cell_height) for a panel `panel_w` px wide.

    Build and scroll both need this and must agree: a scroll step that
    is not exactly one row leaves the grid drifting out of alignment.
    """
    gap = TILE_GAP * s
    reserve = (_list.bar_width + _list.bar_pad) * s
    tile = ((panel_w - reserve) - gap * (COLS - 1)) / COLS
    return tile, gap, tile + LABEL_H * s + gap


def compute_layout(context, rect):
    """(panel, header, filter_rects, clip, tiles, track, thumb, total).

    `tiles` is [(product, tile_rect, image_rect)] for the rows the clip
    rect can actually show -- everything else is skipped, which is what
    keeps the cost flat as the library grows.
    """
    s = scale()
    panel_x, bottom, panel_w, panel_h = rect
    top = bottom + panel_h
    if panel_h < (HEADER_H + FILTER_H + FOOTER_H + MIN_TILE) * s:
        return None

    items = visible_products()
    # The scrollbar is reserved unconditionally in _tile_metrics:
    # letting it come and go would re-size every tile as a filter
    # narrows the list, reflowing the grid while you type.
    tile, gap, cell_h = _tile_metrics(panel_w, s)
    sect_h = SECTION_H * s

    # Group into sections so the grid reads like the sidebar's boxes
    # instead of one undifferentiated wall of tiles. Collapsing folds a
    # section to its header; searching leaves the headers in place so it
    # stays obvious WHERE the matches came from.
    blocks = []          # ('header', section) | ('row', [products])
    order = [sec['key'] for sec in library_catalog.SECTIONS]
    by_section = {}
    for product in items:
        by_section.setdefault(product['section'], []).append(product)
    for key in order:
        group = by_section.get(key)
        if not group:
            continue
        section = library_catalog.section_by_key(key)
        blocks.append(('header', (key, section['label'], len(group))))
        if key in _collapsed:
            continue
        for i in range(0, len(group), COLS):
            blocks.append(('row', group[i:i + COLS]))

    def _block_h(block):
        return sect_h if block[0] == 'header' else cell_h

    content_h = sum(_block_h(b) for b in blocks)

    content_x = panel_x
    content_w = panel_w
    hdr_h = HEADER_H * s
    header_rect = (content_x, top - hdr_h, content_w, hdr_h)
    # Two controls live in the header, right-aligned: Auto Join, which
    # is a mode you want to SEE the state of rather than hunt for, and
    # the cabinet sizes, which are a form and so open as a popup.
    btn = HDR_BTN * s
    sizes_rect = (content_x + content_w - btn, top - hdr_h, btn, hdr_h)
    aj_w = 62 * s
    autojoin_rect = (sizes_rect[0] - 4 * s - aj_w, top - hdr_h, aj_w, hdr_h)
    # Filter bar: category on the left, search on the right. Both are
    # buttons that open a native popup -- a GPU panel is the wrong place
    # to reimplement a text field, and Blender's own popup already does
    # keyboard, undo and paste properly.
    fy = header_rect[1] - 2 * s - FILTER_H * s
    cat_w = content_w * 0.56
    cat_rect = (content_x, fy, cat_w, FILTER_H * s)
    search_rect = (content_x + cat_w + 4 * s, fy,
                   content_w - cat_w - 4 * s, FILTER_H * s)

    list_top = fy - PAD_Y * s
    max_list_h = list_top - (bottom + FOOTER_H * s)
    list_h, _scrollable, _r = _list.measure(content_h, max_list_h, cell_h)
    _list.clamp(content_h, list_h)
    list_bottom = list_top - list_h
    clip_rect = (content_x, list_bottom, content_w, list_h)
    track, thumb = _list.bar_rects(content_x, content_w, list_top, list_h,
                                   content_h, cell_h)

    tiles = []
    headers = []         # (key, label, count, rect)
    for block, block_top, _block_bottom in _list.visible(
            blocks, list_top, list_bottom, _block_h):
        kind, payload = block
        if kind == 'header':
            key, label, count = payload
            headers.append((key, label, count,
                            (content_x, block_top - sect_h,
                             content_w, sect_h)))
            continue
        for col, product in enumerate(payload):
            tx = content_x + col * (tile + gap)
            ty = block_top - tile
            tiles.append((product, (tx, ty - LABEL_H * s, tile,
                                    tile + LABEL_H * s), (tx, ty, tile, tile)))
    panel_rect = rect
    return (panel_rect, header_rect,
            (cat_rect, search_rect, autojoin_rect, sizes_rect), clip_rect,
            tiles, track, thumb, len(items), headers)

def _hit_section(mx, my, layout):
    """Section key whose header is under the cursor, or None."""
    if layout is None:
        return None
    if not point_in_rect(mx, my, layout[3]):
        return None
    for key, _label, _count, rect in layout[8]:
        if point_in_rect(mx, my, rect):
            return key
    return None


def _hit_tile(mx, my, layout):
    if layout is None:
        return None
    clip, tiles = layout[3], layout[4]
    if not point_in_rect(mx, my, clip):
        return None
    for product, tile_rect, _img in tiles:
        if point_in_rect(mx, my, tile_rect):
            return product
    return None


def _hit_filter(mx, my, layout):
    """'CATEGORY' / 'SEARCH' / None."""
    if layout is None:
        return None
    cat_rect, search_rect, autojoin_rect, sizes_rect = layout[2]
    if point_in_rect(mx, my, cat_rect):
        return 'CATEGORY'
    if point_in_rect(mx, my, search_rect):
        return 'SEARCH'
    if point_in_rect(mx, my, autojoin_rect):
        return 'AUTOJOIN'
    if point_in_rect(mx, my, sizes_rect):
        return 'SIZES'
    return None

# ---- Draw ------------------------------------------------------------------

_labels = {}        # (cabinet_name, display, width, size) -> fitted text


def _label_for(product, font_id, size, max_w):
    """fit_text is a binary search over blf.dimensions; the answer is
    the same every frame, so it is worth remembering. Keyed on width
    and size too, so a resize or a UI-scale change re-fits."""
    key = (product['cabinet_name'], product['display'],
           round(max_w, 1), round(size, 1))
    text = _labels.get(key)
    if text is None:
        text = fit_text(font_id, size, product['display'], max_w)
        _labels[key] = text
    return text


def _draw_thumb(tex, rect):
    shader = gpu.shader.from_builtin('IMAGE')
    x, y, w, h = rect
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {"pos": ((x, y), (x + w, y), (x + w, y + h), (x, y + h)),
         "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1))})
    shader.bind()
    shader.uniform_sampler("image", tex)
    batch.draw(shader)


# ---- Tab provider -----------------------------------------------------------
# The scene-navigator shell owns the frame, the header and the tab strip
# and hands this module a rect. It used to be a panel in its own right
# down the right-hand side, which fought the navigation gizmo and split
# the interface across two corners.

PREFERRED_WIDTH = 268       # unscaled; three tiles plus the scrollbar


def build(rect, context):
    """Lay the grid out inside `rect`. One entry, carrying the layout."""
    layout = compute_layout(context, rect)
    return [('library', layout)] if layout else []


def _layout_of(entries):
    for entry in entries or ():
        if entry[0] == 'library':
            return entry[1]
    return None


def paint(entries, mx, my):
    layout = _layout_of(entries)
    if layout is None:
        return
    _paint_grid(layout, mx, my)


def hit(context, mx, my, entries):
    """True when the click landed on something of ours."""
    layout = _layout_of(entries)
    if layout is None:
        return False
    which = _hit_filter(mx, my, layout)
    if which == 'CATEGORY':
        bpy.ops.wm.call_menu(name=HB_MT_library_category.bl_idname)
        return True
    if which == 'SEARCH':
        bpy.ops.home_builder.library_search('INVOKE_DEFAULT')
        return True
    if which == 'AUTOJOIN':
        props = face_frame_props(context)
        if props is not None:
            props.auto_join_cabinets = not props.auto_join_cabinets
        tag_redraw()
        return True
    if which == 'SIZES':
        bpy.ops.home_builder.cabinet_sizes('INVOKE_DEFAULT')
        return True
    key = _hit_section(mx, my, layout)
    if key is not None:
        if key in _collapsed:
            _collapsed.discard(key)
        else:
            _collapsed.add(key)
        tag_redraw()
        return True
    product = _hit_tile(mx, my, layout)
    if product is not None:
        # Close first: unpinned, the panel is a menu, and the
        # drop modal that follows wants the viewport to itself.
        from . import scene_navigator
        scene_navigator.dismiss_after_action()
        bpy.ops.hb_face_frame.draw_cabinet(
            'INVOKE_DEFAULT', cabinet_name=product['cabinet_name'])
        return True
    return False


def scroll(mx, my, entries, rows):
    layout = _layout_of(entries)
    if layout is None or not point_in_rect(mx, my, layout[3]):
        return False
    s = scale()
    _list.scroll_by(rows, _tile_metrics(layout[0][2], s)[2])
    tag_redraw()
    return True


def _paint_grid(layout, mx, my):
    context = bpy.context
    (panel_rect, header_rect,
     (cat_rect, search_rect, autojoin_rect, sizes_rect), clip_rect,
     tiles, track, thumb, total, headers) = layout

    # Hover comes from the cursor the shell hands us, so this module
    # needs no listener of its own.
    _p = _hit_tile(mx, my, layout)
    hover = _p['cabinet_name'] if _p else None
    hover_ui = _hit_filter(mx, my, layout)
    hover_section = _hit_section(mx, my, layout)

    s = scale()
    font_id = 0
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()

    tx, ty, _tw, th = header_rect
    draw_text(font_id, tx + 2 * s, ty + (th - FONT_TITLE * s) / 2.0 + 1 * s,
              FONT_TITLE * s, Theme.TEXT_PRIMARY, 'Library  (%d)' % total)

    aj = auto_join_on(context)
    paint_button(shader, autojoin_rect, hovered=hover_ui == 'AUTOJOIN',
                 active=aj)
    draw_centered_text(font_id, autojoin_rect, FONT_LABEL * s,
                       Theme.TEXT_PRIMARY if aj else Theme.TEXT_DIM,
                       'Auto Join')
    paint_button(shader, sizes_rect, hovered=hover_ui == 'SIZES')
    # Three stacked bars with a mark against them -- a size chart.
    sx, sy, sw, sh = sizes_rect
    for i in range(3):
        by = sy + sh * (0.32 + i * 0.18)
        draw_rects(shader, [(sx + 5 * s, by, sw - 12 * s, 1.4 * s)],
                   Theme.GLYPH)
    draw_rects(shader, [(sx + sw - 6 * s, sy + sh * 0.3, 1.4 * s, sh * 0.42)],
               Theme.GLYPH)

    # Filter bar. The search box shows the live query so it is obvious
    # when a filter is hiding things.
    query = current_query()
    paint_button(shader, cat_rect, hovered=hover_ui == 'CATEGORY')
    paint_button(shader, search_rect, hovered=hover_ui == 'SEARCH',
                 active=bool(query))
    draw_centered_text(font_id, cat_rect, FONT_LABEL * s,
                       Theme.TEXT_NORMAL,
                       fit_text(font_id, FONT_LABEL * s, category_label(),
                                cat_rect[2] - 6 * s))
    draw_centered_text(font_id, search_rect, FONT_LABEL * s,
                       Theme.TEXT_PRIMARY if query else Theme.TEXT_DIM,
                       fit_text(font_id, FONT_LABEL * s,
                                query or 'Search...',
                                search_rect[2] - 6 * s))

    if track is not None:
        draw_rect(shader, *track, Theme.SCROLLBAR_TRACK)
        draw_rect(shader, *thumb, Theme.SCROLLBAR_THUMB)

    if not tiles and not headers:
        draw_centered_text(font_id, clip_rect, FONT_LABEL * s,
                           Theme.TEXT_DIM, 'No products match')
        gpu.state.blend_set('NONE')
        return

    # Scissor the grid so a partly scrolled row cuts off cleanly.
    prev = begin_clip(clip_rect)
    try:
        # Section headers: a chevron, the name, and the count. Clicking
        # one folds the section away.
        for key, label, count, rect in headers:
            hx, hy, hw, hh = rect
            if key == hover_section:
                draw_rects(shader, [rect], Theme.ROW_HOVER_BG)
            collapsed = key in _collapsed
            glyph_chevron(shader, hx + 6 * s, hy + hh / 2.0, 7 * s,
                          collapsed, Theme.GLYPH)
            draw_text(font_id, hx + 16 * s,
                      hy + (hh - FONT_SECTION * s) / 2.0 + 1 * s,
                      FONT_SECTION * s, Theme.TEXT_PRIMARY,
                      '%s  (%d)' % (label, count))
            draw_rects(shader, [(hx, hy, hw, 1 * s)], Theme.SEPARATOR)

        # Tile chrome goes out in two batches rather than two per tile
        # -- see draw_rects. No outline: a border around every tile
        # drew a white grid over the thumbnails and competed with the
        # renders themselves. The fill alone separates them, and
        # hover is the only state that needs to stand out.
        plain = [r for p, r, _i in tiles if p['cabinet_name'] != hover]
        lit = [r for p, r, _i in tiles if p['cabinet_name'] == hover]
        if plain:
            draw_rects(shader, plain, Theme.BTN_BG)
        if lit:
            draw_rects(shader, lit, Theme.BTN_HOVER_BG)
        for product, _tile_rect, img_rect in tiles:
            tex = _textures.get(product['cabinet_name'])
            if tex is None:
                _want(product['cabinet_name'])
                continue
            gpu.state.blend_set('ALPHA')
            _draw_thumb(tex, img_rect)
        shader.bind()
        for product, tile_rect, _img in tiles:
            lx, ly, lw, _lh = tile_rect
            label = _label_for(product, font_id, FONT_LABEL * s, lw - 2 * s)
            draw_centered_text(font_id, (lx, ly, lw, LABEL_H * s),
                               FONT_LABEL * s,
                               Theme.TEXT_PRIMARY
                               if product['cabinet_name'] == hover
                               else Theme.TEXT_NORMAL, label)
    finally:
        end_clip(prev)

    # Footer: the hovered product's full name, which the tile label
    # usually had to truncate.
    if hover is not None:
        px, py, pw, _ph = panel_rect
        frect = (px + PAD_X * s, py + PAD_Y * s, pw - PAD_X * s * 2,
                 FOOTER_H * s)
        shader.bind()
        draw_centered_text(font_id, frect, FONT_LABEL * s, Theme.TEXT_DIM,
                           fit_text(font_id, FONT_LABEL * s, hover,
                                    frect[2] - 4 * s))

    gpu.state.blend_set('NONE')
    _ensure_timer()


class home_builder_OT_library_search(bpy.types.Operator):
    """Filter the viewport library by name"""
    bl_idname = "home_builder.library_search"
    bl_label = "Search Library"

    query: bpy.props.StringProperty(name="Search")  # type: ignore

    def invoke(self, context, event):
        self.query = current_query()
        return context.window_manager.invoke_props_dialog(self, width=280)

    def draw(self, context):
        self.layout.prop(self, 'query', text='')

    def execute(self, context):
        context.window_manager.hb_library_search = self.query
        _list.offset = 0.0
        tag_redraw()
        return {'FINISHED'}


class home_builder_OT_library_set_category(bpy.types.Operator):
    """Show only this part of the library"""
    bl_idname = "home_builder.library_set_category"
    bl_label = "Set Library Category"
    bl_options = {'INTERNAL'}

    category: bpy.props.StringProperty(default='ALL')  # type: ignore

    def execute(self, context):
        context.window_manager.hb_library_category = self.category
        _list.offset = 0.0
        tag_redraw()
        return {'FINISHED'}


class HB_MT_library_category(bpy.types.Menu):
    """Category picker for the viewport library."""
    bl_idname = "HB_MT_library_category"
    bl_label = "Library Category"

    def draw(self, context):
        layout = self.layout
        current = current_category()
        for ident, label, _desc in library_catalog.category_items():
            row = layout.row()
            op = row.operator('home_builder.library_set_category',
                              text=label,
                              icon='CHECKMARK' if ident == current else 'BLANK1')
            op.category = ident

class home_builder_OT_cabinet_sizes(bpy.types.Operator):
    """Default sizes used for newly placed cabinets"""
    bl_idname = "home_builder.cabinet_sizes"
    bl_label = "Cabinet Sizes"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=460)

    def draw(self, context):
        layout = self.layout
        props = face_frame_props(context)
        if props is None:
            layout.label(text="Unavailable in this scene.", icon='ERROR')
            return
        # The sidebar's own Cabinet Sizes form, verbatim.
        props.draw_cabinet_sizes_ui(layout, context)

    def execute(self, context):
        return {'FINISHED'}


classes = (
    home_builder_OT_cabinet_sizes,
    home_builder_OT_library_search,
    home_builder_OT_library_set_category,
    HB_MT_library_category,
)


# ---- Lifecycle -------------------------------------------------------------

def tag_redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def register():
    global _shutdown
    _shutdown = False
    for cls in classes:
        bpy.utils.register_class(cls)
    # Filter state on the WindowManager, not the Scene: it is a way of
    # looking at the library, not part of the job.
    bpy.types.WindowManager.hb_library_search = bpy.props.StringProperty(
        name='Search', default='')
    bpy.types.WindowManager.hb_library_category = bpy.props.StringProperty(
        name='Category', default='ALL')
    from . import scene_navigator
    scene_navigator.register_provider(scene_navigator.TAB_LIBRARY,
                                      sys.modules[__name__])


def unregister():
    global _shutdown, _timer_running
    _shutdown = True
    _timer_running = False
    _drop_textures()
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for prop in ('hb_library_search', 'hb_library_category'):
        if hasattr(bpy.types.WindowManager, prop):
            delattr(bpy.types.WindowManager, prop)
