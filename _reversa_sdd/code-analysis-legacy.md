# Análise de Código — Camada Legada (Home Builder 5) — BlenderToMob

> Gerado pelo **Archaeologist** (Reversa) em 2026-09-29, nível **detalhado**.
> Complementa [`code-analysis.md`](code-analysis.md), que cobre a camada moderna `btm_*` (`data`, `geometry`,
> `operators`, `overlays`, `ui`, `cutting`). Motivação: lacuna **L3** de [`soul.md`](soul.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Evidências no formato `blendertomob/<arquivo>.py:<linha>`.

## Escopo e números

| Módulo (unit) | Caminho | Funções | Entidades | Regras | Complexidade |
|---------------|---------|--------:|----------:|-------:|--------------|
| `hb_core` | `hb_types.py`, `hb_props.py`, `hb_utils.py`, `hb_driver_functions.py`, `hb_project.py`, `hb_props_obstacles.py`, `units.py`, `ops.py` | 51 | 14 | 41 | alta |
| `hb_placement` | `hb_placement.py`, `hb_snap.py`, `hb_gpu_draw.py` | 33 | 7 | 30 | alta |
| `hb_layouts` | `hb_layouts.py`, `hb_details.py`, `hb_detail_library.py`, `hb_assets.py` | 53 | 13 | 42 | alta |
| `frameless` | `product_libraries/frameless/` | 60 | 21 | 45 | alta |
| `face_frame` | `product_libraries/face_frame/` | 43 | 25 | 44 | alta |
| `closets` | `product_libraries/closets/` | 46 | 17 | 50 | alta |
| `product_common` | `product_libraries/common/`, `accessory_registry.py`, `appliance_spec_registry.py` | 85 | 17 | 49 | alta |
| `catalog_molding` | `catalog/`, `molding/` | 43 | 12 | 33 | alta |
| **Total** | ~110 mil linhas | **414** | **126** | **334** | |

Artefatos: este arquivo; [`data-dictionary-legacy.md`](data-dictionary-legacy.md); `.reversa/context/modules-legacy.json`;
`flowcharts/legacy-*.md` (8 por módulo + 40 por função); `<unit>/legacy-mapping.md` para cada unit acima.

## Achados transversais

### T1. Padrão americano em polegadas em todas as bibliotecas de produto 🟢
`frameless`, `face_frame`, `closets` e `product_common` assumem chapa de 3/4" (19,05 mm), fundo de mesma espessura
da caixa (frameless), inferior 34,5"×24", aéreo a 54" do piso, vão máximo 36"/42", catálogo CWP, ferragens Blum,
eletrodomésticos em tamanhos dos EUA. Internamente tudo é metro, mas as constantes nascem em polegadas. Não há noção
de chapa 2750×1830, MDF 15/18 mm nem fundo fino encaixado — conflito direto com a camada `btm_*` e com o
[`cutting`](cutting/) (ver D7 em `soul.md`).

### T2. Produção ausente na camada legada 🟢
Nenhum módulo legado gera lista de corte, furação/usinagem ou orçamento. `closets` tem a retícula do sistema 32 mm
apenas para encaixe (`19+n·32 mm`, furos `12,95+n·32 mm`). `show_machining` em `frameless` não tem efeito. Reforça a
lacuna **L1** de `soul.md`: o `cutting/part_extractor.py` também não lê os gabinetes legados.

### T3. Helpers de Geometry Nodes duplicados e divergentes 🟢
Toda a camada legada acessa inputs de GN via `hb_utils` (nenhum `mod["Socket_X"]`, exceto `ops.py:172-184`, que usa
`Socket_3/4/5` fixos). `hb_utils.set_gn_input(mod, identifier)` e `compat.set_gn_input(mod, input_name)` têm o mesmo
nome e **semântica diferente**, com caches separados (chave `id(node_group)`, reciclável 🟡). O CLAUDE.md exige
sincronia ou consolidação em `compat.py`.

### T4. Riscos Blender 5.x recorrentes 🟢
- `Material.use_nodes = True` (obsoleto desde 5.0, sem efeito): `hb_layouts.py`/`hb_details.py` (6×), `ops.py:386`,
  `materials_closets.py:121`, `props_hb_frameless.py:269`, `ops_snap_line.py:46`, `ops_library.py:227`.
- Escrita por `obj[...]` em propriedade `bpy.props`: `types_face_frame.py:7335` (`refrigerator_opening_height` fica no
  padrão de 62" em vez de 69").
- Enums dinâmicos sem cache das strings (face_frame, frameless, catalog) — `docs/rag/project/04_armadilhas.md`.
- `bpy.ops` dentro de callbacks `update=` (`props_closets.py:97-100`, `props_hb_frameless.py:455`).
- `register()` que engole exceções (closets, frameless, face_frame, molding, hb_core).
- Handlers/timers sem remoção em algum caminho: modal de escala (hb_core), mixins de posicionamento sem `cancel()`
  (hb_placement), `split_preview` (face_frame), timer "Open Door" (closets), timer do catálogo; `driver_namespace`
  (`IF/OR/AND`) nunca limpo.
- Operadores que alteram dados sem `bl_options={'UNDO'}` (ops_defaults, toggle_mode, draw_cabinet, to_do…).
- Dependência de janela/UI (`context.window`, `context.screen`) que falha em `--background`.

### T5. Código morto e stubs 🟢
- `catalog/` não é importado em `__init__.py`: 71 de 78 entradas são stubs; `hb_catalog.render_thumbnail` inexistente.
- `pc_prompts.*` chamados em `Calculator.draw` não existem.
- Pipeline Line Art/iso-freestyle de `hb_layouts` sem chamador; `TitleBlock.update` inoperante.
- `frameless`: cantos diagonais alto/aéreo só criam a gaiola; rodapé "Ladder" é placeholder; várias props sem efeito.
- `accessory_registry` / `appliance_spec_registry`: nenhum provider registrado.
- `add_property` não trata `'TEXT'` → "Hood Style" e "Sink Type" nunca criadas (`types_appliances.py:176,192`).

### T6. Três estratégias de parametrização coexistindo 🟢
1. **Drivers + Calculator** (`frameless`, `hb_core`): medidas por expressões de driver e divisão de "iguais".
2. **Solver Python sem drivers** (`closets`, `face_frame`): props → solver puro → inputs de GN, com guardas de
   reentrância; peças internas são apagadas e recriadas a cada recálculo (malhas órfãs 🟡).
3. **Geometria estática** (bancadas, crown, molduras): não acompanha o gabinete; exige "Refresh".

---

## Módulo hb_core

### Propósito

Núcleo da camada legada (fork do Home Builder 5). Define o **modelo de objetos paramétricos** baseado em Geometry Nodes:
cada peça, gaiola (cage), parede ou anotação é um objeto Blender com um modificador `NODES` cujo node group vem de um
`.blend` embarcado. As medidas são ligadas por **drivers** montados por uma pequena DSL (`Variable` + `driver_*`), e as
distribuições de vão ficam nas **calculadoras** (`Calculator`). O módulo também registra os PropertyGroups `home_builder`
(Object/Scene/WindowManager), os dados de projeto na "cena principal", o catálogo de obstáculos, a fachada de unidades e
operadores gerais de viewport/câmera/anotação. 🟢

### Arquivos

| Arquivo | Linhas | Papel |
|---|---|---|
| `blendertomob/hb_types.py` | 962 | `Variable`, `GeoNodeObject` e 11 subclasses, `CabinetPartModifier`, cache de identificadores GN, fixup de node group de cota |
| `blendertomob/hb_props.py` | 976 | `Calculator_Prompt`, `Calculator`, `Home_Builder_Object_Props`, `Home_Builder_Scene_Props`, `Home_Builder_Window_Manager_Props`, `HB_Wall_Editor_Props`, callbacks de update |
| `blendertomob/hb_utils.py` | 469 | Ponte GN 5.1/5.2, busca de base points, `run_calc_fix`, `add_driver_variables`, estado de vista |
| `blendertomob/hb_driver_functions.py` | 26 | `IF`, `OR`, `AND` para `driver_namespace` |
| `blendertomob/hb_project.py` | 319 | `Home_Builder_Project_Props`, cena principal, cenas de cômodo |
| `blendertomob/hb_props_obstacles.py` | 306 | Catálogo de 36 obstáculos + `Obstacles_Scene_Props` |
| `blendertomob/units.py` | 20 | Reexporta `data/units.py` |
| `blendertomob/ops.py` | 685 | 6 operadores gerais |

### Fluxo de controle

1. **Registro** 🟢 — `__init__.py:212-214` chama `hb_props.register()`, `hb_project.register()`,
   `hb_props_obstacles.register()`; cada um percorre `classes`, desregistra uma versão antiga se houver e registra de
   novo, engolindo qualquer exceção (`hb_props.py:955-966`, `hb_project.py:290-305`, `hb_props_obstacles.py:277-292`).
   Os `register()` classmethods dos PropertyGroups criam os `PointerProperty` em `bpy.types.*`. `ops.register()`
   (`ops.py:664-675`) segue o mesmo padrão. `__init__.py:249-256` injeta `IF/OR/AND` em `bpy.app.driver_namespace` e
   instala `load_file_post` (`@persistent`), que reinjeta as funções e chama `hb_project.ensure_main_scene()`
   (`__init__.py:58-73`).
2. **Criação de objeto** 🟢 — `GeoNodeObject.create(geo_node_name, name)` (`hb_types.py:79-97`): carrega o node group de
   `geometry_nodes/<nome>.blend` se ele não estiver em `bpy.data.node_groups`, cria mesh e objeto, adiciona o modificador
   `NODES`, grava `obj.home_builder.mod_name` e liga o objeto a `scene.collection`. `create_curve` (`:99-122`) faz o mesmo
   com uma curva POLY de 2 pontos (usada por cota e seta) e aplica `annotation_color` das preferências. As subclasses
   complementam com marcadores (ID custom props `IS_*`), aparência e valores padrão de inputs.
3. **Leitura/escrita de inputs GN** 🟢 — `set_input`/`get_input` (`hb_types.py:325-390`) validam modificador e node group,
   resolvem o identificador do socket pelo nome com cache, delegam a `hb_utils.set_gn_input/get_gn_input`
   (`hb_utils.py:16-28`), que escolhe entre `mod.properties.inputs.<id>.value` (≥ 5.2) e `mod[id]` (< 5.2); com falha,
   invalidam o cache e tentam de novo; depois chamam `obj.update_tag()`. Fluxograma:
   `flowcharts/legacy-hb_core-set_input.md`.
4. **Drivers** 🟢 — `var_input`/`var_prop`/`var_location`/`var_rotation`/`var_hide` criam `Variable(obj, data_path, name)`
   (`hb_types.py:167-209`); `driver_input`/`driver_prop`/`driver_location`/`driver_rotation`/`driver_hide`
   (`:211-287`) chamam `driver_add`, adicionam variáveis `SINGLE_PROP` (`hb_utils.py:299-305`) e definem a expressão.
   `Calculator_Prompt.get_var` (`hb_props.py:238-240`) expõe o valor de um prompt como variável pelo caminho
   `home_builder.calculators["C"].prompts["P"].distance_value`.
5. **Calculadoras** 🟢 — `Home_Builder_Object_Props.add_calculator` (`hb_props.py:376-380`) cria uma `Calculator` ligada
   a um `distance_obj` (empty filho); `set_total_distance` põe um driver em `distance_obj.home_builder.calculator_distance`;
   `calculate` (`hb_props.py:294-320`) distribui o total. Fluxograma: `flowcharts/legacy-hb_core-calculator_calculate.md`.
6. **Forçar reavaliação** 🟢 — `run_calc_fix`/`run_calc_fix_until_stable` (`hb_utils.py:190-297`). Fluxograma:
   `flowcharts/legacy-hb_core-run_calc_fix.md`.
7. **Paredes** 🟢 — `GeoNodeWall.create` (`hb_types.py:444-466`) cria o empty `obj_x` com driver `location.x = Length`;
   `connect_to_wall` (`:480-484`) põe `COPY_LOCATION` para o `obj_x` da parede anterior; `get_connected_wall`
   (`:486-561`) acha vizinhos. Fluxograma: `flowcharts/legacy-hb_core-get_connected_wall.md`.
8. **Cotas** 🟢 — `GeoNodeDimension.create` (`hb_types.py:714-730`) aplica o fixup `ensure_dimension_text_offset_basis`
   (`:632-687`), marca `IS_2D_ANNOTATION`/`IS_DIMENSION`, `MENU_ID` e copia tamanhos das props de anotação da cena;
   `set_decimal` (`:732-798`) ajusta as casas decimais. Fluxograma: `flowcharts/legacy-hb_core-set_decimal.md`.
9. **Projeto** 🟢 — `get_main_scene` → `ensure_main_scene` → `get_project_props` (`hb_project.py:143-217`).
10. **Obstáculos** 🟢 — enum dinâmico `get_obstacle_items` → `update_obstacle_type` → `draw_obstacle_ui` →
    operador `home_builder_obstacles.place_obstacle` (definido em `operators/ops_obstacles.py:73`).
11. **Operadores** 🟢 — `set_scale_with_two_points` (`ops.py:542-652`) é modal: `execute` adiciona o draw handler
    `POST_PIXEL` e o modal handler; `modal` trata `MOUSEMOVE`, `LEFTMOUSE` (2 cliques), repassa navegação e cancela com
    `RIGHTMOUSE`/`ESC`; `cleanup` remove o handler nas duas saídas.

**Tratamento de erros** 🟢 — A API `GeoNodeObject` levanta `ValueError` com mensagens explícitas (`hb_types.py:181-193`,
`254-267`, `302-314`, `336-345`, `373-382`, `883-890`, `903-904`, `924-928`, `950-954`); `has_input`/`has_modifier`
(`:392-428`) são as guardas sem exceção. Os registradores engolem todas as exceções. `get_main_scene` engole
`AttributeError` ao marcar a cena em contexto de desenho (`hb_project.py:170-174`). `migrate_project_data` registra via
`print` as chaves que não consegue copiar (`hb_project.py:259-262`).

### Algoritmos e regras

| ID | Regra | Local | Conf. |
|---|---|---|---|
| HB_CORE-R01 | Node group só é carregado do `.blend` se não existir em `bpy.data.node_groups` (reutilização por nome; um grupo local homônimo tem precedência) | `hb_types.py:81-86,103-108` | 🟢 |
| HB_CORE-R02 | Todo objeto GeoNode guarda o nome do seu modificador principal em `obj.home_builder.mod_name` e é ligado à coleção raiz da cena ativa | `hb_types.py:95-97,119-122` | 🟢 |
| HB_CORE-R03 | Identificador de socket resolvido por nome, com cache por `id(node_group)`; em caso de `KeyError`/`AttributeError`, o cache é invalidado e há uma única nova tentativa | `hb_types.py:24-50,347-355,384-390,930-936` | 🟢 |
| HB_CORE-R04 | Após escrever um input, `obj.update_tag()` garante a reavaliação no depsgraph | `hb_types.py:356-360,937-939` | 🟢 |
| HB_CORE-R05 | Acessos a inputs validam, nesta ordem: `mod_name` → modificador → node group → input; qualquer falha gera `ValueError` | `hb_types.py:181-193` (e repetições) | 🟢 |
| HB_CORE-R06 | `driver_hide` aplica a mesma expressão a `hide_viewport` e `hide_render`; `CabinetPartModifier.driver_hide` aciona `show_viewport`/`show_render` do modificador, então a expressão deve ser invertida (visível = verdadeiro) | `hb_types.py:235-241,897-912` | 🟢 |
| HB_CORE-R07 | Paredes encadeiam-se por `COPY_LOCATION` para o empty `obj_x` da anterior; `obj_x.location.x` é dirigido por `Length`, com Y/Z e rotação travados | `hb_types.py:452-466,480-484` | 🟢 |
| HB_CORE-R08 | Vizinho à esquerda = pai do alvo da restrição; à direita = parede cuja restrição aponta para o meu `obj_x`; fallback geométrico opcional com extremos em XY do mundo e tolerância de 0,01 m | `hb_types.py:486-561` | 🟢 |
| HB_CORE-R09 | Gaiola (cage): `WIRE`, cor preta, sem sombra, invisível a câmera e sombra, `hide_render=True`, marcador `IS_GEONODE_CAGE` | `hb_types.py:565-576` | 🟢 |
| HB_CORE-R10 | Padrões de fábrica: Rectangle `Dim X/Y`=1 m e `Line Thickness`=1 mm; DrawerBox espessura 0,5", fundo 0,25", Z do fundo 0,5"; DoorSwing espessura da porta 1,5"; Arrow altura 0,25", comprimento 0,5", `Show Arrow`=True e espessura da linha = da cota | `hb_types.py:584-586,618-620,629,833-840` | 🟢 |
| HB_CORE-R11 | `Unit Type` da cota: `METRIC`+MM=2, CM=3, M=4, outra métrica=3; demais sistemas=0 (polegadas); 1 (pés) nunca é produzido | `hb_types.py:692-712` | 🟢 |
| HB_CORE-R12 | Casas decimais da cota: valor encaixado no incremento da unidade (in 1 ou 1/16; ft 1/12 ou 1/192; mm 10 ou 1; cm 1 ou 0,1; m 0,01 ou 0,001), zeros à direita removidos; resultado inteiro (±0,001) → 0 decimais | `hb_types.py:732-798` | 🟢 |
| HB_CORE-R13 | Fixup idempotente do node group `GeoNodeDimension`: se o nó `Text X Tangent Rotate` não existe e todos os nós-âncora existem, o offset X do texto é religado para seguir a tangente da curva | `hb_types.py:632-687` | 🟢 |
| HB_CORE-R14 | `CabinetPartModifier.get_node` reutiliza o node group pelo nome ou carrega `CabinetPartModifiers/<token>.blend`; retorna `None` se o arquivo não existir (o modificador é criado sem grupo) | `hb_types.py:848-870` | 🟢 |
| HB_CORE-R15 | Calculadora: prompts "igual" e incluídos recebem `(total − Σ fixos incluídos) / nº iguais incluídos`; "igual" excluído = 0; sem prompts "igual" não há recálculo; sem proteção contra negativo | `hb_props.py:294-320` | 🟢 |
| HB_CORE-R16 | O total da calculadora é um driver em `distance_obj.home_builder.calculator_distance` | `hb_props.py:253-257` | 🟢 |
| HB_CORE-R17 | Tipos de prompt de objeto (`add_property`): CHECKBOX, DISTANCE, ANGLE, PERCENTAGE (0–100), QUANTITY (min 0), COMBOBOX (itens `(s,s,s)`); todos marcados com `description='HOME_BUILDER_PROP'` e guardados como ID custom property | `hb_props.py:335-374` | 🟢 |
| HB_CORE-R18 | Mudar `ceiling_height` recalcula, para frameless e face frame: `tall = pé-direito − folga superior` e `upper = pé-direito − folga superior − altura do armário de parede` | `hb_props.py:78-100` | 🟢 |
| HB_CORE-R19 | Mudar `wall_material` aplica o material aos inputs `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge` de toda parede `IS_WALL_BP` da cena | `hb_props.py:211-225` | 🟢 |
| HB_CORE-R20 | Padrões da cena (em polegadas): pé-direito 96, meia parede 42, parede falsa 34, parede 4,5 (externa 6, interna 4,5), porta simples 36 × 84, dupla 72, janela 34 × 34 a 36 do piso | `hb_props.py:468-480` | 🟢 |
| HB_CORE-R21 | `run_calc_fix`: por passada (padrão 2) toca location e `show_viewport` dos modificadores NODES, roda todas as calculadoras, avança e volta um frame e atualiza a view layer; `until_stable` repete até 5 vezes, até as dimensões variarem ≤ 0,0001 m (retorna nº de passadas ou −1) | `hb_utils.py:190-297` | 🟢 |
| HB_CORE-R22 | Cena principal = primeira com `IS_MAIN_SCENE`; senão, primeiro cômodo por `sort_order`; senão, `scenes[0]`; a marcação é tentada e falha em silêncio em contexto de desenho | `hb_project.py:143-176` | 🟢 |
| HB_CORE-R23 | `set_main_scene` garante uma única cena marcada (remove o marcador das demais) | `hb_project.py:225-236` | 🟢 |
| HB_CORE-R24 | `migrate_project_data` copia custom props da cena antiga para a nova, exceto `IS_MAIN_SCENE`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW`, `IS_CROWN_DETAIL`, `home_builder`, `cycles` e `VIEW_*`, sem sobrescrever chaves existentes | `hb_project.py:239-262` | 🟢 |
| HB_CORE-R25 | "Cena de cômodo" tem duas definições: `hb_project.is_room_scene` exclui layout e detalhe; `hb_utils.is_room_scene` também exclui `IS_CROWN_DETAIL` | `hb_project.py:265-271`, `hb_utils.py:461-469` | 🟢 |
| HB_CORE-R26 | Enum de obstáculos: cabeçalhos `HEADER_*` com ids 0/100/200/300 e itens `base+i+1`; escolher um tipo copia as 4 dimensões padrão; cabeçalho não pode ser posicionado; "From Floor" só aparece para superfície `WALL` | `hb_props_obstacles.py:104-145,216-252` | 🟢 |
| HB_CORE-R27 | Limites de obstáculo: largura/altura de 0,5" a 120"; profundidade de 0,25" a 24"; altura do piso de 0 a 120" | `hb_props_obstacles.py:161-199` | 🟢 |
| HB_CORE-R28 | `IF`, `OR`, `AND` ficam disponíveis nas expressões de driver; só são injetados se o nome ainda não existir no namespace | `hb_driver_functions.py:1-26`, `__init__.py:68-70` | 🟢 |
| HB_CORE-R29 | Unidades: base interna em metros; `to_meters/from_meters` com unidade padrão `MM` e fator 0,001 para código desconhecido; unidade da cena = `btm_settings.btm_unit` → `unit_settings` métrico → `MM`; `format_number` com até 3 casas, sem zeros à direita | `data/units.py:9-92` (via `units.py`) | 🟢 |
| HB_CORE-R30 | `meter_to_inch = round(m × 39,3701, 6)`, `meter_to_feet = round(m × 3,28084, 6)`; `inch(x) = x × 0,0254` | `data/units.py:96-115` | 🟢 |
| HB_CORE-R31 | Escala de imagem de referência: `fator = distância conhecida / distância clicada no plano local XY do empty`; aplicado a `empty_display_size`; poll exige empty do tipo `IMAGE` | `ops.py:561-642` | 🟢 |
| HB_CORE-R32 | Backplate da câmera: `vfov` a partir de sensor/lente (ajustado pelo aspecto se o encaixe não for vertical); `altura = 2·d·tan(vfov/2)·1,1`, `largura = altura·aspecto`; material emissivo; sem sombra | `ops.py:337-411` | 🟢 |
| HB_CORE-R33 | "Apply Settings to All" atualiza linhas/polilinhas/círculos (bevel e cor), textos (fonte, tamanho, cor) e, para cotas, apenas objetos **MESH** com `IS_2D_ANNOTATION`, usando os identificadores fixos `Socket_3/4/5` | `ops.py:125-192` | 🟢 |
| HB_CORE-R34 | Configurações recomendadas: `color_type='OBJECT'` é marcado como OBRIGATÓRIO; também desliga linhas de relação e cursor 3D, liga wireframe (limiar 0, opacidade 0,8), usa studio light `paint.sl` e snap `VERTEX` | `ops.py:76-116` | 🟢 |
| HB_CORE-R35 | Tamanhos de anotação em "papel" só recalculam em cenas `IS_LAYOUT_VIEW` com `annotation_auto_scale` ligado | `hb_props.py:136-151` | 🟢 |
| HB_CORE-R36 | Espessura de linha de anotação vale só para curvas `IS_DETAIL_LINE/POLYLINE/CIRCLE`; cotas (`IS_2D_ANNOTATION`) são ignoradas porque têm espessura própria no GN | `hb_props.py:29-38` | 🟢 |
| HB_CORE-R37 | A hierarquia de produto é descoberta subindo pelos pais até achar o marcador (`IS_FRAMELESS_CABINET_CAGE`, `..._PRODUCT_CAGE`, `..._BAY_CAGE`, `..._OPENING_CAGE`, `..._INTERIOR_CAGE`, `..._INTERIOR_SECTION`, `IS_APPLIANCE`, `IS_WALL_BP`); `get_interior_part_bp` não sobe | `hb_utils.py:67-166` | 🟢 |
| HB_CORE-R38 | O estado da vista 3D (posição, rotação, distância, perspectiva, shading) é guardado em custom props `VIEW_*` da cena e restaurado com padrões seguros | `hb_utils.py:311-385` | 🟢 |
| HB_CORE-R39 | `delete_obj_and_children` remove filhos antes do pai (pós-ordem) com `do_unlink=True` | `hb_utils.py:169-187` | 🟢 |
| HB_CORE-R40 | O Editor de Parede usa por padrão: unidade MM, comprimento 1,7 m, altura 2,6 m, espessura 0,15 m, ângulo absoluto/relativo 270°, passo linear 0,05 m, passo angular 45°, orientação RIGHT, tipo NORMAL | `hb_props.py:824-930` | 🟢 |

**Algoritmos principais:** cache de identificadores de socket GN com invalidação e nova tentativa (R03); distribuição
de medidas da calculadora (R15); reavaliação iterativa de drivers até estabilizar (R21); vizinhança de paredes
topológica + geométrica (R08); ajuste de casas decimais por snap de unidade (R12); religação do node group de cota (R13);
tamanho do backplate pelo FOV da câmera (R32); projeção raio–plano para escala por dois pontos (R31).

### Constantes/enums

- 🟢 `geometry_nodes_path`, `cabinet_part_modifiers_path` (`hb_types.py:8-9`).
- 🟢 `GN_INPUTS_AS_RNA = bpy.app.version >= (5, 2, 0)` (`hb_utils.py:13`; duplicado em `compat.py:9`).
- 🟢 Marcadores (ID custom props) definidos aqui: `IS_WALL_BP`, `MENU_ID`, `obj_x`, `IS_GEONODE_CAGE`, `IS_DRAWER_BOX`,
  `IS_2D_ANNOTATION`, `IS_DIMENSION`; lidos aqui: `IS_DETAIL_LINE/POLYLINE/CIRCLE/TEXT`, `IS_ENTRY_DOOR_BP`,
  `IS_WINDOW_BP`, `IS_FRAMELESS_*`, `IS_APPLIANCE`, `IS_MAIN_SCENE`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW`,
  `IS_CROWN_DETAIL`, `FORCE_HALF_OVERLAY_*` (este último nos consumidores).
- 🟢 `main_tab` ∈ {ROOM, PRODUCTS}; `product_tab` ∈ {FRAMELESS, FACE FRAME, CLOSET}; `wall_type` ∈ {Exterior, Interior,
  Half, Fake} (`hb_props.py:444-466`).
- 🟢 `HB_Wall_Editor_Props.unit_system` ∈ {MM, CM, M, IN, FT}; `orientation` ∈ {RIGHT, LEFT}; `wall_type` ∈ {NORMAL,
  DRYWALL} (`hb_props.py:826-924`).
- 🟢 Tipos de `add_property`: CHECKBOX, DISTANCE, ANGLE, PERCENTAGE, QUANTITY, COMBOBOX (`hb_props.py:337-374`).
- 🟢 Superfícies de obstáculo: WALL, FLOOR, CEILING, ANY; 15 de parede, 5 de piso, 10 de teto e 6 diversos
  (`hb_props_obstacles.py:17-101`).
- 🟢 Unidade da cota (`Unit Type`): 0 = in, 1 = ft, 2 = mm, 3 = cm, 4 = m (`hb_types.py:697`).
- 🟢 Fatores de unidade `UNIT_CONVERSION_TO_METERS` e `UNIT_LABELS` (`data/units.py:9-33`).
- 🟢 `bl_idname`s: `blendertomob.to_do`, `blendertomob.set_recommended_settings`, `blendertomob.rendering_settings`,
  `blendertomob.create_camera`, `blendertomob.set_scale_with_two_points`,
  `home_builder_annotations.apply_settings_to_all` (`ops.py`).

### Riscos Blender 5.2

1. 🟢 **Identificadores de socket fixos** — `ops.py:176,180,184` usam `hb_utils.set_gn_input(mod, 'Socket_3'|'Socket_4'|'Socket_5', …)`,
   contrariando a regra do projeto (resolver pelo nome). Além disso, o filtro `obj.type == 'MESH'` (`ops.py:172`) não
   pega cotas, que são objetos `CURVE` (`hb_types.py:109-112`) 🟡 → na prática, o operador não atualiza nenhuma cota.
2. 🟢 **Ponte GN duplicada com semântica divergente** — `hb_utils.set_gn_input(mod, identifier, …)` × `compat.set_gn_input(mod, input_name, …)`;
   dois caches `_INPUT_IDENT_CACHE` (`hb_types.py:21`, `compat.py:4`). A camada `hb_core` não usa `compat.py`. Isso
   contraria a regra "diferenças de versão só em `compat.py`" do CLAUDE.md.
3. 🟡 **Cache por `id()` do wrapper RNA** — `id(node_group)` não é uma chave estável em Python (pode ser reciclada), com
   risco de escrita silenciosa no socket errado (`hb_types.py:30-37`).
4. 🟡 **Caminhos de driver mudam entre versões** — `gn_input_data_path` gera `modifiers["M"].properties.inputs.ID.value`
   no 5.2 e `modifiers["M"]["ID"]` antes (`hb_utils.py:55-60`). Drivers criados em arquivos salvos antes do 5.2 guardam o
   caminho antigo; 🔴 não há migração no módulo para reescrevê-los ao abrir.
5. 🟢 **`Material.use_nodes` obsoleto** — `ops.py:386` (`mat.use_nodes = True`) não tem efeito desde o 5.0 e a remoção está
   prevista para o 6.0 (`docs/rag/blender-api/corpus/bpy.types.Material.md#bpy.types.Material.use_nodes`). Leituras
   `mat.use_nodes` em `hb_props.py:51,72` e `ops.py:143,164` sempre retornam True.
6. 🟢 **`driver_namespace` sem limpeza** — `IF/OR/AND` (e, via `inspect.getmembers`, também os dunders do módulo, como
   `__name__` e `__doc__`) são injetados em `bpy.app.driver_namespace` (`__init__.py:68-70,254-256`) e nunca removidos em
   `unregister()`.
7. 🟢 **Draw handler de modal fora do `unregister`** — `set_scale_with_two_points` remove o handler em `cleanup`
   (`ops.py:588-594`), mas não há remoção em `unregister()` se o modal estiver ativo durante a desativação.
8. 🟢 **Registro que engole exceções** — `except Exception: pass` em todos os `register()` do módulo esconde falhas de
   registro de PropertyGroup (e, por consequência, `AttributeError` em `obj.home_builder`).
9. 🟢 **Convenções** — `mod_name` sem `# type: ignore` (`hb_props.py:325`); `home_builder_OT_to_do` e
   `set_recommended_settings` sem `bl_options` (o segundo altera overlay, shading e `tool_settings`) (`ops.py:10-13,29-32`);
   `bl_options = {'UNDO'}` sem `REGISTER` no modal de escala (`ops.py:546`).
10. 🟡 **`id_properties_ui` / `COMBOBOX`** — `bpy.types.ID.id_properties_ui` não aparece no corpus do RAG (método de
    `bpy_struct`, existente desde 3.0 — inferido). O ramo COMBOBOX (`hb_props.py:367-374`) não chama `id_properties_ensure`
    e passa `items=` à UI de uma propriedade cujo valor pode não ser inteiro — comportamento não verificado no 5.2.
11. 🟢 O uso de `obj["..."]`/`obj.get(...)` no módulo recai sobre **ID custom properties** (marcadores e prompts criados
    por `add_property`), não sobre `bpy.props` — compatível com o armazenamento separado do 5.0.
12. 🟢 `python3 docs/rag/tools/check_api.py` → "OK: no unknown API references found" (148 arquivos).

### Dependências de outros módulos

- 🟢 `data/units.py` (via `units.py`).
- 🟢 `operators/layouts.py` → `recalculate_annotation_sizes_for_scene` (import tardio em `hb_props.py:143,150`).
- 🟢 `molding/ops.py` (`on_package_changed`) e `molding/packages.py` (`enum_items`, `profile_enum_items`) (`hb_props.py:164-208`).
- 🟢 `product_libraries/frameless/operators/ops_crown.py` (`get_molding_categories`, `get_molding_items`) (`hb_props.py:423-439`).
- 🟢 `Scene.hb_frameless` e `Scene.hb_face_frame` (bibliotecas de produto) em `update_ceiling_height` (`hb_props.py:82-100`).
- 🟢 Preferências do add-on (`wall_color`, `annotation_color`) em `__init__.py:110-113` via `get_user_preferences`
  (`hb_props.py:806-809`).
- 🟢 `ui/menus.py` (`HOME_BUILDER_MT_wall_commands` `:64`, `HOME_BUILDER_MT_dimension_commands` `:645`) referenciados por
  `MENU_ID`; `ui/menus.py:428` chama `ensure_dimension_text_offset_basis`.
- 🟢 `operators/ops_obstacles.py:73` (`home_builder_obstacles.place_obstacle`).
- 🟢 `__init__.py` (registro, `load_file_post`, `driver_namespace`).
- 🟢 Consumidores: `product_libraries/*` (Cabinet, Closet, FaceFrame, Appliance), `hb_details.py`, `hb_layouts.py`,
  `hb_placement.py`, `operators/*`, `molding/*`, `ui/*` — 49 arquivos importam `hb_types`.

### Lacunas

- 🔴 Operadores `pc_prompts.add_calculator_prompt`, `pc_prompts.edit_calculator` e `pc_prompts.run_calculator`
  (`hb_props.py:264-280`) não existem em `blendertomob/` — os botões de `Calculator.draw` falham.
- 🔴 `GeoNodeWall.assign_materials` (`hb_types.py:468-478`) é código morto (sem chamadores) e usa inputs
  (`Left/Right/Front/Back Surface`) diferentes dos que `update_wall_material` e `operators/walls.py:4544` usam
  (`Inside/Outside Face`, `Left/Right Edge`); o TODO "GET MATERIAL" (`:469-471`) não foi implementado.
- 🔴 As interfaces dos node groups em `geometry_nodes/*.blend` (nomes e tipos de inputs) não foram verificadas.
- 🟢 `update_main_tab` / `update_product_tab` são stubs com `print` (`hb_props.py:19-26`); `remove_calculator_prompt`
  é stub (`:291-292`).
- 🟢 `annotation_dimension_extend_line` usa `update=update_dimension_tick_length` (`hb_props.py:707`), que só reescreve
  `Tick Length`; mudar "Extend Line" na cena não propaga para as cotas existentes (provável bug).
- 🟢 `driver_location` / `driver_rotation` com eixo fora de x/y/z geram `UnboundLocalError` (`hb_types.py:211-233`).
- 🟡 `Unit Type = 1` (pés) nunca é produzido por `get_unit_type`, e a camada legada ignora `btm_settings.btm_unit`.
- 🟡 `home_builder_OT_rendering_settings.execute` não faz nada: o diálogo altera as props diretamente no `draw`
  (`ops.py:210-265`).
- 🟢 O PropertyGroup `HB_Wall_Editor_Props` está neste módulo, mas pertence funcionalmente ao Editor de Parede moderno
  (ver `_reversa_sdd/wall_editor/`).

---

## Módulo hb_placement

> Camada legada (fork Home Builder 5). Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos à raiz do repositório.

### Propósito

Infraestrutura compartilhada pelos operadores modais de posicionamento (gabinetes, closets, portas/janelas, paredes, obstáculos, desenho 2D e cotas). O módulo **não registra operadores** 🟢; entrega mixins e funções:

- `PlacementMixin` — estado modal (`PlacementState`), entrada numérica com parser de distâncias, raycast/snap via `hb_snap`, cálculo do vão livre numa parede considerando lado, altura, profundidade, paredes vizinhas (cantos), paredes em T, ilhas/penínsulas e snap lines, recuos (hold-off) e snap gabinete-a-gabinete.
- `DimensionOperatorMixin` — cota de 3 cliques (FIRST → SECOND → OFFSET) com modo ortogonal.
- Desenho GPU em POST_PIXEL: cotas de posicionamento com rótulo em pílula e seta de orientação; indicador de snap das cotas; primitivas 2D compartilhadas (`hb_gpu_draw`).
- `duplicate_object_hierarchy` — cópia profunda preservando drivers/parentesco.

### Arquivos

| Arquivo | LOC | Papel |
|---|---|---|
| `blendertomob/hb_placement.py` | 1856 | Mixins, regras de vão/colisão, desenho de cotas |
| `blendertomob/hb_snap.py` | 254 | Região sob o mouse, raycast, snap a geometria e grade |
| `blendertomob/hb_gpu_draw.py` | 114 | Limites visíveis da região WINDOW e primitivas rect/texto/linhas |

Fluxogramas: `_reversa_sdd/flowcharts/legacy-hb_placement.md` e `legacy-hb_placement-{find_placement_gap_by_side,get_adjacent_wall_intrusion,compute_gap_holdoffs,handle_typing_event,snap_main}.md`. Mapa: `_reversa_sdd/hb_placement/legacy-mapping.md`.

### Fluxo de controle

1. **Inicialização** 🟢 — o consumidor chama `init_placement(context)` (`blendertomob/hb_placement.py:115`): `placement_state = PLACING`, `typing_target = NONE`, `typed_value = ""`, `region = hb_snap.get_region(context)`, `placement_objects = []`. Opcionalmente `add_placement_dim_handler` (`:132`) registra `draw_placement_dimensions` em `SpaceView3D` (`'WINDOW'`, `'POST_PIXEL'`); é idempotente via `_placement_dim_handle`.
2. **Tick modal** (padrão do consumidor `hb_frameless_OT_place_cabinet.modal`, `blendertomob/product_libraries/frameless/operators/ops_placement.py:1729-1863`) 🟢: ignora `INBETWEEN_MOUSEMOVE` → setas ↑/↓ alteram quantidade → `handle_typing_event` → oculta previews → `update_snap` → identifica parede (sobe `parent` até `IS_WALL_BP` com modificador) ou fallback `find_nearest_wall_from_cursor` → posiciona na parede (`find_placement_gap_by_side`) ou livre (`detect_cabinet_snap_target`) → LMB/Enter finaliza, RMB/Esc cancela, MMB/roda passam adiante.
3. **Snap** 🟢 — `update_snap` (`hb_placement.py:158`) recalcula a região sob o mouse, converte para coordenadas da região e chama `hb_snap.main(self, event.ctrl, context)` (`blendertomob/hb_snap.py:193`), que preenche `hit_location`, `hit_face_index`, `hit_object`, `view_point`, `hit_grid`.
4. **Entrada numérica** 🟢 — `handle_typing_event` (`hb_placement.py:191`) retorna `True` se consumiu o evento. Máquina: PLACING —(dígito)→ TYPING —(Enter)→ `apply_typed_value` (default volta a PLACING) / —(Esc ou Backspace vazio)→ PLACING / —(Tab)→ aplica e passa ao próximo alvo.
5. **Cancelamento** 🟢 — `cancel_placement` (`:410`) remove recursivamente os objetos registrados (filhos primeiro, tolerando `ReferenceError`), volta a IDLE e restaura o cursor `DEFAULT`. Não remove o draw handler nem limpa o header — responsabilidade do consumidor.
6. **Cotas (DimensionOperatorMixin)** 🟢 — `handle_dimension_event` (`:1476`): MOUSEMOVE atualiza `current_point` (snap em FIRST/SECOND, plano em OFFSET; ortho em SECOND) e preview; LMB avança FIRST→SECOND→OFFSET→FINISHED; `O` cicla ortho; RMB/Esc cancelam; MMB/roda/numpad → `PASS_THROUGH`; o resto → `None` (a subclasse decide). Em FINISHED/CANCELLED remove o draw handler e o header.
7. **Tratamento de erros** 🟢 — leituras de inputs GN sempre em `try/except Exception` com fallback (largura 0, ignorar objeto ou retornar `None`/`0.0`); parser captura `ValueError`/`ZeroDivisionError`; `remove_placement_dim_handler` engole exceções.

**Máquina de estados** (`PlacementState`, `hb_placement.py:34`): `IDLE → PLACING` (init) · `PLACING ↔ TYPING` · `* → IDLE` (cancel). `ADJUSTING` (`:39`) é declarado mas nunca atribuído no módulo 🟢.

### Algoritmos e regras

| ID | Regra | Local | Conf. |
|---|---|---|---|
| HB_PLACEMENT-R01 | Após `init_placement` o estado é PLACING; após `cancel_placement`, IDLE. | `blendertomob/hb_placement.py:117`, `:427` | 🟢 |
| HB_PLACEMENT-R02 | Tecla numérica (PRESS) em PLACING inicia digitação; se não houver alvo, usa `get_default_typing_target()` (padrão `LENGTH`). | `hb_placement.py:201-209`, `:252-258` | 🟢 |
| HB_PLACEMENT-R03 | Em TYPING, Esc e Backspace com valor vazio apenas saem da digitação (evento consumido, operador continua). | `hb_placement.py:223-240` | 🟢 |
| HB_PLACEMENT-R04 | Tab aplica o valor atual e inicia digitação do próximo alvo apenas se `get_next_typing_target()` ≠ NONE (padrão NONE → Tab não faz nada). | `hb_placement.py:243-248`, `:260-265` | 🟢 |
| HB_PLACEMENT-R05 | Precedência do parser: contém `'` → pés/polegadas; sufixo `"`/`in` → pol.; `mm`; `cm`; `m`; `ft`; senão número puro. Frações `a/b` e mistas `a b/c` aceitas. | `hb_placement.py:283-371` | 🟢 |
| HB_PLACEMENT-R06 | Número puro: IMPERIAL → polegadas; METRIC → `length_unit` MILLIMETERS/CENTIMETERS, senão metros; NONE → metros. | `hb_placement.py:373-388` | 🟢 |
| HB_PLACEMENT-R07 | Cancelar remove todos os objetos registrados e descendentes (filhos antes do pai). | `hb_placement.py:410-448` | 🟢 |
| HB_PLACEMENT-R08 | Obstáculos na parede: filhos exceto helpers `obj_x`, objeto excluído, `IS_2D_ANNOTATION` e `IS_SNAP_LINE` (tratadas como fronteira). | `hb_placement.py:958-966` | 🟢 |
| HB_PLACEMENT-R09 | Portas (`IS_ENTRY_DOOR_BP`) e janelas (`IS_WINDOW_BP`) bloqueiam os dois lados da parede. | `hb_placement.py:969-974` | 🟢 |
| HB_PLACEMENT-R10 | Um filho está na face frontal se `location.y < wall_thickness/2`; só conta se estiver do mesmo lado da colocação. | `hb_placement.py:972-974` | 🟢 |
| HB_PLACEMENT-R11 | Filtro vertical (opt-in, exige `object_z_start` e `object_height`): obstáculo só conta se `z0 < oz1 and oz0 < z1` (sobreposição estrita). Aplicado a filhos, ilhas, paredes vizinhas/T e aberturas no hold-off. | `hb_placement.py:494-497`, `:988-993`, `:784-789`, `:885-889`, `:1235-1242` | 🟢 |
| HB_PLACEMENT-R12 | Extensão em X do obstáculo conforme rotação Z (tolerância 0,1 rad): −90°/270° → `[x−DimY, x]`; ±180° → `[x−DimX, x]`; outros → `[x, x+DimX]`. | `hb_placement.py:999-1017` | 🟢 |
| HB_PLACEMENT-R13 | Gabinetes livres (sem pai, com `FREE_CABINET_TAGS`) cuja pegada cruza a faixa de profundidade (front `[−band,0]`, back `[t,t+band]`, `band = object_depth` ou 24") viram obstáculo, recortados a `[0, L]` e descartados se < 1/4". | `hb_placement.py:1028-1070` | 🟢 |
| HB_PLACEMENT-R14 | Invasão de parede vizinha (ponta esquerda/direita, inclusive através da costura do loop): laje da vizinha (se protrai para o lado da colocação) e gabinetes `CABINET_MARKERS` dela viram obstáculos `[0, intr_esq]` e `[L−intr_dir, L]`. | `hb_placement.py:672-826`, `:1078-1097` | 🟢 |
| HB_PLACEMENT-R15 | Parede em T: extremidade de outra parede estritamente dentro do vão (margem 0,01 m) e a até 0,02 m da laje; não paralela (|y| ≥ 0,001); bloqueia só o lado para onde protrai; span = projeção da espessura. | `hb_placement.py:868-915` | 🟢 |
| HB_PLACEMENT-R16 | Snap lines são obstáculos de largura zero em `SNAP_X_POSITION` (fallback `location.x`). | `hb_placement.py:1110-1114` | 🟢 |
| HB_PLACEMENT-R17 | Escolha de `snap_x` no vão: largura ≥ vão → início; cursor a menos de w/2 da borda esquerda → início; a menos de w/2 da direita → `gap_end − w`; senão centrado no cursor (`cursor − w/2`). | `hb_placement.py:563-576`, `:1131-1139` | 🟢 |
| HB_PLACEMENT-R18 | Parede sem obstáculos: vão `[0, L]` e `snap_x = cursor_x` (sem centralizar nem prender às bordas — difere de R17). | `hb_placement.py:540-542`, `:1116-1117` | 🟢 |
| HB_PLACEMENT-R19 | Alvo de snap gabinete→gabinete: primeiro ancestral com marcador de `CABINET_MARKERS`; encontrar `IS_WALL_BP` antes interrompe (gabinetes de parede não são alvos). | `hb_placement.py:580-606` | 🟢 |
| HB_PLACEMENT-R20 | Lado do snap: X local do hit < `DimX/2` → LEFT; senão RIGHT. | `hb_placement.py:631-632` | 🟢 |
| HB_PLACEMENT-R21 | Transformação de snap: LEFT desloca `−new_width` em X local do alvo; RIGHT desloca `+snap_width`; offset rotacionado por `rotation_euler.z` do alvo; Z e rotação copiados do alvo. | `hb_placement.py:661-670` | 🟢 |
| HB_PLACEMENT-R22 | Hold-off por borda: ponta da parede (±1/2") recebe recuo exceto em canto interno; borda que coincide (±1/4") com fim/início de porta/janela com sobreposição vertical recebe recuo; demais (gabinetes vizinhos) 0. `holdoff ≤ 0` desativa. | `hb_placement.py:1209-1261` | 🟢 |
| HB_PLACEMENT-R23 | Os dois recuos são escalados proporcionalmente para deixar ≥ 1" de vão útil. | `hb_placement.py:1263-1269` | 🟢 |
| HB_PLACEMENT-R24 | Canto interno ⇔ direção da vizinha, saindo do vértice comum, tem produto escalar > 1e-4 com a normal do lado de colocação (−Y local frente, +Y trás). | `hb_placement.py:1143-1189` | 🟢 |
| HB_PLACEMENT-R25 | Raycast ignora objetos com `HB_CURRENT_DRAW_OBJ`; se o raio central falha, testa 6 raios num anel de 50 px e fica com o hit mais próximo da origem da vista. | `blendertomob/hb_snap.py:7-8`, `:48-82` | 🟢 |
| HB_PLACEMENT-R26 | Com Ctrl e hit: snap ao vértice do polígono atingido a < 50 px em tela; senão ao ponto mais próximo de uma aresta (busca dicotômica, ε 1e-4). | `hb_snap.py:84-145`, `:207-208` | 🟢 |
| HB_PLACEMENT-R27 | Sem hit: interseção com plano pela origem (normal Z; ou a própria direção de vista em vista lateral alinhada); com Ctrl, snap aos cantos da célula de grade de tamanho `10^(round(log10(view_distance))−1)`. | `hb_snap.py:153-191` | 🟢 |
| HB_PLACEMENT-R28 | `snap_value_to_grid`: IMPERIAL 1" (fino 1/16"); outros 10 mm (fino 1 mm); arredondamento ao mais próximo. | `hb_snap.py:212-236` | 🟢 |
| HB_PLACEMENT-R29 | Cota: 3 cliques FIRST→SECOND→OFFSET; clique sem `current_point` é ignorado; ortho só se aplica no 2º ponto. | `hb_placement.py:1511-1540` | 🟢 |
| HB_PLACEMENT-R30 | Ortho cicla OFF→AUTO→H→V→OFF; AUTO é resolvido uma vez (|dx| ≥ |dy| → H) e permanece fixo. | `hb_placement.py:1438-1474` | 🟢 |
| HB_PLACEMENT-R31 | `duplicate_object_hierarchy`: desoculta temporariamente toda a hierarquia, marca com `_HB_DUP_TOKEN`, usa `bpy.ops.object.duplicate(linked=False)`, restaura flags nos originais e cópias, restaura seleção/ativo; retorna `None` se o ativo continuar sendo a origem. | `hb_placement.py:1273-1340` | 🟢 |
| HB_PLACEMENT-R32 | Cota de posicionamento: linha + ticks perpendiculares de 6 px; rótulo em pílula escura (0.13,0.13,0.14,0.85) com borda, deslocada perpendicularmente; fonte `14 × ui_scale`; cor por spec (padrão branco 0.95); seta de orientação amarela (1,0.85,0.1) com 2,5 px. | `hb_placement.py:1712-1856` | 🟢 |
| HB_PLACEMENT-R33 | Indicador de snap da cota: verde, raio 10 px + cruz quando `is_snapped`; amarelo raio 6 px senão; círculo azul claro (+15,+15) quando ortho ativo. | `hb_placement.py:1642-1705` | 🟢 |
| HB_PLACEMENT-R34 | Área visível da WINDOW desconta TOOLS (esq.), UI (dir.), headers/asset shelf (topo/base decididos pelo centro vertical). | `blendertomob/hb_gpu_draw.py:12-63` | 🟢 |
| HB_PLACEMENT-R35 | Consumidor frameless: posição só é recalculada fora de TYPING ou quando o alvo é WIDTH/HEIGHT; offsets digitados congelam a posição. | `blendertomob/product_libraries/frameless/operators/ops_placement.py:1805-1817` | 🟢 |

**Algoritmos principais**: varredura de intervalos ordenados para achar o vão (sweep 1D); projeção de cantos via `matrix_world` para o espaço local da parede (intrusões, ilhas); teste de sobreposição de intervalos; busca dicotômica em tela para snap a aresta; interseção reta-plano para grade; escala proporcional de recuos.

### Constantes/enums

| Nome | Valor | Local |
|---|---|---|
| `PlacementState` | IDLE, PLACING, TYPING, ADJUSTING (não usado) | `hb_placement.py:34-39` |
| `TypingTarget` | NONE, LENGTH, OFFSET_X, OFFSET_RIGHT, OFFSET_Y, WIDTH, HEIGHT, DEPTH | `hb_placement.py:42-51` |
| `NUMBER_KEYS` | 0-9 (linha e numpad), `.`, `-`, `/` | `hb_placement.py:55-64` |
| `CABINET_MARKERS` | IS_FRAMELESS_CABINET_CAGE, IS_FACE_FRAME_CABINET_CAGE, IS_APPLIANCE, IS_CLOSET_STARTER_CAGE | `hb_placement.py:71-78` |
| `FREE_CABINET_TAGS` | IS_FACE_FRAME_CABINET_CAGE, IS_FRAMELESS_CABINET_CAGE, IS_FRAMELESS_PRODUCT_CAGE, IS_APPLIANCE | `hb_placement.py:27-32` |
| `DIM_STATE_*` | 'FIRST', 'SECOND', 'OFFSET' | `hb_placement.py:1374-1376` |
| `SNAP_RADIUS` | 20 px (declarado, não usado no módulo 🟢) | `hb_placement.py:1379` |
| `RADIUS`, `STEPS` | 50 px, 6 | `hb_snap.py:7-8` |
| `END_MARGIN`, `FACE_TOL` | 0,01 m, 0,02 m | `hb_placement.py:868-869` |
| Tolerâncias hold-off | `end_tol` 1/2", `edge_tol` 1/4", folga mínima 1" | `hb_placement.py:1217-1218`, `:1264` |
| Faixa padrão de ilha | 24" | `hb_placement.py:1028` |
| Largura mínima de ilha | 1/4" | `hb_placement.py:1068` |
| Tolerância de rotação | 0,1 rad | `hb_placement.py:1000-1003` |
| Tags lidas | IS_WALL_BP, obj_x, IS_2D_ANNOTATION, IS_SNAP_LINE, SNAP_X_POSITION, IS_ENTRY_DOOR_BP, IS_WINDOW_BP, HB_CURRENT_DRAW_OBJ, _HB_DUP_TOKEN (escrita) | vários |

### Riscos Blender 5.2

1. 🟢 **Sem acesso direto a `mod["Socket_X"]`** nos três arquivos: todo input GN passa por `hb_types.GeoNodeObject.get_input` → `hb_utils.get_gn_input` (`blendertomob/hb_types.py:362-388`). Continua valendo o risco do projeto de duplicação `hb_utils` × `compat` (CLAUDE.md).
2. 🟢 **Shader builtin obtido direto** com `gpu.shader.from_builtin('UNIFORM_COLOR')` (`hb_placement.py:1650`, `:1756`) em vez de `compat.get_builtin_shader` — nome válido no 5.2 (`docs/rag/blender-api/corpus/gpu.md#d-rectangle`), mas foge da regra de centralizar diferenças de versão.
3. 🟢 **Primitivas `TRI_FAN` e `LINE_LOOP`** (`hb_placement.py:1830-1832`) — ainda listadas como válidas em `docs/rag/blender-api/corpus/gpu.types.md` (GPUBatch type). Sem risco imediato; 🟡 candidatas a remoção futura por backends Vulkan/Metal.
4. 🟡 **Draw handlers sem `cancel()`**: nenhum mixin define `cancel()`; se o Blender abortar o modal (troca de arquivo, fechamento de janela), `_placement_dim_handle`/`_dim_draw_handle` ficam registrados. `add_dimension_draw_handler` (`:1400`) não é idempotente (chamá-lo duas vezes vaza o primeiro handle). A remoção do handler de posicionamento depende de cada consumidor (`face_frame/.../ops_placement.py`, `closets/.../ops_closet.py`).
5. 🟡 **Índice de face do `Scene.ray_cast`**: pode ser `-1` quando os dados originais não estão disponíveis (`docs/rag/blender-api/corpus/bpy.types.Scene.md#bpy.types.Scene.ray_cast`); `snap_to_object` (`hb_snap.py:139`) indexa `polygons[-1]` do mesh avaliado sem checar, e índices originais podem não casar com o mesh avaliado de objetos GN.
6. 🟢 **`context.view_layer.update()` a cada tick** (`hb_snap.py:50`) — correto contra dados desatualizados (`docs/rag/project/04_armadilhas.md`), mas caro em cenas grandes; somado a `get_tee_wall_intrusions`/ilhas que varrem `bpy.context.scene.objects` inteiro por MOUSEMOVE.
7. 🟢 **`region` possivelmente `None`**: `get_region` retorna `None` sem viewport 3D; `update_snap` então acessa `self.region.x` (`hb_placement.py:169-172`) → `AttributeError`.
8. 🟡 **Contexto capturado nos args do handler** (`(self, context)` em `:143` e `:1403`): `draw_placement_dimensions` lê `context.region`/`region_data` a cada desenho; funciona porque o `Context` é o proxy global, mas é frágil fora da viewport de origem.
9. 🟡 `duplicate_object_hierarchy` usa `bpy.ops.object.duplicate`, que exige contexto de objeto/viewport válido; chamado de um modal fora da VIEW_3D pode falhar por `poll`.
10. 🟢 Tags de objeto (`'IS_WALL_BP' in obj`, `obj.get(...)`) são ID properties custom, não `bpy.props` — compatíveis com a separação de armazenamento do 5.0. `home_builder.mod_name` é lido por atributo (correto).

### Dependências de outros módulos

- `hb_types` 🟢 — `GeoNodeObject.get_input('Dim X'|'Dim Y'|'Dim Z')`, `GeoNodeWall.get_input('Length'|'Thickness'|'Height')`, `has_modifier`, `get_connected_wall(direction, include_loop_seam=True)` (`blendertomob/hb_types.py:362`, `:410`, `:486`), import local dentro dos métodos.
- `units` 🟢 — `inch`, `millimeter`, `centimeter`, `feet`.
- `hb_utils` 🟢 (indireto, via `hb_types`) — `get_gn_input`.
- Blender: `bpy`, `blf`, `gpu`, `gpu_extras.batch.batch_for_shader`, `bpy_extras.view3d_utils`, `mathutils` (`Vector`, `Matrix`, `geometry.intersect_line_plane`).
- Consumidores: bibliotecas frameless/face_frame/closets, `operators/walls.py`, `doors_windows.py`, `ops_obstacles.py`, `details.py`, `layouts.py`, `scene_navigator.py`, `viewport_hud.py`.

### Lacunas

- 🔴 Semântica completa dos consumidores (face-frame e closets somam >5000 linhas usando o mixin) não foi escavada aqui; a máquina do tick modal foi documentada pelo consumidor frameless.
- 🔴 Onde `HB_CURRENT_DRAW_OBJ`, `IS_SNAP_LINE`/`SNAP_X_POSITION` e `obj_x` são gravados (fora do módulo).
- 🟢 `PlacementState.ADJUSTING`, `TypingTarget.OFFSET_Y` e `DimensionOperatorMixin.SNAP_RADIUS` não são referenciados em nenhum outro arquivo do pacote (grep); `operators/details.py:19` define seu próprio `SNAP_RADIUS = 20`.
- 🟡 Varredura de vão assume obstáculos não sobrepostos; comportamento com obstáculos aninhados/sobrepostos e com cursor dentro de obstáculo não é tratado explicitamente.
- 🟡 Sufixos de unidade e frações mistas não são digitáveis via `NUMBER_KEYS` (sem espaço, aspas ou letras); o suporte do parser só é exercido se um consumidor montar a string por outro caminho.
- 🟢 Parâmetro `wall_thickness` de `compute_gap_holdoffs` não é usado; o único chamador é `product_libraries/face_frame/operators/ops_placement.py:2543`. `find_placement_gap` (sem lado, sem ilhas, sem intrusão de canto; T-walls dos dois lados) é usado apenas por portas/janelas (`operators/doors_windows.py:583,614,810`), o que é coerente com aberturas atravessarem a parede.

---

## Módulo hb_layouts

> Camada legada (fork do Home Builder 5). Nível: DETALHADO. Confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas: `_reversa_sdd/flowcharts/legacy-hb_layouts.md` (+ `-create_iso_left`, `-elevation_create`,
> `-build_line_art_marked_channel`, `-ensure_asset_libraries`). Mapeamento: `_reversa_sdd/hb_layouts/legacy-mapping.md`.

### Propósito

Produzir a documentação 2D do projeto de marcenaria dentro do Blender: cada prancha é uma **cena dedicada**
(`IS_LAYOUT_VIEW`) que instancia (sem copiar) os objetos da sala por meio de *collection instances*, fotografada
por uma **câmera ortográfica** travada e renderizada em Workbench com traço **Freestyle** ou **Grease Pencil Line Art**.
O módulo cobre elevações de parede com cotas automáticas de gabinetes, planta baixa, vista 3D, multivistas de um objeto
(cruz de projeções ou prancha compacta iso + planta + elevação), carimbo (title block), detalhes 2D estilo CAD com
biblioteca persistente do usuário e o registro das bibliotecas de assets (embutida + do usuário) nas preferências do Blender. 🟢

### Arquivos

| Arquivo | Linhas | Papel | Conf. |
|---|---|---|---|
| `blendertomob/hb_layouts.py` | 3017 | Vistas de layout, câmeras, papel, Freestyle/Line Art, title block, cotas automáticas | 🟢 |
| `blendertomob/hb_details.py` | 439 | Cena de detalhe 2D, primitivas (linha, polilinha, círculo, texto), estilo de rótulo | 🟢 |
| `blendertomob/hb_detail_library.py` | 243 | Biblioteca de detalhes: `.blend` por detalhe + `library_index.json` | 🟢 |
| `blendertomob/hb_assets.py` | 430 | Bibliotecas de assets, catálogos, asset shelf, `BTM_AssetLibraryEntry` | 🟢 |

### Fluxo de controle

**Criação de cena base — `LayoutView.create_scene(name) -> Scene`** (`blendertomob/hb_layouts.py:1141`) 🟢
1. Captura `unit_settings` (system, scale_length, length_unit) e `tool_settings` de snap da cena atual.
2. `bpy.data.scenes.new(name)`, marca `IS_LAYOUT_VIEW`, **troca `bpy.context.window.scene`** para a nova cena.
3. Copia unidades, `home_builder.product_tab` e snap; chama `_setup_render_settings` (`:1194`): Workbench, AA `'32'`,
   cor `OBJECT`, luz `FLAT`, `SOLID`; cria as três collections de roteamento (`_create_freestyle_collections` `:1235`);
   ramifica pela engine de linha (`get_default_line_engine` `:132`) → Line Art (`setup_line_art_for_scene` `:380`)
   ou Freestyle (`_setup_freestyle_linesets` `:1274`) e carimba `scene['HB_LINE_ENGINE']`.

**Vistas concretas** 🟢
- `ElevationView.create(wall_obj, name=None, paper_size='LETTER', landscape=True) -> Scene` (`:1447`): cena +
  `IS_ELEVATION_VIEW`/`SOURCE_WALL`; câmera ORTHO rot `(90°, 0, rotZ da parede)`; `set_paper_size`;
  `add_cabinet_dimensions` (`:1580`) **antes** de `_fit_camera_to_content` (`:1504`) para que as cotas entrem no
  enquadramento; `_create_content_collections` (`:1681`); `TitleBlock.create`.
- `ElevationView.update()` (`:1780`): reposiciona câmera e ortho com regra simplificada (sem cotas/filhos).
- `PlanView.create(name='Floor Plan', source_scene=None, paper_size='LETTER', landscape=True) -> Scene` (`:1819`).
- `View3D.create(name='3D View', perspective=True, source_scene=None, paper_size, landscape) -> Scene` (`:1992`):
  força Freestyle mesmo se a preferência for Line Art (`:2015-2019`).
- `MultiView.create(source_obj, views, name=None, paper_size='TABLOID', landscape=True) -> Scene|None` (`:2205`):
  retorna `None` se `views` vazio; com `'ISO'` desvia para `_create_iso_left` (`:2397`).
- Fábricas: `get_layout_view_from_scene(scene)` (`:2960`) despacha por tags na ordem ELEVATION → PLAN → 3D → MULTI →
  base; `create_all_elevations()` (`:2998`) cria uma elevação por objeto `IS_WALL_BP` em **todo** `bpy.data.objects`.

**Line Art** 🟢
- `setup_line_art_for_scene(scene, solid, dashed, ignore)` (`:380`): recria o objeto GP (remove o anterior),
  2 camadas + 4 modificadores (Lineart Solid, Lineart Dashed, Resample Dashed, Dash Hidden) e chama
  `update_line_art_sizes`.
- `update_line_art_sizes(scene)` (`:476`): lê `hb_layout_scale` e fatores `hb_lineart_*_scale`; converte via
  `operators.layouts.paper_to_world` (import tardio para evitar ciclo, `:493`); qualquer exceção → retorna silenciosamente
  (`:503-504`); associa a câmera jitter aos modificadores LINEART.
- `bake_line_art_editable(scene) -> bool` (`:255`): troca temporariamente `window.scene` (try/finally), captura strokes
  avaliados, desliga todos os modificadores, reescreve as camadas; `False` se nada capturado ou sem GP.
- `unbake_line_art` (`:333`), `set_line_art_visible` (`:198`), `refresh_line_art` (`:217`, alterna `show_viewport`
  para invalidar cache).
- `build_line_art_marked_channel` (`:564`), `build_line_art_text_holdouts(scene, rects)` (`:708`),
  `setup_iso_freestyle` (`:825`) — idempotentes, mas **sem chamador no pacote** 🔴.

**Detalhes** 🟢
- `DetailView.create(name='Detail') -> Scene` (`blendertomob/hb_details.py:29`): nome único (`"Detail 1"`, …), salva o
  estado da vista se a cena atual for de sala (`hb_utils.save_view_state`), cria cena `IS_DETAIL_VIEW`, copia unidades,
  `product_tab` e snap (apenas `snap_elements`/`use_snap`), configura viewport top-down SOLID/OBJECT.
- Primitivas `GeoNodeLine/Polyline/Circle/Text.create(...)` linkam em `bpy.context.scene` e criam material próprio
  (exceto Text, que usa o material compartilhado).

**Biblioteca de detalhes** 🟢 (`blendertomob/hb_detail_library.py`)
- `save_detail_to_library(context, name, description='') -> (bool, str, str)` (`:59`), `load_detail_from_library(context,
  filepath) -> (bool, str, list)` (`:162`), `get_library_details(detail_type=None) -> list` (`:132`),
  `get_detail_info(filepath) -> dict` (`:208`), `delete_detail_from_library(filename) -> (bool, str)` (`:225`).
- Tratamento de erro: índice corrompido → índice vazio silencioso (`:28-35`); escrita de índice sem try (`:38-43`).

**Assets** 🟢 (`blendertomob/hb_assets.py`)
- `register()` (`:408`) registra classes pulando as já presentes e engolindo exceções; `ensure_asset_libraries()`
  (`:209`) é chamado do `register()` do add-on (`blendertomob/__init__.py:248`); `unregister()` (`:418`) remove as
  bibliotecas das preferências e desregistra classes.
- Operadores `home_builder.add_asset_library` / `remove_asset_library` / `refresh_asset_libraries` /
  `assign_asset_catalog` (`:280-394`).

### Algoritmos e regras

| ID | Regra | Local | Conf. |
|---|---|---|---|
| HB_LAYOUTS-R01 | Resolução da prancha = polegadas × DPI (padrão 150), com troca largura/altura em paisagem; tamanho desconhecido cai para LETTER; `resolution_percentage = 100`. | `hb_layouts.py:23-42`, `:1384-1410` | 🟢 |
| HB_LAYOUTS-R02 | Tamanhos de papel (pol., retrato): LETTER 8.5×11, LEGAL 8.5×14, TABLOID 11×17, A4 8.27×11.69, A3 11.69×16.54 — tabela duplicada em `operators/layouts.py:90` (`PAPER_SIZES_INCHES`). | `hb_layouts.py:12-18` | 🟢 |
| HB_LAYOUTS-R03 | Configuração de papel persiste como IDProperties da cena `PAPER_SIZE`, `PAPER_LANDSCAPE`, `PAPER_DPI`; leitura com padrões LETTER/True/150. | `hb_layouts.py:1128-1130`, `:1400-1403` | 🟢 |
| HB_LAYOUTS-R04 | Padrões de papel inconsistentes: vistas LETTER, MultiView TABLOID, `Scene.hb_paper_size` TABLOID, preferência `default_paper_size` LEGAL (aplicada depois por `apply_default_layout_settings`). | `hb_layouts.py:1448`, `:2206`; `operators/layouts.py:4707-4718`; `__init__.py:132-141` | 🟢 |
| HB_LAYOUTS-R05 | Engine de linha de vistas NOVAS vem da preferência `line_engine` (padrão FREESTYLE); cada cena é carimbada com `HB_LINE_ENGINE`; cenas sem carimbo são tratadas como FREESTYLE. | `hb_layouts.py:132-142`, `:1217-1233` | 🟢 |
| HB_LAYOUTS-R06 | Vista 3D sempre usa Freestyle (remove o GP se a preferência for Line Art). | `hb_layouts.py:2015-2019` | 🟢 |
| HB_LAYOUTS-R07 | Cada cena tem três collections de roteamento `<cena>_Freestyle_Ignore` (anotações, cotas, title block), `_Dashed` (peças internas, linha oculta) e `_Solid` (geometria), com tags `IS_FREESTYLE_*`; ambas as engines as usam. | `hb_layouts.py:1235-1272` | 🟢 |
| HB_LAYOUTS-R08 | Freestyle: lineset Solid (silhueta, borda, crease, edge mark; por collection INCLUSIVE; preto; espessura 1,5) e Dashed (idem + visibilidade HIDDEN; espessura 1,0; traço 10 / intervalo 5). | `hb_layouts.py:1274-1321` | 🟢 |
| HB_LAYOUTS-R09 | Render de prancha: Workbench, AA 32, cor por OBJECT, luz FLAT, sombreamento SOLID. | `hb_layouts.py:1194-1210` | 🟢 |
| HB_LAYOUTS-R10 | Line Art: passe Solid oclusão 0; passe Dashed oclusão 1..128; tracejado por reamostragem (SIMPLIFY SAMPLE) + DASH 3 pontos/2 intervalo; collection IGNORE com `lineart_usage='EXCLUDE'`; GP preto, `show_in_front`, não selecionável. | `hb_layouts.py:390-467` | 🟢 |
| HB_LAYOUTS-R11 | Espessuras Line Art definidas em papel (sólida 0,010", tracejada 0,0067", passo 0,025") e convertidas para mundo por `paper_to_world(valor, escala)` × fatores da cena; escala de fallback `1/4"=1'`; raio do modificador = largura (não dividir por 2). | `hb_layouts.py:80-87`, `:476-515` | 🟢 |
| HB_LAYOUTS-R12 | Câmera "jitter" para Line Art: inclinada 0,05° em pitch e yaw, compartilha o datablock e é filha da câmera da cena; recriada quando a câmera da cena muda; oculta em render/viewport. | `hb_layouts.py:75`, `:164-195` | 🟢 |
| HB_LAYOUTS-R13 | Canal Marked: peças MESH cujo nome contém `Rail`, `Stile`, `Door (`, `Blind Panel` ou `Drawer Front` são retraçadas com oclusão 0..2, em cópias de emissão (` LAEmit`) elevadas 1 mm em direção à câmera; células iso (`Isometric*`, `Iso *`) excluídas. | `hb_layouts.py:96-121`, `:564-675` | 🟢 |
| HB_LAYOUTS-R14 | Holdout de texto: cada retângulo (centro, eixo, meia-largura, meia-altura) vira stroke de 2 pontos com raio = meia-altura e extremos a `max(hw − hh, 0)` do centro; camada `Holdout` com opacidade 0 (não oculta) usada como máscara invertida em todas as outras camadas; retângulos com dimensão ≤ 0 descartados. | `hb_layouts.py:708-750` | 🟢 |
| HB_LAYOUTS-R15 | Bake: congela strokes avaliados (posição, raio, opacidade, material, cyclic), desliga TODOS os modificadores (viewport e render) e marca `HB_LINEART_BAKED`; vistas baked não religam modificadores ao alternar visibilidade; unbake limpa frames e religa. | `hb_layouts.py:198-214`, `:255-346` | 🟢 |
| HB_LAYOUTS-R16 | Vista híbrida: células iso migram para `<cena>_Iso_Solid/_Iso_Dashed` e são desenhadas por lineset Freestyle no view layer; sem células iso, `view_layer.use_freestyle=False` (marca de passe único); `render.use_freestyle` permanece desligado (o exportador o liga). | `hb_layouts.py:825-937`, `:763-774` | 🟢 |
| HB_LAYOUTS-R17 | Objetos excluídos das vistas: cage (`IS_GEONODE_CAGE` ou `IS_FACE_FRAME_SPLIT_NODE`) e helper (`obj_x` ou nome contendo `Overlay Prompt Obj`); os filhos de cages continuam sendo percorridos. | `hb_layouts.py:950-960`, `:1752-1768` | 🟢 |
| HB_LAYOUTS-R18 | Câmeras de página são ORTHO, com localização/rotação travadas e `hide_select`, e viram `scene.camera`. | `hb_layouts.py:1357-1377` | 🟢 |
| HB_LAYOUTS-R19 | Enquadramento da elevação: bbox local da parede `[0,L]×[0,H]` ∪ bound_box de filhos MESH ∪ cotas (±0,1 m em X, ±0,25 m em Z); margem = 10% do maior lado em cada eixo; câmera a 3 m à frente (y=−3 local); `ortho_scale = max(w, h)`. | `hb_layouts.py:1504-1578` | 🟢 |
| HB_LAYOUTS-R20 | `ElevationView.update` usa outra regra: câmera no centro da parede a y=−2, `ortho = max(L, H) + 0,4 m`, sem cotas/filhos e sem reconstruir collections. | `hb_layouts.py:1780-1801` | 🟢 |
| HB_LAYOUTS-R21 | Cotas automáticas: só filhos diretos da parede com cage FRAMELESS/FACE_FRAME; Z local > 1,2 m ⇒ superior; base/altos cotados em z = −4" com leader −4"; superiores em z = topo máx. + 4" com leader +4"; cota 2" à frente da parede; comprimento = `Dim X` do cage; objeto renomeado `Dim_<cage>` com `IS_2D_ANNOTATION`. | `hb_layouts.py:1580-1679` | 🟢 |
| HB_LAYOUTS-R22 | Conteúdo da elevação: collection própria para a parede; por gabinete (FRAMELESS, FACE_FRAME ou CLOSET_STARTER) collections Solid/Dashed com peças `IS_*_INTERIOR_PART` em Dashed; Dashed vazia é removida; demais filhos vão para a collection da parede. | `hb_layouts.py:1681-1734` | 🟢 |
| HB_LAYOUTS-R23 | Planta: paredes `IS_WALL_BP` da cena de origem (ou de todo o arquivo); bbox só pelos pontos inicial/final (ignora espessura e gabinetes); câmera a z=5 olhando −Z; `ortho = max(w, h) + 1 m`; sem paredes → centro (0,0,5), ortho 10. | `hb_layouts.py:1840-1878` | 🟢 |
| HB_LAYOUTS-R24 | Vista 3D: alvo = média dos centros das paredes; câmera em alvo + (8, −8, 8); PERSP lente 35 mm ou ORTHO escala 10; rotação por `to_track_quat('-Z','Y')`. Não chama `create_camera` (câmera não travada). | `hb_layouts.py:2023-2062` | 🟢 |
| HB_LAYOUTS-R25 | MultiView em cruz: Front em (0,0); Plan acima (gap), Back acima do Plan, Left/Right laterais; gap 12"; `ortho = max(W, H) + 2·6"`; câmera a z=10 com `scale = ortho_scale`. Rotações: PLAN (0,0,0), FRONT (−90°,0,0), BACK (90°,0,180°), LEFT (0,−90°,−90°), RIGHT (0,90°,90°). | `hb_layouts.py:2181-2188`, `:2272-2375`, `:2869-2919` | 🟢 |
| HB_LAYOUTS-R26 | Instâncias da multivista cancelam a rotação de mundo da origem: `rot = Euler(base) @ R_origem⁻¹`; `loc = pos_base − rot @ loc_origem` (via `matrix_world.decompose`). | `hb_layouts.py:2266-2339` | 🟢 |
| HB_LAYOUTS-R27 | Linhas ocultas da multivista: peças internas são MOVIDAS do conteúdo sólido para `<view> Content Dashed` somente se a abertura de face frame ancestral tiver `front_type ≠ 'NONE'` (sem abertura, p.ex. frameless, considera-se oculta); instância tracejada só em células de elevação (não PLAN/ISO). | `hb_layouts.py:2690-2783`, `:2340-2343` | 🟢 |
| HB_LAYOUTS-R28 | Prancha iso-left: iso com θ=−60° (Rx 30° @ Rz −45° no referencial da câmera +Y); escala = maior de `1/2", 3/8", 1/4", 3/16", 1/8"=1'` que caiba na área (margens 0,5" e base 1,5"), senão 1/8"=1'; gaps iso 1" e planta 0,5" (em papel); elevação ancorada na borda direita/inferior; grava `hb_paper_size`, `hb_paper_landscape`, `hb_layout_scale`. | `hb_layouts.py:2484-2668` | 🟢 |
| HB_LAYOUTS-R29 | Bbox recursivo (espaço local da origem, depsgraph avaliado) ignora anotações `IS_2D_ANNOTATION`, cages, helpers e EMPTYs; sem geometria → `(0, dimensions)` ou `(0, (1,1,1))`. | `hb_layouts.py:2785-2840` | 🟢 |
| HB_LAYOUTS-R30 | Dimensões do objeto da multivista = `Dim X/Y/Z` do cage; fallback `obj.dimensions`, depois (1,1,1). | `hb_layouts.py:2842-2858` | 🟢 |
| HB_LAYOUTS-R31 | Title block: `camera.scale = ortho_scale` para coordenadas normalizadas; retângulo-âncora `GeoNodeRectangle` (1 × 1/aspecto) oculto; 4 textos (Project Name, Designer Name, Scale, Page Number) com placeholders em inglês, tamanho 0,015, espaçados 0,5"; todos na collection IGNORE. | `hb_layouts.py:983-1066` | 🟢 |
| HB_LAYOUTS-R32 | `TitleBlock.update` só reconhece objetos cujo nome contém `view_name` ou `scale` (minúsculas) — nenhum campo criado casa (`..._Scale`), e a lista `text_objects` é vazia em instâncias novas; efetivamente inoperante. | `hb_layouts.py:1100-1107` | 🟡 |
| HB_LAYOUTS-R33 | Detalhe 2D: nome único com sufixo numérico; estado de vista salvo se a cena de origem for sala; viewport top-down SOLID/OBJECT. | `hb_details.py:44-100` | 🟢 |
| HB_LAYOUTS-R34 | Primitivas: linha e círculo pretos com `bevel_depth` 0,002; polilinha usa `annotation_line_thickness/color` da cena; círculo com 32 segmentos POLY cíclico; texto `extrude` 0,001, tamanho padrão 0,05, alinhado LEFT/BOTTOM; tags `IS_DETAIL_*` + `IS_2D_ANNOTATION`; pontos da polilinha convertidos mundo→local. | `hb_details.py:107-439` | 🟢 |
| HB_LAYOUTS-R35 | Fonte de rótulo: `home_builder.annotation_font` > Calibri de `%WINDIR%`/`%LOCALAPPDATA%` (carregada com `check_existing`) > Bfont padrão; cor `annotation_text_color` aplicada ao objeto e ao material compartilhado `HB Label Text`. | `hb_details.py:308-381` | 🟢 |
| HB_LAYOUTS-R36 | Salvar detalhe exige cena `IS_DETAIL_VIEW` ou `IS_CROWN_DETAIL` e ≥1 objeto CURVE/FONT/MESH; arquivo `<nome sanitizado [^a-zA-Z0-9_-]→_>_<AAAAMMDD_HHMMSS>.blend` gravado com objetos + dados + materiais e `fake_user`; tipo `crown` ou `detail`. | `hb_detail_library.py:46-129` | 🟢 |
| HB_LAYOUTS-R37 | Listagem descarta entradas cujo arquivo não existe e recalcula `filepath` a partir da pasta atual; filtro opcional por `detail_type` (padrão `detail`). | `hb_detail_library.py:132-159` | 🟢 |
| HB_LAYOUTS-R38 | Excluir detalhe apaga o arquivo se existir e filtra o índice por `filename`; sempre retorna sucesso. | `hb_detail_library.py:225-243` | 🟢 |
| HB_LAYOUTS-R39 | Biblioteca embutida "Home Builder" → `blendertomob/assets`; bibliotecas do usuário nomeadas `HB: <nome> [<internal_id>]` (id = 12 hex de uuid4); `import_method='APPEND'`; bibliotecas `HB: ` sem tag ou com id desconhecido são removidas; "Home Builder Extended" legado removido. | `hb_assets.py:5-6`, `:83-220` | 🟢 |
| HB_LAYOUTS-R40 | Caminhos de conteúdo por subpasta: embutido primeiro, depois `<lib_usuário>/<subpasta>` existentes, sem duplicatas (convenção `moldings/`, `cabinet_pulls/`, `cabinet_groups/`). | `hb_assets.py:37-62` | 🟢 |
| HB_LAYOUTS-R41 | Catálogos: `blender_assets.cats.txt` lido como `uuid:caminho[:nome]`, ignorando vazias, `#` e `VERSION`; atribuir catálogo aplica o UUID a todos os objects/materials/collections marcados como asset no arquivo. | `hb_assets.py:65-80`, `:342-394` | 🟢 |
| HB_LAYOUTS-R42 | Asset shelf "home_builder" visível apenas no modo OBJECT e para assets OBJECT/COLLECTION/MATERIAL; prévia 96 px. | `hb_assets.py:323-339` | 🟢 |

### Constantes/enums

| Nome | Valor | Local | Conf. |
|---|---|---|---|
| `PAPER_SIZES` | LETTER, LEGAL, TABLOID, A4, A3 (pol.) | `hb_layouts.py:12` | 🟢 |
| `DEFAULT_DPI` | 150 | `hb_layouts.py:21` | 🟢 |
| `LINE_ENGINE_FREESTYLE` / `LINE_ENGINE_LINEART` / `LINE_ENGINE_PROP` | `'FREESTYLE'` / `'LINEART'` / `'HB_LINE_ENGINE'` | `hb_layouts.py:58-60` | 🟢 |
| `LINEART_OBJECT_TAG`, `LINEART_CAMERA_TAG`, `LINEART_MARKED_TAG`, `LINEART_BAKED_PROP` | `IS_HB_LINEART`, `IS_HB_LINEART_CAMERA`, `IS_HB_LINEART_MARKED`, `HB_LINEART_BAKED` | `:64`, `:67`, `:96`, `:126` | 🟢 |
| `LINEART_CAMERA_JITTER_DEG` | 0,05 | `:75` | 🟢 |
| `LINEART_SOLID_WIDTH_PAPER` / `DASHED` / `SAMPLE` | 0,010 / 0,0067 / 0,025 pol. | `:80-85` | 🟢 |
| `LINEART_DASH_POINTS` / `LINEART_GAP_POINTS` | 3 / 2 | `:86-87` | 🟢 |
| `LINEART_MARKED_SUFFIX`, `LINEART_MARKED_PART_KEYWORDS`, `LINEART_MARKED_LEVEL_END`, `LINEART_MARKED_LIFT` | `' LA-Marked'`, (Rail, Stile, Door (, Blind Panel, Drawer Front), 2, 0,001 m | `:97-121` | 🟢 |
| `ISO_CELL_PREFIXES` / `LINEART_MARKED_SKIP_PREFIXES` | ('Isometric', 'Iso ') | `:110`, `:115` | 🟢 |
| `LINEART_HOLDOUT_LAYER` | `'Holdout'` | `:129` | 🟢 |
| `_EMISSION_COPY_SUFFIX` | `' LAEmit'` | `:518` | 🟢 |
| `MultiView.VIEW_TYPES` | PLAN, FRONT, BACK, LEFT, RIGHT, ISO (rótulo + Euler) | `:2181` | 🟢 |
| Tags de cena | `IS_LAYOUT_VIEW`, `IS_ELEVATION_VIEW`, `IS_PLAN_VIEW`, `IS_3D_VIEW`, `IS_MULTI_VIEW`, `IS_DETAIL_VIEW`, `IS_CROWN_DETAIL`, `SOURCE_WALL`, `SOURCE_OBJECT`, `CONTENT_COLLECTION` | vários | 🟢 |
| Tags de objeto lidas | `IS_WALL_BP`, `IS_GEONODE_CAGE`, `IS_FACE_FRAME_SPLIT_NODE`, `obj_x`, `IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_CLOSET_STARTER_CAGE`, `IS_FRAMELESS_INTERIOR_PART`, `IS_FACE_FRAME_INTERIOR_PART`, `IS_FACE_FRAME_OPENING_CAGE`, `IS_2D_ANNOTATION` | vários | 🟢 |
| `GeoNodeCircle.SEGMENTS` | 32 | `hb_details.py:233` | 🟢 |
| `_LABEL_MAT_NAME` | `'HB Label Text'` | `hb_details.py:308` | 🟢 |
| `BUNDLED_LIBRARY_NAME` / `USER_LIBRARY_PREFIX` | `'Home Builder'` / `'HB: '` | `hb_assets.py:5-6` | 🟢 |
| Limiar de gabinete superior | 1,2 m | `hb_layouts.py:1614` | 🟢 |
| Escada de escalas iso-left | 1/2", 3/8", 1/4", 3/16", 1/8" = 1' | `hb_layouts.py:2524` | 🟢 |

### Riscos Blender 5.2

| Risco | Local | Conf. |
|---|---|---|
| `Material.use_nodes = True` está obsoleto desde 5.0 (sem efeito, remoção prevista em 6.0) — ver `docs/rag/blender-api/corpus/bpy.types.Material.md#bpy.types.Material.use_nodes`. | `hb_layouts.py:1091`, `:2947`; `hb_details.py:133`, `:189`, `:266`, `:376` | 🟢 |
| `AssetShelf.asset_poll(asset)` pode receber `None` (`bpy.types.AssetShelf.md#bpy.types.AssetShelf.asset_poll`); `asset.id_type` sem guarda levantaria `AttributeError`. | `hb_assets.py:334-335` | 🟢 |
| `register/unregister` de `hb_assets` testam `hasattr(bpy.types, cls.__name__)`: para operadores o nome RNA é `HOME_BUILDER_OT_*`, não `HB_OT_*`, então o desregistro dos 4 operadores é pulado e exceções de registro são engolidas (vazamento em recarga). | `hb_assets.py:408-428` | 🟡 |
| Dependência de contexto de janela/UI: `bpy.context.window.scene = …` (`hb_layouts.py:1164`, `hb_details.py:61`), `bpy.context.screen.areas` (`hb_details.py:94`), `bpy.ops.object.select_all` (`hb_detail_library.py:198`) e `bpy.ops.grease_pencil.layer_mask_add` com `temp_override` (`hb_layouts.py:695-698`) falham em `--background` (o último silenciosamente). | citados | 🟢 |
| `TitleBlock._add_text_field` atribui `get_font()` que retorna `None` se "Calibri Regular" não estiver carregada; atribuir `None` a `TextCurve.font` pode ser rejeitado. | `hb_layouts.py:44-48`, `:1085` | 🟡 |
| API GP v3: `layer.frames.remove` tem fallback por `TypeError` (assinatura variou entre versões); `drawing.add_strokes`, modificadores `LINEART`/`GREASE_PENCIL_SIMPLIFY`/`GREASE_PENCIL_DASH` — `check_api.py` não aponta símbolos desconhecidos. | `hb_layouts.py:244-252` | 🟢 |
| IDProperties em cenas/objetos (`scene['PAPER_SIZE']`, `obj['IS_…']`) são legítimas (não são `bpy.props`); `bpy.props` de cena são lidas por `getattr` (`hb_layout_scale`, `hb_lineart_*`) — conforme regra do projeto. | `hb_layouts.py:488-491` | 🟢 |
| Entradas de Geometry Nodes passam por `GeoNodeObject.get_input/set_input` → `hb_utils.get/set_gn_input` (sem `mod["Socket_X"]`). | `hb_types.py:325-362` | 🟢 |
| Operadores `home_builder.*_asset_library` sem `bl_options` (alteram preferências, não o arquivo — desfazer não se aplica); `bl_idname` fora do padrão `btm.*` (legado). | `hb_assets.py:280-320` | 🟢 |
| Caminho de dados do usuário usa corretamente `bpy.utils.extension_path_user(__package__, path="detail_library", create=True)`. | `hb_detail_library.py:16` | 🟢 |

### Dependências de outros módulos

- `hb_types`: `GeoNodeWall`, `GeoNodeCage`, `GeoNodeObject`, `GeoNodeRectangle`, `GeoNodeDimension` (entradas GN, `var_input`). 🟢
- `units`: `units.inch`. 🟢
- `operators/layouts.py`: `paper_to_world`, `PAPER_SIZES_INCHES` (import tardio — dependência circular), propriedades de cena `hb_layout_scale`, `hb_paper_size`, `hb_paper_landscape`, `hb_lineart_*` registradas lá (`:4665-4718`). 🟢
- `hb_utils`: `is_room_scene`, `save_view_state`, `set_top_down_view` (via `hb_details`); `get/set_gn_input` via `hb_types`. 🟢
- `hb_props` (`Scene.home_builder`): `product_tab`, `annotation_font`, `annotation_text_color`, `annotation_line_thickness`, `annotation_line_color`; `Object.home_builder.mod_name`; `face_frame_opening.front_type`. 🟢
- Preferências do add-on (`blendertomob/__init__.py`): `line_engine`, `asset_libraries`, `asset_libraries_index`. 🟢
- Consumidores: `operators/layouts.py`, `operators/details.py`, `ui/view3d_sidebar.py`, bibliotecas `frameless`/`face_frame`. 🟢

### Lacunas

- 🔴 `setup_iso_freestyle`, `build_line_art_marked_channel`, `build_line_art_text_holdouts`, `scene_uses_iso_freestyle`,
  `get_iso_freestyle_collections` não têm chamador no pacote; o exportador híbrido (OpenGL GP + F12 Freestyle) citado
  nas docstrings não foi localizado.
- 🔴 Docstring de `hb_detail_library` promete miniaturas embutidas; nenhum código de miniatura existe.
- 🔴 Preenchimento real dos campos do title block (nome do projeto, designer, numeração "PAGE 1 OF 12" fixa) não ocorre
  neste módulo.
- 🟡 `LayoutView.delete` remove apenas a cena: collections de conteúdo/roteamento, câmera e GP ficam órfãos.
- 🟡 Código morto: `PlanView._fit_camera_to_content` e `View3D._fit_camera_to_content` (cópias da lógica de elevação em
  eixo Z, nunca chamadas), `MultiView._calculate_grid`, `MultiView._create_view_label`.
- 🟡 Escada de escalas do iso-left é só imperial, enquanto o fork adota escalas métricas por padrão (`1:50`).
- 🟡 `ortho_scale = max(w, h)` ignora a razão de aspecto do papel na elevação/planta; conteúdo alto em papel paisagem
  pode ser cortado.
- 🟡 `create_all_elevations` percorre `bpy.data.objects` (todas as salas), não a cena atual.
- 🟡 `load_detail_from_library` calcula um conjunto de nomes existentes e o descarta (`hb_detail_library.py:181`).

---

## Módulo frameless

> Camada legada (fork do Home Builder 5). Pacote `blendertomob/product_libraries/frameless/` — 26 arquivos `.py`, ~23 mil linhas.
> Legenda: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas: `_reversa_sdd/flowcharts/legacy-frameless*.md`. Mapeamento arquivo→responsabilidade: `_reversa_sdd/frameless/legacy-mapping.md`.

### Propósito

Biblioteca paramétrica de marcenaria **sem quadro frontal** (frameless/europeia): gera gabinetes inferiores, aéreos,
altos, de canto (pie-cut e diagonal), gaveteiro "lap drawer", gabinete de geladeira e produtos avulsos (prateleira
flutuante, sanca/valance, estrutura de apoio, meia-parede, pernas, painéis, peça avulsa). Cada gabinete é uma
hierarquia de objetos Blender com modificador Geometry Nodes ("cage"/"cutpart"), cujas medidas são **drivers**
sobre prompts (ID properties) do objeto raiz. O módulo também cuida de: frentes (portas, gavetas, basculantes,
frentes falsas), overlays, interiores (prateleiras, divisores), puxadores, estilos de gabinete (madeira/cor/interior/
fita de borda/overlay) e de porta (lisa/5 peças), bancadas, molduras extrudadas (crown, rodapé decorativo, moldura
inferior de aéreo), templates de elevação e biblioteca do usuário. 🟢

### Arquivos

| Arquivo | Linhas | Papel |
|---|---|---|
| `types_frameless.py` | 2921 | Tipos de gabinete/aberturas/frentes/interiores/cantos 🟢 |
| `types_products.py` | 938 | Produtos não-gabinete 🟢 |
| `props_hb_frameless.py` | 2574 | `Scene.hb_frameless`, estilos, puxadores, detalhes, UI 🟢 |
| `props_elevation_templates.py` | 1576 | Templates "Refrigerator Range" e "Island" 🟢 |
| `wood_materials.py` / `finish_colors.py` | 228 / 294 | Shader de madeira por espécie; catálogo de cores + JSON do usuário 🟢 |
| `menus_frameless.py` | 416 | Menus de contexto por nível 🟢 |
| `operators/*.py` (17) | ~14,6 mil | placement, cabinet, opening, interior, front, appliance, styles, crown, toe_kick, upper_bottom, library, defaults, finished_ends, products, countertop, cleanup, snap_line 🟢 |

### Fluxo de controle

1. **Registro** 🟢 — `frameless/__init__.py:10-14`: props → templates → 17 módulos de operadores → menus. `Frameless_Scene_Props.register` cria `bpy.types.Scene.hb_frameless` (`props_hb_frameless.py:2507-2513`); templates criam `Scene.hb_template_refrigerator_range` e `Scene.hb_template_island` (`props_elevation_templates.py:1558-1565`). Vários `register()` engolem exceções (`props_hb_frameless.py:2537-2548`, `ops_placement.py:1986-1997`).
2. **Inserção** 🟢 — UI de biblioteca (`draw_cabinet_library_ui` `:1889`) → `hb_frameless.draw_cabinet(cabinet_name)` (`ops_placement.py:1927`) → `hb_frameless.place_cabinet` modal (`:270`). No modal: raycast → parede (ou parede mais próxima ≤6in) → gap livre por lado → preenchimento automático com N gabinetes ≤36in, snap de centro/borda/janela; ou piso com snap a gabinete vizinho. Confirmação → `get_cabinet_class()` (`:1455`) → `create()` → `assign_cabinet_style` → `run_calc_fix` ×2 → estilos de porta → quantidade de prateleiras → `toggle_mode`.
3. **Construção paramétrica** 🟢 — `Cabinet.create_cabinet` (`types_frameless.py:114`) cria a cage; `create_base_carcass`/`create_tall_carcass`/`create_upper_carcass` criam peças `CabinetPart` com `driver_input`/`driver_location`/`driver_hide`; `add_cage_to_bay` (`:52`) insere a abertura no `Bay`. Aberturas compostas usam `SplitterVertical/Horizontal` com calculadora de vãos (`hb_props.Calculator.calculate`).
4. **Edição** 🟢 — menus por `MENU_ID` gravado em cada objeto (ex.: `HOME_BUILDER_MT_cabinet_commands`); `change_bay_opening` apaga os filhos do Bay e recria (30 configurações, `ops_opening.py:98-141`); prompts via `invoke_props_dialog` que alteram dados em `check()` (ex.: `ops_cabinet.py:52-94`).
5. **Estilos** 🟢 — `Frameless_Cabinet_Style.assign_style_to_cabinet` (`props_hb_frameless.py:693`) atribui materiais por face (`Finish Top/Bottom`), fita de borda, materiais dos modificadores CPM e flags de overlay; `Frameless_Door_Style.assign_style_to_front` (`:1044`) adiciona/remove modificador `CPM_5PIECEDOOR`. Atualização em lote por timer modal (`ops_styles.py:673-789`).
6. **Pós-processamento** 🟢 — bancadas (`ops_countertop.py:614`), crown/rodapé/moldura inferior (extrusão de perfil 2D desenhado numa cena de detalhe), laterais acabadas (`ops_cabinet.py:175`, `ops_finished_ends.py:58`), linhas de snap, limpeza de malha BMesh.
7. **Templates de elevação** 🟢 — seleciona parede → preview de cages rotuladas atualizadas por callbacks `update=` → `draw_cabinets` cria gabinetes reais e aplica estilos (`props_elevation_templates.py:566`, `:1136`).

Tratamento de erros: predominantemente `report({'WARNING'|'ERROR'})` + `CANCELLED`; muitos `try/except Exception: pass` silenciosos (ex.: `props_hb_frameless.py:1136-1143`, registro de classes). 🟢

### Algoritmos e regras

Unidades: todo valor é armazenado em **metros**; os padrões são escritos em polegadas via `units.inch()`. Abaixo, `mt` = espessura da chapa (prompt `Material Thickness`), `tkh`/`tks` = altura/recuo do rodapé.

| ID | Regra | Local | Conf. |
|---|---|---|---|
| FRAMELESS-R01 | Construção de laterais passantes: base, fundo, tampo, rodapé e travessas medem `dim_x − 2·mt` e ficam entre as laterais. | `types_frameless.py:198, 214, 226, 241` | 🟢 |
| FRAMELESS-R02 | Fundo com espessura `mt` (chapa cheia), embutido entre laterais; base: `z = tkh+mt`, `L = dim_z − tkh − mt`; alto desconta mais `mt` (tampo cobre o fundo). Sem canal para fundo fino. | `:206-216`, `:401` | 🟢 |
| FRAMELESS-R03 | Tipo de rodapé (COMBOBOX 0..3): 0 = laterais entalhadas até o piso (CPM_CORNERNOTCH X=tkh, Y=tks, profundidade mt) + painel de rodapé em `y=−dim_y+tks`; 1 = base tipo escada (placeholder); 2 = flutuante; 3 = 4 niveladores com inset `lli`. Nos tipos 1–3 as laterais começam em `z=tkh`. | `:147-190, :218-231, :302-313, :1622-1634` | 🟢 |
| FRAMELESS-R04 | O tipo de rodapé só é aplicado na criação (`obj.get('Toe Kick Type')` lido uma vez); alterá-lo depois não reconstrói a geometria. | `:144`, `ops_defaults.py:19-26` | 🟡 |
| FRAMELESS-R05 | Construção do topo do inferior: 0 = tampo inteiro (`W = dim_y − mt`, recuado do fundo); 1 = duas travessas de 4in (frente em `−dim_y`, trás em `−sw−mt`); 2 = avental de pia vertical de 7in. Visibilidade por `driver_hide`. Enum da cena só oferece Stretchers/Full Top (padrão Stretchers). | `:233-289`, `props_hb_frameless.py:1584-1587` | 🟢 |
| FRAMELESS-R06 | Vão (Bay) do inferior: origem `(mt, −dim_y, tkh + IF(rb,0,mt))`, dimensões `(dim_x−2mt, dim_y−mt, dim_z−tkh−IF(rb,0,mt)−mt)`; aéreo: `(dim_x−2mt, dim_y−mt, dim_z−2mt)`. Profundidade do vão desconta o fundo. | `:292-300`, `:527-535` | 🟢 |
| FRAMELESS-R07 | "Remove Bottom" (rb) oculta base e rodapé e faz o fundo descer até z=0. | `:203, :212-213, :231` | 🟢 |
| FRAMELESS-R08 | Lap Drawer: altura = `top_drawer_front_height` (6in); `z = base_cabinet_height − altura` (topo alinhado ao inferior); sem rodapé. | `:630-654` | 🟢 |
| FRAMELESS-R09 | Gabinete de geladeira: carcaça alta com `Remove Bottom=True`, `Toe Kick Height=0`, splitter com vão inferior vazio de `refrigerator_height` (62in) e portas em cima (meia sobreposição inferior). Largura padrão 38in. | `:822-864`, `props_hb_frameless.py:1425-1435` | 🟢 |
| FRAMELESS-R10 | Exterior padrão do inferior por nome: "Base Door"→Doors, "Base Door Drw"→gaveta(6in)+porta, "Base Drawer"→3 gavetas; pilha de gavetas: topo = `top_drawer_front_height` ou igual se `equal_drawer_stack_heights`. | `ops_placement.py:1488-1495`, `types_frameless.py:558-620` | 🟢 |
| FRAMELESS-R11 | Alto empilhado: porta inferior = `tall_cabinet_split_height` (54in); superior empilhado: porta de cima = `upper_top_stacked_cabinet_height` (15in). | `:802-814`, `:890-902` | 🟢 |
| FRAMELESS-R12 | Splitter: vãos = qtd+1; altura útil = `dim_z − mt·qtd`; tamanho 0 = rateio igual `(total − Σfixos)/n_iguais`; divisórias de cima para baixo em `z = anterior − oh − mt`. | `:918-1026`, `hb_props.py:294-330` | 🟢 |
| FRAMELESS-R13 | Vãos internos de splitter recebem `FORCE_HALF_OVERLAY_TOP` (i>1) e `_BOTTOM` (i≤qtd) (horizontal: LEFT/RIGHT), preservados ao aplicar estilo. | `:1014-1017, :1110-1113`, `props_hb_frameless.py:766-782` | 🟢 |
| FRAMELESS-R14 | Overlay por lado: inset → `−inset_reveal` (1/8in); meia → `(espessura − vertical_gap)/2`; total → `espessura − reveal` (reveal topo/laterais 1/16in, base 0). Calculado num empty separado para evitar ciclo de dependência. | `:1156-1210` | 🟢 |
| FRAMELESS-R15 | Porta: `x=−lo`, `z=−bo`, altura `dim_z+to+bo`, largura `dim_x+lo+ro` (simples) ou `(dim_x+lo+ro−vg)/2` (dupla); Y = `IF(inset, ft, −door_to_cab_gap)` (gap 1/8in, frente 3/4in). Door Swing 0/1/2 oculta porta oposta. | `:1296-1326` | 🟢 |
| FRAMELESS-R16 | Prateleiras reguláveis: array com `qty` cópias, 1ª em `(dim_z − mt·qty)/(qty+1)`, passo `+mt`; folga de clip 1/8in por lado; recuo frontal 1/4in. Interior recua `ft` quando inset. | `:1222-1264, :1330-1342` | 🟢 |
| FRAMELESS-R17 | Quantidade padrão de prateleiras: prof. ≤18in → 1 (≤20in alt), 2 (≤32), 3 (≤44), 4; prof. >18in → 1 (≤28), 2 (≤40), 3 (≤52), 4. | `ops_interior.py:7-37` | 🟢 |
| FRAMELESS-R18 | Caixa de gaveta: X = `largura_frente − lo − ro − 2·0.5in`; Y = `prof_vão − 1in`; Z = `altura_frente − to − bo − 0.75in − 0.5in`; só se `include_drawer_boxes` e não frente falsa. | `:1867-1926` | 🟢 |
| FRAMELESS-R19 | Puxador de porta: Base mede do topo da porta (`length − pvl_base − pull_len/2`, pvl 1.5in); Tall do pé ao centro (45in); Upper do pé (1.5in); horizontal a 2in da borda de abertura. Gaveta: centralizado por padrão. Comprimento default 4in sem objeto. | `:1747-1782, :1834-1862`, `props_hb_frameless.py:1625-1652` | 🟢 |
| FRAMELESS-R20 | Localização do puxador por posição no mundo após trocar vão: base do vão < 36in → Base; ≥ 48in → Upper; entre → Tall, salvo porta mais baixa que a altura Tall (então Base se < 42in, senão Upper). | `ops_opening.py:22-65` | 🟢 |
| FRAMELESS-R21 | Pull location por posição no splitter de alto: 1 vão → Tall; 2 → topo Upper/baixo Base; 3+ → topo Upper, meio Tall, baixo Base. | `ops_opening.py:184-213` | 🟢 |
| FRAMELESS-R22 | Configurações de vão com tamanhos fixos: eletro embutido 30in central; duplo eletro 2×30in + gaveta 6in; micro-ondas + gaveta 6in; portas + basculante 8in; portas 18in + tall pullout. | `ops_opening.py:275, :308, :442, :499, :524` | 🟢 |
| FRAMELESS-R23 | Canto (pie-cut): cage em L com `Left Depth`/`Right Depth` (= profundidade do tipo); tampo/base com CPM_CORNERNOTCH `X = dim_x − ld − mt`, `Y = dim_y − rd − mt`; dois fundos; dois rodapés; duas portas articuladas no canto, larguras distintas para inset/overlay. Diagonal usa CPM_CHAMFER. | `types_frameless.py:2280-2921` | 🟢 |
| FRAMELESS-R24 | Canto: tamanho padrão 36in (base/alto) e 24in (aéreo); ao inserir, se o cursor está a menos de uma largura da ponta da parede, encosta na ponta (direita com rotação −90°). | `props_hb_frameless.py:1482-1498`, `ops_placement.py:1270-1307` | 🟢 |
| FRAMELESS-R25 | Estilo de porta 5 peças: mínimo `2·stile + 1in` de largura e `2·rail + 1in` (+ mid rail) de altura; portas > 45.5in ganham travessa intermediária centralizada automaticamente; stiles usam material com veio vertical, rails o material ROTATED. | `props_hb_frameless.py:1064-1162` | 🟢 |
| FRAMELESS-R26 | Material por face: peças com `Finish Top/Bottom` recebem acabamento, demais o interior; `Finished Interior` força acabamento em tudo; frentes têm ambos True; prateleiras/travessas ambos False; `CabinetPart` padrão = Top False / Bottom True. | `props_hb_frameless.py:716-736`, `types_frameless.py:1600-1602, 1644-1645` | 🟢 |
| FRAMELESS-R27 | Fita de borda = material customizado se `edge_banding=CUSTOM`, senão acabamento ROTATED; aplicada às 4 bordas (W1, W2, L1, L2) de toda peça. | `props_hb_frameless.py:700-736` | 🟢 |
| FRAMELESS-R28 | Material de acabamento: node group "Wood" de `cabinet_material.blend`; par normal/ROTATED com rotação Z 90°/0°; parâmetros de grão por espécie (Maple, Oak, Cherry, Walnut, Birch, Hickory, Alder); PAINT_GRADE zera o grão e usa cor de tinta. | `props_hb_frameless.py:636-669`, `wood_materials.py:22-168` | 🟢 |
| FRAMELESS-R29 | Estilo do gabinete é vinculado por **índice** (`CABINET_STYLE_INDEX`); remover estilo reatribui 0 aos que usavam o removido e decrementa índices maiores. | `ops_styles.py:376-422` | 🟢 |
| FRAMELESS-R30 | Alturas derivadas: `tall_cabinet_height = ceiling − top_clearance`; `upper_cabinet_height = ceiling − top_clearance − wall_cabinet_location` (callback de update). | `props_hb_frameless.py:426-434` | 🟢 |
| FRAMELESS-R31 | Inserção: largura máxima por gabinete 36in no preenchimento automático (`qtd = ceil(gap/36in)`), snap de centro 4in, parede ≤6in, histerese de lado 1in. | `ops_placement.py:1057-1063, 1085, 1182, 1262, 1690` | 🟢 |
| FRAMELESS-R32 | Z de inserção: aéreo em 54in; coifa em 54in com altura até o teto; Support Frame com topo no topo do inferior; prateleira flutuante/valance seguem o cursor em Z (arredondado a polegada inteira). | `ops_placement.py:464-505, 1166-1169` | 🟢 |
| FRAMELESS-R33 | Bancada: espessura 1.5in, balanço frontal 1in, lateral 1in (suprimido em ponta ligada a parede conectada ou a alto adjacente ±5 mm), traseiro 0; corta nos fogões (APPLIANCE_TYPE=RANGE); L nos cantos. Malha estática. | `ops_countertop.py:235-482`, `props_hb_frameless.py:1680-1698` | 🟢 |
| FRAMELESS-R34 | Crown só em UPPER/TALL; rodapé decorativo só em BASE/TALL; agrupamento por adjacência (±2 cm, topos alinhados); pontas: parede → encosta; vizinho não selecionado → morre nele (degrau UPPER→TALL); exposta → retorno em esquadria. | `ops_crown.py:342-1288`, `ops_toe_kick.py:259-678` | 🟢 |
| FRAMELESS-R35 | Lateral aplicada (applied end): altura total do gabinete a partir do piso, profundidade `dim_y + 0.875in` (gap 1/8 + frente 3/4) — constante embutida na expressão do driver, não ligada aos prompts. 5 peças: largura `dim_y − 0.75in`, opcional até o piso. | `ops_cabinet.py:215-262`, `ops_finished_ends.py:148, 238` | 🟢 |
| FRAMELESS-R36 | "Drop to countertop": aéreo desce até `base_cabinet_height + countertop_thickness` mantendo o topo. | `ops_cabinet.py:152-172` | 🟢 |
| FRAMELESS-R37 | Support Frame: travessas internas em array a cada 16in: `count = floor((dim_x − 2mt − ss)/ss)+1`; pernas 3.5×3.5in, altura 34.5in, tipo Inset/Wrapped. | `types_products.py:253-447` | 🟢 |
| FRAMELESS-R38 | Meia-parede: montantes a cada 16in, `count = floor((dim_x − 2mt − 2·1.5in)/ssp)+1`, pele 1/4in, montante 3/4in. | `types_products.py:449-604` | 🟢 |
| FRAMELESS-R39 | Prateleira flutuante: caixa oca (frente, tampo, base, laterais opcionais), rasgo de LED opcional (largura 1/2in, inset 2in, profundidade 1/4in) via CPM_CUTOUT. | `types_products.py:36-154` | 🟢 |
| FRAMELESS-R40 | Pernas (Leg/TallLeg/UpperLeg): frente + rodapé (se tkh>0) + painéis entalhados; "Override Panel Depth" 0 = profundidade total; Finish Type Left/Right/Both. | `types_products.py:633-902` | 🟢 |
| FRAMELESS-R41 | Template Refrigerator/Range: ordem de ocupação pantry → geladeira → inferiores (divididos em torno do fogão central) → aéreos; larguras = área disponível / quantidade (1–6). | `props_elevation_templates.py:566-775` | 🟢 |
| FRAMELESS-R42 | Template Island: gabinetes girados 180°, a `offset_from_wall` (72in) da parede, não parentados; pia central (BaseCabinet comum) e lava-louças à esquerda/direita subtraindo da largura lateral. | `props_elevation_templates.py:1136-1284` | 🟢 |
| FRAMELESS-R43 | Drawer boxes podem ser incluídas/removidas globalmente (callback percorre a cena e apaga/cria `IS_DRAWER_BOX`). | `props_hb_frameless.py:436-450` | 🟢 |
| FRAMELESS-R44 | Cores do usuário persistem em `extension_path_user(.../user_data/custom_colors.json)`; mesmo nome sobrescreve cor padrão. | `finish_colors.py:21-27, 175-225` | 🟢 |
| FRAMELESS-R45 | Grupo de gabinetes salvo com `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)` + thumbnail 256px Workbench/Freestyle. | `ops_library.py:99-300` | 🟢 |

Algoritmos notáveis 🟢: (a) rateio de vãos por calculadora (`hb_props.Calculator.calculate`); (b) busca de gap e preenchimento automático (`set_position_on_wall`); (c) corridas de parede conectadas para bancada (`build_wall_runs`) e L de canto; (d) offset de polilinha com esquadria por interseção de retas (`_offset_polyline_right`, `ops_crown.py:835-871`) e componentes conexos por AABB (`_connected_components`); (e) extrusão de perfil via `bevel_object` em curva POLY 2D.

### Constantes/enums

- Tipos de gabinete (`CABINET_TYPE`): `BASE`, `TALL`, `UPPER`; `CORNER_TYPE`: `DIAGONAL`, `PIECUT`. 🟢
- Rodapé: `Notch Ends to Floor`(0), `Ladder Style`(1), `Floating`(2), `Leg Levelers`(3). 🟢 `types_frameless.py:23-28`
- Topo do inferior: `Full Top`(0), `Stretchers`(1), `Sink`(2). 🟢 `:48`
- Door Swing: `Left`(0), `Right`(1), `Double`(2); Pull Location: `Base`(0), `Tall`(1), `Upper`(2). 🟢
- `base_exterior`: Doors, Door Drawer, 2/3/4 Drawers, Open (não usado). 🟢 `props_hb_frameless.py:1391-1398`
- `frameless_selection_mode`: Cabinets, Bays, Openings, Interiors, Parts → marcadores `IS_FRAMELESS_CABINET_CAGE`, `_BAY_CAGE`, `_OPENING_CAGE`, `_INTERIOR_PART`, `NO_TYPE`. 🟢 `ops_placement.py:1902-1913`
- `wood_species`: MAPLE, OAK, CHERRY, WALNUT, BIRCH, HICKORY, ALDER, PAINT_GRADE, CUSTOM_PROCEDURAL, CUSTOM; `interior_material_type`: MAPLE_PLY ("UV Plywood"), MATCHING, CUSTOM; `door_overlay_type`: FULL, HALF, INSET; `edge_banding`: MATCHING, CUSTOM. 🟢
- `door_type`: SLAB, 5_PIECE; `panel_material`: MATCH_CABINET, GLASS; `edge_profile_type`: SQUARE, EASED, OGEE, BEVEL, ROUNDOVER (não aplicado na geometria — 🔴). 🟢
- 30 tipos de `change_bay_opening` (`ops_opening.py:98-141`). 🟢
- `PULL_FINISHES` (12 acabamentos metálicos), 15 cores tingidas e 12 cores de tinta padrão. 🟢
- Marcadores de objeto: `IS_FRAMELESS_CABINET_CAGE`, `IS_FRAMELESS_BAY_CAGE`, `IS_FRAMELESS_OPENING_CAGE`, `IS_FRAMELESS_INTERIOR_CAGE`, `IS_FRAMELESS_INTERIOR_PART`, `IS_FRAMELESS_SPLITTER_VERTICAL_CAGE/HORIZONTAL_CAGE`, `IS_FRAMELESS_PRODUCT_CAGE`, `IS_FRAMELESS_MISC_PART`, `CABINET_PART`, `IS_CABINET_FRONT`, `IS_DOOR_FRONT`, `IS_DRAWER_FRONT`, `IS_PULLOUT_FRONT`, `IS_FLIP_UP_DOOR`, `IS_CABINET_PULL`, `IS_DRAWER_BOX`, `IS_LEG_LEVELER`, `IS_CORNER_CABINET`, `IS_REFRIGERATOR_CABINET`, `IS_APPLIED_END_{LEFT,RIGHT,BACK}`, `IS_COUNTERTOP`, `IS_CROWN_MOLDING`, `IS_TOE_KICK_MOLDING`, `IS_UPPER_BOTTOM_MOLDING`, `IS_SNAP_LINE`, `IS_TEMPLATE_PREVIEW`, `FORCE_HALF_OVERLAY_*`, `MENU_ID`, `CABINET_STYLE_INDEX/NAME`, `DOOR_STYLE_INDEX/NAME`. 🟢

### Riscos Blender 5.2

| Risco | Local | Conf. |
|---|---|---|
| `Material.use_nodes = True` — obsoleto desde 5.0 (sem efeito, remoção prevista 6.0) (`docs/rag/blender-api/corpus/bpy.types.Material.md#bpy.types.Material.use_nodes`). Leitura `mat.use_nodes` em `_collect_data_blocks` sempre True. | `props_hb_frameless.py:269, 310`; `ops_snap_line.py:46`; `ops_library.py:227` | 🟢 |
| `Material.blend_method = 'BLEND'` — marcado "Deprecated: use surface_render_method" (`bpy.types.Material.md#bpy.types.Material.blend_method`). | `props_hb_frameless.py:313`; `ops_snap_line.py:53-54` | 🟢 |
| `EnumProperty(items=callback)` que devolve strings recém-criadas (f-strings, dados de JSON lido do disco a cada chamada) sem manter referência — limitação documentada (`04_armadilhas.md` §Callbacks). Também custo de I/O a cada redraw. | `props_hb_frameless.py:108-134, 476-499`; `finish_colors.py:207-225` | 🟢 |
| Callback `update=` que chama `bpy.ops` (`update_frameless_selection_mode` → `hb_frameless.toggle_mode`) — operador dentro de callback de propriedade (contexto/undo imprevisíveis). | `props_hb_frameless.py:455-456` | 🟢 |
| Referências a IDs/PropertyGroups guardadas em atributos do operador entre ticks de timer (`_style`, `_cabinets`) — invalidáveis por undo/redo. | `ops_styles.py:680-789` | 🟡 |
| Dados alterados em `check()` de diálogos (`invoke_props_dialog`) em vez de `execute()` — mudanças fora do passo de undo do operador. | `ops_cabinet.py:52-94`, `ops_interior.py:95-103`, `ops_appliance.py:31-35` | 🟡 |
| Operadores que alteram dados sem `bl_options={'UNDO'}`: `update_toe_kick_prompts`, `update_material_thickness_prompts`, `toggle_mode`, `draw_cabinet`, `create_cabinet_group`, `select_cabinet_group`. | `ops_defaults.py:4-35`; `ops_placement.py:1866-1932`; `ops_cabinet.py:412, 543` | 🟢 |
| `register()` com `try/except Exception: pass` esconde falhas de registro. | `props_hb_frameless.py:2537-2558`; `ops_placement.py:1986-2007` | 🟢 |
| Node group "Smooth by Angle" carregado de caminho interno `datafiles/assets/nodes/geometry_nodes_essentials.blend`; falha silenciosa se o arquivo mudar. | `ops_crown.py:1159-1170`; `ops_toe_kick.py`/`ops_upper_bottom.py` equivalentes | 🟡 |
| `UIList.draw_item` sem parâmetro `index` em `HB_UL_toe_kick_details` e `HB_UL_upper_bottom_details` (assinatura divergente das demais). | `props_hb_frameless.py:1262, 1288` | 🟡 |
| Leitura de propriedades "prompt" por `obj['...']`/`obj.get` é legítima (ID properties criadas por `home_builder.add_property`, `hb_props.py:335-374`), **não** bpy.props — não viola a regra do projeto. Nenhum `mod["Socket_X"]`, handler de aplicação, `draw_handler_add` ou thread encontrado no módulo. `check_api.py` sem símbolos desconhecidos. | grep no pacote | 🟢 |
| `BooleanModifier.solver = 'EXACT'` continua válido no 5.2. | `ops_countertop.py:727` | 🟢 |

### Unidades e premissas de mercado

- 🟢 Unidade interna metros; todos os padrões em **polegadas** (`units.inch`). Nomes de UI em inglês.
- 🟢 Espessura de chapa padrão 0.75in = **19,05 mm** (Brasil: MDF/MDP 15 ou 18 mm; fundo 3/6 mm). Frente 0.75in. Fundo usa a mesma espessura da caixa (sem fundo fino encaixado).
- 🟢 Medidas americanas: inferior 34.5in (876 mm) × prof. 23.125in (587 mm); alto 84in (2134 mm) × 25.5in; aéreo 30in × 13in (330 mm); largura padrão 36in; aéreo a 54in (1372 mm) do piso; folga do teto 12in; rodapé 4in × recuo 2.5in (Brasil típico ~100–150 mm × 50–70 mm, inferior total ~850–900 mm incl. tampo, prof. 550–600 mm).
- 🟢 Bancada 1.5in (38 mm) com balanço 1in; Brasil costuma granito 20–30 mm com saia e balanço 20–30 mm, cuba/cooktop por recorte.
- 🟢 Eletros em polegadas (geladeira 62in de altura / nicho 38in; fogão 36in; lava-louças 24in; coifa a 54in).
- 🟢 Gaveta: folgas laterais 0.5in (12,7 mm por lado) típicas de corrediça americana (side-mount); corrediças ocultas/telescópicas nacionais usam 12,5–13 mm por lado (compatível) ou valores do fabricante.
- 🟢 Cores/espécies americanas (Maple, Hickory, Alder; "UV Plywood"; nomes de tinta como "Agreeable Grey", "Iron Ore", "Tricorn Black" — nomes comerciais Sherwin-Williams) — não correspondem a padrões de MDF BP brasileiro (Duratex/Arauco/Guararapes).
- 🔴 Não há noção de chapa (2750×1830), veio/direção de corte nem otimização neste módulo — ficam a cargo do módulo de corte (`cutting`), que lê as `CabinetPart`.
- 🟡 Overlay total 11/16in (17,46 mm) sobre lateral de 19 mm; no Brasil, com lateral 15/18 mm e dobradiça reta, a sobreposição usual é espessura − 1,5 a 2 mm.

### Dependências de outros módulos

`hb_types` (GeoNodeCage/Cutpart/Hardware/DrawerBox/Wall/Dimension/Rectangle, CabinetPartModifier), `hb_props` (prompts, calculadora, `home_builder` object props), `hb_utils` (`run_calc_fix`, `set_gn_input`, `get_*_bp`, `delete_obj_and_children`), `hb_project.get_main_scene`, `hb_placement` + `hb_snap` (inserção modal), `hb_details` + `hb_detail_library` (cenas de detalhe), `hb_assets` (caminhos de bibliotecas), `units`, `product_libraries/common/types_appliances` (Range, Dishwasher, Refrigerator, Hood, Cooktop, WallOven, Microwave, Sink), operadores externos `home_builder_layouts.go_to_layout_view`, `home_builder_details.*`, `pc_prompts.*`. Assets: `frameless_assets/` (puxadores, niveladores, `cabinet_material.blend`), node groups `CPM_CORNERNOTCH`, `CPM_CHAMFER`, `CPM_CUTOUT`, `CPM_5PIECEDOOR`. 🟢

### Lacunas

- 🔴 `DiagonalCornerTallCabinet` e `DiagonalCornerUpperCabinet` são stubs (só a cage); `DiagonalCornerBaseCabinet` não tem portas (`create_corner_bays` vazio, `types_frameless.py:2318-2324`). UI diagonal comentada.
- 🔴 Ladder Style é só gaiola placeholder; rollouts (`_add_rollouts_to_section`) e TRAY_DIVIDERS não implementados (`:2160-2162, :2275-2277`).
- 🔴 `update_base_top_construction_prompts` e `update_drawer_front_height_prompts` são TODO (`ops_defaults.py:58-73`).
- 🔴 Propriedades de cena sem uso: `base_exterior`, `base_corner_type`, `upper_corner_type`, `upper_and_tall_corner_type`, `base/tall/upper_width_blind` (não existe gabinete "blind corner"), `show_machining` (callback só `print`), `range_hood_height`/`RAISE_UPPER` (não eleva), `edge_profile_type`, `outside_profile`/`inside_profile` (não usados na geometria).
- 🔴 `HalfWall`: tampo e base criados com nome "Right End" (`types_products.py:527, 541`); prompts de end cap/finished end/revel declarados mas não usados (`:466-496`).
- 🟡 `SplitterVertical.create` indexa `opening_sizes[i-1]` sem checar tamanho (`types_frameless.py:1021`).
- 🟡 Leitura mista de `bpy.context.scene.hb_frameless` (77 ocorrências) e `hb_project.get_main_scene().hb_frameless` (89): criar gabinetes numa cena de layout/detalhe usa os padrões da cena corrente, enquanto estilos vêm da cena principal.
- 🟡 Bancadas, crown, rodapé decorativo e moldura inferior são geometria estática — não se atualizam com o gabinete.
- 🟡 `ops_snap_line.create_snap_line_mesh` cria um material novo a cada linha (acúmulo de datablocks).
- 🟡 Thumbnail de grupo altera `film_transparent`/`use_freestyle`/`line_thickness` da cena sem restaurar (`ops_library.py:278-282`, `finally` em `:300-307` não os restaura).
- 🟡 Código triplicado de agrupamento/adjacência entre `ops_crown.py`, `ops_toe_kick.py` e `ops_upper_bottom.py`.

---

## Módulo face_frame

> Camada legada (fork Home Builder 5). Pacote `blendertomob/product_libraries/face_frame/` (31 `.py`, ~60 800 linhas).
> Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Detalhes visuais em `_reversa_sdd/flowcharts/legacy-face_frame*.md`;
> mapa arquivo→símbolo em `_reversa_sdd/face_frame/legacy-mapping.md`.

### Propósito
Biblioteca de produtos de marcenaria **com moldura frontal (face frame)** no estilo norte-americano: gabinetes de base,
aéreo (upper), torre (tall), lap drawer, painéis soltos, cantos (pie-cut, diagonal, pie-cut com gavetas), móveis
(cômodas, criados-mudos, window seat), banheiro (medicine cabinet, overstool, tri-view, tub skirt, mirror frame), produtos
lineares (leg/pilar, floating shelf, valance, half wall, support frame) e peças soltas (misc part, door part). Modela a
carcaça (laterais, fundo, costas, tampo/travessas, rodapé), a moldura (stiles, rails, mid stiles, mid rails), bays
(colunas entre mid stiles), a árvore recursiva de aberturas (splits H/V) com frentes (porta, gaveta, pullout, false
front, tilt-out, inset panel, appliance), itens internos, acabamento de laterais expostas, painéis aplicados, estilos
(madeira/cor/overlay/porta) e puxadores. 🟢 (`types_face_frame.py:1-16`, `solver_face_frame.py:1-23`)

### Arquivos
Ver tabela completa em `_reversa_sdd/face_frame/legacy-mapping.md`. Principais: `types_face_frame.py` (9541 l.),
`style_options.py` (9838 l., catálogo gerado), `props_hb_face_frame.py` (8155 l.), `ops_placement.py` (5896 l.),
`solver_face_frame.py` (4797 l.), `ops_cabinet.py` (4751 l.), `types_face_frame_corner.py` (2986 l.). 🟢

### Fluxo de controle
1. **Registro** (`__init__.py:13-26`): props → menus → 13 módulos de operadores → UI → `dim_edit_overlay` (draw handler
   POST_PIXEL permanente + keymap). Props: `Object.face_frame_cabinet/bay/opening/split/interior_*`, `leg_product`,
   `floating_shelf`, `valance_product`, `Scene.hb_face_frame`; handler `load_post` `_seed_style_rename_anchors`
   (`props_hb_face_frame.py:8105-8155`). 🟢
2. **Colocação** (`ops_placement.hb_face_frame_OT_place_cabinet` :1746): modal com raycast em paredes/ilhas/frentes; largura
   por fill-to-gap ou digitada; `_auto_bay_qty = ceil((w − 1/16")/36")` limitado a [1,10] (:317); no `_finalize` (:3543):
   `get_cabinet_class(nome)` → `cls().create(nome, bay_qty)` → `cab_props.width = largura` → `apply_bay_preset` com
   `default_bay_config(nome, largura do bay)` dentro de `suspend_recalc` → `_try_auto_merge_with_neighbor` (:928) → exposição.
   Falha na criação vira `{'CANCELLED'}` com report de erro. 🟢
3. **Criação** (`FaceFrameCabinet.create_cabinet_root` :966 / `create_carcass` :1017): tags + `CLASS_NAME`; defaults de
   top_scribe por tipo (UPPER 1/8", TALL 1/2"); blind amount 12" em uppers; larguras de stile/rail/espessura vindas da cena;
   escreve width/height/depth por último (dispara recálculo). `create_carcass` constrói tudo sob as guardas e faz UM
   `recalculate()`. 🟢
4. **Recálculo** (`recalculate_face_frame_cabinet` :8745 → `FaceFrameCabinet.recalculate` :1842): ver
   `legacy-face_frame-recalculate.md`. Sequência: Dim do cage → distribuições (profundidade, altura, kick, rails, larguras de
   bay, árvore) → `FaceFrameLayout` → segmentos/reconciliação → despacho por `hb_part_role` → pós-passes (painéis aplicados,
   acabados, cortadores, extensões, anotações, furniture top, hutch, wedge) → reaplica estilo e destaques → painel solto. 🟢
5. **Gabinetes de canto** sobrescrevem `recalculate` (`types_face_frame_corner.py:981`) e `_build_carcass_parts` (:312),
   despachando por `corner_type` (PIE_CUT / DIAGONAL / PIE_CUT_DRAWER); tipo desconhecido → `NotImplementedError`. 🟢
6. **Edição**: sidebar/popup (`ui_face_frame.py`), rótulos editáveis (`dim_edit_overlay.py`), arraste de fronteiras
   (`op_modify_cabinet.py`), comandos por peça (`ops_part_commands.py`), menus por `MENU_ID`. Todos escrevem em props, cujos
   callbacks chamam `recalculate_face_frame_cabinet`. 🟢
7. **Tratamento de erros**: predominantemente silencioso — `except Exception: pass` no dreno de `suspend_recalc` (:103-106),
   no registro de classes (`props_hb_face_frame.py:8064-8085`), no desregistro do overlay; funções do solver retornam
   valores neutros (0.0, listas vazias) para índices inválidos. 🟢

### Algoritmos e regras
**Algoritmos centrais**
- A1 **Distribuição com travas (locked/unlocked + share)** — bays (`types_face_frame.py:1641`), nós da árvore
  (`:1763`, `solver_face_frame.py:2816`), seções de canto (`types_face_frame_corner.py:195`), painéis de appliance
  (`operators/ops_appliance_panels.py:120`). `share = (disponível − consumido_por_membros − Σ travados) / nº destravados`. 🟢
- A2 **Segmentação preguiçosa de rails** (`solver_face_frame.py:1305-1456`) — um rail por sequência de bays compatíveis. 🟢
- A3 **Caminhada recursiva da árvore de aberturas** (`_walk_tree` :2993) — gera folhas, splitters e backings com reveals. 🟢
- A4 **Geometria de frentes** (`front_leaves` :3593) — overlay por lado, pivôs de dobradiça/slide, folhas duplas/triplas. 🟢
- A5 **Detecção de exposição** (`exposure.py:218-476`) — união de faixas Z de vizinhos coincidentes. 🟢
- A6 **Cunha tip-up** (`compute_wedge` :1249): `diag = √(d²+h²)`; se `diag > teto − folga`: `altura = min(diag − teto_ef, máx)`,
  `comprimento = d − √(teto_ef² − h²)` (ou `d` se teto_ef ≤ h). 🟢
- A7 **Moldura angular** (`face_frame_angle` :1558, `face_frame_length` :1578): `θ = atan2(ld − rd, width)`,
  `L = hypot(width, rd − ld)`; só 1 bay e sem canto. 🟢
- A8 **Quantidade automática de prateleiras** (`auto_shelf_qty` :3717) — tabela por altura do vão e profundidade (< 18" vs ≥ 18"). 🟢
- A9 **Painel aplicado — escada de aberturas por largura** (`applied_panel_sizing.py:239-256`): ≤20"→1, ≤38"→2, ≤56"→3,
  ≤74"→4, ≤92"→5, ≤110"→6, ≤128"→7, acima→8. 🟢
- A10 **Merge / break de gabinetes** (`types_face_frame.py:9025`, `:9331`) — reparentamento de bays e conservação de largura. 🟢

**Regras de negócio**
| ID | Regra | Local | Conf. |
|---|---|---|---|
| FACE_FRAME-R01 | Origem do gabinete no canto traseiro-esquerdo no piso; +X direita, −Y frente (frente em y = −depth); face externa da moldura rente à frente; carcaça começa em −depth + fft. | `solver_face_frame.py:8-12` | 🟢 |
| FACE_FRAME-R02 | Toe kick só existe para cabinet_type BASE, TALL, LAP_DRAWER; BASE/LAP_DRAWER usam travessas (stretchers) frontal+traseira, UPPER/TALL usam tampo sólido; gabinete angular sempre tampo sólido. | `solver_face_frame.py:77-81,194-195` | 🟢 |
| FACE_FRAME-R03 | Largura de cada bay destravado = (largura disponível − stiles de ponta − mid stiles − bays travados) / nº destravados; disponível desconta blind (se stile BLIND e blind ligado) ou usa a hipotenusa no modo angular. | `types_face_frame.py:1641-1725` | 🟢 |
| FACE_FRAME-R04 | Edição do usuário em bay.width / kick_height / tamanho interior liga automaticamente o unlock correspondente; escritas de sistema (guarda `_DISTRIBUTING_WIDTHS`) não travam. | `props_hb_face_frame.py:4031-4098` | 🟢 |
| FACE_FRAME-R05 | Bays destravados seguem profundidade, altura, kick height e larguras de top/bottom rail do gabinete; travados mantêm override. | `types_face_frame.py:1554-1639` | 🟢 |
| FACE_FRAME-R06 | Offset da lateral: FINISHED → 0 (lateral é a face, 3/4"); PANELED → 3/4"; FLUSH_X/BEADBOARD/SHIPLAP → 1/4"; demais → scribe digitado. | `solver_face_frame.py:379-417` | 🟢 |
| FACE_FRAME-R07 | Lateral FINISHED tem 3/4"; demais usam material_thickness (padrão 1/2"); fundo acabado é peça separada 3/4" sobre as costas (1/4"). | `solver_face_frame.py:391-427` | 🟢 |
| FACE_FRAME-R08 | Topo da carcaça = topo do bay − top_scribe; laterais não FINISHED baixam junto; stiles/top rail não. | `solver_face_frame.py:451-466` | 🟢 |
| FACE_FRAME-R09 | BASE/TALL ancoram no piso (bay_top = height, bay_bottom = kick_height); UPPER ancora no topo (bay_top = dim_z − top_offset, bay_bottom = bay_top − height). | `solver_face_frame.py:493-507` | 🟢 |
| FACE_FRAME-R10 | Um top rail atravessa um gap somente se o mid stile não sobe, topos iguais, larguras iguais e nenhum bay tem front_drop; bottom rail exige extend_down 0, sem to_floor, fundos e larguras iguais e sem remove_bottom. | `solver_face_frame.py:1305-1361` | 🟢 |
| FACE_FRAME-R11 | Toe kick FLUSH: bottom rail vai ao piso com largura = kick_height + bottom_rail_width. | `solver_face_frame.py:1417-1449` | 🟢 |
| FACE_FRAME-R12 | Mid stile: base = menor fundo dos bays vizinhos (+ bottom rail se o rail atravessa) − extend_down (0 se to_floor); topo = maior topo (− top rail se atravessa) + extend_up. Mid stiles nunca são destruídos (um por gap). | `solver_face_frame.py:1743-1809` | 🟢 |
| FACE_FRAME-R13 | remove_bottom zera a largura efetiva do bottom rail: a abertura/cage cresce para baixo; o callback destrava e zera o overlay inferior das aberturas do perímetro inferior (re-trava ao restaurar). | `solver_face_frame.py:597-611`; `props_hb_face_frame.py:3932-3980` | 🟢 |
| FACE_FRAME-R14 | Porta de vaidade (SIZE_ROLE VANITY_DOOR) destravada fica sempre 4" mais larga que a cota igualitária dos irmãos. | `solver_face_frame.py:2813-2852`; `types_face_frame.py:1795-1817` | 🟢 |
| FACE_FRAME-R15 | Mid rail removido: sem peça nem backing; espaço colapsa para 3/32" + overlays adjacentes (frentes a 3/32"). Só em splits H. | `solver_face_frame.py:3051-3062,3255` | 🟢 |
| FACE_FRAME-R16 | Em bay com remove_bottom e vão inferior frontless (NONE/APPLIANCE), o último splitter da raiz vira BOTTOM_RAIL com a largura do bottom rail. | `solver_face_frame.py:3063-3074` | 🟢 |
| FACE_FRAME-R17 | Backing automático: split H → prateleira fixa BAY_SHELF 3/4" (face superior rente ao topo do mid rail); split V → divisão BAY_DIVISION com material_thickness, centrada no mid stile. `add_backing` padrão True. | `solver_face_frame.py:2855-2972`; `props_hb_face_frame.py:6285` | 🟢 |
| FACE_FRAME-R18 | Overlay efetivo por lado = valor da abertura se unlock_<lado>_overlay, senão default do gabinete (0,5"). | `solver_face_frame.py:3232-3241` | 🟢 |
| FACE_FRAME-R19 | Tamanho da porta = vão + overlays; afastamento da frente = 1/8" à frente da moldura menos default_door_inset_amount; abertura máxima 100°; porta dupla com fresta central de 1/8". | `solver_face_frame.py:3248-3431` | 🟢 |
| FACE_FRAME-R20 | Gaveta/pullout desliza até bay_depth − fft − 1"; FALSE_FRONT nunca desliza; TILT_OUT usa dobradiça inferior forçada; INSET_PANEL = painel 1/4" do tamanho do vão. | `solver_face_frame.py:3314-3490,3593-3664` | 🟢 |
| FACE_FRAME-R21 | Tri-view (HB_TRIVIEW_DOORS): 3 portas espelho iguais, fresta 1/8", quadro 1,25", stiles internos zerados, dobradiças R/R/L. | `solver_face_frame.py:3523-3590` | 🟢 |
| FACE_FRAME-R22 | Fillers de appliance: com set_appliance_width, cada filler = (vão − appliance)/2; sem ele, valores digitados escalados se excederem o vão; include_fillers desligado → 0. Mesma regra para os fillers de front_drop (pia/cooktop). | `solver_face_frame.py:519-552,3667-3704` | 🟢 |
| FACE_FRAME-R23 | Prateleiras automáticas: prof. < 18": <15"→0, 15–20"→1, >20"→2, >32"→3, >44"→4; prof. ≥ 18": <20"→0, 20–28"→1, >28"→2, >40"→3, >52"→4 (máx 4). | `solver_face_frame.py:3717-3765` | 🟢 |
| FACE_FRAME-R24 | Selecionar DOOR garante um item ADJUSTABLE_SHELF na abertura (reinsere se removido). | `props_hb_face_frame.py:4011-4028` | 🟢 |
| FACE_FRAME-R25 | Exposição: parede no início/fim da corrida ou ponta encostada em parede → UNEXPOSED (wall_edge); cobertura Z total por vizinhos → UNEXPOSED; parcial → PARTIAL; sem vizinho → EXPOSED. Costas: parede ou costas coincidentes de ilha → UNEXPOSED. | `exposure.py:142-371` | 🟢 |
| FACE_FRAME-R26 | Acabamento automático: lava-louças → preferência da cena (padrão UNFINISHED); PARTIAL → FINISHED; EXPOSED → default_finished_end_type/back_type (padrão FINISHED); UNEXPOSED → UNFINISHED. Scribe auto: 1/2" parede, 1/4" vizinho/lava-louças, 0 se não UNFINISHED. Só em lados com *_finish_end_auto. | `exposure.py:374-440` | 🟢 |
| FACE_FRAME-R27 | Editar acabamento ou scribe manualmente desliga o auto daquele lado. | `props_hb_face_frame.py:3983-4009` | 🟢 |
| FACE_FRAME-R28 | Painel aplicado PANELED com porta 5 peças: rail = rail_gabinete − overlay_default + rail_da_porta (+ kick band em BASE/TALL); stile voltado para frente = stile do gabinete − fft; fundo usa largura de mid stile nos dois lados. | `applied_panel_sizing.py:65-161` | 🟢 |
| FACE_FRAME-R29 | Largura de stile por tipo: BLIND = ff_blind_stile_width (+3/4" se blind ligado); WALL/BUTT/INSIDE_90/ANGLE = célula do estilo (linha × coluna base/tall/upper); STANDARD = ff_end_stile_width; ignorado se unlock do stile. | `props_hb_face_frame.py:4384-4449` | 🟢 |
| FACE_FRAME-R30 | Tabela de larguras de moldura por tipo de overlay (CLASSIC/TRANSITIONAL/FULL/PARTIAL_INSET/FULL_INSET) × (base, tall, upper); rails respeitam unlock, stiles sempre seguem o overlay. | `props_hb_face_frame.py:633-676,1585-1647` | 🟢 |
| FACE_FRAME-R31 | Overlays por estilo (L,R,T,B em pol.): CLASSIC 0,5; TRANSITIONAL 0,625/0,875; FULL 1,0/0,875; PARTIAL_INSET 0,5 com inset = (esp. porta + 1/8")/2; FULL_INSET −0,125 com inset = esp. porta + 1/8". | `props_hb_face_frame.py:1652-1690` | 🟢 |
| FACE_FRAME-R32 | Preset padrão na colocação: largura do bay ≥ 18" → porta dupla/variante larga; abaixo → porta simples; tabela por nome de catálogo (Base→DRAWER_DOOR/DRAWER_DOUBLE_DOOR, Sink→FALSE_FRONT_*, Tall→*_STACKED_DOOR, Refrigerator→BUILT_IN_REFRIGERATOR, etc.). | `bay_presets.py:389-494` | 🟢 |
| FACE_FRAME-R33 | size_role fixa o tamanho de nós: TOP_DRAWER = top_drawer_opening_height (4,5"); TALL_SPLIT_BOTTOM = 54"; UPPER_STACKED_TOP = 12"; REFRIGERATOR = refrigerator_height (69"); VANITY_SINK_WIDTH = 20"; BOOKCASE_STORAGE_BOTTOM = 30"; unlock_size antes de size. | `operators/ops_cabinet.py:2020-2062` | 🟢 |
| FACE_FRAME-R34 | Recálculo via callback usa WRAP_CLASS_REGISTRY por CLASS_NAME; classes ausentes (Furniture*, dressers, night stands, window seat, BookcaseUpper, Hutch, BookcaseStorageUnit) caem em FaceFrameCabinet base, cujo `_has_toe_kick()` é False → kicks do gabinete e kick_height dos bays tendem a ser zerados/removidos após qualquer edição. | `types_face_frame.py:6919-6921,8636-8680`; `:1592-1619` | 🟢 (ausência) / 🟡 (efeito) |
| FACE_FRAME-R35 | Auto nº de bays = ceil((largura − 1/16") / 36"), entre 1 e 10. | `operators/ops_placement.py:48-50,317-329` | 🟢 |
| FACE_FRAME-R36 | Auto-merge com vizinho exige mesma altura, profundidade, Z mundial, mesmo parent, ambos sem canto, encostados ±1"; TALL, leg, floating shelf e valance nunca fundem. | `types_face_frame.py:9025-9080`; `operators/ops_placement.py:928-960` | 🟢 |
| FACE_FRAME-R37 | Break de gabinete: remove o mid stile do gap; novas pontas usam largura de "butt stile" do estilo (fallback bay_mid_stile_width); propaga props do lado direito para o novo gabinete. Cantos não quebram. | `types_face_frame.py:9331-9400` | 🟢 |
| FACE_FRAME-R38 | Geladeira: stiles ao piso, toe_kick_height 0, remove_bottom em todos os bays, back_bottom_inset = kick + altura da abertura + mid rail − mt; lados podem subir até o topo da abertura ("stile in lieu of leg"). | `types_face_frame.py:7286-7383`; `solver_face_frame.py:645-680`; `props_hb_face_frame.py:3902-3929` | 🟢 |
| FACE_FRAME-R39 | Lap drawer: BASE com toe_kick FLOATING e elevação de 27"; preset LAP_DRAWER eleva o bay a 24" (floating_bay) e SUPPORT_FRAME remove fundo com kick 0; esses presets levam os stiles vizinhos ao piso. | `types_face_frame.py:7429-7460`; `bay_presets.py:248-280` | 🟢 |
| FACE_FRAME-R40 | Upper com lateral UNFINISHED é "capturada" pelo fundo (lateral apoia sobre o fundo, que se estende sob ela); FINISHED desce até o fundo do bay. | `solver_face_frame.py:683-730` | 🟢 |
| FACE_FRAME-R41 | Puxador: gaveta centralizada (ou a 1,5" do topo); porta upper a 1,5" da base; tall a 36" do chão (regras de 3 vias); base a 1,5" do topo; horizontal a 1,5" da borda livre; flip door centralizado na borda livre. | `types_face_frame.py:6290-6428`; `props_hb_face_frame.py:6821-6846` | 🟢 |
| FACE_FRAME-R42 | Peça marcada IS_MANUAL_PART (ou sem modifier GN) e abertura IS_MANUAL_FRONT ficam fora da reescrita paramétrica. | `types_face_frame.py:1998-2020,5954` | 🟢 |
| FACE_FRAME-R43 | Tampo (countertop): espessura 1,5", balanço frontal 1", laterais 1", traseiro 0; lados encostados em tall ou em parede conectada não têm balanço; cantos geram L. | `operators/ops_countertop.py:243-330`; `props_hb_face_frame.py:6702-6727` | 🟢 |
| FACE_FRAME-R44 | Canto (pie-cut/diagonal): alturas de seções distribuídas como A1 no vão entre bottom rail efetivo e top rail; FLUSH leva moldura ao piso e soma kick ao bottom rail; diagonal: comprimento da moldura = √((w−ld)²+(d−rd)²), rail = diag − lsw − rsw. | `types_face_frame_corner.py:195-208,2224-2241,2370-2381` | 🟢 |

### Constantes/enums
- **Tags de identidade** (`types_face_frame.py:41-57`): `IS_FACE_FRAME_CABINET_CAGE`, `IS_FACE_FRAME_BAY_CAGE`,
  `IS_FACE_FRAME_OPENING_CAGE`, `IS_FACE_FRAME_SPLIT_NODE`, `IS_FACE_FRAME_PRODUCT_CAGE`, `IS_INTERIOR_SPLIT_NODE`,
  `IS_INTERIOR_REGION`; custom props de ID: `CLASS_NAME`, `CABINET_TYPE`, `MENU_ID`, `STYLE_NAME`, `hb_part_role`,
  `hb_bay_index`, `hb_mid_stile_index`, `hb_segment_start_bay`, `hb_split_child_index`, `hb_splitter_index`, `SIZE_ROLE`,
  `IS_MANUAL_PART`, `IS_MANUAL_FRONT`, `HB_TRIVIEW_DOORS`. 🟢
- **Papéis de peça** `PART_ROLE_*` (~60 em `types_face_frame.py:110-196`, ~30 de canto em `types_face_frame_corner.py:30-79`). 🟢
- **Enums**: `cabinet_type` {BASE, TALL, UPPER, LAP_DRAWER, PANEL}; `corner_type` {NONE, PIE_CUT, DIAGONAL, PIE_CUT_DRAWER};
  `toe_kick_type` {NOTCH, FLUSH, FLOATING, LOOSE, LOOSE_FLUSH}; `FIN_END_ITEMS` {UNFINISHED, FINISHED, PANELED, FALSE_FF,
  WORKING_FF, BEADBOARD, SHIPLAP, FLUSH_X}; `EXPOSURE_ITEMS` {UNEXPOSED, PARTIAL, EXPOSED}; stile type {STANDARD, WALL, BLIND,
  BUTT, INSIDE_90, ANGLE}; `FRONT_TYPE_ITEMS` {NONE, DOOR, DRAWER_FRONT, PULLOUT, FALSE_FRONT, TILT_OUT, INSET_PANEL,
  APPLIANCE}; hinge {LEFT, RIGHT, DOUBLE, TOP, BOTTOM}; split axis {H, V}; interior kind {ADJUSTABLE_SHELF, GLASS_SHELF,
  PULLOUT_SHELF, ROLLOUT, TRAY_DIVIDERS, VANITY_SHELVES, ACCESSORY}; door_overlay_type {CLASSIC, TRANSITIONAL, FULL,
  PARTIAL_INSET, FULL_INSET}; door_type {SLAB, 5_PIECE}; seleção {Cabinets, Bays, Face Frame, Openings, Interiors, Parts,
  Applied Panels}. 🟢 (`props_hb_face_frame.py` — ver dicionário)
- **Constantes do solver** (pol.): `VANITY_DOOR_EXTRA_WIDTH` 4; `DOOR_MAX_SWING_ANGLE` 100°; `DOUBLE_DOOR_REVEAL` 1/8;
  `MID_RAIL_REMOVED_GAP` 3/32; `TRIVIEW_DOOR_REVEAL` 1/8; `TRIVIEW_FRAME_WIDTH` 1,25; `DOOR_TO_FRAME_GAP` 1/8;
  `SHELF_THICKNESS` 3/4; `SHELF_X_CLEARANCE` 1/16; `SHELF_FRONT/BACK_SETBACK` 1/4; `PULLOUT_SPACER_THICKNESS` 1/2;
  `PULLOUT_SPACER_Y_OFFSET` 2,5; `VANITY_SUPPORT_*` 1,5/0,5/0,375; mid stile padrão 2; stretcher 3,5×0,5 (fallback
  0,0889/0,0127 m). 🟢 (`solver_face_frame.py:2813,3248-3261,3707-3713,3854-3855,4033-4035,199-200`)
- **Outros**: `BLIND_PANEL_THICKNESS` 1/4; `INSET_DOOR_REVEAL` 1/8 (canto); `_MAX_BAY_WIDTH` 36, bays 1–10,
  `_WALL_SNAP_DISTANCE` 6, `_FRONT_BACK_HYSTERESIS` 1 (placement); `MIN_BAY_WIDTH` 2, `MIN_OPENING_SIZE` 1 (modify);
  `DOUBLE_DOOR_WIDTH_THRESHOLD` 18; `FLUSH_KICK_BOTTOM_RAIL` 5,25; `_MID_STILE_WIDTH_THRESHOLD` 21;
  `_AUTO_MID_RAIL_DOOR_HEIGHT` 45,5; `_WALL_SCRIBE` 1/2, `_NEIGHBOR_SCRIBE` 1/4, `_WALL_GAP_TOL` 1/8, `_WALL_LATERAL_TOL` 1/2. 🟢

### Riscos Blender 5.2
| Risco | Local | Conf. |
|---|---|---|
| **Escrita dict-style em propriedade `bpy.props`**: `cab_props['refrigerator_opening_height'] = ...` — desde o 5.0 o valor RNA fica em armazenamento separado, então essa escrita não altera a prop (fica o padrão 62" em vez da altura da cena, 69"), e o `back_bottom_inset` calculado a seguir usa a altura da cena → descompasso. | `types_face_frame.py:7335` (ver `docs/rag/project/03_compatibilidade_5x.md:43-51`) | 🟢 código / 🟡 efeito |
| `EnumProperty(items=callback)` sem manter referência às strings (stain/paint/door style/drawer style/pull category/pull) — GC pode corromper rótulos; além disso, itens com índice posicional mudam a seleção quando a lista muda. `_bottom_rail_profile_items` faz o cache corretamente. | `props_hb_face_frame.py:195-258,6406-6425` (ver `docs/rag/project/04_armadilhas.md:86`) | 🟢 código / 🟡 efeito |
| Guardas de reentrância chaveadas por `id(obj)` do wrapper Python — depende de reuso de instância pelo Blender; `as_pointer()`/nome seriam estáveis. | `types_face_frame.py:1029-1037,8765-8777`; `props_hb_face_frame.py:4047` | 🟡 |
| Apagar e recriar frentes/pivôs/puxadores/splitters/backings a cada recálculo (`bpy.data.objects.remove`) — referências inválidas e malhas órfãs acumuladas. | `types_face_frame.py:5961-5972,5785-5830` (ver `04_armadilhas.md:13`) | 🟢 / 🟡 |
| Registro de classes engole exceções (`except Exception: pass`) — falhas de registro passam despercebidas. | `props_hb_face_frame.py:8064-8085` | 🟢 |
| Handler de `split_preview` só é removido pelo operador `split_opening` (execute/cancel) e pelo próprio draw; `unregister()` do pacote não o remove. | `split_preview.py:218-236`; `operators/ops_cabinet.py:863-902` | 🟢 |
| `dim_edit_overlay` mantém draw handler permanente (removido corretamente no `unregister`). | `dim_edit_overlay.py:897-922` | 🟢 |
| Inputs de GN via `hb_utils.get/set_gn_input` (helpers duplicados de `compat.py`, precisam ficar em sincronia); nenhum `mod["Socket_X"]` encontrado. | `types_face_frame.py:2637,2647,4591…`; `types_face_frame_corner.py:134` | 🟢 |
| Shaders `UNIFORM_COLOR`, `blf.size(font, size)`, `render.engine = 'BLENDER_EEVEE'` são válidos no 5.2; `check_api.py` sem símbolos desconhecidos. | `split_preview.py:191`; `dim_edit_overlay.py:532`; `thumbnail_render.py:125` | 🟢 |
| Muitos `setattr` fora de `suspend_recalc` (exposição, `assign_style_to_cabinet`) → vários recálculos completos por ação. | `exposure.py:416-440`; `props_hb_face_frame.py:1668-1690` | 🟡 desempenho |
| `bl_idname` no namespace legado `hb_face_frame.*` e menus `HOME_BUILDER_MT_*` (código novo deve usar `btm.*`). | `operators/*.py` | 🟢 |

### Unidades e premissas de mercado
- **Unidade interna em metros**, mas praticamente todos os padrões são definidos em polegadas via `units.inch()`; catálogo
  `style_options.SERIES_FRAME` armazena larguras em polegadas cruas (conversão tardia); `ops_placement` reporta `"` com
  fator 39.37008. 🟢 (`style_options.py:5025-5088`; `operators/ops_placement.py:2268,3608`)
- **Premissas americanas (conflitam com marcenaria brasileira)** 🟢/🟡:
  - Construção *face frame* (moldura maciça de 3/4" com stiles/rails) — no Brasil predomina construção sem moldura
    (MDF/MDP 15–18 mm, "frameless" com dobradiça de caneco). 🟡
  - Chapas em frações de polegada: carcaça 1/2", costas 1/4", moldura/porta 3/4", laterais acabadas 3/4" — no BR: 15/18/25 mm
    e fundo 3/6 mm. 🟢 (defaults) / 🟡 (comparação)
  - Alturas/profundidades: base 34,5" (876 mm) × 24" (610 mm), rodapé 4" × recuo 3", upper 30" × 12", tall 84" × 25,5",
    montagem de aéreo a 54" do piso, bancada 1,5" — padrões BR usuais: base ~720–750 mm + tampo, profundidade 550–600 mm,
    rodapé ~100–150 mm. 🟢 (defaults) / 🟡 (comparação)
  - Largura máxima de bay 36" e limiar de porta dupla 18" (457 mm). 🟢
  - Cotas de puxador (1,5", 36") e acessórios de marca americana (Blum Tandem BLUMOTION, KV8400/KV4270, "Lazy Susan"),
    geladeira 69" × 40", lava-louças 24", range 36". 🟢
  - Catálogo "CWP" de fornecedor (espécies de madeira americanas: alder, hickory, knotty pine; séries de portas com códigos de
    produto) — dados comerciais sem equivalência no Brasil. 🟢
  - Nomenclatura de acabamento de ponta (FINISHED/PANELED/BEADBOARD/SHIPLAP/FLUSH_X) e "scribe" para parede torta. 🟢

### Dependências de outros módulos
`hb_types` (GeoNodeCage/Cutpart/DrawerBox/Rectangle/Wall), `hb_utils`, `units`, `hb_details`, `hb_placement`,
`hb_project`, `hb_gpu_draw`, `appliance_spec_registry`, `product_libraries/common/types_appliances`,
`product_libraries/frameless/types_frameless.CabinetPart`, `product_libraries/frameless/types_products` (HalfWall,
SupportFrame), `operators/viewport_hud`; consumido por `ui/menu_apend.py` (lê `MENU_ID`). 🟢
Assets: `face_frame_assets/cabinet_pulls/`, `face_frame_assets/profiles/`, `face_frame_assets/door_profiles/`,
`face_frame_thumbnails/`. 🟢

### Lacunas
- 🔴 Conteúdo detalhado de `_recalculate_pie_cut` / `_recalculate_diagonal` / `_recalculate_pie_cut_drawer`
  (~1 500 linhas: portas bifold/revolving, susans, clip back) lido apenas por amostragem.
- 🔴 Passes pós-recálculo de acabamento (`_reconcile_applied_panels`, `_reconcile_textured_panels`, `_reconcile_flush_x_strips`,
  `_reconcile_finished_side_returns`, `_apply_back_extension`, cortadores) — responsabilidades mapeadas, fórmulas não extraídas.
- 🔴 `mid_division_panels` / `partition_skin_panels` (divisórias com profundidades diferentes) e segmentos de fundo/costas.
- 🔴 Solvers de itens internos (rollouts, tray dividers, vanity shelves, árvore interior com face frame interno).
- 🔴 Produtos Leg/FloatingShelf/Valance (`recalculate` próprios em `types_face_frame.py:7649,7927,8065`).
- 🔴 `ui_face_frame.py`, `menus_face_frame.py`, `ops_styles.py`, `ops_library.py` — apenas inventariados.
- 🟡 LAP_DRAWER existe no enum e no solver, mas `LapDrawerFaceFrameCabinet` usa `default_cabinet_type = 'BASE'`
  (`types_face_frame.py:7436`); não foi encontrado quem grave 'LAP_DRAWER' → possível valor morto.
- 🟡 Dois parâmetros de altura de geladeira (scene `refrigerator_height` 69" e cabinet `refrigerator_opening_height` 62") podem divergir.
- 🟡 Tamanho armazenado de filhos destravados em `_redistribute_split_node` ignora overrides por membro, membros removidos,
  remove_bottom e front_drop (o solver ignora esses valores para destravados, então o efeito se limita à exibição e ao valor
  congelado quando o usuário trava).
- 🟡 Sem clamp para largura de bay negativa em `_distribute_bay_widths`.

---

## Módulo closets

> Camada legada (fork Home Builder 5) — `blendertomob/product_libraries/closets/` (17 arquivos .py, 9.751 linhas).
> Confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas: `_reversa_sdd/flowcharts/legacy-closets*.md` · Mapeamento: `_reversa_sdd/closets/legacy-mapping.md`.

### Propósito

Biblioteca de **closets/roupeiros modulares** no estilo do sistema americano "32 mm" (herança de um sistema de closets legado citado nos
comentários, `const_closets.py:1-5`). Um *starter* é uma corrida de módulos entre painéis verticais compartilhados; cada **vão** (bay)
tem prateleiras fixas de topo e base, rodapé, *cleat*, trilho de parede e uma ou mais **aberturas** (openings) que recebem
inserções: prateleiras reguláveis, prateleiras fixas divisoras, varões com cabides, portas (simples/dupla/basculante), gaveteiros
com caixas de sistema (Avantech/Metabox/madeira) e nichos. Há também unidades de canto em L e ilhas (simples e dupla face). 🟢

Diferente das bibliotecas de armários, **não usa drivers**: toda dimensão é propagada por `ClosetStarter.recalculate()` que lê os
PropertyGroups, chama o solver puro (`solver_closets`) e escreve os inputs de Geometry Nodes de cada peça (`types_closets.py:1-8`). 🟢

### Arquivos

| Arquivo | Linhas | Papel |
|---|---|---|
| `types_closets.py` | 2279 | construção/recálculo, regeneradores, presets |
| `operators/ops_closet.py` | 2902 | operadores de negócio e colocação modal |
| `gpu_overlay_closets.py` | 1019 | overlay GPU de rótulos editáveis |
| `operators/op_grab_closet.py` | 921 | arraste de fronteiras |
| `props_closets.py` | 533 | PropertyGroups + UI da biblioteca |
| `pulls_closets.py` | 392 | puxadores, varões, cabides |
| `materials_closets.py` | 313 | materiais/fitas/veio |
| `menus_closets.py` | 251 | menus de contexto |
| `fronts_closets.py` | 237 | estilos de frente 5 peças |
| `operators/op_open_door_closet.py` | 230 | abrir porta/gaveta animado |
| `molding_closets.py` | 218 | moldura de coroa |
| `const_closets.py` | 140 | constantes + sistema 32 mm |
| `solver_closets.py` | 126 | solver de layout (sem bpy) |
| `drawer_boxes_closets.py` | 114 | sistemas de caixa de gaveta |
| `starter_presets.py` | 40 | catálogo declarativo |
| `__init__.py` / `operators/__init__.py` | 21 / 15 | registro |

### Fluxo de controle

1. **Registro** 🟢 — `closets/__init__.py:10-21`: `props → menus → operators → gpu_overlay` (inverso no `unregister`). Os PointerProperty
   `Scene.hb_closets`, `Object.hb_closet_starter`, `Object.hb_closet_bay` são criados em `props_closets.py:508-516` e removidos em
   `:519-533`. `op_grab_closet` e `gpu_overlay_closets` registram **draw handlers permanentes** POST_PIXEL + keymaps de addon
   (`op_grab_closet.py:892-898`, `gpu_overlay_closets.py:994-1001`) e os removem no `unregister`.
2. **Colocação** 🟢 — `hb_closets.place_starter` (`ops_closet.py:399-1483`): `invoke` resolve a classe via `CLOSET_NAME_DISPATCH`
   (ou duplica um starter existente), cria cage de preview com modificador ARRAY (1 célula × `bay_qty`), entra em modal. MOUSEMOVE →
   `_position_on_wall` (gap fill, snaps esq/dir/centro com histerese, recuo de canto 1/2 in, lado da parede com histerese) ou
   `_position_free` (grade; ilhas com folgas e detentes de corredor). Teclas: W/números (largura/offset), ↑/↓ (qtd de vãos 1–9),
   ←/→ (offset de borda ou folga de ilha), R (gira 90°), F (fill no modo duplicar). LMB → `_finalize`: `create_starter` →
   posiciona → `sp.width = largura` (dispara recálculo) → `_apply_finish` → sombreamento do modo de seleção → diálogo
   `set_corner_clearance` se houver vizinho perpendicular. ESC/RMB → `_cancel` (remove handler de cotas e preview).
3. **Criação** 🟢 — `ClosetStarter.create_starter` (`types_closets.py:253-290`): sob as guardas de reentrância, semeia props do
   starter a partir da cena, `_build_parts` cria N+1 painéis, tampo opcional, N vãos com larguras iguais
   `(W − (N+1)·pt)/N` (`:318`) e, por vão, prateleira inferior/superior, rodapé, cleat, fundo aplicado (ilha), rodapé traseiro +
   fundo central + opening BACK (ilha dupla) e a opening FRONT; termina com um `recalculate()`.
4. **Recálculo** 🟢 — `recalculate` (`:458-521`): propaga altura/profundidade do starter para vãos não sobrescritos
   (`hb_last_height/hb_last_depth`), monta spec, `solver.compute_layout`, grava larguras sem auto-travar, dispõe painéis, vãos
   (prateleiras, rodapés, cleat, trilho, fundos, divisoras → segmentos → `_layout_opening_parts`, portas do vão), tampo, pontes;
   ancora suspensos no topo; escreve `Dim X/Y/Z` do root.
5. **Edição** 🟢 — três caminhos convergem no mesmo recálculo: (a) props via diálogos (`starter_prompts`, `bay_prompts`) e update
   callbacks (`props_closets.py:68-94`); (b) rótulos GPU (`gpu_overlay_closets._commit :616-720`); (c) *grab* (`op_grab_closet._apply_drag
   :560-661`). Inserções gravam idprops na opening/vão e os **regeneradores** criam/removem peças para convergir
   (`_reconcile_adj_shelves/doors/drawers/cubbies/bay_openings/bay_doors`, `types_closets.py:1011-1242`).
6. **Opções de sala** 🟢 — enums de cena (`materials`, `fronts`, `pulls`, `rods`, `hangers`, `drawer_box`) têm `update_room` que
   percorre `scene.objects` e recalcula/reaplica em todo starter (`materials_closets.py:307`, `fronts_closets.py:230`,
   `pulls_closets.py:384`, `drawer_boxes_closets.py:107`).
7. **Tratamento de erros** 🟢 — padrão "best-effort": muitos `try/except Exception: pass` (estilo de frente `types_closets.py:113-117`,
   materiais `ops_closet.py:41-51`, draw callbacks `op_grab_closet.py:321`, `gpu_overlay_closets.py:610`, registro de classes
   `ops_closet.py:2881-2892`, `menus_closets.py:230-242`). Falhas ficam silenciosas. Guardas de reentrância `_RECALCULATING` /
   `_DISTRIBUTING_WIDTHS` (`types_closets.py:105-106`) evitam recursão pelos update callbacks.

### Algoritmos e regras

**Algoritmos centrais**

- **A1 — Solver de larguras/painéis** (`solver_closets.py:26-126`) 🟢: ver `flowcharts/legacy-closets-compute_layout.md`.
- **A2 — Segmentação por prateleiras divisoras** (`types_closets.py:635-689, 1194-1242`) 🟢: prateleiras fixas "comprometidas" vivem no
  vão e dividem o interior em segmentos; uma opening por segmento e lado; fusão re-hospeda conteúdo.
- **A3 — Pilha de gavetas que preenche a abertura** (`types_closets.py:810-878, 1813-1831`) 🟢.
- **A4 — Dimensionamento de caixa por sistema** (`drawer_boxes_closets.py:56-85`) 🟢: maior padrão que cabe.
- **A5 — Posicionamento de puxador Base/Tall/Upper referido ao piso** (`types_closets.py:975-992`) 🟢.
- **A6 — Traçado de moldura com retornos/degraus** (`molding_closets.py:159-218`) 🟢.
- **A7 — Folgas de ilha por raio×retângulo orientado (slab test)** (`ops_closet.py:104-167`) 🟢.
- **A8 — Detecção de vizinho de canto** (`ops_closet.py:170-288`) 🟢.
- **A9 — Arraste com snap 32 mm e snapshot/rollback** (`op_grab_closet.py:471-823`) 🟢.
- **A10 — Porta girando na dobradiça** (`types_closets.py:1770-1802`) e tween *smoothstep* (`op_open_door_closet.py:34-185`) 🟢.

**Regras de negócio**

| ID | Regra | Local | Conf. |
|---|---|---|---|
| CLOSETS-R01 | N vãos ⇒ N+1 painéis verticais compartilhados; painel *i* é o esquerdo do vão *i*. | `solver_closets.py:10-17, 80-97` | 🟢 |
| CLOSETS-R02 | Largura interna = `W − (N+1)·pt`; vãos destravados recebem partes iguais do restante após os travados. | `solver_closets.py:35-43` | 🟢 |
| CLOSETS-R03 | Largura mínima de vão destravado no solver = 1 in (25,4 mm); se violada, a soma não fecha (degrada visível). | `solver_closets.py:41`, `const_closets.py:69` | 🟢 |
| CLOSETS-R04 | Todos os vãos travados ⇒ escala proporcional para fechar na largura total. | `solver_closets.py:44-49` | 🟢 |
| CLOSETS-R05 | Editar a largura de um vão pelo usuário **trava** esse vão; escritas do sistema não travam. | `props_closets.py:81-94`, `types_closets.py:494-500` | 🟢 |
| CLOSETS-R06 | Painel entre dois vãos vai do menor fundo ao maior topo dos vizinhos (piso + suspenso ⇒ painel inteiro); profundidade = máx. dos vizinhos. | `solver_closets.py:85-97` | 🟢 |
| CLOSETS-R07 | Vão de piso: envelope começa no piso, rodapé dentro do envelope; vão suspenso: ancorado no topo do starter (`z0 = H − h`). | `solver_closets.py:101-102` | 🟢 |
| CLOSETS-R08 | Altura interna do vão = `h − kick − 2·st` (mín. 0,25 in no solver). | `solver_closets.py:103-106`, `types_closets.py:2135` | 🟢 |
| CLOSETS-R09 | Cleat (4 in) acompanha a prateleira inferior; sem prateleira inferior desce à base do envelope; oculto em ilha dupla. | `solver_closets.py:107-110`, `types_closets.py:363-367, 576-584` | 🟢 |
| CLOSETS-R10 | Rodapé: recuo 1,625 in da frente; oculto se vão suspenso, sem prateleira inferior ou kick ≤ 0; ilha dupla tem rodapé traseiro. | `types_closets.py:560-574` | 🟢 |
| CLOSETS-R11 | Trilho de parede (hang rail) 1,125 × 0,25 in, base 3,3125 in abaixo do topo do vão; criado sob demanda; ilhas não têm; idprop `hb_remove_hang_rail` oculta. | `types_closets.py:594-612`, `const_closets.py:21-23` | 🟢 |
| CLOSETS-R12 | Edição de altura/profundidade do starter propaga apenas aos vãos que ainda estavam no valor anterior (overrides preservados). | `types_closets.py:469-487` | 🟢 |
| CLOSETS-R13 | Starter HANGING cresce para baixo ao mudar a altura (topo fixo na parede). | `types_closets.py:507-515` | 🟢 |
| CLOSETS-R14 | Alturas de painel seguem o sistema 32 mm: `19 + n·32 mm` (Base 819, Hanging 1267, Tall 2131 mm). | `const_closets.py:32-40, 120-134` | 🟢 |
| CLOSETS-R15 | Prateleiras/varões adicionados no modal encaixam em furos `12,95 + n·32 mm` medidos do fundo interno do **vão** (alinha entre segmentos). | `const_closets.py:137-140`, `ops_closet.py:1670-1676` | 🟢 |
| CLOSETS-R16 | Grab: snap COARSE = retícula 32 mm (alturas/furos) ou 1/4 in (larguras); FINE = 1/8 in; Shift/OFF = livre; TAB alterna. | `op_grab_closet.py:41, 534-558, 841-845` | 🟢 |
| CLOSETS-R17 | Nº automático de vãos = `clamp(ceil(W / 42 in), 1, 9)` — nenhum vão acima de 42 in. | `types_closets.py:1749-1754`, `ops_closet.py:26-27` | 🟢 |
| CLOSETS-R18 | Recuo automático de 1/2 in em cantos internos na colocação; offset digitado substitui o recuo do seu lado. | `const_closets.py:73`, `ops_closet.py:724-755, 868-896` | 🟢 |
| CLOSETS-R19 | Ilha: detentes de corredor 30/36/42/48 in com janela de 1 in; raio de busca 240 in; Shift desativa. | `const_closets.py:78-80`, `ops_closet.py:1025-1052` | 🟢 |
| CLOSETS-R20 | Vizinho de canto qualifica se: ângulo 90° ± 5°, faixas de altura se sobrepõem (tol. 1/4 in), canto do vizinho a ≤ 8 in, borda do starter a ≤ 1 in; L-shelves excluídos. | `ops_closet.py:205-288` | 🟢 |
| CLOSETS-R21 | Folga de canto (default 12 in) encolhe o starter; redução total limitada para largura mínima 6 in, rateio proporcional; ponte superior/inferior + rodapé preenchem o vão real. | `ops_closet.py:2539-2653`, `types_closets.py:1279-1339` | 🟢 |
| CLOSETS-R22 | Frentes em meia-sobreposição: cada borda sobrepõe o painel/prateleira em `(esp − 1/8 in)/2`; face da frente afastada 1/8 in da carcaça; folga entre frentes 1/8 in. | `types_closets.py:716-721`, `const_closets.py:93-95` | 🟢 |
| CLOSETS-R23 | Porta dupla: `leaf = (width + lo + ro − gap)/2`; dobradiças para fora (LEFT/RIGHT), puxadores se encontram no centro. | `types_closets.py:781-797, 1120-1127` | 🟢 |
| CLOSETS-R24 | Porta do vão inteiro (bay door) suprime portas das openings no lado FRONT; lado BACK ainda não suportado. | `types_closets.py:1036-1045, 1100-1107` | 🟢 |
| CLOSETS-R25 | Pilha de gavetas preenche a abertura: destravadas dividem igualmente, mínimo 2 in; editar uma frente a trava; todas travadas ⇒ escala. | `types_closets.py:1813-1831`, `gpu_overlay_closets.py:710-719` | 🟢 |
| CLOSETS-R26 | Gaveteiro é "tampado" por prateleira fixa em `qty·(fh + gap) − st`; se já houver tampa no segmento ela é movida. Resultado: cada frente = `fh`. | `ops_closet.py:1949-1974`, `types_closets.py:2138-2140` | 🟢 |
| CLOSETS-R27 | Caixa de gaveta WOOD: altura = frente − 1,25 in; profundidade = profundidade − 0,5 in; largura = vão − 2·1/2 in; mín. 2 in; base 1/2 in acima da borda da frente. | `types_closets.py:825-860`, `const_closets.py:100-103` | 🟢 |
| CLOSETS-R28 | Metabox: alturas N54/M86/K118/H150 mm exigem abertura 78/110/142/174 mm; Avantech: 101/139/187/251 mm exigem altura+5 mm; corrediças 270–550 mm (maior que cabe); Illumination reserva 12,7 mm de profundidade; se nada couber usa o menor. | `drawer_boxes_closets.py:40-85` | 🟢 |
| CLOSETS-R29 | Curso de abertura da gaveta = `min(prof. da caixa, 12 in)`; porta abre 110°. | `types_closets.py:874, 1767` | 🟢 |
| CLOSETS-R30 | Varão: raio 1 in, eixo a 12 in da parede (limitado pela profundidade), centro ≥ raio das faces; default 2,5 in abaixo do topo, ancorado no topo. | `types_closets.py:736-746`, `const_closets.py:85-113` | 🟢 |
| CLOSETS-R31 | Cabides: 3 por varão (6 in das pontas + centro); só se varão > 14 in; modelos "que cabem" = queda ≤ folga − 0,5 in. | `pulls_closets.py:190-240, 176-187` | 🟢 |
| CLOSETS-R32 | Prateleiras reguláveis espaçadas igualmente: `z_i = interior_h·(i+1)/(n+1)`; qtd padrão ≈ 1 por 12 in (1–12; 1–8 no preset). | `types_closets.py:768-778, 1867-1875, 2159` | 🟢 |
| CLOSETS-R33 | Abrir portas semeia reguláveis só em abertura vazia; basculantes não recebem prateleiras. | `types_closets.py:2085-2099`, `ops_closet.py:2025-2036` | 🟢 |
| CLOSETS-R34 | Nichos: `cols−1` divisões de altura total e `rows−1` prateleiras de largura total; células iguais descontando `st`. | `types_closets.py:880-904, 1154-1183` | 🟢 |
| CLOSETS-R35 | Presets de vão: Double Hang (split ih/2), DH Top Shelf (faixa 12 in no topo), DH Mid Shelf (faixa 12 in no meio), Doors over N drawers (N=3–6), Doors Open N drawers (3 segmentos), Base/Upper/Full Height Doors. | `types_closets.py:2065-2222` | 🟢 |
| CLOSETS-R36 | Excluir o único vão exclui o starter inteiro; `delete_bay` remove o painel à direita (ou o da esquerda se for o último). | `ops_closet.py:1534-1543`, `types_closets.py:1404-1443` | 🟢 |
| CLOSETS-R37 | Inserir vão copia altura/profundidade/montagem do vão âncora, entra com largura 0 destravada (recebe parte igual). | `types_closets.py:1344-1402` | 🟢 |
| CLOSETS-R38 | Remover peça dirigida por config decrementa o idprop da abertura (reguláveis, gavetas, portas, nichos) em vez de apagar o objeto. | `ops_closet.py:2324-2390` | 🟢 |
| CLOSETS-R39 | Estilos de frente: montante/travessa por estilo (2,25 / 2,5–3 / 3 in); painel 1/4 in rebaixado 1/2 in; frente menor que o mínimo do estilo (ou < 2·montante + 1 in) vira slab. | `fronts_closets.py:46-69, 174-179` | 🟢 |
| CLOSETS-R40 | Veio: portas VERTICAL e gavetas HORIZONTAL por padrão; montantes sempre veio vertical; fitas de borda usam variante girada 90° em X. | `props_closets.py:281-294`, `materials_closets.py:139-150, 411-464` | 🟢 |
| CLOSETS-R41 | Painel de porta pode ser vidro (Clear/Mirror/Frosted); gavetas sempre painel de madeira; marca `IS_PREP_FOR_GLASS`. | `materials_closets.py:440-460` | 🟢 |
| CLOSETS-R42 | Puxador de porta: alvo 45 in do piso; porta acima disso usa convenção Upper (1,5 in da borda inferior); se o alvo passa do topo usa Base (1,5 in do topo); 2 in da borda (ou meio do montante em 5 peças). | `types_closets.py:960-992`, `props_closets.py:306-325` | 🟢 |
| CLOSETS-R43 | Moldura só em vãos com topo ≥ 60 in; retorna à parede nas pontas expostas e junto a vizinhos mais baixos; degrau para vizinho mais raso; não regenera sozinha (re-executar). | `molding_closets.py:26, 159-218, 393-405` | 🟢 |
| CLOSETS-R44 | Tampo: Base/Ilha têm por padrão; espessura 1,125 in; balanço frontal 1,875 in; ilha dupla balanço 1,5 in em todos os lados. | `types_closets.py:1244-1269`, `const_closets.py:15, 66, 106` | 🟢 |
| CLOSETS-R45 | Ilha dupla: profundidade 30 in, fundo central de espessura `st` no meio, openings FRONT e BACK com profundidade `(d − st)/2`. | `types_closets.py:623-651, 1480-1487` | 🟢 |
| CLOSETS-R46 | L-shelf: pegada 24×24 in, 3 prateleiras em L intermediárias + topo e base (entalhe CPM_CORNERNOTCH), tiras de parede 6 in, rodapés por asa; profundidades das asas limitadas a `W − pt`/`D − pt`. | `types_closets.py:1490-1709`, `const_closets.py:108-110` | 🟢 |
| CLOSETS-R47 | Arraste do fundo de um vão: base ≤ 1 in do piso ⇒ vão vira de piso; acima ⇒ suspenso com altura na retícula 32 mm; prateleiras divisoras mantêm altura absoluta. | `op_grab_closet.py:629-657, 501-525` | 🟢 |
| CLOSETS-R48 | Prateleira arrastada fica entre as vizinhas com folga mínima de 1 in; limites de vão ≥ `kick + 2·st + 1 in`; starter ≥ 6 in; vão ≥ 2 in no grab. | `op_grab_closet.py:36-40, 527-532, 676-704` | 🟢 |
| CLOSETS-R49 | Duplicar espelhado inverte a ordem dos vãos e troca LEFT↔RIGHT das portas (DOUBLE inalterado). | `ops_closet.py:360-386` | 🟢 |
| CLOSETS-R50 | Rótulo OPEN_H de um segmento tampado move a prateleira de tampa; no segmento do topo, reescreve a altura do vão `= valor + seg_bottom + 2·st + kick`. | `gpu_overlay_closets.py:635-670` | 🟢 |

### Constantes/enums

- **Espessuras/perfis** 🟢 (`const_closets.py:13-23`): painel/prateleira/fundo aplicado 0,75 in; tampo 1,125 in; cleat 4 in; trilho 1,125×0,25 in.
- **Starter** 🟢 (`:28-40`): largura 80 in, 4 vãos (default de `create_starter`; a colocação usa `auto_bay_qty`), profundidade 14 in,
  alturas 819/2131/1267 mm, topo suspenso 2131 mm.
- **Rodapé** 🟢 (`:45-61`): altura 96 mm, recuo 1,625 in; `KICK_HEIGHT_ITEMS` 64…320 mm em passos de 32 mm (sem uso no dropdown atual 🟡).
- **Frentes/gavetas** 🟢 (`:93-103`): frente 0,75 in, folgas 1/8 in, frente de gaveta 7,5 in, mínimo 2 in, corrediça 1/2 in por lado.
- **Sistema 32 mm** 🟢 (`:126-140`): passo 32 mm, base de altura 19 mm, base de furo 12,95 mm.
- **Enums** 🟢: `closet_type` BASE/TALL/HANGING/ISLAND (`props_closets.py:121-129`); `closet_selection_mode`
  Starters/Bays/Openings/Parts (`:225-234`); `BOX_TYPES` (`drawer_boxes_closets.py:30`); `FRONT_STYLES` (`fronts_closets.py:34`);
  `PANEL_TYPES` (`materials_closets.py:37`); `PULL_FINISHES`, `ROD_FINISHES`, `ROD_TYPES` OVAL("Signature")/ROUND (`pulls_closets.py:27-48`);
  `BAY_CONFIGS` (15 itens), `OPENING_CONFIGS` (12 itens) (`types_closets.py:2065-2239`); `KIND_ITEMS` do overlay (`gpu_overlay_closets.py:136`).
- **Papéis de peça** 🟢 (`types_closets.py:43-77`): `CLOSET_PANEL, _BOTTOM_SHELF, _TOP_SHELF, _TOE_KICK, _CLEAT, _HANG_RAIL,
  _COUNTERTOP, _APPLIED_BACK, _FIXED_SHELF, _ADJ_SHELF, _ROD, _DOOR_FRONT, _DRAWER_FRONT, _DRAWER_BOX, _CUBBY_DIVISION,
  _CUBBY_SHELF, _CENTER_BACK, _BRIDGE_SHELF`.
- **Tags** 🟢: `IS_CLOSET_STARTER_CAGE`, `IS_CLOSET_BAY_CAGE`, `IS_CLOSET_OPENING_CAGE`, `IS_CLOSET_HANGER`, `IS_CLOSET_MOLDING`,
  `IS_CABINET_PULL`, `MENU_ID`, `CLASS_NAME`, `HB_CURRENT_DRAW_OBJ`.
- **Tunables de UI** 🟢: grab `HIT_TOLERANCE_PX=12`; open door `ANIM_DURATION=0,35 s`, `TIMER_HZ=60`; overlay `FONT_SIZE=12`.

### Riscos Blender 5.2

| # | Risco | Local | Conf. |
|---|---|---|---|
| 1 | `Material.use_nodes` está **deprecado desde 5.0** (sempre True, remoção no 6.0) — usado como guarda em `_mapping_variant`. Ref.: `docs/rag/blender-api/corpus/bpy.types.Material.md#bpy.types.Material.use_nodes`. | `materials_closets.py:121` | 🟢 |
| 2 | Linhas grossas com shader `UNIFORM_COLOR` + `gpu.state.line_width_set(2/3)`: espessura > 1 não garantida (Metal/Vulkan); recomendado `POLYLINE_UNIFORM_COLOR` com `lineWidth`/`viewportSize` (`project/02_padroes_blender_5_2.md:146-149`). | `op_grab_closet.py:273-278, 301` | 🟢 |
| 3 | `LINE_LOOP` + `UNIFORM_COLOR` no contorno dos rótulos — ainda válido no 5.2 (`gpu.types.md:101`), baixo risco. | `gpu_overlay_closets.py:513` | 🟢 |
| 4 | Modo Open Door: `unregister()` não remove o `event_timer` nem encerra o modal se o modo estiver ativo; estado `_active` global. | `op_open_door_closet.py:92-100, 223-230` | 🟢 |
| 5 | `open_door_mode` grava idprops (`hb_door_open/hb_drawer_open`) com `bl_options={'REGISTER'}` sem `UNDO` (viola regra do projeto). `toggle_mode` altera cor/visibilidade sem `bl_options`. | `op_open_door_closet.py:82, 112-114`; `ops_closet.py:294-354` | 🟢 |
| 6 | `bpy.ops.hb_closets.toggle_mode` chamado dentro de **update callback** de propriedade — dependente de contexto, falha em background/contexto sem 3D view (sem try). | `props_closets.py:97-100` | 🟢 |
| 7 | Estado global do grab (`_drag_op`) não é resetado se o modal morrer (ex.: carregar arquivo) — `poll` exige `_drag_op is None` e o grab fica travado; não há `load_post`. | `op_grab_closet.py:55-59, 386-391` | 🟡 |
| 8 | Modais `place_starter`/`add_part` removem o handler de cotas em cancel/finish, mas não há `try/except` no `modal()`: exceção deixaria o handler de cotas órfão. | `ops_closet.py:1226-1330, 1744-1784` | 🟡 |
| 9 | Registro engole exceções (`register_class` em `try/except: pass`) — falhas de registro no 5.2 passam despercebidas. | `ops_closet.py:2881-2902`, `menus_closets.py:230-251` | 🟢 |
| 10 | Uso de `hb_utils.try_get_gn_input/set_gn_input` (helpers duplicados de `compat.py`) — correto para 5.2 (`mod.properties.inputs`), mas sujeito à dessincronia citada no CLAUDE.md. Nenhum `mod["Socket_X"]` direto no módulo. | `types_closets.py:972`, `materials_closets.py:152-158` | 🟢 |
| 11 | `user_hangers_dir` monta o pacote com `'.'.join(__package__.split('.')[:3])` — correto só quando instalado como extensão (`bl_ext.<repo>.blendertomob`); fora disso `extension_path_user` recebe pacote errado. | `pulls_closets.py:61-72` | 🟡 |
| 12 | Muitas **idprops soltas** (`obj['hb_*']`) guardam estado de negócio (qtd de gavetas, swing, offsets). São válidas no 5.x (não são `bpy.props`), mas não têm tipo/validação nem aparecem na UI/undo de forma tipada. Nenhum acesso `obj["hb_closet_*"]` a PropertyGroup foi encontrado. | `types_closets.py:52-100` | 🟢 |
| 13 | Objetos gerados (instâncias de puxador, cabides, perfil de moldura, curvas) são linkados em `scene.collection` e não na coleção do produto. | `types_closets.py:1001`, `pulls_closets.py:221`, `molding_closets.py:482, 523` | 🟢 |
| 14 | Guardas de reentrância por `id(obj)` do wrapper Python: `id` pode ser reaproveitado após exclusão/undo. | `types_closets.py:105-106, 461-464` | 🟡 |
| 15 | APIs verificadas OK no RAG: `KeyMapItems.new(..., head=True)`, `BlendDataLibraries.load(..., assets_only=True)`, `bpy.utils.extension_path_user`; `check_api.py` sem símbolos desconhecidos no módulo. | vários | 🟢 |

### Unidades e premissas de mercado

- **Unidades internas** 🟢: tudo em **metros** (unidades do Blender); `inch(v) = v·0,0254`, `millimeter(v) = v·0,001`
  (`blendertomob/data/units.py:96-103`). O módulo mistura **polegadas** (espessuras, folgas, recuos, profundidades) com **milímetros**
  (alturas do sistema 32 mm, caixas de gaveta) — `const_closets.py:1-5`.
- **Conflitos com marcenaria brasileira** 🟡:
  - Espessura 0,75 in = **19,05 mm** (painel/prateleira/frente/fundo aplicado); no Brasil predominam MDF/MDP **15 e 18 mm** (25 mm em tampos).
    O próprio sistema 32 mm usa base de 19 mm (coerente só com 19 mm).
  - Fundo "aplicado" de 3/4 in e "cleat" de 4 in (fixação americana); no Brasil é comum fundo de 3–6 mm encaixado/grampeado e fixação por
    suportes/cantoneiras.
  - Profundidade 14 in (355,6 mm) e ilha dupla 30 in (762 mm); roupeiros brasileiros costumam ter 550–600 mm (cabide frontal ao varão).
  - Vão máximo 42 in (1066,8 mm) sem apoio — acima do usual para prateleira de 15/18 mm (tipicamente ≤ 800–900 mm).
  - Varão a 12 in (304,8 mm) da parede, "Signature/Oval"; frente de gaveta 7,5 in; puxador de porta a 45 in do piso; corredores 30–48 in;
    moldura só acima de 60 in; tampo 1,125 in com balanço 1,875 in — todas convenções norte-americanas.
  - Sistemas de caixa Avantech (Hettich) e Metabox (Blum) existem no Brasil, mas a nomenclatura de alturas (N/M/K/H) e o catálogo de
    comprimentos 270–550 mm devem ser validados com fornecedores locais.
  - UI e rótulos em inglês; entrada digitada aceita pés/polegadas (`parse_typed_distance`).

### Dependências de outros módulos

🟢 `hb_types` (GeoNodeCage/Cutpart/Object/DrawerBox, CabinetPartModifier, GeoNodeWall), `hb_utils` (GN inputs), `hb_placement`
(PlacementMixin, duplicate_object_hierarchy, cotas, TypingTarget), `hb_snap`, `hb_gpu_draw`, `units`/`data.units`,
`product_libraries.frameless` (`CabinetPart`, `toggle_cabinet_color`), `product_libraries.face_frame` (`split_preview`, `pulls.pull_length`,
`_detect_wall`, `Face_Frame_Cabinet_Style._get_glass_panel_material`, `apply_active_finish_to_product`), `operators.viewport_hud`.
Node groups/Assets: `GeoNodeClosetRod`, `CPM_5PIECEDOOR`, `CPM_CORNERNOTCH`, `assets/materials/library.blend`,
`assets/materials/accessory_finishes.blend`, `assets/handles/*.blend`, `assets/hangers/*.blend`, `assets/moldings/crown/*.blend`,
`closet_thumbnails/*.png`. Consumidores: `blendertomob/__init__.py`, `ui/panels.py`, `operators/ops_general.py`, `operators/viewport_hud.py`.

### Lacunas

- 🔴 Não há **furação** explícita (linha de furos 32 mm para pinos/cavilhas, minifix): o sistema 32 mm só existe como retícula de *snap*;
  nenhuma operação de usinagem/furo é gerada pelo módulo ("the machining layer decides grain later", `types_closets.py:624-625`).
- 🔴 Sem integração visível com lista de corte/orçamento neste módulo (apenas idprops como `hb_pull_name` "pricing keys on it",
  `types_closets.py:1005-1007`, e `hb_drawer_box_size`); consumidor não localizado.
- 🔴 Frentes do lado BACK de ilha dupla: sem puxador e sem portas de vão (pendente, `types_closets.py:914-915, 1037-1039`).
- 🟡 `closet_type` não tem valor próprio para ilha dupla nem L-shelf (L "UPPER" é gravado como HANGING, `types_closets.py:1529-1531`).
- 🟡 Código morto em `LShelfClosetStarter.recalculate` (expressões sem efeito, `types_closets.py:1675, 1678`); docstring de
  `IslandClosetStarter` fica após um atributo e não é docstring (`:1471-1474`).
- 🟡 `DOORS_OPEN_*` não abre portas, apesar do comentário (`types_closets.py:2142-2143` vs `:2180-2186`); `_cfg_hamper` definido sem uso.
- 🟡 `spec.kick_setback` é enviado ao solver mas não usado lá.
- 🔴 Conteúdo dos `.blend` de assets (node groups `GeoNodeClosetRod`, `CPM_5PIECEDOOR`) não foi analisado — sockets inferidos pelos nomes usados.

---

## Módulo product_common

> Camada legada (fork do Home Builder 5). Nível: DETALHADO. Caminhos relativos a `blendertomob/`.
> Confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas: `_reversa_sdd/flowcharts/legacy-product_common*.md`. Mapeamento: `_reversa_sdd/product_common/legacy-mapping.md`.

### Propósito

Biblioteca compartilhada entre as linhas de produto (face frame e frameless) com quatro responsabilidades 🟢:

1. **Motor de portas em Python puro** (`door_builder.py`) — substitui o modificador GN `CPM_5PIECEDOOR`
   (chave `USE_PYTHON_DOORS = True`, `door_builder.py:27-30`). Gera o layout paramétrico de uma porta
   (montantes, travessas, mid rails/stiles, painéis) como dados lineares `(coef, offset)` e realiza a malha
   estática com perfis de borda, sticking aplicado, painel levantado (raised), ranhuras (beadboard/kerf),
   arcos (Arch/Crown/Double/Twin), mullions retos e curvos, construção mitered e fallback para slab.
2. **Biblioteca de perfis** (`door_profiles.py`) — carrega curvas de `.blend` e as converte em seções de
   varredura (u, v) por categoria (OUTER/INNER/PANEL/APPLIED/MITERED); gera perfis de borda de catálogo em código.
3. **Eletrodomésticos e coifas** — `types_appliances.py` (cages GN wireframe com dimensões padrão EUA) e
   `wood_hoods.py` (14 estilos de coifa de madeira construídos como peças filhas do cage `HOOD`, 3 operadores).
4. **Registries plugáveis de catálogo externo** — `accessory_registry.py` (providers por host) e
   `appliance_spec_registry.py` (provider único de specs de fabricante/modelo). O HB5 **não registra nenhum
   provider** (nenhuma chamada a `register_provider` no repositório 🟢 grep).

### Arquivos

| Arquivo | Linhas | Papel |
|---|---|---|
| `product_libraries/common/__init__.py` | 9 | reexporta `types_appliances`; `register/unregister` vazios 🟢 |
| `product_libraries/common/door_builder.py` | 1404 | layout + malha de porta 🟢 |
| `product_libraries/common/door_profiles.py` | 710 | perfis `.blend` → seções 🟢 |
| `product_libraries/common/types_appliances.py` | 220 | `Appliance` + 10 subclasses 🟢 |
| `product_libraries/common/wood_hoods.py` | 2243 | coifas de madeira + 3 operadores 🟢 |
| `product_libraries/common/Trash Pull Outs/Generic Trash Pullout.blend` | binário | asset sem referência em código (grep) 🟡 órfão |
| `accessory_registry.py` | 117 | registry host → provider 🟢 |
| `appliance_spec_registry.py` | 32 | registry de provider único 🟢 |

Observação: `wood_hoods` é registrado diretamente pelo `__init__.py` do add-on (`__init__.py:54,244,269`),
não pelo `register()` do pacote `common` (que é vazio) 🟢.

### Fluxo de controle

**door_builder**

| Função | Parâmetros | Retorno | Notas |
|---|---|---|---|
| `door_style_info(style=None)` `:87` | objeto `Face_Frame_Door_Style` ou None | `dict` (cópia de `DOOR_STYLE_FALLBACK` com `getattr`) | desacopla o cálculo de referências RNA 🟢 |
| `_frame_widths(info)` `:69` | info | `(lsw, rsw, msw, trw, brw, mrw)` | pisos 1/2" (uniformes) e 0.0 (por lado) 🟢 |
| `layout_min_size(info)` `:98` | info | `(min_w, min_h)` | abaixo disso o chamador deve construir SLAB 🟢 |
| `door_layout(info)` `:113` | info | `list[dict]` de peças com pares `(coef, offset)` | núcleo paramétrico 🟢 |
| `evaluate_layout(info, width, height)` `:215` | info, W, H (m) | peças + `x0,x1,z0,z1` absolutos | 🟢 |
| `build_mitered_frame(info, W, H, T, member_section)` `:250` | — | `(verts, faces, slots)` | 1 varredura com meia-esquadria + fundo plano 🟢 |
| `build_door_mesh(mesh, info, width, height, thickness, materials, outer_section, inner_section, panel_section, inner_rail_section, inner_stile_section, member_section, applied_section, applied_scope, panel_grooves, mullion, shape)` `:1202` | — | None (reescreve `mesh`) | orquestrador; cadeia de fallback por peça 🟢 |
| Emissores `_emit_*` `:349-1199` | listas mutáveis `verts/faces/slots`, part, T, seção | `bool` (False = não coube → caixa simples) | 🟢 |

Condicionais não triviais 🟢:
- MITERED só quando `member_section is not None and door_type != 'SLAB'` (`:1249-1250`); nesse caso só painéis
  entram no loop (`:1301-1302`), e `shape`, sticking e applied são ignorados (`:1267`, `:1366`, `:1379`), mas
  mullions são aplicados (`:1385-1388`).
- Cadeia por peça (`:1300-1362`): raised → grooved (+ tampas arqueadas) → shaped flat → shaped top rail →
  shaped bottom rail → edge-profiled box → caixa simples.
- Sticking: `lr = rail or inner or stile`, `ls = stile or inner or rail` (fallback cruzado, `:1370-1371`).

**door_profiles**: `load_profile` (`:85`) com cache `(path, mtime, res)`, `libraries.load` + remoção em
`finally` (`:105-126`); erros explícitos `FileNotFoundError` (`:99-100`) e `ValueError` (`:127-128`); as funções de
seção devolvem `None` quando o desenho não é legível (`:284-285`, `:321-322`, `:354-355`, `:387-391`, `:444-445`,
`:475-476`) e o consumidor cai para borda reta/painel plano com `try/except` amplo
(`face_frame/props_hb_face_frame.py:3528-3645`) 🟢.

**types_appliances**: `Appliance.create_appliance(name, appliance_type)` (`:19-51`) cria o cage GN, grava ID props
`IS_APPLIANCE`, `APPLIANCE_TYPE`, `MENU_ID='HOME_BUILDER_MT_appliance_commands'`, `display_type='WIRE'`, define
`Dim X/Y/Z` e `Mirror Y=True`, e cria um `GeoNodeText` filho com drivers `x = dim_x/2`, `y = -dim_y`,
`z = dim_z/2`, rotacionado 90° em X 🟢. Cada subclasse chama `create_appliance` e adiciona propriedades via
`add_property` 🟢.

**wood_hoods**:
- `build_wood_hood(hood, style)` (`:1762`): limpa peças (`_clear_hood_parts`, preserva `IS_MANUAL_PART`),
  despacha em `_STYLE_BUILDERS.get(style, _build_box)`, grava `WOOD_HOOD_STYLE` e reaplica o acabamento do estilo
  de armário 🟢.
- Operadores 🟢: `blendertomob.build_wood_hood` (`:1773`, `{'REGISTER','UNDO'}`, poll: `APPLIANCE_TYPE=='HOOD'`);
  `blendertomob.wood_hood_prompts` (`:1804`, `{'UNDO'}`, `check()` reconstrói a cada alteração `:2059-2061`,
  5 abas SHAPE/MANTLE/FRONT/ENDS/LINER); `blendertomob.revert_hood_part` (`:2193`, `{'UNDO'}`).
- Tratamento de erro: imports tardios de `face_frame` envoltos em `try/except Exception` que retornam None / no-op
  (`:430-442`, `:452-459`, `:470-475`, `:1594-1601`) — coifas não dependem rigidamente do face_frame 🟢.
- `snapshot_hood_part` / `restore_hood_part` (`:1635`, `:1688`): serializam receita paramétrica (node group,
  inputs, drivers SINGLE_PROP, transform) em JSON; restore re-aponta variáveis para o cage raiz e migra caminhos
  de driver entre formatos pré-5.2 e 5.2 (`_migrate_mod_input_path` `:51-54`) 🟢.

**Registries**: `get_items`/`all_items` capturam `Exception` do provider, imprimem
`"HB5 accessory_registry: provider for %s failed"` e seguem (`accessory_registry.py:28-54`) 🟢.

### Algoritmos e regras

Algoritmos principais 🟢:
- **Layout linear (coef, offset)** — `door_layout` (`door_builder.py:113-212`); permite realização estática
  (`evaluate_layout`) ou composição direta em expressões de driver (`wood_hoods.py:659-749`, `:887-902`).
- **Varredura com meia-esquadria** de seções (u, v) em volta de retângulos/perímetros com arcos, direção
  `(n1+n2)/(1+n1·n2)` (`door_builder.py:621-657`; `door_profiles.py:680-710`).
- **Reamostragem de laço fechado por comprimento acumulado** (`_resample_loop` `:324-346`) para unir strips de
  rail/stile com contagens diferentes de pontos.
- **Sutherland-Hodgman** (recorte por semiplano, `_clip_half` `:660-675`) para mullions e barras sob curvas.
- **Arco circular por flecha**: `R = (rise² + (w/2)²)/(2·rise)`; **ogiva Crown** por Bézier cúbica
  P0=(0,0), P1=(0.22w,0), P2=(0.30w,rise), P3=(0.5w,rise), espelhada (`:585-618`).
- **Amostragem Bézier cúbica** de splines de perfil e projeção no plano de maior extensão
  (`door_profiles.py:56-82`, `:130-146`).
- **Detecção de orientação de desenho** por "face run" / canto do cavaco na origem
  (`door_profiles.py:166-242`, `:525-610`).
- **Ajuste à espessura** esticando apenas o trecho reto atrás do cortador (`door_profiles.py:598-610`).
- **Perfil frontal por partes da coifa** (`_FrontProfile`, `wood_hoods.py:1082-1157`): altura ↔ comprimento de
  arco, afunilamento, offset em meia-esquadria nas quebras.
- **Distribuição de cursos de shiplap** por comprimento de arco com revelação (`wood_hoods.py:1196-1219`).

Regras de negócio:

| ID | Regra | Local | Conf. |
|---|---|---|---|
| PRODUCT_COMMON-R01 | Larguras uniformes de montante, travessa e mid rail têm piso de 1/2"; overrides por lado caem na uniforme quando `None` e só têm piso 0.0 (um lado 0.0 elimina o membro para portas espelhadas se encostarem). | `door_builder.py:69-84`, `:52-55` | 🟢 |
| PRODUCT_COMMON-R02 | Espessura do painel tem piso de 1/8"; recuo do painel (`panel_inset`) piso 0. | `door_builder.py:142-143` | 🟢 |
| PRODUCT_COMMON-R03 | Tamanho mínimo da porta de 5 peças: `min_w = lsw + rsw + m·msw + 1/2"`, `min_h = trw + brw + k·mrw + 1/2"` (k = nº de mid rails efetivos, 1 se `add_mid_rail` ou `mid_rail_z`); SLAB → (0,0). No mínimo ou abaixo, a coifa troca a porta por SLAB. | `door_builder.py:98-110`; `wood_hoods.py:729-731`, `:883-886`, `:994-996`, `:1304-1307` | 🟢 |
| PRODUCT_COMMON-R04 | Frentes de armário usam mínimo próprio mais rígido: `2 montantes + 1"` e `2 travessas + 1"` (+ mid rail se houver), divergente do +1/2" de `layout_min_size`. | `face_frame/props_hb_face_frame.py:3406-3423` | 🟢 |
| PRODUCT_COMMON-R05 | Precedência do mid rail: `mid_rail_count > 0` > `mid_rail_z` explícito > `add_mid_rail` (centralizado `(0.5, −mrw/2)` ou fixo `max(mid_rail_location, brw)` a partir da base). | `door_builder.py:61-65`, `:161-190` | 🟢 |
| PRODUCT_COMMON-R06 | k mid rails equidistantes: altura do campo `fh = H − (trw + brw + k·mrw)`; linha i começa em `fh·i/(k+1) + brw + i·mrw`, com altura `fh/(k+1)`. | `door_builder.py:161-173` | 🟢 |
| PRODUCT_COMMON-R07 | m mid stiles equidistantes: largura de coluna `(W − (lsw + rsw + m·msw))/(m+1)`; mid stiles são segmentados por linha de painel (construção de porta de 6 painéis). | `door_builder.py:193-207` | 🟢 |
| PRODUCT_COMMON-R08 | Painéis ficam recuados da face por `y_inset` e usam espessura própria; membros de quadro usam a espessura da porta (`thickness=None`). | `door_builder.py:122-125`, `:210-211`, `:1351-1353` | 🟢 |
| PRODUCT_COMMON-R09 | Porta MITERED: todo o membro é um único perfil; a largura do membro (`max u`) vira largura do quadro nos 4 lados (overrides por lado não se aplicam) e não há mid rail; arcos, sticking e applied são ignorados; mullions valem. | `door_builder.py:1249-1253`, `:1366`, `:1379`, `:1385-1388`; `face_frame/props_hb_face_frame.py:3337-3358`, `:3498-3501` | 🟢 |
| PRODUCT_COMMON-R10 | Painel raised cai para caixa plana quando `min(w, h) ≤ 2·field_u` ou quando não há profundidade atrás do plano do campo (`thickness − y_inset ≤ 0`). | `door_builder.py:460-466` | 🟢 |
| PRODUCT_COMMON-R11 | Ranhuras (beadboard/kerf) só em painel plano (ignoradas com raise); KERF = 1/8" de largura × 3/32" de profundidade; BEAD = quirk 1/16" + conta de raio 0.09" + profundidade 0.11"; padrão centrado com prancha central sobre a linha de centro; ranhuras a menos de `max(2·meia-largura, 4 mm)` da borda são descartadas; profundidade ≥ espessura do painel → sem ranhura. | `door_builder.py:497-571`, `:1314-1317` | 🟢 |
| PRODUCT_COMMON-R12 | Rise do arco: ARCH `min(0.20·w, 2.25")`; CROWN `min(0.16·w, 1.75")`, onde w = largura da célula; limitado ainda por `shape['rise']`. | `door_builder.py:576-582`, `:1284-1287` | 🟢 |
| PRODUCT_COMMON-R13 | Arco aplica-se às células da linha de topo; nas formas Double também à linha de base; Twin força 1 mid stile (um arco por vidro). O chamador alarga a(s) travessa(s) pelo rise para manter a largura de catálogo na crista; célula ≤ 2" desliga o arco. | `door_builder.py:1263-1298`; `face_frame/props_hb_face_frame.py:3382-3404`, `:3523-3526` | 🟢 |
| PRODUCT_COMMON-R14 | Perfil de borda externa só é cortado nos lados da peça que estão no contorno da porta (slab, montantes e travessas externas); lados internos ficam com u=0 para casar com o vizinho; se `u_max` não cabe na peça, borda reta. | `door_builder.py:1054-1119` | 🟢 |
| PRODUCT_COMMON-R15 | Travessa arqueada: o perfil externo é descartado se não couber no material restante acima (abaixo) do pico da curva. | `door_builder.py:1149-1161` | 🟢 |
| PRODUCT_COMMON-R16 | Sticking strip é pulado em células com `w ≤ 2·largura_strip_stile` ou `h ≤ 2·largura_strip_rail`. Rail/stile com laços diferentes são reamostrados para o mesmo nº de pontos e as esquadrias fechadas com faixas de transição. | `door_builder.py:362-367`, `:401-443` | 🟢 |
| PRODUCT_COMMON-R17 | Moldura aplicada com `scope='RAILS'` corre só no topo/base da abertura, com tampas planas; ignora bordas arqueadas. | `door_builder.py:373-399`, `:356-360` | 🟢 |
| PRODUCT_COMMON-R18 | Mullion GRID (Wood Mullion): 2 vidros na largura; linhas pela tabela de altura (≤24" → 2, ≤36" → 3, ≤48" → 4, senão 5); vertical só se `w > bw + 2"`; horizontais a menos de 1" das bordas são puladas. | `door_builder.py:696-712` | 🟢 |
| PRODUCT_COMMON-R19 | Mullion MISSION: 3 vidros iguais no terço superior (`zb0 = h − h/3 − bw`); inválido se `zb0 ≤ 1"` ou `w ≤ 3·bw + 3"`. PRAIRIE: barras a 2" das bordas (vidros 2×2 nos cantos); inválido se `w` ou `h ≤ 2·(2" + bw) + 1"`. X: diagonal descendente em meia-madeira em volta da ascendente. | `door_builder.py:713-766` | 🟢 |
| PRODUCT_COMMON-R20 | Mullions curvos (GOTHIC, DBL_GOTHIC, DBL_BOW, INTERLOKEN) vêm de centerlines normalizadas traçadas do catálogo, esticadas ao aspecto da abertura; largura padrão da barra 7/8"; profundidade = plano do vidro (`eff_panel_inset`); escalonamento de 0.2 mm por segmento evita z-fighting. | `door_builder.py:842-1051`; `face_frame/props_hb_face_frame.py:3636-3641` | 🟢 |
| PRODUCT_COMMON-R21 | Slots de material: 0 = stile (slab, montantes, mid stiles, barras de mullion), 1 = rail (travessas, mid rails, strips de sticking/applied em travessas), 2 = panel. `materials` é tripla (stile, rail, panel). | `door_builder.py:230-235`, `:1244-1247`, `:1396-1403` | 🟢 |
| PRODUCT_COMMON-R22 | Perfis são arquivos `.blend` com uma curva; vence a spline com mais pontos; cache invalidado pelo mtime do arquivo. | `door_profiles.py:85-150` | 🟢 |
| PRODUCT_COMMON-R23 | Ajuste de perfil à espessura da porta preserva a forma do cortador, esticando só o trecho reto de borda atrás do ponto moldado mais profundo; porta mais fina que a região moldada → escala todo v. | `door_profiles.py:598-610` | 🟢 |
| PRODUCT_COMMON-R24 | Profundidade do raise do painel limitada a `max_depth` (= espessura − recuo do painel) para não atravessar o fundo da porta. | `door_profiles.py:368-371`; `face_frame/props_hb_face_frame.py:3600-3608` | 🟢 |
| PRODUCT_COMMON-R25 | Sticking em painel recuado assenta no plano do painel (`panel_front`); em painel raised corre até a profundidade natural da curva. | `door_profiles.py:399-402`; `face_frame/props_hb_face_frame.py:3560-3564` | 🟢 |
| PRODUCT_COMMON-R26 | Perfis de borda de catálogo gerados em código: 1/8", 1/4", 3/8" radius (roundover); chamfer / 3/16" chamfer (3/16×3/16 a 45°); beveled (3/4" na face × 1/4" na borda); bay (cove côncavo 3/8"). Nomes desconhecidos (Square, Estate, Eclipse, New Cut…) → borda reta (`None`). Lookup case-insensitive com `strip()`. | `door_profiles.py:613-677` | 🟢 |
| PRODUCT_COMMON-R27 | Moldura aplicada OUT fica saliente sobre a face (u=−x, v=−y); IN assenta sobre o painel dentro da abertura (u=x, v=panel_front−y); o próprio desenho define a posição. | `door_profiles.py:428-459` | 🟢 |
| PRODUCT_COMMON-R28 | Dimensões padrão (L × A × P, polegadas): Appliance 30×36×24; Range 30×36×25; Cooktop 30×4×21; WallOven 30×29×24; Dishwasher 24×34×24; Refrigerator 36×70×30; Microwave 24×12×14; Hood 30×6×20; Sink 33×10×22; WashingMachine 27×38×30; Dryer 27×38×30. | `types_appliances.py:11-13`, `:57-59`, `:73-75`, `:85-87`, `:107-109`, `:121-123`, `:145-147`, `:167-169`, `:183-185`, `:199-201`, `:212-214` | 🟢 |
| PRODUCT_COMMON-R29 | Só Range e Hood têm `variable_width=True` (colocação permite override de largura digitada, ex.: coifa acompanhando o fogão). | `types_appliances.py:14-17`, `:60`, `:170` | 🟢 |
| PRODUCT_COMMON-R30 | Forno duplo: altura 51" (simples 29"); geladeira counter-depth: profundidade 24" (padrão 30"); micro-ondas over-range: 30×17×16. | `types_appliances.py:95-101`, `:133-139`, `:156-161` | 🟢 |
| PRODUCT_COMMON-R31 | Cooktop e Sink são marcados `IS_COUNTERTOP_APPLIANCE=True` (instalados no tampo). | `types_appliances.py:79`, `:189` | 🟢 |
| PRODUCT_COMMON-R32 | Propriedades do tipo `'TEXT'` (Hood "Hood Style", Sink "Sink Type") não são tratadas por `add_property` (só CHECKBOX, DISTANCE, ANGLE, PERCENTAGE, QUANTITY, COMBOBOX) → essas propriedades nunca são criadas (bug silencioso). | `types_appliances.py:176`, `:192`; `hb_props.py:335-374` | 🟢 |
| PRODUCT_COMMON-R33 | Material da coifa fixo em 3/4" (`HOOD_MATERIAL`); carcaça: laterais em altura total recuadas 3/4" da face, tampo inserido entre as laterais, frente aplicada em largura total cobrindo as bordas. | `wood_hoods.py:39`, `:151-203` | 🟢 |
| PRODUCT_COMMON-R34 | Presets de estilo: SHELF banda 5" proj. 2"; NICHE banda 6" proj. 1.5"; MANTLE/PLANTATION banda 6" proj. 2" + 2 painéis; GRAND_MANTLE banda 8" + crown 5" proj. 2" + 2 painéis; TRADITIONAL inclinada topo 12"; VILLA topo 12" + crown 5" + banda 6"; CHIMNEY topo 6" + banda 6"; SHIPLAP_MANTLE banda 6" proj. 2"; BOX/PENINSULA/SHIPLAP_BOX/SHIPLAP_PENINSULA caixa simples. Estilo desconhecido → BOX. | `wood_hoods.py:264-358`, `:1511-1541`, `:1767` | 🟢 |
| PRODUCT_COMMON-R35 | Painéis frontais aplicados (MANTLE etc.): montante/travessa 2.5", separação central 3", 1/2" de saliência; 2 portas → largura `(W − 2·2.5" − 3")/2`. | `wood_hoods.py:227-261` | 🟢 |
| PRODUCT_COMMON-R36 | Estilos inclinados (TRADITIONAL/VILLA/CHIMNEY), shiplap e molduras de mantle são malhas estáticas (não acompanham o cage até reconstruir); estilos retos são cutparts com drivers. | `wood_hoods.py:279-294`, `:305-310`, `:1160-1168`, `:1457-1459` | 🟢 |
| PRODUCT_COMMON-R37 | CUSTOM: `top_depth` limitado a [1", D]; `top_width` a [2·3/4" + 2", W]; `H ≥ 1"`; `top_height` a [0, H − banda − 1"]; mantle assembly só se `mantle_depth > 1/8"`; `panel_count` 1..10; `door_mid_rails`/`door_mid_stiles` 0..6; shiplap 4/5/6". | `wood_hoods.py:1335-1352`; `:1914-1958` | 🟢 |
| PRODUCT_COMMON-R38 | Frente de baia: PANEL (painel inset 1/4", fundo rente ao fundo do quadro), OVERLAY_DOOR (sobreposição da `_OVERLAY_TABLE` do estilo; sem estilo ou estilo inset → 1/2" em todos os lados), INSET_DOOR (folga 1/8" = `DOOR_TO_FRAME_GAP`, rente à face); valores inválidos/ausentes → PANEL. | `wood_hoods.py:398-423`, `:445-459`, `:666-731` | 🟢 |
| PRODUCT_COMMON-R39 | Quadro frontal/paneled end: largura de montante e travessas com piso de 1/2"; aberturas `(W − (n+1)·sw)/n`; paneled end/quadro inclinado não é construído se não couber (mantém lateral/frente simples). | `wood_hoods.py:610-657`, `:766-773`, `:917-926`, `:1026-1058` | 🟢 |
| PRODUCT_COMMON-R40 | Recorte do exaustor na prateleira liner: largura ≤ `W − 2·3/4" − 2"`, profundidade ≤ `interior − 2"`; deslocamento limitado a ±`(interior − cd)/2`; recorte zero → prateleira sólida; altura do piso limitada a [0, H − 2"]. | `wood_hoods.py:509-564`, `:1443` | 🟢 |
| PRODUCT_COMMON-R41 | Shiplap: tábua padrão 6" (mín. 1"), revelação 1/8", saliência 1/2", cantos a 45° em planta; último curso aparado se sobra > 1/4". | `wood_hoods.py:1160-1219` | 🟢 |
| PRODUCT_COMMON-R42 | Moldura do mantle: altura do friso limitada a [1/4", banda]; saliência mínima 1/8". | `wood_hoods.py:573-574` | 🟢 |
| PRODUCT_COMMON-R43 | Reconstrução preserva peças marcadas `IS_MANUAL_PART` (edições manuais sobrevivem). | `wood_hoods.py:82-88` | 🟢 |
| PRODUCT_COMMON-R44 | Snapshot só para peças com modificador GN (malhas estáticas não são reversíveis); reverter exige `IS_WOOD_HOOD_PART` + `IS_MANUAL_PART` + snapshot; sucesso remove ambos os flags. | `wood_hoods.py:1641-1646`, `:1755-1757`, `:2206-2211` | 🟢 |
| PRODUCT_COMMON-R45 | Primeira abertura dos prompts numa coifa sem opções CUSTOM semeia `top_width = width/2`; todas as 10 escolhas de baia são persistidas mesmo com menos baias ativas. | `wood_hoods.py:2010-2012`, `:2044-2047` | 🟢 |
| PRODUCT_COMMON-R46 | Opções antigas `panel_rail_width` migram para `panel_top_rail_width` e `panel_bottom_rail_width`. | `wood_hoods.py:501-505` | 🟢 |
| PRODUCT_COMMON-R47 | Accessory provider: função sem argumentos que devolve dicts com ao menos `code` e `name` (opcionais `category`, `min_opening_w`, `section`, `group`); `all_items` injeta `host`; códigos são considerados únicos entre hosts (`find` devolve o primeiro); falha do provider → lista vazia + print. | `accessory_registry.py:1-117` | 🟢 |
| PRODUCT_COMMON-R48 | Hosts de acessórios esperados pelo consumidor: `opening_interior_pullout`, `opening_interior_accessory`, `tall_pantry`, `behind_door_rollout`, `pullout_board`, `tilt_out`, `closet_rod`, `door_mounted` (só abertura com porta), `drawer_accessory` (só gaveta), `blind_corner_hardware` (só armário de canto cego). | `face_frame/operators/ops_cabinet.py:2300`, `:2585-2616` | 🟢 |
| PRODUCT_COMMON-R49 | Appliance spec provider: um único objeto (registro sobrescreve) com `manufacturers()`, `models(mfr)` → `[{model, series, appliance_type}]` e `resolve(mfr, model)` → dict com ao menos `operator_config`, `operator_panel_type` (A/B/C), `appliance_dim_x_m`, `weight_max_lb`, `panels`, `flags`; sem provider, só entrada manual. | `appliance_spec_registry.py:1-32`; `face_frame/operators/ops_appliance_panels.py:518-545` | 🟢 |

### Constantes/enums

| Constante | Valor | Local | Conf. |
|---|---|---|---|
| `USE_PYTHON_DOORS` | `True` | `door_builder.py:30` | 🟢 |
| `DOOR_STYLE_FALLBACK` | `door_type='5_PIECE'`, stile/rail/mid_rail 3", `mid_rail_location` 12", panel 1/2" esp., 1/4" recuo, counts 0, overrides None | `door_builder.py:36-66` | 🟢 |
| `door_type` | `'5_PIECE'`, `'SLAB'` | `door_builder.py:37`, `:102`, `:137` | 🟢 |
| chaves de peça | `slab, left_stile, right_stile, top_rail, bottom_rail, mid_rail, mid_stile, panel` | `door_builder.py:117-118` | 🟢 |
| `_OUTLINE_EDGE_KEYS` | `slab, left_stile, right_stile, top_rail, bottom_rail` | `door_builder.py:1058-1059` | 🟢 |
| curvas | `ARCH`, `CROWN` (+ `double`, `rise`) | `door_builder.py:576-618`, `:1236` | 🟢 |
| padrões de mullion | retos `GRID, MISSION, PRAIRIE, X`; curvos `GOTHIC, DBL_GOTHIC, DBL_BOW, INTERLOKEN` | `door_builder.py:686-691`, `:849-974` | 🟢 |
| estilos de ranhura | `BEAD`, `KERF` | `door_builder.py:497-515` | 🟢 |
| `applied_scope` | `ALL`, `RAILS` | `door_builder.py:350`, `:373` | 🟢 |
| `PROFILE_DIRS` | OUTER, INNER, PANEL, APPLIED, MITERED | `door_profiles.py:31-37` | 🟢 |
| `applied_strip side` | `OUT`, `IN` | `door_profiles.py:434-439` | 🟢 |
| `_EDGE_SECTION_BUILDERS` | 7 nomes (ver R26) | `door_profiles.py:642-655` | 🟢 |
| `APPLIANCE_TYPE` | RANGE, COOKTOP, WALL_OVEN, DISHWASHER, REFRIGERATOR, MICROWAVE, HOOD, SINK, WASHING_MACHINE, DRYER | `types_appliances.py:63-213` | 🟢 |
| ID props do eletrodoméstico | `IS_APPLIANCE`, `APPLIANCE_TYPE`, `MENU_ID`, `IS_APPLIANCE_TEXT`, `IS_COUNTERTOP_APPLIANCE` | `types_appliances.py:27-29`, `:46`, `:79`, `:189` | 🟢 |
| `HOOD_PART_TAG` / `HOOD_STYLE_PROP` / `HOOD_CUSTOM_PROP` / `HOOD_SNAPSHOT_PROP` | `IS_WOOD_HOOD_PART` / `WOOD_HOOD_STYLE` / `WOOD_HOOD_CUSTOM_OPTS` / `HOOD_PARAMETRIC_SNAPSHOT` | `wood_hoods.py:29-38` | 🟢 |
| `HOOD_MATERIAL` | 3/4" | `wood_hoods.py:39` | 🟢 |
| `WOOD_HOOD_STYLE_ITEMS` | BOX, SHIPLAP_BOX, SHIPLAP_MANTLE, SHIPLAP_PENINSULA, SHELF, NICHE, MANTLE, PENINSULA, TRADITIONAL, VILLA, CHIMNEY, PLANTATION, GRAND_MANTLE, CUSTOM | `wood_hoods.py:56-71` | 🟢 |
| `_BAY_FRONT_KINDS` | PANEL, OVERLAY_DOOR, INSET_DOOR | `wood_hoods.py:402-408` | 🟢 |
| `ui_tab` | SHAPE, MANTLE, FRONT, ENDS, LINER | `wood_hoods.py:1823-1832` | 🟢 |
| `hb_part_role` | `INSET_PANEL` | `wood_hoods.py:715`, `:821` | 🟢 |
| `MENU_ID` de peça | `HOME_BUILDER_MT_face_frame_part_commands` | `wood_hoods.py:96`, `:289` | 🟢 |

### Riscos Blender 5.2

| Risco | Local | Conf. |
|---|---|---|
| `restore_hood_part` recria drivers em caminhos `modifiers["X"].properties.inputs.Socket_N.value` (formato 5.2) via `driver_add`; a viabilidade de `driver_add` nesse caminho RNA não foi verificada no RAG. | `wood_hoods.py:1731-1754`, `:41-54` | 🟡 |
| Snapshot persiste caminhos no formato da versão que salvou; a migração regex cobre só o padrão `modifiers["..."]["Socket"]` ↔ `.properties.inputs.X.value` — variáveis com outros formatos não são migradas. | `wood_hoods.py:46-54` | 🟡 |
| `wood_hoods` usa `hb_utils.GN_INPUTS_AS_RNA` / `get_gn_input` / `set_gn_input` (helpers duplicados) em vez de `compat.py` — CLAUDE.md exige manter sincronizados ou consolidar. | `wood_hoods.py:52`, `:1665`, `:1723`; `hb_utils.py:13` vs `compat.py:9` | 🟢 |
| Anotações dinâmicas no corpo da classe (`__annotations__['bay_front_%d']` em laço) — funciona com anotações ansiosas; quebraria com a semântica PEP 649 (Python 3.14). Versão do Python embarcado no 5.2 não confirmada. | `wood_hoods.py:1920-1924` | 🟡 / 🔴 versão |
| `bpy.data.libraries.load` + append/remove de objetos a cada carga de perfil não cacheada; pode ocorrer dentro de update de propriedade/recalc (contexto restrito) e deixar datablocks órfãos (materiais/curvas com usuários). | `door_profiles.py:105-126` | 🟡 |
| `mesh.attributes.new('material_index', 'INT', 'FACE')` + `foreach_set` — API válida (check_api OK), mas depende de `materials.clear()` antes (comentário `:1396`). | `door_builder.py:1394-1404` | 🟢 |
| ID props diretas (`obj['IS_APPLIANCE']`, `obj['Is Double Oven']`, `obj['Counter Depth']`, `hood['WOOD_HOOD_CUSTOM_OPTS']` dict) são propriedades de ID (não `bpy.props`), portanto compatíveis com 5.0+. | `types_appliances.py:27-29`, `:101`, `:139`; `wood_hoods.py:2023` | 🟢 |
| `python3 docs/rag/tools/check_api.py` → "OK: no unknown API references found" (execução nesta análise). | — | 🟢 |

### Unidades e premissas de mercado

- **Tudo em polegadas** convertidas via `units.inch` para metros internos 🟢 (`door_builder.py:24`,
  `types_appliances.py:5`, `wood_hoods.py:25`); `door_profiles` tem `_INCH = 0.0254` próprio (`:619`) 🟢.
  Perfis `.blend` são desenhados "em escala real" (m) 🟢 (`door_profiles.py:5-6`).
- **Chapa de 3/4" (19,05 mm)** fixa na coifa (`HOOD_MATERIAL`) — conflita com MDF/MDP brasileiro de 15/18/25 mm 🟢.
- **Painel recuado 1/4" a 1/8" do fundo** (padrão CWP), sobreposição 1/2", folga de porta inset 1/8", mid rail
  automático acima de 45.5" (consumidor) — convenções americanas de *face frame* e *inset*, pouco usuais na
  marcenaria brasileira (predominantemente frameless/32 mm, sobreposição total com dobradiça caneco) 🟢/🟡.
- **Catálogo CWP** (fornecedor norte-americano): séries (Shaker, Beckony, Brunswick…), padrões de mullion
  (pdf 143-144), perfis de borda (pdf 147), faixas de preço "Prairie up to 30"/48"" — referências literais no
  código 🟢 (`door_builder.py:683-693`, `:842-848`; `door_profiles.py:614-651`).
- **Eletrodomésticos com tamanhos EUA** (fogão 30", lava-louças 24", geladeira 36"×70", lavadora 27") e
  propriedades como "CFM Rating" (400) e "Gas" — não correspondem a medidas usuais no Brasil (ex.: fogão 4/5 bocas
  ~ 51–76 cm, cooktop 60/75 cm) 🟢/🟡.
- **Specs de painel de eletrodoméstico em libras** (`weight_max_lb`) e rótulo `"(min %g\")"` para
  `min_opening_w` em polegadas no consumidor 🟢 (`appliance_spec_registry.py:9`; `ops_cabinet.py:2328`).
- Estilos de coifa (Mantle, Plantation, Villa, Chimney, Shiplap) e beadboard/shiplap são estética americana 🟡.
- Textos de UI em inglês (contraria regra de UI em português para código novo) 🟢.

### Dependências de outros módulos

| Dependência | Uso | Conf. |
|---|---|---|
| `units.inch` | conversão de todas as medidas | 🟢 |
| `hb_types.GeoNodeCage`, `GeoNodeObject`, `GeoNodeCutpart` | cages/peças GN, `set_input`, `var_input`, `driver_input`, `driver_location`, `add_part_modifier('CPM_CUTOUT')` | 🟢 |
| `hb_details.GeoNodeText` | texto de anotação do eletrodoméstico | 🟢 |
| `hb_utils` (`GN_INPUTS_AS_RNA`, `get_gn_input`, `set_gn_input`) | snapshot/restore | 🟢 |
| `hb_props.add_property` (via `obj.home_builder`) | propriedades de eletrodoméstico | 🟢 |
| `bpy.context.scene.home_builder.annotation_text_size` | tamanho do texto | 🟢 |
| `face_frame.props_hb_face_frame` (`get_style_props`, `cabinet_styles`, `door_styles`, `_OVERLAY_TABLE`, `door_overlay_type`, `assign_style_to_hood`) | estilo/acabamento/sobreposição da coifa (import tardio, protegido) | 🟢 |
| `face_frame.style_options` (`SERIES_FRAME`, `SERIES_PROFILES`, `PANEL_KINDS`, `SHAPE_KINDS`, `RECESSED_PANEL`) | dados de catálogo que parametrizam o motor de portas (consumidor) | 🟢 |
| Assets `face_frame/face_frame_assets/door_profiles/*` | perfis `.blend` | 🟢 |
| Consumidores: `face_frame` (props, ops_cabinet, ops_appliance_panels, ops_styles, ops_part_commands, types_face_frame), `frameless` (ops_placement, props_elevation_templates, menus_frameless, ops_countertop), `__init__.py` | — | 🟢 |

### Lacunas

- 🔴 Nenhum provider de `accessory_registry` / `appliance_spec_registry` existe no repositório; o formato real dos
  dados de catálogo (além das chaves lidas) não é observável.
- 🔴 `Trash Pull Outs/Generic Trash Pullout.blend` não é referenciado em código; não se sabe se é carregado pelo
  navegador de assets ou se é asset morto.
- 🔴 Versão do Python embarcado no Blender 5.2 (relevante para o risco de `__annotations__` dinâmico).
- 🟡 Mapeamento de perfis por série e larguras de quadro por série estão em `face_frame/style_options.py`, não em
  `door_profiles.py` — o nome do arquivo sugere o contrário; tratar como dependência.
- 🟡 Nomes de perfis de borda de catálogo sem builder (Estate, Eclipse, New Cut…) viram borda reta silenciosamente.
- 🟡 `PENINSULA`/`SHIPLAP_PENINSULA` ("finished all sides") constroem a mesma caixa com parede traseira aberta que
  BOX; `PLANTATION` é idêntico a `MANTLE` — builders dedicados "são um follow-up" (`wood_hoods.py:1764-1765`).
- 🟡 Divergência de mínimos (+1/2" em `layout_min_size` vs +1" no consumidor de frentes) sem justificativa documentada.
- 🟡 Variável `sobreposicao_esquerda` em `_hood_door_overlays` (`wood_hoods.py:453`) indica tradução parcial de
  identificadores no fork — inconsistência de nomenclatura.

---

## Módulo catalog_molding

> Camada legada (herdada do Home Builder 5). Legenda: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas: `_reversa_sdd/flowcharts/legacy-catalog_molding.md` e `legacy-catalog_molding-{activate_item,chain_sweep_points,kick_sweep_segments,resolve_stack}.md`. Mapeamento: `_reversa_sdd/catalog_molding/legacy-mapping.md`.

### Propósito

Dois subsistemas independentes agrupados neste módulo:

1. **`catalog/` — navegador de catálogo de produtos** 🟢: painel lateral "Catalog" (aba *Home Builder*) que lista produtos colocáveis a partir de uma lista Python estática (`CATALOG`), com busca fuzzy, filtro por categoria, visão lista/grade com thumbnails (`bpy.utils.previews`), cartão de detalhe e despacho do operador de colocação. Inclui um renderizador Workbench de thumbnails. **O pacote não é importado nem registrado pelo add-on** (`blendertomob/__init__.py:9-57` não o menciona; nenhuma referência a `hb_catalog` fora de `catalog/`) — é código latente/morto no build atual 🟢.
2. **`molding/` — pacotes de moldura por ambiente** 🟢: o usuário escolhe pacotes de *crown*, *base* (rodapé) e *light rail* em dropdowns da sala (`Scene.home_builder.molding_*`); cada mudança limpa e reconstrói todos os sweeps da cena, varrendo perfis 2D (bevel object) ao longo de caminhos poligonais que encadeiam armários contíguos, contornam cantos em L, envolvem ilhas, pulam eletrodomésticos e fazem retornos em laterais acabadas (`molding/__init__.py:1-15`, `ops.py:246-297`).

### Arquivos

| Arquivo | LOC | Papel |
|---|---|---|
| `blendertomob/catalog/__init__.py` | 31 | register/unregister (previews → props → ops → ui) |
| `blendertomob/catalog/catalog_data.py` | 382 | `CATALOG` (78 entradas: 7 com operador real, 71 stubs), helpers `_e/_ff/_todo`, categorias |
| `blendertomob/catalog/props_catalog.py` | 154 | `HBCatalogItem`, `HBCatalogState` em `Scene.hb_catalog`; sync via timer + `load_post` |
| `blendertomob/catalog/previews_catalog.py` | 119 | coleção de previews, `get_icon_id`, `reload` |
| `blendertomob/catalog/ops_catalog.py` | 128 | `hb_catalog.activate_item`, `hb_catalog.not_yet_implemented` |
| `blendertomob/catalog/render_thumbnails.py` | 198 | `render_entry`, `render_all` (sem chamador) |
| `blendertomob/catalog/ui_catalog.py` | 314 | `HB_UL_catalog`, `HB_CATALOG_PT_browser` |
| `blendertomob/catalog/thumbnails/` | 6 PNG | `no_thumbnail.png` + `standard_{base,tall,upper,upper_stacked,lap_drawer}.png` |
| `blendertomob/molding/__init__.py` | 25 | registra só `ops` |
| `blendertomob/molding/packages.py` | 347 | presets de pacotes, packs de perfis, contornos embutidos, métricas |
| `blendertomob/molding/adapters.py` | 230 | alvos, bridges e FACTS por biblioteca (face frame, frameless) |
| `blendertomob/molding/engine.py` | 736 | geometria agnóstica: corridas, cadeias, offsets, cantos, rodapé, ilhas |
| `blendertomob/molding/ops.py` | 348 | orquestração, pilhas, cotas Z, criação de curvas, operador refresh |

### Fluxo de controle

**Catálogo**
- `catalog.register()` (`catalog/__init__.py:18-24`) 🟢 → `previews_catalog.register()` cria `_pcoll = bpy.utils.previews.new()` e carrega `no_thumbnail.png` com chave `__no_thumbnail__` (`previews_catalog.py:94-109`) → `props_catalog.register()` registra classes, `Scene.hb_catalog`, `load_post` e agenda sync (`props_catalog.py:138-145`) → operadores → UI.
- `schedule_sync()` (`props_catalog.py:114-125`) 🟢: coalescido por flag global `_sync_pending`; registra timer one-shot `_deferred_sync` que chama `sync_catalog` em cada cena com `needs_sync` (comparação só por **contagem**, `props_catalog.py:93-98`).
- `sync_catalog(scene)` (`props_catalog.py:75-90`) 🟢: `items.clear()` e recria um `HBCatalogItem` por entrada (id, code, name, description, kind, category).
- `_catalog_load_post` (`props_catalog.py:128-132`) 🟢 `@persistent`: re-sync incondicional de todas as cenas após abrir arquivo.
- `HB_CATALOG_PT_browser.draw` (`ui_catalog.py:157-200`) 🟢: se `needs_sync` → `schedule_sync` (nunca escreve em draw); desenha busca, categoria, toggle List/Grid; em GRID usa `grid_flow` 2 colunas com `template_icon(scale=4)` + botão `hb_catalog.activate_item` (`ui_catalog.py:203-241`); em DEFAULT usa `template_list` (rows=8) e, se `active_index` válido, `_draw_detail` com botão de verbo e botão "Render Thumbnail" (`ui_catalog.py:244-282`).
- `HB_UL_catalog.filter_items` (`ui_catalog.py:95-115`) 🟢: flags via `_filter_visible`; reordena por `_priority` apenas se houver armário face frame (via `find_cabinet_root`) ou baia (`IS_FACE_FRAME_BAY_CAGE`) ativos.
- `hb_catalog.activate_item.execute` (`ops_catalog.py:53-86`) 🟢: `find_entry` → valida `action_operator` → `getattr(bpy.ops, mod).op` → `op(**action_args)` → `_apply_global_assembly_config(context.active_object)`. Erros → `report` + CANCELLED; `AttributeError` na resolução → fallback `draw_cabinet('INVOKE_DEFAULT', cabinet_name='Base Door')`.
- `hb_catalog.not_yet_implemented.execute` (`ops_catalog.py:99-108`) 🟢: mapeia nome → `Upper`/`Tall`/`Base Door` e invoca `draw_cabinet`.
- `render_entry(entry)` (`render_thumbnails.py:45-174`) 🟢: cena temporária `_hb_thumbnail_render`, operador em `EXEC_DEFAULT`, bbox mundial de meshes visíveis, câmera esférica, Workbench, grava `thumbnails/{id}.png`, `finally` restaura cena, remove a temporária e `previews_catalog.reload()`. `render_all()` (`:177-198`) itera e acumula `(rendered, skipped, errors)`. **Nenhum código chama estas funções** 🟢; o botão da UI aponta para `hb_catalog.render_thumbnail`, operador **inexistente** 🟢 (`ui_catalog.py:275-280`).

**Molduras**
- Gatilhos 🟢: `update=update_molding_package` em 13 props de `Home_Builder_Scene_Props` (`hb_props.py:164-168`, `:493-580`) → `ops.on_package_changed` (`ops.py:300-307`, captura exceções e só faz `print`); ou o operador `blendertomob.refresh_room_molding` (`ops.py:310-319`), exposto em `props_hb_face_frame.draw_molding_ui` (`product_libraries/face_frame/props_hb_face_frame.py:7668-7740`).
- `apply_scene_packages(scene)` (`ops.py:246-297`) 🟢: aborta se não há `scene.home_builder` ou se a cena é `IS_LAYOUT_VIEW`/`IS_DETAIL_VIEW`; `clear_scene_molding(scene)`; monta `opts`; para cada `(prop, tipo, align)` de `_TYPES` resolve a pilha (BASE via `_base_stack`) e chama `_apply_type`; por fim aplica `CAP` se `molding_crown_furniture_cap`.
- `_apply_type` (`ops.py:190-223`) 🟢: `collect_targets` → (+ `collect_bridges` para BASE) → `build_facts` → `_resolve_stack` → `connected_components` → descarta componentes sem alvo → `order_chain` → por entrada da pilha: `kick_sweep_segments` (BASE) ou `chain_sweep_points` (demais) → `_spawn_sweep`.
- `_spawn_sweep` (`ops.py:126-187`) 🟢: cria perfil (pack ou embutido), curva 2D `bevel_mode='OBJECT'`, `use_fill_caps`, tags, parent no 1º membro, `location.z=_sweep_z(...)`, perfil parentado ao sweep; converte pontos para o espaço local do 1º membro, dedup 1e-4, uma spline BEZIER com handles `VECTOR` por segmento; sem splines → remove objetos e retorna None; material = acabamento do 1º membro que resolver.
- `clear_scene_molding` (`ops.py:26-43`) 🟢: remove todo objeto com `IS_HB_MOLDING_SWEEP` (filtrável por tipo) e seu `bevel_object` se marcado `IS_HB_MOLDING_PROFILE`; remove curvas órfãs.

### Algoritmos e regras

**Catálogo**

- **CATALOG_MOLDING-R01** — ID de item = `category.replace('/','_') + '_' + nome sanitizado` (minúsculas; espaço→`_`; remove `-?(),`; `/`→`_`; colapsa `__`; `strip('_')`). Local: `catalog/catalog_data.py:45-64`. 🟢
- **CATALOG_MOLDING-R02** — Toda entrada tem `kind='product'`, `code=''`, `thumbnail=''`; `KIND_VERBS['product']='Place at cursor'`, ícone `MESH_CUBE`; tipo desconhecido → verbo `Activate`, ícone `QUESTION`. Local: `catalog_data.py:20-26,65-75`; `ui_catalog.py:68,248,266`. 🟢
- **CATALOG_MOLDING-R03** — Estilos de porta, acabamentos, condições de ponta e inserts (rollouts, lixeira, divisórias) **não** fazem parte do catálogo; são modificações sobre armários existentes. Local: `catalog_data.py:10-17`. 🟢
- **CATALOG_MOLDING-R04** — Entradas com operador real usam `hb_face_frame.draw_cabinet(cabinet_name, bay_qty=1)`; apenas 7: Base (`'Base Door'`), Tall, Upper, Upper Stacked, Lap Drawer, Leg Product, Floating Shelves. As 71 demais são stubs `hb_catalog.not_yet_implemented`. Local: `catalog_data.py:29-42,82-96,194-216`. 🟢
- **CATALOG_MOLDING-R05** — Stub coloca armário face frame genérico: nome contém `Upper`/`Wall` → `Upper`; `Tall`/`Pantry`/`Oven` → `Tall`; senão `Base Door` (sensível a maiúsculas; ex.: "Double Oven cabinet" → Tall). Local: `ops_catalog.py:99-106`. 🟢
- **CATALOG_MOLDING-R06** — Após colocar, aplica o estilo de armário **ativo** da cena (face frame se `root.face_frame_cabinet`, senão frameless se `root.hb_frameless`), garantindo estilos padrão; índice fora do intervalo → nada; exceções engolidas. Local: `ops_catalog.py:16-42`. 🟢 Aplicado sobre `context.active_object` logo após um operador que só abre um modal → provavelmente atinge o objeto errado. 🟡
- **CATALOG_MOLDING-R07** — Categoria selecionada casa itens da própria categoria ou descendentes (`startswith(cat + '/')`); `'all'` = "Everything". `list_categories` inclui todos os prefixos intermediários; rótulo = folha com `_`/`-`→espaço em Title Case, indentado 4 espaços por nível. Local: `ui_catalog.py:30-32`; `catalog_data.py:357-382`. 🟢
- **CATALOG_MOLDING-R08** — Busca: `query = search.lower().strip()`; casa se for substring de `code + ' ' + name + ' ' + description` (lower) **ou** subsequência ordenada (fuzzy). Local: `ui_catalog.py:28-51`. 🟢
- **CATALOG_MOLDING-R09** — Reordenação contextual: com baia selecionada, `kind=='insert'` sobe; com armário face frame selecionado, `kind=='option'` sobe. Como todas as entradas são `product`, a regra é hoje inócua. Local: `ui_catalog.py:105-124`. 🟢
- **CATALOG_MOLDING-R10** — Resolução de thumbnail: (1) `entry['thumbnail']` se o arquivo existir, (2) `{item_id}.png`, (3) placeholder; carregamento lazy na coleção; coleção não registrada → `icon_id=0`. Local: `previews_catalog.py:29-64`. 🟢
- **CATALOG_MOLDING-R11** — Item renderizável ⇔ `action_operator != 'hb_catalog.not_yet_implemented'`; botão "Render Thumbnail" aparece desabilitado (não oculto) para stubs. Local: `render_thumbnails.py:40-42`; `ui_catalog.py:270-282`. 🟢
- **CATALOG_MOLDING-R12** — Câmera de thumbnail: `az=-45°`, `el=25°`, `dist = 2 × max(dimensão do bbox)`; `offset = (d·cos el·sin az, −d·cos el·cos az, d·sin el)`; `lens=50`; rotação `direction.to_track_quat('-Z','Y')`. Render Workbench 256×256, RGBA, fundo transparente, MATCAP `basic_grey.exr`, cavity `BOTH`, sem outline. Bbox só de meshes visíveis do armário e descendentes. Local: `render_thumbnails.py:28-33,83-154`. 🟢
- **CATALOG_MOLDING-R13** — Descrição do detalhe quebrada em linhas de ≤ 40 caracteres por palavras. Local: `ui_catalog.py:258-263,285-298`. 🟢

**Molduras**

- **CATALOG_MOLDING-R14** — Elegibilidade por tipo: CROWN/CAP → `UPPER`, `TALL`; BASE → `BASE`, `TALL`, `LAP_DRAWER`; LIGHT_RAIL → `UPPER`. Face frame: `IS_FACE_FRAME_CABINET_CAGE` + `face_frame_cabinet.cabinet_type`; frameless: `IS_FRAMELESS_CABINET_CAGE` ou `IS_FRAMELESS_PRODUCT_CAGE` + ID prop `CABINET_TYPE`. **Closets não têm adaptador.** Local: `molding/adapters.py:16-52`. 🟢
- **CATALOG_MOLDING-R15** — Bridges (só BASE): objetos `IS_APPLIANCE` com `z` mundial ≤ 0,02 m (eletrodomésticos de piso) entram nas corridas mas com papel `APPLIANCE` e rodapé `skip` — mantêm a corrida única e forçam retornos. Aparelhos em altura são ignorados. Local: `adapters.py:55-66,169-174`; `ops.py:195-197`. 🟢
- **CATALOG_MOLDING-R16** — Agrupamento em corridas: dois membros "se tocam" se os AABBs de planta (expandidos por 0,02 m) se sobrepõem **e** a cota de alinhamento coincide (±0,02): topo para CROWN/CAP, base (origem) para BASE/LIGHT_RAIL. Componentes conexos por BFS; componentes sem nenhum alvo (só bridges) são descartados. Local: `engine.py:85-121`; `ops.py:19-23,202-204`. 🟢
- **CATALOG_MOLDING-R17** — Ordenação da cadeia: começa num membro com exatamente 1 vizinho (ou o 1º) e percorre vizinhos não usados; membros não alcançados (ramificações) são anexados ao fim. Componentes ≤ 2 mantêm a ordem recebida. Local: `engine.py:124-152`. 🟢
- **CATALOG_MOLDING-R18** — Offset "à direita do percurso" com meia-esquadria (interseção de linhas deslocadas); trechos colineares/paralelos (|cross| < 1e-6) geram degrau; pontos duplicados (< 1e-6) descartados; versão fechada mitra todos os vértices, inclusive a costura. Local: `engine.py:159-224`. 🟢
- **CATALOG_MOLDING-R19** — Normalização de sentido: se a direita do primeiro trecho reto tem produto escalar negativo com a normal frontal (−Y local) do membro, a cadeia é invertida, garantindo que o offset seja sempre para fora. Local: `engine.py:355-364,716-724`. 🟢
- **CATALOG_MOLDING-R20** — Armário de canto (L): origem no canto da parede; frente = `(ld,−depth) → (ld,−rd) → (width,−rd)` ou diagonal `(ld,−depth) → (width,−rd)`; `ld`/`rd` ausentes → 24". Entrada/saída escolhidas pela proximidade com o ponto anterior/centro do próximo. Local: `engine.py:231-253,281-315`. 🟢
- **CATALOG_MOLDING-R21** — Retorno em ponta acabada: nas extremidades da cadeia, se o lado do membro terminal for acabado, a moldura se estende por `outward × offset` e volta até o canto traseiro da caixa; ponta não acabada termina rente. Face frame: acabado ⇔ `*_finished_end_condition ∉ {'UNFINISHED','',None}`; frameless: acabado ⇔ sonda a 0,03 m para fora da lateral **não** cai dentro de bbox de parede `IS_WALL_BP` (tolerância 0,05). Local: `engine.py:371-387,588-608`; `adapters.py:112-125,195-198`. 🟢
- **CATALOG_MOLDING-R22** — Spans de rodapé por membro reto: aparelho/`skip` → `SKIP`; `setback ≤ 1e-5` → `FRONT` na face; recuado → stiles até o chão viram `FRONT` em L com retorno, trecho entre stiles vira `RECESS` em `y = −depth + setback`. Face frame com rodapé `NOTCH`/`LOOSE`/`FLOATING` fornece stiles/setback; outros tipos → setback 0; `RefrigeratorCabinet` → skip. Frameless usa ID prop `Toe Kick Setback` sem stiles. Local: `engine.py:395-422`; `adapters.py:73,182-194,221-222`. 🟢
- **CATALOG_MOLDING-R23** — Stretches: spans mantidos (`FRONT`, e `RECESS` se `molding_base_include_recessed`) consecutivos formam um trecho; na fronteira com um span descartado o trecho anexa o ponto adjacente → a moldura **retorna** para o rodapé acabado. Local: `engine.py:531-610`. 🟢
- **CATALOG_MOLDING-R24** — Ilha: cadeia em que **nenhum** membro tem `parent`, sem armários de canto, com no máximo 2 rotações Z distintas (arredondadas a 0,01 rad) e, se duas, opostas (π ± 0,05). Fileira única → perímetro frente+laterais+costas; dupla costas-com-costas → frente A + lateral + frente B + lateral. Se tudo mantido → laço fechado (spline cíclica); senão a ordem é rotacionada para começar num span descartado e pontas de ilha não recebem tratamento de acabado. Local: `engine.py:613-708,726-730,542-554`. 🟢
- **CATALOG_MOLDING-R25** — Pilhas: entradas `(profile_ref, fallback_key, dx, dy)`; `dy='STACK_OFFSET'` → `molding_crown_stack_offset`; `dx='STACK_FRONT'` → frente acumulada `max(dx_i + espessura_i)` das entradas anteriores; override por categoria (`Crown Molding`, `Spacer`, `Furniture Caps`, `Light Rail`; `Base Molding` via `_base_stack`) troca `ref` por `categoria/override`; `DEFAULT`/`''` = sem override. Local: `ops.py:46-72,226-243,256-276`. 🟢
- **CATALOG_MOLDING-R26** — Cota Z do sweep (no espaço do 1º membro): CROWN = datum + dy, datum = `altura − largura TOP_RAIL + max(default_top_overlay,0) + molding_crown_reveal` (face frame com TOP_RAIL) ou `altura` (frameless); CAP = `max(altura, topo da pilha crown ativa) + molding_cap_offset + dy`, topo da pilha = datum + dy + altura máx do perfil; BASE/LIGHT_RAIL = dy (origem do cage). Local: `ops.py:75-123`; `adapters.py:199-207`. 🟢
- **CATALOG_MOLDING-R27** — Base shoe é independente do pacote de base: se ligado, entra com `STACK_FRONT` (na face da base molding, ou na face do rodapé se não há pacote). Furniture cap é toggle independente do pacote de crown. Local: `ops.py:240-242,284-287,292-296`; `packages.py:107-109,120-121`. 🟢
- **CATALOG_MOLDING-R28** — Perfis: primeiro procura `<pack>/<Categoria>/<Nome>.blend` em cada pack registrado (`register_profile_path`) e faz append do objeto com nome igual ao stem; senão usa contorno embutido (`_PROFILE_OUTLINES`); nenhum → sem sweep. Perfis ficam ocultos (viewport/render), `2D`, `fill_mode='NONE'`, escala 1, marcados `IS_HB_MOLDING_PROFILE`. Local: `packages.py:219-252,327-347`. 🟢
- **CATALOG_MOLDING-R29** — Métricas de perfil `(top=max Y, depth=max X − min X)` medidas do `.blend` (append temporário, depois remoção) ou do contorno embutido; cache por `profile_ref`, invalidado ao (des)registrar packs. Local: `packages.py:262-311,35-49`. 🟢
- **CATALOG_MOLDING-R30** — Material do sweep = material de acabamento do estilo do **primeiro** membro da cadeia que resolver (face frame por `STYLE_NAME` em `cabinet_styles`; frameless por `CABINET_STYLE_INDEX` nos estilos da cena principal); aparelhos → None. Local: `ops.py:179-186`; `adapters.py:128-160`. 🟢
- **CATALOG_MOLDING-R31** — Reconstrução total e idempotente: qualquer mudança em qualquer prop `molding_*` limpa **todas** as molduras de pacote da cena e recria tudo; mudanças de armários exigem o botão "Refresh Molding" (não há handler de depsgraph). Local: `ops.py:246-254`; `hb_props.py:164-168`. 🟢 / 🟡 (ausência de auto-refresh inferida por não haver outro chamador)
- **CATALOG_MOLDING-R32** — Enum items de pacotes e de perfis são cacheados em nível de módulo (Blender mantém só referências fracas às strings de enums dinâmicos). Local: `packages.py:55-58,164-172`. 🟢

### Constantes/enums

| Constante | Valor | Local |
|---|---|---|
| `KIND_VERBS` / `KIND_ICONS` | `{'product': 'Place at cursor'}` / `{'product': 'MESH_CUBE'}` | `catalog_data.py:20-26` |
| Categorias | `standard`(6), `corner`(9), `appliance`(14), `vanity`(3), `parts`(9), `specialty`(30), `angled`(3), `misc`(4) = 78 | `catalog_data.py:78-346` |
| `_PLACEHOLDER_KEY` | `'__no_thumbnail__'` | `previews_catalog.py:18` |
| `HBCatalogState.view_mode` | `DEFAULT` (List) / `GRID` | `props_catalog.py:59-66` |
| `THUMB_RESOLUTION`, `_AZIMUTH_DEG`, `_ELEVATION_DEG` | 256, −45.0, 25.0 | `render_thumbnails.py:28-33` |
| Nome da cena/câmera temporária | `_hb_thumbnail_render`, `_hb_thumb_cam` | `render_thumbnails.py:60,126-128` |
| Painel | `bl_category="Home Builder"`, `bl_order=1`, `VIEW_3D/UI` | `ui_catalog.py:148-155` |
| `MOLDING_TAG` / `MOLDING_TYPE` / `MOLDING_MEMBERS` | `IS_HB_MOLDING_SWEEP` / `HB_MOLDING_TYPE` / `HB_MOLDING_MEMBERS` (nomes separados por vírgula) | `ops.py:14-16` |
| Tag de perfil | `IS_HB_MOLDING_PROFILE` | `packages.py:229` |
| Tipos de moldura | `CROWN`, `BASE`, `LIGHT_RAIL`, `CAP` | `ops.py:19-23,295` |
| Pacotes CROWN | `SIMPLE` (51 Crown), `STACKED` (Square Edge Spacer + 51 Crown com STACK_FRONT/STACK_OFFSET), `SPACER` | `packages.py:87-102` |
| Pacotes BASE / LIGHT_RAIL | `SIMPLE` (Standard Base) / `SIMPLE` (Cove Cut LR) | `packages.py:111-127` |
| `FURNITURE_CAP_STACK` | `Furniture Caps/Furniture 3 Inch` | `packages.py:107-109` |
| `BASE_SHOE_REF` / `BASE_SHOE_FALLBACK` | `Base Molding/Base Shoe` / `base_shoe` | `packages.py:120-121` |
| Sentinelas | `STACK_FRONT` (dx), `STACK_OFFSET` (dy) | `packages.py:97-98`; `ops.py:61,67` |
| Contornos embutidos (pol.) | `crown_simple` 0,875×3; `flat_stock` 0,75×3,5; `furniture_cap` 1,125×1 (nariz 0,375 à frente); `base_simple` 0,625×3; `base_shoe` 0,4375×0,75; `light_rail_simple` 0,75×−1,5 | `packages.py:183-216` |
| Tipos de rodapé recuado (FF) | `NOTCH`, `LOOSE`, `FLOATING` | `adapters.py:73` |
| Tolerâncias | toque 0,02 m; bridge z ≤ 0,02 m; sonda de parede 0,03 m / tolerância 0,05 m; ilha π ± 0,05 rad; dedup local 1e-4; geometria 1e-6; setback 1e-5 | `engine.py:85`, `adapters.py:63,104,124`, `engine.py:630`, `ops.py:156` |
| Defaults da sala | reveal 0,625"; stack offset 3,5"; cap offset 0 (soft ±6"); include_recessed False; furniture_cap False; base_shoe False | `hb_props.py:514-570` |

### Riscos Blender 5.2

1. 🟢 **Catálogo não registrado**: todo `catalog/` está fora do `register()` do add-on — não há risco de runtime hoje, mas qualquer reativação herda os problemas abaixo.
2. 🟢 **Operador inexistente na UI**: `_draw_detail` chama `layout.operator('hb_catalog.render_thumbnail')` e atribui `rop.item_id` (`ui_catalog.py:275-280`); nenhum operador com esse `bl_idname` existe. 🟡 Em 5.x isso tende a gerar erro no `draw()` (retorno sem propriedades) — o painel quebraria ao selecionar um item.
3. 🟢 **Thumbnails gravados na pasta do add-on** (`os.path.dirname(__file__)/thumbnails`, `render_thumbnails.py:36-37,157-160`) em vez de `bpy.utils.extension_path_user(__package__, path=..., create=True)`; extensões podem estar em diretório somente leitura e são sobrescritas em atualizações.
4. 🟡 **`studio_light = 'basic_grey.exr'`** (`render_thumbnails.py:151`): enum dinâmico (`docs/rag/blender-api/corpus/bpy.types.View3DShading.md#bpy.types.View3DShading.studio_light`); se o nome não existir na instalação lança `TypeError`, propagado para `render_all`.
5. 🟡 **`render_entry` depende de `context.window`** (`render_thumbnails.py:55-63`): em `--background` `window` é `None` → falha; além disso `draw_cabinet` em `EXEC_DEFAULT` só dispara modais `INVOKE_DEFAULT` (`product_libraries/face_frame/operators/ops_cabinet.py:37-68`), então nenhum armário é criado de forma síncrona e o objeto ativo não é o armário → thumbnails inválidos ou `None`.
6. 🟡 **Enum dinâmico sem cache no catálogo**: `_category_items_cb` (`props_catalog.py:24-28`) cria uma nova lista a cada chamada — mesma armadilha de referências fracas que `molding/packages.py:55-58` explicitamente evita (ver `docs/rag/project/04_armadilhas.md`).
7. 🟢 **Timer não cancelado**: `schedule_sync` registra `_deferred_sync` via `bpy.app.timers.register`, mas `unregister()` não chama `bpy.app.timers.unregister` (`props_catalog.py:148-154`); se pendente, roda após o unregister e acessa `scene.hb_catalog` inexistente.
8. 🟢 **previews**: criado em `register` (`previews_catalog.py:104`) e liberado em `unregister` (`:112-118`) ✅; `reload()` recria a coleção e percorre `bpy.context.window_manager.windows` (`:89-91`) — sem janela (background) não há erro, mas depende de `bpy.context` global.
9. 🟢 **`molding/ops.register()` engole exceções** e desregistra por `getattr(bpy.types, cls.__name__)` (`ops.py:327-348`); falhas de registro ficam silenciosas.
10. 🟢 **Reconstrução pesada dentro de `update=` de props** (`hb_props.py:164-168` → `ops.py:300-307`): cria/remove objetos, faz `bpy.data.libraries.load` e remove datablocks durante o callback; erros só vão para `print`. 🟡 Interação com undo e com drivers não verificada.
11. 🟢 **Dados órfãos**: em `_spawn_sweep` sem splines, remove objetos mas não as curvas (`ops.py:174-177`); append de perfis de pack pode trazer materiais/datablocks auxiliares que não são limpos (`packages.py:244-252,289-300`) 🟡.
12. 🟢 **Uso de ID props** (`obj.get('CABINET_TYPE')`, `'Left Depth'`, `'Toe Kick Setback'`, `STYLE_NAME`, `CABINET_STYLE_INDEX`, tags `IS_*`): são propriedades customizadas de ID criadas via `obj[name] = value` (`hb_props.py:335-347`), portanto compatíveis com 5.x; propriedades `bpy.props` (`face_frame_cabinet.*`, `home_builder.*`) são lidas por atributo ✅.
13. 🟡 **Nomes de enum de 5.2** usados: `curve.bevel_mode='OBJECT'` confirmado em `docs/rag/blender-api/corpus/bpy.types.Curve.md#bpy.types.Curve.bevel_mode`; demais (`fill_mode='NONE'` com `dimensions='2D'`, `cavity_type='BOTH'`) não verificados aqui — rodar `python3 docs/rag/tools/check_api.py`.

### Dependências de outros módulos

- `blendertomob/product_libraries/face_frame/types_face_frame.find_cabinet_root` (`ops_catalog.py:20-21`, `ui_catalog.py:134`) e `props_hb_face_frame.ensure_default_styles/get_style_props` (`ops_catalog.py:25-30`, `adapters.py:137-143`).
- `blendertomob/product_libraries/frameless/props_hb_frameless` (`ops_catalog.py:35-40`).
- `hb_face_frame.draw_cabinet` → `place_cabinet` / `place_corner_cabinet` / `place_appliance` (modais) (`product_libraries/face_frame/operators/ops_cabinet.py:18-68`).
- `blendertomob/hb_props.py` (`Home_Builder_Scene_Props.molding_*`, callbacks) e `props_hb_face_frame.draw_molding_ui` (UI de molduras).
- `blendertomob/hb_types.GeoNodeObject.get_input` (`engine.py:39-42`, `adapters.py:83`), `blendertomob/hb_project.get_main_scene` (`adapters.py:147-148`), `blendertomob/units.inch`.
- Marcadores de outros módulos: `IS_FACE_FRAME_CABINET_CAGE`, `IS_FRAMELESS_CABINET_CAGE`, `IS_FRAMELESS_PRODUCT_CAGE`, `IS_CORNER_CABINET`, `IS_APPLIANCE`, `IS_WALL_BP`, `IS_FACE_FRAME_BAY_CAGE`, `hb_part_role=='TOP_RAIL'`, `CLASS_NAME=='RefrigeratorCabinet'`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW`.
- Packs externos de perfis via `packages.register_profile_path` (nenhum chamador no repositório 🟢 → sempre contornos embutidos no build atual 🟡).

### Lacunas

- 🔴 Motivo de o pacote `catalog/` não ser registrado (abandono, substituição pelo `hb_assets`/asset browser, ou esquecimento na migração) — não há comentário nem commit analisado.
- 🔴 Operador `hb_catalog.render_thumbnail` nunca implementado; não se sabe se chamaria `render_entry` ou `render_all`.
- 🔴 Não existe adaptador de molduras para `closets` (apenas face frame e frameless) — não se sabe se é intencional.
- 🔴 Nenhum pack de perfis (`register_profile_path`) no repositório; formato real dos `.blend` (curva 2D com nome = stem) é apenas convenção documentada em docstring.
- 🟡 Comportamento de `getattr(bpy.ops.<mod>, <inexistente>)` (fallback em `ops_catalog.py:69-76`) não verificado em 5.2.
- 🟡 Não verificado se o modal `place_cabinet` deixa algum objeto ativo no instante em que `_apply_global_assembly_config` roda.
- 🟡 Cota Z de LIGHT_RAIL = `dy` pressupõe origem do cage `UPPER` no fundo; não verificado para frameless.

---
