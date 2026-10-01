import bpy

# Cache de identificadores de entrada resolvidos por grupo de nós de geometria.
_INPUT_IDENT_CACHE = {}

# Blender 5.2.0+ alterou o acesso aos inputs de modificadores de Geometry Nodes.
# Em 5.2.0+: mod.properties.inputs[identifier].value
# Em < 5.2.0: mod[identifier]
GN_INPUTS_AS_RNA = bpy.app.version >= (5, 2, 0)


def _cache_key(node_group):
    """Chave estável do grupo de nós para o cache de identificadores.

    `ID.session_uid` não muda com renomeações nem realocações (referência
    da API 5.2 em docs/rag: página do tipo ID, membro session_uid);
    `id()` do wrapper Python pode ser reciclado e só fica como reserva.
    """
    return getattr(node_group, 'session_uid', 0) or id(node_group)


def _get_input_identifier(node_group, input_name):
    """Retorna o identificador do socket do modificador para um determinado input_name.
    Usa um cache na memória para evitar chamar interface_update repetidamente.
    """
    group_cache = _INPUT_IDENT_CACHE.get(_cache_key(node_group))
    if group_cache is not None:
        ident = group_cache.get(input_name)
        if ident is not None:
            return ident
    else:
        group_cache = {}
        _INPUT_IDENT_CACHE[_cache_key(node_group)] = group_cache

    if input_name not in node_group.interface.items_tree:
        raise ValueError(f"Input '{input_name}' não encontrado no Geometry Nodes")

    # Garante que a interface do modificador está atualizada com o grupo de nós
    if hasattr(node_group, 'interface_update'):
        node_group.interface_update(bpy.context)

    ident = node_group.interface.items_tree[input_name].identifier
    group_cache[input_name] = ident
    return ident


def _invalidate_input_cache(node_group):
    """Limpa o cache de identificadores do grupo de nós."""
    _INPUT_IDENT_CACHE.pop(_cache_key(node_group), None)


# Nomes públicos usados pela camada legada (hb_types, hb_utils): um único cache por grupo de nós.
get_input_identifier = _get_input_identifier
invalidate_input_cache = _invalidate_input_cache


# -----------------------------------------------------------------------------
# Acesso por IDENTIFICADOR do socket (ex.: "Socket_2"), usado pela camada legada.
# Não chama update_tag(): quem escreve decide quando reavaliar.
# -----------------------------------------------------------------------------

def get_gn_input_by_id(mod, identifier):
    """Lê o valor de um input de Geometry Nodes pelo identificador do socket."""
    if GN_INPUTS_AS_RNA:
        return getattr(mod.properties.inputs, identifier).value
    return mod[identifier]


def set_gn_input_by_id(mod, identifier, value):
    """Escreve o valor de um input de Geometry Nodes pelo identificador do socket."""
    if GN_INPUTS_AS_RNA:
        getattr(mod.properties.inputs, identifier).value = value
    else:
        mod[identifier] = value


def try_get_gn_input_by_id(mod, identifier, default=None):
    """Como get_gn_input_by_id, mas devolve `default` se o input não existir ou não tiver valor."""
    if not identifier:
        return default
    if GN_INPUTS_AS_RNA:
        item = getattr(mod.properties.inputs, identifier, None)
        return getattr(item, 'value', default) if item is not None else default
    return mod.get(identifier, default)


def gn_input_ui_ref_by_id(mod, identifier):
    """Par (dono, propriedade) para layout.prop() de um input, ou None se não for desenhável."""
    if GN_INPUTS_AS_RNA:
        item = getattr(mod.properties.inputs, identifier, None)
        if item is None or not hasattr(item, 'value'):
            return None
        return item, 'value'
    if identifier not in mod.keys():
        return None
    return mod, '["%s"]' % identifier


def gn_input_data_path_by_id(mod, identifier):
    """Caminho de dados (driver_add / path_resolve) de um input pelo identificador do socket."""
    if GN_INPUTS_AS_RNA:
        return 'modifiers["%s"].properties.inputs.%s.value' % (mod.name, identifier)
    return 'modifiers["%s"]["%s"]' % (mod.name, identifier)


def try_get_gn_input(mod, input_name, default=None):
    """Lê um input pelo NOME do socket; devolve `default` se o grupo ou o input não existirem."""
    if not mod or not mod.node_group:
        return default
    try:
        return get_gn_input(mod, input_name)
    except (ValueError, KeyError, AttributeError):
        return default


def get_gn_input(mod, input_name):
    """Lê de forma compatível o valor de uma entrada (socket) de um modificador de Geometry Nodes."""
    if not mod or not mod.node_group:
        return None
    try:
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            return getattr(mod.properties.inputs, ident).value
        return mod[ident]
    except (KeyError, AttributeError):
        _invalidate_input_cache(mod.node_group)
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            return getattr(mod.properties.inputs, ident).value
        return mod[ident]


def set_gn_input(mod, input_name, value):
    """Escreve de forma compatível um valor em uma entrada (socket) de um modificador de Geometry Nodes."""
    if not mod or not mod.node_group:
        return
    try:
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            getattr(mod.properties.inputs, ident).value = value
        else:
            mod[ident] = value
    except (KeyError, AttributeError):
        _invalidate_input_cache(mod.node_group)
        ident = _get_input_identifier(mod.node_group, input_name)
        if GN_INPUTS_AS_RNA:
            getattr(mod.properties.inputs, ident).value = value
        else:
            mod[ident] = value
    # Tag de atualização do objeto para reavaliação no depsgraph
    mod.id_data.update_tag()


def gn_input_data_path(mod, input_name):
    """Retorna o caminho de dados (data path) de animação/driver para uma entrada do Geometry Nodes."""
    if not mod or not mod.node_group:
        return ""
    ident = _get_input_identifier(mod.node_group, input_name)
    if GN_INPUTS_AS_RNA:
        return f'modifiers["{mod.name}"].properties.inputs.{ident}.value'
    return f'modifiers["{mod.name}"]["{ident}"]'


def get_builtin_shader(name_3d='UNIFORM_COLOR', name_2d='2D_UNIFORM_COLOR'):
    """Retorna o shader builtin de forma compatível entre Blender 3.6, 4.x e 5.x."""
    import gpu
    try:
        return gpu.shader.from_builtin(name_3d)
    except Exception:
        try:
            return gpu.shader.from_builtin(name_2d)
        except Exception:
            return gpu.shader.from_builtin('UNIFORM_COLOR')

