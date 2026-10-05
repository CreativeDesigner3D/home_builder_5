# Impacto no legado — 001-addon-moveis-planejados (incremento 1)

> Gerado por `/reversa-coding` em 2026-10-01 · ações T001–T047 · base: `_reversa_sdd/architecture.md`,
> `_reversa_sdd/domain.md` e os `requirements.md` das units (`hb_core`, `hb_placement`, `frameless`, `closets`,
> `cutting`, `data`, `ui`, `operators`).

## Tabela de impacto

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `blendertomob/compat.py` | hb_core (compat) | regra-alterada | MEDIUM | Cache de identificadores GN por `session_uid`; API por identificador e `try_get_gn_input` centralizadas (`hb_core` RN-03 mantida) |
| `blendertomob/hb_utils.py` | hb_core | regra-alterada | LOW | Helpers GN duplicados viram aliases de `compat` (fim da duplicação) |
| `blendertomob/hb_types.py` | hb_core (cotas) | regra-alterada | MEDIUM | `get_unit_type` prioriza `btm_settings.btm_unit`; `refresh_dimension_units` reaplica `Unit Type` ao trocar a unidade (`hb_core` RN-18) |
| `blendertomob/data/units.py`, `blendertomob/units.py` | data (unidades) | regra-alterada | MEDIUM | Vírgula decimal, `format_length`, `parse_length` (sem frações) e `unit_to_string` recriado na unidade do usuário |
| `blendertomob/hb_placement.py` | hb_placement (digitação) | regra-alterada | HIGH | Parser de medidas digitadas troca pés/polegadas/frações por mm/cm/m com vírgula (`hb_placement` RN-05, RN-06; decisão PL-03) |
| `product_libraries/face_frame/dim_edit_overlay.py`, `product_libraries/closets/gpu_overlay_closets.py` | face_frame / closets (edição de cotas) | regra-alterada | MEDIUM | Reusam o parser novo; caracteres aceitos passam a `0-9 , . - m c` |
| `blendertomob/data/dimension_schema.py` | data (Padrão de Dimensões) | componente-novo | MEDIUM | Esquema declarativo de 870 parâmetros (linhas × componentes), validação e índice Promob |
| `blendertomob/standards/*` (`model`, `builtin`, `api`, `io_json`, `io_promob`, `sync`, `migration`, `previews`) | standards (novo) | componente-novo | HIGH | Fonte única de medidas/chapas/fitas/limites; `Scene.btm_standards`, `WindowManager.btm_standards_draft`; migração M-01/M-02 |
| `blendertomob/data/properties.py` | data (props de cena) | delta-de-dados | MEDIUM | `cut_plan_stale`, `cut_include_client`; `dimension_settings` e `config_*` obsoletos (só migração); troca de unidade atualiza cotas |
| `product_libraries/frameless/operators/ops_defaults.py` | frameless (propagação de padrões) | regra-alterada | MEDIUM | Propagação vira funções com `skip` de medidas manuais; operadores com `UNDO` (dívida "Undo" da unit frameless) |
| `product_libraries/frameless/operators/ops_cabinet.py` | frameless (prompts) | regra-nova | LOW | Edição no diálogo do gabinete registra `btm_overrides` (RN-23) |
| `product_libraries/closets/props_closets.py` | closets (starter) | regra-nova | LOW | Edição de altura/profundidade/rodapé do starter registra `btm_overrides`; recálculo inalterado (`closets` RN-06 mantida) |
| `blendertomob/cutting/nesting.py` | cutting (nesting) | regra-alterada | MEDIUM | `NestingPart` com `uid`, `component`, `edges[4]`, `finish`, `source`, `limit_status`; chapas agrupadas por (material, espessura, acabamento) |
| `blendertomob/cutting/part_roles.py`, `part_sources.py`, `part_extractor.py` | cutting (extração) | regra-alterada | HIGH | Peças sintéticas viram leitura real dos `GeoNodeCutpart` (frameless/closets); `btm_uid` nos módulos; limite de chapa por componente |
| `blendertomob/cutting/json_exporter.py` | cutting (exportação) | delta-de-contrato-externo | HIGH | JSON v1 (`parts_catalog`) substituído pelo v2 (`interfaces/json-global-v2.md`); v1 aceito só na leitura |
| `blendertomob/cutting/csv_exporter.py` | cutting (exportação) | delta-de-contrato-externo | MEDIUM | Novo CSV de peças (`interfaces/csv-pecas.md`) |
| `blendertomob/cutting/stale.py`, `cutting/__init__.py` | cutting | componente-novo | LOW | Handler `depsgraph_update_post` que marca o plano como desatualizado |
| `blendertomob/operators/ops_cutting.py` | operators (corte) | regra-alterada | MEDIUM | Cálculo com extração real, incompatíveis, JSON v2/CSV, importação de JSON, dados do cliente opcionais |
| `blendertomob/operators/ops_standards.py`, `ui/standards_tree.py` | operators / ui (Configurador) | componente-novo | MEDIUM | Configurador, aplicar com confirmação de N módulos, gestão, Promob/JSON, relatório |
| `blendertomob/operators/ops_dimensions.py` | operators (dimensões) | regra-removida | MEDIUM | Diálogo antigo e presets deixam de editar `dimension_settings`; os dois operadores abrem o Configurador |
| `blendertomob/operators/cabinet_builder.py` | operators (módulo rápido) | regra-alterada | LOW | Espessura padrão vem de `COZ.sheets.LAT.thickness`, não de `config_lateral` |
| `blendertomob/ui/panels.py`, `ui/__init__.py` | ui (painéis) | regra-alterada | MEDIUM | Bloco "Padrão de Dimensões" substitui o editor de `dimension_settings`; Plano de Corte com aviso, incompatíveis, JSON v2/CSV |
| `blendertomob/data/i18n.py` | data (i18n) | regra-alterada | LOW | Strings novas pt-BR → en, incluindo os rótulos do esquema |
| `blendertomob/__init__.py`, `operators/__init__.py` | núcleo do add-on | regra-alterada | LOW | Registro de `standards`, `cutting`, novos operadores e `UIList`; migração no `load_file_post` |
| `tests/*`, `docs/usuario/configurador-e-producao.md` | testes / docs | componente-novo | LOW | Testes `unittest` e smokes do incremento; guia do usuário |

## Diff conceitual por componente

**hb_core (compat, cotas).** A leitura de inputs de Geometry Nodes continua por nome de socket com cache e uma nova
tentativa (RN-03), mas o cache agora é chaveado por `session_uid` e toda a família de funções mora em `compat.py`;
`hb_utils` e `hb_types` só reexportam. As cotas legadas passam a ler a unidade do BlenderToMob antes da unidade da
cena, e trocar a unidade reaplica `Unit Type` e casas decimais em todas as cotas existentes.

**hb_placement e edição de cotas.** A gramática imperial (pés, polegadas, frações `a/b`, mistas `a b/c`) sai. Entra a
gramática métrica com vírgula ou ponto decimal e sufixos mm/cm/m; sem sufixo vale a unidade do usuário. O rótulo da
digitação passa a ter nome em português e a unidade. Os overlays de face_frame e closets, que emprestavam o parser,
acompanham.

**data / standards.** Surge a entidade "Definição de Dimensões" (embutidas Brasil/EUA somente leitura, cópias do
usuário, importadas do Promob, migrada). Ela é a fonte das propriedades legadas `hb_frameless.*` e `hb_closets.*`,
gravadas pela sincronização junto com a atualização dos módulos existentes, que respeita as medidas editadas à mão
(`btm_overrides`) salvo pedido explícito. `dimension_settings` e `config_*` ficam como dados obsoletos lidos uma vez
pela migração.

**frameless / closets.** A propagação de padrões e o recálculo não mudam de fórmula; ganham o filtro de medidas
manuais e o registro dessas medidas nas edições do usuário. Os operadores de propagação do frameless passam a ter
`UNDO`.

**cutting.** O otimizador mantém NFD por prateleiras, guilhotina, refilo, kerf e veio, e agrupa também pelo
acabamento. A lista de peças deixa de ser sintética para gabinetes frameless/closets e passa a vir dos `GeoNodeCutpart`
visíveis, com componente, fitas (lados 1–2 comprimento, 3–4 largura), matéria-prima e limite de chapa da definição
ativa. O contrato externo muda de JSON v1 para v2 e ganha CSV.

**operators / ui.** O antigo editor de dimensões dá lugar ao Configurador (árvore, imagem de referência, pendências,
confirmação de módulos afetados) e a operadores de gestão e de arquivos; os operadores antigos só abrem o
Configurador. O painel de corte mostra plano desatualizado e peças incompatíveis.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` e das units que continuam intactas:

- `domain.md` R-02 (piso conformal), R-04 a R-08 (snapping e limites de aberturas): código não tocado.
- `domain.md` R-09 (precedência de área) e R-10 (corte guilhotinado); `cutting` R-01 (refilo), R-02 (kerf), R-03
  (veio impede rotação), R-04 (guilhotina): mesmas rotinas `_can_fit_in_shelf` / `_can_create_shelf`.
- `hb_core` RN-03: socket resolvido por nome, com cache invalidado e uma nova tentativa em `KeyError`/`AttributeError`.
- `hb_core` RN-19: casas decimais pelo encaixe no incremento da unidade.
- `hb_placement` RN-02, RN-03, RN-07: início, saída e efeito da digitação no modal.
- `frameless` RN-02, RN-15, RN-34, RN-37: fórmulas de fundo, sobreposição, "drop to countertop" e lateral aplicada.
- `closets` RN-06: mudar altura/profundidade do starter só propaga aos vãos que estavam no valor anterior.

## Modificadas

- `hb_placement` RN-05 (precedência do parser com pés/polegadas e frações) → **removida**: só mm/cm/m com vírgula ou
  ponto; frações e notação imperial são rejeitadas (decisão PL-03).
- `hb_placement` RN-06 (número puro conforme `unit_settings` da cena) → **alterada**: número puro na unidade do
  BlenderToMob (`btm_settings.btm_unit`), que mantém `unit_settings` em sincronia.
- `hb_core` RN-18 (`Unit Type` pela `unit_settings`) → **alterada**: `btm_unit` tem prioridade; a regra antiga vale
  só sem `btm_settings`.
- `hb_core` objetivo "ler/escrever inputs GN pelo nome" → **alterada** (redação): implementação única em `compat.py`
  com cache por `session_uid`.
- `cutting` (`nesting.py`, agrupamento por material e espessura) → **alterada**: agrupamento por material, espessura e
  acabamento.
- `cutting` (`NestingPart`/exportação JSON v1) → **alterada**: contrato v2; v1 só na leitura.
- `frameless` dívida "Undo" (`ops_defaults.py` sem `UNDO`) → **alterada**: operadores de propagação com `UNDO`.

---

# Impacto no legado — incremento 3, bloco 1 (Inspeção e movimento)

> Gerado por `/reversa-coding` em 2026-10-03 · ações T048–T051, T054–T064, T068, T069, T073–T077.

## Tabela de impacto

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `blendertomob/inspection/*` (`fronts`, `pivot_math`, `props`, `ops_inspect`, `ops_interference`, `interference`, `gizmo`, `overlay`, `save_guard`, `adapters/*`) | inspeção (novo) | componente-novo | MEDIUM | Camada única de abertura das quatro origens de frente, controle no 3D, salvar fechado e interferência |
| `blendertomob/inspection/adapters/frameless.py` | frameless (frentes) | regra-nova | MEDIUM | Frentes frameless passam a abrir por `delta_rotation_euler`/`delta_location`, valor em idprop `btm_open` |
| `blendertomob/product_libraries/closets/types_closets.py` | closets (abertura) | delta-de-dados | MEDIUM | `hb_door_open`/`hb_drawer_open` lidos como fração 0–1 (`open_fraction`); 0/1 antigos continuam válidos |
| `blendertomob/geometry/door_controller.py` | camada moderna (portas) | regra-alterada | MEDIUM | Posição fechada do controlador passa de Y = 0,03 m para 0 (as portas não ficam mais ~13,5° abertas) |
| `blendertomob/data/properties.py` | data (props de cena) | delta-de-dados | LOW | `save_fronts_open`; `collision_global` renomeada para "Evitar Sobreposição" (lógica ainda não ligada — T071) |
| `blendertomob/__init__.py` | núcleo do add-on | regra-alterada | LOW | Registro do pacote `inspection` (gizmo, `save_pre`/`save_post`/`save_post_fail`, draw handlers) |
| `blendertomob/ui/panels.py` | ui (painéis) | regra-alterada | LOW | Bloco "Inspeção de Portas e Gavetas" na aba Construtor; rótulo "Evitar Sobreposição" |
| `blendertomob/data/i18n.py` | data (i18n) | regra-alterada | LOW | Strings do bloco de inspeção |

## Diff conceitual por componente

**Inspeção (novo).** Uma `Front` representa uma porta, basculante, gaveta ou pullout de qualquer linha, com um valor
comum (graus de 0 a 90 para articuladas, fração do curso para gavetas). O valor é aplicado sem recalcular o módulo
durante a animação ou o arraste e gravado no estado da linha ao final. O arquivo é salvo sempre fechado (RN-14) e a
vista é reaberta depois de salvar. O detector de interferência varre a abertura e testa contra os outros objetos.

**frameless.** Ganha abertura sem objetos novos nem mudança no recálculo: só os deltas de transformação da própria
peça e a idprop `btm_open`.

**face frame.** Nenhum arquivo do face frame foi alterado; o adaptador usa `op_open_mode._build_tween_context` e
`_apply_swing` e grava `swing_percent` (90° = 0,9).

**closets.** O estado de abertura passa a ser fracionário para permitir 45°; o layout reaplica a fração no recálculo.

**camada moderna.** O controlador fecha em Y = 0, coerente com a restrição (0–0,2 m) e com o slider.

## Preservadas

- `domain.md` R-02, R-04 a R-10: código não tocado.
- `_reversa_sdd/closets/requirements.md` RN-06 e o recálculo dos starters: inalterados (só a leitura do estado salvo).
- Mecanismo do face frame (`solver_face_frame.front_leaves`, `swing_percent`, pivôs `FRONT_PIVOT`): inalterado.

## Modificadas

- `_reversa_sdd/data-dictionary-legacy.md`, `hb_door_open / hb_drawer_open` (int, 0) → **alterada**: float 0–1.
- `_reversa_sdd/data-dictionary.md`, `collision_global` ("Colisões Globais") → **alterada** (redação): "Evitar
  Sobreposição"; a lógica de posicionamento ainda não a lê (T071 pendente).

## Incremento 3, bloco 1 — segunda rodada (T052, T053, T065–T067, T070–T072, T078, T079)

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `blendertomob/hb_placement.py` | hb_placement (vão) | regra-alterada | HIGH | `avoid_overlap()`; com "Evitar Sobreposição" desligado, módulos, módulos livres e intrusões de paredes deixam de ser obstáculos em `find_placement_gap_by_side` (RN-13) |
| `blendertomob/product_libraries/face_frame/operators/op_open_mode.py` | face_frame (abrir) | regra-alterada | MEDIUM | `hb_face_frame.open_mode` vira atalho de `btm.inspect_fronts`; helpers de pose mantidos |
| `blendertomob/product_libraries/closets/operators/op_open_door_closet.py` | closets (abrir) | regra-alterada | MEDIUM | `hb_closets.open_door_mode` e as funções da pílula delegam ao modo único |
| `blendertomob/operators/viewport_hud.py` | HUD | regra-alterada | LOW | Botão de abrir portas visível no modo Parts de todas as linhas |
| `blendertomob/cutting/stale.py` | cutting (plano desatualizado) | regra-alterada | MEDIUM | Abrir frentes não marca o plano; rodada do recálculo do face frame ignorada |
| `blendertomob/inspection/ops_inspect.py`, `inspection/interference.py`, `inspection/adapters/face_frame.py` | inspeção | regra-alterada | LOW | Cliques nas pílulas do closets passam; teste de contenção no detector; aviso ao handler de plano |
| `tests/*`, `docs/usuario/inspecao-e-movimento.md` | testes / docs | componente-novo | LOW | Testes de `pivot_math`, fumaça da inspeção, checagens de registro corrigidas; guia do usuário |

**hb_placement.** O cálculo do vão continua igual com a opção ligada (padrão). Desligada, só portas, janelas e linhas de
encaixe limitam a posição; os módulos podem se sobrepor (RN-13).

**face frame / closets.** Os dois modos de abrir antigos deixam de ter animação própria e abrem o modo único, que usa
os mesmos mecanismos de pose de cada linha.

### Preservadas (segunda rodada)

- `_reversa_sdd/hb_placement/requirements.md` RN-12 (filtro vertical) e o cálculo de `snap_x` e de recuos: inalterados.
- `_reversa_sdd/closets/requirements.md` "abrir portas/gavetas com animação": continua verdadeiro, agora pelo modo
  único (mesmo `bl_idname`, mesma pílula).
- `find_placement_gap` (portas e janelas nas paredes): inalterado.

### Modificadas (segunda rodada)

- `_reversa_sdd/hb_placement/requirements.md` RN-09 ("obstáculos são os filhos da parede…") → **alterada**: os
  filhos-módulo só são obstáculos com "Evitar Sobreposição" ligado; portas e janelas sempre.
- `_reversa_sdd/hb_placement/requirements.md` RN-14 (gabinetes livres viram obstáculos) → **alterada**: só com
  "Evitar Sobreposição" ligado.

