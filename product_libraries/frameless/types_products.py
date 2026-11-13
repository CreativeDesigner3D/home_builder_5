import bpy
import math
from ...hb_types import GeoNodeCage, GeoNodeCutpart, CabinetPartModifier
from ... import units
from ...units import inch
from .types_frameless import CabinetPart, CabinetSideNotched
from .solver_frameless import (PART_ROLE_KEY, clear_drivers as _clear_drivers,
                               set_part as _set_part, set_modifier as _set_modifier,
                               set_array, prompt as _prompt)


# ---------------------------------------------------------------------------
# Solver scaffolding
# ---------------------------------------------------------------------------
#
# Every product here is solved in Python: one function per product reads
# the cage's Dim X/Y/Z plus its prompts and writes each part's location,
# size and visibility. Nothing is driven. Drivers evaluate in an order the
# product cannot control, need a forced re-evaluation pass to settle after
# a prompt edit, and only come back from a saved file once every target
# they reference has -- so a saved product could reopen with parts
# collapsed onto the origin or missing. Solved values are plain object
# data that a file round-trips unchanged.
#
# Call ``recalculate_product`` after changing any prompt or dimension on a
# product; it accepts the cage or any part under it.

# Tag support frames carried before the products shared one key.
SUPPORT_FRAME_PART_KEY = 'SUPPORT_FRAME_PART'

# Products built before the role tag are matched on the names their parts
# were created with, so an older job upgrades in place on first solve.
SUPPORT_FRAME_LEGACY_NAMES = {
    'Left Panel': 'LEFT_RAIL',
    'Right Panel': 'RIGHT_RAIL',
    'Front Panel': 'FRONT_RAIL',
    'Back Panel': 'BACK_RAIL',
    'Support': 'SUPPORT',
    'Front Left Leg': 'FRONT_LEFT_LEG',
    'Front Right Leg': 'FRONT_RIGHT_LEG',
    'Back Left Leg': 'BACK_LEFT_LEG',
    'Back Right Leg': 'BACK_RIGHT_LEG',
}

LEGACY_PART_NAMES = {
    'FLOATING_SHELF': {
        'Front': 'SHELF_FRONT',
        'Top': 'SHELF_TOP',
        'Bottom': 'SHELF_BOTTOM',
        'Left Panel': 'SHELF_LEFT_PANEL',
        'Right Panel': 'SHELF_RIGHT_PANEL',
    },
    'VALANCE': {
        'Valance Board': 'VALANCE_BOARD',
        'Cover': 'VALANCE_COVER',
        'Left Panel': 'VALANCE_LEFT_PANEL',
        'Right Panel': 'VALANCE_RIGHT_PANEL',
    },
    'SUPPORT_FRAME': SUPPORT_FRAME_LEGACY_NAMES,
    'HALF_WALL': {
        'Left End': 'HALF_WALL_LEFT_END',
        'Right End': 'HALF_WALL_RIGHT_END',
        'Top': 'HALF_WALL_TOP',
        'Bottom': 'HALF_WALL_BOTTOM',
        'Front Skin': 'HALF_WALL_FRONT_SKIN',
        'Back Skin': 'HALF_WALL_BACK_SKIN',
        'Stud': 'HALF_WALL_STUD',
    },
    'LEG': {
        'Front': 'LEG_FRONT',
        'Toe Kick Front': 'LEG_KICK_FRONT',
        'Left Panel': 'LEG_LEFT_PANEL',
        'Right Panel': 'LEG_RIGHT_PANEL',
    },
    'UPPER_LEG': {
        'Front': 'LEG_FRONT',
        'Top': 'LEG_TOP',
        'Bottom': 'LEG_BOTTOM',
        'Left Panel': 'LEG_LEFT_PANEL',
        'Right Panel': 'LEG_RIGHT_PANEL',
    },
    'PANEL': {
        'Panel Board': 'PANEL_BOARD',
    },
}

# Array modifier carrying a product's repeated part (frame supports,
# half wall studs).
ARRAY_MOD_NAME = 'Qty'

# Corner notch modifier on a leg's side panels.
NOTCH_MOD_NAME = 'Notch'

# LED channel modifier on a floating shelf's top / bottom boards.
LED_ROUTE_MOD_NAME = 'LED Route'


def is_product(obj):
    """True for a product's root (cage) object."""
    return (obj is not None
            and bool(obj.get('IS_FRAMELESS_PRODUCT_CAGE'))
            and 'PART_TYPE' in obj)


def product_root(obj):
    """The product root at or above ``obj``, or None."""
    while obj is not None:
        if is_product(obj):
            return obj
        obj = obj.parent
    return None


def _legacy_role(product_obj, child):
    names = LEGACY_PART_NAMES.get(product_obj.get('PART_TYPE'), {})
    base = child.name.split('.')[0]
    if product_obj.get('PART_TYPE') == 'HALF_WALL' and base == 'Right End':
        # Older half walls created their top and bottom boards under the
        # right end's name. The end stands on edge; of the two flat
        # boards only the top hangs from its face.
        if abs(child.rotation_euler.x) > 1e-6:
            return 'HALF_WALL_RIGHT_END'
        try:
            hangs = bool(GeoNodeCutpart(child).get_input('Mirror Z'))
        except Exception:
            hangs = child.location.z > 1e-6
        return 'HALF_WALL_TOP' if hangs else 'HALF_WALL_BOTTOM'
    return names.get(base)


def product_parts(product_obj):
    """``{role: object}`` for the parts of one product."""
    parts = {}
    for child in product_obj.children:
        role = child.get(PART_ROLE_KEY)
        if role is None:
            role = child.get(SUPPORT_FRAME_PART_KEY)
        if role is None:
            role = _legacy_role(product_obj, child)
        if role is not None and role not in parts:
            parts[role] = child
    return parts


def _set_array(part_obj, count, offset_z):
    """Lay a part out ``count`` times along its own Z. The part is built on
    its side, so the product's width runs along the part's Z."""
    set_array(part_obj, ARRAY_MOD_NAME, count, offset_z)


def recalculate_product(obj):
    """Size and place every part of a product from its prompts.

    Accepts the product root or any part of it, so property callbacks and
    menu commands can hand it whatever the user had selected.
    """
    root = product_root(obj)
    if root is None:
        return
    solver = _SOLVERS.get(root.get('PART_TYPE'))
    if solver is None:
        return
    parts = product_parts(root)
    if not parts:
        return
    for role, part_obj in parts.items():
        _clear_drivers(part_obj)
        # A product matched on its part names carries no tags yet; stamp
        # them now so the next solve finds its parts by tag.
        part_obj[PART_ROLE_KEY] = role

    cage = GeoNodeCage(root)
    solver(root, parts,
           cage.get_input('Dim X'), cage.get_input('Dim Y'),
           cage.get_input('Dim Z'))


def upgrade_products(scene=None):
    """Re-solve every product in the file.

    Run on load so a product saved by an older build sheds its drivers and
    comes back at the size it was saved at, rather than waiting for
    something to touch it.
    """
    scenes = [scene] if scene is not None else list(bpy.data.scenes)
    seen = set()
    for scn in scenes:
        for obj in scn.objects:
            if not is_product(obj) or obj.name in seen:
                continue
            seen.add(obj.name)
            try:
                recalculate_product(obj)
            except Exception:
                # One bad product must not stop a file from opening.
                pass


def upgrade_support_frames(scene=None):
    upgrade_products(scene)


# ---------------------------------------------------------------------------
# Product base
# ---------------------------------------------------------------------------

class Product(GeoNodeCage):
    """Base class for frameless products (non-cabinet products).

    Products use IS_FRAMELESS_PRODUCT_CAGE marker so they appear in Cabinets
    selection mode but are distinguishable from actual cabinets.

    Parts are created at rest by ``add_part`` and then sized and placed by
    the product's solver (see ``recalculate_product``).
    """

    width = inch(36)
    height = inch(34.5)
    depth = inch(24)

    def add_properties_common(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Material Thickness', 'DISTANCE', props.default_carcass_part_thickness)

    def create_product(self, name):
        """Create the product cage object with standard markers."""
        super().create(name)
        self.obj['IS_FRAMELESS_PRODUCT_CAGE'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'
        self.obj.display_type = 'WIRE'

        self.set_input('Dim X', self.width)
        self.set_input('Dim Y', self.depth)
        self.set_input('Dim Z', self.height)
        self.set_input('Mirror Y', True)

    def add_part(self, name, role, rotation=(0, 0, 0), mirror=(),
                 part_cls=CabinetPart, finish=None):
        """One product part, parented and tagged. Size and position are
        the solver's to write, so only the fixed orientation is set here."""
        return _add_part(self.obj, name, role, rotation, mirror, part_cls,
                         finish)

    def solve(self):
        recalculate_product(self.obj)


def _add_part(root, name, role, rotation=(0, 0, 0), mirror=(),
              part_cls=CabinetPart, finish=None):
    """One part under the product ``root``, parented and tagged."""
    part = part_cls()
    part.create(name)
    part.obj.parent = root
    part.obj[PART_ROLE_KEY] = role
    part.obj.rotation_euler = tuple(math.radians(a) for a in rotation)
    for axis in mirror:
        part.set_input('Mirror ' + axis, True)
    if finish is not None:
        part.obj['Finish Top'] = finish[0]
        part.obj['Finish Bottom'] = finish[1]
    return part


# A left end panel built mirrored in Z as well faces out on its top
# surface, not the bottom the finish flags assume by default.
LEFT_MIRRORED_FINISH = (True, False)


def _finish_faces(part, finish):
    """Put a part's finish flags right (parts built before they were);
    the next style update paints them."""
    part['Finish Top'], part['Finish Bottom'] = finish


# ---------------------------------------------------------------------------
# Floating shelf
# ---------------------------------------------------------------------------

def _solve_floating_shelf(root, parts, dim_x, dim_y, dim_z):
    get = root.get
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    fl = bool(get('Finish Left', True))
    fr = bool(get('Finish Right', True))
    left_in = mt if fl else 0.0
    right_in = mt if fr else 0.0
    route_depth = float(_prompt(root, 'LED Route Depth', inch(0.25)))

    part = parts.get('SHELF_FRONT')
    if part is not None:
        _set_part(part, (0.0, -dim_y, 0.0),
                  length=dim_x, width=dim_z, thickness=mt)

    part = parts.get('SHELF_TOP')
    if part is not None:
        _set_part(part, (left_in, -dim_y + mt, dim_z),
                  length=dim_x - left_in - right_in, width=dim_y - mt,
                  thickness=mt)
        inset = float(_prompt(root, 'LED Inset Top', inch(2)))
        width = float(_prompt(root, 'LED Width Top', inch(0.5)))
        _set_modifier(part, LED_ROUTE_MOD_NAME,
                      inputs=(('X', -0.01), ('Y', inset), ('End X', dim_x),
                              ('End Y', inset + width),
                              ('Route Depth', route_depth)),
                      visible=bool(get('Include LED Route Top', False)))

    part = parts.get('SHELF_BOTTOM')
    if part is not None:
        _set_part(part, (left_in, -dim_y + mt, 0.0),
                  length=dim_x - left_in - right_in, width=dim_y - mt,
                  thickness=mt)
        inset = float(_prompt(root, 'LED Inset Bottom', inch(2)))
        width = float(_prompt(root, 'LED Width Bottom', inch(0.5)))
        _set_modifier(part, LED_ROUTE_MOD_NAME,
                      inputs=(('X', -0.01), ('Y', inset), ('End X', dim_x),
                              ('End Y', inset + width),
                              ('Route Depth', route_depth)),
                      visible=bool(get('Include LED Route Bottom', False)))

    part = parts.get('SHELF_LEFT_PANEL')
    if part is not None:
        _finish_faces(part, LEFT_MIRRORED_FINISH)
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_y - mt, width=dim_z, thickness=mt, visible=fl)

    part = parts.get('SHELF_RIGHT_PANEL')
    if part is not None:
        _set_part(part, (dim_x, 0.0, 0.0),
                  length=dim_y - mt, width=dim_z, thickness=mt, visible=fr)


class FloatingShelf(Product):
    """Floating shelf mounted on wall.

    Dim X = shelf width, Dim Y = shelf depth, Dim Z = shelf thickness.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = inch(12)
        self.height = inch(2.5)

    def add_properties(self):
        self.add_property('Finish Left', 'CHECKBOX', True)
        self.add_property('Finish Right', 'CHECKBOX', True)
        self.add_property('Include LED Route Bottom', 'CHECKBOX', False)
        self.add_property('Include LED Route Top', 'CHECKBOX', False)
        self.add_property('LED Width Top', 'DISTANCE', inch(0.5))
        self.add_property('LED Width Bottom', 'DISTANCE', inch(0.5))
        self.add_property('LED Inset Top', 'DISTANCE', inch(2))
        self.add_property('LED Inset Bottom', 'DISTANCE', inch(2))
        self.add_property('LED Route Depth', 'DISTANCE', inch(.25))

    def create(self, name="Floating Shelf"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'FLOATING_SHELF'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_floating_shelf_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Front', 'SHELF_FRONT', rotation=(-90, 0, 0), mirror='Y')

        top = self.add_part('Top', 'SHELF_TOP', mirror='Z')
        led_route = top.add_part_modifier('CPM_CUTOUT', LED_ROUTE_MOD_NAME)
        led_route.set_input('Flip Z', True)

        bottom = self.add_part('Bottom', 'SHELF_BOTTOM')
        led_route = bottom.add_part_modifier('CPM_CUTOUT', LED_ROUTE_MOD_NAME)
        led_route.set_input('Flip Z', False)

        self.add_part('Left Panel', 'SHELF_LEFT_PANEL', rotation=(-90, 0, 90),
                      mirror='XYZ', finish=LEFT_MIRRORED_FINISH)
        self.add_part('Right Panel', 'SHELF_RIGHT_PANEL', rotation=(-90, 0, 90),
                      mirror='XY')

        self.solve()


# ---------------------------------------------------------------------------
# Valance
# ---------------------------------------------------------------------------

def _solve_valance(root, parts, dim_x, dim_y, dim_z):
    get = root.get
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    tsa = float(_prompt(root, 'Top Scribe Amount', inch(0.5)))
    fl = bool(get('Finish Left', False))
    fr = bool(get('Finish Right', False))
    left_in = mt if fl else 0.0
    right_in = mt if fr else 0.0

    part = parts.get('VALANCE_BOARD')
    if part is not None:
        _set_part(part, (0.0, -dim_y, 0.0),
                  length=dim_x, width=dim_z, thickness=mt)

    part = parts.get('VALANCE_COVER')
    if part is not None:
        z = 0.0 if get('Flush Bottom', False) else dim_z - tsa - mt
        _set_part(part, (left_in, -dim_y + mt, z),
                  length=dim_x - left_in - right_in, width=dim_y - mt,
                  thickness=mt, visible=not get('Remove Cover', False))

    part = parts.get('VALANCE_LEFT_PANEL')
    if part is not None:
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_y - mt, width=dim_z, thickness=mt, visible=fl)

    part = parts.get('VALANCE_RIGHT_PANEL')
    if part is not None:
        _set_part(part, (dim_x, 0.0, 0.0),
                  length=dim_y - mt, width=dim_z, thickness=mt, visible=fr)


class Valance(Product):
    """Decorative front-facing board.

    A thin board oriented vertically on the front face.
    Dim X = width, Dim Y = depth, Dim Z = height.
    Placed like an upper cabinet.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = props.default_cabinet_width
        self.depth = props.upper_cabinet_depth
        self.height = inch(4)

    def add_properties(self):
        self.add_property('Top Scribe Amount', 'DISTANCE', inch(.5))
        self.add_property('Finish Left', 'CHECKBOX', False)
        self.add_property('Finish Right', 'CHECKBOX', False)
        self.add_property('Remove Cover', 'CHECKBOX', False)
        self.add_property('Flush Bottom', 'CHECKBOX', False)

    def create(self, name="Valance"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'VALANCE'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_valance_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Valance Board', 'VALANCE_BOARD', rotation=(-90, 0, 0),
                      mirror='Y', finish=(True, True))
        self.add_part('Cover', 'VALANCE_COVER', finish=(False, True))
        self.add_part('Left Panel', 'VALANCE_LEFT_PANEL', rotation=(-90, 0, 90),
                      mirror='XYZ', finish=(True, True))
        self.add_part('Right Panel', 'VALANCE_RIGHT_PANEL', rotation=(-90, 0, 90),
                      mirror='XY', finish=(True, True))

        self.solve()


# ---------------------------------------------------------------------------
# Support frame
# ---------------------------------------------------------------------------

# Leg Type prompt: index into ["Inset", "Wrapped"]. A wrapped leg stands
# proud of the frame and the rails stop short of it; an inset leg tucks
# inside, so the rails run past it and only the material thickness is lost.
LEG_TYPE_WRAPPED = 1


def is_support_frame(obj):
    """True for a support frame's root (cage) object."""
    return obj is not None and obj.get('PART_TYPE') == 'SUPPORT_FRAME'


def support_frame_root(obj):
    """The support frame root at or above ``obj``, or None."""
    while obj is not None:
        if is_support_frame(obj):
            return obj
        obj = obj.parent
    return None


def support_frame_parts(frame_obj):
    """``{role: object}`` for the parts of one support frame."""
    return product_parts(frame_obj)


def recalculate_support_frame(obj):
    """Solve the support frame at or above ``obj``."""
    recalculate_product(support_frame_root(obj))


def _solve_support_frame(root, parts, dim_x, dim_y, dim_z):
    get = root.get
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    spacing = float(_prompt(root, 'Support Spacing', inch(16)))
    leg_w = float(_prompt(root, 'Leg Width', inch(3.5)))
    leg_d = float(_prompt(root, 'Leg Depth', inch(3.5)))
    leg_h = float(_prompt(root, 'Leg Height', inch(34.5)))

    legs = {
        'FRONT_LEFT_LEG': (bool(get('Front Left Leg', True)),
                           int(get('Front Left Leg Type', 0))),
        'FRONT_RIGHT_LEG': (bool(get('Front Right Leg', True)),
                            int(get('Front Right Leg Type', 0))),
        'BACK_LEFT_LEG': (bool(get('Back Left Leg', True)),
                          int(get('Back Left Leg Type', 0))),
        'BACK_RIGHT_LEG': (bool(get('Back Right Leg', True)),
                           int(get('Back Right Leg Type', 0))),
    }

    def wrapped(role):
        """True when that corner carries a leg the rails must stop at."""
        on, leg_type = legs[role]
        return on and leg_type == LEG_TYPE_WRAPPED

    # How much each corner takes out of the rail running into it: the leg
    # itself where the leg wraps the frame, otherwise just the rail it
    # butts against.
    fl_y = leg_d if wrapped('FRONT_LEFT_LEG') else mt
    fr_y = leg_d if wrapped('FRONT_RIGHT_LEG') else mt
    bl_y = leg_d if wrapped('BACK_LEFT_LEG') else mt
    br_y = leg_d if wrapped('BACK_RIGHT_LEG') else mt
    bl_x = leg_w if wrapped('BACK_LEFT_LEG') else 0.0
    br_x = leg_w if wrapped('BACK_RIGHT_LEG') else 0.0
    fl_x = leg_w if wrapped('FRONT_LEFT_LEG') else 0.0
    fr_x = leg_w if wrapped('FRONT_RIGHT_LEG') else 0.0

    part = parts.get('LEFT_RAIL')
    if part is not None:
        _finish_faces(part, LEFT_MIRRORED_FINISH)
        _set_part(part, (0.0, -bl_y, 0.0),
                  length=dim_y - fl_y - bl_y, width=dim_z, thickness=mt,
                  visible=bool(get('Left Rail', True)))

    part = parts.get('RIGHT_RAIL')
    if part is not None:
        _set_part(part, (dim_x, -br_y, 0.0),
                  length=dim_y - fr_y - br_y, width=dim_z, thickness=mt,
                  visible=bool(get('Right Rail', True)))

    part = parts.get('FRONT_RAIL')
    if part is not None:
        _set_part(part, (fl_x, -dim_y, 0.0),
                  length=dim_x - fl_x - fr_x, width=dim_z, thickness=mt,
                  visible=bool(get('Front Rail', True)))

    part = parts.get('BACK_RAIL')
    if part is not None:
        _set_part(part, (bl_x, 0.0, 0.0),
                  length=dim_x - bl_x - br_x, width=dim_z, thickness=mt,
                  visible=bool(get('Back Rail', True)))

    part = parts.get('SUPPORT')
    if part is not None:
        # Intermediate supports are one part arrayed across the frame, so
        # the count is how many whole spacings fit inside the rails.
        count = 0
        if spacing > 0.0:
            count = int(math.floor((dim_x - mt * 2.0 - spacing) / spacing)) + 1
            count = max(count, 0)
        _set_part(part, (spacing, -mt, 0.0),
                  length=dim_y - mt * 2.0, width=dim_z, thickness=mt,
                  visible=count > 0)
        _set_array(part, count, -spacing)

    # Legs hang from the top of the frame down to the floor. An inset leg
    # sits inside the rails by their thickness; a wrapped leg sits at the
    # frame's outside face, with the rails stopped short of it above.
    leg_specs = {
        'FRONT_LEFT_LEG': ((mt, -(dim_y - mt)), (0.0, -dim_y), leg_w, leg_d),
        'FRONT_RIGHT_LEG': ((dim_x - mt, -(dim_y - mt)), (dim_x, -dim_y),
                            leg_d, leg_w),
        'BACK_LEFT_LEG': ((mt, -mt), (0.0, 0.0), leg_d, leg_w),
        'BACK_RIGHT_LEG': ((dim_x - mt, -mt), (dim_x, 0.0), leg_w, leg_d),
    }
    for role, (inset_xy, wrapped_xy, width, thickness) in leg_specs.items():
        part = parts.get(role)
        if part is None:
            continue
        on, leg_type = legs[role]
        x, y = wrapped_xy if leg_type == LEG_TYPE_WRAPPED else inset_xy
        _set_part(part, (x, y, dim_z),
                  length=leg_h, width=width, thickness=thickness,
                  visible=on)


class SupportFrame(Product):
    """Open rectangular frame (sides, top, bottom).

    Used for supporting countertop overhangs, peninsulas, etc.
    Has configurable legs at each corner with inset or wrapped options.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(60)
        self.height = inch(4)
        self.depth = inch(24)

    def add_properties(self):
        self.add_property('Support Spacing', 'DISTANCE', inch(16))
        # Per-side band toggles: turning a side off makes an L / U shaped
        # frame (e.g. wrap the back + one side of an island to carry an
        # overhang, leaving the cabinet faces clear).
        self.add_property('Front Rail', 'CHECKBOX', True)
        self.add_property('Back Rail', 'CHECKBOX', True)
        self.add_property('Left Rail', 'CHECKBOX', True)
        self.add_property('Right Rail', 'CHECKBOX', True)
        self.add_property('Front Left Leg', 'CHECKBOX', True)
        self.add_property('Front Right Leg', 'CHECKBOX', True)
        self.add_property('Back Left Leg', 'CHECKBOX', True)
        self.add_property('Back Right Leg', 'CHECKBOX', True)
        self.add_property('Leg Width', 'DISTANCE', inch(3.5))
        self.add_property('Leg Depth', 'DISTANCE', inch(3.5))
        self.add_property('Leg Height', 'DISTANCE', inch(34.5))
        self.add_property('Front Left Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Front Right Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Back Left Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        self.add_property('Back Right Leg Type', 'COMBOBOX', 0, combobox_items=["Inset", "Wrapped"])
        # Square posts, or a vendor turning built into each post (see
        # common/turned_leg): the prompts dialog rebuilds the legs on change.
        from ..common import turned_leg
        self.add_property(turned_leg.LEG_STYLE_PROP, 'COMBOBOX', 0,
                          combobox_items=turned_leg.style_items())

    def create(self, name="Support Frame"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'SUPPORT_FRAME'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_support_frame_commands'

        self.add_properties_common()
        self.add_properties()

        # ---- RAILS ----
        self.add_part('Left Panel', 'LEFT_RAIL', rotation=(-90, 0, 90),
                      mirror='XYZ', finish=LEFT_MIRRORED_FINISH)
        self.add_part('Right Panel', 'RIGHT_RAIL', rotation=(-90, 0, 90),
                      mirror='XY')
        self.add_part('Front Panel', 'FRONT_RAIL', rotation=(90, 0, 0),
                      mirror='Z')
        self.add_part('Back Panel', 'BACK_RAIL', rotation=(90, 0, 0))

        # ---- INTERMEDIATE SUPPORTS ----
        support = self.add_part('Support', 'SUPPORT', rotation=(-90, 0, 90),
                                mirror='XYZ', finish=(False, False))
        array_mod = support.obj.modifiers.new(ARRAY_MOD_NAME, 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)

        # ---- LEGS ----
        for part_name, role, rotation in (
                ('Front Left Leg', 'FRONT_LEFT_LEG', (0, -90, -90)),
                ('Front Right Leg', 'FRONT_RIGHT_LEG', (0, -90, 0)),
                ('Back Left Leg', 'BACK_LEFT_LEG', (0, -90, 180)),
                ('Back Right Leg', 'BACK_RIGHT_LEG', (0, -90, 90))):
            self.add_part(part_name, role, rotation=rotation, mirror='X',
                          finish=(True, True))

        self.solve()


# ---------------------------------------------------------------------------
# Half wall
# ---------------------------------------------------------------------------

def _solve_half_wall(root, parts, dim_x, dim_y, dim_z):
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    st = float(_prompt(root, 'Stud Thickness', inch(0.75)))
    ssp = float(_prompt(root, 'Stud Spacing', inch(16)))
    esfe = float(_prompt(root, 'End Stud From Edge', inch(1.5)))

    part = parts.get('HALF_WALL_LEFT_END')
    if part is not None:
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_z, width=dim_y, thickness=mt)

    part = parts.get('HALF_WALL_RIGHT_END')
    if part is not None:
        _set_part(part, (dim_x, 0.0, 0.0),
                  length=dim_z, width=dim_y, thickness=mt)

    part = parts.get('HALF_WALL_TOP')
    if part is not None:
        _set_part(part, (mt, -st, dim_z),
                  length=dim_x - mt * 2.0, width=dim_y - st * 2.0,
                  thickness=mt)

    part = parts.get('HALF_WALL_BOTTOM')
    if part is not None:
        _set_part(part, (mt, -st, 0.0),
                  length=dim_x - mt * 2.0, width=dim_y - st * 2.0,
                  thickness=mt)

    part = parts.get('HALF_WALL_FRONT_SKIN')
    if part is not None:
        _set_part(part, (mt, -dim_y, 0.0),
                  length=dim_x - mt * 2.0, width=dim_z, thickness=st)

    part = parts.get('HALF_WALL_BACK_SKIN')
    if part is not None:
        _set_part(part, (mt, 0.0, 0.0),
                  length=dim_x - mt * 2.0, width=dim_z, thickness=st)

    part = parts.get('HALF_WALL_STUD')
    if part is not None:
        count = 1
        if ssp > 0.0:
            count = int(math.floor((dim_x - mt * 2.0 - esfe * 2.0) / ssp)) + 1
        _set_part(part, (mt + esfe, -st, mt),
                  length=dim_z - mt * 2.0, width=dim_y - st * 2.0,
                  thickness=st)
        _set_array(part, count, -ssp)


class HalfWall(Product):
    """Pony wall / knee wall.

    Constructed with studs, skins, and optional finished end caps.
    """

    def __init__(self):
        super().__init__()
        self.width = inch(36)
        self.height = inch(42)
        self.depth = inch(6)

    def add_properties(self):
        self.add_property('Stud Thickness', 'DISTANCE', inch(.75))
        self.add_property('Skin Thickness', 'DISTANCE', inch(0.25))
        self.add_property('Stud Spacing', 'DISTANCE', inch(16))
        self.add_property('End Stud From Edge', 'DISTANCE', inch(1.5))
        self.add_property('Left End Cap', 'CHECKBOX', False)
        self.add_property('Right End Cap', 'CHECKBOX', False)
        self.add_property('Finished End Setback', 'DISTANCE', inch(0))
        self.add_property('Left Finished Revel', 'DISTANCE', inch(0))
        self.add_property('Right Finished Revel', 'DISTANCE', inch(0))
        self.add_property('Finish Front', 'CHECKBOX', True)
        self.add_property('Finish Back', 'CHECKBOX', False)

    def create(self, name="Half Wall"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'HALF_WALL'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_half_wall_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Left End', 'HALF_WALL_LEFT_END', rotation=(90, -90, -90),
                      mirror='YZ', finish=(True, True))
        self.add_part('Right End', 'HALF_WALL_RIGHT_END', rotation=(90, -90, -90),
                      mirror='Y', finish=(True, True))
        self.add_part('Top', 'HALF_WALL_TOP', mirror='YZ', finish=(False, False))
        self.add_part('Bottom', 'HALF_WALL_BOTTOM', mirror='Y', finish=(False, False))
        self.add_part('Front Skin', 'HALF_WALL_FRONT_SKIN', rotation=(90, 0, 0),
                      mirror='Z', finish=(True, True))
        self.add_part('Back Skin', 'HALF_WALL_BACK_SKIN', rotation=(90, 0, 0),
                      finish=(True, True))

        stud = self.add_part('Stud', 'HALF_WALL_STUD', rotation=(90, -90, -90),
                             mirror='YZ', finish=(False, False))
        array_mod = stud.obj.modifiers.new(ARRAY_MOD_NAME, 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)

        self.solve()


# ---------------------------------------------------------------------------
# Misc part
# ---------------------------------------------------------------------------

class MiscPart(CabinetPart):
    """A single freely-resizable cabinet part with no cage wrapper.

    Uses IS_FRAMELESS_MISC_PART marker so it does not appear in
    Cabinets selection mode.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(24)
        self.height = props.default_carcass_part_thickness
        self.depth = inch(12)

    def create(self, name="Misc Part"):
        super().create(name)
        self.obj['IS_FRAMELESS_MISC_PART'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'
        self.set_input('Length', self.width)
        self.set_input('Width', self.depth)
        self.set_input('Thickness', self.height)
        self.set_input('Mirror Y', True)
        self.obj['Finish Top'] = True
        self.obj['Finish Bottom'] = True


# ---------------------------------------------------------------------------
# Legs
# ---------------------------------------------------------------------------

# Finish Type prompt: index into ["Left", "Right", "Both"].
FINISH_LEFT, FINISH_RIGHT, FINISH_BOTH = 0, 1, 2


def _leg_side_panel(root, parts, role, x, dim_y, mt, z, length,
                    override_name, finish_sides, notch=None):
    part = parts.get(role)
    if part is None:
        return
    override = float(_prompt(root, override_name, 0.0))
    # An override depth of zero means the panel runs the full depth.
    if override <= 0.0:
        y, width = 0.0, dim_y - mt
    else:
        y, width = -dim_y + mt + override, override
    visible = (not bool(root.get('Only Include Filler', False))
               and int(_prompt(root, 'Finish Type', 0)) in finish_sides)
    _set_part(part, (x, y, z), length=length, width=width, thickness=mt,
              visible=visible)
    if notch is not None:
        _set_modifier(part, NOTCH_MOD_NAME, inputs=notch)


def _solve_leg(root, parts, dim_x, dim_y, dim_z):
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    tkh = float(_prompt(root, 'Toe Kick Height', 0.0))
    tks = float(_prompt(root, 'Toe Kick Setback', 0.0))

    part = parts.get('LEG_FRONT')
    if part is not None:
        _set_part(part, (0.0, -dim_y, tkh),
                  length=dim_z - tkh, width=dim_x, thickness=mt)

    part = parts.get('LEG_KICK_FRONT')
    if part is not None:
        _set_part(part, (0.0, -dim_y + tks, 0.0),
                  length=tkh, width=dim_x, thickness=mt, visible=tkh > 0.0)

    notch = (('X', tkh), ('Y', tks), ('Route Depth', mt))
    _leg_side_panel(root, parts, 'LEG_LEFT_PANEL', 0.0, dim_y, mt, 0.0, dim_z,
                    'Override Left Panel Depth', (FINISH_LEFT, FINISH_BOTH),
                    notch=notch)
    _leg_side_panel(root, parts, 'LEG_RIGHT_PANEL', dim_x, dim_y, mt, 0.0, dim_z,
                    'Override Right Panel Depth', (FINISH_RIGHT, FINISH_BOTH),
                    notch=notch)


def _solve_upper_leg(root, parts, dim_x, dim_y, dim_z):
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))

    part = parts.get('LEG_FRONT')
    if part is not None:
        _set_part(part, (0.0, -dim_y, 0.0),
                  length=dim_z, width=dim_x, thickness=mt)

    part = parts.get('LEG_TOP')
    if part is not None:
        _set_part(part, (0.0, 0.0, dim_z),
                  length=dim_x, width=dim_y - mt, thickness=mt)

    part = parts.get('LEG_BOTTOM')
    if part is not None:
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_x, width=dim_y - mt, thickness=mt)

    _leg_side_panel(root, parts, 'LEG_LEFT_PANEL', 0.0, dim_y, mt, mt,
                    dim_z - mt * 2.0, 'Override Left Panel Depth',
                    (FINISH_LEFT, FINISH_BOTH))
    _leg_side_panel(root, parts, 'LEG_RIGHT_PANEL', dim_x, dim_y, mt, mt,
                    dim_z - mt * 2.0, 'Override Right Panel Depth',
                    (FINISH_RIGHT, FINISH_BOTH))


class Leg(Product):
    """Vertical Leg.

    A narrow square-profile vertical part with toe kick and panel options.
    Dim X = width, Dim Y = depth, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(2)
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth

    def add_properties(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Toe Kick Height', 'DISTANCE', props.default_toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', props.default_toe_kick_setback)
        #Override Depth == 0 means full depth
        self.add_property('Override Left Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Override Right Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Only Include Filler', 'CHECKBOX', False)
        self.add_property('Finish Type', 'COMBOBOX', 0, combobox_items=["Left", "Right", "Both"])

    def create(self, name="Leg"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'LEG'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_leg_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Front', 'LEG_FRONT', rotation=(-90, -90, 0))
        self.add_part('Toe Kick Front', 'LEG_KICK_FRONT', rotation=(-90, -90, 0))
        self.add_part('Left Panel', 'LEG_LEFT_PANEL', rotation=(0, -90, 0),
                      mirror='ZY', part_cls=CabinetSideNotched)
        self.add_part('Right Panel', 'LEG_RIGHT_PANEL', rotation=(0, -90, 0),
                      mirror='Y', part_cls=CabinetSideNotched)

        self.solve()


class TallLeg(Leg):
    """Vertical Leg for tall cabinets.

    Same construction as base Leg but with tall cabinet default sizes.
    Dim X = width, Dim Y = depth, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(2)
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth

    def create(self, name="Tall Leg"):
        super().create(name)


class UpperLeg(Product):
    """Vertical Leg for upper cabinets.

    No toe kick. Includes top and bottom panels.
    Placed at upper cabinet height above the floor.
    Dim X = width, Dim Y = depth, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(2)
        self.height = props.upper_cabinet_height
        self.depth = props.upper_cabinet_depth

    def add_properties(self):
        self.add_property('Override Left Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Override Right Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Only Include Filler', 'CHECKBOX', False)
        self.add_property('Finish Type', 'COMBOBOX', 0, combobox_items=["Left", "Right", "Both"])

    def create(self, name="Upper Leg"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'UPPER_LEG'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_leg_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Front', 'LEG_FRONT', rotation=(-90, -90, 0))
        self.add_part('Top', 'LEG_TOP', mirror='ZY')
        self.add_part('Bottom', 'LEG_BOTTOM', mirror='Y')
        self.add_part('Left Panel', 'LEG_LEFT_PANEL', rotation=(0, -90, 0),
                      mirror='ZY')
        self.add_part('Right Panel', 'LEG_RIGHT_PANEL', rotation=(0, -90, 0),
                      mirror='Y')

        self.solve()


# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

def _solve_panel(root, parts, dim_x, dim_y, dim_z):
    part = parts.get('PANEL_BOARD')
    if part is not None:
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_z, width=dim_y, thickness=dim_x)


class Panel(Product):
    """Single flat vertical panel (filler, end panel, etc).

    A thin vertical board.
    Dim X = width, Dim Y = thickness, Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(3)
        self.height = props.base_cabinet_height
        self.depth = props.default_carcass_part_thickness

    def create(self, name="Panel"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'PANEL'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'

        self.add_part('Panel Board', 'PANEL_BOARD', rotation=(0, -90, 0),
                      mirror='YZ', finish=(True, True))

        self.solve()


# ---------------------------------------------------------------------------
# Corner filler
# ---------------------------------------------------------------------------

CORNER_FILLER_WIDTH = inch(1.5)
CORNER_FILLER_RETURN = inch(3.0)


def corner_filler_width():
    """The room's corner filler face width (Cabinet Sizes)."""
    props = getattr(bpy.context.scene, 'hb_frameless', None)
    return float(getattr(props, 'corner_filler_width', CORNER_FILLER_WIDTH))


def corner_filler_return():
    """The room's corner filler return depth (Cabinet Sizes)."""
    props = getattr(bpy.context.scene, 'hb_frameless', None)
    return float(getattr(props, 'corner_filler_return', CORNER_FILLER_RETURN))


def scribe_filler_flush_with_doors():
    """Whether the room's new wall scribe fillers stand out in the door
    plane (Cabinet Sizes); otherwise their face is flush with the
    carcass front."""
    props = getattr(bpy.context.scene, 'hb_frameless', None)
    return bool(getattr(props, 'scribe_filler_flush_with_doors', False))


def scribe_filler_toe_kick_piece():
    """Whether the room's new wall scribe fillers on a base or tall
    come in with a kick piece under the face (Cabinet Sizes)."""
    props = getattr(bpy.context.scene, 'hb_frameless', None)
    return bool(getattr(props, 'scribe_filler_toe_kick_piece', False))


# How far the door fronts stand off the carcass; the filler's face is
# set to line up with them.
FRONT_THICKNESS = inch(0.75)


def product_front_setback(root):
    """How far behind the front of its cage a product's own front
    stands. A wall scribe filler's cage always reaches the door plane;
    flush with the carcass, its face is a front thickness behind that."""
    if (root.get('PART_TYPE') in ('CORNER_FILLER', 'L_CROWN')
            and not root.get('Flush With Doors', True)):
        return FRONT_THICKNESS
    return 0.0


def product_depth(root):
    """The product's depth as built: wall to its own front."""
    return GeoNodeCage(root).get_input('Dim Y') - product_front_setback(root)


def set_product_depth(root, depth):
    GeoNodeCage(root).set_input('Dim Y', depth + product_front_setback(root))


# A panel closing the gap under an upper's wall scribe filler.
BOTTOM_RETURN_KEY = 'Bottom Return'


def _paint_product(root):
    """Paint a product's parts from its style, by their finish flags."""
    from ... import hb_project
    styles = hb_project.get_main_scene().hb_frameless.cabinet_styles
    if not len(styles):
        return
    index = root.get('CABINET_STYLE_INDEX', 0)
    style = styles[index] if 0 <= index < len(styles) else styles[0]
    style.apply_materials_to_cabinet(root)


def _solve_filler_bottom_return(root, parts, dim_x, depth, mt, on):
    """The bottom return of a filler with no kick under it: a panel
    lying behind the face's bottom edge, from the face back to the wall,
    made when the option is switched on and removed when it is off. Its
    underside is finished when the bottom of the cabinet beside the
    filler is."""
    part = parts.get('FILLER_BOTTOM_RETURN')
    if not on:
        if part is not None:
            parts.pop('FILLER_BOTTOM_RETURN')
            bpy.data.objects.remove(part, do_unlink=True)
        return
    made = part is None
    if made:
        new = CabinetPart()
        new.create('Bottom Return')
        part = new.obj
        part.parent = root
        part[PART_ROLE_KEY] = 'FILLER_BOTTOM_RETURN'
        new.set_input('Mirror Y', True)
        parts['FILLER_BOTTOM_RETURN'] = part
    from . import scribe_fit
    finished = scribe_fit.bottom_return_finished(root)
    repaint = made or bool(part.get('Finish Bottom')) != finished
    part['Finish Top'] = False
    part['Finish Bottom'] = finished
    _set_part(part, (0.0, 0.0, 0.0), length=dim_x, width=depth, thickness=mt)
    if repaint:
        try:
            _paint_product(root)
        except Exception:
            pass


def _solve_corner_filler(root, parts, dim_x, dim_y, dim_z):
    """An L in plan. The face runs across the front, in the door plane
    or flush with the carcass front (Dim Y always reaches from the wall
    to the door plane, so the option can be switched either way); the
    return leg stands behind it against the cabinet's side, on whichever
    side the cabinet is; a kick piece sits set back below the face on a
    base or tall."""
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    tkh = float(_prompt(root, 'Toe Kick Height', 0.0))
    tks = float(_prompt(root, 'Toe Kick Setback', 0.0))
    ret = float(_prompt(root, 'Return Depth', CORNER_FILLER_RETURN))
    cab_right = bool(root.get('Cabinet On Right', True))
    # Fillers built before the option stood in the door plane.
    on_doors = bool(root.get('Flush With Doors', True))
    # Off over a separate toe kick platform, which runs on under it.
    kick_on = bool(root.get('Toe Kick Piece', True))
    face_y = -dim_y + (0.0 if on_doors else FRONT_THICKNESS)
    # Under an upper only: a base or tall stands on its kick or the floor.
    bottom_on = bool(root.get(BOTTOM_RETURN_KEY, False)) and tkh <= 0.0
    _solve_filler_bottom_return(root, parts, dim_x, -(face_y + mt), mt,
                                bottom_on)
    # The return leg stands on the bottom return.
    leg_z = tkh + (mt if bottom_on else 0.0)

    part = parts.get('FILLER_FACE')
    if part is not None:
        _set_part(part, (0.0, face_y, tkh),
                  length=dim_z - tkh, width=dim_x, thickness=mt)

    part = parts.get('FILLER_KICK')
    if part is not None:
        _set_part(part, (0.0, face_y + tks, 0.0),
                  length=tkh, width=dim_x, thickness=mt,
                  visible=tkh > 0.0 and kick_on)

    # The return is inside the filler's own width, so it lies against
    # the cabinet side rather than into the cabinet.
    for role, x, on in (('FILLER_LEFT_RETURN', 0.0, not cab_right),
                        ('FILLER_RIGHT_RETURN', dim_x, cab_right)):
        part = parts.get(role)
        if part is not None:
            # A side panel's width runs toward -Y from where it is set,
            # so it is set at its back edge to run from the face's back
            # toward the wall.
            _set_part(part, (x, face_y + mt + ret, leg_z),
                      length=dim_z - leg_z, width=ret, thickness=mt,
                      visible=on)

    # The cage is what gets clicked, so it is drawn back to the filler
    # itself: to the face when that stands behind the door plane, and up
    # off a separate toe kick platform that runs on under it.
    try:
        from . import solver_frameless as sf
        sf.set_cage_clamp(root, sf.KICK_CLEAR_MOD, sf.KICK_CLEAR_GROUP,
                          'Floor', 'Z', tkh, tkh > 0.0 and not kick_on)
        sf.set_cage_clamp(root, sf.FRONT_CLEAR_MOD, sf.FRONT_CLEAR_GROUP,
                          'Front', 'Y', face_y, not on_doors)
    except Exception:
        pass


class CornerFiller(Product):
    """The wall scribe filler that closes an inside corner.

    Where a run meets the wall it stands against, a plain cabinet cannot
    open its door into the corner. This stands between the cabinet's
    end and the wall: a face flush with the carcass front, or in the
    plane of the doors with its Flush With Doors option on (1.5" wide
    unless the room's filler width says otherwise), with a
    return leg behind it to fix to the cabinet side. Placement adds one
    of its own accord when a cabinet lands in an inside corner.
    Dim X = width, Dim Y = reach from the wall to the door face,
    Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = corner_filler_width()
        self.return_depth = corner_filler_return()
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth + FRONT_THICKNESS
        self.toe_kick_height = props.default_toe_kick_height
        self.toe_kick_setback = props.default_toe_kick_setback
        self.cabinet_on_right = True
        self.flush_with_doors = scribe_filler_flush_with_doors()
        self.kick_piece = scribe_filler_toe_kick_piece()

    def add_properties(self):
        self.add_property('Toe Kick Height', 'DISTANCE', self.toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', self.toe_kick_setback)
        self.add_property('Return Depth', 'DISTANCE', self.return_depth)
        self.add_property('Cabinet On Right', 'CHECKBOX', self.cabinet_on_right)
        self.add_property('Flush With Doors', 'CHECKBOX', self.flush_with_doors)
        self.add_property('Toe Kick Piece', 'CHECKBOX', self.kick_piece)
        self.add_property(BOTTOM_RETURN_KEY, 'CHECKBOX', False)

    def create(self, name="Wall Scribe Filler"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'CORNER_FILLER'
        self.obj['IS_CORNER_FILLER'] = True
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_part_commands'

        self.add_properties_common()
        self.add_properties()

        self.add_part('Filler Face', 'FILLER_FACE', rotation=(-90, -90, 0))
        self.add_part('Filler Kick', 'FILLER_KICK', rotation=(-90, -90, 0))
        self.add_part('Left Return', 'FILLER_LEFT_RETURN', rotation=(0, -90, 0),
                      mirror='ZY')
        self.add_part('Right Return', 'FILLER_RIGHT_RETURN', rotation=(0, -90, 0),
                      mirror='Y')

        self.solve()


# ---------------------------------------------------------------------------
# Voided corner
# ---------------------------------------------------------------------------

VOIDED_CORNER_FILLER = inch(3.0)


def _voided_type(name):
    if 'Upper' in name:
        return 'UPPER'
    if 'Tall' in name:
        return 'TALL'
    return 'BASE'


def _solve_voided_corner(root, parts, dim_x, dim_y, dim_z):
    """An L of filler at the inside corner of two runs, at their door
    planes, with the corner behind it left empty.

    Origin at the corner where the walls meet, as a corner cabinet's
    is. The run along the back wall (+X) stands Right Depth deep; the
    run along the side wall (-Y) Left Depth deep. Each face is in the
    plane of the doors of the run it lines up with and runs out by the
    filler width to where that run's first cabinet starts, so the cage
    is that wide each way. The face along the back wall laps the end of
    the other, so the joint reads closed from the room. A return stands
    behind each face's outer edge against the cabinet beside it; a base
    or tall has a kick under each face, set back; any of them can be
    closed over the top or under the bottom of the void."""
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    ld = float(_prompt(root, 'Left Depth', inch(24)))
    rd = float(_prompt(root, 'Right Depth', inch(24)))
    fw = float(_prompt(root, 'Filler Width', VOIDED_CORNER_FILLER))
    ret = float(_prompt(root, 'Return Depth', CORNER_FILLER_RETURN))
    tkh = float(_prompt(root, 'Toe Kick Height', 0.0))
    tks = float(_prompt(root, 'Toe Kick Setback', 0.0))
    top_on = bool(root.get('Top Panel', False))
    bottom_on = bool(root.get('Bottom Panel', False))

    # The faces' fronts, in the door plane of each run.
    fx = ld + FRONT_THICKNESS        # side-wall run's doors (an X)
    fy = -(rd + FRONT_THICKNESS)     # back-wall run's doors (a Y)
    dim_x = fx + fw
    dim_y = rd + FRONT_THICKNESS + fw
    cage = GeoNodeCage(root)
    cage.set_input('Dim X', dim_x)
    cage.set_input('Dim Y', dim_y)

    z0 = tkh
    h = dim_z - tkh
    # Back-wall face, lapping the end of the side-wall face.
    part = parts.get('VC_FACE_BACK')
    if part is not None:
        _set_part(part, (fx - mt, fy, z0), length=h,
                  width=dim_x - fx + mt, thickness=mt)
    part = parts.get('VC_FACE_SIDE')
    if part is not None:
        _set_part(part, (fx - mt, fy, z0), length=h,
                  width=dim_y + fy, thickness=mt)

    part = parts.get('VC_KICK_BACK')
    if part is not None:
        _set_part(part, (fx - tks - mt, fy + tks, 0.0), length=tkh,
                  width=dim_x - fx + tks + mt, thickness=mt,
                  visible=tkh > 0.0)
    part = parts.get('VC_KICK_SIDE')
    if part is not None:
        _set_part(part, (fx - tks - mt, fy + tks, 0.0), length=tkh,
                  width=dim_y + fy + tks, thickness=mt,
                  visible=tkh > 0.0)

    # Returns inside the void, against the first cabinet of each run,
    # between the panels where those are on.
    rz0 = z0 + (mt if bottom_on else 0.0)
    rh = h - (mt if bottom_on else 0.0) - (mt if top_on else 0.0)
    part = parts.get('VC_RETURN_BACK')
    if part is not None:
        _set_part(part, (dim_x, fy + mt + ret, rz0), length=rh,
                  width=ret, thickness=mt, visible=ret > 0.0)
    part = parts.get('VC_RETURN_SIDE')
    if part is not None:
        _set_part(part, (fx - mt, -dim_y, rz0), length=rh,
                  width=ret, thickness=mt, visible=ret > 0.0)

    # The void closed over or under: everything behind the faces, inside
    # the returns - a square with the room's corner notched out of it.
    pw = dim_x - mt
    pd = dim_y - mt
    notch = (('X', dim_x - fx), ('Y', dim_y + fy),
             ('Route Depth', mt + 0.01))
    for role, on, z in (('VC_BOTTOM', bottom_on, z0),
                        ('VC_TOP', top_on, dim_z - mt)):
        part = parts.get(role)
        if part is None:
            continue
        _set_part(part, (0.0, 0.0, z), length=pw, width=pd,
                  thickness=mt, visible=on)
        _set_modifier(part, 'Corner Notch', notch)


class VoidedCorner(Product):
    """A voided corner: two runs meet at the corner and stop short of
    it, and an L of filler closes the gap between their door faces.

    Placed into a corner like a corner cabinet. It is as deep each way
    as the cabinets that meet there plus their doors and the filler, so
    a cabinet placed along either wall stops against it. Base, tall and
    upper; an upper usually closes the bottom of the void, since it is
    seen from below."""

    def __init__(self, cabinet_type='BASE'):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.cabinet_type = cabinet_type
        depth, height = {
            'UPPER': (props.upper_cabinet_depth, props.upper_cabinet_height),
            'TALL': (props.tall_cabinet_depth, props.tall_cabinet_height),
        }.get(cabinet_type, (props.base_cabinet_depth,
                             props.base_cabinet_height))
        self.cabinet_depth = depth
        self.filler_width = VOIDED_CORNER_FILLER
        self.width = depth + FRONT_THICKNESS + self.filler_width
        self.depth = self.width
        self.height = height
        on_floor = cabinet_type != 'UPPER'
        self.toe_kick_height = (props.default_toe_kick_height
                                if on_floor else 0.0)
        self.toe_kick_setback = (props.default_toe_kick_setback
                                 if on_floor else 0.0)

    def create(self, name="Voided Corner"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'VOIDED_CORNER'
        self.obj['IS_VOIDED_CORNER'] = True
        self.obj['CABINET_TYPE'] = self.cabinet_type

        self.add_properties_common()
        self.add_property('Left Depth', 'DISTANCE', self.cabinet_depth)
        self.add_property('Right Depth', 'DISTANCE', self.cabinet_depth)
        self.add_property('Filler Width', 'DISTANCE', self.filler_width)
        self.add_property('Return Depth', 'DISTANCE', corner_filler_return())
        self.add_property('Toe Kick Height', 'DISTANCE', self.toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE',
                          self.toe_kick_setback)
        self.add_property('Top Panel', 'CHECKBOX', False)
        self.add_property('Bottom Panel', 'CHECKBOX',
                          self.cabinet_type == 'UPPER')

        self.add_part('Filler Face', 'VC_FACE_BACK', rotation=(-90, -90, 0))
        self.add_part('Filler Face', 'VC_FACE_SIDE',
                      rotation=(-90, -90, -90))
        self.add_part('Filler Kick', 'VC_KICK_BACK', rotation=(-90, -90, 0))
        self.add_part('Filler Kick', 'VC_KICK_SIDE',
                      rotation=(-90, -90, -90))
        self.add_part('Filler Return', 'VC_RETURN_BACK',
                      rotation=(0, -90, 0), mirror='Y')
        self.add_part('Filler Return', 'VC_RETURN_SIDE',
                      rotation=(0, -90, -90), mirror='Y')
        for name_, role in (('Bottom', 'VC_BOTTOM'), ('Top', 'VC_TOP')):
            part = self.add_part(name_, role, mirror='Y')
            notch = part.add_part_modifier('CPM_CORNERNOTCH', 'Corner Notch')
            notch.set_input('Flip X', True)
            notch.set_input('Flip Y', True)

        self.solve()


class VoidedCornerBase(VoidedCorner):
    def __init__(self):
        super().__init__('BASE')


class VoidedCornerTall(VoidedCorner):
    def __init__(self):
        super().__init__('TALL')


class VoidedCornerUpper(VoidedCorner):
    def __init__(self):
        super().__init__('UPPER')


# ---------------------------------------------------------------------------
# Base assembly
# ---------------------------------------------------------------------------

BASE_ASSEMBLY_SUPPORT_SPACING = inch(16)
# The back rail is held this far off the wall, so the base can be
# scribed and levelled without the rail fouling the wall.
BASE_ASSEMBLY_BACK_GAP = inch(0.25)
BACK_GAP_KEY = 'Back Gap'


# (Finish Top, Finish Bottom) for the parts that show: whichever surface
# faces out of the base. The front and the right end face out on their
# bottom surface; the left end, mirrored in Z as well, on its top.
BASE_ASSEMBLY_FINISH = {
    'BASE_FRONT': (False, True),
    'BASE_LEFT_END': (True, False),
    'BASE_RIGHT_END': (False, True),
}

# Finish options, all off on a new base.
# Finish Rear: an island's base is held in at the back as it is at the
# front, so the rear shows a toe space of its own.
# Loose Finished Skin: finished toe skins, sent loose and fit on site,
# cover the faces of the base that show; the frame is held back by their
# thickness so the skin's face lands where the frame's would have.
# Base by Others: the base finish (a rubber or vinyl base, say) is
# applied on site by someone else; the frame is held back by the typed
# thickness on the same faces and no skins are made. It wins over the
# loose skin: the two are never both on.
FINISH_REAR_KEY = 'Finish Rear'
LOOSE_SKIN_KEY = 'Loose Finished Skin'
BASE_BY_OTHERS_KEY = 'Base by Others'
BASE_BY_OTHERS_THICKNESS_KEY = 'Base by Others Thickness'
BASE_ASSEMBLY_OPTION_KEYS = (FINISH_REAR_KEY, LOOSE_SKIN_KEY,
                             BASE_BY_OTHERS_KEY, BASE_BY_OTHERS_THICKNESS_KEY)
BASE_ASSEMBLY_SKIN_THICKNESS = inch(0.75)
BASE_BY_OTHERS_THICKNESS = inch(0.125)

# What the base was built from, written by whatever stands it under a
# run: which ends show, and how far the kick face stands back from the
# cabinet fronts (the rear is held in by the same when it is finished).
LEFT_END_EXPOSED_KEY = 'Left End Exposed'
RIGHT_END_EXPOSED_KEY = 'Right End Exposed'
REAR_SETBACK_KEY = 'Rear Setback'

# Marks a part that ships loose to be fit on site.
SENT_LOOSE_KEY = 'SENT_LOOSE'

# role: (name, rotation, mirror, finish) -- each skin stands like the
# frame part it covers.
BASE_ASSEMBLY_SKINS = {
    'LOOSE_KICK_FRONT': ("Loose Toe Skin Front", (90, 0, 0), 'Z',
                         (False, True)),
    'LOOSE_KICK_REAR': ("Loose Toe Skin Rear", (90, 0, 0), '',
                        (False, True)),
    'LOOSE_KICK_END_LEFT': ("Loose Toe Skin Left End", (-90, 0, 90), 'XYZ',
                            (True, False)),
    'LOOSE_KICK_END_RIGHT': ("Loose Toe Skin Right End", (-90, 0, 90), 'XY',
                             (False, True)),
}


def _default_rear_setback():
    try:
        from ... import hb_project
        props = hb_project.get_main_scene().hb_frameless
        return max(float(props.default_toe_kick_setback), 0.0)
    except Exception:
        return inch(2.5)


def add_base_assembly_options(root):
    """Give a base the finish options it does not carry yet (one built
    before they existed), all off."""
    for key, kind, value in (
            (FINISH_REAR_KEY, 'CHECKBOX', False),
            (LOOSE_SKIN_KEY, 'CHECKBOX', False),
            (BASE_BY_OTHERS_KEY, 'CHECKBOX', False),
            (BASE_BY_OTHERS_THICKNESS_KEY, 'DISTANCE',
             BASE_BY_OTHERS_THICKNESS)):
        if key not in root:
            root.home_builder.add_property(key, kind, value)
    if REAR_SETBACK_KEY not in root:
        root[REAR_SETBACK_KEY] = _default_rear_setback()


def _skin_part(root, parts, role, wanted):
    """The loose toe skin ``role``, made when it is wanted and taken
    away when it is not."""
    part = parts.get(role)
    if not wanted:
        if part is not None:
            bpy.data.objects.remove(part, do_unlink=True)
            parts.pop(role, None)
        return None
    if part is None:
        name, rotation, mirror, finish = BASE_ASSEMBLY_SKINS[role]
        part = _add_part(root, name, role, rotation=rotation, mirror=mirror,
                         finish=finish).obj
        part[SENT_LOOSE_KEY] = True
        parts[role] = part
        try:
            from .solver_frameless import _paint_like_cabinet
            _paint_like_cabinet(root, part)
        except Exception:
            pass
    return part


def _solve_base_assembly(root, parts, dim_x, dim_y, dim_z):
    """A ladder in plan: the kick face and a back rail run the length,
    the ends stand between them, and cross supports divide it evenly."""
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    # Bases built before the finish sides were put right; the next style
    # update paints them.
    for role, finish in BASE_ASSEMBLY_FINISH.items():
        part = parts.get(role)
        if part is not None:
            _finish_faces(part, finish)
    spacing = float(_prompt(root, 'Support Spacing',
                            BASE_ASSEMBLY_SUPPORT_SPACING))

    # The kick face runs on past an end under a wall scribe filler, to
    # the wall; the end itself stays under the cabinet side.
    ext_l = float(_prompt(root, 'Left Front Extension', 0.0))
    ext_r = float(_prompt(root, 'Right Front Extension', 0.0))
    if BACK_GAP_KEY in root:
        _solve_base_assembly_capped(root, parts, dim_x, dim_y, dim_z, mt,
                                    spacing, ext_l, ext_r)
        return
    # Bases built before the back gap keep the frame they were cut to.
    part = parts.get('BASE_FRONT')
    if part is not None:
        _set_part(part, (-ext_l, -dim_y, 0.0),
                  length=dim_x + ext_l + ext_r, width=dim_z, thickness=mt)

    part = parts.get('BASE_BACK')
    if part is not None:
        _set_part(part, (0.0, 0.0, 0.0),
                  length=dim_x, width=dim_z, thickness=mt)

    for role, x in (('BASE_LEFT_END', 0.0), ('BASE_RIGHT_END', dim_x)):
        part = parts.get(role)
        if part is not None:
            _set_part(part, (x, -mt, 0.0),
                      length=dim_y - mt * 2.0, width=dim_z, thickness=mt)

    part = parts.get('BASE_SUPPORT')
    if part is not None:
        # One part arrayed along the base. The supports divide it into
        # equal bays no wider than the spacing, so a base never ends on
        # a sliver of a bay.
        bays = 1
        if spacing > 0.0:
            bays = max(int(math.ceil((dim_x - mt) / spacing - 1e-6)), 1)
        pitch = (dim_x - mt) / bays
        count = bays - 1
        _set_part(part, (pitch, -mt, 0.0),
                  length=dim_y - mt * 2.0, width=dim_z, thickness=mt,
                  visible=count > 0)
        _set_array(part, count, -pitch)


def _solve_base_assembly_capped(root, parts, dim_x, dim_y, dim_z, mt,
                                spacing, ext_l, ext_r):
    """The frame as the shop cuts it. An end that shows or butts the
    next base is a full-depth piece with the kick face and the back rail
    between the two ends. An end at a wall, where the kick face runs on
    to the wall, is a cross piece between the face and the rail instead.
    The rail stands off the wall by the back gap.

    The cage is the finished size of the base. With a loose skin, or a
    base finish applied by others, the frame is held back from each face
    that shows -- the front, an exposed end, a finished rear -- by that
    finish's thickness, so the finished face stays where it was."""
    if FINISH_REAR_KEY not in root:
        add_base_assembly_options(root)
    gap = max(float(_prompt(root, BACK_GAP_KEY, 0.0)), 0.0)
    cap_l = 0.0 if ext_l > 0.0 else mt
    cap_r = 0.0 if ext_r > 0.0 else mt

    finish_rear = bool(_prompt(root, FINISH_REAR_KEY, False))
    by_others = bool(_prompt(root, BASE_BY_OTHERS_KEY, False))
    skinned = bool(_prompt(root, LOOSE_SKIN_KEY, False))
    if by_others and skinned:
        root[LOOSE_SKIN_KEY] = False
        skinned = False
    skin_t = BASE_ASSEMBLY_SKIN_THICKNESS
    if by_others:
        hold = max(float(_prompt(root, BASE_BY_OTHERS_THICKNESS_KEY, 0.0)),
                   0.0)
    else:
        hold = skin_t if skinned else 0.0

    # An end under a wall scribe filler is at the wall: it never shows.
    shows_l = bool(root.get(LEFT_END_EXPOSED_KEY, False)) and ext_l <= 0.0
    shows_r = bool(root.get(RIGHT_END_EXPOSED_KEY, False)) and ext_r <= 0.0
    x_l = hold if shows_l else 0.0
    x_r = dim_x - (hold if shows_r else 0.0)
    y_front = -dim_y + hold
    if finish_rear:
        # The finished rear stands in from the cabinet backs by the
        # front's setback; nothing is left to scribe, so no back gap.
        rear_face = -min(max(float(_prompt(root, REAR_SETBACK_KEY, 0.0)),
                             0.0), dim_y)
        y_back = rear_face - hold
        y_cap = y_back
    else:
        rear_face = 0.0
        y_back = -gap
        y_cap = 0.0
    inner = max(y_back - y_front - mt * 2.0, 0.0)
    cap_len = max(y_cap - y_front, 0.0)

    part = parts.get('BASE_FRONT')
    if part is not None:
        _set_part(part, (x_l + cap_l - ext_l, y_front, 0.0),
                  length=x_r - x_l + ext_l + ext_r - cap_l - cap_r,
                  width=dim_z, thickness=mt)

    part = parts.get('BASE_BACK')
    if part is not None:
        _set_part(part, (x_l + cap_l, y_back, 0.0),
                  length=x_r - x_l - cap_l - cap_r, width=dim_z,
                  thickness=mt)

    for role, x, cap in (('BASE_LEFT_END', x_l, cap_l),
                         ('BASE_RIGHT_END', x_r, cap_r)):
        part = parts.get(role)
        if part is None:
            continue
        if cap > 0.0:
            _set_part(part, (x, y_cap, 0.0),
                      length=cap_len, width=dim_z, thickness=mt)
        else:
            _set_part(part, (x, y_back - mt, 0.0),
                      length=inner, width=dim_z, thickness=mt)

    part = parts.get('BASE_SUPPORT')
    if part is not None:
        span = x_r - x_l
        bays = 1
        if spacing > 0.0:
            bays = max(int(math.ceil((span - mt) / spacing - 1e-6)), 1)
        pitch = (span - mt) / bays
        count = bays - 1
        _set_part(part, (x_l + pitch, y_back - mt, 0.0),
                  length=inner, width=dim_z, thickness=mt,
                  visible=count > 0)
        _set_array(part, count, -pitch)

    # Loose skins: the front and the rear run the full length, the kick
    # face's run under a wall filler included; an end skin stands
    # between them.
    part = _skin_part(root, parts, 'LOOSE_KICK_FRONT', skinned)
    if part is not None:
        _set_part(part, (-ext_l, -dim_y, 0.0),
                  length=dim_x + ext_l + ext_r, width=dim_z,
                  thickness=skin_t)

    part = _skin_part(root, parts, 'LOOSE_KICK_REAR', skinned and finish_rear)
    if part is not None:
        _set_part(part, (0.0, rear_face, 0.0),
                  length=dim_x, width=dim_z, thickness=skin_t)

    for role, x, shows in (('LOOSE_KICK_END_LEFT', 0.0, shows_l),
                           ('LOOSE_KICK_END_RIGHT', dim_x, shows_r)):
        part = _skin_part(root, parts, role, skinned and shows)
        if part is not None:
            _set_part(part, (x, y_cap, 0.0),
                      length=cap_len, width=dim_z, thickness=skin_t)


class BaseAssembly(Product):
    """The ladder base a run of base and tall cabinets stands on.

    One assembly carries every cabinet of a straight run rather than
    each cabinet bringing its own, so it is built from the run: Add Base
    Assemblies measures the cabinets set to the Ladder Style toe kick
    and stands one of these under each stretch of them.
    Dim X = length along the run, Dim Y = back of the cabinets to the
    kick face, Dim Z = toe kick height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(36)
        self.height = props.default_toe_kick_height
        self.depth = props.base_cabinet_depth - props.default_toe_kick_setback

    def create(self, name="Base Assembly"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'BASE_ASSEMBLY'
        self.obj['IS_BASE_ASSEMBLY'] = True

        self.add_properties_common()
        self.add_property('Support Spacing', 'DISTANCE',
                          BASE_ASSEMBLY_SUPPORT_SPACING)
        self.add_property('Left Front Extension', 'DISTANCE', 0.0)
        self.add_property('Right Front Extension', 'DISTANCE', 0.0)
        self.add_property(BACK_GAP_KEY, 'DISTANCE', BASE_ASSEMBLY_BACK_GAP)
        add_base_assembly_options(self.obj)

        self.add_part('Front', 'BASE_FRONT', rotation=(90, 0, 0), mirror='Z',
                      finish=BASE_ASSEMBLY_FINISH['BASE_FRONT'])
        self.add_part('Back', 'BASE_BACK', rotation=(90, 0, 0),
                      finish=(False, False))
        self.add_part('Left End', 'BASE_LEFT_END', rotation=(-90, 0, 90),
                      mirror='XYZ', finish=BASE_ASSEMBLY_FINISH['BASE_LEFT_END'])
        self.add_part('Right End', 'BASE_RIGHT_END', rotation=(-90, 0, 90),
                      mirror='XY', finish=BASE_ASSEMBLY_FINISH['BASE_RIGHT_END'])

        support = self.add_part('Support', 'BASE_SUPPORT',
                                rotation=(-90, 0, 90), mirror='XYZ',
                                finish=(False, False))
        array_mod = support.obj.modifiers.new(ARRAY_MOD_NAME, 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)

        self.solve()


# ---------------------------------------------------------------------------
# L crown
# ---------------------------------------------------------------------------

L_CROWN_HEIGHT = inch(6.0)
# Front to back, the face board's own thickness included.
L_CROWN_RETURN_DEPTH = inch(4.0)
RETURN_CLEAT_KEY = 'Return Cleat Depth'


def _solve_l_crown(root, parts, dim_x, dim_y, dim_z):
    """An L in section: a face board standing on the cabinet tops, with
    a return cleat lying on the tops behind it to fix through. The face
    is flush with the carcass front or out in the door plane (Dim Y
    always reaches from the wall to the door plane, so the option can
    be switched either way). In the door plane the bottom of the cleat
    shows from below, so it is finished."""
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    ret = float(_prompt(root, RETURN_CLEAT_KEY, L_CROWN_RETURN_DEPTH))
    on_doors = bool(root.get('Flush With Doors', False))
    face_y = -dim_y + (0.0 if on_doors else FRONT_THICKNESS)

    part = parts.get('CROWN_FRONT')
    if part is not None:
        _set_part(part, (0.0, face_y, 0.0),
                  length=dim_x, width=dim_z, thickness=mt)

    part = parts.get('CROWN_CLEAT')
    if part is not None:
        _finish_faces(part, (False, on_doors))
        _set_part(part, (0.0, face_y + mt, 0.0),
                  length=dim_x, width=ret - mt, thickness=mt,
                  visible=ret - mt > 0.0)

    # The cage is what gets clicked, so it is drawn back to the face
    # when that stands behind the door plane.
    try:
        from . import solver_frameless as sf
        sf.set_cage_clamp(root, sf.FRONT_CLEAR_MOD, sf.FRONT_CLEAR_GROUP,
                          'Front', 'Y', face_y, not on_doors)
    except Exception:
        pass


class LCrown(Product):
    """The closure between the top of a run of cabinets and the ceiling.

    A face board with a return cleat behind its bottom edge, standing
    on the cabinet tops. It belongs to the run rather than to a cabinet,
    so it is built from the room the way base assemblies are: Add L
    Crowns measures the runs of upper and tall cabinets and stands
    these over each.
    Dim X = length along the run, Dim Y = wall to the door plane,
    Dim Z = height above the cabinet tops.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = inch(36)
        self.height = L_CROWN_HEIGHT
        self.depth = props.upper_cabinet_depth + FRONT_THICKNESS
        self.return_depth = L_CROWN_RETURN_DEPTH
        self.flush_with_doors = scribe_filler_flush_with_doors()

    def create(self, name="L Crown"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'L_CROWN'
        self.obj['IS_L_CROWN'] = True

        self.add_properties_common()
        self.add_property(RETURN_CLEAT_KEY, 'DISTANCE', self.return_depth)
        self.add_property('Flush With Doors', 'CHECKBOX', self.flush_with_doors)

        # The face shows on its bottom surface; the cleat only from
        # below, and only where it stands out past the carcass.
        self.add_part('Front', 'CROWN_FRONT', rotation=(-90, 0, 0),
                      mirror='Y', finish=(False, True))
        self.add_part('Return Cleat', 'CROWN_CLEAT',
                      finish=(False, self.flush_with_doors))

        self.solve()


_SOLVERS = {
    'BASE_ASSEMBLY': _solve_base_assembly,
    'L_CROWN': _solve_l_crown,
    'FLOATING_SHELF': _solve_floating_shelf,
    'VALANCE': _solve_valance,
    'SUPPORT_FRAME': _solve_support_frame,
    'HALF_WALL': _solve_half_wall,
    'LEG': _solve_leg,
    'UPPER_LEG': _solve_upper_leg,
    'PANEL': _solve_panel,
    'CORNER_FILLER': _solve_corner_filler,
    'VOIDED_CORNER': _solve_voided_corner,
}
