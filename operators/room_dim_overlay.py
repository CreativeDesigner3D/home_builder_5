"""Editable dimension overlay for walls and placed doors / windows.

While a wall or a door/window cage (or any of its generated geometry
children) is selected in a room scene, a POST_PIXEL draw handler paints
value labels on it:

- Door / window: width, height, and the offsets to each end of its
  wall; windows also show the sill height (height from floor).
- Wall: length and height.

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

from .. import hb_placement, hb_types, units
from ..units import inch
from ..product_libraries.common import door_window_geo

# ---- Style (matches face_frame/dim_edit_overlay.py) ----------------------

FONT_SIZE       = 12
PAD_X           = 6
PAD_Y           = 4
LABEL_BG        = (0.13, 0.13, 0.14, 0.85)
LABEL_BORDER    = (1.0, 1.0, 1.0, 0.25)
EDIT_BG         = (0.20, 0.43, 0.70, 0.95)
TEXT_COLOR      = (0.95, 0.95, 0.95, 1.0)
EDIT_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)

_INPUT_CHARS = set("0123456789./-'\" ")

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

def _resolve_target(obj):
    """('CAGE'|'WALL', bp_object) for ``obj`` or its nearest tagged
    ancestor, else None. A door/window cage resolves before its wall,
    so selecting an opening (or its geometry) never labels the wall."""
    node = obj
    while node is not None:
        if node.get('IS_ENTRY_DOOR_BP') or node.get('IS_WINDOW_BP'):
            return ('CAGE', node)
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
    return out


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
         Vector((length / 2.0, 0.0, height / 2.0))),
    ]


def compute_labels(context, region, rv3d):
    """[(obj_name, kind, rect, text)] for every label currently on
    screen; rect is (x, y, w, h) region-local. Shared by the draw
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
            text = prefix + units.unit_to_string(unit_settings, value)
            tw, th = blf.dimensions(0, text)
            w = tw + 2 * PAD_X * s
            h = th + 2 * PAD_Y * s
            rect = (pt.x - w / 2.0, pt.y - h / 2.0, w, h)
            if rect[0] + w < 0 or rect[0] > region.width:
                continue
            if rect[1] + h < 0 or rect[1] > region.height:
                continue
            labels.append((name, kind, rect, text))
    return labels


# ---- Draw handler --------------------------------------------------------

def _draw_label_rect(shader, rect, bg):
    x, y, w, h = rect
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    from gpu_extras.batch import batch_for_shader
    shader.uniform_float("color", bg)
    batch_for_shader(shader, 'TRI_FAN', {"pos": verts}).draw(shader)
    shader.uniform_float("color", LABEL_BORDER)
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
            _draw_label_rect(shader, rect, LABEL_BG)
            blf.size(0, font_sz)
            blf.color(0, *TEXT_COLOR)
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
    else:
        return False
    door_window_geo.build_geometry(obj)
    return True


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
            bpy.ops.home_builder.edit_room_dim_label(
                'INVOKE_DEFAULT', target_name=name, kind=kind)
            return {'FINISHED'}
        return {'PASS_THROUGH'}


# ---- Lifecycle -----------------------------------------------------------

classes = (
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
