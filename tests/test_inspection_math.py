"""Testes da matemática de abertura de frentes (T052): `blendertomob/inspection/pivot_math.py`."""

import math
import unittest

import _bootstrap  # noqa: F401
from blendertomob.inspection import pivot_math as pm


def close(a, b, tol=1e-9):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def rotate_about_edge(point, euler_xyz, delta_location):
    """Aplica a pose (rotação delta no espaço do pai + delta de posição) a um ponto relativo à origem da peça."""
    rx, ry, rz = euler_xyz
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    m = ((cy * cz, sx * sy * cz - cx * sz, cx * sy * cz + sx * sz),
         (cy * sz, sx * sy * sz + cx * cz, cx * sy * sz - sx * cz),
         (-sy, sx * cy, cx * cy))
    return pm.add(pm.mat_vec(m, point), delta_location)


class ValoresTest(unittest.TestCase):
    def test_encaixe(self):
        self.assertEqual(pm.snap_angle(43.0), 45.0)
        self.assertEqual(pm.snap_angle(52.0), 52.0)
        self.assertEqual(pm.snap_angle(88.0), 90.0)
        self.assertEqual(pm.snap_angle(3.0), 0.0)
        self.assertEqual(pm.snap_angle(120.0), 90.0)

    def test_limites(self):
        self.assertEqual(pm.clamp_angle(-10), 0.0)
        self.assertEqual(pm.clamp_angle(95), 90.0)
        self.assertEqual(pm.clamp_fraction(1.5), 1.0)

    def test_conversoes_entre_linhas(self):
        self.assertAlmostEqual(pm.degrees_to_fraction(90, pm.FACE_FRAME_MAX_ANGLE), 0.9)
        self.assertAlmostEqual(pm.degrees_to_fraction(90, pm.CLOSETS_MAX_ANGLE), 90 / 110)
        self.assertAlmostEqual(pm.degrees_to_fraction(45, pm.BTM_MAX_ANGLE), 0.5)
        self.assertAlmostEqual(pm.fraction_to_degrees(0.9, pm.FACE_FRAME_MAX_ANGLE), 90.0)
        self.assertEqual(pm.fraction_to_degrees(1.0, pm.CLOSETS_MAX_ANGLE), 90.0)   # teto comum


class PoseTest(unittest.TestCase):
    # Porta frameless típica no espaço do pai: altura +Z, frente para −Y.
    def test_porta_esquerda_mantem_dobradica(self):
        hinge = pm.side_hinge((0, 0, 0.7), (0.45, 0, 0), (0, -0.019, 0))
        euler, offset = pm.pose_for(hinge, 90)
        self.assertTrue(close(offset, (0, 0, 0)))
        self.assertTrue(close(rotate_about_edge((0, 0, 0.7), euler, offset), (0, 0, 0.7)))   # aresta fica parada
        free = rotate_about_edge((0.45, 0, 0), euler, offset)
        self.assertTrue(close(free, (0, -0.45, 0), 1e-9))                                     # abre para a frente

    def test_porta_direita_abre_para_frente(self):
        hinge = pm.side_hinge((0, 0, 0.7), (-0.45, 0, 0), (0, -0.019, 0))
        euler, offset = pm.pose_for(hinge, 90)
        self.assertTrue(close(rotate_about_edge((-0.45, 0, 0), euler, offset), (0, -0.45, 0)))

    def test_basculante_sobe_ate_a_aresta_de_cima(self):
        hinge = pm.top_hinge((0, 0, 0.76), (0.9, 0, 0), (0, -0.019, 0))
        euler, offset = pm.pose_for(hinge, 90)
        top = rotate_about_edge((0, 0, 0.76), euler, offset)
        bottom = rotate_about_edge((0, 0, 0), euler, offset)
        self.assertTrue(close(top, (0, 0, 0.76)))                 # dobradiça parada
        self.assertTrue(close(bottom, (0, -0.76, 0.76)))          # borda de baixo vai para a frente, na altura do topo

    def test_fechada_e_identidade(self):
        hinge = pm.top_hinge((0, 0, 0.76), (0.9, 0, 0), (0, -0.019, 0))
        euler, offset = pm.pose_for(hinge, 0)
        self.assertTrue(close(euler, (0, 0, 0)) and close(offset, (0, 0, 0)))

    def test_euler_ida_e_volta(self):
        m = pm.axis_angle_matrix((0.3, 0.5, 0.8), 0.7)
        euler = pm.matrix_to_euler_xyz(m)
        v = (0.2, -0.4, 0.9)
        self.assertTrue(close(rotate_about_edge(v, euler, (0, 0, 0)), pm.mat_vec(m, v), 1e-9))

    def test_gaveta_desliza_pela_face(self):
        self.assertTrue(close(pm.slide((0, -0.019, 0), 0.5, 0.5), (0, -0.25, 0)))
        self.assertTrue(close(pm.slide((0, -1, 0), 0.5, 2.0), (0, -0.5, 0)))   # fração limitada a 1


if __name__ == "__main__":
    unittest.main()
