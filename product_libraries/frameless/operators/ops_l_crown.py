"""L crowns: the closures between the cabinet tops and the ceiling.

Like a base assembly, an L crown belongs to a run rather than to a
cabinet, so it is built from the room: Add L Crowns reads the upper and
tall cabinets, works out the runs and stands types_products.LCrown
pieces over each.

A run is cabinets that share a parent (a wall, a cabinet group, or the
floor) and a facing, touch end to end, and agree on their back line,
depth and top. A wall scribe filler standing against the end of a run
is part of the span: the crown carries on over it to the wall. A span
longer than MAX_LENGTH is cut into pieces left to right, full lengths
first and what is left last.

A crown comes in as tall as the gap between the cabinet tops and the
ceiling when there is one worth closing, and at the stock height
otherwise. Its height, return cleat depth and whether its face stands
flush with the carcass or out in the door plane are its own prompts.
"""
import bpy
from mathutils import Matrix, Vector

from .. import types_products
from ...common import countertop_common
from .... import hb_types, hb_utils, hb_project, units
from .ops_base_assembly import (_cabinet_root, _facing, _frame, JOIN_GAP,
                                ALIGN_TOL)

MAX_LENGTH = units.inch(96.0)       # longest single piece
MIN_PIECE = units.inch(12.0)        # shortest piece a long run is cut into
MIN_GAP = units.inch(0.25)          # less than this is not worth closing
MAX_GAP = units.inch(24.0)          # more than this is not a crown's job
FILLER_TOP_TOL = units.inch(1.0)

MEMBERS_KEY = 'L_CROWN_MEMBERS'


# ---------------------------------------------------------------------------
# Reading the room
# ---------------------------------------------------------------------------

def wants_l_crown(obj):
    """A straight upper or tall cabinet. Corner cabinets are left for
    now: theirs is not a straight piece."""
    return (bool(obj.get('IS_FRAMELESS_CABINET_CAGE'))
            and obj.get('CABINET_TYPE') in ('UPPER', 'TALL')
            and 'CORNER_TYPE' not in obj)


def gather_cabinets(context, selected_only=False):
    if not selected_only:
        return [o for o in context.scene.objects if wants_l_crown(o)]
    picked = []
    for obj in context.selected_objects:
        root = _cabinet_root(obj)
        if root is not None and wants_l_crown(root) and root not in picked:
            picked.append(root)
    return picked


class _Member:
    """One cabinet measured in its run's frame: X along the run, the
    back of the cabinet at ``y``, the body running towards -Y."""

    def __init__(self, obj, to_frame):
        cage = hb_types.GeoNodeCage(obj)
        origin = to_frame @ obj.matrix_world.translation
        self.obj = obj
        self.x0 = origin.x
        self.x1 = origin.x + cage.get_input('Dim X')
        self.y = origin.y
        self.depth = cage.get_input('Dim Y')
        self.top = origin.z + cage.get_input('Dim Z')

    def continues(self, other):
        """True when ``other`` carries straight on from this cabinet."""
        return (abs(other.x0 - self.x1) <= JOIN_GAP
                and abs(other.y - self.y) <= ALIGN_TOL
                and abs(other.top - self.top) <= ALIGN_TOL
                and abs(other.depth - self.depth) <= ALIGN_TOL)


def build_runs(cabinets):
    """[(frame, [members])]: the cabinets sorted into the runs that each
    get their own crown. ``frame`` is the world matrix the members were
    measured in."""
    keyed = {}
    for cab in cabinets:
        keyed.setdefault((cab.parent, _facing(cab)), []).append(cab)

    runs = []
    for group in keyed.values():
        frame = _frame(group[0])
        to_frame = frame.inverted()
        members = sorted((_Member(c, to_frame) for c in group),
                         key=lambda m: m.x0)
        current = []
        for member in members:
            if current and not current[-1].continues(member):
                runs.append((frame, current))
                current = []
            current.append(member)
        if current:
            runs.append((frame, current))
    return runs


def piece_spans(x0, x1):
    """[(start, end)]: a span cut into pieces no longer than MAX_LENGTH,
    left to right. Full lengths first and what is left last; a last
    piece too short to be worth building takes the difference off the
    one before it."""
    if x1 - x0 <= MAX_LENGTH + ALIGN_TOL:
        return [(x0, x1)]
    spans = []
    start = x0
    while x1 - start > MAX_LENGTH + ALIGN_TOL:
        spans.append((start, start + MAX_LENGTH))
        start += MAX_LENGTH
    if x1 - start < MIN_PIECE:
        start = x1 - MIN_PIECE
        spans[-1] = (spans[-1][0], start)
    spans.append((start, x1))
    return spans


def end_fillers(context, frame, members):
    """(left, right): the wall scribe filler standing against each end
    of the run and reaching its top, or None."""
    first, last = members[0], members[-1]
    y_back, y_front = first.y, first.y - first.depth
    to_frame = frame.inverted()
    left = right = None
    for obj in context.scene.objects:
        if obj.get('PART_TYPE') != 'CORNER_FILLER':
            continue
        try:
            points = [to_frame @ p for p in countertop_common.footprint(obj)]
            top = points[0].z + hb_types.GeoNodeCage(obj).get_input('Dim Z')
        except Exception:
            continue
        if abs(top - first.top) > FILLER_TOP_TOL:
            continue
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        if max(ys) <= y_front + ALIGN_TOL or min(ys) >= y_back - ALIGN_TOL:
            continue
        if abs(max(xs) - first.x0) <= JOIN_GAP:
            left = obj
        elif abs(min(xs) - last.x1) <= JOIN_GAP:
            right = obj
    return left, right


def ceiling_gap(context, frame, members):
    """How far the top of the run stands below the ceiling: the wall's
    own height for a run on a wall, the room's ceiling otherwise."""
    first = members[0]
    top = (frame @ Vector((first.x0, first.y, first.top))).z
    parent = first.obj.parent
    if parent is not None and parent.get('IS_WALL_BP'):
        wall = hb_types.GeoNodeWall(parent)
        ceiling = parent.matrix_world.translation.z + wall.get_input('Height')
    else:
        ceiling = hb_project.get_settings_scene(context).home_builder.ceiling_height
    return ceiling - top


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------

def create_l_crowns(context, frame, members):
    """The crown pieces over one run, left to right. None for a run that
    already reaches the ceiling."""
    first, last = members[0], members[-1]
    gap = ceiling_gap(context, frame, members)
    if gap < MIN_GAP:
        return []
    height = gap if gap <= MAX_GAP else types_products.L_CROWN_HEIGHT

    fillers = end_fillers(context, frame, members)
    reach = [hb_types.GeoNodeCage(f).get_input('Dim X') if f is not None
             else 0.0 for f in fillers]
    spans = piece_spans(first.x0 - reach[0], last.x1 + reach[1])

    # On a wall or in a cabinet group the crown belongs to that; a lone
    # cabinet's crown goes with it.
    parent = first.obj.parent or first.obj
    created = []
    for start, end in spans:
        crown = types_products.LCrown()
        crown.width = end - start
        crown.depth = first.depth + types_products.FRONT_THICKNESS
        crown.height = height
        crown.create('Ceiling Closure')
        obj = crown.obj
        over = [m for m in members
                if m.x1 > start + ALIGN_TOL and m.x0 < end - ALIGN_TOL]
        obj[MEMBERS_KEY] = [m.obj.name for m in (over or members)]

        world = frame @ Matrix.Translation(Vector((start, first.y, first.top)))
        local = parent.matrix_world.inverted() @ world
        obj.parent = parent
        obj.matrix_parent_inverse.identity()
        obj.location = local.to_translation()
        obj.rotation_euler = local.to_euler()
        created.append(obj)
    return created


def all_l_crowns(scene):
    return [o for o in scene.objects if o.get('IS_L_CROWN')]


def remove_l_crowns(objs):
    removed = 0
    for obj in objs:
        for child in list(obj.children_recursive):
            bpy.data.objects.remove(child, do_unlink=True)
        bpy.data.objects.remove(obj, do_unlink=True)
        removed += 1
    return removed


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class hb_frameless_OT_add_l_crowns(bpy.types.Operator):
    bl_idname = "hb_frameless.add_l_crowns"
    bl_label = "Add Ceiling Closures"
    bl_description = ("Close the gap between the ceiling and each run of "
                      "upper and tall cabinets with a ceiling closure")
    bl_options = {'REGISTER', 'UNDO'}

    selected_only: bpy.props.BoolProperty(
        name="Selected Only",
        description="Only build crowns over the selected cabinets",
        default=False
    )  # type: ignore

    def execute(self, context):
        cabinets = gather_cabinets(context, self.selected_only)
        if not cabinets:
            self.report({'WARNING'},
                        "No upper or tall cabinets "
                        + ("selected" if self.selected_only else "found"))
            return {'CANCELLED'}

        # Rebuilding replaces the crowns already over these cabinets.
        names = {c.name for c in cabinets}
        existing = all_l_crowns(context.scene)
        if self.selected_only:
            stale = [o for o in existing
                     if names.intersection(o.get(MEMBERS_KEY) or ())]
        else:
            stale = existing
        remove_l_crowns(stale)

        created = []
        for frame, members in build_runs(cabinets):
            created.extend(create_l_crowns(context, frame, members))

        for obj in created:
            bpy.ops.hb_frameless.assign_cabinet_style(cabinet_name=obj.name)
            hb_utils.run_calc_fix(context, obj)
            bpy.ops.hb_frameless.toggle_mode(search_obj_name=obj.name)

        if not created:
            self.report({'WARNING'},
                        "The cabinets already reach the ceiling")
            return {'FINISHED'}
        self.report({'INFO'}, f"Created {len(created)} ceiling closure piece(s)")
        return {'FINISHED'}


class hb_frameless_OT_remove_l_crowns(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_l_crowns"
    bl_label = "Remove Ceiling Closures"
    bl_description = "Remove every ceiling closure from the room"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        removed = remove_l_crowns(all_l_crowns(context.scene))
        self.report({'INFO'}, f"Removed {removed} ceiling closure piece(s)")
        return {'FINISHED'}


classes = (
    hb_frameless_OT_add_l_crowns,
    hb_frameless_OT_remove_l_crowns,
)

register, unregister = bpy.utils.register_classes_factory(classes)
