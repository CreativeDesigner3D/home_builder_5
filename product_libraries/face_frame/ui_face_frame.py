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
        col.separator()
        col.label(text="Pie Cut Options")
        col.prop(cab_props, 'exterior_option',  text="Exterior")
        col.prop(cab_props, 'interior_option',  text="Interior")
        col.prop(cab_props, 'tray_compartment', text="Tray Compartment")
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


def draw_construction(layout, cab_props):
    """Toe kick (if applicable). Panel roots have no carcass - the
    section collapses to just the finished-ends block (which itself
    is irrelevant for panels but harmless to leave visible)."""
    if cab_props.cabinet_type == 'PANEL':
        layout.label(text="No carcass - face frame only", icon='INFO')
        return

    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Toe Kick")
        col.prop(cab_props, 'toe_kick_type', text="Type")
        col.prop(cab_props, 'toe_kick_height', text="Height")
        col.prop(cab_props, 'toe_kick_setback', text="Setback")
        col.prop(cab_props, 'inset_toe_kick_left', text="Left Inset")
        col.prop(cab_props, 'inset_toe_kick_right', text="Right Inset")
        col.prop(cab_props, 'include_finish_toe_kick', text="Finish Toe Kick")

    box = layout.box()
    box.label(text="End Stile Types")
    draw_blind_corners(box, cab_props)

    box = layout.box()
    box.label(text="Finished Ends and Backs")
    draw_finished_ends(box, cab_props)


def draw_face_frame_defaults(layout, cab_props):
    """Default stile and rail widths + per-side overlay defaults.
    Per-opening overrides live on each opening object."""
    col = layout.column(align=True)
    col.prop(cab_props, 'left_stile_width', text="Left Stile")
    col.prop(cab_props, 'right_stile_width', text="Right Stile")
    if cab_props.cabinet_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.prop(cab_props, 'extend_left_stile_to_floor', text="Left Stile to Floor")
        col.prop(cab_props, 'extend_right_stile_to_floor', text="Right Stile to Floor")
    col.separator()
    col.prop(cab_props, 'left_scribe', text="Left Scribe")
    col.prop(cab_props, 'right_scribe', text="Right Scribe")
    col.prop(cab_props, 'top_scribe', text="Top Scribe")
    col.separator()
    col.prop(cab_props, 'top_rail_width', text="Top Rail")
    col.prop(cab_props, 'bottom_rail_width', text="Bottom Rail")
    col.separator()
    col.label(text="Default Overlays")
    col.prop(cab_props, 'default_top_overlay', text="Top")
    col.prop(cab_props, 'default_bottom_overlay', text="Bottom")
    col.prop(cab_props, 'default_left_overlay', text="Left")
    col.prop(cab_props, 'default_right_overlay', text="Right")


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
    col.separator()
    col.prop(bp, 'top_rail_width', text="Top Rail Width")
    col.prop(bp, 'bottom_rail_width', text="Bottom Rail Width")
    col.separator()
    col.prop(bp, 'remove_bottom', text="Remove Bottom")
    col.prop(bp, 'remove_carcass', text="Remove Carcass")
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.prop(bp, 'floating_bay', text="Floating")


def draw_opening_properties(layout, opening_obj):
    """All editable properties of a single opening: front type, hinge
    side, and the four per-side overlays. Each overlay row has an
    unlock toggle (off = use cabinet default, on = use this opening's
    own value) and an overlay field that's only enabled when unlocked.
    """
    op = opening_obj.face_frame_opening
    layout.label(text=f"Opening {op.opening_index + 1}", icon='MESH_PLANE')
    col = layout.column(align=True)

    # Size + unlock - meaningful when the opening is a child of a split
    # node. For the bay's root opening this still shows but is ignored
    # by the redistributor (root fills the bay).
    size_row = col.row(align=True)
    field = size_row.row(align=True)
    field.enabled = op.unlock_size
    field.prop(op, 'size', text="Size")
    lock_icon = 'UNLOCKED' if op.unlock_size else 'LOCKED'
    size_row.prop(op, 'unlock_size', text="", icon=lock_icon)
    col.separator()

    col.prop(op, 'front_type', text="Front Type")
    if op.front_type in ('DOOR', 'PULLOUT'):
        col.prop(op, 'hinge_side', text="Hinge Side")
    # INSET_PANEL has no motion - skip the swing slider for it (and
    # NONE which has no front to animate).
    if op.front_type not in ('NONE', 'INSET_PANEL'):
        col.prop(op, 'swing_percent', text="Open", slider=True)
    col.separator()
    col.label(text="Overlays")
    for side in ('top', 'bottom', 'left', 'right'):
        unlocked = getattr(op, f'unlock_{side}_overlay')
        row = col.row(align=True)
        field = row.row(align=True)
        field.enabled = unlocked
        field.prop(op, f'{side}_overlay', text=side.capitalize())
        lock_icon = 'UNLOCKED' if unlocked else 'LOCKED'
        row.prop(op, f'unlock_{side}_overlay', text="", icon=lock_icon)

    # Interior Items: hidden for panel roots - panels never have
    # interior objects (no carcass to hold them). Walk up to the root
    # to read the cabinet_type; opening -> bay -> root.
    root = types_face_frame.find_cabinet_root(opening_obj)
    if root is not None and root.face_frame_cabinet.cabinet_type == 'PANEL':
        return

    layout.separator()
    layout.label(text="Interior Items")

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
        _draw_interior_items_section(layout, op)
        return

    _draw_interior_tree_inline(layout, opening_obj)


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
        elif item.kind in {'PULLOUT_SHELF', 'ROLLOUT'}:
            qty_row = sub.row(align=True)
            field = qty_row.row(align=True)
            field.enabled = item.unlock_qty
            field.prop(item, 'qty', text="Qty")
            lock_icon = 'UNLOCKED' if item.unlock_qty else 'LOCKED'
            qty_row.prop(item, 'unlock_qty', text="", icon=lock_icon)
            if item.kind == 'PULLOUT_SHELF':
                sub.prop(item, 'pullout_thickness', text="Thickness")
            else:
                sub.prop(item, 'rollout_height', text="Box Height")
            sub.prop(item, 'distance_between', text="Gap Between")
            sub.prop(item, 'bottom_gap', text="Bottom Gap")
            sub.prop(item, 'item_setback', text="Front Setback")
            sub.prop(item, 'spacer_height', text="Spacer Width")
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

    size_row = col.row(align=True)
    field = size_row.row(align=True)
    field.enabled = rp.unlock_size
    field.prop(rp, 'size', text="Region Size")
    lock_icon = 'UNLOCKED' if rp.unlock_size else 'LOCKED'
    size_row.prop(rp, 'unlock_size', text="", icon=lock_icon)

    remove_label = ("Remove Fixed Shelf" if sp.axis == 'H'
                    else "Remove Division")
    col.operator(
        "hb_face_frame.remove_interior_split",
        text=remove_label, icon='X',
    )

    layout.separator()
    layout.label(text="Interior Items")
    _draw_interior_items_section(layout, rp)


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
    layout.prop(bp, attr, text="Width")


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
    """Per-cabinet finished ends + exposed flags.

    One row per side (Left / Right / Back): label, exposed toggle, type
    dropdown, and a context field that only appears when relevant -
    scribe when type is UNFINISHED (left/right), flush-X amount when
    type is FLUSH_X (left/right). Back has neither. Lives in the
    Construction section so the active cabinet's finish state stays
    visible alongside the rest of the carcass settings.
    """
    col = layout.column(align=True)
    for side, label, has_flush_x in (
        ('left', 'Left', True),
        ('right', 'Right', True),
        ('back', 'Back', False),
    ):
        row = col.row(align=True)
        row.label(text=label)
        row.prop(cab_props, f'{side}_exposed', text="")
        row.prop(cab_props, f'{side}_finished_end_condition', text="")
        fin_type = getattr(cab_props, f'{side}_finished_end_condition')
        if has_flush_x and fin_type == 'FLUSH_X':
            row.prop(cab_props, f'{side}_flush_x_amount', text="")
        elif fin_type == 'UNFINISHED' and side != 'back':
            row.prop(cab_props, f'{side}_scribe', text="")


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
    col.separator()
    col.prop(bp, 'top_rail_width', text="Top Rail Width")
    col.prop(bp, 'bottom_rail_width', text="Bottom Rail Width")
    col.separator()
    col.prop(bp, 'remove_bottom', text="Remove Bottom")
    col.prop(bp, 'remove_carcass', text="Remove Carcass")
    if cab_type in ('BASE', 'TALL', 'LAP_DRAWER'):
        col.prop(bp, 'floating_bay', text="Floating")


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

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_construction(self.layout, root.face_frame_cabinet)


class HB_FACE_FRAME_PT_face_frame_defaults(bpy.types.Panel):
    bl_label = "Face Frame Defaults"
    bl_idname = "HB_FACE_FRAME_PT_face_frame_defaults"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Home Builder"
    bl_parent_id = "HB_FACE_FRAME_PT_active_cabinet"
    bl_options = {'DEFAULT_CLOSED'}

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

    def draw(self, context):
        root = types_face_frame.find_cabinet_root(context.active_object)
        if root is None:
            return
        draw_all_bays_summary(self.layout, root)


classes = (
    HB_FACE_FRAME_PT_active_cabinet,
    HB_FACE_FRAME_PT_dimensions,
    HB_FACE_FRAME_PT_construction,
    HB_FACE_FRAME_PT_face_frame_defaults,
    HB_FACE_FRAME_PT_selection,
    HB_FACE_FRAME_PT_all_bays,
)


register, unregister = bpy.utils.register_classes_factory(classes)
