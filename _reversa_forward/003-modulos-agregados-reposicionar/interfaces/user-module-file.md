# Contrato: módulo salvo do usuário

> Feature: `003-modulos-agregados-reposicionar` · Decisões D-10, D-11 · Código: `caffmob_draw/customize/library_io.py`, `customize/manifest.py`

## Local

`bpy.utils.extension_path_user("caffmob_draw", path="modules/<categoria>", create=True)/`

Três arquivos com o mesmo nome base (nome digitado, sanitizado para o sistema de arquivos; o nome original fica no
manifesto):

| Arquivo | Conteúdo |
|---|---|
| `<nome>.blend` | Objetos do módulo e dependências, `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)` |
| `<nome>.png` | Miniatura 256 × 256 |
| `<nome>.json` | Manifesto (abaixo) |

## Manifesto

```json
{
  "format": "caffmob_draw.user-module",
  "schema_version": "1.0.0",
  "name": "Aéreo vidro 2P",
  "category": "Aéreos",
  "library": "FRAMELESS",
  "root_object": "Aéreo vidro 2P",
  "created": "2026-10-07T10:00:00-03:00",
  "addon_version": "x.y.z",
  "dimensions_mm": {"width": 800, "height": 700, "depth": 350},
  "styles": {"cabinet_style": "Carvalho", "door_styles": ["Vidro alumínio"]},
  "materials": ["Laca branca", "MDF carvalho"],
  "pulls": ["Perfil 160"],
  "spec": {
    "openings": [
      {"path": "bay0/opening0", "front": "DOUBLE_DOORS", "door_style": "Vidro alumínio",
       "pull_model": "Perfil 160", "pull_position": "BOTTOM", "front_material": "Laca branca",
       "interior": {"shelves": 2, "dividers": 0, "drawers": 0, "heights_mm": []}}
    ],
    "parts": [{"group": "CAIXA", "material": "MDF carvalho"}],
    "aggregates": [{"name": "Puxador importado", "parent_path": "bay0/opening0/door_L", "kind": "AGGREGATE"}]
  }
}
```

- `library`: `FRAMELESS` | `FACE_FRAME` | `CLOSETS` | `BTM` (valores de `selection.classify.LIBRARY_LABELS`).
- `path` de vão: caminho estável pela ordem dos filhos (`bay<i>/opening<j>`), não pelo nome do objeto.
- Estilos, materiais e puxadores sempre **por nome** (RN-06).

## Inserção

1. Lê o manifesto; formato ou `schema_version` maior desconhecido → aviso e nada é inserido.
2. Anexa o `.blend` e liga os objetos à cena.
3. Re-resolve nomes: estilo ausente no arquivo atual → usa o padrão da biblioteca e avisa (lista dos ausentes);
   material ausente → vem do próprio `.blend` salvo.
4. Reaplica o `spec` pelo adaptador da biblioteca e entra no posicionamento modal existente.

## Erros

| Situação | Comportamento |
|---|---|
| Nome já existe na categoria | Pergunta "Substituir o módulo existente?"; Não → nada é escrito (RF-08) |
| Falha ao gravar (`OSError`) | Relatório de erro com caminho e motivo; arquivos parciais removidos |
| `.blend` presente sem `.json` (grupos antigos) | Aparece na lista como "sem personalização"; inserido sem reaplicar `spec` |

## Idempotência

Salvar o mesmo módulo duas vezes com "Substituir" gera o mesmo manifesto, exceto `created`.
