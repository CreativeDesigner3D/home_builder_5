# Armadilhas da API do Blender que já afetam (ou podem afetar) o BlenderToMob

Resumo dirigido ao projeto das páginas `info_gotcha*.md`, `info_best_practice.md` e notas da referência 5.2.
Para o texto completo: `python3 docs/rag/tools/rag_search.py "<assunto>" --category guide --full`.

## Referências a dados que viram "lixo" (crash)

Fonte: `info_gotchas_crashes.md`.

- **Regra de ouro:** não guarde referências Python diretas a dados do Blender enquanto o *container* é modificado ou quando pode
  haver undo/redo (ex.: durante operadores modais). Guarde **nomes/índices** e busque de novo.
- `CollectionProperty.add()` pode realocar toda a coleção → referências a itens anteriores ficam inválidas.
- Após `bpy.data.objects.remove(obj, do_unlink=True)` (usado ~320x no projeto), qualquer uso de `obj` gera
  `ReferenceError: StructRNA of type Object has been removed`. Zere variáveis/atributos (`self.preview_obj = None`).
- Em Edit Mode, dados de `mesh.polygons`/`vertices` são realocados — use `bmesh.from_edit_mesh`.
- Operadores modais do projeto (posicionamento, portas/janelas, detalhes, escadas) devem reobter objetos pelo nome a cada evento
  se houver chance de undo (`Ctrl+Z`) no meio da operação.
- Para achar a linha que derruba o Blender: módulo `faulthandler` do Python.

## Undo

Fonte: `bpy.types.Operator.md`, `info_gotchas_crashes.md` ("Undo/Redo").

- Operador que altera dados **precisa** de `'UNDO'` em `bl_options`; sem isso o undo corrompe ou mistura passos.
- Retornar `{'CANCELLED'}` depois de já ter modificado dados = mudanças sem passo de undo. Desfaça antes ou retorne `{'FINISHED'}`.
- Undo recarrega os dados: objetos Python obtidos antes do undo ficam inválidos (mesma regra acima).

## Dados "velhos" após alterar valores

Fonte: `info_gotchas_internal_data_and_python_objects.md` ("Stale Data").

- Depois de mudar `location`, drivers, inputs de GN etc., `matrix_world`, bounding box e malha avaliada **não** são recalculados até
  `context.view_layer.update()`. Relevante para cotas, snapping e extração de peças (`cutting/part_extractor.py`).
- Mudanças de UI (`window.scene`, `area.type`, `window.workspace`) só têm efeito depois que o operador termina. Para agir depois,
  use operador modal, `bpy.app.handlers` ou `bpy.app.timers` (o projeto usa `timers.register(..., first_interval=0.0)` no catálogo).

## Operadores chamados por código (`bpy.ops.*`)

Fonte: `info_gotchas_operators.md`, `bpy.types.Context.md`.

- `bpy.ops` usa o **contexto**, não argumentos de dados; `poll()` falha com "context is incorrect" fora da área certa.
- Use `with context.temp_override(window=..., area=..., region=..., **keywords):` (padrão já usado em `viewport_hud.py`,
  `scene_navigator.py`, `hb_utils.py`).
- Prefira a API de dados em vez de operadores quando possível: `bpy.ops.object.select_all` (64x no repo) e `mode_set` são lentos
  e dependem de contexto; `obj.select_set(False)` em loop sobre `context.selected_objects` é mais previsível.
- Cada chamada `bpy.ops` pode empilhar undo e disparar redesenho; evite em loops grandes.

## Nomes de data-blocks

Fonte: `info_gotchas_internal_data_and_python_objects.md` ("Data Names").

- Nomes têm limite de tamanho e podem ser renomeados automaticamente (`Cabinet.001`). Depois de criar, use o objeto retornado
  (`obj = bpy.data.objects.new(...)`), **não** `bpy.data.objects["nome"]` com o nome que você pediu.
- Com bibliotecas linkadas, o mesmo nome pode existir local e na library: use a chave `(nome, caminho_da_lib)` quando importar.

## Threads

Fonte: `info_gotchas_threading.md`.

- Threads Python com `bpy` **derrubam o Blender** de formas difíceis de diagnosticar. Só são seguras se terminarem (`join()`)
  antes do script retornar, e nenhuma thread pode tocar `bpy` enquanto roda.
- Para trabalho pesado independente do Blender (ex.: otimização de nesting), use `multiprocessing` ou `subprocess` com dados
  serializados (JSON) e aplique o resultado no thread principal (timer ou modal).

## Caminhos de arquivo

Fonte: `info_gotchas_file_paths_and_encoding.md`.

- Caminhos relativos ao .blend começam com `//`; converta com `bpy.path.abspath(path)` antes de usar com `os`/`open` (o projeto usa).
- Salve dados do usuário em `bpy.utils.extension_path_user(__package__, path=..., create=True)`, nunca na pasta da extensão.

## Mesh / BMesh

Fonte: `info_gotchas_meshes.md`, `bmesh.md`.

- `bmesh.new()` sempre com `bm.free()` (use `try/finally`), exceto BMesh vindo de `from_edit_mesh`.
- Depois de `bm.to_mesh(me)`, chame `me.update()`; em Edit Mode, `bmesh.update_edit_mesh(me)`.
- Para operar sobre a malha avaliada (com modificadores/GN): `obj.evaluated_get(depsgraph).to_mesh()` e **sempre** `to_mesh_clear()`.

## Callbacks de propriedades

Fonte: `bpy.props.md`, `info_gotchas_crashes.md` ("Abusing RNA property callbacks").

- `update`/`get`/`set` podem rodar em threads e muitas vezes por redesenho; não crie/apague data-blocks nem chame `bpy.ops` dentro deles.
- Dois `set` que se escrevem mutuamente = loop infinito.
- `EnumProperty(items=callback)`: mantenha referência Python às strings retornadas (limitação conhecida documentada em `bpy.props.EnumProperty`).
