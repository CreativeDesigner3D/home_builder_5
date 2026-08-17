"""Appliance panels: the per-section model behind panel-ready appliances.

A panelled appliance (dishwasher, refrigerator, beverage centre, ...) is a
stack of panel SECTIONS per column -- door faces, drawer faces, a grille --
each with its own face size, its own optional backer, and its own place in
the run. Manufacturer panel guides are written exactly this way (one row per
opening: face W x H, backer W x H, thickness, weight cap), so the model
holds those numbers directly: a spec fills the section fields as HELD
values, and everything left auto shares the leftover the way the old
calculator did.

Data (``Object.appliance_panels`` on the appliance root):

    Appliance_Panel_Props
        config / panel_type          preset key; default backer type A / B / C
        toe_kick                     the run starts above it (under-counter)
        end_reveal / section_gap     margins to the run ends / between sections
        backer_reveal                auto backer = face + 2 x this, each way
        rail_width, rail_top / rail_bottom / rail_between   integral rails
        install_type, manufacturer, model, spec_url, weight_max_lb   record
        columns[]                    width, width_hold
        sections[]                   bottom-to-top; see Appliance_Panel_Section

    Appliance_Panel_Section
        label, kind (DOOR / DRAWER / PANEL), column (-1 = spans all columns)
        height (+hold), z_bottom (+hold)      vertical place in the run
        face_thickness
        backer (DEFAULT / NONE / B / C), backer_width (+hold), backer_height (+hold)
        spec_note

Solve (``solve``): column widths share the appliance width between end
reveals and gaps; spanning sections listed before the first column section
are BOTTOM banners, after the last are TOP banners; banners and a "column
region" share the vertical run, then each column stacks its sections in
the region -- held heights keep, held bottoms pin (splitting the stack into
segments that share independently), the rest share. Integral rails ride
the column stacks like face-frame rails. Backers centre on their face.

Build (``rebuild``): fronts / backers / rails are parts under the appliance
root, reused in place by index when the structure is unchanged (live edits
resize instead of flickering); a structural change tears down and rebuilds.
Every property update calls rebuild.
"""

import json
import math

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
                       FloatProperty, IntProperty, PointerProperty,
                       StringProperty)
from bpy.types import PropertyGroup

from ... import hb_types
from ...units import inch
from . import types_face_frame

_I = inch

# Under-counter appliances: the panel run starts above the toe kick, like the
# neighbouring base cabinets' frames.
KICK_APPLIANCE_TYPES = {'DISHWASHER', 'UNDER_COUNTER'}

FACE_THICKNESS = _I(0.75)
BACKER_THICKNESS = {'B': _I(0.25), 'C': _I(0.35)}
# Type C installation-flange rout (representative; tune in Blender): a recess
# around the back-face perimeter where the appliance mounting flange seats.
FLANGE_INSET = _I(1.5)
FLANGE_DEPTH = _I(0.2)
# Full-inset integral rails: face-frame members fastened across the panel run
# (top / bottom) and between stacked sections. 3/4" stock, face flush with
# the inset panel faces; a panel meeting a rail keeps the inset reveal.
RAIL_THICKNESS = _I(0.75)
RAIL_REVEAL = _I(0.125)
# Gap between panels when a manufacturer guide sizes them (the guides'
# faces span the appliance with this between them).
SPEC_PANEL_GAP = _I(0.25)

TAG_FRONT = 'IS_APPLIANCE_PANEL_FRONT'
TAG_BACKER = 'IS_APPLIANCE_PANEL_BACKER'
TAG_RAIL = 'IS_APPLIANCE_PANEL_RAIL'

_SUSPEND = [0]      # > 0 while seeding: property updates don't rebuild


# ----------------------------------------------------------------------
# Presets (seed the section list; the user / spec edits from there)
# ----------------------------------------------------------------------
# config -> columns of (label, kind, default_height, hold) bottom-to-top,
# plus optional full-width banners (bottom / top).
PRESETS = {
    'SINGLE': dict(cols=[[("Door", 'DOOR', 0.0, False)]]),
    'FRENCH_DOOR': dict(cols=[[("Left Door", 'DOOR', 0.0, False)],
                              [("Right Door", 'DOOR', 0.0, False)]]),
    'FRENCH_DOOR_BOTTOM_FREEZER': dict(
        cols=[[("Left Door", 'DOOR', 0.0, False)],
              [("Right Door", 'DOOR', 0.0, False)]],
        bottom=[("Freezer Drawer", 'DRAWER', _I(16), True)]),
    'BOTTOM_FREEZER': dict(cols=[[("Freezer Drawer", 'DRAWER', _I(24), True),
                                  ("Door", 'DOOR', 0.0, False)]]),
    'BOTTOM_FREEZER_2DRAWER': dict(cols=[[("Lower Drawer", 'DRAWER', _I(12), True),
                                          ("Upper Drawer", 'DRAWER', _I(12), True),
                                          ("Door", 'DOOR', 0.0, False)]]),
    'TOP_FREEZER': dict(cols=[[("Door", 'DOOR', 0.0, False),
                               ("Freezer", 'DOOR', _I(16), True)]]),
    'DRAWER_DOOR_DRAWER': dict(cols=[[("Bottom Drawer", 'DRAWER', _I(8), True),
                                      ("Door", 'DOOR', 0.0, False),
                                      ("Top Drawer", 'DRAWER', _I(8), True)]]),
    'SIDE_BY_SIDE_SPLIT': dict(cols=[[("Left Door", 'DOOR', 0.0, False),
                                      ("Left Top Drawer", 'DRAWER', _I(8), True)],
                                     [("Right Door", 'DOOR', 0.0, False)]]),
    'DW_DRAWER_DOOR': dict(cols=[[("Door", 'DOOR', 0.0, False),
                                  ("Drawer", 'DRAWER', _I(6), True)]]),
    'DW_3_DRAWER': dict(cols=[[("Bottom Drawer", 'DRAWER', 0.0, False),
                               ("Middle Drawer", 'DRAWER', 0.0, False),
                               ("Top Drawer", 'DRAWER', 0.0, False)]]),
    'DW_4_DRAWER': dict(cols=[[("Drawer 1", 'DRAWER', 0.0, False),
                               ("Drawer 2", 'DRAWER', 0.0, False),
                               ("Drawer 3", 'DRAWER', 0.0, False),
                               ("Drawer 4", 'DRAWER', 0.0, False)]]),
}

CONFIG_ITEMS = {
    'REFRIGERATOR': [
        ('FRENCH_DOOR', "French Door (Side-by-Side)", "Two tall side-by-side panels"),
        ('FRENCH_DOOR_BOTTOM_FREEZER', "French Door + Bottom Freezer",
         "Two french doors over a full-width freezer drawer"),
        ('SINGLE', "Single Door", "One full-height panel"),
        ('BOTTOM_FREEZER', "Bottom Freezer (1 Drawer)", "Door over a single freezer drawer"),
        ('BOTTOM_FREEZER_2DRAWER', "Bottom Freezer (2 Drawer)", "Door over two freezer drawers"),
        ('TOP_FREEZER', "Top Freezer", "Freezer face over a fridge door"),
        ('DRAWER_DOOR_DRAWER', "Drawer / Door / Drawer", "Drawer face, tall door, drawer face"),
        ('SIDE_BY_SIDE_SPLIT', "Side-by-Side, Split Left", "Tall right door, drawer over door on the left"),
    ],
    'DISHWASHER': [
        ('SINGLE', "Standard (Single)", "One full-height panel"),
        ('DW_DRAWER_DOOR', "Drawer / Door", "Drawer face over a door"),
        ('DW_3_DRAWER', "3-Drawer", "Three equal drawer faces"),
        ('DW_4_DRAWER', "4-Drawer", "Four equal drawer faces"),
    ],
}
DEFAULT_CONFIG_ITEMS = [('SINGLE', "Single", "One full-height panel")]

PANEL_TYPE_ITEMS = [
    ('A', "Type A", "Face only, no backer"),
    ('B', "Type B", "Face applied to a 1/4\" backer"),
    ('C', "Type C", "Face on a .35\" backer routed for an install flange"),
]
SECTION_KIND_ITEMS = [
    ('DOOR', "Door", "Door face"),
    ('DRAWER', "Drawer", "Drawer face"),
    ('PANEL', "Panel", "Fixed panel (grille, filler)"),
]
SECTION_BACKER_ITEMS = [
    ('DEFAULT', "Default", "Follow the appliance's panel type"),
    ('NONE', "None", "Face only"),
    ('B', "Type B", "1/4\" backer"),
    ('C', "Type C", ".35\" backer routed for the install flange"),
]
INSTALL_TYPE_ITEMS = [
    ('OVERLAY', "Overlay", "Panels overlay the appliance frame"),
    ('FLUSH_INSET', "Flush Inset", "Panels flush with the surrounding cabinetry"),
]


# ----------------------------------------------------------------------
# Property groups
# ----------------------------------------------------------------------
def _on_change(self, context):
    if _SUSPEND[0]:
        return
    obj = self.id_data
    if isinstance(obj, bpy.types.Object) and obj.get('IS_APPLIANCE'):
        rebuild(obj)


class Appliance_Panel_Column(PropertyGroup):
    width: FloatProperty(name="Width", unit='LENGTH', default=_I(18), min=_I(1),
                         update=_on_change)  # type: ignore
    width_hold: BoolProperty(name="Hold", default=False, update=_on_change)  # type: ignore


class Appliance_Panel_Section(PropertyGroup):
    label: StringProperty(name="Label", default="Door")  # type: ignore
    kind: EnumProperty(name="Kind", items=SECTION_KIND_ITEMS, default='DOOR',
                       update=_on_change)  # type: ignore
    column: IntProperty(name="Column", default=0, min=-1, max=3,
                        description="Column index; -1 spans every column "
                                    "(a full-width banner)",
                        update=_on_change)  # type: ignore
    height: FloatProperty(name="Height", unit='LENGTH', default=_I(8), min=_I(0.5),
                          update=_on_change)  # type: ignore
    height_hold: BoolProperty(name="Hold", default=False, update=_on_change)  # type: ignore
    z_bottom: FloatProperty(name="Bottom", unit='LENGTH', default=0.0, min=0.0,
                            description="Bottom of this section above the floor",
                            update=_on_change)  # type: ignore
    z_hold: BoolProperty(name="Hold", default=False, update=_on_change)  # type: ignore
    face_thickness: FloatProperty(name="Thickness", unit='LENGTH', default=FACE_THICKNESS,
                                  min=_I(0.25), update=_on_change)  # type: ignore
    backer: EnumProperty(name="Backer", items=SECTION_BACKER_ITEMS, default='DEFAULT',
                         update=_on_change)  # type: ignore
    backer_width: FloatProperty(name="Backer W", unit='LENGTH', default=_I(24), min=_I(1),
                                update=_on_change)  # type: ignore
    backer_width_hold: BoolProperty(name="Hold", default=False, update=_on_change)  # type: ignore
    backer_height: FloatProperty(name="Backer H", unit='LENGTH', default=_I(24), min=_I(1),
                                 update=_on_change)  # type: ignore
    backer_height_hold: BoolProperty(name="Hold", default=False, update=_on_change)  # type: ignore
    spec_note: StringProperty(name="Note", default="")  # type: ignore


class Appliance_Panel_Props(PropertyGroup):
    config: StringProperty(name="Configuration", default="")  # type: ignore
    panel_type: EnumProperty(name="Panel Type", items=PANEL_TYPE_ITEMS, default='A',
                             update=_on_change)  # type: ignore
    toe_kick: FloatProperty(name="Toe Kick", unit='LENGTH', default=0.0, min=0.0,
                            update=_on_change)  # type: ignore
    end_reveal: FloatProperty(name="End Reveal", unit='LENGTH', default=_I(1.0), min=0.0,
                              description="Margin from the run's ends to the first / last panel",
                              update=_on_change)  # type: ignore
    section_gap: FloatProperty(name="Gap", unit='LENGTH', default=_I(1.0), min=0.0,
                               description="Gap between adjacent panels",
                               update=_on_change)  # type: ignore
    backer_reveal: FloatProperty(name="Backer Reveal", unit='LENGTH', default=_I(1.0),
                                 min=-_I(2.0),
                                 description="An auto backer is the face plus this each "
                                             "side (negative = smaller than the face)",
                                 update=_on_change)  # type: ignore
    install_type: EnumProperty(name="Install", items=INSTALL_TYPE_ITEMS, default='OVERLAY')  # type: ignore
    rail_width: FloatProperty(name="Rail Width", unit='LENGTH', default=_I(1.5), min=_I(0.5),
                              update=_on_change)  # type: ignore
    rail_top: BoolProperty(name="Top", default=False, update=_on_change)  # type: ignore
    rail_bottom: BoolProperty(name="Bottom", default=False, update=_on_change)  # type: ignore
    rail_between: BoolProperty(name="Between", default=False, update=_on_change)  # type: ignore
    weight_max_lb: FloatProperty(name="Max Panel Weight (lb)", default=0.0, min=0.0)  # type: ignore
    manufacturer: StringProperty(name="Manufacturer", default="")  # type: ignore
    model: StringProperty(name="Model", default="")  # type: ignore
    spec_url: StringProperty(name="Spec", default="")  # type: ignore
    columns: CollectionProperty(type=Appliance_Panel_Column)  # type: ignore
    sections: CollectionProperty(type=Appliance_Panel_Section)  # type: ignore

    def has_rails(self):
        return bool(self.rail_width > 0.0
                    and (self.rail_top or self.rail_bottom or self.rail_between))


# ----------------------------------------------------------------------
# Seeding
# ----------------------------------------------------------------------
class suspended:
    def __enter__(self):
        _SUSPEND[0] += 1

    def __exit__(self, *exc):
        _SUSPEND[0] -= 1


def default_toe_kick(appliance_obj):
    """Under-counter appliances start above the toe kick: the project toe
    kick default (scene hb_face_frame), else the per-cabinet property
    default."""
    if appliance_obj is None or appliance_obj.get('APPLIANCE_TYPE') not in KICK_APPLIANCE_TYPES:
        return 0.0
    ff = getattr(bpy.context.scene, 'hb_face_frame', None)
    tk = getattr(ff, 'default_toe_kick_height', None) if ff is not None else None
    if tk is not None:
        return tk
    from . import props_hb_face_frame as props
    try:
        return props.Face_Frame_Cabinet_Props.bl_rna.properties['toe_kick_height'].default
    except Exception:
        return _I(4.0)


def default_rail_width():
    """The active cabinet style's base top rail width, so the rails mimic
    the cabinetry around the appliance."""
    from . import props_hb_face_frame as props
    ff = props.get_style_props()
    try:
        cs = ff.cabinet_styles[ff.active_cabinet_style_index]
        w = getattr(cs, 'ff_top_rail_width_base', 0.0)
        return w if w > 0.0 else _I(1.5)
    except Exception:
        return _I(1.5)


def seed_preset(appliance_obj, config, keep_options=True):
    """Reset the section / column lists to a preset. Appliance-level options
    (toe kick, reveals, rails, panel type) are kept unless keep_options is
    False, in which case they seed from the defaults."""
    props = appliance_obj.appliance_panels
    preset = PRESETS.get(config, PRESETS['SINGLE'])
    with suspended():
        props.config = config
        if not keep_options or not props.columns and not props.sections:
            props.toe_kick = default_toe_kick(appliance_obj)
            props.rail_width = default_rail_width()
        props.columns.clear()
        props.sections.clear()
        for _ in preset['cols']:
            props.columns.add()
        for label, kind, h, hold in preset.get('bottom', ()):
            sec = props.sections.add()
            sec.label, sec.kind, sec.column = label, kind, -1
            sec.height, sec.height_hold = (h if h > 0 else _I(8)), hold
        for ci, col in enumerate(preset['cols']):
            for label, kind, h, hold in col:
                sec = props.sections.add()
                sec.label, sec.kind, sec.column = label, kind, ci
                sec.height, sec.height_hold = (h if h > 0 else _I(8)), hold
        for label, kind, h, hold in preset.get('top', ()):
            sec = props.sections.add()
            sec.label, sec.kind, sec.column = label, kind, -1
            sec.height, sec.height_hold = (h if h > 0 else _I(8)), hold


def seed_from_legacy(appliance_obj):
    """Files built before the section model: rebuild the lists from the
    APPLIANCE_PANEL_LAYOUT stamp so the appliance edits without a reset.
    Returns True when a legacy stamp was consumed."""
    props = appliance_obj.appliance_panels
    cfg = appliance_obj.get('APPLIANCE_PANEL_CONFIG')
    raw = appliance_obj.get('APPLIANCE_PANEL_LAYOUT')
    if not cfg or not raw or props.sections:
        return False
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return False
    seed_preset(appliance_obj, cfg, keep_options=False)
    with suspended():
        props.panel_type = appliance_obj.get('APPLIANCE_PANEL_TYPE') or 'A'
        props.toe_kick = float(data.get('toe_kick', props.toe_kick))
        rw = float(data.get('rail_width', 0.0) or 0.0)
        if rw > 0.0:
            props.rail_width = rw
        props.rail_top = bool(data.get('rail_top', False))
        props.rail_bottom = bool(data.get('rail_bottom', False))
        props.rail_between = bool(data.get('rail_between', False))
        sizes = list(data.get('front_sizes', []))
        holds = list(data.get('front_holds', []))
        # Legacy order: column fronts (column-then-front) then bottom banners;
        # seed_preset lists bottom banners FIRST, so map by (column, order).
        col_secs = [s for s in props.sections if s.column >= 0]
        ban_secs = [s for s in props.sections if s.column < 0]
        ordered = col_secs + ban_secs
        for sec, size, hold in zip(ordered, sizes, holds):
            if size > 0:
                sec.height = size
            sec.height_hold = bool(hold)
        for col, w, hold in zip(props.columns, data.get('col_widths', []),
                                data.get('col_holds', [])):
            col.width = w
            col.width_hold = bool(hold)
    return True


# ----------------------------------------------------------------------
# Solver
# ----------------------------------------------------------------------
def _share(total, holds, sizes, gap):
    n = len(holds)
    usable = total - gap * max(0, n - 1)
    held = sum(sizes[i] for i in range(n) if holds[i])
    autos = [i for i in range(n) if not holds[i]]
    share = (usable - held) / len(autos) if autos else 0.0
    return [sizes[i] if holds[i] else max(0.0, share) for i in range(n)]


def _stack(z_lo, z_hi, secs, props, bottom_free=True, top_free=True):
    """Stack ``secs`` (dicts: h, h_hold, z, z_hold, idx) bottom-to-top inside
    [z_lo, z_hi]. Held heights keep; a held bottom pins the section and
    starts a new segment; autos share each segment. A FREE end is the
    appliance's own end: it takes the end reveal (or an integral rail plus
    the inset reveal); a bounded end (a banner sits there, a gap away)
    takes no margin and no rail. Returns ({idx: (z0, z1)}, [rail (z0, z1)])."""
    rw = props.rail_width if props.has_rails() else 0.0
    r_top = bool(rw and props.rail_top and top_free)
    r_bot = bool(rw and props.rail_bottom and bottom_free)
    r_mid = bool(rw and props.rail_between)
    bottom_margin = ((rw + RAIL_REVEAL) if r_bot else props.end_reveal) if bottom_free else 0.0
    top_margin = ((rw + RAIL_REVEAL) if r_top else props.end_reveal) if top_free else 0.0
    gap = (rw + 2.0 * RAIL_REVEAL) if r_mid else props.section_gap
    run_lo, run_hi = z_lo + bottom_margin, z_hi - top_margin

    # Segments split at held bottoms.
    segments = []          # (start_z, [secs])
    for s in secs:
        if s['z_hold'] or not segments:
            start = s['z'] if s['z_hold'] else run_lo
            segments.append([max(start, run_lo) if s['z_hold'] else run_lo, [s]])
        else:
            segments[-1][1].append(s)
    spans, rails = {}, []
    if r_bot:
        rails.append((z_lo, z_lo + rw))
    for si, (start, group) in enumerate(segments):
        end = (segments[si + 1][0] - gap) if si + 1 < len(segments) else run_hi
        heights = _share(max(0.0, end - start), [g['h_hold'] for g in group],
                         [g['h'] for g in group], gap)
        z = start
        for k, g in enumerate(group):
            spans[g['idx']] = (z, z + heights[k])
            z += heights[k]
            last = (si + 1 == len(segments)) and (k + 1 == len(group))
            if not last and r_mid:
                rails.append((z + RAIL_REVEAL, z + RAIL_REVEAL + rw))
            if k + 1 < len(group):
                z += gap
    if r_top:
        rails.append((z_hi - rw, z_hi))
    return spans, rails


def solve(props, dim_x, dim_z):
    """Return (faces, backers, rails):
        faces   {section_index: (x0, x1, z0, z1)}
        backers {section_index: (x0, x1, z0, z1, thickness)}
        rails   [(x0, x1, z0, z1)]
    all in appliance-local X (across) / Z (up), metres."""
    ncol = max(1, len(props.columns))
    col_w = _share(dim_x - 2.0 * props.end_reveal,
                   [c.width_hold for c in props.columns] or [False],
                   [c.width for c in props.columns] or [dim_x], props.section_gap)
    col_x = []
    x = props.end_reveal
    for w in col_w:
        col_x.append((x, x + w))
        x += w + props.section_gap
    z_lo, z_hi = max(0.0, props.toe_kick), dim_z

    secs = list(props.sections)
    col_idx = [i for i, s in enumerate(secs) if 0 <= s.column < ncol]
    first_col = col_idx[0] if col_idx else len(secs)
    last_col = col_idx[-1] if col_idx else -1
    bottom = [i for i, s in enumerate(secs) if s.column < 0 and i < first_col]
    top = [i for i, s in enumerate(secs) if s.column < 0 and i > last_col]
    others = [i for i, s in enumerate(secs) if s.column >= ncol]   # orphaned columns: skip

    faces = {}
    # Vertical: bottom banners + [column region] + top banners share the run.
    v_holds = [secs[i].height_hold for i in bottom] + [False] + [secs[i].height_hold for i in top]
    v_sizes = [secs[i].height for i in bottom] + [0.0] + [secs[i].height for i in top]
    v = _share(z_hi - z_lo - 2.0 * props.end_reveal, v_holds, v_sizes, props.section_gap)
    z = z_lo + props.end_reveal
    for k, i in enumerate(bottom):
        faces[i] = (props.end_reveal, dim_x - props.end_reveal, z, z + v[k])
        z += v[k] + props.section_gap
    region_lo = z
    region_h = v[len(bottom)]
    z = region_lo + region_h + props.section_gap
    for k, i in enumerate(top):
        h = v[len(bottom) + 1 + k]
        faces[i] = (props.end_reveal, dim_x - props.end_reveal, z, z + h)
        z += h + props.section_gap
    # Columns stack inside the region. With no banners the region IS the run
    # (its margins are the end reveals / rails); with a banner at an end the
    # region already sits a gap away from it, so that end has no margin.
    rails = []
    for ci in range(ncol):
        col_secs = [dict(h=secs[i].height, h_hold=secs[i].height_hold,
                         z=secs[i].z_bottom, z_hold=secs[i].z_hold, idx=i)
                    for i in col_idx if secs[i].column == ci]
        if not col_secs:
            continue
        spans, rl = _stack(region_lo if bottom else z_lo,
                           (region_lo + region_h) if top else z_hi,
                           col_secs, props,
                           bottom_free=not bottom, top_free=not top)
        x0, x1 = col_x[ci] if ci < len(col_x) else col_x[-1]
        for i, (za, zb) in spans.items():
            faces[i] = (x0, x1, za, zb)
        rails.extend((x0, x1, za, zb) for za, zb in rl)

    backers = {}
    for i, rect in faces.items():
        s = secs[i]
        btype = props.panel_type if s.backer == 'DEFAULT' else s.backer
        t = BACKER_THICKNESS.get(btype)
        if not t:
            continue
        fx0, fx1, fz0, fz1 = rect
        fw, fh = fx1 - fx0, fz1 - fz0
        bw = s.backer_width if s.backer_width_hold else fw + 2.0 * props.backer_reveal
        bh = s.backer_height if s.backer_height_hold else fh + 2.0 * props.backer_reveal
        cx, cz = (fx0 + fx1) / 2.0, (fz0 + fz1) / 2.0
        backers[i] = (cx - bw / 2.0, cx + bw / 2.0, cz - bh / 2.0, cz + bh / 2.0, t)
    return faces, backers, rails


# ----------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------
def _cage_dims(appliance_obj):
    cage = hb_types.GeoNodeCage(appliance_obj)
    return (cage.get_input('Dim X') or 0.0, cage.get_input('Dim Y') or 0.0,
            cage.get_input('Dim Z') or 0.0)


def _parts(appliance_obj, tag, index_key):
    out = [c for c in appliance_obj.children if c.get(tag)]
    out.sort(key=lambda o: o.get(index_key, 0))
    return out


def _new_part(appliance_obj, name, tag, index_key, index, thickness):
    part = types_face_frame.CabinetPart()
    part.create(name)
    obj = part.obj
    obj[tag] = True
    obj[index_key] = index
    obj['Finish Top'] = True
    obj['Finish Bottom'] = True
    obj.parent = appliance_obj
    obj.rotation_euler = (math.radians(90), math.radians(-90), 0)
    part.set_input('Thickness', thickness)
    part.set_input('Mirror Y', True)
    return obj


def _place(obj, x0, x1, z0, z1, y, thickness=None):
    part = hb_types.GeoNodeCutpart(obj)
    obj.location = (x0, y, z0)
    part.set_input('Width', x1 - x0)
    part.set_input('Length', z1 - z0)
    if thickness is not None:
        part.set_input('Thickness', thickness)


def _finish_part(obj):
    """Backers / rails take the active cabinet style's finish (surface +
    rotated edges), the way the other non-cabinet products do."""
    from . import props_hb_face_frame as props
    ff = props.get_style_props()
    if ff is None:
        return
    idx = ff.active_cabinet_style_index
    if not (0 <= idx < len(ff.cabinet_styles)):
        return
    cs = ff.cabinet_styles[idx]
    finish_mat, finish_mat_rotated = cs.get_finish_material()
    if finish_mat is None:
        return
    cs._set_part_surfaces(obj, finish_mat, finish_mat_rotated)
    obj['STYLE_NAME'] = cs.name


def _rout_flange(backer_obj, w, h, backer_t):
    """Type C: rout a recess around the appliance-facing perimeter for the
    installation flange, as four CPM_CUTOUT edge strips (a rabbet frame)."""
    part = hb_types.GeoNodeCutpart(backer_obj)
    for mod in list(backer_obj.modifiers):
        if mod.name.startswith('Flange '):
            backer_obj.modifiers.remove(mod)
    inset, depth = FLANGE_INSET, FLANGE_DEPTH
    strips = (('Flange Left', 0.0, 0.0, h, inset),
              ('Flange Right', 0.0, w - inset, h, w),
              ('Flange Bottom', 0.0, 0.0, inset, w),
              ('Flange Top', h - inset, 0.0, h, w))
    for name, x0, y0, x1, y1 in strips:
        cpm = part.add_part_modifier('CPM_CUTOUT', name)
        cpm.set_input('X', x0)
        cpm.set_input('Y', y0)
        cpm.set_input('End X', x1)
        cpm.set_input('End Y', y1)
        cpm.set_input('Route Depth', depth)
        cpm.set_input('Flip Z', True)
        cpm.mod.show_viewport = True
        cpm.mod.show_render = True


def _structure_key(props, backers):
    return json.dumps({'config': props.config, 'n': len(props.sections),
                       'backers': sorted(int(i) for i in backers)})


def rebuild(appliance_obj):
    """Build / resize the appliance's fronts, backers and rails from the
    property groups. In place when the structure is unchanged; teardown +
    rebuild otherwise. Stamps the cage for downstream consumers."""
    props = appliance_obj.appliance_panels
    if not props.sections:
        return
    dim_x, dim_y, dim_z = _cage_dims(appliance_obj)
    faces, backers, rails = solve(props, dim_x, dim_z)
    order = sorted(faces)                       # section index order
    key = _structure_key(props, backers)
    fronts = _parts(appliance_obj, TAG_FRONT, 'AP_PANEL_INDEX')
    in_place = (appliance_obj.get('APPLIANCE_PANEL_STRUCTURE') == key
                and len(fronts) == len(order))
    if not in_place:
        for child in list(appliance_obj.children):
            if child.get(TAG_FRONT) or child.get(TAG_BACKER):
                for sub in list(child.children):
                    bpy.data.objects.remove(sub, do_unlink=True)
                bpy.data.objects.remove(child, do_unlink=True)
        fronts = []
        for k, i in enumerate(order):
            obj = _new_part(appliance_obj, 'Appliance Panel', TAG_FRONT,
                            'AP_PANEL_INDEX', k, FACE_THICKNESS)
            obj['AP_SECTION_INDEX'] = i
            obj['hb_part_role'] = types_face_frame.PART_ROLE_DOOR
            fronts.append(obj)
        for i, (bx0, bx1, bz0, bz1, t) in backers.items():
            b = _new_part(appliance_obj, 'Appliance Panel Backer', TAG_BACKER,
                          'AP_SECTION_INDEX', i, t)
            b['APPLIANCE_PANEL_BACKER_TYPE'] = (
                props.panel_type if props.sections[i].backer == 'DEFAULT'
                else props.sections[i].backer)

    # Position everything (in place or fresh).
    backer_objs = {b.get('AP_SECTION_INDEX'): b for b in _parts(appliance_obj, TAG_BACKER, 'AP_SECTION_INDEX')}
    for k, i in enumerate(order):
        sec = props.sections[i]
        x0, x1, z0, z1 = faces[i]
        b = backers.get(i)
        y = -dim_y - (b[4] if b else 0.0)
        obj = fronts[k]
        obj['AP_SECTION_INDEX'] = i
        obj['AP_SECTION_LABEL'] = sec.label
        obj['AP_SECTION_KIND'] = sec.kind
        _place(obj, x0, x1, z0, z1, y, sec.face_thickness)
        if 'HB_DOOR_FRAME' in obj:
            from .operators import ops_part_commands
            ops_part_commands._reapply_front_style(obj)
        if b:
            bobj = backer_objs.get(i)
            if bobj is not None:
                bx0, bx1, bz0, bz1, t = b
                _place(bobj, bx0, bx1, bz0, bz1, -dim_y, t)
                _finish_part(bobj)
                if bobj.get('APPLIANCE_PANEL_BACKER_TYPE') == 'C':
                    _rout_flange(bobj, bx1 - bx0, bz1 - bz0, t)

    # Rails: reuse by index, drop extras.
    rail_objs = _parts(appliance_obj, TAG_RAIL, 'AP_RAIL_INDEX')
    for extra in rail_objs[len(rails):]:
        bpy.data.objects.remove(extra, do_unlink=True)
    rail_objs = rail_objs[:len(rails)]
    for k, (x0, x1, z0, z1) in enumerate(rails):
        if k < len(rail_objs):
            r = rail_objs[k]
        else:
            r = _new_part(appliance_obj, 'Appliance Panel Rail', TAG_RAIL,
                          'AP_RAIL_INDEX', k, RAIL_THICKNESS)
            r['hb_part_role'] = types_face_frame.PART_ROLE_TOP_RAIL
        _place(r, x0, x1, z0, z1, -dim_y)
        _finish_part(r)

    if not in_place:
        # Door style needs the real dims live before it is applied (mid-rail
        # on tall doors keys off height).
        bpy.context.view_layer.update()
        for obj in fronts:
            types_face_frame.apply_active_door_style_to_part(obj)
        for child in appliance_obj.children:
            if child.get('IS_APPLIANCE_TEXT') or child.type == 'FONT':
                child.hide_viewport = True
                child.hide_render = True

    _stamp(appliance_obj, props, key, faces, backers, rails)


def _stamp(appliance_obj, props, key, faces, backers, rails):
    appliance_obj['APPLIANCE_PANEL_STRUCTURE'] = key
    appliance_obj['APPLIANCE_PANEL_CONFIG'] = props.config
    appliance_obj['APPLIANCE_PANEL_TYPE'] = props.panel_type
    # Legacy stamp kept for readers of the flat layout (sizes bottom-to-top
    # in section order, plus the options).
    appliance_obj['APPLIANCE_PANEL_LAYOUT'] = json.dumps({
        'sections': [{'label': s.label, 'kind': s.kind, 'column': s.column,
                      'height': s.height, 'height_hold': s.height_hold,
                      'z_bottom': s.z_bottom, 'z_hold': s.z_hold,
                      'backer': s.backer,
                      'backer_width': s.backer_width, 'backer_width_hold': s.backer_width_hold,
                      'backer_height': s.backer_height, 'backer_height_hold': s.backer_height_hold}
                     for s in props.sections],
        'columns': [{'width': c.width, 'width_hold': c.width_hold} for c in props.columns],
        'toe_kick': props.toe_kick, 'end_reveal': props.end_reveal,
        'section_gap': props.section_gap, 'backer_reveal': props.backer_reveal,
        'rail_width': props.rail_width, 'rail_top': props.rail_top,
        'rail_bottom': props.rail_bottom, 'rail_between': props.rail_between,
        'faces': {str(i): list(r) for i, r in faces.items()},
        'backers': {str(i): list(r) for i, r in backers.items()}})
    if props.has_rails() and rails:
        appliance_obj['APPLIANCE_PANEL_RAILS'] = ','.join(
            k for k, on in (('TOP', props.rail_top), ('BOTTOM', props.rail_bottom),
                            ('BETWEEN', props.rail_between)) if on)
        appliance_obj['APPLIANCE_PANEL_RAIL_WIDTH'] = props.rail_width
        appliance_obj['APPLIANCE_PANEL_RAIL_COUNT'] = len(rails)
    else:
        for k in ('APPLIANCE_PANEL_RAILS', 'APPLIANCE_PANEL_RAIL_WIDTH',
                  'APPLIANCE_PANEL_RAIL_COUNT'):
            if k in appliance_obj:
                del appliance_obj[k]
    if 'Panel Ready' in appliance_obj:
        appliance_obj['Panel Ready'] = True


# ----------------------------------------------------------------------
# Manufacturer spec -> sections
# ----------------------------------------------------------------------
def apply_spec(appliance_obj, spec):
    """Fill the section model from a resolved manufacturer spec (see the
    appliance spec registry). The spec's per-opening face and backer sizes
    become HELD section values; anything the guide leaves open stays auto.
    Each spec panel carries ``position``: TOP / BOTTOM (full-width banners),
    LEFT / RIGHT (columns of a side-by-side), BOTH (one panel per column),
    or MAIN (the single column). Returns a list of notes."""
    props = appliance_obj.appliance_panels
    notes = []
    cfg = spec.get('operator_config') or 'SINGLE'
    seed_preset(appliance_obj, cfg, keep_options=True)
    with suspended():
        ptype = spec.get('operator_panel_type')
        if ptype in ('A', 'B', 'C'):
            props.panel_type = ptype
        props.manufacturer = spec.get('manufacturer') or ''
        props.model = spec.get('model') or ''
        props.spec_url = spec.get('source_url') or ''
        w = spec.get('weight_max_lb')
        props.weight_max_lb = float(w) if isinstance(w, (int, float)) else 0.0
        it = (spec.get('install_type') or '').lower()
        props.install_type = 'FLUSH_INSET' if 'inset' in it and 'overlay' not in it else 'OVERLAY'
        dim_x = spec.get('appliance_dim_x_m')
        if dim_x:
            try:
                hb_types.GeoNodeCage(appliance_obj).set_input('Dim X', dim_x)
            except Exception:
                pass

        ncol = len(props.columns)
        col_secs = [s for s in props.sections if s.column >= 0]
        by_col = {ci: [s for s in col_secs if s.column == ci] for ci in range(ncol)}

        def _fill(sec, panel, held_width_col=None):
            fw, fh = panel.get('face_w_m'), panel.get('face_h_m')
            bw, bh = panel.get('backer_w_m'), panel.get('backer_h_m')
            if fh:
                sec.height, sec.height_hold = fh, True
            if fw and held_width_col is not None and held_width_col < ncol:
                props.columns[held_width_col].width = fw
                props.columns[held_width_col].width_hold = True
            if bw and bh:
                sec.backer_width, sec.backer_width_hold = bw, True
                sec.backer_height, sec.backer_height_hold = bh, True
                if sec.backer == 'DEFAULT' and props.panel_type == 'A':
                    sec.backer = 'B'
            sec.spec_note = ' / '.join(x for x in (
                panel.get('opening'), panel.get('routing')) if x)

        for panel in spec.get('panels') or []:
            pos = (panel.get('position') or 'MAIN').upper()
            opening = panel.get('opening') or 'Panel'
            if pos == 'TOP':
                sec = props.sections.add()
                sec.label, sec.kind, sec.column = opening, 'PANEL', -1
                _fill(sec, panel)
            elif pos == 'BOTTOM' and ncol == 1:
                # Single column: the bottom section of the column.
                secs = by_col.get(0) or []
                if secs:
                    _fill(secs[0], panel, held_width_col=0)
                    secs[0].label = opening
            elif pos == 'BOTTOM':
                # The preset's bottom banner if it has one (a spanning
                # section listed before any column section), else a fresh
                # one moved to the front of the list.
                first_col = next((k for k, s in enumerate(props.sections)
                                  if s.column >= 0), len(props.sections))
                banner = next((s for k, s in enumerate(props.sections)
                               if s.column < 0 and k < first_col), None)
                if banner is None:
                    banner = props.sections.add()
                    banner.label, banner.kind, banner.column = opening, 'DRAWER', -1
                    props.sections.move(len(props.sections) - 1, 0)
                    banner = props.sections[0]
                _fill(banner, panel)
            elif pos == 'BOTH':
                for ci in range(ncol):
                    secs = by_col.get(ci) or []
                    if secs:
                        _fill(secs[0], panel, held_width_col=ci)
            elif pos in ('LEFT', 'RIGHT'):
                ci = 0 if pos == 'LEFT' else min(1, ncol - 1)
                secs = by_col.get(ci) or []
                if secs:
                    _fill(secs[0], panel, held_width_col=ci)
                    secs[0].label = opening
            else:   # MAIN
                secs = by_col.get(0) or []
                target = None
                for s in secs:
                    if s.kind == ('DRAWER' if 'drawer' in opening.lower() else 'DOOR'):
                        target = s
                        break
                if target is None and secs:
                    target = secs[0]
                if target is not None:
                    _fill(target, panel, held_width_col=0)
        # A guide that gives face sizes also fixes the spacing: the faces
        # span the appliance width with the guide's own gap between them
        # (Sub-Zero: 1/4"), so the horizontal margins fall out of the
        # numbers; vertically the stack hangs from the TOP of the appliance
        # (the grille hides the upper frame) and the leftover is the bottom
        # clearance. Only when every column width / section height is held.
        try:
            dim_x, _dy, dim_z = _cage_dims(appliance_obj)
        except Exception:
            dim_x = dim_z = 0.0
        if dim_x and props.columns and all(c.width_hold for c in props.columns):
            gap = SPEC_PANEL_GAP
            widths = sum(c.width for c in props.columns)
            margin = (dim_x - widths - gap * (len(props.columns) - 1)) / 2.0
            if margin >= -1e-6:
                props.section_gap = gap
                props.end_reveal = max(0.0, margin)
        if dim_z and props.sections and all(s.height_hold for s in props.sections):
            secs = list(props.sections)
            ncol_ = len(props.columns)
            col_idx = [i for i, s_ in enumerate(secs) if 0 <= s_.column < ncol_]
            fc = col_idx[0] if col_idx else len(secs)
            lc = col_idx[-1] if col_idx else -1
            bottom_h = [secs[i].height for i, s_ in enumerate(secs) if s_.column < 0 and i < fc]
            top_h = [secs[i].height for i, s_ in enumerate(secs) if s_.column < 0 and i > lc]
            col_h = 0.0
            for ci in range(ncol_):
                hs = [secs[i].height for i in col_idx if secs[i].column == ci]
                if hs:
                    col_h = max(col_h, sum(hs) + props.section_gap * (len(hs) - 1))
            stack = sum(bottom_h) + sum(top_h) + col_h
            stack += props.section_gap * ((1 if bottom_h else 0) + (1 if top_h else 0)
                                          + max(0, len(bottom_h) - 1) + max(0, len(top_h) - 1))
            leftover = dim_z - stack - 2.0 * props.end_reveal
            if leftover > 0.0:
                props.toe_kick = leftover
                notes.append("Panels hung from the top; %.2f\" left at the "
                             "bottom (verify against the guide)."
                             % (leftover / _I(1.0)))
        for f in spec.get('flags') or []:
            notes.append(f)
    return notes


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------
classes = (Appliance_Panel_Column, Appliance_Panel_Section, Appliance_Panel_Props)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.appliance_panels = PointerProperty(type=Appliance_Panel_Props)


def unregister():
    if hasattr(bpy.types.Object, 'appliance_panels'):
        del bpy.types.Object.appliance_panels
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
