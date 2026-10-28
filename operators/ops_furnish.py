"""The Furnish tool: bath fixtures - and later lights and furniture -
placed straight into a room, without going through a cabinet library.

It is a wall placement tool like the window's (gaps, typed offsets, W
for width, placing on until Esc), picking what it places from the
Furnish catalog on its TOOL page. A fixture stands against the face of
the wall the cursor is on, its back to the wall, and comes in modeled.
"""

import math

import bpy
from mathutils import Vector

from .. import hb_types
from ..product_libraries.common import appliance_geo
from ..product_libraries.interiors import catalog
from . import doors_windows


def _model(cage_obj):
    """A fixture comes in with its model, whatever the room's Show Model
    switch: a room's plan wants to see where the tub is."""
    opts = appliance_geo.defaults_for(cage_obj)
    opts['model_style'] = 'MODELED'
    appliance_geo.set_opts(cage_obj, opts)
    appliance_geo.build_geometry(cage_obj)


def face_wall(cage_obj, wall_obj, x, far_side):
    """Stand a fixture against one face of a wall: its left end at x
    along the wall, its back to the reference face (y = 0), or turned
    round onto the thickness face when `far_side`."""
    cage = hb_types.GeoNodeCage(cage_obj)
    width = cage.get_input('Dim X')
    t = hb_types.GeoNodeWall(wall_obj).get_input('Thickness')
    cage_obj.parent = wall_obj
    if far_side:
        cage_obj.location = (x + width, t, cage_obj.location.z)
        cage_obj.rotation_euler = (0.0, 0.0, math.pi)
    else:
        cage_obj.location = (x, 0.0, cage_obj.location.z)
        cage_obj.rotation_euler = (0.0, 0.0, 0.0)


def place_item(context, key, wall_obj, x, far_side=False):
    """Place a catalog item against a wall without the tool, as a click
    of it would. Returns the new fixture's cage object."""
    cls = catalog.item_class(key)
    if cls is None:
        return None
    fixture = cls()
    fixture.create()
    fixture.obj.location.z = 0.0
    face_wall(fixture.obj, wall_obj, x, far_side)
    _model(fixture.obj)
    return fixture.obj


class HOME_BUILDER_OT_furnish(doors_windows._PlaceWallObjectBase):
    bl_idname = "home_builder.furnish"
    bl_label = "Furnish"
    bl_description = ("Place a bath fixture against a wall: pick it on the TOOL page. "
                      "Arrow keys for offset, W for width")

    OBJECT_NAME = "Fixture"
    OBJECT_LABEL = "fixture"
    TEXT_KIND = None
    BUILD_GEO = False

    def create_placed_object(self, context):
        cls = catalog.item_class(context.scene.hb_house.furnish_item) \
            or catalog.item_class(catalog.ITEMS[0][0])
        fixture = cls()
        fixture.create()
        self.placed_obj, self.swing_obj = fixture, None
        self.register_placement_object(fixture.obj)
        self.create_placement_dimensions()
        self._symbol_key = None

    def set_position_on_wall(self):
        if not self.placed_obj:
            return
        depth = self.placed_obj.get_input('Dim Y')
        super().set_position_on_wall()
        if not self.selected_wall:
            return
        # The placement keeps the depth the fixture has, not the wall's
        self.placed_obj.set_input('Dim Y', depth)
        wall = self.selected_wall
        t = hb_types.GeoNodeWall(wall).get_input('Thickness')
        local = wall.matrix_world.inverted() @ Vector(self.hit_location)
        face_wall(self.placed_obj.obj, wall, self.placement_x, local.y > t / 2.0)

    def cut_wall(self, wall_obj, cutting_obj):
        # A fixture stands in front of the wall: nothing is cut
        _model(cutting_obj)
        return None


def _furnish_changed(self, context):
    """Picked from the catalog while placing: place the new one."""
    from . import tool_session
    if tool_session.active_tool() == HOME_BUILDER_OT_furnish.bl_idname:
        tool_session.restart(context)


classes = (
    HOME_BUILDER_OT_furnish,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
