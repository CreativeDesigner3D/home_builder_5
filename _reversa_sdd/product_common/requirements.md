# product_common — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-29, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-product_common`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#product_common`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-product_common-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/`.

## Visão Geral

O `product_common` é a **biblioteca compartilhada** das linhas de produto legadas (face frame e frameless). Reúne um
motor de portas em Python puro que substitui o modificador GN `CPM_5PIECEDOOR`, uma biblioteca de perfis de borda e
seção carregados de `.blend`, os tipos de eletrodoméstico (cages GN wireframe), as coifas de madeira em 14 estilos e
dois registries plugáveis para catálogos externos de acessórios e de painéis de eletrodoméstico. 🟢
Todas as medidas nascem em polegadas (padrão americano/CWP) e são convertidas para metros internos. 🟢

## Responsabilidades

- Calcular o layout paramétrico de uma porta (montantes, travessas, mid rails/stiles, painéis) como pares lineares `(coef, offset)`. 🟢
- Realizar a malha estática da porta: perfis de borda, sticking, moldura aplicada, painel raised/ranhurado, arcos, mullions, construção mitered, fallback para caixa simples/slab. 🟢
- Carregar perfis de `.blend`, amostrar Bézier, projetar no plano da seção, cachear por mtime e converter em seções (u, v) por categoria. 🟢
- Gerar em código os perfis de borda de catálogo (roundover, chamfer, beveled, bay). 🟢
- Criar eletrodomésticos como cages GN wireframe com texto de anotação e dimensões padrão. 🟢
- Construir coifas de madeira filhas do cage `HOOD` em 14 estilos, com estilo CUSTOM configurável por coifa. 🟢
- Guardar e restaurar a receita paramétrica de peças de coifa editadas manualmente. 🟢
- Expor registries de providers externos de acessórios (por host) e de specs de painel de eletrodoméstico (provider único). 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `PRODUCT_COMMON-Rnn`).

**Layout da porta (`door_builder`)**
- RN-01 (R01): larguras uniformes de montante/travessa/mid rail têm piso de 1/2"; overrides por lado caem na uniforme quando `None` e têm piso 0 (um lado 0 elimina o membro, para portas espelhadas se encostarem). 🟢
- RN-02 (R02): espessura do painel com piso de 1/8"; `panel_inset` com piso 0. 🟢
- RN-03 (R03): tamanho mínimo da porta de 5 peças `min_w = lsw + rsw + m·msw + 1/2"`, `min_h = trw + brw + k·mrw + 1/2"`; SLAB → (0, 0). Abaixo ou no mínimo, a coifa troca por SLAB. 🟢
- RN-04 (R04): frentes de armário do face frame usam mínimo próprio mais rígido (`2 montantes + 1"`, `2 travessas + 1"`), divergente de RN-03. 🟢 / 🟡 sem justificativa
- RN-05 (R05): precedência do mid rail — `mid_rail_count > 0` > `mid_rail_z` explícito > `add_mid_rail` (centralizado `(0.5, −mrw/2)` ou fixo `max(mid_rail_location, brw)` a partir da base). 🟢
- RN-06 (R06): k mid rails equidistantes; campo `fh = H − (trw + brw + k·mrw)`; linha i começa em `fh·i/(k+1) + brw + i·mrw`, altura `fh/(k+1)`. 🟢
- RN-07 (R07): m mid stiles equidistantes; coluna `(W − (lsw + rsw + m·msw))/(m+1)`; mid stiles segmentados por linha de painel. 🟢
- RN-08 (R08): painéis recuados da face por `y_inset` com espessura própria; membros de quadro usam a espessura da porta. 🟢
- RN-09 (R21): slots de material — 0 = stile (slab, montantes, mid stiles, barras de mullion), 1 = rail (travessas, mid rails, strips em travessas), 2 = panel; `materials` é a tripla (stile, rail, panel). 🟢

**Malha da porta**
- RN-10 (R09): porta MITERED usa um único perfil de membro; `max u` vira a largura nos 4 lados; sem mid rail, arcos, sticking e applied; mullions valem. Só quando `member_section` existe e `door_type != 'SLAB'`. 🟢
- RN-11: cadeia de fallback por peça — raised → grooved (+ tampas arqueadas) → shaped flat → shaped top rail → shaped bottom rail → edge-profiled box → caixa simples. 🟢
- RN-12 (R10): painel raised cai para caixa plana quando `min(w, h) ≤ 2·field_u` ou `thickness − y_inset ≤ 0`. 🟢
- RN-13 (R11): ranhuras só em painel plano; KERF 1/8" × 3/32"; BEAD quirk 1/16" + conta de raio 0,09" + profundidade 0,11"; padrão centrado; ranhuras a menos de `max(2·meia-largura, 4 mm)` da borda descartadas; profundidade ≥ espessura → sem ranhura. 🟢
- RN-14 (R12/R13): rise ARCH `min(0,20·w, 2,25")`, CROWN `min(0,16·w, 1,75")`, limitado por `shape['rise']`; arco na linha de topo (e na base nas formas Double); Twin força 1 mid stile; célula ≤ 2" desliga o arco. 🟢
- RN-15 (R14): perfil de borda externa só nos lados da peça no contorno da porta; lados internos com u=0; se `u_max` não cabe, borda reta. 🟢
- RN-16 (R15): travessa arqueada descarta o perfil externo se não couber no material acima/abaixo do pico. 🟢
- RN-17 (R16): sticking pulado em células com `w ≤ 2·strip_stile` ou `h ≤ 2·strip_rail`; strips com contagens diferentes são reamostrados e as esquadrias fechadas com faixas de transição. Fallback cruzado: `rail = rail or inner or stile`, `stile = stile or inner or rail`. 🟢
- RN-18 (R17): moldura aplicada com `scope='RAILS'` corre só no topo/base da abertura, com tampas planas, ignorando bordas arqueadas. 🟢
- RN-19 (R18): mullion GRID — 2 vidros na largura; linhas por altura (≤24" → 2, ≤36" → 3, ≤48" → 4, senão 5); vertical só se `w > bw + 2"`; horizontais a < 1" das bordas puladas. 🟢
- RN-20 (R19): MISSION — 3 vidros no terço superior, inválido se `zb0 ≤ 1"` ou `w ≤ 3·bw + 3"`; PRAIRIE — barras a 2" das bordas, inválido se `w` ou `h ≤ 2·(2" + bw) + 1"`; X — diagonal descendente em meia-madeira. 🟢
- RN-21 (R20): mullions curvos (GOTHIC, DBL_GOTHIC, DBL_BOW, INTERLOKEN) por centerlines normalizadas esticadas ao aspecto; barra padrão 7/8"; profundidade = plano do vidro; escalonamento 0,2 mm por segmento contra z-fighting. 🟢

**Perfis (`door_profiles`)**
- RN-22 (R22): perfil = arquivo `.blend` com uma curva; vence a spline com mais pontos; cache invalidado pelo mtime. 🟢
- RN-23 (R23): ajuste à espessura estica só o trecho reto atrás do ponto moldado mais profundo; porta mais fina que a região moldada → escala todo v. 🟢
- RN-24 (R24): profundidade do raise limitada a `espessura − recuo do painel`. 🟢
- RN-25 (R25): sticking em painel recuado assenta no plano do painel; em painel raised corre até a profundidade natural da curva. 🟢
- RN-26 (R26): perfis de borda de catálogo em código — 1/8", 1/4", 3/8" radius; chamfer e 3/16" chamfer (45°); beveled (3/4" × 1/4"); bay (cove 3/8"). Nome desconhecido → borda reta (`None`); lookup case-insensitive com `strip()`. 🟢
- RN-27 (R27): moldura aplicada OUT fica saliente sobre a face; IN assenta sobre o painel dentro da abertura. 🟢
- RN-28: seção ilegível → `None`; o consumidor cai para borda reta/painel plano. Arquivo ausente → `FileNotFoundError`; curva inválida → `ValueError`. 🟢

**Eletrodomésticos (`types_appliances`)**
- RN-29 (R28): dimensões padrão L × A × P (pol.) — Appliance 30×36×24; Range 30×36×25; Cooktop 30×4×21; WallOven 30×29×24; Dishwasher 24×34×24; Refrigerator 36×70×30; Microwave 24×12×14; Hood 30×6×20; Sink 33×10×22; WashingMachine 27×38×30; Dryer 27×38×30. 🟢
- RN-30: todo eletrodoméstico é cage `WIRE` com `IS_APPLIANCE`, `APPLIANCE_TYPE`, `MENU_ID='HOME_BUILDER_MT_appliance_commands'`, `Mirror Y=True` e um `GeoNodeText` filho dirigido por drivers (`x = dim_x/2`, `y = −dim_y`, `z = dim_z/2`, rotação 90° em X). 🟢
- RN-31 (R29): só Range e Hood têm `variable_width=True`. 🟢
- RN-32 (R30): forno duplo 51" de altura (simples 29"); geladeira counter-depth 24" de profundidade (padrão 30"); micro-ondas over-range 30×17×16. 🟢
- RN-33 (R31): Cooktop e Sink recebem `IS_COUNTERTOP_APPLIANCE=True`. 🟢
- RN-34 (R32): propriedades `'TEXT'` ("Hood Style", "Sink Type") nunca são criadas, pois `add_property` não trata esse tipo. 🟢 bug

**Coifas de madeira (`wood_hoods`)**
- RN-35 (R33): chapa fixa de 3/4"; laterais em altura total recuadas 3/4" da face, tampo entre as laterais, frente aplicada em largura total. 🟢
- RN-36 (R34): presets — SHELF banda 5" proj. 2"; NICHE 6"/1,5"; MANTLE/PLANTATION 6"/2" + 2 painéis; GRAND_MANTLE banda 8" + crown 5" + 2 painéis; TRADITIONAL inclinada topo 12"; VILLA topo 12" + crown 5" + banda 6"; CHIMNEY topo 6" + banda 6"; SHIPLAP_MANTLE 6"/2"; BOX/PENINSULA/SHIPLAP_BOX/SHIPLAP_PENINSULA caixa simples. Estilo desconhecido → BOX. 🟢
- RN-37 (R35): painéis frontais aplicados — montante/travessa 2,5", separação 3", saliência 1/2"; 2 portas → `(W − 2·2,5" − 3")/2`. 🟢
- RN-38 (R36): estilos inclinados, shiplap e molduras de mantle são malhas estáticas; estilos retos são cutparts com drivers. 🟢
- RN-39 (R37): limites do CUSTOM — `top_depth` [1", D]; `top_width` [2·3/4" + 2", W]; `H ≥ 1"`; `top_height` [0, H − banda − 1"]; mantle só se `mantle_depth > 1/8"`; `panel_count` 1..10; mid rails/stiles 0..6; shiplap 4/5/6". 🟢
- RN-40 (R38): frente de baia — PANEL (inset 1/4"), OVERLAY_DOOR (sobreposição do estilo; sem estilo ou estilo inset → 1/2"), INSET_DOOR (folga 1/8"); valor inválido → PANEL. 🟢
- RN-41 (R39): quadro frontal/paneled end com piso de 1/2" nos membros; aberturas `(W − (n+1)·sw)/n`; se não couber, mantém lateral/frente simples. 🟢
- RN-42 (R40): recorte do exaustor na prateleira liner — largura ≤ `W − 2·3/4" − 2"`, profundidade ≤ `interior − 2"`, deslocamento ±`(interior − cd)/2`, recorte zero → prateleira sólida, altura [0, H − 2"]. 🟢
- RN-43 (R41): shiplap — tábua 6" (mín. 1"), revelação 1/8", saliência 1/2", cantos a 45°; último curso aparado se sobra > 1/4". 🟢
- RN-44 (R42): friso do mantle limitado a [1/4", banda]; saliência mínima 1/8". 🟢
- RN-45 (R43): reconstrução preserva peças `IS_MANUAL_PART`. 🟢
- RN-46 (R44): snapshot só para peças com modificador GN; reverter exige `IS_WOOD_HOOD_PART` + `IS_MANUAL_PART` + snapshot; sucesso remove os dois flags. 🟢
- RN-47 (R45): primeira abertura dos prompts semeia `top_width = width/2`; as 10 escolhas de baia são sempre persistidas. 🟢
- RN-48 (R46): opção antiga `panel_rail_width` migra para `panel_top_rail_width` e `panel_bottom_rail_width`. 🟢
- RN-49: imports de `face_frame` são tardios e protegidos por `try/except`; sem face frame, a coifa é construída sem estilo/acabamento. 🟢

**Registries**
- RN-50 (R47): accessory provider = função sem argumentos que devolve dicts com ao menos `code` e `name` (opcionais `category`, `min_opening_w`, `section`, `group`); `all_items` injeta `host`; `find` devolve o primeiro código; falha do provider → lista vazia + `print`. 🟢
- RN-51 (R48): hosts esperados — `opening_interior_pullout`, `opening_interior_accessory`, `tall_pantry`, `behind_door_rollout`, `pullout_board`, `tilt_out`, `closet_rod`, `door_mounted`, `drawer_accessory`, `blind_corner_hardware`. 🟢
- RN-52 (R49): appliance spec provider único (registro sobrescreve) com `manufacturers()`, `models(mfr)`, `resolve(mfr, model)`; sem provider, só entrada manual. 🟢

**Comportamentos desconhecidos**
- 🔴 Nenhum provider de acessórios ou de specs existe no repositório; o formato real dos dados é desconhecido além das chaves lidas.
- 🔴 `Trash Pull Outs/Generic Trash Pullout.blend` não é referenciado em código.
- 🔴 Versão do Python embarcado no Blender 5.2 (afeta as anotações dinâmicas `bay_front_%d`).
- 🟡 `PENINSULA`/`SHIPLAP_PENINSULA` e `PLANTATION` não têm builders dedicados (iguais a BOX / MANTLE).

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Normalizar o estilo de porta em `dict` (`door_style_info`) a partir do objeto de estilo ou do fallback | Must | Com `style=None`, devolve cópia de `DOOR_STYLE_FALLBACK` (5_PIECE, membros 3") |
| RF-02 | Calcular larguras de quadro com pisos e overrides por lado | Must | `stile_width = 0,2"` → 1/2"; override por lado `0.0` → membro eliminado |
| RF-03 | Calcular o tamanho mínimo da porta | Must | Membros 3", sem mid → `min_w = min_h = 6,5"`; SLAB → (0, 0) |
| RF-04 | Gerar layout `(coef, offset)` de todas as peças | Must | Soma de larguras de colunas + membros = W para qualquer W ≥ mínimo |
| RF-05 | Avaliar o layout em coordenadas absolutas (`evaluate_layout`) | Must | Cada peça tem `x0 < x1`, `z0 < z1` dentro de [0, W] × [0, H] |
| RF-06 | Posicionar k mid rails e m mid stiles equidistantes com precedência correta | Must | `mid_rail_count=2` ignora `add_mid_rail`; linhas de painel com a mesma altura |
| RF-07 | Construir a malha da porta com a cadeia de fallback por peça | Must | Seção ausente/inválida nunca gera exceção; resultado mínimo é caixa simples |
| RF-08 | Atribuir `material_index` pelos slots stile/rail/panel | Must | Faces de painel com índice 2; de travessa, 1; de montante, 0 |
| RF-09 | Construir porta MITERED por varredura única com meia-esquadria | Should | 4 lados com a mesma largura (`max u`); sem mid rail |
| RF-10 | Painel raised com limite de profundidade | Should | Profundidade nunca ultrapassa `espessura − recuo` |
| RF-11 | Ranhuras BEAD/KERF em painel plano | Could | Nenhuma ranhura a menos de `max(2·meia-largura, 4 mm)` da borda |
| RF-12 | Arcos ARCH/CROWN (simples, Double, Twin) | Should | Célula de 12" em ARCH → rise 2,25"; célula ≤ 2" → sem arco |
| RF-13 | Sticking e moldura aplicada (ALL/RAILS, OUT/IN) | Should | Célula pequena pula o strip sem erro |
| RF-14 | Mullions retos (GRID, MISSION, PRAIRIE, X) e curvos | Could | Porta 30" alta GRID → 3 linhas; MISSION inválido → sem barras |
| RF-15 | Carregar perfil `.blend` com cache por mtime e limpeza de datablocks | Must | Segunda carga sem mudança de mtime não chama `libraries.load` |
| RF-16 | Converter perfil em seções OUTER/INNER/PANEL/APPLIED/MITERED | Must | Seção devolvida é lista de (u, v) ou `None` quando ilegível |
| RF-17 | Ajustar perfil à espessura da porta preservando o cortador | Should | Porta de 1" com perfil de 3/4" estica só o trecho reto |
| RF-18 | Gerar perfis de borda de catálogo por nome | Should | `" 1/4\" Radius "` resolve; `"Estate"` → `None` |
| RF-19 | Criar eletrodoméstico (10 tipos) com cage, marcadores e texto | Must | `Refrigerator().create(...)` → 36×70×30", `APPLIANCE_TYPE='REFRIGERATOR'` |
| RF-20 | Variantes: forno duplo, geladeira counter-depth, micro-ondas over-range | Should | `set_double_oven(True)` → altura 51" |
| RF-21 | Construir coifa de madeira em qualquer um dos 14 estilos | Must | Peças filhas com `IS_WOOD_HOOD_PART`; `WOOD_HOOD_STYLE` gravado |
| RF-22 | Reconstruir coifa preservando peças manuais | Must | Peça `IS_MANUAL_PART` sobrevive à troca de estilo |
| RF-23 | Estilo CUSTOM com opções persistidas por coifa e limites | Should | Valores fora dos limites são grampeados antes da construção |
| RF-24 | Operador `blendertomob.build_wood_hood` | Must | Só habilitado com `APPLIANCE_TYPE=='HOOD'`; registra undo |
| RF-25 | Operador `blendertomob.wood_hood_prompts` (5 abas, reconstrução em `check()`) | Should | Alterar uma opção reconstrói a coifa no diálogo |
| RF-26 | Snapshot e operador `blendertomob.revert_hood_part` | Could | Peça revertida volta a seguir o cage; flags removidos |
| RF-27 | Migrar caminhos de driver no restore (pré-5.2 ↔ 5.2) | Should | Snapshot salvo em 5.1 restaura com drivers válidos em 5.2 |
| RF-28 | Registry de acessórios por host, tolerante a falha do provider | Should | Provider que levanta exceção → `get_items` devolve `[]` |
| RF-29 | Registry de provider único de specs de eletrodoméstico | Could | Segundo `register_provider` substitui o primeiro |
| RF-30 | Criar propriedades `'TEXT'` de coifa e pia | Won't | Bug legado: não reproduzir; tratar na reimplementação |
| RF-31 | Asset `Generic Trash Pullout.blend` | Won't | Sem consumidor em código |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Cache de perfis por `(path, mtime, res)` evita recarregar `.blend` | `product_libraries/common/door_profiles.py:39`, `:85-150` | 🟢 |
| Robustez | Emissores devolvem `False` e caem para geometria mais simples em vez de falhar | `product_libraries/common/door_builder.py:1300-1362` | 🟢 |
| Robustez | Datablocks do `.blend` de perfil removidos em `finally` | `product_libraries/common/door_profiles.py:105-126` | 🟢 |
| Robustez | Falha de provider externo não interrompe a UI | `accessory_registry.py:28-54` | 🟢 |
| Desacoplamento | Coifa funciona sem `face_frame` (imports tardios protegidos) | `product_libraries/common/wood_hoods.py:430-475`, `:1594-1601` | 🟢 |
| Desacoplamento | `door_style_info` isola o cálculo de referências RNA | `product_libraries/common/door_builder.py:87` | 🟢 |
| Compatibilidade | Caminhos de driver de input GN migrados entre < 5.2 e 5.2 no restore | `product_libraries/common/wood_hoods.py:46-54` | 🟢 |
| Compatibilidade | Anotações dinâmicas no corpo da classe dependem da semântica ansiosa de anotações | `product_libraries/common/wood_hoods.py:1920-1924` | 🟡 |
| Qualidade visual | Escalonamento de 0,2 mm evita z-fighting entre barras de mullion | `product_libraries/common/door_builder.py:842-1051` | 🟢 |
| Undo | Operadores de coifa têm `UNDO` | `product_libraries/common/wood_hoods.py:1773`, `:1804`, `:2193` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Layout paramétrico de porta

  Cenário: Porta de 5 peças padrão
    Dado o estilo fallback (montantes e travessas de 3", sem mid rail)
    Quando evaluate_layout é chamado com W = 18" e H = 30"
    Então há 4 membros e 1 painel
    E o painel ocupa x ∈ [3", 15"] e z ∈ [3", 27"]

  Cenário: Porta abaixo do mínimo
    Dado o estilo fallback
    Quando o tamanho pedido é 6" × 6" (mínimo 6,5" × 6,5")
    Então o chamador constrói a porta como SLAB

  Cenário: Dois mid rails equidistantes
    Dado mid_rail_count = 2 e add_mid_rail = True
    Quando door_layout é calculado
    Então existem 2 mid rails e 3 linhas de painel de mesma altura
    E add_mid_rail é ignorado

  Cenário: Override por lado zerado
    Dado left_stile_width = 0.0
    Quando door_layout é calculado
    Então a porta não tem montante esquerdo

Funcionalidade: Malha da porta

  Cenário: Seção inválida cai para caixa simples
    Dado outer_section = None e panel_section ilegível
    Quando build_door_mesh é executado
    Então a malha é criada com caixas simples sem levantar exceção
    E as faces têm material_index 0, 1 ou 2 conforme a peça

  Cenário: Painel raised sem profundidade
    Dado thickness − y_inset ≤ 0
    Quando o painel é emitido
    Então o painel é uma caixa plana

  Cenário: Porta MITERED
    Dado member_section definido e door_type = '5_PIECE'
    Quando build_door_mesh é executado
    Então os 4 lados têm largura max(u) e não há mid rail nem arco

Funcionalidade: Perfis

  Cenário: Cache por mtime
    Dado um perfil já carregado
    Quando load_profile é chamado de novo sem mudança no arquivo
    Então bpy.data.libraries.load não é chamado

  Cenário: Arquivo ausente
    Dado um nome de perfil sem arquivo em PROFILE_DIRS
    Quando load_profile é chamado
    Então FileNotFoundError é levantado

  Cenário: Borda de catálogo desconhecida
    Quando named_edge_section("Estate") é chamado
    Então retorna None (borda reta)

Funcionalidade: Eletrodomésticos

  Cenário: Criar fogão
    Quando Range().create("Fogão") é chamado
    Então o cage tem 30" × 36" × 25", IS_APPLIANCE e APPLIANCE_TYPE = 'RANGE'
    E um texto filho fica centralizado na frente do cage

  Cenário: Propriedade TEXT não criada
    Quando Hood().create("Coifa") é chamado
    Então a propriedade "Hood Style" não existe no objeto (bug legado)

Funcionalidade: Coifas de madeira

  Cenário: Construir estilo MANTLE
    Dado um cage HOOD sem peças
    Quando blendertomob.build_wood_hood é executado com style = 'MANTLE'
    Então existem peças IS_WOOD_HOOD_PART com banda de 6" e 2 painéis frontais
    E WOOD_HOOD_STYLE = 'MANTLE'

  Cenário: Estilo desconhecido
    Quando build_wood_hood é chamado com style = 'INEXISTENTE'
    Então a coifa é construída como BOX

  Cenário: Peça manual preservada
    Dado uma peça marcada IS_MANUAL_PART
    Quando a coifa é reconstruída em outro estilo
    Então a peça manual continua existindo

  Cenário: Reverter peça sem snapshot
    Dado apenas uma peça IS_MANUAL_PART sem HOOD_PARAMETRIC_SNAPSHOT selecionada
    Então blendertomob.revert_hood_part fica indisponível (poll falso)
    E a peça não é alterada

  Cenário: Operador fora de coifa
    Dado o objeto ativo com APPLIANCE_TYPE = 'RANGE'
    Então blendertomob.build_wood_hood fica indisponível (poll falso)

Funcionalidade: Registries

  Cenário: Provider com falha
    Dado um provider registrado para "tall_pantry" que levanta exceção
    Quando get_items("tall_pantry") é chamado
    Então retorna [] e imprime "HB5 accessory_registry: provider for tall_pantry failed"

  Cenário: Sem provider de specs
    Dado que nenhum provider foi registrado
    Quando get_provider() é chamado
    Então retorna None e a UI oferece só entrada manual
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Layout de porta, mínimos, malha com fallback, slots de material — RF-01..RF-08 | Must | Toda frente de armário do face frame e as portas de coifa passam por aqui |
| Carga e conversão de perfis — RF-15, RF-16 | Must | Pré-requisito de qualquer porta com perfil |
| Eletrodomésticos — RF-19 | Must | Usados por face frame, frameless e templates de elevação |
| Construção e reconstrução de coifa — RF-21, RF-22, RF-24 | Must | Único caminho de coifa de madeira |
| MITERED, raised, arcos, sticking, ajuste de espessura, bordas de catálogo — RF-09, RF-10, RF-12, RF-13, RF-17, RF-18 | Should | Enriquecem a porta; fallback para geometria simples existe |
| Variantes de eletrodoméstico, CUSTOM, prompts, migração de drivers, registry de acessórios — RF-20, RF-23, RF-25, RF-27, RF-28 | Should | Importantes com alternativa |
| Ranhuras, mullions, revert, registry de specs — RF-11, RF-14, RF-26, RF-29 | Could | Acionados em estilos específicos ou raramente |
| Propriedades TEXT, asset de lixeira — RF-30, RF-31 | Won't | Bug / asset sem consumidor |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `product_libraries/common/__init__.py` | reexport de `types_appliances`, `register/unregister` vazios | 🟢 |
| `product_libraries/common/door_builder.py` | `door_style_info`, `_frame_widths`, `layout_min_size`, `door_layout`, `evaluate_layout` | 🟢 |
| `product_libraries/common/door_builder.py` | `build_mitered_frame`, `_resample_loop`, `_emit_*`, `_clip_half`, `_mullion_layout`, `_curved_bar_polys`, `build_door_mesh` | 🟢 |
| `product_libraries/common/door_profiles.py` | `load_profile`, `sticking_section`, `panel_profile_section`, `sticking_strip`, `applied_strip`, `member_section`, `edge_profile_section`, `named_edge_section`, `sweep_edge_frame` | 🟢 |
| `product_libraries/common/types_appliances.py` | `Appliance` + 10 subclasses | 🟢 |
| `product_libraries/common/wood_hoods.py` | builders de estilo, `_FrontProfile`, `_wrap_shiplap`, `build_wood_hood`, `snapshot_hood_part`, `restore_hood_part`, 3 operadores | 🟢 |
| `accessory_registry.py` | registry host → provider | 🟢 |
| `appliance_spec_registry.py` | registry de provider único | 🟢 |
| `product_libraries/face_frame/style_options.py:5025-5250` | dados de série/perfil/painel (dependência, pertence a [`face_frame/`](../face_frame/)) | 🟡 |
| `product_libraries/common/Trash Pull Outs/Generic Trash Pullout.blend` | asset sem referência | 🔴 |
