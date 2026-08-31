"""Run with Blender:

blender --background --factory-startup --python tests/test_semantic_edges.py
"""

import os
import sys
import unittest
from types import SimpleNamespace

import bpy
from mathutils import Matrix

PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from semantic_lines import semantic_edges
from semantic_lines import semantic_edge_overlay
from semantic_lines import semantic_line_render


def make_mesh(name, vertices, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


class SemanticEdgeExtractionTests(unittest.TestCase):
    def tearDown(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        for mesh in list(bpy.data.meshes):
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)

    def test_quad_boundary_edges_are_semantic(self):
        obj = make_mesh('Quad', [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                        [(0, 1, 2, 3)])
        edges = semantic_edges.extract_semantic_edges(obj)
        self.assertEqual(4, len(edges))
        self.assertEqual({semantic_edges.EDGE_BOUNDARY},
                         {edge.edge_class for edge in edges})

    def test_coplanar_triangulation_diagonal_is_excluded(self):
        obj = make_mesh('TriangulatedQuad',
                        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                        [(0, 1, 2), (0, 2, 3)])
        edges = semantic_edges.extract_semantic_edges(obj)
        self.assertEqual(4, len(edges))
        self.assertNotIn((0, 2), {edge.topology_vertices for edge in edges})

    def test_sharp_shared_edge_is_semantic(self):
        obj = make_mesh('Fold', [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
                        [(0, 1, 2), (0, 3, 1)])
        edges = semantic_edges.extract_semantic_edges(obj)
        shared = [edge for edge in edges if edge.topology_vertices == (0, 1)]
        self.assertEqual(1, len(shared))
        self.assertEqual(semantic_edges.EDGE_SHARP, shared[0].edge_class)

    def test_user_mark_preserves_coplanar_internal_edge(self):
        obj = make_mesh('MarkedTriangulation',
                        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                        [(0, 1, 2), (0, 2, 3)])
        attr = obj.data.attributes.new(semantic_edges.USER_MARKED_ATTRIBUTE,
                                       'BOOLEAN', 'EDGE')
        diagonal = next(edge for edge in obj.data.edges
                        if tuple(sorted(edge.vertices[:])) == (0, 2))
        attr.data[diagonal.index].value = True
        edges = semantic_edges.extract_semantic_edges(obj)
        marked = [edge for edge in edges if edge.topology_vertices == (0, 2)]
        self.assertEqual(1, len(marked))
        self.assertEqual(semantic_edges.EDGE_USER_MARKED, marked[0].edge_class)

    def test_source_uid_and_edge_uid_remain_stable(self):
        obj = make_mesh('Stable', [(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                        [(0, 1, 2)])
        first = semantic_edges.extract_semantic_edges(obj)
        second = semantic_edges.extract_semantic_edges(obj)
        self.assertEqual(obj[semantic_edges.SOURCE_UID_PROPERTY],
                         first[0].source_object_uid)
        self.assertEqual([edge.uid for edge in first],
                         [edge.uid for edge in second])

    def test_endpoints_are_returned_in_world_space(self):
        obj = make_mesh('Translated', [(0, 0, 0), (1, 0, 0), (0, 1, 0)],
                        [(0, 1, 2)])
        obj.location = (5, -2, 3)
        bpy.context.view_layer.update()
        edge = next(edge for edge in semantic_edges.extract_semantic_edges(obj)
                    if edge.topology_vertices == (0, 1))
        self.assertEqual((5.0, -2.0, 3.0), edge.start)
        self.assertEqual((6.0, -2.0, 3.0), edge.end)

    def test_overlay_test_objects_cover_the_first_edge_cases(self):
        box, panel, fold, marked = semantic_edge_overlay.create_semantic_edge_test_objects(
            bpy.context)
        self.assertEqual(12, len(semantic_edges.extract_semantic_edges(box)))
        panel_edges = semantic_edges.extract_semantic_edges(panel)
        self.assertNotIn((0, 2), {edge.topology_vertices for edge in panel_edges})
        self.assertIn(semantic_edges.EDGE_SHARP,
                      {edge.edge_class for edge in semantic_edges.extract_semantic_edges(fold)})
        self.assertIn(semantic_edges.EDGE_USER_MARKED,
                      {edge.edge_class for edge in semantic_edges.extract_semantic_edges(marked)})

    def test_visibility_runs_split_at_sample_transition_midpoints(self):
        self.assertEqual(
            ((0.0, 0.5, semantic_edge_overlay.VISIBLE),
             (0.5, 1.0, semantic_edge_overlay.HIDDEN)),
            semantic_edge_overlay.visibility_runs([True, True, False, False]))

    def test_visibility_changes_at_edge_endpoints_do_not_overdraw_corners(self):
        self.assertEqual(
            ((0.0, 1.0, semantic_edge_overlay.HIDDEN),),
            semantic_edge_overlay.visibility_runs([True, False, False, False]))
        self.assertEqual(
            ((0.0, 1.0, semantic_edge_overlay.HIDDEN),),
            semantic_edge_overlay.visibility_runs([False, False, False, True]))

    def test_hidden_dashes_are_generated_in_screen_space(self):
        dashes = semantic_edge_overlay.dashed_screen_segments(
            (0.0, 0.0), (20.0, 0.0), dash_length=5.0, gap_length=5.0)
        self.assertEqual((((0.0, 0.0), (5.0, 0.0)),
                          ((10.0, 0.0), (15.0, 0.0))), dashes)

    def test_offscreen_segments_are_rejected_before_visibility_sampling(self):
        region = SimpleNamespace(width=100, height=100)
        self.assertFalse(semantic_edge_overlay._segment_intersects_region(
            SimpleNamespace(x=-20.0, y=10.0),
            SimpleNamespace(x=-5.0, y=40.0), region))
        self.assertTrue(semantic_edge_overlay._segment_intersects_region(
            SimpleNamespace(x=-20.0, y=50.0),
            SimpleNamespace(x=120.0, y=50.0), region))

    def test_visibility_sample_count_adapts_to_projected_length(self):
        short_start = SimpleNamespace(x=0.0, y=0.0)
        short_end = SimpleNamespace(x=20.0, y=0.0)
        long_end = SimpleNamespace(x=480.0, y=0.0)
        self.assertEqual(3, semantic_edge_overlay.visibility_sample_count(
            17, short_start, short_end))
        self.assertEqual(7, semantic_edge_overlay.visibility_sample_count(
            17, short_start, long_end))
        self.assertEqual(5, semantic_edge_overlay.visibility_sample_count(
            5, short_start, long_end))

    def test_fully_aligned_hidden_line_is_suppressed(self):
        visible = semantic_edge_overlay.ProjectedEdgeSegment(
            'front', (0.0, 0.0), (20.0, 0.0), semantic_edge_overlay.VISIBLE)
        hidden = semantic_edge_overlay.ProjectedEdgeSegment(
            'back', (0.0, 0.0), (20.0, 0.0), semantic_edge_overlay.HIDDEN)
        self.assertEqual((visible,),
                         semantic_edge_overlay.suppress_aligned_hidden_segments(
                             (visible, hidden)))

    def test_offset_or_partially_covered_hidden_line_is_retained(self):
        visible = semantic_edge_overlay.ProjectedEdgeSegment(
            'front', (0.0, 0.0), (10.0, 0.0), semantic_edge_overlay.VISIBLE)
        offset_hidden = semantic_edge_overlay.ProjectedEdgeSegment(
            'offset', (0.0, 2.0), (20.0, 2.0), semantic_edge_overlay.HIDDEN)
        partial_hidden = semantic_edge_overlay.ProjectedEdgeSegment(
            'partial', (0.0, 0.0), (20.0, 0.0), semantic_edge_overlay.HIDDEN)
        self.assertEqual((visible, offset_hidden, partial_hidden),
                         semantic_edge_overlay.suppress_aligned_hidden_segments(
                             (visible, offset_hidden, partial_hidden)))

    def test_render_camera_rays_support_perspective_and_orthographic_views(self):
        data = bpy.data.cameras.new('Semantic Test Camera')
        camera = bpy.data.objects.new('Semantic Test Camera', data)
        bpy.context.scene.collection.objects.link(camera)
        camera.location = (0.0, 0.0, 0.0)

        origin, direction, distance = semantic_line_render._camera_ray(
            camera, (0.0, 0.0, -5.0))
        self.assertEqual((0.0, 0.0, 0.0), tuple(origin))
        self.assertAlmostEqual(5.0, distance)
        self.assertAlmostEqual(-1.0, direction.z)

    def test_orthographic_viewport_ray_is_parallel_and_target_aligned(self):
        region_3d = SimpleNamespace(view_matrix=Matrix.Identity(4))
        origin, direction, distance = semantic_edge_overlay._orthographic_view_ray(
            region_3d, (2.0, 3.0, -5.0), 100.0)
        self.assertEqual((2.0, 3.0, 95.0), tuple(origin))
        self.assertEqual((0.0, 0.0, -1.0), tuple(direction))
        self.assertEqual(100.0, distance)

    def test_shared_line_weight_uses_calibrated_viewport_and_render_multipliers(self):
        scene = SimpleNamespace(
            hb_semantic_edge_line_weight=2.0,
            hb_semantic_edge_viewport_weight_multiplier=1.0,
            hb_semantic_edge_render_weight_multiplier=1.25)
        self.assertEqual(2.0, semantic_edge_overlay.viewport_line_width(scene))
        self.assertEqual(2.5, semantic_edge_overlay.render_line_width(scene))
        self.assertAlmostEqual(1.8, semantic_edge_overlay.hidden_line_width(2.5))

    def test_render_line_pass_creates_packed_image_and_compositor_layer(self):
        scene = bpy.context.scene
        old_camera = scene.camera
        old_resolution = (scene.render.resolution_x, scene.render.resolution_y)
        old_engine = scene.render.engine
        data = bpy.data.cameras.new('Semantic Render Camera')
        camera = bpy.data.objects.new('Semantic Render Camera', data)
        bpy.context.scene.collection.objects.link(camera)
        scene.camera = camera
        scene.render.resolution_x, scene.render.resolution_y = 96, 64
        make_mesh('Render Cube',
                  [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                   (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)],
                  [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                   (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]).location = (0, 0, -5)
        semantic_edge_overlay.register()
        semantic_line_render.register()
        try:
            scene.hb_semantic_render_mode = 'TECHNICAL'
            image = semantic_line_render.render_semantic_line_image(scene)
            semantic_line_render.composite_semantic_line_image(scene, image)
            self.assertEqual((96, 64), tuple(image.size))
            self.assertIsNotNone(image.packed_file)
            self.assertIn(semantic_line_render.COMPOSITE_NODE_NAME,
                          scene.compositing_node_group.nodes)
            scene.render.engine = 'BLENDER_WORKBENCH'
            scene.hb_semantic_render_enabled = True
            bpy.ops.render.render()
            self.assertIsNotNone(bpy.data.images.get('Render Result'))
        finally:
            semantic_line_render.unregister()
            semantic_edge_overlay.unregister()
            scene.camera = old_camera
            scene.render.resolution_x, scene.render.resolution_y = old_resolution
            scene.render.engine = old_engine

        data.type = 'ORTHO'
        origin, direction, distance = semantic_line_render._camera_ray(
            camera, (2.0, 3.0, -5.0))
        self.assertEqual((2.0, 3.0, 0.0), tuple(origin))
        self.assertAlmostEqual(5.0, distance)
        self.assertAlmostEqual(-1.0, direction.z)


if __name__ == '__main__':
    # Blender retains its own command-line arguments in sys.argv.  Supplying
    # an explicit argv keeps unittest from trying to parse --background etc.
    unittest.main(argv=[sys.argv[0]])
