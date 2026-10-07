---
schema_version: 1
id: BUG-20261007-A2G7
display_number: 6
title: Ajustar Piso ignora as paredes do editor e do construtor
status: resolved
phase: delivering
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
labels: [piso, spec-desatualizada-provavel]

change_risk:
  classification: média
  reasons: ["muda só o comportamento do botão Ajustar Piso", "sem dados salvos nem contrato externo", "reversível pelo desfazer"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "3/3"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261007-YIMY
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/domain.md#2.1 Regras de Paredes e Piso", "_reversa_sdd/addenda/bug-BUG-20261007-A2G7-v001.md", "_reversa_sdd/geometry/requirements.md", "_reversa_sdd/operators/edge-cases.md#1.2"]
  affected_code: ["caffmob_draw/operators/floor_builder.py", "caffmob_draw/geometry/mesh_gen.py", "caffmob_draw/data/properties.py", "caffmob_draw/walls2d/apply.py"]
  root_cause:
    state: confirmed
    hypothesis: "O operador caffmob.adjust_floor identifica paredes por btm_plane.object_kind == 'WALL' (padrão de todo objeto) e lê os vértices da malha; as paredes do Home Builder 5 (construtor e editor 2D) têm a geometria só no Geometry Nodes (malha vazia), então nenhum ponto entra e o operador cai no quadrado fixo de 5 x 5 m. Com paredes da camada nova, o contorno é fecho convexo dos vértices inferiores (R-02), que cobre recortes e passa pela face externa."
    causal_path:
      - "operators/floor_builder.py:14-25 seleciona objetos por object_kind == 'WALL' (default do enum em data/properties.py:184-193)"
      - "geometry/mesh_gen.py:136-137 ignora malhas sem vértices (todas as paredes GeoNodeWall)"
      - "geometry/mesh_gen.py:146-147 devolve False com menos de 3 pontos"
      - "operators/floor_builder.py:73-75 gera o quadrado de 5 x 5 m"
      - "geometry/mesh_gen.py:148 fecho convexo quando há pontos (camada nova): cobre o recorte e usa a face externa"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sala do editor 4 x 3 m e sala em L geram piso 5 x 5 m; paredes HB com 0 vértices; balcão com object_kind WALL; L da camada nova com área 15,06 m² (fecho convexo, face externa)"
    code_refs:
      - {file: caffmob_draw/operators/floor_builder.py, symbol: BTM_OT_AdjustFloor, commit: f6d9188}
      - {file: caffmob_draw/geometry/mesh_gen.py, symbol: generate_floor_from_walls, commit: f6d9188}
      - {file: caffmob_draw/data/properties.py, symbol: "BTM_PG_InsertionPlane.object_kind (Object.btm_plane)", commit: f6d9188}
  reproduction_tests: ["tests/blender_bug_A2G7_floor.py#1", "tests/blender_bug_A2G7_floor.py#2"]
  regression_tests: ["tests/blender_bug_A2G7_floor.py#3", "tests/blender_bug_A2G7_floor.py#4", "tests/test_floor_outline.py"]

spec_verdict: spec-desatualizada

change_set:
  - id: CHG-001
    kind: code
    artifact: caffmob_draw/geometry/floor_outline.py
    purpose: contorno do piso pela face interna (Python puro)
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/operators/floor_builder.py
    purpose: paredes pelas marcas reais, um polígono por sala, piso sem deslocamento
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/_bootstrap.py
    purpose: importar caffmob_draw.geometry sem o Blender no teste unitário
    diff: fix/CHG-003.diff
  - id: CHG-004
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261007-A2G7-v001.md
    purpose: adendo à R-02 (face interna, polígono ordenado)
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Ajustar Piso ignora as paredes do editor e do construtor

## Summary

O botão "Ajustar Piso" (painel CAFFMob Draw, CONSTRUTOR) não segue as paredes criadas pelo editor de paredes 2D nem
pelo construtor ("Desenhar Paredes"). Numa sala 4 x 3 m feita pelo editor, ele gera um piso 5 x 5 m centrado na origem.

## Expected Behavior

Spec efetiva: `_reversa_sdd/domain.md` R-02 (🟢) diz que o piso se ajusta ao perímetro interno das paredes, calculado
por **fecho convexo** dos vértices inferiores. O titular espera que o piso respeite os limites das paredes, inclusive em
salas em L ou U. O fecho convexo não atende salas côncavas (`_reversa_sdd/operators/edge-cases.md` §1.2 já marca isso
como 🔴), então a correção provavelmente exige veredito `spec-desatualizada` com adendo à R-02.

## Actual Behavior

Piso de 5 x 5 m na origem, sem relação com as paredes (ver evidência). O "Add Floor" do painel Home Builder
(`caffmob_walls.add_floor`) segue a face interna corretamente.

## Steps to Reproduce

1. Arquivo novo; desenhar uma sala 4 x 3 m no Editor de Paredes e clicar OK (ou "Desenhar Paredes").
2. CONSTRUTOR › "Ajustar Piso".
3. Observar o piso 5 x 5 m centrado na origem.

## Evidence

- `evidence/reproduction.md` (cápsula de reprodução: 3 casos, determinístico)
- `evidence/reproducao-ajustar-piso.md` e `.py` (sala 4 x 3 m do editor)
- `evidence/reproducao-sala-L-construtor.py` (sala em L do editor + balcão na cena)
- `evidence/reproducao-sala-L-camada-nova.py` (sala em L de paredes da camada nova, fecho convexo)
- Relato bruto: `../../intake/relato-20261007-1200.md`

## Suspected Area

Hipóteses (não confirmadas; o fix decide):
1. `operators/floor_builder.py:14-25` busca paredes por `btm_plane.object_kind == 'WALL'`, padrão de **todo** objeto
   (`data/properties.py:184-193`), e não olha `IS_WALL_BP`.
2. Paredes do Home Builder 5 têm a geometria só no Geometry Nodes: `mesh_gen.generate_floor_from_walls`
   (`geometry/mesh_gen.py:121-171`) lê `data.vertices` (vazio) e não acha pontos; cai no quadrado 5 x 5 m
   (`floor_builder.py:73-75`).
3. Fecho convexo (`mesh_gen.py:148`, R-02) enche salas em L/U; nas paredes da camada nova passa pela face externa.
4. A localização de um piso antigo fica velha (`floor_builder.py:87-89`) e o refresh do editor 2D só atualiza pisos
   `IS_FLOOR_BP` (`walls2d/apply.py:180-203`).

## Acceptance Criteria

- Sala 4 x 3 m do editor de paredes: "Ajustar Piso" gera o piso pela face interna (4 x 3 m), alinhado às paredes.
- Sala em L: o piso não cobre o recorte.
- Objetos que não são paredes (módulos, portas, pisos) não entram no contorno.
- Ajustar de novo depois de mudar as paredes atualiza o mesmo piso, sem deslocamento.

## Traceability

- Specs: `_reversa_sdd/domain.md#2.1` (R-02 🟢), `_reversa_sdd/geometry/requirements.md`, `_reversa_sdd/operators/edge-cases.md#1.2`
- Código afetado: `operators/floor_builder.py`, `geometry/mesh_gen.py`, `data/properties.py`, `walls2d/apply.py`
- Testes: nenhum ainda

## Resolution

**Causa raiz (confirmed):** `caffmob.adjust_floor` reconhecia parede por `btm_plane.object_kind == 'WALL'` (padrão de
todo objeto) e lia os vértices da malha; as paredes do Home Builder 5 têm a geometria só no Geometry Nodes (malha vazia),
então nenhum ponto entrava e o operador caía no quadrado fixo de 5 x 5 m. Com paredes da camada nova, o fecho convexo
(R-02) cobria o recorte da sala em L e passava pela face externa.

**Veredito de spec:** `spec-desatualizada` (aprovado por Leonardo Lima em 2026-10-07), adendo
`_reversa_sdd/addenda/bug-BUG-20261007-A2G7-v001.md`.

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/geometry/floor_outline.py` | contorno pela face interna (puro) |
| CHG-002 | code | `caffmob_draw/operators/floor_builder.py` | paredes pelas marcas reais; um polígono por sala; matriz identidade; retângulo só sem sala fechada |
| CHG-003 | test | `tests/_bootstrap.py` | importar `caffmob_draw.geometry` sem o Blender |
| CHG-004 | specification | `_reversa_sdd/addenda/bug-BUG-20261007-A2G7-v001.md` | adendo à R-02 |

Diffs: `fix/CHG-001.diff`, `fix/CHG-002.diff`, `fix/CHG-003.diff`; adendo no caminho acima.

**Testes (vermelho → verde):**
- Antes (gate 1): `tests/test_floor_outline.py` → `ImportError` (módulo inexistente);
  `tests/blender_bug_A2G7_floor.py` → `AssertionError: ((-2.5, -2.5), (2.5, 2.5), 25.0)` no caso 1.
- Depois (gate 2): `test_floor_outline` 6/6 OK; `blender_bug_A2G7_floor: OK` (4 casos); suíte unitária completa OK;
  `blender_smoke`, `blender_002_smoke`, `blender_legacy_smoke`, `blender_003_customize_smoke` OK; `ruff` e
  `check_api.py` limpos.
- Reprodução: casos 1 e 2 de `tests/blender_bug_A2G7_floor.py`. Regressão: casos 3 e 4 e `tests/test_floor_outline.py`.

## Agent Notes

- Registrado a partir do achado A010 (e A012) de `_reversa_forward/003-modulos-agregados-reposicionar/audit/cross-check.md`.
- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (high/P1).
- O padrão `object_kind = 'WALL'` também afeta `operators/opening_builder.py:50,59`, `ui/panels.py:16`
  (`_scene_has_walls`) e `walls2d/scene_io.py:98-104` (`is_other_layer_wall`); corrigir sem quebrar paredes da camada
  nova (`btm_wall_segments`). Mudar o padrão do enum afeta arquivos salvos: avaliar migração.
- Proposta de taxonomia: incluir `003-modulos-agregados-reposicionar` em `feature`.
