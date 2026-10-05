"""Arrastar o módulo só no plano da sua parede (T036; RF-34, D-17).

`btm.move_on_wall` (modal): o módulo segue o mouse ao longo da parede (X local); com Shift, sobe e desce (Z). O
afastamento da parede não muda. Com "Evitar Sobreposição" ligado, o módulo para no vizinho da mesma faixa de altura
e nas pontas da parede (`measure/cotas.slide`, `PlacementMixin.avoid_overlap`). As cotas anterior, posterior,
inferior e superior são desenhadas ao vivo pelo overlay de seleção (`overlays/selection_cotas.py`), porque o módulo
continua ativo e selecionado. Clique confirma (um passo de desfazer); Esc ou botão direito volta à posição original.
"""

import bpy  # type: ignore
from bpy_extras import view3d_utils  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.geometry import intersect_line_plane  # type: ignore

from ..data import units
from ..measure import cotas, scene_cotas


def _module_cotas(context):
    obj = context.active_object
    mc = scene_cotas.for_object(obj, context.scene) if obj is not None else None
    return mc if mc is not None and mc.on_wall else None


class BTM_OT_MoveOnWall(bpy.types.Operator):
    """Arrasta o módulo ao longo da parede em que ele está, sem afastá-lo dela (Shift: altura)"""
    bl_idname = "btm.move_on_wall"
    bl_label = "Mover na Parede"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.area is not None and context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'
                and _module_cotas(context) is not None)

    def invoke(self, context, event):
        self.mc = _module_cotas(context)
        self.original = self.mc.root.location.copy()
        self.grab = self._wall_point(context, event)
        if self.grab is None:
            self.report({'WARNING'}, "Não foi possível projetar o mouse na parede.")
            return {'CANCELLED'}
        self.start = self.mc.placement
        context.window_manager.modal_handler_add(self)
        self._header(context)
        return {'RUNNING_MODAL'}

    def _wall_point(self, context, event):
        """Ponto do mouse no plano da frente do módulo, no referencial da parede."""
        # Também chamado pelo botão do painel lateral: usa sempre a região principal da viewport.
        region = next((r for r in context.area.regions if r.type == 'WINDOW'), None)
        rv3d = context.area.spaces.active.region_3d
        if region is None or rv3d is None:
            return None
        mouse = (event.mouse_x - region.x, event.mouse_y - region.y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse)
        vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse)
        matrix = self.mc.wall.matrix_world
        front_y = self.mc.placement.back_y - self.mc.depth
        point = matrix @ Vector((0.0, front_y, 0.0))
        normal = (matrix.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        hit = intersect_line_plane(origin, origin + vector * 1.0e6, point, normal)
        return matrix.inverted() @ hit if hit is not None else None

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            self.mc.root.location = self.original
            return self._end(context, {'CANCELLED'})
        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            return self._end(context, {'FINISHED'})
        if event.type == 'MOUSEMOVE':
            point = self._wall_point(context, event)
            if point is not None:
                self._move(context, point, event.shift)
        return {'RUNNING_MODAL'}

    def _move(self, context, point, vertical):
        from ..hb_placement import PlacementMixin
        start, current = self.start, self.mc.placement
        if vertical:
            new = current._replace(z0=max(0.0, start.z0 + point.z - self.grab.z))
        else:
            target = start.x0 + point.x - self.grab.x
            x0 = cotas.slide(current, self.mc.obstacles(), self.mc.wall_length, target,
                             PlacementMixin.avoid_overlap(context))
            new = current._replace(x0=x0)
        self.mc.root.location = (new.x0, new.back_y, new.z0)
        self.mc.placement = new
        self._header(context)

    def _header(self, context):
        values = self.mc.compute()
        unit = units.get_scene_length_unit()
        fmt = lambda v: units.format_length(v, unit) if v is not None else "—"  # noqa: E731
        context.area.header_text_set(
            f"Anterior {fmt(values.anterior)} | Posterior {fmt(values.posterior)} | Inferior {fmt(values.inferior)} | "
            "Shift: altura | Clique confirma | Esc cancela")

    def _end(self, context, result):
        context.area.header_text_set(None)
        return result


classes = (BTM_OT_MoveOnWall,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
