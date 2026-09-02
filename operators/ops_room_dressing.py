"""
Dressing a room for a rendering: a floor with a real material, and the
commands that clear the room shell back out of the way.

Three commands:

  home_builder.floor                 add a floor and give it a material
  home_builder.toggle_room_scenery   hide / show floor, ceiling and lights
  home_builder.delete_room_scenery   remove floor, ceiling and lights

Add Floor (walls.py) builds the slab with world-scale UVs (1 UV unit =
1 m) but leaves it unshaded, so it renders white. Floor makes the slab
if the room has none and dresses it with a fully procedural material --
wood planks, tile, or a solid color -- built from shader nodes in code,
so no texture files or .blend assets ship with the add-on. Re-running
restyles the existing floor in place.

The room-lights option form for the tool palette lives here too: Add
Room Lights lays a new set on top of any already there, so the strip
needs a way to clear them without going back to the sidebar.
"""

import bpy
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty)

from .. import surface_materials as sm
from . import room_palette

MATERIAL_NAME = "Floor"

STYLE_ITEMS = [
    ('WOOD', "Wood Planks", "Staggered hardwood planks with grain", 'MOD_WAVE', 0),
    ('TILE', "Tile", "Grid or running-bond tile with grout", 'MESH_GRID', 1),
    ('SOLID', "Solid Color", "Flat colored floor (concrete, carpet, paint)", 'MATERIAL', 2),
]

# Named looks: (label, base color, accent color) in sRGB 0-1. Accent is
# the darker plank tone for wood, the grout for tile. Custom keeps
# whatever colors are in the dialog.
WOOD_LOOKS = {
    'LIGHT_OAK':  ("Light Oak",   (0.80, 0.68, 0.50), (0.66, 0.53, 0.37)),
    'NATURAL':    ("Natural Oak", (0.64, 0.45, 0.27), (0.48, 0.32, 0.18)),
    'HONEY':      ("Honey Maple", (0.78, 0.56, 0.32), (0.64, 0.42, 0.22)),
    'WALNUT':     ("Walnut",      (0.34, 0.22, 0.13), (0.22, 0.13, 0.08)),
    'GRAY_WASH':  ("Gray Wash",   (0.58, 0.55, 0.51), (0.44, 0.41, 0.38)),
    'CUSTOM':     ("Custom", None, None),
}
TILE_LOOKS = {
    'WHITE':      ("White",       (0.92, 0.92, 0.90), (0.74, 0.74, 0.72)),
    'LIGHT_GRAY': ("Light Gray",  (0.70, 0.70, 0.68), (0.52, 0.52, 0.50)),
    'CHARCOAL':   ("Charcoal",    (0.24, 0.24, 0.25), (0.17, 0.17, 0.18)),
    'TRAVERTINE': ("Travertine",  (0.82, 0.74, 0.60), (0.64, 0.57, 0.46)),
    'TERRACOTTA': ("Terracotta",  (0.68, 0.38, 0.24), (0.55, 0.47, 0.40)),
    'CUSTOM':     ("Custom", None, None),
}
SOLID_LOOKS = {
    'CONCRETE':   ("Concrete",    (0.60, 0.60, 0.58), None),
    'WARM_GRAY':  ("Warm Gray",   (0.72, 0.69, 0.64), None),
    'CARPET':     ("Carpet Beige",(0.76, 0.70, 0.60), None),
    'BLACK':      ("Black",       (0.08, 0.08, 0.08), None),
    'CUSTOM':     ("Custom", None, None),
}
LOOKS = {'WOOD': WOOD_LOOKS, 'TILE': TILE_LOOKS, 'SOLID': SOLID_LOOKS}
DEFAULT_LOOK = {'WOOD': 'NATURAL', 'TILE': 'LIGHT_GRAY', 'SOLID': 'CONCRETE'}
DEFAULT_SIZE = {'WOOD': 0.127, 'TILE': 0.3048, 'SOLID': 0.3048}   # 5" plank, 12" tile
DEFAULT_ROUGHNESS = {'WOOD': 0.45, 'TILE': 0.2, 'SOLID': 0.7}


def _floor_objects(scene):
    return [o for o in scene.objects if o.get('IS_FLOOR_BP') and o.type == 'MESH']


def build_floor_material(style, base_srgb, accent_srgb, size, roughness,
                         running_bond=False):
    """Create or rebuild the shared floor material and return it."""
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if mat is None:
        mat = bpy.data.materials.new(MATERIAL_NAME)
    base = sm.srgb_to_linear(base_srgb)
    accent = sm.srgb_to_linear(accent_srgb) if accent_srgb else base
    if style == 'WOOD':
        sm.build_wood_nodes(mat, base, accent, size, roughness)
    elif style == 'TILE':
        # The floor has always had a fixed 0.004 Mortar Size, which is a
        # half-width in metres -- so an 8 mm joint whatever the tile.
        # Pass that as the joint width to keep the floor exactly as it
        # has always looked.
        sm.build_tile_nodes(mat, base, accent, size, size, roughness,
                            running_bond, grout_size=0.008)
    else:
        sm.build_solid_nodes(mat, base, roughness)
    mat["HB_FLOOR_STYLE"] = style
    return mat


def _look_items_cb(self, context):
    return [(k, v[0], "") for k, v in LOOKS[self.style].items()]


def _apply_look(self):
    look = LOOKS[self.style].get(self.look)
    if not look or look[1] is None:
        return
    self.color = look[1]
    if look[2] is not None:
        self.accent = look[2]


def _style_changed(self, context):
    self.look = DEFAULT_LOOK[self.style]
    self.size = DEFAULT_SIZE[self.style]
    self.roughness = DEFAULT_ROUGHNESS[self.style]
    _apply_look(self)


def _look_changed(self, context):
    _apply_look(self)


class HOME_BUILDER_OT_floor(bpy.types.Operator):
    bl_idname = "home_builder.floor"
    bl_label = "Floor"
    bl_description = ("Add a floor from the wall layout and give it a "
                      "wood, tile, or solid-color material. Run again to "
                      "restyle the existing floor")
    bl_options = {'REGISTER', 'UNDO'}

    style: EnumProperty(name="Style", items=STYLE_ITEMS, default='WOOD',
                        update=_style_changed)  # type: ignore
    look: EnumProperty(name="Look", items=_look_items_cb,
                       update=_look_changed)  # type: ignore
    color: FloatVectorProperty(
        name="Color", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.64, 0.45, 0.27))  # type: ignore
    accent: FloatVectorProperty(
        name="Accent", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.48, 0.32, 0.18),
        description="Darker plank tone for wood; grout color for tile")  # type: ignore
    size: FloatProperty(
        name="Size", default=0.127, min=0.02, max=2.0, unit='LENGTH',
        description="Plank width for wood; tile size for tile")  # type: ignore
    roughness: FloatProperty(
        name="Roughness", default=0.45, min=0.0, max=1.0, subtype='FACTOR',
        description="0 = glossy, 1 = matte")  # type: ignore
    running_bond: BoolProperty(
        name="Running Bond", default=False,
        description="Offset every other row of tile (brick pattern) "
                    "instead of a straight grid")  # type: ignore

    def invoke(self, context, event):
        _apply_look(self)
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "style", expand=True)
        layout.prop(self, "look")
        col = layout.column(align=True)
        col.prop(self, "color")
        if self.style == 'WOOD':
            col.prop(self, "accent", text="Variation")
            col.prop(self, "size", text="Plank Width")
        elif self.style == 'TILE':
            col.prop(self, "accent", text="Grout")
            col.prop(self, "size", text="Tile Size")
            col.prop(self, "running_bond")
        layout.prop(self, "roughness")
        if not _floor_objects(context.scene):
            layout.label(text="A floor will be created from the walls.",
                         icon='INFO')

    def execute(self, context):
        scene = context.scene
        floors = _floor_objects(scene)
        if not floors:
            try:
                res = bpy.ops.home_builder_walls.add_floor()
            except Exception as exc:
                self.report({'ERROR'}, f"Add Floor failed: {exc}")
                return {'CANCELLED'}
            floors = _floor_objects(scene)
            if 'FINISHED' not in res or not floors:
                self.report({'ERROR'}, "Could not create a floor (draw walls first)")
                return {'CANCELLED'}

        mat = build_floor_material(
            self.style, tuple(self.color),
            tuple(self.accent) if self.style != 'SOLID' else None,
            self.size, self.roughness, self.running_bond)
        for ob in floors:
            sm.assign(ob, mat)

        look = LOOKS[self.style].get(self.look, ("Custom",))[0]
        style_label = {i[0]: i[1] for i in STYLE_ITEMS}[self.style]
        self.report({'INFO'}, f"Floor: {look} {style_label}")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Clearing the room shell
# ---------------------------------------------------------------------------

# Add Floor / Add Ceiling / Add Room Lights tag what they build, and Floor
# goes through Add Floor, so these three tags cover all the dressing.
SCENERY_TAGS = ('IS_FLOOR_BP', 'IS_CEILING_BP', 'IS_ROOM_LIGHT')


def _scenery_objects(scene):
    """Floor, ceiling and room lights of a scene, with their children.

    These are what get in the way of looking at the cabinets: the floor and
    ceiling planes hide whatever the camera sits behind, and the light
    objects clutter the viewport. Materialised up front so a caller can
    delete from the list without mutating the collection it walks.
    """
    objs = []
    seen = set()
    for obj in scene.objects:
        if not any(obj.get(tag) for tag in SCENERY_TAGS):
            continue
        for target in [obj] + list(obj.children_recursive):
            if target.name not in seen:
                seen.add(target.name)
                objs.append(target)
    return objs


class HOME_BUILDER_OT_toggle_room_scenery(bpy.types.Operator):
    bl_idname = "home_builder.toggle_room_scenery"
    bl_label = "Hide/Show"
    bl_description = ("Hide the floor, ceiling, and room lights in the "
                      "viewport and in renders, or show them again if they "
                      "are already hidden")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = _scenery_objects(context.scene)
        if not objs:
            self.report({'WARNING'}, "No floor, ceiling, or room lights here")
            return {'CANCELLED'}

        # Anything still visible means the room is "shown", so the button
        # hides; only once everything is hidden does it bring them back.
        hide = any(not obj.hide_viewport for obj in objs)
        for obj in objs:
            obj.hide_viewport = hide
            obj.hide_render = hide
            # Also drive the eye icon, which is what the user toggled if
            # they hid one of these by hand.
            try:
                obj.hide_set(hide)
            except RuntimeError:
                pass  # not in the active view layer

        self.report({'INFO'},
                    ("Hid " if hide else "Showed ") + f"{len(objs)} object(s)")
        return {'FINISHED'}


class HOME_BUILDER_OT_delete_room_scenery(bpy.types.Operator):
    bl_idname = "home_builder.delete_room_scenery"
    bl_label = "Delete"
    bl_description = ("Remove the floor, ceiling, and room lights from this "
                      "room, leaving the walls and the cabinets")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        objs = _scenery_objects(scene)
        if not objs:
            self.report({'WARNING'}, "No floor, ceiling, or room lights here")
            return {'CANCELLED'}

        count = len(objs)
        light_data = [obj.data for obj in objs
                      if obj.type == 'LIGHT' and obj.data is not None]
        for obj in objs:
            bpy.data.objects.remove(obj, do_unlink=True)
        for data in light_data:
            if data.users == 0:
                bpy.data.lights.remove(data)

        # Drop the now-empty lights collection Add Room Lights made (old
        # and new naming).
        for col_name in (f"{scene.name} - Lights", "Room Lights"):
            col = bpy.data.collections.get(col_name)
            if col is not None and not col.objects:
                if col.name in scene.collection.children:
                    scene.collection.children.unlink(col)
                bpy.data.collections.remove(col)

        self.report({'INFO'}, f"Deleted {count} object(s)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Palette option form
# ---------------------------------------------------------------------------

ROOM_LIGHTS_OPTIONS = 'room_lights_options'


def draw_room_lights_options(layout, context):
    """Add / hide / clear for the room dressing.

    Add Room Lights does not replace what is already there, so pressing
    the tool twice doubles them up. Clear is the way out of that, and
    sits next to Add rather than in another panel.
    """
    scene = context.scene
    lights = [o for o in scene.objects if o.get('IS_ROOM_LIGHT')]
    col = layout.column(align=True)
    if lights:
        col.label(text='%d room light(s) in this room' % len(lights),
                  icon='LIGHT_POINT')
    else:
        col.label(text='No room lights yet', icon='INFO')

    row = layout.row(align=True)
    row.scale_y = 1.2
    row.operator('home_builder_walls.add_room_lights',
                 text='Add Lights', icon='LIGHT_POINT')
    sub = row.row(align=True)
    sub.enabled = bool(lights)
    sub.operator('home_builder_walls.delete_room_lights',
                 text='Clear Lights', icon='X')

    layout.separator()
    layout.label(text='Floor, ceiling and lights together:')
    row = layout.row(align=True)
    row.operator('home_builder.toggle_room_scenery', text='Hide/Show',
                 icon='HIDE_OFF')
    row.operator('home_builder.delete_room_scenery', text='Delete',
                 icon='TRASH')


classes = [
    HOME_BUILDER_OT_floor,
    HOME_BUILDER_OT_toggle_room_scenery,
    HOME_BUILDER_OT_delete_room_scenery,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    room_palette.register_tool_options(ROOM_LIGHTS_OPTIONS,
                                       draw_room_lights_options)


def unregister():
    room_palette.unregister_tool_options(ROOM_LIGHTS_OPTIONS)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
