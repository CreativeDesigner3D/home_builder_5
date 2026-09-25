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
        part = part_cls()
        part.create(name)
        part.obj.parent = self.obj
        part.obj[PART_ROLE_KEY] = role
        part.obj.rotation_euler = tuple(math.radians(a) for a in rotation)
        for axis in mirror:
            part.set_input('Mirror ' + axis, True)
        if finish is not None:
            part.obj['Finish Top'] = finish[0]
            part.obj['Finish Bottom'] = finish[1]
        return part

    def solve(self):
        recalculate_product(self.obj)


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
# How far the door fronts stand off the carcass; the filler's face is
# set to line up with them.
FRONT_THICKNESS = inch(0.75)


def _solve_corner_filler(root, parts, dim_x, dim_y, dim_z):
    """An L in plan. The face runs across the front at the door plane
    (Dim Y reaches from the wall to that plane); the return leg stands
    behind it against the cabinet's side, on whichever side the cabinet
    is; a kick piece sits set back below the face on a base or tall."""
    mt = float(_prompt(root, 'Material Thickness', inch(0.75)))
    tkh = float(_prompt(root, 'Toe Kick Height', 0.0))
    tks = float(_prompt(root, 'Toe Kick Setback', 0.0))
    ret = float(_prompt(root, 'Return Depth', CORNER_FILLER_RETURN))
    cab_right = bool(root.get('Cabinet On Right', True))

    part = parts.get('FILLER_FACE')
    if part is not None:
        _set_part(part, (0.0, -dim_y, tkh),
                  length=dim_z - tkh, width=dim_x, thickness=mt)

    part = parts.get('FILLER_KICK')
    if part is not None:
        _set_part(part, (0.0, -dim_y + tks, 0.0),
                  length=tkh, width=dim_x, thickness=mt, visible=tkh > 0.0)

    # The return is inside the filler's own width, so it lies against
    # the cabinet side rather than into the cabinet.
    for role, x, on in (('FILLER_LEFT_RETURN', 0.0, not cab_right),
                        ('FILLER_RIGHT_RETURN', dim_x, cab_right)):
        part = parts.get(role)
        if part is not None:
            # A side panel's width runs toward -Y from where it is set,
            # so it is set at its back edge to run from the face's back
            # toward the wall.
            _set_part(part, (x, -dim_y + mt + ret, tkh),
                      length=dim_z - tkh, width=ret, thickness=mt,
                      visible=on)


class CornerFiller(Product):
    """The filler that closes an inside corner.

    Where a run meets the wall it stands against, a plain cabinet cannot
    open its door into the corner. This stands between the cabinet's
    end and the wall: a 1.5" face in the plane of the doors, with a
    return leg behind it to fix to the cabinet side. Placement adds one
    of its own accord when a cabinet lands in an inside corner.
    Dim X = width, Dim Y = reach from the wall to the door face,
    Dim Z = height.
    """

    def __init__(self):
        super().__init__()
        props = bpy.context.scene.hb_frameless
        self.width = CORNER_FILLER_WIDTH
        self.height = props.base_cabinet_height
        self.depth = props.base_cabinet_depth + FRONT_THICKNESS
        self.toe_kick_height = props.default_toe_kick_height
        self.toe_kick_setback = props.default_toe_kick_setback
        self.cabinet_on_right = True

    def add_properties(self):
        self.add_property('Toe Kick Height', 'DISTANCE', self.toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', self.toe_kick_setback)
        self.add_property('Return Depth', 'DISTANCE', CORNER_FILLER_RETURN)
        self.add_property('Cabinet On Right', 'CHECKBOX', self.cabinet_on_right)

    def create(self, name="Corner Filler"):
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
# Base assembly
# ---------------------------------------------------------------------------

BASE_ASSEMBLY_SUPPORT_SPACING = inch(16)


# (Finish Top, Finish Bottom) for the parts that show: whichever surface
# faces out of the base. The front and the right end face out on their
# bottom surface; the left end, mirrored in Z as well, on its top.
BASE_ASSEMBLY_FINISH = {
    'BASE_FRONT': (False, True),
    'BASE_LEFT_END': (True, False),
    'BASE_RIGHT_END': (False, True),
}


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

    part = parts.get('BASE_FRONT')
    if part is not None:
        _set_part(part, (0.0, -dim_y, 0.0),
                  length=dim_x, width=dim_z, thickness=mt)

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


_SOLVERS = {
    'BASE_ASSEMBLY': _solve_base_assembly,
    'FLOATING_SHELF': _solve_floating_shelf,
    'VALANCE': _solve_valance,
    'SUPPORT_FRAME': _solve_support_frame,
    'HALF_WALL': _solve_half_wall,
    'LEG': _solve_leg,
    'UPPER_LEG': _solve_upper_leg,
    'PANEL': _solve_panel,
    'CORNER_FILLER': _solve_corner_filler,
}
