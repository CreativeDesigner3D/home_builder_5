# `hb_closets_OT_place_starter._position_on_wall` — encaixe do starter na parede

> Arquivo: `blendertomob/product_libraries/closets/operators/ops_closet.py:795-947` (+ `_corner_insets :724-755`,
> `_reposition_with_offsets :694-722`, `_place_cage_on_wall :949-972`, `_update_place_on_front :768-793`).
> Usa `PlacementMixin.find_placement_gap_by_side` de `hb_placement` (fora do módulo). Confiança geral: 🟢 CONFIRMADO.

## Fluxograma

```mermaid
flowchart TD
    A([_position_on_wall wall]) --> C{starter de canto L?}
    C -- sim --> C1["parenta à parede; z = mount_z"]
    C1 --> C2{hit.x ≤ comprimento/2?}
    C2 -- sim --> C3["origem na ponta esquerda, rot 0°"]
    C2 -- não --> C4["origem na ponta direita, rot −90°"]
    C3 & C4 --> CZ([sem gap / sem cotas])
    C -- não --> D["parenta à parede (matrix_parent_inverse = I)<br/>z = mount_z (suspenso: hanging_top − altura)"]
    D --> E["_update_place_on_front: lado da parede<br/>histerese 0,05 m; em vista de planta projeta no piso"]
    E --> F[[find_placement_gap_by_side]]
    F --> F1{gap encontrado?}
    F1 -- não --> F2["gap = parede inteira; snap_x = cursor − W/2"]
    F1 -- sim --> G
    F2 --> G["_corner_insets: 1/2 in em canto INTERNO<br/>(só se a borda do gap é a ponta da parede)"]
    G --> H{offset digitado esq/dir?}
    H -- sim --> H1[[_reposition_with_offsets]] --> Z([fim])
    H -- não --> I["gap_start += recuo esq; gap_end −= recuo dir<br/>gap_width = max(gap, 1 in)"]
    I --> J["zonas de snap com histerese:<br/>canto: engage = max(W/2, 6 in), release = +1 in<br/>centro: engage 4 in, release 5 in"]
    J --> K{fill_mode?}
    K -- sim --> K1["largura = gap_width (auto_bay_qty recalcula vãos)<br/>x = gap_start"]
    K -- não --> K2{snap}
    K2 -- LEFT --> L1[x = gap_start]
    K2 -- RIGHT --> L2[x = gap_end − W]
    K2 -- CENTER --> L3["x = gap_start + (gap − W)/2"]
    K2 -- nenhum --> L4["x = clamp(snap_x, gap_start, gap_end − W)"]
    K1 & L1 & L2 & L3 & L4 --> M[[_place_cage_on_wall]]
    M --> M1{frente da parede?}
    M1 -- sim --> M2["loc = (x, 0), rot 0"]
    M1 -- não --> M3["loc = (x + W, espessura), rot π"]
    M2 & M3 --> N[cotas GPU de largura e folgas] --> Z
```

## Regras

- 🟢 `auto_bay_qty(width) = clamp(ceil(width / 42 in), 1, 9)` (`types_closets.py:1749-1754`): nenhum vão passa de 42 in (1066,8 mm).
- 🟢 Recuo automático de 1/2 in (12,7 mm) em cantos internos (`const_closets.py:73`, `ops_closet.py:868-885`); um offset digitado
  substitui o recuo só do seu lado.
- 🟢 Offsets em *fill mode* **aparam** a largura; largura digitada é preservada e apenas deslocada (`:694-722`).
- 🟢 Ilhas fora da parede: folgas medidas por raios em planta (3 por face) até paredes/armários; *detentes* em 30/36/42/48 in com
  janela de 1 in; Shift desliga (`ops_closet.py:132-167, 1025-1052`).
- 🟢 Após confirmar, `_detect_corner_closet_neighbor` (`:170-288`) procura starters em paredes perpendiculares (90° ± 5°, faixa de
  altura sobreposta, canto a ≤ 8 in, borda a ≤ 1 in) e abre `set_corner_clearance` (folga default 12 in + pontes).
