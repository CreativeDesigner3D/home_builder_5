# `hb_frameless_OT_place_cabinet` — inserção modal em parede/piso

Local: `blendertomob/product_libraries/frameless/operators/ops_placement.py:270-1863` 🟢
Base: `WallObjectPlacementMixin` (`:60-268`) ← `hb_placement.PlacementMixin` (módulo externo).
Entrada: `hb_frameless.draw_cabinet` (`:1927-1977`) mapeia nome → `cabinet_type`/`is_appliance`.

Legenda: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA.

```mermaid
flowchart TD
    A["execute(): init_placement; reset estado<br/>fill_mode = hb_frameless.fill_cabinets<br/>max_single_cabinet_width = 36in"] --> A1{"cabinet_name"}
    A1 -- "Floating Shelves / Valance" --> A2["cursor_z_tracking; tipo UPPER; z inicial = 54in"]
    A1 -- "Support Frame" --> A3["align_top_to_base; fill_mode"]
    A1 -- outros --> A4
    A2 & A3 & A4["create_preview_cage (ARRAY count=qtd) + create_dimensions"] --> B["modal_handler_add → RUNNING_MODAL"]
    B --> C{"evento"}
    C -- "↑/↓" --> D["auto_quantity=False; qtd±1<br/>largura = gap/qtd se posição travada"]
    C -- "teclas W/H/←/→/dígitos" --> E["handle_typing_event → largura/altura/offset digitados"]
    C -- MOUSEMOVE --> F["esconde preview; update_snap (raycast)"]
    F --> G{"hit em parede com modifier GN?"}
    G -- não --> G1["find_nearest_wall_from_cursor (≤ 6in)"]
    G -- sim --> H
    G1 -- achou --> H["set_position_on_wall"]
    G1 -- não --> I["set_position_free: snap a gabinete vizinho ou grade"]
    H --> H1["lado frente/verso por Y local (histerese 1in)"]
    H1 --> H2["find_placement_gap_by_side → gap_start/gap_end"]
    H2 --> H3{"fill_mode?"}
    H3 -- sim --> H4["qtd = ceil(gap/36in); largura = gap/qtd; x=gap_start"]
    H3 -- não --> H5{"sobre cage sem colisão Z (janela)?"}
    H5 -- sim --> H6["centraliza no cage"]
    H5 -- não --> H7["centro do gap se Δ menor que 4in; borda esq. se menor que 4in; senão grade"]
    H4 & H6 & H7 --> H8{"'Corner' no nome?"}
    H8 -- sim --> H9["perto da ponta (≤ largura): x=0 ou x=L com rot −90°"]
    H8 -- não --> H10["clamp [0, L-total]; verso: x+=total, y=espessura, rot 180°"]
    C -- "LMB / Enter" --> J["create_final_cabinets → get_cabinet_class().create()"]
    J --> K["por gabinete (não eletro): assign_cabinet_style → run_calc_fix ×2 → door styles → calculate_shelf_quantity"]
    K --> L["toggle_mode; cleanup; FINISHED"]
    C -- "RMB / Esc" --> M["cleanup; CANCELLED"]
```

## Regras

- 🟢 Largura máxima por gabinete no preenchimento automático: 36in (914,4 mm); `qtd = ceil(gap/36in)` (`:1057-1063`, `:1690`).
- 🟢 Snap de centro: 4in (101,6 mm) do centro do gap; snap à borda esquerda se < 4in (`:1258-1267`).
- 🟢 Parede mais próxima (fallback): 6in (152,4 mm) (`:1085`).
- 🟢 Z de inserção: UPPER = `default_wall_cabinet_location` (54in); Lap Drawer = `base_h − top_drawer_front_height`; coifa = 54in fixo ("36in fogão + 18in"); Support Frame = `base_h − altura`; demais 0 (`:464-488`).
- 🟢 Altura da coifa = `ceiling_height − 54in` (`:490-499`).
- 🟢 Mapeamento nome→classe: "Base Drawer" gera `3 Drawers`; "Base Door Drw" gera `Door Drawer`; "Tall Stacked"/"Upper Stacked" ligam `is_stacked`; nomes com "Pie Cut Corner"/"L-Shape Corner"/"Diagonal Corner" + Base/Tall/Upper → classes de canto (`:1455-1509`).
- 🟢 `props.base_exterior` (enum com padrão 'Door Drawer') **não é usado**: o exterior vem de `default_exterior` da instância (`types_frameless.py:555-570`).
- 🟢 `run_calc_fix` é chamado 2× por gabinete como contorno do bug Blender #133392 (drivers de netos) (`:1837-1839`).
- 🟡 O modal começa em `execute()` (não há `invoke`), funcionando porque é chamado com `'INVOKE_DEFAULT'`; chamado via `EXEC_DEFAULT` entraria em modal sem evento válido.
- 🟢 O cursor é restaurado em ambos os caminhos de saída; não há `draw_handler` neste operador (cotas são objetos GN).
