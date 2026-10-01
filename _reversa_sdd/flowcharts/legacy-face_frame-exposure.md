# `exposure.recalc_cabinet_exposure` — detecção de lados expostos e acabamento automático

> Arquivo: `blendertomob/product_libraries/face_frame/exposure.py:142-476`. Confiança: 🟢 CONFIRMADO.

## Assinaturas
- `recalc_cabinet_exposure(cab_obj) -> None` (`:443`)
- `_side_exposure(cab_obj, side) -> (state, dishwasher_adjacent, wall_edge)` (`:218`)
- `_back_exposure(cab_obj) -> 'UNEXPOSED'|'EXPOSED'` (`:358`)
- `_resolve_finish_type(scene_props, state, dishwasher, side) -> FIN_END id` (`:374`)
- `_resolve_scribe(state, dishwasher, wall_edge, finish) -> float` (`:399`)
- `_apply_side(cab, side, state, dishwasher, wall_edge, scene_props) -> None` (`:416`)

## Fluxograma

```mermaid
flowchart TD
    A["recalc_cabinet_exposure(cab)"] --> B{"é carcaça face frame e não IS_LEG_PRODUCT?"}
    B -- não --> Z["return"]
    B -- sim --> C["para side em left, right"]
    C --> D{"cab tem parent (parede)?"}
    D -- não --> E{"_end_abuts_wall: ponta encostada<br/>em face de parede (tol 1/8in, sobreposição ≥ 1/2in)?"}
    E -- sim --> E1["UNEXPOSED, wall_edge=True"]
    E -- não --> E2["EXPOSED"]
    D -- sim --> F{"x ≤ 0 (esq.) ou x+w ≥ comprimento da parede (dir.)?"}
    F -- sim --> E1
    F -- não --> G["irmãos na parede com borda coincidente (EPS 1e-4)<br/>coleta faixas Z e flag lava-louças"]
    G --> H{"cobertura Z unida"}
    H -- "≥ altura" --> H1["UNEXPOSED"]
    H -- "> 0" --> H2["PARTIAL"]
    H -- "0 / sem vizinho" --> E2
    E1 --> I["_apply_side"]
    E2 --> I
    H1 --> I
    H2 --> I
    I --> J["grava *_exposure e *_dishwasher_adjacent sempre"]
    J --> K{"*_finish_end_auto?"}
    K -- não --> C
    K -- sim --> L["finish: lava-louças → scene.dishwasher_finished_end_type<br/>PARTIAL → FINISHED<br/>EXPOSED → default_finished_end_type (ou _back_type)<br/>UNEXPOSED → UNFINISHED"]
    L --> M["scribe: finish≠UNFINISHED → 0<br/>lava-louças → 1/4in · parede → 1/2in · vizinho → 1/4in"]
    M --> N{"FLUSH_X?"}
    N -- sim --> N1["flush_x_amount = scene.default_flush_x_amount (4in)"]
    N -- não --> O
    N1 --> O["re-arma *_finish_end_auto = True"]
    O --> C
    C --> P["back: parent → UNEXPOSED; costas coincidentes com outra ilha → UNEXPOSED; senão EXPOSED"]
    P --> Q["_apply_side(back)"]
```

## Explicação
- **Prioridade**: lava-louças > parcial > exposto > não exposto (docstring `:5-8`). 🟢
- **Auto flag**: editar o enum de acabamento ou o scribe na UI desliga `*_finish_end_auto`
  (`props_hb_face_frame.py:3983-4009`); a exposição só reescreve lados com auto ligado e religa o flag ao final porque suas
  próprias escritas disparam os callbacks que o desligam. 🟢
- **Efeito no solver**: `left/right_scribe_offset` usa o acabamento: FINISHED → 0, PANELED → 3/4", FLUSH_X/BEADBOARD/SHIPLAP → 1/4",
  demais → scribe digitado (`solver_face_frame.py:379-417`). 🟢
- Cada `setattr` dispara `_update_cabinet_dim` (recálculo completo) fora de `suspend_recalc` → até ~9 recálculos por gabinete. 🟡 (desempenho)
- Premissa geométrica: lados detectados em X local da parede (`cab_obj.location.x`), assumindo gabinetes sem rotação relativa à parede. 🟡
