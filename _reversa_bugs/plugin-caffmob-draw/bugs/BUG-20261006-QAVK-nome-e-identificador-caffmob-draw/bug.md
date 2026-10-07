---
schema_version: 1
id: BUG-20261006-QAVK
display_number: 2
title: Nome e identificador do plugin devem ser CAFFMob Draw
status: resolved
phase: patching
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-06

origin:
  type: manual-report
  external_ref: null

area: plugin
module: hb_core
feature: 001-addon-moveis-planejados
labels: [spec-gap, change-request, identidade]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: 
  - bug: BUG-20261006-NO4Q
    type: related-to
    state: confirmed
    evidence:
      - ref: evidence/reproduction.md
        observation: "mesma causa de identidade e mesmos arquivos; corrigidos juntos" 

traceability:
  specs: ["_reversa_sdd/architecture.md", "_reversa_sdd/soul.md"]
  affected_code: ["blendertomob/blender_manifest.toml", "blendertomob/__init__.py", "build.py", "blendertomob/data/i18n.py"]
  root_cause:
    state: confirmed
    hypothesis: "A identidade nunca foi definida como CAFFMob Draw: manifesto, pasta, prefixos de operadores e propriedades herdaram 'blendertomob'/'btm' da camada nova e 'home_builder'/'hb_' do Home Builder 5. As propriedades com esses nomes estão gravadas nos .blend (bibliotecas do pacote e projetos)."
    causal_path: ["blender_manifest.toml id/name", "pasta blendertomob/", "~400 bl_idname com 14 prefixos", "~40 propriedades registradas em bpy.types gravadas nos .blend"]
    evidence:
      - ref: evidence/reproduction.md
        observation: "contagens por prefixo; 20 de 21 bibliotecas .blend com dados nos nomes antigos"
    code_refs:
      - file: blendertomob/blender_manifest.toml
        symbol: id
        commit: f6d9188
  reproduction_tests:
    - tests/test_identity.py::IdentidadeTest::test_pacote_e_manifesto
    - tests/test_identity.py::IdentidadeTest::test_sem_nome_antigo_visivel
    - tests/test_identity.py::IdentidadeTest::test_operadores_com_prefixo_caffmob
    - tests/test_identity.py::IdentidadeTest::test_uma_aba_so
  regression_tests:
    - tests/test_identity.py::IdentidadeTest::test_migracao_copia_so_quando_vazio
    - tests/blender_identity_smoke.py

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_identity.py, tests/blender_identity_smoke.py
    purpose: reprodução (manifesto, textos, prefixos, aba única) e regressão (migração, aba, operadores, MENU_ID, salvar/reabrir, JSON, desregistro)
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: blendertomob/ → caffmob_draw/ (git mv), blender_manifest.toml, build.py
    purpose: identificador caffmob_draw e nome CAFFMob Draw
    diff: fix/CHG-002-006-pacote.diff
  - id: CHG-003
    kind: code
    artifact: 402 bl_idname de operadores e referências
    purpose: prefixos caffmob*
    diff: fix/CHG-002-006-pacote.diff
  - id: CHG-004
    kind: code
    artifact: bl_category, textos visíveis, menus_frameless.py
    purpose: aba única CAFFMob Draw; registro do menu das laterais acabadas (achado da regressão)
    diff: fix/CHG-002-006-pacote.diff
  - id: CHG-005
    kind: migration
    artifact: caffmob_draw/compat_identity.py
    purpose: dados do usuário, biblioteca de assets e aviso da extensão antiga
    diff: fix/CHG-002-006-pacote.diff
  - id: CHG-006
    kind: api-contract
    artifact: cutting/json_exporter.py, standards/io_json.py
    purpose: formato caffmob_draw.* com leitura compatível
    diff: fix/CHG-002-006-pacote.diff
  - id: CHG-007
    kind: documentation
    artifact: tests/, build.py, configs, CLAUDE.md, README.md, docs/usuario, docs/rag
    purpose: caminhos e nome novos
    diff: fix/CHG-007-testes-docs-config.diff
  - id: CHG-008
    kind: data-repair
    artifact: Blender do titular (MCP 9876)
    purpose: backup das preferências, troca blendertomob → caffmob_draw, migração conferida
    diff: fix/CHG-008.md
  - id: CHG-009
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261006-QAVK-v001.md
    purpose: adendo spec-gap da identidade
    diff: ../../../../_reversa_sdd/addenda/bug-BUG-20261006-QAVK-v001.md

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
change_risk:
  classification: média
  reasons: ["diff mecânico grande (98 arquivos do pacote, 23 de testes, docs)", "extensão antiga precisa ser desinstalada", "contrato JSON com leitura compatível"]
mitigation: null
---
# Nome e identificador do plugin devem ser CAFFMob Draw

## Summary

O plugin deve se chamar **CAFFMob Draw** em toda referência: nome exibido, identificador técnico (id da extensão,
pasta, prefixos de operadores e propriedades) e documentação, sem nenhuma menção a "Home Builder" (decisão do
titular, 2026-10-06: "tudo, nome que aparece, identificador … deixar um nome só sempre").

## Expected Behavior

**spec-gap:** a identidade "CAFFMob Draw" não está em nenhuma spec. Pedido do titular: nome e identificador únicos
"CAFFMob Draw" em manifesto, interface, operadores (`btm.*`, `home_builder*`), propriedades, pasta do pacote, build e
documentação.

## Actual Behavior

Manifesto `id = "blendertomob"`, `name = "Blender to Mob"`; pasta `blendertomob/`; prefixos `btm.`/`BTM_` e
`home_builder*`; aba "Blender to Mob"; textos "BlenderToMob" e "Home Builder".

## Steps to Reproduce

1. Ler `blendertomob/blender_manifest.toml`.
2. Instalar e abrir Preferências › Add-ons e a barra N.

## Evidence

- Relato: `../../intake/relato-20261006-0900.md` (P2)

## Suspected Area

`blendertomob/blender_manifest.toml`, `blendertomob/__init__.py`, `build.py`, todos os `bl_idname`/`bl_category`,
nomes de propriedades registradas (`btm_*`, `home_builder`), `data/i18n.py`, `docs/`.

## Acceptance Criteria

- Manifesto com nome "CAFFMob Draw" e id novo (a definir no fix, ex.: `caffmob_draw`).
- Nenhuma ocorrência de "Blender to Mob", "BlenderToMob" ou "Home Builder" na interface.
- Arquivos `.blend` salvos com a versão antiga continuam abrindo (migração das propriedades `btm_*`/`home_builder`).

## Traceability

- Specs: `_reversa_sdd/architecture.md`, `_reversa_sdd/soul.md` (spec-gap para a identidade).
- Código: ver Suspected Area.

## Resolution

- **Causa raiz (confirmed):** duas identidades na interface (abas "Home Builder" e "Blender to Mob") e nomes herdados
  no manifesto, na pasta, em 402 operadores e em 40 textos. Evidência: `evidence/reproduction.md`.
- **Estratégia:** fase A escolhida pelo titular (tudo visível + identificador; dados gravados mantêm os nomes internos;
  fase B com migração fica para um bug novo).
- **Veredito de spec (decisão do titular, 2026-10-06):** `spec-gap` → adendo
  `_reversa_sdd/addenda/bug-BUG-20261006-QAVK-v001.md` (CHG-009), registrado junto com o diff do código.
- **resolution_kind:** fixed.

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | test | `tests/test_identity.py`, `tests/blender_identity_smoke.py` | reprodução + regressão |
| CHG-002 | code | `blendertomob/` → `caffmob_draw/`, manifesto, build | identificador e nome |
| CHG-003 | code | 402 `bl_idname` + referências | prefixos `caffmob*` |
| CHG-004 | code | `bl_category`, 40 textos, `menus_frameless.py` | aba única; menu das laterais acabadas registrado |
| CHG-005 | migration | `caffmob_draw/compat_identity.py` | dados do usuário, biblioteca de assets, aviso |
| CHG-006 | api-contract | `json_exporter.py`, `io_json.py` | `caffmob_draw.*`, leitura compatível |
| CHG-007 | documentation | testes, build, configs, `CLAUDE.md`, `README.md`, docs | caminhos e nome |
| CHG-008 | data-repair | Blender do titular | troca de extensão com backup |
| CHG-009 | specification | adendo `bug-BUG-20261006-QAVK-v001` | identidade especificada |

Diffs: `fix/CHG-001.diff`, `fix/CHG-002-006-pacote.diff`, `fix/CHG-007-testes-docs-config.diff`, `fix/CHG-008.md`.

**Testes, vermelho → verde:**
- Antes: `test_pacote_e_manifesto` e `test_uma_aba_so` falharam e `test_migracao_copia_so_quando_vazio` deu erro (pacote
  inexistente); contra o pacote antigo, `test_sem_nome_antigo_visivel`, `test_operadores_com_prefixo_caffmob` e
  `test_uma_aba_so` falharam; a fumaça falhou (`No module named 'caffmob_draw'`).
- Depois: `test_identity` 5/5 OK; suíte 116 OK; `blender_identity_smoke` e as 5 fumaças OK; teste de interface 13/13 OK;
  `check_api` OK; `caffmob_draw.zip` validado.
- Ao vivo (MCP): só `bl_ext.user_default.caffmob_draw`; uma aba "CAFFMob Draw" (35 painéis); biblioteca de assets
  renomeada; arquivo salvo com a versão antiga abre com paredes, pé-direito, MENU_ID e porta de ambiente funcionando.


## Agent Notes

- Fase B (bug novo a registrar): renomear propriedades gravadas (`home_builder`, `hb_*`, `btm_*`), `MENU_ID`/menus
  `HOME_BUILDER_MT_*`, nomes de classes e painéis, chaves `IS_*`, com migração automática de projetos e das bibliotecas
  `.blend`; tradução dos rótulos legados para o português.
- Achado da regressão: `HOME_BUILDER_MT_applied_end_commands` nunca era registrado (corrigido em CHG-004).

- Mudar o `id` e os nomes das propriedades registradas quebra a leitura de arquivos antigos se não houver migração
  (propriedades salvas nos objetos e cenas). O fix precisa de um plano de migração aprovado pelo titular.
- Prioridade P0 assumida (ver bug 1).
