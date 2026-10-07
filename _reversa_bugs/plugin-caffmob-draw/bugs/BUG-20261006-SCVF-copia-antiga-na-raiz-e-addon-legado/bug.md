---
schema_version: 1
id: BUG-20261006-SCVF
display_number: 3
title: Cópia antiga do plugin na raiz do repositório com o mesmo id e add-on legado nas preferências
status: resolved
phase: patching
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-06

origin:
  type: inspection
  external_ref: null

area: plugin
module: hb_core
feature: 001-addon-moveis-planejados
labels: [instalacao, ambiente]

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
    state: proposed
    evidence: []

traceability:
  specs: ["CLAUDE.md#onde-editar", "_reversa_sdd/deployment.md"]
  affected_code: ["blender_manifest.toml", "__init__.py", "build.py"]
  root_cause:
    state: confirmed
    hypothesis: "A raiz do repositório guarda um blender_manifest.toml de extensão (sobra do commit ff10e80) com o mesmo id do pacote real; o build empacota só blendertomob/, mas o manifesto da raiz e o README fazem a raiz parecer instalável. A entrada legada 'blendertomob' das preferências é dado do usuário de uma instalação antiga."
    causal_path:
      - "blender_manifest.toml (raiz) com id blendertomob"
      - "README.md descreve o manifesto da raiz como o da extensão"
      - "instalação manual a partir do repositório / add-on legado registrado nas preferências"
    evidence:
      - ref: evidence/reproduction.md
        observation: "ZIP do repositório com dois manifestos; raiz não registra (sem ui/); preferências com add-on legado 'blendertomob'"
    code_refs:
      - file: blender_manifest.toml
        symbol: id
        commit: ff10e80
  reproduction_tests:
    - tests/test_packaging.py::EmpacotamentoTest::test_raiz_nao_e_extensao
  regression_tests:
    - tests/test_packaging.py::EmpacotamentoTest::test_manifesto_do_pacote
    - tests/test_packaging.py::EmpacotamentoTest::test_zip_tem_manifesto_na_raiz

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_packaging.py
    purpose: reprodução (manifesto fora do pacote) e regressão (manifesto do pacote e zip instalável)
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: configuration
    artifact: blender_manifest.toml (raiz, removido)
    purpose: a raiz deixa de ser uma extensão com o mesmo id
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: documentation
    artifact: README.md
    purpose: versão mínima 5.2 e instalação só pelo blendertomob.zip
    diff: fix/CHG-003.diff
  - id: CHG-004
    kind: data-repair
    artifact: userpref.blend do titular
    purpose: remover a entrada legada 'blendertomob' (backup verificado, rollback disponível)
    diff: fix/CHG-004.md

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
change_risk:
  classification: baixa
  reasons: ["arquivo removido não é lido pelo build nem pelo Blender ao instalar o zip", "reparo de preferências com backup verificado"]
mitigation: null
---
# Cópia antiga do plugin na raiz do repositório com o mesmo id e add-on legado nas preferências

## Summary

A raiz do repositório é uma extensão completa (`blender_manifest.toml` com `id = "blendertomob"`, nome "Blender to
Mob") com o **código antigo** (Home Builder, sem `walls2d/`, `inspection/`, `move_over/` e sem as correções; 131
arquivos `.py` só existem no pacote novo). O `CLAUDE.md` diz que essa cópia "não empacota", mas ela é instalável:
baixar o ZIP do GitHub ou copiar a pasta do repositório instala a cópia antiga. Além disso, as preferências desta
máquina guardam um add-on legado `blendertomob` (fora das extensões) que falha ao abrir o Blender
(`No module named 'blendertomob'`). No Windows, onde o titular diz que o Home Builder "vem junto", é provável que a
cópia antiga esteja carregada junto da extensão nova.

## Expected Behavior

Só existe um pacote instalável: `blendertomob.zip` gerado por `build.py` a partir de `blendertomob/`
(`CLAUDE.md#onde-editar`). Nada na raiz deve parecer uma extensão.

## Actual Behavior

Raiz com `blender_manifest.toml` e `__init__.py` de extensão; entrada legada `blendertomob` nas preferências.

## Steps to Reproduce

1. Baixar o ZIP do repositório no GitHub (ou clonar) e instalar como extensão/add-on no Blender 5.2.
2. Ver que a versão instalada não tem o Editor de Paredes novo nem as correções.
3. Nesta máquina: abrir o Blender e ver no console `Add-on not loaded: "blendertomob", cause: No module named 'blendertomob'`.

## Evidence

- Achado do registrador em 2026-10-06 (inspeção do repositório e das preferências pelo MCP 9876).

## Suspected Area

`blender_manifest.toml` e `__init__.py` na raiz; preferências do usuário (entrada `blendertomob`).

## Acceptance Criteria

- A raiz do repositório não é instalável como extensão (sem manifesto na raiz) ou a cópia antiga é removida.
- Instalação documentada: só `blendertomob.zip` (ou o nome novo).
- Nenhum add-on legado com o mesmo nome carregado junto.

## Traceability

- Specs: `CLAUDE.md#onde-editar`, `_reversa_sdd/deployment.md`.
- Código: ver Suspected Area.

## Resolution

- **Causa raiz (confirmed):** `blender_manifest.toml` de extensão esquecido na raiz (commit `ff10e80`) com o mesmo id do
  pacote real, e entrada legada `blendertomob` nas preferências do titular. Evidência: `evidence/reproduction.md`.
- **Relação refutada:** a cópia antiga não registra (sem `ui/`), então não causa o erro ao salvar no Windows
  (BUG-20261006-KFAR, relação `caused-by` marcada `rejected` lá).
- **Veredito de spec (decisão do titular, 2026-10-06):** `spec-correta` — `CLAUDE.md#onde-editar` já definia que só
  `blendertomob/` é o pacote; nenhum adendo.
- **resolution_kind:** fixed.

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | test | `tests/test_packaging.py` | reprodução + regressão ([diff](fix/CHG-001.diff)) |
| CHG-002 | configuration | `blender_manifest.toml` (raiz, removido) | raiz deixa de ser extensão ([diff](fix/CHG-002.diff)) |
| CHG-003 | documentation | `README.md` | Blender 5.2+ e instalação só pelo zip ([diff](fix/CHG-003.diff)) |
| CHG-004 | data-repair | preferências do titular | entrada legada removida, backup verificado ([registro](fix/CHG-004.md)) |

**Testes, vermelho → verde:**
- Antes: `test_raiz_nao_e_extensao` FALHOU com `['blender_manifest.toml'] != []`; as duas regressões passaram.
- Depois: `Ran 3 tests … OK`. Suíte completa: 111 testes OK; `blender_smoke` e `blender_002_smoke` OK;
  `blendertomob.zip` validado.

## Agent Notes

- O manifesto removido declarava `[permissions] files` e `platforms`, ausentes no manifesto do pacote: avaliar no bug da
  identidade CAFFMob Draw (BUG-20261006-QAVK).
- O código antigo espelhado na raiz (`*.py`, `operators/`, `product_libraries/`) continua no repositório; removê-lo é
  decisão própria (fora deste bug).

- Remover a cópia da raiz é destrutivo: precisa de aprovação do titular (regra do projeto: não apagar o legado).
- Hipótese de causa do erro ao salvar no Windows (ver relação no bug do editor de paredes).
