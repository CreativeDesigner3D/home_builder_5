# Data Delta: 002-editor-parede-mover-sobre

> Diff conceitual sobre o modelo extraído em `_reversa_sdd/` (`data-dictionary.md`, `data-dictionary-legacy.md`) e o
> modelo da feature 001. Roadmap: D-01 a D-19.

## 1. Entidades novas

### `BTM_PG_MoveOverState` → `WindowManager.btm_move_over` (não salvo)

| Campo | Tipo | Descrição |
|---|---|---|
| `enabled` | Bool | Modo "Mover Sobre" ligado (lido pelo `poll` do keymap do botão direito, D-14) |
| `tolerance_px` | Int, padrão 12 | Distância em pixels para "perto de um alvo" (RN-06) |

O estado do diálogo (A, B, posição original de A, alvo em destaque, valores digitados) fica no operador modal, não
em propriedades.

### `BTM_PG_WallEditorState` → `WindowManager.btm_wall_editor` (não salvo)

| Campo | Tipo | Descrição |
|---|---|---|
| `tool` | Enum `SELECT`/`DRAW`/`ADD_NODE`/`REMOVE_NODE`/`INVERT`/`PAN` | Ferramenta ativa da barra |
| `grid_size` | Float (mm), padrão 1.000, 10–5.000 | Painel "Grid" — Tamanho |
| `magnetic` | Bool, padrão desligado | Painel "Grid" — Linhas Magnéticas |
| `selected_segment` | Int (−1 = nenhum) | Trecho selecionado no rascunho |
| `selected_line` | Enum `INNER`/`OUTER`/`REFERENCE` | Linha clicada (RN-15) |
| Campos do trecho: `length`, `angle_abs`, `angle_rel`, `arc_angle` (desabilitado, D-07), `lock_angle`, `thickness`, `height_start`, `height_end`, `orientation`, `wall_type` | conforme RN-18 | Espelho editável do trecho selecionado; `update` grava no rascunho |

O **rascunho** (grafo de nós e trechos) é um objeto Python em memória (`walls2d/model.py`), criado ao abrir e
descartado ao fechar (RN-16). Ele guarda também `references` (contorno das paredes da camada nova, só para ver) e
`converted_sources` (objetos da camada nova convertidos, removidos no OK); a sessão guarda `remove_modules` (D-21, D-22), `typed` (digitação direta, D-27) e a assinatura do rascunho na abertura
(`plan_signature`, para a confirmação do Cancelar, D-30), o pé-direito do projeto lido na abertura e a escolha
"Igualar ao pé-direito do projeto" (`equalize_height`, padrão verdadeiro, D-37). O padrão de `new_height` deixa de ser
2.600 mm fixo e passa a ser o pé-direito do projeto (D-36). Cada cadeia tem `side` (`LEFT`/`RIGHT`, Direção da espessura,
D-25) no lugar de `orientation`; os nós são a face interna.

### `BTM_PG_GeometryProps` → `Object.btm_geometry`

| Campo | Tipo | Descrição |
|---|---|---|
| `kind` | Enum `PLACA`/`CAIXA` | Forma (esclarecimento de 2026-10-05) |
| `width`, `height`, `depth` | Float (m) | Medidas da peça (caixa) |
| `thickness` | Float (m) | Espessura da placa; numa caixa de fabricação, espessura das seis placas que a formam |
| `fabrication` | Bool | "Peça de fabricação" (RN-14) |
| `component` | String | Código do componente do Padrão de Dimensões (001) |
| `material`, `finish` | String | Matéria-prima e acabamento |

O objeto usa `btm_plane.object_kind = 'GEOMETRY'` (valor que já existe em `data/properties.py`).

## 2. Campos novos em entidades existentes

| Entidade | Campo | Tipo | Observação |
|---|---|---|---|
| Parede do Home Builder 5 (`IS_WALL_BP`) | idprop `btm_wall_type` | String `NORMAL`/`DIVISORIA`/`MURETA` | Ausente = `NORMAL` (D-08) |
| Parede do Home Builder 5 | idprop `btm_wall_orientation` | String `RIGHT`/`LEFT`/`CENTER` | Ausente = `RIGHT` (D-06). **Revisão D-25:** deixa de ser gravado e lido; a Direção vem da geometria (legado = espessura à esquerda). Valores antigos ficam no arquivo, sem uso |
| Parede do Home Builder 5 | idprop `btm_wall_lowered` | Bool | Rebaixada (D-19); a parede fica escondida na viewport e uma filha `<parede>_Rebaixada` de 150 mm é mostrada |
| Parede/teto | `display_type` (nativo) | `WIRE` quando "invisível" (D-19) | Sem campo novo |
| Parede/teto | idprop `btm_display_prev` | String | Tipo de exibição antes do "invisível", para voltar ao "Visível" (D-19) |
| Filha da parede rebaixada | idprop `btm_lowered_proxy` | Bool | Marca a cópia de 150 mm (D-19, D-23) |
| Porta de ambiente (`IS_ENTRY_DOOR_BP`) | filho Empty com idprop `btm_room_door_pivot` (`'L'`/`'R'`) | Objeto | Pivô na dobradiça, criado no primeiro "Abrir"; a rotação Z é o ângulo de abertura (D-20) |
| Pivô da porta | filho malha com idprop `btm_room_door_leaf` | Objeto | Folha 3D (largura × espessura × altura), refeita a partir de `Dim X/Z` a cada "Abrir" (D-20) |
| Porta de ambiente | idprop `btm_open` | Float (graus) | Estado de abertura gravado pelo `commit` da inspeção, como nas outras frentes (D-20) |

## 3. Campos não usados (sem remoção)

| Entidade | Campo | Situação |
|---|---|---|
| `Scene.hb_wall_editor` (`HB_Wall_Editor_Props`, `hb_props.py:824`) | todos | Registrado e nunca lido; continua registrado nesta feature (remoção só com migração própria) |

## 4. Migrações

| ID | Quando | O quê | Reversível |
|---|---|---|---|
| M-07 | Leitura | Paredes sem `btm_wall_type`/`btm_wall_orientation` lidas como Normal/Direita | Sim |
| M-08 | Registro | `BTM_PT_ContextProperties` substituído por `BTM_PT_ObjectProperties` (sem dados) | Sim |
| M-09 | Primeiro "Abrir" de uma porta de ambiente | Cria pivô e folha filhos da porta (D-20); portas nunca abertas não mudam | Sim (apagar os filhos marcados) |
| M-12 | OK do editor | Cadeias abertas com fim a ≤ 0,01 m do início são fechadas antes de aplicar (D-35) | Sim (Ctrl+Z) |
| M-13 | OK do editor com "Igualar ao pé-direito do projeto" marcado | `Height`/`End Height` das paredes listadas passam ao pé-direito do projeto (D-37) | Sim (Ctrl+Z) |
| M-14 | Mudança do pé-direito nas Configurações | `Height`/`End Height` de toda parede de altura cheia (sem Mureta, `IS_HALF_WALL`, `IS_FAKE_WALL`) passam ao novo valor (D-38) | Sim (Ctrl+Z) |
| M-11 | Leitura | Paredes da cena entram no editor com Direção Esquerda (espessura à esquerda do sentido, como o legado cria); `btm_wall_orientation` é ignorado | Sim |
| M-10 | OK do editor com conversão aceita | Paredes da camada nova selecionadas viram paredes do Home Builder 5; o objeto original sai (D-22) | Sim (Ctrl+Z) |

## 5. Lista de peças

Geometria com `btm_geometry.fabrication = True` vira `NestingPart` pelo adaptador novo em `cutting/part_sources.py`:
- **placa:** uma peça, com comprimento e largura pelas duas maiores medidas e espessura pela menor;
- **caixa:** seis placas (fundo, tampo, duas laterais, frente e trás) com a espessura `thickness`, sem fitas.

As peças levam `source = "FREE_GEOMETRY"` e `module_uid = null` (JSON v2 da 001).
