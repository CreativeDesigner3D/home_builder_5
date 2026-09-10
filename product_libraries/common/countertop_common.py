"""
Countertop pieces both product libraries share: how an island is grouped
into one slab, and the finishing every new top needs.

An island is rarely a single cabinet. It is a row of them, usually with a
second row back to back behind it, and often with a dishwasher or a
beverage centre standing between two of them. Sizing a top to each
cabinet in turn gives an island as many separate slabs as it has boxes,
with a hole wherever an appliance sits -- an appliance is not a cabinet,
so nothing claimed that stretch.

So members are grouped first. Two members belong to the same island when
their footprints touch, and grouping is transitive, which is what lets a
back row bridge a gap the front row has: a dishwasher between two base
cabinets is spanned even if the dishwasher itself were left out, because
the run behind touches both sides of it.

The group's top is one slab over the union of the footprints, measured in
the frame of one member so a rotated island stays square to itself
rather than to the world.

A range is deliberately not an island member. It gets no countertop --
the same rule the wall runs follow -- so it does not join a group, and an
island split by one comes out as two tops, which is correct.

The library's own countertop module owns the overhang and thickness
settings and passes them in; nothing here reads a property group.

A top is not stuck with the rectangle it was measured into. The outline
it was built from is kept on the object, and the slab is rebuilt from
that outline whenever it changes -- which is what lets an island top be
pushed out over a seating overhang, or cut back around a corner, without
the cabinets underneath having to pretend to be that shape.

Every top also goes through finish(), which stamps the right-click menu
and lays down UVs. The UVs matter more than they look: a procedural
material reads the UV output of a Texture Coordinate node, and a mesh
with NO uv layer hands that node (0, 0) at every point -- so the whole
slab samples a single spot of the texture and renders as one flat
colour. That is why a countertop used to need unwrapping by hand
before its material would show.
"""

import math

import bmesh
import bpy
from mathutils import Vector

from ... import hb_types

MENU_ID = 'HOME_BUILDER_MT_countertop_commands'

# Footprints closer than this count as touching. Wide enough for a
# filler or a scribe gap, far short of any real separation between two
# islands.
JOIN_GAP = 0.0254          # 1 inch

# Appliances that stand under a countertop and so belong to the island.
# A range is excluded on purpose (see the module docstring); anything
# taller than the cabinets, a refrigerator, is excluded by height.
UNDER_COUNTER_MARGIN = 4 * 0.0254

# The top's shape, held on the object so it survives a rebuild and a
# file round trip. OUTLINE is a flat list of local XY pairs going round
# the slab; TOP is the local Z of its underside and THICKNESS its depth.
# An ID property can hold a flat list of floats and not much else, which
# is why the outline is stored the way it is.
OUTLINE_KEY = 'ct_outline'
TOP_KEY = 'ct_top_z'
THICKNESS_KEY = 'ct_thickness'

# Two outline points closer than this are the same corner.
POINT_TOL = 1e-6


def footprint(obj):
    """World-space XY corners of an object's cage.

    The cage runs local X 0..dim_x and local Y 0..-dim_y -- the body
    hangs off the origin line towards the front, which is the same
    convention the wall runs use.
    """
    cage = hb_types.GeoNodeCage(obj)
    dim_x = cage.get_input('Dim X')
    dim_y = cage.get_input('Dim Y')
    corners = [(0.0, 0.0), (dim_x, 0.0), (dim_x, -dim_y), (0.0, -dim_y)]
    return [obj.matrix_world @ Vector((x, y, 0.0)) for x, y in corners]


def _bounds(points):
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def _touching(a_pts, b_pts, gap):
    """Do two footprints touch or overlap, within gap?

    Compared as world-axis boxes. Two islands at an angle to each other
    could in principle be called touching when they only pass close by,
    but they would have to be within an inch to do it.
    """
    ax0, ax1, ay0, ay1 = _bounds(a_pts)
    bx0, bx1, by0, by1 = _bounds(b_pts)
    return (ax0 - gap <= bx1 and bx0 - gap <= ax1
            and ay0 - gap <= by1 and by0 - gap <= ay1)


def group_members(members, gap=JOIN_GAP):
    """Split island members into connected groups by touching footprint.

    Returns a list of lists, each in the order the members came in.
    """
    prints = [footprint(m) for m in members]
    groups = []
    unassigned = set(range(len(members)))
    while unassigned:
        seed = min(unassigned)
        unassigned.discard(seed)
        group = [seed]
        frontier = [seed]
        while frontier:
            i = frontier.pop()
            for j in sorted(unassigned):
                if _touching(prints[i], prints[j], gap):
                    unassigned.discard(j)
                    group.append(j)
                    frontier.append(j)
        groups.append([members[i] for i in sorted(group)])
    return groups


def _faces_opposite(a, b):
    """True when b is turned roughly 180 degrees from a -- the back-to-
    back island, whose far side is another front rather than a back."""
    delta = abs((a.matrix_world.to_euler().z - b.matrix_world.to_euler().z))
    delta = delta % (2.0 * math.pi)
    return abs(delta - math.pi) < 0.2


def create_group_countertop(context, members, overhang_front, overhang_sides,
                            overhang_back, thickness, library,
                            cabinets=None):
    """One slab over a whole island. Returns the new object, or None.

    ``members`` are the cabinets and under-counter appliances of one
    island; ``cabinets`` are just the cabinets, which is what sets the
    height -- a dishwasher is shorter than the boxes beside it and must
    not pull the top down.
    """
    if not members:
        return None
    cabinets = cabinets or members
    anchor = cabinets[0]
    to_local = anchor.matrix_world.inverted()

    # Every footprint in the anchor's frame, so a rotated island is
    # measured square to itself.
    local = []
    for member in members:
        local.extend(to_local @ p for p in footprint(member))
    x0, x1, y0, y1 = _bounds(local)

    # The anchor's own body runs to -Y, so local -Y is a front. The
    # far side is a front too when anything faces the other way.
    back_overhang = (overhang_front
                     if any(_faces_opposite(anchor, m) for m in members)
                     else overhang_back)
    x0 -= overhang_sides
    x1 += overhang_sides
    y0 -= overhang_front
    y1 += back_overhang

    top = None
    for cab in cabinets:
        cage = hb_types.GeoNodeCage(cab)
        corner = cab.matrix_world @ Vector((0.0, 0.0, cage.get_input('Dim Z')))
        z = (to_local @ corner).z
        top = z if top is None else max(top, z)
    if top is None:
        return None

    obj = bpy.data.objects.new('Countertop',
                               bpy.data.meshes.new('Countertop'))
    obj.parent = anchor
    obj.matrix_parent_inverse.identity()
    obj['IS_COUNTERTOP'] = True
    context.scene.collection.objects.link(obj)
    # The measured rectangle is only where the top STARTS. It is stored
    # as an outline and the slab built from that, so reshaping it later
    # is the same operation as building it now.
    obj[TOP_KEY] = float(top)
    obj[THICKNESS_KEY] = float(thickness)
    set_outline(obj, ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
    obj['MENU_ID'] = MENU_ID
    obj['HB_COUNTERTOP_LIB'] = library
    rebuild(obj)
    return obj


def outline_of(obj):
    """The top's outline as a list of local (x, y) corners."""
    flat = obj.get(OUTLINE_KEY) or []
    return [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]


def set_outline(obj, points):
    """Store an outline, dropping corners that repeat the one before.

    A drag that pushes one edge onto its neighbour would otherwise leave
    a zero-length edge behind, and a face built on one of those is a
    face with no area.
    """
    flat = []
    last = None
    for x, y in points:
        if last is not None and (abs(last[0] - x) < POINT_TOL
                                 and abs(last[1] - y) < POINT_TOL):
            continue
        flat.extend((float(x), float(y)))
        last = (x, y)
    obj[OUTLINE_KEY] = flat


def has_outline(obj):
    return len(outline_of(obj)) >= 3


def ensure_outline(obj):
    """Give a top an outline if it has none. True when one is there.

    Tops built before the outline existed are boxes, and a box is fully
    described by the mesh it already carries: its footprint is the
    rectangle, and its Z range the underside and the thickness. Seeding
    from that means an old job can be reshaped without being rebuilt,
    and the seeded shape is exactly the slab that was already there.
    """
    if has_outline(obj):
        return True
    mesh = getattr(obj, 'data', None)
    if mesh is None or len(mesh.vertices) < 8:
        return False
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    thickness = max(zs) - min(zs)
    if thickness <= 0.0:
        return False
    obj[TOP_KEY] = float(min(zs))
    obj[THICKNESS_KEY] = float(thickness)
    set_outline(obj, ((min(xs), min(ys)), (max(xs), min(ys)),
                      (max(xs), max(ys)), (min(xs), max(ys))))
    return True


def rebuild(obj):
    """Rewrite the slab's mesh from its stored outline. True if built.

    Writes into the existing mesh datablock, so the material the top is
    already wearing survives being reshaped.
    """
    points = outline_of(obj)
    if len(points) < 3:
        return False
    top = float(obj.get(TOP_KEY, 0.0))
    thickness = float(obj.get(THICKNESS_KEY, 0.0))
    if thickness <= 0.0:
        return False

    bm = bmesh.new()
    lower = [bm.verts.new((x, y, top)) for x, y in points]
    upper = [bm.verts.new((x, y, top + thickness)) for x, y in points]
    bm.faces.new(list(reversed(lower)))
    bm.faces.new(upper)
    count = len(points)
    for i in range(count):
        j = (i + 1) % count
        bm.faces.new((lower[i], lower[j], upper[j], upper[i]))
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    cut_for_sinks(obj)
    apply_world_uvs(obj)
    return True


def cut_for_sinks(obj):
    """The sinks under a top cut their openings through it."""
    try:
        from . import appliance_geo
    except Exception:
        return 0
    return appliance_geo.cut_sink_openings(obj, world_matrix(obj))


def world_matrix(obj):
    """obj.matrix_world, computed rather than read.

    The cached value is stale for an object parented moments ago, and
    every top here is exactly that.
    """
    if obj.parent is None:
        return obj.matrix_basis.copy()
    return obj.parent.matrix_world @ obj.matrix_parent_inverse @ obj.matrix_basis


def apply_world_uvs(obj):
    """Box-project the mesh in world space, 1 UV unit = 1 metre.

    World rather than object space so neighbouring tops share one
    continuous run of stone or tile instead of each restarting the
    pattern at its own corner. Each face takes the plane its normal
    points along, which keeps the top's projection from smearing down
    the edge band.
    """
    mesh = obj.data
    mw = world_matrix(obj)
    rot = mw.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        normal = rot @ face.normal
        axis = max(range(3), key=lambda i: abs(normal[i]))
        for loop in face.loops:
            co = mw @ loop.vert.co
            if axis == 2:
                loop[uv_layer].uv = (co.x, co.y)
            elif axis == 0:
                loop[uv_layer].uv = (co.y, co.z)
            else:
                loop[uv_layer].uv = (co.x, co.z)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def finish(obj, library):
    """Everything a freshly built countertop still needs: its own
    right-click menu, the library that built it (so the menu can offer
    that library's cut command), and UVs."""
    obj['MENU_ID'] = MENU_ID
    obj['HB_COUNTERTOP_LIB'] = library
    cut_for_sinks(obj)
    apply_world_uvs(obj)
    return obj


def is_under_counter(obj, cabinet_top):
    """Does this appliance belong under an island's countertop?

    Anything reaching no higher than the cabinets beside it, except a
    range, which carries its own top.
    """
    if not obj.get('IS_APPLIANCE') or obj.get('APPLIANCE_TYPE') == 'RANGE':
        return False
    try:
        cage = hb_types.GeoNodeCage(obj)
        top = obj.matrix_world.translation.z + cage.get_input('Dim Z')
    except Exception:
        return False
    return top <= cabinet_top + UNDER_COUNTER_MARGIN
