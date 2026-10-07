"""Testes da folha 3D das portas de ambiente (T043): `caffmob_draw/inspection/room_door_math.py`.

As pontas esperadas vêm do símbolo `GeoNodeDoorSwing` medido no Blender 5.2: porta de 0,90 m em parede de 0,15 m,
folha aberta a 90° chega a y = −0,75 (para dentro) ou y = +0,90 (para fora).
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.inspection import room_door_math as rd

W, T, H, DOOR = 0.9, 0.15, 2.1, 0.0381


def tips(is_left, is_double, inside, degrees=90.0):
    return [rd.open_tip(leaf, degrees) for leaf in rd.leaves(W, T, H, is_left, is_double, inside, DOOR)]


class FolhaTest(unittest.TestCase):
    def assertPoint(self, got, expected):
        self.assertAlmostEqual(got[0], expected[0], places=6)
        self.assertAlmostEqual(got[1], expected[1], places=6)

    def test_simples_para_dentro(self):
        self.assertPoint(tips(True, False, True)[0], (0.9, 0.15 - 0.9))     # Is Left: dobradiça em x = largura
        self.assertPoint(tips(False, False, True)[0], (0.0, 0.15 - 0.9))

    def test_simples_para_fora(self):
        self.assertPoint(tips(True, False, False)[0], (0.9, 0.9))
        self.assertPoint(tips(False, False, False)[0], (0.0, 0.9))

    def test_dupla(self):
        inside = tips(False, True, True)
        self.assertEqual(len(inside), 2)
        self.assertPoint(inside[0], (0.0, 0.15 - 0.45))
        self.assertPoint(inside[1], (0.9, 0.15 - 0.45))
        outside = tips(False, True, False)
        self.assertPoint(outside[0], (0.0, 0.45))
        self.assertPoint(outside[1], (0.9, 0.45))

    def test_fechada_fica_no_vao(self):
        for combo in ((True, False, True), (False, False, False), (False, True, True)):
            for leaf in rd.leaves(W, T, H, *combo, DOOR):
                x, y = rd.open_tip(leaf, 0.0)
                self.assertTrue(-1e-9 <= x <= W + 1e-9)
                self.assertAlmostEqual(y, leaf.hinge_y)

    def test_espessura_do_lado_oposto_ao_giro(self):
        for inside in (True, False):
            leaf = rd.leaves(W, T, H, False, False, inside, DOOR)[0]
            ys = [c[1] for c in rd.leaf_corners(leaf)]
            self.assertAlmostEqual(max(abs(y) for y in ys), DOOR)
            self.assertEqual(leaf.dy, 1.0 if inside else -1.0)
            self.assertAlmostEqual(max(c[2] for c in rd.leaf_corners(leaf)), H)


if __name__ == "__main__":
    unittest.main()
