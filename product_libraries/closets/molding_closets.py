"""Closet crown and base molding.

Profiles live as .blend files under assets/moldings/<kind>/ (a profile
object per file, matching .png thumbnails). Add Molding traces a 2D
bevel curve along each qualifying bay's front edge - per bay, with
returns to the wall at exposed ends and steps where a neighbor bay is
shallower - and bevels it with the selected profile. Clear removes
every molding object.

Crown runs the top edge and skips bays under 60" effective height.
Base runs the floor and skips hanging bays, which have no bottom edge
to trim; a hanging neighbor reads as a wall to the bay beside it, the
same way a short neighbor does for crown.

Curves parent to their starter root, so molding follows a moved closet;
it does NOT regenerate on bay edits - re-run Add Molding after layout
changes (Add clears the starter's previous run of that kind first, so
it is idempotent).
"""
import os
import bpy

from ...units import inch


MOLDING_ROOT = os.path.join(os.path.dirname(__file__), 'assets',
                            'moldings')
CROWN_DIR = os.path.join(MOLDING_ROOT, 'crown')
BASE_DIR = os.path.join(MOLDING_ROOT, 'base')
DEFAULT_PROFILE = 'L Crown with Light Shield.blend'
DEFAULT_BASE_PROFILE = 'BA01 4in.blend'
TAG_MOLDING = 'IS_CLOSET_MOLDING'
# Which run a curve belongs to, so adding one kind leaves the other
# standing and Clear can still take both.
PROP_MOLDING_KIND = 'hb_molding_kind'

MIN_CROWN_HEIGHT = inch(60.0)

# kind -> (directory, default profile, label used for object names)
KINDS = {
    'CROWN': (CROWN_DIR, DEFAULT_PROFILE, "Crown Molding"),
    'BASE': (BASE_DIR, DEFAULT_BASE_PROFILE, "Base Molding"),
}

_enum_cache = {}


def get_profile_files(kind='CROWN'):
    """Sorted profile blends for a kind, standard profile hoisted first
    so the dynamic enum defaults to it."""
    directory, default, _ = KINDS[kind]
    if not os.path.isdir(directory):
        return []
    files = sorted(f for f in os.listdir(directory)
                   if f.lower().endswith('.blend'))
    if default in files:
        files.remove(default)
        files.insert(0, default)
    return files


def _thumb_icon(kind, stem):
    from . import props_closets
    pcoll = props_closets.get_starter_previews()
    key = f'{kind.lower()}_{stem}'
    if key in pcoll:
        return pcoll[key].icon_id
    path = os.path.join(KINDS[kind][0], stem + '.png')
    if os.path.exists(path):
        return pcoll.load(key, path, 'IMAGE').icon_id
    return 0


def _enum_items(kind):
    items = _enum_cache.get(kind)
    if items is None:
        items = []
        for i, fname in enumerate(get_profile_files(kind)):
            stem = os.path.splitext(fname)[0]
            items.append((fname, stem, "", _thumb_icon(kind, stem), i))
        items = items or [('NONE', "None", "No profiles found")]
        _enum_cache[kind] = items
    return items


def profile_enum_items(self, context):
    return _enum_items('CROWN')


def base_profile_enum_items(self, context):
    return _enum_items('BASE')


def load_profile(filename, kind='CROWN'):
    """The profile object for a molding blend (appended once, then
    reused by name; kept hidden - it only serves as the curves' bevel
    object)."""
    if not filename or filename == 'NONE':
        return None
    stem = os.path.splitext(filename)[0]
    existing = bpy.data.objects.get(stem)
    if existing is not None:
        return existing
    path = os.path.join(KINDS[kind][0], filename)
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
    """Per-bay geometry in starter-local space, panels covered (x0/x1 =
    the outer faces of the bay's panels). `top`/`bottom` are the edges
    the two molding kinds run along; `floor` says whether the bay sits
    on the floor at all."""
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
            'bottom': bay.location.z,
            'depth': bp.depth,
            'floor': bp.floor_mounted,
            'ok': top >= MIN_CROWN_HEIGHT,
        })
    return specs


def _new_curve(root, profile, z, kind='CROWN'):
    label = KINDS[kind][2]
    curve_data = bpy.data.curves.new(label, type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.bevel_mode = 'OBJECT'
    curve_data.bevel_object = profile
    curve_data.use_fill_caps = True
    obj = bpy.data.objects.new(label, curve_data)
    obj[TAG_MOLDING] = True
    obj[PROP_MOLDING_KIND] = kind
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


def clear_starter_molding(root, kind=None):
    """Remove this starter's molding. With a kind, only that run goes,
    so adding base leaves crown standing. Curves from before the two
    runs were split carry no kind and read as crown."""
    removed = 0
    for child in list(root.children):
        if not child.get(TAG_MOLDING):
            continue
        if kind is not None and child.get(PROP_MOLDING_KIND,
                                          'CROWN') != kind:
            continue
        bpy.data.objects.remove(child, do_unlink=True)
        removed += 1
    return removed


def _add_molding(root, profile, kind):
    """One bevel curve per qualifying bay along its front edge - the top
    edge for crown, the floor for base.

    Point logic is the same for both runs: return to the wall (y=0) at
    an exposed end or against a neighbor that has no molding of its own,
    step to a shallower neighbor's depth, and put nothing on the shared
    edge with an equal-or-deeper neighbor that carries the run through.
    What differs is which bays qualify and what counts as a break in the
    run - crown skips bays under the minimum height and treats a shorter
    neighbor as a break, base skips hanging bays and treats a hanging
    neighbor as one.

    End returns are gated on the starter's Left/Right Finished End: a
    run that dies into a wall has nothing to return to. Idempotent -
    clears this starter's previous run of the same kind first."""
    clear_starter_molding(root, kind)
    scene_props = bpy.context.scene.hb_closets
    pt = scene_props.panel_thickness
    sp = root.hb_closet_starter
    specs = _bay_specs(root)
    tol = inch(0.05)
    crown = kind == 'CROWN'

    def qualifies(s):
        return s['ok'] if crown else s['floor']

    def breaks(other, s):
        """Neighbor has no run of its own here, so it reads as a wall."""
        if not qualifies(other):
            return True
        return crown and other['top'] < s['top'] - tol

    made = 0
    for i, s in enumerate(specs):
        if not qualifies(s):
            continue
        prev = specs[i - 1] if i > 0 else None
        nxt = specs[i + 1] if i + 1 < len(specs) else None
        prev_breaks = prev is not None and breaks(prev, s)
        next_breaks = nxt is not None and breaks(nxt, s)

        pts = []
        no_back_left = False
        # Back left: broken neighbor -> return to the wall; shallower
        # neighbor -> step out from its depth; an equal-or-deeper
        # continuing neighbor owns the shared edge.
        if prev is not None:
            if prev['depth'] >= s['depth'] - tol and not prev_breaks:
                no_back_left = True
            elif prev_breaks:
                pts.append((s['x0'], 0.0))
            else:
                pts.append((s['x0'], -prev['depth']))
        elif sp.left_finished_end:
            pts.append((s['x0'], 0.0))
        else:
            no_back_left = True

        move_x = pt if (no_back_left and i != 0) else 0.0
        pts.append((s['x0'] + move_x, -s['depth']))   # front left
        pts.append((s['x1'], -s['depth']))            # front right

        # Back right (mirror of back-left).
        if nxt is not None:
            if nxt['depth'] >= s['depth'] - tol and not next_breaks:
                if (crown and nxt['depth'] > s['depth'] + tol
                        and nxt['top'] > s['top'] + tol):
                    pts[-1] = (s['x1'] - pt, -s['depth'])
            elif next_breaks:
                pts.append((s['x1'], 0.0))
            else:
                pts.append((s['x1'], -nxt['depth']))
        elif sp.right_finished_end:
            pts.append((s['x1'], 0.0))

        z = s['top'] if crown else s['bottom']
        obj = _new_curve(root, profile, z, kind)
        _fill_spline(obj, pts)
        made += 1
    return made


def add_crown_to_starter(root, profile):
    """Crown along the top front edge of every bay tall enough for it."""
    return _add_molding(root, profile, 'CROWN')


def add_base_to_starter(root, profile):
    """Base along the floor front edge of every floor-mounted bay."""
    return _add_molding(root, profile, 'BASE')
