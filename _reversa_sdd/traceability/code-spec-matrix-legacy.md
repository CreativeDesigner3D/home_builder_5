# Matriz de Rastreabilidade — Camada Legada (Home Builder 5)

> Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**. Complementa [`code-spec-matrix.md`](code-spec-matrix.md)
> (camada moderna `btm_*`). Cobertura: 🟢 arquivo citado nas specs da unit (`requirements`/`design`/`tasks`/`edge-cases`/`questions`/`legacy-mapping`) ·
> 🟡 coberto parcialmente / transversal · n/a sem unit legada. Caminhos relativos a `blendertomob/`.

## 1. Resumo por unit

| Unit | Arquivos | Linhas | 🟢 | 🟡 | n/a | Specs |
|---|---:|---:|---:|---:|---:|---|
| `hb_core` | 8 | 3.763 | 8 | 0 | 0 | [`hb_core/`](../hb_core/requirements.md) |
| `hb_placement` | 3 | 2.224 | 3 | 0 | 0 | [`hb_placement/`](../hb_placement/requirements.md) |
| `hb_layouts` | 4 | 4.129 | 4 | 0 | 0 | [`hb_layouts/`](../hb_layouts/requirements.md) |
| `product_common` | 7 | 4.735 | 7 | 0 | 0 | [`product_common/`](../product_common/requirements.md) |
| `frameless` | 26 | 22.977 | 26 | 0 | 0 | [`frameless/`](../frameless/requirements.md) |
| `face_frame` | 31 | 60.800 | 31 | 0 | 0 | [`face_frame/`](../face_frame/requirements.md) |
| `closets` | 17 | 9.751 | 17 | 0 | 0 | [`closets/`](../closets/requirements.md) |
| `catalog_molding` — `catalog/` não registrado pelo add-on | 12 | 3.012 | 12 | 0 | 0 | [`catalog_molding/`](../catalog_molding/requirements.md) |
| `hb_core (transversal)` | 1 | 313 | 0 | 1 | 0 | — |
| `— (camada moderna)` | 1 | 100 | 0 | 0 | 1 | — |
| **Total** | **110** | **111.804** | **108** | **1** | **1** | |

Cobertura estimada: **99%** dos arquivos legados mapeados a uma unit (108 completos, 1 parcial). O único `n/a` é `compat.py`, que pertence à camada moderna e é o ponto oficial de diferenças de versão (as units legadas ainda usam os helpers duplicados de `hb_utils` — ver T3 de [`code-analysis-legacy.md`](../code-analysis-legacy.md)).

## 2. Matriz por arquivo

### hb_core

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `hb_driver_functions.py` | `hb_core` | 26 | 🟢 |
| `hb_project.py` | `hb_core` | 319 | 🟢 |
| `hb_props.py` | `hb_core` | 976 | 🟢 |
| `hb_props_obstacles.py` | `hb_core` | 306 | 🟢 |
| `hb_types.py` | `hb_core` | 962 | 🟢 |
| `hb_utils.py` | `hb_core` | 469 | 🟢 |
| `ops.py` | `hb_core` | 685 | 🟢 |
| `units.py` | `hb_core` | 20 | 🟢 |

### hb_placement

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `hb_gpu_draw.py` | `hb_placement` | 114 | 🟢 |
| `hb_placement.py` | `hb_placement` | 1856 | 🟢 |
| `hb_snap.py` | `hb_placement` | 254 | 🟢 |

### hb_layouts

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `hb_assets.py` | `hb_layouts` | 430 | 🟢 |
| `hb_detail_library.py` | `hb_layouts` | 243 | 🟢 |
| `hb_details.py` | `hb_layouts` | 439 | 🟢 |
| `hb_layouts.py` | `hb_layouts` | 3017 | 🟢 |

### product_common

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `accessory_registry.py` | `product_common` | 117 | 🟢 |
| `appliance_spec_registry.py` | `product_common` | 32 | 🟢 |
| `product_libraries/common/__init__.py` | `product_common` | 9 | 🟢 |
| `product_libraries/common/door_builder.py` | `product_common` | 1404 | 🟢 |
| `product_libraries/common/door_profiles.py` | `product_common` | 710 | 🟢 |
| `product_libraries/common/types_appliances.py` | `product_common` | 220 | 🟢 |
| `product_libraries/common/wood_hoods.py` | `product_common` | 2243 | 🟢 |

### frameless

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `product_libraries/frameless/__init__.py` | `frameless` | 21 | 🟢 |
| `product_libraries/frameless/finish_colors.py` | `frameless` | 294 | 🟢 |
| `product_libraries/frameless/menus_frameless.py` | `frameless` | 416 | 🟢 |
| `product_libraries/frameless/operators/__init__.py` | `frameless` | 57 | 🟢 |
| `product_libraries/frameless/operators/ops_appliance.py` | `frameless` | 106 | 🟢 |
| `product_libraries/frameless/operators/ops_cabinet.py` | `frameless` | 1083 | 🟢 |
| `product_libraries/frameless/operators/ops_cleanup.py` | `frameless` | 331 | 🟢 |
| `product_libraries/frameless/operators/ops_countertop.py` | `frameless` | 752 | 🟢 |
| `product_libraries/frameless/operators/ops_crown.py` | `frameless` | 1582 | 🟢 |
| `product_libraries/frameless/operators/ops_defaults.py` | `frameless` | 193 | 🟢 |
| `product_libraries/frameless/operators/ops_finished_ends.py` | `frameless` | 521 | 🟢 |
| `product_libraries/frameless/operators/ops_front.py` | `frameless` | 129 | 🟢 |
| `product_libraries/frameless/operators/ops_interior.py` | `frameless` | 882 | 🟢 |
| `product_libraries/frameless/operators/ops_library.py` | `frameless` | 592 | 🟢 |
| `product_libraries/frameless/operators/ops_opening.py` | `frameless` | 1863 | 🟢 |
| `product_libraries/frameless/operators/ops_placement.py` | `frameless` | 2007 | 🟢 |
| `product_libraries/frameless/operators/ops_products.py` | `frameless` | 568 | 🟢 |
| `product_libraries/frameless/operators/ops_snap_line.py` | `frameless` | 526 | 🟢 |
| `product_libraries/frameless/operators/ops_styles.py` | `frameless` | 1436 | 🟢 |
| `product_libraries/frameless/operators/ops_toe_kick.py` | `frameless` | 707 | 🟢 |
| `product_libraries/frameless/operators/ops_upper_bottom.py` | `frameless` | 674 | 🟢 |
| `product_libraries/frameless/props_elevation_templates.py` | `frameless` | 1576 | 🟢 |
| `product_libraries/frameless/props_hb_frameless.py` | `frameless` | 2574 | 🟢 |
| `product_libraries/frameless/types_frameless.py` | `frameless` | 2921 | 🟢 |
| `product_libraries/frameless/types_products.py` | `frameless` | 938 | 🟢 |
| `product_libraries/frameless/wood_materials.py` | `frameless` | 228 | 🟢 |

### face_frame

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `product_libraries/face_frame/__init__.py` | `face_frame` | 26 | 🟢 |
| `product_libraries/face_frame/applied_panel_sizing.py` | `face_frame` | 912 | 🟢 |
| `product_libraries/face_frame/bay_presets.py` | `face_frame` | 494 | 🟢 |
| `product_libraries/face_frame/dim_edit_overlay.py` | `face_frame` | 922 | 🟢 |
| `product_libraries/face_frame/exposure.py` | `face_frame` | 634 | 🟢 |
| `product_libraries/face_frame/finish_colors.py` | `face_frame` | 289 | 🟢 |
| `product_libraries/face_frame/menus_face_frame.py` | `face_frame` | 690 | 🟢 |
| `product_libraries/face_frame/operators/__init__.py` | `face_frame` | 45 | 🟢 |
| `product_libraries/face_frame/operators/op_modify_cabinet.py` | `face_frame` | 2045 | 🟢 |
| `product_libraries/face_frame/operators/op_open_mode.py` | `face_frame` | 329 | 🟢 |
| `product_libraries/face_frame/operators/ops_appliance_panels.py` | `face_frame` | 687 | 🟢 |
| `product_libraries/face_frame/operators/ops_cabinet.py` | `face_frame` | 4751 | 🟢 |
| `product_libraries/face_frame/operators/ops_countertop.py` | `face_frame` | 630 | 🟢 |
| `product_libraries/face_frame/operators/ops_defaults.py` | `face_frame` | 76 | 🟢 |
| `product_libraries/face_frame/operators/ops_finished_ends.py` | `face_frame` | 155 | 🟢 |
| `product_libraries/face_frame/operators/ops_library.py` | `face_frame` | 561 | 🟢 |
| `product_libraries/face_frame/operators/ops_part_commands.py` | `face_frame` | 2076 | 🟢 |
| `product_libraries/face_frame/operators/ops_placement.py` | `face_frame` | 5896 | 🟢 |
| `product_libraries/face_frame/operators/ops_styles.py` | `face_frame` | 1301 | 🟢 |
| `product_libraries/face_frame/operators/ops_thumbnails.py` | `face_frame` | 196 | 🟢 |
| `product_libraries/face_frame/operators/ops_wedge.py` | `face_frame` | 177 | 🟢 |
| `product_libraries/face_frame/props_hb_face_frame.py` | `face_frame` | 8155 | 🟢 |
| `product_libraries/face_frame/pulls.py` | `face_frame` | 181 | 🟢 |
| `product_libraries/face_frame/solver_face_frame.py` | `face_frame` | 4797 | 🟢 |
| `product_libraries/face_frame/split_preview.py` | `face_frame` | 236 | 🟢 |
| `product_libraries/face_frame/style_options.py` | `face_frame` | 9838 | 🟢 |
| `product_libraries/face_frame/thumbnail_render.py` | `face_frame` | 168 | 🟢 |
| `product_libraries/face_frame/types_face_frame.py` | `face_frame` | 9541 | 🟢 |
| `product_libraries/face_frame/types_face_frame_corner.py` | `face_frame` | 2986 | 🟢 |
| `product_libraries/face_frame/ui_face_frame.py` | `face_frame` | 1719 | 🟢 |
| `product_libraries/face_frame/wood_materials.py` | `face_frame` | 287 | 🟢 |

### closets

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `product_libraries/closets/__init__.py` | `closets` | 21 | 🟢 |
| `product_libraries/closets/const_closets.py` | `closets` | 140 | 🟢 |
| `product_libraries/closets/drawer_boxes_closets.py` | `closets` | 114 | 🟢 |
| `product_libraries/closets/fronts_closets.py` | `closets` | 237 | 🟢 |
| `product_libraries/closets/gpu_overlay_closets.py` | `closets` | 1019 | 🟢 |
| `product_libraries/closets/materials_closets.py` | `closets` | 313 | 🟢 |
| `product_libraries/closets/menus_closets.py` | `closets` | 251 | 🟢 |
| `product_libraries/closets/molding_closets.py` | `closets` | 218 | 🟢 |
| `product_libraries/closets/operators/__init__.py` | `closets` | 15 | 🟢 |
| `product_libraries/closets/operators/op_grab_closet.py` | `closets` | 921 | 🟢 |
| `product_libraries/closets/operators/op_open_door_closet.py` | `closets` | 230 | 🟢 |
| `product_libraries/closets/operators/ops_closet.py` | `closets` | 2902 | 🟢 |
| `product_libraries/closets/props_closets.py` | `closets` | 533 | 🟢 |
| `product_libraries/closets/pulls_closets.py` | `closets` | 392 | 🟢 |
| `product_libraries/closets/solver_closets.py` | `closets` | 126 | 🟢 |
| `product_libraries/closets/starter_presets.py` | `closets` | 40 | 🟢 |
| `product_libraries/closets/types_closets.py` | `closets` | 2279 | 🟢 |

### catalog_molding

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `catalog/__init__.py` | `catalog_molding` | 31 | 🟢 |
| `catalog/catalog_data.py` | `catalog_molding` | 382 | 🟢 |
| `catalog/ops_catalog.py` | `catalog_molding` | 128 | 🟢 |
| `catalog/previews_catalog.py` | `catalog_molding` | 119 | 🟢 |
| `catalog/props_catalog.py` | `catalog_molding` | 154 | 🟢 |
| `catalog/render_thumbnails.py` | `catalog_molding` | 198 | 🟢 |
| `catalog/ui_catalog.py` | `catalog_molding` | 314 | 🟢 |
| `molding/__init__.py` | `catalog_molding` | 25 | 🟢 |
| `molding/adapters.py` | `catalog_molding` | 230 | 🟢 |
| `molding/engine.py` | `catalog_molding` | 736 | 🟢 |
| `molding/ops.py` | `catalog_molding` | 348 | 🟢 |
| `molding/packages.py` | `catalog_molding` | 347 | 🟢 |

### hb_core (transversal)

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `__init__.py` | `hb_core (transversal)` | 313 | 🟡 |

### — (camada moderna)

| Arquivo do legado | Unit correspondente | Linhas | Cobertura |
|---|---|---:|---|
| `compat.py` | `— (camada moderna)` | 100 | n/a |

## 3. Observações

- `__init__.py` (registro do add-on) é citado pelo `hb_core` apenas nos trechos de registro, `load_post` e `driver_namespace`; o restante do registro de cada biblioteca está na unit correspondente. 🟡
- `catalog/` aparece coberto, mas não é registrado pelo add-on (código latente) — destino em [`catalog_molding/questions.md`](../catalog_molding/questions.md) Q-01.
- Trechos de `face_frame` lidos só por amostragem (recálculo de cantos, pós-passes, itens internos) estão 🟢 por arquivo, mas 🔴 por conteúdo — ver [`face_frame/questions.md`](../face_frame/questions.md) Q-02.
- Interfaces dos node groups embarcados: [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md).
- Nenhuma unit legada alimenta `cutting/` (lacuna L1 de [`soul.md`](../soul.md)); as tarefas de integração estão em frameless T-47, face_frame T-34 e closets T-30.
