"""Editable dimension overlay for walls and placed doors / windows.

While a wall or a door/window cage (or any of its generated geometry
children) is selected in a room scene, a POST_PIXEL draw handler paints
value labels on it:

- Door / window: width, height, and the offsets to each end of its
  wall; windows also show the sill height (height from floor) and a
  dashed centerline with its distance to each end of the wall.
- Wall: length and height.

Each value label sits on a ticked dimension line (orange for a
window's centerline).
- Entry door with built 3D geometry: an Open / Close button that swings
  the leaf, the quick version of the door prompts' Open Angle -- the
  same idea as Open Door mode for cabinet fronts.

Clicking a label starts a short-lived modal that captures typed input
(the placement typing grammar: inches, fractions, feet'inches");
Enter commits. Commits write through the same paths the prompts
dialogs use -- cage Dim X/Z inputs and location, wall Length / Height
inputs -- and rebuild the door/window's 3D geometry, so the overlay,
the sidebar and the dialogs can never disagree.

Architecture mirrors face_frame/dim_edit_overlay.py (which itself
mirrors viewport_hud): a permanent draw handler plus an addon-keymap
click operator that PASS_THROUGHs anything that isn't a label hit, so
selection and other tools are untouched and no persistent modal blocks
autosave. The label list is recomputed on click rather than cached, so
draw and hit-test can never drift apart. Selection is the only gate --
no labels draw unless a wall / opening is part of the selection.
"""

import bpy
import blf
import gpu
from mathutils import Vector
from bpy_extras import view3d_utils

from .. import hb_placement, hb_types, hb_utils, units
from ..units import inch
from ..product_libraries.common import door_window_geo

# ---- Style (matches face_frame/dim_edit_overlay.py) ----------------------

FONT_SIZE       = 12
PAD_X           = 6
PAD_Y           = 4
LABEL_BG        = (0.13, 0.13, 0.14, 0.85)
LABEL_BORDER    = (1.0, 1.0, 1.0, 0.25)
EDIT_BG         = (0.20, 0.43, 0.70, 0.95)
ACTION_BG       = (0.20, 0.43, 0.70, 0.75)   # a label that is a button
TEXT_COLOR      = (0.95, 0.95, 0.95, 1.0)
EDIT_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
DIM_LINE_COLOR  = (0.90, 0.90, 0.90, 0.80)
CL_COLOR        = (1.0, 0.56, 0.16, 0.95)
CL_BORDER       = (1.0, 0.56, 0.16, 0.55)
CL_TEXT_COLOR   = (1.0, 0.70, 0.40, 1.0)
CL_DASH_PX      = 8
CL_TICK_PX      = 5
# Labels drawn beside their anchor, not centered on it: the wall
# height sits just left of its dim line up the wall's base point.
_LEFT_OF_ANCHOR_KINDS = {'WALL_H'}

# Window centerline dims: drawn with an orange dimension line.
_CL_KINDS = {'CAGE_CL_L', 'CAGE_CL_R'}

_INPUT_CHARS = set("0123456789./-'\" ")

# Label kinds that run a command on click instead of opening for typing.
_ACTION_KINDS = {'DOOR_OPEN'}
DOOR_OPEN_DEG = 90.0

# ---- Module state --------------------------------------------------------

_draw_handle = None
_shutdown = False
# Active edit: {'name': object name, 'kind': label kind, 'typed': str,
# 'owner': id(modal)} or None; written by the edit modal, read by the
# draw handler so the edited label renders as an input field.
_edit = None
_addon_keymaps = []


class _DistanceParser:
    parse_typed_distance = hb_placement.PlacementMixin.parse_typed_distance
    _parse_feet_inches = hb_placement.PlacementMixin._parse_feet_inches
    _extract_number = hb_placement.PlacementMixin._extract_number
    _number_to_scene_units = hb_placement.PlacementMixin._number_to_scene_units
    typed_value = ""


_parser = _DistanceParser()


def parse_distance(text):
    """Typed string -> metres, or None. Same grammar as placement typing."""
    try:
        return _parser.parse_typed_distance(text)
    except Exception:
        return None


# ---- Gating / target collection ------------------------------------------

# Product roots that sit on (are parented to) walls. A selection inside
# one of these belongs to the product, not the wall -- without this
# check, selecting any cabinet placed on a wall walked up to the wall
# BP and painted the wall's length/height labels. Shared, because the
# room collection sorter has to draw the same line.
_PRODUCT_ROOT_TAGS = hb_utils.PRODUCT_ROOT_TAGS


def _resolve_target(obj):
    """('CAGE'|'WALL', bp_object) for ``obj`` or its nearest tagged
    ancestor, else None. A door/window cage resolves before its wall,
    so selecting an opening (or its geometry) never labels the wall;
    a placed product resolves to nothing, so the wall labels only
    show when the wall's own geometry is selected."""
    node = obj
    while node is not None:
        if node.get('IS_ENTRY_DOOR_BP') or node.get('IS_WINDOW_BP'):
            return ('CAGE', node)
        if any(node.get(tag) for tag in _PRODUCT_ROOT_TAGS):
            return None
        if node.get('IS_WALL_BP'):
            return ('WALL', node)
        node = node.parent
    return None


def _selected_targets(context):
    """{name: (tag, obj)} resolved from the current selection + active
    object. Empty outside room scenes."""
    scene = context.scene
    if scene is None or scene.get('IS_LAYOUT_VIEW') \
            or scene.get('IS_DETAIL_VIEW'):
        return {}
    targets = {}
    objs = list(getattr(context, 'selected_objects', ()) or ())
    act = getattr(context, 'active_object', None)
    if act is not None and act not in objs:
        objs.append(act)
    for obj in objs:
        hit = _resolve_target(obj)
        if hit is not None:
            targets[hit[1].name] = hit
    return targets


# ---- Label collection ----------------------------------------------------

def _cage_label_targets(cage_obj):
    """[(kind, value, prefix, local_anchor)] for one door/window cage
    in cage-local space (x along the wall, z up)."""
    cage = hb_types.GeoNodeCage(cage_obj)
    if not cage.has_modifier():
        return []
    try:
        w = cage.get_input('Dim X')
        h = cage.get_input('Dim Z')
    except Exception:
        return []
    out = [
        ('CAGE_W', w, "W ", Vector((w / 2.0, 0.0, h + inch(3.0)))),
        ('CAGE_H', h, "H ", Vector((inch(3.0), 0.0, h / 2.0))),
    ]
    # An entry door with a built leaf gets an Open / Close button at
    # its centre. A cage-only door has nothing to swing, so no button.
    if cage_obj.get('IS_ENTRY_DOOR_BP'):
        opts = door_window_geo.merged_opts(cage_obj)
        if opts is not None:
            is_open = float(opts.get('open_angle', 0.0)) > 0.0
            out.append(('DOOR_OPEN', None, "Close" if is_open else "Open",
                        Vector((w / 2.0, 0.0, h / 2.0))))
    if cage_obj.get('IS_WINDOW_BP') and cage_obj.location.z > inch(0.25):
        out.append(('CAGE_SILL', cage_obj.location.z, "S ",
                    Vector((w / 2.0, 0.0, -cage_obj.location.z / 2.0))))
    wall_obj = cage_obj.parent
    if wall_obj is not None and wall_obj.get('IS_WALL_BP'):
        wall = hb_types.GeoNodeWall(wall_obj)
        if wall.has_modifier():
            try:
                wall_len = wall.get_input('Length')
            except Exception:
                wall_len = 0.0
            gap_l = cage_obj.location.x
            gap_r = wall_len - cage_obj.location.x - w
            if gap_l > inch(0.5):
                out.append(('CAGE_OFF_L', gap_l, "← ",
                            Vector((-gap_l / 2.0, 0.0, h / 2.0))))
            if gap_r > inch(0.5):
                out.append(('CAGE_OFF_R', gap_r, "→ ",
                            Vector((w + gap_r / 2.0, 0.0, h / 2.0))))
            if cage_obj.get('IS_WINDOW_BP') and wall_len > 0.0:
                # Centerline to each wall end, along the window's bottom
                # edge so the labels clear the gap labels above.
                cl_l = gap_l + w / 2.0
                cl_r = gap_r + w / 2.0
                out.append(('CAGE_CL_L', cl_l, "CL ← ",
                            Vector((w / 2.0 - cl_l / 2.0, 0.0, 0.0))))
                out.append(('CAGE_CL_R', cl_r, "CL → ",
                            Vector((w / 2.0 + cl_r / 2.0, 0.0, 0.0))))
    return out


def _dim_segments(context, region, rv3d, s=1.0):
    """Region-space line endpoints ``(dims, centerline)`` for each
    selected wall / door / window, drawn under its labels so every value
    reads as a dimension. A wall gets its length (above the top) and
    height (up its base point, label to the left). A door / window
    gets a ticked line for the width (above the head), height (up the
    left jamb), the gap from each wall end (at mid
    height) and a window's sill (floor to sill). A window adds its
    centerline -- dashed from below the sill to above the head -- and a
    ticked line from each wall end to it along the window's bottom
    edge, where the CL labels sit."""
    dims = []
    cls = []
    for tag, obj in _selected_targets(context).values():
        mw = obj.matrix_world

        def to2d(x, z):
            return view3d_utils.location_3d_to_region_2d(
                region, rv3d, mw @ Vector((x, 0.0, z)))

        def dim(out, x0, z0, x1, z1):
            a = to2d(x0, z0)
            b = to2d(x1, z1)
            if a is None or b is None:
                return
            d = b - a
            if d.length < 1e-6:
                return
            tick = Vector((-d.y, d.x)).normalized() * CL_TICK_PX * s
            for p in (a, b, a - tick, a + tick, b - tick, b + tick):
                out.append(tuple(p))

        if tag == 'WALL':
            wall = hb_types.GeoNodeWall(obj)
            if not wall.has_modifier():
                continue
            try:
                length = wall.get_input('Length')
                height = wall.get_input('Height')
            except Exception:
                continue
            # Same anchors as _wall_label_targets.
            dim(dims, 0.0, height + inch(3.0), length, height + inch(3.0))
            dim(dims, 0.0, 0.0, 0.0, height)
            continue
        if tag != 'CAGE':
            continue
        cage = hb_types.GeoNodeCage(obj)
        if not cage.has_modifier():
            continue
        try:
            w = cage.get_input('Dim X')
            h = cage.get_input('Dim Z')
        except Exception:
            continue
        is_window = bool(obj.get('IS_WINDOW_BP'))

        dim(dims, 0.0, h + inch(3.0), w, h + inch(3.0))
        dim(dims, inch(3.0), 0.0, inch(3.0), h)
        if is_window and obj.location.z > inch(0.25):
            dim(dims, w / 2.0, -obj.location.z, w / 2.0, 0.0)

        wall_len = None
        wall_obj = obj.parent
        if wall_obj is not None and wall_obj.get('IS_WALL_BP'):
            wall = hb_types.GeoNodeWall(wall_obj)
            if wall.has_modifier():
                try:
                    wall_len = wall.get_input('Length')
                except Exception:
                    wall_len = None
        left_end = -obj.location.x
        if wall_len is not None:
            right_end = wall_len - obj.location.x
            # Same gates as the gap labels in _cage_label_targets.
            if obj.location.x > inch(0.5):
                dim(dims, left_end, h / 2.0, 0.0, h / 2.0)
            if right_end - w > inch(0.5):
                dim(dims, w, h / 2.0, right_end, h / 2.0)

        if not is_window:
            continue
        a = to2d(w / 2.0, -inch(2.0))
        b = to2d(w / 2.0, h + inch(6.0))
        if a is not None and b is not None:
            d = b - a
            length = d.length
            if length > 1e-6:
                dash = CL_DASH_PX * s
                step = d / length * dash
                n = int(length / dash)
                for i in range(0, n, 2):
                    cls.append(tuple(a + step * i))
                    cls.append(tuple(a + step * min(i + 1, length / dash)))
        if wall_len is not None and wall_len > 0.0:
            dim(cls, left_end, 0.0, w / 2.0, 0.0)
            dim(cls, w / 2.0, 0.0, right_end, 0.0)
    return dims, cls


def _wall_label_targets(wall_obj):
    wall = hb_types.GeoNodeWall(wall_obj)
    if not wall.has_modifier():
        return []
    try:
        length = wall.get_input('Length')
        height = wall.get_input('Height')
    except Exception:
        return []
    return [
        ('WALL_LEN', length, "L ",
         Vector((length / 2.0, 0.0, height + inch(3.0)))),
        ('WALL_H', height, "H ",
         Vector((0.0, 0.0, height / 2.0))),
    ]


def _resolve_overlap(rect, existing, gap):
    """Shift ``rect`` downward until it clears every already-placed
    label rect. In head-on views (plan view of a wall, elevation of a
    tall stack) several anchors project to the same screen point; the
    labels stack below each other instead of piling up. Applied inside
    compute_labels so drawing and click hit-testing stay identical."""
    x, y, w, h = rect
    for _ in range(16):
        hit = None
        for _name, _kind, (ex, ey, ew, eh), _text in existing:
            if x < ex + ew and ex < x + w and y < ey + eh and ey < y + h:
                hit = (ex, ey, ew, eh)
                break
        if hit is None:
            break
        y = hit[1] - h - gap
    return (x, y, w, h)


def compute_labels(context, region, rv3d):
    """[(obj_name, kind, rect, text)] for every label currently on
    screen; rect is (x, y, w, h) region-local. Overlapping labels are
    stacked vertically (see _resolve_overlap). Shared by the draw
    handler and the click operator so hits can't drift from pixels."""
    if rv3d is None:
        return []
    targets = _selected_targets(context)
    if not targets:
        return []
    unit_settings = context.scene.unit_settings
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    blf.size(0, FONT_SIZE * s)

    labels = []
    for name, (tag, obj) in targets.items():
        rows = (_cage_label_targets(obj) if tag == 'CAGE'
                else _wall_label_targets(obj))
        mw = obj.matrix_world
        for kind, value, prefix, local in rows:
            anchor = mw @ local
            pt = view3d_utils.location_3d_to_region_2d(region, rv3d, anchor)
            if pt is None:
                continue
            # Action labels carry their caption in the prefix and no value.
            text = prefix if value is None \
                else prefix + units.unit_to_string(unit_settings, value)
            tw, th = blf.dimensions(0, text)
            w = tw + 2 * PAD_X * s
            h = th + 2 * PAD_Y * s
            if kind in _LEFT_OF_ANCHOR_KINDS:
                rect = (pt.x - w - PAD_X * s, pt.y - h / 2.0, w, h)
            else:
                rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
            if rect[0] + w < 0 or rect[0] > region.width:
                continue
            if rect[1] + h < 0 or rect[1] > region.height:
                continue
            rect = _resolve_overlap(rect, labels, 2.0 * s)
            labels.append((name, kind, rect, text))
    return labels


# ---- Draw handler --------------------------------------------------------

def _draw_label_rect(shader, rect, bg, border=LABEL_BORDER):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    from gpu_extras.batch import batch_for_shader
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", border)
    batch_for_shader(shader, 'LINE_LOOP', {"pos": verts}).draw(shader)


def _draw():
    """Permanent POST_PIXEL callback; cheap no-op with nothing selected."""
    if _shutdown:
        return
    context = bpy.context
    area = context.area
    region = context.region
    if area is None or area.type != 'VIEW_3D':
        return
    if region is None or region.type != 'WINDOW':
        return
    labels = compute_labels(context, region, context.region_data)
    if not labels:
        return
    s = 1.0
    try:
        s = bpy.context.preferences.system.ui_scale
    except AttributeError:
        pass
    font_sz = FONT_SIZE * s
    gpu.state.blend_set('ALPHA')
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind()
    dim_pts, cl_pts = _dim_segments(context, region,
                                    context.region_data, s)
    from gpu_extras.batch import batch_for_shader
    for pts, color in ((dim_pts, DIM_LINE_COLOR), (cl_pts, CL_COLOR)):
        if pts:
            shader.uniform_float("color", color)
            batch_for_shader(shader, 'LINES', {"pos": pts}).draw(shader)
    for name, kind, rect, text in labels:
        editing = (_edit is not None and _edit['name'] == name
                   and _edit['kind'] == kind)
        if editing:
            typed = _edit['typed']
            shown = (typed + "|") if typed else text
            blf.size(0, font_sz)
            tw, _th = blf.dimensions(0, shown)
            w = max(rect[2], tw + 2 * PAD_X * s)
            rect = (rect[0], rect[1], w, rect[3])
            _draw_label_rect(shader, rect, EDIT_BG)
            blf.color(0, *EDIT_TEXT_COLOR)
        else:
            is_cl = kind in _CL_KINDS
            _draw_label_rect(shader, rect,
                             ACTION_BG if kind in _ACTION_KINDS else LABEL_BG,
                             CL_BORDER if is_cl else LABEL_BORDER)
            blf.size(0, font_sz)
            blf.color(0, *(CL_TEXT_COLOR if is_cl else TEXT_COLOR))
        blf.position(0, rect[0] + PAD_X * s, rect[1] + PAD_Y * s, 0)
        blf.draw(0, text if not editing else shown)
    gpu.state.blend_set('NONE')


# ---- Commit --------------------------------------------------------------

def _commit(obj, kind, value):
    """Write the typed value through the same paths the prompts dialogs
    use; cage size / position edits rebuild the 3D geometry."""
    if kind == 'WALL_LEN':
        hb_types.GeoNodeWall(obj).set_input('Length', max(value, inch(1.0)))
        return True
    if kind == 'WALL_H':
        hb_types.GeoNodeWall(obj).set_input('Height', max(value, inch(6.0)))
        return True

    cage = hb_types.GeoNodeCage(obj)
    if not cage.has_modifier():
        return False
    wall_len = None
    wall_obj = obj.parent
    if wall_obj is not None and wall_obj.get('IS_WALL_BP'):
        wall = hb_types.GeoNodeWall(wall_obj)
        if wall.has_modifier():
            try:
                wall_len = wall.get_input('Length')
            except Exception:
                wall_len = None
    width = cage.get_input('Dim X')

    if kind == 'CAGE_W':
        value = max(value, inch(4.0))
        cage.set_input('Dim X', value)
        if wall_len is not None:
            obj.location.x = max(0.0, min(obj.location.x, wall_len - value))
    elif kind == 'CAGE_H':
        cage.set_input('Dim Z', max(value, inch(4.0)))
    elif kind == 'CAGE_SILL':
        obj.location.z = max(value, 0.0)
    elif kind == 'CAGE_OFF_L':
        if wall_len is None:
            return False
        obj.location.x = max(0.0, min(value, wall_len - width))
    elif kind == 'CAGE_OFF_R':
        if wall_len is None:
            return False
        obj.location.x = max(0.0, min(wall_len - width - value,
                                      wall_len - width))
    elif kind == 'CAGE_CL_L':
        if wall_len is None:
            return False
        obj.location.x = max(0.0, min(value - width / 2.0,
                                      wall_len - width))
    elif kind == 'CAGE_CL_R':
        if wall_len is None:
            return False
        obj.location.x = max(0.0, min(wall_len - value - width / 2.0,
                                      wall_len - width))
    else:
        return False
    door_window_geo.build_geometry(obj)
    return True


# ---- Door open / close ---------------------------------------------------

class home_builder_OT_toggle_entry_door(bpy.types.Operator):
    """Swing the entry door open, or close it if it is already open.
    Writes the door's Open Angle option and rebuilds its geometry, the
    same path the door prompts use."""
    bl_idname = "home_builder.toggle_entry_door"
    bl_label = "Open / Close Entry Door"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if obj is None or not obj.get('IS_ENTRY_DOOR_BP'):
            return {'CANCELLED'}
        opts = door_window_geo.merged_opts(obj)
        if opts is None:
            return {'CANCELLED'}
        is_open = float(opts.get('open_angle', 0.0)) > 0.0
        opts['open_angle'] = 0.0 if is_open else DOOR_OPEN_DEG
        door_window_geo.set_opts(obj, opts)
        door_window_geo.build_geometry(obj)
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}


# ---- Edit modal ----------------------------------------------------------

class home_builder_OT_edit_room_dim_label(bpy.types.Operator):
    """Type a new value for the clicked wall / door / window label.
    Enter commits, Esc / right-click / click-away cancels."""
    bl_idname = "home_builder.edit_room_dim_label"
    bl_label = "Edit Room Dimension Label"
    bl_options = {'INTERNAL', 'UNDO'}

    target_name: bpy.props.StringProperty(options={'HIDDEN'})  # type: ignore
    kind: bpy.props.EnumProperty(
        items=[('CAGE_W', "Width", ""), ('CAGE_H', "Height", ""),
               ('CAGE_SILL', "Sill Height", ""),
               ('CAGE_OFF_L', "Offset Left", ""),
               ('CAGE_OFF_R', "Offset Right", ""),
               ('CAGE_CL_L', "Centerline From Left", ""),
               ('CAGE_CL_R', "Centerline From Right", ""),
               ('WALL_LEN', "Wall Length", ""),
               ('WALL_H', "Wall Height", "")],
        options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        global _edit
        if bpy.data.objects.get(self.target_name) is None:
            return {'CANCELLED'}
        _edit = {'name': self.target_name, 'kind': self.kind, 'typed': "",
                 'owner': id(self)}
        context.window_manager.modal_handler_add(self)
        context.window.cursor_set('TEXT')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        global _edit
        _edit = None
        try:
            context.window.cursor_set('DEFAULT')
        except Exception:
            pass
        if context.area:
            context.area.tag_redraw()

    def modal(self, context, event):
        global _edit
        if _edit is None or _edit.get('owner') != id(self):
            return {'CANCELLED'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                          'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TIMER'}:
            return {'PASS_THROUGH'}

        if event.value != 'PRESS':
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'}:
            typed = _edit['typed']
            obj = bpy.data.objects.get(self.target_name)
            if not typed:
                self._finish(context)
                return {'FINISHED'}
            value = parse_distance(typed)
            # 0 is meaningful here (an offset or sill can be 0), so
            # only reject unparseable input -- unlike the face-frame
            # overlay, there is no reset-to-auto concept.
            if obj is None or value is None or value < 0.0:
                self.report({'WARNING'},
                            f"Could not read '{typed}' as a distance")
                self._finish(context)
                return {'CANCELLED'}
            self._finish(context)
            _commit(obj, self.kind, value)
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE':
            self._finish(context)
            return {'CANCELLED'}

        if event.type == 'BACK_SPACE':
            _edit['typed'] = _edit['typed'][:-1]
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        ch = event.unicode
        if ch and ch in _INPUT_CHARS:
            _edit['typed'] += ch
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}


# ---- Click routing (addon keymap, mirrors viewport_hud) -------------------

class home_builder_OT_room_dim_label_click(bpy.types.Operator):
    """Routes a viewport left-press to overlay labels. A press on a
    label starts the edit modal and is consumed; anything else passes
    through untouched."""
    bl_idname = "home_builder.room_dim_label_click"
    bl_label = "Room Dimension Label Click"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (not _shutdown
                and context.area is not None
                and context.area.type == 'VIEW_3D'
                and context.region is not None
                and context.region.type == 'WINDOW'
                and bool(_selected_targets(context)))

    def invoke(self, context, event):
        if _edit is not None:
            # An edit is already running; its own modal handles this press.
            return {'PASS_THROUGH'}
        try:
            from . import viewport_hud
            if viewport_hud.click_hits_widget(
                    context, context.area,
                    event.mouse_region_x, event.mouse_region_y):
                return {'PASS_THROUGH'}
        except Exception:
            pass
        mx, my = event.mouse_region_x, event.mouse_region_y
        for name, kind, rect, _text in compute_labels(
                context, context.region, context.region_data):
            x, y, w, h = rect
            if not (x <= mx <= x + w and y <= my <= y + h):
                continue
            if kind == 'DOOR_OPEN':
                bpy.ops.home_builder.toggle_entry_door(target_name=name)
                return {'FINISHED'}
            bpy.ops.home_builder.edit_room_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


# ---- Lifecycle -----------------------------------------------------------

classes = (
    home_builder_OT_toggle_entry_door,
    home_builder_OT_edit_room_dim_label,
    home_builder_OT_room_dim_label_click,
)


def _register_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(
        home_builder_OT_room_dim_label_click.bl_idname, 'LEFTMOUSE',
        'PRESS', any=True, head=True)
    _addon_keymaps.append((km, kmi))


def _unregister_keymaps():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()


def register():
    global _draw_handle, _shutdown
    _shutdown = False
    for cls in classes:
        bpy.utils.register_class(cls)
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
        _draw, (), 'WINDOW', 'POST_PIXEL')
    _register_keymaps()


def unregister():
    global _draw_handle, _shutdown, _edit
    _shutdown = True
    _edit = None
    _unregister_keymaps()
    if _draw_handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        except Exception:
            pass
        _draw_handle = None
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
