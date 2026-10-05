"""Destaque das interferências no viewport (T073; D-29).

Desenha uma cruz vermelha em cada ponto de choque (`POST_VIEW`) e o rótulo "frente × objeto" (`POST_PIXEL`) a partir
de `WindowManager.btm_inspection.interferences`. Os dois handlers são adicionados no `register()` e removidos no
`unregister()`; sem interferências registradas, não desenham nada.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore
from mathutils import Vector  # type: ignore

COLOR = (0.95, 0.15, 0.1, 1.0)
CROSS = 0.04   # m

_handles = []


def _items():
    wm = bpy.context.window_manager
    state = getattr(wm, 'btm_inspection', None) if wm else None
    return list(state.interferences) if state is not None else []


def _draw_3d():
    items = _items()
    if not items:
        return
    region = bpy.context.region
    coords = []
    for item in items:
        p = Vector(item.location)
        for axis in (Vector((CROSS, 0, 0)), Vector((0, CROSS, 0)), Vector((0, 0, CROSS))):
            coords.extend((p - axis, p + axis))
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", COLOR)
    shader.uniform_float("lineWidth", 3.0)
    shader.uniform_float("viewportSize", (region.width, region.height))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _draw_2d():
    items = _items()
    if not items:
        return
    context = bpy.context
    region, rv3d = context.region, context.region_data
    if region is None or rv3d is None:
        return
    font_id = 0
    blf.size(font_id, 13)
    for item in items:
        co = location_3d_to_region_2d(region, rv3d, Vector(item.location))
        if co is None:
            continue
        text = f"{item.front_name} × {item.hit_name}"
        blf.color(font_id, 0.0, 0.0, 0.0, 0.85)
        blf.position(font_id, co.x + 9, co.y + 7, 0)
        blf.draw(font_id, text)
        blf.color(font_id, *COLOR)
        blf.position(font_id, co.x + 8, co.y + 8, 0)
        blf.draw(font_id, text)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW'))
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_2d, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
