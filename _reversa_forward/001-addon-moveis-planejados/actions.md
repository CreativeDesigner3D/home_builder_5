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
| 2026-10-01 | Versão inicial gerada por `/reversa-to-do` (incremento 1) | reversa |
