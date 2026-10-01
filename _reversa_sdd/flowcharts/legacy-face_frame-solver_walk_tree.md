# `solver_face_frame.bay_openings` / `_walk_tree` / `_redistribute_sizes` — distribuição de vãos e aberturas

> Arquivo: `blendertomob/product_libraries/face_frame/solver_face_frame.py:2816-3205`. Confiança geral: 🟢 CONFIRMADO.

## Assinaturas
- `bay_openings(layout, bay_index) -> {'leaves': [...], 'splitters': [...], 'backings': [...]}` (`:3171`)
- `_walk_tree(node, layout, bay_index, cage_x, cage_z, cage_dim_x, cage_dim_y, cage_dim_z, reveals, leaves, splitters, backings, is_bay_root=False) -> None` (`:2993`)
- `_redistribute_sizes(children, available, splitter_total) -> list[float]` (`:2816`)
- `_bay_root_reveals(layout, bay_index) -> dict(top,bottom,left,right)` (`:2763`)

## Fluxograma

```mermaid
flowchart TD
    A["bay_openings(layout, i)"] --> B{"tree do bay existe?"}
    B -- não --> Z["retorna listas vazias"]
    B -- sim --> C["bay_cage_dims → cage_dim_x/y/z<br/>_bay_root_reveals → reveals iniciais"]
    C --> D["_walk_tree(raiz, cage 0,0, is_bay_root=True)"]
    D --> E{"nó é folha?"}
    E -- sim --> F["append leaf rect:<br/>cage_x, cage_z, dims, reveal_top/bottom/left/right,<br/>obj_name, opening_index"]
    E -- não --> G["n filhos → n-1 splitters<br/>widths[i] = override ativo ou splitter_width"]
    G --> H{"axis == H?"}
    H -- sim --> I["para cada splitter removido (remove_member):<br/>eff_w = 3/32in + overlay_bottom(acima) + overlay_top(abaixo)"]
    I --> J{"is_bay_root E remove_bottom E<br/>último filho é folha frontless NONE/APPLIANCE<br/>E último splitter não removido?"}
    J -- sim --> K["último splitter vira BOTTOM_RAIL<br/>eff_w = bottom_rail_width do bay"]
    J -- não --> L
    K --> L["splitter_total = soma(eff_w)"]
    H -- não V --> L
    L --> M["available = dim do cage no eixo − reveals do eixo"]
    M --> N["_redistribute_sizes:<br/>locked = soma(size dos filhos unlock_size)<br/>extra = 4in × nº VANITY_DOOR destravados<br/>share = (available − splitter_total − locked − extra) / nº destravados"]
    N --> O["percorre filhos: H de cima p/ baixo · V da esquerda p/ direita"]
    O --> P["reveal externo herdado só pelo 1º e último filho;<br/>bordas internas = 0"]
    P --> Q["recursão _walk_tree(filho, sub-cage)"]
    Q --> R{"não é o último filho?"}
    R -- sim --> S{"H e membro removido?"}
    S -- sim --> T["só consome o gap colapsado (sem peça)"]
    S -- não --> U["_emit_h_splitter / _emit_v_splitter<br/>rect do mid rail/stile no plano da moldura<br/>+ backing (BAY_SHELF 3/4in ou BAY_DIVISION mt) se add_backing"]
    T --> O
    U --> O
    R -- não --> V["fim do nó"]
```

## Explicação
1. **Retângulo de partida**: o cage do bay cobre a cavidade da carcaça (mais larga que o vão da moldura). `_bay_root_reveals`
   calcula a diferença entre cage e vão: `top = cage_dim_z − (height − top_rail − eff_bottom_rail − kick_height − front_drop)`,
   `left/right = distância da face interna da lateral/divisória até a borda do stile`, `bottom = 0` (topo do fundo = topo do
   bottom rail). Em `PANEL` todos os reveals são zero (`:2774-2775`). 🟢
2. **Distribuição igualitária com travas**: filhos com `unlock_size=True` mantêm o valor; os demais dividem o resto
   igualmente. É o mesmo algoritmo de `_distribute_bay_widths` (bays) e de `_solve_section_heights` (cantos). 🟢
3. **Regra da porta de vaidade**: filho destravado com `SIZE_ROLE == 'VANITY_DOOR'` recebe `share + 4"` (`VANITY_DOOR_EXTRA_WIDTH`, `:2813`). 🟢
4. **Mid rail removido**: o membro some (sem peça nem backing) e o espaço vira `3/32" + overlays adjacentes`, fazendo as frentes
   ficarem a 3/32" uma da outra (`MID_RAIL_REMOVED_GAP`, `:3255`; lógica `:3055-3062`). Só vale para eixo H. 🟢
5. **Rail inferior "promovido"**: bay com `remove_bottom` cujo vão inferior é frontless (NONE/APPLIANCE, ex.: geladeira) tem o
   último splitter construído como `BOTTOM_RAIL` com a largura do bottom rail do bay (`:3063-3074`). 🟢
6. **Saídas em coordenadas locais do bay**; `_update_openings_in_bay` casa as folhas com objetos existentes por `obj_name`
   (in-place) e apaga/recria splitters e backings a cada recálculo (`types_face_frame.py:5715-5815`). 🟢

## Divergência conhecida (risco)
`FaceFrameCabinet._redistribute_split_node` (`types_face_frame.py:1763`) grava os tamanhos "exibidos" usando
`n_splitters × splitter_width` uniforme e `ff_height = height − top_rail − bottom_rail − kick`, **sem** considerar overrides
por membro (`splitter_widths`), membros removidos, `remove_bottom` (bottom rail efetivo 0) nem `front_drop`. O solver
recalcula a geometria corretamente, mas o `size` armazenado de filhos destravados pode divergir do construído. 🟢 (diferença lida)
/ 🟡 (impacto: valores exibidos e o valor "congelado" quando o usuário trava).
