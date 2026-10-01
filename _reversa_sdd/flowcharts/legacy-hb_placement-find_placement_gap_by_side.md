# `PlacementMixin.find_placement_gap_by_side` — busca de vão com lado da parede

Local: `blendertomob/hb_placement.py:918-1141` 🟢
Assinatura: `(wall_obj, cursor_x, object_width, place_on_front, wall_thickness, object_z_start=None, object_height=None, object_depth=None, exclude_obj=None) -> (gap_start, gap_end, snap_x)`; retorna `(None, None, None)` se a parede não tem modificador GN (`l.946-948`).

Versão "ciente do lado" de `find_placement_gap` (`l.502`). Monta uma lista de obstáculos `(x_start, x_end, obj)` no eixo X local da parede, ordena e escolhe o vão que contém `cursor_x`.

```mermaid
flowchart TD
    A[início] --> B{parede tem modificador?}
    B -- não --> Z[None, None, None]
    B -- sim --> C[wall_length; check_vertical = z_start e height ≠ None]
    C --> D[para cada filho da parede]
    D --> D1{obj_x / exclude / IS_2D_ANNOTATION / IS_SNAP_LINE?}
    D1 -- sim --> D
    D1 -- não --> D2{porta ou janela?}
    D2 -- não --> D3{"lado do filho (y < thickness/2) == place_on_front?"}
    D3 -- não --> D
    D2 -- sim --> D4
    D3 -- sim --> D4[lê Dim X / Dim Z]
    D4 --> D5{check_vertical e sem sobreposição Z?}
    D5 -- sim --> D
    D5 -- não --> D6{rotação Z}
    D6 -- "≈ -90° / 270°" --> R1["x ∈ [loc.x − Dim Y, loc.x]"]
    D6 -- "≈ ±180°" --> R2["x ∈ [loc.x − Dim X, loc.x]"]
    D6 -- outro --> R3["x ∈ [loc.x, loc.x + Dim X]"]
    R1 & R2 & R3 --> D
    D -- fim --> F[gabinetes livres na cena: sem pai + FREE_CABINET_TAGS]
    F --> F1[projeta 4 cantos da pegada no espaço da parede]
    F1 --> F2{"pegada Y cruza a faixa<br/>front: [−band,0] / back: [t, t+band]<br/>band = object_depth ou 24#quot;"}
    F2 -- não --> F
    F2 -- sim --> F3{check_vertical sem overlap?}
    F3 -- sim --> F
    F3 -- não --> F4["x recortado em [0, wall_length];<br/>descarta se largura < 1/4#quot;"]
    F4 --> F
    F -- fim --> G[intrusão da parede adjacente esquerda/direita<br/>get_adjacent_wall_intrusion → obstáculos virtuais nas pontas]
    G --> H[get_tee_wall_intrusions → obstáculos virtuais no meio]
    H --> I[snap lines: obstáculo de largura zero em SNAP_X_POSITION]
    I --> J{lista vazia?}
    J -- sim --> K[0, wall_length, cursor_x]
    J -- não --> L["varre ordenado: cursor < x_start → gap_end=x_start, para;<br/>senão gap_start = x_end"]
    L --> M{cursor ≥ fim do último?}
    M -- sim --> M1[gap = último.x_end .. wall_length]
    M -- não --> N
    M1 --> N{object_width ≥ gap?}
    N -- sim --> S1[snap_x = gap_start]
    N -- não --> N2{cursor − gap_start < w/2?}
    N2 -- sim --> S1
    N2 -- não --> N3{gap_end − cursor < w/2?}
    N3 -- sim --> S2[snap_x = gap_end − w]
    N3 -- não --> S3[snap_x = cursor − w/2]
```

## Pontos de atenção

- 🟢 Portas/janelas (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`) bloqueiam os dois lados da parede (`l.969-974`).
- 🟢 O lado do filho é decidido só por `location.y < wall_thickness/2` (`l.972`).
- 🟢 Tolerância de rotação: 0,1 rad (~5,7°) (`l.1000-1003`).
- 🟡 A varredura assume obstáculos não sobrepostos: `gap_start = x_end` é sobrescrito a cada obstáculo cujo início ≤ cursor, então um obstáculo curto depois de um longo que o engloba pode "encolher" `gap_start` para trás. Se o cursor estiver dentro de um obstáculo, `gap_start` > cursor e o objeto encosta na borda direita desse obstáculo.
- 🟢 O teste "além do último" usa `children[-1][1]` (fim do último *por início*), não o maior fim (`l.1127`).
- 🟡 Filhos sem `home_builder.mod_name` entram com largura 0 (obstáculo pontual) (`l.978-986`).
