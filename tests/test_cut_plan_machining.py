"""Testes da usinagem de agregados no JSON de produção (T018): `caffmob_draw/cutting/machining.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cutting import machining as mc


def cut(name, x, ex, y, ey, depth, flip=False):
    return {'name': name, 'x': x, 'end_x': ex, 'y': y, 'end_y': ey, 'depth': depth, 'flip_z': flip}


class MachiningTest(unittest.TestCase):
    def test_bolsao(self):
        out, clipped = mc.entries([cut("Nicho", 0.12, 0.52, 0.3, 0.5, 0.010)], 2.0, 0.6, 0.018)
        self.assertFalse(clipped)
        e = out[0]
        self.assertEqual((e["kind"], e["face"], e["through"]), ("POCKET", "TOP", False))
        self.assertEqual((e["x_mm"], e["y_mm"], e["end_x_mm"], e["end_y_mm"], e["depth_mm"]),
                         (120.0, 300.0, 520.0, 500.0, 10.0))

    def test_passante(self):
        out, _ = mc.entries([cut("Furo", 0.1, 0.2, 0.1, 0.2, 0.030, flip=True)], 1.0, 0.5, 0.018)
        self.assertEqual((out[0]["kind"], out[0]["depth_mm"], out[0]["face"]), ("THROUGH_CUT", 18.0, "BOTTOM"))

    def test_fora_da_peca(self):
        out, clipped = mc.entries([cut("A", -0.1, 0.1, 0.4, 0.8, 0.005)], 1.0, 0.6, 0.018)
        self.assertTrue(clipped)
        self.assertEqual((out[0]["x_mm"], out[0]["end_y_mm"]), (0.0, 600.0))
        out, clipped = mc.entries([cut("B", 2.0, 2.1, 0.1, 0.2, 0.005)], 1.0, 0.6, 0.018)
        self.assertEqual((out, clipped), ([], True))

    def test_ordem_estavel(self):
        cuts = [cut("B", 0.1, 0.2, 0.1, 0.2, 0.01), cut("A", 0.5, 0.6, 0.1, 0.2, 0.01), cut("A", 0.1, 0.2, 0.1, 0.2, 0.01)]
        names = [(e["source_name"], e["x_mm"]) for e in mc.entries(cuts, 1.0, 0.6, 0.018)[0]]
        self.assertEqual(names, [("A", 100.0), ("A", 500.0), ("B", 100.0)])

    def test_nome_do_agregado(self):
        self.assertEqual(mc.source_name("Agregado: Nicho"), "Nicho")
        self.assertIsNone(mc.source_name("Cutout"))


if __name__ == "__main__":
    unittest.main()
