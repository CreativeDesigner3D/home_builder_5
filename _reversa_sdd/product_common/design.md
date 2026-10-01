# product_common — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#product_common`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`; linhas sem arquivo referem-se
> ao arquivo da seção.

## Interface

### Motor de portas (`product_libraries/common/door_builder.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `USE_PYTHON_DOORS` | constante | `True` | Liga o motor Python no lugar do GN `CPM_5PIECEDOOR` (`:30`) 🟢 |
| `DOOR_STYLE_FALLBACK` | constante `dict` | — | 5_PIECE, membros 3", `mid_rail_location` 12", painel 1/2" × recuo 1/4" (`:36-66`) 🟢 |
| `door_style_info` | `(style=None)` | `DoorStyleInfo` (`dict`) | Cópia do fallback preenchida por `getattr(style, campo)`; desacopla o cálculo do RNA (`:87`) 🟢 |
| `_frame_widths` | `(info)` | `(lsw, rsw, msw, trw, brw, mrw)` | Pisos 1/2" (uniformes) e 0.0 (overrides) (`:69-84`) 🟢 |
| `layout_min_size` | `(info)` | `(min_w, min_h)` | SLAB → `(0, 0)` (`:98-110`) 🟢 |
| `door_layout` | `(info)` | `list[DoorPart]` | Peças com pares `(coef, offset)` em W/H (`:113-212`) 🟢 |
| `evaluate_layout` | `(info, width, height)` | `list[DoorPart]` + `x0,x1,z0,z1` | Realizador estático (`:215-227`) 🟢 |
| `shape_rise` | `(curve, w)` | `float` | ARCH `min(0,20·w, 2,25")`; CROWN `min(0,16·w, 1,75")` (`:576-582`) 🟢 |
| `build_mitered_frame` | `(info, W, H, T, member_section)` | `(verts, faces, slots)` | Varredura única com meia-esquadria (`:250-321`) 🟢 |
| `build_door_mesh` | `(mesh, info, width, height, thickness, materials=None, outer_section=None, inner_section=None, panel_section=None, inner_rail_section=None, inner_stile_section=None, member_section=None, applied_section=None, applied_scope='ALL', panel_grooves=None, mullion=None, shape=None)` | `None` | Reescreve `mesh` (efeito colateral) (`:1202-1404`) 🟢 |
| `_emit_*` | `(verts, faces, slots, part, T, seção, …)` | `bool` | `False` = não coube → peça cai para a próxima opção da cadeia (`:349-1199`) 🟢 |

Espaço de saída de `build_door_mesh` 🟢 (`:1208-1215`): altura da porta em **+X** a partir da borda inferior,
largura em **−Y** com a borda esquerda em y=0 (cutpart com Mirror Y), face frontal em **z = thickness**. Cada emissor
mapeia `(x_porta, z_porta, v) → (z_porta, −x_porta, T − v)` (`:272-276`, `:369-371`).

### Perfis (`product_libraries/common/door_profiles.py`)

Espaço comum de seção: **u ≥ 0** da borda do membro para dentro; **v ∈ [0, T]** da face frontal para trás 🟢 (`:12-17`).

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `PROFILE_ROOT` / `PROFILE_DIRS` | constantes | — | `face_frame/face_frame_assets/door_profiles/<Categoria> Profiles` (`:27-37`) 🟢 |
| `profile_path` / `list_profiles` | `(category, name)` / `(category)` | `str` / `list[str]` | Nomes = stem dos `.blend` (`:42-53`) 🟢 |
| `load_profile` | `(category, name, res=16)` | `ProfileData` | Cache `(path, mtime, res)`; `FileNotFoundError`/`ValueError` (`:85-150`) 🟢 |
| `profile_from_object` | `(obj, res=16)` | `ProfileData` | Curva da cena em `matrix_world` (perfis destravados) (`:490-522`) 🟢 |
| `edge_profile_section` | `(profile, T)` | `list[(u, v)] \| None` | Borda externa (OUTER), ajuste à espessura (`:525-610`) 🟢 |
| `sticking_section` / `sticking_strip` | `(profile, T[, panel_front])` | laço fechado \| `None` | Sticking (INNER) (`:245`, `:375-425`) 🟢 |
| `panel_profile_section` | `(profile, max_depth)` | `PanelSection \| None` | Raise (PANEL) (`:271-372`) 🟢 |
| `applied_strip` | `(profile, side='OUT'\|'IN', panel_front)` | laço fechado \| `None` | Moldura aplicada (`:428-459`) 🟢 |
| `member_section` | `(profile, T)` | `list[(u, v)] \| None` | MITERED; largura = `max(u)` (`:462-487`) 🟢 |
| `named_edge_section` | `(name, T)` | `list[(u, v)] \| None` | Perfis de catálogo gerados em código (`:658-677`) 🟢 |
| `sweep_edge_frame` | `(section, width, height, inner=False)` | geometria | Varredura com meia-esquadria em volta de um retângulo, "para builds de revisão e testes" (`:680-710`) 🟢 |

### Eletrodomésticos (`product_libraries/common/types_appliances.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Appliance(GeoNodeCage)` | atributos `width`, `height`, `depth`, `variable_width` | — | Padrão 30×36×24" (`:8-17`) 🟢 |
| `Appliance.create_appliance` | `(name, appliance_type)` | `None` | Cage + marcadores + `GeoNodeText` filho (`:19-51`) 🟢 |
| `Range`, `Cooktop`, `WallOven`, `Dishwasher`, `Refrigerator`, `Microwave`, `Hood`, `Sink`, `WashingMachine`, `Dryer` | `.create(name)` | `None` | Chamam `create_appliance` + `add_property` (`:54-220`) 🟢 |
| `WallOven.set_double_oven` | `(is_double=True)` | — | Altura 51" / 29" (`:95-101`) 🟢 |
| `Refrigerator.set_counter_depth` | `(is_counter_depth=True)` | — | Profundidade 24" / 30" (`:133-139`) 🟢 |
| `Microwave.set_over_range` | `()` | — | Fixa 30×17×16"; não há volta ao padrão (`:156-161`) 🟢 |

### Coifas de madeira (`product_libraries/common/wood_hoods.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `WOOD_HOOD_STYLE_ITEMS` | lista de enum | — | 14 estilos (`:56-71`) 🟢 |
| `build_wood_hood` | `(hood: Object, style: str)` | `None` | Limpa, despacha em `_STYLE_BUILDERS`, grava estilo, reaplica acabamento (`:1762-1770`) 🟢 |
| `find_hood_root` | `(obj)` | `Object \| None` | Sobe até o cage `APPLIANCE_TYPE=='HOOD'` (`:1544`) 🟢 |
| `apply_finish_to_hood` | `(hood_obj, finish_mat, finish_mat_rotated=None)` | — | Cutparts: inputs de superfície/borda; malhas estáticas: material no slot 0 (`:1556-1632`) 🟢 |
| `snapshot_hood_part` | `(hood_part: Object)` | `bool` | JSON em `HOOD_PARAMETRIC_SNAPSHOT`; só peça com modificador GN (`:1635-1685`) 🟢 |
| `restore_hood_part` | `(hood_part: Object)` | `bool` | Recria modificador, inputs, drivers (migrando caminho) e transform; `False` sem snapshot, JSON inválido, sem cage ou sem node group (`:1688-1759`) 🟢 |
| `_migrate_mod_input_path` | `(data_path: str)` | `str` | Converte para o formato da versão em execução (`hb_utils.GN_INPUTS_AS_RNA`): `modifiers["M"]["S"]` ↔ `modifiers["M"].properties.inputs.S.value` (`:46-54`) 🟢 |
| `HOME_BUILDER_OT_build_wood_hood` | `bl_idname = "blendertomob.build_wood_hood"`, `{'REGISTER','UNDO'}`, prop `style` | `{'FINISHED'}` | `poll`: ativo tem `APPLIANCE_TYPE=='HOOD'`; `invoke_props_dialog` (`:1773-1801`) 🟢 |
| `HOME_BUILDER_OT_wood_hood_prompts` | `bl_idname = "blendertomob.wood_hood_prompts"`, `{'UNDO'}` | `{'FINISHED'}` | W/H/D, estilo, opções CUSTOM, `ui_tab`, `bay_front_1..10`; `check()` reconstrói (`:1804-2066`) 🟢 |
| `HOME_BUILDER_OT_revert_hood_part` | `bl_idname = "blendertomob.revert_hood_part"`, `{'UNDO'}` | `{'FINISHED'\|'CANCELLED'}` | Age sobre os selecionados (ou o ativo) com `IS_WOOD_HOOD_PART` + `IS_MANUAL_PART` + snapshot; `poll` falso sem nenhum (`:2193-2226`) 🟢 |
| `register` / `unregister` | `()` | — | Chamados pelo `__init__.py` do add-on, não pelo pacote `common` (`:2236-2243`; `__init__.py:54,244,269`) 🟢 |

### Registries

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `accessory_registry.register_provider` | `(host: str, fn: Callable[[], Iterable[dict]])` | — | Sobrescreve o host (`:14`) 🟢 |
| `accessory_registry.unregister_provider` / `has_provider` | `(host)` | — / `bool` | (`:19-26`) 🟢 |
| `accessory_registry.get_items` | `(host)` | `list[dict]` | `[]` + `print` se o provider falha (`:28-38`) 🟢 |
| `accessory_registry.all_items` | `()` | `list[dict]` | Injeta `host` com `setdefault`; ordem de registro (`:40-54`) 🟢 |
| `all_categories`, `find(code)`, `sections`, `groups`, `group_items`, `lookup(host, code)`, `categories(host)` | — | listas / `dict \| None` | Consultas derivadas (`:57-117`) 🟢 |
| `appliance_spec_registry.register_provider` / `unregister_provider` / `get_provider` | `(obj)` / `()` / `()` | — / — / objeto \| `None` | Provider único (`:17-32`) 🟢 |

## Fluxo Principal

### F1. Frente de armário do face frame com o motor Python 🟢 (fluxograma `flowcharts/legacy-product_common.md` §2)
O consumidor fica em `face_frame/props_hb_face_frame.py:3175-3640`; aqui está só a parte que chama esta unit.
1. `assign_style_to_front` lê Length/Width/Thickness do cutpart e as larguras efetivas por lado.
2. Série mitered (`SERIES_PROFILES.member`) → `member_section(load_profile('MITERED', nome), T)`.
3. Forma Arch/Crown → `shape_rise(curve, cell_w)` e alarga a(s) travessa(s) pelo rise.
4. Frente abaixo do mínimo próprio do consumidor (+1") → caminho SLAB.
5. `info = door_style_info(style)` + overrides (por lado, painel, `mid_rail_z`, twin → `mid_stile_count = 1`).
6. Resolve seções (`edge_profile_section`, `sticking_strip`, `panel_profile_section`, `applied_strip`, ranhuras, mullion)
   com `try/except` amplo; qualquer falha vira `None`.
7. `build_door_mesh(mesh, info, W, H, T, …)`.

### F2. `door_layout` 🟢 (fluxograma `flowcharts/legacy-product_common-door_layout.md`)
1. SLAB → uma peça `slab` cobrindo `(0,0)–(1,0)` em W e H.
2. `_frame_widths` aplica os pisos; `p_th = max(panel_thickness, 1/8")`, `p_in = max(panel_inset, 0)`.
3. Emite montantes esquerdo/direito (altura total) e travessas inferior/superior (entre montantes).
4. Linhas de painel: `mid_rail_count = k > 0` → k mid rails equidistantes (RN-06); senão `mid_rail_z` ou `add_mid_rail`
   → 1 mid rail (centralizado ou fixo); senão 1 linha.
5. Colunas: `mid_stile_count = m > 0` → m+1 colunas (RN-07); senão 1 coluna.
6. Para cada linha: mid stiles segmentados na linha + painéis com `thickness = p_th`, `y_inset = p_in`.

### F3. `build_door_mesh` 🟢 (fluxograma `flowcharts/legacy-product_common-build_door_mesh.md`)
1. `member_section` e não SLAB → `build_mitered_frame` (quadro inteiro); senão listas vazias.
2. `parts = evaluate_layout(info, W, H)`.
3. `shape` (não mitered, não SLAB) → pontos da curva para as células da linha de topo (e de base em Double).
4. Para cada peça (em MITERED, só painéis); pula peças de largura ou altura ≤ 0:
   - painel: raised → grooved (+ tampas arqueadas) → shaped flat → caixa;
   - travessa arqueada: `_emit_shaped_rail` TOP/BOTTOM;
   - peça de contorno com `outer_section`: `_emit_edge_profiled_box`;
   - senão: caixa retangular (8 vértices, 6 faces, `zf = T − y_inset`, slot `_PART_MAT_SLOT[key]`).
5. Não MITERED e não SLAB: sticking por célula (`_emit_strip_rings`, fallback cruzado rail/stile).
6. `applied_section`: moldura aplicada por célula respeitando `applied_scope`.
7. `mullion` (vale também em MITERED): `_emit_mullion_bars` por célula, recortadas sob a curva.
8. `mesh.clear_geometry()`, `from_pydata`, `materials.clear()` + (stile, rail, panel), atributo `material_index`
   `INT`/`FACE` via `foreach_set`, `mesh.update()` (`:1389-1404`).

### F4. Carga de perfil 🟢 (fluxograma `flowcharts/legacy-product_common-door_profiles.md`)
1. `profile_path` → arquivo inexistente = `FileNotFoundError`.
2. Chave `(path, os.path.getmtime, res)` em `_cache` → devolve.
3. `bpy.data.libraries.load(path)` → append de todos os objetos.
4. Para cada curva: aplica `Matrix.LocRotScale`, amostra (Bézier cúbica, `res` por segmento; POLY/NURBS brutos).
5. Vence a spline com mais pontos; `finally` remove objetos e curvas órfãs.
6. Sem pontos → `ValueError`; senão projeta no plano descartando o eixo de menor extensão, remove duplicados, fecha
   laço cíclico e grava no cache.
7. O consumidor converte para a seção da categoria (OUTER/INNER/PANEL/APPLIED/MITERED).

### F5. Criar eletrodoméstico 🟢
1. `Subclasse().create(name)` → `create_appliance(name, TIPO)`.
2. `GeoNodeCage.create`; ID props `IS_APPLIANCE`, `APPLIANCE_TYPE`, `MENU_ID`; `display_type = 'WIRE'`.
3. `Dim X/Y/Z` = `width/depth/height`; `Mirror Y = True`.
4. `GeoNodeText` filho "Appliance Text" com texto = tipo, `IS_APPLIANCE_TEXT`, drivers
   `x = dim_x/2`, `y = −dim_y`, `z = dim_z/2`, rotação X 90°, tamanho `scene.home_builder.annotation_text_size`.
5. A subclasse adiciona prompts via `add_property` (os do tipo `'TEXT'` são ignorados em silêncio).

### F6. Coifa de madeira 🟢 (fluxogramas `flowcharts/legacy-product_common.md` §3 e `legacy-product_common-build_custom_hood.md`)
1. Menu do eletrodoméstico HOOD → `blendertomob.build_wood_hood` (diálogo com `style`) ou
   `blendertomob.wood_hood_prompts`.
2. Prompts: `_apply` grava `Dim X/Y/Z` no cage; se CUSTOM, grava `WOOD_HOOD_CUSTOM_OPTS`; `check()` reconstrói.
3. `build_wood_hood`: `_clear_hood_parts` (apaga `IS_WOOD_HOOD_PART`, preserva `IS_MANUAL_PART`).
4. `_STYLE_BUILDERS.get(style, _build_box)`:
   - retos (BOX, PENINSULA, SHELF, NICHE, MANTLE, PLANTATION, GRAND_MANTLE) → `_build_hood_box`, cutparts com drivers;
   - inclinados (TRADITIONAL, VILLA, CHIMNEY) → `_build_angled`, malha estática;
   - SHIPLAP_* → caixa + `_wrap_shiplap` estático;
   - CUSTOM → `_build_custom`: reta (driven) ou inclinada (estática, via `_FrontProfile`).
5. `hood['WOOD_HOOD_STYLE'] = style`; `_reapply_cabinet_style_finish` (se `STYLE_NAME`).

### F7. Tornar peça editável e reverter 🟢
1. "Make Editable" (`face_frame/operators/ops_part_commands.py:1513-1514`) chama `snapshot_hood_part` e marca
   `IS_MANUAL_PART`.
2. `snapshot_hood_part` serializa `mod_name`, `node_group`, inputs não-geometria (Material/Object →
   `{'__idtype__', 'name'}`), drivers `SINGLE_PROP` e transform.
3. `blendertomob.revert_hood_part` → `restore_hood_part`: recria o modificador, reescreve inputs, recria drivers
   com `_migrate_mod_input_path` e re-aponta variáveis ao cage raiz, restaura transform, remove os dois flags.

### F8. Registries 🟢 (fluxograma `flowcharts/legacy-product_common.md` §4)
1. Hospedeiro externo chama `register_provider` (nenhum no repositório).
2. `face_frame/operators/ops_cabinet.py` monta menus por host/seção/grupo; `ops_appliance_panels.py` preenche
   enums Fabricante/Modelo e aplica o spec (`Dim X`, configuração, tipo de painel).

## Fluxos Alternativos

- **Porta abaixo do mínimo (coifa):** `info = dict(info, door_type='SLAB')` (`wood_hoods.py:729-731`, `:883-886`,
  `:994-996`, `:1304-1307`). 🟢
- **Emissor não cabe:** devolve `False`; a peça vira caixa simples. Nunca há exceção por geometria. 🟢
- **Célula arqueada ≤ 2" ou rise ≤ 1e-6:** `_shape_curve_pts` devolve `None`; sem arco. 🟢
- **Padrão de mullion inválido para o tamanho:** `_mullion_layout` devolve `[]`; vidro sem barras. 🟢
- **Profundidade de mullion ≤ 1e-6:** `_emit_mullion_bars` devolve `False`. 🟢
- **Perfil ilegível:** funções de seção devolvem `None`; o consumidor cai para borda reta/painel plano. 🟢
- **Nome de borda de catálogo desconhecido:** `named_edge_section` → `None` (borda reta). 🟢
- **Face frame indisponível:** imports tardios em `try/except` → coifa sem sobreposição do estilo (1/2") e sem
  acabamento. 🟢
- **Estilo de coifa desconhecido:** `_build_box`. 🟢
- **Revert sem peça elegível na seleção:** `poll` falso; se todas as restaurações falham → `WARNING` "No revertable hood parts (no snapshot)" e `CANCELLED`, peças intactas. 🟢
- **Snapshot inválido, cage ou node group ausente:** `restore_hood_part` devolve `False` e deixa a peça como está. 🟢
- **Provider de acessório falha:** `get_items` → `[]` + `print("HB5 accessory_registry: provider for %s failed")`. 🟢
- **Sem provider de specs:** UI só com "Manual" (`ops_appliance_panels.py:399-401`). 🟢

## Dependências

- `units.inch` — todas as medidas; `door_profiles._INCH = 0.0254` próprio (`door_profiles.py:619`). 🟢
- `hb_types.GeoNodeCage`, `GeoNodeObject`, `GeoNodeCutpart` (`add_part_modifier('CPM_CUTOUT')`, drivers) — unit [`hb_core`](../hb_core/). 🟢
- `hb_details.GeoNodeText` — rótulo do eletrodoméstico — unit [`hb_layouts`](../hb_layouts/). 🟢
- `hb_utils.GN_INPUTS_AS_RNA`, `get_gn_input`, `set_gn_input` — snapshot/restore (não usa `compat.py`). 🟢
- `face_frame.props_hb_face_frame` (`get_style_props`, `cabinet_styles`, `door_styles`, `_OVERLAY_TABLE`,
  `door_overlay_type`, `assign_style_to_hood`) — import tardio protegido — unit [`face_frame`](../face_frame/). 🟢
- `face_frame.style_options` (`SERIES_FRAME`, `SERIES_PROFILES`, `PANEL_KINDS`, `SHAPE_KINDS`, `RECESSED_PANEL`) —
  dados de catálogo que parametrizam o motor (dependência do consumidor). 🟢
- Assets `face_frame/face_frame_assets/door_profiles/*/*.blend`. 🟢
- Consumidores: `face_frame` (props, `ops_cabinet`, `ops_appliance_panels`, `ops_styles`, `ops_part_commands`,
  `types_face_frame`), `frameless` (`ops_placement`, `props_elevation_templates`, `menus_frameless`), `__init__.py`. 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Portas geradas em Python (malha estática) em vez do modificador GN `CPM_5PIECEDOOR` | `door_builder.py:27-30` | 🟢 |
| Layout como pares lineares `(coef, offset)` para servir tanto ao realizador estático quanto a expressões de driver | `door_builder.py:14-19`, `:215-227`; `wood_hoods.py:659-749` | 🟢 |
| Cadeia de fallback por peça: nunca falhar, degradar para geometria mais simples | `door_builder.py:1300-1362` | 🟢 |
| Perfis desenhados como curvas em `.blend` (um por arquivo), orientação detectada pelo desenho | `door_profiles.py:5-17`, `:166-242`, `:525-610` | 🟢 |
| Cache de perfil invalidado por mtime para edição ao vivo do `.blend` | `door_profiles.py:9-10`, `:101-103` | 🟢 |
| Três slots de material fixos (stile, rail, panel) | `door_builder.py:230-235` | 🟢 |
| Coifas retas paramétricas (drivers) e inclinadas estáticas reconstruídas por `check()` | `wood_hoods.py:1457-1459`, `:2059-2061` | 🟢 |
| Edição manual preservada com snapshot reversível em JSON | `wood_hoods.py:82-88`, `:1635-1759` | 🟢 |
| Catálogos externos plugáveis por registry em vez de dados embarcados | `accessory_registry.py`, `appliance_spec_registry.py` | 🟢 |
| Acoplamento fraco com face frame via import tardio protegido | `wood_hoods.py:430-475`, `:1594-1601` | 🟢 |
| Medidas de catálogo americano (CWP) e eletrodomésticos EUA em polegadas | `types_appliances.py`, `door_builder.py:683-693` | 🟢 |

## Estado Interno

- **Cache global de perfis** `door_profiles._cache: dict[(path, mtime, res) → ProfileData]`, sem limite, vive na
  sessão Python. 🟢
- **Registries globais** `accessory_registry._providers: dict[host → fn]` e `appliance_spec_registry._provider`;
  não persistidos. 🟢
- **Por eletrodoméstico** (ID props): `IS_APPLIANCE`, `APPLIANCE_TYPE`, `MENU_ID`, `IS_COUNTERTOP_APPLIANCE`, prompts
  (`Has Hood`, `Is Double Oven`, `Counter Depth`…); inputs GN `Dim X/Y/Z`, `Mirror Y`. Persistidos no `.blend`. 🟢
- **Por coifa**: `WOOD_HOOD_STYLE`, `WOOD_HOOD_CUSTOM_OPTS` (dict IDProperty), `STYLE_NAME`. 🟢
- **Por peça de coifa**: `IS_WOOD_HOOD_PART`, `IS_MANUAL_PART`, `HOOD_PARAMETRIC_SNAPSHOT` (JSON), `hb_part_role`,
  `MENU_ID`. 🟢
- **Porta**: não guarda estado próprio; a malha é recalculada a partir do estilo a cada `assign_style_to_front`. 🟢
- **Runtime do diálogo de prompts**: `ui_tab`, `bay_front_1..10` (não persistidos além de `_apply`). 🟢

## Observabilidade

- Sem logging estruturado. 🟢
- `print` em falha de provider de acessórios (`accessory_registry.py:28-54`). 🟢
- `load_profile` levanta `FileNotFoundError`/`ValueError` com o caminho; os consumidores costumam engolir. 🟢
- Emissores sinalizam só por `bool`; não há registro de qual fallback foi usado. 🟢
- `revert_hood_part` emite `report` `INFO` ("%d hood part(s) restored to parametric") ou `WARNING` (`wood_hoods.py:2220-2226`). 🟢

## Riscos e Lacunas

- 🔴 Nenhum provider de `accessory_registry` / `appliance_spec_registry`; formato de `spec.panels` desconhecido.
- 🔴 `Trash Pull Outs/Generic Trash Pullout.blend` sem referência em código.
- 🔴 Versão do Python do Blender 5.2: `__annotations__['bay_front_%d']` no corpo da classe quebra com PEP 649.
- 🟡 `driver_add` no caminho `modifiers["X"].properties.inputs.S.value` (5.2) não verificado no RAG.
- 🟡 A migração regex de caminhos cobre só o padrão `modifiers["…"]["…"]` ↔ `.properties.inputs.….value`.
- 🟡 `libraries.load` dentro de update de propriedade pode deixar datablocks órfãos (materiais/curvas com usuários).
- 🟢 `wood_hoods` usa os helpers GN de `hb_utils` em vez de `compat.py` (CLAUDE.md exige sincronia/consolidação).
- 🟢 `add_property` não trata `'TEXT'` → "Hood Style" e "Sink Type" nunca existem.
- 🟢 Mínimos divergentes: `layout_min_size` (+1/2") × frentes do face frame (+1").
- 🟢 PENINSULA/SHIPLAP_PENINSULA iguais a BOX; PLANTATION igual a MANTLE.
- 🟢 Coifa com chapa fixa de 3/4" e medidas americanas — conflita com MDF 15/18/25 mm da camada `btm_*`.
- 🟢 Textos de UI em inglês; identificador `sobreposicao_esquerda` indica tradução parcial (`wood_hoods.py:453`).
