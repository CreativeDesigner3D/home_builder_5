"""Parametric models for the Curate drawer system (TAG / Hafele).

The system is a metal frame plus an insert: a TRAY frame carries the
shallow faux-leather organizers (jewelry, sunglasses, tie & belt), a
SUSPEND frame carries the deep hanging inserts (baskets, hampers, the
pants organizer), and a SHELF frame carries the shoe organizer and
storage boxes. Frames come 18/24/30/36 inches wide by 14/20 deep, in
five metal finishes; the soft inserts come in three leathers and a
basket fabric.

Everything here is built to real catalog sizes where the maker
publishes them (widths, depths, finishes, the insert lineup). Heights
and rail profiles are NOT published on the public pages - they are the
named constants right below, set to measured-off-photo estimates, and
meant to be trued up from the printed product manual before the models
are considered final.

Usage inside Blender:
    from curate_models import build, build_all, CURATE_MODELS
    obj = build('TRAY_FRAME', width_in=24, depth_in=14,
                finish='Matte Nickel')
    build_all()          # one of everything, laid out in a grid
Each builder returns the model's root object; every mesh hangs under
it, so the root is what a library or an export step takes hold of.
"""

import math

import bpy


# ---------------------------------------------------------------------------
# Catalog facts (published)
# ---------------------------------------------------------------------------
INCH = 0.0254

WIDTHS_IN = (18, 24, 30, 36)
DEPTHS_IN = (14, 20)

METAL_FINISHES = {
    'Black': (0.02, 0.02, 0.02),
    'Matte Aluminum': (0.55, 0.56, 0.58),
    'Matte Gold': (0.60, 0.45, 0.18),
    'Matte Nickel': (0.44, 0.44, 0.42),
    'Slate': (0.13, 0.14, 0.16),
}
LEATHER_TONES = {
    'Oyster': (0.62, 0.57, 0.50),
    'Pewter': (0.35, 0.34, 0.33),
    'Winter': (0.78, 0.78, 0.76),
}
FABRIC_GREY = (0.42, 0.42, 0.43)

# ---------------------------------------------------------------------------
# Working sizes (NOT published - true these up from the product manual)
# ---------------------------------------------------------------------------
RAIL = 0.75 * INCH            # square section of the frame rails
TRAY_FRAME_H = 2.5 * INCH     # tray frame overall height
SUSPEND_FRAME_H = 1.5 * INCH  # suspend frame rail band height
TRAY_H = 2.0 * INCH           # faux-leather tray insert height
TRAY_WALL = 0.375 * INCH      # tray wall / divider thickness
BASKET_H = {'S': 6.0 * INCH, 'M': 8.0 * INCH, 'L': 10.0 * INCH}
HAMPER_H = 12.0 * INCH        # laundry liner depth below the frame
SHOE_H = 4.0 * INCH           # shoe organizer section height
BOX_H = 4.0 * INCH            # storage box height
PANT_BAR_DROP = 10.0 * INCH   # pants organizer hanger drop
FRONT_PLATE_T = 0.25 * INCH   # metal front plate thickness
FRONT_PLATE_H = 5.0 * INCH    # metal front plate height
INSET = 0.25 * INCH           # insert clearance inside the frame


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _material(name, color, metallic=0.0, rough=0.6):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = rough
    return mat


def metal_material(finish):
    color = METAL_FINISHES.get(finish, METAL_FINISHES['Matte Nickel'])
    return _material(f'Curate {finish}', color, metallic=1.0, rough=0.45)


def leather_material(tone):
    color = LEATHER_TONES.get(tone, LEATHER_TONES['Pewter'])
    return _material(f'Curate Leather {tone}', color, rough=0.8)


def fabric_material():
    return _material('Curate Fabric', FABRIC_GREY, rough=0.95)


def _root(name):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _box(name, parent, size, loc, mat):
    """One rectangular mesh under the root: size (x, y, z), loc = the
    box's minimum corner, so a model reads like a cut list."""
    mesh = bpy.data.meshes.new(name)
    sx, sy, sz = size
    x, y, z = loc
    verts = [(x + dx * sx, y + dy * sy, z + dz * sz)
             for dz in (0, 1) for dy in (0, 1) for dx in (0, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    return obj


def _rail_ring(parent, w, d, z, h, mat, name='Rail'):
    """Four rails in a rectangle: the band every frame is built from."""
    _box(name + ' F', parent, (w, RAIL, h), (0, -RAIL, z), mat)
    _box(name + ' B', parent, (w, RAIL, h), (0, -d, z), mat)
    _box(name + ' L', parent, (RAIL, d - 2 * RAIL, h),
         (0, -d + RAIL, z), mat)
    _box(name + ' R', parent, (RAIL, d - 2 * RAIL, h),
         (w - RAIL, -d + RAIL, z), mat)


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------
def build_tray_frame(width_in=24, depth_in=14, finish='Matte Nickel'):
    """The metal foundation the shallow tray organizers sit in: a rail
    band with runners across the bottom for the tray to rest on."""
    w, d = width_in * INCH, depth_in * INCH
    mat = metal_material(finish)
    root = _root(f'Curate Tray Frame {width_in}x{depth_in}')
    _rail_ring(root, w, d, 0.0, TRAY_FRAME_H, mat)
    runners = max(2, int(width_in / 9))
    for i in range(runners):
        x = RAIL + (w - 2 * RAIL - RAIL) * (i / max(runners - 1, 1))
        _box(f'Runner {i + 1}', root, (RAIL, d - 2 * RAIL, RAIL / 2),
             (x, -d + RAIL, 0.0), mat)
    return root


def build_suspend_frame(width_in=24, depth_in=14, finish='Matte Nickel'):
    """The metal base for the hanging configurations: a top rail band
    the soft inserts hang through, nothing below it."""
    w, d = width_in * INCH, depth_in * INCH
    mat = metal_material(finish)
    root = _root(f'Curate Suspend Frame {width_in}x{depth_in}')
    _rail_ring(root, w, d, 0.0, SUSPEND_FRAME_H, mat)
    # Two cross rails the insert sleeves wrap over.
    for i, frac in enumerate((1.0 / 3.0, 2.0 / 3.0)):
        _box(f'Cross Rail {i + 1}', root,
             (w - 2 * RAIL, RAIL / 2, RAIL / 2),
             (RAIL, -RAIL - (d - 2 * RAIL) * frac,
              SUSPEND_FRAME_H - RAIL / 2), mat)
    return root


def build_shelf_frame(width_in=24, depth_in=14, finish='Matte Nickel'):
    """The flat variant: a rail band with a full slat bed, for the shoe
    organizer and the storage boxes to stand on."""
    w, d = width_in * INCH, depth_in * INCH
    mat = metal_material(finish)
    root = _root(f'Curate Shelf Frame {width_in}x{depth_in}')
    _rail_ring(root, w, d, 0.0, SUSPEND_FRAME_H, mat)
    slats = max(5, int(width_in / 3))
    pitch = (w - 2 * RAIL) / slats
    for i in range(slats):
        _box(f'Slat {i + 1}', root,
             (pitch * 0.55, d - 2 * RAIL, RAIL / 2),
             (RAIL + pitch * i, -d + RAIL, 0.0), mat)
    return root


# ---------------------------------------------------------------------------
# Tray inserts (faux leather, sit in a TRAY frame)
# ---------------------------------------------------------------------------
def _tray_shell(root, w, d, tone):
    mat = leather_material(tone)
    x0, y0 = INSET, -d + INSET
    tw, td = w - 2 * INSET, d - 2 * INSET
    _box('Tray Bottom', root, (tw, td, TRAY_WALL / 2), (x0, y0, 0.0), mat)
    _box('Tray F', root, (tw, TRAY_WALL, TRAY_H),
         (x0, y0 + td - TRAY_WALL, 0.0), mat)
    _box('Tray B', root, (tw, TRAY_WALL, TRAY_H), (x0, y0, 0.0), mat)
    _box('Tray L', root, (TRAY_WALL, td - 2 * TRAY_WALL, TRAY_H),
         (x0, y0 + TRAY_WALL, 0.0), mat)
    _box('Tray R', root, (TRAY_WALL, td - 2 * TRAY_WALL, TRAY_H),
         (x0 + tw - TRAY_WALL, y0 + TRAY_WALL, 0.0), mat)
    return mat, x0, y0, tw, td


def _tray_grid(root, mat, x0, y0, tw, td, cols, rows, name):
    """Adjustable compartments drawn at their out-of-the-box layout."""
    for c in range(1, cols):
        _box(f'{name} Div V{c}', root,
             (TRAY_WALL / 2, td - 2 * TRAY_WALL, TRAY_H * 0.85),
             (x0 + tw * c / cols, y0 + TRAY_WALL, 0.0), mat)
    for r in range(1, rows):
        _box(f'{name} Div H{r}', root,
             (tw - 2 * TRAY_WALL, TRAY_WALL / 2, TRAY_H * 0.85),
             (x0 + TRAY_WALL, y0 + td * r / rows, 0.0), mat)


def build_jewelry_insert(width_in=24, depth_in=14, tone='Pewter'):
    w, d = width_in * INCH, depth_in * INCH
    root = _root(f'Curate Jewelry Insert {width_in}x{depth_in}')
    mat, x0, y0, tw, td = _tray_shell(root, w, d, tone)
    _tray_grid(root, mat, x0, y0, tw, td,
               cols=max(3, width_in // 6), rows=3, name='Jewelry')
    return root


def build_sunglasses_insert(width_in=24, depth_in=14, tone='Pewter'):
    """Long narrow bays, one pair per bay, tilted rest omitted."""
    w, d = width_in * INCH, depth_in * INCH
    root = _root(f'Curate Sunglasses Insert {width_in}x{depth_in}')
    mat, x0, y0, tw, td = _tray_shell(root, w, d, tone)
    _tray_grid(root, mat, x0, y0, tw, td,
               cols=max(4, width_in // 3), rows=1, name='Sunglasses')
    return root


def build_tie_belt_insert(width_in=24, depth_in=14, tone='Pewter'):
    w, d = width_in * INCH, depth_in * INCH
    root = _root(f'Curate Tie & Belt Insert {width_in}x{depth_in}')
    mat, x0, y0, tw, td = _tray_shell(root, w, d, tone)
    _tray_grid(root, mat, x0, y0, tw, td,
               cols=max(4, width_in // 4), rows=2, name='TieBelt')
    return root


# ---------------------------------------------------------------------------
# Hanging inserts (sit in a SUSPEND frame)
# ---------------------------------------------------------------------------
def _soft_bin(root, name, x0, w, d, h, mat):
    """One fabric bin hanging below the frame plane: four walls and a
    bottom, wall thickness a fabric's."""
    t = 0.25 * INCH
    y0 = -d + INSET
    bd = d - 2 * INSET
    _box(f'{name} F', root, (w, t, h), (x0, y0 + bd - t, -h), mat)
    _box(f'{name} B', root, (w, t, h), (x0, y0, -h), mat)
    _box(f'{name} L', root, (t, bd - 2 * t, h), (x0, y0 + t, -h), mat)
    _box(f'{name} R', root, (t, bd - 2 * t, h),
         (x0 + w - t, y0 + t, -h), mat)
    _box(f'{name} Bottom', root, (w, bd, t), (x0, y0, -h), mat)


def build_basket_insert(width_in=24, depth_in=14, size='M',
                        dividers=1):
    """The divided fabric basket: one soft bin the width of the frame,
    its adjustable dividers drawn at even spacing."""
    w, d = width_in * INCH, depth_in * INCH
    h = BASKET_H.get(size, BASKET_H['M'])
    mat = fabric_material()
    root = _root(f'Curate Basket {size} {width_in}x{depth_in}')
    _soft_bin(root, 'Basket', INSET, w - 2 * INSET, d, h, mat)
    for i in range(1, dividers + 1):
        _box(f'Basket Div {i}', root,
             (0.25 * INCH, d - 2 * INSET - 0.5 * INCH, h * 0.9),
             (INSET + (w - 2 * INSET) * i / (dividers + 1),
              -d + INSET + 0.25 * INCH, -h * 0.95), mat)
    return root


def build_laundry_insert(width_in=24, depth_in=14):
    """The laundry organizer: removable hamper liners, one on the
    narrow frames and two side by side on the wide ones."""
    w, d = width_in * INCH, depth_in * INCH
    mat = fabric_material()
    root = _root(f'Curate Laundry Insert {width_in}x{depth_in}')
    liners = 1 if width_in <= 24 else 2
    gap = 0.5 * INCH
    lw = (w - 2 * INSET - (liners - 1) * gap) / liners
    for i in range(liners):
        _soft_bin(root, f'Hamper {i + 1}',
                  INSET + i * (lw + gap), lw, d, HAMPER_H, mat)
    return root


def build_pants_insert(width_in=24, depth_in=14, finish='Matte Nickel'):
    """The pant & skirt organizer: a row of removable hanger bars
    running front to back below the frame."""
    w, d = width_in * INCH, depth_in * INCH
    mat = metal_material(finish)
    root = _root(f'Curate Pants Insert {width_in}x{depth_in}')
    bars = max(6, int(width_in / 2))
    pitch = (w - 2 * INSET) / bars
    bar = 0.375 * INCH
    for i in range(bars):
        x = INSET + pitch * (i + 0.5) - bar / 2
        _box(f'Hanger Bar {i + 1}', root,
             (bar, d - 2 * INSET, bar),
             (x, -d + INSET, -bar), mat)
    # PANT_BAR_DROP is the hanging clearance a run of pants wants
    # below the bars - the layout reserves it; nothing is drawn.
    return root


# ---------------------------------------------------------------------------
# Shelf-frame inserts
# ---------------------------------------------------------------------------
def build_shoe_insert(width_in=24, depth_in=14):
    """The shoe organizer: ventilated sections standing on the shelf
    frame, one pair per section."""
    w, d = width_in * INCH, depth_in * INCH
    mat = fabric_material()
    root = _root(f'Curate Shoe Insert {width_in}x{depth_in}')
    sections = max(2, width_in // 8)
    pitch = (w - 2 * INSET) / sections
    t = 0.25 * INCH
    _box('Shoe Back', root, (w - 2 * INSET, t, SHOE_H),
         (INSET, -INSET - t, 0.0), mat)
    for i in range(sections + 1):
        _box(f'Shoe Div {i + 1}', root, (t, d - 2 * INSET, SHOE_H),
             (INSET + pitch * i - (t if i else 0), -d + INSET, 0.0),
             mat)
    return root


def build_storage_box(width_in=24, depth_in=14, tone='Pewter'):
    """A compact lidded box; drawn one to a frame at half width, the
    way the catalog shows them paired."""
    w, d = width_in * INCH / 2.0, depth_in * INCH
    root = _root(f'Curate Storage Box {width_in}x{depth_in}')
    mat = leather_material(tone)
    t = 0.25 * INCH
    _box('Box Body', root, (w - 2 * INSET, d - 2 * INSET, BOX_H),
         (INSET, -d + INSET, 0.0), mat)
    _box('Box Lid', root,
         (w - 2 * INSET + t, d - 2 * INSET + t, t),
         (INSET - t / 2, -d + INSET - t / 2, BOX_H), mat)
    return root


# ---------------------------------------------------------------------------
# Fronts
# ---------------------------------------------------------------------------
def build_front_plate(width_in=24, finish='Matte Nickel'):
    """The metal front plate option: an architectural face the frame
    carries when it is not taking a full wood front."""
    w = width_in * INCH
    mat = metal_material(finish)
    root = _root(f'Curate Front Plate {width_in}')
    _box('Front Plate', root, (w, FRONT_PLATE_T, FRONT_PLATE_H),
         (0.0, 0.0, -(FRONT_PLATE_H - TRAY_FRAME_H) / 2.0), mat)
    return root


# ---------------------------------------------------------------------------
# Catalog of builders
# ---------------------------------------------------------------------------
CURATE_MODELS = {
    'TRAY_FRAME': build_tray_frame,
    'SUSPEND_FRAME': build_suspend_frame,
    'SHELF_FRAME': build_shelf_frame,
    'JEWELRY_INSERT': build_jewelry_insert,
    'SUNGLASSES_INSERT': build_sunglasses_insert,
    'TIE_BELT_INSERT': build_tie_belt_insert,
    'BASKET_INSERT': build_basket_insert,
    'LAUNDRY_INSERT': build_laundry_insert,
    'PANTS_INSERT': build_pants_insert,
    'SHOE_INSERT': build_shoe_insert,
    'STORAGE_BOX': build_storage_box,
    'FRONT_PLATE': build_front_plate,
}


def build(key, **kwargs):
    """One model by key; kwargs pass through to its builder."""
    return CURATE_MODELS[key](**kwargs)


def build_all(width_in=24, depth_in=14, spacing_in=8):
    """One of everything at one size, laid out in a row for review."""
    roots = []
    x = 0.0
    for key, fn in CURATE_MODELS.items():
        try:
            root = (fn(width_in=width_in)
                    if key == 'FRONT_PLATE'
                    else fn(width_in=width_in, depth_in=depth_in))
        except TypeError:
            root = fn(width_in=width_in, depth_in=depth_in)
        root.location.x = x
        x += (width_in + spacing_in) * INCH
        roots.append(root)
    return roots


def save_asset(key, filepath, **kwargs):
    """Build one model and write it (root + meshes) to its own blend
    file, the shape the accessory loader expects an asset in."""
    root = build(key, **kwargs)
    objs = {root}
    objs.update(root.children_recursive)
    bpy.data.libraries.write(filepath, objs, fake_user=True)
    return filepath
