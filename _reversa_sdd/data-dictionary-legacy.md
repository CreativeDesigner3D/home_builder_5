# Dicionário de Dados — Camada Legada (Home Builder 5)

> Gerado pelo Archaeologist (Reversa) em 2026-09-29. Complementa [`data-dictionary.md`](data-dictionary.md) (camada `btm_*`).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Detalhes de fluxo em [`code-analysis-legacy.md`](code-analysis-legacy.md).

## hb_core

Dicionário de dados da camada legada `hb_core`. Caminhos relativos a `blendertomob/`.
Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

### Variable (classe Python) — `hb_types.py:59-68`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj | `bpy.types.ID` | ID dono da propriedade lida pelo driver (`targets[0].id`) | `None` | 🟢 |
| data_path | str | Caminho RNA relativo ao ID (ex.: `location.z`, `["Material Thickness"]`, caminho de input GN) | `""` | 🟢 |
| name | str | Nome da variável na expressão do driver | `""` | 🟢 |

### GeoNodeObject (classe Python base) — `hb_types.py:71-428`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj | `bpy.types.Object` | Objeto encapsulado (mesh ou curva) com modificador `NODES` | `None`; atribuído no construtor ou em `create` | 🟢 |
| obj.home_builder.mod_name | str (bpy.props) | Nome do modificador GN principal | definido em `create` | 🟢 |
| obj["<prompt>"] | ID custom property | Prompts criados por `add_property` (lidos por `var_prop`/`get_property`) | tipo conforme `add_property` | 🟢 |

### GeoNodeWall — `hb_types.py:431-561`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj_x | `Object` (empty) | Filho que marca a extremidade final da parede; `location.x` dirigido por `Length` | tamanho 0,01; Y/Z e rotação travados; marcador `obj_x=True` | 🟢 |
| obj["IS_WALL_BP"] | bool (ID prop) | Marcador de parede | True | 🟢 |
| obj["MENU_ID"] | str (ID prop) | Menu de contexto | `HOME_BUILDER_MT_wall_commands` | 🟢 |
| obj.color | float[4] | Cor da parede | `prefs.wall_color` (padrão (0,253; 0,500; 0,736; 1)) | 🟢 |
| Input GN `Length` | float (m) | Comprimento da parede | — | 🟢 |
| Inputs GN de material | Material | `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge` | — | 🟢 (nomes usados pelo código); 🔴 interface do `.blend` não verificada |
| obj_x.home_builder.connected_object | Object | Parede ligada a esta extremidade | — | 🟢 |

### GeoNodeCage — `hb_types.py:563-576`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj["IS_GEONODE_CAGE"] | bool (ID prop) | Marcador de gaiola | True | 🟢 |
| display_type | enum | Exibição | `WIRE` | 🟢 |
| color | float[4] | Cor | (0,0,0,1) | 🟢 |
| visible_camera / visible_shadow / hide_render | bool | Invisível no render | False / False / True | 🟢 |
| Inputs GN `Dim X`, `Dim Y`, `Dim Z` | float (m) | Dimensões da gaiola (usadas por subclasses via `var_input`) | — | 🟢 (uso em `types_frameless.py:956-958`) |

### Subclasses simples de GeoNodeObject

| Classe (local) | Node group | Campo / input | Padrão | Confiança |
|---|---|---|---|---|
| GeoNodeRectangle (`hb_types.py:579`) | `GeoNodeRectangle` | `Dim X`, `Dim Y`, `Line Thickness`; cor | 1, 1, 0,001 m; preto | 🟢 |
| GeoNodeCutpart (`:589`) | `GeoNodeCutpart` | — (modificadores extras via `add_part_modifier`) | — | 🟢 |
| GeoNode5PieceDoor (`:601`) | `GeoNode5PieceDoor` | — | — | 🟢 |
| GeoNodeHardware (`:607`) | `GeoNodeHardware` | — | — | 🟢 |
| GeoNodeDrawerBox (`:613`) | `GeoNodeDrawerBox` | `IS_DRAWER_BOX`; `Material Thickness`; `Bottom Thickness`; `Drawer Bottom Z Location` | True; 0,5"; 0,25"; 0,5" | 🟢 |
| GeoNodeDoorSwing (`:623`) | `GeoNodeDoorSwing` | `IS_2D_ANNOTATION`; cor; `Door Thickness` | True; preto; 1,5" | 🟢 |
| GeoNodeArrow (`:801`) | `GeoNodeArrow` (curva POLY de 2 pontos; ponto 0 = ponta) | `IS_2D_ANNOTATION`; `Line Thickness`; `Arrow Height`; `Arrow Length`; `Show Arrow`; `Material` | True; = espessura da cota; 0,25"; 0,5"; True; — | 🟢 |

### GeoNodeDimension — `hb_types.py:690-798`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj.data | Curve (POLY, 2 pontos) | Pontos inicial e final da cota | nome do objeto `Dimension` | 🟢 |
| IS_2D_ANNOTATION / IS_DIMENSION | bool (ID prop) | Marcadores | True | 🟢 |
| MENU_ID | str (ID prop) | Menu de contexto | `HOME_BUILDER_MT_dimension_commands` | 🟢 |
| Input `Tick Length` | float (m) | Comprimento do tick | `scene.home_builder.annotation_dimension_tick_length` | 🟢 |
| Input `Tick Thickness` | float (m) | Espessura do tick | `annotation_dimension_tick_thickness` | 🟢 |
| Input `Line Thickness` | float (m) | Espessura da linha | `annotation_dimension_line_thickness` | 🟢 |
| Input `Extend Line` | float (m) | Linha de extensão | `annotation_dimension_extend_line` | 🟢 |
| Input `Text Size` | float (m) | Tamanho do texto | `annotation_dimension_text_size` | 🟢 |
| Input `Unit Type` | int | 0 = in, 1 = ft, 2 = mm, 3 = cm, 4 = m | por `get_unit_type` (nunca 1) | 🟢 |
| Input `Decimals` | int | Casas decimais exibidas | por `set_decimal` | 🟢 |
| Inputs `Offset Text Amount`, `Offset Text X Amount` | float | Deslocamento do texto (normal / tangente após o fixup) | — | 🟢 (docstring `:632-651`) |

### CabinetPartModifier — `hb_types.py:843-962`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj | Object | Peça dona do modificador | herdado | 🟢 |
| mod | `NodesModifier` | Modificador adicional (`CPM_*`) | `None` até `add_node`; `show_expanded=False` | 🟢 |
| token_type | str | Nome do node group / arquivo em `CabinetPartModifiers/` (`CPM_3SIDEDNOTCH`, `CPM_5PIECEDOOR`, `CPM_CHAMFER`, `CPM_CORNERNOTCH`, `CPM_CUTOUT`, `CPM_RADIUSNOTCH`) | — | 🟢 |
| token_name | str | Nome do modificador | — | 🟢 |

### Calculator_Prompt (PropertyGroup) — `hb_props.py:227-246`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | str (herdado) | Nome do prompt (ex.: `Opening 1 Height`) | — | 🟢 |
| distance_value | FloatProperty, `DISTANCE` | Valor calculado ou fixo | 0; precisão 5 | 🟢 |
| equal | BoolProperty | Participa da divisão igual | True | 🟢 |
| include | BoolProperty | Entra no cálculo | True | 🟢 |

### Calculator (PropertyGroup) — `hb_props.py:249-320`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | str (herdado) | Nome da calculadora (ex.: `Opening Calculator`) | — | 🟢 |
| prompts | CollectionProperty(Calculator_Prompt) | Parcelas | vazia | 🟢 |
| distance_obj | PointerProperty(Object) | Empty cujo `home_builder.calculator_distance` guarda o total (dirigido por driver) | None | 🟢 |

### Home_Builder_Object_Props (`Object.home_builder`) — `hb_props.py:323-419`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| mod_name | StringProperty | Nome do modificador GN principal | `""` | 🟢 |
| connected_object | PointerProperty(Object) | Objeto conectado (parede seguinte) | None | 🟢 |
| calculators | CollectionProperty(Calculator) | Calculadoras do objeto | vazia | 🟢 |
| calculator_distance | FloatProperty, `DISTANCE` | Total da calculadora (quando o objeto é `distance_obj`) | 0 | 🟢 |
| calculator_index | IntProperty | Índice de UI | 0 | 🟢 |

### Prompt de objeto (ID custom property criada por `add_property`) — `hb_props.py:335-374`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | str | Chave da custom property | — | 🟢 |
| type | enum lógico | CHECKBOX, DISTANCE, ANGLE, PERCENTAGE, QUANTITY, COMBOBOX | — | 🟢 |
| value | bool/float/int/str | Valor inicial | — | 🟢 |
| description | str | Marcador `HOME_BUILDER_PROP` | fixo | 🟢 |
| subtype/min/max | UI | DISTANCE / ANGLE / PERCENTAGE (0–100) / QUANTITY (min 0) | — | 🟢 |
| items | lista `(s,s,s)` | Opções do COMBOBOX | `combobox_items` | 🟢; 🟡 comportamento no 5.2 |

### Home_Builder_Scene_Props (`Scene.home_builder`) — `hb_props.py:443-800`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| main_tab | Enum {ROOM, PRODUCTS} | Aba da biblioteca | ROOM; update stub | 🟢 |
| product_tab | Enum {FRAMELESS, FACE FRAME, CLOSET} | Biblioteca de produto | FRAMELESS; update stub | 🟢 |
| room_name | String | Nome do cômodo | `""` | 🟢 |
| room_type | String | Tipo do cômodo | `""` | 🟢 |
| sort_order | Int | Ordem das cenas de cômodo | 0 | 🟢 |
| wall_type | Enum {Exterior, Interior, Half, Fake} | Tipo de parede | Exterior | 🟢 |
| ceiling_height | Float DISTANCE | Pé-direito; recalcula alturas de armários | 96" (2,4384 m) | 🟢 |
| half_wall_height | Float DISTANCE | Altura da meia parede | 42" | 🟢 |
| fake_wall_height | Float DISTANCE | Altura da parede falsa | 34" | 🟢 |
| wall_thickness | Float DISTANCE | Espessura da parede | 4,5" | 🟢 |
| exterior_wall_thickness | Float DISTANCE | Espessura da parede externa | 6" | 🟢 |
| interior_wall_thickness | Float DISTANCE | Espessura da parede interna | 4,5" | 🟢 |
| door_single_width | Float DISTANCE | Porta simples | 36" | 🟢 |
| door_double_width | Float DISTANCE | Porta dupla | 72" | 🟢 |
| door_height | Float DISTANCE | Altura da porta | 84" | 🟢 |
| window_width / window_height | Float DISTANCE | Janela | 34" / 34" | 🟢 |
| window_height_from_floor | Float DISTANCE | Peitoril | 36" | 🟢 |
| wall_material | Pointer(Material) | Material de parede; update aplica em todas as paredes | None | 🟢 |
| show_entry_doors_and_windows, show_obstacles, show_decorations, show_materials, show_room_settings, show_link_objects_from_rooms | Bool | Expansores de UI | False | 🟢 |
| show_entry_door_and_window_cages | Bool | Alterna `TEXTURED`/`WIRE` e `show_in_front` em portas/janelas | True | 🟢 |
| molding_crown_package / molding_base_package / molding_light_rail_package | Enum dinâmico | Pacotes de moldura (de `molding.packages`) | — ; update reaplica | 🟢 |
| molding_base_include_recessed | Bool | Moldura de base atravessa rodapé recuado | False | 🟢 |
| molding_crown_reveal | Float LENGTH | Faixa exposta acima da porta | 0,625"; min 0 | 🟢 |
| molding_crown_stack_offset | Float LENGTH | Offset da cornija empilhada | 3,5"; min 0 | 🟢 |
| molding_crown_furniture_cap | Bool | Tampa de móvel | False | 🟢 |
| molding_cap_offset | Float LENGTH | Ajuste da tampa | 0; soft ±6" | 🟢 |
| molding_crown_profile / molding_spacer_profile / molding_cap_profile / molding_base_profile / molding_light_rail_profile | Enum dinâmico | Perfis do pacote instalado | — | 🟢 |
| molding_base_shoe | Bool | Base shoe no rodapé | False | 🟢 |
| molding_category / molding_selection | Enum dinâmico | Biblioteca de molduras (`ops_crown`) | `NONE` se vazio | 🟢 |
| annotation_line_thickness | Float LENGTH | Espessura de linha de detalhe | 0,05"; 0,0005–0,1 | 🟢 |
| annotation_line_color | FloatVector COLOR[3] | Cor de linha | preto; 0–1 | 🟢 |
| annotation_font | Pointer(VectorFont) | Fonte dos textos | None | 🟢 |
| annotation_text_size | Float LENGTH | Tamanho do texto | 0,05 m; 0,001–2 | 🟢 |
| annotation_text_color | FloatVector COLOR[3] | Cor do texto | preto | 🟢 |
| annotation_dimension_text_size | Float LENGTH | Texto da cota | 2"; 0,001–2 | 🟢 |
| annotation_dimension_tick_length | Float LENGTH | Tick da cota | 1"; 0,001–1 | 🟢 |
| annotation_dimension_line_thickness | Float LENGTH | Linha da cota | 0,05"; 0,0001–0,1 | 🟢 |
| annotation_dimension_tick_thickness | Float LENGTH | Espessura do tick | 0,05"; 0,0001–0,1 | 🟢 |
| annotation_dimension_extend_line | Float LENGTH | Linha de extensão (update aponta para o callback do tick 🟢 — possível bug) | 1"; 0,001–1 | 🟢 |
| annotation_auto_scale | Bool | Escala automática em layout | True | 🟢 |
| annotation_text_paper_height | Float (pol. no papel) | Texto no papel | 0,15; 0,01–1 | 🟢 |
| annotation_line_paper_thickness | Float | Linha no papel | 0,004; 0,001–0,1 | 🟢 |
| annotation_dim_text_paper_height | Float | Texto da cota no papel | 0,15; 0,01–1 | 🟢 |
| annotation_dim_tick_paper_length | Float | Tick no papel | 0,04; 0,01–0,5 | 🟢 |
| annotation_dim_line_paper_thickness | Float | Linha da cota no papel | 0,004; 0,001–0,1 | 🟢 |
| annotation_dim_tick_paper_thickness | Float | Espessura do tick no papel | 0,002; 0,001–0,1 | 🟢 |

### Home_Builder_Window_Manager_Props (`WindowManager.home_builder`) — `hb_props.py:802-822`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| progress | FloatProperty | Progresso de operações longas | 1,0 | 🟢 |
| get_user_preferences() | método | Retorna `preferences.addons[__package__].preferences` | — | 🟢 |

### HB_Wall_Editor_Props (`Scene.hb_wall_editor`) — `hb_props.py:824-943`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| unit_system | Enum {MM, CM, M, IN, FT} | Unidade de entrada/exibição | MM | 🟢 |
| length | Float LENGTH | Comprimento | 1,7 m | 🟢 |
| height | Float LENGTH | Altura | 2,6 m | 🟢 |
| thickness | Float LENGTH | Espessura | 0,15 m | 🟢 |
| offset | Float LENGTH | Afastamento do piso | 0 | 🟢 |
| angle_absolute | Float ANGLE | Ângulo absoluto | 4,71238898 rad (270°) | 🟢 |
| angle_relative | Float ANGLE | Ângulo relativo à parede anterior | 270° | 🟢 |
| orientation | Enum {RIGHT, LEFT} | Lado da espessura | RIGHT | 🟢 |
| step_linear | Float LENGTH | Passo linear | 0,05 m | 🟢 |
| step_angular | Float ANGLE | Passo angular | 0,78539816 rad (45°) | 🟢 |
| wall_type | Enum {NORMAL, DRYWALL} | Tipo construtivo | NORMAL | 🟢 |
| save_as_default | Bool | Salvar como padrão | False | 🟢 |

### Home_Builder_Project_Props (`Scene.hb_project`, na cena principal) — `hb_project.py:30-136`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| project_name | String | Nome do projeto | `New Project` | 🟢 |
| project_number | String | Número/ID | `""` | 🟢 |
| designer_name / designer_phone / designer_email | String | Projetista | `""` | 🟢 |
| client_name / client_address / client_city / client_state / client_zip / client_phone / client_email | String | Cliente (dados pessoais — tratar como sensíveis) | `""` | 🟢 |
| project_notes | String | Observações | `""` | 🟢 |
| project_date | String | Data (texto livre, sem validação) | `""` | 🟢 |

### Marcadores de cena (ID custom properties)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_MAIN_SCENE | bool | Cena que guarda os dados de projeto (única) | — | 🟢 `hb_project.py:158,225-236` |
| IS_LAYOUT_VIEW / IS_DETAIL_VIEW / IS_CROWN_DETAIL | bool | Tipos de cena que não são cômodo | — | 🟢 |
| VIEW_LOCATION_X/Y/Z, VIEW_ROTATION_W/X/Y/Z, VIEW_DISTANCE, VIEW_PERSPECTIVE, VIEW_SHADING_TYPE, VIEW_SHADING_COLOR_TYPE, VIEW_SHADING_XRAY | float/str/bool | Estado salvo da vista 3D | restauração com padrões 0 / quat identidade / 10 / PERSP | 🟢 `hb_utils.py:311-385` |

### Obstacle (tupla de catálogo) — `hb_props_obstacles.py:16-101`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| [0] id | str | Identificador (ex.: `OUTLET_STANDARD`) | único | 🟢 |
| [1] name | str | Nome de UI | — | 🟢 |
| [2] description | str | Descrição | — | 🟢 |
| [3] icon | str | Ícone do Blender | — | 🟢 |
| [4] width | float (m) | Largura | ex.: 2,75" | 🟢 |
| [5] height | float (m) | Altura | — | 🟢 |
| [6] depth | float (m) | Profundidade | — | 🟢 |
| [7] default_height_from_floor | float (m) | Altura do centro em relação ao piso | 0 para piso/teto | 🟢 |
| [8] surface | str | WALL, FLOOR, CEILING, ANY | — | 🟢 |

### Obstacles_Scene_Props (`Scene.hb_obstacles`) — `hb_props_obstacles.py:151-265`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obstacle_type | Enum dinâmico (36 itens + 4 cabeçalhos) | Tipo selecionado; update copia as dimensões | 1º item (`HEADER_WALL`) 🟡 | 🟢 |
| obstacle_width | Float LENGTH | Largura | 2,75"; 0,5"–120" | 🟢 |
| obstacle_height | Float LENGTH | Altura | 4,5"; 0,5"–120" | 🟢 |
| obstacle_depth | Float LENGTH | Profundidade | 2"; 0,25"–24" | 🟢 |
| obstacle_height_from_floor | Float LENGTH | Altura do centro (paredes) | 12"; 0–120" | 🟢 |
| show_obstacle_dimensions | Bool | Mostrar dimensões na UI | True | 🟢 |

### Propriedades de operadores (`ops.py`)

| Operador.Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| set_recommended_settings.turn_off_relationship_lines | Bool | Oculta linhas de relação | True | 🟢 `ops.py:34` |
| .turn_on_object_color_type | Bool | Shading por cor do objeto (obrigatório) | True | 🟢 |
| .use_vertex_snapping | Bool | Snap em vértice | True | 🟢 |
| .turn_off_3d_cursor | Bool | Oculta o cursor 3D | True | 🟢 |
| .show_wireframes | Bool | Wireframe (limiar 0, opacidade 0,8) | True | 🟢 |
| .change_studio_lighting | Bool | Studio light `paint.sl` | True | 🟢 |
| create_camera.add_track_to | Bool | Empty-alvo no centro da cena + TRACK_TO | False | 🟢 `ops.py:276` |
| .add_backplate | Bool | Plano emissivo atrás da cena | False | 🟢 |
| .backplate_color | FloatVector COLOR[4] | Cor do backplate | (1,1,1,1) | 🟢 |
| .backplate_distance | Float LENGTH | Distância câmera–backplate | 50; 1–1000 | 🟢 |
| set_scale_with_two_points.known_distance | Float DISTANCE | Distância real entre os pontos | min 0,0001 | 🟢 `ops.py:548` |
| set_scale_with_two_points.first_point / current_mouse_pos / empty_image / _draw_handle | atributos de runtime | Estado do modal (não salvos) | None | 🟢 |

---

## hb_placement

> Dicionário de dados do módulo legado `hb_placement` (`blendertomob/hb_placement.py`, `hb_snap.py`, `hb_gpu_draw.py`). Não há `PropertyGroup`/`bpy.props` no módulo 🟢: todo o estado é atributo Python de instância do operador (mixin) ou ID property custom nos objetos.
> Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA

### Enum `PlacementState` (`hb_placement.py:34`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IDLE | Enum member (`auto()`) | Sem posicionamento ativo; também estado pós-cancelamento | valor padrão de classe do mixin | 🟢 |
| PLACING | Enum member | Objeto segue o mouse, ainda não confirmado | definido por `init_placement` | 🟢 |
| TYPING | Enum member | Usuário digitando valor numérico | via tecla numérica ou `start_typing` | 🟢 |
| ADJUSTING | Enum member | "Colocado mas ajustando" | nunca atribuído no pacote | 🟢 |

### Enum `TypingTarget` (`hb_placement.py:42`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| NONE | Enum member | Nenhum alvo | padrão | 🟢 |
| LENGTH | Enum member | Comprimento de parede / largura de gabinete | alvo padrão do mixin | 🟢 |
| OFFSET_X | Enum member | Deslocamento a partir da esquerda (rótulo "Offset (←)") | — | 🟢 |
| OFFSET_RIGHT | Enum member | Deslocamento a partir da direita ("Offset (→)") | — | 🟢 |
| OFFSET_Y | Enum member | Deslocamento em profundidade | sem uso no pacote; sem rótulo em `get_typed_display_string` (cai em "Value") | 🟢 |
| WIDTH | Enum member | Largura do objeto | permite mover enquanto digita (consumidor frameless) | 🟢 |
| HEIGHT | Enum member | Altura do objeto | idem | 🟢 |
| DEPTH | Enum member | Profundidade do objeto | — | 🟢 |

### `PlacementDimSpec` (namedtuple, `hb_placement.py:17`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| start | `mathutils.Vector` (mundo) | Início da linha de cota | obrigatório | 🟢 |
| end | `mathutils.Vector` (mundo) | Fim da linha de cota | obrigatório | 🟢 |
| text | str | Rótulo já formatado | vazio → sem pílula | 🟢 |
| color | tuple RGBA \| None | Cor da linha e do texto | `None` → `(1,1,1,0.95)` | 🟢 |

### Estado de instância `PlacementMixin` (`hb_placement.py:101-124`, `:132-156`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| placement_state | PlacementState | Estado modal | classe: IDLE; `init_placement`: PLACING | 🟢 |
| typing_target | TypingTarget | Valor sendo digitado | NONE | 🟢 |
| typed_value | str | Buffer de digitação | `""`; caracteres de `NUMBER_KEYS` | 🟢 |
| region | `bpy.types.Region` \| None | Região 3D sob o mouse | `get_region(context)`; pode ser None | 🟢 |
| mouse_pos | Vector 2D | Mouse em coordenadas da região | `(0,0)` | 🟢 |
| hit_location | Vector \| None | Ponto 3D resolvido pelo snap | None | 🟢 |
| hit_object | `bpy.types.Object` \| None | Objeto atingido pelo raio | None | 🟢 |
| hit_face_index | int \| None | Índice de face do hit (setado por `hb_snap.main`) | pode ser -1 (API) | 🟢 |
| view_point | Vector | Origem do raio da vista (setado por `hb_snap.main`) | — | 🟢 |
| hit_grid | bool | True se o ponto veio da interseção com o plano de grade | False a cada tick | 🟢 |
| placement_objects | list[Object] | Objetos a apagar no cancelamento | `[]` | 🟢 |
| _placement_dim_handle | handle \| None | Handle do draw handler de cotas | None; idempotente | 🟢 |
| _placement_dim_specs | list[PlacementDimSpec] | Cotas a desenhar no próximo redraw | `[]` | 🟢 |
| _facing_arrow_segments | list[(Vector, Vector)] \| None | Segmentos da seta de orientação (definido pelo consumidor, lido via `getattr`) | ausente → não desenha | 🟢 |

### Estado de instância `DimensionOperatorMixin` (`hb_placement.py:1381-1398`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| dim_state | str | 'FIRST' \| 'SECOND' \| 'OFFSET' | 'FIRST' | 🟢 |
| first_point | Vector \| None | 1º ponto confirmado | None | 🟢 |
| second_point | Vector \| None | 2º ponto (com ortho aplicado) | None | 🟢 |
| offset_point | Vector \| None | Ponto de afastamento da linha de cota | None | 🟢 |
| current_point | Vector \| None | Ponto sob o cursor (snap ou plano) | None | 🟢 |
| snap_screen_pos | tuple(x,y) \| None | Posição 2D do indicador | None → indicador não desenhado | 🟢 |
| is_snapped | bool | Indica snap ativo | False | 🟢 |
| ortho_mode | bool | Restrição ortogonal ligada | False | 🟢 |
| ortho_direction | str | 'AUTO' \| 'HORIZONTAL' \| 'VERTICAL' | 'AUTO' (fixa após 1º uso) | 🟢 |
| _dim_draw_handle | handle \| None | Handle do indicador de snap | None | 🟢 |
| SNAP_RADIUS | int (classe) | Raio de snap em px | 20; não usado no pacote | 🟢 |

### Tupla de obstáculo (interna a `find_placement_gap*`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| x_start | float (m, X local da parede) | Início do obstáculo | recortado a ≥0 para ilhas/T | 🟢 |
| x_end | float (m) | Fim do obstáculo | = x_start para snap lines | 🟢 |
| obj | Object \| None | Objeto de origem; `None` para obstáculos virtuais (intrusão de canto, T) | — | 🟢 |

### Retornos estruturados

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| (gap_start, gap_end, snap_x) | tuple[float] \| (None,None,None) | Vão escolhido e X sugerido | None se parede sem modificador | 🟢 |
| (left_holdoff, right_holdoff) | tuple[float] | Recuos por borda | (0,0) se holdoff ≤ 0; soma ≤ vão − 1" | 🟢 |
| (snap_obj, snap_side) | (Object, 'LEFT'\|'RIGHT') \| (None, None) | Alvo de snap gabinete→gabinete | — | 🟢 |
| (location, rotation_euler) | (Vector, Euler) \| None | Transformação encostada no alvo | None se Dim X ilegível | 🟢 |
| spans T | list[(float, float)] | Faixas bloqueadas por paredes em T | `[]` | 🟢 |
| intrusão | float | Invasão da ponta por parede vizinha | ≥ 0 | 🟢 |

### ID properties custom lidas/escritas nos objetos

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_WALL_BP | tag (presença) | Raiz de parede; interrompe `find_cabinet_bp` | — | 🟢 |
| obj_x | tag/valor | Helper de ponta de parede; ignorado como obstáculo | — | 🟢 |
| IS_2D_ANNOTATION | tag | Anotação 2D; ignorada | — | 🟢 |
| IS_SNAP_LINE | tag | Linha de snap; fronteira de largura zero | — | 🟢 |
| SNAP_X_POSITION | float (m) | X da snap line | fallback `location.x` | 🟢 |
| IS_ENTRY_DOOR_BP / IS_WINDOW_BP | tag | Abertura; bloqueia ambos os lados; conta no hold-off | — | 🟢 |
| IS_FRAMELESS_CABINET_CAGE, IS_FACE_FRAME_CABINET_CAGE, IS_APPLIANCE, IS_CLOSET_STARTER_CAGE | tag | `CABINET_MARKERS` | — | 🟢 |
| IS_FRAMELESS_PRODUCT_CAGE | tag | Só em `FREE_CABINET_TAGS` (ilhas) | — | 🟢 |
| HB_CURRENT_DRAW_OBJ | tag | Objeto em desenho, ignorado pelo raycast | — | 🟢 |
| _HB_DUP_TOKEN | int | Token temporário de duplicação | removido ao final | 🟢 |
| home_builder.mod_name | str (PropertyGroup externo, lido por atributo) | Nome do modificador GN do objeto | vazio → sem dimensões | 🟢 |

### Inputs de Geometry Nodes consultados (via `hb_types`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| Dim X / Dim Y / Dim Z | float (m) | Largura / profundidade / altura de gabinetes e aberturas | origem no canto traseiro-esquerdo, profundidade em −Y | 🟢 |
| Length / Thickness / Height | float (m) | Comprimento / espessura / altura de paredes | — | 🟢 |

### Constantes de snap e desenho

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| hb_snap.RADIUS | int | Raio (px) do anel de raycast e do snap a vértice/aresta | 50 | 🟢 |
| hb_snap.STEPS | int | Nº de raios do anel | 6 | 🟢 |
| search_edge_pos.epsilon | float (m) | Parada da busca dicotômica | 1e-4 | 🟢 |
| grade de valores | float (m) | Incremento de `snap_value_to_grid` | IMPERIAL 1" / 1/16"; outros 10 mm / 1 mm | 🟢 |
| tick_pixels | int | Meio comprimento dos ticks das cotas | 6 | 🟢 |
| fonte das cotas | float | Tamanho BLF | 14 × `ui_scale` | 🟢 |
| label_bg / label_border | RGBA | Pílula do rótulo | (0.13,0.13,0.14,0.85) / (1,1,1,0.25) | 🟢 |
| cor da seta | RGBA | Seta de orientação | (1,0.85,0.1,0.95), 2,5 px | 🟢 |

---

## hb_layouts

> Dicionário de dados do módulo legado `hb_layouts` (`blendertomob/hb_layouts.py`, `hb_details.py`,
> `hb_detail_library.py`, `hb_assets.py`). Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

### BTM_AssetLibraryEntry (PropertyGroup) — `blendertomob/hb_assets.py:248`

Armazenada em `AddonPreferences.asset_libraries` (`CollectionProperty`, `blendertomob/__init__.py:163`) com índice ativo
`asset_libraries_index` (`IntProperty`, padrão 0, `:164`). Alias legado `HB_AssetLibraryEntry`.

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | StringProperty | Nome exibido da biblioteca | `"New Library"` | 🟢 |
| `library_path` | StringProperty (subtype `DIR_PATH`) | Pasta raiz da biblioteca (resolvida com `bpy.path.abspath`) | `""`; só registrada se for diretório existente | 🟢 |
| `internal_id` | StringProperty | Id estável que liga a entrada à `UserAssetLibrary` (`HB: <name> [<id>]`) | `""`; preenchido com `uuid4().hex[:12]` | 🟢 |

### Cena de layout (IDProperties em `bpy.types.Scene`) — `blendertomob/hb_layouts.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `IS_LAYOUT_VIEW` | bool (IDProp) | Marca a cena como prancha | True ao criar (`:1163`) | 🟢 |
| `IS_ELEVATION_VIEW` / `IS_PLAN_VIEW` / `IS_3D_VIEW` / `IS_MULTI_VIEW` | bool (IDProp) | Tipo da vista (despacho em `get_layout_view_from_scene`) | um por cena | 🟢 |
| `SOURCE_WALL` | str (IDProp) | Nome do objeto parede da elevação | nome do objeto (`:1473`) | 🟢 |
| `SOURCE_OBJECT` | str (IDProp) | Nome do objeto de origem da multivista | (`:2238`) | 🟢 |
| `CONTENT_COLLECTION` | str (IDProp) | Nome da collection de conteúdo da multivista | (`:2245`) | 🟢 |
| `PAPER_SIZE` | str (IDProp) | Tamanho do papel | `LETTER`; ∈ PAPER_SIZES | 🟢 |
| `PAPER_LANDSCAPE` | bool (IDProp) | Orientação paisagem | True | 🟢 |
| `PAPER_DPI` | int (IDProp) | DPI de render | 150 | 🟢 |
| `HB_LINE_ENGINE` | str (IDProp) | Engine de linha com que a cena foi gerada | `FREESTYLE` \| `LINEART`; ausente ⇒ FREESTYLE | 🟢 |
| `hb_layout_scale` | EnumProperty (registrada em `operators/layouts.py:4665`) | Escala do desenho; lida por `getattr` | fallback `'1/4"=1\''` quando vazia | 🟢 |
| `hb_paper_size` | EnumProperty (`operators/layouts.py:4707`) | Papel (com callback de atualização) | `TABLOID`; LETTER/LEGAL/TABLOID/A4/A3 | 🟢 |
| `hb_paper_landscape` | BoolProperty (`operators/layouts.py:4721`) | Orientação; gravada pelo iso-left | True | 🟢 |
| `hb_lineart_solid_scale` | FloatProperty | Multiplicador da linha visível | 1,0; 0,1–5,0 | 🟢 |
| `hb_lineart_dashed_scale` | FloatProperty | Multiplicador da linha oculta | 1,0; 0,1–5,0 | 🟢 |
| `hb_lineart_dash_scale` | FloatProperty | Escala do padrão de tracejado | 1,0; 0,25–4,0 | 🟢 |
| `hb_lineart_show` | BoolProperty | Mostrar Line Art no viewport | True | 🟢 |

### Collections geradas por cena

| Campo (nome) | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `<cena>_Freestyle_Ignore` | Collection (tag `IS_FREESTYLE_IGNORE`) | Anotações, cotas, title block; `lineart_usage=EXCLUDE` no modo Line Art | criada/reutilizada | 🟢 |
| `<cena>_Freestyle_Dashed` | Collection (tag `IS_FREESTYLE_DASHED`) | Instâncias de peças internas (linha oculta) | — | 🟢 |
| `<cena>_Freestyle_Solid` | Collection (tag `IS_FREESTYLE_SOLID`) | Instâncias de geometria visível | — | 🟢 |
| `<cena>_Iso_Solid` / `<cena>_Iso_Dashed` | Collection | Células iso para passe Freestyle híbrido | criadas por `setup_iso_freestyle` | 🟢 |
| `<cena>_LineArt_Marked` | Collection | Empties do canal Marked | reconstruída a cada chamada | 🟢 |
| `<src> LA-Marked` | Collection | Subconjunto de cópias de emissão (` LAEmit`) por conteúdo | — | 🟢 |
| `<view>_<obj>_Solid` / `_Dashed` | Collection | Conteúdo por gabinete/parede (elevação) | Dashed removida se vazia | 🟢 |
| `<name> Content` / `<view> Content Dashed` | Collection | Conteúdo da planta/3D/multivista; tracejado só com peças internas ocultas | — | 🟢 |

### Objeto GP Line Art (`<cena>_LineArt`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `IS_HB_LINEART` | bool (IDProp) | Tag de localização do GP | True | 🟢 |
| `HB_LINEART_BAKED` | bool (IDProp) | Strokes congelados (modificadores desligados) | ausente ⇒ automático | 🟢 |
| camadas | GreasePencil layers | `Solid`, `Dashed`, `Marked`, `Holdout` (opacidade 0) | keyframe em `frame_current` | 🟢 |
| modificadores | GP modifiers | `Lineart Solid` (nível 0), `Lineart Dashed` (1..128), `Lineart Marked` (0..2), `Resample Dashed` (SAMPLE), `Dash Hidden` (3/2) | radius/length via `update_line_art_sizes` | 🟢 |
| materiais | Material GP | `HB_LineArt_Solid`, `HB_LineArt_Dashed` (preto, só stroke) | compartilhados entre cenas | 🟢 |
| `color` / `show_in_front` / `hide_select` | Object | Preto; desenho à frente; não selecionável | (0,0,0,1) / True / True | 🟢 |

### Câmera jitter (`<cena>_LineArt Camera`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `IS_HB_LINEART_CAMERA` | bool (IDProp) | Tag | True | 🟢 |
| `data` | Camera | Compartilhado com `scene.camera` | — | 🟢 |
| `parent` | Object | `scene.camera` | recriada se diferente | 🟢 |
| `rotation_euler` | Euler | Inclinação local (pitch, yaw, 0) | 0,05° | 🟢 |

### LayoutView (classe Python) — `blendertomob/hb_layouts.py:1110`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `scene` | bpy.types.Scene | Cena da prancha | None | 🟢 |
| `camera` | bpy.types.Object | Primeira câmera da cena (na reidratação) | None | 🟢 |
| `paper_size` | str | Tamanho do papel | `'LETTER'` | 🟢 |
| `landscape` | bool | Paisagem | True | 🟢 |
| `dpi` | int | DPI | 150 | 🟢 |
| `freestyle_ignore` / `freestyle_dashed` / `freestyle_solid` | Collection | Definidas em `_create_freestyle_collections` | só após create_scene | 🟢 |
| `title_block` | TitleBlock | Carimbo criado pelas subclasses | — | 🟢 |

### ElevationView(LayoutView) — `:1425`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `wall_obj` | Object | Parede de origem (via `SOURCE_WALL`) | None | 🟢 |
| `content_collections` | list[Collection] | Collections de conteúdo criadas | [] | 🟢 |
| `collection_instances` | list[Object] | Empties de instância | [] (reidratado por varredura) | 🟢 |

### PlanView / View3D(LayoutView) — `:1804`, `:1986`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `content_collection` | Collection | `<name> Content` | None | 🟢 |
| `collection_instance` | Object | Empty `<name> Instance` (`empty_display_size` 0,01) | None | 🟢 |

### MultiView(LayoutView) — `:2170`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `source_obj` | Object | Objeto/parede de origem | None | 🟢 |
| `content_collection` | Collection | Conteúdo sólido | None | 🟢 |
| `content_collection_dashed` | Collection \| None | Peças internas ocultas (movidas) | None se não houver | 🟢 |
| `view_instances` | list[Object] | Empties por célula | [] | 🟢 |
| `dashed_instances` | list[Object] | Irmãos tracejados (parent = célula) | [] | 🟢 |
| `VIEW_TYPES` | dict[str, (str, tuple\|None)] | Rótulo e rotação por tipo | PLAN, FRONT, BACK, LEFT, RIGHT, ISO | 🟢 |

### TitleBlock — `:967`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `obj` | Object | Retângulo-âncora `<cena>_TitleBlock_Boarder` (tag `IS_TITLE_BLOCK_BOARDER`, oculto) | filho da câmera; local (−0,5, −0,5/aspecto, −0,1) | 🟢 |
| `text_objects` | list[Object] | Textos `<cena>_Project Name`, `_Designer Name`, `_Scale`, `_Page Number` | tamanho 0,015; x = 0,25" | 🟢 |

### Objetos de anotação/detalhe — `blendertomob/hb_details.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `IS_DETAIL_VIEW` | bool (IDProp, Scene) | Cena de detalhe | True | 🟢 |
| `IS_CROWN_DETAIL` | bool (IDProp, Scene) | Cena de detalhe de coroa (criada em outro módulo) | — | 🟡 |
| `IS_DETAIL_LINE` / `IS_DETAIL_POLYLINE` / `IS_DETAIL_CIRCLE` / `IS_DETAIL_TEXT` | bool (IDProp, Object) | Tipo da primitiva | True | 🟢 |
| `IS_2D_ANNOTATION` | bool (IDProp, Object) | Anotação 2D (excluída de bbox/Line Art) | True | 🟢 |
| `bevel_depth` | float (Curve) | Espessura da linha | 0,002 (linha/círculo); `annotation_line_thickness` (polilinha) | 🟢 |
| `GeoNodeCircle._radius` | float | Raio atual | 1,0 | 🟢 |
| `GeoNodeText.size` / `extrude` | float | Tamanho / espessura do texto | 0,05 / 0,001 | 🟢 |

### Entrada do índice da biblioteca de detalhes (`library_index.json`) — `blendertomob/hb_detail_library.py:115`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | Nome informado | obrigatório | 🟢 |
| `description` | str | Descrição | `""` | 🟢 |
| `filename` | str | `<nome_sanitizado>_<AAAAMMDD_HHMMSS>.blend` | chave de exclusão | 🟢 |
| `filepath` | str | Caminho absoluto; reescrito na listagem | — | 🟢 |
| `date_created` | str (ISO 8601) | Data/hora local | `datetime.now().isoformat()` | 🟢 |
| `object_count` | int | Nº de objetos CURVE/FONT/MESH | ≥ 1 | 🟢 |
| `detail_type` | str | `crown` \| `detail` | padrão `detail` na leitura | 🟢 |
| `is_crown_detail` | bool | Redundante com `detail_type` | — | 🟢 |
| raiz `details` | list | Lista de entradas | `{"details": []}` se ausente/corrompido | 🟢 |

### UserAssetLibrary gerenciada (Preferências do Blender) — `blendertomob/hb_assets.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | `Home Builder` (embutida) ou `HB: <nome> [<id>]` | — | 🟢 |
| `path` | str | `blendertomob/assets` ou `library_path` resolvido | diretório existente | 🟢 |
| `import_method` | enum | Método de importação | `'APPEND'` | 🟢 |

### HB_OT_assign_asset_catalog (Operator) — `blendertomob/hb_assets.py:342`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `catalog_path` | EnumProperty (itens dinâmicos) | Caminho de catálogo de `blender_assets.cats.txt` | `'NONE'` quando não há catálogos | 🟢 |

---

## frameless

> Dicionário de dados da camada legada `blendertomob/product_libraries/frameless/`. Valores de comprimento são
> armazenados em **metros**; padrões escritos em polegadas (in) no código — convertidos entre parênteses.
> Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. "Prompt" = ID property no objeto criada por
> `obj.home_builder.add_property` (`hb_props.py:335-374`), lida por driver `["Nome"]`.

### Frameless_Scene_Props (`Scene.hb_frameless`) — `props_hb_frameless.py:1341-2518`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| frameless_selection_mode | Enum | Modo de seleção/visualização (update chama `toggle_mode`) | Cabinets / Bays / Openings / Interiors / Parts; `Cabinets` | 🟢 :1343 |
| frameless_tabs | Enum | Aba do painel | LIBRARY / OPTIONS | 🟢 :1353 |
| show_* (cabinet_sizes, cabinet_library, corner_cabinet_library, appliance_library, part_library, user_library, elevation_templates, general_options, handle_options, front_options, drawer_options, crown_details, toe_kick_details, upper_bottom_details, countertop_options, cabinet_styles) | Bool | Expansão de seções da UI | vários | 🟢 :1358-1382 |
| cabinet_group_category | Enum dinâmico | Categoria da biblioteca do usuário | itens de `ops_library.get_cabinet_group_categories` | 🟢 :1365 |
| calculator_cabinets | Collection[CalculatorCabinet] | Dados do "Adjust Cabinet Sizes" | — | 🟢 :1380 |
| cabinet_styles | Collection[Frameless_Cabinet_Style] | Estilos de gabinete | — | 🟢 :1385 |
| active_cabinet_style_index | Int | Estilo ativo | 0 | 🟢 :1386 |
| fill_cabinets | Bool | Preencher gap automaticamente na inserção | True | 🟢 :1389 |
| base_exterior | Enum | Exterior padrão do inferior (**não usado**) | Doors / Door Drawer / 2,3,4 Drawers / Open; `Door Drawer` | 🟢 :1391 / 🔴 uso |
| include_drawer_boxes | Bool | Cria caixas de gaveta; update cria/remove em toda a cena | True | 🟢 :1400 |
| base_corner_type / upper_corner_type / upper_and_tall_corner_type | Enum | Tipos de canto (**não usados**) | Pie Cut Corner / Pie Cut Corner / Diagonal | 🟢 :1402-1422 / 🔴 uso |
| refrigerator_height | Float LENGTH | Altura do nicho de geladeira | 62in (1574,8 mm) | 🟢 :1425 |
| refrigerator_cabinet_width | Float LENGTH | Largura do gabinete de geladeira | 38in (965,2 mm) | 🟢 :1431 |
| range_width | Float LENGTH | Largura de fogão/coifa/built-in | 36in (914,4 mm) | 🟢 :1437 |
| dishwasher_width | Float LENGTH | Largura de lava-louças | 24in (609,6 mm) | 🟢 :1443 |
| default_top_cabinet_clearance | Float LENGTH | Folga até o teto (update recalcula alturas) | 12in (304,8 mm) | 🟢 :1450 |
| default_wall_cabinet_location | Float LENGTH | Piso → base do aéreo | 54in (1371,6 mm) | 🟢 :1457 |
| default_cabinet_width | Float LENGTH | Largura padrão | 36in (914,4 mm) | 🟢 :1464 |
| base_cabinet_depth / base_cabinet_height | Float LENGTH | Inferior | 23.125in (587,4 mm) / 34.5in (876,3 mm) | 🟢 :1470-1480 |
| base/tall/upper_inside_corner_size | Float LENGTH | Tamanho do canto (X=Y) | 36in / 36in / 24in | 🟢 :1482-1498 |
| tall_cabinet_depth / tall_cabinet_height | Float LENGTH | Alto (altura derivada do teto) | 25.5in (647,7 mm) / 84in (2133,6 mm) | 🟢 :1500-1510 |
| upper_cabinet_depth / upper_cabinet_height | Float LENGTH | Aéreo (altura derivada) | 13in (330,2 mm) / 30in (762 mm) | 🟢 :1512-1522 |
| base/tall/upper_width_blind | Float LENGTH | Canto cego (**sem implementação**) | 48 / 48 / 36in | 🟢 :1524-1540 / 🔴 |
| tall_cabinet_split_height | Float LENGTH | Vão inferior do alto empilhado | 54in (1371,6 mm) | 🟢 :1542 |
| upper_top_stacked_cabinet_height | Float LENGTH | Vão superior do aéreo empilhado | 15in (381 mm) | 🟢 :1548 |
| show_machining | Bool | Mostrar usinagem (callback só `print`) | True | 🟢 :1555 / 🔴 |
| default_carcass_part_thickness | Float LENGTH | Espessura da chapa (mt) | 0.75in (19,05 mm) | 🟢 :1557 |
| default_toe_kick_height / _setback | Float LENGTH | Rodapé | 4in (101,6 mm) / 2.5in (63,5 mm) | 🟢 :1562-1570 |
| default_toe_kick_type | Enum | Tipo de rodapé | Notch Ends to Floor / Ladder Style / Floating / Leg Levelers | 🟢 :1572 |
| default_leg_leveler_inset | Float LENGTH | Recuo dos niveladores | 2in (50,8 mm) | 🟢 :1579 |
| base_top_construction | Enum | Topo do inferior | Stretchers / Full Top; `Stretchers` | 🟢 :1584 |
| equal_drawer_stack_heights | Bool | Gavetas de altura igual | False | 🟢 :1589 |
| top_drawer_front_height | Float LENGTH | Altura da gaveta superior / lap drawer | 6in (152,4 mm) | 🟢 :1593 |
| door_styles / active_door_style_index | Collection[Frameless_Door_Style] / Int | Estilos de porta | — / 0 | 🟢 :1598-1599 |
| selected_template | String | Template de elevação ativo | "" | 🟢 :1601 |
| crown_details / toe_kick_details / upper_bottom_details (+ active_*_index) | Collection / Int | Detalhes de moldura | — / 0 | 🟢 :1608-1617 |
| current_door_pull_object / current_drawer_front_pull_object / current_leg_leveler_object | Pointer[Object] | Cache de objetos de hardware | None | 🟢 :1621-1623 |
| pull_dim_from_edge | Float LENGTH | Borda → centro do puxador | 2in (50,8 mm) | 🟢 :1625 |
| pull_vertical_location_base / _tall / _upper | Float LENGTH | Posição vertical do puxador | 1.5in / 45in / 1.5in | 🟢 :1630-1643 |
| pull_vertical_location_drawers | Float LENGTH | Topo da gaveta → centro do puxador | 1.5in | 🟢 :1645 |
| center_pulls_on_drawer_front | Bool | Centralizar puxador de gaveta | True | 🟢 :1650 |
| pull_category / door_pull_selection / drawer_pull_selection | Enum dinâmico | Biblioteca de puxadores (+ NONE, CUSTOM) | varre `frameless_assets/cabinet_pulls` | 🟢 :1655-1671 |
| pull_finish | Enum dinâmico | Acabamento do puxador | chaves de `PULL_FINISHES` | 🟢 :1673 |
| countertop_thickness | Float LENGTH | Espessura da bancada | 1.5in (38,1 mm) | 🟢 :1680 |
| countertop_overhang_front / _sides / _back | Float LENGTH | Balanços | 1in / 1in / 0 | 🟢 :1685-1698 |

### Frameless_Cabinet_Style — `props_hb_frameless.py:515-866`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | String | Nome (update renomeia materiais) | "Style" | 🟢 :518 |
| show_expanded / show_custom_grain_options / show_advanced_color | Bool | UI | False | 🟢 |
| wood_species | Enum | Madeira externa | MAPLE, OAK, CHERRY, WALNUT, BIRCH, HICKORY, ALDER, PAINT_GRADE, CUSTOM_PROCEDURAL, CUSTOM; `MAPLE` | 🟢 :532 |
| stain_color / paint_color | Enum dinâmico | Cor tingida / tinta (finish_colors + JSON do usuário) | fallback Natural / Arctic White | 🟢 :551-561 |
| interior_material_type | Enum | Interior | MAPLE_PLY ("UV Plywood"), MATCHING, CUSTOM; `MAPLE_PLY` | 🟢 :564 |
| door_overlay_type | Enum | Sobreposição de portas | FULL, HALF, INSET; `FULL` | 🟢 :576 |
| edge_banding | Enum | Fita de borda | MATCHING, CUSTOM | 🟢 :588 |
| material / material_rotated | Pointer[Material] | Acabamento (veio vertical/horizontal) | criado sob demanda | 🟢 :598-599 |
| interior_material / interior_material_rotated | Pointer[Material] | Interior | criado sob demanda | 🟢 :600-601 |
| custom_material / custom_interior_material / custom_edge_material | Pointer[Material] | Materiais do usuário | None | 🟢 :603-605 |
| custom_wood_color_1 / _2 | FloatVector COLOR(3) | Cores do procedural | (0.8,0.65,0.45) / (0.6,0.45,0.3) | 🟢 :608-613 |
| custom_noise_scale_1/2, custom_texture_variation_1/2, custom_noise_detail, custom_voronoi_detail_1/2, custom_knots_scale, custom_knots_darkness, custom_roughness, custom_noise/knots/wood_bump_strength | Float | Parâmetros do shader procedural | 3.5, 2.5, 0.1, 12.5, 15, 0, 0.2, 0, 0, 1.0, 0.1, 0.15, 0.2 (limites 0–50/0–20/0–10/0–1) | 🟢 :614-626 |

### Frameless_Door_Style — `props_hb_frameless.py:890-1208`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | String (herdado de PropertyGroup) | Nome | "Slab"/"Default Door Style" quando auto-criado | 🟢 :1668, :1758 |
| door_type | Enum | Construção | SLAB, 5_PIECE; `SLAB` | 🟢 :900 |
| panel_material | Enum | Almofada | MATCH_CABINET, GLASS | 🟢 :911 |
| outside_profile / inside_profile | Pointer[Object] | Perfis (não usados na geometria) | None | 🟢 :922-931 / 🔴 uso |
| stile_width / rail_width | Float LENGTH | Montante / travessa | 2in (50,8 mm) | 🟢 :934-948 |
| add_mid_rail / center_mid_rail | Bool | Travessa intermediária | False / True | 🟢 :951-961 |
| mid_rail_width / mid_rail_location | Float LENGTH | Largura / altura a partir da base | 2in / 12in | 🟢 :963-977 |
| panel_thickness / panel_inset | Float LENGTH | Almofada | 0.5in / 0.25in | 🟢 :980-994 |
| edge_profile_type | Enum | Perfil de borda de slab (**não aplicado**) | SQUARE, EASED, OGEE, BEVEL, ROUNDOVER | 🟢 :997 / 🔴 uso |

### CalculatorCabinet — `props_hb_frameless.py:1211-1215`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| cabinet_obj | Pointer[Object] | Gabinete | — | 🟢 |
| is_equal | Bool | Largura igual | True | 🟢 |
| cabinet_width | Float DISTANCE | Largura | — | 🟢 |

### Crown_Detail / Toe_Kick_Detail / Upper_Bottom_Detail — `props_hb_frameless.py:1218-1284`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| name | String | Nome do detalhe | "Crown Detail" etc. | 🟢 |
| detail_scene_name | String | Cena 2D com perfis (`IS_MOLDING_PROFILE`/`IS_SOLID_LUMBER`) | — | 🟢 |
| description | String | Descrição | "" | 🟢 |

### HB_Frameless_Base_Template — `props_elevation_templates.py:28-259`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| ceiling_height | Float LENGTH | Pé-direito | 96in (2438,4 mm) | 🟢 :35 |
| wall_width | Float LENGTH | Comprimento da parede | 120in (3048 mm) | 🟢 :43 |
| left_offset / right_offset | Float LENGTH | Recuos nas pontas | 0 | 🟢 :52-66 |
| obj_wall | Pointer[Object] | Parede | — | 🟢 :69 |
| is_active | Bool | Preview ativo | False | 🟢 :75 |

### Refrigerator_Range_Template (herda Base) — `props_elevation_templates.py:266-905`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| refrigerator_location | Enum | NONE/LEFT/RIGHT | NONE | 🟢 :272 |
| range_location | Enum | NONE/CENTER | NONE | 🟢 :283 |
| refrigerator_width | Float LENGTH | Largura geladeira | 36in | 🟢 :293 |
| range_width | Float LENGTH | Largura fogão | 30in | 🟢 :301 |
| range_hood_type | Enum | EMPTY / RAISE_UPPER (RAISE só une uppers) | EMPTY | 🟢 :309 |
| range_hood_height | Float LENGTH | Altura da coifa (só UI) | 20in | 🟢 :319 / 🔴 uso |
| pantry_location / pantry_width | Enum / Float | NONE/LEFT/RIGHT; 18in | NONE | 🟢 :327-344 |
| left/right_base_cabinet_qty, left/right_upper_cabinet_qty | Int | Quantidades | 2 (1–6) | 🟢 :346-376 |
| cage_* / rect_* / rect_top_* (7 cada) | Pointer[Object] | Objetos de preview | — | 🟢 :379-403 |

### Island_Template (herda Base) — `props_elevation_templates.py:915-1377`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| island_depth | Float LENGTH | Profundidade | 24in | 🟢 :921 |
| offset_from_wall | Float LENGTH | Distância da parede | 72in (1828,8 mm) | 🟢 :929 |
| sink_location / sink_width | Enum / Float | NONE/CENTER; 36in | NONE | 🟢 :937-953 |
| dishwasher_location / dishwasher_width | Enum / Float | NONE/LEFT/RIGHT; 24in | NONE | 🟢 :955-972 |
| left_cabinet_qty / right_cabinet_qty | Int | Quantidades | 2 (1–6) | 🟢 :974-988 |
| cage_* / rect_* / rect_top_* (4 cada) | Pointer[Object] | Preview | — | 🟢 :991-1006 |

### FloatingShelfRow — `operators/ops_products.py:423-427`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| obj_name | String | Prateleira | — | 🟢 |
| elevation / thickness | Float LENGTH | Altura mundo / espessura | — | 🟢 |

### Classes Python de gabinete — dimensões iniciais (`types_frameless.py`)

| Classe | Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|---|
| Cabinet | width/height/depth | float (m) | Padrões de classe | 18in / 34in / 24in | 🟢 :12-14 |
| Cabinet | default_exterior | str | Exterior do inferior | "Doors" | 🟢 :10 |
| BaseCabinet | width/height/depth | float | da cena | default_cabinet_width / base_cabinet_height / base_cabinet_depth | 🟢 :544-549 |
| TallCabinet / UpperCabinet | is_stacked | bool | Divide em 2 vãos | False | 🟢 :783, :870 |
| CornerCabinet | corner_size, door_pull_location | float, str | Tamanho e posição de puxador | 36in, "Base" | 🟢 :2302-2304 |
| SplitterVertical/Horizontal | splitter_qty, opening_sizes, opening_inserts | int, list[float], list[CabinetOpening\|None] | Configuração do divisor | 1, [], [] | 🟢 :924-928 |
| CabinetOpening | half_overlay_top/bottom/left/right | bool | Padrões dos prompts | False | 🟢 :1145-1148 |
| Doors / CabinetDoor / Pullout | door_pull_location | str | Base/Tall/Upper | "Base" | 🟢 :1269, :1732 |
| Appliance | appliance_name | str | Texto exibido | "Appliance" | 🟢 :1549 |

### Prompts do gabinete (cage raiz) — `types_frameless.py:16-50, 2306-2308, 2348-2390`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| Material Thickness | DISTANCE | Espessura das peças (mt) | default_carcass_part_thickness | 🟢 :18 |
| Toe Kick Height / Toe Kick Setback | DISTANCE | Rodapé (base/alto) | 4in / 2.5in | 🟢 :33-34 |
| Remove Bottom | CHECKBOX | Sem base/rodapé | False (geladeira: True) | 🟢 :35, :840 |
| Toe Kick Type | COMBOBOX | 0..3 | da cena | 🟢 :37 |
| Leg Leveler Inset | DISTANCE | Recuo dos niveladores | 2in | 🟢 :39 |
| Base Top Construction | COMBOBOX | Full Top / Stretchers / Sink | da cena | 🟢 :48 |
| Stretcher Width / Sink Apron Width | DISTANCE | Travessa / avental | 4in / 7in | 🟢 :49-50 |
| Left Depth / Right Depth | DISTANCE | Asas do canto | = depth do tipo | 🟢 :2307-2308 |
| Front Thickness, Door to Cabinet Gap, Inset Front, Inset Reveal, Half Overlay Top/Bottom/Outer, Top/Bottom/Outer Reveal, Vertical Gap, Door Swing | vários | Overlay das portas de canto (na raiz) | 0.75in, 0.125in, False, 0.125in, False, 0.0625/0/0.0625in, 0.125in, Left | 🟢 :2348-2390 |
| Finished Interior | CHECKBOX (criado sob demanda) | Interior com acabamento | False | 🟢 `ops_cabinet.py:67-71` |
| CABINET_TYPE, CORNER_TYPE, CABINET_STYLE_INDEX/NAME, DOOR_STYLE_INDEX, CROWN_DETAIL_NAME/SCENE, TOE_KICK_DETAIL_NAME/SCENE | ID prop (str/int) | Metadados | — | 🟢 |

### Prompts de abertura (CabinetOpening e derivadas) — `types_frameless.py:1156-1176, 1274-1276`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| Front Thickness | DISTANCE | Espessura da frente | 0.75in (19,05 mm) | 🟢 |
| Inset Front | CHECKBOX | Frente embutida | False | 🟢 |
| Door to Cabinet Gap | DISTANCE | Folga frente–caixa | 0.125in (3,18 mm) | 🟢 |
| Half Overlay Top/Bottom/Left/Right | CHECKBOX | Meia sobreposição por lado | atributos da classe | 🟢 |
| Inset Reveal | DISTANCE | Folga em inset | 0.125in | 🟢 |
| Top/Bottom/Left/Right Reveal | DISTANCE | Revelação | 0.0625 / 0 / 0.0625 / 0.0625in | 🟢 |
| Vertical Gap / Horizontal Gap | DISTANCE | Folga entre frentes | 0.125in | 🟢 |
| Left/Right/Top/Bottom Thickness | DISTANCE | Espessura adjacente | default_carcass_part_thickness | 🟢 |
| Door Swing (Doors) | COMBOBOX | Left/Right/Double | 2 (Double) | 🟢 :1276 |
| Overlay Top/Bottom/Left/Right (empty "Overlay Prompt Obj") | DISTANCE com driver | Overlays calculados | fórmula R14 | 🟢 :1196-1208 |
| FORCE_HALF_OVERLAY_TOP/BOTTOM/LEFT/RIGHT | ID prop bool | Trava meia sobreposição | — | 🟢 :1015-1113 |
| APPLIANCE_NAME (Appliance) | ID prop str | Nome exibido | "Appliance" | 🟢 :1557 |

### Prompts de frente (CabinetFront e derivadas) — `types_frameless.py:1648-1652, 1747-1756, 1833-1840, 1898-1902`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| Top/Bottom/Left/Right Overlay | DISTANCE | Cópia dos overlays (gaveta/pullout) | 0 (driver) | 🟢 |
| Pull Location | COMBOBOX | Base/Tall/Upper | por tipo | 🟢 |
| Handle Horizontal Location | DISTANCE | Porta: borda→puxador; gaveta: topo→puxador | 2in / 1.5in | 🟢 |
| Base/Tall/Upper Pull Vertical Location | DISTANCE | Posição vertical | 1.5 / 45 / 1.5in | 🟢 |
| Pull Length | DISTANCE | Comprimento do puxador | dimensão X do objeto ou 0.1016 m | 🟢 |
| Pull Vertical Location (flip-up) | DISTANCE | Posição | 1.5in | 🟢 :1799 |
| False Front | CHECKBOX | Sem caixa/puxador | False | 🟢 |
| Center Pull | CHECKBOX | Puxador centralizado | center_pulls_on_drawer_front | 🟢 |
| Drawer Box Side/Top/Rear/Bottom Clearance | DISTANCE | Folgas da caixa | 0.5 / 0.75 / 1.0 / 0.5in | 🟢 |
| Finish Top / Finish Bottom | ID prop bool | Faces com acabamento | frentes True/True; peças False/True | 🟢 |
| DOOR_STYLE_INDEX / DOOR_STYLE_NAME | ID prop | Estilo aplicado | — | 🟢 |

### Prompts de interior — `types_frameless.py:947-948, 1228-1231, 2069-2070`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| Shelf Quantity | QUANTITY | Nº de prateleiras (driver no ARRAY) | 1 → recalculado por R17 (0–10 no diálogo) | 🟢 |
| Shelf Clip Gap | DISTANCE | Folga lateral | 0.125in | 🟢 |
| Shelf Setback | DISTANCE | Recuo frontal | 0.25in | 🟢 |
| Divider Quantity | QUANTITY | Nº de divisórias (splitter) | splitter_qty | 🟢 |
| Material Thickness | DISTANCE | Espessura de divisórias | default_carcass_part_thickness | 🟢 |

### Prompts de produtos — `types_products.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| FloatingShelf: Finish Left/Right, Include LED Route Bottom/Top, LED Width Top/Bottom, LED Inset Top/Bottom, LED Route Depth | CHECKBOX/DISTANCE | Laterais e rasgo de LED | True, True, False, False, 0.5in, 0.5in, 2in, 2in, 0.25in; dims 36×12×2.5in | 🟢 :49-58 |
| Valance: Top Scribe Amount, Finish Left/Right, Remove Cover, Flush Bottom | DISTANCE/CHECKBOX | Sanca frontal | 0.5in, False…; altura 4in | 🟢 :172-177 |
| SupportFrame: Support Spacing, Front/Back Left/Right Leg, Leg Width/Depth/Height, * Leg Type | DISTANCE/CHECKBOX/COMBOBOX | Estrutura de apoio | 16in, True, 3.5in, 3.5in, 34.5in, Inset/Wrapped; dims 60×24×4in | 🟢 :266-278 |
| HalfWall: Stud Thickness, Skin Thickness, Stud Spacing, End Stud From Edge, Left/Right End Cap, Finished End Setback, Left/Right Finished Revel, Finish Front/Back | DISTANCE/CHECKBOX | Meia-parede (vários sem uso) | 0.75in, 0.25in, 16in, 1.5in…; dims 36×6×42in | 🟢 :461-472 |
| Leg/TallLeg: Toe Kick Height/Setback, Override Left/Right Panel Depth, Only Include Filler, Finish Type | DISTANCE/CHECKBOX/COMBOBOX | Perna/filler | cena, 0 (=total), False, Left; largura 2in | 🟢 :647-655 |
| UpperLeg: Override Left/Right Panel Depth, Only Include Filler, Finish Type | idem | Perna de aéreo | — | 🟢 :827-831 |
| PART_TYPE | ID prop str | FLOATING_SHELF, VALANCE, SUPPORT_FRAME, HALF_WALL, LEG, UPPER_LEG, PANEL | — | 🟢 |

### hb_frameless_OT_place_cabinet (propriedades do operador) — `operators/ops_placement.py:276-330`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| cabinet_name | String | Nome do item da biblioteca | "" | 🟢 |
| cabinet_type | Enum | BASE / TALL / UPPER | BASE | 🟢 |
| is_appliance / appliance_type | Bool / String | Eletro (RANGE, DISHWASHER, REFRIGERATOR, HOOD, COOKTOP, WALL_OVEN, MICROWAVE, SINK) | False / "" | 🟢 |
| fill_mode, cabinet_quantity, auto_quantity, individual_cabinet_width, max_single_cabinet_width, left/right_offset, gap_left/right_boundary, place_on_front, corner_right_side, snap_cabinet/side, center_snap_state | atributos Python | Estado do modal | max 36in | 🟢 :297-330 |

### Estruturas auxiliares

| Estrutura | Campos | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `PULL_FINISHES` dict | name, color (RGBA), metallic, roughness | 12 acabamentos (Chrome … Polished Gold) | ex.: Chrome (0.8,0.8,0.8,1), 1.0, 0.1 | 🟢 `props_hb_frameless.py:170-243` |
| Cor (finish_colors) | color_1, color_2 (RGBA), roughness?, noise/knots/wood_bump_strength? | Stain (15) e Paint (12) + custom JSON | SHADER_DEFAULTS 1.0/0.1/0.15/0.2 | 🟢 `finish_colors.py:35-172` |
| custom_colors.json | {stain:{nome:cor}, paint:{nome:cor}} | Cores do usuário | em `extension_path_user(...,'user_data')` | 🟢 `finish_colors.py:21-27` |
| `PART_CLASS_MAP` | nome → classe | 9 produtos | — | 🟢 `ops_placement.py:13-23` |
| `TEMPLATE_REGISTRY` | nome → atributo de Scene | Refrigerator Range, Island | — | 🟢 `props_elevation_templates.py:1383` |

---

## face_frame

> Dicionário de dados do módulo legado `blendertomob/product_libraries/face_frame/`.
> Unidade interna: **metros** (valores `float (m)` com `unit='LENGTH'`); padrões definidos em polegadas via `units.inch()`
> — a coluna Padrão mostra polegadas e o equivalente em mm. A coluna "Descrição" reproduz o `name` e, quando curto, o
> `description` declarados no código (texto de UI em inglês, herança do HB5). Todas as props são acessadas por atributo
> (`obj.face_frame_cabinet.width`); nunca por `obj["..."]` (ver risco em `types_face_frame.py:7335`).
> Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

### Relacionamentos (visão geral) 🟢
- `Object.face_frame_cabinet` → `Face_Frame_Cabinet_Props` (1 por cage raiz de gabinete) → `mid_stile_widths` (N−1 por N bays) e `corner_sections`.
- `Object.face_frame_bay` → `Face_Frame_Bay_Props` (1 por bay cage, filho da raiz).
- `Object.face_frame_split` → `Face_Frame_Split_Props` (nó interno da árvore do bay) → `splitter_widths` (≤ filhos−1).
- `Object.face_frame_opening` → `Face_Frame_Opening_Props` (folha) → `interior_items` → `rollout_boxes`; `drawer_look_openings`.
- `Object.face_frame_interior_split` / `face_frame_interior_region` → árvore interior dentro de uma opening.
- `Scene.hb_face_frame` → `Face_Frame_Scene_Props` → `cabinet_styles` (Face_Frame_Cabinet_Style), `door_styles` / `drawer_front_styles` (Face_Frame_Door_Style).
- Vínculo gabinete→estilo é **por nome** (custom prop `STYLE_NAME` na raiz), não por ponteiro (`props_hb_face_frame.py:1690`).
- `Object.leg_product`, `Object.floating_shelf`, `Object.valance_product` → props de produtos sem bays.

### Custom properties de ID (não-RNA) usadas como metadados 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `IS_FACE_FRAME_CABINET_CAGE` | bool (ID prop) | Marca a raiz do gabinete | — | 🟢 |
| `IS_FACE_FRAME_BAY_CAGE` | bool | Marca bay cage | — | 🟢 |
| `IS_FACE_FRAME_OPENING_CAGE` | bool | Marca folha (opening) da árvore | — | 🟢 |
| `IS_FACE_FRAME_SPLIT_NODE` | bool | Marca nó interno (split) | — | 🟢 |
| `IS_FACE_FRAME_PRODUCT_CAGE` | bool | Produto não-gabinete selecionável como gabinete (Half Wall) | — | 🟢 |
| `IS_INTERIOR_SPLIT_NODE` / `IS_INTERIOR_REGION` | bool | Nós da árvore interior | — | 🟢 |
| `CLASS_NAME` | str | Nome da subclasse Python; chave de `WRAP_CLASS_REGISTRY` | ex. 'BaseFaceFrameCabinet' | 🟢 |
| `CABINET_TYPE` | str | Tipo no momento da criação (espelho de `cabinet_type`) | BASE/UPPER/TALL/PANEL | 🟢 |
| `MENU_ID` | str | Menu de contexto do objeto | ex. 'HOME_BUILDER_MT_face_frame_part_commands' | 🟢 |
| `STYLE_NAME` | str | Nome do Face_Frame_Cabinet_Style aplicado | — | 🟢 |
| `hb_part_role` | str | Papel da peça (PART_ROLE_*) — chave do despacho no recálculo | ~90 valores | 🟢 |
| `hb_bay_index` | int | Índice do bay (ordenação) | ≥0 | 🟢 |
| `hb_mid_stile_index` | int | Índice do gap (mid stile / mid division) | 0..N−2 | 🟢 |
| `hb_segment_start_bay` | int | Identidade de rails/fundos/costas/travessas por segmento | — | 🟢 |
| `hb_split_child_index` | int | Ordem do filho dentro do split (H: topo→base; V: esq.→dir.) | — | 🟢 |
| `hb_splitter_index` | int | Índice do membro (mid rail/stile) no split | — | 🟢 |
| `SIZE_ROLE` | str | Papel de tamanho fixo (TOP_DRAWER, TALL_SPLIT_BOTTOM, UPPER_STACKED_TOP, REFRIGERATOR, VANITY_DOOR, VANITY_SINK_WIDTH, BOOKCASE_STORAGE_BOTTOM) | — | 🟢 |
| `IS_MANUAL_PART` / `IS_MANUAL_FRONT` | bool | Peça/abertura congelada (fora do recálculo) | — | 🟢 |
| `HB_TRIVIEW_DOORS` | bool | Liga as 3 portas espelho do tri-view | — | 🟢 |
| `hb_applied_to_cabinet_side` | str | Lado do gabinete hospedeiro de um painel aplicado (`TAG_APPLIED_PANEL_SIDE`) | LEFT/RIGHT/BACK | 🟢 |

### FaceFrameLayout (snapshot em tempo de execução, `solver_face_frame.py:33`) 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `cabinet_type`, `corner_type` | str | Copiados das props | — | 🟢 |
| `dim_x`, `dim_y`, `dim_z` | float (m) | width, depth, height | — | 🟢 |
| `mt`, `bt`, `fft` | float (m) | Espessura carcaça, costas, moldura | — | 🟢 |
| `has_toe_kick` | bool | cabinet_type ∈ {BASE, TALL, LAP_DRAWER} | — | 🟢 |
| `uses_stretchers` | bool | cabinet_type ∈ {BASE, LAP_DRAWER} e não angular | — | 🟢 |
| `tkh`, `tks`, `tkt`, `toe_kick_type` | float/str | Altura, recuo, espessura, tipo do rodapé (0/'FLOATING' sem kick) | — | 🟢 |
| `lsw`, `rsw` | float (m) | Largura dos stiles de ponta | — | 🟢 |
| `blind_offset_left/right` | float (m) | blind_amount se stile BLIND + blind ligado + amount>0 | — | 🟢 |
| `l_scribe`, `r_scribe`, `top_scribe`, `l/r/b_fin_end` | float/str | Scribe e acabamentos | — | 🟢 |
| `bays` | list[dict] | Por bay: width, height, depth, kick_height, top_offset, front_drop*, top/bottom_rail_width, remove_bottom, remove_carcass, floating_bay, finish_bay*, tree | — | 🟢 |
| `mid_stiles` | list[dict] | width, extend_up/down_amount, to_floor, division_location, division_offset (padrão 2") | — | 🟢 |
| `is_angled` | bool | corner NONE, 1 bay, unlock_left/right_depth | — | 🟢 |
| `wedge_*`, `refrigerator_*`, `extend_*_end_down*`, `extend_sides_down*` | vários | Entradas de variantes | — | 🟢 |

### Nó da árvore (snapshot) — `_read_tree_node` (`solver_face_frame.py:272-335`) 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `kind` | str | 'split' ou 'leaf' | — | 🟢 |
| `obj_name` | str | Nome do objeto (identidade para reconciliação) | — | 🟢 |
| `axis` | str | H ou V (split) | — | 🟢 |
| `size`, `unlock_size`, `size_role` | float/bool/str | Tamanho no eixo do pai e trava | — | 🟢 |
| `splitter_width`, `splitter_widths`, `splitter_removes` | float/list | Largura padrão e por membro; remoção por membro | — | 🟢 |
| `add_backing` | bool | Gera prateleira/divisão atrás do membro | — | 🟢 |
| `children` | list | Filhos ordenados por hb_split_child_index | — | 🟢 |
| `opening_index`, `front_type`, `overlay_top`, `overlay_bottom` | int/str/float | Dados da folha | — | 🟢 |

### Leaf rect (saída de `bay_openings`) 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `obj_name`, `opening_index` | str/int | Identidade da abertura | — | 🟢 |
| `cage_x`, `cage_z` | float (m) | Origem do cage no espaço do bay | — | 🟢 |
| `cage_dim_x/y/z` | float (m) | Dimensões do cage (y = profundidade do bay − fft − bt) | — | 🟢 |
| `reveal_top/bottom/left/right` | float (m) | Distância cage→borda do vão da moldura | ≥0 | 🟢 |

### Splitter rect / Backing rect 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `role` | str | BAY_MID_RAIL / BAY_MID_STILE / BAY_SHELF / BAY_DIVISION | — | 🟢 |
| `as_bottom_rail` | bool | Mid rail promovido a BOTTOM_RAIL | — | 🟢 |
| `split_node_name`, `splitter_index` | str/int | Identidade | — | 🟢 |
| `x`, `y`, `z`, `length`, `splitter_width`/`width`, `thickness` | float (m) | Geometria em coordenadas do bay | shelf 3/4"; division = mt | 🟢 |

### Segmento (rails, fundos, costas, travessas, kicks) 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `start_bay`, `end_bay` | int | Faixa inclusiva de bays | — | 🟢 |
| `x`, `y`, `z` | float (m) | Posição mundial-local do gabinete | — | 🟢 |
| `length`, `width`, `thickness` | float (m) | Dimensões da peça | — | 🟢 |
| `panel_dim_y`, `vertical_length`, `horizontal_length` | float (m) | Variantes para fundo/tampo/costas | — | 🟢 |

### Front leaf descriptor (`front_leaves`) 🟢

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `role`, `name` | str | DOOR/DRAWER_FRONT/PULLOUT_FRONT/FALSE_FRONT/TILT_OUT/INSET_PANEL | — | 🟢 |
| `pivot_position`, `pivot_rotation` | vec3 | Transform do pivô no espaço da abertura | — | 🟢 |
| `pivot_anchor_position` | vec3 | Canto do pivô com swing 0 (gavetas) | — | 🟢 |
| `part_position` | vec3 | Offset da peça no pivô | — | 🟢 |
| `part_dims` | (L, W, T) | Altura, largura, espessura da frente | — | 🟢 |
| `hinge` | str | Dobradiça (para posicionar puxador) | — | 🟢 |
| `frame_override` | dict | left/right_stile, top/bottom_rail (tri-view) | 1.25" | 🟢 |

### PropertyGroups (gerado a partir das anotações em `props_hb_face_frame.py`; campos `show_*` de UI omitidos em Scene/Style/Cabinet)

### Face_Frame_Cabinet_Props (`props_hb_face_frame.py:4493`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `width` | float (m) | Width — Cabinet width (X dimension) | padrão 36.0" (914.4 mm); update=_update_cabinet_dim | 🟢 |
| `height` | float (m) | Height — Cabinet height (Z dimension) | padrão 34.5" (876.3 mm); update=_update_cabinet_dim | 🟢 |
| `depth` | float (m) | Depth — Cabinet depth (Y dimension) | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `lock_width` | bool | Lock Width — Hold this cabinet's width when a containing group is resized | padrão False | 🟢 |
| `cabinet_type` | enum | Cabinet Type | padrão 'BASE'; itens: BASE/TALL/UPPER/LAP_DRAWER/PANEL | 🟢 |
| `is_sink` | bool | Is Sink Cabinet | padrão False | 🟢 |
| `is_built_in_appliance` | bool | Is Built-in Appliance | padrão False | 🟢 |
| `is_double` | bool | Is Stacked / Double | padrão False | 🟢 |
| `left_finished_end_condition` | enum | Left Finished End | padrão 'UNFINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X; update=_on_left_finish_end_user_set | 🟢 |
| `right_finished_end_condition` | enum | Right Finished End | padrão 'UNFINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X; update=_on_right_finish_end_user_set | 🟢 |
| `back_finished_end_condition` | enum | Back Finished End | padrão 'UNFINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X; update=_on_back_finish_end_user_set | 🟢 |
| `left_scribe` | float (m) | Left Scribe | padrão 0.0; update=_on_left_scribe_user_set | 🟢 |
| `right_scribe` | float (m) | Right Scribe | padrão 0.0; update=_on_right_scribe_user_set | 🟢 |
| `left_exposure` | enum | Left Exposure | padrão 'EXPOSED'; itens: UNEXPOSED/PARTIAL/EXPOSED | 🟢 |
| `right_exposure` | enum | Right Exposure | padrão 'EXPOSED'; itens: UNEXPOSED/PARTIAL/EXPOSED | 🟢 |
| `back_exposure` | enum | Back Exposure | padrão 'EXPOSED'; itens: UNEXPOSED/PARTIAL/EXPOSED | 🟢 |
| `left_dishwasher_adjacent` | bool | Left Dishwasher Adjacent | padrão False | 🟢 |
| `right_dishwasher_adjacent` | bool | Right Dishwasher Adjacent | padrão False | 🟢 |
| `left_finish_end_auto` | bool | Left Finish End Auto | padrão True | 🟢 |
| `right_finish_end_auto` | bool | Right Finish End Auto | padrão True | 🟢 |
| `back_finish_end_auto` | bool | Back Finish End Auto | padrão True | 🟢 |
| `back_finished_extend_left` | float (m) | Back Extend Left | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `back_finished_extend_right` | float (m) | Back Extend Right | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `left_side_finished_extend_back` | float (m) | Left Side Extend Back | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `right_side_finished_extend_back` | float (m) | Right Side Extend Back | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `left_side_return_width` | float (m) | Left Side Return Width | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `right_side_return_width` | float (m) | Right Side Return Width | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `left_side_return_panel_type` | enum | Left Side Return Type | padrão 'FINISHED'; itens: FINISHED/PANELED; update=_update_cabinet_dim | 🟢 |
| `right_side_return_panel_type` | enum | Right Side Return Type | padrão 'FINISHED'; itens: FINISHED/PANELED; update=_update_cabinet_dim | 🟢 |
| `left_side_return_stile_type` | enum | Left Side Return Stile Type | padrão 'FINISHED'; itens: FINISHED/PANELED; update=_update_cabinet_dim | 🟢 |
| `right_side_return_stile_type` | enum | Right Side Return Stile Type | padrão 'FINISHED'; itens: FINISHED/PANELED; update=_update_cabinet_dim | 🟢 |
| `left_flush_x_amount` | float (m) | Left Flush X Amount | padrão 4" (101.6 mm); update=_update_cabinet_dim | 🟢 |
| `right_flush_x_amount` | float (m) | Right Flush X Amount | padrão 4" (101.6 mm); update=_update_cabinet_dim | 🟢 |
| `panel_frame_auto` | bool | Auto Panel Frame Widths | padrão True | 🟢 |
| `panel_split_auto` | bool | Auto Openings | padrão True; update=_update_panel_split_auto | 🟢 |
| `panel_top_rail_width` | float (m) | Panel Top Rail Width | padrão 1.5" (38.1 mm) | 🟢 |
| `panel_bottom_rail_width` | float (m) | Panel Bottom Rail Width | padrão 1.5" (38.1 mm) | 🟢 |
| `panel_stile_width` | float (m) | Panel Stile Width | padrão 1.5" (38.1 mm) | 🟢 |
| `top_scribe` | float (m) | Top Scribe | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `blind_left` | bool | Blind Left | padrão False; update=_update_blind_left | 🟢 |
| `blind_right` | bool | Blind Right | padrão False; update=_update_blind_right | 🟢 |
| `blind_amount_left` | float (m) | Blind Amount Left | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `blind_amount_right` | float (m) | Blind Amount Right | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `blind_reveal` | float (m) | Blind Reveal | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `left_stile_width` | float (m) | Left Stile Width | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `right_stile_width` | float (m) | Right Stile Width | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_left_stile` | bool | Unlock Left Stile | padrão False; update=update_cabinet_frame_lock | 🟢 |
| `unlock_right_stile` | bool | Unlock Right Stile | padrão False; update=update_cabinet_frame_lock | 🟢 |
| `turn_off_left_stile` | bool | Turn Off Left Stile | padrão False | 🟢 |
| `turn_off_right_stile` | bool | Turn Off Right Stile | padrão False | 🟢 |
| `left_stile_type` | enum | Left Stile Type | padrão 'STANDARD'; itens: STANDARD/WALL/BLIND/BUTT/INSIDE_90/ANGLE; update=_update_left_stile_type | 🟢 |
| `right_stile_type` | enum | Right Stile Type | padrão 'STANDARD'; itens: STANDARD/WALL/BLIND/BUTT/INSIDE_90/ANGLE; update=_update_right_stile_type | 🟢 |
| `extend_left_stile_to_floor` | bool | Extend Left Stile To Floor | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_right_stile_to_floor` | bool | Extend Right Stile To Floor | padrão False; update=_update_cabinet_dim | 🟢 |
| `refrigerator_opening_height` | float (m) | Refrigerator Opening Height | padrão 62.0" (1574.8 mm); update=_update_refrigerator_opening_height | 🟢 |
| `raise_left_to_refrigerator_height` | bool | Raise Left To Refrigerator Height | padrão False; update=_update_cabinet_dim | 🟢 |
| `raise_right_to_refrigerator_height` | bool | Raise Right To Refrigerator Height | padrão False; update=_update_cabinet_dim | 🟢 |
| `refrigerator_stile_left` | bool | Refrigerator Stile In Lieu Of Leg (Left) — Add a floor-to-opening face-frame stile on the left in lieu of a leg; also raises the left end stile to the opening top | padrão False; update=_update_cabinet_dim | 🟢 |
| `refrigerator_stile_right` | bool | Refrigerator Stile In Lieu Of Leg (Right) — Add a floor-to-opening face-frame stile on the right in lieu of a leg; also raises the right end stile to the opening top | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_left_stile_up` | bool | Extend Left Stile Up | padrão False | 🟢 |
| `extend_left_stile_down` | bool | Extend Left Stile Down | padrão False | 🟢 |
| `extend_right_stile_up` | bool | Extend Right Stile Up | padrão False | 🟢 |
| `extend_right_stile_down` | bool | Extend Right Stile Down | padrão False | 🟢 |
| `extend_left_stile_up_amount` | float (m) | Extend Left Stile Up Amount | padrão 0.0 | 🟢 |
| `extend_left_stile_down_amount` | float (m) | Extend Left Stile Down Amount | padrão 0.0 | 🟢 |
| `extend_right_stile_up_amount` | float (m) | Extend Right Stile Up Amount | padrão 0.0 | 🟢 |
| `extend_right_stile_down_amount` | float (m) | Extend Right Stile Down Amount | padrão 0.0 | 🟢 |
| `extend_left` | float (m) | Extend Left | padrão 0.0 | 🟢 |
| `extend_right` | float (m) | Extend Right | padrão 0.0 | 🟢 |
| `left_offset` | float (m) | Left Offset | padrão 0.0 | 🟢 |
| `right_offset` | float (m) | Right Offset | padrão 0.0 | 🟢 |
| `top_rail_width` | float (m) | Top Rail Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `stretcher_width` | float (m) | Stretcher Width — Front-to-back depth of the top stretchers (typical 3.5 in) | padrão 3.5" (88.9 mm); update=_update_cabinet_dim | 🟢 |
| `stretcher_thickness` | float (m) | Stretcher Thickness — Vertical thickness of the top stretchers (typical 1/2 in) | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `bottom_rail_width` | float (m) | Bottom Rail Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_top_rail` | bool | Unlock Top Rail (Cabinet) | padrão False; update=update_cabinet_frame_lock | 🟢 |
| `unlock_bottom_rail` | bool | Unlock Bottom Rail (Cabinet) | padrão False; update=update_cabinet_frame_lock | 🟢 |
| `bay_mid_rail_width` | float (m) | Bay Mid Rail Width — Vertical extent of mid rails created by horizontal splits inside a bay | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `bay_mid_stile_width` | float (m) | Bay Mid Stile Width — Horizontal extent of mid stiles created by vertical splits inside a bay | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `default_top_overlay` | float (m) | Default Top Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `default_bottom_overlay` | float (m) | Default Bottom Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `default_left_overlay` | float (m) | Default Left Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `default_right_overlay` | float (m) | Default Right Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `default_door_inset_amount` | float (m) | Default Door Inset Amount — Distance the door is recessed from the face frame face (0 = overlay, full = flush inset) | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `material_thickness` | float (m) | Material Thickness | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `face_frame_thickness` | float (m) | Face Frame Thickness | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `door_thickness` | float (m) | Door Thickness — Thickness of doors and drawer fronts attached to openings | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `back_thickness` | float (m) | Back Thickness | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `division_thickness` | float (m) | Division Thickness | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `finish_toe_kick_thickness` | float (m) | Finish Toe Kick Thickness | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `toe_kick_type` | enum | Toe Kick Type | padrão 'NOTCH'; itens: NOTCH/FLUSH/FLOATING/LOOSE/LOOSE_FLUSH; update=_update_cabinet_dim | 🟢 |
| `toe_kick_height` | float (m) | Toe Kick Height | padrão 4.0" (101.6 mm); update=_update_cabinet_dim | 🟢 |
| `toe_kick_setback` | float (m) | Toe Kick Setback | padrão 3.0" (76.2 mm); update=_update_cabinet_dim | 🟢 |
| `toe_kick_thickness` | float (m) | Toe Kick Thickness | padrão 0.75" (19.0 mm) | 🟢 |
| `back_bottom_inset` | float (m) | Back Bottom Inset | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `wedge_enabled` | bool | Tip-Up Wedge — Chamfer the back-bottom corner so a tall cabinet clears the ceiling when tipped upright into place | padrão False; update=_update_cabinet_dim | 🟢 |
| `wedge_ceiling_height` | float (m) | Wedge Ceiling Height | padrão 96.0" (2438.4 mm); update=_update_cabinet_dim | 🟢 |
| `wedge_fudge` | float (m) | Wedge Fudge Allowance | padrão 0.5" (12.7 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `wedge_max_height` | float (m) | Wedge Max Height | padrão 3.0" (76.2 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_back_left` | float (m) | Extend Back Left X | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top` | bool | Furniture Top — Add an overhanging veneer wood top sitting proud on the carcass (dresser / furniture products) | padrão False; update=_update_cabinet_dim | 🟢 |
| `furniture_top_thickness` | float (m) | Wood Top Thickness — Thickness of the furniture wood top | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_overhang` | float (m) | Wood Top Overhang — Overhang of the wood top past the carcass on the left, right, and front (the back stays flush) | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_overhang_front` | float (m) | Wood Top Front Overhang — Overhang of the wood top past the front of the carcass | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_overhang_back` | float (m) | Wood Top Back Overhang — Overhang of the wood top past the back of the carcass | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_overhang_left` | float (m) | Wood Top Left Overhang — Overhang of the wood top past the left side of the carcass | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_overhang_right` | float (m) | Wood Top Right Overhang — Overhang of the wood top past the right side of the carcass | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_shape` | enum | Wood Top Shape — Plan shape of the furniture wood top | padrão 'RECTANGLE'; itens: RECTANGLE/BOW_BACK/RADIUS/WATERFALL; update=_update_cabinet_dim | 🟢 |
| `furniture_top_bow_altitude` | float (m) | Wood Top Bow Altitude — Bow Back shape: distance from the straight back edge to the apex of the arc | padrão 2.0" (50.8 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_radius_front_left` | float (m) | Wood Top Front Left Radius — Radius Edges shape: corner radius at the front-left corner of the top (0 = square) | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_radius_front_right` | float (m) | Wood Top Front Right Radius — Radius Edges shape: corner radius at the front-right corner of the top (0 = square) | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_radius_back_left` | float (m) | Wood Top Back Left Radius — Radius Edges shape: corner radius at the back-left corner of the top (0 = square) | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `furniture_top_radius_back_right` | float (m) | Wood Top Back Right Radius — Radius Edges shape: corner radius at the back-right corner of the top (0 = square) | padrão 1.0" (25.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_left_end_down` | bool | Extend Left End Down | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_left_end_down_amount` | float (m) | Left End Drop | padrão 19.5" (495.3 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_right_end_down` | bool | Extend Right End Down | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_right_end_down_amount` | float (m) | Right End Drop | padrão 19.5" (495.3 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_sides_down` | bool | Extend Sides Down | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_sides_down_amount` | float (m) | Sides Drop — How far both side panels drop below the box bottom | padrão 7.0" (177.8 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `side_front_profile` | bool | Side Front Profile — Cut the over-stool decorative profile into the bottom-front corner of each extended side panel | padrão False; update=_update_cabinet_dim | 🟢 |
| `bottom_rail_profile` | enum | Bottom Rail Profile | itens: dinâmico (_bottom_rail_profile_items); update=_update_cabinet_dim | 🟢 |
| `overstool_accessory` | enum | Leg Accessory — What hangs between the extended sides (over-stool legs) | padrão 'SHELF'; itens: SHELF/TOWEL_BAR/SHELF_AND_TOWEL_BAR; update=_update_cabinet_dim | 🟢 |
| `hutch_finished_back` | bool | Finished Back in Recess — When an upper's ends are extended down, add a finished back panel closing the open recess between the dropped sides | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_back_right` | float (m) | Extend Back Right X | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `wing_attached_left` | bool | Attach Left as Wing | padrão False; update=_update_cabinet_dim | 🟢 |
| `wing_attached_right` | bool | Attach Right as Wing | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_bottom_left` | float (m) | Extend Bottom Left X — Overhang the carcass bottom past the LEFT side by this amount to cover a corner void. 0 = flush with the side. | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_bottom_right` | float (m) | Extend Bottom Right X — Overhang the carcass bottom past the RIGHT side by this amount to cover a corner void. 0 = flush with the side. | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `inset_toe_kick_left` | float (m) | Inset Toe Kick Left | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `inset_toe_kick_right` | float (m) | Inset Toe Kick Right | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `inset_toe_kick_back_left` | float (m) | Inset Toe Kick Back Left | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `inset_toe_kick_back_right` | float (m) | Inset Toe Kick Back Right | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `include_finish_toe_kick` | bool | Include Finish Toe Kick | padrão True; update=_update_cabinet_dim | 🟢 |
| `include_external_nailer` | bool | Include External Nailer | padrão False | 🟢 |
| `include_internal_nailer` | bool | Include Internal Nailer | padrão False | 🟢 |
| `include_thin_finished_bottom` | bool | Include 1/4 Finished Bottom | padrão False | 🟢 |
| `include_thick_finished_bottom` | bool | Include 3/4 Finished Bottom | padrão False | 🟢 |
| `include_blocking` | bool | Include Blocking | padrão False | 🟢 |
| `corner_type` | enum | Corner Type | padrão 'NONE'; itens: NONE/PIE_CUT/DIAGONAL/PIE_CUT_DRAWER | 🟢 |
| `left_depth` | float (m) | Left Depth | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `right_depth` | float (m) | Right Depth | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_left_depth` | bool | Unlock Left Depth | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_right_depth` | bool | Unlock Right Depth | padrão False; update=_update_cabinet_dim | 🟢 |
| `exterior_option` | enum | Exterior Option | padrão 'LEFT_DOOR_OPENS_FIRST'; itens: LEFT_DOOR_OPENS_FIRST/RIGHT_DOOR_OPENS_FIRST/BIFOLD_LEFT_SWING/BIFOLD_RIGHT_SWING/REVOLVING_DOORS; update=_update_cabinet_dim | 🟢 |
| `interior_option` | enum | Interior Option | padrão 'NONE'; itens: NONE/POLYMER_KIDNEY_SUSANS_POLE/WOOD_KIDNEY_SUSANS_POLE/POLYMER_PIE_CUT_REVOLVING/WOOD_PIE_CUT_REVOLVING/SUPER_SUSANS/NOT_SO_LAZY_SUSANS; update=_update_cabinet_dim | 🟢 |
| `corner_finish_interior` | bool | Finish Interior — Use the exterior finish material on the interior surfaces and shelves of this corner cabinet | padrão False; update=_update_cabinet_dim | 🟢 |
| `corner_remove_bottom` | bool | Remove Bottom — Remove the carcass bottom and the bottom rail; the lowest opening runs to the carcass floor | padrão False; update=_update_cabinet_dim | 🟢 |
| `tray_compartment` | enum | Tray Compartment | padrão 'NONE'; itens: NONE/LEFT/RIGHT; update=_update_cabinet_dim | 🟢 |
| `tray_compartment_width` | float (m) | Tray Compartment Width — Clear width of the tray storage strip walled off by the partition | padrão 6.0" (152.4 mm); update=_update_cabinet_dim | 🟢 |
| `tray_compartment_qty` | int | Tray Divider Qty — Number of dividers inside the tray compartment (slots = qty + 1) | padrão 3; min 0; max 10; update=_update_cabinet_dim | 🟢 |
| `tray_compartment_divider_thickness` | float (m) | Tray Divider Thickness | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `tray_compartment_setback` | float (m) | Tray Divider Setback — Front setback of the tray compartment dividers from the face frame | padrão 1.0" (25.4 mm); update=_update_cabinet_dim | 🟢 |
| `exterior_config` | enum | Exterior Config — Stacked-section layout of a diagonal corner cabinet front | itens: dinâmico (_exterior_config_items); update=_update_exterior_config | 🟢 |
| `diag_door_swing` | enum | Door Swing — Door leaf layout for the diagonal face's door sections | padrão 'LEFT_SWING'; itens: DOUBLE_DOOR/LEFT_SWING/RIGHT_SWING; update=_update_cabinet_dim | 🟢 |
| `clip_back_amount` | float (m) | Clip Back — Length of the 45 degree clip taken off each wall side at the rear corner (0 = no clip) | padrão 6.0" (152.4 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `mid_stile_widths` | Collection[Face_Frame_Mid_Stile_Width] |  |  | 🟢 |
| `corner_sections` | Collection[Face_Frame_Corner_Section] |  |  | 🟢 |
| `pie_drawer_qty` | int | Drawer Qty — Number of stacked drawers in a pie-cut drawer corner; the top opening defaults to the Top Drawer Opening Height for 3 or 4 drawers | padrão 3; min 2; max 4; update=_update_pie_drawer_qty | 🟢 |

### Face_Frame_Mid_Stile_Width (`props_hb_face_frame.py:4101`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `width` | float (m) | Width | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `unlock` | bool | Unlock — Hold this mid stile width independent of cabinet defaults | padrão False; update=_update_cabinet_dim | 🟢 |
| `extend_up_amount` | float (m) | Extend Up Amount | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `extend_down_amount` | float (m) | Extend Down Amount | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `to_floor` | bool | Stile to Floor — Extend this mid stile past the toe kick down to the floor (pins its bottom to Z=0, like an end stile) | padrão False; update=_update_cabinet_dim | 🟢 |
| `division_location` | enum | Division Location | padrão 'CENTERED'; itens: CENTERED/FLUSH_LEFT/FLUSH_RIGHT/OFFSET; update=_update_cabinet_dim | 🟢 |
| `division_offset` | float (m) | Division Offset — Signed shift of the carcass division off the stile centerline (negative = toward the left bay) | padrão 0.0; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Corner_Section (`props_hb_face_frame.py:4177`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `content` | enum | Content | padrão 'DOORS'; itens: DOORS/FALSE_FRONT/OPEN | 🟢 |
| `height` | float (m) | Section Height — Opening height of this section (used when Unlock Height is on) | padrão 12.0" (304.8 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_height` | bool | Unlock Height — Hold this section's height; the other sections share the leftover space equally | padrão False; update=_update_cabinet_dim | 🟢 |
| `shelf_qty` | int | Shelf Qty — Number of adjustable shelves in this section | padrão 2; min 0; max 10; update=_update_cabinet_dim | 🟢 |
| `unlock_shelf_qty` | bool | Unlock Shelf Qty — Override the auto shelf count for this door section | padrão False; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Bay_Props (`props_hb_face_frame.py:5510`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `bay_index` | int | Bay Index — Position in the parent cabinet's bay list (0-based) | padrão 0 | 🟢 |
| `width` | float (m) | Width | padrão 18.0" (457.2 mm); update=_update_bay_width | 🟢 |
| `height` | float (m) | Height | padrão 34.5" (876.3 mm); update=_update_cabinet_dim | 🟢 |
| `depth` | float (m) | Depth | padrão 24.0" (609.6 mm); update=_update_cabinet_dim | 🟢 |
| `kick_height` | float (m) | Kick Height | padrão 4.0" (101.6 mm); update=_update_bay_kick_height | 🟢 |
| `top_offset` | float (m) | Top Offset — Distance from cabinet top to top of this bay's opening | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `front_drop` | float (m) | Front Drop | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `front_drop_include_fillers` | bool | Include Drop Fillers — Build filler stiles in the dropped band so the clear width fits the farm sink / cooktop | padrão False; update=_update_cabinet_dim | 🟢 |
| `front_drop_set_appliance_width` | bool | Set Appliance Width — Enter the appliance width and split the remainder into equal left/right fillers; off lets you type each filler width directly | padrão True; update=_update_cabinet_dim | 🟢 |
| `front_drop_appliance_width` | float (m) | Appliance Width — Width of the farm sink / cooktop the dropped band must fit; fillers fill the remainder | padrão 30.0" (762.0 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `front_drop_left_filler` | float (m) | Left Drop Filler — Width of the left drop filler stile (used directly when Set Appliance Width is off) | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `front_drop_right_filler` | float (m) | Right Drop Filler — Width of the right drop filler stile (used directly when Set Appliance Width is off) | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `top_rail_width` | float (m) | Top Rail Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `bottom_rail_width` | float (m) | Bottom Rail Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `remove_bottom` | bool | Remove Bottom | padrão False; update=_update_remove_bottom | 🟢 |
| `remove_carcass` | bool | Remove Carcass | padrão False; update=_update_cabinet_dim | 🟢 |
| `floating_bay` | bool | Floating | padrão False; update=_update_cabinet_dim | 🟢 |
| `apron_bay` | bool | Apron Bay | padrão False | 🟢 |
| `finish_bay` | bool | Finish Bay | padrão False; update=_update_cabinet_dim | 🟢 |
| `finish_bay_flush` | bool | Finish Flush | padrão False; update=_update_cabinet_dim | 🟢 |
| `finish_bay_flush_depth` | float (m) | Flush Depth — How far the flush finish runs back into the opening; 0 runs the full cavity depth | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `prompts_expanded` | bool | Show More Bay Properties — Expand secondary properties for this bay in the cabinet prompts popup | padrão False | 🟢 |
| `unlock_width` | bool | Unlock Width — Hold this bay's width during gang-construction redistribution | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_height` | bool | Unlock Height | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_depth` | bool | Unlock Depth | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_kick_height` | bool | Unlock Kick Height | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_top_offset` | bool | Unlock Top Offset | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_top_rail` | bool | Unlock Top Rail | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_bottom_rail` | bool | Unlock Bottom Rail | padrão False; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Opening_Props (`props_hb_face_frame.py:5947`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `opening_index` | int | Opening Index — Position in the parent bay's opening list (0-based) | padrão 0 | 🟢 |
| `show_front` | bool | Show Front Type | padrão True | 🟢 |
| `show_finish` | bool | Show Finish Options | padrão False | 🟢 |
| `show_overlays` | bool | Show Overlays | padrão False | 🟢 |
| `show_interior_items` | bool | Show Interior Items | padrão True | 🟢 |
| `size` | float (m) | Size | padrão 12.0" (304.8 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_size` | bool | Unlock Size — Hold this opening's size during gang-construction redistribution | padrão False; update=_update_cabinet_dim | 🟢 |
| `front_type` | enum | Front Type | padrão 'NONE'; itens: NONE/DOOR/DRAWER_FRONT/PULLOUT/FALSE_FRONT/TILT_OUT/INSET_PANEL/APPLIANCE; update=_update_front_type | 🟢 |
| `set_appliance_width` | bool | Set Appliance Width — Enter the appliance width and split the remainder into equal left/right fillers; off lets you type each filler width directly | padrão True; update=_update_cabinet_dim | 🟢 |
| `appliance_width` | float (m) | Appliance Width — Width of the appliance the opening must fit; fillers fill the remainder | padrão 24.0" (609.6 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `include_fillers` | bool | Include Fillers — Build the left/right filler stiles; off reserves the opening as an appliance with no fillers | padrão False; update=_update_cabinet_dim | 🟢 |
| `left_filler_amount` | float (m) | Left Filler — Width of the left filler stile (used directly when Set Appliance Width is off) | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `right_filler_amount` | float (m) | Right Filler — Width of the right filler stile (used directly when Set Appliance Width is off) | padrão 0.0; min 0.0; update=_update_cabinet_dim | 🟢 |
| `pullout_accessory_code` | str | Pullout Model — Accessory product code selected for this pullout opening | padrão '' | 🟢 |
| `is_tilt_out` | bool | Tilt-Out — Label this false front as a tilt-out on 2D drawings | padrão False | 🟢 |
| `drawer_look_divisions` | enum | Drawer-Look Divisions — Show this door as a stack of N applied drawer fronts (still opens as one door) | padrão 'NONE'; itens: NONE/2/3/4; update=_update_drawer_look_divisions | 🟢 |
| `drawer_look_openings` | Collection[Face_Frame_Drawer_Look_Opening] |  |  | 🟢 |
| `hinge_side` | enum | Hinge Side | padrão 'RIGHT'; itens: LEFT/RIGHT/DOUBLE/TOP/BOTTOM; update=_update_cabinet_dim | 🟢 |
| `swing_percent` | float | Swing Percent — How far the door / drawer front is opened (0 = closed, 1 = fully open) | padrão 0.0; min 0.0; max 1.0; update=_update_cabinet_dim | 🟢 |
| `top_overlay` | float (m) | Top Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `bottom_overlay` | float (m) | Bottom Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `left_overlay` | float (m) | Left Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `right_overlay` | float (m) | Right Overlay | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_top_overlay` | bool | Unlock Top Overlay — Use this opening's own top overlay value instead of the cabinet default | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_bottom_overlay` | bool | Unlock Bottom Overlay — Use this opening's own bottom overlay value instead of the cabinet default | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_left_overlay` | bool | Unlock Left Overlay — Use this opening's own left overlay value instead of the cabinet default | padrão False; update=_update_cabinet_dim | 🟢 |
| `unlock_right_overlay` | bool | Unlock Right Overlay — Use this opening's own right overlay value instead of the cabinet default | padrão False; update=_update_cabinet_dim | 🟢 |
| `finish_opening` | bool | Finish Opening | padrão False; update=_update_cabinet_dim | 🟢 |
| `finish_opening_flush` | bool | Finish Flush | padrão False; update=_update_cabinet_dim | 🟢 |
| `finish_opening_flush_depth` | float (m) | Flush Depth — How far the flush finish runs back into the opening; 0 runs the full cavity depth | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `add_apron` | bool | Add Apron | padrão False; update=_update_cabinet_dim | 🟢 |
| `apron_height` | float (m) | Apron Height | padrão 7.0" (177.8 mm); min 0.0; update=_update_cabinet_dim | 🟢 |
| `interior_items` | Collection[Face_Frame_Interior_Item] |  |  | 🟢 |
| `interior_items_index` | int | Active Interior Item Index | padrão 0; min 0 | 🟢 |

### Face_Frame_Drawer_Look_Opening (`props_hb_face_frame.py:5931`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `size` | float (m) | Opening Height | padrão 6.0" (152.4 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_size` | bool | Unlock Opening Height — Hold this opening height; locked rows share the remainder equally | padrão False; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Split_Props (`props_hb_face_frame.py:6228`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `axis` | enum | Axis | padrão 'H'; itens: H/V; update=_update_cabinet_dim | 🟢 |
| `size` | float (m) | Size | padrão 12.0" (304.8 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_size` | bool | Unlock Size — Hold this split's size during gang-construction redistribution | padrão False; update=_update_cabinet_dim | 🟢 |
| `splitter_width` | float (m) | Splitter Width — Width of mid rails (H-split) or mid stiles (V-split) inside this split node | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `unlock_splitter_width` | bool | Unlock Splitter Width — Hold this split's mid rail / mid stile width when a cabinet style is applied | padrão False; update=_update_cabinet_dim | 🟢 |
| `splitter_widths` | Collection[Face_Frame_Splitter_Width] |  |  | 🟢 |
| `add_backing` | bool | Add Backing — Add a carcass shelf (H-split) or division (V-split) behind each splitter | padrão True; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Splitter_Width (`props_hb_face_frame.py:6186`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `width` | float (m) | Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `active` | bool | Active — Use this per-splitter width instead of the split's default | padrão False | 🟢 |
| `remove_member` | bool | Remove Member | padrão False; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Interior_Item (`props_hb_face_frame.py:5713`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `kind` | enum | Kind | padrão 'ADJUSTABLE_SHELF'; itens: ADJUSTABLE_SHELF/GLASS_SHELF/PULLOUT_SHELF/ROLLOUT/TRAY_DIVIDERS/VANITY_SHELVES/ACCESSORY; update=_update_cabinet_dim | 🟢 |
| `shelf_qty` | int | Shelf Qty | padrão 1; min 0; max 20; update=_update_cabinet_dim | 🟢 |
| `unlock_shelf_qty` | bool | Unlock Shelf Qty — When on, hold the shelf count at the value above instead of auto-computing it from the opening's height | padrão False; update=_update_cabinet_dim | 🟢 |
| `shelf_setback` | float (m) | Shelf Setback — Distance the shelf is pulled back from the front of the cavity | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `qty` | int | Qty | padrão 2; min 0; max 10; update=_update_cabinet_dim | 🟢 |
| `unlock_qty` | bool | Unlock Qty — When on, hold the count at the value above instead of auto-computing it from the opening's height | padrão False; update=_update_cabinet_dim | 🟢 |
| `spacer_height` | float (m) | Spacer Width — Width of the side spacer parts the slides mount to (front and back, both sides) | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `item_setback` | float (m) | Item Setback — Front setback for each item in the stack | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `bottom_gap` | float (m) | Bottom Gap — Gap below the bottom-most item in the stack | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `distance_between` | float (m) | Distance Between — Vertical gap between consecutive items in the stack | padrão 6.0" (152.4 mm); update=_update_cabinet_dim | 🟢 |
| `pullout_thickness` | float (m) | Pullout Thickness — Thickness of each pullout shelf (PULLOUT_SHELF only) | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `rollout_height` | float (m) | Rollout Height — Height of each rollout drawer box (ROLLOUT only) | padrão 3.625" (92.1 mm); update=_update_cabinet_dim | 🟢 |
| `rollout_boxes` | Collection[Face_Frame_Rollout_Box] |  |  | 🟢 |
| `rollout_boxes_index` | int |  | padrão 0 | 🟢 |
| `tray_qty` | int | Tray Qty | padrão 3; min 1; max 10; update=_update_cabinet_dim | 🟢 |
| `tray_remove_shelf` | bool | Remove Locked Shelf — When on, dividers run the full opening height. Off = dividers stop at a horizontal locked shelf at Tray Opening Height | padrão False; update=_update_cabinet_dim | 🟢 |
| `tray_opening_height` | float (m) | Tray Opening Height — Z position of the locked shelf above the tray dividers (only when Remove Locked Shelf is off) | padrão 20.0" (508.0 mm); update=_update_cabinet_dim | 🟢 |
| `tray_divider_thickness` | float (m) | Tray Divider Thickness | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `tray_setback` | float (m) | Tray Setback — Front setback for the tray dividers | padrão 1.0" (25.4 mm); update=_update_cabinet_dim | 🟢 |
| `vanity_z` | float (m) | Shelf Z — Z height of the vanity shelves (both sides) | padrão 11.0" (279.4 mm); update=_update_cabinet_dim | 🟢 |
| `vanity_length` | float (m) | Shelf Length — Length of each side shelf (mirrored L and R) | padrão 7.0" (177.8 mm); update=_update_cabinet_dim | 🟢 |
| `accessory_label` | str | Accessory Label | padrão 'ACCESSORY'; update=_update_cabinet_dim | 🟢 |
| `accessory_code` | str | Accessory Code | padrão '' | 🟢 |

### Face_Frame_Rollout_Box (`props_hb_face_frame.py:5693`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `height_preset` | enum | Height — Standard rollout box height, or Custom to type an exact value | padrão 'IN_4_625'; itens: IN_4_625/IN_6_5/IN_8_375/IN_11_625/CUSTOM; update=_update_rollout_box_preset | 🟢 |
| `height` | float (m) | Box Height — Height of this rollout drawer box | padrão 4.625" (117.5 mm); update=_update_cabinet_dim | 🟢 |

### Face_Frame_Interior_Split_Props (`props_hb_face_frame.py:6313`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `axis` | enum | Axis | padrão 'H'; itens: H/V; update=_update_cabinet_dim | 🟢 |
| `size` | float (m) | Size | padrão 12.0" (304.8 mm); update=_update_interior_size | 🟢 |
| `unlock_size` | bool | Unlock Size — Hold this split's size during sibling redistribution | padrão False; update=_update_cabinet_dim | 🟢 |
| `divider_thickness` | float (m) | Divider Thickness — Thickness of the fixed shelf or division at this split | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `add_face_frame` | bool | Add Face Frame | padrão False; update=_update_interior_add_face_frame | 🟢 |
| `face_frame_width` | float (m) | Face Frame Width — Width of the optional face frame part at this split. Seeded from the cabinet mid rail / mid stile width when first enabled | padrão 0.0; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Interior_Region_Props (`props_hb_face_frame.py:6370`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `interior_items` | Collection[Face_Frame_Interior_Item] |  |  | 🟢 |
| `interior_items_index` | int |  | padrão 0 | 🟢 |
| `size` | float (m) | Size | padrão 12.0" (304.8 mm); update=_update_interior_size | 🟢 |
| `unlock_size` | bool | Unlock Size — Hold this region's size during sibling redistribution | padrão False; update=_update_cabinet_dim | 🟢 |
| `expanded` | bool | Expanded — Show this region's size, divider, and items | padrão False | 🟢 |

### Face_Frame_Scene_Props (`props_hb_face_frame.py:6446`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `face_frame_selection_mode` | enum | Face Frame Selection Mode | padrão 'Cabinets'; itens: Cabinets/Bays/Face Frame/Openings/Interiors/Parts/Applied Panels; update=update_face_frame_selection_mode | 🟢 |
| `face_frame_selection_mode_enabled` | bool | Selection Mode Shading — When off, selection-mode highlighting is disabled: cages stay hidden and every part renders plain regardless of which mode is picked | padrão True; update=update_face_frame_selection_mode | 🟢 |
| `selection_mode_sizes_scope` | enum | Size Labels | padrão 'ALL'; itens: ALL/SELECTED/OFF | 🟢 |
| `face_frame_tabs` | enum | Face Frame Tabs | padrão 'LIBRARY'; itens: LIBRARY/OPTIONS | 🟢 |
| `library_view_mode` | enum | Library View — Show library items as thumbnail tiles or a compact list | padrão 'THUMBNAIL'; itens: THUMBNAIL/LIST | 🟢 |
| `cabinet_group_category` | enum | Category — Filter cabinet groups by category subfolder | itens: dinâmico (get_cabinet_group_category_items) | 🟢 |
| `door_style_tab` | enum | Style Tab — Switch between the door style and drawer front style lists | padrão 'DOOR'; itens: DOOR/DRAWER | 🟢 |
| `include_drawer_boxes` | bool | Include Drawer Boxes — Spawn a drawer box behind every drawer and pullout front | padrão True; update=update_include_drawer_boxes | 🟢 |
| `drawer_box_side_clearance` | float (m) | Drawer Box Side Clearance — Gap between each side of the drawer box and the opening | padrão 0.5" (12.7 mm) | 🟢 |
| `drawer_box_top_clearance` | float (m) | Drawer Box Top Clearance — Gap between the top of the drawer box and the opening top | padrão 0.75" (19.0 mm) | 🟢 |
| `drawer_box_rear_clearance` | float (m) | Drawer Box Rear Clearance — Gap between the back of the drawer box and the cabinet back | padrão 1.0" (25.4 mm) | 🟢 |
| `drawer_box_bottom_clearance` | float (m) | Drawer Box Bottom Clearance — Gap between the bottom of the drawer box and the opening bottom | padrão 0.5" (12.7 mm) | 🟢 |
| `default_finished_end_type` | enum | Default Finished End Type | padrão 'FINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X | 🟢 |
| `default_finished_back_type` | enum | Default Finished Back Type — Finished-end type auto-applied to exposed cabinet backs | padrão 'FINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X | 🟢 |
| `dishwasher_finished_end_type` | enum | Dishwasher Side Finished End Type — Finished end auto-applied to cabinet sides abutting a dishwasher | padrão 'UNFINISHED'; itens: UNFINISHED/FINISHED/PANELED/FALSE_FF/WORKING_FF/BEADBOARD/SHIPLAP/FLUSH_X | 🟢 |
| `default_scribe` | float (m) | Default Scribe | padrão 0.5" (12.7 mm) | 🟢 |
| `default_flush_x_amount` | float (m) | Default Flush X Amount | padrão 4" (101.6 mm) | 🟢 |
| `default_panel_frame_auto` | bool | Default Auto Panel Frame Widths | padrão True | 🟢 |
| `default_panel_top_rail_width` | float (m) | Default Panel Top Rail Width | padrão 1.5" (38.1 mm) | 🟢 |
| `default_panel_bottom_rail_width` | float (m) | Default Panel Bottom Rail Width | padrão 1.5" (38.1 mm) | 🟢 |
| `default_panel_stile_width` | float (m) | Default Panel Stile Width | padrão 1.5" (38.1 mm) | 🟢 |
| `cabinet_styles` | Collection[Face_Frame_Cabinet_Style] |  |  | 🟢 |
| `active_cabinet_style_index` | int | Active Cabinet Style Index | padrão 0 | 🟢 |
| `door_styles` | Collection[Face_Frame_Door_Style] |  |  | 🟢 |
| `active_door_style_index` | int | Active Door Style Index | padrão 0 | 🟢 |
| `drawer_front_styles` | Collection[Face_Frame_Door_Style] |  |  | 🟢 |
| `active_drawer_front_style_index` | int | Active Drawer Front Style Index | padrão 0 | 🟢 |
| `fill_cabinets` | bool | Fill Cabinets — When dropping a cabinet, fill the available space | padrão True | 🟢 |
| `cabinet_placement_holdoff` | float (m) | Cabinet Placement Hold-off | padrão 5.0" (127.0 mm) | 🟢 |
| `default_top_cabinet_clearance` | float (m) | Default Top Cabinet Clearance — Clearance to hold top cabinets from ceiling | padrão 12.0" (304.8 mm); update=update_top_cabinet_clearance | 🟢 |
| `default_wall_cabinet_location` | float (m) | Default Wall Cabinet Location — Distance from floor to bottom of wall cabinet | padrão 54.0" (1371.6 mm); update=update_top_cabinet_clearance | 🟢 |
| `default_cabinet_width` | float (m) | Default Cabinet Width — Default width for cabinets when not filling | padrão 36.0" (914.4 mm) | 🟢 |
| `countertop_thickness` | float (m) | Countertop Thickness — Thickness of the countertop slab | padrão 1.5" (38.1 mm) | 🟢 |
| `countertop_overhang_front` | float (m) | Countertop Front Overhang — Overhang past the front of cabinets | padrão 1.0" (25.4 mm) | 🟢 |
| `countertop_overhang_sides` | float (m) | Countertop Side Overhang — Overhang past exposed ends of cabinets | padrão 1.0" (25.4 mm) | 🟢 |
| `countertop_overhang_back` | float (m) | Countertop Back Overhang — Overhang past the back of cabinets toward wall | padrão 0.0" (0.0 mm) | 🟢 |
| `base_cabinet_depth` | float (m) | Base Cabinet Depth — Default depth for base cabinets | padrão 24.0" (609.6 mm) | 🟢 |
| `base_cabinet_height` | float (m) | Base Cabinet Height — Default height for base cabinets | padrão 34.5" (876.3 mm) | 🟢 |
| `tall_cabinet_depth` | float (m) | Tall Cabinet Depth — Default depth for tall cabinets | padrão 25.5" (647.7 mm) | 🟢 |
| `tall_cabinet_height` | float (m) | Tall Cabinet Height — Default height for tall cabinets | padrão 84.0" (2133.6 mm) | 🟢 |
| `tall_cabinet_split_height` | float (m) | Tall Cabinet Split Height — Height at which a tall cabinet is split into upper and lower sections | padrão 54.0" (1371.6 mm) | 🟢 |
| `top_drawer_opening_height` | float (m) | Top Drawer Opening Height — Height of the top drawer opening in base cabinet drawer presets (1 Drawer x Door, 3 Drawers, 4 Drawers, etc.) | padrão 4.5" (114.3 mm) | 🟢 |
| `upper_cabinet_depth` | float (m) | Upper Cabinet Depth — Default depth for upper cabinets | padrão 12.0" (304.8 mm) | 🟢 |
| `upper_cabinet_height` | float (m) | Upper Cabinet Height — Default height for upper cabinets | padrão 30.0" (762.0 mm) | 🟢 |
| `door_pull_category` | enum | Pull Category | itens: dinâmico (_pull_category_enum_items) | 🟢 |
| `door_pull_selection` | enum | Door Pull | itens: dinâmico (_pull_enum_items); update=_update_pulls_on_selection_change | 🟢 |
| `drawer_pull_selection` | enum | Drawer Pull | itens: dinâmico (_pull_enum_items); update=_update_pulls_on_selection_change | 🟢 |
| `current_door_pull_object` | Pointer[Object] |  |  | 🟢 |
| `current_drawer_pull_object` | Pointer[Object] |  |  | 🟢 |
| `pull_horizontal_offset` | float (m) | Pull Horizontal Offset — Distance from the door's unhinged edge to the pull's nearest edge | padrão 1.5" (38.1 mm); update=_update_pulls_on_selection_change | 🟢 |
| `pull_vertical_location_base` | float (m) | Base Pull Vertical Location | padrão 1.5" (38.1 mm); update=_update_pulls_on_selection_change | 🟢 |
| `pull_vertical_location_tall` | float (m) | Tall Pull Vertical Location | padrão 36.0" (914.4 mm); update=_update_pulls_on_selection_change | 🟢 |
| `pull_vertical_location_upper` | float (m) | Upper Pull Vertical Location | padrão 1.5" (38.1 mm); update=_update_pulls_on_selection_change | 🟢 |
| `center_pulls_on_drawer_front` | bool | Center Pulls on Drawer Front | padrão True; update=_update_pulls_on_selection_change | 🟢 |
| `upper_top_stacked_cabinet_height` | float (m) | Upper Top Stacked Cabinet Height — Height of the top section of a stacked upper cabinet | padrão 12.0" (304.8 mm) | 🟢 |
| `base_inside_corner_size` | float (m) | Base Inside Corner Size — Width and depth for inside base corner cabinets | padrão 36.0" (914.4 mm) | 🟢 |
| `tall_inside_corner_size` | float (m) | Tall Inside Corner Size — Width and depth for inside tall corner cabinets | padrão 36.0" (914.4 mm) | 🟢 |
| `upper_inside_corner_size` | float (m) | Upper Inside Corner Size — Width and depth for inside upper corner cabinets | padrão 24.0" (609.6 mm) | 🟢 |
| `base_width_blind` | float (m) | Base Width Blind — Default width for base blind corner cabinets | padrão 48.0" (1219.2 mm) | 🟢 |
| `tall_width_blind` | float (m) | Tall Width Blind — Default width for tall blind corner cabinets | padrão 48.0" (1219.2 mm) | 🟢 |
| `upper_width_blind` | float (m) | Upper Width Blind — Default width for upper blind corner cabinets | padrão 36.0" (914.4 mm) | 🟢 |
| `refrigerator_height` | float (m) | Refrigerator Height — Default refrigerator height | padrão 69.0" (1752.6 mm) | 🟢 |
| `refrigerator_cabinet_width` | float (m) | Refrigerator Cabinet Width — Default refrigerator cabinet width | padrão 40.0" (1016.0 mm) | 🟢 |
| `range_width` | float (m) | Range Width — Default range width | padrão 36.0" (914.4 mm) | 🟢 |
| `dishwasher_width` | float (m) | Dishwasher Width — Default dishwasher width | padrão 24.0" (609.6 mm) | 🟢 |
| `sink_cabinet_width` | float (m) | Sink Cabinet Width — Default sink cabinet width | padrão 36.0" (914.4 mm) | 🟢 |
| `oven_cabinet_width` | float (m) | Oven Cabinet Width — Default oven cabinet width | padrão 33.0" (838.2 mm) | 🟢 |
| `ff_end_stile_width` | float (m) | End Stile Width — Default end stile width | padrão 2.0" (50.8 mm) | 🟢 |
| `ff_blind_stile_width` | float (m) | Blind Stile Width — Visible (exposed) portion of a blind-corner end stile | padrão 3.0" (76.2 mm) | 🟢 |
| `ff_top_rail_width` | float (m) | Top Rail Width — Default top rail width | padrão 1.5" (38.1 mm) | 🟢 |
| `ff_bottom_rail_width` | float (m) | Bottom Rail Width — Default bottom rail width | padrão 1.5" (38.1 mm) | 🟢 |
| `ff_mid_stile_width` | float (m) | Mid Stile Width — Default mid stile width | padrão 2.0" (50.8 mm) | 🟢 |
| `ff_face_frame_thickness` | float (m) | Face Frame Thickness — Thickness of face frame members | padrão 0.75" (19.0 mm) | 🟢 |
| `ff_door_overlay` | float (m) | Default Door Overlay — Default amount the door overlays the face frame | padrão 0.5" (12.7 mm) | 🟢 |

### Face_Frame_Cabinet_Style (`props_hb_face_frame.py:877`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | Name — Cabinet style name | padrão 'Style'; update=update_cabinet_style_name | 🟢 |
| `rename_anchor` | str | Rename Anchor — Internal: the style's previous name, used to propagate a rename to cabinets tagged with the old STYLE_NAME | padrão '' | 🟢 |
| `color_in_2d_drawings` | float[3] | 2D Drawing Color — Fill color for cabinets of this style in 2D shop drawings | padrão (1.0, 1.0, 1.0); min 0.0; max 1.0 | 🟢 |
| `wood_species` | enum | Wood Species — Wood species for cabinet exterior | padrão 'MAPLE'; itens: MAPLE/OAK/CHERRY/WALNUT/BIRCH/HICKORY/ALDER/PAINT_GRADE/CUSTOM_PROCEDURAL/CUSTOM; update=_propagate_cabinet_style | 🟢 |
| `stain_color` | enum | Stain Color — Stain color for cabinet finish | itens: dinâmico (get_stain_color_enum_items); update=_propagate_cabinet_style | 🟢 |
| `paint_color` | enum | Paint Color — Paint color for cabinet finish | itens: dinâmico (get_paint_color_enum_items); update=_propagate_cabinet_style | 🟢 |
| `finish_wood` | enum | Wood Specie — Catalog wood specie (gates the available colors) | itens: dinâmico (get_finish_wood_items); update=update_finish_wood | 🟢 |
| `finish_color` | enum | Color — Finish color available for the chosen wood specie | itens: dinâmico (get_finish_color_items); update=update_finish_color | 🟢 |
| `finish_varnish` | enum | Varnish — Varnish available for the chosen color (stain colors only) | itens: dinâmico (get_finish_varnish_items) | 🟢 |
| `finish_glaze` | enum | Glaze — Glaze available for the chosen color | itens: dinâmico (get_finish_glaze_items) | 🟢 |
| `finish_overlay` | enum | Overlay (catalog) — Catalog door overlay (gates the available hinges) | itens: dinâmico (get_finish_overlay_items); update=update_finish_overlay | 🟢 |
| `finish_hinge` | enum | Hinge — Hinge available for the chosen overlay | itens: dinâmico (get_finish_hinge_items) | 🟢 |
| `interior_material_type` | enum | Interior Material — Material for cabinet interior | padrão 'MAPLE_PLY'; itens: MAPLE_PLY/MATCHING/CUSTOM; update=_propagate_cabinet_style | 🟢 |
| `door_overlay_type` | enum | Door Overlay — Door overlay style for face frame cabinets | padrão 'CLASSIC'; itens: CLASSIC/TRANSITIONAL/FULL/PARTIAL_INSET/FULL_INSET; update=update_face_frame_sizes | 🟢 |
| `ff_top_rail_width_base` | float (m) | Top Rail (Base) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_top_rail_width_tall` | float (m) | Top Rail (Tall) | padrão 3.5" (88.9 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_top_rail_width_upper` | float (m) | Top Rail (Upper) | padrão 3.5" (88.9 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_bottom_rail_width_base` | float (m) | Bottom Rail (Base) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_bottom_rail_width_tall` | float (m) | Bottom Rail (Tall) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_bottom_rail_width_upper` | float (m) | Bottom Rail (Upper) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_rail_width_base` | float (m) | Mid Rail (Base) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_rail_width_tall` | float (m) | Mid Rail (Tall) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_rail_width_upper` | float (m) | Mid Rail (Upper) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_wall_stile_width_base` | float (m) | Wall Stile (Base) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_wall_stile_width_tall` | float (m) | Wall Stile (Tall) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_wall_stile_width_upper` | float (m) | Wall Stile (Upper) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_stile_width_base` | float (m) | Mid Stile (Base) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_stile_width_tall` | float (m) | Mid Stile (Tall) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_mid_stile_width_upper` | float (m) | Mid Stile (Upper) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_end_stile_width_base` | float (m) | End Stile (Base) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_end_stile_width_tall` | float (m) | End Stile (Tall) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_end_stile_width_upper` | float (m) | End Stile (Upper) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_blind_stile_width_base` | float (m) | Blind Stile (Base) | padrão 3.0" (76.2 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_blind_stile_width_tall` | float (m) | Blind Stile (Tall) | padrão 3.0" (76.2 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_blind_stile_width_upper` | float (m) | Blind Stile (Upper) | padrão 2.0" (50.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_butt_stile_width_base` | float (m) | Butt Stile (Base) | padrão 1.25" (31.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_butt_stile_width_tall` | float (m) | Butt Stile (Tall) | padrão 1.25" (31.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_butt_stile_width_upper` | float (m) | Butt Stile (Upper) | padrão 1.25" (31.8 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_inside_90_stile_width_base` | float (m) | Inside 90 Stile (Base) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_inside_90_stile_width_tall` | float (m) | Inside 90 Stile (Tall) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_inside_90_stile_width_upper` | float (m) | Inside 90 Stile (Upper) | padrão 1.0" (25.4 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_angle_stile_width_base` | float (m) | Angle Stile (Base) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_angle_stile_width_tall` | float (m) | Angle Stile (Tall) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `ff_angle_stile_width_upper` | float (m) | Angle Stile (Upper) | padrão 1.5" (38.1 mm); update=_propagate_cabinet_style | 🟢 |
| `unlock_base_top_rail` | bool | Unlock Base Top Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_tall_top_rail` | bool | Unlock Tall Top Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_upper_top_rail` | bool | Unlock Upper Top Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_base_bottom_rail` | bool | Unlock Base Bottom Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_tall_bottom_rail` | bool | Unlock Tall Bottom Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_upper_bottom_rail` | bool | Unlock Upper Bottom Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_base_mid_rail` | bool | Unlock Base Mid Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_tall_mid_rail` | bool | Unlock Tall Mid Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `unlock_upper_mid_rail` | bool | Unlock Upper Mid Rail | padrão False; update=update_face_frame_sizes | 🟢 |
| `door_style` | enum | Door Style — Door style applied to door fronts on cabinets carrying this style | itens: dinâmico (get_door_style_enum_items); update=_propagate_cabinet_style | 🟢 |
| `drawer_front_style` | enum | Drawer Front Style — Drawer front style applied to drawer fronts on cabinets carrying this style | itens: dinâmico (get_drawer_front_style_enum_items); update=_propagate_cabinet_style | 🟢 |
| `ss_corner_treatment` | enum | Corner Treatment — Corner treatment for the style section page | padrão 'Square'; itens: 1/4" x 1/4" Chamfer/Cove/1/8" Radius/Square/1/4" Radius/3/8" Radius | 🟢 |
| `ss_fin_opening_edge` | enum | Fin Opening Edge — Finished opening edge treatment for the style section page | padrão 'Square'; itens: 1/8" Radius/1/4" Radius/1/4" Drop Radius/1/4" x 1/4" Chamfer/3/8" Radius/3/8" Drop Radius/Beaded/Classic Cut/Cove/Square | 🟢 |
| `ss_drawer_grain` | str | Drawer Grain — Override the drawer-front grain on the style section page; blank uses the drawer front style's grain direction | padrão '' | 🟢 |
| `ss_drawer_top_opening_height` | str | Top Opening Height — Override the top drawer opening height on the style section page; blank uses hb_face_frame.top_drawer_opening_height | padrão '' | 🟢 |
| `ss_drawer_slides` | enum | Drawer Slides — Drawer slide hardware for the style section page | padrão 'Tandem BLUMOTION'; itens: Tandem BLUMOTION/KV8400/KV4270 | 🟢 |
| `ss_drawer_box_construction` | enum | Box Construction — Drawer box construction for the style section page | padrão 'French'; itens: French/English | 🟢 |
| `ss_wood` | str | Wood (override) — Override the wood text on the style section page (blank = catalog value) | padrão '' | 🟢 |
| `ss_interior` | str | Interior (override) — Override the interior text (blank = catalog value) | padrão '' | 🟢 |
| `ss_overlay` | str | Overlay (override) — Override the overlay text (blank = catalog value) | padrão '' | 🟢 |
| `ss_color` | str | Color (override) — Override the color text (blank = catalog value) | padrão '' | 🟢 |
| `ss_varnish` | str | Varnish (override) — Override the varnish text (blank = catalog value) | padrão '' | 🟢 |
| `ss_glaze` | str | Glaze (override) — Override the glaze text (blank = catalog value) | padrão '' | 🟢 |
| `ss_color_ref_name` | str | Color Reference — Reference name for the color, shown on the Style Section finish row | padrão '' | 🟢 |
| `ss_color_ref_image` | str | Color Reference Image — Path to a reference image for the color, shown in the Style Section references box | padrão '' | 🟢 |
| `ss_varnish_ref_name` | str | Varnish Reference — Reference name for the varnish, shown on the Style Section finish row | padrão '' | 🟢 |
| `ss_varnish_ref_image` | str | Varnish Reference Image — Path to a reference image for the varnish, shown in the Style Section references box | padrão '' | 🟢 |
| `ss_glaze_ref_name` | str | Glaze Reference — Reference name for the glaze, shown on the Style Section finish row | padrão '' | 🟢 |
| `ss_glaze_ref_image` | str | Glaze Reference Image — Path to a reference image for the glaze, shown in the Style Section references box | padrão '' | 🟢 |
| `ss_door` | str | Door Style (override) — Override the door style text (blank = composed catalog name) | padrão '' | 🟢 |
| `ss_hinge` | str | Hinge (override) — Override the hinge text (blank = catalog value) | padrão '' | 🟢 |
| `ss_drawer` | str | Drawer Style (override) — Override the drawer style text (blank = composed catalog name) | padrão '' | 🟢 |
| `ss_drawer_box_brand` | str | Drawer Box Brand — Path to a drawer-box brand logo image shown in the DRAWERS section of the Style Section page | padrão '' | 🟢 |
| `ss_edge_profile` | enum | Edge Profile | padrão 'None'; itens: None/Bay/Beveled/Chamfer/Classic Cut/Drop Radius/Eclipse/Estate/New Cut/Square/1/8" Radius/1/4" Radius/3/8" Radius/3/8" Inset 1/8" Radius/3/8" Inset Radius/3/8" Inset square; update=_propagate_cabinet_style | 🟢 |
| `ss_corner_treatment_is_custom` | bool | Custom Corner Treatment | padrão False | 🟢 |
| `ss_corner_treatment_custom` | str | Corner Treatment | padrão '' | 🟢 |
| `ss_fin_opening_edge_is_custom` | bool | Custom Fin Opening Edge | padrão False | 🟢 |
| `ss_fin_opening_edge_custom` | str | Fin Opening Edge | padrão '' | 🟢 |
| `ss_drawer_slides_is_custom` | bool | Custom Drawer Slides | padrão False | 🟢 |
| `ss_drawer_slides_custom` | str | Drawer Slides | padrão '' | 🟢 |
| `ss_drawer_box_construction_is_custom` | bool | Custom Box Construction | padrão False | 🟢 |
| `ss_drawer_box_construction_custom` | str | Box Construction | padrão '' | 🟢 |
| `ss_edge_profile_is_custom` | bool | Custom Edge Profile | padrão False; update=_propagate_cabinet_style | 🟢 |
| `ss_edge_profile_custom` | str | Edge Profile | padrão ''; update=_propagate_cabinet_style | 🟢 |
| `ss_wood_is_custom` | bool | Custom Wood | padrão False | 🟢 |
| `ss_wood_custom` | str | Wood | padrão '' | 🟢 |
| `ss_interior_is_custom` | bool | Custom Interior | padrão False | 🟢 |
| `ss_interior_custom` | str | Interior | padrão '' | 🟢 |
| `ss_overlay_is_custom` | bool | Custom Overlay | padrão False | 🟢 |
| `ss_overlay_custom` | str | Overlay | padrão '' | 🟢 |
| `ss_color_is_custom` | bool | Custom Color | padrão False | 🟢 |
| `ss_color_custom` | str | Color | padrão '' | 🟢 |
| `ss_varnish_is_custom` | bool | Custom Varnish | padrão False | 🟢 |
| `ss_varnish_custom` | str | Varnish | padrão '' | 🟢 |
| `ss_glaze_is_custom` | bool | Custom Glaze | padrão False | 🟢 |
| `ss_glaze_custom` | str | Glaze | padrão '' | 🟢 |
| `ss_door_is_custom` | bool | Custom Door | padrão False | 🟢 |
| `ss_door_custom` | str | Door | padrão '' | 🟢 |
| `ss_hinge_is_custom` | bool | Custom Hinge | padrão False | 🟢 |
| `ss_hinge_custom` | str | Hinge | padrão '' | 🟢 |
| `ss_drawer_is_custom` | bool | Custom Drawer Front | padrão False | 🟢 |
| `ss_drawer_custom` | str | Drawer Front | padrão '' | 🟢 |
| `millwork_items` | Collection[Face_Frame_Millwork_Item] | Millwork Items |  | 🟢 |
| `millwork_index` | int | Millwork Index | padrão 0 | 🟢 |
| `special_effects` | Collection[Face_Frame_Special_Effect] | Special Effects |  | 🟢 |
| `special_effect_index` | int | Special Effect Index | padrão 0 | 🟢 |
| `extra_door_styles` | Collection[Face_Frame_Cabinet_Extra_Front_Style] | Extra Door Styles |  | 🟢 |
| `extra_drawer_front_styles` | Collection[Face_Frame_Cabinet_Extra_Front_Style] | Extra Drawer Front Styles |  | 🟢 |
| `material` | Pointer[Material] | Material |  | 🟢 |
| `material_rotated` | Pointer[Material] | Material Rotated |  | 🟢 |
| `interior_material` | Pointer[Material] | Interior Material |  | 🟢 |
| `interior_material_rotated` | Pointer[Material] | Interior Material Rotated |  | 🟢 |
| `custom_material` | Pointer[Material] | Custom Exterior Material | update=_propagate_cabinet_style | 🟢 |
| `custom_interior_material` | Pointer[Material] | Custom Interior Material | update=_propagate_cabinet_style | 🟢 |
| `custom_wood_color_1` | float[3] | Wood Color 1 | padrão (0.8, 0.65, 0.45); min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_wood_color_2` | float[3] | Wood Color 2 | padrão (0.6, 0.45, 0.3); min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_noise_scale_1` | float | Noise Scale 1 | padrão 3.5; min 0.0; max 50.0; update=update_custom_procedural_material | 🟢 |
| `custom_noise_scale_2` | float | Noise Scale 2 | padrão 2.5; min 0.0; max 50.0; update=update_custom_procedural_material | 🟢 |
| `custom_texture_variation_1` | float | Texture Variation 1 | padrão 0.1; min 0.0; max 20.0; update=update_custom_procedural_material | 🟢 |
| `custom_texture_variation_2` | float | Texture Variation 2 | padrão 12.5; min 0.0; max 20.0; update=update_custom_procedural_material | 🟢 |
| `custom_noise_detail` | float | Noise Detail | padrão 15.0; min 0.0; max 20.0; update=update_custom_procedural_material | 🟢 |
| `custom_voronoi_detail_1` | float | Voronoi Detail 1 | padrão 0.0; min 0.0; max 10.0; update=update_custom_procedural_material | 🟢 |
| `custom_voronoi_detail_2` | float | Voronoi Detail 2 | padrão 0.2; min 0.0; max 10.0; update=update_custom_procedural_material | 🟢 |
| `custom_knots_scale` | float | Knots Scale | padrão 0.0; min 0.0; max 20.0; update=update_custom_procedural_material | 🟢 |
| `custom_knots_darkness` | float | Knots Darkness | padrão 0.0; min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_roughness` | float | Roughness | padrão 1.0; min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_noise_bump_strength` | float | Noise Bump Strength | padrão 0.1; min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_knots_bump_strength` | float | Knots Bump Strength | padrão 0.15; min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |
| `custom_wood_bump_strength` | float | Wood Bump Strength | padrão 0.2; min 0.0; max 1.0; update=update_custom_procedural_material | 🟢 |

### Face_Frame_Door_Style (`props_hb_face_frame.py:2883`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | Name — Door style name | padrão 'Door Style'; update=update_door_style_name | 🟢 |
| `show_expanded` | bool | Show Expanded — Show expanded style options | padrão False | 🟢 |
| `front_series` | enum | Series — Catalog series (gates the available shapes) | itens: dinâmico (get_front_series_items); update=update_front_series | 🟢 |
| `front_shape` | enum | Shape — Shape available for the chosen series | itens: dinâmico (get_front_shape_items); update=update_front_shape | 🟢 |
| `front_panel` | enum | Panel — Panel available for the chosen series + shape | itens: dinâmico (get_front_panel_items); update=update_front_panel | 🟢 |
| `door_type` | enum | Door Type — Door construction type | padrão '5_PIECE'; itens: SLAB/5_PIECE; update=_propagate_door_style | 🟢 |
| `panel_material` | enum | Panel Material — Material for door panel center | padrão 'MATCH_CABINET'; itens: MATCH_CABINET/GLASS; update=_propagate_door_style | 🟢 |
| `grain_direction` | enum | Grain Direction — Direction the wood grain runs on this front | padrão 'VERTICAL'; itens: NONE/VERTICAL/HORIZONTAL; update=update_grain_direction | 🟢 |
| `outside_profile_name` | enum | Outside Profile — Outside edge profile from the shipped library | itens: dinâmico (get_outer_profile_items); update=_propagate_door_style | 🟢 |
| `inside_profile_name` | enum | Inside Profile — Inside (sticking) profile from the shipped library | itens: dinâmico (get_inner_profile_items); update=_propagate_door_style | 🟢 |
| `panel_profile_name` | enum | Panel Profile — Raised panel profile from the shipped library | itens: dinâmico (get_panel_profile_items); update=_propagate_door_style | 🟢 |
| `unlock_profiles` | bool | Unlock Profiles — Override the series' outside / inside / panel profiles | padrão False; update=update_unlock_frame_widths | 🟢 |
| `outside_profile` | Pointer[Object] | Outside Profile | update=_propagate_door_style | 🟢 |
| `inside_profile` | Pointer[Object] | Inside Profile | update=_propagate_door_style | 🟢 |
| `panel_profile` | Pointer[Object] | Panel Profile | update=_propagate_door_style | 🟢 |
| `unlock_stile_width` | bool | Unlock Stile Width — Override the catalog stile width; re-lock to snap back to the series spec | padrão False; update=update_unlock_frame_widths | 🟢 |
| `unlock_rail_width` | bool | Unlock Rail Width — Override the catalog rail width; re-lock to snap back to the series spec | padrão False; update=update_unlock_frame_widths | 🟢 |
| `show_rail_annotation` | bool | Show Rail Callout — Show the rail-size callout (e.g. '3R') on fronts whose rail width deviates from the catalog spec | padrão True; update=_propagate_door_style | 🟢 |
| `match_door_rail_width` | bool | Match Door Rail Width When Possible | padrão False; update=_propagate_door_style | 🟢 |
| `stile_width` | float (m) | Stile Width — Width of left and right stiles | padrão 3.0" (76.2 mm); update=_propagate_door_style | 🟢 |
| `rail_width` | float (m) | Rail Width — Width of top and bottom rails (the mid rail follows it) | padrão 3.0" (76.2 mm); update=update_rail_width | 🟢 |
| `add_mid_rail` | bool | Add Mid Rail — Add a horizontal mid rail | padrão False; update=_propagate_door_style | 🟢 |
| `center_mid_rail` | bool | Center Mid Rail — Center the mid rail vertically | padrão True; update=_propagate_door_style | 🟢 |
| `mid_rail_width` | float (m) | Mid Rail Width — Width of the mid rail | padrão 3.0" (76.2 mm); update=_propagate_door_style | 🟢 |
| `mid_rail_location` | float (m) | Mid Rail Location — Distance from bottom of door to mid rail (if not centered) | padrão 12.0" (304.8 mm); update=_propagate_door_style | 🟢 |
| `panel_thickness` | float (m) | Panel Thickness — Thickness of the center panel | padrão 0.5" (12.7 mm); update=_propagate_door_style | 🟢 |
| `panel_inset` | float (m) | Panel Inset — How far panel is inset from frame face | padrão 0.25" (6.3 mm); update=_propagate_door_style | 🟢 |
| `edge_profile_type` | enum | Edge Profile — Edge profile for slab doors | padrão 'SQUARE'; itens: SQUARE/EASED/OGEE/BEVEL/ROUNDOVER; update=_propagate_door_style | 🟢 |

### Face_Frame_Leg_Props (`props_hb_face_frame.py:7816`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `finish_type` | enum | Finish Type | padrão 'FINISH_LEFT'; itens: FINISH_LEFT/INTERMEDIATE/FINISH_RIGHT/FINISH_BOTH; update=_update_cabinet_dim | 🟢 |
| `only_stile` | bool | Only Include Stile — Drop the side panels and toe-kick filler; keep just the face-frame stile | padrão False; update=_update_cabinet_dim | 🟢 |
| `is_column` | bool | Column — Column variant: no toe kick (runs full height) | padrão False; update=_update_cabinet_dim | 🟢 |
| `show_panel_depth` | bool | Panel Depth Overrides | padrão False | 🟢 |
| `show_back_nailers` | bool | Back & Nailers | padrão False | 🟢 |
| `show_finish_x` | bool | Finish-X Bands | padrão False | 🟢 |
| `material_thickness` | float (m) | Material Thickness | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `face_frame_thickness` | float (m) | Face Frame Thickness | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `toe_kick_height` | float (m) | Toe Kick Height | padrão 4.0" (101.6 mm); update=_update_cabinet_dim | 🟢 |
| `toe_kick_setback` | float (m) | Toe Kick Setback | padrão 3.0" (76.2 mm); update=_update_cabinet_dim | 🟢 |
| `override_left_panel_depth` | float (m) | Override Left Panel Depth | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `override_right_panel_depth` | float (m) | Override Right Panel Depth | padrão 0.0; update=_update_cabinet_dim | 🟢 |
| `include_back_left_nailer` | bool | Include Back Left Nailer | padrão False; update=_update_cabinet_dim | 🟢 |
| `include_back_right_nailer` | bool | Include Back Right Nailer | padrão False; update=_update_cabinet_dim | 🟢 |
| `back_width` | float (m) | Back Width | padrão 18.0" (457.2 mm); update=_update_cabinet_dim | 🟢 |
| `back_thickness` | float (m) | Back Thickness | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |
| `nailer_thickness` | float (m) | Nailer Thickness | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `nailer_width` | float (m) | Nailer Width | padrão 1.5" (38.1 mm); update=_update_cabinet_dim | 🟢 |
| `flush_x_panel_width` | float (m) | Flush X Panel Width | padrão 4.0" (101.6 mm); update=_update_cabinet_dim | 🟢 |
| `is_appliance_leg` | bool | Appliance Leg | padrão False; update=_update_cabinet_dim | 🟢 |
| `is_island_leg` | bool | Island Leg | padrão False; update=_update_cabinet_dim | 🟢 |

### Face_Frame_Floating_Shelf_Props (`props_hb_face_frame.py:7936`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `finish_left` | bool | Finish Left — Close the left end with a finished panel | padrão True; update=_update_cabinet_dim | 🟢 |
| `finish_right` | bool | Finish Right — Close the right end with a finished panel | padrão True; update=_update_cabinet_dim | 🟢 |
| `material_thickness` | float (m) | Material Thickness | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `shelf_type` | enum | Shelf Type | padrão 'FLOATING'; itens: FLOATING/NON_FLOATING/HEAVY_DUTY; update=_update_cabinet_dim | 🟢 |
| `include_groove_top` | bool | Groove Top | padrão False; update=_update_cabinet_dim | 🟢 |
| `include_groove_bottom` | bool | Groove Bottom | padrão False; update=_update_cabinet_dim | 🟢 |
| `groove_distance_from_rear` | float (m) | Groove Distance From Rear | padrão 2.0" (50.8 mm); update=_update_cabinet_dim | 🟢 |
| `groove_width` | float (m) | Groove Width | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `groove_depth` | float (m) | Groove Depth | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |

### Face_Frame_Valance_Props (`props_hb_face_frame.py:7993`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `finish_left` | bool | Finish Left — Close the left end with a finished return panel | padrão True; update=_update_cabinet_dim | 🟢 |
| `finish_right` | bool | Finish Right — Close the right end with a finished return panel | padrão True; update=_update_cabinet_dim | 🟢 |
| `frame_thickness` | float (m) | Frame Thickness — Stock thickness of the valance board and return panels | padrão 0.75" (19.0 mm); update=_update_cabinet_dim | 🟢 |
| `include_cover` | bool | Include Cover — Add a cover board behind the valance board | padrão True; update=_update_cabinet_dim | 🟢 |
| `cover_thickness` | float (m) | Cover Thickness — Stock thickness of the cover board | padrão 0.5" (12.7 mm); update=_update_cabinet_dim | 🟢 |
| `flush_bottom` | bool | Flush Bottom — Rest the cover at the bottom of the valance instead of below the top edge | padrão False; update=_update_cabinet_dim | 🟢 |
| `top_scribe` | float (m) | Top Scribe Amount — Drop the cover down from the top edge by this amount | padrão 0.25" (6.3 mm); update=_update_cabinet_dim | 🟢 |

---

## closets

> Dicionário de dados do módulo legado `blendertomob/product_libraries/closets/`. Unidades de comprimento em **metros** (valores
> default mostrados também em in/mm). Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

### Closet_Starter_Props (`Object.hb_closet_starter`) — `props_closets.py:106-142`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| width | FloatProperty (LENGTH) | largura total do starter (X); update → recálculo | 80 in (2,032 m); sem min/max | 🟢 |
| height | FloatProperty (LENGTH) | altura do envelope (Z) | 819 mm | 🟢 |
| depth | FloatProperty (LENGTH) | profundidade (Y) | 14 in (355,6 mm) | 🟢 |
| closet_type | EnumProperty | BASE / TALL / HANGING / ISLAND (sem update) | BASE | 🟢 |
| toe_kick_height | FloatProperty (LENGTH) | altura do rodapé | 96 mm | 🟢 |
| toe_kick_setback | FloatProperty (LENGTH) | recuo do rodapé | 1,625 in (41,3 mm) | 🟢 |
| include_countertop | BoolProperty | cria/mostra tampo (lazy) | False (Base/Ilha semeiam True) | 🟢 |

### Closet_Bay_Props (`Object.hb_closet_bay`) — `props_closets.py:148-180`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| bay_index | IntProperty | índice do vão (espelha idprop `hb_bay_index`) | 0 | 🟢 |
| width | FloatProperty (LENGTH) | largura livre do vão; edição do usuário trava | 0.0; solver impõe ≥ 1 in | 🟢 |
| width_locked | BoolProperty | mantém a largura na redistribuição | False | 🟢 |
| height | FloatProperty (LENGTH) | altura do envelope do vão (piso→topo, ou topo→base se suspenso) | 819 mm; grab ≥ kick+2·st+1 in | 🟢 |
| depth | FloatProperty (LENGTH) | profundidade do vão | 14 in | 🟢 |
| floor_mounted | BoolProperty | de piso (com rodapé) ou suspenso | True | 🟢 |
| remove_bottom | BoolProperty | oculta prateleira inferior (e rodapé); cleat desce | False | 🟢 |
| remove_cleat | BoolProperty | oculta cleat | False | 🟢 |

### Closets_Scene_Props (`Scene.hb_closets`) — `props_closets.py:186-372`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| default_closet_width | Float (LENGTH) | largura inicial de novos starters | 80 in | 🟢 |
| default_panel_depth | Float (LENGTH) | profundidade inicial | 14 in | 🟢 |
| base_panel_height | Float (LENGTH) | altura Base/Ilha | 819 mm | 🟢 |
| tall_panel_height | Float (LENGTH) | altura Tall | 2131 mm | 🟢 |
| hanging_panel_height | Float (LENGTH) | altura dos vãos suspensos / L Upper | 1267 mm | 🟢 |
| hanging_top_height | Float (LENGTH) | piso → topo dos suspensos | 2131 mm | 🟢 |
| panel_thickness | Float (LENGTH) | espessura de painel (pt) | 0,75 in (19,05 mm) | 🟢 |
| shelf_thickness | Float (LENGTH) | espessura de prateleira (st) | 0,75 in | 🟢 |
| countertop_thickness | Float (LENGTH) | espessura do tampo | 1,125 in (28,6 mm) | 🟢 |
| toe_kick_height / toe_kick_setback | Float (LENGTH) | defaults de rodapé | 96 mm / 1,625 in | 🟢 |
| closet_selection_mode | Enum | Starters/Bays/Openings/Parts; update chama `toggle_mode` | Starters | 🟢 |
| closet_selection_mode_enabled | Bool | liga destaque/overlay | True | 🟢 |
| selection_mode_show_sizes | Bool | mostra rótulos editáveis | True | 🟢 |
| closet_material | Enum dinâmico | material da carcaça (library.blend, assets_only) | 1º item ('White') | 🟢 |
| closet_front_material | Enum dinâmico | material das frentes (MATCH = carcaça) | MATCH | 🟢 |
| closet_edge_material / closet_front_edge_material | Enum dinâmico | fitas de borda (MATCH = superfície) | MATCH | 🟢 |
| closet_panel_type | Enum | Vertical Grain / Clear / Mirror / Frosted Matte Glass | Vertical Grain | 🟢 |
| closet_door_grain / closet_drawer_grain | Enum | VERTICAL / HORIZONTAL | VERTICAL / HORIZONTAL | 🟢 |
| closet_pull | Enum dinâmico (ícones) | arquivo de puxador em assets/handles ou NONE | 'CLASSIC 96.blend' | 🟢 |
| closet_pull_finish | Enum | Black, Matte Aluminum, Matte Gold, Matte Nickel, Polished Chrome, Slate | Polished Chrome | 🟢 |
| pull_horizontal_offset | Float (LENGTH) | borda da porta → centro do puxador | 2 in | 🟢 |
| pull_vertical_location_base / _tall / _upper | Float (LENGTH) | topo da porta→topo do puxador / altura do piso / base→base | 1,5 in / 45 in / 1,5 in | 🟢 |
| center_pulls_on_drawer_front | Bool | centraliza puxador na gaveta | True | 🟢 |
| closet_rod_type | Enum | OVAL ("Signature") / ROUND | OVAL | 🟢 |
| closet_rod_finish | Enum | acabamentos de varão (Slate Graphite ...) | Polished Chrome | 🟢 |
| closet_hanger_model | Enum dinâmico | modelo de cabide (bundled + pacote do usuário) ou NONE | 'Hanger Model.blend' | 🟢 |
| closet_drawer_box | Enum | AVANTECH / AVANTECH_ILL / METABOX / WOOD / NONE | AVANTECH | 🟢 |
| closet_front_style | Enum | SLAB, NARROW/CONTEMPORARY/WIDE × SHAKER/MITER, COMBINATION | SLAB | 🟢 |
| closet_crown_profile | Enum dinâmico | perfil de moldura (sem update) | 'L Crown with Light Shield.blend' | 🟢 |
| show_closet_sizes / show_starter_library / show_closet_options / show_material_options / show_pull_options | Bool | estado da UI | F / T / F / F / F | 🟢 |

### Starter root (Object, idprops soltas) — `types_closets.py:259-262, 475-519, 1271-1339`; `ops_closet.py:2644-2649`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_CLOSET_STARTER_CAGE | bool | tag de identidade | True | 🟢 |
| CLASS_NAME | str | nome da classe p/ `_wrap_starter` | ex. 'BaseClosetStarter' | 🟢 |
| MENU_ID | str | menu de contexto | 'HOME_BUILDER_MT_closet_starter_commands' | 🟢 |
| hb_last_height / hb_last_depth | float | últimos valores aplicados (propagação e âncora de topo) | — | 🟢 |
| hb_remove_hang_rail | int/bool | oculta todos os trilhos | ausente = 0 | 🟢 |
| hb_bridge_left / hb_bridge_right | int | ponte superior ativa | 0/1 | 🟢 |
| hb_bridge_w_left / hb_bridge_w_right | float | vão da ponte além do painel de ponta | ≥ 0 | 🟢 |
| hb_bridge_bot_left / hb_bridge_bot_right | int | ponte inferior (+ rodapé em vão de piso) | 0/1 | 🟢 |
| hb_l_left_depth / hb_l_right_depth | float | (L-shelf) profundidade das asas | default_panel_depth; ≤ W−pt / D−pt | 🟢 |
| hb_l_shelf_qty | int | (L-shelf) prateleiras intermediárias | 3 (+2 topo/base) | 🟢 |
| Inputs GN Dim X/Y/Z, Mirror Y | float/bool | dimensões do cage | = W/D/H | 🟢 |

### Bay cage (Object, idprops) — `types_closets.py:139-148, 92-96, 323`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_CLOSET_BAY_CAGE | bool | tag | True | 🟢 |
| hb_bay_index | int | ordem do vão (reindexado em insert/delete/mirror) | 0..N−1 | 🟢 |
| hb_bay_door_swing | str | portas do vão inteiro: '' / LEFT / RIGHT / DOUBLE | '' | 🟢 |
| hb_bay_is_hamper | int | porta do vão é basculante | 0 | 🟢 |
| MENU_ID | str | 'HOME_BUILDER_MT_closet_bay_commands' | — | 🟢 |

### Opening cage (Object, idprops) — `types_closets.py:78-100, 151-160, 677`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_CLOSET_OPENING_CAGE | bool | tag | True | 🟢 |
| hb_opening_index | int | índice do segmento (baixo→cima) por lado | 0.. | 🟢 |
| hb_opening_side | str | FRONT / BACK (ilha dupla) | FRONT | 🟢 |
| hb_seg_bottom | float | início do segmento no Z interno do vão | reescrito a cada recálculo | 🟢 |
| hb_adj_shelf_qty | int | prateleiras reguláveis | 0; diálogo 0–20 | 🟢 |
| hb_drawer_qty | int | nº de gavetas | 0; diálogo 0–10; preset 1–8 | 🟢 |
| hb_drawer_front_height | float | altura nominal (posiciona a tampa) | 7,5 in | 🟢 |
| hb_door_swing | str | '' / LEFT / RIGHT / DOUBLE | '' | 🟢 |
| hb_is_hamper | int | porta basculante | 0 | 🟢 |
| hb_cubby_cols / hb_cubby_rows | int | grade de nichos | 1; diálogo 1–12; preset 3×3 | 🟢 |

### Peça interior (prateleira fixa/regulável/nicho, varão) — `types_closets.py:52-62, 181-206`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| hb_part_role | str | papel (CLOSET_FIXED_SHELF, _ADJ_SHELF, _ROD, _CUBBY_*) | — | 🟢 |
| hb_z_offset | float | distância da base (ou do topo se ancorado) à face inferior / eixo do varão | clamp ao interior | 🟢 |
| hb_anchor_top | int | 1 = mede do topo (varões) | 0 prateleira / 1 varão | 🟢 |
| hb_preview | int | peça em preview (ignorada pelo reconciliador) | ausente | 🟢 |
| hb_adj_index / hb_cubby_index / hb_l_index | int | ordem para o regenerador | 0.. | 🟢 |
| hb_opening_side | str | lado da divisora (após adoção pelo vão) | FRONT | 🟢 |
| Inputs GN rod: Radius, Cup Depth, Cup Depth 2, Is Oval, Dim X, Material | float/bool/Material | varão | 1 in, 0,2 in, 0,8 in, True | 🟢 |

### Frente (porta / frente de gaveta) — `types_closets.py:83-91, 1023-1034, 1805-1864`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| hb_part_role | str | CLOSET_DOOR_FRONT / CLOSET_DRAWER_FRONT | — | 🟢 |
| hb_door_index / hb_drawer_index | int | ordem | 0.. | 🟢 |
| hb_bay_door | int | porta pertence ao vão inteiro | ausente/1 | 🟢 |
| hb_hinge | str | LEFT / RIGHT | LEFT | 🟢 |
| hb_is_hamper | int | basculante | 0 | 🟢 |
| hb_front_height | float | altura resolvida (reescrita a cada recálculo) | ≥ 2 in se destravada | 🟢 |
| hb_front_locked | int | frente fixada pelo usuário | 0 | 🟢 |
| hb_door_cx/cy/cz, hb_door_leaf, hb_door_side | float/str | estado fechado para girar | — | 🟢 |
| hb_door_open / hb_drawer_open | int | estado persistente aberto | 0 | 🟢 |
| hb_slide_y0 / hb_slide_dist | float | posição fechada / curso da gaveta | curso ≤ 12 in | 🟢 |
| DOOR_STYLE_NAME | str | estilo aplicado (modificador "Door Style") | ausente = slab | 🟢 |
| hb_panel_type / IS_PREP_FOR_GLASS | str / bool | tipo de painel da porta; marcação de vidro | Vertical Grain / False | 🟢 |

### Caixa de gaveta (GeoNodeDrawerBox) — `types_closets.py:840-871`, `drawer_boxes_closets.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| hb_part_role | str | CLOSET_DRAWER_BOX | — | 🟢 |
| hb_drawer_index | int | casa com a frente | 0.. | 🟢 |
| hb_drawer_box_type | str | sistema resolvido | AVANTECH/.../NONE | 🟢 |
| hb_drawer_box_size | str | 'WOOD', 'NONE' ou 'H{mm} L{mm}' | — | 🟢 |
| Dim X / Dim Y / Dim Z / Material | float / Material | largura = vão − 1 in; prof./altura por sistema | mín. 2 in (wood) | 🟢 |

### Puxador / cabide / moldura (objetos gerados)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_CABINET_PULL, hb_part_role='PULL' | bool/str | instância de puxador (mesh compartilhada) | — `types_closets.py:1002-1004` | 🟢 |
| hb_pull_name | str | stem do modelo ("pricing keys on it") | ex. 'CLASSIC 96' `:1007` | 🟢 |
| IS_CLOSET_HANGER | bool | cabide filho do varão | 3 por varão `pulls_closets.py:225` | 🟢 |
| hb_hanger_model | str | override por cabide | ausente = padrão da sala | 🟢 |
| IS_CLOSET_MOLDING / PROFILE_NAME | bool / str | curva de coroa e perfil | `molding_closets.py:520-521` | 🟢 |

### Flags de classe do starter (`ClosetStarter` e subclasses) — `types_closets.py:212-231, 1449-1735`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| default_closet_type | str | BASE/TALL/HANGING/ISLAND (L: BASE/TALL/UPPER) | BASE | 🟢 |
| has_toe_kick / allows_toe_kick | bool | rodapé inicial / pode ter rodapé | True / True | 🟢 |
| floor_mounted | bool | vãos iniciais no piso | True (Hanging/L Upper: False) | 🟢 |
| has_countertop | bool | semeia tampo | Base, Island: True | 🟢 |
| has_applied_back | bool | fundo aplicado por vão | Island: True; Double: False | 🟢 |
| is_double | bool | ilha dupla face | Double: True | 🟢 |
| has_hang_rail | bool | trilho de parede | True; ilhas: False | 🟢 |
| ctop_overhang_all | bool | balanço do tampo em todos os lados | Double: True | 🟢 |
| default_depth | float/None | profundidade própria | Double 30 in; L 24 in | 🟢 |
| is_corner | bool | unidade de canto L | L: True | 🟢 |

### Spec do solver (entrada) — `types_closets.py:434-456`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| width, height | float | W e H do starter | — | 🟢 |
| pt, st | float | espessuras painel/prateleira | 19,05 mm | 🟢 |
| kick_height, kick_setback | float | rodapé (setback não usado no solver) | — | 🟢 |
| bays[] | list[dict] | width, locked, height, depth, floor, remove_bottom, remove_cleat | — | 🟢 |

### Layout do solver (saída) — `solver_closets.py:63-126`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| widths[] | list[float] | larguras finais por vão | ≥ 1 in (destravado) | 🟢 |
| panels[].x/z/length/depth | float | borda esquerda, base, comprimento vertical, profundidade | — | 🟢 |
| bays[].x/z0/width/height/depth | float | envelope do vão | — | 🟢 |
| bays[].kick/floor | float/bool | rodapé efetivo, montagem | — | 🟢 |
| bays[].bottom_z/top_z/cleat_z/interior_z/interior_h | float | cotas locais (faces inferiores das prateleiras) | interior_h ≥ 0,25 in | 🟢 |

### Tabelas de sistema de caixa — `drawer_boxes_closets.py:30-53`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| _AVANTECH_HEIGHTS | list[(h, min_abertura)] | 251/187/139/101 mm; abertura ≥ h+5 mm | maior primeiro | 🟢 |
| _METABOX_HEIGHTS | list[(h, min_abertura)] | 150/118/86/54 mm → 174/142/110/78 mm | maior primeiro | 🟢 |
| _SLIDE_LENGTHS | list[float] | 550/500/450/400/350/270 mm | menor = fallback | 🟢 |
| _BATTERY_CLEARANCE | float | reserva Illumination | 12,7 mm | 🟢 |
| _BOX_MATERIALS | dict | Storm Silver Gray / Metabox White | — | 🟢 |

### Especificação de estilo de frente — `fronts_closets.py:46-69`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| _SPECS[estilo] | (stile, rail porta, rail gaveta, miter) em in | Narrow 2,25; Wide 3; Contemporary/Combination 2,5/3/2 | — | 🟢 |
| _MIN_SIZES[estilo] | (altura, largura) em in | abaixo disso vira slab | ex. Wide 9,5×9,5 | 🟢 |
| _PANEL_THICKNESS / _PANEL_INSET | float | painel central | 1/4 in / 1/2 in | 🟢 |
| hb_wrap_version (node group) | int | versão do wrapper 'Closet Door Style' | 2 | 🟢 |

### Estado do overlay / grab (UI) — `gpu_overlay_closets.py:66-157`, `op_grab_closet.py:55-59, 124-253`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| scene['hb_ov_show_dims'] | int | 1 Todos / 2 Seleção / 0 Off | 1 | 🟢 |
| scene['hb_ov_show_mount'] | int | pílula Bottoms | 1 | 🟢 |
| rótulo (tupla) | (obj_name, kind, editable, locked, rect, text) | kinds: STARTER_W/H/D, BAY_W/H/D, OPEN_H, PART_Z, DRAWER_H, TOGGLE_LOCK/BOTTOM | — | 🟢 |
| _edit | dict | name, kind, typed, owner durante edição | None | 🟢 |
| boundary (grab) | dict | kind (END_L/END_R/TOP/PANEL/BAY_TOP/BAY_BOT/SHELF), root, bay, shelf, left/right, side, p0, p1, axis | — | 🟢 |
| _enabled / _hover / _drag_op | bool / dict / Operator | estado global do grab | False/None/None | 🟢 |

### Clipboard de copiar/colar — `types_closets.py:1958-2021`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| opening.adj / drawer_qty / drawer_fh | int/int/float | conteúdo da abertura | 0 / 0 / 7,5 in | 🟢 |
| opening.door_swing / is_hamper | str / int | portas | '' / 0 | 🟢 |
| opening.cubby_cols / cubby_rows | int | nichos | 1 / 1 | 🟢 |
| opening.rods | list[float] | offsets dos varões | [] | 🟢 |
| bay.remove_bottom / remove_cleat | bool | flags do vão | False | 🟢 |
| bay.bay_door_swing / bay_is_hamper | str / int | portas do vão | '' / 0 | 🟢 |
| bay.shelves | list[float] | offsets das divisoras (lado FRONT) | [] | 🟢 |
| bay.openings | list[dict] | conteúdos por abertura FRONT | — | 🟢 |

---

## product_common

> Dicionário de dados do módulo legado `product_common` (fork HB5). Caminhos relativos a `blendertomob/`.
> Medidas internas em **metros**; valores-padrão expressos em polegadas (") quando o código usa `inch()`.
> Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

### DoorStyleInfo (dict) — `door_builder.DOOR_STYLE_FALLBACK` / `door_style_info()` (`door_builder.py:36-95`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| door_type | str | Construção da porta | `'5_PIECE'` \| `'SLAB'`; padrão `'5_PIECE'` | 🟢 |
| stile_width | float (m) | Largura uniforme dos montantes | 3"; piso efetivo 1/2" | 🟢 |
| rail_width | float (m) | Largura uniforme das travessas | 3"; piso 1/2" | 🟢 |
| add_mid_rail | bool | Trilho do meio legado (único) | False | 🟢 |
| center_mid_rail | bool | Centraliza o trilho do meio | True | 🟢 |
| mid_rail_width | float (m) | Largura do trilho do meio | 3"; piso 1/2" | 🟢 |
| mid_rail_location | float (m) | Borda inferior do trilho quando não centralizado (a partir da base) | 12"; piso = bottom_rail | 🟢 |
| panel_thickness | float (m) | Espessura do painel | 1/2"; piso 1/8" | 🟢 |
| panel_inset | float (m) | Recuo da face do painel em relação à face da porta | 1/4"; piso 0 | 🟢 |
| mid_rail_count | int | Nº de trilhos do meio equidistantes (vence add_mid_rail) | 0; piso 0 | 🟢 |
| mid_stile_count | int | Nº de montantes do meio equidistantes | 0; piso 0 | 🟢 |
| left_stile_width / right_stile_width | float \| None | Override por lado | None → stile_width; 0.0 honrado (sem membro) | 🟢 |
| top_rail_width / bottom_rail_width | float \| None | Override por lado | None → rail_width; piso 0.0 | 🟢 |
| mid_stile_width | float \| None | Largura dos mid stiles | None → stile_width | 🟢 |
| mid_rail_z | (float, float) \| None | Linha de centro explícita (coef, offset) contra H | None; vence add_mid_rail quando count=0 | 🟢 |

### DoorPart (dict) — saída de `door_layout()` / `evaluate_layout()` (`door_builder.py:113-227`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| key | str | Tipo da peça | `slab`, `left_stile`, `right_stile`, `top_rail`, `bottom_rail`, `mid_rail`, `mid_stile`, `panel` | 🟢 |
| name | str | Nome de exibição | ex.: "Left Stile", "Mid Rail 2", "Mid Stile 1-2", "Panel 2-1" | 🟢 |
| x, w | (coef, offset) | Posição/largura lineares em W | valor = coef·W + offset | 🟢 |
| z, h | (coef, offset) | Posição/altura lineares em H | idem contra H | 🟢 |
| thickness | float \| None | None = espessura da porta; float para o painel | painel: max(panel_thickness, 1/8") | 🟢 |
| y_inset | float | Recuo da face da peça em relação à face da porta | 0 (quadro); panel_inset (painel) | 🟢 |
| x0, x1, z0, z1 | float (m) | Retângulo absoluto (só `evaluate_layout`) | local da porta: x a partir da esquerda, z a partir da base | 🟢 |

### Parâmetros de `build_door_mesh` (`door_builder.py:1202-1248`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| mesh | bpy.types.Mesh | Malha substituída | obrigatório | 🟢 |
| info | DoorStyleInfo | Construção | obrigatório | 🟢 |
| width, height, thickness | float (m) | Dimensões da frente | obrigatórios | 🟢 |
| materials | (Material, Material, Material) \| None | (stile, rail, panel) | None = só índices | 🟢 |
| outer_section | list[(u, v)] \| None | Perfil de borda externa | None = borda reta | 🟢 |
| inner_section / inner_rail_section / inner_stile_section | laço fechado [(u, v)] \| None | Sticking aplicado (único ou separado rail/stile) | fallback cruzado | 🟢 |
| panel_section | dict(points, field_u) \| None | Raise do painel | None = painel plano | 🟢 |
| member_section | list[(u, v)] \| None | Perfil de membro (MITERED) | None = FRAMED | 🟢 |
| applied_section | laço fechado \| None | Moldura aplicada | None | 🟢 |
| applied_scope | str | Abrangência da moldura aplicada | `'ALL'` \| `'RAILS'`; padrão `'ALL'` | 🟢 |
| panel_grooves | dict(style, spacing) \| None | Ranhuras no painel plano | style `BEAD`\|`KERF`; spacing (m) > 0 | 🟢 |
| mullion | dict(pattern, bar_width, depth) \| None | Barras sobre vidro | pattern padrão `GRID`; bar_width 7/8"; depth > 1e-6 | 🟢 |
| shape | dict(curve, double, twin, rise) \| None | Arco na borda da abertura | curve `ARCH`\|`CROWN`; rise = teto (m) | 🟢 |

### ShapeSpec / MullionSpec / GrooveSpec (derivados de catálogo)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| shape.curve | str | Família da curva | ARCH: rise = min(0.20·w, 2.25"); CROWN: min(0.16·w, 1.75") | 🟢 |
| shape.double | bool | Arco também na base | False | 🟢 |
| shape.twin | bool | Força 1 mid stile (tratado no consumidor) | False | 🟢 |
| mullion.pattern | str | GRID, MISSION, PRAIRIE, X, GOTHIC, DBL_GOTHIC, DBL_BOW, INTERLOKEN | GRID | 🟢 |
| grooves.style | str | BEAD (quirk 1/16", raio 0.09", prof. 0.11") ou KERF (1/8"×3/32") | BEAD | 🟢 |
| grooves.spacing | float (m) | Passo entre ranhuras | catálogo: 1.6", 2.0", 3.0" | 🟢 |

### ProfileData (dict) — `load_profile()` / `profile_from_object()` (`door_profiles.py:85-150`, `:490-522`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| points | list[(float, float)] | Polilinha no plano do desenho (transform aplicado, duplicados removidos) | ≥ 2 pontos | 🟢 |
| cyclic | bool | Spline fechada | — | 🟢 |
| name | str | Nome do arquivo (stem) ou do objeto | — | 🟢 |
| category | str \| None | OUTER/INNER/PANEL/APPLIED/MITERED; None para objeto da cena | — | 🟢 |

### PanelSection (dict) — `panel_profile_section()` (`door_profiles.py:271-372`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| points | list[(u, v)] | u para dentro a partir da borda do painel; v atrás do plano do campo; ponta do campo primeiro | v escalado para ≤ max_depth | 🟢 |
| field_u | float | u do ponto do campo (largura do raise) | = points[0][0] | 🟢 |

### Cache de perfis — `door_profiles._cache` (`door_profiles.py:39`, `:101-103`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| chave | (path: str, mtime: float, res: int) | Identidade do perfil amostrado | invalida ao editar o .blend | 🟢 |
| valor | ProfileData | Resultado de load_profile | sem limite de tamanho | 🟢 |

### Appliance (classe `GeoNodeCage`) — `types_appliances.py:8-51`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| width / height / depth | float (m, atributo de classe) | Dimensões padrão → Dim X / Dim Z / Dim Y | base 30"×36"×24" | 🟢 |
| variable_width | bool | Permite override de largura na colocação | False (True: Range, Hood) | 🟢 |
| obj['IS_APPLIANCE'] | ID prop bool | Marca de eletrodoméstico | True | 🟢 |
| obj['APPLIANCE_TYPE'] | ID prop str | Tipo | RANGE, COOKTOP, WALL_OVEN, DISHWASHER, REFRIGERATOR, MICROWAVE, HOOD, SINK, WASHING_MACHINE, DRYER | 🟢 |
| obj['MENU_ID'] | ID prop str | Menu de contexto | `HOME_BUILDER_MT_appliance_commands` | 🟢 |
| obj['IS_COUNTERTOP_APPLIANCE'] | ID prop bool | Instalado no tampo | Cooktop, Sink | 🟢 |
| Mirror Y | input GN bool | Espelha Y | True | 🟢 |
| filho "Appliance Text" | GeoNodeText | Rótulo = APPLIANCE_TYPE, `IS_APPLIANCE_TEXT`, drivers no centro da face frontal | tamanho = `scene.home_builder.annotation_text_size` | 🟢 |

### Subtipos de Appliance (`types_appliances.py:54-220`)

| Classe | APPLIANCE_TYPE | L×A×P padrão | Propriedades (add_property) | Confiança |
|---|---|---|---|---|
| Range | RANGE | 30×36×25" | Has Hood (CHECKBOX, False), Hood Height (DISTANCE, 24") | 🟢 |
| Cooktop | COOKTOP | 30×4×21" | — (IS_COUNTERTOP_APPLIANCE) | 🟢 |
| WallOven | WALL_OVEN | 30×29×24" | Is Double Oven (CHECKBOX); `set_double_oven` → 51"/29" | 🟢 |
| Dishwasher | DISHWASHER | 24×34×24" | Panel Ready (CHECKBOX, False) | 🟢 |
| Refrigerator | REFRIGERATOR | 36×70×30" | Counter Depth (False), Has Water Line (True), Panel Ready (False); `set_counter_depth` → 24"/30" | 🟢 |
| Microwave | MICROWAVE | 24×12×14" | Over Range, Built In (False); `set_over_range` → 30×17×16" | 🟢 |
| Hood | HOOD | 30×6×20" | Hood Style (TEXT 'Under Cabinet' — **não criada**), CFM Rating (QUANTITY 400) | 🟢 |
| Sink | SINK | 33×10×22" | Sink Type (TEXT 'Double Bowl' — **não criada**), Undermount (True) | 🟢 |
| WashingMachine | WASHING_MACHINE | 27×38×30" | Front Load (True) | 🟢 |
| Dryer | DRYER | 27×38×30" | Front Load (True), Gas (False) | 🟢 |

### Wood hood cage (objeto HOOD) — ID props (`wood_hoods.py:29-38`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| WOOD_HOOD_STYLE | str | Último estilo construído | um de `WOOD_HOOD_STYLE_ITEMS` | 🟢 |
| WOOD_HOOD_CUSTOM_OPTS | dict (IDProperty) | Opções do estilo CUSTOM (ver tabela abaixo) | ausente = defaults | 🟢 |
| STYLE_NAME | str | Estilo de armário atribuído (acabamento/portas) | opcional; fallback estilo ativo | 🟢 |
| Dim X / Dim Y / Dim Z | inputs GN | Largura / profundidade / altura da coifa | — | 🟢 |

### Wood hood part — ID props (`wood_hoods.py:91-97`, `:279-294`, `:1635-1685`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| IS_WOOD_HOOD_PART | bool | Marca de peça gerada (apagada no rebuild) | True | 🟢 |
| MENU_ID | str | `HOME_BUILDER_MT_face_frame_part_commands` | — | 🟢 |
| IS_MANUAL_PART | bool | Peça tornada editável (preservada no rebuild) | definida por Make Editable | 🟢 |
| HOOD_PARAMETRIC_SNAPSHOT | str (JSON) | Receita para reverter | ver HoodSnapshot | 🟢 |
| hb_part_role | str | `INSET_PANEL` para painéis inset | opcional | 🟢 |

### HoodCustomOptions — `_CUSTOM_DEFAULTS` (`wood_hoods.py:365-396`) + operador de prompts (`:1836-1958`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| angle_front | bool | Inclina a frente até top_depth | False | 🟢 |
| top_depth | float (m) | Profundidade no topo | 12"; clamp [1", D] | 🟢 |
| angle_sides | bool | Afunila as laterais até top_width | False | 🟢 |
| top_width | float (m) | Largura no topo | 24" (1ª abertura: W/2); clamp [2·3/4"+2", W] | 🟢 |
| top_height | float (m) | Trecho reto no topo | 0; min 0; clamp ≤ H − banda − 1" | 🟢 |
| include_mantle | bool | Banda projetada na base | False | 🟢 |
| mantle_height | float (m) | Altura da banda | 6" | 🟢 |
| mantle_depth | float (m) | Profundidade frente-trás do mantle | 2.75"; assembly só se > 1/8" (inclinada) | 🟢 |
| include_mantle_molding | bool | Frisos no topo/base do mantle | False | 🟢 |
| mantle_molding_width | float (m) | Altura do friso | 1.5"; clamp [1/4", banda] | 🟢 |
| mantle_molding_thickness | float (m) | Saliência do friso | 3/4"; piso 1/8" | 🟢 |
| fan_cutout_width | float (m) | Largura do recorte do exaustor | 30"; ≤ W − 1.5" − 2" | 🟢 |
| fan_cutout_depth | float (m) | Profundidade do recorte | 12"; ≤ interior − 2" | 🟢 |
| fan_cutout_offset | float (m) | Desloca para frente (+) / parede (−) | 0; clamp ±slack | 🟢 |
| floor_height | float (m) | Eleva a prateleira liner | 0; min 0; ≤ H − 2" | 🟢 |
| include_front_panel | bool | Quadro frontal com baias | False | 🟢 |
| panel_stile_width | float (m) | Montantes do quadro e paneled ends | 2.5"; piso 1/2" | 🟢 |
| panel_top_rail_width | float (m) | Travessa superior | 2.5"; piso 1/2" | 🟢 |
| panel_bottom_rail_width | float (m) | Travessa inferior | 2.5"; piso 1/2" | 🟢 |
| panel_count | int | Baias; mid stiles = n − 1 | 2; UI 1..10; piso 1 | 🟢 |
| bay_fronts | list[str] | Frente por baia | 10 slots; PANEL \| OVERLAY_DOOR \| INSET_DOOR; inválido → PANEL | 🟢 |
| left_end_panel / right_end_panel | bool | Paneled end substitui a lateral | False | 🟢 |
| left_end_front / right_end_front | str | Frente do paneled end | 'PANEL' | 🟢 |
| door_mid_rails | int | Trilhos do meio em toda porta da coifa | 0; UI 0..6 (0 = regra do estilo) | 🟢 |
| door_mid_stiles | int | Montantes do meio em toda porta | 0; UI 0..6 | 🟢 |
| include_shiplap | bool | Shiplap envolvendo a coifa | False | 🟢 |
| shiplap_board_width | float (m) | Largura do curso | 6"; UI enum '4'/'5'/'6'; piso 1" | 🟢 |
| panel_rail_width (legado) | float (m) | Largura única antiga das travessas | migrada p/ top/bottom | 🟢 |

### HoodSnapshot (JSON) — `snapshot_hood_part()` (`wood_hoods.py:1635-1685`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| mod_name | str | Nome do modificador GN da peça | de `home_builder.mod_name` | 🟢 |
| node_group | str | Nome do node group | precisa existir em `bpy.data.node_groups` no restore | 🟢 |
| inputs | dict[identifier → valor] | Inputs não-geometria serializados | Material/Object → `{'__idtype__', 'name'}`; vetores → lista | 🟢 |
| drivers | list[{data_path, array_index, expression, variables[{name, data_path}]}] | Drivers da peça | variáveis SINGLE_PROP, alvo re-apontado ao cage | 🟢 |
| location / rotation_euler / scale | list[float] | Transform | — | 🟢 |

### _FrontProfile (classe interna) — `wood_hoods.py:1082-1157`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| W, D, H | float (m) | Dimensões do cage | — | 🟢 |
| td | float | Profundidade no topo | None → D | 🟢 |
| side_in | float | Recuo lateral no topo (afunilamento por lado) | 0 | 🟢 |
| z0b | float | Fim do trecho reto inferior | clamp [0, H − 1"] | 🟢 |
| zb | float | Início do trecho reto superior | clamp [z0b + 1", H] | 🟢 |
| dy, span, ln, S | float | D − td; zb − z0b; hipotenusa inclinada; comprimento total de face | ln ≥ 1 fallback se 0 | 🟢 |

### Operadores de coifa (`wood_hoods.py:1773-2226`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| blendertomob.build_wood_hood.style | EnumProperty | Estilo | 14 itens; 'BOX' | 🟢 |
| blendertomob.wood_hood_prompts.width/height/depth | FloatProperty LENGTH | Dimensões enviadas ao cage | precisão 5 | 🟢 |
| blendertomob.wood_hood_prompts.style | EnumProperty | Estilo | 'BOX' | 🟢 |
| blendertomob.wood_hood_prompts.ui_tab | EnumProperty | Aba do diálogo (não persistida) | SHAPE, MANTLE, FRONT, ENDS, LINER | 🟢 |
| blendertomob.wood_hood_prompts.bay_front_1..10 | EnumProperty (anotação dinâmica) | Frente por baia | 'PANEL' | 🟢 |

### AccessoryItem (dict de provider) — `accessory_registry.py:1-8`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| code | str | Código de catálogo (único entre hosts) | obrigatório | 🟢 |
| name | str | Nome | obrigatório | 🟢 |
| category | str | Categoria para filtros | opcional | 🟢 |
| min_opening_w | float | Largura mínima da abertura (exibida em polegadas) | opcional | 🟢 |
| section | str | Seção do menu hierárquico | opcional | 🟢 |
| group | str | Grupo dentro da seção | opcional | 🟢 |
| host | str | Chave do host (injetada por `all_items`) | setdefault | 🟢 |

### AccessoryRegistry — `_providers` (`accessory_registry.py:11`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| chave | str (host) | Ponto de montagem (ex.: `opening_interior_pullout`, `door_mounted`, `drawer_accessory`, `blind_corner_hardware`…) | registro sobrescreve | 🟢 |
| valor | Callable[[], Iterable[dict]] | Provider sem argumentos | falha → [] | 🟢 |

### ApplianceSpecProvider — `appliance_spec_registry._provider` (`appliance_spec_registry.py:1-32`)

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| manufacturers() | → list[str] | Fabricantes | — | 🟢 |
| models(manufacturer) | → list[{model, series, appliance_type}] | Modelos | — | 🟢 |
| resolve(manufacturer, model) | → dict spec | Especificação | — | 🟢 |
| spec.operator_config | str | Configuração do operador de painéis | opcional | 🟢 |
| spec.operator_panel_type | str | Tipo de painel | 'A' \| 'B' \| 'C' | 🟢 |
| spec.appliance_dim_x_m | float (m) | Largura do eletrodoméstico → Dim X | opcional | 🟢 |
| spec.weight_max_lb | float (lb) | Peso máximo do painel | exibido na UI | 🟢 |
| spec.panels | ? | Definição dos painéis | formato não observado | 🔴 |
| spec.flags | list[str] | Avisos exibidos | opcional | 🟢 |
| spec.manufacturer / source_url | str | Metadados (gravados em `APPLIANCE_PANEL_SPEC`) | opcional | 🟢 |

---

## catalog_molding

> Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

### CatalogEntry (dict em `catalog/catalog_data.CATALOG`) — `catalog/catalog_data.py:45-75`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `id` | str | Identificador único derivado de categoria + nome sanitizado; também nome do thumbnail `{id}.png` | gerado por `_e` (R01); 78 ids únicos | 🟢 |
| `code` | str | Código de catálogo do fabricante | sempre `''` hoje | 🟢 |
| `name` | str | Nome exibido | obrigatório | 🟢 |
| `description` | str | Descrição (quebrada em 40 col. no detalhe) | obrigatório em `_e` | 🟢 |
| `kind` | str | Tipo de item; define verbo/ícone | sempre `'product'`; UI prevê `'insert'`/`'option'` | 🟢 |
| `category` | str | Caminho de categoria (hierárquico com `/`) | `standard, corner, appliance, vanity, parts, specialty, angled, misc` | 🟢 |
| `tags` | list[str] | Tags livres | `[]`; não usadas na busca | 🟢 |
| `thumbnail` | str | Nome de arquivo override em `catalog/thumbnails/` | `''` | 🟢 |
| `action_operator` | str | `bl_idname` do operador de colocação (`mod.op`) | `hb_face_frame.draw_cabinet` ou `hb_catalog.not_yet_implemented` | 🟢 |
| `action_args` | dict | kwargs do operador | `{'cabinet_name', 'bay_qty'=1}` ou `{'item_name'}` | 🟢 |
| `catalog_page` | str/int | Página do catálogo impresso (exibida no detalhe) | nunca definido | 🟢 (lido em `ui_catalog.py:251-256`) |

### HBCatalogItem (PropertyGroup, espelho) — `catalog/props_catalog.py:31-42`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `item_id` | StringProperty | `CatalogEntry.id` (chave para `find_entry`) | `''` | 🟢 |
| `code` | StringProperty | cópia de `code` | `''` | 🟢 |
| `name` | StringProperty | cópia de `name` | `''` | 🟢 |
| `description` | StringProperty | cópia de `description` | `''` | 🟢 |
| `kind` | StringProperty | cópia de `kind` | `''` | 🟢 |
| `category` | StringProperty | cópia de `category` | `''` | 🟢 |

### HBCatalogState (PropertyGroup em `Scene.hb_catalog`) — `catalog/props_catalog.py:45-69,141`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `search` | StringProperty | Texto de busca (substring ou subsequência fuzzy) | `''` | 🟢 |
| `category` | EnumProperty (dinâmico) | Filtro de categoria; `'all'` = Everything + todos os prefixos | itens de `_category_items_cb` | 🟢 |
| `view_mode` | EnumProperty | `DEFAULT` (List) / `GRID` | `'DEFAULT'` | 🟢 |
| `items` | CollectionProperty(HBCatalogItem) | Espelho do `CATALOG` | sincronizado por timer/`load_post` | 🟢 |
| `active_index` | IntProperty | Índice selecionado no `UIList` | `-1` | 🟢 |

### Estado de módulo do catálogo

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `previews_catalog._pcoll` | `ImagePreviewCollection` \| None | Coleção de previews (chaves: nome de arquivo ou `__no_thumbnail__`) | criada em `register`, removida em `unregister` | 🟢 |
| `props_catalog._sync_pending` | bool | Coalescência de timers de sync | `False` | 🟢 |

### Operadores do catálogo — `catalog/ops_catalog.py`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `hb_catalog.activate_item.item_id` | StringProperty | Id da entrada a ativar | `''`; `bl_options={'REGISTER','UNDO'}` | 🟢 |
| `hb_catalog.not_yet_implemented.item_name` | StringProperty | Rótulo usado para mapear Upper/Tall/Base Door | `'(unnamed)'` | 🟢 |

### Home_Builder_Scene_Props — campos `molding_*` (em `Scene.home_builder`) — `hb_props.py:493-580`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `molding_crown_package` | EnumProperty dinâmico | `NONE`, `SIMPLE`, `STACKED`, `SPACER` | 1º item (`NONE`) 🟡; update → reaplica | 🟢 |
| `molding_base_package` | EnumProperty dinâmico | `NONE`, `SIMPLE` | idem | 🟢 |
| `molding_light_rail_package` | EnumProperty dinâmico | `NONE`, `SIMPLE` | idem | 🟢 |
| `molding_base_include_recessed` | BoolProperty | Moldura corre sobre rodapés recuados | `False` | 🟢 |
| `molding_crown_reveal` | FloatProperty (LENGTH) | Faixa exposta entre topo da porta e crown | `inch(0.625)`, min 0 | 🟢 |
| `molding_crown_stack_offset` | FloatProperty (LENGTH) | Altura da crown sobre o spacer (`STACK_OFFSET`) | `inch(3.5)`, min 0 | 🟢 |
| `molding_crown_furniture_cap` | BoolProperty | Liga o furniture cap | `False` | 🟢 |
| `molding_cap_offset` | FloatProperty (LENGTH) | Ajuste do cap sobre a moldura mais alta | `0.0`, soft ±`inch(6)` | 🟢 |
| `molding_crown_profile` | EnumProperty dinâmico | Override `Crown Molding` (`DEFAULT` + stems dos packs) | `DEFAULT` 🟡 | 🟢 |
| `molding_spacer_profile` | EnumProperty dinâmico | Override `Spacer` | `DEFAULT` 🟡 | 🟢 |
| `molding_cap_profile` | EnumProperty dinâmico | Override `Furniture Caps` | `DEFAULT` 🟡 | 🟢 |
| `molding_base_profile` | EnumProperty dinâmico | Override `Base Molding` | `DEFAULT` 🟡 | 🟢 |
| `molding_base_shoe` | BoolProperty | Liga base shoe | `False` | 🟢 |
| `molding_light_rail_profile` | EnumProperty dinâmico | Override `Light Rail` | `DEFAULT` 🟡 | 🟢 |

### MoldingPackage (tupla em `packages.PACKAGES`) — `molding/packages.py:87-133`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `identifier` | str | Chave do enum | `SIMPLE`, `STACKED`, `SPACER` | 🟢 |
| `label` | str | Rótulo UI | — | 🟢 |
| `description` | str | Tooltip | — | 🟢 |
| `stack` | list[StackEntry] | Pilha de perfis | ≥ 1 entrada | 🟢 |

### StackEntry (tupla) — `molding/packages.py:1-15`, `molding/ops.py:46-72`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `profile_ref` | str | `"Categoria/Nome do Perfil"` no pack | categorias: `Crown Molding`, `Spacer`, `Furniture Caps`, `Base Molding`, `Light Rail` | 🟢 |
| `fallback_key` | str | Chave em `_PROFILE_OUTLINES` | `crown_simple`, `flat_stock`, `furniture_cap`, `base_simple`, `base_shoe`, `light_rail_simple` | 🟢 |
| `dx` | float \| `'STACK_FRONT'` | Offset frontal (m) do caminho | `0.0` | 🟢 |
| `dy` | float \| `'STACK_OFFSET'` | Offset vertical (m) | `0.0` | 🟢 |

### ProfileOutline (`packages._PROFILE_OUTLINES`) — `molding/packages.py:183-216`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| chave | str | `fallback_key` | 6 chaves | 🟢 |
| valor | list[(x, y)] | Contorno 2D fechado; +Y para cima, X negativo = para o armário | em metros via `units.inch` | 🟢 |

### Caches de `packages`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `_PROFILE_PATHS` | list[str] | Pastas raiz de packs registrados | vazio; nenhum chamador no repo | 🟢 |
| `_category_enum_cache` | dict[str, tuple] | Itens de enum por categoria | limpo ao (des)registrar pack | 🟢 |
| `_profile_height_cache` | dict[str, (top, depth)] | Métricas por `profile_ref` | idem | 🟢 |
| `_ENUM_CACHE` | dict[str, tuple] | Itens de enum de pacotes por tipo | construído no import | 🟢 |

### Facts (dict por `id(obj)`, `adapters.build_facts`) — `molding/adapters.py:163-230`, `molding/engine.py:7-17`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `role` | str | `'CABINET'` ou `'APPLIANCE'` | — | 🟢 |
| `corner` | dict \| None | `{'ld', 'rd', 'diagonal'}` para armário em L | None; ld/rd ausentes → 24" | 🟢 |
| `kick` | dict | `{'skip', 'setback', 'stile_left', 'stile_right', 'stile_left_w', 'stile_right_w'}` | `skip=False, setback=0` | 🟢 |
| `crown_mount` | dict \| None | `{'rail_width', 'door_overlay'}` (só face frame com TOP_RAIL) | None | 🟢 |
| `finished_left` / `finished_right` | bool | Lateral acabada (recebe retorno) | False para aparelhos | 🟢 |

### Terminal (dict interno do engine) — `molding/engine.py:305-344,486-527`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `obj` | Object | Membro extremo da cadeia | — | 🟢 |
| `side` | str | `'left'`/`'right'` — lado que fica na extremidade | — | 🟢 |
| `back` | Vector(2) | Canto traseiro dessa lateral (destino do retorno) | — | 🟢 |
| `front` | Vector(2) | Canto frontal (só em spans de rodapé) | — | 🟢 |

### Span (tupla do engine) — `molding/engine.py:395-422`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `points` | list[Vector(2)] | Polilinha em XY mundial (ou local antes da transformação) | ≥ 2 | 🟢 |
| `kind` | str | `'FRONT'`, `'RECESS'`, `'SKIP'` | — | 🟢 |

### Opts (dict de `apply_scene_packages`) — `molding/ops.py:260-277`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `include_recessed` | bool | de `molding_base_include_recessed` | False | 🟢 |
| `crown_reveal` | float | de `molding_crown_reveal` | 0.0 se ausente | 🟢 |
| `stack_offset` | float | de `molding_crown_stack_offset` | 0.0 se ausente | 🟢 |
| `cap_offset` | float | de `molding_cap_offset` | 0.0 | 🟢 |
| `crown_stack` | list \| None | Pilha crown ativa (para posicionar o cap) | None se `NONE` | 🟢 |
| `overrides` | dict[str, str\|None] | Override por categoria | None = DEFAULT | 🟢 |

### MoldingSweep (Object CURVE criado por `_spawn_sweep`) — `molding/ops.py:126-187`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | `"MoldingSweep"` (+ sufixo Blender) | — | 🟢 |
| `["IS_HB_MOLDING_SWEEP"]` | ID prop bool | Marca de sweep de pacote | True | 🟢 |
| `["HB_MOLDING_TYPE"]` | ID prop str | `CROWN`/`BASE`/`LIGHT_RAIL`/`CAP` | — | 🟢 |
| `["HB_MOLDING_MEMBERS"]` | ID prop str | Nomes dos membros da cadeia, separados por vírgula | — | 🟢 |
| `parent` | Object | Primeiro membro da cadeia | — | 🟢 |
| `location.z` | float | `_sweep_z` | — | 🟢 |
| `data.dimensions` / `bevel_mode` / `bevel_object` / `use_fill_caps` | Curve | `'2D'` / `'OBJECT'` / perfil / True | — | 🟢 |
| `data.splines[]` | BEZIER | Uma por segmento; handles `VECTOR`; `use_cyclic_u` para ilhas fechadas | ≥ 2 pts (3 se cíclica) | 🟢 |
| `data.materials[0]` | Material | Acabamento do 1º membro que resolver | opcional | 🟢 |

### MoldingProfile (Object oculto) — `molding/packages.py:219-230,327-347`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `name` | str | `Molding_Profile_<fallback_key>` (embutido) ou stem do `.blend` | — | 🟢 |
| `["IS_HB_MOLDING_PROFILE"]` | ID prop bool | Marca de perfil (limpeza) | True | 🟢 |
| `hide_viewport` / `hide_render` | bool | Oculto | True / True | 🟢 |
| `data` | Curve 2D POLY cíclica | Contorno do perfil | `fill_mode='NONE'` | 🟢 |
| `parent` | Object | O sweep | — | 🟢 |

### Operador de molduras — `molding/ops.py:310-319`

| Campo | Tipo | Descrição | Padrão/Limites | Confiança |
|---|---|---|---|---|
| `blendertomob.refresh_room_molding` | Operator | Reconstrói todas as molduras da cena; reporta nº de sweeps | `bl_options={'UNDO'}`, sem props | 🟢 |

---

