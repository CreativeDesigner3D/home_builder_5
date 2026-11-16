"""House items and shared products on the SELECTED tab: walls, doors,
windows, soffits, countertops, backsplashes, appliances, tambours,
beams and posts, and room trim.

None of these but room trim keeps its settings in a property group -- a
wall's size is geometry-node inputs, a door's style is a dict of
options, a soffit is its own scale, a beam is custom properties -- so
each field goes through a prop_proxy schema whose write does what the
item's own dialog does after a change: a wall keeps the walls teeing
into it on its face and re-mitres its corners, a door or window
rebuilds its geometry from its options, a countertop, backsplash,
tambour or beam rebuilds its mesh, an appliance re-solves its cabinet
panels. Under the fields is the item's right-click menu, as on every
page.
"""

import bpy

from .. import hb_utils, units


SOURCE_KEY = 'HOUSE_ITEMS'

APPLIANCE_SCHEMA = 'APPLIANCE'
WALL_SCHEMA = 'WALL'
DOOR_SCHEMA = 'ENTRY_DOOR'
WINDOW_SCHEMA = 'WINDOW'
SOFFIT_SCHEMA = 'SOFFIT'
COUNTERTOP_SCHEMA = 'COUNTERTOP'
BACKSPLASH_SCHEMA = 'BACKSPLASH'
TAMBOUR_SCHEMA = 'TAMBOUR'
MEMBER_SCHEMA = 'MEMBER'

DOOR_OP = 'home_builder_doors_windows.door_prompts'
WINDOW_OP = 'home_builder_doors_windows.window_prompts'


def _door_window(obj):
    while obj is not None:
        if obj.get('IS_ENTRY_DOOR_BP') or obj.get('IS_WINDOW_BP'):
            return obj
        obj = obj.parent
    return None


def _tagged_up(obj, tag):
    while obj is not None:
        if obj.get(tag):
            return obj
        obj = obj.parent
    return None


def find(context):
    obj = context.active_object
    if obj is None or not obj.select_get():
        return None
    dw = _door_window(obj)
    if dw is not None:
        return ('door' if dw.get('IS_ENTRY_DOOR_BP') else 'window', dw)
    for tag, kind in (('IS_SOFFIT_BP', 'soffit'), ('IS_COUNTERTOP', 'countertop'),
                      ('IS_BACKSPLASH', 'backsplash'), ('IS_WALL_BP', 'wall'),
                      ('IS_MEMBER', 'member')):
        if obj.get(tag):
            return (kind, obj)
    tambour = _tagged_up(obj, 'IS_TAMBOUR')
    if tambour is not None:
        return ('tambour', tambour)
    if obj.get('IS_ROOM_TRIM') and _trim_room(obj) is not None:
        return ('room_trim', obj)
    appliance = hb_utils.get_appliance_bp(obj)
    if appliance is not None:
        return ('appliance', appliance)
    return None


def _dist(value):
    return units.unit_to_string(bpy.context.scene.unit_settings, value)


# ---- Appliances ----------------------------------------------------------------

def _appliance_size(name):
    from ..product_libraries.common import appliance_geo
    from . import prop_proxy

    def get(obj):
        try:
            return float(appliance_geo._CageWrap(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        if obj.get(appliance_geo.CABINET_APPLIANCE_FLAG):
            # A typed size takes it over from the cabinet it sits in.
            obj[appliance_geo.SIZE_OWNED_FLAG] = True
        appliance_geo._CageWrap(obj).set_input(name, float(value))
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0)


def _after_appliance(obj, context):
    from ..product_libraries.common import appliance_geo
    # Cabinet door panels are solved from the cage, not driven.
    if appliance_geo.supports_panels(obj) and appliance_geo.is_panel_ready(obj):
        panels = appliance_geo._panels_module()
        if panels is not None:
            panels.rebuild(obj)


def _appliance_label(obj):
    label = obj.get('APPLIANCE_LABEL') or obj.get('APPLIANCE_TYPE') or "Appliance"
    return str(label).replace('_', ' ').title()


# ---- Walls -----------------------------------------------------------------------

def _wall_input(name):
    from . import prop_proxy

    def get(obj):
        from ..hb_types import GeoNodeWall
        try:
            return float(GeoNodeWall(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        from ..hb_types import GeoNodeWall
        from .. import hb_house
        from . import walls
        scene = walls._wall_scene(obj) or bpy.context.scene
        # The wall's own T ends are left out, as the wall dialog does: a
        # length typed here is meant to move its end off the face it
        # tees into.
        tees = [t for t in walls.capture_tees(scene, hb_house.level_of(obj))
                if t[0] != obj]
        GeoNodeWall(obj).set_input(name, float(value))
        walls.restore_tees(tees, scene)
        walls.calculate_wall_miter_angles(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0)


def _sloped(owner):
    from ..hb_types import GeoNodeWall
    try:
        return GeoNodeWall(owner.id_data).has_input('End Height')
    except Exception:
        return False


# ---- Doors and windows -----------------------------------------------------------
# Everything but the size is one dict of options on the cage. A write
# reads the whole dict (merged over the defaults, so options the dialog
# does not show keep their values), changes one key, stores it and
# rebuilds the geometry -- what the dialog does on every edit.

def _rebuild_door_window(obj):
    from ..product_libraries.common import door_window_geo
    if door_window_geo.stored_opts(obj) is not None:
        door_window_geo.build_geometry(obj)


def _dw_size(name):
    from . import prop_proxy
    from ..hb_types import GeoNodeObject

    def get(obj):
        try:
            return float(GeoNodeObject(obj).get_input(name))
        except Exception:
            return 0.0

    def set(obj, value):
        GeoNodeObject(obj).set_input(name, float(value))
        _rebuild_door_window(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0)


def _location(axis, rebuild=None):
    from . import prop_proxy

    def get(obj):
        return float(obj.location[axis])

    def set(obj, value):
        obj.location[axis] = float(value)
        if rebuild is not None:
            rebuild(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _op_items(op_id, prop):
    try:
        mod, name = op_id.split('.', 1)
        rna = getattr(getattr(bpy.ops, mod), name).get_rna_type()
        return [(i.identifier, i.name) for i in rna.properties[prop].enum_items]
    except Exception:
        return []


def _cast(kind, value):
    if kind == 'BOOLEAN':
        return bool(value)
    if kind == 'ENUM':
        return str(value) if value is not None else ''
    if kind == 'INT':
        return int(value or 0)
    return float(value or 0.0)


def _opt(key, kind='FLOAT', unit='NONE', items=(), **kw):
    """One key of the cage's options dict."""
    from . import prop_proxy
    from ..product_libraries.common import door_window_geo

    def get(obj):
        return _cast(kind, (door_window_geo.merged_opts(obj) or {}).get(key))

    def set(obj, value):
        opts = door_window_geo.merged_opts(obj)
        if opts is None:
            return
        opts[key] = value
        door_window_geo.set_opts(obj, opts)
        door_window_geo.build_geometry(obj)
    return prop_proxy.computed(get, set, type=kind, unit=unit, items=items, **kw)


def _has_opts(owner):
    from ..product_libraries.common import door_window_geo
    return door_window_geo.stored_opts(owner.id_data) is not None


def _style(owner):
    from ..product_libraries.common import door_window_geo
    opts = door_window_geo.stored_opts(owner.id_data)
    if opts is None:
        return "None (opening only)"
    return str(opts.get('style') or "Custom")


def _opt_is(key, *values):
    def test(owner):
        return _has_opts(owner) and getattr(owner, key) in values
    return test


# ---- Soffits, countertops, backsplashes -----------------------------------------

def _scale(axis):
    from . import prop_proxy

    def get(obj):
        return float(obj.scale[axis])

    def set(obj, value):
        obj.scale[axis] = max(float(value), 0.0254)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4, hard_min=0.0254)


def _countertop_key(key, minimum=None):
    from . import prop_proxy
    from ..product_libraries.common import countertop_common

    def get(obj):
        countertop_common.ensure_outline(obj)
        return float(obj.get(key, 0.0))

    def set(obj, value):
        countertop_common.ensure_outline(obj)
        if minimum is not None:
            value = max(float(value), minimum)
        obj[key] = float(value)
        countertop_common.rebuild(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _backsplash_height():
    """Height of the run's top over its base; setting it levels a
    stepped run at that height, as the size dialog does."""
    from . import prop_proxy
    from .. import backsplash

    def get(obj):
        _x0, _x1, z0, top = backsplash.bounds_of(obj)
        return float(top - z0)

    def set(obj, value):
        segs = backsplash.segments_of(obj)
        if not segs:
            return
        z0 = obj.get('bs_z0', 0.0)
        top = z0 + max(float(value), backsplash.MIN_HEIGHT)
        backsplash.set_segments(obj, [(a, b, top) for a, b, _t in segs])
        backsplash.rebuild(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


def _backsplash_thickness():
    from . import prop_proxy
    from .. import backsplash

    def get(obj):
        return float(obj.get('bs_thickness', backsplash.DEFAULT_THICKNESS))

    def set(obj, value):
        obj['bs_thickness'] = min(max(float(value), 0.001), 0.05)
        backsplash.rebuild(obj)
    return prop_proxy.computed(get, set, unit='LENGTH', precision=4)


# ---- Tambours -------------------------------------------------------------------
# Settings are custom properties read and written whole (tambour.read /
# write); the dialog applies them, then rebuilds the slats.

def _tambour(key, kind='FLOAT', unit='LENGTH', items=()):
    from . import prop_proxy
    from ..product_libraries.common import tambour

    def get(obj):
        return _cast(kind, tambour.read(obj).get(key))

    def set(obj, value):
        s = tambour.read(obj)
        s[key] = value
        if key == 'profile':
            # A new slat takes that slat's standard size, as in the dialog.
            s['width'], s['thickness'] = tambour.PROFILE_DEFAULTS[value]
        tambour.write(obj, s)
        tambour.rebuild(obj)
    return prop_proxy.computed(get, set, type=kind, unit=unit, items=items,
                               precision=4)


def _tambour_flipped():
    from . import prop_proxy
    from ..product_libraries.common import tambour

    def get(obj):
        s = tambour.read(obj)
        return s['face'] != tambour.default_face(s['sagitta'])

    def set(obj, value):
        s = tambour.read(obj)
        if bool(value) != (s['face'] != tambour.default_face(s['sagitta'])):
            s['face'] = -s['face']
            tambour.write(obj, s)
            tambour.rebuild(obj)
    return prop_proxy.computed(get, set, type='BOOLEAN')


def _slats(owner):
    from ..product_libraries.common import tambour
    try:
        return str(tambour.slat_count(tambour.read(owner.id_data)))
    except Exception:
        return None


# ---- Beams and posts -------------------------------------------------------------

def _apply_member(obj):
    """What the member dialog does after a change: a beam is laid between
    its ends again (its height follows its depth and position), anything
    else rebuilt, and the posts re-heighted to the beams above them."""
    from mathutils import Vector
    from .. import hb_house, hb_members
    from . import ops_members
    level = hb_house.get_level(obj.get(hb_house.LEVEL_KEY, ''))
    if obj.get('MEMBER_KIND') == 'BEAM' and level is not None:
        m = obj.matrix_world
        a = (m @ Vector((0.0, 0.0, 0.0))).to_2d()
        b = (m @ Vector((float(obj['MEMBER_LENGTH']), 0.0, 0.0))).to_2d()
        ops_members.set_beam_ends(obj, level, a, b)
    else:
        hb_members.rebuild(obj)
    if level is not None:
        hb_members.refresh_posts(bpy.context.scene, level)


def _member(key, kind='FLOAT', unit='LENGTH', items=(), **kw):
    from . import prop_proxy

    def get(obj):
        return _cast(kind, obj.get(key))

    def set(obj, value):
        obj[key] = value
        _apply_member(obj)
    return prop_proxy.computed(get, set, type=kind, unit=unit, items=items,
                               precision=4, **kw)


def _beam(owner):
    return owner.id_data.get('MEMBER_KIND') == 'BEAM'


def _plied(owner):
    return _beam(owner) and owner.material in ('LUMBER', 'LVL')


def _span_warning(context, owner):
    from .. import hb_members
    warn = hb_members.span_warning(owner.id_data)
    return [warn] if warn else []


# ---- Room trim -------------------------------------------------------------------

def _trim_room(obj):
    from .. import hb_house, hb_room_pick
    found = hb_room_pick.room_of(obj)
    if found is None:
        return None
    scene = hb_house.house_scene_of(bpy.context.scene)
    li, ri = found
    return scene.hb_house.levels[li].rooms[ri]


def _by_room(room):
    return room.id_data.hb_house.trim_by_room


def _own_trim(room):
    return _by_room(room) and not room.trim_auto


ROOM_TRIM_FIELDS = (
    ('notes', lambda c, r: [] if _by_room(r) else
     ["Trim is set for the whole house (House tab)."], "", {'owner': True}),
    ('bool', 'trim_auto', "Use House Default", {'when': _by_room}),
    ('bool', 'trim_base', "Baseboard", {'when': _own_trim}),
    ('distance', 'trim_base_height', "Base Height", {'when': _own_trim}),
    ('bool', 'trim_shoe', "Shoe", {'when': _own_trim}),
    ('distance', 'trim_chair_height', "Chair Rail (0 = None)", {'when': _own_trim}),
    ('bool', 'trim_crown', "Crown", {'when': _own_trim}),
)


# ---- Schemas and fields -----------------------------------------------------------

def _register_schemas():
    from . import prop_proxy as P
    P.register(APPLIANCE_SCHEMA, {
        'width': _appliance_size('Dim X'),
        'depth': _appliance_size('Dim Y'),
        'height': _appliance_size('Dim Z'),
    }, after=_after_appliance)
    P.register(WALL_SCHEMA, {
        'length': _wall_input('Length'),
        'height': _wall_input('Height'),
        'end_height': _wall_input('End Height'),
        'thickness': _wall_input('Thickness'),
    })
    P.register(DOOR_SCHEMA, {
        'width': _dw_size('Dim X'),
        'height': _dw_size('Dim Z'),
        'position': _location(0),
        'door_type': _opt('door_type', 'ENUM', items=_op_items(DOOR_OP, 'door_type')),
        'door_style': _opt('door_style', 'ENUM', items=_op_items(DOOR_OP, 'door_style')),
        'open_angle': _opt('open_angle', hard_min=0.0, hard_max=135.0),
        'panel_raise': _opt('panel_raise', 'BOOLEAN'),
        'include_knob': _opt('include_knob', 'BOOLEAN'),
        'include_interior_casing': _opt('include_interior_casing', 'BOOLEAN'),
        'include_exterior_casing': _opt('include_exterior_casing', 'BOOLEAN'),
        'casing_width': _opt('casing_width', unit='LENGTH', precision=4, hard_min=0.0),
        'threshold_height': _opt('threshold_height', unit='LENGTH', precision=4, hard_min=0.0),
        'sidelite_left': _opt('sidelite_left', unit='LENGTH', precision=4, hard_min=0.0),
        'sidelite_right': _opt('sidelite_right', unit='LENGTH', precision=4, hard_min=0.0),
        'transom_height': _opt('transom_height', unit='LENGTH', precision=4, hard_min=0.0),
    })
    P.register(WINDOW_SCHEMA, {
        'width': _dw_size('Dim X'),
        'height': _dw_size('Dim Z'),
        'position': _location(0),
        'height_from_floor': _location(2, rebuild=_rebuild_door_window),
        'window_type': _opt('window_type', 'ENUM', items=_op_items(WINDOW_OP, 'window_type')),
        'panes': _opt('panes', 'INT', hard_min=1, hard_max=3),
        'sash_split': _opt('sash_split', hard_min=0.25, hard_max=0.75),
        'grille_pattern': _opt('grille_pattern', 'ENUM', items=_op_items(WINDOW_OP, 'grille_pattern')),
        'grille_cols': _opt('grille_cols', 'INT', hard_min=1, hard_max=8),
        'grille_rows': _opt('grille_rows', 'INT', hard_min=1, hard_max=8),
        'include_interior_casing': _opt('include_interior_casing', 'BOOLEAN'),
        'include_exterior_casing': _opt('include_exterior_casing', 'BOOLEAN'),
        'casing_width': _opt('casing_width', unit='LENGTH', precision=4, hard_min=0.0),
        'include_sill': _opt('include_sill', 'BOOLEAN'),
        'include_stool': _opt('include_stool', 'BOOLEAN'),
        'shutter_style': _opt('shutter_style', 'ENUM', items=_op_items(WINDOW_OP, 'shutter_style')),
    })
    P.register(SOFFIT_SCHEMA, {
        'height': _scale(2),
        'depth': _scale(1),
    })
    P.register(COUNTERTOP_SCHEMA, {
        'thickness': _countertop_key('ct_thickness', minimum=0.003),
        'top_z': _countertop_key('ct_top_z'),
    })
    P.register(BACKSPLASH_SCHEMA, {
        'height': _backsplash_height(),
        'thickness': _backsplash_thickness(),
    })
    P.register(TAMBOUR_SCHEMA, {
        'height': _tambour('height'),
        'bottom': _location(2),
        'profile': _tambour('profile', 'ENUM', unit='NONE',
                            items=[('HALF_ROUND', "Half Round"), ('FLAT', "Flat")]),
        'width': _tambour('width'),
        'thickness': _tambour('thickness'),
        'gap': _tambour('gap'),
        'bow': _tambour('sagitta'),
        'flipped': _tambour_flipped(),
    })
    P.register(MEMBER_SCHEMA, {
        'material': _member('MEMBER_MATERIAL', 'ENUM', unit='NONE', items=(
            ('LUMBER', "Lumber"), ('LVL', "LVL"), ('GLULAM', "Glulam"), ('STEEL', "Steel"))),
        'plies': _member('MEMBER_PLIES', 'INT', unit='NONE', hard_min=1, hard_max=5),
        'depth': _member('MEMBER_D', hard_min=0.02),
        'width': _member('MEMBER_W', hard_min=0.02),
        'position': _member('MEMBER_POSITION', 'ENUM', unit='NONE', items=(
            ('DROPPED', "Dropped"), ('FLUSH', "Flush"))),
    })


SCHEMAS = (APPLIANCE_SCHEMA, WALL_SCHEMA, DOOR_SCHEMA, WINDOW_SCHEMA,
           SOFFIT_SCHEMA, COUNTERTOP_SCHEMA, BACKSPLASH_SCHEMA,
           TAMBOUR_SCHEMA, MEMBER_SCHEMA)

WALL_FIELDS = (
    ('distance', 'length', "Length"),
    ('distance', 'height', "Height"),
    ('distance', 'end_height', "End Height (0 = Flat)", {'when': _sloped}),
    ('distance', 'thickness', "Thickness"),
)

APPLIANCE_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
)


def _swing(owner):
    return owner.door_type == 'SWING'


def _panels(owner):
    return owner.door_style not in ('FLUSH', 'LOUVER', 'LITE_QUARTER', 'LITE_HALF',
                                    'LITE_34', 'LITE_FULL')


DOOR_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'position', "Position Along Wall"),
    ('value', _style, "Preset"),
    ('enum', 'door_type', "Door Type", {'when': _has_opts}),
    ('enum', 'door_style', "Panel Layout", {'when': _has_opts}),
    ('bool', 'panel_raise', "Raised Panels",
     {'when': lambda o: _has_opts(o) and _panels(o)}),
    ('number', 'open_angle', "Open Angle",
     {'when': lambda o: _has_opts(o) and _swing(o)}),
    ('number', 'open_angle', "Open %",
     {'when': lambda o: _has_opts(o) and not _swing(o)}),
    ('bool', 'include_knob', "Handle", {'when': _has_opts}),
    ('group', 'item_door_trim', "Trim & Unit", {'when': _has_opts, 'fields': (
        ('bool', 'include_interior_casing', "Interior Casing"),
        ('bool', 'include_exterior_casing', "Exterior Casing"),
        ('distance', 'casing_width', "Casing Width"),
        ('distance', 'threshold_height', "Threshold"),
        ('distance', 'sidelite_left', "Left Sidelite"),
        ('distance', 'sidelite_right', "Right Sidelite"),
        ('distance', 'transom_height', "Transom"),
    )}),
)

WINDOW_FIELDS = (
    ('distance', 'width', "Width"),
    ('distance', 'height', "Height"),
    ('distance', 'height_from_floor', "Above Floor"),
    ('distance', 'position', "Position Along Wall"),
    ('value', _style, "Preset"),
    ('enum', 'window_type', "Window Type", {'when': _has_opts}),
    ('number', 'panes', "Panes", {'when': _opt_is('window_type', 'CASEMENT', 'SLIDER')}),
    ('number', 'sash_split', "Sash Split", {'when': _opt_is('window_type', 'HUNG')}),
    ('enum', 'grille_pattern', "Grille", {'when': _has_opts}),
    ('number', 'grille_cols', "Grille Columns", {'when': _opt_is('grille_pattern', 'COLONIAL')}),
    ('number', 'grille_rows', "Grille Rows", {'when': _opt_is('grille_pattern', 'COLONIAL')}),
    ('group', 'item_window_trim', "Trim", {'when': _has_opts, 'fields': (
        ('bool', 'include_interior_casing', "Interior Casing"),
        ('bool', 'include_exterior_casing', "Exterior Casing"),
        ('distance', 'casing_width', "Casing Width"),
        ('bool', 'include_sill', "Sill"),
        ('bool', 'include_stool', "Stool"),
        ('enum', 'shutter_style', "Shutters"),
    )}),
)

SOFFIT_FIELDS = (
    ('distance', 'height', "Height"),
    ('distance', 'depth', "Depth"),
)

COUNTERTOP_FIELDS = (
    ('distance', 'thickness', "Thickness"),
    ('distance', 'top_z', "Underside Height"),
)

BACKSPLASH_FIELDS = (
    ('distance', 'height', "Height (Levels the Top)"),
    ('distance', 'thickness', "Thickness"),
)

TAMBOUR_FIELDS = (
    ('distance', 'height', "Height"),
    ('distance', 'bottom', "Bottom"),
    ('choices', 'profile', "Slat", {'cols': 2}),
    ('distance', 'width', "Slat Width"),
    ('distance', 'thickness', "Slat Thickness"),
    ('distance', 'gap', "Gap"),
    ('distance', 'bow', "Bow (0 = Straight)"),
    ('bool', 'flipped', "Flip Face Side"),
    ('value', _slats, "Slats"),
)

MEMBER_FIELDS = (
    ('enum', 'material', "Material"),
    ('number', 'plies', "Plies", {'when': _plied}),
    ('distance', 'depth', "Depth"),
    ('distance', 'width', "Width"),
    ('choices', 'position', "Position", {'cols': 2, 'when': _beam}),
    ('notes', _span_warning, "", {'owner': True}),
)


def _summary(*props):
    return lambda o: " x ".join(_dist(getattr(o, p)) for p in props)


def _member_label(obj):
    return str(obj.get('MEMBER_KIND') or "Member").title()


# kind -> (group key, label(obj), schema or None for the object's own
#          group, fields, summary)
_PAGES = {
    'wall': ('item_wall', lambda o: "Wall", WALL_SCHEMA, WALL_FIELDS,
             _summary('length', 'height')),
    'appliance': ('item_appliance', _appliance_label, APPLIANCE_SCHEMA,
                  APPLIANCE_FIELDS, _summary('width', 'height', 'depth')),
    'door': ('item_door', lambda o: "Open Doorway" if o.get('IS_OPEN_DOORWAY') else "Door",
             DOOR_SCHEMA, DOOR_FIELDS, _summary('width', 'height')),
    'window': ('item_window', lambda o: "Window", WINDOW_SCHEMA, WINDOW_FIELDS,
               _summary('width', 'height')),
    'soffit': ('item_soffit', lambda o: "Soffit", SOFFIT_SCHEMA, SOFFIT_FIELDS,
               _summary('height', 'depth')),
    'countertop': ('item_countertop', lambda o: "Countertop", COUNTERTOP_SCHEMA,
                   COUNTERTOP_FIELDS, _summary('thickness')),
    'backsplash': ('item_backsplash', lambda o: "Backsplash", BACKSPLASH_SCHEMA,
                   BACKSPLASH_FIELDS, _summary('height')),
    'tambour': ('item_tambour', lambda o: "Tambour", TAMBOUR_SCHEMA, TAMBOUR_FIELDS,
                _summary('height')),
    'member': ('item_member', _member_label, MEMBER_SCHEMA, MEMBER_FIELDS,
               _summary('width', 'depth')),
    'room_trim': ('item_room_trim', lambda o: "Room Trim", None, ROOM_TRIM_FIELDS,
                  None),
}


# ---- Wall commands ---------------------------------------------------------------
# The wall's right-click menu read straight onto the page came out as
# fourteen buttons two to a row, with odd ones left alone on a row. The
# page groups them instead: the elevation first, then what changes the
# room, what is shown, what goes on the wall, and the rare ones in a
# list beside Delete.

def _wall_act(label, op_id, kwargs=None, icon=None, weight=1.0):
    return (label, op_id, dict(kwargs or {}), None, weight, icon)


def _wall_more(context):
    return [("Wall Prompts", "home_builder_walls.wall_prompts", {'INVOKE': True}),
            ("Delete All Snap Lines", "hb_frameless.delete_all_snap_lines",
             {'INVOKE': True})]


def _wall_commands(obj):
    act = _wall_act
    return [
        ('actions', (act("Show Drawings", "home_builder.show_elevation",
                         {'wall_name': obj.name}, 'elevation'),)),
        ('gap', None),
        ('label', "Room"),
        ('actions', (act("Room Size", "home_builder_walls.change_room_size"),
                     act("Curve Wall", "home_builder_walls.curve_wall"),
                     act("Fix Corners", "home_builder_walls.update_wall_miters"))),
        ('label', "Visibility"),
        ('actions', (act("Hide", "home_builder_walls.hide_wall"),
                     act("Isolate", "home_builder_walls.isolate_selected_walls"),
                     act("Show All", "home_builder_walls.show_all_walls"))),
        ('label', "Add to Wall"),
        ('actions', (act("Cutter", "home_builder_walls.draw_wall_cutter"),
                     act("Soffit", "home_builder_walls.add_soffit"),
                     act("Snap Line", "hb_frameless.place_snap_line"))),
        ('gap', None),
        ('actions', (("More  ›", _wall_more, None, None, 1.0, None),
                     act("Delete Wall", "home_builder_walls.delete_wall"))),
    ]


# ---- The page --------------------------------------------------------------------

_opened = set()


def blocks(context, item):
    from . import options_panel, prop_proxy, generic_page
    kind, obj = item
    key, label_fn, schema, fields, summary = _PAGES[kind]
    if key not in _opened:
        _opened.add(key)
        if not options_panel.section_expanded(context, 'group:' + key):
            options_panel.toggle_section(context, 'group:' + key)
    owner = prop_proxy.owner(obj, schema) if schema else _trim_room(obj)
    options = {'icon': 'cab_parts', 'fields': fields}
    if summary is not None:
        options['summary'] = summary
    out = [('head', (obj.name, False, None))]
    out.extend(options_panel.field_blocks(context, (
        ('group', key, label_fn(obj), options),
    ), owner))
    if kind == 'wall':
        out.append(('gap', None))
        out.extend(_wall_commands(obj))
        return out
    menu = generic_page.menu_id(context.active_object) or generic_page.menu_id(obj)
    if menu:
        out.append(('gap', None))
        out.extend(generic_page.command_blocks(context, menu))
    return out


def register():
    from . import selected_tab
    _register_schemas()
    # Ahead of the cabinet libraries: a countertop or a door sits under
    # a cabinet or a wall, and is what was picked.
    selected_tab.register_source(SOURCE_KEY, find, blocks, first=True)


def unregister():
    from . import selected_tab, prop_proxy
    selected_tab.unregister_source(SOURCE_KEY)
    for key in SCHEMAS:
        prop_proxy.unregister(key)
