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

import bmesh
import bpy
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty

from ... import hb_utils
from ...hb_types import GeoNodeCutpart, GeoNodeObject
from ...units import inch


GEO_OPTS_PROP = "APPLIANCE_GEO_OPTS"
GEO_CHILD_FLAG = "IS_APPLIANCE_GEO"
# Whether the model standing on the cage was built panelled -- that is,
# without the appliance's own doors and handles. The panels read it to
# tell when the model no longer matches them and has to be built again;
# without it, panels added from anywhere but the prompts dialog left the
# factory fronts standing behind the cabinet ones.
MODEL_PANEL_READY_FLAG = "APPLIANCE_MODEL_PANEL_READY"

SUPPORTED_TYPES = {'REFRIGERATOR', 'RANGE', 'DISHWASHER', 'UNDER_COUNTER',
                   'HOOD', 'SINK', 'WALL_OVEN', 'MICROWAVE', 'COOKTOP'}

# Appliances that can wear cabinet door panels instead of their own
# front. Matches what the appliance-panels product accepts.
PANEL_TYPES = {'REFRIGERATOR', 'DISHWASHER', 'UNDER_COUNTER'}

# Shared construction constants: the numbers that must NOT scale with
# the appliance. A wider fridge gets wider doors, not a thicker door or
# a fatter handle.
FRIDGE_DOOR_T = inch(2.0)
FRIDGE_KICK_H = inch(2.5)     # under the doors when the grille is on top
FRIDGE_REVEAL_T = inch(0.125) # the dark face the door gaps open onto
RANGE_DOOR_T = inch(1.75)
DISHWASHER_DOOR_T = inch(1.5)
UNDER_COUNTER_DOOR_T = inch(1.5)
# Glass-door stile / rail width, and how far the cabinet face sets back
# behind the door so there is a cavity to see shelves in.
UNDER_COUNTER_FRAME_W = inch(1.75)
UNDER_COUNTER_INTERIOR_D = inch(3.5)
LINER_T = inch(0.5)
COOKTOP_T = inch(0.5)
LIP_W = inch(0.5)             # the cooktop tray's lip, in plan
LIP_RISE = inch(0.375)        # how far it stands above the cooktop
LIP_PROUD = inch(0.5)         # how far the front edge rolls out
SMALL_OVEN_EVEN_AT = inch(30.0)   # both ovens this wide: split evenly
COOKTOP_PLATE_T = inch(0.5)       # the top that sits on the counter
COOKTOP_LIP = inch(0.75)          # how far it overhangs the body below
COOKTOP_DROP = inch(4.0)          # the body below the counter, in a cabinet
OVEN_CONTROL_H = inch(4.0)        # a wall oven's control band
MICRO_TRIM = inch(1.25)           # a built-in microwave's trim kit frame
MICRO_PANEL_W = inch(6.0)         # its control panel, right of the door
MICRO_RECESS = inch(0.5)          # the face sits this far behind the trim
SINK_WALL_T = inch(0.0625)
SINK_BACK_DECK = inch(2.5)        # rim behind the bowls, where the faucet stands
SINK_FRONT_RIM = inch(1.25)
SINK_SIDE_RIM = inch(1.25)
SINK_DIVIDER = inch(1.25)         # between the bowls of a double
SINK_APRON_T = inch(3.0)          # a farmhouse front: through the cabinet
                                  # front and an inch proud of the frame
SINK_H = inch(10.0)               # a sink cage's height in a cabinet
SINK_SIDE_MARGIN = inch(1.5)      # cabinet inside face to the sink
SINK_END_GAP = inch(0.5)          # front and back
SINK_SEAT = inch(1.0 / 32.0)      # a hair between the sink and the counter,
                                  # so no two faces share a plane
SINK_HOLE_CLEAR = inch(0.125)     # the countertop hole past the bowl walls
HOOD_PANEL_T = inch(1.0)          # a box canopy's walls
HOOD_LIP_H = inch(2.5)            # the vertical band under a pyramid canopy
HOOD_DUCT_W = inch(12.0)          # a chimney's duct cover, in plan
HOOD_DUCT_D = inch(10.0)
GAP = inch(0.125)
HANDLE_SECTION = inch(1.125)
HANDLE_STANDOFF = inch(1.25)
STANDOFF_SECTION = inch(0.75)
BACKGUARD_T = inch(1.0)
# Gas grates: continuous castings, one per column of burners, running
# the cooktop's depth. Side runners stand on the glass; the rails and
# the arms out to each burner's ring are lifted off it.
GRATE_RAIL = inch(0.5)
GRATE_GAP = inch(0.15)        # between neighbouring grates
GRATE_RING_R = inch(2.9)
GRATE_LIFT = inch(0.35)
GRATE_BAR_H = inch(0.45)
GRATE_BACK = 0.12             # fractions of the cooktop depth
GRATE_FRONT = 0.90
KNOB_BEZEL_R = inch(1.125)
DISPLAY_W = inch(5.0)
DISPLAY_H = inch(1.5)
KNOB_R = inch(0.875)
KNOB_DEPTH = inch(1.25)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

FRONT_STYLE_ITEMS = [
    ('APPLIANCE', "Appliance", "The appliance's own front, in its finish"),
    ('CABINET', "Cabinet Door Style",
     "Panel ready: door-style panels in the room's cabinet style, built by "
     "the appliance panels"),
]

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

SINK_MOUNT_ITEMS = [
    ('UNDERMOUNT', "Undermount", "Rim under the countertop; the counter "
                                 "edge shows around the bowl"),
    ('DROP_IN', "Drop-In", "Rim on top of the countertop as a flange "
                           "around the bowl"),
]

DRAIN_SIDE_ITEMS = [
    ('CENTER', "Center", "Drain in the middle of the bowl"),
    ('LEFT', "Left", "Drain toward the left end"),
    ('RIGHT', "Right", "Drain toward the right end"),
]

SINK_STYLE_ITEMS = [
    ('SINGLE', "Single Bowl", "One bowl the width of the sink"),
    ('WORKSTATION', "Workstation", "One long bowl with two ledges along "
                                   "the front and back for a culinary kit"),
    ('DOUBLE', "Double Bowl", "Two equal bowls either side of a divider"),
    ('FARMHOUSE', "Farmhouse", "One bowl behind an apron front standing "
                               "proud of the cabinet"),
]

HOOD_STYLE_ITEMS = [
    ('PRO', "Professional", "Box canopy under a full-width duct cover"),
    ('CHIMNEY', "Wall Chimney", "Pyramid canopy against the wall under a "
                                "narrow duct cover"),
    ('ISLAND', "Island", "Pyramid canopy hung from the ceiling, finished "
                         "on all four sides"),
    ('UNDER_CABINET', "Under Cabinet", "Slim canopy under a wall cabinet, "
                                       "no duct cover"),
]

GRILLE_POSITION_ITEMS = [
    ('TOP', "Top", "Louvered grille above the doors, as on a built-in"),
    ('BOTTOM', "Bottom", "Louvered grille below the doors, as on a "
                         "freestanding unit"),
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
    'grille_position': 'TOP',
    'dispenser': False,
})

_RANGE_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'burner_style': 'GAS',
    'burner_count': 5,
    'oven_doors': 1,
    'control_height': inch(3.0),
    'knob_count': 5,
    'backguard_height': 0.0,
    'drawer_height': inch(6.0),
    'small_oven_width': inch(18.0),
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

_HOOD_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'hood_style': 'CHIMNEY',
    'canopy_height': 0.0,       # 0: the style's own height
    'baffles': True,
    'lamps': True,
})

# Canopy heights per style, for a canopy_height of 0.
_HOOD_CANOPY_H = {
    'PRO': inch(18.0),
    'CHIMNEY': inch(10.0),
    'ISLAND': inch(10.0),
    'UNDER_CABINET': inch(6.0),
}

_SINK_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'sink_style': 'SINGLE',
    'drain_side': 'CENTER',
    'mount': 'UNDERMOUNT',
    'faucet': True,
    'counter_thickness': inch(1.5),   # the countertop below the cage top
    'bowl_depth': 0.0,                # 0: the cage's own depth
})

_OVEN_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'knobs': True,
})

_MICROWAVE_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'trim_kit': False,
    'handle_style': 'NONE',
})

_COOKTOP_DEFAULTS = dict(_COMMON_DEFAULTS, **{
    'burner_style': 'GAS',
    'burner_count': 5,
    'knob_count': 5,
    'counter_thickness': inch(1.5),
})

_DEFAULTS_BY_TYPE = {
    'SINK': _SINK_DEFAULTS,
    'COOKTOP': _COOKTOP_DEFAULTS,
    'WALL_OVEN': _OVEN_DEFAULTS,
    'MICROWAVE': _MICROWAVE_DEFAULTS,
    'HOOD': _HOOD_DEFAULTS,
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


def _panels_module():
    """Lazy, guarded import: appliances live in the shared 'common'
    library and must not hard-depend on the face-frame product."""
    try:
        from ..face_frame import appliance_panels
        return appliance_panels
    except Exception:
        return None


def supports_panels(cage_obj):
    """True when this appliance can carry cabinet door panels."""
    return (appliance_type(cage_obj) in PANEL_TYPES
            and _panels_module() is not None)


# The model's own door configuration, mapped to the panel layout that
# matches it -- switching a french-door fridge to cabinet fronts should
# seed french-door panels, not a single slab.
_PANEL_CONFIG_FOR_FRIDGE = {
    'FRENCH': 'FRENCH_DOOR_BOTTOM_FREEZER',
    'SINGLE': 'BOTTOM_FREEZER',
    'SIDE_BY_SIDE': 'FRENCH_DOOR',
    'TOP_FREEZER': 'TOP_FREEZER',
}


def _panel_config_for(cage_obj, panels):
    """The panel preset to seed, taken from the model's own layout where
    the two line up, else the first preset this appliance offers."""
    opts = merged_opts(cage_obj)
    appl = appliance_type(cage_obj)
    if appl == 'REFRIGERATOR':
        config = opts.get('fridge_config', 'FRENCH')
        if (config == 'SINGLE'
                and int(opts.get('freezer_drawers', 1)) > 1):
            return 'BOTTOM_FREEZER_2DRAWER'
        return _PANEL_CONFIG_FOR_FRIDGE.get(config, 'SINGLE')
    items = panels.CONFIG_ITEMS.get(appl, panels.DEFAULT_CONFIG_ITEMS)
    return items[0][0] if items else 'SINGLE'


def set_front_style(cage_obj, style):
    """Switch an appliance between its own front and cabinet door panels.

    Turning panels on seeds a layout only the first time; the section
    model survives being turned off, so toggling back and forth keeps
    whatever layout was set up. Returns True when the appliance ended up
    panelled.
    """
    panels = _panels_module()
    if panels is None or appliance_type(cage_obj) not in PANEL_TYPES:
        return False
    if style != 'CABINET':
        panels.remove(cage_obj)
        return False
    props = cage_obj.appliance_panels
    panels.seed_from_legacy(cage_obj)
    if not props.sections:
        config = (props.config or cage_obj.get('APPLIANCE_PANEL_CONFIG')
                  or _panel_config_for(cage_obj, panels))
        panels.seed_preset(cage_obj, config, keep_options=False)
    # rebuild stamps the cage, Panel Ready included.
    panels.rebuild(cage_obj)
    return True


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


def _iron_material():
    """Cast-iron grates: black and dead flat."""
    return _material('Appliance Cast Iron', (0.02, 0.02, 0.022), 0.0, 0.85)


def _brass_material():
    """Gas burner heads and caps."""
    return _material('Appliance Brass', (0.62, 0.46, 0.22), 1.0, 0.40)


def _coil_material():
    """Electric elements: dark metal, not chrome."""
    return _material('Appliance Coil', (0.10, 0.10, 0.10), 0.6, 0.55)


def _print_material():
    """The rings printed on induction glass."""
    return _material('Appliance Print', (0.78, 0.78, 0.78), 0.0, 0.5)


def _display_material():
    """The lit digits of a control panel readout. Emissive for renders,
    and a bright solid-mode colour so it reads in the workbench too."""
    name = 'Appliance Display'
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    color = (0.25, 0.65, 1.0)
    mat = _material(name, color, 0.0, 0.4)
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = 4.0
    return mat


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


def _mesh_child(cg, name, verts, faces, mat=None, extra_mats=(),
                face_mats=None, smooth_faces=()):
    """A round detail as a plain mesh. Fixed shape -- only its position
    is driven. ``face_mats`` maps a face index to a slot in
    (mat, *extra_mats); ``smooth_faces`` are shaded smooth."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    for slot in (mat, *extra_mats):
        if slot is not None:
            mesh.materials.append(slot)
    mesh.validate()
    for index, slot in (face_mats or {}).items():
        mesh.polygons[index].material_index = slot
    for index in smooth_faces:
        mesh.polygons[index].use_smooth = True
    mesh.update()
    obj = hb_utils.new_object(name, mesh)
    obj.parent = cg.obj
    obj[GEO_CHILD_FLAG] = True
    if cg.obj.get('MENU_ID'):
        obj['MENU_ID'] = cg.obj['MENU_ID']
    colls = list(cg.obj.users_collection) or [bpy.context.scene.collection]
    for coll in colls:
        coll.objects.link(obj)
    return obj


def _revolve(verts, faces, profile, segments=32, caps=True):
    """Append a surface of revolution about +Z: each (r, z) point of the
    profile becomes a ring, consecutive rings a band of quads, and the
    two end rings flat caps. Returns (side faces, cap faces) as index
    lists so the caller can shade and paint them. A closed profile (last
    point repeating the first) wants ``caps=False``."""
    base = len(verts)
    for radius, z in profile:
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            verts.append((radius * math.cos(angle),
                          radius * math.sin(angle), z))
    side = []
    for ring in range(len(profile) - 1):
        r0 = base + ring * segments
        r1 = r0 + segments
        for i in range(segments):
            j = (i + 1) % segments
            side.append(len(faces))
            faces.append((r0 + i, r0 + j, r1 + j, r1 + i))
    if not caps:
        return side, []
    last = base + (len(profile) - 1) * segments
    cap_faces = [len(faces), len(faces) + 1]
    faces.append(tuple(reversed(range(base, base + segments))))
    faces.append(tuple(range(last, last + segments)))
    return side, cap_faces


def _torus(verts, faces, ring_r, tube_r, z, segments=32, profile=10):
    """Append a torus lying flat at height z. Returns its face indices."""
    base = len(verts)
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        for j in range(profile):
            b = 2.0 * math.pi * j / profile
            r = ring_r + tube_r * math.cos(b)
            verts.append((r * math.cos(a), r * math.sin(a),
                          z + tube_r * math.sin(b)))
    start = len(faces)
    for i in range(segments):
        i2 = (i + 1) % segments
        for j in range(profile):
            j2 = (j + 1) % profile
            faces.append((base + i * profile + j, base + i2 * profile + j,
                          base + i2 * profile + j2, base + i * profile + j2))
    return list(range(start, len(faces)))


def _box(verts, faces, x0, x1, y0, y1, z0, z1):
    """Append an axis-aligned box. Returns its face indices."""
    b = len(verts)
    verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    start = len(faces)
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
              (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        faces.append(tuple(b + k for k in f))
    return list(range(start, len(faces)))


def _display(cg, name, dark, lit):
    """The control panel readout: a dark glass window a hair proud of
    the panel, with four lit digit blocks and a colon on it -- a clock
    at any distance the model is seen from. Built along +Z from the
    panel face, like a knob."""
    verts, faces = [], []
    lit_faces = set()
    hw, hh = DISPLAY_W / 2.0, DISPLAY_H / 2.0
    glass_t = inch(0.0625)
    _box(verts, faces, -hw, hw, -hh, hh, 0.0, glass_t)
    dw, dh, gap, colon = inch(0.5), inch(0.8), inch(0.18), inch(0.18)
    top = glass_t + inch(0.02)
    for x in (-colon - 2.0 * dw - gap, -colon - dw, colon, colon + dw + gap):
        lit_faces.update(_box(verts, faces, x, x + dw, -dh / 2.0, dh / 2.0,
                              glass_t, top))
    for y in (-inch(0.22), inch(0.12)):
        lit_faces.update(_box(verts, faces, -inch(0.05), inch(0.05),
                              y, y + inch(0.1), glass_t, top))
    return _mesh_child(cg, name, verts, faces, dark, extra_mats=(lit,),
                       face_mats={i: 1 for i in lit_faces})


def _knob(cg, name, metal, dark):
    """A control knob, built along +Z from the panel face: a stainless
    bezel ring on the panel, a dark neck, a tapered body with a
    chamfered front rim, and a dark pointer bar on the face. One mesh,
    two materials."""
    verts, faces = [], []
    smooth, dark_faces = set(), set()
    bezel_t = inch(0.0625)
    neck_end = inch(0.4)
    side, _caps = _revolve(verts, faces,
                           [(KNOB_BEZEL_R, 0.0), (KNOB_BEZEL_R, bezel_t)])
    smooth.update(side)
    side, caps = _revolve(verts, faces,
                          [(inch(0.5), bezel_t), (inch(0.5), neck_end)])
    smooth.update(side)
    dark_faces.update(side + caps)
    side, _caps = _revolve(verts, faces,
                           [(KNOB_R, neck_end),
                            (KNOB_R, neck_end + inch(0.15)),
                            (KNOB_R * 0.92, KNOB_DEPTH - inch(0.1)),
                            (KNOB_R * 0.8, KNOB_DEPTH)])
    smooth.update(side)
    # Pointer: up the face from just off centre, so the knob reads as
    # turned to OFF. Local +Y is up once the knob is stood up.
    dark_faces.update(_box(verts, faces, -inch(0.06), inch(0.06),
                           inch(0.12), KNOB_R * 0.7,
                           KNOB_DEPTH, KNOB_DEPTH + inch(0.07)))
    return _mesh_child(cg, name, verts, faces, metal, extra_mats=(dark,),
                       face_mats={i: 1 for i in dark_faces},
                       smooth_faces=smooth)


def _gas_burner(cg, name, brass, metal):
    """A sealed gas burner, built up from the cooktop: a stainless base
    dish and a brass head and cap, topping out under the grate so a pan
    would sit on iron. One mesh, two materials."""
    verts, faces = [], []
    smooth, mats = set(), {}
    side, caps = _revolve(verts, faces,
                          [(inch(2.7), 0.0), (inch(2.5), inch(0.25))])
    smooth.update(side)
    mats.update({i: 1 for i in side + caps})
    side, caps = _revolve(verts, faces,
                          [(inch(1.7), inch(0.25)), (inch(1.7), inch(0.6))])
    smooth.update(side)
    side, caps = _revolve(verts, faces,
                          [(inch(1.35), inch(0.6)), (inch(1.35), inch(0.68)),
                           (inch(1.1), inch(0.75))])
    smooth.update(side)
    return _mesh_child(cg, name, verts, faces, brass, extra_mats=(metal,),
                       face_mats=mats, smooth_faces=smooth)


def _grate_ring(cg, name, iron):
    """The cast ring around a gas burner, lifted like the rails. A closed
    square profile revolved; only its walls shade smooth."""
    verts, faces = [], []
    r0, r1 = GRATE_RING_R - GRATE_RAIL, GRATE_RING_R
    z0, z1 = GRATE_LIFT, GRATE_LIFT + GRATE_BAR_H
    side, _caps = _revolve(verts, faces,
                           [(r0, z0), (r1, z0), (r1, z1), (r0, z1), (r0, z0)],
                           caps=False)
    n = len(side) // 4
    return _mesh_child(cg, name, verts, faces, iron,
                       smooth_faces=side[n:2 * n] + side[3 * n:])


# Grate columns per burner count, as (x0, x1) fractions of the width.
_GRATE_COLUMNS = {
    4: ((0.02, 0.50), (0.50, 0.98)),
    5: ((0.02, 0.36), (0.36, 0.64), (0.64, 0.98)),
    6: ((0.02, 0.345), (0.345, 0.655), (0.655, 0.98)),
}


def _build_gas_grates(cg, layout, iron, top='dim_z', front=GRATE_FRONT):
    """One continuous grate per column of burners. The frame is driven
    slabs, so it stretches with the range; each burner inside it gets a
    fixed ring joined to the frame by driven arms -- out to the runners
    either side, and front and back to the rails or, where two burners
    share a column, to each other. Arm lengths clamp at zero so a
    narrow range cannot fold one inside out. ``top`` is the cooking
    surface as an expression; ``front`` how far down the depth the
    grates reach, as a fraction."""
    columns = _GRATE_COLUMNS.get(len(layout), _GRATE_COLUMNS[5])
    rail, gap, lift, bar_h = GRATE_RAIL, GRATE_GAP, GRATE_LIFT, GRATE_BAR_H
    reach = rail + GRATE_RING_R - inch(0.1)   # arm end tucks into the ring
    z_top = '%s + %f' % (top, lift)
    y_back = '-dim_y * %f' % GRATE_BACK
    depth = 'dim_y * %f' % (front - GRATE_BACK)
    for c, (c0, c1) in enumerate(columns):
        tag = "Grate %d" % (c + 1)
        x0 = 'dim_x * %f + %f' % (c0, gap)
        width = 'dim_x * %f - %f' % (c1 - c0, 2.0 * gap)
        _flat(cg, tag + " Left Runner", x0, y_back, top, rail, depth,
              lift + bar_h, iron)
        _flat(cg, tag + " Right Runner", 'dim_x * %f - %f' % (c1, gap + rail),
              y_back, top, rail, depth, lift + bar_h, iron)
        _flat(cg, tag + " Back Rail", x0, y_back, z_top, width, rail, bar_h,
              iron)
        _flat(cg, tag + " Front Rail", x0,
              '-dim_y * %f + %f' % (front, rail), z_top, width, rail,
              bar_h, iron)
        members = sorted((fy, fx, i) for i, (fx, fy) in enumerate(layout)
                         if c0 <= fx < c1)
        for k, (fy, fx, i) in enumerate(members):
            name = "Burner %d" % (i + 1)
            ring = _CageWrap(_grate_ring(cg, name + " Ring", iron))
            ring.driver_location('x', 'dim_x * %f' % fx, [cg.dim_x])
            ring.driver_location('y', '-dim_y * %f' % fy, [cg.dim_y])
            ring.driver_location('z', top, [cg.dim_z])
            _flat(cg, name + " Left Arm", '%s + %f' % (x0, rail),
                  '-dim_y * %f + %f' % (fy, rail / 2.0), z_top,
                  'max(dim_x * %f - %f, 0.0)' % (fx - c0, gap + reach),
                  rail, bar_h, iron)
            _flat(cg, name + " Right Arm",
                  'dim_x * %f + %f' % (fx, GRATE_RING_R - inch(0.1)),
                  '-dim_y * %f + %f' % (fy, rail / 2.0), z_top,
                  'max(dim_x * %f - %f, 0.0)' % (c1 - fx, gap + reach),
                  rail, bar_h, iron)
            if k == 0:
                _flat(cg, name + " Back Arm",
                      'dim_x * %f - %f' % (fx, rail / 2.0),
                      '-dim_y * %f - %f' % (GRATE_BACK, rail), z_top, rail,
                      'max(dim_y * %f - %f, 0.0)' % (fy - GRATE_BACK, reach),
                      bar_h, iron)
            if k == len(members) - 1:
                _flat(cg, name + " Front Arm",
                      'dim_x * %f - %f' % (fx, rail / 2.0),
                      '-dim_y * %f - %f' % (fy, GRATE_RING_R - inch(0.1)),
                      z_top, rail,
                      'max(dim_y * %f - %f, 0.0)' % (front - fy, reach),
                      bar_h, iron)
            else:
                fy_next = members[k + 1][0]
                _flat(cg, name + " Link Arm",
                      'dim_x * %f - %f' % (fx, rail / 2.0),
                      '-dim_y * %f - %f' % (fy, GRATE_RING_R - inch(0.1)),
                      z_top, rail,
                      'max(dim_y * %f - %f, 0.0)'
                      % (fy_next - fy, 2.0 * (GRATE_RING_R - inch(0.1))),
                      bar_h, iron)


def _electric_burner(cg, name, coil, dark):
    """A coil element in its drip bowl. Concentric rings read as the
    spiral from any distance the model is seen at."""
    verts, faces = [], []
    smooth, mats = set(), {}
    side, caps = _revolve(verts, faces,
                          [(inch(3.7), 0.0), (inch(3.7), inch(0.1)),
                           (inch(3.2), inch(0.2))])
    smooth.update(side)
    mats.update({i: 1 for i in side + caps})
    for ring in (1.0, 1.7, 2.4, 3.05):
        smooth.update(_torus(verts, faces, inch(ring), inch(0.2), inch(0.35)))
    return _mesh_child(cg, name, verts, faces, coil, extra_mats=(dark,),
                       face_mats=mats, smooth_faces=smooth)


def _induction_mark(cg, name, print_mat):
    """The ring printed on induction glass for one element, with a small
    centre ring, sitting a hair proud so it is not lost in the glass."""
    verts, faces = [], []
    h = inch(0.01)
    for r0, r1 in ((inch(3.4), inch(3.6)), (inch(0.9), inch(1.05))):
        _revolve(verts, faces,
                 [(r0, 0.0), (r1, 0.0), (r1, h), (r0, h), (r0, 0.0)],
                 caps=False)
    return _mesh_child(cg, name, verts, faces, print_mat)


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


def models_shown(scene=None):
    """Whether the scene shows its appliance models, or only the cages."""
    scene = scene or bpy.context.scene
    hb = getattr(scene, 'home_builder', None)
    return bool(getattr(hb, 'show_appliance_models', True))


def _set_hidden(obj, hide):
    # Render visibility goes with it: the generated drawings and
    # renders are produced through the render path, and a model the
    # room is not showing has no business printing on a sheet.
    obj.hide_viewport = hide
    obj.hide_render = hide
    try:
        obj.hide_set(hide)
    except RuntimeError:
        pass  # not in the active view layer


def _follows_switch(cage_obj):
    """An appliance that has never been given its own model choice
    follows the scene switch: modeled while it is on, a cage while
    off. One that was set to None in its prompts stays a cage."""
    return supports(cage_obj) and stored_opts(cage_obj) is None


def _seed_modeled(cage_obj):
    opts = defaults_for(cage_obj)
    opts['model_style'] = 'MODELED'
    set_opts(cage_obj, opts)
    return build_geometry(cage_obj)


def apply_visibility(scene=None):
    """Hide or show the model parts on every appliance in the scene, per
    its Show Model switch. Turning it on also models the appliances
    that have been following the switch. The switch covers renders and
    generated drawings too -- models turned off stay off the sheet --
    while the cages, and the labels they carry, remain."""
    scene = scene or bpy.context.scene
    hide = not models_shown(scene)
    if not hide:
        # Snapshot first: building adds objects to the scene.
        waiting = [obj for obj in scene.objects
                   if obj.get('IS_APPLIANCE') and _follows_switch(obj)]
        for obj in waiting:
            _seed_modeled(obj)
    parts = [obj for obj in scene.objects if obj.get(GEO_CHILD_FLAG)]
    for obj in parts:
        _set_hidden(obj, hide)
    for obj in [o for o in scene.objects if o.get('IS_APPLIANCE')]:
        refresh_labels(obj)
    refresh_clearance_cuts(scene)
    return len(parts)


# ---------------------------------------------------------------------------
# Appliances housed in a cabinet opening
#
# A refrigerator cabinet's appliance opening carries the refrigerator
# model itself: an ordinary appliance cage parented to the opening and
# sized to it on every solve, so the model follows the cabinet. It is a
# normal appliance after that -- its prompts, the Show Model switch --
# minus the label, which the opening already carries.
# ---------------------------------------------------------------------------

CABINET_APPLIANCE_FLAG = 'IS_CABINET_APPLIANCE'
CABINET_APPLIANCE_CLEARANCE = inch(0.25)
CABINET_APPLIANCE_PROUD = inch(2.5)   # a built-in's doors stand this far
                                      # out of the carcass

_OPENING_APPLIANCE_CLASSES = {'REFRIGERATOR': 'Refrigerator', 'SINK': 'Sink',
                              'WALL_OVEN': 'WallOven',
                              'MICROWAVE': 'Microwave'}


def opening_appliance(opening_obj):
    return next((c for c in opening_obj.children
                 if c.get(CABINET_APPLIANCE_FLAG)), None)


def sync_opening_appliance(opening_obj, appliance_type='REFRIGERATOR',
                           span=None):
    """Keep the appliance in a cabinet opening sized to it, creating it
    the first time. The opening's origin is at its front face and the
    cabinet's back lies at +Dim Y, so the appliance stands with its
    back there and its doors out past the front. ``span`` is
    (x, width, z, height) in the opening's own space when the appliance
    must fit something narrower than the cage -- a face frame's stiles
    and rail -- and defaults to the whole cage."""
    from . import types_appliances
    cls = getattr(types_appliances,
                  _OPENING_APPLIANCE_CLASSES.get(appliance_type, ''), None)
    if cls is None:
        return None
    wrap = _CageWrap(opening_obj)
    dim_x, dim_y, dim_z = (wrap.get_input('Dim X'), wrap.get_input('Dim Y'),
                           wrap.get_input('Dim Z'))
    x0, span_w, z0, span_h = span or (0.0, dim_x, 0.0, dim_z)
    c = CABINET_APPLIANCE_CLEARANCE
    return _ensure_cabinet_appliance(
        opening_obj, cls, max(span_w - 2.0 * c, 0.0),
        dim_y + CABINET_APPLIANCE_PROUD, max(span_h - c, 0.0),
        (x0 + c, dim_y, z0))


SIZE_OWNED_FLAG = 'APPLIANCE_SIZE_OWNED'


def sync_bay_appliance(bay_obj, kind, top_z):
    """A sink or cooktop bay carries the appliance itself, hung with the
    countertop's top surface at the top of its cage so it can sit under
    or on the counter. ``top_z`` is the cabinet top in the bay's own
    space; the bay's origin is at its front and the cabinet's back lies
    at +Dim Y. The appliance fills the bay until its own prompts take
    over its size, after which the bay only keeps it centred."""
    from . import types_appliances
    wrap = _CageWrap(bay_obj)
    dim_x, dim_y = wrap.get_input('Dim X'), wrap.get_input('Dim Y')
    existing = opening_appliance(bay_obj)
    defaults = _DEFAULTS_BY_TYPE.get(kind, _COMMON_DEFAULTS)
    ct = float(merged_opts(existing).get('counter_thickness', inch(1.5))
               if existing is not None
               else defaults.get('counter_thickness', inch(1.5)))
    if kind == 'COOKTOP':
        cls, drop = types_appliances.Cooktop, COOKTOP_DROP
    else:
        cls, drop = types_appliances.Sink, SINK_H
    return _ensure_cabinet_appliance(
        bay_obj, cls,
        max(dim_x - 2.0 * SINK_SIDE_MARGIN, 0.0),
        max(dim_y - 2.0 * SINK_END_GAP, 0.0), drop + ct,
        (SINK_SIDE_MARGIN, dim_y - SINK_END_GAP, top_z - drop),
        top_anchored=True)


def sync_bay_sink(bay_obj, top_z):
    return sync_bay_appliance(bay_obj, 'SINK', top_z)


def sync_galley_sink(root_obj, x, width, y_back, depth, top_z):
    """A workstation cabinet carries its sink on the cabinet itself,
    spanning every bay between the end partitions: ``x`` / ``width``
    across the cabinet, ``y_back`` and ``depth`` from the back panel to
    the front apron, the rim at ``top_z``. Seeded as a workstation bowl
    nine inches deep."""
    from . import types_appliances
    existing = opening_appliance(root_obj)
    ct = float(merged_opts(existing).get('counter_thickness', inch(1.5))
               if existing is not None
               else _SINK_DEFAULTS['counter_thickness'])
    return _ensure_cabinet_appliance(
        root_obj, types_appliances.Sink, width, depth, SINK_H + ct,
        (x, y_back, top_z - SINK_H), top_anchored=True,
        seed={'sink_style': 'WORKSTATION', 'bowl_depth': inch(9.0)})


def _drop_own_label(cage_obj):
    """Remove an appliance's own label text. Run on every sync, not only
    when the cage is created, so a cage that kept its label heals on the
    next recalc instead of printing the word over the cabinet front."""
    for child in list(cage_obj.children):
        if not child.get('IS_APPLIANCE_TEXT'):
            continue
        data = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if data is not None and data.users == 0:
            try:
                bpy.data.curves.remove(data)
            except Exception:
                pass


def _ensure_cabinet_appliance(parent_obj, cls, width, depth, height,
                              location, top_anchored=False, seed=None):
    """The appliance cage a cabinet part houses, created the first time
    and sized every time -- until its own prompts take its size over
    (SIZE_OWNED_FLAG), after which it keeps its size and is centred in
    the width it would have filled, holding its top or its bottom as
    ``top_anchored`` says. Its label is dropped: the cabinet already
    carries one."""
    cage = opening_appliance(parent_obj)
    if cage is not None and cage.get('APPLIANCE_TYPE') != getattr(
            cls, 'APPLIANCE_TYPE', cage.get('APPLIANCE_TYPE')):
        remove_opening_appliance(parent_obj)
        cage = None
    if cage is None:
        app = cls()
        app.width, app.depth, app.height = width, depth, height
        app.create()
        cage = app.obj
        cage.parent = parent_obj
        cage[CABINET_APPLIANCE_FLAG] = True
        _link_like_cage(cage, parent_obj)
    elif cage.get(SIZE_OWNED_FLAG):
        own = _CageWrap(cage)
        own_w, own_h = own.get_input('Dim X'), own.get_input('Dim Z')
        location = (location[0] + (width - own_w) / 2.0, location[1],
                    location[2] + ((height - own_h) if top_anchored else 0.0))
    else:
        own = _CageWrap(cage)
        own.set_input('Dim X', width)
        own.set_input('Dim Y', depth)
        own.set_input('Dim Z', height)
    cage.location = location
    _drop_own_label(cage)
    if stored_opts(cage) is None:
        seed_on_place(cage)
        if seed and stored_opts(cage) is not None:
            opts = merged_opts(cage)
            opts.update(seed)
            set_opts(cage, opts)
            build_geometry(cage)
    refresh_labels(cage)
    return cage


def remove_opening_appliance(opening_obj):
    """Take the appliance out of an opening that no longer houses one."""
    cage = opening_appliance(opening_obj)
    if cage is None:
        return
    remove_geometry(cage)
    for child in list(cage.children_recursive):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(cage, do_unlink=True)


def seed_on_place(cage_obj):
    """Called once an appliance has been placed. With the switch on it
    comes in modeled with its type's defaults; off, it stays a cage
    and picks up a model when the switch turns on."""
    if cage_obj is None or not _follows_switch(cage_obj):
        return False
    if not models_shown():
        return False
    return _seed_modeled(cage_obj)


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
    refresh_labels(cage_obj)


def _label_objects(cage_obj):
    """The words that name an appliance in the room: its own label text,
    and for one housed in a cabinet, the annotation or accessory label
    the cabinet part carries."""
    for child in cage_obj.children:
        if child.get('IS_APPLIANCE_TEXT'):
            yield child
    parent = cage_obj.parent
    if cage_obj.get(CABINET_APPLIANCE_FLAG) and parent is not None:
        for child in parent.children:
            if (child.get('APPLIANCE_ANNOTATION')
                    or child.name.startswith('Accessory Label')):
                yield child


def refresh_labels(cage_obj):
    """An appliance's label shows only while its model does not: the
    word stands in for a bare cage. Hidden in this view layer alone, so
    the drawing scenes keep their labels."""
    hide = models_shown() and bool(_geo_children(cage_obj))
    for obj in _label_objects(cage_obj):
        try:
            obj.hide_set(hide)
        except RuntimeError:
            pass


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


def _fridge_grille(cg, z, height, mat, dark, door_t):
    """A louvered grille: slats in the body finish standing proud of a
    dark recess, pitched evenly down its height with a margin top and
    bottom. ``z`` may be an expression, for a grille up at the top."""
    _front(cg, "Fridge Grille", 0.0, z, 'dim_x', height, door_t, dark)
    slat, pitch = inch(0.5), inch(0.875)
    count = int((height - inch(0.5)) // pitch)
    if count <= 0:
        return
    z0 = (height - (count * pitch - (pitch - slat))) / 2.0
    for i in range(count):
        _front(cg, "Grille Slat %d" % (i + 1), inch(1.0),
               _add(z, z0 + i * pitch), 'dim_x - %f' % inch(2.0), slat,
               inch(0.1875), mat, proud=True)


def _fridge_dispenser(cg, z, mat, dark, metal):
    """The water and ice dispenser on the upper left door: a dark panel
    on the door face, a lit readout across its top and a stainless drip
    tray at its foot. Fixed size -- a dispenser is a dispenser whatever
    the fridge measures. ``z`` is the panel's bottom edge."""
    x, w, h = inch(3.0), inch(9.0), inch(13.0)
    _front(cg, "Fridge Dispenser", x, z, w, h, inch(0.125), dark, proud=True)
    _flat(cg, "Dispenser Tray", x + inch(0.75), '-dim_y - %f' % inch(0.125),
          _add(z, inch(0.75)), w - inch(1.5), inch(0.85), inch(0.25), metal)
    obj = _display(cg, "Dispenser Display", dark, _display_material())
    obj.rotation_euler.x = math.radians(90)
    obj.location.x = x + w / 2.0
    wrap = _CageWrap(obj)
    wrap.driver_location('y', '-dim_y - %f' % inch(0.125), [cg.dim_y])
    wrap.driver_location('z', _add(z, h - inch(2.0)), cg.vars_for(z))


def _build_refrigerator(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = FRIDGE_DOOR_T
    grille_h = float(opts.get('grille_height', inch(4.0)))
    grille_top = opts.get('grille_position', 'TOP') == 'TOP'
    panel_ready = is_panel_ready(cage_obj)

    # The case: everything behind the doors, faced with a dark reveal
    # so the gaps between the doors read as gaps and not as more steel.
    _flat(cg, "Fridge Case", 0.0, 0.0, 0.0,
          'dim_x', 'dim_y - %f' % (door_t + FRIDGE_REVEAL_T), 'dim_z',
          dark if panel_ready else mat)
    _front(cg, "Fridge Reveal", 0.0, 0.0, 'dim_x', 'dim_z', FRIDGE_REVEAL_T,
           dark, y='-dim_y + %f' % door_t)

    # The grille sits above the doors on a built-in, with a kick below
    # them, or below the doors on a freestanding unit.
    base, top = 0.0, 0.0
    if grille_h > 0.0 and grille_top:
        _fridge_grille(cg, 'dim_z - %f' % grille_h, grille_h, mat, dark,
                       door_t)
        top = grille_h + GAP
        _front(cg, "Fridge Kick", 0.0, 0.0, 'dim_x', FRIDGE_KICK_H, door_t,
               dark, y='-dim_y + %f' % inch(0.5))
        base = FRIDGE_KICK_H + GAP
    elif grille_h > 0.0:
        _fridge_grille(cg, 0.0, grille_h, mat, dark, door_t)
        base = grille_h

    if panel_ready:
        # The fronts come from the appliance panels on this same cage.
        return

    config = opts.get('fridge_config', 'FRENCH')
    freezer_h = float(opts.get('freezer_height', inch(24.0)))

    if config == 'SIDE_BY_SIDE':
        frac = min(max(float(opts.get('freezer_fraction', 0.42)), 0.2), 0.8)
        height = 'dim_z - %f' % (base + top)
        _fridge_door(cg, opts, mat, metal, "Freezer Door", 0.0,
                     'dim_x * %f - %f' % (frac, GAP * 0.5),
                     base, height, door_t, handle_at_right=True)
        _fridge_door(cg, opts, mat, metal, "Fridge Door",
                     'dim_x * %f + %f' % (frac, GAP * 0.5),
                     'dim_x * %f - %f' % (1.0 - frac, GAP * 0.5),
                     base, height, door_t)
    elif config == 'TOP_FREEZER':
        _fridge_door(cg, opts, mat, metal, "Freezer Door", 0.0, 'dim_x',
                     'dim_z - %f' % (freezer_h + top), freezer_h, door_t,
                     vertical_handle=False, handle_at_bottom=True)
        _fridge_door(cg, opts, mat, metal, "Fridge Door", 0.0, 'dim_x',
                     base, 'dim_z - %f' % (base + freezer_h + GAP + top),
                     door_t, vertical_handle=False)
    else:
        _fridge_drawers(cg, opts, mat, metal, base, freezer_h, door_t)
        door_z = base + freezer_h + GAP
        door_h = 'dim_z - %f' % (door_z + top)
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
        _fridge_dispenser(cg, 'dim_z - %f' % (top + inch(21.0)), mat, dark,
                          metal)


# ---------------------------------------------------------------------------
# Built-in wall oven and microwave
#
# Both live in a tall cabinet's appliance opening: the cage fills the
# opening between the fillers, a couple of inches proud of the carcass.
# ---------------------------------------------------------------------------

def _build_wall_oven(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    door_t = RANGE_DOOR_T
    ctrl = OVEN_CONTROL_H
    _flat(cg, "Oven Case", 0.0, 0.0, 0.0, 'dim_x', 'dim_y - %f' % door_t,
          'dim_z', mat)
    # Control band across the top, with the readout in the middle and a
    # knob either side of it.
    _front(cg, "Oven Controls", 0.0, 'dim_z - %f' % ctrl, 'dim_x', ctrl,
           door_t, dark)
    z_ctrl = 'dim_z - %f' % (ctrl * 0.5)
    obj = _display(cg, "Oven Display", dark, _display_material())
    obj.rotation_euler.x = math.radians(90)
    wrap = _CageWrap(obj)
    wrap.driver_location('x', 'dim_x * 0.5', [cg.dim_x])
    wrap.driver_location('y', '-dim_y', [cg.dim_y])
    wrap.driver_location('z', z_ctrl, [cg.dim_z])
    if opts.get('knobs', True):
        for i, fx in enumerate((0.16, 0.84)):
            obj = _knob(cg, "Oven Knob %d" % (i + 1), metal, dark)
            obj.rotation_euler.x = math.radians(90)
            wrap = _CageWrap(obj)
            wrap.driver_location('x', 'dim_x * %f' % fx, [cg.dim_x])
            wrap.driver_location('y', '-dim_y', [cg.dim_y])
            wrap.driver_location('z', z_ctrl, [cg.dim_z])
    # The door fills what is left, with the full-width window and a bar
    # handle along its top, like a range's oven.
    height = 'dim_z - %f' % (ctrl + GAP)
    _front(cg, "Oven Door", 0.0, 0.0, 'dim_x', height, door_t, mat)
    _oven_window(cg, "Oven Door", 0.0, 'dim_x', 0.0, height, dark)
    _bar_handle(cg, "Oven Handle", opts, metal, inch(2.0),
                _sub(height, inch(3.0)), 'dim_x - %f' % inch(4.0), False)


def _keypad(cg, name, dark, lit):
    """A microwave's keypad: a grid of small keys, built up from the
    panel face, with the top row lit as the readout's neighbours."""
    verts, faces = [], []
    key_w, key_h, gap = inch(1.0), inch(0.55), inch(0.3)
    cols, rows = 3, 4
    total_w = cols * key_w + (cols - 1) * gap
    total_h = rows * key_h + (rows - 1) * gap
    for r in range(rows):
        for c in range(cols):
            x = -total_w / 2.0 + c * (key_w + gap)
            y = total_h / 2.0 - key_h - r * (key_h + gap)
            _box(verts, faces, x, x + key_w, y, y + key_h, 0.0, inch(0.05))
    return _mesh_child(cg, name, verts, faces, dark, extra_mats=(lit,))


def _build_microwave(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    t = inch(1.0)
    trim = MICRO_TRIM if opts.get('trim_kit', True) else 0.0
    # The face recesses behind a trim kit; without one it is the front.
    # The case stops where the door and panel begin, so no two faces
    # share the front plane.
    recess = MICRO_RECESS if trim > 0.0 else 0.0
    face_y = '-dim_y + %f' % recess
    _flat(cg, "Microwave Case", 0.0, 0.0, 0.0, 'dim_x',
          'dim_y - %f' % (recess + t), 'dim_z', mat)
    if trim > 0.0:
        # The trim kit: a stainless frame at the front plane around a
        # recessed face.
        _front(cg, "Trim Top", 0.0, 'dim_z - %f' % trim, 'dim_x', trim,
               MICRO_RECESS, mat)
        _front(cg, "Trim Bottom", 0.0, 0.0, 'dim_x', trim, MICRO_RECESS, mat)
        _front(cg, "Trim Left", 0.0, trim, trim, 'dim_z - %f' % (2.0 * trim),
               MICRO_RECESS, mat)
        _front(cg, "Trim Right", 'dim_x - %f' % trim, trim, trim,
               'dim_z - %f' % (2.0 * trim), MICRO_RECESS, mat)
    # Door on the left, control panel on the right.
    door_w = 'dim_x - %f' % (2.0 * trim + MICRO_PANEL_W + GAP)
    height = 'dim_z - %f' % (2.0 * trim)
    _front(cg, "Microwave Door", trim, trim, door_w, height, t, mat,
           y=face_y)
    inset = inch(1.5)
    _front(cg, "Microwave Window", trim + inset, trim + inset,
           _sub(door_w, 2.0 * inset), _sub(height, 2.0 * inset), inch(0.0625),
           dark, y=face_y, proud=True)
    _bar_handle(cg, "Microwave Handle", opts, metal,
                _sub(_add(trim, door_w), inch(2.0) + HANDLE_SECTION),
                trim + inch(3.0), _sub(height, inch(6.0)), True)
    x_panel = 'dim_x - %f' % (trim + MICRO_PANEL_W)
    _front(cg, "Microwave Controls", x_panel, trim, MICRO_PANEL_W, height, t,
           dark, y=face_y)
    lit = _display_material()
    obj = _display(cg, "Microwave Display", dark, lit)
    obj.rotation_euler.x = math.radians(90)
    wrap = _CageWrap(obj)
    wrap.driver_location('x', 'dim_x - %f' % (trim + MICRO_PANEL_W / 2.0),
                         [cg.dim_x])
    wrap.driver_location('y', face_y, [cg.dim_y])
    wrap.driver_location('z', 'dim_z - %f' % (trim + inch(1.75)), [cg.dim_z])
    obj = _keypad(cg, "Microwave Keypad", metal, lit)
    obj.rotation_euler.x = math.radians(90)
    wrap = _CageWrap(obj)
    wrap.driver_location('x', 'dim_x - %f' % (trim + MICRO_PANEL_W / 2.0),
                         [cg.dim_x])
    wrap.driver_location('y', face_y, [cg.dim_y])
    wrap.driver_location('z', 'dim_z - %f' % (trim + inch(5.5)), [cg.dim_z])


# ---------------------------------------------------------------------------
# Sink
#
# The cage top is the countertop's top surface, with the countertop
# taking the top ``counter_thickness`` of the cage. An undermount's rim
# sits at the counter's underside and a drop-in's flange on its top; the
# bowl is the same depth either way, and the faucet stands on the
# counter surface.
# ---------------------------------------------------------------------------

def _sweep(verts, faces, points, tube_r, segments=12):
    """Append a round tube along a polyline, capped at both ends. Returns
    its face indices. Frames are built against +X, so the path should
    not run along X."""
    def norm(v):
        n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
        return (v[0] / n, v[1] / n, v[2] / n)

    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0])

    base = len(verts)
    count = len(points)
    for i, p in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, count - 1)]
        t = norm((b[0] - a[0], b[1] - a[1], b[2] - a[2]))
        n = norm(cross(t, (1.0, 0.0, 0.0)))
        bn = cross(t, n)
        for k in range(segments):
            ang = 2.0 * math.pi * k / segments
            c, s = math.cos(ang), math.sin(ang)
            verts.append((p[0] + tube_r * (c * n[0] + s * bn[0]),
                          p[1] + tube_r * (c * n[1] + s * bn[1]),
                          p[2] + tube_r * (c * n[2] + s * bn[2])))
    start = len(faces)
    for i in range(count - 1):
        r0 = base + i * segments
        r1 = r0 + segments
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((r0 + k, r0 + j, r1 + j, r1 + k))
    last = base + (count - 1) * segments
    faces.append(tuple(reversed(range(base, base + segments))))
    faces.append(tuple(range(last, last + segments)))
    return list(range(start, len(faces)))


def _faucet(cg, name, metal):
    """A gooseneck faucet: base plate, column, an arc up and over that
    drops to the spout, and a lever handle out to the right. Built up
    from the deck it stands on."""
    verts, faces = [], []
    smooth = set()
    side, _caps = _revolve(verts, faces,
                           [(inch(1.1), 0.0), (inch(1.0), inch(0.4))])
    smooth.update(side)
    top = inch(9.0)
    side, _caps = _revolve(verts, faces,
                           [(inch(0.55), inch(0.4)), (inch(0.55), top)])
    smooth.update(side)
    radius = inch(3.0)
    path = [(0.0, -radius + radius * math.cos(a), top + radius * math.sin(a))
            for a in (i * math.pi / 16.0 for i in range(17))]
    path += [(0.0, -2.0 * radius, top - inch(1.0)),
             (0.0, -2.0 * radius, top - inch(2.0))]
    smooth.update(_sweep(verts, faces, path, inch(0.42)))
    _box(verts, faces, inch(0.5), inch(2.8), -inch(0.25), inch(0.25),
         inch(7.6), inch(8.2))
    return _mesh_child(cg, name, verts, faces, metal, smooth_faces=smooth)


def _sink_bowl(cg, name, x0, width, floor_z, height, mat, dark,
               drain_frac=0.5, ledges=()):
    """One bowl: four thin walls and a floor hanging from the rim, with
    a drain ``drain_frac`` of the way across the floor. ``x0`` and
    ``width`` may be expressions; ``floor_z`` is where the floor sits
    and ``height`` runs from there to the rim's underside. ``ledges``
    are drops below the rim at which a strip steps in along the front
    and back walls, as a workstation's tiers."""
    t = SINK_WALL_T
    depth = 'dim_y - %f' % (SINK_BACK_DECK + SINK_FRONT_RIM)
    _flat(cg, name + " Floor", x0, -SINK_BACK_DECK, floor_z, width, depth, t,
          mat)
    _front(cg, name + " Back", x0, floor_z, width, height, t, mat,
           y=-SINK_BACK_DECK)
    _front(cg, name + " Front", x0, floor_z, width, height, t, mat,
           y='-dim_y + %f' % SINK_FRONT_RIM, proud=True)
    _side(cg, name + " Left", x0, -SINK_BACK_DECK, floor_z, height, depth, t,
          mat, plus_x=False)
    _side(cg, name + " Right", _add(x0, width), -SINK_BACK_DECK, floor_z,
          height, depth, t, mat)
    verts, faces = [], []
    side, _caps = _revolve(verts, faces,
                           [(inch(1.75), 0.0), (inch(1.75), inch(0.05))])
    drain = _CageWrap(_mesh_child(cg, name + " Drain", verts, faces, dark,
                                  smooth_faces=side))
    x_mid = _add(x0, '(%s) * %f' % (width, drain_frac)
                 if isinstance(width, str) else width * drain_frac)
    y_mid = '-(dim_y + %f) * 0.5' % (SINK_BACK_DECK - SINK_FRONT_RIM)
    drain.driver_location('x', x_mid, cg.vars_for(x_mid))
    drain.driver_location('y', y_mid, [cg.dim_y])
    _place(cg, drain, 'z', _add(floor_z, t))
    ledge_d, ledge_t = inch(1.25), inch(0.1)
    for k, drop in enumerate(ledges):
        z = _sub(_add(floor_z, height), drop)
        _flat(cg, "%s Back Ledge %d" % (name, k + 1), x0, -SINK_BACK_DECK, z,
              width, ledge_d, ledge_t, mat)
        _flat(cg, "%s Front Ledge %d" % (name, k + 1), x0,
              '-dim_y + %f' % (SINK_FRONT_RIM + ledge_d), z, width, ledge_d,
              ledge_t, mat)


def _sink_levels(opts):
    """Where a sink's rim and bowl floor sit, as offsets from the cage
    top (the counter surface). Returns (rim_z, rim_t, floor_drop): the
    rim's underside and thickness, and how far below the cage top the
    floor lies -- None when the floor is simply the cage floor (or, for
    a drop-in, a counter thickness above it)."""
    ct = float(opts.get('counter_thickness', inch(1.5)))
    drop_in = opts.get('mount', 'UNDERMOUNT') == 'DROP_IN'
    depth = float(opts.get('bowl_depth', 0.0))
    if drop_in:
        # The flange seats on the counter, a hair up so no face shares
        # the counter's top plane.
        rim_t = inch(0.125)
        rim_z = SINK_SEAT
        floor_drop = depth if depth > 0.0 else None
    else:
        # The rim tucks a hair under the counter for the same reason.
        rim_t = SINK_WALL_T
        rim_z = -(ct + SINK_SEAT + rim_t)
        floor_drop = (ct + SINK_SEAT + rim_t + depth) if depth > 0.0 else None
    return rim_z, rim_t, floor_drop


def _build_sink(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    style = opts.get('sink_style', 'DOUBLE')
    bowls = 2 if style == 'DOUBLE' else 1
    ct = float(opts.get('counter_thickness', inch(1.5)))
    drop_in = opts.get('mount', 'UNDERMOUNT') == 'DROP_IN'
    # A drop-in's flange is what you see; an undermount's rim is a
    # hairline under the counter. The bowl hangs from the rim to its
    # floor: the cage floor by default (a counter thickness up for a
    # drop-in, so the bowl is the same depth), or Bowl Depth down.
    rim_off, t, floor_drop = _sink_levels(opts)
    z_rim = 'dim_z + %f' % rim_off if rim_off >= 0 else 'dim_z - %f' % -rim_off
    if floor_drop is not None:
        floor_z = 'dim_z - %f' % floor_drop
    else:
        floor_z = ct if drop_in else 0.0
    bowl_h = _sub(z_rim, floor_z)

    # The rim: strips around the bowls, and between them on a double.
    inner = 'dim_y - %f' % (SINK_BACK_DECK + SINK_FRONT_RIM)
    _flat(cg, "Sink Rim Back", 0.0, 0.0, z_rim, 'dim_x', SINK_BACK_DECK, t, mat)
    _flat(cg, "Sink Rim Front", 0.0, '-dim_y + %f' % SINK_FRONT_RIM, z_rim,
          'dim_x', SINK_FRONT_RIM, t, mat)
    _flat(cg, "Sink Rim Left", 0.0, -SINK_BACK_DECK, z_rim, SINK_SIDE_RIM,
          inner, t, mat)
    _flat(cg, "Sink Rim Right", 'dim_x - %f' % SINK_SIDE_RIM, -SINK_BACK_DECK,
          z_rim, SINK_SIDE_RIM, inner, t, mat)
    if bowls == 1:
        drain = {'LEFT': 0.25, 'RIGHT': 0.75}.get(
            opts.get('drain_side', 'CENTER'), 0.5)
        ledges = (inch(1.75), inch(3.5)) if style == 'WORKSTATION' else ()
        _sink_bowl(cg, "Bowl", SINK_SIDE_RIM,
                   'dim_x - %f' % (2.0 * SINK_SIDE_RIM), floor_z, bowl_h, mat,
                   dark, drain, ledges)
    else:
        _flat(cg, "Sink Rim Divider", 'dim_x * 0.5 - %f' % (SINK_DIVIDER / 2.0),
              -SINK_BACK_DECK, z_rim, SINK_DIVIDER, inner, t, mat)
        width = '(dim_x - %f) * 0.5' % (2.0 * SINK_SIDE_RIM + SINK_DIVIDER)
        _sink_bowl(cg, "Left Bowl", SINK_SIDE_RIM, width, floor_z, bowl_h, mat,
                   dark)
        _sink_bowl(cg, "Right Bowl", 'dim_x * 0.5 + %f' % (SINK_DIVIDER / 2.0),
                   width, floor_z, bowl_h, mat, dark)

    if style == 'FARMHOUSE':
        # The apron runs from the bowl floor up past the counter: to the
        # flange on a drop-in, a hair proud on an undermount, so its top
        # never lies in the counter's own plane.
        lip = (SINK_SEAT + t) if drop_in else inch(0.0625)
        _front(cg, "Sink Apron", 0.0, floor_z, 'dim_x',
               _sub('dim_z + %f' % lip, floor_z), SINK_APRON_T, mat,
               proud=True)
    if opts.get('faucet', True):
        obj = _faucet(cg, "Faucet", metal)
        obj.location.y = -SINK_BACK_DECK / 2.0
        wrap = _CageWrap(obj)
        wrap.driver_location('x', 'dim_x * 0.5', [cg.dim_x])
        wrap.driver_location('z', 'dim_z', [cg.dim_z])
    # A sink in a cabinet keeps its clearance cutter sized to the bowl
    # it now has, without waiting for the cabinet to recalculate.
    if any(c.get(SINK_CUTTER_FLAG) for c in cage_obj.children):
        sink_clearance_cutter(cage_obj)
    refresh_countertops()


def refresh_countertops(scene=None):
    """The countertops follow the sinks: a top that knows its outline is
    rebuilt from it, which cuts it afresh for every sink; an older box
    top just takes the current cut, so it gains a hole but cannot lose
    one until countertops are added again."""
    try:
        from . import countertop_common
    except Exception:
        return
    scene = scene or bpy.context.scene
    for top in [o for o in scene.objects if o.get('IS_COUNTERTOP')]:
        if countertop_common.has_outline(top):
            countertop_common.rebuild(top)
        else:
            cut_sink_openings(top, countertop_common.world_matrix(top), scene)


def sink_cutout_boxes(cage_obj):
    """The holes a countertop needs over a sink, as boxes in the sink's
    own space: the bowl area with a little clearance past its walls,
    so the counter and the sink never share a face, and for a farmhouse
    a notch through the counter's front edge for the apron. Tall enough
    to pass through any countertop over the rim. Empty for anything but
    a sink."""
    kind = appliance_type(cage_obj)
    if kind not in ('SINK', 'COOKTOP'):
        return []
    wrap = _CageWrap(cage_obj)
    dim_x, dim_y, dim_z = (wrap.get_input('Dim X'), wrap.get_input('Dim Y'),
                           wrap.get_input('Dim Z'))
    opts = merged_opts(cage_obj)
    ct = float(opts.get('counter_thickness', inch(1.5)))
    c = SINK_HOLE_CLEAR
    z0, z1 = dim_z - ct - inch(0.25), dim_z + inch(2.0)
    if kind == 'COOKTOP':
        # The body drops through; the plate covers the hole.
        lip = COOKTOP_LIP
        return [(lip - c, dim_x - lip + c, -(dim_y - lip) - c, -lip + c,
                 z0, z1)]
    boxes = [(SINK_SIDE_RIM - c, dim_x - SINK_SIDE_RIM + c,
              -(dim_y - SINK_FRONT_RIM) - c, -SINK_BACK_DECK + c, z0, z1)]
    if opts.get('sink_style') == 'FARMHOUSE':
        # The counter stops at the apron's back face, a hair into it.
        boxes.append((-c, dim_x + c, -(dim_y + SINK_APRON_T + inch(1.0)),
                      -dim_y - SINK_SEAT, z0, z1))
    return boxes


def cut_sink_openings(countertop_obj, matrix=None, scene=None):
    """Cut the opening for every sink under a countertop, into its mesh,
    so the top stays a plain mesh the way the manual cut leaves it.
    ``matrix`` is the top's world matrix when the cached one is stale.
    Returns how many sinks cut it."""
    scene = scene or bpy.context.scene
    if countertop_obj.type != 'MESH' or not countertop_obj.data.vertices:
        return 0
    sinks = [o for o in scene.objects if o.get('IS_APPLIANCE')
             and appliance_type(o) in ('SINK', 'COOKTOP')]
    if not sinks:
        return 0
    matrix = matrix or countertop_obj.matrix_world
    pts = [matrix @ v.co for v in countertop_obj.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    count = 0
    for sink in sinks:
        cut = False
        for bounds in sink_cutout_boxes(sink):
            x0, x1, y0, y1, z0, z1 = bounds
            corners = [sink.matrix_world @ Vector((x, y, z))
                       for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
            s_lo = [min(p[i] for p in corners) for i in range(3)]
            s_hi = [max(p[i] for p in corners) for i in range(3)]
            if any(s_lo[i] >= hi[i] or s_hi[i] <= lo[i] for i in range(3)):
                continue
            _subtract_box(countertop_obj, sink.matrix_world, bounds, scene)
            cut = True
        count += cut
    return count


SINK_CUTTER_FLAG = 'IS_SINK_CUTTER'


def sink_clearance_cutter(cage_obj):
    """The volume a sink takes out of the cabinet around it -- the whole
    sink and a little more -- as a hidden mesh child for the cabinet's
    parts to boolean against. Made once and resized every call, so it
    tracks the sink. Not a model part: it outlives the model and the
    Show Model switch."""
    cutter = next((c for c in cage_obj.children if c.get(SINK_CUTTER_FLAG)),
                  None)
    wrap = _CageWrap(cage_obj)
    dim_x, dim_y, dim_z = (wrap.get_input('Dim X'), wrap.get_input('Dim Y'),
                           wrap.get_input('Dim Z'))
    m = inch(0.25)
    bottom = 0.0
    if appliance_type(cage_obj) == 'SINK':
        _rim, _t, floor_drop = _sink_levels(merged_opts(cage_obj))
        if floor_drop is not None:
            bottom = min(0.0, dim_z - floor_drop)
    verts, faces = [], []
    _box(verts, faces, -m, dim_x + m, -dim_y - m, m, bottom - m, dim_z + m)
    if cutter is None:
        mesh = bpy.data.meshes.new('Sink Clearance')
        cutter = hb_utils.new_object('Sink Clearance', mesh)
        cutter.parent = cage_obj
        cutter[SINK_CUTTER_FLAG] = True
        cutter.display_type = 'WIRE'
        cutter.hide_viewport = True
        cutter.hide_render = True
        _link_like_cage(cutter, cage_obj)
    mesh = cutter.data
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    return cutter


def clearance_active(cage_obj, scene=None):
    """A sink or cooktop clears the cabinet around it only while its
    model shows: a cage with no model, or a room showing only cages,
    leaves the cabinet parts whole."""
    return (cage_obj is not None and models_shown(scene)
            and bool(_geo_children(cage_obj)))


def set_clearance_cut(mod, active):
    if mod.show_viewport != active:
        mod.show_viewport = active
    if mod.show_render != active:
        mod.show_render = active


def refresh_clearance_cuts(scene=None, cage_obj=None):
    """Switch every boolean cut against a clearance cutter on or off to
    match its appliance -- all of them, or just ``cage_obj``'s."""
    scene = scene or bpy.context.scene
    for obj in scene.objects:
        for mod in obj.modifiers:
            if mod.type != 'BOOLEAN':
                continue
            cutter = mod.object
            if cutter is None or not cutter.get(SINK_CUTTER_FLAG):
                continue
            if cage_obj is not None and cutter.parent is not cage_obj:
                continue
            set_clearance_cut(mod, clearance_active(cutter.parent, scene))


def _subtract_box(target, matrix, bounds, scene):
    """Boolean a box out of a mesh, evaluated through a temporary
    modifier and written back into the mesh datablock it already has."""
    verts, faces = [], []
    _box(verts, faces, *bounds)
    mesh = bpy.data.meshes.new('Sink Cutter')
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    cutter = hb_utils.new_object('Sink Cutter', mesh)
    cutter.matrix_world = matrix.copy()
    scene.collection.objects.link(cutter)
    mod = target.modifiers.new('SinkCut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    try:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(target, depsgraph)
        target.modifiers.remove(mod)
        bm.to_mesh(target.data)
        bm.free()
        target.data.update()
    finally:
        if 'SinkCut' in target.modifiers:
            target.modifiers.remove(target.modifiers['SinkCut'])
        bpy.data.objects.remove(cutter, do_unlink=True)
        bpy.data.meshes.remove(mesh)


# ---------------------------------------------------------------------------
# Range hood
#
# A generic stainless hood on the range hood cage, as an alternative to a
# wood hood. The cage runs from the hood's mounting height to the
# ceiling; the canopy takes the bottom of it and a duct cover the rest.
# The pyramid canopy and the filter are cut to the cage at build time,
# so the prompts rebuild them on a size change (the driven parts follow
# on their own).
# ---------------------------------------------------------------------------

def _cage_dims(cg):
    wrap = _CageWrap(cg.obj)
    return (wrap.get_input('Dim X'), wrap.get_input('Dim Y'),
            wrap.get_input('Dim Z'))


def _hood_lamp(cg, name, lit, metal):
    """A downlight in a canopy's underside: a stainless trim ring around
    a lit lens. Built up from its origin; the caller turns it over."""
    verts, faces = [], []
    smooth, mats = set(), {}
    side, _caps = _revolve(verts, faces,
                           [(inch(1.5), 0.0), (inch(1.5), inch(0.2))])
    smooth.update(side)
    side, caps = _revolve(verts, faces,
                          [(inch(1.1), inch(0.2)), (inch(1.1), inch(0.25))])
    smooth.update(side)
    mats.update({i: 1 for i in side + caps})
    return _mesh_child(cg, name, verts, faces, metal, extra_mats=(lit,),
                       face_mats=mats, smooth_faces=smooth)


def _hood_filter(cg, name, w, d, metal, dark, baffles):
    """The filter in a box canopy's open underside: a dark panel with,
    on a professional hood, stainless baffles hanging below it. Origin
    at the back-left corner of the baffles' bottom edge, built up."""
    verts, faces = [], []
    mats = {}
    t, bh = inch(0.125), inch(0.75) if baffles else 0.0
    _box(verts, faces, 0.0, w, -d, 0.0, bh, bh + t)
    if baffles:
        pitch, bw = inch(1.5), inch(0.5)
        count = max(1, int((w - inch(1.0)) // pitch))
        x0 = (w - ((count - 1) * pitch + bw)) / 2.0
        for i in range(count):
            x = x0 + i * pitch
            mats.update({k: 1 for k in _box(
                verts, faces, x, x + bw, -d + inch(0.75), -inch(0.75),
                0.0, bh)})
    return _mesh_child(cg, name, verts, faces, dark, extra_mats=(metal,),
                       face_mats=mats)


def _pyramid_canopy(cg, name, w, d, h, island, mat, dark, ceiling_z):
    """A chimney hood's canopy: a vertical lip band around the bottom,
    then faces sloping up to the duct cover's footprint -- at the back
    against a wall, centred over an island. The underside is open: a
    recess inside the lip band up to a dark ceiling at ``ceiling_z``,
    where the filter and lamps hang. Cut to the cage at build time."""
    tx0 = (w - HOOD_DUCT_W) / 2.0
    tx1 = tx0 + HOOD_DUCT_W
    if island:
        ty0, ty1 = -(d + HOOD_DUCT_D) / 2.0, -(d - HOOD_DUCT_D) / 2.0
    else:
        ty0, ty1 = -HOOD_DUCT_D, 0.0
    wall = inch(0.5)
    # Rings run clockwise in plan: back-left, back-right, front-right,
    # front-left. Three outside, two inside for the recess.
    rings = [[(0.0, 0.0, 0.0), (w, 0.0, 0.0), (w, -d, 0.0), (0.0, -d, 0.0)],
             [(0.0, 0.0, HOOD_LIP_H), (w, 0.0, HOOD_LIP_H),
              (w, -d, HOOD_LIP_H), (0.0, -d, HOOD_LIP_H)],
             [(tx0, ty1, h), (tx1, ty1, h), (tx1, ty0, h), (tx0, ty0, h)],
             [(wall, -wall, 0.0), (w - wall, -wall, 0.0),
              (w - wall, -d + wall, 0.0), (wall, -d + wall, 0.0)],
             [(wall, -wall, ceiling_z), (w - wall, -wall, ceiling_z),
              (w - wall, -d + wall, ceiling_z), (wall, -d + wall, ceiling_z)]]
    verts = [v for ring in rings for v in ring]
    faces = []
    for r in range(2):                    # lip band, then the slopes
        a, b = r * 4, (r + 1) * 4
        for i in range(4):
            j = (i + 1) % 4
            faces.append((a + j, a + i, b + i, b + j))
    faces.append((11, 10, 9, 8))          # top, facing up
    for i in range(4):                    # bottom edge of the wall
        j = (i + 1) % 4
        faces.append((i, j, 12 + j, 12 + i))
    for i in range(4):                    # inside of the wall, facing in
        j = (i + 1) % 4
        faces.append((12 + i, 12 + j, 16 + j, 16 + i))
    faces.append((16, 17, 18, 19))        # recess ceiling, facing down
    return _mesh_child(cg, name, verts, faces, mat, extra_mats=(dark,),
                       face_mats={len(faces) - 1: 1})


def _build_hood(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    lit = _display_material()
    style = opts.get('hood_style', 'PRO')
    w, d, total_h = _cage_dims(cg)
    canopy_h = float(opts.get('canopy_height', 0.0)) or _HOOD_CANOPY_H.get(
        style, inch(18.0))
    if total_h > 0.0:
        canopy_h = min(canopy_h, total_h)
    duct_h = 'max(dim_z - %f, 0.0)' % canopy_h
    # Every style hangs its filter in a recess under the canopy, with
    # the lamps on the recess ceiling beside it.
    recess = inch(1.5)
    baffles = bool(opts.get('baffles', True))
    filter_h = (inch(0.75) if baffles else 0.0) + inch(0.125)
    lamp_z = recess + filter_h
    # The lamps take a strip across the front of the recess; the filter
    # stops short of it, so the two never share the same patch.
    lamps = bool(opts.get('lamps', True))
    lamp_strip = inch(4.5) if lamps else 0.0

    if style in ('CHIMNEY', 'ISLAND'):
        island = style == 'ISLAND'
        _pyramid_canopy(cg, "Hood Canopy", w, d, canopy_h, island, mat, dark,
                        recess + filter_h)
        filt = _hood_filter(cg, "Hood Filter", w - inch(2.0),
                            d - inch(2.0) - lamp_strip, metal, dark, baffles)
        filt.location = (inch(1.0), -inch(1.0), recess)
        y_duct = ('-dim_y * 0.5 + %f' % (HOOD_DUCT_D / 2.0) if island
                  else 0.0)
        _flat(cg, "Hood Duct Cover", 'dim_x * 0.5 - %f' % (HOOD_DUCT_W / 2.0),
              y_duct, canopy_h, HOOD_DUCT_W, HOOD_DUCT_D, duct_h, mat)
    else:
        # A box canopy open underneath, with the filter recessed in it.
        t = HOOD_PANEL_T
        _front(cg, "Hood Front", 0.0, 0.0, 'dim_x', canopy_h, t, mat)
        _side(cg, "Hood Left", 0.0, 0.0, 0.0, canopy_h, 'dim_y', t, mat)
        _side(cg, "Hood Right", 'dim_x', 0.0, 0.0, canopy_h, 'dim_y', t, mat,
              plus_x=False)
        _flat(cg, "Hood Top", 0.0, 0.0, canopy_h, 'dim_x', 'dim_y', t, mat,
              down=True)
        filt = _hood_filter(cg, "Hood Filter", w - 2.0 * t,
                            d - 2.0 * t - lamp_strip, metal, dark, baffles)
        filt.location = (t, -t, recess)
        _front(cg, "Hood Controls", 'dim_x - %f' % inch(9.0), inch(0.75),
               inch(7.0), inch(1.0), inch(0.0625), dark, proud=True)
        if style == 'PRO':
            _flat(cg, "Hood Duct Cover", inch(1.0), 0.0, canopy_h,
                  'dim_x - %f' % inch(2.0), 'dim_y - %f' % inch(3.0), duct_h,
                  mat)

    if lamps:
        for i, fx in enumerate((0.25, 0.75)):
            obj = _hood_lamp(cg, "Hood Lamp %d" % (i + 1), lit, metal)
            # Built up from its origin; turned over to hang below it.
            obj.rotation_euler.x = math.pi
            obj.location.z = lamp_z
            wrap = _CageWrap(obj)
            wrap.driver_location('x', 'dim_x * %f' % fx, [cg.dim_x])
            wrap.driver_location('y', '-dim_y + %f' % (inch(1.0) + lamp_strip / 2.0),
                                 [cg.dim_y])


def _drop_wood_hood(cage_obj):
    """A generic hood model and a wood hood cannot share a cage: building
    the model takes the wood hood down."""
    try:
        from . import wood_hoods
    except Exception:
        return
    if cage_obj.get(wood_hoods.HOOD_STYLE_PROP):
        wood_hoods.remove_wood_hood(cage_obj)


def drop_model_for_wood_hood(cage_obj):
    """The other direction, called by the wood hoods when one is built:
    the model comes off, and the cage remembers it chose None so the
    Show Model switch leaves it alone."""
    remove_geometry(cage_obj)
    opts = merged_opts(cage_obj)
    opts['model_style'] = 'NONE'
    set_opts(cage_obj, opts)


# ---------------------------------------------------------------------------
# Range
# ---------------------------------------------------------------------------

# Burner centers as fractions of (dim_x, dim_y).
_BURNER_LAYOUTS = {
    4: ((0.27, 0.30), (0.73, 0.30), (0.27, 0.72), (0.73, 0.72)),
    5: ((0.20, 0.28), (0.80, 0.28), (0.50, 0.50),
        (0.20, 0.75), (0.80, 0.75)),
    6: ((0.19, 0.28), (0.50, 0.28), (0.81, 0.28),
        (0.19, 0.75), (0.50, 0.75), (0.81, 0.75)),
}

def _build_burners(cg, opts, dark, top='dim_z', y_scale=1.0):
    """The burners and, for gas, their grates on a cooking surface at
    ``top``. ``y_scale`` pulls the layout toward the back, for a
    cooktop whose knobs take the front of the surface."""
    style = opts.get('burner_style', 'GAS')
    count = int(opts.get('burner_count', 5))
    layout = [(fx, fy * y_scale) for fx, fy in
              _BURNER_LAYOUTS.get(count, _BURNER_LAYOUTS[5])]
    if style == 'ELECTRIC':
        coil = _coil_material()
        make = lambda name: _electric_burner(cg, name, coil, dark)
    elif style == 'INDUCTION':
        print_mat = _print_material()
        make = lambda name: _induction_mark(cg, name, print_mat)
    else:
        brass, metal = _brass_material(), _metal_material()
        make = lambda name: _gas_burner(cg, name, brass, metal)
    for i, (fx, fy) in enumerate(layout):
        wrap = _CageWrap(make("Burner %d" % (i + 1)))
        # Fixed shape, driven position: burners spread with the cooktop
        # but never grow.
        wrap.driver_location('x', 'dim_x * %f' % fx, [cg.dim_x])
        wrap.driver_location('y', '-dim_y * %f' % fy, [cg.dim_y])
        wrap.driver_location('z', top, [cg.dim_z])
    if style not in ('ELECTRIC', 'INDUCTION'):
        _build_gas_grates(cg, layout, _iron_material(), top,
                          GRATE_FRONT * y_scale)


# ---------------------------------------------------------------------------
# Cooktop
#
# Like the sink, the cage top is the countertop's top surface: the
# body drops through the counter into the cabinet and the top plate
# sits on the counter, carrying the range's burners and, for gas, a row
# of knobs along its front.
# ---------------------------------------------------------------------------

def _build_cooktop(cage_obj, opts):
    cg = _Cage(cage_obj)
    mat = _finish_material(opts)
    dark = _dark_material()
    metal = _metal_material()
    style = opts.get('burner_style', 'GAS')
    lip = COOKTOP_LIP
    _flat(cg, "Cooktop Body", lip, -lip, 0.0, 'dim_x - %f' % (2.0 * lip),
          'dim_y - %f' % (2.0 * lip), 'dim_z + %f' % SINK_SEAT, dark)
    _flat(cg, "Cooktop", 0.0, 0.0, 'dim_z + %f' % SINK_SEAT, 'dim_x', 'dim_y',
          COOKTOP_PLATE_T, mat if style == 'GAS' else dark)
    top = 'dim_z + %f' % (SINK_SEAT + COOKTOP_PLATE_T)
    if style == 'GAS':
        # The burners keep clear of a strip along the front where the
        # knobs stand up out of the plate.
        _build_burners(cg, opts, dark, top, y_scale=0.8)
        count = int(opts.get('knob_count', 0))
        margin = 0.08
        for i in range(count):
            frac = margin + (1.0 - 2.0 * margin) * (i + 0.5) / count
            wrap = _CageWrap(_knob(cg, "Cooktop Knob %d" % (i + 1), metal,
                                   dark))
            wrap.driver_location('x', 'dim_x * %f' % frac, [cg.dim_x])
            wrap.driver_location('y', '-dim_y + %f' % inch(2.0), [cg.dim_y])
            wrap.driver_location('z', top, [cg.dim_z])
    else:
        _build_burners(cg, opts, dark, top)
    if any(c.get(SINK_CUTTER_FLAG) for c in cage_obj.children):
        sink_clearance_cutter(cage_obj)
    refresh_countertops()


def _build_knobs(cg, opts, metal, dark, control_h):
    count = int(opts.get('knob_count', 0))
    if count <= 0 or control_h <= 0.0:
        return
    # Two groups, either side of the display: the burner knobs to the
    # left, the oven's to the right. Each group runs from a margin at
    # the panel's end in to a fixed clearance from the display, so the
    # knobs spread with the range while the display stays put.
    margin = 0.07
    clear = DISPLAY_W / 2.0 + inch(1.5)
    left = (count + 1) // 2
    number = 0
    for size, mirrored in ((left, False), (count - left, True)):
        for k in range(size):
            t = (k + 0.5) / size
            frac = margin + t * (0.5 - margin)
            if mirrored:
                x = 'dim_x * %f + %f' % (1.0 - frac, t * clear)
            else:
                x = 'dim_x * %f - %f' % (frac, t * clear)
            number += 1
            obj = _knob(cg, "Range Knob %d" % number, metal, dark)
            # The knob builds along +Z; stand it up so it points forward.
            obj.rotation_euler.x = math.radians(90)
            wrap = _CageWrap(obj)
            wrap.driver_location('x', x, [cg.dim_x])
            wrap.driver_location('y', '-dim_y', [cg.dim_y])
            wrap.driver_location(
                'z', 'dim_z - %f' % (COOKTOP_T + control_h * 0.5),
                [cg.dim_z])
    obj = _display(cg, "Range Display", dark, _display_material())
    obj.rotation_euler.x = math.radians(90)
    wrap = _CageWrap(obj)
    wrap.driver_location('x', 'dim_x * 0.5', [cg.dim_x])
    wrap.driver_location('y', '-dim_y', [cg.dim_y])
    wrap.driver_location(
        'z', 'dim_z - %f' % (COOKTOP_T + control_h * 0.5), [cg.dim_z])


def _oven_window(cg, name, x, width, z, height, dark):
    """The window in an oven door: a dark glass band the full width of
    the door, barely proud of its face. It stops short of the top edge
    to leave the handle its own band of steel, and of the bottom edge
    for the door's lower rail."""
    inset_top = inch(4.0)
    inset_bottom = inch(3.0)
    _front(cg, "%s Window" % name, x, _add(z, inset_bottom), width,
           _sub(height, inset_top + inset_bottom), inch(0.0625), dark,
           proud=True)


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
    _flat(cg, "Cooktop", 0.0, 0.0, 'dim_z', 'dim_x', 'dim_y - %f' % LIP_W,
          COOKTOP_T, dark if opts.get('burner_style') == 'INDUCTION' else mat,
          down=True)
    # The cooktop is a tray: a lip stands up around its sides and back,
    # and its front edge rolls out proud of the panel below. The back
    # lip gives way to a backguard where there is one.
    _flat(cg, "Cooktop Front Lip", 0.0, '-dim_y + %f' % LIP_W,
          'dim_z - %f' % COOKTOP_T, 'dim_x', LIP_W + LIP_PROUD,
          COOKTOP_T + LIP_RISE, mat)
    _flat(cg, "Cooktop Left Lip", 0.0, 0.0, 'dim_z', LIP_W,
          'dim_y - %f' % LIP_W, LIP_RISE, mat)
    _flat(cg, "Cooktop Right Lip", 'dim_x - %f' % LIP_W, 0.0, 'dim_z', LIP_W,
          'dim_y - %f' % LIP_W, LIP_RISE, mat)
    if backguard_h <= 0.0:
        _flat(cg, "Cooktop Back Lip", LIP_W, 0.0, 'dim_z',
              'dim_x - %f' % (2.0 * LIP_W), LIP_W, LIP_RISE, mat)

    # Control panel across the front, under the cooktop, in the body
    # finish: the knobs and the display are what mark it out.
    if control_h > 0.0:
        _front(cg, "Range Controls", 0.0,
               'dim_z - %f' % (COOKTOP_T + control_h), 'dim_x', control_h,
               door_t, mat)
    _build_knobs(cg, opts, metal, dark, control_h)

    # Storage / warming drawer at the bottom, when there is one. It has
    # no handle: on a real range the drawer front is a plain panel that
    # pulls on its top edge, and a bar there fights the oven handle.
    oven_z = 0.0
    if drawer_h > 0.0:
        _front(cg, "Range Drawer", 0.0, 0.0, 'dim_x', drawer_h, door_t, mat)
        oven_z = drawer_h + GAP

    # Oven doors fill what is left between the drawer and the controls.
    doors = max(1, int(opts.get('oven_doors', 1)))
    span = 'dim_z - %f' % (COOKTOP_T + control_h + oven_z + GAP)
    if doors == 1:
        _front(cg, "Oven Door", 0.0, oven_z, 'dim_x', span, door_t, mat)
        _oven_window(cg, "Oven Door", 0.0, 'dim_x', oven_z, span, dark)
        _bar_handle(cg, "Oven Handle", opts, metal, inch(2.0),
                    _sub(_add(oven_z, span), inch(3.0)),
                    'dim_x - %f' % inch(4.0), False)
    else:
        # A double oven sits side by side, each door the full height.
        # The small oven is on the right at its set width and the large
        # one takes the rest, unless the range is wide enough for two
        # full-size ovens, when they split evenly. A width of 0 always
        # splits evenly. Decided in the driver, so a width change
        # re-decides it without a rebuild.
        small = float(opts.get('small_oven_width', inch(18.0)))
        even = '(dim_x - %f) * 0.5' % GAP
        if small > 0.0:
            # A nominal 60 counts: the gap comes out of the ovens.
            full_pair = 2.0 * SMALL_OVEN_EVEN_AT - inch(0.01)
            large = '(dim_x - %f) if dim_x < %f else (%s)' % (
                small + GAP, full_pair, even)
            widths = (large, '%f if dim_x < %f else (%s)' % (
                small, full_pair, even))
        else:
            widths = (even, even)
        x = 0.0
        for i, width in enumerate(widths[:doors]):
            name = "Oven Door %d" % (i + 1)
            _front(cg, name, x, oven_z, width, span, door_t, mat)
            _oven_window(cg, name, x, width, oven_z, span, dark)
            _bar_handle(cg, "%s Handle" % name, opts, metal,
                        _add(x, inch(2.0)),
                        _sub(_add(oven_z, span), inch(3.0)),
                        _sub(width, inch(4.0)), False)
            x = _add(_add(x, width), GAP)

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
    'SINK': _build_sink,
    'COOKTOP': _build_cooktop,
    'WALL_OVEN': _build_wall_oven,
    'MICROWAVE': _build_microwave,
    'HOOD': _build_hood,
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
    # Record what this build is for before anything can return early: a
    # cage with no model has no front of its own either way, so it
    # matches whatever the panels are doing.
    cage_obj[MODEL_PANEL_READY_FLAG] = is_panel_ready(cage_obj)
    if not supports(cage_obj) or stored_opts(cage_obj) is None:
        _refresh_own_clearance(cage_obj)
        return False
    opts = merged_opts(cage_obj)
    if opts.get('model_style', 'NONE') == 'NONE':
        _refresh_own_clearance(cage_obj)
        return False
    builder = _BUILDERS.get(appliance_type(cage_obj))
    if builder is None:
        return False
    if appliance_type(cage_obj) == 'HOOD':
        _drop_wood_hood(cage_obj)
    builder(cage_obj, opts)
    # A model built while the scene is showing cages lands hidden, so
    # the switch means the same thing for new and existing appliances.
    if not models_shown():
        for child in _geo_children(cage_obj):
            _set_hidden(child, True)
    refresh_labels(cage_obj)
    _refresh_own_clearance(cage_obj)
    return True


def _refresh_own_clearance(cage_obj):
    if any(c.get(SINK_CUTTER_FLAG) for c in cage_obj.children):
        refresh_clearance_cuts(cage_obj=cage_obj)


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
    size_from_cabinet: BoolProperty(
        name="Size From Cabinet",
        description="Let the cabinet size this appliance to its opening; "
                    "off keeps the size set here and the cabinet only "
                    "centres it")  # type: ignore
    front_style: EnumProperty(name="Front", items=FRONT_STYLE_ITEMS,
                              default='APPLIANCE')  # type: ignore
    finish: EnumProperty(name="Finish", items=FINISH_ITEMS,
                         default='STAINLESS')  # type: ignore
    handle_style: EnumProperty(name="Handles", items=HANDLE_ITEMS,
                               default='BAR')  # type: ignore

    # Wall oven / microwave
    knobs: BoolProperty(
        name="Knobs", description="A knob either side of the "
                                  "readout")  # type: ignore
    trim_kit: BoolProperty(
        name="Trim Kit", description="A stainless frame around the "
                                     "microwave's face")  # type: ignore

    # Sink
    sink_style: EnumProperty(name="Style", items=SINK_STYLE_ITEMS,
                             default='SINGLE')  # type: ignore
    drain_side: EnumProperty(name="Drain", items=DRAIN_SIDE_ITEMS,
                             default='CENTER')  # type: ignore
    mount: EnumProperty(name="Mount", items=SINK_MOUNT_ITEMS,
                        default='UNDERMOUNT')  # type: ignore
    faucet: BoolProperty(
        name="Faucet", description="A gooseneck faucet on the back "
                                   "deck")  # type: ignore
    counter_thickness: FloatProperty(
        name="Counter Thickness", unit='LENGTH', precision=5, min=0.0,
        description="The countertop, which takes the top of the sink's "
                    "cage: an undermount's rim sits under it, a drop-in's "
                    "flange on it, and the faucet stands on it")  # type: ignore
    bowl_depth: FloatProperty(
        name="Bowl Depth", unit='LENGTH', precision=5, min=0.0,
        description="Rim to bowl floor; 0 fills the sink's cage. A "
                    "farmhouse apron runs from the floor to the counter "
                    "top, so this sets its height too")  # type: ignore

    # Range hood
    hood_style: EnumProperty(name="Style", items=HOOD_STYLE_ITEMS,
                             default='CHIMNEY')  # type: ignore
    canopy_height: FloatProperty(
        name="Canopy Height", unit='LENGTH', precision=5, min=0.0,
        description="Height of the canopy at the bottom of the hood; the "
                    "duct cover takes the rest up to the ceiling. 0 uses "
                    "the style's own height")  # type: ignore
    baffles: BoolProperty(
        name="Baffle Filters",
        description="Stainless baffles in the filter opening")  # type: ignore
    lamps: BoolProperty(
        name="Lamps", description="Two downlights in the underside")  # type: ignore

    # Refrigerator
    fridge_config: EnumProperty(name="Configuration",
                                items=FRIDGE_CONFIG_ITEMS,
                                default='FRENCH')  # type: ignore
    grille_position: EnumProperty(name="Grille",
                                  items=GRILLE_POSITION_ITEMS,
                                  default='TOP')  # type: ignore
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
        description="1 for a single oven, 2 for a double with the "
                    "ovens side by side")  # type: ignore
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
    small_oven_width: FloatProperty(
        name="Small Oven", unit='LENGTH', precision=5, min=0.0,
        description="Width of the smaller oven of a double, on the "
                    "right. 0 splits the two evenly, as does a range "
                    "wide enough for two full-size ovens")  # type: ignore

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
        self.front_style = ('CABINET' if is_panel_ready(self.appliance)
                            else 'APPLIANCE')
        for key, value in merged_opts(self.appliance).items():
            if hasattr(self, key):
                try:
                    setattr(self, key, value)
                except (TypeError, ValueError):
                    pass
        self.size_from_cabinet = not self.appliance.get(SIZE_OWNED_FLAG)
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
        if self.appliance.get(CABINET_APPLIANCE_FLAG):
            # Typing a size takes it over from the cabinet; the checkbox
            # hands it back.
            was = (cage.get_input('Dim X'), cage.get_input('Dim Z'),
                   cage.get_input('Dim Y'))
            now = (self.appliance_width, self.appliance_height,
                   self.appliance_depth)
            if any(abs(a - b) > 1e-6 for a, b in zip(was, now)):
                self.size_from_cabinet = False
            if self.size_from_cabinet:
                self.appliance.pop(SIZE_OWNED_FLAG, None)
            else:
                self.appliance[SIZE_OWNED_FLAG] = True
        cage.set_input('Dim X', self.appliance_width)
        cage.set_input('Dim Z', self.appliance_height)
        cage.set_input('Dim Y', self.appliance_depth)

        # Cabinet door panels are solved from the cage rather than
        # driven, so they have to be re-solved against the size just
        # pushed. rebuild only tears parts down on a structural change,
        # so it is safe to call this often.
        panels = _panels_module() if supports_panels(self.appliance) else None
        if panels is not None:
            want = self.front_style == 'CABINET'
            if want != is_panel_ready(self.appliance):
                set_front_style(self.appliance, self.front_style)
            elif want:
                panels.rebuild(self.appliance)

        # The model itself is another matter. check() fires on every
        # dialog interaction, and each rebuild removes and recreates part
        # objects; doing that on every mouse move destabilizes the draw
        # cache -- the same crash wood_hoods guards against -- so only
        # rebuild when the options actually changed.
        opts = self._opts_dict()
        key = repr(sorted(opts.items())) + '|' + self.front_style
        if appliance_type(self.appliance) == 'HOOD':
            # The canopy and filter are cut to the cage at build time,
            # so a size change is a rebuild too.
            key += '|%.5f,%.5f,%.5f' % (self.appliance_width,
                                        self.appliance_height,
                                        self.appliance_depth)
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
        if self.appliance.get(CABINET_APPLIANCE_FLAG):
            col.prop(self, 'size_from_cabinet')

        box = layout.box()
        col = box.column(align=True)
        col.prop(self, 'model_style')
        if self.model_style == 'NONE':
            col.label(text="The appliance stays a wireframe box.",
                      icon='INFO')
            return
        col.prop(self, 'finish')
        if appl not in ('HOOD', 'SINK', 'COOKTOP'):
            col.prop(self, 'handle_style')

        if supports_panels(self.appliance):
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Front:")
            col.row(align=True).prop(self, 'front_style', expand=True)
            if self.front_style == 'CABINET':
                col.separator()
                col.operator("hb_face_frame.add_appliance_panels",
                             text="Edit Panels...", icon='MOD_SOLIDIFY')

        if self.front_style == 'CABINET' and supports_panels(self.appliance):
            box = layout.box()
            box.label(text="The appliance builds its box only; the fronts "
                           "are cabinet panels.", icon='INFO')
            return

        box = layout.box()
        col = box.column(align=True)
        if appl == 'COOKTOP':
            col.prop(self, 'burner_style')
            col.prop(self, 'burner_count')
            if self.burner_style == 'GAS':
                col.prop(self, 'knob_count')
            col.prop(self, 'counter_thickness')
        elif appl == 'WALL_OVEN':
            col.prop(self, 'knobs')
        elif appl == 'MICROWAVE':
            col.prop(self, 'trim_kit')
        elif appl == 'SINK':
            col.prop(self, 'sink_style')
            if self.sink_style != 'DOUBLE':
                col.row(align=True).prop(self, 'drain_side', expand=True)
            col.row(align=True).prop(self, 'mount', expand=True)
            col.prop(self, 'faucet')
            col.prop(self, 'counter_thickness')
            col.prop(self, 'bowl_depth')
        elif appl == 'HOOD':
            col.prop(self, 'hood_style')
            col.prop(self, 'canopy_height')
            col.prop(self, 'baffles')
            col.prop(self, 'lamps')
        elif appl == 'REFRIGERATOR':
            col.prop(self, 'fridge_config')
            if self.fridge_config == 'SIDE_BY_SIDE':
                col.prop(self, 'freezer_fraction')
            else:
                col.prop(self, 'freezer_height')
                if self.fridge_config in {'FRENCH', 'SINGLE'}:
                    col.prop(self, 'freezer_drawers')
            col.separator()
            col.row(align=True).prop(self, 'grille_position', expand=True)
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
            if self.oven_doors > 1:
                col.prop(self, 'small_oven_width')
            col.prop(self, 'drawer_height')
            col.separator()
            col.prop(self, 'control_height')
            col.prop(self, 'knob_count')
            col.prop(self, 'backguard_height')


_CLASSES = (
    HOME_BUILDER_OT_appliance_prompts,
)


@bpy.app.handlers.persistent
def _hidden_models_load_post(_dummy):
    """Re-assert the Show Model switch on every room of a file opened.

    Files saved before the switch covered render visibility carry models
    that are hidden on screen but not in a render, so they still print.
    Only the switched-off rooms are touched, and only to hide: nothing
    is built and a room showing its models is left alone.
    """
    for scene in bpy.data.scenes:
        if models_shown(scene):
            continue
        for obj in scene.objects:
            if obj.get(GEO_CHILD_FLAG) and not obj.hide_render:
                _set_hidden(obj, True)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    if _hidden_models_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_hidden_models_load_post)


def unregister():
    if _hidden_models_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_hidden_models_load_post)
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
