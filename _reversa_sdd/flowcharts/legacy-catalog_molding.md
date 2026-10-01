# Fluxogramas — módulo legado `catalog_molding`

> Camada legada (herdada do Home Builder 5). Pacotes: `blendertomob/catalog/` e `blendertomob/molding/`.
> Legenda: 🟢 CONFIRMADO (lido no código) · 🟡 INFERIDO · 🔴 LACUNA

## 1. Visão geral do módulo

```mermaid
flowchart LR
    subgraph CATALOG["catalog/ (NÃO registrado pelo add-on 🟢)"]
        CD[catalog_data.CATALOG<br/>lista de dicts] --> PC[props_catalog<br/>Scene.hb_catalog + espelho items]
        PV[previews_catalog<br/>bpy.utils.previews] --> UI[ui_catalog<br/>HB_UL_catalog + HB_CATALOG_PT_browser]
        PC --> UI
        UI -->|botão| OP[ops_catalog<br/>hb_catalog.activate_item]
        OP -->|bpy.ops dinâmico| FF[hb_face_frame.draw_cabinet]
        RT[render_thumbnails<br/>render_entry / render_all] -.sem chamador.-> PV
        UI -.->|hb_catalog.render_thumbnail<br/>operador inexistente 🔴| RT
    end
    subgraph MOLDING["molding/ (registrado em blendertomob/__init__.py 🟢)"]
        HBP[Scene.home_builder<br/>molding_* props] -->|update=| OPS[ops.apply_scene_packages]
        REF[blendertomob.refresh_room_molding] --> OPS
        OPS --> PK[packages<br/>pilhas + perfis]
        OPS --> AD[adapters<br/>alvos + FACTS]
        OPS --> EN[engine<br/>cadeias + offsets]
        AD --> EN
        OPS --> SW[Objetos Curve MoldingSweep<br/>bevel_object = perfil]
    end
    FFUI[face_frame.props_hb_face_frame.draw_molding_ui] --> HBP
    FFUI --> REF
```

## 2. Ciclo de vida do catálogo (register → sync → draw)

```mermaid
flowchart TD
    R[catalog.register] --> R1[previews_catalog.register:<br/>previews.new + carrega no_thumbnail.png]
    R1 --> R2[props_catalog.register:<br/>classes + Scene.hb_catalog + load_post]
    R2 --> R3[schedule_sync → timer one-shot]
    R3 --> T[_deferred_sync: para cada cena<br/>needs_sync? → sync_catalog]
    LP[load_post _catalog_load_post] --> S[sync_catalog em TODAS as cenas]
    D[HB_CATALOG_PT_browser.draw] --> N{needs_sync?<br/>len items != len CATALOG}
    N -- sim --> R3
    N -- não --> V{view_mode}
    V -- GRID --> G[_draw_grid: _filter_visible →<br/>template_icon + botão activate_item]
    V -- DEFAULT --> L[template_list HB_UL_catalog]
    L --> DET{active_index válido?}
    DET -- sim --> DC[_draw_detail: nome, código,<br/>descrição quebrada em 40 col,<br/>botão verbo + Render Thumbnail]
```

## 3. Filtro e ordenação da lista (`HB_UL_catalog.filter_items`)

```mermaid
flowchart TD
    A[filter_items] --> B[_filter_visible state]
    B --> C{category != 'all'?}
    C -- sim --> C1{item.category == cat<br/>ou começa com cat + '/'?}
    C1 -- não --> X[oculta]
    C1 -- sim --> Q
    C -- não --> Q{query não vazia?}
    Q -- sim --> Q1{query ⊂ code+name+desc<br/>OU subsequência fuzzy?}
    Q1 -- não --> X
    Q1 -- sim --> OK[visível]
    Q -- não --> OK
    OK --> F[flags = bitflag_filter_item]
    F --> S{armário FF ou baia selecionados?}
    S -- sim --> O[neworder = sort por _priority<br/>insert/option → 0, demais → 1]
    S -- não --> E[neworder = vazio]
```

## 4. Render de thumbnail (`render_thumbnails.render_entry`)

```mermaid
flowchart TD
    A[render_entry entry] --> B{action_operator ==<br/>hb_catalog.not_yet_implemented?}
    B -- sim --> N[None]
    B -- não --> C[cria cena _hb_thumbnail_render<br/>window.scene = nova; cursor = 0]
    C --> D[op EXEC_DEFAULT com action_args]
    D --> E{FINISHED?}
    E -- não --> N
    E -- sim --> F[cabinet = objeto ativo]
    F --> G[bbox mundo de meshes visíveis<br/>cabinet + children_recursive]
    G --> H{bbox válido e size > 0?}
    H -- não --> N
    H -- sim --> I[câmera esférica: az=-45°, el=25°,<br/>dist = 2×size, lens 50, track -Z/Y]
    I --> J[Workbench 256×256 RGBA transparente,<br/>MATCAP basic_grey.exr + cavity BOTH]
    J --> K[render write_still → catalog/thumbnails/id.png]
    K --> Z[finally: restaura cena, remove cena temporária,<br/>previews_catalog.reload]
    N --> Z
```

## 5. Aplicação de pacotes de moldura (visão geral)

```mermaid
flowchart TD
    U[update de qualquer molding_* ou<br/>operador refresh_room_molding] --> A[apply_scene_packages scene]
    A --> B{scene.home_builder existe<br/>e cena não é LAYOUT/DETAIL?}
    B -- não --> R0[retorna 0]
    B -- sim --> C[clear_scene_molding: remove sweeps<br/>IS_HB_MOLDING_SWEEP + perfis]
    C --> D[monta opts: reveal, stack_offset, cap_offset,<br/>include_recessed, crown_stack, overrides]
    D --> E[para CROWN/top, BASE/bottom, LIGHT_RAIL/bottom]
    E --> F{pacote != NONE?}
    F -- BASE --> F1[_base_stack: troca perfil Base Molding<br/>+ base shoe STACK_FRONT se ligado]
    F1 --> G
    F -- sim --> G[_apply_type]
    F -- não --> E
    G --> E
    E -->|fim| H{molding_crown_furniture_cap?}
    H -- sim --> I[_apply_type CAP / top / FURNITURE_CAP_STACK]
    H -- não --> Z[retorna total de sweeps]
    I --> Z
```

## 6. `_apply_type` — de cabinets a sweeps

```mermaid
flowchart TD
    A[_apply_type] --> B[adapters.collect_targets<br/>FF + frameless por tipo]
    B --> C{há alvos?}
    C -- não --> Z0[0]
    C -- sim --> D{BASE?}
    D -- sim --> D1[+ collect_bridges:<br/>IS_APPLIANCE com z ≤ 0.02]
    D --> E[build_facts]
    D1 --> E
    E --> F[_resolve_stack]
    F --> G[connected_components align]
    G --> H{componente tem algum alvo?}
    H -- não --> G
    H -- sim --> I[order_chain]
    I --> J[para cada entrada da pilha]
    J --> K{BASE?}
    K -- sim --> K1[engine.kick_sweep_segments dx]
    K -- não --> K2[engine.chain_sweep_points dx,dx]
    K1 --> L[_spawn_sweep]
    K2 --> L
    L --> J
```

## 7. `_spawn_sweep` — criação do objeto curva

```mermaid
flowchart TD
    A[_spawn_sweep] --> B[packages.make_profile_object:<br/>pack instalado → senão contorno embutido]
    B --> C{perfil?}
    C -- não --> N[None]
    C -- sim --> D[Curve 2D, bevel_mode OBJECT,<br/>bevel_object = perfil, fill caps]
    D --> E[tags IS_HB_MOLDING_SWEEP, HB_MOLDING_TYPE,<br/>HB_MOLDING_MEMBERS; parent = chain 0]
    E --> F[location.z = _sweep_z]
    F --> G[para cada segmento: localiza em chain 0,<br/>dedup 1e-4, spline BEZIER handles VECTOR]
    G --> H{alguma spline escrita?}
    H -- não --> H1[remove sweep + perfil → None]
    H -- sim --> I[material = acabamento do 1º membro<br/>que resolver estilo]
    I --> Z[sweep]
```
