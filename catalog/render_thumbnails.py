"""Catalog thumbnail renderer.

Drives an entry's action_operator inside a temporary scene to place a
cabinet at the origin, frames a camera on its world-space bounding
box, and renders to catalog/thumbnails/{item.id}.png with the
Workbench engine.

Workbench is chosen over Eevee/Cycles because it is fast (sub-second
per render), deterministic, and does not require a light setup. The
shading uses a Studio MatCap with cavity enabled, which gives clean
shape definition without the user having to configure materials.

The camera is positioned at a fixed front-right-above angle relative
to the cabinet bbox center, with distance scaled to the largest bbox
dimension so cabinets of different sizes (Base ~36" wide vs Tall ~84"
tall) all frame consistently.
"""

import os
import math
import bpy
from mathutils import Vector

from . import catalog_data
from . import previews_catalog


THUMB_RESOLUTION = 256

# 3/4 view angles: front-right azimuth, slight downward look from above.
# These match the conventions most furniture catalogs use.
_AZIMUTH_DEG = -45.0   # negative = swing from -Y (front) toward +X (right)
_ELEVATION_DEG = 25.0  # above horizontal


def _thumbs_dir():
    return os.path.join(os.path.dirname(__file__), 'thumbnails')


def _is_renderable(entry):
    """True if the entry has a real action_operator (not the stub)."""
    return entry.get('action_operator', '') != 'hb_catalog.not_yet_implemented'


def render_entry(entry):
    """Render a thumbnail for one catalog entry. Returns saved path or None.

    Caller is responsible for handling exceptions - this function lets
    them propagate so the bulk renderer can decide whether to abort or
    skip-and-continue.
    """
    if not _is_renderable(entry):
        return None

    context = bpy.context
    original_scene = context.window.scene

    # Build a fresh scene so we don't pollute the user's working scene
    # with throwaway objects, lights, or cameras.
    thumb_scene = bpy.data.scenes.new('_hb_thumbnail_render')

    try:
        context.window.scene = thumb_scene
        thumb_scene.cursor.location = (0.0, 0.0, 0.0)

        # Place the cabinet via the entry's real operator. Using
        # EXEC_DEFAULT skips any modal phase and runs execute() directly.
        op_full = entry['action_operator']
        mod_name, op_name = op_full.split('.', 1)
        op_func = getattr(getattr(bpy.ops, mod_name), op_name)
        result = op_func('EXEC_DEFAULT', **entry.get('action_args', {}))

        if 'CANCELLED' in result or 'FINISHED' not in result:
            return None

        # The placed cabinet is left as the active object by draw_cabinet.
        cabinet = context.view_layer.objects.active
        if cabinet is None:
            return None

        # World-space bbox over cabinet + all descendants. Cabinets are
        # hierarchies of cages and parts, so we need to walk the tree.
        bb_min = Vector((float('inf'),) * 3)
        bb_max = Vector((float('-inf'),) * 3)
        any_mesh = False
        for obj in [cabinet] + list(cabinet.children_recursive):
            if obj.type != 'MESH':
                continue
            # Skip hidden objects (cages are hidden in the active mode)
            if not obj.visible_get(view_layer=context.view_layer):
                continue
            any_mesh = True
            for corner in obj.bound_box:
                world = obj.matrix_world @ Vector(corner)
                for i in range(3):
                    if world[i] < bb_min[i]:
                        bb_min[i] = world[i]
                    if world[i] > bb_max[i]:
                        bb_max[i] = world[i]

        if not any_mesh or bb_min[0] == float('inf'):
            return None

        center = (bb_min + bb_max) * 0.5
        size = max(bb_max[0] - bb_min[0],
                   bb_max[1] - bb_min[1],
                   bb_max[2] - bb_min[2])
        if size <= 0:
            return None

        # Camera at front-right-above. Math: spherical coordinates with
        # the cabinet center as the origin, distance proportional to size.
        az = math.radians(_AZIMUTH_DEG)
        el = math.radians(_ELEVATION_DEG)
        distance = size * 2.0  # 2x size leaves comfortable margin

        cam_offset = Vector((
            distance * math.cos(el) * math.sin(az),     # +X = right
            distance * math.cos(el) * (-math.cos(az)),  # -Y = toward front
            distance * math.sin(el),                    # +Z = above
        ))
        # az=-45 + sin(-45)=-0.71, cos(-45)=0.71 - so cam is to the right
        # and toward -Y (front). That puts the cabinet's face frame visible
        # since face frames sit on the -Y side.

        cam_data = bpy.data.cameras.new('_hb_thumb_cam')
        cam_data.lens = 50.0
        cam = bpy.data.objects.new('_hb_thumb_cam', cam_data)
        thumb_scene.collection.objects.link(cam)
        cam.location = center + cam_offset

        # Look at the bbox center. to_track_quat aligns -Z (camera forward)
        # with the direction vector and uses +Y as up.
        direction = center - cam.location
        cam.rotation_mode = 'QUATERNION'
        cam.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

        thumb_scene.camera = cam

        # Workbench render config
        thumb_scene.render.engine = 'BLENDER_WORKBENCH'
        thumb_scene.render.resolution_x = THUMB_RESOLUTION
        thumb_scene.render.resolution_y = THUMB_RESOLUTION
        thumb_scene.render.resolution_percentage = 100
        thumb_scene.render.film_transparent = True
        thumb_scene.render.image_settings.file_format = 'PNG'
        thumb_scene.render.image_settings.color_mode = 'RGBA'

        shading = thumb_scene.display.shading
        shading.light = 'MATCAP'
        shading.studio_light = 'basic_grey.exr'  # neutral grey - shows shape without distracting material cues
        shading.show_cavity = True
        shading.cavity_type = 'BOTH'
        shading.show_object_outline = False

        # Output path
        out_dir = _thumbs_dir()
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{entry['id']}.png")
        thumb_scene.render.filepath = out_path

        bpy.ops.render.render(write_still=True)
        return out_path
    finally:
        # Restore user scene, drop the temp scene + its data-blocks. New
        # scenes own their cursor/view layer, but cameras/objects we
        # added live in bpy.data and need explicit removal.
        context.window.scene = original_scene
        # Removing the scene removes references; orphan objects/datablocks
        # get cleaned up by Blender unless still linked elsewhere.
        if thumb_scene.name in bpy.data.scenes:
            bpy.data.scenes.remove(thumb_scene, do_unlink=True)
        # Reload preview collection so freshly-rendered thumbnails appear.
        previews_catalog.reload()


def render_all():
    """Render thumbnails for every renderable (non-stub) catalog entry.

    Returns (rendered_count, skipped_count, errors). Errors are tuples
    of (item_id, exception) so the caller can show a summary.
    """
    rendered = 0
    skipped = 0
    errors = []
    for entry in catalog_data.CATALOG:
        if not _is_renderable(entry):
            skipped += 1
            continue
        try:
            path = render_entry(entry)
            if path:
                rendered += 1
            else:
                skipped += 1
        except Exception as e:  # pragma: no cover
            errors.append((entry['id'], e))
    return rendered, skipped, errors
