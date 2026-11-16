"""Steel countertop supports: flat bar, L and U brackets on a cabinet.

A support is one mesh object parented to the cabinet root, built in the
cabinet's own frame (back face at Y=0, front at Y=-depth, top at the
cabinet height). It runs square out of the face it exits -- the back,
the front or either end -- or diagonally out of a corner:

- FLAT: bar laid flat, top at the cabinet top, running ``run_in`` into
  the cabinet and ``run_out`` past the face (an island overhang).
- L: the flat leg plus a leg turned down the outside of the face it
  exits (screwed to the cabinet back / end).
- U: bar on edge, a cross piece inside the cabinet and two legs running
  out through the face (a floating vanity hung off the wall).

It is steel, not a cabinet part: no CABINET_PART tag, so the wood
material walk and the wood part lists leave it alone.

A support is added from the cabinet's own menu, or placed from the part
library: pick a shape, then click cabinets. Each click puts a support
where it lands, out of the nearest face, or out of the corner when the
click is close to one.

What a new support starts as is kept on the scene (Placement Options in
the shape menu): its bar, how far it runs, and whether it stops a set
distance short of the edge of the countertop over the cabinet.
"""

import math

import bpy
import bmesh
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       PointerProperty)
from bpy.types import Operator, PropertyGroup, Menu
from mathutils import Vector

from ...units import inch

STEEL_SUPPORT_TAG = 'IS_STEEL_SUPPORT'
PART_ROLE_STEEL_SUPPORT = 'STEEL_SUPPORT'
MENU_ID = 'HOME_BUILDER_MT_face_frame_steel_support_commands'
STEEL_MATERIAL = 'Steel Support'

SHAPE_ITEMS = (
    ('FLAT', "Flat Bar", "Flat steel bar laid on the cabinet top"),
    ('L', "L-Shaped", "Flat leg plus a leg turned down the outside of the "
                      "face it exits"),
    ('U', "U-Shaped", "Bar on edge: cross piece inside the cabinet, two "
                      "legs running out through the face"),
)


EXIT_ITEMS = (
    ('BACK', "Back", "Runs out through the cabinet back"),
    ('FRONT', "Front", "Runs out through the cabinet front"),
    ('LEFT', "Left End", "Runs out through the cabinet's left end"),
    ('RIGHT', "Right End", "Runs out through the cabinet's right end"),
    ('BACK_LEFT', "Back Left Corner",
     "Runs diagonally out of the back left corner"),
    ('BACK_RIGHT', "Back Right Corner",
     "Runs diagonally out of the back right corner"),
    ('FRONT_LEFT', "Front Left Corner",
     "Runs diagonally out of the front left corner"),
    ('FRONT_RIGHT', "Front Right Corner",
     "Runs diagonally out of the front right corner"),
)
SIDE_EXITS = ('LEFT', 'RIGHT')
CORNER_EXITS = ('BACK_LEFT', 'BACK_RIGHT', 'FRONT_LEFT', 'FRONT_RIGHT')
# A click this close to two faces at once asks for the corner.
CORNER_ZONE = inch(4.0)
_DIAG = math.sqrt(0.5)


def exit_frame(exits, position, width, depth):
    """Where a support leaves the cabinet, in the cabinet's XY:
    (origin on the face, unit vector pointing out, unit vector along
    the face). ``position`` runs from the cabinet's left end on the
    back and front, and from its back on an end; a corner has none."""
    table = {
        'BACK': ((position, 0.0), (0.0, 1.0)),
        'FRONT': ((position, -depth), (0.0, -1.0)),
        'LEFT': ((0.0, -position), (-1.0, 0.0)),
        'RIGHT': ((width, -position), (1.0, 0.0)),
        'BACK_LEFT': ((0.0, 0.0), (-_DIAG, _DIAG)),
        'BACK_RIGHT': ((width, 0.0), (_DIAG, _DIAG)),
        'FRONT_LEFT': ((0.0, -depth), (-_DIAG, -_DIAG)),
        'FRONT_RIGHT': ((width, -depth), (_DIAG, -_DIAG)),
    }
    origin, out = table.get(exits, table['BACK'])
    return origin, out, (out[1], -out[0])


def face_length(exits, width, depth):
    """The length of the face a support exits (0 for a corner)."""
    if exits in CORNER_EXITS:
        return 0.0
    return depth if exits in SIDE_EXITS else width


def reach(exits, width, depth):
    """How far the cabinet runs back from the face a support exits."""
    if exits in CORNER_EXITS:
        return min(width, depth)
    return width if exits in SIDE_EXITS else depth


def _cabinet_of(obj):
    from . import types_face_frame
    return types_face_frame.find_cabinet_root(obj)


def _steel_material():
    mat = bpy.data.materials.get(STEEL_MATERIAL)
    if mat is None:
        mat = bpy.data.materials.new(STEEL_MATERIAL)
        mat.diffuse_color = (0.35, 0.36, 0.38, 1.0)
        mat.metallic = 1.0
        mat.roughness = 0.45
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = (0.35, 0.36, 0.38, 1.0)
            bsdf.inputs['Metallic'].default_value = 1.0
            bsdf.inputs['Roughness'].default_value = 0.45
    return mat


def _prism(bm, outline, co, lo, hi):
    """Add a closed prism: ``outline`` (2D, counter-clockwise or not)
    swept from ``lo`` to ``hi``. ``co(point, w)`` puts an outline point
    at sweep distance ``w`` in the cabinet."""
    pts = []
    for p in outline:
        if not pts or (abs(p[0] - pts[-1][0]) > 1e-9
                       or abs(p[1] - pts[-1][1]) > 1e-9):
            pts.append(p)
    if len(pts) > 2 and (abs(pts[0][0] - pts[-1][0]) < 1e-9
                         and abs(pts[0][1] - pts[-1][1]) < 1e-9):
        pts.pop()

    a = [bm.verts.new(co(p, lo)) for p in pts]
    b = [bm.verts.new(co(p, hi)) for p in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))


def build(obj):
    """Rebuild the support's mesh from its settings and its cabinet."""
    sp = obj.hb_steel_support
    cab = obj.parent
    cp = getattr(cab, 'face_frame_cabinet', None) if cab is not None else None
    if cp is None:
        return
    width, depth, height = cp.width, cp.depth, cp.height
    th = max(sp.thickness, inch(0.0625))
    bw = max(sp.bar_width, inch(0.25))
    top = height - sp.top_offset
    run_in = max(sp.run_in, 0.0)
    run_out = max(sp.run_out, 0.0)
    # u: distance outward from the face the support exits; a: distance
    # along that face from the support's centre.
    (ox, oy), (ux, uy), (ax, ay) = exit_frame(sp.exits, sp.x_position,
                                              width, depth)

    def side_view(p, a):
        # Outline drawn (u, z), swept along the face.
        return (ox + ux * p[0] + ax * a, oy + uy * p[0] + ay * a, p[1])

    def plan_view(p, z):
        # Outline drawn (a, u), swept up.
        return (ox + ax * p[0] + ux * p[1], oy + ay * p[0] + uy * p[1], z)

    bm = bmesh.new()
    if sp.shape == 'FLAT':
        outline = [(-run_in, top - th), (run_out, top - th),
                   (run_out, top), (-run_in, top)]
        _prism(bm, outline, side_view, -bw / 2.0, bw / 2.0)
    elif sp.shape == 'L':
        drop = max(sp.drop, th)
        out = max(run_out, th)
        outline = [(-run_in, top), (out, top), (out, top - th),
                   (th, top - th), (th, top - drop), (0.0, top - drop),
                   (0.0, top - th), (-run_in, top - th)]
        _prism(bm, outline, side_view, -bw / 2.0, bw / 2.0)
    else:
        span = max(sp.span, 2.0 * th + inch(0.25))
        left = -span / 2.0
        right = left + span
        inner = -max(run_in, th)
        outline = [(left, run_out), (left, inner), (right, inner),
                   (right, run_out), (right - th, run_out),
                   (right - th, inner + th), (left + th, inner + th),
                   (left + th, run_out)]
        _prism(bm, outline, plan_view, top - bw, top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if not obj.data.materials:
        obj.data.materials.append(_steel_material())
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)


def refit(root):
    """Rebuild the supports on a cabinet (its size may have changed)."""
    for child in list(root.children):
        if child.get(STEEL_SUPPORT_TAG):
            build(child)


def _update(self, context):
    obj = self.id_data
    if obj is not None and obj.get(STEEL_SUPPORT_TAG):
        build(obj)


def _update_shape(self, context):
    # Seed sensible runs for the new shape the first time it's picked.
    obj = self.id_data
    cab = obj.parent if obj is not None else None
    cp = getattr(cab, 'face_frame_cabinet', None) if cab is not None else None
    if cp is not None and not self.get('runs_set'):
        seed(self, cp)
    _update(self, context)


def defaults(scene=None):
    """The scene's settings for a new support, or None before the
    property is registered."""
    scene = scene or bpy.context.scene
    return getattr(scene, 'hb_steel_bracket_defaults', None)


def _default(name, fallback, scene=None):
    d = defaults(scene)
    return float(getattr(d, name, fallback)) if d is not None else fallback


def seed_values(shape, exits, width, depth):
    """Starting position and runs for a shape leaving a cabinet of this
    size through ``exits``."""
    along = face_length(exits, width, depth)
    out = {'x_position': along / 2.0}
    run_out = _default('run_out', inch(12.0))
    if shape == 'FLAT':
        out.update(run_in=_default('run_in', inch(12.0)), run_out=run_out)
    elif shape == 'L':
        out.update(run_in=0.0, run_out=run_out,
                   drop=_default('drop', inch(8.0)))
    else:
        out.update(
            span=min(inch(20.5), max((along or inch(22.0)) - inch(1.5),
                                     inch(2.0))),
            run_in=max(reach(exits, width, depth) - inch(1.0), inch(1.0)),
            run_out=0.0)
    return out


def seed(sp, cp):
    """Starting runs for the support's shape on this cabinet."""
    for key, value in seed_values(sp.shape, sp.exits, cp.width,
                                  cp.depth).items():
        sp[key] = value


def placement_at(cab, point):
    """(exits, position) for a support asked for at ``point`` (x, y in
    the cabinet's frame): out of the face nearest the point, at the
    point's place along it, or out of the corner when the point is
    within CORNER_ZONE of two faces."""
    cp = cab.face_frame_cabinet
    width, depth = cp.width, cp.depth
    x = min(max(point[0], 0.0), width)
    back = min(max(-point[1], 0.0), depth)
    near = sorted((
        (back, 'BACK'), (depth - back, 'FRONT'),
        (x, 'LEFT'), (width - x, 'RIGHT')))
    (d0, f0), (d1, f1) = near[0], near[1]
    pair = {f0, f1}
    if d1 <= CORNER_ZONE and not pair <= {'BACK', 'FRONT'} \
            and not pair <= {'LEFT', 'RIGHT'}:
        exits = (('BACK' if 'BACK' in pair else 'FRONT') + '_'
                 + ('LEFT' if 'LEFT' in pair else 'RIGHT'))
        return exits, 0.0
    return f0, (back if f0 in SIDE_EXITS else x)


# ---- The countertop over the cabinet --------------------------------------------

TOP_TAGS = ('IS_COUNTERTOP', 'IS_WOOD_TOP')
# A top this far above or below the cabinet's own top still sits on it.
TOP_Z_TOL = inch(3.0)


def _top_edges(cab):
    """Every edge of the tops lying on ``cab``, flattened to the
    cabinet's XY: [((x, y), (x, y))]."""
    height = cab.face_frame_cabinet.height
    inv = cab.matrix_world.inverted()
    scene = cab.users_scene[0] if cab.users_scene else bpy.context.scene
    out = []
    for obj in scene.objects:
        if obj.type != 'MESH' or not any(obj.get(t) for t in TOP_TAGS):
            continue
        try:
            if obj.hide_viewport or not obj.data.vertices:
                continue
            m = inv @ obj.matrix_world
            co = [m @ v.co for v in obj.data.vertices]
        except Exception:
            continue
        low = min(c.z for c in co)
        if abs(low - height) > TOP_Z_TOL:
            continue
        for e in obj.data.edges:
            a, b = co[e.vertices[0]], co[e.vertices[1]]
            if abs(a.x - b.x) > 1e-7 or abs(a.y - b.y) > 1e-7:
                out.append(((a.x, a.y), (b.x, b.y)))
    return out


def countertop_reach(cab, exits, position):
    """How far the countertop over ``cab`` runs past the face a support
    exits, measured along the support, or None with no top there."""
    cp = cab.face_frame_cabinet
    (ox, oy), (ux, uy), _along = exit_frame(exits, position, cp.width,
                                            cp.depth)
    # Start a little inside the cabinet so a top flush with the face
    # still reads as over it.
    back = inch(0.5)
    px, py = ox - ux * back, oy - uy * back
    best = None
    for (ax, ay), (bx, by) in _top_edges(cab):
        ex, ey = bx - ax, by - ay
        den = ux * ey - uy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - px) * ey - (ay - py) * ex) / den
        w = ((ax - px) * uy - (ay - py) * ux) / den
        if t >= 0.0 and -1e-9 <= w <= 1.0 + 1e-9:
            best = t if best is None else max(best, t)
    return None if best is None else best - back


def fitted_run_out(cab, exits, position, setback=None):
    """The run past the cabinet that stops ``setback`` short of the
    countertop's edge, or None when there is no top over the face. A
    top that overhangs less than the setback gives 0: the support stays
    inside the cabinet rather than showing past the counter."""
    over = countertop_reach(cab, exits, position)
    if over is None:
        return None
    if setback is None:
        setback = _default('edge_setback', inch(3.0))
    return max(over - setback, 0.0)


def planned(cab, shape, point):
    """(exits, values) for the support a click at ``point`` adds: where
    it leaves the cabinet and what it starts as."""
    cp = cab.face_frame_cabinet
    exits, position = placement_at(cab, point)
    values = seed_values(shape, exits, cp.width, cp.depth)
    if exits not in CORNER_EXITS:
        values['x_position'] = position
    values['fitted'] = False
    d = defaults()
    if shape != 'U' and (d is None or d.fit_to_countertop):
        run = fitted_run_out(cab, exits, values['x_position'])
        if run is not None:
            values['run_out'] = run
            values['fitted'] = True
    return exits, values


def add_support_at(cab, shape, point):
    """Add a support to ``cab`` where ``point`` asks for it (see
    placement_at). Returns the object."""
    exits, values = planned(cab, shape, point)
    obj = add_support(cab, shape, exits=exits)
    sp = obj.hb_steel_support
    for key in ('x_position', 'run_in', 'run_out', 'drop', 'span'):
        if key in values:
            sp[key] = values[key]
    build(obj)
    return obj


def _update_run(self, context):
    self['runs_set'] = True
    _update(self, context)


class Face_Frame_Steel_Support_Props(PropertyGroup):
    shape: EnumProperty(name="Shape", items=SHAPE_ITEMS, default='FLAT',
                        update=_update_shape)  # type: ignore
    exits: EnumProperty(
        name="Exits", items=EXIT_ITEMS,
        default='BACK', update=_update_shape)  # type: ignore
    x_position: FloatProperty(
        name="Center Along Face",
        description="Where the support sits along the face it exits: from "
                    "the cabinet's left end on the back or front, from its "
                    "back on an end. A corner support has no position",
        default=inch(12.0), unit='LENGTH', precision=4,
        update=_update_run)  # type: ignore
    run_in: FloatProperty(
        name="Into Cabinet",
        description="How far the support runs into the cabinet from the face it exits",
        default=inch(12.0), min=0.0, unit='LENGTH', precision=4,
        update=_update_run)  # type: ignore
    run_out: FloatProperty(
        name="Past Cabinet",
        description="How far the support runs out past the face it exits",
        default=inch(12.0), min=0.0, unit='LENGTH', precision=4,
        update=_update_run)  # type: ignore
    drop: FloatProperty(
        name="Drop Leg",
        description="L-shaped: length of the leg turned down the outside of the face",
        default=inch(8.0), min=0.0, unit='LENGTH', precision=4,
        update=_update_run)  # type: ignore
    span: FloatProperty(
        name="Span",
        description="U-shaped: outside width across the two legs",
        default=inch(20.5), min=inch(1.0), unit='LENGTH', precision=4,
        update=_update_run)  # type: ignore
    top_offset: FloatProperty(
        name="Down From Top",
        description="Cabinet top to the top of the support (0 = flush with the top)",
        default=0.0, unit='LENGTH', precision=4, update=_update)  # type: ignore
    bar_width: FloatProperty(
        name="Bar Width", default=inch(4.0), min=inch(0.25),
        unit='LENGTH', precision=4, update=_update)  # type: ignore
    thickness: FloatProperty(
        name="Thickness", default=inch(0.375), min=inch(0.0625),
        unit='LENGTH', precision=4, update=_update)  # type: ignore


def draw_props(layout, sp):
    col = layout.column(align=True)
    col.use_property_split = True
    col.use_property_decorate = False
    col.prop(sp, 'shape')
    col.prop(sp, 'exits')
    col.separator()
    if sp.exits not in CORNER_EXITS:
        col.prop(sp, 'x_position')
    col.prop(sp, 'run_in')
    col.prop(sp, 'run_out')
    if sp.shape == 'L':
        col.prop(sp, 'drop')
    if sp.shape == 'U':
        col.prop(sp, 'span')
    col.prop(sp, 'top_offset')
    col.separator()
    col.prop(sp, 'bar_width')
    col.prop(sp, 'thickness')


def add_support(cab, shape='FLAT', exits='BACK'):
    """Create a support on cabinet root ``cab``; returns the object."""
    me = bpy.data.meshes.new('Steel Support')
    obj = bpy.data.objects.new('Steel Support', me)
    coll = cab.users_collection[0] if cab.users_collection else \
        bpy.context.scene.collection
    coll.objects.link(obj)
    obj.parent = cab
    obj[STEEL_SUPPORT_TAG] = True
    obj['hb_part_role'] = PART_ROLE_STEEL_SUPPORT
    obj['MENU_ID'] = MENU_ID
    sp = obj.hb_steel_support
    sp['shape'] = [i[0] for i in SHAPE_ITEMS].index(shape)
    sp['exits'] = [i[0] for i in EXIT_ITEMS].index(exits)
    sp['bar_width'] = _default('bar_width', inch(4.0))
    sp['thickness'] = _default('thickness', inch(0.375))
    seed(sp, cab.face_frame_cabinet)
    build(obj)
    return obj


class HB_FACE_FRAME_OT_add_steel_support(Operator):
    """Add a steel countertop support (flat bar, L or U bracket) to this cabinet"""
    bl_idname = "hb_face_frame.add_steel_support"
    bl_label = "Add Steel Support"
    bl_options = {'REGISTER', 'UNDO'}

    shape: EnumProperty(name="Shape", items=SHAPE_ITEMS, default='FLAT')  # type: ignore

    @classmethod
    def poll(cls, context):
        cab = _cabinet_of(context.active_object)
        return cab is not None and hasattr(cab, 'face_frame_cabinet')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        cab = _cabinet_of(context.active_object)
        if cab is None:
            return {'CANCELLED'}
        obj = add_support(cab, self.shape)
        for o in context.selected_objects:
            o.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


# ---- Placing from the part library --------------------------------------------

_place = {'lines': [], 'text': "", 'mouse': (0, 0), 'label': ""}
_place_handles = []


def footprint(cab, shape, point):
    """World-space outline (line pairs) of the support a click at
    ``point`` would add, on the cabinet top."""
    cp = cab.face_frame_cabinet
    exits, v = planned(cab, shape, point)
    (ox, oy), (ux, uy), (ax, ay) = exit_frame(exits, v['x_position'],
                                              cp.width, cp.depth)
    bar = _default('bar_width', inch(4.0))
    half = (v.get('span', bar) if shape == 'U' else bar) / 2.0
    lo, hi = -v['run_in'], max(v['run_out'], inch(0.375))
    mw = cab.matrix_world
    corners = [mw @ Vector((ox + ux * u + ax * a, oy + uy * u + ay * a,
                            cp.height))
               for a, u in ((-half, lo), (half, lo), (half, hi), (-half, hi))]
    lines = []
    for i in range(4):
        lines += [tuple(corners[i]), tuple(corners[(i + 1) % 4])]
    return lines, exits, v


def _view_region(context, event):
    """The 3D view region under the cursor. The tool is started from a
    menu, where the context carries no area, so the view is found from
    the mouse the way the other placement tools find theirs."""
    from ... import hb_snap
    try:
        return hb_snap.get_region(context, event.mouse_x, event.mouse_y)
    except Exception:
        return None


def _redraw_views(context):
    screen = getattr(context, 'screen', None)
    for area in (screen.areas if screen is not None else ()):
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def _hit_cabinet(context, event):
    """(cabinet root, hit point in its frame) under the cursor."""
    from bpy_extras import view3d_utils
    region = _view_region(context, event)
    rv3d = region.data if region is not None else None
    if region is None or rv3d is None:
        return None, None
    coord = (event.mouse_x - region.x, event.mouse_y - region.y)
    _place['mouse'] = coord
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    depsgraph = context.evaluated_depsgraph_get()
    # Walls, countertops and the like are passed through to the cabinet
    # behind them.
    for _ in range(16):
        hit, loc, _n, _i, obj, _m = context.scene.ray_cast(
            depsgraph, origin, direction)
        if not hit or obj is None:
            return None, None
        cab = _cabinet_of(obj.original)
        if cab is not None and hasattr(cab, 'face_frame_cabinet'):
            return cab, cab.matrix_world.inverted() @ loc
        origin = loc + direction * 1e-4
    return None, None


def _draw_place_3d():
    lines = _place['lines']
    if not lines:
        return
    import gpu
    from gpu_extras.batch import batch_for_shader
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": lines})
    gpu.state.blend_set('ALPHA')
    gpu.state.depth_test_set('NONE')
    shader.bind()
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    shader.uniform_float("lineWidth", 3.0)
    shader.uniform_float("color", (0.25, 0.85, 0.4, 1.0))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _draw_place_2d():
    import blf
    x, y = _place['mouse']
    size = 13 * bpy.context.preferences.system.ui_scale
    blf.size(0, size)
    rows = [(_place['label'], (1, 1, 1, 1)),
            (_place['text'] or "Point at a cabinet", (0.45, 0.95, 0.55, 1)
             if _place['text'] else (0.8, 0.8, 0.8, 1)),
            ("Esc or right-click to finish", (0.7, 0.7, 0.7, 1))]
    for i, (text, color) in enumerate(rows):
        blf.position(0, x + 18, y - 18 - i * size * 1.35, 0)
        blf.color(0, *color)
        blf.draw(0, text)


def _remove_place_handles():
    for handle in _place_handles:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
        except Exception:
            pass
    _place_handles.clear()
    _place['lines'] = []
    _place['text'] = ""


class HOME_BUILDER_MT_face_frame_steel_support_shapes(Menu):
    """The shape picker the Steel Bracket tile opens."""
    bl_label = "Steel Bracket"

    def draw(self, context):
        layout = self.layout
        # The pick starts the placing tool, which is a modal: ask for
        # it to be invoked whatever context the menu was opened from.
        layout.operator_context = 'INVOKE_DEFAULT'
        for key, label, _desc in SHAPE_ITEMS:
            layout.operator("hb_face_frame.place_steel_support",
                            text=label).shape = key
        layout.separator()
        layout.operator("hb_face_frame.steel_bracket_options",
                        text="Placement Options...", icon='PREFERENCES')


class HB_FACE_FRAME_OT_place_steel_support(Operator):
    """Click cabinets to add a steel support: out of the nearest face, or out of the corner when the click is near one. Without a shape, opens the shape menu"""
    bl_idname = "hb_face_frame.place_steel_support"
    bl_label = "Place Steel Bracket"
    bl_options = {'REGISTER'}

    # Not remembered: the tile always asks for the shape.
    shape: bpy.props.StringProperty(
        name="Shape", default="", options={'SKIP_SAVE'})  # type: ignore

    _waiting_for_menu = False

    def invoke(self, context, event):
        if self.shape not in [i[0] for i in SHAPE_ITEMS]:
            # A library tile acts on the mouse PRESS; a menu opened
            # there would take the release as its pick and close.
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                self._waiting_for_menu = True
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            bpy.ops.wm.call_menu(
                name=HOME_BUILDER_MT_face_frame_steel_support_shapes.__name__)
            return {'FINISHED'}
        return self._start(context)

    def execute(self, context):
        # Reached when the menu runs the pick without an event: the
        # tool needs none to start, the cursor is read as it moves.
        if self.shape not in [i[0] for i in SHAPE_ITEMS]:
            return {'CANCELLED'}
        return self._start(context)

    def _start(self, context):
        from ... import hb_snap
        if hb_snap.get_region(context) is None:
            self.report({'WARNING'}, "Open a 3D view to place a bracket")
            return {'CANCELLED'}
        self._waiting_for_menu = False
        self.added = 0
        _remove_place_handles()
        _place['label'] = "Steel Bracket  (%s)" % dict(
            (i[0], i[1]) for i in SHAPE_ITEMS)[self.shape]
        # Off screen until the cursor is over a view.
        _place['mouse'] = (-1000, -1000)
        _place_handles.append(bpy.types.SpaceView3D.draw_handler_add(
            _draw_place_3d, (), 'WINDOW', 'POST_VIEW'))
        _place_handles.append(bpy.types.SpaceView3D.draw_handler_add(
            _draw_place_2d, (), 'WINDOW', 'POST_PIXEL'))
        context.window_manager.modal_handler_add(self)
        _redraw_views(context)
        return {'RUNNING_MODAL'}

    def _hover(self, context, event):
        cab, point = _hit_cabinet(context, event)
        if cab is None:
            _place['lines'], _place['text'] = [], ""
        else:
            lines, exits, values = footprint(cab, self.shape, point)
            _place['lines'] = lines
            text = "Click to add: %s" % dict(
                (i[0], i[1]) for i in EXIT_ITEMS)[exits]
            if values.get('fitted'):
                from ...units import unit_to_string
                units_ = context.scene.unit_settings
                text += ", %s past the cabinet (%s from the counter edge)" % (
                    unit_to_string(units_, values['run_out']),
                    unit_to_string(units_, _default('edge_setback',
                                                    inch(3.0))))
            _place['text'] = text
        _redraw_views(context)
        return cab, point

    def _finish(self, context):
        _remove_place_handles()
        _redraw_views(context)
        if getattr(self, 'added', 0):
            self.report({'INFO'}, "Added %d steel support%s" % (
                self.added, "" if self.added == 1 else "s"))
        return {'FINISHED'}

    def modal(self, context, event):
        if self._waiting_for_menu:
            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                bpy.ops.wm.call_menu(
                    name=HOME_BUILDER_MT_face_frame_steel_support_shapes
                    .__name__)
                return {'FINISHED'}
            if event.type in {'ESC', 'RIGHTMOUSE'}:
                return {'CANCELLED'}
            return {'RUNNING_MODAL'}
        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            return self._finish(context)
        if event.type == 'MOUSEMOVE':
            self._hover(context, event)
            # Let the move through: the views keep their own hover.
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            cab, point = self._hover(context, event)
            if cab is None:
                return {'RUNNING_MODAL'}
            add_support_at(cab, self.shape, point)
            self.added += 1
            bpy.ops.ed.undo_push(message="Add Steel Support")
            return {'RUNNING_MODAL'}
        # Orbit, pan and zoom keep working while placing.
        return {'PASS_THROUGH'}


class Face_Frame_Steel_Bracket_Defaults(PropertyGroup):
    """What a newly placed support starts as, kept on the scene."""
    fit_to_countertop: BoolProperty(
        name="Stop Short Of The Counter Edge",
        description="Where a countertop lies over the cabinet, a flat or "
                    "L-shaped support runs out to the set distance from "
                    "its edge. Off, or with no countertop, it runs Past "
                    "Cabinet",
        default=True)  # type: ignore
    edge_setback: FloatProperty(
        name="From Counter Edge",
        description="How far short of the countertop's edge a support "
                    "stops",
        default=inch(3.0), min=0.0, unit='LENGTH',
        precision=4)  # type: ignore
    run_in: FloatProperty(
        name="Into Cabinet",
        description="How far a flat bar runs into the cabinet",
        default=inch(12.0), min=0.0, unit='LENGTH',
        precision=4)  # type: ignore
    run_out: FloatProperty(
        name="Past Cabinet",
        description="How far a support runs past the cabinet when it is "
                    "not stopped short of a counter edge",
        default=inch(12.0), min=0.0, unit='LENGTH',
        precision=4)  # type: ignore
    drop: FloatProperty(
        name="Drop Leg",
        description="L-shaped: length of the leg turned down the face",
        default=inch(8.0), min=0.0, unit='LENGTH',
        precision=4)  # type: ignore
    bar_width: FloatProperty(
        name="Bar Width", default=inch(4.0), min=inch(0.25),
        unit='LENGTH', precision=4)  # type: ignore
    thickness: FloatProperty(
        name="Thickness", default=inch(0.375), min=inch(0.0625),
        unit='LENGTH', precision=4)  # type: ignore


class HB_FACE_FRAME_OT_steel_bracket_options(Operator):
    """What a newly placed steel support starts as"""
    bl_idname = "hb_face_frame.steel_bracket_options"
    bl_label = "Steel Bracket Placement Options"
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        d = defaults(context.scene)
        col = self.layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(d, 'fit_to_countertop')
        sub = col.column(align=True)
        sub.active = d.fit_to_countertop
        sub.prop(d, 'edge_setback')
        col.separator()
        col.prop(d, 'run_in')
        col.prop(d, 'run_out')
        col.prop(d, 'drop')
        col.separator()
        col.prop(d, 'bar_width')
        col.prop(d, 'thickness')

    def execute(self, context):
        return {'FINISHED'}


class HB_FACE_FRAME_OT_steel_support_fit_countertop(Operator):
    """Run this support out to the set distance from the edge of the countertop over its cabinet"""
    bl_idname = "hb_face_frame.steel_support_fit_countertop"
    bl_label = "Fit To Countertop"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get(STEEL_SUPPORT_TAG))

    def execute(self, context):
        done = 0
        picked = [o for o in context.selected_objects
                  if o.get(STEEL_SUPPORT_TAG)]
        if context.active_object not in picked:
            picked.append(context.active_object)
        for obj in picked:
            cab = obj.parent
            sp = obj.hb_steel_support
            if cab is None or sp.shape == 'U':
                continue
            run = fitted_run_out(cab, sp.exits, sp.x_position)
            if run is None:
                continue
            sp.run_out = run
            done += 1
        if not done:
            self.report({'WARNING'},
                        "No countertop overhangs the cabinet there")
            return {'CANCELLED'}
        return {'FINISHED'}


class HB_FACE_FRAME_OT_steel_support_prompts(Operator):
    """Steel support options"""
    bl_idname = "hb_face_frame.steel_support_prompts"
    bl_label = "Steel Support Options"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and bool(obj.get(STEEL_SUPPORT_TAG))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        draw_props(self.layout, context.active_object.hb_steel_support)

    def execute(self, context):
        return {'FINISHED'}


class HOME_BUILDER_MT_face_frame_steel_support_commands(Menu):
    """Right-click menu for a steel support."""
    bl_label = "Steel Support Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("hb_face_frame.steel_support_prompts",
                        text="Steel Support Options...", icon='WINDOW')
        layout.operator("hb_face_frame.steel_support_fit_countertop",
                        icon='SNAP_EDGE')
        layout.separator()
        layout.operator("hb_general.delete", text="Delete Steel Support",
                        icon='X')


classes = (
    Face_Frame_Steel_Support_Props,
    Face_Frame_Steel_Bracket_Defaults,
    HB_FACE_FRAME_OT_steel_bracket_options,
    HB_FACE_FRAME_OT_steel_support_fit_countertop,
    HB_FACE_FRAME_OT_add_steel_support,
    HB_FACE_FRAME_OT_steel_support_prompts,
    HOME_BUILDER_MT_face_frame_steel_support_commands,
    HOME_BUILDER_MT_face_frame_steel_support_shapes,
    HB_FACE_FRAME_OT_place_steel_support,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_steel_support = PointerProperty(
        type=Face_Frame_Steel_Support_Props)
    bpy.types.Scene.hb_steel_bracket_defaults = PointerProperty(
        type=Face_Frame_Steel_Bracket_Defaults)


def unregister():
    _remove_place_handles()
    if hasattr(bpy.types.Object, 'hb_steel_support'):
        del bpy.types.Object.hb_steel_support
    if hasattr(bpy.types.Scene, 'hb_steel_bracket_defaults'):
        del bpy.types.Scene.hb_steel_bracket_defaults
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
