"""Simulação gráfica da folha de porta (feature 003, T053; RF-17, D-20).

Com uma folha convertida ativa (a própria malha ou o pivô), desenha na viewport: o eixo de giro (ou o trilho do
correr), o caminho da borda livre do fechado até o máximo, a folha na posição atual e, se ela bateu, a caixa da folha
em vermelho com o nome do objeto. O handler fica registrado com o add-on e só desenha quando há folha ativa.
"""

import blf  # type: ignore
import bpy  # type: ignore
import gpu  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from gpu_extras.batch import batch_for_shader  # type: ignore

from . import leaf

PATH_COLOR = (0.2, 0.75, 1.0, 0.9)
AXIS_COLOR = (1.0, 0.8, 0.1, 1.0)
LEAF_COLOR = (0.2, 0.75, 1.0, 0.6)
HIT_COLOR = (1.0, 0.2, 0.2, 1.0)
ARC_STEPS = 24
_EDGES = ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7))
_handles = []


def _active_leaf(context):
    obj = context.active_object
    if obj is None:
        return None
    if obj.get('btm_leaf'):
        obj = bpy.data.objects.get(obj['btm_leaf'])
    agg = getattr(obj, 'btm_aggregate', None) if obj is not None else None
    if agg is None or not agg.is_aggregate or agg.kind != 'LEAF' or leaf.pivot_of(obj) is None:
        return None
    return obj


def _lines(shader, coords, color, width, region):
    if not coords:
        return
    batch = batch_for_shader(shader, 'LINES', {"pos": coords})
    shader.bind()
    shader.uniform_float("color", color)
    shader.uniform_float("lineWidth", width)
    shader.uniform_float("viewportSize", (region.width, region.height))
    batch.draw(shader)


def _box_lines(corners):
    return [corners[i] for edge in _EDGES for i in edge]


def _draw_3d():
    context = bpy.context
    obj = _active_leaf(context)
    region = context.region
    if obj is None or region is None:
        return
    from . import collision
    tester = collision.Tester(obj)
    agg = obj.btm_aggregate
    parent_world = agg.parent_ref.matrix_world
    base_world = parent_world @ tester.base
    # caminho da borda livre: o canto mais distante do eixo, do fechado ao máximo
    closed = tester.corners_at(0.0)
    far = max(range(8), key=lambda i: (closed[i] - base_world).length)
    path = [tester.corners_at(step / ARC_STEPS)[far] for step in range(ARC_STEPS + 1)]
    path_lines = [p for a, b in zip(path, path[1:]) for p in (a, b)]
    if agg.motion == 'SWING':
        axis_dir = parent_world.to_3x3() @ (leaf.pose_matrix(agg, tester.base, 0.0).to_3x3().col[
            2 if agg.hinge in ('LEFT', 'RIGHT') else 0])
        lo, hi = leaf.leaf_box(obj)
        size = (hi - lo).z if agg.hinge in ('LEFT', 'RIGHT') else (hi - lo).x
        axis_lines = [base_world, base_world + axis_dir.normalized() * size]
    else:
        axis_lines = [path[0], path[-1]]
    current = tester.corners_at(leaf.current_fraction(obj))
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    gpu.state.depth_test_set('NONE')
    gpu.state.blend_set('ALPHA')
    _lines(shader, path_lines, PATH_COLOR, 2.0, region)
    _lines(shader, axis_lines, AXIS_COLOR, 3.0, region)
    _lines(shader, _box_lines(current), HIT_COLOR if agg.contact_name else LEAF_COLOR,
           3.0 if agg.contact_name else 1.5, region)
    gpu.state.blend_set('NONE')


def _draw_2d():
    context = bpy.context
    obj = _active_leaf(context)
    region, rv3d = context.region, context.region_data
    if obj is None or region is None or rv3d is None or not obj.btm_aggregate.contact_name:
        return
    co = location_3d_to_region_2d(region, rv3d, obj.matrix_world.translation)
    if co is None:
        return
    text = f"Folha bateu em {obj.btm_aggregate.contact_name}"
    blf.size(0, 14)
    blf.color(0, 0.0, 0.0, 0.0, 0.85)
    blf.position(0, co.x + 11, co.y + 9, 0)
    blf.draw(0, text)
    blf.color(0, *HIT_COLOR)
    blf.position(0, co.x + 10, co.y + 10, 0)
    blf.draw(0, text)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW'))
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw_2d, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
