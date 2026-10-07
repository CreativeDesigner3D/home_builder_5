# Requirements: Módulos personalizáveis, agregados e Reposicionar

> Identificador: `003-modulos-agregados-reposicionar`
> Data: `2026-10-07`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: bug #5 `BUG-20261006-OG3P` (contexto `modulos-personalizaveis`) + `docs/elicitação-requisitos-reposicionamento-3d.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Hoje o projetista insere módulos prontos e só ajusta medidas: não troca a frente de uma porta, o puxador, o material
de uma peça ou a divisão interna de um módulo específico, e não guarda o resultado para reutilizar. Também não há como
trazer um modelo de fora (uma porta baixada do SketchUp, por exemplo) e fazê-lo se comportar como peça do móvel.
Esta feature entrega três coisas para o projetista de interiores: (1) **personalizar o módulo inserido** (portas,
gavetas, puxadores, materiais e divisões internas) e salvá-lo como **novo módulo da biblioteca**; (2) **agregados**:
qualquer malha vira peça presa a um elemento pai, que só se move dentro do espaço do pai, pode se afastar dele ou
afundar nele (com opção de perfurar), e uma malha pode virar **folha de porta** com barra de abertura; (3) a janela
**Reposicionar** no estilo Promob, ampliando o Mover Sobre da feature 002 com campos X/Y/Z, rotação, passo, posição
relativa/absoluta, posições salvas e plano de inserção.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/frameless/requirements.md#Responsabilidades` | O módulo frameless já cuida de frentes, sobreposições, interiores, puxadores, estilos de gabinete e de porta, e "Salvar e carregar grupos de gabinetes numa biblioteca do usuário" | 🟢 |
| `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-44) | Grupo salvo com `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)` e miniatura 256 px (`ops_library.save_cabinet_group_to_user_library`) | 🟢 |
| `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-25, RN-29) | Porta 5 peças tem tamanho mínimo; estilo é vinculado por **índice**, e remover um estilo reindexa os gabinetes | 🟢 |
| `_reversa_sdd/frameless/requirements.md#Requisitos Funcionais` (RF-09, RF-20, RF-21) | Trocar configuração do vão (30 tipos) recria os filhos e relocaliza puxadores; estilos de gabinete e de porta têm CRUD | 🟢 |
| `_reversa_sdd/product_common/requirements.md#Requisitos Funcionais` (RF-01..RF-04) | Motor de porta comum: `door_style_info`, larguras de quadro, tamanho mínimo e layout de peças | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-02..RF-06, RF-15) | Raycast com anel de raios, snap a vértice/grade, digitação com conversão de unidade, cota de 3 cliques | 🟢 |
| `_reversa_sdd/geometry/requirements.md#Requisitos Funcionais` | Malhas paramétricas por bmesh e caixa de armário com peças de espessura | 🟢 |
| `_reversa_sdd/domain.md#2.2 Regras de Snapping e Movimentação de Aberturas` | Aberturas presas à parede se movem só ao longo dela | 🟢 |
| `_reversa_forward/001-addon-moveis-planejados/` (decisões D-20, D-21, D-25) + `caffmob_draw/inspection/pivot_math.py` | Abertura de frentes: articuladas em graus (0 = fechada, máx. 90°), gavetas em fração do curso, paradas 0/45/90° | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#5` (RF-26..RF-34) | Mover Sobre: arraste com botão direito de A até B, janela com vistas superior e frontal, alvos de alinhamento, campos de distância, Confirmar/Cancelar | 🟢 |
| `_reversa_bugs/modulos-personalizaveis/bugs/BUG-20261006-OG3P-*/bug.md` | Pedido do titular: portas, gavetas, puxadores, materiais, divisões internas; salvar como módulo; agregados presos ao pai com perfurar | 🟢 |
| `docs/elicitação-requisitos-reposicionamento-3d.md#8` (RF-001..RF-022) | Fluxo Reposicionar do Promob: vistas frontal e planta, X/Y/Z, rotação, passo, relativa/absoluta, posições salvas, Substituir, plano de inserção, painel Arranjo/Modelos/Movimentação/Propriedades, limites, cotas, salvar, desfazer | 🟡 (evidência em vídeo, sem código) |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores (P01 da elicitação) | Adaptar o módulo ao pedido do cliente sem remodelar | Troca a porta lisa do aéreo por uma de vidro, o puxador por um perfil e a prateleira por duas gavetas, e salva como "Aéreo vidro 2G" |
| Modelador técnico (P02) | Usar modelos de fornecedores no projeto | Importa uma porta de correr baixada do SketchUp, converte em folha de porta do roupeiro e testa a abertura pela barra |
| Projetista de interiores | Posicionar com precisão em relação a outro objeto | Arrasta o nicho até o painel, digita X = 150 mm e rotação 90°, confirma, e guarda a posição para os outros quartos |
| Revisor interno (P03) | Conferir medidas e encaixes | Abre as propriedades do agregado e vê limites mínimo/máximo e a profundidade em que ele afunda no pai |

## 4. Regras de negócio novas ou alteradas

**Personalização de módulo**

1. **RN-01:** A personalização vale para **um módulo inserido** (a instância). Os outros módulos do mesmo tipo e o catálogo não mudam. 🟡
   - Tipo: nova
2. **RN-02:** Os itens personalizáveis são: frente de cada vão (porta, gaveta, basculante, painel, vazio), estilo de cada frente, puxador de cada frente (modelo e posição), material de cada peça ou grupo de peças, e divisões internas (prateleiras, divisórias verticais, gavetas internas). Vale para os módulos de **todas** as bibliotecas: frameless, face frame, closets e os paramétricos do CAFFMob (`btm`). 🟢 (pedido do titular; Esclarecimentos 2026-10-07, Q4)
   - Origem no legado: `_reversa_sdd/frameless/requirements.md#Requisitos Funcionais` (RF-09, RF-20, RF-21)
   - Tipo: alterada (o legado aplica estilo e configuração por vão, sem o conjunto unificado por instância)
3. **RN-03:** Trocar uma frente respeita as regras do motor de porta: porta abaixo do tamanho mínimo do estilo não recebe o estilo e o usuário vê a mensagem. 🟢
   - Origem no legado: `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-25)
   - Tipo: preservada
4. **RN-04:** "Salvar como módulo" grava uma **cópia** na biblioteca do usuário, com nome, categoria e miniatura; o módulo salvo continua paramétrico (largura, altura e profundidade editáveis depois de inserido) e guarda as personalizações. 🟡
   - Origem no legado: `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-44)
   - Tipo: alterada (o legado salva grupos de gabinetes frameless; passa a valer para qualquer módulo e para um módulo só)
5. **RN-05:** Salvar com nome já existente na mesma categoria pede confirmação para substituir; nunca sobrescreve em silêncio. 🟡
   - Tipo: nova
6. **RN-06:** O módulo salvo referencia materiais e estilos por **nome**, não por índice, para não trocar de estilo quando outro é removido. 🟡
   - Origem no legado: `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-29, vínculo por índice)
   - Tipo: alterada só para o módulo salvo

**Agregados**

7. **RN-07:** Qualquer objeto de malha pode ser convertido em **agregado** de um elemento pai (módulo, peça de módulo, parede, painel ou outro agregado). O agregado fica preso ao pai: mover, girar ou apagar o pai leva o agregado junto. 🟢 (pedido do titular)
   - Tipo: nova
8. **RN-08:** O agregado só se move dentro do **espaço do pai**: nas direções da face em que está preso, a caixa do agregado não passa do contorno do pai. Valor fora do limite é ajustado ao limite e o campo mostra o valor ajustado. 🟢 (pedido do titular)
   - Tipo: nova
9. **RN-09:** Na direção perpendicular à face, o agregado pode **se afastar** (valor positivo) ou **afundar** no pai (valor negativo, até a espessura do pai). 🟢 (pedido do titular)
   - Tipo: nova
10. **RN-10:** Agregado afundado com **Perfurar** ligado recorta o pai no volume ocupado, só no 3D e de forma não destrutiva; desligar Perfurar ou remover o agregado devolve o pai inteiro. Se o usuário marcar também **"Furo real no plano de corte"**, o furo vira usinagem da peça pai no plano de corte e na exportação de produção; sem essa marca, a produção não muda. 🟢 (Esclarecimentos 2026-10-07, Q2)
    - Tipo: nova
11. **RN-11:** Uma malha convertida em **folha de porta** recebe um tipo de movimento: **giro** (eixo à esquerda, à direita, no topo ou na base; sentido; ângulo máximo configurável por folha, ex.: 90°, 110°, 180°) ou **correr** (trilho na horizontal, sentido e curso configurável). A barra de abertura vai de 0 (fechada) ao máximo e move a folha em tempo real; o valor é guardado no arquivo. 🟢 (pedido do titular; Esclarecimentos 2026-10-07, Q5)
    - Origem no legado: `caffmob_draw/inspection/pivot_math.py` (D-20: graus, 0 = fechada; D-25: paradas 0/45/90°)
    - Tipo: nova (reutiliza a convenção existente)
11a. **RN-11a:** Durante a abertura, a folha **para ao encostar** em parede, módulo ou outro objeto sólido no caminho: o valor da barra fica preso no ponto do contato, a folha é desenhada encostada e o painel avisa "Folha bateu em <objeto>". Fechar continua livre. 🟢 (Esclarecimentos 2026-10-07, Q5)
    - Tipo: nova
12. **RN-12:** Converter não apaga a malha importada: desfazer a conversão (Ctrl+Z ou "Desconverter") devolve o objeto como era. 🟡
    - Tipo: nova
13. **RN-13:** Um agregado entra na lista de peças (plano de corte) só se o usuário marcar "Peça de produção"; por padrão é acessório e fica fora do corte. 🟡
    - Tipo: nova

**Reposicionar**

14. **RN-14:** Reposicionar exige um objeto móvel e uma referência; a referência nunca se move. Grupos (módulo com filhos, agregados) movem-se inteiros, preservando a posição relativa dos filhos. 🟡
    - Origem: `docs/elicitação-requisitos-reposicionamento-3d.md#9` (RN-01..RN-03)
    - Tipo: nova
15. **RN-15:** Fechar a janela sem confirmar não aplica nada; confirmar gera **um** passo de desfazer. 🟢
    - Origem no legado: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#5` (RF-32)
    - Tipo: preservada
16. **RN-16:** Valores mostrados e digitados usam a unidade da cena; texto digitado segue a conversão já existente (`600` em mm → 0,6 m). 🟢
    - Origem no legado: `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-06)
    - Tipo: preservada
17. **RN-17:** O plano de inserção escolhido vale para as próximas inserções e para os movimentos que usam o plano, até o usuário trocar. 🟡
    - Origem: `docs/elicitação-requisitos-reposicionamento-3d.md#9` (RN-04)
    - Tipo: nova

## 5. Requisitos Funcionais

**A. Personalização de módulo**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Painel "Personalizar módulo" para o módulo selecionado de qualquer biblioteca (frameless, face frame, closets, `btm`), com seções Frentes, Puxadores, Materiais e Divisões internas | Must | Selecionar um balcão frameless, um face frame, um roupeiro e um módulo `btm` mostra as quatro seções preenchidas com o estado atual de cada um; seção sem suporte numa biblioteca aparece desabilitada com o motivo | 🟢 |
| RF-02 | Trocar a frente de um vão: porta (1 ou 2 folhas), gaveta(s), basculante, painel fixo ou vazio | Must | Trocar o vão de porta por 3 gavetas recria as frentes e realoca os puxadores (RN-02) | 🟢 |
| RF-03 | Trocar o estilo de uma frente (lisa, 5 peças, vidro) só naquela frente | Must | Aplicar 5 peças numa porta de 50 cm altera só ela; porta abaixo do mínimo mostra a mensagem e fica como estava (RN-03) | 🟢 |
| RF-04 | Trocar o puxador de uma frente ou de todas do módulo: modelo, posição (topo, meio, base, lateral) e "sem puxador" | Must | Escolher perfil na gaveta superior troca só ela; "aplicar a todas" troca todas as frentes do módulo | 🟢 |
| RF-05 | Trocar o material por peça ou por grupo (caixa, frentes, fundo, interno) | Must | Frentes em laca branca e caixa em MDF carvalho, com o veio preservado | 🟡 |
| RF-06 | Editar divisões internas: número de prateleiras, divisórias verticais e gavetas internas por vão, com espaçamento igual ou alturas digitadas | Must | 3 prateleiras num vão de 72 cm ficam com vãos iguais; digitar alturas posiciona cada uma | 🟡 |
| RF-07 | "Salvar como módulo": nome, categoria e miniatura gerada; grava na biblioteca do usuário e aparece no navegador de módulos | Must | Depois de salvar, o módulo aparece na biblioteca; inserido noutro arquivo, vem com frentes, puxadores, materiais e divisões iguais (RN-04) | 🟢 |
| RF-08 | Nome repetido na mesma categoria pede confirmação para substituir | Should | Salvar "Aéreo vidro" duas vezes abre a pergunta; "Não" mantém o anterior (RN-05) | 🟡 |
| RF-09 | Módulo salvo inserido continua paramétrico | Must | Mudar a largura de 80 para 60 cm redistribui frentes e divisões sem perder a personalização | 🟡 |
| RF-10 | Gerir módulos salvos: renomear, apagar (com confirmação) e abrir a pasta | Should | Apagar remove da lista e do disco após confirmar | 🟢 |

**B. Agregados**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-11 | Importar um modelo 3D externo pelo plugin com os importadores do Blender (OBJ, FBX, glTF/GLB); objetos trazidos por outros addons de importação (ex.: `.skp`) também podem ser convertidos, pois a conversão aceita qualquer objeto de malha da cena | Must | Importar uma porta em OBJ coloca a malha em escala correta; uma malha trazida por outro addon aparece como candidata a "Converter em agregado" | 🟢 |
| RF-12 | "Converter em agregado": com a malha e o pai selecionados (ou escolhendo o pai pelo clique), a malha vira agregado preso à face mais próxima do pai | Must | Mover o balcão leva o agregado junto; apagar o balcão pergunta se apaga também os agregados (RN-07) | 🟢 |
| RF-13 | Mover o agregado arrastando ou pelos campos, limitado ao espaço do pai | Must | Arrastar o nicho para fora do painel o faz parar na borda; digitar valor acima do máximo mostra o máximo (RN-08) | 🟢 |
| RF-14 | Campo "Afastamento" (positivo afasta, negativo afunda até a espessura do pai) | Must | −10 mm num painel de 18 mm deixa o agregado 10 mm dentro; −30 mm fica em −18 mm (RN-09) | 🟢 |
| RF-15 | Opção "Perfurar" para agregado afundado, com recorte não destrutivo do pai no 3D, e a opção "Furo real no plano de corte" que leva o furo para a usinagem da peça pai | Must | Ligar Perfurar abre o furo no 3D e o plano de corte não muda; marcar "Furo real" faz a peça pai aparecer com a usinagem no plano de corte; desligar devolve tudo (RN-10) | 🟢 |
| RF-16 | "Converter em folha de porta": escolher giro (eixo, sentido, ângulo máximo) ou correr (sentido, curso); o painel mostra a barra de abertura (0 a 100%) que move a folha em tempo real | Must | Giro com máximo 90°: 50% deixa a folha a 45°; correr com curso 80 cm: 50% desliza 40 cm; voltar a 0 fecha exatamente na posição original (RN-11) | 🟢 |
| RF-17 | Simulação gráfica na viewport enquanto o usuário mexe na barra ou nas opções: eixo de giro ou trilho, arco/curso de abertura e a folha na posição atual; ao encostar em parede ou objeto a folha para no contato e o ponto de batida é destacado (RN-11a) | Must | Porta de giro a 20 cm da parede lateral: a barra para no ângulo do contato, a folha aparece encostada e o aviso cita a parede | 🟢 |
| RF-18 | "Desconverter" devolve a malha como estava antes | Must | Desconverter um agregado perfurado remove o furo e deixa a malha solta na mesma posição (RN-12) | 🟡 |
| RF-19 | Propriedades do agregado: pai, face, posição na face, afastamento, perfurar, "Peça de produção", e limites mín./máx. de cada campo | Should | O painel mostra os limites calculados pelo tamanho do pai (RN-13) | 🟡 |
| RF-20 | Agregados (e folhas de porta convertidas) entram no "Salvar como módulo" | Should | Módulo salvo com puxador importado como agregado traz o puxador ao ser inserido | 🟡 |

**C. Reposicionar (amplia o Mover Sobre da 002)**

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-21 | A janela **"Mover Sobre"** da 002 (nome mantido) ganha os recursos do Reposicionar numa janela só, mantendo as vistas Planta baixa e Vista frontal e os alvos de alinhamento por clique | Must | Arrastar o móvel até a referência abre a mesma janela "Mover Sobre", com as duas vistas, os alvos de 002 e os campos novos de RF-22..RF-27 | 🟢 |
| RF-22 | Campos X, Y e Z de deslocamento com prévia | Must | Digitar X = 150 mm move o móvel 150 mm em X na prévia e nas duas vistas | 🟢 |
| RF-23 | Campo de rotação em graus em torno do eixo vertical, com prévia | Must | 90° gira o móvel em torno do próprio centro de base e as vistas acompanham | 🟡 |
| RF-24 | "Passo do teclado": setas e Page Up/Down movem o móvel pelo passo escolhido | Should | Passo 10 mm: seta direita soma 10 mm em X | 🟡 |
| RF-25 | "Visualizar posição relativa": liga mostra os campos como distância à referência; desliga mostra a posição absoluta na cena | Must | Alternar não move o objeto, só muda os números exibidos | 🟡 |
| RF-26 | Posições salvas: guardar a posição relativa atual com nome e reaplicar a outro par móvel/referência | Should | Posição "nicho centrado" salva num quarto aplicada no outro dá o mesmo resultado relativo | 🔴 |
| RF-27 | Botão Substituir: troca o objeto móvel por outro módulo do catálogo mantendo posição e rotação | Could | Substituir um aéreo de 80 por um de 60 mantém o canto de referência | 🔴 |
| RF-28 | Plano de inserção: com botão direito sobre uma face, "Usar como plano de inserção"; novas inserções e movimentos usam esse plano (RN-17) | Should | Escolher a face lateral de um painel faz o próximo módulo entrar apoiado nela | 🟡 |
| RF-29 | Painel de propriedades organizado em Arranjo, Modelos, Movimentação e Propriedades para o objeto selecionado | Should | Selecionar um módulo mostra as quatro seções; Movimentação traz posição, rotação e passo | 🟡 |
| RF-30 | Mostrar dimensões, limites mín./máx. e grade do objeto selecionado | Should | Um módulo paramétrico mostra largura com mín./máx.; um agregado mostra os limites do pai | 🟡 |
| RF-31 | Cotas da cena ligadas ao objeto se atualizam após confirmar o reposicionamento | Should | A cota da lateral até a parede muda de 30 para 45 cm depois de mover 15 cm | 🟡 |
| RF-32 | Confirmar gera um passo de desfazer; Cancelar ou Esc devolve tudo; salvar o arquivo mostra aviso de sucesso ou de falha | Must | Ctrl+Z depois de confirmar volta a posição anterior; falha de gravação mostra mensagem e não diz "salvo" | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Prévia de arraste, barra de abertura e campos do Reposicionar respondem em até 100 ms numa cena com 200 módulos | `docs/elicitação-requisitos-reposicionamento-3d.md#12` (RNF-01) | 🟡 |
| Desempenho | Perfurar usa recorte não destrutivo e não recalcula durante o arraste se a cena ficar lenta (recorte aplicado ao soltar) | RN-10; risco R-06 da elicitação | 🟡 |
| Precisão | Posições e limites com erro ≤ 0,1 mm; abrir e fechar a folha 10 vezes volta à pose original com erro ≤ 0,01 mm | RNF-02 da elicitação; `pivot_math.py` | 🟡 |
| Consistência | Toda operação confirmada é um passo de desfazer; cancelar não deixa resto (objetos de prévia, handlers) | `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-01); CLAUDE.md (handlers) | 🟢 |
| Compatibilidade | Blender 5.2; propriedades lidas por atributo; diferenças de versão só em `compat.py`; arquivos do usuário via `extension_path_user` | CLAUDE.md "Regras do código" | 🟢 |
| Segurança | Importação só lê arquivos escolhidos pelo usuário; nenhum script embutido no modelo importado é executado | Política de extensões do Blender (`[permissions] files`) | 🟡 |
| Usabilidade | Textos de UI em português; o gesto de botão direito tem também um botão no painel (alternativa descobrível) | Risco R-05 da elicitação; regra do repositório | 🟢 |
| Observabilidade | Falhas de importação, conversão e gravação aparecem no relatório do Blender com o motivo | RNF-07 da elicitação; bug #4 (erro ao salvar no Windows sem diagnóstico) | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Personalizar e salvar módulo (RF-02, RF-04, RF-06, RF-07)
  Dado um aéreo de 80 cm com 2 portas lisas e 1 prateleira
  Quando troco as portas por vidro, o puxador por perfil, coloco 2 prateleiras e salvo como "Aéreo vidro 2P"
  Então o módulo aparece na biblioteca do usuário com miniatura
  E inserido num arquivo novo ele vem com vidro, perfil e 2 prateleiras

Cenário: Estilo abaixo do mínimo (RF-03)
  Dado uma porta de 12 cm de largura
  Quando aplico o estilo 5 peças com montantes de 7 cm
  Então a porta continua lisa e vejo a mensagem de tamanho mínimo

Cenário: Agregado limitado ao pai (RF-12, RF-13, RF-14)
  Dado uma malha importada convertida em agregado da lateral de um roupeiro
  Quando arrasto o agregado para além da borda da lateral
  Então ele para na borda
  E ao digitar Afastamento -30 mm numa lateral de 18 mm o campo mostra -18 mm

Cenário: Perfurar e desconverter (RF-15, RF-18)
  Dado um agregado afundado 10 mm com Perfurar ligado
  Quando desconverto o agregado
  Então o pai volta inteiro, sem furo
  E a malha fica solta na mesma posição

Cenário: Folha de porta importada (RF-16)
  Dado uma malha de porta convertida em folha com eixo à esquerda
  Quando arrasto a barra de abertura até 100%
  Então a folha gira 90° em torno do eixo esquerdo
  E ao voltar a 0% ela fecha exatamente na posição original

Cenário: Folha bate na parede (RF-16, RF-17)
  Dado uma porta convertida com giro à direita, máximo 180°, e uma parede a 30 cm da dobradiça
  Quando arrasto a barra de abertura até 100%
  Então a folha para encostada na parede e a barra fica presa no ângulo do contato
  E o painel avisa "Folha bateu em Parede"

Cenário: Furo só visual por padrão (RF-15)
  Dado um agregado afundado com Perfurar ligado e "Furo real no plano de corte" desmarcado
  Quando gero o plano de corte
  Então a peça pai sai sem usinagem

Cenário: Reposicionar com campos e cancelar (RF-21, RF-22, RF-32)
  Dado o nicho arrastado com botão direito até o painel e a janela Reposicionar aberta
  Quando digito X = 150 mm e rotação 90° e clico Cancelar
  Então o nicho volta exatamente à posição e rotação de antes
  E nenhum passo de desfazer é criado

Cenário: Posição relativa x absoluta (RF-25)
  Dado a janela Reposicionar aberta
  Quando desligo "Visualizar posição relativa"
  Então os campos mostram a posição na cena e o objeto não se move

Cenário: Converter sem pai ou sem malha (RF-12, RF-16)
  Dado nenhum objeto de malha selecionado, ou só a malha sem um elemento pai
  Quando aciono "Converter em agregado" ou "Converter em folha de porta"
  Então o botão fica indisponível ou o relatório diz o que falta selecionar
  E nada na cena é alterado

Cenário: Personalizar sem módulo selecionado (RF-01)
  Dado nenhum módulo selecionado
  Quando abro o painel "Personalizar módulo"
  Então o painel mostra "Selecione um módulo" e nenhuma seção de edição
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01..RF-07, RF-09 | Must | Pedido central do bug #5; sem salvar como módulo a personalização se perde a cada projeto |
| RF-08, RF-10 | Should | Proteção e gestão da biblioteca; há a pasta como alternativa |
| RF-11..RF-18 | Must | Agregados, folha de porta e a simulação com batida são o segundo pedido explícito do titular |
| RF-19, RF-20 | Should | Melhoram a precisão e o reuso, com alternativa manual |
| RF-21..RF-23, RF-25, RF-32 | Must | Núcleo do fluxo Reposicionar da elicitação (CA-01, CA-02, CA-03) |
| RF-24, RF-28..RF-31 | Should | Aceleram o uso diário; o Mover Sobre da 002 já cobre o caso básico |
| RF-26, RF-27 | Could | Evidência fraca no vídeo (🔴); entram se sobrar fôlego |
| Colaboração, login, orçamento, exportação de imagem | Won't | Fora do escopo da elicitação (§3.2) |

**Orçamento de esforço:** a feature tem 32 RF em três blocos independentes. O plano deve fatiar em incrementos
entregáveis na ordem A (personalização + salvar) → B (agregados + folha de porta) → C (Reposicionar), cada um com o
próprio teste de fumaça, em vez de um único lote.

## 9. Esclarecimentos

### Sessão 2026-10-07

- **Q:** Quais formatos de importação são obrigatórios (RF-11)? **R:** OBJ, FBX e glTF/GLB pelos importadores do Blender, mais objetos trazidos por outros addons de importação (a conversão aceita qualquer malha da cena).
- **Q:** "Perfurar" aparece onde (RF-15)? **R:** No 3D sempre; no plano de corte e na exportação de produção só se o usuário marcar "Furo real no plano de corte".
- **Q:** Reposicionar e Mover Sobre são uma janela ou duas (RF-21)? **R:** Uma janela só, mantendo o nome "Mover Sobre".
- **Q:** Quais bibliotecas recebem Personalizar e Salvar como módulo no primeiro incremento? **R:** Todas: frameless, face frame, closets e os módulos paramétricos `btm`.
- **Q:** Como a folha de porta convertida se move (RF-16)? **R:** Giro com ângulo máximo configurável por folha e porta de correr com curso configurável, com simulação gráfica durante o movimento; ao chegar no limite entre a folha e a parede, a folha simula a batida e não avança mais.

## 10. Lacunas

- 🟡 Pontos da elicitação mantidos fora desta versão: autosave, multiusuário, atalhos alternativos ao botão direito além do botão no painel, leitor de tela (perguntas 17, 18, 21 da §16).
- 🟡 Risco de escopo: "todas as bibliotecas" (Q4) multiplica o trabalho de A por quatro modelos de dados diferentes (frameless, face frame, closets, `btm`). O plano deve ter um adaptador por biblioteca e entregar uma de cada vez, com teste de fumaça próprio.
- 🟡 Colisão da folha (RN-11a) é teste de varredura do arco/curso contra a cena; o plano define a precisão (passo angular) e o custo em cenas grandes.
- 🟡 "Mobi Editor" e botões flutuantes (D-24 da 002) não fazem parte desta feature e ficam para a próxima numeração.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-requirements` a partir do bug #5 e da elicitação do Reposicionar | reversa |
| 2026-10-07 | `/reversa-clarify`: 5 respostas integradas (importação, Perfurar, janela única "Mover Sobre", todas as bibliotecas, giro/correr com batida) | reversa |

## Pendências de Qualidade

- Q-010 (parcial): os cenários Gherkin cobrem os RF centrais de cada bloco (RF-01..RF-07, RF-12..RF-18,
  RF-21, RF-22, RF-25, RF-32). Os demais RF têm critério de aceite verificável na tabela da seção 5; os cenários
  completos ficam para o `onboarding.md` do `/reversa-plan`.
