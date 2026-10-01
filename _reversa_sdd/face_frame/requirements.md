# face_frame — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-face_frame`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#face_frame`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-face_frame-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/face_frame/`
> salvo indicação. Medidas entre parênteses em mm.

## Visão Geral

O `face_frame` é a **biblioteca de marcenaria com moldura frontal** no estilo norte-americano: a frente do gabinete é um
quadro de montantes (stiles) e travessas (rails) de 3/4", e as portas/gavetas sobrepõem ou embutem nesse quadro. 🟢
Cobre base, aéreo, torre, lap drawer, painéis, cantos (pie-cut, diagonal, pie-cut com gavetas), móveis (cômodas,
criados-mudos, window seat), banheiro (medicine cabinet, tri-view, tub skirt), produtos lineares e peças soltas. 🟢
Diferente do frameless, usa um **solver Python puro** (sem drivers): as propriedades alimentam um solver que escreve os
inputs de Geometry Nodes e recria frentes e itens internos a cada recálculo. 🟢
São 31 arquivos, ~60 800 linhas — o maior módulo do projeto, com catálogo comercial do fornecedor americano CWP. 🟢

## Responsabilidades

- Criar o gabinete a partir do catálogo (classe por nome) e um preset de bay padrão. 🟢
- Distribuir larguras de bays e tamanhos da árvore de aberturas com travas por item (locked/unlocked + share). 🟢
- Montar a carcaça (laterais, fundo, costas, tampo/travessas, rodapé) e a moldura (stiles, rails, mid stiles, mid rails). 🟢
- Segmentar rails ao longo de bays compatíveis. 🟢
- Percorrer a árvore recursiva de aberturas (splits H/V) e gerar frentes (porta, gaveta, pullout, false front, tilt-out,
  inset panel, appliance), backings e itens internos. 🟢
- Detectar exposição lateral/traseira e escolher acabamento e scribe automáticos. 🟢
- Gerar painéis aplicados e acabamentos de ponta (finished, paneled, beadboard, shiplap, flush-x). 🟢
- Aplicar estilos (madeira, cor, overlay, porta, série do catálogo) e puxadores. 🟢
- Inserir gabinetes por modal (parede, ilha, frente de fogão, cantos), com auto nº de bays e fusão com vizinho. 🟢
- Editar por sidebar, rótulos de dimensão editáveis, arraste de fronteiras e comandos por peça. 🟢
- Gerar tampos, painéis de eletrodoméstico, cunha tip-up, biblioteca do usuário e miniaturas. 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `FACE_FRAME-Rnn`). `fft` = espessura da moldura.

**Geometria e carcaça**
- RN-01 (R01): origem no canto traseiro-esquerdo no piso; +X à direita, −Y para a frente (frente em `y = −depth`); a carcaça começa em `−depth + fft`. 🟢
- RN-02 (R02): rodapé só em BASE, TALL e LAP_DRAWER; BASE/LAP_DRAWER com travessas frontal+traseira, UPPER/TALL com tampo sólido; gabinete angular sempre com tampo sólido. 🟢
- RN-03 (R06/R07): lateral FINISHED de 3/4" (offset 0); PANELED offset 3/4"; FLUSH_X/BEADBOARD/SHIPLAP 1/4"; demais = scribe; carcaça em `material_thickness` (padrão 1/2"); costas 1/4"; fundo acabado separado de 3/4". 🟢
- RN-04 (R08/R09): topo da carcaça = topo do bay − top_scribe; BASE/TALL ancoram no piso, UPPER no topo. 🟢
- RN-05 (R40): aéreo com lateral UNFINISHED apoia sobre o fundo; FINISHED desce até o fundo do bay. 🟢

**Bays e moldura**
- RN-06 (R03): bay destravado = (disponível − stiles das pontas − mid stiles − bays travados) / nº destravados; o disponível desconta o blind ou usa a hipotenusa no modo angular. 🟢 Sem clamp para valor negativo. 🟡
- RN-07 (R04): editar largura do bay, altura do rodapé ou tamanho interior trava o item automaticamente; escritas do sistema (guarda `_DISTRIBUTING_WIDTHS`) não travam. 🟢
- RN-08 (R05): bays destravados seguem profundidade, altura, rodapé e rails do gabinete. 🟢
- RN-09 (R10): um top rail atravessa um gap só se o mid stile não sobe, topos e larguras iguais e sem front_drop; bottom rail exige extend_down 0, sem to_floor, fundos iguais e sem remove_bottom. 🟢
- RN-10 (R11): rodapé FLUSH leva o bottom rail ao piso com largura `kick + bottom_rail`. 🟢
- RN-11 (R12): mid stile da menor base à maior altura dos vizinhos (± rails que atravessam ± extensões); nunca é destruído (um por gap). 🟢
- RN-12 (R13/R16): remove_bottom zera o bottom rail e cresce a abertura para baixo, zerando o overlay inferior; com vão inferior sem frente, o último splitter vira BOTTOM_RAIL. 🟢
- RN-13 (R29/R30): largura de stile por tipo (BLIND, WALL/BUTT/INSIDE_90/ANGLE, STANDARD) e tabela de larguras por overlay × (base, tall, upper). 🟢
- RN-14 (R35): nº automático de bays = `ceil((largura − 1/16")/36")`, entre 1 e 10. 🟢

**Aberturas e frentes**
- RN-15 (R15): mid rail removido colapsa o espaço para 3/32" + overlays (só em splits H). 🟢
- RN-16 (R17): backing automático — split H → prateleira fixa 3/4"; split V → divisão centrada no mid stile. 🟢
- RN-17 (R18/R31): overlay por lado = valor da abertura se destravado, senão o padrão do estilo (CLASSIC 0,5"; TRANSITIONAL 0,625/0,875"; FULL 1,0/0,875"; PARTIAL_INSET e FULL_INSET com inset calculado). 🟢
- RN-18 (R19): porta = vão + overlays; 1/8" à frente da moldura menos o inset; abertura máx. 100°; porta dupla com fresta 1/8". 🟢
- RN-19 (R20): gaveta/pullout desliza até `bay_depth − fft − 1"`; FALSE_FRONT não desliza; TILT_OUT com dobradiça inferior; INSET_PANEL = painel 1/4". 🟢
- RN-20 (R14): porta de vaidade destravada fica 4" mais larga que a cota igual dos irmãos. 🟢
- RN-21 (R21): tri-view — 3 portas espelho iguais, fresta 1/8", quadro 1,25". 🟢
- RN-22 (R22): fillers de eletrodoméstico = `(vão − eletro)/2`; sem `set_appliance_width`, valores digitados escalados se excederem o vão. 🟢
- RN-23 (R23/R24): prateleiras automáticas por altura e profundidade (máx. 4); selecionar DOOR garante uma prateleira regulável. 🟢
- RN-24 (R33): `SIZE_ROLE` fixa tamanhos — TOP_DRAWER 4,5", TALL_SPLIT_BOTTOM 54", UPPER_STACKED_TOP 12", REFRIGERATOR 69", VANITY_SINK_WIDTH 20", BOOKCASE_STORAGE_BOTTOM 30". 🟢
- RN-25 (R32): preset padrão na inserção — bay ≥ 18" → porta dupla/variante larga; menor → porta simples; tabela por nome de catálogo. 🟢
- RN-26 (R41): puxador — gaveta centralizada (ou 1,5" do topo); upper a 1,5" da base; tall a 36" do chão; base a 1,5" do topo; horizontal a 1,5" da borda livre. 🟢

**Exposição e acabamento**
- RN-27 (R25): exposição por lado — parede/ponta encostada ou cobertura Z total → UNEXPOSED; parcial → PARTIAL; sem vizinho → EXPOSED; costas por parede ou costas de ilha coincidentes. 🟢
- RN-28 (R26/R27): acabamento automático — lava-louças pela preferência; PARTIAL → FINISHED; EXPOSED → padrão da cena; UNEXPOSED → UNFINISHED; scribe 1/2" parede, 1/4" vizinho; editar manualmente desliga o auto daquele lado. 🟢
- RN-29 (R28): painel aplicado PANELED com porta 5 peças calcula rails/stiles a partir do gabinete e da porta (A9: nº de aberturas por largura, ≤ 20" → 1 … > 128" → 8). 🟢

**Tipos especiais**
- RN-30 (R38): geladeira — stiles ao piso, rodapé 0, remove_bottom em todos os bays, `back_bottom_inset` calculado. 🟢
- RN-31 (R39): lap drawer — BASE com rodapé FLOATING e elevação de 27"; presets LAP_DRAWER/SUPPORT_FRAME levam os stiles vizinhos ao piso. 🟢
- RN-32 (R44): cantos — seções distribuídas por A1; diagonal com moldura `√((w−ld)² + (d−rd)²)`. 🟢
- RN-33 (A6): cunha tip-up — `diag = √(d² + h²)`; se `diag > teto − folga`, gera cunha. 🟢
- RN-34 (A7): moldura angular — `θ = atan2(ld − rd, w)`, `L = hypot(w, rd − ld)`; só 1 bay e sem canto. 🟢

**Edição, fusão e preservação**
- RN-35 (R36): fusão automática com vizinho exige mesma altura/profundidade/Z, mesmo parent, ambos sem canto, encostados ±1"; TALL, leg, floating shelf e valance não fundem. 🟢
- RN-36 (R37): quebrar gabinete remove o mid stile do gap e usa stiles "butt" nas novas pontas; cantos não quebram. 🟢
- RN-37 (R42): peças `IS_MANUAL_PART` (ou sem GN) e aberturas `IS_MANUAL_FRONT` ficam fora da reescrita. 🟢
- RN-38 (R34): recálculo por `WRAP_CLASS_REGISTRY`; classes ausentes (móveis, cômodas, window seat, hutch…) caem na base, cujo `_has_toe_kick()` é False → rodapés zerados após qualquer edição. 🟢 (ausência) / 🟡 (efeito)

**Tampo**
- RN-39 (R43): espessura 1,5", balanço frontal 1", laterais 1", traseiro 0; sem balanço junto a tall ou parede conectada; cantos em L. 🟢

**Comportamentos desconhecidos**
- 🔴 Recálculo detalhado dos cantos (~1 500 linhas: bifold, revolving, lazy susan, clip back) lido por amostragem.
- 🔴 Fórmulas dos passes pós-recálculo (painéis aplicados texturizados, flush-x, retornos, extensão de costas, cortadores).
- 🔴 Divisórias com profundidades diferentes, segmentos de fundo/costas e solvers de itens internos (rollout, tray dividers, vanity shelves).
- 🔴 `recalculate` próprio de Leg/FloatingShelf/Valance.
- 🟡 `LAP_DRAWER` no enum sem quem grave esse valor; duas alturas de geladeira (69" × 62") que podem divergir.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Criar gabinete pela classe do catálogo, com preset de bay padrão e recálculo único | Must | `create_carcass` faz um único `recalculate()`; preset conforme RN-25 |
| RF-02 | Distribuir larguras de bays com travas e share | Must | 3 bays em 90" com um travado de 24" → os outros com a mesma largura |
| RF-03 | Travar automaticamente o item editado pelo usuário | Must | Editar `bay.width` liga `unlock_width`; distribuição do sistema não trava |
| RF-04 | Montar carcaça e moldura por tipo de gabinete | Must | Rodapé só em BASE/TALL/LAP_DRAWER; UPPER ancorado no topo |
| RF-05 | Segmentar rails e posicionar mid stiles | Must | RN-09/RN-11; um mid stile por gap |
| RF-06 | Percorrer a árvore de aberturas e gerar frentes, backings e itens internos | Must | Splits H/V aninhados geram as folhas certas; backing automático |
| RF-07 | Overlay por lado e geometria de portas/gavetas | Must | RN-17..RN-19 |
| RF-08 | Remove bottom, mid rail removido e casos de bottom rail | Should | RN-12, RN-15 |
| RF-09 | Exposição e acabamento automático com scribe | Must | Gabinete isolado → laterais FINISHED; encostado em parede → UNFINISHED com scribe 1/2" |
| RF-10 | Painéis aplicados e acabamentos de ponta | Should | Lateral PANELED com nº de aberturas por largura (A9) |
| RF-11 | Estilos (madeira, cor, overlay, porta, série) e puxadores | Must | Trocar o overlay do estilo muda larguras de moldura e overlays |
| RF-12 | Inserção modal com auto nº de bays, fill-to-gap e fusão com vizinho | Must | 72" livres → 2 bays; vizinho compatível → um só gabinete |
| RF-13 | Quebrar e juntar gabinetes | Should | RN-36 |
| RF-14 | Editar por rótulos de dimensão e arraste de fronteiras | Should | Digitar no rótulo altera e trava a dimensão |
| RF-15 | Comandos por peça (largura, scribe, stile ao piso, remover rail, tornar editável/reverter) | Should | Peça manual sobrevive ao recálculo |
| RF-16 | Cantos pie-cut, diagonal e pie-cut com gavetas | Should | Tipo desconhecido não deve levantar `NotImplementedError` para o usuário |
| RF-17 | Geladeira, lap drawer, vaidade, tri-view, móveis e produtos lineares | Should | RN-20, RN-21, RN-30, RN-31 |
| RF-18 | Tampos por corrida e ilha | Should | RN-39 |
| RF-19 | Painéis de eletrodoméstico panel-ready com provider de specs | Could | Sem provider → só entrada manual |
| RF-20 | Cunha tip-up e moldura angular | Could | RN-33, RN-34 |
| RF-21 | Abrir/fechar frentes com animação sem recálculo | Could | Abrir não altera dimensões |
| RF-22 | Biblioteca do usuário e miniaturas | Could | Grupo salvo reaparece na lista |
| RF-23 | Recálculo correto para móveis e cômodas (classes fora do registro) | Must | Editar uma cômoda não zera o rodapé (corrige RN-38) |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Consistência | Guardas de reentrância (`suspend_recalc`, `_DISTRIBUTING_WIDTHS`) evitam recálculos em cascata | `types_face_frame.py:1029-1037`, `:8765-8777`; `props_hb_face_frame.py:4031-4098` | 🟢 |
| Desempenho | Muitas escritas fora de `suspend_recalc` disparam vários recálculos completos por ação | `exposure.py:416-440`; `props_hb_face_frame.py:1668-1690` | 🟡 |
| Robustez | Frentes, pivôs, puxadores e splitters apagados e recriados a cada recálculo | `types_face_frame.py:5785-5830`, `:5961-5972` | 🟢 |
| Robustez | Erros silenciosos (registro, dreno de recálculo); funções do solver devolvem valores neutros | `types_face_frame.py:103-106`; `props_hb_face_frame.py:8064-8085` | 🟢 |
| Compatibilidade | Escrita `cab_props['refrigerator_opening_height']` não altera a `bpy.props` desde o 5.0 | `types_face_frame.py:7335` | 🟢 |
| Compatibilidade | Enums dinâmicos sem cache das strings | `props_hb_face_frame.py:195-258`, `:6406-6425` | 🟢 |
| Recursos | Draw handler POST_PIXEL permanente (`dim_edit_overlay`) removido no `unregister`; `split_preview` não | `dim_edit_overlay.py:897-922`; `split_preview.py:218-236` | 🟢 |
| Persistência | Cores do usuário em `extension_path_user` | `finish_colors.py:16-…` | 🟢 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Distribuição de bays

  Cenário: Bays iguais com um travado
    Dado um gabinete base de 90" com 3 bays, stiles de ponta de 1,5" e mid stiles de 2"
    E o bay do meio travado em 24"
    Quando o gabinete é recalculado
    Então os outros dois bays ficam com (90 − 3 − 4 − 24)/2 = 29,5" cada

  Cenário: Edição do usuário trava o bay
    Dado um bay destravado
    Quando o usuário digita 20" na largura do bay
    Então unlock_width do bay fica ligado
    E uma nova distribuição do sistema não altera esse bay

  Cenário: Bays travados maiores que o gabinete
    Dado bays travados que somam mais que a largura disponível
    Quando o gabinete é recalculado
    Então o bay destravado recebe largura negativa (comportamento legado, sem clamp)

Funcionalidade: Rails e mid stiles

  Cenário: Top rail contínuo
    Dado dois bays com topos e larguras de rail iguais e mid stile que não sobe
    Então um único top rail atravessa os dois bays

  Cenário: Bay com remove_bottom
    Dado um bay com remove_bottom ligado
    Então o bottom rail desse bay some e a abertura cresce para baixo

Funcionalidade: Exposição

  Cenário: Gabinete isolado
    Dado um gabinete base sem vizinhos e sem parede nas pontas
    Quando a exposição é calculada
    Então as duas laterais ficam EXPOSED e recebem o acabamento padrão (FINISHED)

  Cenário: Ponta encostada na parede
    Dado a ponta esquerda encostada numa parede
    Então o lado esquerdo fica UNEXPOSED, UNFINISHED, com scribe de 1/2"

  Cenário: Acabamento manual
    Dado o usuário escolhe PANELED no lado direito
    Então o auto do lado direito é desligado e futuras exposições não mudam esse lado

Funcionalidade: Inserção

  Cenário: Auto nº de bays
    Quando o usuário insere um base de 72" com preenchimento
    Então o gabinete nasce com ceil((72 − 1/16)/36) = 2 bays

  Cenário: Fusão com vizinho
    Dado um base existente com mesma altura, profundidade e Z, encostado a menos de 1"
    Quando outro base é inserido ao lado
    Então os dois viram um único gabinete com os bays somados

  Cenário: TALL não funde
    Dado um tall encostado num base
    Então nenhuma fusão acontece

Funcionalidade: Preservação

  Cenário: Peça manual
    Dado uma peça marcada IS_MANUAL_PART
    Quando o gabinete é recalculado
    Então a peça não é reescrita

  Cenário: Móvel fora do registro de classes
    Dado uma cômoda (classe ausente de WRAP_CLASS_REGISTRY) com rodapé
    Quando o usuário altera a largura
    Então o rodapé é zerado (bug legado RN-38; RF-23 deve corrigir)
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Criação, distribuição, carcaça/moldura, rails, árvore de aberturas, frentes — RF-01..RF-07 | Must | Núcleo do solver; todo gabinete passa por aqui |
| Exposição, estilos, inserção, móveis no recálculo — RF-09, RF-11, RF-12, RF-23 | Must | Aplicados em toda criação/edição |
| Casos de rail, painéis aplicados, quebrar/juntar, edição direta, comandos por peça, cantos, especiais, tampo — RF-08, RF-10, RF-13..RF-18 | Should | Importantes, com alternativa |
| Painéis de eletro, cunha, moldura angular, abrir frentes, biblioteca — RF-19..RF-22 | Could | Uso ocasional |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências. A permanência desta unit no
> produto depende da decisão de mercado (ver [`questions.md`](questions.md), Q-01).

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `types_face_frame.py` | `FaceFrameCabinet` (`create_cabinet_root`, `create_carcass`, `recalculate`), classes do catálogo, merge/break, produtos | 🟢 |
| `types_face_frame_corner.py` | gabinetes de canto e recálculo próprio | 🟢 / 🔴 detalhes |
| `solver_face_frame.py` | snapshot, segmentos, stiles, `_walk_tree`, `front_leaves`, itens internos | 🟢 |
| `props_hb_face_frame.py` | PropertyGroups, callbacks, estilos, registro | 🟢 |
| `bay_presets.py`, `applied_panel_sizing.py`, `exposure.py` | presets, painéis aplicados, exposição | 🟢 |
| `style_options.py` | catálogo CWP | 🟢 |
| `wood_materials.py`, `finish_colors.py`, `pulls.py` | materiais, cores, puxadores | 🟢 |
| `split_preview.py`, `dim_edit_overlay.py`, `ui_face_frame.py`, `menus_face_frame.py`, `thumbnail_render.py` | UI e GPU | 🟢 |
| `operators/*.py` (13 módulos) | inserção, cabinet, modify, part commands, estilos, tampos, painéis de eletro, cunha, acabamentos, abrir, biblioteca, padrões, miniaturas | 🟢 |
