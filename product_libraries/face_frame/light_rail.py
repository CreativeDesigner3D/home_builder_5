"""Room light rail: grow the bottom rail of a room's upper cabinets.

The room's Light Rail settings (Molding section) set one bottom rail
height for every hanging upper in the room, and optionally drop the
bottom-row doors so they cover the taller rail and keep the same bottom
reveal as an upper without a light rail. A cabinet can opt out with its
exclude_light_rail toggle.

The rail and overlays are written through the cabinet's own unlock
props (unlock_bottom_rail, each opening's unlock_bottom_overlay, a
diagonal section's unlock_bottom_overlay), so style changes and recalcs
keep them. Every value changed is recorded first in the cabinet's
LIGHT_RAIL_STAMP, and apply_room_light_rail restores exactly those
values before re-applying -- turning the room setting off, excluding a
cabinet, or moving an upper onto the counter puts the cabinet back the
way it was.

The stamp is also the record downstream consumers read: height, whether
the doors cover the rail, the covered openings and the covered diagonal
section door count.
"""

import bpy

from ... import units

LIGHT_RAIL_STAMP = 'HB_LIGHT_RAIL'
# An upper whose bottom sits below this rests on the countertop (a hutch
# or appliance garage); its bottom rail is not a light rail.
MIN_MOUNT_HEIGHT = units.inch(42.0)
_EPS = units.inch(1.0 / 64.0)


def _room_settings(scene):
    hb = getattr(scene, 'home_builder', None)
    if hb is None:
        return 0.0, False
    return (float(getattr(hb, 'molding_light_rail_height', 0.0) or 0.0),
            bool(getattr(hb, 'molding_light_rail_doors_cover', False)))


def _scene_uppers(scene):
    from . import types_face_frame
    out = []
    for obj in scene.objects:
        if not obj.get('IS_FACE_FRAME_CABINET_CAGE'):
            continue
        props = getattr(obj, 'face_frame_cabinet', None)
        if props is None or props.cabinet_type != 'UPPER':
            continue
        if types_face_frame.find_cabinet_root(obj) is not obj:
            continue
        out.append(obj)
    return out


def _style_bottom_rail(cab):
    """The cabinet style's upper bottom rail, or None."""
    name = cab.get('STYLE_NAME')
    if not name:
        return None
    try:
        from .props_hb_face_frame import get_style_props
        cs = next((c for c in get_style_props().cabinet_styles
                   if c.name == name), None)
    except Exception:
        cs = None
    return getattr(cs, 'ff_bottom_rail_width_upper', None) if cs else None


def _bottom_row_openings(cab):
    """Opening cage objects along the bottom of each bay whose own bottom
    rail follows the cabinet (a bay with its own rail is left alone)."""
    from . import solver_face_frame
    out = []
    try:
        layout = solver_face_frame.FaceFrameLayout(cab)
    except Exception:
        return out
    for bay_obj in cab.children:
        if not bay_obj.get('IS_FACE_FRAME_BAY_CAGE'):
            continue
        ffb = getattr(bay_obj, 'face_frame_bay', None)
        bi = bay_obj.get('hb_bay_index')
        if ffb is None or bi is None or ffb.unlock_bottom_rail:
            continue
        try:
            leaves = solver_face_frame.bay_openings(layout, bi)['leaves']
        except Exception:
            continue
        if not leaves:
            continue
        min_z = min(lf['cage_z'] for lf in leaves)
        for lf in leaves:
            if abs(lf['cage_z'] - min_z) > 1e-5:
                continue
            opening = bpy.data.objects.get(lf['obj_name'])
            if opening is not None:
                out.append(opening)
    return out


def _restore(cab):
    stamp = cab.get(LIGHT_RAIL_STAMP)
    if stamp is None:
        return
    try:
        stamp = stamp.to_dict()
    except AttributeError:
        stamp = dict(stamp)
    props = cab.face_frame_cabinet
    prev_unlock = bool(stamp.get('prev_unlock_rail', False))
    props.unlock_bottom_rail = prev_unlock
    rail = stamp.get('prev_rail')
    if not prev_unlock:
        # A locked rail follows the style; read it now in case the style
        # changed while the light rail was on.
        rail = _style_bottom_rail(cab) or rail
    if rail is not None:
        props.bottom_rail_width = rail
    for name, (unlock, value) in (stamp.get('openings') or {}).items():
        opening = bpy.data.objects.get(name)
        ffo = getattr(opening, 'face_frame_opening', None)
        if ffo is None:
            continue
        ffo.bottom_overlay = value
        ffo.unlock_bottom_overlay = bool(unlock)
    sec = stamp.get('section')
    if sec:
        idx, unlock, value = sec
        if 0 <= int(idx) < len(props.corner_sections):
            s = props.corner_sections[int(idx)]
            s.bottom_overlay = value
            s.unlock_bottom_overlay = bool(unlock)
    del cab[LIGHT_RAIL_STAMP]


def _apply(cab, height, cover):
    props = cab.face_frame_cabinet
    current = props.bottom_rail_width
    if height <= current + _EPS:
        return                       # already at least that tall
    delta = height - current
    stamp = {
        'height': height,
        'cover': cover,
        'prev_unlock_rail': props.unlock_bottom_rail,
        'prev_rail': current,
        'openings': {},
        'section': [],
        'section_doors': 0,
    }
    props.unlock_bottom_rail = True
    props.bottom_rail_width = height
    if cover:
        default = props.default_bottom_overlay
        for opening in _bottom_row_openings(cab):
            ffo = getattr(opening, 'face_frame_opening', None)
            if ffo is None or ffo.front_type != 'DOOR':
                continue
            was = ffo.bottom_overlay if ffo.unlock_bottom_overlay else default
            # ID-property arrays are single-typed: the flag rides as 0 / 1.
            stamp['openings'][opening.name] = [
                float(ffo.unlock_bottom_overlay), ffo.bottom_overlay]
            ffo.unlock_bottom_overlay = True
            ffo.bottom_overlay = was + delta
        if props.corner_type == 'DIAGONAL' and len(props.corner_sections):
            idx = len(props.corner_sections) - 1      # ordered top to bottom
            s = props.corner_sections[idx]
            if s.content == 'DOORS':
                was = s.bottom_overlay if s.unlock_bottom_overlay else default
                stamp['section'] = [float(idx), float(s.unlock_bottom_overlay),
                                    s.bottom_overlay]
                stamp['section_doors'] = 2            # a double-door pair
                s.unlock_bottom_overlay = True
                s.bottom_overlay = was + delta
    cab[LIGHT_RAIL_STAMP] = stamp


def apply_room_light_rail(scene):
    """Bring every upper in the scene in line with the room's light rail
    settings. Safe to call repeatedly."""
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return
    from . import types_face_frame
    height, cover = _room_settings(scene)
    with types_face_frame.suspend_recalc():
        for cab in _scene_uppers(scene):
            props = cab.face_frame_cabinet
            wanted = (height > 0.0 and not props.exclude_light_rail
                      and cab.matrix_world.translation.z >= MIN_MOUNT_HEIGHT)
            stamp = cab.get(LIGHT_RAIL_STAMP)
            if (wanted and stamp is not None
                    and abs(stamp.get('height', 0.0) - height) < 1e-6
                    and bool(stamp.get('cover')) == cover
                    and abs(props.bottom_rail_width - height) < 1e-6):
                continue             # already set up this way: no recalc
            _restore(cab)
            if wanted:
                _apply(cab, height, cover)


def update_exclude_light_rail(self, context):
    scene = getattr(context, 'scene', None)
    if scene is not None:
        apply_room_light_rail(scene)
