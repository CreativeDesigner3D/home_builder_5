# `PlacementMixin.compute_gap_holdoffs` — recuo por borda do vão

Local: `blendertomob/hb_placement.py:1191-1270` 🟢 (usa `_wall_end_is_inside_corner`, `l.1143-1189`).
Assinatura: `(wall_obj, gap_start, gap_end, holdoff, place_on_front=True, wall_thickness=0.0, object_z_start=None, object_height=None) -> (left_holdoff, right_holdoff)`.

Define quanto o gabinete deve ficar afastado de cada borda do vão. `wall_thickness` é recebido mas **não é usado** no corpo 🟢.

```mermaid
flowchart TD
    A[início] --> B{holdoff ≤ 0?}
    B -- sim --> Z[0, 0]
    B -- não --> C{lê Length da parede?}
    C -- falha --> Z
    C -- ok --> D["end_tol = 1/2#quot;, edge_tol = 1/4#quot;"]
    D --> E[coleta spans de portas/janelas que sobrepõem Z do objeto]
    E --> F[boundary_holdoff gap_start, is_left=True]
    E --> G[boundary_holdoff gap_end, is_left=False]
    F & G --> H["true_w = gap_end − gap_start<br/>max_total = max(true_w − 1#quot;, 0)"]
    H --> I{"left+right > max_total?"}
    I -- sim --> J[escala ambos por max_total / total]
    I -- não --> K[retorna]
    J --> K

    subgraph boundary_holdoff["boundary_holdoff(x, is_left)"]
        b1{"borda é ponta da parede (±end_tol)?"} -- sim --> b2{_wall_end_is_inside_corner?}
        b2 -- sim --> b0[0]
        b2 -- não --> bh[holdoff]
        b1 -- não --> b3{"borda coincide (±edge_tol) com<br/>fim de abertura (esq.) / início (dir.)?"}
        b3 -- sim --> bh
        b3 -- não --> b0
    end
```

## `_wall_end_is_inside_corner(wall_geo, side, place_on_front)`

🟢 `l.1156-1189`: canto interno ⇔ existe vizinha (`include_loop_seam=True`) e a direção da vizinha que **se afasta** do vértice compartilhado tem produto escalar > 1e-4 com a normal do lado de colocação (`-Y` local para frente, `+Y` para trás). Pontas abertas e cantos externos (convexos) retornam `False` → recebem recuo.

Regras resumidas:
- Canto interno e borda de gabinete vizinho → recuo 0 (corrida encosta).
- Ponta aberta, canto externo ou borda de porta/janela que se sobrepõe verticalmente → recuo `holdoff`.
- Os dois recuos são escalados juntos para deixar pelo menos 1" útil.
