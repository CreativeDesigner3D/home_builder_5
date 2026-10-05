"""Propriedades da geometria livre: `Object.btm_geometry` (T008; data-delta §1, D-18).

A geometria é um objeto de malha com `btm_plane.object_kind = 'GEOMETRY'`. As medidas ficam em `btm_geometry` e
qualquer mudança refaz a malha (`mesh.update`). A origem é o canto mínimo: a peça cresce em +X, +Y e +Z, de modo
que mudar a espessura não move a face de apoio (RF-12).

- **Placa:** largura × profundidade × altura, com a medida do eixo da espessura trocada por `thickness`
  (`plane`: deitada, em pé de frente ou em pé de lado).
- **Caixa:** sólido largura × profundidade × altura; na fabricação, vira seis placas com `thickness`.
"""

import bpy  # type: ignore

from ..data import dimension_schema as schema

KINDS = [('PLACA', "Placa", "Uma chapa"), ('CAIXA', "Caixa", "Uma caixa fechada de seis chapas")]
PLANES = [('XY', "Deitada", "Espessura na vertical (Z)"),
          ('XZ', "Em pé, de frente", "Espessura na profundidade (Y)"),
          ('YZ', "Em pé, de lado", "Espessura na largura (X)")]
COMPONENT_ITEMS = [(c.code, c.label_pt, "") for c in schema.COMPONENTS]
LIMIT_MIN, LIMIT_MAX = 0.001, 10.0


def _update(self, context):
    obj = self.id_data
    if isinstance(obj, bpy.types.Object) and obj.type == 'MESH':
        from . import mesh
        mesh.update(obj)


def _length(name, default, description=""):
    return bpy.props.FloatProperty(name=name, description=description, subtype='DISTANCE', unit='LENGTH',
                                   default=default, min=LIMIT_MIN, max=LIMIT_MAX, precision=1, update=_update)


class BTM_PG_GeometryProps(bpy.types.PropertyGroup):
    kind: bpy.props.EnumProperty(name="Forma", items=KINDS, default='PLACA', update=_update)  # type: ignore
    plane: bpy.props.EnumProperty(name="Posição da Placa", items=PLANES, default='XY', update=_update)  # type: ignore
    width: _length("Largura", 0.6)  # type: ignore
    depth: _length("Profundidade", 0.4)  # type: ignore
    height: _length("Altura", 0.4)  # type: ignore
    thickness: _length("Espessura", 0.018, "Espessura da placa; numa caixa, das seis placas")  # type: ignore
    fabrication: bpy.props.BoolProperty(
        name="Peça de Fabricação", default=False,
        description="Entra na lista de peças e no orçamento; sem a marca é só visual")  # type: ignore
    component: bpy.props.EnumProperty(name="Componente", items=COMPONENT_ITEMS, default='ESP')  # type: ignore
    material: bpy.props.StringProperty(name="Matéria-prima", default="MDF")  # type: ignore
    finish: bpy.props.StringProperty(name="Acabamento", default="")  # type: ignore


classes = (BTM_PG_GeometryProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_geometry = bpy.props.PointerProperty(type=BTM_PG_GeometryProps)


def unregister():
    if hasattr(bpy.types.Object, 'btm_geometry'):
        del bpy.types.Object.btm_geometry
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
