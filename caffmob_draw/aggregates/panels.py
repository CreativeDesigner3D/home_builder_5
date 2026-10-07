"""Painel do agregado e da folha de porta (feature 003, T054; RF-11 a RF-19).

Subpainel de "Propriedades" (`BTM_PT_object_properties`, feature 002): importar, converter e, para o objeto ativo
convertido, pai, face, posição com mínimo/máximo, afastamento, Perfurar, Furo real, Peça de produção; para a folha,
movimento, eixo, sentido, máximo ou curso, a barra de abertura e o aviso de batida.
"""

import bpy  # type: ignore

from ..data import units
from . import apply, leaf, limits, perforate


def _active_aggregate(context):
    obj = context.active_object
    if obj is not None and obj.get('btm_leaf'):
        obj = bpy.data.objects.get(obj['btm_leaf'])
    agg = getattr(obj, 'btm_aggregate', None) if obj is not None else None
    return obj if agg is not None and agg.is_aggregate else None


def _fmt(context, value):
    return units.format_value(value, context.scene)


def draw_aggregate(layout, context):
    row = layout.row(align=True)
    row.operator("caffmob.import_model", icon='IMPORT')
    col = layout.column(align=True)
    col.operator("caffmob.aggregate_convert", icon='LINKED')
    col.operator("caffmob.leaf_convert", icon='MOD_SIMPLEDEFORM')
    obj = _active_aggregate(context)
    if obj is None:
        layout.label(text="Selecione a malha e, por último, o elemento pai.", icon='INFO')
        return
    agg = obj.btm_aggregate
    box = layout.box()
    box.label(text=f"{obj.name} — pai: {agg.parent_ref.name if agg.parent_ref else '—'}", icon='OBJECT_DATA')
    if agg.kind == 'AGGREGATE':
        box.prop(agg, "face")
        box_p = apply.parent_box(obj)
        lim = limits.limits(box_p, tuple(agg.size), agg.face) if box_p else None
        for name in ('u', 'v'):
            row = box.row(align=True)
            row.prop(agg, name)
            if lim:
                row.label(text=f"{_fmt(context, lim[name][0])} a {_fmt(context, lim[name][1])}")
        row = box.row(align=True)
        row.prop(agg, "offset")
        if lim:
            row.label(text=f"mín. {_fmt(context, lim['offset'][0])}")
        box.operator("caffmob.aggregate_move", icon='VIEW_PAN')
        box.prop(agg, "perforate")
        row = box.row()
        reason = perforate.real_hole_reason(obj)
        row.enabled = agg.perforate and reason is None
        row.prop(agg, "real_hole")
        if agg.perforate and reason:
            box.label(text=reason, icon='INFO')
        box.prop(agg, "production_part")
        if agg.production_part:
            geometry = getattr(obj, 'btm_geometry', None)
            if geometry is not None:
                box.prop(geometry, "component")
                box.prop(geometry, "material")
    else:
        box.prop(agg, "motion", expand=True)
        if agg.motion == 'SWING':
            box.prop(agg, "hinge")
            box.prop(agg, "swing_sign")
            box.prop(agg, "max_angle")
        else:
            box.prop(agg, "slide_dir")
            box.prop(agg, "travel")
        box.prop(agg, "open_value", slider=True)
        if agg.contact_name:
            row = box.row()
            row.alert = True
            row.label(text=f"Folha bateu em {agg.contact_name}", icon='ERROR')
        if leaf.pivot_of(obj) is None:
            box.label(text="Pivô ausente; desconverta e converta de novo", icon='ERROR')
    layout.operator("caffmob.aggregate_unconvert", icon='UNLINKED')


class BTM_PT_Aggregate(bpy.types.Panel):
    bl_label = "Agregados e folhas"
    bl_idname = "BTM_PT_aggregate"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        draw_aggregate(self.layout, context)


classes = (BTM_PT_Aggregate,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
