"""Padrão de Dimensões (Configurador de Dimensões) — feature 001, incremento 1.

Fonte única de medidas externas, materiais, espessuras, limites de chapa e fitas de borda das linhas de produto
(RN-23, RN-24). Módulos:

- `model`: PropertyGroups (`Scene.btm_standards`, `WindowManager.btm_standards_draft`)
- `builtin`: definições embutidas "Padrão Brasil" e "Padrão EUA (HB5)"
- `api`: leitura, escrita, rascunho, pendências e validação
- `io_json` / `io_promob`: arquivos `.btmdim.json` e `DIMENSIONEXPORT`
- `sync`: propagação para as bibliotecas legadas
- `migration` / `previews`: migração em `load_post` e imagens de referência
"""

from . import migration, model, previews

# Submódulos com registro próprio, na ordem de registro.
_MODULES = [model, previews, migration]


def register():
    for module in _MODULES:
        module.register()


def unregister():
    for module in reversed(_MODULES):
        module.unregister()
