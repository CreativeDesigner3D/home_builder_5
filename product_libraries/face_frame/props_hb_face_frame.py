"""Face Frame product library - scene properties and library UI.

Phase 2 scaffolding: scene-level PropertyGroup, library presentation, and
section toggles. Construction logic and per-cabinet PropertyGroups land in
Phase 3 (types_face_frame.py).
"""
import bpy
import os
from bpy.types import (
    PropertyGroup,
    UIList,
)
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
)
from ... import units


# ---------------------------------------------------------------------------
# Preview collection management - mirrors frameless lifecycle
# ---------------------------------------------------------------------------
preview_collections = {}


def get_library_previews():
    """Get or create the library preview collection (user library, moldings)."""
    if "library_previews" not in preview_collections:
        preview_collections["library_previews"] = bpy.utils.previews.new()
    return preview_collections["library_previews"]


def get_cabinet_previews():
    """Get or create the cabinet preview collection (button thumbnails)."""
    if "cabinet_previews" not in preview_collections:
        preview_collections["cabinet_previews"] = bpy.utils.previews.new()
    return preview_collections["cabinet_previews"]


def get_cabinet_thumbnail_path():
    """Path to the bundled face_frame_thumbnails folder."""
    return os.path.join(os.path.dirname(__file__), "face_frame_thumbnails")


def get_frameless_thumbnail_fallback_path():
    """Fallback to the frameless thumbnails folder while face_frame ones are
    being created. A face_frame thumbnail of the same name takes precedence."""
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "frameless",
        "frameless_thumbnails",
    )


def load_library_thumbnail(filepath, name):
    """Load a thumbnail image into the user library preview collection."""
    pcoll = get_library_previews()
    if name in pcoll:
        return pcoll[name].icon_id
    if os.path.exists(filepath):
        thumb = pcoll.load(name, filepath, 'IMAGE')
        return thumb.icon_id
    return 0


def load_cabinet_thumbnail(name):
    """Load a cabinet button thumbnail by name (without extension).

    Looks in face_frame_thumbnails/ first, falls back to the frameless folder
    so the library has visible icons before face-frame-specific renders are
    produced. Returns 0 if no thumbnail is found anywhere.
    """
    pcoll = get_cabinet_previews()
    if name in pcoll:
        return pcoll[name].icon_id

    # Primary: face frame thumbnails
    primary = os.path.join(get_cabinet_thumbnail_path(), f"{name}.png")
    if os.path.exists(primary):
        return pcoll.load(name, primary, 'IMAGE').icon_id

    # Fallback: frameless thumbnails
    fallback = os.path.join(get_frameless_thumbnail_fallback_path(), f"{name}.png")
    if os.path.exists(fallback):
        return pcoll.load(name, fallback, 'IMAGE').icon_id

    return 0


def clear_library_previews():
    """Clear loaded user library previews (called when refreshing)."""
    if "library_previews" in preview_collections:
        preview_collections["library_previews"].clear()


# ---------------------------------------------------------------------------
# Update callbacks
# ---------------------------------------------------------------------------
def update_cabinet_style_name(self, context):
    """Keep style names unique within the collection."""
    main = context.scene.hb_face_frame
    base_name = self.name if self.name else "Style"
    existing = [s.name for s in main.cabinet_styles if s != self]
    if base_name not in existing:
        return
    i = 1
    while f"{base_name}.{i:03d}" in existing:
        i += 1
    self.name = f"{base_name}.{i:03d}"


def update_top_cabinet_clearance(self, context):
    """Recompute upper cabinet location when clearance changes.

    Mirrors the frameless behaviour - this is a hook point for Phase 3 when
    we wire it to existing cabinets.
    """
    pass


def update_face_frame_selection_mode(self, context):
    """Apply visibility highlighting for the active selection mode.

    Calls the hb_face_frame.toggle_mode operator which iterates all scene
    objects and highlights/dims them based on which mode is active.
    """
    bpy.ops.hb_face_frame.toggle_mode(search_obj_name="")


# ---------------------------------------------------------------------------
# Cabinet Style (placeholder shell, full implementation in Phase 4)
# ---------------------------------------------------------------------------
class Face_Frame_Cabinet_Style(PropertyGroup):
    """Per-cabinet face frame style: wood, finish, face frame member sizes,
    door overlay. This is a Phase 2 shell - the full property set, custom
    procedural material support, and assign_style_to_cabinet logic are
    implemented in Phase 4."""

    name: StringProperty(
        name="Name",
        description="Cabinet style name",
        default="Style",
        update=update_cabinet_style_name,
    )  # type: ignore

    show_expanded: BoolProperty(
        name="Show Expanded",
        description="Show expanded style options",
        default=False,
    )  # type: ignore

    wood_species: EnumProperty(
        name="Wood Species",
        description="Wood species for cabinet exterior",
        items=[
            ('MAPLE', "Maple", "Maple wood"),
            ('OAK', "Oak", "Oak wood"),
            ('CHERRY', "Cherry", "Cherry wood"),
            ('WALNUT', "Walnut", "Walnut wood"),
            ('BIRCH', "Birch", "Birch wood"),
            ('HICKORY', "Hickory", "Hickory wood"),
            ('ALDER', "Alder", "Alder wood"),
            ('PAINT_GRADE', "Paint Grade", "Paint Grade"),
            ('CUSTOM', "Custom Material", "Use a custom material"),
        ],
        default='MAPLE',
    )  # type: ignore

    door_overlay_type: EnumProperty(
        name="Door Overlay",
        description="Door overlay style for face frame cabinets",
        items=[
            ('STANDARD', "Standard Overlay", "Standard partial overlay"),
            ('TRANSITIONAL', "Transitional", "Transitional overlay"),
            ('FULL', "Full Overlay", "Full overlay"),
            ('PARTIAL_INSET', "Partial Inset", "Partial inset"),
            ('FULL_INSET', "Full Inset", "Full inset (flush)"),
        ],
        default='STANDARD',
    )  # type: ignore


class HB_UL_face_frame_cabinet_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon='SHADERFX')


# ---------------------------------------------------------------------------
# Object-level PropertyGroups - face frame cabinet & bay state
# ---------------------------------------------------------------------------
def _update_cabinet_dim(self, context):
    """Triggered when a cabinet-level dimension changes. Walks back to the
    cabinet root (works even if the prop is on a descendant somehow) and
    runs recalculate() to push values to all parts.

    Imported lazily to avoid any chance of a circular import at module load.
    """
    from . import types_face_frame
    types_face_frame.recalculate_face_frame_cabinet(self.id_data)

def _update_front_type(self, context):
    """Front-type write hook: when a user picks DOOR, ensure the opening
    carries an ADJUSTABLE_SHELF interior item. If the user later removes
    the shelves manually, switching front_type away and back to DOOR
    re-adds them; switching to any other front_type leaves the
    interior_items collection untouched.
    """
    if self.front_type == 'DOOR':
        has_shelves = any(
            item.kind == 'ADJUSTABLE_SHELF' for item in self.interior_items
        )
        if not has_shelves:
            # .add() picks up the EnumProperty default ('ADJUSTABLE_SHELF')
            # without firing the kind update. Quantity is left at the
            # IntProperty default (1) and gets recomputed by the recalc
            # below since unlock_shelf_qty defaults to False.
            self.interior_items.add()
    _update_cabinet_dim(self, context)


def _update_bay_width(self, context):
    """Update callback for Face_Frame_Bay_Props.width.

    Distinguishes user edits from system writes:
    - System writes (during the cabinet's _distribute_bay_widths) are
      bracketed by _DISTRIBUTING_WIDTHS. We exit immediately for those.
    - User edits flip unlock_width=True so the new width holds during
      future redistributions, then trigger a recalc. Setting unlock_width
      itself fires _update_cabinet_dim which runs the recalc, so we don't
      need to call it again here.
    """
    from . import types_face_frame
    root = types_face_frame.find_cabinet_root(self.id_data)
    if root is None:
        return
    if id(root) in types_face_frame._DISTRIBUTING_WIDTHS:
        return  # system write - skip auto-lock and skip recalc
    # User edit
    if not self.unlock_width:
        # Auto-lock. Setting unlock_width fires _update_cabinet_dim
        # which triggers recalc, so we don't call recalc directly here.
        self.unlock_width = True
    else:
        # Already locked - user is just nudging the value. Run recalc
        # so other unlocked bays redistribute around the new locked value.
        types_face_frame.recalculate_face_frame_cabinet(self.id_data)


class Face_Frame_Mid_Stile_Width(PropertyGroup):
    """Width of the mid stile that sits between two adjacent bays.

    Lives in a CollectionProperty on Face_Frame_Cabinet_Props.
    Index N is the mid stile between bay N and bay N+1.
    """
    width: FloatProperty(
        name="Width",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    unlock: BoolProperty(
        name="Unlock",
        description="Hold this mid stile width independent of cabinet defaults",
        default=False,
    )  # type: ignore

    extend_up_amount: FloatProperty(
        name="Extend Up Amount",
        default=0.0,
        unit='LENGTH',
        precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    extend_down_amount: FloatProperty(
        name="Extend Down Amount",
        default=0.0,
        unit='LENGTH',
        precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore


class Face_Frame_Cabinet_Props(PropertyGroup):
    """Cabinet-level face frame state. Attached to the cabinet's root object
    as bpy.types.Object.face_frame_cabinet.

    Holds everything that describes the cabinet as a whole: type, finished
    end conditions, blind setup, stile/rail defaults, toe kick, optional
    parts, mid stile collection. Per-bay data lives on each bay child object.
    """

    # ---- Live dimensions (single source of truth; cage Dim X/Y/Z is mirrored from these) ----
    width: FloatProperty(
        name="Width",
        description="Cabinet width (X dimension)",
        default=units.inch(36.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    height: FloatProperty(
        name="Height",
        description="Cabinet height (Z dimension)",
        default=units.inch(34.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    depth: FloatProperty(
        name="Depth",
        description="Cabinet depth (Y dimension)",
        default=units.inch(24.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    cabinet_type: EnumProperty(
        name="Cabinet Type",
        items=[
            ('BASE', "Base", "Base cabinet"),
            ('TALL', "Tall", "Tall cabinet"),
            ('UPPER', "Upper", "Upper cabinet"),
            ('LAP_DRAWER', "Lap Drawer", "Lap drawer cabinet"),
        ],
        default='BASE',
    )  # type: ignore

    is_sink: BoolProperty(name="Is Sink Cabinet", default=False)  # type: ignore
    is_built_in_appliance: BoolProperty(name="Is Built-in Appliance", default=False)  # type: ignore
    is_double: BoolProperty(name="Is Stacked / Double", default=False)  # type: ignore

    FIN_END_ITEMS = [
        ('NONE', "None", "No finished end"),
        ('THREE_QUARTER', '3/4 Finished', "Three-quarter finished end"),
        ('HALF', '1/2 Finished', "Half finished end"),
        ('QUARTER', '1/4 Finished', "Quarter finished end"),
        ('PANELED', "Paneled", "Paneled finished end"),
        ('FALSE_FF', "False Face Frame", "False face frame end"),
        ('WORKING_FF', "Working Face Frame", "Working face frame end"),
        ('SOLID_BEADBOARD', "Solid Beadboard", "Solid beadboard finished end"),
        ('MDF_BEADBOARD', "MDF Beadboard", "MDF beadboard finished end"),
        ('FLUSH_X', "Finished Flush X Inches", "Finished flush x inches"),
    ]

    left_finished_end_condition: EnumProperty(
        name="Left Finished End", items=FIN_END_ITEMS, default='NONE'
    )  # type: ignore
    right_finished_end_condition: EnumProperty(
        name="Right Finished End", items=FIN_END_ITEMS, default='NONE'
    )  # type: ignore
    back_finished_end_condition: EnumProperty(
        name="Back Finished End", items=FIN_END_ITEMS, default='NONE'
    )  # type: ignore

    blind_left: BoolProperty(name="Blind Left", default=False)  # type: ignore
    blind_right: BoolProperty(name="Blind Right", default=False)  # type: ignore
    blind_amount_left: FloatProperty(
        name="Blind Amount Left", default=units.inch(24.0), unit='LENGTH', precision=4
    )  # type: ignore
    blind_amount_right: FloatProperty(
        name="Blind Amount Right", default=units.inch(24.0), unit='LENGTH', precision=4
    )  # type: ignore
    blind_reveal: FloatProperty(
        name="Blind Reveal", default=units.inch(1.5), unit='LENGTH', precision=4
    )  # type: ignore

    left_stile_width: FloatProperty(
        name="Left Stile Width", default=units.inch(2.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_stile_width: FloatProperty(
        name="Right Stile Width", default=units.inch(2.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_left_stile: BoolProperty(name="Unlock Left Stile", default=False)  # type: ignore
    unlock_right_stile: BoolProperty(name="Unlock Right Stile", default=False)  # type: ignore
    turn_off_left_stile: BoolProperty(name="Turn Off Left Stile", default=False)  # type: ignore
    turn_off_right_stile: BoolProperty(name="Turn Off Right Stile", default=False)  # type: ignore

    LEFT_STILE_TYPE_ITEMS = [
        ('STANDARD', "Standard", "Standard stile"),
        ('WALL', "Wall", "Wall stile (extends past carcass)"),
        ('BLIND', "Blind", "Blind corner stile"),
    ]
    left_stile_type: EnumProperty(
        name="Left Stile Type", items=LEFT_STILE_TYPE_ITEMS, default='STANDARD'
    )  # type: ignore
    right_stile_type: EnumProperty(
        name="Right Stile Type", items=LEFT_STILE_TYPE_ITEMS, default='STANDARD'
    )  # type: ignore

    extend_left_stile_up: BoolProperty(name="Extend Left Stile Up", default=False)  # type: ignore
    extend_left_stile_down: BoolProperty(name="Extend Left Stile Down", default=False)  # type: ignore
    extend_right_stile_up: BoolProperty(name="Extend Right Stile Up", default=False)  # type: ignore
    extend_right_stile_down: BoolProperty(name="Extend Right Stile Down", default=False)  # type: ignore
    extend_left_stile_up_amount: FloatProperty(
        name="Extend Left Stile Up Amount", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    extend_left_stile_down_amount: FloatProperty(
        name="Extend Left Stile Down Amount", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    extend_right_stile_up_amount: FloatProperty(
        name="Extend Right Stile Up Amount", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    extend_right_stile_down_amount: FloatProperty(
        name="Extend Right Stile Down Amount", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore

    extend_left: FloatProperty(
        name="Extend Left", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    extend_right: FloatProperty(
        name="Extend Right", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    left_offset: FloatProperty(
        name="Left Offset", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    right_offset: FloatProperty(
        name="Right Offset", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore

    top_rail_width: FloatProperty(
        name="Top Rail Width", default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    stretcher_width: FloatProperty(
        name="Stretcher Width",
        description="Front-to-back depth of the top stretchers (typical 3.5 in)",
        default=units.inch(3.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    stretcher_thickness: FloatProperty(
        name="Stretcher Thickness",
        description="Vertical thickness of the top stretchers (typical 1/2 in)",
        default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    bottom_rail_width: FloatProperty(
        name="Bottom Rail Width", default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_top_rail: BoolProperty(name="Unlock Top Rail (Cabinet)", default=False)  # type: ignore
    unlock_bottom_rail: BoolProperty(name="Unlock Bottom Rail (Cabinet)", default=False)  # type: ignore

    # Mid rails / mid stiles INSIDE a bay (face frame members created by
    # splitting an opening). Cabinet-level defaults; per-member override
    # comes later if needed.
    bay_mid_rail_width: FloatProperty(
        name="Bay Mid Rail Width",
        description="Vertical extent of mid rails created by horizontal splits inside a bay",
        default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    bay_mid_stile_width: FloatProperty(
        name="Bay Mid Stile Width",
        description="Horizontal extent of mid stiles created by vertical splits inside a bay",
        default=units.inch(2.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # Cabinet-level overlay defaults. Applied to every opening unless the
    # opening unlocks the corresponding side and supplies its own value.
    default_top_overlay: FloatProperty(
        name="Default Top Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    default_bottom_overlay: FloatProperty(
        name="Default Bottom Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    default_left_overlay: FloatProperty(
        name="Default Left Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    default_right_overlay: FloatProperty(
        name="Default Right Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    material_thickness: FloatProperty(
        name="Material Thickness", default=units.inch(0.75), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    face_frame_thickness: FloatProperty(
        name="Face Frame Thickness", default=units.inch(0.75), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    door_thickness: FloatProperty(
        name="Door Thickness",
        description="Thickness of doors and drawer fronts attached to openings",
        default=units.inch(0.75), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    back_thickness: FloatProperty(
        name="Back Thickness", default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    finish_toe_kick_thickness: FloatProperty(
        name="Finish Toe Kick Thickness", default=units.inch(0.25), unit='LENGTH', precision=4
    )  # type: ignore

    toe_kick_type: EnumProperty(
        name="Toe Kick Type",
        items=[
            ('NOTCH', "Notch Ends to Floor", "Sides notch to floor; toe kick recessed"),
            ('LADDER', "Ladder Style", "Ladder-style toe kick; sides start above floor"),
            ('BASE_ASSEMBLY', "Base Assembly Each Box", "Each box has its own base"),
        ],
        default='NOTCH',
    )  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height", default=units.inch(4.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback", default=units.inch(3.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    toe_kick_thickness: FloatProperty(
        name="Toe Kick Thickness", default=units.inch(0.75), unit='LENGTH', precision=4
    )  # type: ignore
    inset_toe_kick_left: FloatProperty(
        name="Inset Toe Kick Left", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    inset_toe_kick_right: FloatProperty(
        name="Inset Toe Kick Right", default=0.0, unit='LENGTH', precision=4
    )  # type: ignore
    flush_toe_kick: BoolProperty(name="Flush Toe Kick", default=False)  # type: ignore
    loose_toe_kick: BoolProperty(name="Loose Toe Kick", default=False)  # type: ignore
    include_finish_toe_kick: BoolProperty(name="Include Finish Toe Kick", default=True)  # type: ignore

    include_external_nailer: BoolProperty(name="Include External Nailer", default=False)  # type: ignore
    include_internal_nailer: BoolProperty(name="Include Internal Nailer", default=False)  # type: ignore
    include_thin_finished_bottom: BoolProperty(name="Include 1/4 Finished Bottom", default=False)  # type: ignore
    include_thick_finished_bottom: BoolProperty(name="Include 3/4 Finished Bottom", default=False)  # type: ignore
    include_blocking: BoolProperty(name="Include Blocking", default=False)  # type: ignore

    mid_stile_widths: CollectionProperty(type=Face_Frame_Mid_Stile_Width)  # type: ignore


class Face_Frame_Bay_Props(PropertyGroup):
    """Per-bay state for face frame cabinets. Attached to each bay's cage
    object as bpy.types.Object.face_frame_bay.

    Each bay carries its own width, height, depth, kick height, top offset,
    plus per-bay rail widths. Unlock toggles mark bays that hold their values
    independently of cabinet-level defaults.
    """

    bay_index: IntProperty(
        name="Bay Index",
        description="Position in the parent cabinet's bay list (0-based)",
        default=0,
    )  # type: ignore

    width: FloatProperty(
        name="Width", default=units.inch(18.0), unit='LENGTH', precision=4,
        update=_update_bay_width,
    )  # type: ignore
    height: FloatProperty(
        name="Height", default=units.inch(34.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    depth: FloatProperty(
        name="Depth", default=units.inch(24.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    kick_height: FloatProperty(
        name="Kick Height", default=units.inch(4.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    top_offset: FloatProperty(
        name="Top Offset",
        description="Distance from cabinet top to top of this bay's opening",
        default=0.0,
        unit='LENGTH',
        precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    top_rail_width: FloatProperty(
        name="Top Rail Width", default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    bottom_rail_width: FloatProperty(
        name="Bottom Rail Width", default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    delete_bay: BoolProperty(
        name="Delete Bay",
        description="Skip this bay during construction (used for appliance cutouts)",
        default=False,
    )  # type: ignore
    remove_bottom: BoolProperty(
        name="Remove Bottom", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    apron_bay: BoolProperty(name="Apron Bay", default=False)  # type: ignore
    finish_bay: BoolProperty(name="Finish Bay", default=False)  # type: ignore

    unlock_width: BoolProperty(
        name="Unlock Width",
        description="Hold this bay's width during gang-construction redistribution",
        default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_height: BoolProperty(
        name="Unlock Height", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_depth: BoolProperty(
        name="Unlock Depth", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_kick_height: BoolProperty(
        name="Unlock Kick Height", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_top_offset: BoolProperty(
        name="Unlock Top Offset", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_top_rail: BoolProperty(
        name="Unlock Top Rail", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_bottom_rail: BoolProperty(
        name="Unlock Bottom Rail", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore


class Face_Frame_Interior_Item(bpy.types.PropertyGroup):
    """One interior item attached to an opening - shelf, accessory, etc.
    Holds every kind's data side-by-side; the recalc reads only the
    fields relevant to the active kind. New kinds add their own fields
    here and a mapping in INTERIOR_KIND_TO_ROLE.
    """

    INTERIOR_KIND_ITEMS = [
        ('ADJUSTABLE_SHELF', "Adjustable Shelves", "Set of evenly-spaced shelves on shelf pins"),
        ('ACCESSORY',        "Accessory",          "Free-text accessory label rendered inside the opening"),
    ]
    kind: EnumProperty(
        name="Kind", items=INTERIOR_KIND_ITEMS, default='ADJUSTABLE_SHELF',
        update=_update_cabinet_dim,
    )  # type: ignore

    # ADJUSTABLE_SHELF: count is auto-seeded on creation from the
    # opening's interior height, then becomes a plain user-editable
    # number. The auto rule lives in the operator that creates the
    # item, not here, so changing the rule later doesn't migrate
    # existing data.
    # ADJUSTABLE_SHELF: auto-recomputed from opening height every recalc
    # while unlocked is False. Set unlock_shelf_qty to True to pin a
    # specific count and stop the auto-recompute.
    shelf_qty: IntProperty(
        name="Shelf Qty", default=1, min=0, max=20,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_shelf_qty: BoolProperty(
        name="Unlock Shelf Qty",
        description="When on, hold the shelf count at the value above instead of auto-computing it from the opening's height",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    # ACCESSORY: free-text label (e.g., 'Lazy Susan', 'Trash Pullout').
    accessory_label: StringProperty(
        name="Accessory Label", default="Accessory",
        update=_update_cabinet_dim,
    )  # type: ignore


class Face_Frame_Opening_Props(PropertyGroup):
    """Per-opening state for face frame cabinets. Attached to each
    opening's cage object as bpy.types.Object.face_frame_opening.

    A bay starts with one opening filling its face frame opening.
    Splitter operations subdivide a bay by adding more openings to it.

    Each opening carries its front type and per-side overlay overrides.
    Unlocked overlays use the opening's own value; locked overlays fall
    back to the cabinet-level default (Face_Frame_Cabinet_Props.default_*_overlay).
    """

    opening_index: IntProperty(
        name="Opening Index",
        description="Position in the parent bay's opening list (0-based)",
        default=0,
    )  # type: ignore

    # Size along the parent split's axis (height when parent is an
    # H-split, width when parent is a V-split). Meaningful only when
    # this opening is a child of a Face_Frame_Split node; ignored when
    # the opening is the bay's root tree node. Behaves like
    # Face_Frame_Bay_Props.width: equally redistributed by default,
    # held during redistribution when unlocked.
    size: FloatProperty(
        name="Size", default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_size: BoolProperty(
        name="Unlock Size",
        description="Hold this opening's size during gang-construction redistribution",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    FRONT_TYPE_ITEMS = [
        ('NONE', "None", "No front (open shelving)"),
        ('DOOR', "Door", "Hinged door"),
        ('DRAWER_FRONT', "Drawer Front", "Drawer front"),
        ('PULLOUT', "Pullout", "Door front on a pullout slide; supports pullout accessories"),
        ('FALSE_FRONT', "False Front", "Decorative drawer-style panel; fixed (does not open)"),
    ]
    front_type: EnumProperty(
        name="Front Type", items=FRONT_TYPE_ITEMS, default='NONE',
        update=_update_front_type,
    )  # type: ignore

    HINGE_SIDE_ITEMS = [
        ('LEFT', "Left", "Single door, hinged on the left edge"),
        ('RIGHT', "Right", "Single door, hinged on the right edge"),
        ('DOUBLE', "Double", "Pair of doors meeting in the middle, hinged on outer edges"),
        ('TOP', "Top", "Flip-up door, hinged on the top edge"),
        ('BOTTOM', "Bottom", "Flip-down door, hinged on the bottom edge"),
    ]
    hinge_side: EnumProperty(
        name="Hinge Side", items=HINGE_SIDE_ITEMS, default='RIGHT',
        update=_update_cabinet_dim,
    )  # type: ignore

    # Visual open state. 0 = closed, 1 = fully open. For DOOR / PULLOUT
    # with a vertical hinge it drives a swing rotation; for DRAWER_FRONT
    # and PULLOUT slide-out it drives a forward translation. The "fully
    # open" reference (max swing angle, max slide distance) lives in the
    # solver, not in props - they're construction constants for now and
    # become cabinet props later if customization is wanted.
    swing_percent: FloatProperty(
        name="Swing Percent",
        description="How far the door / drawer front is opened (0 = closed, 1 = fully open)",
        default=0.0, min=0.0, max=1.0,
        subtype='FACTOR', precision=2,
        update=_update_cabinet_dim,
    )  # type: ignore

    # Per-side overlay overrides. Used only when the matching unlock flag
    # is True; otherwise the cabinet-level default is applied.
    top_overlay: FloatProperty(
        name="Top Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    bottom_overlay: FloatProperty(
        name="Bottom Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    left_overlay: FloatProperty(
        name="Left Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_overlay: FloatProperty(
        name="Right Overlay", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    unlock_top_overlay: BoolProperty(
        name="Unlock Top Overlay",
        description="Use this opening's own top overlay value instead of the cabinet default",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    unlock_bottom_overlay: BoolProperty(
        name="Unlock Bottom Overlay",
        description="Use this opening's own bottom overlay value instead of the cabinet default",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    unlock_left_overlay: BoolProperty(
        name="Unlock Left Overlay",
        description="Use this opening's own left overlay value instead of the cabinet default",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    unlock_right_overlay: BoolProperty(
        name="Unlock Right Overlay",
        description="Use this opening's own right overlay value instead of the cabinet default",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    # Interior items: shelves, accessory labels, and (future) glass
    # shelves, half shelves, pullouts, tray dividers, rollouts. Order
    # in this collection is the visual order from bottom to top inside
    # the opening for items that stack (shelves); accessory labels
    # ignore order.
    interior_items: CollectionProperty(type=Face_Frame_Interior_Item)  # type: ignore
    interior_items_index: IntProperty(
        name="Active Interior Item Index", default=0, min=0,
    )  # type: ignore


class Face_Frame_Split_Props(PropertyGroup):
    """Per-split-node state. Attached to each split node Empty as
    bpy.types.Object.face_frame_split.

    Split nodes are internal nodes of the bay's opening tree; their
    children are either openings (leaves) or other split nodes. The
    split's axis dictates how the children are arranged: H = stacked
    vertically (children differ in Z), V = side by side (children
    differ in X). The split node is also a tree node itself, so it has
    its own size / unlock_size for the redistribution logic when it's
    a child of a parent split.
    """

    SPLIT_AXIS_ITEMS = [
        ('H', "Horizontal", "Children stacked vertically; mid rail between them"),
        ('V', "Vertical",   "Children side by side; mid stile between them"),
    ]
    axis: EnumProperty(
        name="Axis", items=SPLIT_AXIS_ITEMS, default='H',
        update=_update_cabinet_dim,
    )  # type: ignore

    size: FloatProperty(
        name="Size", default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_size: BoolProperty(
        name="Unlock Size",
        description="Hold this split's size during gang-construction redistribution",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    # Width of THIS split's mid rail / mid stile members. Initialized
    # from the cabinet's bay_mid_rail_width / bay_mid_stile_width when
    # the split is created; per-split override afterwards.
    splitter_width: FloatProperty(
        name="Splitter Width",
        description="Width of mid rails (H-split) or mid stiles (V-split) inside this split node",
        default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # Carcass part rendered BEHIND each splitter member. The KIND of
    # backing is implied by the split's axis: H-splits (mid rails)
    # always get a shelf; V-splits (mid stiles) always get a division.
    # The user just toggles whether one is present at all.
    add_backing: BoolProperty(
        name="Add Backing",
        description="Add a carcass shelf (H-split) or division (V-split) behind each splitter",
        default=True,
        update=_update_cabinet_dim,
    )  # type: ignore


# ---------------------------------------------------------------------------
# Main scene props
# ---------------------------------------------------------------------------
class Face_Frame_Scene_Props(PropertyGroup):
    """Scene-level face frame settings: defaults, library state, cabinet
    styles, and the library/options UI.
    """

    # ---- Selection mode (mirrors frameless) ----
    face_frame_selection_mode: EnumProperty(
        name="Face Frame Selection Mode",
        items=[
            ('Cabinets', "Cabinets", "Select cabinet roots"),
            ('Bays', "Bays", "Select bay cages"),
            ('Face Frame', "Face Frame", "Select face frame members (rails and stiles)"),
            ('Openings', "Openings", "Select opening cages"),
            ('Interiors', "Interiors", "Select interior parts"),
            ('Parts', "Parts", "Select all individual cuttable parts"),
        ],
        default='Cabinets',
        update=update_face_frame_selection_mode,
    )  # type: ignore
    face_frame_selection_mode_enabled: BoolProperty(
        name="Selection Mode Shading",
        description="When off, selection-mode highlighting is disabled: cages stay hidden and every part renders plain regardless of which mode is picked",
        default=True,
        update=update_face_frame_selection_mode,
    )  # type: ignore

    # ---- Top-level tabs ----
    face_frame_tabs: EnumProperty(
        name="Face Frame Tabs",
        items=[
            ('LIBRARY', "Library", "Library"),
            ('OPTIONS', "Options", "Options"),
        ],
        default='LIBRARY',
    )  # type: ignore

    # ---- Library section toggles ----
    show_cabinet_sizes: BoolProperty(name="Show Cabinet Sizes", default=True)  # type: ignore
    show_cabinet_library: BoolProperty(name="Show Cabinet Library", default=True)  # type: ignore
    show_corner_cabinet_library: BoolProperty(name="Show Corner Cabinet Library", default=False)  # type: ignore
    show_appliance_library: BoolProperty(name="Show Appliance Library", default=False)  # type: ignore
    show_part_library: BoolProperty(name="Show Part Library", default=False)  # type: ignore
    show_user_library: BoolProperty(name="Show User Library", default=False)  # type: ignore

    # ---- Options section toggles ----
    show_cabinet_styles: BoolProperty(name="Show Cabinet Styles", default=False)  # type: ignore
    show_general_options: BoolProperty(name="Show General Options", default=False)  # type: ignore
    show_face_frame_options: BoolProperty(name="Show Face Frame Options", default=False)  # type: ignore
    show_handle_options: BoolProperty(name="Show Handle Options", default=False)  # type: ignore
    show_front_options: BoolProperty(name="Show Front Options", default=False)  # type: ignore
    show_drawer_options: BoolProperty(name="Show Drawer Options", default=False)  # type: ignore
    show_countertop_options: BoolProperty(name="Show Countertop Options", default=False)  # type: ignore

    # ---- Cabinet styles collection ----
    cabinet_styles: CollectionProperty(type=Face_Frame_Cabinet_Style)  # type: ignore
    active_cabinet_style_index: IntProperty(name="Active Cabinet Style Index", default=0)  # type: ignore

    # ---- Default placement behaviour ----
    fill_cabinets: BoolProperty(
        name="Fill Cabinets",
        description="When dropping a cabinet, fill the available space",
        default=True,
    )  # type: ignore

    # ---- Cabinet sizes ----
    default_top_cabinet_clearance: FloatProperty(
        name="Default Top Cabinet Clearance",
        description="Clearance to hold top cabinets from ceiling",
        default=units.inch(12.0),
        unit='LENGTH',
        precision=4,
        update=update_top_cabinet_clearance,
    )  # type: ignore

    default_wall_cabinet_location: FloatProperty(
        name="Default Wall Cabinet Location",
        description="Distance from floor to bottom of wall cabinet",
        default=units.inch(54.0),
        unit='LENGTH',
        precision=4,
        update=update_top_cabinet_clearance,
    )  # type: ignore

    default_cabinet_width: FloatProperty(
        name="Default Cabinet Width",
        description="Default width for cabinets when not filling",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    base_cabinet_depth: FloatProperty(
        name="Base Cabinet Depth",
        description="Default depth for base cabinets",
        default=units.inch(24.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    base_cabinet_height: FloatProperty(
        name="Base Cabinet Height",
        description="Default height for base cabinets",
        default=units.inch(34.5),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    tall_cabinet_depth: FloatProperty(
        name="Tall Cabinet Depth",
        description="Default depth for tall cabinets",
        default=units.inch(24.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    tall_cabinet_height: FloatProperty(
        name="Tall Cabinet Height",
        description="Default height for tall cabinets",
        default=units.inch(84.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    tall_cabinet_split_height: FloatProperty(
        name="Tall Cabinet Split Height",
        description="Height at which a tall cabinet is split into upper and lower sections",
        default=units.inch(54.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    upper_cabinet_depth: FloatProperty(
        name="Upper Cabinet Depth",
        description="Default depth for upper cabinets",
        default=units.inch(12.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    upper_cabinet_height: FloatProperty(
        name="Upper Cabinet Height",
        description="Default height for upper cabinets",
        default=units.inch(30.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    upper_top_stacked_cabinet_height: FloatProperty(
        name="Upper Top Stacked Cabinet Height",
        description="Height of the top section of a stacked upper cabinet",
        default=units.inch(12.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    # ---- Corner cabinet sizes ----
    base_inside_corner_size: FloatProperty(
        name="Base Inside Corner Size",
        description="Width and depth for inside base corner cabinets",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    tall_inside_corner_size: FloatProperty(
        name="Tall Inside Corner Size",
        description="Width and depth for inside tall corner cabinets",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    upper_inside_corner_size: FloatProperty(
        name="Upper Inside Corner Size",
        description="Width and depth for inside upper corner cabinets",
        default=units.inch(24.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    base_width_blind: FloatProperty(
        name="Base Width Blind",
        description="Default width for base blind corner cabinets",
        default=units.inch(48.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    tall_width_blind: FloatProperty(
        name="Tall Width Blind",
        description="Default width for tall blind corner cabinets",
        default=units.inch(48.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    upper_width_blind: FloatProperty(
        name="Upper Width Blind",
        description="Default width for upper blind corner cabinets",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    # ---- Appliance sizes ----
    refrigerator_height: FloatProperty(
        name="Refrigerator Height",
        description="Default refrigerator height",
        default=units.inch(62.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    refrigerator_cabinet_width: FloatProperty(
        name="Refrigerator Cabinet Width",
        description="Default refrigerator cabinet width",
        default=units.inch(38.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    range_width: FloatProperty(
        name="Range Width",
        description="Default range width",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    dishwasher_width: FloatProperty(
        name="Dishwasher Width",
        description="Default dishwasher width",
        default=units.inch(24.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    sink_cabinet_width: FloatProperty(
        name="Sink Cabinet Width",
        description="Default sink cabinet width",
        default=units.inch(36.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    oven_cabinet_width: FloatProperty(
        name="Oven Cabinet Width",
        description="Default oven cabinet width",
        default=units.inch(33.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    # ---- Face frame defaults (used by Phase 3 cabinet construction) ----
    ff_end_stile_width: FloatProperty(
        name="End Stile Width",
        description="Default end stile width",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    ff_top_rail_width: FloatProperty(
        name="Top Rail Width",
        description="Default top rail width",
        default=units.inch(1.5),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    ff_bottom_rail_width: FloatProperty(
        name="Bottom Rail Width",
        description="Default bottom rail width",
        default=units.inch(1.5),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    ff_mid_stile_width: FloatProperty(
        name="Mid Stile Width",
        description="Default mid stile width",
        default=units.inch(2.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    ff_face_frame_thickness: FloatProperty(
        name="Face Frame Thickness",
        description="Thickness of face frame members",
        default=units.inch(0.75),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    ff_door_overlay: FloatProperty(
        name="Default Door Overlay",
        description="Default amount the door overlays the face frame",
        default=units.inch(0.5),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    # =====================================================================
    # UI: cabinet sizes section
    # =====================================================================
    def draw_cabinet_sizes_ui(self, layout, context):
        unit_settings = context.scene.unit_settings

        row = layout.row()
        row.label(text="Top Cabinet Clearance:")
        row.prop(self, 'default_top_cabinet_clearance', text="")
        row.operator('hb_face_frame.update_cabinet_sizes', text="", icon='FILE_REFRESH')

        row = layout.row()
        row.label(text="Upper Cabinet Dim to Floor:")
        row.prop(self, 'default_wall_cabinet_location', text="")
        row.label(text="", icon='BLANK1')

        row = layout.row()
        row.label(text="Sizes")
        row.label(text="Base")
        row.label(text="Tall")
        row.label(text="Upper")

        row = layout.row()
        row.label(text="Depth:")
        row.prop(self, 'base_cabinet_depth', text="")
        row.prop(self, 'tall_cabinet_depth', text="")
        row.prop(self, 'upper_cabinet_depth', text="")

        row = layout.row()
        row.label(text="Height:")
        row.prop(self, 'base_cabinet_height', text="")
        row.prop(self, 'tall_cabinet_height', text="")
        row.prop(self, 'upper_cabinet_height', text="")

        row = layout.row()
        row.label(text="Tall Split Height:")
        row.prop(self, 'tall_cabinet_split_height', text="")

        row = layout.row()
        row.label(text="Upper Stacked Top Height:")
        row.prop(self, 'upper_top_stacked_cabinet_height', text="")

        layout.separator()

        row = layout.row()
        row.prop(self, 'fill_cabinets', text="Fill Available Space")
        row.prop(self, 'default_cabinet_width', text="Default Width")

    # =====================================================================
    # UI: cabinet library section
    # =====================================================================
    def draw_cabinet_library_ui(self, layout, context):
        # (display_name, cabinet_name passed to operator, thumbnail_name)
        base_cabinets = [
            ("Door", "Base Door", "Base Door"),
            ("Door Drw", "Base Door Drw", "Base Door Drw"),
            ("Drawer", "Base Drawer", "Base Drw"),
            ("Lap Drawer", "Lap Drawer", "Lap Drw"),
        ]
        upper_and_tall_cabinets = [
            ("Upper", "Upper", "Upper"),
            ("Upper Stacked", "Upper Stacked", "Upper Stacked"),
            ("Tall", "Tall", "Tall"),
            ("Tall Stacked", "Tall Stacked", "Tall Stacked"),
        ]

        layout.label(text="Base Cabinets:")
        flow = layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in base_cabinets:
            box = flow.box()
            box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            op = box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

        layout.label(text="Upper & Tall Cabinets:")
        flow = layout.grid_flow(row_major=True, columns=4, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in upper_and_tall_cabinets:
            box = flow.box()
            box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            op = box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

    # =====================================================================
    # UI: corner cabinet library
    # =====================================================================
    def draw_corner_cabinet_library_ui(self, layout, context):
        row = layout.row()
        row.label(text="Corner Cabinet Sizes")
        row = layout.row()
        row.prop(self, 'base_inside_corner_size', text="Base")
        row.prop(self, 'tall_inside_corner_size', text="Tall")
        row.prop(self, 'upper_inside_corner_size', text="Upper")

        layout.label(text="Pie Cut Corner")
        piecut_cabinets = [
            ("Base", "Pie Cut Corner Base", "Frameless Base Corner"),
            ("Tall", "Pie Cut Corner Tall", "Frameless Tall Corner"),
            ("Upper", "Pie Cut Corner Upper", "Frameless Upper Corner"),
        ]
        flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in piecut_cabinets:
            cab_box = flow.box()
            cab_box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                cab_box.template_icon(icon_value=icon_id, scale=4.0)
            op = cab_box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

        layout.label(text="Diagonal Corner")
        diagonal_cabinets = [
            ("Base", "Diagonal Corner Base", "Frameless Base Corner"),
            ("Tall", "Diagonal Corner Tall", "Frameless Tall Corner"),
            ("Upper", "Diagonal Corner Upper", "Frameless Upper Corner"),
        ]
        flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in diagonal_cabinets:
            cab_box = flow.box()
            cab_box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                cab_box.template_icon(icon_value=icon_id, scale=4.0)
            op = cab_box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

        layout.separator()
        row = layout.row()
        row.label(text="Blind Corner Widths")
        row = layout.row()
        row.prop(self, 'base_width_blind', text="Base")
        row.prop(self, 'tall_width_blind', text="Tall")
        row.prop(self, 'upper_width_blind', text="Upper")

    # =====================================================================
    # UI: appliance library
    # =====================================================================
    def draw_appliance_library_ui(self, layout, context):
        row = layout.row()
        row.label(text="Refrigerator Height")
        row.prop(self, 'refrigerator_height', text="")

        row = layout.row()
        row.label(text="Widths")
        row = layout.row()
        row.prop(self, 'refrigerator_cabinet_width', text="Refrigerator")
        row = layout.row()
        row.prop(self, 'dishwasher_width', text="Dishwasher")
        row.prop(self, 'range_width', text="Range")
        row = layout.row()
        row.prop(self, 'sink_cabinet_width', text="Sink")
        row.prop(self, 'oven_cabinet_width', text="Oven")

        appliance_cabinets = [
            ("Sink", "Sink Cabinet", "Sink Cabinet"),
            ("Fridge Cab", "Refrigerator Cabinet", "Refrigerator Frameless Cabinet"),
            ("Dishwasher", "Dishwasher", "Dishwasher"),
            ("Range", "Range", "Range"),
            ("Range Hood", "Range Hood", "Range Hood"),
            ("Refrigerator", "Refrigerator", "Refrigerator"),
        ]

        flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in appliance_cabinets:
            app_box = flow.box()
            app_box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                app_box.template_icon(icon_value=icon_id, scale=4.0)
            op = app_box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

    # =====================================================================
    # UI: parts & misc library
    # =====================================================================
    def draw_part_library_ui(self, layout, context):
        parts = [
            ("Floating Shelves", "Floating Shelves", "Floating Shelves"),
            ("Valance", "Valance", "Valance"),
            ("Applied Panel", "Applied Panel", "Panel"),
            ("Half Wall", "Half Wall", "Half Wall"),
            ("Leg", "Leg", "Leg"),
            ("Misc Part", "Misc Part", "Misc Part"),
        ]

        flow = layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)
        for display_name, cabinet_name, thumb_name in parts:
            part_box = flow.box()
            part_box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(thumb_name)
            if icon_id:
                part_box.template_icon(icon_value=icon_id, scale=4.0)
            op = part_box.operator('hb_face_frame.draw_cabinet', text=display_name)
            op.cabinet_name = cabinet_name

    # =====================================================================
    # UI: user library (placeholder for Phase 5)
    # =====================================================================
    def draw_user_library_ui(self, layout, context):
        box = layout.box()
        box.label(text="User Library - coming in Phase 5", icon='INFO')
        box.label(text="Saved cabinet groups will appear here")

    # =====================================================================
    # UI: cabinet styles (Options tab, placeholder for Phase 4)
    # =====================================================================
    def draw_cabinet_styles_ui(self, layout, context):
        row = layout.row()
        row.template_list(
            "HB_UL_face_frame_cabinet_styles", "",
            self, "cabinet_styles",
            self, "active_cabinet_style_index",
            rows=3,
        )

        if self.cabinet_styles and self.active_cabinet_style_index < len(self.cabinet_styles):
            style = self.cabinet_styles[self.active_cabinet_style_index]
            box = layout.box()
            box.prop(style, 'name', text="Name")
            box.prop(style, 'wood_species', text="Wood")
            box.prop(style, 'door_overlay_type', text="Door Overlay")
            box.label(text="Full style settings coming in Phase 4", icon='INFO')
        else:
            box = layout.box()
            box.label(text="No cabinet styles defined", icon='INFO')

    # =====================================================================
    # UI: master draw entry point (called by view3d_sidebar)
    # =====================================================================
    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        # Tab selector
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, 'face_frame_tabs', 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, 'face_frame_tabs', 'OPTIONS', icon='PREFERENCES')

        if self.face_frame_tabs == 'LIBRARY':
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_cabinet_sizes', text="Cabinet Sizes",
                     icon='TRIA_DOWN' if self.show_cabinet_sizes else 'TRIA_RIGHT', emboss=False)
            if self.show_cabinet_sizes:
                self.draw_cabinet_sizes_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_cabinet_library', text="Cabinets",
                     icon='TRIA_DOWN' if self.show_cabinet_library else 'TRIA_RIGHT', emboss=False)
            if self.show_cabinet_library:
                self.draw_cabinet_library_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_corner_cabinet_library', text="Corner Cabinets",
                     icon='TRIA_DOWN' if self.show_corner_cabinet_library else 'TRIA_RIGHT', emboss=False)
            if self.show_corner_cabinet_library:
                self.draw_corner_cabinet_library_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_appliance_library', text="Appliances",
                     icon='TRIA_DOWN' if self.show_appliance_library else 'TRIA_RIGHT', emboss=False)
            if self.show_appliance_library:
                self.draw_appliance_library_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_part_library', text="Parts & Miscellaneous",
                     icon='TRIA_DOWN' if self.show_part_library else 'TRIA_RIGHT', emboss=False)
            if self.show_part_library:
                self.draw_part_library_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_user_library', text="User",
                     icon='TRIA_DOWN' if self.show_user_library else 'TRIA_RIGHT', emboss=False)
            if self.show_user_library:
                self.draw_user_library_ui(box, context)

        else:  # OPTIONS tab
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_cabinet_styles', text="Cabinet Styles",
                     icon='TRIA_DOWN' if self.show_cabinet_styles else 'TRIA_RIGHT', emboss=False)
            if self.show_cabinet_styles:
                self.draw_cabinet_styles_ui(box, context)

            box = col.box()
            box.label(text="Additional options sections will arrive with Phase 3-5 work.",
                      icon='INFO')

    # =====================================================================
    # Registration
    # =====================================================================
    @classmethod
    def register(cls):
        bpy.types.Scene.hb_face_frame = PointerProperty(
            name="Face Frame Props",
            description="Face Frame scene-level settings and library state",
            type=cls,
        )

    @classmethod
    def unregister(cls):
        if hasattr(bpy.types.Scene, 'hb_face_frame'):
            del bpy.types.Scene.hb_face_frame


# ---------------------------------------------------------------------------
# Module registration
# ---------------------------------------------------------------------------
classes = (
    Face_Frame_Cabinet_Style,
    HB_UL_face_frame_cabinet_styles,
    Face_Frame_Mid_Stile_Width,
    Face_Frame_Cabinet_Props,
    Face_Frame_Bay_Props,
    Face_Frame_Interior_Item,
    Face_Frame_Opening_Props,
    Face_Frame_Split_Props,
    Face_Frame_Scene_Props,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()

    # Object-level pointer properties: face frame cabinets and bays carry
    # their state on the cage object directly. Only objects that get tagged
    # by the construction code populate these.
    bpy.types.Object.face_frame_cabinet = PointerProperty(type=Face_Frame_Cabinet_Props)
    bpy.types.Object.face_frame_bay = PointerProperty(type=Face_Frame_Bay_Props)
    bpy.types.Object.face_frame_opening = PointerProperty(type=Face_Frame_Opening_Props)
    bpy.types.Object.face_frame_split = PointerProperty(type=Face_Frame_Split_Props)

    # Initialize preview collections so thumbnails load on first sidebar draw
    get_library_previews()
    get_cabinet_previews()


def unregister():
    if hasattr(bpy.types.Object, 'face_frame_split'):
        del bpy.types.Object.face_frame_split
    if hasattr(bpy.types.Object, 'face_frame_opening'):
        del bpy.types.Object.face_frame_opening
    if hasattr(bpy.types.Object, 'face_frame_bay'):
        del bpy.types.Object.face_frame_bay
    if hasattr(bpy.types.Object, 'face_frame_cabinet'):
        del bpy.types.Object.face_frame_cabinet

    _unregister_classes()
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
