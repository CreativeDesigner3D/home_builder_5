"""Pullout models in frameless drawers and pullouts.

A drawer or pullout opening can name a pullout product from the host's
accessory list (the same code the face frame library stores). Most stay
data only; a hamper or a trash roll-out also shows what it is: a hamper
basket, or one or two bins on a base frame, standing where the drawer
box would, which is hidden while the model stands in for it.
"""

import bpy
import bmesh
from ...units import inch

PULLOUT_HOST = 'opening_interior_pullout'
MODEL_TAG = 'IS_PULLOUT_MODEL'
SIGNATURE_KEY = 'hb_pullout_model_signature'
HIDDEN_KEY = 'hb_hidden_by_pullout_model'

# Bin sizes (width, depth, height) by quart capacity.
_BIN_SIZES = {
    30: (inch(8.5), inch(15.0), inch(17.0)),
    35: (inch(9.0), inch(16.0), inch(18.0)),
    50: (inch(10.75), inch(17.0), inch(20.0)),
}
_SHALLOW_DROP = inch(3.0)
_BASE_T = inch(0.5)
_BIN_WALL = inch(0.125)
_BIN_GAP = inch(0.5)


def model_for(code):
    """('HAMPER', {}) / ('TRASH', {'count', 'quarts', 'shallow'}) for a
    pullout code, or None when it is data only."""
    if not code:
        return None
    from ... import accessory_registry
    entry = accessory_registry.lookup(PULLOUT_HOST, code) or {}
    name = (entry.get('name') or '').lower()
    group = (entry.get('group') or entry.get('section') or '').lower()
    if 'hamper' in name or 'hamper' in group:
        return 'HAMPER', {}
    if 'trash' in group or '-qt' in name:
        quarts = 50 if '50' in name else 30 if '30' in name else 35
        return 'TRASH', {'count': 2 if 'double' in name else 1,
                         'quarts': quarts, 'shallow': 'shallow' in name}
    return None


def _material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        mat.diffuse_color = color
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Roughness'].default_value = 0.6
    return mat


def _open_box(bm, x0, x1, y0, y1, z0, z1, wall, taper=0.0):
    """A bin: a floor and four walls, open at the top, the bottom drawn
    in by ``taper`` on every side."""
    def ring(z, inset):
        return [bm.verts.new((x0 + inset, y0 + inset, z)),
                bm.verts.new((x1 - inset, y0 + inset, z)),
                bm.verts.new((x1 - inset, y1 - inset, z)),
                bm.verts.new((x0 + inset, y1 - inset, z))]
    outer_bot, outer_top = ring(z0, taper), ring(z1, 0.0)
    inner_bot, inner_top = ring(z0 + wall, taper + wall), ring(z1, wall)
    bm.faces.new(list(reversed(outer_bot)))
    bm.faces.new(inner_bot)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((outer_bot[i], outer_bot[j], outer_top[j], outer_top[i]))
        bm.faces.new((inner_bot[j], inner_bot[i], inner_top[i], inner_top[j]))
        bm.faces.new((outer_top[i], outer_top[j], inner_top[j], inner_top[i]))


def _slab(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new(p) for p in (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
              (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[k] for k in f])


def _emit(box_obj, name, bm, mat):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    for coll in box_obj.users_collection:
        coll.objects.link(obj)
        break
    else:
        bpy.context.scene.collection.objects.link(obj)
    obj.parent = box_obj
    obj[MODEL_TAG] = True
    obj['IS_FRAMELESS_INTERIOR_PART'] = True
    obj['MENU_ID'] = 'HOME_BUILDER_MT_interior_part_commands'
    return obj


def _build_hamper(box_obj, dx, dy, dz):
    bm = bmesh.new()
    _open_box(bm, 0.0, dx, 0.0, dy, 0.0, max(dz - inch(1.0), inch(4.0)),
              inch(0.1875), taper=inch(0.25))
    obj = _emit(box_obj, 'Hamper Basket', bm,
                _material('Hamper Liner', (0.78, 0.74, 0.66, 1.0)))
    obj['hb_part_role'] = 'HAMPER_BASKET'
    return [obj]


def _build_trash(box_obj, dx, dy, dz, spec):
    bin_w, bin_d, bin_h = _BIN_SIZES.get(spec['quarts'], _BIN_SIZES[35])
    if spec['shallow']:
        bin_h -= _SHALLOW_DROP
    count = spec['count']
    # Bins shrink to fit a box smaller than they are made.
    fit_w = (dx - _BIN_GAP * (count + 1)) / count
    bin_w = min(bin_w, max(fit_w, inch(2.0)))
    bin_d = min(bin_d, max(dy - inch(1.0), inch(2.0)))
    bin_h = min(bin_h, max(dz - _BASE_T, inch(2.0)))
    made = []
    bm = bmesh.new()
    _slab(bm, 0.0, dx, 0.0, dy, 0.0, _BASE_T)
    frame = _emit(box_obj, 'Trash Pullout Frame', bm,
                  _material('Pullout Frame', (0.55, 0.56, 0.58, 1.0)))
    frame['hb_part_role'] = 'TRASH_FRAME'
    made.append(frame)
    total = count * bin_w + (count - 1) * _BIN_GAP
    x = (dx - total) / 2.0
    y0 = (dy - bin_d) / 2.0
    for k in range(count):
        bm = bmesh.new()
        _open_box(bm, x, x + bin_w, y0, y0 + bin_d, _BASE_T, _BASE_T + bin_h,
                  _BIN_WALL, taper=inch(0.375))
        obj = _emit(box_obj, 'Trash Bin', bm,
                    _material('Trash Bin', (0.9, 0.9, 0.88, 1.0)))
        obj['hb_part_role'] = 'TRASH_BIN'
        made.append(obj)
        x += bin_w + _BIN_GAP
    return made


def _clear(box_obj):
    for child in list(box_obj.children):
        if child.get(MODEL_TAG):
            data = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if isinstance(data, bpy.types.Mesh) and data.users == 0:
                bpy.data.meshes.remove(data)


def solve(opening_obj, box_obj, dims, hidden):
    """Show the pullout model an opening names in place of its drawer
    box, or put the box back. Returns True while a model stands in."""
    code = getattr(opening_obj.face_frame_opening, 'pullout_accessory_code', '')
    model = None if hidden else model_for(code)
    if model is None:
        if box_obj.get(SIGNATURE_KEY) is not None:
            _clear(box_obj)
            box_obj.pop(SIGNATURE_KEY, None)
        box_obj.pop(HIDDEN_KEY, None)
        return False
    signature = repr((code, tuple(round(v, 5) for v in dims)))
    if box_obj.get(SIGNATURE_KEY) != signature or not any(
            c.get(MODEL_TAG) for c in box_obj.children):
        _clear(box_obj)
        kind, spec = model
        if kind == 'HAMPER':
            _build_hamper(box_obj, *dims)
        else:
            _build_trash(box_obj, *dims, spec)
        box_obj[SIGNATURE_KEY] = signature
    # The model stands where the box would; the box itself is not drawn.
    box_obj[HIDDEN_KEY] = True
    box_obj.hide_viewport = True
    box_obj.hide_render = True
    return True
