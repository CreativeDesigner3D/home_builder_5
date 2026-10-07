"""Testes do manifesto do módulo salvo (T013): `caffmob_draw/customize/manifest.py`."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.customize import manifest as mf
from caffmob_draw.customize import spec as sp


def sample_spec():
    s = sp.Spec(library='FRAMELESS')
    s.ensure_opening("bay0/opening0").door_style = "Vidro"
    return s


class ManifestTest(unittest.TestCase):
    def test_montar_e_ler(self):
        data = mf.build("Aéreo vidro 2P", "Aéreos", 'FRAMELESS', "Aéreo", sample_spec(),
                        materials=["Laca", "", "Laca"], pulls=["Perfil", sp.NO_PULL])
        self.assertEqual(data["materials"], ["Laca"])
        self.assertEqual(data["pulls"], ["Perfil"])
        loaded, spec, errors = mf.loads(mf.dumps(data))
        self.assertEqual(errors, [])
        self.assertEqual(loaded["name"], "Aéreo vidro 2P")
        self.assertEqual(spec.opening("bay0/opening0").door_style, "Vidro")

    def test_versao_maior_recusada(self):
        data = mf.build("A", "B", 'BTM', "A", sp.Spec())
        data["schema_version"] = "2.0.0"
        _d, spec, errors = mf.loads(json.dumps(data))
        self.assertIsNone(spec)
        self.assertTrue(any("não suportada" in e for e in errors))

    def test_formato_e_biblioteca(self):
        errors = mf.validate({"format": "x", "schema_version": "1.0.0", "library": "OUTRA", "name": "", "root_object": ""})
        self.assertEqual(len(errors), 4)

    def test_json_invalido(self):
        self.assertTrue(mf.loads("{")[2][0].startswith("JSON inválido"))

    def test_nome_de_arquivo(self):
        self.assertEqual(mf.file_stem('Aéreo 80/60: "vidro"?'), "Aéreo 80_60_ _vidro__")
        self.assertEqual(mf.file_stem(" ... "), "modulo")


if __name__ == "__main__":
    unittest.main()
