"""Testes dos limites do agregado (T014): `caffmob_draw/aggregates/limits.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import limits as lm

# Lateral de roupeiro: 18 mm em X, 600 mm de profundidade, 2 m de altura.
PANEL = ((0.0, 0.0, 0.0), (0.018, 0.6, 2.0))
NICHO = (0.10, 0.30, 0.40)


class LimitsTest(unittest.TestCase):
    def test_para_na_borda(self):
        u, v, off = lm.clamp(PANEL, NICHO, 'POS_X', 5.0, -1.0, 0.0)
        self.assertAlmostEqual(u, 0.6 - 0.30)
        self.assertEqual(v, 0.0)

    def test_afunda_ate_a_espessura(self):
        self.assertAlmostEqual(lm.clamp(PANEL, NICHO, 'POS_X', 0, 0, -0.010)[2], -0.010)
        self.assertAlmostEqual(lm.clamp(PANEL, NICHO, 'POS_X', 0, 0, -0.030)[2], -0.018)
        self.assertAlmostEqual(lm.clamp(PANEL, NICHO, 'POS_X', 0, 0, 0.5)[2], 0.5)

    def test_caixa_e_inverso_nas_seis_faces(self):
        parent = ((-0.4, -0.3, 0.0), (0.4, 0.3, 0.7))
        agg = (0.1, 0.05, 0.2)
        for face in lm.FACES:
            box = lm.box_for(parent, agg, face, 0.05, 0.02, -0.01)
            u, v, off = lm.params_from_box(parent, box, face)
            self.assertAlmostEqual(u, 0.05, msg=face)
            self.assertAlmostEqual(v, 0.02, msg=face)
            self.assertAlmostEqual(off, -0.01, msg=face)

    def test_afundado(self):
        box = lm.box_for(PANEL, NICHO, 'POS_X', 0.1, 0.1, -0.010)
        self.assertAlmostEqual(lm.sunk_depth(PANEL, box, 'POS_X'), 0.010)
        free = lm.box_for(PANEL, NICHO, 'POS_X', 0.1, 0.1, 0.002)
        self.assertIsNone(lm.sunk_box(PANEL, free, 'POS_X'))

    def test_maior_que_a_face(self):
        lim = lm.limits(PANEL, (0.1, 0.9, 0.4), 'POS_X')
        self.assertEqual(lim['u'], (0.0, 0.0))

    def test_face_mais_proxima(self):
        self.assertEqual(lm.nearest_face(PANEL, (0.05, 0.3, 1.0)), 'POS_X')
        self.assertEqual(lm.nearest_face(PANEL, (0.009, 0.3, 1.995)), 'POS_Z')


if __name__ == "__main__":
    unittest.main()
