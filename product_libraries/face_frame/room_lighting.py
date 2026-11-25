"""Room lighting: under cabinet lights and toe kick lights for a whole room.

The room's Lighting settings (Options tab) switch the lights on for
every cabinet in the room at once:

* Under Cabinet Lights -- every standard upper gets the LED route and
  render light of its finished bottom. An upper with no finished bottom
  gets the room's Finished Bottom condition. What each upper had before
  is kept in its ROOM_UC_LIGHT_STAMP, so turning the room setting off
  puts every upper back the way it was (an upper that was already lit
  stays lit).
* Toe Kick Lights -- every base and tall cabinet's toe_kick_light. A
  cabinet's own toggle still turns it off on its own.

New cabinets placed while a setting is on pick it up (seed_new_cabinet).
"""

import json

ROOM_UC_LIGHT_STAMP = 'HB_ROOM_UC_LIGHT'
_STAMP_FIELDS = ('finished_bottom_type', 'finished_bottom_led_route',
                 'finished_bottom_light')


def _room_cabinets(scene, types):
    from . import types_face_frame
    out = []
    for obj in scene.objects:
        if not obj.get(types_face_frame.TAG_CABINET_CAGE):
            continue
        props = getattr(obj, 'face_frame_cabinet', None)
        if props is None or props.cabinet_type not in types:
            continue
        if types_face_frame.find_cabinet_root(obj) is not obj:
            continue
        out.append(obj)
    return out


def _standard_upper(cab):
    # Corner uppers build no finished bottom (same rule as the
    # finished bottom dialog's room apply).
    return getattr(cab, 'corner_type', 'NONE') == 'NONE'


def _light_upper(obj, condition):
    cab = obj.face_frame_cabinet
    if ROOM_UC_LIGHT_STAMP not in obj:
        obj[ROOM_UC_LIGHT_STAMP] = json.dumps(
            {f: getattr(cab, f) for f in _STAMP_FIELDS})
    prev = json.loads(obj[ROOM_UC_LIGHT_STAMP])
    if prev.get('finished_bottom_type', 'NONE') == 'NONE':
        if cab.finished_bottom_type != condition:
            cab.finished_bottom_type = condition
    elif cab.finished_bottom_type == 'NONE':
        cab.finished_bottom_type = prev['finished_bottom_type']
    if not cab.finished_bottom_led_route:
        cab.finished_bottom_led_route = True
    if not cab.finished_bottom_light:
        cab.finished_bottom_light = True


def _restore_upper(obj):
    raw = obj.get(ROOM_UC_LIGHT_STAMP)
    if raw is None:
        return
    cab = obj.face_frame_cabinet
    try:
        prev = json.loads(raw)
    except (TypeError, ValueError):
        prev = {}
    for f in _STAMP_FIELDS:
        if f in prev and getattr(cab, f) != prev[f]:
            setattr(cab, f, prev[f])
    del obj[ROOM_UC_LIGHT_STAMP]


def apply_under_cabinet_lights(scene):
    from . import types_face_frame
    ff = getattr(scene, 'hb_face_frame', None)
    if ff is None:
        return 0
    on = ff.room_under_cabinet_lights
    count = 0
    with types_face_frame.suspend_recalc():
        for obj in _room_cabinets(scene, ('UPPER',)):
            if on and _standard_upper(obj.face_frame_cabinet):
                _light_upper(obj, ff.room_under_cabinet_light_bottom)
                count += 1
            else:
                _restore_upper(obj)
    return count


def apply_toe_kick_lights(scene):
    from . import types_face_frame
    ff = getattr(scene, 'hb_face_frame', None)
    if ff is None:
        return 0
    on = ff.room_toe_kick_lights
    count = 0
    with types_face_frame.suspend_recalc():
        for obj in _room_cabinets(scene, ('BASE', 'TALL')):
            cab = obj.face_frame_cabinet
            if cab.toe_kick_light != on:
                cab.toe_kick_light = on
            count += 1
    return count


def seed_new_cabinet(obj, scene):
    """Give a cabinet placed in a lit room the room's lights. Called once
    the cabinet's props are written, before its first full build."""
    ff = getattr(scene, 'hb_face_frame', None)
    cab = getattr(obj, 'face_frame_cabinet', None)
    if ff is None or cab is None:
        return
    if cab.cabinet_type == 'UPPER':
        if ff.room_under_cabinet_lights and _standard_upper(cab):
            _light_upper(obj, ff.room_under_cabinet_light_bottom)
    elif cab.cabinet_type in ('BASE', 'TALL'):
        if ff.room_toe_kick_lights and not cab.toe_kick_light:
            cab.toe_kick_light = True


def update_under_cabinet_lights(self, context):
    scene = self.id_data
    if hasattr(scene, 'objects'):
        apply_under_cabinet_lights(scene)


def update_under_cabinet_light_bottom(self, context):
    scene = self.id_data
    if hasattr(scene, 'objects') and self.room_under_cabinet_lights:
        apply_under_cabinet_lights(scene)


def update_toe_kick_lights(self, context):
    scene = self.id_data
    if hasattr(scene, 'objects'):
        apply_toe_kick_lights(scene)
