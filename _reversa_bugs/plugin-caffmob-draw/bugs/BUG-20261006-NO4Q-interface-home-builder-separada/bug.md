---
schema_version: 1
id: BUG-20261006-NO4Q
display_number: 1
title: Interface legada Home Builder aparece separada do plugin
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
module: ui
feature: 001-addon-moveis-planejados
labels: [spec-gap, unificacao]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/ui/requirements.md#R-01", "_reversa_sdd/architecture.md", "_reversa_sdd/hb_core/requirements.md"]
  affected_code: ["blendertomob/ui/view3d_sidebar.py", "blendertomob/ui/menus.py", "blendertomob/ui/panels.py", "blendertomob/operators/viewport_hud.py", "blendertomob/__init__.py"]
  root_cause:
    state: confirmed
    hypothesis: "A interface legada do Home Builder 5 foi mantida com a própria categoria de painéis (bl_category 'Home Builder') e rótulos em inglês; a camada nova criou outra categoria ('Blender to Mob'). O plugin é um só, mas a interface tem duas identidades."
    causal_path: ["ui/view3d_sidebar.py e product_libraries/*: bl_category = 'Home Builder'", "ui/panels.py e ui/object_properties.py: bl_category = 'Blender to Mob'"]
    evidence:
      - ref: evidence/reproduction.md
        observation: "9 classes com bl_category 'Home Builder', 3 com 'Blender to Mob'; 54 textos 'Home Builder'"
    code_refs:
      - file: blendertomob/ui/view3d_sidebar.py
        symbol: bl_category
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

change_set: []  # change set conjunto registrado em BUG-20261006-QAVK

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
change_risk:
  classification: média
  reasons: ["diff mecânico grande (98 arquivos do pacote, 23 de testes, docs)", "extensão antiga precisa ser desinstalada", "contrato JSON com leitura compatível"]
mitigation: null
---
# Interface legada Home Builder aparece separada do plugin

## Summary

O usuário vê o "Home Builder antigo" ativo ao lado do BlenderToMob. Não é outro add-on: é a interface legada embutida
no próprio plugin (aba "Home Builder" com 96 painéis na barra N, comandos `home_builder_*` em inglês), enquanto a
interface nova fica na aba "Blender to Mob" (9 painéis). O titular quer um plugin só: tudo que era Home Builder deve
fazer parte do plugin novo, nos critérios novos (nome, idioma, organização).

## Expected Behavior

**spec-gap:** nenhuma spec define que a interface do Home Builder deve ser absorvida pela do plugin. Pedido do titular
(2026-10-06): uma única aba e uma única identidade; tudo o que era Home Builder dentro do plugin novo, em português.

## Actual Behavior

Barra N com duas abas concorrentes ("Home Builder" 96 painéis, "Blender to Mob" 9 painéis); 54 ocorrências do texto
"Home Builder" nos `.py`; menus e HUD com rótulos do Home Builder em inglês.

## Steps to Reproduce

1. Instalar `blendertomob.zip` (Blender 5.2).
2. Abrir a barra lateral da Viewport 3D (N).
3. Observar as abas "Home Builder" e "Blender to Mob".

## Evidence

- `evidence/mcp-addons-e-abas-n.txt` (add-ons e abas lidos pelo MCP 9876)
- Relato: `../../intake/relato-20261006-0900.md` (P1)

## Suspected Area

`blendertomob/ui/view3d_sidebar.py` (painéis `HOME_BUILDER_PT_*`), `ui/menus.py`, `ui/panels.py`,
`operators/viewport_hud.py`, rótulos de operadores legados em `operators/*` e `product_libraries/*`.

## Acceptance Criteria

- Uma única aba na barra N, com o nome do plugin; nenhuma aba "Home Builder".
- Nenhum texto "Home Builder" visível na interface (painéis, menus, HUD, mensagens).
- As funções do Home Builder continuam acessíveis dentro do plugin.

## Traceability

- Specs: `_reversa_sdd/ui/requirements.md#R-01`, `_reversa_sdd/architecture.md`, `_reversa_sdd/hb_core/requirements.md` (spec-gap para a unificação).
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

Diffs (na pasta do BUG-20261006-QAVK): `fix/CHG-001.diff`, `fix/CHG-002-006-pacote.diff`, `fix/CHG-007-testes-docs-config.diff`, `fix/CHG-008.md`.

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

- Prioridade P0 assumida pelo registrador: o titular respondeu "critical" para todos sem informar prioridade.
- Depende da decisão de identidade (bug do nome CAFFMob Draw): fazer as duas mudanças juntas evita renomear duas vezes.
