"""Testes do núcleo das telas 2D (T009): `caffmob_draw/canvas2d/view.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.canvas2d import view as v


class ViewTest(unittest.TestCase):
    def test_ida_e_volta(self):
        view = v.View2D((10, 20, 400, 300), scale=250.0, center=(1.0, -0.5))
        for point in [(0, 0), (1.2, -0.8), (-3, 4)]:
            back = view.to_world(view.to_screen(point))
            self.assertAlmostEqual(back[0], point[0])
            self.assertAlmostEqual(back[1], point[1])
        self.assertEqual(view.to_screen((1.0, -0.5)), (210.0, 170.0))   # centro do mundo no centro da área

    def test_pan_e_zoom_ancorado(self):
        view = v.View2D((0, 0, 400, 400), scale=100.0)
        anchor = (300.0, 250.0)
        before = view.to_world(anchor)
        view.zoom(2.0, anchor)
        after = view.to_world(anchor)
        self.assertAlmostEqual(before[0], after[0])
        self.assertAlmostEqual(before[1], after[1])
        view.pan(100, 0)
        self.assertAlmostEqual(view.to_world((300.0, 250.0))[0], before[0] - 100 / view.scale)

    def test_enquadrar(self):
        view = v.View2D((0, 0, 400, 200))
        view.fit(((0, 0), (4, 1)), margin=0.0)
        self.assertAlmostEqual(view.scale, 100.0)         # largura limita: 400 px / 4 m
        self.assertEqual(view.center, (2.0, 0.5))

    def test_trava_ortogonal(self):
        point, locked = v.ortho_snap((0, 0), (1.0, 0.0349))    # ~2°
        self.assertTrue(locked)
        self.assertAlmostEqual(point[1], 0.0)
        self.assertAlmostEqual(point[0], (1.0 ** 2 + 0.0349 ** 2) ** 0.5)
        _point, locked = v.ortho_snap((0, 0), (1.0, 0.0524))   # ~3°
        self.assertFalse(locked)
        point, locked = v.ortho_snap((0, 0), (-0.02, -2.0))    # perto de 270°
        self.assertTrue(locked)
        self.assertAlmostEqual(point[0], 0.0, places=9)

    def test_distancias_e_grade(self):
        self.assertAlmostEqual(v.distance_point_segment((5, 3), (0, 0), (10, 0)), 3.0)
        self.assertAlmostEqual(v.distance_point_segment((13, 4), (0, 0), (10, 0)), 5.0)
        self.assertEqual(v.snap_to_grid((1.26, 0.74), 0.5), (1.5, 0.5))
        view = v.View2D((0, 0, 400, 400), scale=100.0)
        xs, ys = view.grid_lines(1.0)
        self.assertIn(0.0, xs)
        self.assertIn(-2.0, ys)


if __name__ == "__main__":
    unittest.main()
