"""Testes da regra do pé-direito do projeto (T077): `blendertomob/walls2d/heights.py`."""

import unittest

import _bootstrap  # noqa: F401
from blendertomob.walls2d import heights as h


def wall(name, height, end_height=None, btm=None, legacy=None):
    return {'name': name, 'height': height, 'end_height': height if end_height is None else end_height,
            'btm_wall_type': btm, 'legacy_wall_type': legacy}


class PeDireitoTest(unittest.TestCase):
    def test_quem_acompanha(self):
        self.assertTrue(h.follows_project_height(None, None))
        self.assertTrue(h.follows_project_height('NORMAL', 'Exterior'))
        self.assertTrue(h.follows_project_height('DIVISORIA', 'Interior'))
        self.assertFalse(h.follows_project_height('MURETA', None))
        self.assertFalse(h.follows_project_height(None, 'Half'))
        self.assertFalse(h.follows_project_height(None, 'Fake'))

    def test_lista_para_igualar(self):
        walls = [wall("A", 2.7), wall("B", 2.7005), wall("C", 2.702), wall("D", 2.7, end_height=2.5),
                 wall("Mureta", 1.1, btm='MURETA'), wall("Meia", 1.07, legacy='Half'), wall("Falsa", 0.86, legacy='Fake')]
        self.assertEqual(h.walls_to_equalize(walls, 2.7), ["C", "D"])


if __name__ == "__main__":
    unittest.main()
