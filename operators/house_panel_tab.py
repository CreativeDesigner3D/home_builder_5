"""HOUSE tab for the viewport panel -- house projects, levels and rooms.

Drawn with the Options tab's widgets (options_panel.build_page): before
a house project is started the tab offers to start one. In the house
scene a row of icon tabs across the top picks one page at a time, so
the panel stays short:

* Levels -- the level list as a pool (pick a level to draw on it, a
  second click renames it, NEW adds one on top, the delete chip removes
  the active one), its heights, and what the viewport shows.
* Outside -- the siding on the outside walls (the house's, and the
  gables', the active level's or the selected walls' own) and the base.
* Roof -- the active level's roof and its pieces.
* Rooms -- the active level's rooms, another pool: pick a room to see
  its area and set its floor, ceiling and porch. Rooms are found from
  the walls, so the list has no NEW or delete.

Long pages fold into groups whose header says what is set inside (a
floor's finish, a roof's overhangs), so they read at a glance and open
where they are needed. See hb_house and hb_rooms for the data.
"""

import sys

import bpy
import gpu

from .. import hb_house
from .. import hb_rooms
from .. import units
from ..hb_gpu_draw import draw_rect, draw_text, point_in_rect
from ..hb_gpu_ui import (Theme, scale, paint_button, draw_polyline, text_width,
                         fit_text, enum_label)

TAB_KEY = 'HOUSE'
TAB_LABEL = "HOUSE"
TAB_ORDER = 5           # between ROOMS (0) and LIBRARY (10)
PREFERRED_WIDTH = 280   # unscaled

TABS_H = 26             # the page tabs' height, unscaled
TABS_GAP = 6            # and the space under them
FONT = 11

_list = None            # this tab's ScrollList, made on first build
_page = 'LEVELS'        # the page on show


def available(scene):
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return False
    return _tab_enabled() or bool(scene.get('IS_HOUSE_SCENE'))


def _tab_enabled():
    """The House Tab preference (off by default while houses are in
    development)."""
    addon = bpy.context.preferences.addons.get(hb_house.__package__)
    return bool(addon and getattr(addon.preferences, 'show_house_tab', False))


def _length(owner, value):
    return units.unit_to_string(owner.id_data.unit_settings, value)


def _label(owner, prop):
    try:
        return enum_label(owner, prop)
    except Exception:
        return str(getattr(owner, prop, ""))


# ---- Levels -----------------------------------------------------------------

def _view_summary(house):
    shown = [_label(house, 'level_display')]
    if house.show_roofs:
        shown.append("roofs")
    if house.show_ceilings:
        shown.append("ceilings")
    if house.show_room_labels:
        shown.append("labels")
    return " · ".join(shown)


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
}

# The plan view first: it sets most of what the Show group holds.
PLAN_VIEW_FIELDS = (
    ('enum', 'plan_view', "View"),
    ('gap', None, ""),
)

def _framing_summary(house):
    if not house.show_framing:
        return "Off"
    return f"{house.framing_spacing}\" o.c. · " + ("crawlspace" if house.ground_floor == 'CRAWL' else "slab")


VIEW_FIELDS = (
    ('group', 'house_view', "Show", {'summary': _view_summary, 'fields': (
        ('enum', 'level_display', "Levels"),
        ('bool', 'show_level_below', "Ghost Level Below",
         {'when': lambda house: house.level_display == 'ACTIVE'}),
        ('bool', 'show_roofs', "Roofs"),
        ('bool', 'show_ceilings', "Ceilings"),
        ('bool', 'show_room_labels', "Room Labels"),
        ('bool', 'show_framing', "Framing"),
    )}),
    ('pick', lambda context: _import_entries(context), "Import Room as Level"),
)


# ---- Backdrop -----------------------------------------------------------------
# A plan to trace on the active level (hb_backdrop)

def _backdrop_summary(level):
    from .. import hb_backdrop
    return hb_backdrop.backdrop_summary(level)


BACKDROP_FIELDS = (
    ('group', 'house_backdrop', "Backdrop", {'summary': _backdrop_summary, 'fields': (
        ('actions', (("Add PDF / Image", "home_builder.add_backdrop"),
                     ("Set Scale", "home_builder.scale_backdrop")), ""),
        ('bool', 'backdrop_shown', "Show"),
        ('bool', 'backdrop_locked', "Lock"),
        ('number', 'backdrop_opacity', "Opacity"),
        ('actions', (("Remove", "home_builder.remove_backdrop"),), ""),
        ('notes', lambda context: ("Or drop a PDF on the view. Set Scale:",
                                   "click both ends of a printed dimension",
                                   "and type its length."), ""),
    )}),
)


# ---- Structure ----------------------------------------------------------------
# What the house is built of: its framing now, its foundation and wall
# layers as they come.

STRUCTURE_FIELDS = (
    ('group', 'house_framing', "Framing", {'summary': _framing_summary, 'fields': (
        ('bool', 'show_framing', "Show Framing"),
        ('choices', 'framing_spacing', "Spacing", {'cols': 2}),
        ('choices', 'ground_floor', "Ground Floor", {'cols': 2}),
        ('bool', 'framing_walls', "Walls"),
        ('bool', 'framing_floors', "Floors"),
        ('bool', 'framing_ceilings', "Ceilings"),
        ('bool', 'framing_roofs', "Roofs"),
        ('actions', (("Rebuild Framing", "home_builder.rebuild_framing"),), ""),
    )}),
)


# ---- Outside ----------------------------------------------------------------

def _gable_summary(house):
    return _label(house, 'gable_siding_style')


def _overriding(owner):
    return owner.siding_style not in ('INHERIT', 'NONE')


EXTERIOR_FIELDS = (
    ('label', None, "Siding"),
    ('enum', 'siding_style', "Siding"),
    ('native', 'siding_color', "Siding Color", {'when': lambda h: h.siding_style != 'NONE'}),
    ('bool', 'siding_geometry', "Real Geometry"),
    ('group', 'outside_gables', "Gables", {'summary': _gable_summary, 'fields': (
        ('enum', 'gable_siding_style', "Gable Siding"),
        ('native', 'gable_siding_color', "Gable Color",
         {'when': lambda h: h.gable_siding_style not in ('INHERIT', 'NONE')}),
    )}),
)

BASE_FIELDS = (
    ('label', None, "Base"),
    ('enum', 'base_style', "Base"),
    ('distance', 'base_height', "Base Height", {'when': lambda h: h.base_style != 'NONE'}),
    ('native', 'base_color', "Base Color", {'when': lambda h: h.base_style != 'NONE'}),
)


def _level_siding_fields(level):
    return (
        ('group', 'outside_level', f"{level.name} Walls",
         {'summary': lambda lv: _label(lv, 'siding_style'), 'fields': (
             ('enum', 'siding_style', "Siding"),
             ('native', 'siding_color', "Siding Color", {'when': _overriding}),
         )}),
    )


def _selected_walls(context):
    return [o for o in context.selected_objects
            if o.get('IS_WALL_BP') and o.get('WALL_TYPE', 'Exterior') == 'Exterior']


def _wall_siding_fields(count):
    word = "Wall" if count == 1 else f"{count} Walls"
    return (
        ('group', 'outside_walls', f"Selected {word}",
         {'summary': lambda ws: _label(ws, 'style'), 'fields': (
             ('enum', 'style', "Siding"),
             ('native', 'color', "Siding Color",
              {'when': lambda ws: ws.style not in ('INHERIT', 'NONE')}),
         )}),
    )


# ---- Roof -------------------------------------------------------------------

def _on(roof):
    return roof.enabled


def _footprint_summary(roof):
    if not roof.use_extents:
        return "The walls' outline"
    return f"Custom, {_length(roof, roof.ext_x1 - roof.ext_x0)} x {_length(roof, roof.ext_y1 - roof.ext_y0)}"


def _overhang_summary(roof):
    out = f"{_length(roof, roof.eave_overhang)} eaves"
    if roof.style != 'HIP':
        out += f" · {_length(roof, roof.gable_overhang)} gables"
    return out


def _dormer_summary(roof):
    if not roof.dormers:
        return "Off"
    return f"On · {roof.dormer_pitch:g} in 12"


ROOF_FIELDS = (
    ('actions', (("Fit Roof to Outline", "home_builder.fit_roof_to_outline"),
                 ("Edit Roof", "home_builder.edit_roof")), ""),
    ('bool', 'enabled', "Roof on This Level"),
    ('enum', 'style', "Style", {'when': _on}),
    ('enum', 'base', "Sits On", {'when': _on}),
    ('distance', 'eave_height', "Eave Height", {'when': _on}),
    ('number', 'pitch', "Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style in ('GABLE', 'HIP')}),
    ('number', 'lower_pitch', "Lower Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('distance', 'break_height', "Break Height",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('number', 'pitch', "Upper Pitch (in 12)",
     {'when': lambda roof: roof.enabled and roof.style == 'GAMBREL'}),
    ('enum', 'ridge', "Ridge", {'when': _on}),
    ('bool', 'rise_through', "Upper Floor Rises Through", {'when': _on}),
    ('group', 'roof_footprint', "Footprint", {'when': _on, 'summary': _footprint_summary, 'fields': (
        ('bool', 'use_extents', "Custom Footprint"),
        ('distance', 'ext_x0', "Left", {'when': lambda roof: roof.use_extents}),
        ('distance', 'ext_x1', "Right", {'when': lambda roof: roof.use_extents}),
        ('distance', 'ext_y0', "Front", {'when': lambda roof: roof.use_extents}),
        ('distance', 'ext_y1', "Back", {'when': lambda roof: roof.use_extents}),
    )}),
    ('group', 'roof_build', "Overhangs & Finish", {'when': _on, 'summary': _overhang_summary, 'fields': (
        ('distance', 'eave_overhang', "Eave Overhang"),
        ('distance', 'gable_overhang', "Gable Overhang",
         {'when': lambda roof: roof.style != 'HIP'}),
        ('distance', 'thickness', "Thickness"),
        ('native', 'material', "Material"),
    )}),
    ('group', 'roof_bump_dormers', "Bump-out Dormers", {'when': _on, 'summary': _dormer_summary, 'fields': (
        ('bool', 'dormers', "Dormers from Bump-outs"),
        ('number', 'dormer_pitch', "Dormer Pitch (in 12)", {'when': lambda roof: roof.dormers}),
        ('distance', 'dormer_wall_height', "Dormer Wall Height", {'when': lambda roof: roof.dormers}),
        ('distance', 'dormer_overhang', "Dormer Overhang", {'when': lambda roof: roof.dormers}),
    )}),
)


def _piece_size(piece):
    return f"{_length(piece, abs(piece.x1 - piece.x0))} x {_length(piece, abs(piece.y1 - piece.y0))}"


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
                 ("Add Shed Dormer", "home_builder.add_roof_piece", {'kind': 'SHED'}, None)),
                (("Add Gable Dormer", "home_builder.add_roof_piece", {'kind': 'DORMER'}, None),)),
    'fields': (
        ('enum', 'kind', "Kind"),
        ('distance', 'eave_height', "Eave Height", {'when': lambda p: p.kind == 'GABLE'}),
        ('distance', 'eave_height', "Front Wall Height",
         {'when': lambda p: p.kind in ('SHED', 'DORMER')}),
        ('number', 'pitch', "Pitch (in 12)"),
        ('distance', 'overhang', "Overhang"),
        ('group', 'piece_edges', "Position", {'summary': _piece_size, 'fields': (
            ('distance', 'x0', "Left Edge"),
            ('distance', 'x1', "Right Edge"),
            ('distance', 'y0', "Front Edge"),
            ('distance', 'y1', "Back Edge"),
        )}),
    ),
}


# ---- Rooms ------------------------------------------------------------------

def _room_area(room):
    if room.orphaned:
        return "Not enclosed"
    return hb_rooms.area_text(room.id_data, room.area)


def _room_height_note(context, room):
    if room.ceiling_height > 0:
        return ()
    level = hb_rooms.level_of_room(room)
    height = units.unit_to_string(room.id_data.unit_settings, level.ceiling_height)
    return (f"0 follows the level ({height})",)


def _styled(room):
    """A wood, tile, solid, deck or carpet floor: the procedural finishes."""
    return room.has_floor and room.floor_finish in ('WOOD', 'TILE', 'SOLID', 'DECK', 'CARPET')


def _planked(room):
    return _styled(room) and room.floor_finish in ('WOOD', 'DECK')


def _room_row(room):
    return room.name + ("  (not enclosed)" if room.orphaned else "")


def _floor_summary(room):
    if not room.has_floor:
        return "None"
    out = _label(room, 'floor_finish')
    if _styled(room):
        out += " · " + _label(room, 'floor_look')
    if room.floor_auto:
        out += " (default)"
    return out


def _has_looks(finish):
    return finish in ('WOOD', 'TILE', 'SOLID', 'DECK', 'CARPET')


def _defaults_summary(house):
    parts = []
    for kind in hb_house.FLOOR_KINDS[:3]:
        parts.append(_label(house, f'floor_{kind}_finish').split()[0])
    return " · ".join(parts)


FLOOR_DEFAULT_FIELDS = (
    ('group', 'floor_defaults', "Floor Defaults", {'summary': _defaults_summary, 'fields': (
        ('enum', 'floor_room_finish', "Rooms"),
        ('enum', 'floor_room_look', "Look", {'when': lambda h: _has_looks(h.floor_room_finish)}),
        ('enum', 'floor_wet_finish', "Baths & Laundry"),
        ('enum', 'floor_wet_look', "Look", {'when': lambda h: _has_looks(h.floor_wet_finish)}),
        ('enum', 'floor_garage_finish', "Garages"),
        ('enum', 'floor_garage_look', "Look", {'when': lambda h: _has_looks(h.floor_garage_finish)}),
        ('enum', 'floor_porch_finish', "Porches & Patios"),
        ('enum', 'floor_porch_look', "Look", {'when': lambda h: _has_looks(h.floor_porch_finish)}),
        ('enum', 'floor_outdoor_finish', "Decks & Balconies"),
        ('enum', 'floor_outdoor_look', "Look", {'when': lambda h: _has_looks(h.floor_outdoor_finish)}),
        ('notes', lambda context: ("Rooms take these from their names; a floor",
                                   "chosen by hand stays."), ""),
        ('actions', (("Apply to All Rooms", "home_builder.apply_floor_defaults"),), ""),
    )}),
)


def _ceiling_summary(room):
    height = room.ceiling_height
    if height <= 0:
        level = hb_rooms.level_of_room(room)
        height = level.ceiling_height if level is not None else 0.0
    if not room.has_ceiling:
        return f"None · walls {_length(room, height)}"
    return f"{_label(room, 'ceiling_style')} · {_length(room, height)}"


def _porch_summary(room):
    return f"Roof: {_label(room, 'porch_roof')} · {_length(room, room.post_width)} posts"


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
        ('enum', 'room_type', "Room Type"),
        ('bool', 'outdoor', "Outdoor"),
        ('group', 'room_floor', "Floor", {'summary': _floor_summary, 'fields': (
            ('bool', 'floor_auto', "Use House Default"),
            ('bool', 'has_floor', "Floor"),
            ('enum', 'floor_finish', "Floor Finish", {'when': lambda room: room.has_floor}),
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
        )}),
        ('group', 'room_ceiling', "Ceiling", {'summary': _ceiling_summary, 'fields': (
            ('distance', 'ceiling_height', "Ceiling Height"),
            ('notes', _room_height_note, "", {'owner': True}),
            ('bool', 'has_ceiling', "Ceiling"),
            ('enum', 'ceiling_style', "Ceiling Shape", {'when': lambda room: room.has_ceiling}),
            ('distance', 'vault_peak', "Peak Height",
             {'when': lambda room: room.has_ceiling and room.ceiling_style == 'VAULTED'}),
            ('native', 'ceiling_material', "Ceiling Material",
             {'when': lambda room: room.has_ceiling}),
        )}),
        ('group', 'room_porch', "Porch", {'when': lambda room: room.is_porch,
                                          'summary': _porch_summary, 'fields': (
            ('enum', 'porch_roof', "Porch Roof"),
            ('number', 'porch_roof_pitch', "Porch Roof Pitch (in 12)",
             {'when': lambda room: room.porch_roof != 'NONE'}),
            ('distance', 'post_width', "Post Width"),
            ('distance', 'post_spacing', "Post Spacing (most)"),
            ('distance', 'beam_depth', "Beam Depth"),
            ('distance', 'floor_drop', "Step Down"),
            ('native', 'post_material', "Post Material"),
        )}),
    ),
    'actions': ((("Rebuild Rooms", "home_builder.rebuild_rooms"),
                 ("Select Marker", "home_builder.select_room")),),
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


# ---- The page tabs ----------------------------------------------------------
# Small line icons, drawn into a square of side `g` centred on (cx, cy).

def _icon_levels(shader, cx, cy, g, color):
    """Three floors stacked."""
    for k in (-1, 0, 1):
        y = cy + k * g * 0.32
        draw_polyline(shader, [(cx - g * 0.45, y - g * 0.08), (cx - g * 0.1, y + g * 0.1),
                               (cx + g * 0.45, y + g * 0.1), (cx + g * 0.1, y - g * 0.08)],
                      color, closed=True)


def _icon_outside(shader, cx, cy, g, color):
    """A house: walls under a gable."""
    h = g * 0.5
    draw_polyline(shader, [(cx - h * 0.8, cy - h), (cx - h * 0.8, cy + h * 0.15), (cx, cy + h),
                           (cx + h * 0.8, cy + h * 0.15), (cx + h * 0.8, cy - h)], color, closed=True)
    draw_polyline(shader, [(cx - h * 0.2, cy - h), (cx - h * 0.2, cy - h * 0.3),
                           (cx + h * 0.2, cy - h * 0.3), (cx + h * 0.2, cy - h)], color)


def _icon_roof(shader, cx, cy, g, color):
    """A roof's slopes over its eaves."""
    h = g * 0.5
    draw_polyline(shader, [(cx - h, cy - h * 0.3), (cx, cy + h * 0.7), (cx + h, cy - h * 0.3)], color)
    draw_polyline(shader, [(cx - h * 0.65, cy - h * 0.05), (cx - h * 0.65, cy - h * 0.8),
                           (cx + h * 0.65, cy - h * 0.8), (cx + h * 0.65, cy - h * 0.05)], color)


def _icon_rooms(shader, cx, cy, g, color):
    """A plan of rooms."""
    h = g * 0.45
    draw_polyline(shader, [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)],
                  color, closed=True)
    draw_polyline(shader, [(cx - h * 0.1, cy - h), (cx - h * 0.1, cy + h)], color)
    draw_polyline(shader, [(cx - h * 0.1, cy + h * 0.05), (cx + h, cy + h * 0.05)], color)


def _icon_structure(shader, cx, cy, g, color):
    """A framed wall: studs between plates."""
    h = g * 0.45
    draw_polyline(shader, [(cx - h, cy - h), (cx + h, cy - h)], color)
    draw_polyline(shader, [(cx - h, cy + h), (cx + h, cy + h)], color)
    for k in (-1.0, -0.33, 0.33, 1.0):
        draw_polyline(shader, [(cx + h * k, cy - h), (cx + h * k, cy + h)], color)


PAGES = (
    ('LEVELS', "Levels", _icon_levels),
    ('OUTSIDE', "Outside", _icon_outside),
    ('ROOF', "Roof", _icon_roof),
    ('ROOMS', "Rooms", _icon_rooms),
    ('STRUCTURE', "Structure", _icon_structure),
)


def set_page(key):
    global _page
    if key in [p[0] for p in PAGES] and key != _page:
        _page = key
        _scroll_list().offset = 0.0     # each page opens at its top


def current_page():
    return _page


def _tabs_shown(context):
    scene = context.scene
    return (hb_house.is_house_project(context) and not hb_house.is_room_view(scene)
            and bool(scene.get(hb_house.HOUSE_SCENE_KEY)))


def _tab_cells(rect):
    x0, y0, w, h = rect
    n = len(PAGES)
    bw = w / n
    return [(key, label, icon, (x0 + i * bw, y0, bw, h)) for i, (key, label, icon) in enumerate(PAGES)]


def _paint_tabs(entry, mx, my):
    _kind, rect = entry
    s = scale()
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    font = 0
    for key, label, icon, cell in _tab_cells(rect):
        x, y, w, h = cell
        inner = (x + 1 * s, y, w - 2 * s, h)
        active = key == _page
        hot = point_in_rect(mx, my, cell)
        paint_button(shader, inner, hovered=hot, active=active)
        color = Theme.TEXT_PRIMARY if (active or hot) else Theme.TEXT_NORMAL
        g = 12 * s
        shown = fit_text(font, FONT * s, label, w - g - 14 * s)
        tw = text_width(font, FONT * s, shown)
        total = g + 5 * s + tw
        left = x + (w - total) / 2.0
        shader.bind()
        icon(shader, left + g / 2.0, y + h / 2.0, g, color)
        draw_text(font, left + g + 5 * s, y + h * 0.32, FONT * s, color, shown)


# ---- The pages ----------------------------------------------------------------

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

    level = hb_house.active_level(context)
    where = f" · {level.name}" if level is not None else ""
    if _page == 'LEVELS':
        blocks = options_panel.field_blocks(context, PLAN_VIEW_FIELDS, scene.hb_house)
        blocks.extend(options_panel.pool_blocks(context, LEVEL_SPEC))
        if level is not None:
            blocks.extend(options_panel.field_blocks(context, BACKDROP_FIELDS, level))
        blocks.append(('gap', None))
        blocks.extend(options_panel.field_blocks(context, VIEW_FIELDS, scene.hb_house))
    elif _page == 'OUTSIDE':
        blocks = [('head', ("Outside", False, None))]
        blocks.extend(options_panel.field_blocks(context, EXTERIOR_FIELDS, scene.hb_house))
        if level is not None:
            blocks.extend(options_panel.field_blocks(context, _level_siding_fields(level), level))
        walls = _selected_walls(context)
        if walls:
            owner = context.active_object if context.active_object in walls else walls[0]
            blocks.extend(options_panel.field_blocks(context, _wall_siding_fields(len(walls)),
                                                     owner.hb_siding))
        else:
            blocks.append(('note', "Select outside walls to give them their own siding."))
        blocks.append(('gap', None))
        blocks.extend(options_panel.field_blocks(context, BASE_FIELDS, scene.hb_house))
    elif _page == 'ROOF':
        blocks = [('head', ("Roof" + where, False, None))]
        if level is not None:
            blocks.extend(options_panel.field_blocks(context, ROOF_FIELDS, level.roof))
            if level.roof.enabled:
                blocks.append(('gap', None))
                blocks.extend(options_panel.pool_blocks(context, PIECE_SPEC))
                blocks.append(('note', "Draw pieces in Edit Roof (G, D, A),"))
                blocks.append(('note', "or select walls and use an Add button."))
    elif _page == 'STRUCTURE':
        blocks = [('head', ("Structure", False, None))]
        blocks.extend(options_panel.field_blocks(context, STRUCTURE_FIELDS, scene.hb_house))
    else:
        blocks = options_panel.field_blocks(context, FLOOR_DEFAULT_FIELDS, scene.hb_house)
        blocks.append(('gap', None))
        if level is not None:
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
    if not _tabs_shown(context):
        return options_panel.build_page(rect, context, _blocks, _scroll_list())
    s = scale()
    x0, bottom, w, h = rect
    th, gap = TABS_H * s, TABS_GAP * s
    entries = options_panel.build_page((x0, bottom, w, h - th - gap), context, _blocks,
                                       _scroll_list())
    # The tabs stay put at the top while the page under them scrolls
    entries.append(('house_tabs', (x0, bottom + h - th, w, th)))
    return entries


def _split(entries):
    tabs = [e for e in entries if e[0] == 'house_tabs']
    return [e for e in entries if e[0] != 'house_tabs'], (tabs[0] if tabs else None)


def paint(entries, mx, my):
    from . import options_panel
    rest, tabs = _split(entries)
    options_panel.paint(rest, mx, my)
    if tabs is not None:
        _paint_tabs(tabs, mx, my)


def hit(context, mx, my, entries):
    from . import options_panel
    rest, tabs = _split(entries)
    if tabs is not None and point_in_rect(mx, my, tabs[1]):
        for key, _label_, _icon, cell in _tab_cells(tabs[1]):
            if point_in_rect(mx, my, cell):
                set_page(key)
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
                return True
        return True
    return options_panel.hit(context, mx, my, rest)


def scroll(mx, my, entries, rows):
    from . import options_panel
    rest, _tabs = _split(entries)
    return options_panel.scroll_page(mx, my, rest, rows, _scroll_list())


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
