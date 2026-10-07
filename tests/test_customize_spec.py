"""Testes da personalização por instância (T012): `caffmob_draw/customize/spec.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.customize import spec as sp


class SpecTest(unittest.TestCase):
    def sample(self):
        s = sp.Spec(library='FRAMELESS')
        item = s.ensure_opening("bay0/opening0")
        item.front, item.door_style, item.pull_model, item.pull_position = 'DOUBLE_DOORS', "Vidro", "Perfil 160", 'BOTTOM'
        item.interior = sp.Interior(shelves=2, heights=[0.25, 0.5])
        s.group_materials['CAIXA'] = "MDF carvalho"
        s.part_materials['bay0/back'] = "Branco"
        return s

    def test_ida_e_volta(self):
        s = self.sample()
        again = sp.from_dict(sp.to_dict(s))
        self.assertEqual(sp.to_dict(again), sp.to_dict(s))
        self.assertEqual(again.opening("bay0/opening0").interior.heights, [0.25, 0.5])

    def test_vao_sem_interior_nao_grava_chave(self):
        s = sp.Spec()
        s.ensure_opening("bay0/opening0").front = 'OPEN'
        self.assertNotIn('interior', sp.to_dict(s)['openings'][0])

    def test_valido(self):
        self.assertEqual(sp.validate(self.sample()), [])

    def test_invalidos(self):
        s = self.sample()
        s.opening("bay0/opening0").front = 'JANELA'
        s.ensure_opening("bay0/opening1").front = 'DRAWERS'          # sem quantidade
        s.group_materials['TETO'] = "X"
        s.part_materials['p'] = "  "
        errors = " | ".join(sp.validate(s))
        for text in ("frente desconhecida", "gavetas fora", "grupo de material desconhecido", "material vazio"):
            self.assertIn(text, errors)

    def test_vao_repetido(self):
        s = sp.Spec(openings=[sp.Opening("a"), sp.Opening("a")])
        self.assertTrue(any("repetido" in e for e in sp.validate(s)))

    def test_interior_alturas(self):
        self.assertTrue(sp.validate_interior(sp.Interior(shelves=2, heights=[0.5, 0.3])))       # decrescente
        self.assertTrue(sp.validate_interior(sp.Interior(shelves=3, heights=[0.2, 0.4])))       # quantidade
        self.assertTrue(sp.validate_interior(sp.Interior(shelves=1, heights=[0.8]), inner_height=0.7))  # fora
        self.assertEqual(sp.validate_interior(sp.Interior(shelves=1, heights=[0.3]), inner_height=0.7), [])

    def test_posicoes_iguais(self):
        pos = sp.shelf_positions(3, 0.72, 0.018)
        gap = (0.72 - 3 * 0.018) / 4
        self.assertAlmostEqual(pos[0], gap)
        self.assertAlmostEqual(pos[2] + 0.018 + gap, 0.72)
        self.assertEqual(sp.shelf_positions(2, 0.72, 0.018, [0.1, 0.4]), [0.1, 0.4])
        self.assertEqual(sp.shelf_positions(0, 0.72, 0.018), [])

    def test_grupos_e_interior_json(self):
        self.assertEqual(sp.group_of_component("POR"), 'FRENTES')
        self.assertEqual(sp.group_of_component("FUN_INF"), 'FUNDO')
        self.assertEqual(sp.group_of_component("PRAT"), 'INTERNO')
        self.assertEqual(sp.group_of_component("LAT"), 'CAIXA')
        inner = sp.Interior(shelves=2, drawers=1, heights=[0.2, 0.5])
        self.assertEqual(sp.interior_from_json(sp.interior_to_json(inner)), inner)
        self.assertIsNone(sp.interior_from_json("x"))
        self.assertIsNone(sp.interior_from_json(""))


if __name__ == "__main__":
    unittest.main()
