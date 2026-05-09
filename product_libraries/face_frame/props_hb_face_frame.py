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


# Finish-end / back conditions. Module-level so both Cabinet_Props and
# Scene_Props can reference the same enum items list.
FIN_END_ITEMS = [
    ('UNFINISHED', "Unfinished", "Side is unfinished (against a wall or hidden)"),
    ('FINISHED', "Finished", "Side IS the outer face (3/4 stock)"),
    ('PANELED', "Paneled", "Applied panel with rails and stiles"),
    ('FALSE_FF', "False Face Frame", "Applied frame with non-working fronts"),
    ('WORKING_FF', "Working Face Frame", "Applied frame with working fronts"),
    ('BEADBOARD', "Beadboard", "Beadboard finished end"),
    ('SHIPLAP', "Shiplap", "Shiplap finished end"),
    ('FLUSH_X', "Finished Flush X Inches", "Finished strip running the front X inches of the side"),
]


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
    """Recompute the derived cabinet heights when either the top
    clearance or the wall cabinet location changes. Same callback is
    wired to default_top_cabinet_clearance and default_wall_cabinet_location
    since both formulas read both source props.

    Formulas:
        tall_cabinet_height  = ceiling - top_clearance
        upper_cabinet_height = ceiling - top_clearance - wall_location

    Ceiling height lives on scene.home_builder (the addon-wide scene
    props). Skip silently if it isn't present - the addon may not be
    fully registered yet during initial load.
    """
    if not hasattr(context.scene, 'home_builder'):
        return
    ceiling = context.scene.home_builder.ceiling_height
    self.tall_cabinet_height = ceiling - self.default_top_cabinet_clearance
    self.upper_cabinet_height = (ceiling
                                 - self.default_top_cabinet_clearance
                                 - self.default_wall_cabinet_location)


def update_face_frame_selection_mode(self, context):
    """Apply visibility highlighting for the active selection mode.

    Calls the hb_face_frame.toggle_mode operator which iterates all scene
    objects and highlights/dims them based on which mode is active.
    """
    bpy.ops.hb_face_frame.toggle_mode(search_obj_name="")


def update_include_drawer_boxes(self, context):
    """Toggle: rebuild every face frame cabinet so drawer boxes are added
    behind drawer/pullout fronts (when True) or removed (when False).

    Reuses the cabinet recalc path rather than walking children directly
    so drawer-box presence stays a derived consequence of front parts -
    one source of truth in _update_fronts_in_opening. Wrapped in
    suspend_recalc so a scene full of cabinets recalcs once per cabinet
    instead of once per intermediate prop write.
    """
    from . import types_face_frame
    with types_face_frame.suspend_recalc():
        for obj in context.scene.objects:
            if obj.get(types_face_frame.TAG_CABINET_CAGE):
                types_face_frame.recalculate_face_frame_cabinet(obj)


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


def _update_bay_kick_height(self, context):
    """Auto-lock-on-edit for Face_Frame_Bay_Props.kick_height.

    Mirrors _update_bay_width. Without this, _distribute_bay_kick_heights
    overwrites the user's edit on the recalc that fires from the prop
    update, because unlock_kick_height is still False at that point.
    Reuses _DISTRIBUTING_WIDTHS as the system-write guard since recalc
    already adds the cabinet id to it for the entire body.
    """
    from . import types_face_frame
    root = types_face_frame.find_cabinet_root(self.id_data)
    if root is None:
        return
    if id(root) in types_face_frame._DISTRIBUTING_WIDTHS:
        return  # system write - skip auto-lock and skip recalc
    if not self.unlock_kick_height:
        self.unlock_kick_height = True
    else:
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
            ('PANEL', "Panel", "Standalone face frame panel (no carcass)"),
        ],
        default='BASE',
    )  # type: ignore

    is_sink: BoolProperty(name="Is Sink Cabinet", default=False)  # type: ignore
    is_built_in_appliance: BoolProperty(name="Is Built-in Appliance", default=False)  # type: ignore
    is_double: BoolProperty(name="Is Stacked / Double", default=False)  # type: ignore

    left_finished_end_condition: EnumProperty(
        name="Left Finished End", items=FIN_END_ITEMS, default='UNFINISHED',
        update=_update_cabinet_dim,
    )  # type: ignore
    right_finished_end_condition: EnumProperty(
        name="Right Finished End", items=FIN_END_ITEMS, default='UNFINISHED',
        update=_update_cabinet_dim,
    )  # type: ignore
    back_finished_end_condition: EnumProperty(
        name="Back Finished End", items=FIN_END_ITEMS, default='UNFINISHED',
        update=_update_cabinet_dim,
    )  # type: ignore

    # Scribe = inset from the face frame outer face to the side panel
    # outer face. The solver multiplexes this against the finish end
    # condition (3/4 finished forces 0 since the side IS the outer face;
    # paneled reserves 3/4" for the panel; others use the typed value),
    # so this prop holds the user setpoint for the unfinished /
    # against-a-wall case (~1/2" typical, 0 for an adjacent cabinet).
    left_scribe: FloatProperty(
        name="Left Scribe", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_scribe: FloatProperty(
        name="Right Scribe", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # Exposure flags. Default True for testing - placement logic will
    # eventually compute these from neighbor / wall geometry and flip
    # them to False where a side is hidden against an adjacent cabinet
    # or wall. Drives the "Apply to All Exposed" bulk operator and
    # signals to the solver which sides need finished treatment.
    left_exposed: BoolProperty(name="Left Exposed", default=True)  # type: ignore
    right_exposed: BoolProperty(name="Right Exposed", default=True)  # type: ignore
    back_exposed: BoolProperty(name="Back Exposed", default=True)  # type: ignore

    # FLUSH_X writes a finished strip running the front X inches of the
    # side panel; per-side because adjacent-appliance widths can differ.
    # Back has no FLUSH_X by design.
    left_flush_x_amount: FloatProperty(
        name="Left Flush X Amount", default=units.inch(4),
        unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_flush_x_amount: FloatProperty(
        name="Right Flush X Amount", default=units.inch(4),
        unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # Applied-panel frame member sizes. Used when a side's finish type is
    # PANELED / FALSE_FF / WORKING_FF. panel_frame_auto=True (default)
    # asks the parts builder to compute widths from opening/cabinet
    # dimensions; turning it off uses the explicit values below. One set
    # per cabinet rather than per-side - builder style is uniform within
    # a cabinet in practice. Easy to split later if that doesn't hold.
    panel_frame_auto: BoolProperty(name="Auto Panel Frame Widths", default=True)  # type: ignore
    panel_top_rail_width: FloatProperty(
        name="Panel Top Rail Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
    panel_bottom_rail_width: FloatProperty(
        name="Panel Bottom Rail Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
    panel_stile_width: FloatProperty(
        name="Panel Stile Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore

    # Top scribe = amount the carcass top (top panel or stretchers) is
    # held down from the bay's top opening. Sides matching the held-down
    # top drop with it; sides flagged as the finished face stay
    # full-height to provide a visible end face. Type defaults are
    # seeded in create_cabinet_root: Upper 1/8", Tall 1/2", Base 0.
    top_scribe: FloatProperty(
        name="Top Scribe", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
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

    # End stile drops to the floor instead of stopping at the bay bottom,
    # filling the area beside the kick recess. Solver also forces this on
    # for FLUSH so the wide bottom rail butts into a full-height stile.
    extend_left_stile_to_floor: BoolProperty(
        name="Extend Left Stile To Floor", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_right_stile_to_floor: BoolProperty(
        name="Extend Right Stile To Floor", default=False,
        update=_update_cabinet_dim,
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
        name="Material Thickness", default=units.inch(0.5), unit='LENGTH', precision=4,
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
    # Mid-division panels are typically thinner than carcass sides /
    # tops / bottoms (1/2" plywood) - exposed as its own prop so it can
    # diverge from material_thickness without changing other parts.
    division_thickness: FloatProperty(
        name="Division Thickness", default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    finish_toe_kick_thickness: FloatProperty(
        name="Finish Toe Kick Thickness", default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    toe_kick_type: EnumProperty(
        name="Toe Kick Type",
        items=[
            ('NOTCH', "Notched Ends to Floor",
             "Sides extend to the floor with a front-bottom notch sized "
             "by toe_kick_height x toe_kick_setback"),
            ('FLUSH', "Flush (Wide Bottom Rail)",
             "No recess; the face frame's bottom rail extends to the floor"),
            ('FLOATING', "Floating",
             "Sides start above the floor by toe_kick_height; toe kick is a "
             "separate base assembly the cabinet sits on"),
        ],
        default='NOTCH',
        update=_update_cabinet_dim,
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
    # Raises the carcass back panel's bottom edge above the cabinet
    # floor by this amount. Default 0 leaves the back full-height
    # (current behavior); a positive value leaves the lower portion
    # open at the back, used by refrigerator cabinets so the fridge
    # zone is open both at the front (no door) and at the back.
    back_bottom_inset: FloatProperty(
        name="Back Bottom Inset", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    inset_toe_kick_left: FloatProperty(
        name="Inset Toe Kick Left", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    inset_toe_kick_right: FloatProperty(
        name="Inset Toe Kick Right", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    include_finish_toe_kick: BoolProperty(
        name="Include Finish Toe Kick", default=True,
        update=_update_cabinet_dim,
    )  # type: ignore

    include_external_nailer: BoolProperty(name="Include External Nailer", default=False)  # type: ignore
    include_internal_nailer: BoolProperty(name="Include Internal Nailer", default=False)  # type: ignore
    include_thin_finished_bottom: BoolProperty(name="Include 1/4 Finished Bottom", default=False)  # type: ignore
    include_thick_finished_bottom: BoolProperty(name="Include 3/4 Finished Bottom", default=False)  # type: ignore
    include_blocking: BoolProperty(name="Include Blocking", default=False)  # type: ignore

    # ---- Corner cabinet props (PIE_CUT / DIAGONAL / CORNER_DRAWER) and
    # angled standard cabinets ----
    # corner_type defaults to NONE on regular cabinets. left_depth and
    # right_depth serve two roles:
    #   - Corner cabinets: perpendicular stub-side lengths along each
    #     wall (always authoritative when corner_type != NONE).
    #   - Standard single-bay cabinets: per-side depths used when
    #     unlock_left_depth / unlock_right_depth is on, producing an
    #     angled face frame plane (face frame becomes the hypotenuse;
    #     back stays at cab_props.depth between the sides).
    # Width / depth tweaks propagate through recalc via
    # _update_cabinet_dim.
    corner_type: EnumProperty(
        name="Corner Type",
        items=[
            ('NONE', "None", "Not a corner cabinet"),
            ('PIE_CUT', "Pie Cut", "Pie cut corner cabinet"),
            ('DIAGONAL', "Diagonal", "Diagonal corner cabinet with angled front face"),
        ],
        default='NONE',
    )  # type: ignore
    left_depth: FloatProperty(
        name="Left Depth", default=units.inch(24.0),
        unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_depth: FloatProperty(
        name="Right Depth", default=units.inch(24.0),
        unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    # Angled standard cabinet unlocks. Single-bay only (UI hides them
    # when bay count > 1). When on, the matching left_depth / right_depth
    # drives that side's depth; when off, the side falls back to
    # cab_props.depth and the face frame stays square to the back.
    unlock_left_depth: BoolProperty(
        name="Unlock Left Depth", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_right_depth: BoolProperty(
        name="Unlock Right Depth", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore

    # ---- Pie cut corner options ----
    # exterior_option: door / front configuration on the L-front faces.
    # interior_option: rotating-shelf accessory inside the cabinet.
    # tray_compartment: optional partitioned tray storage on one side.
    # All three are wired to recalc but only the LEFT/RIGHT door-opens-
    # first variants currently affect geometry; the rest are UI stubs.
    exterior_option: EnumProperty(
        name="Exterior Option",
        items=[
            ('LEFT_DOOR_OPENS_FIRST',  "Left Door Opens First",  "Left door tucks behind right at the corner"),
            ('RIGHT_DOOR_OPENS_FIRST', "Right Door Opens First", "Right door tucks behind left at the corner"),
            ('BIFOLD_DOORS',           "Bi-fold Doors",          "Pair of bi-fold doors per face"),
            ('REVOLVING_DOORS',        "Revolving Doors",        "Door rotates with the susan inside"),
        ],
        default='LEFT_DOOR_OPENS_FIRST',
        update=_update_cabinet_dim,
    )  # type: ignore
    interior_option: EnumProperty(
        name="Interior Option",
        items=[
            ('NONE',               "None",                "No interior accessory"),
            ('KIDNEY_SUSANS',      "Kidney Susans",       "Kidney-shaped rotating shelves"),
            ('SUPER_SUSANS',       "Super Susans",        "Round rotating shelves on bearings"),
            ('NOT_SO_LAZY_SUSANS', "Not So Lazy Susans",  "Pan storage with hooks plus a lower tray"),
        ],
        default='NONE',
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_compartment: EnumProperty(
        name="Tray Compartment",
        items=[
            ('NONE',  "None",  "No tray compartment"),
            ('LEFT',  "Left",  "Tray compartment on the left side"),
            ('RIGHT', "Right", "Tray compartment on the right side"),
        ],
        default='NONE',
        update=_update_cabinet_dim,
    )  # type: ignore

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
        update=_update_bay_kick_height,
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

    remove_bottom: BoolProperty(
        name="Remove Bottom", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    remove_carcass: BoolProperty(
        name="Remove Carcass", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    # Per-bay override: when True this bay behaves as FLOATING regardless
    # of the cabinet's toe_kick_type. Sides under an end bay anchor at the
    # bay bottom rather than the floor, and kick subfront / finish kick
    # segments skip this bay. Bay kick_height is the lift amount.
    floating_bay: BoolProperty(
        name="Floating", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    apron_bay: BoolProperty(name="Apron Bay", default=False)  # type: ignore
    finish_bay: BoolProperty(name="Finish Bay", default=False)  # type: ignore

    # UI-only toggle: in the cabinet_prompts popup each bay shows just
    # its size by default; flipping this expands the bay's secondary
    # properties (kick height, top offset, rails, flags) inline. Per-
    # bay so each bay collapses independently.
    prompts_expanded: BoolProperty(
        name="Show More Bay Properties",
        description="Expand secondary properties for this bay in the cabinet prompts popup",
        default=False,
    )  # type: ignore

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
        ('INSET_PANEL', "Inset Panel", "1/4\" panel filling the face frame opening; no overlay, no swing"),
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
def _pull_category_enum_items(self, context):
    # Deferred import to avoid a circular dependency: pulls.py imports
    # this module for the thumbnail preview collection.
    from . import pulls
    return pulls.get_pull_categories()


def _pull_enum_items(self, context):
    """Items for door/drawer pull selection. Filtered to the currently
    chosen category. Real pulls come first (so the EnumProperty defaults
    to the first one) with 'NONE' appended at the end as an opt-out.
    """
    from . import pulls
    items = []
    cat = self.door_pull_category
    if cat != 'NONE':
        # Category id is uppercased; resolve back to on-disk folder name.
        real_cat = None
        for entry in pulls.get_pull_categories():
            if entry[0] == cat:
                real_cat = entry[1]
                break
        if real_cat is not None:
            items.extend(pulls.get_pulls_in_category(real_cat))
    items.append(('NONE', "None", "No pull"))
    return items


def _update_pulls_on_selection_change(self, context):
    """Selection change -> trigger recalc on every face frame cabinet
    so the new pull (or NONE) shows up. Cached pull objects are NOT
    invalidated here; the front-builder reloads from the new selection
    on its next pass.
    """
    from . import types_face_frame
    for obj in context.scene.objects:
        if obj.get(types_face_frame.TAG_CABINET_CAGE):
            types_face_frame.recalculate_face_frame_cabinet(obj)


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
    show_cabinet_library: BoolProperty(name="Show Standard Cabinets", default=True)  # type: ignore
    show_corner_cabinet_library: BoolProperty(name="Show Corner Cabinets", default=False)  # type: ignore
    show_appliance_library: BoolProperty(name="Show Appliance Products", default=False)  # type: ignore
    show_vanity_library: BoolProperty(name="Show Vanities", default=False)  # type: ignore
    show_part_library: BoolProperty(name="Show Parts", default=False)  # type: ignore
    show_specialty_bath_library: BoolProperty(name="Show Specialty Bath", default=False)  # type: ignore
    show_bedroom_bookcase_library: BoolProperty(name="Show Specialty Bedroom & Bookcases", default=False)  # type: ignore
    show_angled_library: BoolProperty(name="Show Angled", default=False)  # type: ignore
    show_misc_library: BoolProperty(name="Show Misc", default=False)  # type: ignore
    show_user_library: BoolProperty(name="Show User Library", default=False)  # type: ignore

    # ---- Options section toggles ----
    show_cabinet_styles: BoolProperty(name="Show Cabinet Styles", default=False)  # type: ignore
    show_finished_ends_options: BoolProperty(name="Show Finished Ends and Backs", default=False)  # type: ignore
    show_general_options: BoolProperty(name="Show General Options", default=False)  # type: ignore
    show_face_frame_options: BoolProperty(name="Show Face Frame Options", default=False)  # type: ignore
    show_handle_options: BoolProperty(name="Show Handle Options", default=False)  # type: ignore
    show_countertop_options: BoolProperty(name="Show Countertop Options", default=False)  # type: ignore
    show_drawer_box_options: BoolProperty(name="Show Drawer Box Options", default=False)  # type: ignore

    # ---- Drawer box defaults ----
    # include_drawer_boxes gates spawning of drawer boxes behind drawer
    # and pullout fronts; clearances are subtracted from the opening hole
    # to size each box. v1 keeps these scene-wide; per-front overrides
    # land when front parts grow editable per-part props.
    include_drawer_boxes: BoolProperty(
        name="Include Drawer Boxes",
        description="Spawn a drawer box behind every drawer and pullout front",
        default=True,
        update=update_include_drawer_boxes,
    )  # type: ignore
    drawer_box_side_clearance: FloatProperty(
        name="Drawer Box Side Clearance",
        description="Gap between each side of the drawer box and the opening",
        default=units.inch(0.5), unit='LENGTH', precision=4,
    )  # type: ignore
    drawer_box_top_clearance: FloatProperty(
        name="Drawer Box Top Clearance",
        description="Gap between the top of the drawer box and the opening top",
        default=units.inch(0.75), unit='LENGTH', precision=4,
    )  # type: ignore
    drawer_box_rear_clearance: FloatProperty(
        name="Drawer Box Rear Clearance",
        description="Gap between the back of the drawer box and the cabinet back",
        default=units.inch(1.0), unit='LENGTH', precision=4,
    )  # type: ignore
    drawer_box_bottom_clearance: FloatProperty(
        name="Drawer Box Bottom Clearance",
        description="Gap between the bottom of the drawer box and the opening bottom",
        default=units.inch(0.5), unit='LENGTH', precision=4,
    )  # type: ignore

    # ---- Finished Ends and Backs defaults ----
    # Drives the "Apply to All Exposed" bulk operator and seeds new
    # cabinets at create_cabinet_root time. Cabinet-level overrides
    # live on Face_Frame_Cabinet_Props.
    default_finished_end_type: EnumProperty(
        name="Default Finished End Type",
        items=FIN_END_ITEMS, default='FINISHED',
    )  # type: ignore
    default_scribe: FloatProperty(
        name="Default Scribe", default=units.inch(0.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
    default_flush_x_amount: FloatProperty(
        name="Default Flush X Amount", default=units.inch(4),
        unit='LENGTH', precision=4,
    )  # type: ignore
    default_panel_frame_auto: BoolProperty(
        name="Default Auto Panel Frame Widths", default=True,
    )  # type: ignore
    default_panel_top_rail_width: FloatProperty(
        name="Default Panel Top Rail Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
    default_panel_bottom_rail_width: FloatProperty(
        name="Default Panel Bottom Rail Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
    default_panel_stile_width: FloatProperty(
        name="Default Panel Stile Width", default=units.inch(1.5),
        unit='LENGTH', precision=4,
    )  # type: ignore
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

    countertop_thickness: FloatProperty(
        name="Countertop Thickness",
        description="Thickness of the countertop slab",
        default=units.inch(1.5),
        unit='LENGTH',
    )  # type: ignore

    countertop_overhang_front: FloatProperty(
        name="Countertop Front Overhang",
        description="Overhang past the front of cabinets",
        default=units.inch(1.0),
        unit='LENGTH',
    )  # type: ignore

    countertop_overhang_sides: FloatProperty(
        name="Countertop Side Overhang",
        description="Overhang past exposed ends of cabinets",
        default=units.inch(1.0),
        unit='LENGTH',
    )  # type: ignore

    countertop_overhang_back: FloatProperty(
        name="Countertop Back Overhang",
        description="Overhang past the back of cabinets toward wall",
        default=units.inch(0.0),
        unit='LENGTH',
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

    top_drawer_opening_height: FloatProperty(
        name="Top Drawer Opening Height",
        description="Height of the top drawer opening in base cabinet drawer presets (1 Drawer x Door, 3 Drawers, 4 Drawers, etc.)",
        default=units.inch(4.5),
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

    # ---- Pulls: scene-level selection ----
    door_pull_category: EnumProperty(
        name="Pull Category",
        items=_pull_category_enum_items,
    )  # type: ignore
    door_pull_selection: EnumProperty(
        name="Door Pull",
        items=_pull_enum_items,
        update=_update_pulls_on_selection_change,
    )  # type: ignore
    drawer_pull_selection: EnumProperty(
        name="Drawer Pull",
        items=_pull_enum_items,
        update=_update_pulls_on_selection_change,
    )  # type: ignore

    # Cached pull objects. Once the user picks a pull we load the .blend
    # once and link the same Object to every cabinet's pull instances.
    # Cleared / repopulated by the front-builder when selection or
    # category changes.
    current_door_pull_object: PointerProperty(type=bpy.types.Object)  # type: ignore
    current_drawer_pull_object: PointerProperty(type=bpy.types.Object)  # type: ignore

    # ---- Pulls: positioning controls ----
    # Door pulls measure horizontally from the unhinged edge of the door
    # (the side opposite the hinge). Drawer pulls use this offset as a
    # margin from one end when not centered.
    pull_horizontal_offset: FloatProperty(
        name="Pull Horizontal Offset",
        description="Distance from the door's unhinged edge to the pull's nearest edge",
        default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_pulls_on_selection_change,
    )  # type: ignore
    # Vertical placement is per cabinet zone:
    #   Base: distance from TOP of door down to pull (reach from above)
    #   Tall: distance from BOTTOM of door up to pull
    #   Upper: distance from BOTTOM of door up to pull (reach from below)
    pull_vertical_location_base: FloatProperty(
        name="Base Pull Vertical Location",
        default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_pulls_on_selection_change,
    )  # type: ignore
    pull_vertical_location_tall: FloatProperty(
        name="Tall Pull Vertical Location",
        default=units.inch(36.0), unit='LENGTH', precision=4,
        update=_update_pulls_on_selection_change,
    )  # type: ignore
    pull_vertical_location_upper: FloatProperty(
        name="Upper Pull Vertical Location",
        default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_pulls_on_selection_change,
    )  # type: ignore
    center_pulls_on_drawer_front: BoolProperty(
        name="Center Pulls on Drawer Front",
        default=True,
        update=_update_pulls_on_selection_change,
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

        # Tall and upper heights are derived from ceiling, top clearance,
        # and wall cabinet location - disable their fields so the user
        # edits the source values instead. Base height stays editable.
        row = layout.row()
        row.label(text="Height:")
        row.prop(self, 'base_cabinet_height', text="")
        sub = row.row()
        sub.enabled = False
        sub.prop(self, 'tall_cabinet_height', text="")
        sub = row.row()
        sub.enabled = False
        sub.prop(self, 'upper_cabinet_height', text="")

        row = layout.row()
        row.label(text="Tall Split Height:")
        row.prop(self, 'tall_cabinet_split_height', text="")

        row = layout.row()
        row.label(text="Top Drawer Opening Height:")
        row.prop(self, 'top_drawer_opening_height', text="")

        row = layout.row()
        row.label(text="Upper Stacked Top Height:")
        row.prop(self, 'upper_top_stacked_cabinet_height', text="")

        layout.separator()

        row = layout.row()
        row.prop(self, 'fill_cabinets', text="Fill Available Space")
        row.prop(self, 'default_cabinet_width', text="Default Width")

    # =====================================================================
    # UI: shared helper - draw a grid of catalog buttons
    # =====================================================================
    def _draw_catalog_grid(self, layout, products, columns=3):
        """Render a grid_flow of catalog buttons. `products` is an
        iterable of names; each name is used identically as the display
        label, the cabinet_name passed to draw_cabinet, and the
        thumbnail filename in face_frame_thumbnails/. Folding all three
        into one string keeps placeholder lists short - real renders
        and per-product dispatch routing can deviate later by switching
        to (display, cabinet_name, thumb_name) triples.
        """
        flow = layout.grid_flow(row_major=True, columns=columns,
                                even_columns=True, even_rows=True, align=True)
        for name in products:
            box = flow.box()
            box.scale_y = 0.9
            icon_id = load_cabinet_thumbnail(name)
            if icon_id:
                box.template_icon(icon_value=icon_id, scale=4.0)
            op = box.operator('hb_face_frame.draw_cabinet', text=name)
            op.cabinet_name = name

    # =====================================================================
    # UI: standard cabinet library
    # =====================================================================
    def draw_cabinet_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Base", "Tall", "Upper", "Upper Stacked",
            "Lap Drawer", "Floating Base Cabinet",
        ], columns=3)

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
        layout.separator()
        self._draw_catalog_grid(layout, [
            "Pie Cut Base", "Pie Cut Upper", "Pie Cut Drawer",
            "Diagonal Base", "Diagonal Upper", "Diagonal Tall",
        ], columns=2)
        layout.separator()
        row = layout.row()
        row.label(text="Blind Corner Widths")
        row = layout.row()
        row.prop(self, 'base_width_blind', text="Base")
        row.prop(self, 'tall_width_blind', text="Tall")
        row.prop(self, 'upper_width_blind', text="Upper")

    # =====================================================================
    # UI: appliance products library
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
        layout.separator()
        self._draw_catalog_grid(layout, [
            "Elevated Dishwasher", "Dishwasher", "Built in Tall",
            "Range", "Range Hood", "Standalone Refrigerator",
            "Refrigerator Cabinet", "Sink",
        ], columns=3)

    # =====================================================================
    # UI: vanities library
    # =====================================================================
    def draw_vanity_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Special", "Combination", "Deluxe",
        ], columns=3)

    # =====================================================================
    # UI: parts library
    # =====================================================================
    def draw_part_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Panel",
            "Loose Stile", "End Leg", "Intermediate Leg",
            "Vanity End Leg Assembly", "Vanity Support Leg",
            "Vanity Fixed Shelf", "Floating Shelves",
        ], columns=3)

    # =====================================================================
    # UI: specialty bath library
    # =====================================================================
    def draw_specialty_bath_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Recessed Medicine Cabinet", "Tri-View Medicine Cabinet",
            "Overstool", "Mirror Frame", "Tub Skirt",
        ], columns=2)

    # =====================================================================
    # UI: specialty bedroom & bookcases library
    # =====================================================================
    def draw_bedroom_bookcase_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Bookcase", "Bookcase Upper", "Bookcase Corner",
            "Bookcase Corner Upper", "Window Seat", "Dresser",
            "Night Stand",
        ], columns=2)

    # =====================================================================
    # UI: angled library
    # =====================================================================
    def draw_angled_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Angled Ends with Doors", "Double Angled Ends",
            "Angled Finished Ends",
        ], columns=2)

    # =====================================================================
    # UI: misc library
    # =====================================================================
    def draw_misc_library_ui(self, layout, context):
        self._draw_catalog_grid(layout, [
            "Half Wall", "Support Frame", "Face Frame and Doors",
            "X-Frame Ends",
        ], columns=2)

    # =====================================================================
    # UI: user library (placeholder for Phase 5)
    # =====================================================================
    def draw_user_library_ui(self, layout, context):
        box = layout.box()
        box.label(text="User Library - coming in Phase 5", icon='INFO')
        box.label(text="Saved cabinet groups will appear here")

    # =====================================================================
    # UI: pulls (Options tab)
    # =====================================================================
    def draw_finished_ends_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'default_finished_end_type', text="Type")
        col.separator()
        col.prop(self, 'default_scribe', text="Default Scribe")
        if self.default_finished_end_type == 'FLUSH_X':
            col.prop(self, 'default_flush_x_amount', text="Flush X Amount")
        col.separator()
        col.prop(self, 'default_panel_frame_auto', text="Auto Panel Frame Widths")
        if not self.default_panel_frame_auto:
            sub = col.column(align=True)
            sub.prop(self, 'default_panel_top_rail_width', text="Top Rail")
            sub.prop(self, 'default_panel_bottom_rail_width', text="Bottom Rail")
            sub.prop(self, 'default_panel_stile_width', text="Stile")
        col.separator()
        # The bulk operator walks every cabinet in the scene and writes
        # default_finished_end_type to any side flagged exposed. Type
        # only - scribe / flush_x / panel-frame defaults are read by the
        # solver per cabinet, so changing them here propagates without a
        # sweep.
        col.operator(
            "hb_face_frame.apply_finished_ends_to_exposed",
            text="Apply to All Exposed", icon='CHECKMARK',
        )

    def draw_pulls_ui(self, layout, context):
        from . import pulls

        col = layout.column(align=True)
        col.prop(self, 'door_pull_category', text="Category")

        # Door pull row + thumbnail beneath
        col.label(text="Door Pull:")
        col.prop(self, 'door_pull_selection', text="")
        if self.door_pull_selection not in ('NONE', ''):
            icon_id = pulls.load_pull_thumbnail_icon(
                self.door_pull_selection,
                pulls._resolve_real_category(self.door_pull_category),
            )
            if icon_id:
                col.template_icon(icon_value=icon_id, scale=4.0)

        col.separator()
        col.label(text="Drawer Pull:")
        col.prop(self, 'drawer_pull_selection', text="")
        if self.drawer_pull_selection not in ('NONE', ''):
            icon_id = pulls.load_pull_thumbnail_icon(
                self.drawer_pull_selection,
                pulls._resolve_real_category(self.door_pull_category),
            )
            if icon_id:
                col.template_icon(icon_value=icon_id, scale=4.0)

        col.separator()
        col.label(text="Position:")
        col.prop(self, 'pull_horizontal_offset', text="Horizontal Offset")
        col.prop(self, 'pull_vertical_location_base', text="Base Vertical")
        col.prop(self, 'pull_vertical_location_tall', text="Tall Vertical")
        col.prop(self, 'pull_vertical_location_upper', text="Upper Vertical")
        col.prop(self, 'center_pulls_on_drawer_front', text="Center Drawer Pulls")

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

            # Each section is one collapsible box; default state matches
            # the "Standard Cabinets open, rest closed" hierarchy of the
            # catalog. Order mirrors the canonical product-list order so
            # users can scan top-down.
            sections = [
                ('show_cabinet_library',          "Standard Cabinets",            self.draw_cabinet_library_ui),
                ('show_corner_cabinet_library',   "Corner Cabinets",              self.draw_corner_cabinet_library_ui),
                ('show_appliance_library',        "Appliance Products",           self.draw_appliance_library_ui),
                ('show_vanity_library',           "Vanities",                     self.draw_vanity_library_ui),
                ('show_part_library',             "Parts",                        self.draw_part_library_ui),
                ('show_specialty_bath_library',   "Specialty Bath",               self.draw_specialty_bath_library_ui),
                ('show_bedroom_bookcase_library', "Specialty Bedroom & Bookcases", self.draw_bedroom_bookcase_library_ui),
                ('show_angled_library',           "Angled",                       self.draw_angled_library_ui),
                ('show_misc_library',             "Misc",                         self.draw_misc_library_ui),
                ('show_user_library',             "User",                         self.draw_user_library_ui),
            ]
            for prop_name, label, draw_fn in sections:
                expanded = getattr(self, prop_name)
                box = col.box()
                row = box.row()
                row.alignment = 'LEFT'
                row.prop(self, prop_name, text=label,
                         icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT',
                         emboss=False)
                if expanded:
                    draw_fn(box, context)

        else:  # OPTIONS tab
            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_cabinet_styles', text="Cabinet Styles",
                     icon='TRIA_DOWN' if self.show_cabinet_styles else 'TRIA_RIGHT', emboss=False)
            if self.show_cabinet_styles:
                self.draw_cabinet_styles_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_finished_ends_options', text="Finished Ends and Backs",
                     icon='TRIA_DOWN' if self.show_finished_ends_options else 'TRIA_RIGHT', emboss=False)
            if self.show_finished_ends_options:
                self.draw_finished_ends_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_handle_options', text="Pulls",
                     icon='TRIA_DOWN' if self.show_handle_options else 'TRIA_RIGHT', emboss=False)
            if self.show_handle_options:
                self.draw_pulls_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_drawer_box_options', text="Drawer Boxes",
                     icon='TRIA_DOWN' if self.show_drawer_box_options else 'TRIA_RIGHT', emboss=False)
            if self.show_drawer_box_options:
                self.draw_drawer_box_ui(box, context)

            box = col.box()
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(self, 'show_countertop_options', text="Countertops",
                     icon='TRIA_DOWN' if self.show_countertop_options else 'TRIA_RIGHT', emboss=False)
            if self.show_countertop_options:
                self.draw_countertop_ui(box, context)

    # =====================================================================
    # UI: drawer boxes
    # =====================================================================
    def draw_drawer_box_ui(self, layout, context):
        from ... import hb_project
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_face_frame

        col = layout.column(align=True)
        col.prop(props, 'include_drawer_boxes', text="Include Drawer Boxes")

        col.separator()
        col.label(text="Clearances:")
        col.prop(props, 'drawer_box_side_clearance', text="Side")
        col.prop(props, 'drawer_box_top_clearance', text="Top")
        col.prop(props, 'drawer_box_bottom_clearance', text="Bottom")
        col.prop(props, 'drawer_box_rear_clearance', text="Rear")

    # =====================================================================
    # UI: countertops
    # =====================================================================
    def draw_countertop_ui(self, layout, context):
        from ... import hb_project
        main_scene = hb_project.get_main_scene()
        props = main_scene.hb_face_frame

        col = layout.column(align=True)
        col.prop(props, 'countertop_thickness', text="Thickness")
        col.prop(props, 'countertop_overhang_front', text="Front Overhang")
        col.prop(props, 'countertop_overhang_sides', text="Side Overhang")
        col.prop(props, 'countertop_overhang_back', text="Back Overhang")

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.3
        op = row.operator('hb_face_frame.add_countertops',
                          text="Add Countertops", icon='MESH_PLANE')
        op.selected_only = False
        row.operator('hb_face_frame.remove_countertops', text="", icon='X')

        row = layout.row(align=True)
        row.scale_y = 1.3
        op = row.operator('hb_face_frame.add_countertops',
                          text="Add to Selected", icon='RESTRICT_SELECT_OFF')
        op.selected_only = True

        layout.separator()

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_face_frame.countertop_boolean_cut',
                     text="Cut Hole (Select 2)", icon='MOD_BOOLEAN')

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
