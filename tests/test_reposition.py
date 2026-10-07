"""Testes do reposicionamento do Mover Sobre ampliado (T016): `caffmob_draw/move_over/reposition.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.move_over import reposition as rp

B = ((0.0, -0.6, 0.0), (0.8, 0.0, 0.9))
A = ((0.95, -0.4, 0.2), (1.25, 0.0, 0.5))


class RepositionTest(unittest.TestCase):
    def test_rotacao_mantem_o_centro_da_base(self):
        center = rp.box_center_base(A)
        self.assertEqual(rp.origin_after_rotation(center, A, 90.0), center)
        x, y, z = rp.origin_after_rotation((A[0][0], A[0][1], A[0][2]), A, 90.0)
        self.assertAlmostEqual(x, center[0] + 0.2)
        self.assertAlmostEqual(y, center[1] - 0.15)

    def test_caixa_girada_90(self):
        lo, hi = rp.rotated_box(A, 90.0)
        self.assertAlmostEqual(hi[0] - lo[0], 0.4)
        self.assertAlmostEqual(hi[1] - lo[1], 0.3)
        self.assertAlmostEqual(lo[2], 0.2)

    def test_passo(self):
        self.assertEqual(rp.step_delta('RIGHT_ARROW', 0.01), (0.01, 0.0, 0.0))
        self.assertEqual(rp.step_delta('PAGE_DOWN', 0.01), (0.0, 0.0, -0.01))
        self.assertIsNone(rp.step_delta('A', 0.01))

    def test_absoluta_nao_move(self):
        shift = (10.0, 20.0, 0.0)
        values = rp.absolute_values(lambda p: tuple(p[i] + shift[i] for i in range(3)), A)
        self.assertAlmostEqual(values[0], 10.95)
        self.assertEqual(A[0][0], 0.95)

    def test_posicao_salva_em_outro_par(self):
        saved = rp.save_position(A, B, 0.0)
        self.assertEqual(saved['b_side'], 'RIGHT')
        self.assertAlmostEqual(saved['delta'][0], 0.15)
        other_b = ((2.0, -0.6, 0.0), (2.6, 0.0, 0.9))
        other_a = ((5.0, -0.4, 0.0), (5.3, 0.0, 0.3))
        d = rp.apply_position(saved, other_a, other_b)
        moved = tuple(tuple(c[i] + d[i] for i in range(3)) for c in other_a)
        self.assertAlmostEqual(moved[0][0] - other_b[1][0], 0.15)
        self.assertAlmostEqual(moved[0][2] - other_b[0][2], 0.2)

    def test_lado_esquerdo(self):
        left = ((-0.5, -0.4, 0.0), (-0.2, 0.0, 0.3))
        saved = rp.save_position(left, B, 0.0)
        self.assertEqual(saved['b_side'], 'LEFT')
        self.assertAlmostEqual(saved['delta'][0], -0.2)


if __name__ == "__main__":
    unittest.main()
