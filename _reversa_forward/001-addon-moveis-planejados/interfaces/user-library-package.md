# Contrato: Pacote de móvel pronto da biblioteca do usuário (incremento 2 — esboço)

> Feature `001-addon-moveis-planejados` · Requisitos RF-030..RF-036, RN-19, RN-23 · Status: **esboço**; detalhar no
> planejamento do incremento 2.

## Finalidade

Guardar móveis prontos criados pelo usuário e levá-los a outro computador.

## Local

`bpy.utils.extension_path_user(__package__, path="library", create=True)/<categoria>/<subcategoria>/<uid>/`

## Conteúdo de cada item

| Arquivo | Conteúdo |
|---|---|
| `item.blend` | Objetos do móvel (raiz + hierarquia), gravados com `bpy.data.libraries.write` |
| `item.json` | Metadados (abaixo) |
| `thumbnail.png` | Miniatura 256×256 |

`item.json`:

```json
{
  "schema": "blendertomob.library-item", "schema_version": 1,
  "uid": "…", "name": "Gaveteiro 4G", "description": "…", "category": ["Escritório", "Gaveteiros"],
  "line": "ESC", "library": "FRAMELESS",
  "external_mm": {"width": 450, "height": 720, "depth": 550},
  "keep_aggregate_overrides": true,
  "finish_by_component": {"Externo Caixas": "Cinza Fóssil"},
  "standard_uid_at_save": "8c1e…", "created_at": "…", "app_version": "…"
}
```

## Regras

- Inserção cria cópia independente com novo `btm_uid` (RN-19).
- Na inserção, materiais, espessuras, folgas e fitas vêm da definição ativa; medidas externas e composição vêm do item (RN-23, RF-036).
- Pacote de exportação = zip da pasta do item (ou de uma categoria); importação recusa `schema_version` maior que o suportado.
