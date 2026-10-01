# hb_placement — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-hb_placement`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#hb_placement`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-hb_placement*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Visão Geral

O `hb_placement` é a **infraestrutura compartilhada dos operadores modais de posicionamento**: gabinetes, closets,
portas/janelas, paredes, obstáculos, desenho 2D e cotas. Ele **não registra operadores**; entrega mixins
(`PlacementMixin`, `DimensionOperatorMixin`) e funções que resolvem snap sob o mouse, entrada numérica digitada, o vão
livre numa parede (com obstáculos, cantos, paredes em T, ilhas e recuos), o encosto gabinete-a-gabinete e o desenho GPU
das cotas de posicionamento. 🟢 Tem mais de 15 consumidores em `product_libraries/*` e `operators/*`. 🟢

## Responsabilidades

- Manter o estado modal de posicionamento (`IDLE → PLACING ↔ TYPING → IDLE`). 🟢
- Resolver o ponto 3D sob o mouse: raycast com anel de busca, snap a vértice/aresta (Ctrl) e a grade. 🟢
- Receber valores digitados e converter texto em metros (pés/polegadas, frações, mm/cm/m, unidade da cena). 🟢
- Calcular o vão livre numa parede, por lado, considerando filhos, portas/janelas, snap lines, paredes vizinhas em
  canto, paredes em T, gabinetes livres (ilhas/penínsulas) e sobreposição vertical. 🟢
- Escolher o X de encaixe (`snap_x`) dentro do vão a partir do cursor. 🟢
- Calcular recuos (hold-off) por borda do vão (ponta aberta, canto externo, abertura). 🟢
- Encostar um objeto novo na face esquerda/direita de um gabinete livre. 🟢
- Cancelar o posicionamento apagando os objetos de preview. 🟢
- Conduzir a cota de 3 cliques com modo ortogonal (`DimensionOperatorMixin`). 🟢
- Desenhar em `POST_PIXEL` as cotas de posicionamento, a seta de orientação e o indicador de snap. 🟢
- Fornecer primitivas 2D (retângulo, texto, linhas) e a área visível da região WINDOW. 🟢
- Duplicar uma hierarquia de objetos preservando drivers e parentesco. 🟢

## Regras de Negócio

IDs `HB_PLACEMENT-Rnn` de `code-analysis-legacy.md`.

**Estado e digitação**
- RN-01 (R01): após `init_placement` o estado é `PLACING`; após `cancel_placement`, `IDLE`. `ADJUSTING` existe mas nunca é atribuído. 🟢
- RN-02 (R02): tecla numérica em `PLACING` inicia a digitação; sem alvo, usa `get_default_typing_target()` (padrão `LENGTH`). 🟢
- RN-03 (R03): em `TYPING`, Esc ou Backspace com buffer vazio apenas saem da digitação; o evento é consumido e o operador continua. 🟢
- RN-04 (R04): Tab aplica o valor e passa ao próximo alvo só se `get_next_typing_target()` ≠ `NONE` (padrão `NONE` → Tab não faz nada). 🟢
- RN-05 (R05): precedência do parser — contém `'` → pés/polegadas; sufixo `"`/`in` → polegadas; `mm`; `cm`; `m`; `ft`; senão número puro. Frações `a/b` e mistas `a b/c` aceitas. 🟢
- RN-06 (R06): número puro — IMPERIAL → polegadas; METRIC → `length_unit` MILLIMETERS/CENTIMETERS, senão metros; NONE → metros. 🟢
- RN-07 (R35): no consumidor frameless, a posição só é recalculada fora de `TYPING` ou quando o alvo é `WIDTH`/`HEIGHT`; offsets digitados congelam a posição. 🟢

**Cancelamento**
- RN-08 (R07): cancelar remove todos os objetos registrados e seus descendentes (filhos antes do pai, tolerando `ReferenceError`), volta a `IDLE` e restaura o cursor `DEFAULT`. Não remove draw handler nem header (responsabilidade do consumidor). 🟢

**Vão em parede**
- RN-09 (R08): obstáculos são os filhos da parede, exceto `obj_x`, o objeto excluído e `IS_2D_ANNOTATION`; `IS_SNAP_LINE` é fronteira. 🟢
- RN-10 (R09): portas (`IS_ENTRY_DOOR_BP`) e janelas (`IS_WINDOW_BP`) bloqueiam os dois lados da parede. 🟢
- RN-11 (R10): um filho está na face frontal se `location.y < espessura/2`; só conta se estiver do mesmo lado da colocação. 🟢
- RN-12 (R11): filtro vertical opcional (exige `object_z_start` e `object_height`): obstáculo conta só se `z0 < oz1 ∧ oz0 < z1` (sobreposição estrita). Vale para filhos, ilhas, paredes vizinhas/T e aberturas no hold-off. 🟢
- RN-13 (R12): extensão em X pelo giro em Z (tolerância 0,1 rad): −90°/270° → `[x−DimY, x]`; ±180° → `[x−DimX, x]`; demais → `[x, x+DimX]`. 🟢
- RN-14 (R13): gabinetes livres (sem pai, com `FREE_CABINET_TAGS`) cuja pegada cruza a faixa de profundidade (frente `[−band, 0]`, trás `[t, t+band]`, `band = object_depth` ou 24") viram obstáculos, recortados a `[0, L]` e descartados se < 1/4". 🟢
- RN-15 (R14): parede vizinha em canto (inclusive pela emenda do cômodo fechado): a laje dela (se protrai para o lado da colocação) e os gabinetes `CABINET_MARKERS` dela viram obstáculos `[0, intr_esq]` e `[L−intr_dir, L]`. 🟢
- RN-16 (R15): parede em T — ponta de outra parede estritamente dentro do vão (margem 0,01 m) e a até 0,02 m da laje; não paralela (|y| ≥ 0,001); bloqueia só o lado para onde protrai; largura = projeção da espessura. 🟢
- RN-17 (R16): snap lines são obstáculos de largura zero em `SNAP_X_POSITION` (fallback `location.x`). 🟢
- RN-18 (R17): `snap_x` no vão — largura ≥ vão → início; cursor a menos de w/2 da borda esquerda → início; a menos de w/2 da direita → `fim − w`; senão centrado (`cursor − w/2`). 🟢
- RN-19 (R18): parede sem obstáculos → vão `[0, L]` e `snap_x = cursor_x` (sem centralizar nem prender às bordas; difere de RN-18). 🟢
- RN-20: `find_placement_gap` (sem lado, sem ilhas, sem intrusão de canto, T nos dois lados) é usado só por portas/janelas, coerente com aberturas atravessarem a parede. 🟢

**Recuos (hold-off)**
- RN-21 (R22): por borda — ponta da parede (±1/2") recebe recuo, exceto em canto interno; borda que coincide (±1/4") com início/fim de porta/janela com sobreposição vertical recebe recuo; demais bordas (gabinetes vizinhos) = 0. `holdoff ≤ 0` desliga. 🟢
- RN-22 (R23): os dois recuos são escalados proporcionalmente para sobrar ≥ 1" de vão útil. 🟢
- RN-23 (R24): canto interno ⇔ a direção da parede vizinha, saindo do vértice comum, tem produto escalar > 1e-4 com a normal do lado de colocação (−Y local frente, +Y trás). 🟢

**Snap gabinete→gabinete**
- RN-24 (R19): alvo = primeiro ancestral com marcador de `CABINET_MARKERS`; encontrar `IS_WALL_BP` antes interrompe (gabinetes de parede não são alvos). 🟢
- RN-25 (R20): lado = LEFT se o X local do hit < `DimX/2`, senão RIGHT. 🟢
- RN-26 (R21): LEFT desloca `−nova_largura` no X local do alvo; RIGHT desloca `+largura_do_alvo`; offset girado por `rotation_euler.z` do alvo; Z e rotação copiados do alvo. 🟢

**Snap de ponto**
- RN-27 (R25): raycast ignora objetos com `HB_CURRENT_DRAW_OBJ`; se o raio central falha, testa 6 raios num anel de 50 px e fica com o hit mais próximo da origem da vista. 🟢
- RN-28 (R26): com Ctrl e hit — snap ao vértice do polígono atingido a < 50 px em tela; senão ao ponto mais próximo de uma aresta (busca dicotômica, ε 1e-4). 🟢
- RN-29 (R27): sem hit — interseção com plano pela origem (normal Z, ou a direção da vista em vista lateral alinhada); com Ctrl, snap aos cantos da célula de grade `10^(round(log10(view_distance))−1)`. 🟢
- RN-30 (R28): `snap_value_to_grid` — IMPERIAL 1" (fino 1/16"); demais 10 mm (fino 1 mm); arredonda ao mais próximo. 🟢

**Cotas**
- RN-31 (R29): 3 cliques FIRST → SECOND → OFFSET; clique sem `current_point` é ignorado; ortho só vale no 2º ponto. 🟢
- RN-32 (R30): ortho cicla OFF → AUTO → H → V → OFF; AUTO é resolvido uma vez (|dx| ≥ |dy| → H) e fica fixo. 🟢

**Desenho e duplicação**
- RN-33 (R32): cota de posicionamento — linha + ticks de 6 px; rótulo em pílula escura (0.13,0.13,0.14,0.85) com borda; fonte `14 × ui_scale`; cor padrão branco 0.95; seta de orientação amarela (1,0.85,0.1) de 2,5 px. 🟢
- RN-34 (R33): indicador de snap — verde, raio 10 px + cruz quando `is_snapped`; amarelo raio 6 px senão; círculo azul claro (+15,+15) com ortho ativo. 🟢
- RN-35 (R34): área visível da WINDOW desconta TOOLS (esq.), UI (dir.) e headers/asset shelf (topo/base pelo centro vertical). 🟢
- RN-36 (R31): `duplicate_object_hierarchy` desoculta toda a hierarquia, marca com `_HB_DUP_TOKEN`, usa `bpy.ops.object.duplicate(linked=False)`, restaura flags e seleção; retorna `None` se o ativo continuar sendo a origem. 🟢

**Comportamentos desconhecidos**
- 🔴 Onde `HB_CURRENT_DRAW_OBJ`, `IS_SNAP_LINE`/`SNAP_X_POSITION` e `obj_x` são gravados (fora do módulo).
- 🔴 Semântica completa dos consumidores face_frame e closets (> 5000 linhas usando o mixin).
- 🟡 Vão com obstáculos sobrepostos/aninhados ou cursor dentro de um obstáculo não é tratado explicitamente.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Inicializar e cancelar o posicionamento com limpeza dos previews | Must | Após cancelar, nenhum objeto registrado (nem descendente) resta e o estado é `IDLE` |
| RF-02 | Resolver ponto sob o mouse por raycast com anel de 6 raios | Must | Mouse sobre a borda de um objeto fino ainda retorna hit |
| RF-03 | Snap a vértice/aresta com Ctrl | Should | Com Ctrl a 30 px de um vértice, `hit_location` = vértice |
| RF-04 | Snap a plano e grade quando não há hit | Must | Sem objeto sob o mouse, retorna ponto no plano Z=0; com Ctrl, canto da célula |
| RF-05 | Máquina de digitação PLACING ↔ TYPING com Enter/Esc/Backspace/Tab | Must | Transições de RN-02..RN-04 |
| RF-06 | Converter texto digitado em metros | Must | `600` em cena MM → 0,6; `2'6"` → 0,762; `1 1/2"` → 0,0381 |
| RF-07 | Calcular vão livre por lado com todos os tipos de obstáculo | Must | Gabinete na frente não bloqueia colocação atrás; porta bloqueia os dois lados |
| RF-08 | Escolher `snap_x` pelo cursor | Must | Regras RN-18/RN-19 |
| RF-09 | Considerar gabinetes da parede vizinha em canto | Must | Gabinete de 600 mm de profundidade na parede vizinha gera obstáculo `[0, 0,6]` |
| RF-10 | Considerar paredes em T | Should | Parede interna encostada no meio bloqueia só o lado para onde protrai |
| RF-11 | Considerar ilhas/penínsulas soltas diante da parede | Should | Ilha na faixa de 24" vira obstáculo recortado |
| RF-12 | Filtro vertical opcional | Should | Aéreo não é bloqueado por inferior abaixo dele |
| RF-13 | Recuos por borda com mínimo de 1" de vão útil | Should | Ponta livre com holdoff 1/2" recua; canto interno não recua |
| RF-14 | Encostar novo objeto na face de gabinete livre | Should | Hit na metade esquerda → novo à esquerda, mesma rotação e Z |
| RF-15 | Cota de 3 cliques com ortho | Must | Três cliques criam a cota; `O` cicla o modo; RMB/Esc cancela e remove handler |
| RF-16 | Desenhar cotas de posicionamento e seta de orientação | Should | Handler idempotente; removido ao sair |
| RF-17 | Desenhar indicador de snap das cotas | Should | Verde quando `is_snapped`, amarelo caso contrário |
| RF-18 | Primitivas 2D e área visível da região | Should | `get_visible_window_bounds` exclui N-panel com Region Overlap |
| RF-19 | Duplicar hierarquia preservando drivers | Should | Cópia com drivers apontando para a cópia; flags de ocultação restauradas |
| RF-20 | Arredondar valores à grade de unidades | Could | 12,3 mm → 10 mm (grosso) ou 12 mm (fino) |
| RF-21 | Estado `ADJUSTING`, alvo `OFFSET_Y`, `SNAP_RADIUS` do mixin de cota | Won't | Declarados e não usados |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | `view_layer.update()` a cada tick para evitar dados desatualizados no raycast | `hb_snap.py:50` | 🟢 |
| Performance | Paredes em T e ilhas varrem `scene.objects` inteiro a cada `MOUSEMOVE` | `hb_placement.py:828-915,1028-1070` | 🟢 |
| Performance | `INBETWEEN_MOUSEMOVE` ignorado pelo consumidor | `frameless/operators/ops_placement.py:1729-1863` | 🟢 |
| Robustez | Leitura de inputs GN sempre com `try/except` e fallback (largura 0, ignorar objeto) | `hb_placement.py` (várias) | 🟢 |
| Robustez | Draw handler de posicionamento idempotente | `hb_placement.py:132-156` | 🟢 |
| Usabilidade | Tamanho de fonte das cotas escala com `ui_scale` | `hb_placement.py:1712-1856` | 🟢 |
| Usabilidade | Navegação (MMB/roda/numpad) repassada à viewport durante a cota | `hb_placement.py:1476-1565` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Digitação durante o posicionamento

  Cenário: Digitar largura em cena métrica
    Dado um posicionamento em PLACING numa cena METRIC com length_unit MILLIMETERS
    Quando o usuário digita "6", "0", "0" e Enter
    Então apply_typed_value recebe 0,6 m e o estado volta a PLACING

  Cenário: Sair da digitação sem aplicar
    Dado o estado TYPING com buffer "45"
    Quando o usuário pressiona Esc
    Então o estado volta a PLACING, o valor não é aplicado e o operador continua

  Cenário: Texto inválido
    Dado o buffer "1/0"
    Quando o valor é aplicado
    Então parse_typed_distance captura o ZeroDivisionError e retorna None
    E o consumidor não deve mover o objeto (checar None antes de aplicar)

Funcionalidade: Vão livre na parede

  Cenário: Porta bloqueia os dois lados
    Dado uma parede de 4 m com uma porta de 0,8 m em x=1,5
    Quando busco o vão por lado na face traseira com o cursor em x=1,0
    Então o vão retornado termina em 1,5

  Cenário: Gabinete do outro lado não bloqueia
    Dado um gabinete na face frontal em x=[1,0; 1,6]
    Quando busco o vão na face traseira com o cursor em x=1,3
    Então o gabinete é ignorado

  Cenário: Aéreo sobre inferior
    Dado um inferior em z=[0; 0,87] ocupando x=[0; 0,6]
    Quando busco o vão para um aéreo com object_z_start=1,4 e object_height=0,7
    Então o inferior não é obstáculo

  Cenário: Parede sem modificador
    Dado um objeto IS_WALL_BP sem modificador GN
    Quando find_placement_gap_by_side é chamado
    Então retorna (None, None, None)

Funcionalidade: Recuos

  Cenário: Ponta livre recebe recuo
    Dado um vão que começa na ponta esquerda da parede (canto externo) e holdoff = 1/2"
    Quando compute_gap_holdoffs é chamado
    Então left_holdoff = 1/2"

  Cenário: Canto interno não recebe recuo
    Dado a parede vizinha formando canto interno do lado da colocação
    Quando compute_gap_holdoffs é chamado
    Então left_holdoff = 0

  Cenário: Vão estreito
    Dado um vão de 1,5" com dois recuos de 1/2"
    Quando compute_gap_holdoffs é chamado
    Então os recuos são reduzidos proporcionalmente até restar 1" de vão útil

Funcionalidade: Snap gabinete→gabinete

  Cenário: Encostar à direita
    Dado um gabinete livre de 0,6 m girado 90° e um hit em X local 0,45
    Quando detect_cabinet_snap_target e compute_cabinet_snap_transform são chamados
    Então o lado é RIGHT e o novo gabinete fica 0,6 m adiante no X local do alvo, com a mesma rotação

  Cenário: Gabinete preso à parede não é alvo
    Dado um hit num gabinete filho de uma parede
    Quando find_cabinet_bp sobe na hierarquia
    Então encontra IS_WALL_BP antes do marcador e retorna None

Funcionalidade: Cota de 3 cliques

  Cenário: Cota horizontal com ortho
    Dado ortho em AUTO e primeiro ponto em (0,0)
    Quando o segundo clique ocorre em (1,0; 0,1)
    Então o segundo ponto é (1,0; 0) e o terceiro clique define o afastamento

  Cenário: Cancelar a cota
    Dado dim_state = SECOND
    Quando o usuário pressiona RMB
    Então handle_dimension_event retorna 'CANCELLED' e o draw handler e o header são removidos
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Estado, cancelamento, snap de ponto, digitação e parser (RF-01..RF-06) | Must | Todo operador modal de posicionamento depende |
| Vão por lado, `snap_x`, cantos (RF-07..RF-09) | Must | Caminho crítico da colocação de gabinetes |
| Cota de 3 cliques (RF-15) | Must | Base de todas as cotas de layout/detalhe |
| T, ilhas, filtro vertical, recuos, encosto (RF-10..RF-14) | Should | Refinam o encaixe; há alternativa manual |
| Desenho GPU, primitivas, duplicação (RF-16..RF-19) | Should | Feedback visual e cópia |
| Arredondar à grade (RF-20) | Could | Uso pontual |
| `ADJUSTING`, `OFFSET_Y`, `SNAP_RADIUS` (RF-21) | Won't | Código morto |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `hb_placement.py` | `PlacementState`, `TypingTarget`, `PlacementDimSpec`, `NUMBER_KEYS`, `CABINET_MARKERS`, `FREE_CABINET_TAGS` | 🟢 |
| `hb_placement.py` | `PlacementMixin` (ciclo de vida, digitação, parser, vão, intrusões, recuos, encosto) | 🟢 |
| `hb_placement.py` | `DimensionOperatorMixin`, `draw_dimension_snap_indicator`, `draw_placement_dimensions` | 🟢 |
| `hb_placement.py` | `duplicate_object_hierarchy`, `draw_header_text`, `clear_header_text` | 🟢 |
| `hb_snap.py` | `get_region`, `ray_cast`, `best_hit`, `search_edge_pos`, `snap_to_geometry`, `snap_to_object`, `snap_to_grid`, `main`, `snap_value_to_grid`, `snap_vector_to_grid` | 🟢 |
| `hb_gpu_draw.py` | `get_visible_window_bounds`, `draw_rect`, `draw_rect_outline`, `draw_text`, `vcenter_baseline`, `point_in_rect`, `draw_lines` | 🟢 |
| `product_libraries/frameless/operators/ops_placement.py:1729-1863` | consumidor de referência (tick modal) | 🟢 |
