# `ops._resolve_stack` + `_sweep_z` — pilhas de moldura e cotas verticais

Local: `blendertomob/molding/ops.py:46` (`_resolve_stack`), `:75` (`_crown_datum`), `:88` (`_crown_stack_top`), `:106` (`_sweep_z`), `:226` (`_base_stack`); métricas de perfil em `blendertomob/molding/packages.py:278`.

```mermaid
flowchart TD
    A[_resolve_stack stack, opts] --> B[front = 0]
    B --> C[para cada ref, fallback, dx, dy]
    C --> D{dy == 'STACK_OFFSET'?}
    D -- sim --> D1[dy = opts.stack_offset]
    D -- não --> E
    D1 --> E[categoria = 1º segmento de ref]
    E --> F{override da categoria?}
    F -- sim --> F1[ref = categoria/override]
    F -- não --> G
    F1 --> G{dx == 'STACK_FRONT'?}
    G -- sim --> G1[dx = front]
    G -- não --> H
    G1 --> H[append ref, fallback, dx, dy]
    H --> I[front = max front, dx + profile_front_depth ref]
    I --> C
    C -->|fim| Z[lista concreta]

    subgraph Z_[_sweep_z molding_type, first, dy]
        Z1{tipo} -- CROWN --> Z2[_crown_datum + dy]
        Z1 -- CAP --> Z3[z = altura; se topo da pilha crown > z → z = topo;<br/>z + cap_offset + dy]
        Z1 -- BASE / LIGHT_RAIL --> Z4[dy — origem do cage<br/>piso p/ base, fundo p/ upper]
    end
    subgraph CD[_crown_datum]
        C1{facts.crown_mount?<br/>face frame com TOP_RAIL} -- sim --> C2[altura - largura_top_rail + overlay_porta + reveal]
        C1 -- não --> C3[altura do cage — frameless]
    end
```

## Explicação

- 🟢 **Sentinelas**: `STACK_OFFSET` (dy) vira a altura ajustável `molding_crown_stack_offset` (padrão 3,5"); `STACK_FRONT` (dx) vira a "frente acumulada" das entradas anteriores, i.e. `max(dx + espessura medida)` — permite crown montada sobre spacer e base shoe na face do rodapé — `ops.py:58-72`.
- 🟢 **Métricas de perfil** `(top, depth)`: `top = max(Y)`, `depth = max(X) - min(X)` do contorno; carregadas de um `.blend` de pack (append temporário e remoção) ou do contorno embutido, com cache por `profile_ref` — `packages.py:262-311`. 🟡 A chave do cache é só `profile_ref`, ignorando `fallback_key`.
- 🟢 **Datum da crown** (face frame): `altura - TOP_RAIL.Width + max(default_top_overlay,0) + molding_crown_reveal` (reveal padrão 0,625") — `ops.py:80-85`, `adapters.py:199-207`, `hb_props.py:520-525`.
- 🟢 **Furniture cap**: nunca abaixo do topo do cage; sobe até o topo da pilha crown ativa (datum + dy + altura do perfil mais alto), depois soma `molding_cap_offset` — `ops.py:88-122`.
- 🟢 **Base**: override `molding_base_profile` aplica-se a refs da categoria `Base Molding`; base shoe é anexada com `STACK_FRONT` mesmo sem pacote (frente acumulada 0 → rente à face do rodapé) — `ops.py:226-243`, `ops.py:284-287`.
