"""Pictures of catalog accessories for the accessory browser.

Nothing ships with the add-on: an accessory's picture is rendered from
its own 3D model the first time the browser shows it with pictures on,
and kept as a small PNG in the extension's user folder, so later
sessions only read the file. Rendering runs from a timer, one picture
per tick, so the panel never waits on it; a row shows its picture once
the file exists. Accessories with no model of their own have none.
"""

import os

import bpy
from mathutils import Matrix, Vector

from ...units import inch
from . import accessory_models

PX = 128
FOLDER = "accessory_thumbs"
# Bump to re-render every cached picture (a model or the look changed).
VERSION = 1

_queue = []         # codes waiting for a render, in the order asked
_failed = set()     # codes with no picture this session (no model / error)
_folder = None


def _base_package():
    return __package__.split('.product_libraries')[0]


def folder():
    global _folder
    if _folder is None:
        try:
            _folder = bpy.utils.extension_path_user(
                _base_package(), path=FOLDER, create=True)
        except Exception:
            import tempfile
            _folder = os.path.join(tempfile.gettempdir(),
                                   "home_builder_" + FOLDER)
            os.makedirs(_folder, exist_ok=True)
    return _folder


def _path(code):
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in code)
    return os.path.join(folder(), "%s_v%d.png" % (safe, VERSION))


def picture(item):
    """The PNG path for a catalog item's picture, or None while it is
    still to be rendered (it is queued) or when it has none."""
    code = item.get('code')
    if not code or code in _failed:
        return None
    path = _path(code)
    if os.path.exists(path):
        return path
    if code not in _queue:
        if not _queue and not bpy.app.background:
            bpy.app.timers.register(_tick, first_interval=0.05)
        _queue.append(code)
    return None


def _size(item):
    """(w, depth, h) in metres a model is built at for its picture."""
    params = item.get('model_params') or {}
    if not isinstance(params, dict):
        params = {}
    w = params.get('unit_width') or item.get('min_opening_w') or 15.0
    h = params.get('unit_height') or item.get('min_opening_h') or 20.0
    try:
        w, h = float(w), float(h)
    except (TypeError, ValueError):
        w, h = 15.0, 20.0
    return inch(w), inch(accessory_models.PULLOUT_DEFAULT_DEPTH), inch(h)


def render(item, path):
    """Render ``item``'s model to ``path``. False when it has none."""
    model = item.get('model')
    if not model:
        return False
    w, d, h = _size(item)
    obj = accessory_models.build_object(
        model, "HB_AccessoryThumb", w, d, h,
        item.get('model_params') or {})
    if obj is None:
        return False
    mesh = obj.data
    scene = bpy.data.scenes.new("HB_AccessoryThumb")
    cam_data = bpy.data.cameras.new("HB_AccessoryThumb")
    cam = bpy.data.objects.new("HB_AccessoryThumb_CAM", cam_data)
    try:
        scene.collection.objects.link(obj)
        scene.collection.objects.link(cam)
        pts = [Vector(c) for c in obj.bound_box]
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        center = (lo + hi) / 2.0
        # A three-quarter view from the front (-Y) and above.
        direction = Vector((0.55, -1.0, 0.6)).normalized()
        rot = direction.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        cam_data.type = 'ORTHO'
        # Every corner projected on the view plane sets the frame.
        inv = rot.inverted()
        corners = [inv @ (Vector((x, y, z)) - center)
                   for x in (lo.x, hi.x) for y in (lo.y, hi.y)
                   for z in (lo.z, hi.z)]
        span = max(max(abs(c.x) for c in corners),
                   max(abs(c.y) for c in corners)) * 2.0
        cam_data.ortho_scale = max(span * 1.08, 1e-3)
        cam_data.clip_start = 0.001
        cam_data.clip_end = 100.0
        cam.matrix_world = (Matrix.Translation(center + direction * 10.0)
                            @ rot)
        scene.camera = cam
        r = scene.render
        r.engine = 'BLENDER_WORKBENCH'
        r.resolution_x = r.resolution_y = PX
        r.resolution_percentage = 100
        r.film_transparent = True
        r.image_settings.file_format = 'PNG'
        r.image_settings.color_mode = 'RGBA'
        r.filepath = path
        scene.view_settings.view_transform = 'Standard'
        sh = scene.display.shading
        sh.light = 'STUDIO'
        sh.color_type = 'MATERIAL'
        sh.show_object_outline = True
        sh.object_outline_color = (0.15, 0.15, 0.15)
        scene.display.render_aa = '8'
        bpy.ops.render.render(write_still=True, scene=scene.name)
        return os.path.exists(path)
    finally:
        bpy.data.objects.remove(obj)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        bpy.data.objects.remove(cam)
        bpy.data.cameras.remove(cam_data)
        bpy.data.scenes.remove(scene)


def _tick():
    from ... import accessory_registry
    if not _queue:
        return None
    code = _queue.pop(0)
    item = accessory_registry.find(code)
    ok = False
    if item is not None:
        try:
            ok = render(item, _path(code))
        except Exception as ex:
            print("Home Builder: accessory picture %s failed: %s" % (code, ex))
    if not ok:
        _failed.add(code)
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    return 0.02 if _queue else None


def clear_queue():
    _queue.clear()
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
