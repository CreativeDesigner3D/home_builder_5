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

Styles are built-in preset tables (DOOR_STYLE_PRESETS /
WINDOW_STYLE_PRESETS) feeding the scene-default dropdowns and the
prompts dialogs. Extensibility comes through GEOMETRY asset packs
instead: door handle models install as .blend files into a per-user
folder (zip installer, user files shadow shipped ones of the same
name -- the same dual-root pattern as the cabinet pull libraries).

Handle asset convention: each .blend contributes its first mesh
object, with its origin at the latch mount point on the door face.
Each face's handle places at its mount point rotated by the per-door
Front / Back rotation options (XYZ degrees, defaults (0, 180, 0) and
(180, 180, 0)) -- handle models are not all authored in one
orientation, so the angles are editable in the door prompts rather
than fixed. Both ride the leaf's open-swing transform. Placed handles
link the source mesh, so every door updates if the asset is swapped.
"""

import math
import os
import zipfile

import bpy
from mathutils import Euler, Matrix, Vector

from ... import hb_types
from ...hb_details import GeoNodeText
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
    'handle': 'DEFAULT',
    # Handle asset orientation, XYZ euler degrees applied at the mount
    # point of each face. Editable per door in the prompts because
    # handle models are not all authored in one orientation.
    'handle_rot_front_x': 0.0,
    'handle_rot_front_y': 180.0,
    'handle_rot_front_z': 0.0,
    'handle_rot_back_x': 180.0,
    'handle_rot_back_y': 180.0,
    'handle_rot_back_z': 0.0,
    'open_angle': 0.0,
    'sidelite_left': 0.0,
    'sidelite_right': 0.0,
    'transom_height': 0.0,
    # Splayed reveal: two INDEPENDENT reveals, one carved in from each
    # wall face (reveal_ext_* from the y=0 face, reveal_int_* from the
    # y=thickness face - "ext"/"int" just name the wall's own two faces,
    # not a verified real-world exterior/interior). Each, when its _on
    # flag is set, is a sequence measured in from its own face:
    # 1. An instant 90-degree step outward by `_clearance_amount` (not a
    #    taper), then straight for `_clearance_depth` (bare reveal, no
    #    frame material).
    # 2. Widened further outward by `_splay_amount` (a distance, not an
    #    angle) as a taper over `_splay_depth`.
    # Any depth left over after a side's stages (before reaching the
    # opposite face or the other side's own reveal) stays straight at
    # that side's final widened size.
    #
    # The frame/casing material only ever occupies the middle span NOT
    # claimed by an active reveal - i.e. wall_thickness minus each active
    # side's (clearance_depth + splay_depth). Both reveals off keeps the
    # old plain straight-through cut, frame filling the full thickness.
    'reveal_ext_on': False,
    'reveal_ext_clearance_amount': 0.0,
    'reveal_ext_clearance_depth': 0.0,
    'reveal_ext_splay_amount': 0.0,
    'reveal_ext_splay_depth': 0.0,
    'reveal_int_on': False,
    'reveal_int_clearance_amount': 0.0,
    'reveal_int_clearance_depth': 0.0,
    'reveal_int_splay_amount': 0.0,
    'reveal_int_splay_depth': 0.0,
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
    # Splayed reveal: two INDEPENDENT reveals, one carved in from each
    # wall face (reveal_ext_* from the y=0 face, reveal_int_* from the
    # y=thickness face - "ext"/"int" just name the wall's own two faces,
    # not a verified real-world exterior/interior). Each, when its _on
    # flag is set, is a sequence measured in from its own face:
    # 1. An instant 90-degree step outward by `_clearance_amount` (not a
    #    taper), then straight for `_clearance_depth` (bare reveal, no
    #    frame material).
    # 2. Widened further outward by `_splay_amount` (a distance, not an
    #    angle) as a taper over `_splay_depth`.
    # Any depth left over after a side's stages (before reaching the
    # opposite face or the other side's own reveal) stays straight at
    # that side's final widened size.
    #
    # The frame/casing material only ever occupies the middle span NOT
    # claimed by an active reveal - i.e. wall_thickness minus each active
    # side's (clearance_depth + splay_depth). Both reveals off keeps the
    # old plain straight-through cut, frame filling the full thickness.
    'reveal_ext_on': False,
    'reveal_ext_clearance_amount': 0.0,
    'reveal_ext_clearance_depth': 0.0,
    'reveal_ext_splay_amount': 0.0,
    'reveal_ext_splay_depth': 0.0,
    'reveal_int_on': False,
    'reveal_int_clearance_amount': 0.0,
    'reveal_int_clearance_depth': 0.0,
    'reveal_int_splay_amount': 0.0,
    'reveal_int_splay_depth': 0.0,
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
# Style presets (built-in tables; tuple order is display order)
# ---------------------------------------------------------------------------

DOOR_STYLE_PRESETS = (
    ('6 Panel', "6 Panel",
     dict(door_style='PANEL_6', panel_raise=True)),
    ('2 Panel Shaker', "2 Panel Shaker",
     dict(door_style='PANEL_2', panel_raise=False)),
    ('Craftsman 3 Panel', "Craftsman 3 Panel",
     dict(door_style='PANEL_3', panel_raise=False,
          top_rail_width=inch(6.0))),
    ('Flush', "Flush", dict(door_style='FLUSH')),
    ('Quarter Lite', "Quarter Lite",
     dict(door_style='LITE_QUARTER', panel_raise=False)),
    ('Half Lite', "Half Lite",
     dict(door_style='LITE_HALF', panel_raise=False)),
    ('Three Quarter Lite', "Three Quarter Lite",
     dict(door_style='LITE_34', panel_raise=False)),
    ('Full Lite', "Full Lite", dict(door_style='LITE_FULL')),
    ('Full Lite 15 Grid', "Full Lite 15 Grid",
     dict(door_style='LITE_FULL', glass_grid_cols=3, glass_grid_rows=5)),
    ('6 Panel with Sidelites', "6 Panel with Sidelites",
     dict(door_style='PANEL_6', panel_raise=True,
          sidelite_left=inch(14.0), sidelite_right=inch(14.0))),
    ('Half Lite with Transom', "Half Lite with Transom",
     dict(door_style='LITE_HALF', panel_raise=False,
          transom_height=inch(14.0))),
)

WINDOW_STYLE_PRESETS = (
    ('Double Hung', "Double Hung", dict(window_type='HUNG')),
    ('Double Hung 6 Lite', "Double Hung 6 Lite",
     dict(window_type='HUNG', grille_pattern='COLONIAL',
          grille_cols=3, grille_rows=2)),
    ('Cottage Hung', "Cottage Hung",
     dict(window_type='HUNG', sash_split=0.6)),
    ('Casement', "Casement", dict(window_type='CASEMENT', panes=1)),
    ('Casement Pair', "Casement Pair",
     dict(window_type='CASEMENT', panes=2)),
    ('Slider XO', "Slider XO", dict(window_type='SLIDER', panes=2)),
    ('Slider XOX', "Slider XOX", dict(window_type='SLIDER', panes=3)),
    ('Awning', "Awning", dict(window_type='AWNING')),
    ('Picture', "Picture", dict(window_type='PICTURE')),
    ('Picture Prairie', "Picture Prairie",
     dict(window_type='PICTURE', grille_pattern='PRAIRIE')),
)


def _presets_for(category):
    return (WINDOW_STYLE_PRESETS if category == WINDOW_CATEGORY
            else DOOR_STYLE_PRESETS)


def list_styles(category):
    """[(name, label), ...] for the category's presets, in display
    order."""
    return [(name, label) for name, label, _opts in _presets_for(category)]


def load_style(category, name):
    """The preset's option dict (values already in meters), or None."""
    for pname, _label, opts in _presets_for(category):
        if pname == name:
            return dict(opts)
    return None


# ---------------------------------------------------------------------------
# Door handle asset library (dual-root .blend discovery, user shadows
# shipped -- the cabinet-pull pattern)
# ---------------------------------------------------------------------------

def get_handles_root():
    """Absolute path to the shipped door handle assets folder (may not
    exist -- shipping handles is optional)."""
    return os.path.join(os.path.dirname(__file__), 'door_handle_assets')


def get_user_handles_root(create=False):
    """Per-user handle folder installed packs land in. Prefers
    Blender's per-extension user directory (survives addon updates);
    falls back to the user datafiles resource when not running as an
    extension."""
    addon_pkg = __package__.split('.product_libraries')[0]
    try:
        return bpy.utils.extension_path_user(
            addon_pkg, path='door_handles', create=create)
    except Exception:
        base = bpy.utils.user_resource(
            'DATAFILES', path='home_builder_5', create=create)
        path = os.path.join(base, 'door_handles')
        if create:
            os.makedirs(path, exist_ok=True)
        return path


def get_handles_roots():
    """Existing handle roots in search order: user first so an
    installed handle overrides a shipped one of the same name."""
    return [r for r in (get_user_handles_root(), get_handles_root())
            if os.path.isdir(r)]


def list_handles():
    """[(filename, label), ...] for every .blend handle across every
    root (subfolders included), label = filename stem, sorted by label.
    A same-named file in the user root shadows the shipped one."""
    seen = {}
    for root in get_handles_roots():
        for folder, _dirs, files in os.walk(root):
            for fname in files:
                if not fname.lower().endswith('.blend'):
                    continue
                if fname.lower() in seen:
                    continue
                seen[fname.lower()] = (fname, os.path.splitext(fname)[0])
    return sorted(seen.values(), key=lambda it: it[1].lower())


def find_handle_file(filename):
    """Absolute path for a handle .blend, searching every root in
    order; None when not found."""
    for root in get_handles_roots():
        for folder, _dirs, files in os.walk(root):
            if filename in files:
                return os.path.join(folder, filename)
    return None


# Loaded handle source objects keyed by filename; instances link each
# source's mesh data, so swapping the source updates every door. Dead
# references (file reload / purge) are detected and reloaded.
_handle_cache = {}


def load_handle_object(filename):
    """The first mesh object out of a handle .blend (cached), or None.
    The object is loaded into bpy.data but not linked to any scene --
    placed handles link its MESH into their own child objects."""
    cached = _handle_cache.get(filename)
    if cached is not None:
        try:
            cached.name  # dead-reference check
            return cached
        except ReferenceError:
            pass
    path = find_handle_file(filename)
    if path is None:
        return None
    try:
        with bpy.data.libraries.load(path) as (data_from, data_to):
            data_to.objects = list(data_from.objects)
    except Exception:
        return None
    for obj in data_to.objects:
        if obj is not None and obj.type == 'MESH':
            _handle_cache[filename] = obj
            return obj
    return None


_handle_enum_cache = {}


def handle_enum_items():
    """Enum items for the door handle picker: the built-in default
    knob plus every installed handle asset. Cached so the strings stay
    alive for Blender's dynamic-enum requirement."""
    handles = list_handles()
    key = tuple(h[0] for h in handles)
    cached = _handle_enum_cache.get(key)
    if cached is not None:
        return cached
    items = [('DEFAULT', "Default Knob", "Built-in door knob")]
    items += [(fname, label, "Installed handle asset %s" % label)
              for fname, label in handles]
    _handle_enum_cache[key] = items
    return items


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
    items = [(name, label, "Apply the %s style preset" % label)
             for name, label in styles]
    if include_custom:
        items.append(('CUSTOM', "Custom (No Preset)",
                      "Keep the current option values"))
    if include_none:
        items.append(('NONE', "No 3D Geometry (Cage Only)",
                      "Remove the 3D geometry and show only the "
                      "wireframe cage"))
    if not items:
        items = [('NONE', "No 3D Geometry (Cage Only)",
                  "Remove the 3D geometry and show only the "
                  "wireframe cage")]
    _style_enum_cache[key] = items
    return items


def door_unit_extras(opts):
    """(extra_width, extra_height) a door unit needs beyond the slab
    for its sidelites / transom, mull posts included. Used to grow the
    cage when a preset introduces them, so the door slab keeps its
    size instead of shrinking to make room."""
    extra_w = 0.0
    for key in ('sidelite_left', 'sidelite_right'):
        try:
            val = float(opts.get(key, 0.0))
        except (TypeError, ValueError):
            val = 0.0
        if val > 0.0:
            extra_w += val + MULL_WIDTH
    try:
        transom = float(opts.get('transom_height', 0.0))
    except (TypeError, ValueError):
        transom = 0.0
    extra_h = transom + MULL_WIDTH if transom > 0.0 else 0.0
    return extra_w, extra_h


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
    if category == DOOR_CATEGORY:
        # A preset with sidelites / a transom describes a wider / taller
        # UNIT: grow the opening so the door slab keeps the placed size.
        extra_w, extra_h = door_unit_extras(full)
        if extra_w > 0.0 or extra_h > 0.0:
            cage = hb_types.GeoNodeCage(cage_obj)
            if cage.has_modifier():
                if extra_w > 0.0:
                    cage.set_input('Dim X',
                                   cage.get_input('Dim X') + extra_w)
                if extra_h > 0.0:
                    cage.set_input('Dim Z',
                                   cage.get_input('Dim Z') + extra_h)
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


def _handle_material():
    """Brushed-metal material for the built-in knob (handle assets
    keep their own materials)."""
    name = 'Door Handle Metal'
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = _material(name, (0.62, 0.62, 0.64), roughness=0.35)
    bsdf = next((n for n in mat.node_tree.nodes
                 if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None and 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = 1.0
    return mat


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


def _lathe_z(verts, faces, slots, cx, cy, z_base, profile, slot=0,
             segs=16, flip=False):
    """Surface of revolution around the Z axis at (cx, cy): ``profile``
    is [(radius, offset)] walked base-outward, offsets measured along
    +Z from ``z_base`` (negated when ``flip`` -- the back-face handle).
    Rings are quad-stitched; a near-zero radius closes at a pole, and a
    nonzero first ring is capped flat. Used for the built-in door knob,
    authored in the door mesh's local space so it rides the slab's
    transform."""
    sgn = -1.0 if flip else 1.0
    b0 = len(faces)
    ring_of = []
    for radius, offset in profile:
        z = z_base + sgn * offset
        if radius <= 1e-6:
            ring_of.append((len(verts), True))
            verts.append((cx, cy, z))
            continue
        ring_of.append((len(verts), False))
        for i in range(segs):
            a = 2.0 * math.pi * i / segs
            verts.append((cx + radius * math.cos(a),
                          cy + radius * math.sin(a), z))
    first, first_pole = ring_of[0]
    if not first_pole:
        faces.append(tuple(first + i for i in reversed(range(segs))))
        slots.append(slot)
    for k in range(len(ring_of) - 1):
        (a, a_pole), (b, b_pole) = ring_of[k], ring_of[k + 1]
        for i in range(segs):
            j = (i + 1) % segs
            if a_pole and b_pole:
                continue
            if a_pole:
                faces.append((a, b + j, b + i))
            elif b_pole:
                faces.append((a + i, a + j, b))
            else:
                faces.append((a + i, a + j, b + j, b + i))
            slots.append(slot)
    if flip:
        # Mirrored along Z: reverse windings so normals stay outward.
        for k in range(b0, len(faces)):
            faces[k] = tuple(reversed(faces[k]))


# Built-in default knob: rose plate, tapered stem, ball. (radius,
# projection-from-door-face) pairs in inches, lathed around the knob
# axis.
_KNOB_PROFILE = (
    (1.35, 0.00), (1.35, 0.28), (0.55, 0.40), (0.50, 1.05),
    (0.90, 1.40), (1.10, 1.85), (0.95, 2.35), (0.50, 2.62), (0.0, 2.72),
)


def _new_child(cage_obj, name, mesh=None):
    """A mesh child of the cage: tagged as generated geometry, routed
    to the cage's right-click menu, linked wherever the cage is linked.
    ``mesh`` links existing mesh data (handle assets) instead of
    creating a fresh empty mesh."""
    me = mesh if mesh is not None else bpy.data.meshes.new(name)
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


def remove_geometry(cage_obj, restore_annotations=False):
    """Delete every generated geometry child (the swing annotation
    stays). ``restore_annotations`` brings back the DOOR / WINDOW text
    label a geometry build removed -- used when the user returns an
    opening to cage-only display, not by the rebuild path."""
    for child in list(cage_obj.children):
        if not child.get(GEO_CHILD_FLAG):
            continue
        me = child.data
        bpy.data.objects.remove(child, do_unlink=True)
        if me is not None and me.users == 0:
            bpy.data.meshes.remove(me)
    if restore_annotations:
        _ensure_annotation_text(cage_obj, True)


REVEAL_CUTTER_FLAG = "IS_REVEAL_CUTTER"


def _reveal_cutter_child(cage_obj):
    for child in cage_obj.children:
        if child.get(REVEAL_CUTTER_FLAG):
            return child
    return None


def _reveal_side_consumed(opts, side, thickness):
    """(clearance_depth + splay_depth) actually used by one side's reveal
    (0.0 if that side is off), clamped to the wall thickness."""
    if not opts.get(f'reveal_{side}_on', False):
        return 0.0
    used = (max(0.0, opts.get(f'reveal_{side}_clearance_depth', 0.0))
            + max(0.0, opts.get(f'reveal_{side}_splay_depth', 0.0)))
    return min(used, thickness)


def reveal_frame_span(opts, thickness):
    """(fy0, fy1): the Y-range the frame/casing material may occupy -
    whatever's left of the wall thickness after each active reveal's own
    consumed depth (see _reveal_side_consumed). Both reveals off spans
    the full thickness (the old plain straight-through behavior)."""
    ext_used = _reveal_side_consumed(opts, 'ext', thickness)
    int_used = _reveal_side_consumed(opts, 'int', thickness)
    if ext_used + int_used > thickness:
        # Both sides claim more than the wall has - scale back
        # proportionally so they meet in the middle instead of crossing.
        scale = thickness / (ext_used + int_used)
        ext_used *= scale
        int_used *= scale
    return ext_used, thickness - int_used


def _build_reveal_cutter_mesh(mesh, width, height, thickness, opts):
    """Fill `mesh` with a cutter volume spanning the same local box as the
    cage (X: 0..width, Y: 0..thickness, Z: 0..height). Shaped from two
    INDEPENDENT reveals, one carved in from each wall face - see the
    reveal_ext_* / reveal_int_* comment on DOOR_DEFAULTS/WINDOW_DEFAULTS.

    Each active side is WIDEST right at its own wall face (the visible
    flare) and narrows inward: splay tapers from (clearance_amount +
    splay_amount) down to just clearance_amount over splay_depth, then a
    straight clearance run holds that width for clearance_depth, then an
    instant 90-degree step drops straight to 0 (the rough-opening width)
    right where the frame/casing begins - see reveal_frame_span, which
    this uses so the cutter and the frame always agree on that boundary
    (the frame is built at the plain rough-opening width, so the cutter
    must return to 0 there too, or the frame floats disconnected from
    the wall). Both reveals off reproduces the original plain
    straight-through cut."""
    import bmesh

    bm = bmesh.new()

    fy0, fy1 = reveal_frame_span(opts, thickness)

    def side_stations(on, ca, cd, sa, sd, face_y, sign, frame_edge):
        """Stations from `face_y` (direction `sign`, +1 for the y=0 face,
        -1 for y=thickness) in to `frame_edge`, the shared, already-
        clamped boundary with the frame (fy0 for ext, fy1 for int - see
        reveal_frame_span). Widest at the face, stepping down to 0 right
        at frame_edge."""
        span = abs(frame_edge - face_y)
        if not on or span < 1e-9:
            return [(face_y, 0.0), (frame_edge, 0.0)]
        ca = max(0.0, ca)
        sa = max(0.0, sa)
        # cd/sd are just a ratio here - reveal_frame_span already clamped
        # the total (cd+sd) to fit the wall, so rescale both to land
        # exactly on frame_edge rather than reclamping independently
        # (which could disagree with reveal_frame_span's own clamp when
        # both sides are active and over budget).
        raw_total = max(0.0, cd) + max(0.0, sd)
        if raw_total < 1e-9:
            sd_scaled, cd_scaled = span, 0.0
        else:
            scale = span / raw_total
            sd_scaled = max(0.0, sd) * scale
            cd_scaled = max(0.0, cd) * scale
        pts = [(face_y, ca + sa)]
        y = face_y
        if sd_scaled > 1e-6:
            y += sign * sd_scaled
            pts.append((y, ca))
        if cd_scaled > 1e-6:
            y += sign * cd_scaled
            pts.append((y, ca))
        pts.append((frame_edge, 0.0))
        return pts

    ext_pts = side_stations(
        opts.get('reveal_ext_on', False),
        opts.get('reveal_ext_clearance_amount', 0.0),
        opts.get('reveal_ext_clearance_depth', 0.0),
        opts.get('reveal_ext_splay_amount', 0.0),
        opts.get('reveal_ext_splay_depth', 0.0),
        0.0, 1, fy0)
    int_pts = side_stations(
        opts.get('reveal_int_on', False),
        opts.get('reveal_int_clearance_amount', 0.0),
        opts.get('reveal_int_clearance_depth', 0.0),
        opts.get('reveal_int_splay_amount', 0.0),
        opts.get('reveal_int_splay_depth', 0.0),
        thickness, -1, fy1)
    int_pts = list(reversed(int_pts))

    stations = list(ext_pts) + int_pts

    def ring(y, expand):
        x0, x1 = -expand, width + expand
        z0, z1 = -expand, height + expand
        return [bm.verts.new(co) for co in (
            (x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))]

    rings = [ring(*stations[0])]
    for y, expand in stations[1:]:
        py, pe = rings[-1][0].co.y, (rings[-1][1].co.x - rings[-1][0].co.x - width) / 2.0
        if abs(y - py) < 1e-6 and abs(expand - pe) < 1e-6:
            continue
        rings.append(ring(y, expand))

    for a, b in zip(rings, rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()


def update_reveal_cutter(cage_obj):
    """Create/refresh the boolean-cutter child used to cut the wall
    opening, shaped from the cage's current Dim X/Y/Z plus the
    reveal_ext_* / reveal_int_* options (falling back to the kind's
    defaults when no options are stored yet, e.g. right after placement).
    Returns the cutter object - callers pass this to cut_wall instead of
    the cage itself so the reveal doesn't have to be baked into the
    cage's own GeoNodes asset."""
    cage = hb_types.GeoNodeCage(cage_obj)
    if not cage.has_modifier():
        return cage_obj

    category = _category_for(cage_obj)
    opts = merged_opts(cage_obj) or (dict(_defaults_for(category)) if category else {})

    W = cage.get_input('Dim X')
    T = cage.get_input('Dim Y')
    H = cage.get_input('Dim Z')

    cutter = _reveal_cutter_child(cage_obj)
    if cutter is None:
        mesh = bpy.data.meshes.new(f"{cage_obj.name}_reveal_cutter")
        cutter = bpy.data.objects.new(f"{cage_obj.name}_reveal_cutter", mesh)
        cutter[REVEAL_CUTTER_FLAG] = True
        cutter.parent = cage_obj
        cutter.matrix_local = Matrix.Identity(4)
        cutter.hide_render = True
        cutter.hide_select = True
        cutter.display_type = 'WIRE'
        # Wherever the cage is linked, the same as any other child the
        # cage grows (see _new_child). The active collection is not it:
        # a rebuild can be run from anywhere - a prompts dialog, the
        # dimension overlay - and the cutter would land in whatever
        # collection happened to be active at the time, away from the
        # door it belongs to.
        colls = list(cage_obj.users_collection) or [
            bpy.context.scene.collection]
        for coll in colls:
            coll.objects.link(cutter)

    _build_reveal_cutter_mesh(cutter.data, W, H, T, opts)

    # Retrofit doors/windows placed before the reveal-cutter system
    # existed: their wall's boolean modifier still targets the cage
    # directly, so the reveal never actually cuts the wall even though
    # the cutter (visible as its wire outline) is shaped correctly.
    # Repoint any such modifier to the cutter instead.
    wall_obj = cage_obj.parent
    if wall_obj is not None:
        for mod in wall_obj.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == cage_obj:
                mod.object = cutter

    return cutter


def remove_reveal_cutter(cage_obj):
    """Take the cutter away and give the wall back to the cage.

    An opening with no stored options carries no reveal, and the cage
    cuts its own plain rectangle perfectly well. Keeping a cutter for it
    would only be a second mesh to hold in step: the cage resizes live
    with Dim X/Z, a cutter mesh is rebuilt when something remembers to
    rebuild it, and the hole stops matching the opening the moment one
    is resized without the other."""
    cutter = _reveal_cutter_child(cage_obj)
    if cutter is None:
        return
    wall_obj = cage_obj.parent
    if wall_obj is not None:
        for mod in wall_obj.modifiers:
            if mod.type == 'BOOLEAN' and mod.object == cutter:
                mod.object = cage_obj
    me = cutter.data
    bpy.data.objects.remove(cutter, do_unlink=True)
    if me is not None and me.users == 0:
        bpy.data.meshes.remove(me)


def _text_children(cage_obj):
    return [c for c in cage_obj.children if c.type == 'FONT']


def _ensure_annotation_text(cage_obj, want):
    """The cage's centered DOOR / WINDOW text label exists only while
    the opening is cage-only -- built 3D geometry says what it is. The
    recreation mirrors the placement operator's setup (dim-driven
    centering)."""
    texts = _text_children(cage_obj)
    if not want:
        for child in texts:
            data = child.data
            bpy.data.objects.remove(child, do_unlink=True)
            if data is not None and data.users == 0:
                bpy.data.curves.remove(data)
        return
    if texts:
        return
    # Open doorways are never labeled -- they're just an opening. The
    # name check covers doorways placed before the flag existed.
    if cage_obj.get('IS_OPEN_DOORWAY') \
            or cage_obj.name.startswith('Open Door'):
        return
    cage = hb_types.GeoNodeCage(cage_obj)
    if not cage.has_modifier():
        return
    props = bpy.context.scene.home_builder
    is_window = bool(cage_obj.get('IS_WINDOW_BP'))
    text = GeoNodeText()
    text.create("Window Text" if is_window else "Door Text",
                'WINDOW' if is_window else 'DOOR',
                props.annotation_text_size)
    text.obj.parent = cage_obj
    text.obj.rotation_euler.x = math.radians(90)
    dim_x = cage.var_input('Dim X', 'dim_x')
    dim_y = cage.var_input('Dim Y', 'dim_y')
    dim_z = cage.var_input('Dim Z', 'dim_z')
    text.driver_location("x", 'dim_x/2', [dim_x])
    text.driver_location("y", 'dim_y/2', [dim_y])
    text.driver_location("z", 'dim_z/2', [dim_z])
    text.set_alignment('CENTER', 'CENTER')


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
    """(is_double, hinge_left, swing_inside) read off the swing
    annotation; single / hinge-left / inswing when there is none (open
    doorways)."""
    child = _swing_child(cage_obj)
    if child is None:
        return False, True, True
    swing = hb_types.GeoNodeObject(child)
    try:
        return (bool(swing.get_input('Is Double')),
                bool(swing.get_input('Is Left')),
                bool(swing.get_input('Swing Inside')))
    except Exception:
        return False, True, True


def _leaf_open_transform(x, y_front, thickness, width, hinge,
                         swing_inside, open_deg):
    """Cage-local open-swing transform for a door leaf: a rotation
    about the hinge edge's vertical axis, identity when closed.
    Interior is -Y; an inswing leaf rotates toward it. Applied to the
    slab AND to everything mounted on it (knob, handle assets) so the
    hardware swings with the door."""
    a = math.radians(min(max(open_deg, 0.0), 135.0))
    if a <= 1e-4:
        return Matrix.Identity(4)
    hinge_x = x if hinge == 'L' else x + width
    pivot_y = y_front if swing_inside else y_front + thickness
    if swing_inside:
        delta = -a if hinge == 'L' else a
    else:
        delta = a if hinge == 'L' else -a
    pivot = Vector((hinge_x, pivot_y, 0.0))
    return (Matrix.Translation(pivot) @ Matrix.Rotation(delta, 4, 'Z')
            @ Matrix.Translation(-pivot))


def _slab_matrix(x, y_front, z, thickness, width, hinge, swing_inside,
                 open_deg):
    """Cage-local matrix for a door leaf: the standard door-mesh
    reorientation composed with the open-swing transform."""
    base = (Matrix.Translation((x, y_front + thickness, z))
            @ Euler((0.0, math.radians(-90.0),
                     math.radians(90.0))).to_matrix().to_4x4())
    return _leaf_open_transform(x, y_front, thickness, width, hinge,
                                swing_inside, open_deg) @ base


def _build_slab(cage_obj, name, opts, width, height, x, y_front,
                hinge='L', swing_inside=True, open_deg=0.0):
    info, kwargs, glass = _slab_spec(opts)
    min_w, min_h = door_builder.layout_min_size(info)
    if width <= min_w or height <= min_h:
        info = dict(info, door_type='SLAB')
        glass = 'NONE'
    door_mat = _door_material()
    panel_mat = _glass_material() if glass == 'ALL' else door_mat
    st = max(opts['slab_thickness'], inch(0.75))
    z0 = max(opts['threshold_height'], 0.0)
    obj = _door_mesh_child(
        cage_obj, name, info, kwargs, width, height, st,
        (door_mat, door_mat, panel_mat), x, y_front, z0)
    if glass == 'TOP':
        frac = _LITE_FRACTION[opts['door_style']]
        mrw = max(opts['lock_rail_width'], inch(0.5))
        _glassify_above(obj, (1.0 - frac) * height + mrw / 2.0 - 0.001)
    matrix = _slab_matrix(x, y_front, z0, st, width, hinge, swing_inside,
                          open_deg)
    obj.matrix_basis = matrix
    # Handle on the latch edge, one per face, carrying the leaf's
    # open-swing transform so it swings with the door.
    if opts['include_knob']:
        open_t = _leaf_open_transform(x, y_front, st, width, hinge,
                                      swing_inside, open_deg)
        _place_handles(cage_obj, name, opts, matrix, open_t, x, y_front,
                       width, st, z0, height, hinge)
    return obj


def _place_handles(cage_obj, name, opts, leaf_matrix, open_t, x, y_front,
                   width, thickness, z0, height, hinge):
    """Both faces' handles for one leaf: an installed handle asset
    (mesh linked from its .blend) when selected and resolvable, else
    the built-in lathed knob.

    Asset handles place in plain cage space at the latch mount point
    of each door face, rotated by the per-door handle_rot_front /
    handle_rot_back eulers (degrees) -- handle models are not all
    authored in one orientation, so the angles are options rather than
    constants. Both compose with the leaf's open-swing transform."""
    selection = str(opts.get('handle', 'DEFAULT'))
    src = (load_handle_object(selection)
           if selection not in ('', 'DEFAULT') else None)
    latch_x = (x + width - inch(2.5) if hinge == 'L' else x + inch(2.5))
    handle_z = z0 + min(inch(36.0), height * 0.45)
    if src is not None:
        def rot_euler(prefix):
            return Euler(
                (math.radians(float(opts['handle_rot_%s_x' % prefix])),
                 math.radians(float(opts['handle_rot_%s_y' % prefix])),
                 math.radians(float(opts['handle_rot_%s_z' % prefix]))),
                'XYZ')
        closed = open_t == Matrix.Identity(4)
        placements = (
            ("Front", (latch_x, y_front, handle_z), rot_euler('front')),
            ("Back", (latch_x, y_front + thickness, handle_z),
             rot_euler('back')),
        )
        for side, mount, euler in placements:
            obj = _new_child(cage_obj, "%s %s Handle" % (name, side),
                             mesh=src.data)
            obj.matrix_basis = (open_t @ Matrix.Translation(mount)
                                @ euler.to_matrix().to_4x4())
            if closed:
                # Same orientation, but shown with the user's literal
                # angles instead of a re-decomposed equivalent.
                obj.rotation_euler = euler
        return
    knob = _new_child(cage_obj, name + " Knob")
    verts, faces, slots = [], [], []
    latch_my = (-(width - inch(2.5)) if hinge == 'L' else -inch(2.5))
    handle_mx = min(inch(36.0), height * 0.45)
    profile = [(inch(r), inch(p)) for r, p in _KNOB_PROFILE]
    _lathe_z(verts, faces, slots, handle_mx, latch_my, thickness, profile)
    _lathe_z(verts, faces, slots, handle_mx, latch_my, 0.0, profile,
             flip=True)
    _finish_mesh(knob, verts, faces, slots, [_handle_material()])
    knob.matrix_basis = leaf_matrix


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

    # Past an active reveal (reveal_ext_on / reveal_int_on) the actual cut
    # opens wider than the door's own footprint on that side. Rather than
    # building the frame/casing against the wall's real thickness T, the
    # frame only spans whatever's left after each active reveal's own
    # consumed depth - see reveal_frame_span - so the door sits and trims
    # exactly like it would in a wall of that (possibly narrower, possibly
    # off-center) thickness, with the reveals left as bare cut beyond it.
    fy0, fy1 = reveal_frame_span(opts, T)
    T_eff = max(fy1 - fy0, inch(0.5))
    fy1 = fy0 + T_eff

    # The cage's Dim X / Dim Z are the OVERALL unit including casing:
    # the casing band sits inside the footprint and the opening
    # shrinks inward by it. Filler boxes (frame-depth only, see above)
    # close the wall cut behind the band (the cage still cuts its full
    # rectangle, splay included).
    any_casing = (opts['include_exterior_casing']
                  or opts['include_interior_casing'])
    band = min(cw, W / 4.0, H / 4.0) if any_casing else 0.0
    ox0, ox1, oz1 = band, W - band, H - band

    if band > 0.0:
        _box(verts, faces, slots, 0.0, band, fy0, fy1, 0.0, H)
        _box(verts, faces, slots, W - band, W, fy0, fy1, 0.0, H)
        _box(verts, faces, slots, band, W - band, fy0, fy1, oz1, H)

    # Jamb lining the opening, frame depth only (see above).
    _box(verts, faces, slots, ox0, ox0 + jw, fy0, fy1, 0.0, oz1)
    _box(verts, faces, slots, ox1 - jw, ox1, fy0, fy1, 0.0, oz1)
    _box(verts, faces, slots, ox0 + jw, ox1 - jw, fy0, fy1,
         oz1 - jw, oz1)
    if th_h > 0.0:
        _box(verts, faces, slots, ox0 + jw, ox1 - jw, fy0, fy1, 0.0, th_h)

    # Casing (sides + head, butt joints, no bottom) proud of each face
    # of the T_eff virtual wall (see above), within the reserved band.
    if band > 0.0:
        for on, y0, y1 in ((opts['include_exterior_casing'], fy1, fy1 + ct),
                           (opts['include_interior_casing'], fy0 - ct, fy0)):
            if not on:
                continue
            _box(verts, faces, slots, 0.0, band, y0, y1, 0.0, oz1)
            _box(verts, faces, slots, W - band, W, y0, y1, 0.0, oz1)
            _box(verts, faces, slots, 0.0, W, y0, y1, oz1, H)

    # Interior layout: sidelites and a transom subdivide the opening
    # with mull posts; the slab(s) take what remains.
    x0, x1 = ox0 + jw, ox1 - jw
    z_top = oz1 - jw
    # Sidelites / transom that don't fit the opening shrink to fit
    # (dropping entirely only below a usable minimum) rather than
    # silently vanishing -- the door zone keeps at least 18" / 24".
    transom_h = max(opts['transom_height'], 0.0)
    if transom_h > 0.0:
        transom_h = min(transom_h,
                        max(z_top - th_h - inch(24.0) - MULL_WIDTH, 0.0))
        if transom_h < inch(4.0):
            transom_h = 0.0
    sl_l = max(opts['sidelite_left'], 0.0)
    sl_r = max(opts['sidelite_right'], 0.0)
    if sl_l > 0.0 or sl_r > 0.0:
        mulls = MULL_WIDTH * ((sl_l > 0.0) + (sl_r > 0.0))
        avail = (x1 - x0) - inch(18.0) - mulls
        total = sl_l + sl_r
        if total > avail:
            scale = max(avail / total, 0.0) if total > 0.0 else 0.0
            sl_l *= scale
            sl_r *= scale
        if sl_l < inch(3.0):
            sl_l = 0.0
        if sl_r < inch(3.0):
            sl_r = 0.0

    # Centered within the frame band (near the flush face), not the full
    # wall thickness - keeps the slab sitting close to the flush face
    # instead of the middle of a splayed reveal.
    y_center_front = fy0 + max(0.0, (T_eff - st) / 2.0)

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
    is_double, hinge_left, swing_inside = _swing_state(cage_obj)
    open_deg = max(float(opts['open_angle']), 0.0)
    if is_double and slab_zone_w > inch(24):
        half = slab_zone_w / 2.0
        _build_slab(cage_obj, "Door Slab Left", opts, half, slab_h,
                    door_x0, y_center_front, hinge='L',
                    swing_inside=swing_inside, open_deg=open_deg)
        _build_slab(cage_obj, "Door Slab Right", opts, half, slab_h,
                    door_x0 + half, y_center_front, hinge='R',
                    swing_inside=swing_inside, open_deg=open_deg)
    else:
        _build_slab(cage_obj, "Door Slab", opts, slab_zone_w, slab_h,
                    door_x0, y_center_front,
                    hinge='L' if hinge_left else 'R',
                    swing_inside=swing_inside, open_deg=open_deg)

    frame = _new_child(cage_obj, "Door Frame")
    _finish_mesh(frame, verts, faces, slots, [trim_mat])
    _ensure_annotation_text(cage_obj, False)


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

    # Frame only spans whatever's left after each active reveal's own
    # consumed depth - see build_door_geometry's matching comment.
    fy0, fy1 = reveal_frame_span(opts, T)
    T_eff = max(fy1 - fy0, inch(0.5))
    fy1 = fy0 + T_eff

    # The cage's Dim X / Dim Z are the OVERALL unit including casing,
    # sill and stool: the trim sits inside the footprint and the frame
    # shrinks inward by the reserved bands. Filler boxes (T_eff deep
    # only, see above) close the wall cut behind the bands.
    any_casing = (opts['include_exterior_casing']
                  or opts['include_interior_casing'])
    sill_on = bool(opts['include_sill'])
    stool_on = bool(opts['include_stool'])
    sh = max(opts['sill_height'], inch(0.5)) if sill_on else 0.0
    side_b = min(cw, W / 4.0) if any_casing else 0.0
    top_b = min(cw, H / 4.0) if any_casing else 0.0
    bot_b = max(sh,
                min(cw, H / 4.0) if any_casing else 0.0,
                inch(1.0) if stool_on else 0.0)
    fx0, fx1 = side_b, W - side_b
    fz0, fz1 = bot_b, H - top_b

    if side_b > 0.0:
        _box(verts, faces, slots, 0.0, side_b, fy0, fy1, 0.0, H)
        _box(verts, faces, slots, W - side_b, W, fy0, fy1, 0.0, H)
    if top_b > 0.0:
        _box(verts, faces, slots, fx0, fx1, fy0, fy1, fz1, H)
    if bot_b > 0.0:
        _box(verts, faces, slots, fx0, fx1, fy0, fy1, 0.0, fz0)

    # Frame lining the opening, frame depth only (see above).
    _box(verts, faces, slots, fx0, fx0 + fw, fy0, fy1, fz0, fz1)
    _box(verts, faces, slots, fx1 - fw, fx1, fy0, fy1, fz0, fz1)
    _box(verts, faces, slots, fx0 + fw, fx1 - fw, fy0, fy1, fz0, fz0 + fw)
    _box(verts, faces, slots, fx0 + fw, fx1 - fw, fy0, fy1, fz1 - fw, fz1)

    ox0, ox1 = fx0 + fw, fx1 - fw
    oz0, oz1 = fz0 + fw, fz1 - fw
    ow, oh = ox1 - ox0, oz1 - oz0

    # Sash depth planes: exterior sashes sit behind the T_eff-wall
    # middle, interior sashes in front of it (front face toward the
    # room). Anchored to the T_eff virtual wall (near the flush face),
    # not the full wall thickness - see build_door_geometry's matching
    # comment.
    frame_mid = fy0 + T_eff / 2.0
    y_ext_front = frame_mid
    y_int_front = frame_mid - st
    y_center_front = fy0 + max(0.0, (T_eff - st) / 2.0)

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
    # stand-in for the sloped sill), full unit width. Proud of fy1 (the
    # reveal-adjusted exterior casing face), not the wall's true
    # thickness T, or it stays behind when a reveal shifts the casing.
    if sill_on:
        sp = max(opts['sill_projection'], 0.0)
        _box(verts, faces, slots, 0.0, W, fy1, fy1 + ct + sp,
             fz0 - sh, fz0)

    # Casing per face (sides + head + bottom leg, butt joints) within
    # the reserved bands; the exterior skips its bottom leg for the
    # sill, the interior for the stool.
    for on, y0, y1, skip_bottom in (
            (opts['include_exterior_casing'], fy1, fy1 + ct, sill_on),
            (opts['include_interior_casing'], fy0 - ct, fy0, stool_on)):
        if not on or side_b <= 0.0:
            continue
        z_side0 = fz0 if skip_bottom else max(fz0 - side_b, 0.0)
        _box(verts, faces, slots, 0.0, side_b, y0, y1, z_side0, fz1)
        _box(verts, faces, slots, W - side_b, W, y0, y1, z_side0, fz1)
        _box(verts, faces, slots, 0.0, W, y0, y1, fz1, H)
        if not skip_bottom:
            _box(verts, faces, slots, side_b, W - side_b, y0, y1,
                 max(fz0 - side_b, 0.0), fz0)

    # Interior stool: top flush with the frame bottom, projecting into
    # the room, with an apron strip below. Proud of fy0 (the reveal-
    # adjusted interior casing face), not y=0, or it stays behind when a
    # reveal shifts the casing.
    if stool_on:
        _box(verts, faces, slots, 0.0, W, fy0 - ct - inch(1.0), fy0,
             fz0 - inch(0.75), fz0)
        _box(verts, faces, slots, 0.0, W, fy0 - ct, fy0,
             max(fz0 - inch(0.75) - cw, 0.0), fz0 - inch(0.75))

    frame = _new_child(cage_obj, "Window Frame")
    _finish_mesh(frame, verts, faces, slots, [trim_mat])
    _ensure_annotation_text(cage_obj, False)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def build_geometry(cage_obj):
    """Rebuild the cage's generated geometry from its stored options.
    No stored options -> any stale children are removed and nothing is
    built (cage-only display)."""
    # Cage-only display goes back to cutting with the cage, so a plain
    # opening keeps resizing its hole live the way it always did.
    if stored_opts(cage_obj) is None:
        remove_reveal_cutter(cage_obj)
    else:
        update_reveal_cutter(cage_obj)
    if cage_obj.get('IS_WINDOW_BP'):
        build_window_geometry(cage_obj)
    elif cage_obj.get('IS_ENTRY_DOOR_BP'):
        build_door_geometry(cage_obj)


# ---------------------------------------------------------------------------
# Handle pack install / open operators
# ---------------------------------------------------------------------------

class HOME_BUILDER_OT_install_door_handle_pack(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.install_handle_pack"
    bl_label = "Install Door Handle Pack"
    bl_description = ("Install a zip of door handle .blend models into "
                      "the user handle folder")
    bl_options = {'REGISTER'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')  # type: ignore
    filter_glob: bpy.props.StringProperty(default='*.zip',
                                          options={'HIDDEN'})  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath or not os.path.isfile(self.filepath):
            self.report({'ERROR'}, "Select a handle pack zip file")
            return {'CANCELLED'}
        root = get_user_handles_root(create=True)
        installed = 0
        try:
            with zipfile.ZipFile(self.filepath) as zf:
                for member in zf.namelist():
                    if member.endswith('/'):
                        continue
                    lower = member.lower()
                    if not lower.endswith(('.blend', '.png')):
                        continue
                    # Only the basename is used, so a hostile zip path
                    # cannot escape the handle folder.
                    fname = os.path.basename(member.replace('\\', '/'))
                    if not fname:
                        continue
                    with open(os.path.join(root, fname), 'wb') as f:
                        f.write(zf.read(member))
                    if lower.endswith('.blend'):
                        installed += 1
        except zipfile.BadZipFile:
            self.report({'ERROR'}, "Not a valid zip file")
            return {'CANCELLED'}
        if installed == 0:
            self.report({'WARNING'}, "No handle .blend files in the zip")
            return {'CANCELLED'}
        # Stale cached source objects would shadow reinstalled files.
        _handle_cache.clear()
        self.report({'INFO'}, "Installed %d handle model%s" %
                    (installed, "" if installed == 1 else "s"))
        return {'FINISHED'}


class HOME_BUILDER_OT_open_door_handle_folder(bpy.types.Operator):
    bl_idname = "home_builder_doors_windows.open_handle_folder"
    bl_label = "Open Handle Folder"
    bl_description = ("Open the user door handle folder in the file "
                      "browser")

    def execute(self, context):
        path = get_user_handles_root(create=True)
        try:
            os.startfile(path)
        except AttributeError:
            import subprocess
            subprocess.Popen(['xdg-open', path])
        return {'FINISHED'}


classes = (
    HOME_BUILDER_OT_install_door_handle_pack,
    HOME_BUILDER_OT_open_door_handle_folder,
)


register, unregister = bpy.utils.register_classes_factory(classes)
