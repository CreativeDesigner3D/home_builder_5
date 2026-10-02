"""Batch thumbnail rendering for the closet library.

Maintenance operator, not part of the end-user flow. For each catalog
product it builds the real thing in a throwaway scene, renders a
preview into closet_thumbnails/, then tears the scene down. The
resulting PNGs are committed to the repo so users get them shipped.

The renderer itself is the one the face frame library already uses -
same camera, same framing, same 540px output - so the two grids cannot
drift into looking like different products.

Three kinds of product need three ways of building:

- A STARTER resolves through the name dispatch and builds itself.
- A LOOSE part is cut at a size and stands on its own, so it is built
  bare, the way it arrives on the cursor.
- A FITTED part only exists inside an opening, so it is built into one
  and the whole run is what gets framed. On its own a fixed shelf is a
  rectangle indistinguishable from the loose shelf beside it in the
  grid; in an opening it reads as what it is.

Existing renders are left alone unless `overwrite` is set: geometry
changes are what this is for, and a run to fill in a new product
should not quietly restyle the ones already shipped.
"""
import os

import bpy

from .... import hb_types
from .. import types_closets
from .. import props_closets
from .. import const_closets as const
from ..library_catalog import products
from ...face_frame import thumbnail_render


# Loose parts, by the catalog name they carry -> the kind they are cut
# as.
_LOOSE_KINDS = {
    'Misc Part': 'MISC',
    'Back': 'BACK',
    'Cleat': 'CLEAT',
    'Shelf': 'SHELF',
}

# Parts that live in an opening, as (the starter to show it in, how
# many bays that starter gets). A rod and a shelf hang in a single-bay
# wall box, where the part is most of the picture rather than a line
# across one opening of four.
_FITTED_IN = {
    'Fixed Shelf': ('Hanging', 1),
    'Closet Rod': ('Hanging', 1),
}


def _first_opening(root):
    """The first opening under a starter, or None. Openings hang off
    bays, which hang off the starter root."""
    for bay in root.children:
        if not bay.get(types_closets.TAG_BAY_CAGE):
            continue
        for opening in bay.children:
            if opening.get(types_closets.TAG_OPENING_CAGE):
                return opening
    return None


def _build_starter(name, bay_qty=const.DEFAULT_BAY_QTY):
    cls = types_closets.get_starter_class(name)
    if cls is None:
        return None
    starter = cls()
    starter.create_starter(name, bay_qty)
    return starter.obj


def _build_fitted(name):
    """A starter with the part standing in it, and the starter is what
    the camera frames."""
    starter_name, bay_qty = _FITTED_IN[name]
    root = _build_starter(starter_name, bay_qty)
    if root is None:
        return None
    opening = _first_opening(root)
    if opening is None:
        return None
    if name == 'Closet Rod':
        types_closets.add_rod(opening, const.ROD_TOP_OFFSET)
    else:
        # Halfway up, on a hole. At zero it lands on the opening floor,
        # where the bottom panel hides it and the thumbnail is a picture
        # of an empty box. The hole lattice is datumed off the bay
        # interior bottom, so the segment offset goes on before the snap
        # and comes off after.
        interior_h = hb_types.GeoNodeCage(opening).get_input('Dim Z')
        seg_bottom = opening.get('hb_seg_bottom', 0.0)
        z = (const.snap_system_hole(seg_bottom + interior_h / 2.0)
             - seg_bottom)
        types_closets.add_fixed_shelf(opening, max(z, 0.0))
    types_closets.recalculate_closet_starter(root)
    return root


def _build_bay_countertop():
    """A tall run with its middle bays at base height and a countertop
    across them - the counter between taller sections the part is
    for."""
    root = _build_starter('Tall', const.DEFAULT_BAY_QTY)
    if root is None:
        return None
    bays = types_closets.ClosetStarter(root)._sorted_bays()
    middle = bays[1:-1] or bays
    for bay in middle:
        bay.hb_closet_bay.unlock_height = True
        bay.hb_closet_bay.height = const.BASE_PANEL_HEIGHT
    types_closets.recalculate_closet_starter(root)
    types_closets.add_bay_countertop(root, middle[0])
    return root


def _build_in_scene(name):
    """Build the catalog product `name` into the active scene and
    return the object the camera should frame, or None when nothing
    here knows how to build it."""
    if name == 'Countertop':
        return _build_bay_countertop()
    if name == 'Slab Countertop':
        return types_closets.add_slab_countertop()
    if name in _LOOSE_KINDS:
        return types_closets.add_misc_part(kind=_LOOSE_KINDS[name])
    if name in _FITTED_IN:
        return _build_fitted(name)
    return _build_starter(name)


class hb_closets_OT_render_library_thumbnails(bpy.types.Operator):
    """Render thumbnails for the built-in closet library"""
    bl_idname = "hb_closets.render_library_thumbnails"
    bl_label = "Render Library Thumbnails"
    bl_description = (
        "Build each closet product in a throwaway scene and render its "
        "thumbnail into closet_thumbnails/. Maintenance tool"
    )

    overwrite: bpy.props.BoolProperty(
        name="Re-render Existing",
        description=("Render every product. Off, only the ones with no "
                     "thumbnail yet are rendered"),
        default=False,
    )  # type: ignore

    def execute(self, context):
        out_dir = props_closets.get_thumbnail_path()
        os.makedirs(out_dir, exist_ok=True)

        window = context.window
        original_scene = window.scene
        rendered = []
        failed = []
        skipped = []

        for product in products():
            name = product['key']
            out_path = os.path.join(out_dir, "%s.png" % name)
            if not self.overwrite and os.path.isfile(out_path):
                skipped.append(name)
                continue
            scene = bpy.data.scenes.new("__hb5_closet_thumb__")
            window.scene = scene
            # Snapshot before the build so teardown removes exactly what
            # this iteration added and nothing from the user's real data.
            before = set(bpy.data.objects.keys())
            try:
                target = _build_in_scene(name)
                if target is None:
                    failed.append(name)
                    continue
                context.view_layer.update()
                result = thumbnail_render.render_thumbnail(
                    scene, target, out_path)
                (rendered if result else failed).append(name)
            except Exception as exc:
                print("[thumbnails] %s failed: %s" % (name, exc))
                failed.append(name)
            finally:
                for obj_name in set(bpy.data.objects.keys()) - before:
                    obj = bpy.data.objects.get(obj_name)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
                window.scene = original_scene
                bpy.data.scenes.remove(scene, do_unlink=True)

        # Drop both caches that hold a decoded copy of these files - the
        # sidebar's preview collection and the viewport browser's
        # textures - so the new PNGs show on the next draw rather than
        # after a reload.
        pcoll = props_closets.preview_collections.get("starter_previews")
        if pcoll is not None:
            pcoll.clear()
        try:
            from ....operators import library_panel
            library_panel._textures.clear()
        except Exception:
            pass
        for area in context.screen.areas:
            area.tag_redraw()

        message = "Rendered %d thumbnails" % len(rendered)
        if skipped:
            message += ", %d already had one" % len(skipped)
        if failed:
            message += " - failed: %s" % ', '.join(failed)
        self.report({'INFO'}, message)
        return {'FINISHED'}


classes = (
    hb_closets_OT_render_library_thumbnails,
)

register, unregister = bpy.utils.register_classes_factory(classes)
