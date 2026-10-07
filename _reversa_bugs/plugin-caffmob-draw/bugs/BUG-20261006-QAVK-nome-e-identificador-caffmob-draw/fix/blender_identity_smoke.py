"""Fumaça da identidade CAFFMob Draw no Blender (BUG-20261006-NO4Q e BUG-20261006-QAVK, fase A).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_identity_smoke.py

Regressão: o pacote `caffmob_draw` registra; os painéis do plugin na barra lateral da Viewport 3D estão numa aba só;
todo operador citado na interface existe; os MENU_ID gravados nos objetos (`HOME_BUILDER_MT_*`, nomes internos
mantidos na fase A) resolvem; dados gravados com os nomes internos sobrevivem a salvar e reabrir; o JSON novo sai com o
formato `caffmob_draw.*` e o formato antigo continua sendo aceito; desregistrar não deixa sobras.
"""

import os
import re
import sys
import tempfile
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
type(bpy.context.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0))

# 1. Uma aba só na barra lateral da Viewport 3D.
categories = {c.bl_category for c in bpy.types.Panel.__subclasses__()
              if c.__module__.startswith("caffmob_draw") and getattr(c, "bl_space_type", "") == 'VIEW_3D'
              and getattr(c, "bl_region_type", "") == 'UI' and hasattr(c, "bl_category")}
assert categories == {"CAFFMob Draw"}, categories

# 2. Todo operador citado na interface existe.
missing = set()
for path in (ROOT / "caffmob_draw").rglob("*.py"):
    for idname in re.findall(r'\.operator(?:_menu_enum)?\(\s*"([a-z0-9_]+\.[a-z0-9_]+)"', path.read_text()):
        module, name = idname.split(".")
        try:
            getattr(getattr(bpy.ops, module), name).get_rna_type()
        except (AttributeError, KeyError):
            missing.add(idname)
assert not missing, sorted(missing)

# 3. MENU_ID gravados continuam resolvendo.
menu_ids = set()
for path in (ROOT / "caffmob_draw").rglob("*.py"):
    menu_ids |= set(re.findall(r"\['MENU_ID'\]\s*=\s*['\"]([A-Za-z_]+)['\"]", path.read_text()))
unresolved = [m for m in menu_ids if bpy.types.Menu.bl_rna_get_subclass_py(m) is None and getattr(bpy.types, m, None) is None]
assert not unresolved, unresolved

# 4. Dados com os nomes internos sobrevivem a salvar e reabrir.
from caffmob_draw.walls2d import apply, model  # noqa: E402
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
apply.apply_plan(bpy.context, model.WallPlan([model.rectangle(3.0, 2.0)]))
bpy.context.scene.home_builder.ceiling_height = 2.7
path = os.path.join(tempfile.mkdtemp(), "identidade.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
walls = [o for o in bpy.context.scene.objects if o.get('IS_WALL_BP')]
assert len(walls) == 4 and abs(bpy.context.scene.home_builder.ceiling_height - 2.7) < 1e-6

# 5. JSON: formato novo na exportação, antigo aceito na leitura.
from caffmob_draw.cutting import json_exporter  # noqa: E402
from caffmob_draw.standards import io_json  # noqa: E402
assert json_exporter.FORMAT == "caffmob_draw.project", json_exporter.FORMAT
assert io_json.FORMAT == "caffmob_draw.dimension-standard", io_json.FORMAT
assert "blendertomob.project" in json_exporter.ACCEPTED_FORMATS
assert "blendertomob.dimension-standard" in io_json.ACCEPTED_FORMATS

# 6. Desregistrar sem sobras (pelo bl_idname).
addon.unregister()
leftover = []
for path in (ROOT / "caffmob_draw").rglob("*.py"):
    for idname in re.findall(r'bl_idname\s*=\s*["\']([a-z0-9_]+\.[a-z0-9_]+)["\']', path.read_text()):
        module, name = idname.split(".")
        try:
            getattr(getattr(bpy.ops, module), name).get_rna_type()
            leftover.append(idname)
        except (AttributeError, KeyError):
            pass
assert not leftover, leftover[:10]
print("blender_identity_smoke: OK")
