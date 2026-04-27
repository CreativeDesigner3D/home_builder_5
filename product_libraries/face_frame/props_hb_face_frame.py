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
    """Hook for Phase 3 - will toggle outliner visibility / select filters."""
    pass


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
            ('Cabinets', "Cabinets", "Cabinets"),
            ('Bays', "Bays", "Bays"),
            ('Openings', "Openings", "Openings"),
            ('Interiors', "Interiors", "Interiors"),
            ('Parts', "Parts", "Parts"),
        ],
        default='Cabinets',
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
    Face_Frame_Scene_Props,
)


_register_classes, _unregister_classes = bpy.utils.register_classes_factory(classes)


def register():
    _register_classes()
    # Initialize preview collections so thumbnails load on first sidebar draw
    get_library_previews()
    get_cabinet_previews()


def unregister():
    _unregister_classes()
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
