# hb_core — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-hb_core`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#hb_core`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-hb_core-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Visão Geral

O `hb_core` é o **núcleo do modelo de objetos paramétricos** da camada legada. Cada peça, gaiola (cage), parede ou
anotação é um objeto Blender com um modificador Geometry Nodes cujo node group vem de um `.blend` embarcado; as medidas
se ligam por **drivers** montados por uma DSL Python (`Variable` + `driver_*`) e as divisões de vão ficam em
**calculadoras**. O módulo também registra os PropertyGroups `home_builder` (Object/Scene/WindowManager), os dados de
projeto da "cena principal", o catálogo de obstáculos, a fachada de unidades e 6 operadores gerais. 🟢
Todo o resto da camada legada (49 arquivos, 37 em `product_libraries/`) depende dele. 🟢

## Responsabilidades

- Criar objetos paramétricos a partir de node groups GN embarcados (malha ou curva POLY de 2 pontos). 🟢
- Ler e escrever inputs GN pelo **nome** do socket, independente da versão do Blender (5.1 × 5.2). 🟢
- Montar drivers entre objetos (entrada GN, custom prop, location, rotation, visibilidade) com funções `IF/OR/AND`. 🟢
- Distribuir medidas por calculadoras (parcelas fixas + parcelas "iguais"). 🟢
- Forçar a reavaliação de drivers/calculadoras até estabilizar. 🟢
- Modelar paredes encadeadas e descobrir vizinhos. 🟢
- Criar cotas e setas 2D com unidade e casas decimais corretas. 🟢
- Guardar configuração global de cena (pé-direito, paredes, portas/janelas, molduras, anotações). 🟢
- Guardar dados de projeto (cliente, projetista) numa única cena principal. 🟢
- Manter o catálogo de 36 obstáculos (tomadas, interruptores, luzes, colunas…) e suas dimensões. 🟢
- Expor unidades (metro interno ↔ mm/cm/m/in/ft) via fachada sobre `data/units.py`. 🟢
- Oferecer operadores gerais: configurações recomendadas, render, câmera com backplate, estilo de anotação, escala de
  imagem de referência por dois pontos. 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `HB_CORE-Rnn`).

**Modelo de objetos**
- RN-01 (R01): node group só é carregado do `.blend` se não existir em `bpy.data.node_groups`; grupo local homônimo tem precedência. 🟢
- RN-02 (R02): todo objeto GeoNode guarda o nome do modificador principal em `obj.home_builder.mod_name` e é ligado a `scene.collection`. 🟢
- RN-03 (R03): identificador de socket é resolvido por nome, com cache; em `KeyError`/`AttributeError` o cache é invalidado e há **uma** nova tentativa. 🟢
- RN-04 (R04): após escrever um input, `obj.update_tag()` é chamado. 🟢
- RN-05 (R05): validação em ordem `mod_name` → modificador → node group → input; qualquer falha gera `ValueError` com mensagem explícita. 🟢
- RN-06 (R06): `driver_hide` escreve a mesma expressão em `hide_viewport` e `hide_render`; em `CabinetPartModifier` a expressão controla `show_viewport/show_render` (semântica invertida: verdadeiro = visível). 🟢
- RN-07 (R09): gaiola é `WIRE`, preta, sem sombra, invisível a câmera/sombra, `hide_render=True`, marcador `IS_GEONODE_CAGE`. 🟢
- RN-08 (R10): padrões de fábrica — Rectangle 1×1 m, linha 1 mm; DrawerBox 0,5"/0,25"/Z 0,5"; DoorSwing porta 1,5"; Arrow 0,25"×0,5". 🟢
- RN-09 (R14): `CabinetPartModifier` carrega `CabinetPartModifiers/<token>.blend`; arquivo ausente → modificador sem grupo (sem erro). 🟢

**Drivers e calculadoras**
- RN-10 (R15): calculadora — cada prompt `equal ∧ include` recebe `(total − Σ fixos incluídos) / nº iguais incluídos`; `equal ∧ ¬include` = 0; sem prompts iguais, nada é recalculado; **sem proteção contra valor negativo**. 🟢
- RN-11 (R16): o total da calculadora é um driver em `distance_obj.home_builder.calculator_distance`. 🟢
- RN-12 (R17): prompts de objeto (`add_property`) têm os tipos CHECKBOX, DISTANCE, ANGLE, PERCENTAGE (0–100), QUANTITY (≥0), COMBOBOX, com `description='HOME_BUILDER_PROP'`, guardados como ID custom property. 🟢
- RN-13 (R21): `run_calc_fix` faz N passadas (padrão 2) tocando location/`show_viewport`, rodando todas as calculadoras e avançando/voltando um frame; `until_stable` repete até 5 vezes até a variação de dimensões ser ≤ 0,0001 m (retorna nº de passadas ou −1). 🟢
- RN-14 (R28): `IF`, `OR`, `AND` ficam disponíveis nas expressões de driver; só são injetados se o nome não existir no namespace. 🟢

**Paredes**
- RN-15 (R07): paredes se encadeiam por `COPY_LOCATION` para o empty `obj_x` da anterior; `obj_x.location.x = Length`, Y/Z e rotação travados. 🟢
- RN-16 (R08): vizinho à esquerda = pai do alvo da restrição; à direita = parede cuja restrição aponta para o meu `obj_x`; fallback geométrico opcional pelos extremos em XY do mundo, tolerância 0,01 m. 🟢
- RN-17 (R19): mudar `wall_material` aplica o material aos inputs `Top Surface`, `Bottom Surface`, `Inside Face`, `Outside Face`, `Left Edge`, `Right Edge` de toda parede `IS_WALL_BP`. 🟢

**Cotas e anotações**
- RN-18 (R11): `Unit Type` da cota — MM=2, CM=3, M=4, outra métrica=3, imperial=0; 1 (pés) nunca é produzido. 🟢
- RN-19 (R12): casas decimais pelo encaixe no incremento da unidade (in 1 ou 1/16; ft 1/12 ou 1/192; mm 10 ou 1; cm 1 ou 0,1; m 0,01 ou 0,001); resultado inteiro (±0,001) → 0 casas. 🟢
- RN-20 (R13): fixup idempotente do node group `GeoNodeDimension` religa o offset X do texto à tangente da curva quando falta o nó `Text X Tangent Rotate`. 🟢
- RN-21 (R35): tamanhos de anotação "em papel" só recalculam em cenas `IS_LAYOUT_VIEW` com `annotation_auto_scale`. 🟢
- RN-22 (R36): espessura de linha de anotação vale só para `IS_DETAIL_LINE/POLYLINE/CIRCLE`; cotas têm espessura própria. 🟢
- RN-23 (R33): "Apply Settings to All" atualiza linhas, textos e — para cotas — só objetos `MESH` com `IS_2D_ANNOTATION` via `Socket_3/4/5` fixos (na prática não atinge cotas, que são `CURVE`). 🟢 / 🟡 efeito nulo

**Cena, projeto e ambiente**
- RN-24 (R18): mudar `ceiling_height` recalcula, em frameless e face frame, `tall = pé-direito − folga superior` e `upper = pé-direito − folga superior − altura do aéreo`. 🟢
- RN-25 (R20): padrões de cena em polegadas — pé-direito 96, meia parede 42, parede falsa 34, parede 4,5 (externa 6, interna 4,5), porta 36×84 (dupla 72), janela 34×34 a 36 do piso. 🟢
- RN-26 (R22/R23): cena principal = primeira com `IS_MAIN_SCENE`; senão, primeiro cômodo por `sort_order`; senão, `scenes[0]`; só uma cena pode estar marcada. 🟢
- RN-27 (R24): migrar projeto copia custom props da cena antiga para a nova, exceto `IS_MAIN_SCENE`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW`, `IS_CROWN_DETAIL`, `home_builder`, `cycles`, `VIEW_*`, sem sobrescrever chaves existentes. 🟢
- RN-28 (R25): "cena de cômodo" tem **duas** definições divergentes (`hb_project` × `hb_utils`, esta exclui também `IS_CROWN_DETAIL`). 🟢
- RN-29 (R37): a hierarquia de produto é descoberta subindo pelos pais até achar o marcador (`IS_FRAMELESS_CABINET_CAGE`, …, `IS_WALL_BP`). 🟢
- RN-30 (R38): o estado da vista 3D é salvo em custom props `VIEW_*` da cena e restaurado com padrões seguros. 🟢
- RN-31 (R39): exclusão recursiva remove filhos antes do pai (pós-ordem). 🟢

**Obstáculos e unidades**
- RN-32 (R26): enum de obstáculos com cabeçalhos (ids 0/100/200/300) e itens `base+i+1`; escolher tipo copia 4 dimensões; cabeçalho não é posicionável; "From Floor" só para superfície `WALL`. 🟢
- RN-33 (R27): limites — largura/altura 0,5"–120", profundidade 0,25"–24", altura do piso 0–120". 🟢
- RN-34 (R29/R30): base interna em metros; unidade padrão `MM`; código desconhecido → fator 0,001; unidade da cena = `btm_settings.btm_unit` → métrico de `unit_settings` → `MM`; `format_number` até 3 casas; `meter_to_inch = round(m×39,3701, 6)`. 🟢

**Operadores gerais**
- RN-35 (R31): escala de imagem de referência = distância conhecida / distância clicada no plano XY local do empty; só para empty `IMAGE`. 🟢
- RN-36 (R32): backplate da câmera dimensionado pelo FOV vertical: `altura = 2·d·tan(vfov/2)·1,1`, `largura = altura·aspecto`; material emissivo, sem sombra. 🟢
- RN-37 (R34): "configurações recomendadas" tornam `color_type='OBJECT'` obrigatório e desligam linhas de relação/cursor 3D, ligam wireframe (limiar 0, opacidade 0,8), studio light `paint.sl`, snap `VERTEX`. 🟢

**Comportamentos desconhecidos**
- 🔴 Interfaces (nomes/tipos de inputs) dos node groups em `geometry_nodes/*.blend` não verificadas.
- 🔴 Não há migração de caminhos de driver `modifiers["M"]["ID"]` (< 5.2) para `…properties.inputs.ID.value` (5.2) ao abrir arquivos antigos.
- 🔴 Operadores `pc_prompts.*` usados pela UI da calculadora não existem.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Criar objeto GeoNode (malha) a partir de um node group nomeado, reutilizando grupo existente | Must | Objeto tem modificador `NODES` com o grupo; `mod_name` gravado; ligado a `scene.collection`; segunda criação não duplica o node group |
| RF-02 | Criar objeto GeoNode curva (POLY, 2 pontos) com cor de anotação das preferências | Must | `obj.type == 'CURVE'`, 2 pontos, cor = `annotation_color` |
| RF-03 | Ler/escrever input GN por nome em 5.1 e 5.2 | Must | Valor lido = valor escrito; input inexistente → `ValueError` com nome do input |
| RF-04 | Invalidar cache de identificador e tentar de novo após falha | Must | Após renomear/recriar o node group, `set_input` ainda escreve no socket certo |
| RF-05 | Criar drivers de input, prop, location, rotation e hide com variáveis `SINGLE_PROP` | Must | Mudar a variável-fonte atualiza o alvo após reavaliação do depsgraph |
| RF-06 | Disponibilizar `IF/OR/AND` em `driver_namespace` no registro e após `load_post` | Must | Expressão `IF(a>b, a, b)` avalia sem erro após abrir arquivo |
| RF-07 | Calculadora distribui o total entre prompts iguais incluídos | Must | Total 1000, fixo 200, 2 iguais → cada igual = 400 |
| RF-08 | Reavaliar drivers/calculadoras até estabilizar (máx. 5 passadas) | Must | Retorna nº de passadas quando Δ ≤ 0,0001 m; −1 se não convergir |
| RF-09 | Criar parede com empty `obj_x` dirigido por `Length` e encadear à anterior | Must | Mudar `Length` da parede A move a origem da parede B conectada |
| RF-10 | Descobrir vizinhos esquerdo/direito (topológico + geométrico opcional via `include_loop_seam`) | Should | Retorna a parede conectada; com `include_loop_seam`, acha parede cujos extremos coincidem (≤ 0,01 m) |
| RF-11 | Criar cota com marcadores, tamanhos da cena e `Unit Type` | Must | Inputs `Tick Length`, `Line Thickness`, `Text Size`, `Unit Type` iguais aos da cena |
| RF-12 | Ajustar casas decimais da cota pela unidade | Should | 1000 mm → 0 casas; 12,5 mm → 1 casa |
| RF-13 | Aplicar fixup idempotente do node group de cota | Should | Rodar 2× não altera o grupo na segunda vez |
| RF-14 | Propagar pé-direito para alturas de alto/aéreo em frameless e face frame | Must | 96" pé-direito, folga 12", aéreo 30" → tall 84", upper 54" |
| RF-15 | Aplicar material de parede a todas as paredes | Should | Todas as `IS_WALL_BP` recebem o material nos 6 inputs |
| RF-16 | Manter uma única cena principal com dados de projeto | Must | Após `set_main_scene(B)`, só B tem `IS_MAIN_SCENE` |
| RF-17 | Migrar dados de projeto entre cenas sem sobrescrever | Should | Chaves já existentes na nova cena ficam inalteradas |
| RF-18 | Catálogo de obstáculos com seleção e cópia de dimensões | Should | Escolher `OUTLET_STANDARD` preenche as 4 dimensões padrão |
| RF-19 | Localizar a base de cabinet/product/bay/opening/interior/appliance/wall subindo na hierarquia | Must | De qualquer peça filha, retorna o objeto com o marcador correspondente |
| RF-20 | Excluir objeto e descendentes | Must | Nenhum filho órfão sobra em `bpy.data.objects` |
| RF-21 | Salvar e restaurar estado da vista 3D em custom props da cena | Could | Após restaurar, posição/rotação/distância iguais às salvas |
| RF-22 | Converter unidades (metro ↔ mm/cm/m/in/ft) e formatar números | Must | `to_meters(18, 'MM') == 0.018`; `format_number(1.50) == "1.5"` |
| RF-23 | Operador: configurações recomendadas da viewport | Should | Shading `color_type == 'OBJECT'` após executar |
| RF-24 | Operador: criar câmera a partir da vista, com track-to e backplate opcionais | Could | Backplate cobre o frustum com margem de 10% |
| RF-25 | Operador modal: escalar imagem de referência por dois pontos | Could | Após 2 cliques, `empty_display_size` multiplicado pelo fator; ESC/RMB cancela sem alterar |
| RF-26 | Operador: aplicar estilo de anotação a todas as anotações | Could | Linhas e textos atualizados (cotas: ver lacuna RN-23) |
| RF-27 | Operador: diálogo de configurações de render | Won't | `execute` vazio; props alteradas direto no `draw` |
| RF-28 | Botões da calculadora (`pc_prompts.*`) | Won't | Operadores inexistentes — não implementar como estão |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Compatibilidade | Inputs GN via RNA no ≥ 5.2 e por chave de ID no < 5.2, decidido por `bpy.app.version` | `hb_utils.py:13-28` | 🟢 |
| Compatibilidade | Caminho de driver de input GN muda com a versão | `hb_utils.py:55-60` | 🟢 |
| Performance | Cache de identificador de socket por node group evita varrer a interface a cada escrita | `hb_types.py:21-45` | 🟢 |
| Performance | Reavaliação limitada a 5 passadas com limiar 0,0001 m | `hb_utils.py:249-297` | 🟢 |
| Robustez | `register()` tolera versão antiga registrada (desregistra e registra de novo) | `hb_props.py:955-966` | 🟢 |
| Robustez | `get_main_scene` tolera contexto de desenho (escrita de ID proibida) | `hb_project.py:170-174` | 🟢 |
| Privacidade | Dados de cliente (nome, endereço, telefone, e-mail) gravados no `.blend` sem proteção | `hb_project.py:30-136` | 🟢 |
| Usabilidade | Modal de escala repassa eventos de navegação à viewport | `ops.py:617-652` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Objetos paramétricos GeoNode

  Cenário: Criar objeto reutilizando node group existente
    Dado que o node group "GeoNodeCage" já existe em bpy.data.node_groups
    Quando GeoNodeCage().create("Gaiola") é chamado duas vezes
    Então existe um único node group "GeoNodeCage"
    E os dois objetos têm obj.home_builder.mod_name preenchido

  Cenário: Escrever input inexistente
    Dado um objeto GeoNodeCage válido
    Quando set_input("Largura Inventada", 1.0) é chamado
    Então um ValueError é levantado mencionando "Largura Inventada"
    E nenhum input do modificador é alterado

  Cenário: Cache desatualizado após recriar o node group
    Dado um identificador de socket em cache para o node group "G"
    E o node group foi substituído por outro com a mesma interface
    Quando set_input("Dim X", 0.6) é chamado
    Então o cache é invalidado, a leitura é refeita uma vez
    E get_input("Dim X") retorna 0.6

Funcionalidade: Calculadora

  Cenário: Distribuição de iguais
    Dado uma calculadora com total 1,0 m
    E um prompt fixo incluído de 0,2 m e dois prompts iguais incluídos
    Quando calculate() é executado
    Então cada prompt igual recebe 0,4 m

  Cenário: Prompt igual excluído
    Dado um prompt com equal=True e include=False
    Quando calculate() é executado
    Então o valor desse prompt é 0

  Cenário: Fixos maiores que o total
    Dado total 0,5 m e um fixo incluído de 0,8 m com um prompt igual
    Quando calculate() é executado
    Então o prompt igual recebe -0,3 m (comportamento legado, sem proteção)

Funcionalidade: Reavaliação até estabilizar

  Cenário: Convergência
    Dado uma cena com drivers encadeados que estabilizam em 2 passadas
    Quando run_calc_fix_until_stable é chamado
    Então retorna um número entre 1 e 5

  Cenário: Não convergência
    Dado drivers que oscilam acima de 0,0001 m
    Quando run_calc_fix_until_stable é chamado
    Então retorna -1 depois de 5 passadas

Funcionalidade: Paredes encadeadas

  Cenário: Mudar o comprimento propaga para a próxima parede
    Dado a parede B conectada ao obj_x da parede A
    Quando o input Length de A muda de 3 m para 4 m
    Então a origem de B passa a ficar a 4 m da origem de A no eixo local de A

  Cenário: Parede sem vizinho
    Dado uma parede isolada
    Quando get_connected_wall("left") é chamado com include_loop_seam=False
    Então retorna None

Funcionalidade: Cena principal

  Cenário: Marcação única
    Dado as cenas A (principal) e B
    Quando set_main_scene(B) é chamado
    Então apenas B tem IS_MAIN_SCENE

  Cenário: Contexto de desenho
    Dado que nenhuma cena está marcada e o código roda dentro de um draw()
    Quando get_main_scene() é chamado
    Então retorna a cena escolhida pelas regras de fallback sem levantar exceção

Funcionalidade: Pé-direito

  Cenário: Recalcular alturas
    Dado pé-direito 96", folga superior 12" e altura de aéreo 30"
    Quando ceiling_height é alterado
    Então tall_cabinet_height = 84" e upper_cabinet_height = 54" em hb_frameless e hb_face_frame

Funcionalidade: Escala de imagem por dois pontos

  Cenário: Caminho feliz
    Dado um empty IMAGE selecionado e known_distance = 2 m
    Quando o usuário clica dois pontos a 1 m de distância no plano da imagem
    Então empty_display_size é multiplicado por 2 e o draw handler é removido

  Cenário: Cancelamento
    Dado o modal ativo após o primeiro clique
    Quando o usuário pressiona ESC
    Então a escala não muda e o draw handler é removido
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| API `GeoNodeObject` (criar, inputs, drivers) — RF-01..RF-06 | Must | 49 arquivos dependem; caminho crítico de toda a camada legada |
| Calculadora e reavaliação — RF-07, RF-08 | Must | Usadas por frameless/face_frame em toda edição |
| Paredes e hierarquia — RF-09, RF-19, RF-20 | Must | Base de posicionamento e exclusão |
| Cotas — RF-11 | Must | Todas as vistas de layout dependem |
| Cena principal e pé-direito — RF-14, RF-16 | Must | Estado global de projeto |
| Unidades — RF-22 | Must | Todas as conversões |
| Vizinho geométrico, decimais, fixup, material de parede, migração, obstáculos — RF-10, RF-12, RF-13, RF-15, RF-17, RF-18 | Should | Importantes, com alternativa manual |
| Configurações recomendadas — RF-23 | Should | Marcado como obrigatório na UI, mas fora do fluxo de dados |
| Estado de vista, câmera, escala de imagem, estilo de anotação — RF-21, RF-24..RF-26 | Could | Acionados raramente |
| Diálogo de render, botões `pc_prompts` — RF-27, RF-28 | Won't | Stub / operadores inexistentes |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `hb_types.py` | `Variable`, `GeoNodeObject` (`create`, `create_curve`, `set_input`, `get_input`, `var_*`, `driver_*`) | 🟢 |
| `hb_types.py` | `GeoNodeWall`, `GeoNodeCage`, `GeoNodeRectangle`, `GeoNodeCutpart`, `GeoNode5PieceDoor`, `GeoNodeHardware`, `GeoNodeDrawerBox`, `GeoNodeDoorSwing`, `GeoNodeArrow` | 🟢 |
| `hb_types.py` | `GeoNodeDimension`, `ensure_dimension_text_offset_basis`, `CabinetPartModifier` | 🟢 |
| `hb_props.py` | `Calculator_Prompt`, `Calculator`, `Home_Builder_Object_Props`, `Home_Builder_Scene_Props`, `Home_Builder_Window_Manager_Props`, callbacks `update_*` | 🟢 |
| `hb_props.py` | `HB_Wall_Editor_Props` (pertence funcionalmente a [`wall_editor/`](../wall_editor/)) | 🟢 |
| `hb_utils.py` | ponte GN, `get_*_bp`, `delete_obj_and_children`, `run_calc_fix*`, `add_driver_variables`, `save/restore_view_state` | 🟢 |
| `hb_driver_functions.py` | `IF`, `OR`, `AND` | 🟢 |
| `hb_project.py` | `Home_Builder_Project_Props`, `get_main_scene`, `ensure_main_scene`, `set_main_scene`, `migrate_project_data`, `get_room_scenes` | 🟢 |
| `hb_props_obstacles.py` | catálogos `*_OBSTACLES`, `get_obstacle_items`, `Obstacles_Scene_Props` | 🟢 |
| `units.py` → `data/units.py` | fachada de unidades | 🟢 |
| `ops.py` | 6 operadores gerais | 🟢 |
| `__init__.py:58-73,212-214,249-256` | registro, `load_file_post`, `driver_namespace` | 🟢 |
