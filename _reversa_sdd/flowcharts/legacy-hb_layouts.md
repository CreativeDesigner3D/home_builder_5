# Fluxogramas — módulo legado `hb_layouts`

> Camada legada (fork do Home Builder 5). Arquivos: `blendertomob/hb_layouts.py`, `blendertomob/hb_details.py`,
> `blendertomob/hb_detail_library.py`, `blendertomob/hb_assets.py`.
> Legenda de confiança: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

## 1. Visão geral do módulo 🟢

```mermaid
flowchart LR
    subgraph OPS["operators/layouts.py · operators/details.py · ui/view3d_sidebar.py"]
        OP_EL[create_elevation_view]
        OP_PL[create_plan_view]
        OP_3D[create_3d_view]
        OP_ALL[create_all_elevations]
        OP_MV[create_multi_view]
        OP_DET[operadores de detalhe]
    end

    subgraph LAY["hb_layouts.py"]
        LV[LayoutView<br/>create_scene / câmera / papel]
        EV[ElevationView]
        PV[PlanView]
        V3[View3D]
        MV[MultiView]
        TB[TitleBlock]
        LA[Line Art GP<br/>setup / sizes / bake / holdouts]
        FS[Freestyle linesets<br/>Solid / Dashed / Iso]
    end

    subgraph DET["hb_details.py"]
        DV[DetailView]
        GL[GeoNodeLine / Polyline / Circle / Text]
        LS[apply_label_style]
    end

    subgraph LIB["hb_detail_library.py"]
        IDX[(library_index.json<br/>+ *.blend)]
    end

    subgraph AST["hb_assets.py"]
        REG[ensure_asset_libraries]
        PREF[(Preferences.filepaths<br/>.asset_libraries)]
        ENTRY[BTM_AssetLibraryEntry]
    end

    OP_EL --> EV
    OP_PL --> PV
    OP_3D --> V3
    OP_ALL --> EV
    OP_MV --> MV
    EV & PV & V3 & MV --> LV
    LV --> FS
    LV --> LA
    EV & PV & V3 & MV --> TB
    OP_DET --> DV
    OP_DET --> GL
    GL --> LS
    OP_DET --> IDX
    REG --> PREF
    ENTRY --> REG
```

## 2. Criação de uma cena de layout (base comum) 🟢

`LayoutView.create_scene` (`blendertomob/hb_layouts.py:1141`) → `_setup_render_settings` (`:1194`).

```mermaid
flowchart TD
    A[create_scene name] --> B[Guarda unit_settings e snap<br/>da cena atual]
    B --> C[bpy.data.scenes.new<br/>scene IS_LAYOUT_VIEW = True]
    C --> D[window.scene = nova cena]
    D --> E[Copia unidades, product_tab e snap]
    E --> F[_setup_render_settings]
    F --> G[Workbench · AA 32 · cor OBJECT · luz FLAT · SOLID]
    G --> H[_create_freestyle_collections<br/>Scene_Freestyle_Ignore / Dashed / Solid]
    H --> I{get_default_line_engine<br/>== LINEART?}
    I -- sim --> J[render.use_freestyle = False<br/>view_layer.use_freestyle = False]
    J --> K[_setup_lineart → setup_line_art_for_scene]
    K --> L[scene HB_LINE_ENGINE = LINEART]
    I -- não --> M[render.use_freestyle = True]
    M --> N[_setup_freestyle_linesets<br/>Solid 1.5px · Dashed HIDDEN 1.0px dash 10/5]
    N --> O[scene HB_LINE_ENGINE = FREESTYLE]
```

## 3. Tipos de vista e despacho 🟢

`get_layout_view_from_scene` (`blendertomob/hb_layouts.py:2960`).

```mermaid
flowchart TD
    S[scene] --> A{IS_LAYOUT_VIEW?}
    A -- não --> N[None]
    A -- sim --> B{IS_ELEVATION_VIEW?}
    B -- sim --> EV[ElevationView scene]
    B -- não --> C{IS_PLAN_VIEW?}
    C -- sim --> PV[PlanView scene]
    C -- não --> D{IS_3D_VIEW?}
    D -- sim --> V3[View3D scene]
    D -- não --> E{IS_MULTI_VIEW?}
    E -- sim --> MV[MultiView scene]
    E -- não --> LV[LayoutView scene]
```

## 4. PlanView.create 🟢

`blendertomob/hb_layouts.py:1819`.

```mermaid
flowchart TD
    A[create name, source_scene, paper] --> B[create_scene + IS_PLAN_VIEW]
    B --> C[set_paper_size]
    C --> D[Varre source_scene.objects<br/>ou bpy.data.objects]
    D --> E{objeto tem IS_WALL_BP?}
    E -- sim --> F[start = M·0 · end = M·Length<br/>atualiza min/max X,Y]
    E -- não --> D
    F --> D
    D --> G{Há paredes?}
    G -- não --> H[center 0,0,5 · size 10]
    G -- sim --> I[center = meio do bbox, z=5<br/>size = max w,h + 1 m]
    H & I --> J[create_camera ORTHO rot 0,0,0<br/>ortho_scale = size]
    J --> K[Collection 'name Content'<br/>paredes + filhos sem cage/helper]
    K --> L[Empty instanciando Content<br/>→ Freestyle_Solid]
    L --> M[TitleBlock.create]
```

## 5. View3D.create 🟢

`blendertomob/hb_layouts.py:1992`.

```mermaid
flowchart TD
    A[create name, perspective, source_scene] --> B[create_scene + IS_3D_VIEW]
    B --> C{engine da cena == LINEART?}
    C -- sim --> D[remove_line_art_from_scene<br/>força Freestyle]
    C -- não --> E
    D --> E[set_paper_size]
    E --> F{Há paredes IS_WALL_BP?}
    F -- sim --> G[avg_center = média dos centros das paredes<br/>camera = avg + 8,-8,8]
    F -- não --> H[camera 8,-8,8 · alvo origem]
    G & H --> I{perspective?}
    I -- sim --> J[PERSP lens 35]
    I -- não --> K[ORTHO ortho_scale 10]
    J & K --> L[to_track_quat -Z,Y aponta para o centro]
    L --> M[Content + Instance → Freestyle_Solid]
    M --> N[TitleBlock.create]
```

## 6. MultiView.create — layout em cruz 🟢

`blendertomob/hb_layouts.py:2205`. O ramo ISO desvia para `_create_iso_left` (ver `legacy-hb_layouts-create_iso_left.md`).

```mermaid
flowchart TD
    A[create source_obj, views, paper TABLOID] --> B{views vazio?}
    B -- sim --> Z[return None]
    B -- não --> C[_get_object_dimensions<br/>Dim X/Y/Z do cage ou dimensions]
    C --> D[create_scene + IS_MULTI_VIEW + SOURCE_OBJECT]
    D --> E[Content collection + _add_object_to_collection]
    E --> F[_build_dashed_content_collection<br/>MOVE peças internas ocultas]
    F --> G[decompose matrix_world da origem]
    G --> H{'ISO' em views?}
    H -- sim --> ISO[_create_iso_left]
    H -- não --> I[Calcula limites visuais<br/>Front no 0,0 · Plan acima · Back acima<br/>Left à esquerda · Right à direita · gap 12 in]
    I --> J[Para cada view: Empty instância<br/>rot = Euler base @ R_origem⁻¹]
    J --> K[pos = _calculate_instance_position − rot·loc_origem]
    K --> L{view ∉ PLAN, ISO?}
    L -- sim --> M[_add_dashed_cell_instance]
    L -- não --> N
    M --> N[Bounds totais → ortho = max w,h + 2·6 in]
    N --> O[Câmera ORTHO em center, z=10<br/>scale = ortho_scale]
    O --> P[Instâncias → Solid · tracejadas → Dashed]
    P --> Q[TitleBlock.create]
```

## 7. Pipeline Line Art (Grease Pencil) 🟢

```mermaid
flowchart TD
    A[setup_line_art_for_scene] --> B[remove_line_art_from_scene]
    B --> C[IGNORE.lineart_usage = EXCLUDE]
    C --> D[GP 'Scene_LineArt' tag IS_HB_LINEART<br/>cor preta · in_front · hide_select]
    D --> E[Materiais HB_LineArt_Solid / Dashed]
    E --> F[Camadas Solid, Dashed com keyframe]
    F --> G[Mod Lineart Solid · SOLID · nível 0]
    G --> H[Mod Lineart Dashed · DASHED · níveis 1..128]
    H --> I[Resample Dashed SIMPLIFY SAMPLE]
    I --> J[Dash Hidden 3 pontos / 2 gap]
    J --> K[update_line_art_sizes]
    K --> L[paper_to_world das larguras × fatores da cena]
    L --> M[_ensure_lineart_camera<br/>câmera jitter 0,05°]
    M --> N[mods LINEART usam câmera jitter]

    P[build_line_art_marked_channel] -.-> K
    Q[build_line_art_text_holdouts] --> R[_apply_holdout_masks<br/>ops grease_pencil.layer_mask_add]
    S[bake_line_art_editable] --> T[Snapshot depsgraph → strokes reais<br/>desliga modificadores · HB_LINEART_BAKED]
    U[unbake_line_art] --> V[Limpa frames · religa mods · refresh_line_art]
```

## 8. Detalhes 2D e biblioteca de detalhes 🟢

```mermaid
flowchart TD
    A[DetailView.create name] --> B[Nome único 'name N']
    B --> C{cena atual é room?}
    C -- sim --> D[hb_utils.save_view_state]
    C -- não --> E
    D --> E[scenes.new · IS_DETAIL_VIEW · troca janela]
    E --> F[Copia unidades, product_tab, snap]
    F --> G[_setup_2d_view: vista de topo + SOLID/OBJECT]

    H[save_detail_to_library] --> I{IS_DETAIL_VIEW ou IS_CROWN_DETAIL?}
    I -- não --> X1[False 'Not in a detail view']
    I -- sim --> J[Objetos CURVE/FONT/MESH da cena]
    J --> K{lista vazia?}
    K -- sim --> X2[False]
    K -- não --> L[filename = nome limpo + timestamp .blend]
    L --> M[libraries.write objs+data+materiais fake_user]
    M --> N[Append entrada em library_index.json]

    O[load_detail_from_library] --> P{detalhe? arquivo existe?}
    P -- sim --> Q[libraries.load link=False → objects]
    Q --> R[link na cena · seleciona · ativo = 1º]
```

## 9. Registro de bibliotecas de assets 🟢

Detalhe em `legacy-hb_layouts-ensure_asset_libraries.md`.

```mermaid
flowchart TD
    A[register do add-on] --> B[hb_assets.register classes]
    B --> C[ensure_asset_libraries]
    C --> D[remove 'Home Builder Extended' legado]
    D --> E[registra 'Home Builder' → blendertomob/assets]
    E --> F[Para cada entrada: internal_id + _register_user_entry]
    F --> G[_cleanup_orphaned_libraries]
    H[unregister] --> I[remove_asset_libraries] --> J[unregister classes]
```
