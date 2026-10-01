# hb_placement — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Sequência para reimplementar a unit na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md) e [`design.md`](design.md).
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Pré-requisitos
- [ ] Unit [`hb_core`](../hb_core/) disponível: `GeoNodeObject.get_input`, `GeoNodeWall.get_input/has_modifier/get_connected_wall(include_loop_seam)`.
- [ ] `units` (`inch`, `feet`, `millimeter`, `centimeter`).
- [ ] `compat.get_builtin_shader` disponível para o desenho GPU.
- [ ] Receitas "modal + GPU" e "raycast" conferidas em `docs/rag/project/02_padroes_blender_5_2.md`; armadilhas em `04_armadilhas.md`.
- [ ] Assinaturas confirmadas: `bpy.types.Scene.ray_cast`, `bpy.types.SpaceView3D.draw_handler_add`,
      `bpy_extras.view3d_utils.region_2d_to_vector_3d`, `mathutils.geometry.intersect_line_plane`.

## Tarefas

### Bloco A — Snap e primitivas

- [ ] T-01, `hb_snap.get_region` com retorno `None` tratado pelos chamadores
  - Origem no legado: `hb_snap.py:10-29`, `hb_placement.py:158-173`
  - Critério de pronto: `update_snap` sem viewport 3D não levanta `AttributeError` (mantém o último ponto)
  - Confiança: 🟢

- [ ] T-02, Raycast com anel (6 raios, 50 px), ignorando `HB_CURRENT_DRAW_OBJ`
  - Origem no legado: `hb_snap.py:7-8,38-82`
  - Critério de pronto: RF-02; `view_point` devolvido é o do raio vencedor
  - Confiança: 🟢

- [ ] T-03, Snap a vértice/aresta com Ctrl, checando `hit_face_index >= 0` e usando o mesh avaliado consistente
  - Origem no legado: `hb_snap.py:84-145`
  - Critério de pronto: RF-03; `hit_face_index == -1` não pega o último polígono
  - Confiança: 🟡 (correspondência de índices em objetos GN a validar, Q-04)

- [ ] T-04, Plano de fallback e grade (`snap_to_grid`), `snap_value_to_grid`, `snap_vector_to_grid`
  - Origem no legado: `hb_snap.py:147-254`
  - Critério de pronto: RF-04, RF-20
  - Confiança: 🟢

- [ ] T-05, `hb_gpu_draw` (área visível e primitivas) usando `compat.get_builtin_shader`
  - Origem no legado: `hb_gpu_draw.py:12-114`
  - Critério de pronto: RF-18; nenhum `gpu.shader.from_builtin` fora de `compat.py`
  - Confiança: 🟢

### Bloco B — Estado e digitação

- [ ] T-06, Enums `PlacementState`/`TypingTarget`, `NUMBER_KEYS`, `PlacementDimSpec`; remover `ADJUSTING` e `OFFSET_Y` ou documentá-los como reservados
  - Origem no legado: `hb_placement.py:17-78`
  - Critério de pronto: grep sem membros mortos (ou comentário de reserva)
  - Confiança: 🟢

- [ ] T-07, Ciclo de vida: `init_placement`, `register_placement_object`, `cancel_placement` com remoção pós-ordem
  - Origem no legado: `hb_placement.py:115-130,410-452`
  - Critério de pronto: RF-01
  - Confiança: 🟢

- [ ] T-08, Máquina de digitação `handle_typing_event` e hooks
  - Origem no legado: `hb_placement.py:179-281`
  - Critério de pronto: RF-05; cenários "Digitar largura" e "Sair da digitação" passam
  - Confiança: 🟢

- [ ] T-09, Parser `parse_typed_distance` com precedência RN-05 e unidade da cena RN-06; permitir digitar `'`, `"`, espaço e letras de unidade
  - Origem no legado: `hb_placement.py:283-388`, `:55-64`
  - Critério de pronto: RF-06 (`600`, `2'6"`, `1 1/2"`, `60cm`, `0.6m`); texto inválido → `None`
  - Confiança: 🟢 (parser) / 🟡 (ampliação de teclas, Q-03)

### Bloco C — Vão e colisões

- [ ] T-10, Coleta de obstáculos filhos com lado, portas/janelas, anotações, snap lines e extensão por rotação
  - Origem no legado: `hb_placement.py:454-500,958-1017,1110-1114`
  - Critério de pronto: cenários "Porta bloqueia os dois lados" e "Gabinete do outro lado" passam
  - Confiança: 🟢

- [ ] T-11, Filtro vertical opt-in (sobreposição estrita)
  - Origem no legado: `hb_placement.py:494-497,988-993`
  - Critério de pronto: cenário "Aéreo sobre inferior" passa
  - Confiança: 🟢

- [ ] T-12, Gabinetes livres (ilhas/penínsulas) pela faixa de profundidade
  - Origem no legado: `hb_placement.py:1028-1070`
  - Critério de pronto: RF-11; faixa padrão configurável (hoje 24")
  - Confiança: 🟢

- [ ] T-13, `get_adjacent_wall_intrusion` (laje + gabinetes da vizinha)
  - Origem no legado: `hb_placement.py:672-826`
  - Critério de pronto: RF-09, inclusive pela emenda de cômodo fechado
  - Confiança: 🟢

- [ ] T-14, `get_tee_wall_intrusions`, com índice espacial ou filtro prévio por `IS_WALL_BP` para não varrer a cena inteira a cada tick
  - Origem no legado: `hb_placement.py:828-915`
  - Critério de pronto: RF-10; tempo por tick medido em cena com 500+ objetos
  - Confiança: 🟢

- [ ] T-15, Varredura do vão e escolha de `snap_x`, **mesclando intervalos sobrepostos** antes da varredura
  - Origem no legado: `hb_placement.py:502-576,1116-1139`
  - Critério de pronto: RF-07/RF-08; obstáculos sobrepostos não recuam `gap_start`; cursor dentro de obstáculo tem regra definida (Q-02)
  - Confiança: 🟡

- [ ] T-16, `find_placement_gap` (sem lado) para portas/janelas
  - Origem no legado: `hb_placement.py:502-576`
  - Critério de pronto: consumidor `operators/doors_windows.py` continua funcionando
  - Confiança: 🟢

- [ ] T-17, Recuos `compute_gap_holdoffs` + `_wall_end_is_inside_corner`; remover o parâmetro morto `wall_thickness`
  - Origem no legado: `hb_placement.py:1143-1270`
  - Critério de pronto: RF-13; cenários de recuo passam; único chamador (`face_frame/operators/ops_placement.py:2543`) atualizado
  - Confiança: 🟢

- [ ] T-18, Converter tolerâncias em polegadas (1/2", 1/4", 1", 24") para constantes nomeadas em metros, parametrizáveis
  - Origem no legado: `hb_placement.py:1028,1068,1217-1264`
  - Critério de pronto: nenhum literal `inch(...)` solto nas regras; valores equivalentes mantidos por padrão
  - Confiança: 🟢 (valores) / 🔴 (padrões para o mercado BR, Q-01)

### Bloco D — Encosto e cota

- [ ] T-19, `find_cabinet_bp`, `detect_cabinet_snap_target`, `compute_cabinet_snap_transform`
  - Origem no legado: `hb_placement.py:580-670`
  - Critério de pronto: RF-14; cenários de encosto passam
  - Confiança: 🟢

- [ ] T-20, `DimensionOperatorMixin` com `add_dimension_draw_handler` idempotente e `cancel()` que remove handler e header
  - Origem no legado: `hb_placement.py:1360-1639`
  - Critério de pronto: RF-15; chamar `add` 2× não vaza handle
  - Confiança: 🟢

### Bloco E — Desenho e duplicação

- [ ] T-21, `draw_placement_dimensions` e `draw_dimension_snap_indicator` sem `TRI_FAN`/`LINE_LOOP` (usar `TRIS`/`LINES`)
  - Origem no legado: `hb_placement.py:1642-1856`
  - Critério de pronto: RF-16/RF-17; visual igual (cores e tamanhos de RN-33/RN-34)
  - Confiança: 🟢

- [ ] T-22, `PlacementMixin.cancel()` padrão que chama `cancel_placement` e `remove_placement_dim_handler`
  - Origem no legado: ausência de `cancel()` nos mixins
  - Critério de pronto: abrir outro arquivo durante o posicionamento não deixa handler órfão
  - Confiança: 🟡

- [ ] T-23, `duplicate_object_hierarchy` sem `bpy.ops` (cópia via `obj.copy()`/`data.copy()` + remapeamento de drivers e parentesco), ou com `temp_override`
  - Origem no legado: `hb_placement.py:1273-1340`
  - Critério de pronto: RF-19; funciona fora da VIEW_3D
  - Confiança: 🟡

## Tarefas de Teste

- [ ] TT-01, Parser: tabela de entradas/saídas por sistema de unidades (teste Python puro com `scene.unit_settings` simulado)
- [ ] TT-02, Máquina de digitação: sequências de eventos simulados (PRESS de dígito, Backspace, Esc, Enter, Tab)
- [ ] TT-03, Vão por lado: parede sintética com porta, gabinete frente/trás, snap line, ilha, parede em T, vizinha em canto
- [ ] TT-04, Obstáculos sobrepostos e cursor dentro de obstáculo (regressão de T-15)
- [ ] TT-05, Recuos: ponta livre, canto interno, borda de porta, vão estreito
- [ ] TT-06, Encosto LEFT/RIGHT com alvo girado 0°/90°/180°
- [ ] TT-07, Cota: sequência FIRST→SECOND→OFFSET, ortho AUTO/H/V, cancelamento remove handler
- [ ] TT-08, Registro/remoção de draw handlers: nenhum handler órfão após `unregister()` (smoke `--background` onde possível)

## Tarefas de Migração de Dados

Não se aplica: a unit não persiste dados. 🟢 Os marcadores lidos (`IS_*`, `SNAP_X_POSITION`) já existem nos `.blend`.

## Ordem Sugerida
1. **Bloco A** e **Bloco B** primeiro (base de todos os operadores modais).
2. **Bloco C** em seguida, na ordem T-10 → T-11 → T-12/T-13/T-14 → T-15 → T-16 → T-17 → T-18.
3. **Bloco D** e **Bloco E** em paralelo.
4. Migrar os consumidores (frameless → face_frame → closets → operators) só depois de TT-01..TT-07 passarem.
5. Bloqueios: T-15 depende de Q-02; T-18 depende de Q-01; T-03 depende de Q-04.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 1 (2026-09-30) — ver **Decisões da rodada 1** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md): Q-01 (tolerâncias em polegadas no mercado BR), Q-02 (cursor dentro de
obstáculo), Q-03 (teclas digitáveis), Q-04 (índice de face em objetos GN), Q-05 (origem dos marcadores), Q-06
(consumidores face_frame/closets).

## Decisões da rodada 1 (2026-09-30)

Respostas em [`questions.md`](questions.md); fonte: `.reversa/respostas-questions.md`, investigações no Blender 5.2.0 e RAG do Manual Promob.

| Pergunta | Decisão | Efeito nas tarefas |
|---|---|---|
| Q-01 | Tolerâncias 10 / 5 / 25 / 600 / 5 mm | T-18 🟢 com esses valores |
| Q-02 | Vão livre mais próximo do cursor (confirmado pelo Promob) | T-15 🟢 |
| Q-03 | Sufixos `mm`/`cm`/`m` e vírgula; sem frações | T-09 🟢 — **não** aceitar `'`, `"` nem espaço (revoga essa parte do texto da tarefa); **nova T-24**: campos de posição precisa (Afastamento, Cotas Anterior/Posterior/Inferior/Superior) e deslocamento por valor, como no Promob |
| Q-04 | `index` do `ray_cast` = polígono do mesh avaliado | T-03 🟢: usar `evaluated_get(depsgraph).to_mesh()` |
| Q-05 | Marcadores documentados (grep) | 🟢; **nova T-25**: o preview do frameless deve gravar `HB_CURRENT_DRAW_OBJ` como face_frame/closets |
| Q-06 | face_frame passa `wall_thickness` por nome; face_frame/closets usam `PlacementDimSpec` e `duplicate_object_hierarchy` | T-17 🟢 **alterada**: manter `wall_thickness` aceito e ignorado (deprecado), não removê-lo; não reordenar `PlacementDimSpec` |
| Q-07 | Rejeitar largura negativa com mensagem | T-09 🟢 |
| Q-08 | Aviso + alternador global "Evitar Sobreposição" | T-15 🟢 + **nova T-26**: alternador na barra de status (ligado = para no limite do vão; desligado = permite sobrepor), nome diferente de "Colisão" |
