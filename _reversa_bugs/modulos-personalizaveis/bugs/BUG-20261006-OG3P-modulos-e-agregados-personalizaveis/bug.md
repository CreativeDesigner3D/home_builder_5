---
schema_version: 1
id: BUG-20261006-OG3P
display_number: 5
title: Módulos instalados não podem ser personalizados nem salvos e não existem agregados
status: open
phase: triaging
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-06

origin:
  type: manual-report
  external_ref: null

area: modulos
module: product_common
feature: 001-addon-moveis-planejados
labels: [spec-gap, change-request, agregados]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_forward/001-addon-moveis-planejados/requirements.md", "_reversa_sdd/product_common/requirements.md"]
  affected_code: ["blendertomob/product_libraries/", "blendertomob/inspection/", "blendertomob/ui/object_properties.py"]
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
# Módulos instalados não podem ser personalizados nem salvos e não existem agregados

## Summary

O titular quer personalizar os módulos instalados (portas, gavetas, puxadores, materiais, divisões internas) e salvar
o resultado como **módulo novo na biblioteca**. Também quer **agregados**: qualquer malha importada (ex.: uma porta
baixada do SketchUp/OBJ) pode ser convertida em agregado de um elemento; o agregado fica colado ao elemento pai, só se
move dentro do espaço do pai, pode se afastar dele ou afundar nele com opção de perfurar; uma malha convertida em
folha de porta ganha propriedades e uma barra que simula a abertura conforme o usuário arrasta.

## Expected Behavior

**spec-gap:** o comportamento acima não está especificado (a 001 previa "criar móveis prontos e guardá-los na
biblioteca", sem detalhes). Pedido do titular, 2026-10-06:
- personalizar portas, gavetas, puxadores, materiais e divisões internas;
- salvar o módulo personalizado como novo módulo na biblioteca;
- agregados: converter malha em agregado preso ao pai, movimento limitado ao pai, afastar/afundar com opção de perfurar;
- folha de porta a partir de malha importada, com barra de abertura.

## Actual Behavior

Existem dimensões editáveis (002), cores de acabamento personalizadas (frameless) e biblioteca de detalhes 2D; não há
salvar módulo personalizado, nem agregados, nem conversão de malha em folha de porta com barra de abertura.

## Steps to Reproduce

1. Inserir um módulo da biblioteca.
2. Tentar trocar puxador/porta por uma malha própria e salvar como novo módulo: não há caminho.

## Evidence

- Relato: `../../intake/relato-20261006-0900.md` (P4) e resposta do titular de 2026-10-06 (agregados).

## Suspected Area

`blendertomob/product_libraries/*` (bibliotecas e biblioteca de produtos), `inspection/` (abertura de frentes, base
para a barra de abertura), `ui/object_properties.py`.

## Acceptance Criteria

- Personalizar portas, gavetas, puxadores, materiais e divisões internas de um módulo inserido.
- Salvar o módulo personalizado como novo item da biblioteca e inseri-lo de novo.
- Converter uma malha importada em agregado de um elemento, com movimento limitado ao pai, afastar/afundar e perfurar.
- Converter uma malha em folha de porta com barra de abertura.

## Traceability

- Specs: `_reversa_forward/001-addon-moveis-planejados/requirements.md`, `_reversa_sdd/product_common/requirements.md` (spec-gap).
- Código: ver Suspected Area.

## Resolution

(preenchida pelo `/reversa-debugger-fix`)

## Agent Notes

- É escopo de feature (vários requisitos novos), não um defeito pontual: o caminho natural é `/reversa-requirements`
  (feature nova) em vez de `/reversa-debugger-fix`. Registrado aqui para rastreabilidade a pedido do titular.
- Prioridade P0 assumida (titular informou só "critical").
