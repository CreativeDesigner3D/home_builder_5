"""Closet library properties.

Three PropertyGroups:
- Closets_Scene_Props (Scene.hb_closets): library defaults + library UI.
- Closet_Starter_Props (Object.hb_closet_starter): live dimensions and
  starter-level options on each starter root cage.
- Closet_Bay_Props (Object.hb_closet_bay): per-bay overrides on each bay
  cage (width/lock, height, depth, floor-mounted, remove flags).

No drivers: every update callback routes through
types_closets.recalculate_closet_starter, which is guarded against
reentry (system writes during a recalc don't loop back here).
"""
import bpy
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


def _update_bay_prop(self, context):
    """Bay-level prop changed (height/depth/floor/remove flags)."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_bay_width(self, context):
    """Bay width changed. System writes during redistribution are
    ignored; a user edit locks the bay so the value holds when the
    remaining widths are redistributed."""
    from . import types_closets
    root = types_closets.find_starter_root(self.id_data)
    if root is None:
        return
    root_id = id(root)
    if (root_id in types_closets._RECALCULATING
            or root_id in types_closets._DISTRIBUTING_WIDTHS):
        return
    self.width_locked = True
    types_closets.recalculate_closet_starter(root)


def _update_closet_selection_mode(self, context):
    """Apply visibility highlighting for the active closet selection
    mode (mirrors face_frame's update_face_frame_selection_mode)."""
    bpy.ops.hb_closets.toggle_mode(search_obj_name="")


# ---------------------------------------------------------------------------
# Object-level: starter root
# ---------------------------------------------------------------------------
class Closet_Starter_Props(PropertyGroup):

    width: FloatProperty(
        name="Width", description="Starter width (X)",
        default=const.DEFAULT_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    height: FloatProperty(
        name="Height", description="Panel height (Z)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Panel depth (Y)",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    closet_type: EnumProperty(
        name="Closet Type",
        items=[
            ('BASE', "Base", "Floor-mounted base starter"),
            ('TALL', "Tall", "Floor-mounted full-height starter"),
            ('HANGING', "Hanging", "Wall-mounted hanging starter"),
            ('ISLAND', "Island", "Single-sided island starter"),
        ],
        default='BASE')  # type: ignore

    toe_kick_height: FloatProperty(
        name="Toe Kick Height",
        default=const.DEFAULT_TOE_KICK_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback",
        default=const.DEFAULT_TOE_KICK_SETBACK, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    include_countertop: BoolProperty(
        name="Include Countertop", default=False,
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
    width_locked: BoolProperty(
        name="Lock Width",
        description="Hold this bay's width during redistribution",
        default=starter_presets.BAY_PROP_DEFAULTS['width_locked'])  # type: ignore

    height: FloatProperty(
        name="Height", description="Bay height (envelope, floor to top shelf)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Bay depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore

    floor_mounted: BoolProperty(
        name="Floor Mounted",
        description="Bay sits on the floor with a toe kick; off = the bay "
                    "hangs from its top height (top and bottom fixed shelves)",
        default=True, update=_update_bay_prop)  # type: ignore
    remove_bottom: BoolProperty(
        name="Remove Bottom", default=starter_presets.BAY_PROP_DEFAULTS['remove_bottom'],
        update=_update_bay_prop)  # type: ignore
    remove_cleat: BoolProperty(
        name="Remove Cleat", default=starter_presets.BAY_PROP_DEFAULTS['remove_cleat'],
        update=_update_bay_prop)  # type: ignore


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

    # ----- Library UI state -----
    show_closet_sizes: BoolProperty(name="Show Closet Sizes", default=False)  # type: ignore
    show_starter_library: BoolProperty(name="Show Closet Starters", default=True)  # type: ignore
    show_closet_options: BoolProperty(name="Show Closet Options", default=False)  # type: ignore
    # Sub-toggles inside Closet Options for the two dense categories.
    show_material_options: BoolProperty(name="More Material Options", default=False)  # type: ignore
    show_pull_options: BoolProperty(name="More Pull Options", default=False)  # type: ignore

    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, 'show_closet_sizes', text="Closet Sizes",
                 icon='TRIA_DOWN' if self.show_closet_sizes else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_closet_sizes:
            for prop_name in ('default_closet_width', 'default_panel_depth',
                              'base_panel_height', 'tall_panel_height',
                              'hanging_panel_height', 'hanging_top_height',
                              'panel_thickness', 'shelf_thickness',
                              'countertop_thickness', 'toe_kick_height',
                              'toe_kick_setback'):
                box.prop(self, prop_name)

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, 'show_starter_library', text="Closet Starters",
                 icon='TRIA_DOWN' if self.show_starter_library else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_starter_library:
            # One row per section: the section LABEL on the left, then a
            # thumbnail tile + place button per product to its right
            # (matches the face_frame catalog's labeled-row layout). Bay
            # count is derived from width at placement (target ~42").
            for sec_label, entries in starter_presets.STARTER_SECTIONS:
                row = box.row(align=True)
                row.label(text=sec_label)
                for name, label, _desc in entries:
                    cell = row.column(align=True)
                    icon_id = load_starter_thumbnail(name)
                    if icon_id:
                        cell.template_icon(icon_value=icon_id, scale=4.0)
                    op = cell.operator('hb_closets.place_starter',
                                      text=label)
                    op.starter_name = name

        # ----- Options: one collapsible "Closet Options" section.
        # One aligned label / value row per category; the two dense
        # categories (Materials, Pulls) tuck their extra fields behind
        # "More ..." sub-toggles. Dropdown changes re-apply room-wide.
        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(self, 'show_closet_options', text="Closet Options",
                 icon='TRIA_DOWN' if self.show_closet_options
                 else 'TRIA_RIGHT',
                 emboss=False)
        if self.show_closet_options:
            def option_row(parent, label):
                """Aligned label / value row: label in a fixed-width
                left column so the dropdowns line up in one column."""
                split = parent.split(factor=0.35)
                split.label(text=label)
                return split.row(align=True)

            def sub_toggle(parent, prop_name, label):
                row = parent.row()
                row.alignment = 'LEFT'
                row.prop(self, prop_name, text=label,
                         icon='TRIA_DOWN' if getattr(self, prop_name)
                         else 'TRIA_RIGHT',
                         emboss=False)
                return getattr(self, prop_name)

            # align=False keeps Blender's normal row spacing so the
            # option rows read as separate items rather than a block.
            opts = box.column(align=False)

            option_row(opts, "Materials").prop(
                self, 'closet_material', text="")
            if sub_toggle(opts, 'show_material_options',
                          "More Material Options"):
                sub = opts.box().column(align=True)
                option_row(sub, "Fronts").prop(
                    self, 'closet_front_material', text="")
                option_row(sub, "Closet Edge").prop(
                    self, 'closet_edge_material', text="")
                option_row(sub, "Front Edge").prop(
                    self, 'closet_front_edge_material', text="")
                option_row(sub, "Door Grain").prop(
                    self, 'closet_door_grain', text="")
                option_row(sub, "Drawer Grain").prop(
                    self, 'closet_drawer_grain', text="")

            option_row(opts, "Pulls").prop(self, 'closet_pull', text="")
            if sub_toggle(opts, 'show_pull_options', "More Pull Options"):
                sub = opts.box().column(align=True)
                option_row(sub, "Finish").prop(
                    self, 'closet_pull_finish', text="")
                sub.label(text="Vertical Location:")
                vrow = sub.row(align=True)
                vrow.prop(self, 'pull_vertical_location_base')
                vrow.prop(self, 'pull_vertical_location_upper')
                vrow.prop(self, 'pull_vertical_location_tall')
                option_row(sub, "From Edge").prop(
                    self, 'pull_horizontal_offset', text="")
                sub.prop(self, 'center_pulls_on_drawer_front')

            rrow = option_row(opts, "Rods")
            rrow.prop(self, 'closet_rod_type', text="")
            rrow.prop(self, 'closet_rod_finish', text="")

            hrow = option_row(opts, "Hangers")
            hrow.prop(self, 'closet_hanger_model', text="")
            hrow.operator('hb_closets.randomize_hangers', text="",
                          icon='FILE_REFRESH')
            hrow.operator('hb_closets.install_model_pack', text="",
                          icon='IMPORT')

            option_row(opts, "Front Style").prop(
                self, 'closet_front_style', text="")
            option_row(opts, "Door Panel").prop(
                self, 'closet_panel_type', text="")
            option_row(opts, "Drawer Box").prop(
                self, 'closet_drawer_box', text="")

            mrow = option_row(opts, "Molding")
            mrow.prop(self, 'closet_crown_profile', text="")
            mrow.operator('hb_closets.add_molding', text="", icon='ADD')
            mrow.operator('hb_closets.delete_molding', text="", icon='X')


classes = (
    Closet_Starter_Props,
    Closet_Bay_Props,
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
