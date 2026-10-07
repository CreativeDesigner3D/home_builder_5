"""Identidade CAFFMob Draw (BUG-20261006-NO4Q e BUG-20261006-QAVK, fase A). Python puro.

Reprodução (falham antes da correção):
- o pacote é `caffmob_draw/`, com manifesto id `caffmob_draw` e nome "CAFFMob Draw";
- nenhum texto visível com os nomes antigos (constantes de texto e docstrings de classe; comentários e docstrings de
  módulo/função não aparecem para o usuário);
- todo operador tem `bl_idname` com prefixo `caffmob`;
- uma aba só na barra lateral: todo `bl_category` é "CAFFMob Draw" (o Editor de Paredes tem a própria janela).

Regressão:
- a migração copia as pastas de dados do usuário da extensão antiga só quando a nova está vazia.
"""

import ast
import importlib.util
import pathlib
import re
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "caffmob_draw"
OLD_NAMES = re.compile(r"Home Builder|Blender to Mob|Blender To Mob|BlenderToMob")
EDITOR_WINDOW_CATEGORY = "Editor de Paredes"


def package_sources():
    return [p for p in PACKAGE.rglob("*.py") if "__pycache__" not in p.parts]


def visible_strings(path):
    tree = ast.parse(path.read_text())
    hidden = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                hidden.add(id(first.value))
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in hidden]


class IdentidadeTest(unittest.TestCase):
    def test_pacote_e_manifesto(self):
        self.assertTrue(PACKAGE.is_dir(), "o pacote deve ser caffmob_draw/")
        text = (PACKAGE / "blender_manifest.toml").read_text()
        data = dict(re.findall(r'^(\w+)\s*=\s*"([^"]*)"', text, re.M))
        self.assertEqual(data["id"], "caffmob_draw")
        self.assertEqual(data["name"], "CAFFMob Draw")

    def test_sem_nome_antigo_visivel(self):
        found = [f"{p.relative_to(ROOT)}:{line}: {value[:60]!r}"
                 for p in package_sources() for line, value in visible_strings(p) if OLD_NAMES.search(value)]
        self.assertEqual(found, [])

    def test_operadores_com_prefixo_caffmob(self):
        wrong = []
        for p in package_sources():
            for m in re.finditer(r"bl_idname\s*=\s*['\"]([a-z0-9_]+)\.([a-z0-9_]+)['\"]", p.read_text()):
                if not m.group(1).startswith("caffmob"):
                    wrong.append(f"{p.relative_to(ROOT)}: {m.group(1)}.{m.group(2)}")
        self.assertEqual(wrong, [])

    def test_uma_aba_so(self):
        categories = set()
        for p in package_sources():
            categories |= set(re.findall(r"bl_category\s*=\s*['\"]([^'\"]+)['\"]", p.read_text()))
        self.assertEqual(categories - {EDITOR_WINDOW_CATEGORY}, {"CAFFMob Draw"})

    def test_migracao_copia_so_quando_vazio(self):
        spec = importlib.util.spec_from_file_location("compat_identity", PACKAGE / "compat_identity.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            old, new = pathlib.Path(tmp, "old"), pathlib.Path(tmp, "new")
            (old / "detail_library").mkdir(parents=True)
            (old / "detail_library" / "a.json").write_text("{}")
            self.assertTrue(mod.copy_if_empty(old / "detail_library", new / "detail_library"))
            self.assertTrue((new / "detail_library" / "a.json").exists())
            (old / "detail_library" / "b.json").write_text("{}")
            self.assertFalse(mod.copy_if_empty(old / "detail_library", new / "detail_library"))   # já tem dados
            self.assertFalse((new / "detail_library" / "b.json").exists())
            self.assertFalse(mod.copy_if_empty(old / "nao_existe", new / "x"))


if __name__ == "__main__":
    unittest.main()
