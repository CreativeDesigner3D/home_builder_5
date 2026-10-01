# Contrato: JSON global v2 (projeto, peças e plano de corte)

> Feature `001-addon-moveis-planejados` · Requisitos RF-110, RF-111, RF-113 (issue #20) · Substitui o v1 de
> `blendertomob/cutting/json_exporter.py` (`schema_version: "1.0.0"`).

## Finalidade

Arquivo único para levar a produção do projeto a ferramentas externas (otimizadores de corte, planilhas, seccionadoras
via conversor, ERP da marcenaria) e reimportar a lista de peças/plano sem perda.

## Envelope

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `schema` | string | sim | `"blendertomob.project"` |
| `schema_version` | string semver | sim | `"2.0.0"` |
| `generator` | object | sim | `{name, version, blender_version}` |
| `exported_at` | string ISO 8601 | sim | Com fuso |
| `unit` | string | sim | Sempre `"mm"` no arquivo (independe da unidade da interface) |
| `decimal_precision` | integer | sim | Casas decimais dos valores em mm (padrão 1) |
| `project` | object | sim | Ver abaixo |
| `standard` | object | sim | Snapshot da definição de dimensões usada (ver `dimension-definition.md`, só `uid`, `name`, `version`, `market`) |
| `materials` | array | sim | Materiais referenciados |
| `modules` | array | sim | Módulos |
| `parts` | array | sim | Peças |
| `cut_plan` | object | não | Presente se o plano foi gerado |
| `warnings` | array | sim | Peças incompatíveis com a chapa, sem componente, sem material… |

### `project`

`{ name, uid, rooms: [{uid, name}], client: {name, document?, phone?, email?, address?} | null, company: {name, author, phone?, email?} }`.
`client` é omitido (null) se o usuário exportar com "sem dados do cliente" (RN-21).

### `materials[]`

`{ id, name, kind: "SHEET"|"EDGE", thickness_mm?, brand?, line?, code?, sheet: {width_mm, length_mm, trim_mm: {top, bottom, left, right}}? }`

### `modules[]`

`{ uid, name, room_uid, line: "COZ"|"DOR"|…, library: "FRAMELESS"|"CLOSETS"|"FACE_FRAME"|"BTM", type, width_mm, height_mm, depth_mm,
   location_mm: [x,y,z], rotation_deg: [x,y,z], finish: {component: material_id} }`

### `parts[]`

| Campo | Tipo | Descrição |
|---|---|---|
| `uid` | string | `<module_uid>/<papel>/<índice>` — estável entre recálculos (RN-18) |
| `module_uid` | string \| null | null para geometria livre de fabricação |
| `name` | string | Ex.: "Lateral esquerda" |
| `component` | string | Código do componente (`LAT`, `BAS`, `FUN_INF`…) ou `"UNCLASSIFIED"` |
| `length_mm`, `width_mm`, `thickness_mm` | number | Dimensões de corte |
| `quantity` | integer | ≥ 1 |
| `material_id` | string | → `materials[].id` |
| `grain` | `"NONE"`\|`"LENGTH"`\|`"WIDTH"` | Sentido do veio |
| `finish_id` | string | Acabamento/cor (entra na separação das chapas) |
| `edges` | array[4] | `[{side: 1..4, material_id|null, thickness_mm}]`; lados 1–2 = bordas do comprimento, 3–4 = bordas da largura |
| `source` | `"CUTPART"`\|`"SYNTHETIC"`\|`"FREE_GEOMETRY"` | Origem da peça |
| `limit_status` | `"OK"`\|`"EXCEEDS_WIDTH"`\|`"EXCEEDS_LENGTH"` | Contra o limite do componente |
| `drilling` | array | Vazio no incremento 1 (furação 32 mm no incremento 4) |

### `cut_plan`

`{ algorithm: "guillotine-shelf-nfd", kerf_mm, allow_rotation, respect_grain, stale: bool,
   sheets: [{ id, material_id, finish_id, thickness_mm, width_mm, length_mm, usable: {width_mm, length_mm}, utilization_pct,
              placements: [{part_uid, x_mm, y_mm, rotated: bool}], offcuts: [{x_mm, y_mm, width_mm, length_mm}] }],
   unplaced: [part_uid], stats: {sheets, parts_placed, utilization_pct, waste_m2} }`

## Erros e validação

- O validador (stdlib) rejeita: campo obrigatório ausente, tipo errado, `unit` ≠ `"mm"`, `part.material_id` sem material,
  `placement.part_uid` inexistente, dimensão ≤ 0, `schema_version` maior que o suportado.
- Mensagens apontam o caminho JSON (`parts[12].thickness_mm`).
- Versão `1.x` é aceita na importação e convertida (M-04); a exportação gera só `2.x`.

## Idempotência

- Exportar o mesmo projeto sem mudanças gera o mesmo conteúdo, exceto `exported_at` (ordem estável: módulos por `uid`,
  peças por `uid`).
- Importar e exportar de novo produz um arquivo equivalente (mesmos `uid`, medidas e plano).

## Limites

- Escrita atômica (arquivo temporário + renomear); codificação UTF-8 sem BOM; `ensure_ascii=False`.
- Sem rede: o add-on só lê/grava arquivos locais.
