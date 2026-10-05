"""Permite importar módulos puros de `blendertomob/` sem executar os `__init__.py` que dependem de `bpy`.

Registra pacotes vazios (`blendertomob`, `blendertomob.cutting`, …) em `sys.modules`; os submódulos são então
importados normalmente, inclusive com imports relativos entre eles.
Uso nos testes: `import _bootstrap  # noqa: F401` antes de `from blendertomob.data import units`.
"""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "blendertomob"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _stub(name, path):
    if name in sys.modules:
        return
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module


_stub("blendertomob", PACKAGE)
for _sub in ("cutting", "data", "standards", "inspection", "selection", "canvas2d", "move_over", "measure", "walls2d"):
    _stub(f"blendertomob.{_sub}", PACKAGE / _sub)
