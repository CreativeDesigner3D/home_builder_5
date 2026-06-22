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
geometry.
"""

import json
import math
import bpy
from bpy.props import EnumProperty, FloatProperty

from ...hb_types import GeoNodeObject, GeoNodeCutpart
from ...units import inch


HOOD_PART_TAG = "IS_WOOD_HOOD_PART"
HOOD_STYLE_PROP = "WOOD_HOOD_STYLE"
# JSON snapshot of a hood part's parametric recipe (modifier node group +
# input values, drivers, transform), stashed when the part is Made Editable so
# it can be reverted to parametric one part at a time. See snapshot_hood_part.
HOOD_SNAPSHOT_PROP = "HOOD_PARAMETRIC_SNAPSHOT"
HOOD_MATERIAL = inch(0.75)

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
]


class _HoodWrap(GeoNodeObject):
    """Wrap an existing hood cage object so GeoNodeObject helpers
    (var_input) can read its Dim X/Y/Z for driving child parts."""

    def __init__(self, obj):
        self.obj = obj


def _clear_hood_parts(hood_obj):
    for child in list(hood_obj.children):
        if child.get(HOOD_PART_TAG):
            bpy.data.objects.remove(child, do_unlink=True)


def _panel(hood_obj, name):
    p = GeoNodeCutpart()
    p.create(name)
    p.obj.parent = hood_obj
    p.obj[HOOD_PART_TAG] = True
    p.obj['MENU_ID'] = 'HOME_BUILDER_MT_face_frame_part_commands'
    return p


def _build_hood_box(hood_obj, bottom_band=0.0, top_crown=0.0, band_proj=0.0):
    """Core box carcass: full left/right sides, a top cap inset between
    them, and a front face between the sides. Optional projecting bands at
    the bottom (mantle / shelf base) and top (crown). All driven off the
    cage Dim X/Y/Z and butted on 3/4" material; the front sits between the
    bands."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    mt = HOOD_MATERIAL
    two_mt = 2.0 * mt

    # Left + right sides (full height x full depth at the ends).
    for name, at_right in (("Hood Left Side", False), ("Hood Right Side", True)):
        s = _panel(hood_obj, name)
        s.obj.rotation_euler.y = math.radians(-90)
        if at_right:
            s.driver_location('x', 'dim_x', [dim_x])
        s.driver_input("Length", 'dim_z', [dim_z])
        s.driver_input("Width", 'dim_y', [dim_y])
        s.set_input("Thickness", mt)
        s.set_input("Mirror Y", True)
        s.set_input("Mirror Z", not at_right)

    # Top cap, inset between the sides.
    top = _panel(hood_obj, "Hood Top")
    top.obj.location.x = mt
    top.driver_location('z', 'dim_z', [dim_z])
    top.driver_input("Length", 'dim_x - %f' % two_mt, [dim_x])
    top.driver_input("Width", 'dim_y', [dim_y])
    top.set_input("Thickness", mt)
    top.set_input("Mirror Y", True)
    top.set_input("Mirror Z", True)

    # Front face, between the sides and between the bands.
    front = _panel(hood_obj, "Hood Front")
    front.obj.rotation_euler.x = math.radians(90)
    front.obj.location.x = mt
    front.obj.location.z = bottom_band
    front.driver_location('y', '-dim_y', [dim_y])
    front.driver_input("Length", 'dim_x - %f' % two_mt, [dim_x])
    front.driver_input("Width", 'dim_z - %f' % (mt + bottom_band + top_crown), [dim_z])
    front.set_input("Thickness", mt)
    front.set_input("Mirror Z", True)

    # Bottom band (mantle / shelf base), full width, projecting forward.
    if bottom_band > 0.0:
        bb = _panel(hood_obj, "Hood Bottom Band")
        bb.obj.rotation_euler.x = math.radians(90)
        bb.driver_location('y', '-dim_y', [dim_y])
        bb.driver_input("Length", 'dim_x', [dim_x])
        bb.set_input("Width", bottom_band)
        bb.set_input("Thickness", mt + band_proj)
        bb.set_input("Mirror Z", False)

    # Top crown band, full width, projecting forward.
    if top_crown > 0.0:
        tc = _panel(hood_obj, "Hood Crown")
        tc.obj.rotation_euler.x = math.radians(90)
        tc.obj.location.z = 0.0
        tc.driver_location('y', '-dim_y', [dim_y])
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
    height_expr = 'dim_z - %f' % (bottom_band + top_crown + 2.0 * rail)
    if ndoors == 2:
        width_expr = '(dim_x - %f) * 0.5' % (2.0 * mt + 2.0 * stile + center)
        doors = [("Hood Panel L", mt + stile, None),
                 ("Hood Panel R", None, 'dim_x * 0.5 + %f' % (center * 0.5))]
    else:
        width_expr = 'dim_x - %f' % (2.0 * mt + 2.0 * stile)
        doors = [("Hood Panel", mt + stile, None)]
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


def _shiplap_front(hood_obj, mt, bottom_band=0.0, top_crown=0.0, wrap_sides=True):
    """Horizontal shiplap boards on the front (and, with wrap_sides, the
    left/right sides), ~6" boards standing 1/2" proud of the flat faces with
    a 1/8" reveal gap between each. Board count fixed at build time from the
    current height; widths/z driven so they track the hood."""
    w = _HoodWrap(hood_obj)
    dim_x = w.var_input('Dim X', 'dim_x')
    dim_y = w.var_input('Dim Y', 'dim_y')
    dim_z = w.var_input('Dim Z', 'dim_z')
    board = inch(6.0)
    reveal = inch(0.125)
    proud = inch(0.5)
    cap = bottom_band + top_crown + mt
    front_h = max(w.get_input('Dim Z') - cap, board)
    n = max(2, int(round(front_h / board)))
    inv = 1.0 / n
    height_expr = 'dim_z * %f - %f' % (inv, cap * inv + reveal)
    for i in range(n):
        z_expr = 'dim_z * %f + %f' % (i * inv, bottom_band - i * cap * inv)
        # Front board.
        fb = _panel(hood_obj, "Hood Shiplap F%d" % i)
        fb.obj.rotation_euler.x = math.radians(90)
        fb.obj.location.x = mt
        fb.driver_location('y', '-dim_y', [dim_y])
        fb.driver_location('z', z_expr, [dim_z])
        fb.driver_input("Length", 'dim_x - %f' % (2.0 * mt), [dim_x])
        fb.driver_input("Width", height_expr, [dim_z])
        fb.set_input("Thickness", proud)
        fb.set_input("Mirror Z", False)
        if not wrap_sides:
            continue
        # Left + right side boards (run the full depth, proud of the sides).
        for name, at_right in (("Hood Shiplap L%d" % i, False), ("Hood Shiplap R%d" % i, True)):
            sb = _panel(hood_obj, name)
            sb.obj.rotation_euler.y = math.radians(-90)
            if at_right:
                sb.driver_location('x', 'dim_x', [dim_x])
            sb.driver_location('z', z_expr, [dim_z])
            sb.driver_input("Length", height_expr, [dim_z])
            sb.driver_input("Width", 'dim_y', [dim_y])
            sb.set_input("Thickness", proud)
            sb.set_input("Mirror Y", True)
            sb.set_input("Mirror Z", at_right)


def _build_shiplap_mantle(hood_obj):
    _build_hood_box(hood_obj, bottom_band=inch(6), band_proj=inch(2))
    _shiplap_front(hood_obj, HOOD_MATERIAL, bottom_band=inch(6))


def _build_shiplap_peninsula(hood_obj):
    _build_hood_box(hood_obj)
    _shiplap_front(hood_obj, HOOD_MATERIAL)


def _build_shiplap_box(hood_obj):
    _build_hood_box(hood_obj)
    _shiplap_front(hood_obj, HOOD_MATERIAL)


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
            sval = _ser_value(mod[ident])
        except (KeyError, TypeError):
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
            mod[ident] = _deser_value(sval)
        except (KeyError, TypeError):
            pass
    hood_part.location = data.get('location', list(hood_part.location))
    hood_part.rotation_euler = data.get('rotation_euler',
                                        list(hood_part.rotation_euler))
    hood_part.scale = data.get('scale', list(hood_part.scale))
    old_mn = data.get('mod_name')
    for drv in data.get('drivers', []):
        dp = drv['data_path']
        on_modifier = dp.startswith('modifiers[')
        # The part's own modifier may come back under a new name; re-point its
        # driver paths. Cage-targeted variable paths are left as captured.
        if on_modifier and old_mn:
            dp = dp.replace('modifiers["%s"]' % old_mn,
                            'modifiers["%s"]' % mod.name, 1)
        try:
            # Modifier inputs are scalar custom props (no array index); object
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
            nv.targets[0].data_path = var['data_path']
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
        return context.window_manager.invoke_props_dialog(self, width=300)

    def _apply(self):
        # Set the cage size before rebuilding so the static styles, which read
        # the cage dims at build time, pick up the new dimensions.
        wrap = _HoodWrap(self.hood)
        wrap.set_input('Dim X', self.width)
        wrap.set_input('Dim Y', self.depth)
        wrap.set_input('Dim Z', self.height)
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

        row = col.row(align=True)
        row.label(text="Width:")
        row.prop(self, 'width', text="")

        row = col.row(align=True)
        row.label(text="Height:")
        row.prop(self, 'height', text="")

        row = col.row(align=True)
        row.label(text="Depth:")
        row.prop(self, 'depth', text="")

        layout.prop(self, 'style')


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
