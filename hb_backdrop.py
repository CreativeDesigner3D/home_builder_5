"""Backdrops: a plan to trace, laid flat on a level of a house.

Most houses start from a plan someone already has - an architect's PDF
set, a scan, a photo of a sketch. Add PDF / Image (HOUSE > Levels) or a
PDF dropped on the viewport lays a page on the active level, just under
its floor, as an image empty: walls are drawn over it with the usual
tools, and rays pass through it, so it never gets in their way.

A page has no real size until something says what a paper inch means.
A PDF's import takes the sheet's drawing scale (1/4" = 1'-0" by default)
as a first guess; Set Scale makes it exact: click both ends of a
dimension printed on the sheet, type its length, and the page rescales
about the first point, which stays where it is. Pages of one PDF are
printed at one scale, so a scale set on one page carries to the others
already placed from that PDF and becomes the default for later ones.

Each level keeps its own backdrops, in its Backdrop part collection, so
they show and hide with the level. They never render.

The PDF reading is Spaces' (spaces/ui/reference_images.py), ported:
pypdfium2 rasterizes a page into a byte buffer, which OpenImageIO -
shipped with Blender - writes as PNG. The import is lazy, so Home
Builder still loads without the wheel; the operator says what is
missing instead.
"""

import hashlib
import os
import tempfile

import bpy
import bpy.utils.previews
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty, IntProperty, StringProperty)
from mathutils import Matrix, Vector

from . import hb_house

BACKDROP_KEY = 'IS_HOUSE_BACKDROP'
PART = 'Backdrop'               # the level sub-collection
# Custom props on a placed page: the file it came from, its 1-based page,
# the page's longer side in points (so a scale can be turned back into a
# display size), and - once scaled - world metres per paper metre.
SOURCE_KEY = 'HB_BACKDROP_SOURCE'
PAGE_KEY = 'HB_BACKDROP_PAGE'
PT_SIZE_KEY = 'HB_BACKDROP_PT_SIZE'
FACTOR_KEY = 'HB_BACKDROP_FACTOR'

ABOVE_FLOOR = 0.003             # a backdrop lies just on its level's floor
# It is drawn in front of the model, at its Opacity, so the plan stays in
# view over the floors and walls built on it. (Drawn behind, or in depth
# with the model, a floor hides it: Blender draws a see-through image
# before the solid model, whatever its height.)
DEPTH = 'FRONT'
PT_TO_M = 0.0254 / 72.0
THUMB_PX = 256                  # longer side of a page thumbnail
THUMB_LIMIT = 200               # pages past this get a label but no thumbnail
IMAGE_GUESS = 15.0              # metres across for an image with no scale yet
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp')

# Architectural scales as "world units per paper unit". The name is what
# a title block says; the identifier is the factor.
_SCALE_ITEMS = [
    ('48', '1/4" = 1\'-0"', "1:48"),
    ('96', '1/8" = 1\'-0"', "1:96"),
    ('64', '3/16" = 1\'-0"', "1:64"),
    ('32', '3/8" = 1\'-0"', "1:32"),
    ('24', '1/2" = 1\'-0"', "1:24"),
    ('100', "1:100", "Metric 1:100"),
    ('50', "1:50", "Metric 1:50"),
    ('200', "1:200", "Metric 1:200"),
    ('1', "Actual page size", "1:1 - set the scale afterwards"),
]
# Enum item lists handed to Blender have to stay referenced from Python.
_SCALE_ITEMS_WITH_SET = []
_FALLBACK_PAGE_ITEMS = [('1', "Page 1", "")]

_PREVIEWS = None    # bpy.utils.previews collection of page thumbnails
_THUMBS = {}        # abs path -> (mtime, [enum items with icons])
_PAGE_COUNTS = {}   # abs path -> (mtime, count)


# ---- pdfium ---------------------------------------------------------------

def _pdfium():
    """pypdfium2, imported on demand. Raises ImportError with a message
    the operator can show when the wheel is not installed."""
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise ImportError(
            "PDF backdrops need the pypdfium2 wheel. Re-enable Home "
            "Builder so Blender installs its wheels.") from exc
    return pdfium


def _page_count(path):
    """Pages in ``path``, cached by (path, mtime). Raises on a bad file."""
    path = bpy.path.abspath(path)
    mtime = os.path.getmtime(path)
    hit = _PAGE_COUNTS.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    pdf = _pdfium().PdfDocument(path)
    try:
        n = len(pdf)
    finally:
        pdf.close()
    _PAGE_COUNTS[path] = (mtime, n)
    return n


def _write_png(path, arr):
    """Write an (h, w, 3|4) uint8 array, top row first, as PNG."""
    import numpy as np
    arr = np.ascontiguousarray(arr)
    h, w, c = arr.shape
    try:
        import OpenImageIO as oiio
    except ImportError:
        oiio = None
    if oiio is not None:
        spec = oiio.ImageSpec(w, h, c, oiio.UINT8)
        out = oiio.ImageOutput.create(path)
        if out is None:
            raise RuntimeError(oiio.geterror())
        if not out.open(path, spec):
            raise RuntimeError(out.geterror())
        ok = out.write_image(arr)
        err = out.geterror()
        out.close()
        if not ok:
            raise RuntimeError(err or "PNG write failed")
        return
    # No OpenImageIO: go through a Blender image buffer (float RGBA, so
    # heavy for a large sheet, but it works everywhere)
    img = bpy.data.images.new("__hb_pdf_page", w, h, alpha=False)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = arr[::-1, :, :3].astype(np.float32) / 255.0
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = path
    img.file_format = 'PNG'
    img.save()
    bpy.data.images.remove(img)


def _render_page_to(page, scale, out_png):
    bitmap = page.render(scale=scale, rev_byteorder=True, prefer_bgrx=False)
    try:
        _write_png(out_png, bitmap.to_numpy())
    finally:
        bitmap.close()


def render_pdf_page(path, page_index, dpi, out_png):
    """Rasterize one page (zero-based) of ``path`` to ``out_png``.
    Returns the page size in points."""
    pdf = _pdfium().PdfDocument(bpy.path.abspath(path))
    try:
        page = pdf[page_index]
        try:
            size = page.get_size()
            _render_page_to(page, dpi / 72.0, out_png)
        finally:
            page.close()
    finally:
        pdf.close()
    return size


def _thumb_folder():
    folder = os.path.join(tempfile.gettempdir(), "hb_backdrops", "thumbs")
    os.makedirs(folder, exist_ok=True)
    return folder


def _page_items_for(path):
    """Enum items - one per page, with a thumbnail icon - for the page
    picker, rendered once per (path, mtime). Raises on a bad file."""
    path = bpy.path.abspath(path)
    mtime = os.path.getmtime(path)
    hit = _THUMBS.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    key_base = hashlib.md5(f"{path}|{mtime}".encode("utf-8")).hexdigest()[:12]
    folder = _thumb_folder()
    items = []
    pdf = _pdfium().PdfDocument(path)
    try:
        n = len(pdf)
        _PAGE_COUNTS[path] = (mtime, n)
        for i in range(n):
            icon = 0
            if i < THUMB_LIMIT and _PREVIEWS is not None:
                key = f"{key_base}:{i + 1}"
                png = os.path.join(folder, f"{key_base}_p{i + 1}.png")
                try:
                    if key not in _PREVIEWS:
                        if not os.path.isfile(png):
                            page = pdf[i]
                            try:
                                w, h = page.get_size()
                                _render_page_to(page, THUMB_PX / max(w, h), png)
                            finally:
                                page.close()
                        _PREVIEWS.load(key, png, 'IMAGE')
                    icon = _PREVIEWS[key].icon_id
                except Exception:
                    icon = 0
            items.append((str(i + 1), f"Page {i + 1}", "", icon, i))
    finally:
        pdf.close()
    _THUMBS[path] = (mtime, items)
    return items


def _png_path(pdf_path, page_number):
    """Where a rasterized page goes: a backdrops folder beside the .blend,
    or the temp dir for an unsaved file (the image is packed either way)."""
    stem = os.path.splitext(os.path.basename(pdf_path))[0]
    if bpy.data.filepath:
        folder = os.path.join(os.path.dirname(bpy.data.filepath), "backdrops")
    else:
        folder = os.path.join(tempfile.gettempdir(), "hb_backdrops")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{stem}_p{page_number}.png")


# ---- backdrops on a level -------------------------------------------------

def _collection(scene, level):
    hb_house.ensure_level_collections(scene, level)
    col = hb_house.level_subcollection(level, PART)
    if col is None:
        col = bpy.data.collections.new(f"{level.name} - {PART}")
        col['HB_LEVEL_PART'] = PART
        level.collection.children.link(col)
    return col


def backdrops_of(scene, level=None):
    """The backdrops in a scene, or on one level."""
    return [o for o in scene.objects if o.get(BACKDROP_KEY)
            and (level is None or o.get(hb_house.LEVEL_KEY) == level.uid)]


def place_backdrop(scene, level, image, display_size, center, opacity=0.6):
    """Lay an image flat on a level, centred on `center` (x, y), its longer
    side `display_size` metres. Returns the image empty."""
    empty = bpy.data.objects.new(image.name, None)
    _collection(scene, level).objects.link(empty)
    empty.empty_display_type = 'IMAGE'
    empty.data = image
    # Centred on its origin; Set Scale moves it to keep its first point
    empty.empty_image_offset = (-0.5, -0.5)
    empty.empty_display_size = display_size
    empty.empty_image_depth = DEPTH
    empty.empty_image_side = 'FRONT'
    empty.use_empty_image_alpha = True
    empty.show_empty_image_perspective = False
    empty.show_empty_image_orthographic = True
    empty.show_empty_image_only_axis_aligned = False
    empty.color = (1.0, 1.0, 1.0, opacity)
    empty.location = (center[0], center[1], level.elevation + ABOVE_FLOOR)
    empty.hide_render = True
    empty[BACKDROP_KEY] = True
    empty[hb_house.LEVEL_KEY] = level.uid
    apply_level_settings(scene, level)
    return empty


def scale_about(obj, point, ratio):
    """Scale an image backdrop by `ratio` about a plan point, which stays
    where it is."""
    obj.empty_display_size *= ratio
    p = Vector((point[0], point[1]))
    loc = obj.location.xy
    new = p + (loc - p) * ratio
    obj.location.x, obj.location.y = new.x, new.y


def _factor_of(obj):
    """World metres per paper metre implied by a page's display size."""
    pt = obj.get(PT_SIZE_KEY)
    if not pt:
        return None
    return obj.empty_display_size / (float(pt) * PT_TO_M)


def _same_source(path):
    """Every placed page from ``path``, any scene."""
    path = bpy.path.abspath(path)
    return [o for o in bpy.data.objects
            if o.get(SOURCE_KEY) == path and o.get(PT_SIZE_KEY)]


def _scaled_sibling(path):
    """(object, factor) of a scaled page from ``path``, or None."""
    if not path:
        return None
    for o in _same_source(path):
        if o.get(FACTOR_KEY):
            return o, float(o[FACTOR_KEY])
    return None


def apply_level_settings(scene, level):
    """A level's backdrops take its Backdrop settings: shown, opacity, and
    locked against picking - and lie on its floor."""
    for obj in backdrops_of(scene, level):
        obj.hide_viewport = not level.backdrop_shown
        obj.hide_select = level.backdrop_locked
        obj.color[3] = level.backdrop_opacity
        lay_on_floor(obj, level)


def lay_on_floor(obj, level):
    """Just above the level's floor, drawn in front of the model. (Older
    backdrops lay under the floor, drawn behind everything, and a floor
    hid them.)"""
    z = level.elevation + ABOVE_FLOOR
    if abs(obj.location.z - z) > 1e-6:
        obj.location.z = z
    if obj.empty_image_depth != DEPTH:
        obj.empty_image_depth = DEPTH


@bpy.app.handlers.persistent
def _load_post(_dummy):
    """Bring a file's backdrops up onto their floors."""
    for scene in bpy.data.scenes:
        house = getattr(scene, 'hb_house', None)
        if house is None:
            continue
        for level in house.levels:
            for obj in backdrops_of(scene, level):
                lay_on_floor(obj, level)


def _level_settings_changed(self, context):
    scene = hb_house.house_scene_of(context.scene) if context else None
    if scene is not None:
        apply_level_settings(scene, self)


def backdrop_summary(level):
    scene = hb_house.get_house_scene()
    objs = backdrops_of(scene, level) if scene is not None else []
    if not objs:
        return "None"
    name = objs[0].get(SOURCE_KEY) or (objs[0].data.name if objs[0].data else objs[0].name)
    name = os.path.basename(name)
    more = f" +{len(objs) - 1}" if len(objs) > 1 else ""
    scaled = "" if any(o.get(FACTOR_KEY) or o.get('HB_BACKDROP_SCALED') for o in objs) else " · not scaled"
    return name + more + scaled


def _view_center(context):
    rv3d = getattr(context, 'region_data', None)
    if rv3d is not None:
        return tuple(rv3d.view_location.xy)
    for area in getattr(context.screen, 'areas', ()) if context.screen else ():
        if area.type == 'VIEW_3D':
            return tuple(area.spaces.active.region_3d.view_location.xy)
    return tuple(context.scene.cursor.location.xy)


def _house_level(context):
    if not hb_house.is_house_project(context):
        return None
    scene = context.scene
    if not scene.get(hb_house.HOUSE_SCENE_KEY):
        return None
    return hb_house.active_level(context)


# ---- operators ------------------------------------------------------------

def _page_items(self, context):
    hit = _THUMBS.get(bpy.path.abspath(self.filepath))
    return hit[1] if hit else _FALLBACK_PAGE_ITEMS


def _scale_items(self, context):
    sib = _scaled_sibling(self.filepath)
    if sib is None:
        return _SCALE_ITEMS
    obj, factor = sib
    _SCALE_ITEMS_WITH_SET[:] = [
        ('SCALED', f"Match scaled page {obj.get(PAGE_KEY, '?')}  (1:{factor:.1f})",
         "Use the scale set on another page of this PDF")
    ] + _SCALE_ITEMS
    return _SCALE_ITEMS_WITH_SET


class HOME_BUILDER_OT_add_backdrop(bpy.types.Operator):
    """Lay a PDF page or an image on the active level to trace walls over"""
    bl_idname = "home_builder.add_backdrop"
    bl_label = "Add PDF / Image"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})  # type: ignore
    filter_glob: StringProperty(
        default="*.pdf;" + ";".join("*" + e for e in IMAGE_EXTENSIONS),
        options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return _house_level(context) is not None

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        path = bpy.path.abspath(self.filepath)
        if not os.path.isfile(path):
            self.report({'WARNING'}, "Pick a PDF or an image.")
            return {'CANCELLED'}
        if path.lower().endswith('.pdf'):
            bpy.ops.home_builder.import_pdf_backdrop('INVOKE_DEFAULT', filepath=path)
            return {'FINISHED'}
        level = _house_level(context)
        try:
            img = bpy.data.images.load(path, check_existing=True)
        except RuntimeError as exc:
            self.report({'ERROR'}, f"Could not read the image: {exc}")
            return {'CANCELLED'}
        try:
            img.pack()
        except RuntimeError:
            pass
        empty = place_backdrop(context.scene, level, img, IMAGE_GUESS,
                               _view_center(context), level.backdrop_opacity)
        empty[SOURCE_KEY] = path
        self.report({'INFO'}, f"{os.path.basename(path)} placed on {level.name}. "
                              "Use Set Scale on a known dimension to size it.")
        return {'FINISHED'}


class HOME_BUILDER_OT_import_pdf_backdrop(bpy.types.Operator):
    """Lay a page of a PDF on the active level to trace walls over"""
    bl_idname = "home_builder.import_pdf_backdrop"
    bl_label = "Add PDF Page"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})  # type: ignore
    location: FloatVectorProperty(size=2, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    has_location: BoolProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    page_enum: EnumProperty(name="Page", items=_page_items)  # type: ignore
    dpi: IntProperty(name="Resolution", description="Pixels per paper inch",
                     default=150, min=50, max=400)  # type: ignore
    scale: EnumProperty(
        name="Drawing Scale", items=_scale_items, options={'SKIP_SAVE'},
        description="Scale printed in the sheet's title block; sizes the page "
                    "as a first guess before Set Scale")  # type: ignore

    @classmethod
    def poll(cls, context):
        return _house_level(context) is not None

    def invoke(self, context, event):
        path = bpy.path.abspath(self.filepath)
        if not (self.filepath and os.path.isfile(path)):
            bpy.ops.home_builder.add_backdrop('INVOKE_DEFAULT')
            return {'FINISHED'}
        try:
            items = _page_items_for(path)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not read the PDF: {exc}")
            return {'CANCELLED'}
        if not items:
            self.report({'ERROR'}, "The PDF has no pages.")
            return {'CANCELLED'}
        if not self.has_location:
            region, rv3d = context.region, context.region_data
            point = None
            if event is not None and region is not None and rv3d is not None:
                from bpy_extras.view3d_utils import region_2d_to_location_3d
                level = _house_level(context)
                point = region_2d_to_location_3d(
                    region, rv3d, (event.mouse_region_x, event.mouse_region_y),
                    Vector((0.0, 0.0, level.elevation)))
            self.location = tuple(point.xy) if point is not None else _view_center(context)
        self.page_enum = '1'
        self.scale = 'SCALED' if _scaled_sibling(path) else '48'
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        layout.label(text=os.path.basename(self.filepath), icon='FILE')
        n = len(_page_items(self, context))
        layout.template_icon_view(self, "page_enum", show_labels=True,
                                  scale=7.0, scale_popup=4.0)
        layout.label(text=f"Page {self.page_enum} of {n}")
        layout.separator()
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "scale")
        col.prop(self, "dpi")

    def execute(self, context):
        level = _house_level(context)
        path = bpy.path.abspath(self.filepath)
        if level is None or not os.path.isfile(path):
            self.report({'WARNING'}, "Pick a PDF file.")
            return {'CANCELLED'}
        try:
            n = _page_count(path)
            page_number = max(1, min(int(self.page_enum), n))
            png = _png_path(path, page_number)
            w_pt, h_pt = render_pdf_page(path, page_number - 1, int(self.dpi), png)
        except Exception as exc:
            self.report({'ERROR'}, f"Could not read the PDF: {exc}")
            return {'CANCELLED'}
        img = bpy.data.images.load(png, check_existing=True)
        img.reload()
        try:
            img.pack()
        except RuntimeError:
            pass
        if self.scale == 'SCALED':
            sib = _scaled_sibling(path)
            factor = sib[1] if sib else 48.0
            label = "the scale set on its other pages"
        else:
            factor = float(self.scale)
            label = next(item[1] for item in _SCALE_ITEMS if item[0] == self.scale)
        pt_size = max(w_pt, h_pt)
        center = tuple(self.location) if self.location else _view_center(context)
        empty = place_backdrop(context.scene, level, img, pt_size * PT_TO_M * factor,
                               center, level.backdrop_opacity)
        empty.name = f"{os.path.splitext(os.path.basename(path))[0]} p{page_number}"
        empty[SOURCE_KEY] = path
        empty[PAGE_KEY] = page_number
        empty[PT_SIZE_KEY] = float(pt_size)
        if self.scale == 'SCALED':
            empty[FACTOR_KEY] = float(factor)
        tail = ("" if self.scale == 'SCALED' else
                " Use Set Scale on a known dimension to make it exact.")
        self.report({'INFO'}, f"Page {page_number} of {n} placed on {level.name} at {label}.{tail}")
        return {'FINISHED'}


class HOME_BUILDER_FH_pdf_backdrop(bpy.types.FileHandler):
    bl_idname = "HOME_BUILDER_FH_pdf_backdrop"
    bl_label = "PDF backdrop"
    bl_import_operator = "home_builder.import_pdf_backdrop"
    bl_file_extensions = ".pdf"

    @classmethod
    def poll_drop(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and _house_level(context) is not None)


def _plane_pick(region, rv3d, coord, z):
    """Screen ``coord`` -> the world point at height z, or None."""
    from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d
    origin = region_2d_to_origin_3d(region, rv3d, coord)
    direction = region_2d_to_vector_3d(region, rv3d, coord)
    if abs(direction.z) < 1e-7:
        return None
    t = (z - origin.z) / direction.z
    if rv3d.is_perspective and t < 0:
        return None
    return origin + direction * t


def _fmt_length(context, value):
    unit = context.scene.unit_settings
    try:
        return bpy.utils.units.to_string(unit.system, 'LENGTH', value, precision=4)
    except Exception:
        return f"{value:.4f} m"


class HOME_BUILDER_OT_scale_backdrop(bpy.types.Operator):
    """Click both ends of a dimension printed on the backdrop, then type its real length; the backdrop rescales about the first point"""
    bl_idname = "home_builder.scale_backdrop"
    bl_label = "Set Scale"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        level = _house_level(context)
        return level is not None and bool(backdrops_of(context.scene, level))

    def invoke(self, context, event):
        level = _house_level(context)
        objs = backdrops_of(context.scene, level)
        obj = context.object if context.object in objs else objs[0]
        area = context.area
        if area is None or area.type != 'VIEW_3D':
            return {'CANCELLED'}
        if context.region is None or context.region.type != 'WINDOW':
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if region is None:
                return {'CANCELLED'}
            with context.temp_override(area=area, region=region):
                return bpy.ops.home_builder.scale_backdrop('INVOKE_DEFAULT')
        self._obj_name = obj.name
        self._z = obj.location.z
        self._region = context.region
        self._rv3d = context.region_data
        self._points = []
        self._mouse = (event.mouse_region_x, event.mouse_region_y)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self._draw, (context,), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _pick(self, coord):
        return _plane_pick(self._region, self._rv3d, coord, self._z)

    def _header(self, context):
        if not self._points:
            text = "Set Scale: click one end of a dimension printed on the sheet"
        else:
            hit = self._pick(self._mouse)
            length = (hit - self._points[0]).length if hit else 0.0
            text = f"Set Scale: click its other end    {_fmt_length(context, length)}"
        context.area.header_text_set(text + "    (Esc / right-click to cancel)")

    def _end(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self._mouse = (event.mouse_region_x, event.mouse_region_y)
            self._header(context)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'TRACKPADPAN', 'TRACKPADZOOM'} or event.type.startswith('NUMPAD'):
            return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            hit = self._pick(self._mouse)
            if hit is None:
                return {'RUNNING_MODAL'}
            self._points.append(hit)
            if len(self._points) < 2:
                self._header(context)
                return {'RUNNING_MODAL'}
            measured = (self._points[1] - self._points[0]).length
            self._end(context)
            if measured < 1e-6:
                self.report({'WARNING'}, "The two points are the same spot.")
                return {'CANCELLED'}
            p0 = self._points[0]
            bpy.ops.home_builder.apply_backdrop_scale(
                'INVOKE_DEFAULT', object_name=self._obj_name, measured=measured,
                anchor=(p0.x, p0.y))
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def _draw(self, context):
        if context.region != self._region:
            return
        import gpu
        from gpu_extras.batch import batch_for_shader
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        pts = [location_3d_to_region_2d(self._region, self._rv3d, p) for p in self._points]
        pts = [p for p in pts if p is not None]
        if not pts:
            return
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        gpu.state.line_width_set(2.0)
        shader.bind()
        shader.uniform_float("color", (1.0, 0.6, 0.1, 0.9))
        batch_for_shader(shader, 'LINES', {"pos": [tuple(pts[0]), tuple(self._mouse)]}).draw(shader)
        gpu.state.line_width_set(1.0)
        gpu.state.point_size_set(8.0)
        batch_for_shader(shader, 'POINTS', {"pos": [tuple(p) for p in pts]}).draw(shader)
        gpu.state.blend_set('NONE')


class HOME_BUILDER_OT_apply_backdrop_scale(bpy.types.Operator):
    """Scale the backdrop so the measured span matches its real length"""
    bl_idname = "home_builder.apply_backdrop_scale"
    bl_label = "Set Scale"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    object_name: StringProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    measured: FloatProperty(options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    anchor: FloatVectorProperty(size=2, options={'HIDDEN', 'SKIP_SAVE'})  # type: ignore
    distance: FloatProperty(
        name="Real Length", description="What the span you clicked measures in the house",
        min=0.0001, subtype='DISTANCE', unit='LENGTH')  # type: ignore
    apply_to_siblings: BoolProperty(
        name="Other Pages of This PDF",
        description="Rescale the pages already placed from the same PDF to "
                    "match; pages placed later default to it too",
        default=True)  # type: ignore

    def _siblings(self, obj):
        src = obj.get(SOURCE_KEY)
        if not src or not obj.get(PT_SIZE_KEY):
            return []
        return [o for o in _same_source(src) if o != obj]

    def invoke(self, context, event):
        self.distance = self.measured
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.label(text=f"Measured on the sheet: {_fmt_length(context, self.measured)}")
        layout.prop(self, "distance")
        obj = bpy.data.objects.get(self.object_name)
        if obj is not None and obj.get(PT_SIZE_KEY):
            n = len(self._siblings(obj))
            row = layout.row()
            row.active = n > 0
            row.prop(self, "apply_to_siblings", text=f"Other Pages of This PDF ({n})")

    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if obj is None or self.measured <= 0:
            return {'CANCELLED'}
        ratio = self.distance / self.measured
        scale_about(obj, self.anchor, ratio)
        obj['HB_BACKDROP_SCALED'] = True
        factor = _factor_of(obj)
        carried = 0
        if factor is not None:
            obj[FACTOR_KEY] = float(factor)
            if self.apply_to_siblings:
                for o in self._siblings(obj):
                    o.empty_display_size = float(o[PT_SIZE_KEY]) * PT_TO_M * factor
                    o[FACTOR_KEY] = float(factor)
                    carried += 1
        msg = f"Backdrop scaled by {ratio:.4f}."
        if carried:
            msg += f" {carried} other page{'s' if carried != 1 else ''} matched."
        self.report({'INFO'}, msg)
        return {'FINISHED'}


# ---- Moving it into place -------------------------------------------------------
# A backdrop can't be clicked (rays pass through it), so it is moved by
# its level's Backdrop settings - X, Y and Rotation - or Move to Match:
# click a point on the plan, then where that point belongs, snapping to
# the corners of the walls on any level (the floor below, traced already).

SNAP_PX = 14


def move_by(scene, level, dx, dy):
    for obj in backdrops_of(scene, level):
        obj.location.x += dx
        obj.location.y += dy


def turn_to(scene, level, degrees):
    """Turn a level's backdrops to `degrees`, about the first one's middle."""
    import math
    objs = backdrops_of(scene, level)
    if not objs:
        return
    c = objs[0].location.xy.copy()
    d = math.radians(degrees) - objs[0].rotation_euler.z
    rot = Matrix.Rotation(d, 2)
    for obj in objs:
        p = c + rot @ (obj.location.xy - c)
        obj.location.x, obj.location.y = p.x, p.y
        obj.rotation_euler.z += d


def wall_corners(scene):
    """The corners of every wall in the house, in the world."""
    pts = []
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP'):
            continue
        try:
            from . import hb_types
            w = hb_types.GeoNodeWall(obj)
            length, t = w.get_input('Length'), w.get_input('Thickness')
        except Exception:
            continue
        m = obj.matrix_world
        pts += [m @ Vector(p) for p in ((0, 0, 0), (length, 0, 0), (0, t, 0), (length, t, 0))]
    return pts


class HOME_BUILDER_OT_move_backdrop(bpy.types.Operator):
    """Click a point on the backdrop, then where that point belongs - a wall corner on the floor below snaps - and the backdrop moves there"""
    bl_idname = "home_builder.move_backdrop"
    bl_label = "Move to Match"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        level = _house_level(context)
        return level is not None and bool(backdrops_of(context.scene, level))

    def invoke(self, context, event):
        area = context.area
        if area is None or area.type != 'VIEW_3D':
            return {'CANCELLED'}
        if context.region is None or context.region.type != 'WINDOW':
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            if region is None:
                return {'CANCELLED'}
            with context.temp_override(area=area, region=region):
                return bpy.ops.home_builder.move_backdrop('INVOKE_DEFAULT')
        level = _house_level(context)
        objs = backdrops_of(context.scene, level)
        self._level_uid = level.uid
        self._z = objs[0].location.z
        self._region = context.region
        self._rv3d = context.region_data
        self._from = None
        self._snap = None
        self._corners = wall_corners(context.scene)
        self._mouse = (event.mouse_region_x, event.mouse_region_y)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            self._draw, (context,), 'WINDOW', 'POST_PIXEL')
        context.window.cursor_set('CROSSHAIR')
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _target(self):
        """Where the mouse points: a wall corner near it, else the plane."""
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        best, best_d = None, SNAP_PX
        for p in self._corners:
            q = location_3d_to_region_2d(self._region, self._rv3d, p)
            if q is None:
                continue
            d = ((q.x - self._mouse[0]) ** 2 + (q.y - self._mouse[1]) ** 2) ** 0.5
            if d < best_d:
                best, best_d = p, d
        self._snap = best
        if best is not None:
            return Vector((best.x, best.y, self._z))
        return _plane_pick(self._region, self._rv3d, self._mouse, self._z)

    def _header(self, context):
        if self._from is None:
            text = "Move to Match: click a point on the plan (a corner of the house drawn on it)"
        else:
            text = "Move to Match: click where that point belongs - wall corners snap"
        context.area.header_text_set(text + "    (Esc / right-click to cancel)")

    def _end(self, context):
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None
        context.area.header_text_set(None)
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self._mouse = (event.mouse_region_x, event.mouse_region_y)
            if self._from is not None:
                self._target()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'TRACKPADPAN', 'TRACKPADZOOM'} or event.type.startswith('NUMPAD'):
            return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'PRESS':
            self._end(context)
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self._from is None:
                hit = _plane_pick(self._region, self._rv3d, self._mouse, self._z)
                if hit is not None:
                    self._from = hit
                    self._header(context)
                return {'RUNNING_MODAL'}
            to = self._target()
            if to is None:
                return {'RUNNING_MODAL'}
            level = hb_house.get_level(self._level_uid)
            move_by(context.scene, level, to.x - self._from.x, to.y - self._from.y)
            self._end(context)
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def _draw(self, context):
        if context.region != self._region:
            return
        import gpu
        from gpu_extras.batch import batch_for_shader
        from bpy_extras.view3d_utils import location_3d_to_region_2d
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        gpu.state.blend_set('ALPHA')
        shader.bind()
        pts = []
        if self._from is not None:
            a = location_3d_to_region_2d(self._region, self._rv3d, self._from)
            if a is not None:
                pts.append(tuple(a))
                gpu.state.line_width_set(2.0)
                shader.uniform_float("color", (1.0, 0.6, 0.1, 0.9))
                batch_for_shader(shader, 'LINES', {"pos": [tuple(a), tuple(self._mouse)]}).draw(shader)
                gpu.state.line_width_set(1.0)
        if self._snap is not None:
            q = location_3d_to_region_2d(self._region, self._rv3d, self._snap)
            if q is not None:
                shader.uniform_float("color", (0.2, 0.9, 0.4, 1.0))
                gpu.state.point_size_set(12.0)
                batch_for_shader(shader, 'POINTS', {"pos": [tuple(q)]}).draw(shader)
        if pts:
            shader.uniform_float("color", (1.0, 0.6, 0.1, 0.9))
            gpu.state.point_size_set(8.0)
            batch_for_shader(shader, 'POINTS', {"pos": pts}).draw(shader)
        gpu.state.blend_set('NONE')


class HOME_BUILDER_OT_remove_backdrop(bpy.types.Operator):
    """Remove the active level's backdrops"""
    bl_idname = "home_builder.remove_backdrop"
    bl_label = "Remove Backdrop"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        level = _house_level(context)
        return level is not None and bool(backdrops_of(context.scene, level))

    def execute(self, context):
        level = _house_level(context)
        objs = backdrops_of(context.scene, level)
        if context.object in objs:
            objs = [context.object]     # the selected one, when one is
        for obj in objs:
            img = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if img is not None and img.users == 0:
                bpy.data.images.remove(img)
        self.report({'INFO'}, f"Removed {len(objs)} backdrop{'s' if len(objs) != 1 else ''}.")
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_add_backdrop,
    HOME_BUILDER_OT_import_pdf_backdrop,
    HOME_BUILDER_FH_pdf_backdrop,
    HOME_BUILDER_OT_scale_backdrop,
    HOME_BUILDER_OT_apply_backdrop_scale,
    HOME_BUILDER_OT_move_backdrop,
    HOME_BUILDER_OT_remove_backdrop,
)


def register():
    global _PREVIEWS
    _PREVIEWS = bpy.utils.previews.new()
    for cls in classes:
        bpy.utils.register_class(cls)
    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)


def unregister():
    global _PREVIEWS
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if _PREVIEWS is not None:
        bpy.utils.previews.remove(_PREVIEWS)
        _PREVIEWS = None
    _THUMBS.clear()
