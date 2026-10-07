"""Offscreen thumbnail rendering for face frame library items.

Frames an object and its descendants with an orthographic 3/4 camera and
renders it through EEVEE with a flat uniform world and a black Freestyle
outline. The depsgraph-evaluated bounding box is used for framing so
geometry-node-generated parts are captured at their rendered size, not
their (often empty) base-mesh extent.

The caller owns scene lifecycle. The batch catalog renderer passes a
throwaway scene; an on-demand save would pass the active scene with its
render settings snapshotted, since this function leaves them changed.
"""
import bpy
from mathutils import Matrix, Vector

THUMBNAIL_SIZE = 540
# Padding around the product's projected on-screen extent; 1.0 is exact fit.
FRAME_MARGIN = 1.1


def _world_bounds(objs, depsgraph):
    """Combined world-space AABB of objs, evaluated through depsgraph so
    geometry node output is included. Non-rendering objects (hide_render)
    are skipped, so construction cages and parked placeholder parts don't
    inflate the box past the visible product. Returns (min, max) Vectors,
    or None if nothing renders.
    """
    mins = [float('inf')] * 3
    maxs = [float('-inf')] * 3
    found = False
    for obj in objs:
        if obj.type not in {'MESH', 'CURVE'}:
            continue
        if obj.hide_render:
            continue
        eobj = obj.evaluated_get(depsgraph)
        matrix = eobj.matrix_world
        for corner in eobj.bound_box:
            world_corner = matrix @ Vector(corner)
            for axis in range(3):
                mins[axis] = min(mins[axis], world_corner[axis])
                maxs[axis] = max(maxs[axis], world_corner[axis])
            found = True
    if not found:
        return None
    return Vector(mins), Vector(maxs)


def _configure_freestyle(view_layer):
    """Point the view layer's Freestyle lineset at a black silhouette /
    border / crease outline. A view layer with Freestyle enabled ships
    with one default lineset and linestyle; reuse it, creating one only
    if it is somehow missing.
    """
    fs = view_layer.freestyle_settings
    lineset = fs.linesets[0] if fs.linesets else fs.linesets.new("LineSet")
    lineset.select_silhouette = True
    lineset.select_border = True
    lineset.select_crease = True
    lineset.select_edge_mark = False
    lineset.select_contour = False
    lineset.select_external_contour = False
    lineset.select_material_boundary = False
    lineset.select_ridge_valley = False
    style = lineset.linestyle
    if style is not None:
        style.color = (0.0, 0.0, 0.0)
        style.alpha = 1.0
        style.thickness = 3.0


def render_thumbnail(scene, target_obj, out_path, size=THUMBNAIL_SIZE):
    """Render a 3/4 orthographic EEVEE thumbnail of target_obj plus its
    descendants to out_path.

    Operates on `scene`, which must be the active context scene so the
    evaluated depsgraph resolves against it. Render settings on the scene
    are modified and not restored - pass a throwaway scene, or snapshot.
    Returns out_path on success, None on failure.
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objs = [target_obj] + list(target_obj.children_recursive)
    bounds = _world_bounds(objs, depsgraph)
    if bounds is None:
        print(f"[thumbnail] nothing to frame for {target_obj.name}")
        return None

    bb_min, bb_max = bounds
    center = (bb_min + bb_max) / 2.0
    max_dim = max(bb_max - bb_min) or 1.0

    cam_data = bpy.data.cameras.new("HB_ThumbnailCam")
    cam_data.type = 'ORTHO'
    cam_obj = bpy.data.objects.new("HB_ThumbnailCam", cam_data)
    scene.collection.objects.link(cam_obj)

    # Front-right-above 3/4 view. Matches the user-library save thumbnail
    # angle so saved groups and built-in catalog items read consistently.
    # Camera distance is irrelevant to an ortho projection - ortho_scale,
    # fitted below, is what controls the framing.
    cam_location = center + Vector((max_dim, -max_dim, max_dim * 0.8))
    aim = center - cam_location
    cam_rotation = aim.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.location = cam_location
    cam_obj.rotation_euler = cam_rotation
    scene.camera = cam_obj

    # Fit ortho_scale to the geometry's real projected size. From a 3/4
    # view the on-screen extent is the projection of the bounding box, not
    # any single 3D axis - so project the eight box corners into camera
    # space and take the larger of the X / Y spans. This makes every
    # product fill the frame the same regardless of its proportions.
    cam_matrix = Matrix.Translation(cam_location) @ cam_rotation.to_matrix().to_4x4()
    cam_inv = cam_matrix.inverted()
    box_corners = [Vector((x, y, z))
                   for x in (bb_min.x, bb_max.x)
                   for y in (bb_min.y, bb_max.y)
                   for z in (bb_min.z, bb_max.z)]
    projected = [cam_inv @ corner for corner in box_corners]
    span_x = max(p.x for p in projected) - min(p.x for p in projected)
    span_y = max(p.y for p in projected) - min(p.y for p in projected)
    cam_data.ortho_scale = max(span_x, span_y) * FRAME_MARGIN

    render = scene.render
    render.engine = 'BLENDER_EEVEE'
    render.resolution_x = size
    render.resolution_y = size
    render.resolution_percentage = 100
    render.film_transparent = True
    render.filepath = out_path

    # Freestyle line art. Both the render-level and view-layer switches
    # must be on; the linestyle itself lives on the view layer's lineset.
    render.use_freestyle = True
    render.line_thickness_mode = 'ABSOLUTE'
    view_layer = scene.view_layers[0]
    view_layer.use_freestyle = True
    _configure_freestyle(view_layer)

    # Flat fill: a bright uniform world lights the cabinet evenly with
    # shadows off, so EEVEE shading stays even and the Freestyle outline
    # carries the read. film_transparent keeps the background clear while
    # the world still contributes the fill light.
    scene.eevee.use_shadows = False
    created_world = None
    if scene.world is None:
        created_world = bpy.data.worlds.new("HB_ThumbnailWorld")
        scene.world = created_world
    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get('Background')
    if background is not None:
        background.inputs['Color'].default_value = (0.9, 0.9, 0.9, 1.0)
        background.inputs['Strength'].default_value = 1.0

    try:
        bpy.ops.render.render(write_still=True)
        succeeded = True
    except Exception as exc:
        print(f"[thumbnail] render failed for {target_obj.name}: {exc}")
        succeeded = False
    finally:
        bpy.data.objects.remove(cam_obj)
        bpy.data.cameras.remove(cam_data)
        if created_world is not None:
            bpy.data.worlds.remove(created_world)

    return out_path if succeeded else None
