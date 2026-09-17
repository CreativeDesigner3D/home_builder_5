"""Frameless crown molding, the way the closet library does it.

One profile picked for the room, from the closet library's crown
folder, and one command that runs it along the top front edge of every
cabinet tall enough to carry it. Each cabinet gets a 2D bevel curve in
its own space, parented to it so the crown follows a moved cabinet.
Neighbours on the same wall that continue the run share the edge; a
shallower neighbour gets a step, and an exposed end or a neighbour with
no crown of its own gets a return to the wall.

The previous crown system drew profiles in detail scenes and assigned
them per cabinet; it is left registered for files that used it, but
nothing in the panel reaches it any more.

Curves do not regenerate on layout edits -- re-run Add Crown after
moving cabinets (Add clears the room's previous run first, so it is
idempotent). Picking a different profile re-runs it for you when the
room already has crown.
"""

import bpy

from ...units import inch
from ..closets import molding_closets

TAG_MOLDING = 'IS_FRAMELESS_MOLDING'
PROP_MOLDING_KIND = 'hb_molding_kind'
MIN_CROWN_HEIGHT = inch(60.0)
KIND = 'CROWN'


def profile_enum_items(self, context):
    """The closet library's crown profiles, thumbnails included."""
    return molding_closets.profile_enum_items(self, context)


def profile_thumbnail(ident):
    """Picture for a crown profile file, or None."""
    import os
    stem, ext = os.path.splitext(ident or '')
    if ext.lower() != '.blend':
        return None
    path = os.path.join(molding_closets.CROWN_DIR, stem + '.png')
    return path if os.path.exists(path) else None


def load_profile(filename):
    return molding_closets.load_profile(filename, KIND)


def current_profile_name(scene):
    """The room's pick, or the standard profile while the dynamic enum
    still reads back empty."""
    return (getattr(scene.hb_frameless, 'crown_profile', '')
            or molding_closets.KINDS[KIND][1])


# ---- Which cabinets, and where their edges are ---------------------------

def _dims(obj):
    from ... import hb_types
    cage = hb_types.GeoNodeCage(obj)
    return (cage.get_input('Dim X'), cage.get_input('Dim Y'),
            cage.get_input('Dim Z'))


def _is_run_cabinet(obj):
    """A frameless cabinet whose footprint is a plain box: corner
    cabinets (with their wing depths) and flattened cabinets are left
    alone."""
    if not obj.get('IS_FRAMELESS_CABINET_CAGE'):
        return False
    if 'Left Depth' in obj or 'Right Depth' in obj:
        return False
    return any(m.type == 'NODES' and m.node_group for m in obj.modifiers)


def _specs(scene):
    """Cabinets grouped into runs -- same parent, same heading -- each
    run sorted along its wall. A spec carries the cabinet and its edges
    in the PARENT's space, which is what neighbours are compared in."""
    groups = {}
    for obj in scene.objects:
        if not _is_run_cabinet(obj):
            continue
        try:
            dim_x, dim_y, dim_z = _dims(obj)
        except Exception:
            continue
        if not dim_x or not dim_y or not dim_z:
            continue
        key = (obj.parent.name if obj.parent else '',
               round(obj.matrix_local.to_euler().z, 3))
        groups.setdefault(key, []).append({
            'obj': obj,
            'x0': obj.matrix_local.translation.x,
            'x1': obj.matrix_local.translation.x + dim_x,
            'top': obj.matrix_local.translation.z + dim_z,
            'depth': dim_y,
            'width': dim_x,
            'height': dim_z,
            'ok': obj.matrix_local.translation.z + dim_z >= MIN_CROWN_HEIGHT,
        })
    runs = []
    for specs in groups.values():
        specs.sort(key=lambda s: s['x0'])
        runs.append(specs)
    return runs


# ---- Curves ------------------------------------------------------------------

def _crown_material(cabinet):
    """The cabinet's own finish, so the crown matches what it sits on."""
    try:
        from ... import hb_project
        props = hb_project.get_main_scene().hb_frameless
        index = cabinet.get('CABINET_STYLE_INDEX', 0)
        if not len(props.cabinet_styles):
            return None
        style = props.cabinet_styles[min(index, len(props.cabinet_styles) - 1)]
        mat, _ = style.get_finish_material()
        return mat
    except Exception:
        return None


def _new_curve(cabinet, profile, z):
    label = "Crown Molding"
    curve_data = bpy.data.curves.new(label, type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = profile
    curve_data.use_fill_caps = True
    obj = bpy.data.objects.new(label, curve_data)
    obj[TAG_MOLDING] = True
    obj[PROP_MOLDING_KIND] = KIND
    obj['PROFILE_NAME'] = profile.name
    obj.modifiers.new('Edge Split', type='EDGE_SPLIT')
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = cabinet
    obj.matrix_parent_inverse.identity()
    obj.location = (0.0, 0.0, z)
    mat = _crown_material(cabinet)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def _fill_spline(obj, points):
    spline = obj.data.splines.new('BEZIER')
    spline.bezier_points.add(count=len(points) - 1)
    for bp, (x, y) in zip(spline.bezier_points, points):
        bp.co = (x, y, 0.0)
        bp.handle_left_type = 'VECTOR'
        bp.handle_right_type = 'VECTOR'


def clear_molding(scene):
    """Remove every crown run in the room."""
    removed = 0
    for obj in list(scene.objects):
        if obj.get(TAG_MOLDING):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1
    return removed


def has_molding(scene):
    return any(obj.get(TAG_MOLDING) for obj in scene.objects)


def add_crown(scene, profile):
    """Crown along the top front edge of every cabinet tall enough for
    it. Point logic follows the closet library: an exposed end, or a
    neighbour that carries no crown, gets a return to the wall; a
    shallower neighbour a step out from its depth; an equal-or-deeper
    neighbour that continues the run owns the shared edge. Points are
    in the cabinet's own space -- origin at its back-left corner, the
    front at -depth -- and the curve sits at its top."""
    clear_molding(scene)
    tol = inch(0.05)
    made = 0
    for specs in _specs(scene):
        for i, s in enumerate(specs):
            if not s['ok']:
                continue
            prev = specs[i - 1] if i > 0 else None
            nxt = specs[i + 1] if i + 1 < len(specs) else None
            # A neighbour counts only when it actually touches.
            if prev is not None and prev['x1'] < s['x0'] - tol:
                prev = None
            if nxt is not None and nxt['x0'] > s['x1'] + tol:
                nxt = None

            def breaks(other):
                return (not other['ok']
                        or abs(other['top'] - s['top']) > tol)

            w, d = s['width'], s['depth']
            pts = []
            if prev is not None and not breaks(prev):
                if prev['depth'] < d - tol:
                    pts.append((0.0, -prev['depth']))
            else:
                pts.append((0.0, 0.0))
            pts.append((0.0, -d))
            pts.append((w, -d))
            if nxt is not None and not breaks(nxt):
                if nxt['depth'] < d - tol:
                    pts.append((w, -nxt['depth']))
            else:
                pts.append((w, 0.0))
            if len(pts) < 2:
                continue
            obj = _new_curve(s['obj'], profile, s['height'])
            _fill_spline(obj, pts)
            made += 1
    return made


def update_profile(self, context):
    """Dropdown callback: a room that already has crown is re-run with
    the new profile."""
    scene = getattr(context, 'scene', None) or bpy.context.scene
    if not has_molding(scene):
        return
    profile = load_profile(current_profile_name(scene))
    if profile is not None:
        add_crown(scene, profile)
