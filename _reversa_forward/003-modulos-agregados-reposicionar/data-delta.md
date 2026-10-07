# Data delta: Módulos personalizáveis, agregados e Reposicionar

> Feature: `003-modulos-agregados-reposicionar` · Data: `2026-10-07`
> Base: `_reversa_sdd/data-dictionary.md`, `_reversa_sdd/erd-complete.md` e o mapeamento de código do `/reversa-plan`

Nada do legado é removido nem migrado. Todas as estruturas novas são `PropertyGroup` lidas por atributo
(regra do `CLAUDE.md`), registradas no `register()` e removidas no `unregister()`.

## 1. Novos PropertyGroups

### `Object.btm_custom` → `BTM_PG_CustomSpec` (D-03, D-06..D-09)

Fica no **vão** (opening cage) ou na **peça**; vazio = segue as seleções globais da biblioteca, como hoje.

| Campo | Tipo | Onde | Observação |
|---|---|---|---|
| `door_style` | String | vão | Nome do estilo de porta; vazio = estilo do módulo |
| `drawer_style` | String | vão | Nome do estilo de frente de gaveta |
| `pull_model` | String | vão | Nome do arquivo do puxador (`cabinet_pulls/`); `"__NONE__"` = sem puxador |
| `pull_position` | Enum `DEFAULT`/`TOP`/`MIDDLE`/`BOTTOM`/`SIDE` | vão | `DEFAULT` = regra da biblioteca |
| `pull_all_fronts` | Bool | módulo | "Aplicar a todas as frentes" |
| `front_material` | String | vão | Nome do material das frentes do vão |
| `material` | String | peça | Material da peça; vence o do grupo |
| `group_materials` | Coleção (`group` Enum CAIXA/FRENTES/FUNDO/INTERNO, `material` String) | módulo | Material por grupo |
| `interior_heights` | String (JSON, lista em metros) | vão | Alturas digitadas das prateleiras; vazio = espaçamento igual |

### `Object.btm_aggregate` → `BTM_PG_Aggregate` (D-12..D-19)

| Campo | Tipo | Observação |
|---|---|---|
| `is_aggregate` | Bool | Marca o objeto convertido |
| `kind` | Enum `AGGREGATE`/`LEAF` | `LEAF` = folha de porta |
| `parent_ref` | Pointer `Object` | Pai lógico (o pai Blender também é ele) |
| `face` | Enum `POS_X`/`NEG_X`/`POS_Y`/`NEG_Y`/`POS_Z`/`NEG_Z` | Face do pai em que está preso |
| `u`, `v` | Float (distância, m) | Posição na face; `update` aplica o clamp (RN-08) |
| `offset` | Float (distância, m) | > 0 afasta; < 0 afunda até −espessura do pai (RN-09) |
| `perforate` | Bool | Recorte 3D (D-13) |
| `real_hole` | Bool | Usinagem no plano de corte (D-14); só com `perforate` e pai `GeoNodeCutpart` |
| `production_part` | Bool | Entra no corte como geometria livre (D-15) |
| `cutter` | Pointer `Object` | Caixa cortadora oculta (`IS_CUTTING_OBJ`) |
| `orig_parent` | Pointer `Object` | Para desconverter (RN-12) |
| `orig_matrix` | FloatVector 16 | `matrix_world` antes da conversão |
| `motion` | Enum `SWING`/`SLIDE` | Só `LEAF` |
| `hinge` | Enum `LEFT`/`RIGHT`/`TOP`/`BOTTOM` | Giro |
| `swing_sign` | Enum `IN`/`OUT` | Sentido do giro |
| `max_angle` | Float (graus, 1–180, padrão 90) | Giro (D-18) |
| `slide_dir` | Enum `POS_X`/`NEG_X` | Correr |
| `travel` | Float (distância, m) | Curso do correr |
| `open_value` | Float 0–1 (fator, exibido em %) | Barra de abertura; `update` passa pela varredura (D-19) |
| `contact_name` | String (só leitura na UI) | Objeto da última batida; vazio = livre |
| `pivot` | Pointer `Object` | Empty da dobradiça/trilho |

### `Scene.btm_saved_positions` → coleção de `BTM_PG_SavedPosition` (D-22)

| Campo | Tipo |
|---|---|
| `name` | String |
| `delta` | FloatVector 3 (m, referencial de B) |
| `rotation` | Float (graus) |
| `b_side` | Enum `LEFT`/`RIGHT` (lado de B em que A estava) |

`Scene.btm_saved_positions_index`: Int (item ativo da lista).

### `WindowManager.btm_insertion_plane` → `BTM_PG_InsertionPlane` (D-24)

| Campo | Tipo |
|---|---|
| `active` | Bool |
| `matrix` | FloatVector 16 (origem e normal da face) |
| `source_name` | String (objeto de onde veio) |

Não persiste no arquivo (vive no `WindowManager`), coerente com RN-17 ("até o usuário trocar" na sessão).

## 2. Campos acrescentados a estruturas existentes

| Estrutura | Campo novo | Tipo | Observação |
|---|---|---|---|
| `Object.btm_cabinet` (`data/properties.py:258`) | `shelves` | Int 0–20 | Prateleiras geradas em `geometry/mesh_gen.py` (D-09) |
| `WindowManager.btm_move_over` (`move_over/props.py`) | `step` | Float (m, padrão 0,01) | Passo do teclado (RF-24) |
| `WindowManager.btm_move_over` | `show_relative` | Bool (padrão Verdadeiro) | RF-25 |

## 3. Idprops legados lidos/escritos (sem estrutura nova)

| Idprop | Biblioteca | Uso nesta feature |
|---|---|---|
| `hb_front_door_style`, `hb_front_drawer_style` (vão) | face frame | Escritos junto com `btm_custom` (o solver já respeita) |
| `DOOR_STYLE_NAME`, `DOOR_STYLE_INDEX` (frente) | frameless/face frame/closets | Lidos para preencher o `spec` inicial |
| `Pull Location`, `Handle Horizontal Location`, `* Pull Vertical Location` (frente) | frameless | Escritos por `pull_position` |
| `IS_CUTTING_OBJ` (cortador) | todas | Marca o cortador do Perfurar |
| `btm_open` (frente) | inspeção 001 | Também nas folhas convertidas |

## 4. Arquivos

- Novo diretório do usuário `modules/<categoria>/` com `.blend` + `.png` + `.json` (`interfaces/user-module-file.md`).
- JSON de produção `2.1.0` com `machining` (`interfaces/cut-plan-json.md`).

## 5. Migração

Nenhuma. Arquivos `.blend` antigos abrem com os PropertyGroups novos vazios; módulos sem `btm_custom` mantêm o
comportamento atual; o JSON `2.0.0` continua aceito.
