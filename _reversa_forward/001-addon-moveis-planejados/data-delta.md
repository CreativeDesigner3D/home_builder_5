# Data Delta: Add-on de Móveis Planejados — incremento 1

> Identificador: `001-addon-moveis-planejados` · Data: `2026-10-01`
> Base extraída: `_reversa_sdd/architecture.md#3-modelo-de-entidades-e-relacionamentos-erd`, `_reversa_sdd/data/design.md`,
> `_reversa_sdd/cutting/design.md`, `_reversa_sdd/hb_core/node-group-interfaces.md`.
> Unidade interna: metros (Blender). Valores de exemplo em mm.

## 1. Entidades novas

### 1.1 `Scene.btm_standards` → `BTM_PG_Standards` (só na cena principal)

| Campo | Tipo | Descrição |
|---|---|---|
| `definitions` | Collection[`BTM_PG_StandardDefinition`] | Definições nomeadas |
| `active_index` | Int | Definição ativa do projeto |
| `schema_version` | Int | Versão do formato (inicia em 1) |

### 1.2 `BTM_PG_StandardDefinition`

| Campo | Tipo | Descrição |
|---|---|---|
| `uid` | String | UUID estável |
| `name` | String | Ex.: "Padrão Brasil", "ME MOVEIS - COZ. ESCR." |
| `builtin` | Bool | Embutida (somente-leitura; duplicar para editar) |
| `market` | Enum `BR` / `US` | Origem do preset |
| `source` | Enum `BUILTIN` / `USER` / `PROMOB_IMPORT` / `MIGRATED` | Proveniência |
| `version` | Int | Incrementa a cada aplicação |
| `updated_at` | String ISO 8601 | Última alteração |
| `max_measures` | Pointer[`BTM_PG_MaxMeasures`] | "Medidas Máximas" globais |
| `lines` | Collection[`BTM_PG_StandardLine`] | Uma por linha de produto |
| `raw_attributes` | Collection[`BTM_PG_RawAttribute`] | Atributos importados não reconhecidos (`id`, `value` como texto) |

### 1.3 `BTM_PG_StandardLine`

| Campo | Tipo | Descrição |
|---|---|---|
| `code` | Enum `COZ` `DOR` `BAN` `SAL` `ESC` `BANC` `GAV` | Linha (Cozinhas, Dormitórios, Banheiros, Salas, Escritórios, Bancadas, Gavetas) |
| `external` | Pointer[`BTM_PG_ExternalDims`] | Alturas/profundidades por tipo de módulo |
| `sheets` | Collection[`BTM_PG_SheetComponent`] | Componentes de chapa (RN-24) |
| `components` | Collection[`BTM_PG_LineParam`] | Sarrafo, rodapé, moldura e demais parâmetros escalares/enumerados |

### 1.4 `BTM_PG_ExternalDims`

| Campo | Tipo | Exemplo BR |
|---|---|---|
| `base_height`, `base_depth` | Float LENGTH | 720 / 550 (inferior sem tampo) |
| `upper_low_height`, `upper_mid_height`, `upper_high_height`, `upper_depth` | Float LENGTH | 350 / 700 / 900 / 350 |
| `tall_height`, `tall_depth` | Float LENGTH | 2200 / 550 |
| `island_depth` | Float LENGTH | 900 |
| `top_overhang` | Float LENGTH | 20 (avanço do tampo) |
| `toe_kick_height`, `toe_kick_setback` | Float LENGTH | 100 / 50 |
| `install_height_upper` | Float LENGTH | 1500 (piso → base do aéreo) |

(Itens A–L de `docs/rag/promob/corpus/06-projeto-ii.md#6-1-2-como-definir-dimensoes-padroes`.)

### 1.5 `BTM_PG_SheetComponent`

| Campo | Tipo | Descrição | Promob |
|---|---|---|---|
| `code` | Enum `LAT` `DIV` `BAS` `FUN_INF` `FUN_SUP` `FUN_ALT` `TRAS` `TRA_TRAS` `PRAT` `POR` `PAI_POR` `FRE_GAV_INT` `FRE_FORNO` `TAMP` `TAMPON` `PAI` `ESP` | Componente | árvore "Chapas" |
| `material` | String (id do catálogo de materiais) | Ex.: `MDF` | `*_MAT_*` |
| `max_width` | Float LENGTH | Largura máxima da chapa (2730) | `*_L_*` |
| `max_length` | Float LENGTH | Comprimento máximo da chapa (1810) | `*_C_*` |
| `thickness` | Float LENGTH | 15 / 18 | `*_ESP_*` |
| `edge_1..edge_4` | Float LENGTH | Fita por lado: 1–2 = bordas do comprimento, 3–4 = bordas da largura (0,4) | `*_FIT_*_1A..4A` |

### 1.6 `BTM_PG_LineParam` e `BTM_PG_MaxMeasures`

| Campo | Tipo | Descrição |
|---|---|---|
| `key` | String | Chave do esquema (`data/dimension_schema.py`) |
| `value_float` / `value_enum` / `value_bool` | conforme o tipo do esquema | Valor |
| `overridden` | Bool | Diferente do valor da definição embutida de origem |

`BTM_PG_MaxMeasures`: `module_width_max`, `module_height_max`, `module_depth_max`, `sheet_width_max`, `sheet_length_max`.

### 1.7 Esquema de parâmetros (código, não dado) — `data/dimension_schema.py`

Registro por chave: `key, line, group (EXTERNAL/SHEET/COMPONENT/MAX), label_pt, label_en, unit, type (FLOAT/ENUM/BOOL),
default_br, default_us, min, max, step, precision, enum_items, zero_meaning, negative_allowed, image_key,
promob_codes[], legacy_targets[]` (`legacy_targets` = props legadas sincronizadas, ex.: `hb_frameless.default_carcass_part_thickness`).

### 1.8 `WindowManager.btm_standards_draft`

Cópia da definição ativa em edição + `pending_changes` (Collection: `key`, `old`, `new`, `impact_count`). Não é salva.

## 2. Campos novos em entidades existentes

| Entidade | Campo | Tipo | Descrição |
|---|---|---|---|
| Objeto raiz de módulo (frameless, closets, face_frame, `btm_*`) | `btm_uid` | ID prop String | UUID estável (RN-18) |
| idem | `btm_line` | ID prop String | Linha do padrão que o módulo segue |
| idem | `btm_overrides` | ID prop String (JSON de chaves) | Medidas sobrescritas que a sincronização não toca |
| Peça `GeoNodeCutpart` | `btm_component` | ID prop String | Componente do padrão (cache da classificação) |
| `Scene.btm_settings` | `btm_unit` | Enum (existente) | Passa a valer para todas as cotas e pré-visualizações |
| `Scene.btm_settings` | `cut_plan_stale` | Bool | Plano de corte desatualizado |

## 3. `NestingPart` (`cutting/nesting.py`)

| Campo | Situação | Descrição |
|---|---|---|
| `id` | alterado | Passa a ser `uid` estável `<btm_uid>/<papel>/<índice>` |
| `component` | novo | Código do componente |
| `edges` | novo | Lista de 4 espessuras (lados 1–2 comprimento, 3–4 largura); `edge_top/bottom/left/right` mantidos como aliases de leitura |
| `finish` | novo | Acabamento/cor; entra na chave de agrupamento de chapas (matéria-prima, espessura, acabamento) |
| `source` | novo | `CUTPART` / `SYNTHETIC` / `FREE_GEOMETRY` |
| `limit_status` | novo | `OK` / `EXCEEDS_WIDTH` / `EXCEEDS_LENGTH` |

## 4. Campos removidos (após migração)

| Entidade | Campo | Destino |
|---|---|---|
| `Scene.btm_settings` | `dimension_settings` (`BTM_PG_DimensionSettings`) | `btm_standards` (definição "Migrada") |
| `Scene.btm_settings` | `config_lateral/divisoria/base/fundo/prateleira/porta` (`BTM_PG_ComponentConfig`) | `sheets` da definição migrada (LAT, DIV, BAS, FUN_INF, PRAT, POR) |

## 5. Migrações

| ID | Quando | O quê | Reversível |
|---|---|---|---|
| M-01 | `load_post` | `dimension_settings` + `config_*` → definição `MIGRATED` ativa | Sim (props antigas mantidas 1 versão) |
| M-02 | `load_post` | Projeto sem definição: EUA (HB5) se houver gabinete legado, Brasil se não | Sim |
| M-03 | Primeira extração | `btm_uid` nos módulos sem ele | Sim (só adiciona) |
| M-04 | Importação de JSON v1 | Conversão em memória para v2 | n/a |

## 6. Sincronização (padrão → props legadas), incremento 1

| Chave do padrão | Destino legado |
|---|---|
| `COZ.sheets.LAT.thickness` (e demais caixa) | `Scene.hb_frameless.default_carcass_part_thickness` + prompts `Material Thickness` dos gabinetes (lógica de `hb_frameless.update_material_thickness_prompts`, extraída para função) |
| `COZ.external.base_height/base_depth`, `upper_*`, `tall_*` | `Scene.hb_frameless.base_cabinet_height/…` + lógica de `update_cabinet_sizes` (função) |
| `COZ.external.toe_kick_*` | `Scene.hb_frameless.default_toe_kick_height/_setback` + lógica de `hb_frameless.update_toe_kick_prompts` (função) |
| `COZ.external.install_height_upper` | `Scene.hb_frameless.default_wall_cabinet_location` |
| `DOR.sheets.LAT.thickness`, `PRAT` | `Scene.hb_closets.panel_thickness`, `shelf_thickness` + recálculo dos starters |
| `DOR.external.*` | `Scene.hb_closets.default_panel_depth`, alturas, `toe_kick_*` |

Tabela completa gerada a partir de `legacy_targets` do esquema; parâmetros sem destino entram no relatório de sincronização.


---

# Incremento 3 — bloco 1: Inspeção e movimento

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/` e o modelo do incremento 1. Roadmap: seção
> "Incremento 3 — bloco 1" (D-19 a D-32).

## I3-1. Entidades novas

### `BTM_PG_InspectionState` → `WindowManager.btm_inspection` (não salvo)

| Campo | Tipo | Descrição |
|---|---|---|
| `active` | Bool | Modo de inspeção em execução (lido pelo HUD e pelo pólo do gizmo) |
| `snap_stops` | Bool, padrão ligado | Encaixe em 0°/45°/90° no gizmo (Ctrl inverte durante o arraste) |
| `default_angle` | Enum `45`/`90`, padrão `90` | Ângulo de "Abrir tudo" e do clique no modo de inspeção |
| `interferences` | Coleção de `BTM_PG_Interference` | Último resultado do detector |
| `interference_index` | Int | Item ativo da lista |

### `BTM_PG_Interference`

| Campo | Tipo | Descrição |
|---|---|---|
| `front_name` | String | Objeto da frente |
| `module_name` | String | Módulo dono da frente |
| `hit_name` | String | Objeto atingido |
| `location` | FloatVector(3), `subtype='TRANSLATION'` | Ponto aproximado do choque (mundo, metros) |
| `kind` | Enum `DOOR`/`FLIP_UP`/`FLIP_DOWN`/`DRAWER`/`PULLOUT` | Tipo da frente |

### Tipo Python `inspection.fronts.Front` (sem persistência)

`kind`, `module_root`, `obj`, `pivot` (opcional), `hinge` (`LEFT`/`RIGHT`/`TOP`/`BOTTOM`/`NONE`), `max_value`
(90 ou curso em m), `library` (`FRAMELESS`/`FACE_FRAME`/`CLOSETS`/`BTM`), métodos `get()`, `apply(v)`, `commit(v)`,
`hinge_axis_world()` (para o gizmo e o envelope).

## I3-2. Campos novos em entidades existentes

| Entidade | Campo | Tipo | Observação |
|---|---|---|---|
| `Scene.btm_settings` (`BTM_PG_SceneSettings`) | `save_fronts_open` | Bool, padrão False | "Salvar com frentes abertas" — escolha explícita do RF-090 |
| Frente frameless (`CabinetDoor`, `CabinetFlipUpDoor`, `CabinetDrawerFront`, `CabinetPulloutFront`) | idprop `btm_open` | Float | Graus (articuladas) ou fração (gaveta/pullout); ausente = 0 |
| Frente frameless | `delta_rotation_euler`, `delta_location` | nativos do Blender | Pose de abertura; zero = fechada. Não são tocados pelos drivers de medida |
| Módulo rápido (`btm_cabinet`) | idprop `btm_open` na porta | Float | Espelho do valor canônico; `door_open` continua a fonte |

## I3-3. Campos alterados

| Entidade | Campo | Antes | Depois |
|---|---|---|---|
| Frente do closets (`CLOSET_DOOR_FRONT`) | `hb_door_open` | Int 0/1 | Float 0–1 (fração de `DOOR_OPEN_ANGLE`) |
| Frente do closets (`CLOSET_DRAWER_FRONT`) | `hb_drawer_open` | Int 0/1 | Float 0–1 (fração do curso) |
| `Scene.btm_settings.collision_global` | rótulo / efeito | "Evitar Colisões Físicas", sem efeito | "Evitar Sobreposição", lido pelo posicionamento (RN-13) |

Face frame: sem mudança (`Face_Frame_Opening_Props.swing_percent` já é Float 0–1; conversão graus = `swing_percent * 100`).

## I3-4. Migrações

| ID | Quando | O quê | Reversível |
|---|---|---|---|
| M-05 | Leitura | Closets: `hb_door_open`/`hb_drawer_open` inteiros lidos como 0,0/1,0 (sem regravar) | Sim |
| M-06 | Leitura | Frameless sem `btm_open`: fechada; `delta_*` não é alterado no carregamento | Sim |

## I3-5. Estado salvo × estado de inspeção

- `save_pre` fecha todas as frentes abertas (pose e valor confirmados em 0) e guarda numa lista em memória
  `(biblioteca, objeto, valor)`; `save_post` reaplica. Com `save_fronts_open` ligado, nada é feito.
- O detector de interferência não grava nada no arquivo além da coleção não salva em `WindowManager`.
