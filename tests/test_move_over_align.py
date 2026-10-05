"""Testes do alinhamento do "Mover Sobre" (T011): `blendertomob/move_over/align.py`."""

import unittest

import _bootstrap  # noqa: F401
from blendertomob.canvas2d.view import View2D
from blendertomob.move_over import align as al

# B: balcão 600 × 550 × 720 (frente em Y = −0,55, fundo em Y = 0). A: aéreo 400 × 350 × 700, solto ao lado.
B = ((0.0, -0.55, 0.0), (0.6, 0.0, 0.72))
A = ((1.5, -0.40, 1.4), (1.9, -0.05, 2.1))


def moved(target_list, box_a=A, box_b=B, wall=False):
    return al.translate(box_a, al.combine(target_list, box_a, box_b, wall))


class AlinharTest(unittest.TestCase):
    def test_lados_sem_folga(self):
        right = moved([al.Target(al.RIGHT, None)])
        self.assertAlmostEqual(right[0][0], 0.6)
        left = moved([al.Target(al.LEFT, None)])
        self.assertAlmostEqual(left[1][0], 0.0)
        self.assertEqual(right[0][1:], A[0][1:])       # Y e Z não mudam

    def test_profundidades(self):
        for fraction in al.FRACTIONS:
            box = moved([al.Target(al.DEPTH, fraction)])
            self.assertAlmostEqual(box[0][1], -0.55 + fraction * 0.55)   # frente de A na linha de B

    def test_alturas_e_empilhar(self):
        self.assertAlmostEqual(moved([al.Target(al.HEIGHT, 0.5)])[0][2], 0.36)
        self.assertAlmostEqual(moved([al.Target(al.HEIGHT, 1.0)])[0][2], 0.72)
        self.assertAlmostEqual(moved([al.Target(al.STACK, None)])[0][2], 0.72)

    def test_lado_mais_profundidade(self):
        box = moved([al.Target(al.RIGHT, None), al.Target(al.DEPTH, 0.0)])
        self.assertAlmostEqual(box[0][0], 0.6)
        self.assertAlmostEqual(box[0][1], -0.55)

    def test_parede_como_referencia(self):
        wall = ((0.0, 0.0, 0.0), (3.0, 0.15, 2.6))     # face da parede em Y = 0
        lines = [t.kind for t, _seg in al.top_view_lines(wall, wall=True)]
        self.assertIn(al.WALL_FACE, lines)
        box = moved([al.Target(al.WALL_FACE, None)], box_b=wall, wall=True)
        self.assertAlmostEqual(box[1][1], 0.0)          # fundo de A encostado na face da parede

    def test_clique_e_tolerancia(self):
        view = View2D((0, 0, 400, 400), scale=200.0, center=(0.3, -0.3))
        lines_px = [(t, (view.to_screen(p0), view.to_screen(p1))) for t, (p0, p1) in al.top_view_lines(B)]
        right_px = view.to_screen((0.6, -0.3))
        hits = al.pick((right_px[0] + 11, right_px[1]), lines_px, 12)
        self.assertEqual([t.kind for t in hits], [al.RIGHT])
        self.assertEqual(al.pick((right_px[0] + 13, right_px[1]), lines_px, 12), [])
        corner = view.to_screen((0.6, -0.55))
        kinds = sorted(t.kind for t in al.pick((corner[0] + 3, corner[1] - 3), lines_px, 12))
        self.assertEqual(kinds, [al.DEPTH, al.RIGHT])   # perto do lado e da frente ao mesmo tempo

    def test_empilhar_pelo_clique(self):
        top = ((0.0, 0.72), (0.6, 0.72))
        view = View2D((0, 0, 400, 400), scale=200.0, center=(0.3, 0.5))
        top_px = (view.to_screen(top[0]), view.to_screen(top[1]))
        above = view.to_screen((0.3, 0.9))
        self.assertTrue(al.pick_stack(above, top_px, 12))
        self.assertFalse(al.pick_stack(view.to_screen((0.3, 0.73)), top_px, 12))
        self.assertFalse(al.pick_stack(view.to_screen((0.9, 0.9)), top_px, 12))

    def test_folgas_e_sobreposicao(self):
        dx, dy, dz = al.gaps(A, B)
        self.assertAlmostEqual(dx, 0.9)
        self.assertAlmostEqual(dy, 0.15)
        self.assertAlmostEqual(dz, 1.4)
        self.assertFalse(al.overlaps(moved([al.Target(al.RIGHT, None)]), B))
        inside = ((0.1, -0.5, 0.1), (0.5, -0.1, 0.6))
        self.assertTrue(al.overlaps(inside, B))


if __name__ == "__main__":
    unittest.main()
