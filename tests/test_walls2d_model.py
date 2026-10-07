"""Testes do modelo de paredes do Editor de Paredes (T010, T058): `caffmob_draw/walls2d/model.py`."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import model as m


class ModeloTest(unittest.TestCase):
    def sala(self):
        # Sala de medidas internas 3.600 × 2.400, paredes de 150 mm, espessura para fora (externa 3.900 × 2.700).
        return m.rectangle(3.6, 2.4, thickness=0.15)

    def test_interna_e_externa(self):
        sala = self.sala()
        self.assertTrue(sala.is_ccw())
        self.assertEqual(sala.side, 'RIGHT')
        self.assertAlmostEqual(sala.face_length(0, m.INNER), 3.6)    # medida real = distância entre nós
        self.assertAlmostEqual(sala.face_length(1, m.INNER), 2.4)
        self.assertAlmostEqual(sala.face_length(0, m.OUTER), 3.9)    # externa = interna + espessuras
        self.assertAlmostEqual(sala.face_length(1, m.OUTER), 2.7)

    def test_espessura_para_fora_nos_dois_sentidos(self):
        anti = self.sala()
        self.assertEqual(anti.outward_side(), 'RIGHT')
        horario = m.Chain(list(reversed(anti.nodes)), anti.segments, closed=True, side='LEFT')
        self.assertFalse(horario.is_ccw())
        self.assertEqual(horario.outward_side(), 'LEFT')
        for sala in (anti, horario):
            (x0, y0), (x1, y1) = sala.outer_line(0)
            # a face externa fica fora do retângulo interno 0..3,6 × 0..2,4
            self.assertTrue(min(y0, y1) < -0.1 or max(y0, y1) > 2.5 or min(x0, x1) < -0.1 or max(x0, x1) > 3.7,
                            sala.outer_line(0))

    def test_direcao_troca_o_lado_sem_mudar_a_interna(self):
        sala = self.sala()
        sala.side = 'LEFT'                                          # espessura para dentro
        self.assertAlmostEqual(sala.face_length(0, m.INNER), 3.6)
        self.assertAlmostEqual(sala.face_length(0, m.OUTER), 3.3)

    def test_ordem_do_home_builder(self):
        sala = self.sala()
        nodes, segments = sala.hb_order()                           # RIGHT → invertida (HB põe à esquerda)
        twin = m.Chain(nodes, segments, closed=True, side='LEFT')
        self.assertFalse(twin.is_ccw())
        self.assertAlmostEqual(twin.face_length(0, m.OUTER), sala.face_length(3, m.OUTER))
        left = m.Chain([(0, 0), (2, 0)], [m.Segment()], side='LEFT')
        self.assertEqual(left.hb_order()[0], [(0.0, 0.0), (2.0, 0.0)])

    def test_angulos_e_esquadria(self):
        sala = self.sala()
        self.assertAlmostEqual(sala.angle_abs(1), 90.0)
        self.assertAlmostEqual(sala.angle_rel(1), 90.0)
        left, right = sala.miter_angles(0)
        self.assertAlmostEqual(left, math.pi / 4)
        self.assertAlmostEqual(right, -math.pi / 4)

    def test_comprimento_pela_face(self):
        sala = self.sala()
        sala.set_length(0, 4.1)                       # interna: o nó final anda no sentido da seta
        self.assertAlmostEqual(sala.nodes[1][0], 4.1)
        sala = self.sala()
        sala.set_length(1, 3.0, m.OUTER)              # externa 3.000; a interna cresce (o trecho de cima inclina)
        self.assertAlmostEqual(sala.face_length(1, m.OUTER), 3.0, places=6)
        self.assertGreater(sala.face_length(1, m.INNER), 2.6)

    def test_dividir_unir_inverter(self):
        aberta = m.Chain([(0, 0), (3.9, 0)], [m.Segment()])
        k = aberta.split(0, (1.5, 0.2))
        self.assertEqual(aberta.segment_count(), 2)
        self.assertAlmostEqual(aberta.length(0) + aberta.length(1), 3.9)
        aberta.remove_node(k)
        self.assertEqual(aberta.segment_count(), 1)
        self.assertAlmostEqual(aberta.length(0), 3.9)
        outer = aberta.outer_line(0)
        aberta.invert()                               # sentido oposto, parede no mesmo lugar
        self.assertEqual(aberta.nodes[0], (3.9, 0.0))
        self.assertEqual(aberta.side, 'RIGHT')
        self.assertAlmostEqual(aberta.outer_line(0)[0][1], outer[0][1])

    def test_fechar(self):
        cadeia = m.Chain([(0, 0), (3.9, 0), (3.9, 2.7), (0, 2.7), (0, 0)], [m.Segment() for _ in range(4)])
        cadeia.close()
        self.assertTrue(cadeia.closed)
        self.assertEqual(len(cadeia.nodes), 4)
        self.assertAlmostEqual(cadeia.length(3), 2.7)

    def test_bloquear_angulo(self):
        sala = self.sala()
        sala.segments[0].lock_angle = True
        sala.move_node(1, (4.5, 0.3))                 # sai da direção; só anda ao longo do trecho
        self.assertAlmostEqual(sala.nodes[1][1], 0.0)
        self.assertAlmostEqual(sala.nodes[1][0], 4.5)

    def test_validacao_e_tipos(self):
        sala = self.sala()
        with self.assertRaisesRegex(ValueError, "Valor Inválido"):
            sala.set_segment_value(0, 'thickness', 0.005)
        sala.set_segment_value(0, 'height', 2.8)
        self.assertAlmostEqual(sala.segments[0].end_height, 2.8)
        sala.set_segment_value(1, 'wall_type', 'MURETA')
        self.assertAlmostEqual(sala.segments[1].height, 1.10)
        with self.assertRaises(ValueError):
            sala.set_length(0, 0.0)
        with self.assertRaises(ValueError):
            m.Chain([(0, 0), (1, 0)], [m.Segment()], side='CENTER')

    def test_assinatura(self):
        plan = m.WallPlan([self.sala()])
        before = m.plan_signature(plan)
        plan.chains[0].set_length(0, 4.0)
        self.assertNotEqual(m.plan_signature(plan), before)
        plan.chains[0].set_length(0, 3.6)
        self.assertEqual(m.plan_signature(plan), before)
        plan.removed_sources.append("Wall")
        self.assertNotEqual(m.plan_signature(plan), before)


    def test_fechar_quando_encosta_no_inicio(self):
        aberta = m.Chain([(0, 0), (3, 0), (3, 2), (0, 2), (0.004, 0.003)], [m.Segment() for _ in range(4)])
        self.assertTrue(aberta.touches_start((0.004, 0.003)))
        self.assertFalse(aberta.touches_start((0.02, 0.0)))
        self.assertTrue(aberta.close_if_touching())
        self.assertTrue(aberta.closed)
        self.assertEqual(len(aberta.nodes), 4)
        curta = m.Chain([(0, 0), (3, 0), (0, 0.001)], [m.Segment(), m.Segment()])
        self.assertFalse(curta.close_if_touching())                 # 2 trechos não fecham
        longe = m.Chain([(0, 0), (3, 0), (3, 2), (0, 2), (0.05, 0)], [m.Segment() for _ in range(4)])
        self.assertFalse(longe.close_if_touching())


if __name__ == "__main__":
    unittest.main()
