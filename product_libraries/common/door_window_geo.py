"""3D geometry for placed entry doors and windows.

A placed entry door / window is a GeoNodeCage that cuts the wall (see
operators/doors_windows.py). This module hangs real, render-visible
geometry off that cage as plain mesh children: jamb, casing, threshold,
sill, stool, door slabs and window sashes. Slabs and sashes build
through the shared python door builder (door_builder.build_door_mesh),
so entry doors carry the same 5-piece construction, raised panels and
mullion patterns cabinet fronts use.

Options live on the cage as an id-property dict (GEO_OPTS_PROP);
build_geometry re-reads it and replaces the children, so rebuilds are
idempotent and safe to run from the prompts dialogs, the swing flips
and the duplicate operators. A cage without the property builds
nothing -- legacy files and open doorways stay cage-only until a style
is assigned from the prompts.

Styles are JSON presets on disk (lengths in inches). Two roots are
searched -- the shipped door_window_styles folder next to this module
and a per-user folder installed style packs land in -- and user files
shadow shipped ones of the same name, so the defaults can be both
extended and overridden without touching the addon. Same dual-root
pattern as the cabinet pull libraries.
"""

import json
import math
import os
import zipfile

import bpy

from ... import hb_types
from ...units import inch
from . import door_builder


GEO_OPTS_PROP = "DOOR_WINDOW_GEO_OPTS"
GEO_CHILD_FLAG = "IS_DOOR_WINDOW_GEO"

DOOR_CATEGORY = "Entry Doors"
WINDOW_CATEGORY = "Windows"

# Mull post between a door and its sidelites / under a transom.
MULL_WIDTH = inch(1.0)


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

DOOR_STYLE_ITEMS = [
    ('PANEL_6', "6 Panel", "Colonial six panel (2 wide x 3 high)"),
    ('PANEL_4', "4 Panel", "Four panel (2 wide x 2 high)"),
    ('PANEL_3', "3 Panel", "Craftsman three vertical panels"),
    ('PANEL_2', "2 Panel", "Two stacked panels"),
    ('FLUSH', "Flush", "Flat slab"),
    ('LITE_QUARTER', "Quarter Lite", "Glass in the top quarter"),
    ('LITE_HALF', "Half Lite", "Glass in the top half"),
    ('LITE_34', "3/4 Lite", "Glass in the top three quarters"),
    ('LITE_FULL', "Full Lite", "Glass full height, optional grille grid"),
]

WINDOW_TYPE_ITEMS = [
    ('HUNG', "Hung", "Vertically sliding sashes with a check rail"),
    ('CASEMENT', "Casement", "Side-hinged sash (1 or 2 panes)"),
    ('SLIDER', "Slider", "Horizontally sliding sashes (2 or 3 panes)"),
    ('AWNING', "Awning", "Top-hinged sash, wider than tall"),
    ('PICTURE', "Picture", "Fixed non-operating sash"),
]

GRILLE_PATTERN_ITEMS = [
    ('NONE', "None", "Plain glass"),
    ('COLONIAL', "Colonial", "Divided lites in a columns x rows grid"),
    ('PRAIRIE', "Prairie", "Perimeter bars with small corner lites"),
]

# Glass share of the door height per partial-lite style.
_LITE_FRACTION = {'LITE_QUARTER': 0.30, 'LITE_HALF': 0.50, 'LITE_34': 0.72}

DOOR_DEFAULTS = {
    'style': 'CUSTOM',
    'door_style': 'PANEL_6',
    'panel_raise': True,
    'glass_grid_cols': 1,
    'glass_grid_rows': 1,
    'grille_bar_width': inch(0.875),
    'slab_thickness': inch(1.75),
    'stile_width': inch(4.5),
    'top_rail_width': inch(4.5),
    'bottom_rail_width': inch(9.5),
    'lock_rail_width': inch(7.0),
    'jamb_width': inch(0.75),
    'include_interior_casing': True,
    'include_exterior_casing': True,
    'casing_width': inch(2.25),
    'casing_thickness': inch(0.75),
    'threshold_height': inch(0.75),
    'include_knob': True,
    'sidelite_left': 0.0,
    'sidelite_right': 0.0,
    'transom_height': 0.0,
}

WINDOW_DEFAULTS = {
    'style': 'CUSTOM',
    'window_type': 'HUNG',
    'panes': 2,
    'sash_split': 0.5,
    'frame_width': inch(2.0),
    'sash_face_width': inch(2.0),
    'check_rail_width': inch(1.0),
    'sash_thickness': inch(1.375),
    'glass_thickness': inch(0.25),
    'grille_pattern': 'NONE',
    'grille_cols': 2,
    'grille_rows': 2,
    'grille_bar_width': inch(0.75),
    'include_exterior_casing': True,
    'include_interior_casing': True,
    'casing_width': inch(2.0),
    'casing_thickness': inch(0.75),
    'include_sill': True,
    'sill_height': inch(1.25),
    'sill_projection': inch(1.0),
    'sill_horn': inch(1.0),
    'include_stool': True,
}

# Preset JSON stores lengths in inches for readability; these keys are
# converted to meters on load (per category).
DOOR_LENGTH_KEYS = {
    'grille_bar_width', 'slab_thickness', 'stile_width', 'top_rail_width',
    'bottom_rail_width', 'lock_rail_width', 'jamb_width', 'casing_width',
    'casing_thickness', 'threshold_height', 'sidelite_left',
    'sidelite_right', 'transom_height',
}

WINDOW_LENGTH_KEYS = {
    'frame_width', 'sash_face_width', 'check_rail_width', 'sash_thickness',
    'glass_thickness', 'grille_bar_width', 'casing_width',
    'casing_thickness', 'sill_height', 'sill_projection', 'sill_horn',
}


def _category_for(cage_obj):
    if cage_obj.get('IS_WINDOW_BP'):
        return WINDOW_CATEGORY
    if cage_obj.get('IS_ENTRY_DOOR_BP'):
        return DOOR_CATEGORY
    return None


def _defaults_for(category):
    return WINDOW_DEFAULTS if category == WINDOW_CATEGORY else DOOR_DEFAULTS


def stored_opts(cage_obj):
    """The raw stored option dict, or None when the cage has never been
    given 3D geometry (legacy files, open doorways, cage-only)."""
    raw = cage_obj.get(GEO_OPTS_PROP)
    if raw is None:
        return None
    try:
        return dict(raw.to_dict())
    except AttributeError:
        return dict(raw)


def merged_opts(cage_obj):
    """Stored options merged over the kind's defaults with the default
    types enforced (id-props round-trip bools as ints), or None when
    nothing is stored."""
    category = _category_for(cage_obj)
    if category is None:
        return None
    stored = stored_opts(cage_obj)
    if stored is None:
        return None
    opts = dict(_defaults_for(category))
    for key, default in opts.items():
        if key not in stored:
            continue
        val = stored[key]
        if isinstance(default, bool):
            opts[key] = bool(val)
        elif isinstance(default, int) and not isinstance(default, bool):
            try:
                opts[key] = int(val)
            except (TypeError, ValueError):
                pass
        elif isinstance(default, float):
            try:
                opts[key] = float(val)
            except (TypeError, ValueError):
                pass
        else:
            opts[key] = str(val)
    return opts


def set_opts(cage_obj, opts):
    cage_obj[GEO_OPTS_PROP] = dict(opts)


def clear_opts(cage_obj):
    if GEO_OPTS_PROP in cage_obj:
        del cage_obj[GEO_OPTS_PROP]


# ---------------------------------------------------------------------------
# Style presets (dual-root JSON discovery, user shadows shipped)
# ---------------------------------------------------------------------------

def get_styles_root():
    """Absolute path to the shipped door_window_styles folder."""
    return os.path.join(os.path.dirname(__file__), 'door_window_styles')


def get_user_styles_root(create=False):
    """Per-user styles folder installed packs land in. Prefers Blender's
    per-extension user directory (survives addon updates); falls back to
    the user datafiles resource when not running as an extension."""
    addon_pkg = __package__.split('.product_libraries')[0]
    try:
        return bpy.utils.extension_path_user(
            addon_pkg, path='door_window_styles', create=create)
    except Exception:
        base = bpy.utils.user_resource(
            'DATAFILES', path='home_builder_5', create=create)
        path = os.path.join(base, 'door_window_styles')
        if create:
            os.makedirs(path, exist_ok=True)
        return path


def get_styles_roots():
    """Existing style roots in search order: user first so an installed
    style overrides a shipped one of the same name."""
    return [r for r in (get_user_styles_root(), get_styles_root())
            if os.path.isdir(r)]


def list_styles(category):
    """[(name, label, path, sort), ...] for every .json preset in the
    category folder across every root, sorted by the preset's optional
    'sort' number then label. A same-named file in the user root
    shadows the shipped one."""
    seen = {}
    for root in get_styles_roots():
        folder = os.path.join(root, category)
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            if not fname.lower().endswith('.json'):
                continue
            stem = os.path.splitext(fname)[0]
            if stem.lower() in seen:
                continue
            path = os.path.join(folder, fname)
            label, sort = stem, 100
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                label = str(data.get('label', stem))
                sort = int(data.get('sort', 100))
            except Exception:
                pass
            seen[stem.lower()] = (stem, label, path, sort)
    return sorted(seen.values(), key=lambda it: (it[3], it[1].lower()))


def load_style(category, name):
    """The preset's option dict with lengths converted from inches to
    meters, or None when the preset can't be found / read."""
    length_keys = (WINDOW_LENGTH_KEYS if category == WINDOW_CATEGORY
                   else DOOR_LENGTH_KEYS)
    for stem, _label, path, _sort in list_styles(category):
        if stem != name:
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return None
        raw = data.get('options', {})
        defaults = _defaults_for(category)
        opts = {}
        for key, val in raw.items():
            if key not in defaults:
                continue
            if key in length_keys:
                try:
                    val = inch(float(val))
                except (TypeError, ValueError):
                    continue
            opts[key] = val
        return opts
    return None


# Enum item lists are cached so the strings stay alive for as long as
# Blender holds references into them (dynamic-enum requirement).
_style_enum_cache = {}


def style_enum_items(category, include_custom=False, include_none=False):
    """Enum items for the category's style presets. NONE ('cage only,
    no 3D geometry') and CUSTOM ('keep the current fields') append at
    the end so the first preset stays the default."""
    styles = list_styles(category)
    key = (category, include_custom, include_none,
           tuple(s[0] for s in styles))
    cached = _style_enum_cache.get(key)
    if cached is not None:
        return cached
    items = [(stem, label, "Apply the %s style preset" % label)
             for stem, label, _path, _sort in styles]
    if include_custom:
        items.append(('CUSTOM', "Custom", "Keep the current option values"))
    if include_none:
        items.append(('NONE', "None (Cage Only)", "No 3D geometry"))
    if not items:
        items = [('NONE', "None (Cage Only)", "No 3D geometry")]
    _style_enum_cache[key] = items
    return items


def apply_scene_style_and_build(cage_obj, context):
    """Placement-drop hook: seed the cage's options from the scene's
    default style for its kind and build the geometry. A cage that
    already carries options (a duplicate) just rebuilds."""
    category = _category_for(cage_obj)
    if category is None:
        return
    if stored_opts(cage_obj) is not None:
        build_geometry(cage_obj)
        return
    props = context.scene.home_builder
    name = (props.window_style if category == WINDOW_CATEGORY
            else props.entry_door_style)
    if not name or name == 'NONE':
        return
    opts = load_style(category, name)
    if opts is None:
        return
    full = dict(_defaults_for(category))
    full.update(opts)
    full['style'] = name
    set_opts(cage_obj, full)
    build_geometry(cage_obj)


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------

def _material(name, color, roughness=0.5):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
    mat.diffuse_color = (*color, 1.0)
    return mat


def _trim_material():
    return _material('Door Window Trim', (0.92, 0.92, 0.90))


def _door_material():
    return _material('Entry Door Slab', (0.87, 0.85, 0.80))


def _glass_material():
    name = 'Door Window Glass'
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = (0.60, 0.75, 0.80, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = 0.25
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 1.0
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'BLENDED'
    elif hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    # Alpha in the solid-mode display color so glass reads as glass in
    # the workbench viewport too.
    mat.diffuse_color = (0.55, 0.70, 0.75, 0.25)
    return mat


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------

def _box(verts, faces, slots, x0, x1, y0, y1, z0, z1, slot=0):
    """Axis-aligned box appended to the caller's lists (outward faces,
    same winding as door_builder's part boxes). Degenerate boxes are
    skipped."""
    if x1 - x0 <= 1e-9 or y1 - y0 <= 1e-9 or z1 - z0 <= 1e-9:
        return
    b = len(verts)
    verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                  (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
    faces.extend([(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                  (b, b + 1, b + 5, b + 4), (b + 1, b + 2, b + 6, b + 5),
                  (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)])
    slots.extend([slot] * 6)


def _cylinder_y(verts, faces, slots, cx, cz, y0, y1, radius, slot=0,
                segs=16):
    """Closed cylinder along the Y axis (door knobs)."""
    if y1 - y0 <= 1e-9 or radius <= 1e-9:
        return
    b = len(verts)
    for y in (y0, y1):
        for i in range(segs):
            a = 2.0 * math.pi * i / segs
            verts.append((cx + radius * math.cos(a), y,
                          cz + radius * math.sin(a)))
    for i in range(segs):
        j = (i + 1) % segs
        faces.append((b + i, b + segs + i, b + segs + j, b + j))
        slots.append(slot)
    faces.append(tuple(b + i for i in reversed(range(segs))))
    slots.append(slot)
    faces.append(tuple(b + segs + i for i in range(segs)))
    slots.append(slot)


def _new_child(cage_obj, name):
    """A fresh mesh child of the cage: tagged as generated geometry,
    routed to the cage's right-click menu, linked wherever the cage is
    linked."""
    me = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, me)
    obj.parent = cage_obj
    obj[GEO_CHILD_FLAG] = True
    if cage_obj.get('MENU_ID'):
        obj['MENU_ID'] = cage_obj['MENU_ID']
    colls = list(cage_obj.users_collection)
    if not colls:
        colls = [bpy.context.scene.collection]
    for coll in colls:
        coll.objects.link(obj)
    return obj


def _finish_mesh(obj, verts, faces, slots, materials):
    me = obj.data
    me.from_pydata(verts, [], faces)
    me.materials.clear()
    for mat in materials:
        me.materials.append(mat)
    attr = (me.attributes.get('material_index')
            or me.attributes.new('material_index', 'INT', 'FACE'))
    attr.data.foreach_set('value', slots)
    me.validate()
    me.update()


def _door_mesh_child(cage_obj, name, info, kwargs, width, height, thickness,
                     materials, x, y_front, z):
    """One build_door_mesh product placed in cage-local space: the door
    width runs along +X from ``x``, the height up from ``z``, and the
    mesh's front face lands on the ``y_front`` plane (the door mesh is
    authored in front-cutpart local space; the (0, -90, 90) Euler is
    the standard reorientation, see wood_hoods._static_hood_door)."""
    obj = _new_child(cage_obj, name)
    door_builder.build_door_mesh(obj.data, info, width, height, thickness,
                                 materials=materials, **kwargs)
    obj.rotation_euler = (0.0, math.radians(-90.0), math.radians(90.0))
    obj.location = (x, y_front + thickness, z)
    return obj


def _glassify_above(obj, x_cut):
    """Partial-lite doors: retag every panel face above the lock rail
    (mesh-local X is the door height) onto a glass material slot."""
    me = obj.data
    me.materials.append(_glass_material())
    glass_idx = len(me.materials) - 1
    for poly in me.polygons:
        if poly.material_index == 2 and poly.center.x >= x_cut:
            poly.material_index = glass_idx


def remove_geometry(cage_obj):
    """Delete every generated geometry child (annotations and the swing
    stay)."""
    for child in list(cage_obj.children):
        if not child.get(GEO_CHILD_FLAG):
            continue
        me = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)


# ---------------------------------------------------------------------------
# Door construction
# ---------------------------------------------------------------------------

def _raise_section():
    """Simple synthesized raised-panel sweep section (field, bevel,
    tongue) so entry doors get a raise without depending on the
    profile asset library."""
    return dict(points=[(inch(1.5), 0.0), (inch(0.45), inch(0.19)),
                        (0.0, inch(0.19))],
                field_u=inch(1.5))


def _slab_spec(opts):
    """(info, kwargs, glass) for the door slab at the stored options.
    glass is 'NONE' (all wood), 'ALL' (every panel cell is glass) or
    'TOP' (glass above the lock rail, retagged after the build)."""
    info = dict(door_builder.DOOR_STYLE_FALLBACK)
    lock = max(opts['lock_rail_width'], inch(0.5))
    info.update(
        stile_width=max(opts['stile_width'], inch(0.5)),
        rail_width=max(opts['top_rail_width'], inch(0.5)),
        top_rail_width=max(opts['top_rail_width'], inch(0.5)),
        bottom_rail_width=max(opts['bottom_rail_width'], inch(0.5)),
    )
    p_th = min(inch(0.75), max(opts['slab_thickness'] - inch(0.5),
                               inch(0.25)))
    info['panel_thickness'] = p_th
    info['panel_inset'] = max((opts['slab_thickness'] - p_th) / 2.0, 0.0)
    kwargs = {}
    glass = 'NONE'
    style = opts['door_style']
    if style == 'FLUSH':
        info['door_type'] = 'SLAB'
    elif style == 'PANEL_2':
        info.update(mid_rail_count=1, mid_rail_width=lock,
                    mid_rail_fractions=[1.35, 1.0])
    elif style == 'PANEL_4':
        info.update(mid_rail_count=1, mid_stile_count=1,
                    mid_rail_width=lock, mid_stile_width=inch(1.25),
                    mid_rail_fractions=[1.35, 1.0])
    elif style == 'PANEL_6':
        info.update(mid_rail_count=2, mid_stile_count=1,
                    mid_rail_width=inch(4.0), mid_stile_width=inch(1.25),
                    mid_rail_fractions=[1.25, 1.55, 0.65])
    elif style == 'PANEL_3':
        info.update(mid_stile_count=2, mid_stile_width=inch(1.25))
    elif style == 'LITE_FULL':
        glass = 'ALL'
        cols = max(int(opts['glass_grid_cols']), 1)
        rows = max(int(opts['glass_grid_rows']), 1)
        if cols > 1 or rows > 1:
            bar = max(opts['grille_bar_width'], inch(0.5))
            info.update(mid_stile_count=cols - 1, mid_rail_count=rows - 1,
                        mid_stile_width=bar, mid_rail_width=bar)
    elif style in _LITE_FRACTION:
        glass = 'TOP'
        frac = _LITE_FRACTION[style]
        info.update(mid_rail_z=(1.0 - frac, 0.0), mid_rail_width=lock)
    if glass == 'NONE' and opts['panel_raise']:
        kwargs['panel_section'] = _raise_section()
    return info, kwargs, glass


def _sidelite_spec(opts):
    """A sidelite is a narrow full-lite fixed unit whose bottom rail
    lines through with the door's."""
    info = dict(door_builder.DOOR_STYLE_FALLBACK)
    info.update(
        stile_width=inch(2.0), rail_width=inch(2.0),
        top_rail_width=max(opts['top_rail_width'] / 2.0, inch(2.0)),
        bottom_rail_width=max(opts['bottom_rail_width'], inch(2.0)),
    )
    gt = inch(0.25)
    info['panel_thickness'] = gt
    info['panel_inset'] = max((opts['slab_thickness'] - gt) / 2.0, 0.0)
    return info


def _swing_child(cage_obj):
    for child in cage_obj.children:
        hbp = getattr(child, 'home_builder', None)
        if hbp and (hbp.mod_name or '').startswith('GeoNodeDoorSwing'):
            return child
    return None


def _swing_state(cage_obj):
    """(is_double, hinge_left) read off the swing annotation; single /
    hinge-left when there is none (open doorways)."""
    child = _swing_child(cage_obj)
    if child is None:
        return False, True
    swing = hb_types.GeoNodeObject(child)
    try:
        return bool(swing.get_input('Is Double')), \
            bool(swing.get_input('Is Left'))
    except Exception:
        return False, True


def _build_slab(cage_obj, name, opts, width, height, x, y_front):
    info, kwargs, glass = _slab_spec(opts)
    min_w, min_h = door_builder.layout_min_size(info)
    if width <= min_w or height <= min_h:
        info = dict(info, door_type='SLAB')
        glass = 'NONE'
    door_mat = _door_material()
    panel_mat = _glass_material() if glass == 'ALL' else door_mat
    obj = _door_mesh_child(
        cage_obj, name, info, kwargs, width, height,
        opts['slab_thickness'], (door_mat, door_mat, panel_mat),
        x, y_front, max(opts['threshold_height'], 0.0))
    if glass == 'TOP':
        frac = _LITE_FRACTION[opts['door_style']]
        mrw = max(opts['lock_rail_width'], inch(0.5))
        _glassify_above(obj, (1.0 - frac) * height + mrw / 2.0 - 0.001)
    return obj


def build_door_geometry(cage_obj):
    """Replace the door cage's generated children from its stored
    options: jamb, casing both faces, threshold, slab(s), optional
    sidelites / transom, and a knob on the latch side."""
    remove_geometry(cage_obj)
    opts = merged_opts(cage_obj)
    if opts is None:
        return
    cage = hb_types.GeoNodeCage(cage_obj)
    if not cage.has_modifier():
        return
    W = cage.get_input('Dim X')
    T = cage.get_input('Dim Y')
    H = cage.get_input('Dim Z')
    if W <= inch(6) or H <= inch(12) or T <= inch(0.5):
        return

    jw = min(max(opts['jamb_width'], inch(0.25)), inch(2.0))
    cw = max(opts['casing_width'], inch(0.5))
    ct = max(opts['casing_thickness'], inch(0.25))
    th_h = max(opts['threshold_height'], 0.0)
    st = max(opts['slab_thickness'], inch(0.75))
    trim_mat = _trim_material()

    verts, faces, slots = [], [], []

    # Jamb lining the rough opening, full wall depth.
    _box(verts, faces, slots, 0.0, jw, 0.0, T, 0.0, H)
    _box(verts, faces, slots, W - jw, W, 0.0, T, 0.0, H)
    _box(verts, faces, slots, jw, W - jw, 0.0, T, H - jw, H)
    if th_h > 0.0:
        _box(verts, faces, slots, jw, W - jw, 0.0, T, 0.0, th_h)

    # Casing rings (sides + head, no bottom) proud of each wall face.
    for on, y0, y1 in ((opts['include_exterior_casing'], T, T + ct),
                       (opts['include_interior_casing'], -ct, 0.0)):
        if not on:
            continue
        _box(verts, faces, slots, -cw, 0.0, y0, y1, 0.0, H)
        _box(verts, faces, slots, W, W + cw, y0, y1, 0.0, H)
        _box(verts, faces, slots, -cw, W + cw, y0, y1, H, H + cw)

    # Interior layout: sidelites and a transom subdivide the opening
    # with mull posts; the slab(s) take what remains.
    x0, x1 = jw, W - jw
    z_top = H - jw
    transom_h = max(opts['transom_height'], 0.0)
    if transom_h > z_top - th_h - inch(24):
        transom_h = 0.0
    sl_l = max(opts['sidelite_left'], 0.0)
    sl_r = max(opts['sidelite_right'], 0.0)
    if sl_l + sl_r > (x1 - x0) - inch(18):
        sl_l = sl_r = 0.0

    y_center_front = (T - st) / 2.0

    if transom_h > 0.0:
        zt0 = z_top - transom_h
        info = _sidelite_spec(opts)
        info['bottom_rail_width'] = inch(2.0)
        glass_mat = _glass_material()
        door_mat = _door_material()
        _door_mesh_child(
            cage_obj, "Transom", info, {}, x1 - x0, transom_h, st,
            (door_mat, door_mat, glass_mat), x0, y_center_front, zt0)
        _box(verts, faces, slots, x0, x1, y_center_front,
             y_center_front + st, zt0 - MULL_WIDTH, zt0)
        z_top = zt0 - MULL_WIDTH

    door_x0, door_x1 = x0, x1
    for side, sl in (('Left', sl_l), ('Right', sl_r)):
        if sl <= 0.0:
            continue
        info = _sidelite_spec(opts)
        glass_mat = _glass_material()
        door_mat = _door_material()
        if side == 'Left':
            _door_mesh_child(
                cage_obj, "Left Sidelite", info, {}, sl,
                z_top - th_h, st, (door_mat, door_mat, glass_mat),
                x0, y_center_front, th_h)
            _box(verts, faces, slots, x0 + sl, x0 + sl + MULL_WIDTH,
                 y_center_front, y_center_front + st, th_h, z_top)
            door_x0 = x0 + sl + MULL_WIDTH
        else:
            _door_mesh_child(
                cage_obj, "Right Sidelite", info, {}, sl,
                z_top - th_h, st, (door_mat, door_mat, glass_mat),
                x1 - sl, y_center_front, th_h)
            _box(verts, faces, slots, x1 - sl - MULL_WIDTH, x1 - sl,
                 y_center_front, y_center_front + st, th_h, z_top)
            door_x1 = x1 - sl - MULL_WIDTH

    slab_h = z_top - th_h
    slab_zone_w = door_x1 - door_x0
    is_double, hinge_left = _swing_state(cage_obj)
    slab_edges = []
    if is_double and slab_zone_w > inch(24):
        half = slab_zone_w / 2.0
        _build_slab(cage_obj, "Door Slab Left", opts, half, slab_h,
                    door_x0, y_center_front)
        _build_slab(cage_obj, "Door Slab Right", opts, half, slab_h,
                    door_x0 + half, y_center_front)
        # Double doors latch at the middle astragal.
        slab_edges = [door_x0 + half - inch(2.5),
                      door_x0 + half + inch(2.5)]
    else:
        _build_slab(cage_obj, "Door Slab", opts, slab_zone_w, slab_h,
                    door_x0, y_center_front)
        slab_edges = [door_x1 - inch(2.5) if hinge_left
                      else door_x0 + inch(2.5)]

    if opts['include_knob']:
        kz = th_h + min(inch(36.0), slab_h * 0.45)
        for kx in slab_edges:
            _cylinder_y(verts, faces, slots, kx, kz,
                        y_center_front - inch(2.25), y_center_front,
                        inch(1.0))
            _cylinder_y(verts, faces, slots, kx, kz,
                        y_center_front + st,
                        y_center_front + st + inch(2.25), inch(1.0))

    frame = _new_child(cage_obj, "Door Frame")
    _finish_mesh(frame, verts, faces, slots, [trim_mat])


# ---------------------------------------------------------------------------
# Window construction
# ---------------------------------------------------------------------------

def _sash_spec(opts, top_rail=None, bottom_rail=None):
    """(info, kwargs, materials) for one window sash: a 5-piece frame
    at the sash stock width with a centered glass panel; colonial
    grilles divide the glass with true bar members, prairie grilles
    ride the shared mullion machinery."""
    info = dict(door_builder.DOOR_STYLE_FALLBACK)
    fw = max(opts['sash_face_width'], inch(0.75))
    st = max(opts['sash_thickness'], inch(0.75))
    gt = min(max(opts['glass_thickness'], inch(0.125)), st - inch(0.25))
    inset = max((st - gt) / 2.0, 0.0)
    info.update(stile_width=fw, rail_width=fw, panel_thickness=gt,
                panel_inset=inset)
    if top_rail is not None:
        info['top_rail_width'] = max(top_rail, inch(0.5))
    if bottom_rail is not None:
        info['bottom_rail_width'] = max(bottom_rail, inch(0.5))
    kwargs = {}
    pattern = opts['grille_pattern']
    bar = max(opts['grille_bar_width'], inch(0.5))
    if pattern == 'COLONIAL':
        cols = max(int(opts['grille_cols']), 1)
        rows = max(int(opts['grille_rows']), 1)
        info.update(mid_stile_count=cols - 1, mid_rail_count=rows - 1,
                    mid_stile_width=bar, mid_rail_width=bar)
    elif pattern == 'PRAIRIE':
        kwargs['mullion'] = dict(pattern='PRAIRIE', bar_width=bar,
                                 depth=inset + 0.0005)
    trim_mat = _trim_material()
    materials = (trim_mat, trim_mat, _glass_material())
    return info, kwargs, materials


def build_window_geometry(cage_obj):
    """Replace the window cage's generated children from its stored
    options: frame, sashes per window type, sloped-sill stand-in,
    casing both faces and an interior stool."""
    remove_geometry(cage_obj)
    opts = merged_opts(cage_obj)
    if opts is None:
        return
    cage = hb_types.GeoNodeCage(cage_obj)
    if not cage.has_modifier():
        return
    W = cage.get_input('Dim X')
    T = cage.get_input('Dim Y')
    H = cage.get_input('Dim Z')
    if W <= inch(8) or H <= inch(8) or T <= inch(0.5):
        return

    fw = min(max(opts['frame_width'], inch(0.75)), min(W, H) / 4.0)
    st = max(opts['sash_thickness'], inch(0.75))
    cw = max(opts['casing_width'], inch(0.5))
    ct = max(opts['casing_thickness'], inch(0.25))
    trim_mat = _trim_material()

    verts, faces, slots = [], [], []

    # Frame lining the rough opening, full wall depth.
    _box(verts, faces, slots, 0.0, fw, 0.0, T, 0.0, H)
    _box(verts, faces, slots, W - fw, W, 0.0, T, 0.0, H)
    _box(verts, faces, slots, fw, W - fw, 0.0, T, 0.0, fw)
    _box(verts, faces, slots, fw, W - fw, 0.0, T, H - fw, H)

    ox0, ox1 = fw, W - fw
    oz0, oz1 = fw, H - fw
    ow, oh = ox1 - ox0, oz1 - oz0

    # Sash depth planes: exterior sashes sit behind the wall middle,
    # interior sashes in front of it (front face toward the room).
    y_ext_front = T / 2.0
    y_int_front = T / 2.0 - st
    y_center_front = (T - st) / 2.0

    wtype = opts['window_type']
    check = max(opts['check_rail_width'], inch(0.5))

    def sash(name, width, height, x, y_front, z, top_rail=None,
             bottom_rail=None):
        info, kwargs, materials = _sash_spec(opts, top_rail, bottom_rail)
        min_w, min_h = door_builder.layout_min_size(info)
        if width <= min_w or height <= min_h:
            info = dict(info, door_type='SLAB')
            kwargs = {}
        _door_mesh_child(cage_obj, name, info, kwargs, width, height, st,
                         materials, x, y_front, z)

    if wtype == 'HUNG':
        split = min(max(float(opts['sash_split']), 0.25), 0.75)
        zs = oz0 + oh * split
        sash("Bottom Sash", ow, zs - oz0, ox0, y_int_front, oz0,
             top_rail=check)
        sash("Top Sash", ow, oz1 - zs, ox0, y_ext_front, zs,
             bottom_rail=check)
    elif wtype in ('CASEMENT', 'SLIDER'):
        panes = max(int(opts['panes']), 1)
        panes = min(panes, 2 if wtype == 'CASEMENT' else 3)
        pw = ow / panes
        for i in range(panes):
            if wtype == 'SLIDER' and panes > 1:
                y_front = y_int_front if i % 2 == 0 else y_ext_front
            else:
                y_front = y_center_front
            sash("Sash %d" % (i + 1) if panes > 1 else "Sash",
                 pw, oh, ox0 + i * pw, y_front, oz0)
    else:  # AWNING / PICTURE
        sash("Sash", ow, oh, ox0, y_center_front, oz0)

    # Exterior sill: a projecting board under the frame (rectangular
    # stand-in for the sloped sill), with horns past the casing.
    sill_on = bool(opts['include_sill'])
    if sill_on:
        sh = max(opts['sill_height'], inch(0.5))
        sp = max(opts['sill_projection'], 0.0)
        horn = max(opts['sill_horn'], 0.0)
        ext_cw = cw if opts['include_exterior_casing'] else 0.0
        _box(verts, faces, slots, -ext_cw - horn, W + ext_cw + horn,
             T, T + ct + sp, -sh, 0.0)

    # Casing rings proud of each wall face; the exterior ring skips its
    # bottom leg when the sill is on, the interior when the stool is.
    for on, y0, y1, skip_bottom in (
            (opts['include_exterior_casing'], T, T + ct, sill_on),
            (opts['include_interior_casing'], -ct, 0.0,
             bool(opts['include_stool']))):
        if not on:
            continue
        _box(verts, faces, slots, -cw, 0.0, y0, y1, 0.0, H)
        _box(verts, faces, slots, W, W + cw, y0, y1, 0.0, H)
        _box(verts, faces, slots, -cw, W + cw, y0, y1, H, H + cw)
        if not skip_bottom:
            _box(verts, faces, slots, -cw, W + cw, y0, y1, -cw, 0.0)

    # Interior stool: top flush with the opening bottom, projecting
    # into the room past the casing, with an apron strip below.
    if opts['include_stool']:
        int_cw = cw if opts['include_interior_casing'] else 0.0
        _box(verts, faces, slots, -int_cw - inch(0.5),
             W + int_cw + inch(0.5), -ct - inch(1.0), 0.0,
             -inch(0.75), 0.0)
        _box(verts, faces, slots, -int_cw, W + int_cw, -ct, 0.0,
             -inch(0.75) - cw, -inch(0.75))

    frame = _new_child(cage_obj, "Window Frame")
    _finish_mesh(frame, verts, faces, slots, [trim_mat])


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def build_geometry(cage_obj):
    """Rebuild the cage's generated geometry from its stored options.
    No stored options -> any stale children are removed and nothing is
    built (cage-only display)."""
    if cage_obj.get('IS_WINDOW_BP'):
        build_window_geometry(cage_obj)
    elif cage_obj.get('IS_ENTRY_DOOR_BP'):
        build_door_geometry(cage_obj)


# ---------------------------------------------------------------------------
# Style pack install / open operators
# ---------------------------------------------------------------------------

_CATEGORY_FOLDERS = {
    DOOR_CATEGORY.lower(): DOOR_CATEGORY,
    WINDOW_CATEGORY.lower(): WINDOW_CATEGORY,
}


def _zip_style_entries(zf):
    """Yield (category, filename, member) for every .json preset in the
    zip. Category comes from a path segment matching a known category
    folder, else from the preset's own 'category' field."""
    for member in zf.namelist():
        if member.endswith('/') or not member.lower().endswith('.json'):
            continue
        parts = [p for p in member.replace('\\', '/').split('/') if p]
        fname = parts[-1]
        category = None
        for seg in parts[:-1]:
            category = _CATEGORY_FOLDERS.get(seg.lower())
            if category:
                break
        if category is None:
            try:
                data = json.loads(zf.read(member).decode('utf-8'))
                category = _CATEGORY_FOLDERS.get(
                    str(data.get('category', '')).lower())
            except Exception:
                category = None
        if category is None:
            continue
        yield category, fname, member


class HOME_BUILDER_OT_install_door_window_styles(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.install_style_pack"
    bl_label = "Install Door & Window Style Pack"
    bl_description = ("Install a zip of door / window style presets into "
                      "the user styles folder")
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: bpy.props.StringProperty(default='*.zip',
                                          options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath or not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "Select a style pack zip file")
            return {'CANCELLED'}
        root = get_user_styles_root(create=True)
        installed = 0
        try:
            with zipfile.ZipFile(self.filepath) as zf:
                for category, fname, member in _zip_style_entries(zf):
                    folder = os.path.join(root, category)
                    os.makedirs(folder, exist_ok=True)
                    # Only the basename is used, so a hostile zip path
                    # cannot escape the styles folder.
                    target = os.path.join(folder, os.path.basename(fname))
                    with open(target, 'wb') as f:
                        f.write(zf.read(member))
                    installed += 1
        except zipfile.BadZipFile:
            self.report({'ERROR'}, "Not a valid zip file")
            return {'CANCELLED'}
        if installed == 0:
            self.report({'WARNING'},
                        "No style presets found in the zip")
            return {'CANCELLED'}
        # No cache invalidation needed: the enum cache is keyed by the
        # style-name set, so new presets produce a fresh entry.
        self.report({'INFO'}, "Installed %d style preset%s" %
                    (installed, "" if installed == 1 else "s"))
        return {'FINISHED'}


class HOME_BUILDER_OT_open_door_window_styles_folder(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.open_styles_folder"
    bl_label = "Open Styles Folder"
    bl_description = ("Open the user door / window styles folder in the "
                      "file browser")

    def execute(self, context):
        path = get_user_styles_root(create=True)
        try:
            os.startfile(path)
        except AttributeError:
            import subprocess
            subprocess.Popen(['xdg-open', path])
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_install_door_window_styles,
    HOME_BUILDER_OT_open_door_window_styles_folder,
)


register, unregister = bpy.utils.register_classes_factory(classes)
