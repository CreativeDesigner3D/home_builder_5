# Mapeamento legado — `catalog_molding`

> Camada legada herdada do Home Builder 5. Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

## Estado de integração

| Pacote | Registrado pelo add-on? | Evidência |
|---|---|---|
| `blendertomob/catalog/` | 🟢 **Não** — nenhum `import`/`register()` em `blendertomob/__init__.py` nem em outro módulo; nenhuma referência a `hb_catalog` fora do pacote | `blendertomob/__init__.py:9-17,23-57` (listas de submódulos/imports) |
| `blendertomob/molding/` | 🟢 Sim | `blendertomob/__init__.py:55` (import), `:245` (register), `:268` (unregister) |

## Tabela arquivo → responsabilidade → símbolos-chave

| Arquivo | Responsabilidade | Classes / funções-chave (caminho:linha) |
|---|---|---|
| `blendertomob/catalog/__init__.py` | Agrega os submódulos do navegador de catálogo; ordem de register (previews antes da UI) e unregister inversa | `register` `catalog/__init__.py:18`, `unregister` `:27` |
| `blendertomob/catalog/catalog_data.py` | Fonte da verdade do catálogo: lista `CATALOG` de 78 dicts (7 com operador real, 71 stubs), helpers de construção e de categorias | `KIND_VERBS` `:20`, `KIND_ICONS` `:24`, `_ff` `:29`, `_todo` `:37`, `_e` `:45`, `CATALOG` `:78`, `find_entry` `:349`, `list_categories` `:357`, `category_label` `:372`, `category_indented_label` `:379` |
| `blendertomob/catalog/props_catalog.py` | Estado do navegador em `Scene.hb_catalog` e espelho do `CATALOG` em `CollectionProperty` para o `UIList`; sincronização adiada (timer) e em `load_post` | `_category_items_cb` `:24`, `HBCatalogItem` `:31`, `HBCatalogState` `:45`, `sync_catalog` `:75`, `needs_sync` `:93`, `_deferred_sync` `:104`, `schedule_sync` `:114`, `_catalog_load_post` `:128-132`, `register` `:138`, `unregister` `:148` |
| `blendertomob/catalog/previews_catalog.py` | Coleção `bpy.utils.previews` para thumbnails; resolução lazy por nome de arquivo → `{item_id}.png` → placeholder | `_pcoll` `:17`, `_PLACEHOLDER_KEY` `:18`, `get_icon_id` `:29`, `reload` `:67`, `register` `:94` (cria `previews.new()` `:104`), `unregister` `:112` (libera `previews.remove` `:116`) |
| `blendertomob/catalog/ops_catalog.py` | Despacho de ação de item e fallback para itens não implementados; aplicação do estilo global ao produto colocado | `_apply_global_assembly_config` `:16`, `hb_catalog_OT_activate_item` `:45`, `hb_catalog_OT_not_yet_implemented` `:89` |
| `blendertomob/catalog/render_thumbnails.py` | Render Workbench de thumbnails em cena temporária com câmera em coordenadas esféricas; gravação em `catalog/thumbnails/` | `THUMB_RESOLUTION` `:28`, `_AZIMUTH_DEG` `:32`, `_ELEVATION_DEG` `:33`, `_is_renderable` `:40`, `render_entry` `:45`, `render_all` `:177` |
| `blendertomob/catalog/ui_catalog.py` | Painel lateral "Catalog" (aba Home Builder), `UIList` com filtro fuzzy/categoria e reordenação contextual, grade manual 2 colunas, cartão de detalhe | `_filter_visible` `:21`, `_fuzzy_subseq` `:43`, `HB_UL_catalog` `:54` (`draw_item` `:60`, `filter_items` `:95`, `_priority` `:118`), `HB_CATALOG_PT_browser` `:148` (`draw` `:157`, `_draw_grid` `:203`, `_draw_detail` `:244`), `_wrap` `:285` |
| `blendertomob/catalog/thumbnails/` | PNGs estáticos: `no_thumbnail.png` + 5 thumbnails `standard_*` (base, tall, upper, upper_stacked, lap_drawer) | — |
| `blendertomob/molding/__init__.py` | Fachada do pacote; registra apenas `ops` | `register` `molding/__init__.py:20`, `unregister` `:24` |
| `blendertomob/molding/packages.py` | Presets de pacotes (pilhas de perfis), registro de packs de perfis externos, contornos de perfil embutidos, métricas de perfil com cache, criação do objeto-perfil | `register_profile_path` `:35`, `unregister_profile_path` `:44`, `profile_enum_items` `:60`, `CROWN_PACKAGES` `:87`, `FURNITURE_CAP_STACK` `:107`, `BASE_PACKAGES` `:111`, `BASE_SHOE_REF` `:120`, `LIGHT_RAIL_PACKAGES` `:123`, `PACKAGES` `:129`, `package_stack` `:136`, `stack_has_adjustable_offset` `:143`, `stack_uses_category` `:151`, `_ENUM_CACHE` `:164`, `enum_items` `:171`, `_PROFILE_OUTLINES` `:183`, `_finish_profile` `:219`, `_load_library_profile` `:233`, `_curve_metrics` `:262`, `_profile_metrics` `:278`, `profile_top_height` `:314`, `profile_front_depth` `:320`, `make_profile_object` `:327` |
| `blendertomob/molding/adapters.py` | Adaptadores por biblioteca (face frame, frameless): coleta de alvos por tipo, "bridges" (eletrodomésticos de piso), FACTS (papel, canto, rodapé, laterais acabadas, datum crown), material de acabamento | `_CROWN_TYPES` `:16`, `_BASE_TYPES` `:17`, `_RAIL_TYPES` `:18`, `_face_frame_roots` `:21`, `_frameless_roots` `:33`, `collect_targets` `:45`, `collect_bridges` `:55`, `_RECESSED_FF_KICKS` `:73`, `_top_rail_width` `:76`, `_wall_bounds` `:91`, `_near_wall` `:104`, `_frameless_end_finished` `:112`, `finish_material` `:128`, `build_facts` `:163` |
| `blendertomob/molding/engine.py` | Geometria agnóstica de biblioteca: medidas de cage, agrupamento em corridas, ordenação em cadeia, offsets com meia-esquadria, planta de canto em L, caminho frontal (crown/rail) e spans de rodapé (base) incl. ilhas | `cage_dims` `:35`, `footprint_xy` `:55`, `top_z` `:64`, `bottom_z` `:69`, `front_normal_xy` `:73`, `members_touch` `:85`, `connected_components` `:106`, `order_chain` `:124`, `offset_polyline_right` `:159`, `offset_polygon_right` `:195`, `corner_plan_data` `:231`, `_assemble_front_raw` `:260`, `chain_sweep_points` `:348`, `_kick_spans_local` `:395`, `_assemble_kick_spans` `:425`, `_stretch_segments` `:531`, `_island_perimeter_spans` `:613`, `kick_sweep_segments` `:711` |
| `blendertomob/molding/ops.py` | Orquestração: limpar e reconstruir todos os sweeps da cena a partir das props da sala; resolução de pilhas; cotas Z; criação das curvas; callback de update; operador de refresh | `MOLDING_TAG` `:14`, `MOLDING_TYPE` `:15`, `MOLDING_MEMBERS` `:16`, `_TYPES` `:19`, `clear_scene_molding` `:26`, `_resolve_stack` `:46`, `_crown_datum` `:75`, `_crown_stack_top` `:88`, `_sweep_z` `:106`, `_spawn_sweep` `:126`, `_apply_type` `:190`, `_base_stack` `:226`, `apply_scene_packages` `:246`, `on_package_changed` `:300`, `home_builder_OT_refresh_room_molding` `:310`, `register` `:327`, `unregister` `:341` |

## Pontos de contato externos

| Externo | Uso | Evidência |
|---|---|---|
| `blendertomob/hb_props.py` (`Home_Builder_Scene_Props`) | Define as 13 props `molding_*` com `update=update_molding_package` e os callbacks de itens de enum | `hb_props.py:164-208`, `hb_props.py:493-580` |
| `product_libraries/face_frame/props_hb_face_frame.py` | UI das molduras (`draw_molding_ui`) e botão `blendertomob.refresh_room_molding` | `props_hb_face_frame.py:7668-7740` |
| `product_libraries/face_frame/operators/ops_cabinet.py` | `hb_face_frame.draw_cabinet` (alvo das ações do catálogo) | `ops_cabinet.py:18-68` |
| `hb_types.GeoNodeObject.get_input` | Leitura de `Dim X/Y/Z` e `Width` do TOP_RAIL | `engine.py:39-42`, `adapters.py:83` |
| `hb_project.get_main_scene` | Estilos frameless para material de acabamento | `adapters.py:147-148` |
| `units.inch` | Conversão de polegadas nos contornos/defaults | `packages.py:24-25`, `engine.py:241` |
