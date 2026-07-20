"""
Wood Hood part construction.

Builds the 3D parts of a wood hood as driven cutparts parented to the
Hood appliance cage, so they resize with the hood like face-frame cabinet
parts. Triggered from the appliance right-click menu ("Build Wood Hood")
with a style picker.

Styles share a parametric box carcass (front + two sides + top, open
bottom) with optional bottom/crown bands, applied front panels, shiplap
boards, or trapezoid (angled) and flared profiles. A style without its
own builder falls back to the plain box so the command always produces
geometry. The CUSTOM style composes these pieces from per-hood options
(angles, mantle, fan cutout, front panel) stored on the cage.
"""

import json
import math
import re
import bpy
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty,
                       StringProperty)
from mathutils import Euler, Matrix

from ... import hb_utils
from ...hb_types import GeoNodeObject, GeoNodeCutpart
from ...units import inch
from . import door_builder


HOOD_PART_TAG = "IS_WOOD_HOOD_PART"
HOOD_STYLE_PROP = "WOOD_HOOD_STYLE"
# Per-hood options for the CUSTOM style (angles, mantle, fan cutout, front
# panel), stored as a dict on the hood cage so rebuilds / reopening the
# prompts keep them. See _CUSTOM_DEFAULTS for the keys.
HOOD_CUSTOM_PROP = "WOOD_HOOD_CUSTOM_OPTS"
# JSON snapshot of a hood part's parametric recipe (modifier node group +
# input values, drivers, transform), stashed when the part is Made Editable so
# it can be reverted to parametric one part at a time. See snapshot_hood_part.
HOOD_SNAPSHOT_PROP = "HOOD_PARAMETRIC_SNAPSHOT"
HOOD_MATERIAL = inch(0.75)

# Pre-5.2 driver paths address modifier inputs as ID properties
# (modifiers["X"]["Socket_2"]); 5.2 moved them to RNA
# (modifiers["X"].properties.inputs.Socket_2.value). Snapshots persist in
# saved files and may have been written under either version, so restore
# migrates paths to whichever format the running Blender uses.
_OLD_MOD_INPUT_PATH_RE = re.compile(r'(modifiers\["[^"]+"\])\["([A-Za-z0-9_]+)"\]')
_NEW_MOD_INPUT_PATH_RE = re.compile(
    r'(modifiers\["[^"]+"\])\.properties\.inputs\.([A-Za-z0-9_]+)\.value')


def _migrate_mod_input_path(data_path):
    if hb_utils.GN_INPUTS_AS_RNA:
        return _OLD_MOD_INPUT_PATH_RE.sub(r'\1.properties.inputs.\2.value', data_path)
    return _NEW_MOD_INPUT_PATH_RE.sub(r'\1["\2"]', data_path)

WOOD_HOOD_STYLE_ITEMS = [
    ('BOX', "Box", "Box wood hood"),
    ('SHIPLAP_BOX', "Shiplap Box", "Box hood with shiplap face"),
    ('SHIPLAP_MANTLE', "Shiplap Mantle", "Mantle hood with shiplap face"),
    ('SHIPLAP_PENINSULA', "Shiplap Peninsula", "Peninsula hood with shiplap, finished all sides"),
    ('SHELF', "Shelf", "Shelf wood hood"),
    ('NICHE', "Niche", "Niche wood hood"),
    ('MANTLE', "Mantle", "Mantle wood hood"),
    ('PENINSULA', "Peninsula", "Peninsula wood hood"),
    ('TRADITIONAL', "Traditional", "Traditional wood hood"),
    ('VILLA', "Villa", "Villa wood hood"),
    ('CHIMNEY', "Chimney", "Chimney wood hood"),
    ('PLANTATION', "Plantation", "Plantation wood hood"),
    ('GRAND_MANTLE', "Grand Mantle", "Grand mantle wood hood"),
    ('CUSTOM', "Custom", "Custom hood built from user options (angles, mantle, fan cutout, front panel)"),
]


class _HoodWrap(GeoNodeObject):
    """Wrap an existing hood cage object so GeoNodeObject helpers
    (var_input) can read its Dim X/Y/Z for driving child parts."""

    def __init__(self, obj):
        self.obj = obj


def _clear_hood_parts(hood_obj):
    """Wipe the hood's generated parts ahead of a rebuild. Parts the user
    made editable (IS_MANUAL_PART) are kept -- their hand edits survive the
    rebuild, alongside the freshly generated parts."""
    for child in list(hood_obj.children):
        if child.get(HOOD_PART_TAG) and not child.get('IS_MANUAL_PART'):
            bpy.data.objects.remove(child, do_unlink=True)


def _panel(hood_obj, name):
    p = GeoNodeCutpart()
    p.create(name)
    p.obj.parent = hood_obj
    p.obj[HOOD_PART_TAG] = True
    p.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
    return p


def _mantle_parts(hood_obj, band, depth):
    """Mantle assembly at the hood bottom -- real parts rather than one
    solid slab: a full-width front board at the mantle's front plane, side
    fillers running back to the hood sides' front edges, and (when the
    depth projects past the applied front) a top board capping the ledge.
    ``depth`` is the mantle's total front-to-back depth off the sides.
    All driven so the assembly tracks the cage."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    mt = HOOD_MATERIAL
    depth = max(depth, mt)

    # Front board, full width, its face at the mantle's front plane.
    mf = _panel(hood_obj, "Hood Mantle Front")
    mf.obj.rotation_euler.x = math.radians(90)
    mf.driver_location('y', '-dim_y + %f' % (2.0 * mt - depth), [dim_y])
    mf.driver_input("Length", 'dim_x', [dim_x])
    mf.set_input("Width", band)
    mf.set_input("Thickness", mt)
    mf.set_input("Mirror Z", False)

    # Side fillers from the hood sides' front edges to the front board.
    if depth - mt > 0.0:
        for name, at_right in (("Hood Mantle Side L", False),
                               ("Hood Mantle Side R", True)):
            ms = _panel(hood_obj, name)
            ms.obj.rotation_euler.y = math.radians(-90)
            if at_right:
                ms.driver_location('x', 'dim_x', [dim_x])
            ms.driver_location('y', '-dim_y + %f' % mt, [dim_y])
            ms.set_input("Length", band)
            ms.set_input("Width", depth - mt)
            ms.set_input("Thickness", mt)
            ms.set_input("Mirror Y", True)
            ms.set_input("Mirror Z", not at_right)

    # Top board filling the projection past the applied front, flush with
    # the mantle top.
    if depth - 2.0 * mt > 0.0:
        tf = _panel(hood_obj, "Hood Mantle Top")
        tf.obj.location.x = mt
        tf.obj.location.z = band
        tf.driver_location('y', '-dim_y', [dim_y])
        tf.driver_input("Length", 'dim_x - %f' % (2.0 * mt), [dim_x])
        tf.set_input("Width", depth - 2.0 * mt)
        tf.set_input("Thickness", mt)
        tf.set_input("Mirror Y", True)
        tf.set_input("Mirror Z", True)


def _build_hood_box(hood_obj, bottom_band=0.0, top_crown=0.0, band_proj=0.0,
                    include_front=True, include_left_side=True,
                    include_right_side=True):
    """Core box carcass: full left/right sides, a top cap inset between
    them, and an applied front -- full width, in front of the sides and
    top, which stop 3/4" short of the face. Optional projecting bands at
    the bottom (mantle / shelf base) and top (crown). All driven off the
    cage Dim X/Y/Z and butted on 3/4" material. The include_* flags skip
    a plain part when something else fills its layer (the CUSTOM paneled
    face frame / paneled ends)."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    mt = HOOD_MATERIAL
    two_mt = 2.0 * mt

    # Left + right sides (full height, stopping behind the applied front).
    for name, at_right, wanted in (("Hood Left Side", False, include_left_side),
                                   ("Hood Right Side", True, include_right_side)):
        if not wanted:
            continue
        s = _panel(hood_obj, name)
        s.obj.rotation_euler.y = math.radians(-90)
        if at_right:
            s.driver_location('x', 'dim_x', [dim_x])
        s.driver_input("Length", 'dim_z', [dim_z])
        s.driver_input("Width", 'dim_y - %f' % mt, [dim_y])
        s.set_input("Thickness", mt)
        s.set_input("Mirror Y", True)
        s.set_input("Mirror Z", not at_right)

    # Top cap, inset between the sides, stopping behind the applied front.
    top = _panel(hood_obj, "Hood Top")
    top.obj.location.x = mt
    top.driver_location('z', 'dim_z', [dim_z])
    top.driver_input("Length", 'dim_x - %f' % two_mt, [dim_x])
    top.driver_input("Width", 'dim_y - %f' % mt, [dim_y])
    top.set_input("Thickness", mt)
    top.set_input("Mirror Y", True)
    top.set_input("Mirror Z", True)

    # Applied front: full width, covering the side + top edges, between
    # the bands.
    if include_front:
        front = _panel(hood_obj, "Hood Front")
        front.obj.rotation_euler.x = math.radians(90)
        front.obj.location.z = bottom_band
        front.driver_location('y', '-dim_y', [dim_y])
        front.driver_input("Length", 'dim_x', [dim_x])
        front.driver_input("Width", 'dim_z - %f' % (bottom_band + top_crown), [dim_z])
        front.set_input("Thickness", mt)
        front.set_input("Mirror Z", True)

    # Bottom mantle / shelf base: a built assembly (front + side fillers +
    # projection cap) whose total depth off the sides is mt + band_proj.
    if bottom_band > 0.0:
        _mantle_parts(hood_obj, bottom_band, mt + band_proj)

    # Top crown band, full width, back against the sides like the mantle.
    if top_crown > 0.0:
        tc = _panel(hood_obj, "Hood Crown")
        tc.obj.rotation_euler.x = math.radians(90)
        tc.obj.location.z = 0.0
        tc.driver_location('y', '-dim_y + %f' % mt, [dim_y])
        tc.driver_location('z', 'dim_z - %f' % top_crown, [dim_z])
        tc.driver_input("Length", 'dim_x', [dim_x])
        tc.set_input("Width", top_crown)
        tc.set_input("Thickness", mt + band_proj)
        tc.set_input("Mirror Z", False)


def _build_box(hood_obj):
    _build_hood_box(hood_obj)


def _add_front_panels(hood_obj, mt, bottom_band=0.0, top_crown=0.0, ndoors=2):
    """Applied raised panels on the front face (driven). Splits the face
    into ``ndoors`` side-by-side panels, each inset by stile/rail and stood
    proud of the front to read as a panelled door."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    stile = inch(2.5)
    rail = inch(2.5)
    center = inch(3.0)
    proud = inch(0.5)
    # Margins measure from the hood edges: the front is applied full width,
    # so the panels inset by stile alone.
    height_expr = 'dim_z - %f' % (bottom_band + top_crown + 2.0 * rail)
    if ndoors == 2:
        width_expr = '(dim_x - %f) * 0.5' % (2.0 * stile + center)
        doors = [("Hood Panel L", stile, None),
                 ("Hood Panel R", None, 'dim_x * 0.5 + %f' % (center * 0.5))]
    else:
        width_expr = 'dim_x - %f' % (2.0 * stile)
        doors = [("Hood Panel", stile, None)]
    for name, x_static, x_expr in doors:
        pnl = _panel(hood_obj, name)
        pnl.obj.rotation_euler.x = math.radians(90)
        pnl.obj.location.z = bottom_band + rail
        if x_static is not None:
            pnl.obj.location.x = x_static
        else:
            pnl.driver_location('x', x_expr, [dim_x])
        pnl.driver_location('y', '-dim_y', [dim_y])
        pnl.driver_input("Length", width_expr, [dim_x])
        pnl.driver_input("Width", height_expr, [dim_z])
        pnl.set_input("Thickness", proud)
        pnl.set_input("Mirror Z", False)


def _build_mantle(hood_obj):
    _build_hood_box(hood_obj, bottom_band=inch(6), band_proj=inch(2))
    _add_front_panels(hood_obj, HOOD_MATERIAL, bottom_band=inch(6), ndoors=2)


def _build_plantation(hood_obj):
    _build_hood_box(hood_obj, bottom_band=inch(6), band_proj=inch(2))
    _add_front_panels(hood_obj, HOOD_MATERIAL, bottom_band=inch(6), ndoors=2)


def _build_grand_mantle(hood_obj):
    _build_hood_box(hood_obj, bottom_band=inch(8), top_crown=inch(5), band_proj=inch(2))
    _add_front_panels(hood_obj, HOOD_MATERIAL, bottom_band=inch(8), top_crown=inch(5), ndoors=2)


def _mesh_part(hood_obj, name, verts, faces):
    """Custom mesh part parented to the hood cage (for non-rectangular
    shapes cutparts can't do). Built at the hood's current size; not
    driven -- re-run Build Wood Hood after resizing an angled/flared
    style. Tagged like the other parts so a rebuild wipes it."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    obj[HOOD_PART_TAG] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
    cols = hood_obj.users_collection or [bpy.context.scene.collection]
    for c in cols:
        c.objects.link(obj)
    obj.parent = hood_obj
    return obj


def _mesh_box(hood_obj, name, x0, x1, y0, y1, z0, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
         (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return _mesh_part(hood_obj, name, v, f)


def _build_angled(hood_obj, top_depth_in, top_crown=0.0, bottom_band=0.0):
    """Angled hood (Traditional / Villa / Chimney): trapezoid side panels
    (full depth at the base, narrowing to ``top_depth_in`` at the top), a
    sloped front face between them, and a top. Optional crown box at the
    top and mantle band at the bottom. Custom meshes -> static (rebuilt on
    the command, not live-driven)."""
    w = _HoodWrap(hood_obj)
    W = w.get_input('Dim X')
    D = w.get_input('Dim Y')
    H = w.get_input('Dim Z')
    mt = HOOD_MATERIAL
    td = inch(top_depth_in)
    body_top = H - top_crown

    def side(x0):
        x1 = x0 + mt
        v = [(x0, 0.0, 0.0), (x0, -D, 0.0), (x0, -td, body_top), (x0, 0.0, body_top),
             (x1, 0.0, 0.0), (x1, -D, 0.0), (x1, -td, body_top), (x1, 0.0, body_top)]
        f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        _mesh_part(hood_obj, "Hood Side", v, f)

    side(0.0)
    side(W - mt)
    # Sloped front face between the sides.
    fz = bottom_band
    _mesh_part(hood_obj, "Hood Front",
               [(mt, -D, fz), (W - mt, -D, fz),
                (W - mt, -td, body_top), (mt, -td, body_top)],
               [(0, 1, 2, 3)])
    # Top cap.
    _mesh_part(hood_obj, "Hood Top",
               [(mt, -td, body_top), (W - mt, -td, body_top),
                (W - mt, 0.0, body_top), (mt, 0.0, body_top)],
               [(0, 1, 2, 3)])
    if bottom_band > 0.0:
        _mesh_box(hood_obj, "Hood Bottom Band",
                  0.0, W, -D - inch(2), 0.0, 0.0, bottom_band)
    if top_crown > 0.0:
        _mesh_box(hood_obj, "Hood Crown",
                  -inch(1), W + inch(1), -td - inch(1), inch(1),
                  body_top, H)


def _build_traditional(hood_obj):
    _build_angled(hood_obj, 12.0)


def _build_villa(hood_obj):
    _build_angled(hood_obj, 12.0, top_crown=inch(5), bottom_band=inch(6))


def _build_chimney(hood_obj):
    _build_angled(hood_obj, 6.0, bottom_band=inch(6))


# ---------------------------------------------------------------------------
# CUSTOM style -- user-driven options stored on the hood cage
# ---------------------------------------------------------------------------

_CUSTOM_DEFAULTS = {
    'angle_front': False,           # slope the front back to top_depth
    'top_depth': inch(12.0),
    'angle_sides': False,           # taper the sides in to top_width
    'top_width': inch(24.0),
    'top_height': 0.0,              # straight section at the top of an
    #                                 angled hood; 0 = angle runs to the top
    'include_mantle': False,        # projecting band at the bottom
    'mantle_height': inch(6.0),
    'mantle_depth': inch(2.75),     # front-to-back depth of the mantle part
    'include_mantle_molding': False,  # strips wrapping the mantle top + bottom
    'mantle_molding_width': inch(1.5),
    'mantle_molding_thickness': inch(0.75),
    'include_bottom_molding': False,  # strip wrapping the hood bottom front + sides
    'bottom_molding_width': inch(1.5),
    'bottom_molding_thickness': inch(0.75),
    'fan_cutout_width': inch(30.0),  # opening in the bottom liner shelf
    'fan_cutout_depth': inch(12.0),
    'fan_cutout_offset': 0.0,        # shift the opening front (+) / back (-)
    'floor_height': 0.0,             # raise the liner shelf off the bottom
    'include_front_panel': False,   # paneled face frame replacing the front
    'panel_stile_width': inch(2.5),
    'panel_top_rail_width': inch(2.5),
    'panel_bottom_rail_width': inch(2.5),
    'panel_count': 2,               # bays across; mid stiles = count - 1
    'bay_fronts': (),               # per-bay front kind (see _BAY_FRONT_KINDS)
    'left_end_panel': False,        # paneled end replacing the left side
    'right_end_panel': False,       # paneled end replacing the right side
    'left_end_front': 'PANEL',      # what fills the left end frame
    'right_end_front': 'PANEL',     # what fills the right end frame
    'door_mid_rails': 0,            # mid rails on every hood door
    'door_mid_stiles': 0,           # mid stiles on every hood door
    # Relative panel sizes for the door grid, as ratio strings parsed by
    # door_builder.parse_grid_ratios ("1 2 1" / "1/4 1/2 1/4" = quarter,
    # half, quarter). Blank = equal cells.
    'door_grid_col_ratios': "",     # column widths, left to right
    'door_grid_row_ratios': "",     # row heights, bottom to top
    'include_shiplap': False,       # shiplap boards on the front
    'shiplap_board_width': inch(6.0),  # course width; last course trims
}

# Front kinds a face-frame bay can carry: an overlay door, an inset door
# (flush with the frame, 1/8" reveal), or no door -- just the 1/4" inset
# panel closing the opening (back flush with the frame back, like a
# cabinet's INSET_PANEL bay).
_BAY_FRONT_KINDS = ('PANEL', 'OVERLAY_DOOR', 'INSET_DOOR')

BAY_FRONT_ITEMS = [
    ('PANEL', "Inset Panel", "No door; a 1/4\" inset panel closes the opening"),
    ('OVERLAY_DOOR', "Overlay Door", "Door overlaying the face frame opening"),
    ('INSET_DOOR', "Inset Door", "Door inset in the opening, flush with the frame"),
]


def _bay_front_list(opts, n):
    """The per-bay front kinds normalized to ``n`` entries (unknown /
    missing entries fall back to the inset panel so the hood stays
    closed)."""
    fronts = [f if f in _BAY_FRONT_KINDS else 'PANEL'
              for f in list(opts.get('bay_fronts') or [])]
    return (fronts + ['PANEL'] * n)[:n]


def _end_front_kind(opts, at_right):
    """What fills a paneled end's frame opening, normalized."""
    kind = opts.get('right_end_front' if at_right else 'left_end_front')
    return kind if kind in _BAY_FRONT_KINDS else 'PANEL'


def _hood_style(hood_obj):
    """The face-frame cabinet style assigned to the hood (STYLE_NAME),
    falling back to the project's active style; None when the face-frame
    library / style props can't be resolved."""
    try:
        from ..face_frame.props_hb_face_frame import get_style_props
        ff = get_style_props()
        if ff is None:
            return None
        name = hood_obj.get('STYLE_NAME')
        style = next((s for s in ff.cabinet_styles if s.name == name), None) \
            if name else None
        if style is None and 0 <= ff.active_cabinet_style_index < len(ff.cabinet_styles):
            style = ff.cabinet_styles[ff.active_cabinet_style_index]
        return style
    except Exception:
        return None


def _hood_door_overlays(hood_obj):
    """(left, right, top, bottom) overlay amounts for the hood's overlay
    doors, read from the assigned / active cabinet style's overlay table
    (the same table assign_style_to_cabinet writes onto cabinets). An
    inset-flavored style or no style falls back to the classic 1/2"."""
    style = _hood_style(hood_obj)
    try:
        if style is not None:
            l, r, t, b = style._OVERLAY_TABLE.get(
                style.door_overlay_type, style._OVERLAY_TABLE['CLASSIC'])
            if min(l, r, t, b) > 0.0:
                return inch(l), inch(r), inch(t), inch(b)
    except Exception:
        pass
    return inch(0.5), inch(0.5), inch(0.5), inch(0.5)


def _hood_door_style(hood_obj):
    """The Face_Frame_Door_Style the hood's doors should build from (the
    hood's cabinet style's door style), or None -- door_builder falls
    back to its default construction fields."""
    style = _hood_style(hood_obj)
    if style is None:
        return None
    try:
        from ..face_frame.props_hb_face_frame import get_style_props
        ff = get_style_props()
        return next((d for d in ff.door_styles if d.name == style.door_style),
                    None)
    except Exception:
        return None


def _hood_door_info(hood_obj, opts):
    """door_builder construction info for this hood's doors: the
    resolved door style's fields with the hood's door-grid options
    (mid rail / mid stile counts) layered on top. A zero count leaves
    the style's own mid rail setting in charge."""
    info = door_builder.door_style_info(_hood_door_style(hood_obj))
    info['mid_rail_count'] = max(int(opts.get('door_mid_rails', 0)), 0)
    info['mid_stile_count'] = max(int(opts.get('door_mid_stiles', 0)), 0)
    info['mid_rail_fractions'] = door_builder.parse_grid_ratios(
        opts.get('door_grid_row_ratios'))
    info['mid_stile_fractions'] = door_builder.parse_grid_ratios(
        opts.get('door_grid_col_ratios'))
    return info


def _hood_door_mesh_spec(hood_obj, opts, width, height, thickness):
    """(info, build_door_mesh kwargs) for one hood door at a concrete
    size: _hood_door_info plus the door style's full construction the
    way cabinet fronts resolve it -- panel construction kinds, profile
    sweeps, mitered members, applied moldings, mullions, and arched
    shapes (via the style helpers resolve_member_section /
    effective_panel_fields / resolve_mesh_sections). The cabinet-level
    Door and Drawer Edge Profile rides in from the hood's assigned
    cabinet style. No resolvable style keeps the plain fallback fields
    with square sections. A door too small for the frame falls back to
    a slab (which still carries any edge profile)."""
    style = _hood_door_style(hood_obj)
    info = _hood_door_info(hood_obj, opts)
    kwargs = dict(shape=None)
    if style is not None:
        member_sec = style.resolve_member_section(thickness)
        pkind, p_th, p_inset = style.effective_panel_fields(thickness)
        info['panel_thickness'] = p_th
        info['panel_inset'] = p_inset
        if member_sec is not None:
            # Mitered: one continuous molding loop -- equal members at
            # the profile width, no mid grid.
            mw = max(u for u, v in member_sec)
            info.update(stile_width=mw, rail_width=mw,
                        left_stile_width=mw, right_stile_width=mw,
                        top_rail_width=mw, bottom_rail_width=mw,
                        mid_rail_count=0, mid_stile_count=0)
        else:
            # Arched shapes: widen the shaped rail(s) by the curve's
            # peak rise so the catalog rail width survives at the
            # crest; Twin forces one mid stile (one arch per lite).
            shape_k = None
            try:
                from ..face_frame import style_options
                shape_k = style_options.shape_kind(style.front_shape)
            except Exception:
                shape_k = None
            if shape_k is not None:
                msw = info.get('mid_stile_width') or info['stile_width']
                n_ms = max(int(info.get('mid_stile_count', 0) or 0), 0)
                if shape_k.get('twin') and n_ms == 0:
                    n_ms = 1
                    info['mid_stile_count'] = 1
                    info['mid_stile_width'] = msw
                lsw = (info.get('left_stile_width')
                       if info.get('left_stile_width') is not None
                       else info['stile_width'])
                rsw = (info.get('right_stile_width')
                       if info.get('right_stile_width') is not None
                       else info['stile_width'])
                cell_w = (width - lsw - rsw - n_ms * msw) / (n_ms + 1)
                if cell_w > inch(2):
                    rise = door_builder.shape_rise(shape_k['curve'], cell_w)
                    info['top_rail_width'] = (
                        info['top_rail_width']
                        if info.get('top_rail_width') is not None
                        else info['rail_width']) + rise
                    if shape_k.get('double'):
                        info['bottom_rail_width'] = (
                            info['bottom_rail_width']
                            if info.get('bottom_rail_width') is not None
                            else info['rail_width']) + rise
                    kwargs['shape'] = dict(shape_k, rise=rise)
        edge_name = None
        cs = _hood_style(hood_obj)
        if cs is not None:
            if getattr(cs, 'ss_edge_profile_is_custom', False):
                edge_name = cs.ss_edge_profile_custom.strip() or None
            else:
                _en = getattr(cs, 'ss_edge_profile', 'None')
                edge_name = None if _en == 'None' else _en
        kwargs.update(style.resolve_mesh_sections(
            thickness, info['panel_inset'], pkind, member_sec,
            edge_name=edge_name))
    min_w, min_h = door_builder.layout_min_size(info)
    if width <= min_w or height <= min_h:
        info = dict(info, door_type='SLAB')
    return info, kwargs


def _static_hood_door(hood_obj, name, width, height, location, opts,
                      rotation=None, mirror_z=None):
    """One hood door as a python-built static mesh part, carrying the
    door style's full construction like a cabinet front. The cutpart
    stays as the dimension carrier (Length / Width / Thickness inputs
    for readers) with its box hidden; the mesh replaces it 1:1 (it is
    authored in Mirror-Y front-cutpart local space, the same convention
    front_part uses). ``rotation`` reorients the door onto another
    plane (default: the front convention -- mesh height up, width to
    +X, front face toward the viewer); ``mirror_z`` sets the carrier's
    Mirror Z input for readers, matching the driven parts around it.
    Sized at build time -- the hood prompts rebuild on any size change,
    so it tracks the cage the same way the static angled / shiplap
    parts do."""
    mt = HOOD_MATERIAL
    info, kwargs = _hood_door_mesh_spec(hood_obj, opts, width, height, mt)
    p = _panel(hood_obj, name)
    p.obj.rotation_euler = ((0.0, math.radians(-90.0), math.radians(90.0))
                            if rotation is None else rotation)
    p.obj.location = location
    p.set_input("Length", height)
    p.set_input("Width", width)
    p.set_input("Thickness", mt)
    p.set_input("Mirror Y", True)
    if mirror_z is not None:
        p.set_input("Mirror Z", mirror_z)
    if p.obj.data.users > 1:
        p.obj.data = p.obj.data.copy()
    door_builder.build_door_mesh(p.obj.data, info, width, height, mt,
                                 **kwargs)
    p.obj['HB_HOOD_STATIC_DOOR'] = True
    for mod in p.obj.modifiers:
        if mod.type == 'NODES':
            mod.show_viewport = False
            mod.show_render = False
    return p


def _get_custom_opts(hood_obj):
    """The hood's CUSTOM-style options: stored values merged over defaults."""
    opts = dict(_CUSTOM_DEFAULTS)
    stored = hood_obj.get(HOOD_CUSTOM_PROP)
    if stored is not None:
        try:
            stored = stored.to_dict()
        except AttributeError:
            stored = dict(stored)
        for key in opts:
            if key in stored:
                opts[key] = stored[key]
        # Migrate the old single rail width to the split top / bottom pair.
        if 'panel_rail_width' in stored:
            for key in ('panel_top_rail_width', 'panel_bottom_rail_width'):
                if key not in stored:
                    opts[key] = stored['panel_rail_width']
    return opts


def _liner_shelf(hood_obj, cutout_w, cutout_d, front_ext=0.0,
                 cutout_offset=0.0, floor_z=0.0):
    """Bottom liner-mount shelf: one 3/4" board across the hood bottom, inset
    between the sides and behind the front, with the fan opening cut by a
    CPM_CUTOUT part modifier -- the same cut Add Cutout applies, so it shows
    in the 2D machining views and Remove Cutout works on it. ``front_ext``
    extends the board forward past the hood front to close the bottom of a
    projecting mantle; a NEGATIVE value insets its front edge (an angled
    hood's floor raised into the slope). ``floor_z`` raises the shelf off
    the hood bottom. The fan opening centers over the hood interior;
    ``cutout_offset`` then shifts it toward the front (+) or the wall (-),
    clamped so the opening stays on the board. The board and the cut are
    driven, so the opening stays put (at the entered size, clamped to the
    interior at build time) as the cage resizes. A zero cutout leaves the
    board solid."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    mt = HOOD_MATERIAL
    W = w.get_input('Dim X')
    D = w.get_input('Dim Y')
    H = w.get_input('Dim Z')
    ext = front_ext

    shelf = _panel(hood_obj, "Hood Liner Shelf")
    shelf.obj.location.x = mt
    shelf.obj.location.z = min(max(floor_z, 0.0), max(H - inch(2.0), 0.0))
    shelf.driver_location('y', '-dim_y + %f' % (mt - ext), [dim_y])
    shelf.driver_input("Length", 'dim_x - %f' % (2.0 * mt), [dim_x])
    shelf.driver_input("Width", 'dim_y - %f' % (mt - ext), [dim_y])
    shelf.set_input("Thickness", mt)
    shelf.set_input("Mirror Z", False)

    # Interior depth available to the opening (a front-inset board has
    # less; a mantle-extended board still keeps the opening over the
    # hood interior proper). The opening may use the full interior --
    # rim widths are the dealer's call (liners can need a 3/8" front
    # rim), so no extra reserve beyond the hood sides/front material.
    interior = (D - mt) + min(ext, 0.0)
    cw = max(0.0, min(cutout_w, W - 2.0 * mt))
    cd = max(0.0, min(cutout_d, interior))
    if cw <= 0.0 or cd <= 0.0:
        return
    slack = max((interior - cd) / 2.0, 0.0)
    off = max(-slack, min(cutout_offset, slack))
    cpm = shelf.add_part_modifier('CPM_CUTOUT', 'Cutout')
    cpm.mod.show_render = True
    # Cutout coords are in the part's Length/Width space (Length =
    # dim_x - 2mt, Width = dim_y - mt + ext): centered over the hood
    # interior, which starts ``ext`` up the extended board, then
    # shifted forward by ``off``.
    cpm.driver_input('X', '(dim_x - %f) * 0.5' % (2.0 * mt + cw), [dim_x])
    cpm.driver_input('End X', '(dim_x - %f) * 0.5' % (2.0 * mt - cw), [dim_x])
    cpm.driver_input('Y', '(dim_y - %f) * 0.5'
                     % (mt + cd - 2.0 * ext + 2.0 * off), [dim_y])
    cpm.driver_input('End Y', '(dim_y - %f) * 0.5'
                     % (mt - cd - 2.0 * ext + 2.0 * off), [dim_y])
    cpm.set_input('Route Depth', mt)


def _molding_wrap(hood_obj, prefix, tag, W, y_face, z0, z1, m_th):
    """One mitred molding band wrapping the hood between ``z0`` and
    ``z1``: a strip across the front face (``y_face``) and strips back
    along both hood sides to the wall, mitred at the front corners (45
    degrees in plan), standing ``m_th`` proud of the faces. Parts are
    named ``<prefix> F<tag>`` / ``L<tag>`` / ``R<tag>``. Static meshes
    sized at build time."""
    corners = {
        'fl_i': (0.0, y_face), 'fr_i': (W, y_face),
        'fl_o': (-m_th, y_face - m_th), 'fr_o': (W + m_th, y_face - m_th),
        'bl_i': (0.0, 0.0), 'br_i': (W, 0.0),
        'bl_o': (-m_th, 0.0), 'br_o': (W + m_th, 0.0),
    }

    def prism(name, keys):
        v = ([(corners[k][0], corners[k][1], z0) for k in keys]
             + [(corners[k][0], corners[k][1], z1) for k in keys])
        f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        _mesh_part(hood_obj, name, v, f)

    prism(prefix + " F" + tag, ('fl_i', 'fr_i', 'fr_o', 'fl_o'))
    prism(prefix + " L" + tag, ('bl_i', 'fl_i', 'fl_o', 'bl_o'))
    prism(prefix + " R" + tag, ('br_i', 'fr_i', 'fr_o', 'br_o'))


def _mantle_molding(hood_obj, W, y_face, band, m_w, m_th):
    """Mantle molding: strips of material wrapping the top and bottom of
    the mantle -- across the mantle front (``y_face``) and back along both
    hood sides to the wall, mitred at the front corners (45 degrees in
    plan), standing ``m_th`` proud of the faces. ``m_w`` is the strip
    height. Static meshes sized at build time."""
    m_w = min(max(m_w, inch(0.25)), band)
    m_th = max(m_th, inch(0.125))
    for tag, z0, z1 in (("B", 0.0, m_w), ("T", band - m_w, band)):
        _molding_wrap(hood_obj, "Hood Mantle Molding", tag,
                      W, y_face, z0, z1, m_th)


def _bottom_molding(hood_obj, opts, W, y_face):
    """Bottom molding: one strip of material wrapping the bottom of the
    hood -- across the front and back along both sides to the wall,
    mitred at the front corners. The standalone counterpart of the
    mantle molding's bottom band, for hoods without a mantle (e.g. a
    face-frame front whose bottom rail wants a wrapped trim strip)."""
    m_w = max(opts['bottom_molding_width'], inch(0.25))
    m_th = max(opts['bottom_molding_thickness'], inch(0.125))
    _molding_wrap(hood_obj, "Hood Bottom Molding", "",
                  W, y_face, 0.0, m_w, m_th)


def _front_face_frame(hood_obj, opts, band):
    """Face frame forming the straight hood front, treated like a
    cabinet face frame: full-height stiles, top / bottom rails, and mid
    stiles splitting the front into ``panel_count`` bays. The frame
    REPLACES the plain applied front -- its members occupy the same
    3/4" front layer. Each bay then carries its assigned front (see
    _BAY_FRONT_KINDS): an overlay door, an inset door, or just a 1/4"
    inset panel closing the opening. Frame members and inset panels are
    driven so they track the cage; bay DOORS are static python-built
    meshes (_static_hood_door) rebuilt with the hood so they carry the
    door style's full construction."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    sw = max(opts['panel_stile_width'], inch(0.5))
    trw = max(opts['panel_top_rail_width'], inch(0.5))
    brw = max(opts['panel_bottom_rail_width'], inch(0.5))
    n = max(int(opts['panel_count']), 1)
    mt = HOOD_MATERIAL

    def member(name):
        p = _panel(hood_obj, name)
        p.obj.rotation_euler.x = math.radians(90)
        p.driver_location('y', '-dim_y', [dim_y])
        p.set_input("Thickness", mt)
        p.set_input("Mirror Z", True)
        return p

    # Stiles run the full frame height at the outer edges.
    for name, x_expr in (("Hood Frame Stile L", None),
                         ("Hood Frame Stile R", 'dim_x - %f' % sw)):
        st = member(name)
        if x_expr is not None:
            st.driver_location('x', x_expr, [dim_x])
        st.obj.location.z = band
        st.set_input("Length", sw)
        st.driver_input("Width", 'dim_z - %f' % band, [dim_z])

    # Rails between the stiles.
    for name, width, z_static, z_expr in (
            ("Hood Frame Rail B", brw, band, None),
            ("Hood Frame Rail T", trw, None, 'dim_z - %f' % trw)):
        rl = member(name)
        rl.obj.location.x = sw
        if z_expr is None:
            rl.obj.location.z = z_static
        else:
            rl.driver_location('z', z_expr, [dim_z])
        rl.driver_input("Length", 'dim_x - %f' % (2.0 * sw), [dim_x])
        rl.set_input("Width", width)

    # Mid stiles between the rails, one less than the panel count. The
    # openings share the width left after all the stiles: opening =
    # (dim_x - stile stock) / n; mid stile j sits after opening j.
    stock = 2.0 * sw + (n - 1) * sw
    for j in range(1, n):
        ms = member("Hood Frame Mid Stile %d" % j)
        ms.driver_location('x', '(dim_x - %f) * %f + %f'
                           % (stock, j / n, sw + (j - 1) * sw), [dim_x])
        ms.obj.location.z = band + brw
        ms.set_input("Length", sw)
        ms.driver_input("Width", 'dim_z - %f' % (band + brw + trw), [dim_z])

    # Bay fronts. Opening j runs x [x0_j, x0_j + ow] with
    # ow = (dim_x - stock) / n and x0_j = (j+1)*sw + j*ow, and
    # z [band + brw, dim_z - trw]. Every dimension is linear in the
    # cage dims, handled as (coef, offset) pairs against dim_x (x /
    # width) and dim_z (z / height) so door_builder's layout rects
    # compose straight into driver expressions and everything keeps
    # tracking the cage.
    gap = inch(0.125)     # inset door reveal (solver DOOR_TO_FRAME_GAP)
    pt = inch(0.25)       # inset panel thickness (cabinet INSET_PANEL)
    ov_l, ov_r, ov_t, ov_b = _hood_door_overlays(hood_obj)
    frame_h = band + brw + trw    # z eaten by band + rails
    cage_w = w.get_input('Dim X')
    cage_h = w.get_input('Dim Z')
    cage_d = w.get_input('Dim Y')

    def front_part(name, xa, xb, za, zb, wa, wb, ha, hb, th, y_off,
                   role=None):
        """One bay-front cutpart from linear (coef, offset) dims, its
        thickness extending forward from the y plane at -dim_y + y_off.
        Cutpart Length = front HEIGHT, Width = front WIDTH, Mirror Y
        (the cabinet door convention): local X (Length) up, local -Y
        (Width) across to the right, thickness toward the viewer."""
        p = _panel(hood_obj, name)
        p.obj.rotation_euler = (0.0, math.radians(-90.0), math.radians(90.0))
        if role:
            p.obj['hb_part_role'] = role
        if xa:
            p.driver_location('x', 'dim_x * %f + %f' % (xa, xb), [dim_x])
        else:
            p.obj.location.x = xb
        if za:
            p.driver_location('z', 'dim_z * %f + %f' % (za, zb), [dim_z])
        else:
            p.obj.location.z = zb
        p.driver_location('y', '-dim_y + %f' % y_off, [dim_y])
        if ha:
            p.driver_input("Length", 'dim_z * %f + %f' % (ha, hb), [dim_z])
        else:
            p.set_input("Length", hb)
        if wa:
            p.driver_input("Width", 'dim_x * %f + %f' % (wa, wb), [dim_x])
        else:
            p.set_input("Width", wb)
        p.set_input("Thickness", th)
        p.set_input("Mirror Y", True)
        return p

    for j, kind in enumerate(_bay_front_list(opts, n)):
        # Opening rect: x = oxa*dim_x + oxb, width = owa*dim_x + owb,
        # height = dim_z + ohb, bottom at oz0.
        oxa, oxb = j / n, (j + 1) * sw - stock * (j / n)
        owa, owb = 1.0 / n, -stock / n
        oz0, ohb = band + brw, -frame_h
        if kind == 'PANEL':
            front_part("Hood Inset Panel %d" % (j + 1),
                       oxa, oxb, 0.0, oz0, owa, owb, 1.0, ohb,
                       pt, mt, role='INSET_PANEL')
            continue
        # Door rect off the opening: overlay grows it in front of the
        # frame; inset shrinks it by the reveal, flush with the frame.
        if kind == 'OVERLAY_DOOR':
            dxb, dwb = oxb - ov_l, owb + ov_l + ov_r
            dz0, dhb = oz0 - ov_b, ohb + ov_t + ov_b
            y_off = 0.0
        else:
            dxb, dwb = oxb + gap, owb - 2.0 * gap
            dz0, dhb = oz0 + gap, ohb - 2.0 * gap
            y_off = mt
        # One static python-built door per bay, carrying the door
        # style's full construction (profile sweeps, panel kinds,
        # mullions, arched shapes) exactly like a cabinet front. Sized
        # at the current cage dims; the prompts dialog rebuilds the
        # hood on any size change so the door tracks the cage the same
        # way the static angled / shiplap parts do. Too-small doors
        # fall back to a slab inside _hood_door_mesh_spec.
        _static_hood_door(
            hood_obj, "Hood Door %d" % (j + 1),
            owa * cage_w + dwb, cage_h + dhb,
            (oxa * cage_w + dxb, -cage_d + y_off, dz0),
            opts)


def _paneled_end(hood_obj, opts, at_right):
    """Paneled end REPLACING the plain hood side: a frame in the side's
    3/4" layer -- front + back stiles running full height, top / bottom
    rails between them -- filled by the end's assigned front (see
    _BAY_FRONT_KINDS): a 1/4" inset panel with its back flush with the
    frame's inner face (the cabinet paneled-end read), an overlay door
    proud of the side face, or an inset door flush in the frame layer.
    Uses the front frame's stile / rail widths. Driven so it tracks the
    cage. Returns False without building when the side is too small for
    the frame (caller keeps the plain side)."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    sw = max(opts['panel_stile_width'], inch(0.5))
    trw = max(opts['panel_top_rail_width'], inch(0.5))
    brw = max(opts['panel_bottom_rail_width'], inch(0.5))
    mt = HOOD_MATERIAL
    pt = inch(0.25)
    if (w.get_input('Dim Y') - mt - 2.0 * sw <= 0.0
            or w.get_input('Dim Z') - brw - trw <= 0.0):
        return False
    tag = "R" if at_right else "L"

    def member(name):
        p = _panel(hood_obj, "Hood End %s %s" % (tag, name))
        p.obj.rotation_euler.y = math.radians(-90)
        if at_right:
            p.driver_location('x', 'dim_x', [dim_x])
        p.set_input("Thickness", mt)
        p.set_input("Mirror Y", True)
        p.set_input("Mirror Z", not at_right)
        return p

    # Stiles run full height at the side's front edge (behind the front
    # layer) and at the wall.
    fs = member("Front Stile")
    fs.driver_location('y', '-dim_y + %f' % (mt + sw), [dim_y])
    fs.driver_input("Length", 'dim_z', [dim_z])
    fs.set_input("Width", sw)
    bs = member("Back Stile")
    bs.driver_input("Length", 'dim_z', [dim_z])
    bs.set_input("Width", sw)

    # Rails between the stiles at the top and bottom.
    for name, width, z_static, z_expr in (
            ("Bottom Rail", brw, 0.0, None),
            ("Top Rail", trw, None, 'dim_z - %f' % trw)):
        rl = member(name)
        rl.obj.location.y = -sw
        if z_expr is None:
            rl.obj.location.z = z_static
        else:
            rl.driver_location('z', z_expr, [dim_z])
        rl.set_input("Length", width)
        rl.driver_input("Width", 'dim_y - %f' % (mt + 2.0 * sw), [dim_y])

    kind = _end_front_kind(opts, at_right)
    if kind == 'PANEL':
        # 1/4" inset panel closing the opening, back face flush with the
        # frame's inner face.
        pnl = _panel(hood_obj, "Hood End %s Panel" % tag)
        pnl.obj.rotation_euler.y = math.radians(-90)
        if at_right:
            pnl.driver_location('x', 'dim_x - %f' % (mt - pt), [dim_x])
        else:
            pnl.obj.location.x = mt - pt
        pnl.obj.location.y = -sw
        pnl.obj.location.z = brw
        pnl.obj['hb_part_role'] = 'INSET_PANEL'
        pnl.driver_input("Length", 'dim_z - %f' % (brw + trw), [dim_z])
        pnl.driver_input("Width", 'dim_y - %f' % (mt + 2.0 * sw), [dim_y])
        pnl.set_input("Thickness", pt)
        pnl.set_input("Mirror Y", True)
        pnl.set_input("Mirror Z", not at_right)
        return True

    # Door filling the end frame's opening -- ONE static python-built
    # mesh (_static_hood_door) laid on the side plane, carrying the
    # door style's full construction like the front bay doors. Width
    # runs front-to-back, height up; each side is a proper rotation of
    # the door (its left edge at that side's viewer's left -- the wall
    # on the left end, the front on the right end), not a mirrored
    # mesh. Overlay sits proud of the side face; inset sits in the
    # frame layer flush with it. The opening is y [-dim_y + mt + sw,
    # -sw], z [brw, dim_z - trw]. Sized at the current cage dims; the
    # prompts rebuild the hood on any size change. Too-small doors
    # fall back to a slab inside _hood_door_mesh_spec.
    gap = inch(0.125)
    ov_l, ov_r, ov_t, ov_b = _hood_door_overlays(hood_obj)
    if kind == 'OVERLAY_DOOR':
        # The wall side is the door's left edge on the left end and
        # its right edge on the right end.
        oy = -sw + (ov_r if at_right else ov_l)   # wall-side edge
        wb = -(mt + 2.0 * sw) + ov_l + ov_r       # width = dim_y + wb
        z0 = brw - ov_b
        hb = -(brw + trw) + ov_t + ov_b           # height = dim_z + hb
        d0_door = -mt                             # proud of the side face
    else:
        oy = -sw - gap
        wb = -(mt + 2.0 * sw) - 2.0 * gap
        z0 = brw + gap
        hb = -(brw + trw) - 2.0 * gap
        d0_door = 0.0                             # in the side layer

    w_d = w.get_input('Dim Y') + wb
    h_d = w.get_input('Dim Z') + hb
    if at_right:
        rot = (0.0, math.radians(-90.0), math.radians(180.0))
        loc = (w.get_input('Dim X') - d0_door - mt, oy - w_d, z0)
    else:
        rot = (0.0, math.radians(-90.0), 0.0)
        loc = (d0_door + mt, oy, z0)
    _static_hood_door(hood_obj, "Hood End %s Door" % tag, w_d, h_d, loc,
                      opts, rotation=rot, mirror_z=not at_right)
    return True


def _angled_paneled_end(hood_obj, opts, prof, at_right, setback):
    """Paneled end for the ANGLED section of a custom hood side: the
    same frame + 1/4" inset panel as _paneled_end, as static meshes
    following the side plane's taper, with the front stile parallel to
    the sloped front edge. It spans the slope only -- the straight
    mantle zone below and the top_height box above keep their plain box
    sides (separate boxes, like the mantle) -- so no member breaks
    across a profile kink. The panel's back face is flush with the
    side's inner face. Returns False without building when the sloped
    section is too small for the frame (caller keeps the plain angled
    side)."""
    sw = max(opts['panel_stile_width'], inch(0.5))
    trw = max(opts['panel_top_rail_width'], inch(0.5))
    brw = max(opts['panel_bottom_rail_width'], inch(0.5))
    mt = HOOD_MATERIAL
    pt = inch(0.25)
    W, D, td = prof.W, prof.D, prof.td
    z0, z1 = prof.z0b, prof.zb
    if (min(D, td) - setback - 2.0 * sw <= 0.0
            or (z1 - z0) - brw - trw <= inch(1.0)):
        return False

    def front_edge(z):
        # The angled side's front edge, one slope-setback behind the face.
        return prof.y_at(z) + setback

    def strip(name, y0f, y1f, za, zc, band=(0.0, None)):
        """Prism in the side plane; ``band`` is the depth slice in x,
        measured inward from the side's outer face (negative = proud;
        None = one material thickness)."""
        d0, d1 = band[0], mt if band[1] is None else band[1]

        def ring(z):
            xin = prof.x_in_at(z)
            xa, xb = xin + d0, xin + d1
            if at_right:
                xa, xb = W - xb, W - xa
            y0, y1 = y0f(z), y1f(z)
            return [(xa, y0, z), (xb, y0, z), (xb, y1, z), (xa, y1, z)]

        r0, r1 = ring(za), ring(zc)
        v = [r0[0], r0[1], r1[1], r1[0], r0[3], r0[2], r1[2], r1[3]]
        f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        _mesh_part(hood_obj, name, v, f)

    base = "Hood End %s " % ("R" if at_right else "L")

    def inner0(z):
        return front_edge(z) + sw

    def inner1(z):
        return -sw

    strip(base + "Back Stile", lambda z: -sw, lambda z: 0.0, z0, z1)
    strip(base + "Front Stile", front_edge, inner0, z0, z1)
    strip(base + "Bottom Rail", inner0, inner1, z0, z0 + brw)
    strip(base + "Top Rail", inner0, inner1, z1 - trw, z1)

    kind = _end_front_kind(opts, at_right)
    if kind == 'PANEL':
        strip(base + "Panel", inner0, inner1, z0 + brw, z1 - trw,
              band=(mt - pt, mt))
        return True

    # Door filling the end frame's opening, a 5-piece assembly from
    # door_builder laid on the (possibly tilted) side plane: width runs
    # front-to-back following the sloped front edge, height straight up.
    # Overlay sits proud of the side face; inset sits in the frame layer.
    # Stays plain prisms (unlike _paneled_end / the untapered sloped bay
    # doors): the front edge follows the slope so the door width varies
    # with z -- a trapezoid build_door_mesh has no mapping for.
    gap = inch(0.125)
    ov_l, ov_r, ov_t, ov_b = _hood_door_overlays(hood_obj)
    if kind == 'OVERLAY_DOOR':
        adj_f, adj_b = -ov_l, ov_r
        dz0, dz1 = max(z0 + brw - ov_b, z0), min(z1 - trw + ov_t, z1)
        d_front = -mt
    else:
        adj_f, adj_b = gap, -gap
        dz0, dz1 = z0 + brw + gap, z1 - trw - gap
        d_front = 0.0
    h_d = dz1 - dz0

    def door_front(z, adj_f=adj_f):
        return inner0(z) + adj_f

    def door_w(z, adj_f=adj_f, adj_b=adj_b):
        return (inner1(z) + adj_b) - (inner0(z) + adj_f)

    info = _hood_door_info(hood_obj, opts)
    min_w, min_h = door_builder.layout_min_size(info)
    if min(door_w(dz0), door_w(dz1)) <= min_w or h_d <= min_h:
        info = dict(info, door_type='SLAB')
    for part in door_builder.door_layout(info):
        cx, ox = part['x']
        cw, ow = part['w']
        cz, oz = part['z']
        ch, oh = part['h']
        name = (base + "Door" if part['key'] == 'slab'
                else base + "Door " + part['name'])
        th = mt if part['thickness'] is None else part['thickness']
        d0 = d_front if part['thickness'] is None \
            else d_front + part['y_inset']
        strip(name,
              lambda z, cx=cx, ox=ox: door_front(z) + cx * door_w(z) + ox,
              lambda z, cx=cx, cw=cw, ox=ox, ow=ow:
                  door_front(z) + (cx + cw) * door_w(z) + ox + ow,
              dz0 + cz * h_d + oz, dz0 + (cz + ch) * h_d + oz + oh,
              band=(d0, d0 + th))
    return True


def _custom_sloped_frame(hood_obj, opts, prof, fz):
    """Static version of _front_face_frame following the sloped / tapered
    custom front: stiles hug the slanted edges, rails run across the top
    and bottom of the face, mid stiles split the field into panel_count
    openings. The frame REPLACES the plain angled front -- members fill
    the 3/4" front layer inward from the face, follow the straight top
    section, and kink (mitred face) at the break; the caller builds the
    recessed panel behind the openings. Returns True when the frame was
    built, False when the face is too small (the caller keeps the plain
    front so the hood stays closed)."""
    sw = max(opts['panel_stile_width'], inch(0.5))
    trw = max(opts['panel_top_rail_width'], inch(0.5))
    brw = max(opts['panel_bottom_rail_width'], inch(0.5))
    n = max(int(opts['panel_count']), 1)
    mt = HOOD_MATERIAL
    W = prof.W
    # The frame lives on the sloped face only (fz..zb), so members use
    # the slope normal throughout -- square ends, no mitred kinks (the
    # straight top_height section is a separate plain box above it).
    n_y = -(prof.span or 1.0) / prof.ln
    n_z = prof.dy / prof.ln

    def prism(name, x0f, x1f, z0, z1):
        for za, zc in prof.split(z0, z1):
            def ring(z):
                y = prof.y_at(z)
                return [(x0f(z), y, z), (x1f(z), y, z),
                        (x1f(z), y - n_y * mt, z - n_z * mt),
                        (x0f(z), y - n_y * mt, z - n_z * mt)]
            r0, r1 = ring(za), ring(zc)
            v = [r0[0], r0[1], r1[1], r1[0], r0[3], r0[2], r1[2], r1[3]]
            f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
            _mesh_part(hood_obj, name, v, f)

    # The frame covers the angled section only -- the straight top_height
    # stack above the break stays plain. Rail widths are measured along
    # the face, so lay the frame out in face arc length and map back to
    # heights.
    s0 = prof.s_at(fz)
    s1 = prof.s_at(prof.zb)
    if (s1 - s0) <= brw + trw or (W - 2.0 * prof.side_in) <= (n + 1) * sw:
        return False
    z0, z1 = fz, prof.zb
    zbr = prof.z_at(s0 + brw)         # top of the bottom rail
    ztr = prof.z_at(s1 - trw)         # bottom of the top rail
    prism("Hood Frame Stile L",
          lambda z: prof.x_in_at(z), lambda z: prof.x_in_at(z) + sw, z0, z1)
    prism("Hood Frame Stile R",
          lambda z: W - prof.x_in_at(z) - sw, lambda z: W - prof.x_in_at(z),
          z0, z1)
    prism("Hood Frame Rail B",
          lambda z: prof.x_in_at(z) + sw, lambda z: W - prof.x_in_at(z) - sw,
          z0, zbr)
    prism("Hood Frame Rail T",
          lambda z: prof.x_in_at(z) + sw, lambda z: W - prof.x_in_at(z) - sw,
          ztr, z1)
    for j in range(1, n):
        def x0f(z, j=j):
            avail = (W - 2.0 * prof.x_in_at(z) - 2.0 * sw - (n - 1) * sw)
            return prof.x_in_at(z) + sw + j * (avail / n) + (j - 1) * sw
        prism("Hood Frame Mid Stile %d" % j,
              x0f, lambda z, x0f=x0f: x0f(z) + sw, zbr, ztr)
    return True


class _FrontProfile:
    """Piecewise custom-hood front / side profile: straight (full depth /
    width) from the base up to ``z0b`` (the mantle-height bottom section),
    sloped from there to ``zb`` (where the top depth / width are reached),
    then straight to the top (the ``top_height`` section; zb == H when
    there is none). Maps a height to the front plane (y_at), the side
    taper (x_in_at), face arc length (s_at / z_at -- for laying out boards
    along the wrapped surface), and the outward proud offset, mitred at
    the straight / slope breaks (off_at)."""

    def __init__(self, W, D, H, td=None, side_in=0.0, top_h=0.0,
                 bottom_h=0.0):
        self.W, self.D, self.H = W, D, H
        self.td = D if td is None else td
        self.side_in = side_in
        self.z0b = min(max(bottom_h, 0.0), max(H - inch(1.0), 0.0))
        self.zb = min(max(H - max(top_h, 0.0), self.z0b + inch(1.0)), H)
        self.dy = self.D - self.td
        self.span = self.zb - self.z0b               # sloped z range
        self.ln = math.hypot(self.dy, self.span) or 1.0  # sloped-face length
        self.S = self.z0b + self.ln + (H - self.zb)  # base-to-top face length

    def _t(self, z):
        """Slope fraction at z (0 below the slope, 1 above it)."""
        return (min(max(z, self.z0b), self.zb) - self.z0b) / (self.span or 1.0)

    def y_at(self, z):
        return -self.D + self.dy * self._t(z)

    def x_in_at(self, z):
        return self.side_in * self._t(z)

    def s_at(self, z):
        if z <= self.z0b:
            return z
        if z <= self.zb:
            return self.z0b + (z - self.z0b) * self.ln / (self.span or 1.0)
        return self.z0b + self.ln + (z - self.zb)

    def z_at(self, s):
        if s <= self.z0b:
            return s
        if s <= self.z0b + self.ln:
            return self.z0b + (s - self.z0b) * (self.span or 1.0) / self.ln
        return min(self.zb + (s - self.z0b - self.ln), self.H)

    def off_at(self, z):
        """Outward offset (y, z) per unit of proud at height z; on the
        straight / slope breaks this is the exact miter direction."""
        n1 = (-(self.span or 1.0) / self.ln, self.dy / self.ln)
        vert = (-1.0, 0.0)

        def miter(na, nb):
            denom = 1.0 + (na[0] * nb[0] + na[1] * nb[1])
            return ((na[0] + nb[0]) / denom, (na[1] + nb[1]) / denom)

        if self.z0b > 1e-9 and abs(z - self.z0b) <= 1e-9:
            return miter(vert, n1)
        if self.zb < self.H - 1e-9 and abs(z - self.zb) <= 1e-9:
            return miter(n1, vert)
        if z < self.z0b or z > self.zb:
            return vert
        return n1

    def split(self, z0, z1):
        """(z0, z1) spans split at the straight / slope breaks when
        crossed, so boards spanning one kink instead of cutting the
        corner."""
        spans = []
        cur = z0
        for zc in (self.z0b, self.zb):
            if cur < zc - 1e-6 and z1 > zc + 1e-6:
                spans.append((cur, zc))
                cur = zc
        spans.append((cur, z1))
        return spans


def _wrap_shiplap(hood_obj, prof, fz=0.0, board=None):
    """Shiplap wrapping the hood box: full ``board``-width courses (6"
    when not given) standing 1/2" proud of the front and side faces,
    mitred at the front corners (45 degrees in plan), with a 1/8" reveal
    between courses. Courses lay bottom-up along the face (arc length),
    following ``prof``'s slope / taper and its straight top section; a
    course crossing the break is built as two boards, and the last
    course trims down to whatever remains at the top. Static meshes --
    rebuilt by the command / prompts."""
    board = inch(6.0) if board is None else max(board, inch(1.0))
    reveal = inch(0.125)
    proud = inch(0.5)
    W = prof.W

    def plan(z):
        """Inner + outer wrap corners at height z (plan coordinates):
        f/b = front/back (wall), l/r = left/right, i/o = inner/outer."""
        xi = prof.x_in_at(z)
        yf = prof.y_at(z)
        return {
            'fl_i': (xi, yf), 'fr_i': (W - xi, yf),
            'fl_o': (xi - proud, yf - proud),
            'fr_o': (W - xi + proud, yf - proud),
            'bl_i': (xi, 0.0), 'br_i': (W - xi, 0.0),
            'bl_o': (xi - proud, 0.0), 'br_o': (W - xi + proud, 0.0),
        }

    def prism(name, keys, z0, z1):
        for za, zc in prof.split(z0, z1):
            p0, p1 = plan(za), plan(zc)
            v = ([(p0[k][0], p0[k][1], za) for k in keys]
                 + [(p1[k][0], p1[k][1], zc) for k in keys])
            f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
            _mesh_part(hood_obj, name, v, f)

    s0 = prof.s_at(fz)
    span_s = prof.S - s0
    if span_s <= 0.0:
        return
    # Full-width courses from the bottom up (board + reveal pitch); the
    # last course is whatever remains at the top, trimmed down.
    pitch = board + reveal
    n_full = int(span_s // pitch)
    courses = [(s0 + i * pitch, s0 + i * pitch + board)
               for i in range(n_full)]
    rem_a = s0 + n_full * pitch
    if prof.S - rem_a > inch(0.25):
        courses.append((rem_a, prof.S))
    elif not courses:
        courses.append((s0, prof.S))
    for i, (sa, sb) in enumerate(courses):
        z0, z1 = prof.z_at(sa), prof.z_at(min(sb, prof.S))
        if z1 <= z0:
            continue
        # One course = front + left + right boards sharing the 45-degree
        # miter line from each inner front corner to its outer corner.
        prism("Hood Shiplap F%d" % i, ('fl_i', 'fr_i', 'fr_o', 'fl_o'), z0, z1)
        prism("Hood Shiplap L%d" % i, ('bl_i', 'fl_i', 'fl_o', 'bl_o'), z0, z1)
        prism("Hood Shiplap R%d" % i, ('br_i', 'fr_i', 'fr_o', 'br_o'), z0, z1)


def _sloped_bay_fronts(hood_obj, opts, prof, fz):
    """Bay fronts filling the sloped face frame's openings: the same
    per-bay choices as the straight hood (overlay door / inset door /
    1/4" inset panel), lying in (inset) or on (overlay) the sloped
    front plane. On an UNTAPERED slope (no angled sides) each door is
    a flat rectangle in the face plane, so it builds as one static
    python-built mesh (_static_hood_door) tilted onto the slope,
    carrying the door style's full construction like the straight
    hood's bay doors. On a TAPERED hood the door width varies up the
    slope -- a trapezoid build_door_mesh has no mapping for -- so
    doors stay 5-piece assemblies of static prisms from door_layout:
    height runs up the slope in face arc length, width follows the
    side taper like the frame members. Uses the same stile / rail
    layout math as _custom_sloped_frame (which must have built)."""
    sw = max(opts['panel_stile_width'], inch(0.5))
    trw = max(opts['panel_top_rail_width'], inch(0.5))
    brw = max(opts['panel_bottom_rail_width'], inch(0.5))
    n = max(int(opts['panel_count']), 1)
    mt = HOOD_MATERIAL
    pt = inch(0.25)
    gap = inch(0.125)
    W = prof.W
    n_y = -(prof.span or 1.0) / prof.ln
    n_z = prof.dy / prof.ln
    ov_l, ov_r, ov_t, ov_b = _hood_door_overlays(hood_obj)
    ds_info = _hood_door_info(hood_obj, opts)

    s_lo = prof.s_at(fz)               # face span of the framed area
    s_hi = prof.s_at(prof.zb)
    s0 = s_lo + brw                    # opening span, between the rails
    s1 = s_hi - trw

    def prism(name, x0f, x1f, sa, sb, d0, d1):
        """Face-plane prism: x edges x0f(z) / x1f(z), face span sa..sb
        (arc length up the slope), depth band d0..d1 inward along the
        slope normal from the face plane (negative = proud)."""
        za, zc = prof.z_at(sa), prof.z_at(sb)

        def ring(z):
            y = prof.y_at(z)
            pts = []
            for d in (d0, d1):
                yd, zd = y - n_y * d, z - n_z * d
                pts.append(((x0f(z), yd, zd), (x1f(z), yd, zd)))
            (a0, b0), (a1, b1) = pts
            return [a0, b0, b1, a1]

        r0, r1 = ring(za), ring(zc)
        v = [r0[0], r0[1], r1[1], r1[0], r0[3], r0[2], r1[2], r1[3]]
        f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        _mesh_part(hood_obj, name, v, f)

    def opening_w(z):
        return (W - 2.0 * prof.x_in_at(z) - (n + 1) * sw) / n

    def opening_left(z, j):
        return prof.x_in_at(z) + sw + j * (opening_w(z) + sw)

    for j, kind in enumerate(_bay_front_list(opts, n)):
        if kind == 'PANEL':
            # Back face flush with the frame's inner face, like the
            # straight hood / cabinet INSET_PANEL convention.
            prism("Hood Inset Panel %d" % (j + 1),
                  lambda z, j=j: opening_left(z, j),
                  lambda z, j=j: opening_left(z, j) + opening_w(z),
                  s0, s1, mt - pt, mt)
            continue
        if kind == 'OVERLAY_DOOR':
            dl, dw = -ov_l, ov_l + ov_r
            ds0 = max(s0 - ov_b, s_lo)
            ds1 = min(s1 + ov_t, s_hi)
            d_front = -mt              # proud of the frame face
        else:
            dl, dw = gap, -2.0 * gap
            ds0, ds1 = s0 + gap, s1 - gap
            d_front = 0.0              # in the frame layer, flush face
        h_s = ds1 - ds0

        if prof.side_in <= 1e-9:
            # Untapered slope: one static styled door mesh, rotated
            # from the front-door convention onto the face plane
            # (tilted about X by the slope angle). Its origin sits one
            # door thickness behind the door's front face, measured
            # along the slope normal from the face-plane bottom-left
            # corner of the opening rect.
            z_a = prof.z_at(ds0)
            w_d = opening_w(z_a) + dw
            d_back = d_front + mt
            tilt = math.atan2(prof.dy, prof.span or 1.0)
            rot = (Matrix.Rotation(-tilt, 3, 'X')
                   @ Euler((0.0, math.radians(-90.0),
                            math.radians(90.0))).to_matrix())
            _static_hood_door(
                hood_obj, "Hood Door %d" % (j + 1), w_d, h_s,
                (opening_left(z_a, j) + dl,
                 prof.y_at(z_a) - n_y * d_back,
                 z_a - n_z * d_back),
                opts, rotation=rot.to_euler())
            continue

        def door_left(z, j=j, dl=dl):
            return opening_left(z, j) + dl

        def door_w(z, dw=dw):
            return opening_w(z) + dw

        # Too small for the style's frame (at the door's narrowest) -> slab.
        info = ds_info
        min_w, min_h = door_builder.layout_min_size(info)
        if (min(door_w(prof.z_at(ds0)), door_w(prof.z_at(ds1))) <= min_w
                or h_s <= min_h):
            info = dict(info, door_type='SLAB')
        for part in door_builder.door_layout(info):
            cx, ox = part['x']
            cw, ow = part['w']
            cz, oz = part['z']
            ch, oh = part['h']
            name = ("Hood Door %d" % (j + 1) if part['key'] == 'slab'
                    else "Hood Door %d %s" % (j + 1, part['name']))
            th = mt if part['thickness'] is None else part['thickness']
            d0 = d_front if part['thickness'] is None \
                else d_front + part['y_inset']
            prism(name,
                  lambda z, cx=cx, ox=ox: door_left(z) + cx * door_w(z) + ox,
                  lambda z, cx=cx, cw=cw, ox=ox, ow=ow:
                      door_left(z) + (cx + cw) * door_w(z) + ox + ow,
                  ds0 + cz * h_s + oz, ds0 + (cz + ch) * h_s + oz + oh,
                  d0, d0 + th)


def _build_custom_angled(hood_obj, opts):
    """Custom hood with an angled front and/or tapered sides: a general
    frustum -- full W x D at the base narrowing to top_width / top_depth --
    optionally topped by a straight ``top_height`` section (chimney-style
    stack) built as additional parts. Custom meshes like _build_angled
    (static; the prompts rebuild on every change)."""
    w = _HoodWrap(hood_obj)
    W = w.get_input('Dim X')
    D = w.get_input('Dim Y')
    H = max(w.get_input('Dim Z'), inch(1.0))
    mt = HOOD_MATERIAL
    band = opts['mantle_height'] if opts['include_mantle'] else 0.0
    td = min(max(opts['top_depth'], inch(1.0)), D) if opts['angle_front'] else D
    tw = min(max(opts['top_width'], 2.0 * mt + inch(2.0)), W) \
        if opts['angle_sides'] else W
    side_in = (W - tw) / 2.0
    fz = band
    # Straight bottom section (the mantle zone -- the angle starts at the
    # mantle height) and straight top section (top_height).
    top_h = min(max(opts['top_height'], 0.0), max(H - fz - inch(1.0), 0.0))
    prof = _FrontProfile(W, D, H, td, side_in, top_h, bottom_h=fz)
    zb0, zb = prof.z0b, prof.zb
    # A projecting mantle assembly supplies the mantle zone's front and
    # sides itself, so the straight lower front / side parts are skipped.
    mantle_dep = (opts['mantle_depth']
                  if band > 0.0 and opts['mantle_depth'] > inch(0.125) else 0.0)
    has_mantle_assy = mantle_dep > 0.0

    # The front parts are 3/4" stock applied over the sides: the sides set
    # back by the front's thickness and butt its inner face. On the slope
    # the perpendicular 3/4" reads as a larger horizontal setback.
    setback = mt * prof.ln / (prof.span or 1.0)

    # A paneled face frame replaces the plain angled front: the frame
    # fills the front layer and a recessed panel closes the openings
    # behind it. When the face is too small for the frame it stays plain.
    framed_front = (opts['include_front_panel']
                    and _custom_sloped_frame(hood_obj, opts, prof, fz))

    def side(x_bot, x_top, angled=True):
        if zb0 > 0.0 and not has_mantle_assy:
            # Straight lower side through the mantle zone (a projecting
            # mantle's full-depth sides replace it).
            _mesh_box(hood_obj, "Hood Side Lower",
                      x_bot, x_bot + mt, -D + mt, 0.0, 0.0, zb0)
        if angled:
            # Angled section of the side (bottom break to top break).
            v = [(x_bot, 0.0, zb0), (x_bot, -D + setback, zb0),
                 (x_top, -td + setback, zb), (x_top, 0.0, zb),
                 (x_bot + mt, 0.0, zb0), (x_bot + mt, -D + setback, zb0),
                 (x_top + mt, -td + setback, zb), (x_top + mt, 0.0, zb)]
            f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                 (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
            _mesh_part(hood_obj, "Hood Side", v, f)
        if zb < H:
            # Straight upper side continuing to the top.
            _mesh_box(hood_obj, "Hood Side Upper",
                      x_top, x_top + mt, -td + mt, 0.0, zb, H)

    # Paneled ends replace the sides' ANGLED section only; the straight
    # mantle-zone / top boxes stay plain (side() still builds them). A
    # slope too small for its frame falls back to the plain side.
    left_pe = (bool(opts['left_end_panel'])
               and _angled_paneled_end(hood_obj, opts, prof, False, setback))
    right_pe = (bool(opts['right_end_panel'])
                and _angled_paneled_end(hood_obj, opts, prof, True, setback))
    side(0.0, side_in, angled=not left_pe)
    side(W - mt, W - side_in - mt, angled=not right_pe)
    # Applied front, 3/4" thick, full width, covering the sides' front
    # edges. A straight lower front spans the mantle zone, the angled
    # front runs between the breaks, and a straight upper front continues
    # to the top.
    if zb0 > 0.0 and not has_mantle_assy:
        _mesh_box(hood_obj, "Hood Front Lower", 0.0, W, -D, -D + mt,
                  0.0, zb0)
    if framed_front:
        # Per-bay fronts fill the frame's openings (doors / inset
        # panels), the same choices as the straight hood.
        _sloped_bay_fronts(hood_obj, opts, prof, fz)
    else:
        sy = prof.span * mt / prof.ln     # outer face -> inner face shift
        sz = -prof.dy * mt / prof.ln
        outer = [(prof.x_in_at(fz), prof.y_at(fz), fz),
                 (W - prof.x_in_at(fz), prof.y_at(fz), fz),
                 (W - side_in, -td, zb), (side_in, -td, zb)]
        inner = [(x, y + sy, z + sz) for (x, y, z) in outer]
        _mesh_part(hood_obj, "Hood Front", outer + inner,
                   [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                    (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    if zb < H:
        _mesh_box(hood_obj, "Hood Front Upper", side_in, W - side_in,
                  -td, -td + mt, zb, H)
    _mesh_part(hood_obj, "Hood Top",
               [(mt + side_in, -td + mt, H), (W - mt - side_in, -td + mt, H),
                (W - mt - side_in, 0.0, H), (mt + side_in, 0.0, H)],
               [(0, 1, 2, 3)])
    if has_mantle_assy:
        # Mantle assembly: front board, full-depth sides running back to
        # the wall (these ARE the mantle zone's front / sides), and the
        # projection cap. Near-zero depth skips it -- the straight lower
        # front / sides are the flush mantle, mirroring the top section.
        y_mf = -D - mantle_dep
        _mesh_box(hood_obj, "Hood Mantle Front", 0.0, W,
                  y_mf, y_mf + mt, 0.0, band)
        for x0, x1 in ((0.0, mt), (W - mt, W)):
            _mesh_box(hood_obj, "Hood Mantle Side", x0, x1,
                      y_mf + mt, 0.0, 0.0, band)
        if mantle_dep - mt > 0.0 and band - mt > 0.0:
            _mesh_box(hood_obj, "Hood Mantle Top", mt, W - mt,
                      y_mf + mt, -D, band - mt, band)
    if band > 0.0 and opts['include_mantle_molding']:
        _mantle_molding(hood_obj, W, -D - mantle_dep, band,
                        opts['mantle_molding_width'],
                        opts['mantle_molding_thickness'])
    if opts['include_bottom_molding']:
        # The base of an angled hood is full W x D, so the wrap uses the
        # same corner geometry as the straight hood (the mantle front
        # when one projects, else the hood front plane).
        _bottom_molding(hood_obj, opts, W, -D - mantle_dep)
    # Shelf extends forward under a projecting mantle to close its
    # bottom (only while it sits at the bottom); a floor raised into the
    # slope insets its front edge to the interior depth at that height.
    floor_z = min(max(opts['floor_height'], 0.0), max(H - inch(2.0), 0.0))
    z_top = min(floor_z + mt, H)
    shrink = max(D + prof.y_at(z_top), 0.0)
    if shrink > 0.0:
        shrink += setback
    _liner_shelf(hood_obj, opts['fan_cutout_width'], opts['fan_cutout_depth'],
                 front_ext=(mantle_dep if floor_z <= 0.0 else 0.0) - shrink,
                 cutout_offset=opts['fan_cutout_offset'], floor_z=floor_z)
    if opts['include_shiplap']:
        _wrap_shiplap(hood_obj, prof, fz=fz,
                      board=opts['shiplap_board_width'])


def _build_custom(hood_obj):
    """Custom hood from the per-hood options (HOOD_CUSTOM_PROP). Straight
    hoods use the driven box carcass so they keep resizing with the cage;
    any angle switches to the static mesh path."""
    opts = _get_custom_opts(hood_obj)
    if opts['angle_front'] or opts['angle_sides']:
        _build_custom_angled(hood_obj, opts)
        return
    band = opts['mantle_height'] if opts['include_mantle'] else 0.0
    # Paneled ends replace the plain sides; build them first so an
    # end too small for its frame can fall back to the plain side.
    left_pe = bool(opts['left_end_panel']) and _paneled_end(hood_obj, opts, False)
    right_pe = bool(opts['right_end_panel']) and _paneled_end(hood_obj, opts, True)
    # band thickness builds as mt + band_proj, so proj = depth - mt gives the
    # mantle its full front-to-back depth off the sides' front edges.
    # A paneled face frame replaces the plain front outright.
    _build_hood_box(hood_obj, bottom_band=band,
                    band_proj=max(opts['mantle_depth'] - HOOD_MATERIAL, 0.0)
                    if band > 0.0 else 0.0,
                    include_front=not opts['include_front_panel'],
                    include_left_side=not left_pe,
                    include_right_side=not right_pe)
    if band > 0.0 and opts['include_mantle_molding']:
        w2 = _HoodWrap(hood_obj)
        W = w2.get_input('Dim X')
        D = w2.get_input('Dim Y')
        # The mantle front face: sides' front edge minus the mantle depth
        # (flush with the applied front when the depth is 3/4" or less).
        y_face = -D + HOOD_MATERIAL - max(opts['mantle_depth'], HOOD_MATERIAL)
        _mantle_molding(hood_obj, W, y_face, band,
                        opts['mantle_molding_width'],
                        opts['mantle_molding_thickness'])
    if opts['include_bottom_molding']:
        w2 = _HoodWrap(hood_obj)
        W = w2.get_input('Dim X')
        D = w2.get_input('Dim Y')
        # Wraps the mantle face when a mantle is built, else the applied
        # front / face-frame plane.
        y_face = (-D + HOOD_MATERIAL - max(opts['mantle_depth'], HOOD_MATERIAL)
                  if band > 0.0 else -D)
        _bottom_molding(hood_obj, opts, W, y_face)
    if opts['include_shiplap']:
        _add_wrap_shiplap(hood_obj, fz=band,
                          board=opts['shiplap_board_width'])
    if opts['include_front_panel']:
        _front_face_frame(hood_obj, opts, band)
    # Shelf extends forward under a projecting mantle to close its
    # bottom (only while it sits at the bottom).
    _liner_shelf(hood_obj, opts['fan_cutout_width'], opts['fan_cutout_depth'],
                 front_ext=max(opts['mantle_depth'] - HOOD_MATERIAL, 0.0)
                 if band > 0.0 and opts['floor_height'] <= 0.0 else 0.0,
                 cutout_offset=opts['fan_cutout_offset'],
                 floor_z=opts['floor_height'])


def _add_wrap_shiplap(hood_obj, fz=0.0, board=None):
    """Mitred wrap shiplap on a straight box hood, sized from the cage's
    current dims (static -- rebuilt by the command / prompts)."""
    w = _HoodWrap(hood_obj)
    prof = _FrontProfile(w.get_input('Dim X'), w.get_input('Dim Y'),
                         max(w.get_input('Dim Z'), inch(1.0)))
    _wrap_shiplap(hood_obj, prof, fz=fz, board=board)


def _build_shiplap_mantle(hood_obj):
    _build_hood_box(hood_obj, bottom_band=inch(6), band_proj=inch(2))
    _add_wrap_shiplap(hood_obj, fz=inch(6))


def _build_shiplap_peninsula(hood_obj):
    _build_hood_box(hood_obj)
    _add_wrap_shiplap(hood_obj)


def _build_shiplap_box(hood_obj):
    _build_hood_box(hood_obj)
    _add_wrap_shiplap(hood_obj)


_STYLE_BUILDERS = {
    'BOX':          lambda o: _build_hood_box(o),
    'SHIPLAP_BOX':  _build_shiplap_box,
    'SHIPLAP_MANTLE': _build_shiplap_mantle,
    'SHIPLAP_PENINSULA': _build_shiplap_peninsula,
    'PENINSULA':    lambda o: _build_hood_box(o),
    'SHELF':        lambda o: _build_hood_box(o, bottom_band=inch(5), band_proj=inch(2)),
    'NICHE':        lambda o: _build_hood_box(o, bottom_band=inch(6), band_proj=inch(1.5)),
    'MANTLE':       _build_mantle,
    'PLANTATION':   _build_plantation,
    'GRAND_MANTLE': _build_grand_mantle,
    'VILLA':        _build_villa,
    'TRADITIONAL':  _build_traditional,
    'CHIMNEY':      _build_chimney,
    'CUSTOM':       _build_custom,
}


def find_hood_root(obj):
    """Walk up from obj to the wood-hood cage (APPLIANCE_TYPE == 'HOOD'), or
    None if obj is not part of a wood hood. Mirrors the cabinet-root walk so
    the cabinet-style assign / paint tools can target hoods the same way."""
    cur = obj
    while cur is not None:
        if cur.get('APPLIANCE_TYPE') == 'HOOD':
            return cur
        cur = cur.parent
    return None


def apply_finish_to_hood(hood_obj, finish_mat, finish_mat_rotated=None):
    """Push a cabinet style's exterior finish onto every wood-hood part.
    Driven cutpart parts get their Top/Bottom Surface + edge inputs set the
    same way face-frame cabinet parts do; plain-mesh parts (the angled
    Traditional / Villa / Chimney styles) take the material in slot 0. Parts
    are matched by HOOD_PART_TAG so nothing else under the cage is touched. A
    None finish material no-ops (e.g. an unresolved custom material)."""
    if finish_mat is None:
        return
    edge_mat = finish_mat_rotated or finish_mat
    for child in hood_obj.children_recursive:
        if not child.get(HOOD_PART_TAG) or child.type != 'MESH':
            continue
        if child.get('HB_HOOD_STATIC_DOOR'):
            # Python-built static door: the finish goes into the mesh's
            # material slots (its cutpart box is hidden, so the input
            # branch below would do nothing visible). build_door_mesh
            # indexes faces against 3 slots (stile / rail / panel).
            mats = child.data.materials
            while len(mats) < 3:
                mats.append(finish_mat)
            for i in range(3):
                mats[i] = finish_mat
            continue
        if any(m.type == 'NODES' and m.node_group for m in child.modifiers):
            part = GeoNodeCutpart(child)
            for slot, mat in (("Top Surface", finish_mat),
                              ("Bottom Surface", finish_mat),
                              ("Edge W1", edge_mat), ("Edge W2", edge_mat),
                              ("Edge L1", edge_mat), ("Edge L2", edge_mat)):
                try:
                    part.set_input(slot, mat)
                except Exception:
                    pass
        elif child.data is not None:
            if child.data.materials:
                child.data.materials[0] = finish_mat
            else:
                child.data.materials.append(finish_mat)


def _reapply_cabinet_style_finish(hood_obj):
    """If the hood carries an assigned cabinet style (STYLE_NAME), re-push that
    style's finish onto the freshly built parts so a rebuild / resize keeps the
    assigned look. Lazy, guarded import: hoods live in the shared 'common'
    library and must not hard-depend on the face-frame product."""
    name = hood_obj.get('STYLE_NAME')
    if not name:
        return
    try:
        from ..face_frame.props_hb_face_frame import get_style_props
        ff = get_style_props()
        style = next((s for s in ff.cabinet_styles if s.name == name), None)
        if style is not None:
            style.assign_style_to_hood(hood_obj)
    except Exception:
        pass


def _ser_value(val):
    """JSON-safe form of a geometry-node input value. Scalars/strings pass
    through; ID pointers (materials / objects) are stored by name + type;
    vectors / colors become lists. Anything else returns None (skipped)."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float, str)):
        return val
    if isinstance(val, bpy.types.Material):
        return {'__idtype__': 'Material', 'name': val.name}
    if isinstance(val, bpy.types.Object):
        return {'__idtype__': 'Object', 'name': val.name}
    try:
        return [v for v in val]
    except TypeError:
        return None


def _deser_value(sval):
    """Inverse of _ser_value: re-resolve ID pointers by name (None if the
    datablock is gone), pass scalars / lists through unchanged."""
    if isinstance(sval, dict):
        idt = sval.get('__idtype__')
        if idt == 'Material':
            return bpy.data.materials.get(sval.get('name'))
        if idt == 'Object':
            return bpy.data.objects.get(sval.get('name'))
        return None
    return sval


def snapshot_hood_part(hood_part):
    """Capture a driven hood cutpart's full parametric recipe -- its modifier
    node group + input values, every driver (data path / index / expression /
    SINGLE_PROP variables), and the transform -- as a JSON string on the part.
    Called right before Make Editable bakes the part to mesh so restore can
    rebuild exactly this one part later. Returns False (no snapshot written) for
    a part with no geometry-node modifier (e.g. the angled styles' plain
    meshes), which can't be reverted this way."""
    mn = getattr(hood_part.home_builder, 'mod_name', '')
    mod = hood_part.modifiers.get(mn) if mn else None
    if mod is None or mod.type != 'NODES' or mod.node_group is None:
        return False
    data = {
        'mod_name': mn,
        'node_group': mod.node_group.name,
        'inputs': {},
        'drivers': [],
        'location': list(hood_part.location),
        'rotation_euler': list(hood_part.rotation_euler),
        'scale': list(hood_part.scale),
    }
    for item in mod.node_group.interface.items_tree:
        if getattr(item, 'item_type', '') != 'SOCKET':
            continue
        if getattr(item, 'in_out', '') != 'INPUT':
            continue
        if getattr(item, 'socket_type', '') == 'NodeSocketGeometry':
            continue
        ident = item.identifier
        try:
            sval = _ser_value(hb_utils.get_gn_input(mod, ident))
        except (KeyError, AttributeError, TypeError):
            continue
        if sval is not None:
            data['inputs'][ident] = sval
    ad = hood_part.animation_data
    if ad:
        for fc in ad.drivers:
            drv = fc.driver
            variables = []
            for v in drv.variables:
                tgt = v.targets[0]
                variables.append({'name': v.name, 'data_path': tgt.data_path})
            data['drivers'].append({
                'data_path': fc.data_path,
                'array_index': fc.array_index,
                'expression': drv.expression,
                'variables': variables,
            })
    hood_part[HOOD_SNAPSHOT_PROP] = json.dumps(data)
    return True


def restore_hood_part(hood_part):
    """Rebuild ONE made-editable hood part from its snapshot: re-add the cutpart
    geometry-node modifier with the captured inputs, recreate every driver
    against the live hood cage, and restore the transform. All driver variables
    on hood parts target the hood cage, so they are re-pointed at the part's
    hood root. Clears the manual flag + snapshot on success. Other parts (driven
    or manual) are untouched. Returns False -- leaving the part as-is so the
    caller can fall back to a full hood rebuild -- if the snapshot, hood cage, or
    node group can't be resolved."""
    raw = hood_part.get(HOOD_SNAPSHOT_PROP)
    if not raw:
        return False
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return False
    hood_root = find_hood_root(hood_part)
    if hood_root is None:
        return False
    ng = bpy.data.node_groups.get(data.get('node_group'))
    if ng is None:
        return False
    # Drop the baked mesh and any leftover drivers (the location / rotation
    # drivers survive the Make-Editable modifier_apply) before rebuilding.
    if hood_part.animation_data:
        for fc in list(hood_part.animation_data.drivers):
            hood_part.animation_data.drivers.remove(fc)
    hood_part.modifiers.clear()
    if hood_part.data is not None and hasattr(hood_part.data, 'clear_geometry'):
        hood_part.data.clear_geometry()
    mod = hood_part.modifiers.new(name=data.get('node_group'), type='NODES')
    mod.node_group = ng
    hood_part.home_builder.mod_name = mod.name
    for ident, sval in data.get('inputs', {}).items():
        try:
            hb_utils.set_gn_input(mod, ident, _deser_value(sval))
        except (KeyError, AttributeError, TypeError):
            pass
    hood_part.location = data.get('location', list(hood_part.location))
    hood_part.rotation_euler = data.get('rotation_euler',
                                        list(hood_part.rotation_euler))
    hood_part.scale = data.get('scale', list(hood_part.scale))
    old_mn = data.get('mod_name')
    for drv in data.get('drivers', []):
        dp = _migrate_mod_input_path(drv['data_path'])
        on_modifier = dp.startswith('modifiers[')
        # The part's own modifier may come back under a new name; re-point its
        # driver paths. Cage-targeted variable paths are left as captured.
        if on_modifier and old_mn:
            dp = dp.replace('modifiers["%s"]' % old_mn,
                            'modifiers["%s"]' % mod.name, 1)
        try:
            # Modifier input values are scalar (no array index); object
            # transform channels (location / rotation) are indexed.
            if on_modifier:
                fc = hood_part.driver_add(dp)
            else:
                fc = hood_part.driver_add(dp, drv['array_index'])
        except (TypeError, RuntimeError):
            continue
        fc.driver.expression = drv['expression']
        for var in drv['variables']:
            nv = fc.driver.variables.new()
            nv.type = 'SINGLE_PROP'
            nv.name = var['name']
            nv.targets[0].id = hood_root
            nv.targets[0].data_path = _migrate_mod_input_path(var['data_path'])
    for key in ('IS_MANUAL_PART', HOOD_SNAPSHOT_PROP):
        if key in hood_part.keys():
            del hood_part[key]
    hood_part.update_tag()
    return True


def build_wood_hood(hood_obj, style):
    """Wipe + rebuild the hood's parts for ``style``. Parts are driven, so
    they resize with the hood cage afterward. Unknown styles fall back to
    the Box (3D builders for the other styles are a follow-up)."""
    _clear_hood_parts(hood_obj)
    builder = _STYLE_BUILDERS.get(style, _build_box)
    builder(hood_obj)
    hood_obj[HOOD_STYLE_PROP] = style
    _reapply_cabinet_style_finish(hood_obj)


def rebuild_built_hood(hood_obj):
    """Rebuild the hood's parts at its current style if a wood hood has
    been built on it (HOOD_STYLE_PROP set); returns True when it rebuilt.

    Used by the style propagation callbacks: hood doors are static
    python-built meshes, so a door-style or overlay edit must rebuild
    them -- unlike cabinet fronts, which restyle in place via
    assign_style_to_front. build_wood_hood ends by re-pushing the
    cabinet style's finish, so callers need no separate finish pass.
    """
    style = hood_obj.get(HOOD_STYLE_PROP)
    if style not in _STYLE_BUILDERS:
        return False
    build_wood_hood(hood_obj, style)
    return True


class HOME_BUILDER_OT_build_wood_hood(bpy.types.Operator):
    """Build the 3D wood-hood parts for the selected range hood. Parts are
    driven so they resize with the hood."""

    bl_idname = "home_builder.build_wood_hood"
    bl_label = "Build Wood Hood"
    bl_description = "Build wood-hood parts on the selected range hood (parts resize with the hood)"
    bl_options = {'REGISTER', 'UNDO'}

    style: EnumProperty(name="Style", items=WOOD_HOOD_STYLE_ITEMS, default='BOX')  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get('APPLIANCE_TYPE') == 'HOOD'

    def invoke(self, context, event):
        existing = context.active_object.get(HOOD_STYLE_PROP)
        if existing in {i[0] for i in WOOD_HOOD_STYLE_ITEMS}:
            self.style = existing
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        self.layout.prop(self, "style")

    def execute(self, context):
        build_wood_hood(context.active_object, self.style)
        self.report({'INFO'}, "Built %s wood hood" % self.style)
        return {'FINISHED'}


class HOME_BUILDER_OT_wood_hood_prompts(bpy.types.Operator):
    """Unified wood-hood dialog: edit the hood's size and style in one place.
    For range hoods this replaces the generic appliance prompts and the
    separate build command. Size is pushed to the cage and the driven parts
    are rebuilt live as the size or style changes (static angled / shiplap
    styles read the cage size at build time, so they track too)."""

    bl_idname = "home_builder.wood_hood_prompts"
    bl_label = "Wood Hood Prompts"
    bl_description = "Edit the size and style of the selected wood hood"
    bl_options = {'UNDO'}

    width: FloatProperty(name="Width", unit='LENGTH', precision=5)  # type: ignore
    height: FloatProperty(name="Height", unit='LENGTH', precision=5)  # type: ignore
    depth: FloatProperty(name="Depth", unit='LENGTH', precision=5)  # type: ignore
    style: EnumProperty(name="Style", items=WOOD_HOOD_STYLE_ITEMS, default='BOX')  # type: ignore

    # Dialog-only: which CUSTOM options section is showing. Not stored
    # on the hood; it just keeps the dialog readable.
    ui_tab: EnumProperty(
        name="Section",
        items=[
            ('SHAPE', "Shape", "Angles, top section, and shiplap"),
            ('MANTLE', "Mantle", "Mantle band, mantle molding, and bottom molding"),
            ('FRONT', "Front", "Face frame, bays, and door grid"),
            ('ENDS', "Ends", "Paneled ends and their fronts"),
            ('LINER', "Liner", "Fan cutout and floor"),
        ],
        default='SHAPE')  # type: ignore

    # CUSTOM-style options (shown when style == 'CUSTOM'; persisted on the
    # hood cage as HOOD_CUSTOM_PROP so they survive rebuilds / reopening).
    angle_front: BoolProperty(
        name="Angle Front",
        description="Slope the front back to the top depth")  # type: ignore
    top_depth: FloatProperty(
        name="Top Depth", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['top_depth'],
        description="Hood depth at the top when the front is angled")  # type: ignore
    angle_sides: BoolProperty(
        name="Angle Sides",
        description="Taper the sides in to the top width")  # type: ignore
    top_width: FloatProperty(
        name="Top Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['top_width'],
        description="Hood width at the top when the sides are angled")  # type: ignore
    top_height: FloatProperty(
        name="Top Height", unit='LENGTH', precision=5, min=0.0,
        default=_CUSTOM_DEFAULTS['top_height'],
        description="Height of the straight section at the top of an angled "
                    "hood; the angle stops there and the hood continues "
                    "straight to the top (0 = angle runs all the way up)")  # type: ignore
    include_mantle: BoolProperty(
        name="Include Mantle",
        description="Projecting mantle band at the bottom of the hood")  # type: ignore
    mantle_height: FloatProperty(
        name="Mantle Height", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['mantle_height'],
        description="Height of the mantle band")  # type: ignore
    mantle_depth: FloatProperty(
        name="Mantle Depth", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['mantle_depth'],
        description="Front-to-back depth of the mantle part, measured from "
                    "the sides' front edges")  # type: ignore
    include_mantle_molding: BoolProperty(
        name="Mantle Molding",
        description="Strips of material wrapping the top and bottom of the "
                    "mantle, mitred at the front corners")  # type: ignore
    mantle_molding_width: FloatProperty(
        name="Molding Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['mantle_molding_width'],
        description="Height of the molding strip")  # type: ignore
    mantle_molding_thickness: FloatProperty(
        name="Molding Thickness", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['mantle_molding_thickness'],
        description="How far the molding stands proud of the mantle faces")  # type: ignore
    include_bottom_molding: BoolProperty(
        name="Bottom Molding",
        description="Strip of material wrapping the bottom of the hood -- "
                    "across the front and back along both sides to the "
                    "wall, mitred at the front corners. Works with or "
                    "without a mantle")  # type: ignore
    bottom_molding_width: FloatProperty(
        name="Bottom Molding Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['bottom_molding_width'],
        description="Height of the bottom molding strip")  # type: ignore
    bottom_molding_thickness: FloatProperty(
        name="Bottom Molding Thickness", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['bottom_molding_thickness'],
        description="How far the bottom molding stands proud of the hood "
                    "faces")  # type: ignore
    fan_cutout_width: FloatProperty(
        name="Fan Cutout Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['fan_cutout_width'],
        description="Width of the fan opening in the bottom liner shelf")  # type: ignore
    fan_cutout_depth: FloatProperty(
        name="Fan Cutout Depth", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['fan_cutout_depth'],
        description="Depth of the fan opening in the bottom liner shelf")  # type: ignore
    fan_cutout_offset: FloatProperty(
        name="Cutout Offset", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['fan_cutout_offset'],
        description="The fan opening centers between the front and the "
                    "wall; shift it toward the front (+) or the wall (-). "
                    "Rim behind the opening = (interior depth - cutout "
                    "depth) / 2 + this value")  # type: ignore
    floor_height: FloatProperty(
        name="Floor Height", unit='LENGTH', precision=5, min=0.0,
        default=_CUSTOM_DEFAULTS['floor_height'],
        description="Raise the hood's bottom liner shelf this far up "
                    "from the hood bottom")  # type: ignore
    include_front_panel: BoolProperty(
        name="Include Front Panel",
        description="Paneled face frame that replaces the plain front "
                    "(stiles, rails, mid stiles over a recessed panel)")  # type: ignore
    panel_stile_width: FloatProperty(
        name="Stile Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['panel_stile_width'],
        description="Width of the frame stiles (outer and mid)")  # type: ignore
    panel_top_rail_width: FloatProperty(
        name="Top Rail Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['panel_top_rail_width'],
        description="Width of the top frame rail")  # type: ignore
    panel_bottom_rail_width: FloatProperty(
        name="Bottom Rail Width", unit='LENGTH', precision=5,
        default=_CUSTOM_DEFAULTS['panel_bottom_rail_width'],
        description="Width of the bottom frame rail")  # type: ignore
    panel_count: IntProperty(
        name="Bays", min=1, max=10,
        default=_CUSTOM_DEFAULTS['panel_count'],
        description="Number of face frame bays across; mid stiles = bays - 1")  # type: ignore
    # Per-bay front pickers (bay_front_1..bay_front_10; the first
    # panel_count are shown / used).
    for _j in range(1, 11):
        __annotations__['bay_front_%d' % _j] = EnumProperty(
            name="Bay %d" % _j, items=BAY_FRONT_ITEMS, default='PANEL',
            description="Front for bay %d of the face frame" % _j)
    del _j
    include_left_end_panel: BoolProperty(
        name="Left Paneled End",
        description="Paneled end (frame + front) replacing the "
                    "left side")  # type: ignore
    include_right_end_panel: BoolProperty(
        name="Right Paneled End",
        description="Paneled end (frame + front) replacing the "
                    "right side")  # type: ignore
    left_end_front: EnumProperty(
        name="Left End Front", items=BAY_FRONT_ITEMS, default='PANEL',
        description="What fills the left paneled end's frame")  # type: ignore
    right_end_front: EnumProperty(
        name="Right End Front", items=BAY_FRONT_ITEMS, default='PANEL',
        description="What fills the right paneled end's frame")  # type: ignore
    door_mid_rails: IntProperty(
        name="Door Mid Rails", min=0, max=6, default=0,
        description="Mid rails on every hood door, splitting it into "
                    "panel rows (0 = the door style's own mid rail "
                    "setting)")  # type: ignore
    door_mid_stiles: IntProperty(
        name="Door Mid Stiles", min=0, max=6, default=0,
        description="Mid stiles on every hood door, splitting each "
                    "panel row into columns")  # type: ignore
    door_grid_col_ratios: StringProperty(
        name="Column Widths",
        description="Relative widths of the door's panel columns, left "
                    "to right -- e.g. \"1 2 1\" or \"1/4 1/2 1/4\" for "
                    "quarter / half / quarter. Any positive numbers "
                    "work; blank = equal columns")  # type: ignore
    door_grid_row_ratios: StringProperty(
        name="Row Heights",
        description="Relative heights of the door's panel rows, bottom "
                    "to top -- e.g. \"1 2 1\" or \"1/4 1/2 1/4\". Any "
                    "positive numbers work; blank = equal rows")  # type: ignore
    include_shiplap: BoolProperty(
        name="Include Shiplap",
        description="Shiplap boards on the front face")  # type: ignore
    shiplap_board_width: EnumProperty(
        name="Shiplap Board Width",
        items=[('4', "4\"", "4 inch shiplap boards"),
               ('5', "5\"", "5 inch shiplap boards"),
               ('6', "6\"", "6 inch shiplap boards")],
        default='6',
        description="Shiplap course width; the last course trims down "
                    "to whatever remains at the top")  # type: ignore

    hood = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.get('APPLIANCE_TYPE') == 'HOOD'

    def invoke(self, context, event):
        self.hood = context.active_object
        wrap = _HoodWrap(self.hood)
        self.width = wrap.get_input('Dim X')
        self.depth = wrap.get_input('Dim Y')
        self.height = wrap.get_input('Dim Z')
        existing = self.hood.get(HOOD_STYLE_PROP)
        if existing in {i[0] for i in WOOD_HOOD_STYLE_ITEMS}:
            self.style = existing
        opts = _get_custom_opts(self.hood)
        self.angle_front = bool(opts['angle_front'])
        self.top_depth = opts['top_depth']
        self.angle_sides = bool(opts['angle_sides'])
        self.top_width = opts['top_width']
        self.top_height = opts['top_height']
        self.include_mantle = bool(opts['include_mantle'])
        self.mantle_height = opts['mantle_height']
        self.mantle_depth = opts['mantle_depth']
        self.include_mantle_molding = bool(opts['include_mantle_molding'])
        self.mantle_molding_width = opts['mantle_molding_width']
        self.mantle_molding_thickness = opts['mantle_molding_thickness']
        self.include_bottom_molding = bool(opts['include_bottom_molding'])
        self.bottom_molding_width = opts['bottom_molding_width']
        self.bottom_molding_thickness = opts['bottom_molding_thickness']
        self.fan_cutout_width = opts['fan_cutout_width']
        self.fan_cutout_depth = opts['fan_cutout_depth']
        self.fan_cutout_offset = opts['fan_cutout_offset']
        self.floor_height = opts['floor_height']
        self.include_front_panel = bool(opts['include_front_panel'])
        self.panel_stile_width = opts['panel_stile_width']
        self.panel_top_rail_width = opts['panel_top_rail_width']
        self.panel_bottom_rail_width = opts['panel_bottom_rail_width']
        self.panel_count = int(opts['panel_count'])
        fronts = _bay_front_list(opts, 10)
        for j in range(10):
            setattr(self, 'bay_front_%d' % (j + 1), fronts[j])
        self.include_left_end_panel = bool(opts['left_end_panel'])
        self.include_right_end_panel = bool(opts['right_end_panel'])
        self.left_end_front = _end_front_kind(opts, False)
        self.right_end_front = _end_front_kind(opts, True)
        self.door_mid_rails = max(int(opts.get('door_mid_rails', 0)), 0)
        self.door_mid_stiles = max(int(opts.get('door_mid_stiles', 0)), 0)
        self.door_grid_col_ratios = str(opts.get('door_grid_col_ratios', ""))
        self.door_grid_row_ratios = str(opts.get('door_grid_row_ratios', ""))
        self.include_shiplap = bool(opts['include_shiplap'])
        bw = opts['shiplap_board_width']
        self.shiplap_board_width = str(min((4, 5, 6),
                                           key=lambda v: abs(inch(v) - bw)))
        if self.hood.get(HOOD_CUSTOM_PROP) is None:
            # First time on this hood: seed the taper from the current size.
            self.top_width = self.width / 2.0
        return context.window_manager.invoke_props_dialog(self, width=330)

    def _apply(self):
        # Set the cage size before rebuilding so the static styles, which read
        # the cage dims at build time, pick up the new dimensions.
        wrap = _HoodWrap(self.hood)
        wrap.set_input('Dim X', self.width)
        wrap.set_input('Dim Y', self.depth)
        wrap.set_input('Dim Z', self.height)
        if self.style == 'CUSTOM':
            self.hood[HOOD_CUSTOM_PROP] = {
                'angle_front': self.angle_front,
                'top_depth': self.top_depth,
                'angle_sides': self.angle_sides,
                'top_width': self.top_width,
                'top_height': self.top_height,
                'include_mantle': self.include_mantle,
                'mantle_height': self.mantle_height,
                'mantle_depth': self.mantle_depth,
                'include_mantle_molding': self.include_mantle_molding,
                'mantle_molding_width': self.mantle_molding_width,
                'mantle_molding_thickness': self.mantle_molding_thickness,
                'include_bottom_molding': self.include_bottom_molding,
                'bottom_molding_width': self.bottom_molding_width,
                'bottom_molding_thickness': self.bottom_molding_thickness,
                'fan_cutout_width': self.fan_cutout_width,
                'fan_cutout_depth': self.fan_cutout_depth,
                'fan_cutout_offset': self.fan_cutout_offset,
                'floor_height': self.floor_height,
                'include_front_panel': self.include_front_panel,
                'panel_stile_width': self.panel_stile_width,
                'panel_top_rail_width': self.panel_top_rail_width,
                'panel_bottom_rail_width': self.panel_bottom_rail_width,
                'panel_count': self.panel_count,
                # All 10 slots persist so shrinking / regrowing the bay
                # count doesn't forget per-bay picks.
                'bay_fronts': [getattr(self, 'bay_front_%d' % (j + 1))
                               for j in range(10)],
                'left_end_panel': self.include_left_end_panel,
                'right_end_panel': self.include_right_end_panel,
                'left_end_front': self.left_end_front,
                'right_end_front': self.right_end_front,
                'door_mid_rails': self.door_mid_rails,
                'door_mid_stiles': self.door_mid_stiles,
                'door_grid_col_ratios': self.door_grid_col_ratios,
                'door_grid_row_ratios': self.door_grid_row_ratios,
                'include_shiplap': self.include_shiplap,
                'shiplap_board_width': inch(float(self.shiplap_board_width)),
            }
        build_wood_hood(self.hood, self.style)

    def check(self, context):
        self._apply()
        return True

    def execute(self, context):
        self._apply()
        self.report({'INFO'}, "Built %s wood hood" % self.style)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        for label, prop in (("Width:", 'width'), ("Height:", 'height'),
                            ("Depth:", 'depth')):
            row = col.row(align=True)
            row.label(text=label)
            row.prop(self, prop, text="")

        layout.prop(self, 'style')

        if self.style != 'CUSTOM':
            return
        row = layout.row(align=True)
        row.prop(self, 'ui_tab', expand=True)
        box = layout.box()
        getattr(self, '_draw_' + self.ui_tab.lower())(box)

    def _draw_shape(self, box):
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'angle_front')
        sub = row.row(align=True)
        sub.active = self.angle_front
        sub.prop(self, 'top_depth', text="Top Depth")

        row = col.row(align=True)
        row.prop(self, 'angle_sides')
        sub = row.row(align=True)
        sub.active = self.angle_sides
        sub.prop(self, 'top_width', text="Top Width")

        row = col.row(align=True)
        row.active = self.angle_front or self.angle_sides
        row.label(text="Top Height:")
        row.prop(self, 'top_height', text="")

        col.separator()
        row = col.row(align=True)
        row.prop(self, 'include_shiplap')
        sub = row.row(align=True)
        sub.active = self.include_shiplap
        sub.prop(self, 'shiplap_board_width', text="")

    def _draw_mantle(self, box):
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'include_mantle')
        sub = row.row(align=True)
        sub.active = self.include_mantle
        sub.prop(self, 'mantle_height', text="H")
        sub.prop(self, 'mantle_depth', text="D")

        row = col.row(align=True)
        row.active = self.include_mantle
        row.prop(self, 'include_mantle_molding')
        sub = row.row(align=True)
        sub.active = self.include_mantle and self.include_mantle_molding
        sub.prop(self, 'mantle_molding_width', text="W")
        sub.prop(self, 'mantle_molding_thickness', text="T")

        col.separator()
        row = col.row(align=True)
        row.prop(self, 'include_bottom_molding')
        sub = row.row(align=True)
        sub.active = self.include_bottom_molding
        sub.prop(self, 'bottom_molding_width', text="W")
        sub.prop(self, 'bottom_molding_thickness', text="T")

    def _draw_front(self, box):
        col = box.column(align=True)
        col.prop(self, 'include_front_panel')
        # Stile / rail widths feed the front face frame AND the paneled
        # ends, so they light up when either is on.
        sub = col.column(align=True)
        sub.active = (self.include_front_panel or self.include_left_end_panel
                      or self.include_right_end_panel)
        row = sub.row(align=True)
        row.label(text="Stile:")
        row.prop(self, 'panel_stile_width', text="")
        row = sub.row(align=True)
        row.label(text="Rails:")
        row.prop(self, 'panel_top_rail_width', text="T")
        row.prop(self, 'panel_bottom_rail_width', text="B")

        bays = col.column(align=True)
        bays.active = self.include_front_panel
        bays.prop(self, 'panel_count')
        for j in range(self.panel_count):
            row = bays.row(align=True)
            row.label(text="Bay %d:" % (j + 1))
            row.prop(self, 'bay_front_%d' % (j + 1), text="")

        col.separator()
        row = col.row(align=True)
        row.label(text="Door Grid:")
        row.prop(self, 'door_mid_rails', text="Rails")
        row.prop(self, 'door_mid_stiles', text="Stiles")
        # Panel-size ratios: each field lights up once its grid
        # direction exists (a blank field keeps equal cells).
        row = col.row(align=True)
        row.active = self.door_mid_stiles > 0
        row.label(text="Col Widths:")
        row.prop(self, 'door_grid_col_ratios', text="")
        row = col.row(align=True)
        row.active = self.door_mid_rails > 0
        row.label(text="Row Heights:")
        row.prop(self, 'door_grid_row_ratios', text="")

    def _draw_ends(self, box):
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Paneled Ends:")
        row.prop(self, 'include_left_end_panel', text="Left", toggle=True)
        row.prop(self, 'include_right_end_panel', text="Right", toggle=True)
        row = col.row(align=True)
        row.active = self.include_left_end_panel
        row.label(text="Left End:")
        row.prop(self, 'left_end_front', text="")
        row = col.row(align=True)
        row.active = self.include_right_end_panel
        row.label(text="Right End:")
        row.prop(self, 'right_end_front', text="")
        # The frame widths live on the Front tab; door grids apply to
        # end doors too.

    def _draw_liner(self, box):
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Fan Cutout:")
        row.prop(self, 'fan_cutout_width', text="W")
        row.prop(self, 'fan_cutout_depth', text="D")

        row = col.row(align=True)
        row.label(text="Cutout Offset:")
        row.prop(self, 'fan_cutout_offset', text="")

        row = col.row(align=True)
        row.label(text="Floor Height:")
        row.prop(self, 'floor_height', text="")


class HOME_BUILDER_OT_revert_hood_part(bpy.types.Operator):
    """Revert a made-editable wood-hood part to parametric control, restoring
    just that part from the snapshot taken when it was made editable. Other
    parts -- driven or manually edited -- are left untouched. Hand edits to the
    reverted part are lost. Needs the snapshot (parts made editable before the
    snapshot feature have none -- rebuild the hood to restore those)."""

    bl_idname = "home_builder.revert_hood_part"
    bl_label = "Revert to Parametric"
    bl_description = ("Discard manual edits on this hood part and let it follow "
                      "the hood again. Hand edits are lost")
    bl_options = {'UNDO'}

    @staticmethod
    def _is_revertable(obj):
        return bool(obj is not None
                    and obj.get(HOOD_PART_TAG)
                    and obj.get('IS_MANUAL_PART')
                    and obj.get(HOOD_SNAPSHOT_PROP))

    @classmethod
    def poll(cls, context):
        return any(cls._is_revertable(o) for o in context.selected_objects)

    def execute(self, context):
        targets = [o for o in context.selected_objects if self._is_revertable(o)]
        if not targets and self._is_revertable(context.active_object):
            targets = [context.active_object]
        done = sum(1 for o in targets if restore_hood_part(o))
        if done == 0:
            self.report({'WARNING'}, "No revertable hood parts (no snapshot)")
            return {'CANCELLED'}
        self.report({'INFO'}, "%d hood part(s) restored to parametric" % done)
        return {'FINISHED'}


_CLASSES = (
    HOME_BUILDER_OT_build_wood_hood,
    HOME_BUILDER_OT_wood_hood_prompts,
    HOME_BUILDER_OT_revert_hood_part,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
