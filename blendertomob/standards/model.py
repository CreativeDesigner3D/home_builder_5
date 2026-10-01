"""PropertyGroups do Padrão de Dimensões (T013; data-delta §1).

Cada definição guarda os valores numa coleção genérica indexada pela chave do esquema
(`data/dimension_schema.py`), em **mm** (unidade do esquema) — o esquema dá a estrutura (linhas, dimensões
externas, chapas, componentes); a coleção dá os valores. Atributos importados não reconhecidos ficam em
`raw_attributes`, na ordem original, para reexportação sem perda.
"""

import bpy


class BTM_PG_StandardValue(bpy.types.PropertyGroup):
    """Valor de um parâmetro; `name` é a chave do esquema (ex.: "COZ.sheets.LAT.thickness")."""
    value: bpy.props.FloatProperty(name="Valor (mm)", default=0.0)  # type: ignore
    text: bpy.props.StringProperty(name="Valor (texto)", default="")  # type: ignore
    is_text: bpy.props.BoolProperty(name="É texto", default=False)  # type: ignore


class BTM_PG_RawAttribute(bpy.types.PropertyGroup):
    """Atributo de arquivo importado (Promob), preservado na ordem original."""
    attr_id: bpy.props.StringProperty(name="ID")  # type: ignore
    value: bpy.props.StringProperty(name="Valor original")  # type: ignore
    key: bpy.props.StringProperty(name="Chave mapeada", description="Vazio = não reconhecido")  # type: ignore


class BTM_PG_StandardDefinition(bpy.types.PropertyGroup):
    """Definição nomeada do Padrão de Dimensões (ex.: "Padrão Brasil", "ME MOVEIS - COZ. ESCR.")."""
    uid: bpy.props.StringProperty(name="Identificador")  # type: ignore
    builtin: bpy.props.BoolProperty(
        name="Embutida", description="Definição de fábrica, somente leitura (duplique para editar)",
        default=False)  # type: ignore
    market: bpy.props.EnumProperty(
        name="Mercado",
        items=[('BR', "Brasil", "Padrões brasileiros (mm, MDF 15/18)"),
               ('US', "EUA", "Padrões americanos herdados do Home Builder 5")],
        default='BR')  # type: ignore
    source: bpy.props.EnumProperty(
        name="Origem",
        items=[('BUILTIN', "Embutida", ""), ('USER', "Usuário", ""),
               ('PROMOB_IMPORT', "Importada do Promob", ""), ('MIGRATED', "Migrada", "")],
        default='USER')  # type: ignore
    version: bpy.props.IntProperty(name="Versão", default=1, min=1)  # type: ignore
    updated_at: bpy.props.StringProperty(name="Atualizada em")  # type: ignore
    values: bpy.props.CollectionProperty(type=BTM_PG_StandardValue)  # type: ignore
    raw_attributes: bpy.props.CollectionProperty(type=BTM_PG_RawAttribute)  # type: ignore


class BTM_PG_Standards(bpy.types.PropertyGroup):
    """Definições do projeto (vivem na cena principal; ver standards/api.py)."""
    definitions: bpy.props.CollectionProperty(type=BTM_PG_StandardDefinition)  # type: ignore
    active_index: bpy.props.IntProperty(name="Definição ativa", default=0, min=0)  # type: ignore
    schema_version: bpy.props.IntProperty(name="Versão do formato", default=1)  # type: ignore


class BTM_PG_StandardTreeItem(bpy.types.PropertyGroup):
    """Linha da árvore do Configurador (UIList)."""
    label: bpy.props.StringProperty()  # type: ignore
    node_type: bpy.props.EnumProperty(
        items=[('GROUP', "Grupo", ""), ('PARAM', "Parâmetro", "")], default='GROUP')  # type: ignore
    key: bpy.props.StringProperty(description="Chave do parâmetro (só para PARAM)")  # type: ignore
    depth: bpy.props.IntProperty(default=0)  # type: ignore
    path: bpy.props.StringProperty(description="Caminho do nó, ex.: COZ/CHAPAS/LAT")  # type: ignore


def _edit_text_update(self, context):
    from . import api
    api.commit_edit_text(self)


def _edit_enum_update(self, context):
    from . import api
    api.commit_edit_enum(self)


def _tree_index_update(self, context):
    from . import api
    api.activate_tree_row(self, context.scene)


def _search_update(self, context):
    from . import api
    api.rebuild_tree(self)


def _edit_enum_items(self, context):
    from . import api
    return api.edit_enum_items(self)


class BTM_PG_StandardsDraft(bpy.types.PropertyGroup):
    """Rascunho do Configurador (não salvo): cópia editável da definição ativa (D-16)."""
    definition_uid: bpy.props.StringProperty()  # type: ignore
    definition_name: bpy.props.StringProperty(name="Nome")  # type: ignore
    values: bpy.props.CollectionProperty(type=BTM_PG_StandardValue)  # type: ignore
    tree: bpy.props.CollectionProperty(type=BTM_PG_StandardTreeItem)  # type: ignore
    tree_index: bpy.props.IntProperty(default=0, update=_tree_index_update)  # type: ignore
    expanded: bpy.props.StringProperty(description="Caminhos dos grupos abertos, separados por |")  # type: ignore
    search: bpy.props.StringProperty(
        name="Buscar", description="Filtra parâmetros e componentes pelo nome", options={'TEXTEDIT_UPDATE'},
        update=_search_update)  # type: ignore
    selected_key: bpy.props.StringProperty()  # type: ignore
    edit_text: bpy.props.StringProperty(
        name="Valor", description="Digite a medida (aceita vírgula e mm/cm/m)",
        update=_edit_text_update)  # type: ignore
    edit_enum: bpy.props.EnumProperty(name="Valor", items=_edit_enum_items, update=_edit_enum_update)  # type: ignore
    error: bpy.props.StringProperty()  # type: ignore
    include_manual: bpy.props.BoolProperty(
        name="Incluir medidas manuais",
        description="Também substitui medidas editadas à mão nos módulos (RN-23)",
        default=False)  # type: ignore


classes = (
    BTM_PG_StandardValue,
    BTM_PG_RawAttribute,
    BTM_PG_StandardDefinition,
    BTM_PG_Standards,
    BTM_PG_StandardTreeItem,
    BTM_PG_StandardsDraft,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.btm_standards = bpy.props.PointerProperty(type=BTM_PG_Standards)
    bpy.types.WindowManager.btm_standards_draft = bpy.props.PointerProperty(type=BTM_PG_StandardsDraft)


def unregister():
    del bpy.types.WindowManager.btm_standards_draft
    del bpy.types.Scene.btm_standards
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
