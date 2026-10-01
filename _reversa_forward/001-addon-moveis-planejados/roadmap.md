# Roadmap: Add-on de Móveis Planejados e Design de Interiores (paridade Promob)

> Identificador: `001-addon-moveis-planejados`
> Data: `2026-10-01`
> Requirements: `_reversa_forward/001-addon-moveis-planejados/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

O produto é entregue em 4 incrementos (requirements §8). Este roadmap detalha o **incremento 1 — Fundação e produção** e
traça os incrementos 2–4 em nível de componente.

O eixo do incremento 1 é um **Padrão de Dimensões** (o "Configurador de Dimensões" do Promob) que vira a fonte única de
medidas, materiais, espessuras, limites de chapa e fitas de borda de todas as linhas de produto. Ele substitui
`BTM_PG_DimensionSettings` e `BTM_PG_ComponentConfig` (`blendertomob/data/properties.py`), guarda definições nomeadas na
cena principal e em arquivos do usuário, e é **sincronizado** com as propriedades de cena das bibliotecas legadas
(`Scene.hb_frameless`, `Scene.hb_closets`) em vez de reescrever essas bibliotecas agora. O preset Brasil/EUA passa a ser
simplesmente uma definição embutida.

A produção deixa de **sintetizar** peças a partir das dimensões externas (`cutting/part_extractor.py`) e passa a ler as
peças reais (`GeoNodeCutpart`: `Length`, `Width`, `Thickness`, `Edge W1/W2/L1/L2`) de frameless e closets, classificadas
por componente, com identificador estável, limite de chapa por componente e exportação num **JSON global v2** documentado.
O algoritmo de nesting atual (`cutting/nesting.py`, ADR `0002`) é mantido.

## 2. Princípios aplicados

Não existe `.reversa/principles.md`. As regras obrigatórias do projeto estão em `CLAUDE.md` e são tratadas como princípios.

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Editar só `blendertomob/` | Todo código novo vai para o pacote da extensão | respeita |
| II. API do Blender confirmada no RAG; `check_api.py` sem `[UNKNOWN in 5.2]` | APIs novas confirmadas: `bpy.utils.extension_path_user`, `bpy.utils.previews.new`, `UILayout.template_icon`, `UILayout.template_list`, `WindowManager.invoke_props_dialog`, `ImagePreview.icon_id` (`docs/rag/blender-api/corpus/`) | respeita |
| III. Diferenças de versão só em `compat.py`; inputs GN via `compat.get_gn_input` | A extração de peças lê `GeoNodeCutpart` por `compat.get_gn_input` — exige consolidar `hb_utils` × `compat` (`_reversa_sdd/hb_core/tasks.md` T-01) antes ou junto | respeita (com dependência) |
| IV. `bpy.props` por atributo; `# type: ignore` | Novos PropertyGroups seguem a convenção | respeita |
| V. Operadores que alteram dados com `UNDO`; `bl_idname` `btm.*` | Aplicar definição, importar, gerar lista de peças: `{'REGISTER','UNDO'}` | respeita |
| VI. Arquivos do usuário em `extension_path_user` | Definições, imagens personalizadas e exportações padrão usam essa pasta | respeita |
| VII. Handlers com `@persistent` e remoção no `unregister()` | Migração em `load_post` e coleção de previews removidas no `unregister()` | respeita |
| VIII. Sem threads tocando `bpy` | Nesting e parser XML rodam no thread principal (volume pequeno) | respeita |
| IX. UI e comentários novos em português | Toda string nova em pt-BR com tradução em `data/i18n.py` | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **Padrão de Dimensões** como modelo de dados próprio: definição → linhas → (dimensões externas, chapas por componente, componentes, medidas máximas) + atributos brutos preservados | Espelha a tela do Promob (imagem da issue #20) e o `DIMENSIONEXPORT`; requirements RN-23/RN-24 | Manter `BTM_PG_DimensionSettings` plano (não comporta linhas nem 17 componentes); usar só presets em Python (não editáveis pelo usuário) | 🟢 |
| D-02 | Metadados dos parâmetros (rótulo, unidade, faixa, passo, precisão, zero, negativo, imagem, código Promob) num **esquema declarativo** em Python (`data/dimension_schema.py`); valores na definição | Separa "o que existe" (código revisado) de "quanto vale" (dado do usuário); RN-05 | Metadados no arquivo do usuário (permite corromper domínios); metadados em `.blend` | 🟢 |
| D-03 | Definições ficam em `Scene.btm_standards` **da cena principal** (`hb_project.get_main_scene`) e podem ser exportadas/importadas como `.btmdim.json` na pasta do usuário | Projeto leva consigo o padrão usado (reabre igual); empresa distribui o padrão por arquivo; decisão FL-09 (cena principal) | Só arquivos externos (projeto não reabre igual); só na cena (sem distribuição) | 🟢 |
| D-04 | Preset Brasil e EUA são **definições embutidas somente-leitura** ("Padrão Brasil", "Padrão EUA (HB5)"); o usuário duplica para editar | Unifica RF-004 e RF-050a; nada de constantes soltas (RN-02) | Enum de preset separado do configurador | 🟢 |
| D-05 | Propagação no incremento 1 por **camada de sincronização** (`standards/sync.py`): aplicar a definição escreve nas props legadas (`Scene.hb_frameless.*`, `Scene.hb_closets.*`) e reaproveita a lógica dos operadores de atualização de gabinetes (`frameless/operators/ops_defaults.py`: `hb_frameless.update_material_thickness_prompts`, `hb_frameless.update_toe_kick_prompts`, `update_cabinet_sizes`), extraída para funções chamáveis sem `bpy.ops`, e o recálculo dos starters de closets | Entrega RN-23 sem reescrever 33 mil linhas de bibliotecas; os módulos passam a seguir o padrão | Reescrever frameless/closets para ler o padrão diretamente (incremento 3+); drivers apontando para a definição (frágeis, `_reversa_sdd/hb_core/questions.md` Q-02) | 🟡 |
| D-06 | Medidas sobrescritas num módulo ficam marcadas (`btm_overrides` por objeto) e a sincronização não as toca, salvo com a opção "incluir medidas manuais" (D-16a) | RN-23; clarify C-4 | Sobrescrever sempre; perguntar módulo a módulo | 🟢 |
| D-07 | Unidade interna continua o metro do Blender; um único formatador/parser em `data/units.py` (vírgula decimal, sufixos `mm`/`cm`/`m`) usado por painéis, cotas, rótulos de pré-visualização e campos digitáveis | RN-01; decisões CORE-08 e PL-03 | Converter o modelo para mm (quebra o legado e o Blender) | 🟢 |
| D-08 | Lista de peças lida das **peças reais** (`GeoNodeCutpart`) via adaptadores por linha (`cutting/part_sources.py`): frameless (`CABINET_PART`), closets (`hb_part_role` `CLOSET_*`), geometria de fabricação; o extrator sintético atual vira fallback para módulos `btm_*` sem peças | RN-16; lacuna L1 de `soul.md`; interface confirmada em `_reversa_sdd/hb_core/node-group-interfaces.md#geonodecutpart` | Continuar sintetizando (errado para qualquer gabinete real); ler a malha avaliada (perde semântica de componente e fita) | 🟢 |
| D-09 | Classificação de peça por **tabela de papéis** (`cutting/part_roles.py`): nome/`hb_part_role` → componente do padrão (lateral, base, fundo…) | O padrão é por componente (RN-24); frameless identifica peças por nome, closets por papel | Classificar por geometria (ambíguo) | 🟡 |
| D-10 | **Identificador estável**: `btm_uid` (UUID) gravado no objeto raiz do módulo na criação ou na primeira extração; ID da peça = `<btm_uid do módulo>/<papel>/<índice>` | RN-18; face_frame Q-08 | `obj.name` (muda ao duplicar/renomear); ponteiro de memória | 🟢 |
| D-11 | Fita por lado: aresta com material atribuído → espessura da `Fita Borda 1..4` do componente, com `Edge L1/L2` → lados 1/2 (comprimento) e `Edge W1/W2` → lados 3/4 (largura) | RN-24; clarify C-1 | Uma espessura única por peça; numeração por posição na peça montada | 🟢 |
| D-12 | Limite de chapa checado por componente **antes** do nesting; peça fora do limite vai para a lista "incompatíveis com a chapa" | RN-17, RF-059 | Deixar o nesting falhar e devolver "não alocadas" | 🟢 |
| D-13 | Nesting atual (Next-Fit Decreasing guilhotinado) mantido; agrupamento passa de (material, espessura) para (matéria-prima, espessura, acabamento) | ADR `_reversa_sdd/adrs/0002-nested-cutlist-algorithm.md`; clarify C-2 | Trocar por maxrects/skyline agora | 🟢 |
| D-14 | **JSON global v2** com esquema publicado e validador mínimo em stdlib (campos obrigatórios, tipos, unidades); importação reconstrói a lista de peças e o plano (não a cena 3D) | Issue #20; RF-113; dependências só stdlib (`_reversa_sdd/dependencies.md`) | Biblioteca externa de JSON Schema (não embarcada); reimportar a cena 3D (fora do escopo) | 🟡 |
| D-15 | Importação/exportação do `DIMENSIONEXPORT` com `xml.etree` (stdlib): famílias confirmadas mapeadas; demais preservadas em `raw_attributes` e reexportadas sem perda | RF-058; D-3 do requirements | Mapear só o conhecido e descartar o resto (perde dados do cliente) | 🟢 confirmadas / 🟡 demais |
| D-16a | Aplicar definição mostra a contagem de módulos afetados e confirma uma vez, com a opção "incluir medidas manuais" que ignora `btm_overrides` | RN-23; clarify C-4 | Confirmar módulo a módulo; nunca tocar manuais | 🟢 |
| D-16 | Configurador como **diálogo com rascunho**: edição numa cópia (`WindowManager.btm_standards_draft`), lista de pendências, e "Aplicar" como um único operador com `UNDO`; "Cancelar" descarta | RF-056; RN-22; UC-DIM-10/13 | Editar direto nas props (sem revisão nem cancelamento) | 🟢 |
| D-17 | Imagens de referência PNG embarcadas por parâmetro (`assets/dimension_refs/<chave>.png`), carregadas numa coleção de `bpy.utils.previews` e exibidas com `template_icon`; ausência mostra aviso | RF-051; issue #20 | Desenhar a ilustração por GPU (custo alto); sem imagem | 🟢 |
| D-18 | Incrementos 2–4 ficam como **esboço**: biblioteca única sobre `hb_assets` + pasta do usuário; móveis prontos consolidando `frameless/operators/ops_library.py` e `face_frame/operators/ops_library.py`; motor único de molduras (`molding/`); orçamento sobre a lista de peças | Requirements §8; decisões R1/R2 | Detalhar tudo agora (planos envelhecem antes da execução) | 🟡 |

## 4. Premissas

O requirements não tem `[DÚVIDA]` pendente. Premissas técnicas adotadas neste plano:

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Os valores dos inputs `Length/Width/Thickness` lidos do modificador (após avaliação do depsgraph) correspondem às dimensões de corte da peça | §5.12 RF-110; D-08 | Lista de peças com dimensões erradas; mitigado por teste que compara com `obj.dimensions` avaliado |
| A presença de material em `Edge W1/W2/L1/L2` indica fita naquele lado em frameless e closets (`L` = comprimento → lados 1/2) | §4 RN-24; D-11; C-1 | Fitas erradas na produção; validar com 3 gabinetes de referência |
| `C_*` = comprimento máximo e `L_*` = largura máxima no `DIMENSIONEXPORT` (1810 / 2730) | §9 D-3; imagem da issue #20 | Limites trocados; o teste de importação confere com a tela |
| A sincronização com `hb_frameless`/`hb_closets` cobre as medidas do padrão que essas bibliotecas consomem hoje | §4 RN-23; D-05 | Algum módulo ignora o padrão; o relatório de sincronização lista parâmetros sem destino |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Padrão de Dimensões (`standards/`) | — | componente-novo | Modelo, esquema de parâmetros, definições embutidas, sincronização, import/export |
| `data/properties.py` (`BTM_PG_DimensionSettings`, `BTM_PG_ComponentConfig`, `BTM_PG_SceneSettings.config_*`) | `_reversa_sdd/architecture.md#3-modelo-de-entidades-e-relacionamentos-erd`; `_reversa_sdd/data/design.md` | componente-extinto (migrado) | Substituídos por `Scene.btm_standards`; migração em `load_post` |
| `data/dimensions_preset.py` | `_reversa_sdd/data/design.md` | componente-extinto (migrado) | Vira a fonte das definições embutidas "Padrão Brasil" |
| `operators/ops_dimensions.py` (`btm.dimension_settings_dialog`) | `_reversa_sdd/operators/design.md` | regra-alterada | Substituído pelo Configurador (`btm.standards_configurator`) |
| `data/units.py` | `_reversa_sdd/data/design.md`; `_reversa_sdd/hb_core/design.md` (fachada `units.py`) | regra-alterada | Parser/formatador único com vírgula e sufixos; usado também pelas bibliotecas legadas |
| `cutting/part_extractor.py` | `_reversa_sdd/cutting/design.md` | regra-alterada | Orquestra adaptadores de peças reais; síntese vira fallback |
| `cutting/part_sources.py`, `cutting/part_roles.py` | — | componente-novo | Leitura de `GeoNodeCutpart` e classificação por componente |
| `cutting/nesting.py` | `_reversa_sdd/cutting/design.md`; ADR 0002 | regra-alterada (pequena) | Recebe chapa por material/espessura do padrão; pré-checagem de limite fica fora (D-12) |
| `cutting/json_exporter.py` | `_reversa_sdd/cutting/design.md` | contrato-alterado | JSON global v1 → v2 com esquema, importação e validação |
| `cutting/csv_exporter.py` | — | contrato-novo | CSV genérico de peças (RF-113a) |
| `operators/ops_cutting.py` | `_reversa_sdd/operators/design.md` | regra-alterada | Gera lista de peças real, mostra incompatíveis, marca plano desatualizado |
| `ui/panels.py` (`BTM_PT_nesting_panel`, `BTM_PT_environment_builder`) | `_reversa_sdd/ui/design.md` | regra-alterada | Entrada do Configurador, seleção de definição ativa, unidade, lista de peças |
| `product_libraries/frameless/operators/ops_defaults.py` | `_reversa_sdd/frameless/design.md` | regra-alterada | Lógica dos operadores extraída para funções chamadas pela sincronização (sem `bpy.ops`); operadores viram atalhos com `UNDO`; resolve os 2 TODO (`update_base_top_construction_prompts`, `update_drawer_front_height_prompts`) |
| `product_libraries/closets/types_closets.py` / `props_closets.py` | `_reversa_sdd/closets/design.md` | regra-alterada | Padrões de espessura/profundidade/rodapé lidos via sincronização |
| `hb_utils.py` × `compat.py` | `_reversa_sdd/hb_core/tasks.md` (T-01) | regra-alterada | Ponte GN consolidada em `compat.py` (pré-requisito de D-08) |
| `data/i18n.py` | `_reversa_sdd/data/design.md` | regra-alterada | Strings novas em pt-BR/en |

## 6. Delta no modelo de dados

- Resumo das mudanças: novo `Scene.btm_standards` (definições → linhas → dimensões externas, chapas por componente com
  fitas de 4 lados, componentes, medidas máximas, atributos brutos); `WindowManager.btm_standards_draft` para edição;
  ID props `btm_uid`, `btm_line`, `btm_component` e `btm_overrides` nos objetos; `NestingPart` ganha `uid`, `component`,
  `edges[4]` e `source`; JSON global v2. `BTM_PG_DimensionSettings` e `BTM_PG_ComponentConfig` são migrados e removidos.
- Detalhe completo em: `_reversa_forward/001-addon-moveis-planejados/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| JSON global v2 (projeto, peças, plano de corte) | arquivo | `_reversa_forward/001-addon-moveis-planejados/interfaces/json-global-v2.md` |
| Definição de Padrão de Dimensões (`.btmdim.json`) | arquivo | `_reversa_forward/001-addon-moveis-planejados/interfaces/dimension-definition.md` |
| `DIMENSIONEXPORT` do Promob (importar/exportar) | arquivo | `_reversa_forward/001-addon-moveis-planejados/interfaces/promob-dimensionexport.md` |
| CSV genérico de peças | arquivo | `_reversa_forward/001-addon-moveis-planejados/interfaces/csv-pecas.md` |
| Pacote de móvel pronto (incremento 2, esboço) | arquivo | `_reversa_forward/001-addon-moveis-planejados/interfaces/user-library-package.md` |

## 8. Plano de migração

1. `load_post` (`@persistent`) detecta `BTM_PG_DimensionSettings`/`config_*` preenchidos e cria uma definição "Migrada de
   <arquivo>" com os valores, marcando-a como ativa; os campos antigos ficam somente-leitura por uma versão e depois saem.
2. Projetos sem nenhuma definição recebem "Padrão EUA (HB5)" como ativa **se** já tiverem gabinetes legados (não muda
   medidas existentes) ou "Padrão Brasil" se forem novos (RN-02, TM-03 de frameless/closets).
3. Na primeira extração de peças, módulos sem `btm_uid` recebem um; nenhum outro dado é alterado.
4. JSON v1 continua importável (lido como v1 e convertido em memória); exportação passa a gerar só v2.
5. `dimensions_preset.py` deixa de ser lido pelas propriedades e passa a gerar a definição "Padrão Brasil".

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Sincronização não cobre todos os parâmetros consumidos pelas bibliotecas | alto | médio | Relatório de sincronização lista parâmetros do padrão sem destino e props legadas sem origem; teste por linha |
| Dimensões lidas do `GeoNodeCutpart` divergem do corte real (sobreposições, entalhes `CPM_*`) | alto | médio | Teste de referência com 3 gabinetes medidos à mão; peças com modificador de recorte marcadas para revisão |
| Classificação por nome de peça frágil (frameless usa nomes em inglês livres) | médio | alto | Tabela de papéis com teste que falha para peça sem papel; marcar peça "sem componente" em vez de adivinhar |
| Aplicar uma definição em projeto grande é lento (recálculo de todos os gabinetes) | médio | médio | Um único `suspend`/lote; indicador de progresso; medir com 60 módulos |
| `hb_utils`/`compat` divergentes quebram a leitura de inputs | alto | baixo | Consolidar antes (T-01 do `hb_core`); teste do extrator em `--background` |
| Códigos não reconhecidos do `DIMENSIONEXPORT` mudam de significado entre versões do Promob | baixo | médio | Preservados brutos; reexportação sem perda; relatório no import |
| Imagens de referência faltando para parâmetros | baixo | alto | Aviso na tela; tarefa explícita de produção das imagens dos parâmetros do incremento 1 |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` do incremento 1 marcadas `[X]`
- [ ] Configurador abre, edita com rascunho, aplica com um único desfazer e propaga aos gabinetes frameless e closets
- [ ] Importar o `PROMOBCONFIGURAÇÃOMEDIDASMEMOVEIS.xml` gera uma definição e reexporta os 692 atributos sem perda
- [ ] Lista de peças de uma cozinha frameless + um roupeiro bate com a contagem e as medidas de referência
- [ ] Peça acima do limite do componente aparece em "incompatíveis" antes do nesting
- [ ] JSON v2 exportado valida no validador e reimporta as mesmas peças e o mesmo plano; CSV de peças abre numa planilha
- [ ] Peças de acabamentos diferentes caem em chapas diferentes
- [ ] Unidade mm/cm/m e vírgula decimal funcionam em painéis, cotas e pré-visualizações
- [ ] `ruff check blendertomob/`, `python3 docs/rag/tools/check_api.py` e o teste de fumaça em `--background` passam
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-01 | Acrescentado o incremento 3, bloco 1 (inspeção e movimento), ao fim do documento | reversa |
| 2026-10-01 | Alinhado ao `/reversa-clarify` C-1..C-5 (D-06, D-11, D-13, D-16a, CSV) | reversa |
| 2026-10-01 | Versão inicial gerada por `/reversa-plan` (incremento 1 detalhado; 2–4 em esboço) | reversa |


---

# Incremento 3 — bloco 1: Inspeção e movimento

> Data: `2026-10-01` · Escopo pedido pelo usuário: controle de abertura de portas (0–90° com paradas em 45°/90°) nas três
> linhas, gavetas e basculantes no mesmo controle, abrir/fechar tudo, salvar fechado, ligar "Evitar Sobreposição" e
> detectar interferência do envelope de abertura · Requisitos: RF-090, RF-091, RF-046, RN-13, RN-14 · Confidência:
> 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA
>
> As ações deste bloco continuam a numeração do `actions.md` (a partir de T048). O incremento 1 acima permanece
> como registro; nada dele é alterado.

## I3-1. Resumo da abordagem

Hoje existem três mecanismos de abertura sem nada em comum, e a cozinha (frameless) não abre:
- **face frame:** `swing_percent` + pivô Empty recriado a cada recálculo (`face_frame/solver_face_frame.py`, `op_open_mode.py`);
- **closets:** idprops 0/1 `hb_door_open`/`hb_drawer_open` com escrita direta de transformação (`closets/types_closets.py`, `op_open_door_closet.py`);
- **camada moderna `btm_cabinet`:** Empty controlador + drivers (`geometry/door_controller.py`);
- **frameless:** sem conceito de abertura.

O bloco cria uma **camada de inspeção** única (`blendertomob/inspection/`). Cada linha ganha um adaptador que
expõe as frentes do módulo (porta, basculante, gaveta, basculante para baixo, pullout) como objetos com um valor
canônico (ângulo em graus para frentes articuladas; fração do curso para gavetas) e sabe aplicar esse valor sem
recalcular o módulo. Sobre ela ficam:
1. um **gizmo de abertura** (dial 3D na dobradiça; seta para gavetas) com paradas em 0°, 45° e 90°;
2. um **modo de inspeção** único (clicar abre/fecha com animação), acessível pelo HUD e pelo painel, com "Abrir tudo" e "Fechar tudo";
3. **salvar fechado** por `save_pre`/`save_post` (RN-14);
4. o detector de **interferência** do envelope de abertura (RF-091), por BVH;
5. o alternador **"Evitar Sobreposição"** (`collision_global`, hoje sem efeito) ligado ao posicionamento (RN-13).

Os operadores legados (`hb_face_frame.open_mode`, `hb_closets.open_door_mode`) continuam registrados como atalhos do
modo único.

## I3-2. Princípios aplicados

`.reversa/principles.md` não existe; valem as regras do `CLAUDE.md`, todas respeitadas:

| Princípio (CLAUDE.md) | Como o bloco se relaciona | Status |
|---|---|---|
| Editar só `blendertomob/`; consultar o RAG 5.2 | Gizmo (`bpy.types.GizmoGroup`, `Gizmos.new`, `Gizmo.target_set_handler`), `bpy.app.handlers.save_pre/save_post`, `mathutils.bvhtree.BVHTree.FromObject/overlap` confirmados no RAG | respeita |
| Handlers com remoção correspondente e `@persistent` | `save_pre`, `save_post`, timer de animação e `draw_handler` do destaque de interferência removidos em todos os caminhos e no `unregister()` | respeita |
| Operadores que alteram dados com `UNDO` | Abrir/fechar é inspeção (RN-14) e fica **sem** `UNDO`, como o `open_mode` legado; o detector e o alternador não alteram geometria. Ver D-24 | respeita (com justificativa) |
| Sem threads tocando `bpy` | Animação por timer do modal no thread principal; BVH no thread principal | respeita |
| Diferenças de versão só em `compat.py` | Nenhuma diferença de versão prevista; se o nome de um tipo de gizmo mudar, vai para `compat.py` | respeita |

## I3-3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|---|---|---|---|---|
| D-19 | Pacote novo `blendertomob/inspection/` com o tipo `Front` (`kind`: `DOOR`, `FLIP_UP`, `FLIP_DOWN`, `DRAWER`, `PULLOUT`; `module_root`, `obj`, `hinge`, `max_value`, `get()`, `apply(valor)`, `commit(valor)`) e um adaptador por linha: `frameless`, `face_frame`, `closets`, `btm` | Um só controle para três mecanismos incompatíveis (survey do código: face frame por pivô, closets por transformação direta, frameless sem abertura) | Reescrever os três mecanismos num modelo único (mexe em ~33 mil linhas e no solver do face frame); um operador por linha (mantém a fragmentação de hoje) | 🟢 |
| D-20 | Valor canônico: **ângulo em graus** (0–90, limite comum a todas as linhas) para frentes articuladas e **fração do curso** (0–1) para gavetas e pullouts. Conversão por adaptador: face frame `swing_percent = graus/100` (`DOOR_MAX_SWING_ANGLE` 100°); closets `frac = graus/110` (`DOOR_OPEN_ANGLE` 110°); `btm` `door_open = graus/90` | O usuário pediu 0–90° com paradas 45°/90°; os máximos legados (100° e 110°) ficam como teto físico e não são expostos | Expor o máximo de cada linha (inconsistente entre linhas); fração para tudo (não fala "graus" ao usuário) | 🟡 |
| D-21 | **Frameless sem novos objetos**: porta gira por `delta_rotation_euler.z` (a origem da peça já é a dobradiça; rotação estática `(90°,-90°,0)`), com sinal pela folha `Left Door`/`Right Door`; gaveta/pullout desliza por `delta_location.y` (o `location.y` já tem driver; a caixa é filha da frente); basculante (`IS_FLIP_UP_DOOR`, origem no canto inferior) gira em torno da aresta superior com `delta_rotation_euler` + compensação em `delta_location` calculada pela matemática de pivô | Não altera a hierarquia nem os drivers de medida; `delta_*` não colide com os drivers de `location`/`rotation` | Criar Empty pivô por porta (muda a hierarquia de todos os gabinetes e o recálculo); driver novo em `rotation_euler` (conflita com recálculo e é frágil, `_reversa_sdd/hb_core/questions.md` Q-02) | 🟢 |
| D-22 | **Face frame e closets reaproveitam o próprio mecanismo**: durante arraste e animação o adaptador aplica a pose sem recalcular (face frame: `front_leaves` com proxy de `swing_percent`, como `_apply_swing`; closets: `apply_door_open`/`apply_drawer_open`) e só **confirma** no fim (`swing_percent` / `hb_door_open`) | Evita o recálculo completo a cada movimento e o defeito de duas animações no mesmo gabinete (o recálculo do face frame recria os pivôs e invalida a outra animação) | Confirmar a cada passo (lento; perde a referência do pivô) | 🟢 |
| D-23 | Closets passam a guardar fração em `hb_door_open`/`hb_drawer_open` (float 0–1); valores 0/1 de arquivos antigos continuam válidos | Ângulos intermediários (45°) exigem estado fracionário; a leitura legada já trata o valor como fração | Manter 0/1 (impede 45°) | 🟡 |
| D-24 | Abrir/fechar **não** entra no histórico de desfazer (`bl_options={'REGISTER'}`, sem `UNDO`); o estado é de inspeção | RN-14: inspeção não altera o projeto; desfazer cheio de "abrir porta" atrapalha | Registrar cada abertura no undo | 🟡 |
| D-25 | **Gizmo de abertura**: `GizmoGroup` `BTM_GGT_front_open` (VIEW_3D/WINDOW, `3D`, `PERSISTENT`), visível com o modo de inspeção ativo ou com uma frente selecionada; `GIZMO_GT_dial_3d` no eixo da dobradiça para articuladas e `GIZMO_GT_arrow_3d` no sentido do curso para gavetas, com `target_set_handler` ligado ao adaptador; o valor **encaixa** em 0°, 45° e 90° quando estiver a até 5° (Ctrl desliga o encaixe) | É o "controle tipo engrenagem" pedido pelo usuário, integrado ao viewport do Blender | Arrastar o Empty controlador (mecanismo `btm` atual: só uma porta, sem paradas); só slider no painel (não é manipulação no 3D) | 🟡 |
| D-26 | **Modo de inspeção único** `btm.inspect_fronts` (modal, timer 60 Hz, 0,35 s, *smoothstep*): clique numa frente alterna 0 ↔ máximo (90° ou curso total); clique durante a animação inverte; Esc/RMB sai confirmando as poses. Registra-se no HUD (`viewport_hud.register_active_modal`, contrato `_exit_requested`). `hb_face_frame.open_mode` e `hb_closets.open_door_mode` viram atalhos dele, e a pílula "Open Door" do closets passa a chamá-lo | Um botão e um comportamento para todas as linhas | Manter três modos | 🟢 |
| D-27 | Operadores `btm.fronts_set_open` (todos / do módulo / selecionados; valor 0°, 45°, 90° ou curso) e botões "Abrir tudo" / "Fechar tudo" / 45° no painel; o botão do HUD deixa de depender da aba do face frame (`_ModalToggleButton.visible`) | RF-090 "individual ou todas" | — | 🟢 |
| D-28 | **Salvar fechado** (RN-14): `save_pre` (`@persistent`) guarda as frentes abertas em memória e fecha todas; `save_post` reabre como estavam. A propriedade `btm_settings.save_fronts_open` (padrão desligado) é a "escolha explícita" do RF-090 para salvar aberto | Critério de aceitação "salvar com portas abertas reabre fechado" sem fechar a vista do usuário | Fechar no `load_post` (o arquivo em disco continuaria aberto; outros programas veriam aberto) | 🟢 |
| D-29 | **Interferência (RF-091)**: o envelope de cada frente é uma malha temporária (BMesh) que varre a frente de 0 ao valor máximo em passos de 15° (articuladas) ou estende a caixa pelo curso (gavetas). Pré-filtro por caixas alinhadas (AABB) e teste fino com `BVHTree.overlap` contra as malhas avaliadas dos outros objetos (paredes, módulos, geometria livre). Excluem-se o próprio módulo e as frentes vizinhas do mesmo vão. Resultado: lista com frente, objeto atingido e ponto (centro dos pares sobrepostos), destaque vermelho no viewport e botão "ir para". Roda pelo operador `btm.check_front_interference` (todo o projeto ou seleção), nunca automaticamente | Atende "porta que bate numa sanca é sinalizada com objeto e local"; sob demanda para não pesar no viewport | Teste só por AABB (falso positivo em L e em paredes inclinadas); booleana (lenta, altera dados); verificar a cada movimento (custo) | 🟡 |
| D-30 | **Evitar Sobreposição** (RN-13, RF-046): `collision_global` passa a valer. Ligado, mantém o comportamento atual de posicionamento (`hb_placement.PlacementMixin.find_placement_gap`, intrusões e recuos). Desligado, o posicionamento ignora vizinhos e intrusões e permite sobrepor, mostrando as cotas totais. Leitura centralizada em `PlacementMixin.avoid_overlap(context)`; o rótulo do painel passa a "Evitar Sobreposição" | Hoje a opção é desenhada mas nenhuma lógica a lê | Implementar colisão 3D genérica no posicionamento (fora do escopo; o detector D-29 cobre a inspeção) | 🟡 |
| D-31 | O handler de plano desatualizado (`cutting/stale.py`) **ignora** mudanças de frentes e pivôs marcados como frente (`IS_CABINET_FRONT`, `IS_DOOR_FRONT`, `hb_part_role` de frente, `FRONT_PIVOT`) e qualquer atualização enquanto a inspeção anima | Abrir uma porta não muda nenhuma peça | Desligar o handler durante a inspeção (perde edições reais feitas ao mesmo tempo) | 🟢 |
| D-32 | Camada `btm` (módulo rápido): o adaptador lê e escreve `btm_cabinet.door_open` via o Empty controlador; corrige a inconsistência do deslocamento `0.03` entre `update_door_geometry_and_controller` e `update_door_rotation_from_property` | Deixa as quatro origens de frente no mesmo controle | Remover o controlador (quebra arquivos existentes) | 🟡 |

## I3-4. Premissas

| Premissa | Origem | Risco se errada |
|---|---|---|
| "Engrenagem de 45–90 graus" significa um controle giratório (dial) no 3D com paradas em 45° e 90°, até 90° | Pedido do usuário no chat (2026-10-01); não está no `requirements.md` | Se for "dobradiça de 45°/90°" como ferragem (catálogo), o gizmo continua útil mas falta o tipo de dobradiça como dado — vira item do incremento 3 (RF-062/catálogo) |
| Limite comum de 90° para todas as linhas, mesmo onde o legado permitia 100°/110° | D-20 | Usuário pode querer ver a porta de canto a 110°; mitigação: o máximo vira preferência simples depois |
| O envelope varrido em passos de 15° basta para detectar a interferência relevante | D-29 | Objetos finos entre dois passos podem escapar; mitigação: passo configurável e checagem também na pose final |

O `requirements.md` deve ganhar o detalhe "controle no 3D com paradas 0/45/90°" no RF-090 (sugestão: `/reversa-clarify`
ou edição do requirements antes do `/reversa-to-do`).

## I3-5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|---|---|---|---|
| Inspeção (novo) | — | componente-novo | `blendertomob/inspection/` (`fronts.py`, `adapters/*.py`, `gizmo.py`, `ops_inspect.py`, `save_guard.py`, `interference.py`, `overlay.py`) |
| frameless (frentes) | `_reversa_sdd/frameless/requirements.md` (frentes, `types_frameless.py` `CabinetDoor`/`CabinetFlipUpDoor`/`CabinetDrawerFront`/`CabinetPulloutFront`) | regra-nova | Frentes passam a abrir por `delta_*`; nada muda no recálculo |
| face_frame (abertura) | `_reversa_sdd/face_frame/` (`op_open_mode.py`, `solver_face_frame.front_leaves`) | regra-alterada | `open_mode` vira atalho do modo único; `TILT_OUT` passa a ser clicável |
| closets (abertura) | `_reversa_sdd/closets/` (`op_open_door_closet.py`, `types_closets.apply_door_open`) | regra-alterada | Estado fracionário; pílula "Open Door" chama o modo único |
| Camada moderna (portas) | `_reversa_sdd/geometry/` (`door_controller.py`) | regra-alterada | Adaptador + correção do deslocamento do controlador |
| hb_placement (posicionamento) | `_reversa_sdd/hb_placement/requirements.md` | regra-alterada | `avoid_overlap` desliga busca de vão e intrusões quando "Evitar Sobreposição" está desligado |
| HUD do viewport | `operators/viewport_hud.py` | regra-alterada | Botão de inspeção visível em todas as linhas |
| cutting (plano desatualizado) | `blendertomob/cutting/stale.py` (incremento 1) | regra-alterada | Ignora frentes |
| ui (painéis) | `_reversa_sdd/ui/` (`ui/panels.py`) | regra-alterada | Bloco "Inspeção": modo, abrir/fechar tudo, 45°, verificar interferência, lista de interferências; "Evitar Sobreposição" |

## I3-6. Delta no modelo de dados

- Novos: `WindowManager.btm_inspection` (estado do modo, encaixe, último relatório de interferência);
  `Scene.btm_settings.save_fronts_open`; idprop `btm_open` (graus ou fração) nas frentes frameless e `btm`;
  `hb_door_open`/`hb_drawer_open` do closets passam a float. Nenhuma mudança em face frame (`swing_percent` já é
  fracionário).
- Detalhe completo em: `_reversa_forward/001-addon-moveis-planejados/data-delta.md` (seção "Incremento 3 — bloco 1").

## I3-7. Delta de contratos externos

Nenhum contrato externo muda: o estado de abertura não entra no JSON global v2 nem no CSV (`interfaces/` inalterado).

## I3-8. Plano de migração

1. Arquivos sem `btm_open`: frentes frameless consideradas fechadas (delta zero), sem escrita no carregamento.
2. Closets com `hb_door_open`/`hb_drawer_open` inteiros: lidos como fração 0,0/1,0.
3. Arquivos salvos abertos antes deste bloco continuam abertos até o próximo salvamento, que já sai fechado (D-28).

## I3-9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|---|---|---|---|
| Recálculo do face frame recria os pivôs durante o arraste do gizmo | alto | média | Adaptador reobtém o pivô pelo papel a cada passo; confirma só no fim (D-22); teste com duas portas no mesmo gabinete |
| `delta_*` do frameless somado a uma rotação/escala não prevista (portas espelhadas, `Mirror Y`) | médio | média | Testes por folha (esquerda, direita, dupla, basculante, canto) comparando a aresta da dobradiça antes e depois |
| `save_pre` muito lento em projetos grandes (face frame confirma `swing_percent` → recálculo) | médio | baixa | Fechar pela pose (sem recálculo) e só confirmar o valor 0; medir com 50 módulos |
| Falso positivo de interferência com o próprio gabinete ou com a frente vizinha | médio | alta | Exclusões explícitas (D-29) e tolerância de 1 mm |
| Gizmo sem pólo em contexto sem janela (testes em lote) | baixo | alta | Lógica do valor fica no adaptador e é testada sem gizmo |
| Desligar "Evitar Sobreposição" muda o comportamento padrão de quem já usa | médio | baixa | Padrão continua ligado (comportamento atual) |

## I3-10. Critério de pronto

- [ ] Porta (esquerda, direita, dupla), basculante, gaveta e pullout abrem e fecham nas três linhas e no módulo rápido,
  pelo clique (modo de inspeção), pelo gizmo (com paradas 0/45/90°) e por "Abrir tudo"/"Fechar tudo"
- [ ] Salvar com frentes abertas e reabrir mostra tudo fechado; a vista continua aberta depois de salvar; com
  `save_fronts_open` ligado, reabre aberto
- [ ] Abrir portas não marca o plano de corte como desatualizado
- [ ] Porta que bate numa sanca/parede é listada com objeto e ponto; nenhum aviso para o próprio gabinete
- [ ] "Evitar Sobreposição" desligado permite sobrepor módulos no posicionamento; ligado, comportamento atual
- [ ] `ruff`, `check_api.py`, testes `unittest` e smokes no Blender 5.2 passando; registro/desregistro sem resíduo
  (gizmo, handlers `save_pre`/`save_post`, timer, draw handler)
- [ ] `legacy-impact.md` e `regression-watch.md` atualizados pelo `/reversa-coding`

## I3-11. Histórico de alterações

| Data | Alteração | Autor |
|---|---|---|
| 2026-10-01 | Incremento 3, bloco 1 (inspeção e movimento) gerado por `/reversa-plan` | reversa |
