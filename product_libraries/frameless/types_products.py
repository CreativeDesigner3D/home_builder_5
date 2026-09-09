import bpy
import math
from ...hb_types import GeoNodeCage, GeoNodeCutpart
from ... import units
from ...units import inch
from .types_frameless import CabinetPart, CabinetSideNotched


class Product(GeoNodeCage):
    """Base class for frameless products (non-cabinet products).
    
    Products use IS_FRAMELESS_PRODUCT_CAGE marker so they appear in Cabinets
    selection mode but are distinguishable from actual cabinets.
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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        fl = self.var_prop('Finish Left', 'fl')
        fr = self.var_prop('Finish Right', 'fr')
        led_rb = self.var_prop('Include LED Route Bottom', 'led_rb')
        led_rt = self.var_prop('Include LED Route Top', 'led_rt')
        led_wt = self.var_prop('LED Width Top', 'led_wt')
        led_wb = self.var_prop('LED Width Bottom', 'led_wb')
        led_it = self.var_prop('LED Inset Top', 'led_it')
        led_ib = self.var_prop('LED Inset Bottom', 'led_ib')
        led_depth = self.var_prop('LED Route Depth', 'led_depth')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.driver_location('y', '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_x', [dim_x])
        front.driver_input("Width", 'dim_z', [dim_z])
        front.driver_input("Thickness", 'mt', [mt])
        front.set_input("Mirror Y", True)

        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        top.driver_location('y', '-dim_y+mt', [dim_y, mt])
        top.driver_location('z', 'dim_z', [dim_z, mt])
        top.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        top.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Z", True)

        led_route = top.add_part_modifier('CPM_CUTOUT','LED Route')
        led_route.driver_input('X','-.01',[])
        led_route.driver_input('Y','led_ib',[led_ib])
        led_route.driver_input('End X','dim_x',[dim_x])
        led_route.driver_input('End Y','led_ib+led_wb',[led_ib,led_wb])        
        led_route.driver_input('Route Depth','led_depth',[led_depth])
        led_route.set_input('Flip Z',True)
        led_route.driver_hide('IF(led_rt,False,True)', [led_rt])

        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        bottom.driver_location('y', '-dim_y+mt', [dim_y, mt])
        bottom.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        bottom.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        bottom.driver_input("Thickness", 'mt', [mt])

        led_route = bottom.add_part_modifier('CPM_CUTOUT','LED Route')
        led_route.driver_input('X','-.01',[])
        led_route.driver_input('Y','led_it',[led_it])
        led_route.driver_input('End X','dim_x',[dim_x])
        led_route.driver_input('End Y','led_it+led_wt',[led_it,led_wt])        
        led_route.driver_input('Route Depth','led_depth',[led_depth])
        led_route.set_input('Flip Z',False)
        led_route.driver_hide('IF(led_rb,False,True)', [led_rb])

        l_panel = CabinetPart()
        l_panel.create('Left Panel')
        l_panel.obj.parent = self.obj
        l_panel.obj.rotation_euler.x = math.radians(-90)
        l_panel.obj.rotation_euler.z = math.radians(90)
        l_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        l_panel.driver_input("Width", 'dim_z', [dim_z])
        l_panel.driver_input("Thickness", 'mt', [mt])
        l_panel.driver_hide('IF(fl,False,True)', [fl])
        l_panel.set_input("Mirror X", True)
        l_panel.set_input("Mirror Y", True)
        l_panel.set_input("Mirror Z", True)

        r_panel = CabinetPart()
        r_panel.create('Right Panel')
        r_panel.obj.parent = self.obj
        r_panel.obj.rotation_euler.x = math.radians(-90)
        r_panel.obj.rotation_euler.z = math.radians(90)
        r_panel.driver_location('x', 'dim_x', [dim_x])
        r_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        r_panel.driver_input("Width", 'dim_z', [dim_z])
        r_panel.driver_input("Thickness", 'mt', [mt])
        r_panel.driver_hide('IF(fr,False,True)', [fr])
        r_panel.set_input("Mirror X", True)
        r_panel.set_input("Mirror Y", True)


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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tsa = self.var_prop('Top Scribe Amount', 'tsa')
        fl = self.var_prop('Finish Left', 'fl')
        fr = self.var_prop('Finish Right', 'fr')
        rc = self.var_prop('Remove Cover', 'rc')
        fb = self.var_prop('Flush Bottom', 'fb')

        valance = CabinetPart()
        valance.create('Valance Board')
        valance.obj.parent = self.obj
        valance.obj.rotation_euler.x = math.radians(-90)
        valance.driver_location('y', '-dim_y', [dim_y])
        valance.driver_input("Length", 'dim_x', [dim_x])
        valance.driver_input("Width", 'dim_z', [dim_z])
        valance.driver_input("Thickness", 'mt', [mt])
        valance.set_input("Mirror Y", True)
        valance.obj['Finish Top'] = True
        valance.obj['Finish Bottom'] = True

        cover = CabinetPart()
        cover.create('Cover')
        cover.obj.parent = self.obj
        cover.driver_location('x', 'IF(fl,mt,0)',[mt,fl])
        cover.driver_location('y', '-dim_y+mt', [dim_y, mt])
        cover.driver_location('z', 'IF(fb,0,dim_z-tsa-mt)', [fb, dim_z, mt, tsa])
        cover.driver_input("Length", 'dim_x-IF(fl,mt,0)-IF(fr,mt,0)', [dim_x,fl,fr,mt])
        cover.driver_input("Width", 'dim_y-mt', [dim_y,mt])
        cover.driver_input("Thickness", 'mt', [mt])
        cover.driver_hide('IF(rc,True,False)', [rc])
        cover.obj['Finish Top'] = False
        cover.obj['Finish Bottom'] = True

        l_panel = CabinetPart()
        l_panel.create('Left Panel')
        l_panel.obj.parent = self.obj
        l_panel.obj.rotation_euler.x = math.radians(-90)
        l_panel.obj.rotation_euler.z = math.radians(90)
        l_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        l_panel.driver_input("Width", 'dim_z', [dim_z])
        l_panel.driver_input("Thickness", 'mt', [mt])
        l_panel.driver_hide('IF(fl,False,True)', [fl])
        l_panel.set_input("Mirror X", True)
        l_panel.set_input("Mirror Y", True)
        l_panel.set_input("Mirror Z", True)
        l_panel.obj['Finish Top'] = True
        l_panel.obj['Finish Bottom'] = True

        r_panel = CabinetPart()
        r_panel.create('Right Panel')
        r_panel.obj.parent = self.obj
        r_panel.obj.rotation_euler.x = math.radians(-90)
        r_panel.obj.rotation_euler.z = math.radians(90)
        r_panel.driver_location('x', 'dim_x', [dim_x])
        r_panel.driver_input("Length", 'dim_y-mt', [dim_y,mt])
        r_panel.driver_input("Width", 'dim_z', [dim_z])
        r_panel.driver_input("Thickness", 'mt', [mt])
        r_panel.driver_hide('IF(fr,False,True)', [fr])
        r_panel.set_input("Mirror X", True)
        r_panel.set_input("Mirror Y", True)
        r_panel.obj['Finish Top'] = True
        r_panel.obj['Finish Bottom'] = True


# ---------------------------------------------------------------------------
# Support frame
# ---------------------------------------------------------------------------

# Role tag written on every support frame part. The frame is solved in
# Python, so each pass has to find its own parts again; a tag survives a
# rename or a duplicate, where matching on the object name does not.
SUPPORT_FRAME_PART_KEY = 'SUPPORT_FRAME_PART'

# Frames built before the tag existed are matched on the names their parts
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

# Array modifier carrying the intermediate supports.
SUPPORT_FRAME_ARRAY_MOD = 'Qty'

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
    parts = {}
    for child in frame_obj.children:
        role = child.get(SUPPORT_FRAME_PART_KEY)
        if role is None:
            role = SUPPORT_FRAME_LEGACY_NAMES.get(child.name.split('.')[0])
        if role is not None and role not in parts:
            parts[role] = child
    return parts


def _clear_drivers(obj):
    """Drop every driver on ``obj``.

    Frames built before the solver carry a driver on each part's location,
    each geometry-node size input and its visibility. The solver writes
    those same values directly, and a leftover driver would overwrite the
    written value on the next depsgraph evaluation -- so the old drivers
    have to go before the first solve. Parts built by the solver have no
    animation data at all, which makes this a no-op for them.
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


def _set_part(part_obj, location, length=None, width=None, thickness=None,
              visible=True):
    """Write one part's position, size and visibility.

    Sizes are clamped at zero: a rail whose legs eat more than the frame
    they sit in has no board left, and a negative length would build the
    part inside out rather than not at all.
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


def recalculate_support_frame(obj):
    """Size and place every part of a support frame from its prompts.

    Standard cabinets solve their parts in Python on demand. This frame
    used to hold the same arithmetic in Blender drivers -- one per part,
    per axis, per size input. Drivers evaluate in an order nothing here
    controls, need a forced re-evaluation pass to settle after a prompt
    edit, and only come back from a saved file once every target they
    reference has: which is how a saved frame could reopen with its parts
    collapsed onto the origin or missing altogether. Solving here makes
    the built values plain object data that a file round-trips unchanged.

    Accepts the frame root or any part of it, so property callbacks and
    menu commands can hand it whatever the user had selected.
    """
    frame_obj = support_frame_root(obj)
    if frame_obj is None:
        return
    parts = support_frame_parts(frame_obj)
    if not parts:
        return
    for role, part_obj in parts.items():
        _clear_drivers(part_obj)
        # A frame matched on its part names carries no tags yet; stamp
        # them now so the next solve finds its parts by tag like any
        # frame built here.
        part_obj[SUPPORT_FRAME_PART_KEY] = role

    cage = GeoNodeCage(frame_obj)
    dim_x = cage.get_input('Dim X')
    dim_y = cage.get_input('Dim Y')
    dim_z = cage.get_input('Dim Z')

    get = frame_obj.get
    mt = float(get('Material Thickness', inch(0.75)))
    spacing = float(get('Support Spacing', inch(16)))
    leg_w = float(get('Leg Width', inch(3.5)))
    leg_d = float(get('Leg Depth', inch(3.5)))
    leg_h = float(get('Leg Height', inch(34.5)))

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
        array_mod = part.modifiers.get(SUPPORT_FRAME_ARRAY_MOD)
        if array_mod is not None and array_mod.type == 'ARRAY':
            array_mod.use_relative_offset = False
            array_mod.use_constant_offset = True
            # The support is laid on its side, so the frame's width runs
            # along the part's own Z.
            array_mod.constant_offset_displace = (0.0, 0.0, -spacing)
            array_mod.count = max(count, 1)

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


def upgrade_support_frames(scene=None):
    """Re-solve every support frame in the file.

    Run on load so a frame saved by an older build sheds its drivers and
    comes back at the size it was saved at, rather than waiting for
    something to touch it.
    """
    scenes = [scene] if scene is not None else list(bpy.data.scenes)
    seen = set()
    for scn in scenes:
        for obj in scn.objects:
            if not is_support_frame(obj) or obj.name in seen:
                continue
            seen.add(obj.name)
            try:
                recalculate_support_frame(obj)
            except Exception:
                # One bad frame must not stop a file from opening.
                pass


class SupportFrame(Product):
    """Open rectangular frame (sides, top, bottom).

    Used for supporting countertop overhangs, peninsulas, etc.
    Has configurable legs at each corner with inset or wrapped options.

    Parts are solved by ``recalculate_support_frame`` -- created at rest
    here, then sized and placed from the prompts. Call the solver after
    changing any prompt or dimension on the frame.
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

    def add_part(self, name, role, rotation=(0, 0, 0), mirror=()):
        """One frame part, parented and tagged. Size and position are the
        solver's to write, so only the fixed orientation is set here."""
        part = CabinetPart()
        part.create(name)
        part.obj.parent = self.obj
        part.obj[SUPPORT_FRAME_PART_KEY] = role
        part.obj.rotation_euler = tuple(math.radians(a) for a in rotation)
        for axis in mirror:
            part.set_input('Mirror ' + axis, True)
        return part

    def create(self, name="Support Frame"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'SUPPORT_FRAME'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_support_frame_commands'

        self.add_properties_common()
        self.add_properties()

        # ---- RAILS ----
        self.add_part('Left Panel', 'LEFT_RAIL', rotation=(-90, 0, 90),
                      mirror='XYZ')
        self.add_part('Right Panel', 'RIGHT_RAIL', rotation=(-90, 0, 90),
                      mirror='XY')
        self.add_part('Front Panel', 'FRONT_RAIL', rotation=(90, 0, 0),
                      mirror='Z')
        self.add_part('Back Panel', 'BACK_RAIL', rotation=(90, 0, 0))

        # ---- INTERMEDIATE SUPPORTS ----
        support = self.add_part('Support', 'SUPPORT', rotation=(-90, 0, 90),
                                mirror='XYZ')
        support.obj['Finish Top'] = False
        support.obj['Finish Bottom'] = False
        array_mod = support.obj.modifiers.new(SUPPORT_FRAME_ARRAY_MOD, 'ARRAY')
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
            leg = self.add_part(part_name, role, rotation=rotation,
                                mirror='X')
            leg.obj['Finish Top'] = True
            leg.obj['Finish Bottom'] = True

        recalculate_support_frame(self.obj)


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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        st = self.var_prop('Stud Thickness', 'st')
        skt = self.var_prop('Skin Thickness', 'skt')
        ssp = self.var_prop('Stud Spacing', 'ssp')
        esfe = self.var_prop('End Stud From Edge', 'esfe')
        lec = self.var_prop('Left End Cap', 'lec')
        rec = self.var_prop('Right End Cap', 'rec')
        fes = self.var_prop('Finished End Setback', 'fes')
        lfr = self.var_prop('Left Finished Revel', 'lfr')
        rfr = self.var_prop('Right Finished Revel', 'rfr')
        ff = self.var_prop('Finish Front', 'ff')
        fba = self.var_prop('Finish Back', 'fba')

        left_end = CabinetPart()
        left_end.create('Left End')
        left_end.obj.parent = self.obj
        left_end.obj.rotation_euler.x = math.radians(90)
        left_end.obj.rotation_euler.y = math.radians(-90)
        left_end.obj.rotation_euler.z = math.radians(-90)
        left_end.driver_input("Length", 'dim_z', [dim_z])
        left_end.driver_input("Width", 'dim_y', [dim_y])
        left_end.driver_input("Thickness", 'mt', [mt])
        left_end.set_input("Mirror Y", True)
        left_end.set_input("Mirror Z", True)
        left_end.obj['Finish Top'] = True
        left_end.obj['Finish Bottom'] = True

        right_end = CabinetPart()
        right_end.create('Right End')
        right_end.obj.parent = self.obj
        right_end.obj.rotation_euler.x = math.radians(90)
        right_end.obj.rotation_euler.y = math.radians(-90)
        right_end.obj.rotation_euler.z = math.radians(-90)
        right_end.driver_location('x', 'dim_x', [dim_x])
        right_end.driver_input("Length", 'dim_z', [dim_z])
        right_end.driver_input("Width", 'dim_y', [dim_y])
        right_end.driver_input("Thickness", 'mt', [mt])
        right_end.set_input("Mirror Y", True)
        right_end.obj['Finish Top'] = True
        right_end.obj['Finish Bottom'] = True

        top = CabinetPart()
        top.create('Right End')
        top.obj.parent = self.obj
        top.driver_location('x', 'mt', [mt])
        top.driver_location('y', '-st', [st])
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        top.driver_input("Width", 'dim_y-st*2', [dim_y,st])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Y", True)
        top.set_input("Mirror Z", True)
        top.obj['Finish Top'] = False
        top.obj['Finish Bottom'] = False

        bottom = CabinetPart()
        bottom.create('Right End')
        bottom.obj.parent = self.obj
        bottom.driver_location('x', 'mt', [mt])
        bottom.driver_location('y', '-st', [st])
        bottom.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        bottom.driver_input("Width", 'dim_y-st*2', [dim_y,st])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)
        bottom.obj['Finish Top'] = False
        bottom.obj['Finish Bottom'] = False

        front_skin = CabinetPart()
        front_skin.create('Front Skin')
        front_skin.obj.parent = self.obj
        front_skin.obj.rotation_euler.x = math.radians(90)
        front_skin.driver_location('x', 'mt', [mt])
        front_skin.driver_location('y', '-dim_y', [dim_y])
        front_skin.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        front_skin.driver_input("Width", 'dim_z', [dim_z])
        front_skin.driver_input("Thickness", 'st', [st])
        front_skin.set_input("Mirror Z", True)
        front_skin.obj['Finish Top'] = True
        front_skin.obj['Finish Bottom'] = True

        back_skin = CabinetPart()
        back_skin.create('Back Skin')
        back_skin.obj.parent = self.obj
        back_skin.obj.rotation_euler.x = math.radians(90)
        back_skin.driver_location('x', 'mt', [mt])
        back_skin.driver_input("Length", 'dim_x-mt-mt', [dim_x,mt])
        back_skin.driver_input("Width", 'dim_z', [dim_z])
        back_skin.driver_input("Thickness", 'st', [st])
        back_skin.obj['Finish Top'] = True
        back_skin.obj['Finish Bottom'] = True

        # Stud with array modifier
        stud = CabinetPart()
        stud.create('Stud')
        stud.obj.parent = self.obj
        stud.obj.rotation_euler.x = math.radians(90)
        stud.obj.rotation_euler.y = math.radians(-90)
        stud.obj.rotation_euler.z = math.radians(-90)
        stud.driver_location('x', 'mt+esfe', [mt, esfe])
        stud.driver_location('y', '-st', [st])
        stud.driver_location('z', 'mt', [mt])
        stud.driver_input("Length", 'dim_z-mt*2', [dim_z, mt])
        stud.driver_input("Width", 'dim_y-st*2', [dim_y, st])
        stud.driver_input("Thickness", 'st', [st])
        stud.set_input("Mirror Y", True)
        stud.set_input("Mirror Z", True)
        stud.obj['Finish Top'] = False
        stud.obj['Finish Bottom'] = False
        array_mod = stud.obj.modifiers.new('Qty', 'ARRAY')
        array_mod.count = 1
        array_mod.use_relative_offset = False
        array_mod.use_constant_offset = True
        array_mod.constant_offset_displace = (0, 0, 0)
        stud.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].count', -1,
            'IF(ssp>0,floor((dim_x-mt*2-esfe*2)/ssp)+1,1)',
            [ssp, dim_x, mt, esfe])
        stud.obj.home_builder.add_driver(
            'modifiers["' + array_mod.name + '"].constant_offset_displace', 2,
            '-ssp', [ssp])


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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        olpd = self.var_prop('Override Left Panel Depth', 'olpd')
        orpd = self.var_prop('Override Right Panel Depth', 'orpd')
        oif = self.var_prop('Only Include Filler', 'oif')
        ft = self.var_prop('Finish Type', 'ft')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.obj.rotation_euler.y = math.radians(-90)
        front.driver_location("z", 'tkh', [tkh])
        front.driver_location("y", '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_z-tkh', [dim_z,tkh])
        front.driver_input("Width", 'dim_x', [dim_x])
        front.driver_input("Thickness", 'mt', [mt])

        tk_front = CabinetPart()
        tk_front.create('Toe Kick Front')
        tk_front.obj.parent = self.obj
        tk_front.obj.rotation_euler.x = math.radians(-90)
        tk_front.obj.rotation_euler.y = math.radians(-90)
        tk_front.driver_location("y", '-dim_y+tks', [dim_y,tks])
        tk_front.driver_input("Length", 'tkh', [tkh])
        tk_front.driver_input("Width", 'dim_x', [dim_x])
        tk_front.driver_input("Thickness", 'mt', [mt])
        tk_front.driver_hide('IF(tkh==0,True,False)', [tkh])

        left_panel = CabinetSideNotched()
        left_panel.create('Left Panel',tkh,tks,mt)
        left_panel.obj.parent = self.obj
        left_panel.obj.rotation_euler.y = math.radians(-90)
        left_panel.driver_location("y", 'IF(olpd==0,0,-dim_y+mt+olpd)', [olpd,dim_y,mt])
        left_panel.driver_input("Length", 'dim_z', [dim_z])
        left_panel.driver_input("Width", 'IF(olpd==0,dim_y-mt,olpd)', [olpd,dim_y,mt])
        left_panel.driver_input("Thickness", 'mt', [mt])
        left_panel.set_input('Mirror Z', True)
        left_panel.set_input('Mirror Y', True)
        left_panel.driver_hide('IF(oif,True,IF(OR(ft==0,ft==2),False,True))', [oif,ft])

        right_panel = CabinetSideNotched()
        right_panel.create('Right Panel',tkh,tks,mt)
        right_panel.obj.parent = self.obj
        right_panel.obj.rotation_euler.y = math.radians(-90)
        right_panel.driver_location("x", 'dim_x', [dim_x])
        right_panel.driver_location("y", 'IF(orpd==0,0,-dim_y+mt+orpd)', [orpd,dim_y,mt])
        right_panel.driver_input("Length", 'dim_z', [dim_z])
        right_panel.driver_input("Width", 'IF(orpd==0,dim_y-mt,orpd)', [orpd,dim_y,mt])
        right_panel.driver_input("Thickness", 'mt', [mt])
        right_panel.driver_hide('IF(oif,True,IF(OR(ft==1,ft==2),False,True))', [oif,ft])
        right_panel.set_input('Mirror Y', True)


class TallLeg(Product):
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

    def add_properties(self):
        props = bpy.context.scene.hb_frameless
        self.add_property('Toe Kick Height', 'DISTANCE', props.default_toe_kick_height)
        self.add_property('Toe Kick Setback', 'DISTANCE', props.default_toe_kick_setback)
        self.add_property('Override Left Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Override Right Panel Depth', 'DISTANCE', 0.0)
        self.add_property('Only Include Filler', 'CHECKBOX', False)
        self.add_property('Finish Type', 'COMBOBOX', 0, combobox_items=["Left", "Right", "Both"])

    def create(self, name="Tall Leg"):
        self.create_product(name)
        self.obj['PART_TYPE'] = 'LEG'
        self.obj['MENU_ID'] = 'HOME_BUILDER_MT_leg_commands'

        self.add_properties_common()
        self.add_properties()

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        tkh = self.var_prop('Toe Kick Height', 'tkh')
        tks = self.var_prop('Toe Kick Setback', 'tks')
        olpd = self.var_prop('Override Left Panel Depth', 'olpd')
        orpd = self.var_prop('Override Right Panel Depth', 'orpd')
        oif = self.var_prop('Only Include Filler', 'oif')
        ft = self.var_prop('Finish Type', 'ft')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.obj.rotation_euler.y = math.radians(-90)
        front.driver_location("z", 'tkh', [tkh])
        front.driver_location("y", '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_z-tkh', [dim_z, tkh])
        front.driver_input("Width", 'dim_x', [dim_x])
        front.driver_input("Thickness", 'mt', [mt])

        tk_front = CabinetPart()
        tk_front.create('Toe Kick Front')
        tk_front.obj.parent = self.obj
        tk_front.obj.rotation_euler.x = math.radians(-90)
        tk_front.obj.rotation_euler.y = math.radians(-90)
        tk_front.driver_location("y", '-dim_y+tks', [dim_y, tks])
        tk_front.driver_input("Length", 'tkh', [tkh])
        tk_front.driver_input("Width", 'dim_x', [dim_x])
        tk_front.driver_input("Thickness", 'mt', [mt])
        tk_front.driver_hide('IF(tkh==0,True,False)', [tkh])

        left_panel = CabinetSideNotched()
        left_panel.create('Left Panel', tkh, tks, mt)
        left_panel.obj.parent = self.obj
        left_panel.obj.rotation_euler.y = math.radians(-90)
        left_panel.driver_location("y", 'IF(olpd==0,0,-dim_y+mt+olpd)', [olpd, dim_y, mt])
        left_panel.driver_input("Length", 'dim_z', [dim_z])
        left_panel.driver_input("Width", 'IF(olpd==0,dim_y-mt,olpd)', [olpd, dim_y, mt])
        left_panel.driver_input("Thickness", 'mt', [mt])
        left_panel.set_input('Mirror Z', True)
        left_panel.set_input('Mirror Y', True)
        left_panel.driver_hide('IF(oif,True,IF(OR(ft==0,ft==2),False,True))', [oif, ft])

        right_panel = CabinetSideNotched()
        right_panel.create('Right Panel', tkh, tks, mt)
        right_panel.obj.parent = self.obj
        right_panel.obj.rotation_euler.y = math.radians(-90)
        right_panel.driver_location("x", 'dim_x', [dim_x])
        right_panel.driver_location("y", 'IF(orpd==0,0,-dim_y+mt+orpd)', [orpd, dim_y, mt])
        right_panel.driver_input("Length", 'dim_z', [dim_z])
        right_panel.driver_input("Width", 'IF(orpd==0,dim_y-mt,orpd)', [orpd, dim_y, mt])
        right_panel.driver_input("Thickness", 'mt', [mt])
        right_panel.driver_hide('IF(oif,True,IF(OR(ft==1,ft==2),False,True))', [oif, ft])
        right_panel.set_input('Mirror Y', True)


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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')
        mt = self.var_prop('Material Thickness', 'mt')
        olpd = self.var_prop('Override Left Panel Depth', 'olpd')
        orpd = self.var_prop('Override Right Panel Depth', 'orpd')
        oif = self.var_prop('Only Include Filler', 'oif')
        ft = self.var_prop('Finish Type', 'ft')

        front = CabinetPart()
        front.create('Front')
        front.obj.parent = self.obj
        front.obj.rotation_euler.x = math.radians(-90)
        front.obj.rotation_euler.y = math.radians(-90)
        front.driver_location("y", '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_z', [dim_z])
        front.driver_input("Width", 'dim_x', [dim_x])
        front.driver_input("Thickness", 'mt', [mt])

        top = CabinetPart()
        top.create('Top')
        top.obj.parent = self.obj
        top.driver_location('z', 'dim_z', [dim_z])
        top.driver_input("Length", 'dim_x', [dim_x])
        top.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        top.driver_input("Thickness", 'mt', [mt])
        top.set_input("Mirror Z", True)
        top.set_input("Mirror Y", True)

        bottom = CabinetPart()
        bottom.create('Bottom')
        bottom.obj.parent = self.obj
        bottom.driver_input("Length", 'dim_x', [dim_x])
        bottom.driver_input("Width", 'dim_y-mt', [dim_y, mt])
        bottom.driver_input("Thickness", 'mt', [mt])
        bottom.set_input("Mirror Y", True)

        left_panel = CabinetPart()
        left_panel.create('Left Panel')
        left_panel.obj.parent = self.obj
        left_panel.obj.rotation_euler.y = math.radians(-90)
        left_panel.driver_location("y", 'IF(olpd==0,0,-dim_y+mt+olpd)', [olpd, dim_y, mt])
        left_panel.driver_location("z", 'mt', [mt])
        left_panel.driver_input("Length", 'dim_z-mt*2', [dim_z, mt])
        left_panel.driver_input("Width", 'IF(olpd==0,dim_y-mt,olpd)', [olpd, dim_y, mt])
        left_panel.driver_input("Thickness", 'mt', [mt])
        left_panel.set_input('Mirror Z', True)
        left_panel.set_input('Mirror Y', True)
        left_panel.driver_hide('IF(oif,True,IF(OR(ft==0,ft==2),False,True))', [oif, ft])

        right_panel = CabinetPart()
        right_panel.create('Right Panel')
        right_panel.obj.parent = self.obj
        right_panel.obj.rotation_euler.y = math.radians(-90)
        right_panel.driver_location("x", 'dim_x', [dim_x])
        right_panel.driver_location("y", 'IF(orpd==0,0,-dim_y+mt+orpd)', [orpd, dim_y, mt])
        right_panel.driver_location("z", 'mt', [mt])
        right_panel.driver_input("Length", 'dim_z-mt*2', [dim_z, mt])
        right_panel.driver_input("Width", 'IF(orpd==0,dim_y-mt,orpd)', [orpd, dim_y, mt])
        right_panel.driver_input("Thickness", 'mt', [mt])
        right_panel.driver_hide('IF(oif,True,IF(OR(ft==1,ft==2),False,True))', [oif, ft])
        right_panel.set_input('Mirror Y', True)


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

        dim_x = self.var_input('Dim X', 'dim_x')
        dim_y = self.var_input('Dim Y', 'dim_y')
        dim_z = self.var_input('Dim Z', 'dim_z')

        panel = CabinetPart()
        panel.create('Panel Board')
        panel.obj.parent = self.obj
        panel.obj.rotation_euler.y = math.radians(-90)
        panel.driver_input("Length", 'dim_z', [dim_z])
        panel.driver_input("Width", 'dim_y', [dim_y])
        panel.driver_input("Thickness", 'dim_x', [dim_x])
        panel.set_input("Mirror Y", True)
        panel.set_input("Mirror Z", True)
        panel.obj['Finish Top'] = True
        panel.obj['Finish Bottom'] = True
