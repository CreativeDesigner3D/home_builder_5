# closets — Requisitos

> Unit legada (fork do Home Builder 5). Gerado pelo **Writer** (Reversa) em 2026-10-01, nível **detalhado**.
> Fontes: [`code-analysis-legacy.md#módulo-closets`](../code-analysis-legacy.md), [`data-dictionary-legacy.md#closets`](../data-dictionary-legacy.md),
> [`legacy-mapping.md`](legacy-mapping.md), `flowcharts/legacy-closets-*.md`.
> Escala: 🟢 CONFIRMADO · 🟡 INFERIDO · 🔴 LACUNA. Caminhos relativos a `blendertomob/product_libraries/closets/`.

## Visão Geral

O `closets` é a biblioteca de **closets e roupeiros modulares** no sistema 32 mm. Um *starter* é uma corrida de vãos
entre painéis verticais compartilhados. Cada vão tem prateleiras de base e topo, rodapé, cleat, trilho de parede e
aberturas que recebem inserções: prateleiras reguláveis e fixas, varões com cabides, portas, gaveteiros com caixas de
sistema (Avantech, Metabox, madeira) e nichos. Há também cantos em L e ilhas simples e dupla face. 🟢
Como o face_frame, **não usa drivers**: `ClosetStarter.recalculate()` lê as propriedades, chama o solver puro e escreve
os inputs de Geometry Nodes de cada peça. 🟢 São 17 arquivos, ~9 750 linhas. 🟢
Mistura polegadas (espessuras, folgas) com milímetros (alturas do sistema 32 mm, caixas de gaveta). 🟢

## Responsabilidades

- Criar starters (BASE, TALL, HANGING, ISLAND, ilha dupla, L-shelf) a partir de um catálogo declarativo. 🟢
- Resolver larguras de vãos e painéis compartilhados com travas (solver puro). 🟢
- Montar cada vão: prateleiras de base/topo, rodapé, cleat, trilho, fundo aplicado, prateleiras divisoras e segmentos. 🟢
- Gerar inserções nas aberturas: reguláveis, fixas, varões e cabides, portas, gavetas com caixa de sistema, nichos. 🟢
- Aplicar presets de vão (double hang, portas sobre gavetas, etc.). 🟢
- Inserir starters por modal na parede ou livre (ilhas), com auto nº de vãos e tratamento de canto. 🟢
- Editar por diálogos, rótulos GPU editáveis e arraste de fronteiras com snap 32 mm. 🟢
- Aplicar opções de sala (materiais, frentes, puxadores, varões, cabides, caixa de gaveta) a todos os starters. 🟢
- Gerar moldura de coroa, abrir portas/gavetas com animação e duplicar starters (inclusive espelhado). 🟢

## Regras de Negócio

Todas as regras vêm de `code-analysis-legacy.md` (IDs `CLOSETS-Rnn`). `pt` = espessura do painel, `st` = da prateleira.

**Layout do starter**
- RN-01 (R01/R02): N vãos ⇒ N+1 painéis compartilhados; largura interna `W − (N+1)·pt`; vãos destravados dividem igualmente o restante dos travados. 🟢
- RN-02 (R03/R04): vão destravado mínimo 1" no solver (se violado, a soma não fecha); todos travados ⇒ escala proporcional. 🟢
- RN-03 (R05): editar a largura de um vão trava esse vão; escritas do sistema não travam. 🟢
- RN-04 (R06): painel entre dois vãos vai do menor fundo ao maior topo dos vizinhos; profundidade = a maior. 🟢
- RN-05 (R07/R08): vão de piso começa no piso; vão suspenso ancora no topo (`z0 = H − h`); altura interna `h − kick − 2·st` (mín. 0,25"). 🟢
- RN-06 (R12/R13): mudar altura/profundidade do starter só propaga aos vãos que estavam no valor anterior; starter HANGING cresce para baixo. 🟢
- RN-07 (R17): nº automático de vãos = `clamp(ceil(W/42"), 1, 9)`. 🟢

**Sistema 32 mm**
- RN-08 (R14): alturas de painel `19 + n·32 mm` (Base 819, Hanging 1267, Tall 2131 mm). 🟢
- RN-09 (R15): prateleiras e varões adicionados encaixam em furos `12,95 + n·32 mm` medidos do fundo interno do vão. 🟢
- RN-10 (R16): arraste com snap COARSE (retícula 32 mm em alturas, 1/4" em larguras), FINE 1/8", livre com Shift; TAB alterna. 🟢
- RN-11: não há furação gerada — o 32 mm é só retícula de snap. 🔴

**Peças do vão**
- RN-12 (R09): cleat de 4" acompanha a prateleira inferior; sem ela, desce à base do envelope; oculto em ilha dupla. 🟢
- RN-13 (R10): rodapé recuado 1,625"; oculto se vão suspenso, sem prateleira inferior ou kick ≤ 0; ilha dupla tem rodapé traseiro. 🟢
- RN-14 (R11): trilho de parede 1,125 × 0,25", 3,3125" abaixo do topo do vão; sob demanda; ilhas não têm. 🟢
- RN-15 (A2): prateleiras fixas divisoras vivem no vão e dividem o interior em segmentos; uma abertura por segmento e lado. 🟢

**Frentes e gavetas**
- RN-16 (R22/R23): meia sobreposição `(esp − 1/8")/2`; frente 1/8" à frente da carcaça; folga entre frentes 1/8"; porta dupla `(w + lo + ro − gap)/2`, dobradiças para fora. 🟢
- RN-17 (R24): porta do vão inteiro suprime as portas das aberturas do lado FRONT; BACK não suportado. 🟢
- RN-18 (R25/R26): pilha de gavetas preenche a abertura (iguais, mín. 2"); editar uma frente a trava; todas travadas ⇒ escala; gaveteiro tampado por prateleira fixa. 🟢
- RN-19 (R27): caixa WOOD = frente − 1,25" de altura, profundidade − 0,5", vão − 2·1/2" de largura, mín. 2". 🟢
- RN-20 (R28): Metabox N54/M86/K118/H150 exigem abertura 78/110/142/174 mm; Avantech 101/139/187/251 mm exigem altura + 5 mm; corrediças 270–550 mm (a maior que cabe); Illumination reserva 12,7 mm; nada cabe ⇒ menor. 🟢
- RN-21 (R29): curso da gaveta `min(prof. da caixa, 12")`; porta abre 110°. 🟢
- RN-22 (R39): estilos de frente 5 peças por estilo (montante/travessa 2,25–3"); frente pequena ⇒ slab. 🟢
- RN-23 (R40/R41): veio — portas vertical, gavetas horizontal, montantes vertical; painel de porta pode ser vidro (gavetas não). 🟢
- RN-24 (R42): puxador de porta a 45" do piso; acima disso convenção Upper (1,5" da base); se passar do topo, Base (1,5" do topo); 2" da borda. 🟢

**Varões, prateleiras, nichos**
- RN-25 (R30/R31): varão de raio 1", eixo a 12" da parede, 2,5" abaixo do topo; 3 cabides por varão (> 14"), modelos que cabem na folga. 🟢
- RN-26 (R32/R33): reguláveis espaçadas `ih·(i+1)/(n+1)`, ~1 a cada 12"; portas semeiam reguláveis só em abertura vazia; basculantes não. 🟢
- RN-27 (R34): nichos com `cols−1` divisões e `rows−1` prateleiras iguais. 🟢
- RN-28 (R35): presets de vão (Double Hang, DH Top/Mid Shelf, Doors over N drawers, Doors Open N drawers, Base/Upper/Full Height Doors). 🟢

**Inserção, canto e ilha**
- RN-29 (R18): recuo de 1/2" em cantos internos; offset digitado substitui o recuo do seu lado. 🟢
- RN-30 (R19): ilha com detentes de corredor 30/36/42/48" (janela 1"), busca 240"; Shift desativa. 🟢
- RN-31 (R20/R21): vizinho de canto a 90° ± 5°, alturas sobrepostas, canto ≤ 8", borda ≤ 1"; folga de canto (12") encolhe o starter até mín. 6", com pontes e rodapé no vão real. 🟢
- RN-32 (R45/R46): ilha dupla 30" com fundo central; L-shelf 24×24" com 3 prateleiras em L, entalhe `CPM_CORNERNOTCH`. 🟢

**Edição e estrutura**
- RN-33 (R36/R37): excluir o único vão exclui o starter; inserir vão copia o âncora e entra com largura 0 destravada. 🟢
- RN-34 (R38): remover peça dirigida por config decrementa o idprop em vez de apagar o objeto. 🟢
- RN-35 (R47/R48): arrastar o fundo de um vão a ≤ 1" do piso o torna de piso; prateleira arrastada mantém 1" das vizinhas; limites mínimos. 🟢
- RN-36 (R49/R50): duplicar espelhado inverte vãos e troca LEFT↔RIGHT; rótulo de segmento tampado move a tampa. 🟢

**Acabamentos**
- RN-37 (R43): moldura só em vãos com topo ≥ 60"; retornos e degraus; não regenera sozinha. 🟢
- RN-38 (R44): tampo em Base/Ilha (1,125"); balanço frontal 1,875"; ilha dupla 1,5" em todos os lados. 🟢

**Comportamentos desconhecidos**
- 🔴 Sem furação (linha 32 mm, minifix, cavilhas) e sem integração com lista de corte/orçamento.
- 🔴 Frentes do lado BACK da ilha dupla sem puxador e sem portas de vão.
- 🔴 Interfaces de `GeoNodeClosetRod` não analisadas na escavação (agora em [`hb_core/node-group-interfaces.md`](../hb_core/node-group-interfaces.md)).
- 🟡 `DOORS_OPEN_*` não abre portas, apesar do comentário; `_cfg_hamper` sem uso; `spec.kick_setback` sem uso.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Criar starter com N+1 painéis e N vãos iguais | Must | 80" com 4 vãos e painel 3/4" → vãos de (80 − 3,75)/4 = 19,06" |
| RF-02 | Solver de larguras com travas e escala | Must | RN-01..RN-03 |
| RF-03 | Recálculo completo sem drivers, com guardas de reentrância | Must | Editar a altura do starter atualiza vãos não sobrescritos |
| RF-04 | Peças do vão (prateleiras, rodapé, cleat, trilho, fundo) | Must | RN-12..RN-14 |
| RF-05 | Prateleiras divisoras e segmentos | Must | 1 prateleira fixa no meio → 2 aberturas |
| RF-06 | Retícula 32 mm em alturas e furos | Must | Painel Tall = 2131 mm; prateleira encaixa em 12,95 + n·32 mm |
| RF-07 | Portas simples/dupla/basculante e porta do vão | Must | RN-16, RN-17 |
| RF-08 | Gavetas com caixa de sistema (Metabox/Avantech/madeira) | Must | Abertura de 115 mm com Metabox → altura M86 |
| RF-09 | Varões e cabides | Should | Varão de 30" com 3 cabides |
| RF-10 | Reguláveis, nichos e presets de vão | Should | Preset "Doors over 4 drawers" cria 4 gavetas e portas |
| RF-11 | Inserção modal na parede com auto nº de vãos e recuo de canto | Must | 120" livres → 3 vãos |
| RF-12 | Inserção de ilha com detentes de corredor | Should | Corredor encaixa em 36" ± 1" |
| RF-13 | Detecção de vizinho de canto e folga de canto | Should | RN-31 |
| RF-14 | Ilha dupla e L-shelf | Should | RN-32 |
| RF-15 | Edição por rótulos GPU e arraste com snap 32 mm | Should | RN-10, RN-35 |
| RF-16 | Inserir/excluir vão e remover peças por config | Should | RN-33, RN-34 |
| RF-17 | Opções de sala aplicadas a todos os starters | Should | Trocar o material da sala recalcula todos |
| RF-18 | Estilos de frente, veio e vidro | Should | RN-22, RN-23 |
| RF-19 | Moldura de coroa e tampo | Could | RN-37, RN-38 |
| RF-20 | Abrir portas/gavetas com animação | Could | 0,35 s, sem recálculo |
| RF-21 | Duplicar starter (inclusive espelhado) | Could | RN-36 |
| RF-22 | Furação 32 mm (linha de furos, minifix) | Won't (legado) | Não existe no legado; ver Q-02 |
| RF-23 | Frentes do lado BACK da ilha dupla | Won't (legado) | Pendente no legado |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Testabilidade | Solver de layout puro, sem `bpy` | `solver_closets.py:26-126` | 🟢 |
| Consistência | Guardas `_RECALCULATING` / `_DISTRIBUTING_WIDTHS` | `types_closets.py:105-106` | 🟢 |
| Recursos | Draw handlers POST_PIXEL permanentes (grab e overlay) removidos no `unregister` | `op_grab_closet.py:892-898`; `gpu_overlay_closets.py:994-1001` | 🟢 |
| Robustez | Erros silenciosos (`except Exception: pass`) em estilos, materiais, draw e registro | `types_closets.py:113-117`; `ops_closet.py:41-51`, `:2881-2892` | 🟢 |
| Undo | `open_door_mode` e `toggle_mode` alteram dados sem `UNDO` | `op_open_door_closet.py:82`; `ops_closet.py:294-354` | 🟢 |
| Compatibilidade | `Material.use_nodes` obsoleto; linhas grossas com `UNIFORM_COLOR` | `materials_closets.py:121`; `op_grab_closet.py:273-301` | 🟢 |
| Persistência | Cabides do usuário em `extension_path_user` (pacote montado à mão) | `pulls_closets.py:61-72` | 🟡 |

> Inferido a partir do código. Validar com a equipe.

## Critérios de Aceitação

```gherkin
Funcionalidade: Solver do starter

  Cenário: Vãos iguais
    Dado um starter de 80" com 4 vãos e painéis de 3/4"
    Quando compute_layout roda
    Então cada vão tem (80 − 5·0,75)/4 = 19,0625"

  Cenário: Um vão travado
    Dado o vão 2 travado em 24"
    Então os outros 3 dividem igualmente (76,25 − 24)/3

  Cenário: Todos travados
    Dado todos os vãos travados somando 70" para 76,25" internos
    Então todos são escalados proporcionalmente para fechar 76,25"

  Cenário: Vão destravado abaixo do mínimo
    Dado travados que deixam menos de 1" para o vão livre
    Então o solver usa 1" e a soma não fecha (comportamento legado)

Funcionalidade: Sistema 32 mm

  Cenário: Altura de painel
    Quando um starter TALL é criado
    Então os painéis têm 19 + 66·32 = 2131 mm

  Cenário: Prateleira adicionada
    Quando o usuário adiciona uma prateleira a 400 mm do fundo interno
    Então ela encaixa no furo mais próximo de 12,95 + n·32 mm

Funcionalidade: Gavetas

  Cenário: Metabox
    Dado uma abertura de gaveta de 115 mm e sistema Metabox
    Então a caixa escolhida é M86 (exige 110 mm)

  Cenário: Nada cabe
    Dado uma abertura de 60 mm
    Então a menor caixa do sistema é usada (comportamento legado)

Funcionalidade: Inserção

  Cenário: Auto nº de vãos
    Quando um starter de 120" é inserido
    Então nasce com ceil(120/42) = 3 vãos

  Cenário: Canto interno
    Dado o starter encostado num canto interno
    Então há recuo automático de 1/2" desse lado

Funcionalidade: Edição

  Cenário: Excluir o único vão
    Dado um starter com 1 vão
    Quando o vão é excluído
    Então o starter inteiro é excluído

  Cenário: Arraste para o piso
    Dado um vão suspenso
    Quando o usuário arrasta o fundo para 0,5" do piso
    Então o vão passa a ser de piso
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Starter, solver, recálculo, peças do vão, segmentos, 32 mm, portas, gavetas, inserção — RF-01..RF-08, RF-11 | Must | Núcleo do roupeiro, mais próximo da marcenaria brasileira |
| Varões, presets, ilhas, canto, L-shelf, edição direta, estrutura, opções de sala, estilos — RF-09, RF-10, RF-12..RF-18 | Should | Importantes, com alternativa |
| Moldura, tampo, animação, duplicar — RF-19..RF-21 | Could | Uso ocasional |
| Furação, frentes BACK — RF-22, RF-23 | Won't (legado) | Ausentes; a furação é decisão de produto (Q-02) |

> Prioridade inferida por frequência de chamada e posição na cadeia de dependências.

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `types_closets.py` | `ClosetStarter` (`create_starter`, `recalculate`, regeneradores), Island, IslandDouble, LShelf, presets | 🟢 |
| `solver_closets.py` | `compute_layout` | 🟢 |
| `props_closets.py` | `Closet_Starter_Props`, `Closet_Bay_Props`, `Closets_Scene_Props` | 🟢 |
| `const_closets.py`, `starter_presets.py` | constantes, sistema 32 mm, catálogo | 🟢 |
| `drawer_boxes_closets.py`, `fronts_closets.py`, `materials_closets.py`, `pulls_closets.py`, `molding_closets.py` | sistemas e opções de sala | 🟢 |
| `gpu_overlay_closets.py`, `menus_closets.py` | rótulos editáveis e menus | 🟢 |
| `operators/ops_closet.py`, `op_grab_closet.py`, `op_open_door_closet.py` | inserção, comandos, arraste, abrir | 🟢 |
