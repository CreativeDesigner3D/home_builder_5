"""Testes do classificador de tipo de objeto (T013): `caffmob_draw/selection/classify.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.selection import classify as c


class Obj(dict):
    """Objeto simulado: idprops via dict, `name`, `parent` e `btm_plane` opcional."""

    def __init__(self, name, parent=None, kind=None, **props):
        super().__init__(props)
        self.name = name
        self.parent = parent
        if kind:
            self.btm_plane = type('Plane', (), {'object_kind': kind})()


wall = Obj("Parede", IS_WALL_BP=True)
balcao = Obj("Balcao", wall, IS_FRAMELESS_CABINET_CAGE=True)
vao = Obj("Doors", balcao, IS_FRAMELESS_OPENING_CAGE=True)
porta = Obj("Left Door", vao, IS_DOOR_FRONT=True)
puxador = Obj("Pull", porta)
prateleira = Obj("Shelf", vao)
pivot = Obj("Front Pivot", Obj("Opening", Obj("FF", wall, IS_FACE_FRAME_CABINET_CAGE=True)), hb_part_role='FRONT_PIVOT')
janela = Obj("Janela", wall, IS_WINDOW_BP=True)
vidro = Obj("Vidro", janela)
rapido = Obj("BTM_Cabinet", kind='MODULE')
rapido_porta = Obj("BTM_Cabinet_Door_L", rapido)
cota = Obj("Dimension", balcao, IS_2D_ANNOTATION=True)


class ClassifyTest(unittest.TestCase):
    def check(self, obj, kind, root, library):
        info = c.classify(obj)
        self.assertEqual((info.kind, info.root.name, info.library), (kind, root, library))

    def test_precedencia(self):
        self.check(porta, c.FRONT, "Balcao", 'FRAMELESS')
        self.check(puxador, c.FRONT, "Balcao", 'FRAMELESS')         # filho da frente conta como a frente
        self.check(prateleira, c.PART, "Balcao", 'FRAMELESS')
        self.check(balcao, c.MODULE, "Balcao", 'FRAMELESS')         # módulo antes da parede
        self.check(pivot, c.FRONT, "FF", 'FACE_FRAME')
        self.check(wall, c.WALL, "Parede", 'HB')
        self.check(vidro, c.WINDOW, "Janela", 'HB')
        self.check(rapido_porta, c.FRONT, "BTM_Cabinet", 'BTM')
        self.check(cota, c.ANNOTATION, "Dimension", 'HB')

    def test_mover_sobre(self):
        self.assertIs(c.movable_root(puxador), balcao)
        self.assertIsNone(c.movable_root(wall))
        self.assertIs(c.reference_root(wall), wall)
        self.assertIsNone(c.movable_root(janela))
        self.assertIsNone(c.classify(None))
        self.assertEqual(c.classify(Obj("Solto")).kind, c.OTHER)


if __name__ == "__main__":
    unittest.main()
