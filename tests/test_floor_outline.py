"""Testes do contorno do piso (BUG-20261007-A2G7): `caffmob_draw/geometry/floor_outline.py`.

Regressão: o piso segue a face interna das paredes, inclusive em sala côncava (L), nas duas camadas de parede.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.geometry import floor_outline as fo


def seg(a, b, t=0.15):
    return {'start': a, 'end': b, 'thickness': t, 'height': 2.6}


class FloorOutlineTest(unittest.TestCase):
    def test_laco_home_builder_espessura_para_fora(self):
        # horário: a espessura (à esquerda do sentido, +Y local) fica para fora; as origens já são a face interna
        poly = fo.hb_loop_inner([(0, 0), (0, 3), (4, 3), (4, 0)], [0.15] * 4)
        self.assertAlmostEqual(fo.area(poly), 12.0, places=6)
        self.assertTrue(fo.is_ccw(poly))

    def test_laco_home_builder_espessura_para_dentro(self):
        # anti-horário: a espessura cai para dentro; a face interna fica uma espessura para dentro
        poly = fo.hb_loop_inner([(0, 0), (4, 0), (4, 3), (0, 3)], [0.15] * 4)
        self.assertAlmostEqual(fo.area(poly), (4 - 0.3) * (3 - 0.3), places=6)

    def test_sala_em_l_nao_vira_fecho_convexo(self):
        poly = fo.hb_loop_inner([(0, 0), (0, 4), (2, 4), (2, 2), (4, 2), (4, 0)], [0.15] * 6)
        self.assertAlmostEqual(fo.area(poly), 12.0, places=6)      # convexo daria 14

    def test_camada_nova_pela_face_interna(self):
        pts = [(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4), (0, 0)]
        loops = fo.segments_inner_loops([seg(a, b) for a, b in zip(pts, pts[1:])])
        self.assertEqual(len(loops), 1)
        self.assertAlmostEqual(fo.area(loops[0]), 3.85 * 1.85 + 1.85 * 2.0, places=6)

    def test_camada_nova_cadeia_aberta_nao_fecha(self):
        self.assertEqual(fo.segments_inner_loops([seg((0, 0), (3, 0)), seg((3, 0), (3, 2))]), [])

    def test_retangulo_de_fallback(self):
        rect = fo.bounding_rect([(1, 1), (4, 1), (4, 3)])
        self.assertAlmostEqual(fo.area(rect), 6.0)
        self.assertIsNone(fo.bounding_rect([]))


if __name__ == "__main__":
    unittest.main()
