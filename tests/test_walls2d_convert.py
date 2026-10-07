"""Testes da conversão das paredes da camada nova (T045): `caffmob_draw/walls2d/convert.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import convert


def seg(a, b, t=0.15, h=2.6):
    return {'start': a, 'end': b, 'thickness': t, 'height': h}


class ConversaoTest(unittest.TestCase):
    def test_um_trecho(self):
        (chain,) = convert.chains_from_segments([seg((0, 0), (3, 0), 0.2, 2.8)])
        # aberta: Direção esquerda; a face interna fica meia espessura à direita da linha de centro
        self.assertEqual(chain.side, 'LEFT')
        for (x, y), ex in zip(chain.nodes, (0.0, 3.0)):
            self.assertAlmostEqual(x, ex)
            self.assertAlmostEqual(y, -0.1)
        self.assertFalse(chain.closed)
        self.assertAlmostEqual(chain.segments[0].thickness, 0.2)
        self.assertAlmostEqual(chain.segments[0].height, 2.8)
        self.assertIsNone(chain.segments[0].source)

    def test_cadeia_aberta(self):
        (chain,) = convert.chains_from_segments([seg((0, 0), (2, 0)), seg((2, 0), (2, 2)), seg((2, 2), (0, 2))])
        self.assertEqual(chain.segment_count(), 3)
        self.assertFalse(chain.closed)
        self.assertEqual(len(chain.nodes), 4)

    def test_sala_fechada_fora_de_ordem(self):
        parts = [seg((4, 0), (4, 3)), seg((0, 3), (0, 0)), seg((0, 0), (4, 0)), seg((4, 3), (0, 3))]
        (chain,) = convert.chains_from_segments(parts)
        self.assertTrue(chain.closed)
        self.assertEqual(chain.segment_count(), 4)
        self.assertEqual(len(chain.nodes), 4)
        for i in range(4):
            a, b = chain.endpoints(i)
            self.assertTrue(abs(a[0] - b[0]) + abs(a[1] - b[1]) > 1.0)

    def test_sala_fechada_face_interna(self):
        # Linha de centro 4 × 3 com paredes de 0,2: a face interna é 3,8 × 2,8 e a espessura fica para fora.
        parts = [seg((0, 0), (4, 0), 0.2), seg((4, 0), (4, 3), 0.2), seg((4, 3), (0, 3), 0.2), seg((0, 3), (0, 0), 0.2)]
        (chain,) = convert.chains_from_segments(parts)
        self.assertEqual(chain.side, 'RIGHT')
        xs = [n[0] for n in chain.nodes]
        ys = [n[1] for n in chain.nodes]
        self.assertAlmostEqual(min(xs), 0.1)
        self.assertAlmostEqual(max(xs), 3.9)
        self.assertAlmostEqual(min(ys), 0.1)
        self.assertAlmostEqual(max(ys), 2.9)
        self.assertAlmostEqual(chain.face_length(0, 'OUTER'), 4.2)

    def test_tolerancia(self):
        joined = convert.chains_from_segments([seg((0, 0), (2, 0)), seg((2.005, 0), (2, 2))])
        self.assertEqual(len(joined), 1)
        apart = convert.chains_from_segments([seg((0, 0), (2, 0)), seg((2.02, 0), (2, 2))])
        self.assertEqual(len(apart), 2)


if __name__ == "__main__":
    unittest.main()
