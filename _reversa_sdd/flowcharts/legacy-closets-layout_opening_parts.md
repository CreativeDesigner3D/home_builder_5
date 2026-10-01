# `ClosetStarter._layout_opening_parts` — portas, gavetas, prateleiras, varões e nichos

> Arquivo: `blendertomob/product_libraries/closets/types_closets.py:691-904` (+ regeneradores `:1011-1183`,
> `_distribute_front_heights :1813-1831`, `drawer_boxes_closets.size_box :65-85`, `_position_front_pull :908-1009`).
> Confiança geral: 🟢 CONFIRMADO.

## Fluxograma

```mermaid
flowchart TD
    A([_layout_opening_parts opening, width, depth, interior_h]) --> R[Regeneradores: reconcilia filhos com idprops]
    R --> R1["_reconcile_adj_shelves (hb_adj_shelf_qty)"]
    R --> R2["_reconcile_doors (hb_door_swing: LEFT/RIGHT=1, DOUBLE=2;<br/>porta de vão inteiro suprime portas da opening)"]
    R --> R3["_reconcile_drawers (hb_drawer_qty → frentes + caixas)"]
    R --> R4["_reconcile_cubbies (cols−1 divisões, rows−1 prateleiras)"]
    R1 & R2 & R3 & R4 --> OV["Sobreposição meia-espessura:<br/>lo=ro=(pt−gap)/2 ; to=bo=(st−gap)/2<br/>front_y = −depth − 1/8 in (FRONT) | +1/8 in (BACK)"]
    OV --> L{para cada filho}
    L -- FIXED_SHELF --> FS["z = offset (ou interior_h − offset se anchor_top)<br/>clamp 0..interior_h−st"]
    L -- ROD --> RD["z clamp [R, interior_h−R] (R=1 in)<br/>y = −min(12 in, max(depth−R, R))<br/>perfil oval/redondo + acabamento + cabides"]
    L -- outro papel --> GR[agrupa por papel]
    GR --> ADJ["Reguláveis: spacing = interior_h/(n+1)<br/>z_i = spacing·(i+1), clamp"]
    GR --> DOOR["Portas: full = width + lo + ro<br/>2 folhas → leaf = (full − gap)/2<br/>altura = interior_h + to + bo<br/>x_i = −lo + i·(leaf+gap)"]
    DOOR --> DOOR2[estilo de frente → stash fechado → puxador → aplica hb_door_open]
    GR --> DRW["Gavetas: span = interior_h + to + bo<br/>avail = span − (n−1)·gap"]
    DRW --> DH[[_distribute_front_heights avail]]
    DH --> DB["por frente (baixo→cima): grava hb_front_height<br/>Length = width+lo+ro, Width = dh"]
    DB --> BOX{sistema de caixa}
    BOX -- NONE --> BN[caixa oculta]
    BOX -- WOOD --> BW["h = max(dh − 1,25 in, 2 in)<br/>d = max(depth − 0,5 in, 2 in)"]
    BOX -- AVANTECH/METABOX --> BS["altura padrão = maior que cabe em dh<br/>comprimento de corrediça = maior ≤ depth<br/>(Illumination: depth − 12,7 mm)"]
    BW & BS --> BP["caixa: x = 1/2 in; largura = width − 2·1/2 in<br/>z = max(z,0) + 1/2 in; y ancorado na face"]
    BP --> TR["curso = min(box_d, 12 in); stash; aplica hb_drawer_open"]
    BN --> TR
    TR --> NXT["z += dh + gap"]
    GR --> CUB["Nichos: cell_w = (width − nd·st)/cols<br/>cell_h = (interior_h − ns·st)/rows"]
```

## `_distribute_front_heights` 🟢 `types_closets.py:1813-1831`

- Frentes travadas (`hb_front_locked=1`) mantêm a altura; destravadas dividem `avail − Σ travadas` igualmente, com mínimo **2 in (50,8 mm)**.
- Todas travadas → escala proporcional para caber em `avail` (análogo vertical de `distribute_widths`).

## Regra derivada: gaveteiro "fechado" por prateleira 🟢

`add_drawers` (`operators/ops_closet.py:1954-1974`) e `apply_bay_config` (`types_closets.py:2138-2140`) colocam a prateleira de
tampa em `cap = qty·(fh + gap) − st`. Substituindo no layout: `span = cap + (st − gap)`, `avail = span − (qty−1)·gap = qty·fh`
→ cada frente sai exatamente com `fh` (7,5 in por padrão). O idprop `hb_drawer_front_height` **não** dimensiona as frentes
diretamente; só posiciona a tampa.

## Puxadores (`_position_front_pull`) 🟢 `types_closets.py:908-1009`

| Tipo | X | Y (na frente) | Rotação |
|---|---|---|---|
| gaveta | centro | centro (`center_pulls_on_drawer_front`) ou `altura − 1,5 in − meia-barra` | (−90°,0,0) |
| basculante (hamper) | centro | `altura − 1,5 in − meia-barra` | (−90°,0,0) |
| porta | lado oposto à dobradiça: `offset` = meia largura do montante (5 peças) ou 2 in | regra Base/Tall/Upper referida ao piso (abaixo) | (−90°,0,90°) |

Regra de altura da porta: alvo = 45 in do piso. Se a base da porta ≥ 45 in → convenção *Upper* (`1,5 in + meia-barra` acima da borda
inferior); se o alvo passar do topo → convenção *Base* (`altura − 1,5 in − meia-barra`); senão, altura do alvo. Frentes do lado BACK
(ilha dupla) ficam **sem puxador** (pendente, `:914-915, 925-930`).
