# Fluxogramas — módulo legado `closets` (fork Home Builder 5)

> Escopo: `blendertomob/product_libraries/closets/` (17 arquivos .py, ~9,7 mil linhas).
> Legenda de confiança: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxos detalhados por função: ver `legacy-closets-compute_layout.md`, `legacy-closets-recalculate.md`,
> `legacy-closets-layout_opening_parts.md`, `legacy-closets-apply_bay_config.md`, `legacy-closets-position_on_wall.md`.

## 1. Visão geral da arquitetura do módulo 🟢

```mermaid
flowchart LR
    subgraph REG["Registro (closets/__init__.py)"]
        P[props_closets.register] --> M[menus_closets.register] --> O[operators.register] --> G[gpu_overlay_closets.register]
    end

    subgraph DADOS["Dados"]
        SP["Scene.hb_closets<br/>Closets_Scene_Props"]
        ST["Object.hb_closet_starter<br/>Closet_Starter_Props"]
        BP["Object.hb_closet_bay<br/>Closet_Bay_Props"]
        IDP["idprops soltas<br/>(hb_z_offset, hb_drawer_qty,<br/>hb_door_swing, ...)"]
    end

    subgraph NUCLEO["Núcleo paramétrico"]
        T["types_closets<br/>ClosetStarter.recalculate()"]
        S["solver_closets<br/>compute_layout() (sem bpy)"]
        C["const_closets<br/>constantes + sistema 32 mm"]
    end

    subgraph OPCOES["Opções de sala (scene-wide)"]
        MAT[materials_closets]
        FR[fronts_closets]
        PU[pulls_closets<br/>puxadores, varões, cabides]
        DB[drawer_boxes_closets]
        MO[molding_closets]
    end

    subgraph UI["Interação"]
        OPS["operators/ops_closet<br/>place_starter, add_part, change_bay..."]
        GRAB["operators/op_grab_closet<br/>arrastar painéis/prateleiras"]
        OPEN["operators/op_open_door_closet<br/>abrir portas/gavetas"]
        OV["gpu_overlay_closets<br/>rótulos editáveis + pílulas"]
        MN["menus_closets<br/>menus de contexto (MENU_ID)"]
    end

    OPS --> T
    GRAB --> ST & BP & IDP
    OV --> ST & BP & IDP
    ST & BP -- "update callback" --> T
    T --> S --> C
    T --> FR & PU & DB
    T -- escreve --> GN["Inputs GeoNodes<br/>(GeoNodeCutpart / Cage)"]
    SP -- "update_room()" --> T
    SP -- "update_room()" --> MAT
    OPS --> MAT
```

## 2. Hierarquia de objetos de um starter 🟢

`types_closets.py:10-17`

```mermaid
flowchart TD
    R["Starter root cage<br/>IS_CLOSET_STARTER_CAGE<br/>CLASS_NAME, hb_closet_starter"] --> PN["Painéis 0..N<br/>CLOSET_PANEL (hb_panel_index)"]
    R --> CT["Tampo (CLOSET_COUNTERTOP) — opcional"]
    R --> BR["Pontes de canto (CLOSET_BRIDGE_SHELF) — idprops"]
    R --> MOLD["Moldura (IS_CLOSET_MOLDING) — curvas"]
    R --> B["Bay cage 0..N-1<br/>IS_CLOSET_BAY_CAGE, hb_closet_bay"]
    B --> BS["Prateleira inferior / superior fixas"]
    B --> TK["Rodapé (toe kick) / rodapé traseiro"]
    B --> CL["Cleat (travessa de fixação)"]
    B --> HR["Hang rail (trilho de parede)"]
    B --> AB["Fundo aplicado / fundo central (ilhas)"]
    B --> FS["Prateleiras fixas divisoras (CLOSET_FIXED_SHELF)"]
    B --> BD["Portas do vão inteiro (hb_bay_door)"]
    B --> OP["Opening cage(s) — 1 por segmento e lado<br/>IS_CLOSET_OPENING_CAGE"]
    OP --> ADJ["Prateleiras reguláveis"]
    OP --> ROD["Varão (CLOSET_ROD)"] --> HG["Cabides (IS_CLOSET_HANGER) x3"]
    OP --> DR["Portas (CLOSET_DOOR_FRONT)"] --> PL["Puxador (IS_CABINET_PULL)"]
    OP --> DF["Frentes de gaveta"] --> PL2["Puxador"]
    OP --> DBX["Caixas de gaveta (GeoNodeDrawerBox)"]
    OP --> CUB["Nichos: divisões + prateleiras"]
```

## 3. Ciclo de vida: colocação de um starter 🟢

`operators/ops_closet.py:446-552` (invoke), `1226-1330` (modal), `1334-1409` (finalize)

```mermaid
flowchart TD
    A([Clique no catálogo<br/>hb_closets.place_starter]) --> B{source_starter_name?}
    B -- sim --> B1[Modo duplicar: resolve classe pelo CLASS_NAME<br/>fill OFF, bay_qty fixo]
    B -- não --> B2[get_starter_class starter_name]
    B1 --> C
    B2 --> C{classe é canto L?}
    C -- sim --> C1[largura=profundidade=24 in<br/>bay_qty=1, sem fill]
    C -- não --> C2[largura default 80 in<br/>bay_qty = auto_bay_qty largura]
    C1 --> D[Cria cage de preview + ARRAY modifier]
    C2 --> D
    D --> E[init_placement + dim handler<br/>modal_handler_add]
    E --> F{{evento modal}}
    F -- MOUSEMOVE --> G[update_snap → _position_from_hit]
    G --> G1{parede detectada?}
    G1 -- sim --> G2[_position_on_wall<br/>gap fill / snaps / recuo de canto]
    G1 -- não --> G3[_position_free<br/>grade + ilha: clearances e detentes]
    G2 --> F
    G3 --> F
    F -- W / números --> H[digitação de largura/offset] --> F
    F -- Setas cima/baixo --> I[bay_qty ± 1, auto OFF] --> F
    F -- R --> J[gira 90° livre] --> F
    F -- F (duplicar) --> K[alterna fill] --> F
    F -- ESC / RMB --> X[_cancel: remove dim handler + preview] --> Z([CANCELLED])
    F -- LMB --> L[_finalize]
    L --> L1{duplicar?}
    L1 -- sim --> L2[duplicate_object_hierarchy<br/>mirror opcional]
    L1 -- não --> L3[cls.create_starter nome, bay_qty]
    L3 --> L4[posiciona root; sp.width = largura capturada<br/>update callback → recalculate]
    L2 --> L5
    L4 --> L5[_apply_finish materiais]
    L5 --> L6[_apply_selection_shading]
    L6 --> L7{vizinho de canto perpendicular?}
    L7 -- sim --> L8[invoca set_corner_clearance]
    L7 -- não --> Y([FINISHED])
    L8 --> Y
```

## 4. Propagação de edição (props → recalc) 🟢

`props_closets.py:68-94`, `types_closets.py:1914-1921`

```mermaid
flowchart TD
    E1[Usuário edita hb_closet_starter.*] --> U1[_update_starter_prop]
    E2[Usuário edita bay height/depth/floor/remove_*] --> U2[_update_bay_prop]
    E3[Usuário edita bay.width] --> U3[_update_bay_width]
    U3 --> Q{root em _RECALCULATING<br/>ou _DISTRIBUTING_WIDTHS?}
    Q -- sim --> N([ignora: escrita do sistema])
    Q -- não --> LK[width_locked = True] --> RC
    U1 --> RC[recalculate_closet_starter obj]
    U2 --> RC
    RC --> F{root existe e não está<br/>em recálculo?}
    F -- não --> N
    F -- sim --> W[_wrap_starter via CLASS_NAME] --> RE[ClosetStarter.recalculate]
    S1[Scene: material/frente/puxador/gaveta] --> UR[update_room] --> LOOP[para cada starter na cena] --> RC
```

## 5. Configuração de conteúdo de vão / abertura 🟢

`types_closets.py:2117-2272`, `operators/ops_closet.py:1893-2064`

```mermaid
flowchart LR
    MENU[Menu de contexto<br/>MENU_ID] --> CB[change_bay config]
    MENU --> CO[change_opening config]
    MENU --> AD[add_doors / add_drawers / add_cubbies / add_adj_shelves]
    CB --> ABC[apply_bay_config]
    CO --> AOC[apply_opening_config]
    AD --> IDP[grava idprops na opening/bay]
    ABC --> CLR[clear_bay_contents] --> SPL[add_fixed_shelf nos splits] --> RC1[recalc: adota divisoras → segmentos] --> ACT[ações por segmento: varão, portas, gavetas] --> RC2[recalc final]
    AOC --> CLO[clear_opening_contents] --> IDP
    IDP --> RC3[recalculate → regeneradores criam/removem peças]
```

## 6. Camada GPU passiva (overlay + grab + abrir porta) 🟢

`gpu_overlay_closets.py:549-611, 836-929`, `operators/op_grab_closet.py:281-427`, `operators/op_open_door_closet.py:92-220`

```mermaid
flowchart TD
    DH["draw_handler POST_PIXEL permanente<br/>(registrado em register())"] --> AM{_active_mode?<br/>aba CLOSET + modo seleção ativo}
    AM -- None --> NOP([não desenha])
    AM -- modo --> CL[compute_labels: W/H/D, BAY_W/H/D,<br/>OPEN_H, PART_Z, DRAWER_H, toggles]
    CL --> DRAW[desenha pílulas + rótulos]
    KM["keymap addon LMB (head=True)"] --> CLK[dim_label_click.invoke]
    CLK --> HIT{acertou pílula?}
    HIT -- Grab --> GM[toggle grab]
    HIT -- Add Shelf/Rod --> AP[add_part INVOKE]
    HIT -- Open Door --> OD[open_door_mode]
    HIT -- Dims --> CY[cicla Todos→Seleção→Off]
    HIT -- não --> LB{acertou rótulo?}
    LB -- toggle --> TG[remove_bottom / width_locked]
    LB -- editável --> ED[edit_dim_label modal → _commit]
    LB -- não --> PT([PASS_THROUGH])
    KM2["keymap LMB grab_drag (head=True)"] --> GD{handle sob o cursor?}
    GD -- sim --> DRAG[modal de arraste com snap 32 mm]
    GD -- não --> PT
```
