# `engine.chain_sweep_points` — caminho de crown / light rail / cap

Local: `blendertomob/molding/engine.py:348` (auxiliares `_assemble_front_raw` em `:260`, `offset_polyline_right` em `:159`, `corner_plan_data` em `:231`).

```mermaid
flowchart TD
    A[chain_sweep_points chain, facts, face_offset, end_offset] --> B[_assemble_front_raw]
    subgraph RAW[_assemble_front_raw]
        B1[para cada membro i] --> B2{facts.corner?}
        B2 -- sim --> B3[corner_plan_data: frente em L<br/>ld,-depth → ld,-rd → width,-rd<br/>ou diagonal só 2 pontos]
        B3 --> B4[inverte se ponto anterior/centro seguinte<br/>estiver mais perto da outra ponta]
        B2 -- não --> B5[cantos frontais fl, fr em mundo;<br/>left_first pela distância ao anterior/seguinte]
        B5 --> B6[1º membro reto registra first_straight<br/>= índice + normal frontal]
        B4 --> B7[terminais: 1º e último membro<br/>obj, lado, canto traseiro]
        B6 --> B7
    end
    B --> C{first_straight e ≥ 2 pontos?}
    C -- sim --> D[travel = raw idx+1 - raw idx<br/>right = travel.y, -travel.x]
    D --> E{right · normal_frontal < 0?}
    E -- sim --> F[inverte chain e remonta raw]
    E -- não --> G
    C -- não --> G{len raw < 2?}
    F --> G
    G -- sim --> N[None]
    G -- não --> H[off = offset_polyline_right raw, face_offset<br/>juntas em meia-esquadria]
    H --> I[para cada terminal 0 e 1]
    I --> J{lado do terminal é finished?}
    J -- não --> I
    J -- sim --> K[estende ponta por outward×end_offset<br/>e acrescenta canto traseiro + outward×end_offset<br/>= retorno até a parede]
    K --> I
    I -->|fim| Z[retorna off, chain]
```

## Explicação

1. 🟢 Monta uma polilinha "crua" pelas frentes dos membros em ordem de cadeia. Membros de canto (L) contribuem com a frente do nicho (3 pontos) ou a diagonal (2 pontos) — `engine.py:241-253`. Sem `ld`/`rd`, assume 24" (`engine.py:241-242`).
2. 🟢 **Normalização de sentido**: o engine sempre desloca "à direita do percurso"; se a direita do primeiro trecho reto apontar para trás (produto escalar negativo com a normal frontal `-Y` local), a cadeia é invertida — `engine.py:355-364`.
3. 🟢 `offset_polyline_right` calcula a interseção das linhas deslocadas de trechos consecutivos (`t = ((p2-p1)×d2)/(d1×d2)`); trechos paralelos (|cross| < 1e-6) recebem dois pontos (degrau) — `engine.py:176-185`.
4. 🟢 **Retornos em laterais acabadas**: apenas se `facts['finished_left'|'finished_right']` do membro terminal for True, a moldura contorna a extremidade até o canto traseiro da caixa; caso contrário termina rente — `engine.py:371-387`.
5. 🟡 `end_offset` é sempre chamado com o mesmo valor de `face_offset` (dx da pilha) em `ops.py:212`, então o retorno fica alinhado ao deslocamento frontal da peça.
