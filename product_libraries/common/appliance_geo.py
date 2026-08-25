"""3D geometry for placed appliances.

A placed appliance is a GeoNodeCage carrying Dim X / Dim Y / Dim Z and an
annotation label (see types_appliances.py). This module hangs a real,
render-visible model off that cage as child parts: case, doors, drawer
fronts, handles, cooktop and burners.

The model is DRIVEN, not regenerated: every part that spans the box takes
its size from a driver expression over the cage's dim_x / dim_y / dim_z,
the way wood_hoods builds hood parts. Resize the appliance -- from the
prompts dialog, from placement, from the Counter Depth toggle -- and the
model follows with no rebuild call anywhere. Only things that change the
NUMBER of parts (door configuration, burner count) need a rebuild, and
that happens in the prompts dialog.

Three tiers, and which one a dimension belongs in is the whole design:

    driven      case, doors, drawer fronts, handle bars -- anything that
                spans the box, sized by expression
    fixed shape, driven position
                knobs and burners: a 36" range must not get fatter knobs
                than a 30" one, but they still have to spread across the
                wider cooktop
    rebuild     door configuration, burner count, drawer count

Parts are plain GeoNodeCutparts, deliberately WITHOUT the CABINET_PART
flag that types_frameless.CabinetPart sets: an appliance shell is not a
manufactured part and must never reach a cut list, a DXF or a price.
Round details (burners, knobs) are plain meshes, positioned by drivers.

Options live on the cage as an id-property dict (GEO_OPTS_PROP);
build_geometry re-reads it and replaces the children, so rebuilds are
idempotent. A cage without the property builds nothing, so every
existing file stays the wireframe box it is today -- the model is opt-in
per appliance from the appliance right-click menu.

Panel-ready appliances build the case and the base grille only. Their
fronts come from appliance_panels.py, which builds real cabinet parts on
this same cage; drawing our own doors there would put two doors in the
same space.

2D NOTE: elevations and plans draw appliances from the cage, but real
geometry parented to the cage does flow into the drawing scenes and
picks up outlines there. That is the other reason the model is off by
default. Routing these parts out of the 2D passes -- or drawing them
deliberately -- is a follow-up on the drawings side.
"""

import math

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from ... import hb_utils
from ...hb_types import GeoNodeCutpart, GeoNodeObject
from ...units import inch


GEO_OPTS_PROP = "APPLIANCE_GEO_OPTS"
GEO_CHILD_FLAG = "IS_APPLIANCE_GEO"

SUPPORTED_TYPES = {'REFRIGERATOR', 'RANGE', 'DISHWASHER', 'UNDER_COUNTER'}

# Shared construction constants: the numbers that must NOT scale with
# the appliance. A wider fridge gets wider doors, not a thicker door or
# a fatter handle.
FRIDGE_DOOR_T = inch(2.0)
RANGE_DOOR_T = inch(1.75)
DISHWASHER_DOOR_T = inch(1.5)
UNDER_COUNTER_DOOR_T = inch(1.5)
# Glass-door stile / rail width, and how far the cabinet face sets back
# behind the door so there is a cavity to see shelves in.
UNDER_COUNTER_FRAME_W = inch(1.75)
UNDER_COUNTER_INTERIOR_D = inch(3.5)
LINER_T = inch(0.5)
COOKTOP_T = inch(0.5)
GAP = inch(0.125)
HANDLE_SECTION = inch(1.125)
HANDLE_STANDOFF = inch(1.25)
STANDOFF_SECTION = inch(0.75)
BACKGUARD_T = inch(1.0)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

MODEL_STYLE_ITEMS = [
    ('NONE', "None", "Wireframe cage only -- no 3D model"),
    ('MODELED', "Modeled", "Build the 3D appliance model"),
]

FINISH_ITEMS = [
    ('STAINLESS', "Stainless", "Brushed stainless steel"),
    ('BLACK_STAINLESS', "Black Stainless", "Dark brushed finish"),
    ('WHITE', "White", "White enamel"),
    ('BLACK', "Black", "Black enamel"),
]

HANDLE_ITEMS = [
    ('BAR', "Bar", "Bar handle standing off the door on two standoffs"),
    ('NONE', "None", "No handles -- integrated or push to open"),
]

FRIDGE_CONFIG_ITEMS = [
    ('FRENCH', "French Door", "Two doors over a freezer drawer"),
    ('SINGLE', "Single Door", "One door over a freezer drawer"),
    ('SIDE_BY_SIDE', "Side by Side", "Full-height freezer beside the fridge"),
    ('TOP_FREEZER', "Top Freezer", "Freezer door above the fridge door"),
]

UNDER_COUNTER_KIND_ITEMS = [
    ('BEVERAGE', "Beverage Center", "Shelves behind the door"),
    ('WINE', "Wine Fridge", "Wine rack slats behind the door"),
    ('ICE', "Ice Maker", "No interior behind the door"),
]

DOOR_STYLE_ITEMS = [
    ('SOLID', "Solid", "Solid door panel"),
    ('GLASS', "Glass", "Glass panel in a stile and rail frame, with the "
                       "interior visible behind it"),
]

CONTROL_STYLE_ITEMS = [
    ('TOP', "Top / Hidden", "Controls on the top edge of the door, so the "
                            "front is a clean panel"),
    ('FRONT', "Front", "Control panel across the front above the door"),
]

BURNER_STYLE_ITEMS = [
    ('GAS', "Gas", "Grates over sealed burners"),
    ('ELECTRIC', "Electric", "Coil elements"),
    ('INDUCTION', "Induction", "Flat glass top with element markings"),
]

# Every key that can appear in the options dict, with its default. The
# dict is stored as an id-property, so values stay plain floats, ints,
# bools and strings.
_COMMON_DEFAULTS = {
    'model_style': 'NONE',
    'finish': 'STAINLESS',
    'handle_style': 'BAR',
}

_FRIDGE_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'fridge_config': 'FRENCH',
    'freezer_height': inch(24.0),
    'freezer_drawers': 1,
    'freezer_fraction': 0.42,
    'grille_height': inch(4.0),
    'dispenser': False,
})

_RANGE_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'burner_style': 'GAS',
    'burner_count': 5,
    'oven_doors': 1,
    'control_height': inch(3.0),
    'knob_count': 5,
    'backguard_height': 0.0,
    'drawer_height': 0.0,
})

_DISHWASHER_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'control_style': 'TOP',
    'control_height': inch(2.5),
    'kick_height': inch(4.0),
})

_UNDER_COUNTER_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'uc_kind': 'BEVERAGE',
    'door_style': 'GLASS',
    'shelf_count': 3,
    'wine_rows': 5,
    'kick_height': inch(3.5),
})

_DEFAULTS_BY_TYPE = {
    'REFRIGERATOR': _FRIDGE_DEFAULTS,
    'RANGE': _RANGE_DEFAULTS,
    'DISHWASHER': _DISHWASHER_DEFAULTS,
    'UNDER_COUNTER': _UNDER_COUNTER_DEFAULTS,
}


def appliance_type(cage_obj):
    return cage_obj.get('APPLIANCE_TYPE') if cage_obj else None


def supports(cage_obj):
    """True when this appliance type has a model builder."""
    return appliance_type(cage_obj) in SUPPORTED_TYPES


def defaults_for(cage_obj):
    return dict(_DEFAULTS_BY_TYPE.get(appliance_type(cage_obj),
                                      _COMMON_DEFAULTS))


def stored_opts(cage_obj):
    """The options dict as stored, or None when this appliance has never
    been modeled -- legacy files, and every appliance until someone opens
    the dialog."""
    raw = cage_obj.get(GEO_OPTS_PROP)
    if raw is None:
        return None
    try:
        return {key: raw[key] for key in raw.keys()}
    except Exception:
        return None


def merged_opts(cage_obj):
    """Stored options over the type's defaults, so a dict written by an
    older version still resolves every key."""
    opts = defaults_for(cage_obj)
    stored = stored_opts(cage_obj)
    if stored:
        opts.update(stored)
    return opts


def set_opts(cage_obj, opts):
    cage_obj[GEO_OPTS_PROP] = dict(opts)


def clear_opts(cage_obj):
    if GEO_OPTS_PROP in cage_obj:
        del cage_obj[GEO_OPTS_PROP]


def is_panel_ready(cage_obj):
    """Panel Ready is a cage property owned by the appliance panels, not
    one of ours -- read it there so the two never disagree."""
    return bool(cage_obj.get('Panel Ready'))


# ---------------------------------------------------------------------------
# Expression helpers
#
# Sizes and positions arrive as either a number (fixed) or a driver
# expression string over dim_x / dim_y / dim_z (driven). These compose
# the two forms without the call sites having to care which they hold.
# ---------------------------------------------------------------------------

def _as_expr(value):
    return value if isinstance(value, str) else repr(float(value))


def _add(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return '(%s) + (%s)' % (_as_expr(a), _as_expr(b))
    return a + b


def _sub(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return '(%s) - (%s)' % (_as_expr(a), _as_expr(b))
    return a - b


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

_FINISH_COLORS = {
    'STAINLESS': ((0.62, 0.63, 0.65), 0.9, 0.32),
    'BLACK_STAINLESS': ((0.15, 0.15, 0.16), 0.8, 0.38),
    'WHITE': ((0.90, 0.90, 0.88), 0.0, 0.45),
    'BLACK': ((0.05, 0.05, 0.05), 0.0, 0.40),
}


def _material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = (*color, 1.0)
    return mat


def _finish_material(opts):
    finish = opts.get('finish', 'STAINLESS')
    color, metallic, roughness = _FINISH_COLORS.get(
        finish, _FINISH_COLORS['STAINLESS'])
    return _material('Appliance %s' % finish.title().replace('_', ' '),
                     color, metallic, roughness)


def _dark_material():
    """Grilles, control strips, cooktop glass, oven windows."""
    return _material('Appliance Dark', (0.045, 0.045, 0.05), 0.0, 0.30)


def _glass_material():
    """Door glass. Same recipe as the entry-door glazing, under its own
    name so the two can be tuned apart."""
    name = 'Appliance Glass'
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = _material(name, (0.60, 0.75, 0.80), 0.0, 0.05)
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = 0.25
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 1.0
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'BLENDED'
    elif hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    # Alpha in the solid-mode display color too, so it reads as glass in
    # the workbench viewport.
    mat.diffuse_color = (0.55, 0.70, 0.75, 0.25)
    return mat


def _metal_material():
    """Handles and burner hardware: metal whatever the body finish is."""
    return _material('Appliance Handle Metal', (0.66, 0.67, 0.69), 1.0, 0.28)


def _apply_material(part, mat):
    """Push one material into every surface and edge slot of a cutpart.
    Wrapped because the slots are geometry-node inputs, and a node group
    revision could rename them."""
    if mat is None:
        return
    for name in ("Top Surface", "Bottom Surface",
                 "Edge W1", "Edge W2", "Edge L1", "Edge L2"):
        try:
            part.set_input(name, mat)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Cage-local geometry helpers
#
# Cage space: x runs 0 -> dim_x left to right, y runs 0 (back, at the
# wall) -> -dim_y (front), z runs 0 (floor) -> dim_z. Cutpart orientation
# recipes match wood_hoods:
#
#   flat (no rotation)  Length -> +X, Width -> -Y (Mirror Y),
#                       Thickness -> +Z, or -Z with Mirror Z
#   front (rot x +90)   Length -> +X, Width -> +Z,
#                       Thickness -> +Y with Mirror Z (back into the
#                       box), -Y without it (proud of the face)
#   side (rot y -90)    Length -> +Z, Width -> -Y (Mirror Y),
#                       Thickness -> +X with Mirror Z, -X without
# ---------------------------------------------------------------------------

class _CageWrap(GeoNodeObject):
    """Wrap an existing object so the GeoNodeObject helpers (var_input,
    driver_location) can be used on it."""

    def __init__(self, obj):
        self.obj = obj


class _Cage:
    def __init__(self, cage_obj):
        self.obj = cage_obj
        wrap = _CageWrap(cage_obj)
        self.dim_x = wrap.var_input('Dim X', 'dim_x')
        self.dim_y = wrap.var_input('Dim Y', 'dim_y')
        self.dim_z = wrap.var_input('Dim Z', 'dim_z')

    def vars_for(self, value):
        """The driver variables an expression needs, picked from the
        names it mentions."""
        if not isinstance(value, str):
            return []
        return [var for name, var in (('dim_x', self.dim_x),
                                      ('dim_y', self.dim_y),
                                      ('dim_z', self.dim_z))
                if name in value]


def _link_like_cage(obj, cage_obj):
    """Link a new part wherever the cage lives, not into whatever
    collection happens to be active."""
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    colls = list(cage_obj.users_collection) or [bpy.context.scene.collection]
    for coll in colls:
        coll.objects.link(obj)


def _part(cg, name, mat=None):
    part = GeoNodeCutpart()
    part.create(name)
    part.obj.parent = cg.obj
    part.obj[GEO_CHILD_FLAG] = True
    # Right-clicking the model reaches the appliance menu: these are not
    # editable cabinet parts.
    if cg.obj.get('MENU_ID'):
        part.obj['MENU_ID'] = cg.obj['MENU_ID']
    _link_like_cage(part.obj, cg.obj)
    _apply_material(part, mat)
    return part


def _size(cg, part, input_name, value):
    if isinstance(value, str):
        part.driver_input(input_name, value, cg.vars_for(value))
    else:
        part.set_input(input_name, value)


def _place(cg, part, axis, value):
    if isinstance(value, str):
        part.driver_location(axis, value, cg.vars_for(value))
    else:
        setattr(part.obj.location, axis, value)


def _flat(cg, name, x, y, z, length, width, thickness, mat=None, down=False):
    """Horizontal slab: length across X, width back from y, thickness up
    from z (or down from it)."""
    part = _part(cg, name, mat)
    _place(cg, part, 'x', x)
    _place(cg, part, 'y', y)
    _place(cg, part, 'z', z)
    _size(cg, part, 'Length', length)
    _size(cg, part, 'Width', width)
    _size(cg, part, 'Thickness', thickness)
    part.set_input('Mirror Y', True)
    part.set_input('Mirror Z', down)
    return part


def _front(cg, name, x, z, width, height, thickness, mat=None,
           y=None, proud=False):
    """Front-facing panel. Sits at the cage's front plane unless ``y``
    says otherwise; ``proud`` stands the thickness in front of that plane
    instead of behind it."""
    part = _part(cg, name, mat)
    _place(cg, part, 'x', x)
    _place(cg, part, 'y', '-dim_y' if y is None else y)
    _place(cg, part, 'z', z)
    part.obj.rotation_euler.x = math.radians(90)
    _size(cg, part, 'Length', width)
    _size(cg, part, 'Width', height)
    _size(cg, part, 'Thickness', thickness)
    part.set_input('Mirror Z', not proud)
    return part


def _side(cg, name, x, y, z, height, depth, thickness, mat=None,
          plus_x=True):
    """Vertical panel in the YZ plane: height up Z from z, depth back
    from y, thickness across X (toward +X unless plus_x is False)."""
    part = _part(cg, name, mat)
    _place(cg, part, 'x', x)
    _place(cg, part, 'y', y)
    _place(cg, part, 'z', z)
    part.obj.rotation_euler.y = math.radians(-90)
    _size(cg, part, 'Length', height)
    _size(cg, part, 'Width', depth)
    _size(cg, part, 'Thickness', thickness)
    part.set_input('Mirror Y', True)
    part.set_input('Mirror Z', plus_x)
    return part


def _mesh_child(cg, name, verts, faces, mat=None):
    """A round detail as a plain mesh. Fixed shape -- only its position
    is driven."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    if mat is not None:
        mesh.materials.append(mat)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.parent = cg.obj
    obj[GEO_CHILD_FLAG] = True
    if cg.obj.get('MENU_ID'):
        obj['MENU_ID'] = cg.obj['MENU_ID']
    colls = list(cg.obj.users_collection) or [bpy.context.scene.collection]
    for coll in colls:
        coll.objects.link(obj)
    return obj


def _disc(cg, name, radius, height, mat=None, segments=16):
    """Capped cylinder standing on the object origin, built along +Z."""
    verts = []
    faces = []
    for level in (0.0, height):
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            verts.append((radius * math.cos(angle),
                          radius * math.sin(angle), level))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((i, j, j + segments, i + segments))
    faces.append(tuple(range(segments)))
    faces.append(tuple(reversed(range(segments, 2 * segments))))
    return _mesh_child(cg, name, verts, faces, mat)


def _bar_handle(cg, name, opts, mat, x, z, length, vertical):
    """Bar handle on two standoffs. ``x`` / ``z`` are the bar's near
    corner; it runs ``length`` up Z when vertical, across X when not.
    Either may be a number or a driver expression."""
    if opts.get('handle_style', 'BAR') == 'NONE':
        return
    y_bar = '-dim_y - %f' % HANDLE_STANDOFF
    if vertical:
        bar = _part(cg, "%s Bar" % name, mat)
        _place(cg, bar, 'x', x)
        _place(cg, bar, 'y', y_bar)
        _place(cg, bar, 'z', z)
        bar.obj.rotation_euler.y = math.radians(-90)
        _size(cg, bar, 'Length', length)
        bar.set_input('Width', HANDLE_SECTION)
        bar.set_input('Thickness', HANDLE_SECTION)
        bar.set_input('Mirror Y', True)
        bar.set_input('Mirror Z', True)
    else:
        _flat(cg, "%s Bar" % name, x, y_bar, z,
              length, HANDLE_SECTION, HANDLE_SECTION, mat)

    inset = inch(1.5)
    base = z if vertical else x
    near = _add(base, inset)
    far = _sub(_add(base, length), _add(inset, STANDOFF_SECTION))
    # The standoffs are thinner than the bar; center them under it.
    cross = _add(x if vertical else z,
                 (HANDLE_SECTION - STANDOFF_SECTION) * 0.5)
    for tag, along in (("Near", near), ("Far", far)):
        _flat(cg, "%s Standoff %s" % (name, tag),
              cross if vertical else along, '-dim_y',
              along if vertical else cross,
              STANDOFF_SECTION, HANDLE_STANDOFF, STANDOFF_SECTION, mat)


# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------

def _geo_children(cage_obj):
    return [c for c in cage_obj.children if c.get(GEO_CHILD_FLAG)]


def remove_geometry(cage_obj):
    """Drop every generated part. Leaves the cage, its label text and any
    appliance panels alone."""
    for child in _geo_children(cage_obj):
        data = child.data
        try:
            child.animation_data_clear()
        except Exception:
            pass
        bpy.data.objects.remove(child, do_unlink=True)
        if isinstance(data, bpy.types.Mesh) and data.users == 0:
            bpy.data.meshes.remove(data)


# ---------------------------------------------------------------------------
# Refrigerator
# ---------------------------------------------------------------------------

def _fridge_door(cg, opts, mat, metal, name, x, width, z, height, door_t,
                 handle_at_right=False, vertical_handle=True,
                 handle_at_bottom=False):
    _front(cg, name, x, z, width, height, door_t, mat)
    margin = inch(2.5)
    if vertical_handle:
        # The bar rides just inside the door's meeting edge.
        bar_x = (_sub(_add(x, width), _add(margin, HANDLE_SECTION))
                 if handle_at_right else _add(x, margin))
        _bar_handle(cg, "%s Handle" % name, opts, metal, bar_x,
                    _add(z, inch(6.0)), _sub(height, inch(12.0)), True)
    else:
        bar_z = (_add(z, inch(3.0)) if handle_at_bottom
                 else _sub(_add(z, height), inch(4.0)))
        _bar_handle(cg, "%s Handle" % name, opts, metal, inch(4.0), bar_z,
                    'dim_x - %f' % inch(8.0), False)


def _fridge_drawers(cg, opts, mat, metal, z0, height, door_t):
    """One or two freezer drawer fronts filling ``height`` from ``z0``."""
    count = max(1, int(opts.get('freezer_drawers', 1)))
    each = (height - (count - 1) * GAP) / count
    for i in range(count):
        z = z0 + i * (each + GAP)
        name = ("Freezer Drawer" if count == 1
                else "Freezer Drawer %d" % (i + 1))
        _front(cg, name, 0.0, z, 'dim_x', each, door_t, mat)
        _bar_handle(cg, "%s Handle" % name, opts, metal, inch(4.0),
                    z + each - inch(3.5), 'dim_x - %f' % inch(8.0), False)


def _build_refrigerator(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = FRIDGE_DOOR_T
    grille_h = float(opts.get('grille_height', inch(4.0)))
    panel_ready = is_panel_ready(cage_obj)

    # The case: everything behind the doors.
    _flat(cg, "Fridge Case", 0.0, 0.0, 0.0,
          'dim_x', 'dim_y - %f' % door_t, 'dim_z',
          dark if panel_ready else mat)

    if grille_h > 0.0:
        _front(cg, "Fridge Grille", 0.0, 0.0, 'dim_x', grille_h, door_t, dark)

    if panel_ready:
        # The fronts come from the appliance panels on this same cage.
        return

    config = opts.get('fridge_config', 'FRENCH')
    freezer_h = float(opts.get('freezer_height', inch(24.0)))
    base = grille_h

    if config == 'SIDE_BY_SIDE':
        frac = min(max(float(opts.get('freezer_fraction', 0.42)), 0.2), 0.8)
        height = 'dim_z - %f' % base
        _fridge_door(cg, opts, mat, metal, "Freezer Door", 0.0,
                     'dim_x * %f - %f' % (frac, GAP * 0.5),
                     base, height, door_t, handle_at_right=True)
        _fridge_door(cg, opts, mat, metal, "Fridge Door",
                     'dim_x * %f + %f' % (frac, GAP * 0.5),
                     'dim_x * %f - %f' % (1.0 - frac, GAP * 0.5),
                     base, height, door_t)
    elif config == 'TOP_FREEZER':
        _fridge_door(cg, opts, mat, metal, "Freezer Door", 0.0, 'dim_x',
                     'dim_z - %f' % freezer_h, freezer_h, door_t,
                     vertical_handle=False, handle_at_bottom=True)
        _fridge_door(cg, opts, mat, metal, "Fridge Door", 0.0, 'dim_x',
                     base, 'dim_z - %f' % (base + freezer_h + GAP), door_t,
                     vertical_handle=False)
    else:
        _fridge_drawers(cg, opts, mat, metal, base, freezer_h, door_t)
        door_z = base + freezer_h + GAP
        door_h = 'dim_z - %f' % door_z
        if config == 'SINGLE':
            _fridge_door(cg, opts, mat, metal, "Fridge Door", 0.0, 'dim_x',
                         door_z, door_h, door_t)
        else:
            half = '(dim_x - %f) * 0.5' % GAP
            _fridge_door(cg, opts, mat, metal, "Fridge Door L", 0.0, half,
                         door_z, door_h, door_t, handle_at_right=True)
            _fridge_door(cg, opts, mat, metal, "Fridge Door R",
                         'dim_x * 0.5 + %f' % (GAP * 0.5), half,
                         door_z, door_h, door_t)

    if opts.get('dispenser'):
        # Recessed water / ice panel, upper left. Fixed size: a
        # dispenser is a dispenser whatever the fridge measures.
        _front(cg, "Fridge Dispenser", inch(3.0),
               'dim_z - %f' % inch(26.0), inch(9.0), inch(13.0),
               inch(1.0), dark, y='-dim_y + %f' % inch(0.25))


# ---------------------------------------------------------------------------
# Range
# ---------------------------------------------------------------------------

# Burner centers as fractions of (dim_x, dim_y).
_BURNER_LAYOUTS = {
    4: ((0.27, 0.30), (0.73, 0.30), (0.27, 0.72), (0.73, 0.72)),
    5: ((0.24, 0.28), (0.76, 0.28), (0.50, 0.50),
        (0.24, 0.75), (0.76, 0.75)),
    6: ((0.19, 0.28), (0.50, 0.28), (0.81, 0.28),
        (0.19, 0.75), (0.50, 0.75), (0.81, 0.75)),
}

# (radius, height) discs stacked per burner style.
_BURNER_SHAPES = {
    'GAS': ((inch(4.0), inch(0.55)), (inch(1.6), inch(0.85))),
    'ELECTRIC': ((inch(3.4), inch(0.30)),),
    'INDUCTION': ((inch(3.6), inch(0.02)),),
}


def _build_burners(cg, opts, dark):
    style = opts.get('burner_style', 'GAS')
    count = int(opts.get('burner_count', 5))
    layout = _BURNER_LAYOUTS.get(count, _BURNER_LAYOUTS[5])
    shapes = _BURNER_SHAPES.get(style, _BURNER_SHAPES['GAS'])
    for i, (fx, fy) in enumerate(layout):
        for j, (radius, height) in enumerate(shapes):
            name = ("Burner %d" % (i + 1) if j == 0
                    else "Burner %d Cap" % (i + 1))
            wrap = _CageWrap(_disc(cg, name, radius, height, dark))
            # Fixed shape, driven position: burners spread with the
            # cooktop but never grow.
            wrap.driver_location('x', 'dim_x * %f' % fx, [cg.dim_x])
            wrap.driver_location('y', '-dim_y * %f' % fy, [cg.dim_y])
            wrap.driver_location('z', 'dim_z', [cg.dim_z])


def _build_knobs(cg, opts, metal, control_h):
    count = int(opts.get('knob_count', 0))
    if count <= 0 or control_h <= 0.0:
        return
    for i in range(count):
        frac = (i + 0.5) / count
        obj = _disc(cg, "Range Knob %d" % (i + 1), inch(0.75), inch(0.9),
                    metal)
        # The disc builds along +Z; stand it up so it points forward.
        obj.rotation_euler.x = math.radians(90)
        wrap = _CageWrap(obj)
        wrap.driver_location('x', 'dim_x * %f' % frac, [cg.dim_x])
        wrap.driver_location('y', '-dim_y', [cg.dim_y])
        wrap.driver_location(
            'z', 'dim_z - %f' % (COOKTOP_T + control_h * 0.5), [cg.dim_z])


def _oven_window(cg, name, z, height, dark):
    """The window in an oven door: a dark panel just proud of the door
    face, inset from its edges."""
    inset_x = inch(3.0)
    inset_z = inch(3.0)
    _front(cg, "%s Window" % name, inset_x, _add(z, inset_z),
           'dim_x - %f' % (2.0 * inset_x), _sub(height, 2.0 * inset_z),
           inch(0.125), dark, proud=True)


def _build_range(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = RANGE_DOOR_T
    control_h = float(opts.get('control_height', inch(3.0)))
    drawer_h = float(opts.get('drawer_height', 0.0))
    backguard_h = float(opts.get('backguard_height', 0.0))

    # Body, capped by the cooktop.
    _flat(cg, "Range Case", 0.0, 0.0, 0.0, 'dim_x',
          'dim_y - %f' % door_t, 'dim_z - %f' % COOKTOP_T, mat)
    _flat(cg, "Cooktop", 0.0, 0.0, 'dim_z', 'dim_x', 'dim_y', COOKTOP_T,
          dark if opts.get('burner_style') == 'INDUCTION' else mat,
          down=True)

    # Control strip across the front, under the cooktop.
    if control_h > 0.0:
        _front(cg, "Range Controls", 0.0,
               'dim_z - %f' % (COOKTOP_T + control_h), 'dim_x', control_h,
               door_t, dark)
    _build_knobs(cg, opts, metal, control_h)

    # Storage / warming drawer at the bottom, when there is one.
    oven_z = 0.0
    if drawer_h > 0.0:
        _front(cg, "Range Drawer", 0.0, 0.0, 'dim_x', drawer_h, door_t, mat)
        _bar_handle(cg, "Range Drawer Handle", opts, metal, inch(4.0),
                    drawer_h - inch(2.5), 'dim_x - %f' % inch(8.0), False)
        oven_z = drawer_h + GAP

    # Oven doors fill what is left between the drawer and the controls.
    doors = max(1, int(opts.get('oven_doors', 1)))
    span = 'dim_z - %f' % (COOKTOP_T + control_h + oven_z + GAP)
    if doors == 1:
        _front(cg, "Oven Door", 0.0, oven_z, 'dim_x', span, door_t, mat)
        _oven_window(cg, "Oven Door", oven_z, span, dark)
        _bar_handle(cg, "Oven Handle", opts, metal, inch(2.0),
                    _sub(_add(oven_z, span), inch(3.0)),
                    'dim_x - %f' % inch(4.0), False)
    else:
        each = '((%s) - %f) * 0.5' % (span, GAP)
        for i in range(doors):
            z = oven_z if i == 0 else _add(_add(oven_z, each), GAP)
            name = "Oven Door %d" % (i + 1)
            _front(cg, name, 0.0, z, 'dim_x', each, door_t, mat)
            _oven_window(cg, name, z, each, dark)
            _bar_handle(cg, "%s Handle" % name, opts, metal, inch(2.0),
                        _sub(_add(z, each), inch(3.0)),
                        'dim_x - %f' % inch(4.0), False)

    if backguard_h > 0.0:
        _front(cg, "Range Backguard", 0.0, 'dim_z', 'dim_x', backguard_h,
               BACKGUARD_T, mat, y=0.0, proud=True)

    _build_burners(cg, opts, dark)


# ---------------------------------------------------------------------------
# Dishwasher
# ---------------------------------------------------------------------------

def _build_dishwasher(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = DISHWASHER_DOOR_T
    kick_h = float(opts.get('kick_height', inch(4.0)))
    # Top controls sit on the door's top edge, so the front carries no
    # control panel at all and the door runs to the top of the box.
    front_controls = opts.get('control_style', 'TOP') == 'FRONT'
    control_h = (float(opts.get('control_height', inch(2.5)))
                 if front_controls else 0.0)
    panel_ready = is_panel_ready(cage_obj)

    _flat(cg, "Dishwasher Case", 0.0, 0.0, 0.0, 'dim_x',
          'dim_y - %f' % door_t, 'dim_z', dark if panel_ready else mat)

    # Lower access panel. It stays on a panel-ready machine: the
    # appliance panels cover the door opening, not the toe.
    if kick_h > 0.0:
        _front(cg, "Dishwasher Access Panel", 0.0, 0.0, 'dim_x', kick_h,
               door_t, dark if panel_ready else mat)

    if panel_ready:
        # The door front comes from the appliance panels on this cage.
        return

    if control_h > 0.0:
        _front(cg, "Dishwasher Controls", 0.0, 'dim_z - %f' % control_h,
               'dim_x', control_h, door_t, dark)

    door_z = kick_h + (GAP if kick_h > 0.0 else 0.0)
    door_h = 'dim_z - %f' % (door_z + control_h
                             + (GAP if control_h > 0.0 else 0.0))
    _front(cg, "Dishwasher Door", 0.0, door_z, 'dim_x', door_h, door_t, mat)
    _bar_handle(cg, "Dishwasher Handle", opts, metal, inch(2.0),
                _sub(_add(door_z, door_h), inch(3.0)),
                'dim_x - %f' % inch(4.0), False)


# ---------------------------------------------------------------------------
# Under-counter appliance (beverage center, wine fridge, ice maker)
# ---------------------------------------------------------------------------

def _under_counter_interior(cg, opts, kind, dark, z0, depth):
    """Shelves or wine slats in the cavity behind a glass door. Their
    spacing is driven, so they stay evenly divided as the box grows.

    Anchored at the BACK of the cavity: a part's width runs toward the
    front (Mirror Y), so starting one at the door face would build it out
    through the glass.
    """
    if kind == 'ICE':
        return
    if kind == 'WINE':
        count = max(1, int(opts.get('wine_rows', 5)))
        thickness = inch(0.375)
        name = "Wine Slat"
    else:
        count = max(1, int(opts.get('shelf_count', 3)))
        thickness = inch(0.5)
        name = "Shelf"
    y_back = '-dim_y + %f' % (UNDER_COUNTER_DOOR_T + depth)
    for i in range(count):
        fraction = (i + 1.0) / (count + 1.0)
        _flat(cg, "%s %d" % (name, i + 1), LINER_T, y_back,
              '%f + (dim_z - %f) * %f' % (z0, z0, fraction),
              'dim_x - %f' % (2.0 * LINER_T), depth - inch(0.25),
              thickness, dark)


def _under_counter_liner(cg, dark, z0, depth):
    """Line the cavity so the recess reads as a box rather than a hole
    with open sides. Anchored at the back of the cavity, for the reason
    in _under_counter_interior."""
    y_back = '-dim_y + %f' % (UNDER_COUNTER_DOOR_T + depth)
    height = 'dim_z - %f' % z0
    _side(cg, "Liner Left", 0.0, y_back, z0, height, depth, LINER_T, dark,
          plus_x=True)
    _side(cg, "Liner Right", 'dim_x', y_back, z0, height, depth, LINER_T,
          dark, plus_x=False)
    _flat(cg, "Liner Bottom", LINER_T, y_back, z0,
          'dim_x - %f' % (2.0 * LINER_T), depth, LINER_T, dark)
    _flat(cg, "Liner Top", LINER_T, y_back, 'dim_z',
          'dim_x - %f' % (2.0 * LINER_T), depth, LINER_T, dark, down=True)
    # The cabinet keeps its finish on the outside, so the cavity needs
    # its own dark back rather than showing the case face through the
    # glass.
    _front(cg, "Liner Back", 0.0, z0, 'dim_x', height, LINER_T, dark,
           y=y_back, proud=True)


def _glass_door(cg, opts, mat, glass, metal, z0, height, door_t):
    """Stile and rail frame with a glass panel, built on the door face."""
    frame = UNDER_COUNTER_FRAME_W
    _front(cg, "Door Stile L", 0.0, z0, frame, height, door_t, mat)
    _front(cg, "Door Stile R", 'dim_x - %f' % frame, z0, frame, height,
           door_t, mat)
    rail_w = 'dim_x - %f' % (2.0 * frame)
    _front(cg, "Door Rail Bottom", frame, z0, rail_w, frame, door_t, mat)
    _front(cg, "Door Rail Top", frame,
           _sub(_add(z0, height), frame), rail_w, frame, door_t, mat)
    # The pane sits in the middle of the frame's thickness.
    _front(cg, "Door Glass", frame, _add(z0, frame), rail_w,
           _sub(height, 2.0 * frame), inch(0.25), glass,
           y='-dim_y + %f' % (door_t * 0.5))


def _build_under_counter(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = UNDER_COUNTER_DOOR_T
    kick_h = float(opts.get('kick_height', inch(3.5)))
    kind = opts.get('uc_kind', 'BEVERAGE')
    panel_ready = is_panel_ready(cage_obj)
    glass_door = (opts.get('door_style', 'GLASS') == 'GLASS'
                  and not panel_ready)
    # A solid door hides everything behind it, so only a glass one pays
    # for a cavity, a liner and shelves.
    interior = UNDER_COUNTER_INTERIOR_D if glass_door else 0.0

    _flat(cg, "Under Counter Case", 0.0, 0.0, 0.0, 'dim_x',
          'dim_y - %f' % (door_t + interior), 'dim_z',
          dark if panel_ready else mat)

    if kick_h > 0.0:
        _front(cg, "Under Counter Grille", 0.0, 0.0, 'dim_x', kick_h,
               door_t, dark)

    if panel_ready:
        # The door front comes from the appliance panels on this cage.
        return

    door_z = kick_h + (GAP if kick_h > 0.0 else 0.0)
    door_h = 'dim_z - %f' % door_z

    if glass_door:
        _under_counter_liner(cg, dark, door_z, interior)
        _under_counter_interior(cg, opts, kind, dark, door_z, interior)
        _glass_door(cg, opts, mat, _glass_material(), metal, door_z, door_h,
                    door_t)
    else:
        _front(cg, "Under Counter Door", 0.0, door_z, 'dim_x', door_h,
               door_t, mat)

    # Vertical bar handle inside the right-hand edge, the way an
    # under-counter unit is normally pulled. On a glass door it centers
    # on the stile -- mounting it over the pane would be nonsense.
    if glass_door:
        handle_inset = (UNDER_COUNTER_FRAME_W + HANDLE_SECTION) * 0.5
    else:
        handle_inset = inch(2.5) + HANDLE_SECTION
    _bar_handle(cg, "Under Counter Handle", opts, metal,
                'dim_x - %f' % handle_inset,
                _add(door_z, inch(4.0)), _sub(door_h, inch(8.0)), True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_BUILDERS = {
    'REFRIGERATOR': _build_refrigerator,
    'RANGE': _build_range,
    'DISHWASHER': _build_dishwasher,
    'UNDER_COUNTER': _build_under_counter,
}


def build_geometry(cage_obj):
    """Wipe and rebuild the appliance model from the options on the cage.

    Idempotent, so it is safe to call from the prompts dialog, a
    duplicate, or a style change. No options, an unsupported appliance
    type, or a style of NONE all leave the appliance a bare cage.
    """
    if cage_obj is None:
        return False
    remove_geometry(cage_obj)
    if not supports(cage_obj) or stored_opts(cage_obj) is None:
        return False
    opts = merged_opts(cage_obj)
    if opts.get('model_style', 'NONE') == 'NONE':
        return False
    builder = _BUILDERS.get(appliance_type(cage_obj))
    if builder is None:
        return False
    builder(cage_obj, opts)
    return True


def rebuild_all(scene=None):
    """Rebuild every modeled appliance in a scene, for callers that
    change something global rather than one appliance."""
    scene = scene or bpy.context.scene
    return sum(1 for obj in list(scene.objects)
               if obj.get('IS_APPLIANCE')
               and stored_opts(obj) is not None
               and build_geometry(obj))


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

class HOME_BUILDER_OT_appliance_prompts(bpy.types.Operator):
    """Edit the size and the 3D model of the selected appliance"""

    bl_idname = "home_builder.appliance_prompts"
    bl_label = "Appliance Prompts"
    bl_description = ("Edit the size of the selected appliance and the "
                      "options of its 3D model")
    bl_options = {'REGISTER', 'UNDO'}

    appliance_width: FloatProperty(
        name="Width", unit='LENGTH', precision=5)  # type: ignore
    appliance_height: FloatProperty(
        name="Height", unit='LENGTH', precision=5)  # type: ignore
    appliance_depth: FloatProperty(
        name="Depth", unit='LENGTH', precision=5)  # type: ignore

    model_style: EnumProperty(name="Model", items=MODEL_STYLE_ITEMS,
                              default='NONE')  # type: ignore
    finish: EnumProperty(name="Finish", items=FINISH_ITEMS,
                         default='STAINLESS')  # type: ignore
    handle_style: EnumProperty(name="Handles", items=HANDLE_ITEMS,
                               default='BAR')  # type: ignore

    # Refrigerator
    fridge_config: EnumProperty(name="Configuration",
                                items=FRIDGE_CONFIG_ITEMS,
                                default='FRENCH')  # type: ignore
    freezer_height: FloatProperty(
        name="Freezer Height", unit='LENGTH', precision=5, min=0.0,
        description="Height of the freezer zone")  # type: ignore
    freezer_drawers: IntProperty(
        name="Freezer Drawers", min=1, max=2,
        description="Drawer fronts in the freezer zone")  # type: ignore
    freezer_fraction: FloatProperty(
        name="Freezer Share", min=0.2, max=0.8, precision=2,
        description="Share of the width the freezer takes on a side by "
                    "side")  # type: ignore
    grille_height: FloatProperty(
        name="Base Grille", unit='LENGTH', precision=5, min=0.0,
        description="Height of the grille below the doors")  # type: ignore
    dispenser: BoolProperty(
        name="Water / Ice Dispenser",
        description="Recessed dispenser panel in the door")  # type: ignore

    # Range
    # Under counter
    uc_kind: EnumProperty(name="Type", items=UNDER_COUNTER_KIND_ITEMS,
                          default='BEVERAGE')  # type: ignore
    door_style: EnumProperty(name="Door", items=DOOR_STYLE_ITEMS,
                             default='GLASS')  # type: ignore
    shelf_count: IntProperty(
        name="Shelves", min=1, max=8,
        description="Shelves visible behind a glass door")  # type: ignore
    wine_rows: IntProperty(
        name="Rack Rows", min=1, max=12,
        description="Wine rack slats visible behind a glass door")  # type: ignore

    # Dishwasher
    control_style: EnumProperty(name="Controls", items=CONTROL_STYLE_ITEMS,
                                default='TOP')  # type: ignore
    kick_height: FloatProperty(
        name="Access Panel", unit='LENGTH', precision=5, min=0.0,
        description="Height of the panel below the door")  # type: ignore

    # Range
    burner_style: EnumProperty(name="Cooktop", items=BURNER_STYLE_ITEMS,
                               default='GAS')  # type: ignore
    burner_count: IntProperty(name="Burners", min=4, max=6)  # type: ignore
    oven_doors: IntProperty(
        name="Oven Doors", min=1, max=2,
        description="1 for a single oven, 2 for a stacked double")  # type: ignore
    control_height: FloatProperty(
        name="Control Panel", unit='LENGTH', precision=5, min=0.0,
        description="Height of the control strip below the cooktop")  # type: ignore
    knob_count: IntProperty(
        name="Knobs", min=0, max=8,
        description="Knobs on the control strip, 0 for touch "
                    "controls")  # type: ignore
    backguard_height: FloatProperty(
        name="Backguard", unit='LENGTH', precision=5, min=0.0,
        description="Riser above the cooktop at the back, 0 for a "
                    "slide in")  # type: ignore
    drawer_height: FloatProperty(
        name="Bottom Drawer", unit='LENGTH', precision=5, min=0.0,
        description="Storage or warming drawer below the oven, 0 for "
                    "none")  # type: ignore

    appliance = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is None:
            return False
        cage = hb_utils.get_appliance_bp(obj)
        return cage is not None and supports(cage)

    def invoke(self, context, event):
        self.appliance = hb_utils.get_appliance_bp(context.object)
        cage = _CageWrap(self.appliance)
        self.appliance_width = cage.get_input('Dim X')
        self.appliance_height = cage.get_input('Dim Z')
        self.appliance_depth = cage.get_input('Dim Y')
        for key, value in merged_opts(self.appliance).items():
            if hasattr(self, key):
                try:
                    setattr(self, key, value)
                except (TypeError, ValueError):
                    pass
        self._applied_key = None
        return context.window_manager.invoke_props_dialog(self, width=340)

    def _opts_dict(self):
        keys = _DEFAULTS_BY_TYPE.get(appliance_type(self.appliance),
                                     _COMMON_DEFAULTS).keys()
        return {key: getattr(self, key) for key in keys if hasattr(self, key)}

    def _apply(self):
        # Size is pushed on every interaction: the parts are driven, so
        # this restretches the model without touching an object.
        cage = _CageWrap(self.appliance)
        cage.set_input('Dim X', self.appliance_width)
        cage.set_input('Dim Z', self.appliance_height)
        cage.set_input('Dim Y', self.appliance_depth)

        # The model itself is another matter. check() fires on every
        # dialog interaction, and each rebuild removes and recreates part
        # objects; doing that on every mouse move destabilizes the draw
        # cache -- the same crash wood_hoods guards against -- so only
        # rebuild when the options actually changed.
        opts = self._opts_dict()
        key = repr(sorted(opts.items()))
        if getattr(self, '_applied_key', None) == key:
            return
        self._applied_key = key
        set_opts(self.appliance, opts)
        build_geometry(self.appliance)
        # The rebuild just created and removed objects mid-dialog; force
        # the depsgraph current before the next viewport draw.
        bpy.context.view_layer.update()

    def check(self, context):
        self._apply()
        return True

    def execute(self, context):
        self._apply()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        appl = appliance_type(self.appliance)

        box = layout.box()
        col = box.column(align=True)
        for label, prop in (("Width:", 'appliance_width'),
                            ("Height:", 'appliance_height'),
                            ("Depth:", 'appliance_depth')):
            row = col.row(align=True)
            row.label(text=label)
            row.prop(self, prop, text="")

        box = layout.box()
        col = box.column(align=True)
        col.prop(self, 'model_style')
        if self.model_style == 'NONE':
            col.label(text="The appliance stays a wireframe box.",
                      icon='INFO')
            return
        col.prop(self, 'finish')
        col.prop(self, 'handle_style')

        if is_panel_ready(self.appliance):
            box = layout.box()
            box.label(text="Panel Ready: the fronts come from the "
                           "appliance panels.", icon='INFO')
            return

        box = layout.box()
        col = box.column(align=True)
        if appl == 'REFRIGERATOR':
            col.prop(self, 'fridge_config')
            if self.fridge_config == 'SIDE_BY_SIDE':
                col.prop(self, 'freezer_fraction')
            else:
                col.prop(self, 'freezer_height')
                if self.fridge_config in {'FRENCH', 'SINGLE'}:
                    col.prop(self, 'freezer_drawers')
            col.prop(self, 'grille_height')
            col.prop(self, 'dispenser')
        elif appl == 'UNDER_COUNTER':
            col.prop(self, 'uc_kind')
            col.prop(self, 'door_style')
            if self.door_style == 'GLASS':
                if self.uc_kind == 'WINE':
                    col.prop(self, 'wine_rows')
                elif self.uc_kind == 'BEVERAGE':
                    col.prop(self, 'shelf_count')
            col.prop(self, 'kick_height')
        elif appl == 'DISHWASHER':
            col.prop(self, 'control_style')
            if self.control_style == 'FRONT':
                col.prop(self, 'control_height')
            col.prop(self, 'kick_height')
        elif appl == 'RANGE':
            col.prop(self, 'burner_style')
            col.prop(self, 'burner_count')
            col.separator()
            col.prop(self, 'oven_doors')
            col.prop(self, 'drawer_height')
            col.separator()
            col.prop(self, 'control_height')
            col.prop(self, 'knob_count')
            col.prop(self, 'backguard_height')


_CLASSES = (
    HOME_BUILDER_OT_appliance_prompts,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
