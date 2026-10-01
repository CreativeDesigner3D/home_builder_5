# frameless — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-30, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#frameless`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/frameless/`;
> linhas sem arquivo referem-se ao arquivo da seção. Namespace de operadores legado: `hb_frameless.*`.

## Interface

### Hierarquia de objetos de um gabinete 🟢

```
Cabinet cage (IS_FRAMELESS_CABINET_CAGE, prompts do gabinete, CABINET_TYPE)
├── CabinetPart: laterais, base, fundo, tampo/travessas/avental, rodapé, niveladores
├── Bay cage (IS_FRAMELESS_BAY_CAGE)            ← add_cage_to_bay (types_frameless.py:52)
│   └── Opening cage (IS_FRAMELESS_OPENING_CAGE, prompts de abertura)
│       ├── "Overlay Prompt Obj" (empty com os overlays calculados)
│       ├── Splitter (IS_FRAMELESS_SPLITTER_*_CAGE) → divisórias + Openings filhas
│       ├── Frentes: CabinetDoor / CabinetDrawerFront / FlipUp / Pullout (IS_CABINET_FRONT…)
│       │   ├── Puxador (IS_CABINET_PULL)  └── Caixa de gaveta (IS_DRAWER_BOX)
│       └── Interior cage (IS_FRAMELESS_INTERIOR_CAGE) → prateleiras/divisórias (IS_FRAMELESS_INTERIOR_PART)
└── Laterais aplicadas (IS_APPLIED_END_*), bancada/molduras (estáticas, fora da hierarquia paramétrica)
```

Todas as medidas filhas são **drivers** sobre `Dim X/Y/Z` do pai e prompts (ID properties) da raiz/abertura.

### Tipos (`types_frameless.py`, `types_products.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Cabinet` | atributos `width=18"`, `height=34"`, `depth=24"`, `default_exterior="Doors"` | — | Base de todos (`:8-14`) 🟢 |
| `Cabinet.create_cabinet` | `(name)` | — | Cage raiz + prompts (`:16-50`, `:114`) 🟢 |
| `Cabinet.create_base_carcass` / `create_tall_carcass` / `create_upper_carcass` | `()` | — | Peças com `driver_input/location/hide` (`:125`, `:315`, `:457`) 🟢 |
| `Cabinet.add_cage_to_bay` | `(cage)` | — | Insere abertura no vão (`:52`) 🟢 |
| `Cabinet._add_leg_levelers` | `()` | — | 4 niveladores de `frameless_assets/leg_levelers/Leg Leveler.blend` (`:77-92`) 🟢 |
| `BaseCabinet` | dims da cena | — | `add_exterior` (`:558`), `add_drawer_stack` (`:593`) 🟢 |
| `LapDrawerCabinet`, `TallCabinet(is_stacked)`, `RefrigeratorCabinet`, `UpperCabinet(is_stacked)` | `.create(name)` | — | (`:623`, `:780`, `:822`, `:870`) 🟢 |
| `SplitterVertical` / `SplitterHorizontal` | atributos `splitter_qty=1`, `opening_sizes=[]`, `opening_inserts=[]` | — | 0 em `opening_sizes` = igual (`:918-1140`) 🟢 |
| `CabinetOpening` | `half_overlay_*` | — | `add_properties_front_overlays` (`:1156`), `…_calculations` (`:1178`) 🟢 |
| `Doors`, `Drawer`, `FlipUp`, `Pullout`, `Appliance`, `CabinetShelves`, `CabinetDoor`, `CabinetDrawerFront` | `.create(name)` | — | Frentes e interiores (`:1271-1926`) 🟢 |
| `InteriorSplitterVertical/Horizontal` | idem splitter | — | (`:2050-2277`) 🟢 |
| `CornerCabinet` e derivadas Pie-cut/Diagonal | `corner_size=36"`, `door_pull_location="Base"` | — | `add_corner_doors` (`:2326-2446`); diagonais alto/aéreo stubs 🔴 (`:2302-2921`) 🟢 |
| `Product` e `FloatingShelf`, `Valance`, `SupportFrame`, `HalfWall`, `MiscPart`, `Leg`, `TallLeg`, `UpperLeg`, `Panel` | `.create(name)` | — | `IS_FRAMELESS_PRODUCT_CAGE`, `PART_TYPE` (`types_products.py:8-905`) 🟢 |

### Propriedades e estilos (`props_hb_frameless.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Frameless_Scene_Props` | `Scene.hb_frameless` | — | Padrões, estilos, detalhes, puxadores, bancada (`:1341-2518`) 🟢 |
| `Frameless_Cabinet_Style.assign_style_to_cabinet` | `(cabinet_obj)` | — | Materiais por face, fita, CPM, overlay (`:693-866`) 🟢 |
| `Frameless_Cabinet_Style.get_finish_material` / `get_interior_material` | `()` | `Material` | Node group "Wood" de `cabinet_material.blend` (`:636`, `:671`) 🟢 |
| `Frameless_Door_Style.assign_style_to_front` | `(front_obj)` | `True \| False \| str` | String = mensagem de erro (frente pequena) (`:1044-1162`) 🟢 |
| `update_*` (callbacks) | `(self, context)` | — | Alturas por pé-direito (`:426-434`), caixas de gaveta (`:436-450`), modo de seleção chama `bpy.ops` (`:455`) 🟢 |
| `get_pull_enum_items`, `load_pull_object`, `get_or_create_pull_finish_material` | — | — | Puxadores de `frameless_assets/cabinet_pulls` (`:37-353`) 🟢 |
| `finish_colors.get_all_stain_colors` / `save_custom_color` | — | — | Cores + JSON do usuário (`finish_colors.py:175-269`) 🟢 |
| `wood_materials.update_finish_material` | `(cabinet_style)` | — | Parâmetros de grão por espécie (`wood_materials.py:22-168`) 🟢 |

### Operadores (`operators/`, `bl_idname` `hb_frameless.*`)

| Grupo | Operadores principais | Observação |
|-------|----------------------|------------|
| Inserção | `place_cabinet` (modal), `draw_cabinet`, `toggle_mode` | `ops_placement.py:270`, `:1927`, `:1866`; `draw_cabinet`/`toggle_mode` sem `UNDO` 🟢 |
| Gabinete | `cabinet_prompts`, `drop_cabinet_to_countertop`, `add/remove_applied_end`, `delete_cabinet`, `create/select_cabinet_group`, `adjust_multiple_cabinet_widths`, `finish_interior` | `ops_cabinet.py`; prompts alteram dados em `check()` 🟢 |
| Abertura/interior/frente | `change_bay_opening` (30 tipos), `opening_prompts`, `change_opening_type`, `custom_vertical/horizontal_splitter`, `interior_prompts`, `change_interior_type`, `custom_interior_*`, `door_front_prompts`, `delete_front` | `ops_opening.py`, `ops_interior.py`, `ops_front.py` 🟢 |
| Estilos | CRUD de estilos de porta/gabinete, `assign_cabinet_style_to_selected_cabinets` (modal), `update_fronts_from_style` | `ops_styles.py`; lote por timer (`:673-789`) 🟢 |
| Padrões | `update_toe_kick_prompts`, `update_material_thickness_prompts`, `update_door_and_drawer_front_style`, `update_cabinet_sizes` (2 TODO) | `ops_defaults.py`; sem `UNDO` 🟢 |
| Pós-processamento | `add/remove_countertops`, `assign_crown_to_cabinets/room`, `assign_toe_kick_to_cabinets`, `assign_upper_bottom_to_cabinets`, detalhes 2D | `ops_countertop.py`, `ops_crown.py`, `ops_toe_kick.py`, `ops_upper_bottom.py` 🟢 |
| Produtos/biblioteca/snap/limpeza | `product_prompts`, `convert_to_door_panel`, `adjust_floating_shelves`, `save/load_cabinet_group…`, `place_snap_line`, `cleanup_mesh`… | `ops_products.py`, `ops_library.py`, `ops_snap_line.py`, `ops_cleanup.py` 🟢 |

## Fluxo Principal

### F1. Registro 🟢
1. `frameless/__init__.py:10-14`: props → templates → 17 módulos de operadores → menus.
2. `Frameless_Scene_Props.register` cria `Scene.hb_frameless`; templates criam `Scene.hb_template_refrigerator_range`
   e `Scene.hb_template_island` (`props_elevation_templates.py:1558-1565`).
3. Vários `register()` engolem exceções (`props_hb_frameless.py:2537-2548`, `operators/ops_placement.py:1986-1997`).

### F2. Inserção modal 🟢 (fluxograma `flowcharts/legacy-frameless-place_cabinet_modal.md`)
1. Biblioteca → `hb_frameless.draw_cabinet(cabinet_name)` → `place_cabinet` com `'INVOKE_DEFAULT'`; o modal começa em
   `execute()` (não há `invoke`) 🟡.
2. `create_preview_cage` (ARRAY com a quantidade) + cotas como objetos GN; `modal_handler_add`.
3. MOUSEMOVE: raycast (`hb_snap`) → parede GN ou parede mais próxima ≤ 6" → `set_position_on_wall`; senão piso com snap.
4. Na parede: lado por Y local (histerese 1"), `find_placement_gap_by_side`, preenchimento `qtd = ceil(gap/36")` ou snap
   de centro/borda 4"; canto encosta na ponta.
5. ↑/↓ muda a quantidade; W/H/setas/dígitos → `handle_typing_event`.
6. LMB/Enter → `create_final_cabinets`: `get_cabinet_class()` → `create()` → `assign_cabinet_style` → `run_calc_fix` ×2
   (contorno do bug Blender #133392) → estilos de porta → `calculate_shelf_quantity` → `toggle_mode`. RMB/Esc cancela.

### F3. Carcaça do inferior 🟢 (fluxograma `flowcharts/legacy-frameless-create_base_carcass.md`)
1. Lê `Toe Kick Type` uma vez (`:144`).
2. Laterais: tipo 0 → altura total + `CPM_CORNERNOTCH` (X = tkh, Y = tks); tipos 1–3 → começam em `tkh`.
3. Base, fundo (`z = tkh + mt`), topo (tampo/travessas/avental com `driver_hide`), rodapé `y = −dim_y + tks`.
4. Bay com origem/dimensões de RN-06; "Remove Bottom" oculta base/rodapé.
5. Tipo 3 → `_add_leg_levelers`.

### F4. Splitter 🟢 (fluxograma `flowcharts/legacy-frameless-splitter_vertical.md`)
1. Cage + empty "Calc Object" + calculadora "Opening Calculator" com prompts `Opening i Height`.
2. `total_distance = dim_z − mt·qtd` (driver).
3. De cima para baixo: divisória `z = anterior − oh_i − mt`; abertura `z = divisória + mt` (última em 0).
4. Inserts filhos com drivers de dimensão e `FORCE_HALF_OVERLAY_*`.
5. Tamanhos ≠ 0 viram fixos; `calculate()` rateia os iguais. Não é driver: mudar `Dim Z` depois exige rodar a calculadora.

### F5. Frentes e sobreposição 🟢 (fluxograma `flowcharts/legacy-frameless-front_overlay.md`)
1. Prompts da abertura (reveal, gaps, espessuras = `mt`).
2. Empty "Overlay Prompt Obj" calcula `to/bo/lo/ro` (inset / meia / total).
3. Porta: posição/tamanho de RN-16; Door Swing oculta a folha oposta.
4. Gaveta: frente copia os overlays; caixa com folgas 0,5/0,75/1/0,5".
5. Puxador por `Pull Location` e posições da cena.
6. Interior: prateleiras em array com quantidade padrão de RN-18.

### F6. Troca de vão 🟢
`change_bay_opening` apaga os filhos do Bay e recria a configuração escolhida (30 tipos, `ops_opening.py:98-141`,
`execute` `:587`); depois `assign_pull_locations_to_cabinet` (`:68`) aplica RN-23/RN-24.

### F7. Estilos 🟢
1. `assign_style_to_cabinet`: material de acabamento/interior por `Finish Top/Bottom`, fita nas 4 bordas, materiais dos
   CPM, flags de overlay (respeitando `FORCE_HALF_OVERLAY_*`), grava `CABINET_STYLE_INDEX/NAME`.
2. `assign_style_to_front`: SLAB remove `Door Style`; 5 peças valida o mínimo, adiciona `CPM_5PIECEDOOR` e materiais
   (montante normal, travessa ROTATED), travessa central automática > 45,5".
3. Pintura em lote por timer modal; remoção de estilo reindexa (`ops_styles.py:376-422`).

### F8. Pós-processamento 🟢 (fluxogramas `legacy-frameless-create_wall_countertop.md`, `legacy-frameless-assign_crown.md`)
1. Bancada: `gather_base_cabinets` → `split_cabinets_at_ranges` → `build_wall_runs` (corridas por parede conectada) →
   malha com balanços e L de canto; ilha separada; recorte booleano `EXACT` (`ops_countertop.py:727`).
2. Crown/rodapé/moldura inferior: componentes conexos por AABB (±2 cm), polilinha deslocada com esquadria
   (`_offset_polyline_right`, `ops_crown.py:835-871`), perfil 2D da cena de detalhe extrudado por `bevel_object`.

### F9. Templates de elevação 🟢
Seleciona parede → preview de cages rotuladas atualizadas por callbacks `update=` → `draw_cabinets` cria os
gabinetes reais e aplica estilos (`props_elevation_templates.py:566`, `:1136`).

## Fluxos Alternativos

- **Porta 5 peças abaixo do mínimo:** `assign_style_to_front` devolve string de erro; a porta fica sem `CPM_5PIECEDOOR`. 🟢
- **`opening_sizes` curta no splitter vertical:** `IndexError` (`types_frameless.py:1021`); o horizontal checa (`:1135`). 🟢
- **Mudar Toe Kick Type depois:** sem efeito na geometria. 🟡
- **Sem parede perto do cursor:** inserção no piso com snap a vizinho/grade. 🟢
- **Chamada com `EXEC_DEFAULT`:** modal sem evento válido. 🟡
- **Registro com falha:** exceção engolida; sintoma aparece depois. 🟢
- **Cena de layout/detalhe ativa:** padrões vêm de `bpy.context.scene.hb_frameless` e estilos da cena principal (leituras mistas: 77 × 89). 🟡
- **Caminho interno do Blender ausente:** "Smooth by Angle" de `datafiles/assets/nodes/geometry_nodes_essentials.blend` falha em silêncio. 🟡
- **Gabinete redimensionado após bancada/moldura:** geometria estática não acompanha. 🟢

## Dependências

- [`hb_core`](../hb_core/): `GeoNodeCage/Cutpart/Hardware/DrawerBox/Wall/Dimension/Rectangle`, `CabinetPartModifier`,
  prompts e calculadora (`hb_props`), `run_calc_fix`, `get_*_bp`, `delete_obj_and_children`, `get_main_scene`. 🟢
- [`hb_placement`](../hb_placement/): `PlacementMixin`, `hb_snap`. 🟢
- [`hb_layouts`](../hb_layouts/): `hb_details`, `hb_detail_library` (cenas de detalhe), `hb_assets` (caminhos). 🟢
- [`product_common`](../product_common/): `types_appliances` (Range, Dishwasher, Refrigerator, Hood…). 🟢
- `units` (`inch`, `meter_to_inch`, `unit_to_string`). 🟢
- Node groups `CPM_CORNERNOTCH`, `CPM_CHAMFER`, `CPM_CUTOUT`, `CPM_5PIECEDOOR` — interfaces em
  [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md). 🟢
- Assets `frameless_assets/` (puxadores, niveladores, `cabinet_material.blend`). 🟢
- Operadores externos `home_builder_layouts.go_to_layout_view`, `home_builder_details.*`, `pc_prompts.*`. 🟢
- Consumidor: `cutting/part_extractor.py` **não** lê os `CabinetPart` legados (lacuna L1 de `soul.md`). 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Construção europeia: laterais passantes, peças entre laterais | `types_frameless.py:198-241` | 🟢 |
| Fundo de chapa cheia (`mt`) embutido, sem rasgo para fundo fino | `types_frameless.py:206-216` | 🟢 |
| Parametrização por drivers + calculadora de vãos | `types_frameless.py:918-1026`; `hb_props.py:294-330` | 🟢 |
| Sobreposição calculada num empty separado para quebrar ciclo de dependência | `types_frameless.py:1178-1210` | 🟢 |
| Prompts como ID properties (não `bpy.props`) | `hb_props.py:335-374` | 🟢 |
| Estilos vinculados por índice na coleção da cena principal | `ops_styles.py:376-422` | 🟢 |
| `run_calc_fix` ×2 como contorno do bug Blender #133392 | `operators/ops_placement.py:1837-1839` | 🟢 |
| Pós-processamento (bancada, molduras) como malha estática | `ops_countertop.py`, `ops_crown.py` | 🟢 |
| Padrões americanos em polegadas | `props_hb_frameless.py:1425-1698` | 🟢 |
| Material de madeira procedural por espécie | `wood_materials.py:22-168` | 🟢 |

## Estado Interno

- **Por cena** (`Scene.hb_frameless`): padrões de medida, estilos (coleções), detalhes de moldura, puxadores (ponteiros
  de cache), bancada, modo de seleção. Persistido. 🟢
- **Templates** (`Scene.hb_template_*`): parâmetros + ponteiros para objetos de preview. Persistido. 🟢
- **Por gabinete/abertura/frente** (ID props): prompts, `CABINET_TYPE`, `CORNER_TYPE`, `CABINET_STYLE_INDEX/NAME`,
  `DOOR_STYLE_INDEX/NAME`, `FORCE_HALF_OVERLAY_*`, `Finish Top/Bottom`, `MENU_ID`, marcadores `IS_*`. Persistido. 🟢
- **Calculadoras**: `Object.home_builder.calculators` no empty "Calc Object". Persistido; recalcula só quando chamado. 🟢
- **Arquivo do usuário**: `custom_colors.json` e biblioteca de grupos em `extension_path_user`. 🟢
- **Runtime do modal**: quantidade, larguras, gaps, lado, snap (atributos do operador). Não salvo. 🟢
- **Runtime do lote de estilos**: `_style`, `_cabinets` entre ticks de timer (invalidáveis por undo). 🟡

## Observabilidade

- Sem logging estruturado. 🟢
- `report({'WARNING'|'ERROR'})` + `CANCELLED` na maioria dos operadores. 🟢
- `print` de depuração em `assign_style_to_front` (dimensões da frente, `props_hb_frameless.py:1078`) e no callback
  de `show_machining`. 🟢
- Muitos `try/except Exception: pass` silenciosos (ex.: `props_hb_frameless.py:1136-1143`). 🟢

## Riscos e Lacunas

- 🔴 Cantos diagonais alto/aéreo são stubs; diagonal inferior sem portas.
- 🔴 Rodapé Ladder, rollouts e TRAY_DIVIDERS não implementados; 2 TODO em `ops_defaults.py:58-73`.
- 🔴 Propriedades de cena sem efeito (`base_exterior`, blind corner, `show_machining`, `RAISE_UPPER`, `edge_profile_type`, perfis).
- 🔴 Sem lista de corte própria; o `cutting` não lê os `CabinetPart` legados.
- 🟢 `Material.use_nodes` e `blend_method` obsoletos (`props_hb_frameless.py:269, 310, 313`; `ops_snap_line.py:46, 53`; `ops_library.py:227`).
- 🟢 Enums dinâmicos sem cache das strings e com I/O a cada redraw (`props_hb_frameless.py:108-134`; `finish_colors.py:207-225`).
- 🟢 `bpy.ops` dentro de callback `update=` (`props_hb_frameless.py:455`).
- 🟢 Operadores que alteram dados sem `UNDO`; diálogos que alteram dados em `check()`.
- 🟢 Mínimo de porta 5 peças (+1") divergente da coifa (+1/2") — decidido em `product_common` Q-05: unificar em +1".
- 🟢 O preview do `place_cabinet` não grava `HB_CURRENT_DRAW_OBJ` (decidido em `hb_placement` Q-05 → T-25).
- 🟡 `SplitterVertical` sem checagem de tamanho de `opening_sizes`.
- 🟡 Leituras mistas de `hb_frameless` entre cena corrente e cena principal.
- 🟡 Thumbnail de grupo altera configurações de render da cena sem restaurar (`ops_library.py:278-307`).
- 🟡 Código de agrupamento triplicado entre crown, rodapé e moldura inferior.
- 🟢 Medidas americanas (chapa 19,05 mm, inferior 876 mm, aéreo a 1372 mm) — decidido em `product_common` Q-06:
  preset brasileiro padrão, alternável.
