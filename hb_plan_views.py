"""Plan views: what the viewport shows of a house, picked by name.

A house has a handful of show switches - one level or all of them, the
level below ghosted, roofs, ceilings, room labels, door swings - plus
the viewport's shading and where it looks from. Which of them you want
depends on what you are doing: drawing walls wants the active level
from above with its labels; checking the roof wants every level with
the roofs on; showing the house wants it in 3D with its finishes. A
plan view sets them all at once.

The house's plan_view reads which view the switches match right now
(Custom when none does, as soon as one is changed by hand) and setting
it applies that view - so it needs no state of its own and can never
disagree with the switches.
"""
import math

import bpy
from mathutils import Euler, Quaternion, Vector

# hb_house imports this module for its plan_view property, so hb_house is
# imported inside the functions that need it.

# key: (label, description, settings)
#   level_display, show_level_below (only matters for ACTIVE),
#   show_roofs, show_ceilings, show_room_labels  -- on scene.hb_house
#   show_door_swings                             -- on scene.home_builder
#   shading  -- the 3D views' shading type
#   camera   -- 'TOP' straight down, orthographic; 'MODEL' a 3/4 view
VIEWS = {
    'WORKING': ("Working Plan", "Draw on the active level from above: the level below ghosted, "
                "room labels and door swings on, roofs and ceilings off", {
        'level_display': 'ACTIVE', 'show_level_below': True, 'show_roofs': False,
        'show_ceilings': False, 'show_room_labels': True, 'show_door_swings': True,
        'shading': 'SOLID', 'camera': 'TOP'}),
    'ROOF': ("Roof Plan", "Every level from above with the roofs on", {
        'level_display': 'ALL', 'show_roofs': True, 'show_ceilings': False,
        'show_room_labels': False, 'show_door_swings': False,
        'shading': 'SOLID', 'camera': 'TOP'}),
    'MODEL': ("Model", "The whole house in 3D, roofs on, no labels", {
        'level_display': 'ALL', 'show_roofs': True, 'show_ceilings': False,
        'show_room_labels': False, 'show_door_swings': False,
        'shading': 'SOLID', 'camera': 'MODEL'}),
    'INTERIOR': ("Interior", "The active level in 3D with its finishes, roof off, to look into the rooms", {
        'level_display': 'ACTIVE', 'show_level_below': False, 'show_roofs': False,
        'show_ceilings': False, 'show_room_labels': False, 'show_door_swings': False,
        'shading': 'MATERIAL', 'camera': 'MODEL'}),
    'PRESENTATION': ("Presentation", "The whole house in 3D with its finishes", {
        'level_display': 'ALL', 'show_roofs': True, 'show_ceilings': False,
        'show_room_labels': False, 'show_door_swings': False,
        'shading': 'MATERIAL', 'camera': 'MODEL'}),
    'FRAMING': ("Framing", "The whole house in 3D with its framing showing, the solids as outlines", {
        'level_display': 'ALL', 'show_roofs': True, 'show_ceilings': False,
        'show_room_labels': False, 'show_door_swings': False, 'show_framing': True,
        'shading': 'SOLID', 'camera': 'MODEL'}),
}

# A view that does not mention framing turns it off
for _key, (_l, _d, _s) in VIEWS.items():
    _s.setdefault('show_framing', False)

ITEMS = [(key, label, desc) for key, (label, desc, _s) in VIEWS.items()]
ITEMS.append(('CUSTOM', "Custom", "The switches have been set by hand"))

HOUSE_KEYS = ('level_display', 'show_level_below', 'show_roofs', 'show_ceilings',
              'show_room_labels', 'show_framing')

MODEL_ROTATION = Euler((math.radians(62.0), 0.0, math.radians(32.0))).to_quaternion()


# ---------------------------------------------------------------------------
# The viewport
# ---------------------------------------------------------------------------

def _view3d_spaces():
    screen = getattr(bpy.context, 'screen', None)
    if screen is None:
        return []
    return [a.spaces.active for a in screen.areas if a.type == 'VIEW_3D']


def _camera_of(space):
    rv3d = space.region_3d
    if rv3d is None:
        return None
    if rv3d.view_perspective == 'ORTHO' and \
            rv3d.view_rotation.rotation_difference(Quaternion()).angle < 1e-3:
        return 'TOP'
    return 'MODEL'


def current(scene=None):
    """The view the switches match now, or 'CUSTOM'."""
    from . import hb_house
    scene = scene or bpy.context.scene
    if scene is None or not scene.get(hb_house.HOUSE_SCENE_KEY):
        return 'CUSTOM'
    house = scene.hb_house
    spaces = _view3d_spaces()
    shading = spaces[0].shading.type if spaces else None
    camera = _camera_of(spaces[0]) if spaces else None
    for key, (_l, _d, s) in VIEWS.items():
        if any(getattr(house, k) != s[k] for k in HOUSE_KEYS
               if k in s and not (k == 'show_level_below' and s['level_display'] != 'ACTIVE')):
            continue
        if scene.home_builder.show_door_swings != s['show_door_swings']:
            continue
        if shading is not None and shading != s['shading']:
            continue
        if camera is not None and camera != s['camera']:
            continue
        return key
    return 'CUSTOM'


def house_bounds(scene, level=None):
    """(centre, (width, depth), z) of the walls on a level (or every
    level) in plan."""
    from . import hb_house
    from .operators import walls as hb_walls
    xs, ys = [], []
    for obj in scene.objects:
        if not obj.get('IS_WALL_BP') or obj.get('WALL_TYPE') == 'Dormer':
            continue
        if level is not None and obj.get(hb_house.LEVEL_KEY) != level.uid:
            continue
        try:
            a, b = hb_walls.get_wall_endpoints(obj)
        except Exception:
            continue
        xs += [a.x, b.x]
        ys += [a.y, b.y]
    z = level.elevation if level is not None else 0.0
    if not xs:
        return Vector((0.0, 0.0, z)), (10.0, 10.0), z
    centre = Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, z))
    return centre, (max(max(xs) - min(xs), 3.0), max(max(ys) - min(ys), 3.0)), z


FIT_MARGIN = 1.3            # room round the walls when framed: the eaves overhang them


def _left_inset(area):
    """Pixels the HUD covers down the left of a view (its panel, the tool
    strip), so the house is framed in what is left."""
    try:
        from .operators import viewport_hud
        return viewport_hud.left_inset(bpy.context, area) or 0.0
    except Exception:
        return 0.0


def frame(scene, camera, level=None):
    """Point every 3D view at the house: straight down, or a 3/4 view,
    sized to fit the part of the view the HUD leaves clear."""
    centre, (wx, wy), _z = house_bounds(scene, level)
    screen = getattr(bpy.context, 'screen', None)
    for area in (screen.areas if screen else ()):
        if area.type != 'VIEW_3D':
            continue
        space = area.spaces.active
        rv3d = space.region_3d
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if rv3d is None or region is None or region.width < 2 or region.height < 2:
            continue
        inset = min(_left_inset(area), region.width * 0.6)
        clear_w = region.width - inset
        if camera == 'TOP':
            # An orthographic view spans view_distance * 72 / lens across
            # its longer side.
            k = 72.0 / space.lens
            long_px = max(region.width, region.height)
            need = max(wx * long_px / clear_w, wy * long_px / region.height)
            dist = need * FIT_MARGIN / k
            per_px = dist * k / long_px
            rv3d.view_rotation = Quaternion()
            rv3d.view_perspective = 'ORTHO'
            rv3d.view_distance = dist
            # Centre the house in the clear part, right of the panel
            rv3d.view_location = centre - Vector((inset / 2.0 * per_px, 0.0, 0.0))
        else:
            # Fit a sphere round the house - plan and height - inside the
            # narrower of the view's angles across the clear part.
            top = _top_z(scene, level)
            mid = centre + Vector((0.0, 0.0, (top - centre.z) / 2.0))
            radius = 0.5 * math.sqrt(wx * wx + wy * wy + (top - centre.z) ** 2)
            long_px = max(region.width, region.height)
            half = 36.0 / space.lens
            tan_h = half * clear_w / long_px
            tan_v = half * region.height / long_px
            dist = radius / math.sin(math.atan(min(tan_h, tan_v))) * 1.05
            rv3d.view_rotation = MODEL_ROTATION
            rv3d.view_perspective = 'PERSP'
            rv3d.view_distance = dist
            # Slide the house right of the panel, along the view's own x
            right = MODEL_ROTATION @ Vector((1.0, 0.0, 0.0))
            shift = (inset / 2.0) / (long_px / 2.0) * half * dist
            rv3d.view_location = mid - right * shift


def _top_z(scene, level=None):
    """The highest point of the walls and roofs shown (a level's, or the
    house's)."""
    from . import hb_house
    top = None
    for obj in scene.objects:
        if not (obj.get('IS_WALL_BP') or (obj.get('IS_ROOF') and not obj.get('IS_ROOF_CUTTER'))):
            continue
        if level is not None and obj.get(hb_house.LEVEL_KEY) != level.uid:
            continue
        if obj.hide_get() or obj.hide_viewport:
            continue
        z = max((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
        top = z if top is None else max(top, z)
    return top if top is not None else 3.0


def apply(scene, key):
    """Set the switches, the shading and the camera for a view."""
    from . import hb_house
    if key not in VIEWS:
        return
    house = scene.hb_house
    s = VIEWS[key][2]
    for k in HOUSE_KEYS:
        if k in s and getattr(house, k) != s[k]:
            setattr(house, k, s[k])
    if scene.home_builder.show_door_swings != s['show_door_swings']:
        scene.home_builder.show_door_swings = s['show_door_swings']
    for space in _view3d_spaces():
        try:
            space.shading.type = s['shading']
        except TypeError:
            pass                # Material Preview is not offered without a GPU
    active = hb_house.active_level_of_scene(scene) if s['level_display'] == 'ACTIVE' else None
    frame(scene, s['camera'], active)


# ---------------------------------------------------------------------------
# The house's plan_view property
# ---------------------------------------------------------------------------

def get_plan_view(house):
    keys = [i[0] for i in ITEMS]
    try:
        return keys.index(current(house.id_data))
    except ValueError:
        return len(keys) - 1


def set_plan_view(house, value):
    key = ITEMS[value][0]
    if key != 'CUSTOM':
        apply(house.id_data, key)
