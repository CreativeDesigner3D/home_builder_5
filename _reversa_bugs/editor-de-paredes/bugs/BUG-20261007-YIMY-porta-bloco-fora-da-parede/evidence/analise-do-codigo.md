# Análise do código (2026-10-07, sem execução com janela)

Caminho dos botões "Porta Simples", "Porta Dupla", "Janela" e "Vão Livre" (`ui/panels.py:219-222`,
`ui/view3d_sidebar.py:433-441`):

- `operators/doors_windows.py:732-783` `_PlaceWallObjectBase.create_placed_object`: cria uma `GeoNodeCage`
  (`hb_types.py:539-552`), caixa Dim X/Y/Z sem batente nem folha, `hide_render=True`; com
  `show_entry_door_and_window_cages` (padrão True, `hb_props.py:498`) fica `TEXTURED` e `show_in_front`: o "bloco".
- Dim Y = `props.wall_thickness` (`:745`), depois a espessura da parede copiada uma vez (`:825-826`), sem driver.
- `:785-830` `set_position_on_wall`: filho da parede, `location=(x, 0, z)`; a gaiola cresce em +Y, como a parede.
- `:991` → `cut_wall` (`:429-446`): BOOLEAN DIFFERENCE EXACT com a própria gaiola como cortador, sempre ligado, faces
  coplanares às da parede; sem `IS_CUTTING_OBJ`.
- Folha 3D só existe no "Abrir" da inspeção (`inspection/room_door_leaf.py`).

Hipótese do deslocamento para fora (🟡): trocar a Direção de uma cadeia no editor 2D (`walls2d/props.py:146-151`,
`apply.py:106`) inverte os trechos (`model.py:173-181`, `hb_order`) e `apply_plan` mantém a matriz de mundo dos filhos
quando a parede gira mais de 90° (`apply.py:126-140`): a porta fica do lado antigo e a espessura da parede passa para o
outro lado.

Divergência de spec: `_reversa_sdd/domain.md` R-04 (cortador = 3 x espessura) descreve `operators/opening_builder.py`
(`caffmob.insert_opening`), que não tem botão na interface.
