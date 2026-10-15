"""Corbels: fixed-size decorative wood brackets placed as standalone items.

A corbel is a stock part bought at a catalog size, so it is placed whole
rather than sized: a cage the size of the style's bounding box (origin at
the back-left-bottom corner, front toward -Y, like an appliance cage) and
a static mesh child, ``Corbel Body``, carrying the style's geometry.

Styles come from two places:

* ``BUILTIN_STYLES`` -- generic brackets drawn as a side profile extruded
  across the width, so the library has something to place on its own.
* Providers registered with ``register_style_provider`` -- a zero-arg
  callable returning style dicts. A provider can hand over a side
  ``profile`` like the built-ins or a full ``mesh`` table, which is how
  carved shapes that are not a straight extrusion get in.

A style dict::

    {'key':    unique id (stored on the placed corbel),
     'label':  menu text,
     'width', 'depth', 'height': inches,
     'profile': [(d, z), ...]  side outline, inches; d = distance in front
                               of the mounting face, z = up from the bottom.
                               Extruded across the full width.
     -- or --
     'mesh':   (verts, faces)  verts as (x, y, z) in 1/1000 inch with x
                               centered on the width, y = 0 at the
                               mounting face and negative toward the
                               front, z = up from the bottom; faces as
                               vertex index lists.
     'description': optional tooltip}

Keys are stored on the placed object, so a style's key must never be
reused for a different shape.
"""

import bpy
import bmesh
from mathutils import Vector

from ...hb_types import GeoNodeCage
from ...units import inch

CORBEL_TAG = 'IS_CORBEL'
STYLE_PROP = 'CORBEL_STYLE'
LABEL_PROP = 'CORBEL_LABEL'
BODY_TAG = 'IS_CORBEL_BODY'
MENU_ID = 'HOME_BUILDER_MT_corbel_commands'

# Built-in generic shapes: a stepped cap over a cove that sweeps down to
# a narrow foot. (d, z) inches, counter-clockwise from the bottom of the
# mounting face.
BUILTIN_STYLES = (
    {
        'key': 'BRACKET_COVE',
        'label': "Cove Bracket",
        'description': "Generic cove bracket, 3-1/2\" x 7-1/2\" x 12\"",
        'width': 3.5, 'depth': 7.5, 'height': 12.0,
        'profile': None,     # filled below
    },
    {
        'key': 'BRACKET_COVE_SMALL',
        'label': "Small Cove Bracket",
        'description': "Generic cove bracket, 2-1/2\" x 5\" x 8\"",
        'width': 2.5, 'depth': 5.0, 'height': 8.0,
        'profile': None,
    },
)


def _cove_profile(depth, height, segments=16):
    """Side outline for a cove bracket of the given size."""
    import math
    cap_h = height * 0.12          # flat cap the counter sits on
    step = depth * 0.08            # small step under the cap
    foot_d = depth * 0.30          # foot projection at the bottom
    foot_h = height * 0.06
    pts = [(0.0, 0.0), (foot_d, 0.0), (foot_d, foot_h)]
    # Quarter-ellipse cove from the foot up to under the step, centred
    # on the front-bottom corner so it hollows the underside.
    top_z = height - cap_h - step
    cove_d = depth - step - foot_d
    cove_h = top_z - foot_h
    for i in range(1, segments):
        a = (math.pi / 2.0) * i / segments
        pts.append((foot_d + cove_d * (1.0 - math.cos(a)),
                    foot_h + cove_h * math.sin(a)))
    pts += [(depth - step, top_z), (depth - step, height - cap_h),
            (depth, height - cap_h), (depth, height), (0.0, height)]
    return pts


for _s in BUILTIN_STYLES:
    _s['profile'] = _cove_profile(_s['depth'], _s['height'])


# ---- Style registry ---------------------------------------------------------

_providers = []


def register_style_provider(fn):
    """Add ``fn`` (zero-arg callable -> list of style dicts) as a source
    of corbel styles. Provider styles list ahead of the built-ins."""
    if fn not in _providers:
        _providers.append(fn)


def unregister_style_provider(fn):
    if fn in _providers:
        _providers.remove(fn)


def styles():
    """Every available style, provider styles first, unique by key."""
    out, seen = [], set()
    for fn in list(_providers):
        try:
            items = list(fn())
        except Exception as e:  # pragma: no cover - defensive
            print("HB5 corbels: style provider failed: %s" % e)
            continue
        for s in items:
            if s.get('key') and s['key'] not in seen:
                seen.add(s['key'])
                out.append(s)
    for s in BUILTIN_STYLES:
        if s['key'] not in seen:
            seen.add(s['key'])
            out.append(s)
    return out


def get_style(key=None):
    """The style for ``key``, else the first available one."""
    all_styles = styles()
    for s in all_styles:
        if s['key'] == key:
            return s
    return all_styles[0] if all_styles else None


def style_size(style):
    """(width, depth, height) in meters."""
    return (inch(style['width']), inch(style['depth']), inch(style['height']))


# EnumProperty item callbacks must keep their strings alive.
_enum_cache = []


def style_enum_items(_self=None, _context=None):
    global _enum_cache
    _enum_cache = [(s['key'], s['label'], s.get('description', s['label']))
                   for s in styles()]
    if not _enum_cache:
        _enum_cache = [('NONE', "None", "No corbel styles available")]
    return _enum_cache


# ---- Geometry ---------------------------------------------------------------

def _mesh_from_profile(bm, style):
    """Extrude the side profile across the width (x = 0..width)."""
    w = inch(style['width'])
    ring0, ring1 = [], []
    for d, z in style['profile']:
        ring0.append(bm.verts.new((0.0, -inch(d), inch(z))))
        ring1.append(bm.verts.new((w, -inch(d), inch(z))))
    bm.faces.new(ring0)
    bm.faces.new(list(reversed(ring1)))
    n = len(ring0)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))


def _mesh_from_table(bm, style):
    """Lay the vertex/face table into 0..width on x."""
    verts, faces = style['mesh']
    half_w = inch(style['width']) / 2.0
    k = 0.0254 / 1000.0
    bv = [bm.verts.new((x * k + half_w, y * k, z * k)) for x, y, z in verts]
    for f in faces:
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            # Duplicate face in the table; skip it.
            pass


def _box_uvs(bm):
    """Box projection in meters, picked per face by its dominant normal,
    with v running up the corbel on the sides and front so the grain
    runs the long way."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            co = loop.vert.co
            if ax == 0:
                loop[uv].uv = (co.y, co.z)
            elif ax == 1:
                loop[uv].uv = (co.x, co.z)
            else:
                loop[uv].uv = (co.x, co.y)


def build_mesh(style, name="Corbel"):
    """A new mesh datablock for ``style``, in cage space."""
    bm = bmesh.new()
    if style.get('mesh'):
        _mesh_from_table(bm, style)
    else:
        _mesh_from_profile(bm, style)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _box_uvs(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = False
    return me


# ---- Product ----------------------------------------------------------------

class Corbel(GeoNodeCage):
    """A placed corbel: wire cage at the style's size + static body."""

    style_key = None
    # Read by the appliance placement modal for the preview cage size.
    width = inch(3.5)
    depth = inch(7.5)
    height = inch(12.0)
    variable_width = False

    @classmethod
    def size_for(cls, key=None):
        style = get_style(key)
        if style is None:
            return (cls.width, cls.height, cls.depth)
        w, d, h = style_size(style)
        return (w, h, d)

    def create(self, name="Corbel"):
        super().create(name)
        obj = self.obj
        obj[CORBEL_TAG] = True
        obj['MENU_ID'] = MENU_ID
        obj.display_type = 'WIRE'
        obj.hide_render = True
        self.set_input('Mirror Y', True)
        apply_style(obj, self.style_key)


def body_of(cage_obj):
    for child in cage_obj.children:
        if child.get(BODY_TAG):
            return child
    return None


def apply_style(cage_obj, key=None):
    """Size the cage to ``key``'s style and rebuild the body mesh.
    Keeps the body's material."""
    style = get_style(key)
    if style is None:
        return None
    w, d, h = style_size(style)
    cage = GeoNodeCage(cage_obj)
    cage.set_input('Dim X', w)
    cage.set_input('Dim Y', d)
    cage.set_input('Dim Z', h)
    cage_obj[STYLE_PROP] = style['key']
    cage_obj[LABEL_PROP] = style['label']

    body = body_of(cage_obj)
    mat = None
    if body is not None:
        old = body.data
        if old.materials:
            mat = old.materials[0]
        body.data = build_mesh(style, "Corbel Body")
        if old.users == 0:
            bpy.data.meshes.remove(old)
    else:
        body = bpy.data.objects.new("Corbel Body",
                                    build_mesh(style, "Corbel Body"))
        body[BODY_TAG] = True
        body['CABINET_PART'] = True
        for coll in cage_obj.users_collection:
            coll.objects.link(body)
        body.parent = cage_obj
    if mat is not None:
        set_material(cage_obj, mat)
    return body


def set_material(cage_obj, mat):
    body = body_of(cage_obj)
    if body is None or mat is None:
        return
    mats = body.data.materials
    if len(mats) == 0:
        mats.append(mat)
    else:
        mats[0] = mat
