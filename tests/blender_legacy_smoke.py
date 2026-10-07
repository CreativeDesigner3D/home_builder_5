"""Valida calculadoras e duplicação de ambientes no Blender real."""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caffmob_draw as addon

addon.register()
addon.load_file_post(None)
obj = bpy.context.scene.objects['Cube']
calculator = obj.home_builder.add_calculator('Teste', obj)
calculator.add_calculator_prompt('A')
calculator.add_calculator_prompt('B')
obj.home_builder.calculator_distance = 1.2
calculator.calculate()
assert abs(calculator.prompts['A'].distance_value - 0.6) < 1e-6
variable = calculator.prompts['A'].get_var('Teste', 'a')
assert abs(obj.path_resolve(variable.data_path) - 0.6) < 1e-6
calculator.set_total_distance('2.0')
assert obj.animation_data.drivers[-1].data_path == 'home_builder.calculator_distance'
original = bpy.context.scene
assert bpy.ops.caffmob.duplicate_room(new_name='Ambiente de teste') == {'FINISHED'}
duplicate = bpy.context.window.scene
assert duplicate != original
assert duplicate.home_builder.sort_order > original.home_builder.sort_order
copied_mesh = next(item for item in duplicate.objects if item.type == 'MESH')
assert copied_mesh.data != obj.data
addon.unregister()
print('BLENDER_LEGACY_SMOKE_OK')
