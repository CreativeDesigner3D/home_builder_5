# closets — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#closets`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/closets/`.
> Namespace de operadores legado: `hb_closets.*`.

## Interface

### Modelo de dados 🟢

```
Starter root (IS_CLOSET_STARTER_CAGE, CLASS_NAME)  .hb_closet_starter → Closet_Starter_Props
│   idprops: hb_last_height/depth, hb_remove_hang_rail, hb_bridge_*, hb_l_* (L-shelf)
├── painéis CLOSET_PANEL (N+1), tampo CLOSET_COUNTERTOP, pontes CLOSET_BRIDGE_SHELF
└── bay cage (IS_CLOSET_BAY_CAGE, hb_bay_index, hb_bay_door_swing)  .hb_closet_bay → Closet_Bay_Props
    ├── prateleira inferior/superior, rodapé, cleat, trilho, fundo aplicado/central, prateleiras divisoras
    ├── portas do vão (hb_bay_door)
    └── opening cage (IS_CLOSET_OPENING_CAGE, hb_opening_index, hb_opening_side, hb_seg_bottom)
        idprops de config: hb_adj_shelf_qty, hb_drawer_qty, hb_drawer_front_height, hb_door_swing, hb_is_hamper, hb_cubby_cols/rows
        └── peças: reguláveis, fixas, varões (+cabides), portas, frentes + caixas de gaveta, nichos, puxadores
Scene.hb_closets → Closets_Scene_Props (padrões, opções de sala, modo de seleção)
```

A configuração das aberturas fica em **ID properties** soltas; os **regeneradores** criam/removem peças até convergir. 🟢

### Núcleo (`types_closets.py`, `solver_closets.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `solver_closets.distribute_widths` | `(total_width, panel_thickness, bays)` | `list[float]` | Travas, mín. 1", escala se todos travados (`solver_closets.py:26`) 🟢 |
| `solver_closets.compute_layout` | `(spec)` | `{widths, panels, bays}` | Puro, sem `bpy` (`:63`) 🟢 |
| `ClosetStarter.create_starter` | `(name, bay_qty=DEFAULT_BAY_QTY)` | — | Constrói sob guardas e faz um `recalculate()` (`types_closets.py:253`) 🟢 |
| `ClosetStarter.recalculate` | `()` | — | Propagação → spec → solver → layout (`:458`) 🟢 |
| `_layout_panels` / `_layout_bays` / `_layout_opening_parts` / `_layout_starter_parts` / `_layout_bridge_parts` | — | — | Escrevem location e inputs GN (`:523`, `:532`, `:691`, `:1244`, `:1279`) 🟢 |
| `_reconcile_adj_shelves` / `_doors` / `_drawers` / `_cubbies` / `_bay_openings` / `_bay_doors` | `(opening \| bay, …)` | — | Regeneradores (`:1011-1242`) 🟢 |
| `insert_bay` / `delete_bay` | `(anchor_index, direction)` / `(bay_index)` | — | (`:1344`, `:1404`) 🟢 |
| `BaseClosetStarter`, `TallClosetStarter`, `HangingClosetStarter`, `IslandClosetStarter`, `DoubleIslandClosetStarter` | — | — | (`:1449-1487`) 🟢 |
| `LShelfClosetStarter` (+ Base/Tall/Upper) | `create_starter(name, bay_qty=1)`, `recalculate()` | — | Não herda de `ClosetStarter` (`:1490-1720`) 🟢 |
| `CLOSET_NAME_DISPATCH`, `get_starter_class`, `auto_bay_qty` | — | — | (`:1726`, `:1744`, `:1749`) 🟢 |
| `find_starter_root` / `_wrap_starter` / `recalculate_closet_starter` | `(obj)` | — | Entrada de recálculo (`:1896-1914`) 🟢 |
| `apply_door_open` / `apply_drawer_open` | `(obj, frac)` | — | Giro na dobradiça / deslize (`:1770`, `:1834`) 🟢 |
| `_distribute_front_heights` | `(avail, fronts)` | — | Pilha de gavetas (A3) (`:1813`) 🟢 |
| `serialize_opening` / `apply_opening_data` / `serialize_bay` | — | `dict` | Copiar/colar (`:1958-2005`) 🟢 |
| `apply_bay_config` / `apply_opening_config` | `(bay_obj \| opening, config)` | `bool` | Presets `BAY_CONFIGS` (15) e `OPENING_CONFIGS` (12) (`:2117`, `:2242`) 🟢 |

### Sistemas e opções de sala

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `drawer_boxes_closets.size_box` | `(box_type, avail_h, avail_d, wood_h, wood_d)` | tamanho | A4: maior padrão que cabe (`drawer_boxes_closets.py:65`) 🟢 |
| `update_room` (materiais, frentes, puxadores, caixas) | `(self, context)` | — | Percorre a cena e recalcula todos os starters (`materials_closets.py:307`, `fronts_closets.py:230`, `pulls_closets.py:384`, `drawer_boxes_closets.py:107`) 🟢 |
| `molding_closets.add_crown_to_starter` / `clear_starter_molding` | `(root, profile)` / `(root)` | — | A6, estático (`molding_closets.py:153-218`) 🟢 |
| `gpu_overlay_closets.parse_distance` | `(text)` | `float` | Rótulos editáveis (`gpu_overlay_closets.py:174`) 🟢 |
| `const_closets` | constantes | — | Espessuras, 32 mm (`:126-140`) 🟢 |

### Operadores (`operators/`, `bl_idname` `hb_closets.*`)

| Grupo | Operadores | Observação |
|-------|-----------|------------|
| Inserção | `place_starter` (modal, `ops_closet.py:405`) | `invoke` + modal; preview com `HB_CURRENT_DRAW_OBJ` 🟢 |
| Estrutura | `insert_bay`, `delete_bay`, `delete_starter`, `change_bay`, `copy/paste_bay`, `clear_bay`, `set_corner_clearance` | `ops_closet.py:1491-2653` 🟢 |
| Aberturas | `add_part` (modal), `add_adj_shelves`, `add_drawers`, `add_doors`, `add_cubbies`, `change/copy/paste/clear_opening`, `adj_shelf_step`, `delete_part` | `ops_closet.py:1559-2390` 🟢 |
| Diálogos | `starter_prompts`, `bay_prompts` | `ops_closet.py:2419`, `:2468` 🟢 |
| Acessórios | `change_hanger`, `randomize_hangers`, `install_model_pack`, `add/delete_molding` | `ops_closet.py:2659-2835` 🟢 |
| Modos | `toggle_mode` (sem `UNDO`), `grab_mode` / `grab_hover` / `grab_drag` (keymap + POST_PIXEL), `open_door_mode` (timer, sem `UNDO`) | `ops_closet.py:298`; `op_grab_closet.py:328-369`; `op_open_door_closet.py:80` 🟢 |

## Fluxo Principal

### F1. Registro 🟢
`closets/__init__.py:10-21`: props → menus → operadores → overlay GPU (inverso no `unregister`). Cria
`Scene.hb_closets`, `Object.hb_closet_starter`, `Object.hb_closet_bay` (`props_closets.py:508-533`). Grab e overlay
registram draw handlers POST_PIXEL permanentes + keymaps e os removem no `unregister`.

### F2. Inserção 🟢 (fluxograma `flowcharts/legacy-closets-position_on_wall.md`)
1. `invoke` resolve a classe por `CLOSET_NAME_DISPATCH` (ou duplica um starter), cria preview com ARRAY (1 célula ×
   `bay_qty`) e entra em modal.
2. MOUSEMOVE: `_position_on_wall` (gap fill, snaps esq./dir./centro com histerese, recuo de canto 1/2", lado da parede)
   ou `_position_free` (grade; ilhas com folgas e detentes de corredor).
3. Teclas: W/números (largura/offset), ↑/↓ (vãos 1–9), ←/→ (offset ou folga de ilha), R (gira 90°), F (fill ao duplicar).
4. LMB → `_finalize`: `create_starter` → posiciona → `sp.width = largura` (recalcula) → acabamento → destaques → diálogo
   `set_corner_clearance` se há vizinho perpendicular. ESC/RMB → `_cancel` (remove handler e preview).

### F3. Criação 🟢
`create_starter`: semeia props da cena, cria N+1 painéis, tampo opcional, N vãos com `(W − (N+1)·pt)/N` e, por vão,
prateleiras, rodapé, cleat, fundo (ilha), rodapé traseiro + fundo central + opening BACK (ilha dupla) e a opening FRONT;
um `recalculate()` no fim.

### F4. Recálculo 🟢 (fluxogramas `legacy-closets-recalculate.md`, `legacy-closets-compute_layout.md`)
1. Guarda `id(obj)` em `_RECALCULATING`.
2. Propaga altura/profundidade do starter só aos vãos que estavam no valor anterior (`hb_last_height/depth`).
3. `_spec_from_props` → `compute_layout` → grava larguras sob `_DISTRIBUTING_WIDTHS` (sem travar).
4. `_layout_panels`; `_layout_bays` (prateleiras, rodapés, cleat, trilho, fundos, divisoras → segmentos →
   `_reconcile_bay_openings` → `_layout_opening_parts`, portas do vão); tampo; pontes.
5. Ancora suspensos no topo; escreve `Dim X/Y/Z` do root.

### F5. Peças da abertura 🟢 (fluxograma `legacy-closets-layout_opening_parts.md`)
Regeneradores reconciliam filhos com os idprops → sobreposição meia-espessura → por filho: fixa (offset com clamp),
varão (eixo a ≤ 12", cabides), reguláveis (espaçamento igual), portas (folhas, estilo, puxador, estado aberto),
gavetas (pilha que preenche, caixa do sistema), nichos.

### F6. Presets de vão 🟢 (fluxograma `legacy-closets-apply_bay_config.md`)
`clear_bay_contents` → recálculo (1 opening por lado) → splits e idprops conforme o preset → recálculo.

### F7. Edição 🟢
Três caminhos convergem no mesmo recálculo: diálogos/update callbacks (`props_closets.py:68-94`), rótulos GPU
(`gpu_overlay_closets._commit`, `:616-720`) e grab (`op_grab_closet._apply_drag`, `:560-661`, snap 32 mm com
snapshot/rollback).

### F8. Opções de sala 🟢
Enums de cena com `update_room` percorrem `scene.objects` e recalculam/reaplicam em todo starter.

## Fluxos Alternativos

- **Vão livre abaixo de 1":** solver usa 1" e a soma não fecha (degradação visível). 🟢
- **Todos travados:** escala proporcional. 🟢
- **Nenhuma caixa de gaveta cabe:** usa a menor do sistema. 🟢
- **Excluir o único vão:** exclui o starter. 🟢
- **Exceção no modal de inserção:** sem `try/except` → handler de cotas órfão. 🟡
- **Carregar arquivo com grab ativo:** `_drag_op` global não é limpo; o grab fica travado (sem `load_post`). 🟡
- **`unregister()` com Open Door ativo:** timer e modal não encerrados. 🟢
- **Erro em estilo/material/draw/registro:** `except Exception: pass`. 🟢
- **Fora do pacote de extensão:** `user_hangers_dir` monta o pacote errado para `extension_path_user`. 🟡

## Dependências

- [`hb_core`](../hb_core/): `GeoNodeCage/Cutpart/Object/DrawerBox`, `CabinetPartModifier`, `GeoNodeWall`, `hb_utils` (GN). 🟢
- [`hb_placement`](../hb_placement/): `PlacementMixin`, `PlacementDimSpec` (4 posicionais), `duplicate_object_hierarchy`,
  `TypingTarget`; `hb_snap`, `hb_gpu_draw`. 🟢
- [`frameless`](../frameless/): `CabinetPart`, `toggle_cabinet_color`. 🟢
- [`face_frame`](../face_frame/): `split_preview`, `pulls.pull_length`, `_detect_wall`, material de vidro,
  `apply_active_finish_to_product`. 🟢
- `units` / `data.units`; `operators.viewport_hud`. 🟢
- Node groups `GeoNodeClosetRod`, `CPM_5PIECEDOOR`, `CPM_CORNERNOTCH` — interfaces em
  [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md). 🟢
- Assets `assets/materials/library.blend`, `accessory_finishes.blend`, `assets/handles`, `assets/hangers`,
  `assets/moldings/crown`, `closet_thumbnails`. 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Solver puro + recálculo imperativo (sem drivers) | `types_closets.py:1-8`; `solver_closets.py` | 🟢 |
| Painéis compartilhados entre vãos (N+1) | `solver_closets.py:10-17` | 🟢 |
| Configuração de aberturas em idprops + regeneradores convergentes | `types_closets.py:1011-1242` | 🟢 |
| Sistema 32 mm como retícula de alturas e de snap (sem furação) | `const_closets.py:126-140`; `op_grab_closet.py:534-558` | 🟢 |
| Caixas de gaveta por catálogo de sistema (Metabox/Avantech) | `drawer_boxes_closets.py:40-85` | 🟢 |
| Opções de sala globais aplicadas a todos os starters | `update_room` nos módulos de opção | 🟢 |
| Edição direta por overlay GPU e grab com snapshot/rollback | `gpu_overlay_closets.py`; `op_grab_closet.py:471-823` | 🟢 |
| Moldura estática regenerada sob comando | `molding_closets.py:393-405` | 🟢 |
| Mistura de polegadas (espessuras/folgas) e mm (alturas/caixas) | `const_closets.py:1-5` | 🟢 |

## Estado Interno

- **Por objeto** (`bpy.props`): `hb_closet_starter`, `hb_closet_bay`. Persistido. 🟢
- **Idprops** de configuração e estado (aberturas, frentes, caixas, peças, root). Persistidos; sem tipo/validação. 🟢
- **Por cena**: `Scene.hb_closets`. Persistido. 🟢
- **Globais de processo**: `_RECALCULATING`, `_DISTRIBUTING_WIDTHS` (por `id`), `_drag_op` (grab), `_active` (open door). 🟢
- **Draw handlers**: grab e overlay (permanentes), cotas do modal (temporário), timer do open door. 🟢
- **Objetos gerados** (puxadores, cabides, perfis de moldura) linkados em `scene.collection`, não na coleção do produto. 🟢

## Observabilidade

- Sem logging estruturado. 🟢
- `report` nos operadores; muitas falhas silenciosas (`except Exception: pass`). 🟢
- Idprops como `hb_pull_name` e `hb_drawer_box_size` existem "para precificação", mas nenhum consumidor foi localizado. 🔴

## Riscos e Lacunas

- 🔴 Sem furação 32 mm, minifix ou cavilhas; sem lista de corte nem orçamento.
- 🔴 Lado BACK da ilha dupla sem puxador e sem portas de vão.
- 🟢 `Material.use_nodes` obsoleto (`materials_closets.py:121`).
- 🟢 Linhas grossas com `UNIFORM_COLOR` + `line_width_set` (`op_grab_closet.py:273-301`) — usar `POLYLINE_UNIFORM_COLOR`.
- 🟢 `open_door_mode` e `toggle_mode` sem `UNDO`; `bpy.ops` em callback `update=` (`props_closets.py:97-100`).
- 🟢 Open Door sem remoção de timer no `unregister`; registro que engole exceções.
- 🟢 Helpers GN de `hb_utils` em vez de `compat.py`.
- 🟡 Grab travado após carregar arquivo; handler de cotas órfão em exceção; guardas por `id`.
- 🟡 `closet_type` sem valor para ilha dupla e L-shelf; `DOORS_OPEN_*` não abre portas; `_cfg_hamper` e `spec.kick_setback` sem uso.
- 🟢 Premissas americanas: chapa 19,05 mm, profundidade 14" (356 mm), vão até 42" (1067 mm), varão a 12" da parede,
  puxador a 45" — decisão de mercado em `product_common` Q-06; valores BR em [`questions.md`](questions.md).
