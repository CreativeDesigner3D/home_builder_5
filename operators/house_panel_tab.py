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
    'actions': ((("Walk Through", "home_builder.walk_through"),),),
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
        ('bool', 'show_roofs', "Show Roofs"),
        ('pick', lambda context: _import_entries(context), "Import Room as Level"),
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
    """A wood, tile, solid or deck floor: the procedural finishes."""
    return room.has_floor and room.floor_finish in ('WOOD', 'TILE', 'SOLID', 'DECK')


def _planked(room):
    return _styled(room) and room.floor_finish in ('WOOD', 'DECK')


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
        ('bool', 'outdoor', "Outdoor"),
        ('distance', 'ceiling_height', "Ceiling Height"),
        ('notes', _room_height_note, "", {'owner': True}),
        ('bool', 'has_floor', "Floor"),
        ('enum', 'floor_finish', "Floor Finish",
         {'when': lambda room: room.has_floor}),
        ('enum', 'floor_look', "Look", {'when': _styled}),
        ('native', 'floor_color', "Color", {'when': _styled}),
        ('native', 'floor_accent', "Variation", {'when': _planked}),
        ('native', 'floor_accent', "Grout",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('distance', 'floor_size', "Plank Width", {'when': _planked}),
        ('distance', 'floor_size', "Tile Size",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('bool', 'floor_running_bond', "Running Bond",
         {'when': lambda room: _styled(room) and room.floor_finish == 'TILE'}),
        ('number', 'floor_roughness', "Roughness", {'when': _styled}),
        ('native', 'floor_material', "Material",
         {'when': lambda room: room.has_floor and room.floor_finish == 'CUSTOM'}),
        ('distance', 'post_width', "Post Width", {'when': lambda room: room.is_porch}),
        ('distance', 'post_spacing', "Post Spacing (most)", {'when': lambda room: room.is_porch}),
        ('distance', 'beam_depth', "Beam Depth", {'when': lambda room: room.is_porch}),
        ('distance', 'floor_drop', "Step Down", {'when': lambda room: room.is_porch}),
        ('native', 'post_material', "Post Material", {'when': lambda room: room.is_porch}),
        ('bool', 'has_ceiling', "Ceiling"),
        ('enum', 'ceiling_style', "Ceiling Shape", {'when': lambda room: room.has_ceiling}),
        ('distance', 'vault_peak', "Peak Height",
         {'when': lambda room: room.has_ceiling and room.ceiling_style == 'VAULTED'}),
        ('native', 'ceiling_material', "Ceiling Material",
         {'when': lambda room: room.has_ceiling}),
    ),
    'actions': ((("Rebuild Rooms", "home_builder.rebuild_rooms"),
                 ("Select Marker", "home_builder.select_room")),),
}


ROOF_FIELDS = (
    ('bool', 'enabled', "Roof on This Level"),
    ('enum', 'style', "Style", {'when': lambda roof: roof.enabled}),
    ('enum', 'base', "Sits On", {'when': lambda roof: roof.enabled}),
    ('distance', 'eave_height', "Eave Height", {'when': lambda roof: roof.enabled}),
    ('number', 'pitch', "Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style == 'GABLE'}),
    ('number', 'lower_pitch', "Lower Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('distance', 'break_height', "Break Height",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('number', 'pitch', "Upper Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('enum', 'ridge', "Ridge", {'when': lambda roof: roof.enabled}),
    ('distance', 'eave_overhang', "Eave Overhang", {'when': lambda roof: roof.enabled}),
    ('distance', 'gable_overhang', "Gable Overhang", {'when': lambda roof: roof.enabled}),
    ('distance', 'thickness', "Thickness", {'when': lambda roof: roof.enabled}),
    ('native', 'material', "Material", {'when': lambda roof: roof.enabled}),
    ('bool', 'dormers', "Dormers from Bump-outs", {'when': lambda roof: roof.enabled}),
    ('number', 'dormer_pitch', "Dormer Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.dormers}),
    ('distance', 'dormer_wall_height', "Dormer Wall Height",
     {'when': lambda roof: roof.enabled and roof.dormers}),
    ('distance', 'dormer_overhang', "Dormer Overhang",
     {'when': lambda roof: roof.enabled and roof.dormers}),
)


PIECE_SPEC = {
    'kind': 'pool',
    'title': "Roof Pieces",
    'list_label': "Roof Pieces",
    'props': lambda context: hb_house.active_level(context).roof,
    'collection': 'pieces',
    'index': 'active_piece_index',
    'remove_op': 'home_builder.remove_roof_piece',
    'allow_empty': True,
    'actions': ((("Add Cross Gable", "home_builder.add_roof_piece", {'kind': 'GABLE'}, None),
                 ("Add Shed Dormer", "home_builder.add_roof_piece", {'kind': 'SHED'}, None)),),
    'fields': (
        ('enum', 'kind', "Kind"),
        ('distance', 'x0', "Left Edge"),
        ('distance', 'x1', "Right Edge"),
        ('distance', 'y0', "Front Edge"),
        ('distance', 'y1', "Back Edge"),
        ('distance', 'eave_height', "Eave Height", {'when': lambda p: p.kind == 'GABLE'}),
        ('distance', 'eave_height', "Front Wall Height", {'when': lambda p: p.kind == 'SHED'}),
        ('number', 'pitch', "Pitch (in 12)"),
        ('distance', 'overhang', "Overhang"),
    ),
}


def _import_entries(context):
    """The pick menu for Import Room as Level: each room scene with walls."""
    scenes = hb_house.importable_room_scenes(context.scene)
    if not scenes:
        return [("No room scenes with walls to import", None, {})]
    return [(scene.name, "home_builder.import_room_as_level",
             {'scene_name': scene.name, 'INVOKE': True}) for scene in scenes]


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
    if hb_house.is_room_view(scene):
        # A room view: say which room, the way back, and the level's rooms
        level = hb_house.active_level(context)
        where = f" on {level.name}" if level is not None else ""
        blocks.append(('note', f"Room view of {scene.name}{where}."))
        blocks.append(('actions', (("Go to House", "home_builder.go_to_house",
                                    None, None),)))
        if level is not None:
            blocks.append(('gap', None))
            blocks.extend(options_panel.pool_blocks(context, ROOM_SPEC))
        return blocks

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
    level = hb_house.active_level(context)
    if level is not None:
        blocks.append(('gap', None))
        blocks.append(('head', ("Roof", False, None)))
        blocks.extend(options_panel.field_blocks(context, ROOF_FIELDS, level.roof))
        if level.roof.enabled:
            blocks.append(('gap', None))
            blocks.append(('note', "Select the walls or porch a piece goes over."))
            blocks.extend(options_panel.pool_blocks(context, PIECE_SPEC))
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
