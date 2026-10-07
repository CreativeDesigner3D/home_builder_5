# Actions: Módulos personalizáveis, agregados e Mover Sobre ampliado

> Identificador: `003-modulos-agregados-reposicionar`
> Data: `2026-10-07`
> Roadmap: `_reversa_forward/003-modulos-agregados-reposicionar/roadmap.md` (D-01 a D-27)
> Data delta: `_reversa_forward/003-modulos-agregados-reposicionar/data-delta.md`
> Interfaces: `interfaces/cut-plan-json.md`, `interfaces/user-module-file.md`
> Incrementos: I1 núcleo + frameless; I2 face frame, closets, `btm`; I3 agregados; I4 folha de porta; I5 Mover Sobre ampliado.
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 71 |
| Paralelizáveis (`[//]`) | 32 |
| Maior cadeia de dependência | 13 (T001 → T019 → T020 → T021 → T022 → T023 → T025 → T026 → T028 → T029 → T064 → T068 → T071) |
| Ordem de entrega | I1 → I2 → I3 → I4 → I5; I5 (Should/Could) pode ser cortado sem afetar I1..I4 |

## Fase 1, Preparação

Núcleos puros, propriedades e pacotes.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Núcleo puro da personalização: estrutura `spec` por instância (vãos com frente, estilo de porta/gaveta, modelo e posição do puxador, material de frente, interior com prateleiras/divisórias/gavetas/alturas; materiais por peça e por grupo CAIXA/FRENTES/FUNDO/INTERNO), validação (estilos e materiais por nome, RN-06) e serialização para dict (D-01) | - | `[//]` | `caffmob_draw/customize/spec.py` | 🟢 | `[X]` |
| T002 | Núcleo puro do manifesto do módulo salvo: montar, validar (`format`, `schema_version` 1.x, `library`) e ler o `<nome>.json`; nome de arquivo sanitizado preservando o nome original (`interfaces/user-module-file.md`, D-10) | T001 | - | `caffmob_draw/customize/manifest.py` | 🟡 | `[X]` |
| T003 | Núcleo puro dos limites do agregado: referencial da face do pai (±X/±Y/±Z) a partir das caixas locais, clamp de `u`/`v` para a caixa do agregado não sair do contorno, faixa de `offset` de −espessura do pai a +∞, matriz final do agregado (RN-08, RN-09, D-12) | - | `[//]` | `caffmob_draw/aggregates/limits.py` | 🟢 | `[X]` |
| T004 | Núcleo puro da varredura de abertura: do valor atual ao pedido em passos (2° no giro, 1 cm no correr), bissecção até 0,25° / 1 mm no primeiro contato, usando uma função de teste injetada; fechar não testa; devolve valor alcançado e índice do contato (RN-11a, D-19) | - | `[//]` | `caffmob_draw/aggregates/sweep.py` | 🟡 | `[X]` |
| T005 | Núcleo puro do reposicionamento: rotação em graus em torno do centro da base de A no referencial de B, passo do teclado, conversão relativa ↔ absoluta (só exibição), posição salva como delta + rotação + lado de B e reaplicação a outro par (RF-22..RF-26, D-21, D-22) | - | `[//]` | `caffmob_draw/move_over/reposition.py` | 🟢 | `[X]` |
| T006 | `pivot_math.clamp_angle(degrees, maximum=MAX_ANGLE)` e `pose_for` aceitando o máximo da folha; comportamento padrão de 90° preservado para os módulos (D-18) | - | `[//]` | `caffmob_draw/inspection/pivot_math.py` | 🟢 | `[X]` |
| T007 | `Object.btm_custom` (`BTM_PG_CustomSpec`: `door_style`, `drawer_style`, `pull_model`, `pull_position`, `pull_all_fronts`, `front_material`, `material`, `group_materials`, `interior_heights`) com registro e remoção (data-delta §1) | - | `[//]` | `caffmob_draw/customize/props.py` | 🟢 | `[X]` |
| T008 | `Object.btm_aggregate` (`BTM_PG_Aggregate`, todos os campos do data-delta §1) com `update` de `u`/`v`/`offset` passando por `aggregates/limits.py`, registro e remoção | T003 | - | `caffmob_draw/aggregates/props.py` | 🟢 | `[X]` |
| T009 | `btm_move_over` ganha `step` e `show_relative`; `Scene.btm_saved_positions` + índice; `WindowManager.btm_insertion_plane` (`active`, `matrix`, `source_name`), com registro e remoção (data-delta §1-§2) | - | `[//]` | `caffmob_draw/move_over/props.py` | 🟡 | `[X]` |
| T010 | `btm_cabinet.shelves` (Int 0-20) com `update` que regenera a malha (data-delta §2, D-09) | - | `[//]` | `caffmob_draw/data/properties.py` | 🟡 | `[X]` |
| T011 | Pacotes `customize/` e `aggregates/` com `register()`/`unregister()` próprios, chamados por `caffmob_draw/__init__.py` na ordem certa (props antes de operadores e painéis) | T007, T008 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |

## Fase 2, Testes

`unittest` dos núcleos puros (sem Blender).

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T012 | Testes do `spec`: ida e volta dict, validação de nomes vazios/inválidos, interior com alturas digitadas fora do vão | T001 | `[//]` | `tests/test_customize_spec.py` | 🟢 | `[X]` |
| T013 | Testes do manifesto: montar/ler, `schema_version` maior recusado, nome com caracteres proibidos sanitizado, `.blend` sem `.json` tratado como grupo antigo | T002 | `[//]` | `tests/test_module_manifest.py` | 🟡 | `[X]` |
| T014 | Testes dos limites: arrastar além da borda para na borda, `offset` −30 mm numa lateral de 18 mm vira −18 mm, as seis faces, pai girado | T003 | `[//]` | `tests/test_aggregate_limits.py` | 🟢 | `[X]` |
| T015 | Testes da varredura: obstáculo no meio do arco para no contato com erro ≤ 0,25°, correr com curso 80 cm e obstáculo a 50 cm, fechar sem teste, sem obstáculo chega ao máximo | T004 | `[//]` | `tests/test_leaf_sweep.py` | 🟡 | `[X]` |
| T016 | Testes do reposicionamento: X = 150 mm, rotação 90° com A e B girados, relativa ↔ absoluta sem mover, posição salva aplicada a outro par dá o mesmo resultado relativo | T005 | `[//]` | `tests/test_reposition.py` | 🟢 | `[X]` |
| T017 | Testes do máximo por folha em `pivot_math` (180° permitido com `maximum`, 90° mantido sem ele) | T006 | `[//]` | `tests/test_inspection_math.py` | 🟢 | `[X]` |
| T018 | Testes do `machining`: retângulo do `CPM_CUTOUT` → entrada do JSON, `THROUGH_CUT` quando a profundidade ≥ espessura, recorte fora da peça é cortado ao contorno, ordenação estável | T045 | `[//]` | `tests/test_cut_plan_machining.py` | 🟡 | `[X]` |

## Fase 3, Núcleo

Incrementos I1 (T019-T031), I2 (T032-T040), I3 (T041-T048), I4 (T049-T054), I5 (T055-T061).

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T019 | Registro de adaptadores de personalização (padrão de `inspection.fronts._adapters()`): interface `capabilities(root)` / `read(root)` / `apply(root, spec)`, escolha pela biblioteca de `selection.classify.module_library` e raiz por `inspection.fronts.module_root_of` (D-02) | T001 | `[//]` | `caffmob_draw/customize/adapters/__init__.py` | 🟢 | `[X]` |
| T020 | Adaptador frameless, leitura: `capabilities` (todas as seções) e `read` do vão (tipo de frente, `DOOR_STYLE_NAME`, puxador e posição pelos idprops, material do estilo, interior) (D-02) | T019 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟢 | `[X]` |
| T021 | Adaptador frameless, frentes e estilo: troca pelo `caffmob_frameless.change_opening_type`; estilo aplicado por nome → índice em `assign_style_to_front`, mensagem do tamanho mínimo repassada (RN-03, D-05, D-06) | T020 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟢 | `[X]` |
| T022 | Adaptador frameless, puxador por frente: troca o input "Object" do `GeoNodeHardware` `IS_CABINET_PULL` via `compat` pelo modelo de `btm_custom.pull_model` (carregado por `load_pull_object`), "sem puxador" esconde, posição pelos idprops `Pull Location`/`* Pull Vertical Location` (D-07) | T021 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T023 | Adaptador frameless, materiais por peça e grupo: `Top Surface`/`Bottom Surface` das `GeoNodeCutpart` via `compat`, grupos por `CABINET_PART`/`part_roles.classify`, veio preservado (D-08) | T022 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T024 | Frameless: implementar o `TODO` `_add_rollouts_to_section` (as duas ocorrências) com a caixa de gaveta da frente `Drawer`, para gavetas internas por seção (D-09) | - | `[//]` | `caffmob_draw/product_libraries/frameless/types_frameless.py` | 🟡 | `[X]` |
| T025 | Adaptador frameless, interior: prateleiras, divisórias e gavetas pelo `change_interior_type`/`custom_interior_*`, alturas digitadas de `interior_heights` (D-09) | T023, T024 | - | `caffmob_draw/customize/adapters/frameless.py` | 🟡 | `[X]` |
| T026 | `customize.reapply(root)`: lê `btm_custom` dos vãos e peças e chama o `apply` do adaptador; chamada no fim de `change_opening_type` e de `assign_door_style` do frameless (D-04) | T025 | - | `caffmob_draw/customize/reapply.py` | 🟡 | `[X]` |
| T027 | `customize/library_io.py`, gravação: mecânica comum extraída de `frameless/operators/ops_library.py` (coleta de objetos, malhas, materiais, imagens e node groups; `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)`; miniatura 256 px) para `modules/<categoria>/`, gravando o manifesto; arquivos parciais removidos em erro (D-10) | T002 | - | `caffmob_draw/customize/library_io.py` | 🟡 | `[X]` |
| T028 | `customize/library_io.py`, leitura: anexa o `.blend`, re-resolve estilos/materiais/puxadores por nome (ausente → padrão + aviso com a lista), reaplica o `spec` pelo adaptador (D-10) | T027, T026 | - | `caffmob_draw/customize/library_io.py` | 🟡 | `[X]` |
| T029 | Operadores da biblioteca de módulos: `caffmob.module_save` (nome, categoria, confirmação ao substituir, D-11), `caffmob.module_insert` (posicionamento modal de `hb_placement.PlacementMixin`), renomear, apagar com confirmação e abrir pasta (RF-07..RF-10) | T028 | - | `caffmob_draw/customize/ops_library.py` | 🟡 | `[X]` |
| T030 | Operadores de personalização com `UNDO`: frente do vão, estilo da frente, puxador (frente ou todas), material (peça ou grupo), interior; gravam `btm_custom` e chamam o adaptador (RF-02..RF-06) | T019, T007 | - | `caffmob_draw/customize/ops_customize.py` | 🟢 | `[X]` |
| T031 | Painel "Personalizar módulo" com as seções Frentes, Puxadores, Materiais e Divisões internas; seção sem suporte desabilitada com o motivo de `capabilities`; "Selecione um módulo" sem seleção (RF-01) | T030 | - | `caffmob_draw/customize/panels.py` | 🟢 | `[X]` |
| T032 | Adaptador face frame, frentes e estilo: `capabilities`/`read`; troca por `caffmob_face_frame.change_opening`; estilo por `assign_style_to_front(record_override=True)` gravando também `hb_front_door_style`/`hb_front_drawer_style` (D-03, D-05, D-06) | T019 | - | `caffmob_draw/customize/adapters/face_frame.py` | 🟢 | `[X]` |
| T033 | Adaptador face frame, puxador por frente (troca `pull.data` pelo modelo de `pulls.resolve_pull_object` e reposiciona), material arbitrário por peça/grupo, interior por `add_interior_item`/`add_interior_division`/`add_rollout_box` (D-07..D-09) | T032 | - | `caffmob_draw/customize/adapters/face_frame.py` | 🟡 | `[X]` |
| T034 | Chamar `customize.reapply(root)` no fim da reconstrução de frentes do solver face frame (D-04) | T033, T026 | - | `caffmob_draw/product_libraries/face_frame/solver_face_frame.py` | 🟡 | `[X]` |
| T035 | Adaptador closets, frentes e estilo: `capabilities` (basculante, painel e divisória vertical desabilitados com motivo), `read`, troca por `caffmob_closets.change_opening`, estilo por frente com `fronts_closets.apply_style_to_front` (D-05, D-06) | T019 | - | `caffmob_draw/customize/adapters/closets.py` | 🟢 | `[X]` |
| T036 | Adaptador closets, puxador por frente (`pulls_closets.resolve_pull_object`), material por peça/grupo, interior por `add_adj_shelves`/`add_drawers` (D-07..D-09) | T035 | - | `caffmob_draw/customize/adapters/closets.py` | 🟡 | `[X]` |
| T037 | Chamar `customize.reapply(root)` no fim de `recalculate_closet_starter` (D-04) | T036, T026 | - | `caffmob_draw/product_libraries/closets/types_closets.py` | 🟡 | `[X]` |
| T038 | `btm`: prateleiras na malha do módulo em `generate_cabinet_mesh` a partir de `btm_cabinet.shelves` (espaçamento igual, espessura do módulo) (D-09) | T010 | `[//]` | `caffmob_draw/geometry/mesh_gen.py` | 🟡 | `[X]` |
| T039 | `btm`: puxador como filho das portas `_Door_L`/`_Door_R`/`_Door_Flip` e materiais da caixa e das portas por `geometry/materials.build_material` (D-07, D-08) | - | `[//]` | `caffmob_draw/geometry/door_controller.py` | 🟡 | `[X]` |
| T040 | Adaptador `btm`: `capabilities` (gavetas, divisórias e estilo desabilitados com motivo), `read`/`apply` de `door_swing`, `shelves`, puxador e materiais (D-05, D-09) | T019, T038, T039 | - | `caffmob_draw/customize/adapters/btm.py` | 🟡 | `[X]` |
| T041 | Converter/desconverter agregado: escolhe a face do pai mais próxima, vira filho Blender do pai, guarda pai e matriz originais, inicia `u`/`v`/`offset`; desconverter devolve tudo e remove recortes (RN-07, RN-12, D-12) | T008 | `[//]` | `caffmob_draw/aggregates/convert.py` | 🟢 | `[X]` |
| T042 | Aplicar posição do agregado a partir de `u`/`v`/`offset` com clamp de `limits.py`, chamado pelos `update` e pela recalculação quando o pai muda de tamanho (RN-08, RN-09) | T041 | - | `caffmob_draw/aggregates/apply.py` | 🟢 | `[X]` |
| T043 | Perfurar 3D: caixa cortadora do volume afundado, oculta e marcada `IS_CUTTING_OBJ`; `BOOLEAN` DIFFERENCE `EXACT` no pai depois do GN; desligar remove modificador e cortador; atualiza ao mudar `offset`/posição (D-13) | T042 | - | `caffmob_draw/aggregates/perforate.py` | 🟢 | `[X]` |
| T044 | Furo real: com `real_hole` e pai `GeoNodeCutpart`, `CPM_CUTOUT` "Agregado: <nome>" por `add_part_modifier` com `X/End X/Y/End Y/Route Depth/Flip Z` do retângulo afundado; desligar remove; pai sem peça de corte → opção indisponível com motivo (D-14) | T043 | - | `caffmob_draw/aggregates/perforate.py` | 🟡 | `[X]` |
| T045 | Núcleo puro do `machining`: parâmetros de `CPM_CUTOUT` + medidas da peça → entradas `POCKET`/`THROUGH_CUT`, recorte ao contorno com `MACHINING_CLIPPED`, ordenação (`interfaces/cut-plan-json.md`) | - | `[//]` | `caffmob_draw/cutting/machining.py` | 🟡 | `[X]` |
| T046 | Agregado como peça de produção: `production_part` liga/desliga `btm_geometry.fabrication` com medidas da caixa do agregado, para entrar por `part_sources.geometry_records` (RN-13, D-15) | T042 | - | `caffmob_draw/aggregates/production.py` | 🟢 | `[X]` |
| T047 | `caffmob.import_model` (`ImportHelper`, `*.obj;*.fbx;*.glb;*.gltf`): chama `bpy.ops.wm.obj_import`/`import_scene.fbx`/`import_scene.gltf` pelo sufixo, seleciona o que entrou, relata erro de importação com o motivo (RF-11, D-16) | - | `[//]` | `caffmob_draw/aggregates/ops_import.py` | 🟢 | `[X]` |
| T048 | Operadores de agregado com `UNDO`: converter (malha + pai selecionados, ou clique no pai), desconverter, mover modal restrito ao plano da face com clamp; apagar pai pergunta se apaga os agregados (RF-12, RF-13, RF-18, D-12) | T042, T043 | - | `caffmob_draw/aggregates/ops_aggregate.py` | 🟢 | `[X]` |
| T049 | Converter em folha de porta: pivô Empty na dobradiça (giro: eixo esquerdo/direito/topo/base pela caixa) ou na origem do trilho (correr), malha filha do pivô, `kind = LEAF` com `motion`, `max_angle`, `slide_dir`, `travel` (RN-11, D-17) | T041 | - | `caffmob_draw/aggregates/leaf.py` | 🟢 | `[X]` |
| T050 | Adaptador `aggregate_leaf` em `inspection.fronts._adapters()`: `get/apply/commit` com `pivot_math` e o máximo da folha, `slide` para correr; vale para "Abrir/Fechar Frentes" e o salvar fechado (D-17, D-18) | T049, T006 | - | `caffmob_draw/inspection/adapters/aggregate_leaf.py` | 🟢 | `[X]` |
| T051 | Teste de contato da folha: cascas de `interference.envelope_hulls` + `BVHTree.overlap` com pré-filtro por caixa, excluindo folha, pai e módulo raiz; cache de alvos por folha invalidado por `depsgraph_update_post` `@persistent` (removido no `unregister`) (D-19) | T004 | `[//]` | `caffmob_draw/aggregates/collision.py` | 🟡 | `[X]` |
| T052 | `update` de `open_value`: varredura (`sweep.py`) com o teste de contato, trava no contato, grava `contact_name`; fechar livre (RN-11a, RF-16) | T050, T051 | - | `caffmob_draw/aggregates/leaf.py` | 🟡 | `[X]` |
| T053 | Simulação gráfica `POST_VIEW` com a folha selecionada: eixo ou trilho, arco/curso até o máximo, posição atual e ponto de contato em vermelho; handler removido ao desmarcar e no `unregister` (RF-17, D-20) | T052 | - | `caffmob_draw/aggregates/overlay.py` | 🟢 | `[X]` |
| T054 | Painel do agregado e da folha: pai, face, `u`/`v`/`offset` com mín./máx., Perfurar, Furo real, Peça de produção; folha com tipo, eixo, sentido, máximo/curso, barra de abertura (%) e aviso "Folha bateu em <objeto>" (RF-19, RF-17) | T048, T052 | - | `caffmob_draw/aggregates/panels.py` | 🟢 | `[X]` |
| T055 | `MoveOver` com rotação (em torno do centro da base de A) e leitura absoluta, usando `reposition.py`; `restore()` volta também a rotação (D-21) | T005 | `[//]` | `caffmob_draw/move_over/scene.py` | 🟢 | `[X]` |
| T056 | Janela "Mover Sobre": campos Rotação e Passo, chave "Visualizar posição relativa", setas e Page Up/Down movendo pelo passo dentro do modal (RF-22..RF-25, D-21) | T055, T009 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟢 | `[X]` |
| T057 | Janela "Mover Sobre": lista de posições salvas com Salvar posição e Aplicar (RF-26, D-22) | T056 | - | `caffmob_draw/move_over/ops_dialog.py` | 🟡 | `[X]` |
| T058 | Substituir: busca de módulos (biblioteca do usuário e catálogo), insere o novo com a rotação de A, encosta o mesmo canto de referência e apaga o antigo, num passo de desfazer (RF-27, D-23) | T055, T029 | - | `caffmob_draw/move_over/ops_substitute.py` | 🔴 | `[X]` |
| T059 | Plano de inserção: `caffmob.set_insertion_plane` (raycast no ponto do clique, grava a matriz da face) e `caffmob.clear_insertion_plane`, no menu de contexto do objeto (RF-28, D-24) | T009 | `[//]` | `caffmob_draw/move_over/insertion_plane.py` | 🟡 | `[X]` |
| T060 | `hb_placement`: quando `btm_insertion_plane.active`, o ponto sem acerto cai no plano gravado em vez de Z = 0 (RN-17, D-24) | T059 | - | `caffmob_draw/hb_placement.py` | 🟡 | `[X]` |
| T061 | Painel de propriedades: subpainéis Arranjo (pai, filhos, agregados), Modelos ("Personalizar módulo"), Movimentação (posição, rotação, passo, plano) e Propriedades (dimensões com mín./máx.) (RF-29, RF-30, D-25) | T031, T054 | - | `caffmob_draw/ui/object_properties.py` | 🟢 | `[X]` |

## Fase 4, Integração

Contrato do JSON, registro e testes de fumaça por incremento.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T062 | JSON de produção `2.1.0`: campo `machining` em cada peça (lista vazia sem agregado), leitor aceitando `2.0.0` e `2.1.0` (`interfaces/cut-plan-json.md`) | T045 | `[//]` | `caffmob_draw/cutting/json_exporter.py` | 🟢 | `[X]` |
| T063 | `part_sources`: ler os `CPM_CUTOUT` "Agregado: *" de cada `GeoNodeCutpart` via `compat` e entregar ao `machining` da peça (D-14) | T045, T044 | `[//]` | `caffmob_draw/cutting/part_sources.py` | 🟡 | `[X]` |
| T064 | Registro final: operadores, painéis, handler `depsgraph_update_post` e de desenho dos pacotes `customize/` e `aggregates/`, operadores novos do `move_over/`, item do menu de contexto; `unregister` desfaz tudo | T029, T031, T040, T048, T053, T054, T057, T059 | `[//]` | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T065 | Aviso ao salvar: handler `save_post` `@persistent` com "Projeto salvo: <arquivo>" na barra de status; erro de gravação registrado no console com caminho e motivo (RF-32, D-27) | - | `[//]` | `caffmob_draw/ui/save_feedback.py` | 🟡 | `[X]` |
| T066 | Fumaça I1/I2 no Blender: um módulo de cada biblioteca — personalizar cada seção, mudar a largura e conferir que a personalização fica, salvar como módulo, inserir num arquivo novo e comparar; nome repetido pergunta (onboarding I1/I2) | T064 | - | `tests/blender_003_customize_smoke.py` | 🟡 | `[X]` |
| T067 | Fumaça I3/I4 no Blender: importar OBJ, converter, clamp na borda, `offset` −30 → −18 mm, Perfurar, furo real no JSON, desconverter; folha de giro bate na parede, correr 50% = 40 cm, salvar fechado (onboarding I3/I4) | T064, T062, T063 | - | `tests/blender_003_aggregates_smoke.py` | 🟡 | `[X]` |
| T068 | Fumaça I5 no Blender: Mover Sobre com X/rotação, cancelar sem desfazer, confirmar com um desfazer, relativa/absoluta sem mover, posição salva em outro par, plano de inserção (onboarding I5) | T064 | - | `tests/blender_003_move_over_smoke.py` | 🟡 | `[X]` |

## Fase 5, Polimento

Documentação do usuário.

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T069 | Guia do usuário: personalizar módulo e salvar como módulo | T066 | `[//]` | `docs/usuario/modulos-personalizaveis.md` | 🟢 | `[X]` |
| T070 | Guia do usuário: agregados, Perfurar, furo real e folha de porta com simulação | T067 | `[//]` | `docs/usuario/agregados-e-folhas.md` | 🟢 | `[X]` |
| T071 | Guia do usuário: seção do Mover Sobre ampliado (rotação, passo, relativa/absoluta, posições salvas, Substituir, plano de inserção) | T068 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |

## Notas de execução

- O face frame não entra no plano de corte (`cutting/part_sources.py:72`); "Furo real" em peça face frame fica indisponível com motivo até um bug próprio ser corrigido.
- 2026-10-07 (rodada única, T001–T071): desvios de arquivo alvo, sem mudar o escopo:
  - T034: o recálculo central do face frame está em `product_libraries/face_frame/types_face_frame.py`
    (`recalculate_face_frame_cabinet`), não em `solver_face_frame.py`; o gancho foi posto lá.
  - T060: o fallback do ponto sem acerto fica em `hb_snap.py` (`snap_to_grid`), chamado por
    `hb_placement.update_snap`; o plano de inserção entrou em `hb_snap.py`.
  - T046: além de `aggregates/production.py`, `cutting/part_sources.geometry_records` passou a incluir os agregados
    marcados (sem trocar o tipo do objeto para geometria livre, que refaria a malha importada).
  - T025: o pedido de interior por vão fica em `btm_custom.interior` (JSON de `spec.Interior`) em vez de
    `interior_heights` do data-delta, para guardar prateleiras, divisórias, gavetas e alturas juntas.
  - T027: a mecânica de gravação foi reimplementada em `customize/library_io.py` no mesmo formato do frameless; os
    operadores de grupo antigos não foram tocados.
  - T039: `geometry/materials.build_material` não foi usado; o módulo `btm` recebe os materiais escolhidos por nome.
  - T053: o handler de desenho fica registrado com o add-on e só desenha com uma folha ativa (mesmo padrão de
    `inspection/overlay.py`); é removido no `unregister`.
  - T059: o menu de contexto não sabe onde foi o clique; "Usar como plano de inserção" pede um clique na face.
  - T062: três testes antigos fixavam o JSON em 2.0.0 e foram atualizados para 2.1.0.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-to-do` | reversa |
