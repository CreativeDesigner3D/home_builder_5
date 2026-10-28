"""Wall assemblies: what a wall is made of, layer by layer.

A wall's Thickness stays its whole depth, outside finish to inside
finish; an assembly's layers - siding, sheathing, studs, drywall, or
block, concrete, insulation - add up to it. The layers are data, read
here and nowhere else: framing puts its studs in the framing layer, real
siding is built inward of the face when the outside layer is siding, and
roofs and foundations line up on the outside of the sheathing.

A wall carries its assembly as HB_ASSEMBLY (a uid of one of the house's
assemblies). A wall without one - every wall in an older file - reads as
today's stack: studs as deep as stud_depth makes them, centred, with a
finish each side. So nothing reads differently until an assembly is
applied.

Applying an assembly (apply) changes the walls' thickness and keeps their
inside faces where they are: the walls grow outward. Where a wall's drawn
line is its outside face, that line moves out, and the run of walls it
is part of gets new corners together; cabinets on the inside face and
walls meeting it at a T stay put.
"""

import math

import bpy
from mathutils import Vector

from . import hb_house
from .units import inch

ASSEMBLY_KEY = 'HB_ASSEMBLY'
TOLERANCE = 0.001           # an assembly that no longer sums to the wall within this is ignored

DEFAULTS = (
    ("2x6 Exterior", 'Exterior', (('SIDING', inch(0.75)), ('SHEATHING', inch(0.4375)),
                                  ('FRAMING', inch(5.5)), ('DRYWALL', inch(0.5)))),
    ("2x4 Interior", 'Interior', (('DRYWALL', inch(0.5)), ('FRAMING', inch(3.5)),
                                  ('DRYWALL', inch(0.5)))),
)


def total(assembly):
    return sum(layer.thickness for layer in assembly.layers)


def house_of(obj=None):
    scene = hb_house.house_scene_of(bpy.context.scene)
    return scene.hb_house if scene is not None else None


def assembly_of(obj):
    """The assembly a wall is made with, or None: none set, or one that
    no longer adds up to the wall's thickness."""
    uid = obj.get(ASSEMBLY_KEY)
    house = house_of()
    if not uid or house is None:
        return None
    asm = next((a for a in house.assemblies if a.uid == uid), None)
    if asm is None or not asm.layers:
        return None
    from . import hb_types
    t = hb_types.GeoNodeWall(obj).get_input('Thickness')
    if abs(total(asm) - t) > TOLERANCE:
        return None
    return asm


def default_for(house, wall_type):
    """The assembly new walls of a type are made with, or None."""
    if house is None:
        return None
    return next((a for a in house.assemblies
                 if a.wall_type == wall_type and a.for_new_walls and a.layers), None)


def wall_layers(obj):
    """[(kind, thickness)] from the outside in. A wall without an
    assembly reads as today's stack: a finish, studs as deep as framing
    makes them, a finish."""
    asm = assembly_of(obj)
    if asm is not None:
        return [(layer.kind, layer.thickness) for layer in asm.layers]
    from . import hb_framing, hb_types
    t = hb_types.GeoNodeWall(obj).get_input('Thickness')
    d = hb_framing.stud_depth(t)
    f = max((t - d) / 2.0, 0.0)
    return [('OTHER', f), ('FRAMING', d), ('OTHER', f)]


def _outside_is_ref(obj, rooms=None):
    """Whether a wall's layers start (outside) at its drawn face, y = 0.
    An interior wall reads from its drawn face. Pass `rooms`
    (hb_exterior._indoor_polygons) when asking about many walls."""
    from . import hb_exterior
    side = hb_exterior.outdoor_side(obj, rooms)
    return side != 'FAR'


def layer_faces(obj, rooms=None):
    """[(kind, y0, y1)] across the wall in its own space (y from its drawn
    face), outside first."""
    from . import hb_types
    t = hb_types.GeoNodeWall(obj).get_input('Thickness')
    out = []
    y = 0.0
    ref = _outside_is_ref(obj, rooms)
    for kind, th in wall_layers(obj):
        a, b = y, y + th
        out.append((kind, a, b) if ref else (kind, t - b, t - a))
        y = b
    return out


def framing_band(obj, rooms=None):
    """(y0, y1) of the studs across the wall: centred, as deep as
    stud_depth makes them, without an assembly."""
    bands = []
    if assembly_of(obj) is not None:
        bands = [(a, b) for kind, a, b in layer_faces(obj, rooms) if kind == 'FRAMING']
    if not bands:
        from . import hb_framing, hb_types
        t = hb_types.GeoNodeWall(obj).get_input('Thickness')
        d = hb_framing.stud_depth(t)
        return (t - d) / 2.0, (t + d) / 2.0
    return bands[0]


def siding_inset(obj):
    """How deep the outside siding layer is: real siding is built that
    far in from the face. 0 for a wall whose outside layer isn't siding,
    or which has no assembly."""
    if assembly_of(obj) is None:
        return 0.0
    layers = wall_layers(obj)
    return layers[0][1] if layers and layers[0][0] == 'SIDING' else 0.0


def level_siding_inset(scene, level_uid):
    """The deepest siding layer among a level's exterior walls: the
    filled-in gable ends over them take their siding that far in too."""
    return max((siding_inset(o) for o in scene.objects
                if o.get('IS_WALL_BP') and o.get(hb_house.LEVEL_KEY) == level_uid
                and o.get('WALL_TYPE', 'Exterior') == 'Exterior'), default=0.0)


# ---- Defaults and editing -------------------------------------------------------

def add_assembly(house, name, wall_type, layers):
    """Add an assembly with its layers. The assembly is looked up again by
    uid after each add: nothing is held across an add()."""
    uid = hb_house._new_uid()
    asm = house.assemblies.add()
    asm.uid = uid
    asm.name = name
    asm.wall_type = wall_type
    for kind, th in layers:
        asm = next(a for a in house.assemblies if a.uid == uid)
        layer = asm.layers.add()
        layer.kind = kind
        layer.thickness = th
        layer.name = next(item[1] for item in hb_house.LAYER_KINDS if item[0] == kind)
    return uid


def ensure_defaults(house):
    if len(house.assemblies):
        return
    for name, wall_type, layers in DEFAULTS:
        add_assembly(house, name, wall_type, layers)


# ---- Applying ---------------------------------------------------------------------

def _seg_of(obj):
    """(start, direction, length, thickness) of a wall's drawn line as it
    stands - its start from where it is evaluated, not its location: a
    wall linked to the one before has its start set by a constraint."""
    from .operators import walls as hb_walls
    seg = hb_walls.wall_seg(obj)
    return Vector(seg.start), Vector(seg.dir), seg.length, seg.thickness


def _intersect(p1, d1, p2, d2):
    den = d1.x * d2.y - d1.y * d2.x
    if abs(den) < 1e-9:
        return None
    t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / den
    return p1 + d1 * t


last_skipped = []           # the walls the last apply left alone


def _two_sided(scene, level_uid):
    """Names of a level's walls with rooms (porches left out) facing both
    their faces somewhere along them."""
    from . import hb_porches, hb_wall_graph
    from .operators import walls as hb_walls
    _objs, segs = hb_walls.level_wall_segs(scene, level_uid)
    sides = {}
    for area in hb_wall_graph.find_rooms(segs):
        if hb_porches.is_porch_area(area):
            continue
        for sid, side, _t0, _t1 in area.faces:
            sides.setdefault(sid, set()).add(side)
    return {sid for sid, ss in sides.items() if len(ss) == 2}


def apply(scene, walls, asm_uid):
    """Make walls with an assembly: their thickness becomes its total, and
    they grow outward, inside faces kept. Returns how many changed."""
    from . import hb_types, hb_wall_graph
    from .operators import walls as hb_walls
    from .product_libraries.common import door_window_geo
    house = scene.hb_house
    asm = next((a for a in house.assemblies if a.uid == asm_uid), None)
    if asm is None or not asm.layers:
        return 0
    new_t = total(asm)
    targets = {o.name for o in walls if o.get('IS_WALL_BP')}
    # An exterior wall with rooms on both faces (an old outside wall an
    # addition was built against) has no outside to grow to: left alone
    global last_skipped
    last_skipped = [n for n in targets
                    if bpy.data.objects[n].get('WALL_TYPE', 'Exterior') in ('Exterior', 'Dormer')
                    and n in _two_sided(scene, hb_house.level_of(bpy.data.objects[n]))]
    targets -= set(last_skipped)
    if not targets:
        return 0
    levels = {hb_house.level_of(bpy.data.objects[n]) for n in targets}
    tees = []
    for uid in levels:
        tees += hb_walls.capture_tees(scene, uid)
    # Which way each wall grows: a wall whose drawn line is outdoors moves
    # that line out; one whose drawn line is indoors (or an interior wall)
    # keeps it and grows on its far side
    shift = {}
    for name in targets:
        obj = bpy.data.objects[name]
        _p, _d, _l, t = _seg_of(obj)
        grow = new_t - t
        shift[name] = grow if (obj.get('WALL_TYPE') in ('Exterior', 'Dormer')
                               and _outside_is_ref(obj)) else 0.0
    # The outdoor faces as they are now, for the roof pieces lined up on them
    bpy.context.view_layer.update()
    faces_before = []
    for name in targets:
        obj = bpy.data.objects[name]
        if obj.get('WALL_TYPE') not in ('Exterior', 'Dormer'):
            continue
        p, d, length, t = _seg_of(obj)
        left = Vector((-d.y, d.x))
        ref = _outside_is_ref(obj)
        face = p if ref else p + left * t
        out = -left if ref else left
        faces_before.append((face, d, length, out, new_t - t))

    # New corners where wall ends meet: each wall's drawn line moves out by
    # its shift, and every end shared by two walls goes to where their
    # lines now cross - linked into runs or only touching. A wall's lone
    # end moves out square to it; a T end is put back on its host after
    for uid in levels:
        objs, segs = hb_walls.level_wall_segs(scene, uid)
        segs = hb_wall_graph.built_walls(segs)
        if not any(shift.get(sg.id, 0.0) for sg in segs):
            continue
        graph = hb_wall_graph.build_graph(segs)
        lines = {}
        for sg in segs:
            d = Vector(sg.dir)
            left = Vector(sg.normal)
            lines[sg.id] = (Vector(sg.start) - left * shift.get(sg.id, 0.0), d)
        new_end = {}
        for node in graph.nodes:
            if node.kind == hb_wall_graph.TEE:
                continue
            ends = node.ends
            if len(ends) == 1:
                sid, which = ends[0]
                p, d = lines[sid]
                q = Vector(graph.segs[sid].point(which))
                new_end[(sid, which)] = p + d * (q - p).dot(d)
                continue
            # Where the moved lines of the walls meeting here cross (the
            # first pair that isn't parallel)
            pt = None
            for i in range(len(ends)):
                for j in range(i + 1, len(ends)):
                    p1, d1 = lines[ends[i][0]]
                    p2, d2 = lines[ends[j][0]]
                    pt = _intersect(p1, d1, p2, d2)
                    if pt is not None:
                        break
                if pt is not None:
                    break
            for sid, which in ends:
                p, d = lines[sid]
                q = Vector(graph.segs[sid].point(which)) if pt is None else pt
                new_end[(sid, which)] = p + d * (q - p).dot(d)
        for sg in segs:
            obj = objs[sg.id]
            off = Vector(sg.normal) * shift.get(sg.id, 0.0)
            # An end at a T moves square to the wall with it; restore_tees
            # puts it back on its host after
            a = new_end.get((sg.id, hb_wall_graph.START), Vector(sg.start) - off)
            b = new_end.get((sg.id, hb_wall_graph.END), Vector(sg.end) - off)
            d = Vector(sg.dir)
            new_len = (b - a).dot(d)
            if new_len > 0.01:
                hb_types.GeoNodeWall(obj).set_input('Length', new_len)
            if not hb_walls._constrained_start(obj):
                obj.location.x, obj.location.y = a.x, a.y
            # A start that moved along the wall would carry what is on it
            # along too: it stays where it was
            along = (a - Vector(sg.start)).dot(d)
            if abs(along) > 1e-7:
                for child in obj.children:
                    if not child.get('obj_x'):
                        child.location.x -= along
        bpy.context.view_layer.update()
    # Thickness, and what hangs on the walls
    for name in targets:
        obj = bpy.data.objects[name]
        wall = hb_types.GeoNodeWall(obj)
        old = wall.get_input('Thickness')
        grow = new_t - old
        wall.set_input('Thickness', new_t)
        obj[ASSEMBLY_KEY] = asm_uid
        for child in obj.children:
            if child.get('obj_x') or child.get('IS_WALL_BP'):
                continue
            if child.get('IS_ENTRY_DOOR_BP') or child.get('IS_WINDOW_BP'):
                cage = hb_types.GeoNodeCage(child)
                if cage.has_modifier():
                    cage.set_input('Dim Y', new_t)
                continue
            if child.location.y >= old - 0.001:
                child.location.y += grow           # on the far face: it moves with it
        obj.update_tag()
    bpy.context.view_layer.update()
    hb_walls.restore_tees(tees, scene)
    for name in targets:
        for child in bpy.data.objects[name].children:
            if (child.get('IS_ENTRY_DOOR_BP') or child.get('IS_WINDOW_BP')) \
                    and door_window_geo.stored_opts(child) is not None:
                door_window_geo.build_geometry(child)
    _follow_faces(scene, faces_before)
    for uid in levels:
        hb_walls.refresh_wall_junctions(scene, uid)
    return len(targets)


def _follow_faces(scene, faces):
    """Roof pieces and custom roof footprints are plan rectangles; an edge
    that lay on a wall's outdoor face moves out with it."""
    for level in scene.hb_house.levels:
        rects = [(piece, ('x0', 'x1', 'y0', 'y1')) for piece in level.roof.pieces]
        if level.roof.use_extents:
            rects.append((level.roof, ('ext_x0', 'ext_x1', 'ext_y0', 'ext_y1')))
        for owner, (kx0, kx1, ky0, ky1) in rects:
            x0, x1, y0, y1 = (getattr(owner, k) for k in (kx0, kx1, ky0, ky1))
            moves = {}
            for face, d, length, out, grow in faces:
                if abs(grow) < 1e-6:
                    continue
                lo_x, hi_x = sorted((face.x, face.x + d.x * length))
                lo_y, hi_y = sorted((face.y, face.y + d.y * length))
                if abs(d.y) > 0.999:            # a wall running along y: x edges
                    for key, val in ((kx0, x0), (kx1, x1)):
                        if abs(val - face.x) < 0.002 and hi_y > y0 and lo_y < y1:
                            moves[key] = val + out.x * grow
                elif abs(d.x) > 0.999:          # along x: y edges
                    for key, val in ((ky0, y0), (ky1, y1)):
                        if abs(val - face.y) < 0.002 and hi_x > x0 and lo_x < x1:
                            moves[key] = val + out.y * grow
            for key, val in moves.items():
                owner[key] = val                # no update: the roofs rebuild after


# ---- Operators ----------------------------------------------------------------------

def _house(context):
    scene = hb_house.house_scene_of(context.scene)
    return scene.hb_house if scene is not None else None


def active_assembly(context):
    house = _house(context)
    if house is None or not len(house.assemblies):
        return None
    return house.assemblies[min(max(house.active_assembly_index, 0), len(house.assemblies) - 1)]


class HOME_BUILDER_OT_add_standard_assemblies(bpy.types.Operator):
    """Add a 2x6 exterior and a 2x4 interior wall assembly to start from"""
    bl_idname = "home_builder.add_standard_assemblies"
    bl_label = "Add Standard Assemblies"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _house(context) is not None

    def execute(self, context):
        house = _house(context)
        before = len(house.assemblies)
        for name, wall_type, layers in DEFAULTS:
            if not any(a.name == name for a in house.assemblies):
                add_assembly(house, name, wall_type, layers)
        house.active_assembly_index = before if len(house.assemblies) > before else 0
        return {'FINISHED'}


class HOME_BUILDER_OT_add_assembly(bpy.types.Operator):
    """Add a wall assembly, a copy of the one picked"""
    bl_idname = "home_builder.add_assembly"
    bl_label = "Add Assembly"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return _house(context) is not None

    def execute(self, context):
        house = _house(context)
        src = active_assembly(context)
        if src is None:
            ensure_defaults(house)
            return {'FINISHED'}
        name, wall_type = src.name + " Copy", src.wall_type
        layers = [(layer.kind, layer.thickness) for layer in src.layers]
        add_assembly(house, name, wall_type, layers)
        house.active_assembly_index = len(house.assemblies) - 1
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_assembly(bpy.types.Operator):
    """Remove the wall assembly picked (walls made with it keep their thickness)"""
    bl_idname = "home_builder.remove_assembly"
    bl_label = "Remove Assembly"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return active_assembly(context) is not None

    def execute(self, context):
        house = _house(context)
        i = min(max(house.active_assembly_index, 0), len(house.assemblies) - 1)
        house.assemblies.remove(i)
        house.active_assembly_index = max(0, i - 1)
        return {'FINISHED'}


class HOME_BUILDER_OT_add_wall_layer(bpy.types.Operator):
    """Add a layer to the assembly picked, under the layer picked"""
    bl_idname = "home_builder.add_wall_layer"
    bl_label = "Add Layer"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return active_assembly(context) is not None

    def execute(self, context):
        asm = active_assembly(context)
        uid = asm.uid
        at = asm.active_layer_index
        asm.layers.add()
        asm = next(a for a in _house(context).assemblies if a.uid == uid)
        new = len(asm.layers) - 1
        asm.layers[new].name = "Insulation"
        asm.layers[new].kind = 'INSULATION'
        asm.layers[new].thickness = inch(1.0)
        if 0 <= at < new - 1:
            asm.layers.move(new, at + 1)
            new = at + 1
        asm.active_layer_index = new
        return {'FINISHED'}


class HOME_BUILDER_OT_remove_wall_layer(bpy.types.Operator):
    """Remove the layer picked"""
    bl_idname = "home_builder.remove_wall_layer"
    bl_label = "Remove Layer"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        asm = active_assembly(context)
        return asm is not None and len(asm.layers) > 1

    def execute(self, context):
        asm = active_assembly(context)
        i = min(max(asm.active_layer_index, 0), len(asm.layers) - 1)
        asm.layers.remove(i)
        asm.active_layer_index = max(0, i - 1)
        return {'FINISHED'}


class HOME_BUILDER_OT_apply_assembly(bpy.types.Operator):
    """Make walls with the assembly picked: they grow outward to its thickness, their inside faces kept"""
    bl_idname = "home_builder.apply_assembly"
    bl_label = "Apply to Walls"
    bl_options = {'REGISTER', 'UNDO'}

    target: bpy.props.EnumProperty(
        name="Walls",
        items=[('SELECTED', "Selected Walls", ""),
               ('LEVEL', "Level", "Every wall of its type on the active level"),
               ('HOUSE', "House", "Every wall of its type in the house")],
        default='SELECTED')  # type: ignore

    @classmethod
    def poll(cls, context):
        return active_assembly(context) is not None

    def execute(self, context):
        asm = active_assembly(context)
        scene = hb_house.house_scene_of(context.scene)
        if self.target == 'SELECTED':
            walls = [o for o in context.selected_objects if o.get('IS_WALL_BP')]
        else:
            level = hb_house.active_level(context)
            walls = [o for o in scene.objects if o.get('IS_WALL_BP')
                     and o.get('WALL_TYPE', 'Exterior') == asm.wall_type
                     and (self.target == 'HOUSE' or o.get(hb_house.LEVEL_KEY) == level.uid)]
        if not walls:
            self.report({'WARNING'}, "No walls to apply it to")
            return {'CANCELLED'}
        n = apply(scene, walls, asm.uid)
        msg = f"{asm.name} on {n} wall(s)"
        if last_skipped:
            msg += (f"; {len(last_skipped)} exterior wall(s) with rooms on both sides left "
                    "as they are - make them Interior walls to give them an interior assembly")
        self.report({'INFO'}, msg)
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_add_standard_assemblies,
    HOME_BUILDER_OT_add_assembly,
    HOME_BUILDER_OT_remove_assembly,
    HOME_BUILDER_OT_add_wall_layer,
    HOME_BUILDER_OT_remove_wall_layer,
    HOME_BUILDER_OT_apply_assembly,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
