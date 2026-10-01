# Fluxogramas — módulo legado `hb_placement` (fork Home Builder 5)

Arquivos: `blendertomob/hb_placement.py`, `blendertomob/hb_snap.py`, `blendertomob/hb_gpu_draw.py`.

> Legenda de confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA

O módulo **não registra operadores próprios** 🟢 (não há `bpy.types.Operator` nem `register()` em nenhum dos três arquivos). Ele fornece:

- `PlacementMixin` (`hb_placement.py:81`) — base de estado + entrada numérica + consultas de colisão/gap em paredes, herdada por ~15 operadores modais (paredes, portas/janelas, obstáculos, detalhes 2D, layouts, gabinetes frameless/face-frame, closets).
- `DimensionOperatorMixin` (`hb_placement.py:1360`) — máquina de 3 cliques para cotas (FIRST → SECOND → OFFSET).
- `hb_snap` — raycast com busca em anel, snap a vértice/aresta e à grade.
- Desenho GPU: `draw_placement_dimensions` (`hb_placement.py:1712`), `draw_dimension_snap_indicator` (`hb_placement.py:1642`) e primitivas compartilhadas de `hb_gpu_draw.py`.

## 1. Visão geral (dependências e fluxo de um tick modal)

```mermaid
flowchart TD
    subgraph Consumidores["Operadores consumidores (fora do módulo)"]
        OP1[hb_frameless_OT_place_cabinet<br/>frameless/ops_placement.py:270]
        OP2[face_frame ops_placement]
        OP3[walls / doors_windows / obstacles]
        OP4[details / layouts add_dimension]
    end
    subgraph hb_placement.py
        PM[PlacementMixin]
        DM[DimensionOperatorMixin]
        DPD[draw_placement_dimensions]
        DSI[draw_dimension_snap_indicator]
        DUP[duplicate_object_hierarchy]
        HT[draw_header_text / clear_header_text]
    end
    subgraph hb_snap.py
        GR[get_region]
        MAIN[main]
        BH[best_hit]
        SO[snap_to_object]
        SG[snap_to_grid]
        SVG[snap_value_to_grid]
    end
    subgraph hb_gpu_draw.py
        VB[get_visible_window_bounds]
        PR[draw_rect / draw_text / draw_lines ...]
    end
    OP1 & OP2 & OP3 --> PM
    OP4 --> DM
    PM -->|update_snap| MAIN
    MAIN --> BH
    MAIN --> SO
    MAIN --> SG
    PM -->|add_placement_dim_handler| DPD
    DM -->|add_dimension_draw_handler| DSI
    PM -->|find_placement_gap*, intrusões| HT2[hb_types.GeoNodeWall / GeoNodeObject]
    NAV[scene_navigator / viewport_hud] --> VB & PR
```

## 2. Tick modal típico de um consumidor do `PlacementMixin`

Baseado no consumidor representativo `hb_frameless_OT_place_cabinet.modal` (`product_libraries/frameless/operators/ops_placement.py:1729-1863`) 🟢.

```mermaid
flowchart TD
    E[evento] --> I{INBETWEEN_MOUSEMOVE?}
    I -- sim --> RM[RUNNING_MODAL]
    I -- não --> Q{UP/DOWN_ARROW?}
    Q -- sim --> QA[aplica valor digitado; auto_quantity=False; qty±1] --> RM
    Q -- não --> T{handle_typing_event consumiu?}
    T -- sim --> H[update_header] --> RM
    T -- não --> HID[oculta preview + cotas] --> US[update_snap → hb_snap.main]
    US --> W{hit_object ou ancestral tem IS_WALL_BP<br/>e modificador GN?}
    W -- não --> NW[find_nearest_wall_from_cursor]
    W -- sim --> SW[selected_wall]
    NW --> MOV
    SW --> MOV{estado permite mover?<br/>≠TYPING ou alvo WIDTH/HEIGHT}
    MOV -- sim, parede --> POW[set_position_on_wall → find_placement_gap_by_side]
    MOV -- sim, sem parede --> PF[set_position_free → detect_cabinet_snap_target]
    MOV -- não --> UD
    POW --> UD[update_dimensions + update_header]
    PF --> UD
    UD --> C{LEFTMOUSE / RET?}
    C -- sim --> FIN[aplica digitado; create_final_cabinets; limpa] --> F[FINISHED]
    C -- não --> X{RIGHTMOUSE / ESC?}
    X -- sim --> CAN[cleanup_placement_objects] --> CN[CANCELLED]
    X -- não --> P{MIDDLEMOUSE / WHEEL?}
    P -- sim --> PT[PASS_THROUGH]
    P -- não --> RM
```

## 3. Máquina de estados do posicionamento (`PlacementState` × `TypingTarget`)

```mermaid
stateDiagram-v2
    [*] --> IDLE : valor padrão da classe (hb_placement.py:102)
    IDLE --> PLACING : init_placement() (l.117)
    PLACING --> TYPING : tecla de NUMBER_KEYS [PRESS]\n(target = get_default_typing_target() se NONE) (l.201-209)
    PLACING --> TYPING : start_typing(target) (l.179)
    TYPING --> TYPING : dígito/símbolo → typed_value += c (l.217)
    TYPING --> TYPING : BACK_SPACE com valor → remove último (l.224)
    TYPING --> TYPING : TAB com próximo alvo ≠ NONE → apply + start_typing(next) (l.243-248)
    TYPING --> PLACING : BACK_SPACE com valor vazio → stop_typing (l.229)
    TYPING --> PLACING : ESC → stop_typing (l.238)
    TYPING --> PLACING : RET/NUMPAD_ENTER → apply_typed_value (default chama stop_typing) (l.233, 281)
    PLACING --> IDLE : cancel_placement() (l.427)
    TYPING --> IDLE : cancel_placement()
    IDLE --> [*]
    note right of TYPING
        ADJUSTING (l.39) é declarado mas
        nunca atribuído no módulo (🟢 grep)
    end note
```

## 4. Máquina de estados do `DimensionOperatorMixin`

```mermaid
stateDiagram-v2
    [*] --> FIRST : init_dimension_state() (l.1381)
    FIRST --> SECOND : LEFTMOUSE com current_point\nfirst_point=copy; create_preview_dimension (l.1516-1522)
    SECOND --> OFFSET : LEFTMOUSE\nsecond_point (com ortho se ativo) (l.1524-1532)
    OFFSET --> [*] : LEFTMOUSE → finalize_dimension;\nremove handler; limpa header → FINISHED (l.1534-1540)
    FIRST --> [*] : RIGHTMOUSE/ESC → cancel_dimension → CANCELLED
    SECOND --> [*] : RIGHTMOUSE/ESC → CANCELLED
    OFFSET --> [*] : RIGHTMOUSE/ESC → CANCELLED (l.1549-1553)
    state Ortho {
        OFF --> AUTO : tecla O
        AUTO --> HORIZONTAL : tecla O
        HORIZONTAL --> VERTICAL : tecla O
        VERTICAL --> OFF : tecla O
        AUTO --> HORIZONTAL : 1º apply com |dx|≥|dy| (fixa)
        AUTO --> VERTICAL : 1º apply com |dx|<|dy| (fixa)
    }
```

## 5. Ciclo de vida dos draw handlers

```mermaid
flowchart LR
    A[add_placement_dim_handler<br/>l.132 — idempotente] -->|SpaceView3D.draw_handler_add<br/>WINDOW/POST_PIXEL| H1((handle em<br/>self._placement_dim_handle))
    H1 --> R1[remove_placement_dim_handler<br/>l.147 — idempotente, engole exceções]
    B[add_dimension_draw_handler<br/>l.1400 — NÃO idempotente] --> H2((self._dim_draw_handle))
    H2 --> R2[remove_dimension_draw_handler l.1406]
    R2 -.chamado em.-> F1[FINISHED l.1538]
    R2 -.chamado em.-> F2[CANCELLED l.1551]
    R1 -.chamado pelos consumidores.-> C1[face_frame/ops_placement.py:3545,3842,4550,4608,5350,5414<br/>closets/ops_closet.py:603,1337,1739]
```

🟡 Não existe `cancel()` no mixin: se o operador for abortado pelo Blender (ex.: troca de arquivo durante o modal), nenhum dos dois handlers é removido pelo módulo — depende do consumidor.

## 6. `hb_snap.main` — resolução do ponto sob o cursor

```mermaid
flowchart TD
    M[main self, ctrl, context] --> R[hit_location=None, hit_grid=False]
    R --> BH[best_hit: view_layer.update + ray_cast no cursor]
    BH --> OK{acertou objeto sem HB_CURRENT_DRAW_OBJ?}
    OK -- sim --> RET[retorna hit]
    OK -- não --> RING[6 raios num anel de 50 px;<br/>mantém o mais próximo do view_point]
    RING --> RET
    RET --> S[grava hit_location, hit_face_index, hit_object, view_point]
    S --> D{result?}
    D -- sim e Ctrl --> SO[snap_to_object: vértices do polígono → snap_to_geometry]
    D -- sim sem Ctrl --> END[fim]
    D -- não --> SG[snap_to_grid: interseção com plano Z=0<br/>ou plano ⟂ vista em vista lateral ortográfica]
    SG --> CG{Ctrl?}
    CG -- sim --> Q[quad da célula de grade → snap_to_geometry]
    CG -- não --> END2[hit_location = interseção]
    Q --> END2
```

Ver detalhes em `legacy-hb_placement-snap_main.md`.
