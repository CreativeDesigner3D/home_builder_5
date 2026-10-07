# Cross-check — 003-modulos-agregados-reposicionar

> Data: 2026-10-07 · Auditoria por `/reversa-audit` (somente leitura; nenhum artefato da feature foi alterado)
> Artefatos: [requirements.md](../requirements.md) · [roadmap.md](../roadmap.md) · [actions.md](../actions.md)
> (+ [data-delta.md](../data-delta.md), [interfaces/](../interfaces/))
> Pedido do titular: relato ao vivo sobre "Ajustar Piso" e inserção de portas/janelas (seção "Relato do titular").

## Resumo

| Severidade | Cruzamento da 003 | Relato do titular | Total |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 1 | 2 | 3 |
| MEDIUM | 5 | 2 | 7 |
| LOW | 3 | 0 | 3 |

O cruzamento da 003 não tem contradição de conteúdo: as 71 ações estão concluídas, sem dependência inválida nem ciclo.
O que pesa são os dois defeitos relatados, que **não pertencem à 003**: vêm do legado (piso, portas e janelas) e
pedem bug ou feature própria.

## Achados

| ID | Severidade | Eixo | Descrição | Onde está |
|---|---|---|---|---|
| A001 | HIGH | Cobertura | D-26 (cotas recalculadas a cada desenho) não tem ação; é decisão de "não mudar nada", mas pela regra do Reversa decisão sem ação é HIGH | `roadmap.md` §3 D-26; `actions.md` (nenhuma ação cita D-26) |
| A002 | MEDIUM | Consistência | Substituir: RF-27 fala em "módulo do catálogo"; D-23, em "biblioteca do usuário e catálogo"; T058 entregou só a biblioteca do usuário | `requirements.md` RF-27; `roadmap.md` D-23; `actions.md` T058 + Notas |
| A003 | MEDIUM | Consistência | Plano de inserção: RF-28 diz "com botão direito sobre uma face"; D-24, "raycast no ponto do clique"; a implementação pede escolher no menu e depois clicar na face | `requirements.md` RF-28; `roadmap.md` D-24; `actions.md` Notas (T059) |
| A004 | MEDIUM | Consistência | O data-delta descreve `btm_custom.interior_heights`; o código usa `btm_custom.interior` (JSON de `spec.Interior`) | `data-delta.md` §1; `actions.md` Notas (T025) |
| A005 | MEDIUM | Consistência | Arquivo alvo de T034 (`solver_face_frame.py`) e T060 (`hb_placement.py`) difere do arquivo mudado (`types_face_frame.py`, `hb_snap.py`) | `actions.md` T034, T060 + Notas |
| A006 | MEDIUM | Cobertura | RNF de desempenho (100 ms com 200 módulos) e o risco "medido na fumaça" não têm ação de medição; os smokes não medem tempo | `requirements.md` §6; `roadmap.md` §9; `actions.md` T066-T068 |
| A007 | LOW | Consistência | D-20/T053 pedem o handler da simulação removido ao desmarcar; ele fica registrado e só desenha com folha ativa (mesmo padrão de `inspection/overlay.py`) | `roadmap.md` D-20; `actions.md` T053 + Notas |
| A008 | LOW | Cobertura | RF-20 (agregados entram no módulo salvo) não é citado por nenhuma ação; está coberto por T027/T028 (o `.blend` leva a árvore inteira e o manifesto lista `aggregates`) | `requirements.md` RF-20; `actions.md` T027 |
| A009 | LOW | Cobertura | Gherkin "Reposicionar com campos e cancelar" pede "nenhum passo de desfazer"; o smoke confere a volta da posição, não o desfazer (precisa de janela) | `requirements.md` §7; `tests/blender_003_move_over_smoke.py` |
| A010 | HIGH | Relato / legado | **"Ajustar Piso" ignora as paredes do editor e do construtor.** Reproduzido: sala 4 × 3 m feita pelo editor de paredes → piso de 5 × 5 m centrado na origem | `operators/floor_builder.py:14-25, 57-89`; `geometry/mesh_gen.py:121-206`; `data/properties.py:184-193` |
| A011 | HIGH | Relato / legado | **Porta, janela e vão livre viram um bloco liso**, que é o próprio cortador, sem folha nem batente. Fica fora da espessura depois de mudar a Direção da parede, e o corte não tem opção. Não existe tipo "Portal" | `operators/doors_windows.py:429-446, 732-830, 991`; `hb_types.py:539-552`; `hb_props.py:498` |
| A012 | MEDIUM | Relato / legado | `btm_plane.object_kind` tem padrão `'WALL'` em todo objeto: tudo vira "parede" para o Ajustar Piso, para `caffmob.insert_opening`, para `_scene_has_walls` e para `scene_io.is_other_layer_wall` (o editor 2D trata qualquer malha selecionada como parede da outra camada) | `data/properties.py:184-193`; `floor_builder.py:15,24`; `opening_builder.py:50,59`; `ui/panels.py:16`; `walls2d/scene_io.py:98-104` |
| A013 | MEDIUM | Coerência com o legado | A spec R-04 (cortador = 3 × espessura) descreve `caffmob.insert_opening`, que não tem botão; os botões usam `cut_wall`, com o cortador do tamanho exato da parede (faces coplanares) | `_reversa_sdd/domain.md:40,57`; `operators/opening_builder.py`; `doors_windows.py:429-446` |

## Impacto e direção (CRITICAL e HIGH)

**A001 — D-26 sem ação.** O impacto é baixo: as cotas da 002 já são redesenhadas a cada quadro, então RF-31 é
atendido sem código novo. Só fica uma decisão órfã no roadmap. Direção: aceitar como está (decisão de "não mudar") ou
registrar uma ação de verificação manual numa revisão do `actions.md`.

**A010 — Ajustar Piso.**
- **Causa principal (🟢, reproduzida):** o botão `caffmob.adjust_floor` procura paredes por `btm_plane.object_kind
  == 'WALL'`, que é o valor padrão de **todo** objeto (A012).
- As paredes do Home Builder 5, desenhadas pelo construtor ou pelo editor 2D, têm a geometria só no modificador
  Geometry Nodes. A malha delas não tem vértices, então não entram no contorno.
- Sem pontos, o operador cai no quadrado de 5 × 5 m (`floor_builder.py:73-75`). Com outras malhas na cena, o
  contorno sai delas.
- **Causa secundária (🟢 na spec):** mesmo com as paredes certas, o contorno é um **fecho convexo**. Isso enche o
  recorte de salas em L ou U e, nas paredes da camada nova, passa pela face externa.
- **Atenção à spec:** o fecho convexo é a regra **R-02 🟢** de `_reversa_sdd/domain.md`. A correção pedida (respeitar
  os limites da parede) contraria essa regra e precisa de um veredito de spec ("spec-desatualizada") com adendo.
  `_reversa_sdd/operators/edge-cases.md` §1.2 já aponta o problema do L como 🔴.
- **Caminho que funciona hoje:** "Add Floor" do painel Home Builder (`caffmob_walls.add_floor`) segue a face interna
  em polígono ordenado, com sala côncava e tudo. Ele é o que o editor 2D atualiza ao aplicar (`walls2d/apply.py:180-203`).
- **Direção:** registrar com `/reversa-debugger` no contexto `editor-de-paredes` e corrigir com
  `/reversa-debugger-fix`. A correção provável é fazer "Ajustar Piso" usar as cadeias das paredes (o caminho do
  `add_floor`) e deixar de depender de `object_kind`.

**A011 — Portas, janelas e vãos.**
- **Inserção (🟢, pelo código):** os quatro botões ("Porta Simples", "Porta Dupla", "Janela", "Vão Livre") criam uma
  `GeoNodeCage`. É uma caixa sem detalhe, invisível no render, que também é o cortador da booleana. Com "Show Entry Door
  and Window Cages" ligado (padrão), ela aparece como bloco sólido na frente da parede e esconde o furo.
- **Folha e batente:** não há folha, batente nem guarnição. A folha 3D só nasce no "Abrir" da inspeção (D-20 da 002).
- **Fora da parede (🟡, hipótese pelo código):**
  - a espessura é copiada uma vez, sem vínculo com a parede;
  - ao trocar a Direção da parede no editor 2D, a parede passa a crescer para o outro lado e a porta fica onde
    estava, fora da espessura, e o furo corta o ar;
  - na colocação livre, ela usa a espessura padrão da cena.
- **Corte da parede:** sempre ligado e sem opção, com cortador coplanar às faces da parede.
- **Tipos:** não existe "Portal" (passagem com guarnição e sem folha). O pedido é corte por padrão, com opção, para
  janela, porta, portal e vão livre.
- **Direção:** é evolução de produto, não ajuste pequeno. Folha e batente realistas, o tipo Portal, a opção de furar
  e a espessura acompanhando a parede pedem uma feature nova (`/reversa-requirements`), com o furo "por padrão" como
  regra. O deslocamento para fora da parede pode ir antes, como bug (`/reversa-debugger`, contexto `editor-de-paredes`),
  porque nasce da Direção (D-25 da 002).

## Itens verificados que passaram

**Cobertura**
- Os 32 RF têm decisão no roadmap. Os 9 sem citação literal (RF-09, 13, 18, 19, 20, 22, 23, 24, 25) estão cobertos
  por D-10, D-12, D-21 e pelo data-delta.
- As 26 decisões, exceto D-26, têm ação.
- Os 11 cenários Gherkin têm ação e teste de fumaça (exceto o desfazer, A009).

**Consistência**
- Nenhum RF fantasma no roadmap ou no actions, e nenhum D fantasma no actions.
- RN-25, RN-29 e RN-44 citados no roadmap são regras do frameless (`_reversa_sdd/frameless/requirements.md`), não da
  003.
- Os contratos `interfaces/cut-plan-json.md` (JSON 2.1.0 + `machining`) e `interfaces/user-module-file.md`
  aparecem no roadmap (§7, D-10, D-14) e foram implementados como descritos.

**Coerência com o legado**
- Nenhuma decisão da 003 contradiz regra 🟢 de `_reversa_sdd/domain.md` (R-01 a R-10 preservadas, ver
  `legacy-impact.md`).
- Os componentes citados existem: `inspection/pivot_math.py`, `inspection/interference.py`,
  `ops_library.save_cabinet_group_to_user_library`, `GeoNodeCutpart.add_part_modifier`, `CPM_CUTOUT`,
  `part_sources.geometry_records`, `BTM_PT_ObjectProperties`.

**Sanidade do actions**
- 71 ações, todas `[X]`; as dependências apontam para IDs existentes; não há ciclo.
- Nenhuma tarefa `[//]` divide o arquivo alvo com outra da mesma fase.
