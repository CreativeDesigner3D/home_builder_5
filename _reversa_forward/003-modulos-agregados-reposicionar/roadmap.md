# Roadmap: Módulos personalizáveis, agregados e Reposicionar

> Identificador: `003-modulos-agregados-reposicionar`
> Data: `2026-10-07`
> Requirements: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Cinco incrementos entregáveis em sequência, cada um com teste de fumaça próprio (requirements §8, "orçamento de esforço"):

- **I1. Núcleo + frameless:** contrato único de personalização (`customize/`) com um adaptador por biblioteca, no
  mesmo padrão de `inspection/adapters/`; o primeiro adaptador é o frameless, a biblioteca com mais peças prontas
  (troca de vão, estilos, puxador com posição por frente, interiores). Inclui "Salvar como módulo" genérico.
- **I2. Face frame, closets e `btm`:** os outros três adaptadores, um de cada vez. Cada seção que a biblioteca não
  suporta aparece desabilitada com o motivo (RF-01).
- **I3. Agregados:** conversão de qualquer malha em agregado preso à face de um pai, limites, afastar/afundar,
  Perfurar (3D) e "Furo real no plano de corte" (usinagem no JSON de produção). Inclui a importação OBJ/FBX/glTF.
- **I4. Folha de porta:** malha → folha com giro (máximo por folha) ou correr (curso), barra de abertura, simulação
  gráfica e parada na batida.
- **I5. Mover Sobre ampliado:** rotação, passo do teclado, relativa/absoluta, posições salvas, Substituir, plano de
  inserção e as seções Arranjo/Modelos/Movimentação/Propriedades no painel de propriedades da 002.

Como na 001 e na 002, a matemática fica em Python puro testável com `unittest` (limites do agregado, varredura de
abertura, reposicionamento, manifesto de módulo), e a camada do Blender é fina por cima.

## 2. Princípios aplicados

`.reversa/principles.md` não existe; valem as regras do `CLAUDE.md`:

| Princípio (CLAUDE.md) | Como a feature se relaciona | Status |
|---|---|---|
| Editar só `caffmob_draw/`; consultar o RAG 5.2 | APIs confirmadas: `bpy.ops.wm.obj_import`, `bpy.ops.import_scene.fbx`, `bpy.ops.import_scene.gltf` (`docs/rag/blender-api/corpus/bpy.ops.wm.md#bpy.ops.wm.obj_import`, `.../bpy.ops.import_scene.md`); `bpy.data.libraries.write` já usado no legado | respeita |
| Operadores que alteram dados com `UNDO` | Personalizar, salvar/inserir módulo, converter/desconverter, Perfurar, abrir folha, Mover Sobre: um passo por confirmação | respeita |
| Handlers removidos em todos os caminhos e no `unregister()` | Desenho da simulação da folha (`POST_VIEW`), cache de colisão limpo por `depsgraph_update_post` (`@persistent`), keymap das setas no Mover Sobre | respeita |
| Inputs de GN só via `compat` | Materiais (`Top Surface`, `Bottom Surface`), objeto do puxador (`GeoNodeHardware` "Object"), `CPM_CUTOUT` (`X`, `End X`, `Y`, `End Y`, `Route Depth`) | respeita |
| Propriedades por atributo | Dados novos em `PropertyGroup` (`btm_custom`, `btm_aggregate`, `btm_saved_positions`); idprops legados (`DOOR_STYLE_NAME`, `hb_front_door_style`) só lidos onde o legado já grava | respeita |
| Arquivos do usuário em `extension_path_user` | Módulos salvos em `extension_path_user(pkg, path="modules", create=True)` | respeita |
| Textos em português | Toda UI nova em português | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **Núcleos puros:** `customize/spec.py` (estrutura da personalização por instância: frentes, estilo, puxador, material, divisões; validação; serialização), `aggregates/limits.py` (referencial da face do pai, clamp de U/V, afastamento entre −espessura e +∞), `aggregates/sweep.py` (varredura de abertura com parada no primeiro contato, sobre uma função de teste injetada), `move_over/reposition.py` (rotação em torno do centro da base, passo, relativa ↔ absoluta, posição salva como delta no referencial de B), `customize/manifest.py` (manifesto do módulo salvo) | Matemática e formatos são o maior risco; testes rápidos fora do Blender, como `pivot_math.py` (001) e `walls2d/model.py` (002) | Lógica dentro dos operadores | 🟢 |
| D-02 | **Adaptador por biblioteca** em `customize/adapters/{frameless,face_frame,closets,btm}.py`, registrados como `inspection.fronts._adapters()`. Cada um expõe `capabilities(root)` → por seção `ok` ou motivo; `read(root)` → `spec`; `apply(root, spec)`. A identificação da raiz reaproveita `selection.classify.module_library` e `inspection.fronts.module_root_of` | As quatro bibliotecas têm modelos de dados diferentes (mapeamento: frameless por drivers, face frame e closets reconstroem as frentes a cada recálculo, `btm` é malha única) | Um painel por biblioteca; unificar os modelos | 🟢 |
| D-03 | **Onde a personalização mora:** no **vão** (opening cage), que sobrevive à reconstrução: `Object.btm_custom` (PropertyGroup) com `door_style`, `drawer_style`, `pull_model`, `pull_position`, `front_material`. Peças guardam `btm_custom.material` por nome. Depois de cada reconstrução, o adaptador reaplica o que está no vão. No face frame, grava também `hb_front_door_style`/`hb_front_drawer_style`, que o solver já respeita (`props_hb_face_frame.py:3252-3268`) | Face frame e closets apagam e recriam as frentes no recálculo; gravar na frente perderia a escolha | Gravar na frente; aplicar uma vez só | 🟢 |
| D-04 | **Gancho pós-reconstrução:** cada adaptador registra a reaplicação no ponto de saída do recálculo da biblioteca (frameless: depois de `change_opening_type`/`assign_door_style`; face frame: depois do solver de frentes; closets: fim de `recalculate_closet_starter`; `btm`: fim da regeneração da malha) por uma função `customize.reapply(root)` chamada explicitamente, não por handler global | Previsível e barato; handler `depsgraph_update_post` rodaria em toda mudança | Handler global de depsgraph | 🟡 (pontos exatos de saída confirmados no `/reversa-coding`) |
| D-05 | **Frentes (RF-02):** frameless usa `caffmob_frameless.change_opening_type`; face frame `caffmob_face_frame.change_opening`; closets `caffmob_closets.change_opening` (sem basculante e sem painel: desabilitados com motivo); `btm` mapeia para `btm_cabinet.door_swing` (NONE/LEFT/RIGHT/DOUBLE/FLIP), gavetas `btm` desabilitadas com motivo | Reaproveita a troca de vão que cada biblioteca já faz | Motor de frentes novo | 🟢 |
| D-06 | **Estilo de porta (RF-03) por nome:** frameless resolve nome → índice no momento de aplicar (`assign_style_to_front`), sem gravar índice na personalização; face frame usa `assign_style_to_front(record_override=True)`; closets ganha estilo por frente pelo `fronts_closets.apply_style_to_front` chamado com o estilo do vão; `btm` desabilitado (sem estilos) | RN-06: índice muda quando um estilo é removido (frameless RN-29) | Gravar `DOOR_STYLE_INDEX` | 🟢 |
| D-07 | **Puxador por frente (RF-04):** o vão guarda `pull_model` (nome do arquivo de puxador) e `pull_position`. Frameless: troca o input "Object" do `GeoNodeHardware` `IS_CABINET_PULL` (via `compat`) e os idprops de posição já existentes por frente. Face frame e closets: depois da reconstrução, troca `pull.data` pela malha do modelo escolhido (resolvido pelos `resolve_pull_object` de cada biblioteca) e reposiciona pela regra da frente. `btm`: cria puxador como filho da porta `_Door_L/_R/_Flip` | Hoje o modelo é global por cena nas três bibliotecas (`door_pull_selection`) | Mudar a seleção global (afeta todos os módulos) | 🟡 |
| D-08 | **Material arbitrário por peça ou grupo (RF-05):** grupos = Caixa, Frentes, Fundo, Interno, pela função da peça (`part_roles.classify`, `hb_part_role`, `CABINET_PART`). Peças `GeoNodeCutpart`: `Top Surface`/`Bottom Surface` via `compat`; demais malhas: slot de material. O nome fica em `btm_custom.material` da peça ou do vão e é reaplicado depois da reconstrução (D-04). Veio: preserva o `ROTATED` do legado (frameless RN-25) | Face frame só pinta acabamento/interior do estilo; frameless e closets só por estilo global | Criar estilos novos para cada combinação | 🟡 |
| D-09 | **Divisões internas (RF-06):** frameless usa `change_interior_type`, `custom_interior_vertical/horizontal`; gavetas internas frameless implementam o `TODO` de `_add_rollouts_to_section` (`types_frameless.py:2160/2275`) com a caixa de gaveta já usada pela frente `Drawer`; face frame usa `add_interior_item`/`add_interior_division`/`add_rollout_box`; closets usa `add_adj_shelves`/`add_drawers` (divisória vertical desabilitada com motivo); `btm`: prateleiras geradas em `geometry/mesh_gen.py` (novo parâmetro `shelves`), divisórias e gavetas desabilitadas com motivo | Cobre o pedido sem inventar motor de interiores | Motor de interiores único | 🟡 |
| D-10 | **"Salvar como módulo" genérico (RF-07..RF-10):** extrair a mecânica comum de `frameless/operators/ops_library.py` (coleta de dados, `bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)`, miniatura 256 px) para `customize/library_io.py`, usada pelos quatro adaptadores. Destino: `extension_path_user(pkg, path="modules/<categoria>")`; ao lado do `.blend`, `<nome>.json` (manifesto, `interfaces/user-module-file.md`) com biblioteca, estilos e materiais **por nome** e o `spec` da personalização. Inserir: anexa, re-resolve nomes, reaplica o `spec` pelo adaptador e entra no posicionamento modal já existente. Os operadores antigos de grupo (frameless/face frame) continuam funcionando sem mudança | Reaproveita mecânica testada; manifesto resolve RN-06 e o índice errado ao carregar em outro arquivo (mapeamento §2) | Asset Browser nativo (sem parâmetro e sem reaplicação); salvar só o `.blend` | 🟡 |
| D-11 | **Nome repetido (RF-08):** `invoke_props_dialog` com "Substituir o módulo existente?"; não → cancela sem escrever | RN-05 | Sufixo automático | 🟢 |
| D-12 | **Agregado (RF-12..RF-14):** `Object.btm_aggregate` (PropertyGroup: `parent_ref`, `face` (±X/±Y/±Z do pai), `u`, `v`, `offset`, `perforate`, `real_hole`, `production_part`, `kind` AGGREGATE/LEAF, e o estado original para desconverter). O objeto vira filho Blender do pai (mover/girar/apagar levam junto; apagar o pai pergunta, RF-12). A posição é sempre calculada por `aggregates/limits.py` a partir de `u/v/offset` no referencial da face; o `update` das propriedades aplica o clamp e o campo mostra o valor ajustado (RN-08). Arrastar: modal `caffmob.aggregate_move` restrito ao plano da face, também com clamp | Parentesco nativo dá RN-07 de graça; clamp num lugar só | Constraint `LIMIT_LOCATION` (não conhece a caixa do agregado nem a face) | 🟢 |
| D-13 | **Perfurar 3D (RF-15):** cortador = caixa gerada do volume afundado (não a malha importada, que pode ser pesada), objeto oculto marcado `IS_CUTTING_OBJ` (já excluído do posicionamento, seleção e exportação); modificador `BOOLEAN` DIFFERENCE `EXACT` no pai, depois do GN, como o legado faz em aberturas de parede. Desligar remove modificador e cortador | Não destrutivo; mesmo padrão de `operators/opening_builder.py:391` | Booleana com a malha do agregado (lenta, falha em malhas não fechadas) | 🟢 |
| D-14 | **Furo real (RF-15):** com "Furo real no plano de corte", se o pai é `GeoNodeCutpart`, o agregado adiciona `CPM_CUTOUT` (`GeoNodeCutpart.add_part_modifier`) com `X/End X/Y/End Y` do retângulo afundado e `Route Depth` = profundidade; nome `Agregado: <nome>`. `cutting/` passa a ler esses `CPM_CUTOUT` e exporta em `machining` no JSON (contrato alterado, `interfaces/cut-plan-json.md`). Pai que não é peça de corte: opção desabilitada com motivo | Reaproveita o primitivo de recorte existente; sem marca, a produção não muda (RN-10) | Usinagem só no PDF | 🟡 |
| D-15 | **Agregado como peça de produção (RN-13):** marcado, ganha `btm_geometry.fabrication` e entra por `cutting/part_sources.geometry_records` (caminho já existente da 002) | Sem fonte nova no corte | Fonte nova em `part_sources` | 🟢 |
| D-16 | **Importação (RF-11):** `caffmob.import_model` (`ImportHelper`, filtro `*.obj;*.fbx;*.glb;*.gltf`) chama o importador do Blender pelo sufixo e seleciona o que entrou; escala pela unidade da cena. A conversão aceita qualquer `MESH` da cena, inclusive vindo de outros addons | Esclarecimentos Q1; sem dependência nova | Importador `.skp` próprio | 🟢 |
| D-17 | **Folha de porta (RF-16):** mesmo padrão de `inspection/room_door_leaf.py`: pivô Empty na dobradiça (giro) ou na origem do trilho (correr), com a malha como filha. Giro: eixo esquerdo/direito/topo/base pela caixa da malha, sentido, `max_angle` por folha (90 a 180°). Correr: direção ±X da folha e curso. Novo adaptador `inspection/adapters/aggregate_leaf.py` em `fronts._adapters()`, então "Abrir/Fechar Frentes", o controle giratório e o salvar fechado (`save_guard.py`) valem também para essas folhas | Um controle de abrir só (001/002) | Drivers por folha | 🟢 |
| D-18 | **Máximo por folha:** `pivot_math.clamp_angle` ganha parâmetro opcional `maximum` (padrão `MAX_ANGLE`, comportamento atual preservado); as folhas convertidas passam o seu | Q5 pede máximo configurável; a regra comum de 90° (001 D-20) continua para módulos | Subir o máximo global | 🟢 |
| D-19 | **Batida (RN-11a, RF-17):** `aggregates/sweep.py` anda do valor atual ao pedido em passos de 2° / 1 cm e refina por bissecção até 0,25° / 1 mm; o teste de contato reaproveita `inspection/interference.envelope_hulls` + `BVHTree.overlap` com pré-filtro por caixa, excluindo a própria folha, o pai e o módulo raiz. Fechar não testa. Alvos (BVH) ficam em cache por folha, invalidado por `depsgraph_update_post` (`@persistent`) | Reaproveita a detecção da 001; custo limitado ao trecho percorrido | Física do Blender; testar só o valor final (atravessaria a parede) | 🟡 (custo em cena grande medido na fumaça) |
| D-20 | **Simulação gráfica (RF-17):** `SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_VIEW')` enquanto a folha está selecionada: eixo/trilho, arco ou curso até o máximo, posição atual e ponto de contato em vermelho; aviso "Folha bateu em <objeto>" no painel | Feedback contínuo pedido em Q5 | Objetos de prévia na cena | 🟢 |
| D-21 | **Mover Sobre ampliado (RF-21..RF-27):** mesma janela `caffmob.move_over_dialog` (nome mantido, Q3). Acrescenta: campo Rotação (graus, em torno do centro da base de A), campo Passo, chave "Visualizar posição relativa" (relativa = distâncias atuais a B; absoluta = posição no mundo, só exibição), lista de posições salvas com Salvar/Aplicar, botão Substituir. Setas/Page Up/Down movem pelo passo dentro do modal. `MoveOver` ganha `rotation` e `set_absolute`; matemática em `move_over/reposition.py` | Uma janela só, sem segundo modal | Janela nova | 🟢 |
| D-22 | **Posições salvas (RF-26):** `Scene.btm_saved_positions` (coleção: nome, delta no referencial de B, rotação, lado de B). Aplicar a outro par repete o delta relativo | Persiste no `.blend` do projeto | Preferências do add-on | 🟡 |
| D-23 | **Substituir (RF-27):** abre a busca de módulos da biblioteca do usuário e do catálogo; insere o novo, copia a rotação e encosta o mesmo canto de referência (canto do lado de B mais próximo), apaga o antigo, num passo de desfazer | Pedido 🔴 da elicitação; Could | — | 🔴 |
| D-24 | **Plano de inserção (RF-28):** `WindowManager.btm_insertion_plane` (ativo, matriz da face). Operador `caffmob.set_insertion_plane` no menu de contexto do objeto (raycast no ponto do clique); `hb_placement` usa o plano no lugar de Z = 0 quando não há acerto (RF-04 do placement) até "Limpar plano" | Esse é o único ponto em que o posicionamento já cai num plano | Mudar todos os raycasts | 🟡 |
| D-25 | **Seções Arranjo/Modelos/Movimentação/Propriedades (RF-29, RF-30):** subpainéis do `BTM_PT_ObjectProperties` (002 D-10): Arranjo = pai/filhos/agregados; Modelos = Personalizar módulo (D-02); Movimentação = posição, rotação, passo, plano; Propriedades = dimensões com mín./máx. (limites do agregado vêm de `aggregates/limits.py`) | Reaproveita o painel da 002 | Painel novo | 🟢 |
| D-26 | **Cotas (RF-31):** as cotas da 002 (desenhadas ao selecionar, `measure/cotas.py`) já são recalculadas a cada redesenho, então valem depois de confirmar. Cotas permanentes `GeoNodeDimension` não viram associativas nesta feature | Atende o critério sem motor de cota associativa | Vincular cotas permanentes | 🟡 |
| D-27 | **Aviso ao salvar (RF-32):** handler `save_post` (`@persistent`) mostra "Projeto salvo: <arquivo>" na barra de status; falha de gravação continua com o relatório do Blender e é registrada no console com o caminho e o erro (ajuda o bug #4) | Blender já reporta a falha; falta o sucesso explícito | Salvamento próprio | 🟡 |

## 4. Premissas

Nenhum `[DÚVIDA]` aberto no requirements. Premissas técnicas a confirmar durante a codificação:

| Premissa | Origem | Risco se errada |
|---|---|---|
| Os quatro pontos de saída do recálculo (D-04) são alcançáveis sem mexer no fluxo das bibliotecas | Mapeamento de código | Reaplicar a personalização exigirá handler; mais custo de desempenho |
| O face frame continua fora do plano de corte (`part_sources.iter_modules` não o reconhece) | `cutting/part_sources.py:72` | "Furo real" em peça face frame não chega ao JSON; fica desabilitado com motivo e vira bug separado |
| `bpy.data.libraries.write` grava `PropertyGroup` de objeto (`btm_custom`, `btm_aggregate`) junto com os dados | Comportamento de bloco de dados do Blender | Manifesto passaria a carregar o `spec` como fonte primária (já previsto) |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Personalização de módulo (`customize/`) | — | componente-novo | `spec`, manifesto, `library_io`, quatro adaptadores, painel "Personalizar módulo" |
| Agregados (`aggregates/`) | — | componente-novo | PropertyGroup, limites, conversão/desconversão, mover, Perfurar, furo real, importação |
| Biblioteca do usuário frameless/face frame | `_reversa_sdd/frameless/requirements.md#Regras de Negócio` (RN-44) | regra-alterada | Mecânica de gravação extraída para `customize/library_io.py`; operadores de grupo antigos preservados |
| Interiores frameless | `_reversa_sdd/frameless/requirements.md#Comportamentos desconhecidos` | regra-nova | Gavetas internas implementadas no `TODO` `_add_rollouts_to_section` |
| Inspeção de frentes | `_reversa_forward/001-addon-moveis-planejados/roadmap.md` (D-20, D-25) | regra-alterada | Adaptador `aggregate_leaf`; `clamp_angle(maximum=)`; correr com curso livre |
| Interferência | `inspection/interference.py` | regra-alterada | Usada também para parar a folha no contato (antes só relatório) |
| Mover Sobre | `_reversa_forward/002-editor-parede-mover-sobre/roadmap.md` (D-15, D-16) | regra-alterada | Rotação, passo, relativa/absoluta, posições salvas, Substituir |
| Posicionamento | `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-04) | regra-alterada | Plano de inserção substitui Z = 0 quando ativo |
| Plano de corte (JSON) | `cutting/json_exporter.py` | contrato-alterado | `machining` com recortes de agregados; `drilling` continua vazio |
| Painel de propriedades | 002 D-10 | regra-alterada | Subpainéis Arranjo/Modelos/Movimentação/Propriedades |
| `btm` (módulo paramétrico) | `geometry/mesh_gen.py`, `geometry/door_controller.py` | regra-alterada | Prateleiras na malha, puxador e material nas portas |

## 6. Delta no modelo de dados

- Novos PropertyGroups `Object.btm_custom`, `Object.btm_aggregate`, `Scene.btm_saved_positions`,
  `WindowManager.btm_insertion_plane`; `btm_cabinet` ganha `shelves`; manifesto JSON do módulo salvo; `machining` no
  JSON de produção. Nenhum dado legado é apagado ou migrado.
- Detalhe completo em: `_reversa_forward/003-modulos-agregados-reposicionar/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| JSON de produção (`caffmob_draw.project` 2.x) | arquivo | `interfaces/cut-plan-json.md` |
| Módulo salvo do usuário (`.blend` + `.json`) | arquivo | `interfaces/user-module-file.md` |

## 8. Plano de migração

1. Nenhuma migração de dados: as propriedades novas nascem vazias e os módulos sem `btm_custom` seguem as
   seleções globais como hoje.
2. JSON de produção: `machining` é campo novo e opcional; a versão sobe de `2.0.0` para `2.1.0` (menor), e o leitor
   continua aceitando `2.0.0`.
3. Grupos já salvos em `cabinet_groups/` continuam carregáveis pelos operadores antigos; os novos módulos vão para
   `modules/`.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| "Todas as bibliotecas" multiplica o I2 por três modelos diferentes | alto | alto | Um adaptador por vez, com fumaça própria; seção sem suporte desabilitada com motivo em vez de implementação forçada |
| Reconstrução do face frame/closets apaga a personalização | alto | médio | D-03/D-04: estado no vão e reaplicação no fim do recálculo; teste de fumaça muda a largura e confere |
| Booleana `EXACT` lenta em peças com muitos agregados | médio | médio | Cortador em caixa simples (D-13); recorte aplicado ao soltar o arraste |
| Varredura de colisão lenta em cena grande | médio | médio | Pré-filtro por caixa, cache de BVH, passo grosso + bissecção (D-19); meta de 100 ms (RNF) medida na fumaça |
| Módulo salvo carregado em outro arquivo com estilos ausentes | médio | alto | Manifesto por nome; estilo ausente vira aviso e a frente usa o estilo padrão |
| Face frame fora do plano de corte | médio | certo | Furo real desabilitado em peça face frame; registrar bug separado |
| Escopo total grande (32 RF) | alto | alto | Incrementos I1..I5 com critério de pronto próprio; I5 (Should/Could) pode ser cortado sem afetar I1..I4 |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Testes `unittest` dos núcleos puros (D-01) passando; teste de fumaça por incremento no Blender 5.2
- [ ] `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erro
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-plan` | reversa |
