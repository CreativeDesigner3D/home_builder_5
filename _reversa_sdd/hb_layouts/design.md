# hb_layouts — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados em [`data-dictionary-legacy.md#hb_layouts`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Interface

### Papel e Line Art (`hb_layouts.py`, funções de módulo)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `get_paper_resolution` | `(paper_size: str, landscape=True, dpi=DEFAULT_DPI)` | `(int, int)` | Trunca com `int()`; desconhecido → LETTER (`:23`) 🟢 |
| `get_font` | `(font_name='Calibri Regular')` | `VectorFont \| None` | Só procura em `bpy.data.fonts` (`:44`) 🟢 |
| `get_default_line_engine` / `get_scene_line_engine` | `()` / `(scene)` | `'FREESTYLE' \| 'LINEART'` | Preferência / carimbo (`:132-143`) 🟢 |
| `get_line_art_object` / `remove_line_art_from_scene` | `(scene)` | `Object \| None` / — | (`:145-162`) 🟢 |
| `set_line_art_visible` | `(scene, visible)` | — | Não religa modificadores se baked (`:198`) 🟢 |
| `refresh_line_art` | `(scene)` | — | Alterna `show_viewport` (`:217`) 🟢 |
| `is_line_art_baked` | `(scene)` | `bool` | (`:238`) 🟢 |
| `bake_line_art_editable` | `(scene)` | `bool` | Troca `window.scene` com try/finally (`:255`) 🟢 |
| `unbake_line_art` | `(scene)` | — | (`:333`) 🟢 |
| `setup_line_art_for_scene` | `(scene, solid_collection, dashed_collection, ignore_collection)` | GP `Object` | Recria o GP (`:380`) 🟢 |
| `update_line_art_sizes` | `(scene)` | — | Exceção → retorna em silêncio (`:476-515`) 🟢 |
| `build_line_art_marked_channel` | `(scene)` | — | Sem chamador (`:564`) 🔴 |
| `build_line_art_text_holdouts` | `(scene, rects)` | — | Sem chamador (`:708`) 🔴 |
| `get_iso_freestyle_collections` / `scene_uses_iso_freestyle` / `setup_iso_freestyle` | `(scene)` | — | Sem chamador (`:753-937`) 🔴 |
| `is_cage_object` / `is_helper_object` | `(obj)` | `bool` | RN-18 (`:950-966`) 🟢 |
| `get_layout_view_from_scene` | `(scene)` | `LayoutView` | Tags ELEVATION → PLAN → 3D → MULTI → base (`:2960`) 🟢 |
| `create_elevation_for_wall` / `create_plan_view` / `create_3d_view` / `create_multi_view` | `(wall_obj)` / `()` / `(perspective=True)` / `(source_obj, views)` | vista | Atalhos (`:2977-3017`) 🟢 |
| `create_all_elevations` | `()` | `list[ElevationView]` | Varre `bpy.data.objects` (`:2998`) 🟢 |

### Classes de vista (`hb_layouts.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `TitleBlock.create` | `(scene, camera)` | — | Âncora + 4 textos (`:983-1066`) 🟢 |
| `TitleBlock.update` | `(scene)` | — | Inoperante (`:1100`) 🟡 |
| `LayoutView.__init__` | `(scene=None)` | — | Lê `PAPER_*` da cena (`:1119-1131`) 🟢 |
| `LayoutView.get_all_layout_views` | `()` (static) | `list[Scene]` | (`:1133`) 🟢 |
| `LayoutView.create_scene` | `(name: str)` | `Scene` | Troca `window.scene` (`:1141-1192`) 🟢 |
| `LayoutView.get_freestyle_collection` / `add_to_freestyle_collection` | `(collection_type)` / `(obj, collection_type)` | `Collection \| None` / — | `'SOLID' \| 'DASHED' \| 'IGNORE'` → `<cena>_Freestyle_<Tipo>`; outro valor → `None` (`:1333-1356`) 🟢 |
| `LayoutView.create_camera` | `(name, location: Vector, rotation: tuple)` | `Object` | ORTHO, travada (`:1357`) 🟢 |
| `LayoutView.set_camera_ortho_scale` | `(scale)` | — | (`:1379`) 🟢 |
| `LayoutView.set_paper_size` | `(paper_size='LETTER', landscape=True, dpi=None)` | — | Grava `PAPER_*` (`:1384`) 🟢 |
| `LayoutView.get_paper_aspect_ratio` | `()` | `float` | (`:1412`) 🟢 |
| `LayoutView.delete` | `()` | — | Só remove a cena (`:1417`) 🟢 |
| `ElevationView.create` | `(wall_obj, name=None, paper_size='LETTER', landscape=True)` | `Scene` | (`:1447`) 🟢 |
| `ElevationView.add_cabinet_dimensions` | `()` | — | RN-24 (`:1580`) 🟢 |
| `ElevationView.update` | `()` | — | Regra simplificada (`:1780`) 🟢 |
| `PlanView.create` | `(name='Floor Plan', source_scene=None, paper_size='LETTER', landscape=True)` | `Scene` | (`:1819`) 🟢 |
| `View3D.create` | `(name='3D View', perspective=True, source_scene=None, paper_size=…, landscape=…)` | `Scene` | Força Freestyle (`:1992`) 🟢 |
| `MultiView.create` | `(source_obj, views: list, name=None, paper_size='TABLOID', landscape=True)` | `Scene \| None` | `None` se `views` vazio; `'ISO'` → `_create_iso_left` (`:2205`) 🟢 |

### Detalhes (`hb_details.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `DetailView.create` | `(name='Detail')` | `Scene` | Nome único; `IS_DETAIL_VIEW` (`:29`) 🟢 |
| `DetailView.get_all_detail_views` | `()` (static) | `list[Scene]` | (`:21`) 🟢 |
| `GeoNodeLine.create` / `set_points` / `get_length` | `(name='Line')` / `(start, end)` / `()` | — / — / `float` | (`:107-158`) 🟢 |
| `GeoNodePolyline.create` / `add_point` / `set_point` / `close` | `(name='Polyline')` / `(point)` / `(index, point)` / `()` | — | Mundo → local (`:161-228`) 🟢 |
| `GeoNodeCircle.create` / `set_radius` / `set_center` / `get_radius` | `(name='Circle', radius=1.0)` / … | — | 32 segmentos (`:230-305`) 🟢 |
| `GeoNodeText.create` | `(name='Text', text='Text', size=0.05)` | — | (`:387`) 🟢 |
| `GeoNodeText.set_text` / `get_text` / `set_size` / `set_location` / `set_alignment` | … / `(align_x='LEFT', align_y='BOTTOM')` | — | (`:411-439`) 🟢 |
| `get_label_font` / `apply_label_style` | `(scene)` / `(text_obj, scene)` | `VectorFont` / — | RN-35 (`:329-381`) 🟢 |

Apesar do prefixo `GeoNode*`, as primitivas de detalhe são **curvas/texto nativos** com material próprio (herdam de
`hb_types.GeoNodeObject` pelo encapsulamento). 🟡

### Biblioteca de detalhes (`hb_detail_library.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `get_user_library_path` / `get_library_index_path` | `()` | `str` | `extension_path_user(__package__, path="detail_library", create=True)` (`:14-22`) 🟢 |
| `load_library_index` / `save_library_index` | `()` / `(index: dict)` | `dict` / — | Corrompido → vazio; escrita sem try (`:24-43`) 🟢 |
| `generate_detail_filename` | `(name)` | `str` | `[^a-zA-Z0-9_-]` → `_` + `_AAAAMMDD_HHMMSS.blend` (`:46`) 🟢 |
| `save_detail_to_library` | `(context, name, description="")` | `(ok, msg, filepath)` | (`:59`) 🟢 |
| `get_library_details` | `(detail_type=None)` | `list[dict]` | (`:132`) 🟢 |
| `load_detail_from_library` | `(context, filepath)` | `(ok, msg, objetos)` | Usa `bpy.ops.object.select_all` (`:162`) 🟢 |
| `get_detail_info` | `(filepath)` | `dict` | (`:208`) 🟢 |
| `delete_detail_from_library` | `(filename)` | `(True, msg)` | Sempre sucesso (`:225`) 🟢 |

Entrada do índice (`library_index.json`, lista `details`): `name`, `description`, `filename`, `filepath`,
`date_created` (ISO 8601), `object_count`, `detail_type` (`detail`/`crown`), `is_crown_detail` (`hb_detail_library.py:115-124`). 🟢

### Assets (`hb_assets.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `get_addon_assets_path` | `()` | `str` | `blendertomob/assets` (`:9`) 🟢 |
| `get_user_libraries` / `get_user_library_paths` | `()` | lista | Das preferências (`:14-35`) 🟢 |
| `get_all_subfolder_paths` | `(subfolder_name, bundled_path=None)` | `list[str]` | RN-40 (`:37`) 🟢 |
| `get_catalog_map` | `()` | `dict` | `blender_assets.cats.txt` (`:65`) 🟢 |
| `ensure_asset_libraries` / `remove_asset_libraries` / `refresh_user_libraries` | `()` | — | (`:209-246`) 🟢 |
| `BTM_AssetLibraryEntry` | PropertyGroup | — | `name` (padrão "New Library"), `library_path` (`DIR_PATH`), `internal_id`; alias `HB_AssetLibraryEntry` (`:248-267`) 🟢 |
| `HB_OT_add_asset_library` / `remove` / `refresh` | `home_builder.*_asset_library` | — | Sem `bl_options` (`:280-320`) 🟢 |
| `HB_OT_assign_asset_catalog` | `home_builder.assign_asset_catalog` | — | (`:342-394`) 🟢 |
| `VIEW3D_AST_home_builder` | `AssetShelf` | — | `poll` modo OBJECT; `asset_poll` sem guarda de `None` (`:323-339`) 🟢 |

### Estado persistido na cena (IDProperties)

`IS_LAYOUT_VIEW`, `IS_ELEVATION_VIEW`, `IS_PLAN_VIEW`, `IS_3D_VIEW`, `IS_MULTI_VIEW`, `IS_DETAIL_VIEW`, `IS_CROWN_DETAIL`,
`SOURCE_WALL`, `SOURCE_OBJECT`, `CONTENT_COLLECTION`, `PAPER_SIZE`, `PAPER_LANDSCAPE`, `PAPER_DPI`, `HB_LINE_ENGINE`,
`HB_LINEART_BAKED`. Propriedades `bpy.props` de cena usadas (registradas em `operators/layouts.py:4665-4718`):
`hb_layout_scale`, `hb_paper_size`, `hb_paper_landscape`, `hb_lineart_*_scale`. 🟢

## Fluxo Principal

### F1. Criar cena base (`LayoutView.create_scene`) 🟢
1. Captura `unit_settings` (system, scale_length, length_unit) e snap da cena atual.
2. `bpy.data.scenes.new(name)`, marca `IS_LAYOUT_VIEW`, troca `bpy.context.window.scene`.
3. Copia unidades, `home_builder.product_tab` e snap.
4. `_setup_render_settings` (Workbench, AA 32, OBJECT, FLAT, SOLID).
5. `_create_freestyle_collections` → `<cena>_Freestyle_Ignore`, `<cena>_Freestyle_Dashed`, `<cena>_Freestyle_Solid`.
6. Engine: Line Art → `_setup_lineart` → `setup_line_art_for_scene`; Freestyle → `_setup_freestyle_linesets`.
   Carimba `HB_LINE_ENGINE`.

### F2. Elevação (`flowcharts/legacy-hb_layouts-elevation_create.md`) 🟢
1. `create_scene(nome)`; marca `IS_ELEVATION_VIEW`, `SOURCE_WALL`.
2. Câmera ORTHO com rotação `(90°, 0, rotZ da parede)`.
3. `set_paper_size`.
4. `add_cabinet_dimensions()` — para cada filho direto com cage FRAMELESS/FACE_FRAME: classifica por Z local
   (> 1,2 m = superior); cria `GeoNodeDimension` a 2" à frente, em z = −4" (inferiores/altos) ou topo máx. + 4"
   (superiores), comprimento `Dim X`, nome `Dim_<cage>`, `IS_2D_ANNOTATION`, na collection IGNORE.
5. `_fit_camera_to_content(wall)` — bbox local ∪ filhos MESH ∪ cotas; margem 10%; câmera a y=−3; `ortho = max(w, h)`.
6. `_create_content_collections(wall, nome)` — collections por parede/gabinete, peças internas em Dashed, instâncias
   (`_create_collection_instance`) na cena de layout; `_collect_objects_split` pula cages e helpers.
7. `TitleBlock.create(scene, camera)`.

### F3. Planta e 3D 🟢
- Planta: coleta `IS_WALL_BP` da cena de origem; bbox pelos pontos inicial/final; câmera z=5; `ortho = max(w,h) + 1 m`.
- 3D: alvo = média dos centros das paredes; câmera em alvo + (8, −8, 8), `to_track_quat('-Z', 'Y')`; remove GP se a
  preferência for Line Art.

### F4. Multivista (`flowcharts/legacy-hb_layouts-create_iso_left.md`) 🟢
1. `views` vazio → `None`. Contém `'ISO'` → `_create_iso_left`.
2. Dimensões do objeto (`_get_object_dimensions`) e bbox recursivo (`_compute_recursive_bbox`).
3. Conteúdo sólido: collection com o objeto; conteúdo tracejado (`_build_dashed_content_collection`): move peças
   internas cuja abertura ancestral tem `front_type ≠ 'NONE'`.
4. Por vista: instância com `rot = Euler(base) @ R_origem⁻¹` e posição por `_calculate_instance_position`
   (cruz, gap 12"); instância tracejada só em células de elevação.
5. Câmera a z=10, `ortho = max(W, H) + 2·6"`; carimbo.
6. Iso-left: iso θ=−60°; escolhe a maior escala da escada que caiba nas margens; ancora elevação à direita/abaixo;
   grava `hb_paper_size`, `hb_paper_landscape`, `hb_layout_scale`.

### F5. Line Art (`flowcharts/legacy-hb_layouts-build_line_art_marked_channel.md`) 🟢
1. `setup_line_art_for_scene` remove o GP anterior, cria GP preto `show_in_front` não selecionável, 2 camadas
   (Solid/Dashed) e 4 modificadores; chama `update_line_art_sizes`.
2. `update_line_art_sizes`: lê `hb_layout_scale` + fatores; `paper_to_world` (import tardio de
   `operators.layouts`); raio = largura; associa a câmera jitter (`_ensure_lineart_camera`).
3. Bake: troca `window.scene`, captura strokes avaliados, desliga modificadores, reescreve camadas, restaura a cena.

### F6. Detalhe 2D e biblioteca 🟢
1. `DetailView.create`: nome único, `save_view_state` se a origem for cômodo, cena `IS_DETAIL_VIEW`, unidades e snap,
   viewport top-down (`_setup_2d_view` via `context.screen.areas`).
2. Primitivas criadas em `bpy.context.scene`.
3. `save_detail_to_library`: valida cena e objetos; grava `.blend` com `bpy.data.libraries.write(filepath, data_blocks,
   fake_user=True)` (objetos, dados, materiais); acrescenta ao índice (`hb_detail_library.py:107-127`).
4. `load_detail_from_library`: append dos objetos para a cena atual, seleciona-os.

### F7. Bibliotecas de assets (`flowcharts/legacy-hb_layouts-ensure_asset_libraries.md`) 🟢
1. `ensure_asset_libraries` (chamado de `__init__.register`, `:248`): garante "Home Builder" → `assets/`.
2. Para cada entrada do usuário: garante `internal_id`, registra `HB: <nome> [<id>]` com `APPEND`.
3. `_cleanup_orphaned_libraries`: remove `HB: ` sem tag ou com id desconhecido e "Home Builder Extended".
4. `unregister` remove as bibliotecas e desregistra classes.

## Fluxos Alternativos

- **Line Art sem escala (`hb_layout_scale` ausente):** fallback `1/4"=1'`; exceção em `update_line_art_sizes` → retorna calado. 🟢
- **`views` vazio na multivista:** `None`. 🟢
- **Planta sem paredes:** câmera (0,0,5), ortho 10. 🟢
- **Bake sem GP ou sem strokes:** `False`. 🟢
- **Índice JSON corrompido:** índice vazio (os `.blend` continuam no disco, invisíveis). 🟢
- **`--background`:** `window.scene`, `context.screen.areas`, `bpy.ops.object.select_all` e
  `bpy.ops.grease_pencil.layer_mask_add` falham (o último em silêncio). 🟢
- **Calibri ausente (Linux/macOS):** `get_font` → `None`; `TextCurve.font = None` pode ser rejeitado. 🟡
- **`asset_poll(None)`:** `AttributeError` em `asset.id_type`. 🟢
- **Recarga da extensão:** `unregister` de `hb_assets` testa `hasattr(bpy.types, 'HB_OT_*')`, mas o nome RNA é
  `HOME_BUILDER_OT_*` → operadores não desregistrados. 🟡

## Dependências

- [`hb_core`](../hb_core/) — `GeoNodeWall`, `GeoNodeCage`, `GeoNodeObject`, `GeoNodeRectangle`, `GeoNodeDimension`;
  `hb_utils.is_room_scene`, `save_view_state`, `set_top_down_view`; `Scene.home_builder` (anotações, `product_tab`). 🟢
- `units.inch`. 🟢
- `operators/layouts.py` — `paper_to_world`, `PAPER_SIZES_INCHES`, props `hb_layout_scale`/`hb_paper_*`/`hb_lineart_*`
  (dependência circular resolvida por import tardio). 🟢
- Preferências do add-on — `line_engine`, `default_paper_size`, `asset_libraries`, `asset_libraries_index`. 🟢
- `face_frame` — `face_frame_opening.front_type` (linhas ocultas da multivista). 🟢
- Consumidores — `operators/layouts.py`, `operators/details.py`, `ui/view3d_sidebar.py`, frameless/face_frame. 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Uma cena por prancha com collection instances (sem copiar geometria) | `hb_layouts.py:1141,1681-1750` | 🟢 |
| Duas engines de traço (Freestyle padrão, Line Art opcional) com roteamento comum em 3 collections | `:132-142,1235-1332` | 🟢 |
| Papel em polegadas e DPI; escalas imperiais (`1/4"=1'`) como fallback | `:12-21,80-87,2524` | 🟢 |
| Line Art assável para edição manual e desempenho | `:255-346` | 🟢 |
| Câmera jitter de 0,05° para estabilizar o Line Art em vistas ortogonais perfeitas | `:75,164-195` | 🟢 |
| Cotas automáticas só para gabinetes frameless/face frame (closets fora) | `:1580-1634` | 🟢 |
| Biblioteca de detalhes em arquivos `.blend` separados + índice JSON na pasta do usuário | `hb_detail_library.py:14-129` | 🟢 |
| Bibliotecas de assets do usuário identificadas por id estável no nome | `hb_assets.py:83-220` | 🟢 |

## Estado Interno

- **Por cena:** IDProperties listadas acima + collections `<cena>_*`, câmera, GP Line Art e câmera jitter. 🟢
- **Por objeto gerado:** `IS_HB_LINEART`, `IS_HB_LINEART_CAMERA`, `IS_HB_LINEART_MARKED`, `IS_2D_ANNOTATION`,
  `IS_DETAIL_*`, `IS_FREESTYLE_*` (collections). 🟢
- **Instâncias Python** (`LayoutView` e subclasses): `scene`, `camera`, `paper_size`, `landscape`, `dpi` —
  reconstruídas da cena em `__init__`. 🟢
- **Arquivos do usuário:** `detail_library/*.blend` + `library_index.json`. 🟢
- **Preferências:** `asset_libraries` (coleção de `BTM_AssetLibraryEntry`) e as `UserAssetLibrary` do Blender. 🟢

## Observabilidade

- Sem logs estruturados; falhas de Line Art e de registro engolidas. 🟢
- Operadores de assets e biblioteca devolvem `(ok, mensagem)` para `self.report`. 🟢
- `print` pontuais 🟡 (não inventariados).

## Riscos e Lacunas

- 🔴 Exportador híbrido e funções de canal Marked/holdout/iso sem chamador.
- 🔴 Campos do carimbo não são preenchidos com dados do projeto; `TitleBlock.update` inoperante.
- 🔴 Miniaturas da biblioteca de detalhes inexistentes.
- 🟢 `Material.use_nodes = True` obsoleto em `hb_layouts.py:1091,2947` e `hb_details.py:133,189,266,376`.
- 🟢 Dependência de janela/tela em `create_scene`, `DetailView.create`, `load_detail_from_library`.
- 🟡 `LayoutView.delete` deixa collections, câmera e GP órfãos.
- 🟡 `ortho_scale = max(w, h)` ignora o aspecto do papel (conteúdo alto em paisagem pode ser cortado).
- 🟡 `create_all_elevations` percorre todas as salas (`bpy.data.objects`).
- 🟡 Código morto: `PlanView/View3D._fit_camera_to_content`, `MultiView._calculate_grid`, `_create_view_label`.
- 🟡 Escada de escalas do iso-left só imperial; o fork usa escalas métricas (`1:50`) por padrão.
- 🟡 `load_detail_from_library` calcula nomes existentes e descarta (`hb_detail_library.py:181`).
