# `PlacementMixin.get_adjacent_wall_intrusion` e `get_tee_wall_intrusions` — invasão de paredes vizinhas

## `get_adjacent_wall_intrusion`

Local: `blendertomob/hb_placement.py:672-826` 🟢
Assinatura: `(wall_obj, side, object_z_start=None, object_height=None, object_depth=None, place_on_front=True) -> float` (≥ 0). `side ∈ {'left' (x=0), 'right' (x=wall_length)}`.

Calcula quanto (em metros, ao longo do X local desta parede) a parede vizinha **e** os gabinetes dela invadem o vão na ponta indicada. Tudo é feito projetando cantos com `matrix_world` para o espaço local desta parede, sem enumerar casos de rotação.

```mermaid
flowchart TD
    A[início] --> B[get_connected_wall side, include_loop_seam=True]
    B --> C{há vizinha?}
    C -- não --> Z[0.0]
    C -- sim --> D[wall_length, thickness, matriz inversa]
    D --> E{check_depth?}
    E -- sim --> E1["faixa Y própria:<br/>front [−depth, 0] / back [t, t+depth]"]
    E -- não --> F
    E1 --> F[lê Length/Thickness/Height da vizinha]
    F --> G{lida e Z da laje sobrepõe o objeto?}
    G -- não --> K
    G -- sim --> H["ponta de junção jx = adj_len se left, 0 se right;<br/>away = −1 se left, +1 se right"]
    H --> I[away_local_y = componente Y, no espaço desta parede,<br/>do eixo X da vizinha × away]
    I --> J{"protrai para o lado da colocação?<br/>front: away_y < −0.001 / back: > 0.001"}
    J -- não --> K
    J -- sim --> J1["cantos da laje (jx,0) e (jx,adj_thk) projetados<br/>left: max(c.x>0) · right: max(L − c.x, c.x<L)"]
    J1 --> K[para cada filho da vizinha com CABINET_MARKERS]
    K --> K1{obj_x / IS_2D_ANNOTATION / sem marcador?}
    K1 -- sim --> K
    K1 -- não --> K2[Dim X / Dim Y / Dim Z]
    K2 --> K3{sem overlap Z?}
    K3 -- sim --> K
    K3 -- não --> K4["4 cantos da pegada (0,0) (W,0) (0,−D) (W,−D)<br/>→ espaço desta parede"]
    K4 --> K5{check_depth e faixa Y não cruza?}
    K5 -- sim --> K
    K5 -- não --> K6[atualiza max_intrusion como na laje]
    K6 --> K
    K -- fim --> R["max(0, max_intrusion)"]
```

Regra-chave 🟢 (`l.722-730`): em canto interno, a corrida na face traseira precisa começar depois da espessura da vizinha; na face frontal típica a laje fica fora da faixa e a intrusão é 0.

## `get_tee_wall_intrusions`

Local: `blendertomob/hb_placement.py:828-916` 🟢 — retorna lista de `(x_start, x_end)`.

```mermaid
flowchart TD
    A[início] --> B{parede com modificador?}
    B -- não --> Z["[]"]
    B -- sim --> C[para cada objeto da cena com IS_WALL_BP ≠ esta]
    C --> C1{outra tem modificador e Z sobrepõe?}
    C1 -- não --> C
    C1 -- sim --> D[o_dir, o_off=normal×espessura, o_start, o_end]
    D --> E[para cada extremidade pt, away_sign ∈ start:+1, end:−1]
    E --> F{"0,01 < lp.x < L − 0,01<br/>e −0,02 ≤ lp.y ≤ t + 0,02?"}
    F -- não --> E
    F -- sim --> G{"|away_local_y| < 0,001 (paralela)?"}
    G -- sim --> E
    G -- não --> H{"(away_y < 0) == place_on_front?"}
    H -- não --> E
    H -- sim --> I["span = [max(0,min(xa,xb)), min(L,max(xa,xb))]"]
    I --> E
    E -- fim --> C
    C -- fim --> R[spans]
```

- 🟢 `END_MARGIN = 0.01 m` e `FACE_TOL = 0.02 m` (`l.868-869`).
- 🟢 Nada é armazenado: calculado a cada chamada, não fica obsoleto quando paredes se movem (`l.838-840`).
- 🟡 Custo O(nº de objetos da cena) por chamada, e `find_placement_gap` chama duas vezes (front e back) (`l.529-536`), executado a cada MOUSEMOVE.
