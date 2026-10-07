"""Closet crown molding.

Crown profiles live as .blend files under assets/moldings/crown/ (a
profile object per file, matching .png thumbnails). Add Molding traces
a 2D bevel curve along each qualifying bay's top front edge - per bay,
with returns to the wall at exposed ends, steps where a neighbor bay is
shallower, and skips for bays under 60" effective height - and bevels
it with the selected profile. Clear removes every molding object.

Curves parent to their starter root, so molding follows a moved closet;
it does NOT regenerate on bay edits - re-run Add Molding after layout
changes (Add clears the starter's previous crown first, so it's
idempotent).
"""
import os
import bpy

from ...units import inch


CROWN_DIR = os.path.join(os.path.dirname(__file__), 'assets',
                         'moldings', 'crown')
DEFAULT_PROFILE = 'L Crown with Light Shield.blend'
TAG_MOLDING = 'IS_CLOSET_MOLDING'

MIN_CROWN_HEIGHT = inch(60.0)

_enum_cache = None


def get_profile_files():
    """Sorted crown profile blends, standard profile hoisted first so
    the dynamic enum defaults to it."""
    if not os.path.isdir(CROWN_DIR):
        return []
    files = sorted(f for f in os.listdir(CROWN_DIR)
                   if f.lower().endswith('.blend'))
    if DEFAULT_PROFILE in files:
        files.remove(DEFAULT_PROFILE)
        files.insert(0, DEFAULT_PROFILE)
    return files


def _thumb_icon(stem):
    from . import props_closets
    pcoll = props_closets.get_starter_previews()
    key = f'crown_{stem}'
    if key in pcoll:
        return pcoll[key].icon_id
    path = os.path.join(CROWN_DIR, stem + '.png')
    if os.path.exists(path):
        return pcoll.load(key, path, 'IMAGE').icon_id
    return 0


def profile_enum_items(self, context):
    global _enum_cache
    if _enum_cache is None:
        items = []
        for i, fname in enumerate(get_profile_files()):
            stem = os.path.splitext(fname)[0]
            items.append((fname, stem, "", _thumb_icon(stem), i))
        _enum_cache = items or [('NONE', "None", "No profiles found")]
    return _enum_cache


def load_profile(filename):
    """The profile object for a crown blend (appended once, then reused
    by name; kept hidden - it only serves as the curves' bevel object).
    """
    if not filename or filename == 'NONE':
        return None
    stem = os.path.splitext(filename)[0]
    existing = bpy.data.objects.get(stem)
    if existing is not None:
        return existing
    path = os.path.join(CROWN_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = [n for n in src.objects if n == stem] or \
                list(src.objects)
    except Exception:
        return None
    profile = next((o for o in dst.objects if o is not None), None)
    if profile is None:
        return None
    try:
        bpy.context.scene.collection.objects.link(profile)
    except RuntimeError:
        pass
    profile.hide_viewport = True
    profile.hide_render = True
    return profile


def _bay_specs(root):
    """Per-bay (x0, x1, top, depth, qualifies) in starter-local space,
    panels covered (x0/x1 = outer faces of the bay's panels)."""
    scene_props = bpy.context.scene.hb_closets
    pt = scene_props.panel_thickness
    from . import types_closets
    bays = sorted([c for c in root.children
                   if c.get(types_closets.TAG_BAY_CAGE)],
                  key=lambda o: o.get('hb_bay_index', 0))
    specs = []
    for bay in bays:
        bp = bay.hb_closet_bay
        top = bay.location.z + bp.height
        specs.append({
            'x0': bay.location.x - pt,
            'x1': bay.location.x + bp.width + pt,
            'top': top,
            'depth': bp.depth,
            'ok': top >= MIN_CROWN_HEIGHT,
        })
    return specs


def _new_curve(root, profile, z):
    curve_data = bpy.data.curves.new('Crown Molding', type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = profile
    curve_data.use_fill_caps = True
    obj = bpy.data.objects.new('Crown Molding', curve_data)
    obj[TAG_MOLDING] = True
    obj['PROFILE_NAME'] = profile.name
    obj.modifiers.new('Edge Split', type='EDGE_SPLIT')
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    obj.matrix_parent_inverse.identity()
    obj.location = (0.0, 0.0, z)
    # Molding follows the closet's material selection.
    from . import materials_closets
    mat = materials_closets.load_material(
        getattr(bpy.context.scene.hb_closets, 'closet_material', ''))
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


def clear_starter_molding(root):
    for child in list(root.children):
        if child.get(TAG_MOLDING):
            bpy.data.objects.remove(child, do_unlink=True)


def add_crown_to_starter(root, profile):
    """One bevel curve per qualifying bay along its top front edge.
    Point logic: returns to the wall (y=0) at exposed ends and against
    lower neighbors, steps to a shallower neighbor's depth, nothing on
    the shared edge with an equal/deeper same-height neighbor. Bays
    under the height threshold are skipped and count as 'lower' for
    their neighbors. Idempotent: clears this starter's previous crown
    first."""
    clear_starter_molding(root)
    scene_props = bpy.context.scene.hb_closets
    pt = scene_props.panel_thickness
    specs = _bay_specs(root)
    tol = inch(0.05)
    made = 0
    for i, s in enumerate(specs):
        if not s['ok']:
            continue
        prev = specs[i - 1] if i > 0 else None
        nxt = specs[i + 1] if i + 1 < len(specs) else None
        prev_lower = prev is not None and (
            not prev['ok'] or prev['top'] < s['top'] - tol)
        next_lower = nxt is not None and (
            not nxt['ok'] or nxt['top'] < s['top'] - tol)

        pts = []
        no_back_left = False
        # Back left: exposed end / lower neighbor -> return to the
        # wall; shallower neighbor -> step out from its depth; an
        # equal-or-deeper same-height neighbor owns the shared edge.
        if prev is not None:
            if prev['depth'] >= s['depth'] - tol and not prev_lower:
                no_back_left = True
            elif prev_lower:
                pts.append((s['x0'], 0.0))
            else:
                pts.append((s['x0'], -prev['depth']))
        else:
            pts.append((s['x0'], 0.0))

        move_x = pt if (no_back_left and i != 0) else 0.0
        pts.append((s['x0'] + move_x, -s['depth']))   # front left
        pts.append((s['x1'], -s['depth']))            # front right

        # Back right (mirror of back-left).
        if nxt is not None:
            if nxt['depth'] >= s['depth'] - tol and not next_lower:
                if (nxt['depth'] > s['depth'] + tol
                        and nxt['top'] > s['top'] + tol):
                    pts[-1] = (s['x1'] - pt, -s['depth'])
            elif next_lower:
                pts.append((s['x1'], 0.0))
            else:
                pts.append((s['x1'], -nxt['depth']))
        else:
            pts.append((s['x1'], 0.0))

        obj = _new_curve(root, profile, s['top'])
        _fill_spline(obj, pts)
        made += 1
    return made
