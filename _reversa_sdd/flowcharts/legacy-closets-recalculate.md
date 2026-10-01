# `ClosetStarter.recalculate` — orquestrador sem drivers (props → solver → objetos)

> Arquivo: `blendertomob/product_libraries/closets/types_closets.py:458-521` (+ `_layout_panels :523`, `_layout_bays :532-689`,
> `_reconcile_bay_openings :1194-1242`, `_layout_starter_parts :1244-1269`, `_layout_bridge_parts :1279-1339`).
> Confiança geral: 🟢 CONFIRMADO.

## Fluxograma

```mermaid
flowchart TD
    A([recalculate]) --> G{id obj em _RECALCULATING?}
    G -- sim --> Z([return — evita reentrância])
    G -- não --> G1[adiciona id ao guard]
    G1 --> PR["Propagação: para cada vão<br/>se bay.height == hb_last_height e starter mudou → bay.height = sp.height<br/>idem para depth (hb_last_depth)"]
    PR --> SD[hb_last_depth = sp.depth]
    SD --> SPEC[_spec_from_props]
    SPEC --> E{spec.bays vazio?}
    E -- sim --> Z2([return])
    E -- não --> SOL[[solver.compute_layout]]
    SOL --> WB["grava widths nos vãos sob _DISTRIBUTING_WIDTHS<br/>(não auto-trava)"]
    WB --> LP[_layout_panels: location + Length/Width/Thickness]
    LP --> LB[_layout_bays]
    subgraph LBS["_layout_bays por vão"]
        B1[cage: location x,0,z0; Dim X/Y/Z] --> B2[prat. inferior em bottom_z<br/>oculta se remove_bottom]
        B2 --> B3[prat. superior em top_z]
        B3 --> B4["rodapés: y = −depth + setback (frente)<br/>ou −setback (traseiro, ilha dupla)<br/>ocultos se suspenso/remove_bottom/kick≤0"]
        B4 --> B5["cleat em cleat_z, largura 4 in"]
        B5 --> B6["hang rail: cria se faltar (lazy)<br/>z = height − 3,3125 in; 1,125 x 0,25 in"]
        B6 --> B7[fundo aplicado / fundo central]
        B7 --> B8[[_reconcile_bay_openings]]
        B8 --> B9["para cada lado FRONT/BACK:<br/>prat. divisoras: clamp 0..interior_h−st<br/>boundaries = offsets"]
        B9 --> B10["segmentos: bottoms=[0]+[b+st], tops=boundaries+[interior_h]<br/>cada opening: hb_seg_bottom, Dim Z = max(t−b, 1 cm)"]
        B10 --> B11[[_layout_opening_parts]]
        B11 --> B12[_layout_bay_doors: portas do vão inteiro]
    end
    LB --> LS["_layout_starter_parts: tampo<br/>(cria lazy se include_countertop)"]
    LS --> LBR["_layout_bridge_parts: pontes TOP/BOTTOM/KICK<br/>por idprops hb_bridge_*"]
    LBR --> H{closet_type == HANGING<br/>e altura mudou?}
    H -- sim --> H1["location.z += last_h − sp.height<br/>(cresce para baixo, topo fixo)"]
    H -- não --> H2
    H1 --> H2[hb_last_height = sp.height]
    H2 --> H3[root Dim X/Y/Z = W/D/H]
    H3 --> F[finally: remove id do guard]
    F --> Z3([fim])
```

## `_reconcile_bay_openings` (divisoras → segmentos) 🟢 `types_closets.py:1194-1242`

```mermaid
flowchart TD
    A([início]) --> B[Para cada opening do vão]
    B --> C{filho é FIXED_SHELF<br/>e não é preview?}
    C -- sim --> D["reparenta ao vão;<br/>hb_z_offset = seg_bottom + offset<br/>(ancorado no topo: seg_h − offset)<br/>hb_anchor_top=0; herda lado"]
    C -- não --> B
    D --> B
    B -- fim --> E[para cada lado]
    E --> F["want = nº divisoras do lado + 1"]
    F --> G{openings > want?}
    G -- sim --> G1[move filhos da opening extra para openings[0]<br/>remove a opening] --> G
    G -- não --> H{openings < want?}
    H -- sim --> H1[cria ClosetOpening 'Opening k'] --> H
    H -- não --> I[renumera hb_opening_index]
```

## Notas

- **Sem drivers** 🟢: todas as dimensões são escritas por Python a cada recálculo (`types_closets.py:1-8`); o custo cresce com o nº de peças (recalcula o starter inteiro a cada edição) 🟡.
- **Guardas de reentrância** 🟢 (`:105-106`): `set()` de `id(obj)` em nível de módulo; o `id()` de wrappers Python pode ser reaproveitado após exclusão 🟡.
- **Âncora de topo dos suspensos** 🟢 (`:511-515`): edição de altura desloca a origem para baixo; mover com G não é afetado porque só compara com `hb_last_height`.
- Conteúdo de uma abertura fundida é **re-hospedado** na opening de menor índice, não descartado 🟢 (`:1229-1233`).
