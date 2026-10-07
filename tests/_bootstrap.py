"""Permite importar módulos puros de `caffmob_draw/` sem executar os `__init__.py` que dependem de `bpy`.

Registra pacotes vazios (`caffmob_draw`, `caffmob_draw.cutting`, …) em `sys.modules`; os submódulos são então
importados normalmente, inclusive com imports relativos entre eles.
Uso nos testes: `import _bootstrap  # noqa: F401` antes de `from caffmob_draw.data import units`.
"""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "caffmob_draw"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _stub(name, path):
    if name in sys.modules:
        return
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module


_stub("caffmob_draw", PACKAGE)
for _sub in ("cutting", "data", "standards", "inspection", "selection", "canvas2d", "move_over", "measure", "walls2d", "geometry"):
    _stub(f"caffmob_draw.{_sub}", PACKAGE / _sub)
