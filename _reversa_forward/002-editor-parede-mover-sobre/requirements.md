# Requirements: Editor de parede 2D, editor de geometria, propriedades por tipo de objeto e "Mover Sobre"

> Identificador: `002-editor-parede-mover-sobre`
> Data: `2026-10-04`
> Pasta da extração reversa: `_reversa_sdd/`
> Feature anterior relacionada: `_reversa_forward/001-addon-moveis-planejados/` (concluída)
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Projetistas de móveis planejados precisam posicionar módulos com precisão e conferir cada parede como numa planta técnica.
Esta feature entrega quatro ferramentas inspiradas no fluxo de trabalho do Promob (referência de comportamento, ver §2):
1. Um **editor de paredes 2D**: uma planta vista de cima onde o usuário desenha as paredes como com um lápis e edita cada trecho (comprimento, ângulos, espessura, pé-direito). Clicar na linha interna mostra a medida interna; clicar na externa, a medida externa. Tudo é aplicado ao 3D de uma vez, ao confirmar.
2. Um **editor de geometria** para placas e caixas livres.
3. Uma **janela de propriedades** que muda conforme o tipo do objeto selecionado.
4. O modo **"Mover Sobre"**: arrastar um objeto sobre outro com o botão direito abre uma janela com as vistas superior e frontal dos dois, e um clique alinha um ao outro pelos lados, pela profundidade ou pela altura.

Hoje nada disso existe de forma utilizável:
- as paredes só podem ser desenhadas no próprio 3D, e as vistas de parede são cenas de prancha renderizadas à parte;
- o painel de propriedades ignora os gabinetes das bibliotecas principais;
- não há movimento relativo entre objetos.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/wall_editor/requirements.md` | O "Editor de Parede" do legado é desenho interativo de paredes (encaixe, comprimento digitado, trava de 45°) e um painel de propriedades da parede (comprimento, altura, espessura, afastamento, ângulos, orientação, tipo Normal/Drywall). Não há visualizador 2D. O grupo `HB_Wall_Editor_Props` (`hb_props.py:824`) está registrado e nunca é usado. | 🟡 (spec sem marcação de confidência; inconsistência spec × código) |
| Código de paredes (levantamento de 2026-10-04) | Paredes são desenhadas no 3D (`home_builder_walls.draw_walls`, `btm.wall_builder`) e editadas por diálogo (`home_builder_walls.wall_prompts`: comprimento, altura, altura final, espessura, com recálculo dos encontros). Já existem excluir parede, ocultar/isolar, ajustar piso e construir teto (`operators/walls.py`, `floor_builder.py`). Não há planta 2D editável. | 🟢 |
| `_reversa_sdd/hb_layouts/requirements.md#RF-05, RN-22` | As vistas de planta e elevação existentes são cenas de prancha renderizadas à parte, sem edição. | 🟢 |
| Vídeos "Promob — construção de paredes" (resumo fornecido pelo usuário, 2026-10-05) | Editor de Paredes em janela própria: planta 2D com linhas interna e externa, seta de sentido, vértices arrastáveis, ferramentas (selecionar/mover, construir parede, inverter sentido, adicionar e remover vértice, pan, zoom), painel do trecho (comprimento, ângulo absoluto, relativo e do arco, bloquear ângulo, espessura, pé-direito inicial e final, orientação, tipo), grade (tamanho, linhas magnéticas), OK/Cancelar. Também: remover parede (segmento/tudo/manter o selecionado), rebaixar parede, objeto invisível. | 🟡 (descrição de terceiros) |
| `_reversa_sdd/ui/requirements.md#R-02` | O painel de contexto adapta-se ao tipo do objeto ativo (parede, módulo, abertura), mas só para objetos da camada nova (`btm_plane`). | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md#RN-09..RN-14` | Vão na parede, obstáculos, filtro vertical e gabinetes livres: base para as cotas anterior e posterior e para a colisão. | 🟢 |
| `_reversa_sdd/domain.md#R-04..R-08` | Portas e janelas presas ao segmento de parede, movimento restrito ao plano da parede, limites e peitoril. | 🟢 |
| `_reversa_forward/001-addon-moveis-planejados/requirements.md` RF-040..RF-044, RF-046, RF-070, RF-071, RF-074, RN-13 | Já especificados na 001 e **não implementados**: painel de propriedades e edição imediata; cotas relativas editáveis (exemplo: cota anterior de 75 mm deixa o módulo a 75 mm do vizinho); "Evitar Sobreposição"; geometria por pontos de referência; geometria livre na lista de peças. Esta feature assume esses requisitos; o editor de perfil (001 RF-072/RF-073) fica fora (esclarecimento de 2026-10-05). | 🟢 |
| Código (levantamento de 2026-10-04) | Os objetos vêm de dois modelos: bibliotecas do Home Builder 5, marcadas por propriedades `IS_*` e `MENU_ID`, e camada nova (`btm_plane.object_kind`). Não existe classificador único de tipo; a melhor referência de precedência é a exclusão em `operators/ops_general.py:121-210`. O menu do botão direito vem de `MENU_ID` acrescentado ao menu de contexto do Blender. A matemática de encostar ao lado existe em `hb_placement.py:520-582`. Não há janela capaz de desenhar 2D próprio. | 🟢 |
| Vídeo "Curso Promob — movimentação básica" (resumo fornecido pelo usuário) | Inspetor de propriedades com Dimensões, Cotas (afastamento da parede, anterior, posterior, inferior, superior) e Outras; cotas desenhadas ao selecionar; arraste restrito ao plano da parede com linhas-guia e cotas ao vivo; barra de status com o item selecionado; botões Colisão, Junções e Auto Rebaixar. | 🟡 (descrição de terceiros) |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de móveis planejados (uso diário) | Montar uma cozinha com módulos alinhados entre si e às paredes | Arrasta o aéreo sobre o balcão com o botão direito, clica perto da "profundidade 0" na vista superior e o aéreo fica com a frente alinhada à do balcão |
| Projetista levantando o ambiente (uma vez por projeto, com ajustes) | Desenhar a planta do cômodo com as medidas da obra e conferir medidas internas e externas | Abre o editor de paredes, desenha os quatro trechos digitando 3.900 e 2.700 (medidas externas), clica na linha interna e confere 3.600 × 2.400 com paredes de 150 mm |
| Projetista de interiores (semanal) | Criar um painel, uma prateleira avulsa ou uma caixa que não existe na biblioteca | Usa o editor de geometria, desenha a placa pelos pontos da parede e marca como peça de fabricação |
| Qualquer usuário (sempre) | Saber o que pode ser feito com o objeto selecionado | Clica numa gaveta e a janela de propriedades mostra "Abrir/Fechar", as medidas da frente e o módulo a que pertence |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 — Tipo do objeto selecionado.** O tipo vem do próprio objeto ou do primeiro ancestral reconhecido, nesta ordem de precedência:
   1. cota/anotação;
   2. frente de módulo (porta, gaveta, basculante, pullout);
   3. peça interna de módulo;
   4. módulo (frameless, face frame, closets, módulo rápido);
   5. porta ou janela de ambiente;
   6. geometria livre;
   7. obstáculo;
   8. parede;
   9. piso/teto.

   Vale para as duas famílias de objetos (bibliotecas do Home Builder 5 e camada nova). 🟢
   - Origem no legado: `_reversa_sdd/ui/requirements.md#R-02`; precedência de `operators/ops_general.py:121-210` (frente e módulo antes de parede).
   - Tipo: alterada (passa a cobrir todas as bibliotecas).
2. **RN-02 — Janela de propriedades.** Ela mostra sempre o objeto **ativo**. Com mais de um objeto selecionado, informa quantos são e edita só o ativo. Sem seleção, mostra "Nenhum objeto selecionado" e as opções gerais do ambiente. 🟡
   - Tipo: nova.
3. **RN-03 — Edição imediata.** Um campo editado na janela de propriedades altera o 3D na hora, como um único passo de desfazer. Um valor fora do domínio é recusado com "Valor Inválido", com campo, valor, unidade e faixa, e o objeto não muda. 🟢
   - Origem no legado: `_reversa_forward/001-addon-moveis-planejados/requirements.md` RF-041, RF-042.
   - Tipo: nova.
4. **RN-04 — Cotas de um módulo**, medidas no plano da parede em que ele está, na unidade do usuário:
   - **afastamento da parede:** da face de trás do módulo à face da parede;
   - **cota anterior:** da lateral esquerda ao obstáculo mais próximo à esquerda (módulo vizinho, abertura ou fim da parede);
   - **cota posterior:** a mesma medida, à direita;
   - **cota inferior:** do piso à base do módulo;
   - **cota superior:** do topo do módulo ao teto.

   Editar uma cota move o módulo e preserva as dimensões dele. 🟢
   - Origem no legado: 001 RF-044; vão e obstáculos de `_reversa_sdd/hb_placement/requirements.md#RN-09`.
   - Tipo: nova.
5. **RN-05 — Papéis no "Mover Sobre".**
   - O objeto **arrastado (A)** é o que se move.
   - O objeto **de destino (B)**, aquele sobre o qual o botão direito foi solto, vira o objeto ativo e é a referência. B não se move.
   - Uma peça (frente, puxador, peça interna) conta como o módulo a que pertence, tanto para A quanto para B.
   - B pode ser uma parede; A não. 🟢 (pedido do usuário)
   - Tipo: nova.
6. **RN-06 — Alvos de alinhamento na vista superior.** Um clique perto de um alvo, a até 12 px na tela, alinha A a B:
   - **lado direito ou esquerdo de B:** A fica encostado nesse lado, sem folga nem sobreposição;
   - **linhas de profundidade de B a 0%, 30%, 50%, 75% e 100%**, contadas da face frontal (0%) à face de trás (100%): a face frontal de A passa para essa linha.

   Perto de um lado **e** de uma linha de profundidade ao mesmo tempo, as duas coisas se aplicam. Fora de qualquer alvo, o clique não faz nada. 🟢 (pedido do usuário; tolerância de 12 px 🟡)
   - Tipo: nova.
7. **RN-07 — Alvos de alinhamento na vista frontal:**
   - **lados direito e esquerdo de B:** como na vista superior;
   - **linhas de altura de B a 0%, 30%, 50%, 75% e 100%**, contadas da base (0%) ao topo (100%): a base de A passa para a linha clicada;
   - **acima do topo de B:** A fica empilhado sobre B (base de A no topo de B). 🟢 (esclarecimento de 2026-10-05)
   - Tipo: nova.
8. **RN-08 — Referencial do alinhamento.** Lados, profundidade e altura são medidos no referencial de B (paralelo à parede de B ou à orientação de B). Se a rotação de A no plano for diferente da de B, A passa a ter a rotação de B antes de alinhar. 🟡
   - Tipo: nova.
9. **RN-09 — Confirmar e cancelar o "Mover Sobre".**
   - Cada alinhamento na janela 2D é mostrado em prévia, nas vistas e no 3D.
   - **Confirmar** grava a posição como um único passo de desfazer.
   - **Cancelar** ou Esc devolve A à posição original. 🟢
   - Tipo: nova.
10. **RN-10 — Botão direito no modo "Mover Sobre".**
    - Com o modo ligado, pressionar o botão direito sobre um objeto e arrastar inicia o "Mover Sobre", e um clique simples no botão direito não abre menu.
    - Soltar sobre o vazio, sobre A ou sobre um objeto que não pode ser referência cancela, sem mudar nada.
    - Com o modo desligado, o botão direito volta a abrir o menu de contexto normal. 🟢 (pedido do usuário)
    - Tipo: nova.
11. **RN-11 — Sobreposição no "Mover Sobre".** O usuário pode confirmar uma posição em que A se sobrepõe a outro módulo, porque o posicionamento é explícito. Com "Evitar Sobreposição" ligado, a janela avisa antes de confirmar e lista os objetos sobrepostos. 🟡
    - Origem no legado: 001 RN-13 (`btm_settings.collision_global`).
    - Tipo: alterada (exceção explícita à regra de evitar sobreposição).
12. **RN-12 — Paredes ligadas.** Ao confirmar o editor de paredes, os encontros (esquadrias) entre trechos ligados são recalculados e as paredes 3D são refeitas. Os filhos (módulos, portas, janelas) mantêm a posição relativa ao início da parede. 🟢
    - Origem no legado: comportamento de `home_builder_walls.wall_prompts` (`operators/walls.py:2354`).
    - Tipo: nova (mesma regra, nova tela).
13. **RN-13 — Itens presos à parede.** O editor de paredes desenha e edita **só paredes**: portas, janelas e módulos não são editados nele. Se uma parede ficar mais curta que o necessário para um item preso a ela, o editor avisa antes de confirmar e lista os itens; as regras de limite das aberturas continuam valendo. Se um trecho com módulos for apagado no editor, o OK pergunta se os módulos devem ser removidos junto; por padrão eles ficam soltos no mesmo lugar (esclarecimento de 2026-10-05). 🟡
    - Origem no legado: `_reversa_sdd/domain.md#R-05`, `#R-06`, `#R-08`.
    - Tipo: nova (esclarecimento de 2026-10-05: só parede no editor).
14. **RN-14 — Geometria livre como peça.** Uma geometria livre marcada como "peça de fabricação" entra na lista de peças com componente, matéria-prima, espessura e acabamento. Sem a marca, ela é só visual e fica fora do orçamento. 🟡
    - Origem no legado: 001 RF-074.
    - Tipo: nova.
15. **RN-15 — Linha interna e linha externa.** Cada parede da planta tem duas linhas: a **interna** (face voltada para dentro do ambiente) e a **externa**. Selecionar a linha interna mostra e edita a medida interna do trecho; a externa, a medida externa. Num cômodo retangular, medida interna = medida externa − espessuras das duas paredes que chegam nas pontas (ex.: externa 2.700 mm com paredes de 150 mm → interna 2.400 mm). 🟢 (esclarecimento de 2026-10-05)
    - **A medida real é a interna** (espaço útil): comprimentos digitados valem para a face interna; a externa é sempre a interna + as espessuras. A linha interna é desenhada **tracejada** e a externa **contínua** (esclarecimento de 2026-10-05, 2ª sessão).
    - **Direção (Direita/Esquerda):** propriedade do editor que diz para que lado da linha desenhada a parede cresce. A linha desenhada é a face interna; a espessura vai para o lado oposto ao interior. Mudar a Direção troca o lado (inverte o sentido) sem mudar as medidas internas. O interior do ambiente — onde ficam a frente dos módulos e o lado "para dentro" das portas — é sempre o lado da face interna, qualquer que seja o sentido em que a sala foi desenhada.
    - Tipo: nova.
16. **RN-16 — Edição em rascunho.** O editor de paredes trabalha sobre uma cópia das paredes do ambiente. Nada muda no 3D até **OK**; **Cancelar** ou Esc descarta tudo. OK aplica todas as mudanças como um único passo de desfazer. 🟢
    - Tipo: nova.
17. **RN-17 — Desenho a lápis.** Com a ferramenta de construir parede:
    - o primeiro clique marca o ponto inicial;
    - digitar números vai direto para o comprimento (medida interna, em mm), sem clicar em campo;
    - Enter confirma o trecho e começa o próximo a partir do ponto final;
    - perto de 0°, 90°, 180° ou 270° (até 2,5°) o trecho trava na direção e a linha fica sólida;
    - clicar de volta no ponto inicial pergunta "Deseja fechar a parede e finalizar a sua construção?"; Sim fecha o contorno. 🟢
    - **ímã no ponto inicial:** com 2 ou mais trechos, o cursor a até 15 px (na tela) do ponto inicial gruda nele, que fica destacado; clicar ali faz a mesma pergunta;
    - chegar ao ponto inicial **pelo teclado** (medida digitada) ou **arrastando um vértice** (até 10 mm) também faz a pergunta; Sim fecha, Não mantém aberto;
    - nenhuma sala é aplicada com a última parede solta: no OK, um contorno aberto cujo fim coincide com o início (até 10 mm) é fechado (esclarecimento de 2026-10-05, 3ª sessão).
    - Tipo: nova.
18. **RN-18 — Domínio dos campos do trecho** (unidade do usuário, valores em mm):
    - comprimento > 0;
    - ângulo absoluto de 0° a 360°, medido no sentido anti-horário a partir do eixo X;
    - ângulo relativo de −180° a 180°, em relação ao trecho anterior;
    - ângulo do arco de −180° a 180° (0 = reto);
    - espessura de 10 a 2.000 mm (padrão 150);
    - pé-direito inicial e final de 500 a 10.000 mm (padrão: o pé-direito do projeto, definido nas Configurações; Mureta 1.100; o final acompanha o inicial salvo quando editado);
    - orientação Direita, Esquerda ou Centro (padrão Direita);
    - tipo Normal, Divisória ou Mureta (padrão Normal).

    Valor fora da faixa é recusado com "Valor Inválido". Mudar o comprimento estende o trecho no sentido da seta. 🟡 (faixas da referência de terceiros)
    - Tipo: nova.

## 5. Requisitos Funcionais

### 5.1 Editor de paredes 2D (planta)

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Abrir o Editor de Paredes em janela própria: pelo menu do botão direito de uma parede ("Editar Paredes…"), pelo construtor de paredes ou por um botão no painel. Abre com as paredes do ambiente atual; sem paredes, abre vazio e pronto para desenhar | Must | Com a sala de 4 paredes, o editor mostra os 4 trechos; num ambiente vazio, mostra só a grade | 🟢 |
| RF-02 | Planta 2D de cima: cada parede com linha interna (tracejada) e externa (contínua) (espessura), seta de sentido no trecho ativo, vértices como alças quadradas e grade de fundo; paredes da camada nova (`btm.wall_builder`) aparecem como contorno tracejado, só para referência; navegação com pan, zoom mais/menos, zoom janela e enquadrar tudo | Must | O contorno de uma sala de 3.900 × 2.700 mm aparece em escala, com as duas linhas por parede | 🟢 |
| RF-03 | Ferramenta "Construir Parede" (lápis) dentro do editor, com digitação direta do comprimento, Enter para o próximo trecho, trava ortogonal e pergunta de fechamento (RN-17) | Must | Desenhar 3.900, 2.700, 3.900 e clicar no ponto inicial pergunta se deve fechar; Sim fecha o contorno | 🟢 |
| RF-04 | Selecionar a linha interna ou a externa de um trecho para ver e editar a medida interna ou a externa (RN-15) | Must | Na sala com paredes de 150 mm, a linha externa mostra 2.700 e a interna 2.400 | 🟢 |
| RF-05 | Painel "Painel" do trecho selecionado: comprimento, ângulo absoluto, ângulo relativo, ângulo do arco, bloquear ângulo, espessura, pé-direito inicial, pé-direito final, **Direção (Direita/Esquerda)** e tipo de parede (RN-15, RN-18) | Must | Mudar o comprimento de 3.900 para 4.100 estende o trecho no sentido da seta e atualiza a planta | 🟢 |
| RF-06 | Ferramenta "Selecionar/Mover": arrastar vértices com prévia tracejada, trava ortogonal com linha sólida e painel atualizado em tempo real; com "Bloquear Ângulo" ligado, o arraste mantém a inclinação do trecho | Must | Arrastar um vértice altera comprimento e ângulos no painel enquanto arrasta | 🟢 |
| RF-07 | Ferramentas "Inverter Sentido da Parede", "Adicionar Vértice" (divide o trecho no ponto clicado) e "Remover Vértice" (une dois trechos) | Should | Adicionar um vértice no meio de 3.900 cria dois trechos que somam 3.900 | 🟢 |
| RF-08 | Painel "Grid": tamanho da grade (padrão 1.000 mm, de 10 a 5.000) e "Linhas Magnéticas" (encaixe dos vértices nos cruzamentos da grade) | Should | Com linhas magnéticas, um vértice solto a 30 mm de um cruzamento vai para o cruzamento | 🟡 |
| RF-09 | OK aplica tudo de uma vez (encontros, paredes 3D, piso e teto ligados) com indicação de processamento; Cancelar ou Esc descarta, pedindo confirmação quando houver alterações; OK e Cancelar ficam no fim do painel lateral (RN-16, RN-12) | Must | Cancelar depois de mudar 3 trechos deixa o 3D igual ao de antes; OK gera um passo de desfazer | 🟢 |
| RF-10 | Aviso antes do OK quando uma parede ficar curta demais para os itens presos a ela; e, para trechos apagados com módulos, pergunta "Remover os módulos junto?" (padrão: não, os módulos ficam soltos no lugar) (RN-13) | Should | Encurtar para 800 mm uma parede com um balcão de 1.200 mm lista o balcão antes de confirmar; apagar o trecho do balcão e responder "Não" deixa o balcão solto no mesmo lugar | 🟢 |

### 5.2 Editor de geometria

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-11 | Criar placa ou caixa por pontos de referência no ambiente (cantos de parede, faces de módulos, piso), com pré-visualização e medidas digitadas | Must | Cancelar não cria objeto; confirmar cria a peça com as medidas mostradas (001 RF-070) | 🟢 |
| RF-12 | Editar uma geometria existente: dimensões, posição pelas cotas, material e acabamento por face | Must | Mudar a espessura de 18 para 25 mm atualiza o 3D sem mover a face de apoio | 🟡 |
| RF-14 | Marcar a geometria como "peça de fabricação", com componente, matéria-prima e espessura (RN-14) | Should | Uma placa de MDF de 18 mm marcada aparece na lista de peças e no JSON global | 🟡 |
| RF-15 | Duplicar, espelhar e excluir uma geometria, com desfazer | Should | Excluir e desfazer devolve a peça com o mesmo material | 🟡 |

### 5.3 Janela de propriedades por tipo de objeto

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-16 | Janela de propriedades única, que identifica o tipo do objeto ativo (RN-01) e mostra só os grupos desse tipo, para objetos de todas as bibliotecas | Must | Selecionar um gabinete frameless, um face frame, um starter de closets e um módulo rápido mostra os grupos de "Módulo" para os quatro | 🟢 |
| RF-17 | Grupo **Dimensões** (largura, altura, profundidade) para módulos, geometrias, aberturas e obstáculos, com edição imediata (RN-03) | Must | Largura do balcão de 600 para 800 mm atualiza o 3D em um passo de desfazer | 🟢 |
| RF-18 | Grupo **Cotas** para módulos e geometrias: afastamento da parede, anterior, posterior, inferior e superior, editáveis (RN-04) | Must | Cota anterior de 75 mm deixa o módulo a 75 mm do vizinho, com a largura igual | 🟢 |
| RF-19 | Grupo **Abrir** para frentes de módulo (porta, gaveta, basculante, pullout) e para o módulo que tem frentes: abrir, fechar e escolher o ângulo (0°, 45°, 90°), com o mesmo comportamento da inspeção da 001 | Must | Com uma gaveta selecionada, "Abrir" a desliza até o fim do curso; a janela mostra também o módulo a que ela pertence | 🟢 |
| RF-20 | Grupo **Abrir** para portas e janelas de ambiente, além de largura, altura, peitoril e posição na parede. As portas de ambiente ganham uma **folha 3D simples** (placa com a espessura da porta, presa no lado da dobradiça e no sentido de abertura do símbolo 2D), que o "Abrir" gira (esclarecimento de 2026-10-05) | Should | "Abrir" gira a folha da porta de ambiente; salvar e reabrir mostra a porta fechada (mesma regra de salvar fechado da 001, RN-14) | 🟢 |
| RF-21 | Grupo **Parede** para paredes (comprimento, alturas, espessura, ângulo, tipo) e botão "Abrir editor de parede" (RF-01) | Must | Selecionar a parede mostra os campos dela e o botão do editor | 🟢 |
| RF-22 | Grupo **Outras**: nome, biblioteca/linha de produto, código e camada (coleção) do objeto | Should | O balcão mostra "Frameless — Balcão 2 portas" e a coleção em que está | 🟡 |
| RF-23 | Ações próprias do tipo (as do menu do botão direito daquele objeto) também acessíveis na janela, em um grupo **Ações** | Should | As opções do menu do botão direito do gabinete aparecem como botões no grupo Ações | 🟡 |
| RF-24 | Linha de estado com o objeto ativo: nome, dimensões (L × A × P) e rotação, na unidade do usuário | Could | "Selecionado: Balcão 2 portas (800 × 720 × 550) — rotação 0°" | 🟡 |
| RF-25 | Ao selecionar um módulo, desenhar no 3D as cotas de RN-04 até as paredes, o piso e o teto, com os valores | Should | Selecionar o aéreo mostra a cota inferior até o piso e a cota superior até o teto | 🟡 |

### 5.4 "Mover Sobre"

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-26 | Botão "Mover Sobre" que liga e desliga o modo, no painel e no HUD da viewport, com estado visível (ligado/desligado) e saída por Esc | Must | Com o modo ligado o botão aparece destacado; Esc ou novo clique desliga | 🟢 |
| RF-27 | Com o modo ligado, em qualquer modo da viewport 3D, pressionar o botão direito sobre um objeto (A) e arrastar até outro (B) mostra uma linha do ponto de partida até o cursor e destaca o objeto sob o cursor; soltar sobre B abre a janela "Mover Sobre" (RN-05, RN-10) | Must | Arrastar do aéreo até o balcão e soltar abre a janela com os dois | 🟢 |
| RF-28 | A janela "Mover Sobre" mostra **duas vistas 2D lado a lado**, superior e frontal, com **apenas A e B** desenhados em contorno: B destacado como referência, A em outra cor, e as distâncias entre eles (X, profundidade, altura) na unidade do usuário | Must | Nenhum outro objeto da cena aparece nas vistas; as distâncias batem com o 3D | 🟢 |
| RF-29 | Na vista superior, os alvos de RN-06 (lados de B e profundidades de 0%, 30%, 50%, 75% e 100%) aparecem como marcas; passar o cursor perto de um alvo o destaca, e clicar alinha A (prévia) | Must | Clicar perto do lado direito de B deixa A encostado à direita de B; clicar perto da profundidade 0 deixa a frente de A alinhada à frente de B | 🟢 |
| RF-30 | Na vista frontal, os alvos de RN-07 (lados de B e alturas de 0%, 30%, 50%, 75% e 100%) com o mesmo comportamento | Must | Clicar perto da altura 100% de B deixa a base de A na altura do topo de B | 🟡 |
| RF-31 | Campos numéricos na janela para a distância de A a B em X, profundidade e altura, editáveis, com prévia | Should | Digitar 50 mm em X deixa 50 mm entre a lateral de B e a de A | 🟡 |
| RF-32 | Botões **Confirmar** e **Cancelar** (RN-09) e aviso de sobreposição (RN-11) | Must | Cancelar devolve A exatamente à posição de antes; Confirmar gera um passo de desfazer | 🟢 |
| RF-33 | Funciona para módulos de todas as bibliotecas, geometrias livres e obstáculos como A; e para esses e paredes como B | Must | A = aéreo face frame, B = balcão frameless funciona; B = parede alinha a profundidade de A à face da parede | 🟡 |

### 5.5 Movimento no plano da parede

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-34 | Arrastar um módulo já posicionado ao longo da parede em que ele está, só no plano da parede, com linhas-guia de alinhamento e as cotas de RN-04 atualizadas durante o arraste | Should | Arrastar o balcão mostra as cotas anterior e posterior mudando e não o afasta da parede | 🟡 |

### 5.6 Operações de parede no ambiente

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-35 | Remover parede com três opções: "Segmento" (só o trecho), "Tudo" (todo o contorno ligado) ou "Manter o selecionado" (remove os outros), e a caixa "Remover módulos que estão na parede" | Should | "Segmento" numa sala fechada abre o contorno; com a caixa marcada, os módulos da parede saem junto | 🟡 |
| RF-36 | "Rebaixar Parede": baixa a parede no 3D para 150 mm (altura fixa, esclarecimento de 2026-10-05), mantendo medidas, encontros e itens; desfazer o rebaixamento restaura a altura | Should | Rebaixar a parede da frente deixa ver o interior sem alterar o pé-direito gravado | 🟢 |
| RF-37 | Tornar parede ou teto invisível, mostrando só o contorno quando selecionado, e uma opção para esconder também esse contorno | Could | O teto invisível não aparece; selecionado, aparece em contorno | 🟡 |
| RF-38 | Ao abrir o Editor de Paredes com paredes de outra camada (`btm.wall_builder`) **selecionadas**, perguntar "Converter as paredes selecionadas para paredes editáveis?"; Sim converte cada trecho selecionado em parede do Home Builder 5 (mesma posição, comprimento, espessura e alturas) e remove a original; Não abre o editor com elas só como referência (esclarecimento de 2026-10-05) | Should | Com duas paredes da camada nova selecionadas, "Sim" as mostra editáveis na planta e "Não" as mostra tracejadas | 🟢 |
| RF-39 | Editar medida por digitação direta: com Selecionar/Mover, clicar na face (linha interna ou externa) ou num vértice da parede e digitar a nova medida no teclado (mm) e Enter; na face, muda o comprimento medido naquela face; no vértice, o trecho que termina nele (esclarecimento de 2026-10-05; referência: qualificad.com.br/editor-de-paredes-promob) | Must | Clicar na linha interna de 2.400, digitar 3000 e Enter deixa a interna com 3.000 e a externa com 3.300 | 🟢 |
| RF-40 | Direção da parede (Direita/Esquerda) no painel do trecho e no lápis: troca o lado para onde a espessura cresce; a sala desenhada em qualquer sentido fica com a espessura para fora, a frente dos módulos e o "para dentro" das portas voltados para o interior (RN-15) | Must | Desenhar 3.000 × 2.000 no sentido anti-horário e no horário gera a mesma sala (interna 3.000 × 2.000) com módulos encostados por dentro | 🟢 |
| RF-41 | Fechamento seguro da sala: ímã de 15 px no ponto inicial com destaque; pergunta "Deseja fechar a parede?" ao chegar ao início por clique, teclado ou arraste; no OK, contorno aberto com o fim no início é fechado (RN-17) | Must | Digitar 3000, 2000, 3000, 2000 voltando ao início pergunta; Sim liga os pontos e o 3D sai sem o canto solto | 🟢 |
| RF-42 | Pé-direito do projeto: paredes novas do editor nascem com o pé-direito das Configurações; no OK, paredes com outra altura (exceto Mureta) são listadas com a caixa "Igualar ao pé-direito do projeto", marcada por padrão | Must | Com o projeto em 2.700, a sala desenhada sai com 2.700; uma parede existente de 2.500 aparece na lista e, com a caixa marcada, vai para 2.700 | 🟢 |
| RF-43 | Mudar o pé-direito nas Configurações atualiza sozinho a altura (inicial e final) de todas as paredes do projeto, exceto Mureta | Must | Passar o pé-direito de 2.600 para 2.800 deixa todas as paredes normais e divisórias com 2.800 | 🟢 |
| RF-44 | O construtor "Desenhar Paredes" (3D) tem o mesmo ímã no ponto inicial e a mesma pergunta de fechamento do editor | Should | Desenhando no 3D, aproximar do início gruda e pergunta; Sim fecha a sala | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Vistas 2D (editor de parede e "Mover Sobre") redesenham em até 100 ms ao mover o cursor, num projeto com 50 módulos | Uso interativo; vistas atuais são renderizações à parte (`_reversa_sdd/hb_layouts/requirements.md#RN-22`) | 🟡 |
| Desempenho | Alinhamento no "Mover Sobre" mostra a prévia no 3D em até 200 ms | 001, RNF de edição em até 200 ms | 🟢 |
| Precisão | Alinhamentos sem folga nem sobreposição (erro ≤ 0,1 mm); cotas com 0,1 mm de precisão | 001, RNF de precisão | 🟢 |
| Reversibilidade | Toda edição (propriedades, editor de parede, geometria, "Mover Sobre") desfaz em um passo; cancelar não deixa objetos nem estado pela metade | 001, RNF de reversibilidade; CLAUDE.md | 🟢 |
| Robustez | Com o modo "Mover Sobre" ligado, o salvamento automático do Blender continua funcionando | Modais permanentes bloqueiam o salvamento automático (`operators/viewport_hud.py`, docstring) | 🟢 |
| Compatibilidade | O botão direito volta ao comportamento normal do Blender sempre que o modo for desligado, inclusive após fechar o arquivo ou desativar a extensão | RN-10 | 🟢 |
| Compatibilidade | Desligar ou atualizar a extensão remove **todos** os operadores, painéis, menus e atalhos que ela registrou (inclusive os legados do Home Builder 5) | Auditoria de 2026-10-05 (A002): 280 operadores sobravam; esclarecimento: corrigir dentro da 002 | 🟢 |
| Localização | Textos em português, vírgula decimal e unidade do usuário (mm/cm/m) em todas as vistas, cotas e campos | 001, unidades e localização | 🟢 |
| Acessibilidade | Referência, alvo destacado, sobreposição e erro comunicados por texto e forma, não só por cor | 001, RNF de acessibilidade | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Abrir o editor com as paredes do ambiente (RF-01, RF-02)
  Dado uma sala de 4 paredes
  Quando o usuário escolhe "Editar Paredes…" no botão direito de uma parede
  Então abre a janela do editor com a planta dos 4 trechos, linha interna e externa e a grade

Cenário: Desenhar a sala a lápis (RF-03)
  Dado o Editor de Paredes aberto num ambiente vazio, com a ferramenta Construir Parede
  Quando o usuário clica o ponto inicial, digita 3900 e Enter, 2700 e Enter, 3900 e Enter e clica no ponto inicial
  Então o editor pergunta "Deseja fechar a parede e finalizar a sua construção?"
  E ao responder Sim o contorno fica fechado com 4 trechos

Cenário: Medida interna e externa (RF-04)
  Dado uma sala de 3.900 × 2.700 mm (externa) com paredes de 150 mm
  Quando o usuário clica na linha externa do trecho menor
  Então o painel mostra comprimento 2.700 mm
  Quando clica na linha interna do mesmo trecho
  Então o painel mostra 2.400 mm
  E a linha interna aparece tracejada e a externa contínua

Cenário: Digitar a medida direto na face (RF-39)
  Dado o editor com a linha interna de 2.400 mm selecionada
  Quando o usuário digita 3000 e pressiona Enter
  Então a medida interna passa a 3.000 mm e a externa a 3.300 mm

Cenário: Ímã e fechamento pelo teclado (RF-41)
  Dado o lápis com 3 trechos desenhados
  Quando o cursor chega a 10 px do ponto inicial
  Então o ponto inicial fica destacado e a pré-visualização gruda nele
  Quando o usuário digita 2000 e Enter e o trecho termina no ponto inicial
  Então o editor pergunta "Deseja fechar a parede?"
  E respondendo Sim, o contorno fecha e o 3D sai sem o canto solto

Cenário: Pé-direito do projeto (RF-42, RF-43)
  Dado o pé-direito do projeto em 2.700 nas Configurações
  Quando o usuário desenha uma sala no editor e clica OK
  Então todas as paredes saem com 2.700
  Quando o usuário muda o pé-direito do projeto para 2.800
  Então todas as paredes, exceto Mureta, passam a 2.800

Cenário: Direção da parede (RF-40, RN-15)
  Dado uma sala desenhada a lápis no sentido anti-horário
  Quando o usuário clica OK
  Então a espessura fica do lado de fora e as medidas internas são as digitadas
  E um balcão encostado numa parede fica dentro da sala e uma porta "para dentro" abre para dentro
  Quando o usuário muda a Direção de um trecho
  Então a espessura troca de lado e a medida interna não muda

Cenário: Editar o trecho e arrastar vértice (RF-05, RF-06)
  Dado um trecho de 3.900 mm selecionado
  Quando o usuário muda o comprimento para 4.100 mm
  Então o trecho cresce no sentido da seta
  E arrastar um vértice atualiza comprimento e ângulos no painel durante o arraste

Cenário: Valor fora da faixa no editor (RF-05, RN-18)
  Dado um trecho selecionado
  Quando o usuário digita espessura de 5 mm
  Então aparece "Valor Inválido" com a faixa de 10 a 2.000 mm
  E o trecho não muda

Cenário: Vértices, sentido e grade (RF-07, RF-08)
  Dado um trecho de 3.900 mm e a grade de 1.000 mm com linhas magnéticas
  Quando o usuário adiciona um vértice no meio e solta outro vértice perto de um cruzamento
  Então surgem dois trechos que somam 3.900 mm e o vértice vai para o cruzamento
  E "Inverter Sentido" troca a seta do trecho

Cenário: Cancelar não muda o 3D (RF-09)
  Dado o editor aberto com 3 trechos alterados
  Quando o usuário clica Cancelar
  Então as paredes 3D ficam exatamente como antes

Cenário: OK aplica e avisa itens presos (RF-09, RF-10)
  Dado uma parede com um balcão de 1.200 mm
  Quando o usuário encurta essa parede para 800 mm e clica OK
  Então o editor lista o balcão antes de confirmar
  E ao confirmar, paredes, encontros, piso e teto ligados são refeitos em um passo de desfazer

Cenário: Apagar trecho com módulos (RF-10, RN-13)
  Dado uma sala com um balcão preso à parede da frente
  Quando o usuário apaga esse trecho no editor e clica OK
  Então o editor pergunta "Remover os módulos junto?"
  E respondendo "Não", o balcão fica solto no mesmo lugar
  E respondendo "Sim", o balcão é removido com a parede

Cenário: Paredes de outra camada (RF-02, RF-38)
  Dado duas paredes feitas com o construtor da camada nova, selecionadas
  Quando o usuário abre o Editor de Paredes
  Então o editor pergunta se deve convertê-las para paredes editáveis
  E respondendo "Sim", elas aparecem na planta como trechos editáveis, no mesmo lugar
  E respondendo "Não", elas aparecem só como contorno tracejado

Cenário: Remover, rebaixar e esconder paredes (RF-35, RF-36, RF-37)
  Dado uma sala fechada com módulos numa parede
  Quando o usuário remove essa parede com "Segmento" e "Remover módulos que estão na parede"
  Então o contorno fica aberto e os módulos dela saem junto
  E "Rebaixar Parede" em outra parede deixa ver o interior sem mudar o pé-direito gravado
  E o teto invisível só aparece em contorno quando selecionado

Cenário: Criar geometria por pontos (RF-11)
  Dado o editor de geometria em modo de criação
  Quando o usuário clica dois cantos da parede e digita a espessura de 18 mm
  Então uma placa com essas medidas aparece na pré-visualização
  E só é criada ao confirmar

Cenário: Cancelar a criação de geometria (RF-11)
  Dado a pré-visualização de uma placa
  Quando o usuário pressiona Esc
  Então nenhum objeto é criado

Cenário: Editar e fabricar geometria (RF-12, RF-14, RF-15)
  Dado uma placa de MDF de 18 mm marcada como peça de fabricação
  Quando o usuário muda a espessura para 25 mm, duplica a placa e gera a lista de peças
  Então a placa e a cópia aparecem na lista com matéria-prima e espessura
  E excluir e desfazer devolve a cópia com o mesmo material

Cenário: Propriedades acompanham o tipo do objeto (RF-16, RF-21, RF-22)
  Dado um projeto com parede, balcão frameless e gaveta
  Quando o usuário seleciona a parede, depois o balcão, depois a gaveta
  Então a janela mostra o grupo Parede, depois Dimensões e Cotas, depois Abrir com o módulo da gaveta
  E o grupo Outras mostra biblioteca e coleção de cada um

Cenário: Editar dimensões e cotas pela janela (RF-17, RF-18)
  Dado um balcão com cota anterior de 200 mm
  Quando o usuário digita 75 mm na cota anterior
  Então o balcão fica a 75 mm do vizinho com a mesma largura
  E desfazer volta a 200 mm em um passo

Cenário: Valor inválido nas propriedades (RF-17, RN-03)
  Dado um balcão selecionado
  Quando o usuário digita largura 0
  Então aparece "Valor Inválido" com campo, unidade e faixa
  E o balcão não muda

Cenário: Abrir pela janela de propriedades (RF-19, RF-20)
  Dado uma gaveta e uma porta de ambiente
  Quando o usuário clica "Abrir" em cada uma
  Então a gaveta desliza até o fim do curso e a porta gira
  E salvar e reabrir mostra as duas fechadas

Cenário: Ações, estado e cotas ao selecionar (RF-23, RF-24, RF-25)
  Dado um aéreo selecionado
  Então o grupo Ações tem as opções do menu do aéreo
  E a linha de estado mostra nome, L × A × P e rotação
  E o 3D mostra a cota inferior até o piso e a superior até o teto

Cenário: Sem seleção (RF-16, RN-02)
  Dado nenhum objeto selecionado
  Então a janela de propriedades mostra "Nenhum objeto selecionado"

Cenário: Mover Sobre encostando ao lado (RF-26, RF-27, RF-28, RF-29, RF-32)
  Dado o modo "Mover Sobre" ligado, um aéreo A e um balcão B
  Quando o usuário arrasta A sobre B com o botão direito e solta
  Então abre a janela com as vistas superior e frontal só com A e B
  E B passa a ser o objeto ativo
  Quando o usuário clica perto do lado direito de B na vista superior
  Então A fica encostado à direita de B, sem folga nem sobreposição
  E Confirmar grava a posição em um passo de desfazer

Cenário: Mover Sobre alinhando profundidade e altura (RF-29, RF-30, RF-31)
  Dado a janela "Mover Sobre" aberta com A e B
  Quando o usuário clica perto da linha de 50% de profundidade de B na vista superior
  Então a face frontal de A fica na metade da profundidade de B
  Quando o usuário clica perto da altura 100% de B na vista frontal
  Então a base de A fica na altura do topo de B
  E digitar 50 mm em X deixa 50 mm entre as laterais

Cenário: Clique longe de qualquer alvo (RF-29)
  Dado a janela "Mover Sobre" aberta
  Quando o usuário clica a mais de 12 px de qualquer alvo
  Então A não se move

Cenário: Cancelar o Mover Sobre (RF-32)
  Dado a janela "Mover Sobre" com uma prévia aplicada
  Quando o usuário clica Cancelar
  Então A volta exatamente à posição original

Cenário: Soltar sobre o vazio (RF-27, RN-10)
  Dado o modo "Mover Sobre" ligado
  Quando o usuário arrasta A com o botão direito e solta sobre o vazio
  Então nada muda e nenhum menu abre

Cenário: Botão direito volta ao normal (RF-26, RN-10)
  Dado o modo "Mover Sobre" ligado
  Quando o usuário desliga o modo
  Então o botão direito volta a abrir o menu de contexto

Cenário: Aviso de sobreposição (RF-32, RN-11)
  Dado "Evitar Sobreposição" ligado
  Quando o alinhamento escolhido sobrepõe A a outro módulo
  Então a janela lista o módulo sobreposto antes de confirmar

Cenário: Mover Sobre entre bibliotecas e com parede (RF-33)
  Dado um aéreo face frame A e um balcão frameless B
  Quando o usuário alinha A à profundidade 0 de B
  Então a frente de A fica alinhada à de B
  E com uma parede como B, A fica com a face de trás na face da parede

Cenário: Arrastar no plano da parede (RF-34)
  Dado um balcão encostado numa parede
  Quando o usuário o arrasta ao longo da parede
  Então ele só se move no plano da parede e as cotas anterior e posterior mudam ao vivo
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01..RF-06, RF-09 | Must | Editor de paredes 2D a lápis pedido pelo usuário, com medida interna/externa |
| RF-07, RF-08, RF-10 | Should | Ferramentas de vértice, grade e aviso de itens; há alternativa (redesenhar, digitar) |
| RF-35, RF-36 | Should | Operações de parede da referência; parte já existe no legado |
| RF-41, RF-42, RF-43 | Must | Esclarecimento de 2026-10-05 (3ª sessão): ímã, fechamento seguro e pé-direito único do projeto |
| RF-44 | Should | Mesmo comportamento no construtor 3D legado |
| RF-39, RF-40 | Must | Esclarecimento de 2026-10-05 (2ª sessão): medida real = interna, digitação direta e Direção |
| RF-38 | Should | Esclarecimento de 2026-10-05: trazer paredes da camada nova para o editor sob pedido |
| RF-37 | Could | Ocultar já existe no legado de forma simples |
| Vista de frente (elevação) editável da parede, editar portas/janelas/módulos dentro do editor | Won't | Esclarecimento de 2026-10-05: o editor de paredes desenha só paredes |
| RF-11, RF-12 | Must | Editor de geometria pedido pelo usuário; já Must na 001 (RF-070) |
| RF-14, RF-15 | Should | Fabricação e edição auxiliar |
| Geometria por perfil extrudado (sanca, rodapé, moldura), cilindro, recortes em L/U | Won't (nesta feature) | Esclarecimento de 2026-10-05: só placa e caixa; 001 RF-072/RF-073 continuam pendentes para outra feature |
| RF-16..RF-19, RF-21 | Must | Janela de propriedades por tipo pedida pelo usuário, com "abrir" |
| RF-20, RF-22, RF-23, RF-25 | Should | Complementos da janela de propriedades |
| RF-24 | Could | Informação já visível na janela |
| RF-26..RF-30, RF-32, RF-33 | Must | "Mover Sobre" pedido pelo usuário |
| RF-31 | Should | Alternativa numérica ao clique |
| RF-34 | Should | Movimentação do vídeo de referência; há o "Mover Sobre" e as cotas como alternativas |
| Navegação de câmera do vídeo (pan, zoom, órbita com botões do meio + direito, seletor de modos Pan/Zoom/Caminhar, "Mover HotPoint"), F8 para alternar projeção e atalho Ctrl+Shift+P | Won't | O Blender já tem navegação própria; trocar os atalhos conflita com o resto do programa e com o modo "Mover Sobre" (botão direito) |
| "Mobi Editor" (área própria do plugin) e botões em grade flutuantes na viewport | Won't (nesta feature) | Esclarecimento de 2026-10-05: vira a feature 003 |
| Botões "Junções" e "Auto Rebaixar" do vídeo | Won't (nesta feature) | Sem regra definida no material de referência; ficam para uma feature própria |
| RNF de desempenho das vistas 2D | Should | Uso interativo |

## 9. Esclarecimentos

### Sessão 2026-10-05

- **Q:** No editor de parede, basta editar por campos e cotas, ou o usuário também deve arrastar aberturas e módulos com o mouse na vista 2D?
  **R:** No editor de parede só se desenha parede, em 2D — diferente do construtor de paredes que usa a viewport do Blender. É como um lápis desenhando a parede, e permite selecionar a linha interna para ver a medida interna e a externa para ver a medida externa. Referência detalhada: resumo dos vídeos de construção de paredes do Promob fornecido pelo usuário. → §1, §2, RN-12, RN-13, RN-15–RN-18, RF-01–RF-10, RF-35–RF-37.
- **Q:** No editor de geometria, quais formas entram agora?
  **R:** Só placa e caixa. → RF-11, RF-13 (removido), MoSCoW.
- **Q:** Na vista frontal do "Mover Sobre", clicar acima do topo empilha A sobre B, e as alturas de 0% a 100% alinham a base de A?
  **R:** Sim. → RN-07, RF-30.
- **Q:** RF-20 pede "Abrir" para portas de ambiente, mas elas não têm folha 3D (só o recorte e o símbolo 2D). O que fazer?
  **R:** Modelar uma folha 3D simples (placa com a espessura da porta, presa na dobradiça), que gira pelo "Abrir" e volta fechada ao salvar. → RF-20.
- **Q:** "Rebaixar Parede" (RF-36): a altura de 150 mm serve?
  **R:** 150 mm fixo. → RF-36.
- **Q:** No Editor de Paredes, ao apagar um trecho com módulos, o OK deve deixar os módulos soltos, perguntar ou removê-los junto?
  **R:** Deixar soltos por padrão e perguntar no OK se devem ser removidos junto. → RN-13, RF-10.
- **Q:** As paredes da camada nova (`btm.wall_builder`) devem aparecer no editor só como contorno de referência?
  **R:** Sim, como referência; e, se houver paredes de outra camada selecionadas, perguntar se devem ser convertidas. → RF-02, RF-38.
- **Q:** "Mobi Editor" e botões em grade flutuantes: entram na 002 ou numa feature nova?
  **R:** Feature nova (003); a 002 segue para o fechamento. → MoSCoW.

### Sessão 2026-10-05 (3ª, fechamento e pé-direito)

- **Q:** Raio do ímã no ponto inicial?
  **R:** 15 px na tela, o mesmo raio em qualquer zoom. → RN-17, RF-41.
- **Q:** Chegar ao ponto inicial pelo teclado ou arrastando um vértice deve perguntar ou fechar direto?
  **R:** Perguntar "Deseja fechar a parede?", igual ao clique. → RN-17, RF-41.
- **Q:** Paredes existentes com outra altura?
  **R:** No OK, listar e oferecer "Igualar ao pé-direito do projeto", marcada por padrão. → RF-42.
- **Q:** Mudar o pé-direito nas Configurações depois de as paredes existirem?
  **R:** As paredes mudam sozinhas para a nova altura (todas, menos Mureta). → RF-43.
- **Q:** O "Desenhar Paredes" (3D) também deve ter o ímã e a pergunta?
  **R:** Sim, o mesmo comportamento nas duas ferramentas. → RF-44.

### Sessão 2026-10-05 (2ª, pós-auditoria ao vivo)

- **Q:** Salas desenhadas no sentido anti-horário ficam com a espessura para dentro e os módulos e portas "para fora" (A003). Como corrigir?
  **R:** O editor ganha a propriedade **Direção (Direita/Esquerda)**, que muda o sentido (o lado da espessura). As medidas digitadas valem para a face **interna** (medida real); a externa é a interna + a espessura. Linha interna tracejada, externa contínua. Para mudar uma medida: abrir o editor, clicar na face ou no vértice, digitar a medida (mm) e Enter. Referência: https://qualificad.com.br/editor-de-paredes-promob/ → RN-15, RN-17, RF-02, RF-05, RF-39, RF-40.
- **Q:** Mover Sobre ligado: o botão direito vale em todos os modos ou só no Modo Objeto (A001)?
  **R:** Em todos os modos da viewport 3D. → RF-27.
- **Q:** Cancelar do Editor de Paredes (A005)?
  **R:** OK/Cancelar no fim do painel e confirmação ao cancelar com alterações. → RF-09.
- **Q:** Onde corrigir os 280 operadores legados que não saem ao desligar (A002)?
  **R:** Dentro da 002. → RNF de compatibilidade.
- **Q:** Placa/Caixa por pontos: o primeiro clique deve encaixar em objetos (A009)?
  **R:** Manter o encaixe automático no objeto sob o cursor. → RF-11 (sem mudança).

## 10. Lacunas

- 🟡 Tolerância de 12 px para "perto de um alvo" e referencial de B para objetos com rotação diferente (RN-06, RN-08): premissas a confirmar no uso.
- 🟡 Faixas e padrões dos campos do editor de paredes (RN-18) vêm de descrição de terceiros; confirmar no uso.
- 🟡 Tipos de parede "Divisória" e "Mureta" (RN-18) não existem no legado (hoje Normal/Drywall/Vidro); o efeito de cada tipo no 3D precisa ser definido no plano.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-05 | Esclarecimentos (4ª rodada, fechamento e pé-direito): ímã de 15 px, pergunta também por teclado/arraste, fechamento seguro no OK (RN-17, RF-41); pé-direito do projeto nas paredes novas, igualar existentes no OK (RF-42), Configurações atualizam todas as paredes (RF-43), ímã no construtor 3D (RF-44) | reversa |
| 2026-10-05 | Esclarecimentos (3ª rodada, pós-auditoria ao vivo): medida real = interna, Direção Direita/Esquerda, digitação direta na face/vértice (RN-15, RN-17, RF-02, RF-05, RF-39, RF-40), botão direito do Mover Sobre em todos os modos (RF-27), Cancelar com confirmação no fim do painel (RF-09), desregistro completo (RNF) | reversa |
| 2026-10-05 | Esclarecimentos (2ª rodada, pós-auditoria): folha 3D para portas de ambiente (RF-20), rebaixar 150 mm fixo (RF-36), pergunta sobre módulos de trecho apagado (RN-13, RF-10), paredes da camada nova como referência + conversão sob pergunta (RF-02, RF-38), "Mobi Editor" vira feature 003 | reversa |
| 2026-10-05 | Esclarecimentos integrados: editor de paredes vira planta 2D a lápis (só paredes, linha interna/externa); geometria só placa e caixa; empilhar no "Mover Sobre" | reversa |
| 2026-10-04 | Versão inicial gerada por `/reversa-requirements` (pedido do usuário + resumo do vídeo de movimentação básica do Promob + levantamento do código) | reversa |

## Pendências de Qualidade

- Q-018 (nome de produto comercial): "Promob" e "Blender" aparecem de propósito. O Promob é a referência de comportamento pedida pelo usuário; o Blender é a plataforma do produto. Nenhuma biblioteca ou framework de implementação é citado.
