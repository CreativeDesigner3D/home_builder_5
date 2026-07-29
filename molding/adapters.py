"""Per-library fact providers for the molding engine.

The engine works on world geometry plus a FACTS dict; these adapters
read each library's property groups / tags and produce those facts, so
the engine itself stays library-agnostic. Both HB5 libraries are
covered: face frame and frameless.
"""

import bpy
import mathutils

from . import engine
from .. import hb_types


# Roots eligible per molding type, per library.
_CROWN_TYPES = ('UPPER', 'TALL')
_BASE_TYPES = ('BASE', 'TALL', 'LAP_DRAWER')
_RAIL_TYPES = ('UPPER',)


def _face_frame_roots(scene, types):
    out = []
    for obj in scene.objects:
        if not obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            continue
        ffc = getattr(obj, 'face_frame_cabinet', None)
        if ffc is None or ffc.cabinet_type not in types:
            continue
        out.append(obj)
    return out


def _frameless_roots(scene, types):
    out = []
    for obj in scene.objects:
        if not (obj.get('IS_FRAMELESS_CABINET_CAGE')
                or obj.get('IS_FRAMELESS_PRODUCT_CAGE')):
            continue
        if obj.get('CABINET_TYPE', '') not in types:
            continue
        out.append(obj)
    return out


def collect_targets(scene, molding_type):
    """Eligible molding-carrying roots in the room, across both
    libraries. molding_type in {'CROWN', 'BASE', 'LIGHT_RAIL'}."""
    types = {'CROWN': _CROWN_TYPES,
             'CAP': _CROWN_TYPES,
             'BASE': _BASE_TYPES,
             'LIGHT_RAIL': _RAIL_TYPES}[molding_type]
    return _face_frame_roots(scene, types) + _frameless_roots(scene, types)


def collect_bridges(scene):
    """Floor-standing appliances that sit inside runs (dishwashers,
    ranges, freestanding refrigerators): they keep a run in one piece
    and contribute skip spans."""
    out = []
    for obj in scene.objects:
        if not obj.get('IS_APPLIANCE'):
            continue
        if obj.matrix_world.translation.z > 0.02:
            continue  # mounted at height (wall ovens, OTR microwaves)
        out.append(obj)
    return out


# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------

_RECESSED_FF_KICKS = {'NOTCH', 'LOOSE', 'FLOATING'}


def _top_rail_width(cage):
    """Width of the built TOP_RAIL face-frame part, read from the
    geometry rather than the style props - it's exactly what's drawn."""
    for child in cage.children_recursive:
        if child.get('hb_part_role') != 'TOP_RAIL':
            continue
        try:
            width = hb_types.GeoNodeObject(child).get_input('Width')
        except Exception:
            width = None
        if width:
            return width
    return None


def _wall_bounds(scene):
    bounds = []
    for wall in scene.objects:
        if not wall.get('IS_WALL_BP'):
            continue
        corners = [wall.matrix_world @ mathutils.Vector(c)
                   for c in wall.bound_box]
        xs = [c.x for c in corners]
        ys = [c.y for c in corners]
        bounds.append((min(xs), max(xs), min(ys), max(ys)))
    return bounds


def _near_wall(point_xy, wall_bounds, tolerance=0.05):
    for x0, x1, y0, y1 in wall_bounds:
        if (x0 - tolerance <= point_xy.x <= x1 + tolerance
                and y0 - tolerance <= point_xy.y <= y1 + tolerance):
            return True
    return False


def _frameless_end_finished(obj, side, wall_bounds):
    """Frameless has no per-end exposure props: an end reads finished
    (molding wraps it) when it is NOT against a wall."""
    width, depth, _ = engine.cage_dims(obj)
    mw = obj.matrix_world
    x = 0.0 if side == 'left' else width
    mid = mw @ mathutils.Vector((x, -depth / 2.0, 0.0))
    outward3 = mw.to_3x3() @ mathutils.Vector(
        (-1.0 if side == 'left' else 1.0, 0.0, 0.0))
    outward = mathutils.Vector((outward3.x, outward3.y))
    if outward.length > 1e-6:
        outward.normalize()
    probe = mathutils.Vector((mid.x, mid.y)) + outward * 0.03
    return not _near_wall(probe, wall_bounds)


def finish_material(obj):
    """The exterior finish material of the cabinet's assigned style,
    resolved through its library's style system. None for appliances
    or when no style / material resolves."""
    try:
        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            style_name = obj.get('STYLE_NAME')
            if not style_name:
                return None
            from ..product_libraries.face_frame import props_hb_face_frame
            ff = props_hb_face_frame.get_style_props()
            style = next((cs for cs in ff.cabinet_styles
                          if cs.name == style_name), None)
            if style is None:
                return None
            material, _rotated = style.get_finish_material()
            return material
        if (obj.get('IS_FRAMELESS_CABINET_CAGE')
                or obj.get('IS_FRAMELESS_PRODUCT_CAGE')):
            from .. import hb_project
            main = hb_project.get_main_scene()
            props = getattr(main, 'hb_frameless', None)
            if props is None or not props.cabinet_styles:
                return None
            index = obj.get('CABINET_STYLE_INDEX', 0)
            if not 0 <= index < len(props.cabinet_styles):
                return None
            material, _rotated = \
                props.cabinet_styles[index].get_finish_material()
            return material
    except Exception:
        return None
    return None


def build_facts(scene, members):
    """FACTS dict (keyed by id(obj)) for the engine, covering every
    member: role, corner data, kick config, finished ends."""
    wall_bounds = _wall_bounds(scene)
    facts = {}
    for obj in members:
        if obj.get('IS_APPLIANCE'):
            facts[id(obj)] = {'role': 'APPLIANCE', 'corner': None,
                              'kick': {'skip': True, 'setback': 0.0},
                              'finished_left': False,
                              'finished_right': False}
            continue

        if obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            ffc = obj.face_frame_cabinet
            corner = None
            if getattr(ffc, 'corner_type', 'NONE') != 'NONE':
                corner = {'ld': ffc.left_depth, 'rd': ffc.right_depth,
                          'diagonal': ffc.corner_type == 'DIAGONAL'}
            if obj.get('CLASS_NAME') == 'RefrigeratorCabinet':
                kick = {'skip': True, 'setback': 0.0}
            elif obj.get('IS_LEG_PRODUCT'):
                # Leg products keep their toe kick on the leg_product
                # propgroup (is_column / only_stile suppress it), not on
                # face_frame_cabinet - whose untouched 'NOTCH' default
                # read every leg as recessed. Columns and stile-only
                # legs run to the floor: flush front.
                leg = getattr(obj, 'leg_product', None)
                kick_active = (leg is not None and not leg.is_column
                               and not leg.only_stile
                               and leg.toe_kick_height > 0.0)
                kick = {'skip': False,
                        'setback': leg.toe_kick_setback if kick_active
                        else 0.0}
            elif ffc.toe_kick_type not in _RECESSED_FF_KICKS:
                kick = {'skip': False, 'setback': 0.0}
            else:
                kick = {
                    'skip': False,
                    'setback': ffc.toe_kick_setback,
                    'stile_left': ffc.extend_left_stile_to_floor,
                    'stile_right': ffc.extend_right_stile_to_floor,
                    'stile_left_w': ffc.left_stile_width,
                    'stile_right_w': ffc.right_stile_width,
                }
            fin_l = getattr(ffc, 'left_finished_end_condition',
                            'UNFINISHED') not in ('UNFINISHED', '', None)
            fin_r = getattr(ffc, 'right_finished_end_condition',
                            'UNFINISHED') not in ('UNFINISHED', '', None)
            # Crown mounting datum: the DOOR TOP (face-frame opening top
            # plus the door's top overlay). The room's crown reveal is
            # measured up from here, matching the crown detail drawing.
            crown_mount = None
            rail = _top_rail_width(obj)
            if rail:
                overlay = max(
                    getattr(ffc, 'default_top_overlay', 0.0) or 0.0, 0.0)
                crown_mount = {'rail_width': rail, 'door_overlay': overlay}
            facts[id(obj)] = {'role': 'CABINET', 'corner': corner,
                              'kick': kick,
                              'crown_mount': crown_mount,
                              'finished_left': fin_l,
                              'finished_right': fin_r}
            continue

        # Frameless (cabinet or product cage).
        corner = None
        if obj.get('IS_CORNER_CABINET'):
            corner = {'ld': obj.get('Left Depth'),
                      'rd': obj.get('Right Depth'),
                      'diagonal': obj.get('CORNER_TYPE') == 'DIAGONAL'}
        setback = obj.get('Toe Kick Setback', 0.0) or 0.0
        kick = {'skip': False, 'setback': setback}
        facts[id(obj)] = {
            'role': 'CABINET', 'corner': corner, 'kick': kick,
            'finished_left': _frameless_end_finished(obj, 'left',
                                                     wall_bounds),
            'finished_right': _frameless_end_finished(obj, 'right',
                                                      wall_bounds),
        }
    return facts
