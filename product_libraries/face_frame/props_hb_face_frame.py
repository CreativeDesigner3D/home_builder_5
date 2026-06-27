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
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    CollectionProperty,
    EnumProperty,
)
from ... import units
from . import finish_colors, wood_materials, style_options


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


# Exposure states per side. UNEXPOSED = covered by wall or neighbor over
# the full cabinet height. PARTIAL = neighbor abuts but only covers part
# of the height (tall vs. base/upper). EXPOSED = no abutting neighbor.
# Drives the auto-pick of finished_end_condition in exposure.py.
EXPOSURE_ITEMS = [
    ('UNEXPOSED', "Unexposed", "Side is fully covered by a wall or neighbor"),
    ('PARTIAL', "Partial", "Side is partially covered by a shorter neighbor"),
    ('EXPOSED', "Exposed", "Side has no abutting neighbor"),
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

def get_style_props(context=None):
    """Return the hb_face_frame props that own the shared style pools.

    Cabinet styles and door styles are project-global -- they live on the
    main scene so every room sees the same set. Route any cabinet_styles /
    door_styles / active-index access through here instead of reading
    context.scene.hb_face_frame directly. Per-scene settings (default
    sizes, selection mode) stay on the active scene.
    """
    from ... import hb_project
    ctx = context or bpy.context
    main = hb_project.get_main_scene(ctx)
    if main is not None and hasattr(main, "hb_face_frame"):
        return main.hb_face_frame
    return ctx.scene.hb_face_frame


def update_cabinet_style_name(self, context):
    """Keep style names unique within the collection AND propagate a rename
    to every cabinet already tagged with this style (its STYLE_NAME), so an
    assigned cabinet keeps resolving -- and 2D-colouring -- after a rename.
    The prior name is tracked in rename_anchor because Blender's update
    callback does not expose the old value."""
    main = get_style_props(context)
    base_name = self.name if self.name else "Style"
    existing = [s.name for s in main.cabinet_styles if s != self]
    final = base_name
    if base_name in existing:
        i = 1
        while f"{base_name}.{i:03d}" in existing:
            i += 1
        final = f"{base_name}.{i:03d}"
    old = self.rename_anchor
    if old and old != final:
        for obj in bpy.data.objects:
            if obj.get('STYLE_NAME') == old:
                obj['STYLE_NAME'] = final
    self.rename_anchor = final
    # Apply the de-duplicated name last. If this re-enters the callback,
    # final is already unique and anchor == final, so it is a clean no-op.
    if self.name != final:
        self.name = final


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
    ff = get_style_props(context)
    for i, ds in enumerate(ff.door_styles):
        items.append((ds.name, ds.name, ds.name, i))
    if not items:
        items.append(('NONE', "(none defined)", "No door styles defined", 0))
    return items


def get_drawer_front_style_enum_items(self, context):
    """Dynamic items for the cabinet style's drawer-front picker. Reads names
    from the drawer_front_styles pool (independent from door_styles)."""
    items = []
    ff = get_style_props(context)
    for i, ds in enumerate(ff.drawer_front_styles):
        items.append((ds.name, ds.name, ds.name, i))
    if not items:
        items.append(('NONE', "(none defined)", "No drawer front styles defined", 0))
    return items


# ---------------------------------------------------------------------------
# Catalog options + compatibility cascades (baked in style_options.py from the
# reference partner spreadsheets). These are SPEC selections: they record the
# correct, compatibility-filtered choices -- wood -> color -> varnish/glaze,
# overlay -> hinge, and front series -> shape -> panel -- WITHOUT yet driving
# geometry or material. The existing wood_species / door_overlay_type enums
# still own rendering + face-frame sizing; wiring these to material /
# sizing is a deliberate later pass.
#
# Enum item-tuples are built ONCE at module load into module-level dicts. That
# doubles as the keepalive Blender needs (a callback returning freshly built
# tuples each call risks GC mid-use -- see the _EXTERIOR_CONFIG_ITEMS note).
# The callbacks just look the cached list up by the current upstream value.

def _enum_items(values):
    """[(identifier, name, description, index), ...] from a list of names."""
    return [(v, v, v, i) for i, v in enumerate(values)]


def _hinge_items(rows):
    """De-duplicated hinge items [(code, desc, desc, index), ...]."""
    seen, out = set(), []
    for code, desc, _default in rows:
        if code in seen:
            continue
        seen.add(code)
        out.append((code, desc, desc, len(out)))
    return out


_NONE_ITEMS = [('NONE', "(none)", "No selection", 0)]


def _items_or_none(items):
    return items if items else _NONE_ITEMS


# --- cabinet-style finish caches ---
_FINISH_WOOD_ITEMS = [(i, lbl, lbl, n)
                      for n, (i, lbl) in enumerate(style_options.woods_for_ui())]
_FINISH_COLOR_ITEMS = {w: [(i, lbl, lbl, n)
                           for n, (i, lbl) in enumerate(style_options.colors_for_wood_ui(w))]
                       for w in style_options.WOOD_SPECIES}
_FINISH_VARNISH_ITEMS = {c: _enum_items(style_options.varnishes_for_color(c) or ["N/A"])
                         for c in style_options.COLORS}
_FINISH_GLAZE_ITEMS = {c: _enum_items(style_options.glazes_for_color(c))
                       for c in style_options.COLORS}
_FINISH_OVERLAY_ITEMS = [(i, lbl, lbl, n)
                         for n, (i, lbl) in enumerate(style_options.overlays_for_ui())]
_FINISH_HINGE_ITEMS = {o: _hinge_items(rows)
                       for o, rows in style_options.OVERLAY_TO_HINGES.items()}


def _set_enum_safe(owner, prop, identifier):
    """Assign an enum identifier only if valid for the prop's current items
    (assigning an out-of-list identifier raises). No-op on mismatch."""
    try:
        setattr(owner, prop, identifier)
    except (TypeError, ValueError):
        pass


def get_finish_wood_items(self, context):
    return _items_or_none(_FINISH_WOOD_ITEMS)


def get_finish_color_items(self, context):
    return _items_or_none(_FINISH_COLOR_ITEMS.get(self.finish_wood, []))


def get_finish_varnish_items(self, context):
    return _items_or_none(_FINISH_VARNISH_ITEMS.get(self.finish_color, []))


def get_finish_glaze_items(self, context):
    return _items_or_none(_FINISH_GLAZE_ITEMS.get(self.finish_color, []))


def get_finish_overlay_items(self, context):
    return _items_or_none(_FINISH_OVERLAY_ITEMS)


def get_finish_hinge_items(self, context):
    return _items_or_none(_FINISH_HINGE_ITEMS.get(self.finish_overlay, []))


def update_finish_wood(self, context):
    """Wood gates color: reset to the first compatible color (which cascades
    on to varnish + glaze through update_finish_color)."""
    items = _FINISH_COLOR_ITEMS.get(self.finish_wood, [])
    if items:
        _set_enum_safe(self, "finish_color", items[0][0])
    _propagate_cabinet_style(self, context)


def update_finish_color(self, context):
    """Color gates varnish + glaze: reset both to their first compatible."""
    v = _FINISH_VARNISH_ITEMS.get(self.finish_color, [])
    if v:
        _set_enum_safe(self, "finish_varnish", v[0][0])
    g = _FINISH_GLAZE_ITEMS.get(self.finish_color, [])
    if g:
        _set_enum_safe(self, "finish_glaze", g[0][0])
    _propagate_cabinet_style(self, context)


def update_finish_overlay(self, context):
    """Overlay gates hinge AND drives FF sizing: reset to the overlay's
    default hinge, then map the catalog overlay onto one of the five FF
    sizing buckets by setting door_overlay_type (which runs
    update_face_frame_sizes -> writes the rail/stile widths + reveals)."""
    default = style_options.default_hinge_for_overlay(self.finish_overlay)
    if default:
        _set_enum_safe(self, "finish_hinge", default)
    bucket = style_options.ff_overlay_bucket(self.finish_overlay)
    if bucket:
        _set_enum_safe(self, "door_overlay_type", bucket)


# --- door / drawer front catalog caches (series -> shape -> panel) ---
# _front_is_drawer (which pool the style lives in) selects which catalog the
# cascade reads -- the door_styles pool models doors, drawer_front_styles
# models drawer fronts.
_DOOR_SERIES_ITEMS = _enum_items(style_options.DOOR_SERIES)
_DRAWER_SERIES_ITEMS = _enum_items(style_options.DRAWER_SERIES)
_DOOR_SHAPE_ITEMS = {s: _enum_items(style_options.door_shapes(s))
                     for s in style_options.DOOR_SERIES}
_DRAWER_SHAPE_ITEMS = {s: _enum_items(style_options.door_shapes(s, drawer=True))
                       for s in style_options.DRAWER_SERIES}
_DOOR_PANEL_ITEMS = {(s, sh): _enum_items(style_options.door_panels(s, sh))
                     for s in style_options.DOOR_SERIES
                     for sh in style_options.door_shapes(s)}
_DRAWER_PANEL_ITEMS = {(s, sh): _enum_items(style_options.door_panels(s, sh, drawer=True))
                       for s in style_options.DRAWER_SERIES
                       for sh in style_options.door_shapes(s, drawer=True)}


def _front_is_drawer(self):
    """A style reads the DRAWER catalog when it lives in the
    drawer_front_styles pool (vs door_styles). Derived from the RNA path so
    there is no separate Kind property. Defaults to door (False) if the path
    can't be read (e.g. transient / unlinked)."""
    try:
        return "drawer_front_styles" in self.path_from_id()
    except Exception:
        return False


def get_front_series_items(self, context):
    return _items_or_none(_DRAWER_SERIES_ITEMS if _front_is_drawer(self) else _DOOR_SERIES_ITEMS)


def get_front_shape_items(self, context):
    table = _DRAWER_SHAPE_ITEMS if _front_is_drawer(self) else _DOOR_SHAPE_ITEMS
    return _items_or_none(table.get(self.front_series, []))


def get_front_panel_items(self, context):
    table = _DRAWER_PANEL_ITEMS if _front_is_drawer(self) else _DOOR_PANEL_ITEMS
    return _items_or_none(table.get((self.front_series, self.front_shape), []))


def update_front_series(self, context):
    table = _DRAWER_SHAPE_ITEMS if _front_is_drawer(self) else _DOOR_SHAPE_ITEMS
    items = table.get(self.front_series, [])
    if items:
        _set_enum_safe(self, "front_shape", items[0][0])
    _apply_series_frame_to_door_style(self)
    _propagate_door_style(self, context)


def _apply_series_frame_to_door_style(self):
    """Derive the door style's construction (stile / rail widths, drawer-rail,
    panel inset/thickness, slab vs 5-piece) from the catalog series + front
    kind, and WRITE it into the construction fields. This keeps the catalog
    (series/shape/panel) as the single source of truth while the existing
    geometry path (assign_style_to_front) and the applied-panel sizing engine
    keep reading stile_width / rail_width / door_type unchanged. Widths in the
    baked spec are inches -> converted with units.inch()."""
    spec = style_options.frame_for_series(self.front_series)
    if spec.get('is_slab'):
        self.door_type = 'SLAB'
        return
    self.door_type = '5_PIECE'
    # Stile and rail unlock independently; the catalog cascade (any of kind/
    # series/shape/panel routes through here) must not clobber a field the
    # dealer manages. Everything else still derives.
    if not self.unlock_stile_width:
        self.stile_width = units.inch(spec['stile'])
    if not self.unlock_rail_width:
        # Drawer fronts use the series' drawer-rail width; doors use the rail.
        rail_in = spec['drw_rail'] if _front_is_drawer(self) else spec['rail']
        self.rail_width = units.inch(rail_in)
    if 'panel_inset' in spec:
        self.panel_inset = units.inch(spec['panel_inset'])
    if 'panel_thickness' in spec:
        self.panel_thickness = units.inch(spec['panel_thickness'])


def update_front_shape(self, context):
    table = _DRAWER_PANEL_ITEMS if _front_is_drawer(self) else _DOOR_PANEL_ITEMS
    items = table.get((self.front_series, self.front_shape), [])
    if items:
        _set_enum_safe(self, "front_panel", items[0][0])


def update_front_panel(self, context):
    """Panel chosen -> re-derive the frame construction from the series, push
    to assigned fronts, and re-apply materials so a Prep-for-Glass panel
    renders as glass immediately (and switching away restores the finish)."""
    _apply_series_frame_to_door_style(self)
    _propagate_door_style(self, context)
    _reapply_materials_for_door_style(self, context)


def update_rail_width(self, context):
    """The door's mid rail always mirrors the (top/bottom) rail width, so any
    change to rail_width -- catalog-derived or a manual override while frame
    widths are unlocked -- carries into mid_rail_width before propagating to
    assigned fronts. Setting mid_rail_width fires its own _propagate_door_style,
    so only propagate directly here when mid already matched (one rebuild)."""
    if self.mid_rail_width != self.rail_width:
        self.mid_rail_width = self.rail_width
    else:
        _propagate_door_style(self, context)


def update_unlock_frame_widths(self, context):
    """Shared lock-toggle callback for unlock_stile_width / unlock_rail_width.
    Re-deriving here writes only the still-LOCKED fields from the catalog
    series (the unlocked one is skipped in _apply_series_frame_to_door_style),
    so re-locking a field snaps it back to the series spec while a re-derive of
    an already-locked field is idempotent. The catalog rail write fires
    rail_width's update, which re-mirrors the mid rail."""
    _apply_series_frame_to_door_style(self)
    _propagate_door_style(self, context)


def _reapply_materials_for_door_style(door_style, context):
    """Re-run the CABINET material walk for every cabinet with a front using
    ``door_style``. Material application lives on the cabinet style
    (_apply_materials_to_cabinet), so a door-style change that affects a
    front's surfaces -- grain rotation OR a Prep-for-Glass panel -- only
    takes effect once that walk re-runs. Resolve each affected front's
    cabinet root + cabinet style and run it once per cabinet. Scoped to the
    active scene (same as _propagate_door_style)."""
    target = door_style.name
    ff = get_style_props()
    styles_by_name = {cs.name: cs for cs in ff.cabinet_styles}
    seen = set()
    for obj in context.scene.objects:
        if obj.get('DOOR_STYLE_NAME') != target:
            continue
        cur, cab = obj, None
        while cur is not None:
            if cur.get('IS_FACE_FRAME_CABINET_CAGE'):
                cab = cur
                break
            cur = cur.parent
        if cab is None or cab.name in seen:
            continue
        seen.add(cab.name)
        cs = styles_by_name.get(cab.get('STYLE_NAME'))
        if cs is not None:
            cs._apply_materials_to_cabinet(cab)


def update_grain_direction(self, context):
    """Grain direction changed -> re-apply materials to every cabinet with a
    front using this door style so the grain rotation takes effect
    immediately, no manual recalc."""
    _reapply_materials_for_door_style(self, context)


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
            if obj.get('STYLE_NAME') != target_name:
                continue
            if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
                self.assign_style_to_cabinet(obj)
            elif obj.get('APPLIANCE_TYPE') == 'HOOD':
                self.assign_style_to_hood(obj)


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
    rails keep the user's value. The bulk width writes are coalesced
    under suspend_propagate(); a single _propagate_cabinet_style at the
    end then pushes the new sizes to every scene cabinet carrying this
    style (same auto-propagation as the other style props - the manual
    Update Cabinets op is a force-resync fallback, not the normal path).
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
        for row in ('wall_stile', 'mid_stile', 'end_stile', 'blind_stile',
                    'butt_stile', 'inside_90_stile', 'angle_stile'):
            base_in, tall_in, upper_in = defaults[row]
            setattr(self, f"ff_{row}_width_base", units.inch(base_in))
            setattr(self, f"ff_{row}_width_tall", units.inch(tall_in))
            setattr(self, f"ff_{row}_width_upper", units.inch(upper_in))

    # One propagate now that the style is fully consistent.
    _propagate_cabinet_style(self, context)


# Out-of-box default front for a freshly created door / drawer-front style
# (ensure_default_styles). Craftsman / Square / Solid Wood Recessed is a
# common starting point; without it a new style falls on the alphabetical-
# first series. Applied in cascade order (series resets shape, shape resets
# panel) so each level sticks; valid for both the door and drawer catalogs.
_DEFAULT_FRONT = ("Craftsman", "Square", "Solid Wood Recessed")


def _apply_default_front_style(ds):
    series, shape, panel = _DEFAULT_FRONT
    _set_enum_safe(ds, "front_series", series)
    _set_enum_safe(ds, "front_shape", shape)
    _set_enum_safe(ds, "front_panel", panel)


def ensure_default_styles(context):
    """Make sure the scene carries at least one cabinet style and one
    door style. Operators that read from those collections call this
    on entry so the user never sees an empty-active state. Adds a
    Default cabinet style + Slab door style when empty; idempotent.
    """
    ff = get_style_props(context)
    if len(ff.cabinet_styles) == 0:
        cs = ff.cabinet_styles.add()
        cs.name = "Default"
        ff.active_cabinet_style_index = 0
    if len(ff.door_styles) == 0:
        ds = ff.door_styles.add()
        ds.name = "Craftsman Square Recessed Panel"
        _apply_default_front_style(ds)
        ff.active_door_style_index = 0
    if len(ff.drawer_front_styles) == 0:
        ds = ff.drawer_front_styles.add()
        ds.name = "Craftsman Square Recessed Panel"
        _apply_default_front_style(ds)
        ff.active_drawer_front_style_index = 0


def update_door_style_name(self, context):
    """Keep style names unique within the style's OWN pool (door_styles or
    drawer_front_styles -- independent lists, so a name may repeat across
    pools). Pool is read from the RNA path."""
    main = get_style_props(context)
    try:
        in_drawer = "drawer_front_styles" in self.path_from_id()
    except Exception:
        in_drawer = False
    pool = main.drawer_front_styles if in_drawer else main.door_styles
    base_name = self.name if self.name else "Door Style"
    existing = [s.name for s in pool if s != self]
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
class Face_Frame_Millwork_Item(PropertyGroup):
    """One millwork line item on a cabinet style's Style Section.

    Shown on the Style Section page as ``name`` + ``quantity`` (always in
    FEET). ``product_code`` is stored for later pricing. ``auto_collected``
    flags items added by the Collect Millwork scan so a re-collect can replace
    just those while leaving hand-typed items alone.
    """
    name: StringProperty(
        name="Name",
        description="Millwork item name (e.g. 'Finish Toe Kick', '51 Crown')",
        default="Millwork",
    )  # type: ignore
    quantity: FloatProperty(
        name="Quantity (ft)",
        description="Linear quantity in feet",
        default=0.0,
        min=0.0,
        precision=1,
    )  # type: ignore
    product_code: StringProperty(
        name="Product Code",
        description="Millwork product code (used for pricing)",
        default="",
    )  # type: ignore
    auto_collected: BoolProperty(
        name="Auto Collected",
        description="True when added by the Collect Millwork scan (replaced on "
                    "re-collect; hand-typed items are kept)",
        default=False,
    )  # type: ignore


class Face_Frame_Special_Effect(PropertyGroup):
    """One special-effect line on a cabinet style's finish (e.g. a distress
    or rub-through). The built-in ``name`` holds the catalog effect name
    (offered names gated by the style's wood + color via
    style_options.special_effects_for). ``ref_name`` / ``ref_image`` are an
    optional finish reference: the name is appended to the effect's FINISH
    row on the Style Section page, the image is collected into the page's
    right-side references box (mirrors the per-finish refs on the style)."""
    ref_name: StringProperty(
        name="Reference",
        description="Reference name for this special effect, shown on the Style Section finish row",
        default="",
    )  # type: ignore
    ref_image: StringProperty(
        name="Reference Image",
        description="Path to a reference image for this special effect, shown in the Style Section references box",
        subtype='FILE_PATH',
        default="",
    )  # type: ignore


def get_cabinet_extra_front_style_items(self, context):
    """Items for an extra-front-style row on a cabinet style. Resolves the
    pool by the row's RNA path (the _front_is_drawer trick): a row living in
    extra_drawer_front_styles reads the drawer-front pool, otherwise the door
    pool. Works on a collection item as self because it derives the pool from
    the path, not the row's own state."""
    ff = get_style_props(context)
    try:
        drawer = "extra_drawer_front_styles" in self.path_from_id()
    except Exception:
        drawer = False
    pool = ff.drawer_front_styles if drawer else ff.door_styles
    items = [(ds.name, ds.name, ds.name, i) for i, ds in enumerate(pool)]
    if not items:
        items.append(('NONE', "(none defined)", "No front styles defined", 0))
    return items


class Face_Frame_Cabinet_Extra_Front_Style(PropertyGroup):
    """One additional door- or drawer-front style listed on a cabinet style.

    The primary door_style / drawer_front_style drives the geometry; these
    extra entries document the OTHER front styles a designer assigns to this
    cabinet style's cabinets in 3D, so the Style Section page can list every
    front style in use, not just the primary. Pure documentation -- no
    geometric effect. The pool (door vs drawer front) is fixed by which
    collection the row lives in.
    """
    style: EnumProperty(
        name="Front Style",
        description="Additional front style shown on the Style Section page",
        items=get_cabinet_extra_front_style_items,
    )  # type: ignore


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
    rename_anchor: StringProperty(
        name="Rename Anchor",
        description="Internal: the style's previous name, used to propagate a "
                    "rename to cabinets tagged with the old STYLE_NAME",
        default="",
        options={'HIDDEN'},
    )  # type: ignore

    show_expanded: BoolProperty(
        name="Show Expanded",
        description="Show expanded style options",
        default=False,
    )  # type: ignore

    color_in_2d_drawings: FloatVectorProperty(
        name="2D Drawing Color",
        description="Fill color for cabinets of this style in 2D shop drawings",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
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

    # ---- Catalog finish spec (compatibility-filtered; see style_options) ----
    # The correct wood/color/varnish/glaze + overlay/hinge selections with the
    # proper cascade. Spec-only for now (does not drive material or FF sizing).
    finish_wood: EnumProperty(
        name="Wood Specie",
        description="Catalog wood specie (gates the available colors)",
        items=get_finish_wood_items,
        update=update_finish_wood,
    )  # type: ignore
    finish_color: EnumProperty(
        name="Color",
        description="Finish color available for the chosen wood specie",
        items=get_finish_color_items,
        update=update_finish_color,
    )  # type: ignore
    finish_varnish: EnumProperty(
        name="Varnish",
        description="Varnish available for the chosen color (stain colors only)",
        items=get_finish_varnish_items,
    )  # type: ignore
    finish_glaze: EnumProperty(
        name="Glaze",
        description="Glaze available for the chosen color",
        items=get_finish_glaze_items,
    )  # type: ignore
    finish_overlay: EnumProperty(
        name="Overlay (catalog)",
        description="Catalog door overlay (gates the available hinges)",
        items=get_finish_overlay_items,
        update=update_finish_overlay,
    )  # type: ignore
    finish_hinge: EnumProperty(
        name="Hinge",
        description="Hinge available for the chosen overlay",
        items=get_finish_hinge_items,
    )  # type: ignore

    # ---- Interior material ----
    interior_material_type: EnumProperty(
        name="Interior Material",
        description="Material for cabinet interior",
        items=[
            ('MAPLE_PLY', "UV Plywood", "UV plywood"),
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

    # Joint stile types (Butt / Inside 90 / Angle) - width-only, sourced
    # from the overlay table like the other stile rows; defaults match CLASSIC.
    ff_butt_stile_width_base: FloatProperty(
        name="Butt Stile (Base)", default=units.inch(1.25),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_butt_stile_width_tall: FloatProperty(
        name="Butt Stile (Tall)", default=units.inch(1.25),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_butt_stile_width_upper: FloatProperty(
        name="Butt Stile (Upper)", default=units.inch(1.25),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_inside_90_stile_width_base: FloatProperty(
        name="Inside 90 Stile (Base)", default=units.inch(3.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_inside_90_stile_width_tall: FloatProperty(
        name="Inside 90 Stile (Tall)", default=units.inch(3.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_inside_90_stile_width_upper: FloatProperty(
        name="Inside 90 Stile (Upper)", default=units.inch(2.0),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_angle_stile_width_base: FloatProperty(
        name="Angle Stile (Base)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_angle_stile_width_tall: FloatProperty(
        name="Angle Stile (Tall)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore
    ff_angle_stile_width_upper: FloatProperty(
        name="Angle Stile (Upper)", default=units.inch(1.5),
        unit='LENGTH', precision=4,
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Rail unlock toggles (9: 3 row types x 3 cabinet types) ----
    # When False (locked), the rail's width follows the overlay default
    # and is rewritten on overlay change AND immediately on re-lock (the
    # update callback re-derives every locked cell). When True (unlocked),
    # the user's value persists.
    unlock_base_top_rail: BoolProperty(name="Unlock Base Top Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_tall_top_rail: BoolProperty(name="Unlock Tall Top Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_upper_top_rail: BoolProperty(name="Unlock Upper Top Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_base_bottom_rail: BoolProperty(name="Unlock Base Bottom Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_tall_bottom_rail: BoolProperty(name="Unlock Tall Bottom Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_upper_bottom_rail: BoolProperty(name="Unlock Upper Bottom Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_base_mid_rail: BoolProperty(name="Unlock Base Mid Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_tall_mid_rail: BoolProperty(name="Unlock Tall Mid Rail", default=False, update=update_face_frame_sizes)  # type: ignore
    unlock_upper_mid_rail: BoolProperty(name="Unlock Upper Mid Rail", default=False, update=update_face_frame_sizes)  # type: ignore

    # ---- Door / drawer-front style refs (by name into Face_Frame_Scene_Props.door_styles) ----
    door_style: EnumProperty(
        name="Door Style",
        description="Door style applied to door fronts on cabinets carrying this style",
        items=get_door_style_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    drawer_front_style: EnumProperty(
        name="Drawer Front Style",
        description="Drawer front style applied to drawer fronts on cabinets carrying this style",
        items=get_drawer_front_style_enum_items,
        update=_propagate_cabinet_style,
    )  # type: ignore

    # ---- Style-section descriptors (free text shown on the Style Section
    # page). These have no geometric effect -- they're presentation fields the
    # dealer types in. Defaults mirror common CWP selections so a fresh style
    # reads sensibly. Editable from the Style Sections panel.
    ss_corner_treatment: EnumProperty(
        name="Corner Treatment",
        description="Corner treatment for the style section page",
        items=[
            ('1/4" x 1/4" Chamfer', '1/4" x 1/4" Chamfer', ''),
            ('Cove', 'Cove', ''),
            ('1/8" Radius', '1/8" Radius', ''),
            ('Square', 'Square', ''),
            ('1/4" Radius', '1/4" Radius', ''),
            ('3/8" Radius', '3/8" Radius', ''),
        ],
        default='Square',
    )  # type: ignore
    ss_fin_opening_edge: EnumProperty(
        name="Fin Opening Edge",
        description="Finished opening edge treatment for the style section page",
        items=[
            ('1/8" Radius', '1/8" Radius', ''),
            ('1/4" Radius', '1/4" Radius', ''),
            ('1/4" Drop Radius', '1/4" Drop Radius', ''),
            ('1/4" x 1/4" Chamfer', '1/4" x 1/4" Chamfer', ''),
            ('3/8" Radius', '3/8" Radius', ''),
            ('3/8" Drop Radius', '3/8" Drop Radius', ''),
            ('Beaded', 'Beaded', ''),
            ('Classic Cut', 'Classic Cut', ''),
            ('Cove', 'Cove', ''),
            ('Square', 'Square', ''),
        ],
        default='Square',
    )  # type: ignore
    ss_drawer_grain: StringProperty(
        name="Drawer Grain",
        description="Override the drawer-front grain on the style section page; "
                    "blank uses the drawer front style's grain direction",
        default="",
    )  # type: ignore
    ss_drawer_top_opening_height: StringProperty(
        name="Top Opening Height",
        description="Override the top drawer opening height on the style section "
                    "page; blank uses hb_face_frame.top_drawer_opening_height",
        default="",
    )  # type: ignore
    ss_drawer_slides: EnumProperty(
        name="Drawer Slides",
        description="Drawer slide hardware for the style section page",
        items=[
            ('Tandem BLUMOTION', 'Tandem BLUMOTION', ''),
            ('KV8400', 'KV8400', ''),
            ('KV4270', 'KV4270', ''),
        ],
        default='Tandem BLUMOTION',
    )  # type: ignore
    ss_drawer_box_construction: EnumProperty(
        name="Box Construction",
        description="Drawer box construction for the style section page",
        items=[
            ('French', 'French', ''),
            ('English', 'English', ''),
        ],
        default='French',
    )  # type: ignore

    # ---- Style-section OVERRIDES for the catalog-backed fields ----
    # Each is blank by default: blank => the page shows the catalog/derived
    # value (wood, color, overlay, hinge, the composed door/drawer name, edge
    # profile); type anything in to OVERRIDE what prints for that style. This
    # lets a dealer hand-correct a single line without changing the cabinet's
    # actual catalog selection. Resolved by ``style_section_value``.
    ss_wood: StringProperty(
        name="Wood (override)",
        description="Override the wood text on the style section page (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_interior: StringProperty(
        name="Interior (override)",
        description="Override the interior text (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_overlay: StringProperty(
        name="Overlay (override)",
        description="Override the overlay text (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_color: StringProperty(
        name="Color (override)",
        description="Override the color text (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_varnish: StringProperty(
        name="Varnish (override)",
        description="Override the varnish text (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_glaze: StringProperty(
        name="Glaze (override)",
        description="Override the glaze text (blank = catalog value)",
        default="",
    )  # type: ignore
    # Finish REFERENCE name + image per Color / Varnish / Glaze. A ref name
    # is appended to the field's FINISH row on the Style Section page
    # ("AUBURN – SUNSET"); a ref image is collected into the page's right-side
    # references box. Both are independent and optional (either alone works).
    ss_color_ref_name: StringProperty(
        name="Color Reference",
        description="Reference name for the color, shown on the Style Section finish row",
        default="",
    )  # type: ignore
    ss_color_ref_image: StringProperty(
        name="Color Reference Image",
        description="Path to a reference image for the color, shown in the Style Section references box",
        subtype='FILE_PATH',
        default="",
    )  # type: ignore
    ss_varnish_ref_name: StringProperty(
        name="Varnish Reference",
        description="Reference name for the varnish, shown on the Style Section finish row",
        default="",
    )  # type: ignore
    ss_varnish_ref_image: StringProperty(
        name="Varnish Reference Image",
        description="Path to a reference image for the varnish, shown in the Style Section references box",
        subtype='FILE_PATH',
        default="",
    )  # type: ignore
    ss_glaze_ref_name: StringProperty(
        name="Glaze Reference",
        description="Reference name for the glaze, shown on the Style Section finish row",
        default="",
    )  # type: ignore
    ss_glaze_ref_image: StringProperty(
        name="Glaze Reference Image",
        description="Path to a reference image for the glaze, shown in the Style Section references box",
        subtype='FILE_PATH',
        default="",
    )  # type: ignore
    ss_door: StringProperty(
        name="Door Style (override)",
        description="Override the door style text (blank = composed catalog name)",
        default="",
    )  # type: ignore
    ss_hinge: StringProperty(
        name="Hinge (override)",
        description="Override the hinge text (blank = catalog value)",
        default="",
    )  # type: ignore
    ss_drawer: StringProperty(
        name="Drawer Style (override)",
        description="Override the drawer style text (blank = composed catalog name)",
        default="",
    )  # type: ignore
    # Path to a drawer-box brand logo image. When set, the Style Section page
    # renders the logo (textured quad) inside the DRAWERS section. FILE_PATH so
    # the sidebar shows a file-picker. Stored per cabinet style like the other
    # ss_* fields; resolved by style_section.style_section_value.
    ss_drawer_box_brand: StringProperty(
        name="Drawer Box Brand",
        description="Path to a drawer-box brand logo image shown in the DRAWERS section of the Style Section page",
        subtype='FILE_PATH',
        default="",
    )  # type: ignore
    ss_edge_profile: EnumProperty(
        name="Edge Profile",
        description="Edge profile for the style section page (None = use the door style's edge profile)",
        items=[
            ('None', 'None', ''),
            ('Bay', 'Bay', ''),
            ('Beveled', 'Beveled', ''),
            ('Chamfer', 'Chamfer', ''),
            ('Classic Cut', 'Classic Cut', ''),
            ('Drop Radius', 'Drop Radius', ''),
            ('Eclipse', 'Eclipse', ''),
            ('Estate', 'Estate', ''),
            ('New Cut', 'New Cut', ''),
            ('Square', 'Square', ''),
            ('1/8" Radius', '1/8" Radius', ''),
            ('1/4" Radius', '1/4" Radius', ''),
            ('3/8" Radius', '3/8" Radius', ''),
            ('3/8" Inset 1/8" Radius', '3/8" Inset 1/8" Radius', ''),
            ('3/8" Inset Radius', '3/8" Inset Radius', ''),
            ('3/8" Inset square', '3/8" Inset square', ''),
        ],
        default='None',
    )  # type: ignore

    # Custom-text companions for the toggleable dropdown fields. When
    # <field>_is_custom is set, the UI shows <field>_custom (free text) in
    # place of the dropdown and the style section resolves the typed value --
    # for entering a value the catalog list doesn't offer.
    ss_corner_treatment_is_custom: BoolProperty(name="Custom Corner Treatment", default=False)  # type: ignore
    ss_corner_treatment_custom: StringProperty(name="Corner Treatment", default="")  # type: ignore
    ss_fin_opening_edge_is_custom: BoolProperty(name="Custom Fin Opening Edge", default=False)  # type: ignore
    ss_fin_opening_edge_custom: StringProperty(name="Fin Opening Edge", default="")  # type: ignore
    ss_drawer_slides_is_custom: BoolProperty(name="Custom Drawer Slides", default=False)  # type: ignore
    ss_drawer_slides_custom: StringProperty(name="Drawer Slides", default="")  # type: ignore
    ss_drawer_box_construction_is_custom: BoolProperty(name="Custom Box Construction", default=False)  # type: ignore
    ss_drawer_box_construction_custom: StringProperty(name="Box Construction", default="")  # type: ignore
    ss_edge_profile_is_custom: BoolProperty(name="Custom Edge Profile", default=False)  # type: ignore
    ss_edge_profile_custom: StringProperty(name="Edge Profile", default="")  # type: ignore
    ss_wood_is_custom: BoolProperty(name="Custom Wood", default=False)  # type: ignore
    ss_wood_custom: StringProperty(name="Wood", default="")  # type: ignore
    ss_interior_is_custom: BoolProperty(name="Custom Interior", default=False)  # type: ignore
    ss_interior_custom: StringProperty(name="Interior", default="")  # type: ignore
    ss_overlay_is_custom: BoolProperty(name="Custom Overlay", default=False)  # type: ignore
    ss_overlay_custom: StringProperty(name="Overlay", default="")  # type: ignore
    ss_color_is_custom: BoolProperty(name="Custom Color", default=False)  # type: ignore
    ss_color_custom: StringProperty(name="Color", default="")  # type: ignore
    ss_varnish_is_custom: BoolProperty(name="Custom Varnish", default=False)  # type: ignore
    ss_varnish_custom: StringProperty(name="Varnish", default="")  # type: ignore
    ss_glaze_is_custom: BoolProperty(name="Custom Glaze", default=False)  # type: ignore
    ss_glaze_custom: StringProperty(name="Glaze", default="")  # type: ignore
    ss_door_is_custom: BoolProperty(name="Custom Door", default=False)  # type: ignore
    ss_door_custom: StringProperty(name="Door", default="")  # type: ignore
    ss_hinge_is_custom: BoolProperty(name="Custom Hinge", default=False)  # type: ignore
    ss_hinge_custom: StringProperty(name="Hinge", default="")  # type: ignore
    ss_drawer_is_custom: BoolProperty(name="Custom Drawer Front", default=False)  # type: ignore
    ss_drawer_custom: StringProperty(name="Drawer Front", default="")  # type: ignore

    # ---- Style-section millwork (per-style list shown under the column on the
    # Style Section page). Each item is name + quantity(ft) + product_code.
    # Populated by hand and/or the Collect Millwork scan.
    millwork_items: CollectionProperty(
        name="Millwork Items",
        type=Face_Frame_Millwork_Item,
    )  # type: ignore
    millwork_index: IntProperty(
        name="Millwork Index",
        default=0,
    )  # type: ignore

    # ---- Style-section special effects (per-style finish add-ons shown in
    # the FINISH section + on the page). Each item is a catalog effect name;
    # the Add dialog offers the wood+color-compatible set.
    special_effects: CollectionProperty(
        name="Special Effects",
        type=Face_Frame_Special_Effect,
    )  # type: ignore
    special_effect_index: IntProperty(
        name="Special Effect Index",
        default=0,
    )  # type: ignore

    # ---- Extra front styles (Style Section documentation) ----
    # The primary door_style / drawer_front_style drives geometry; these list
    # the ADDITIONAL door / drawer-front styles a designer has assigned to this
    # cabinet style's cabinets in 3D, so the Style Section page documents every
    # front style in use. Pure documentation -- no geometric effect.
    extra_door_styles: CollectionProperty(
        name="Extra Door Styles",
        type=Face_Frame_Cabinet_Extra_Front_Style,
    )  # type: ignore
    extra_drawer_front_styles: CollectionProperty(
        name="Extra Drawer Front Styles",
        type=Face_Frame_Cabinet_Extra_Front_Style,
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
    show_finish_references: BoolProperty(
        name="Show Reference Fields",
        description="Show the per-finish reference name + image fields (Color / Varnish / Glaze / Special Effects) in this style's editor",
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
            # Standard finish is catalog-driven (finish_wood / finish_color).
            wood_materials.update_finish_material_from_catalog(self)
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
    # callback. Tables mirror the reference library defaults.
    _FF_SIZE_DEFAULTS = {
        'CLASSIC': {
            'top_rail':    (1.5, 3.5, 3.5),
            'bottom_rail': (1.5, 1.5, 1.5),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (2.0, 2.0, 2.0),
            'mid_stile':   (2.0, 2.0, 2.0),
            'end_stile':   (2.0, 2.0, 2.0),
            'blind_stile': (3.0, 3.0, 2.0),
            'butt_stile':      (1.25, 1.25, 1.25),
            'inside_90_stile': (3.0, 3.0, 2.0),
            'angle_stile':     (1.5, 1.5, 1.5),
        },
        'TRANSITIONAL': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (2.0, 2.0, 2.0),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
            'butt_stile':      (1.25, 1.25, 1.25),
            'inside_90_stile': (3.0, 3.0, 2.0),
            'angle_stile':     (1.5, 1.5, 1.5),
        },
        'FULL': {
            'top_rail':    (1.125, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.125),
            'mid_rail':    (2.0, 2.0, 2.0),
            'wall_stile':  (2.5, 2.5, 2.5),
            'mid_stile':   (2.25, 2.25, 2.25),
            'end_stile':   (1.25, 1.25, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
            'butt_stile':      (1.125, 1.125, 1.125),
            'inside_90_stile': (3.5, 3.5, 3.5),
            'angle_stile':     (1.75, 1.75, 1.75),
        },
        'PARTIAL_INSET': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
            'butt_stile':      (1.25, 1.25, 1.25),
            'inside_90_stile': (2.5, 2.5, 1.5),
            'angle_stile':     (1.5, 1.5, 1.5),
        },
        'FULL_INSET': {
            'top_rail':    (1.5, 3.0, 3.0),
            'bottom_rail': (1.25, 1.25, 1.25),
            'mid_rail':    (1.5, 1.5, 1.5),
            'wall_stile':  (1.5, 1.5, 1.5),
            'mid_stile':   (1.5, 1.5, 1.5),
            'end_stile':   (1.5, 1.5, 1.5),
            'blind_stile': (3.75, 3.75, 2.75),
            'butt_stile':      (1.25, 1.25, 1.25),
            'inside_90_stile': (2.5, 2.5, 1.5),
            'angle_stile':     (1.5, 1.5, 1.5),
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
        # Assign overwrites whatever the user had per-
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

    def assign_style_to_hood(self, hood_obj):
        """Apply this cabinet style's exterior finish to a wood hood and
        tag it with the style name. Hoods have no face frame, overlay, or
        door, so only the finish material is meaningful - the width /
        overlay / door wiring is intentionally skipped. The STYLE_NAME tag
        lets style edits and Update Cabinets re-reach the hood (see
        _propagate_cabinet_style).
        """
        finish_mat, finish_mat_rotated = self.get_finish_material()
        if finish_mat is None:
            return
        hood_obj['STYLE_NAME'] = self.name
        from ..common import wood_hoods
        wood_hoods.apply_finish_to_hood(hood_obj, finish_mat, finish_mat_rotated)

    # =================================================================
    # Material walking
    # =================================================================
    # Visible exterior surfaces (finish material on top + bottom + edges).
    _FINISH_EXTERIOR_ROLES = {
        # Face frame members
        'TOP_RAIL', 'BOTTOM_RAIL', 'LEFT_STILE', 'RIGHT_STILE', 'MID_STILE',
        'MID_RAIL', 'BAY_MID_RAIL', 'BAY_MID_STILE',
        'INTERIOR_FF_RAIL', 'INTERIOR_FF_STILE',
        # Fronts
        'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT', 'TILT_OUT', 'INSET_PANEL',
        # Furniture / veneer wood top (dresser products)
        'FURNITURE_TOP',
        # Finished back closing a hutch upper's dropped-end recess
        'HUTCH_BACK',
        # Over-stool shelf between the extended legs
        'OVERSTOOL_SHELF',
        # Visible toe kick parts
        'CORNER_MID_RAIL', 'CORNER_FALSE_FRONT',
        'FINISH_TOE_KICK', 'CORNER_LEFT_FINISH_KICK', 'CORNER_RIGHT_FINISH_KICK',
        'LEFT_KICK_RETURN', 'RIGHT_KICK_RETURN',
        # Loose ladder sub-base boards - finished material
        'LOOSE_KICK_FRONT', 'LOOSE_KICK_REAR',
        'LOOSE_KICK_END_LEFT', 'LOOSE_KICK_END_RIGHT',
        # Leg product boards - finished material
        'LEG_PANEL_LEFT', 'LEG_PANEL_RIGHT', 'LEG_STILE',
        'LEG_TK_STILE', 'LEG_TK_FILLER',
        'LEG_FINISH_X_LEFT', 'LEG_FINISH_X_RIGHT',
        # Floating shelf boards - finished material
        'SHELF_FRONT', 'SHELF_TOP', 'SHELF_BOTTOM',
        'SHELF_PANEL_LEFT', 'SHELF_PANEL_RIGHT',
        # Blind ends + finished back + flush skins / decorative panels
        'BLIND_PANEL_LEFT', 'BLIND_PANEL_RIGHT',
        'FINISHED_BACK', 'FLUSH_X', 'BEADBOARD', 'SHIPLAP',
        # Partition skins fill the exposed step between bays of differing
        # height / depth (added when a bay's height is adjusted) and are
        # visible through the opening, so they take the exterior finish
        # material, not the interior material.
        'PARTITION_SKIN',
        # Per-bay finish liner panels (left / right / top / back) added
        # when a bay is finished - their whole purpose is to show the
        # exterior finish inside the opening.
        'BAY_FINISH',
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
        # Leg product back + nailers
        'LEG_BACK', 'LEG_NAILER_LEFT', 'LEG_NAILER_RIGHT',
        # Internal dividers / shelves
        'BAY_DIVISION', 'BAY_SHELF', 'MID_DIVISION',
        # Drawer box
        'DRAWER_BOX',
        # Interior items
        'ADJUSTABLE_SHELF', 'PULLOUT_SHELF', 'PULLOUT_SPACER',
        'ROLLOUT_BOX', 'ROLLOUT_SPACER',
        'TRAY_DIVIDER', 'TRAY_LOCKED_SHELF',
        'VANITY_SHELF', 'VANITY_SUPPORT',
        'INTERIOR_FIXED_SHELF', 'INTERIOR_DIVISION',
        # Corner cabinet carcass: bottom, top, backs, side panels, and
        # toe kick subfronts. Corner finish kicks are visible exterior
        # (listed above); corner sides default to interior - a finished
        # exposed side is a follow-up, same as standard cabinets.
        'CORNER_BOTTOM', 'CORNER_TOP',
        'CORNER_LEFT_BACK', 'CORNER_RIGHT_BACK',
        'CORNER_LEFT_SIDE', 'CORNER_RIGHT_SIDE',
        'CORNER_LEFT_KICK', 'CORNER_RIGHT_KICK', 'DIAGONAL_KICK',
        # Corner loose ladder rear rails + end boards (utility sub-base,
        # same interior material as the corner kicks above).
        'CORNER_LOOSE_REAR_LEFT', 'CORNER_LOOSE_REAR_RIGHT',
        'CORNER_LOOSE_END_LEFT', 'CORNER_LOOSE_END_RIGHT',
        'CORNER_PARTITION', 'CORNER_TRAY_DIVIDER', 'CORNER_SHELF',
        'CORNER_ANGLED_BACK',
    }

    # Roles that read materials from the 5-piece door modifier instead
    # of (or in addition to) the cutpart surface inputs.
    _FRONT_ROLES = {'DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT', 'FALSE_FRONT', 'TILT_OUT'}

    # Interior shelving that follows the bay's finish_bay flag: a finished
    # bay shows the exterior finish on its shelves too, otherwise they
    # stay interior. Glass shelves and functional hardware (pullouts /
    # rollouts / trays) are excluded.
    _BAY_FINISH_SHELF_ROLES = {
        'ADJUSTABLE_SHELF', 'INTERIOR_FIXED_SHELF', 'BAY_SHELF', 'VANITY_SHELF',
        # Corner cabinet shelves live under the cabinet root (no bay /
        # opening cage above them), so the finish walk resolves to
        # not-finished and they take the interior material -- correct,
        # and better than the no-material fallthrough they had before.
        'CORNER_SHELF',
    }

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

    def _door_style_grain(self, front_obj):
        """Grain direction ('VERTICAL' / 'HORIZONTAL', default VERTICAL) of the
        style assigned to front_obj, resolved by DOOR_STYLE_NAME. A DOOR-role
        front resolves in the door_styles pool; a drawer front in the separate
        drawer_front_styles pool. The two are independent lists, so a name may
        appear in both -- the front's role picks the right pool.
        """
        ds_name = front_obj.get('DOOR_STYLE_NAME')
        if not ds_name:
            return 'VERTICAL'
        ff = get_style_props()
        role = front_obj.get('hb_part_role')
        pool = (ff.drawer_front_styles
                if role in ('DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT')
                else ff.door_styles)
        for ds in pool:
            if ds.name == ds_name:
                return ds.grain_direction
        return 'VERTICAL'

    def _door_style_is_glass(self, front_obj):
        """True if the style assigned to front_obj is a 'Prep for Glass' panel
        (the centre panel should render as glass). Resolved by DOOR_STYLE_NAME
        in the role-appropriate pool, same lookup as _door_style_grain."""
        ds_name = front_obj.get('DOOR_STYLE_NAME')
        if not ds_name:
            return False
        ff = get_style_props()
        role = front_obj.get('hb_part_role')
        pool = (ff.drawer_front_styles
                if role in ('DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT')
                else ff.door_styles)
        for ds in pool:
            if ds.name == ds_name:
                return getattr(ds, 'front_panel', '') == 'Prep for Glass'
        return False

    @staticmethod
    def _get_glass_panel_material():
        """Get/create the 'Door Panel Glass' material for prep-for-glass door
        panels. Mirrors the Pulito reference: a Glass BSDF mixed 50/50 with a
        Transparent shader -- near-clear, very slight blue tint, roughness 0,
        IOR 1.45. Cached by name. Socket writes are guarded so a renamed input
        on a future Blender can't raise."""
        name = "Door Panel Glass"
        mat = bpy.data.materials.get(name)
        if mat is not None:
            return mat
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (400, 0)
        mix = nodes.new('ShaderNodeMixShader')
        mix.location = (200, 0)
        if 'Fac' in mix.inputs:
            mix.inputs['Fac'].default_value = 0.5
        glass = nodes.new('ShaderNodeBsdfGlass')
        glass.location = (0, 100)
        if 'Color' in glass.inputs:
            glass.inputs['Color'].default_value = (0.95, 0.97, 1.0, 1.0)
        if 'Roughness' in glass.inputs:
            glass.inputs['Roughness'].default_value = 0.0
        if 'IOR' in glass.inputs:
            glass.inputs['IOR'].default_value = 1.45
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        transparent.location = (0, -100)
        if 'Color' in transparent.inputs:
            transparent.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        links.new(transparent.outputs['BSDF'], mix.inputs[1])
        links.new(glass.outputs['BSDF'], mix.inputs[2])
        links.new(mix.outputs['Shader'], output.inputs['Surface'])
        # Blender 5.x EEVEE-Next dropped Material.blend_method; set only if present.
        if hasattr(mat, 'blend_method'):
            mat.blend_method = 'BLEND'
        if hasattr(mat, 'use_backface_culling'):
            mat.use_backface_culling = False
        return mat

    def _set_door_modifier_materials(self, front_obj, finish_mat, finish_mat_rotated):
        """Set Stile / Rail / Panel material on a front's 'Door Style'
        CPM_5PIECEDOOR modifier, when present. Slab fronts have no
        such modifier and skip silently. Rails get the rotated variant
        so cross-grain reads correctly. The PANEL follows the door style's
        grain_direction: VERTICAL -> finish_mat, HORIZONTAL -> the rotated
        variant (falling back to finish_mat when no rotated material exists).
        """
        # Panel grain follows the door style's grain_direction (see
        # _door_style_grain): HORIZONTAL feeds the rotated finish material.
        panel_mat = finish_mat
        if (self._door_style_grain(front_obj) == 'HORIZONTAL'
                and finish_mat_rotated is not None):
            panel_mat = finish_mat_rotated
        # Prep-for-glass fronts render the centre panel as glass, not wood.
        if self._door_style_is_glass(front_obj):
            panel_mat = self._get_glass_panel_material()
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
            if 'Panel Material' in tree and panel_mat is not None:
                # panel_mat is the glass material for prep-for-glass fronts,
                # else the finish (rotated for HORIZONTAL grain -- see above).
                mod[tree['Panel Material'].identifier] = panel_mat
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
            if role == 'WING':
                # Attached wing: a free-standing angled return, finished on its
                # OUTER face only (Bottom Surface = finish, like a FINISHED
                # side); inner face + edges stay interior. Mirror Z is set per
                # side at create so Bottom = the outer face.
                self._set_part_surfaces_split(
                    child,
                    top_mat=interior_mat,
                    bottom_mat=finish_mat,
                    edge_mat=interior_mat_rotated,
                )
                continue

            # Interior shelves in a finished region take the exterior
            # finish so the finished look continues onto the shelving;
            # shelves elsewhere stay interior. A shelf is finished when its
            # bay is finished (nearest IS_FACE_FRAME_BAY_CAGE -> finish_bay)
            # OR its opening is finished (nearest IS_FACE_FRAME_OPENING_CAGE
            # -> finish_opening).
            if role in self._BAY_FINISH_SHELF_ROLES:
                bay_cage = self._bay_cage_for_part(child)
                opening_cage = self._opening_cage_for_part(child)
                finished = (
                    (bay_cage is not None
                     and bay_cage.face_frame_bay.finish_bay)
                    or (opening_cage is not None
                        and opening_cage.face_frame_opening.finish_opening)
                )
                if finish_mat is not None and finished:
                    self._set_part_surfaces(child, finish_mat, finish_mat_rotated)
                else:
                    self._set_part_surfaces(child, interior_mat, interior_mat_rotated)
                continue

            if role in self._FRONT_ROLES:
                # Front cutpart face honors the door style's grain. This IS
                # the visible face for a SLAB front (HORIZONTAL rotates it);
                # a 5-piece front hides the cutpart behind the door modifier
                # (its panel grain is set below), so rotating here is a
                # harmless visual no-op. Edges keep the rotated variant.
                face_mat = finish_mat
                if (self._door_style_grain(child) == 'HORIZONTAL'
                        and finish_mat_rotated is not None):
                    face_mat = finish_mat_rotated
                self._set_part_surfaces(child, face_mat, finish_mat_rotated)
            elif role in self._FINISH_EXTERIOR_ROLES:
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

    def _bay_cage_for_part(self, part_obj):
        """Walk up from a part to its nearest face-frame bay cage
        (IS_FACE_FRAME_BAY_CAGE) so per-bay flags like finish_bay can be
        read from bay_cage.face_frame_bay. Returns None if the part isn't
        under a bay cage (e.g. carcass parts parented to the cabinet root).
        The tag string mirrors types_face_frame.TAG_BAY_CAGE.
        """
        node = part_obj.parent
        while node is not None:
            if node.get('IS_FACE_FRAME_BAY_CAGE'):
                return node
            node = node.parent
        return None

    def _opening_cage_for_part(self, part_obj):
        """Walk up from a part to its nearest face-frame opening cage
        (IS_FACE_FRAME_OPENING_CAGE) so per-opening flags like
        finish_opening can be read from opening_cage.face_frame_opening.
        Returns None if the part isn't under an opening cage. The tag
        string mirrors types_face_frame.TAG_OPENING_CAGE.
        """
        node = part_obj.parent
        while node is not None:
            if node.get('IS_FACE_FRAME_OPENING_CAGE'):
                return node
            node = node.parent
        return None

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
        'BUTT': 'butt_stile',
        'INSIDE_90': 'inside_90_stile',
        'ANGLE': 'angle_stile',
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
        # Respect the per-cabinet unlock flags: a style change re-applies the
        # style to every cabinet carrying it, so writing these unconditionally
        # would wipe a cabinet's own rail/stile override back to the style
        # default. An unlocked field keeps the cabinet's value - mirrors the
        # bay-rail / split unlock handling noted below.
        if not props.unlock_top_rail:
            props.top_rail_width = self._ff_size_for('top_rail', col)
        if not props.unlock_bottom_rail:
            props.bottom_rail_width = self._ff_size_for('bottom_rail', col)

        # Per-side stile widths: each side picks its row by its
        # stile_type. Unknown stile types fall back to end_stile.
        left_row = self._STILE_TYPE_TO_ROW.get(props.left_stile_type, 'end_stile')
        right_row = self._STILE_TYPE_TO_ROW.get(props.right_stile_type, 'end_stile')
        if not props.unlock_left_stile:
            props.left_stile_width = self._ff_size_for(left_row, col)
        if not props.unlock_right_stile:
            props.right_stile_width = self._ff_size_for(right_row, col)

        # Bay-level rail widths are intentionally NOT written here. Each
        # bay carries its own top/bottom rail copy with an unlock flag;
        # the recalc that follows this apply runs _distribute_bay_rails,
        # which pushes the cabinet rail width into locked bays and leaves
        # an unlocked bay's per-bay override intact. Writing every bay
        # directly here would clobber that override.

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
        #    A split whose unlock_splitter_width is set is left alone,
        #    mirroring the per-stile unlock handling in (3).
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
            if sp.unlock_splitter_width:
                continue
            sp.splitter_width = mid_rail_w if sp.axis == 'H' else mid_stile_w

        for entry in props.mid_stile_widths:
            if not entry.unlock:
                entry.width = mid_stile_w

    def _apply_door_styles_to_fronts(self, cabinet_obj):
        """Walk every front under cabinet_obj. DOOR-role and PULLOUT_FRONT
        fronts get self.door_style (a pullout is a door on a slide, so it
        reads the door pool, not the drawer-front pool); DRAWER_FRONT /
        FALSE_FRONT get self.drawer_front_style. Other roles (INSET_PANEL,
        structural parts, hardware) are skipped.
        """
        DOOR_ROLES = {'DOOR', 'PULLOUT_FRONT'}
        DRAWER_ROLES = {'DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT',
                        'DRAWER_LOOK_FRONT'}

        ff = get_style_props()

        def resolve(name, pool):
            if not name or name == 'NONE':
                return None
            for ds in pool:
                if ds.name == name:
                    return ds
            return None

        # door_style resolves in door_styles, drawer_front_style in the
        # separate drawer_front_styles pool (independent lists). These are the
        # cabinet-level DEFAULTS, applied only to fronts that carry no per-front
        # assignment of their own (see the DOOR_STYLE_NAME check below).
        door_ds = resolve(self.door_style, ff.door_styles)
        drawer_ds = resolve(self.drawer_front_style, ff.drawer_front_styles)

        for child in cabinet_obj.children_recursive:
            if 'CABINET_PART' not in child:
                continue
            # Manual (applied / hand-edited) fronts have no Door Style modifier
            # to drive - re-styling would add geometry onto the baked mesh.
            if child.get('IS_MANUAL_PART'):
                continue
            # Drawer-look carrier leaf stays a flat slab (its applied
            # drawer fronts carry the visible style); never style it.
            if child.get('HB_DRAWER_LOOK_CARRIER'):
                continue
            role = child.get('hb_part_role')
            if role in DOOR_ROLES:
                pool, default_ds = ff.door_styles, door_ds
            elif role in DRAWER_ROLES:
                pool, default_ds = ff.drawer_front_styles, drawer_ds
            else:
                continue
            # The solver wipes and rebuilds every front on each recalc, so an
            # opening-size edit (or any cabinet alteration) lands here. Prefer
            # the front's OWN previously-assigned style, recorded in
            # DOOR_STYLE_NAME, so a per-front override survives the rebuild;
            # fall back to the cabinet default only for fronts with no stored
            # assignment. Mirrors _reapply_front_style (ops_part_commands.py).
            ds = resolve(child.get('DOOR_STYLE_NAME'), pool) or default_ds
            if ds is not None:
                ds.assign_style_to_front(child)

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
            ("Butt Stile", "ff_butt_stile_width"),
            ("Inside 90 Stile", "ff_inside_90_stile_width"),
            ("Angle Stile", "ff_angle_stile_width"),
        ):
            r = box.row(align=True)
            r.label(text=row_label)
            for col_key in ("base", "tall", "upper"):
                r.label(text="", icon='BLANK1')
                r.label(text=inch_label(getattr(self, f"{prop_root}_{col_key}")))

    def _draw_toggle_field(self, col, dropdown_attr, label, custom_base=None):
        """Draw a dropdown field with a button toggling to a free-text field,
        so a value outside the list can be typed. The typed value is stored on
        <base>_custom, gated by <base>_is_custom. ``base`` defaults to the
        dropdown attr; pass custom_base when the page-override store differs
        from the dropdown (e.g. the finish_wood dropdown stores custom text on
        ss_wood). The dropdown still drives geometry/material; custom text is a
        print-only spec value."""
        base = custom_base or dropdown_attr
        row = col.row(align=True)
        if getattr(self, base + "_is_custom", False):
            row.prop(self, base + "_custom", text=label)
        else:
            row.prop(self, dropdown_attr, text=label)
        row.prop(self, base + "_is_custom", text="",
                 icon='GREASEPENCIL', toggle=True)

    def _draw_finish_reference(self, col, ref_name_attr, ref_image_attr):
        """Compact reference row beneath a finish field: a ref NAME (appended
        to the field's row on the Style Section page) and a ref IMAGE path
        (collected into the page's right-side references box). Both optional."""
        r = col.row(align=True)
        r.prop(self, ref_name_attr, text="Ref")
        r.prop(self, ref_image_attr, text="", icon='IMAGE_DATA')

    def draw_cabinet_style_ui(self, layout, context):
        """Per-style settings drawn inside the cabinet styles UIList panel.

        Sections: CABINET / FINISH / FRONTS / DOORS / DRAWERS / EDGE PROFILE.
        The Door / Drawer Front pickers reference a style by name from the
        shared front-style pools.
        """
        main = layout.column()

        name_box = main.box()
        name_box.prop(self, "name", text="Style Name")

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="CABINET")
        col = box.column(align=True)
        self._draw_toggle_field(col, "finish_wood", "Wood", "ss_wood")
        self._draw_toggle_field(col, "interior_material_type", "Interior",
                                "ss_interior")
        if not self.ss_interior_is_custom and self.interior_material_type == 'CUSTOM':
            col.prop(self, "custom_interior_material", text="")
        self._draw_toggle_field(col, "finish_overlay", "Overlay", "ss_overlay")
        self._draw_toggle_field(col, "ss_corner_treatment", "Corner Treatment")
        self._draw_toggle_field(col, "ss_fin_opening_edge", "Fin Opening Edge")
        # Face frame size grid is large; collapsed by default.
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, "show_face_frame_sizes",
                 text="Face Frame Sizes",
                 icon='TRIA_DOWN' if self.show_face_frame_sizes else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_face_frame_sizes:
            self._draw_face_frame_sizes(box, context)

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="FINISH")
        # Toggle the per-finish reference name + image fields on/off (off by
        # default to keep the editor compact when references aren't in use).
        trow = box.row()
        trow.alignment = 'RIGHT'
        trow.prop(self, "show_finish_references", text="References",
                  icon='IMAGE_REFERENCE', toggle=True)
        show_refs = self.show_finish_references
        col = box.column(align=True)
        # Each finish field optionally shows a Reference row beneath it: a ref
        # NAME (shown on the Style Section page next to the field descriptor)
        # and a ref IMAGE path (collected into the page's right-side references
        # box). Gated on the References toggle above.
        self._draw_toggle_field(col, "finish_color", "Color", "ss_color")
        if show_refs:
            self._draw_finish_reference(col, "ss_color_ref_name", "ss_color_ref_image")
        self._draw_toggle_field(col, "finish_varnish", "Varnish", "ss_varnish")
        if show_refs:
            self._draw_finish_reference(col, "ss_varnish_ref_name", "ss_varnish_ref_image")
        self._draw_toggle_field(col, "finish_glaze", "Glaze", "ss_glaze")
        if show_refs:
            self._draw_finish_reference(col, "ss_glaze_ref_name", "ss_glaze_ref_image")
        # Special effects: catalog finish add-ons gated by this style's
        # wood + color. Add opens a checkbox dialog of the compatible set.
        # Each effect row also carries its own ref name + image.
        sfx = box.column(align=True)
        sfx.operator("hb_face_frame.add_special_effects",
                     text="Add Special Effects", icon='ADD')
        for effect in self.special_effects:
            r = sfx.row(align=True)
            r.label(text=effect.name, icon='DOT')
            if show_refs:
                r.prop(effect, "ref_name", text="")
                r.prop(effect, "ref_image", text="", icon='IMAGE_DATA')
            r.operator("hb_face_frame.remove_special_effect",
                       text="", icon='X', emboss=False).effect_name = effect.name

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="FRONTS")
        col = box.column(align=True)
        self._draw_toggle_field(col, "door_style", "Door", "ss_door")
        # Extra door styles: additional front styles listed on the Style
        # Section page (documentation only; no geometric effect).
        for i, ex in enumerate(self.extra_door_styles):
            r = col.row(align=True)
            r.prop(ex, "style", text="")
            op = r.operator("hb_face_frame.remove_cabinet_extra_front_style",
                            text="", icon='X', emboss=False)
            op.kind = 'DOOR'
            op.index = i
        col.operator("hb_face_frame.add_cabinet_extra_front_style",
                     text="Add Door Style", icon='ADD').kind = 'DOOR'

        col.separator()
        self._draw_toggle_field(col, "drawer_front_style", "Drawer Front", "ss_drawer")
        for i, ex in enumerate(self.extra_drawer_front_styles):
            r = col.row(align=True)
            r.prop(ex, "style", text="")
            op = r.operator("hb_face_frame.remove_cabinet_extra_front_style",
                            text="", icon='X', emboss=False)
            op.kind = 'DRAWER'
            op.index = i
        col.operator("hb_face_frame.add_cabinet_extra_front_style",
                     text="Add Drawer Front Style", icon='ADD').kind = 'DRAWER'

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="DOORS")
        col = box.column(align=True)
        self._draw_toggle_field(col, "finish_hinge", "Hinge", "ss_hinge")

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="DRAWERS")
        col = box.column(align=True)
        self._draw_toggle_field(col, "ss_drawer_slides", "Drawer Slides")
        self._draw_toggle_field(col, "ss_drawer_box_construction", "Box Construction")
        # Drawer-box brand logo (FILE_PATH image) -- plain file-picker row; the
        # Style Section page renders the logo in the DRAWERS section when set.
        col.prop(self, "ss_drawer_box_brand", text="Box Brand Logo")

        box = main.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="DOOR & DRAWER EDGE PROFILE")
        col = box.column(align=True)
        self._draw_toggle_field(col, "ss_edge_profile", "Edge Profile")


class HB_UL_face_frame_cabinet_styles(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon='SHADERFX')


# ---------------------------------------------------------------------------
# Door Style - shared pool, referenced from cabinet styles via index
# ---------------------------------------------------------------------------
RAIL_SIZE_ANNOTATION_TAG = 'DOOR_ANNOTATION'


def _sync_rail_size_annotation(front_obj, part, top_rail_width,
                               right_stile_width, active):
    """Maintain the '<N>R' rail-size FONT callout on a 5-piece front.

    Shown when the front's rail width deviates from the catalog spec
    (the style's rail unlock, or a locked per-front frame override) so
    the shop drawing calls out the non-standard rail. Parented to the
    front, it is torn down with the front on every recalc (the pivot
    wipe removes children_recursive) and recreated here; it rides into
    elevations like any other IS_2D_ANNOTATION FONT under the cabinet,
    where the Spaces elevation pass links it to IGNORE freestyle.

    Idempotent: an existing annotation is removed first, covering live
    style edits (unlock toggled off) with no front rebuild in between.
    Placement matches the legacy convention: text sits centered on the
    top rail, inset 1" from the hinge-far stile, just proud of the
    face (part-local; Mirror Y flips the cross-width axis).
    """
    for child in list(front_obj.children):
        if child.get(RAIL_SIZE_ANNOTATION_TAG):
            bpy.data.objects.remove(child, do_unlink=True)
    if not active:
        return

    inches = units.meter_to_inch(top_rail_width)
    label = ('%g' % round(inches, 3)) + 'R'

    fd = bpy.data.curves.new('Rail Size Annotation', type='FONT')
    fd.body = label
    fd.size = 0.04
    fd.align_x = 'RIGHT'
    fd.align_y = 'CENTER'
    text_obj = bpy.data.objects.new('Rail Size Annotation', fd)
    text_obj[RAIL_SIZE_ANNOTATION_TAG] = True
    text_obj['IS_2D_ANNOTATION'] = True
    text_obj.color = (0.0, 0.0, 0.0, 1.0)
    for coll in front_obj.users_collection:
        coll.objects.link(text_obj)
    if not text_obj.users_collection:
        bpy.context.scene.collection.objects.link(text_obj)
    text_obj.parent = front_obj
    text_obj.rotation_euler.z = -1.5707963267948966  # -90 deg

    try:
        front_length = part.get_input('Length')
        front_width = part.get_input('Width')
    except Exception:
        return
    try:
        mirror_y = bool(part.get_input('Mirror Y'))
    except Exception:
        mirror_y = False
    text_obj.location.x = front_length - top_rail_width / 2.0
    y = front_width - right_stile_width - units.inch(1.0)
    text_obj.location.y = -y if mirror_y else y
    text_obj.location.z = units.inch(0.76)


def _front_frame_store(front_obj):
    """Persistent home for a front's locked frame overrides.

    Fronts (and their pivots) are torn down and rebuilt as NEW objects
    on every recalc, so custom props set on the front do not survive a
    cabinet edit. The front's OPENING cage (IS_FACE_FRAME_OPENING_CAGE)
    does survive, so the lock flag + HB_FRAME_OVR_* values live there.
    A cage-less front (bare Door Part) is its own store - it is not
    rebuilt by a cabinet recalc. NOTE: an opening with two leaves (double
    door) shares one store, so both leaves take the same locked frame.
    """
    o = front_obj.parent
    while o is not None:
        if o.get('IS_FACE_FRAME_OPENING_CAGE'):
            return o
        o = o.parent
    return front_obj

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

    # ---- Catalog front spec (series -> shape -> panel; see style_options) ----
    # Whether this style reads the DOOR or DRAWER catalog is implied by which
    # pool it lives in (door_styles vs drawer_front_styles); see
    # _front_is_drawer (path-based). No stored "kind" property.
    front_series: EnumProperty(
        name="Series",
        description="Catalog series (gates the available shapes)",
        items=get_front_series_items,
        update=update_front_series,
    )  # type: ignore
    front_shape: EnumProperty(
        name="Shape",
        description="Shape available for the chosen series",
        items=get_front_shape_items,
        update=update_front_shape,
    )  # type: ignore
    front_panel: EnumProperty(
        name="Panel",
        description="Panel available for the chosen series + shape",
        items=get_front_panel_items,
        update=update_front_panel,
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

    # Wood-grain run direction for this front. HORIZONTAL feeds the 5-piece
    # panel the rotated finish material (finish_mat_rotated) so the panel
    # grain runs across; VERTICAL uses finish_mat (see
    # _set_door_modifier_materials). NONE renders like VERTICAL (only
    # HORIZONTAL is special-cased in the material walk) but carries no
    # grain spec: the Style Section page skips its Grain row, for
    # painted / non-grained fronts where a grain callout is noise.
    grain_direction: EnumProperty(
        name="Grain Direction",
        description="Direction the wood grain runs on this front",
        items=[
            ('NONE', "None", "No grain direction (painted / non-grained fronts; no callout on the style section)"),
            ('VERTICAL', "Vertical", "Grain runs vertically"),
            ('HORIZONTAL', "Horizontal", "Grain runs horizontally"),
        ],
        default='VERTICAL',
        update=update_grain_direction,
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
    # Stile / rail widths derive from the catalog series by default; each has
    # its own unlock toggle to override it (see update_unlock_frame_widths /
    # _apply_series_frame_to_door_style).
    unlock_stile_width: BoolProperty(
        name="Unlock Stile Width",
        description="Override the catalog stile width; re-lock to snap back "
                    "to the series spec",
        default=False,
        update=update_unlock_frame_widths,
    )  # type: ignore

    unlock_rail_width: BoolProperty(
        name="Unlock Rail Width",
        description="Override the catalog rail width; re-lock to snap back "
                    "to the series spec",
        default=False,
        update=update_unlock_frame_widths,
    )  # type: ignore

    stile_width: FloatProperty(
        name="Stile Width",
        description="Width of left and right stiles",
        default=units.inch(3.0), unit='LENGTH', precision=4,
        update=_propagate_door_style,
    )  # type: ignore

    rail_width: FloatProperty(
        name="Rail Width",
        description="Width of top and bottom rails (the mid rail follows it)",
        default=units.inch(3.0), unit='LENGTH', precision=4,
        update=update_rail_width,
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

    # Front roles this style will act on (DOOR + PULLOUT_FRONT read door_style
    # on the parent cabinet style - a pullout is a door on a slide; the rest
    # read drawer_front_style).
    _DOOR_FRONT_ROLES = {'DOOR', 'PULLOUT_FRONT'}
    _DRAWER_FRONT_ROLES = {'DRAWER_FRONT', 'FALSE_FRONT', 'TILT_OUT',
                            'DRAWER_LOOK_FRONT'}
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

        ff = get_style_props()
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

        # Every styleable front carries the part right-click menu. Fronts are
        # rebuilt each recalc (new objects), so stamping here - on the freshly
        # built front - is reliable where the recalc-time backfill is not.
        if not front_obj.get('MENU_ID'):
            front_obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'

        # Tag prep-for-glass fronts so the 2D drawing layer can hatch the glass
        # panel (Spaces reads IS_PREP_FOR_GLASS); mirrors the 3D glass render.
        # Set on every style assignment so it tracks the current panel choice.
        front_obj['IS_PREP_FOR_GLASS'] = (self.front_panel == 'Prep for Glass')

        from ... import hb_types

        # Slab: strip any existing door style modifier and tag.
        if self.door_type == 'SLAB':
            for mod in list(front_obj.modifiers):
                if mod.type == 'NODES' and 'Door Style' in mod.name:
                    front_obj.modifiers.remove(mod)
            # Slabs carry no rails; drop a stale rail-size callout left
            # over from a live 5-piece -> slab style edit.
            _sync_rail_size_annotation(front_obj, None, 0.0, 0.0, False)
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

        # Per-side frame-width overrides (tri-view mirror doors). When the
        # front object carries an HB_FRAME_OVR_* custom prop, that side's
        # stile / rail width comes from it (0.0 = no stile, so adjacent
        # mirrors butt) instead of the uniform door-style width.
        # The per-front stile / rail / mid-rail overrides only take effect
        # when the front's frame is LOCKED (HB_FRAME_FRAME_LOCKED). Locked
        # pins the whole Set Door Frame interface so a cabinet edit can't
        # overwrite it; unlocked, the front follows the door style and is
        # recomputed on any cabinet change.
        frame_store = _front_frame_store(front_obj)
        frame_locked = bool(frame_store.get('HB_FRAME_FRAME_LOCKED', False))
        if frame_locked:
            eff_left_stile  = frame_store.get('HB_FRAME_OVR_LEFT_STILE',  self.stile_width)
            eff_right_stile = frame_store.get('HB_FRAME_OVR_RIGHT_STILE', self.stile_width)
            eff_top_rail    = frame_store.get('HB_FRAME_OVR_TOP_RAIL',    self.rail_width)
            eff_bottom_rail = frame_store.get('HB_FRAME_OVR_BOTTOM_RAIL', self.rail_width)
        else:
            eff_left_stile  = self.stile_width
            eff_right_stile = self.stile_width
            eff_top_rail    = self.rail_width
            eff_bottom_rail = self.rail_width

        # Locked NONE mode removes the mid rail entirely, overriding both the
        # style's add_mid_rail and the tall-door auto rail.
        ovr_mid_mode = frame_store.get('HB_FRAME_OVR_MID_RAIL_MODE') if frame_locked else None

        min_width = eff_left_stile + eff_right_stile + units.inch(1)
        min_height = eff_top_rail + eff_bottom_rail + units.inch(1)
        if ovr_mid_mode != 'NONE' and (self.add_mid_rail or needs_auto_mid_rail):
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

        door_style_mod.set_input("Left Stile Width", eff_left_stile)
        door_style_mod.set_input("Right Stile Width", eff_right_stile)
        door_style_mod.set_input("Top Rail Width", eff_top_rail)
        door_style_mod.set_input("Bottom Rail Width", eff_bottom_rail)
        door_style_mod.set_input("Panel Thickness", self.panel_thickness)
        door_style_mod.set_input("Panel Inset", self.panel_inset)

        # Per-front mid rail override (durable, set from the Set Door Frame
        # popup) wins over the style / auto-center. CENTERED centers it; THIRD /
        # QUARTER place it by fraction; CUSTOM, TOP_PANEL and BOTTOM_PANEL use the
        # single stored value (a from-bottom centerline, or an interior panel
        # height that the solver converts to a centerline). Presence of an
        # override also forces a mid rail on.
        if ovr_mid_mode != 'NONE' and (needs_auto_mid_rail or self.add_mid_rail or ovr_mid_mode):
            try:
                door_style_mod.set_input("Add Mid Rail", True)
                door_style_mod.set_input("Mid Rail Width", self.mid_rail_width)
                if ovr_mid_mode == 'CENTERED':
                    door_style_mod.set_input("Center Mid Rail", True)
                elif ovr_mid_mode == 'THIRD':
                    door_style_mod.set_input("Center Mid Rail", False)
                    # Mid Rail Location is the rail CENTERLINE measured from the
                    # BOTTOM, so 2/3 up puts the rail near the top (bottom opening
                    # = 2/3, top = 1/3).
                    door_style_mod.set_input("Mid Rail Location", front_length * 2.0 / 3.0)
                elif ovr_mid_mode == 'QUARTER':
                    door_style_mod.set_input("Center Mid Rail", False)
                    # 3/4 up from the bottom (bottom opening = 3/4, top = 1/4).
                    door_style_mod.set_input("Mid Rail Location", front_length * 3.0 / 4.0)
                elif ovr_mid_mode in ('CUSTOM', 'TOP_PANEL', 'BOTTOM_PANEL'):
                    door_style_mod.set_input("Center Mid Rail", False)
                    # One stored value, interpreted by mode. The door spans
                    # [0, L] along its length; the rail spans [loc - Rm/2,
                    # loc + Rm/2] about its centerline loc. So the bottom opening
                    # is (loc - Rm/2) - bottom_rail and the top opening is
                    # (L - top_rail) - (loc + Rm/2). CUSTOM stores loc directly;
                    # the panel modes store the opening height on that side and we
                    # solve for loc, clamping so a too-large height can't push the
                    # rail past either end rail.
                    stored = frame_store.get('HB_FRAME_OVR_MID_RAIL_LOCATION',
                                             self.mid_rail_location)
                    half_rm = self.mid_rail_width / 2.0
                    if ovr_mid_mode == 'BOTTOM_PANEL':
                        loc = eff_bottom_rail + stored + half_rm
                    elif ovr_mid_mode == 'TOP_PANEL':
                        loc = front_length - eff_top_rail - stored - half_rm
                    else:
                        loc = stored
                    loc_min = eff_bottom_rail + half_rm
                    loc_max = front_length - eff_top_rail - half_rm
                    if loc_max >= loc_min:
                        loc = max(loc_min, min(loc, loc_max))
                    door_style_mod.set_input("Mid Rail Location", loc)
                elif needs_auto_mid_rail:
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

        # Rail-size callout ('3R'): rail width deviates from the catalog
        # via the style's rail unlock, or via a locked per-front frame
        # override whose top rail differs from the style.
        _sync_rail_size_annotation(
            front_obj, part, eff_top_rail, eff_right_stile,
            active=(self.unlock_rail_width
                    or (frame_locked
                        and abs(eff_top_rail - self.rail_width) > 1e-6)),
        )

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

        # Catalog front spec (series -> shape -> panel) is the single source
        # of truth. Series + kind derive the stile / rail widths, drawer-rail,
        # panel inset/thickness and slab-vs-5-piece (see
        # _apply_series_frame_to_door_style); the construction fields are
        # written from it and consumed by the geometry + applied-panel-sizing
        # engines, so they're no longer shown here.
        col = box.column(align=True)
        col.label(text="Catalog:")
        col.prop(self, "front_series", text="Series")
        col.prop(self, "front_shape", text="Shape")
        col.prop(self, "front_panel", text="Panel")

        box.prop(self, "grain_direction", text="Grain Direction")

        # Frame widths derive from the catalog series by default (read-only).
        # Stile and rail each have an independent unlock toggle to override
        # them; the mid rail always follows the rail width. Re-locking a field
        # snaps it back to the series spec (see update_unlock_frame_widths).
        if self.door_type == '5_PIECE':
            box.label(text="Frame Widths:")
            srow = box.row(align=True)
            sfield = srow.column(align=True)
            sfield.enabled = self.unlock_stile_width
            sfield.prop(self, "stile_width", text="Stile Width")
            srow.prop(self, "unlock_stile_width", text="",
                      icon='UNLOCKED' if self.unlock_stile_width else 'LOCKED')
            rrow = box.row(align=True)
            rfield = rrow.column(align=True)
            rfield.enabled = self.unlock_rail_width
            rfield.prop(self, "rail_width", text="Rail Width")
            rrow.prop(self, "unlock_rail_width", text="",
                      icon='UNLOCKED' if self.unlock_rail_width else 'LOCKED')

        # Assign by Painting starts a modal brush: click fronts in the
        # viewport to apply THIS style. Door styles paint door fronts,
        # drawer-front styles paint drawer fronts (kind derived from the
        # pool this style lives in). Update re-applies to every matching
        # front already tagged with the style name.
        try:
            kind = 'DRAWER' if "drawer_front_styles" in self.path_from_id() else 'DOOR'
        except Exception:
            kind = 'DOOR'
        row = box.row(align=True)
        row.scale_y = 1.3
        op = row.operator("hb_face_frame.paint_assign_front_style",
                          text="Assign by Painting", icon='BRUSH_DATA')
        op.kind = kind
        op = row.operator("hb_face_frame.update_fronts_from_style",
                          text="Update Fronts", icon='FILE_REFRESH')
        op.kind = kind


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


# Standard rollout box heights (inches) keyed by the preset enum id, plus the
# matching enum items. CUSTOM is intentionally absent from the map: it leaves
# a box's height untouched so a typed value stands.
_ROLLOUT_HEIGHT_PRESETS_IN = {
    'IN_4_625': 4.625,
    'IN_6_5': 6.5,
    'IN_8_375': 8.375,
    'IN_11_625': 11.625,
}

ROLLOUT_HEIGHT_PRESET_ITEMS = [
    ('IN_4_625',  '4 5/8"',  'Standard 4 5/8" rollout box height'),
    ('IN_6_5',    '6 1/2"',  'Standard 6 1/2" rollout box height'),
    ('IN_8_375',  '8 3/8"',  'Standard 8 3/8" rollout box height'),
    ('IN_11_625', '11 5/8"', 'Standard 11 5/8" rollout box height'),
    ('CUSTOM',    'Custom',  'Type an exact box height in the field beside it'),
]


def _update_rollout_box_preset(self, context):
    """A rollout box's preset writes its inch value into the box's height
    (the field the solver reads when stacking boxes); CUSTOM leaves height
    alone for a typed value. The inner write is suspended so it coalesces
    into the one recalc below.
    """
    from . import types_face_frame
    inches = _ROLLOUT_HEIGHT_PRESETS_IN.get(self.height_preset)
    with types_face_frame.suspend_recalc():
        if inches is not None:
            self.height = units.inch(inches)
    _update_cabinet_dim(self, context)


def _update_refrigerator_opening_height(self, context):
    """Per-cabinet refrigerator opening height.

    Drives the bottom APPLIANCE opening node (SIZE_ROLE == 'REFRIGERATOR')
    and keeps back_bottom_inset in sync so the carcass back keeps spanning
    only the door zone above the opening (kick + opening + mid rail - mt,
    mirroring the create-time formula). No bottom_rail term: the fridge
    cabinet's bays carry remove_bottom, so the appliance opening starts
    at the kick top with no rail below it -- adding the rail width here
    floated the back above the mid rail, leaving a gap behind the door
    zone. Batched under suspend_recalc so the inset + node-size writes
    collapse into one recalc.
    """
    from . import types_face_frame
    cab_obj = self.id_data
    value = self.refrigerator_opening_height
    with types_face_frame.suspend_recalc():
        self.back_bottom_inset = (
            self.toe_kick_height
            + value
            + self.bay_mid_rail_width
            - self.material_thickness
        )
        for child in cab_obj.children_recursive:
            if child.get('SIZE_ROLE') == 'REFRIGERATOR':
                op = child.face_frame_opening
                op.unlock_size = True
                op.size = value


def _update_remove_bottom(self, context):
    """Update callback for a bay's remove_bottom toggle.

    Removing the bottom rail makes the opening grow down into the rail's
    space (see solver.effective_bottom_rail_width). The door that sat on
    that rail then has no rail to overlay, so we default it flush:
    unlock the opening's bottom overlay and set it to 0. The value stays
    editable - the user can dial in a bottom overlay afterwards in the
    opening properties and it will be honored (unlocked wins over the
    cabinet default). Restoring the rail re-locks the override so the
    bottom overlay follows the cabinet default again.

    The affected openings are the bay's bottom-perimeter leaves: the
    lowest opening of an H-split, or every opening of a V-split. They are
    identified geometrically as the leaves at the lowest bay-local cage Z,
    which holds regardless of split layout.
    """
    from . import types_face_frame, solver_face_frame
    bay_obj = self.id_data
    bi = bay_obj.get('hb_bay_index')
    removing = self.remove_bottom
    # One suspend so the overlay writes + the dimension recalc coalesce
    # into a single cabinet recalc when this callback returns.
    with types_face_frame.suspend_recalc():
        root = types_face_frame.find_cabinet_root(bay_obj)
        if root is not None and bi is not None:
            layout = solver_face_frame.FaceFrameLayout(root)
            leaves = solver_face_frame.bay_openings(layout, bi).get('leaves', [])
            if leaves:
                min_z = min(lf['cage_z'] for lf in leaves)
                for lf in leaves:
                    if abs(lf['cage_z'] - min_z) > 1e-5:
                        continue  # not a bottom-perimeter opening
                    opening = bpy.data.objects.get(lf['obj_name'])
                    if opening is None:
                        continue
                    op = opening.face_frame_opening
                    if removing:
                        op.unlock_bottom_overlay = True
                        op.bottom_overlay = 0.0
                    else:
                        op.unlock_bottom_overlay = False
        # Always recalc - even when there were no openings to adjust the
        # rail removal still changes the carcass / face frame.
        types_face_frame.recalculate_face_frame_cabinet(bay_obj)


# When the user edits a finished-end-condition enum from the UI, flip the
# matching auto flag off so subsequent exposure recalcs don't clobber the
# choice. Exposure recalc re-arms auto explicitly after writing its own
# value, so its own writes don't permanently disable auto.
def _on_left_finish_end_user_set(self, context):
    self.left_finish_end_auto = False
    _update_cabinet_dim(self, context)


def _on_right_finish_end_user_set(self, context):
    self.right_finish_end_auto = False
    _update_cabinet_dim(self, context)


def _on_back_finish_end_user_set(self, context):
    self.back_finish_end_auto = False
    _update_cabinet_dim(self, context)


# Scribe edits also flip the side's auto flag off. The single auto flag
# governs both finish type and scribe so the user's mental model stays
# "this side is auto-managed" or not - touching either auto-managed
# value pins it.
def _on_left_scribe_user_set(self, context):
    self.left_finish_end_auto = False
    _update_cabinet_dim(self, context)


def _on_right_scribe_user_set(self, context):
    self.right_finish_end_auto = False
    _update_cabinet_dim(self, context)

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
        default=False, update=_update_cabinet_dim,
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

    to_floor: BoolProperty(
        name="Stile to Floor",
        default=False,
        description="Extend this mid stile past the toe kick down to the "
                    "floor (pins its bottom to Z=0, like an end stile)",
        update=_update_cabinet_dim,
    )  # type: ignore


# ---------------------------------------------------------------------------
# Corner cabinet exterior configuration
# ---------------------------------------------------------------------------
class Face_Frame_Corner_Section(PropertyGroup):
    """One stacked section of a diagonal corner cabinet's front.

    Lives in a CollectionProperty on Face_Frame_Cabinet_Props, ordered
    top to bottom. content is fixed by the chosen exterior_config preset;
    the user only adjusts heights. A section's height is auto - an equal
    share of the leftover space - unless unlock_height is on, mirroring
    the bay-width / mid-stile lock pattern.
    """
    content: EnumProperty(
        name="Content",
        items=[
            ('DOORS',       "Doors",       "Double-door pair"),
            ('FALSE_FRONT', "False Front", "Fixed false front panel"),
            ('OPEN',        "Open",        "Open section with shelves"),
        ],
        default='DOORS',
    )  # type: ignore
    height: FloatProperty(
        name="Section Height",
        description="Opening height of this section (used when Unlock Height is on)",
        default=units.inch(12.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    unlock_height: BoolProperty(
        name="Unlock Height",
        description="Hold this section's height; the other sections share the leftover space equally",
        default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    shelf_qty: IntProperty(
        name="Shelf Qty",
        description="Number of adjustable shelves in this section",
        default=2, min=0, max=10,
        update=_update_cabinet_dim,
    )  # type: ignore
    # DOORS sections on upper corner cabinets auto-count their shelves
    # by section height (synced into shelf_qty each recalc so the UI
    # shows the live count). Unlock to override with a manual count.
    # OPEN sections are unaffected -- their shelf_qty has always been
    # fully manual and stays that way.
    unlock_shelf_qty: BoolProperty(
        name="Unlock Shelf Qty",
        description="Override the auto shelf count for this door section",
        default=False,
        update=_update_cabinet_dim,
    )  # type: ignore


# exterior_config items vary by cabinet type. Module-level lists keep the
# string references alive - a dynamic EnumProperty items callback that
# rebuilt fresh tuples each call would risk them being garbage collected.
_EXTERIOR_CONFIG_ITEMS = {
    'BASE': [
        ('DOORS',             "Full Height Doors",      "One full-height door pair"),
        ('FALSE_FRONT_DOORS', "False Front with Doors", "False front above a door pair"),
    ],
    'UPPER': [
        ('DOORS',         "Doors",             "One door pair"),
        ('STACKED_DOORS', "Stacked Doors",     "Two stacked door pairs"),
        ('HUTCH',         "Hutch",             "Doors on top, open below, no bottom"),
        ('OPEN_SHELVES',  "Open with Shelves", "Open shelf section, no bottom"),
    ],
    'TALL': [
        ('HUTCH',    "Hutch",    "Upper doors, open middle, base doors"),
        ('BOOKCASE', "Bookcase", "Open shelves on top, base doors below"),
    ],
}


# Pie cut exterior configs. Pie cut has two face frames (one per arm);
# a config splits both arms together. Base pie cut is full-height door
# only; upper pie cut adds a two-section stacked option.
_PIE_CUT_CONFIG_ITEMS = {
    'BASE': [
        ('DOORS', "Full Height Doors", "One full-height door per arm"),
    ],
    'UPPER': [
        ('DOORS',         "Full Height Doors", "One full-height door per arm"),
        ('STACKED_DOORS', "Stacked Doors",     "Two stacked doors per arm"),
    ],
}


def _exterior_config_items(self, context):
    """Dynamic items for exterior_config, filtered by corner type and
    cabinet type. Pie cut and diagonal offer different config sets."""
    obj = self.id_data
    ctype = obj.get('CABINET_TYPE', 'BASE') if obj is not None else 'BASE'
    if self.corner_type == 'PIE_CUT':
        return _PIE_CUT_CONFIG_ITEMS.get(ctype, _PIE_CUT_CONFIG_ITEMS['BASE'])
    return _EXTERIOR_CONFIG_ITEMS.get(ctype, _EXTERIOR_CONFIG_ITEMS['BASE'])


# (cabinet_type, exterior_config) -> ordered tuple of section content kinds,
# top to bottom. The preset fixes section count and content; section
# heights stay user-adjustable (see Face_Frame_Corner_Section).
_CORNER_SECTION_PRESETS = {
    ('BASE',  'DOORS'):             ('DOORS',),
    ('BASE',  'FALSE_FRONT_DOORS'): ('FALSE_FRONT', 'DOORS'),
    ('UPPER', 'DOORS'):             ('DOORS',),
    ('UPPER', 'STACKED_DOORS'):     ('DOORS', 'DOORS'),
    ('UPPER', 'HUTCH'):             ('DOORS', 'OPEN'),
    ('UPPER', 'OPEN_SHELVES'):      ('OPEN',),
    ('TALL',  'HUTCH'):             ('DOORS', 'OPEN', 'DOORS'),
    ('TALL',  'BOOKCASE'):          ('OPEN', 'DOORS'),
}

# Optional per-section DEFAULT heights for a preset, ordered like the
# preset's content tuple (top to bottom). A non-None entry pins that
# section when the config is selected (height written + unlock_height
# on) so it starts at a sensible opening size instead of an equal
# share - e.g. the bookcase's bottom door opening at 24". Configs not
# listed (or None entries) keep the unlocked equal-share default. The
# sentinel 'TOP_DRAWER' resolves to the scene's
# hb_face_frame.top_drawer_opening_height at populate time (same size
# role the bay presets use), so the false front lines up with adjacent
# drawer fronts.
_CORNER_SECTION_DEFAULT_HEIGHTS = {
    ('TALL', 'BOOKCASE'): (None, units.inch(24.0)),
    ('BASE', 'FALSE_FRONT_DOORS'): ('TOP_DRAWER', None),
}


def corner_section_contents(cab_props):
    """Section content tuple for the cabinet's current type and config,
    falling back to a single door section for unknown combinations."""
    obj = cab_props.id_data
    ctype = obj.get('CABINET_TYPE', 'BASE') if obj is not None else 'BASE'
    return _CORNER_SECTION_PRESETS.get(
        (ctype, cab_props.exterior_config), ('DOORS',))


def populate_corner_sections(cab_props):
    """Rebuild cab_props.corner_sections from the current exterior_config
    preset. Sections start unlocked (evenly spaced) unless the preset
    carries a default height for them in _CORNER_SECTION_DEFAULT_HEIGHTS,
    in which case the section is pinned to that height (e.g. the
    bookcase's bottom door opening at 24")."""
    contents = corner_section_contents(cab_props)
    obj = cab_props.id_data
    ctype = obj.get('CABINET_TYPE', 'BASE') if obj is not None else 'BASE'
    defaults = _CORNER_SECTION_DEFAULT_HEIGHTS.get(
        (ctype, cab_props.exterior_config), ())
    cab_props.corner_sections.clear()
    for i, content in enumerate(contents):
        sec = cab_props.corner_sections.add()
        sec.content = content
        h = defaults[i] if i < len(defaults) else None
        if h == 'TOP_DRAWER':
            # Scene-level size preference; None during first-load /
            # unregister when the scene props aren't attached yet.
            ff_scene = getattr(bpy.context.scene, 'hb_face_frame', None)
            h = (ff_scene.top_drawer_opening_height
                 if ff_scene is not None else None)
        if h is not None:
            # Unlock BEFORE writing the height: each write fires a
            # recalc, and the recalc's height-sync overwrites an
            # unlocked section's height with the solved share - so a
            # height written first would be clobbered before the
            # unlock landed.
            sec.unlock_height = True
            sec.height = h
        else:
            sec.unlock_height = False


def _update_exterior_config(self, context):
    """exterior_config changed: repopulate the section collection from the
    new preset, then recalc."""
    populate_corner_sections(self)
    from . import types_face_frame
    types_face_frame.recalculate_face_frame_cabinet(self.id_data)


def populate_pie_drawer_sections(cab_props):
    """Rebuild corner_sections for a pie-cut drawer corner to match
    pie_drawer_qty - one stacked DOORS section per drawer (rendered as drawer
    fronts). For 3+ drawer stacks the TOP opening is pinned to the scene's
    Top Drawer Opening Height by default (mirroring the base drawer presets);
    the remaining sections share the leftover space equally. The user can then
    lock / set any section's height in the Sections box.
    """
    qty = cab_props.pie_drawer_qty
    secs = cab_props.corner_sections
    secs.clear()
    for _ in range(qty):
        secs.add().content = 'DOORS'
    if qty >= 3:
        ff_scene = getattr(bpy.context.scene, 'hb_face_frame', None)
        if ff_scene is not None:
            # Unlock BEFORE writing the height (same ordering reason as
            # populate_corner_sections: each write fires a recalc whose
            # height-sync would clobber an unlocked section's height).
            secs[0].unlock_height = True
            secs[0].height = ff_scene.top_drawer_opening_height


def _update_pie_drawer_qty(self, context):
    """pie_drawer_qty changed: repopulate the stacked drawer sections, then
    recalc. Only repopulates on a pie-cut drawer corner."""
    if self.corner_type == 'PIE_CUT_DRAWER':
        populate_pie_drawer_sections(self)
    from . import types_face_frame
    types_face_frame.recalculate_face_frame_cabinet(self.id_data)


def _style_stile_width_for(cab_props, stile_type):
    """Per-(row, column) stile width from the cabinet's assigned style, or
    None if it can't be resolved. Lets a width-only joint stile type take its
    value from the style's row for that type + the cabinet's column."""
    cabinet_obj = cab_props.id_data
    style_name = cabinet_obj.get('STYLE_NAME') if cabinet_obj else None
    if not style_name:
        return None
    try:
        ff = get_style_props()
    except Exception:
        return None
    style = next((cs for cs in ff.cabinet_styles if cs.name == style_name), None)
    if style is None:
        return None
    row = style._STILE_TYPE_TO_ROW.get(stile_type, 'end_stile')
    col = style._CABINET_TYPE_COLUMN.get(cab_props.cabinet_type, 'base')
    return getattr(style, f"ff_{row}_width_{col}", None)


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
    elif stile_type in ('WALL', 'BUTT', 'INSIDE_90', 'ANGLE'):
        # Width-only types (incl. WALL): take the style's per-row/column value.
        width = _style_stile_width_for(cab_props, stile_type)
        if width is None:
            return
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


def update_cabinet_frame_lock(self, context):
    """Toggling a per-cabinet stile / rail lock re-applies the assigned
    cabinet style's frame sizes to this cabinet: a re-locked field snaps
    back to the style value, while still-unlocked fields keep the user's
    override (the apply respects each unlock flag). No-op when the cabinet
    has no resolvable style (e.g. during load)."""
    cabinet_obj = self.id_data
    if cabinet_obj is None:
        return
    style_name = cabinet_obj.get('STYLE_NAME')
    if not style_name:
        return
    try:
        ff = get_style_props(context)
    except Exception:
        return
    style = next((cs for cs in ff.cabinet_styles if cs.name == style_name), None)
    if style is not None:
        style._apply_face_frame_sizes_to_cabinet(cabinet_obj)


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

    # Width lock - consulted by the Grab Cabinet Group operator when
    # distributing a delta across cabinets in a group. Locked cabinets
    # hold their width; unlocked ones absorb. Defaulting False matches
    # bay-level unlock_width semantics (unlocked = free to resize).
    lock_width: BoolProperty(
        name="Lock Width",
        description="Hold this cabinet's width when a containing group is resized",
        default=False,
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
        update=_on_left_finish_end_user_set,
    )  # type: ignore
    right_finished_end_condition: EnumProperty(
        name="Right Finished End", items=FIN_END_ITEMS, default='UNFINISHED',
        update=_on_right_finish_end_user_set,
    )  # type: ignore
    back_finished_end_condition: EnumProperty(
        name="Back Finished End", items=FIN_END_ITEMS, default='UNFINISHED',
        update=_on_back_finish_end_user_set,
    )  # type: ignore

    # Scribe = inset from the face frame outer face to the side panel
    # outer face. The solver multiplexes this against the finish end
    # condition (3/4 finished forces 0 since the side IS the outer face;
    # paneled reserves 3/4" for the panel; others use the typed value),
    # so this prop holds the user setpoint for the unfinished /
    # against-a-wall case (~1/2" typical, 0 for an adjacent cabinet).
    left_scribe: FloatProperty(
        name="Left Scribe", default=0.0, unit='LENGTH', precision=4,
        update=_on_left_scribe_user_set,
    )  # type: ignore
    right_scribe: FloatProperty(
        name="Right Scribe", default=0.0, unit='LENGTH', precision=4,
        update=_on_right_scribe_user_set,
    )  # type: ignore

    # Per-side exposure state. Computed by exposure.recalc_cabinet_exposure
    # from wall edges and parent-wall siblings (cabinets + appliances).
    # Drives the auto-pick of finished_end_condition. Defaults are EXPOSED
    # so a cabinet that hasn't yet been touched by detection reads as if
    # it stands alone - matches the prior default-True placeholder.
    left_exposure: EnumProperty(
        name="Left Exposure", items=EXPOSURE_ITEMS, default='EXPOSED',
    )  # type: ignore
    right_exposure: EnumProperty(
        name="Right Exposure", items=EXPOSURE_ITEMS, default='EXPOSED',
    )  # type: ignore
    back_exposure: EnumProperty(
        name="Back Exposure", items=EXPOSURE_ITEMS, default='EXPOSED',
    )  # type: ignore

    # Adjacent dishwasher (or other panel-ready appliance handled the same
    # way) on this side. Forces FLUSH_X regardless of exposure state when
    # auto-pick is on. Back has no dishwasher concept by design.
    left_dishwasher_adjacent: BoolProperty(
        name="Left Dishwasher Adjacent", default=False,
    )  # type: ignore
    right_dishwasher_adjacent: BoolProperty(
        name="Right Dishwasher Adjacent", default=False,
    )  # type: ignore

    # Auto flag per side. True = exposure recalc is allowed to overwrite
    # the finished_end_condition based on detection. Flipped to False
    # automatically when the user edits the enum directly (see the
    # per-side update callbacks). The Recalculate operator re-arms all
    # three before re-running detection.
    left_finish_end_auto: BoolProperty(
        name="Left Finish End Auto", default=True,
    )  # type: ignore
    right_finish_end_auto: BoolProperty(
        name="Right Finish End Auto", default=True,
    )  # type: ignore
    back_finish_end_auto: BoolProperty(
        name="Back Finish End Auto", default=True,
    )  # type: ignore

    # Finished-end overhang extensions (signed; meters). Applied to the
    # finished-end PART for a side (the FINISHED back/side panel, an
    # applied panel, or a beadboard/shiplap panel) AFTER the carcass is
    # built, growing that part past the cabinet body without changing the
    # carcass. FLUSH_X is excluded - its depth already IS flush_x_amount.
    #   back L/R  -> grow the BACK finished part past the cabinet's left
    #               (-X) / right (+X) end. Positive = overhang, negative
    #               = inset that edge.
    #   side back -> run the LEFT / RIGHT finished part past the cabinet
    #               back (+Y). Positive = overhang behind the cabinet,
    #               negative = inset the back edge forward. The square
    #               front edge stays put.
    back_finished_extend_left: FloatProperty(
        name="Back Extend Left", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    back_finished_extend_right: FloatProperty(
        name="Back Extend Right", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    left_side_finished_extend_back: FloatProperty(
        name="Left Side Extend Back", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_side_finished_extend_back: FloatProperty(
        name="Right Side Extend Back", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

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
    unlock_left_stile: BoolProperty(name="Unlock Left Stile", default=False, update=update_cabinet_frame_lock)  # type: ignore
    unlock_right_stile: BoolProperty(name="Unlock Right Stile", default=False, update=update_cabinet_frame_lock)  # type: ignore
    turn_off_left_stile: BoolProperty(name="Turn Off Left Stile", default=False)  # type: ignore
    turn_off_right_stile: BoolProperty(name="Turn Off Right Stile", default=False)  # type: ignore

    LEFT_STILE_TYPE_ITEMS = [
        ('STANDARD', "Standard", "Standard stile"),
        ('WALL', "Wall", "Wall stile (extends past carcass)"),
        ('BLIND', "Blind", "Blind corner stile"),
        ('BUTT', "Butt", "Butt joint against an adjacent cabinet"),
        ('INSIDE_90', "Inside 90", "Against an inside 90 (pie cut) corner"),
        ('ANGLE', "Angle", "Against a diagonal / angled cabinet"),
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

    # Refrigerator cabinet: per-cabinet opening height + per-side raise.
    # refrigerator_opening_height drives the bottom appliance opening node
    # and keeps the carcass back in sync (see _update_refrigerator_opening_height).
    # The two raise toggles lift that side's carcass side panel AND end stile
    # up to the top of the fridge opening so the side spans only the door zone
    # (consumed in solver_face_frame: side_bottom_z + left/right_end_stile_*).
    refrigerator_opening_height: FloatProperty(
        name="Refrigerator Opening Height", default=units.inch(62.0),
        unit='LENGTH', precision=4,
        update=_update_refrigerator_opening_height,
    )  # type: ignore
    raise_left_to_refrigerator_height: BoolProperty(
        name="Raise Left To Refrigerator Height", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    raise_right_to_refrigerator_height: BoolProperty(
        name="Raise Right To Refrigerator Height", default=False,
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
    unlock_top_rail: BoolProperty(name="Unlock Top Rail (Cabinet)", default=False, update=update_cabinet_frame_lock)  # type: ignore
    unlock_bottom_rail: BoolProperty(name="Unlock Bottom Rail (Cabinet)", default=False, update=update_cabinet_frame_lock)  # type: ignore

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
             "Sides start above the floor by toe_kick_height; the kick is "
             "left open for a separate base the user supplies"),
            ('LOOSE', "Loose (Ladder Base)",
             "Sides float by toe_kick_height; a separate ladder sub-base "
             "(front + rear rail + two end boards) is built on the floor "
             "for the cabinet to sit on"),
            ('LOOSE_FLUSH', "Loose Flush (Ladder Base)",
             "Like Loose, but the ladder sub-base sits FLUSH with the "
             "cabinet front (setback 0) instead of recessed"),
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

    # Tip-up wedge (refrigerator / tall cabinets). When enabled, recalc
    # chamfers the back-bottom corner so the cabinet's tip-up diagonal
    # clears the ceiling. Inputs persist on the cabinet so the wedge
    # recomputes live whenever depth / height / ceiling change; the
    # computed length + height are derived in the solver, not stored.
    wedge_enabled: BoolProperty(
        name="Tip-Up Wedge", default=False,
        description="Chamfer the back-bottom corner so a tall cabinet clears "
                    "the ceiling when tipped upright into place",
        update=_update_cabinet_dim,
    )  # type: ignore
    wedge_ceiling_height: FloatProperty(
        name="Wedge Ceiling Height", default=units.inch(96.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    wedge_fudge: FloatProperty(
        name="Wedge Fudge Allowance", default=units.inch(0.5),
        unit='LENGTH', precision=4, min=0.0, update=_update_cabinet_dim,
    )  # type: ignore
    wedge_max_height: FloatProperty(
        name="Wedge Max Height", default=units.inch(3.0),
        unit='LENGTH', precision=4, min=0.0, update=_update_cabinet_dim,
    )  # type: ignore
    # ---- Construction-tab section visibility (UI only) ----
    show_angled_back_extension: BoolProperty(
        name="Show Angled Back Extension", default=False)  # type: ignore
    show_upper_extensions: BoolProperty(
        name="Show Upper Extensions", default=False)  # type: ignore
    show_toe_kick: BoolProperty(name="Show Toe Kick", default=True)  # type: ignore
    show_finished_ends: BoolProperty(name="Show Finished Ends", default=True)  # type: ignore
    show_wood_top: BoolProperty(name="Show Wood Top", default=False)  # type: ignore
    # ---- Angled back extension (trapezoidal back) ----
    # Per-cabinet, per-end: extend the BACK corner outward in +X (left or
    # right) by the given amount, splaying that side panel so the back is
    # wider than the front while depth and the front face frame stay
    # square. Used to angle a cabinet's back into an angled wall corner so
    # it provides access into the corner instead of leaving a void. Zero
    # = square (no extension); either / both ends may be extended.
    extend_back_left: FloatProperty(
        name="Extend Back Left X", default=0.0,
        unit='LENGTH', precision=4,
        description="Angle the left side by moving the back-left corner along "
                    "X. Positive moves it outward (-X, back wider than front); "
                    "NEGATIVE moves it inward (back narrower than front, e.g. "
                    "into an acute corner). 0 = square.",
        update=_update_cabinet_dim,
    )  # type: ignore
    furniture_top: BoolProperty(
        name="Furniture Top",
        default=False,
        description="Add an overhanging veneer wood top sitting proud on "
                    "the carcass (dresser / furniture products)",
        update=_update_cabinet_dim,
    )  # type: ignore
    furniture_top_thickness: FloatProperty(
        name="Wood Top Thickness", default=units.inch(1.0), min=0.0,
        unit='LENGTH', precision=4,
        description="Thickness of the furniture wood top",
        update=_update_cabinet_dim,
    )  # type: ignore
    furniture_top_overhang: FloatProperty(
        name="Wood Top Overhang", default=units.inch(1.0), min=0.0,
        unit='LENGTH', precision=4,
        description="Overhang of the wood top past the carcass on the "
                    "left, right, and front (the back stays flush)",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_left_end_down: BoolProperty(
        name="Extend Left End Down",
        default=False,
        description="Upper cabinets only: drop the LEFT side and left end "
                    "stile below the box (toward the counter) for a hutch "
                    "look. Independent of the right end; box / doors / back "
                    "stay at standard upper height",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_left_end_down_amount: FloatProperty(
        name="Left End Drop", default=units.inch(19.5), min=0.0,
        unit='LENGTH', precision=4,
        description="How far the left side / end stile drops below the box "
                    "bottom (defaults to the wall-cabinet mount minus the "
                    "base-cabinet height - the counter gap)",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_right_end_down: BoolProperty(
        name="Extend Right End Down",
        default=False,
        description="Upper cabinets only: drop the RIGHT side and right end "
                    "stile below the box (toward the counter) for a hutch "
                    "look. Independent of the left end; box / doors / back "
                    "stay at standard upper height",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_right_end_down_amount: FloatProperty(
        name="Right End Drop", default=units.inch(19.5), min=0.0,
        unit='LENGTH', precision=4,
        description="How far the right side / end stile drops below the box "
                    "bottom (defaults to the wall-cabinet mount minus the "
                    "base-cabinet height - the counter gap)",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_sides_down: BoolProperty(
        name="Extend Sides Down",
        default=False,
        description="Upper cabinets only: drop BOTH carcass side panels "
                    "below the box as furniture legs (the over-stool look). "
                    "Unlike Extend Ends Down, ONLY the sides move - the end "
                    "stiles, face frame, doors and box stay at box bottom",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_sides_down_amount: FloatProperty(
        name="Sides Drop", default=units.inch(7.0), min=0.0,
        unit='LENGTH', precision=4,
        description="How far both side panels drop below the box bottom",
        update=_update_cabinet_dim,
    )  # type: ignore
    side_front_profile: BoolProperty(
        name="Side Front Profile",
        default=False,
        description="Cut the over-stool decorative profile into the "
                    "bottom-front corner of each extended side panel",
        update=_update_cabinet_dim,
    )  # type: ignore
    overstool_accessory: EnumProperty(
        name="Leg Accessory",
        items=[
            ('SHELF', "With Shelf",
             "A shelf spanning between the extended sides"),
            ('TOWEL_BAR', "With Towel Bar",
             "A towel bar spanning between the extended sides"),
            ('SHELF_AND_TOWEL_BAR', "With Shelf and Towel Bar",
             "Both a shelf and a towel bar between the extended sides"),
        ],
        default='SHELF',
        description="What hangs between the extended sides (over-stool legs)",
        update=_update_cabinet_dim,
    )  # type: ignore
    hutch_finished_back: BoolProperty(
        name="Finished Back in Recess",
        default=False,
        description="When an upper's ends are extended down, add a finished "
                    "back panel closing the open recess between the dropped "
                    "sides",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_back_right: FloatProperty(
        name="Extend Back Right X", default=0.0,
        unit='LENGTH', precision=4,
        description="Angle the right side by moving the back-right corner along "
                    "X. Positive moves it outward (+X, back wider than front); "
                    "NEGATIVE moves it inward (back narrower than front, e.g. "
                    "into an acute corner). 0 = square.",
        update=_update_cabinet_dim,
    )  # type: ignore
    # ---- Wing Attached (convert the back extension into a wing) ----
    # Per-cabinet, per-end modifier of extend_back_left / extend_back_right.
    # When ON (and that end's extend is non-zero): instead of splaying the
    # carcass into a trapezoid, keep the carcass SQUARE and add a flat wing
    # panel along the SAME angled line the extension would have used. So the
    # wing's angle / depth come entirely from the extend value - no separate
    # size. No-op when that end's extend is 0. Built in the cabinet recalc
    # (_apply_back_extension branches on these).
    wing_attached_left: BoolProperty(
        name="Attach Left as Wing",
        default=False,
        description="Convert the LEFT end's back extension into an attached "
                    "wing: keep the carcass square and add a flat angled panel "
                    "along the extension line. No effect when Extend Back Left "
                    "is 0.",
        update=_update_cabinet_dim,
    )  # type: ignore
    wing_attached_right: BoolProperty(
        name="Attach Right as Wing",
        default=False,
        description="Convert the RIGHT end's back extension into an attached "
                    "wing: keep the carcass square and add a flat angled panel "
                    "along the extension line. No effect when Extend Back Right "
                    "is 0.",
        update=_update_cabinet_dim,
    )  # type: ignore
    # Extend Bottom (uppers): push the carcass bottom panel laterally past
    # the side(s) to cover the void left in a corner where two uppers meet.
    # Outward only (min 0); only the bottom panel overhangs - the face frame,
    # sides, and doors stay square. Applied in _apply_bottom_extension.
    extend_bottom_left: FloatProperty(
        name="Extend Bottom Left X", default=0.0, min=0.0,
        unit='LENGTH', precision=4,
        description="Overhang the carcass bottom past the LEFT side by this "
                    "amount to cover a corner void. 0 = flush with the side.",
        update=_update_cabinet_dim,
    )  # type: ignore
    extend_bottom_right: FloatProperty(
        name="Extend Bottom Right X", default=0.0, min=0.0,
        unit='LENGTH', precision=4,
        description="Overhang the carcass bottom past the RIGHT side by this "
                    "amount to cover a corner void. 0 = flush with the side.",
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
    # Corner cabinets only: pull each arm's rear (wall-side) toe-kick /
    # loose-ladder rail away from its wall by this amount (left arm off
    # the left wall, right arm off the back wall). 0 = flush to the wall.
    inset_toe_kick_back_left: FloatProperty(
        name="Inset Toe Kick Back Left", default=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    inset_toe_kick_back_right: FloatProperty(
        name="Inset Toe Kick Back Right", default=0.0, unit='LENGTH', precision=4,
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
            ('PIE_CUT_DRAWER', "Pie Cut Drawer", "Pie cut corner drawer base: 45-degree channel carcass with stacked drawer fronts"),
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
            ('BIFOLD_LEFT_SWING',      "Bi-fold Left Swing",     "Bi-fold pair hinged on the left, pull leads on the right"),
            ('BIFOLD_RIGHT_SWING',     "Bi-fold Right Swing",    "Bi-fold pair hinged on the right, pull leads on the left"),
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
    tray_compartment_width: FloatProperty(
        name="Tray Compartment Width",
        description="Clear width of the tray storage strip walled off by the partition",
        default=units.inch(6.0),
        unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_compartment_qty: IntProperty(
        name="Tray Divider Qty",
        description="Number of dividers inside the tray compartment (slots = qty + 1)",
        default=3, min=0, max=10,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_compartment_divider_thickness: FloatProperty(
        name="Tray Divider Thickness",
        default=units.inch(0.25), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    tray_compartment_setback: FloatProperty(
        name="Tray Divider Setback",
        description="Front setback of the tray compartment dividers from the face frame",
        default=units.inch(1.0), unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore
    exterior_config: EnumProperty(
        name="Exterior Config",
        description="Stacked-section layout of a diagonal corner cabinet front",
        items=_exterior_config_items,
        update=_update_exterior_config,
    )  # type: ignore
    # Door swing for the diagonal face's DOORS sections. Per-cabinet,
    # applied to every DOORS section (matches the pie cut's per-cabinet
    # exterior_option swing handling). The single swings build one
    # full-width leaf hinged on the named edge, pull on the unhinged
    # edge. Default LEFT_SWING (was DOUBLE_DOOR historically; changed
    # by request -- note an old blend's diagonal cabinet left at the
    # default will read LEFT_SWING after this change and flip on its
    # next recalc).
    diag_door_swing: EnumProperty(
        name="Door Swing",
        description="Door leaf layout for the diagonal face's door sections",
        items=[
            ('DOUBLE_DOOR', "Double Door", "Pair of doors meeting at the center, hinged on the outer edges"),
            ('LEFT_SWING',  "Left Swing",  "Single full-width door hinged on the left edge"),
            ('RIGHT_SWING', "Right Swing", "Single full-width door hinged on the right edge"),
        ],
        default='LEFT_SWING',
        update=_update_cabinet_dim,
    )  # type: ignore
    clip_back_amount: FloatProperty(
        name="Clip Back",
        description="Length of the 45 degree clip taken off each wall side at the rear corner (0 = no clip)",
        default=units.inch(6.0), min=0.0, unit='LENGTH', precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    mid_stile_widths: CollectionProperty(type=Face_Frame_Mid_Stile_Width)  # type: ignore
    corner_sections: CollectionProperty(type=Face_Frame_Corner_Section)  # type: ignore
    pie_drawer_qty: IntProperty(
        name="Drawer Qty",
        description="Number of stacked drawers in a pie-cut drawer corner; the top opening defaults to the Top Drawer Opening Height for 3 or 4 drawers",
        default=3, min=2, max=4,
        update=_update_pie_drawer_qty,
    )  # type: ignore


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
        update=_update_remove_bottom,
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
    # Finished interior: the exterior finish material reads inside this
    # bay's opening, realized by adding finish-material liner panels on
    # the left / right / top / back inner faces (a shared carcass back /
    # top can't be re-materialed per-bay, so dedicated liner parts carry
    # the finish). finish_bay_flush brings those liners flush with the
    # face frame opening and runs them only finish_bay_flush_depth back
    # into the opening - the common "refrigerator opening finished flush
    # X inches" case. Flush off = liner lines the full cavity depth.
    finish_bay: BoolProperty(
        name="Finish Bay", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    finish_bay_flush: BoolProperty(
        name="Finish Flush", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    finish_bay_flush_depth: FloatProperty(
        name="Flush Depth", default=0.0, unit='LENGTH', precision=4,
        description="How far the flush finish runs back into the opening; "
                    "0 runs the full cavity depth",
        update=_update_cabinet_dim,
    )  # type: ignore

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


class Face_Frame_Rollout_Box(bpy.types.PropertyGroup):
    """One drawer box in a ROLLOUT stack. Each box carries its own height
    so a stack can mix sizes; height_preset picks a standard size (or
    Custom to type one). The preset writes its value into `height`, which
    the solver reads when stacking the boxes bottom to top.
    """
    height_preset: EnumProperty(
        name="Height",
        description="Standard rollout box height, or Custom to type an exact value",
        items=ROLLOUT_HEIGHT_PRESET_ITEMS, default='IN_4_625',
        update=_update_rollout_box_preset,
    )  # type: ignore
    height: FloatProperty(
        name="Box Height",
        description="Height of this rollout drawer box",
        default=units.inch(4.625), unit='LENGTH', precision=4,
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
    # Per-box rollout heights: each ROLLOUT box is an entry here with its
    # own height, so a stack can mix sizes. Empty on items saved before this
    # field; the recalc seeds it once from rollout_height x qty (migration)
    # and the solver falls back to that uniform stack until it does. For a
    # ROLLOUT the box count is len(rollout_boxes); qty/unlock_qty are now
    # PULLOUT_SHELF-only.
    rollout_boxes: CollectionProperty(type=Face_Frame_Rollout_Box)  # type: ignore
    rollout_boxes_index: IntProperty(default=0)  # type: ignore

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
        name="Accessory Label", default="ACCESSORY",
        update=_update_cabinet_dim,
    )  # type: ignore

    # ACCESSORY: product code from the host application's accessory catalog,
    # set when the accessory is picked from the catalog rather than typed as
    # a free label. Drives the 2D legend + pricing; no 3D effect. Empty for a
    # hand-typed accessory_label.
    accessory_code: StringProperty(
        name="Accessory Code", default="",
    )  # type: ignore


# Front-type options for a face-frame opening. Module-level so operators
# (e.g. the split-opening dialog) can build per-opening enums from the
# same canonical list the opening PropertyGroup uses.
FRONT_TYPE_ITEMS = [
    ('NONE', "None", "No front (open shelving)"),
    ('DOOR', "Door", "Hinged door"),
    ('DRAWER_FRONT', "Drawer Front", "Drawer front"),
    ('PULLOUT', "Pullout", "Door front on a pullout slide; supports pullout accessories"),
    ('FALSE_FRONT', "False Front", "Decorative drawer-style panel; fixed (does not open)"),
    ('TILT_OUT', "Tilt-Out", "Drawer-style front hinged on the bottom; tilts down to open"),
    ('INSET_PANEL', "Inset Panel", "1/4\" panel filling the face frame opening; no overlay, no swing"),
    ('APPLIANCE', "Appliance", "Open opening sized for an appliance; adds left/right filler stiles to fit the appliance width"),
]


def _update_drawer_look_divisions(self, context):
    """Sync the per-opening height list to the division count, then recalc.

    Mirrors a standard drawer stack: on a count change the top opening is
    seeded to the scene Top Drawer Opening Height (held) and the rest start
    auto / equal. Editing the rows afterwards behaves like stack openings.
    """
    from . import types_face_frame
    coll = self.drawer_look_openings
    n = 0 if self.drawer_look_divisions == 'NONE' else int(self.drawer_look_divisions)
    with types_face_frame.suspend_recalc():
        while len(coll) > n:
            coll.remove(len(coll) - 1)
        while len(coll) < n:
            coll.add()
        if n:
            top_oh = bpy.context.scene.hb_face_frame.top_drawer_opening_height
            for i, item in enumerate(coll):
                # index n-1 == top opening: held at the top-drawer height;
                # the rest auto (share the remainder equally).
                item.unlock_size = (i == n - 1)
                if i == n - 1:
                    item.size = top_oh
        types_face_frame.recalculate_face_frame_cabinet(self.id_data)


class Face_Frame_Drawer_Look_Opening(PropertyGroup):
    """One drawer-opening height for a drawer-look door. unlock_size = the
    user set this height (held); locked rows share the remainder equally,
    matching a standard drawer stack. Heights are OPENING heights (front
    height = opening + overlays), consumed by _build_drawer_look_fronts."""
    size: FloatProperty(
        name="Opening Height", default=units.inch(6.0), unit='LENGTH',
        precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    unlock_size: BoolProperty(
        name="Unlock Opening Height",
        description="Hold this opening height; locked rows share the remainder equally",
        default=False, update=_update_cabinet_dim,
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
    # ---- Opening dialog section visibility (UI only) ----
    show_front: BoolProperty(name="Show Front Type", default=True)  # type: ignore
    show_finish: BoolProperty(name="Show Finish Options", default=False)  # type: ignore
    show_overlays: BoolProperty(name="Show Overlays", default=False)  # type: ignore
    show_interior_items: BoolProperty(name="Show Interior Items", default=True)  # type: ignore

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

    front_type: EnumProperty(
        name="Front Type", items=FRONT_TYPE_ITEMS, default='NONE',
        update=_update_front_type,
    )  # type: ignore

    # ---- APPLIANCE front type: filler stiles fitting an appliance ----
    # When front_type == 'APPLIANCE' the opening carries no door/drawer;
    # instead up to two narrow face-frame filler stiles are added at the
    # left/right inboard edges so the clear opening matches the appliance
    # width. Two input modes, toggled by set_appliance_width:
    #   ON  -> user types appliance_width; left/right fillers are computed
    #          at build time as (clear_opening - appliance_width)/2 each.
    #   OFF -> user types left/right filler widths directly; the appliance
    #          width is whatever clear opening remains.
    # include_fillers gates whether the filler parts are built, so an
    # opening can be reserved as an appliance without fillers yet.
    set_appliance_width: BoolProperty(
        name="Set Appliance Width",
        description="Enter the appliance width and split the remainder into equal left/right fillers; off lets you type each filler width directly",
        default=True, update=_update_cabinet_dim,
    )  # type: ignore
    appliance_width: FloatProperty(
        name="Appliance Width",
        description="Width of the appliance the opening must fit; fillers fill the remainder",
        default=units.inch(24.0), unit='LENGTH', precision=4, min=0.0,
        update=_update_cabinet_dim,
    )  # type: ignore
    include_fillers: BoolProperty(
        name="Include Fillers",
        description="Build the left/right filler stiles; off reserves the opening as an appliance with no fillers",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore
    left_filler_amount: FloatProperty(
        name="Left Filler",
        description="Width of the left filler stile (used directly when Set Appliance Width is off)",
        default=0.0, unit='LENGTH', precision=4, min=0.0,
        update=_update_cabinet_dim,
    )  # type: ignore
    right_filler_amount: FloatProperty(
        name="Right Filler",
        description="Width of the right filler stile (used directly when Set Appliance Width is off)",
        default=0.0, unit='LENGTH', precision=4, min=0.0,
        update=_update_cabinet_dim,
    )  # type: ignore

    # PULLOUT model: an accessory product code chosen for a PULLOUT
    # opening. Stored as a bare string code; the display name, price and
    # minimum opening width are looked up from whatever accessory catalog
    # the host application registers (see accessory_registry). Empty when
    # no model is chosen. No 3D effect -- drives 2D annotation and pricing.
    pullout_accessory_code: StringProperty(
        name="Pullout Model",
        description="Accessory product code selected for this pullout opening",
        default="",
    )  # type: ignore
    # Tilt-out: a FALSE_FRONT on hinges (tray behind). Geometrically
    # identical to a plain false front, so it's a flag rather than a
    # front_type -- the only behavioral difference is the 2D elevation
    # label (TILT-OUT instead of FALSE, read by Spaces). Set / cleared
    # by the TILT_OUT opening preset; lives on the persistent opening
    # cage so it survives recalcs.
    is_tilt_out: BoolProperty(
        name="Tilt-Out",
        description="Label this false front as a tilt-out on 2D drawings",
        default=False,
    )  # type: ignore

    # Drawer-look door: a single working DOOR leaf whose face carries N
    # applied drawer-front panels (reveal gaps between them read as mid
    # rails) so it looks like a stack of drawers but opens as one door.
    # NONE = a plain door. The applied fronts + their pulls are built in
    # _update_fronts_in_opening, parented to the door so they swing as one;
    # they carry no pricing tags (the leaf prices as a single door). Lives
    # on the persistent opening cage so it survives recalcs.
    drawer_look_divisions: EnumProperty(
        name="Drawer-Look Divisions",
        description="Show this door as a stack of N applied drawer fronts (still opens as one door)",
        items=[
            ('NONE', "None", "Plain door (no drawer-look fronts)"),
            ('2', "2 Drawers", "Two applied drawer fronts"),
            ('3', "3 Drawers", "Three applied drawer fronts"),
            ('4', "4 Drawers", "Four applied drawer fronts"),
        ],
        default='NONE',
        update=_update_drawer_look_divisions,
    )  # type: ignore
    # Per-drawer OPENING heights, edited like a standard drawer stack
    # (unlock to set a height; locked rows share the remainder). Synced to
    # the division count by _update_drawer_look_divisions; consumed by
    # _build_drawer_look_fronts (front height = opening height + overlays).
    drawer_look_openings: CollectionProperty(type=Face_Frame_Drawer_Look_Opening)  # type: ignore

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

    # Per-opening finish: the bay-level finish_bay behavior scoped to a
    # single opening (e.g. one sub-opening of a split bay). The exterior
    # finish reads inside this opening via liner panels on its inner
    # faces; finish_opening_flush + finish_opening_flush_depth mirror the
    # bay flush controls (0 depth = full cavity depth). A bay-level finish
    # supersedes per-opening finish within that bay.
    finish_opening: BoolProperty(
        name="Finish Opening", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    finish_opening_flush: BoolProperty(
        name="Finish Flush", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    finish_opening_flush_depth: FloatProperty(
        name="Flush Depth", default=0.0, unit='LENGTH', precision=4,
        description="How far the flush finish runs back into the opening; "
                    "0 runs the full cavity depth",
        update=_update_cabinet_dim,
    )  # type: ignore

    # Sink apron: a fixed face-frame-depth panel across the top of a door
    # opening (for an apron / farmhouse sink). The door(s) stay full
    # height; the apron sits behind them at the frame plane. Only built
    # for door front types.
    add_apron: BoolProperty(
        name="Add Apron", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    apron_height: FloatProperty(
        name="Apron Height", default=units.inch(7.0), unit='LENGTH',
        precision=4, min=0.0, update=_update_cabinet_dim,
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


class Face_Frame_Splitter_Width(PropertyGroup):
    """Per-splitter width override inside one split node.

    A split node with N children emits N-1 splitter members (mid rails
    for an H-split, mid stiles for a V-split). The node's scalar
    splitter_width is the default applied to every member; this
    collection lets an individual member hold its own width so the user
    can size one mid rail in a bay without dragging its siblings along.

    Index N maps to the splitter at gap N (the solver's splitter_index,
    also stamped on the part as hb_splitter_index). An entry is honored
    only when `active` is True; otherwise the member follows the node's
    scalar splitter_width. The collection grows lazily on first edit, so
    a split with no per-member overrides carries an empty collection and
    behaves exactly as before.
    """
    width: FloatProperty(
        name="Width",
        default=units.inch(1.5),
        unit='LENGTH',
        precision=4,
        update=_update_cabinet_dim,
    )  # type: ignore

    active: BoolProperty(
        name="Active",
        description="Use this per-splitter width instead of the split's default",
        default=False,
    )  # type: ignore

    remove_member: BoolProperty(
        name="Remove Member",
        description=(
            "Drop this splitter's face-frame member (and its carcass backing). "
            "The opening stays split; the solver collapses the gap so the two "
            "fronts sit 3/32\" apart. Used between drawers"
        ),
        default=False,
        update=_update_cabinet_dim,
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
    unlock_splitter_width: BoolProperty(
        name="Unlock Splitter Width",
        description="Hold this split's mid rail / mid stile width when a cabinet style is applied",
        default=False, update=_update_cabinet_dim,
    )  # type: ignore

    # Per-splitter width overrides, indexed by splitter_index. Empty =
    # every member follows the scalar splitter_width above; an entry with
    # active=True holds that one member's width independently (set via the
    # right-click Set Width on a single mid rail / mid stile).
    splitter_widths: CollectionProperty(type=Face_Frame_Splitter_Width)  # type: ignore

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


def _update_interior_add_face_frame(self, context):
    """Toggle callback for the optional interior face frame part.
    The first time the toggle is enabled, seed face_frame_width from
    the cabinet mid rail (H-split) or mid stile (V-split) width so
    the width field opens on the cabinet default; 0.0 marks it
    unseeded. Writing face_frame_width fires its own recalc, so the
    seed path returns without a second _update_cabinet_dim call.
    """
    if self.add_face_frame and self.face_frame_width <= 0.0:
        from . import types_face_frame
        cab = types_face_frame.find_cabinet_root(self.id_data)
        if cab is not None:
            cp = cab.face_frame_cabinet
            self.face_frame_width = (cp.bay_mid_rail_width
                                     if self.axis == 'H'
                                     else cp.bay_mid_stile_width)
            return
    _update_cabinet_dim(self, context)


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

    add_face_frame: BoolProperty(
        name="Add Face Frame",
        description="Add a face frame rail (fixed shelf) or stile "
                    "(division) inline with the cabinet face frame at "
                    "this split. Sits behind the doors and does not "
                    "split the door fronts",
        default=False, update=_update_interior_add_face_frame,
    )  # type: ignore
    face_frame_width: FloatProperty(
        name="Face Frame Width",
        description="Width of the optional face frame part at this "
                    "split. Seeded from the cabinet mid rail / mid "
                    "stile width when first enabled",
        default=0.0, unit='LENGTH', precision=4,
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
            # 'Applied Panels' is reachable via the Show Applied Panels
            # operator in the Finished Ends and Backs panel; intentionally
            # absent from the main mode picker (see ui/view3d_sidebar.py).
            ('Applied Panels', "Applied Panels",
             "Select applied finished-end panels"),
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

    library_view_mode: EnumProperty(
        name="Library View",
        description="Show library items as thumbnail tiles or a compact list",
        items=[
            ('THUMBNAIL', "Thumbnail", "Thumbnail tiles with previews", 'IMGDISPLAY', 0),
            ('LIST', "List", "Compact list of names", 'LONGDISPLAY', 1),
        ],
        default='THUMBNAIL',
    )  # type: ignore

    # ---- Library section toggles ----
    show_cabinet_sizes: BoolProperty(name="Show Cabinet Sizes", default=True)  # type: ignore
    show_corner_sizes: BoolProperty(name="Show Corner Sizes", default=False)  # type: ignore
    show_appliance_sizes: BoolProperty(name="Show Appliance Sizes", default=False)  # type: ignore
    show_opening_heights: BoolProperty(name="Show Opening Heights", default=False)  # type: ignore
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
    door_style_tab: EnumProperty(
        name="Style Tab",
        description="Switch between the door style and drawer front style lists",
        items=[('DOOR', "Door Styles", "Edit door styles"),
               ('DRAWER', "Drawer Front Styles", "Edit drawer front styles")],
        default='DOOR',
    )  # type: ignore
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
    # Backs get their own default (a shop often runs a different
    # treatment on an exposed island back than on exposed ends).
    # Defaults to FINISHED so existing scenes behave as before until
    # the user picks something else. Read by exposure._resolve_finish_
    # type for side == 'back'; L/R keep default_finished_end_type.
    default_finished_back_type: EnumProperty(
        name="Default Finished Back Type",
        description="Finished-end type auto-applied to exposed cabinet backs",
        items=FIN_END_ITEMS, default='FINISHED',
    )  # type: ignore
    # What exposure auto-pick writes to a side that abuts a dishwasher
    # (or other panel-ready appliance). Default UNFINISHED: the side
    # comes in unfinished with the standard 0.25" neighbor scribe, and
    # a flush fin is added manually per side when wanted. Pick FLUSH_X
    # here to restore the automatic flush fin (amount from Default
    # Flush X Amount). Read by exposure._resolve_finish_type.
    dishwasher_finished_end_type: EnumProperty(
        name="Dishwasher Side Finished End Type",
        description="Finished end auto-applied to cabinet sides abutting a dishwasher",
        items=FIN_END_ITEMS, default='UNFINISHED',
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
    drawer_front_styles: CollectionProperty(type=Face_Frame_Door_Style)  # type: ignore
    active_drawer_front_style_index: IntProperty(name="Active Drawer Front Style Index", default=0)  # type: ignore

    # ---- Default placement behaviour ----
    fill_cabinets: BoolProperty(
        name="Fill Cabinets",
        description="When dropping a cabinet, fill the available space",
        default=True,
    )  # type: ignore

    cabinet_placement_holdoff: FloatProperty(
        name="Cabinet Placement Hold-off",
        description=(
            "Hold cabinets back from entry doors, windows, open wall "
            "ends, and outside corners by this amount during placement. "
            "Inside corners run flush. Arrow-key offsets override this "
            "per side."
        ),
        default=units.inch(5.0),
        unit='LENGTH',
        precision=4,
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
        default=units.inch(69.0),
        unit='LENGTH',
        precision=4,
    )  # type: ignore

    refrigerator_cabinet_width: FloatProperty(
        name="Refrigerator Cabinet Width",
        description="Default refrigerator cabinet width",
        default=units.inch(40.0),
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

        layout.separator()
        ohbox = layout.box()
        ohbox.prop(self, 'show_opening_heights', text="Opening Heights",
                   icon='TRIA_DOWN' if self.show_opening_heights else 'TRIA_RIGHT',
                   emboss=False)
        if self.show_opening_heights:
            row = ohbox.row()
            row.label(text="Tall Split Height:")
            row.prop(self, 'tall_cabinet_split_height', text="")
            row = ohbox.row()
            row.label(text="Top Drawer Opening Height:")
            row.prop(self, 'top_drawer_opening_height', text="")
            # Re-sync existing drawer-preset cabinets to the value above
            # (changing it does not re-flow cabinets already built).
            row.operator('hb_face_frame.refresh_top_drawer_openings',
                         text="", icon='FILE_REFRESH')
            row = ohbox.row()
            row.label(text="Upper Stacked Top Height:")
            row.prop(self, 'upper_top_stacked_cabinet_height', text="")

        # Corner + appliance sizes live here (moved out of their library
        # sections) so those sections list only products and this whole
        # block collapses with Cabinet Sizes.
        cbox = layout.box()
        cbox.prop(self, 'show_corner_sizes', text="Corner Sizes",
                  icon='TRIA_DOWN' if self.show_corner_sizes else 'TRIA_RIGHT',
                  emboss=False)
        if self.show_corner_sizes:
            row = cbox.row()
            row.label(text="")
            row.label(text="Base")
            row.label(text="Tall")
            row.label(text="Upper")
            row = cbox.row()
            row.label(text="Inside Corner:")
            row.prop(self, 'base_inside_corner_size', text="")
            row.prop(self, 'tall_inside_corner_size', text="")
            row.prop(self, 'upper_inside_corner_size', text="")
            row = cbox.row()
            row.label(text="Blind Width:")
            row.prop(self, 'base_width_blind', text="")
            row.prop(self, 'tall_width_blind', text="")
            row.prop(self, 'upper_width_blind', text="")

        abox = layout.box()
        abox.prop(self, 'show_appliance_sizes', text="Appliance Sizes",
                  icon='TRIA_DOWN' if self.show_appliance_sizes else 'TRIA_RIGHT',
                  emboss=False)
        if self.show_appliance_sizes:
            row = abox.row()
            row.label(text="Refrigerator Height:")
            row.prop(self, 'refrigerator_height', text="")
            row = abox.row()
            row.label(text="Refrigerator Width:")
            row.prop(self, 'refrigerator_cabinet_width', text="")
            row = abox.row()
            row.label(text="Dishwasher / Range:")
            row.prop(self, 'dishwasher_width', text="")
            row.prop(self, 'range_width', text="")
            row = abox.row()
            row.label(text="Sink / Oven:")
            row.prop(self, 'sink_cabinet_width', text="")
            row.prop(self, 'oven_cabinet_width', text="")

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
        # List view: a tight column of full-width name buttons -- no
        # thumbnails, so many more products fit without scrolling. The
        # operator + payload match the thumbnail tiles exactly.
        if self.library_view_mode == 'LIST':
            # Two-column grid of plain name buttons -- denser than one
            # full-width row each, no thumbnails. Long names truncate.
            flow = layout.grid_flow(row_major=True, columns=2,
                                    even_columns=True, even_rows=False,
                                    align=True)
            for name in products:
                op = flow.operator('hb_face_frame.draw_cabinet', text=name)
                op.cabinet_name = name
            return

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

    def _draw_catalog_labeled_row(self, layout, label, items):
        """One row: an optional left LABEL (omitted when blank) then
        product buttons to its right. `items` is a list of
        (display, cabinet_name) so the button
        can show a short name (e.g. "Base") while firing the full product
        ("Pie Cut Base"). Honors the thumbnail/list toggle: thumbnails get
        a tile each, list gets compact text buttons.
        """
        row = layout.row(align=True)
        if label:
            row.label(text=label)
        if self.library_view_mode == 'LIST':
            for display, cab in items:
                op = row.operator('hb_face_frame.draw_cabinet', text=display)
                op.cabinet_name = cab
        else:
            for display, cab in items:
                cell = row.column(align=True)
                icon_id = load_cabinet_thumbnail(cab)
                if icon_id:
                    cell.template_icon(icon_value=icon_id, scale=4.0)
                op = cell.operator('hb_face_frame.draw_cabinet', text=display)
                op.cabinet_name = cab

    # =====================================================================
    # UI: standard cabinet library
    # =====================================================================
    def draw_cabinet_library_ui(self, layout, context):
        # One row, short labels (the section header already says
        # "Standard Cabinets", so no per-row label is needed).
        self._draw_catalog_labeled_row(layout, "", [
            ("Base", "Base"), ("Tall", "Tall"), ("Upper", "Upper"),
            ("Lap", "Lap Drawer"), ("Stacked", "Upper Stacked"),
        ])

    # =====================================================================
    # UI: corner cabinet library
    # =====================================================================
    def draw_corner_cabinet_library_ui(self, layout, context):
        # Sizes moved to Cabinet Sizes. Grouped by corner type, one
        # labeled row each: Pie Cut (Base/Drawer/Upper), Diagonal
        # (Base/Tall/Upper).
        self._draw_catalog_labeled_row(layout, "Pie Cut", [
            ("Base", "Pie Cut Base"), ("Drawer", "Pie Cut Drawer"),
            ("Upper", "Pie Cut Upper"),
        ])
        self._draw_catalog_labeled_row(layout, "Diagonal", [
            ("Base", "Diagonal Base"), ("Tall", "Diagonal Tall"),
            ("Upper", "Diagonal Upper"),
        ])

    # =====================================================================
    # UI: appliance products library
    # =====================================================================
    def draw_appliance_library_ui(self, layout, context):
        # Sizes (heights + widths) moved to Cabinet Sizes. Grouped into
        # two labeled rows: freestanding appliances vs appliance cabinets.
        # NOTE: there is no dedicated "Oven" product, so the Oven button
        # maps to "Built in Tall" (the built-in tall oven tower).
        self._draw_catalog_labeled_row(layout, "Cabinet", [
            ("Sink", "Sink"), ("Refrigerator", "Refrigerator Cabinet"),
            ("Oven", "Built in Tall"),
        ])
        self._draw_catalog_labeled_row(layout, "Standalone", [
            ("Dishwasher", "Dishwasher"), ("Range", "Range"),
            ("Hood", "Range Hood"),
            ("Refrigerator", "Standalone Refrigerator"),
        ])

    # =====================================================================
    # UI: vanities library
    # =====================================================================
    def draw_vanity_library_ui(self, layout, context):
        self._draw_catalog_labeled_row(layout, "Vanity", [
            ("Special", "Special"), ("Combination", "Combination"),
            ("Deluxe", "Deluxe"),
        ])

    # =====================================================================
    # UI: parts library
    # =====================================================================
    def draw_part_library_ui(self, layout, context):
        # Vanity parts hidden for now -- re-add when the Vanity part
        # products are created:
        # self._draw_catalog_labeled_row(layout, "Vanity", [
        #     ("End Leg", "Vanity End Leg Assembly"),
        #     ("Support Leg", "Vanity Support Leg"),
        #     ("Fixed Shelf", "Vanity Fixed Shelf"),
        # ])
        # General label hidden for now (only row in Parts); blank label omits it.
        self._draw_catalog_labeled_row(layout, "", [
            ("Panel", "Panel"), ("Leg", "Leg Product"), ("Door", "Door"),
            ("Misc", "Misc Part"), ("Floating Shelf", "Floating Shelves"),
        ])

    # =====================================================================
    # UI: specialty bath library
    # =====================================================================
    def draw_specialty_bath_library_ui(self, layout, context):
        self._draw_catalog_labeled_row(layout, "Medicine", [
            ("Recessed", "Standard Recessed Medicine Cabinet"),
            ("Standard", "Medicine Cabinet"),
            ("Tri-View", "Tri-View Medicine Cabinet"),
        ])
        self._draw_catalog_labeled_row(layout, "Other", [
            ("Overstool", "Overstool Cabinet"), ("Mirror", "Mirror Frame"),
            ("Tub Skirt", "Tub Skirt"),
        ])

    # =====================================================================
    # UI: specialty bedroom & bookcases library
    # =====================================================================
    def draw_bedroom_bookcase_library_ui(self, layout, context):
        # Bookcase Corner / Bookcase Corner Upper dropped -- not in the
        # catalog dispatch (dead buttons).
        self._draw_catalog_labeled_row(layout, "Bookcase", [
            ("Base", "Bookcase"), ("Storage", "Bookcase Storage Unit"),
            ("Upper", "Bookcase Upper"),
        ])
        self._draw_catalog_labeled_row(layout, "Dresser", [
            ("5 Drawer", "5 Drawer Dresser"),
            ("6 Drawer", "6 Drawer Dresser"),
        ])
        self._draw_catalog_labeled_row(layout, "Night Stand", [
            ("Standard", "Night Stand"),
            ("3 Drawer", "3 Drawer Night Stand"),
        ])
        self._draw_catalog_labeled_row(layout, "Other", [
            ("Hutch", "Hutch Upper"), ("Window Seat", "Window Seat"),
        ])

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
        # One row, short labels (matches the other categories). X-Frame Ends
        # hidden for now -- re-add when that product has a builder:
        #     ("X-Frame", "X-Frame Ends"),
        self._draw_catalog_labeled_row(layout, "", [
            ("Half Wall", "Half Wall"), ("Support", "Support Frame"),
            ("FF & Doors", "Face Frame and Doors"),
        ])

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
        # default_scribe and default_panel_frame_auto (with its top/bottom
        # rail and stile width children) are intentionally hidden from
        # this UI. The underlying properties still drive the solver - the
        # user just doesn't access them here.
        col = layout.column(align=True)
        col.prop(self, 'default_finished_end_type', text="Type")
        col.prop(self, 'default_finished_back_type', text="Back Type")
        col.prop(self, 'dishwasher_finished_end_type', text="Dishwasher Side")
        # The amount field serves whichever default resolves to FLUSH_X;
        # exposure auto-pick seeds the per-cabinet amount from it.
        if (self.default_finished_end_type == 'FLUSH_X'
                or self.default_finished_back_type == 'FLUSH_X'
                or self.dishwasher_finished_end_type == 'FLUSH_X'):
            col.prop(self, 'default_flush_x_amount', text="Flush X Amount")
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
        col.operator(
            "hb_face_frame.recalculate_side_exposure",
            text="Recalculate Side Exposure", icon='FILE_REFRESH',
        )
        # When the scene default is anything other than plain FINISHED,
        # applied panels can exist in the scene. Surface the Show Applied
        # Panels operator here so it's reachable from the same panel that
        # configures the finish type.
        if (self.default_finished_end_type != 'FINISHED'
                or self.default_finished_back_type != 'FINISHED'):
            col.separator()
            col.operator(
                "hb_face_frame.show_applied_panels",
                text="Show Applied Panels", icon='HIDE_OFF',
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
        # Pool is project-global (main scene); draw it regardless of which
        # room scene is active.
        sp = get_style_props(context)
        row = layout.row()
        row.template_list(
            "HB_UL_face_frame_cabinet_styles", "",
            sp, "cabinet_styles",
            sp, "active_cabinet_style_index",
            rows=3,
        )
        side = row.column(align=True)
        side.operator("hb_face_frame.add_cabinet_style", text="", icon='ADD')
        side.operator("hb_face_frame.remove_cabinet_style", text="", icon='REMOVE')
        # Reorder: 2D fill colours follow list order (first style = white), so
        # moving a style up/down changes which one is left white.
        side.separator()
        side.operator("hb_face_frame.move_cabinet_style", text="", icon='TRIA_UP').direction = 'UP'
        side.operator("hb_face_frame.move_cabinet_style", text="", icon='TRIA_DOWN').direction = 'DOWN'

        if sp.cabinet_styles and sp.active_cabinet_style_index < len(sp.cabinet_styles):
            style = sp.cabinet_styles[sp.active_cabinet_style_index]
            # Assign to Selected hits the current selection; Assign by
            # Painting is a modal click-to-assign; Update walks every
            # cabinet already tagged with this style name.
            btn = layout.row(align=True)
            btn.scale_y = 1.3
            btn.operator("hb_face_frame.assign_style_to_selected_cabinets",
                         text="Assign to Selected", icon='RESTRICT_SELECT_OFF')
            btn.operator("hb_face_frame.paint_assign_cabinet_style",
                         text="Assign by Painting", icon='BRUSH_DATA')
            btn.operator("hb_face_frame.update_cabinets_from_style",
                         text="", icon='FILE_REFRESH')
            style.draw_cabinet_style_ui(layout, context)
        else:
            box = layout.box()
            box.label(text="No cabinet styles defined", icon='INFO')

    def draw_door_styles_ui(self, layout, context):
        # Door styles and drawer front styles are SEPARATE project-global
        # pools (independent lists). A tab switches between them so only one
        # list + editor draws at a time; the catalog the editor reads is
        # implied by the pool (see _front_is_drawer), so neither shows a Kind
        # field.
        sp = get_style_props(context)
        tab_row = layout.row()
        tab_row.prop(sp, "door_style_tab", expand=True)

        if sp.door_style_tab == 'DRAWER':
            coll, idx_attr = "drawer_front_styles", "active_drawer_front_style_index"
            add_op = "hb_face_frame.add_drawer_front_style"
            rem_op = "hb_face_frame.remove_drawer_front_style"
            empty = "No drawer front styles defined"
        else:
            coll, idx_attr = "door_styles", "active_door_style_index"
            add_op = "hb_face_frame.add_door_style"
            rem_op = "hb_face_frame.remove_door_style"
            empty = "No door styles defined"

        row = layout.row()
        row.template_list(
            "HB_UL_face_frame_door_styles", "",
            sp, coll,
            sp, idx_attr,
            rows=3,
        )
        side = row.column(align=True)
        side.operator(add_op, text="", icon='ADD')
        side.operator(rem_op, text="", icon='REMOVE')

        pool = getattr(sp, coll)
        idx = getattr(sp, idx_attr)
        if pool and idx < len(pool):
            pool[idx].draw_door_style_ui(layout, context)
        else:
            layout.box().label(text=empty, icon='INFO')

    # =====================================================================
    # UI: master draw entry point (called by view3d_sidebar)
    # =====================================================================
    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        # Tab selector. On the LIBRARY tab an icon-only Thumbnail/List
        # toggle is pinned to the right end of this same row.
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, 'face_frame_tabs', 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, 'face_frame_tabs', 'OPTIONS', icon='PREFERENCES')

        if self.face_frame_tabs == 'LIBRARY':
            view = row.row(align=True)
            view.alignment = 'RIGHT'
            view.prop(self, 'library_view_mode', expand=True, icon_only=True)

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
                ('show_appliance_library',        "Appliance Products",           self.draw_appliance_library_ui),
                ('show_corner_cabinet_library',   "Corner Cabinets",              self.draw_corner_cabinet_library_ui),
                ('show_vanity_library',           "Vanities",                     self.draw_vanity_library_ui),
                ('show_part_library',             "Parts",                        self.draw_part_library_ui),
                ('show_specialty_bath_library',   "Specialty Bath",               self.draw_specialty_bath_library_ui),
                ('show_bedroom_bookcase_library', "Specialty Bedroom & Bookcases", self.draw_bedroom_bookcase_library_ui),
                # Angled hidden for now -- re-add when Angled products exist:
                # ('show_angled_library', "Angled", self.draw_angled_library_ui),
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
            row.prop(self, 'show_door_styles', text="Door & Drawer Front Styles",
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
class Face_Frame_Leg_Props(PropertyGroup):
    """Options for the Leg Product (a slim face-frame post / filler).

    Lives on the leg's cage object alongside face_frame_cabinet. The leg's
    recalculate() override reads these to build its parts; width / height /
    depth still come from face_frame_cabinet (the cage Dim X/Z/Y). All
    fields reuse _update_cabinet_dim so an edit re-runs the leg recalc
    through the standard cabinet recalc entry point.

    v1 covers the core post (two finished side panels + stile + toe kick).
    Back / nailers, Finish-X bands, and the column / appliance / island
    variants are deferred to a later pass.
    """
    finish_type: EnumProperty(
        name="Finish Type",
        items=[
            ('FINISH_LEFT', "Finish Left",
             "Finished panel on the left face only"),
            ('INTERMEDIATE', "Intermediate",
             "Unfinished filler post between cabinets"),
            ('FINISH_RIGHT', "Finish Right",
             "Finished panel on the right face only"),
            ('FINISH_BOTH', "Finish Both",
             "Finished panels on both faces"),
        ],
        default='FINISH_LEFT',
        update=_update_cabinet_dim,
    )  # type: ignore
    only_stile: BoolProperty(
        name="Only Include Stile", default=False,
        description="Drop the side panels and toe-kick filler; keep just "
                    "the face-frame stile",
        update=_update_cabinet_dim,
    )  # type: ignore
    is_column: BoolProperty(
        name="Column", default=False,
        description="Column variant: no toe kick (runs full height)",
        update=_update_cabinet_dim,
    )  # type: ignore
    material_thickness: FloatProperty(
        name="Material Thickness", default=units.inch(0.75),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    face_frame_thickness: FloatProperty(
        name="Face Frame Thickness", default=units.inch(0.75),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height", default=units.inch(4.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback", default=units.inch(3.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore

    # --- v2 fields ---
    # Per-panel depth overrides: 0 means "use depth - face frame thickness".
    override_left_panel_depth: FloatProperty(
        name="Override Left Panel Depth", default=0.0,
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    override_right_panel_depth: FloatProperty(
        name="Override Right Panel Depth", default=0.0,
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    # Back + nailers (interior). The back spans only the included
    # nailer side(s); panels shift forward by the back thickness when a
    # back is present.
    include_back_left_nailer: BoolProperty(
        name="Include Back Left Nailer", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    include_back_right_nailer: BoolProperty(
        name="Include Back Right Nailer", default=False,
        update=_update_cabinet_dim,
    )  # type: ignore
    back_width: FloatProperty(
        name="Back Width", default=units.inch(18.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    back_thickness: FloatProperty(
        name="Back Thickness", default=units.inch(0.25),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    nailer_thickness: FloatProperty(
        name="Nailer Thickness", default=units.inch(0.75),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    nailer_width: FloatProperty(
        name="Nailer Width", default=units.inch(1.5),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    # Finished band covering the front X inches on the unfinished side(s).
    flush_x_panel_width: FloatProperty(
        name="Flush X Panel Width", default=units.inch(4.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    # Placement / labeling metadata variants (no geometry effect today;
    # parity with the reference for downstream routing).
    is_appliance_leg: BoolProperty(
        name="Appliance Leg", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    is_island_leg: BoolProperty(
        name="Island Leg", default=False, update=_update_cabinet_dim,
    )  # type: ignore


class Face_Frame_Floating_Shelf_Props(PropertyGroup):
    """Options for a Floating Shelf (a wall-mounted hollow slab).

    Lives on the shelf's cage object alongside face_frame_cabinet; the
    shelf's recalculate() reads these to build its parts. Width / height
    / depth come from face_frame_cabinet (cage Dim X/Z/Y) - note height
    (Dim Z) is the shelf's overall thickness. finish_left / finish_right
    add a closed end panel on that end (auto-set on placement from the
    neighbouring exposure, editable after). LED routes are a later pass.
    """
    finish_left: BoolProperty(
        name="Finish Left", default=True, update=_update_cabinet_dim,
        description="Close the left end with a finished panel",
    )  # type: ignore
    finish_right: BoolProperty(
        name="Finish Right", default=True, update=_update_cabinet_dim,
        description="Close the right end with a finished panel",
    )  # type: ignore
    material_thickness: FloatProperty(
        name="Material Thickness", default=units.inch(0.75),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    shelf_type: EnumProperty(
        name="Shelf Type",
        items=[
            ('FLOATING', "Floating Shelves",
             "Cantilevered floating shelf"),
            ('NON_FLOATING', "Non-Floating Shelves",
             "Shelf with visible support"),
            ('HEAVY_DUTY', "Heavy Duty Floating Shelves",
             "Heavy duty floating shelf; supports a light groove"),
        ],
        default='FLOATING',
        update=_update_cabinet_dim,
    )  # type: ignore
    # Light groove (Heavy Duty only) - a routed LED channel on the top
    # and/or bottom face, set a distance in from the rear edge.
    include_groove_top: BoolProperty(
        name="Groove Top", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    include_groove_bottom: BoolProperty(
        name="Groove Bottom", default=False, update=_update_cabinet_dim,
    )  # type: ignore
    groove_distance_from_rear: FloatProperty(
        name="Groove Distance From Rear", default=units.inch(2.0),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    groove_width: FloatProperty(
        name="Groove Width", default=units.inch(0.5),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore
    groove_depth: FloatProperty(
        name="Groove Depth", default=units.inch(0.25),
        unit='LENGTH', precision=4, update=_update_cabinet_dim,
    )  # type: ignore


classes = (
    Face_Frame_Leg_Props,
    Face_Frame_Floating_Shelf_Props,
    Face_Frame_Millwork_Item,
    Face_Frame_Special_Effect,
    Face_Frame_Cabinet_Extra_Front_Style,
    Face_Frame_Cabinet_Style,
    HB_UL_face_frame_cabinet_styles,
    Face_Frame_Door_Style,
    HB_UL_face_frame_door_styles,
    Face_Frame_Mid_Stile_Width,
    Face_Frame_Corner_Section,
    Face_Frame_Cabinet_Props,
    Face_Frame_Bay_Props,
    Face_Frame_Rollout_Box,
    Face_Frame_Interior_Item,
    Face_Frame_Interior_Region_Props,
    Face_Frame_Drawer_Look_Opening,
    Face_Frame_Opening_Props,
    Face_Frame_Splitter_Width,
    Face_Frame_Split_Props,
    Face_Frame_Interior_Split_Props,
    Face_Frame_Scene_Props,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


@bpy.app.handlers.persistent
def _seed_style_rename_anchors(_dummy):
    """On file load, seed each cabinet style's rename_anchor from its current
    name. Files saved before rename-propagation existed have empty anchors;
    without this seed their first rename could not re-tag assigned cabinets."""
    for scene in bpy.data.scenes:
        ff = getattr(scene, 'hb_face_frame', None)
        if ff is None:
            continue
        for style in getattr(ff, 'cabinet_styles', ()):
            if not style.rename_anchor:
                style.rename_anchor = style.name


def register():
    _register_classes()

    if _seed_style_rename_anchors not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_seed_style_rename_anchors)

    # Object-level pointer properties: face frame cabinets and bays carry
    # their state on the cage object directly. Only objects that get tagged
    # by the construction code populate these.
    bpy.types.Object.face_frame_cabinet = PointerProperty(type=Face_Frame_Cabinet_Props)
    bpy.types.Object.leg_product = PointerProperty(type=Face_Frame_Leg_Props)
    bpy.types.Object.floating_shelf = PointerProperty(type=Face_Frame_Floating_Shelf_Props)
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
    if hasattr(bpy.types.Object, 'floating_shelf'):
        del bpy.types.Object.floating_shelf
    if hasattr(bpy.types.Object, 'leg_product'):
        del bpy.types.Object.leg_product
    if hasattr(bpy.types.Object, 'face_frame_cabinet'):
        del bpy.types.Object.face_frame_cabinet

    if _seed_style_rename_anchors in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_seed_style_rename_anchors)

    _unregister_classes()
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
