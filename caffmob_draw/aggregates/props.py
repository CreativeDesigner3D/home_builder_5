"""Dados do agregado e da folha de porta convertida (feature 003, T008; data-delta §1, D-12 a D-19).

Os `update` delegam para os módulos de aplicação (import tardio). `_guard` evita recursão quando a aplicação
grava de volta o valor ajustado ao limite (RN-08).
"""

import bpy  # type: ignore

from . import limits

_guard = set()

FACE_ITEMS = [(f, limits.FACE_LABELS[f], "") for f in limits.FACES]
KIND_ITEMS = [('AGGREGATE', "Agregado", "Peça presa ao pai"), ('LEAF', "Folha de porta", "Folha que abre e fecha")]
MOTION_ITEMS = [('SWING', "Giro", "A folha gira em torno de um eixo"),
                ('SLIDE', "Correr", "A folha desliza num trilho")]
HINGE_ITEMS = [('LEFT', "Esquerda", ""), ('RIGHT', "Direita", ""), ('TOP', "Topo", ""), ('BOTTOM', "Base", "")]
SWING_ITEMS = [('OUT', "Para fora", "Abre para o lado da frente"), ('IN', "Para dentro", "Abre para o lado de trás")]
SLIDE_ITEMS = [('POS_X', "Para a direita", ""), ('NEG_X', "Para a esquerda", "")]


def _guarded(name, func):
    def update(self, context):
        obj = self.id_data
        key = (obj.name, name)
        if key in _guard:
            return
        _guard.add(key)
        try:
            func(obj, context)
        finally:
            _guard.discard(key)
    return update


def _position(obj, context):
    from . import apply
    apply.update_position(obj)


def _perforate(obj, context):
    from . import perforate
    perforate.sync(obj)


def _production(obj, context):
    from . import production
    production.sync(obj)


def _open(obj, context):
    from . import leaf
    leaf.update_open(obj, context)


def _leaf_setup(obj, context):
    from . import leaf
    leaf.rebuild_pivot(obj)


class BTM_PG_Aggregate(bpy.types.PropertyGroup):
    is_aggregate: bpy.props.BoolProperty(default=False)  # type: ignore
    kind: bpy.props.EnumProperty(name="Tipo", items=KIND_ITEMS, default='AGGREGATE')  # type: ignore
    parent_ref: bpy.props.PointerProperty(name="Pai", type=bpy.types.Object)  # type: ignore
    face: bpy.props.EnumProperty(name="Face", items=FACE_ITEMS, default='NEG_Y',
                                 update=_guarded('face', _position))  # type: ignore
    u: bpy.props.FloatProperty(name="Horizontal", subtype='DISTANCE', unit='LENGTH',
                               update=_guarded('u', _position))  # type: ignore
    v: bpy.props.FloatProperty(name="Vertical", subtype='DISTANCE', unit='LENGTH',
                               update=_guarded('v', _position))  # type: ignore
    offset: bpy.props.FloatProperty(
        name="Afastamento", subtype='DISTANCE', unit='LENGTH',
        description="Positivo afasta do pai; negativo afunda no pai até a espessura dele",
        update=_guarded('offset', _position))  # type: ignore
    perforate: bpy.props.BoolProperty(
        name="Perfurar", description="Recorta o pai no volume em que o agregado afunda (só no 3D)",
        update=_guarded('perforate', _perforate))  # type: ignore
    real_hole: bpy.props.BoolProperty(
        name="Furo real no plano de corte",
        description="Leva o recorte para a usinagem da peça pai no plano de corte e na exportação de produção",
        update=_guarded('real_hole', _perforate))  # type: ignore
    production_part: bpy.props.BoolProperty(
        name="Peça de produção", description="O agregado entra na lista de peças do plano de corte",
        update=_guarded('production_part', _production))  # type: ignore
    cutter: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    orig_parent: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    orig_matrix: bpy.props.FloatVectorProperty(size=16)  # type: ignore
    size: bpy.props.FloatVectorProperty(size=3, subtype='XYZ', unit='LENGTH')  # type: ignore
    rest_offset: bpy.props.FloatVectorProperty(size=3)  # type: ignore
    # Folha de porta
    motion: bpy.props.EnumProperty(name="Movimento", items=MOTION_ITEMS, default='SWING',
                                   update=_guarded('motion', _leaf_setup))  # type: ignore
    hinge: bpy.props.EnumProperty(name="Eixo", items=HINGE_ITEMS, default='LEFT',
                                  update=_guarded('hinge', _leaf_setup))  # type: ignore
    swing_sign: bpy.props.EnumProperty(name="Sentido", items=SWING_ITEMS, default='OUT',
                                       update=_guarded('swing_sign', _open))  # type: ignore
    max_angle: bpy.props.FloatProperty(name="Ângulo máximo", default=90.0, min=1.0, max=180.0,
                                       update=_guarded('max_angle', _open))  # type: ignore
    slide_dir: bpy.props.EnumProperty(name="Sentido", items=SLIDE_ITEMS, default='POS_X',
                                      update=_guarded('slide_dir', _leaf_setup))  # type: ignore
    travel: bpy.props.FloatProperty(name="Curso", default=0.5, min=0.001, subtype='DISTANCE', unit='LENGTH',
                                    update=_guarded('travel', _open))  # type: ignore
    open_value: bpy.props.FloatProperty(
        name="Abertura", min=0.0, max=1.0, subtype='FACTOR',
        description="0 = fechada; 1 = abertura máxima. Para ao encostar em parede ou objeto",
        update=_guarded('open_value', _open))  # type: ignore
    contact_name: bpy.props.StringProperty(name="Encostou em")  # type: ignore
    pivot: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore


classes = (BTM_PG_Aggregate,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_aggregate = bpy.props.PointerProperty(type=BTM_PG_Aggregate)


def unregister():
    if hasattr(bpy.types.Object, 'btm_aggregate'):
        del bpy.types.Object.btm_aggregate
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
