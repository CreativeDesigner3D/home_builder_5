"""Personalização gravada no objeto (feature 003, T007; data-delta §1, D-03).

`Object.btm_custom` fica no **vão** (opening cage), que sobrevive à reconstrução das frentes, ou na **peça**
(`material`). Campo vazio = segue a biblioteca, como antes da feature. `interior` guarda o pedido de divisões
internas do vão (JSON de `spec.Interior`), para a reconstrução da biblioteca não voltar ao padrão dela.
"""

import bpy  # type: ignore

from . import spec

PULL_POSITION_ITEMS = [
    ('DEFAULT', "Padrão", "Posição definida pela biblioteca"),
    ('TOP', "Topo", "Puxador perto da borda de cima"),
    ('MIDDLE', "Meio", "Puxador no meio da frente"),
    ('BOTTOM', "Base", "Puxador perto da borda de baixo"),
    ('SIDE', "Lateral", "Puxador na lateral livre da frente"),
]
GROUP_ITEMS = [(g, spec.GROUP_LABELS[g], "") for g in spec.GROUPS]


class BTM_PG_GroupMaterial(bpy.types.PropertyGroup):
    group: bpy.props.EnumProperty(name="Grupo", items=GROUP_ITEMS)  # type: ignore
    material: bpy.props.StringProperty(name="Material")  # type: ignore


class BTM_PG_CustomSpec(bpy.types.PropertyGroup):
    door_style: bpy.props.StringProperty(name="Estilo da porta", description="Vazio = estilo do módulo")  # type: ignore
    drawer_style: bpy.props.StringProperty(
        name="Estilo da gaveta", description="Vazio = estilo do módulo")  # type: ignore
    pull_model: bpy.props.StringProperty(
        name="Puxador", description="Nome do puxador; vazio = puxador do projeto")  # type: ignore
    pull_position: bpy.props.EnumProperty(name="Posição do puxador", items=PULL_POSITION_ITEMS,
                                          default='DEFAULT')  # type: ignore
    pull_all_fronts: bpy.props.BoolProperty(
        name="Aplicar a todas as frentes", description="Usa o mesmo puxador em todas as frentes do módulo",
        default=False)  # type: ignore
    front_material: bpy.props.StringProperty(name="Material das frentes")  # type: ignore
    material: bpy.props.StringProperty(name="Material da peça", description="Vence o material do grupo")  # type: ignore
    group_materials: bpy.props.CollectionProperty(type=BTM_PG_GroupMaterial)  # type: ignore
    interior: bpy.props.StringProperty(
        name="Divisões internas",
        description="JSON {shelves, dividers, drawers, heights}; vazio = interior da biblioteca")  # type: ignore

    def group_material(self, group):
        for item in self.group_materials:
            if item.group == group:
                return item.material
        return ""

    def set_group_material(self, group, material):
        for item in self.group_materials:
            if item.group == group:
                item.material = material
                return
        item = self.group_materials.add()
        item.group, item.material = group, material


classes = (BTM_PG_GroupMaterial, BTM_PG_CustomSpec)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.btm_custom = bpy.props.PointerProperty(type=BTM_PG_CustomSpec)


def unregister():
    if hasattr(bpy.types.Object, 'btm_custom'):
        del bpy.types.Object.btm_custom
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
