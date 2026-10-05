"""Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_smoke.py"""
import json
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blendertomob as addon
from blendertomob.cutting.part_extractor import extract_parts_from_scene

addon.register()
addon.load_file_post(None)
assert addon.hb_project.get_main_scene() is not None
assert 'wall_color' in addon.BTM_AddonPreferences.bl_rna.properties
assert 'dimension_settings' in bpy.context.scene.btm_settings.bl_rna.properties
assert extract_parts_from_scene(bpy.context) == [], 'Default cube must not produce cabinet parts'
assert bpy.ops.btm.cabinet_builder(width=0.9) == {'FINISHED'}
first = bpy.context.object
assert abs(first.btm_cabinet.width - 0.9) < 1e-6
assert len(first.data.vertices) > 0
assert bpy.ops.btm.cabinet_builder() == {'FINISHED'}
second = bpy.context.object
assert first != second
parts = extract_parts_from_scene(bpy.context)
assert len(parts) == 14, [(p.id, p.module_ref) for p in parts]
assert {p.module_ref for p in parts} == {first.name, second.name}
assert bpy.ops.btm.calculate_nesting() == {'FINISHED'}
cache = json.loads(bpy.context.scene['btm_nesting_json_cache'])
assert cache['stats']['total_placed_parts'] == 14
assert cache['stats']['unplaced_count'] == 0
with tempfile.TemporaryDirectory() as directory:
    output = str(Path(directory) / 'cut_plan.json')
    assert bpy.ops.btm.export_cut_plan_json(filepath=output) == {'FINISHED'}
    exported = json.loads(Path(output).read_text())
    assert exported['schema_version'] == '2.0.0'
    assert len(exported['parts']) == 14
    assert exported['cut_plan']['stats']['parts_placed'] == 14


def assert_clean_unregister():
    """T047: nada do add-on pode sobrar depois do unregister (propriedades, previews, handlers, timers)."""
    from blendertomob.cutting import stale
    from blendertomob.standards import migration, previews
    assert not hasattr(bpy.types.Scene, 'btm_settings')
    assert not hasattr(bpy.types.Scene, 'btm_standards')
    assert not hasattr(bpy.types.WindowManager, 'btm_standards_draft')
    assert previews._collection is None
    assert stale.depsgraph_update_post not in bpy.app.handlers.depsgraph_update_post
    assert addon.load_file_post not in bpy.app.handlers.load_post
    assert not bpy.app.timers.is_registered(migration._startup_timer)
    # Operadores e grupos de gizmo registrados em Python só aparecem pelo RNA (o nome da classe não vale).
    assert bpy.types.Operator.bl_rna_get_subclass_py('BTM_OT_standards_configurator') is None
    # Inspeção (T079): gizmo, estado, operadores, handlers de salvar, draw handlers e timer do gizmo.
    from blendertomob.inspection import gizmo, overlay, save_guard
    assert not hasattr(bpy.types.WindowManager, 'btm_inspection')
    assert bpy.types.GizmoGroup.bl_rna_get_subclass_py('BTM_GGT_front_open') is None
    assert bpy.types.Operator.bl_rna_get_subclass_py('BTM_OT_inspect_fronts') is None
    assert save_guard.save_pre not in bpy.app.handlers.save_pre
    assert save_guard.save_post not in bpy.app.handlers.save_post
    assert save_guard.save_post not in bpy.app.handlers.save_post_fail
    assert not overlay._handles
    assert not bpy.app.timers.is_registered(gizmo._commit_pending)
    assert bpy.types.UIList.bl_rna_get_subclass_py('BTM_UL_StandardsTree') is None


addon.unregister()
assert_clean_unregister()
for _ in range(2):
    addon.register()
    addon.load_file_post(None)
    assert bpy.context.scene.btm_standards.definitions, 'definições embutidas ausentes'
    addon.unregister()
    assert_clean_unregister()
print('BLENDER_SMOKE_OK', flush=True)
