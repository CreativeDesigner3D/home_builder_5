# `ElevationView.create` — elevação de parede

Local: `blendertomob/hb_layouts.py:1447` (+ `_fit_camera_to_content` `:1504`, `add_cabinet_dimensions` `:1580`,
`_create_cabinet_dimension` `:1636`, `_create_content_collections` `:1681`, `_collect_objects_split` `:1752`). 🟢
Chamado por `home_builder_layouts.create_elevation_view` e `create_all_elevations` (`blendertomob/operators/layouts.py:302`, `:368`).

## Fluxograma

```mermaid
flowchart TD
    A[create wall_obj, name, paper LETTER, landscape] --> B[GeoNodeWall: Length, Height]
    B --> C[create_scene 'Parede Elevation'<br/>IS_ELEVATION_VIEW · SOURCE_WALL]
    C --> D[Câmera ORTHO rot 90°,0,rotZ_parede<br/>pos = M·L/2,−2,H/2]
    D --> E[set_paper_size]
    E --> F[add_cabinet_dimensions]
    F --> F1{filho é cage de gabinete<br/>FRAMELESS ou FACE_FRAME?}
    F1 -- sim --> F2{z local > 1,2 m?}
    F2 -- sim --> F3[uppers]
    F2 -- não --> F4[base/tall]
    F3 & F4 --> F5[Ordena por x]
    F5 --> F6[base: cota em z = −4 in, leader −4 in]
    F5 --> F7[uppers: z = max topo + 4 in, leader +4 in]
    F6 & F7 --> G[_fit_camera_to_content]
    G --> G1[bbox: parede 0..L × 0..H<br/>+ bound_box de filhos MESH não-cage/helper<br/>+ cotas IS_2D_ANNOTATION ±0,1 / ±0,25 m]
    G1 --> G2[margem = 10% do maior lado, ambos os eixos]
    G2 --> G3[câmera em centro, y = −3 m · ortho = max w,h]
    G3 --> H[_create_content_collections]
    H --> H1[Collection da parede Solid → instância SOLID]
    H1 --> H2{filho é cage FRAMELESS / FACE_FRAME / CLOSET_STARTER?}
    H2 -- sim --> H3[_collect_objects_split recursivo<br/>INTERIOR_PART → Dashed, resto → Solid]
    H3 --> H4[Instância Solid; Dashed só se não vazio<br/>senão remove a collection]
    H2 -- não, e não cage/helper --> H5[linka na collection da parede]
    H4 & H5 --> I[TitleBlock.create]
    I --> J[return scene]
```

## Explicação

- **Classificação de gabinetes para cotas** 🟢 (`:1613-1617`): limiar fixo de 1,2 m (48") sobre a posição Z local do
  cage decide se o gabinete é "superior" (cota acima) ou "base/alto" (cota abaixo). Só filhos DIRETOS da parede com
  `IS_FRAMELESS_CABINET_CAGE`/`IS_FACE_FRAME_CABINET_CAGE` recebem cota — closets não (🟢 `:1595`).
- **Cotas** 🟢: `GeoNodeDimension` com comprimento no ponto 1 do spline = `Dim X` do cage; afastadas 2" à frente da
  parede (`-units.inch(2)` em Y local); `Leader Length` ±4". O objeto é renomeado para `Dim_<cage>` porque
  `create_curve` ignora o nome (`:1641-1645`) e é removido de qualquer cena onde foi linkado por `bpy.context.scene`.
- **Enquadramento** 🟢: margem 10% do maior lado; `ortho_scale = max(largura, altura)` — ignora a razão de aspecto do
  papel (🟡 conteúdo muito alto/estreito pode ser cortado em papel paisagem, pois ortho_scale aplica-se ao lado maior
  da resolução).
- **Divergência com `update()`** 🟢 (`:1780-1801`): a atualização recalcula a câmera com outra regra (y = −2 m, margem
  fixa 0,2 m, sem cotas nem filhos) e não reconstrói collections nem cotas.
- As collections de conteúdo linkam os OBJETOS ORIGINAIS da sala (sem cópia); a vista é uma instância de collection 🟢.
