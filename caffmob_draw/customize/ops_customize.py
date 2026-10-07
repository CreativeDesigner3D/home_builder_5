"""Operadores de personalização do módulo selecionado (feature 003, T030; RF-02 a RF-06).

Todos com desfazer. O vão é endereçado pelo caminho estável do adaptador (`bay0/opening1`); o pedido fica em
`btm_custom` (vão, peça ou raiz) e o adaptador aplica pela própria biblioteca (D-02, D-03).
"""

import bpy  # type: ignore

from ..data import units
from . import adapters, reapply, spec
from .props import PULL_POSITION_ITEMS

_ENUM_CACHE = {}      # mantém vivas as strings dos enums dinâmicos (exigência da API de enums dinâmicos)


def _target(context):
    root, adapter = adapters.for_object(context.active_object)
    return root, adapter


def _opening(root, adapter, path):
    for item_path, obj in adapter.openings(root):
        if item_path == path:
            return obj
    return None


def _report(op, messages, ok_text):
    if messages:
        op.report({'WARNING'}, " | ".join(messages))
    else:
        op.report({'INFO'}, ok_text)


def _front_items(self, context):
    root, adapter = _target(context)
    allowed = adapter.front_types(root) if adapter else []
    items = [(f, spec.FRONT_LABELS[f], "") for f in spec.FRONT_TYPES if f in allowed]
    _ENUM_CACHE['front'] = items
    return items


def _style_items(self, context):
    root, adapter = _target(context)
    names = adapter.style_names() if adapter else []
    items = [("", "Estilo do módulo", "Volta ao estilo da biblioteca")] + [(n, n, "") for n in names]
    _ENUM_CACHE['style'] = items
    return items


def _pull_items(self, context):
    root, adapter = _target(context)
    pulls = adapter.pull_items() if adapter else []
    items = ([("", "Puxador do projeto", "Usa a escolha geral do projeto"), (spec.NO_PULL, "Sem puxador", "")]
             + [(key, label, "") for key, label in pulls])
    _ENUM_CACHE['pull'] = items
    return items


class _OpeningOperator:
    bl_options = {'REGISTER', 'UNDO'}

    path: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    @classmethod
    def poll(cls, context):
        root, adapter = _target(context)
        return adapter is not None and hasattr(adapter, 'openings')

    def resolve(self, context):
        root, adapter = _target(context)
        opening = _opening(root, adapter, self.path) if adapter else None
        if opening is None:
            self.report({'WARNING'}, "Vão não encontrado; selecione o módulo de novo")
        return root, adapter, opening


class BTM_OT_CustomizeSetFront(_OpeningOperator, bpy.types.Operator):
    """Troca a frente deste vão (porta, gavetas, basculante, painel ou vazio)"""
    bl_idname = "caffmob.customize_set_front"
    bl_label = "Trocar frente"

    front: bpy.props.EnumProperty(name="Frente", items=_front_items)  # type: ignore
    drawer_count: bpy.props.IntProperty(name="Gavetas", default=1, min=1, max=spec.MAX_DRAWERS)  # type: ignore

    def invoke(self, context, event):
        if self.front == 'DRAWERS':
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def execute(self, context):
        root, adapter, opening = self.resolve(context)
        if opening is None:
            return {'CANCELLED'}
        messages = adapter.set_front(context, root, opening, self.front, self.drawer_count)
        messages += reapply.reapply(context, root)
        _report(self, messages, f"Frente trocada para {spec.FRONT_LABELS[self.front]}")
        return {'FINISHED'}


class BTM_OT_CustomizeSetStyle(_OpeningOperator, bpy.types.Operator):
    """Aplica um estilo só nas frentes deste vão"""
    bl_idname = "caffmob.customize_set_style"
    bl_label = "Estilo da frente"

    kind: bpy.props.EnumProperty(items=[('DOOR', "Porta", ""), ('DRAWER', "Gaveta", "")])  # type: ignore
    style: bpy.props.EnumProperty(name="Estilo", items=_style_items)  # type: ignore

    def execute(self, context):
        root, adapter, opening = self.resolve(context)
        if opening is None:
            return {'CANCELLED'}
        if self.kind == 'DOOR':
            opening.btm_custom.door_style = self.style
        else:
            opening.btm_custom.drawer_style = self.style
        _report(self, reapply.reapply(context, root), f"Estilo aplicado: {self.style or 'do módulo'}")
        return {'FINISHED'}


class BTM_OT_CustomizeSetPull(_OpeningOperator, bpy.types.Operator):
    """Troca o puxador das frentes deste vão (ou de todas as frentes do módulo)"""
    bl_idname = "caffmob.customize_set_pull"
    bl_label = "Puxador"

    model: bpy.props.EnumProperty(name="Modelo", items=_pull_items)  # type: ignore
    position: bpy.props.EnumProperty(name="Posição", items=PULL_POSITION_ITEMS)  # type: ignore
    all_fronts: bpy.props.BoolProperty(name="Aplicar a todas as frentes", default=False)  # type: ignore

    def invoke(self, context, event):
        root, adapter, opening = self.resolve(context)
        if opening is not None:
            custom = opening.btm_custom
            self.position = custom.pull_position
            self.all_fronts = root.btm_custom.pull_all_fronts
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        root, adapter, opening = self.resolve(context)
        if opening is None:
            return {'CANCELLED'}
        root.btm_custom.pull_all_fronts = self.all_fronts
        if self.all_fronts:
            root.btm_custom.pull_model = self.model
            for _path, other in adapter.openings(root):
                other.btm_custom.pull_position = self.position
        else:
            opening.btm_custom.pull_model = self.model
            opening.btm_custom.pull_position = self.position
        _report(self, reapply.reapply(context, root), "Puxador atualizado")
        return {'FINISHED'}


class BTM_OT_CustomizeSetMaterial(bpy.types.Operator):
    """Escolhe o material das frentes de um vão, de um grupo de peças ou da peça selecionada"""
    bl_idname = "caffmob.customize_set_material"
    bl_label = "Material"
    bl_options = {'REGISTER', 'UNDO'}

    target: bpy.props.EnumProperty(items=[('FRONTS', "Frentes do vão", ""), ('GROUP', "Grupo", ""),
                                          ('PART', "Peça selecionada", "")])  # type: ignore
    path: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    group: bpy.props.EnumProperty(items=[(g, spec.GROUP_LABELS[g], "") for g in spec.GROUPS])  # type: ignore
    material: bpy.props.StringProperty(name="Material", description="Vazio = volta ao material da biblioteca")  # type: ignore

    @classmethod
    def poll(cls, context):
        return _target(context)[1] is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop_search(self, "material", bpy.data, "materials")

    def execute(self, context):
        root, adapter = _target(context)
        if self.target == 'FRONTS':
            opening = _opening(root, adapter, self.path)
            if opening is None:
                return {'CANCELLED'}
            opening.btm_custom.front_material = self.material
        elif self.target == 'GROUP':
            root.btm_custom.set_group_material(self.group, self.material)
        else:
            context.active_object.btm_custom.material = self.material
        _report(self, reapply.reapply(context, root), f"Material: {self.material or 'da biblioteca'}")
        return {'FINISHED'}


class BTM_OT_CustomizeSetInterior(_OpeningOperator, bpy.types.Operator):
    """Prateleiras, divisórias e gavetas internas deste vão"""
    bl_idname = "caffmob.customize_set_interior"
    bl_label = "Divisões internas"

    shelves: bpy.props.IntProperty(name="Prateleiras", min=0, max=spec.MAX_SHELVES)  # type: ignore
    dividers: bpy.props.IntProperty(name="Divisórias", min=0, max=spec.MAX_DIVIDERS)  # type: ignore
    drawers: bpy.props.IntProperty(name="Gavetas internas", min=0, max=spec.MAX_DRAWERS)  # type: ignore
    heights: bpy.props.StringProperty(
        name="Alturas", description="Alturas das prateleiras a partir da base do vão, separadas por ';' "
        "(na unidade da cena). Vazio = espaçamento igual")  # type: ignore

    def invoke(self, context, event):
        root, adapter, opening = self.resolve(context)
        if opening is not None:
            current = adapter.read(root).opening(self.path)
            inner = current.interior if current and current.interior else spec.Interior()
            self.shelves, self.dividers, self.drawers = inner.shelves, inner.dividers, inner.drawers
            unit = units.get_scene_length_unit(context.scene)
            self.heights = "; ".join(units.format_length(h, unit=unit) for h in inner.heights)
        return context.window_manager.invoke_props_dialog(self)

    def _heights(self, context):
        unit = units.get_scene_length_unit(context.scene)
        return [units.parse_length(raw.strip(), default_unit=unit) for raw in self.heights.split(";") if raw.strip()]

    def execute(self, context):
        root, adapter, opening = self.resolve(context)
        if opening is None:
            return {'CANCELLED'}
        try:
            heights = self._heights(context)
        except ValueError:
            self.report({'WARNING'}, "Alturas inválidas")
            return {'CANCELLED'}
        inner = spec.Interior(self.shelves, self.dividers, self.drawers, heights)
        messages = adapter.set_interior(context, root, opening, inner)
        if not messages:
            messages = reapply.reapply(context, root)
        _report(self, messages, "Divisões internas atualizadas")
        return {'FINISHED'}


class BTM_OT_CustomizeClear(_OpeningOperator, bpy.types.Operator):
    """Volta estilo, puxador e material deste vão aos da biblioteca"""
    bl_idname = "caffmob.customize_clear"
    bl_label = "Limpar personalização do vão"

    def execute(self, context):
        root, adapter, opening = self.resolve(context)
        if opening is None:
            return {'CANCELLED'}
        custom = opening.btm_custom
        custom.door_style = custom.drawer_style = custom.pull_model = custom.front_material = ""
        custom.pull_position = 'DEFAULT'
        self.report({'INFO'}, "Personalização do vão removida; troque o estilo do projeto para refazer as frentes")
        return {'FINISHED'}


classes = (BTM_OT_CustomizeSetFront, BTM_OT_CustomizeSetStyle, BTM_OT_CustomizeSetPull, BTM_OT_CustomizeSetMaterial,
           BTM_OT_CustomizeSetInterior, BTM_OT_CustomizeClear)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
