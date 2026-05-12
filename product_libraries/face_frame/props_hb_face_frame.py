"""Face Frame product library - scene properties and library UI.

Phase 2 scaffolding: scene-level PropertyGroup, library presentation, and
section toggles. Construction logic and per-cabinet PropertyGroups land in
Phase 3 (types_face_frame.py).
"""
import bpy
import os
from contextlib import contextmanager
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
from . import finish_colors, wood_materials


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


def get_cabinet_group_category_items(self, context):
    """Dynamic enum items for the user library category dropdown. Indirect
    through the operators package so this module doesn't pull operator
    code in at import time."""
    from .operators import ops_library
    return ops_library.get_cabinet_group_categories()


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


def get_stain_color_enum_items(self, context):
    """Dynamic items for the stain color dropdown. Pulled fresh so newly
    saved custom colors show up without restart."""
    items = []
    colors = finish_colors.get_all_stain_colors()
    for i, name in enumerate(colors.keys()):
        is_custom = finish_colors.is_custom_color(name, 'stain')
        desc = f"Custom: {name}" if is_custom else name
        items.append((name, name, desc, i))
    if not items:
        items.append(('Natural', "Natural", "Natural", 0))
    return items


def get_paint_color_enum_items(self, context):
    """Dynamic items for the paint color dropdown."""
    items = []
    colors = finish_colors.get_all_paint_colors()
    for i, name in enumerate(colors.keys()):
        is_custom = finish_colors.is_custom_color(name, 'paint')
        desc = f"Custom: {name}" if is_custom else name
        items.append((name, name, desc, i))
    if not items:
        items.append(('Arctic White', "Arctic White", "Arctic White", 0))
    return items


def get_door_style_enum_items(self, context):
    """Dynamic items for the cabinet style's door / drawer-front pickers.
    Reads names from the shared door_styles pool on the scene props.
    """
    items = []
    ff = context.scene.hb_face_frame
    for i, ds in enumerate(ff.door_styles):
        items.append((ds.name, ds.name, ds.name, i))
    if not items:
        items.append(('NONE', "(none defined)", "No door styles defined", 0))
    return items


def update_custom_procedural_material(self, context):
    """Forward custom-procedural shader edits to the wood material module."""
    wood_materials.update_finish_material_custom_procedural(self)


# Suspend-propagation refcount. While > 0, _propagate_cabinet_style
# returns immediately - used to silence the storm of update callbacks
# that fire when one user action writes many style props in sequence
# (e.g. an overlay change writes 21 width props, each of which would
# otherwise re-propagate to the whole scene).
_PROPAGATE_SUSPEND_DEPTH = 0


@contextmanager
def suspend_propagate():
    """Refcounted context manager around _propagate_cabinet_style. Use
    around bulk style-prop writes to coalesce into a single explicit
    propagate at the outermost resume.
    """
    global _PROPAGATE_SUSPEND_DEPTH
    _PROPAGATE_SUSPEND_DEPTH += 1
    try:
        yield
    finally:
        _PROPAGATE_SUSPEND_DEPTH -= 1


def _propagate_cabinet_style(self, context):
    """Push this cabinet style's current state to every face frame
    cabinet in the scene tagged with STYLE_NAME == self.name. Wired
    as the update callback on every cabinet-style prop that affects
    cabinet geometry / appearance, so changes in the style panel
    reflect across the scene without needing an explicit Update
    Cabinets click.

    Returns immediately under suspend_propagate(); callers performing
    bulk writes (update_face_frame_sizes' overlay sweep) hold the
    suspend through the inner setattrs and call propagate explicitly
    once at the end.

    Wrapped in suspend_recalc(): each assign_style_to_cabinet ends
    with an explicit recalculate_face_frame_cabinet call; under the
    outer suspend those recalcs queue by name and drain once at
    exit, so we get one recalc per cabinet (not one per assign step
    per cabinet) when a single style change sweeps through the scene.
    """
    if _PROPAGATE_SUSPEND_DEPTH > 0:
        return
    from . import types_face_frame
    target_name = self.name
    with types_face_frame.suspend_recalc():
        for obj in context.scene.objects:
            if (obj.get('IS_FACE_FRAME_CABINET_CAGE')
                    and obj.get('STYLE_NAME') == target_name):
                self.assign_style_to_cabinet(obj)


def _propagate_door_style(self, context):
    """Push this door style's current state to every front tagged with
    DOOR_STYLE_NAME == self.name. Same pattern as the cabinet style
    propagator: edits in the door style panel reflect across every
    front using that style without a button press.
    """
    target_name = self.name
    for obj in context.scene.objects:
        if obj.get('DOOR_STYLE_NAME') == target_name:
            self.assign_style_to_front(obj)


def update_face_frame_sizes(self, context):
    """door_overlay_type change handler. Writes new widths into every
    locked rail cell + every stile cell based on the overlay. Unlocked
    rails keep the user's value. The cabinet-side propagation (Update
    Cabinets op) is intentionally manual - this only rewrites style
    props, never touches scene cabinets.
    """
    defaults = self._FF_SIZE_DEFAULTS.get(
        self.door_overlay_type, self._FF_SIZE_DEFAULTS['CLASSIC'])

    # Each ff_*_width_* prop carries update=_propagate_cabinet_style,
    # which would re-propagate to every matching cabinet per setattr.
    # Suspend it for the bulk write and propagate ONCE at the end.
    with suspend_propagate():
        # Rails - only write the cell when its unlock flag is False.
        for row, key in (('top_rail', 'top'),
                         ('bottom_rail', 'bottom'),
                         ('mid_rail', 'mid')):
            base_in, tall_in, upper_in = defaults[row]
            if not getattr(self, f"unlock_base_{key}_rail"):
                setattr(self, f"ff_{row}_width_base", units.inch(base_in))
            if not getattr(self, f"unlock_tall_{key}_rail"):
                setattr(self, f"ff_{row}_width_tall", units.inch(tall_in))
            if not getattr(self, f"unlock_upper_{key}_rail"):
                setattr(self, f"ff_{row}_width_upper", units.inch(upper_in))

        # Stiles - always overlay-driven, no unlocks.
        for row in ('wall_stile', 'mid_stile', 'end_stile', 'blind_stile'):
            base_in, tall_in, upper_in = defaults[row]
            setattr(self, f"ff_{row}_width_base", units.inch(base_in))
            setattr(self, f"ff_{row}_width_tall", units.inch(tall_in))
            setattr(self, f"ff_{row}_width_upper", units.inch(upper_in))

    # One propagate now that the style is fully consistent.
    _propagate_cabinet_style(self, context)


def ensure_default_styles(context):
    """Make sure the scene carries at least one cabinet style and one
    door style. Operators that read from those collections call this
    on entry so the user never sees an empty-active state. Adds a
    Default cabinet style + Slab door style when empty; idempotent.
    """
    ff = context.scene.hb_face_frame
    if len(ff.cabinet_styles) == 0:
        cs = ff.cabinet_styles.add()
        cs.name = "Default"
        ff.active_cabinet_style_index = 0
    if len(ff.door_styles) == 0:
        ds = ff.door_styles.add()
        ds.name = "Default"
        ff.active_door_style_index = 0


def update_door_style_name(self, context):
    """Keep door style names unique within the shared collection."""
    main = context.scene.hb_face_frame
    base_name = self.name if self.name else "Door Style"
    existing = [s.name for s in main.door_styles if s != self]
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
    """Face frame cabinet style: wood species, finish color, interior
    material, door overlay, and references to a door style + drawer front
    style from the shared door_styles collection. Applied via
    assign_style_to_cabinet(), which writes the four overlay floats and
    inset depth onto the cabinet, assigns materials to every part, and
    walks fronts to apply the referenced door/drawer-front styles.
    """

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

    # ---- Wood / exterior material ----
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
            ('CUSTOM_PROCEDURAL', "Custom Procedural", "Procedural wood material with custom parameters"),
            ('CUSTOM', "Custom Material", "Use a custom material from the file"),
        ],
        default='MAPLE',
        update=_propagate_cabinet_style,
    )  # type: ignore

    stain_color: EnumProperty(
        name="Stain Color",
        description="Stain color for cabinet finish",
        items=get_stain_color_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    paint_color: EnumProperty(
        name="Paint Color",
        description="Paint color for cabinet finish",
        items=get_paint_color_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Interior material ----
    interior_material_type: EnumProperty(
        name="Interior Material",
        description="Material for cabinet interior",
        items=[
            ('MAPLE_PLY', "Maple Plywood", "Maple veneer plywood"),
            ('MATCHING', "Matching Exterior", "Use the same material as the exterior"),
            ('CUSTOM', "Custom Material", "Use a custom material from the file"),
        ],
        default='MAPLE_PLY',
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Door overlay (five face frame options) ----
    door_overlay_type: EnumProperty(
        name="Door Overlay",
        description="Door overlay style for face frame cabinets",
        items=[
            ('CLASSIC', "Classic", "Classic partial overlay"),
            ('TRANSITIONAL', "Transitional", "Transitional overlay"),
            ('FULL', "Full Overlay", "Full overlay"),
            ('PARTIAL_INSET', "Partial Inset", "Door is partially inset into the opening"),
            ('FULL_INSET', "Full Inset", "Door is fully inset, flush with the frame"),
        ],
        default='CLASSIC',
        update=update_face_frame_sizes,
    )  # type: ignore

    # ---- Face frame member widths (7 row types x 3 cabinet types) ----
    # Driven by door_overlay_type via update_face_frame_sizes. Rails have
    # per-cell unlock toggles so users can override the overlay default
    # for one cabinet type without losing the others. Stiles are always
    # overlay-driven (no unlock toggles). Defaults below match CLASSIC.
    ff_top_rail_width_base: FloatProperty(
        name="Top Rail (Base)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_top_rail_width_tall: FloatProperty(
        name="Top Rail (Tall)", default=units.inch(3.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_top_rail_width_upper: FloatProperty(
        name="Top Rail (Upper)", default=units.inch(3.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_bottom_rail_width_base: FloatProperty(
        name="Bottom Rail (Base)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_bottom_rail_width_tall: FloatProperty(
        name="Bottom Rail (Tall)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_bottom_rail_width_upper: FloatProperty(
        name="Bottom Rail (Upper)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_mid_rail_width_base: FloatProperty(
        name="Mid Rail (Base)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_mid_rail_width_tall: FloatProperty(
        name="Mid Rail (Tall)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_mid_rail_width_upper: FloatProperty(
        name="Mid Rail (Upper)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_wall_stile_width_base: FloatProperty(
        name="Wall Stile (Base)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_wall_stile_width_tall: FloatProperty(
        name="Wall Stile (Tall)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_wall_stile_width_upper: FloatProperty(
        name="Wall Stile (Upper)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_mid_stile_width_base: FloatProperty(
        name="Mid Stile (Base)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_mid_stile_width_tall: FloatProperty(
        name="Mid Stile (Tall)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_mid_stile_width_upper: FloatProperty(
        name="Mid Stile (Upper)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_end_stile_width_base: FloatProperty(
        name="End Stile (Base)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_end_stile_width_tall: FloatProperty(
        name="End Stile (Tall)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_end_stile_width_upper: FloatProperty(
        name="End Stile (Upper)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    ff_blind_stile_width_base: FloatProperty(
        name="Blind Stile (Base)", default=units.inch(3.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_blind_stile_width_tall: FloatProperty(
        name="Blind Stile (Tall)", default=units.inch(3.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_blind_stile_width_upper: FloatProperty(
        name="Blind Stile (Upper)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Rail unlock toggles (9: 3 row types x 3 cabinet types) ----
    # When False (locked), the rail's width follows the overlay default
    # and gets rewritten on overlay change. When True (unlocked), the
    # user's value persists across overlay changes.
    unlock_base_top_rail: BoolProperty(name="Unlock Base Top Rail", default=False)  # type: ignore
    unlock_tall_top_rail: BoolProperty(name="Unlock Tall Top Rail", default=False)  # type: ignore
    unlock_upper_top_rail: BoolProperty(name="Unlock Upper Top Rail", default=False)  # type: ignore
    unlock_base_bottom_rail: BoolProperty(name="Unlock Base Bottom Rail", default=False)  # type: ignore
    unlock_tall_bottom_rail: BoolProperty(name="Unlock Tall Bottom Rail", default=False)  # type: ignore
    unlock_upper_bottom_rail: BoolProperty(name="Unlock Upper Bottom Rail", default=False)  # type: ignore
    unlock_base_mid_rail: BoolProperty(name="Unlock Base Mid Rail", default=False)  # type: ignore
    unlock_tall_mid_rail: BoolProperty(name="Unlock Tall Mid Rail", default=False)  # type: ignore
    unlock_upper_mid_rail: BoolProperty(name="Unlock Upper Mid Rail", default=False)  # type: ignore

    # ---- Door / drawer-front style refs (by name into Face_Frame_Scene_Props.door_styles) ----
    door_style: EnumProperty(
        name="Door Style",
        description="Door style applied to door fronts on cabinets carrying this style",
        items=get_door_style_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    drawer_front_style: EnumProperty(
        name="Drawer Front Style",
        description="Door style applied to drawer fronts on cabinets carrying this style",
        items=get_door_style_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Cached materials (lazy-loaded from face_frame_assets/materials/cabinet_material.blend) ----
    material: PointerProperty(name="Material", type=bpy.types.Material)  # type: ignore
    material_rotated: PointerProperty(name="Material Rotated", type=bpy.types.Material)  # type: ignore
    interior_material: PointerProperty(name="Interior Material", type=bpy.types.Material)  # type: ignore
    interior_material_rotated: PointerProperty(name="Interior Material Rotated", type=bpy.types.Material)  # type: ignore
    custom_material: PointerProperty(name="Custom Exterior Material", type=bpy.types.Material, update=_propagate_cabinet_style)  # type: ignore
    custom_interior_material: PointerProperty(name="Custom Interior Material", type=bpy.types.Material, update=_propagate_cabinet_style)  # type: ignore

    # ---- Custom procedural shader (active when wood_species == 'CUSTOM_PROCEDURAL') ----
    custom_wood_color_1: bpy.props.FloatVectorProperty(
        name="Wood Color 1", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.8, 0.65, 0.45), update=update_custom_procedural_material)  # type: ignore
    custom_wood_color_2: bpy.props.FloatVectorProperty(
        name="Wood Color 2", subtype='COLOR', size=3, min=0.0, max=1.0,
        default=(0.6, 0.45, 0.3), update=update_custom_procedural_material)  # type: ignore
    custom_noise_scale_1: FloatProperty(name="Noise Scale 1", default=3.5, min=0.0, max=50.0, update=update_custom_procedural_material)  # type: ignore
    custom_noise_scale_2: FloatProperty(name="Noise Scale 2", default=2.5, min=0.0, max=50.0, update=update_custom_procedural_material)  # type: ignore
    custom_texture_variation_1: FloatProperty(name="Texture Variation 1", default=0.1, min=0.0, max=20.0, update=update_custom_procedural_material)  # type: ignore
    custom_texture_variation_2: FloatProperty(name="Texture Variation 2", default=12.5, min=0.0, max=20.0, update=update_custom_procedural_material)  # type: ignore
    custom_noise_detail: FloatProperty(name="Noise Detail", default=15.0, min=0.0, max=20.0, update=update_custom_procedural_material)  # type: ignore
    custom_voronoi_detail_1: FloatProperty(name="Voronoi Detail 1", default=0.0, min=0.0, max=10.0, update=update_custom_procedural_material)  # type: ignore
    custom_voronoi_detail_2: FloatProperty(name="Voronoi Detail 2", default=0.2, min=0.0, max=10.0, update=update_custom_procedural_material)  # type: ignore
    custom_knots_scale: FloatProperty(name="Knots Scale", default=0.0, min=0.0, max=20.0, update=update_custom_procedural_material)  # type: ignore
    custom_knots_darkness: FloatProperty(name="Knots Darkness", default=0.0, min=0.0, max=1.0, update=update_custom_procedural_material)  # type: ignore
    custom_roughness: FloatProperty(name="Roughness", default=1.0, min=0.0, max=1.0, update=update_custom_procedural_material)  # type: ignore
    custom_noise_bump_strength: FloatProperty(name="Noise Bump Strength", default=0.1, min=0.0, max=1.0, update=update_custom_procedural_material)  # type: ignore
    custom_knots_bump_strength: FloatProperty(name="Knots Bump Strength", default=0.15, min=0.0, max=1.0, update=update_custom_procedural_material)  # type: ignore
    custom_wood_bump_strength: FloatProperty(name="Wood Bump Strength", default=0.2, min=0.0, max=1.0, update=update_custom_procedural_material)  # type: ignore
    show_custom_grain_options: BoolProperty(name="Show Grain Options", default=False)  # type: ignore

    show_advanced_color: BoolProperty(
        name="Show Advanced Color Options",
        description="Show advanced shader parameters for color editing",
        default=False,
    )  # type: ignore

    show_face_frame_sizes: BoolProperty(
        name="Show Face Frame Sizes",
        description="Show the face frame sizes grid (top/bottom/mid rail and stile widths per cabinet type)",
        default=False,
    )  # type: ignore

    # =================================================================
    # Material resolution
    # =================================================================
    def _get_material_blend_path(self):
        return os.path.join(
            os.path.dirname(__file__),
            'face_frame_assets', 'materials', 'cabinet_material.blend',
        )

    def get_finish_material(self):
        """Return (material, material_rotated) for the exterior finish.

        CUSTOM returns the user-picked material as-is for both slots.
        CUSTOM_PROCEDURAL + named species lazy-load 'Wood' from the
        face frame material blend, then forward to wood_materials for
        node-graph updates based on the current species / colors.
        """
        if self.wood_species == 'CUSTOM':
            if self.custom_material:
                return self.custom_material, self.custom_material
            return None, None

        if not self.material or not self.material_rotated:
            with bpy.data.libraries.load(self._get_material_blend_path()) as (data_from, data_to):
                data_to.materials = ["Wood"]
            mat = data_to.materials[0]
            mat.name = self.name + " Finish"
            self.material = mat
            rotated = mat.copy()
            rotated.name = mat.name + " ROTATED"
            self.material_rotated = rotated

        if self.wood_species == 'CUSTOM_PROCEDURAL':
            wood_materials.update_finish_material_custom_procedural(self)
        else:
            wood_materials.update_finish_material(self)
        return self.material, self.material_rotated

    def get_interior_material(self):
        """Return (material, material_rotated) for the interior surfaces."""
        if self.interior_material_type == 'CUSTOM':
            if self.custom_interior_material:
                return self.custom_interior_material, self.custom_interior_material
            return None, None
        if self.interior_material_type == 'MATCHING':
            return self.get_finish_material()

        if not self.interior_material or not self.interior_material_rotated:
            with bpy.data.libraries.load(self._get_material_blend_path()) as (data_from, data_to):
                data_to.materials = ["Wood"]
            mat = data_to.materials[0]
            mat.name = self.name + " Interior"
            self.interior_material = mat
            rotated = mat.copy()
            rotated.name = mat.name + " ROTATED"
            self.interior_material_rotated = rotated
        return self.interior_material, self.interior_material_rotated

    # =================================================================
    # Apply style to a cabinet
    # =================================================================
    # overlay -> row_type -> (base, tall, upper) widths in inches.
    # Used by update_face_frame_sizes when door_overlay_type changes.
    # All values are inches; conversion to meters happens in the
    # callback. Tables mirror the Pulito Spaces defaults.
    _FF_SIZE_DEFAULTS = {
        'CLASSIC': {
            'top_rail':    (1.5, 3.5, 3.5),
            'bottom_rail': (1.5, 1.5, 1.5),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (2.0, 2.0, 2.0),
            'mid_stile':   (2.0, 2.0, 2.0),
            'end_stile':   (2.0, 2.0, 2.0),
            'blind_stile': (3.0, 3.0, 2.0),
        },
        'TRANSITIONAL': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (2.0, 2.0, 2.0),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
        },
        'FULL': {
            'top_rail':    (1.125, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.125),
            'mid_rail':    (2.0, 2.0, 2.0),
            'wall_stile':  (2.5, 2.5, 2.5),
            'mid_stile':   (2.25, 2.25, 2.25),
            'end_stile':   (1.25, 1.25, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
        },
        'PARTIAL_INSET': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
        },
        'FULL_INSET': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
        },
    }

    # door_overlay_type -> (L, R, T, B) overlay reveals in inches. Pure
    # overlay (CLASSIC / TRANSITIONAL / FULL) sits in front of the face
    # frame; inset is computed separately in assign_style_to_cabinet
    # because it scales with door thickness.
    _OVERLAY_TABLE = {
        'CLASSIC':       (0.5,    0.5,    0.5,    0.5),
        'TRANSITIONAL':  (0.625,  0.625,  0.875,  0.875),
        'FULL':          (1.0,    1.0,    0.875,  0.875),
        'PARTIAL_INSET': (0.5,    0.5,    0.5,    0.5),
        'FULL_INSET':    (-0.125, -0.125, -0.125, -0.125),
    }

    def assign_style_to_cabinet(self, cabinet_obj):
        """Write the style's overlay floats + inset amount onto the cabinet
        and recalc. Material assignment to parts and door-style application
        to fronts ship in the next phase, once Face_Frame_Door_Style and
        the per-part material rules are in place.
        """
        l, r, t, b = self._OVERLAY_TABLE.get(
            self.door_overlay_type, self._OVERLAY_TABLE['CLASSIC'])
        props = cabinet_obj.face_frame_cabinet
        props.default_left_overlay = units.inch(l)
        props.default_right_overlay = units.inch(r)
        props.default_top_overlay = units.inch(t)
        props.default_bottom_overlay = units.inch(b)

        # Inset depth scales with door thickness so non-standard
        # doors land correctly. FULL_INSET makes the outer face flush
        # with the face frame; PARTIAL_INSET sits halfway between
        # flush and the standard overlay position. The 0.125 magic
        # number must stay in sync with DOOR_TO_FRAME_GAP in
        # solver_face_frame.py.
        door_thickness = props.door_thickness
        door_to_frame_gap = units.inch(0.125)
        full_inset = door_thickness + door_to_frame_gap
        if self.door_overlay_type == 'FULL_INSET':
            props.default_door_inset_amount = full_inset
        elif self.door_overlay_type == 'PARTIAL_INSET':
            props.default_door_inset_amount = full_inset / 2.0
        else:
            props.default_door_inset_amount = 0.0

        cabinet_obj['STYLE_NAME'] = self.name

        # Push face frame widths to the cabinet BEFORE recalc so the
        # carcass rebuild picks up the new stile/rail dimensions.
        # Pulito-style: assign overwrites whatever the user had per-
        # cabinet; Update Cabinets re-runs this for every cabinet
        # tagged with this style.
        self._apply_face_frame_sizes_to_cabinet(cabinet_obj)

        # Materials -> deferred to next phase.

        # Recalc rebuilds carcass + fronts; its tail hook
        # (_reapply_cabinet_style_to_fronts) reads STYLE_NAME on the
        # root and re-runs _apply_door_styles_to_fronts, so every
        # recalc keeps door styles applied without each caller having
        # to re-trigger it.
        from . import types_face_frame
        types_face_frame.recalculate_face_frame_cabinet(cabinet_obj)

    # =================================================================
    # Material walking
    # =================================================================
    # Visible exterior surfaces (finish material on top + bottom + edges).
    _FINISH_EXTERIOR_ROLES = {
        # Face frame members
        'TOP_RAIL', 'BOTTOM_RAIL', 'LEFT_STILE', 'RIGHT_STILE', 'MID_STILE',
        'MID_RAIL', 'BAY_MID_RAIL', 'BAY_MID_STILE',
        # Fronts
        'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT', 'INSET_PANEL',
        # Visible toe kick parts
        'FINISH_TOE_KICK', 'LEFT_CORNER_FINISH_KICK', 'RIGHT_CORNER_FINISH_KICK',
        'LEFT_KICK_RETURN', 'RIGHT_KICK_RETURN',
        # Blind ends + finished back + flush skins / decorative panels
        'BLIND_PANEL_LEFT', 'BLIND_PANEL_RIGHT',
        'FINISHED_BACK', 'FLUSH_X', 'BEADBOARD', 'SHIPLAP',
    }

    # Hidden surfaces (interior material on top + bottom + edges).
    # Sides land here for v1; the .75 FINISHED end-condition case where
    # a side panel is the visible exterior is a follow-up.
    _INTERIOR_PART_ROLES = {
        # Carcass (LEFT_SIDE / RIGHT_SIDE handled separately in
        # _apply_materials_to_cabinet because their material depends on
        # the per-side finished_end_condition, not the role alone)
        'TOP', 'BOTTOM',
        'FRONT_STRETCHER', 'REAR_STRETCHER', 'BACK',
        'TOE_KICK_SUBFRONT',
        # Internal dividers / shelves
        'BAY_DIVISION', 'BAY_SHELF', 'MID_DIVISION', 'PARTITION_SKIN',
        # Drawer box
        'DRAWER_BOX',
        # Interior items
        'ADJUSTABLE_SHELF', 'PULLOUT_SHELF', 'PULLOUT_SPACER',
        'ROLLOUT_BOX', 'ROLLOUT_SPACER',
        'TRAY_DIVIDER', 'TRAY_LOCKED_SHELF',
        'VANITY_SHELF', 'VANITY_SUPPORT',
        'INTERIOR_FIXED_SHELF', 'INTERIOR_DIVISION',
    }

    # Roles that read materials from the 5-piece door modifier instead
    # of (or in addition to) the cutpart surface inputs.
    _FRONT_ROLES = {'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'}

    def _set_part_surfaces(self, part_obj, surface_mat, edge_mat):
        """Plug surface_mat into Top Surface + Bottom Surface and edge_mat
        into all four edge slots of a cutpart. Silently no-ops when
        either material is None (uncached / unresolved custom material)
        so the user just sees the previous slot value.
        """
        from ... import hb_types
        part = hb_types.GeoNodeCutpart(part_obj)
        if surface_mat is not None:
            try:
                part.set_input("Top Surface", surface_mat)
                part.set_input("Bottom Surface", surface_mat)
            except Exception:
                pass
        if edge_mat is not None:
            try:
                part.set_input("Edge W1", edge_mat)
                part.set_input("Edge W2", edge_mat)
                part.set_input("Edge L1", edge_mat)
                part.set_input("Edge L2", edge_mat)
            except Exception:
                pass

    def _set_part_surfaces_split(self, part_obj, top_mat, bottom_mat, edge_mat):
        """Like _set_part_surfaces but writes Top Surface and Bottom
        Surface independently. Used when the two faces of a cutpart
        should differ - a FINISHED side panel's outer face (Bottom
        Surface, regardless of left vs right side - see analysis in
        the chat thread that introduced this) gets finish material
        while the inner face (Top Surface) gets interior. Silent
        no-op for any material that's None.
        """
        from ... import hb_types
        part = hb_types.GeoNodeCutpart(part_obj)
        try:
            if top_mat is not None:
                part.set_input("Top Surface", top_mat)
            if bottom_mat is not None:
                part.set_input("Bottom Surface", bottom_mat)
            if edge_mat is not None:
                part.set_input("Edge W1", edge_mat)
                part.set_input("Edge W2", edge_mat)
                part.set_input("Edge L1", edge_mat)
                part.set_input("Edge L2", edge_mat)
        except Exception:
            pass

    def _set_door_modifier_materials(self, front_obj, finish_mat, finish_mat_rotated):
        """Set Stile / Rail / Panel material on a front's 'Door Style'
        CPM_5PIECEDOOR modifier, when present. Slab fronts have no
        such modifier and skip silently. Rails get the rotated variant
        so cross-grain reads correctly.
        """
        for mod in front_obj.modifiers:
            if mod.type != 'NODES' or not mod.node_group:
                continue
            if 'Door Style' not in mod.name:
                continue
            tree = mod.node_group.interface.items_tree
            if 'Stile Material' in tree and finish_mat is not None:
                mod[tree['Stile Material'].identifier] = finish_mat
            if 'Rail Material' in tree and finish_mat_rotated is not None:
                mod[tree['Rail Material'].identifier] = finish_mat_rotated
            if 'Panel Material' in tree and finish_mat is not None:
                # Glass-panel override is v2 - currently the panel always
                # gets the cabinet's finish material.
                mod[tree['Panel Material'].identifier] = finish_mat
            break

    def _apply_materials_to_cabinet(self, cabinet_obj):
        """Walk every CABINET_PART under cabinet_obj and write surface
        materials based on role. Face frame classifies by part role
        (face frame member / front / carcass / interior item) rather
        than the per-part Finish Top/Bottom flags frameless uses,
        because face frame construction does not vary those flags.
        Also wires the 5-piece door modifier material slots on fronts.
        """
        finish_mat, finish_mat_rotated = self.get_finish_material()
        interior_mat, interior_mat_rotated = self.get_interior_material()

        # Bail entirely if we have nothing useful to apply (e.g. CUSTOM
        # wood species with no custom_material picked yet).
        if finish_mat is None and interior_mat is None:
            return

        # Side panels read from the cabinet's per-side finished-end
        # condition: 'FINISHED' = the side itself is the visible
        # exterior (3/4" stock), all other values mean a covering part
        # (FLUSH_X / BEADBOARD / SHIPLAP / PANELED / FALSE_FF /
        # WORKING_FF) provides the visible face and the side stays
        # interior. Read once outside the loop.
        ff_cab = cabinet_obj.face_frame_cabinet
        left_side_finished = (ff_cab.left_finished_end_condition == 'FINISHED')
        right_side_finished = (ff_cab.right_finished_end_condition == 'FINISHED')

        for child in cabinet_obj.children_recursive:
            if 'CABINET_PART' not in child:
                continue
            role = child.get('hb_part_role')

            # Sides routed per-condition. For FINISHED sides the outer
            # face (Bottom Surface) gets finish, the inner face (Top
            # Surface, visible from inside the cabinet) gets interior.
            # Edges stay interior - they're mostly hidden behind the
            # face frame / against neighbors. Non-FINISHED sides are
            # interior throughout; the visible exterior comes from a
            # separate covering part (FLUSH_X / BEADBOARD / etc.).
            if role == 'LEFT_SIDE':
                if left_side_finished:
                    self._set_part_surfaces_split(
                        child,
                        top_mat=interior_mat,
                        bottom_mat=finish_mat,
                        edge_mat=interior_mat_rotated,
                    )
                else:
                    self._set_part_surfaces(child, interior_mat, interior_mat_rotated)
                continue
            if role == 'RIGHT_SIDE':
                if right_side_finished:
                    self._set_part_surfaces_split(
                        child,
                        top_mat=interior_mat,
                        bottom_mat=finish_mat,
                        edge_mat=interior_mat_rotated,
                    )
                else:
                    self._set_part_surfaces(child, interior_mat, interior_mat_rotated)
                continue

            if role in self._FINISH_EXTERIOR_ROLES:
                self._set_part_surfaces(
                    child, finish_mat, finish_mat_rotated,
                )
            elif role in self._INTERIOR_PART_ROLES:
                self._set_part_surfaces(
                    child, interior_mat, interior_mat_rotated,
                )
            # 5-piece door modifier slots, only on actual fronts (the
            # INSET_PANEL role is excluded - inset panels are flat).
            if role in self._FRONT_ROLES:
                self._set_door_modifier_materials(
                    child, finish_mat, finish_mat_rotated,
                )

    # cabinet_type -> column key in the ff_* width props.
    # LAP_DRAWER behaves as a base-cabinet; PANEL has no per-type
    # column yet (parent-cabinet inheritance is a follow-up) so it
    # falls back to base values.
    _CABINET_TYPE_COLUMN = {
        'BASE': 'base',
        'TALL': 'tall',
        'UPPER': 'upper',
        'LAP_DRAWER': 'base',
        'PANEL': 'base',
    }

    # left/right_stile_type -> ff_*_stile_width row prefix.
    _STILE_TYPE_TO_ROW = {
        'STANDARD': 'end_stile',
        'WALL': 'wall_stile',
        'BLIND': 'blind_stile',
    }

    def _ff_size_for(self, row, col):
        """Read the inch-meter value for a (row, col) cell."""
        return getattr(self, f"ff_{row}_width_{col}")

    def _apply_face_frame_sizes_to_cabinet(self, cabinet_obj):
        """Push the style's 21 face frame widths into the cabinet's
        stile/rail props. cabinet_type picks the column; left and
        right stile widths additionally depend on each side's
        stile_type. PANEL cabinets get the panel_* slot trio drawn
        from the BASE column.

        Wrapped in suspend_recalc(): the cabinet- and bay-level width
        props carry update callbacks that trigger recalc, and recalc
        wipes and rebuilds bays. Without suspending, the first bay
        write tears down the very list children_recursive is iterating
        and the next child reference dangles. Suspend coalesces all
        writes into one queued recalc that fires at the outermost
        resume - which here is the explicit recalc call back in
        assign_style_to_cabinet.
        """
        from . import types_face_frame
        with types_face_frame.suspend_recalc():
            self._apply_face_frame_sizes_to_cabinet_inner(cabinet_obj)

    def _apply_face_frame_sizes_to_cabinet_inner(self, cabinet_obj):
        props = cabinet_obj.face_frame_cabinet
        col = self._CABINET_TYPE_COLUMN.get(props.cabinet_type, 'base')

        if props.cabinet_type == 'PANEL':
            # PANEL has its own three-prop slot, no left/right or bays
            # to write into. Stile width borrows the end-stile row.
            props.panel_top_rail_width = self._ff_size_for('top_rail', 'base')
            props.panel_bottom_rail_width = self._ff_size_for('bottom_rail', 'base')
            props.panel_stile_width = self._ff_size_for('end_stile', 'base')
            return

        # Regular carcass cabinets - top/bottom rail at cabinet level.
        props.top_rail_width = self._ff_size_for('top_rail', col)
        props.bottom_rail_width = self._ff_size_for('bottom_rail', col)

        # Per-side stile widths: each side picks its row by its
        # stile_type. Unknown stile types fall back to end_stile.
        left_row = self._STILE_TYPE_TO_ROW.get(props.left_stile_type, 'end_stile')
        right_row = self._STILE_TYPE_TO_ROW.get(props.right_stile_type, 'end_stile')
        props.left_stile_width = self._ff_size_for(left_row, col)
        props.right_stile_width = self._ff_size_for(right_row, col)

        # Bay-level top/bottom rail widths: bays carry their own copies
        # of these (Face_Frame_Bay_Props), construction reads from the
        # bay, so writing only at the cabinet level leaves visible rails
        # unchanged for any bay whose values were seeded at creation
        # time.
        top_rail_w = self._ff_size_for('top_rail', col)
        bottom_rail_w = self._ff_size_for('bottom_rail', col)
        # Materialize the bay list before writing - even with recalcs
        # suspended, this is the safer pattern.
        bays = [
            child for child in cabinet_obj.children_recursive
            if child.get('IS_FACE_FRAME_BAY_CAGE')
        ]
        for bay_obj in bays:
            bay = bay_obj.face_frame_bay
            bay.top_rail_width = top_rail_w
            bay.bottom_rail_width = bottom_rail_w

        # Mid rail / mid stile widths cascade in THREE places:
        #
        # 1. The cabinet's bay_mid_rail_width / bay_mid_stile_width are
        #    the *defaults* used to initialize the per-split copy when a
        #    new split node is created. Setting these affects future
        #    splits only.
        #
        # 2. Each existing split node (inside-a-bay subdivisions) carries
        #    its own splitter_width on its face_frame_split PropertyGroup;
        #    bay mid rail / mid stile parts read THAT value at construction
        #    time. H-axis splits produce mid rails, V-axis splits produce
        #    mid stiles, so the per-split value picks from a different row.
        #
        # 3. The cabinet's mid_stile_widths CollectionProperty stores the
        #    width of each BETWEEN-BAYS mid stile (PART_ROLE_MID_STILE).
        #    Entry index N is the stile between bay N and bay N+1. Each
        #    entry carries an `unlock` flag - True means the user has
        #    overridden that specific stile and the style apply should
        #    leave it alone.
        mid_rail_w = self._ff_size_for('mid_rail', col)
        mid_stile_w = self._ff_size_for('mid_stile', col)
        props.bay_mid_rail_width = mid_rail_w
        props.bay_mid_stile_width = mid_stile_w

        split_nodes = [
            child for child in cabinet_obj.children_recursive
            if child.get('IS_FACE_FRAME_SPLIT_NODE')
        ]
        for split_obj in split_nodes:
            sp = split_obj.face_frame_split
            sp.splitter_width = mid_rail_w if sp.axis == 'H' else mid_stile_w

        for entry in props.mid_stile_widths:
            if not entry.unlock:
                entry.width = mid_stile_w

    def _apply_door_styles_to_fronts(self, cabinet_obj):
        """Walk every front under cabinet_obj. DOOR-role fronts get
        self.door_style; DRAWER_FRONT / PULLOUT_FRONT / FALSE_FRONT get
        self.drawer_front_style. Other roles (INSET_PANEL, structural
        parts, hardware) are skipped.
        """
        DOOR_ROLES = {'DOOR'}
        DRAWER_ROLES = {'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'}

        ff = bpy.context.scene.hb_face_frame

        def resolve(name):
            if not name or name == 'NONE':
                return None
            for ds in ff.door_styles:
                if ds.name == name:
                    return ds
            return None

        door_ds = resolve(self.door_style)
        drawer_ds = resolve(self.drawer_front_style)
        if door_ds is None and drawer_ds is None:
            return

        for child in cabinet_obj.children_recursive:
            if 'CABINET_PART' not in child:
                continue
            role = child.get('hb_part_role')
            if role in DOOR_ROLES and door_ds is not None:
                door_ds.assign_style_to_front(child)
            elif role in DRAWER_ROLES and drawer_ds is not None:
                drawer_ds.assign_style_to_front(child)

    # =================================================================
    # UI
    # =================================================================
    def _draw_face_frame_sizes(self, layout, context):
        """7x3 grid of face frame sizes drawn inside the cabinet style
        panel. Rail cells get an unlock checkbox + either a float input
        (unlocked) or a read-only inch label (locked). Stile cells are
        always overlay-driven and render as read-only inch labels.
        """
        from ... import units as _units  # for inch() display conversion

        def inch_label(meters):
            return f'{_units.meter_to_inch(meters):.4g}"'

        box = layout.box()
        row = box.row()
        row.label(text=f"Face Frame Sizes: Overlay = {self.door_overlay_type.replace('_', ' ').title()}")

        # Header row
        row = box.row(align=True)
        row.label(text="")
        row.label(text="", icon='BLANK1')
        row.label(text="Base")
        row.label(text="Tall")
        row.label(text="Upper")

        # Rail rows - each cell has an unlock checkbox + value
        for row_label, row_key, prop_root in (
            ("Top Rail", "top", "ff_top_rail_width"),
            ("Bottom Rail", "bottom", "ff_bottom_rail_width"),
            ("Mid Rail", "mid", "ff_mid_rail_width"),
        ):
            r = box.row(align=True)
            r.label(text=row_label)
            for col_key in ("base", "tall", "upper"):
                unlock_name = f"unlock_{col_key}_{row_key}_rail"
                unlocked = getattr(self, unlock_name)
                r.prop(self, unlock_name, text="",
                       icon='UNLOCKED' if unlocked else 'LOCKED',
                       emboss=False)
                if unlocked:
                    r.prop(self, f"{prop_root}_{col_key}", text="")
                else:
                    r.label(text=inch_label(getattr(self, f"{prop_root}_{col_key}")))

        # Stile rows - read-only labels (overlay-driven)
        for row_label, prop_root in (
            ("Wall Stile", "ff_wall_stile_width"),
            ("Mid Stile", "ff_mid_stile_width"),
            ("End Stile", "ff_end_stile_width"),
            ("Blind Stile", "ff_blind_stile_width"),
        ):
            r = box.row(align=True)
            r.label(text=row_label)
            for col_key in ("base", "tall", "upper"):
                r.label(text="", icon='BLANK1')
                r.label(text=inch_label(getattr(self, f"{prop_root}_{col_key}")))

    def draw_cabinet_style_ui(self, layout, context):
        """Per-style settings drawn inside the cabinet styles UIList panel.
        Door / drawer-front style dropdowns land after the door_styles
        collection is in place.
        """
        box = layout.box()
        box.prop(self, "name", text="Style Name")

        # Exterior material
        col = box.column(align=True)
        col.prop(self, "wood_species", text="Exterior")
        if self.wood_species == 'CUSTOM':
            col.prop(self, "custom_material", text="")
        elif self.wood_species == 'CUSTOM_PROCEDURAL':
            col.prop(self, "custom_wood_color_1", text="Color 1")
            col.prop(self, "custom_wood_color_2", text="Color 2")
            col.prop(self, "custom_roughness", text="Roughness")
            col.prop(self, "custom_noise_bump_strength", text="Noise Bump")
            col.prop(self, "custom_knots_bump_strength", text="Knots Bump")
            col.prop(self, "custom_wood_bump_strength", text="Wood Bump")
            row = box.row()
            row.prop(self, "show_custom_grain_options",
                     text="Grain Options",
                     icon='TRIA_DOWN' if self.show_custom_grain_options else 'TRIA_RIGHT',
                     emboss=False)
            if self.show_custom_grain_options:
                gcol = box.column(align=True)
                gcol.prop(self, "custom_noise_scale_1", text="Noise Scale 1")
                gcol.prop(self, "custom_noise_scale_2", text="Noise Scale 2")
                gcol.prop(self, "custom_texture_variation_1", text="Texture Variation 1")
                gcol.prop(self, "custom_texture_variation_2", text="Texture Variation 2")
                gcol.prop(self, "custom_noise_detail", text="Noise Detail")
                gcol.prop(self, "custom_voronoi_detail_1", text="Voronoi Detail 1")
                gcol.prop(self, "custom_voronoi_detail_2", text="Voronoi Detail 2")
                gcol.prop(self, "custom_knots_scale", text="Knots Scale")
                gcol.prop(self, "custom_knots_darkness", text="Knots Darkness")
        elif self.wood_species == 'PAINT_GRADE':
            col.prop(self, "paint_color", text="Paint Color")
        else:
            col.prop(self, "stain_color", text="Stain Color")

        # Interior material
        col = box.column(align=True)
        col.prop(self, "interior_material_type", text="Interior")
        if self.interior_material_type == 'CUSTOM':
            col.prop(self, "custom_interior_material", text="")

        # Door overlay (writes to L/R/T/B + inset at apply time)
        box.prop(self, "door_overlay_type", text="Door Overlay")

        # Door / drawer-front style picks (from the shared pool). The
        # selected names land in self.door_style / self.drawer_front_style;
        # assign_style_to_cabinet consumes them once assign_style_to_front
        # is wired.
        col = box.column(align=True)
        col.label(text="Fronts:")
        col.prop(self, "door_style", text="Door")
        col.prop(self, "drawer_front_style", text="Drawer Front")

        # Face frame sizes grid - 7 row types x 3 cabinet types. Rails
        # carry per-cell unlock toggles; stiles are always overlay-driven
        # and render as read-only inch labels. Collapsed by default
        # since the grid is large; expand to edit.
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, "show_face_frame_sizes",
                 text="Face Frame Sizes",
                 icon='TRIA_DOWN' if self.show_face_frame_sizes else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_face_frame_sizes:
            self._draw_face_frame_sizes(box, context)

        # Apply / re-apply buttons. Assign hits the current selection;
        # Update walks every cabinet already tagged with this style name.
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("hb_face_frame.assign_style_to_selected_cabinets",
                     text="Assign Style", icon='BRUSH_DATA')
        row.operator("hb_face_frame.update_cabinets_from_style",
                     text="Update Cabinets", icon='FILE_REFRESH')


class HB_UL_face_frame_cabinet_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon='SHADERFX')


# ---------------------------------------------------------------------------
# Door Style - shared pool, referenced from cabinet styles via index
# ---------------------------------------------------------------------------
class Face_Frame_Door_Style(PropertyGroup):
    """Door / drawer-front construction style. Lives in a single
    Face_Frame_Scene_Props.door_styles collection; cabinet styles reference
    one entry as the door style and another as the drawer-front style via
    integer indices.
    """

    name: StringProperty(
        name="Name",
        description="Door style name",
        default="Door Style",
        update=update_door_style_name,
    )  # type: ignore

    show_expanded: BoolProperty(
        name="Show Expanded",
        description="Show expanded style options",
        default=False,
    )  # type: ignore

    # ---- Construction type ----
    door_type: EnumProperty(
        name="Door Type",
        description="Door construction type",
        items=[
            ('SLAB', "Slab", "Solid slab door"),
            ('5_PIECE', "5 Piece", "5-piece frame and panel door"),
        ],
        default='5_PIECE',
        update=_propagate_door_style,
    )  # type: ignore

    panel_material: EnumProperty(
        name="Panel Material",
        description="Material for door panel center",
        items=[
            ('MATCH_CABINET', "Match Cabinet", "Match the parent cabinet style material"),
            ('GLASS', "Glass", "Glass panel"),
        ],
        default='MATCH_CABINET',
        update=_propagate_door_style,
    )  # type: ignore

    # ---- Profile object references ----
    outside_profile: PointerProperty(
        name="Outside Profile",
        type=bpy.types.Object,
        update=_propagate_door_style,
    )  # type: ignore

    inside_profile: PointerProperty(
        name="Inside Profile",
        type=bpy.types.Object,
        update=_propagate_door_style,
    )  # type: ignore

    # ---- 5-piece dimensions ----
    stile_width: FloatProperty(
        name="Stile Width",
        description="Width of left and right stiles",
        default=units.inch(3.0), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    rail_width: FloatProperty(
        name="Rail Width",
        description="Width of top and bottom rails",
        default=units.inch(3.0), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    # ---- Mid rail ----
    add_mid_rail: BoolProperty(
        name="Add Mid Rail",
        description="Add a horizontal mid rail",
        default=False,
        update=_propagate_door_style,
    )  # type: ignore

    center_mid_rail: BoolProperty(
        name="Center Mid Rail",
        description="Center the mid rail vertically",
        default=True,
        update=_propagate_door_style,
    )  # type: ignore

    mid_rail_width: FloatProperty(
        name="Mid Rail Width",
        description="Width of the mid rail",
        default=units.inch(3.0), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    mid_rail_location: FloatProperty(
        name="Mid Rail Location",
        description="Distance from bottom of door to mid rail (if not centered)",
        default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    # ---- Panel ----
    panel_thickness: FloatProperty(
        name="Panel Thickness",
        description="Thickness of the center panel",
        default=units.inch(0.5), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    panel_inset: FloatProperty(
        name="Panel Inset",
        description="How far panel is inset from frame face",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    # ---- Edge profile (slab doors) ----
    edge_profile_type: EnumProperty(
        name="Edge Profile",
        description="Edge profile for slab doors",
        items=[
            ('SQUARE', "Square", "Square edge"),
            ('EASED', "Eased", "Slightly rounded edge"),
            ('OGEE', "Ogee", "Ogee profile"),
            ('BEVEL', "Bevel", "Beveled edge"),
            ('ROUNDOVER', "Roundover", "Rounded edge"),
        ],
        default='SQUARE',
        update=_propagate_door_style,
    )  # type: ignore

    # Front roles this style will act on (DOOR fronts read door_style on the
    # parent cabinet style, the rest read drawer_front_style).
    _DOOR_FRONT_ROLES = {'DOOR'}
    _DRAWER_FRONT_ROLES = {'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT'}
    _STYLEABLE_ROLES = _DOOR_FRONT_ROLES | _DRAWER_FRONT_ROLES

    def get_parent_cabinet_style(self, front_obj):
        """Walk up from a front object to its face frame cabinet root,
        read the cabinet's STYLE_NAME custom prop, and return the matching
        Face_Frame_Cabinet_Style on the scene (or None if unresolvable).
        Used for material inheritance once material walking is wired.
        """
        cur = front_obj
        cabinet_obj = None
        while cur is not None:
            if cur.get('IS_FACE_FRAME_CABINET_CAGE'):
                cabinet_obj = cur
                break
            cur = cur.parent
        if cabinet_obj is None:
            return None

        style_name = cabinet_obj.get('STYLE_NAME')
        if not style_name:
            return None

        ff = bpy.context.scene.hb_face_frame
        for cs in ff.cabinet_styles:
            if cs.name == style_name:
                return cs
        return None

    def assign_style_to_front(self, front_obj):
        """Apply this door style to a face frame front object.

        SLAB: remove any existing 'Door Style' modifier so the front
        renders as a flat slab.
        5_PIECE: add or update a CPM_5PIECEDOOR modifier named
        'Door Style' with the configured stile/rail widths, mid rail,
        panel thickness/inset.

        Returns:
            True on success.
            False if front_obj is not a styleable face frame front.
            A string with an error message on a 5-piece dimension check
            failure (front too narrow / too short for the configured
            stiles + rails).
        """
        role = front_obj.get('hb_part_role')
        if role not in self._STYLEABLE_ROLES:
            return False

        from ... import hb_types

        # Slab: strip any existing door style modifier and tag.
        if self.door_type == 'SLAB':
            for mod in list(front_obj.modifiers):
                if mod.type == 'NODES' and 'Door Style' in mod.name:
                    front_obj.modifiers.remove(mod)
            front_obj['DOOR_STYLE_NAME'] = self.name
            return True

        # 5-piece: dimension check, then add / update the modifier.
        # GeoNodeCutpart (not GeoNodeObject) is the class that exposes
        # add_part_modifier - matches the wrap used elsewhere for fronts.
        part = hb_types.GeoNodeCutpart(front_obj)
        try:
            front_length = part.get_input("Length")
            front_width = part.get_input("Width")
        except Exception:
            return "Could not read front dimensions"

        # Auto-add a centered mid rail above 45.5" so tall doors are
        # split. Matches the frameless convention.
        auto_mid_rail_threshold = units.inch(45.5)
        needs_auto_mid_rail = front_length > auto_mid_rail_threshold

        min_width = self.stile_width * 2 + units.inch(1)
        min_height = self.rail_width * 2 + units.inch(1)
        if self.add_mid_rail or needs_auto_mid_rail:
            min_height += self.mid_rail_width

        if front_width < min_width:
            return (f"Front too narrow ({front_width:.3f}m) for stile "
                    f"widths (need {min_width:.3f}m)")
        if front_length < min_height:
            return (f"Front too short ({front_length:.3f}m) for rail "
                    f"widths (need {min_height:.3f}m)")

        # Find or add the 'Door Style' CPM_5PIECEDOOR modifier.
        existing_mod = None
        for mod in front_obj.modifiers:
            if mod.type == 'NODES' and 'Door Style' in mod.name:
                existing_mod = mod
                break
        if existing_mod is not None:
            door_style_mod = hb_types.CabinetPartModifier()
            door_style_mod.obj = front_obj
            door_style_mod.mod = existing_mod
        else:
            door_style_mod = part.add_part_modifier('CPM_5PIECEDOOR', 'Door Style')

        door_style_mod.set_input("Left Stile Width", self.stile_width)
        door_style_mod.set_input("Right Stile Width", self.stile_width)
        door_style_mod.set_input("Top Rail Width", self.rail_width)
        door_style_mod.set_input("Bottom Rail Width", self.rail_width)
        door_style_mod.set_input("Panel Thickness", self.panel_thickness)
        door_style_mod.set_input("Panel Inset", self.panel_inset)

        if needs_auto_mid_rail or self.add_mid_rail:
            try:
                door_style_mod.set_input("Add Mid Rail", True)
                door_style_mod.set_input("Mid Rail Width", self.mid_rail_width)
                if needs_auto_mid_rail:
                    door_style_mod.set_input("Center Mid Rail", True)
                else:
                    door_style_mod.set_input("Center Mid Rail", self.center_mid_rail)
                    if not self.center_mid_rail:
                        door_style_mod.set_input("Mid Rail Location", self.mid_rail_location)
            except Exception:
                pass
        else:
            try:
                door_style_mod.set_input("Add Mid Rail", False)
            except Exception:
                pass

        # Material inheritance from the parent cabinet style lands once
        # cabinet-style material walking is implemented.
        front_obj['DOOR_STYLE_NAME'] = self.name
        return True

    def draw_door_style_ui(self, layout, context):
        """Per-style settings drawn inside the door styles UIList panel.
        Assign / Update ops for fronts ship alongside assign_style_to_front.
        """
        box = layout.box()
        box.prop(self, "name", text="Style Name")

        col = box.column(align=True)
        col.label(text="Construction:")
        col.prop(self, "door_type", text="Type")

        if self.door_type == 'SLAB':
            col = box.column(align=True)
            col.label(text="Edge Profile:")
            col.prop(self, "edge_profile_type", text="")
        else:
            col = box.column(align=True)
            col.label(text="Frame Dimensions:")
            col.prop(self, "stile_width", text="Stile Width")
            col.prop(self, "rail_width", text="Rail Width")

            col = box.column(align=True)
            col.label(text="Mid Rail:")
            col.prop(self, "add_mid_rail", text="Add Mid Rail")
            # Width stays editable even when Add Mid Rail is off: tall
            # doors above 45.5" get an auto-added mid rail in
            # assign_style_to_front using this same value, so the user
            # needs to be able to set it without first toggling Add.
            col.prop(self, "mid_rail_width", text="Width")
            if self.add_mid_rail:
                col.prop(self, "center_mid_rail", text="Center")
                if not self.center_mid_rail:
                    col.prop(self, "mid_rail_location", text="Location")

            col = box.column(align=True)
            col.label(text="Panel:")
            col.prop(self, "panel_material", text="Material")
            col.prop(self, "panel_thickness", text="Thickness")
            col.prop(self, "panel_inset", text="Inset")

        col = box.column(align=True)
        col.label(text="Profiles:")
        col.prop(self, "outside_profile", text="Outside")
        if self.door_type != 'SLAB':
            col.prop(self, "inside_profile", text="Inside")

        # Assign hits the current selection (anything not a face frame
        # front is silently skipped); Update walks every front already
        # tagged with this style name.
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("hb_face_frame.assign_door_style_to_selected_fronts",
                     text="Assign Door Style", icon='BRUSH_DATA')
        row.operator("hb_face_frame.update_fronts_from_door_style",
                     text="Update Fronts", icon='FILE_REFRESH')


class HB_UL_face_frame_door_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon='MESH_PLANE')


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


def _update_interior_size(self, context):
    """Auto-lock-on-edit for interior tree node sizes (region or split).

    Mirrors _update_bay_width: distinguishes user edits from the
    redistribution pass by checking the _DISTRIBUTING_WIDTHS guard.
    User edits flip unlock_size=True so the new size holds during
    future redistributions; that flip itself fires _update_cabinet_dim
    which runs the recalc, so we don't call recalc directly here.
    """
    from . import types_face_frame
    root = types_face_frame.find_cabinet_root(self.id_data)
    if root is None:
        return
    if id(root) in types_face_frame._DISTRIBUTING_WIDTHS:
        return  # system write - skip auto-lock and skip recalc
    if not self.unlock_size:
        self.unlock_size = True
    else:
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


def _recompute_blind_stile_width(cab_props, side):
    """Set left_stile_width or right_stile_width from the current stile-type
    and blind-state combination. No-op when the side's unlock flag is True
    (user has taken manual control) or when the scene doesn't carry the
    face frame defaults yet (during first-load / unregister).

    Coupling: stile_type=='BLIND' uses ff_blind_stile_width as the visible
    portion; the blind_left/blind_right flag adds 0.75" for the adjacent
    cabinet's face. stile_type=='STANDARD' or 'WALL' restores the plain
    ff_end_stile_width default.
    """
    scene = bpy.context.scene
    ff_scene = getattr(scene, 'hb_face_frame', None)
    if ff_scene is None:
        return

    if side == 'LEFT':
        if cab_props.unlock_left_stile:
            return
        stile_type = cab_props.left_stile_type
        is_blind = cab_props.blind_left
        target_attr = 'left_stile_width'
    else:
        if cab_props.unlock_right_stile:
            return
        stile_type = cab_props.right_stile_type
        is_blind = cab_props.blind_right
        target_attr = 'right_stile_width'

    if stile_type == 'BLIND':
        width = ff_scene.ff_blind_stile_width
        if is_blind:
            width += units.inch(0.75)
    else:
        width = ff_scene.ff_end_stile_width

    # Only write if the value actually changed - avoids a redundant
    # _update_cabinet_dim recalc trip in the common case where the user
    # toggles a flag that doesn't change the resulting width.
    if abs(getattr(cab_props, target_attr) - width) > 1e-7:
        setattr(cab_props, target_attr, width)


def _update_left_stile_type(self, context):
    _recompute_blind_stile_width(self, 'LEFT')
    _update_cabinet_dim(self, context)


def _update_right_stile_type(self, context):
    _recompute_blind_stile_width(self, 'RIGHT')
    _update_cabinet_dim(self, context)


def _update_blind_left(self, context):
    _recompute_blind_stile_width(self, 'LEFT')
    _update_cabinet_dim(self, context)


def _update_blind_right(self, context):
    _recompute_blind_stile_width(self, 'RIGHT')
    _update_cabinet_dim(self, context)


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

    blind_left: BoolProperty(
        name="Blind Left", default=False, update=_update_blind_left
    )  # type: ignore
    blind_right: BoolProperty(
        name="Blind Right", default=False, update=_update_blind_right
    )  # type: ignore
    blind_amount_left: FloatProperty(
        name="Blind Amount Left", default=units.inch(24.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    blind_amount_right: FloatProperty(
        name="Blind Amount Right", default=units.inch(24.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    blind_reveal: FloatProperty(
        name="Blind Reveal", default=units.inch(1.5), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
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
        name="Left Stile Type", items=LEFT_STILE_TYPE_ITEMS, default='STANDARD',
        update=_update_left_stile_type,
    )  # type: ignore
    right_stile_type: EnumProperty(
        name="Right Stile Type", items=LEFT_STILE_TYPE_ITEMS, default='STANDARD',
        update=_update_right_stile_type,
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

    # Distance the door is recessed into the face frame thickness. Zero for
    # overlay doors (door front face sits proud of the frame face); positive
    # for inset doors (door pushed back into the opening). Partial inset
    # typically ~0.375"; full inset = face_frame_thickness (flush).
    default_door_inset_amount: FloatProperty(
        name="Default Door Inset Amount",
        description="Distance the door is recessed from the face frame face (0 = overlay, full = flush inset)",
        default=0.0, unit='LENGTH', precision=4,
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

    Field naming convention:
      - shared shelf-like fields use shelf_*
      - shared multi-count assembly fields (PULLOUT_SHELF, ROLLOUT) use
        the bare names qty / unlock_qty / spacer_height / item_setback /
        bottom_gap / distance_between / item_height
      - kind-specific fields use the kind as a prefix (tray_*, vanity_*)
    """

    INTERIOR_KIND_ITEMS = [
        ('ADJUSTABLE_SHELF', "Adjustable Shelves", "Set of evenly-spaced shelves on shelf pins"),
        ('GLASS_SHELF',      "Glass Shelves",      "Adjustable shelves with a glass material override"),
        ('PULLOUT_SHELF',    "Pullout Shelves",    "Stack of flat shelves on slide hardware"),
        ('ROLLOUT',          "Rollouts",           "Stack of drawer boxes on slide hardware"),
        ('TRAY_DIVIDERS',    "Tray Dividers",      "Vertical dividers for trays / cookie sheets, optionally with a locked shelf above"),
        ('VANITY_SHELVES',   "Vanity Shelves",     "Pair of L/R shelves on corbel supports, around plumbing"),
        ('ACCESSORY',        "Accessory",          "Free-text accessory label rendered inside the opening"),
    ]
    kind: EnumProperty(
        name="Kind", items=INTERIOR_KIND_ITEMS, default='ADJUSTABLE_SHELF',
        update=_update_cabinet_dim,
    )  # type: ignore

    # ADJUSTABLE_SHELF / GLASS_SHELF
    # shelf_qty is auto-recomputed from opening height every recalc
    # while unlock_shelf_qty is False. Set unlock_shelf_qty to True to
    # pin a specific count and stop the auto-recompute.
    shelf_qty: IntProperty(
        name="Shelf Qty", default=1, min=0, max=20,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_shelf_qty: BoolProperty(
        name="Unlock Shelf Qty",
        description="When on, hold the shelf count at the value above instead of auto-computing it from the opening's height",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    # Front setback for shelf-likes. Default = standard pin clearance;
    # the half-depth preset bumps this to 6" for a half-depth feel.
    shelf_setback: FloatProperty(
        name="Shelf Setback",
        description="Distance the shelf is pulled back from the front of the cavity",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # PULLOUT_SHELF / ROLLOUT
    # Multi-count assembly fields. qty defaults to 2 (typical use); the
    # auto rule (when unlock_qty is False) fills the opening from
    # item_height + distance_between.
    qty: IntProperty(
        name="Qty", default=2, min=0, max=10,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_qty: BoolProperty(
        name="Unlock Qty",
        description="When on, hold the count at the value above instead of auto-computing it from the opening's height",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    # Side spacer width: vertical filler the assembly mounts to. The
    # spacers run the full opening height on both sides, front + back,
    # giving slide hardware a flush surface that bridges any face frame
    # inset. Width is the X-dimension of each spacer.
    spacer_height: FloatProperty(
        name="Spacer Width",
        description="Width of the side spacer parts the slides mount to (front and back, both sides)",
        default=units.inch(2.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    item_setback: FloatProperty(
        name="Item Setback",
        description="Front setback for each item in the stack",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    bottom_gap: FloatProperty(
        name="Bottom Gap",
        description="Gap below the bottom-most item in the stack",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    distance_between: FloatProperty(
        name="Distance Between",
        description="Vertical gap between consecutive items in the stack",
        default=units.inch(6.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    # Split per kind because the natural defaults are far apart: a
    # pullout shelf is 0.75" stock; a rollout drawer box is ~3.625" tall.
    # Sharing the field would force one or the other to be wrong on
    # creation and on kind switches.
    pullout_thickness: FloatProperty(
        name="Pullout Thickness",
        description="Thickness of each pullout shelf (PULLOUT_SHELF only)",
        default=units.inch(0.75), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    rollout_height: FloatProperty(
        name="Rollout Height",
        description="Height of each rollout drawer box (ROLLOUT only)",
        default=units.inch(3.625), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # TRAY_DIVIDERS
    # Vertical dividers; tray_remove_shelf=False adds a horizontal locked
    # shelf at tray_opening_height that the dividers stop against.
    tray_qty: IntProperty(
        name="Tray Qty", default=3, min=1, max=10,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_remove_shelf: BoolProperty(
        name="Remove Locked Shelf",
        description="When on, dividers run the full opening height. Off = dividers stop at a horizontal locked shelf at Tray Opening Height",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    tray_opening_height: FloatProperty(
        name="Tray Opening Height",
        description="Z position of the locked shelf above the tray dividers (only when Remove Locked Shelf is off)",
        default=units.inch(20.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_divider_thickness: FloatProperty(
        name="Tray Divider Thickness",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_setback: FloatProperty(
        name="Tray Setback",
        description="Front setback for the tray dividers",
        default=units.inch(1.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    # VANITY_SHELVES
    # Pair of side-mounted shelves around plumbing. Single Z, mirrored
    # length L/R.
    vanity_z: FloatProperty(
        name="Shelf Z",
        description="Z height of the vanity shelves (both sides)",
        default=units.inch(11.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    vanity_length: FloatProperty(
        name="Shelf Length",
        description="Length of each side shelf (mirrored L and R)",
        default=units.inch(7.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
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


class Face_Frame_Interior_Split_Props(PropertyGroup):
    """Per-interior-split-node state. Attached to each interior split
    node Empty as bpy.types.Object.face_frame_interior_split.

    Interior splits subdivide an opening into regions. H-splits are
    fixed shelves (children stacked in Z; horizontal divider between);
    V-splits are divisions (children side by side in X; vertical
    divider between). Children are sorted by hb_interior_child_index
    (0 = lower / left, 1 = upper / right) and each carries its own
    size (Face_Frame_Interior_Region_Props.size for leaves, or this
    same Face_Frame_Interior_Split_Props.size for nested splits).
    """

    SPLIT_AXIS_ITEMS = [
        ('H', "Fixed Shelf", "Horizontal divider; children stacked vertically"),
        ('V', "Division",    "Vertical divider; children side by side"),
    ]
    axis: EnumProperty(
        name="Axis", items=SPLIT_AXIS_ITEMS, default='H',
        update=_update_cabinet_dim,
    )  # type: ignore

    size: FloatProperty(
        name="Size", default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_update_interior_size,
    )  # type: ignore
    unlock_size: BoolProperty(
        name="Unlock Size",
        description="Hold this split's size during sibling redistribution",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    divider_thickness: FloatProperty(
        name="Divider Thickness",
        description="Thickness of the fixed shelf or division at this split",
        default=units.inch(0.75), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore


class Face_Frame_Interior_Region_Props(PropertyGroup):
    """Per-leaf-region state. Attached to each leaf cage as
    bpy.types.Object.face_frame_interior_region.

    A leaf region is a sub-rect of an opening, isolated by zero or
    more splits in the interior tree. It carries its own
    interior_items collection (same item type as the opening's flat
    collection) plus the size/unlock used by sibling redistribution.
    """

    interior_items: CollectionProperty(type=Face_Frame_Interior_Item)  # type: ignore
    interior_items_index: IntProperty(default=0)  # type: ignore

    size: FloatProperty(
        name="Size", default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_update_interior_size,
    )  # type: ignore
    unlock_size: BoolProperty(
        name="Unlock Size",
        description="Hold this region's size during sibling redistribution",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    # UI-only: collapsed by default in the inline tree view to keep
    # the opening prompts popup short. Toggled by the triangle button
    # next to each region's header.
    expanded: BoolProperty(
        name="Expanded",
        description="Show this region's size, divider, and items",
        default=False,
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

    # User library category filter. Items are dynamic so newly-created
    # subfolders show up without a restart.
    cabinet_group_category: EnumProperty(
        name="Category",
        description="Filter cabinet groups by category subfolder",
        items=get_cabinet_group_category_items,
    )  # type: ignore

    # ---- Options section toggles ----
    show_cabinet_styles: BoolProperty(name="Show Cabinet Styles", default=False)  # type: ignore
    show_door_styles: BoolProperty(name="Show Door Styles", default=False)  # type: ignore
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

    # Shared door-style pool. Cabinet styles reference one entry as the door
    # style and another as the drawer-front style via integer indices.
    door_styles: CollectionProperty(type=Face_Frame_Door_Style)  # type: ignore
    active_door_style_index: IntProperty(name="Active Door Style Index", default=0)  # type: ignore

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
        default=units.inch(25.5),
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

    # Exposed (visible) portion of a blind-corner end stile. When the
    # adjacent cabinet butts into the blind side (blind_left/right True),
    # the stile widens by another 0.75" to accept the adjacent face -
    # so a 3.0" default yields a 3.75" stile with 3.0" visible.
    ff_blind_stile_width: FloatProperty(
        name="Blind Stile Width",
        description="Visible (exposed) portion of a blind-corner end stile",
        default=units.inch(3.0),
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
    # UI: user library
    # =====================================================================
    def draw_user_library_ui(self, layout, context):
        from .operators import ops_library

        # Header row: refresh + open-folder. Keeps these one tap away when
        # the user is iterating on a saved group.
        row = layout.row()
        row.label(text="User Library")
        row.operator('hb_face_frame.refresh_user_library', text="", icon='FILE_REFRESH')
        row.operator('hb_face_frame.open_user_library_folder', text="", icon='FILE_FOLDER')

        # Create + save sit at the top so the workflow reads top-down:
        # build a group, save it, browse what's already saved.
        col = layout.column(align=True)
        col.operator('hb_face_frame.create_cabinet_group', text="Create Cabinet Group", icon='ADD')
        col.operator('hb_face_frame.save_cabinet_group_to_user_library',
                     text="Save to Library", icon='FILE_TICK')

        layout.separator()

        row = layout.row(align=True)
        row.label(text="Category:")
        row.prop(self, 'cabinet_group_category', text="")

        category = self.cabinet_group_category if hasattr(self, 'cabinet_group_category') else 'ALL'
        library_items = ops_library.get_user_library_items(
            None if category == 'ALL' else category
        )

        if not library_items:
            box = layout.box()
            box.label(text="No saved cabinet groups", icon='INFO')
            box.label(text="Save a cabinet group to see it here")
            return

        box = layout.box()
        box.label(text=f"Saved Groups ({len(library_items)})", icon='ASSET_MANAGER')

        # Two-column grid of saved items. Each cell shows name + delete +
        # thumbnail (if rendered) + an Add-to-Scene button that fires the
        # modal load operator.
        flow = box.column_flow(columns=2, align=True)

        for item in library_items:
            item_box = flow.box()

            row = item_box.row()
            row.label(text=item['name'])
            del_op = row.operator('hb_face_frame.delete_library_item',
                                  text="", icon='X', emboss=False)
            del_op.filepath = item['filepath']
            del_op.item_name = item['name']

            if item['thumbnail']:
                icon_id = load_library_thumbnail(item['thumbnail'], item['name'])
                if icon_id:
                    item_box.template_icon(icon_value=icon_id, scale=5.0)

            op = item_box.operator('hb_face_frame.load_cabinet_group_from_library',
                                   text="Add to Scene", icon='IMPORT')
            op.filepath = item['filepath']

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
        side = row.column(align=True)
        side.operator("hb_face_frame.add_cabinet_style", text="", icon='ADD')
        side.operator("hb_face_frame.remove_cabinet_style", text="", icon='REMOVE')

        if self.cabinet_styles and self.active_cabinet_style_index < len(self.cabinet_styles):
            style = self.cabinet_styles[self.active_cabinet_style_index]
            style.draw_cabinet_style_ui(layout, context)
        else:
            box = layout.box()
            box.label(text="No cabinet styles defined", icon='INFO')

    def draw_door_styles_ui(self, layout, context):
        row = layout.row()
        row.template_list(
            "HB_UL_face_frame_door_styles", "",
            self, "door_styles",
            self, "active_door_style_index",
            rows=3,
        )
        side = row.column(align=True)
        side.operator("hb_face_frame.add_door_style", text="", icon='ADD')
        side.operator("hb_face_frame.remove_door_style", text="", icon='REMOVE')

        if self.door_styles and self.active_door_style_index < len(self.door_styles):
            ds = self.door_styles[self.active_door_style_index]
            ds.draw_door_style_ui(layout, context)
        else:
            box = layout.box()
            box.label(text="No door styles defined", icon='INFO')

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
            row.prop(self, 'show_door_styles', text="Door Styles",
                     icon='TRIA_DOWN' if self.show_door_styles else 'TRIA_RIGHT', emboss=False)
            if self.show_door_styles:
                self.draw_door_styles_ui(box, context)

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
    Face_Frame_Door_Style,
    HB_UL_face_frame_door_styles,
    Face_Frame_Mid_Stile_Width,
    Face_Frame_Cabinet_Props,
    Face_Frame_Bay_Props,
    Face_Frame_Interior_Item,
    Face_Frame_Interior_Region_Props,
    Face_Frame_Opening_Props,
    Face_Frame_Split_Props,
    Face_Frame_Interior_Split_Props,
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
    bpy.types.Object.face_frame_interior_split = PointerProperty(type=Face_Frame_Interior_Split_Props)
    bpy.types.Object.face_frame_interior_region = PointerProperty(type=Face_Frame_Interior_Region_Props)

    # Initialize preview collections so thumbnails load on first sidebar draw
    get_library_previews()
    get_cabinet_previews()


def unregister():
    if hasattr(bpy.types.Object, 'face_frame_interior_region'):
        del bpy.types.Object.face_frame_interior_region
    if hasattr(bpy.types.Object, 'face_frame_interior_split'):
        del bpy.types.Object.face_frame_interior_split
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
