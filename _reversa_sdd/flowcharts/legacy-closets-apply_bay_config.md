# `apply_bay_config` — presets "Change Bay" (configurações padrão de vão)

> Arquivo: `blendertomob/product_libraries/closets/types_closets.py:2117-2222` (catálogo `BAY_CONFIG_GROUPS :2065-2082`).
> Chamado por `hb_closets.change_bay` (`operators/ops_closet.py:2066-2108`) para cada vão selecionado.
> Confiança geral: 🟢 CONFIRMADO.

## Fluxograma

```mermaid
flowchart TD
    A([apply_bay_config bay, config]) --> B{root encontrado?}
    B -- não --> F0([False])
    B -- sim --> C[clear_bay_contents: remove divisoras,<br/>idprops de porta do vão, conteúdo das openings]
    C --> D[recalc → volta a 1 opening por lado]
    D --> E{opening FRONT existe?}
    E -- não --> F0
    E -- sim --> IH["ih = bay.height − 2·st − kick (kick só se piso)<br/>dh = 7,5 in"]
    IH --> P{config}
    P -- ADJ_SHELVES --> P1["hb_adj_shelf_qty = clamp(int(ih/12 in), 1, 8)"]
    P -- DOUBLE_HANG --> P2["splits=[ih/2]; varão nos seg 0 e 1"]
    P -- DH_TOP_SHELF --> P3["hang_top = ih − 12 in<br/>splits=[hang_top/2, hang_top]; varão seg 0 e 1"]
    P -- DH_MID_SHELF --> P4["splits=[ih/2, min(ih/2+12 in, ih−st−1 in)]<br/>varão seg 0 e 2"]
    P -- "DOORS_NDR (N=3..6)" --> P5["cap = N·(dh+gap) − st<br/>splits=[cap]; gavetas seg 0; portas duplas seg 1"]
    P -- "DOORS_OPEN_NDR" --> P6["mid = cap + (ih−cap)/2<br/>splits=[cap, mid]; gavetas seg 0; portas seg 2; seg 1 aberto"]
    P -- OPEN_OVER_DOORS --> P7["splits=[ih/2]; portas seg 0 (baixo)"]
    P -- DOORS_OVER_OPEN --> P8["splits=[ih/2]; portas seg 1 (cima)"]
    P -- FULL_HEIGHT_DOORS --> P9["bay_door = DOUBLE (sem split)"]
    P -- outro --> F0
    P1 & P2 & P3 & P4 & P5 & P6 & P7 & P8 & P9 --> S[add_fixed_shelf em cada split]
    S --> R1[recalc → divisoras viram segmentos]
    R1 --> AC[executa ações por índice de segmento]
    AC --> BD{bay_door?}
    BD -- sim --> BD1["hb_bay_door_swing=DOUBLE; hamper=0;<br/>seed_door_shelves(opening)"]
    BD -- não --> R2
    BD1 --> R2[recalc final] --> T([True])
```

## Ações de segmento 🟢

| Ação | Efeito | Local |
|---|---|---|
| `_cfg_rod` | varão a 2,5 in abaixo do topo do segmento, ancorado no topo | `:2102-2103` |
| `_cfg_doors` | porta DOUBLE, não-basculante, semeia reguláveis (`seed_door_shelves`) | `:2106-2109` |
| `_cfg_hamper` | porta LEFT basculante (definida, sem uso no catálogo atual 🟡) | `:2112-2114` |
| `_cfg_drawers` | `hb_drawer_qty = N`, `hb_drawer_front_height = 7,5 in` | `:2175-2177` |

`seed_door_shelves` (`:2085-2099`): só semeia se a opening estiver vazia (sem reguláveis, gavetas, nichos ou varão); qtd =
`clamp(int(interior_h / 12 in), 1, 12)` (`default_adj_shelf_qty :1867-1875`).

## Observações

- 🟡 "Doors Open N Drawers" (`DOORS_OPEN_*`) **não** abre as portas: cria 3 segmentos (gavetas / vão aberto / portas). O comentário
  "same build with the doors shown open" (`:2142-2143`) diverge da implementação.
- 🟢 A regra de 12 in (≈305 mm) por prateleira regulável e a faixa de 12 in acima dos varões são convenções do mercado americano.
- 🟢 Cada split é escrito em Z do interior do vão (`hb_z_offset` a partir de `interior_z`); o *snap* 32 mm **não** é aplicado aqui
  (só no modal `add_part` e no *grab*).
