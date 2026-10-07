"""Adaptadores de personalização por biblioteca (feature 003, T019; D-02).

Mesmo padrão de `inspection/adapters/`: cada módulo expõe
- `LIBRARY`: 'FRAMELESS' | 'FACE_FRAME' | 'CLOSETS' | 'BTM' (valores de `selection.classify`);
- `capabilities(root)` → {seção: None (suportada) ou motivo}, e `front_types(root)` → frentes aceitas;
- `openings(root)` → [(caminho, objeto do vão)] em ordem estável;
- `read(root)` → `spec.Spec` com o estado atual (biblioteca + `btm_custom`);
- `set_front(context, root, opening, front, drawer_count)`, `set_interior(context, root, opening, interior)`:
  mudanças estruturais pela própria biblioteca; devolvem mensagens (vazio = ok);
- `reapply(context, root)`: reaplica estilo, puxador e materiais gravados em `btm_custom` (D-03, D-04);
- `pull_items()`, `style_names()`: opções para a interface.
"""

from ...selection import classify


def _adapters():
    from . import btm, closets, face_frame, frameless
    return (frameless, face_frame, closets, btm)


def module_root(obj):
    """Raiz do módulo de qualquer biblioteca (o próprio objeto, uma peça, uma frente ou um vão dele)."""
    return classify.module_root(obj)[0] if obj is not None else None


def for_root(root):
    """Adaptador da biblioteca do módulo, ou None."""
    if root is None:
        return None
    library = classify.module_library(root)
    for adapter in _adapters():
        if adapter.LIBRARY == library:
            return adapter
    return None


def for_object(obj):
    root = module_root(obj)
    return root, for_root(root)
