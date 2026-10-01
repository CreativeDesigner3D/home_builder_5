# `engine.kick_sweep_segments` — rodapé (base molding) por spans de rodapé

Local: `blendertomob/molding/engine.py:711`; auxiliares `_kick_spans_local` (`:395`), `_assemble_kick_spans` (`:425`), `_island_perimeter_spans` (`:613`), `_stretch_segments` (`:531`), `offset_polygon_right` (`:195`).

```mermaid
flowchart TD
    A[kick_sweep_segments chain, facts, x_off, include_recessed] --> B[_assemble_front_raw → normaliza sentido<br/>inverte chain se direita aponta p/ trás]
    B --> C{todos os membros sem parent?}
    C -- sim --> D[_island_perimeter_spans]
    D --> D1{algum canto? ou > 2 rotações Z?<br/>ou 2 fileiras não opostas ±0.05 rad?}
    D1 -- sim --> E
    D1 -- não --> D2[fileira única: frente + lateral + costas + lateral<br/>fileira dupla costas-com-costas: frente A + lateral + frente B + lateral]
    D2 --> S1[_stretch_segments island=True]
    C -- não --> E[_assemble_kick_spans: spans mundiais em ordem de percurso<br/>+ terminais obj/lado/frente/trás]
    E --> E1{spans vazios?}
    E1 -- sim --> Z0[lista vazia]
    E1 -- não --> S2[_stretch_segments island=False]

    subgraph KL[_kick_spans_local por membro reto]
        K1{APPLIANCE ou kick.skip?} -- sim --> K2[1 span SKIP na frente]
        K1 -- não --> K3{setback ≤ 1e-5?}
        K3 -- sim --> K4[1 span FRONT na frente]
        K3 -- não --> K5[stile esquerdo até o chão → FRONT com retorno<br/>trecho recuado r = -depth + setback → RECESS<br/>stile direito → FRONT]
    end

    subgraph ST[_stretch_segments]
        T1[kept = FRONT, + RECESS se include_recessed] --> T2{ilha e todos kept?}
        T2 -- sim --> T3[laço fechado: offset_polygon_right → cyclic]
        T2 -- não --> T4[se ilha: rotaciona ordem p/ começar no 1º span descartado]
        T4 --> T5[agrupa spans kept consecutivos em stretches;<br/>na fronteira com span descartado, anexa o ponto adjacente<br/>= moldura RETORNA para o rodapé acabado]
        T5 --> T6[offset_polyline_right de cada stretch]
        T6 --> T7{não-ilha e stretch toca extremo da cadeia<br/>e lado do terminal finished?}
        T7 -- sim --> T8[retorno até o canto traseiro]
        T7 -- não --> T9[termina rente]
    end
    S1 --> R[lista de pontos, cyclic]
    S2 --> R
```

## Explicação

- 🟢 **Três tipos de span**: `FRONT` sempre recebe moldura; `RECESS` (rodapé recuado entre stiles) só com `include_recessed`; `SKIP` (eletrodomésticos, `RefrigeratorCabinet`, `kick.skip`) nunca — `engine.py:395-422`, `adapters.py:182-183`.
- 🟢 **Stiles até o chão** (face frame com rodapé `NOTCH`/`LOOSE`/`FLOATING`): cada stile vira um span FRONT em "L" que inclui o retorno lateral até o plano recuado — `engine.py:416-421`, `adapters.py:73`.
- 🟢 **Ilhas**: se nenhum membro da cadeia tem `parent` (não está preso a parede), tenta-se o perímetro; dupla fileira exige diferença de rotação Z ≈ π (tolerância 0,05) — `engine.py:622-631`, `engine.py:726-730`. 🟡 A heurística "sem parent = ilha" pode classificar corridas encostadas em parede mas não parentadas como ilha.
- 🟢 Cantos em L com setback têm a frente deslocada para dentro (`offset_polyline_right(local_pts, -setback)`) e viram `RECESS` — `engine.py:456-459`.
- 🟢 Eletrodomésticos de piso ("bridges") entram na cadeia para manter a corrida contínua mas geram span SKIP, forçando retornos dos dois lados — `adapters.py:55-66`, `ops.py:195-197`.
