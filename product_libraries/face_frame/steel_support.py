"""Steel countertop supports: flat bar, L and U brackets on a cabinet.

A support is one mesh object parented to the cabinet root, built in the
cabinet's own frame (back face at Y=0, front at Y=-depth, top at the
cabinet height). It runs front-to-back and exits the cabinet through its
back or front face:

- FLAT: bar laid flat, top at the cabinet top, running ``run_in`` into
  the cabinet and ``run_out`` past the face (an island overhang).
- L: the flat leg plus a leg turned down the outside of the face it
  exits (screwed to the cabinet back / end).
- U: bar on edge, a cross piece inside the cabinet and two legs running
  out through the face (a floating vanity hung off the wall).

It is steel, not a cabinet part: no CABINET_PART tag, so the wood
material walk and the wood part lists leave it alone.
"""

import bpy
import bmesh
from bpy.props import EnumProperty, FloatProperty, PointerProperty
from bpy.types import Operator, PropertyGroup, Menu

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


def _prism(bm, outline, axis, lo, hi):
    """Add a closed prism: ``outline`` (2D, counter-clockwise or not)
    swept from ``lo`` to ``hi`` along ``axis`` ('X' or 'Z'). Outline
    points are (y, z) for an X sweep and (x, y) for a Z sweep."""
    pts = []
    for p in outline:
        if not pts or (abs(p[0] - pts[-1][0]) > 1e-9
                       or abs(p[1] - pts[-1][1]) > 1e-9):
            pts.append(p)
    if len(pts) > 2 and (abs(pts[0][0] - pts[-1][0]) < 1e-9
                         and abs(pts[0][1] - pts[-1][1]) < 1e-9):
        pts.pop()

    def co(p, w):
        if axis == 'X':
            return (w, p[0], p[1])
        return (p[0], p[1], w)

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
    # u: distance outward from the face the support exits.
    if sp.exits == 'BACK':
        face_y, sign = 0.0, 1.0
    else:
        face_y, sign = -depth, -1.0

    def y(u):
        return face_y + sign * u

    bm = bmesh.new()
    x0 = sp.x_position - bw / 2.0
    if sp.shape == 'FLAT':
        outline = [(y(-run_in), top - th), (y(run_out), top - th),
                   (y(run_out), top), (y(-run_in), top)]
        _prism(bm, outline, 'X', x0, x0 + bw)
    elif sp.shape == 'L':
        drop = max(sp.drop, th)
        out = max(run_out, th)
        outline = [(y(-run_in), top), (y(out), top), (y(out), top - th),
                   (y(th), top - th), (y(th), top - drop), (y(0.0), top - drop),
                   (y(0.0), top - th), (y(-run_in), top - th)]
        _prism(bm, outline, 'X', x0, x0 + bw)
    else:
        span = max(sp.span, 2.0 * th + inch(0.25))
        left = sp.x_position - span / 2.0
        right = left + span
        inner = -max(run_in, th)
        outline = [(left, y(run_out)), (left, y(inner)), (right, y(inner)),
                   (right, y(run_out)), (right - th, y(run_out)),
                   (right - th, y(inner + th)), (left + th, y(inner + th)),
                   (left + th, y(run_out))]
        _prism(bm, outline, 'Z', top - bw, top)
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


def seed(sp, cp):
    """Starting runs for the support's shape on this cabinet."""
    sp['x_position'] = cp.width / 2.0
    if sp.shape == 'FLAT':
        sp['run_in'] = inch(12.0)
        sp['run_out'] = inch(12.0)
    elif sp.shape == 'L':
        sp['run_in'] = 0.0
        sp['run_out'] = inch(12.0)
        sp['drop'] = inch(8.0)
    else:
        sp['span'] = min(inch(20.5), max(cp.width - inch(1.5), inch(2.0)))
        sp['run_in'] = max(cp.depth - inch(1.0), inch(1.0))
        sp['run_out'] = 0.0


def _update_run(self, context):
    self['runs_set'] = True
    _update(self, context)


class Face_Frame_Steel_Support_Props(PropertyGroup):
    shape: EnumProperty(name="Shape", items=SHAPE_ITEMS, default='FLAT',
                        update=_update_shape)  # type: ignore
    exits: EnumProperty(
        name="Exits",
        items=(('BACK', "Back", "Runs out through the cabinet back"),
               ('FRONT', "Front", "Runs out through the cabinet front")),
        default='BACK', update=_update)  # type: ignore
    x_position: FloatProperty(
        name="Center From Left",
        description="Side to side: cabinet left edge to the support's center",
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


def add_support(cab, shape='FLAT'):
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
        layout.separator()
        layout.operator("hb_general.delete", text="Delete Steel Support",
                        icon='X')


classes = (
    Face_Frame_Steel_Support_Props,
    HB_FACE_FRAME_OT_add_steel_support,
    HB_FACE_FRAME_OT_steel_support_prompts,
    HOME_BUILDER_MT_face_frame_steel_support_commands,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.hb_steel_support = PointerProperty(
        type=Face_Frame_Steel_Support_Props)


def unregister():
    if hasattr(bpy.types.Object, 'hb_steel_support'):
        del bpy.types.Object.hb_steel_support
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
