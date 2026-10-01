# Requirements: Add-on de Móveis Planejados e Design de Interiores (paridade Promob)

> Identificador: `001-addon-moveis-planejados`
> Data: `2026-10-01`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Entregar ao projetista de móveis planejados, dentro do Blender, o fluxo de trabalho completo do Promob: ambiente, catálogo
de módulos, configuração de dimensões por linha de produto, edição e posicionamento precisos, acabamentos e estilos,
inspeção de aberturas, documentação técnica e produção (lista de peças, plano de corte, exportação). Inclui criar móveis
prontos e guardá-los numa biblioteca do usuário para reuso. Resolve a fragmentação do legado: duas camadas de modelo
(`btm_*` × Home Builder), padrões americanos em polegadas e plano de corte que ignora os gabinetes reais. Absorve os
7 pedidos da issue #20 do Home Builder 5.

> **Siglas.** MDF/MDP: chapas de fibra/partículas de madeira; BP: baixa pressão (revestimento melamínico); ABNT/NBR: normas técnicas brasileiras; ID: identificador; kerf: espessura consumida pela serra; refilo: margem aparada das bordas da chapa; veio: sentido da textura da madeira; agregado: componente interno de um módulo.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/soul.md#1-propósito` | Extensão Blender 5.2 de marcenaria paramétrica, fork do Home Builder 5, "fluxo estilo Promob" para o Brasil | 🟢 |
| `_reversa_sdd/soul.md#4-lacunas` | L1: plano de corte não lê gabinetes legados; L2: convivência `btm_*` × Home Builder | 🔴 |
| `_reversa_sdd/domain.md#1-glossário-de-domínio` | Ambiente, parede, abertura, plano de inserção, módulo, chapa, refilo (10 mm), kerf (4 mm), veio | 🟢 |
| `_reversa_sdd/domain.md#23-regras-de-otimização-de-plano-de-corte` | Corte guilhotinado, precedência de área | 🟢 |
| `_reversa_sdd/architecture.md#3-modelo-de-entidades-e-relacionamentos-erd` | Entidades de cena, parede, abertura, gabinete e configurações | 🟢 |
| `_reversa_sdd/frameless/requirements.md` | Carcaça, vãos, frentes, sobreposição, estilos, bancada, molduras (44 regras) | 🟢 |
| `_reversa_sdd/closets/requirements.md` | Roupeiros no sistema 32 mm, caixas de gaveta por sistema | 🟢 |
| `_reversa_sdd/product_common/requirements.md` | Motor de portas, perfis, eletrodomésticos | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md` | Inserção modal, vãos livres, digitação de medidas | 🟢 |
| `_reversa_sdd/hb_layouts/requirements.md` | Pranchas, cotas automáticas, carimbo | 🟢 |
| `_reversa_sdd/catalog_molding/requirements.md` | Molduras por ambiente; catálogo latente a substituir | 🟢 |
| `_reversa_sdd/traceability/code-spec-matrix-legacy.md` | 110 arquivos legados mapeados | 🟢 |
| `_reversa_sdd/*/questions.md` (rodadas 1 e 2) | 76 decisões de produto já tomadas: preset BR padrão alternável com EUA, construção brasileira, produção a partir de todas as linhas, motor único de molduras, biblioteca única de módulos | 🟢 |
| `docs/rag/promob/` | Manual de Treinamento Promob indexado (32 capítulos) | 🟢 |
| `promob_pacote_completo.zip:documentos/analise_requisitos_promob*.md` (v1–v4) | RF01–RF115, RN01–RN54, RNF01–RNF51, UC01–UC-N32, CA01–CA105 observados em 6 vídeos | 🟢 observado / 🟡 derivado |
| `promob_pacote_completo.zip:documentos/casos_uso_criterios_configuracao_dimensoes_promob.md` | UC-DIM-01..13, CA-DIM-001..049 do Configurador de Dimensões | 🟢 / 🟡 |
| `promob_pacote_completo.zip:configuracoes/PROMOBCONFIGURAÇÃOMEDIDASMEMOVEIS.xml` | `DIMENSIONEXPORT` com 692 atributos `ID/VALUE` em 8 linhas (ALT, PROF, BAN, COZ, DOR, ESC, GAV, SAL) | 🟢 |
| `evidencias/issue20-configurador-dimensoes.png` (imagem da issue #20) | Tela do Configurador de Dimensões do Promob: árvore `Medidas Máximas` / linha → `Dimensões Externas`, `Chapas` (17 componentes), `Componentes`; por chapa: Material, Largura e Comprimento Máximos, Espessura e Fita Borda 1–4 | 🟢 |
| Issue `CreativeDesigner3D/home_builder_5#20` | Blender 5.2; unidades mm/cm na pré-visualização; pt-BR; configuração de dimensões com imagem de referência; gerador de plano de corte; exportação JSON global; limites de chapa MDF | 🟢 |

Situação atual dos itens da issue #20 no código: Blender 5.2 (`blender_manifest.toml`, mínimo 5.2.0) 🟢 feito;
pt-BR (`data/i18n.py`) 🟢 parcial; unidades m/cm/mm (`Scene.btm_settings.btm_unit`) 🟢 parcial, não aplicadas às bibliotecas
legadas; presets de dimensão (`data/dimensions_preset.py`) 🟡 sem imagem e sem configurador; chapa MDF
(`BTM_PG_MDFSheetConfig`, 2750×1830) 🟢 parcial, sem limite por peça; plano de corte e JSON (`cutting/`) 🟢 parcial, sem
os gabinetes reais.

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de loja de planejados | Vender o projeto ao cliente com rapidez e precisão | Monta uma cozinha em L, aplica o estilo do cliente, gera pranchas e imagens, diariamente |
| Designer de interiores | Compor ambientes completos com móveis e decoração | Desenha paredes e aberturas, insere módulos e itens decorativos, documenta para a obra, semanalmente |
| Marceneiro / fabricante | Produzir o que foi vendido sem retrabalho | Abre o projeto aprovado, gera a lista de peças e o plano de corte, exporta para a seccionadora, por pedido |
| Configurador de produto (fábrica) | Padronizar medidas, espessuras e montagem das linhas | Ajusta o Configurador de Dimensões da linha Cozinhas, salva e distribui a configuração, mensalmente |
| Projetista experiente | Reaproveitar soluções | Salva um gaveteiro customizado como móvel pronto na biblioteca e reutiliza em outro cliente |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** Toda medida é armazenada numa unidade interna única e exibida/digitada na unidade escolhida pelo usuário
   (mm, cm ou m; padrão mm), com vírgula decimal aceita; nenhum campo converte silenciosamente (`0,4` nunca vira `4`). 🟢
   - Origem: `_reversa_sdd/hb_core/questions.md` (Q-08), issue #20, Promob RN09/RNF04.
   - Tipo: alterada (o legado mistura polegadas e metros).
2. **RN-02:** Há um **preset de medidas** ativo por projeto: Brasil (padrão) ou EUA, alternável; todos os padrões das linhas
   de produto vêm do preset, nunca de constantes no código. 🟢
   - Origem: `_reversa_sdd/product_common/questions.md` (Q-06). Tipo: nova.
   - Valores do **Padrão Brasil** embutido (clarify C-3): inferior 720 mm sem tampo × 550 mm de profundidade; aéreo com
     350 mm de profundidade instalado a 1500 mm do piso; torre 2200 mm; rodapé 100 mm com recuo de 50 mm; caixa 15 mm;
     portas e frentes 18 mm; fundo 6 mm; fita de borda 0,4 mm nas bordas visíveis. Ajustáveis no Configurador. 🟢
3. **RN-03:** Construção brasileira padrão: laterais passantes; chapa 15 ou 18 mm escolhida por peça; fundo 6 mm encaixado
   em rasgo (ou parafusado) com recuo configurável; sobreposição total = espessura − 1,5 a 2 mm. 🟢
   - Origem: `_reversa_sdd/frameless/questions.md` (Q-04); Promob `DIMENSIONEXPORT` (`*_ESP_*=15`, `*_AVA_FUN`, `*_REB_FUN`).
   - Tipo: alterada (legado usa chapa 19,05 mm e fundo de chapa cheia).
4. **RN-04:** Os parâmetros de dimensão pertencem a uma **linha de produto** (Cozinhas, Dormitórios, Banheiros, Salas,
   Escritórios, Bancadas, Gavetas, globais) e não se misturam entre linhas. 🟢
   - Origem: Promob RN04/RN05, UC-DIM-01.
5. **RN-05:** Cada parâmetro declara tipo, unidade, valor padrão, mínimo, máximo, incremento, precisão, opções válidas,
   significado do zero, se aceita negativo, dependências e imagem de referência. 🟡
   - Origem: Promob RF18, UC-DIM-03, registro mínimo por parâmetro.
6. **RN-06:** Valor fora do domínio é rejeitado com mensagem que informa campo, valor, unidade e faixa permitida; a
   geometria anterior é preservada (nada é aplicado parcialmente). 🟢
   - Origem: Promob RF54–RF57, RN27/RN28 ("Valor Inválido").
7. **RN-07:** Alterar um parâmetro recalcula todas as peças dependentes de todos os módulos afetados, numa única operação
   que pode ser desfeita. 🟡
   - Origem: Promob RF16, RN02, UC-DIM-06; `_reversa_sdd/frameless/questions.md` (Q-06, Q-10).
8. **RN-08:** Projeto, configuração de dimensões, estilo de acabamentos e móvel da biblioteca são quatro artefatos
   distintos, com formatos e escopos documentados. 🟡
   - Origem: Promob RF50, RNF38.
9. **RN-09:** Acabamento é por componente (caixa externa, caixa interna, portas/frentes, tampas, fitas de borda, divisórias,
   prateleiras, puxadores, bancada); trocar a textura nunca altera dimensão nem peça de fabricação sem regra explícita. 🟢
   - Origem: Promob RF63–RF64, RN31, RN37, RNF36.
10. **RN-10:** Um **estilo** guarda a associação componente → acabamento e é aplicado a um escopo explícito (seleção,
    projeto, linha ou novos módulos); incompatibilidades são listadas, nunca ignoradas. 🟢
    - Origem: Promob RF72–RF75, RN34–RN36.
11. **RN-11:** Substituir um módulo por outro de dimensão diferente aplica a dimensão válida mais próxima e informa a
    diferença (original, aplicada, tolerância); o usuário pode confirmar, cancelar ou escolher outra opção. 🟢
    - Origem: Promob RF59–RF61, RN29/RN30 (alerta "Atenção").
12. **RN-12:** Arranjo linear repete um item ao longo de X, Y ou Z; o modo "entre limites" distribui uniformemente sem mover
    os limites; um item editado depois do arranjo vira exceção marcada e preservada. 🟢
    - Origem: Promob RF35–RF39, RN17–RN20.
13. **RN-13:** Com "Evitar Sobreposição" ligado, nenhum módulo ocupa o espaço de outro ou atravessa paredes; desligado,
    sobrepor é permitido e as cotas totais são exibidas. 🟢
    - Origem: `_reversa_sdd/hb_placement/questions.md` (Q-08); manual Promob §3.8 "Colisão".
14. **RN-14:** Abrir portas e gavetas é inspeção e não altera o estado salvo; ausência de aviso de colisão não equivale a
    aprovação quando não há detector automático ativo. 🟢
    - Origem: Promob RN38, RN48, RN51.
15. **RN-15:** Prateleira **fixa** divide a abertura e o fundo; prateleira **móvel** não divide; divisórias e prateleiras
    têm recuos frontal/traseiro configuráveis. 🟢
    - Origem: `_reversa_sdd/closets/questions.md` (Q-07, Q-10); manual Promob §10.10.1.
16. **RN-16:** A **lista de peças** é gerada das peças reais de todos os módulos do projeto (todas as linhas de produto), com
    dimensões de corte, espessura, material, fita de borda por lado e sentido do veio. 🟢
    - Origem: `_reversa_sdd/soul.md#4-lacunas` (L1); `_reversa_sdd/frameless/questions.md` (Q-08); issue #20.
    - Tipo: alterada (o legado sintetiza peças a partir das dimensões externas).
17. **RN-17:** Nenhuma peça excede o limite da chapa configurada (descontados refilo e kerf); peça maior é sinalizada como
    "dimensão incompatível com a chapa" antes do plano de corte. 🟢
    - O plano de corte separa as chapas por **matéria-prima + espessura + acabamento/cor** (clarify C-2; manual Promob
      §23.1: chapas "separadas por abas, que exibem o acabamento, a matéria-prima e a espessura").
    - Origem: issue #20 ("Configure MDF dimensions limit"); Promob Cut "Item com dimensões incompatíveis";
      `_reversa_sdd/domain.md#12-entidades-de-produção-plano-de-corte`.
18. **RN-18:** Cada módulo e cada peça tem um **identificador único estável** entre recálculos, usado na lista de peças, no
    plano de corte, nas etiquetas e na exportação. 🟢
    - Origem: `_reversa_sdd/face_frame/questions.md` (Q-08); manual Promob §23.7 "ID Único".
19. **RN-19:** Um **móvel pronto** salvo na biblioteca guarda geometria, parâmetros, acabamentos, agregados e uma miniatura;
    ao ser inserido, vira um módulo editável independente do original. 🟡
    - Origem: pedido do usuário; manual Promob §6.4 "Favorito de Modulação"; `_reversa_sdd/catalog_molding/questions.md` (Q-01).
    - Tipo: nova.
20. **RN-20:** Bancadas, molduras e geometrias estáticas não acompanham automaticamente os módulos: ficam marcadas como
    "desatualizadas" quando um módulo de referência muda e são refeitas sob comando. 🟢
    - Origem: `_reversa_sdd/frameless/questions.md` (Q-05); `_reversa_sdd/catalog_molding/questions.md` (Q-04).
21. **RN-21:** Dados do cliente e dados da empresa/projetista autora são registros separados; os da empresa persistem entre
    projetos; os do cliente podem ser limpos antes de compartilhar o arquivo. 🟢
    - Origem: `_reversa_sdd/hb_core/questions.md` (Q-11); manual Promob §2.2.2.
22. **RN-22:** Toda operação que altera o projeto pode ser desfeita; cancelar um diálogo ou modal restaura o estado anterior
    sem deixar objetos órfãos. 🟢
    - Origem: Promob RF23, RF83, RNF43; CLAUDE.md (operadores com undo).
23. **RN-23:** O **Configurador de Dimensões é o padrão global da empresa** por linha de produto (cozinha, dormitório,
    banheiro…): todo módulo da biblioteca — de fábrica ou móvel pronto do usuário — tira dele medidas externas, materiais,
    espessuras, limites de chapa, folgas, recuos e fitas de borda. Alterar e confirmar uma definição propaga para os módulos
    existentes do projeto (RN-07): antes de aplicar, o sistema mostra quantos módulos serão alterados e pede uma única
    confirmação. Medidas editadas à mão num módulo são preservadas e marcadas por padrão; a confirmação oferece a opção
    de **sobrescrever também as medidas manuais** (clarify C-4). 🟢
    - Origem: resposta do usuário em §9 (D-3); `evidencias/issue20-configurador-dimensoes.png`; manual Promob §6.1.1.
    - Tipo: nova.
24. **RN-24:** Cada componente de chapa (lateral, divisória, base, fundos, traseira, travessas, prateleira, portas/frentes,
    painel para portas, frentes de gaveta interna e de forno/micro, tampo, tamponamento, painel, especial) declara material,
    largura máxima, comprimento máximo e espessura da chapa, e a fita de borda de cada um dos 4 lados numerados — lados
    **1 e 2 = bordas do comprimento** da peça, **3 e 4 = bordas da largura**, convenção única para todas as peças e fixa na
    ilustração de cada componente (clarify C-1). O limite
    padrão é a chapa menos o refilo (2750 × 1830 − 2·10 = 2730 × 1810 mm). 🟢
    - Origem: `evidencias/issue20-configurador-dimensoes.png`; `DIMENSIONEXPORT` (`*_L_*=2730`, `*_C_*=1810`, `*_ESP_*`,
      `*_MAT_*`, `*_FIT_*_1A..4A`); `_reversa_sdd/domain.md#12-entidades-de-produção-plano-de-corte`.
    - Tipo: nova.
25. **RN-25:** O **preço de venda** de um módulo = preço base (por m² da chapa conforme material, espessura e acabamento;
    por módulo; ou por unidade, para acessórios) acrescido das margens da linha de produto e das condições de pagamento. 🟢
    - Origem: resposta do usuário em §9 (D-2); manual Promob §20.6–20.8.
    - Tipo: nova.

## 5. Requisitos Funcionais

Rastreabilidade: `P:` = IDs da análise Promob (v1–v4 e UC-DIM); `#20` = issue do Home Builder 5; `R1/R2` = decisões das
rodadas de perguntas em `_reversa_sdd/*/questions.md`.

### 5.1 Plataforma, idioma e unidades (issue #20)

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-001 | Funcionar no Blender 5.2 ou superior, sem chamadas de API inexistentes nessa versão | Must | Verificador de API sem itens desconhecidos; teste de fumaça em modo sem janela passa (#20) | 🟢 |
| RF-002 | Toda a interface, mensagens e documentação em português do Brasil, com inglês como alternativa | Must | Nenhum texto de interface novo sem tradução pt-BR (#20) | 🟢 |
| RF-003 | Exibir e aceitar medidas em mm, cm ou m em painéis, cotas, rótulos de pré-visualização e campos digitáveis | Must | Trocar a unidade atualiza cotas e pré-visualizações sem reabrir o arquivo (#20; R1 CORE-08, PL-03) | 🟢 |
| RF-004 | Preset de medidas Brasil/EUA por projeto, alternável | Must | Novo projeto nasce no preset Brasil com os valores de RN-02 (inferior 720×550 mm, caixa 15 mm…); trocar para EUA altera padrões de novos módulos sem mudar os existentes (R1 PC-06; C-3) | 🟢 |

### 5.2 Projeto e ambiente

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-010 | Criar, abrir e salvar projeto com vários ambientes | Must | Reabrir mostra o mesmo estado de módulos, dimensões, posições, camadas, acabamentos e arranjos (P: RF01, RF44, RF81) | 🟢 |
| RF-011 | Registrar dados do cliente e da empresa/projetista em seções separadas | Must | Dados da empresa reaparecem num novo projeto; "limpar dados do cliente" remove só os do cliente (R1 CORE-11) | 🟢 |
| RF-012 | Construir paredes retas e curvas com espessura e pé-direito, e aberturas (portas, janelas) | Must | Padrões do preset Brasil: pé-direito 2,60 m, parede 150 mm, porta 800×2100 mm (R1 CORE-07) | 🟢 |
| RF-013 | Inserir obstáculos de instalação (tomadas 4×2/4×4, pontos de água, esgoto, gás, quadro, colunas/vigas) | Should | Catálogo de obstáculos brasileiro em mm (R1 CORE-12) | 🟢 |
| RF-014 | Ocultar e restaurar camadas (paredes, teto, piso) sem excluir nem alterar cotas | Should | Parede oculta não muda nenhuma medida (P: RF30, RF48) | 🟢 |
| RF-015 | Vista Dinâmica: focar uma região e aplicar corte anterior/posterior sem alterar a geometria; restaurar a vista anterior | Should | Coordenadas e dimensões iguais antes e depois (P: RF84, RF85, RF111) | 🟢 |
| RF-016 | Modos de visualização com e sem textura, com contorno, só linhas visíveis e linhas ocultas | Should | Alternar o modo não altera o modelo (R1 LY-02) | 🟢 |

### 5.3 Biblioteca de módulos e inserção

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-020 | Biblioteca única de módulos em níveis (linha → família → subfamília), com miniaturas, gerada das linhas de produto reais | Must | Caminho tipo `Cozinhas > Superiores > Diversos > Nicho` navegável; nenhum item sem modelo real (P: RF02, RF03; R2 CM-01) | 🟢 |
| RF-021 | Busca rápida por nome na biblioteca | Should | Digitar parte do nome lista os itens e seus caminhos (manual Promob §4.10) | 🟢 |
| RF-022 | Inserir módulo por arraste ou duplo clique num plano de inserção (piso, parede, módulo, geometria), com pré-visualização da posição | Must | Contorno de inserção visível; módulo vinculado ao plano escolhido (P: RF04, RF40; manual §4.2) | 🟢 |
| RF-023 | Preencher vão livre na parede com um ou mais módulos de largura igual | Should | Vão de 1,8 m com largura máxima 0,9 m → 2 módulos de 0,9 m (R2 FL) | 🟢 |
| RF-024 | Substituir módulo por outro do catálogo aplicando a dimensão válida mais próxima, com aviso da diferença | Should | Mensagem informa original, aplicada e diferença; cancelar mantém o original (P: RF58–RF62) | 🟢 |
| RF-025 | Consultar e editar os agregados (componentes internos) de um módulo | Should | Lista de agregados com seleção individual (P: RF08) | 🟢 |

### 5.4 Biblioteca do usuário — móveis prontos

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-030 | Salvar um módulo ou um grupo de módulos como **móvel pronto** na biblioteca do usuário, com nome, descrição, categoria e miniatura | Must | Item aparece na biblioteca e sobrevive a reiniciar e a atualizar a extensão (pedido do usuário; manual §6.4) | 🟡 |
| RF-031 | Gerar a miniatura posicionando o item e escolhendo enquadramento e iluminação, ou automaticamente | Should | Miniatura salva junto do item (R1 LY-06) | 🟢 |
| RF-032 | Escolher se as dimensões e posições de agregados modificados são mantidas no móvel salvo | Should | Opção registrada no item (manual §6.4, etapa 3) | 🟢 |
| RF-033 | Organizar a biblioteca do usuário em categorias e subcategorias; renomear, editar e remover itens | Must | Mover item de categoria não altera o item | 🟡 |
| RF-034 | Inserir móvel pronto como módulo independente e editável | Must | Alterar o inserido não altera o salvo nem outros inseridos (RN-19) | 🟡 |
| RF-035 | Exportar e importar itens da biblioteca do usuário para outro computador | Should | Pacote importado aparece com miniaturas e categorias | 🟡 |
| RF-036 | Móvel pronto inserido adota materiais, espessuras, folgas e fitas da definição ativa, mantendo suas medidas externas e composição | Must | Gaveteiro salvo com lateral 15 mm, inserido num projeto com lateral 18 mm, nasce com 18 mm (RN-23) | 🟡 |

### 5.5 Seleção, edição e posicionamento

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-040 | Painel de propriedades com dimensões, acabamentos, agregados, aberturas e movimentação do item selecionado | Must | Selecionar no 3D carrega as propriedades (P: RF07, RF26) | 🟢 |
| RF-041 | Editar largura, altura e profundidade com atualização imediata do 3D | Must | Edição visível em até 200 ms ou indicador de processamento (P: RF33, RF34; RNF01) | 🟢 |
| RF-042 | Rejeitar valores fora do domínio com "Valor Inválido" detalhado | Must | Mensagem com campo, valor, unidade, faixa; geometria preservada (P: RF54–RF57) | 🟢 |
| RF-043 | Mover, rotacionar, duplicar e excluir módulos; reposicionar por arraste; trocar de plano de inserção | Must | Mover não perde dimensões, agregados nem vínculo com o catálogo (P: RF05, RF06, RF27, RF29) | 🟢 |
| RF-044 | Posição absoluta e relativa (X/Y/Z) e cotas relativas (anterior, posterior, inferior, superior, afastamento) editáveis | Must | Definir cota anterior 75 mm posiciona o módulo a 75 mm do vizinho (P: RF28, RF41, RF43; R1 PL-03) | 🟢 |
| RF-045 | Deslocar por valor e por setas com incremento configurável | Should | Seta move pelo incremento; Ctrl+seta ocupa todo o espaço livre (manual §4.5) | 🟢 |
| RF-046 | Alternador "Evitar Sobreposição" | Must | RN-13 (R1 PL-08) | 🟢 |
| RF-047 | Medir distância entre dois pontos com unidade e pontos destacados | Must | Medida exibida na unidade do usuário (P: RF31, RF32) | 🟢 |
| RF-048 | Arranjo linear em X/Y/Z com quantidade, espaçamento e modo "entre limites"; exceções individuais preservadas | Should | 4 prateleiras "entre" num vão de 1000 mm ficam equidistantes; editar uma a marca como exceção (P: RF35–RF39, RF49) | 🟢 |
| RF-049 | Agrupar e desagrupar módulos explicitamente | Should | Fusão automática desligada por padrão (R2 FF-11) | 🟢 |

### 5.6 Configurador de Dimensões (issue #20)

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-050 | Abrir o Configurador de Dimensões com árvore `Medidas Máximas` e, por linha (Cozinhas, Dormitórios, Banheiros, Salas, Escritórios, Bancadas), os grupos `Dimensões Externas`, `Chapas` e `Componentes` (sarrafo, rodapé, moldura…), com busca | Must | Árvore carrega os valores da definição ativa; busca por nome encontra o parâmetro (P: RF11, RF12; UC-DIM-01, 02; imagem da issue #20) | 🟢 |
| RF-050a | Manter várias **definições** nomeadas (ex.: "ME MOVEIS - COZ. ESCR.") e escolher a ativa; criar, duplicar, renomear, excluir, importar e exportar definições | Must | Trocar a definição ativa mostra "N módulos serão atualizados" e, após confirmar, reaplica o padrão; a opção "incluir medidas manuais" também as sobrescreve (RN-23; C-4) | 🟢 |
| RF-051 | Exibir para cada parâmetro: rótulo, código, valor, unidade, faixa, precisão, descrição e **imagem de referência** que destaca a medida | Must | Selecionar "recuo do fundo" mostra a imagem com a cota destacada (#20; P: RF17, RF18; UC-DIM-03) | 🟢 |
| RF-052 | Editar alturas e profundidades por tipo de módulo (inferior, aéreo, torre, ilha), espessuras, folgas, avanços, recuos e rebaixos | Must | Mudar a altura dos inferiores de 720 para 700 mm atualiza todos os inferiores (P: RF13; manual §6.1.2) | 🟢 |
| RF-053 | Por componente de chapa (RN-24): material, largura máxima, comprimento máximo, espessura e **fita de borda dos 4 lados**, com ilustração que numera os lados | Must | Lateral com fita 0,4 mm só no lado 4 gera a peça com fita apenas numa borda da largura (lados 1–2 = comprimento, 3–4 = largura; C-1) (P: RF14; UC-DIM-07; imagem da issue #20) | 🟢 |
| RF-054 | Escolher montagem da caixa, tipo de fundo, travessas, fechamentos, frentes e construção de gavetas | Must | Trocar "fundo encaixado" por "pregado" atualiza imagem e peças (P: RF15; UC-DIM-08, 09) | 🟢 |
| RF-055 | Recalcular todas as peças dependentes ao confirmar uma alteração | Must | RN-07 (P: RF16; UC-DIM-06) | 🟡 |
| RF-056 | Revisar alterações pendentes (valor anterior/novo/impacto) antes de confirmar; cancelar restaura o último estado válido | Must | Lista de pendências; cancelar não deixa estado parcial (UC-DIM-10, 13) | 🟢 |
| RF-057 | Salvar a configuração com nome; abrir, validar e aplicar a outro projeto compatível | Must | Configuração de Dormitórios aplicada a projeto de Cozinhas é recusada com mensagem (P: RF20–RF22; UC-DIM-11, 12) | 🟢 |
| RF-058 | Importar o arquivo `DIMENSIONEXPORT` do Promob (`.xml`/`.dimensionExport`) como uma definição: mapear as famílias confirmadas (`C`/`L` = limites de chapa, `ESP`, `MAT`, `FIT_1A..4A`, alturas/profundidades globais `ALT_*`/`PROF_*`) e listar os códigos não reconhecidos | Should | Arquivo de 692 atributos vira a definição "ME MOVEIS - COZ. ESCR."; relatório mapeados × não reconhecidos; nada é perdido na reexportação | 🟢 confirmadas / 🟡 demais |
| RF-059 | Limites de chapa por componente (RN-24) e `Medidas Máximas` globais | Must | Lateral de 2800 mm com comprimento máximo 2730 mm é sinalizada antes do plano de corte (#20; RN-17) | 🟢 |
| RF-059a | Módulos da biblioteca (de fábrica e móveis prontos) seguem a definição ativa ao serem inseridos | Must | Com a lateral configurada em 18 mm, todo módulo inserido nasce com lateral de 18 mm (RN-23) | 🟢 |

### 5.7 Construtor de módulos e internos

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-060 | Montar módulos com vãos iguais por padrão, divisórias e prateleiras fixas/móveis, gavetas, portas, internos e fundo | Must | Largura total = laterais + vãos + divisórias; redimensionar mantém os internos (manual §6.2.3; RN-15) | 🟢 |
| RF-061 | Portas simples, duplas, basculantes e de correr; frentes lisas e com moldura; puxadores posicionados por regra | Must | Porta dupla divide o vão com folga configurada | 🟢 |
| RF-062 | Gavetas com caixa por sistema de corrediça (catálogo de dados) | Must | Abertura de 115 mm com sistema que exige 110 mm escolhe a caixa compatível (R2 CL-06) | 🟢 |
| RF-063 | Roupeiros no sistema 32 mm, com prateleiras e varões encaixados na furação | Should | Prateleira posicionada em 12,95 + n·32 mm (R2 CL) | 🟢 |
| RF-064 | Cantos em L e ilhas | Should | Canto em L com duas portas articuladas | 🟢 |
| RF-065 | Eletrodomésticos com medidas brasileiras e painéis/nichos para eletros | Should | Fogão, cooktop, geladeira e lava-louças com medidas do preset BR (R1 PC-06) | 🟢 |

### 5.8 Geometria livre

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-070 | Construir geometria retangular por pontos de referência no ambiente, com pré-visualização e cancelamento | Must | Cancelar não cria objeto (P: RF51, RF86–RF88) | 🟢 |
| RF-071 | Configuração de construção: face (por cima/por baixo) e material antes de confirmar | Must | Peça criada com a face e o material escolhidos (P: RF89–RF94) | 🟢 |
| RF-072 | Editor de perfil 2D: selecionar pontos e segmentos; editar comprimento, ângulo e X/Y | Must | Ângulos e unidades declarados; perfil atualiza o 3D (P: RF53, RF95–RF101) | 🟢 |
| RF-073 | Validar o perfil (aberto, autointersecção, segmento degenerado) antes de aplicar; preservar a última versão válida | Must | Perfil inválido não é aplicado e o erro aponta o segmento (P: RF100–RF104) | 🟡 |
| RF-074 | Geometria livre entra na lista de peças quando marcada como peça de fabricação | Should | Sanca de MDF aparece na lista de peças com material e espessura | 🟡 |

### 5.9 Acabamentos e estilos

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-080 | Aplicar acabamento por componente (RN-09) com atualização visual imediata | Must | Trocar "Externo Caixas" para "Pau Ferro" não altera portas (P: RF63–RF66) | 🟢 |
| RF-081 | Aplicar acabamento em lote a uma seleção múltipla, com resultado por item | Must | Itens incompatíveis listados; nenhum falha em silêncio (P: RF67–RF69) | 🟢 |
| RF-082 | Criar, renomear, aplicar e remover estilos com escopo explícito | Must | RN-10; nome duplicado pede confirmação (P: RF72–RF77) | 🟢 |
| RF-083 | Definir regra de acabamento para novos módulos | Should | Novo módulo inserido já nasce com o estilo da regra (P: RF70, RF71) | 🟡 |
| RF-084 | Catálogo de acabamentos por fabricante (MDF BP nacionais) como dados, com nome, código e origem | Should | Acabamento mostra nome, linha e fabricante (P: RF65, RF92; RNF44) | 🟡 |

### 5.10 Inspeção

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-090 | Abrir e fechar portas e gavetas (individual ou todas) para inspeção, sem alterar o estado salvo | Must | Salvar com portas abertas reabre fechado, salvo escolha explícita (P: RF09, RF78; RN-14) | 🟢 |
| RF-091 | Detectar interferência entre o envelope de abertura de portas/gavetas e outros objetos | Should | Porta que bate numa sanca é sinalizada com objeto e local (P: RF10, RF107) | 🟡 |
| RF-092 | Sinalizar interseções inválidas (prateleira atravessando lateral, módulo fora do ambiente) | Should | Aviso com os objetos envolvidos (P: RF47) | 🟡 |

### 5.11 Documentação técnica

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-100 | Pranchas em papel ABNT (A4–A0) e escalas métricas, com protótipos reutilizáveis e carimbo NBR ligado aos dados do projeto | Must | Carimbo preenche cliente, projetista, escala, data e "Folha N de M" (R1 LY-03, LY-04) | 🟢 |
| RF-101 | Documentação automática: vistas por parede com cotas automáticas, planta baixa e indicadores de vista | Must | Selecionar as paredes do cômodo gera um documento por vista (R1 LY-05, LY-08) | 🟢 |
| RF-102 | Cotas manuais (linear, alinhada, angular, raio) e textos com campos do projeto | Should | Texto com campo "cliente" mostra o nome cadastrado | 🟢 |
| RF-103 | Renderização de imagens do projeto para apresentação | Should | Imagem gerada com a iluminação do ambiente | 🟡 |

### 5.12 Produção (issue #20)

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-110 | Gerar a lista de peças do projeto a partir das peças reais de todos os módulos e geometrias de fabricação | Must | Cozinha com 3 linhas de produto gera todas as peças com ID único, dimensões, espessura, material, bordas e veio (RN-16, RN-18; #20) | 🟢 |
| RF-111 | Gerar o plano de corte agrupando chapas por matéria-prima, espessura e acabamento/cor, respeitando refilo, kerf, veio e dimensão máxima de corte | Must | Peças de MDF 18 mm Branco e MDF 18 mm Cinza Fóssil caem em chapas diferentes; chapas listadas com aproveitamento, nº de peças e cortes (#20; `_reversa_sdd/domain.md#23`; C-2) | 🟢 |
| RF-112 | Indicar sobras reaproveitáveis e marcar o plano como desatualizado quando o projeto muda | Should | Alterar um módulo marca o plano; "atualizar" refaz (manual Promob §23.1) | 🟢 |
| RF-113 | Exportar o projeto num **JSON global** documentado (projeto, ambientes, módulos, peças, materiais, bordas, furações, plano) para ferramentas externas | Must | Arquivo valida contra o esquema publicado; reimportável sem perda (#20) | 🟢 |
| RF-113a | Exportar a lista de peças em **CSV genérico** (uma linha por peça: ID, módulo, nome, componente, comprimento, largura, espessura, quantidade, matéria-prima, acabamento, fitas 1–4, veio), importável pelos otimizadores de corte | Must | Arquivo abre numa planilha com vírgula decimal e separador `;`, uma linha por peça (C-5) | 🟢 |
| RF-114 | Gerar furação 32 mm (pinos, minifix, dobradiças, corrediças) por peça | Should | Lateral de roupeiro lista furos com posição, diâmetro e profundidade (R2 CL-02) | 🟡 |
| RF-115 | Imprimir etiquetas por peça com ID único e plano de corte | Could | Etiqueta com ID, dimensões, material e bordas (manual §23.6) | 🟡 |

### 5.13 Complementos

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-120 | Molduras de ambiente (rodapé, sanca, roda-teto, perfil de LED) por pacote, com motor único para todas as linhas | Should | Pacote de rodapé aplicado a cozinha e roupeiro (R2 CM-02, CM-03, CM-05) | 🟢 |
| RF-121 | Bancadas por corrida de parede e ilha, com recortes de cuba e cooktop | Should | Bancada contínua com recorte no cooktop (`_reversa_sdd/frameless/requirements.md`) | 🟢 |
| RF-122 | Itens decorativos sem orçamento, editáveis | Could | Item da biblioteca "Decore" não entra na lista de peças (manual §2.3.2.1) | 🟢 |
| RF-123 | Cadastro de preços: por m² de chapa (material, espessura, acabamento), por módulo e por unidade (acessórios, puxadores, aramados) | Should | Módulo de MDF 18 mm Branco calculado pela área das peças × preço do m² (RN-25; manual §20.6) | 🟢 |
| RF-124 | Margens por linha de produto, com acesso restrito e ocultas nos relatórios ao cliente | Should | Relatório do cliente mostra só o preço final (manual §20.7) | 🟡 |
| RF-125 | Condições de pagamento (à vista, parcelado, entrada) aplicadas ao total | Should | Total recalculado ao trocar a condição (manual §20.8) | 🟢 |
| RF-126 | Relatórios de orçamento (por ambiente, por módulo, resumo) com dados do cliente e da empresa | Should | Relatório gerado em PDF/planilha com logotipo da empresa (manual §20.3, §4.14.6.1) | 🟢 |
| RF-127 | Itens extras orçados sem aparecer no 3D (instalação, frete, acessórios avulsos) e geração do pedido | Could | Item extra soma no total e entra no pedido (manual §12.3, §20.9) | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Edição dimensional refletida no 3D em até 200 ms; acima de 1 s, indicador de processamento | Promob RNF01, RNF20, RNF31 | 🟡 |
| Desempenho | Plano de corte de 300 peças gerado em até 10 s | Escala típica de cozinha completa; meta a medir | 🟡 |
| Precisão | Medidas guardadas e exibidas sem arredondamento silencioso; precisão declarada por campo (0,1 mm padrão) | Promob RNF04, RNF25, RNF39 | 🟢 |
| Integridade | Nenhuma peça duplicada, sem dimensão ou com vínculo quebrado após recálculo | Promob RNF03, RNF41, RNF50 | 🟢 |
| Reversibilidade | Toda operação pode ser desfeita; cancelar não deixa objetos órfãos | Promob RNF43, RN-22; CLAUDE.md | 🟢 |
| Persistência | Salvamento atômico; arquivos da biblioteca e configurações do usuário fora da pasta da extensão | Promob RNF08; CLAUDE.md (pasta do usuário da extensão) | 🟢 |
| Compatibilidade | Projetos de versões anteriores abrem com migração; arquivos de configuração versionados | Promob RNF09; `_reversa_sdd/hb_core/questions.md` (Q-02) | 🟢 |
| Rastreabilidade | Acabamento, configuração e estilo registram nome, código, origem e versão | Promob RNF11, RNF44 | 🟡 |
| Acessibilidade | Estados e erros comunicados por texto e ícone, nunca só por cor | Promob RNF13, RNF19 | 🟢 |
| Localização | Vírgula decimal e unidade explícita em todas as telas e arquivos | Promob RNF04, RNF05; #20 | 🟢 |
| Manutenibilidade | Catálogos, parâmetros, acabamentos, sistemas de ferragem e pacotes de moldura como dados editáveis, não código | Promob RNF14; R2 FF-06, CL-06 | 🟢 |
| Privacidade | Dados do cliente identificados e removíveis antes de compartilhar o arquivo | R1 CORE-11 | 🟢 |
| Robustez | Funcionar sem janela (modo em lote) para exportações e testes | `_reversa_sdd/hb_layouts/requirements.md` | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Unidade do usuário em cotas e pré-visualização (issue #20)
  Dado um projeto com unidade "cm"
  Quando o usuário insere um balcão de 800 mm
  Então a pré-visualização e as cotas exibem "80 cm"
  E digitar "75,5" aplica 755 mm

Cenário: Vírgula decimal não é perdida
  Dado o parâmetro "fita de borda" com valor 0,4 mm
  Quando o usuário salva e reabre a configuração
  Então o valor continua 0,4 mm e não 4 mm

Cenário: Configurador com imagem de referência (issue #20)
  Dado o Configurador de Dimensões da linha Cozinhas aberto
  Quando o usuário seleciona "recuo do fundo"
  Então a imagem de referência destaca essa medida
  E o painel mostra unidade, faixa permitida e valor padrão

Cenário: Valor fora do domínio
  Dado a largura de um balcão com faixa de 300 a 1200 mm
  Quando o usuário digita 1500
  Então aparece "Valor Inválido: largura deve estar entre 300 e 1200 mm"
  E o balcão mantém a largura anterior

Cenário: Recalcular dependentes
  Dado 6 inferiores com lateral de 15 mm
  Quando o configurador muda a lateral para 18 mm e confirma
  Então todas as peças dependentes dos 6 inferiores são recalculadas
  E um único "desfazer" restaura os 6

Cenário: Configuração de outra linha
  Dado uma configuração salva da linha Dormitórios
  Quando o usuário tenta aplicá-la a um projeto de Cozinhas
  Então a aplicação é recusada com a mensagem de linha incompatível

Cenário: Salvar móvel pronto na biblioteca
  Dado um gaveteiro customizado com 4 gavetas e acabamento "Cinza Fóssil"
  Quando o usuário salva como móvel pronto na categoria "Escritório"
  Então o item aparece na biblioteca com miniatura
  E continua disponível após reiniciar o Blender e atualizar a extensão

Cenário: Móvel pronto é independente
  Dado o móvel pronto "Gaveteiro 4G" inserido duas vezes
  Quando o usuário altera a largura do primeiro
  Então o segundo e o item da biblioteca permanecem inalterados

Cenário: Substituição com dimensão diferente
  Dado um vão de 486 mm ocupado por um balcão
  Quando o usuário o substitui por um modelo disponível em 480 e 500 mm
  Então é aplicada a largura de 480 mm
  E o aviso informa original 486 mm, aplicada 480 mm, diferença 6 mm

Cenário: Arranjo entre limites
  Dado um nicho com altura interna de 1000 mm
  Quando o usuário faz um arranjo de 4 prateleiras no modo "entre limites"
  Então as prateleiras ficam equidistantes e os limites não se movem

Cenário: Evitar Sobreposição
  Dado o alternador "Evitar Sobreposição" ligado
  Quando o usuário arrasta um módulo contra outro
  Então o módulo para no limite do vizinho

Cenário: Estilo com componente incompatível
  Dado um estilo que define acabamento para "Puxadores"
  Quando é aplicado a um módulo sem puxador
  Então o módulo aparece na lista de incompatibilidades e os demais recebem o estilo

Cenário: Geometria livre cancelada
  Dado o modo de construção de geometria ativo com um retângulo em pré-visualização
  Quando o usuário cancela
  Então nenhum objeto é criado

Cenário: Perfil autointersectante
  Dado o editor de perfil de uma sanca
  Quando um ponto é movido criando autointersecção
  Então a alteração não é aplicada e o segmento problemático é destacado

Cenário: Inspeção de portas não altera o projeto
  Dado portas abertas para inspeção
  Quando o usuário salva e reabre
  Então as portas aparecem fechadas

Cenário: Lista de peças de todas as linhas (issue #20)
  Dado um projeto com módulos de cozinha, roupeiro e uma sanca de MDF
  Quando o usuário gera a lista de peças
  Então todas as peças reais aparecem com ID único, dimensões, espessura, material, bordas e veio

Cenário: Peça maior que a chapa (issue #20)
  Dado uma chapa de 2750 × 1830 mm com refilo de 10 mm
  Quando uma lateral de 2800 mm é enviada ao plano de corte
  Então a peça é marcada como incompatível com a chapa antes da otimização

Cenário: Exportação JSON global (issue #20)
  Dado um projeto com plano de corte gerado
  Quando o usuário exporta o JSON global
  Então o arquivo valida contra o esquema publicado
  E reimportá-lo reproduz as mesmas peças e o mesmo plano

Cenário: Chapas separadas por acabamento
  Dado peças de MDF 18 mm Branco e de MDF 18 mm Cinza Fóssil
  Quando o plano de corte é gerado
  Então as peças de cada acabamento ficam em chapas diferentes

Cenário: Aplicar definição com medidas manuais
  Dado 6 balcões, um deles com largura editada à mão
  Quando o usuário aplica uma nova definição
  Então o sistema informa "6 módulos serão atualizados" e pede confirmação
  E, sem a opção "incluir medidas manuais", a largura editada é preservada
  E, com a opção marcada, ela também é substituída pelo padrão

Cenário: CSV de peças
  Dado uma lista de peças gerada
  Quando o usuário exporta o CSV
  Então cada peça ocupa uma linha com medidas, matéria-prima, acabamento, fitas 1–4 e veio

Cenário: Plano de corte desatualizado
  Dado um plano de corte gerado
  Quando a largura de um módulo muda
  Então o plano é marcado como desatualizado até ser refeito
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-001..RF-004 (plataforma, pt-BR, unidades, preset) | Must | Base de tudo; itens da issue #20 |
| RF-010..RF-012, RF-020, RF-022, RF-040..RF-044, RF-046, RF-047 | Must | Fluxo mínimo de projeto observado em todos os vídeos |
| RF-030, RF-033, RF-034 (móveis prontos) | Must | Pedido explícito do usuário |
| RF-050..RF-057, RF-059 (Configurador de Dimensões e limite de chapa) | Must | Centro da paridade com o Promob; issue #20 |
| RF-060..RF-062, RF-070..RF-073, RF-080..RF-082, RF-090 | Must | Construção, geometria livre e acabamentos observados |
| RF-100, RF-101, RF-110, RF-111, RF-113, RF-113a | Must | Documentação e produção; issue #20 |
| RF-013..RF-016, RF-021, RF-023..RF-025, RF-031, RF-032, RF-035, RF-045, RF-048, RF-049, RF-058, RF-063..RF-065, RF-074, RF-083, RF-084, RF-091, RF-092, RF-102, RF-103, RF-112, RF-114, RF-120, RF-121 | Should | Importantes, com alternativa manual |
| RF-036, RF-115, RF-122, RF-123 | Could | Acessórios ou dependentes de decisão |
| RNF de desempenho | Should | Metas a medir com protótipo |
| RNF de precisão, integridade, reversibilidade, localização | Must | Erros aqui inviabilizam fabricação |
| RF-123..RF-127 (orçamento) | Should | Confirmado pelo usuário (§9, D-2); entra no incremento 4 |

**Incrementos de entrega** (decisão D-1, §9):

| Incremento | Conteúdo | Requisitos |
|---|---|---|
| 1 — Fundação e produção | Plataforma, pt-BR, unidades, preset BR; Configurador de Dimensões (definições, chapas, limites, fitas, imagem de referência, importação do `DIMENSIONEXPORT`); lista de peças, plano de corte e JSON global das linhas frameless e closets | RF-001..RF-004, RF-050..RF-059a, RF-110..RF-113a |
| 2 — Biblioteca e móveis prontos | Biblioteca única de módulos, busca, inserção, substituição; móveis prontos do usuário | RF-020..RF-025, RF-030..RF-036, RF-059a |
| 3 — Modelagem, acabamento e documentação | Edição e posicionamento, arranjo, geometria livre, acabamentos e estilos, inspeção, pranchas e cotas automáticas | RF-040..RF-049, RF-060..RF-065, RF-070..RF-074, RF-080..RF-084, RF-090..RF-092, RF-100..RF-103 |
| 4 — Comercial e complementos | Orçamento, furação, etiquetas, molduras, bancadas, decoração; projeto e ambiente avançados | RF-010..RF-016, RF-114, RF-115, RF-120..RF-127 |

## 9. Esclarecimentos

### Sessão 2026-10-01 — `/reversa-clarify`

- **Q (C-1):** Como numerar os lados 1–4 da fita de borda? **R:** a) Pelo comprimento e largura da peça: 1 e 2 = bordas do comprimento, 3 e 4 = bordas da largura, convenção única e fixa na ilustração de cada componente. → RN-24, RF-053.
- **Q (C-2):** Como separar as chapas no plano de corte? **R:** a) Matéria-prima + espessura + acabamento/cor, como o Promob. → RN-17, RF-111.
- **Q (C-3):** Quais valores no Padrão Brasil embutido? **R:** a) Aceitos os propostos (inferior 720×550, aéreo prof. 350 a 1500 do piso, torre 2200, rodapé 100/50, caixa 15, portas 18, fundo 6, fita 0,4). → RN-02, RF-004.
- **Q (C-4):** O que acontece com módulos existentes ao aplicar uma definição? **R:** a) Mostrar a contagem e confirmar uma vez, preservando medidas manuais — **com opção de sobrescrever também as manuais**. → RN-23, RF-050a.
- **Q (C-5):** Saídas de produção além do JSON v2? **R:** a) JSON v2 + CSV genérico de peças. → RF-113a.

### Sessão 2026-10-01 (respostas do usuário no chat)

| ID | Pergunta | Resposta | Efeito |
|----|----------|----------|--------|
| D-1 | Qual é o primeiro incremento entregável? | **Concordo** com a sugestão: (1) unidades, preset BR, Configurador de Dimensões e lista de peças/plano de corte de frameless e closets; (2) biblioteca e móveis prontos; (3) geometria livre, estilos e documentação | Tabela de incrementos em §8; orçamento vai para o incremento 4 |
| D-2 | O orçamento entra no produto? | **Sim** | RF-123 desdobrado em RF-123..RF-127 e RN-25, a partir do manual Promob cap. 20 |
| D-3 | Como tratar a importação do `DIMENSIONEXPORT` (692 códigos)? | As configurações (vistas na imagem da issue #20) **definem o padrão global de dimensões dos módulos de cozinha, dormitório, banheiro etc. da empresa, e todos os módulos da biblioteca seguem esse padrão** | RN-23 e RN-24; RF-050, RF-050a, RF-053, RF-058, RF-059, RF-059a e RF-036 refinados; imagem guardada em `evidencias/`. A tela confirma o significado de `C`/`L` (limites de chapa), `ESP`, `MAT` e `FIT_1A..4A` (fita por lado) |

## 10. Lacunas

- ✅ D-1, D-2 e D-3 respondidas em §9.
- 🟡 Códigos do `DIMENSIONEXPORT` ainda sem significado confirmado (`BD`, `CR`, `CTO`, `ENT`, `AFB`, `ALF`, `CAV`, `RFB`/`RFD`/`RFL`/`RLB`):
  importados como "não reconhecidos" e preservados na reexportação (RF-058); não bloqueiam o incremento 1.
- 🟡 Margens com acesso restrito (RF-124): dentro de um arquivo aberto, a restrição é de interface, não de segurança; validar
  se basta ocultá-las nos relatórios ao cliente.
- 🟡 Pendências herdadas da análise Promob, a validar em testes controlados (não bloqueiam o plano): unidade do
  `DIMENSIONEXPORT` (mm inferido), significado de zero e de `DOR_AVA_FUN=-15`, fórmula exata de "entre limites", tolerância
  da substituição por dimensão mais próxima, existência de detector automático de colisão no Promob.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-01 | `/reversa-clarify` C-1..C-5: convenção dos lados da fita, chapas por acabamento, valores do Padrão Brasil, confirmação com opção de sobrescrever manuais, CSV de peças (RF-113a) | reversa |
| 2026-10-01 | Esclarecimentos D-1..D-3 integrados: incrementos de entrega, orçamento (RF-123..RF-127, RN-25), Configurador de Dimensões como padrão global da empresa (RN-23, RN-24, RF-050a, RF-059a) | reversa |
| 2026-10-01 | Versão inicial gerada por `/reversa-requirements` a partir de `promob_pacote_completo.zip` (análises v1–v4, configuração de dimensões, 6 vídeos), da issue `home_builder_5#20`, do manual Promob (`docs/rag/promob/`) e das 76 decisões das rodadas 1 e 2 | reversa |
