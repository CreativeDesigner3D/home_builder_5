"""Cotas desenhadas ao selecionar um módulo (T024; D-12, RF-25).

Com um módulo (ou peça/frente dele) ativo, desenha no 3D as cotas de RN-04: anterior e posterior ao longo da parede,
inferior até o piso e superior até o teto, com o mesmo desenho das cotas de posicionamento
(`hb_placement.draw_placement_dimensions`). Módulo livre: só inferior e superior. O handler `POST_PIXEL` é adicionado
no `register()` e removido no `unregister()`.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

_handles = []


class _Specs:
    """Portador das cotas no formato que `draw_placement_dimensions` lê."""

    def __init__(self, specs):
        self._placement_dim_specs = specs


def _specs(context):
    from ..data import units
    from ..hb_placement import PlacementDimSpec
    from ..measure import cotas as cotas_mod
    from ..measure import scene_cotas
    obj = context.active_object
    if obj is None or not obj.select_get():
        return []
    mc = scene_cotas.for_object(obj, context.scene)
    if mc is None:
        return []
    values = mc.compute()
    p = mc.placement
    specs = []
    if mc.on_wall:
        matrix = mc.wall.matrix_world
        y = p.back_y - mc.depth        # frente do módulo
        z_mid = p.z0 + p.height / 2.0
        left, right = cotas_mod.limits(p, mc.obstacles(), mc.wall_length)
        if values.anterior and values.anterior > 1e-4:
            specs.append(PlacementDimSpec(matrix @ Vector((left, y, z_mid)), matrix @ Vector((p.x0, y, z_mid)),
                                          units.format_value(values.anterior)))
        if values.posterior and values.posterior > 1e-4:
            x1 = p.x0 + p.width
            specs.append(PlacementDimSpec(matrix @ Vector((x1, y, z_mid)), matrix @ Vector((right, y, z_mid)),
                                          units.format_value(values.posterior)))
        x_mid = p.x0 + p.width / 2.0
        base, top, floor, ceiling = ((x_mid, y, p.z0), (x_mid, y, p.z0 + p.height), (x_mid, y, 0.0),
                                     (x_mid, y, mc.ceiling))
        to_world = [matrix @ Vector(v) for v in (base, top, floor, ceiling)]
    else:
        root = mc.root
        center = root.matrix_world.translation
        base_z, top_z = p.z0, p.z0 + p.height
        to_world = [Vector((center.x, center.y, base_z)), Vector((center.x, center.y, top_z)),
                    Vector((center.x, center.y, 0.0)), Vector((center.x, center.y, mc.ceiling))]
    base, top, floor, ceiling = to_world
    if values.inferior and values.inferior > 1e-4:
        specs.append(PlacementDimSpec(floor, base, units.format_value(values.inferior)))
    if values.superior and values.superior > 1e-4:
        specs.append(PlacementDimSpec(top, ceiling, units.format_value(values.superior)))
    return specs


def _draw():
    context = bpy.context
    settings = getattr(context.scene, 'btm_settings', None)
    if settings is not None and not settings.show_dimensions:
        return
    try:
        specs = _specs(context)
    except (ReferenceError, AttributeError, ValueError):
        return
    if specs:
        from ..hb_placement import draw_placement_dimensions
        draw_placement_dimensions(_Specs(specs), context)


def register():
    if not _handles:
        _handles.append(bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL'))


def unregister():
    while _handles:
        bpy.types.SpaceView3D.draw_handler_remove(_handles.pop(), 'WINDOW')
