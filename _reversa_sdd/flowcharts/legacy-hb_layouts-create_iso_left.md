# `MultiView._create_iso_left` — prancha compacta (Iso + Planta + Elevação)

Local: `blendertomob/hb_layouts.py:2397`. Chamado por `MultiView.create` quando `'ISO' in views` (`:2277`). 🟢

## Fluxograma

```mermaid
flowchart TD
    A[_create_iso_left views, dims, view_name] --> B[wall_obj = source_obj]
    B --> C[Localiza source_scene: cena não-layout<br/>que contém wall_obj]
    C --> D[Troca window.scene para source_scene<br/>try/finally restaura]
    D --> E[view_layer.update · Length/Height da parede]
    E --> F[_compute_recursive_bbox<br/>bbox recursivo no espaço local da parede]
    F --> G[bb_w, bb_d, bb_h]
    G --> H[θ_local = 90° + -60° = 30°<br/>iso_view_w = √½·bb_w+bb_d<br/>iso_view_h = √½·sin·bb_w+bb_d + cos·bb_h]
    H --> I[Papel: PAPER_SIZES_INCHES, landscape troca lados<br/>margens 0.5 · base 1.5 in]
    I --> J[Para cada escala em 1/2, 3/8, 1/4, 3/16, 1/8 pol=1 pé]
    J --> K[composed_w = iso_w + iso_gap + wall_length<br/>composed_h = max iso_h, wall_h + plan_gap + bb_d]
    K --> L{cabe em avail_w × avail_h?}
    L -- sim --> M[chosen_scale = escala]
    L -- não --> J
    J -- esgotou --> N[chosen_scale = 1/8 pol=1 pé]
    M & N --> O[Offsets locais:<br/>plan_z = wall_h + plan_gap − bb_min.y<br/>iso_x = −iso_gap − √½·bb_max.x+bb_max.y<br/>iso_z = −√½·sin·bb_min.y−bb_max.x + cos·bb_min.z]
    O --> P[M_elev = I<br/>M_plan = T 0,0,plan_z · Rx 90°<br/>M_iso = T iso_x,0,iso_z · Rx 30° · Rz −45°]
    P --> Q[Para FRONT, PLAN, ISO presentes em views:<br/>instance.matrix_world = W · M_local · W⁻¹]
    Q --> R{FRONT?}
    R -- sim --> S[_add_dashed_cell_instance]
    R -- não --> T
    S --> T[Câmera: x = wall_length − ortho_w/2 + margem_dir<br/>z = ortho_h/2 − margem_inf · y = −10]
    T --> U[matrix_world = T pos · Euler 90°,0,rotZ_parede]
    U --> V[scene.hb_paper_size / hb_paper_landscape / hb_layout_scale = chosen]
    V --> W[Instâncias → SOLID · tracejadas → DASHED]
    W --> X[TitleBlock.create]
```

## Explicação

- **Leitura no depsgraph correto** 🟢 (`:2447-2470`): como `create_scene` já trocou a janela para a cena de layout
  vazia, o método volta temporariamente para a cena de origem antes de avaliar o bbox; caso contrário, descendentes
  fora do depsgraph leriam `matrix_world` identidade e o bbox seria deslocado pela posição mundial da parede
  (comentário longo no código).
- **Projeção isométrica** 🟢 (`:2484-2495`): rotação `Rx(90°+θ) @ Rz(−45°)` com θ = −60°, expressa no referencial
  da câmera que olha para +Y. Tamanho projetado calculado analiticamente a partir do bbox.
- **Escada de escalas** 🟢 (`:2524-2543`): escolhe a MAIOR escala imperial (de 1/2"=1' até 1/8"=1') em que o
  conjunto cabe na área imprimível; se nenhuma couber, usa 1/8"=1' mesmo que transborde. 🟡 A escada é só imperial,
  embora a preferência padrão do fork seja métrica (`1:50`, `blendertomob/__init__.py:141-154`).
- **Âncora na parede** 🟢 (`:2636-2637`): a borda direita da elevação sempre cai em `página − margem direita` e a base em
  `margem inferior (1,5 in)`, qualquer que seja o tamanho da parede.
- **Instâncias por matriz** 🟢 (`:2579-2603`): `M_E = W · M_local · W⁻¹` mantém a elevação na posição nativa (identidade)
  e desloca planta/iso em coordenadas locais da parede.
- **Câmera por `matrix_world`** 🟢 (`:2655-2662`): atribuída diretamente porque `location/rotation_euler` não atualizam
  `matrix_world` antes da avaliação do depsgraph.
- Parâmetros `gap_unused`, `source_loc_unused`, `source_rot_inv_unused` são ignorados 🟢; margens esquerda/superior são
  calculadas e descartadas (`:2622`, `:2624`) 🟢.
