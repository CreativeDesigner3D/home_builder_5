"""Furniture in a house: a piece's settings for the HUD, and its commands.
The pieces themselves are in product_libraries/interiors (types_furniture,
furniture_geo); the Furnish tool places them."""

import bpy

from . import hb_types
from .units import inch


def _fg():
    from .product_libraries.interiors import furniture_geo
    return furniture_geo


def is_furnishing(obj):
    return obj is not None and bool(obj.get('IS_FURNISHING'))


def furnishing_of(obj):
    while obj is not None:
        if is_furnishing(obj):
            return obj
        obj = obj.parent
    return None


def _rebuild(cage):
    _fg().build(cage)


def _dim(name):
    def get(self):
        c = hb_types.GeoNodeCage(self.id_data)
        return c.get_input(name) if c.has_modifier() else 0.0

    def set(self, value):
        hb_types.GeoNodeCage(self.id_data).set_input(name, value)
        _rebuild(self.id_data)
    return get, set


def _enum(key, items, default):
    ids = [i[0] for i in items]

    def get(self):
        value = self.id_data.get(key, default)
        return ids.index(value) if value in ids else 0

    def set(self, index):
        self.id_data[key] = ids[index]
        if key == 'FURNISHING_SIZE':
            # A bed's size sets its width
            c = hb_types.GeoNodeCage(self.id_data)
            c.set_input('Dim X', _fg().BED_SIZES[ids[index]])
        _rebuild(self.id_data)
    return get, set


def _get_chairs(self):
    return int(self.id_data.get('FURNISHING_CHAIRS', 0))


def _set_chairs(self, value):
    self.id_data['FURNISHING_CHAIRS'] = int(value)
    _rebuild(self.id_data)


BED_SIZE_ITEMS = [('TWIN', "Twin", ""), ('FULL', "Full", ""), ('QUEEN', "Queen", ""), ('KING', "King", "")]
SHAPE_ITEMS = [('RECT', "Rectangular", ""), ('ROUND', "Round", "")]
SIDE_ITEMS = [('LEFT', "Left", "The return at the left end"), ('RIGHT', "Right", "The return at the right end")]

_w, _d, _h = _dim('Dim X'), _dim('Dim Y'), _dim('Dim Z')
_size = _enum('FURNISHING_SIZE', BED_SIZE_ITEMS, 'QUEEN')
_shape = _enum('FURNISHING_SHAPE', SHAPE_ITEMS, 'RECT')
_side = _enum('FURNISHING_SIDE', SIDE_ITEMS, 'LEFT')


class HB_Furnishing(bpy.types.PropertyGroup):
    """A piece of furniture's settings, read from and written to its cage."""
    width: bpy.props.FloatProperty(name="Width", min=0.1, max=8.0, subtype='DISTANCE', precision=4,
                                   get=_w[0], set=_w[1])  # type: ignore
    depth: bpy.props.FloatProperty(name="Depth", min=0.1, max=8.0, subtype='DISTANCE', precision=4,
                                   get=_d[0], set=_d[1])  # type: ignore
    height: bpy.props.FloatProperty(name="Height", min=0.005, max=3.0, subtype='DISTANCE', precision=4,
                                    get=_h[0], set=_h[1])  # type: ignore
    bed_size: bpy.props.EnumProperty(name="Size", items=BED_SIZE_ITEMS, get=_size[0], set=_size[1])  # type: ignore
    shape: bpy.props.EnumProperty(name="Shape", items=SHAPE_ITEMS, get=_shape[0], set=_shape[1])  # type: ignore
    chairs: bpy.props.IntProperty(name="Chairs", description="0 seats as many as the table's size allows",
                                  min=0, max=16, get=_get_chairs, set=_set_chairs)  # type: ignore
    side: bpy.props.EnumProperty(name="Return", items=SIDE_ITEMS, get=_side[0], set=_side[1])  # type: ignore


def kind(obj):
    return obj.get('FURNISHING_KIND', '') if obj is not None else ''


def delete(cage):
    for o in [cage] + list(cage.children_recursive):
        mesh = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


class HOME_BUILDER_OT_delete_furnishing(bpy.types.Operator):
    bl_idname = "home_builder.delete_furnishing"
    bl_label = "Delete Furniture"
    bl_description = "Delete this piece of furniture"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return furnishing_of(context.active_object) is not None

    def execute(self, context):
        delete(furnishing_of(context.active_object))
        return {'FINISHED'}


class HOME_BUILDER_OT_turn_furnishing(bpy.types.Operator):
    bl_idname = "home_builder.turn_furnishing"
    bl_label = "Turn"
    bl_description = "Turn this piece a quarter turn about its middle"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        cage = furnishing_of(context.active_object)
        return cage is not None and cage.parent is None

    def execute(self, context):
        import math
        from mathutils import Matrix
        from .operators import ops_furnish
        cage = furnishing_of(context.active_object)
        centre = ops_furnish._centre_local(cage)
        mid = cage.matrix_basis @ centre
        cage.rotation_euler.z += math.pi / 2.0
        off = Matrix.Rotation(cage.rotation_euler.z, 3, 'Z') @ centre
        cage.location = (mid.x - off.x, mid.y - off.y, cage.location.z)
        return {'FINISHED'}


class HOME_BUILDER_MT_furnishing_commands(bpy.types.Menu):
    bl_label = "Furniture"
    bl_idname = "HOME_BUILDER_MT_furnishing_commands"

    def draw(self, context):
        self.layout.operator("home_builder.turn_furnishing", icon='FILE_REFRESH')
        self.layout.separator()
        self.layout.operator("home_builder.delete_furnishing", icon='X')


classes = (
    HB_Furnishing,
    HOME_BUILDER_OT_delete_furnishing,
    HOME_BUILDER_OT_turn_furnishing,
    HOME_BUILDER_MT_furnishing_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_furniture = bpy.props.PointerProperty(type=HB_Furnishing)


def unregister():
    if hasattr(bpy.types.Object, 'hb_furniture'):
        del bpy.types.Object.hb_furniture
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
