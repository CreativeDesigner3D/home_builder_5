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
import math
import re
import traceback
from mathutils import Euler, Matrix, Vector
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
# A slab end's own sizes, when it carries them: how far it runs past the
# carcass front (APPLIED_END_EXTENSION when unset) and past the back, and
# its height (0 or unset: the cabinet's).
END_FRONT_EXTENSION_KEY = 'End Front Extension'
END_BACK_EXTENSION_KEY = 'End Back Extension'
END_HEIGHT_KEY = 'End Height'

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
            height = float(part.get(END_HEIGHT_KEY, 0.0) or 0.0)
            length = height if height > 0.0 else dim_z
            front = float(part.get(END_FRONT_EXTENSION_KEY,
                                   APPLIED_END_EXTENSION))
            back = float(part.get(END_BACK_EXTENSION_KEY, 0.0))
            width = dim_y + front + back
        visible = not part.hide_viewport
        y = 0.0
        if not part.get('IS_APPLIED_PANEL_5PIECE'):
            # Runs back past the cabinet from its back face.
            y = float(part.get(END_BACK_EXTENSION_KEY, 0.0))
        if side == 'LEFT':
            set_part(part, (0.0, y, z), length=length, width=width, visible=visible)
        elif side == 'RIGHT':
            set_part(part, (dim_x, y, z), length=length, width=width, visible=visible)
        else:
            set_part(part, (0.0, 0.0, 0.0), length=dim_x, width=dim_z, visible=visible)


# ---------------------------------------------------------------------------
# Carcass solve
# ---------------------------------------------------------------------------

# A flush toe kick stands in the plane of the doors: the board comes
# forward under them, across the full width of the cabinet, and the sides
# run straight to the floor with no notch.
FLUSH_TOE_KICK_KEY = 'Flush Toe Kick'


def _front_plane(root):
    """(inset, front thickness, door gap) of the first front insert in
    the cabinet -- where its doors and drawer fronts stand. A corner
    cabinet carries its door prompts on the cabinet itself."""
    if 'Front Thickness' in root:
        return (bool(root.get('Inset Front', False)),
                float(prompt(root, 'Front Thickness', inch(0.75))),
                float(prompt(root, 'Door to Cabinet Gap', inch(0.125))))
    bay = next((c for c in root.children if c.get('IS_FRAMELESS_BAY_CAGE')),
               None)
    for obj in (bay.children_recursive if bay is not None else ()):
        if 'Inset Front' in obj and 'Front Thickness' in obj:
            return (bool(obj.get('Inset Front', False)),
                    float(prompt(obj, 'Front Thickness', inch(0.75))),
                    float(prompt(obj, 'Door to Cabinet Gap', inch(0.125))))
    return False, inch(0.75), inch(0.125)


def kick_front_setback(root):
    """How far the toe kick's face stands back from the carcass front:
    the setback, or for a flush toe kick the negative of how far the
    fronts stand forward of it (none for inset fronts)."""
    if not prompt(root, FLUSH_TOE_KICK_KEY, False):
        return float(prompt(root, 'Toe Kick Setback', 0.0))
    inset, front_t, gap = _front_plane(root)
    return 0.0 if inset else -(gap + front_t)


# A finished panel on the toe kick's face (a veneered or laminated skin),
# and a kick held in from the cabinet's ends so the cabinet reads as
# floating, with finished returns running back to the wall.
KICK_PANEL_KEY = 'Toe Kick Panel'
KICK_PANEL_THICKNESS_KEY = 'Toe Kick Panel Thickness'
KICK_END_INSET_KEY = 'Toe Kick End Inset'
_KICK_EXTRA_PARTS = {
    # role: (name, rotation, mirror) -- the toe kick's own orientation
    # for the panel, the sides' for the returns.
    'TOE_KICK_PANEL': ("Toe Kick Panel", (-90, 0, 0), 'Y'),
    'TOE_KICK_RETURN_LEFT': ("Toe Kick Return Left", (0, -90, 0), 'YZ'),
    'TOE_KICK_RETURN_RIGHT': ("Toe Kick Return Right", (0, -90, 0), 'Y'),
}


def _kick_part(root, parts, role, wanted):
    """The toe kick panel or return ``role``, made when it is wanted and
    taken away when it is not."""
    part = parts.get(role)
    if not wanted:
        if part is not None:
            bpy.data.objects.remove(part, do_unlink=True)
            parts.pop(role, None)
        return None
    if part is None:
        from . import types_frameless
        name, rotation, mirror = _KICK_EXTRA_PARTS[role]
        part = types_frameless.Cabinet(root)._add_carcass_part(
            name, role, rotation=rotation, mirror=mirror,
            finish=(True, True)).obj
        parts[role] = part
        _paint_like_cabinet(root, part)
    return part


def _paint_like_cabinet(root, part_obj):
    """A part made after the cabinet was styled takes the style's finish."""
    from ... import hb_project
    styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
    if not len(styles):
        return
    index = root.get('CABINET_STYLE_INDEX', 0)
    style = styles[index] if 0 <= index < len(styles) else styles[0]
    finish, _ = style.get_finish_material()
    edge, _front_edge = style.get_edge_materials()
    part = GeoNodeCutpart(part_obj)
    for name, mat in (('Top Surface', finish), ('Bottom Surface', finish),
                      ('Edge W1', edge), ('Edge W2', edge),
                      ('Edge L1', edge), ('Edge L2', edge)):
        try:
            part.set_input(name, mat)
        except Exception:
            pass


def _solve_toe_kick(root, parts, p, dim_x, dim_y):
    part = parts.get('TOE_KICK')
    if part is None:
        return
    visible = not p.rb
    inner = dim_x - p.mt * 2.0
    # Where the kick's visible face stands, and the span it runs.
    x0, length = p.mt, inner
    if p.flush:
        inset, front_t, gap = _front_plane(root)
        if inset:
            # Inset fronts face the carcass front, so the kick does too.
            face = -dim_y
        else:
            face = -dim_y - gap - front_t
            x0, length = 0.0, dim_x
    else:
        face = -dim_y + p.tks
        if p.kick_end_inset > 0.0:
            x0 = p.kick_end_inset
            length = max(dim_x - 2.0 * p.kick_end_inset, 0.0)
    panel_t = p.kick_panel_t if p.kick_panel else 0.0

    panel = _kick_part(root, parts, 'TOE_KICK_PANEL', p.kick_panel)
    if panel is not None:
        set_part(panel, (x0, face, 0.0), length=length, width=p.tkh,
                 thickness=panel_t, visible=visible)
    # The board stands behind the panel.
    set_part(part, (x0, face + panel_t, 0.0), length=length, width=p.tkh,
             thickness=p.mt, visible=visible)

    held_in = p.kick_end_inset > 0.0
    back_of_kick = face + panel_t + p.mt
    for role, x in (('TOE_KICK_RETURN_LEFT', x0),
                    ('TOE_KICK_RETURN_RIGHT', x0 + length)):
        ret = _kick_part(root, parts, role, held_in)
        if ret is not None:
            set_part(ret, (x, 0.0, 0.0), length=p.tkh,
                     width=max(-back_of_kick, 0.0), thickness=p.mt,
                     visible=visible)


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
        self.flush = bool(prompt(root, FLUSH_TOE_KICK_KEY, False))
        self.kick_panel = bool(prompt(root, KICK_PANEL_KEY, False))
        self.kick_panel_t = float(prompt(root, KICK_PANEL_THICKNESS_KEY,
                                         inch(0.375)))
        # Holding the kick in from the ends only means something when it
        # stands back from the fronts.
        self.kick_end_inset = (0.0 if self.flush else
                               max(float(prompt(root, KICK_END_INSET_KEY, 0.0)), 0.0))


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
            if p.flush:
                notch_y = 0.0
            elif p.kick_end_inset > 0.0:
                # The kick stands in from the ends, so the side stops at
                # the top of it all the way back.
                notch_y = dim_y
            else:
                notch_y = p.tks
            set_modifier(part, NOTCH_MOD_NAME,
                         (('X', tkh), ('Y', notch_y), ('Route Depth', p.mt)))
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


def _solve_toe_kick_extras(parts, p, dim_x, dim_y, root=None):
    part = parts.get('LADDER_BASE')
    if part is not None:
        tks = kick_front_setback(root) if root is not None else p.tks
        set_cage(part, (0.0, -dim_y + tks, 0.0), dim_x=dim_x,
                 dim_y=dim_y - tks, dim_z=p.tkh)
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

    _solve_toe_kick(root, parts, p, dim_x, dim_y)

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
        _sync_bay_sink(root, part, dim_z - tkh - bottom_t)

    _solve_toe_kick_extras(parts, p, dim_x, dim_y, root)


def _sync_bay_sink(root, bay_obj, top_z):
    """A sink base carries the sink model in its bay, hung from the
    cabinet top; the Show Appliance Models switch decides whether it
    comes in modeled or as a cage."""
    if not root.get('IS_SINK_CABINET'):
        return
    from ..common import appliance_geo
    appliance_geo.sync_bay_sink(bay_obj, top_z)


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

    _solve_toe_kick(root, parts, p, dim_x, dim_y)

    part = parts.get('TOP')
    if part is not None:
        set_part(part, (mt, 0.0, dim_z), length=inner, width=dim_y,
                 thickness=mt)

    bottom_t = 0.0 if rb else mt
    part = parts.get('BAY')
    if part is not None:
        set_cage(part, (mt, -dim_y, tkh + bottom_t), dim_x=inner,
                 dim_y=dim_y - mt, dim_z=dim_z - tkh - bottom_t - mt)

    _solve_toe_kick_extras(parts, p, dim_x, dim_y, root)


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


# Finished bottom on an upper: an applied panel of finished stock under
# the carcass, full width to the outside of the sides, with an optional
# LED groove routed in its underside behind the front.
FINISHED_BOTTOM_KEY = 'Finished Bottom'      # 0 none, 1 1/4 in, 2 3/4 in
FINISHED_BOTTOM_THICKNESS = {1: inch(0.25), 2: inch(0.75)}
FB_LED_KEY = 'Finished Bottom LED Route'
FB_LED_WIDTH_KEY = 'LED Route Width'
FB_LED_DEPTH_KEY = 'LED Route Depth'
FB_LED_INSET_KEY = 'LED Route Inset'
FB_LED_MOD_NAME = 'LED Route'


def _solve_finished_bottom(root, parts, p, dim_x, dim_y, dim_z):
    t = FINISHED_BOTTOM_THICKNESS.get(int(prompt(root, FINISHED_BOTTOM_KEY, 0)))
    panel = parts.get('FINISHED_BOTTOM')
    if t is None:
        if panel is not None:
            parts.pop('FINISHED_BOTTOM')
            bpy.data.objects.remove(panel, do_unlink=True)
        return
    if panel is None:
        from . import types_frameless
        # Built from the front back, like the floating shelf's bottom, so
        # its underside is the Bottom Surface and a route's inset counts
        # from the front.
        panel = types_frameless.Cabinet(root)._add_carcass_part(
            'Finished Bottom', 'FINISHED_BOTTOM', finish=(False, True)).obj
        parts['FINISHED_BOTTOM'] = panel
        _paint_like_cabinet(root, panel)
    set_part(panel, (0.0, -dim_y, -t), length=dim_x, width=dim_y, thickness=t)

    led = bool(prompt(root, FB_LED_KEY, False))
    mod = panel.modifiers.get(FB_LED_MOD_NAME)
    if led and mod is None:
        cpm = GeoNodeCutpart(panel).add_part_modifier('CPM_CUTOUT', FB_LED_MOD_NAME)
        cpm.set_input('Flip Z', False)
    if led or mod is not None:
        width = float(prompt(root, FB_LED_WIDTH_KEY, inch(0.875)))
        inset = float(prompt(root, FB_LED_INSET_KEY, inch(1.5)))
        # Always leave 1/16 in of the panel above the groove.
        depth = min(float(prompt(root, FB_LED_DEPTH_KEY, inch(0.375))),
                    t - inch(0.0625))
        set_modifier(panel, FB_LED_MOD_NAME,
                     (('X', -0.01), ('Y', inset), ('End X', dim_x + 0.01),
                      ('End Y', inset + width), ('Route Depth', max(depth, 0.0))),
                     visible=led)


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


# An angled front: any straight cabinet can run its front from a left
# depth to a right depth; the angle follows from the two. The cabinet's
# Depth is the deeper of them.
FRONT_LEFT_DEPTH_KEY = 'Front Left Depth'
FRONT_RIGHT_DEPTH_KEY = 'Front Right Depth'
STRAIGHT_KINDS = ('BASE', 'TALL', 'UPPER', 'LAP_DRAWER')
# Parts that run along the front: carried onto the angle, their straight
# rotation kept here to put back when the front goes square again.
ANGLED_FRONT_ROLES = ('TOE_KICK', 'TOE_KICK_PANEL', 'FRONT_STRETCHER',
                      'SINK_APRON')
BASE_ROTATION_KEY = 'hb_square_rotation'


def angled_front_depths(root, dim_y, mt):
    """``(left, right)`` depths of an angled front, or None for a square
    one."""
    if FRONT_LEFT_DEPTH_KEY not in root and FRONT_RIGHT_DEPTH_KEY not in root:
        return None
    lo = mt * 2.0
    ld = min(max(float(prompt(root, FRONT_LEFT_DEPTH_KEY, dim_y)), lo), dim_y)
    rd = min(max(float(prompt(root, FRONT_RIGHT_DEPTH_KEY, dim_y)), lo), dim_y)
    return ld, rd


def _front_frame(ax, ay, bx, by):
    length = math.hypot(bx - ax, by - ay)
    if length <= 1e-6:
        return None
    ux, uy = (bx - ax) / length, (by - ay) / length
    return (ax, ay), (ux, uy), (uy, -ux), length


def _diagonal_frame(root, dim_x, dim_y):
    """The angled face of a diagonal corner: its left end A, the unit
    vector u from A to its right end, the outward normal n, and its
    length."""
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))
    ax, ay = ld, -dim_y
    bx, by = dim_x, -rd
    length = math.hypot(bx - ax, by - ay)
    if length <= 1e-6:
        return None
    ux, uy = (bx - ax) / length, (by - ay) / length
    return (ax, ay), (ux, uy), (uy, -ux), length


def _diagonal_matrix(u, n, origin):
    """A part's placement on the angled face: length up, across along
    -u (so a Mirror Y part runs +u from ``origin``), thickness out along
    n."""
    m = Matrix(((0.0, -u[0], n[0]), (0.0, -u[1], n[1]), (1.0, 0.0, 0.0)))
    return m.to_euler('XYZ'), Vector(origin)


ANGLED_CUTTER_ROLE = 'ANGLED_CUTTER'
ANGLED_CUT_MOD_NAME = 'Angled Cut'


def _solve_angled_cut(root, targets, frame, dim_y, dim_z,
                      role=ANGLED_CUTTER_ROLE, mod_name=ANGLED_CUT_MOD_NAME):
    """Trim ``targets`` along an angled face -- ``frame`` as from
    ``_diagonal_frame`` -- with a boolean off one hidden cage covering
    everything on the outside of it. (The chamfer part modifier's cutter
    no longer cuts.)"""
    if frame is None:
        return
    (ax, ay), u, _n, face = frame
    cutter = next((c for c in root.children
                   if c.get(PART_ROLE_KEY) == role), None)
    if cutter is None:
        cage = GeoNodeCage()
        cage.create('Angled Cutter')
        cutter = cage.obj
        cutter.parent = root
        cutter[PART_ROLE_KEY] = role
        cage.set_input('Show Cage', True)
        cutter.hide_viewport = cutter.hide_render = True
    # Local X runs along the face; a Mirror Y cage reaches out along the
    # outward normal from it.
    margin = inch(2.0)
    cutter.rotation_euler = (0.0, 0.0, math.atan2(u[1], u[0]))
    set_cage(cutter, (ax - u[0] * margin, ay - u[1] * margin, -margin),
             dim_x=face + margin * 2.0, dim_y=dim_y + margin,
             dim_z=dim_z + margin * 2.0)
    GeoNodeCage(cutter).set_input('Mirror Y', True)
    for part in targets:
        mod = part.modifiers.get(mod_name)
        if mod is None:
            mod = part.modifiers.new(name=mod_name, type='BOOLEAN')
            mod.operation = 'DIFFERENCE'
        if mod.object is not cutter:
            mod.object = cutter
        set_modifier(part, 'Chamfer', (('Turn On', False),))


def _solve_diagonal_door(root, parts, p, dim_x, dim_y, dim_z):
    """A diagonal corner's door: square to the angled face, a door gap
    off it, the width of the face less a reveal each side."""
    door = parts.get('DIAGONAL_DOOR')
    if door is None:
        return
    frame = _diagonal_frame(root, dim_x, dim_y)
    if frame is None:
        return
    (ax, ay), u, n, face = frame
    mt, tkh = p.mt, p.tkh
    ft = float(prompt(root, 'Front Thickness', inch(0.75)))
    gap = float(prompt(root, 'Door to Cabinet Gap', inch(0.125)))
    reveal = float(prompt(root, 'Outer Reveal', inch(0.0625)))
    top = mt - float(prompt(root, 'Top Reveal', inch(0.0625)))
    bottom = mt - float(prompt(root, 'Bottom Reveal', 0.0))
    bottom_t = 0.0 if p.rb else mt
    z = tkh + bottom_t - bottom
    length = dim_z - tkh - bottom_t - mt + top + bottom
    width = max(face - 2.0 * reveal, 0.0)
    ox = ax + n[0] * gap + u[0] * reveal
    oy = ay + n[1] * gap + u[1] * reveal
    euler, loc = _diagonal_matrix(u, n, (ox, oy, z))
    clear_drivers(door)
    door.rotation_euler = euler
    set_part(door, loc, length=length, width=width, thickness=ft,
             visible=not door.hide_viewport)
    swing = int(prompt(root, 'Door Swing', 0))
    for pull in door.children:
        if pull.get('IS_CABINET_PULL'):
            _solve_pull(door, pull, length, width, ft, False)
            if swing == 1:
                # Hinged on the right: the pull goes to the left end.
                offset = float(prompt(door, 'Handle Horizontal Location', inch(2.0)))
                pull.location.y = -offset


def _solve_diagonal_toe_kick(root, parts, p, dim_x, dim_y):
    """A diagonal corner's kick runs along the angled face at the setback,
    between the two sides; the wing kicks of a pie cut are not used."""
    kick = parts.get('LEFT_TOE_KICK') or parts.get('TOE_KICK')
    other = parts.get('RIGHT_TOE_KICK')
    if other is not None:
        other.hide_viewport = other.hide_render = True
    if kick is None:
        return
    frame = _diagonal_frame(root, dim_x, dim_y)
    if frame is None:
        return
    (ax, ay), u, n, _face = frame
    mt, tks = p.mt, p.tks
    # The kick's face line, and where it meets the two sides' inside faces.
    fx, fy = ax - n[0] * tks, ay - n[1] * tks
    t0 = ((-dim_y + mt) - fy) / u[1] if abs(u[1]) > 1e-6 else 0.0
    t1 = ((dim_x - mt) - fx) / u[0] if abs(u[0]) > 1e-6 else 0.0
    length = max(t1 - t0, 0.0)
    sx, sy = fx + u[0] * t0 - n[0] * mt, fy + u[1] * t0 - n[1] * mt
    # Length along u, height up, thickness out along n to the face.
    m = Matrix(((u[0], 0.0, n[0]), (u[1], 0.0, n[1]), (0.0, 1.0, 0.0)))
    clear_drivers(kick)
    # Built for a pie cut's wing, flipped; along the angle it stands up.
    GeoNodeCutpart(kick).set_input('Mirror Y', False)
    kick.rotation_euler = m.to_euler('XYZ')
    set_part(kick, (sx, sy, 0.0), length=length, width=p.tkh, thickness=mt,
             visible=not p.rb)
    kick.hide_viewport = kick.hide_render = p.rb


def _square_rotation(part, rot_z):
    """Turn a front-running part ``rot_z`` about Z from its straight
    rotation (0 puts it back)."""
    if rot_z == 0.0:
        if BASE_ROTATION_KEY in part:
            part.rotation_euler = tuple(part[BASE_ROTATION_KEY])
            del part[BASE_ROTATION_KEY]
        return
    if BASE_ROTATION_KEY not in part:
        part[BASE_ROTATION_KEY] = list(part.rotation_euler)
    base = Euler(tuple(part[BASE_ROTATION_KEY])).to_matrix()
    part.rotation_euler = (Matrix.Rotation(rot_z, 3, 'Z') @ base).to_euler('XYZ')


def _clear_cut(root, parts, cutter_role, mod_name):
    obj = parts.pop(cutter_role, None)
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
    for child in root.children_recursive:
        mod = child.modifiers.get(mod_name)
        if mod is not None:
            child.modifiers.remove(mod)


def _solve_angled_front(root, parts, p, dim_x, dim_y, dim_z):
    """A front run from the left depth to the right: each side takes its
    own depth, the bay turns to the angle (so every door and drawer in it
    follows), the parts along the front are carried onto it and the top,
    bottom and back stretcher are cut to it."""
    mt = p.mt
    bay = parts.get('BAY')
    depths = angled_front_depths(root, dim_y, mt)
    frame = None
    if depths is not None:
        frame = _front_frame(0.0, -depths[0], dim_x, -depths[1])
    if frame is None:
        # Square: put back anything a past angle turned.
        for role in ('BAY', 'LADDER_BASE'):
            cage = parts.get(role)
            if cage is not None and cage.rotation_euler.z != 0.0:
                cage.rotation_euler = (0.0, 0.0, 0.0)
        for role in ANGLED_FRONT_ROLES:
            part = parts.get(role)
            if part is not None:
                _square_rotation(part, 0.0)
        if parts.get(ANGLED_CUTTER_ROLE) is not None:
            _clear_cut(root, parts, ANGLED_CUTTER_ROLE, ANGLED_CUT_MOD_NAME)
        return
    ld, rd = depths
    (ax, ay), (ux, uy), _n, face = frame
    theta = math.atan2(uy, ux)
    # Back, square to the front, into the cabinet.
    bx, by = -uy, ux

    for role, depth in (('LEFT_SIDE', ld), ('RIGHT_SIDE', rd)):
        side = parts.get(role)
        if side is not None:
            GeoNodeCutpart(side).set_input('Width', depth)

    for role in ANGLED_FRONT_ROLES:
        part = parts.get(role)
        if part is None:
            continue
        # How far behind the front the straight solve put it, laid onto
        # the angle at the same x.
        x, y, z = part.location
        behind = y + dim_y
        along = (x - bx * behind) / ux
        part.location = (x, ay + uy * along + by * behind, z)
        cut = GeoNodeCutpart(part)
        cut.set_input('Length', float(cut.get_input('Length')) / ux)
        _square_rotation(part, theta)

    ladder = parts.get('LADDER_BASE')
    if ladder is not None:
        # A ladder stays square -- turned, its back corner would swing out
        # past a side -- and stands the setback behind the shallow end.
        tks = kick_front_setback(root)
        shallow = min(ld, rd)
        ladder.location.x, ladder.location.y = 0.0, -shallow + tks
        ladder.rotation_euler = (0.0, 0.0, 0.0)
        GeoNodeCage(ladder).set_input('Dim Y', max(shallow - tks, 0.0))
    for role, x in (('LEG_LEVELER_FL', p.lli), ('LEG_LEVELER_FR', dim_x - p.lli)):
        part = parts.get(role)
        if part is not None:
            part.location.x = x
            part.location.y = ay + uy * ((x - bx * p.lli) / ux) + by * p.lli

    targets = [parts[r] for r in ('TOP', 'BOTTOM', 'BACK_STRETCHER',
                                  'LEFT_SIDE', 'RIGHT_SIDE', 'FINISHED_BOTTOM')
               if r in parts]
    if bay is not None:
        # The bay stays square, so shelves, dividers and drawer boxes stay
        # square to the back; they are cut to the front with the carcass. Only the
        # fronts turn onto the angle (see angled_front_placement).
        targets += [o for o in bay.children_recursive
                    if o.get('IS_DRAWER_BOX')
                    or o.get('IS_FRAMELESS_INTERIOR_PART')
                    or o.get(PART_ROLE_KEY) == 'SPLITTER'
                    or 'SHELF' in (o.get(PART_ROLE_KEY) or '')]
    _solve_angled_cut(root, targets, frame, dim_y, dim_z)


def angled_front_placement(insert_obj):
    """``(frame, offset, dim_y)`` for laying an insert's fronts onto its
    cabinet's angled front, or None when the front is square. ``offset``
    is the insert's origin in cabinet space -- the cages between run
    square, so their locations add up."""
    root = cabinet_root(insert_obj)
    if root is None or carcass_kind(root) not in STRAIGHT_KINDS:
        return None
    dim_x, dim_y, _dz = cage_dims(root)
    mt = float(prompt(root, 'Material Thickness', inch(0.75)))
    depths = angled_front_depths(root, dim_y, mt)
    if depths is None:
        return None
    frame = _front_frame(0.0, -depths[0], dim_x, -depths[1])
    if frame is None:
        return None
    offset = Vector((0.0, 0.0, 0.0))
    obj = insert_obj
    while obj is not None and obj is not root:
        offset += Vector(obj.location)
        obj = obj.parent
    return frame, offset, dim_y


def angle_front(front_obj, placement):
    """Carry one front, placed square by the insert solve (open or
    closed), onto the angled front: turned about its hinge edge -- the
    edge its origin sits on -- and stretched along the angle so side by
    side fronts still meet. Returns the stretch factor."""
    (ax, ay), (ux, uy), (nx, ny), _face = placement[0]
    offset, dim_y = placement[1], placement[2]
    theta = math.atan2(uy, ux)
    # The hinge edge in cabinet space, and how far in front of the
    # square carcass front its back face stood.
    origin = offset + Vector(front_obj.location)
    ahead = -dim_y - origin.y
    along = (origin.x - nx * ahead) / ux
    target = Vector((ax + ux * along + nx * ahead,
                     ay + uy * along + ny * ahead, origin.z))
    rot = Matrix.Rotation(theta, 4, 'Z')
    move = (Matrix.Translation(target) @ rot @ Matrix.Translation(-origin))
    local = (Matrix.Translation(-offset) @ move @ Matrix.Translation(offset))
    front_obj.matrix_basis = local @ front_obj.matrix_basis
    return 1.0 / ux


ANGLED_BACK_KEY = 'Angled Back'              # 0 none, 1 left, 2 right
ANGLED_BACK_WIDTH_KEY = 'Angled Back Width'  # along the back from the side
ANGLED_BACK_DEPTH_KEY = 'Angled Back Depth'  # down the side from the back
ANGLED_BACK_CUTTER_ROLE = 'ANGLED_BACK_CUTTER'
ANGLED_BACK_CUT_MOD_NAME = 'Angled Back Cut'


def _angled_back_frame(root, dim_x, dim_y, mt):
    """The angled back across one back corner, run so the frame's normal
    points out of the cabinet: A on the side, B on the back."""
    hand = int(prompt(root, ANGLED_BACK_KEY, 0))
    cx = min(max(float(prompt(root, ANGLED_BACK_WIDTH_KEY, inch(12.0))), mt),
             dim_x - mt * 2.0)
    cy = min(max(float(prompt(root, ANGLED_BACK_DEPTH_KEY, inch(12.0))), mt),
             dim_y - mt * 2.0)
    if hand == 2:
        ax, ay, bx, by = dim_x, -cy, dim_x - cx, 0.0
    else:
        ax, ay, bx, by = cx, 0.0, 0.0, -cy
    length = math.hypot(bx - ax, by - ay)
    if length <= 1e-6:
        return None, cx, cy
    ux, uy = (bx - ax) / length, (by - ay) / length
    return ((ax, ay), (ux, uy), (uy, -ux), length), cx, cy


def _clear_angled_back(root, parts):
    """Take an angled back off: its panel, its cutter and the cuts."""
    for role in ('ANGLED_BACK', ANGLED_BACK_CUTTER_ROLE):
        obj = parts.pop(role, None)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)
    for obj in root.children_recursive:
        mod = obj.modifiers.get(ANGLED_BACK_CUT_MOD_NAME)
        if mod is not None:
            obj.modifiers.remove(mod)


def _solve_angled_back(root, parts, p, dim_x, dim_y, dim_z):
    """One back corner cut off across an angled wall: the side on that
    hand stops short of the back, the back stops short of the side, a
    panel closes the angle and the rest is trimmed to it."""
    hand = int(prompt(root, ANGLED_BACK_KEY, 0))
    if hand not in (1, 2):
        if parts.get('ANGLED_BACK') or parts.get(ANGLED_BACK_CUTTER_ROLE):
            _clear_angled_back(root, parts)
        return
    mt = p.mt
    frame, cx, cy = _angled_back_frame(root, dim_x, dim_y, mt)
    if frame is None:
        return
    side = parts.get('RIGHT_SIDE' if hand == 2 else 'LEFT_SIDE')
    if side is not None:
        # Short of its own depth, which an angled front may have cut.
        cut = GeoNodeCutpart(side)
        side.location.y = -cy
        cut.set_input('Width', max(float(cut.get_input('Width')) - cy, 0.0))
    back = parts.get('BACK')
    back_z, back_len = mt, dim_z - mt * 2.0
    if back is not None:
        back_z = back.location.z
        back_len = float(GeoNodeCutpart(back).get_input('Length'))
        if hand == 1:
            back.location.x = cx
        GeoNodeCutpart(back).set_input('Width', max(dim_x - mt - cx, 0.0))
    panel = parts.get('ANGLED_BACK')
    if panel is None:
        from . import types_frameless
        panel = types_frameless.Cabinet(root)._add_carcass_part(
            'Angled Back', 'ANGLED_BACK', mirror='YZ').obj
        parts['ANGLED_BACK'] = panel
        _paint_like_cabinet(root, panel)
    (ax, ay), u, n, face = frame
    # Outer face on the angle, thickness in towards the cabinet.
    euler, loc = _diagonal_matrix(u, n, (ax, ay, back_z))
    panel.rotation_euler = euler
    set_part(panel, loc, length=back_len, width=face, thickness=mt)
    targets = [parts[r] for r in ('TOP', 'BOTTOM', 'FRONT_STRETCHER',
                                  'BACK_STRETCHER', 'SINK_APRON',
                                  'FINISHED_BOTTOM')
               if r in parts]
    targets += [o for o in root.children_recursive
                if 'SHELF' in (o.get(PART_ROLE_KEY) or '')]
    _solve_angled_cut(root, targets, frame, dim_y, dim_z,
                      role=ANGLED_BACK_CUTTER_ROLE,
                      mod_name=ANGLED_BACK_CUT_MOD_NAME)


def _solve_corner_base(root, parts, p, dim_x, dim_y, dim_z):
    mt, tkh = p.mt, p.tkh
    ld = float(prompt(root, 'Left Depth', dim_y))
    rd = float(prompt(root, 'Right Depth', dim_y))
    # How far each wing's kick stands back from its carcass front; a
    # flush kick stands forward, in the plane of the doors.
    tks = kick_front_setback(root)
    # A flush kick runs out over the side panel at each wing's outer end.
    end = mt if p.flush else 0.0

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
                         (('X', tkh), ('Y', 0.0 if p.flush else p.tks),
                          ('Route Depth', mt)))
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
        # Flush, the left kick also runs on across the inside corner,
        # the way the left door does, so the two kicks close the corner.
        set_part(part, (ld - tks, -dim_y + mt - end, 0.0),
                 length=dim_y - rd - mt + tks + end * 2.0, width=tkh,
                 thickness=mt)

    part = parts.get('RIGHT_TOE_KICK')
    if part is not None:
        set_part(part, (dim_x - mt + end, -rd + tks, 0.0),
                 length=dim_x - ld - mt + tks + end, width=tkh, thickness=mt)

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
    if root.get('CORNER_TYPE') == 'DIAGONAL':
        _solve_angled_cut(root, [parts[r] for r in ('TOP', 'BOTTOM') if r in parts],
                          _diagonal_frame(root, dim_x, dim_y), dim_y, dim_z)
        _solve_diagonal_toe_kick(root, parts, p, dim_x, dim_y)
        _solve_diagonal_door(root, parts, p, dim_x, dim_y, dim_z)


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
    if root.get('CORNER_TYPE') == 'DIAGONAL':
        _solve_angled_cut(root, [parts[r] for r in ('TOP', 'BOTTOM') if r in parts],
                          _diagonal_frame(root, dim_x, dim_y), dim_y, dim_z)
        _solve_diagonal_door(root, parts, p, dim_x, dim_y, dim_z)


# The least a blind corner keeps for its doors, whatever the blind asks.
BLIND_MIN_DOOR_OPENING = inch(9.0)
# Written on a blind corner's bay: how far the blind runs beside the door
# opening, and how thick the panel closing it is.
BLIND_SPAN_KEY = 'Blind Span'
BLIND_PANEL_THICKNESS_KEY = 'Blind Panel Thickness'


def blind_reach(insert_obj):
    """(span, on_left, panel_thickness) for an insert standing directly
    in a blind corner's bay, else None. An insert under a splitter fills
    its own opening only: the blind belongs to the bay as a whole."""
    bay = insert_obj.parent if insert_obj is not None else None
    if bay is None or BLIND_SPAN_KEY not in bay:
        return None
    span = float(bay[BLIND_SPAN_KEY])
    if span <= 0.0:
        return None
    root = cabinet_root(bay)
    on_left = root is None or root.get('Blind Side') != 'Right'
    return span, on_left, float(bay.get(BLIND_PANEL_THICKNESS_KEY, 0.0))


def _solve_blind_corner(root, parts, p, dim_x, dim_y, dim_z):
    """A blind corner's captured panel, and the bay narrowed to the door
    opening beside it. Blind Width runs from the corner-side end of the
    cabinet to the edge of the doors; the panel carries on one material
    thickness past that, standing in for the side the doors overlay."""
    panel = parts.get('BLIND_PANEL')
    bay = parts.get('BAY')
    if panel is None or bay is None:
        return
    mt = p.mt
    inner = dim_x - mt * 2.0
    blind = float(prompt(root, 'Blind Width', dim_x / 2.0))
    span = max(min(blind, inner - BLIND_MIN_DOOR_OPENING), 0.0)
    bay_x, bay_y, bay_z = bay.location
    bay_h = GeoNodeCage(bay).get_input('Dim Z')
    if root.get('Blind Side') == 'Right':
        panel_x = dim_x - mt - span
    else:
        panel_x = mt
        bay_x = mt + span
    set_part(panel, (panel_x, -dim_y + mt, bay_z), length=bay_h, width=span,
             thickness=mt)
    set_cage(bay, (bay_x, bay_y, bay_z), dim_x=inner - span)
    # The bay is the door opening, but the inside of the box is open
    # right across: the interior reads these to reach behind the panel.
    bay[BLIND_SPAN_KEY] = span
    bay[BLIND_PANEL_THICKNESS_KEY] = mt


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
    if kind == 'UPPER':
        _solve_finished_bottom(root, parts, prompts, *dims)
    if kind in STRAIGHT_KINDS:
        _solve_angled_front(root, parts, prompts, *dims)
    if ANGLED_BACK_KEY in root and kind in STRAIGHT_KINDS:
        _solve_angled_back(root, parts, prompts, *dims)
    _solve_blind_corner(root, parts, prompts, *dims)
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
    interior behind an inset front starts behind the front, and one in
    a blind corner reaches across behind the blind panel."""
    dim_x, dim_y, dim_z = dims
    if not child_obj.get('IS_FRAMELESS_INTERIOR_CAGE'):
        return (0.0, 0.0, 0.0), (dim_x, dim_y, dim_z)
    x = 0.0
    blind = blind_reach(parent_obj)
    if blind is not None:
        span, on_left, _panel_t = blind
        dim_x += span
        if on_left:
            x = -span
    offset = 0.0
    if parent_obj.get('Inset Front'):
        offset = float(prompt(parent_obj, 'Front Thickness', 0.0))
    return (x, offset, 0.0), (dim_x, dim_y - offset, dim_z)


# Stamped on an appliance model that an Appliance insert asked for, so it
# goes when the insert does (the opening changed to doors, say).
INSERT_APPLIANCE_KEY = 'HB_FROM_APPLIANCE_INSERT'


def _sync_opening_appliance(opening_obj):
    """An opening that houses an appliance model -- a refrigerator
    cabinet's bottom opening, or one holding an oven or microwave
    Appliance insert -- keeps that model sized to itself."""
    from ..common import appliance_geo
    kind = opening_obj.get('APPLIANCE_OPENING')
    from_insert = False
    if not kind:
        kind = next((c.get('APPLIANCE_KIND') for c in opening_obj.children
                     if c.get('APPLIANCE_KIND')), None)
        from_insert = bool(kind)
    if not kind:
        model = appliance_geo.opening_appliance(opening_obj)
        if model is not None and model.get(INSERT_APPLIANCE_KEY):
            for child in list(model.children_recursive):
                bpy.data.objects.remove(child, do_unlink=True)
            bpy.data.objects.remove(model, do_unlink=True)
        return
    proud = opening_obj.get('APPLIANCE_PROUD')
    seed = opening_obj.get('APPLIANCE_SEED')
    model = appliance_geo.sync_opening_appliance(
        opening_obj, kind,
        proud=float(proud) if proud is not None else None,
        seed=seed.to_dict() if hasattr(seed, 'to_dict') else seed)
    if from_insert and model is not None:
        model[INSERT_APPLIANCE_KEY] = True


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
                    _sync_opening_appliance(opening)
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
    blind = blind_reach(interior_obj.parent)
    if blind is not None:
        # One shelf runs behind the doors and the blind panel alike, so
        # it stands back far enough to clear the panel.
        setback += blind[2]
    pocket_l, pocket_r = pocket_sides(interior_obj.parent)
    if pocket_l or pocket_r:
        # Retracting doors: the shelves stop short of the pockets and
        # stand back from the front.
        setback = max(setback, POCKET_FRONT)
    pocket_l = POCKET_WIDTH if pocket_l else 0.0
    pocket_r = POCKET_WIDTH if pocket_r else 0.0
    spacing = (dim_z - mt * qty) / (qty + 1)
    # A quantity of zero means no shelves, which the array's own minimum
    # of one could not express.
    set_part(shelf, (clip_gap + pocket_l, setback, spacing),
             length=dim_x - clip_gap * 2.0 - pocket_l - pocket_r,
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
                # A section may hold an interior of its own.
                solve_cage_tree(section)
    elif interior_obj.get('IS_FRAMELESS_ITEMS_INTERIOR'):
        # Imported here: interior_items reads the face frame item rules,
        # and the face frame library imports this module while loading.
        from . import interior_items
        interior_items.solve(interior_obj)
    elif interior_obj.get('IS_FRAMELESS_SHOE_SHELVES'):
        from . import closet_parts
        closet_parts.solve_shoe_shelves(interior_obj)
    elif 'Shelf Quantity' in interior_obj:
        _solve_shelves(interior_obj)
    # Any interior can carry a row of coat hooks on its back wall.
    from . import closet_parts
    closet_parts.solve_hooks(interior_obj)


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
    dims = (max(width - left - right - side * 2.0, 0.0),
            max(depth - rear, 0.0),
            max(length - top - bottom - top_clr - bottom_clr, 0.0))
    set_cage(box_obj, (bottom + bottom_clr, -left - side, 0.0), *dims)
    box_obj.hide_viewport = hidden
    box_obj.hide_render = hidden
    # The box construction pick and the inserts inside the box.
    from . import interior_items
    interior_items.solve_drawer_inserts(insert_obj, box_obj, dims, hidden)


# Retracting (pocket) doors: they open, then slide back into pockets
# along the hinge sides. The pockets take interior width off each hinged
# side and hold what is inside back from the front.
DOOR_MECHANISM_KEY = 'Door Mechanism'
MECH_STANDARD, MECH_RETRACTING = 0, 1
POCKET_WIDTH = inch(3.25)
POCKET_FRONT = inch(3.0)
POCKET_CLEARANCE = inch(0.25)


def pocket_sides(insert_obj):
    """(left, right): which sides of a door insert carry a pocket."""
    if (insert_obj is None
            or int(prompt(insert_obj, DOOR_MECHANISM_KEY, MECH_STANDARD)) != MECH_RETRACTING
            or 'Door Swing' not in insert_obj):
        return False, False
    swing = int(prompt(insert_obj, 'Door Swing', SWING_DOUBLE))
    return swing in (SWING_LEFT, SWING_DOUBLE), swing in (SWING_RIGHT, SWING_DOUBLE)


def _solve_pocket_panels(insert_obj, dim_x, dim_y, dim_z):
    """The panel that closes each pocket off from the cabinet's inside,
    made when the doors retract and taken away when they don't."""
    left, right = pocket_sides(insert_obj)
    mt = float(prompt(insert_obj, 'Left Thickness', inch(0.75)))
    existing = {c.get(PART_ROLE_KEY): c for c in insert_obj.children
                if c.get(PART_ROLE_KEY) in ('POCKET_PANEL_LEFT', 'POCKET_PANEL_RIGHT')}
    for role, wanted, x, mirror in (
            ('POCKET_PANEL_LEFT', left, POCKET_WIDTH - mt, True),
            ('POCKET_PANEL_RIGHT', right, dim_x - POCKET_WIDTH + mt, False)):
        part = existing.get(role)
        if not wanted:
            if part is not None:
                bpy.data.objects.remove(part, do_unlink=True)
            continue
        if part is None:
            from . import types_frameless
            import math as _math
            cp = types_frameless.CabinetPart()
            cp.create('Pocket Panel')
            part = cp.obj
            part.parent = insert_obj
            part[PART_ROLE_KEY] = role
            part['Finish Top'] = False
            part['Finish Bottom'] = False
            part.rotation_euler = (0.0, _math.radians(-90.0), 0.0)
            cp.set_input('Mirror Z', mirror)
            root = cabinet_root(insert_obj)
            if root is not None:
                _paint_interior(root, part)
        set_part(part, (x, 0.0, 0.0), length=dim_z, width=dim_y, thickness=mt)


def _paint_interior(root, part_obj):
    from ... import hb_project
    styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
    if not len(styles):
        return
    index = root.get('CABINET_STYLE_INDEX', 0)
    style = styles[index] if 0 <= index < len(styles) else styles[0]
    face, _ = style.get_interior_material()
    edge, _front_edge = style.get_edge_materials()
    part = GeoNodeCutpart(part_obj)
    for name, mat in (('Top Surface', face), ('Bottom Surface', face),
                      ('Edge W1', edge), ('Edge W2', edge),
                      ('Edge L1', edge), ('Edge L2', edge)):
        try:
            part.set_input(name, mat)
        except Exception:
            pass


# How far an insert's fronts are open, 0 closed to 1 fully open. Written
# by the open mode and the Open / Close command; an insert that never had
# it set is left exactly as the solver always placed it.
OPEN_KEY = 'Open Amount'
DOOR_MAX_SWING = math.radians(90.0)
# Clearance a drawer keeps at full extension.
DRAWER_OPEN_CLEARANCE = inch(1.0)
# Rotation every door front is built with (length up, thickness forward).
_FRONT_ROTATION = (math.radians(90.0), math.radians(-90.0), 0.0)


def open_amount(insert_obj):
    return min(max(float(prompt(insert_obj, OPEN_KEY, 0.0)), 0.0), 1.0)


def _open_front(front_obj, role, amount, thickness, length, travel,
                retract=None):
    """Move one closed front to its open position. Drawers and pullouts
    slide forward; doors swing 90 degrees on a hinge line at the front
    face of the hinge edge, which keeps every point of the door on its
    own side of that line; a flip-up door swings up on its top edge."""
    x, y, z = front_obj.location
    if front_obj.get('IS_DRAWER_FRONT') or front_obj.get('IS_PULLOUT_FRONT'):
        front_obj.location.y = y - amount * travel
        return
    if role == 'LEFT_DOOR':
        axis, angle = 'Z', -amount * DOOR_MAX_SWING
        pivot, offset = Vector((x, y - thickness, z)), Vector((0.0, thickness, 0.0))
    elif role == 'RIGHT_DOOR':
        axis, angle = 'Z', amount * DOOR_MAX_SWING
        pivot, offset = Vector((x, y - thickness, z)), Vector((0.0, thickness, 0.0))
    elif front_obj.get('IS_FLIP_UP_DOOR'):
        axis, angle = 'X', -amount * DOOR_MAX_SWING
        pivot = Vector((x, y - thickness, z + length))
        offset = Vector((0.0, thickness, -length))
    else:
        return
    slide = Vector((0.0, 0.0, 0.0))
    if retract is not None and axis == 'Z':
        # A retracting door swings open in the first half of its travel
        # and slides back into its pocket in the second.
        swing_part = min(amount * 2.0, 1.0)
        slide_part = max(amount * 2.0 - 1.0, 0.0)
        angle = (-1.0 if role == 'LEFT_DOOR' else 1.0) * swing_part * DOOR_MAX_SWING
        shift_x, depth = retract
        slide = Vector((shift_x * slide_part, depth * slide_part, 0.0))
    rot = Matrix.Rotation(angle, 3, axis)
    front_obj.rotation_euler = (rot @ Euler(_FRONT_ROTATION).to_matrix()).to_euler('XYZ')
    front_obj.location = pivot + rot @ offset + slide


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
    angled = angled_front_placement(insert_obj) if has_fronts else None

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
        if child.get('IS_LIFT_UPPER_FRONT'):
            # A bi-fold's upper panel is placed with the front below it.
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
        if child.get('IS_FLIP_UP_DOOR'):
            # The lift splits, opens and fits hardware to the front; the
            # pull goes on the part it leaves at the bottom.
            from . import lift_hardware
            length = lift_hardware.solve(insert_obj, child, length, width,
                                         thickness, child.hide_viewport)
        elif OPEN_KEY in insert_obj:
            retract = None
            pockets = pocket_sides(insert_obj)
            if role == 'LEFT_DOOR' and pockets[0]:
                retract = (left + POCKET_CLEARANCE,
                           min(width + thickness, dim_y - POCKET_CLEARANCE))
            elif role == 'RIGHT_DOOR' and pockets[1]:
                retract = (-(right + POCKET_CLEARANCE),
                           min(width + thickness, dim_y - POCKET_CLEARANCE))
            _open_front(child, role, open_amount(insert_obj), thickness,
                        length, max(dim_y - DRAWER_OPEN_CLEARANCE, 0.0),
                        retract)
        square_basis = child.matrix_basis.copy()
        square_width = width
        if angled is not None:
            stretch = angle_front(child, angled)
            width *= stretch
            GeoNodeCutpart(child).set_input('Width', width)
            for upper in insert_obj.children:
                if child.get('IS_FLIP_UP_DOOR') and upper.get('IS_LIFT_UPPER_FRONT'):
                    angle_front(upper, angled)
                    GeoNodeCutpart(upper).set_input('Width', width)

        false_front = bool(child.get('False Front', False))
        from . import edge_pulls
        front_hidden = (false_front if (child.get('IS_DRAWER_FRONT') or child.get('IS_PULLOUT_FRONT'))
                        else child.hide_viewport)
        # An edge handle (tab, continuous pull, finger notch) stands in
        # for the pull model.
        by_pull = edge_pulls.handle_type(child) == 'PULL'
        for part in list(child.children):
            if part.get('IS_CABINET_PULL'):
                _solve_pull(child, part, length, width, thickness,
                            front_hidden or not by_pull)
            elif part.get('IS_DRAWER_BOX'):
                _solve_drawer_box(child, part, insert_obj, length,
                                  square_width, overlays, false_front)
                if angled is not None:
                    # The box stays square to the back (cut to the front
                    # with the carcass), however the front turned.
                    part.matrix_basis = (child.matrix_basis.inverted()
                                         @ square_basis @ part.matrix_basis)
        edge_pulls.solve_front(child, length, width, thickness, front_hidden)
        edge_pulls.solve_lock(child, length, width, thickness, front_hidden)
    if 'Door Swing' in insert_obj:
        _solve_pocket_panels(insert_obj, dim_x, dim_y, dim_z)


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
