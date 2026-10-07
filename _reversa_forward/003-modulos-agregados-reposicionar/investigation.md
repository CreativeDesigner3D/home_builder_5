# Investigation: Módulos personalizáveis, agregados e Reposicionar

> Feature: `003-modulos-agregados-reposicionar` · Data: `2026-10-07`

## 1. Estado do legado por biblioteca (mapeamento de código)

| Área | Frameless | Face frame | Closets | `btm` |
|---|---|---|---|---|
| Raiz | `IS_FRAMELESS_CABINET_CAGE` | `IS_FACE_FRAME_CABINET_CAGE` | `IS_CLOSET_STARTER_CAGE` | `btm_plane.object_kind == 'MODULE'` + `btm_cabinet` |
| Trocar frente | `change_opening_type` (`ops_opening.py:808`), recria os filhos do vão | `change_opening` (`ops_cabinet.py:2228`), `face_frame_opening.front_type` | `change_opening` → `apply_opening_config` (sem basculante/painel) | `door_swing` NONE/LEFT/RIGHT/DOUBLE/FLIP |
| Estilo de porta | Índice + nome (`DOOR_STYLE_INDEX`), frágil | Nome, override no vão (`hb_front_door_style`) | Global por cena | Não existe |
| Puxador | Posição por frente (idprops + drivers); modelo **global** | Modelo e posição **globais** | Globais | Não existe |
| Material | Por estilo de gabinete (índice) | Pintura por peça, só acabamento/interior do estilo | Global | `build_material` existe e nunca é chamado |
| Interiores | Prateleiras e divisórias; gavetas internas `TODO` | Os mais completos (prateleiras, rollouts, divisões, acessórios) | Prateleiras, varões, gavetas, nichos | Não existe |
| Reconstrução | Frentes ficam; posição por drivers | Solver recria frentes a cada recálculo | Starter inteiro recalculado | Malha única regenerada |
| Plano de corte | Sim | **Não** (`part_sources.py:72`) | Sim | Peças sintéticas |

Conclusão: a personalização precisa morar no vão (sobrevive à reconstrução) e ser reaplicada pelo adaptador (D-03,
D-04). O face frame fora do corte é um defeito do legado, não desta feature: registrar com `/reversa-debugger`.

## 2. Biblioteca do usuário

`frameless/operators/ops_library.py` e a cópia quase idêntica no face frame gravam com
`bpy.data.libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)` em `cabinet_groups/`, com miniatura
Workbench 256 px. A carga não recupera o estado de estilos por índice da cena de origem nem religa drivers para
objetos externos. Alternativas avaliadas:

| Alternativa | Prós | Contras | Decisão |
|---|---|---|---|
| Asset Browser nativo (`asset_mark`) | Interface pronta | Sem reaplicação de personalização nem resolução de estilos | descartada |
| Reaproveitar `cabinet_groups` como está | Zero código | Só frameless/face frame; índice errado em outro arquivo | descartada |
| **Mecânica comum + manifesto JSON** | Quatro bibliotecas, estilos por nome | Código novo em `customize/library_io.py` | **escolhida (D-10)** |

## 3. Recorte e usinagem

- `CPM_CUTOUT` (`geometry_nodes/CabinetPartModifiers/`) com `X`, `End X`, `Y`, `End Y`, `Route Depth`, `Flip Z`,
  adicionado por `GeoNodeCutpart.add_part_modifier`: aparece no 3D e é o primitivo de usinagem do legado.
- O exportador ignora modificadores CPM; `drilling` é sempre `[]` (`json_exporter.py:110`).
- Booleanas do legado: sempre `DIFFERENCE` + `EXACT`, cortador marcado `IS_CUTTING_OBJ` (excluído de posicionamento,
  seleção e exportação).

Escolha: Perfurar 3D por booleana com cortador em caixa (funciona com qualquer pai); furo real por `CPM_CUTOUT`
(só pai peça de corte) exportado em `machining` (D-13, D-14).

## 4. Abertura e colisão

- `inspection/pivot_math.py`: `edge_rotation`, `side_hinge`/`top_hinge`/`bottom_hinge`, `slide`, `MAX_ANGLE = 90`.
- `inspection/room_door_leaf.py`: pivô Empty + folha filha; abertura = rotação Z do pivô (padrão para a folha
  convertida).
- `inspection/interference.py`: amostra poses a cada 15°, cascas convexas encolhidas 1 mm (`envelope_hulls`),
  pré-filtro por caixa, `BVHTree.overlap`. Só relata; não para.

Escolha: varredura incremental com bissecção sobre as mesmas cascas (D-19). Física do Blender (rigid body) foi
descartada: precisa de simulação por quadros e não dá um valor de abertura determinístico.

## 5. Importação

O Blender 5.2 traz `bpy.ops.wm.obj_import`, `bpy.ops.import_scene.fbx` e `bpy.ops.import_scene.gltf`
(`docs/rag/blender-api/corpus/bpy.ops.wm.md#bpy.ops.wm.obj_import`,
`docs/rag/blender-api/corpus/bpy.ops.import_scene.md#bpy.ops.import_scene.fbx`,
`docs/rag/blender-api/corpus/bpy.ops.import_scene.md#bpy.ops.import_scene.gltf`). Não há leitor `.skp`; arquivos do
SketchUp chegam exportados ou por outro addon, e a conversão aceita qualquer malha (Esclarecimentos Q1).

## 6. Referência Promob

`docs/elicitação-requisitos-reposicionamento-3d.md`: RF-001..RF-022, máquina de estados §11, riscos R-01..R-06.
Mitigações adotadas: R-01 (referencial de B explícito, D-21), R-02 (rotação em torno do centro da base com filhos
preservados), R-03 (cotas recalculadas a cada desenho, D-26), R-05 (botão no painel além do botão direito).

## 7. Custo

Nenhum componente de IA ou serviço externo; sem custo recorrente de tokens ou API. O custo é de desenvolvimento e
manutenção: quatro adaptadores de biblioteca são o item mais caro, por isso entram um de cada vez (I2).
