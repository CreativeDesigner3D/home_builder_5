"""
Operators for rendering surfaces: wall backsplashes and the materials
that dress them and the countertops.

Four commands and a right-click menu:

  home_builder.add_backsplash      build them, over the room or a pick
  home_builder.edit_backsplash     drag the edges in the viewport
  home_builder.remove_backsplash   take them out again
  home_builder.surface_material    restyle a backsplash or a countertop

Add gets a short material choice (style, look, tile format) so a splash
lands looking like something; the full control -- custom colors, joint
width, or a photographed material dragged in from a material asset
library -- lives in the restyle dialog, where it can be pointed at
countertops too.

The edit modal draws only while it is running: no persistent overlay,
nothing left behind when it exits.
"""

import blf
import bpy
import gpu
from bpy.props import (BoolProperty, EnumProperty, FloatProperty,
                       FloatVectorProperty, StringProperty)
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.geometry import intersect_line_plane

from .. import backsplash, units
from .. import surface_materials as sm

SPLASH_MATERIAL = "Backsplash"
COUNTERTOP_MATERIAL = "Countertop"


def _length(context, value):
    """A distance in the file's own units, for header and overlay text."""
    try:
        return units.unit_to_string(context.scene.unit_settings, value)
    except Exception:
        return f"{value / backsplash.INCH:.3f} in"


def _look_colors(style, look):
    entry = sm.SURFACE_LOOKS.get(style, {}).get(look)
    if not entry or entry[1] is None:
        return None, None
    return entry[1], entry[2] or entry[1]


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------

def _add_look_items(self, context):
    return sm.look_items(self.style)


def _add_style_changed(self, context):
    self.look = sm.DEFAULT_LOOK.get(self.style, 'CUSTOM')


class HOME_BUILDER_OT_add_backsplash(bpy.types.Operator):
    bl_idname = "home_builder.add_backsplash"
    bl_label = "Add Backsplash"
    bl_description = ("Tile the wall above the countertop. Runs across the "
                      "base cabinets on each wall, cut around any windows "
                      "and doors")
    bl_options = {'REGISTER', 'UNDO'}

    scope: EnumProperty(
        name="Where", default='ROOM',
        items=[('ROOM', "Whole Room",
                "Every run of base cabinets in this room", 'HOME', 0),
               ('SELECTED', "Selected Walls",
                "Only the walls holding the selected cabinets or walls",
                'RESTRICT_SELECT_OFF', 1)])
    height_mode: EnumProperty(name="Height", default='UPPERS',
                              items=backsplash.HEIGHT_MODE_ITEMS)
    height: FloatProperty(
        name="Fixed Height", default=backsplash.DEFAULT_HEIGHT,
        min=backsplash.MIN_HEIGHT, max=3.0, unit='LENGTH', precision=4,
        description="Height above the countertop, and the height used "
                    "across the gaps between upper cabinets")
    thickness: FloatProperty(
        name="Thickness", default=backsplash.DEFAULT_THICKNESS,
        min=0.001, max=0.05, unit='LENGTH', precision=4,
        description="How far the tile stands off the wall")

    style: EnumProperty(name="Material", default='TILE',
                        items=sm.SURFACE_STYLE_ITEMS[:4],
                        update=_add_style_changed)
    look: EnumProperty(name="Look", items=_add_look_items)
    tile_format: EnumProperty(name="Tile", default='SUBWAY',
                              items=sm.format_items())

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "scope")
        col.prop(self, "height_mode")
        if self.height_mode != 'CEILING':
            col.prop(self, "height")
        col.prop(self, "thickness")
        layout.separator()
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "style")
        col.prop(self, "look")
        if self.style == 'TILE':
            col.prop(self, "tile_format")
        layout.label(text="Drag the edges afterwards with Edit Backsplash.",
                     icon='INFO')

    def _wall_names(self, context):
        names = set()
        for obj in context.selected_objects:
            node = obj
            while node is not None:
                if node.get('IS_WALL_BP'):
                    names.add(node.name)
                    break
                node = node.parent
        return names

    def _material(self):
        base, accent = _look_colors(self.style, self.look)
        if base is None:
            base, accent = (0.94, 0.94, 0.92), (0.80, 0.79, 0.76)
        fmt = sm.TILE_FORMATS.get(self.tile_format)
        if fmt and fmt[1]:
            tile_w, tile_h, bond = fmt[1], fmt[2], fmt[3]
        else:
            tile_w = tile_h = 6 * sm.INCH
            bond = False
        return sm.build_surface_material(
            SPLASH_MATERIAL, self.style, base, accent,
            sm.DEFAULT_ROUGHNESS.get(self.style, 0.2),
            tile_w=tile_w, tile_h=tile_h, running_bond=bond,
            grout_size=0.125 * sm.INCH)

    def execute(self, context):
        wall_names = None
        if self.scope == 'SELECTED':
            wall_names = self._wall_names(context)
            if not wall_names:
                self.report({'WARNING'},
                            "Select a wall or a cabinet on one first")
                return {'CANCELLED'}

        runs = backsplash.base_runs(context, wall_names)
        if not runs:
            self.report({'WARNING'},
                        "No base cabinets found to run a backsplash along")
            return {'CANCELLED'}

        mat = self._material()

        # Clear every wall face being rebuilt BEFORE building any of it.
        # Clearing inside the loop would delete the splash a previous run
        # on the same wall had just made -- one wall carries two runs
        # whenever a doorway breaks the cabinets.
        cleared = set()
        for run in runs:
            key = (run['wall'].name, run['is_back'])
            if key in cleared:
                continue
            cleared.add(key)
            for old in backsplash.existing(context, run['wall'],
                                           run['is_back']):
                bpy.data.objects.remove(old, do_unlink=True)

        made = 0
        for run in runs:
            segs = backsplash.segments_for(
                run['wall'], run['is_back'], run['x0'], run['x1'],
                run['z0'], self.height_mode, self.height)
            if not segs:
                continue
            obj = backsplash.create(context, run['wall'], run['is_back'],
                                    segs, run['z0'], self.thickness)
            obj['bs_height_mode'] = self.height_mode
            sm.assign(obj, mat)
            made += 1

        if not made:
            self.report({'WARNING'}, "Nothing to tile")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Added {made} backsplash(es)")
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_backsplash(bpy.types.Operator):
    bl_idname = "home_builder.remove_backsplash"
    bl_label = "Remove Backsplash"
    bl_description = ("Delete backsplashes -- the selected ones, or all of "
                      "them when nothing is selected")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        picked = [o for o in context.selected_objects
                  if backsplash.is_backsplash(o)]
        targets = picked or backsplash.existing(context)
        if not targets:
            self.report({'WARNING'}, "No backsplashes here")
            return {'CANCELLED'}
        count = len(targets)
        for obj in targets:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Removed {count} backsplash(es)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Numeric edit
# ---------------------------------------------------------------------------

class HOME_BUILDER_OT_backsplash_prompts(bpy.types.Operator):
    bl_idname = "home_builder.backsplash_prompts"
    bl_label = "Backsplash Prompts"
    bl_description = "Set this backsplash's height and thickness by number"
    bl_options = {'REGISTER', 'UNDO'}

    height: FloatProperty(
        name="Height", default=backsplash.DEFAULT_HEIGHT,
        min=backsplash.MIN_HEIGHT, max=3.0, unit='LENGTH', precision=4,
        description="Height above the countertop. Applied to every step, "
                    "so a run that follows the uppers goes flat")
    thickness: FloatProperty(
        name="Thickness", default=backsplash.DEFAULT_THICKNESS,
        min=0.001, max=0.05, unit='LENGTH', precision=4)
    flatten: BoolProperty(
        name="Level the Top", default=False,
        description="Give the whole run one height instead of stepping "
                    "it around the upper cabinets")

    @classmethod
    def poll(cls, context):
        return backsplash.is_backsplash(context.active_object)

    def invoke(self, context, event):
        obj = context.active_object
        x0, x1, z0, z_top = backsplash.bounds_of(obj)
        self.height = max(z_top - z0, backsplash.MIN_HEIGHT)
        self.thickness = obj.get('bs_thickness',
                                 backsplash.DEFAULT_THICKNESS)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        z0 = obj.get('bs_z0', 0.0)
        segs = backsplash.segments_of(obj)
        if not segs:
            return {'CANCELLED'}
        if self.flatten:
            segs = [(segs[0][0], segs[-1][1], z0 + self.height)]
        else:
            segs = [(s[0], s[1], z0 + self.height) for s in segs]
        backsplash.set_segments(obj, segs)
        obj['bs_thickness'] = self.thickness
        backsplash.rebuild(obj)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Interactive edit
# ---------------------------------------------------------------------------

GRIP_PX = 4.0
EDGE_PX = 2.0
EDGE_HOT_PX = 6.0
PICK_PX = 14.0
SNAP_STEP = backsplash.INCH

COL_OUTLINE = (0.15, 0.65, 1.0, 0.5)
COL_EDGE = (0.15, 0.65, 1.0, 1.0)
COL_HOT = (1.0, 0.75, 0.15, 1.0)
COL_TEXT = (1.0, 1.0, 1.0, 1.0)
COL_LABEL_BG = (0.0, 0.0, 0.0, 0.65)


def _thick_line(shader, a, b, width):
    """A screen-space line as a quad.

    Not gpu.state.line_width_set: a core profile clamps glLineWidth to
    1.0 on plenty of drivers, so the highlight would simply not thicken
    on the machines it matters for.
    """
    d = b - a
    if d.length < 1e-6:
        return
    n = Vector((-d.y, d.x)).normalized() * (width / 2.0)
    batch_for_shader(shader, 'TRI_FAN', {"pos": [
        tuple(a + n), tuple(b + n), tuple(b - n), tuple(a - n)]}).draw(shader)


def _quad(shader, x, y, w, h):
    batch_for_shader(shader, 'TRI_FAN', {"pos": [
        (x, y), (x + w, y), (x + w, y + h), (x, y + h)]}).draw(shader)


def _draw_edit(op):
    """Draw every edge that can be dragged, and light up the one under
    the mouse.

    The edge IS the control. Drawing only a grip dot left it unclear
    what the tool even offered, so all four kinds of edge are painted in
    full, and hovering thickens one and puts its dimension beside it --
    before any click, so what a drag is about to change is visible first.
    """
    # bpy.context, not the context captured at registration: the handler
    # fires once per region and only the live one names the right region.
    #
    # `!=`, never `is not`: every access to context.region builds a fresh
    # Python wrapper around the same C pointer, so identity is false even
    # for the region we are standing in. RNA's own comparison is what
    # actually asks "same region".
    context = bpy.context
    if context.region != op.region:
        return
    region, rv3d = context.region, context.region_data

    def to2d(p):
        return view3d_utils.location_3d_to_region_2d(region, rv3d, p)

    active = op.drag if op.drag is not None else op.hover
    label = None
    if op.readout and active is not None and 0 <= active < len(op.handles):
        pos = to2d(op.handles[active]['world'])
        if pos is not None:
            blf.size(0, 13)
            tw, th = blf.dimensions(0, op.readout)
            label = (pos.x + 14.0, pos.y + 14.0, tw, th)

    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    try:
        pts = [to2d(p) for p in op.outline_world]
        if len(pts) > 2 and all(p is not None for p in pts):
            shader.uniform_float("color", COL_OUTLINE)
            batch_for_shader(shader, 'LINE_LOOP',
                             {"pos": [tuple(p) for p in pts]}).draw(shader)

        for i, handle in enumerate(op.handles):
            a, b = to2d(handle['a']), to2d(handle['b'])
            if a is None or b is None:
                continue
            hot = (i == active)
            shader.uniform_float("color", COL_HOT if hot else COL_EDGE)
            _thick_line(shader, a, b, EDGE_HOT_PX if hot else EDGE_PX)
            # A grip at the middle keeps a very short edge -- the end of
            # a shallow step -- something to aim at.
            mid = (a + b) / 2.0
            r = GRIP_PX * (1.6 if hot else 1.0)
            _quad(shader, mid.x - r, mid.y - r, r * 2.0, r * 2.0)

        if label is not None:
            x, y, tw, th = label
            shader.uniform_float("color", COL_LABEL_BG)
            _quad(shader, x - 5.0, y - 4.0, tw + 10.0, th + 8.0)
    finally:
        gpu.state.blend_set('NONE')

    if label is not None:
        x, y, _tw, _th = label
        blf.size(0, 13)
        blf.color(0, *COL_TEXT)
        blf.position(0, x, y, 0)
        blf.draw(0, op.readout)
        gpu.state.blend_set('NONE')


class HOME_BUILDER_OT_edit_backsplash(bpy.types.Operator):
    bl_idname = "home_builder.edit_backsplash"
    bl_label = "Edit Backsplash"
    bl_description = ("Drag the backsplash edges in the viewport -- the top "
                      "of each step, the two ends, and the bottom")
    bl_options = {'REGISTER', 'UNDO'}

    _draw_handle = None

    @classmethod
    def poll(cls, context):
        if context.area is None or context.area.type != 'VIEW_3D':
            return False
        obj = context.active_object
        return backsplash.is_backsplash(obj)

    # -- state ---------------------------------------------------------
    def _plane(self):
        """(point, normal) of the tile face in world space -- the plane a
        drag is measured in."""
        y_back, y_front = backsplash.slab_y(self.obj, self.wall)
        mw = self.wall.matrix_world
        point = mw @ Vector((0.0, y_front, 0.0))
        normal = (mw.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        return point, normal

    def _rebuild_handles(self):
        obj = self.obj
        segs = backsplash.segments_of(obj)
        z0 = obj.get('bs_z0', 0.0)
        _, y_front = backsplash.slab_y(obj, self.wall)
        mw = self.wall.matrix_world

        def world(x, z):
            return mw @ Vector((x, y_front, z))

        # Each handle is an EDGE (a, b) rather than a point, so the
        # whole line is the hit target and the highlight.
        self.handles = []
        for i, (x0, x1, top) in enumerate(segs):
            self.handles.append({'kind': 'TOP', 'index': i,
                                 'a': world(x0, top), 'b': world(x1, top)})
        if segs:
            first, last = segs[0], segs[-1]
            self.handles.append({'kind': 'LEFT', 'index': 0,
                                 'a': world(first[0], z0),
                                 'b': world(first[0], first[2])})
            self.handles.append({'kind': 'RIGHT', 'index': len(segs) - 1,
                                 'a': world(last[1], z0),
                                 'b': world(last[1], last[2])})
            self.handles.append({'kind': 'BOTTOM', 'index': -1,
                                 'a': world(first[0], z0),
                                 'b': world(last[1], z0)})
        for handle in self.handles:
            handle['world'] = (handle['a'] + handle['b']) / 2.0

        profile = backsplash.profile_points(segs, z0)
        self.outline_world = [world(x, z) for x, z in profile]

    @staticmethod
    def _distance_to_edge(p, a, b):
        """Screen distance from p to the segment ab, not to its ends --
        so anywhere along a long top edge picks it."""
        ab = b - a
        length_sq = ab.length_squared
        if length_sq < 1e-9:
            return (p - a).length
        t = max(0.0, min(1.0, (p - a).dot(ab) / length_sq))
        return (p - (a + ab * t)).length

    def _pick(self, context, event):
        region, rv3d = context.region, context.region_data
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        best, best_d = None, PICK_PX
        for i, handle in enumerate(self.handles):
            a = view3d_utils.location_3d_to_region_2d(region, rv3d,
                                                      handle['a'])
            b = view3d_utils.location_3d_to_region_2d(region, rv3d,
                                                      handle['b'])
            if a is None or b is None:
                continue
            d = self._distance_to_edge(mouse, a, b)
            if d < best_d:
                best, best_d = i, d
        return best

    def _readout_for(self, context, index):
        """What the edge under the mouse currently measures."""
        if index is None or not (0 <= index < len(self.handles)):
            return ""
        segs = backsplash.segments_of(self.obj)
        if not segs:
            return ""
        handle = self.handles[index]
        z0 = self.obj.get('bs_z0', 0.0)
        if handle['kind'] == 'TOP':
            return _length(context, segs[handle['index']][2] - z0)
        if handle['kind'] == 'BOTTOM':
            return _length(context, max(s[2] for s in segs) - z0)
        return _length(context, segs[-1][1] - segs[0][0])

    def _set_cursor(self, context):
        """Point the cursor the way the edge under it moves."""
        kind = None
        if self.hover is not None and 0 <= self.hover < len(self.handles):
            kind = self.handles[self.hover]['kind']
        if kind in ('TOP', 'BOTTOM'):
            context.window.cursor_modal_set('MOVE_Y')
        elif kind in ('LEFT', 'RIGHT'):
            context.window.cursor_modal_set('MOVE_X')
        else:
            context.window.cursor_modal_set('DEFAULT')

    def _local_point(self, context, event):
        """The mouse, projected onto the tile plane, in wall-local space.

        Ray / plane rather than a view-depth guess so a drag reads the
        same whether the wall is seen square on or at an angle; an
        edge-on view (no intersection) falls back to the view-depth
        point through the handle, which is the best available there.
        """
        region, rv3d = context.region, context.region_data
        co = (event.mouse_region_x, event.mouse_region_y)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, co)
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, co)
        point, normal = self._plane()
        world = intersect_line_plane(origin, origin + direction * 1000.0,
                                     point, normal)
        if world is None:
            anchor = self.handles[self.drag]['world']
            world = view3d_utils.region_2d_to_location_3d(
                region, rv3d, co, anchor)
        return self.wall.matrix_world.inverted() @ world

    def _apply(self, context, event):
        handle = self.handles[self.drag]
        local = self._local_point(context, event)
        obj = self.obj
        segs = backsplash.segments_of(obj)
        z0 = obj.get('bs_z0', 0.0)
        if not segs:
            return

        value = local.z if handle['kind'] in ('TOP', 'BOTTOM') else local.x
        if event.ctrl:
            value = round(value / SNAP_STEP) * SNAP_STEP

        kind, i = handle['kind'], handle['index']
        if kind == 'TOP':
            segs[i] = (segs[i][0], segs[i][1],
                       max(value, z0 + backsplash.MIN_HEIGHT))
        elif kind == 'BOTTOM':
            ceiling = min(s[2] for s in segs) - backsplash.MIN_HEIGHT
            obj['bs_z0'] = min(value, ceiling)
        elif kind == 'LEFT':
            segs[0] = (min(value, segs[0][1] - backsplash.MIN_SPAN),
                       segs[0][1], segs[0][2])
        else:
            segs[-1] = (segs[-1][0],
                        max(value, segs[-1][0] + backsplash.MIN_SPAN),
                        segs[-1][2])

        backsplash.set_segments(obj, segs)
        backsplash.rebuild(obj)
        self._rebuild_handles()
        # Levelling a step with its neighbour fuses the two -- which is
        # the right shape, but it leaves the handle list shorter than the
        # index being dragged. Snapping to the inch makes that easy to
        # hit, so hold the drag on the last handle rather than crash.
        last = len(self.handles) - 1
        if self.drag is not None:
            self.drag = min(self.drag, last)
        if self.hover is not None:
            self.hover = min(self.hover, last)
        self.readout = self._readout_for(context, self.drag)

    # -- modal ---------------------------------------------------------
    def invoke(self, context, event):
        self.obj = context.active_object
        self.wall = backsplash.wall_of(self.obj)
        if self.wall is None:
            self.report({'WARNING'}, "This backsplash is not on a wall")
            return {'CANCELLED'}

        self.region = context.region
        self.hover = None
        self.drag = None
        self.readout = ""
        self._undo_segments = backsplash.segments_of(self.obj)
        self._undo_z0 = self.obj.get('bs_z0', 0.0)
        self._rebuild_handles()

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_edit, (self,), 'WINDOW', 'POST_PIXEL')
        context.workspace.status_text_set(
            "Hover an edge to highlight it, then drag   |   "
            "Ctrl: snap to the inch   |   Enter: done   |   Esc: cancel")
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            self._rebuild_handles()
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if self.drag is not None:
                self._apply(context, event)
            else:
                self.hover = self._pick(context, event)
                self.readout = self._readout_for(context, self.hover)
                self._set_cursor(context)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                picked = self._pick(context, event)
                if picked is None:
                    return self._finish(context)
                if picked >= len(self.handles):
                    return {'RUNNING_MODAL'}
                self.drag = picked
                self.hover = picked
                return {'RUNNING_MODAL'}
            if event.value == 'RELEASE' and self.drag is not None:
                self.drag = None
                self.readout = ""
                context.area.tag_redraw()
                return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            return self._finish(context)

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            backsplash.set_segments(self.obj, self._undo_segments)
            self.obj['bs_z0'] = self._undo_z0
            backsplash.rebuild(self.obj)
            return self._finish(context, cancelled=True)

        return {'RUNNING_MODAL'}

    def _finish(self, context, cancelled=False):
        if self._draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(
                self._draw_handle, 'WINDOW')
            self._draw_handle = None
        context.workspace.status_text_set(None)
        context.window.cursor_modal_restore()
        if context.area:
            context.area.tag_redraw()
        return {'CANCELLED'} if cancelled else {'FINISHED'}


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def _mat_look_items(self, context):
    return sm.look_items(self.style)


def _mat_style_changed(self, context):
    self.look = sm.DEFAULT_LOOK.get(self.style, 'CUSTOM')
    self.roughness = sm.DEFAULT_ROUGHNESS.get(self.style, 0.3)
    _mat_look_changed(self, context)


def _mat_look_changed(self, context):
    base, accent = _look_colors(self.style, self.look)
    if base is not None:
        self.color = base
        self.accent = accent


def _mat_format_changed(self, context):
    fmt = sm.TILE_FORMATS.get(self.tile_format)
    if fmt and fmt[1]:
        self.tile_width = fmt[1]
        self.tile_height = fmt[2]
        self.running_bond = fmt[3]


class HOME_BUILDER_OT_surface_material(bpy.types.Operator):
    bl_idname = "home_builder.surface_material"
    bl_label = "Surface Material"
    bl_description = ("Give backsplashes and countertops a material -- tile, "
                      "stone, wood or a flat color, or one already in this "
                      "file")
    bl_options = {'REGISTER', 'UNDO'}

    target: EnumProperty(
        name="Apply To", default='SELECTED',
        items=[('SELECTED', "Selected", "The selected surfaces", 'RESTRICT_SELECT_OFF', 0),
               ('BACKSPLASH', "All Backsplashes", "Every backsplash in the room", 'MESH_GRID', 1),
               ('COUNTERTOP', "All Countertops", "Every countertop in the room", 'MESH_PLANE', 2)])
    style: EnumProperty(name="Style", default='TILE',
                        items=sm.SURFACE_STYLE_ITEMS,
                        update=_mat_style_changed)
    look: EnumProperty(name="Look", items=_mat_look_items,
                       update=_mat_look_changed)
    material_name: StringProperty(
        name="Material",
        description="A material already in this file. Drag one in from "
                    "the Materials content library to get it here")
    color: FloatVectorProperty(
        name="Color", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.94, 0.94, 0.92))
    accent: FloatVectorProperty(
        name="Accent", subtype='COLOR_GAMMA', size=3, min=0.0, max=1.0,
        default=(0.80, 0.79, 0.76),
        description="Grout for tile, vein for stone, the darker board "
                    "tone for wood")
    tile_format: EnumProperty(name="Format", default='SUBWAY',
                              items=sm.format_items(),
                              update=_mat_format_changed)
    tile_width: FloatProperty(name="Tile Width", default=6 * sm.INCH,
                              min=0.005, max=2.0, unit='LENGTH', precision=4)
    tile_height: FloatProperty(name="Tile Height", default=3 * sm.INCH,
                               min=0.005, max=2.0, unit='LENGTH', precision=4)
    grout_size: FloatProperty(
        name="Grout", default=0.125 * sm.INCH, min=0.0005, max=0.02,
        unit='LENGTH', precision=4, description="Joint width between tiles")
    running_bond: BoolProperty(
        name="Running Bond", default=True,
        description="Offset every other row, the way subway tile is laid")
    roughness: FloatProperty(
        name="Roughness", default=0.15, min=0.0, max=1.0, subtype='FACTOR',
        description="0 = polished, 1 = matte")

    def invoke(self, context, event):
        picked = [o for o in context.selected_objects
                  if backsplash.is_backsplash(o)]
        if not picked and any(o.get('IS_COUNTERTOP')
                              for o in context.selected_objects):
            self.style = 'STONE'
            _mat_style_changed(self, context)
        return context.window_manager.invoke_props_dialog(self, width=340)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "target")
        col.prop(self, "style")

        if self.style == 'EXISTING':
            layout.prop_search(self, "material_name", bpy.data, "materials")
            layout.label(
                text="Add a material asset library for more to choose "
                     "from.", icon='INFO')
            return

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(self, "look")
        col.prop(self, "color")
        if self.style != 'SOLID':
            col.prop(self, "accent")
        if self.style == 'TILE':
            col.prop(self, "tile_format")
            sub = col.column(align=True)
            sub.enabled = self.tile_format == 'CUSTOM'
            sub.prop(self, "tile_width")
            sub.prop(self, "tile_height")
            col.prop(self, "grout_size")
            col.prop(self, "running_bond")
        elif self.style == 'WOOD':
            col.prop(self, "tile_height", text="Board Width")
        col.prop(self, "roughness")

    def _targets(self, context):
        if self.target == 'BACKSPLASH':
            return backsplash.existing(context)
        if self.target == 'COUNTERTOP':
            return [o for o in context.scene.objects
                    if o.get('IS_COUNTERTOP') and o.type == 'MESH']
        return [o for o in context.selected_objects
                if o.type == 'MESH'
                and (backsplash.is_backsplash(o) or o.get('IS_COUNTERTOP'))]

    def execute(self, context):
        targets = self._targets(context)
        if not targets:
            self.report({'WARNING'},
                        "Select a backsplash or a countertop first")
            return {'CANCELLED'}

        if self.style == 'EXISTING':
            mat = bpy.data.materials.get(self.material_name)
            if mat is None:
                self.report({'WARNING'}, "Pick a material")
                return {'CANCELLED'}
        else:
            # One material per kind of surface, rebuilt in place: trying
            # looks does not leave a pile of Backsplash.001 behind.
            only_tops = all(o.get('IS_COUNTERTOP') for o in targets)
            name = COUNTERTOP_MATERIAL if only_tops else SPLASH_MATERIAL
            mat = sm.build_surface_material(
                name, self.style, tuple(self.color), tuple(self.accent),
                self.roughness, tile_w=self.tile_width,
                tile_h=self.tile_height, running_bond=self.running_bond,
                grout_size=self.grout_size,
                **sm.stone_character(self.look))

        for obj in targets:
            sm.assign(obj, mat)
        self.report({'INFO'}, f"Materialled {len(targets)} surface(s)")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Right-click menu
# ---------------------------------------------------------------------------

def _operator_exists(idname):
    """Is this operator registered?

    Not hasattr: bpy.ops resolves lazily, so getattr succeeds for a
    module and an operator that do not exist -- hasattr on pure
    nonsense comes back True. get_rna_type is the call that actually
    goes and looks.
    """
    module, _, name = idname.partition('.')
    try:
        getattr(getattr(bpy.ops, module), name).get_rna_type()
        return True
    except (AttributeError, KeyError, TypeError):
        return False


class HOME_BUILDER_OT_delete_countertop(bpy.types.Operator):
    bl_idname = "home_builder.delete_countertop"
    bl_label = "Delete Countertop"
    bl_description = "Delete the selected countertops"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(o.get('IS_COUNTERTOP') for o in context.selected_objects)

    def execute(self, context):
        targets = [o for o in context.selected_objects if o.get('IS_COUNTERTOP')]
        if not targets:
            self.report({'WARNING'}, "No countertops selected")
            return {'CANCELLED'}
        count = len(targets)
        for obj in targets:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Deleted {count} countertop(s)")
        return {'FINISHED'}


class HOME_BUILDER_MT_countertop_commands(bpy.types.Menu):
    bl_label = "Countertop Commands"

    # Cut Hole belongs to whichever library built the top, so the tops
    # carry that stamp and the menu offers the matching command. Older
    # tops predate the stamp and fall back to face frame.
    _CUT = {
        'FACE_FRAME': 'hb_face_frame.countertop_boolean_cut',
        'FRAMELESS': 'hb_frameless.countertop_boolean_cut',
    }

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder.surface_material",
                        text="Countertop Material", icon='MATERIAL')
        layout.separator()
        obj = context.active_object
        library = (obj.get('HB_COUNTERTOP_LIB') if obj else None) or 'FACE_FRAME'
        cut = self._CUT.get(library)
        if cut and _operator_exists(cut):
            layout.operator(cut, text="Cut Hole (Select 2)", icon='MOD_BOOLEAN')
        layout.separator()
        layout.operator("home_builder.delete_countertop",
                        text="Delete Countertop", icon='X')


class HOME_BUILDER_MT_backsplash_commands(bpy.types.Menu):
    bl_label = "Backsplash Commands"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder.edit_backsplash", icon='EDITMODE_HLT')
        layout.operator("home_builder.backsplash_prompts", text="Backsplash Size",
                        icon='DRIVER_DISTANCE')
        layout.separator()
        layout.operator("home_builder.surface_material", icon='MATERIAL')
        layout.separator()
        layout.operator("home_builder.remove_backsplash", text="Delete Backsplash",
                        icon='X')


classes = [
    HOME_BUILDER_OT_add_backsplash,
    HOME_BUILDER_OT_delete_countertop,
    HOME_BUILDER_MT_countertop_commands,
    HOME_BUILDER_OT_remove_backsplash,
    HOME_BUILDER_OT_backsplash_prompts,
    HOME_BUILDER_OT_edit_backsplash,
    HOME_BUILDER_OT_surface_material,
    HOME_BUILDER_MT_backsplash_commands,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
