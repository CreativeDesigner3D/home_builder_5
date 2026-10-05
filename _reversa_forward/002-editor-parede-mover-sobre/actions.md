# Actions: 002-editor-parede-mover-sobre — editor de paredes 2D, geometria, propriedades por tipo e "Mover Sobre"

> Identificador: `002-editor-parede-mover-sobre`
> Data: `2026-10-05`
> Roadmap: `_reversa_forward/002-editor-parede-mover-sobre/roadmap.md` (D-01 a D-19)
> Data delta: `_reversa_forward/002-editor-parede-mover-sobre/data-delta.md`
> Blocos do roadmap:
> - B1: propriedades e cotas;
> - B2: "Mover Sobre";
> - B3: Editor de Paredes;
> - B4: geometria e operações de parede.
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 90 |
| Paralelizáveis (`[//]`) | 53 |
| Maior cadeia de dependência | 7 (T002 → T018 → T028 → T029 → T030 → T037 → T038); na revisão de 2026-10-05: 5 (T041 → T044 → T016 → T050 → T051) |
| Revisão de 2026-10-05 | T041–T053 (D-20 a D-22) + T016 revista; concluídas |
| Fechamento e pé-direito | T074–T090 (D-33 a D-39); concluídas; maior cadeia 4 (T075 → T082 → T083 → T087) |
| Revisão pós-auditoria ao vivo | T054–T073 (D-25 a D-32); concluídas; maior cadeia 6 (T054 → T063 → T065 → T066 → T067 → T070) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Classificador único de tipo de objeto: dado um objeto, devolve (tipo, raiz, biblioteca) pela precedência de RN-01, para objetos do Home Builder 5 (`IS_*`, `hb_part_role`, `MENU_ID`) e da camada nova (`btm_plane.object_kind`), com a regra de "frente" por biblioteca (D-09, D-16) | - | `[//]` | `blendertomob/selection/classify.py` | 🟢 | `[X]` |
| T002 | Núcleo 2D em Python puro: transformação mundo ↔ tela, pan, zoom, enquadrar tudo, grade, encaixe ortogonal (±2,5°), distância ponto–segmento e ponto–ponto em pixels (D-01) | - | `[//]` | `blendertomob/canvas2d/view.py` | 🟢 | `[X]` |
| T003 | Modelo de paredes em Python puro: nós e trechos; linhas interna, externa e de referência por espessura e orientação; comprimento interno/externo com os cantos; ângulos absoluto e relativo; dividir, unir e inverter; fechamento do contorno; domínio de RN-18 (D-01, D-06, D-07) | - | `[//]` | `blendertomob/walls2d/model.py` | 🟡 | `[X]` |
| T004 | Alinhamento do "Mover Sobre" em Python puro: alvos da vista superior (lados, profundidades 0/30/50/75/100%) e da frontal (lados, alturas 0/30/50/75/100%, empilhar), escolha por tolerância em pixels e deslocamento de A no referencial de B (RN-06, RN-07, RN-08) | - | `[//]` | `blendertomob/move_over/align.py` | 🟡 | `[X]` |
| T005 | Cotas em Python puro: anterior e posterior a partir dos intervalos ocupados da parede, inferior, superior (pé-direito), afastamento, e a operação inversa (cota → nova posição mantendo dimensões) (RN-04, D-11) | - | `[//]` | `blendertomob/measure/cotas.py` | 🟡 | `[X]` |
| T006 | `WindowManager.btm_move_over` (`enabled`, `tolerance_px`) com registro e remoção (data-delta §1) | - | `[//]` | `blendertomob/move_over/props.py` | 🟢 | `[X]` |
| T007 | `WindowManager.btm_wall_editor` (ferramenta, grade, linhas magnéticas, trecho e linha selecionados, campos do trecho com `update` para o rascunho) com registro e remoção (data-delta §1) | - | `[//]` | `blendertomob/walls2d/props.py` | 🟡 | `[X]` |
| T008 | `Object.btm_geometry` (placa/caixa, medidas, espessura, fabricação, componente, matéria-prima, acabamento) com registro e remoção (data-delta §1) | - | `[//]` | `blendertomob/geometry_free/props.py` | 🟢 | `[X]` |
| T041 | Núcleo puro da folha da porta de ambiente: a partir da caixa 2D do símbolo de abertura (local da porta), da largura e de `Is Left`/`Is Double`/`Swing Inside`, devolve os pivôs (posição da dobradiça, lado `L`/`R`, sinal do giro) e o tamanho de cada folha; porta dupla = duas folhas de meia largura (D-20) | - | `[//]` | `blendertomob/inspection/room_door_math.py` | 🟡 | `[X]` |
| T042 | Núcleo puro da conversão: trechos do `btm_wall_segments` (linha de centro, espessura, altura, já no mundo) → cadeias do modelo com orientação `CENTER`, juntando pontas coincidentes (0,01 m) e fechando o contorno quando o fim volta ao início (D-22) | - | `[//]` | `blendertomob/walls2d/convert.py` | 🟡 | `[X]` |
| T054 | Modelo com Direção: `Chain.side` (`LEFT`/`RIGHT`, lado da espessura) no lugar de `orientation`; nós = face interna; `INNER` = linha dos nós, `OUTER` = linha deslocada pela espessura para `side`; `face_length`/`set_length` sobre isso; `outward_side()` para contorno fechado (espessura para fora); `plan_signature(plan)`; sai `CENTER`/`offset_for_orientation` (D-25, D-30) | - | `[//]` | `blendertomob/walls2d/model.py` | 🟡 | `[X]` |
| T055 | Desregistro legado por `cls.is_registered` em vez de `getattr(bpy.types, cls.__name__)`: módulos da raiz e de `operators/` (`walls.py`, `details.py`, `doors_windows.py`, `rooms.py`, `ops_stairs.py`, `scene_navigator.py`, `export.py`, `ops.py`, `hb_assets.py`, `molding/ops.py`) (D-32) | - | `[//]` | `blendertomob/operators/walls.py` | 🟢 | `[X]` |
| T056 | Mesmo ajuste de desregistro nos operadores do frameless (`product_libraries/frameless/operators/*`) (D-32) | - | `[//]` | `blendertomob/product_libraries/frameless/operators/ops_cabinet.py` | 🟢 | `[X]` |
| T057 | Mesmo ajuste de desregistro nos operadores do face frame e do closets (`product_libraries/face_frame/operators/*`, `product_libraries/closets/operators/*`) (D-32) | - | `[//]` | `blendertomob/product_libraries/face_frame/operators/ops_cabinet.py` | 🟢 | `[X]` |
| T074 | Modelo: `Chain.touches_start(ponto, tol)` e `Chain.close_if_touching(tol)` (fecha a cadeia aberta de 3+ trechos cujo fim está a até 10 mm do início, tirando o vértice duplicado) (D-34, D-35) | - | `[//]` | `blendertomob/walls2d/model.py` | 🟢 | `[X]` |
| T075 | Regra pura do pé-direito: `follows_project_height(tipo_btm, WALL_TYPE)` (falso para Mureta, `Half`, `Fake`) e `walls_to_equalize(paredes, pé-direito, tolerância 1 mm)` (D-37, D-38) | - | `[//]` | `blendertomob/walls2d/heights.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Testes `unittest` do núcleo 2D: ida e volta mundo ↔ tela com pan/zoom, enquadrar tudo, encaixe ortogonal a 2° e não a 3°, distâncias em pixels | T002 | `[//]` | `tests/test_canvas2d_view.py` | 🟢 | `[X]` |
| T010 | Testes do modelo de paredes: sala 3.900 × 2.700 externa com 150 mm → internas 3.600 × 2.400; dividir 3.900 em dois que somam 3.900; inverter; fechamento; valores fora de RN-18 recusados | T003 | `[//]` | `tests/test_walls2d_model.py` | 🟢 | `[X]` |
| T011 | Testes do alinhamento: lado direito/esquerdo sem folga, profundidades 0/30/50/75/100%, alturas e empilhamento, clique a 13 px sem efeito, B rotacionado | T004 | `[//]` | `tests/test_move_over_align.py` | 🟢 | `[X]` |
| T012 | Testes das cotas: anterior/posterior com vizinhos e aberturas, filtro vertical, cota anterior 75 mm → posição, módulo livre sem anterior/posterior | T005 | `[//]` | `tests/test_cotas.py` | 🟢 | `[X]` |
| T013 | Testes do classificador com objetos simulados: frente antes de módulo, módulo antes de parede, peça interna resolvida para o módulo, objeto da camada nova | T001 | `[//]` | `tests/test_classify.py` | 🟢 | `[X]` |
| T043 | Testes da folha: as 4 combinações de porta simples (Inside/Outside × Left/Right) e as 2 de porta dupla dão dobradiça no canto certo e giro para o lado do arco; largura e espessura da folha | T041 | - | `tests/test_room_door_math.py` | 🟢 | `[X]` |
| T045 | Testes da conversão: um trecho; cadeia aberta de 3; sala fechada de 4 com trechos fora de ordem; espessura e altura preservadas; ponta a 5 mm junta, a 20 mm não | T042 | - | `tests/test_walls2d_convert.py` | 🟢 | `[X]` |
| T058 | Testes do modelo com Direção: nós = interna; externa = interna + espessuras na sala; `LEFT`/`RIGHT` trocam o lado sem mudar a interna; `outward_side` para contorno horário e anti-horário; assinatura muda ao editar e volta igual ao desfazer a mudança | T054 | - | `tests/test_walls2d_model.py` | 🟢 | `[X]` |
| T059 | Testes da conversão com Direção: linha de centro vira face interna deslocada meia espessura para o interior (fechado) ou para a direita (aberto), com `side` para fora | T060 | - | `tests/test_walls2d_convert.py` | 🟢 | `[X]` |
| T076 | Testes do fechamento: `touches_start` dentro/fora de 10 mm; `close_if_touching` fecha 4 trechos voltando ao início e ignora cadeia de 2 trechos e fim distante | T074 | - | `tests/test_walls2d_model.py` | 🟢 | `[X]` |
| T077 | Testes da regra do pé-direito: Mureta, meia-parede e parede falsa ficam de fora; diferença de 0,5 mm não conta, de 2 mm conta; pé-direito final diferente conta | T075 | - | `tests/test_walls2d_heights.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T014 | Cotas na cena: intervalos ocupados da parede do módulo (`hb_placement.PlacementMixin.get_wall_children_sorted`, vão e filtro vertical), pé-direito (`scene.home_builder.ceiling_height`), leitura e escrita da posição no referencial da parede (D-11) | T001, T005 | `[//]` | `blendertomob/measure/scene_cotas.py` | 🟡 | `[X]` |
| T015 | Leitura e escrita de dimensões por tipo: gabinetes do Home Builder 5 (`Dim X/Y/Z` via `compat`, registrando `btm_overrides`), módulo rápido (`btm_cabinet`), geometria, portas e janelas de ambiente; "Valor Inválido" com faixa (RN-03, D-10) | T001 | `[//]` | `blendertomob/selection/editing.py` | 🟡 | `[X]` |
| T016 | Adaptador de abertura das portas de ambiente, incluído em `inspection.fronts._adapters()`: encontra portas `IS_ENTRY_DOOR_BP` com símbolo `GeoNodeDoorSwing`, `get/apply` giram os pivôs em Z (0–90°), `commit` grava `btm_open`, `hinge_frame` para o controle giratório; porta sem símbolo e janelas ficam de fora (D-20, RF-20; revisto em 2026-10-05 — o levantamento mostrou que não há folha no legado) | T044 | - | `blendertomob/inspection/adapters/room_doors.py` | 🟡 | `[X]` |
| T017 | "Mover Sobre" na cena: raízes de A e B pelo classificador, caixas de A e B no referencial de B, regra de frente por biblioteca, parede como B, aplicar deslocamento e rotação de B, guardar e restaurar a posição original (D-16) | T001, T004 | `[//]` | `blendertomob/move_over/scene.py` | 🟡 | `[X]` |
| T018 | Desenho 2D sobre o núcleo: contornos, linhas tracejadas/sólidas, marcas de alvo, textos com unidade do usuário, botões e campos com área de clique (sobre `hb_gpu_draw.py`) | T002 | `[//]` | `blendertomob/canvas2d/draw.py` | 🟢 | `[X]` |
| T019 | Ler as paredes do ambiente do Home Builder 5 para o modelo: cadeia por `GeoNodeWall.get_connected_wall` (com vizinho geométrico), posição, rotação, `Length`, `Thickness`, `Height`, `End Height`, `btm_wall_type`/`btm_wall_orientation`; confirmar o lado da espessura (premissa de D-06) | T003 | `[//]` | `blendertomob/walls2d/scene_io.py` | 🟡 | `[X]` |
| T020 | Aplicar o rascunho: atualizar paredes existentes, criar trechos pelo caminho do construtor (`operators/walls.py` `create_wall`, `connect_to_wall`), remover excluídos, recalcular esquadrias e piso/teto ligados, listar itens que não cabem (RF-10); um passo de desfazer (D-04) | T019 | - | `blendertomob/walls2d/apply.py` | 🟡 | `[X]` |
| T021 | Malha da placa e da caixa por BMesh, criada e atualizada a partir de `btm_geometry` (D-18) | T008 | `[//]` | `blendertomob/geometry_free/mesh.py` | 🟢 | `[X]` |
| T022 | Geometria de fabricação na lista de peças: adaptador com origem `FREE_GEOMETRY` (placa = 1 peça; caixa = 6 placas na espessura) incluído na extração (data-delta §5) | T008 | `[//]` | `blendertomob/cutting/part_sources.py` | 🟢 | `[X]` |
| T044 | Folha 3D na cena: cria (no primeiro uso) ou atualiza pivôs (Empty, `btm_room_door_pivot`) e folhas (BMesh, `btm_room_door_leaf`) filhos da porta, com tamanho de `Dim X/Z` da gaiola e `Door Thickness`, lado pela caixa avaliada do `GeoNodeDoorSwing` via T041 (D-20, M-09) | T041 | - | `blendertomob/inspection/room_door_leaf.py` | 🟡 | `[X]` |
| T046 | Módulos de trecho apagado: `Session.remove_modules` (padrão Falso), `apply.modules_of_removed(plan)` (filhos que não são `obj_x`, cotas, portas ou janelas) e `apply_plan(..., remove_modules)` repassando a `ops_wall_extras.remove_wall` (D-21) | - | `[//]` | `blendertomob/walls2d/apply.py` | 🟢 | `[X]` |
| T047 | Conversão na cena: lê `btm_wall_segments` dos objetos da camada nova selecionados (JSON → mundo por `matrix_world`), monta as cadeias por T042, guarda os objetos em `plan.converted_sources`; no OK, `apply_plan` remove esses objetos; objeto sem JSON fica como referência com aviso (D-22, M-10) | T042 | - | `blendertomob/walls2d/scene_io.py` | 🟡 | `[X]` |
| T060 | Conversão sem Centro: deslocar a linha de centro meia espessura até a face interna e definir `side` (D-26) | T054 | - | `blendertomob/walls2d/convert.py` | 🟢 | `[X]` |
| T061 | Aplicador com Direção: cadeia `side == 'RIGHT'` aplicada com nós e trechos em ordem inversa; parede existente que muda de sentido mantém os filhos na posição do mundo; deixa de gravar `btm_wall_orientation` (D-25, M-11) | T054 | - | `blendertomob/walls2d/apply.py` | 🟡 | `[X]` |
| T062 | Leitura com Direção: paredes da cena entram com `side = 'LEFT'`, ignorando `btm_wall_orientation`; `convert_into` usa a conversão nova (D-25, D-26, M-11) | T054, T060 | - | `blendertomob/walls2d/scene_io.py` | 🟢 | `[X]` |
| T063 | Estado do editor: campo virtual **Direção** (Direita/Esquerda) sobre `side` da cadeia, com aviso quando o trecho tem filhos; `new_direction` do lápis; `Session.typed` para a digitação direta e `Session.signature` gravada na abertura (D-25, D-27, D-30) | T054 | - | `blendertomob/walls2d/props.py` | 🟡 | `[X]` |
| T064 | Gizmo: a seta só lê/escreve `travel()` de frentes não articuladas; portas (ambiente e Módulo Rápido) devolvem 0 (D-31) | - | `[//]` | `blendertomob/inspection/gizmo.py` | 🟢 | `[X]` |
| T078 | Ímã no ponto inicial do lápis: com 2+ trechos e o cursor a até 15 px do início, a pré-visualização gruda nele, o ponto ganha anel de destaque e o rótulo "Fechar"; o clique abre a pergunta de fechamento (D-33) | T074 | - | `blendertomob/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T079 | Pergunta de fechamento pelo teclado e pelo arraste: trecho digitado (Enter) ou vértice arrastado que termina a até 10 mm do início tira o vértice duplicado e abre a pergunta; Sim fecha com a Direção para fora, Não mantém aberto (D-34) | T078 | - | `blendertomob/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T080 | Rede de segurança no OK: `apply_plan` fecha as cadeias abertas com fim no início (`close_if_touching`, Direção para fora se nova) antes de criar as paredes e informa quantas fechou (D-35, M-12) | T074 | - | `blendertomob/walls2d/apply.py` | 🟢 | `[X]` |
| T081 | Pé-direito do projeto nas paredes novas: ao abrir o editor, `new_height` = `measure/scene_cotas.ceiling_height` (cena principal); a sessão guarda o valor lido (D-36) | - | `[//]` | `blendertomob/walls2d/props.py` | 🟢 | `[X]` |
| T082 | Igualar existentes no OK (dados e aplicador): `Session.equalize_height` (padrão verdadeiro) e lista das paredes a igualar (T075); `apply_plan(..., project_height)` grava `Height`/`End Height` quando marcado (D-37, M-13) | T075, T081 | - | `blendertomob/walls2d/apply.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T023 | Painel `BTM_PT_ObjectProperties` com grupos por tipo (Dimensões, Cotas, Abrir, Parede com botão do editor, Outras, Ações via `UILayout.menu_contents(MENU_ID)`) e linha de estado no topo; retirar `BTM_PT_ContextProperties` do registro (D-10, M-08) | T001, T014, T015, T016 | `[//]` | `blendertomob/ui/object_properties.py` | 🟢 | `[X]` |
| T024 | Cotas desenhadas ao selecionar um módulo (`POST_PIXEL`, mesmo visual de `hb_placement.draw_placement_dimensions`), com remoção no `unregister()` (D-12) | T014 | `[//]` | `blendertomob/overlays/selection_cotas.py` | 🟡 | `[X]` |
| T025 | Modo "Mover Sobre": `btm.move_over_toggle`; item de keymap em "3D View" (`RIGHTMOUSE` `PRESS`, `head=True`) para `btm.move_over_drag`, cujo `poll` exige modo ligado e objeto movível sob o cursor; modal de arraste com linha elástica e destaque, que abre o diálogo ao soltar sobre B ou cancela (D-14, RN-05, RN-10) | T006, T017 | `[//]` | `blendertomob/move_over/ops_drag.py` | 🟢 | `[X]` |
| T026 | Diálogo `btm.move_over_dialog`: painel sobre a viewport com as telas superior e frontal só com A e B, alvos com destaque, prévia no 3D, campos digitáveis (Tab), Confirmar/Cancelar (Enter/Esc), aviso de sobreposição; `UNDO` ao confirmar (D-15, RN-09, RN-11) | T018, T025 | `[//]` | `blendertomob/move_over/ops_dialog.py` | 🟡 | `[X]` |
| T027 | Botão "Mover Sobre" no HUD (`_ModalToggleButton`, visível em todas as linhas) e no painel, com estado ligado/desligado | T025 | `[//]` | `blendertomob/operators/viewport_hud.py` | 🟢 | `[X]` |
| T028 | Abrir e fechar a janela do Editor de Paredes: `wm.window_new`, área convertida para Image Editor e marcada como editor, handler de desenho da planta, fechamento no OK/Cancelar; alternativa numa área da janela atual (D-02) | T018, T007 | `[//]` | `blendertomob/walls2d/window.py` | 🟡 | `[X]` |
| T029 | Modal `btm.wall_editor`: Selecionar/Mover (arrastar vértice com prévia, escolher linha interna/externa), Construir Parede a lápis (digitação direta, Enter, trava ortogonal, pergunta de fechamento), Adicionar/Remover Vértice, Inverter Sentido, pan e zoom (RN-15, RN-17) | T028, T003 | - | `blendertomob/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T030 | Painéis da região lateral do editor: "Painel" (campos do trecho, bloquear ângulo, arco desabilitado com aviso), "Grid" (tamanho, linhas magnéticas) e OK/Cancelar (`btm.wall_editor_ok` com aviso de itens, `btm.wall_editor_cancel`) (RF-05, RF-08, RF-09, RF-10, D-07) | T029, T020 | - | `blendertomob/walls2d/panels.py` | 🟡 | `[X]` |
| T031 | Entradas do editor: "Editar Paredes…" no menu do botão direito da parede (`HOME_BUILDER_MT_wall_commands`) e botão na aba Construtor (RF-01) | T028 | `[//]` | `blendertomob/ui/menus.py` | 🟢 | `[X]` |
| T032 | `btm.geometry_create`: placa ou caixa por pontos de referência (`hb_snap`, seletor de pontos de `DimensionOperatorMixin`), pré-visualização, medidas digitadas, Esc sem criar (RF-11) | T021 | `[//]` | `blendertomob/geometry_free/ops_create.py` | 🟡 | `[X]` |
| T033 | Edição de geometria: dimensões, cotas e material pela janela de propriedades; duplicar, espelhar e excluir com desfazer (RF-12, RF-15) | T021, T023 | `[//]` | `blendertomob/geometry_free/ops_edit.py` | 🟡 | `[X]` |
| T034 | `btm.wall_remove`: diálogo Segmento / Tudo / Manter o selecionado e "Remover módulos que estão na parede", sobre a exclusão existente (RF-35, D-19) | - | `[//]` | `blendertomob/operators/ops_wall_extras.py` | 🟡 | `[X]` |
| T035 | Rebaixar parede (esconde a parede e mostra filha de 150 mm, `btm_wall_lowered`, desfazer o rebaixamento) e invisível (contorno, com opção de esconder o contorno) (RF-36, RF-37, D-19) | T034 | - | `blendertomob/operators/ops_wall_extras.py` | 🟡 | `[X]` |
| T036 | `btm.move_on_wall`: arrastar o módulo só no plano da sua parede, com cotas ao vivo e `PlacementMixin.avoid_overlap` (RF-34, D-17) | T014 | `[//]` | `blendertomob/move_over/ops_move_on_wall.py` | 🟡 | `[X]` |
| T037 | Registrar os pacotes novos no add-on (seleção/propriedades, cotas, "Mover Sobre" com keymap, editor de paredes, geometria, operações de parede) com `unregister()` simétrico: keymaps, handlers, janelas abertas | T023, T024, T025, T026, T027, T030, T031, T032, T033, T035, T036 | - | `blendertomob/__init__.py` | 🟢 | `[X]` |
| T048 | Painel "Confirmar" do editor: com módulos em trechos apagados, lista os módulos e mostra a caixa "Remover os módulos junto?"; o OK pede o segundo clique (fluxo `confirm_pending`) e passa a escolha ao aplicador (D-21, RF-10) | T046 | - | `blendertomob/walls2d/panels.py` | 🟢 | `[X]` |
| T049 | `btm.wall_editor.invoke`: com paredes da camada nova selecionadas, diálogo "Converter para paredes editáveis" / "Só referência" antes de abrir a janela; "Converter" chama T047 (D-22, RF-38) | T047 | - | `blendertomob/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T050 | Janela de propriedades: grupo "Abrir" para portas de ambiente (abrir/fechar, 45°/90°) pelo adaptador da T016, no lugar do aviso "sem folha 3D"; janelas continuam sem "Abrir" (D-20, RF-20) | T016 | - | `blendertomob/ui/object_properties.py` | 🟢 | `[X]` |
| T065 | Desenho da planta: face interna tracejada, externa contínua; rótulo mostra a medida interna; digitação em andamento junto do cursor (D-28, D-27) | T063 | - | `blendertomob/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T066 | Digitação direta na ferramenta Selecionar/Mover: clicar num vértice sem arrastar o seleciona; dígitos/Backspace/Enter aplicam a medida na face (interna ou externa) ou no trecho que termina no vértice; Esc limpa a digitação (D-27, RF-39) | T065 | - | `blendertomob/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T067 | Fechamento e cancelamento: ao fechar o contorno, `side = outward_side()`; Esc e o botão Cancelar com rascunho alterado pedem confirmação (pergunta desenhada na planta / `invoke_confirm`) (D-25, D-30, RF-09) | T066, T061 | - | `blendertomob/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T068 | Painéis do editor com `bl_order` (OK/Cancelar no fim), campo Direção no lugar de Orientação e no grupo "Novas paredes" (D-30, D-25) | T063 | - | `blendertomob/walls2d/panels.py` | 🟢 | `[X]` |
| T069 | Atalho do "Mover Sobre" também em cada mapa de modo da viewport cujo botão direito abre menu de contexto (descobertos no `keyconfigs.default`), com remoção no `unregister()` (D-29, RF-27) | - | `[//]` | `blendertomob/move_over/ops_drag.py` | 🟡 | `[X]` |
| T083 | Painel Confirmar: lista das paredes com outra altura e a caixa "Igualar ao pé-direito do projeto" (marcada), no mesmo fluxo do segundo clique do OK (D-37, RF-42) | T082 | - | `blendertomob/walls2d/panels.py` | 🟢 | `[X]` |
| T084 | Configurações atualizam as paredes: `update_ceiling_height` grava `Height`/`End Height` nas paredes de altura cheia de todas as cenas (regra T075), recalcula esquadrias e refaz pisos/tetos (D-38, RF-43, M-14) | T075 | - | `blendertomob/hb_props.py` | 🟢 | `[X]` |
| T085 | "Desenhar Paredes" 3D: ímã de 15 px de tela no lugar dos 0,15 m e estado `pending_close` (pergunta no cabeçalho e no 3D) antes do `close_room`; Enter/clique = Sim, Esc = Não (D-39, RF-44) | - | `[//]` | `blendertomob/operators/walls.py` | 🟡 | `[X]` |
| T086 | "Desenhar Paredes" 3D: comprimento digitado que termina a até 10 mm do início entra em `pending_close` em vez de só confirmar a parede (D-39) | T085 | - | `blendertomob/operators/walls.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T038 | Strings novas pt-BR → en (editor de paredes, "Mover Sobre", propriedades, geometria, operações de parede) | T037 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |
| T039 | Guia curto do usuário: editor de paredes, propriedades e cotas, "Mover Sobre", geometria, remover/rebaixar/invisível | T037 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T040 | Teste de fumaça no Blender: classificador e cotas editáveis em gabinetes de cada biblioteca; alinhar e cancelar no "Mover Sobre" pela camada de cena; aplicar rascunho numa sala de 4 paredes (editar, dividir, cancelar); geometria na lista de peças; registro/desregistro 2× sem resíduo | T037 | `[//]` | `tests/blender_002_smoke.py` | 🟢 | `[X]` |
| T051 | Fumaça da revisão: porta de ambiente nas 6 combinações abre para o lado do símbolo, fecha e salva fechada; OK com trecho apagado deixa o módulo solto (padrão) ou o remove (marcado); conversão de paredes da camada nova (aberta e fechada) gera paredes do Home Builder 5 no lugar e remove o original | T016, T048, T049, T050 | - | `tests/blender_002_smoke.py` | 🟢 | `[X]` |
| T052 | Guia do usuário: abrir porta de ambiente, pergunta dos módulos no OK, conversão de paredes de outra camada | T048, T049, T050 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T053 | Strings novas pt-BR → en (Abrir porta de ambiente, "Remover os módulos junto?", "Converter para paredes editáveis", "Só referência") | T048, T049, T050 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |
| T070 | Fumaça: salas horária e anti-horária com espessura para fora e balcão/porta "para dentro"; trocar Direção mantém a interna; digitação direta; Cancelar com alterações pede confirmação; nenhum operador do pacote sobra após `unregister()` (verificação por `bl_idname`); seta do gizmo com porta devolve 0 | T055, T056, T057, T061, T062, T064, T066, T067 | - | `tests/blender_002_smoke.py` | 🟢 | `[X]` |
| T071 | Teste de interface com eventos simulados (`--enable-event-simulate`): botão direito do "Mover Sobre" abre a janela em Modo Objeto e em Edição; troca de ferramenta, lápis com digitação e OK/Cancelar pelo painel do editor | T067, T068, T069 | - | `tests/blender_002_ui_events.py` | 🟡 | `[X]` |
| T072 | Guia do usuário: medida real = interna (tracejada), Direção, digitação na face/vértice, confirmação do Cancelar, botão direito em todos os modos | T067, T068, T069 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T073 | Strings novas pt-BR → en (Direção, Direita/Esquerda, confirmação de descarte, avisos de digitação) | T067, T068 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |
| T087 | Fumaça do fechamento e do pé-direito: lápis voltando ao início pelo teclado pergunta e fecha; ímã a 10 px e não a 20 px; OK fecha cadeia com fim no início; paredes novas com o pé-direito do projeto; igualar existentes marcado/desmarcado; mudar as Configurações atualiza só as de altura cheia | T079, T080, T081, T083, T084 | - | `tests/blender_002_smoke.py` | 🟢 | `[X]` |
| T088 | Teste com eventos simulados: ímã e pergunta no editor (clique e teclado) e no "Desenhar Paredes" 3D (Enter fecha, Esc continua) | T079, T086 | - | `tests/blender_002_ui_events.py` | 🟡 | `[X]` |
| T089 | Guia do usuário: ímã e pergunta de fechamento (editor e 3D), pé-direito do projeto, igualar existentes, Configurações atualizam as paredes | T079, T083, T084, T086 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |
| T090 | Strings novas pt-BR → en (Fechar, Deseja fechar a parede?, Igualar ao pé-direito do projeto, mensagens do 3D) | T079, T083, T086 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
-->

Rodada de 2026-10-05 (`/reversa-coding` "principais ações começando da de maior impacto"): blocos **B1** (propriedades
por tipo e cotas) e **B2** ("Mover Sobre") com as dependências — 18 ações. Ficam para as próximas rodadas o B3
(Editor de Paredes: T003, T007, T010, T019, T020, T028–T031), o B4 (geometria e operações de parede: T008, T021, T022,
T032–T035), T016, T036 e o fechamento (T037–T040).

- **T023 sem a T016:** a janela de propriedades mostra "Abrir" para frentes e módulos; para portas e janelas de
  ambiente só depois da T016 (🔴).
- **Campos editáveis = propriedades virtuais da cena** (`Scene.btm_selection`, com `get`/`set`): a cena tem desfazer,
  então cada edição é um passo de Ctrl+Z; valor inválido não é aplicado e aparece no painel.
- **`BTM_PT_ContextProperties` removido** (substituído por `BTM_PT_ObjectProperties`, M-08); o botão "Remover Abertura"
  das aberturas do módulo rápido foi mantido no painel novo.
- **"Mover Sobre" — escolha além do plano:** se B está numa parede, A passa a ser filho dessa parede (mantendo a
  posição no mundo) para as cotas continuarem valendo; Cancelar restaura pai e posição.
- **Botão direito com o modo ligado:** sem objeto movível sob o cursor, o operador consome o clique (o menu não abre,
  RN-10). Modo desligado: o `poll` falha e o evento segue para o menu do Blender.
- **Registro:** `move_over` entrou no `__init__.py` do add-on; o painel e o overlay de cotas entram por `ui` e
  `overlays`. A T037 (registro de todos os pacotes) fica aberta até o B3/B4.
- **Não exercitado de forma interativa:** a janela "Mover Sobre", o arraste com o botão direito, o painel e as cotas
  ao selecionar dependem de janela (testes em `--background`); a lógica e as camadas de cena foram testadas.
- Verificação: `ruff` OK; `check_api.py` OK; testes `unittest` OK (novos: `test_canvas2d_view`, `test_move_over_align`,
  `test_cotas`, `test_classify`); fumaças `blender_smoke`, `increment1`, `legacy` e `inspection` OK; teste de
  integração (scratch): cotas e "Valor Inválido" na cena, dimensões nas bibliotecas, alinhamento lado + profundidade +
  empilhar entre face frame e frameless com restauração, campos virtuais, atalho registrado e removido sem resíduo.

Rodada de 2026-10-05 (`/reversa-coding` "Editor de Paredes, a geometria com remover, rebaixar e invisível, a T016 e o
fechamento"): B3, B4, T036 e o fechamento — 21 ações concluídas; **T016 bloqueada** (fica `[ ]`).

- **T016 bloqueada (🔴 confirmado):** as portas e janelas de ambiente do Home Builder 5 são só a gaiola de recorte
  (`GeoNodeCage` com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP`) e o símbolo 2D `GeoNodeDoorSwing` (inputs `Is Double`,
  `Is Left`, `Swing Inside`, `Door Thickness`; sem ângulo). As aberturas da camada nova (`btm_opening`) também são só o
  recorte. Não há folha 3D para girar, então não foi criado adaptador. O painel mostra o aviso "Porta de ambiente sem
  folha 3D". RF-20 depende de decisão do titular: modelar uma folha 3D para as portas de ambiente (escopo novo).
- **Editor de Paredes — janela:** `screen.area_dupli` cria a janela nova e a área vira Image Editor sem imagem; sem
  janela nova, o editor ocupa a área atual e devolve o tipo ao fechar. A janela é fechada por um timer depois que o
  modal termina (fechar a janela dentro do próprio modal não é seguro).
- **Correção durante o teste:** a resposta "Sim" ao fechar o contorno acrescentava o nó sem o trecho de fechamento;
  corrigido (`_append` + `Chain.close`).
- **Desvios registrados:** (1) módulos de um trecho removido no editor ficam soltos na mesma posição (a remoção junto
  é opção do "Remover Parede…"); (2) orientação editável só em paredes novas; (3) piso e teto ligados **não** são
  regenerados no OK (o recálculo cobre as esquadrias); (4) um desenho novo não se liga a cadeias existentes, mesmo
  começando num vértice delas (só copia a posição).
- **Remoção de parede unificada:** `operators/ops_wall_extras.remove_wall` serve ao "Remover Parede…" e ao OK do editor;
  além do que a exclusão legada faz, solta os módulos (mantendo `matrix_world`) e apaga portas, janelas e cotas.
  O `home_builder_walls.delete_wall` legado não foi alterado e continua no menu.
- **Rebaixar:** a parede fica com `hide_viewport` e uma filha `<parede>_Rebaixada` (malha 150 mm, mesmo material,
  `btm_lowered_proxy`); a filha não acompanha esquadria (ponta reta). **Invisível:** `display_type = 'WIRE'`, guarda o
  tipo anterior em `btm_display_prev`; "Esconder contorno" usa `hide_set` (Alt+H mostra de novo).
- **Geometria livre:** origem no canto mínimo; placa com "Posição da Placa" (deitada, em pé de frente, em pé de lado)
  para escolher o eixo da espessura; caixa = fundo/tampo inteiros, laterais entre eles, frente/trás entre as laterais.
  As peças têm linha vazia para valer a matéria-prima digitada (sem fitas e sem limite de chapa do padrão).
  Espelhar = passa a peça para o outro lado do ponto de origem (X local), sem escala negativa.
- **Criação por pontos:** usa `hb_snap.main` (Ctrl encaixa em vértices/arestas, como no legado), não o seletor de
  pontos do `DimensionOperatorMixin` previsto no D-18.
- **"Mover na Parede" (T036):** movimento em X ao longo da parede; com Shift, em Z. A parada no vizinho é
  `measure/cotas.slide` (testada); as cotas ao vivo vêm do overlay de seleção e do cabeçalho.
- **Não exercitado de forma interativa:** a janela do editor (desenho real com mouse), os painéis da região lateral, a
  criação por pontos e o "Mover na Parede" com mouse. A lógica do modal do editor foi exercitada com eventos simulados
  e o deslizar com a função de movimento real na fumaça.
- Verificação: `ruff` OK; `check_api.py` OK; `unittest` 93 testes OK (novo: deslizar em `test_cotas`); fumaças
  `blender_smoke`, `increment1`, `legacy`, `inspection` e a nova `blender_002_smoke` OK; `build.py` + `extension
  validate` OK com os pacotes novos no zip.

Correções de 2026-10-05 após `/reversa-audit` (achados em `audit/cross-check.md`):

- **A001 (T029):** o modal do editor consumia cliques e teclas do painel lateral (região UI sobreposta à planta, padrão
  do Blender) — ferramentas, campos, OK e Cancelar não respondiam. Agora os eventos sobre o painel passam e a vista da
  planta usa só a largura visível (`window.over_side_panel`, `window.visible_width`).
- **A013 (T030):** a janela do editor esconde os menus e as ferramentas do Image Editor.
- **A004 (T019, D-05):** paredes da camada nova (`btm.wall_builder`) aparecem tracejadas na planta, só como referência.
- **A005 (T020):** o OK refaz a malha de pisos e tetos existentes com o contorno novo; o desvio "piso/teto não
  regenerados" deixa de valer. Pisos/tetos sem sala fechada correspondente ficam como estão.
- **A002 (fora da 002, UI legada):** o Gerenciador de Ambientes chamava `home_builder.*_room`, inexistentes; trocado para
  `blendertomob.*_room`. A fumaça passou a verificar todos os operadores citados na interface.
- **Pendentes de decisão do titular:** A006 (RF-20, portas de ambiente sem folha 3D) e A003 ("Mobi Editor" + botões
  flutuantes, escopo novo).
- Verificação: ruff, `check_api.py`, `unittest` e as 5 fumaças OK. Ao vivo (Blender MCP): o build novo instalou e o
  editor abriu com o código novo; o teste do clique no painel ao vivo não terminou (o Blender foi encerrado por um
  `SystemExit` do script de teste), ficando coberto pela fumaça com regiões simuladas.

Rodada de 2026-10-05 (`/reversa-coding` da revisão): T041–T053 e T016 — 14 ações concluídas, nenhuma falha.

- **Porta de ambiente (D-20):** lado da dobradiça e sentido saem dos inputs do símbolo (`Is Left`, `Is Double`,
  `Swing Inside`), conferidos contra o símbolo medido no Blender (pontas do arco a 90°, nas 6 combinações); a caixa
  avaliada não é lida em tempo de uso (mais simples e determinístico que o previsto no D-20). A folha só nasce no
  primeiro "Abrir"; `Front.can_sweep()` evita que a verificação de interferência crie folhas; `module_root_of` passou a
  reconhecer a porta (`IS_ENTRY_DOOR_BP`), para "abrir selecionado" e a janela de propriedades.
- **Módulos no OK (D-21):** `modules_of_removed` lista só módulos/itens soltos (portas, janelas e cotas saem com a
  parede); `items_that_do_not_fit` deixou de listar os filhos de paredes removidas (agora é a lista de módulos).
- **Conversão (D-22):** o `offset` (base Z) do `btm_wall_segments` é ignorado — as paredes convertidas nascem no piso.
  Cancelar o diálogo de conversão cancela a abertura do editor.
- **Bug corrigido (achado pela fumaça):** `Chain.offset_for_orientation` deslocava os cantos por `1/(2·cos(θ/2))`
  em vez de `1/(2·cos²(θ/2))` — paredes novas com orientação Centro/Esquerda saíam ~30% deslocadas nos cantos.
- Verificação: `ruff`, `check_api.py`, `unittest` 103 OK (novos: `test_room_door_math`, `test_walls2d_convert`, canto
  em `test_walls2d_model`), 5 fumaças OK, `build.py` + `extension validate` OK. Não exercitado com mouse: o diálogo de
  conversão e a caixa de módulos no painel (desenho de UI em janela).

Rodada de 2026-10-05 (`/reversa-coding` pós-auditoria ao vivo): T054–T073 — 20 ações concluídas, nenhuma falha.

- **Direção e medida real (D-25):** os nós passam a ser a face interna; `Chain.side` diz o lado da espessura; o OK
  inverte a cadeia quando `side = 'RIGHT'` (o Home Builder só põe a espessura à esquerda). Sala fechada pelo lápis
  ganha `side` para fora. Medido na fumaça: salas horária e anti-horária ficam com a parede fora do interior e o lado
  −Y (frente dos módulos) para dentro. Trocar a Direção de paredes existentes mantém a interna e os itens no lugar.
- **Limitação registrada:** salas **legadas** desenhadas no anti-horário (espessura para dentro) são lidas como estão,
  sem inverter paredes num OK sem edição; nelas a linha dos nós é a externa. Trocar a Direção corrige.
- **Desregistro (D-32):** o padrão `getattr(bpy.types, cls.__name__)` estava em 46 arquivos (operadores, menus,
  propriedades, painéis), não só nos 33 de operadores: 91 trocas + `hb_assets.py`. Antes: 280 operadores sobravam;
  agora 0 (2 ciclos), nenhuma classe sobra; ao vivo, reinstalar a extensão passou de 280 avisos para 0.
- **Painel do editor (D-30) — achados pelo print da tela na instância de teste:** (1) com `HIDE_HEADER` o Blender
  ignora `bl_order` e o Confirmar ficava no topo — o painel ganhou cabeçalho "Confirmar"; (2) a região lateral podia
  abrir na aba "Tool" do Image Editor — o modal ativa a aba "Editor de Paredes" quando ela existe; (3) o cabeçalho
  View/New/Open do Image Editor foi escondido.
- **Botão direito (D-29):** atalho também em 19 mapas de modo da viewport (lista fixa; em background o teclado padrão
  vem sem itens). Teste com cliques reais: abre a janela em Modo Objeto e em Edição.
- **Teste de interface (T071):** `tests/blender_002_ui_events.py` roda numa instância própria com
  `--enable-event-simulate` (10 verificações: botão direito, ferramentas pelo painel, ordem do painel, lápis, fechamento
  com espessura para fora, OK, Esc com pergunta, Não/Sim). Dois cuidados do próprio teste: o Blender ativa o botão no
  movimento do mouse e só depois recebe o clique (o toque espera um ciclo); o 1º botão direito da sessão simulada se
  perde (aquecimento).
- Verificação: `ruff`, `check_api.py`, `unittest` 105 OK, 5 fumaças OK, teste de interface OK, `build.py` +
  `extension validate` OK; extensão atualizada no Blender do titular (MCP).

Rodada de 2026-10-05 (`/reversa-coding` fechamento e pé-direito): T074–T090 — 17 ações concluídas, nenhuma falha.

- **Fechar a sala (D-33 a D-35):** ímã de 15 px no ponto inicial (anel + "Fechar") no clique e no arraste do último
  vértice; chegar ao início pelo teclado ou pelo arraste pergunta "Deseja fechar a parede?" — "Não" mantém o trecho
  digitado; no OK, contorno aberto com o fim no início é fechado (rede de segurança) e o relatório informa.
- **Pé-direito (D-36 a D-38):** paredes novas com o pé-direito do projeto (`scene_cotas.ceiling_height`); no OK,
  lista + "Igualar ao pé-direito do projeto" (marcada); mudar o pé-direito nas Configurações atualiza todas as paredes
  de altura cheia (fora Mureta, `Half`, `Fake`) pelo callback legado `update_ceiling_height`. Limitação: piso e teto
  são refeitos só na cena atual.
- **"Desenhar Paredes" 3D (D-39):** ímã de 15 px de tela (0,15 m se a vista não projetar); clique com ímã ou medida
  digitada que termina no início entra em `pending_close` (pergunta no cabeçalho e junto do ponto); Enter/clique fecham
  com o `close_room` existente; Esc continua. A tecla C continua fechando direto.
- Verificação: `ruff`, `check_api.py`, `unittest` 108 OK, 5 fumaças OK, teste de interface 13/13 OK (inclui o 3D),
  `build.py` + `extension validate` OK; extensão atualizada no Blender do titular (0 avisos de registro).

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-05 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-05 | Rodada 2 de `/reversa-coding`: 21 ações concluídas, T016 bloqueada | reversa |
| 2026-10-05 | Correções A001, A002, A004, A005, A013 da auditoria | reversa |
| 2026-10-05 | `/reversa-to-do` da revisão: T041–T053 (D-20 folha da porta, D-21 módulos no OK, D-22 conversão) e T016 revista | reversa |
| 2026-10-05 | `/reversa-coding` da revisão: 14 ações concluídas; feature sem ações abertas | reversa |
| 2026-10-05 | `/reversa-to-do` pós-auditoria ao vivo: T054–T073 (D-25 a D-32) | reversa |
| 2026-10-05 | `/reversa-coding` pós-auditoria ao vivo: 20 ações concluídas; feature sem ações abertas | reversa |
| 2026-10-05 | `/reversa-to-do` fechamento e pé-direito: T074–T090 (D-33 a D-39) | reversa |
| 2026-10-05 | `/reversa-coding` fechamento e pé-direito: 17 ações concluídas; feature sem ações abertas | reversa |
