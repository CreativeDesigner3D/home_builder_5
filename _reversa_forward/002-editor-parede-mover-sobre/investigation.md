# Investigation: 002-editor-parede-mover-sobre

## 1. Fontes consultadas

- **Levantamento do código (2026-10-04):**
  - modelos de objeto (Home Builder 5 `IS_*`/`MENU_ID` × camada nova `btm_plane`);
  - paredes: `operators/walls.py` (`draw_walls`, `create_wall`, `wall_prompts`, esquadrias, excluir, ocultar), `hb_types.GeoNodeWall` (cadeia `COPY_LOCATION`, `get_connected_wall`, vizinho geométrico com tolerância de 0,01 m);
  - elevações em `hb_layouts.py` (cenas de prancha, sem edição);
  - painel `BTM_PT_ContextProperties` (só camada nova);
  - prompts por biblioteca;
  - menus por `MENU_ID`;
  - posicionamento e vão em `hb_placement.py`;
  - encostar ao lado (`hb_placement.py:520-582`);
  - botões do HUD (`operators/viewport_hud.py`);
  - keymap no botão direito (`face_frame/dim_edit_overlay.py`);
  - ausência de `GPUOffScreen` no projeto.
- `_reversa_sdd/hb_core/node-group-interfaces.md`, `GeoNodeWall`: entradas `Length`, `Height`, `End Height`, `Thickness`, `Left Angle`, `Right Angle` e materiais; **sem entrada de curvatura**.
- `_reversa_sdd/wall_editor/requirements.md`, `_reversa_sdd/hb_layouts/requirements.md`, `_reversa_sdd/ui/requirements.md`, `_reversa_sdd/hb_placement/requirements.md`, `_reversa_sdd/domain.md#R-04..R-08`.
- RAG Blender 5.2 (APIs confirmadas):
  - `docs/rag/blender-api/corpus/bpy.ops.wm.md#bpy.ops.wm.window_new`
  - `docs/rag/blender-api/corpus/bpy.types.SpaceImageEditor.md#bpy.types.SpaceImageEditor.draw_handler_add`
  - `docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.menu_contents`
  - `docs/rag/blender-api/corpus/bpy.types.KeyMapItems.md#bpy.types.KeyMapItems.new`
  - `docs/rag/blender-api/corpus/bpy.types.Context.md#bpy.types.Context.temp_override`
  - `docs/rag/blender-api/corpus/bpy.types.Window.md#bpy.types.Window.screen`, `bpy.types.Area.md#bpy.types.Area.type`
  - A classe da barra de status (`STATUSBAR_HT_header`) não consta da referência: a linha de estado vai para o painel.
- Material de referência do usuário: resumos dos vídeos do Promob (movimentação básica; construção e Editor de Paredes).

## 2. Alternativas avaliadas

### Onde desenhar a planta do Editor de Paredes

| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Janela nova com área Image Editor (desenho `POST_PIXEL`, painéis na região N) | Janela própria como na referência; painéis nativos do Blender; não interfere no 3D | Comportamento de janelas varia por sistema; não testável em `--background` | **Escolhida (D-02)** |
| Painel sobre a viewport 3D | Simples de abrir | Disputa eventos com a navegação e a seleção do 3D; sem painéis nativos | Descartada |
| Imagem renderizada fora da tela (`GPUOffScreen`) mostrada num diálogo | Diálogo modal "de verdade" | Diálogos do Blender não recebem cliques dentro da imagem; sem precedente no projeto | Descartada |

### Onde mostrar a janela "Mover Sobre"

| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Painel desenhado sobre a viewport, controlado por modal | Abre na hora, perto do ponto do arraste; mesmo motor 2D | Campos digitáveis feitos à mão (Tab/Enter) | **Escolhida (D-15)** |
| Janela nova (como o editor de paredes) | Painéis nativos | Lenta para uma ação repetida dezenas de vezes por projeto | Descartada |

### Como capturar o botão direito

| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Item de keymap do add-on com `poll` dependente do modo | Sem modal permanente (o salvamento automático continua); volta ao normal sozinho | Conflito possível com "selecionar com o botão direito" (só com o modo ligado) | **Escolhida (D-14)** |
| Modal permanente | Controle total | Bloqueia o salvamento automático (docstring do HUD) | Descartada |

### Rebaixar parede

| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Esconder a parede e mostrar uma cópia baixa | Dados intactos para posicionamento, elevações e teto | Um objeto auxiliar por parede rebaixada | **Escolhida (D-19)** |
| Reduzir `Height` e guardar o original | Simples | Quebra tudo que lê a altura | Descartada |

### Folha 3D da porta de ambiente (revisão de 2026-10-05)

Levantamento: a porta do Home Builder 5 é uma gaiola `GeoNodeCage` (`Dim X/Y/Z`, `IS_ENTRY_DOOR_BP`) com o filho
`GeoNodeDoorSwing` (símbolo 2D; inputs `Is Double`, `Is Left`, `Swing Inside`, `Door Thickness`, sem ângulo). As
aberturas da camada nova (`btm_opening`) são só o recorte. Nenhuma tem folha 3D.

| Alternativa | Prós | Contras | Escolha |
|---|---|---|---|
| Pivô + folha BMesh filhos da porta, criados no primeiro "Abrir" | Não mexe no node group; projetos antigos só mudam quando o usuário abre uma porta; reaproveita a inspeção | Lado e sentido precisam ser deduzidos | **Escolhida (D-20)** |
| Folha para todas as portas ao carregar | Visual uniforme | Muda arquivos sem pedido | Descartada |
| Input de ângulo no `GeoNodeDoorSwing` / folha no node group | Uma fonte só | Node group do legado, fora do pacote; quebra atualizações | Descartada |
| Girar só o símbolo 2D | Simples | Não atende "a porta gira" do RF-20 | Descartada (esclarecimento) |

Lado e sentido: a caixa avaliada do símbolo (o arco ocupa o quarto de círculo da abertura) dá a dobradiça (canto do
arco no eixo da porta) e o lado (sinal de Y); os inputs servem de conferência. Fonte: `hb_types.py:599`,
`operators/doors_windows.py:11-22` (combinações de abertura).

### Conversão das paredes da camada nova (revisão de 2026-10-05)

`btm.wall_builder` grava `obj["btm_wall_segments"]` (JSON: `start`, `end` na linha de centro, `thickness`, `height`,
`offset`) e gera a malha com ±t/2 (`geometry/mesh_gen.generate_wall_from_segments`). A conversão usa o JSON (exato)
em vez de reconstruir pela malha. Trechos com pontas coincidentes viram uma cadeia com orientação `CENTER`, que o
modelo e o aplicador já tratam (`Chain.offset_for_orientation`).

### Lado da espessura e Direção (revisão pós-auditoria ao vivo)

Medido no Blender do titular: sala anti-horária criada pelo editor → paredes com a espessura para dentro (y 0–0,15),
balcão filho da parede em y −0,59…0 (fora), porta "Inside" abrindo para fora. O construtor legado
(`home_builder_walls.draw_walls`) sempre põe a espessura em +Y local (à esquerda do sentido) e não corrige o sentido:
fica certo só quando a sala é desenhada no horário. Referência pedida pelo titular (Promob): a linha interna (tracejada) é
a medida real; a externa (contínua) soma a espessura; clicar na face ou vértice e digitar a medida.
https://qualificad.com.br/editor-de-paredes-promob/

| Alternativa | Escolha |
|---|---|
| Nós = face interna + `side` da espessura, invertendo a cadeia no OK quando `side = RIGHT` | **Escolhida (D-25)** |
| Normalizar todo contorno para horário, sem opção | Descartada (titular pediu a Direção) |
| Manter as três orientações (face direita/esquerda/centro) | Descartada (não atende "medida real = interna") |

### Botão direito no Modo Objeto (A001)

Experimento na instância de teste com `event_simulate`: o atalho em "3D View" não dispara porque o mapa "Object Mode"
liga RMB a `wm.call_menu VIEW3D_MT_object_context_menu` antes; com o atalho também em "Object Mode", o arraste e a
janela abriram. Os demais modos têm menus de contexto em seus próprios mapas → registrar em todos (D-29).

### Desregistro legado (A002)

`getattr(bpy.types, cls.__name__)` só acha a classe quando o nome Python coincide com o identificador RNA
(`HOME_BUILDER_WALLS_OT_x`); com nomes em minúsculas (`home_builder_walls_OT_x`) devolve None e o `unregister()` pula.
`cls.is_registered` funciona no 5.2 (experimento: False → True → False), embora não esteja no RAG.

### Fechamento da sala e pé-direito (4ª auditoria)

Reproduzido em fumaça: com o lápis, digitar 3000/2000/3000/2000 volta ao início, mas a cadeia fica aberta com o último
vértice duplicado (nós `(0,0)…(0,0)`), sem pergunta; no OK sai a sala com o último canto solto (imagem do titular). O
clique a 15 px do início também cria vértice solto (raio atual de 12 px, sem ímã). O lápis usava 2.600 mm; o projeto
(`scene.home_builder.ceiling_height`, cena principal) estava em 2.438 mm — o mesmo valor que o "Desenhar Paredes"
(`operators/walls.py:1604`) e as cotas (`measure/scene_cotas.ceiling_height`) usam.

| Alternativa | Escolha |
|---|---|
| Ímã em pixels de tela (15 px) + pergunta | **Escolhida (D-33)** |
| Ímã em milímetros | Descartada (varia na tela com o zoom) |
| Rede de segurança no OK (fechar cadeias com pontas coincidentes) | **Escolhida (D-35)**, além do ímã |
| Pé-direito das paredes novas = projeto; existentes por opção marcada | **Escolhida (D-36, D-37)** |

### Legado: "Desenhar Paredes" e pé-direito (3ª sessão de esclarecimento)

- `home_builder_walls_OT_draw_walls` já tem um "close snap": a 0,15 m do primeiro ponto (com 2+ paredes) a parede atual
  é esticada até o início e o clique chama `close_room` (liga `obj_x.connected_object` e ajusta as esquadrias) —
  sem perguntar e sem tratar o comprimento digitado (`apply_typed_value` só confirma a parede). D-39 troca o raio e
  põe a pergunta antes do `close_room`.
- As paredes do legado guardam o tipo em `WALL_TYPE` (`Exterior`/`Interior`/`Half`/`Fake`) e marcam `IS_HALF_WALL` e
  `IS_FAKE_WALL`; a altura de criação vem de `ceiling_height`, `half_wall_height` ou `fake_wall_height`. O callback
  `update_ceiling_height` só recalcula armários; D-38 acrescenta as paredes de altura cheia.

## 3. Padrões aplicáveis

- Núcleo puro + casca Blender, como `inspection/pivot_math.py` (001): `unittest` sem `bpy`.
- Rascunho e aplicação transacional (abrir → editar cópia → OK aplica, Cancelar descarta), como o Configurador de Dimensões da 001 (`standards/api.py` `begin_draft`/`apply_draft`).
- Contrato de modal do HUD (`register_active_modal`, `_exit_requested`) para os botões dos modos.
- Classificação por precedência (frente/módulo antes de parede), como a exclusão em `operators/ops_general.py`.

## 4. Questões técnicas em aberto (não bloqueiam)

- Lado da espessura do `GeoNodeWall` em relação à base e efeito de "Orientação" no construtor atual (D-06).
- ~~Mecanismo da folha de portas e janelas de ambiente do Home Builder 5 (D-13)~~ — levantado: não há folha; decisão D-20.
- Conferir no uso as 6 combinações de abertura contra o símbolo 2D (D-20).
- Regra de "frente" por biblioteca para o alinhamento (gabinetes face frame e closets, D-16).
