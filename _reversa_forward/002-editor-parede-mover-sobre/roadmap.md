# Roadmap: Editor de paredes 2D, editor de geometria, propriedades por tipo e "Mover Sobre"

> Identificador: `002-editor-parede-mover-sobre`
> Data: `2026-10-05`
> Requirements: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Quatro entregas, em blocos que podem ser usados separadamente:

- **B1 — Identificar e editar o selecionado:** classificador único de tipo de objeto; janela de propriedades por tipo, com dimensões, cotas editáveis e "Abrir"; cotas desenhadas ao selecionar.
- **B2 — "Mover Sobre":** botão que liga o modo; arraste com o botão direito; painel com as vistas superior e frontal desenhado sobre a viewport; alinhamento por lados, profundidade e altura.
- **B3 — Editor de Paredes 2D:** janela própria com uma planta vetorial em rascunho. O desenho a lápis, a linha interna/externa, o painel do trecho e a grade só mudam as paredes do Home Builder 5 no OK.
- **B4 — Geometria e operações de parede:** placa e caixa por pontos de referência, que entram na lista de peças; remover parede com opções; rebaixar; invisível.

A lógica que dá para testar sem o Blender fica em módulos de Python puro (como `inspection/pivot_math.py` na 001): modelo das paredes, transformação de tela 2D, alvos de alinhamento e cálculo de cotas. A parte do Blender (desenho, entrada, aplicação) é fina por cima disso.

## 2. Princípios aplicados

`.reversa/principles.md` não existe; valem as regras do `CLAUDE.md`:

| Princípio (CLAUDE.md) | Como a feature se relaciona | Status |
|---|---|---|
| Editar só `blendertomob/`; consultar o RAG 5.2 | APIs confirmadas no RAG: `bpy.ops.wm.window_new`, `SpaceImageEditor.draw_handler_add`, `UILayout.menu_contents`, `KeyMapItems.new`, `Context.temp_override`, `Window.screen`, `Area.type` | respeita |
| Operadores que alteram dados com `UNDO` | Editor de paredes (OK), "Mover Sobre" (Confirmar), propriedades, geometria e operações de parede: todos com `UNDO`, um passo por confirmação | respeita |
| Handlers e keymaps removidos em todos os caminhos e no `unregister()` | Keymap do botão direito, handlers de desenho da janela de paredes, do painel "Mover Sobre" e das cotas ao selecionar | respeita |
| Inputs de GN só via `compat` | Dimensões de gabinetes e paredes (`Dim X/Y/Z`, `Length`, `Height`, `End Height`, `Thickness`, `Left/Right Angle`) por `compat.get/set_gn_input` | respeita |
| Sem threads tocando `bpy` | Desenho e aplicação no thread principal | respeita |
| Textos de UI em português | Rótulos da referência ("Painel", "Grid", "Construir Parede", "Linhas Magnéticas"…) em português | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|---|---|---|---|---|
| D-01 | Núcleos de Python puro e testáveis: `canvas2d/view.py` (transformação mundo ↔ tela, pan/zoom, enquadrar, grade, encaixe ortogonal ±2,5°, distância a segmento/ponto), `walls2d/model.py` (grafo de nós e trechos, linhas interna/externa, comprimento interno/externo, ângulos absoluto/relativo, dividir/unir/inverter, fechamento), `move_over/align.py` (alvos e deslocamento no referencial de B), `measure/cotas.py` (cotas a partir de intervalos e alturas) | Matemática é o maior risco e precisa de testes rápidos fora do Blender (`unittest`, como a 001) | Lógica dentro dos operadores (só testável em fumaça no Blender) | 🟢 |
| D-02 | **Editor de Paredes em janela própria:** `wm.window_new` + troca da área para Image Editor sem imagem; a planta é desenhada por `SpaceImageEditor.draw_handler_add` (`POST_PIXEL`), a entrada vem do modal `btm.wall_editor` ligado a essa área, e os painéis "Painel", "Grid" e OK/Cancelar ficam na região lateral (N) do Image Editor, visíveis só nessa área (marca na área/janela). OK e Cancelar fecham a janela | O Blender não tem janela flutuante personalizada; o Image Editor dá uma área 2D com região lateral de painel nativo | Desenhar a planta sobre a viewport 3D (conflita com navegação e seleção do 3D); Node Editor (layout de nós sem uso) | 🟡 |
| D-03 | **Rascunho em memória:** ao abrir, as paredes do ambiente (Home Builder 5, `IS_WALL_BP`, encadeadas por `COPY_LOCATION`, `hb_types.GeoNodeWall.get_connected_wall`) viram o modelo de D-01; nada é gravado até o OK | RN-16: Cancelar não pode tocar no 3D | Editar as paredes ao vivo e desfazer no Cancelar (desfazer no meio de modal é frágil) | 🟢 |
| D-04 | **Aplicador no OK** (`walls2d/apply.py`): atualiza paredes existentes (`Length`, `Height`, `End Height`, `Thickness`, posição e rotação); cria trechos novos pelo mesmo caminho do construtor (`operators/walls.py` `create_wall`, `GeoNodeWall.connect_to_wall`); remove os excluídos; recalcula esquadrias (`walls.py` atualização de esquadrias, `Left/Right Angle`) e piso/teto ligados; tudo num passo de desfazer, com aviso prévio dos itens presos (RF-10) | Reaproveita o legado que os gabinetes já entendem (filhos da parede, posicionamento) | Gerar paredes novas da camada `btm_wall` (os gabinetes das bibliotecas não usam) | 🟡 |
| D-05 | **Escopo das paredes:** só paredes do Home Builder 5 (as do construtor "Desenhar Paredes"); paredes da camada nova (`btm.wall_builder`) aparecem na planta como referência, sem edição | É o sistema usado pelos gabinetes e pelo construtor do painel | Unificar os dois modelos agora (custo alto, fora do pedido) | 🟡 |
| D-06 | **Linha interna/externa e orientação:** a linha de desenho é a base da parede (origem e eixo X local do `GeoNodeWall`); a espessura vai para um lado. "Orientação" define qual face é a linha de desenho (Direita, Esquerda ou Centro). A linha interna é a face voltada para o interior do contorno (lado do giro); o comprimento interno sai das esquadrias com as paredes vizinhas | RN-15 e exemplo 2.700/2.400 | Medida interna fixa = externa − 2×espessura (erra em cantos não retos) | 🟡 (lado da espessura no nó a confirmar) |
| D-07 | **Ângulo do Arco:** o `GeoNodeWall` não tem entrada de curvatura (`_reversa_sdd/hb_core/node-group-interfaces.md`, `GeoNodeWall`); o campo aparece desabilitado com "Paredes curvas não são suportadas" | Sem suporte no nó, aplicar arco exigiria um nó novo | Implementar parede curva agora | 🟢 |
| D-08 | **Tipos "Divisória" e "Mureta":** guardados em idprop `btm_wall_type`; mudam só padrões e rótulo (Divisória: espessura padrão 100 mm; Mureta: pé-direito padrão 1.100 mm); a geometria é a mesma parede | Não há regra de geometria na referência | Tipos com geometria própria (sem especificação) | 🔴 |
| D-09 | **Classificador único** `selection/classify.py`: dado um objeto, devolve (tipo, raiz, biblioteca) pela precedência de RN-01, para objetos do Home Builder 5 (`IS_*`, `hb_part_role`, `MENU_ID`) e da camada nova (`btm_plane.object_kind`); usado pela janela de propriedades e pelo "Mover Sobre" | Hoje cada operador decide do seu jeito; a exclusão (`operators/ops_general.py:121-210`) mostra a precedência certa | Um painel por biblioteca | 🟢 |
| D-10 | **Janela de propriedades** = novo painel `BTM_PT_ObjectProperties` na barra lateral "Blender to Mob" (substitui `BTM_PT_ContextProperties`, `ui/panels.py:327`), com grupos por tipo: Dimensões, Cotas, Abrir, Parede, Outras e Ações. Dimensões de gabinetes pelos inputs `Dim X/Y/Z` (via `compat`), registrando medida manual (`standards.sync.add_override`, 001 RN-23); "Abrir" usa `inspection.fronts`; "Ações" embute o menu do objeto com `UILayout.menu_contents(MENU_ID)`; a linha de estado (RF-24) fica no topo do painel | Uma janela para todos os tipos; reaproveita prompts e inspeção existentes | Janela flutuante própria (sem região de painel nativa) | 🟢 |
| D-11 | **Cotas de RN-04** em `measure/cotas.py`: anterior e posterior pelos intervalos da parede (`hb_placement.PlacementMixin.get_wall_children_sorted` e o vão, respeitando o filtro vertical), inferior por `location.z` no mundo, superior por `scene.home_builder.ceiling_height` − topo, afastamento pela face de trás até a parede. Editar uma cota muda só a posição do módulo no referencial da parede. Módulo sem parede: anterior e posterior ficam vazias com a nota "módulo livre" | Mesmos obstáculos que o posicionamento já usa (`_reversa_sdd/hb_placement/requirements.md#RN-09..RN-14`) | Raios nas 6 direções (custo, falsos acertos em peças internas) | 🟡 |
| D-12 | **Cotas ao selecionar (RF-25):** handler `POST_PIXEL` em `overlays/` reaproveitando o desenho de `hb_placement.draw_placement_dimensions` | Mesmo visual das cotas de posicionamento | Objetos de cota permanentes (`GeoNodeDimension`), que poluem a cena | 🟡 |
| D-13 | **"Abrir" em portas e janelas de ambiente (RF-20):** novo adaptador `inspection/adapters/room_doors.py` para portas e janelas do Home Builder 5 (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`); o mecanismo da folha dessas portas não foi levantado | Mantém um só controle de abrir (001) | — | 🔴 |
| D-14 | **Modo "Mover Sobre" sem modal permanente:** o estado é `WindowManager.btm_move_over.enabled`; um item de keymap do add-on em "3D View" (`RIGHTMOUSE` `PRESS`, `head=True`) chama `btm.move_over_drag`, cujo `poll` só passa com o modo ligado e um objeto movível sob o cursor. Com o modo desligado, o evento segue para o menu do Blender. O modal existe só durante o arraste | Modal permanente bloqueia o salvamento automático (docstring de `operators/viewport_hud.py`); há precedente de keymap no botão direito (`face_frame/dim_edit_overlay.py`) | Modal permanente que captura o botão direito | 🟢 |
| D-15 | **Janela "Mover Sobre" como painel sobre a viewport:** modal `btm.move_over_dialog` desenha (`POST_PIXEL`) um painel com duas telas (superior e frontal), alvos, distâncias, campos digitáveis (Tab alterna X, profundidade, altura) e botões Confirmar/Cancelar; Enter confirma, Esc cancela; a prévia move A no 3D; Confirmar fecha com `UNDO` | Abre na hora e usa o mesmo motor `canvas2d` do editor de paredes | Janela nova do Blender a cada uso (lenta e sem foco no ponto do arraste) | 🟡 |
| D-16 | **Alinhamento no referencial de B:** caixas de A e B no espaço local de B (cantos da caixa avaliada); "frente" = lado oposto à parede (−Y local nos gabinetes do Home Builder 5; regra por biblioteca no classificador); A recebe a rotação Z de B antes de alinhar; com parede como B, "profundidade 0" é a face interna da parede | Medidas coerentes com qualquer rotação | Eixos do mundo (erra com paredes inclinadas) | 🟡 |
| D-17 | **Arrastar no plano da parede (RF-34):** modal `btm.move_on_wall` restrito a X/Z da parede, com cotas ao vivo e respeitando "Evitar Sobreposição" (`PlacementMixin.avoid_overlap`) | Reaproveita o vão e as cotas | — | 🟡 |
| D-18 | **Geometria livre:** `btm_plane.object_kind = 'GEOMETRY'` (já existe no enum) + PropertyGroup `btm_geometry` (placa/caixa, medidas, fabricação, componente, matéria-prima, espessura, acabamento); criação por pontos com `hb_snap` e o seletor de pontos de `hb_placement.DimensionOperatorMixin`; malha por BMesh; entra na lista de peças por um adaptador novo em `cutting/part_sources.py` com origem `FREE_GEOMETRY` (já prevista no JSON v2 da 001) | Sem contrato novo; o JSON v2 já aceita a origem | Obstáculos (`ops_obstacles.py`), que não são peças | 🟢 |
| D-19 | **Operações de parede:** "Remover Parede" é um diálogo novo (Segmento, Tudo, Manter o selecionado, Remover módulos) sobre a exclusão existente (`operators/walls.py`); "Rebaixar" esconde a parede na viewport e mostra uma cópia baixa de 150 mm como filha, mantendo todas as entradas (o posicionamento e as vistas continuam lendo a altura real); "Invisível" usa exibição em contorno, com a opção de esconder o contorno | Não muda os dados lidos por outras partes | Reduzir `Height` de verdade (quebra posicionamento, elevações e teto) | 🟡 |
| D-20 | **Folha 3D das portas de ambiente (RF-20):** cada porta `IS_ENTRY_DOOR_BP` com símbolo `GeoNodeDoorSwing` ganha, **no primeiro "Abrir"**, um pivô (Empty) na dobradiça e uma folha filha (BMesh: largura × `Door Thickness` × altura da porta), marcados `btm_room_door_pivot`/`btm_room_door_leaf`; porta dupla = dois pivôs. Lado da dobradiça e sentido saem da caixa avaliada do próprio símbolo 2D (o arco desenha o quarto de círculo do lado certo), com `Is Left`/`Is Double`/`Swing Inside` lidos por `compat` como conferência. A folha é refeita a partir de `Dim X/Z` da gaiola a cada "Abrir" (porta redimensionada continua certa). Adaptador `inspection/adapters/room_doors.py` em `inspection.fronts._adapters()`: `get/apply` giram o pivô em Z (0–90°); o salvar fechado da 001 (`inspection/save_guard.py`) passa a valer para elas automaticamente. Porta sem símbolo (vão aberto) e janelas: sem "Abrir" | Sem mexer no node group do Home Builder 5; reaproveita inspeção, controle giratório e salvar fechado | Folha criada para todas as portas ao carregar o arquivo (muda o visual de projetos antigos sem pedido); editar o node group `GeoNodeCage` (fora do pacote, quebra atualizações) | 🟡 |
| D-21 | **Módulos de trecho apagado (RF-10, RN-13):** a sessão do editor ganha `remove_modules` (padrão Falso). No OK, se `plan.removed_sources` tiver filhos que não sejam `obj_x`/cotas/portas/janelas, o painel "Confirmar" mostra a lista e a caixa "Remover os módulos junto?" e pede o segundo clique (mesmo fluxo `confirm_pending` dos itens que não cabem); `apply.apply_plan(context, plan, remove_modules)` repassa para `ops_wall_extras.remove_wall` | Mesma rotina e mesmo vocabulário do "Remover Parede…" (D-19) | Diálogo modal separado no OK (dois diálogos seguidos) | 🟢 |
| D-22 | **Paredes de outra camada (RF-02, RF-38):** referência = contorno no piso da malha (`scene_io.reference_segments`, já feito na correção A004). Conversão: ao abrir o editor com objetos `btm_plane.object_kind = 'WALL'` selecionados, `btm.wall_editor.invoke` abre `invoke_props_dialog` com a escolha "Converter para paredes editáveis" / "Só referência". Converter lê `obj["btm_wall_segments"]` (JSON do `btm.wall_builder`: `start`, `end` na linha de centro, `thickness`, `height`, `offset`), passa para o mundo com `matrix_world`, junta trechos consecutivos de pontas coincidentes (0,01 m) em cadeias com orientação `CENTER` e entra no rascunho como trechos **novos**; no OK, o objeto original é removido (um passo de desfazer junto com o resto). Sem o JSON, o objeto fica só como referência e o editor avisa | Reaproveita modelo, aplicador e orientação `CENTER` já existentes; desfazer em um passo | Converter na hora de abrir (gravaria no 3D antes do OK, contra RN-16) | 🟡 |
| D-23 | **Rebaixar 150 mm fixo (RF-36):** confirma D-19 com `LOWERED_HEIGHT = 0.15`; sem campo de configuração | Esclarecimento de 2026-10-05 | Altura configurável | 🟢 |
| D-24 | **"Mobi Editor" e botões em grade flutuantes:** fora da 002 (Won't); vão para a feature 003. Registro técnico para lá: o Python do Blender não cria tipo de editor novo; as saídas são área de trabalho própria (`bpy.types.WorkSpace`) com 3D Viewport e HUD ampliado, e/ou `NodeTree` próprio no seletor de editores | Esclarecimento de 2026-10-05 | — | 🟢 |
| D-25 | **Direção e medida real = interna (RN-15, RF-40; corrige A003):** o modelo troca `Chain.orientation` (Direita/Esquerda/Centro, "qual face é a linha desenhada") por `Chain.side` = `'LEFT'`/`'RIGHT'`, o lado para onde a espessura cresce em relação ao sentido dos nós. **Os nós são sempre a face interna** (medida real): `INNER` = linha dos nós, `OUTER` = linha deslocada pela espessura; o comprimento digitado é a distância entre nós. No OK: `side == 'LEFT'` usa a cadeia como está (o `GeoNodeWall` põe a espessura em +Y, à esquerda); `'RIGHT'` inverte a ordem dos nós e trechos antes de criar/atualizar, para a espessura cair à direita do desenho. Ao fechar um contorno, o lápis escolhe `side` para a espessura ficar **para fora** (horário → LEFT, anti-horário → RIGHT), de modo que o interior fique em −Y local: frente dos módulos e "Swing Inside" das portas voltados para dentro. Paredes lidas da cena entram com `side = 'LEFT'` (o legado sempre põe a espessura à esquerda). Trocar a Direção de paredes existentes inverte o sentido delas; os filhos (módulos, portas) mantêm a posição no mundo | Uma regra só para medir, desenhar e aplicar; corrige a inversão medida na auditoria ao vivo | Normalizar todo contorno para horário sem expor a Direção (o titular pediu a opção) | 🟡 |
| D-26 | **Conversão com a Direção (D-22 revista):** a linha de centro do `btm_wall_segments` é deslocada meia espessura para virar a face interna: em contorno fechado, para o interior (área com sinal do polígono) e `side` para fora; em cadeia aberta, `side = 'LEFT'` e deslocamento para a direita. A orientação `CENTER` sai do modelo | Mantém a parede convertida no mesmo lugar do 3D | Manter `CENTER` só para a conversão (dois conceitos de lado) | 🟢 |
| D-27 | **Digitação direta (RF-39):** na ferramenta Selecionar/Mover, com uma face ou um vértice selecionado, dígitos vão para `Session.typed` (mostrado junto do cursor) e Enter aplica: na face, `set_length(i, valor, INNER/OUTER)`; no vértice `k`, o comprimento interno do trecho que termina em `k`. Backspace corrige; Esc limpa a digitação antes de cancelar. Clicar num vértice sem arrastar o seleciona | Mesmo fluxo da referência Promob (clicar e digitar) | Só pelo campo do painel | 🟢 |
| D-28 | **Linhas da planta (RF-02):** face interna tracejada, externa contínua (antes as duas eram contínuas); a face selecionada continua destacada | Leitura da referência | — | 🟢 |
| D-29 | **Botão direito do "Mover Sobre" em todos os modos (RF-27; corrige A001):** além de "3D View", o atalho é registrado (`head=True`) em cada mapa de modo da viewport cujo mapa padrão liga o botão direito a um menu de contexto ("Object Mode", "Mesh", "Curve", "Armature", "Pose", "Grease Pencil" etc., descobertos no `keyconfigs.default` ao registrar); o `poll` continua falhando com o modo desligado, devolvendo o clique ao menu. Todos removidos no `unregister()` | Experimento na auditoria: com o atalho em "Object Mode" o arraste e a janela abriram | Trocar o menu de contexto global (afeta o usuário com o modo desligado) | 🟡 |
| D-30 | **OK/Cancelar (RF-09; corrige A005):** painéis do editor com `bl_order` (Ferramentas 0, Painel 1, Grid 2, Confirmar 99), OK/Cancelar no fim. "Cancelar" e Esc pedem confirmação quando o rascunho mudou: `model.plan_signature(plan)` (nós, trechos, removidos, convertidos) comparada à da abertura; o botão usa `WindowManager.invoke_confirm`, o Esc usa a mesma pergunta desenhada na planta (como a de fechamento) | Evita perder o desenho num clique | Desfazer dentro do editor (fora do escopo) | 🟢 |
| D-31 | **Gizmo das portas (corrige A004):** em `inspection/gizmo.py`, a seta só lê/escreve `front.travel()` quando a frente não é articulada (`front.hinged` falso); para portas devolve 0. Vale para a porta de ambiente e para o Módulo Rápido | Erro no console a cada redesenho | Acrescentar `travel()` a todos os adaptadores | 🟢 |
| D-32 | **Desregistro completo (RNF; corrige A002):** nos `register()`/`unregister()` legados que procuram a classe por `getattr(bpy.types, cls.__name__)` (falha para nomes de classe em minúsculas, como `home_builder_walls_OT_*`), trocar por `cls.is_registered` (verificado no Blender 5.2: False → True → False; não consta no RAG). A fumaça passa a conferir, pelo `bl_idname` de todo operador do pacote, que nada sobra após `unregister()` | 280 operadores sobravam (33 arquivos) | Reescrever o registro legado inteiro com `register_classes_factory` (mais invasivo) | 🟢 |
| D-33 | **Ímã no ponto inicial (pedido do titular; A002):** com 2 ou mais trechos desenhados, quando o cursor fica a até `SNAP_CLOSE_PX` = 15 px do ponto inicial, a pré-visualização gruda nele (sem trava ortogonal nem grade), o ponto inicial ganha um anel de destaque e o rótulo "Fechar"; clicar ali abre a pergunta "Deseja fechar a parede?" (a mesma de RN-17). Fora do raio, nada muda | Fechar fica fácil e visível; um clique "quase lá" não cria vértice solto | Raio em mm (varia em pixels com o zoom) | 🟢 (esclarecimento 3ª sessão) |
| D-34 | **Fechamento pelo teclado (A001):** quando um trecho digitado (Enter) ou um vértice arrastado termina a até `CLOSE_TOLERANCE` = 0,01 m do ponto inicial, com 3 ou mais trechos, o editor tira o vértice duplicado e faz a mesma pergunta; Sim fecha (Direção para fora, D-25), Não mantém o desenho aberto | O caminho do teclado tinha a pergunta faltando | Fechar sem perguntar | 🟢 (esclarecimento 3ª sessão) |
| D-35 | **Rede de segurança no OK (A004):** antes de aplicar, toda cadeia aberta com 3 ou mais trechos cujo fim esteja a até 0,01 m do início é fechada (`Chain.close_if_touching`), com a Direção para fora se a cadeia for nova; o relatório do OK diz quantas foram fechadas. Assim nenhuma sala sai com o último canto solto, venha de onde vier | Garante o encontro e a esquadria no canto | Recusar o OK | 🟢 |
| D-36 | **Pé-direito do projeto nas paredes novas (pedido do titular; A003):** ao abrir o editor, `new_height` recebe o pé-direito do projeto (`measure/scene_cotas.ceiling_height`, cena principal — o mesmo `scene.home_builder.ceiling_height` que o "Desenhar Paredes" usa em `operators/walls.py:1604`), em vez do padrão fixo de 2.600 mm da RN-18. Mureta continua com 1.100 mm (tipo explícito) | Uma altura só para o projeto, como o legado | Manter 2.600 mm | 🟢 |
| D-37 | **Uniformizar paredes existentes (RF-42; A005):** no OK, paredes do rascunho de altura cheia (exceto Mureta, meia-parede `IS_HALF_WALL` e parede falsa `IS_FAKE_WALL` do legado) com pé-direito inicial ou final diferente do projeto (tolerância 1 mm) são listadas no painel Confirmar com a caixa "Igualar ao pé-direito do projeto", **marcada por padrão**; marcada, o aplicador grava `Height` e `End Height` = projeto. Desmarcada, mantém as alturas | Atende "toda parede com o mesmo pé-direito" sem apagar silenciosamente uma altura proposital | Forçar sempre, sem opção | 🟢 (esclarecimento 3ª sessão) |
| D-38 | **Configurações atualizam as paredes (RF-43):** o callback legado `update_ceiling_height` (`hb_props.py:78`, hoje só recalcula armários altos/aéreos) passa a gravar também `Height` e `End Height` = novo pé-direito em toda parede `IS_WALL_BP` de todas as cenas do projeto que seja de altura cheia: exclui `btm_wall_type == 'MURETA'`, `WALL_TYPE in {'Half', 'Fake'}` (`IS_HALF_WALL`/`IS_FAKE_WALL`, `operators/walls.py:1626-1628`); depois recalcula as esquadrias (`update_all_wall_miters`) e refaz pisos/tetos ligados (`walls2d/apply.refresh_floors_and_ceilings`). A lógica de quais paredes mudam fica numa função pura testável | Uma regra para todo o projeto, igual ao legado para armários | Atualizar só ao abrir o editor (D-37) | 🟢 |
| D-39 | **Ímã e pergunta no "Desenhar Paredes" 3D (RF-44):** no modal `home_builder_walls.draw_walls` (`operators/walls.py:947`), o "close snap" existente (raio fixo de 0,15 m, fecha **sem perguntar**, só pelo clique) passa a: (1) raio de 15 px de tela, medido como no editor; (2) clicar com o ímã ativo, ou terminar um comprimento digitado (`apply_typed_value`) a até 10 mm do início, entra no estado `pending_close`, que mostra "Deseja fechar a parede?  Enter/Sim · Esc/Não" no cabeçalho e no 3D; Enter ou clique de novo chama o `close_room` existente; Esc volta a desenhar | Mesmo comportamento nas duas ferramentas; reaproveita `close_room` (encontros e esquadrias) | Popup modal do Blender dentro do modal (não suportado de forma simples) | 🟡 (modal legado grande) |

## 4. Premissas

| Premissa | Origem | Risco se errada |
|---|---|---|
| A espessura do `GeoNodeWall` vai para um lado conhecido da base, e a face interna pode ser deduzida do sentido do contorno (D-06) | requirements RN-15; código não confirmado | Linha interna/externa trocada; corrigir só o lado no modelo |
| O Image Editor sem imagem serve de tela 2D com painéis laterais e eventos de modal (D-02) | API confirmada no RAG; uso não testado no projeto | Trocar a área por outra 2D, mantendo o motor `canvas2d` |
| Divisória e Mureta só mudam padrões (D-08) | requirements §10 | Precisar de geometria própria depois |
| A caixa avaliada do `GeoNodeDoorSwing` indica o lado da dobradiça e o sentido de abertura (D-20) | levantamento de 2026-10-05: o símbolo desenha o arco no quarto de círculo da abertura; inputs `Is Left`, `Is Double`, `Swing Inside` | Folha girando para o lado errado; corrigir lendo só os inputs |
| As paredes do `btm.wall_builder` sempre têm `btm_wall_segments` com a linha de centro (D-22) | `operators/wall_builder.py` `_finish` grava o JSON e gera a malha com ±t/2 (`geometry/mesh_gen.generate_wall_from_segments`) | Paredes antigas sem JSON ficam só como referência |

**Desvios em relação ao `requirements.md` (para o usuário confirmar):**
- RN-18 ("ângulo do arco de −180° a 180°"): fica desabilitado, porque a parede atual não é curva (D-07).
- RF-37 ("contorno só quando selecionado"): o contorno aparece sempre e pode ser escondido (D-19).
- RF-24 ("linha de estado"): fica no topo da janela de propriedades, e não na barra de status do Blender, que não tem API pública de acréscimo na referência 5.2.
- RF-20: a folha 3D aparece a partir do primeiro "Abrir" de cada porta (D-20); antes disso a porta continua só com o recorte e o símbolo 2D.
- Janelas de ambiente continuam sem "Abrir" (não há folha nem símbolo de abertura).
- RN-18/RF-05 "orientação Direita, Esquerda ou Centro": passa a ser **Direção** Direita/Esquerda (D-25); o Centro só existia para a conversão e sai (D-26).
- RN-18 "pé-direito … padrão 2.600": passa a ser o pé-direito do projeto (D-36).
- As premissas da 4ª rodada (raio de 15 px, pergunta também no teclado/arraste, igualar existentes com caixa marcada) foram confirmadas no `/reversa-clarify` (3ª sessão).
- RF-11 (placa por pontos): o encaixe automático no objeto sob o cursor fica como está (esclarecimento); o resultado intermitente da auditoria (A009) não vira ação.

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|---|---|---|---|
| Classificador de seleção | — (`operators/ops_general.py:121-210` como referência) | componente-novo | `blendertomob/selection/classify.py` |
| Canvas 2D | — (`hb_gpu_draw.py` como base de desenho) | componente-novo | `blendertomob/canvas2d/` (transformação, grade, encaixe, desenho) |
| Editor de Paredes | `_reversa_sdd/wall_editor/` (spec sem código); `operators/walls.py`, `hb_types.py` `GeoNodeWall` | componente-novo + regra-nova | `blendertomob/walls2d/` (modelo, aplicador, operador, painéis, janela) |
| Janela de propriedades | `_reversa_sdd/ui/requirements.md#R-02`; `ui/panels.py` `BTM_PT_ContextProperties` | regra-alterada | `BTM_PT_ObjectProperties` com grupos por tipo e todas as bibliotecas |
| Cotas | `_reversa_sdd/hb_placement/requirements.md#RN-09..RN-14`; `hb_placement.py` | componente-novo | `blendertomob/measure/cotas.py` + overlay de cotas ao selecionar |
| "Mover Sobre" | — (`hb_placement.py:520-582` encostar ao lado, `viewport_hud.py` botões) | componente-novo | `blendertomob/move_over/` (alvos, arraste, painel, keymap) |
| Inspeção | `inspection/` (001) | regra-alterada | Adaptador de portas de ambiente com folha 3D criada no primeiro "Abrir" (D-20); "Abrir" na janela de propriedades |
| Portas de ambiente | `operators/doors_windows.py` (gaiola + `GeoNodeDoorSwing`), `hb_types.py:599` | regra-nova | Pivô e folha 3D filhos da porta (D-20); o node group não muda |
| Construtor da camada nova | `operators/wall_builder.py` (`btm_wall_segments`) | regra-nova | Conversão das paredes selecionadas no editor (D-22) |
| Geometria livre | `data/properties.py` `object_kind='GEOMETRY'` | componente-novo | `blendertomob/geometry_free/` + adaptador em `cutting/part_sources.py` |
| Operações de parede | `operators/walls.py` (excluir, ocultar) | regra-nova | Remover com opções, rebaixar e invisível |
| HUD | `operators/viewport_hud.py` | regra-alterada | Botão "Mover Sobre" |
| Propriedades do projeto | `hb_props.py` `update_ceiling_height` | regra-alterada | Também atualiza a altura das paredes de altura cheia (D-38) |
| Construtor 3D de paredes | `operators/walls.py` `home_builder_walls_OT_draw_walls` | regra-alterada | Ímã de 15 px e pergunta antes de fechar (D-39) |

## 6. Delta no modelo de dados

- **Novos:**
  - `WindowManager.btm_move_over` (modo ligado, tolerância de 12 px);
  - `WindowManager.btm_wall_editor` (ferramenta ativa, grade, linhas magnéticas, trecho e linha selecionados — o rascunho fica em memória);
  - PropertyGroup `Object.btm_geometry`;
  - idprops de parede `btm_wall_type`, `btm_wall_orientation`, `btm_wall_lowered`;
  - objetos filhos da porta de ambiente marcados `btm_room_door_pivot` / `btm_room_door_leaf` (D-20);
  - campo de sessão `remove_modules` no editor (não salvo, D-21).
- **Nenhum campo removido.** O `HB_Wall_Editor_Props` (`hb_props.py:824`, nunca usado) continua lá; ver `data-delta.md`.
- Detalhe completo em: `_reversa_forward/002-editor-parede-mover-sobre/data-delta.md`

## 7. Delta de contratos externos

Nenhum contrato muda. As geometrias marcadas como peça de fabricação entram no JSON global v2 e no CSV da 001 com a origem `FREE_GEOMETRY`, que já existe no esquema (`_reversa_forward/001-addon-moveis-planejados/interfaces/json-global-v2.md`).

## 8. Plano de migração

1. Paredes existentes sem `btm_wall_type`/`btm_wall_orientation` são lidas como Normal e Direita.
2. `BTM_PT_ContextProperties` sai do registro e é substituído por `BTM_PT_ObjectProperties` (sem dados persistentes).
3. Nenhuma migração de arquivo é necessária.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|---|---|---|---|
| Aplicar o rascunho quebra a cadeia `COPY_LOCATION` ou as esquadrias (paredes desalinhadas) | alto | média | Aplicador sobre as funções do construtor; teste de fumaça com sala de 4 paredes, divisão e remoção de vértice; Cancelar sem efeito |
| Keymap do botão direito conflita com quem usa "selecionar com o botão direito" | médio | média | Só age com o modo ligado (poll); com o modo desligado o evento segue normalmente |
| A janela do Image Editor tem comportamento diferente entre sistemas (foco, tamanho) | médio | média | Fallback: abrir o editor numa área da janela atual |
| Cotas erradas em módulos de canto ou rotacionados | médio | média | Testes de `measure/cotas.py` com casos de canto; nota "módulo livre" quando não houver parede |
| Alinhamento do "Mover Sobre" entre bibliotecas com origens diferentes (frente em −Y ou +Y) | médio | alta | Regra de frente por biblioteca no classificador (D-16) e testes por par de bibliotecas |
| Volume da feature (4 blocos) | alto | alta | Blocos independentes (B1 → B2 → B3 → B4), cada um com critério de pronto próprio |
| Folha 3D girando para o lado errado em alguma combinação de `Is Left`/`Swing Inside`/porta dupla (D-20) | médio | média | Fumaça com as 4 combinações de porta simples e as 2 de porta dupla, comparando a folha aberta com a caixa do símbolo 2D |
| Conversão de parede da camada nova com trechos fora de ordem ou com deslocamento (`offset`) (D-22) | médio | baixa | Juntar trechos pela coincidência de pontas; `offset` vira a base Z da parede; teste com 1 trecho, cadeia aberta e sala fechada |
| A pergunta de módulos no OK passar despercebida (D-21) | baixo | média | Mesmo padrão do aviso de itens que não cabem: lista + segundo clique; padrão seguro (não remove) |
| Inverter a Direção de paredes existentes deixa módulos atrás do corpo da parede (D-25) | médio | baixa | Filhos mantêm a posição no mundo; aviso no painel ao trocar a Direção de trecho com filhos |
| Atalho em mapas de modo conflitar com atalhos do usuário (D-29) | baixo | média | Só age com o modo ligado (`poll`); itens criados no keyconfig do add-on e removidos no `unregister()` |
| Trocar o padrão de registro em 33 arquivos legados quebrar algum registro (D-32) | médio | baixa | Troca mecânica e uniforme; as 5 fumaças e a verificação por `bl_idname` antes/depois |
| Ímã atrapalhar quem quer terminar perto do início sem fechar (D-33) | baixo | baixa | Raio pequeno (15 px) e pergunta com "Não" |
| Igualar o pé-direito apagar uma altura proposital (D-37) | médio | média | Lista no painel antes do OK e caixa desmarcável; Mureta excluída |
| Mudar o pé-direito nas Configurações alterar paredes que deviam ficar baixas (D-38) | médio | baixa | Exclui Mureta, meia-parede e parede falsa pelas marcas; um passo de desfazer |
| Alterar o modal legado do "Desenhar Paredes" quebrar o desenho no 3D (D-39) | alto | média | Mudança restrita ao "close snap" e ao `apply_typed_value`; fumaça do legado + teste com eventos simulados do construtor 3D |

## 10. Critério de pronto

- [ ] B1: selecionar parede, gabinete de cada biblioteca, frente, porta/janela de ambiente, geometria e obstáculo mostra os grupos certos; cotas editáveis movem o módulo; desfazer em um passo
- [ ] B2: "Mover Sobre" alinha lado, profundidade (0/30/50/75/100%), altura e empilhamento; Cancelar restaura; o botão direito volta ao normal com o modo desligado; o salvamento automático continua
- [ ] B3: desenhar a lápis, linha interna/externa, painel do trecho, vértices, grade e OK/Cancelar funcionando sobre paredes do Home Builder 5; sala de 4 paredes refeita sem desalinhamento
- [ ] B4: placa e caixa por pontos, na lista de peças quando marcadas; remover com opções, rebaixar e invisível
- [ ] Revisão de 2026-10-05: porta de ambiente abre e fecha pela janela de propriedades e pela inspeção, nas 6 combinações, e salva fechada (D-20); OK pergunta pelos módulos de trecho apagado e respeita a resposta (D-21); paredes da camada nova selecionadas são convertidas sob pergunta ou ficam como referência (D-22)
- [ ] Revisão pós-auditoria ao vivo: sala desenhada nos dois sentidos fica com espessura para fora e módulos/portas "para dentro" (D-25); digitar na face/vértice muda a medida (D-27); botão direito do "Mover Sobre" abre a janela em Modo Objeto e em Edição (D-29, com eventos simulados); Cancelar com alterações pergunta (D-30); sem erro de gizmo com porta selecionada (D-31); nenhum operador sobra após `unregister()` (D-32)
- [ ] Configurações → todas as paredes de altura cheia acompanham o pé-direito (D-38); "Desenhar Paredes" 3D com ímã de 15 px e pergunta (D-39)
- [ ] Fechamento: ímã a 15 px com destaque; fechar por clique, teclado ou arraste pergunta; nenhum OK cria sala com o último canto solto (D-33 a D-35); paredes novas com o pé-direito do projeto e opção de igualar as existentes (D-36, D-37)
- [ ] `ruff`, `check_api.py`, testes `unittest` dos núcleos de Python puro e fumaças no Blender 5.2 passando; registro/desregistro sem resíduo (keymaps, handlers, janelas)
- [ ] `legacy-impact.md` e `regression-watch.md` gerados pelo `/reversa-coding`

## 11. Histórico de alterações

| Data | Alteração | Autor |
|---|---|---|
| 2026-10-05 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-10-05 | Delta pós-esclarecimento (3ª sessão): D-33, D-34 e D-37 confirmadas (🟢); D-38 Configurações atualizam as paredes de altura cheia; D-39 ímã e pergunta no "Desenhar Paredes" 3D | reversa |
| 2026-10-05 | Delta da 4ª auditoria (fechamento e pé-direito): D-33 ímã no ponto inicial, D-34 fechar pelo teclado/arraste, D-35 rede de segurança no OK, D-36 pé-direito do projeto nas paredes novas, D-37 igualar existentes; premissas visíveis por falta de `/reversa-clarify` | reversa |
| 2026-10-05 | Delta pós-auditoria ao vivo (3ª rodada): D-25 Direção e medida real = interna, D-26 conversão sem Centro, D-27 digitação direta, D-28 linha interna tracejada, D-29 botão direito em todos os modos, D-30 OK/Cancelar com confirmação, D-31 gizmo das portas, D-32 desregistro completo | reversa |
| 2026-10-05 | Delta pós-auditoria e esclarecimentos (2ª rodada): D-20 folha 3D de porta de ambiente, D-21 pergunta dos módulos no OK, D-22 paredes de outra camada (referência + conversão), D-23 rebaixar 150 mm fixo, D-24 "Mobi Editor" para a 003 | reversa |
