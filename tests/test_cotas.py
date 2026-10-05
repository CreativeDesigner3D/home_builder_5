"""Testes das cotas de módulo na parede (T012): `blendertomob/measure/cotas.py`."""

import unittest

import _bootstrap  # noqa: F401
from blendertomob.measure import cotas as c

WALL = 3.0
CEILING = 2.6
# Balcão de 600 mm a partir de x = 1,0; vizinho de 0,2 a 0,8; janela alta de 2,0 a 2,8 (z 1,0–2,2); aéreo acima.
BALCAO = c.Placement(x0=1.0, width=0.6, z0=0.0, height=0.72, back_y=0.0)
OBST = [(0.2, 0.8, 0.0, 0.72), (2.0, 2.8, 1.0, 2.2), (1.0, 1.6, 1.4, 2.1)]


class CotasTest(unittest.TestCase):
    def test_calculo(self):
        cotas = c.compute(BALCAO, OBST, WALL, CEILING)
        self.assertAlmostEqual(cotas.anterior, 0.2)       # até o vizinho (termina em 0,8)
        self.assertAlmostEqual(cotas.posterior, 1.4)      # janela alta não conta (outra faixa de altura)
        self.assertAlmostEqual(cotas.inferior, 0.0)
        self.assertAlmostEqual(cotas.superior, 1.88)
        self.assertAlmostEqual(cotas.afastamento, 0.0)

    def test_cota_anterior_75mm(self):
        moved = c.apply('anterior', 0.075, BALCAO, OBST, WALL, CEILING)
        self.assertAlmostEqual(moved.x0, 0.875)
        self.assertAlmostEqual(moved.width, 0.6)          # dimensões preservadas
        self.assertAlmostEqual(c.compute(moved, OBST, WALL, CEILING).anterior, 0.075)

    def test_outras_cotas(self):
        self.assertAlmostEqual(c.apply('posterior', 0.1, BALCAO, OBST, WALL, CEILING).x0, 3.0 - 0.1 - 0.6)
        self.assertAlmostEqual(c.apply('inferior', 0.15, BALCAO, OBST, WALL, CEILING).z0, 0.15)
        self.assertAlmostEqual(c.apply('superior', 1.0, BALCAO, OBST, WALL, CEILING).z0, 2.6 - 1.0 - 0.72)
        self.assertAlmostEqual(c.apply('afastamento', 0.02, BALCAO, OBST, WALL, CEILING).back_y, -0.02)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            c.apply('anterior', -0.01, BALCAO, OBST, WALL, CEILING)
        with self.assertRaisesRegex(ValueError, "Valor Inválido"):
            c.apply('posterior', 2.6, BALCAO, OBST, WALL, CEILING)   # sairia da parede
        with self.assertRaises(ValueError):
            c.apply('superior', 2.5, BALCAO, OBST, WALL, CEILING)    # base abaixo do piso

    def test_modulo_livre(self):
        cotas = c.compute_free(BALCAO, CEILING)
        self.assertIsNone(cotas.anterior)
        self.assertAlmostEqual(cotas.superior, 1.88)

    def test_deslizar_na_parede(self):
        self.assertAlmostEqual(c.slide(BALCAO, OBST, WALL, 1.5), 1.5)
        self.assertAlmostEqual(c.slide(BALCAO, OBST, WALL, 0.0), 0.8)        # para no vizinho
        self.assertAlmostEqual(c.slide(BALCAO, OBST, WALL, 9.0), 2.4)        # janela alta não bloqueia
        self.assertAlmostEqual(c.slide(BALCAO, OBST, WALL, 0.0, avoid=False), 0.0)


if __name__ == "__main__":
    unittest.main()
