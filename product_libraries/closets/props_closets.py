"""Closet library properties.

One typed group per level of the product tree, each attached to the cage
object for that level, so every setting has one declared home, one
declared default and one declared range:
- Closets_Scene_Props (Scene.hb_closets): library defaults + library UI.
- Closet_Starter_Props (Object.hb_closet_starter): live dimensions and
  starter-level options on each starter root cage.
- Closet_Bay_Props (Object.hb_closet_bay): per-bay overrides on each bay
  cage (width/lock, height, depth, floor-mounted, remove flags).
- Closet_Opening_Props (Object.hb_closet_opening): what fills each
  opening (shelves, drawers, cubbies, trays, shoe shelves, front).

No drivers: every update callback routes through
types_closets.recalculate_closet_starter, which is guarded against
reentry (system writes during a recalc don't loop back here).
"""
import bpy
import math
from bpy.types import PropertyGroup
from bpy.props import (
        BoolProperty,
        CollectionProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        EnumProperty,
        StringProperty,
        )

import os

from . import const_closets as const
from ...units import inch
from . import starter_presets
from . import materials_closets
from . import pulls_closets
from . import drawer_boxes_closets
from . import fronts_closets
from . import molding_closets
from . import accessories_closets
from ... import units


# ---------------------------------------------------------------------------
# Thumbnail previews (mirrors face_frame's preview-collection pattern)
# ---------------------------------------------------------------------------
preview_collections = {}


def get_starter_previews():
    if "starter_previews" not in preview_collections:
        import bpy.utils.previews
        preview_collections["starter_previews"] = bpy.utils.previews.new()
    return preview_collections["starter_previews"]


def get_thumbnail_path():
    return os.path.join(os.path.dirname(__file__), "closet_thumbnails")


def load_starter_thumbnail(name):
    """Icon id for a starter thumbnail (closet_thumbnails/<name>.png),
    or 0 when no render exists yet - callers fall back to a text button."""
    pcoll = get_starter_previews()
    if name in pcoll:
        return pcoll[name].icon_id
    path = os.path.join(get_thumbnail_path(), f"{name}.png")
    if os.path.exists(path):
        return pcoll.load(name, path, 'IMAGE').icon_id
    return 0


# ---------------------------------------------------------------------------
# Update callbacks
# ---------------------------------------------------------------------------
def _update_starter_prop(self, context):
    """Starter-level prop changed: recalc that starter. Lazy import so
    module load order can't create a cycle."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_hang_rail_height(self, context):
    """The one rail height was typed: hold it against the automatic
    lowest-top figure for the rest of this dialog session (the dialogs
    clear the mark when they open). The build writes the automatic
    figure straight into storage, so only a typed value lands here."""
    self.id_data['hb_rail_typed'] = True
    _update_starter_prop(self, context)


def _update_l_interior(self, context):
    """A rod put in a corner hangs off the back partition: the reference widened
    that partition to 14" if it was narrower, and ran the rod along the
    side wall unless the partition had been flipped onto it."""
    if self.l_interior in ('ROD', 'DOUBLE'):
        if self.l_back_width < inch(14.0):
            self['l_back_width'] = inch(14.0)
        self['l_rod_on_left'] = not self.l_flip_partition
    elif self.l_interior in ('ADJ', 'LOCK') and int(self.l_shelf_qty) == 0:
        # Shelves put into an empty corner deal one a foot through
        # the opening, as the reference's L shelves insert did when dropped.
        from . import types_closets
        self['l_shelf_qty'] = types_closets.default_l_shelf_qty(
            self.id_data)
    _update_starter_prop(self, context)


def sync_end_overhangs(sp, sides=('LEFT', 'RIGHT')):
    """Set the countertop's side overhang and exposed-end flag from
    what stands at that end of the run. A wall filler means the run
    goes to the wall: the top runs out over the filler and stops there,
    and that end is not exposed. A finished end with no filler is
    exposed: the top overhangs it by the end overhang. Anything else
    has no side overhang.

    Written only when one of those changes, so a side overhang typed in
    by hand afterwards is kept until the end condition changes again."""
    for side in sides:
        key = side.lower()
        filler = float(getattr(sp, key + '_side_wall_filler'))
        finished = bool(getattr(sp, key + '_finished_end'))
        if filler > 0.0:
            overhang, exposed = filler, False
        elif finished:
            overhang, exposed = const.COUNTERTOP_OVERHANG_END, True
        else:
            overhang, exposed = 0.0, False
        if abs(getattr(sp, 'countertop_overhang_' + key) - overhang) > 1e-6:
            setattr(sp, 'countertop_overhang_' + key, overhang)
        if getattr(sp, 'countertop_%s_finished_end' % key) != exposed:
            setattr(sp, 'countertop_%s_finished_end' % key, exposed)


def _end_condition_update(side):
    """Update for a finished-end flag or a wall filler width: carry the
    change to the countertop's end, then solve the run once."""
    def _update(self, context):
        from . import types_closets
        with types_closets.suspend_recalc():
            sync_end_overhangs(self, (side,))
        _update_starter_prop(self, context)
    return _update


def _system_panel_height(value):
    """A height someone set, on the 32mm system: down to the step below,
    never under the smallest panel the system builds."""
    return const.snap_system_height_down(
        max(float(value), const.PANEL_MIN_HEIGHT))


def _update_starter_height(self, context):
    """Starter height changed. Panels are drilled on the 32mm system,
    so a height set from outside a solve lands on it - rewriting it
    fires this again with the height already on a step."""
    from . import types_closets
    if id(self.id_data) not in types_closets._RECALCULATING:
        want = _system_panel_height(self.height)
        if abs(want - self.height) > 1e-5:
            self.height = want
            return
    _update_starter_prop(self, context)


def _system_default_height(attr):
    """A default height typed in the room sizes: onto the 32mm system,
    so the starters it seeds come out on a dropdown height."""
    def _update(self, context):
        want = _system_panel_height(getattr(self, attr))
        if abs(want - getattr(self, attr)) > 1e-5:
            setattr(self, attr, want)
    return _update


def _update_starter_depth(self, context):
    """Starter depth changed: no shallower than the system's panel."""
    from . import types_closets
    if (id(self.id_data) not in types_closets._RECALCULATING
            and self.depth < const.PANEL_MIN_DEPTH - 1e-5):
        self.depth = const.PANEL_MIN_DEPTH
        return
    _update_starter_prop(self, context)


def _update_room_solve(self, context):
    """A room construction figure changed: re-solve every run, so the
    whole room reads the new figure at once."""
    from . import types_closets
    scene = getattr(context, 'scene', None) or bpy.context.scene
    with types_closets.suspend_recalc():
        for obj in scene.objects:
            if obj.get(types_closets.TAG_STARTER_CAGE):
                types_closets.recalculate_closet_starter(obj)
    # A slab top stands on its own rather than in a run, so it is sized
    # again here (the room's countertop thickness is one of its figures).
    for obj in scene.objects:
        if types_closets.is_slab_countertop(obj):
            types_closets.layout_slab_countertop(obj)


def _update_lock_shelf_color(self, context):
    """The room's lock-shelf colour changed: repaint every run in that
    room with it (reference Lock Shelf Color). The setting belongs to the
    room's scene, and each part reads its colour from the scene it
    stands in (types_closets.lock_shelf_color), so the room repainted
    is the one whose setting changed, not whichever scene is current."""
    from . import types_closets
    scene = self.id_data if isinstance(self.id_data, bpy.types.Scene) \
        else (getattr(context, 'scene', None) or bpy.context.scene)
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            types_closets.mark_parts(obj)


def _thickness_lock_update(attr):
    """The padlock beside one of the run's part thicknesses. Opening it
    hands the run the room's figure as it stands, so the field opens on
    what the run is already built to rather than on something left over
    from when the file was made; closing it puts the run back on the
    room's. Either way it is held to one solve."""
    def _update(self, context):
        from . import types_closets
        with types_closets.suspend_recalc():
            if getattr(self, 'unlock_' + attr):
                scene = getattr(context, 'scene', None) or bpy.context.scene
                setattr(self, attr,
                        float(getattr(scene.hb_closets, attr)))
            _update_starter_prop(self, context)
    return _update


def _update_kick_preset(self, context):
    """Toe-kick height dropdown changed: set the distance to the chosen
    standard height (the key is millimetres), then recalc. 'CUSTOM'
    leaves the typed distance alone. The distance carries a recalc of
    its own, so the pair is held to one solve."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.toe_kick_height_preset != 'CUSTOM':
            self.toe_kick_height = const.millimeter(
                int(self.toe_kick_height_preset))
        _update_starter_prop(self, context)


_ROOM_KICK_ITEMS = const.KICK_HEIGHT_ITEMS + [
    ('CUSTOM', "Custom", "A height off the standard kicks")]


def _get_room_kick_preset(self):
    """Room kick dropdown reads the room's kick distance: Custom when
    Custom was picked (toe_kick_custom) or the distance matches no
    standard kick, otherwise the standard kick it matches."""
    key = const.kick_height_key(self.toe_kick_height)
    keys = [item[0] for item in _ROOM_KICK_ITEMS]
    if self.toe_kick_custom or not key:
        return keys.index('CUSTOM')
    return keys.index(key)


def _update_room_kick_height(self, context):
    """A kick distance typed off the standard list marks the room's
    kick Custom, so the field stays open for it."""
    if not const.kick_height_key(self.toe_kick_height):
        self['toe_kick_custom'] = True


def _set_room_kick_preset(self, value):
    """Picking a standard kick sets the room's kick distance; Custom
    keeps the distance and opens it for typing."""
    key = _ROOM_KICK_ITEMS[value][0]
    if key == 'CUSTOM':
        self.toe_kick_custom = True
    else:
        self.toe_kick_custom = False
        self.toe_kick_height = const.millimeter(int(key))


def _update_height_preset(self, context):
    """Section-height dropdown changed: set the distance to the chosen
    standard height (the key is millimetres). 'CUSTOM' leaves the typed
    distance alone. Held to one solve - the distance recalcs too."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.height_preset != 'CUSTOM':
            self.height = const.millimeter(int(self.height_preset))
        _update_starter_prop(self, context)


def _height_preset_items(self, context):
    """Standard section heights only; Custom appears solely on a
    section that still carries it from an older file."""
    if self.get('height_preset') == const.PANEL_HEIGHT_CUSTOM_INDEX:
        return const.PANEL_HEIGHT_PRESET_ITEMS_LEGACY
    return const.PANEL_HEIGHT_PRESET_ITEMS


def hang_line(sp):
    """Floor to a run's hang line - the top of the run in the room.
    A Hanging run keeps its top where it is when its height changes by
    moving its origin, so the origin is not always on the floor and
    the run height alone is not the hang line."""
    root = sp.id_data
    return float(root.matrix_world.translation.z) + float(sp.height)


def _hang_height_items(self, context):
    """The 32mm lattice; Custom only while the hang line sits off it
    (a run kept from an older file, or one moved by hand)."""
    if not const.nearest_panel_height_key(hang_line(self)):
        return const.PANEL_HEIGHT_PRESET_ITEMS_LEGACY
    return const.PANEL_HEIGHT_PRESET_ITEMS


def _get_hanging_height_preset(self):
    return const.panel_height_preset_index(
        const.nearest_panel_height_key(hang_line(self)))


def _set_hanging_height_preset(self, value):
    """Hanging Height, as in the reference version: put the hang line, and only the hang line,
    at the height picked, measured from the floor.

    A floor bay still following the run height is handed the height it
    stands at first, so it stays where it is while the hanging bays go
    up or down with the line. A run with every bay hanging moves as a
    whole - its origin, the way a Hanging run already keeps its top -
    so no bay changes size. One with a floor bay keeps its origin and
    takes the difference in its height; the bays stand on the 32mm
    system whatever that comes to, so it is written as it is rather
    than snapped off the line picked."""
    if value == const.PANEL_HEIGHT_CUSTOM_INDEX:
        return
    key = const.PANEL_HEIGHT_ITEMS[value][0]
    delta = const.millimeter(int(key)) - hang_line(self)
    if abs(delta) < 1e-6:
        return
    from . import types_closets
    root = self.id_data
    bays = types_closets._run_bays(root)
    with types_closets.suspend_recalc():
        if (self.closet_type == 'HANGING' and bays
                and not any(b.hb_closet_bay.floor_mounted for b in bays)):
            root.location.z += delta
        else:
            for bay in bays:
                bp = bay.hb_closet_bay
                if bp.floor_mounted and not bp.unlock_height:
                    bp.height = self.height
                    bp.unlock_height = True
            new = max(float(self.height) + delta, const.PANEL_MIN_HEIGHT)
            # The origin stays put: the hang line is what moves.
            root['hb_last_height'] = new
            self['height'] = new
            self['height_preset'] = const.panel_height_preset_index(
                const.nearest_panel_height_key(new))
        types_closets.recalculate_closet_starter(root)


def _set_all_bay_heights(sp, root):
    """Overall Height (as in the reference version) with its padlock open: every opening takes the
    one height - a floor bay from the floor up, a hanging bay down from
    the hang line - each handed it as its own."""
    from . import types_closets
    h = const.millimeter(int(sp.overall_height_preset))
    idx = const.panel_height_preset_index(sp.overall_height_preset)
    with types_closets.suspend_recalc():
        for bay in types_closets._run_bays(root):
            bp = bay.hb_closet_bay
            bp.unlock_height = True
            bp.height = h
            bp['height_preset'] = idx
        types_closets.recalculate_closet_starter(root)


def _update_overall_height(self, context):
    if self.set_all_heights:
        _set_all_bay_heights(self, self.id_data)


def _update_bay_open_door(self, context):
    """The bay's open percentage speaks for every front across it, so a
    front someone had clicked open hands its own answer back and follows
    the number again."""
    from . import types_closets
    bay = self.id_data
    for child in bay.children:
        if (child.get('hb_part_role') == types_closets.PART_ROLE_DOOR
                and 'hb_door_open' in child):
            del child['hb_door_open']
    types_closets.recalculate_closet_starter(bay)


def _update_bay_prop(self, context):
    """Bay-level prop changed - a size the bay owns, one of the padlocks
    that hands it a size, or a construction flag. Recalcs the run; the
    call is a no-op while that run is already solving, so the seeding
    passes that write these props in bulk cost nothing."""
    from . import types_closets
    types_closets.recalculate_closet_starter(self.id_data)


def _update_rod_options(self, context):
    """Room rod type, finish or hangers changed: re-solve the closets,
    whose rods take them on the solve, then re-dress the free rods on
    the walls, which no solve reaches."""
    pulls_closets.update_room(self, context)
    from . import types_closets
    scene = getattr(context, 'scene', None) or bpy.context.scene
    for obj in scene.objects:
        if obj.get(types_closets.PROP_WALL_ROD):
            types_closets.layout_wall_rod(obj)


def _update_bay_height_preset(self, context):
    """Bay height dropdown changed (the key is millimetres). Held to
    one solve - the distance and the padlock both recalc."""
    from . import types_closets
    with types_closets.suspend_recalc():
        if self.height_preset != 'CUSTOM':
            self.height = const.millimeter(int(self.height_preset))
        _update_bay_height(self, context)


def _bay_edit_root(bay_props):
    """The starter a bay belongs to, or None when the write came from
    the system rather than from someone typing in the dialog. Layout
    writes its own values back to the bays, and those must not read as
    edits - otherwise every bay would lock itself the first time the
    run was solved."""
    from . import types_closets
    root = types_closets.find_starter_root(bay_props.id_data)
    if root is None:
        return None
    root_id = id(root)
    if (root_id in types_closets._RECALCULATING
            or root_id in types_closets._DISTRIBUTING_WIDTHS):
        return None
    return root


def _update_bay_width(self, context):
    """Bay width changed. The first edit hands the bay its own width so
    the value holds while the remaining widths are redistributed. That
    flag carries a recalc of its own, so only a later nudge - the bay
    already owning its width - has to ask for one here."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    if not self.unlock_width:
        self.unlock_width = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_bay_height(self, context):
    """Bay height changed. Same idea as the width: a height typed here
    hands the bay its own, so it keeps it when the run height changes.
    Clear the padlock to put the bay back on the run height."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    # On the 32mm system, as the starter's height is.
    want = _system_panel_height(self.height)
    if abs(want - self.height) > 1e-5:
        self.height = want
        return
    if not self.unlock_height:
        self.unlock_height = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_bay_depth(self, context):
    """Bay depth changed - hands the bay its own depth, as above."""
    from . import types_closets
    root = _bay_edit_root(self)
    if root is None:
        return
    if self.depth < const.PANEL_MIN_DEPTH - 1e-5:
        self.depth = const.PANEL_MIN_DEPTH
        return
    if not self.unlock_depth:
        self.unlock_depth = True
    else:
        types_closets.recalculate_closet_starter(root)


def _update_closet_selection_mode(self, context):
    """Apply visibility highlighting for the active closet selection
    mode (mirrors face_frame's update_face_frame_selection_mode)."""
    bpy.ops.hb_closets.toggle_mode(search_obj_name="")


def countertop_thickness_for(scene_props):
    from . import types_closets
    return types_closets.room_countertop_thickness(scene_props)


def _thickness_label(value):
    from . import types_closets
    return types_closets._in_str(value)


def _update_countertop_mode(self, context):
    """Switching the tops between a countertop material and the closet
    material changes what they are made of, so it changes how thick
    they are too. Every top in the room follows, the same way the
    material selections do - a thickness typed on one starter is a
    setting for that material, not a size to carry across."""
    from . import types_closets
    scene = getattr(context, 'scene', None) or bpy.context.scene
    thickness = countertop_thickness_for(self)
    for obj in scene.objects:
        if obj.get(types_closets.TAG_STARTER_CAGE):
            sp = obj.hb_closet_starter
            if abs(sp.countertop_thickness - thickness) > 1e-9:
                # Assigning re-runs the starter, which is what puts the
                # new thickness on the part.
                sp.countertop_thickness = thickness
    materials_closets.update_room(self, context)


def starter_wall(obj):
    """The wall a starter hangs on, or None for a free-standing one."""
    wall = obj.parent if obj is not None else None
    if wall is not None and 'IS_WALL_BP' in wall:
        return wall
    return None


def _starter_on_wall_back(obj):
    # Placed on the back of a wall: turned half round, origin at its
    # right end in wall space.
    return abs(math.cos(obj.rotation_euler.z) + 1.0) < 1e-3


def _wall_length(wall):
    from ... import hb_types
    try:
        return float(hb_types.GeoNodeWall(wall).get_input('Length'))
    except Exception:
        return 0.0


def _get_wall_offset(self):
    obj = self.id_data
    wall = starter_wall(obj)
    if wall is not None and _starter_on_wall_back(obj):
        return _wall_length(wall) - obj.location.x
    return obj.location.x


def _set_wall_offset(self, value):
    obj = self.id_data
    wall = starter_wall(obj)
    if wall is not None and _starter_on_wall_back(obj):
        obj.location.x = _wall_length(wall) - value
    else:
        obj.location.x = value


# ---------------------------------------------------------------------------
# Object-level: starter root
# ---------------------------------------------------------------------------
def _bay_ctop_end_update(side):
    """A countertop end marked finished (or not): an exposed end gets
    the end overhang, a covered one none. Typed afterwards, the
    overhang stays as typed until the flag changes again."""
    def _update(self, context):
        from . import types_closets
        key = side.lower()
        with types_closets.suspend_recalc():
            setattr(self, 'overhang_' + key,
                    const.COUNTERTOP_OVERHANG_END
                    if getattr(self, key + '_finished_end') else 0.0)
        _update_starter_prop(self, context)
    return _update


class Closet_Bay_Countertop_Props(PropertyGroup):
    """A countertop over some of a run's bays rather than the whole run
    - a counter at base height between taller sections, say. It runs
    from the first bay named to the last, sits on their tops, and runs
    over a partition between it and a lower neighbour but stops against
    one that rises above it. Laid out by the run, so it follows the
    bays it covers when they change."""
    uid: StringProperty(options={'HIDDEN'})  # type: ignore
    first_bay: StringProperty(options={'HIDDEN'})  # type: ignore
    last_bay: StringProperty(options={'HIDDEN'})  # type: ignore
    overhang_front: FloatProperty(
        name="Front", description="How far the top projects past the "
                                  "front of the bays",
        default=const.COUNTERTOP_OVERHANG_FRONT, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    overhang_left: FloatProperty(
        name="Left", description="How far the top runs past its left end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    overhang_right: FloatProperty(
        name="Right", description="How far the top runs past its right end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The left end is exposed: it overhangs and gets no "
                    "side splash",
        default=False, update=_bay_ctop_end_update('LEFT'))  # type: ignore
    right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The right end is exposed: it overhangs and gets no "
                    "side splash",
        default=False, update=_bay_ctop_end_update('RIGHT'))  # type: ignore
    include_backsplash: BoolProperty(
        name="Include Backsplash",
        description="Add an upstand along the back, and along each end "
                    "that is not finished",
        default=True, update=_update_starter_prop)  # type: ignore
    backsplash_height: FloatProperty(
        name="Backsplash Height",
        description="How far the backsplash stands above the countertop",
        default=const.BACKSPLASH_HEIGHT, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore


def _update_slab(self, context):
    from . import types_closets
    types_closets.layout_slab_countertop(self.id_data)


def _slab_end_update(side):
    """A slab end marked finished (or not): an exposed end gets the end
    overhang and no side splash, a covered one neither overhang nor
    exposure. A typed overhang stands until the flag changes again."""
    def _update(self, context):
        key = side.lower()
        self['overhang_' + key] = (const.COUNTERTOP_OVERHANG_END
                                   if getattr(self, key + '_finished_end')
                                   else 0.0)
        _update_slab(self, context)
    return _update


class Closet_Slab_Countertop_Props(PropertyGroup):
    """A slab countertop standing on its own: a 1 1/8" laminate top
    set on whatever it was placed over (closet or cabinets) or wherever
    it was put down. Width and depth are of what it covers; the
    overhangs are added to them, so the top grows past its ends and
    out at the front without moving what it sits over."""
    width: FloatProperty(
        name="Width", description="Width of what the top covers, before "
                                  "the end overhangs",
        default=inch(40.0), min=inch(1.0), unit='LENGTH', precision=4,
        update=_update_slab)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Depth of what the top covers, before "
                                  "the front overhang",
        default=inch(24.0), min=inch(1.0), unit='LENGTH', precision=4,
        update=_update_slab)  # type: ignore
    overhang_front: FloatProperty(
        name="Front", description="How far the top projects past the "
                                  "front",
        default=const.COUNTERTOP_OVERHANG_FRONT, min=0.0, unit='LENGTH',
        precision=4, update=_update_slab)  # type: ignore
    overhang_left: FloatProperty(
        name="Left", description="How far the top runs past its left end",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_slab)  # type: ignore
    overhang_right: FloatProperty(
        name="Right", description="How far the top runs past its right end",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_slab)  # type: ignore
    left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The left end is exposed: it overhangs and gets no "
                    "side splash",
        default=False, update=_slab_end_update('LEFT'))  # type: ignore
    right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The right end is exposed: it overhangs and gets no "
                    "side splash",
        default=False, update=_slab_end_update('RIGHT'))  # type: ignore
    include_backsplash: BoolProperty(
        name="Include Backsplash",
        description="Add an upstand along the back, and along each end "
                    "that is not finished",
        default=True, update=_update_slab)  # type: ignore
    backsplash_height: FloatProperty(
        name="Backsplash Height",
        description="How far the backsplash stands above the countertop",
        default=const.BACKSPLASH_HEIGHT, min=0.0, unit='LENGTH',
        precision=4, update=_update_slab)  # type: ignore


class Closet_Bay_Cleat_Props(PropertyGroup):
    """A support cleat under some of a run's hanging bays rather than
    all of them (the Cleat part dropped low in a hanging bay): one
    cleat under the bottom shelf against the wall, from the first bay
    named to the last, laid out the way the run-wide Bottom Cleat is."""
    uid: StringProperty(options={'HIDDEN'})  # type: ignore
    first_bay: StringProperty(options={'HIDDEN'})  # type: ignore
    last_bay: StringProperty(options={'HIDDEN'})  # type: ignore
    # The reference's Cleat prompts (Length, Width, Vertical and Horizontal
    # Location). Each is kept against where the cleat is laid out on its
    # own - under the bottom shelf, end partition to end partition - so
    # nothing set leaves it there, following the bays as they change.
    length: FloatProperty(
        name="Length",
        description="How long the cleat is cut. Nothing runs it the "
                    "full span of its bays",
        default=0.0, min=0.0, unit='LENGTH', precision=4)  # type: ignore
    width: FloatProperty(
        name="Width",
        description="How deep the cleat is cut. Nothing is the standard "
                    "cleat width",
        default=0.0, min=0.0, unit='LENGTH', precision=4)  # type: ignore
    z_offset: FloatProperty(
        name="Vertical Location",
        description="How far the cleat is raised (negative: dropped) "
                    "from the underside of the bottom shelf",
        default=0.0, unit='LENGTH', precision=4)  # type: ignore
    x_offset: FloatProperty(
        name="Horizontal Location",
        description="How far in from the left end of its span the cleat "
                    "starts",
        default=0.0, min=0.0, unit='LENGTH', precision=4)  # type: ignore


class Closet_Starter_Props(PropertyGroup):

    # Where the starter sits along its wall, read off and written to the
    # root's location - nothing is stored here.
    wall_offset: FloatProperty(
        name="Distance From Left",
        description="How far the starter's left side is from the left end "
                    "of the wall, looking at the side of the wall it is on",
        unit='LENGTH', precision=4,
        get=_get_wall_offset, set=_set_wall_offset)  # type: ignore

    # Which page of the properties dialog is showing. Purely UI state.
    prompt_tab: EnumProperty(
        name="Tab",
        items=[
            ('SIZES', "Sizes", "Overall size and the size of each bay"),
            ('CONSTRUCTION', "Construction",
             "Toe kick, ends, hang rail and the per-bay build options"),
            ('COUNTERTOP', "Countertop",
             "Countertop, overhangs and backsplash"),
        ],
        default='SIZES')  # type: ignore

    # Which Construction sections are open. Purely UI state - every
    # section starts closed so the page opens as a short list of headers
    # and only what is being worked on is unfolded.
    show_toe_kick: BoolProperty(
        name="Show Toe Kick", default=False)  # type: ignore
    show_top: BoolProperty(
        name="Show Top", default=False)  # type: ignore
    show_hang_rail: BoolProperty(
        name="Show Hang Rail", default=False)  # type: ignore
    show_applied_back: BoolProperty(
        name="Show Applied Back", default=False)  # type: ignore
    show_insets: BoolProperty(
        name="Show Insets", default=False)  # type: ignore
    show_corner: BoolProperty(
        name="Show Corner", default=False)  # type: ignore
    show_panels: BoolProperty(
        name="Show Panels", default=False)  # type: ignore
    show_per_bay: BoolProperty(
        name="Show Per Bay", default=False)  # type: ignore

    width: FloatProperty(
        name="Width", description="Starter width (X)",
        default=const.DEFAULT_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    height: FloatProperty(
        name="Height", description="Panel height (Z), on the 32mm system",
        default=const.TALL_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_height)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Panel depth (Y)",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_depth)  # type: ignore

    # Standard section heights (the 32mm-system lattice). Picking one
    # writes the distance above.
    height_preset: EnumProperty(
        name="Height",
        description="Standard section height on the 32mm system",
        items=_height_preset_items,
        default=const.PANEL_HEIGHT_DEFAULT_INDEX,
        update=_update_height_preset)  # type: ignore

    # The reference's pair on a run that hangs (Tall and Hanging): the hang line
    # on its own, and one height written to every bay at once. The hang
    # line is the run height read another way, so it stores nothing.
    hanging_height_preset: EnumProperty(
        name="Hanging Height",
        description="Floor to the hang line the hanging bays hang from. "
                    "Floor bays stay at the height they stand at",
        items=_hang_height_items,
        get=_get_hanging_height_preset,
        set=_set_hanging_height_preset)  # type: ignore
    set_all_heights: BoolProperty(
        name="Set All Opening Heights",
        description="Give every bay the Overall Height at once. Off sets "
                    "each bay's height in the Bays table",
        default=False,
        update=_update_overall_height)  # type: ignore
    overall_height_preset: EnumProperty(
        name="Overall Height",
        description="The height every bay takes while Set All Opening "
                    "Heights is on",
        items=const.PANEL_HEIGHT_ITEMS,
        default='2131',
        update=_update_overall_height)  # type: ignore

    closet_type: EnumProperty(
        name="Closet Type",
        items=[
            ('BASE', "Base", "Floor-mounted base starter"),
            ('TALL', "Tall", "Floor-mounted full-height starter"),
            ('HANGING', "Hanging", "Wall-mounted hanging starter"),
            ('ISLAND', "Island", "Single-sided island starter"),
        ],
        default='BASE')  # type: ignore

    toe_kick_height_preset: EnumProperty(
        name="Toe Kick Height",
        description="Standard toe-kick height (Custom keeps the typed "
                    "value)",
        items=const.KICK_HEIGHT_ITEMS + [('CUSTOM', "Custom",
                                          "Use the typed height")],
        default='96', update=_update_kick_preset)  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height",
        description="Floor to the underside of the bottom shelf on a "
                    "floor bay",
        default=const.DEFAULT_TOE_KICK_HEIGHT, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback",
        description="How far the kick sits back from the front of the "
                    "panels",
        default=const.DEFAULT_TOE_KICK_SETBACK, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    include_countertop: BoolProperty(
        name="Include Countertop",
        description="Lay a countertop across the top of the run",
        default=False, update=_update_starter_prop)  # type: ignore

    # What this run's parts are cut from. Every figure follows the
    # room until the padlock hands this run its own, the same way a bay
    # takes a size over from the run. Held here rather than on the
    # parts so nothing is driven: the run is read once at the top of a
    # pass and the figures go straight into the part sizes.
    unlock_panel_thickness: BoolProperty(
        name="Panel Thickness",
        description="Give this run its own panel thickness instead of "
                    "following the room",
        default=False,
        update=_thickness_lock_update('panel_thickness'))  # type: ignore
    panel_thickness: FloatProperty(
        name="Panel", description="What this run's panels are cut from",
        default=const.PANEL_THICKNESS, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    unlock_shelf_thickness: BoolProperty(
        name="Shelf Thickness",
        description="Give this run its own shelf thickness instead of "
                    "following the room",
        default=False,
        update=_thickness_lock_update('shelf_thickness'))  # type: ignore
    shelf_thickness: FloatProperty(
        name="Shelf", description="What this run's shelves are cut from",
        default=const.SHELF_THICKNESS, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    unlock_divider_thickness: BoolProperty(
        name="Cubby Divider Thickness",
        description="Give this run its own cubby divider thickness "
                    "instead of following the room",
        default=False,
        update=_thickness_lock_update('divider_thickness'))  # type: ignore
    divider_thickness: FloatProperty(
        name="Cubby Divider",
        description="What the uprights in this run's cubby grids are "
                    "cut from",
        default=const.DIVIDER_THICKNESS, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    unlock_batten_thickness: BoolProperty(
        name="Batten Thickness",
        description="Give this run its own batten thickness instead of "
                    "following the room",
        default=False,
        update=_thickness_lock_update('batten_thickness'))  # type: ignore
    batten_thickness: FloatProperty(
        name="Batten",
        description="How thick the scribe strip on the end of this run "
                    "is",
        default=const.BATTEN_THICKNESS, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    unlock_batten_width: BoolProperty(
        name="Batten Width",
        description="Give this run its own batten width instead of "
                    "following the room",
        default=False,
        update=_thickness_lock_update('batten_width'))  # type: ignore
    batten_width: FloatProperty(
        name="Batten Width",
        description="How wide the scribe strip on the end of this run "
                    "is. Whatever it carries past the panel edge is "
                    "what there is to scribe to the wall",
        default=const.BATTEN_WIDTH, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore

    # Countertop shaping. The overhangs are measured past the carcass on
    # each side; finished ends and the radius option are edge treatments
    # a downstream pass consumes.
    countertop_thickness: FloatProperty(
        name="Thickness", description="Countertop material thickness",
        default=const.COUNTERTOP_THICKNESS,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_front: FloatProperty(
        name="Front", description="Countertop projection past the front "
                                  "of the carcass",
        default=const.COUNTERTOP_OVERHANG_FRONT, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore
    countertop_overhang_rear: FloatProperty(
        name="Rear", description="Countertop projection past the back of "
                                 "the carcass",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_left: FloatProperty(
        name="Left", description="Countertop projection past the left end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_overhang_right: FloatProperty(
        name="Right", description="Countertop projection past the right end",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    countertop_left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The countertop's left end is exposed, so it gets an "
                    "edge treatment and no side backsplash",
        default=False, update=_update_starter_prop)  # type: ignore
    countertop_right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The countertop's right end is exposed, so it gets an "
                    "edge treatment and no side backsplash",
        default=False, update=_update_starter_prop)  # type: ignore
    # The rounding is not drawn on the top. The prior library carried
    # it the same way - a choice recorded against the part for whoever
    # cuts it - so it rides along on hb_ctop_corner_radius beside the
    # two finished-end flags, which say which corners it applies to.
    countertop_radius_finished_ends: BoolProperty(
        name="Radius Finished Ends",
        description="Round the exposed corners of a finished end "
                    "instead of leaving them square",
        default=False, update=_update_starter_prop)  # type: ignore
    include_backsplash: BoolProperty(
        name="Include Backsplash",
        description="Add an upstand along the countertop's wall edges. "
                    "An end marked finished has no wall, so it gets no "
                    "side splash",
        default=True, update=_update_starter_prop)  # type: ignore
    backsplash_height: FloatProperty(
        name="Backsplash Height",
        description="How far the backsplash stands above the countertop",
        default=const.BACKSPLASH_HEIGHT,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    # Countertops over some of the bays (the Countertop part).
    bay_countertops: CollectionProperty(
        type=Closet_Bay_Countertop_Props)  # type: ignore

    # Applied back: the panel closing the rear face of an island bay.
    back_to_floor: BoolProperty(
        name="Back to Floor",
        description="Run the applied back all the way down to the floor "
                    "instead of starting above the toe kick",
        default=False, update=_update_starter_prop)  # type: ignore
    applied_back_overlay: FloatProperty(
        name="Applied Back Overlay",
        description="How far the applied back laps onto the panels and "
                    "shelves around its bay",
        default=const.APPLIED_BACK_OVERLAY, min=0.0, unit='LENGTH',
        precision=4, update=_update_starter_prop)  # type: ignore

    # Hanging panels can run down past the bottom of their section so
    # they finish alongside the countertop of whatever sits below.
    extend_panels_to_countertop: BoolProperty(
        name="Extend Panels to Countertop",
        description="Run every hanging panel down past the bottom of its "
                    "section so it finishes alongside the countertop "
                    "below. Panels that already reach the floor are left "
                    "alone",
        default=False, update=_update_starter_prop)  # type: ignore
    extend_panel_amount: FloatProperty(
        name="Extend Panel Amount",
        description="How far past the bottom of the section an extended "
                    "panel runs",
        default=const.EXTEND_PANEL_AMOUNT,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Bridge shelves spanning the access gap to a corner neighbor. The
    # Corner Clearance command fills these in from the measured gap;
    # they can also be set by hand here.
    bridge_left: BoolProperty(
        name="Bridge Left",
        description="Span the gap past the left end with a shelf at the "
                    "corner bay's top shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    bridge_right: BoolProperty(
        name="Bridge Right",
        description="Span the gap past the right end with a shelf at the "
                    "corner bay's top shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    bridge_left_width: FloatProperty(
        name="Left Bridge Shelf Width",
        description="How far the left bridge shelf reaches past the end "
                    "of the run",
        default=const.BRIDGE_SHELF_WIDTH,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    bridge_right_width: FloatProperty(
        name="Right Bridge Shelf Width",
        description="How far the right bridge shelf reaches past the end "
                    "of the run",
        default=const.BRIDGE_SHELF_WIDTH,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    include_bottom_bridge_left: BoolProperty(
        name="Include Bottom Bridge Left",
        description="Also bridge the gap at the bottom shelf height",
        default=False, update=_update_starter_prop)  # type: ignore
    include_bottom_bridge_right: BoolProperty(
        name="Include Bottom Bridge Right",
        description="Also bridge the gap at the bottom shelf height",
        default=False, update=_update_starter_prop)  # type: ignore

    # Run-wide insets, both floor-bay only (a hanging bay has neither a
    # kick nor a bottom to set in). A bay can add its own bottom shelf
    # inset on top of the run-wide one in the bay properties.
    inset_bottom: FloatProperty(
        name="Inset Bottom",
        description="Hold every floor bay's bottom shelf off the wall by "
                    "this much (the front edge stays where it was)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    inset_cleat: FloatProperty(
        name="Inset Cleat",
        description="Raise every floor bay's cleat this far above the "
                    "bottom shelf",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    bottom_cleat: BoolProperty(
        name="Bottom Cleat",
        description="Run one continuous cleat under the bottom of the "
                    "hanging bays, end panel to end panel, to carry the "
                    "load against the wall",
        default=False, update=_update_starter_prop)  # type: ignore
    # Support cleats under some of the hanging bays (the Cleat part).
    bay_cleats: CollectionProperty(
        type=Closet_Bay_Cleat_Props)  # type: ignore

    # End options. Finished end and drill through are recorded on the
    # panel as flags - whether the end is exposed, and whether its
    # system holes run all the way through; turn-off frees the panel
    # thickness back to the openings for shared-panel runs; battens are
    # cosmetic scribe strips.
    left_finished_end: BoolProperty(
        name="Left Finished End",
        description="The left end panel is exposed, so it gets an edge "
                    "treatment and no through drilling",
        default=False, update=_end_condition_update('LEFT'))  # type: ignore
    right_finished_end: BoolProperty(
        name="Right Finished End",
        description="The right end panel is exposed, so it gets an edge "
                    "treatment and no through drilling",
        default=False, update=_end_condition_update('RIGHT'))  # type: ignore
    turn_off_left_panel: BoolProperty(
        name="Turn Off Left Panel",
        description="Hide the left end panel and give its thickness to "
                    "the first bay (share a panel with the neighbor)",
        default=False, update=_update_starter_prop)  # type: ignore
    turn_off_right_panel: BoolProperty(
        name="Turn Off Right Panel",
        description="Hide the right end panel and give its thickness to "
                    "the last bay (share a panel with the neighbor)",
        default=False, update=_update_starter_prop)  # type: ignore
    drill_through_left: BoolProperty(
        name="Drill Through Left Side",
        description="Carry the shelf holes all the way through the left "
                    "end panel instead of stopping partway",
        default=False, update=_update_starter_prop)  # type: ignore
    drill_through_right: BoolProperty(
        name="Drill Through Right Side",
        description="Carry the shelf holes all the way through the right "
                    "end panel instead of stopping partway",
        default=False, update=_update_starter_prop)  # type: ignore
    include_batten_left: BoolProperty(
        name="Include Batten Left",
        description="Add a scribe strip down the inside front edge of the "
                    "left end panel",
        default=False, update=_update_starter_prop)  # type: ignore
    include_batten_right: BoolProperty(
        name="Include Batten Right",
        description="Add a scribe strip down the inside front edge of the "
                    "right end panel",
        default=False, update=_update_starter_prop)  # type: ignore

    # Top accent shelf: a decorative shelf on
    # top of the run projecting forward by the overhang, with a side
    # overhang past each finished end.
    add_top_accent_shelf: BoolProperty(
        name="Add Top Accent Shelf",
        description="Lay a decorative shelf across the top of the run",
        default=False, update=_update_starter_prop)  # type: ignore
    top_accent_overhang: FloatProperty(
        name="Top Accent Shelf Overhang",
        description="How far the accent shelf projects past the front and "
                    "past each finished end",
        default=const.TOP_ACCENT_OVERHANG, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    # By default the shelf's ends follow the run: out over a wall filler
    # to the wall, past a finished end by the overhang, flush otherwise.
    # Set separately, each end takes its own figure regardless - to
    # bridge over to a neighbouring starter, say.
    top_accent_set_sides: BoolProperty(
        name="Set Left/Right Separately",
        description="Give the accent shelf its own left and right "
                    "overhangs instead of following the finished ends "
                    "and fillers",
        default=False, update=_update_starter_prop)  # type: ignore
    top_accent_overhang_left: FloatProperty(
        name="Left",
        description="How far the accent shelf runs past the left end",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    top_accent_overhang_right: FloatProperty(
        name="Right",
        description="How far the accent shelf runs past the right end",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    # Hang rail options.
    remove_hang_rail: BoolProperty(
        name="Remove Hang Rail",
        description="Hide the wall hang rail on every bay",
        default=False, update=_update_starter_prop)  # type: ignore
    extend_hang_rail_left: FloatProperty(
        name="Extend Hang Rail Left",
        description="Lengthen the leftmost bay's rail toward the left "
                    "wall by this much",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    extend_hang_rail_right: FloatProperty(
        name="Extend Hang Rail Right",
        description="Lengthen the rightmost bay's rail toward the right "
                    "wall by this much",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    use_one_hang_rail_height: BoolProperty(
        name="Use One Hang Rail Height",
        description="Force every bay's rail to a single height instead "
                    "of each bay's own top",
        default=False, update=_update_starter_prop)  # type: ignore
    hang_rail_height_location: FloatProperty(
        name="Hang Rail Height",
        description="Rail height above the floor when Use One Hang Rail "
                    "Height is on. Follows the lowest opening top less "
                    "3 5/16\" whenever a height changes, unless typed in "
                    "the dialog that changed it",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_hang_rail_height)  # type: ignore

    # Side wall fillers: a front scribe
    # strip standing past the end of the run to close the gap to a side
    # wall. Width 0 = no filler. The prompt value is the filler width.
    left_side_wall_filler: FloatProperty(
        name="Left Side Wall Filler",
        description="Width of the scribe filler past the left end (0 = "
                    "none)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_end_condition_update('LEFT'))  # type: ignore
    right_side_wall_filler: FloatProperty(
        name="Right Side Wall Filler",
        description="Width of the scribe filler past the right end (0 = "
                    "none)",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_end_condition_update('RIGHT'))  # type: ignore

    # Corner (L-shelf) starter prompts. Only meaningful when the
    # starter class is an L-shelf variant (is_corner); the prompts
    # dialog gates on that.
    l_left_depth: FloatProperty(
        name="Left Depth", description="Left wing panel depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_right_depth: FloatProperty(
        name="Right Depth", description="Right wing panel depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    filler_left_width: FloatProperty(
        name="Left Filler Width",
        description="How wide the board against the side wall is cut",
        default=const.CORNER_FILLER_WIDTH, min=0.0,
        unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    filler_right_width: FloatProperty(
        name="Right Filler Width",
        description="How wide the board against the back wall is cut",
        default=const.CORNER_FILLER_WIDTH, min=0.0,
        unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore

    l_interior: EnumProperty(
        name="Corner Holds",
        description="What goes inside the corner unit",
        # Numbered so saved units keep what they hold: 'NONE' came
        # later and takes the next number, though it lists first.
        items=[
            ('NONE', "Empty",
             "Only the top and bottom - the reference version's corner "
             "as it was dropped", 4),
            ('ADJ', "Adjustable Shelves",
             "Shelves on pins, moved by hand. Any one of them can be "
             "locked afterwards", 0),
            ('LOCK', "Lock Shelves",
             "Shelves fixed on cams, holding the unit square", 1),
            ('ROD', "Single Hanging Rod",
             "One rod along a wing, for full-length hanging", 2),
            ('DOUBLE', "Double Hang",
             "Two rods with a fixed shelf between them", 3),
        ],
        default='ADJ', update=_update_l_interior)  # type: ignore
    l_rod_on_left: BoolProperty(
        name="Rod On The Side Wall",
        description="Hang the rod along the side wall rather than the "
                    "back wall. A rod needs the other wing to be at "
                    "least two feet for the clothes to clear",
        default=True, update=_update_starter_prop)  # type: ignore
    l_top_opening_height: FloatProperty(
        name="Top Opening Height",
        description="Clear opening over the shelf between the two "
                    "rods: its top to the underside of the top shelf",
        default=const.L_DOUBLE_TOP_OPENING, min=0.0,
        unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    # Where a corner rod stands across its wing (reference
    # Closet_Rod_Corner_Insert: Closet Rod Location From Rear / From
    # Front, Set Distance From Front, Remove Hangers).
    l_rod_from_rear: FloatProperty(
        name="Rod Dim From Rear",
        description="How far the rod stands out from the wall behind "
                    "the wing it runs along",
        default=const.L_ROD_FROM_WALL, min=0.0,
        unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_rod_set_from_front: BoolProperty(
        name="Set Distance From Front",
        description="Measure the rod back from the front of its wing "
                    "instead of out from the wall",
        default=False, update=_update_starter_prop)  # type: ignore
    l_rod_from_front: FloatProperty(
        name="Dim From Front",
        description="How far the rod stands back from the front of the "
                    "wing it runs along",
        default=inch(2.0), min=0.0,
        unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_remove_hangers: BoolProperty(
        name="Remove Hangers",
        description="Leave the display hangers off the corner's rods",
        default=False, update=_update_starter_prop)  # type: ignore

    l_shelf_qty: IntProperty(
        name="Shelf Quantity",
        description="Interior L shelves between the bottom and top",
        default=const.L_SHELF_QTY, min=0, max=12,
        update=_update_starter_prop)  # type: ignore
    l_back_width: FloatProperty(
        name="Back Partition Width",
        description="Width of the corner back partition the L shelves "
                    "notch around",
        default=const.L_BACK_STRIP_WIDTH, unit='LENGTH', precision=4,
        update=_update_starter_prop)  # type: ignore
    l_flip_partition: BoolProperty(
        name="Flip Back Partition",
        description="Move the back partition from the back wall to the "
                    "side wall",
        default=False,
        update=_update_starter_prop)  # type: ignore
    l_use_radius: BoolProperty(
        name="Radius Front Corner",
        description="Round the inside front corner of the L shelves "
                    "instead of cutting it square",
        default=True,
        update=_update_starter_prop)  # type: ignore
    l_corner_radius: FloatProperty(
        name="Corner Radius",
        description="Radius of the rounded inside front corner",
        default=const.L_CORNER_RADIUS, min=0.0, unit='LENGTH',
        precision=4,
        update=_update_starter_prop)  # type: ignore
    # Which shelves take the rounded corner. All three on is the way
    # the prior library had it; turning one off cuts that shelf square
    # instead.
    l_radius_top: BoolProperty(
        name="Radius Top",
        description="Round the front corner of the top shelf",
        default=True,
        update=_update_starter_prop)  # type: ignore
    l_radius_shelves: BoolProperty(
        name="Radius Shelves",
        description="Round the front corner of the shelves between the "
                    "top and the bottom",
        default=True,
        update=_update_starter_prop)  # type: ignore
    l_radius_bottom: BoolProperty(
        name="Radius Bottom",
        description="Round the front corner of the bottom shelf",
        default=True,
        update=_update_starter_prop)  # type: ignore
    l_add_cleat: BoolProperty(
        name="Add Cleat",
        description="Stand a cleat against each of the two walls for "
                    "the unit to be fixed with",
        default=False,
        update=_update_starter_prop)  # type: ignore


# ---------------------------------------------------------------------------
# Object-level: bay
# ---------------------------------------------------------------------------
class Closet_Bay_Props(PropertyGroup):

    bay_index: IntProperty(name="Bay Index", default=0)  # type: ignore

    width: FloatProperty(
        name="Width", description="Bay opening width",
        default=0.0, unit='LENGTH', precision=4,
        update=_update_bay_width)  # type: ignore
    unlock_width: BoolProperty(
        name="Unlock Width",
        description="Give this bay its own width, held while the rest "
                    "of the run is redistributed to fill the run width",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_width'],
        update=_update_bay_prop)  # type: ignore

    height: FloatProperty(
        name="Height", description="Bay height (envelope, floor to top shelf)",
        default=const.BASE_PANEL_HEIGHT, unit='LENGTH', precision=4,
        update=_update_bay_height)  # type: ignore
    unlock_height: BoolProperty(
        name="Unlock Height",
        description="Give this bay its own height instead of following "
                    "the run height",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_height'],
        update=_update_bay_prop)  # type: ignore
    height_preset: EnumProperty(
        name="Height",
        description="Standard section height on the 32mm system",
        items=_height_preset_items,
        default=const.PANEL_HEIGHT_DEFAULT_INDEX,
        update=_update_bay_height_preset)  # type: ignore
    depth: FloatProperty(
        name="Depth", description="Bay depth",
        default=const.DEFAULT_DEPTH, unit='LENGTH', precision=4,
        update=_update_bay_depth)  # type: ignore
    unlock_depth: BoolProperty(
        name="Unlock Depth",
        description="Give this bay its own depth instead of following "
                    "the run depth",
        default=starter_presets.BAY_PROP_DEFAULTS['unlock_depth'],
        update=_update_bay_prop)  # type: ignore

    floor_mounted: BoolProperty(
        name="Floor Mounted",
        description="Bay sits on the floor with a toe kick; off = the bay "
                    "hangs from its top height (top and bottom fixed shelves)",
        default=True, update=_update_bay_prop)  # type: ignore
    remove_bottom: BoolProperty(
        name="Remove Bottom",
        description="Leave this bay's fixed bottom shelf out. On a floor "
                    "bay the toe kick goes with it and the bay opens all "
                    "the way to the floor; on a hanging bay it opens to "
                    "the hang line",
        default=starter_presets.BAY_PROP_DEFAULTS['remove_bottom'],
        update=_update_bay_prop)  # type: ignore
    remove_cleat: BoolProperty(
        name="Remove Cleat",
        description="Leave this bay's wall cleat out",
        default=starter_presets.BAY_PROP_DEFAULTS['remove_cleat'],
        update=_update_bay_prop)  # type: ignore
    remove_shelf_cleat: BoolProperty(
        name="Remove Shelf Cleat",
        description="Leave out the cleat that stands behind this bay's "
                    "mid shelf",
        default=starter_presets.BAY_PROP_DEFAULTS['remove_shelf_cleat'],
        update=_update_bay_prop)  # type: ignore
    bottom_shelf_inset: FloatProperty(
        name="Bottom Shelf Inset",
        description="Hold this bay's bottom shelf off the wall by this "
                    "much on top of the run-wide Inset Bottom",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore
    # Numbered the way the prior library numbered it: the checkbox for a
    # doubled junction belongs to the bay on its LEFT, so a four bay run
    # offers Double Panel 1, 2 and 3 for its three shared partitions.
    double_panel_right: BoolProperty(
        name="Double Panel",
        description="Add a second partition at the junction on this bay's "
                    "right, so this bay and its right neighbor each get "
                    "their own panel",
        default=False, update=_update_bay_prop)  # type: ignore

    # Double-sided islands only: the divider between the two faces. As
    # the reference version had it, the divider is always there; ticked it
    # sits centered, unticked it sits at Center Back Location, measured
    # in from the island's FRONT face, and both faces' openings size to
    # it (reference add_double_opening).
    include_center_back: BoolProperty(
        name="Center Back",
        description="Keep this bay's divider centered between the two "
                    "faces. Untick to place it with Center Back Location",
        default=True, update=_update_bay_prop)  # type: ignore
    center_back_location: FloatProperty(
        name="Center Back Location",
        description="How far in from the island's front face the divider "
                    "sits - the depth of the front opening. The back "
                    "opening takes what is left behind the divider",
        default=0.0, min=0.0, unit='LENGTH', precision=4,
        update=_update_bay_prop)  # type: ignore
    # Files saved while the checkbox above meant "include the divider"
    # could have it switched off. That is carried over here so those
    # islands come back without one; nothing new sets it.
    remove_center_back: BoolProperty(
        name="Remove Center Back",
        description="Leave this bay's divider out (set by an older file)",
        default=False, update=_update_bay_prop)  # type: ignore

    # ----- Bay-wide front -----
    # A front that spans the whole bay rather than one opening. Held as a
    # string for the same reason the opening's front is: an empty value
    # has to be tellable from a choice, and empty means no bay-wide
    # front at all.
    door_swing: bpy.props.StringProperty(
        name="Door",
        description="Front spanning the whole bay: LEFT, RIGHT, DOUBLE, "
                    "LIFT_UP or TILT_OUT. Empty leaves the bay's "
                    "openings to carry their own fronts",
        default='', update=_update_bay_prop)  # type: ignore
    # The same on a double island's back face (the reference hung doors on its back
    # opening as on its front). Empty for every other run.
    back_door_swing: bpy.props.StringProperty(
        name="Back Door",
        description="Front spanning the whole bay on a double island's "
                    "back face: LEFT, RIGHT, DOUBLE, LIFT_UP or TILT_OUT. "
                    "Empty leaves the back openings their own fronts",
        default='', update=_update_bay_prop)  # type: ignore
    # A tilt-out hamper is one of the fronts the bay can carry now, so
    # it is read off door_swing rather than held beside it. This is kept
    # only so a bay drawn before the change still comes back a hamper:
    # it is read once and put back. See carry_over_hampers().
    is_hamper: BoolProperty(
        name="Tilt Out Hamper",
        default=False, update=_update_bay_prop)  # type: ignore
    # How far a bay-wide front is drawn standing open. Purely a drawing
    # setting: it moves the front and nothing else.
    open_door: FloatProperty(
        name="Open Door",
        description="How far the front across this bay is drawn standing "
                    "open. For the drawing only",
        default=0.0, min=0.0, max=100.0,
        subtype='PERCENTAGE', precision=0,
        update=_update_bay_open_door)  # type: ignore


# ---------------------------------------------------------------------------
# Object-level: opening
# ---------------------------------------------------------------------------
class Closet_Opening_Props(PropertyGroup):
    """What fills one opening, on that opening's cage object.

    Every default here is the EMPTY state, not the state the Change
    Opening dialog offers when you pick an interior. An untouched opening
    reads zero shelves, zero drawers, one cubby column, no front - which
    is what an untouched opening is. The dialog carries its own starting
    numbers (three shelves, three drawers, and so on) and only writes them
    here once the user accepts them.

    Deliberately no update callbacks. An opening is edited through the
    Change Opening dialog, which writes the whole set at once and then
    recalculates the run a single time. Callbacks here would fire a full
    recalculation per field written.
    """

    # Note on what is NOT here: which face of a double-sided island an
    # opening serves stays a plain idprop (hb_opening_side). It is stamped
    # on splitting shelves as well as on openings, so it is a tag the
    # whole tree is sorted by rather than a setting one opening owns.

    # ----- Adjustable shelves -----
    adj_shelf_qty: IntProperty(
        name="Shelf Quantity",
        description="How many adjustable shelves to space through the "
                    "opening",
        default=0, min=0, max=12)  # type: ignore
    # The count follows the opening's height (one shelf per foot, the
    # prior library's rule) until someone takes it over, so a resize
    # re-deals the shelves. The padlock in the shelf dialog sets this.
    unlock_adj_qty: BoolProperty(
        name="Shelf Quantity Lock",
        description="Hold the shelf count typed here instead of "
                    "following the opening's height",
        default=False)  # type: ignore
    # How the shelves in this opening are cut. Both figures are the
    # room's until this opening takes one over, which is what the
    # unlock flags say. They describe how a shelf is made rather than
    # what is in the opening, so like the overlays they are
    # deliberately not contents: stripping an opening empties it
    # without losing the way its shelves were cut.
    unlock_shelf_clip_gap: BoolProperty(
        name="Clip Gap",
        description="Set this opening's shelf clip gap here instead "
                    "of following the room",
        default=False)  # type: ignore
    shelf_clip_gap: FloatProperty(
        name="Clip Gap",
        description="How much narrower than the opening each shelf is "
                    "cut, per side, so it drops onto its clips",
        default=const.SHELF_CLIP_GAP,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    unlock_shelf_setback: BoolProperty(
        name="Setback",
        description="Set this opening's shelf setback here instead of "
                    "following the room",
        default=False)  # type: ignore
    shelf_setback: FloatProperty(
        name="Setback",
        description="How far back from the front edge of the opening "
                    "each shelf stops",
        default=const.SHELF_SETBACK,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    # ----- Drawers -----
    drawer_qty: IntProperty(
        name="Drawer Quantity",
        description="How many drawers to stack in the opening",
        default=0, min=0, max=10)  # type: ignore
    drawer_front_height: FloatProperty(
        name="Front Height",
        description="Height of a drawer front the opening holds; fronts "
                    "left to share split what the opening has left "
                    "equally",
        default=const.DRAWER_FRONT_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore
    # Held as a plain string rather than an enum so an opening keeps a box
    # system that is not in the current list, and so an empty value can
    # mean "no override" alongside the explicit 'DEFAULT'.
    drawer_box_override: bpy.props.StringProperty(
        name="Drawer Box",
        description="Which drawer box to build instead of the one the "
                    "opening size would pick on its own. Empty or DEFAULT "
                    "defers to the scene setting",
        default='')  # type: ignore
    drawer_stretcher_width: FloatProperty(
        name="Drawer Stretcher Width",
        description="How far back from the front the stretcher "
                    "between one drawer and the next runs",
        default=const.DRAWER_STRETCHER_WIDTH, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Pull-out trays -----
    rollout_qty: IntProperty(
        name="Rollout Quantity",
        description="How many pull-out trays to space through the opening",
        default=0, min=0, max=12)  # type: ignore
    rollout_height: FloatProperty(
        name="Rollout Height", description="Height of each tray",
        default=const.ROLLOUT_HEIGHT,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Slanted shoe shelves -----
    slant_qty: IntProperty(
        name="Shoe Shelf Quantity",
        description="How many slanted shoe shelves to stack from the "
                    "bottom of the opening up",
        default=0, min=0, max=10)  # type: ignore
    slant_spacing: FloatProperty(
        name="Distance Between Shelves",
        description="Vertical spacing from one shoe shelf to the next",
        default=const.SLANT_SHELF_SPACING,
        unit='LENGTH', precision=4)  # type: ignore
    slant_angle: FloatProperty(
        name="Shelf Angle",
        description="How far the shoe shelves tilt up toward the front",
        # A shoe shelf that is not tilted is just a shelf, so the standard
        # tilt is the default rather than zero. An opening with no shoe
        # shelves in it still reports this angle; nothing reads it until
        # the shelf quantity goes above zero.
        default=math.radians(const.SLANT_SHELF_ANGLE_DEG),
        subtype='ANGLE', unit='ROTATION')  # type: ignore
    slant_color: bpy.props.StringProperty(
        name="Fence Color",
        description="Finish of the metal shoe fence across the front of "
                    "each shelf",
        default='')  # type: ignore
    # Which line the fences are bought from. Blank is the library's own
    # fence; a host that sells another line of fences names it here, and
    # prices and offers it for itself.
    slant_fence_line: bpy.props.StringProperty(
        name="Fence Line",
        description="Which line of shoe fences the shelves carry",
        default='')  # type: ignore
    # The fence is a bought rail, so it is cut shorter than the shelf and
    # held off each end. Both figures are the prior library's.
    slant_fence_inset: FloatProperty(
        name="Metal Lip Width Inset",
        description="How far in from each end of the shelf the metal "
                    "fence starts. The fence is cut to suit",
        default=const.SHOE_FENCE_INSET, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore
    slant_back_inset: FloatProperty(
        name="Back Inset",
        description="How far back from the front edge of the shelf the "
                    "metal fence stands",
        default=const.SHOE_FENCE_BACK_INSET, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore
    # The reference's Slanted Shoe Shelves' Vertical Location: how far up the
    # opening the stack starts. Nothing means the opening floor.
    slant_z: FloatProperty(
        name="Vertical Location",
        description="Height of the bottom shoe shelf off the floor of "
                    "the opening",
        default=0.0, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Cubbies -----
    # One column by one row is "no cubbies"; the regenerator only builds
    # divisions once either count goes above one.
    cubby_cols: IntProperty(
        name="Columns", description="How many cubbies across the opening",
        default=1, min=1, max=12)  # type: ignore
    cubby_rows: IntProperty(
        name="Rows", description="How many cubbies up the opening",
        default=1, min=1, max=12)  # type: ignore
    cubby_setback: FloatProperty(
        name="Setback",
        description="How far the cubby divisions and shelves sit back "
                    "from the front edge of the opening",
        default=const.CUBBY_SETBACK,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    # Where the grid went when it was put in (the reference's Cubbies kept its
    # Placement and Cubby Height editable): a band at the bottom or top
    # capped by a shelf, or the whole opening. Read back by the Cubbies
    # and Opening dialogs so the band can be resized or moved later.
    cubby_placement: EnumProperty(
        name="Placement",
        description="Whether the grid takes a band of the opening or "
                    "the whole of it",
        items=const.CUBBY_PLACEMENT_ITEMS, default='FILL')  # type: ignore
    cubby_height: FloatProperty(
        name="Cubby Height",
        description="How tall the band of cubbies stands",
        default=const.CUBBY_HEIGHT, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Front -----
    # Empty means no front. Held as a string for the same reason as the
    # box override: an empty value has to be distinguishable from a choice.
    door_swing: bpy.props.StringProperty(
        name="Door",
        description="Front on this opening: LEFT, RIGHT, DOUBLE, "
                    "LIFT_UP or TILT_OUT. Empty leaves the opening open",
        default='')  # type: ignore
    # Read off door_swing now, the same as the bay's. Kept only so an
    # opening drawn before the change still comes back a hamper; read
    # once and put back. See carry_over_hampers().
    is_hamper: BoolProperty(
        name="Tilt Out Hamper",
        default=False)  # type: ignore

    # ----- Hang rod -----
    # One opening's worth of rod settings. How far the rod stands off the
    # wall, how much shorter than the opening it is cut, and whether it
    # is shown hung. They sit on the opening rather than on the rod for
    # the same reason every other setting does: the opening is the cage
    # the user edits, and the rod under it is placed by the solve.
    rod_set_from_front: BoolProperty(
        name="Set Distance From Front",
        description="Measure the rod front to back from the front edge of "
                    "the opening instead of from the back",
        default=False)  # type: ignore
    rod_from_front: FloatProperty(
        name="Dim From Front",
        description="How far back from the front edge of the opening the "
                    "rod's centerline sits",
        default=const.ROD_FROM_FRONT,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_from_rear: FloatProperty(
        name="Dim From Rear",
        description="How far out from the back of the opening the rod's "
                    "centerline sits",
        default=const.ROD_FROM_REAR,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    rod_width_deduction: FloatProperty(
        name="Width Deduction",
        description="How much shorter than the opening the rod is cut, so "
                    "it drops into the cups at each end",
        default=const.ROD_WIDTH_DEDUCTION,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    remove_hangers: BoolProperty(
        name="Remove Hangers",
        description="Leave the display hangers off the rods in this "
                    "opening",
        default=False)  # type: ignore

    # ----- Front overlays -----
    # Per-side overrides of what the run works out. Unlocking a side
    # lets this opening's front reach further over, or hold further
    # back from, whatever it meets there - the opening against a
    # finished end, say, where the run's half overlay would run the
    # front off the edge. A side left locked follows the run.
    #
    # These say how a front sits rather than what is in the opening, so
    # they are deliberately not contents: stripping an opening empties
    # it without losing the way its front was set up.
    top_overlay: FloatProperty(
        name="Top Overlay",
        description="How far this opening's front reaches over the shelf "
                    "above it",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    bottom_overlay: FloatProperty(
        name="Bottom Overlay",
        description="How far this opening's front reaches over the shelf "
                    "below it",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    left_overlay: FloatProperty(
        name="Left Overlay",
        description="How far this opening's front reaches over the panel "
                    "on its left",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    right_overlay: FloatProperty(
        name="Right Overlay",
        description="How far this opening's front reaches over the panel "
                    "on its right",
        default=const.DEFAULT_OVERLAY, unit='LENGTH',
        precision=4)  # type: ignore
    unlock_top_overlay: BoolProperty(
        name="Unlock Top Overlay",
        description="Use this opening's own top overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore
    unlock_bottom_overlay: BoolProperty(
        name="Unlock Bottom Overlay",
        description="Use this opening's own bottom overlay instead of "
                    "the one the run works out",
        default=False)  # type: ignore
    unlock_left_overlay: BoolProperty(
        name="Unlock Left Overlay",
        description="Use this opening's own left overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore
    unlock_right_overlay: BoolProperty(
        name="Unlock Right Overlay",
        description="Use this opening's own right overlay instead of the "
                    "one the run works out",
        default=False)  # type: ignore

    # How the pulls sit on this opening's fronts. The room's Options
    # tab sets what every opening starts from; unlocking a setting keeps
    # it to this opening, which is how one bank of wide drawers ends up
    # with a pair of pulls apiece while the rest of the run stays
    # single. Left out of the contents list below on purpose: stripping
    # an opening empties it, it does not re-hardware the job.
    no_pulls: BoolProperty(
        name="No Pulls",
        description="Draw this opening's fronts without pulls",
        default=False)  # type: ignore
    unlock_center_pull: BoolProperty(
        name="Centered",
        description="Say here whether this opening's drawer pulls are "
                    "centered, instead of following the room",
        default=False)  # type: ignore
    center_pull_on_front: BoolProperty(
        name="Center Pull On Front",
        description="Center the pull on the height of the drawer front",
        default=True)  # type: ignore
    unlock_pull_location: BoolProperty(
        name="From Top",
        description="Set how far down this opening's drawer pulls sit, "
                    "instead of following the room",
        default=False)  # type: ignore
    drawer_pull_vertical_location: FloatProperty(
        name="Drawer Pull Vertical Location",
        description="Top of the drawer front to the middle of the pull",
        default=const.DRAWER_PULL_VERTICAL_LOCATION,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    door_pull_location: EnumProperty(
        name="Door Pull Location",
        description="Which convention holds the pulls on this opening's "
                    "doors. Auto reads it off where the door sits",
        items=const.DOOR_PULL_LOCATION_ITEMS,
        default='AUTO')  # type: ignore
    unlock_door_pull_vertical: BoolProperty(
        name="From Top/Bottom",
        description="Set how high this opening's door pulls sit, instead "
                    "of following the room. Read the way the convention "
                    "above reads it: Base down from the door top, Upper "
                    "up from the door bottom, Tall up from the door "
                    "bottom",
        default=False)  # type: ignore
    door_pull_vertical_location: FloatProperty(
        name="Door Pull Vertical Location",
        description="To the near end of the pull",
        default=const.DOOR_PULL_VERTICAL_LOCATION,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    unlock_door_pull_edge: BoolProperty(
        name="From Edge",
        description="Set how far in from the latch edge this opening's "
                    "door pulls sit, instead of following the room",
        default=False)  # type: ignore
    door_pull_horizontal_offset: FloatProperty(
        name="Door Pull From Edge",
        description="Latch edge of the door to the pull center",
        default=const.DOOR_PULL_FROM_EDGE,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore
    double_pull_on_front: BoolProperty(
        name="Double Pull On Front",
        description="Put two pulls on each of this opening's drawer "
                    "fronts instead of one",
        default=False)  # type: ignore
    distance_between_pulls: FloatProperty(
        name="Distance Between Pulls",
        description="Middle to middle of the two pulls on a front",
        default=const.DISTANCE_BETWEEN_PULLS,
        min=0.0, unit='LENGTH', precision=4)  # type: ignore

    # Which way the grain runs on this opening's drawer fronts. Left
    # on Use Default they follow the room's Vertical Grain setting; a
    # single drawer can still be turned the other way in its own
    # Drawer Options. Left out of the contents list below on purpose,
    # same as the overlays and the pulls: stripping an opening empties
    # it, it does not re-finish it.
    drawer_grain: EnumProperty(
        name="Grain",
        description="Which way the grain runs on this opening's "
                    "drawer fronts, instead of following the room",
        items=materials_closets.GRAIN_OVERRIDE_ITEMS,
        default='DEFAULT')  # type: ignore

    # ----- Captured back -----
    # A back that closes this opening on its own, held between the
    # panels and shelves around it. Independent of the interior: an
    # opening can be backed whatever is standing in front of it.
    add_back: BoolProperty(
        name="Add Back",
        description="Close this opening with a back held between the "
                    "panels and shelves around it",
        default=False)  # type: ignore
    back_inset: FloatProperty(
        name="Inset",
        description="How far forward of the back of the opening the "
                    "back sits",
        default=0.0, min=0.0, unit='LENGTH', precision=4)  # type: ignore
    back_notch_left: BoolProperty(
        name="Left",
        description="Relieve the top left corner of the back",
        default=False)  # type: ignore
    back_notch_right: BoolProperty(
        name="Right",
        description="Relieve the top right corner of the back",
        default=False)  # type: ignore
    back_notch_width: FloatProperty(
        name="Notch Width",
        description="How far in from the side each corner relief cuts",
        default=const.CAPTURED_BACK_NOTCH_WIDTH, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore
    back_notch_height: FloatProperty(
        name="Notch Height",
        description="How far down from the top each corner relief cuts",
        default=const.CAPTURED_BACK_NOTCH_HEIGHT, min=0.0,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Drawn standing open -----
    # How far the fronts here are drawn open, so a drawing can show what
    # is inside. They move the fronts and nothing else - sizes, parts
    # and hardware read the same open or closed. Clicking one front in
    # Open Door mode says the same thing about that one front, and what
    # it says outranks these until the number here is changed again.
    open_door: FloatProperty(
        name="Open Door",
        description="How far the doors on this opening are drawn standing "
                    "open. For the drawing only",
        default=0.0, min=0.0, max=100.0,
        subtype='PERCENTAGE', precision=0)  # type: ignore
    open_drawer: FloatProperty(
        name="Open Drawer",
        description="How far the drawers in this opening are drawn "
                    "standing open. For the drawing only",
        default=0.0, min=0.0, max=100.0,
        subtype='PERCENTAGE', precision=0)  # type: ignore

    # Every field on this group is contents, so stripping an opening
    # clears the lot. Kept as an explicit list so a field added later has
    # to be considered rather than silently surviving a clear.
    CONTENTS_FIELDS = (
        'adj_shelf_qty',
        'drawer_qty', 'drawer_front_height', 'drawer_box_override',
        'drawer_stretcher_width',
        'rollout_qty', 'rollout_height',
        'slant_qty', 'slant_spacing', 'slant_angle', 'slant_color',
        'slant_fence_line', 'slant_fence_inset', 'slant_back_inset',
        'slant_z',
        'cubby_cols', 'cubby_rows', 'cubby_setback',
        'cubby_placement', 'cubby_height',
        'door_swing', 'is_hamper',
        'rod_set_from_front', 'rod_from_front', 'rod_from_rear',
        'rod_width_deduction', 'remove_hangers',
        'add_back', 'back_inset',
        'back_notch_left', 'back_notch_right',
        'back_notch_width', 'back_notch_height',
        'open_door', 'open_drawer',
    )

    def clear_contents(self):
        """Put every field back to its empty default."""
        for name in self.CONTENTS_FIELDS:
            self.property_unset(name)


# ---------------------------------------------------------------------------
# Scene-level: defaults + library UI
# ---------------------------------------------------------------------------
class Closets_Scene_Props(PropertyGroup):

    # ----- Defaults (seed new starters; existing starters keep their values) -----
    default_closet_width: FloatProperty(
        name="Default Width", default=const.DEFAULT_WIDTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_panel_depth: FloatProperty(
        name="Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    # Per-type panel depths. Seeded onto a new starter by
    # its closet type; default_panel_depth is the fallback.
    default_base_panel_depth: FloatProperty(
        name="Base Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_tall_panel_depth: FloatProperty(
        name="Tall Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_hanging_panel_depth: FloatProperty(
        name="Hanging Panel Depth", default=const.DEFAULT_DEPTH,
        unit='LENGTH', precision=4)  # type: ignore
    default_corner_closet_size: FloatProperty(
        name="Corner Closet Size", default=const.L_SHELF_SIZE,
        unit='LENGTH', precision=4)  # type: ignore
    default_accent_overhang: FloatProperty(
        name="Accent Shelf Overhang", default=const.TOP_ACCENT_OVERHANG,
        unit='LENGTH', precision=4)  # type: ignore
    # Whether a new run is built with its hang rails (the prior
    # library's Add Hanging Rail for closet starters). Seeds the run's
    # Remove Hang Rail; runs already in the room keep theirs.
    # Access gap left at a corner where a run meets a perpendicular one
    # (the reference version's Adjacent Closet Spacing). Seeds the Corner
    # Clearance dialog that placement opens; each corner keeps its own.
    corner_clearance: FloatProperty(
        name="Corner Clearance",
        description="Gap a new run leaves between its end and a "
                    "perpendicular closet at the corner",
        default=inch(12.0), min=0.0, unit='LENGTH',
        precision=4)  # type: ignore
    add_hanging_rail: BoolProperty(
        name="Add Hanging Rail",
        description="Build new closet runs with a hanging rail; each run "
                    "can still turn its own off or on",
        default=True)  # type: ignore
    base_panel_height: FloatProperty(
        name="Base Panel Height", default=const.BASE_PANEL_HEIGHT,
        unit='LENGTH', precision=4,
        update=_system_default_height('base_panel_height'))  # type: ignore
    tall_panel_height: FloatProperty(
        name="Tall Panel Height", default=const.TALL_PANEL_HEIGHT,
        unit='LENGTH', precision=4,
        update=_system_default_height('tall_panel_height'))  # type: ignore
    hanging_panel_height: FloatProperty(
        name="Hanging Panel Height", default=const.HANGING_PANEL_HEIGHT,
        unit='LENGTH', precision=4,
        update=_system_default_height('hanging_panel_height'))  # type: ignore
    hanging_top_height: FloatProperty(
        name="Hanging Top Height",
        description="Floor to the top of wall-mounted hanging starters",
        default=const.HANGING_TOP_HEIGHT, unit='LENGTH', precision=4,
        update=_system_default_height('hanging_top_height'))  # type: ignore
    # A part thickness, the shelf clip gap or setback changed: every
    # run that has not taken the figure over re-solves at once, as
    # the gaps and reveals below do.
    panel_thickness: FloatProperty(
        name="Panel Thickness", default=const.PANEL_THICKNESS,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    shelf_thickness: FloatProperty(
        name="Shelf Thickness", default=const.SHELF_THICKNESS,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    divider_thickness: FloatProperty(
        name="Cubby Divider Thickness",
        description="What the uprights in a cubby grid are cut from. "
                    "The shelves across the grid follow the shelf "
                    "thickness",
        default=const.DIVIDER_THICKNESS,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    batten_thickness: FloatProperty(
        name="Batten Thickness",
        description="How thick the scribe strip on the end of a run is",
        default=const.BATTEN_THICKNESS,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    batten_width: FloatProperty(
        name="Batten Width",
        description="How wide the scribe strip on the end of a run is. "
                    "Whatever it carries past the panel edge is what "
                    "there is to scribe to the wall",
        default=const.BATTEN_WIDTH,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    # The room's standard for how a shelf on clips is cut. An opening
    # can take either figure over for itself.
    shelf_clip_gap: FloatProperty(
        name="Shelf Clip Gap", default=const.SHELF_CLIP_GAP,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    shelf_setback: FloatProperty(
        name="Shelf Setback", default=const.SHELF_SETBACK,
        min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    countertop_thickness: FloatProperty(
        name="Countertop Thickness", default=const.COUNTERTOP_THICKNESS,
        unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    # The room's kick is picked from the 32mm kick list the way the reference's
    # Default Toe Kick Height was. The dropdown holds nothing of its own:
    # it reads and writes toe_kick_height, which placement and Update Toe
    # Kicks copy to the runs. A height off the list (a file made before
    # the list) reads as Custom and keeps its typed distance.
    toe_kick_height_preset: EnumProperty(
        name="Toe Kick Height",
        description="Standard toe-kick height for closets placed in "
                    "this room",
        items=_ROOM_KICK_ITEMS,
        get=_get_room_kick_preset,
        set=_set_room_kick_preset)  # type: ignore
    # Custom picked on the dropdown: the typed distance is shown and
    # kept even when it lands on a standard kick. A distance off the
    # list reads as Custom without it.
    toe_kick_custom: BoolProperty(
        name="Custom Toe Kick Height", default=False,
        options={'HIDDEN'})  # type: ignore
    toe_kick_height: FloatProperty(
        name="Toe Kick Height", default=const.DEFAULT_TOE_KICK_HEIGHT,
        unit='LENGTH', precision=4,
        update=_update_room_kick_height)  # type: ignore
    toe_kick_setback: FloatProperty(
        name="Toe Kick Setback", default=const.DEFAULT_TOE_KICK_SETBACK,
        unit='LENGTH', precision=4)  # type: ignore

    # ----- Fronts -----
    # How every door and drawer front in the room hangs. These are the
    # room's figures - every run hangs its fronts the same way, so they
    # live here rather than in a starter dialog. A half overlay splits
    # what the front shares with its neighbour: the two meet over the
    # middle of the panel or shelf between them and the gap is what
    # shows. Turning a side off holds the front back from that edge by
    # the reveal instead, which is how a finished end or a top is left
    # showing. Left and right work off the panel thickness and the
    # horizontal gap, top and bottom off the shelf thickness and the
    # vertical gap. Any opening can still take a side over for itself.
    door_to_cabinet_gap: FloatProperty(
        name="Door to Cabinet Gap",
        description="How far the back of a front is held off the front "
                    "edge of the closet",
        default=const.DOOR_TO_CABINET_GAP, min=0.0, unit='LENGTH',
        precision=4, update=_update_room_solve)  # type: ignore
    vertical_gap: FloatProperty(
        name="Vertical Gap",
        description="Gap between a front and the front above or below it",
        default=const.VERTICAL_GAP, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    horizontal_gap: FloatProperty(
        name="Horizontal Gap",
        description="Gap between a front and the front beside it",
        default=const.HORIZONTAL_GAP, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    half_overlay_top: BoolProperty(
        name="Half Overlay Top",
        description="Share the shelf above with the front over it, "
                    "rather than holding back by the top reveal",
        default=True, update=_update_room_solve)  # type: ignore
    half_overlay_bottom: BoolProperty(
        name="Half Overlay Bottom",
        description="Share the shelf below with the front under it, "
                    "rather than holding back by the bottom reveal",
        default=True, update=_update_room_solve)  # type: ignore
    half_overlay_left: BoolProperty(
        name="Half Overlay Left",
        description="Share the panel on the left with the front beside "
                    "it, rather than holding back by the left reveal",
        default=True, update=_update_room_solve)  # type: ignore
    half_overlay_right: BoolProperty(
        name="Half Overlay Right",
        description="Share the panel on the right with the front beside "
                    "it, rather than holding back by the right reveal",
        default=True, update=_update_room_solve)  # type: ignore
    top_reveal: FloatProperty(
        name="Top Reveal",
        description="How much of the shelf above is left showing when "
                    "the top is not a half overlay",
        default=const.TOP_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    bottom_reveal: FloatProperty(
        name="Bottom Reveal",
        description="How much of the shelf below is left showing when "
                    "the bottom is not a half overlay",
        default=const.BOTTOM_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    left_reveal: FloatProperty(
        name="Left Reveal",
        description="How much of the panel on the left is left showing "
                    "when the left is not a half overlay",
        default=const.LEFT_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore
    right_reveal: FloatProperty(
        name="Right Reveal",
        description="How much of the panel on the right is left showing "
                    "when the right is not a half overlay",
        default=const.RIGHT_REVEAL, min=0.0, unit='LENGTH', precision=4,
        update=_update_room_solve)  # type: ignore

    # ----- Selection modes -----
    closet_selection_mode: EnumProperty(
        name="Closet Selection Mode",
        items=[
            ('Starters', "Starters", "Select whole closet starters"),
            ('Bays', "Bays", "Select bay cages"),
            ('Openings', "Openings", "Select opening cages"),
            ('Parts', "Parts", "Select individual parts"),
        ],
        default='Starters',
        update=_update_closet_selection_mode)  # type: ignore
    closet_selection_mode_enabled: BoolProperty(
        name="Enable Closet Selection Mode",
        description="Highlight objects matching the active selection mode",
        default=True,
        update=_update_closet_selection_mode)  # type: ignore

    selection_mode_show_sizes: BoolProperty(
        name="Show Sizes",
        description="Show editable dimension labels in selection modes",
        default=True)  # type: ignore

    # ----- Options (materials / fronts / pulls / drawer boxes /
    # molding). Selections live at scene level and re-apply to the
    # whole room on change; new placements pick them up at finish
    # time. Materials is the first category wired up - the remaining
    # dropdowns land one category at a time.
    closet_material: EnumProperty(
        name="Closet Material",
        description="Carcass material (panels, shelves, kicks, tops)",
        items=materials_closets.material_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_front_material: EnumProperty(
        name="Front Material",
        description="Door and drawer front material (Match Closet "
                    "follows the closet material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_edge_material: EnumProperty(
        name="Closet Edgebanding",
        description="Edgebanding on closet parts (Match = the closet "
                    "material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore
    closet_front_edge_material: EnumProperty(
        name="Front Edgebanding",
        description="Edgebanding on doors and drawer fronts (Match = "
                    "the fronts material)",
        items=materials_closets.match_enum_items,
        update=materials_closets.update_room)  # type: ignore

    closet_countertop_material: EnumProperty(
        name="Countertop Material",
        description="Surface material on countertops and their "
                    "backsplashes",
        items=materials_closets.countertop_material_enum_items,
        update=materials_closets.update_room)  # type: ignore
    use_closet_material_for_countertops: BoolProperty(
        name="Use Closet Material for Countertops",
        description="Surface the tops in the closet material instead "
                    "of a countertop material, so the run reads as one "
                    "piece. Tops then take the shelf thickness",
        default=False,
        update=_update_countertop_mode)  # type: ignore

    closet_panel_type: EnumProperty(
        name="Door Panel",
        description="Center panel on 5-piece doors and drawer fronts: "
                    "wood or glass",
        items=materials_closets.PANEL_TYPES,
        default='Vertical Grain',
        update=materials_closets.update_room)  # type: ignore
    # Grain on the drawer fronts. Doors always run vertical, so this
    # is the only grain choice the room makes; a single drawer can
    # still be turned the other way in its own Drawer Options.
    closet_drawer_vertical_grain: BoolProperty(
        name="Vertical Grain",
        description="Run the grain up the drawer fronts instead of "
                    "across them",
        default=False,
        update=materials_closets.update_drawer_grain)  # type: ignore

    closet_pull: EnumProperty(
        name="Pull",
        description="Handle used on the closet doors (and on the drawer "
                    "fronts unless they have a pull of their own)",
        items=pulls_closets.pull_enum_items,
        update=pulls_closets.update_room)  # type: ignore
    closet_drawer_pull: EnumProperty(
        name="Drawer Pull",
        description="Handle used on the drawer fronts",
        items=pulls_closets.drawer_pull_enum_items,
        update=pulls_closets.update_room)  # type: ignore
    closet_custom_pull_size: FloatProperty(
        name="Pull Size",
        description="Center to center of the Custom pull's mounting holes",
        default=0.096, min=0.01, unit='LENGTH', precision=4,
        update=pulls_closets.update_room)  # type: ignore
    closet_pull_finish: EnumProperty(
        name="Pull Finish",
        items=pulls_closets.PULL_FINISHES,
        default='Polished Chrome',
        update=pulls_closets.update_room)  # type: ignore
    pull_horizontal_offset: FloatProperty(
        name="From Edge",
        description="Latch edge of the door to the pull center, on every "
                    "door - slab and five-piece alike",
        default=units.inch(1.5), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_base: FloatProperty(
        name="Base",
        description="Top of a base door to the top of the pull",
        default=units.inch(2.0), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_tall: FloatProperty(
        name="Tall",
        description="Pull height up from the bottom of a tall door to "
                    "the pull",
        default=units.inch(45.0), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_upper: FloatProperty(
        name="Upper",
        description="Bottom of an upper door to the bottom of the pull",
        default=units.inch(2.0), unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore
    center_pulls_on_drawer_front: BoolProperty(
        name="Center Pulls on Drawer Fronts",
        default=True,
        update=pulls_closets.update_room)  # type: ignore
    pull_vertical_location_drawers: FloatProperty(
        name="Drawer",
        description="Top of the drawer front to the middle of the pull",
        default=const.DRAWER_PULL_VERTICAL_LOCATION, unit='LENGTH',
        update=pulls_closets.update_room)  # type: ignore

    closet_rod_type: EnumProperty(
        name="Rod Type",
        items=pulls_closets.ROD_TYPES,
        default='OVAL',
        update=_update_rod_options)  # type: ignore
    closet_rod_finish: EnumProperty(
        name="Rod Finish",
        items=pulls_closets.ROD_FINISHES,
        default='Polished Chrome',
        update=_update_rod_options)  # type: ignore
    closet_hanger_model: EnumProperty(
        name="Hangers",
        description="Display hanger model shown on closet rods",
        items=pulls_closets.hanger_enum_items,
        update=_update_rod_options)  # type: ignore

    # What accessories are made in unless one is set otherwise: new
    # ones arrive in it, and changing it re-dresses the room's. One not
    # made in it is made in black, and the Accessories section says so.
    default_accessory_color: EnumProperty(
        name="Accessory Finish",
        description="Metal finish every closet accessory is made in. "
                    "One not offered in it is made in black",
        items=accessories_closets.ACCESSORY_COLOR_ITEMS,
        default=accessories_closets.FALLBACK_COLOR,
        update=accessories_closets.update_room_finishes)  # type: ignore
    default_accessory_fabric: EnumProperty(
        name="Accessory Fabric",
        description="Fabric every closet accessory with a fabric is "
                    "made in. One not offered in it is made in black, "
                    "or the first fabric it comes in",
        items=accessories_closets.ACCESSORY_FABRIC_ITEMS,
        default='Fabric Slate',     # the reference's default fabric
        update=accessories_closets.update_room_finishes)  # type: ignore

    closet_drawer_box: EnumProperty(
        name="Drawer Box",
        description="Drawer box system used by every closet drawer",
        items=drawer_boxes_closets.BOX_TYPES,
        default='AVANTECH',
        update=drawer_boxes_closets.update_room)  # type: ignore

    closet_front_style: EnumProperty(
        name="Front Style",
        description="Door and drawer front style for every closet front",
        items=fronts_closets.FRONT_STYLES,
        default='SLAB',
        update=fronts_closets.update_room)  # type: ignore
    # The reference's Update Doors in Room: a style change can restyle the doors,
    # the drawer fronts, or both. The kind left out keeps the style it
    # had (fronts_closets.update_room).
    front_style_update_doors: BoolProperty(
        name="Update Doors",
        description="Restyle the doors in the room when the front style "
                    "changes. Off, they keep the style they have",
        default=True,
        update=fronts_closets.note_room_style)  # type: ignore
    front_style_update_drawer_fronts: BoolProperty(
        name="Update Drawer Fronts",
        description="Restyle the drawer fronts in the room when the "
                    "front style changes. Off, they keep the style they "
                    "have",
        default=True,
        update=fronts_closets.note_room_style)  # type: ignore

    closet_seed_door_shelves: BoolProperty(
        name="Shelves Behind Doors",
        description="Put adjustable shelves into an opening when a "
                    "door is added to it, where the opening is still "
                    "empty. Off, adding a door adds nothing else, the "
                    "way the reference version did",
        default=False)  # type: ignore

    notch_panels_for_base_board: BoolProperty(
        name="Notch Panels for Base Board",
        description="Notch the bottom rear of partitions standing on the "
                    "floor around the room's baseboard. Off, the "
                    "baseboard is cut on site",
        default=True, update=_update_room_solve)  # type: ignore
    closet_door_edgeband: EnumProperty(
        name="Door Edgebanding",
        description="How thick the fronts' edgebanding is bought - "
                    "the room-wide choice the prior library offered. "
                    "Companion systems read it for what a front's "
                    "edges cost and how long they take to run",
        items=[('1MM', "1mm", "Standard 1mm edgebanding"),
               ('3MM', "3mm", "Heavy 3mm edgebanding")],
        default='1MM')  # type: ignore

    closet_crown_profile: EnumProperty(
        name="Crown Profile",
        description="Profile used by Add Crown Molding",
        items=molding_closets.profile_enum_items)  # type: ignore

    closet_base_profile: EnumProperty(
        name="Base Profile",
        description="Profile used by Add Base Molding",
        items=molding_closets.base_profile_enum_items)  # type: ignore

    # ----- Library UI state -----
    closet_tabs: EnumProperty(
        name="Closet Tabs",
        items=[
            ('LIBRARY', "Library", "Library"),
            ('OPTIONS', "Options", "Options"),
        ],
        default='LIBRARY')  # type: ignore

    library_view_mode: EnumProperty(
        name="Library View",
        description="Show library items as thumbnail tiles or a compact list",
        items=[
            ('THUMBNAIL', "Thumbnail", "Thumbnail tiles with previews",
             'IMGDISPLAY', 0),
            ('LIST', "List", "Compact list of names", 'LONGDISPLAY', 1),
        ],
        default='THUMBNAIL')  # type: ignore

    # ---- Library tab section toggles ----
    show_closet_sizes: BoolProperty(
        name="Show Closet Sizes", default=False)  # type: ignore
    show_starter_library: BoolProperty(
        name="Show Closet Starters", default=True)  # type: ignore
    show_thickness_sizes: BoolProperty(
        name="Show Part Thicknesses", default=False)  # type: ignore
    show_shelf_sizes: BoolProperty(
        name="Show Shelf Sizes", default=False)  # type: ignore
    show_toe_kick_sizes: BoolProperty(
        name="Show Toe Kick Sizes", default=False)  # type: ignore

    # The marking on fixed shelves and finished ends (reference Lock Shelf
    # Color). The default stays the library's stronger orange rather
    # than the reference's peach (see const.LOCK_SHELF_COLOR).
    lock_shelf_color: FloatVectorProperty(
        name="Lock Shelf Color",
        description="Viewport colour marking fixed (locked) shelves and "
                    "finished end panels",
        subtype='COLOR_GAMMA', size=4, min=0.0, max=1.0,
        default=const.LOCK_SHELF_COLOR,
        update=_update_lock_shelf_color)  # type: ignore

    # ---- Options tab section toggles ----
    show_material_options: BoolProperty(
        name="Show Materials", default=False)  # type: ignore
    show_front_options: BoolProperty(
        name="Show Front Styles", default=False)  # type: ignore
    show_pull_options: BoolProperty(
        name="Show Pulls", default=False)  # type: ignore
    show_drawer_box_options: BoolProperty(
        name="Show Drawer Boxes", default=False)  # type: ignore
    show_rod_options: BoolProperty(
        name="Show Rods and Hangers", default=False)  # type: ignore
    show_accessory_options: BoolProperty(
        name="Show Accessories", default=False)  # type: ignore
    show_countertop_options: BoolProperty(
        name="Show Countertops", default=False)  # type: ignore
    show_molding_options: BoolProperty(
        name="Show Molding", default=False)  # type: ignore
    show_user_library: BoolProperty(
        name="My Closets", default=False)  # type: ignore
    show_design_warnings: BoolProperty(
        name="Show Design Warnings", default=True)  # type: ignore

    # =====================================================================
    # UI: closet sizes (Library tab)
    # =====================================================================
    def draw_closet_sizes_ui(self, layout, context):
        """Seed sizes for new starters. The three closet types share a
        depth / height grid so the columns read across; the values that
        belong to one type only sit under it."""
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Default Width:")
        row.prop(self, 'default_closet_width', text="")

        col.separator()
        row = col.row()
        row.label(text="Sizes")
        row.label(text="Base")
        row.label(text="Tall")
        row.label(text="Hanging")

        row = col.row()
        row.label(text="Depth:")
        row.prop(self, 'default_base_panel_depth', text="")
        row.prop(self, 'default_tall_panel_depth', text="")
        row.prop(self, 'default_hanging_panel_depth', text="")

        row = col.row()
        row.label(text="Height:")
        row.prop(self, 'base_panel_height', text="")
        row.prop(self, 'tall_panel_height', text="")
        row.prop(self, 'hanging_panel_height', text="")

        col.separator()
        # The fallback depth serves any starter whose type has no depth
        # of its own - the corner starters read it for both wings.
        row = col.row()
        row.label(text="Fallback Depth:")
        row.prop(self, 'default_panel_depth', text="")
        row = col.row()
        row.label(text="Hanging Top Height:")
        row.prop(self, 'hanging_top_height', text="")
        # Pushes the figure to the hanging closets already placed; a
        # new one takes it as it is placed.
        row.operator('hb_closets.update_hanging_heights', text="",
                     icon='FILE_REFRESH')
        row = col.row()
        row.label(text="Corner Size:")
        row.prop(self, 'default_corner_closet_size', text="")
        row = col.row()
        row.label(text="Accent Overhang:")
        row.prop(self, 'default_accent_overhang', text="")
        row = col.row()
        row.label(text="Corner Clearance:")
        row.prop(self, 'corner_clearance', text="")
        col.prop(self, 'add_hanging_rail')

        box = layout.box()
        box.prop(self, 'show_thickness_sizes', text="Part Thicknesses",
                 icon='TRIA_DOWN' if self.show_thickness_sizes
                 else 'TRIA_RIGHT', emboss=False)
        if self.show_thickness_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'panel_thickness', text="Panel")
            sub.prop(self, 'shelf_thickness', text="Shelf")
            sub.prop(self, 'divider_thickness', text="Cubby Divider")
            sub.prop(self, 'batten_thickness', text="Batten")
            sub.prop(self, 'batten_width', text="Batten Width")

        box = layout.box()
        box.prop(self, 'show_shelf_sizes', text="Adjustable Shelves",
                 icon='TRIA_DOWN' if self.show_shelf_sizes
                 else 'TRIA_RIGHT', emboss=False)
        if self.show_shelf_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'shelf_clip_gap', text="Clip Gap")
            sub.prop(self, 'shelf_setback', text="Setback")
            box.prop(self, 'lock_shelf_color', text="Lock Shelf Color")

        box = layout.box()
        row = box.row()
        row.prop(self, 'show_toe_kick_sizes', text="Toe Kick",
                 icon='TRIA_DOWN' if self.show_toe_kick_sizes
                 else 'TRIA_RIGHT', emboss=False)
        # Pushes height and setback to every closet already placed.
        row.operator('hb_closets.update_toe_kicks', text="",
                     icon='FILE_REFRESH')
        if self.show_toe_kick_sizes:
            sub = box.column(align=True)
            sub.prop(self, 'toe_kick_height_preset', text="Height")
            if self.toe_kick_height_preset == 'CUSTOM':
                sub.prop(self, 'toe_kick_height', text="Custom Height")
            sub.prop(self, 'toe_kick_setback', text="Setback")

    # =====================================================================
    # UI: starters (Library tab)
    # =====================================================================
    def draw_starter_library_ui(self, layout, context):
        """One row per section: the section label on the left, then a
        cell per product to its right. Thumbnail view puts a preview
        tile above each button; list view drops the tiles for a compact
        list of names. Bay count is derived from width at placement."""
        for sec_label, entries in starter_presets.STARTER_SECTIONS:
            row = layout.row(align=True)
            row.label(text=sec_label)
            for name, label, _desc in entries:
                cell = row.column(align=True)
                if self.library_view_mode == 'THUMBNAIL':
                    icon_id = load_starter_thumbnail(name)
                    if icon_id:
                        cell.template_icon(icon_value=icon_id, scale=4.0)
                op = cell.operator('hb_closets.place_starter', text=label)
                op.starter_name = name
        for sec_label, entries in starter_presets.PART_SECTIONS:
            row = layout.row(align=True)
            row.label(text=sec_label)
            for name, label, _desc, op_id, op_props in entries:
                cell = row.column(align=True)
                if self.library_view_mode == 'THUMBNAIL':
                    icon_id = load_starter_thumbnail(name)
                    if icon_id:
                        cell.template_icon(icon_value=icon_id, scale=4.0)
                op = cell.operator(op_id, text=label)
                for key, value in (op_props or {}).items():
                    setattr(op, key, value)

    # =====================================================================
    # UI: materials (Options tab)
    # =====================================================================
    def draw_material_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_material', text="Closet")
        col.prop(self, 'closet_front_material', text="Fronts")

        col.separator()
        col.label(text="Edgebanding:")
        col.prop(self, 'closet_edge_material', text="Closet Edge")
        col.prop(self, 'closet_front_edge_material', text="Front Edge")
        if materials_closets.front_edge_lacks_3mm(self):
            warn = col.box()
            warn.alert = True
            warn.label(text="Edgebanding Color not available in 3mm",
                       icon='ERROR')

    # =====================================================================
    # UI: door and drawer front styles (Options tab)
    # =====================================================================
    def draw_front_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_front_style', text="Front Style")
        row = col.row(align=True)
        row.prop(self, 'front_style_update_doors', text="Doors",
                 toggle=True)
        row.prop(self, 'front_style_update_drawer_fronts',
                 text="Drawer Fronts", toggle=True)
        col.prop(self, 'closet_panel_type', text="Door Panel")
        col.prop(self, 'closet_door_edgeband', text="Edgebanding")
        if materials_closets.front_edge_lacks_3mm(self):
            warn = col.box()
            warn.alert = True
            warn.label(text="Edgebanding Color not available in 3mm",
                       icon='ERROR')

        col.separator()
        col.prop(self, 'closet_seed_door_shelves',
                 text="Shelves Behind Doors")

        # Every front in the room stood open or shut at once, for the
        # drawing, where the reference kept its Open/Close Doors buttons.
        row = layout.row(align=True)
        op = row.operator('hb_closets.open_room_fronts',
                          text="Open Doors", icon='HIDE_OFF')
        op.open = True
        op.fronts = 'ALL'
        op = row.operator('hb_closets.open_room_fronts',
                          text="Close Doors", icon='HIDE_ON')
        op.open = False
        op.fronts = 'ALL'

        # How every front in the room hangs. Room figures - a change
        # here re-solves every run; any one opening can still take an
        # overlay side over for itself in its own dialog.
        col = layout.column(align=True)
        col.label(text="Gaps:")
        col.prop(self, 'door_to_cabinet_gap', text="Door to Cabinet")
        col.prop(self, 'vertical_gap', text="Vertical")
        col.prop(self, 'horizontal_gap', text="Horizontal")

        col = layout.column(align=True)
        col.label(text="Half Overlay / Reveal:")
        for side, label in (('top', "Top"), ('bottom', "Bottom"),
                            ('left', "Left"), ('right', "Right")):
            row = col.row(align=True)
            row.prop(self, 'half_overlay_%s' % side, text=label)
            sub = row.row(align=True)
            sub.enabled = not getattr(self, 'half_overlay_%s' % side)
            sub.prop(self, '%s_reveal' % side, text="")

    # =====================================================================
    # UI: pulls (Options tab)
    # =====================================================================
    def draw_pull_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_pull', text="Door Pull")
        col.prop(self, 'closet_drawer_pull', text="Drawer Pull")
        if pulls_closets.CUSTOM_PULL in (self.closet_pull,
                                         self.closet_drawer_pull):
            col.prop(self, 'closet_custom_pull_size',
                     text="Center to Center")
        col.prop(self, 'closet_pull_finish', text="Finish")

        col.separator()
        col.label(text="Position:")
        col.prop(self, 'pull_horizontal_offset', text="From Edge")
        col.prop(self, 'pull_vertical_location_base', text="Base Vertical")
        col.prop(self, 'pull_vertical_location_tall', text="Tall Vertical")
        col.prop(self, 'pull_vertical_location_upper', text="Upper Vertical")
        col.prop(self, 'center_pulls_on_drawer_front',
                 text="Center Drawer Pulls")
        # A tilt-out hamper takes this figure even where drawer pulls
        # are centered (the reference always offered it), so the row stays live;
        # while centered it is only the hampers' figure.
        col.prop(self, 'pull_vertical_location_drawers',
                 text=("Hamper Vertical"
                       if self.center_pulls_on_drawer_front
                       else "Drawer Vertical"))

    # =====================================================================
    # UI: drawers (Options tab)
    # =====================================================================
    def draw_design_warnings_ui(self, layout, context):
        """What the room has been asked to build that cannot be built
        at the size it has been given. Each part carries its own
        warning, written when it was last drawn, so this gathers what
        is already there rather than working anything out again."""
        from . import types_closets, molding_closets
        col = layout.column(align=True)
        found = []
        keys = (types_closets.PROP_BOX_WARNING,
                types_closets.PROP_ACCESSORY_WARNING,
                types_closets.PROP_STYLE_WARNING)
        no_shield = not molding_closets.light_shield_available(
            context.scene)
        for obj in context.scene.objects:
            seen = set()
            for key in keys:
                for message in str(obj.get(key, '') or '').split('; '):
                    if message and message not in seen:
                        seen.add(message)
                        found.append((obj.name, message))
            if (no_shield and obj.get(molding_closets.TAG_MOLDING)
                    and obj.get(molding_closets.PROP_MOLDING_KIND,
                                'CROWN') == 'CROWN'):
                found.append((obj.name, "Light Shield not available "
                                        "for this material"))
        if not found:
            col.label(text="No design warnings.")
            return
        col.label(text=str(len(found)) + " Design Warnings Found",
                  icon='ERROR')
        col.separator()
        for name, message in sorted(found):
            row = col.row()
            row.label(text=message)
            row.label(text=name)

    def draw_drawer_box_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'closet_drawer_box', text="Drawer Box")

        col.separator()
        col.prop(self, 'closet_drawer_vertical_grain')

        row = layout.row(align=True)
        op = row.operator('hb_closets.open_room_fronts',
                          text="Open Drawers", icon='HIDE_OFF')
        op.open = True
        op.fronts = 'DRAWERS'
        op = row.operator('hb_closets.open_room_fronts',
                          text="Close Drawers", icon='HIDE_ON')
        op.open = False
        op.fronts = 'DRAWERS'

    # =====================================================================
    # UI: rods and hangers (Options tab)
    # =====================================================================
    def draw_rod_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.label(text="Hanging Rods:")
        col.prop(self, 'closet_rod_type', text="Type")
        col.prop(self, 'closet_rod_finish', text="Finish")

        col.separator()
        col.label(text="Hangers:")
        col.prop(self, 'closet_hanger_model', text="Model")

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.randomize_hangers',
                     text="Randomize Hangers", icon='FILE_REFRESH')
        row.operator('hb_closets.install_model_pack', text="", icon='IMPORT')

    # =====================================================================
    # UI: accessories (Options tab)
    # =====================================================================
    def draw_accessory_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.prop(self, 'default_accessory_color', text="Metal")
        col.prop(self, 'default_accessory_fabric', text="Fabric")
        rows = accessories_closets.unavailable_finishes(context.scene)
        if not rows:
            return
        box = layout.box()
        box.label(text="Not available in this finish:", icon='ERROR')
        sub = box.column(align=True)
        for line in accessories_closets.notice_lines(rows):
            sub.label(text=line)

    # =====================================================================
    # UI: countertops (Options tab)
    # =====================================================================
    def draw_countertop_options_ui(self, layout, context):
        col = layout.column(align=True)
        # With the toggle on, tops take the closet material and the
        # shelf thickness, so neither field below applies.
        col.prop(self, 'use_closet_material_for_countertops',
                 text="Use Closet Material for Tops")
        sub = col.row()
        sub.enabled = not self.use_closet_material_for_countertops
        sub.prop(self, 'closet_countertop_material', text="Material")
        if self.use_closet_material_for_countertops:
            col.label(text="Thickness: %s" % _thickness_label(
                countertop_thickness_for(self)))
        else:
            # Typed for the room, as the reference's Countertop Thickness was.
            col.prop(self, 'countertop_thickness', text="Thickness")

    # =====================================================================
    # UI: molding (Options tab)
    # =====================================================================
    def draw_molding_options_ui(self, layout, context):
        col = layout.column(align=True)
        col.label(text="Crown:")
        col.prop(self, 'closet_crown_profile', text="Profile")
        if (molding_closets.resolve_crown_profile(
                self.closet_crown_profile or molding_closets.DEFAULT_PROFILE,
                context.scene)
                != (self.closet_crown_profile
                    or molding_closets.DEFAULT_PROFILE)):
            col.label(text="Light shield not available for this material "
                      "- adds L crown", icon='INFO')
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.add_molding', text="Add Crown Molding",
                     icon='ADD').molding_kind = 'CROWN'
        row.operator('hb_closets.delete_molding', text="",
                     icon='X').molding_kind = 'CROWN'

        col.separator()
        col.label(text="Base:")
        col.prop(self, 'closet_base_profile', text="Profile")
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('hb_closets.add_molding', text="Add Base Molding",
                     icon='ADD').molding_kind = 'BASE'
        row.operator('hb_closets.delete_molding', text="",
                     icon='X').molding_kind = 'BASE'

    # =====================================================================
    # UI: master draw entry point (called by view3d_sidebar)
    # =====================================================================
    def draw_user_library_ui(self, layout, context):
        from .operators import ops_user_library
        ops_user_library.draw_library_section(layout, context)

    def draw_library_ui(self, layout, context):
        col = layout.column(align=True)

        # Tab selector. On the LIBRARY tab an icon-only Thumbnail/List
        # toggle is pinned to the right end of this same row.
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, 'closet_tabs', 'LIBRARY', icon='ASSET_MANAGER')
        row.prop_enum(self, 'closet_tabs', 'OPTIONS', icon='PREFERENCES')

        if self.closet_tabs == 'LIBRARY':
            view = row.row(align=True)
            view.alignment = 'RIGHT'
            view.prop(self, 'library_view_mode', expand=True, icon_only=True)
            sections = [
                ('show_closet_sizes', "Closet Sizes",
                 self.draw_closet_sizes_ui),
                ('show_starter_library', "Closet Starters",
                 self.draw_starter_library_ui),
                ('show_user_library', "My Closets",
                 self.draw_user_library_ui),
                ('show_design_warnings', "Design Warnings",
                 self.draw_design_warnings_ui),
            ]
        else:
            # Dropdown changes on this tab re-apply room-wide.
            sections = [
                ('show_material_options', "Materials",
                 self.draw_material_options_ui),
                ('show_front_options', "Door & Drawer Front Styles",
                 self.draw_front_options_ui),
                ('show_pull_options', "Pulls",
                 self.draw_pull_options_ui),
                ('show_drawer_box_options', "Drawers",
                 self.draw_drawer_box_options_ui),
                ('show_rod_options', "Rods & Hangers",
                 self.draw_rod_options_ui),
                ('show_accessory_options', "Accessories",
                 self.draw_accessory_options_ui),
                ('show_countertop_options', "Countertops",
                 self.draw_countertop_options_ui),
                ('show_molding_options', "Molding",
                 self.draw_molding_options_ui),
                ('show_design_warnings', "Design Warnings",
                 self.draw_design_warnings_ui),
            ]

        for prop_name, label, draw_fn in sections:
            expanded = getattr(self, prop_name)
            box = col.box()
            hrow = box.row()
            hrow.alignment = 'LEFT'
            hrow.prop(self, prop_name, text=label,
                      icon='TRIA_DOWN' if expanded else 'TRIA_RIGHT',
                      emboss=False)
            if expanded:
                draw_fn(box, context)


classes = (
    Closet_Bay_Countertop_Props,
    Closet_Slab_Countertop_Props,
    Closet_Bay_Cleat_Props,
    Closet_Starter_Props,
    Closet_Bay_Props,
    Closet_Opening_Props,
    Closets_Scene_Props,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hb_closets = PointerProperty(
        name="Closets Props", type=Closets_Scene_Props)
    bpy.types.Object.hb_closet_starter = PointerProperty(
        name="Closet Starter Props", type=Closet_Starter_Props)
    bpy.types.Object.hb_closet_bay = PointerProperty(
        name="Closet Bay Props", type=Closet_Bay_Props)
    bpy.types.Object.hb_closet_opening = PointerProperty(
        name="Closet Opening Props", type=Closet_Opening_Props)
    bpy.types.Object.hb_closet_slab = PointerProperty(
        name="Slab Countertop Props", type=Closet_Slab_Countertop_Props)
    # Files that saved their colours by list place open on the right one.
    materials_closets.register_handlers()


def unregister():
    materials_closets.unregister_handlers()
    for pcoll in preview_collections.values():
        try:
            bpy.utils.previews.remove(pcoll)
        except Exception:
            pass
    preview_collections.clear()
    if hasattr(bpy.types.Scene, 'hb_closets'):
        del bpy.types.Scene.hb_closets
    if hasattr(bpy.types.Object, 'hb_closet_starter'):
        del bpy.types.Object.hb_closet_starter
    if hasattr(bpy.types.Object, 'hb_closet_bay'):
        del bpy.types.Object.hb_closet_bay
    if hasattr(bpy.types.Object, 'hb_closet_opening'):
        del bpy.types.Object.hb_closet_opening
    if hasattr(bpy.types.Object, 'hb_closet_slab'):
        del bpy.types.Object.hb_closet_slab
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
