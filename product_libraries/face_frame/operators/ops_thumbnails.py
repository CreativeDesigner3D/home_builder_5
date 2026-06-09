"""Batch thumbnail rendering for built-in face frame catalog items.

Maintenance operator, not part of the end-user flow. For each renderable
catalog entry it builds the real cabinet in a throwaway scene, renders a
workbench preview into face_frame_thumbnails/, then tears the scene down.
The resulting PNGs are committed to the repo so users get them shipped.

Only catalog names with a genuine builder are listed: get_cabinet_class
falls back to a plain base cabinet for any unrecognized name, so an
explicit allowlist is the safeguard against rendering misleading images.
"""
import os
import bpy
from .. import types_face_frame
from .. import props_hb_face_frame
from .. import thumbnail_render
from .. import bay_presets
from . import ops_cabinet


# Catalog names whose builder produces a faithful cabinet at default dims.
# Extend as corner / appliance / specialty builders are migrated in. Note
# "Upper Stacked" currently dispatches to the plain upper class, so until
# stacked geometry exists its thumbnail will match "Upper".
RENDERABLE_CATALOG = (
    # Standard cabinets.
    "Base",
    "Tall",
    "Upper",
    "Upper Stacked",
    "Hutch Upper",
    "Lap Drawer",
    "Floating Base Cabinet",
    # Corner cabinets - create() builds them populated with doors, so no
    # bay preset applies. "Pie Cut Drawer" is omitted: it has no dispatch
    # entry and would fall back to a plain base cabinet.
    "Pie Cut Base",
    "Pie Cut Upper",
    "Diagonal Base",
    "Diagonal Upper",
    "Diagonal Tall",
    # Appliance-housing cabinets - face frame cabinet classes, not the
    # appliance products. Built and populated via the bay preset path.
    "Built in Tall",
    "Refrigerator Cabinet",
    "Sink",
    # Vanity products - standard base cabinets with a vanity bay preset.
    "Special",
    "Combination",
    "Deluxe",
    # Specialty bedroom & bookcase products.
    "Bookcase",
    "Bookcase Storage Unit",
    "Bookcase Upper",
    # Window seat - flush-kick 18" base; bays default to an inset panel
    # via the bay-preset path, same as the other base products.
    "Window Seat",
    "Standard Recessed Medicine Cabinet",
    "Medicine Cabinet",
    "Tri-View Medicine Cabinet",
    "Overstool Cabinet",
    "Mirror Frame",
    "Tub Skirt",
    # Freestanding furniture - flush kick + veneer wood top, built and
    # populated via the bay preset path like the other base products.
    "5 Drawer Dresser",
    "6 Drawer Dresser",
    "Night Stand",
    "3 Drawer Night Stand",
    # Bare parts (no cage): a lone cutpart, and a door front + pull.
    "Misc Part",
    "Door",
    # Misc products. Half Wall / Support Frame reuse the frameless
    # geometry (no bay preset applies; default_bay_config returns None).
    "Half Wall",
    "Support Frame",
    # FF & Doors: carcass-less panel whose opening defaults to a door
    # (no bay preset; default_bay_config returns None).
    "Face Frame and Doors",
)


def _build_in_scene(name):
    """Build the catalog item `name` into the active context scene and
    populate its bays so the thumbnail shows doors and drawers. Returns
    the cabinet root, or None if the name has no real builder.
    """
    cls = types_face_frame.get_cabinet_class(name)
    if cls is None:
        return None
    cabinet = cls()
    cabinet.create(name, bay_qty=1)
    root = cabinet.obj

    # cabinet.create() leaves every opening at front_type NONE. The
    # placement operator's _finalize is what fills bays, via a name-driven
    # preset; replicate that step so a catalog thumbnail matches a freshly
    # placed cabinet instead of showing an empty carcass.
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if bays:
        config = bay_presets.default_bay_config(name, bays[0].face_frame_bay.width)
        if config is not None:
            with types_face_frame.suspend_recalc():
                for bay_obj in bays:
                    ops_cabinet.apply_bay_preset(bay_obj, config)
    return root


class hb_face_frame_OT_render_library_thumbnails(bpy.types.Operator):
    """Render workbench thumbnails for the built-in face frame catalog"""
    bl_idname = "hb_face_frame.render_library_thumbnails"
    bl_label = "Render Library Thumbnails"
    bl_description = (
        "Build each catalog cabinet in a throwaway scene and render its "
        "thumbnail into face_frame_thumbnails/. Maintenance tool"
    )

    def execute(self, context):
        out_dir = props_hb_face_frame.get_cabinet_thumbnail_path()
        os.makedirs(out_dir, exist_ok=True)

        window = context.window
        original_scene = window.scene
        rendered = []
        failed = []

        for name in RENDERABLE_CATALOG:
            scene = bpy.data.scenes.new(f"__hb5_thumb_{name}__")
            window.scene = scene
            # Snapshot before the build so teardown removes exactly what
            # this iteration added and nothing from the user's real data.
            before = set(bpy.data.objects.keys())
            try:
                root = _build_in_scene(name)
                if root is None:
                    failed.append(name)
                    continue
                context.view_layer.update()
                out_path = os.path.join(out_dir, f"{name}.png")
                result = thumbnail_render.render_thumbnail(scene, root, out_path)
                (rendered if result else failed).append(name)
            except Exception as exc:
                print(f"[thumbnails] {name} failed: {exc}")
                failed.append(name)
            finally:
                for obj_name in set(bpy.data.objects.keys()) - before:
                    obj = bpy.data.objects.get(obj_name)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
                window.scene = original_scene
                bpy.data.scenes.remove(scene, do_unlink=True)

        # Drop the cached cabinet previews so the new PNGs load on the next
        # sidebar draw without an addon reload.
        pcoll = props_hb_face_frame.preview_collections.get("cabinet_previews")
        if pcoll is not None:
            pcoll.clear()
        for area in context.screen.areas:
            area.tag_redraw()

        message = f"Rendered {len(rendered)}/{len(RENDERABLE_CATALOG)} thumbnails"
        if failed:
            message += f" - failed: {', '.join(failed)}"
        self.report({'INFO'}, message)
        return {'FINISHED'}


classes = (
    hb_face_frame_OT_render_library_thumbnails,
)

register, unregister = bpy.utils.register_classes_factory(classes)
