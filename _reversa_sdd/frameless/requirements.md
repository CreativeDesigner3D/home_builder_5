# frameless — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-09-30, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-frameless`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#frameless`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-frameless-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/frameless/`
> salvo indicação.

## Visão Geral

O `frameless` é a **biblioteca paramétrica de marcenaria sem quadro frontal** (construção europeia, a mais próxima da
marcenaria brasileira). Gera gabinetes inferiores, aéreos, altos, de canto, gaveteiro "lap drawer", gabinete de
geladeira e produtos avulsos (prateleira flutuante, sanca, estrutura de apoio, meia-parede, pernas, painéis). Cada
gabinete é uma hierarquia de objetos com Geometry Nodes cujas medidas são **drivers** sobre prompts do objeto raiz. 🟢
O módulo também cuida de frentes, sobreposições, interiores, puxadores, estilos de gabinete e de porta, bancadas,
molduras extrudadas, templates de elevação e biblioteca do usuário. São 26 arquivos e ~23 mil linhas. 🟢
Todos os padrões nascem em polegadas (mercado dos EUA) e são guardados em metros. 🟢

## Responsabilidades

- Construir a carcaça de inferiores, altos e aéreos (laterais passantes, base, fundo, tampo/travessas, rodapé). 🟢
- Dividir vãos em aberturas por splitters verticais/horizontais com rateio de tamanhos. 🟢
- Gerar frentes (portas, gavetas, basculantes, frentes falsas) com sobreposição inset/meia/total. 🟢
- Gerar interiores (prateleiras reguláveis, divisores) e caixas de gaveta. 🟢
- Posicionar puxadores por tipo de gabinete e por posição do vão. 🟢
- Inserir gabinetes, produtos e eletrodomésticos com modal (parede, piso, preenchimento automático de vão). 🟢
- Trocar a configuração de um vão entre 30 tipos predefinidos. 🟢
- Aplicar estilos de gabinete (madeira/cor, interior, fita de borda, sobreposição) e de porta (lisa/5 peças). 🟢
- Criar bancadas, crown, rodapé decorativo e moldura inferior de aéreo por grupos de gabinetes adjacentes. 🟢
- Criar laterais aplicadas/acabadas e linhas de snap. 🟢
- Gerar elevações completas por template (Geladeira/Fogão e Ilha). 🟢
- Salvar e carregar grupos de gabinetes numa biblioteca do usuário. 🟢
- Guardar os padrões globais na cena (`Scene.hb_frameless`). 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `FRAMELESS-Rnn`). `mt` = espessura da chapa, `tkh`/`tks` =
altura/recuo do rodapé, `lo/ro/to/bo` = sobreposição esquerda/direita/topo/base.

**Carcaça**
- RN-01 (R01): laterais passantes; base, fundo, tampo, rodapé e travessas medem `dim_x − 2·mt` e ficam entre as laterais. 🟢
- RN-02 (R02): fundo com espessura `mt` (chapa cheia) embutido entre as laterais; inferior: `z = tkh + mt`, `L = dim_z − tkh − mt`; alto desconta mais `mt`. Não há fundo fino encaixado. 🟢
- RN-03 (R03): rodapé — 0 laterais entalhadas até o piso (`CPM_CORNERNOTCH` X=tkh, Y=tks) + painel em `y = −dim_y + tks`; 1 escada (placeholder); 2 flutuante; 3 quatro niveladores. Nos tipos 1–3 as laterais começam em `z = tkh`. 🟢
- RN-04 (R04): o tipo de rodapé só vale na criação; alterá-lo depois não reconstrói. 🟡
- RN-05 (R05): topo do inferior — 0 tampo inteiro; 1 duas travessas de 4"; 2 avental de pia de 7". A UI da cena só oferece Stretchers (padrão) e Full Top. 🟢
- RN-06 (R06): vão do inferior em `(mt, −dim_y, tkh + IF(rb, 0, mt))` com `(dim_x − 2mt, dim_y − mt, dim_z − tkh − IF(rb, 0, mt) − mt)`; aéreo `(dim_x − 2mt, dim_y − mt, dim_z − 2mt)`. 🟢
- RN-07 (R07): "Remove Bottom" oculta base e rodapé e leva o fundo até z = 0. 🟢

**Tipos especiais**
- RN-08 (R08): Lap Drawer — altura = `top_drawer_front_height` (6"), topo alinhado ao do inferior, sem rodapé. 🟢
- RN-09 (R09): gabinete de geladeira — carcaça alta sem base e sem rodapé; vão inferior vazio de `refrigerator_height` (62"); portas em cima; largura padrão 38". 🟢
- RN-10 (R10): exterior padrão do inferior pelo nome ("Base Door", "Base Door Drw", "Base Drawer"); topo da pilha de gavetas = `top_drawer_front_height` ou alturas iguais. 🟢
- RN-11 (R11): alto empilhado com porta inferior de 54"; aéreo empilhado com porta superior de 15". 🟢
- RN-12 (R23/R24): canto pie-cut em L com `Left/Right Depth`, entalhes `CPM_CORNERNOTCH`, dois fundos, dois rodapés e duas portas articuladas; diagonal usa `CPM_CHAMFER`; tamanho padrão 36" (base/alto) e 24" (aéreo); encosta na ponta da parede quando o cursor está a menos de uma largura dela. 🟢

**Aberturas, frentes e interiores**
- RN-13 (R12): splitter — `qtd + 1` vãos; altura útil `dim_z − mt·qtd`; tamanho 0 = rateio igual `(total − Σ fixos)/n_iguais`. 🟢
- RN-14 (R13): vãos internos de splitter recebem `FORCE_HALF_OVERLAY_*`, preservados ao aplicar estilo. 🟢
- RN-15 (R14): sobreposição por lado — inset `−1/8"`; meia `(espessura − vertical_gap)/2`; total `espessura − reveal` (reveal topo/laterais 1/16", base 0); calculada num empty separado para evitar ciclo de dependência. 🟢
- RN-16 (R15): porta com `x = −lo`, `z = −bo`, altura `dim_z + to + bo`, largura `dim_x + lo + ro` (simples) ou `(dim_x + lo + ro − vg)/2` (dupla); Y inset = `ft`, senão `−1/8"`. Door Swing 0/1/2. 🟢
- RN-17 (R16): prateleiras reguláveis em array; 1ª em `(dim_z − mt·qty)/(qty + 1)`; folga 1/8" por lado; recuo frontal 1/4"; interior recua `ft` quando inset. 🟢
- RN-18 (R17): quantidade padrão de prateleiras por profundidade e altura (prof. ≤ 18": 1/2/3/4 até 20/32/44"; > 18": até 28/40/52"). 🟢
- RN-19 (R18): caixa de gaveta `X = largura − lo − ro − 1"`, `Y = prof_vão − 1"`, `Z = altura − to − bo − 1,25"`; só com `include_drawer_boxes` e fora de frente falsa. 🟢
- RN-20 (R43): incluir/remover caixas de gaveta é global — o callback percorre a cena. 🟢
- RN-21 (R22): configurações de vão com tamanhos fixos (eletro 30", duplo eletro 2×30" + gaveta 6", micro-ondas + gaveta 6", portas + basculante 8", portas 18" + tall pullout). 🟢

**Puxadores**
- RN-22 (R19): Base mede do topo da porta (1,5"); Tall do pé ao centro (45"); Upper do pé (1,5"); horizontal a 2" da borda; gaveta centralizada; comprimento 4" sem objeto. 🟢
- RN-23 (R20): após trocar vão, a posição vem da altura no mundo: < 36" Base; ≥ 48" Upper; entre = Tall (com exceções para portas baixas). 🟢
- RN-24 (R21): em splitter de alto: 1 vão Tall; 2 vãos Upper/Base; 3+ Upper/Tall/Base. 🟢

**Estilos e materiais**
- RN-25 (R25): porta 5 peças com mínimo `2·montante + 1"` × `2·travessa + 1"` (+ mid rail); abaixo do mínimo `assign_style_to_front` devolve uma mensagem de erro (string) e não aplica o estilo; portas > 45,5" ganham travessa central automática; montantes com veio vertical, travessas com material ROTATED. 🟢 (`props_hb_frameless.py:1069-1092`)
- RN-26 (R26): material por face via `Finish Top/Bottom`; `Finished Interior` força acabamento; frentes com ambos; prateleiras/travessas sem; padrão Top False / Bottom True. 🟢
- RN-27 (R27): fita de borda = material customizado ou acabamento ROTATED, nas 4 bordas. 🟢
- RN-28 (R28): acabamento pelo node group "Wood" com par normal/ROTATED e grão por espécie; PAINT_GRADE sem grão. 🟢
- RN-29 (R29): estilo vinculado por **índice**; remover um estilo reatribui 0 a quem o usava e decrementa os maiores. 🟢
- RN-30 (R30): `tall = pé-direito − folga superior`; `upper = pé-direito − folga − altura de instalação do aéreo`. 🟢
- RN-31 (R44): cores do usuário em `extension_path_user(.../user_data/custom_colors.json)`; mesmo nome sobrescreve a cor padrão. 🟢

**Inserção**
- RN-32 (R31): preenchimento automático com `qtd = ceil(gap/36")`; snap de centro 4"; parede ≤ 6"; histerese de lado 1". 🟢
- RN-33 (R32): Z de inserção — aéreo a 54"; coifa a 54" até o teto; Support Frame com topo no topo do inferior; prateleira flutuante e sanca seguem o cursor (arredondado à polegada). 🟢
- RN-34 (R36): "Drop to countertop" desce o aéreo até `base_cabinet_height + countertop_thickness`, mantendo o topo. 🟢

**Pós-processamento (geometria estática)**
- RN-35 (R33): bancada 1,5" com balanço frontal 1", lateral 1" (suprimido junto a parede conectada ou alto adjacente ±5 mm), traseiro 0; recorte nos fogões; L nos cantos. 🟢
- RN-36 (R34): crown só em UPPER/TALL; rodapé decorativo só em BASE/TALL; agrupamento por adjacência (±2 cm, topos alinhados); pontas encostam na parede, morrem no vizinho não selecionado ou retornam em esquadria. 🟢
- RN-37 (R35): lateral aplicada com profundidade `dim_y + 0,875"` embutida na expressão (não ligada aos prompts); 5 peças com largura `dim_y − 0,75"`. 🟢

**Produtos**
- RN-38 (R37): Support Frame com travessas a cada 16" e pernas 3,5 × 3,5 × 34,5". 🟢
- RN-39 (R38): meia-parede com montantes a cada 16", pele 1/4", montante 3/4". 🟢
- RN-40 (R39): prateleira flutuante oca com rasgo de LED opcional (1/2" × 1/4", inset 2") via `CPM_CUTOUT`. 🟢
- RN-41 (R40): pernas (Leg/TallLeg/UpperLeg) com painéis entalhados; "Override Panel Depth" 0 = profundidade total. 🟢

**Templates e biblioteca**
- RN-42 (R41): template Geladeira/Fogão ocupa pantry → geladeira → inferiores (em volta do fogão) → aéreos; larguras = área / quantidade (1–6). 🟢
- RN-43 (R42): template Ilha com gabinetes girados 180° a 72" da parede, não parentados; pia central e lava-louças laterais. 🟢
- RN-44 (R45): grupo salvo com `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)` e miniatura 256 px. 🟢

**Comportamentos desconhecidos**
- 🔴 Cantos diagonais alto/aéreo são só a gaiola; o diagonal inferior não tem portas.
- 🔴 Rodapé "Ladder", rollouts e TRAY_DIVIDERS não implementados.
- 🔴 `update_base_top_construction_prompts` e `update_drawer_front_height_prompts` são TODO.
- 🔴 Várias propriedades de cena sem efeito (`base_exterior`, blind corner, `show_machining`, `RAISE_UPPER`, `edge_profile_type`, perfis de borda).

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Criar gabinete inferior com carcaça, vão e exterior padrão | Must | Peças em RN-01/RN-02/RN-06; drivers seguem `Dim X/Y/Z` |
| RF-02 | Criar aéreo e alto (incluindo empilhados) | Must | Vão do aéreo `dim_z − 2mt`; alto com porta inferior de 54" |
| RF-03 | Rodapé nos 4 tipos na criação | Should | Tipo 0 entalha as laterais; tipo 3 cria 4 niveladores |
| RF-04 | Construção do topo do inferior (tampo, travessas, avental) | Should | Só a peça do tipo escolhido fica visível |
| RF-05 | Lap Drawer e gabinete de geladeira | Should | Geladeira: vão inferior vazio de 62", sem base |
| RF-06 | Cantos pie-cut (inferior, alto, aéreo) | Should | Entalhes e duas portas conforme RN-12 |
| RF-07 | Cantos diagonais completos | Won't | Stubs no legado (alto/aéreo só gaiola) |
| RF-08 | Splitter vertical/horizontal com rateio | Must | 3 vãos com um fixo de 6" em 30" úteis → iguais de 12" |
| RF-09 | Trocar a configuração do vão (30 tipos) | Must | Filhos do vão recriados; puxadores relocalizados |
| RF-10 | Frentes com sobreposição inset/meia/total por lado | Must | Valores de RN-15; sem ciclo de dependência |
| RF-11 | Portas simples/duplas e Door Swing | Must | Dupla: duas folhas de `(dim_x + lo + ro − vg)/2` |
| RF-12 | Gavetas, basculantes e frentes falsas; caixas de gaveta | Must | Caixa com as folgas de RN-19; frente falsa sem caixa |
| RF-13 | Prateleiras reguláveis com quantidade padrão | Must | Prof. 12", altura 30" → 2 prateleiras |
| RF-14 | Divisores internos customizados | Should | Divisores criados no interior sem sobrepor prateleiras |
| RF-15 | Puxadores posicionados por tipo/posição | Must | Base a 1,5" do topo; após troca de vão, regra RN-23 |
| RF-16 | Inserção modal na parede com preenchimento automático | Must | Vão livre de 80" → 3 gabinetes de 26,67" |
| RF-17 | Inserção no piso com snap a vizinho | Should | Gabinete encosta no vizinho |
| RF-18 | Inserir eletrodomésticos (via `types_appliances`) | Should | Coifa a 54" até o teto |
| RF-19 | Modo de seleção por nível (Cabinets/Bays/Openings/Interiors/Parts) | Should | Só objetos com o marcador do nível ficam selecionáveis |
| RF-20 | Estilos de gabinete: CRUD, pintura modal, atualização em lote | Must | Remover estilo reindexa os gabinetes |
| RF-21 | Estilos de porta lisa/5 peças | Must | Porta de 50" ganha travessa central; porta abaixo do mínimo devolve mensagem e fica sem o estilo |
| RF-22 | Materiais de madeira por espécie e cores tingidas/pintadas + cores do usuário | Should | Cor do usuário persiste após reiniciar o Blender |
| RF-23 | Propagar padrões da cena para gabinetes existentes (rodapé, espessura, alturas) | Should | `update_cabinet_sizes` altera todos os gabinetes |
| RF-24 | Alturas derivadas do pé-direito | Must | Pé-direito 96", folga 12", aéreo 54" → tall 84", upper 30" |
| RF-25 | Bancadas por corrida de parede, grupo e ilha | Should | Recorte no fogão; L no canto |
| RF-26 | Crown, rodapé decorativo e moldura inferior por grupo | Could | Retorno em esquadria na ponta exposta |
| RF-27 | Laterais aplicadas/acabadas (slab/5 peças) | Should | Profundidade `dim_y + 0,875"` |
| RF-28 | "Drop to countertop" | Could | Topo do aéreo inalterado |
| RF-29 | Produtos: prateleira flutuante, sanca, Support Frame, meia-parede, pernas, painel, peça avulsa | Should | Contagem de travessas/montantes de RN-38/RN-39 |
| RF-30 | Templates Geladeira/Fogão e Ilha com preview | Could | Preview atualiza ao mudar quantidades; `draw_cabinets` cria os reais |
| RF-31 | Biblioteca do usuário: salvar, carregar, apagar grupos | Could | Grupo salvo reaparece na lista após "refresh" |
| RF-32 | Linhas de snap na parede | Could | Inserção respeita o limite da linha |
| RF-33 | Limpeza de malha (dissolve, faces soltas, reconstruir) | Could | Operadores com undo |
| RF-34 | Rodapé Ladder, rollouts, TRAY_DIVIDERS, propriedades sem efeito | Won't | Não implementados no legado |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Consistência | Sobreposição calculada num empty separado para evitar ciclo de dependência nos drivers | `types_frameless.py:1156-1210` | 🟢 |
| Consistência | Reavaliação forçada (`run_calc_fix` ×2) após criar gabinete | `operators/ops_placement.py` (fluxo de confirmação) | 🟢 |
| Performance | Estilos aplicados em lote por timer modal (não trava a UI) | `operators/ops_styles.py:673-789` | 🟢 |
| Performance | Enums de puxadores e cores lidos do disco a cada redraw | `props_hb_frameless.py:108-134`, `finish_colors.py:207-225` | 🟢 |
| Persistência | Cores do usuário na pasta de extensão do usuário | `finish_colors.py:21-27` | 🟢 |
| Portabilidade | Biblioteca com caminhos relativos e `fake_user` | `operators/ops_library.py:99-300` | 🟢 |
| Robustez | `register()` engole exceções | `props_hb_frameless.py:2537-2558`, `operators/ops_placement.py:1986-2007` | 🟢 |
| Undo | Vários operadores que alteram dados sem `UNDO`; diálogos alteram dados em `check()` | `operators/ops_defaults.py:4-35`, `operators/ops_cabinet.py:52-94` | 🟢 |
| Compatibilidade | `Material.use_nodes` e `blend_method` obsoletos no 5.x | `props_hb_frameless.py:269, 310, 313` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Carcaça do inferior

  Cenário: Inferior padrão
    Dado mt = 3/4", tkh = 4", Dim X = 36", Dim Z = 34,5"
    Quando BaseCabinet é criado com rodapé tipo 0
    Então a base mede 34,5" de largura e fica em z = 4,75"
    E as laterais descem até o piso com entalhe de 4" × 2,5"

  Cenário: Remove Bottom
    Dado um inferior com Remove Bottom = True
    Então base e rodapé ficam ocultos e o fundo começa em z = 0

  Cenário: Trocar o tipo de rodapé depois de criado
    Dado um inferior criado com rodapé tipo 0
    Quando o prompt Toe Kick Type muda para 3
    Então a geometria não é reconstruída (comportamento legado)

Funcionalidade: Splitter

  Cenário: Rateio com um vão fixo
    Dado um splitter vertical com 2 divisórias, altura útil 30" e o vão de cima fixo em 6"
    Quando a calculadora roda
    Então os dois outros vãos ficam com 12" cada

  Cenário: Lista de tamanhos menor que a quantidade de vãos
    Dado opening_sizes com menos itens que a quantidade de vãos
    Quando SplitterVertical.create é executado
    Então ocorre IndexError (lacuna legada)

Funcionalidade: Frentes

  Cenário: Sobreposição total
    Dado estilo com overlay FULL e lateral de 3/4"
    Então lo = ro = to = 3/4" − 1/16" e bo = 3/4"

  Cenário: Porta muito pequena para 5 peças
    Dado estilo 5 peças com montantes de 2,5"
    Quando assign_style_to_front é aplicado a uma porta de 5,5" de largura
    Então a função devolve a mensagem "Front too narrow (…) for stile widths (…)"
    E o modificador CPM_5PIECEDOOR não é adicionado

Funcionalidade: Inserção

  Cenário: Preenchimento automático
    Dado um vão livre de 80" numa parede
    Quando o usuário confirma a inserção de "Base Door" com preenchimento
    Então 3 gabinetes de 80/3" são criados lado a lado

  Cenário: Cursor longe de parede
    Dado o cursor a mais de 6" de qualquer parede
    Então o gabinete é colocado no piso, com snap a vizinhos

Funcionalidade: Estilos

  Cenário: Remover estilo em uso
    Dado os estilos 0, 1 e 2, com gabinetes nos estilos 1 e 2
    Quando o estilo 1 é removido
    Então os gabinetes do estilo 1 passam ao 0 e os do 2 passam ao 1

Funcionalidade: Bancada

  Cenário: Corrida com fogão
    Dado três inferiores contíguos com um fogão no meio
    Quando add_countertops é executado
    Então a bancada tem 1,5" de espessura, balanço frontal de 1" e é interrompida no fogão

  Cenário: Ponta encostada em alto
    Dado um inferior adjacente (±5 mm) a um alto
    Então o balanço lateral desse lado é suprimido
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Carcaças, splitter, frentes, interiores, puxadores — RF-01, RF-02, RF-08..RF-13, RF-15 | Must | Núcleo de todo gabinete |
| Inserção modal na parede — RF-16 | Must | Único caminho de criação pela UI |
| Estilos de gabinete e porta, alturas derivadas — RF-20, RF-21, RF-24 | Must | Aplicados em toda criação |
| Rodapé, topo, especiais, cantos, divisores, piso, eletros, seleção, materiais, propagação, bancada, laterais, produtos — RF-03..RF-06, RF-14, RF-17..RF-19, RF-22, RF-23, RF-25, RF-27, RF-29 | Should | Importantes, com alternativa |
| Molduras, drop, templates, biblioteca, snap lines, limpeza — RF-26, RF-28, RF-30..RF-33 | Could | Pós-processamento ou uso ocasional |
| Diagonais completos, Ladder, rollouts, props sem efeito — RF-07, RF-34 | Won't | Não implementados no legado |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `types_frameless.py` | `Cabinet`, `BaseCabinet`, `LapDrawerCabinet`, `TallCabinet`, `RefrigeratorCabinet`, `UpperCabinet`, splitters, aberturas, frentes, interiores, cantos | 🟢 |
| `types_products.py` | `Product`, `FloatingShelf`, `Valance`, `SupportFrame`, `HalfWall`, `MiscPart`, `Leg`, `TallLeg`, `UpperLeg`, `Panel` | 🟢 |
| `props_hb_frameless.py` | `Frameless_Scene_Props`, `Frameless_Cabinet_Style`, `Frameless_Door_Style`, puxadores, detalhes | 🟢 |
| `props_elevation_templates.py` | `Refrigerator_Range_Template`, `Island_Template` | 🟢 |
| `wood_materials.py`, `finish_colors.py` | espécies, cores, cores do usuário | 🟢 |
| `menus_frameless.py` | menus por `MENU_ID` | 🟢 |
| `operators/ops_placement.py` | `hb_frameless.place_cabinet`, `draw_cabinet`, `toggle_mode` | 🟢 |
| `operators/ops_cabinet.py`, `ops_opening.py`, `ops_interior.py`, `ops_front.py`, `ops_appliance.py` | prompts e edição | 🟢 |
| `operators/ops_styles.py`, `ops_defaults.py`, `ops_finished_ends.py` | estilos e propagação | 🟢 |
| `operators/ops_countertop.py`, `ops_crown.py`, `ops_toe_kick.py`, `ops_upper_bottom.py` | pós-processamento | 🟢 |
| `operators/ops_products.py`, `ops_library.py`, `ops_snap_line.py`, `ops_cleanup.py` | produtos, biblioteca, snap, limpeza | 🟢 |
