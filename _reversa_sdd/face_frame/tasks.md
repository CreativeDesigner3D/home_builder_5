# face_frame — Tarefas de Implementação

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Sequência para reimplementar a unit a partir do legado, na API do **Blender 5.2**. Ver [`requirements.md`](requirements.md)
> e [`design.md`](design.md). Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Caminhos relativos a `blendertomob/product_libraries/face_frame/`.

## Pré-requisitos
- [ ] **Decisão de permanência** desta unit no produto (Q-01). Recomendação: manter como linha "Face frame (EUA)"
      ativada pelo preset EUA, priorizando o frameless para o mercado brasileiro.
- [ ] [`hb_core`](../hb_core/tasks.md) (ponte GN por nome em `compat.py`), [`hb_placement`](../hb_placement/tasks.md)
      (com `wall_thickness` mantido em `compute_gap_holdoffs` — decisão PL-06) e
      [`product_common`](../product_common/tasks.md) blocos A–C (motor de portas e perfis).
- [ ] Escavação complementar dos trechos 🔴 (cantos, pós-passes, itens internos) — Q-02.
- [ ] `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`.

## Tarefas

### Bloco A — Propriedades e registro

- [ ] T-01, PropertyGroups `Object.face_frame_*`, produtos e `Scene.hb_face_frame` com `# type: ignore`, leitura por atributo
  - Origem no legado: `props_hb_face_frame.py:4101-8155`
  - Critério de pronto: nenhum acesso `obj["prop"]` a `bpy.props` no pacote
  - Confiança: 🟢

- [ ] T-02, Corrigir `cab_props['refrigerator_opening_height'] = …` para escrita por atributo e unificar com `refrigerator_height`
  - Origem no legado: `types_face_frame.py:7335`; `props_hb_face_frame.py` (cena 69" × gabinete 62")
  - Critério de pronto: abertura da geladeira e `back_bottom_inset` usam a mesma altura
  - Confiança: 🟢 (bug) / 🟡 (qual valor manter, Q-07)

- [ ] T-03, Enums dinâmicos (stain, paint, estilos de porta/gaveta, puxadores) com cache das strings e identificador estável
  - Origem no legado: `props_hb_face_frame.py:195-258`, `:6406-6425` (modelo correto: `_bottom_rail_profile_items`)
  - Critério de pronto: seleção não muda quando a lista muda; rótulos estáveis após 100 redraws
  - Confiança: 🟢

- [ ] T-04, `register()`/`unregister()` sem engolir exceções, removendo `dim_edit_overlay`, keymap, handler `load_post` e o handler de `split_preview`
  - Origem no legado: `__init__.py:13-26`; `props_hb_face_frame.py:8064-8155`; `dim_edit_overlay.py:897-922`; `split_preview.py:218-236`
  - Critério de pronto: registrar/desregistrar 2× sem resíduo, inclusive com o diálogo de split aberto
  - Confiança: 🟢

### Bloco B — Pipeline de recálculo

- [ ] T-05, `suspend_recalc`, `_PENDING_RECALC_NAMES` e guardas de reentrância com chave estável (`as_pointer()` ou nome), sem engolir exceções no dreno
  - Origem no legado: `types_face_frame.py:81-107`, `:1029-1037`, `:8745-8777`
  - Critério de pronto: N escritas dentro de `suspend_recalc` → 1 recálculo; exceção no dreno é relatada
  - Confiança: 🟢

- [ ] T-06, Registrar **todas** as classes em `WRAP_CLASS_REGISTRY` (móveis, cômodas, criados-mudos, window seat, BookcaseUpper, Hutch, BookcaseStorageUnit) e checar no registro que nenhuma subclasse ficou de fora
  - Origem no legado: `types_face_frame.py:6919-6921`, `:8636-8700`
  - Critério de pronto: editar uma cômoda não zera o rodapé (RF-23); teste falha se uma subclasse não estiver no registro
  - Confiança: 🟢

- [ ] T-07, `FaceFrameCabinet.recalculate` na ordem obrigatória (profundidades → alturas → kicks → rails → larguras → árvores → layout → peças → pós-passes → estilo)
  - Origem no legado: `types_face_frame.py:1842-2531`
  - Critério de pronto: cenários de `requirements.md`; ordem coberta por teste
  - Confiança: 🟢

- [ ] T-08, Agrupar as escritas da exposição e de `assign_style_to_cabinet` em `suspend_recalc`
  - Origem no legado: `exposure.py:416-440`; `props_hb_face_frame.py:1668-1690`
  - Critério de pronto: exposição de um gabinete → 1 recálculo (hoje até ~9)
  - Confiança: 🟡

- [ ] T-09, Reconciliar frentes, pivôs, puxadores, splitters e backings por identidade (em vez de apagar e recriar)
  - Origem no legado: `types_face_frame.py:5785-5830`, `:5927-5975`
  - Critério de pronto: recalcular 10× não cria malhas órfãs nem muda nomes de objetos
  - Confiança: 🟡 (Q-08)

### Bloco C — Solver puro

- [ ] T-10, `FaceFrameLayout` e `_read_tree_node` como snapshot imutável
  - Origem no legado: `solver_face_frame.py:33`, `:272-335`
  - Critério de pronto: solver testável sem cena (dados de entrada em dict)
  - Confiança: 🟢

- [ ] T-11, Distribuição com travas (A1) com clamp em 0 e aviso quando os travados excedem o disponível
  - Origem no legado: `types_face_frame.py:1641-1725`, `:1763-1817`; `solver_face_frame.py:2813-2852`
  - Critério de pronto: cenários de distribuição; nenhum bay negativo
  - Confiança: 🟢 (regra) / 🟡 (clamp, Q-04)

- [ ] T-12, `_redistribute_split_node` considerando overrides por membro, membros removidos, remove_bottom e front_drop
  - Origem no legado: `types_face_frame.py:1763`
  - Critério de pronto: tamanho exibido = tamanho construído em todos os casos
  - Confiança: 🟢

- [ ] T-13, Segmentos de rails/fundos/costas/travessas/kicks (A2) e mid stiles
  - Origem no legado: `solver_face_frame.py:1305-1456`, `:1743-1809`
  - Critério de pronto: RN-09..RN-11
  - Confiança: 🟢

- [ ] T-14, Carcaça: offsets de lateral por acabamento, topo com scribe, ancoragem BASE/TALL × UPPER, lateral capturada pelo fundo
  - Origem no legado: `solver_face_frame.py:379-507`, `:683-730`
  - Critério de pronto: RN-01..RN-05
  - Confiança: 🟢

- [ ] T-15, Árvore de aberturas (A3): reveals da raiz, membros removidos, promoção a BOTTOM_RAIL, backings
  - Origem no legado: `solver_face_frame.py:2774-3074`
  - Critério de pronto: RN-12, RN-15, RN-16
  - Confiança: 🟢

- [ ] T-16, Frentes (A4): overlay por lado, pivôs, folhas duplas/triplas, tri-view, gavetas/pullouts
  - Origem no legado: `solver_face_frame.py:3232-3664`
  - Critério de pronto: RN-17..RN-21
  - Confiança: 🟢

- [ ] T-17, Fillers de eletrodoméstico/front drop e prateleiras automáticas
  - Origem no legado: `solver_face_frame.py:519-552`, `:3667-3765`
  - Critério de pronto: RN-22, RN-23
  - Confiança: 🟢

### Bloco D — Exposição e acabamentos

- [ ] T-18, Exposição (A5) com suporte a gabinetes girados em relação à parede
  - Origem no legado: `exposure.py:142-476`
  - Critério de pronto: RN-27/RN-28; gabinete girado 90° detecta a parede corretamente
  - Confiança: 🟢 (regra) / 🟡 (rotação, Q-10)

- [ ] T-19, Painéis aplicados (A9) e acabamentos de ponta (paneled, beadboard, shiplap, flush-x)
  - Origem no legado: `applied_panel_sizing.py:65-256`; pós-passes de `types_face_frame.py`
  - Critério de pronto: RN-29; fórmulas dos pós-passes documentadas antes de implementar
  - Confiança: 🟢 (A9) / 🔴 (pós-passes, Q-02)

### Bloco E — Tipos especiais e cantos

- [ ] T-20, Geladeira, lap drawer, vaidade, tri-view, banheiro, móveis e produtos lineares
  - Origem no legado: `types_face_frame.py:7286-8700`
  - Critério de pronto: RN-20, RN-21, RN-30, RN-31; `LAP_DRAWER` gravado ou removido do enum
  - Confiança: 🟢 / 🟡 (LAP_DRAWER, Q-09) / 🔴 (produtos lineares, Q-02)

- [ ] T-21, Cantos pie-cut, diagonal e pie-cut drawer, com `corner_type` desconhecido tratado sem `NotImplementedError`
  - Origem no legado: `types_face_frame_corner.py:195-2986`
  - Critério de pronto: RN-32; tipos desconhecidos viram NONE com aviso
  - Confiança: 🔴 (Q-02)

- [ ] T-22, Cunha tip-up e moldura angular
  - Origem no legado: `solver_face_frame.py:1249`, `:1558-1578`; `operators/ops_wedge.py`
  - Critério de pronto: RN-33, RN-34
  - Confiança: 🟢

### Bloco F — Estilos, catálogo e puxadores

- [ ] T-23, Estilos de gabinete e porta (madeira, cor, overlay, série) vinculados por nome com âncoras de renomeação
  - Origem no legado: `props_hb_face_frame.py:877-2883`, `:8105-8155`; `operators/ops_styles.py`
  - Critério de pronto: renomear um estilo mantém os gabinetes vinculados
  - Confiança: 🟢

- [ ] T-24, Catálogo de séries/perfis/painéis desacoplado do código (arquivo de dados), com o catálogo CWP como pacote opcional
  - Origem no legado: `style_options.py` (9838 linhas geradas)
  - Critério de pronto: trocar o catálogo não exige editar Python
  - Confiança: 🟡 (Q-06)

- [ ] T-25, Puxadores e regras de posição
  - Origem no legado: `pulls.py`; `types_face_frame.py:6290-6428`
  - Critério de pronto: RN-26
  - Confiança: 🟢

### Bloco G — Inserção e edição

- [ ] T-26, `place_cabinet` com auto nº de bays, preset padrão, fusão automática e preview com `HB_CURRENT_DRAW_OBJ`
  - Origem no legado: `operators/ops_placement.py:48-50`, `:317-329`, `:928-960`, `:1746`, `:3543`; `bay_presets.py:389-494`
  - Critério de pronto: cenários de inserção de `requirements.md`
  - Confiança: 🟢

- [ ] T-27, Quebrar/juntar gabinetes, equalizar, inserir/apagar bay, split opening com preview GPU
  - Origem no legado: `types_face_frame.py:9025-9400`; `operators/ops_cabinet.py`; `split_preview.py`
  - Critério de pronto: RN-35, RN-36; handler do preview removido em todas as saídas
  - Confiança: 🟢

- [ ] T-28, Rótulos editáveis (`dim_edit_overlay`) e arraste de fronteiras (`op_modify_cabinet`) com unidade do usuário
  - Origem no legado: `dim_edit_overlay.py:102-922`; `op_modify_cabinet.py`
  - Critério de pronto: `parse_distance` aceita `mm`/`cm`/`m` e vírgula (decisão PL-03)
  - Confiança: 🟢

- [ ] T-29, Comandos por peça e preservação `IS_MANUAL_PART` / `IS_MANUAL_FRONT`
  - Origem no legado: `operators/ops_part_commands.py`; `types_face_frame.py:1998-2020`, `:5954`
  - Critério de pronto: RN-37
  - Confiança: 🟢

- [ ] T-30, Operadores com `bl_idname` `btm.*` e `UNDO` onde alteram dados
  - Origem no legado: `operators/*.py` (`hb_face_frame.*`)
  - Critério de pronto: Ctrl+Z desfaz cada comando estrutural
  - Confiança: 🟢

### Bloco H — Complementos

- [ ] T-31, Tampos por corrida e ilha (código comum com o frameless)
  - Origem no legado: `operators/ops_countertop.py`; `frameless/operators/ops_countertop.py`
  - Critério de pronto: RN-39; um único módulo de tampo para as duas linhas
  - Confiança: 🟢

- [ ] T-32, Painéis de eletrodoméstico (solver hold/share) com o registry de specs
  - Origem no legado: `operators/ops_appliance_panels.py:120-600`
  - Critério de pronto: sem provider → só manual; menus ocultos (decisão `product_common` Q-01)
  - Confiança: 🟢

- [ ] T-33, Abrir/fechar frentes, biblioteca do usuário, padrões e miniaturas
  - Origem no legado: `operators/op_open_mode.py`, `ops_library.py`, `ops_defaults.py`, `ops_thumbnails.py`, `thumbnail_render.py`
  - Critério de pronto: abrir não dispara recálculo; miniatura restaura as configurações de render
  - Confiança: 🟢

- [ ] T-34, Expor as peças do face frame ao `cutting/` (lista de corte)
  - Origem no legado: ausente (lacuna L1 de `soul.md`)
  - Critério de pronto: gabinete gera lista de corte com moldura, carcaça, costas e frentes
  - Confiança: 🔴 (Q-05)

## Tarefas de Teste

- [ ] TT-01, Solver puro: distribuição, segmentos, árvore, frentes (sem Blender, a partir de snapshots)
- [ ] TT-02, Recálculo idempotente: 10 recálculos seguidos não mudam nada nem criam objetos novos (T-09)
- [ ] TT-03, `suspend_recalc` coalesce N escritas em 1 recálculo
- [ ] TT-04, Todas as subclasses estão em `WRAP_CLASS_REGISTRY` (T-06)
- [ ] TT-05, Exposição: isolado, encostado em parede, vizinho parcial, ilha, gabinete girado
- [ ] TT-06, Inserção: auto bays, fusão, TALL não funde
- [ ] TT-07, Geladeira com altura unificada (T-02)
- [ ] TT-08, `register()`/`unregister()` 2× sem resíduo, com split preview aberto
- [ ] TT-09, Lista de corte do face frame (T-34)

## Tarefas de Migração de Dados

- [ ] TM-01, Reescrever `refrigerator_opening_height` salvo como ID property para a `bpy.props` correspondente
  - Origem: `types_face_frame.py:7335`
  - Confiança: 🟡
- [ ] TM-02, Preservar tags e metadados (`IS_FACE_FRAME_*`, `CLASS_NAME`, `STYLE_NAME`, `hb_*`, `SIZE_ROLE`, flags manuais) como ID properties
  - Confiança: 🟢
- [ ] TM-03, Converter seleções de enum por índice para identificador estável (T-03)
  - Confiança: 🟢

## Ordem Sugerida
1. Resolver **Q-01** (permanência) antes de qualquer código.
2. **Bloco C** (solver puro) primeiro: testável sem Blender e base de tudo.
3. **Blocos A e B** em seguida; depois **D**, **F** e **G**.
4. **Bloco E** só após a escavação complementar (Q-02).
5. **Bloco H** por último; T-31 junto com o tampo do frameless.
6. Bloqueios: tudo ← Q-01; T-19/T-20/T-21 ← Q-02; T-11 ← Q-04; T-34 ← Q-05; T-24 ← Q-06; T-02 ← Q-07; T-09 ← Q-08;
   T-20 ← Q-09; T-18 ← Q-10.

## Lacunas Pendentes (🔴)

> ✅ Todas respondidas na rodada 2 (2026-10-01) — ver **Decisões da rodada 2** abaixo e a coluna Resposta de [`questions.md`](questions.md).
Detalhadas em [`questions.md`](questions.md):
- Q-01 Permanência da construção face frame no produto.
- Q-02 Escavação complementar (cantos, pós-passes, itens internos, produtos lineares).
- Q-03 Escopo de móveis e banheiro.
- Q-04 Clamp de bays negativos.
- Q-05 Integração com a lista de corte.
- Q-06 Catálogo CWP: manter, isolar ou substituir.
- Q-07 Altura única da geladeira.
- Q-08 Reconciliar frentes em vez de recriar.
- Q-09 Valor `LAP_DRAWER` do enum.
- Q-10 Exposição de gabinetes girados.
- Q-11 Fusão automática × opcional.

## Decisões da rodada 2 (2026-10-01)

Todas as recomendações ⭐ foram aceitas. As tarefas listadas saem do estado bloqueado e seguem a decisão.

| Pergunta | Decisão | Tarefas desbloqueadas |
|---|---|---|
| Q-01 | Sim, como linha opcional "Face frame (EUA)" ligada ao preset EUA; esforço de reimplementação depois do frameless. | Todas |
| Q-02 | Sim, só se Q-01 = manter; limitar ao que o subconjunto de `product_common` Q-11 usa. | T-19, T-20, T-21 |
| Q-03 | Fora do escopo inicial (`Could`). | T-20 |
| Q-04 | Sim, igual à calculadora (`hb_core` Q-09). | T-11 |
| Q-05 | Sim, se Q-01 = manter. | T-34 |
| Q-06 | Pacote de dados opcional (fora do código); catálogo BR quando houver fornecedor parceiro. | T-24 |
| Q-07 | Única, vinda do preset (EUA 69"; BR conforme o eletrodoméstico, ~1,70–1,85 m). | T-02 |
| Q-08 | Sim. | T-09 |
| Q-09 | Gravar (o solver já trata LAP_DRAWER). | T-20 |
| Q-10 | Sim. | T-18 |
| Q-11 | Não: virar opção (tecla/preferência), padrão desligado. | T-26 |
