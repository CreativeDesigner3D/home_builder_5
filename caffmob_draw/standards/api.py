"""API do Padrão de Dimensões (T015).

Leitura e escrita de valores por chave do esquema, definição ativa da cena principal, rascunho do Configurador,
lista de pendências e validação ("Valor Inválido" — RN-06). Valores em mm (unidade do esquema).
"""

import uuid

from ..data import dimension_schema as schema
from ..data import units
from . import builtin


class StandardsError(Exception):
    """Erro de uso do Padrão de Dimensões (mensagem em português, pronta para o usuário)."""


# ----------------------------------------------------------------------------------------------------------------
# Cena principal e definições
# ----------------------------------------------------------------------------------------------------------------

def main_scene(scene=None):
    """Cena que guarda o padrão do projeto (hb_project.get_main_scene; reserva: a cena dada)."""
    try:
        from .. import hb_project
        main = hb_project.get_main_scene()
    except Exception:
        main = None
    return main or scene


def standards(scene=None):
    target = main_scene(scene)
    return getattr(target, 'btm_standards', None) if target else None


def ensure_ready(scene=None):
    """Garante as definições embutidas e um índice ativo válido. Devolve `Scene.btm_standards`."""
    data = standards(scene)
    if data is None:
        raise StandardsError("Padrão de Dimensões indisponível nesta cena.")
    builtin.ensure_builtins(data)
    if data.active_index >= len(data.definitions):
        data.active_index = 0
    return data


def active_definition(scene=None):
    data = standards(scene)
    if data is None or not len(data.definitions):
        return None
    index = min(data.active_index, len(data.definitions) - 1)
    return data.definitions[index]


def find_definition(scene, uid=None, name=None):
    data = standards(scene)
    if data is None:
        return None
    for definition in data.definitions:
        if (uid and definition.uid == uid) or (name and definition.name == name):
            return definition
    return None


def set_active(scene, definition):
    data = standards(scene)
    for index, item in enumerate(data.definitions):
        if item.as_pointer() == definition.as_pointer():
            data.active_index = index
            return
    raise StandardsError("Definição não encontrada.")


def new_uid():
    return uuid.uuid4().hex


def unique_name(scene, base):
    data = standards(scene)
    names = {d.name for d in data.definitions} if data else set()
    if base not in names:
        return base
    index = 2
    while f"{base} ({index})" in names:
        index += 1
    return f"{base} ({index})"


def copy_values(source, target):
    target.values.clear()
    for item in source.values:
        new = target.values.add()
        new.name = item.name
        new.value = item.value
        new.text = item.text
        new.is_text = item.is_text


def duplicate_definition(scene, definition, name=None):
    """Cópia editável (USER) da definição, que passa a ser a ativa."""
    data = standards(scene)
    # `add()` pode realocar a coleção: guarda o índice da origem e busca os itens de novo (RAG 04_armadilhas).
    source_index = next(i for i, d in enumerate(data.definitions) if d.as_pointer() == definition.as_pointer())
    data.definitions.add()
    definition = data.definitions[source_index]
    new = data.definitions[len(data.definitions) - 1]
    new.uid = new_uid()
    new.name = unique_name(scene, name or f"{definition.name} - cópia")
    new.builtin = False
    new.market = definition.market
    new.source = 'USER'
    new.version = 1
    new.updated_at = builtin.now_iso()
    copy_values(definition, new)
    for attr in definition.raw_attributes:
        raw = new.raw_attributes.add()
        raw.attr_id, raw.value, raw.key = attr.attr_id, attr.value, attr.key
    set_active(scene, new)
    return new


def remove_definition(scene, definition):
    if definition.builtin:
        raise StandardsError("Definições embutidas não podem ser excluídas.")
    data = standards(scene)
    for index, item in enumerate(data.definitions):
        if item.as_pointer() == definition.as_pointer():
            data.definitions.remove(index)
            data.active_index = min(data.active_index, max(len(data.definitions) - 1, 0))
            return
    raise StandardsError("Definição não encontrada.")


# ----------------------------------------------------------------------------------------------------------------
# Valores
# ----------------------------------------------------------------------------------------------------------------

def _raw_value(item):
    return item.text if item.is_text else item.value


def get_definition_value(definition, key):
    """Valor da chave na definição; se faltar, o padrão do esquema para o mercado da definição."""
    item = definition.values.get(key)
    if item is not None:
        return _raw_value(item)
    param = schema.get_param(key)
    if param is None:
        raise StandardsError(f"Parâmetro desconhecido: {key}")
    return param.default(definition.market)


def get_value(scene, key, definition=None):
    definition = definition or active_definition(scene)
    if definition is None:
        param = schema.get_param(key)
        return param.default('BR') if param else None
    return get_definition_value(definition, key)


def get_value_m(scene, key, definition=None):
    """Valor numérico convertido para metros (unidade interna do Blender)."""
    return float(get_value(scene, key, definition)) / 1000.0


def definition_values(definition):
    """Dicionário chave → valor com todos os parâmetros do esquema (faltantes = padrão do mercado)."""
    values = {key: param.default(definition.market) for key, param in schema.PARAMS.items()}
    for item in definition.values:
        values[item.name] = _raw_value(item)
    return values


def _write(collection, key, value):
    param = schema.get_param(key)
    if param is None:
        raise StandardsError(f"Parâmetro desconhecido: {key}")
    ok, message = schema.validate(param, value)
    if not ok:
        raise StandardsError(message)
    item = collection.get(key)
    if item is None:
        item = collection.add()
        item.name = key
    if param.type == 'ENUM':
        item.is_text = True
        item.text = str(value)
    else:
        item.is_text = False
        item.value = float(value)


def set_value(definition, key, value):
    if definition.builtin:
        raise StandardsError("Definições embutidas são somente leitura: duplique para editar.")
    _write(definition.values, key, value)


def set_values(definition, values):
    """Grava vários valores; valida tudo antes de gravar (nada é aplicado parcialmente — RN-06)."""
    errors = []
    for key, value in values.items():
        param = schema.get_param(key)
        if param is None:
            errors.append(f"Parâmetro desconhecido: {key}")
            continue
        ok, message = schema.validate(param, value)
        if not ok:
            errors.append(message)
    if errors:
        raise StandardsError("\n".join(errors))
    for key, value in values.items():
        set_value(definition, key, value)


# ----------------------------------------------------------------------------------------------------------------
# Rascunho do Configurador (D-16)
# ----------------------------------------------------------------------------------------------------------------

def user_unit(scene=None):
    return units.get_scene_length_unit(scene)


def format_param_value(param, value, unit='MM'):
    """Texto do valor para a interface (unidade do usuário, vírgula decimal)."""
    if param.type == 'ENUM':
        return str(value)
    return units.format_length(float(value) / 1000.0, unit)


def begin_draft(scene, window_manager):
    """Copia a definição ativa para o rascunho e monta a árvore. Devolve o rascunho."""
    ensure_ready(scene)
    definition = active_definition(scene)
    draft = window_manager.btm_standards_draft
    draft.definition_uid = definition.uid
    draft.definition_name = definition.name
    draft.error = ""
    draft.include_manual = False
    copy_values(definition, draft)
    builtin.fill_from_schema(draft, definition.market)
    rebuild_tree(draft)
    return draft


def set_draft_value(draft, key, value):
    _write(draft.values, key, value)


def draft_definition(scene, draft):
    return find_definition(scene, uid=draft.definition_uid)


def pending_changes(scene, draft):
    """Lista de alterações do rascunho em relação à definição: dicts com chave, rótulo, antes e depois."""
    definition = draft_definition(scene, draft)
    if definition is None:
        return []
    unit = user_unit(scene)
    changes = []
    for item in draft.values:
        param = schema.get_param(item.name)
        if param is None:
            continue
        new = _raw_value(item)
        old = get_definition_value(definition, item.name)
        same = (new == old) if param.type == 'ENUM' else abs(float(new) - float(old)) < 1e-6
        if not same:
            changes.append({
                'key': item.name,
                'label': f"{schema.line_label(param.line) if param.line != 'GLOBAL' else 'Medidas Máximas'} › "
                         f"{_component_label(param)}{param.label_pt}",
                'old': format_param_value(param, old, unit),
                'new': format_param_value(param, new, unit),
            })
    return changes


def _component_label(param):
    if param.component:
        return f"{schema.COMPONENTS_BY_CODE[param.component].label_pt} › "
    return ""


def apply_draft(scene, draft, include_manual=False):
    """Grava o rascunho na definição (versão +1) e sincroniza os módulos. Devolve o relatório da sincronização."""
    definition = draft_definition(scene, draft)
    if definition is None:
        raise StandardsError("A definição do rascunho não existe mais.")
    if definition.builtin:
        raise StandardsError("Definições embutidas são somente leitura: duplique para editar.")
    changes = pending_changes(scene, draft)
    if draft.definition_name and draft.definition_name != definition.name:
        definition.name = unique_name(scene, draft.definition_name)
    copy_values(draft, definition)
    if changes:
        definition.version += 1
        definition.updated_at = builtin.now_iso()
    from . import sync
    report = sync.apply_definition(scene, definition, include_manual=include_manual,
                                   changed_keys=[c['key'] for c in changes])
    report['changes'] = changes
    return report


# ----------------------------------------------------------------------------------------------------------------
# Árvore e edição (usados pela interface)
# ----------------------------------------------------------------------------------------------------------------

def expanded_paths(draft):
    return {p for p in (draft.expanded or "").split('|') if p}


def toggle_group(draft, path):
    paths = expanded_paths(draft)
    paths.symmetric_difference_update({path})
    draft.expanded = '|'.join(sorted(paths))
    rebuild_tree(draft)


def rebuild_tree(draft):
    """Árvore: Medidas Máximas; por linha → Dimensões Externas, Chapas (componentes), Componentes.

    Só os filhos dos grupos abertos (`draft.expanded`) entram na lista; com busca, tudo o que casa fica aberto.
    """
    draft.tree.clear()
    search = (draft.search or "").strip().lower()
    opened = expanded_paths(draft)

    def is_open(path):
        return bool(search) or path in opened

    def add(label, node_type, depth, path, key=""):
        item = draft.tree.add()
        item.label, item.node_type, item.depth, item.path, item.key = label, node_type, depth, path, key

    def matches(param):
        return not search or search in param.label_pt.lower() or search in param.key.lower() or (
            param.component and search in schema.COMPONENTS_BY_CODE[param.component].label_pt.lower())

    params = [p for p in schema.params_for(group=schema.GROUP_MAX) if matches(p)]
    if params:
        add("Medidas Máximas", 'GROUP', 0, "MAX")
        if is_open("MAX"):
            for p in params:
                add(p.label_pt, 'PARAM', 1, "MAX", p.key)
    for line, line_pt, _line_en in schema.LINES:
        ext = [p for p in schema.params_for(line=line, group=schema.GROUP_EXTERNAL) if matches(p)]
        sheet_params = {c.code: [p for p in schema.params_for(line=line, component=c.code) if matches(p)]
                        for c in schema.COMPONENTS}
        if not ext and not any(sheet_params.values()):
            continue
        add(line_pt, 'GROUP', 0, line)
        if not is_open(line):
            continue
        if ext:
            path = f"{line}/EXT"
            add("Dimensões Externas", 'GROUP', 1, path)
            if is_open(path):
                for p in ext:
                    add(p.label_pt, 'PARAM', 2, path, p.key)
        for tree_name, title in ((schema.TREE_SHEETS, "Chapas"), (schema.TREE_COMPONENTS, "Componentes")):
            comps = [c for c in schema.COMPONENTS if c.tree == tree_name and sheet_params[c.code]]
            if not comps:
                continue
            tree_path = f"{line}/{tree_name}"
            add(title, 'GROUP', 1, tree_path)
            if not is_open(tree_path):
                continue
            for comp in comps:
                comp_path = f"{tree_path}/{comp.code}"
                add(comp.label_pt, 'GROUP', 2, comp_path)
                if is_open(comp_path):
                    for p in sheet_params[comp.code]:
                        add(p.label_pt, 'PARAM', 3, comp_path, p.key)
    draft['_suppress'] = True
    try:
        draft.tree_index = min(draft.tree_index, max(len(draft.tree) - 1, 0))
    finally:
        del draft['_suppress']


def activate_tree_row(draft, scene=None):
    """Clique numa linha da árvore: grupo abre/fecha; parâmetro é selecionado para edição."""
    if draft.get('_suppress') or not (0 <= draft.tree_index < len(draft.tree)):
        return
    item = draft.tree[draft.tree_index]
    if item.node_type == 'GROUP':
        toggle_group(draft, item.path)
    else:
        select_param(draft, item.key, scene)


def tree_image_key(draft):
    """Imagem de referência do item ativo da árvore (parâmetro selecionado ou componente do grupo)."""
    param = schema.get_param(draft.selected_key)
    if param is not None:
        return param.image_key
    return ""


def select_param(draft, key, scene=None):
    """Seleciona o parâmetro para edição e preenche o campo com o valor atual na unidade do usuário."""
    param = schema.get_param(key)
    if param is None:
        return
    draft.selected_key = key
    draft.error = ""
    item = draft.values.get(key)
    value = _raw_value(item) if item is not None else param.default('BR')
    if param.type == 'ENUM':
        draft['_suppress'] = True
        try:
            draft.edit_enum = str(value)
        finally:
            del draft['_suppress']
    else:
        draft['_suppress'] = True
        try:
            draft.edit_text = format_param_value(param, value, user_unit(scene))
        finally:
            del draft['_suppress']


def commit_edit_text(draft):
    """Callback do campo de texto: interpreta a medida digitada, valida e grava no rascunho."""
    if draft.get('_suppress'):
        return
    param = schema.get_param(draft.selected_key)
    if param is None or param.type == 'ENUM':
        return
    try:
        meters = units.parse_length(draft.edit_text, user_unit(), allow_negative=param.negative_allowed)
        set_draft_value(draft, param.key, round(meters * 1000.0, 4))
        draft.error = ""
    except (ValueError, StandardsError) as exc:
        draft.error = str(exc)


_ENUM_ITEMS_CACHE = {}


def edit_enum_items(draft):
    """Itens do enum do parâmetro selecionado, com cache das strings (evita coleta de lixo pelo Blender)."""
    param = schema.get_param(draft.selected_key)
    options = param.enum_items if param is not None and param.type == 'ENUM' else ('-',)
    if options not in _ENUM_ITEMS_CACHE:
        _ENUM_ITEMS_CACHE[options] = [(o, o, "") for o in options]
    return _ENUM_ITEMS_CACHE[options]


def commit_edit_enum(draft):
    if draft.get('_suppress'):
        return
    param = schema.get_param(draft.selected_key)
    if param is None or param.type != 'ENUM':
        return
    try:
        set_draft_value(draft, param.key, draft.edit_enum)
        draft.error = ""
    except StandardsError as exc:
        draft.error = str(exc)
