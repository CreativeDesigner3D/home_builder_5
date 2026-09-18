"""Batch thumbnail rendering for the frameless library.

Maintenance operator, not part of the end-user flow. For each catalog
product it builds the real thing in a throwaway scene -- through the
same dispatch the placement tool uses, styled the way a freshly placed
one is -- renders a preview into frameless_thumbnails/, then tears the
scene down. The resulting PNGs are committed to the repo so users get
them shipped.

The renderer is the one the face frame and closet libraries use: same
camera, same framing, same 540px output, so the three grids read as one
set.

Existing renders are left alone unless `overwrite` is set: a run to
fill in a new product should not quietly restyle the ones already
shipped, and a run to restyle the set says so.
"""
import os

import bpy

from .... import hb_project, hb_utils, units
from .. import props_hb_frameless
from ..library_catalog import products
from ...face_frame import thumbnail_render
from . import ops_placement


# Catalog names that are appliances rather than cabinets, and the type
# the appliance dispatch wants for them (mirrors draw_cabinet).
APPLIANCE_NAMES = {
    'Range': 'RANGE',
    'Dishwasher': 'DISHWASHER',
    'Refrigerator': 'REFRIGERATOR',
    'Range Hood': 'HOOD',
}


def cabinet_type_for(name):
    """BASE / TALL / UPPER for a catalog name, by the same words the
    library's Draw Cabinet operator reads."""
    if 'Base' in name:
        return 'BASE'
    if 'Tall' in name or name in ('Refrigerator Cabinet', 'Tall Leg'):
        return 'TALL'
    if 'Upper' in name:
        return 'UPPER'
    return 'BASE'


def _style_like_placed(context, root):
    """The finishing the placement tool gives a cabinet once it stands:
    the active cabinet style, a re-solve, the active door style on every
    front, and shelf counts from the opening heights."""
    bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=root.name)
    hb_utils.run_calc_fix(context, root)
    hb_utils.run_calc_fix(context, root)
    props = hb_project.get_main_scene().hb_frameless
    if len(props.door_styles) == 0:
        style = props.door_styles.add()
        style.name = "Slab"
        props.active_door_style_index = 0
    index = props.active_door_style_index
    if index >= len(props.door_styles):
        index = 0
    style = props.door_styles[index]
    for obj in root.children_recursive:
        if obj.get('IS_DOOR_FRONT') or obj.get('IS_DRAWER_FRONT'):
            obj['DOOR_STYLE_INDEX'] = index
            style.assign_style_to_front(obj)
    try:
        bpy.ops.hb_frameless.calculate_shelf_quantity(cabinet_name=root.name)
    except Exception:
        pass
    _paint_neutral(root)


def _paint_neutral(root):
    """The library's plain White on every part. A room's active style
    is whatever the designer picked, and a browser tile should not
    change colour with it -- the face frame and closet tiles are
    neutral, and this set sits beside them."""
    from ...closets import materials_closets
    from .... import hb_types
    white = materials_closets.load_material(materials_closets.DEFAULT_MATERIAL)
    if white is None:
        return
    for child in root.children_recursive:
        if 'CABINET_PART' not in child:
            continue
        part = hb_types.GeoNodeObject(child)
        for socket in ('Top Surface', 'Bottom Surface',
                       'Edge W1', 'Edge W2', 'Edge L1', 'Edge L2'):
            try:
                part.set_input(socket, white)
            except Exception:
                pass
        for mod in child.modifiers:
            if mod.type != 'NODES' or not mod.node_group:
                continue
            tree_items = mod.node_group.interface.items_tree
            for socket in ('Material', 'Stile Material', 'Rail Material',
                           'Panel Material'):
                if socket in tree_items:
                    hb_utils.set_gn_input(mod, tree_items[socket].identifier,
                                          white)


def _hide_scaffolding(root):
    """Cages, prompt empties and the 2D annotations (an appliance's
    label) are construction, not product: keep them out of the render
    and out of the framing."""
    for obj in [root] + list(root.children_recursive):
        if (obj.get('IS_GEONODE_CAGE') or obj.get('IS_2D_ANNOTATION')
                or obj.type == 'EMPTY'):
            obj.hide_render = True


def _build_in_scene(context, name):
    """Build the catalog product `name` into the active scene and return
    the object the camera should frame, or None when nothing here knows
    how to build it."""
    is_appliance = name in APPLIANCE_NAMES
    cabinet = ops_placement.build_cabinet_for(
        name, cabinet_type_for(name), is_appliance,
        APPLIANCE_NAMES.get(name, ''))
    if cabinet is None:
        return None
    if is_appliance or name in ops_placement.PART_CLASS_MAP:
        if APPLIANCE_NAMES.get(name) == 'HOOD':
            # Placement runs a hood up to the ceiling; on its own it is
            # a 24" hood, which is what the picture should show.
            cabinet.height = units.inch(24.0)
        cabinet.create(name)
    else:
        cabinet.create('Cabinet')
    root = cabinet.obj
    if is_appliance:
        # The cage alone renders nothing: the model is seeded on
        # placement, so seed it here too.
        from ...common import appliance_geo
        appliance_geo.seed_on_place(root)
    else:
        _style_like_placed(context, root)
    _hide_scaffolding(root)
    return root


class hb_frameless_OT_render_library_thumbnails(bpy.types.Operator):
    """Render thumbnails for the built-in frameless library"""
    bl_idname = "hb_frameless.render_library_thumbnails"
    bl_label = "Render Library Thumbnails"
    bl_description = (
        "Build each frameless product in a throwaway scene and render its "
        "thumbnail into frameless_thumbnails/. Maintenance tool"
    )

    overwrite: bpy.props.BoolProperty(
        name="Re-render Existing",
        description=("Render every product. Off, only the ones with no "
                     "thumbnail yet are rendered"),
        default=False,
    )  # type: ignore

    def execute(self, context):
        out_dir = props_hb_frameless.get_cabinet_thumbnail_path()
        os.makedirs(out_dir, exist_ok=True)

        window = context.window
        original_scene = window.scene
        rendered = []
        failed = []
        skipped = []
        done = set()

        for product in products():
            name = product['key']
            picture = product['thumbnail']
            if picture in done:
                continue            # three legs share one picture
            done.add(picture)
            out_path = os.path.join(out_dir, "%s.png" % picture)
            if not self.overwrite and os.path.isfile(out_path):
                skipped.append(name)
                continue
            scene = bpy.data.scenes.new("__hb5_frameless_thumb__")
            window.scene = scene
            # Snapshot before the build so teardown removes exactly what
            # this iteration added and nothing from the user's real data.
            before = set(bpy.data.objects.keys())
            try:
                target = _build_in_scene(context, name)
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
        pcoll = props_hb_frameless.preview_collections.get("cabinet_previews")
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
    hb_frameless_OT_render_library_thumbnails,
)

register, unregister = bpy.utils.register_classes_factory(classes)
