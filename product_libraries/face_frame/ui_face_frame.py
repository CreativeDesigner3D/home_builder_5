"""Face frame sidebar UI + shared draw helpers + selection awareness.

The sidebar is a parent panel with collapsible sub-panels:
    - Dimensions                (open by default)
    - Construction              (collapsed by default)
    - Face Frame Defaults       (collapsed by default)
    - Selection                 (dynamic - shows the active bay / stile / rail)
    - All Bays                  (collapsed by default)

Three popup operators provide focused editors that share these helpers:
    - hb_face_frame.cabinet_prompts    -> cabinet-wide only
    - hb_face_frame.bay_prompts        -> single bay
    - hb_face_frame.mid_stile_prompts  -> single mid stile

Adding a property to a section adds it everywhere because both the
sidebar sub-panels and the popups call the same draw_* helper.
"""
import bpy

from . import types_face_frame
from . import shelf_nosing
from ... import units


# ---------------------------------------------------------------------------
# Selection helper
# ---------------------------------------------------------------------------
def find_active_selection(context):
    """Identify what the user is editing based on the active object.

    Returns a tuple keyed by kind:
        ('none',)
        ('cabinet',   root)
        ('bay',       bay_obj, root)
        ('opening',   opening_obj, bay_obj, root)
        ('interior_region', leaf_obj, opening_obj, root)
        ('mid_stile', stile_obj, msi, root)
        ('end_stile', stile_obj, role, root)
        ('rail',      rail_obj, role, root)
        ('other',     obj, root)
    """
    obj = context.active_object
    if obj is None:
        return ('none',)
    root = types_face_frame.find_cabinet_root(obj)
    if root is None:
        return ('none',)
    if obj == root:
        return ('cabinet', root)
    if obj.get(types_face_frame.TAG_BAY_CAGE):
        return ('bay', obj, root)
    if obj.get(types_face_frame.TAG_OPENING_CAGE):
        bay_obj = obj.parent
        return ('opening', obj, bay_obj, root)
    if obj.get(types_face_frame.TAG_INTERIOR_REGION):
        # Walk up through (zero or more) split nodes to find the
        # owning opening so panels that need it (e.g. for context
        # labels) can resolve it without re-walking.
        opening_obj = obj.parent
        while opening_obj is not None and not opening_obj.get(
                types_face_frame.TAG_OPENING_CAGE):
            opening_obj = opening_obj.parent
        return ('interior_region', obj, opening_obj, root)
    role = obj.get('hb_part_role')
    if role == types_face_frame.PART_ROLE_MID_STILE:
        msi = obj.get('hb_mid_stile_index', 0)
        return ('mid_stile', obj, msi, root)
    if role in (types_face_frame.PART_ROLE_TOP_RAIL,
                types_face_frame.PART_ROLE_BOTTOM_RAIL):
        return ('rail', obj, role, root)
    if role in (types_face_frame.PART_ROLE_LEFT_STILE,
                types_face_frame.PART_ROLE_RIGHT_STILE):
        return ('end_stile', obj, role, root)
    return ('other', obj, root)


# ---------------------------------------------------------------------------
# Focused draw helpers - reused by sidebar sub-panels AND popup operators
# ---------------------------------------------------------------------------
def draw_identity(layout, root):
    """Editable cabinet name + read-only type. Compact."""
    cab_props = root.face_frame_cabinet
    row = layout.row()
    row.prop(root, 'name', text='', icon='MESH_CUBE')
    row.label(text=cab_props.cabinet_type)


def draw_dimensions(layout, root):
    cab_props = root.face_frame_cabinet
    bay_count = sum(
        1 for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)
    )
    col = layout.column(align=True)
    col.prop(cab_props, 'width', text="Width")
    col.prop(cab_props, 'depth', text="Depth")
    col.prop(cab_props, 'height', text="Height")
    # Corner cabinets: stub-side lengths perpendicular to each wall.
    # Drive the L-shape of the carcass and the inset of each face frame
    # from the wall corner. width / depth here is the full bounding
    # square; left_depth / right_depth carve the L back out of it.
    if cab_props.corner_type != 'NONE':
        col.separator()
        col.prop(cab_props, 'left_depth', text="Left Depth")
        col.prop(cab_props, 'right_depth', text="Right Depth")
        col.prop(cab_props, 'clip_back_amount', text="Clip Back")
        col.separator()
        if cab_props.corner_type == 'PIE_CUT':
            col.label(text="Pie Cut Options")
            col.prop(cab_props, 'exterior_option',  text="Door Swing")
            # Stacked-door config is upper pie cut only; base pie cut is
            # full-height door and has no config choice to make.
            is_upper = root.get('CABINET_TYPE') == 'UPPER'
            if is_upper:
                col.prop(cab_props, 'exterior_config', text="Config")
            col.prop(cab_props, 'interior_option',  text="Interior")
            col.prop(cab_props, 'corner_finish_interior', text="Finish Interior")
            col.prop(cab_props, 'tray_compartment', text="Tray Compartment")
            if cab_props.tray_compartment != 'NONE':
                col.prop(cab_props, 'tray_compartment_width', text="Tray Comp. Width")
                col.prop(cab_props, 'tray_compartment_qty', text="Divider Qty")
                col.prop(cab_props, 'tray_compartment_divider_thickness', text="Divider Thickness")
                col.prop(cab_props, 'tray_compartment_setback', text="Divider Setback")
            draw_corner_sections(layout, cab_props)
        elif cab_props.corner_type == 'DIAGONAL':
            col.label(text="Exterior Configuration")
            col.prop(cab_props, 'exterior_config', text="Config")
            col.prop(cab_props, 'diag_door_swing', text="Door Swing")
            col.prop(cab_props, 'interior_option', text="Interior")
            col.prop(cab_props, 'corner_finish_interior', text="Finish Interior")
            col.prop(cab_props, 'corner_remove_bottom', text="Remove Bottom")
            draw_corner_sections(layout, cab_props)
        elif cab_props.corner_type == 'PIE_CUT_DRAWER':
            col.label(text="Pie Cut Drawer Options")
            col.prop(cab_props, 'pie_drawer_qty', text="Drawer Qty")
            # Per-section opening heights (top to bottom). Section rows label
            # by content ("Doors") until a dedicated drawer-front content type
            # lands; the height + lock controls are what matter here.
            draw_corner_sections(layout, cab_props)
    # Angled standard cabinet: per-side depth unlocks, single-bay only.
    # When either is on, the face frame becomes the hypotenuse spanning
    # the two front edges; the back stays at cab_props.depth between
    # the sides. Hidden entirely on multi-bay carcasses.
    elif bay_count == 1:
        col.separator()
        left_row = col.row(align=True)
        field = left_row.row(align=True)
        field.enabled = cab_props.unlock_left_depth
        field.prop(cab_props, 'left_depth', text="Left Depth")
        lock_icon = 'UNLOCKED' if cab_props.unlock_left_depth else 'LOCKED'
        left_row.prop(cab_props, 'unlock_left_depth', text="", icon=lock_icon)

        right_row = col.row(align=True)
        field = right_row.row(align=True)
        field.enabled = cab_props.unlock_right_depth
        field.prop(cab_props, 'right_depth', text="Right Depth")
        lock_icon = 'UNLOCKED' if cab_props.unlock_right_depth else 'LOCKED'
        right_row.prop(cab_props, 'unlock_right_depth', text="", icon=lock_icon)


_CORNER_SECTION_LABELS = {
    'DOORS':       "Doors",
    'FALSE_FRONT': "False Front",
    'OPEN':        "Open",
}


def draw_corner_sections(layout, cab_props):
    """Per-section height controls for a diagonal corner cabinet.

    One row per section, top to bottom. Each row shows the section's
    content kind and an editable height with a lock toggle: locked
    sections hold their height, unlocked sections share the leftover
    space equally (see _solve_section_heights). Open sections also get
    a shelf-count field.
    """
    sections = cab_props.corner_sections
    # Nothing to adjust for a lone BASE door section (height is the full
    # span, no shelves) - skip the box entirely. A lone OPEN section
    # still shows for its shelf count, and a lone UPPER doors section
    # (e.g. the bi-fold upper) shows for its shelf-qty override.
    has_open = any(s.content == 'OPEN' for s in sections)
    has_upper_doors = (cab_props.cabinet_type == 'UPPER'
                       and any(s.content == 'DOORS' for s in sections))
    if len(sections) < 2 and not has_open and not has_upper_doors:
        return
    box = layout.box()
    box.label(text="Sections (top to bottom)")
    for idx, section in enumerate(sections):
        kind = _CORNER_SECTION_LABELS.get(section.content, section.content)
        col = box.column(align=True)
        col.label(text="%d. %s" % (idx + 1, kind))
        row = col.row(align=True)
        field = row.row(align=True)
        # A single unlocked section has no leftover to share, so its
        # height is always the full span - lock toggle would be a no-op.
        field.enabled = section.unlock_height
        field.prop(section, 'height', text="Height")
        lock_icon = 'UNLOCKED' if section.unlock_height else 'LOCKED'
        row.prop(section, 'unlock_height', text="", icon=lock_icon)
        if section.content == 'OPEN':
            col.prop(section, 'shelf_qty', text="Shelves")
        elif (section.content == 'DOORS'
              and cab_props.cabinet_type == 'UPPER'):
            # Upper door sections auto-count shelves by height; the
            # lock mirrors the standard interior-item qty pattern
            # (locked = auto, unlocked = manual override).
            qty_row = col.row(align=True)
            field = qty_row.row(align=True)
            field.enabled = section.unlock_shelf_qty
            field.prop(section, 'shelf_qty', text="Shelves")
            lock_icon = ('UNLOCKED' if section.unlock_shelf_qty
                         else 'LOCKED')
            qty_row.prop(section, 'unlock_shelf_qty', text="",
                         icon=lock_icon)


def draw_construction(layout, cab_props):
    """Toe kick (if applicable). Panel roots have no carcass - the
    section collapses to just the finished-ends block (which itself
    is irrelevant for panels but harmless to leave visible)."""
    if cab_props.cabinet_type == 'PANEL':
        layout.label(text="No carcass - face frame only", icon='INFO')
        return

    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        box = layout.box()
        box.prop(cab_props, 'show_toe_kick', text="Toe Kick",
                 icon='TRIA_DOWN' if cab_props.show_toe_kick else 'TRIA_RIGHT',
                 emboss=False)
        if cab_props.show_toe_kick:
            col = box.column(align=True)
            col.prop(cab_props, 'toe_kick_type', text="Type")
            col.prop(cab_props, 'toe_kick_height', text="Height")
            col.prop(cab_props, 'toe_kick_setback', text="Setback")
            col.prop(cab_props, 'inset_toe_kick_left', text="Left Inset")
            col.prop(cab_props, 'inset_toe_kick_right', text="Right Inset")
            # Back insets pull each arm's rear (wall-side) rail off its wall;
            # corner cabinets only (no wall-side rail on a straight run).
            if cab_props.corner_type != 'NONE':
                col.prop(cab_props, 'inset_toe_kick_back_left', text="Back Left Inset")
                col.prop(cab_props, 'inset_toe_kick_back_right', text="Back Right Inset")
            col.prop(cab_props, 'include_finish_toe_kick', text="Finish Toe Kick")

    box = layout.box()
    box.prop(cab_props, 'show_finished_ends', text="Finished Ends and Backs",
             icon='TRIA_DOWN' if cab_props.show_finished_ends else 'TRIA_RIGHT',
             emboss=False)
    if cab_props.show_finished_ends:
        draw_finished_ends(box, cab_props)

    # Decorative bottom-rail profile (valance) - base / upper. The chosen
    # '* Cutter' curve is cut into the bottom rail with fixed end details and
    # a stretched middle (see types_face_frame._apply_bottom_rail_profile).
    if cab_props.cabinet_type in ('BASE', 'UPPER'):
        rpbox = layout.box()
        rpbox.label(text="Bottom Rail Profile", icon='MOD_BEVEL')
        rpbox.prop(cab_props, 'bottom_rail_profile', text="Profile")

    abx = layout.box()
    abx.prop(cab_props, 'show_angled_back_extension',
             text="Angled Back Extension",
             icon='TRIA_DOWN' if cab_props.show_angled_back_extension
             else 'TRIA_RIGHT', emboss=False)
    if cab_props.show_angled_back_extension:
        col = abx.column(align=True)
        col.prop(cab_props, 'extend_back_left', text="Extend Back Left X")
        # Convert this end's extension into an attached wing instead of
        # splaying the carcass: the carcass stays square and a flat panel
        # is added along the same angled line. Only meaningful when the
        # extend above is non-zero.
        row = col.row()
        row.enabled = cab_props.extend_back_left != 0.0
        row.prop(cab_props, 'wing_attached_left', text="Attach as Wing")
        col.separator()
        col.prop(cab_props, 'extend_back_right', text="Extend Back Right X")
        row = col.row()
        row.enabled = cab_props.extend_back_right != 0.0
        row.prop(cab_props, 'wing_attached_right', text="Attach as Wing")

    # Uppers only: hutch / over-stool / corner-cover extensions, grouped
    # under one collapsible category (rarely used).
    if cab_props.cabinet_type == 'UPPER':
        uex = layout.box()
        uex.prop(cab_props, 'show_upper_extensions', text="Upper Extensions",
                 icon='TRIA_DOWN' if cab_props.show_upper_extensions
                 else 'TRIA_RIGHT', emboss=False)
        if cab_props.show_upper_extensions:
            # Drop the left / right sides + end stiles below the box
            # (hutch look). Left and right are independent.
            box = uex.box()
            box.label(text="Extend Ends Down")
            col = box.column(align=True)
            col.prop(cab_props, 'extend_left_end_down', text="Left")
            if cab_props.extend_left_end_down:
                col.prop(cab_props, 'extend_left_end_down_amount', text="Left Drop")
            col.prop(cab_props, 'extend_right_end_down', text="Right")
            if cab_props.extend_right_end_down:
                col.prop(cab_props, 'extend_right_end_down_amount', text="Right Drop")
            # Finished back closes the recess once a side is dropped.
            if cab_props.extend_left_end_down or cab_props.extend_right_end_down:
                box.prop(cab_props, 'hutch_finished_back',
                         text="Finished Back in Recess")

            # Drop BOTH sides below the box as furniture legs (over-stool
            # look) - decorative front profile + a shelf / towel bar.
            box = uex.box()
            box.label(text="Extend Sides Down")
            col = box.column(align=True)
            col.prop(cab_props, 'extend_sides_down', text="Extend Sides Down")
            if cab_props.extend_sides_down:
                col.prop(cab_props, 'extend_sides_down_amount', text="Sides Drop")
                col.prop(cab_props, 'side_front_profile', text="Front Profile")
                col.prop(cab_props, 'overstool_accessory', text="Accessory")

            # Bottom panel overhangs a side to cover the void where two
            # uppers meet in a corner (bottom only - faces stay square).
            box = uex.box()
            box.label(text="Extend Bottom", icon='MOD_BEVEL')
            col = box.column(align=True)
            col.prop(cab_props, 'extend_bottom_left', text="Extend Bottom Left X")
            col.prop(cab_props, 'extend_bottom_right', text="Extend Bottom Right X")

    # Furniture wood top sits at the bottom - a finishing option layered
    # on after the carcass, ends, and any extensions are set.
    box = layout.box()
    box.prop(cab_props, 'show_wood_top', text="Furniture Wood Top",
             icon='TRIA_DOWN' if cab_props.show_wood_top else 'TRIA_RIGHT',
             emboss=False)
    if cab_props.show_wood_top:
        box.prop(cab_props, 'furniture_top', text="Enable")
        if cab_props.furniture_top:
            col = box.column(align=True)
            col.prop(cab_props, 'furniture_top_thickness', text="Thickness")
            col.label(text="Overhang")
            col.prop(cab_props, 'furniture_top_overhang_front', text="Front")
            col.prop(cab_props, 'furniture_top_overhang_back', text="Back")
            col.prop(cab_props, 'furniture_top_overhang_left', text="Left")
            col.prop(cab_props, 'furniture_top_overhang_right', text="Right")
            # Plan shape + its per-shape inputs (bow altitude / corner
            # radii). Waterfall has no extra inputs - the drop panels
            # follow the top's ends, thickness, and plan depth.
            col = box.column(align=True)
            col.prop(cab_props, 'furniture_top_shape', text="Shape")
            if cab_props.furniture_top_shape == 'BOW_BACK':
                col.prop(cab_props, 'furniture_top_bow_altitude',
                         text="Bow Altitude")
            elif cab_props.furniture_top_shape == 'RADIUS':
                col.label(text="Corner Radius")
                col.prop(cab_props, 'furniture_top_radius_front_left',
                         text="Front Left")
                col.prop(cab_props, 'furniture_top_radius_front_right',
                         text="Front Right")
                col.prop(cab_props, 'furniture_top_radius_back_left',
                         text="Back Left")
                col.prop(cab_props, 'furniture_top_radius_back_right',
                         text="Back Right")


def draw_refrigerator_options(layout, root):
    """Refrigerator opening height + per-side raise. Refrigerator cabinets only.

    Opening Height drives the bottom appliance opening node and keeps the
    carcass back in sync. Raise Left / Right lift that side's carcass side
    panel AND end stile to the top of the opening, so the side spans only the
    door zone above the fridge (handy for sliding a wider unit past one end)."""
    if root.get('CLASS_NAME') != 'RefrigeratorCabinet':
        return
    cab = root.face_frame_cabinet
    box = layout.box()
    box.label(text="Refrigerator", icon='MOD_BUILD')
    box.prop(cab, 'refrigerator_opening_height', text="Opening Height")
    row = box.row(align=True)
    row.label(text="Raise Side Up:")
    row.prop(cab, 'raise_left_to_refrigerator_height', text="Left", toggle=True)
    row.prop(cab, 'raise_right_to_refrigerator_height', text="Right", toggle=True)
    row = box.row(align=True)
    row.label(text="Stile In Lieu Of Leg:")
    row.prop(cab, 'refrigerator_stile_left', text="Left", toggle=True)
    row.prop(cab, 'refrigerator_stile_right', text="Right", toggle=True)


def draw_wedge(layout, root):
    """Tip-up wedge calculator + live inputs. Refrigerator cabinets only.

    When enabled the three calc inputs are shown as live props (their
    update callback re-runs recalc, so the chamfer tracks edits); the
    calculator dialog is still available for the guided preview."""
    if root.get('CLASS_NAME') != 'RefrigeratorCabinet':
        return
    cab = root.face_frame_cabinet
    box = layout.box()
    box.label(text="Tip-Up Wedge", icon='MOD_BEVEL')
    if cab.wedge_enabled:
        col = box.column(align=True)
        col.prop(cab, 'wedge_ceiling_height', text="Ceiling")
        col.prop(cab, 'wedge_fudge', text="Fudge")
        col.prop(cab, 'wedge_max_height', text="Max Height")
        row = box.row(align=True)
        row.operator("hb_face_frame.add_refrigerator_wedge",
                     text="Calculator", icon='MOD_BEVEL')
        row.operator("hb_face_frame.remove_refrigerator_wedge",
                     text="Remove", icon='X')
    else:
        box.operator("hb_face_frame.add_refrigerator_wedge", icon='MOD_BEVEL')


def _is_floating_shelf(obj):
    """True when obj (or its cabinet root) is a floating shelf."""
    root = types_face_frame.find_cabinet_root(obj)
    return root is not None and bool(root.get('IS_FLOATING_SHELF'))


def draw_floating_shelf(layout, root):
    """Floating shelf prompts: type, dimensions, finished ends, and the
    Heavy-Duty light groove. Shown in the sidebar
    (HB_FACE_FRAME_PT_floating_shelf) and the right-click popup. Height
    (Dim Z) is the shelf's overall thickness."""
    cab = root.face_frame_cabinet
    shelf = root.floating_shelf

    layout.prop(shelf, 'shelf_type', text="Type")

    col = layout.column(align=True)
    col.prop(cab, 'width', text="Width")
    col.prop(cab, 'depth', text="Depth")
    col.prop(cab, 'height', text="Thickness")

    box = layout.box()
    box.label(text="Finished Ends")
    row = box.row(align=True)
    row.prop(shelf, 'finish_left', text="Left", toggle=True)
    row.prop(shelf, 'finish_right', text="Right", toggle=True)

    layout.prop(shelf, 'material_thickness', text="Material Thickness")

    layout.separator()
    layout.operator("hb_face_frame.duplicate_floating_shelf",
                    text="Set Quantity & Spacing...", icon='LINENUMBERS_ON')

    # Light groove - Heavy Duty shelves only.
    if shelf.shelf_type == 'HEAVY_DUTY':
        gbox = layout.box()
        gbox.label(text="Light Groove")
        grow = gbox.row(align=True)
        grow.prop(shelf, 'include_groove_top', text="Top", toggle=True)
        grow.prop(shelf, 'include_groove_bottom', text="Bottom", toggle=True)
        gsub = gbox.column(align=True)
        gsub.enabled = shelf.include_groove_top or shelf.include_groove_bottom
        gsub.prop(shelf, 'groove_distance_from_rear', text="Distance From Rear")
        gsub.prop(shelf, 'groove_width', text="Width")
        gsub.prop(shelf, 'groove_depth', text="Depth")


def draw_valance_product(layout, root):
    """Valance prompts: dimensions, finished ends, and the cover board.
    Shown in the right-click popup. Height (Dim Z) is the valance
    board's vertical drop."""
    cab = root.face_frame_cabinet
    val = root.valance_product

    col = layout.column(align=True)
    col.prop(cab, 'width', text="Width")
    col.prop(cab, 'depth', text="Depth")
    col.prop(cab, 'height', text="Height")

    box = layout.box()
    box.label(text="Finished Ends")
    row = box.row(align=True)
    row.prop(val, 'finish_left', text="Left", toggle=True)
    row.prop(val, 'finish_right', text="Right", toggle=True)

    layout.prop(val, 'frame_thickness', text="Frame Thickness")

    cbox = layout.box()
    cbox.prop(val, 'include_cover', text="Include Cover")
    csub = cbox.column(align=True)
    csub.enabled = val.include_cover
    csub.prop(val, 'cover_thickness', text="Cover Thickness")
    csub.prop(val, 'flush_bottom', text="Flush Bottom")
    srow = csub.row()
    srow.enabled = not val.flush_bottom
    srow.prop(val, 'top_scribe', text="Top Scribe")


def _is_leg_product(obj):
    """True when obj (or its cabinet root) is a leg product."""
    root = types_face_frame.find_cabinet_root(obj)
    return root is not None and bool(root.get('IS_LEG_PRODUCT'))


def draw_leg_product(layout, root):
    """Leg product prompts: dimensions + the leg_product options.

    Shown in the sidebar (HB_FACE_FRAME_PT_leg_product) and the
    right-click "Leg Properties..." popup. finish_type covers the old
    loose-stile / end-leg / intermediate-leg variants; only_stile drops
    everything but the stile; column removes the toe kick.
    """
    cab = root.face_frame_cabinet
    leg = root.leg_product

    col = layout.column(align=True)
    col.prop(cab, 'width', text="Width")
    col.prop(cab, 'height', text="Height")
    col.prop(cab, 'depth', text="Depth")

    box = layout.box()
    box.label(text="Leg Options")
    box.prop(leg, 'finish_type', text="Finish")
    row = box.row(align=True)
    row.prop(leg, 'only_stile', text="Only Stile", toggle=True)
    row.prop(leg, 'is_column', text="Column", toggle=True)
    vrow = box.row(align=True)
    vrow.prop(leg, 'is_appliance_leg', text="Appliance", toggle=True)
    vrow.prop(leg, 'is_island_leg', text="Island", toggle=True)

    # Material Thickness / Face Frame Thickness are intentionally not
    # exposed here - users never change them (recalc still reads the
    # propgroup defaults).
    col = layout.column(align=True)
    sub = col.column(align=True)
    sub.enabled = not leg.is_column
    sub.prop(leg, 'toe_kick_height', text="Toe Kick Height")
    sub.prop(leg, 'toe_kick_setback', text="Toe Kick Setback")

    # Rarely-touched sections collapse (closed by default) to keep the
    # dialog short. Toggle state lives on the leg_product propgroup.
    dbox = layout.box()
    dbox.prop(leg, 'show_panel_depth',
              icon='TRIA_DOWN' if leg.show_panel_depth else 'TRIA_RIGHT',
              emboss=False, text="Panel Depth Overrides")
    if leg.show_panel_depth:
        dcol = dbox.column(align=True)
        dcol.prop(leg, 'override_left_panel_depth', text="Left (0 = auto)")
        dcol.prop(leg, 'override_right_panel_depth', text="Right (0 = auto)")

    nbox = layout.box()
    nbox.prop(leg, 'show_back_nailers',
              icon='TRIA_DOWN' if leg.show_back_nailers else 'TRIA_RIGHT',
              emboss=False, text="Back & Nailers")
    if leg.show_back_nailers:
        nrow = nbox.row(align=True)
        nrow.prop(leg, 'include_back_left_nailer', text="Left Nailer", toggle=True)
        nrow.prop(leg, 'include_back_right_nailer', text="Right Nailer", toggle=True)
        nsub = nbox.column(align=True)
        nsub.enabled = leg.include_back_left_nailer or leg.include_back_right_nailer
        nsub.prop(leg, 'back_width', text="Back Width")
        nsub.prop(leg, 'back_thickness', text="Back Thickness")
        nsub.prop(leg, 'nailer_width', text="Nailer Width")
        nsub.prop(leg, 'nailer_thickness', text="Nailer Thickness")

    fbox = layout.box()
    fbox.prop(leg, 'show_finish_x',
              icon='TRIA_DOWN' if leg.show_finish_x else 'TRIA_RIGHT',
              emboss=False, text="Finish-X Bands")
    if leg.show_finish_x:
        fbox.prop(leg, 'flush_x_panel_width', text="Band Width")

    # Applied finished-end panels on the leg's Left / Right sides.
    # Mirrors the cabinet Finished Ends control: choosing Paneled /
    # False FF / Working FF spawns an applied panel on that side, built
    # in LegProductFaceFrameCabinet.recalculate via
    # _reconcile_applied_panels.
    ebox = layout.box()
    ebox.label(text="Finished Ends")
    ecol = ebox.column(align=True)
    for side, slabel in (('left', 'Left'), ('right', 'Right')):
        erow = ecol.row(align=True)
        erow.label(text=slabel)
        erow.prop(cab, f'{side}_finished_end_condition', text="")
        if getattr(cab, f'{side}_finished_end_condition') not in (
                'UNFINISHED', 'FLUSH_X'):
            erow.prop(cab, f'{side}_side_finished_extend_back',
                      text="Extend Back")


def draw_face_frame_defaults(layout, cab_props):
    """Face frame stile / rail / mid-stile widths, scribe, stile-to-floor,
    and end stile types. Per-opening overlay overrides live on the opening
    and are edited there, so they are no longer shown here."""
    # Face Frame Sizes: top rail, the two end stiles on one row, bottom
    # rail, then every mid stile width on a single row.
    fbox = layout.box()
    fbox.label(text="Face Frame Sizes")
    fcol = fbox.column(align=False)
    _draw_locked_rail_row(fcol, cab_props, 'top_rail_width',
                          'unlock_top_rail', "Top Rail")
    srow = fcol.row(align=True)
    _locked_field(srow, cab_props, 'left_stile_width',
                  'unlock_left_stile', "Left Stile")
    _locked_field(srow, cab_props, 'right_stile_width',
                  'unlock_right_stile', "Right Stile")
    _draw_locked_rail_row(fcol, cab_props, 'bottom_rail_width',
                          'unlock_bottom_rail', "Bottom Rail")
    # Mid stiles -- the dividers between bays. One width field per mid
    # stile on one row; index i is the stile between bay i and bay i + 1.
    if len(cab_props.mid_stile_widths) > 0:
        mrow = fcol.row(align=True)
        for i, ms in enumerate(cab_props.mid_stile_widths):
            _locked_field(mrow, ms, 'width', 'unlock', "Mid %d" % (i + 1))

    # Scribe Options
    scbox = layout.box()
    scbox.label(text="Scribe Options")
    sccol = scbox.column(align=True)
    sccol.prop(cab_props, 'left_scribe', text="Left Scribe")
    sccol.prop(cab_props, 'right_scribe', text="Right Scribe")
    sccol.prop(cab_props, 'top_scribe', text="Top Scribe")

    # Stile to Floor (base / tall / lap only) -- both toggles on one row.
    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        stfbox = layout.box()
        stfbox.label(text="Stile to Floor")
        stfrow = stfbox.row(align=True)
        stfrow.prop(cab_props, 'extend_left_stile_to_floor', text="Left")
        stfrow.prop(cab_props, 'extend_right_stile_to_floor', text="Right")

    # Stile Types (end stiles)
    ebox = layout.box()
    ebox.label(text="Stile Types")
    draw_blind_corners(ebox, cab_props)


def _locked_field(parent, bp, attr, unlock_attr, text):
    """A single width field + lock toggle drawn into ``parent`` (a row or
    column). Shared building block: _draw_locked_rail_row uses it for a
    full-width row, and the Face Frame Sizes grid uses it to pack two
    locked fields (Left / Right stile, or several mid stiles) onto one
    row. Locked = field disabled, value follows its computed default;
    unlocked = editable override that persists across style propagation."""
    unlocked = getattr(bp, unlock_attr)
    cell = parent.row(align=True)
    field = cell.row(align=True)
    field.enabled = unlocked
    field.prop(bp, attr, text=text)
    cell.prop(bp, unlock_attr, text="",
              icon='UNLOCKED' if unlocked else 'LOCKED')


def _draw_locked_rail_row(layout, bp, attr, unlock_attr, text):
    """Full-width width field + lock toggle on its own row. Generic over
    any object carrying ``attr`` + ``unlock_attr`` (bay or cabinet props).
    See _locked_field for the shared building block."""
    _locked_field(layout, bp, attr, unlock_attr, text)


def draw_bay_properties(layout, bay_obj):
    """All editable properties of a single bay. Used by both the
    sidebar Selection sub-panel and the bay_prompts popup. Includes a
    structural-edits row up top (insert before / after, delete)."""
    bp = bay_obj.face_frame_bay
    layout.label(text=f"Bay {bp.bay_index + 1}", icon='MESH_CUBE')

    # Structural edit strip: insert next to / delete this bay. Operators
    # take the bay index explicitly so they don't depend on selection.
    edits = layout.row(align=True)
    op = edits.operator(
        'hb_face_frame.insert_bay', text="Insert Before", icon='TRIA_LEFT',
    )
    op.bay_index = bp.bay_index
    op.direction = 'BEFORE'
    op = edits.operator(
        'hb_face_frame.insert_bay', text="Insert After", icon='TRIA_RIGHT',
    )
    op.bay_index = bp.bay_index
    op.direction = 'AFTER'
    op = edits.operator(
        'hb_face_frame.delete_bay', text="Delete", icon='X',
    )
    op.bay_index = bp.bay_index
    layout.separator()

    col = layout.column(align=True)

    # Width with unlock toggle - field disabled when auto, unlocked when manual
    width_row = col.row(align=True)
    field = width_row.row(align=True)
    field.enabled = bp.unlock_width
    field.prop(bp, 'width', text="Width")
    lock_icon = 'UNLOCKED' if bp.unlock_width else 'LOCKED'
    width_row.prop(bp, 'unlock_width', text="", icon=lock_icon)

    # Height with unlock toggle - same pattern as width. Greyed out on
    # auto since the recalc owns the value (= cabinet height - toe kick).
    height_row = col.row(align=True)
    field = height_row.row(align=True)
    field.enabled = bp.unlock_height
    field.prop(bp, 'height', text="Height")
    lock_icon = 'UNLOCKED' if bp.unlock_height else 'LOCKED'
    height_row.prop(bp, 'unlock_height', text="", icon=lock_icon)

    depth_row = col.row(align=True)
    field = depth_row.row(align=True)
    field.enabled = bp.unlock_depth
    field.prop(bp, 'depth', text="Depth")
    lock_icon = 'UNLOCKED' if bp.unlock_depth else 'LOCKED'
    depth_row.prop(bp, 'unlock_depth', text="", icon=lock_icon)
    col.separator()
    cab_type = bay_obj.parent.face_frame_cabinet.cabinet_type if bay_obj.parent else ''
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        kick_row = col.row(align=True)
        field = kick_row.row(align=True)
        field.enabled = bp.unlock_kick_height
        field.prop(bp, 'kick_height', text="Kick Height")
        lock_icon = 'UNLOCKED' if bp.unlock_kick_height else 'LOCKED'
        kick_row.prop(bp, 'unlock_kick_height', text="", icon=lock_icon)
    if cab_type == 'UPPER':
        col.prop(bp, 'top_offset', text="Top Offset")
    if cab_type in ('BASE', 'LAP_DRAWER'):
        col.prop(bp, 'front_drop', text="Front Drop")
        if bp.front_drop > 0.0:
            col.prop(bp, 'front_drop_include_fillers', text="Drop Fillers")
            if bp.front_drop_include_fillers:
                col.prop(bp, 'front_drop_set_appliance_width',
                         text="Set Appliance Width")
                if bp.front_drop_set_appliance_width:
                    col.prop(bp, 'front_drop_appliance_width',
                             text="Appliance Width")
                else:
                    col.prop(bp, 'front_drop_left_filler', text="Left Filler")
                    col.prop(bp, 'front_drop_right_filler', text="Right Filler")
    col.separator()
    _draw_locked_rail_row(col, bp, 'top_rail_width',
                          'unlock_top_rail', "Top Rail Width")
    _draw_locked_rail_row(col, bp, 'bottom_rail_width',
                          'unlock_bottom_rail', "Bottom Rail Width")
    col.separator()
    col.prop(bp, 'remove_bottom', text="Remove Bottom")
    col.prop(bp, 'remove_carcass', text="Remove Carcass")
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.prop(bp, 'floating_bay', text="Floating")
    col.prop(bp, 'finish_bay', text="Finish")
    if bp.finish_bay:
        col.prop(bp, 'finish_bay_flush', text="Finish Flush")
        if bp.finish_bay_flush:
            col.prop(bp, 'finish_bay_flush_depth', text="Flush Depth")


def _root_opening_size(opening_obj):
    """FF opening height for a bay's ROOT opening (a full-height opening
    that fills its bay), or None if it can't be resolved or the opening
    is a split child.

    A root opening's `size` prop is ignored by the redistributor (it
    fills the bay), so the stored value is meaningless. This returns the
    real opening height the solver builds - cage height minus the top /
    bottom reveals - so the UI can show the correct size read-only."""
    bay = opening_obj.parent
    if bay is None or not bay.get(types_face_frame.TAG_BAY_CAGE):
        return None  # split child (or detached) - its own size is real
    root = types_face_frame.find_cabinet_root(opening_obj)
    bi = bay.get('hb_bay_index')
    if root is None or bi is None:
        return None
    from . import solver_face_frame
    layout = solver_face_frame.FaceFrameLayout(root)
    for lf in solver_face_frame.bay_openings(layout, bi).get('leaves', []):
        if lf['obj_name'] == opening_obj.name:
            return lf['cage_dim_z'] - lf['reveal_top'] - lf['reveal_bottom']
    return None


def draw_opening_properties(layout, opening_obj):
    """All editable properties of a single opening: front type, hinge
    side, and the four per-side overlays. Each overlay row has an
    unlock toggle (off = use cabinet default, on = use this opening's
    own value) and an overlay field that's only enabled when unlocked.
    """
    op = opening_obj.face_frame_opening
    layout.label(text=f"Opening {op.opening_index + 1}", icon='MESH_PLANE')

    # Size + unlock - meaningful only when the opening is a child of a
    # split node (the redistributor uses it). A bay's ROOT opening fills
    # the bay, so its size is bay-driven and not adjustable here; show the
    # real opening height read-only instead of the stale, ignored prop.
    root_size = _root_opening_size(opening_obj)
    if root_size is not None:
        size_row = layout.row(align=True)
        size_row.enabled = False
        size_row.label(
            text="Size:  " + units.unit_to_string(
                bpy.context.scene.unit_settings, root_size))
    else:
        size_row = layout.row(align=True)
        field = size_row.row(align=True)
        field.enabled = op.unlock_size
        field.prop(op, 'size', text="Size")
        lock_icon = 'UNLOCKED' if op.unlock_size else 'LOCKED'
        size_row.prop(op, 'unlock_size', text="", icon=lock_icon)

    # Front: collapsible -- front type plus its conditional extras.
    fbox = layout.box()
    fbox.prop(op, 'show_front', text="Front Type",
              icon='TRIA_DOWN' if op.show_front else 'TRIA_RIGHT', emboss=False)
    if op.show_front:
        fcol = fbox.column(align=True)
        fcol.prop(op, 'front_type', text="Front Type")
        if op.front_type in ('DOOR', 'PULLOUT'):
            fcol.prop(op, 'hinge_side', text="Hinge Side")

        # Sink apron (door openings only): a fixed face-frame panel across
        # the top of the opening for an apron / farmhouse sink. Doors stay
        # full height; the apron sits behind them.
        if op.front_type == 'DOOR':
            fcol.prop(op, 'add_apron', text="Add Apron")
            if op.add_apron:
                fcol.prop(op, 'apron_height', text="Apron Height")

        # Drawer-look door (single-leaf swing doors): render the leaf as a
        # stack of applied drawer fronts that still opens as one door.
        if op.front_type == 'DOOR' and op.hinge_side in ('LEFT', 'RIGHT'):
            fcol.prop(op, 'drawer_look_divisions', text="Drawer-Look")
            if op.drawer_look_divisions != 'NONE':
                heights_box = fcol.box()
                heights_box.label(text="Drawer Opening Heights (top to bottom)")
                for idx in range(len(op.drawer_look_openings) - 1, -1, -1):
                    item = op.drawer_look_openings[idx]
                    hrow = heights_box.row(align=True)
                    field = hrow.row(align=True)
                    field.enabled = item.unlock_size
                    field.prop(item, 'size', text="Opening " + str(idx + 1))
                    hrow.prop(item, 'unlock_size', text="",
                              icon='UNLOCKED' if item.unlock_size else 'LOCKED')

        # Tilt-out flag (false fronts only): label-only -- the 2D elevation
        # prints TILT-OUT instead of FALSE. No geometry change.
        if op.front_type == 'FALSE_FRONT':
            fcol.prop(op, 'is_tilt_out', text="Tilt-Out")

        # Appliance: filler stiles fitting an appliance. Two input modes
        # toggled by Set Appliance Width (see Face_Frame_Opening_Props).
        if op.front_type == 'APPLIANCE':
            fcol.prop(op, 'include_fillers', text="Include Fillers")
            if op.include_fillers:
                fcol.prop(op, 'set_appliance_width', text="Set Appliance Width")
                if op.set_appliance_width:
                    fcol.prop(op, 'appliance_width', text="Appliance Width")
                else:
                    frow = fcol.row(align=True)
                    frow.prop(op, 'left_filler_amount', text="Left Filler")
                    frow.prop(op, 'right_filler_amount', text="Right Filler")

    # Open: swing / motion amount, kept separate from the front-type
    # controls. INSET_PANEL has no motion; NONE has no front to animate.
    if op.front_type not in ('NONE', 'INSET_PANEL', 'APPLIANCE'):
        opbox = layout.box()
        opbox.prop(op, 'swing_percent', text="Open", slider=True)

    # Finish: collapsible.
    nbox = layout.box()
    nbox.prop(op, 'show_finish', text="Finish Options",
              icon='TRIA_DOWN' if op.show_finish else 'TRIA_RIGHT', emboss=False)
    if op.show_finish:
        ncol = nbox.column(align=True)
        ncol.prop(op, 'finish_opening', text="Finish Opening")
        if op.finish_opening:
            ncol.prop(op, 'finish_opening_flush', text="Finish Flush")
            if op.finish_opening_flush:
                ncol.prop(op, 'finish_opening_flush_depth', text="Flush Depth")

    # Overlays: collapsible.
    obox = layout.box()
    obox.prop(op, 'show_overlays', text="Overlays",
              icon='TRIA_DOWN' if op.show_overlays else 'TRIA_RIGHT', emboss=False)
    if op.show_overlays:
        ocol = obox.column(align=True)
        from . import solver_face_frame
        ov_root = types_face_frame.find_cabinet_root(opening_obj)
        ov_cab = ov_root.face_frame_cabinet if ov_root is not None else None
        for side in ('top', 'bottom', 'left', 'right'):
            unlocked = getattr(op, f'unlock_{side}_overlay')
            row = ocol.row(align=True)
            field = row.row(align=True)
            field.enabled = unlocked
            if unlocked or ov_cab is None:
                field.prop(op, f'{side}_overlay', text=side.capitalize())
            else:
                # Locked: the solver uses the cabinet default, so show that
                # resolved value read-only instead of this opening's own
                # (ignored) stored overlay -- which would otherwise misread
                # as the 0.5" property default.
                eff = solver_face_frame.resolved_overlay(ov_cab, op, side)
                field.label(text=side.capitalize() + ":  " + units.unit_to_string(
                    bpy.context.scene.unit_settings, eff))
            lock_icon = 'UNLOCKED' if unlocked else 'LOCKED'
            row.prop(op, f'unlock_{side}_overlay', text="", icon=lock_icon)

    # Interior Items: hidden for panel roots - panels never have
    # interior objects (no carcass to hold them). Walk up to the root
    # to read the cabinet_type; opening -> bay -> root.
    root = types_face_frame.find_cabinet_root(opening_obj)
    if root is not None and root.face_frame_cabinet.cabinet_type == 'PANEL':
        return

    ibox = layout.box()
    ibox.prop(op, 'show_interior_items', text="Interior Items",
              icon='TRIA_DOWN' if op.show_interior_items else 'TRIA_RIGHT',
              emboss=False)
    if op.show_interior_items:
        # When the opening has no tree the user can subdivide it directly,
        # add items to the flat collection, or both. Once a tree exists,
        # items live on leaves so the flat add buttons are suppressed; the
        # tree itself is rendered inline below so the modal popup remains
        # self-sufficient (no need to leave the popup to edit a region).
        has_tree = any(
            c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)
            or c.get(types_face_frame.TAG_INTERIOR_REGION)
            for c in opening_obj.children
        )
        if not has_tree:
            # Pass the opening's name as target_name so the Add / Remove
            # operators in the buttons below survive an active-object
            # change mid-popup (e.g., the shelf the user right-clicked
            # gets wiped on a kind-change recalc).
            _draw_interior_items_section(ibox, op, target_name=opening_obj.name)
        else:
            _draw_interior_tree_inline(ibox, opening_obj)


def _draw_interior_items_section(layout, target_props, target_name=""):
    """Add buttons + per-item rows for any object whose props expose an
    `interior_items` collection. Used by the opening panel (flat path),
    the leaf region panel, and the inline tree view in the opening
    popup. When `target_name` is non-empty it is stamped on every
    add/remove button so the operators address that object regardless
    of context.active_object - required when the panel renders inside
    a modal popup that locks the active object to the opening cage.
    """
    # Single Add button pops a menu of every option (subdivisions
    # and item kinds) so the panel stays compact regardless of how
    # many leaves are visible at once.
    add_op = layout.operator(
        "hb_face_frame.show_interior_add_menu",
        text="Add...", icon='ADD',
    )
    add_op.target_name = target_name

    if not target_props.interior_items:
        layout.label(text="(none)")
        return

    # One inline block per item. Each row carries its own remove
    # button keyed by index so the operator doesn't have to consult
    # interior_items_index.
    box = layout.box()
    for i, item in enumerate(target_props.interior_items):
        sub = box.column(align=True)
        header = sub.row(align=True)
        header.prop(item, 'kind', text="")
        rm = header.operator(
            "hb_face_frame.remove_interior_item",
            text="", icon='X',
        )
        rm.index = i
        rm.target_name = target_name

        if item.kind in {'ADJUSTABLE_SHELF', 'GLASS_SHELF'}:
            qty_row = sub.row(align=True)
            field = qty_row.row(align=True)
            # Greyed out when on auto - the recalc owns the value.
            field.enabled = item.unlock_shelf_qty
            field.prop(item, 'shelf_qty', text="Qty")
            lock_icon = 'UNLOCKED' if item.unlock_shelf_qty else 'LOCKED'
            qty_row.prop(item, 'unlock_shelf_qty', text="", icon=lock_icon)
            sub.prop(item, 'shelf_setback', text="Setback")
            if item.kind == 'ADJUSTABLE_SHELF':
                sub.prop(item, 'shelf_nosing_style', text="Nosing")
                if item.shelf_nosing_style in shelf_nosing.EXTRA_HEIGHT_STYLES:
                    sub.prop(item, 'shelf_nosing_height', text="Nosing Height")
        elif item.kind == 'PULLOUT_SHELF':
            qty_row = sub.row(align=True)
            field = qty_row.row(align=True)
            field.enabled = item.unlock_qty
            field.prop(item, 'qty', text="Qty")
            lock_icon = 'UNLOCKED' if item.unlock_qty else 'LOCKED'
            qty_row.prop(item, 'unlock_qty', text="", icon=lock_icon)
            sub.prop(item, 'pullout_thickness', text="Thickness")
            sub.prop(item, 'distance_between', text="Gap Between")
            sub.prop(item, 'bottom_gap', text="Bottom Gap")
            sub.prop(item, 'item_setback', text="Front Setback")
            # Spacer width is fixed (ASSEMBLY_SPACER_WIDTH in the
            # solver), so no spacer_height row -- same as rollouts.
        elif item.kind == 'ROLLOUT':
            # One row per box: each box picks its own standard height (or
            # Custom to type one). The box count is the number of rows.
            for j, box in enumerate(item.rollout_boxes):
                brow = sub.row(align=True)
                brow.label(text=f"Box {j + 1}")
                brow.prop(box, 'height_preset', text="")
                if box.height_preset == 'CUSTOM':
                    brow.prop(box, 'height', text="")
                rm_box = brow.operator(
                    "hb_face_frame.remove_rollout_box", text="", icon='X',
                )
                rm_box.item_index = i
                rm_box.box_index = j
                rm_box.target_name = target_name
            add_box = sub.operator(
                "hb_face_frame.add_rollout_box", text="Add Box", icon='ADD',
            )
            add_box.item_index = i
            add_box.target_name = target_name
            sub.prop(item, 'distance_between', text="Gap Between")
            sub.prop(item, 'bottom_gap', text="Bottom Gap")
            sub.prop(item, 'item_setback', text="Front Setback")
            # Spacer width is fixed (ASSEMBLY_SPACER_WIDTH in the
            # solver), so no spacer_height row -- same as pullouts.
        elif item.kind == 'TRAY_DIVIDERS':
            sub.prop(item, 'tray_qty', text="Qty")
            sub.prop(item, 'tray_remove_shelf', text="Remove Locked Shelf")
            shelf_row = sub.row()
            shelf_row.enabled = not item.tray_remove_shelf
            shelf_row.prop(item, 'tray_opening_height', text="Opening Height")
            sub.prop(item, 'tray_divider_thickness', text="Divider Thickness")
            sub.prop(item, 'tray_setback', text="Setback")
        elif item.kind == 'VANITY_SHELVES':
            sub.prop(item, 'vanity_z', text="Shelf Z")
            sub.prop(item, 'vanity_length', text="Shelf Length")
        elif item.kind == 'ACCESSORY':
            sub.prop(item, 'accessory_label', text="Label")

        if i < len(target_props.interior_items) - 1:
            box.separator()


def _walk_tree_leaves(opening_obj):
    """DFS yielder for leaf cages of the opening's interior tree.
    Yields (leaf_obj, parent_split, child_index, depth). Skips when
    no tree exists.
    """
    def _recurse(node, depth):
        if node.get(types_face_frame.TAG_INTERIOR_REGION):
            parent = node.parent
            if parent is not None and parent.get(
                    types_face_frame.TAG_INTERIOR_SPLIT_NODE):
                yield (node, parent,
                       node.get('hb_interior_child_index', 0), depth)
            return
        if not node.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE):
            return
        children = sorted(
            [c for c in node.children
             if c.get(types_face_frame.TAG_INTERIOR_REGION)
             or c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)],
            key=lambda c: c.get('hb_interior_child_index', 0),
        )
        for c in children:
            yield from _recurse(c, depth + 1)

    for c in opening_obj.children:
        if (c.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE)
                or c.get(types_face_frame.TAG_INTERIOR_REGION)):
            yield from _recurse(c, 0)


def _draw_split_face_frame_props(layout, sp):
    """Optional inline face frame member for an interior split. The
    width field is enabled only while the toggle is on; the width
    seeds itself from the cabinet mid rail / mid stile width the first
    time the toggle is enabled.
    """
    layout.prop(sp, 'add_face_frame')
    width_row = layout.row(align=True)
    width_row.enabled = sp.add_face_frame
    width_row.prop(sp, 'face_frame_width', text="Face Frame Width")


def _draw_interior_tree_inline(layout, opening_obj):
    """Render every leaf of the opening's interior tree as an inline
    sub-section. Used by the opening's modal popup so the user can
    edit any region's divider position, items, and further splits
    without leaving the popup. Buttons stamp `target_name` on the
    operators so they address the right leaf despite active_object
    being the opening cage.

    Per-leaf section layout:
      - Header: leaf name + side label (Left/Right/Bottom/Top)
      - Divider Thickness (parent split)
      - Region Size + lock (child 0 only - walker reads child 0's size
        and computes child 1 as the remainder; child 1 shows a hint)
      - Add Division / Add Fixed Shelf (subdivide further)
      - Items section
    """
    leaves = list(_walk_tree_leaves(opening_obj))
    if not leaves:
        layout.label(text="(no regions)", icon='INFO')
        return
    for leaf, sp_obj, child_index, depth in leaves:
        rp = leaf.face_frame_interior_region
        sp = sp_obj.face_frame_interior_split

        if sp.axis == 'H':
            side = "Bottom" if child_index == 0 else "Top"
        else:
            side = "Left" if child_index == 0 else "Right"

        box = layout.box()
        header = box.row(align=True)
        # Triangle toggle drives the per-region `expanded` prop.
        # Collapsed by default keeps the popup short; user expands
        # only the regions they want to edit.
        tri_icon = 'TRIA_DOWN' if rp.expanded else 'TRIA_RIGHT'
        header.prop(rp, 'expanded', text="", icon=tri_icon, emboss=False)
        # Depth indent so nested regions read as visually nested
        # even though all leaves are flat-listed.
        if depth > 0:
            header.label(text="  " * depth + "")
        header.label(
            text=f"{leaf.name}  -  {side}",
            icon='MESH_PLANE',
        )

        if not rp.expanded:
            continue

        col = box.column(align=True)
        col.prop(sp, 'divider_thickness', text="Divider Thickness")
        _draw_split_face_frame_props(col, sp)

        # Both children carry an editable size now that sibling
        # redistribution honors locks. Editing either side moves the
        # divider; the unlocked sibling absorbs the remainder.
        size_row = col.row(align=True)
        field = size_row.row(align=True)
        field.enabled = rp.unlock_size
        field.prop(rp, 'size', text="Region Size")
        lock_icon = 'UNLOCKED' if rp.unlock_size else 'LOCKED'
        size_row.prop(rp, 'unlock_size', text="", icon=lock_icon)

        # Remove the parent split. Label tracks the split's axis so
        # it reads naturally for the user (either child of the same
        # split removes the same divider, so the wording matches the
        # divider type rather than the side).
        remove_label = ("Remove Fixed Shelf" if sp.axis == 'H'
                        else "Remove Division")
        remove_op = col.operator(
            "hb_face_frame.remove_interior_split",
            text=remove_label, icon='X',
        )
        remove_op.target_name = leaf.name

        # Items list + Add menu (the menu covers both subdivisions
        # and item kinds, so no separate subdivide row needed).
        box.separator()
        _draw_interior_items_section(box, rp, target_name=leaf.name)


def draw_interior_region_properties(layout, leaf_obj, opening_obj):
    """N-panel content when an interior region (leaf cage) is active.
    Shows the parent split's axis + divider thickness, this leaf's
    size (the divider position handle), Add Division / Add Fixed Shelf
    for further subdivision, and the leaf's interior_items list.
    """
    rp = leaf_obj.face_frame_interior_region
    parent = leaf_obj.parent
    if parent is None or not parent.get(types_face_frame.TAG_INTERIOR_SPLIT_NODE):
        layout.label(text="Region with no parent split", icon='ERROR')
        return
    sp = parent.face_frame_interior_split
    child_index = leaf_obj.get('hb_interior_child_index', 0)

    # Header: which side of the split this leaf is on
    if sp.axis == 'H':
        side = "Bottom" if child_index == 0 else "Top"
    else:
        side = "Left" if child_index == 0 else "Right"
    header = "Interior Region"
    if opening_obj is not None:
        header += f" ({side} of {opening_obj.name})"
    layout.label(text=header, icon='MESH_PLANE')

    # Divider geometry: parent split's axis label + thickness, and
    # this leaf's own size (editing it moves the divider when this
    # leaf is the lower/left child; for the upper/right leaf the size
    # is currently advisory until sibling redistribution is wired).
    col = layout.column(align=True)
    axis_label = "Fixed Shelf" if sp.axis == 'H' else "Division"
    col.label(text=f"Parent Split: {axis_label}")
    col.prop(sp, 'divider_thickness', text="Divider Thickness")
    _draw_split_face_frame_props(col, sp)

    size_row = col.row(align=True)
    field = size_row.row(align=True)
    field.enabled = rp.unlock_size
    field.prop(rp, 'size', text="Region Size")
    lock_icon = 'UNLOCKED' if rp.unlock_size else 'LOCKED'
    size_row.prop(rp, 'unlock_size', text="", icon=lock_icon)

    remove_label = ("Remove Fixed Shelf" if sp.axis == 'H'
                    else "Remove Division")
    remove_op = col.operator(
        "hb_face_frame.remove_interior_split",
        text=remove_label, icon='X',
    )
    # target_name keeps the operator pointed at this region even if
    # the active object goes stale (e.g., an interior part wipe).
    remove_op.target_name = leaf_obj.name

    layout.separator()
    layout.label(text="Interior Items")
    # target_name is the leaf region's name; lets buttons resolve back
    # to this region's propgroup even if active_object goes stale.
    _draw_interior_items_section(layout, rp, target_name=leaf_obj.name)


def draw_mid_stile_properties(layout, root, msi):
    """All editable properties of a single mid stile."""
    cab_props = root.face_frame_cabinet
    if msi >= len(cab_props.mid_stile_widths):
        layout.label(text="Mid stile not found", icon='ERROR')
        return
    ms = cab_props.mid_stile_widths[msi]
    layout.label(text=f"Mid Stile {msi + 1}", icon='SNAP_EDGE')
    col = layout.column(align=True)
    col.prop(ms, 'width', text="Width")
    col.prop(ms, 'extend_up_amount', text="Extend Up")
    col.prop(ms, 'extend_down_amount', text="Extend Down")
    col.separator()
    col.prop(ms, 'division_location', text="Division")
    if ms.division_location == 'OFFSET':
        col.prop(ms, 'division_offset', text="Offset")


def draw_end_stile_properties(layout, root, role):
    cab_props = root.face_frame_cabinet
    is_left = role == types_face_frame.PART_ROLE_LEFT_STILE
    side = "Left" if is_left else "Right"
    attr = 'left_stile_width' if is_left else 'right_stile_width'
    layout.label(text=f"{side} End Stile", icon='SNAP_EDGE')
    layout.prop(cab_props, attr, text="Width")


def draw_rail_properties(layout, root, rail_obj, role):
    """Rails are segment-keyed; the editable property is the bay's rail
    width override at the segment's start bay."""
    cab_props = root.face_frame_cabinet
    seg_start = rail_obj.get('hb_segment_start_bay', 0)
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if seg_start >= len(bays):
        layout.label(text="Rail's bay not found", icon='ERROR')
        return
    bp = bays[seg_start].face_frame_bay
    is_top = role == types_face_frame.PART_ROLE_TOP_RAIL
    label = "Top Rail" if is_top else "Bottom Rail"
    attr = 'top_rail_width' if is_top else 'bottom_rail_width'
    layout.label(text=f"{label} (Bay {seg_start + 1})", icon='SNAP_EDGE')
    unlock_attr = 'unlock_top_rail' if is_top else 'unlock_bottom_rail'
    _draw_locked_rail_row(layout, bp, attr, unlock_attr, "Width")
    # Bottom rail can be removed outright (drops Remove Bottom across the
    # rail's bay span). Restore via Remove Bottom in the bay properties.
    if not is_top:
        layout.separator()
        layout.operator("hb_face_frame.remove_bottom_rail",
                        text="Remove Bottom Rail", icon='X')


def draw_blind_corners(layout, cab_props):
    """Per-side stile type plus blind flag and depth.

    Stile type is the structural choice (Standard / Wall / Blind) that
    drives the end stile's width. The blind flag and amount are only
    relevant - and only revealed - when the type is BLIND. The flag
    indicates an adjacent perpendicular cabinet is butted against this
    end (widens the stile by 0.75" and shows the blind panel); the
    amount controls how far the blind panel extends forward from the
    back to close off the dead corner.
    """
    col = layout.column(align=True)
    for side, label in (('left', 'Left'), ('right', 'Right')):
        row = col.row(align=True)
        row.label(text=label)
        row.prop(cab_props, f'{side}_stile_type', text="")
        if getattr(cab_props, f'{side}_stile_type') == 'BLIND':
            row.prop(cab_props, f'blind_{side}', text="")
            if getattr(cab_props, f'blind_{side}'):
                row.prop(cab_props, f'blind_amount_{side}', text="")


def draw_finished_ends(layout, cab_props):
    """Per-cabinet finished ends.

    One row per side (Left / Right / Back): label + finish-type dropdown.
    Left / Right also show that side's Extend Back inline on the same row
    when finished; their scribe (UNFINISHED) or flush-X amount (FLUSH_X)
    drops to its own labeled row. The Back's two extends (L / R) sit on a
    dedicated row below its dropdown.
    """
    col = layout.column(align=True)
    for side, label, has_flush_x in (
        ('left', 'Left', True),
        ('right', 'Right', True),
        ('back', 'Back', False),
    ):
        fin_type = getattr(cab_props, f'{side}_finished_end_condition')
        # Left / Right: label + dropdown, with that side's Extend Back
        # inline on the same row when it carries a finished part. The Back
        # keeps its two extends (L / R) on a dedicated row below.
        row = col.row(align=True)
        row.label(text=label)
        row.prop(cab_props, f'{side}_finished_end_condition', text="")
        if (side in ('left', 'right')
                and fin_type not in ('UNFINISHED', 'FLUSH_X')):
            row.prop(cab_props, f'{side}_side_finished_extend_back',
                     text="Extend Back")
        if has_flush_x and fin_type == 'FLUSH_X':
            col.prop(cab_props, f'{side}_flush_x_amount', text="Flush-X Amount")
        elif fin_type == 'UNFINISHED' and side != 'back':
            col.prop(cab_props, f'{side}_scribe', text="Scribe")

        # Return closeout: only meaningful when a FINISHED or PANELED side is
        # extended back past a FINISHED or PANELED back. Nonzero return width
        # caps the exposed corner with a return panel + a rear stile that wide.
        if (side in ('left', 'right') and fin_type in ('FINISHED', 'PANELED')
                and getattr(cab_props, f'{side}_side_finished_extend_back') != 0.0
                and getattr(cab_props, 'back_finished_end_condition')
                in ('FINISHED', 'PANELED')):
            col.prop(cab_props, f'{side}_side_return_width', text="Return Width")
            # Per-member Finished / Paneled construction, once a return exists.
            if getattr(cab_props, f'{side}_side_return_width') != 0.0:
                col.prop(cab_props, f'{side}_side_return_panel_type',
                         text="Side Return")
                col.prop(cab_props, f'{side}_side_return_stile_type',
                         text="Return Stile")

        # Back: extend past the L / R cabinet ends, on its own row.
        if side == 'back' and fin_type != 'UNFINISHED':
            ext = col.row(align=True)
            ext.prop(cab_props, 'back_finished_extend_left', text="Extend L")
            ext.prop(cab_props, 'back_finished_extend_right', text="Extend R")

    # Shiplap course width: one setting shared by every shiplap side.
    if 'SHIPLAP' in (cab_props.left_finished_end_condition,
                     cab_props.right_finished_end_condition,
                     cab_props.back_finished_end_condition):
        col.prop(cab_props, 'shiplap_board_width', text="Shiplap Width")


def draw_all_bays_summary(layout, root):
    """Compact list of all bays with index and dims."""
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if not bays:
        layout.label(text="No bays", icon='INFO')
        return
    M_TO_IN = 39.3700787
    col = layout.column(align=True)
    for bay_obj in bays:
        bp = bay_obj.face_frame_bay
        row = col.row()
        w = bp.width * M_TO_IN
        h = bp.height * M_TO_IN
        d = bp.depth * M_TO_IN
        row.label(text=f"Bay {bp.bay_index + 1}")
        row.label(text=f"{w:.0f} x {h:.0f} x {d:.0f} in")


def _bay_size_summary(bp):
    """Compact 'W x H x D in' string for read-only bay display. Uses
    inches with one-decimal precision to match the All Bays summary
    style."""
    M_TO_IN = 39.3700787
    w = bp.width * M_TO_IN
    h = bp.height * M_TO_IN
    d = bp.depth * M_TO_IN
    return f"{w:.1f} x {h:.1f} x {d:.1f} in"


def draw_bay_in_prompts(layout, bay_obj):
    """Compact bay block for the cabinet_prompts popup. Collapsed
    state: a single header row 'Bay N   W x H x D in' plus an expand
    arrow. Expanded state: editable W / H / D with locks, then the
    secondary properties (kick, top offset, rails, flags). Single-bay
    cabinets bypass this and use a fully read-only summary.
    """
    bp = bay_obj.face_frame_bay

    # Header row: expand arrow + label + size summary + delete X.
    expand_icon = 'TRIA_DOWN' if bp.prompts_expanded else 'TRIA_RIGHT'
    header = layout.row(align=True)
    header.prop(
        bp, 'prompts_expanded',
        text="", icon=expand_icon, emboss=False,
    )
    header.label(text=f"Bay {bp.bay_index + 1}", icon='MESH_PLANE')
    header.label(text=_bay_size_summary(bp))
    rm = header.operator(
        'hb_face_frame.delete_bay', text="", icon='X', emboss=False,
    )
    rm.bay_index = bp.bay_index

    if not bp.prompts_expanded:
        return

    col = layout.column(align=True)
    # Width / Height / Depth - same lock-and-field pattern as the full
    # draw_bay_properties helper.
    for attr in ('width', 'height', 'depth'):
        unlocked = getattr(bp, f'unlock_{attr}')
        row = col.row(align=True)
        field = row.row(align=True)
        field.enabled = unlocked
        field.prop(bp, attr, text=attr.capitalize())
        lock_icon = 'UNLOCKED' if unlocked else 'LOCKED'
        row.prop(bp, f'unlock_{attr}', text="", icon=lock_icon)
    col.separator()
    cab_type = bay_obj.parent.face_frame_cabinet.cabinet_type if bay_obj.parent else ''
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        kick_row = col.row(align=True)
        field = kick_row.row(align=True)
        field.enabled = bp.unlock_kick_height
        field.prop(bp, 'kick_height', text="Kick Height")
        lock_icon = 'UNLOCKED' if bp.unlock_kick_height else 'LOCKED'
        kick_row.prop(bp, 'unlock_kick_height', text="", icon=lock_icon)
    if cab_type == 'UPPER':
        col.prop(bp, 'top_offset', text="Top Offset")
    if cab_type in ('BASE', 'LAP_DRAWER'):
        col.prop(bp, 'front_drop', text="Front Drop")
        if bp.front_drop > 0.0:
            col.prop(bp, 'front_drop_include_fillers', text="Drop Fillers")
            if bp.front_drop_include_fillers:
                col.prop(bp, 'front_drop_set_appliance_width',
                         text="Set Appliance Width")
                if bp.front_drop_set_appliance_width:
                    col.prop(bp, 'front_drop_appliance_width',
                             text="Appliance Width")
                else:
                    col.prop(bp, 'front_drop_left_filler', text="Left Filler")
                    col.prop(bp, 'front_drop_right_filler', text="Right Filler")
    col.separator()
    _draw_locked_rail_row(col, bp, 'top_rail_width',
                          'unlock_top_rail', "Top Rail Width")
    _draw_locked_rail_row(col, bp, 'bottom_rail_width',
                          'unlock_bottom_rail', "Bottom Rail Width")
    col.separator()
    col.prop(bp, 'remove_bottom', text="Remove Bottom")
    col.prop(bp, 'remove_carcass', text="Remove Carcass")
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.prop(bp, 'floating_bay', text="Floating")
    col.prop(bp, 'finish_bay', text="Finish")
    if bp.finish_bay:
        col.prop(bp, 'finish_bay_flush', text="Finish Flush")
        if bp.finish_bay_flush:
            col.prop(bp, 'finish_bay_flush_depth', text="Flush Depth")


def draw_bays_in_prompts(layout, root):
    """Bays section for the cabinet_prompts popup. Single-bay cabinets
    get a read-only size summary - the cabinet's Dimensions section above
    IS the editor for that bay. Multi-bay cabinets get one compact box
    per bay with editable size + an expand toggle for secondary props.
    """
    bays = sorted(
        [c for c in root.children if c.get(types_face_frame.TAG_BAY_CAGE)],
        key=lambda c: c.get('hb_bay_index', 0),
    )
    if not bays:
        return
    box = layout.box()
    box.label(text="Bays", icon='MESH_GRID')
    if len(bays) == 1:
        bp = bays[0].face_frame_bay
        row = box.row()
        row.label(text=f"Bay {bp.bay_index + 1}")
        row.label(text=_bay_size_summary(bp))
    else:
        for bay_obj in bays:
            bay_box = box.box()
            draw_bay_in_prompts(bay_box, bay_obj)
    # Footer: add a new bay at the end of the run.
    last_index = bays[-1].face_frame_bay.bay_index
    add = box.operator(
        'hb_face_frame.insert_bay', text="Add Bay", icon='ADD',
    )
    add.bay_index = last_index
    add.direction = 'AFTER'


# ---------------------------------------------------------------------------
# Cabinet-wide content (used by both sidebar parent and cabinet_prompts popup)
# ---------------------------------------------------------------------------
def draw_cabinet_wide(layout, root):
    """Cabinet-level content only - identity, dimensions, construction,
    face frame defaults, and a Bays section. Used by the cabinet_prompts
    popup. The sidebar splits these across sub-panels for collapsible
    browsing.
    """
    cab_props = root.face_frame_cabinet
    draw_identity(layout, root)
    layout.separator()
    box = layout.box()
    box.label(text="Dimensions", icon='ARROW_LEFTRIGHT')
    draw_dimensions(box, root)
    box = layout.box()
    box.label(text="Construction", icon='MODIFIER')
    draw_construction(box, cab_props)
    draw_refrigerator_options(layout, root)
    box = layout.box()
    box.label(text="Face Frame Defaults", icon='MESH_GRID')
    draw_face_frame_defaults(box, cab_props)
    draw_bays_in_prompts(layout, root)


# ---------------------------------------------------------------------------
# Parent panel - identity + recalc
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_active_cabinet(bpy.types.Panel):
    """Top-level face frame cabinet panel. Sub-panels register as children."""
    bl_label = "Face Frame Cabinet"
    bl_idname = "HB_FACE_FRAME_PT_active_cabinet"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_order = 11

    @classmethod
    def poll(cls, context):
        return types_face_frame.find_cabinet_root(context.active_object) is not None

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        layout = self.layout
        draw_identity(layout, root)


# ---------------------------------------------------------------------------
# Sub-panels
# ---------------------------------------------------------------------------
class HB_FACE_FRAME_PT_dimensions(bpy.types.Panel):
    bl_label = "Dimensions"
    bl_idname = "HB_FACE_FRAME_PT_dimensions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    @classmethod
    def poll(cls, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        return (root is not None and not root.get('IS_LEG_PRODUCT')
                and not root.get('IS_FLOATING_SHELF'))

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_dimensions(self.layout, root)


class HB_FACE_FRAME_PT_construction(bpy.types.Panel):
    bl_label = "Construction"
    bl_idname = "HB_FACE_FRAME_PT_construction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        return (root is not None and not root.get('IS_LEG_PRODUCT')
                and not root.get('IS_FLOATING_SHELF'))

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_construction(self.layout, root.face_frame_cabinet)
        draw_refrigerator_options(self.layout, root)
        draw_wedge(self.layout, root)


class HB_FACE_FRAME_PT_face_frame_defaults(bpy.types.Panel):
    bl_label = "Face Frame Defaults"
    bl_idname = "HB_FACE_FRAME_PT_face_frame_defaults"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        return (root is not None and not root.get('IS_LEG_PRODUCT')
                and not root.get('IS_FLOATING_SHELF'))

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_face_frame_defaults(self.layout, root.face_frame_cabinet)


class HB_FACE_FRAME_PT_selection(bpy.types.Panel):
    """Dynamic content based on active object - shown only when something
    specific is selected (a bay, mid stile, end stile, or rail)."""
    bl_label = "Selection"
    bl_idname = "HB_FACE_FRAME_PT_selection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    @classmethod
    def poll(cls, context):
        kind = find_active_selection(context)[0]
        return kind in ('bay', 'opening', 'interior_region',
                        'mid_stile', 'end_stile', 'rail')

    def draw(self, context):
        sel = find_active_selection(context)
        kind = sel[0]
        if kind == 'bay':
            draw_bay_properties(self.layout, sel[1])
        elif kind == 'opening':
            draw_opening_properties(self.layout, sel[1])
        elif kind == 'interior_region':
            draw_interior_region_properties(self.layout, sel[1], sel[2])
        elif kind == 'mid_stile':
            draw_mid_stile_properties(self.layout, sel[3], sel[2])
        elif kind == 'end_stile':
            draw_end_stile_properties(self.layout, sel[3], sel[2])
        elif kind == 'rail':
            draw_rail_properties(self.layout, sel[3], sel[1], sel[2])


class HB_FACE_FRAME_PT_all_bays(bpy.types.Panel):
    bl_label = "All Bays"
    bl_idname = "HB_FACE_FRAME_PT_all_bays"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        return (root is not None and not root.get('IS_LEG_PRODUCT')
                and not root.get('IS_FLOATING_SHELF'))

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_all_bays_summary(self.layout, root)


class HB_FACE_FRAME_PT_floating_shelf(bpy.types.Panel):
    """Floating shelf options. Shown only when the active object is a
    floating shelf; the bay/construction sub-panels are hidden for it."""
    bl_label = "Floating Shelf"
    bl_idname = "HB_FACE_FRAME_PT_floating_shelf"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    @classmethod
    def poll(cls, context):
        return _is_floating_shelf(context.active_object)

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_floating_shelf(self.layout, root)


class HB_FACE_FRAME_PT_leg_product(bpy.types.Panel):
    """Leg product options. Shown only when the active object is a leg;
    the bay/construction sub-panels are hidden for legs (they have no
    bays). Mirrors the right-click "Leg Properties..." popup."""
    bl_label = "Leg Product"
    bl_idname = "HB_FACE_FRAME_PT_leg_product"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"

    @classmethod
    def poll(cls, context):
        return _is_leg_product(context.active_object)

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_leg_product(self.layout, root)


classes = (
    HB_FACE_FRAME_PT_active_cabinet,
    HB_FACE_FRAME_PT_leg_product,
    HB_FACE_FRAME_PT_floating_shelf,
    HB_FACE_FRAME_PT_dimensions,
    HB_FACE_FRAME_PT_construction,
    HB_FACE_FRAME_PT_face_frame_defaults,
    HB_FACE_FRAME_PT_selection,
    HB_FACE_FRAME_PT_all_bays,
)


register, unregister = bpy.utils.register_classes_factory(classes)
