"""Apply molding packages to a room.

apply_scene_packages(scene) is the single entry point: it clears every
package sweep in the scene and rebuilds from the scene's three package
props. The scene-prop update callbacks and the refresh operator both
route through it, so the dropdowns are the whole UI.
"""

import bpy
import mathutils

from . import adapters, engine, packages
from .. import hb_types, hb_utils, units

MOLDING_TAG = 'IS_HB_MOLDING_SWEEP'
MOLDING_TYPE = 'HB_MOLDING_TYPE'
MOLDING_MEMBERS = 'HB_MOLDING_MEMBERS'

# (prop name, molding type, grouping alignment)
_TYPES = (
    ('molding_crown_package', 'CROWN', 'top'),
    ('molding_base_package', 'BASE', 'bottom'),
    ('molding_light_rail_package', 'LIGHT_RAIL', 'bottom'),
)


def clear_scene_molding(scene, molding_type=None):
    """Remove package sweeps (and their hidden profiles) from the
    scene, optionally scoped to one molding type."""
    doomed = []
    for obj in list(scene.objects):
        if not obj.get(MOLDING_TAG):
            continue
        if molding_type and obj.get(MOLDING_TYPE) != molding_type:
            continue
        bevel = obj.data.bevel_object if obj.type == 'CURVE' else None
        doomed.append(obj)
        if bevel is not None and bevel.get('IS_HB_MOLDING_PROFILE'):
            doomed.append(bevel)
    for obj in doomed:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.curves.remove(data)


def _resolve_stack(stack, opts):
    """Resolve a stack against the room settings, in order:

    - per-category profile overrides swap each preset's profile
    - Spacer-category entries carry the room's spacer height (their
      profile is scaled to it); other entries have no height override
    - the STACK_OFFSET dy sentinel becomes the spacer height, so a
      stacked crown rides on top of the room-sized spacer
    - the STACK_FRONT dx sentinel becomes the running front of the
      PRECEDING entries (max of their dx + measured profile
      thickness), so an entry mounts on the face of what's below it -
      the crown on its spacer, the shoe on its base molding.

    Returns a list of concrete (ref, fallback, dx, dy, height) tuples.
    """
    resolved = []
    front = 0.0
    for profile_ref, fallback_key, dx, dy in stack:
        if dy == 'STACK_OFFSET':
            dy = opts['spacer_height']
        category = profile_ref.replace("\\", "/").split("/")[0]
        override = opts['overrides'].get(category)
        if override:
            profile_ref = f"{category}/{override}"
        height = opts['spacer_height'] if category == 'Spacer' else None
        if dx == 'STACK_FRONT':
            dx = front
        resolved.append((profile_ref, fallback_key, dx, dy, height))
        front = max(front, dx + packages.profile_front_depth(
            profile_ref, fallback_key))
    return resolved


def _run_ceiling_local(first, opts):
    """Ceiling Z in the run's first-member local frame: the top of the
    wall the run hangs on when there is one, else the room's ceiling
    height (measured from the world floor)."""
    ceiling = None
    wall = hb_utils.get_wall_bp(first)
    if wall is not None:
        try:
            h = hb_types.GeoNodeObject(wall).get_input('Height')
        except Exception:
            h = None
        if h:
            ceiling = wall.matrix_world.translation.z + h
    if ceiling is None:
        ceiling = opts['ceiling_height']
    return ceiling - first.matrix_world.translation.z


def _ceiling_stack(first, facts, resolved_stack, opts):
    """Re-aim a resolved crown stack at this run's ceiling: the crown
    tops out at the ceiling line and spacer entries stretch to fill
    from the crown datum up to the crown bottom (all the way to the
    ceiling when the stack has no crown). Entries keep their dx."""

    def _category(ref):
        return ref.replace("\\", "/").split("/")[0]

    datum = _crown_datum(first, facts, opts)
    ceiling = _run_ceiling_local(first, opts)
    crown_h = 0.0
    for ref, fb, _dx, _dy, _height in resolved_stack:
        if _category(ref) == 'Crown Molding':
            crown_h = max(crown_h, packages.profile_top_height(ref, fb))
    fill = max(ceiling - datum - crown_h, 0.0)
    out = []
    for ref, fb, dx, dy, height in resolved_stack:
        category = _category(ref)
        if category == 'Crown Molding':
            dy = fill
        elif category == 'Spacer':
            if fill < units.inch(0.25):
                # No usable gap under the crown - drop the spacer.
                continue
            dy, height = 0.0, fill
        out.append((ref, fb, dx, dy, height))
    return out


def _crown_datum(first, facts, opts):
    """Crown mounting Z in the first member's local frame: a REVEAL
    above the door top when the cabinet exposes one (face frame:
    height - top rail + door overlay + reveal, the same datum the
    crown detail drawing uses); the top line otherwise (frameless)."""
    _, _, height = engine.cage_dims(first)
    mount = (facts.get(id(first)) or {}).get('crown_mount')
    if mount:
        return (height - mount['rail_width'] + mount['door_overlay']
                + opts['crown_reveal'])
    return height


def _crown_stack_top(first, facts, opts):
    """Local Z of the TOP of the room's crown stack on this run: the
    crown datum plus the tallest resolved entry (its vertical offset
    plus its profile height). With the to-ceiling option the stack
    tops out at the ceiling line. None when no crown package is
    active - the furniture cap then defaults to the cabinet top."""
    stack = opts.get('crown_stack')
    if not stack:
        return None
    if opts.get('to_ceiling'):
        return _run_ceiling_local(first, opts)
    base = _crown_datum(first, facts, opts)
    top = None
    for profile_ref, fallback_key, _dx, dy, height in _resolve_stack(
            stack, opts):
        if height is None:
            height = packages.profile_top_height(profile_ref, fallback_key)
        t = base + dy + height
        if top is None or t > top:
            top = t
    return top


def _sweep_z(molding_type, first, dy, facts, opts):
    """Sweep Z in the first member's local frame.

    Crown mounts at the crown datum (see _crown_datum). The furniture
    CAP sits on top of the tallest crown-stack molding - never below
    the cabinet top - plus the room's cap offset. Base sits on the
    floor; light rail hangs at the bottom line (upper roots originate
    at their bottom)."""
    if molding_type == 'CROWN':
        return _crown_datum(first, facts, opts) + dy
    if molding_type == 'CAP':
        _, _, height = engine.cage_dims(first)
        z = height
        crown_top = _crown_stack_top(first, facts, opts)
        if crown_top is not None and crown_top > z:
            z = crown_top
        return z + opts['cap_offset'] + dy
    return dy


def _member_plan_distance(member, point_xy):
    """Plan distance from a world XY point to the member's cage
    footprint rectangle (0 when the point is over the member)."""
    inv = member.matrix_world.inverted()
    lp = inv @ mathutils.Vector((point_xy.x, point_xy.y, 0.0))
    width, depth, _ = engine.cage_dims(member)
    dx = max(-lp.x, 0.0, lp.x - width)
    dy = max(-depth - lp.y, 0.0, lp.y)
    return (dx * dx + dy * dy) ** 0.5


def _material_runs(pts, cyclic, member_materials, fallback):
    """Split one sweep polyline into (points, material, cyclic) runs of
    consecutive edges attributed to the same style finish, so a run
    across mixed-style cabinets changes color at the cabinet seams.

    Each edge goes to the nearest chain member in plan (by midpoint);
    members that resolve no material - appliance bridges, styleless
    cabinets - take the fallback. Consecutive runs share their boundary
    point so the sweep stays continuous. A single-material loop stays
    cyclic; a mixed loop is rotated so a style boundary lands at the
    seam and emitted as open runs covering the whole perimeter."""
    edges = list(zip(pts, pts[1:]))
    if cyclic and len(pts) > 2:
        edges.append((pts[-1], pts[0]))
    if not edges:
        return []

    def _edge_material(a, b):
        mid = (a + b) * 0.5
        best_mat, best_d = fallback, None
        for member, mat in member_materials:
            d = _member_plan_distance(member, mid)
            if best_d is None or d < best_d:
                best_d = d
                best_mat = mat if mat is not None else fallback
        return best_mat

    mats = [_edge_material(a, b) for a, b in edges]
    if all(m is mats[0] for m in mats):
        return [(pts, mats[0], cyclic)]
    if cyclic:
        for i in range(1, len(edges)):
            if mats[i] is not mats[i - 1]:
                edges = edges[i:] + edges[:i]
                mats = mats[i:] + mats[:i]
                break
    runs = []
    for (a, b), mat in zip(edges, mats):
        if runs and runs[-1][1] is mat:
            runs[-1][0].append(b)
        else:
            runs.append(([a, b], mat))
    return [(run_pts, mat, False) for run_pts, mat in runs]


def _material_slot(curve, material):
    """Index of the material in the curve's slots, appending it on
    first use."""
    for i, existing in enumerate(curve.materials):
        if existing is material:
            return i
    curve.materials.append(material)
    return len(curve.materials) - 1


def _spawn_sweep(scene, molding_type, chain, segments, profile_ref,
                 fallback_key, dy, facts, opts, height=None):
    """Create one sweep object: hidden profile + curve through the
    world-space segments, localized to (and parented on) chain[0]."""
    first = chain[0]
    profile = packages.make_profile_object(
        profile_ref, fallback_key,
        f"Molding_Profile_{fallback_key}", scene.collection, height=height)
    if profile is None:
        return None
    curve = bpy.data.curves.new("MoldingSweep", type='CURVE')
    curve.dimensions = '2D'
    curve.bevel_mode = 'OBJECT'
    curve.bevel_object = profile
    curve.use_fill_caps = True
    sweep = bpy.data.objects.new("MoldingSweep", curve)
    scene.collection.objects.link(sweep)
    sweep[MOLDING_TAG] = True
    sweep[MOLDING_TYPE] = molding_type
    sweep[MOLDING_MEMBERS] = ",".join(c.name for c in chain)
    sweep.parent = first
    sweep.location.z = _sweep_z(molding_type, first, dy, facts, opts)
    profile.parent = sweep

    # Each stretch of the sweep takes the style finish of the cabinet
    # it fronts: mixed-style chains split into per-style splines at the
    # cabinet seams (see _material_runs). Members that resolve no
    # material - appliance bridges - fall back to the first material
    # the chain resolves.
    member_materials = [(m, adapters.finish_material(m)) for m in chain]
    fallback_mat = next(
        (mat for _m, mat in member_materials if mat is not None), None)

    first_inv = first.matrix_world.inverted()
    wrote = 0
    for pts, cyclic in segments:
        for run_pts, material, run_cyclic in _material_runs(
                pts, cyclic, member_materials, fallback_mat):
            local = []
            for p in run_pts:
                lp = first_inv @ mathutils.Vector((p.x, p.y, 0.0))
                if not local or (abs(lp.x - local[-1][0]) > 1e-4
                                 or abs(lp.y - local[-1][1]) > 1e-4):
                    local.append((lp.x, lp.y, 0.0))
            if (run_cyclic and len(local) > 2
                    and abs(local[0][0] - local[-1][0]) < 1e-4
                    and abs(local[0][1] - local[-1][1]) < 1e-4):
                local.pop()
            if len(local) < (3 if run_cyclic else 2):
                continue
            spline = curve.splines.new('BEZIER')
            spline.use_smooth = False
            spline.bezier_points.add(count=len(local) - 1)
            for bp, co in zip(spline.bezier_points, local):
                bp.co = co
                bp.handle_left_type = 'VECTOR'
                bp.handle_right_type = 'VECTOR'
            spline.use_cyclic_u = run_cyclic
            if material is not None:
                spline.material_index = _material_slot(curve, material)
            wrote += 1
    if wrote == 0:
        bpy.data.objects.remove(sweep, do_unlink=True)
        bpy.data.objects.remove(profile, do_unlink=True)
        return None
    return sweep


def _apply_type(scene, molding_type, align, stack, opts):
    targets = adapters.collect_targets(scene, molding_type)
    if not targets:
        return 0
    members = list(targets)
    if molding_type == 'BASE':
        members += [b for b in adapters.collect_bridges(scene)
                    if b not in members]
    facts = adapters.build_facts(scene, members)
    resolved_stack = _resolve_stack(stack, opts)

    made = 0
    for component in engine.connected_components(members, align=align):
        if not any(m in targets for m in component):
            continue
        chain = engine.order_chain(component, align=align)
        run_stack = resolved_stack
        if molding_type == 'CROWN' and opts['to_ceiling']:
            # Ceiling-relative sizing is per run: the datum and the
            # ceiling line live in the (winding-normalized) first
            # member's local frame.
            result = engine.chain_sweep_points(chain, facts, 0.0, 0.0)
            if result is None:
                continue
            _pts, norm_chain = result
            run_stack = _ceiling_stack(norm_chain[0], facts,
                                       resolved_stack, opts)
        for profile_ref, fallback_key, dx, dy, height in run_stack:
            if molding_type == 'BASE':
                segments = engine.kick_sweep_segments(
                    chain, facts, dx, opts['include_recessed'])
                sweep_chain = chain
            elif molding_type == 'LIGHT_RAIL':
                result = engine.rail_sweep_segments(chain, facts, dx, dx)
                if result is None:
                    continue
                segments, sweep_chain = result
            else:
                if molding_type == 'CAP':
                    dx += opts['cap_overhang']
                result = engine.chain_sweep_points(chain, facts, dx, dx)
                if result is None:
                    continue
                pts, sweep_chain = result
                segments = [(pts, False)]
            if not segments:
                continue
            if _spawn_sweep(scene, molding_type, sweep_chain, segments,
                            profile_ref, fallback_key, dy, facts,
                            opts, height=height) is not None:
                made += 1
    return made


def _base_stack(hb, stack):
    """Base stack from the room settings: the package's base molding
    (empty when the package is None) with the room's base-profile
    choice swapped in, plus the base shoe when toggled on. The shoe's
    STACK_FRONT dx resolves to the molding's measured thickness so it
    applies to the front of the base molding; with no base molding it
    sits directly at the toe kick face (running front 0)."""
    profile = getattr(hb, 'molding_base_profile', 'DEFAULT')
    out = []
    for ref, fallback, dx, dy in stack:
        if (profile not in ('DEFAULT', '')
                and ref.replace("\\", "/").split("/")[0] == 'Base Molding'):
            ref = f"Base Molding/{profile}"
        out.append((ref, fallback, dx, dy))
    if getattr(hb, 'molding_base_shoe', False):
        out.append((packages.BASE_SHOE_REF, packages.BASE_SHOE_FALLBACK,
                    'STACK_FRONT', 0.0))
    return out


def apply_scene_packages(scene):
    """Rebuild every molding-package sweep in the scene from its three
    package props. Safe to call from prop update callbacks."""
    hb = getattr(scene, 'home_builder', None)
    if hb is None:
        return 0
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return 0
    clear_scene_molding(scene)

    def _override(prop_name):
        value = getattr(hb, prop_name, 'DEFAULT')
        return None if value in ('DEFAULT', '') else value

    crown_ident = getattr(hb, 'molding_crown_package', 'NONE')
    opts = {
        'include_recessed': getattr(hb, 'molding_base_include_recessed',
                                    False),
        'crown_reveal': getattr(hb, 'molding_crown_reveal', 0.0),
        'spacer_height': getattr(hb, 'molding_spacer_height',
                                 units.inch(3.5)),
        'to_ceiling': getattr(hb, 'molding_crown_to_ceiling', False),
        'ceiling_height': getattr(hb, 'ceiling_height', units.inch(96.0)),
        'cap_offset': getattr(hb, 'molding_cap_offset', 0.0),
        'cap_overhang': getattr(hb, 'molding_cap_overhang', 0.0),
        # The active crown stack, kept for the furniture cap's default
        # position (on top of the tallest crown-stack molding).
        'crown_stack': (packages.package_stack('CROWN', crown_ident)
                        if crown_ident != 'NONE' else None),
        'overrides': {
            'Crown Molding': _override('molding_crown_profile'),
            'Spacer': _override('molding_spacer_profile'),
            'Furniture Caps': _override('molding_cap_profile'),
            'Light Rail': _override('molding_light_rail_profile'),
        },
    }

    made = 0
    for prop_name, molding_type, align in _TYPES:
        ident = getattr(hb, prop_name, 'NONE')
        stack = (packages.package_stack(molding_type, ident)
                 if ident != 'NONE' else None)
        if molding_type == 'BASE':
            # The base shoe is independent of the package: with the
            # package set to None the shoe still runs, at the kick face.
            stack = _base_stack(hb, stack or [])
        if not stack:
            continue
        made += _apply_type(scene, molding_type, align, stack, opts)

    # The furniture cap is an independent toggle: it caps the top line
    # over whichever crown package (or none) sits at the reveal.
    if getattr(hb, 'molding_crown_furniture_cap', False):
        made += _apply_type(scene, 'CAP', 'top',
                            packages.FURNITURE_CAP_STACK, opts)
    return made


def on_package_changed(self, context):
    """Scene-prop update callback: re-apply immediately so the dropdown
    IS the interaction. Errors are contained so a bad room can't wedge
    the property system."""
    try:
        apply_scene_packages(self.id_data)
    except Exception as ex:  # pragma: no cover - defensive
        print(f"Home Builder molding: apply failed: {ex}")


class home_builder_OT_refresh_room_molding(bpy.types.Operator):
    """Rebuild this room's molding packages after cabinets change"""
    bl_idname = "home_builder.refresh_room_molding"
    bl_label = "Refresh Room Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        made = apply_scene_packages(context.scene)
        self.report({'INFO'}, f"Rebuilt {made} molding run(s)")
        return {'FINISHED'}


classes = (
    home_builder_OT_refresh_room_molding,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
