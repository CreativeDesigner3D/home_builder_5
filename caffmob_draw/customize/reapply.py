"""Reaplicar a personalização depois que a biblioteca reconstrói frentes ou materiais (feature 003, T026; D-04).

As bibliotecas chamam `after_rebuild(context, obj)` no fim das operações que recriam frentes ou reatribuem materiais;
o adaptador relê `btm_custom` (vãos, peças e raiz) e reaplica estilo, puxador e materiais. Módulo sem personalização
sai sem custo.
"""

from . import adapters

_running = set()


def has_custom(root):
    if root.btm_custom.group_materials or root.btm_custom.pull_all_fronts:
        return True
    for obj in [root] + list(root.children_recursive):
        custom = getattr(obj, 'btm_custom', None)
        if custom is None:
            continue
        if (custom.door_style or custom.drawer_style or custom.pull_model or custom.pull_position != 'DEFAULT'
                or custom.front_material or custom.material or custom.interior):
            return True
    return False


def reapply(context, root):
    """Reaplica pelo adaptador da biblioteca; devolve a lista de avisos."""
    adapter = adapters.for_root(root)
    if adapter is None or root.name in _running:
        return []
    _running.add(root.name)
    try:
        return adapter.reapply(context, root)
    finally:
        _running.discard(root.name)


def after_rebuild(context, obj):
    """Gancho das bibliotecas: `obj` é a raiz ou qualquer objeto do módulo."""
    root = adapters.module_root(obj)
    if root is None or not hasattr(root, 'btm_custom') or not has_custom(root):
        return []
    return reapply(context, root)
