# Mapeamento legado — módulo `hb_placement`

Camada legada (fork do Home Builder 5). Caminhos relativos a `blendertomob/`.
Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

## Arquivo → responsabilidade

| Arquivo | LOC | Responsabilidade | Classes / funções-chave (caminho:linha) | Conf. |
|---|---|---|---|---|
| `hb_placement.py` | 1856 | Estado e entrada numérica de operadores modais de posicionamento; consultas de colisão/vão em paredes (lado, altura, profundidade, paredes vizinhas, T, ilhas); snap gabinete→gabinete; mixin de cotas de 3 cliques; desenho GPU de cotas de posicionamento e do indicador de snap; duplicação de hierarquia | `PlacementDimSpec` `hb_placement.py:17` · `FREE_CABINET_TAGS` `:27` · `PlacementState` `:34` · `TypingTarget` `:42` · `NUMBER_KEYS` `:55` · `CABINET_MARKERS` `:71` · `PlacementMixin` `:81` · `duplicate_object_hierarchy` `:1273` · `draw_header_text` `:1343` · `clear_header_text` `:1352` · `DimensionOperatorMixin` `:1360` · `draw_dimension_snap_indicator` `:1642` · `draw_placement_dimensions` `:1712` | 🟢 |
| `hb_snap.py` | 254 | Localização da região 3D sob o mouse; raycast com anel de busca; snap a vértice/aresta (Ctrl); interseção com plano de grade; arredondamento de valores à grade de unidades | `RADIUS=50` `hb_snap.py:7` · `STEPS=6` `:8` · `get_region` `:10` · `event_is_pass_through` `:31` · `ray_cast` `:38` · `best_hit` `:48` · `search_edge_pos` `:84` · `snap_to_geometry` `:100` · `snap_to_object` `:131` · `floor_fit`/`ceil_fit` `:147/:150` · `snap_to_grid` `:153` · `main` `:193` · `snap_value_to_grid` `:212` · `snap_vector_to_grid` `:239` | 🟢 |
| `hb_gpu_draw.py` | 114 | Primitivas GPU/BLF 2D compartilhadas e cálculo da área visível da região WINDOW (descontando toolbar, N-panel, headers e asset shelf com Region Overlap) | `get_visible_window_bounds` `hb_gpu_draw.py:12` · `draw_rect` `:66` · `draw_rect_outline` `:76` · `draw_text` `:88` · `vcenter_baseline` `:96` · `point_in_rect` `:104` · `draw_lines` `:110` | 🟢 |

## Métodos de `PlacementMixin` (`hb_placement.py:81`)

| Grupo | Método (linha) | Papel | Conf. |
|---|---|---|---|
| Ciclo de vida | `init_placement` (115), `register_placement_object` (126), `cancel_placement` (410), `_delete_object_and_children` (430) | Inicializa estado PLACING; registra objetos de preview; remove-os recursivamente no cancelamento | 🟢 |
| Draw handler | `add_placement_dim_handler` (132), `remove_placement_dim_handler` (147) | Liga/desliga `draw_placement_dimensions` em `SpaceView3D` WINDOW/POST_PIXEL; ambos idempotentes | 🟢 |
| Snap | `update_snap` (158) | Atualiza região e `mouse_pos`, delega a `hb_snap.main` | 🟢 |
| Digitação | `start_typing` (179), `stop_typing` (185), `handle_typing_event` (191), `get_default_typing_target` (252), `get_next_typing_target` (260), `on_typed_value_changed` (267), `apply_typed_value` (274), `get_typed_display_string` (390) | Máquina PLACING↔TYPING e hooks para subclasses | 🟢 |
| Parser | `parse_typed_distance` (283), `_parse_feet_inches` (338), `_extract_number` (349), `_number_to_scene_units` (373) | Texto → metros (pés/pol., frações, mm/cm/m, unidades da cena) | 🟢 |
| Vão em parede | `get_wall_children_sorted` (454), `find_placement_gap` (502), `find_placement_gap_by_side` (918) | Obstáculos ordenados em X local e escolha de `snap_x` | 🟢 |
| Intrusões | `get_adjacent_wall_intrusion` (672), `get_tee_wall_intrusions` (828) | Paredes vizinhas em canto e paredes em T como obstáculos virtuais | 🟢 |
| Recuos | `_wall_end_is_inside_corner` (1143), `compute_gap_holdoffs` (1191) | Recuo por borda (ponta aberta, canto externo, abertura) | 🟢 |
| Snap gabinete | `find_cabinet_bp` (580), `detect_cabinet_snap_target` (608), `compute_cabinet_snap_transform` (635) | Encostar novo objeto na face LEFT/RIGHT de gabinete livre | 🟢 |

## Métodos de `DimensionOperatorMixin` (`hb_placement.py:1360`)

| Método (linha) | Papel | Conf. |
|---|---|---|
| `init_dimension_state` (1381) | Estado FIRST, pontos nulos, ortho desligado | 🟢 |
| `add_dimension_draw_handler` (1400) / `remove_dimension_draw_handler` (1406) | Liga/desliga `draw_dimension_snap_indicator` (POST_PIXEL) | 🟢 |
| `get_ortho_display` (1412), `get_dimension_header_text` (1422), `update_dimension_header` (1434) | Texto do header | 🟢 |
| `apply_ortho_constraint` (1438), `cycle_ortho_mode` (1463) | Restrição horizontal/vertical relativa a `first_point` | 🟢 |
| `handle_dimension_event` (1476) | Despacho de eventos; retorna string `'RUNNING_MODAL'`/`'FINISHED'`/`'CANCELLED'`/`'PASS_THROUGH'`/`None` | 🟢 |
| Abstratos (1567-1639): `get_snap_point`, `get_plane_point`, `create_preview_dimension`, `update_dimension_preview`, `finalize_dimension`, `cancel_dimension` | `NotImplementedError` — implementados pelos consumidores | 🟢 |

## Consumidores (fora do módulo)

| Consumidor | Usa | Conf. |
|---|---|---|
| `product_libraries/frameless/operators/ops_placement.py:60,270` (`WallObjectPlacementMixin`, `hb_frameless_OT_place_cabinet`) | `PlacementMixin`, `find_placement_gap_by_side`, `detect_cabinet_snap_target`, `compute_cabinet_snap_transform` | 🟢 |
| `product_libraries/face_frame/operators/ops_placement.py` | `PlacementMixin`, `PlacementDimSpec`, `add/remove_placement_dim_handler`, `TypingTarget`, `duplicate_object_hierarchy` | 🟢 |
| `product_libraries/closets/operators/ops_closet.py:548,603,1337,1721,1739` | `add/remove_placement_dim_handler` | 🟢 |
| `operators/walls.py:947,5115,5474` | `PlacementMixin` (paredes, cortadores de piso/parede) | 🟢 |
| `operators/doors_windows.py:190,660` | `PlacementMixin` via `WallObjectPlacementMixin` | 🟢 |
| `operators/ops_obstacles.py:72` | `PlacementMixin` | 🟢 |
| `operators/details.py:253,1013,1713,2014,2780` e `operators/layouts.py:1054,1416,1790,2503,3053,3516` | `PlacementMixin` (desenho 2D) e `DimensionOperatorMixin` (cotas) | 🟢 |
| `product_libraries/*/operators/ops_library.py:304/310` | `PlacementMixin` (carregar grupo de gabinetes) | 🟢 |
| `operators/scene_navigator.py`, `operators/viewport_hud.py` | `hb_gpu_draw` | 🟢 |

## Dependências internas

`hb_placement` → `hb_snap`, `units` (import de topo, `hb_placement.py:10`), `hb_types` (import local em cada método: `GeoNodeObject.get_input`, `GeoNodeWall.get_input`/`has_modifier`/`get_connected_wall`). `hb_snap` → `units` (import local, `hb_snap.py:226`). `hb_gpu_draw` → apenas `blf` e `gpu_extras`. 🟢
