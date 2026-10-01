# `GeoNodeDimension.set_decimal` — precisão decimal da cota

Local: 🟢 `blendertomob/hb_types.py:732-798`; unidade em `get_unit_type` (`hb_types.py:692-712`).

```mermaid
flowchart TD
    A[set_decimal fine=False] --> B[dist = distância 3D entre points 0 e 1 da spline 0]
    B --> C[unit_type = get_unit_type]
    C --> D{unit_type}
    D -- 0 pol --> U0[v = m→in; inc = 1/16 se fine senão 1; prec 4/2]
    D -- 1 pés --> U1[v = m→in/12; inc = 1/16/12 ou 1/12; prec 4/2]
    D -- 2 mm --> U2[v = dist×1000; inc = 1 ou 10; prec 2/1]
    D -- 3 cm --> U3[v = dist×100; inc = 0,1 ou 1; prec 3/2]
    D -- 4 m --> U4[v = dist; inc = 0,001 ou 0,01; prec 4/3]
    D -- outro --> U0
    U0 --> E[v = round v/inc × inc - remove ruído de ponto flutuante]
    U1 --> E
    U2 --> E
    U3 --> E
    U4 --> E
    E --> F[r = round v, prec]
    F --> G{abs r - round r < 0,001?}
    G -- sim --> H[set_input Decimals = 0]
    G -- não --> I[texto = r formatado com prec, sem zeros à direita e sem ponto final]
    I --> J{tem ponto?}
    J -- não --> H
    J -- sim --> K[set_input Decimals = nº de dígitos após o ponto]
```

**Regras (HB_CORE-R11, R12).**
- 🟢 `get_unit_type`: sistema `METRIC` → `MILLIMETERS`=2, `CENTIMETERS`=3, `METERS`=4, outra unidade métrica=3;
  `IMPERIAL`/`NONE` → 0 (polegadas). O valor 1 (pés) nunca é devolvido, embora `set_decimal` o trate.
- 🟢 O valor é "encaixado" no incremento de snap da unidade (grosso ou fino) antes de contar decimais.

**Observações.**
- 🟢 No modo grosso em mm, o incremento é 10 mm (cota "arredonda" para centímetro), com precisão 1; na prática, cotas em
  mm não fino sempre ficam com 0 decimais.
- 🟡 `get_unit_type` ignora `scene.btm_settings.btm_unit`, que o sistema moderno de unidades consulta
  (`data/units.py:57-64`); as duas camadas podem divergir quanto à unidade exibida.
