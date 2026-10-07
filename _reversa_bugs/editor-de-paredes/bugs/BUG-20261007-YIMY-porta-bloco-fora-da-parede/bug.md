---
schema_version: 1
id: BUG-20261007-YIMY
display_number: 7
title: Porta e janela inseridas viram bloco liso com a espessura fora da parede
status: open
phase: triaging
severity: high
priority: P1
created: 2026-10-07
updated: 2026-10-07

origin:
  type: inspection
  external_ref: null

area: paredes
module: operators
feature: 002-editor-parede-mover-sobre
labels: [aberturas, portas, janelas]

visibility: normal
security_suspected: false

reproduction:
  classification: unknown
  rate: "0/0"
  suspected_triggers: ["trocar a Direção da parede no editor 2D depois de inserir a porta", "espessura da parede alterada depois da inserção"]

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/domain.md#2.2 Regras de Snapping e Movimentação de Aberturas", "_reversa_sdd/hb_core/design.md", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["caffmob_draw/operators/doors_windows.py", "caffmob_draw/hb_types.py", "caffmob_draw/hb_props.py", "caffmob_draw/walls2d/apply.py", "caffmob_draw/walls2d/model.py"]
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---
# Porta e janela inseridas viram bloco liso com a espessura fora da parede

## Summary

Ao inserir uma porta (também janela e vão livre) aparece um bloco sem detalhe, com a espessura para fora da parede,
em vez de a abertura ficar dentro da parede, furando-a.

## Expected Behavior

Spec efetiva: `_reversa_sdd/domain.md` R-04 (🟢): a abertura fica presa à parede hospedeira, herda a rotação e a
espessura do segmento, e o cortador booleano passa toda a espessura (3 x a espessura) para um furo limpo. A abertura
deve ficar dentro da espessura da parede e o furo deve aparecer. A R-04 descreve `caffmob.insert_opening`, que não tem
botão na interface; os botões usam outro caminho (`doors_windows.py`), por isso a correção pode exigir veredito de spec.

Fora do escopo deste bug (pedido de produto, vai para feature própria): porta/janela realistas com folha e batente,
tipo "Portal" e a opção "furar a parede" ligada por padrão.

## Actual Behavior

Bloco sólido sem detalhe (a gaiola que serve de cortador, mostrada por "Show Entry Door and Window Cages"), com a
espessura do lado de fora da parede (relato do titular). Ainda não reproduzido aqui com janela.

## Steps to Reproduce

1. Desenhar paredes (editor de paredes ou "Desenhar Paredes").
2. Painel CAFFMob Draw › Aberturas & Vãos › "Porta Simples" e clicar na parede.
3. Observar o bloco e a posição em relação à espessura. Variante suspeita: depois, mudar a Direção da parede no editor 2D e dar OK.

## Evidence

- `evidence/analise-do-codigo.md` (caminho do código e hipóteses)
- Relato bruto: `../../intake/relato-20261007-1200.md`

## Suspected Area

Hipóteses (não confirmadas; o fix reproduz e decide):
1. A gaiola de inserção é o próprio cortador (`doors_windows.py:732-783`, `hb_types.py:539-552`), exibida sólida por
   padrão (`hb_props.py:498`): é o "bloco sem detalhe".
2. Espessura copiada uma vez, sem vínculo (`doors_windows.py:745, 825-826`); trocar a Direção no editor 2D inverte o lado
   da espessura (`walls2d/model.py:173-181`, `apply.py:106, 126-140`) e a porta fica fora.
3. Cortador coplanar às faces da parede (`cut_wall`, `doors_windows.py:429-446`), contra a R-04 (3 x espessura).

## Acceptance Criteria

- Porta, porta dupla, janela e vão livre inseridos ficam dentro da espessura da parede e o furo aparece de face a face.
- Mudar a Direção ou a espessura da parede no editor 2D mantém a abertura dentro da parede e o furo limpo.
- O cortador não deixa película (faces coplanares).

## Traceability

- Specs: `_reversa_sdd/domain.md#2.2` (R-04 a R-08 🟢), `_reversa_sdd/hb_core/design.md`, `_reversa_sdd/wall_editor/requirements.md`
- Código afetado: `operators/doors_windows.py`, `hb_types.py`, `hb_props.py`, `walls2d/apply.py`, `walls2d/model.py`
- Testes: nenhum ainda

## Resolution

(preenchida pelo `/reversa-debugger-fix`)

## Agent Notes

- Registrado a partir dos achados A011 e A013 de `_reversa_forward/003-modulos-agregados-reposicionar/audit/cross-check.md`.
- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (high/P1).
- Decisão do titular: porta/janela realistas, tipo Portal e "furar a parede" ligado por padrão com opção vão para
  feature nova (`/reversa-requirements`), não para este bug. Não ampliar a correção para isso.
- Proposta de taxonomia: incluir `003-modulos-agregados-reposicionar` em `feature`.
