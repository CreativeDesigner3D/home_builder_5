"""Python solver for frameless cabinets and products.

A cabinet's parts used to hold their position, size and visibility in
Blender drivers reading the cage's dimensions and prompts. Drivers evaluate
in an order the cabinet cannot control, need a forced re-evaluation pass to
settle after a prompt edit, and only come back from a saved file once every
target they reference has -- so a saved cabinet could reopen with parts
collapsed onto the origin or missing. The solver reads the same inputs and
writes the same values as plain object data that a file round-trips
unchanged.

``recalculate_cabinet`` solves the carcass: sides, bottom, back, toe kick,
top and stretchers, the bay cage and the toe kick extras. Everything below
the bay is still driven from the bay's dimensions, which the solver writes,
so the two mechanisms meet at the bay.

Shared helpers here are also used by the product solvers in
``types_products``.
"""

import bpy
import re
import traceback
from ... import hb_utils
from ...hb_types import GeoNodeCage, GeoNodeCutpart, CabinetPartModifier
from ...units import inch


# Role tag written on every solved part. The solver finds its parts by role
# each pass, which survives a rename or a duplicate where matching on the
# object name does not.
PART_ROLE_KEY = 'hb_part_role'

# Which carcass a cabinet cage was built as: BASE, TALL, UPPER or
# LAP_DRAWER. Cages from before the tag are typed from CABINET_TYPE.
CARCASS_KEY = 'CARCASS'

# Corner notch modifier on a notched side.
NOTCH_MOD_NAME = 'Notch'

# Cabinets built before the role tag are matched on the names their parts
# were created with, so an older job upgrades in place on first solve. A
# legacy part has to carry the tag its kind was created with and a driver
# -- an untouched part of some other kind that happens to share a name is
# left alone.
CARCASS_LEGACY_NAMES = {
    'Left Side': ('LEFT_SIDE', 'CABINET_PART'),
    'Right Side': ('RIGHT_SIDE', 'CABINET_PART'),
    'Bottom': ('BOTTOM', 'CABINET_PART'),
    'Back': ('BACK', 'CABINET_PART'),
    'Toe Kick': ('TOE_KICK', 'CABINET_PART'),
    'Top': ('TOP', 'CABINET_PART'),
    'Front Stretcher': ('FRONT_STRETCHER', 'CABINET_PART'),
    'Back Stretcher': ('BACK_STRETCHER', 'CABINET_PART'),
    'Sink Apron': ('SINK_APRON', 'CABINET_PART'),
    'Bay': ('BAY', 'IS_FRAMELESS_BAY_CAGE'),
    'Ladder Base': ('LADDER_BASE', 'IS_FRAMELESS_LADDER_CAGE'),
    'Leg Leveler FL': ('LEG_LEVELER_FL', 'IS_LEG_LEVELER'),
    'Leg Leveler FR': ('LEG_LEVELER_FR', 'IS_LEG_LEVELER'),
    'Leg Leveler BL': ('LEG_LEVELER_BL', 'IS_LEG_LEVELER'),
    'Leg Leveler BR': ('LEG_LEVELER_BR', 'IS_LEG_LEVELER'),
}

# Base Top Construction prompt: index into ["Full Top", "Stretchers", "Sink"].
TOP_FULL, TOP_STRETCHERS, TOP_SINK = 0, 1, 2


# ---------------------------------------------------------------------------
# Shared part writers
# ---------------------------------------------------------------------------

def clear_drivers(obj):
    """Drop every driver on ``obj``.

    A part built before the solver carries a driver on its location, each
    geometry-node size input and its visibility. The solver writes those
    same values directly, and a leftover driver would overwrite the written
    value on the next depsgraph evaluation -- so the old drivers have to go
    before the first solve. Parts built by the solver have no animation
    data at all, which makes this a no-op.
    """
    anim = obj.animation_data
    if anim is None:
        return
    for fcurve in list(anim.drivers):
        try:
            anim.drivers.remove(fcurve)
        except (RuntimeError, ReferenceError):
            pass
    if anim.action is None and not anim.nla_tracks:
        obj.animation_data_clear()


def has_drivers(obj):
    anim = obj.animation_data
    return anim is not None and len(anim.drivers) > 0


def set_part(part_obj, location, length=None, width=None, thickness=None,
             visible=True):
    """Write one part's position, size and visibility.

    Sizes are clamped at zero: a board whose neighbours eat more than the
    span it sits in has nothing left, and a negative length would build
    the part inside out rather than not at all.
    """
    part = GeoNodeCutpart(part_obj)
    part_obj.location = location
    if length is not None:
        part.set_input('Length', max(length, 0.0))
    if width is not None:
        part.set_input('Width', max(width, 0.0))
    if thickness is not None:
        part.set_input('Thickness', max(thickness, 0.0))
    part_obj.hide_viewport = not visible
    part_obj.hide_render = not visible


def set_cage(cage_obj, location, dim_x=None, dim_y=None, dim_z=None):
    """Write a cage's position and dimensions."""
    cage = GeoNodeCage(cage_obj)
    cage_obj.location = location
    if dim_x is not None:
        cage.set_input('Dim X', max(dim_x, 0.0))
    if dim_y is not None:
        cage.set_input('Dim Y', max(dim_y, 0.0))
    if dim_z is not None:
        cage.set_input('Dim Z', max(dim_z, 0.0))


def set_modifier(part_obj, mod_name, inputs=(), visible=None):
    """Write a part modifier's node inputs and visibility. No-op when the
    part has no such modifier (an older build, or an applied part)."""
    mod = part_obj.modifiers.get(mod_name)
    if mod is None or mod.type != 'NODES' or mod.node_group is None:
        return
    cpm = CabinetPartModifier(part_obj)
    cpm.mod = mod
    for name, value in inputs:
        try:
            cpm.set_input(name, value)
        except (KeyError, AttributeError, ValueError):
            pass
    if visible is not None:
        mod.show_viewport = visible
        mod.show_render = visible


def set_array(part_obj, mod_name, count, offset_z):
    """Lay a part out ``count`` times along its own Z."""
    array_mod = part_obj.modifiers.get(mod_name)
    if array_mod is None or array_mod.type != 'ARRAY':
        return
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace = (0.0, 0.0, offset_z)
    array_mod.count = max(count, 1)


def prompt(obj, name, default):
    value = obj.get(name, default)
    return default if value is None else value


# ---------------------------------------------------------------------------
# Cabinet lookup
# ---------------------------------------------------------------------------

def cabinet_root(obj):
    """The frameless cabinet cage at or above ``obj``, or None."""
    while obj is not None:
        if obj.get('IS_FRAMELESS_CABINET_CAGE'):
            return obj
        obj = obj.parent
    return None


def carcass_kind(root):
    kind = root.get(CARCASS_KEY)
    if kind:
        return kind
    cabinet_type = root.get('CABINET_TYPE')
    if cabinet_type == 'UPPER':
        return 'UPPER'
    if cabinet_type == 'TALL':
        return 'TALL'
    if cabinet_type == 'BASE':
        # A lap drawer is a base cabinet without a toe kick.
        return 'BASE' if 'Toe Kick Height' in root else 'LAP_DRAWER'
    return None


def is_solved_cabinet(obj):
    """True for a cabinet cage whose carcass the solver owns. Corner
    cabinets are built differently and stay driven for now."""
    return (obj is not None
            and bool(obj.get('IS_FRAMELESS_CABINET_CAGE'))
            and 'CORNER_TYPE' not in obj
            and carcass_kind(obj) in _SOLVERS)


def carcass_parts(root):
    """``{role: object}`` for the carcass parts of one cabinet."""
    parts = {}
    for child in root.children:
        role = child.get(PART_ROLE_KEY)
        if role is None:
            entry = CARCASS_LEGACY_NAMES.get(child.name.split('.')[0])
            if entry is not None and child.get(entry[1]) and has_drivers(child):
                role = entry[0]
        if role is not None and role not in parts:
            parts[role] = child
    return parts


# ---------------------------------------------------------------------------
# Carcass solve
# ---------------------------------------------------------------------------

class _Prompts:
    def __init__(self, root):
        self.mt = float(prompt(root, 'Material Thickness', inch(0.75)))
        self.tkh = float(prompt(root, 'Toe Kick Height', 0.0))
        self.tks = float(prompt(root, 'Toe Kick Setback', 0.0))
        self.rb = bool(prompt(root, 'Remove Bottom', False))
        self.btc = int(prompt(root, 'Base Top Construction', TOP_FULL))
        self.sw = float(prompt(root, 'Stretcher Width', inch(4)))
        self.saw = float(prompt(root, 'Sink Apron Width', inch(7)))
        self.lli = float(prompt(root, 'Leg Leveler Inset', 0.0))


def _solve_sides(parts, p, dim_x, dim_y, dim_z, tkh):
    for role, x in (('LEFT_SIDE', 0.0), ('RIGHT_SIDE', dim_x)):
        part = parts.get(role)
        if part is None:
            continue
        if part.modifiers.get(NOTCH_MOD_NAME) is not None:
            # A notched side runs to the floor with the toe kick cut out
            # of its front bottom corner.
            set_part(part, (x, 0.0, 0.0), length=dim_z, width=dim_y,
                     thickness=p.mt)
            set_modifier(part, NOTCH_MOD_NAME,
                         (('X', tkh), ('Y', p.tks), ('Route Depth', p.mt)))
        else:
            set_part(part, (x, 0.0, tkh), length=dim_z - tkh, width=dim_y,
                     thickness=p.mt)


def _solve_top_options(parts, p, dim_x, dim_y, dim_z, back_stretcher_y):
    inner = dim_x - p.mt * 2.0
    part = parts.get('FRONT_STRETCHER')
    if part is not None:
        set_part(part, (p.mt, -dim_y, dim_z), length=inner, width=p.sw,
                 thickness=p.mt, visible=p.btc == TOP_STRETCHERS)
    part = parts.get('BACK_STRETCHER')
    if part is not None:
        set_part(part, (p.mt, back_stretcher_y, dim_z), length=inner,
                 width=p.sw, thickness=p.mt, visible=p.btc == TOP_STRETCHERS)
    part = parts.get('SINK_APRON')
    if part is not None:
        set_part(part, (p.mt, -dim_y, dim_z), length=inner, width=p.saw,
                 thickness=p.mt, visible=p.btc == TOP_SINK)


def _solve_toe_kick_extras(parts, p, dim_x, dim_y):
    part = parts.get('LADDER_BASE')
    if part is not None:
        set_cage(part, (0.0, -dim_y + p.tks, 0.0), dim_x=dim_x,
                 dim_y=dim_y - p.tks, dim_z=p.tkh)
    lli = p.lli
    for role, x, y in (('LEG_LEVELER_FL', lli, -(dim_y - lli)),
                       ('LEG_LEVELER_FR', dim_x - lli, -(dim_y - lli)),
                       ('LEG_LEVELER_BL', lli, -lli),
                       ('LEG_LEVELER_BR', dim_x - lli, -lli)):
        part = parts.get(role)
        if part is not None:
            part.location = (x, y, 0.0)


def _solve_base(root, parts, p, dim_x, dim_y, dim_z):
    mt, tkh, rb = p.mt, p.tkh, p.rb
    inner = dim_x - mt * 2.0
    _solve_sides(parts, p, dim_x, dim_y, dim_z, tkh)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (mt, 0.0, tkh), length=inner, width=dim_y,
                 thickness=mt, visible=not rb)

    part = parts.get('BACK')
    if part is not None:
        set_part(part, (mt, 0.0, 0.0 if rb else tkh + mt),
                 length=dim_z if rb else dim_z - tkh - mt,
                 width=inner, thickness=mt)

    part = parts.get('TOE_KICK')
    if part is not None:
        set_part(part, (mt, -dim_y + p.tks, 0.0), length=inner, width=tkh,
                 thickness=mt, visible=not rb)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (mt, -mt, dim_z), length=inner, width=dim_y - mt,
                 thickness=mt, visible=p.btc == TOP_FULL)

    _solve_top_options(parts, p, dim_x, dim_y, dim_z, -p.sw - mt)

    bottom_t = 0.0 if rb else mt
    part = parts.get('BAY')
    if part is not None:
        set_cage(part, (mt, -dim_y, tkh + bottom_t), dim_x=inner,
                 dim_y=dim_y - mt, dim_z=dim_z - tkh - bottom_t - mt)

    _solve_toe_kick_extras(parts, p, dim_x, dim_y)


def _solve_tall(root, parts, p, dim_x, dim_y, dim_z):
    mt, tkh, rb = p.mt, p.tkh, p.rb
    inner = dim_x - mt * 2.0
    _solve_sides(parts, p, dim_x, dim_y, dim_z, tkh)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (mt, 0.0, tkh), length=inner, width=dim_y,
                 thickness=mt, visible=not rb)

    part = parts.get('BACK')
    if part is not None:
        set_part(part, (mt, 0.0, 0.0 if rb else tkh + mt),
                 length=(dim_z if rb else dim_z - tkh - mt) - mt,
                 width=inner, thickness=mt)

    part = parts.get('TOE_KICK')
    if part is not None:
        set_part(part, (mt, -dim_y + p.tks, 0.0), length=inner, width=tkh,
                 thickness=mt, visible=not rb)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (mt, 0.0, dim_z), length=inner, width=dim_y,
                 thickness=mt)

    bottom_t = 0.0 if rb else mt
    part = parts.get('BAY')
    if part is not None:
        set_cage(part, (mt, -dim_y, tkh + bottom_t), dim_x=inner,
                 dim_y=dim_y - mt, dim_z=dim_z - tkh - bottom_t - mt)

    _solve_toe_kick_extras(parts, p, dim_x, dim_y)


def _solve_upper(root, parts, p, dim_x, dim_y, dim_z):
    mt = p.mt
    inner = dim_x - mt * 2.0
    _solve_sides(parts, p, dim_x, dim_y, dim_z, 0.0)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (mt, 0.0, 0.0), length=inner, width=dim_y,
                 thickness=mt)

    part = parts.get('BACK')
    if part is not None:
        set_part(part, (mt, 0.0, mt), length=dim_z - mt * 2.0, width=inner,
                 thickness=mt)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (mt, 0.0, dim_z), length=inner, width=dim_y,
                 thickness=mt)

    part = parts.get('BAY')
    if part is not None:
        set_cage(part, (mt, -dim_y, mt), dim_x=inner, dim_y=dim_y - mt,
                 dim_z=dim_z - mt * 2.0)


def _solve_lap_drawer(root, parts, p, dim_x, dim_y, dim_z):
    mt = p.mt
    inner = dim_x - mt * 2.0
    _solve_sides(parts, p, dim_x, dim_y, dim_z, 0.0)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (mt, 0.0, 0.0), length=inner, width=dim_y,
                 thickness=mt)

    part = parts.get('BACK')
    if part is not None:
        # Under a sink apron the back runs up to the top of the box.
        top_t = 0.0 if p.btc == TOP_SINK else mt
        set_part(part, (mt, 0.0, mt), length=dim_z - mt - top_t,
                 width=inner, thickness=mt)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (mt, 0.0, dim_z), length=inner, width=dim_y,
                 thickness=mt, visible=p.btc == TOP_FULL)

    _solve_top_options(parts, p, dim_x, dim_y, dim_z, -p.sw)

    part = parts.get('BAY')
    if part is not None:
        set_cage(part, (mt, -dim_y, mt), dim_x=inner, dim_y=dim_y - mt,
                 dim_z=dim_z - mt * 2.0)


_SOLVERS = {
    'BASE': _solve_base,
    'TALL': _solve_tall,
    'UPPER': _solve_upper,
    'LAP_DRAWER': _solve_lap_drawer,
}


def recalculate_cabinet(obj):
    """Size and place the carcass of the cabinet at or above ``obj``.

    Accepts the cabinet cage or anything under it, so property callbacks
    and menu commands can hand it whatever the user had selected.
    """
    root = cabinet_root(obj)
    if not is_solved_cabinet(root):
        return
    parts = carcass_parts(root)
    if not parts:
        return
    for role, part_obj in parts.items():
        clear_drivers(part_obj)
        # A cabinet matched on its part names carries no tags yet; stamp
        # them now so the next solve finds its parts by tag.
        part_obj[PART_ROLE_KEY] = role
    kind = carcass_kind(root)
    if CARCASS_KEY not in root:
        root[CARCASS_KEY] = kind

    cage = GeoNodeCage(root)
    _SOLVERS[kind](root, parts, _Prompts(root),
                   cage.get_input('Dim X'), cage.get_input('Dim Y'),
                   cage.get_input('Dim Z'))

    bay = parts.get('BAY')
    if bay is not None:
        solve_cage_tree(bay)


# ---------------------------------------------------------------------------
# Below the bay: cage links and splitters
# ---------------------------------------------------------------------------
#
# Every cage under the bay takes its size from the cage above it: an insert
# fills its opening, an interior fills its insert, a splitter fills the bay
# or opening it divides. Splitters then hand each of their openings a share
# of that size from the calculator prompts the user edits. Parts inside an
# insert (fronts, pulls, drawer boxes, shelves) are still driven from the
# insert's dimensions, which are written here.

DIM_INPUTS = ('Dim X', 'Dim Y', 'Dim Z')

SPLITTER_VERTICAL_TAG = 'IS_FRAMELESS_SPLITTER_VERTICAL_CAGE'
SPLITTER_HORIZONTAL_TAG = 'IS_FRAMELESS_SPLITTER_HORIZONTAL_CAGE'

# A child carrying one of these is sized from its parent cage.
CAGE_LINK_TAGS = (
    SPLITTER_VERTICAL_TAG,
    SPLITTER_HORIZONTAL_TAG,
    'IS_FRAMELESS_OPENING_CAGE',
    'IS_FRAMELESS_INTERIOR_CAGE',
)

# Index of an opening or splitter board within its splitter, top to bottom
# or left to right, counted from 1.
SPLIT_INDEX_KEY = 'hb_split_index'

_SPLIT_LEGACY_NAME = re.compile(r'^(Opening|Vertical Splitter|Horizontal Splitter) (\d+)$')


def is_cage_link(obj):
    return any(obj.get(tag) for tag in CAGE_LINK_TAGS)


def cage_dims(cage_obj):
    cage = GeoNodeCage(cage_obj)
    return (cage.get_input('Dim X'), cage.get_input('Dim Y'),
            cage.get_input('Dim Z'))


def clear_input_drivers(obj, names=DIM_INPUTS, location=False):
    """Drop the drivers on the named geometry-node inputs (and the object's
    location) while leaving any other driver on the object alone."""
    anim = obj.animation_data
    if anim is None:
        return
    paths = set()
    mod_name = obj.home_builder.mod_name if hasattr(obj, 'home_builder') else ''
    mod = obj.modifiers.get(mod_name) if mod_name else None
    if mod is not None and mod.node_group is not None:
        for name in names:
            item = mod.node_group.interface.items_tree.get(name)
            if item is not None:
                paths.add(hb_utils.gn_input_data_path(mod, item.identifier))
    for fcurve in list(anim.drivers):
        if fcurve.data_path in paths or (location and fcurve.data_path == 'location'):
            try:
                anim.drivers.remove(fcurve)
            except (RuntimeError, ReferenceError):
                pass
    if not anim.drivers and anim.action is None and not anim.nla_tracks:
        obj.animation_data_clear()


def tag_split_part(obj, role, index):
    obj[PART_ROLE_KEY] = role
    obj[SPLIT_INDEX_KEY] = index


def split_parts(splitter_obj):
    """``{(role, index): object}`` for a splitter's openings and boards."""
    parts = {}
    for child in splitter_obj.children:
        role = child.get(PART_ROLE_KEY)
        index = child.get(SPLIT_INDEX_KEY)
        if role not in ('OPENING', 'SPLITTER') or index is None:
            match = _SPLIT_LEGACY_NAME.match(child.name.split('.')[0])
            if match is None:
                continue
            role = 'OPENING' if match.group(1) == 'Opening' else 'SPLITTER'
            index = int(match.group(2))
        key = (role, int(index))
        if key not in parts:
            parts[key] = child
    return parts


def splitter_calculator(splitter_obj):
    calcs = splitter_obj.home_builder.calculators
    calc = calcs.get('Opening Calculator')
    if calc is None and len(calcs):
        calc = calcs[0]
    return calc


def solve_calculator(calc, total):
    """Share ``total`` among the calculator's prompts: fixed prompts keep
    their value, equal prompts split what is left. Returns the sizes in
    prompt order."""
    if calc.distance_obj is not None:
        clear_drivers(calc.distance_obj)
        calc.distance_obj.home_builder.calculator_distance = total
    fixed = sum(p.distance_value for p in calc.prompts if p.include and not p.equal)
    equal = [p for p in calc.prompts if p.equal]
    included = sum(1 for p in equal if p.include)
    if included:
        share = (total - fixed) / included
        for p in equal:
            p.distance_value = share if p.include else 0.0
    return [p.distance_value for p in calc.prompts]


def _solve_splitter(splitter_obj, vertical):
    parts = split_parts(splitter_obj)
    calc = splitter_calculator(splitter_obj)
    if calc is None or not parts:
        return
    for (role, index), part_obj in parts.items():
        clear_drivers(part_obj)
        tag_split_part(part_obj, role, index)

    dim_x, dim_y, dim_z = cage_dims(splitter_obj)
    mt = float(prompt(splitter_obj, 'Material Thickness', inch(0.75)))
    count = len(calc.prompts)
    span = dim_z if vertical else dim_x
    sizes = solve_calculator(calc, span - mt * (count - 1))

    if vertical:
        # Openings run top to bottom; the last one sits on the floor of
        # the splitter whatever the sizes above it add up to.
        top = dim_z
        for i in range(1, count + 1):
            size = sizes[i - 1]
            opening = parts.get(('OPENING', i))
            if opening is not None:
                z = 0.0 if i == count else top - size
                set_cage(opening, (0.0, 0.0, z), dim_x=dim_x, dim_y=dim_y,
                         dim_z=size)
            board = parts.get(('SPLITTER', i))
            if board is not None:
                set_part(board, (0.0, 0.0, top - size - mt), length=dim_x,
                         width=dim_y, thickness=mt)
            top -= size + mt
    else:
        x = 0.0
        for i in range(1, count + 1):
            size = sizes[i - 1]
            opening = parts.get(('OPENING', i))
            if opening is not None:
                set_cage(opening, (x, 0.0, 0.0), dim_x=size, dim_y=dim_y,
                         dim_z=dim_z)
            board = parts.get(('SPLITTER', i))
            if board is not None:
                set_part(board, (x + size, 0.0, 0.0), length=dim_z,
                         width=dim_y, thickness=mt)
            x += size + mt


def link_dims(parent_obj, child_obj, dims):
    """Where a linked child sits in its parent and how big it is. An
    interior behind an inset front starts behind the front."""
    dim_x, dim_y, dim_z = dims
    if child_obj.get('IS_FRAMELESS_INTERIOR_CAGE') and 'Inset Front' in parent_obj:
        offset = 0.0
        if parent_obj.get('Inset Front'):
            offset = float(prompt(parent_obj, 'Front Thickness', 0.0))
        return (0.0, offset, 0.0), (dim_x, dim_y - offset, dim_z)
    return (0.0, 0.0, 0.0), (dim_x, dim_y, dim_z)


def solve_cage_tree(cage_obj):
    """Size every cage under ``cage_obj`` from the cage above it."""
    dims = cage_dims(cage_obj)
    for child in list(cage_obj.children):
        if not is_cage_link(child):
            continue
        loc, child_dims = link_dims(cage_obj, child, dims)
        clear_input_drivers(child, DIM_INPUTS, location=True)
        set_cage(child, loc, *child_dims)
        if child.get(SPLITTER_VERTICAL_TAG) or child.get(SPLITTER_HORIZONTAL_TAG):
            _solve_splitter(child, bool(child.get(SPLITTER_VERTICAL_TAG)))
            for (role, _index), opening in split_parts(child).items():
                if role == 'OPENING':
                    solve_cage_tree(opening)
        else:
            solve_cage_tree(child)


def attach_cage(child_obj, parent_obj):
    """Parent a cage (insert, splitter, interior) under another cage and
    size everything under the parent."""
    child_obj.parent = parent_obj
    solve_cage_tree(parent_obj)


# ---------------------------------------------------------------------------
# Entry points for callers that settle a hierarchy
# ---------------------------------------------------------------------------

def solve_roots(objects):
    """Solve every cabinet and product that owns one of ``objects``.

    Called before drivers are settled so the parts still driven below a
    solved cage read values that have already landed.
    """
    from . import types_products
    cabinets = {}
    products = {}
    for obj in objects:
        root = cabinet_root(obj)
        if root is not None and root.name not in cabinets:
            cabinets[root.name] = root
        root = types_products.product_root(obj)
        if root is not None and root.name not in products:
            products[root.name] = root
    for root in cabinets.values():
        try:
            recalculate_cabinet(root)
        except Exception:
            traceback.print_exc()
    for root in products.values():
        try:
            types_products.recalculate_product(root)
        except Exception:
            traceback.print_exc()


def upgrade_cabinets(scene=None):
    """Re-solve every cabinet in the file.

    Run on load so a cabinet saved by an older build sheds its carcass
    drivers and comes back at the size it was saved at, rather than
    waiting for something to touch it.
    """
    scenes = [scene] if scene is not None else list(bpy.data.scenes)
    seen = set()
    for scn in scenes:
        for obj in scn.objects:
            if not is_solved_cabinet(obj) or obj.name in seen:
                continue
            seen.add(obj.name)
            try:
                recalculate_cabinet(obj)
            except Exception:
                # One bad cabinet must not stop a file from opening.
                traceback.print_exc()
