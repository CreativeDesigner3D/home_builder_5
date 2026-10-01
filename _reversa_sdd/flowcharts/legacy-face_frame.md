# Fluxogramas — módulo legado `face_frame` (fork Home Builder 5)

> Camada legada: `blendertomob/product_libraries/face_frame/` (31 arquivos, ~61 mil linhas).
> Gerado pelo Archaeologist (Reversa), nível DETALHADO. Legenda de confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.
> Fluxogramas por função: `legacy-face_frame-solver_walk_tree.md`, `legacy-face_frame-recalculate.md`,
> `legacy-face_frame-distribute_bay_widths.md`, `legacy-face_frame-rail_segments.md`,
> `legacy-face_frame-front_leaves.md`, `legacy-face_frame-exposure.md`.

## 1. Visão geral (arquitetura interna do módulo) 🟢

```mermaid
flowchart TB
    subgraph REG["Registro (__init__.py)"]
        R1["props_hb_face_frame.register<br/>PropertyGroups + Object/Scene pointers + load_post"]
        R2["menus_face_frame.register"]
        R3["operators.register (13 módulos)"]
        R4["ui_face_frame.register"]
        R5["dim_edit_overlay.register<br/>draw handler POST_PIXEL permanente + keymap"]
    end

    subgraph DADOS["Estado persistente (bpy.props em Object)"]
        P1["obj.face_frame_cabinet<br/>Face_Frame_Cabinet_Props"]
        P2["bay.face_frame_bay<br/>Face_Frame_Bay_Props"]
        P3["opening.face_frame_opening<br/>Face_Frame_Opening_Props"]
        P4["split.face_frame_split<br/>Face_Frame_Split_Props"]
        P5["scene.hb_face_frame<br/>Face_Frame_Scene_Props (estilos, padrões, puxadores)"]
    end

    subgraph DOM["Domínio (types_face_frame*.py)"]
        T1["FaceFrameCabinet.create*<br/>cria cage raiz, carcaça, bays, mid stiles"]
        T2["recalculate_face_frame_cabinet<br/>ponto de entrada seguro (guardas)"]
        T3["FaceFrameCabinet.recalculate<br/>distribui → solver → reconcilia partes"]
        T4["CornerFaceFrameCabinet.recalculate<br/>pie-cut / diagonal / pie-cut drawer"]
    end

    subgraph SOLVER["solver_face_frame.py (Python puro, sem drivers)"]
        S1["FaceFrameLayout (snapshot)"]
        S2["segmentos de rails / carcaça / kicks"]
        S3["bay_openings → _walk_tree"]
        S4["front_leaves / interior descriptors"]
    end

    subgraph AUX["Serviços auxiliares"]
        A1["exposure.py — lados expostos / acabamento automático"]
        A2["applied_panel_sizing.py — painéis aplicados"]
        A3["bay_presets.py — receitas de bays"]
        A4["style_options.py / wood_materials.py / finish_colors.py"]
        A5["pulls.py — puxadores (.blend)"]
    end

    subgraph OPS["Operadores (operators/)"]
        O1["ops_placement: place_cabinet / corner / appliance"]
        O2["ops_cabinet: split, change_bay, insert/delete bay, join/break"]
        O3["op_modify_cabinet: arrastar fronteiras (modal+GPU)"]
        O4["ops_part_commands: set width, scribe, editable part"]
        O5["ops_countertop / ops_wedge / ops_finished_ends / ops_styles"]
    end

    REG --> DADOS
    OPS -->|"escrevem props"| DADOS
    DADOS -->|"update callbacks<br/>_update_cabinet_dim"| T2
    T2 --> T3
    T2 --> T4
    T3 --> S1 --> S2 --> T3
    S1 --> S3 --> S4 --> T3
    O1 --> T1 --> T3
    O1 --> A3
    O1 --> A1
    T3 --> A2
    T3 --> A5
    A4 --> P5
```

## 2. Ciclo de vida de um gabinete (colocação → recálculo) 🟢

```mermaid
sequenceDiagram
    participant U as Usuário
    participant OP as place_cabinet (modal)
    participant CL as get_cabinet_class
    participant CAB as FaceFrameCabinet
    participant REC as recalculate_face_frame_cabinet
    participant PR as apply_bay_preset
    participant EX as exposure

    U->>OP: escolhe item do catálogo e move o mouse
    OP->>OP: detecta parede, fill-to-gap, _auto_bay_qty(largura/36")
    U->>OP: clique (confirma)
    OP->>CL: nome do catálogo → classe (CABINET_NAME_DISPATCH)
    CL-->>OP: subclasse (ex.: BaseFaceFrameCabinet)
    OP->>CAB: create(nome, bay_qty)
    CAB->>CAB: create_cabinet_root (props + defaults da cena)
    CAB->>CAB: create_carcass sob guardas _RECALCULATING/_DISTRIBUTING_WIDTHS
    CAB->>CAB: recalculate() inicial
    OP->>CAB: cab_props.width = largura capturada (update → REC)
    OP->>PR: default_bay_config(nome, largura do bay) em suspend_recalc
    PR->>REC: recálculo único ao sair do suspend
    OP->>OP: _try_auto_merge_with_neighbor
    OP->>EX: recalc de exposição (vizinhos)
```

## 3. Árvore de objetos de um gabinete (estrutura de dados na cena) 🟢

```mermaid
flowchart TB
    ROOT["Cabinet cage (GeoNodeCage)<br/>tag IS_FACE_FRAME_CABINET_CAGE<br/>CLASS_NAME, CABINET_TYPE, STYLE_NAME"]
    ROOT --> PARTS["Partes de carcaça (CabinetPart GN)<br/>hb_part_role: LEFT_SIDE, BOTTOM, BACK, TOP / STRETCHERS..."]
    ROOT --> FF["Membros da moldura<br/>LEFT/RIGHT_STILE, TOP/BOTTOM_RAIL (por segmento), MID_STILE (por gap)"]
    ROOT --> BAY["Bay cage (tag IS_FACE_FRAME_BAY_CAGE)<br/>hb_bay_index · face_frame_bay"]
    BAY --> NODE{"Nó raiz da árvore"}
    NODE -->|"folha"| OPEN["Opening cage (IS_FACE_FRAME_OPENING_CAGE)<br/>face_frame_opening"]
    NODE -->|"interno"| SPLIT["Split node (IS_FACE_FRAME_SPLIT_NODE)<br/>face_frame_split · axis H/V"]
    SPLIT --> OPEN
    SPLIT --> SPLIT
    SPLIT -.-> SPL["BAY_MID_RAIL / BAY_MID_STILE<br/>+ BAY_SHELF / BAY_DIVISION (backing)"]
    OPEN --> PIV["Front pivot (FRONT_PIVOT)"] --> FRONT["Door / Drawer / Pullout / False front"] --> PULL["Pull (instância de malha)"]
    OPEN --> INT["Itens internos: prateleiras, rollouts, tray dividers<br/>ou árvore interior (IS_INTERIOR_SPLIT_NODE / IS_INTERIOR_REGION)"]
```

## 4. Hierarquia de classes 🟢

```mermaid
classDiagram
    class GeoNodeCage
    class CabinetPart
    class FaceFrameCabinet {
        +default_width 36in
        +default_height 34.5in
        +default_depth 24in
        +default_cabinet_type BASE
        +single_placement False
        +create_cabinet_root(name)
        +create_carcass(has_toe_kick, bay_qty)
        +insert_bay(anchor_index, direction)
        +delete_bay(bay_index)
        +recalculate()
        +_has_toe_kick() False
        +_has_carcass() True
    }
    GeoNodeCage <|-- FaceFrameCabinet
    FaceFrameCabinet <|-- BaseFaceFrameCabinet
    BaseFaceFrameCabinet <|-- FloatingBaseFaceFrameCabinet
    BaseFaceFrameCabinet <|-- SinkFaceFrameCabinet
    BaseFaceFrameCabinet <|-- FurnitureFaceFrameCabinet
    FurnitureFaceFrameCabinet <|-- FiveDrawerDresserCabinet
    FurnitureFaceFrameCabinet <|-- SixDrawerDresserCabinet
    FurnitureFaceFrameCabinet <|-- NightStandFaceFrameCabinet
    FurnitureFaceFrameCabinet <|-- ThreeDrawerNightStandCabinet
    FurnitureFaceFrameCabinet <|-- WindowSeatFaceFrameCabinet
    FaceFrameCabinet <|-- UpperFaceFrameCabinet
    UpperFaceFrameCabinet <|-- BookcaseUpperFaceFrameCabinet
    UpperFaceFrameCabinet <|-- HutchUpperFaceFrameCabinet
    UpperFaceFrameCabinet <|-- StandardRecessedMedicineCabinet
    UpperFaceFrameCabinet <|-- MedicineCabinetFaceFrameCabinet
    MedicineCabinetFaceFrameCabinet <|-- OverstoolCabinetFaceFrameCabinet
    MedicineCabinetFaceFrameCabinet <|-- TriViewMedicineCabinetFaceFrameCabinet
    FaceFrameCabinet <|-- TallFaceFrameCabinet
    TallFaceFrameCabinet <|-- RefrigeratorCabinet
    TallFaceFrameCabinet <|-- BuiltInTallFaceFrameCabinet
    TallFaceFrameCabinet <|-- BookcaseFaceFrameCabinet
    BookcaseFaceFrameCabinet <|-- BookcaseStorageUnitFaceFrameCabinet
    FaceFrameCabinet <|-- LapDrawerFaceFrameCabinet
    FaceFrameCabinet <|-- PanelFaceFrameCabinet
    PanelFaceFrameCabinet <|-- FaceFrameAndDoorsCabinet
    PanelFaceFrameCabinet <|-- MirrorFrameFaceFrameCabinet
    PanelFaceFrameCabinet <|-- TubSkirtFaceFrameCabinet
    FaceFrameCabinet <|-- LegProductFaceFrameCabinet
    FaceFrameCabinet <|-- FloatingShelfFaceFrameCabinet
    FaceFrameCabinet <|-- ValanceFaceFrameProduct
    FaceFrameCabinet <|-- CornerFaceFrameCabinet
    CornerFaceFrameCabinet <|-- BasePieCutCabinet
    CornerFaceFrameCabinet <|-- UpperPieCutCabinet
    CornerFaceFrameCabinet <|-- BaseDiagonalCabinet
    CornerFaceFrameCabinet <|-- UpperDiagonalCabinet
    CornerFaceFrameCabinet <|-- TallDiagonalCabinet
    CornerFaceFrameCabinet <|-- BasePieCutDrawerCabinet
    CabinetPart <|-- MiscPart
    CabinetPart <|-- DoorPart
    class HalfWallFaceFrameProduct
    class SupportFrameFaceFrameProduct
    note for FurnitureFaceFrameCabinet "Subclasses de Furniture, BookcaseUpper, Hutch e BookcaseStorageUnit NÃO estão em WRAP_CLASS_REGISTRY: no recálculo via callback são embrulhadas como FaceFrameCabinet base (ver regra FACE_FRAME-R34)"
```

Fontes: `types_face_frame.py:941` (FaceFrameCabinet), `:6940-8467` (subclasses), `types_face_frame_corner.py:211,2828-2960`,
`types_face_frame.py:8636-8680` (WRAP_CLASS_REGISTRY), `types_face_frame_corner.py:2979` (registro de cantos).

## 5. Máquina de estados de "lock" de tamanhos (auto-lock on edit) 🟢

```mermaid
stateDiagram-v2
    [*] --> Distribuido: criação (unlock_* = False)
    Distribuido --> Distribuido: recálculo do sistema<br/>(escrita dentro de _DISTRIBUTING_WIDTHS, sem lock)
    Distribuido --> Travado: usuário edita bay.width / kick_height / interior size<br/>(callback liga unlock_* = True)
    Travado --> Travado: usuário ajusta valor → recálculo redistribui os outros
    Travado --> Distribuido: usuário desliga unlock_* (ou change_bay reseta)
    note right of Travado
      Opening.size e Split.size NÃO têm auto-lock no callback:
      overlay/diálogos precisam ligar unlock_size antes (dim_edit_overlay,
      split_opening, _build_recipe_into).
    end note
```
Fontes: `props_hb_face_frame.py:4031` (`_update_bay_width`), `:4059`, `:4080`, `:5976-5984`, `operators/ops_cabinet.py:2020-2062`.
