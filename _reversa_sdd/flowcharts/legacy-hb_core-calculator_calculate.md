# `Calculator.calculate` — distribuição de medidas entre prompts

Local: 🟢 `blendertomob/hb_props.py:294-320`. Estrutura: `Calculator` (`hb_props.py:249-320`) com coleção de
`Calculator_Prompt` (`hb_props.py:227-246`); o total vem do driver em `distance_obj.home_builder.calculator_distance`
criado por `set_total_distance` (`hb_props.py:253-257`). Uso real: 🟢 `product_libraries/frameless/types_frameless.py:953-1026`
("Opening Calculator" que divide a altura do vão entre divisórias: total = `dim_z - mt*qtd`).

```mermaid
flowchart TD
    A[calculate] --> B{distance_obj definido?}
    B -- não --> Z[return]
    B -- sim --> C[distance_obj.hide_viewport = False<br/>view_layer.update - avalia o driver do total]
    C --> D[non_equal_total = 0; equal_qty = 0; calc_prompts = lista]
    D --> E{para cada prompt}
    E --> F{prompt.equal?}
    F -- sim --> G{include?}
    G -- sim --> G1[equal_qty += 1]
    G -- não --> G2[ ]
    G1 --> G3[calc_prompts.append prompt]
    G2 --> G3
    F -- não --> H{include?}
    H -- sim --> H1[non_equal_total += distance_value]
    H -- não --> E
    H1 --> E
    G3 --> E
    E -- fim --> I{equal_qty > 0?}
    I -- não --> Z
    I -- sim --> J[valor = calculator_distance - non_equal_total / equal_qty]
    J --> K{para cada prompt em calc_prompts}
    K --> L{include?}
    L -- sim --> L1[distance_value = valor]
    L -- não --> L2[distance_value = 0]
    L1 --> K
    L2 --> K
    K -- fim --> M[id_data.location = id_data.location<br/>'toque' para disparar drivers dependentes]
```

**Regra (HB_CORE-R15).** 🟢 Prompts marcados "igual" e incluídos recebem partes iguais do que sobra do total depois de
subtrair os prompts de valor fixo incluídos. Prompts "igual" excluídos ficam com 0. Prompts fixos não mudam. Sem prompts
"igual", nada é recalculado.

**Observações.**
- 🟢 Não há proteção contra resultado negativo (valores fixos maiores que o total).
- 🟢 `hide_viewport = False` é permanente; o objeto de cálculo é um empty de tamanho 0,001 (`types_frameless.py:951-952`).
- 🔴 Os operadores `pc_prompts.add_calculator_prompt`, `pc_prompts.edit_calculator` e `pc_prompts.run_calculator`,
  usados em `Calculator.draw` (`hb_props.py:264-280`), não estão definidos em `blendertomob/` (grep sem resultado de
  `bl_idname`). `remove_calculator_prompt` é um stub (`hb_props.py:291-292`).
