# hb_core — Design Técnico

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Complementa [`requirements.md`](requirements.md). Dados completos em [`data-dictionary-legacy.md#hb_core`](../data-dictionary-legacy.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Interface

### Modelo de objetos (`hb_types.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Variable` | `(obj: ID, data_path: str, name: str)` | — | Descritor de variável de driver `SINGLE_PROP` (`:59-68`) 🟢 |
| `GeoNodeObject.__init__` | `(obj: Object \| None = None)` | — | Encapsula um objeto existente 🟢 |
| `GeoNodeObject.create` | `(geo_node_name: str, name: str)` | `None` (preenche `self.obj`) | Malha + modificador `NODES`; carrega o grupo de `geometry_nodes/<nome>.blend` se não existir (`:79-97`) 🟢 |
| `GeoNodeObject.create_curve` | `(geo_node_name: str, name: str)` | `None` | Curva POLY de 2 pontos; cor = `annotation_color` (`:99-122`) 🟢 |
| `GeoNodeObject.add_empty` | `(obj_name: str)` | `Object` | Empty filho (`:124`) 🟢 |
| `GeoNodeObject.add_property` | `(name, type, value, combobox_items=[])` | — | Delega a `obj.home_builder.add_property` (`:131`) 🟢 |
| `GeoNodeObject.set_property` / `get_property` | `(prop_name, value)` / `(prop_name, default=None)` | — / valor | ID custom property (`:146-165`) 🟢 |
| `GeoNodeObject.set_input` | `(name: str, value)` | — | Resolve identificador por nome; `ValueError` em falha; `update_tag()` (`:325-360`) 🟢 |
| `GeoNodeObject.get_input` | `(name: str)` | valor | Idem, leitura (`:362-390`) 🟢 |
| `GeoNodeObject.has_input` / `has_modifier` | `(name)` / `()` | `bool` | Guardas sem exceção (`:392-428`) 🟢 |
| `GeoNodeObject.var_input` / `var_prop` / `var_location` / `var_rotation` / `var_hide` | `(input_name, name)`, `(prop_name, name)`, `(name, axis)`, `(name)` | `Variable` | Caminho RNA correto para a versão (`:167-209`) 🟢 |
| `GeoNodeObject.driver_input` | `(input_name: str, expression: str, variables: list[Variable] = [])` | — | `driver_add` no caminho do input GN (`:243-272`) 🟢 |
| `GeoNodeObject.driver_prop` | `(prop_name, expression, variables=[])` | — | Driver em ID custom prop (`:274-287`) 🟢 |
| `GeoNodeObject.driver_location` / `driver_rotation` | `(axis: 'x'\|'y'\|'z', expression, variables=[])` | — | Eixo inválido → `UnboundLocalError` (`:211-233`) 🟢 |
| `GeoNodeObject.driver_hide` | `(expression, variables=[])` | — | Mesma expressão em `hide_viewport` e `hide_render` (`:235-241`) 🟢 |
| `GeoNodeObject.draw_input` | `(layout, input_name, text, icon='')` | — | UI do input via `gn_input_ui_ref` (`:288`) 🟢 |
| `GeoNodeWall.create` | `(name: str)` | — | Cria parede + `obj_x` (`:444-466`) 🟢 |
| `GeoNodeWall.connect_to_wall` | `(wall: GeoNodeWall)` | — | `COPY_LOCATION` → `wall.obj_x` (`:480-484`) 🟢 |
| `GeoNodeWall.get_connected_wall` | `(direction: 'left'\|'right' = 'left', include_loop_seam=False)` | `GeoNodeWall \| None` | `include_loop_seam` ativa `_geometric_neighbor` para atravessar a emenda de cômodo fechado; percorredores de cadeia devem deixá-lo desligado ou o laço não termina (`:486-561`) 🟢 |
| `GeoNodeCage.create` | `(name)` | — | Gaiola wire invisível no render (`:565-576`) 🟢 |
| `GeoNodeCutpart.add_part_modifier` | `(token_type, token_name)` | `CabinetPartModifier` | (`:594`) 🟢 |
| `GeoNodeDimension.get_unit_type` | `()` | `int` | 0/2/3/4 (`:693-712`) 🟢 |
| `GeoNodeDimension.create` | `(name)` | — | Curva + fixup + marcadores + tamanhos da cena (`:714-730`) 🟢 |
| `GeoNodeDimension.set_decimal` | `(fine=False)` | — | Ajusta `Decimals` (`:732-798`) 🟢 |
| `ensure_dimension_text_offset_basis` | `(node_group)` | `bool` | Fixup idempotente (`:632-687`) 🟢 |
| `CabinetPartModifier.add_node` | `(token_type, token_name)` | — | Carrega `CabinetPartModifiers/<token>.blend` (`:848-870`) 🟢 |
| `CabinetPartModifier.set_input` / `get_input` / `driver_input` / `driver_hide` | como em `GeoNodeObject` | — | Operam sobre `self.mod` (`:872-962`) 🟢 |

### Propriedades e calculadoras (`hb_props.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Calculator_Prompt.get_var` | `(calculator_name: str, name: str)` | `Variable` | Caminho `home_builder.calculators["C"].prompts["P"].distance_value` (`:238-240`) 🟢 |
| `Calculator.set_total_distance` | `(expression="", variables=[], value=0)` | — | Driver em `distance_obj.home_builder.calculator_distance` (`:253-257`) 🟢 |
| `Calculator.add_calculator_prompt` | `(name)` | `Calculator_Prompt` | 🟢 |
| `Calculator.calculate` | `()` | — | Distribuição (`:294-320`) 🟢 |
| `Home_Builder_Object_Props.add_property` | `(name, type, value, combobox_items)` | — | 6 tipos (`:335-374`) 🟢 |
| `Home_Builder_Object_Props.add_calculator` | `(calculator_name, calculator_object)` | `Calculator` | (`:376-380`) 🟢 |
| `Home_Builder_Object_Props.driver_prop` / `add_driver` / `var_prop` | — | — | Drivers em props do PropertyGroup (`:382-407`) 🟢 |

### Utilitários (`hb_utils.py`)

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `get_gn_input` / `set_gn_input` | `(mod, identifier[, value])` | valor / — | **Identificador**, não nome — difere de `compat.set_gn_input(mod, input_name)` (`:16-28`) 🟢 |
| `try_get_gn_input` | `(mod, identifier, default)` | valor | (`:31`) 🟢 |
| `gn_input_ui_ref` | `(mod, identifier)` | `(owner, prop)` | Para `layout.prop` (`:42`) 🟢 |
| `gn_input_data_path` | `(mod, identifier)` | `str` | `modifiers["M"].properties.inputs.ID.value` (≥ 5.2) ou `modifiers["M"]["ID"]` (`:55-60`) 🟢 |
| `get_cabinet_bp` … `get_wall_bp` | `(obj)` | `Object \| None` | Sobe pelos pais até o marcador (`:67-166`) 🟢 |
| `delete_obj_and_children` | `(obj)` | — | Pós-ordem, `do_unlink=True` (`:169-187`) 🟢 |
| `run_calc_fix` | `(context, obj=None, passes=2)` | — | (`:190-246`) 🟢 |
| `run_calc_fix_until_stable` | `(context, obj=None, max_passes=5, tolerance=0.0001)` | `int` | Passadas ou −1 (`:249-297`) 🟢 |
| `add_driver_variables` | `(driver, variables)` | — | `SINGLE_PROP` (`:299-305`) 🟢 |
| `save_view_state` / `restore_view_state` | `(scene)` | — | Custom props `VIEW_*` (`:311-385`) 🟢 |
| `set_camera_view`, `set_top_down_view`, `set_layout_shading`, `frame_all_objects` | `()` (usam `bpy.context`) | — | Vistas de layout (`:388-458`) 🟢 |
| `is_room_scene` | `(scene)` | `bool` | Exclui layout, detalhe e `IS_CROWN_DETAIL` (`:461-469`) 🟢 |

### Projeto e obstáculos

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `hb_project.get_main_scene` | `(context=None)` | `Scene` | Fallback em 3 níveis (`:143-176`) 🟢 |
| `hb_project.get_project_props` | `(context=None)` | `Home_Builder_Project_Props` | Da cena principal (`:179`) 🟢 |
| `hb_project.ensure_main_scene` | `(context=None)` | `Scene` | Chamado em `load_post` (`:195`) 🟢 |
| `hb_project.set_main_scene` | `(scene)` | — | Marcação única (`:225-236`) 🟢 |
| `hb_project.migrate_project_data` | `(old_scene, new_scene)` | — | Cópia sem sobrescrever (`:239-262`) 🟢 |
| `hb_project.is_room_scene` / `get_room_scenes` | `(scene)` / `()` | `bool` / `list[Scene]` | Ordenadas por `sort_order` (`:265-289`) 🟢 |
| `hb_props_obstacles.get_obstacle_items` | `(self, context)` | lista de enum | Cabeçalhos 0/100/200/300 (`:104-126`) 🟢 |
| `hb_props_obstacles.get_obstacle_data` | `(obstacle_id)` | tupla \| `None` | (`:128`) 🟢 |

### Operadores (`ops.py`)

| `bl_idname` | Tipo | `bl_options` | Observação |
|-------------|------|--------------|------------|
| `blendertomob.to_do` | execute | — | Placeholder 🟢 |
| `blendertomob.set_recommended_settings` | invoke_props_dialog + execute | — (**deveria ter UNDO**) | 6 bools (`:29-116`) 🟢 |
| `home_builder_annotations.apply_settings_to_all` | execute | `{'REGISTER', 'UNDO'}` | `Socket_3/4/5` fixos (`:119-192`) 🟢 |
| `blendertomob.rendering_settings` | dialog | `{'REGISTER', 'UNDO'}` | `execute` vazio (`:197-265`) 🟢 |
| `blendertomob.create_camera` | execute | `{'REGISTER', 'UNDO'}` | Track-to e backplate opcionais (`:270-490`) 🟢 |
| `blendertomob.set_scale_with_two_points` | modal | `{'UNDO'}` (sem `REGISTER`) | Draw handler `POST_PIXEL` (`:542-652`) 🟢 |

### Ponteiros registrados em `bpy.types`

| Ponteiro | PropertyGroup |
|---|---|
| `Object.home_builder` | `Home_Builder_Object_Props` |
| `Scene.home_builder` | `Home_Builder_Scene_Props` |
| `WindowManager.home_builder` | `Home_Builder_Window_Manager_Props` |
| `Scene.hb_wall_editor` | `HB_Wall_Editor_Props` |
| `Scene.hb_project` | `Home_Builder_Project_Props` |
| `Scene.hb_obstacles` | `Obstacles_Scene_Props` |

Todos 🟢, criados nos `register()` classmethods e removidos nos `unregister()` correspondentes. Exceção: `IF/OR/AND` em
`bpy.app.driver_namespace` **não** são removidos. 🟢

## Fluxo Principal

### F1. Registro e carga de arquivo 🟢
1. `__init__.register()` chama `hb_props.register()`, `hb_project.register()`, `hb_props_obstacles.register()` e
   `ops.register()` (`__init__.py:212-214`).
2. Cada `register()` percorre `classes`: tenta `unregister_class` (versão antiga), depois `register_class`; qualquer
   exceção é engolida (`hb_props.py:955-966`).
3. Os classmethods `register` dos PropertyGroups criam os `PointerProperty` listados acima.
4. `IF/OR/AND` entram em `bpy.app.driver_namespace` se o nome estiver livre (`__init__.py:249-256`).
5. `load_file_post` (`@persistent`) reinjeta as funções e chama `hb_project.ensure_main_scene()` (`__init__.py:58-73`).

### F2. Criar objeto paramétrico e ligar por drivers 🟢
1. Consumidor instancia a subclasse (ex.: `GeoNodeCage()`) e chama `create(name)`.
2. `create` procura `bpy.data.node_groups[geo_node_name]`; se não existe, carrega de `geometry_nodes/<nome>.blend`
   via `bpy.data.libraries.load(file_path)` (append, `hb_types.py:81-86`).
3. Cria mesh vazia + objeto, adiciona modificador `NODES`, atribui o grupo, grava `mod_name`, liga a `scene.collection`.
4. A subclasse grava marcadores (`IS_*`), aparência e valores padrão via `set_input`.
5. Consumidor define parentesco e cria drivers: `var_input("Dim X", "dim_x")` → `driver_input("Dim X", "dim_x - mt*2", [..])`.
6. `driver_input` chama `obj.driver_add(gn_input_data_path(mod, ident))`, adiciona variáveis e define a expressão.

### F3. `set_input` com cache 🟢 (fluxograma `flowcharts/legacy-hb_core-set_input.md`)
1. Valida `mod_name`, modificador, node group — `ValueError` a cada falha.
2. `_get_input_identifier(node_group, name)`: consulta `_INPUT_IDENT_CACHE[id(node_group)]`; se falta, varre
   `node_group.interface.items_tree` (sockets de entrada) e preenche o cache.
3. Chama `hb_utils.set_gn_input(mod, ident, value)`.
4. Em `KeyError`/`AttributeError`: `_invalidate_input_cache(node_group)`, resolve de novo e tenta uma vez mais;
   segunda falha → `ValueError`.
5. `obj.update_tag()`.

### F4. Calculadora 🟢 (fluxograma `flowcharts/legacy-hb_core-calculator_calculate.md`)
1. Sem `distance_obj` → retorna.
2. `distance_obj.hide_viewport = False` (permanente) e `view_layer.update()` para avaliar o driver do total.
3. Soma os fixos incluídos; conta os iguais incluídos; lista os iguais.
4. Sem iguais → retorna.
5. `valor = (calculator_distance − Σ fixos) / nº iguais`; atribui `valor` aos iguais incluídos e 0 aos excluídos.
6. "Toca" `id_data.location` para disparar drivers dependentes.

Uso real: "Opening Calculator" do frameless (`product_libraries/frameless/types_frameless.py:953-1026`), total
`dim_z − mt·qtd`. 🟢

### F5. Reavaliação forçada 🟢 (fluxograma `flowcharts/legacy-hb_core-run_calc_fix.md`)
Contorno do bug do Blender #133392 (drivers de "netos" não atualizam). ~61 chamadores.
1. Objetos = `obj` + `children_recursive` ou todos da cena.
2. Por passada: reatribui `location`, alterna `show_viewport` dos modificadores `NODES`, roda todas as calculadoras,
   `frame_set(atual+1)` e volta, `view_layer.update()`.
3. Ao final, avalia cada MESH no depsgraph (erros ignorados).
4. `until_stable`: 1 passada por iteração, compara `dimensions` de cada MESH com a iteração anterior (tolerância
   0,0001 m), máximo 5.

### F6. Paredes 🟢 (fluxograma `flowcharts/legacy-hb_core-get_connected_wall.md`)
1. `GeoNodeWall.create`: objeto GN `GeoNodeWall`, marcadores `IS_WALL_BP`, `MENU_ID`, cor `prefs.wall_color`.
2. Cria empty filho `obj_x` (tamanho 0,01, marcador `obj_x=True`), driver `location.x = Length`, trava Y/Z/rotação.
3. `connect_to_wall(prev)`: `COPY_LOCATION` com alvo `prev.obj_x`; `prev.obj_x.home_builder.connected_object = self.obj`.
4. `get_connected_wall('left')`: pai do alvo da restrição; `('right')`: varre paredes cuja restrição aponta para o meu
   `obj_x`; com `include_loop_seam=True` e sem vizinho topológico, `_geometric_neighbor` compara extremos em XY do
   mundo com tolerância 0,01 m (atravessa a emenda de cômodo fechado e cômodos que só compartilham um canto).

### F7. Cota 🟢 (fluxograma `flowcharts/legacy-hb_core-set_decimal.md`)
1. `create_curve("GeoNodeDimension", name)`; fixup `ensure_dimension_text_offset_basis`.
2. Marcadores `IS_2D_ANNOTATION`, `IS_DIMENSION`, `MENU_ID = HOME_BUILDER_MT_dimension_commands`.
3. Copia `Tick Length`, `Tick Thickness`, `Line Thickness`, `Extend Line`, `Text Size` de `scene.home_builder`.
4. `Unit Type = get_unit_type()`.
5. `set_decimal()`: mede o comprimento, converte para a unidade de exibição, testa o encaixe no incremento grosso e
   fino da unidade, remove zeros à direita; inteiro (±0,001) → 0.

### F8. Cena principal 🟢
`get_main_scene`: primeira cena com `IS_MAIN_SCENE` → senão primeiro cômodo (`is_room_scene`) por `sort_order` →
senão `scenes[0]`; tenta marcar a escolhida e engole `AttributeError` em contexto de desenho.

### F9. Escala de imagem por dois pontos (modal) 🟢
1. `execute`: guarda o empty `IMAGE` ativo, adiciona draw handler `POST_PIXEL` (`_draw_scale_line`) e o modal handler.
2. `modal`: `MOUSEMOVE` projeta o mouse no plano XY local do empty (`get_image_plane_point`, raio–plano);
   `LEFTMOUSE` 1 guarda o 1º ponto; `LEFTMOUSE` 2 calcula `fator = known_distance / distância` e multiplica
   `empty_display_size`; navegação é repassada (`PASS_THROUGH`); `RIGHTMOUSE`/`ESC` cancela.
3. `cleanup` remove o draw handler nos caminhos de término e cancelamento.

## Fluxos Alternativos

- **Node group ausente no `.blend`:** `libraries.load` não traz o grupo → o modificador fica sem grupo e o primeiro
  `set_input` levanta `ValueError("… node group …")`. 🟡
- **`CabinetPartModifier` sem arquivo:** `get_node` retorna `None`; modificador criado vazio, sem erro. 🟢
- **Registro com falha:** exceção engolida; o sintoma aparece depois como `AttributeError: 'Object' has no attribute 'home_builder'`. 🟢
- **Arquivo salvo antes do 5.2 aberto no 5.2:** drivers continuam com `modifiers["M"]["ID"]` e ficam inválidos. 🔴
- **`driver_location('w', …)`:** `UnboundLocalError` por variável não atribuída. 🟢
- **Calculadora com fixos > total:** valores negativos propagados às peças. 🟢
- **Objetos criados/removidos durante `until_stable`:** comparação por `zip` pode desalinhar pares. 🟡
- **`--background`:** operadores que usam `context.window`/`context.screen` (câmera, recomendadas, escala) falham. 🟢

## Dependências

- `data/units.py` — conversão e formatação de unidades (via fachada `units.py`). 🟢
- Preferências do add-on (`wall_color`, `annotation_color`) via `get_user_preferences`. 🟢
- `operators/layouts.py` — `recalculate_annotation_sizes_for_scene` (import tardio). 🟢
- `molding/ops.py`, `molding/packages.py` — itens e callback de pacotes de moldura (unit [`catalog_molding`](../catalog_molding/)). 🟢
- `product_libraries/frameless/operators/ops_crown.py` — categorias/itens de moldura. 🟢
- `Scene.hb_frameless` e `Scene.hb_face_frame` — alvo do recálculo de pé-direito. 🟢
- `ui/menus.py` — menus referenciados por `MENU_ID`. 🟢
- `operators/ops_obstacles.py` — operador `home_builder_obstacles.place_obstacle`. 🟢
- `geometry_nodes/*.blend`, `geometry_nodes/CabinetPartModifiers/*.blend` — node groups. 🟢 (interfaces 🔴)
- `compat.py` — ponte "oficial" **não usada** por esta unit (dívida de consolidação). 🟢

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Parametrização por drivers Blender + DSL Python em vez de solver próprio | `hb_types.py:167-287` | 🟢 |
| Node groups embarcados em `.blend` e carregados sob demanda, reutilizados por nome | `hb_types.py:8-9,81-86` | 🟢 |
| Acesso a input GN pelo nome do socket com cache de identificador | `hb_types.py:21-50` | 🟢 |
| Ponte de versão 5.1/5.2 própria em `hb_utils`, paralela a `compat.py` | `hb_utils.py:13-60`, `compat.py:9-88` | 🟢 |
| Prompts de objeto como ID custom properties (não `bpy.props`) | `hb_props.py:335-374` | 🟢 |
| Dados de projeto numa única "cena principal" marcada | `hb_project.py:143-236` | 🟢 |
| Reavaliação forçada por "toques" + troca de frame para contornar bug de drivers | `hb_utils.py:190-297` | 🟢 |
| Padrões de cena em polegadas (mercado dos EUA) | `hb_props.py:468-480` | 🟢 |
| Paredes encadeadas por restrição `COPY_LOCATION` a um empty de extremidade | `hb_types.py:452-484` | 🟢 |

## Estado Interno

- **Cache global** `_INPUT_IDENT_CACHE: dict[int, dict[str, str]]` (`hb_types.py:21`), chave `id(node_group)`; vive
  durante a sessão Python; invalidado por grupo em falha. 🟢 Chave pode ser reciclada. 🟡
- **Por objeto** (`Object.home_builder`): `mod_name`, `connected_object`, `calculators[]`, `calculator_distance`,
  `calculator_index`. Persistido no `.blend`. 🟢
- **Prompts e marcadores**: ID custom properties no objeto (`IS_*`, `MENU_ID`, prompts). Persistidos. 🟢
- **Por cena** (`Scene.home_builder`, `Scene.hb_project`, `Scene.hb_obstacles`, `Scene.hb_wall_editor`) e custom
  props `IS_MAIN_SCENE`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW`, `IS_CROWN_DETAIL`, `VIEW_*`. Persistidos. 🟢
- **Runtime do modal de escala**: `first_point`, `current_mouse_pos`, `empty_image`, `_draw_handle` (não salvos). 🟢
- **Global de processo**: `bpy.app.driver_namespace["IF"|"OR"|"AND"]` (+ dunders do módulo, via `inspect.getmembers`). 🟢

## Observabilidade

- Não há logging estruturado. 🟢
- `print` em `migrate_project_data` para chaves não copiadas (`hb_project.py:259-262`) e nos stubs
  `update_main_tab`/`update_product_tab` (`hb_props.py:19-26`). 🟢
- Erros da API `GeoNodeObject` saem como `ValueError` com nome do objeto/modificador/input. 🟢
- `run_calc_fix_until_stable` retorna o nº de passadas (ou −1), único sinal de convergência. 🟢
- `WindowManager.home_builder.progress` existe para operações longas; uso nesta unit não observado. 🟡

## Riscos e Lacunas

- 🔴 Interfaces dos node groups `.blend` não verificadas; nomes de inputs usados pelo código são a única fonte.
- 🔴 Sem migração de caminhos de driver entre < 5.2 e 5.2.
- 🔴 Operadores `pc_prompts.*` inexistentes (UI da calculadora quebrada).
- 🔴 `GeoNodeWall.assign_materials` morto e com nomes de input divergentes de `update_wall_material`.
- 🟢 `hb_utils.set_gn_input(identifier)` × `compat.set_gn_input(input_name)`: mesmo nome, semântica diferente, dois caches.
- 🟢 `apply_settings_to_all` usa `Socket_3/4/5` fixos e filtra `MESH` → não atualiza cotas (`CURVE`).
- 🟢 `annotation_dimension_extend_line` aponta para o callback do tick — mudar "Extend Line" não propaga.
- 🟢 `driver_namespace` e draw handler do modal não são limpos em `unregister()`.
- 🟢 `register()` engole exceções.
- 🟢 `Material.use_nodes = True` em `ops.py:386` é inócuo desde 5.0.
- 🟡 `id(node_group)` como chave de cache pode colidir após coleta de lixo.
- 🟡 Ramo `COMBOBOX` de `add_property` sem `id_properties_ensure` — comportamento no 5.2 não verificado.
- 🟡 A camada legada ignora `btm_settings.btm_unit` para cotas; `Unit Type = 1` (pés) nunca produzido.
