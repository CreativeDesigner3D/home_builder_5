# `door_builder.build_door_mesh` — construção da porta

`blendertomob/product_libraries/common/door_builder.py:1202-1404` 🟢

Assinatura: `build_door_mesh(mesh, info, width, height, thickness, materials=None, outer_section=None,
inner_section=None, panel_section=None, inner_rail_section=None, inner_stile_section=None, member_section=None,
applied_section=None, applied_scope='ALL', panel_grooves=None, mullion=None, shape=None) -> None`
(efeito colateral: substitui a geometria de `mesh`).

Espaço de saída (cutpart local da frente): altura da porta em **+X** a partir da borda inferior, largura em
**−Y** com a borda ESQUERDA em y=0 (cutpart com Mirror Y), face frontal em **z = thickness** 🟢 (`:1208-1215`).
Mapeamento interno de cada emissor: `(x_porta, z_porta, v) → (z_porta, −x_porta, T − v)` 🟢 (`:272-276`, `:369-371`).

```mermaid
flowchart TD
    A([build_door_mesh]) --> B{"member_section != None<br/>e door_type != SLAB?"}
    B -- Sim: MITERED --> B1["build_mitered_frame: 1 varredura do perfil<br/>em volta da porta, meia-esquadria nos 4 cantos<br/>+ face traseira plana até o hull das aberturas"]
    B -- Não: FRAMED/SLAB --> B2["verts/faces/slots vazios"]
    B1 --> C
    B2 --> C["parts = evaluate_layout(info, W, H)"]
    C --> D{"shape != None e não mitered<br/>e não SLAB?"}
    D -- Sim --> D1["para cada célula da linha de TOPO<br/>(e de BASE se double): rise = min(shape_rise, cap)<br/>_shape_curve_pts → shaped_top/bottom[id(p)]<br/>e top_rail_segs / bottom_rail_segs"]
    D -- Não --> E
    D1 --> E["para cada part"]
    E --> E0{"mitered e key != panel?"}
    E0 -- Sim --> E
    E0 -- Não --> E1{"largura ou altura <= 0?<br/>(lado com largura 0.0)"}
    E1 -- Sim: pula --> E
    E1 -- Não --> P{"key == panel?"}
    P -- Sim --> P0["cells.append(part)"]
    P0 --> R{"panel_section?"}
    R -- Sim --> R1{"_emit_raised_panel ok?<br/>(célula > 2·field_u e back_v > 0)"}
    R1 -- Sim --> E
    R1 -- Não --> BOX
    R -- Não --> G{"panel_grooves?"}
    G -- Sim --> G1{"_emit_grooved_panel ok?"}
    G1 -- Sim --> G2["células arqueadas: tampa plana<br/>_emit_shaped_panel acima/abaixo do ombro"] --> E
    G1 -- Não --> SH
    G -- Não --> SH{"célula arqueada?"}
    SH -- Sim --> SH1["_emit_shaped_panel (prisma com borda curva)"] --> E
    SH -- Não --> BOX
    P -- Não --> TR{"top_rail com segs arqueados?"}
    TR -- Sim --> TR1{"_emit_shaped_rail('TOP') ok?"}
    TR1 -- Sim --> E
    TR1 -- Não --> BR
    TR -- Não --> BR{"bottom_rail com segs?"}
    BR -- Sim --> BR1{"_emit_shaped_rail('BOTTOM') ok?"}
    BR1 -- Sim --> E
    BR1 -- Não --> OE
    BR -- Não --> OE{"outer_section e key ∈ _OUTLINE_EDGE_KEYS?"}
    OE -- Sim --> OE1{"_emit_edge_profiled_box ok?<br/>(lado no contorno e u_max cabe)"}
    OE1 -- Sim --> E
    OE1 -- Não --> BOX
    OE -- Não --> BOX["caixa retangular 8 verts / 6 faces<br/>th = thickness ou part.thickness; zf = T − y_inset<br/>slot = _PART_MAT_SLOT[key]"]
    BOX --> E
    E -->|fim do loop| ST{"não mitered, não SLAB e<br/>inner/rail/stile section?"}
    ST -- Sim --> ST1["para cada célula: _emit_strip_rings<br/>(sticking aplicado, lr/ls com fallback cruzado,<br/>segue curva se arqueada)"]
    ST -- Não --> AP
    ST1 --> AP{"applied_section e não mitered/SLAB?"}
    AP -- Sim --> AP1["para cada célula: _emit_strip_rings(applied, scope)"]
    AP -- Não --> MU
    AP1 --> MU{"mullion e não SLAB?<br/>(vale também p/ mitered)"}
    MU -- Sim --> MU1["para cada célula: _emit_mullion_bars<br/>(recorta sob a curva)"]
    MU -- Não --> Z
    MU1 --> Z["mesh.clear_geometry(); from_pydata;<br/>materials (stile, rail, panel);<br/>atributo material_index FACE ← slots; mesh.update()"]
```

## Explicação

- **Três construções** 🟢: *FRAMED* (padrão: montantes/travessas como caixas retangulares, perfil interno como
  **sticking strip aplicado** varrido em volta de cada abertura, `:1363-1376`); *MITERED* (`member_section`:
  todo o membro é um perfil, varrido com meia-esquadria, `:1249-1253`, `:250-321`); *APPLIED* (moldura decorativa
  adicional por abertura, `:1377-1384`, com `applied_scope='RAILS'` só em cima/baixo, `:373-399`).
- **Cadeia de fallback por peça** 🟢: raised → grooved → shaped flat → shaped rail → edge-profiled → caixa simples.
  Toda função emissora devolve `False` quando a geometria não cabe e a peça cai para a caixa simples.
- **Slots de material** 🟢: 0 = stile (inclui slab, mid_stile e barras de mullion), 1 = rail (inclui mid_rail e
  strips de sticking das travessas), 2 = panel (`:232-235`, `:432-433`, `:1050`).
- **Mitered ignora** `shape`, sticking e applied, mas **aceita mullion** 🟢 (`:1267`, `:1366`, `:1379`, `:1385-1388`).
- **Arcos**: o chamador alarga a travessa pelo rise para preservar a largura de catálogo na crista 🟢
  (`:1241-1242`; consumidor `props_hb_face_frame.py` usa `shape_rise`).
- **Z-fighting**: barras curvas escalonadas em profundidade `(i+1)·0.0002 m` 🟢 (`:1045-1050`).
