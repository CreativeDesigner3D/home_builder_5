# Actions: Add-on de Móveis Planejados — incremento 1 (Fundação e produção)

> Identificador: `001-addon-moveis-planejados`
> Data: `2026-10-01`
> Roadmap: `_reversa_forward/001-addon-moveis-planejados/roadmap.md`
> Escopo: incremento 1 (requirements §8): plataforma e unidades, Padrão de Dimensões (Configurador), lista de peças,
> plano de corte, JSON v2 e CSV para as linhas frameless e closets. Incrementos 2–4 terão `actions.md` próprios.
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 47 |
| Paralelizáveis (`[//]`) | 26 |
| Maior cadeia de dependência | 10 (T003 → T004 → T013 → T015 → T031 → T032 → T033 → T034 → T039 → T044) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Consolidar a ponte de inputs de Geometry Nodes em `compat.py` com acesso por **nome** e por **identificador** (`get/set_gn_input`, `gn_input_data_path`) e um único cache por node group (princípio III; `_reversa_sdd/hb_core/tasks.md` T-01) | - | `[//]` | `blendertomob/compat.py` | 🟢 | `[X]` |
| T002 | Fazer os helpers de GN de `hb_utils.py` delegarem a `compat.py`, mantendo as assinaturas usadas pela camada legada | T001 | - | `blendertomob/hb_utils.py` | 🟢 | `[X]` |
| T003 | Criar o esquema declarativo de parâmetros: estrutura do registro (chave, linha, grupo, rótulos pt/en, unidade, tipo, padrões BR/EUA, mín., máx., passo, precisão, opções, significado do zero, negativo, imagem, códigos Promob, destinos legados) e funções de consulta (D-02) | - | `[//]` | `blendertomob/data/dimension_schema.py` | 🟢 | `[X]` |
| T004 | Preencher o esquema: Medidas Máximas; por linha (COZ, DOR, BAN, SAL, ESC) as Dimensões Externas (itens A–L), os 17 componentes de chapa com material/limites/espessura/fitas 1–4 e os componentes (sarrafo, rodapé, moldura); valores do Padrão Brasil (clarify C-3) e EUA; mapeamento Promob e `legacy_targets` | T003 | - | `blendertomob/data/dimension_schema.py` | 🟡 | `[X]` |
| T005 | Parser e formatador únicos de medidas: unidade do usuário (mm/cm/m), vírgula decimal, sufixos `mm`/`cm`/`m`, rejeição de negativo onde proibido, precisão por campo (RN-01, D-07) | - | `[//]` | `blendertomob/data/units.py` | 🟢 | `[X]` |
| T006 | Script que gera por render as imagens de referência dos parâmetros do incremento 1 (lados 1–4 por componente de chapa, dimensões externas de inferior/aéreo/torre, rodapé) em `blendertomob/assets/dimension_refs/` (D-17) | - | `[//]` | `tools/render_dimension_refs.py` | 🟡 | `[X]` |
| T007 | Criar o pacote `standards` com `register()`/`unregister()` vazios e a lista de classes | - | `[//]` | `blendertomob/standards/__init__.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T008 | Testes do parser/formatador: `75,5` cm → 755 mm; `0,4` mm preservado; sufixos; valor inválido; arredondamento declarado | T005 | `[//]` | `tests/test_units.py` | 🟢 | `[X]` |
| T009 | Testes de integridade do esquema: toda chave tem unidade, faixa e imagem; padrão BR e EUA dentro da faixa; códigos Promob únicos | T004 | `[//]` | `tests/test_dimension_schema.py` | 🟢 | `[X]` |
| T010 | Fixture com o `DIMENSIONEXPORT` de referência (692 atributos) e testes de importação/exportação: mapeamento de `C`/`L`/`ESP`/`MAT`/`FIT`, `raw_attributes`, reexportação com os mesmos pares | T004 | `[//]` | `tests/test_promob_io.py` | 🟢 | `[X]` |
| T011 | Testes dos contratos de produção: validador do JSON v2 (campos, tipos, referências cruzadas, caminho do erro), ida e volta v2, conversão v1 → v2, formato do CSV de peças | - | `[//]` | `tests/test_production_contracts.py` | 🟢 | `[X]` |
| T012 | Teste de fumaça do incremento 1 em `--background`: criar balcão frameless e roupeiro closets, aplicar definição, gerar lista de peças, plano de corte, exportar JSON v2 e CSV | T007 | `[//]` | `tests/blender_increment1_smoke.py` | 🟡 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T013 | PropertyGroups do Padrão de Dimensões (Standards, Definition, Line, ExternalDims, SheetComponent, LineParam, MaxMeasures, RawAttribute) e ponteiros `Scene.btm_standards` e `WindowManager.btm_standards_draft` (data-delta §1) | T004, T007 | - | `blendertomob/standards/model.py` | 🟢 | `[X]` |
| T014 | Definições embutidas somente-leitura "Padrão Brasil" (valores C-3, a partir de `data/dimensions_preset.py`) e "Padrão EUA (HB5)" (padrões atuais de frameless/closets); função que garante sua existência na cena principal (D-04) | T013 | - | `blendertomob/standards/builtin.py` | 🟢 | `[X]` |
| T015 | API do padrão: definição ativa da cena principal, leitura/escrita por caminho, cópia para o rascunho, lista de pendências (antes/depois/impacto), validação contra o esquema com mensagem "Valor Inválido" (campo, valor, unidade, faixa) | T013 | - | `blendertomob/standards/api.py` | 🟢 | `[X]` |
| T016 | Exportar e importar definições `.btmdim.json` conforme `interfaces/dimension-definition.md` (escrita atômica, versão do esquema, colisão de nome, pasta do usuário) | T015 | `[//]` | `blendertomob/standards/io_json.py` | 🟢 | `[X]` |
| T017 | Importar e exportar `DIMENSIONEXPORT` conforme `interfaces/promob-dimensionexport.md` (`xml.etree`, vírgula decimal, famílias confirmadas, `raw_attributes`, relatório mapeados × não reconhecidos) | T015, T010 | `[//]` | `blendertomob/standards/io_promob.py` | 🟢 | `[X]` |
| T018 | Extrair a lógica dos operadores `hb_frameless.update_material_thickness_prompts`, `update_toe_kick_prompts` e `update_cabinet_sizes` para funções chamáveis sem `bpy.ops`, e implementar os 2 TODO (`update_base_top_construction_prompts`, `update_drawer_front_height_prompts`); operadores viram atalhos com `UNDO` | T002 | `[//]` | `blendertomob/product_libraries/frameless/operators/ops_defaults.py` | 🟡 | `[X]` |
| T019 | Sincronização definição → props legadas (`Scene.hb_frameless`, `Scene.hb_closets`) pelos `legacy_targets`, atualização dos gabinetes existentes pelas funções de T018 e recálculo dos starters de closets; respeitar `btm_overrides` salvo `include_manual`; devolver relatório (módulos alterados, parâmetros sem destino) (D-05, D-06, D-16a) | T015, T018 | - | `blendertomob/standards/sync.py` | 🟡 | `[X]` |
| T020 | Registrar `btm_overrides` quando o usuário edita largura/altura/profundidade/espessura de um gabinete frameless pelos diálogos de prompts | T013 | `[//]` | `blendertomob/product_libraries/frameless/operators/ops_cabinet.py` | 🟡 | `[X]` |
| T021 | Registrar `btm_overrides` quando o usuário edita medidas de um starter ou vão de closets | T013 | `[//]` | `blendertomob/product_libraries/closets/props_closets.py` | 🟡 | `[X]` |
| T022 | Tabela de papéis: nome de peça do frameless e `hb_part_role` do closets → componente do padrão; arestas `Edge L1/L2` → lados 1/2 e `Edge W1/W2` → lados 3/4 (D-09, D-11, clarify C-1) | T004 | `[//]` | `blendertomob/cutting/part_roles.py` | 🟡 | `[X]` |
| T023 | `NestingPart` com `uid`, `component`, `edges[4]`, `finish`, `source`, `limit_status` (aliases de leitura para `edge_*`) e agrupamento de chapas por (matéria-prima, espessura, acabamento) (D-13, clarify C-2) | - | `[//]` | `blendertomob/cutting/nesting.py` | 🟢 | `[X]` |
| T024 | Adaptadores de peças: leitura dos `GeoNodeCutpart` visíveis (`Length`, `Width`, `Thickness`, material de `Top Surface`, fitas por `Edge *`) via `compat.get_gn_input`, atribuição de `btm_uid` ao módulo raiz, `uid` da peça e adaptador sintético (fallback `btm_*`) (D-08, D-10) | T002, T022, T023 | - | `blendertomob/cutting/part_sources.py` | 🟢 | `[X]` |
| T025 | Orquestrar a extração: adaptadores → classificação → espessura das fitas pelo componente da definição ativa → checagem de limite por componente → (peças, incompatíveis) (RN-16, RN-17, D-12) | T015, T024 | - | `blendertomob/cutting/part_extractor.py` | 🟢 | `[X]` |
| T026 | JSON global v2: exportação conforme `interfaces/json-global-v2.md`, validador stdlib com caminho do erro, importação de v2 e conversão de v1 (D-14) | T023, T011 | `[//]` | `blendertomob/cutting/json_exporter.py` | 🟡 | `[X]` |
| T027 | CSV genérico de peças conforme `interfaces/csv-pecas.md` (`;`, vírgula decimal, BOM, ordem estável) | T023, T011 | `[//]` | `blendertomob/cutting/csv_exporter.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T028 | Migrações em `load_post` (`@persistent`): M-01 (`dimension_settings` + `config_*` → definição "Migrada") e M-02 (definição padrão conforme haja gabinetes legados) (data-delta §5) | T014 | - | `blendertomob/standards/migration.py` | 🟢 | `[X]` |
| T029 | Coleção `bpy.utils.previews` das imagens de referência, com carga sob demanda, aviso para imagem ausente e remoção no `unregister()` (D-17) | T006, T007 | - | `blendertomob/standards/previews.py` | 🟢 | `[X]` |
| T030 | Registrar o pacote `standards` e o handler de migração no add-on, com remoção simétrica no `unregister()` | T013, T028, T029 | - | `blendertomob/__init__.py` | 🟢 | `[X]` |
| T031 | `UIList` da árvore do Configurador (Medidas Máximas; linha → Dimensões Externas / Chapas / Componentes) com busca por nome | T015 | - | `blendertomob/ui/standards_tree.py` | 🟢 | `[X]` |
| T032 | Operador `btm.standards_configurator`: `invoke` copia a definição ativa para o rascunho; `draw` com árvore, imagem de referência (`template_icon`), campos com unidade/faixa e lista de pendências; cancelar descarta o rascunho (D-16) | T031, T029 | - | `blendertomob/operators/ops_standards.py` | 🟢 | `[X]` |
| T033 | Operador de aplicar: mostra "N módulos serão atualizados", opção "incluir medidas manuais", aplica o rascunho e chama a sincronização num único passo com `UNDO` (RN-23, D-16a) | T032, T019 | - | `blendertomob/operators/ops_standards.py` | 🟢 | `[X]` |
| T034 | Operadores de gestão: definir ativa, duplicar, renomear, excluir (embutidas protegidas), exportar/importar `.btmdim.json` e `DIMENSIONEXPORT` com seletor de arquivo e relatório | T033, T016, T017 | - | `blendertomob/operators/ops_standards.py` | 🟢 | `[X]` |
| T035 | Operador de gerar lista de peças e plano de corte: usa a extração real, lista incompatíveis com a chapa, agrupa chapas por acabamento, limpa a marca de desatualizado | T025 | - | `blendertomob/operators/ops_cutting.py` | 🟢 | `[X]` |
| T036 | Operadores de exportar/importar JSON v2 e exportar CSV de peças, com dados do cliente opcionais (RN-21) | T035, T026, T027 | - | `blendertomob/operators/ops_cutting.py` | 🟢 | `[X]` |
| T037 | Propriedade `cut_plan_stale` em `Scene.btm_settings` e marcação de `dimension_settings`/`config_*` como obsoletos (somente leitura para a migração) | - | `[//]` | `blendertomob/data/properties.py` | 🟢 | `[X]` |
| T038 | Handler `depsgraph_update_post` (`@persistent`) que marca o plano como desatualizado quando um módulo com `btm_uid` muda, com registro e remoção no pacote `cutting` | T037 | - | `blendertomob/cutting/stale.py` | 🟡 | `[X]` |
| T039 | Painéis: entrada do Configurador e seletor da definição ativa; seletor de unidade; no Plano de Corte, lista de incompatíveis, aviso de desatualizado e botões de JSON v2/CSV | T034, T036 | - | `blendertomob/ui/panels.py` | 🟢 | `[X]` |
| T040 | Cotas legadas (`GeoNodeDimension`) usando `btm_settings.btm_unit` em `get_unit_type` e `set_decimal` (`_reversa_sdd/hb_core/tasks.md` T-16) | T005 | `[//]` | `blendertomob/hb_types.py` | 🟢 | `[X]` |
| T041 | Posicionamento modal: digitação de medidas pelo parser de `data/units.py` (sem frações, decisão PL-03) e rótulos de pré-visualização na unidade do usuário | T005 | `[//]` | `blendertomob/hb_placement.py` | 🟢 | `[X]` |
| T042 | Cotas e rótulos das sobreposições da camada moderna formatados pela unidade do usuário | T005 | `[//]` | `blendertomob/overlays/draw_handlers.py` | 🟢 | `[X]` |
| T043 | `btm.dimension_settings_dialog` e `btm.apply_dimension_preset` passam a abrir o Configurador (compatibilidade com menus existentes) | T032 | - | `blendertomob/operators/ops_dimensions.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T044 | Strings novas em pt-BR e en (Configurador, mensagens de validação, relatórios, painel de corte) | T039 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |
| T045 | Janela de relatório após aplicar/importar: módulos alterados, parâmetros sem destino na sincronização, códigos Promob não reconhecidos | T034 | - | `blendertomob/operators/ops_standards.py` | 🟢 | `[X]` |
| T046 | Guia curto do usuário: Configurador de Dimensões, importação do Promob, lista de peças, plano de corte, JSON v2 e CSV | T039 | `[//]` | `docs/usuario/configurador-e-producao.md` | 🟢 | `[X]` |
| T047 | Teste de fumaça geral: registrar/desregistrar a extensão 2× sem resíduo (Scene.btm_standards, previews, handlers) | T030 | `[//]` | `tests/blender_smoke.py` | 🟢 | `[X]` |

## Notas de execução

<!--
Reservado para /reversa-coding registrar avisos ou observações que surgiram durante a execução.
-->

Rodada de 2026-10-01 (`/reversa-coding`, incremento 1, T001–T047):

- **Desvio — armazenamento dos valores (T013):** a definição guarda os 870 parâmetros numa coleção genérica
  (`values`, `name` = chave do esquema, valor em mm ou texto), e não em PropertyGroups estruturados por linha e
  componente como no `data-delta.md` §2. A estrutura vem de `data/dimension_schema.py`. 🟡
- **Desvio — `BTM_PG_RawAttribute.key` (T013/T017):** campo extra com a chave do esquema do atributo Promob mapeado
  (vazio = não reconhecido), usado para reexportar sem perda.
- **Desvio — valores do Padrão Brasil (T014):** vêm do esquema (`Param.default('BR')`, valores do clarify C-3), não
  de `data/dimensions_preset.py`, que fica sem uso.
- **Desvio — mapeamento do Promob (T004/T017):** mapeamento genérico por família (`PROMOB_INDEX` + permutação dos lados
  de fita), em vez de uma tabela ID a ID.
- **Desvio — edição no Configurador (T032):** o valor é digitado num campo de texto (`edit_text`) interpretado na
  unidade do usuário com vírgula decimal, em vez de um `FloatProperty` por parâmetro; a árvore abre/fecha por clique
  (são ~900 linhas abertas).
- **Correção fora do escopo original (T041/T042):** `units.unit_to_string` tinha sido removido de
  `blendertomob/units.py` no commit `ff10e80` e é usado em 98 rótulos (placement, frameless, closets, face_frame);
  foi recriado em `data/units.py` já na unidade do usuário. As cópias do parser em
  `face_frame/dim_edit_overlay.py` e `closets/gpu_overlay_closets.py` foram ajustadas ao parser novo (sem frações).
- **Correção (T028):** `api.duplicate_definition` e `builtin.ensure_builtins` passaram a buscar os itens de novo após
  `definitions.add()` (realocação da coleção — `docs/rag/project/04_armadilhas.md`).
- **Decisão (T025):** limite de chapa comparado com as medidas ordenadas (lado maior × maior limite); `Top` do
  frameless mapeado para `BAS` e fundo por tipo de gabinete (`FUN_INF`/`FUN_SUP`/`FUN_ALT`). 🟡
- **Decisão (T030):** a migração roda no fim do `load_file_post` já existente (depois de garantir a cena principal) e,
  na abertura sem arquivo, num timer; não há um segundo handler `load_post`.
- **Decisão (T038):** `calculate()` força `view_layer.update()` depois da extração para que a gravação de `btm_uid`
  não marque o plano recém-calculado como desatualizado.
- Verificação final: `ruff` OK; `check_api.py` sem `[UNKNOWN in 5.2]`; 54 testes `unittest` OK; `blender_smoke`,
  `blender_increment1_smoke` e `blender_legacy_smoke` OK no Blender 5.2.0.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-02 | Acrescentadas as ações do incremento 3, bloco 1 (T048–T079), ao fim do documento | reversa |
| 2026-10-01 | Versão inicial gerada por `/reversa-to-do` (incremento 1) | reversa |


---

# Actions: incremento 3 — bloco 1 (Inspeção e movimento)

> Data: `2026-10-02` · Roadmap: seção "Incremento 3 — bloco 1" do `roadmap.md` (D-19 a D-32) · Data delta: seção
> "Incremento 3 — bloco 1" do `data-delta.md` · Requisitos: RF-090, RF-091, RF-046, RN-13, RN-14.
> Os IDs continuam a numeração do incremento 1 (T001–T047, concluídas), conforme a regra de não reciclar IDs.
> Premissa herdada (roadmap I3-4): "engrenagem de 45–90°" = controle giratório no 3D com paradas em 0°/45°/90°.

## Resumo (incremento 3, bloco 1)

| Métrica | Valor |
|---------|-------|
| Total de ações | 32 (T048–T079) |
| Paralelizáveis (`[//]`) | 23 |
| Maior cadeia de dependência | 8 (T048 → T054 → T055 → T063 → T064 → T075 → T076 → T077) |

## Fase 1, Preparação (incremento 3)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T048 | Criar o pacote `inspection/` com o tipo `Front` (`kind` DOOR/FLIP_UP/FLIP_DOWN/DRAWER/PULLOUT, `module_root`, `obj`, `pivot`, `hinge`, `max_value`, `library`, `get/apply/commit`, `hinge_axis_world`) e o registro de adaptadores (`iter_fronts(scene)`, `fronts_of(module)`, `front_for_object(obj)`) (D-19) | - | `[//]` | `blendertomob/inspection/fronts.py` | 🟢 | `[X]` |
| T049 | PropertyGroups `BTM_PG_InspectionState` (`active`, `snap_stops`, `default_angle`, `interferences`, `interference_index`) e `BTM_PG_Interference`, registrados em `WindowManager.btm_inspection` com remoção simétrica (data-delta I3-1) | - | `[//]` | `blendertomob/inspection/props.py` | 🟢 | `[X]` |
| T050 | `btm_settings.save_fronts_open` (Bool, padrão desligado) e rótulo/descrição de `collision_global` como "Evitar Sobreposição" (data-delta I3-2, I3-3; RN-13) | - | `[//]` | `blendertomob/data/properties.py` | 🟢 | `[X]` |
| T051 | Matemática pura (sem `bpy`): rotação em torno de uma aresta → `delta_location`/`delta_rotation`, deslizamento de gaveta, encaixe em 0°/45°/90° (tolerância 5°) e conversões graus ⇄ `swing_percent` (100°), fração closets (110°) e `door_open` (90°) (D-20, D-21, D-25) | - | `[//]` | `blendertomob/inspection/pivot_math.py` | 🟡 | `[X]` |

## Fase 2, Testes (incremento 3)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T052 | Testes `unittest` da matemática de pivô: basculante volta à aresta superior, porta esquerda/direita mantém a dobradiça, encaixe 43°→45° e 52°→52°, conversões entre linhas e limites 0/90 | T051 | `[//]` | `tests/test_inspection_math.py` | 🟢 | `[X]` |
| T053 | Teste de fumaça no Blender: abrir/fechar por adaptador nas quatro origens (frameless porta dupla, basculante e gaveta; face frame; closets; módulo rápido), 45°, salvar fechado e reabrir, plano de corte não marcado como desatualizado, interferência com parede à frente, "Evitar Sobreposição" desligado | T048 | `[//]` | `tests/blender_inspection_smoke.py` | 🟢 | `[X]` |

## Fase 3, Núcleo (incremento 3)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T054 | Adaptador frameless: `Left Door`/`Right Door` giram por `delta_rotation_euler.z` (sinal pela folha), `Drawer Front`/`Pullout Front` deslizam por `delta_location.y`, `Flip Up Door` gira em torno da aresta superior com compensação em `delta_location`; valor em idprop `btm_open`; ausência = fechada (D-21, M-06) | T048, T051 | `[//]` | `blendertomob/inspection/adapters/frameless.py` | 🟢 | `[X]` |
| T055 | Adaptador frameless: portas de canto (`add_corner_doors`) com eixo e sinal no entalhe, e portas ocultas por `driver_hide` fora da lista de frentes | T054 | - | `blendertomob/inspection/adapters/frameless.py` | 🟡 | `[X]` |
| T056 | Adaptador face frame: graus ⇄ `swing_percent`; pose aplicada sem recálculo via `solver_face_frame.front_leaves` com proxy de `swing_percent` (como `_apply_swing`); `commit` grava `swing_percent`; pivô reobtido pelo papel `FRONT_PIVOT` a cada passo; `TILT_OUT` como `FLIP_DOWN` (D-22) | T048, T051 | `[//]` | `blendertomob/inspection/adapters/face_frame.py` | 🟢 | `[X]` |
| T057 | Closets: `hb_door_open`/`hb_drawer_open` lidos e regravados como fração 0–1 no recálculo (`apply_door_open`/`apply_drawer_open`), mantendo 0/1 de arquivos antigos (D-23, M-05) | - | `[//]` | `blendertomob/product_libraries/closets/types_closets.py` | 🟡 | `[X]` |
| T058 | Adaptador closets: graus ⇄ fração de `DOOR_OPEN_ANGLE`, pose por `apply_door_open`/`apply_drawer_open`, `commit` nas idprops fracionárias (D-22, D-23) | T048, T051, T057 | - | `blendertomob/inspection/adapters/closets.py` | 🟡 | `[X]` |
| T059 | Corrigir a posição do Empty controlador do módulo rápido (deslocamento `0.03` divergente entre `update_door_geometry_and_controller` e `update_door_rotation_from_property`) (D-32) | - | `[//]` | `blendertomob/geometry/door_controller.py` | 🟡 | `[X]` |
| T060 | Adaptador `btm` (módulo rápido): `_Door_L`/`_Door_R`/`_Door_Flip` lidos e escritos via `btm_cabinet.door_open` e o controlador; espelho em `btm_open` (D-32) | T048, T051, T059 | - | `blendertomob/inspection/adapters/btm.py` | 🟡 | `[X]` |
| T061 | Envelope de abertura: malha temporária (BMesh) varrendo a frente de 0 ao máximo em passos de 15° (articuladas) ou estendendo a caixa pelo curso (gavetas), sempre incluindo a pose final (D-29) | T048, T051 | `[//]` | `blendertomob/inspection/interference.py` | 🟡 | `[X]` |
| T062 | Detecção: pré-filtro AABB, `BVHTree.overlap` contra malhas avaliadas dos outros objetos, exclusão do próprio módulo e das frentes do mesmo vão, tolerância 1 mm; resultado (frente, módulo, objeto atingido, ponto, tipo) em `btm_inspection.interferences` (D-29) | T061, T049 | - | `blendertomob/inspection/interference.py` | 🟡 | `[X]` |

## Fase 4, Integração (incremento 3)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T063 | Operador `btm.fronts_set_open` (escopo: todas / do módulo / selecionadas; valor 0°, 45°, 90° ou curso total), `bl_options={'REGISTER'}` sem `UNDO` (D-24, D-27) | T054, T055, T056, T058, T060 | - | `blendertomob/inspection/ops_inspect.py` | 🟢 | `[X]` |
| T064 | Modal `btm.inspect_fronts`: clique alterna 0 ↔ ângulo padrão/curso com animação (timer 60 Hz, 0,35 s, smoothstep), clique durante a animação inverte, Esc/RMB sai confirmando; contrato do HUD (`register_active_modal`, `_exit_requested`, `click_hits_widget`); timer removido em todos os caminhos (D-26) | T063 | - | `blendertomob/inspection/ops_inspect.py` | 🟢 | `[X]` |
| T065 | `hb_face_frame.open_mode` vira atalho de `btm.inspect_fronts` (mesmo `bl_idname`, sem a lógica própria de tween) (D-26) | T064 | `[//]` | `blendertomob/product_libraries/face_frame/operators/op_open_mode.py` | 🟢 | `[X]` |
| T066 | `hb_closets.open_door_mode` vira atalho de `btm.inspect_fronts` e a pílula "Open Door" do overlay passa a chamá-lo (D-26) | T064 | `[//]` | `blendertomob/product_libraries/closets/operators/op_open_door_closet.py` | 🟢 | `[X]` |
| T067 | Botão de inspeção do HUD visível em todas as linhas (`_ModalToggleButton.visible` sem depender da aba do face frame), apontando para `btm.inspect_fronts` (D-27) | T064 | `[//]` | `blendertomob/operators/viewport_hud.py` | 🟢 | `[X]` |
| T068 | `GizmoGroup` `BTM_GGT_front_open`: `GIZMO_GT_dial_3d` no eixo da dobradiça e `GIZMO_GT_arrow_3d` no curso da gaveta, `target_set_handler` ligado ao adaptador (aplica no arraste, confirma ao soltar), encaixe 0°/45°/90° com Ctrl invertendo, pólo barato (frente ativa ou modo ativo) (D-25) | T054, T056, T058, T060, T049, T051 | `[//]` | `blendertomob/inspection/gizmo.py` | 🟡 | `[X]` |
| T069 | `save_pre`/`save_post` (`@persistent`): fecha e guarda em memória as frentes abertas antes de salvar e reabre depois; não age com `save_fronts_open` ligado (D-28, RN-14) | T063, T050 | `[//]` | `blendertomob/inspection/save_guard.py` | 🟢 | `[X]` |
| T070 | Handler de plano desatualizado ignora frentes e pivôs (`IS_CABINET_FRONT`, `IS_DOOR_FRONT`, papéis de frente, `FRONT_PIVOT`) e qualquer atualização enquanto a inspeção anima (D-31) | T048 | `[//]` | `blendertomob/cutting/stale.py` | 🟢 | `[X]` |
| T071 | `PlacementMixin.avoid_overlap(context)` lendo `collision_global`; desligado, `find_placement_gap`, intrusões de paredes adjacentes/em T e recuos não restringem a posição (D-30, RN-13) | T050 | `[//]` | `blendertomob/hb_placement.py` | 🟡 | `[X]` |
| T072 | Checagens de colisão próprias dos operadores de posicionamento frameless e face frame (sobreposição de altura, encosto em vizinho) respeitam `avoid_overlap` (D-30) | T071 | - | `blendertomob/product_libraries/frameless/operators/ops_placement.py` | 🟡 | `[X]` |
| T073 | Destaque de interferência no viewport (`draw_handler` POST_VIEW/POST_PIXEL com marcador e rótulo) e operador `btm.interference_goto` que enquadra o ponto; handler removido no `unregister()` (D-29) | T062 | `[//]` | `blendertomob/inspection/overlay.py` | 🟡 | `[X]` |
| T074 | Operador `btm.check_front_interference` (projeto inteiro ou seleção) com relatório "N interferências" e aviso explícito quando nenhuma frente foi verificada (RN-14, D-29) | T062 | `[//]` | `blendertomob/inspection/ops_interference.py` | 🟡 | `[X]` |
| T075 | Registrar o pacote `inspection` no add-on (props, operadores, gizmo, `save_pre`/`save_post`, draw handler) com `unregister()` simétrico | T049, T063, T064, T068, T069, T073, T074 | - | `blendertomob/__init__.py` | 🟢 | `[X]` |
| T076 | Bloco "Inspeção" no painel: modo de inspeção, Abrir tudo (45°/90°), Fechar tudo, `save_fronts_open`, Verificar interferência com lista e "Ir para"; "Evitar Sobreposição" na aba de configurações (D-27, D-29, D-30) | T075 | - | `blendertomob/ui/panels.py` | 🟢 | `[X]` |

## Fase 5, Polimento (incremento 3)

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T077 | Strings novas pt-BR → en (modo de inspeção, gizmo, abrir/fechar tudo, salvar com frentes abertas, interferência, Evitar Sobreposição) | T076 | `[//]` | `blendertomob/data/i18n.py` | 🟢 | `[X]` |
| T078 | Guia curto do usuário: abrir portas e gavetas, controle com paradas, salvar fechado, verificar interferência, Evitar Sobreposição | T076 | `[//]` | `docs/usuario/inspecao-e-movimento.md` | 🟢 | `[X]` |
| T079 | Teste de fumaça geral: registrar/desregistrar 2× sem resíduo do pacote `inspection` (gizmo, `WindowManager.btm_inspection`, `save_pre`/`save_post`, timers, draw handler) | T075 | `[//]` | `tests/blender_smoke.py` | 🟢 | `[X]` |

## Notas de execução (incremento 3)

Rodada de 2026-10-03 (`/reversa-coding` com escopo "T048 → T054 → T055 → T063 → T064 → T075 → T076 → T077"):

- **Escopo:** a cadeia pedida depende de ações abertas fora dela (T054 precisa de T051; T063 de T056/T058/T060; T075 de
  T049, T068, T069, T073, T074). Executou-se a cadeia **com o fecho das dependências**: T048–T051, T054–T064, T068,
  T069, T073–T077 (22 ações). Ficaram abertas T052, T053, T065–T067, T070–T072, T078, T079.
- **Liberação:** `.reversa/reversa-config.json` passou a `allowLegacyEdits: true` com `allowedPaths` vazio (projeto
  inteiro liberado). Esta rodada escreveu só em `blendertomob/`.
- **Desvio — dobradiça do frameless (T054/T055):** em vez de regra de sinal por nome (`Left Door`/`Right Door`), a
  dobradiça e o sentido de abrir são deduzidos da caixa local avaliada da peça (origem = quina da dobradiça,
  comprimento = altura, largura = borda livre, espessura = face frontal). A mesma regra cobre portas de canto
  (rotação `(0°, −90°, 180°)`) e o basculante (aresta superior). Verificado no Blender: dobradiça parada, borda livre
  para a frente, basculante subindo à aresta de cima, gaveta deslizando pelo `Dim Y` da caixa.
- **Desvio — encaixe do gizmo (T068):** o encaixe em 0°/45°/90° é ligado/desligado por `btm_inspection.snap_stops`
  (painel); "Ctrl inverte" não foi implementado porque o *handler* de valor do gizmo não recebe o evento. A gravação
  ao soltar roda num timer (gravar no face frame recalcula e recria objetos, o que não deve ocorrer durante o desenho).
- **Campo extra (T049):** `BTM_PG_InspectionState.checked_fronts` (frentes verificadas na última checagem; −1 = nunca),
  usado para o aviso "nenhuma frente verificada" (RN-14). Não estava no `data-delta.md`.
- **Correção legada (T059):** o Empty do módulo rápido era posicionado "fechado" em Y = 0,03 m, o que pelo driver
  (`y·(π/2)/0,2`) deixava as portas ~13,5° abertas; agora fechado = 0 nas duas funções. As linhas de `location.x/z`
  do controlador continuam sem efeito (a restrição trava X/Z em 0); não foram tocadas.
- **Limitação conhecida (T069):** reabrir as frentes no `save_post` altera dados depois de salvar, então o arquivo
  aparece como modificado logo após Ctrl+S quando havia frentes abertas.
- **Pendente que afeta o uso:** sem a T070, abrir portas ainda marca o plano de corte como desatualizado; sem as
  T065–T067, os modos legados (`hb_face_frame.open_mode`, pílula "Open Door" do closets) continuam separados e o botão
  do HUD continua só no face frame; o novo modo está no painel "Inspeção de Portas e Gavetas".
- **Achado fora do escopo:** `ui/panels.py` usa o ícone `OUTLINER_OB_LIGHTPATH`, que não existe no Blender 5.2
  (painel "Portas & Abertura" do módulo rápido); anterior a esta rodada, não alterado.
- Verificação: `ruff` OK; `check_api.py` sem `[UNKNOWN in 5.2]`; 54 testes `unittest` OK; `blender_smoke`,
  `blender_increment1_smoke`, `blender_legacy_smoke` OK; teste de integração (scratch) nas quatro origens:
  abrir 90°, conversões legadas (face frame 0,9; closets 0,818; controlador 0,2 m), salvar → tela aberta e arquivo
  fechado, interferência com obstáculo à frente da porta, pólo do gizmo, registro/desregistro sem resíduo. O gizmo e o
  modal não puderam ser exercitados interativamente (Blender em modo `--background`).

Rodada de 2026-10-03, segunda parte (`/reversa-coding` T052, T053, T065–T067, T070–T072, T078, T079) — incremento 3,
bloco 1 concluído (T048–T079 todas `[X]`):

- **T072 sem alteração de código:** o posicionamento de frameless, face frame e closets já passa por
  `PlacementMixin.find_placement_gap_by_side`, onde a T071 liga "Evitar Sobreposição". As verificações de altura do
  frameless (`get_cage_center_snap`) e do face frame (`_z_ranges_overlap`) são centralização sob janela e detecção de
  canto cego, não bloqueio de colisão.
- **T071 — escopo:** desligado, o vão ignora módulos na parede, módulos livres e as intrusões de paredes adjacentes
  e em T; portas, janelas e linhas de encaixe continuam valendo. `find_placement_gap` (portas e janelas) não muda.
- **T070:** o handler ignora frentes, pivôs e o que pendura neles; ignora tudo enquanto o modo de inspeção anima; e o
  adaptador do face frame pede para ignorar a rodada seguinte quando grava `swing_percent` (que recalcula o gabinete).
- **T065/T066:** `hb_face_frame.open_mode` e `hb_closets.open_door_mode` agora só chamam `btm.inspect_fronts`; a
  lógica de tween própria saiu. `op_open_mode.py` mantém `_SwingOverrideProxy`, `_build_tween_context` e
  `_apply_swing` (usados pelo adaptador). O novo modo deixa passar cliques nas pílulas do overlay do closets.
- **T067:** o botão do HUD virou `_InspectButton`, visível no modo **Parts** de qualquer linha; rótulos em português.
  No closets, o botão do HUD e a pílula "Open Door" aparecem juntos e fazem a mesma coisa.
- **Correção (T062):** o teste de choque passou a considerar também objetos inteiros dentro do casco do envelope
  (`BVHTree.overlap` só acha superfícies que se cruzam); registrado como `corrected` no progresso.
- **Achado de teste (não é defeito da inspeção):** em `--background`, o balcão frameless "Door Drawer" às vezes fica
  com a geometria errada (porta com 3 cm de altura, puxadores abaixo do piso) — bug do Blender #133392, já contornado
  pelos operadores do frameless com `hb_utils.run_calc_fix`. O teste de fumaça chama `run_calc_fix_until_stable`
  depois de criar o gabinete (12/12 execuções OK).
- **Testes:** as checagens de "classe não registrada" por `hasattr(bpy.types, 'Classe')` eram vazias (o nome da classe
  Python não aparece em `bpy.types`), inclusive as do incremento 1; trocadas por `bl_rna_get_subclass_py`.
- Verificação: `ruff` OK; `check_api.py` OK; testes `unittest` OK (inclui 9 novos de `pivot_math`);
  `blender_smoke`, `blender_increment1_smoke`, `blender_legacy_smoke` e o novo `blender_inspection_smoke` OK.

<!--
Reservado para /reversa-coding registrar avisos ou observações desta rodada.
Pré-condição registrada em 2026-10-02: `.reversa/reversa-config.json` está com `allowLegacyEdits: false`; o
`/reversa-coding` só pode escrever em `blendertomob/`, `tests/` e `docs/usuario/` depois que o titular liberar esses
caminhos em `allowedPaths`.
-->
