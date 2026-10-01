# Interfaces dos node groups embarcados

> Gerado pelo **Reversa** em 2026-09-30 ao responder a pergunta CORE-01 (`hb_core/questions.md` Q-01).
> Extraído com `blender --background` (5.2.0 LTS, Python 3.13.13) via `bpy.data.libraries.load` +
> `node_group.interface.items_tree`. 🟢 CONFIRMADO. Caminhos relativos a `blendertomob/geometry_nodes/`.

Use o **nome** com `compat.get_gn_input/set_gn_input`; o **identificador** só aparece em caminhos de driver
(`modifiers["M"].properties.inputs.<identificador>.value` no 5.2). Identificadores não seguem a ordem dos sockets.

| Arquivo | Versão do `.blend` | Node groups |
|---|---|---|
| `CabinetPartModifiers/CPM_3SIDEDNOTCH.blend` | 5.0.118 | `GeoNodeMVCutPart`, `CPM_3SIDEDNOTCH` |
| `CabinetPartModifiers/CPM_5PIECEDOOR.blend` | 5.0.118 | `GeoNodeMVCutPart.001`, `CPM_5PIECEDOOR` |
| `CabinetPartModifiers/CPM_CHAMFER.blend` | 5.0.118 | `GeoNodeMVCutPart.002`, `CPM_CHAMFER` |
| `CabinetPartModifiers/CPM_CORNERNOTCH.blend` | 5.0.118 | `GeoNodeCabinetPart`, `CPM_CORNERNOTCH` |
| `CabinetPartModifiers/CPM_CUTOUT.blend` | 5.0.118 | `GeoNodeMVCutPart.003`, `CPM_CUTOUT` |
| `CabinetPartModifiers/CPM_RADIUSNOTCH.blend` | 5.0.118 | `GeoNodeMVCutPart.004`, `CPM_RADIUSNOTCH` |
| `GeoNode5PieceDoor.blend` | 5.0.118 | `GeoNodeMVCutPart.005`, `GeoNode5PieceDoor` |
| `GeoNodeArrow.blend` | 5.1.29 | `GeoNodeArrow` |
| `GeoNodeCage.blend` | 5.0.118 | `GeoNodeCage` |
| `GeoNodeClosetRod.blend` | 5.1.29 | `GeoNodeClosetRod` |
| `GeoNodeCutpart.blend` | 5.0.118 | `GeoNodeCutpart` |
| `GeoNodeDimension.blend` | 5.1.29 | `GeoNodeDimension` |
| `GeoNodeDoorSwing.blend` | 5.0.118 | `GeoNodeDoorSwing` |
| `GeoNodeDrawerBox.blend` | 5.0.118 | `GeoNodeDrawerBox` |
| `GeoNodeHardware.blend` | 5.0.118 | `GeoNodeHardware` |
| `GeoNodeRectangle.blend` | 5.0.118 | `GeoNodeRectangle` |
| `GeoNodeWall.blend` | 5.1.29 | `GeoNodeWall` |

## `GeoNodeMVCutPart` — `CabinetPartModifiers/CPM_3SIDEDNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_3SIDEDNOTCH` — `CabinetPartModifiers/CPM_3SIDEDNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_3` | X | Float |
| entrada | `Socket_4` | Y | Float |
| entrada | `Socket_5` | Z | Float |
| entrada | `Socket_6` | End X | Float |
| entrada | `Socket_17` | End Y | Float |
| entrada | `Socket_22` | Flip Z | Bool |
| entrada | `Socket_23` | Flip Edge | Bool |
| entrada | `Socket_25` | Apply to Width | Bool |
| entrada | `Socket_24` | Material | Material |

## `GeoNodeMVCutPart.001` — `CabinetPartModifiers/CPM_5PIECEDOOR.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_5PIECEDOOR` — `CabinetPartModifiers/CPM_5PIECEDOOR.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_6` | Outer Profile | Object |
| entrada | `Socket_9` | Inner Profile | Object |
| entrada | `Socket_10` | Panel Profile | Object |
| entrada | `Socket_7` | Use Miter | Bool |
| entrada | `Socket_16` | Add Mid Rail | Bool |
| entrada | `Socket_17` | Center Mid Rail | Bool |
| entrada | `Socket_8` | Use Raised Panel | Bool |
| entrada | `Socket_2` | Left Stile Width | Float |
| entrada | `Socket_3` | Right Stile Width | Float |
| entrada | `Socket_4` | Top Rail Width | Float |
| entrada | `Socket_5` | Bottom Rail Width | Float |
| entrada | `Socket_18` | Mid Rail Width | Float |
| entrada | `Socket_19` | Mid Rail Location | Float |
| entrada | `Socket_14` | Panel Thickness | Float |
| entrada | `Socket_15` | Panel Inset | Float |
| entrada | `Socket_11` | Stile Material | Material |
| entrada | `Socket_12` | Rail Material | Material |
| entrada | `Socket_13` | Panel Material | Material |

## `GeoNodeMVCutPart.002` — `CabinetPartModifiers/CPM_CHAMFER.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_CHAMFER` — `CabinetPartModifiers/CPM_CHAMFER.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_3` | X | Float |
| entrada | `Socket_4` | Y | Float |
| entrada | `Socket_5` | Route Depth | Float |
| entrada | `Socket_15` | Flip X | Bool |
| entrada | `Socket_16` | Flip Y | Bool |
| entrada | `Socket_17` | Flip Z | Bool |
| entrada | `Socket_18` | Turn On | Bool |
| entrada | `Socket_19` | Material | Material |

## `GeoNodeCabinetPart` — `CabinetPartModifiers/CPM_CORNERNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_CORNERNOTCH` — `CabinetPartModifiers/CPM_CORNERNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_3` | X | Float |
| entrada | `Socket_4` | Y | Float |
| entrada | `Socket_5` | Route Depth | Float |
| entrada | `Socket_15` | Flip X | Bool |
| entrada | `Socket_16` | Flip Y | Bool |
| entrada | `Socket_17` | Flip Z | Bool |
| entrada | `Socket_19` | Material | Material |

## `GeoNodeMVCutPart.003` — `CabinetPartModifiers/CPM_CUTOUT.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_CUTOUT` — `CabinetPartModifiers/CPM_CUTOUT.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_21` | Face Name | Int |
| entrada | `Socket_3` | X | Float |
| entrada | `Socket_4` | Y | Float |
| entrada | `Socket_5` | Route Depth | Float |
| entrada | `Socket_6` | End X | Float |
| entrada | `Socket_17` | End Y | Float |
| entrada | `Socket_24` | Flip Z | Bool |
| entrada | `Socket_25` | Material | Material |

## `GeoNodeMVCutPart.004` — `CabinetPartModifiers/CPM_RADIUSNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `CPM_RADIUSNOTCH` — `CabinetPartModifiers/CPM_RADIUSNOTCH.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_3` | X | Float |
| entrada | `Socket_4` | Y | Float |
| entrada | `Socket_18` | Radius | Float |
| entrada | `Socket_19` | Resolution | Int |
| entrada | `Socket_5` | Route Depth | Float |
| entrada | `Socket_15` | Flip X | Bool |
| entrada | `Socket_16` | Flip Y | Bool |
| entrada | `Socket_17` | Flip Z | Bool |
| entrada | `Socket_20` | Turn On | Bool |
| entrada | `Socket_21` | Material | Material |

## `GeoNodeMVCutPart.005` — `GeoNode5PieceDoor.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `GeoNode5PieceDoor` — `GeoNode5PieceDoor.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_6` | Outer Profile | Object |
| entrada | `Socket_9` | Inner Profile | Object |
| entrada | `Socket_16` | Inner Top Bottom Profile | Object |
| entrada | `Socket_10` | Panel Profile | Object |
| entrada | `Socket_18` | Applied Profile | Object |
| entrada | `Socket_7` | Use Miter | Bool |
| entrada | `Socket_8` | Use Raised Panel | Bool |
| entrada | `Socket_2` | Left Stile Width | Float |
| entrada | `Socket_3` | Right Stile Width | Float |
| entrada | `Socket_4` | Top Rail Width | Float |
| entrada | `Socket_5` | Bottom Rail Width | Float |
| entrada | `Socket_14` | Panel Thickness | Float |
| entrada | `Socket_15` | Panel Inset | Float |
| entrada | `Socket_17` | Inner Profile Inset | Float |
| entrada | `Socket_11` | Stile Material | Material |
| entrada | `Socket_12` | Rail Material | Material |
| entrada | `Socket_13` | Panel Material | Material |

## `GeoNodeArrow` — `GeoNodeArrow.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_3` | Arrow Height | Float |
| entrada | `Input_4` | Arrow Length | Float |
| entrada | `Input_5` | Line Thickness | Float |
| entrada | `Input_7` | Material | Material |
| entrada | `Input_8` | Show Arrow | Bool |

## `GeoNodeCage` — `GeoNodeCage.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_2` | Dim X | Float |
| entrada | `Socket_3` | Dim Y | Float |
| entrada | `Socket_4` | Dim Z | Float |
| entrada | `Socket_5` | Mirror X | Bool |
| entrada | `Socket_6` | Mirror Y | Bool |
| entrada | `Socket_7` | Mirror Z | Bool |
| entrada | `Socket_8` | Show Cage | Bool |

## `GeoNodeClosetRod` — `GeoNodeClosetRod.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_2` | Dim X | Float |
| entrada | `Socket_3` | Radius | Float |
| entrada | `Socket_5` | Cup Depth | Float |
| entrada | `Socket_6` | Cup Depth 2 | Float |
| entrada | `Socket_7` | Is Oval | Bool |
| entrada | `Socket_4` | Material | Material |

## `GeoNodeCutpart` — `GeoNodeCutpart.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_3` | Width | Float |
| entrada | `Input_4` | Thickness | Float |
| entrada | `Input_5` | Mirror X | Bool |
| entrada | `Input_6` | Mirror Y | Bool |
| entrada | `Input_7` | Mirror Z | Bool |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Edge W1 | Material |
| entrada | `Input_11` | Edge W2 | Material |
| entrada | `Input_12` | Edge L1 | Material |
| entrada | `Input_13` | Edge L2 | Material |

## `GeoNodeDimension` — `GeoNodeDimension.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Socket_5` | Tick Length | Float |
| entrada | `Socket_6` | Tick Thickness | Float |
| entrada | `Input_5` | Leader Length | Float |
| entrada | `Input_6` | Line Thickness | Float |
| entrada | `Input_7` | Extend Line | Float |
| entrada | `Input_8` | Align Text To Curve | Bool |
| entrada | `Input_9` | Text Size | Float |
| entrada | `Input_10` | Offset Text From Line | Bool |
| entrada | `Input_11` | Offset Text Amount | Float |
| entrada | `Socket_4` | Offset Text X Amount | Float |
| entrada | `Socket_9` | Offset Start Point | Float |
| entrada | `Input_12` | Flip Arrows | Bool |
| entrada | `Input_14` | Decimals | Int |
| entrada | `Input_13` | Material | Material |
| entrada | `Input_15` | Flip Text | Bool |
| entrada | `Socket_0` | Additional Text | String |
| entrada | `Socket_1` | Additional Text Y Offset | Float |
| entrada | `Socket_3` | Additional Text X Offset | Float |
| entrada | `Socket_2` | Additional Text Size | Float |
| entrada | `Socket_7` | Unit Type | Int |
| entrada | `Socket_8` | Replace Text | String |

## `GeoNodeDoorSwing` — `GeoNodeDoorSwing.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_2` | Dim X | Float |
| entrada | `Socket_3` | Dim Y | Float |
| entrada | `Socket_4` | Is Double | Bool |
| entrada | `Socket_5` | Is Left | Bool |
| entrada | `Socket_6` | Swing Inside | Bool |
| entrada | `Socket_7` | Door Thickness | Float |

## `GeoNodeDrawerBox` — `GeoNodeDrawerBox.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_2` | Dim X | Float |
| entrada | `Socket_3` | Dim Y | Float |
| entrada | `Socket_4` | Dim Z | Float |
| entrada | `Socket_5` | Material Thickness | Float |
| entrada | `Socket_6` | Bottom Thickness | Float |
| entrada | `Socket_7` | Drawer Bottom Z Location | Float |
| entrada | `Socket_9` | Remove Subfront | Bool |
| entrada | `Socket_10` | Material | Material |

## `GeoNodeHardware` — `GeoNodeHardware.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_2` | Object | Object |

## `GeoNodeRectangle` — `GeoNodeRectangle.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Socket_1` | Geometry | Geometry |
| entrada | `Socket_0` | Geometry | Geometry |
| entrada | `Socket_3` | Dim X | Float |
| entrada | `Socket_4` | Dim Y | Float |
| entrada | `Socket_12` | Line Thickness | Float |
| entrada | `Socket_30` | Include X | Bool |
| entrada | `Socket_31` | Text | String |
| entrada | `Socket_32` | Text Size | Float |
| entrada | `Socket_35` | Text Y Offset | Float |
| entrada | `Socket_25` | Material | Material |
| entrada | `Socket_33` | Cutout Size | Vector |
| entrada | `Socket_34` | Cutout Location | Vector |

## `GeoNodeWall` — `GeoNodeWall.blend`

| E/S | Identificador | Nome | Tipo |
|---|---|---|---|
| saída | `Output_1` | Geometry | Geometry |
| entrada | `Input_0` | Geometry | Geometry |
| entrada | `Input_2` | Length | Float |
| entrada | `Input_4` | Height | Float |
| entrada | `Socket_2` | End Height | Float |
| entrada | `Input_3` | Thickness | Float |
| entrada | `Socket_0` | Left Angle | Float |
| entrada | `Socket_1` | Right Angle | Float |
| entrada | `Input_8` | Top Surface | Material |
| entrada | `Input_9` | Bottom Surface | Material |
| entrada | `Input_10` | Inside Face | Material |
| entrada | `Input_11` | Outside Face | Material |
| entrada | `Input_12` | Left Edge | Material |
| entrada | `Input_13` | Right Edge | Material |

## Achados

- 🟢 **Cota (`GeoNodeDimension`)**: `Socket_3` = *Additional Text X Offset*, `Socket_4` = *Offset Text X Amount*,
  `Socket_5` = *Tick Length*. `ops.py:172-184` ("Apply Settings to All") escreve tamanho de texto, tick e espessura
  nesses três identificadores — **inputs errados**. Corretos: *Text Size* (`Input_9`), *Tick Length* (`Socket_5`),
  *Line Thickness* (`Input_6`). Hoje o efeito é nulo só porque o filtro exige `MESH` e as cotas são `CURVE`.
- 🟢 **Parede (`GeoNodeWall`)**: os materiais são *Top/Bottom Surface*, *Inside/Outside Face*, *Left/Right Edge* — os
  mesmos de `update_wall_material` (`hb_props.py:211-225`). `GeoNodeWall.assign_materials` (`hb_types.py:468-478`)
  usa *Left/Right/Front/Back Surface*, que **não existem**.
- 🟢 Os `.blend` foram salvos no Blender 5.0.118 ou 5.1.29; nenhum contém drivers.
- 🟢 Cada `CPM_*` e `GeoNode5PieceDoor` traz junto um grupo auxiliar (`GeoNodeMVCutPart*`, `GeoNodeCabinetPart`), que
  ganha sufixo `.001`, `.002`… quando mais de um desses arquivos é carregado na mesma sessão (observado na extração).
