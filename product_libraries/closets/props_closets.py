"""Closet library properties.

One typed group per level of the product tree, each attached to the cage
object for that level, so every setting has one declared home, one
declared default and one declared range:
- Closets_Scene_Props (Scene.hb_closets): library defaults + library UI.
- Closet_Starter_Props (Object.hb_closet_starter): live dimensions and
  starter-level options on each starter root cage.
- Closet_Bay_Props (Object.hb_closet_bay): per-bay overrides on each bay
  cage (width/lock, height, depth, floor-mounted, remove flags).
- Closet_Opening_Props (Object.hb_closet_opening): what fills each
  opening (shelves, drawers, cubbies, trays, shoe shelves, front).

No drivers: every update callback routes through
types_closets.recalculate_closet_starter, which is guarded against
reentry (system writes during a recalc don't loop back here).
"""
import bpy
import math
from bpy.types import PropertyGroup
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        EnumProperty,
        )

import os

from . import const_closets as const
from . import starter_presets
from . import materials_closets
from . import pulls_closets
from . import drawer_boxes_closets
from . import fronts_closets
from . import molding_closets
from ... import units


# ---------------------------------------------------------------------------
# Thumbnail previews (mirrors face_frame's preview-collection pattern)
# ---------------------------------------------------------------------------
preview_collections = {}


def get_starter_previews():
    if "starter_previews" not in preview_collections:
        import bpy.utils.previews
        preview_collections["starter_previews"] = bpy.utils.previews.new()
    return preview_collections["starter_previews"]


def get_thumbnail_path():
    return os.path.join(os.path.dirname(__file__), "closet_thumbnails")


def load_starter_thumbnail(name):
    """Icon id for a starter thumbnail (closet_thumbnails/<name>.png),
    or 0 when no render exists yet - callers fall back to a text button."""
    pcoll = get_starter_previews()
    if name in pcoll:
        return pcoll[name].icon_id
    path = os.path.join(get_thumbnail_path(), f"{name}.png")
    if os.path.exists(path):
        return pcoll.load(name, path, 'IMAGE').icon_id
    return 0


# ---------------------------------------------------------------------------
# Update callbacks
# ---------------------------------------------------------------------------
def _update_starter_prop(self, context):
    """Starter-level prop changed: recalc that starter. Lazy import so
    module load order can't create a cycle."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_kick_preset(self, context):
    """Toe-kick height dropdown changed: set the distance to the chosen
    standard height (the key is millimetres), then recalc. 'CUSTOM'
    leaves the typed distance alone. The distance carries a recalc of
    its own, so the pair is held to one solve."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.toe_kick_height_preset != 'CUSTOM':
            self.toe_kick_height = const.millimeter(
                int(self.toe_kick_height_preset))
        _update_starter_prop(self, context)


def _update_height_preset(self, context):
    """Section-height dropdown changed: set the distance to the chosen
    standard height (the key is millimetres). 'CUSTOM' leaves the typed
    distance alone. Held to one solve - the distance recalcs too."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.height_preset != 'CUSTOM':
            self.height = const.millimeter(int(self.height_preset))
        _update_starter_prop(self, context)


def _update_bay_prop(self, context):
    """Bay-level prop changed - a size the bay owns, one of the padlocks
    that hands it a size, or a construction flag. Recalcs the run; the
    call is a no-op while that run is already solving, so the seeding
    passes that write these props in bulk cost nothing."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_bay_height_preset(self, context):
    """Bay height dropdown changed (the key is millimetres). Held to
    one solve - the distance and the padlock both recalc."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.height_preset != 'CUSTOM':
            self.height = const.millimeter(int(self.height_preset))
        _update_bay_height(self, context)


def _bay_edit_root(bay_props):
    """The starter a bay belongs to, or None when the write came from
    the system rather than from someone typing in the dialog. Layout
    writes its own values back to the bays, and those must not read as
    edits - otherwise every bay would lock itself the first time the
    run was solved."""
    from . import types_closets
    root = types_closets.find_starter_root(bay_props.id_data)
    if root is None:
        return None
    root_id = id(root)
    if (root_id in types_closets._RECALCULATING
            or root_id in types_closets._DISTRIBUTING_WIDTHS):
        return None
    return root


def _update_bay_width(self, context):
    """Bay width changed. The first edit hands the bay its own width so
    the value holds while the remaining widths are redistributed. That
    flag carries a recalc of its own, so only a later nudge - the bay
    already owning its width - has to ask for one here."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    if not self.unlock_width:
        self.unlock_width = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_bay_height(self, context):
    """Bay height changed. Same idea as the width: a height typed here
    hands the bay its own, so it keeps it when the run height changes.
    Clear the padlock to put the bay back on the run height."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    if not self.unlock_height:
        self.unlock_height = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_bay_depth(self, context):
    """Bay depth changed - hands the bay its own depth, as above."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    if not self.unlock_depth:
        self.unlock_depth = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_closet_selection_mode(self, context):
    """Apply visibility highlighting for the active closet selection
    mode (mirrors face_frame's update_face_frame_selection_mode)."""
    bpy.ops.hb_closets.toggle_mode(search_obj_name="")


def _update_countertop_mode(self, context):
    """Switching the tops between a countertop material and the closet
    material changes what they are made of, so it changes how thick
    they are too. Every top in the room follows, the same way the
    material selections do - a thickness typed on one starter is a
    setting for that material, not a size to carry across."""
    from . import types_closets
    scene = getattr(context, 'scene', None) or bpy.context.scene
    thickness = (self.shelf_thickness
                 if self.use_closet_material_for_countertops
                 else self.countertop_thickness)
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            sp = obj.hb_closet_starter
            if abs(sp.countertop_thickness - thickness) > 1e-9:
                # Assigning re-runs the starter, which is what puts the
                # new thickness on the part.
                sp.countertop_thickness = thickness
    materials_closets.update_room(self, context)


# ---------------------------------------------------------------------------
# Object-level: starter root
# ---------------------------------------------------------------------------
class Closet_Starter_Props(PropertyGroup):

    # Which page of the properties dialog is showing. Purely UI state.
    prompt_tab: EnumProperty(
        name="Tab",
        items=[
            ('SIZES', "Sizes", "Overall size and the size of each bay"),
            ('CONSTRUCTION', "Construction",
             "Toe kick, ends, hang rail and the per-bay build options"),
            ('COUNTERTOP', "Countertop",
             "Countertop, overhangs and backsplash"),
        ],
        default='SIZES')  # type: ignore

    # Which Construction sections are open. Purely UI state - every
    # section starts closed so the page opens as a short list of headers
    # and only what is being worked on is unfolded.
    show_toe_kick: BoolProperty(
        name="Show Toe Kick", default=False)  # type: ignore
    show_ends: BoolProperty(
        name="Show Ends", default=False)  # type: ignore
    show_top: BoolProperty(
        name="Show Top", default=False)  # type: ignore
    show_hang_rail: BoolProperty(
        name="Show Hang Rail", default=False)  # type: ignore
    show_applied_back: BoolProperty(
        name="Show Applied Back", default=False)  # type: ignore
    show_insets: BoolProperty(
        name="Show Insets", default=False)  # type: ignore
    show_panels: BoolProperty(
        name="Show Panels", default=False)  # type: ignore
    show_fronts: BoolProperty(
        name="Show Fronts", default=False)  # type: ignore
    show_per_bay: BoolProperty(
        name="Show Per Bay", default=False)  # type: ignore

    width: FloatProperty(
        name="Width", description="Starter width (X)",
        default=const.DEFAULT_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    height: FloatProperty(
        name="Height", description="Panel height (Z)",
        default=const.TALL_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Panel depth (Y)",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Standard section heights (the 32mm-system lattice). Picking one
    # writes the distance above; Custom leaves whatever is typed there.
    height_preset: EnumProperty(
        name="Height",
        description="Standard section height (Custom keeps the typed "
                    "value)",
        items=const.PANEL_HEIGHT_ITEMS + [('CUSTOM', "Custom",
                                           "Use the typed height")],
        default='2131', update=_update_height_preset)  # type: ignore

    closet_type: EnumProperty(
        name="Closet Type",
        items=[
            ('BASE', "Base", "Floor-mounted base starter"),
            ('TALL', "Tall", "Floor-mounted full-height starter"),
            ('HANGING', "Hanging", "Wall-mounted hanging starter"),
            ('ISLAND', "Island", "Single-sided island starter"),
        ],
        default='BASE')  # type: ignore

    toe_kick_height_preset: EnumProperty(
        name="Toe Kick Height",
        description="Standard toe-kick height (Custom keeps the typed "
                    "value)",
        items=const.KICK_HEIGHT_ITEMS + [('CUSTOM', "Custom",
                                          "Use the typed height")],
        default='96', update=_update_kick_preset)  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height",
        description="Floor to the underside of the bottom shelf on a "
                    "floor bay",
        default=const.DEFAULT_TOE_KICK_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback",
        description="How far the kick sits back from the front of the "
                    "panels",
        default=const.DEFAULT_TOE_KICK_SETBACK, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    include_countertop: BoolProperty(
        name="Include Countertop",
        description="Lay a countertop across the top of the run",
        default=False, update=_update_starter_prop)  # type: ignore

    # Countertop shaping. The overhangs are measured past the carcass on
    # each side; finished ends and the radius option are edge treatments
    # a downstream pass consumes.
    countertop_thickness: FloatProperty(
        name="Thickness", description="Countertop material thickness",
        default=const.COUNTERTOP_THICKNESS,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_front: FloatProperty(
        name="Front", description="Countertop projection past the front "
                                  "of the carcass",
        default=const.COUNTERTOP_OVERHANG_FRONT, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    countertop_overhang_rear: FloatProperty(
        name="Rear", description="Countertop projection past the back of "
                                 "the carcass",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_left: FloatProperty(
        name="Left", description="Countertop projection past the left end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_right: FloatProperty(
        name="Right", description="Countertop projection past the right end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The countertop's left end is exposed, so it gets an "
                    "edge treatment and no side backsplash",
        default=False, update=_update_starter_prop)  # type: ignore
    countertop_right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The countertop's right end is exposed, so it gets an "
                    "edge treatment and no side backsplash",
        default=False, update=_update_starter_prop)  # type: ignore
    # Not drawn in the dialog yet - rounding an exposed countertop
    # corner needs a node group the library does not have. The
    # property stays defined so putting the row back is one line.
    countertop_radius_finished_ends: BoolProperty(
        name="Radius Finished Ends",
        description="Round the exposed countertop corners instead of "
                    "leaving them square",
        default=False, update=_update_starter_prop)  # type: ignore
    include_backsplash: BoolProperty(
        name="Include Backsplash",
        description="Add an upstand along the countertop's wall edges. "
                    "An end marked finished has no wall, so it gets no "
                    "side splash",
        default=True, update=_update_starter_prop)  # type: ignore
    backsplash_height: FloatProperty(
        name="Backsplash Height",
        description="How far the backsplash stands above the countertop",
        default=const.BACKSPLASH_HEIGHT,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Applied back: the panel closing the rear face of an island bay.
    back_to_floor: BoolProperty(
        name="Back to Floor",
        description="Run the applied back all the way down to the floor "
                    "instead of starting above the toe kick",
        default=False, update=_update_starter_prop)  # type: ignore
    applied_back_overlay: FloatProperty(
        name="Applied Back Overlay",
        description="How far the applied back laps onto the panels and "
                    "shelves around its bay",
        default=const.APPLIED_BACK_OVERLAY, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore

    # Hanging panels can run down past the bottom of their section so
    # they finish alongside the countertop of whatever sits below.
    extend_panels_to_countertop: BoolProperty(
        name="Extend Panels to Countertop",
        description="Run every hanging panel down past the bottom of its "
                    "section so it finishes alongside the countertop "
                    "below. Panels that already reach the floor are left "
                    "alone",
        default=False, update=_update_starter_prop)  # type: ignore
    extend_panel_amount: FloatProperty(
        name="Extend Panel Amount",
        description="How far past the bottom of the section an extended "
                    "panel runs",
        default=const.EXTEND_PANEL_AMOUNT,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Bridge shelves spanning the access gap to a corner neighbor. The
    # Corner Clearance command fills these in from the measured gap;
    # they can also be set by hand here.
    bridge_left: BoolProperty(
        name="Bridge Left",
        description="Span the gap past the left end with a shelf at the "
                    "corner bay's top shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    bridge_right: BoolProperty(
        name="Bridge Right",
        description="Span the gap past the right end with a shelf at the "
                    "corner bay's top shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    bridge_left_width: FloatProperty(
        name="Left Bridge Shelf Width",
        description="How far the left bridge shelf reaches past the end "
                    "of the run",
        default=const.BRIDGE_SHELF_WIDTH,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    bridge_right_width: FloatProperty(
        name="Right Bridge Shelf Width",
        description="How far the right bridge shelf reaches past the end "
                    "of the run",
        default=const.BRIDGE_SHELF_WIDTH,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    include_bottom_bridge_left: BoolProperty(
        name="Include Bottom Bridge Left",
        description="Also bridge the gap at the bottom shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    include_bottom_bridge_right: BoolProperty(
        name="Include Bottom Bridge Right",
        description="Also bridge the gap at the bottom shelf height",
        default=False, update=_update_starter_prop)  # type: ignore

    # Run-wide insets, both floor-bay only (a hanging bay has neither a
    # kick nor a bottom to set in). A bay can add its own bottom shelf
    # inset on top of the run-wide one in the bay properties.
    inset_bottom: FloatProperty(
        name="Inset Bottom",
        description="Hold every floor bay's bottom shelf off the wall by "
                    "this much (the front edge stays where it was)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    inset_cleat: FloatProperty(
        name="Inset Cleat",
        description="Raise every floor bay's cleat this far above the "
                    "bottom shelf",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # ----- Fronts -----
    # How far a door or drawer front reaches over what it meets on each
    # of its four sides. A half overlay splits what the front shares
    # with its neighbour: the two meet over the middle of the panel or
    # shelf between them and the gap is what shows. Turning a side off
    # holds the front back from that edge by the reveal instead, which
    # is how a finished end or a top is left showing. Left and right
    # work off the panel thickness and the horizontal gap, top and
    # bottom off the shelf thickness and the vertical gap. Any opening
    # can take a side over for itself.
    half_overlay_top: BoolProperty(
        name="Half Overlay Top",
        description="Share the shelf above with the front over it, "
                    "rather than holding back by the top reveal",
        default=True, update=_update_starter_prop)  # type: ignore
    half_overlay_bottom: BoolProperty(
        name="Half Overlay Bottom",
        description="Share the shelf below with the front under it, "
                    "rather than holding back by the bottom reveal",
        default=True, update=_update_starter_prop)  # type: ignore
    half_overlay_left: BoolProperty(
        name="Half Overlay Left",
        description="Share the panel on the left with the front beside "
                    "it, rather than holding back by the left reveal",
        default=True, update=_update_starter_prop)  # type: ignore
    half_overlay_right: BoolProperty(
        name="Half Overlay Right",
        description="Share the panel on the right with the front beside "
                    "it, rather than holding back by the right reveal",
        default=True, update=_update_starter_prop)  # type: ignore
    top_reveal: FloatProperty(
        name="Top Reveal",
        description="How much of the shelf above is left showing when "
                    "the top is not a half overlay",
        default=const.TOP_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    bottom_reveal: FloatProperty(
        name="Bottom Reveal",
        description="How much of the shelf below is left showing when "
                    "the bottom is not a half overlay",
        default=const.BOTTOM_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    left_reveal: FloatProperty(
        name="Left Reveal",
        description="How much of the panel on the left is left showing "
                    "when the left is not a half overlay",
        default=const.LEFT_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    right_reveal: FloatProperty(
        name="Right Reveal",
        description="How much of the panel on the right is left showing "
                    "when the right is not a half overlay",
        default=const.RIGHT_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    vertical_gap: FloatProperty(
        name="Vertical Gap",
        description="Gap between a front and the front above or below it",
        default=const.VERTICAL_GAP, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    horizontal_gap: FloatProperty(
        name="Horizontal Gap",
        description="Gap between a front and the front beside it",
        default=const.HORIZONTAL_GAP, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    door_to_cabinet_gap: FloatProperty(
        name="Door to Cabinet Gap",
        description="How far the back of a front is held off the front "
                    "edge of the closet",
        default=const.DOOR_TO_CABINET_GAP, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore

    # End options. Finished end and drill through are recorded on the
    # panel as flags - whether the end is exposed, and whether its
    # system holes run all the way through; turn-off frees the panel
    # thickness back to the openings for shared-panel runs; battens are
    # cosmetic scribe strips.
    left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The left end panel is exposed, so it gets an edge "
                    "treatment and no through drilling",
        default=False, update=_update_starter_prop)  # type: ignore
    right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The right end panel is exposed, so it gets an edge "
                    "treatment and no through drilling",
        default=False, update=_update_starter_prop)  # type: ignore
    turn_off_left_panel: BoolProperty(
        name="Turn Off Left Panel",
        description="Hide the left end panel and give its thickness to "
                    "the first bay (share a panel with the neighbor)",
        default=False, update=_update_starter_prop)  # type: ignore
    turn_off_right_panel: BoolProperty(
        name="Turn Off Right Panel",
        description="Hide the right end panel and give its thickness to "
                    "the last bay (share a panel with the neighbor)",
        default=False, update=_update_starter_prop)  # type: ignore
    drill_through_left: BoolProperty(
        name="Drill Through Left Side",
        description="Carry the shelf holes all the way through the left "
                    "end panel instead of stopping partway",
        default=False, update=_update_starter_prop)  # type: ignore
    drill_through_right: BoolProperty(
        name="Drill Through Right Side",
        description="Carry the shelf holes all the way through the right "
                    "end panel instead of stopping partway",
        default=False, update=_update_starter_prop)  # type: ignore
    include_batten_left: BoolProperty(
        name="Include Batten Left",
        description="Add a scribe strip down the inside front edge of the "
                    "left end panel",
        default=False, update=_update_starter_prop)  # type: ignore
    include_batten_right: BoolProperty(
        name="Include Batten Right",
        description="Add a scribe strip down the inside front edge of the "
                    "right end panel",
        default=False, update=_update_starter_prop)  # type: ignore

    # Top accent shelf: a decorative shelf on
    # top of the run projecting forward by the overhang, with a side
    # overhang past each finished end.
    add_top_accent_shelf: BoolProperty(
        name="Add Top Accent Shelf",
        description="Lay a decorative shelf across the top of the run",
        default=False, update=_update_starter_prop)  # type: ignore
    top_accent_overhang: FloatProperty(
        name="Top Accent Shelf Overhang",
        description="How far the accent shelf projects past the front and "
                    "past each finished end",
        default=const.TOP_ACCENT_OVERHANG, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Hang rail options.
    remove_hang_rail: BoolProperty(
        name="Remove Hang Rail",
        description="Hide the wall hang rail on every bay",
        default=False, update=_update_starter_prop)  # type: ignore
    extend_hang_rail_left: FloatProperty(
        name="Extend Hang Rail Left",
        description="Lengthen the leftmost bay's rail toward the left "
                    "wall by this much",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    extend_hang_rail_right: FloatProperty(
        name="Extend Hang Rail Right",
        description="Lengthen the rightmost bay's rail toward the right "
                    "wall by this much",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    use_one_hang_rail_height: BoolProperty(
        name="Use One Hang Rail Height",
        description="Force every bay's rail to a single height instead "
                    "of each bay's own top",
        default=False, update=_update_starter_prop)  # type: ignore
    hang_rail_height_location: FloatProperty(
        name="Hang Rail Height",
        description="Rail height above the floor when Use One Hang Rail "
                    "Height is on",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Side wall fillers: a front scribe
    # strip standing past the end of the run to close the gap to a side
    # wall. Width 0 = no filler. The prompt value is the filler width.
    left_side_wall_filler: FloatProperty(
        name="Left Side Wall Filler",
        description="Width of the scribe filler past the left end (0 = "
                    "none)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    right_side_wall_filler: FloatProperty(
        name="Right Side Wall Filler",
        description="Width of the scribe filler past the right end (0 = "
                    "none)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Corner (L-shelf) starter prompts. Only meaningful when the
    # starter class is an L-shelf variant (is_corner); the prompts
    # dialog gates on that.
    l_left_depth: FloatProperty(
        name="Left Depth", description="Left wing panel depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_right_depth: FloatProperty(
        name="Right Depth", description="Right wing panel depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_shelf_qty: IntProperty(
        name="Shelf Quantity",
        description="Interior L shelves between the bottom and top",
        default=const.L_SHELF_QTY, min=0, max=12,
        update=_update_starter_prop)  # type: ignore
    l_back_width: FloatProperty(
        name="Back Partition Width",
        description="Width of the corner back partition the L shelves "
                    "notch around",
        default=const.L_BACK_STRIP_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_flip_partition: BoolProperty(
        name="Flip Back Partition",
        description="Move the back partition from the back wall to the "
                    "side wall",
        default=False,
        update=_update_starter_prop)  # type: ignore
    l_use_radius: BoolProperty(
        name="Radius Front Corner",
        description="Round the inside front corner of the L shelves "
                    "instead of cutting it square",
        default=True,
        update=_update_starter_prop)  # type: ignore
    l_corner_radius: FloatProperty(
        name="Corner Radius",
        description="Radius of the rounded inside front corner",
        default=const.L_CORNER_RADIUS, min=0.0, unit='LENGTH',
        precision=4,
        update=_update_starter_prop)  # type: ignore


# ---------------------------------------------------------------------------
# Object-level: bay
# ---------------------------------------------------------------------------
class Closet_Bay_Props(PropertyGroup):

    bay_index: IntProperty(name="Bay Index", default=0)  # type: ignore

    width: FloatProperty(
        name="Width", description="Bay opening width",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_bay_width)  # type: ignore
    unlock_width: BoolProperty(
        name="Unlock Width",
        description="Give this bay its own width, held while the rest "
                    "of the run is redistributed to fill the run width",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_width'],
        update=_update_bay_prop)  # type: ignore

    height: FloatProperty(
        name="Height", description="Bay height (envelope, floor to top shelf)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_bay_height)  # type: ignore
    unlock_height: BoolProperty(
        name="Unlock Height",
        description="Give this bay its own height instead of following "
                    "the run height",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_height'],
        update=_update_bay_prop)  # type: ignore
    height_preset: EnumProperty(
        name="Height",
        description="Standard section height (Custom keeps the typed "
                    "value)",
        items=const.PANEL_HEIGHT_ITEMS + [('CUSTOM', "Custom",
                                           "Use the typed height")],
        default='2131', update=_update_bay_height_preset)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Bay depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_bay_depth)  # type: ignore
    unlock_depth: BoolProperty(
        name="Unlock Depth",
        description="Give this bay its own depth instead of following "
                    "the run depth",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_depth'],
        update=_update_bay_prop)  # type: ignore

    floor_mounted: BoolProperty(
        name="Floor Mounted",
        description="Bay sits on the floor with a toe kick; off = the bay "
                    "hangs from its top height (top and bottom fixed shelves)",
        default=True, update=_update_bay_prop)  # type: ignore
    remove_bottom: BoolProperty(
        name="Remove Bottom",
        description="Leave this bay's fixed bottom shelf out. On a floor "
                    "bay the toe kick goes with it and the bay opens all "
                    "the way to the floor; on a hanging bay it opens to "
                    "the hang line",
        default=starter_presets.BAY_PROP_DEFAULTS['remove_bottom'],
        update=_update_bay_prop)  # type: ignore
    remove_cleat: BoolProperty(
        name="Remove Cleat",
        description="Leave this bay's wall cleat out",
        default=starter_presets.BAY_PROP_DEFAULTS['remove_cleat'],
        update=_update_bay_prop)  # type: ignore
    bottom_shelf_inset: FloatProperty(
        name="Bottom Shelf Inset",
        description="Hold this bay's bottom shelf off the wall by this "
                    "much on top of the run-wide Inset Bottom",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore
    # Numbered the way the prior library numbered it: the checkbox for a
    # doubled junction belongs to the bay on its LEFT, so a four bay run
    # offers Double Panel 1, 2 and 3 for its three shared partitions.
    double_panel_right: BoolProperty(
        name="Double Panel",
        description="Add a second partition at the junction on this bay's "
                    "right, so this bay and its right neighbor each get "
                    "their own panel",
        default=False, update=_update_bay_prop)  # type: ignore

    # Double-sided islands only: the divider between the two faces.
    include_center_back: BoolProperty(
        name="Center Back",
        description="Close this bay's two faces off from each other with "
                    "a divider panel",
        default=True, update=_update_bay_prop)  # type: ignore
    center_back_location: FloatProperty(
        name="Center Back Location",
        description="How far in from the island's back face the divider "
                    "sits. Leave at 0 to keep it centered",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore

    # ----- Bay-wide front -----
    # A front that spans the whole bay rather than one opening. Held as a
    # string for the same reason the opening's front is: an empty value
    # has to be tellable from a choice, and empty means no bay-wide
    # front at all.
    door_swing: bpy.props.StringProperty(
        name="Door",
        description="Front spanning the whole bay: LEFT, RIGHT, DOUBLE "
                    "or LIFT_UP. Empty leaves the bay's openings to "
                    "carry their own fronts",
        default='', update=_update_bay_prop)  # type: ignore
    is_hamper: BoolProperty(
        name="Tilt Out Hamper",
        description="Hang the bay-wide front on a tilt-out hamper with a "
                    "wire basket behind it instead of a plain door",
        default=False, update=_update_bay_prop)  # type: ignore


# ---------------------------------------------------------------------------
# Object-level: opening
# ---------------------------------------------------------------------------
class Closet_Opening_Props(PropertyGroup):
    """What fills one opening, on that opening's cage object.

    Every default here is the EMPTY state, not the state the Change
    Opening dialog offers when you pick an interior. An untouched opening
    reads zero shelves, zero drawers, one cubby column, no front - which
    is what an untouched opening is. The dialog carries its own starting
    numbers (three shelves, three drawers, and so on) and only writes them
    here once the user accepts them.

    Deliberately no update callbacks. An opening is edited through the
    Change Opening dialog, which writes the whole set at once and then
    recalculates the run a single time. Callbacks here would fire a full
    recalculation per field written.
    """

    # Note on what is NOT here: which face of a double-sided island an
    # opening serves stays a plain idprop (hb_opening_side). It is stamped
    # on splitting shelves as well as on openings, so it is a tag the
    # whole tree is sorted by rather than a setting one opening owns.

    # ----- Adjustable shelves -----
    adj_shelf_qty: IntProperty(
        name="Shelf Quantity",
        description="How many adjustable shelves to space through the "
                    "opening",
        default=0, min=0, max=20)  # type: ignore
    # How the shelves in this opening are cut. Both figures are the
    # room's until this opening takes one over, which is what the
    # unlock flags say. They describe how a shelf is made rather than
    # what is in the opening, so like the overlays they are
    # deliberately not contents: stripping an opening empties it
    # without losing the way its shelves were cut.
    unlock_shelf_clip_gap: BoolProperty(
        name="Clip Gap",
        description="Set this opening's shelf clip gap here instead "
                    "of following the room",
        default=False)  # type: ignore
    shelf_clip_gap: FloatProperty(
        name="Clip Gap",
        description="How much narrower than the opening each shelf is "
                    "cut, per side, so it drops onto its clips",
        default=const.SHELF_CLIP_GAP,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    unlock_shelf_setback: BoolProperty(
        name="Setback",
        description="Set this opening's shelf setback here instead of "
                    "following the room",
        default=False)  # type: ignore
    shelf_setback: FloatProperty(
        name="Setback",
        description="How far back from the front edge of the opening "
                    "each shelf stops",
        default=const.SHELF_SETBACK,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    # ----- Drawers -----
    drawer_qty: IntProperty(
        name="Drawer Quantity",
        description="How many drawers to stack in the opening",
        default=0, min=0, max=10)  # type: ignore
    drawer_front_height: FloatProperty(
        name="Front Height",
        description="Height of each drawer front. The top drawer takes up "
                    "whatever height is left over",
        default=const.DRAWER_FRONT_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    # Held as a plain string rather than an enum so an opening keeps a box
    # system that is not in the current list, and so an empty value can
    # mean "no override" alongside the explicit 'DEFAULT'.
    drawer_box_override: bpy.props.StringProperty(
        name="Drawer Box",
        description="Which drawer box to build instead of the one the "
                    "opening size would pick on its own. Empty or DEFAULT "
                    "defers to the scene setting",
        default='')  # type: ignore

    # ----- Pull-out trays -----
    rollout_qty: IntProperty(
        name="Rollout Quantity",
        description="How many pull-out trays to space through the opening",
        default=0, min=0, max=12)  # type: ignore
    rollout_height: FloatProperty(
        name="Rollout Height", description="Height of each tray",
        default=const.ROLLOUT_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Slanted shoe shelves -----
    slant_qty: IntProperty(
        name="Shoe Shelf Quantity",
        description="How many slanted shoe shelves to stack from the "
                    "bottom of the opening up",
        default=0, min=0, max=10)  # type: ignore
    slant_spacing: FloatProperty(
        name="Distance Between Shelves",
        description="Vertical spacing from one shoe shelf to the next",
        default=const.SLANT_SHELF_SPACING,
        unit='LENGTH', precision=4)  # type: ignore
    slant_angle: FloatProperty(
        name="Shelf Angle",
        description="How far the shoe shelves tilt up toward the front",
        # A shoe shelf that is not tilted is just a shelf, so the standard
        # tilt is the default rather than zero. An opening with no shoe
        # shelves in it still reports this angle; nothing reads it until
        # the shelf quantity goes above zero.
        default=math.radians(const.SLANT_SHELF_ANGLE_DEG),
        subtype='ANGLE', unit='ROTATION')  # type: ignore
    slant_color: bpy.props.StringProperty(
        name="Fence Color",
        description="Finish of the metal shoe fence across the front of "
                    "each shelf",
        default='')  # type: ignore

    # ----- Cubbies -----
    # One column by one row is "no cubbies"; the regenerator only builds
    # divisions once either count goes above one.
    cubby_cols: IntProperty(
        name="Columns", description="How many cubbies across the opening",
        default=1, min=1, max=12)  # type: ignore
    cubby_rows: IntProperty(
        name="Rows", description="How many cubbies up the opening",
        default=1, min=1, max=12)  # type: ignore
    cubby_setback: FloatProperty(
        name="Setback",
        description="How far the cubby divisions and shelves sit back "
                    "from the front edge of the opening",
        default=const.CUBBY_SETBACK,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    # ----- Front -----
    # Empty means no front. Held as a string for the same reason as the
    # box override: an empty value has to be distinguishable from a choice.
    door_swing: bpy.props.StringProperty(
        name="Door",
        description="Front on this opening: LEFT, RIGHT, DOUBLE or "
                    "LIFT_UP. Empty leaves the opening open",
        default='')  # type: ignore
    is_hamper: BoolProperty(
        name="Tilt Out Hamper",
        description="Hang the front on a tilt-out hamper with a wire "
                    "basket behind it instead of a plain door",
        default=False)  # type: ignore

    # ----- Hang rod -----
    # One opening's worth of rod settings. How far the rod stands off the
    # wall, how much shorter than the opening it is cut, and whether it
    # is shown hung. They sit on the opening rather than on the rod for
    # the same reason every other setting does: the opening is the cage
    # the user edits, and the rod under it is placed by the solve.
    rod_set_from_front: BoolProperty(
        name="Set Distance From Front",
        description="Measure the rod front to back from the front edge of "
                    "the opening instead of from the back",
        default=False)  # type: ignore
    rod_from_front: FloatProperty(
        name="Dim From Front",
        description="How far back from the front edge of the opening the "
                    "rod's centerline sits",
        default=const.ROD_FROM_FRONT,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_from_rear: FloatProperty(
        name="Dim From Rear",
        description="How far out from the back of the opening the rod's "
                    "centerline sits",
        default=const.ROD_FROM_REAR,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_width_deduction: FloatProperty(
        name="Width Deduction",
        description="How much shorter than the opening the rod is cut, so "
                    "it drops into the cups at each end",
        default=const.ROD_WIDTH_DEDUCTION,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    remove_hangers: BoolProperty(
        name="Remove Hangers",
        description="Leave the display hangers off the rods in this "
                    "opening",
        default=False)  # type: ignore

    # ----- Front overlays -----
    # Per-side overrides of what the run works out. Unlocking a side
    # lets this opening's front reach further over, or hold further
    # back from, whatever it meets there - the opening against a
    # finished end, say, where the run's half overlay would run the
    # front off the edge. A side left locked follows the run.
    #
    # These say how a front sits rather than what is in the opening, so
    # they are deliberately not contents: stripping an opening empties
    # it without losing the way its front was set up.
    top_overlay: FloatProperty(
        name="Top Overlay",
        description="How far this opening's front reaches over the shelf "
                    "above it",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    bottom_overlay: FloatProperty(
        name="Bottom Overlay",
        description="How far this opening's front reaches over the shelf "
                    "below it",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    left_overlay: FloatProperty(
        name="Left Overlay",
        description="How far this opening's front reaches over the panel "
                    "on its left",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    right_overlay: FloatProperty(
        name="Right Overlay",
        description="How far this opening's front reaches over the panel "
                    "on its right",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    unlock_top_overlay: BoolProperty(
        name="Unlock Top Overlay",
        description="Use this opening's own top overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore
    unlock_bottom_overlay: BoolProperty(
        name="Unlock Bottom Overlay",
        description="Use this opening's own bottom overlay instead of "
                    "the one the run works out",
        default=False)  # type: ignore
    unlock_left_overlay: BoolProperty(
        name="Unlock Left Overlay",
        description="Use this opening's own left overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore
    unlock_right_overlay: BoolProperty(
        name="Unlock Right Overlay",
        description="Use this opening's own right overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore

    # How the pulls sit on this opening's fronts. The room's Options
    # tab sets what every opening starts from; unlocking a setting keeps
    # it to this opening, which is how one bank of wide drawers ends up
    # with a pair of pulls apiece while the rest of the run stays
    # single. Left out of the contents list below on purpose: stripping
    # an opening empties it, it does not re-hardware the job.
    no_pulls: BoolProperty(
        name="No Pulls",
        description="Draw this opening's fronts without pulls",
        default=False)  # type: ignore
    unlock_center_pull: BoolProperty(
        name="Centered",
        description="Say here whether this opening's drawer pulls are "
                    "centered, instead of following the room",
        default=False)  # type: ignore
    center_pull_on_front: BoolProperty(
        name="Center Pull On Front",
        description="Center the pull on the height of the drawer front",
        default=True)  # type: ignore
    unlock_pull_location: BoolProperty(
        name="From Top",
        description="Set how far down this opening's drawer pulls sit, "
                    "instead of following the room",
        default=False)  # type: ignore
    drawer_pull_vertical_location: FloatProperty(
        name="Drawer Pull Vertical Location",
        description="Top of the drawer front to the middle of the pull",
        default=const.DRAWER_PULL_VERTICAL_LOCATION,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    double_pull_on_front: BoolProperty(
        name="Double Pull On Front",
        description="Put two pulls on each of this opening's drawer "
                    "fronts instead of one",
        default=False)  # type: ignore
    distance_between_pulls: FloatProperty(
        name="Distance Between Pulls",
        description="Middle to middle of the two pulls on a front",
        default=const.DISTANCE_BETWEEN_PULLS,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    # Which way the grain runs on this opening's fronts. Locked,
    # they follow the room's settings for doors and for drawer fronts;
    # unlocked, everything on this opening runs the way it is set here.
    # Left out of the contents list below on purpose, same as the
    # overlays and the pulls: stripping an opening empties it, it does
    # not re-finish it.
    unlock_grain: BoolProperty(
        name="Grain",
        description="Set which way the grain runs on this opening's "
                    "fronts, instead of following the room",
        default=False)  # type: ignore
    grain_direction: EnumProperty(
        name="Grain Direction",
        description="Which way the grain runs on this opening's fronts",
        items=materials_closets.GRAIN_ITEMS,
        default='VERTICAL')  # type: ignore

    # Every field on this group is contents, so stripping an opening
    # clears the lot. Kept as an explicit list so a field added later has
    # to be considered rather than silently surviving a clear.
    CONTENTS_FIELDS = (
        'adj_shelf_qty',
        'drawer_qty', 'drawer_front_height', 'drawer_box_override',
        'rollout_qty', 'rollout_height',
        'slant_qty', 'slant_spacing', 'slant_angle', 'slant_color',
        'cubby_cols', 'cubby_rows', 'cubby_setback',
        'door_swing', 'is_hamper',
        'rod_set_from_front', 'rod_from_front', 'rod_from_rear',
        'rod_width_deduction', 'remove_hangers',
    )

    def clear_contents(self):
        """Put every field back to its empty default."""
        for name in self.CONTENTS_FIELDS:
            self.property_unset(name)


# ---------------------------------------------------------------------------
# Scene-level: defaults + library UI
# ---------------------------------------------------------------------------
class Closets_Scene_Props(PropertyGroup):

    # ----- Defaults (seed new starters; existing starters keep their values) -----
    default_closet_width: FloatProperty(
        name="Default Width", default=const.DEFAULT_WIDTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_panel_depth: FloatProperty(
        name="Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    # Per-type panel depths. Seeded onto a new starter by
    # its closet type; default_panel_depth is the fallback.
    default_base_panel_depth: FloatProperty(
        name="Base Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_tall_panel_depth: FloatProperty(
        name="Tall Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_hanging_panel_depth: FloatProperty(
        name="Hanging Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_corner_closet_size: FloatProperty(
        name="Corner Closet Size", default=const.L_SHELF_SIZE,
        unit='LENGTH', precision=4)  # type: ignore
    default_accent_overhang: FloatProperty(
        name="Accent Shelf Overhang", default=const.TOP_ACCENT_OVERHANG,
        unit='LENGTH', precision=4)  # type: ignore
    base_panel_height: FloatProperty(
        name="Base Panel Height", default=const.BASE_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    tall_panel_height: FloatProperty(
        name="Tall Panel Height", default=const.TALL_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    hanging_panel_height: FloatProperty(
        name="Hanging Panel Height", default=const.HANGING_PANEL_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    hanging_top_height: FloatProperty(
        name="Hanging Top Height",
        description="Floor to the top of wall-mounted hanging starters",
        default=const.HANGING_TOP_HEIGHT, unit='LENGTH', precision=4)  # type: ignore
    panel_thickness: FloatProperty(
        name="Panel Thickness", default=const.PANEL_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    shelf_thickness: FloatProperty(
        name="Shelf Thickness", default=const.SHELF_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    # The room's standard for how a shelf on clips is cut. An opening
    # can take either figure over for itself.
    shelf_clip_gap: FloatProperty(
        name="Shelf Clip Gap", default=const.SHELF_CLIP_GAP,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    shelf_setback: FloatProperty(
        name="Shelf Setback", default=const.SHELF_SETBACK,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    countertop_thickness: FloatProperty(
        name="Countertop Thickness", default=const.COUNTERTOP_THICKNESS,
        unit='LENGTH', precision=4)  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height", default=const.DEFAULT_TOE_KICK_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback", default=const.DEFAULT_TOE_KICK_SETBACK,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Selection modes -----
    closet_selection_mode: EnumProperty(
        name="Closet Selection Mode",
        items=[
            ('Starters', "Starters", "Select whole closet starters"),
            ('Bays', "Bays", "Select bay cages"),
            ('Openings', "Openings", "Select opening cages"),
            ('Parts', "Parts", "Select individual parts"),
        ],
        default='Starters',
        update=_update_closet_selection_mode)  # type: ignore
    closet_selection_mode_enabled: BoolProperty(
        name="Enable Closet Selection Mode",
        description="Highlight objects matching the active selection mode",
        default=True,
        update=_update_closet_selection_mode)  # type: ignore

    selection_mode_show_sizes: BoolProperty(
        name="Show Sizes",
        description="Show editable dimension labels in selection modes",
        default=True)  # type: ignore

    # ----- Options (materials / fronts / pulls / drawer boxes /
    # molding). Selections live at scene level and re-apply to the
    # whole room on change; new placements pick them up at finish
    # time. Materials is the first category wired up - the remaining
    # dropdowns land one category at a time.
    closet_material: EnumProperty(
        name="Closet Material",
        description="Carcass material (panels, shelves, kicks, tops)",
        items=materials_closets.material_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_front_material: EnumProperty(
        name="Front Material",
        description="Door and drawer front material (Match Closet "
                    "follows the closet material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_edge_material: EnumProperty(
        name="Closet Edgebanding",
        description="Edgebanding on closet parts (Match = the closet "
                    "material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_front_edge_material: EnumProperty(
        name="Front Edgebanding",
        description="Edgebanding on doors and drawer fronts (Match = "
                    "the fronts material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore

    closet_countertop_material: EnumProperty(
        name="Countertop Material",
        description="Surface material on countertops and their "
                    "backsplashes",
        items=materials_closets.countertop_material_enum_items,
        update=materials_closets.update_room)  # type: ignore
    use_closet_material_for_countertops: BoolProperty(
        name="Use Closet Material for Countertops",
        description="Surface the tops in the closet material instead "
                    "of a countertop material, so the run reads as one "
                    "piece. Tops then take the shelf thickness",
        default=False,
        update=_update_countertop_mode)  # type: ignore

    closet_panel_type: EnumProperty(
        name="Door Panel",
        description="Center panel on 5-piece doors: wood or glass",
        items=materials_closets.PANEL_TYPES,
        default='Vertical Grain',
        update=materials_closets.update_room)  # type: ignore
    closet_door_grain: EnumProperty(
        name="Door Grain",
        description="Grain direction on closet doors",
        items=[('VERTICAL', "Vertical", ""),
               ('HORIZONTAL', "Horizontal", "")],
        default='VERTICAL',
        update=materials_closets.update_room)  # type: ignore
    closet_drawer_grain: EnumProperty(
        name="Drawer Front Grain",
        description="Grain direction on closet drawer fronts",
        items=[('VERTICAL', "Vertical", ""),
               ('HORIZONTAL', "Horizontal", "")],
        default='HORIZONTAL',
        update=materials_closets.update_room)  # type: ignore

    closet_pull: EnumProperty(
        name="Pull",
        description="Handle used on every closet front",
        items=pulls_closets.pull_enum_items,
        update=pulls_closets.update_room)  # type: ignore
    closet_pull_finish: EnumProperty(
        name="Pull Finish",
        items=pulls_closets.PULL_FINISHES,
        default='Polished Chrome',
        update=pulls_closets.update_room)  # type: ignore
    pull_horizontal_offset: FloatProperty(
        name="From Edge",
        description="Door edge to pull center",
        default=units.inch(2.0), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_base: FloatProperty(
        name="Base",
        description="Top of base door to top of pull",
        default=units.inch(1.5), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_tall: FloatProperty(
        name="Tall",
        description="Pull height off the floor on tall doors",
        default=units.inch(45.0), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_upper: FloatProperty(
        name="Upper",
        description="Bottom of upper door to bottom of pull",
        default=units.inch(1.5), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    center_pulls_on_drawer_front: BoolProperty(
        name="Center Pulls on Drawer Fronts",
        default=True,
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_drawers: FloatProperty(
        name="Drawer",
        description="Top of the drawer front to the middle of the pull",
        default=const.DRAWER_PULL_VERTICAL_LOCATION, unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore

    closet_rod_type: EnumProperty(
        name="Rod Type",
        items=pulls_closets.ROD_TYPES,
        default='OVAL',
        update=pulls_closets.update_room)  # type: ignore
    closet_rod_finish: EnumProperty(
        name="Rod Finish",
        items=pulls_closets.ROD_FINISHES,
        default='Polished Chrome',
        update=pulls_closets.update_room)  # type: ignore
    closet_hanger_model: EnumProperty(
        name="Hangers",
        description="Display hanger model shown on closet rods",
        items=pulls_closets.hanger_enum_items,
        update=pulls_closets.update_room)  # type: ignore

    closet_drawer_box: EnumProperty(
        name="Drawer Box",
        description="Drawer box system used by every closet drawer",
        items=drawer_boxes_closets.BOX_TYPES,
        default='AVANTECH',
        update=drawer_boxes_closets.update_room)  # type: ignore

    closet_front_style: EnumProperty(
        name="Front Style",
        description="Door and drawer front style for every closet front",
        items=fronts_closets.FRONT_STYLES,
        default='SLAB',
        update=fronts_closets.update_room)  # type: ignore

    closet_crown_profile: EnumProperty(
        name="Crown Profile",
        description="Profile used by Add Crown Molding",
        items=molding_closets.profile_enum_items)  # type: ignore

    closet_base_profile: EnumProperty(
        name="Base Profile",
        description="Profile used by Add Base Molding",
        items=molding_closets.base_profile_enum_items)  # type: ignore

    # ----- Library UI state -----
    closet_tabs: EnumProperty(
        name="Closet Tabs",
        items=[
            ('LIBRARY', "Library", "Library"),
            ('OPTIONS', "Options", "Options"),
        ],
        default='LIBRARY')  # type: ignore

    library_view_mode: EnumProperty(
        name="Library View",
        description="Show library items as thumbnail tiles or a compact list",
        items=[
            ('THUMBNAIL', "Thumbnail", "Thumbnail tiles with previews",
             'IMGDISPLAY', 0),
            ('LIST', "List", "Compact list of names", 'LONGDISPLAY', 1),
        ],
        default='THUMBNAIL')  # type: ignore

    # ---- Library tab section toggles ----
    show_closet_sizes: BoolProperty(
        name="Show Closet Sizes", default=False)  # type: ignore
    show_starter_library: BoolProperty(
        name="Show Closet Starters", default=True)  # type: ignore
    show_thickness_sizes: BoolProperty(
        name="Show Part Thicknesses", default=False)  # type: ignore
    show_shelf_sizes: BoolProperty(
        name="Show Shelf Sizes", default=False)  # type: ignore
    show_toe_kick_sizes: BoolProperty(
        name="Show Toe Kick Sizes", default=False)  # type: ignore

    # ---- Options tab section toggles ----
    show_material_options: BoolProperty(
        name="Show Materials", default=False)  # type: ignore
    show_front_options: BoolProperty(
        name="Show Front Styles", default=False)  # type: ignore
    show_pull_options: BoolProperty(
        name="Show Pulls", default=False)  # type: ignore
    show_drawer_box_options: BoolProperty(
        name="Show Drawer Boxes", default=False)  # type: ignore
    show_rod_options: BoolProperty(
        name="Show Rods and Hangers", default=False)  # type: ignore
    show_countertop_options: BoolProperty(
        name="Show Countertops", default=False)  # type: ignore
    show_molding_options: BoolProperty(
        name="Show Molding", default=False)  # type: ignore

    # =====================================================================
    # UI: closet sizes (Library tab)
    # =====================================================================
    def draw_closet_sizes_ui(self, layout, context):
        """Seed sizes for new starters. The three closet types share a
        depth / height grid so the columns read across; the values that
        belong to one type only sit under it."""
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Default Width:")
        row.prop(self, 'default_closet_width', text="")

        col.separator()
        row = col.row()
        row.label(text="Sizes")
        row.label(text="Base")
        row.label(text="Tall")
        row.label(text="Hanging")

        row = col.row()
        row.label(text="Depth:")
        row.prop(self, 'default_base_panel_depth', text="")
        row.prop(self, 'default_tall_panel_depth', text="")
        row.prop(self, 'default_hanging_panel_depth', text="")

        row = col.row()
        row.label(text="Height:")
        row.prop(self, 'base_panel_height', text="")
        row.prop(self, 'tall_panel_height', text="")
        row.prop(self, 'hanging_panel_height', text="")

        col.separator()
        # The fallback depth serves any starter whose type has no depth
        # of its own - the corner starters read it for both wings.
        row = col.row()
        row.label(text="Fallback Depth:")
        row.prop(self, 'default_panel_depth', text="")
        row = col.row()
        row.label(text="Hanging Top Height:")
        row.prop(self, 'hanging_top_height', text="")
        row = col.row()
        row.label(text="Corner Size:")
        row.prop(self, 'default_corner_closet_size', text="")
        row = col.row()
        row.label(text="Accent Overhang:")
        row.prop(self, 'default_accent_overhang', text="")

        box = layout.box()
        box.prop(self, 'show_thickness_sizes', text="Part Thicknesses",
                 icon='TRIA_DOWN' if self.show_thickness_sizes
                 else 'TRIA_RIGHT', emboss=False)
        if self.show_thickness_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'panel_thickness', text="Panel")
            sub.prop(self, 'shelf_thickness', text="Shelf")

        box = layout.box()
        box.prop(self, 'show_shelf_sizes', text="Adjustable Shelves",
                 icon='TRIA_DOWN' if self.show_shelf_sizes
                 else 'TRIA_RIGHT', emboss=False)
        if self.show_shelf_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'shelf_clip_gap', text="Clip Gap")
            sub.prop(self, 'shelf_setback', text="Setback")

        box = layout.box()
        box.prop(self, 'show_toe_kick_sizes', text="Toe Kick",
                 icon='TRIA_DOWN' if self.show_toe_kick_sizes
                 else 'TRIA_RIGHT', emboss=False)
        if self.show_toe_kick_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'toe_kick_height', text="Height")
            sub.prop(self, 'toe_kick_setback', text="Setback")

    # =====================================================================
    # UI: starters (Library tab)
    # =====================================================================
    def draw_starter_library_ui(self, layout, context):
        """One row per section: the section label on the left, then a
        cell per product to its right. Thumbnail view puts a preview
        tile above each button; list view drops the tiles for a compact
        list of names. Bay count is derived from width at placement."""
        for sec_label, entries in starter_presets.STARTER_SECTIONS:
            row = layout.row(align=True)
            row.label(text=sec_label)
            for name, label, _desc in entries:
                cell = row.column(align=True)
                if self.library_view_mode == 'THUMBNAIL':
                    icon_id = load_starter_thumbnail(name)
                    if icon_id:
                        cell.template_icon(icon_value=icon_id, scale=4.0)
                op = cell.operator('hb_closets.place_starter', text=label)
                op.starter_name = name

    # =====================================================================
    # UI: materials (Options tab)
    # =====================================================================
    def draw_material_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_material', text="Closet")
        col.prop(self, 'closet_front_material', text="Fronts")

        col.separator()
        col.label(text="Edgebanding:")
        col.prop(self, 'closet_edge_material', text="Closet Edge")
        col.prop(self, 'closet_front_edge_material', text="Front Edge")

        col.separator()
        col.label(text="Grain Direction:")
        col.prop(self, 'closet_door_grain', text="Doors")
        col.prop(self, 'closet_drawer_grain', text="Drawer Fronts")

    # =====================================================================
    # UI: door and drawer front styles (Options tab)
    # =====================================================================
    def draw_front_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_front_style', text="Front Style")
        col.prop(self, 'closet_panel_type', text="Door Panel")

    # =====================================================================
    # UI: pulls (Options tab)
    # =====================================================================
    def draw_pull_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_pull', text="Pull")
        col.prop(self, 'closet_pull_finish', text="Finish")

        col.separator()
        col.label(text="Position:")
        col.prop(self, 'pull_horizontal_offset', text="From Edge")
        col.prop(self, 'pull_vertical_location_base', text="Base Vertical")
        col.prop(self, 'pull_vertical_location_tall', text="Tall Vertical")
        col.prop(self, 'pull_vertical_location_upper', text="Upper Vertical")
        col.prop(self, 'center_pulls_on_drawer_front',
                 text="Center Drawer Pulls")
        sub = col.row()
        sub.enabled = not self.center_pulls_on_drawer_front
        sub.prop(self, 'pull_vertical_location_drawers',
                 text="Drawer Vertical")

    # =====================================================================
    # UI: drawer boxes (Options tab)
    # =====================================================================
    def draw_drawer_box_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_drawer_box', text="Drawer Box")

    # =====================================================================
    # UI: rods and hangers (Options tab)
    # =====================================================================
    def draw_rod_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.label(text="Hanging Rods:")
        col.prop(self, 'closet_rod_type', text="Type")
        col.prop(self, 'closet_rod_finish', text="Finish")

        col.separator()
        col.label(text="Hangers:")
        col.prop(self, 'closet_hanger_model', text="Model")

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.randomize_hangers',
                     text="Randomize Hangers", icon='FILE_REFRESH')
        row.operator('hb_closets.install_model_pack', text="", icon='IMPORT')

    # =====================================================================
    # UI: countertops (Options tab)
    # =====================================================================
    def draw_countertop_options_ui(self, layout, context):
        col = layout.column(align=True)
        # With the toggle on, tops take the closet material and the
        # shelf thickness, so neither field below applies.
        col.prop(self, 'use_closet_material_for_countertops',
                 text="Use Closet Material for Tops")
        sub = col.row()
        sub.enabled = not self.use_closet_material_for_countertops
        sub.prop(self, 'closet_countertop_material', text="Material")
        sub = col.row()
        sub.enabled = not self.use_closet_material_for_countertops
        sub.prop(self, 'countertop_thickness', text="Thickness")

    # =====================================================================
    # UI: molding (Options tab)
    # =====================================================================
    def draw_molding_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.label(text="Crown:")
        col.prop(self, 'closet_crown_profile', text="Profile")
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.add_molding', text="Add Crown Molding",
                     icon='ADD').molding_kind = 'CROWN'
        row.operator('hb_closets.delete_molding', text="",
                     icon='X').molding_kind = 'CROWN'

        col.separator()
        col.label(text="Base:")
        col.prop(self, 'closet_base_profile', text="Profile")
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.add_molding', text="Add Base Molding",
                     icon='ADD').molding_kind = 'BASE'
        row.operator('hb_closets.delete_molding', text="",
                     icon='X').molding_kind = 'BASE'

    # =====================================================================
    # UI: master draw entry point (called by view3d_sidebar)
    # =====================================================================
    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        # Tab selector. On the LIBRARY tab an icon-only Thumbnail/List
        # toggle is pinned to the right end of this same row.
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, 'closet_tabs', 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, 'closet_tabs', 'OPTIONS', icon='PREFERENCES')

        if self.closet_tabs == 'LIBRARY':
            view = row.row(align=True)
            view.alignment = 'RIGHT'
            view.prop(self, 'library_view_mode', expand=True, icon_only=True)
            sections = [
                ('show_closet_sizes', "Closet Sizes",
                 self.draw_closet_sizes_ui),
                ('show_starter_library', "Closet Starters",
                 self.draw_starter_library_ui),
            ]
        else:
            # Dropdown changes on this tab re-apply room-wide.
            sections = [
                ('show_material_options', "Materials",
                 self.draw_material_options_ui),
                ('show_front_options', "Door & Drawer Front Styles",
                 self.draw_front_options_ui),
                ('show_pull_options', "Pulls",
                 self.draw_pull_options_ui),
                ('show_drawer_box_options', "Drawer Boxes",
                 self.draw_drawer_box_options_ui),
                ('show_rod_options', "Rods & Hangers",
                 self.draw_rod_options_ui),
                ('show_countertop_options', "Countertops",
                 self.draw_countertop_options_ui),
                ('show_molding_options', "Molding",
                 self.draw_molding_options_ui),
            ]

        for prop_name, label, draw_fn in sections:
            expanded = getattr(self, prop_name)
            box = col.box()
            hrow = box.row()
            hrow.alignment = 'LEFT'
            hrow.prop(self, prop_name, text=label,
                      icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT',
                      emboss=False)
            if expanded:
                draw_fn(box, context)


classes = (
    Closet_Starter_Props,
    Closet_Bay_Props,
    Closet_Opening_Props,
    Closets_Scene_Props,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hb_closets = PointerProperty(
        name="Closets Props", type=Closets_Scene_Props)
    bpy.types.Object.hb_closet_starter = PointerProperty(
        name="Closet Starter Props", type=Closet_Starter_Props)
    bpy.types.Object.hb_closet_bay = PointerProperty(
        name="Closet Bay Props", type=Closet_Bay_Props)
    bpy.types.Object.hb_closet_opening = PointerProperty(
        name="Closet Opening Props", type=Closet_Opening_Props)


def unregister():
    for pcoll in preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    preview_collections.clear()
    if hasattr(bpy.types.Scene, 'hb_closets'):
        del bpy.types.Scene.hb_closets
    if hasattr(bpy.types.Object, 'hb_closet_starter'):
        del bpy.types.Object.hb_closet_starter
    if hasattr(bpy.types.Object, 'hb_closet_bay'):
        del bpy.types.Object.hb_closet_bay
    if hasattr(bpy.types.Object, 'hb_closet_opening'):
        del bpy.types.Object.hb_closet_opening
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
