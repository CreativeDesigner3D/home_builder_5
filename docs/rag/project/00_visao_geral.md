# Visão geral do BlenderToMob para quem consulta o RAG

Contexto mínimo do repositório para interpretar a referência da API do Blender 5.2 à luz deste código.

## Alvo de versão

- **Referência do RAG:** Blender **5.2.2 LTS** Python API (`docs/rag/blender-api/index/manifest.json`).
- **Manifesto da extensão:** `blender_manifest.toml` declara `blender_version_min = "4.2.0"`, mas o código já depende de APIs 5.x
  (ex.: `blendertomob/compat.py` usa `NodesModifier.properties`, adicionado no 5.2). Ao escrever código novo,
  **o alvo é 5.2**; se precisar manter 4.2–5.1, isole a diferença em `blendertomob/compat.py` com `bpy.app.version`.

## Onde está o código de verdade

| Caminho | Papel |
|---|---|
| `blendertomob/` | **Pacote da extensão** (é o que `build.py` empacota em `blendertomob.zip`). Edite aqui. |
| `*.py`, `operators/`, `product_libraries/`… na raiz | Cópia antiga/espelhada do pacote (herança do Home Builder). Não é empacotada. |
| `tests/blender_smoke.py` | Teste de fumaça que roda dentro do Blender (`blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py`). |
| `_reversa_sdd/` | Especificações/arquitetura geradas pelo Reversa (domínio, ERD, operadores, UI). Complementa este RAG no lado de negócio. |
| `docs/rag/` | Este RAG: referência da API 5.2 + conhecimento curado do projeto. |

## Fluxo de registro (`blendertomob/__init__.py`)

1. Hot-reload dos submódulos já importados (`importlib.reload`) para iterar sem reiniciar o Blender.
2. `register()` registra, em ordem: assets → `BTM_AddonPreferences` (`bl_idname = __package__`) → camada de dados moderna (`data`) → props legadas (`hb_props`, `hb_project`…) → operadores legados → operadores/UI/overlays modernos (`btm_operators`, `ui`, `overlays`) → UI legada → bibliotecas de produtos (closets, face_frame, frameless, wood_hoods, molding).
3. Handler `load_post` com `@persistent` (`load_file_post`): injeta `hb_driver_functions` em `bpy.app.driver_namespace`,
   garante a cena principal (`scene['IS_MAIN_SCENE']`), cria o estilo padrão frameless e **re-arma o HUD modal** (operadores modais não sobrevivem ao carregar um .blend).
4. `unregister()` faz o caminho inverso e remove as propriedades de `bpy.types.Scene`/`Object` (o smoke test verifica `not hasattr(bpy.types.Scene, 'btm_settings')`).

## Convenções do código

- **Namespaces de operadores (`bl_idname`)**: `hb_face_frame.*`, `hb_frameless.*`, `hb_closets.*`, `home_builder_*.*` (herdados do Home Builder),
  `blendertomob.*` e `btm.*` (código novo). Código novo usa `btm.` ou `blendertomob.`.
- **`bl_options`**: operadores que alteram dados usam `{'UNDO'}` ou `{'REGISTER', 'UNDO'}` (ver `bpy.types.Operator` → "Modifying Blender Data & Undo").
- **Painéis**: sidebar da Viewport 3D (`bl_space_type='VIEW_3D'`, `bl_region_type='UI'`), abas `"Blender to Mob"` e `"Home Builder"`.
- **Propriedades do domínio**: `PointerProperty` em `bpy.types.Object` (`btm_cabinet`, `btm_wall`, `btm_opening`, `btm_plane`, `home_builder`, `face_frame_*`, `hb_closet_*`)
  e em `bpy.types.Scene` (`btm_settings`, `hb_frameless`, `hb_face_frame`, `hb_closets`…).
- **Geometria paramétrica**: modificadores Geometry Nodes (`modifiers.new(type='NODES')`) carregados de `.blend` via `bpy.data.libraries.load`, com inputs lidos/escritos
  por `compat.get_gn_input` / `compat.set_gn_input` e animados por drivers (`driver_add`) — ver `03_compatibilidade_5x.md`.
- **Desenho na viewport**: `SpaceView3D.draw_handler_add` + `gpu` + `gpu_extras.batch` + `blf`, geralmente dentro de operadores modais (posicionamento, cotas, HUD).
- **Interação**: `bpy_extras.view3d_utils` (`region_2d_to_origin_3d`, `region_2d_to_vector_3d`, `location_3d_to_region_2d`) + `Scene.ray_cast(depsgraph, ...)` para snapping (`hb_snap.py`).
- **Arquivos do usuário**: `bpy.utils.extension_path_user(__package__, path=..., create=True)` (nunca gravar dentro da pasta da extensão).
- **Idioma**: rótulos/descrições da UI e comentários novos em português.

## Mapa rápido tarefa → onde procurar

| Tarefa | Código | Referência 5.2 |
|---|---|---|
| Novo operador | `blendertomob/operators/` | `bpy.types.Operator`, `bpy.props`, `info_gotchas_operators` |
| Painel / menu | `blendertomob/ui/` | `bpy.types.Panel`, `bpy.types.Menu`, `bpy.types.UILayout` |
| Propriedade persistente | `blendertomob/data/properties.py`, `hb_props.py` | `bpy.props`, `bpy.types.PropertyGroup` |
| Geometria por código | `blendertomob/geometry/mesh_gen.py` | `bmesh`, `bmesh.ops`, `bpy.types.Mesh`, `info_gotchas_meshes` |
| Geometry Nodes / drivers | `hb_types.py`, `compat.py`, `geometry/door_controller.py` | `bpy.types.NodesModifier`, `bpy.types.bpy_struct.driver_add`, `bpy.types.Driver` |
| Overlay / cotas na viewport | `overlays/draw_handlers.py`, `hb_placement.py`, `hb_gpu_draw.py` | `gpu`, `gpu.shader`, `gpu.state`, `gpu_extras.batch`, `blf` |
| Snapping / raycast | `hb_snap.py` | `bpy.types.Scene.ray_cast`, `bpy_extras.view3d_utils` |
| Plano de corte / nesting | `blendertomob/cutting/` | (Python puro; `bpy.types.Depsgraph` para ler objetos avaliados) |
| Layouts 2D / pranchas | `hb_layouts.py` | `bpy.types.GreasePencil`, `bpy.types.GreasePencilLineartModifier`, `bpy.types.Camera` |
