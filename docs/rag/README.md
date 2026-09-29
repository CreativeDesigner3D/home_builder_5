# RAG — Blender 5.2 Python API para o BlenderToMob

Base de conhecimento consultável (por pessoas e por agentes de IA) para desenvolver o BlenderToMob contra a
**Blender 5.2.2 LTS Python API**. Gerada a partir de `blender_python_reference_5_2.zip` (build Sphinx oficial da referência).

| Camada | Conteúdo | Tamanho |
|---|---|---|
| `project/` | Conhecimento **curado** do projeto: visão geral, mapa de API usada, padrões, compatibilidade 5.x, armadilhas | 5 arquivos |
| `blender-api/corpus/` | Referência completa convertida para Markdown, 1 arquivo por página, links internos preservados (`.md#símbolo`) | 2159 páginas |
| `blender-api/index/chunks.jsonl` | 7048 chunks prontos para busca/embedding (por seção/membro, ≤ 6000 caracteres, sem links) | ~12 MB |
| `blender-api/index/symbols.tsv` | 26 776 símbolos (`objects.inv`) → arquivo#âncora | — |
| `blender-api/index/pages.tsv`, `manifest.json` | Catálogo de páginas e metadados do build | — |
| `tools/` | `rag_search.py` (busca), `check_api.py` (verificador de compatibilidade), `build_rag.py` (gera tudo) | — |

## Comece por aqui

1. [`project/00_visao_geral.md`](project/00_visao_geral.md) — estrutura do repo, alvo de versão, convenções, mapa tarefa → código → referência.
2. [`project/02_padroes_blender_5_2.md`](project/02_padroes_blender_5_2.md) — receitas verificadas: operador com undo, PropertyGroup, handlers, modal + GPU, raycast, BMesh, depsgraph, libraries.load, drivers.
3. [`project/03_compatibilidade_5x.md`](project/03_compatibilidade_5x.md) — mudanças 5.0/5.2 que tocam o projeto (inputs de Geometry Nodes, `bpy.props` × custom properties, shaders).
4. [`project/04_armadilhas.md`](project/04_armadilhas.md) — crashes, undo, dados desatualizados, threads, contexto de operadores.
5. [`project/01_mapa_api_blendertomob.md`](project/01_mapa_api_blendertomob.md) — cada símbolo da API usado em `blendertomob/`, com contagem e link (gerado).

## Consultar

Só precisa de Python 3 (stdlib). Rode da raiz do repositório.

```bash
# Busca livre (BM25 + boost por símbolo/título; inclui project/*.md)
python3 docs/rag/tools/rag_search.py "draw handler POST_PIXEL"
python3 docs/rag/tools/rag_search.py "bmesh extrude face region" -k 3 --full

# Filtrar por área: bpy.types, bpy.ops, bpy.props, bpy.app, bmesh, gpu, gpu_extras, blf, mathutils, bpy_extras, guide, project, enum_items
python3 docs/rag/tools/rag_search.py "undo modal" --category guide

# Símbolo exato (assinatura + documentação do membro)
python3 docs/rag/tools/rag_search.py --symbol bpy.types.Scene.ray_cast
python3 docs/rag/tools/rag_search.py --symbol location_3d_to_region_2d     # sufixo também funciona

# Saída JSON (para pipelines/agentes)
python3 docs/rag/tools/rag_search.py "PointerProperty" --json -k 3
```

Sem ferramenta: `grep -rn "SpaceView3D.draw_handler_add" docs/rag/blender-api/corpus/` ou
`grep -P "^bpy.types.Object.matrix_world\t" docs/rag/blender-api/index/symbols.tsv`.

## Verificar código contra a 5.2

```bash
python3 docs/rag/tools/check_api.py                   # varre blendertomob/; exit 1 se usar API inexistente no 5.2
python3 docs/rag/tools/check_api.py blendertomob/operators/walls.py
python3 docs/rag/tools/check_api.py --map docs/rag/project/01_mapa_api_blendertomob.md   # regenera o mapa
```

## Protocolo para agentes de IA (Claude Code, Codex, Kilo…)

Ao escrever ou revisar código que toca `bpy`, `bmesh`, `gpu`, `blf`, `mathutils` ou `bpy_extras`:

1. **Contexto do projeto primeiro:** leia `project/00_visao_geral.md` e o arquivo de `project/` do tema.
2. **Não confie na memória para assinaturas.** Confirme cada chamada com `rag_search.py --symbol <nome>` ou busca livre.
   A API muda entre versões (ex.: inputs de GN no 5.2, armazenamento de `bpy.props` no 5.0, nomes de shaders builtin).
3. **Cite a fonte** (`docs/rag/blender-api/corpus/<página>.md#<símbolo>`) ao justificar uma escolha de API.
4. **Rode `check_api.py`** após editar arquivos em `blendertomob/`; trate `[UNKNOWN in 5.2]` como erro.
5. Diferenças entre versões vão para `blendertomob/compat.py` (com `bpy.app.version`), nunca espalhadas pelo código.
6. Validação em runtime: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py`.

## Usar com embeddings / vetor

`chunks.jsonl` já está no formato de ingestão — uma linha por chunk:

```json
{"id": "bpy.types.Operator#3", "page": "bpy.types.Operator", "title": "Operator(bpy_struct)",
 "category": "bpy.types", "heading": "Operator(bpy_struct) > Calling a File Selector", "anchor": "calling-a-file-selector",
 "symbols": [], "path": "corpus/bpy.types.Operator.md#calling-a-file-selector", "text": "[Operator(bpy_struct)] ..."}
```

Embede o campo `text`; guarde `path`/`symbols`/`category` como metadados para filtro e citação.
Os chunks de `project/*.md` não estão no JSONL (são lidos direto por `rag_search.py`); inclua-os na ingestão com peso maior.

## Regenerar

```bash
pip install beautifulsoup4 markdownify lxml        # lxml é opcional (acelera ~3x)
python3 docs/rag/tools/build_rag.py [caminho/blender_python_reference_X_Y.zip]   # ~4 min em 8 núcleos
python3 docs/rag/tools/check_api.py --map docs/rag/project/01_mapa_api_blendertomob.md
```

O build é determinístico e sobrescreve `blender-api/`. Para uma nova versão do Blender: gere o zip da referência, rode o build,
leia `blender-api/corpus/change_log.md` e atualize `project/03_compatibilidade_5x.md`. Os arquivos em `project/` (exceto o mapa)
são escritos à mão — revise-os a cada atualização.

## Limitações conhecidas

- A referência documenta a API estática; estruturas geradas em runtime (ex.: `NodesModifier.properties.inputs.<socket>`) e menus
  nativos de UI (`VIEW3D_MT_*`) não aparecem.
- `change_log.md` do zip cobre apenas **5.1 → 5.2**.
- `rag_search.py` é léxico (BM25): para perguntas conceituais sem nomes de API, tente sinônimos em inglês ou use `--category guide`.
