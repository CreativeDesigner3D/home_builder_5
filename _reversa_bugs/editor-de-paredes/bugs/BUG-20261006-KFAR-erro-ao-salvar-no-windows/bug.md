---
schema_version: 1
id: BUG-20261006-KFAR
display_number: 4
title: Erro ao salvar no Windows com o editor de paredes e o construtor de paredes
status: open
phase: triaging
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-06

origin:
  type: manual-report
  external_ref: null

area: paredes
module: wall_editor
feature: 002-editor-parede-mover-sobre
labels: [windows, ambiente]

visibility: normal
security_suspected: false

reproduction:
  classification: environment-dependent
  rate: "0/2 (Linux)"
  suspected_triggers: []

blocking: []

relationships: 
  - bug: BUG-20261006-SCVF
    type: caused-by
    state: rejected
    evidence:
      - ref: ../../../plugin-caffmob-draw/bugs/BUG-20261006-SCVF-copia-antiga-na-raiz-e-addon-legado/evidence/reproduction.md
        observation: "a cópia antiga da raiz não registra (sem ui/), então não pode rodar junto da extensão; com só a extensão nova, salvar funciona" 

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["blendertomob/walls2d/ops_editor.py", "blendertomob/walls2d/window.py", "blendertomob/inspection/save_guard.py", "blendertomob/operators/walls.py"]
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
# Erro ao salvar no Windows com o editor de paredes e o construtor de paredes

## Summary

Num computador com Windows (Blender 5.2.0, Home Builder "vindo junto na instalação"), abrir o editor de paredes e
salvar retorna erro; o construtor de paredes também. Sem texto do erro disponível.

## Expected Behavior

Salvar o arquivo (Ctrl+S) com o editor aberto ou depois do OK grava sem erro; o editor trabalha em rascunho e o OK
aplica em um passo de desfazer (RN-16 da 002). O salvar fechado das portas/gavetas (`inspection/save_guard`) não
deve falhar.

## Actual Behavior

No Windows: erro ao salvar (texto desconhecido). No Linux (2026-10-06, MCP 9876, extensão recém-instalada):
salvar com o editor aberto e salvar depois do OK funcionaram, sem `Traceback`.

## Steps to Reproduce

1. Windows, Blender 5.2.0, plugin instalado como no computador do titular.
2. Abrir o Editor de Paredes (ou usar "Desenhar Paredes").
3. Salvar o arquivo.

## Evidence

- Relato: `../../intake/relato-20261006-0900.md` (P3).
- Linux: 2 tentativas sem erro (salvar com o editor aberto; salvar após OK).

## Suspected Area

`inspection/save_guard.py` (handlers `save_pre`/`save_post`), `walls2d/window.py` (área do editor), operadores
legados `home_builder_walls.*`; conflito com a cópia antiga do plugin carregada junto (hipótese).

## Acceptance Criteria

- No Windows, salvar com o editor aberto, após OK e após o construtor 3D grava sem erro.
- O console do Windows não mostra `Traceback` ao salvar.

## Traceability

- Specs: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16`, `_reversa_sdd/wall_editor/requirements.md`.
- Código: ver Suspected Area.

## Resolution

(preenchida pelo `/reversa-debugger-fix`)

## Agent Notes

- Não reproduzido no Linux. Para o fix: pedir ao titular o console do Windows (Janela › Alternar Console do Sistema)
  ou o `%TEMP%\blender.crash.txt`, e a lista de add-ons em Preferências › Add-ons do Windows.
- Hipótese principal (`proposed`): cópia antiga/add-on legado `blendertomob` carregado junto da extensão nova
  (ver relação).
- Prioridade P0 assumida (titular informou só "critical").
