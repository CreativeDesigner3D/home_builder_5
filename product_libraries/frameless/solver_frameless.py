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
    # Corner cabinets
    'Left Back': ('LEFT_BACK', 'CABINET_PART'),
    'Right Back': ('RIGHT_BACK', 'CABINET_PART'),
    'Left Toe Kick': ('LEFT_TOE_KICK', 'CABINET_PART'),
    'Right Toe Kick': ('RIGHT_TOE_KICK', 'CABINET_PART'),
    'Left Door': ('LEFT_DOOR', 'IS_DOOR_FRONT'),
    'Right Door': ('RIGHT_DOOR', 'IS_DOOR_FRONT'),
    'Corner Overlay Calc': ('CORNER_OVERLAY', None),
}

# Corner shape modifier on a corner cabinet's top and bottom (one of these).
CORNER_SHAPE_MODS = ('Chamfer', 'Corner Notch')

# Applied end panels hang off the cabinet cage by side.
APPLIED_END_TAGS = (
    ('IS_APPLIED_END_LEFT', 'APPLIED_END_LEFT'),
    ('IS_APPLIED_END_RIGHT', 'APPLIED_END_RIGHT'),
    ('IS_APPLIED_END_BACK', 'APPLIED_END_BACK'),
)
# A slab end runs past the carcass front to sit flush with the fronts:
# the door gap plus the front thickness.
APPLIED_END_EXTENSION = inch(0.875)
# A five-piece end either runs to the floor or stops at the toe kick.
PANEL_TO_FLOOR_KEY = 'Panel To Floor'

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


def clear_modifier_drivers(obj, mod_name):
    """Drop the drivers on one modifier's inputs, leaving the rest."""
    anim = obj.animation_data
    if anim is None:
        return
    prefix = 'modifiers["%s"]' % mod_name
    for fcurve in list(anim.drivers):
        if fcurve.data_path.startswith(prefix):
            try:
                anim.drivers.remove(fcurve)
            except (RuntimeError, ReferenceError):
                pass
    if not anim.drivers and anim.action is None and not anim.nla_tracks:
        obj.animation_data_clear()


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
    if 'CORNER_TYPE' in root:
        return 'CORNER_UPPER' if cabinet_type == 'UPPER' else 'CORNER_BASE'
    if cabinet_type == 'UPPER':
        return 'UPPER'
    if cabinet_type == 'TALL':
        return 'TALL'
    if cabinet_type == 'BASE':
        # A lap drawer is a base cabinet without a toe kick.
        return 'BASE' if 'Toe Kick Height' in root else 'LAP_DRAWER'
    return None


def is_solved_cabinet(obj):
    """True for a cabinet cage whose carcass the solver owns."""
    return (obj is not None
            and bool(obj.get('IS_FRAMELESS_CABINET_CAGE'))
            and carcass_kind(obj) in _SOLVERS)


def carcass_parts(root):
    """``{role: object}`` for the carcass parts of one cabinet."""
    parts = {}
    for child in root.children:
        role = child.get(PART_ROLE_KEY)
        if role is None:
            entry = CARCASS_LEGACY_NAMES.get(child.name.split('.')[0])
            if (entry is not None and has_drivers(child)
                    and (entry[1] is None or child.get(entry[1]))):
                role = entry[0]
        if role is None:
            for tag, end_role in APPLIED_END_TAGS:
                if child.get(tag):
                    role = end_role
                    break
        if role is not None and role not in parts:
            parts[role] = child
    return parts


def _solve_applied_ends(root, parts, p, dim_x, dim_y, dim_z):
    """Applied end panels on the cabinet's outside faces."""
    for role, side in (('APPLIED_END_LEFT', 'LEFT'), ('APPLIED_END_RIGHT', 'RIGHT'),
                       ('APPLIED_END_BACK', 'BACK')):
        part = parts.get(role)
        if part is None:
            continue
        if part.get('IS_APPLIED_PANEL_5PIECE'):
            if PANEL_TO_FLOOR_KEY not in part:
                # An older panel recorded the choice only in where it
                # was built.
                part[PANEL_TO_FLOOR_KEY] = part.location.z <= 1e-6
            to_floor = bool(part.get(PANEL_TO_FLOOR_KEY))
            z = 0.0 if to_floor else p.tkh
            length = dim_z if to_floor else dim_z - p.tkh
            width = dim_y - inch(0.75)
        else:
            z = 0.0
            length = dim_z
            width = dim_y + APPLIED_END_EXTENSION
        visible = not part.hide_viewport
        if side == 'LEFT':
            set_part(part, (0.0, 0.0, z), length=length, width=width, visible=visible)
        elif side == 'RIGHT':
            set_part(part, (dim_x, 0.0, z), length=length, width=width, visible=visible)
        else:
            set_part(part, (0.0, 0.0, 0.0), length=dim_x, width=dim_z, visible=visible)


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


def _solve_corner_shape(root, parts, p, dim_x, dim_y, dim_z):
    """The L-shaped top and bottom, and the pie-cut notch on the cage."""
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))
    for role in ('TOP', 'BOTTOM'):
        part = parts.get(role)
        if part is None:
            continue
        for mod_name in CORNER_SHAPE_MODS:
            set_modifier(part, mod_name,
                         (('X', dim_x - ld - p.mt), ('Y', dim_y - rd - p.mt),
                          ('Route Depth', p.mt + 0.01)))
    # A pie-cut cage carries the same notch so its wireframe reads as an L.
    # The cage keeps whatever else is on it; only the notch's own drivers
    # go, so they cannot overwrite the written values.
    clear_modifier_drivers(root, 'Corner Notch')
    set_modifier(root, 'Corner Notch',
                 (('X', dim_x - ld), ('Y', dim_y - rd), ('Route Depth', dim_z + 0.01)))


def _solve_corner_doors(root, parts, p, dim_x, dim_y, dim_z):
    """Pie-cut doors: one on each face of the notch, hinged at the
    notch corner. Top and bottom overlay the horizontal boards; the outer
    edge overlays the side panel; the two doors meet at the corner."""
    left = parts.get('LEFT_DOOR')
    right = parts.get('RIGHT_DOOR')
    if left is None and right is None:
        return
    mt, tkh = p.mt, p.tkh
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))
    ft = float(prompt(root, 'Front Thickness', inch(0.75)))
    gap = float(prompt(root, 'Door to Cabinet Gap', inch(0.125)))
    inset = bool(root.get('Inset Front', False))
    inset_reveal = float(prompt(root, 'Inset Reveal', inch(0.125)))
    vg = float(prompt(root, 'Vertical Gap', inch(0.125)))

    def overlay(half_key, reveal_key, reveal_default):
        if inset:
            return -inset_reveal
        if root.get(half_key, False):
            return (mt - vg) / 2.0
        return mt - float(prompt(root, reveal_key, reveal_default))

    top = overlay('Half Overlay Top', 'Top Reveal', inch(0.0625))
    bottom = overlay('Half Overlay Bottom', 'Bottom Reveal', 0.0)
    outer = overlay('Half Overlay Outer', 'Outer Reveal', inch(0.0625))

    calc = parts.get('CORNER_OVERLAY')
    if calc is not None:
        calc['Overlay Top'] = top
        calc['Overlay Bottom'] = bottom
        calc['Overlay Outer'] = outer

    bottom_t = 0.0 if p.rb else mt
    y = -rd + ft if inset else -rd - gap
    z = tkh + bottom_t - bottom
    length = dim_z - tkh - bottom_t - mt + top + bottom
    swing = int(prompt(root, 'Door Swing', 0))

    if left is not None:
        x = ld - ft if inset else ld + gap
        width = dim_y - rd + outer if inset else dim_y - rd - mt + outer - gap
        set_part(left, (x, y, z), length=length, width=width, thickness=ft,
                 visible=not left.hide_viewport)
        for pull in left.children:
            if pull.get('IS_CABINET_PULL'):
                _solve_pull(left, pull, length, width, ft, swing == 0)

    if right is not None:
        x = ld + mt - ft - outer if inset else ld + gap * 2.0 + mt
        width = (dim_x - ld - mt + outer * 2.0 if inset
                 else dim_x - ld - mt + outer - gap * 2.0 - mt)
        set_part(right, (x, y, z), length=length, width=width, thickness=ft,
                 visible=not right.hide_viewport)
        for pull in right.children:
            if pull.get('IS_CABINET_PULL'):
                _solve_pull(right, pull, length, width, ft, swing == 1)


def _solve_corner_base(root, parts, p, dim_x, dim_y, dim_z):
    mt, tkh = p.mt, p.tkh
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))

    # Sides: the left wing runs back along -Y, the right wing along +X.
    for role, loc, width in (('LEFT_SIDE', (0.0, -dim_y), ld),
                             ('RIGHT_SIDE', (dim_x, 0.0), rd)):
        part = parts.get(role)
        if part is None:
            continue
        if part.modifiers.get(NOTCH_MOD_NAME) is not None:
            set_part(part, (loc[0], loc[1], 0.0), length=dim_z, width=width,
                     thickness=mt)
            set_modifier(part, NOTCH_MOD_NAME,
                         (('X', tkh), ('Y', p.tks), ('Route Depth', mt)))
        else:
            set_part(part, (loc[0], loc[1], tkh), length=dim_z - tkh,
                     width=width, thickness=mt)

    part = parts.get('LEFT_BACK')
    if part is not None:
        set_part(part, (0.0, 0.0, tkh + mt), length=dim_z - tkh - mt * 2.0,
                 width=dim_y - mt, thickness=mt)

    part = parts.get('RIGHT_BACK')
    if part is not None:
        set_part(part, (mt, 0.0, tkh + mt), length=dim_x - mt * 2.0,
                 width=dim_z - tkh - mt * 2.0, thickness=mt)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (0.0, 0.0, tkh), length=dim_x - mt, width=dim_y - mt,
                 thickness=mt)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (0.0, 0.0, dim_z), length=dim_x - mt, width=dim_y - mt,
                 thickness=mt)

    part = parts.get('LEFT_TOE_KICK')
    if part is not None:
        set_part(part, (ld - p.tks, -dim_y + mt, 0.0),
                 length=dim_y - rd - mt + p.tks, width=tkh, thickness=mt)

    part = parts.get('RIGHT_TOE_KICK')
    if part is not None:
        set_part(part, (dim_x - mt, -rd + p.tks, 0.0),
                 length=dim_x - ld - mt + p.tks, width=tkh, thickness=mt)

    part = parts.get('LADDER_BASE')
    if part is not None:
        set_cage(part, (0.0, 0.0, 0.0), dim_x=dim_x, dim_y=dim_y, dim_z=tkh)

    lli = p.lli
    for role, x, y in (('LEG_LEVELER_BL', lli, -(dim_y - lli)),
                       ('LEG_LEVELER_BR', dim_x - lli, -lli),
                       ('LEG_LEVELER_FL', ld, -(dim_y - lli)),
                       ('LEG_LEVELER_FR', dim_x - lli, -rd)):
        part = parts.get(role)
        if part is not None:
            part.location = (x, y, 0.0)

    _solve_corner_shape(root, parts, p, dim_x, dim_y, dim_z)
    _solve_corner_doors(root, parts, p, dim_x, dim_y, dim_z)


def _solve_corner_upper(root, parts, p, dim_x, dim_y, dim_z):
    mt = p.mt
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))

    part = parts.get('LEFT_SIDE')
    if part is not None:
        set_part(part, (0.0, -dim_y, 0.0), length=dim_z, width=ld, thickness=mt)

    part = parts.get('RIGHT_SIDE')
    if part is not None:
        set_part(part, (dim_x, 0.0, 0.0), length=dim_z, width=rd, thickness=mt)

    part = parts.get('LEFT_BACK')
    if part is not None:
        set_part(part, (0.0, 0.0, mt), length=dim_z - mt * 2.0,
                 width=dim_y - mt, thickness=mt)

    part = parts.get('RIGHT_BACK')
    if part is not None:
        set_part(part, (mt, 0.0, mt), length=dim_x - mt * 2.0,
                 width=dim_z - mt * 2.0, thickness=mt)

    part = parts.get('BOTTOM')
    if part is not None:
        set_part(part, (0.0, 0.0, 0.0), length=dim_x - mt, width=dim_y - mt,
                 thickness=mt)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (0.0, 0.0, dim_z), length=dim_x - mt, width=dim_y - mt,
                 thickness=mt)

    _solve_corner_shape(root, parts, p, dim_x, dim_y, dim_z)
    _solve_corner_doors(root, parts, p, dim_x, dim_y, dim_z)


_SOLVERS = {
    'BASE': _solve_base,
    'TALL': _solve_tall,
    'UPPER': _solve_upper,
    'LAP_DRAWER': _solve_lap_drawer,
    'CORNER_BASE': _solve_corner_base,
    'CORNER_UPPER': _solve_corner_upper,
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
    prompts = _Prompts(root)
    dims = (cage.get_input('Dim X'), cage.get_input('Dim Y'),
            cage.get_input('Dim Z'))
    _SOLVERS[kind](root, parts, prompts, *dims)
    _solve_applied_ends(root, parts, prompts, *dims)

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

_SPLIT_LEGACY_NAME = re.compile(
    r'^(Opening|Section|Vertical Splitter|Horizontal Splitter|Interior Divider) (\d+)$')
_SPLIT_OPENING_NAMES = ('Opening', 'Section')

INTERIOR_SPLITTER_VERTICAL_TAG = 'IS_FRAMELESS_INTERIOR_SPLITTER_VERTICAL'
INTERIOR_SPLITTER_HORIZONTAL_TAG = 'IS_FRAMELESS_INTERIOR_SPLITTER_HORIZONTAL'

# Array modifier carrying a shelf interior's repeated shelf.
SHELF_ARRAY_MOD = 'Qty'


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
            role = 'OPENING' if match.group(1) in _SPLIT_OPENING_NAMES else 'SPLITTER'
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
        elif child.get('IS_FRAMELESS_INTERIOR_CAGE'):
            solve_interior_parts(child)
            solve_cage_tree(child)
        else:
            solve_insert_parts(child)
            solve_cage_tree(child)


# ---------------------------------------------------------------------------
# Interiors: shelves and interior splitters
# ---------------------------------------------------------------------------

def _solve_shelves(interior_obj):
    """One shelf part arrayed up the interior at equal spacing."""
    shelf = None
    for child in interior_obj.children:
        if child.get('IS_FRAMELESS_INTERIOR_PART') and child.modifiers.get(SHELF_ARRAY_MOD) is not None:
            shelf = child
            break
    if shelf is None:
        return
    clear_drivers(shelf)
    shelf[PART_ROLE_KEY] = 'SHELF'
    dim_x, dim_y, dim_z = cage_dims(interior_obj)
    mt = float(prompt(interior_obj, 'Material Thickness', inch(0.75)))
    qty = int(prompt(interior_obj, 'Shelf Quantity', 1))
    clip_gap = float(prompt(interior_obj, 'Shelf Clip Gap', inch(0.125)))
    setback = float(prompt(interior_obj, 'Shelf Setback', inch(0.25)))
    spacing = (dim_z - mt * qty) / (qty + 1)
    # A quantity of zero means no shelves, which the array's own minimum
    # of one could not express.
    set_part(shelf, (clip_gap, setback, spacing), length=dim_x - clip_gap * 2.0,
             width=dim_y - setback, thickness=mt, visible=qty > 0)
    set_array(shelf, SHELF_ARRAY_MOD, qty, spacing + mt)


def _solve_section_parts(section_obj):
    """A section's own shelf sits mid-height and spans the section."""
    dim_x, dim_y, dim_z = cage_dims(section_obj)
    for child in section_obj.children:
        if not child.get('IS_FRAMELESS_INTERIOR_PART'):
            continue
        clear_drivers(child)
        child[PART_ROLE_KEY] = 'SECTION_SHELF'
        part = GeoNodeCutpart(child)
        child.location.z = dim_z / 2.0
        part.set_input('Length', max(dim_x, 0.0))
        part.set_input('Width', max(dim_y - 0.025, 0.0))


def solve_interior_parts(interior_obj):
    """Place the parts of one interior cage."""
    if interior_obj.get(INTERIOR_SPLITTER_VERTICAL_TAG) or interior_obj.get(INTERIOR_SPLITTER_HORIZONTAL_TAG):
        _solve_splitter(interior_obj, bool(interior_obj.get(INTERIOR_SPLITTER_VERTICAL_TAG)))
        for (role, _index), section in split_parts(interior_obj).items():
            if role == 'OPENING':
                _solve_section_parts(section)
    elif 'Shelf Quantity' in interior_obj:
        _solve_shelves(interior_obj)


# ---------------------------------------------------------------------------
# Inserts: fronts, pulls, drawer boxes
# ---------------------------------------------------------------------------
#
# An insert (doors, drawer, pullout, false front, flip-up door, appliance)
# is an opening cage carrying the front prompts. Its fronts overlay the
# cage by the reveal rules, each front carries its pull, and a drawer or
# pullout front carries its drawer box.

OVERLAY_EMPTY_NAME = 'Overlay Prompt Obj'

# Door Swing prompt: index into ["Left", "Right", "Double"].
SWING_LEFT, SWING_RIGHT, SWING_DOUBLE = 0, 1, 2

# Pull Location prompt: index into ["Base", "Tall", "Upper"].
PULL_BASE, PULL_TALL, PULL_UPPER = 0, 1, 2

_DOOR_ROLE_BY_NAME = {'Left Door': 'LEFT_DOOR', 'Right Door': 'RIGHT_DOOR'}


def front_overlays(insert_obj):
    """(top, bottom, left, right) overlay of a front on its opening.

    Inset fronts sit inside the opening by the inset reveal; a half
    overlay splits the neighbouring board with the front next door; a
    full overlay covers the board less the reveal.
    """
    inset = bool(insert_obj.get('Inset Front', False))
    inset_reveal = float(prompt(insert_obj, 'Inset Reveal', inch(0.125)))
    gap = float(prompt(insert_obj, 'Vertical Gap', inch(0.125)))

    def overlay(half_key, thickness_key, reveal_key, reveal_default):
        if inset:
            return -inset_reveal
        thickness = float(prompt(insert_obj, thickness_key, inch(0.75)))
        if insert_obj.get(half_key, False):
            return (thickness - gap) / 2.0
        return thickness - float(prompt(insert_obj, reveal_key, reveal_default))

    return (overlay('Half Overlay Top', 'Top Thickness', 'Top Reveal', inch(0.0625)),
            overlay('Half Overlay Bottom', 'Bottom Thickness', 'Bottom Reveal', 0.0),
            overlay('Half Overlay Left', 'Left Thickness', 'Left Reveal', inch(0.0625)),
            overlay('Half Overlay Right', 'Right Thickness', 'Right Reveal', inch(0.0625)))


def _front_role(child):
    role = child.get(PART_ROLE_KEY)
    if role in ('LEFT_DOOR', 'RIGHT_DOOR', 'FRONT'):
        return role
    if child.get('IS_DOOR_FRONT') and not child.get('IS_FLIP_UP_DOOR'):
        return _DOOR_ROLE_BY_NAME.get(child.name.split('.')[0], 'FRONT')
    return 'FRONT'


def _pull_x(front_obj, length, pull_len):
    """Height of the pull up the front for door-style pull locations."""
    location = int(prompt(front_obj, 'Pull Location', PULL_BASE))
    if location == PULL_BASE:
        # Measured from the top of the door to the top of the pull.
        return length - float(prompt(front_obj, 'Base Pull Vertical Location', 0.0)) - pull_len / 2.0
    if location == PULL_TALL:
        return float(prompt(front_obj, 'Tall Pull Vertical Location', 0.0)) + pull_len / 2.0
    return float(prompt(front_obj, 'Upper Pull Vertical Location', 0.0)) + pull_len / 2.0


def _solve_pull(front_obj, pull_obj, length, width, thickness, hidden):
    clear_drivers(pull_obj)
    pull_obj[PART_ROLE_KEY] = 'PULL'
    pull_len = float(prompt(front_obj, 'Pull Length', 0.0))
    if front_obj.get('IS_FLIP_UP_DOOR'):
        x = float(prompt(front_obj, 'Pull Vertical Location', 0.0))
        y = -width / 2.0
    elif front_obj.get('IS_DRAWER_FRONT'):
        if front_obj.get('Center Pull', False):
            x = length / 2.0
        else:
            x = length - float(prompt(front_obj, 'Handle Horizontal Location', 0.0)) - pull_len / 2.0
        y = -width / 2.0
    elif front_obj.get('IS_PULLOUT_FRONT'):
        x = _pull_x(front_obj, length, pull_len)
        y = -width / 2.0
    else:
        x = _pull_x(front_obj, length, pull_len)
        offset = float(prompt(front_obj, 'Handle Horizontal Location', 0.0))
        try:
            mirrored = bool(GeoNodeCutpart(front_obj).get_input('Mirror Y'))
        except Exception:
            mirrored = False
        y = -width + offset if mirrored else width - offset
    pull_obj.location = (x, y, thickness)
    pull_obj.hide_viewport = hidden
    pull_obj.hide_render = hidden


def _solve_drawer_box(front_obj, box_obj, insert_obj, length, width,
                      overlays, hidden):
    clear_drivers(box_obj)
    box_obj[PART_ROLE_KEY] = 'DRAWER_BOX'
    top, bottom, left, right = overlays
    side = float(prompt(front_obj, 'Drawer Box Side Clearance', inch(0.5)))
    top_clr = float(prompt(front_obj, 'Drawer Box Top Clearance', inch(0.75)))
    rear = float(prompt(front_obj, 'Drawer Box Rear Clearance', inch(1.0)))
    bottom_clr = float(prompt(front_obj, 'Drawer Box Bottom Clearance', inch(0.5)))
    depth = cage_dims(insert_obj)[1]
    set_cage(box_obj, (bottom + bottom_clr, -left - side, 0.0),
             dim_x=width - left - right - side * 2.0,
             dim_y=depth - rear,
             dim_z=length - top - bottom - top_clr - bottom_clr)
    box_obj.hide_viewport = hidden
    box_obj.hide_render = hidden


def solve_insert_parts(insert_obj):
    """Place the fronts, pulls and drawer boxes of one insert."""
    has_fronts = 'Inset Front' in insert_obj
    dim_x, dim_y, dim_z = cage_dims(insert_obj)
    overlays = front_overlays(insert_obj) if has_fronts else (0.0, 0.0, 0.0, 0.0)
    top, bottom, left, right = overlays
    thickness = float(prompt(insert_obj, 'Front Thickness', inch(0.75)))
    gap = float(prompt(insert_obj, 'Vertical Gap', inch(0.125)))
    swing = int(prompt(insert_obj, 'Door Swing', SWING_DOUBLE))
    if insert_obj.get('Inset Front', False):
        y = thickness
    else:
        y = -float(prompt(insert_obj, 'Door to Cabinet Gap', inch(0.125)))

    for child in list(insert_obj.children):
        if child.get('IS_APPLIANCE_TEXT'):
            clear_drivers(child)
            child[PART_ROLE_KEY] = 'APPLIANCE_TEXT'
            child.location.x = dim_x / 2.0
            child.location.z = dim_z / 2.0
            continue
        if child.name.split('.')[0] == OVERLAY_EMPTY_NAME or child.get(PART_ROLE_KEY) == 'OVERLAY_PROMPTS':
            clear_drivers(child)
            child[PART_ROLE_KEY] = 'OVERLAY_PROMPTS'
            child['Overlay Top'] = top
            child['Overlay Bottom'] = bottom
            child['Overlay Left'] = left
            child['Overlay Right'] = right
            continue
        if not child.get('IS_CABINET_FRONT') or not has_fronts:
            continue

        role = _front_role(child)
        clear_drivers(child)
        child[PART_ROLE_KEY] = role
        length = dim_z + top + bottom
        if role == 'LEFT_DOOR':
            width = (dim_x + left + right - gap) / 2.0 if swing == SWING_DOUBLE else dim_x + left + right
            set_part(child, (-left, y, -bottom), length=length, width=width,
                     thickness=thickness, visible=swing != SWING_RIGHT)
        elif role == 'RIGHT_DOOR':
            width = (dim_x + left + right - gap) / 2.0 if swing == SWING_DOUBLE else dim_x + left + right
            set_part(child, (dim_x + right, y, -bottom), length=length,
                     width=width, thickness=thickness, visible=swing != SWING_LEFT)
        else:
            width = dim_x + left + right
            # A lone front keeps whatever visibility it was given.
            set_part(child, (-left, y, -bottom), length=length, width=width,
                     thickness=thickness, visible=not child.hide_viewport)
        for key, value in (('Top Overlay', top), ('Bottom Overlay', bottom),
                           ('Left Overlay', left), ('Right Overlay', right)):
            if key in child:
                child[key] = value

        false_front = bool(child.get('False Front', False))
        for part in list(child.children):
            if part.get('IS_CABINET_PULL'):
                hidden = false_front if (child.get('IS_DRAWER_FRONT') or child.get('IS_PULLOUT_FRONT')) else child.hide_viewport
                _solve_pull(child, part, length, width, thickness, hidden)
            elif part.get('IS_DRAWER_BOX'):
                _solve_drawer_box(child, part, insert_obj, length, width,
                                  overlays, false_front)


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
