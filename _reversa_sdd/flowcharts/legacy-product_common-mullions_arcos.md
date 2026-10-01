# Mullions (retos e curvos) e arcos Arch/Crown

`blendertomob/product_libraries/common/door_builder.py:574-1051` 🟢

## Arcos (`shape_rise`, `_shape_curve_pts`, `_cell_perimeter`)

```mermaid
flowchart TD
    A(["shape_rise(curve, w)"]) --> B{"curve == 'CROWN'?"}
    B -- Sim --> B1["rise = min(0.16·w, 1.75&quot;)"]
    B -- Não: ARCH --> B2["rise = min(0.20·w, 2.25&quot;)"]
    C(["_shape_curve_pts(curve, w, rise, segs=16)"]) --> C0{"rise <= 1e-6 ou w <= 1e-6?"}
    C0 -- Sim --> C00["None (vão degenerado)"]
    C0 -- Não --> C1{"CROWN?"}
    C1 -- Sim --> C2["meia ogiva: Bézier cúbica<br/>P0=(0,0) P1=(0.22w,0) P2=(0.30w,rise) P3=(0.5w,rise)<br/>m = max(segs/2, 4) amostras; espelha em x = w − x"]
    C1 -- Não --> C3["arco circular (eyebrow):<br/>R = (rise² + (w/2)²) / (2·rise)<br/>centro (w/2, rise − R); varre a0→a1 em segs passos;<br/>z = max(·, 0)"]
    C2 --> C4["força extremos (0,0) e (w,0)"]
    C3 --> C4
```

- `_cell_perimeter` gera estações anti-horárias a partir do canto inferior esquerdo; a direção de meia-esquadria é
  a bissetriz das normais esticada por `1/(1 + n1·n2)` (limitada a 0.2 no denominador), o que reduz ao clássico
  `(±1, ±1)` num retângulo 🟢 (`:621-657`).
- Quem usa: `_emit_raised_panel` (painel "catedral"), `_emit_strip_rings`, `_emit_shaped_panel`,
  `_emit_shaped_rail`, `_emit_mullion_bars` (recorte) 🟢.
- `SHAPE_KINDS` (em `face_frame/style_options.py`, fora do módulo): Arch, Crown, Double Arch, Double Crown
  (`double` → também na travessa inferior), Twin (`twin` → força 1 mid stile, um arco por vidro) 🟢.

## Mullions (`_emit_mullion_bars`)

```mermaid
flowchart TD
    A(["_emit_mullion_bars(part, T, spec, top_pts, bottom_pts)"]) --> A0{"depth <= 1e-6 ou w/h <= 0?"}
    A0 -- Sim --> F0["False"]
    A0 -- Não --> A1["bw = spec.bar_width (padrão 7/8&quot;)<br/>pattern = spec.pattern (padrão GRID)"]
    A1 --> CV{"pattern ∈ _CURVED_MULLION_BARS?<br/>GOTHIC / DBL_GOTHIC / DBL_BOW / INTERLOKEN"}
    CV -- Sim --> CB["_curved_bar_polys: centerlines normalizadas (0..1)<br/>× (w,h); offset ±bw/2 pela normal local;<br/>recorte Sutherland-Hodgman no retângulo"]
    CV -- Não --> SL["_mullion_layout (retos)"]
    SL --> G{"GRID"}
    G --> G1["linhas = 2 se h≤24&quot;, 3 se ≤36&quot;, 4 se ≤48&quot;, senão 5<br/>vertical central se w > bw + 2&quot;;<br/>horizontais topam na vertical; pula se a < 1&quot; da borda"]
    SL --> MI{"MISSION"}
    MI --> MI1["barra horizontal em zb0 = h − h/3 − bw;<br/>2 verticais acima → 3 vidros iguais;<br/>[] se zb0 ≤ 1&quot; ou w ≤ 3·bw + 3&quot;"]
    SL --> PR{"PRAIRIE"}
    PR --> PR1["barras de borda a m = 2&quot; das arestas<br/>(vidro 2×2 nos cantos); [] se w/h ≤ 2(m+bw)+1&quot;"]
    SL --> X{"X"}
    X --> X1["diagonal ascendente inteira; descendente<br/>cortada em 2 meias (meia-madeira) pelo semiplano<br/>da normal da ascendente ± bw/2"]
    CB --> CL["se célula arqueada: _curve_clip_planes<br/>(semiplanos por corda: abaixo do topo / acima da base)"]
    G1 --> CL
    MI1 --> CL
    PR1 --> CL
    X1 --> CL
    CL --> PZ["_emit_prism de z_front = T até z_back = T − depth<br/>(curvos: −(i+1)·0.0002 m) slot 0"]
    PZ --> T0["True"]
```

## Explicação

- Padrões retos seguem "CWP Enhanced Panel Options" (catálogo pdf 143-144) 🟢 (`:683-693`); curvos foram
  traçados dos desenhos do catálogo (pdf 144) como polilinhas por **segmento** — as barras se dividem nos
  cruzamentos e as pontas são pré-estendidas para serem aparadas pelo recorte 🟢 (`:842-848`).
- Aspectos não uniformes esticam o padrão curvo (escala x·w, z·h) 🟢 (`:981-982`, `:988`).
- O recorte por cordas "sub-preenche" levemente onde a curva é convexa: barras terminam um fio antes em vez de
  atravessar a travessa 🟢 (`:803-805`).
- `bar_width`/`depth` são montados pelo consumidor: `bar_width = inch(PANEL_KINDS[..].get('bar_width', 0.875))`
  e `depth = eff_panel_inset` (o plano do vidro = recuo do painel) 🟢
  (`face_frame/props_hb_face_frame.py:3636-3641`).
