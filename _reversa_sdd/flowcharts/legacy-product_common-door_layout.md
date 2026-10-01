# `door_builder.door_layout` / `layout_min_size` — layout paramétrico da porta

`blendertomob/product_libraries/common/door_builder.py:69-227` 🟢

Todo retângulo de peça é **linear** na largura W ou altura H da porta, como par `(coef, offset)`:
`valor = coef·W + offset` (x/w contra W; z/h contra H) 🟢 (`:14-19`). Isso permite dois realizadores:
estático (`evaluate_layout`, `:215-227`) e com drivers (coifa: compõe os pares em expressões de driver,
`wood_hoods.py:659-749`).

```mermaid
flowchart TD
    A([door_layout info]) --> S{"door_type == 'SLAB'?"}
    S -- Sim --> S1["[slab: x=(0,0) w=(1,0) z=(0,0) h=(1,0)]"]
    S -- Não --> FW["_frame_widths: sw,rw,mrw = max(·, 1/2&quot;)<br/>por lado: None → uniforme; valor → max(v, 0.0)"]
    FW --> PT["p_th = max(panel_thickness, 1/8&quot;)<br/>p_in = max(panel_inset, 0)<br/>k = mid_rail_count, m = mid_stile_count"]
    PT --> BASE["left_stile x=(0,0) w=(0,lsw) h=(1,0)<br/>right_stile x=(1,−rsw) w=(0,rsw)<br/>bottom_rail x=(0,lsw) w=(1,−(lsw+rsw)) h=(0,brw)<br/>top_rail z=(1,−trw) h=(0,trw)"]
    BASE --> K{"k > 0?"}
    K -- Sim --> K1["fh = (1, −(trw+brw+k·mrw))<br/>linha i: z=(fh0·i/(k+1), fh1·i/(k+1)+brw+i·mrw)<br/>h=(fh0/(k+1), fh1/(k+1))<br/>mid rail i (1..k): z = (fh0·i/(k+1), fh1·i/(k+1)+brw+(i−1)·mrw)"]
    K -- Não --> MZ{"mid_rail_z ou add_mid_rail?"}
    MZ -- Sim --> MZ1{"mid_rail_z != None?"}
    MZ1 -- Sim --> MZa["mz = (c, o − mrw/2)  (borda INFERIOR)"]
    MZ1 -- Não --> MZ2{"center_mid_rail?"}
    MZ2 -- Sim --> MZb["mz = (0.5, −mrw/2)"]
    MZ2 -- Não --> MZc["mz = (0, max(mid_rail_location, brw))"]
    MZa --> MR["mid_rail + 2 linhas de painel"]
    MZb --> MR
    MZc --> MR
    MZ -- Não --> R1["1 linha: z=(0,brw) h=(1,−(trw+brw))"]
    K1 --> M{"m > 0?"}
    MR --> M
    R1 --> M
    M -- Sim --> M1["cw = (1/(m+1), −(lsw+rsw+m·msw)/(m+1))<br/>coluna c: x = (c·cw0, c·(cw1+msw)+lsw)"]
    M -- Não --> M2["1 coluna: x=(0,lsw) w=(1,−(lsw+rsw))"]
    M1 --> G["para cada linha: mid stiles (segmentados por linha)<br/>+ painéis (thickness=p_th, y_inset=p_in)"]
    M2 --> G
    G --> OUT([lista de dicts de peças])

    MIN([layout_min_size info]) --> MS{"SLAB?"}
    MS -- Sim --> MS0["(0, 0)"]
    MS -- Não --> MS1["k efetivo = mid_rail_count ou 1 se add_mid_rail/mid_rail_z<br/>min_w = lsw + rsw + m·msw + 1/2&quot;<br/>min_h = trw + brw + k·mrw + 1/2&quot;"]
```

## Explicação

- Precedência do trilho do meio 🟢: `mid_rail_count > 0` vence; senão `mid_rail_z` (par explícito de linha de
  centro) vence `add_mid_rail/center_mid_rail/mid_rail_location` (`:61-65`, `:161-190`).
- Construção de "porta de seis painéis": mid rails correm a largura inteira do campo; mid stiles são
  segmentados por linha de painel e topam nas travessas 🟢 (`:127-130`, `:200-207`).
- Largura por lado 0.0 é honrada (gera membro de largura zero que os realizadores pulam) para portas espelhadas
  que se encostam 🟢 (`:52-55`, `:1303-1304`).
- **Fallback slab**: `layout_min_size` é consumido pela coifa (`wood_hoods.py:729-731`, `:883-886`, `:994-996`,
  `:1304-1307`): se a porta ≤ mínimo, `info = dict(info, door_type='SLAB')`. As frentes de armário usam um
  mínimo PRÓPRIO mais rígido (+1" em vez de +1/2") em `props_hb_face_frame.py` 🟢 — divergência registrada.
