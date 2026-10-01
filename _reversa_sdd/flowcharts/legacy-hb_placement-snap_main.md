# `hb_snap.main` / `best_hit` / `snap_to_grid` — raycast e snapping de cursor

Local: `blendertomob/hb_snap.py:193-210` (main), `48-82` (best_hit), `100-145` (snap a geometria), `153-191` (grade) 🟢.
Chamado por `PlacementMixin.update_snap` (`hb_placement.py:158-173`), que antes converte o mouse para coordenadas da região sob o cursor (`hb_snap.get_region`, `hb_snap.py:10-29`).

Efeitos colaterais no operador (`self`): `hit_location`, `hit_face_index`, `hit_object`, `view_point`, `hit_grid`.

```mermaid
flowchart TD
    U[update_snap] --> R1[get_region mouse_x, mouse_y<br/>área VIEW_3D sob o mouse, 1ª região com .data]
    R1 --> R2["mouse_pos = (mouse_x − region.x, mouse_y − region.y)"]
    R2 --> M[main self, event.ctrl]
    M --> A[view_layer.update  ← a cada tick]
    A --> B[scene.ray_cast da origem da vista na direção do cursor]
    B --> C{hit e objeto sem HB_CURRENT_DRAW_OBJ?}
    C -- sim --> H[hit direto]
    C -- não --> RING["anel: 6 raios a 50 px, ângulos 0,60°,…,300°"]
    RING --> RB[escolhe o hit válido mais próximo do view_point]
    RB --> H
    H --> D{result}
    D -- True + Ctrl --> SO{objeto MESH?}
    SO -- sim --> SO1[vértices do polígono hit_face_index no mesh avaliado]
    SO1 --> SG1[snap_to_geometry]
    SO -- não --> END
    D -- True sem Ctrl --> END[fim: hit_location = ponto do raio]
    D -- False --> G[snap_to_grid]
    G --> G1{"vista lateral alinhada a eixo?<br/>region.data.is_orthographic_side_view"}
    G1 -- sim --> G2[normal do plano = view_vector]
    G1 -- não --> G3["normal = (0,0,1)"]
    G2 & G3 --> G4["scale = 10^(round(log10(view_distance)) − 1)"]
    G4 --> G5[intersect_line_plane pela origem]
    G5 --> G6{Ctrl?}
    G6 -- sim --> G7[quad da célula floor/ceil em scale → snap_to_geometry]
    G6 -- não --> G8
    G7 --> G8[se hit_location None → interseção]

    subgraph snap_to_geometry
        V1["vértice mais próximo em tela com distância < 50 px"] -->|achou| VX[hit_location = vértice]
        V1 -->|não achou| V2[para cada aresta: busca dicotômica<br/>search_edge_pos eps 1e-4 m]
        V2 --> V3["ponto de aresta < 50 px mais próximo"]
    end
```

## Utilitários de grade para valores

- 🟢 `snap_value_to_grid(value, unit_settings=None, fine=False)` (`hb_snap.py:212-236`): imperial 1" (fino 1/16"); demais sistemas 10 mm (fino 1 mm); `round(value/grid)*grid`.
- 🟢 `snap_vector_to_grid` (`l.239-254`): aplica em X e Y, mantém Z.

## Achados

- 🟢 `HB_CURRENT_DRAW_OBJ` (propriedade custom) exclui do raycast o objeto sendo desenhado.
- 🟢 No fallback do anel, `view_point` retornado é o do **último** raio (`l.82`), não o do raio vencedor (diferença desprezível, mesma origem em perspectiva; 🟡 em ortográfica a origem varia com o pixel).
- 🟡 `Scene.ray_cast` devolve `index = -1` quando os dados originais não estão disponíveis (`docs/rag/blender-api/corpus/bpy.types.Scene.md#bpy.types.Scene.ray_cast`); `snap_to_object` indexa `data.polygons[self.hit_face_index]` no mesh **avaliado** — com `-1` pegaria o último polígono, e em objetos com modificadores GN o índice pode não corresponder ao mesh avaliado.
- 🟢 `context.view_layer.update()` a cada MOUSEMOVE (`l.50`) — custo alto em cenas grandes, mas coerente com `docs/rag/project/04_armadilhas.md` (dados desatualizados).
- 🟢 Se `get_region` retornar `None` no `init_placement` (sem viewport 3D) e também no `update_snap`, `self.region.x` falha com `AttributeError` (`hb_placement.py:169-172`).
