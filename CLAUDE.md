# BlenderToMob — instruções para agentes

Extensão do Blender para marcenaria paramétrica e projeto de interiores (inspirada no Promob, herdeira do Home Builder).
Este arquivo vale para Claude Code, Codex, Kilo e demais agentes (`AGENTS.md` é um link simbólico para ele).

## Onde editar

- **`blendertomob/` é o pacote da extensão** — é o que `build.py` empacota. Edite sempre aqui.
- Os `*.py`, `operators/`, `product_libraries/` etc. na **raiz** são uma cópia antiga espelhada: não edite, não empacotam.
- `_reversa_sdd/` contém specs de domínio/arquitetura (geradas pelo Reversa); consulte para regras de negócio.
- Não versionar: `*.blend`, `blendertomob.zip`, `blender_python_reference_*.zip`, `manual-treinamento-promob.pdf`.

## API do Blender: consulte o RAG, não a memória

Alvo: **Blender 5.2** (a API muda entre versões; assinaturas "de memória" costumam estar erradas).
A referência completa + guia do projeto está em [`docs/rag/`](docs/rag/README.md).

1. Antes de usar `bpy`, `bmesh`, `gpu`, `blf`, `mathutils` ou `bpy_extras`, leia o arquivo relevante de `docs/rag/project/`:
   - `00_visao_geral.md` — estrutura, convenções, mapa tarefa → código → referência
   - `02_padroes_blender_5_2.md` — receitas verificadas (operador, props, handlers, modal+GPU, raycast, BMesh, drivers)
   - `03_compatibilidade_5x.md` — mudanças 5.0/5.2 (inputs de Geometry Nodes, `bpy.props`, shaders builtin)
   - `04_armadilhas.md` — crashes, undo, dados desatualizados, threads, contexto
2. Confirme cada assinatura:
   ```bash
   python3 docs/rag/tools/rag_search.py --symbol bpy.types.Scene.ray_cast
   python3 docs/rag/tools/rag_search.py "draw handler POST_PIXEL" -k 5
   ```
3. Depois de editar `blendertomob/`, rode o verificador — `[UNKNOWN in 5.2]` é erro:
   ```bash
   python3 docs/rag/tools/check_api.py
   ```
4. Ao justificar uma escolha de API, cite `docs/rag/blender-api/corpus/<página>.md#<símbolo>`.

## Regras do código

- Diferenças entre versões do Blender ficam em `blendertomob/compat.py` (via `bpy.app.version`), nunca espalhadas.
- Inputs de Geometry Nodes: use `compat.get_gn_input` / `set_gn_input` / `gn_input_data_path` — nunca `mod["Socket_X"]`
  (caminho < 5.2). `hb_utils.py` tem helpers duplicados: mantenha os dois em sincronia ou consolide em `compat.py`.
- Propriedades `bpy.props` são lidas por atributo (`obj.btm_cabinet.width`), nunca por `obj["..."]` (armazenamento separado desde o 5.0).
- Operadores que alteram dados: `bl_options = {'REGISTER', 'UNDO'}` (ou `{'UNDO'}`). Código novo usa `bl_idname` `btm.*` ou `blendertomob.*`.
- Anotações `bpy.props` levam `# type: ignore` (convenção do repo para o Pyright).
- Todo `draw_handler_add` / `modal_handler_add` / `load_post.append` tem remoção correspondente em todos os caminhos de saída e no `unregister()`.
- Handlers de aplicação usam `@persistent`; `unregister()` desfaz tudo que `register()` fez (propriedades em `bpy.types.*` inclusive).
- Arquivos do usuário: `bpy.utils.extension_path_user(__package__, path=..., create=True)`.
- Sem threads tocando `bpy`; trabalho pesado vai para `subprocess`/`multiprocessing` e o resultado é aplicado no thread principal.
- Textos de UI e comentários novos em **português**. Estilo: ruff (`line-length = 120`, regras E/W/F).

## Comandos

```bash
ruff check blendertomob/                             # lint
python3 docs/rag/tools/check_api.py                  # compatibilidade com a API 5.2
blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py   # teste de fumaça no Blender
python3 build.py                                     # gera blendertomob.zip (Edit → Preferences → Get Extensions → Install from Disk)
```

Regenerar o RAG (nova versão da referência): ver "Regenerar" em [`docs/rag/README.md`](docs/rag/README.md).
