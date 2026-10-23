"""HOUSE tab for the viewport panel -- house projects and their levels.

Drawn with the Options tab's widgets (options_panel.build_page): before
a house project is started the tab offers to start one; in the house
scene it is the level list as a pool -- pick a level to draw on it, a
second click renames it, NEW adds a level on top and the delete chip
removes the active one -- with the active level's heights below it and
the level display settings under those. See hb_house for the data.
"""

import sys

import bpy

from .. import hb_house

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
    ),
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

    # The pool heads itself ("Levels"), so the tab's own head goes.
    return options_panel.pool_blocks(context, LEVEL_SPEC)


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
