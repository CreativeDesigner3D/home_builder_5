# `PlacementMixin.handle_typing_event` + `parse_typed_distance` — entrada numérica

Locais: `blendertomob/hb_placement.py:191-250` (eventos) e `283-388` (parser) 🟢.

## Tratamento de teclas

```mermaid
flowchart TD
    A[evento] --> B{state == PLACING?}
    B -- sim --> B1{tipo ∈ NUMBER_KEYS e PRESS?}
    B1 -- sim --> B2["se target NONE → get_default_typing_target()<br/>state=TYPING; typed_value = char<br/>on_typed_value_changed()"] --> T[True]
    B1 -- não --> C
    B -- não --> C{state == TYPING?}
    C -- não --> FL[False]
    C -- sim --> D{value == PRESS?}
    D -- não --> FL
    D -- sim --> E{tipo}
    E -- NUMBER_KEYS --> E1[typed_value += char; on_typed_value_changed] --> T
    E -- BACK_SPACE --> E2{typed_value vazio?}
    E2 -- não --> E3[remove último; on_typed_value_changed] --> T
    E2 -- sim --> E4[stop_typing → PLACING] --> T
    E -- RET/NUMPAD_ENTER --> E5[apply_typed_value] --> T
    E -- ESC --> E6[stop_typing] --> T
    E -- TAB --> E7{get_next_typing_target ≠ NONE?}
    E7 -- sim --> E8[apply_typed_value; start_typing next] --> T
    E7 -- não --> T
    E -- outro --> FL
```

Pontos 🟢: ESC em modo TYPING é **consumido** (só sai da digitação, não cancela o operador); o 2º ESC cai no consumidor e cancela. Um PRESS de número no estado PLACING só inicia digitação se `event.value == 'PRESS'`.

O consumidor frameless sobrescreve `handle_typing_event` (`frameless/ops_placement.py:85-183`) acrescentando `LEFT_ARROW`/`RIGHT_ARROW` (offset esquerdo/direito), `W` (largura) e `H` (altura) 🟢.

## Parser de distância

```mermaid
flowchart TD
    P[value_str.strip] --> V{vazio?}
    V -- sim --> N[None]
    V -- não --> F{"contém ' ?"}
    F -- sim --> FI["_parse_feet_inches: split em ' → pés + polegadas"]
    F -- não --> IN{"termina com #quot; ou in?"}
    IN -- sim --> I1[units.inch]
    IN -- não --> MM{'mm'?} -- sim --> M1[units.millimeter]
    MM -- não --> CM{'cm'?} -- sim --> C1[units.centimeter]
    CM -- não --> ME{'m'?} -- sim --> M2[número já em metros]
    ME -- não --> FT{"' ou 'ft'?"} -- sim --> F1[units.feet]
    FT -- não --> PL[número puro → _number_to_scene_units]
    PL --> U{unit_settings.system}
    U -- IMPERIAL --> UI[polegadas]
    U -- METRIC --> UM{length_unit}
    UM -- MILLIMETERS --> UMM[mm]
    UM -- CENTIMETERS --> UCM[cm]
    UM -- outro --> UMT[metros]
    U -- NONE --> UMT
```

`_extract_number` aceita `"a b/c"` (misto, exige espaço), `"a/b"` e float puro; `ValueError`/`ZeroDivisionError` → `None` (`l.333-336`).

Achados 🟢:
- O ramo `endswith("'")` (`l.324`) é inalcançável: qualquer `'` já cai em `_parse_feet_inches` (`l.304`).
- `NUMBER_KEYS` (`l.55-64`) só produz `0-9 . - /`. Espaço, aspas e letras de unidade não são digitáveis pelo modal, logo, na prática, apenas números puros e frações simples (`3/4`) chegam ao parser; frações mistas e sufixos de unidade só funcionam se o consumidor montar a string por outro caminho (🟡).
- Número puro em sistema imperial é sempre polegada, mesmo que `length_unit` seja pés (`l.377-379`).
