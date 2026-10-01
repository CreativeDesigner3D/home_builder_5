# `door_profiles` — perfis .blend → seções de varredura (u, v)

`blendertomob/product_libraries/common/door_profiles.py` 🟢

Espaço de varredura comum: **u ≥ 0** através da face, medido a partir da borda do membro (para dentro);
**v ∈ [0, thickness]** através da espessura, a partir da face frontal 🟢 (`:12-17`, `:537-540`).

```mermaid
flowchart TD
    A(["load_profile(category, name, res=16)"]) --> A1{"arquivo existe?<br/>face_frame_assets/door_profiles/&lt;Dir&gt;/&lt;name&gt;.blend"}
    A1 -- Não --> E1["FileNotFoundError"]
    A1 -- Sim --> A2{"(path, mtime, res) em _cache?"}
    A2 -- Sim --> R0["retorna do cache"]
    A2 -- Não --> A3["bpy.data.libraries.load → append de TODOS os objetos"]
    A3 --> A4["para cada CURVE: Matrix.LocRotScale(loc, rot, scale);<br/>_sample_spline (Bézier cúbica, res amostras/segmento<br/>ou pontos POLY/NURBS brutos) → pontos transformados"]
    A4 --> A5["spline mais longa vence"]
    A5 --> A6["finally: remove objetos e curvas órfãs"]
    A6 --> A7{"algum ponto?"}
    A7 -- Não --> E2["ValueError"]
    A7 -- Sim --> A8["projeta no plano: descarta o eixo de menor extensão;<br/>remove duplicados consecutivos; fecha laço cíclico"]
    A8 --> A9["dict(points, cyclic, name, category) → _cache"]

    A9 --> CAT{"categoria / uso"}
    CAT -- "OUTER (borda externa)" --> O1["edge_profile_section(profile, T):<br/>eixo de maior extensão → v; detecta 'face run'<br/>para orientar; ajusta à espessura esticando SÓ<br/>o trecho reto atrás da forma do cortador"]
    CAT -- "INNER (sticking)" --> I1["sticking_strip(profile, T, panel_front):<br/>sticking_section → cyclic? _closed_cut_chain (cavaco Pulito)<br/>: edge_profile_section (DIP_* abertos);<br/>espelha u = w − u; apara trecho reto até o fundo;<br/>fundo em panel_front ou profundidade da curva;<br/>laço FECHADO anti-horário"]
    CAT -- "PANEL (raised)" --> P1["panel_profile_section(profile, max_depth):<br/>cíclico: remove run do plano da borda (x-extremo), divide no ponto de campo;<br/>aberto: remove run da face traseira (y-extremo);<br/>v atrás do plano do campo; escala se v_max > max_depth<br/>→ dict(points, field_u)"]
    CAT -- "APPLIED" --> AP1["applied_strip(profile, side, panel_front):<br/>OUT: u = −x, v = −y (proud na face)<br/>IN: u = x, v = panel_front − y (sobre o painel)<br/>laço anti-horário"]
    CAT -- "MITERED" --> M1["member_section(profile, T): normaliza à origem,<br/>ordena a partir da borda externa, fecha as 2 pontas<br/>até o fundo; largura do membro = max(u)"]
    N(["named_edge_section(name, T)"]) --> N1{"nome em _EDGE_SECTION_BUILDERS?"}
    N1 -- Não --> N0["None = borda reta (Square/Estate/Eclipse/New Cut...)"]
    N1 -- Sim --> N2["gera seção em código (raios 1/8, 1/4, 3/8&quot;;<br/>chanfro 3/16&quot;; bevel 3/4×1/4&quot;; bay = cove 3/8&quot;);<br/>escala tudo se v_max ≥ T; completa até (0, T)"]
```

## Explicação

- Diretórios por categoria 🟢 (`:31-37`): OUTER→"Outer Profiles", INNER→"Inner Profiles", PANEL→"Panel Profiles",
  APPLIED→"Applied Profiles", MITERED→"Mitered Profiles"; raiz `face_frame/face_frame_assets/door_profiles`
  (`:27-29`).
- **Cache invalidado por mtime**: editar o .blend do perfil vale no próximo build 🟢 (`:9-10`, `:101-103`).
- **Orientação detectada, não configurada**: a "face run" (trecho sobre um extremo de v) fixa o referencial 🟢
  (`:530-535`, `:564-596`). Porta mais fina que a região moldada → escala todo o eixo v (último recurso) 🟢
  (`:605-607`).
- `_closed_cut_chain` escolhe o canto cujos runs passam pela ORIGEM (desenhos ancoram face/aresta em (0,0)) e
  desempata pelo comprimento combinado 🟢 (`:208-226`).
- `profile_from_object` amostra uma curva da cena (ponteiro do estilo quando "unlock_profiles") usando
  `matrix_world` 🟢 (`:490-522`).
- **Mapeamento série → perfis NÃO está neste módulo**: `SERIES_PROFILES` / `profiles_for_series` ficam em
  `face_frame/style_options.py:5100-5157` 🟢 e apenas nomeiam arquivos desta biblioteca.
