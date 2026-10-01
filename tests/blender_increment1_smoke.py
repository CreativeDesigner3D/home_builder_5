"""Teste de fumaça do incremento 1 da feature 001 (T012).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_increment1_smoke.py

Cobre: Padrão de Dimensões (definição embutida, rascunho, aplicação com sincronização), importação do Promob,
lista de peças a partir dos GeoNodeCutpart (frameless + closets), limite de chapa, plano de corte por acabamento,
exportação JSON v2 e CSV.
"""

import json
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import blendertomob as addon  # noqa: E402
from blendertomob.cutting import part_extractor  # noqa: E402
from blendertomob.standards import api as standards_api  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "dimensionexport_me_moveis.xml"

addon.register()
addon.load_file_post(None)
scene = bpy.context.scene

# 1. Projeto novo nasce no Padrão Brasil.
active = standards_api.active_definition(scene)
assert active is not None and active.name == "Padrão Brasil", active and active.name
assert standards_api.get_value(scene, 'COZ.sheets.LAT.thickness') == 15.0

# 2. Gabinetes: um balcão frameless e um roupeiro closets.
assert bpy.ops.btm.standards_duplicate() == {'FINISHED'}
assert standards_api.active_definition(scene).name.startswith("Padrão Brasil")
from blendertomob.product_libraries.frameless import types_frameless  # noqa: E402
from blendertomob.product_libraries.closets import types_closets  # noqa: E402

cabinet = types_frameless.BaseCabinet()
cabinet.create("Balcão Teste")
starter = types_closets.BaseClosetStarter()
starter.create_starter("Roupeiro Teste", bay_qty=2)
bpy.context.view_layer.update()

# 3. Aplicar definição com lateral 18 mm propaga aos gabinetes existentes.
draft = standards_api.begin_draft(scene, bpy.context.window_manager)
standards_api.set_draft_value(draft, 'COZ.sheets.LAT.thickness', 18.0)
standards_api.set_draft_value(draft, 'DOR.sheets.LAT.thickness', 18.0)
assert len(standards_api.pending_changes(scene, draft)) == 2
report = standards_api.apply_draft(scene, draft, include_manual=False)
assert report['modules_updated'] >= 2, report
assert abs(scene.hb_frameless.default_carcass_part_thickness - 0.018) < 1e-6
assert abs(scene.hb_closets.panel_thickness - 0.018) < 1e-6

# 4. Lista de peças real.
bpy.context.view_layer.update()
parts, incompatible = part_extractor.extract_production_parts(bpy.context)
assert parts, "nenhuma peça extraída"
assert all(p.source in ('CUTPART', 'SYNTHETIC', 'FREE_GEOMETRY') for p in parts)
assert len({p.uid for p in parts}) == len(parts), "uids repetidos"
laterals = [p for p in parts if p.component == 'LAT']
assert laterals and all(abs(p.thickness - 18.0) < 0.01 for p in laterals), [(p.name, p.thickness) for p in laterals]
again, _ = part_extractor.extract_production_parts(bpy.context)
assert [p.uid for p in again] == [p.uid for p in parts], "uids instáveis entre extrações"

# 5. Plano de corte, JSON v2 e CSV.
assert bpy.ops.btm.calculate_nesting() == {'FINISHED'}
assert not scene.btm_settings.cut_plan_stale
with tempfile.TemporaryDirectory() as directory:
    json_path = Path(directory) / 'projeto.json'
    assert bpy.ops.btm.export_cut_plan_json(filepath=str(json_path)) == {'FINISHED'}
    payload = json.loads(json_path.read_text(encoding='utf-8'))
    assert payload['schema_version'] == '2.0.0'
    assert len(payload['parts']) == len(parts)
    csv_path = Path(directory) / 'pecas.csv'
    assert bpy.ops.btm.export_parts_csv(filepath=str(csv_path)) == {'FINISHED'}
    assert csv_path.read_text(encoding='utf-8-sig').count('\n') == len(parts) + 1

# 6. Importar o padrão do Promob.
assert bpy.ops.btm.standards_import_promob(filepath=str(FIXTURE)) == {'FINISHED'}
names = [d.name for d in scene.btm_standards.definitions]
assert "ME MOVEIS - COZ. ESCR." in names, names

# 7. Registro limpo.
addon.unregister()
assert not hasattr(bpy.types.Scene, 'btm_standards')
addon.register()
addon.unregister()
print('BLENDER_INCREMENT1_SMOKE_OK', flush=True)
