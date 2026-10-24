"""HOUSE tab for the viewport panel -- house projects, levels and rooms.

Drawn with the Options tab's widgets (options_panel.build_page): before
a house project is started the tab offers to start one; in the house
scene it is the level list as a pool -- pick a level to draw on it, a
second click renames it, NEW adds a level on top and the delete chip
removes the active one -- with the active level's heights below it and
the level display settings under those. Then the active level's rooms,
another pool: pick a room to see its area, ceiling height and finishes;
a second click renames it. Rooms are found from the walls, so the list
has no NEW or delete. See hb_house and hb_rooms for the data.
"""

import sys

import bpy

from .. import hb_house
from .. import hb_rooms

TAB_KEY = 'HOUSE'
TAB_LABEL = "HOUSE"
TAB_ORDER = 5           # between ROOMS (0) and LIBRARY (10)
PREFERRED_WIDTH = 280   # unscaled

_list = None            # this tab's ScrollList, made on first build


def available(scene):
    return not (scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'))


LEVEL_SPEC = {
    'kind': 'pool',
    'title': "Levels",
    'list_label': "Levels",
    'scope': 'scene',
    'props': 'hb_house',
    'collection': 'levels',
    'index': 'active_level_index',
    'add_op': 'home_builder.add_level',
    'remove_op': 'home_builder.remove_level',
    'fields': (
        ('distance', 'elevation', "Elevation"),
        ('distance', 'floor_to_floor', "Floor to Floor"),
        ('distance', 'floor_thickness', "Floor Thickness"),
        ('distance', 'ceiling_height', "Ceiling Height"),
    ),
    'scene_fields': (
        ('enum', 'level_display', "Show"),
        ('bool', 'show_level_below', "Ghost Level Below",
         {'when': lambda house: house.level_display == 'ACTIVE'}),
        ('bool', 'show_ceilings', "Show Ceilings"),
    ),
}


def _room_area(room):
    if room.orphaned:
        return "Not enclosed"
    return hb_rooms.area_text(room.id_data, room.area)


def _room_height_note(context, room):
    if room.ceiling_height > 0:
        return ()
    level = hb_rooms.level_of_room(room)
    from .. import units
    height = units.unit_to_string(room.id_data.unit_settings, level.ceiling_height)
    return (f"0 follows the level ({height})",)


def _styled(room):
    """A wood, tile or solid floor: the Floor tool's procedural finishes."""
    return room.has_floor and room.floor_finish in ('WOOD', 'TILE', 'SOLID')


def _room_row(room):
    return room.name + ("  (not enclosed)" if room.orphaned else "")


ROOM_SPEC = {
    'kind': 'pool',
    'title': "Rooms",
    'list_label': "Rooms",
    'props': hb_house.active_level,
    'collection': 'rooms',
    'index': 'active_room_index',
    'row_text': _room_row,
    'fields': (
        ('value', _room_area, "Area"),
        ('distance', 'ceiling_height', "Ceiling Height"),
        ('notes', _room_height_note, "", {'owner': True}),
        ('bool', 'has_floor', "Floor"),
        ('enum', 'floor_finish', "Floor Finish",
         {'when': lambda room: room.has_floor}),
        ('enum', 'floor_look', "Look", {'when': _styled}),
        ('native', 'floor_color', "Color", {'when': _styled}),
        ('native', 'floor_accent', "Variation",
         {'when': lambda room: _styled(room) and room.floor_finish == 'WOOD'}),
        ('native', 'floor_accent', "Grout",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('distance', 'floor_size', "Plank Width",
         {'when': lambda room: _styled(room) and room.floor_finish == 'WOOD'}),
        ('distance', 'floor_size', "Tile Size",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('bool', 'floor_running_bond', "Running Bond",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('number', 'floor_roughness', "Roughness", {'when': _styled}),
        ('native', 'floor_material', "Material",
         {'when': lambda room: room.has_floor and room.floor_finish == 'CUSTOM'}),
        ('bool', 'has_ceiling', "Ceiling"),
        ('native', 'ceiling_material', "Ceiling Material",
         {'when': lambda room: room.has_ceiling}),
    ),
    'actions': ((("Rebuild Rooms", "home_builder.rebuild_rooms"),
                 ("Select Marker", "home_builder.select_room")),),
}


def _start_notes(context):
    return ("Draw the whole house in one scene,",
            "on levels stacked by elevation.",
            "Walls already in this scene become Level 1.")


def _blocks(context):
    from . import options_panel
    blocks = [('head', ("House", False, None))]
    if not hb_house.is_house_project(context):
        blocks.extend(options_panel.field_blocks(context, (
            ('notes', _start_notes, ""),
            ('actions', (("Start House Project",
                          "home_builder.start_house_project"),), ""),
        ), context.scene))
        return blocks

    scene = context.scene
    if not scene.get(hb_house.HOUSE_SCENE_KEY):
        house_scene = hb_house.get_house_scene()
        if house_scene is None:
            blocks.append(('note', "This project has no house scene."))
            return blocks
        blocks.append(('note', f"The levels are in '{house_scene.name}'."))
        blocks.append(('actions', (
            ("Go to House", "home_builder_layouts.go_to_layout_view",
             {'scene_name': house_scene.name}, None),)))
        return blocks

    # Each pool heads itself ("Levels", "Rooms"), so the tab's own head goes.
    blocks = options_panel.pool_blocks(context, LEVEL_SPEC)
    if hb_house.active_level(context) is not None:
        blocks.append(('gap', None))
        blocks.extend(options_panel.pool_blocks(context, ROOM_SPEC))
    return blocks


def _scroll_list():
    global _list
    if _list is None:
        from . import options_panel
        _list = options_panel.new_scroll_list()
    return _list


# ---- Provider ---------------------------------------------------------------

def build(rect, context):
    from . import options_panel
    return options_panel.build_page(rect, context, _blocks, _scroll_list())


def paint(entries, mx, my):
    from . import options_panel
    options_panel.paint(entries, mx, my)


def hit(context, mx, my, entries):
    from . import options_panel
    return options_panel.hit(context, mx, my, entries)


def scroll(mx, my, entries, rows):
    from . import options_panel
    return options_panel.scroll_page(mx, my, entries, rows, _scroll_list())


def register():
    from . import scene_navigator
    scene_navigator.register_tab(TAB_KEY, sys.modules[__name__],
                                 label=TAB_LABEL, order=TAB_ORDER,
                                 available=available)


def unregister():
    from . import scene_navigator
    try:
        scene_navigator.unregister_tab(TAB_KEY)
    except Exception:
        pass
