import bpy
import math
import json
from bpy.props import EnumProperty, FloatProperty, BoolProperty, StringProperty
from .. import types_face_frame
from .... import hb_utils, hb_types, units, appliance_spec_registry

# --- Appliance panels: face-frame door-style panels on a panel-ready appliance.
# Fronts are bare CabinetParts (no pull) tagged DOOR-role so the active FACE-FRAME
# door style renders them. The layout is a calculator: every front (and column)
# shows its size; a HELD front/column keeps its size and the rest share the
# leftover space equally (mirrors the face-frame opening-size sections). The
# cage carries neutral descriptor tags (APPLIANCE_PANEL_CONFIG / _TYPE / _LAYOUT
# json) that downstream consumers can read.
APPLIANCE_PANEL_REVEAL = units.inch(1.0)     # gap between appliance edge and panel
APPLIANCE_PANEL_GAP = units.inch(1.0)        # gap between adjacent panels
APPLIANCE_PANEL_THICKNESS = units.inch(0.75)
# Type B/C backer panel thickness; the door face is applied to its front.
BACKER_THICKNESS = {'B': units.inch(0.25), 'C': units.inch(0.35)}
# Type C installation-flange rout (representative; tune in Blender): a recess
# around the back-face perimeter where the appliance mounting flange seats.
FLANGE_INSET = units.inch(1.5)   # recess band width in from each edge
FLANGE_DEPTH = units.inch(0.2)   # rout depth into the backer
_I = units.inch

_CONFIG_ITEMS = {
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
_DEFAULT_CONFIG_ITEMS = [('SINGLE', "Single", "One full-height panel")]

_PANEL_TYPE_ITEMS = [
    ('A', "Type A", "Face on 1/4\" backer"),
    ('B', "Type B", "Face with access panel / backer"),
    ('C', "Type C", "Face on .35\" backer, routed for an install flange"),
]

# Configuration -> columns, each a list of fronts ordered BOTTOM to TOP.
# Each front = (label, default_size_meters, default_hold). default_size is only
# meaningful when held; auto (hold=False) fronts share the leftover equally.
MAX_FRONTS = 4
MAX_COLUMNS = 2
_CONFIG_LAYOUT = {
    'SINGLE': [[("Door", 0.0, False)]],
    'FRENCH_DOOR': [[("Left Door", 0.0, False)], [("Right Door", 0.0, False)]],
    'FRENCH_DOOR_BOTTOM_FREEZER': [[("Left Door", 0.0, False)],
                                  [("Right Door", 0.0, False)]],
    'BOTTOM_FREEZER': [[("Freezer Drawer", _I(24), True), ("Door", 0.0, False)]],
    'BOTTOM_FREEZER_2DRAWER': [[("Lower Drawer", _I(12), True),
                                ("Upper Drawer", _I(12), True),
                                ("Door", 0.0, False)]],
    'TOP_FREEZER': [[("Door", 0.0, False), ("Freezer", _I(16), True)]],
    'DRAWER_DOOR_DRAWER': [[("Bottom Drawer", _I(8), True),
                            ("Door", 0.0, False),
                            ("Top Drawer", _I(8), True)]],
    'SIDE_BY_SIDE_SPLIT': [[("Left Door", 0.0, False), ("Left Top Drawer", _I(8), True)],
                           [("Right Door", 0.0, False)]],
    # Dishwasher / under-counter configs (single column, fronts bottom->top).
    'DW_DRAWER_DOOR': [[("Door", 0.0, False), ("Drawer", _I(6), True)]],
    'DW_3_DRAWER': [[("Bottom Drawer", 0.0, False),
                     ("Middle Drawer", 0.0, False),
                     ("Top Drawer", 0.0, False)]],
    'DW_4_DRAWER': [[("Drawer 1", 0.0, False), ("Drawer 2", 0.0, False),
                     ("Drawer 3", 0.0, False), ("Drawer 4", 0.0, False)]],
}

# Configs with a full-width front (a "banner") spanning the bottom, BELOW the
# columns - for a single drawer that runs the full width under a multi-column
# region (e.g. a freezer drawer under french doors), which the column model
# alone cannot express. Banner fronts take global indices AFTER the column
# fronts (see _iter_fronts).
_CONFIG_FULLWIDTH_BOTTOM = {
    'FRENCH_DOOR_BOTTOM_FREEZER': [("Freezer Drawer", _I(16), True)],
}


def _appliance_type(context):
    obj = context.object
    bp = hb_utils.get_appliance_bp(obj) if obj else None
    return bp.get('APPLIANCE_TYPE') if bp else None


def _config_enum_items(self, context):
    return _CONFIG_ITEMS.get(_appliance_type(context), _DEFAULT_CONFIG_ITEMS)


def _iter_fronts(config):
    """Yield (global_index, col_index, label, default_size, default_hold) for a
    config: the column fronts in column-then-front order, then any full-width
    bottom banner fronts (col_index None)."""
    g = 0
    for ci, col in enumerate(_CONFIG_LAYOUT.get(config, _CONFIG_LAYOUT['SINGLE'])):
        for (label, size, hold) in col:
            yield g, ci, label, size, hold
            g += 1
    for (label, size, hold) in _CONFIG_FULLWIDTH_BOTTOM.get(config, ()):
        yield g, None, label, size, hold
        g += 1


def _num_columns(config):
    return len(_CONFIG_LAYOUT.get(config, _CONFIG_LAYOUT['SINGLE']))


def _solve(total, holds, sizes):
    """Distribute `total` among items: held items keep their size, the rest
    share the leftover equally. Accounts for a reveal at each end and a gap
    between items. Returns the solved size of each item (meters)."""
    n = len(holds)
    usable = total - 2 * APPLIANCE_PANEL_REVEAL - APPLIANCE_PANEL_GAP * (n - 1)
    held = sum(sizes[i] for i in range(n) if holds[i])
    autos = [i for i in range(n) if not holds[i]]
    share = (usable - held) / len(autos) if autos else 0.0
    return [sizes[i] if holds[i] else max(0.0, share) for i in range(n)]


def _solve_region(total, holds, sizes):
    """Like _solve but WITHOUT the two end reveals - fills a sub-region whose
    extents are already fixed (e.g. the column region above a banner)."""
    n = len(holds)
    usable = total - APPLIANCE_PANEL_GAP * (n - 1)
    held = sum(sizes[i] for i in range(n) if holds[i])
    autos = [i for i in range(n) if not holds[i]]
    share = (usable - held) / len(autos) if autos else 0.0
    return [sizes[i] if holds[i] else max(0.0, share) for i in range(n)]


def _banner_split(config, dim_z, front_sizes, front_holds):
    """Split dim_z for a banner config into (banner_heights, region_height,
    ncol_fronts): the full-width bottom banners (bottom-to-top) plus the height
    left for the column region above them. Banners + region solve as one
    vertical stack, so the cabinet's end reveals land at the true top/bottom."""
    cols = _CONFIG_LAYOUT.get(config, _CONFIG_LAYOUT['SINGLE'])
    ncol_fronts = sum(len(c) for c in cols)
    banners = _CONFIG_FULLWIDTH_BOTTOM.get(config, ())
    nb = len(banners)
    bh = [front_holds[ncol_fronts + i] for i in range(nb)]
    bs = [front_sizes[ncol_fronts + i] for i in range(nb)]
    v = _solve(dim_z, bh + [False], bs + [0.0])
    return v[:nb], v[nb], ncol_fronts


def _solve_layout(config, dim_x, dim_z, front_sizes, front_holds, col_widths, col_holds):
    """Return [(x0, x1, z0, z1)] literal panel rects (meters) for the config, in
    _iter_fronts order: column fronts first, then any full-width bottom banners.
    Column widths solve over dim_x; front heights over dim_z, or over the region
    above the banners when the config has them."""
    cols = _CONFIG_LAYOUT.get(config, _CONFIG_LAYOUT['SINGLE'])
    ncol = len(cols)
    banners = _CONFIG_FULLWIDTH_BOTTOM.get(config, ())
    solved_w = _solve(dim_x, [col_holds[c] for c in range(ncol)],
                      [col_widths[c] for c in range(ncol)])

    if banners:
        banner_h, region_h, ncf = _banner_split(config, dim_z, front_sizes, front_holds)
        rects = [None] * (ncf + len(banners))
        x0b, x1b = APPLIANCE_PANEL_REVEAL, dim_x - APPLIANCE_PANEL_REVEAL
        z = APPLIANCE_PANEL_REVEAL
        for i in range(len(banners)):
            rects[ncf + i] = (x0b, x1b, z, z + banner_h[i])
            z += banner_h[i] + APPLIANCE_PANEL_GAP
        region_z0 = z  # bottom of the column region (above the banners + a gap)
        x_cursor = APPLIANCE_PANEL_REVEAL
        g = 0
        for ci, col in enumerate(cols):
            w = solved_w[ci]
            x0, x1 = x_cursor, x_cursor + w
            x_cursor += w + APPLIANCE_PANEL_GAP
            idxs = list(range(g, g + len(col)))
            h_solved = _solve_region(region_h, [front_holds[i] for i in idxs],
                                     [front_sizes[i] for i in idxs])
            z_cursor = region_z0
            for k, _front in enumerate(col):
                rects[g + k] = (x0, x1, z_cursor, z_cursor + h_solved[k])
                z_cursor += h_solved[k] + APPLIANCE_PANEL_GAP
            g += len(col)
        return rects

    rects = []
    x_cursor = APPLIANCE_PANEL_REVEAL
    g = 0
    for ci, col in enumerate(cols):
        w = solved_w[ci]
        x0, x1 = x_cursor, x_cursor + w
        x_cursor += w + APPLIANCE_PANEL_GAP
        idxs = list(range(g, g + len(col)))
        h_solved = _solve(dim_z, [front_holds[i] for i in idxs],
                          [front_sizes[i] for i in idxs])
        z_cursor = APPLIANCE_PANEL_REVEAL
        for k, _front in enumerate(col):
            h = h_solved[k]
            z0, z1 = z_cursor, z_cursor + h
            z_cursor += h + APPLIANCE_PANEL_GAP
            rects.append((x0, x1, z0, z1))
        g += len(col)
    return rects


def _set_front_geometry(obj, front_y, rect):
    """Push a solved rect onto an existing panel front (no object churn).
    front_y is the front's depth position (shifts forward of a Type B/C
    backer). A GN 'Door Style' modifier reflows from the cutpart inputs by
    itself; a python-built door (HB_DOOR_FRAME) is a static mesh, so its
    style is re-applied to rebuild it at the new size."""
    x0, x1, z0, z1 = rect
    part = hb_types.GeoNodeCutpart(obj)
    obj.location = (x0, front_y, z0)
    part.set_input('Width', x1 - x0)
    part.set_input('Length', z1 - z0)
    if 'HB_DOOR_FRAME' in obj:
        from . import ops_part_commands
        ops_part_commands._reapply_front_style(obj)


def _build_backer(appliance_obj, dim_x, dim_y, dim_z, backer_t, panel_type):
    """Type B/C: a plywood backer panel spanning the appliance front, behind
    the door faces (the faces are applied to its front). Type C is additionally
    routed for the appliance's installation flange. No door style (plain panel)."""
    backer = types_face_frame.CabinetPart()
    backer.create('Appliance Panel Backer')
    backer.obj['IS_APPLIANCE_PANEL_BACKER'] = True
    backer.obj['APPLIANCE_PANEL_BACKER_TYPE'] = panel_type
    backer.obj.parent = appliance_obj
    backer.obj.rotation_euler = (math.radians(90), math.radians(-90), 0)
    backer.obj.location = (0.0, -dim_y, 0.0)   # full appliance front, behind fronts
    backer.set_input('Width', dim_x)
    backer.set_input('Length', dim_z)
    backer.set_input('Thickness', backer_t)
    backer.set_input('Mirror Y', True)
    if panel_type == 'C':
        _rout_flange(backer, dim_x, dim_z, backer_t)
    return backer


def _rout_flange(backer, dim_x, dim_z, backer_t):
    """Type C: rout a recess around the appliance-facing perimeter for the
    appliance installation flange, as four CPM_CUTOUT edge strips (a rabbet
    frame). Representative dims (FLANGE_INSET / FLANGE_DEPTH) - tune in Blender.

    CPM_CUTOUT coords: X/End X run along the part Length (here = dim_z height),
    Y/End Y along the part Width (= dim_x), Route Depth into thickness, Flip Z
    selects the face (True = appliance-facing back; verify in render)."""
    part = hb_types.GeoNodeCutpart(backer.obj)
    inset = FLANGE_INSET
    depth = FLANGE_DEPTH
    L = dim_z   # Length-axis extent
    W = dim_x   # Width-axis extent
    strips = (
        ('Flange Left',   0.0,         0.0,         L,     inset),
        ('Flange Right',  0.0,         W - inset,   L,     W),
        ('Flange Bottom', 0.0,         0.0,         inset, W),
        ('Flange Top',    L - inset,   0.0,         L,     W),
    )
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


def _stamp_cage(appliance_obj, config, panel_type, front_sizes, front_holds,
                col_widths, col_holds):
    appliance_obj['APPLIANCE_PANEL_CONFIG'] = config
    appliance_obj['APPLIANCE_PANEL_TYPE'] = panel_type
    appliance_obj['APPLIANCE_PANEL_LAYOUT'] = json.dumps({
        'front_sizes': front_sizes, 'front_holds': front_holds,
        'col_widths': col_widths, 'col_holds': col_holds})
    if 'Panel Ready' in appliance_obj:
        appliance_obj['Panel Ready'] = True


def build_appliance_panels(appliance_obj, config, panel_type, front_sizes,
                           front_holds, col_widths, col_holds):
    """Create or resize the panel fronts from solved literal sizes.

    On a live size drag the configuration is unchanged and the panel count
    matches, so we RESIZE the existing fronts in place - no delete/recreate, no
    door-style re-apply - which avoids the flicker (and wrong intermediate size)
    that a full teardown causes on every value change. Objects are only rebuilt
    when the configuration / panel count actually changes.
    """
    cage = hb_types.GeoNodeCage(appliance_obj)
    dim_x = cage.get_input('Dim X')
    dim_y = cage.get_input('Dim Y')
    dim_z = cage.get_input('Dim Z')

    rects = _solve_layout(config, dim_x, dim_z, front_sizes, front_holds,
                          col_widths, col_holds)

    # Type B/C add a backer panel; the door faces shift forward of it.
    backer_t = BACKER_THICKNESS.get(panel_type, 0.0)
    front_y = -dim_y - backer_t

    existing = [c for c in appliance_obj.children if c.get('IS_APPLIANCE_PANEL_FRONT')]
    existing.sort(key=lambda o: o.get('AP_PANEL_INDEX', 0))

    # In-place resize when the structure is unchanged (the common live-edit case).
    # Panel type is part of the structure (it drives the backer), so a type
    # change falls through to a full rebuild.
    if (len(existing) == len(rects)
            and appliance_obj.get('APPLIANCE_PANEL_CONFIG') == config
            and appliance_obj.get('APPLIANCE_PANEL_TYPE') == panel_type):
        for obj, rect in zip(existing, rects):
            _set_front_geometry(obj, front_y, rect)
        _stamp_cage(appliance_obj, config, panel_type, front_sizes, front_holds,
                    col_widths, col_holds)
        return

    # Structure changed: tear down fronts + backer and recreate.
    for child in list(appliance_obj.children):
        if child.get('IS_APPLIANCE_PANEL_FRONT') or child.get('IS_APPLIANCE_PANEL_BACKER'):
            for sub in list(child.children):
                bpy.data.objects.remove(sub, do_unlink=True)
            bpy.data.objects.remove(child, do_unlink=True)

    fronts = []
    for idx, rect in enumerate(rects):
        x0, x1, z0, z1 = rect
        front = types_face_frame.CabinetPart()
        front.create('Appliance Panel')
        front.obj['IS_APPLIANCE_PANEL_FRONT'] = True
        front.obj['AP_PANEL_INDEX'] = idx
        front.obj['hb_part_role'] = types_face_frame.PART_ROLE_DOOR
        front.obj['Finish Top'] = True
        front.obj['Finish Bottom'] = True
        front.obj.parent = appliance_obj
        front.obj.rotation_euler = (math.radians(90), math.radians(-90), 0)
        front.obj.location = (x0, front_y, z0)
        front.set_input('Width', x1 - x0)
        front.set_input('Length', z1 - z0)
        front.set_input('Thickness', APPLIANCE_PANEL_THICKNESS)
        front.set_input('Mirror Y', True)
        fronts.append(front)

    if backer_t > 0:
        _build_backer(appliance_obj, dim_x, dim_y, dim_z, backer_t, panel_type)

    # Door style needs the real dims live before it is applied (mid-rail on tall
    # doors keys off height).
    bpy.context.view_layer.update()
    for front in fronts:
        types_face_frame.apply_active_door_style_to_part(front.obj)

    for child in appliance_obj.children:
        if child.get('IS_APPLIANCE_TEXT') or child.type == 'FONT':
            child.hide_viewport = True
            child.hide_render = True

    _stamp_cage(appliance_obj, config, panel_type, front_sizes, front_holds,
                col_widths, col_holds)


# --- Manufacturer spec dropdowns: items come from whatever provider the host
# app registered in appliance_spec_registry (HB5 ships none, so the default is
# Manual). Enum item lists must stay alive at module scope - Blender keeps only
# the char* of each string, so a list built and dropped in the callback can be
# garbage-collected and crash the UI.
_mfr_items = []
_model_items = []


def _draw_wrapped(layout, text, icon='NONE', width=46):
    """Emit `text` across multiple labels so the operator popup doesn't
    truncate long notes. The icon (if any) sits on the first line; wrapped
    lines indent under it with a blank icon."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines or [text]):
        layout.label(text=ln, icon=(icon if i == 0 else 'BLANK1'))


def _manufacturer_enum(self, context):
    _mfr_items.clear()
    _mfr_items.append(('MANUAL', "Manual", "Set the size and layout by hand"))
    p = appliance_spec_registry.get_provider()
    if p is not None:
        try:
            for m in p.manufacturers():
                _mfr_items.append((m, m, m))
        except Exception as e:  # pragma: no cover - defensive
            print("HB5 appliance spec provider (manufacturers) failed: %s" % e)
    return _mfr_items


def _model_enum(self, context):
    _model_items.clear()
    p = appliance_spec_registry.get_provider()
    if p is not None and self.manufacturer not in ('MANUAL', ''):
        try:
            for d in p.models(self.manufacturer):
                _model_items.append(
                    (d['model'], d['model'], d.get('appliance_type', "")))
        except Exception as e:  # pragma: no cover - defensive
            print("HB5 appliance spec provider (models) failed: %s" % e)
    if not _model_items:
        _model_items.append(('NONE', "(none)", "No models in this catalog"))
    return _model_items


class hb_face_frame_OT_add_appliance_panels(bpy.types.Operator):
    bl_idname = "hb_face_frame.add_appliance_panels"
    bl_label = "Appliance Panels"
    bl_description = "Add or edit face-frame door-style panels on a panel-ready appliance"
    bl_options = {'REGISTER', 'UNDO'}

    manufacturer: EnumProperty(name="Manufacturer", items=_manufacturer_enum)  # type: ignore
    model: EnumProperty(name="Model", items=_model_enum)  # type: ignore
    last_model: StringProperty(default="")  # type: ignore
    configuration: EnumProperty(name="Configuration", items=_config_enum_items)  # type: ignore
    panel_type: EnumProperty(name="Panel Type", items=_PANEL_TYPE_ITEMS, default='A')  # type: ignore
    last_config: StringProperty(default="")  # type: ignore

    # Flat pools (mapped to fronts/columns per configuration in draw/execute).
    # invoke_props_popup re-runs execute on every edit, so plain props give a
    # reliable live update.
    size_1: FloatProperty(name="Size", unit='LENGTH', default=_I(8), min=_I(0.5))  # type: ignore
    size_2: FloatProperty(name="Size", unit='LENGTH', default=_I(8), min=_I(0.5))  # type: ignore
    size_3: FloatProperty(name="Size", unit='LENGTH', default=_I(8), min=_I(0.5))  # type: ignore
    size_4: FloatProperty(name="Size", unit='LENGTH', default=_I(8), min=_I(0.5))  # type: ignore
    hold_1: BoolProperty(name="Hold", default=False)  # type: ignore
    hold_2: BoolProperty(name="Hold", default=False)  # type: ignore
    hold_3: BoolProperty(name="Hold", default=False)  # type: ignore
    hold_4: BoolProperty(name="Hold", default=False)  # type: ignore
    col_width_1: FloatProperty(name="Width", unit='LENGTH', default=_I(18), min=_I(1))  # type: ignore
    col_width_2: FloatProperty(name="Width", unit='LENGTH', default=_I(18), min=_I(1))  # type: ignore
    col_hold_1: BoolProperty(name="Hold", default=False)  # type: ignore
    col_hold_2: BoolProperty(name="Hold", default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bp = hb_utils.get_appliance_bp(obj)
            if bp:
                return bp.get('APPLIANCE_TYPE') in {'DISHWASHER', 'REFRIGERATOR',
                                                    'UNDER_COUNTER'}
        return False

    def _reset_to_preset(self, config):
        """Seed the flat size/hold pools from the configuration preset."""
        for g, _ci, _label, size, hold in _iter_fronts(config):
            setattr(self, 'size_%d' % (g + 1), size if size > 0 else _I(8))
            setattr(self, 'hold_%d' % (g + 1), hold)
        for c in range(MAX_COLUMNS):
            setattr(self, 'col_hold_%d' % (c + 1), False)
        self.last_config = config

    def _gather(self, config):
        fronts = list(_iter_fronts(config))
        n = len(fronts)
        ncol = _num_columns(config)
        sizes = [getattr(self, 'size_%d' % (i + 1)) for i in range(n)]
        holds = [getattr(self, 'hold_%d' % (i + 1)) for i in range(n)]
        cwid = [getattr(self, 'col_width_%d' % (c + 1)) for c in range(ncol)]
        chold = [getattr(self, 'col_hold_%d' % (c + 1)) for c in range(ncol)]
        return sizes, holds, cwid, chold

    def invoke(self, context, event):
        bp = hb_utils.get_appliance_bp(context.object)
        cfg = bp.get('APPLIANCE_PANEL_CONFIG')
        if cfg:
            try:
                self.configuration = cfg
            except TypeError:
                cfg = None
        ptype = bp.get('APPLIANCE_PANEL_TYPE')
        if ptype:
            try:
                self.panel_type = ptype
            except TypeError:
                pass
        stored = bp.get('APPLIANCE_PANEL_LAYOUT')
        if cfg and stored:
            try:
                data = json.loads(stored)
                for i, v in enumerate(data.get('front_sizes', [])[:MAX_FRONTS]):
                    setattr(self, 'size_%d' % (i + 1), v)
                for i, v in enumerate(data.get('front_holds', [])[:MAX_FRONTS]):
                    setattr(self, 'hold_%d' % (i + 1), v)
                for i, v in enumerate(data.get('col_widths', [])[:MAX_COLUMNS]):
                    setattr(self, 'col_width_%d' % (i + 1), v)
                for i, v in enumerate(data.get('col_holds', [])[:MAX_COLUMNS]):
                    setattr(self, 'col_hold_%d' % (i + 1), v)
                self.last_config = cfg
            except (ValueError, TypeError):
                self._reset_to_preset(self.configuration)
        else:
            self._reset_to_preset(self.configuration)
        self.execute(context)
        return context.window_manager.invoke_props_popup(self, event)

    def _apply_spec(self, context, bp):
        """Drive appliance width + config + panel type from the selected
        manufacturer model and stamp the spec for downstream consumers."""
        p = appliance_spec_registry.get_provider()
        if p is None:
            return
        try:
            spec = p.resolve(self.manufacturer, self.model)
        except Exception as e:
            print("HB5 appliance spec resolve failed: %s" % e)
            return
        cfg = spec.get('operator_config')
        if cfg:
            try:
                self.configuration = cfg
            except TypeError:
                pass
        ptype = spec.get('operator_panel_type')
        if ptype in {'A', 'B', 'C'}:
            self.panel_type = ptype
        dim_x = spec.get('appliance_dim_x_m')
        if dim_x:
            try:
                hb_types.GeoNodeCage(bp).set_input('Dim X', dim_x)
            except Exception:
                pass
        bp['APPLIANCE_PANEL_SPEC'] = json.dumps({
            'manufacturer': spec.get('manufacturer'),
            'model': spec.get('model'),
            'weight_max_lb': spec.get('weight_max_lb'),
            'panel_thickness': spec.get('panel_thickness'),
            'panels': spec.get('panels'),
            'flags': spec.get('flags'),
            'source_url': spec.get('source_url'),
        })

    def execute(self, context):
        bp = hb_utils.get_appliance_bp(context.object)
        if bp is None:
            return {'CANCELLED'}
        if (self.manufacturer not in ('MANUAL', '')
                and self.model not in ('NONE', '')
                and self.model != self.last_model):
            self._apply_spec(context, bp)
            self.last_model = self.model
        if self.configuration != self.last_config:
            self._reset_to_preset(self.configuration)
        sizes, holds, cwid, chold = self._gather(self.configuration)
        build_appliance_panels(bp, self.configuration, self.panel_type,
                               sizes, holds, cwid, chold)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        provider = appliance_spec_registry.get_provider()
        if provider is not None:
            layout.prop(self, 'manufacturer')
            if self.manufacturer not in ('MANUAL', ''):
                layout.prop(self, 'model')
                bp = hb_utils.get_appliance_bp(context.object)
                spec_json = bp.get('APPLIANCE_PANEL_SPEC') if bp else None
                if spec_json:
                    try:
                        sp = json.loads(spec_json)
                    except (ValueError, TypeError):
                        sp = None
                    if sp:
                        sbox = layout.box()
                        wmax = sp.get('weight_max_lb')
                        if wmax is not None:
                            sbox.label(text="Max panel weight: %g lb" % wmax)
                        for flag in (sp.get('flags') or []):
                            _draw_wrapped(sbox, flag, icon='ERROR')
                        url = sp.get('source_url')
                        if url:
                            sbox.operator("wm.url_open", text="Open spec sheet",
                                          icon='URL').url = url
        layout.prop(self, 'configuration')
        layout.prop(self, 'panel_type')

        bp = hb_utils.get_appliance_bp(context.object)
        config = self.configuration
        dim_x = dim_z = 0.0
        if bp is not None:
            cage = hb_types.GeoNodeCage(bp)
            dim_x = cage.get_input('Dim X')
            dim_z = cage.get_input('Dim Z')
        sizes, holds, cwid, chold = self._gather(config)
        ncol = _num_columns(config)
        solved_w = _solve(dim_x, chold, cwid) if dim_x else cwid

        box = layout.box()
        box.label(text="Fronts (hold to fix a size; others share the rest)")
        fronts = list(_iter_fronts(config))
        banner_fronts = [(g, lbl) for g, c, lbl, _s, _h in fronts if c is None]
        if banner_fronts and dim_z:
            banner_h, region_h, _ncf = _banner_split(config, dim_z, sizes, holds)
        else:
            banner_h, region_h = [], dim_z
        for ci in range(ncol):
            col_fronts = [(g, lbl) for g, c, lbl, _s, _h in fronts if c == ci]
            cbox = box.column(align=True)
            if ncol > 1:
                wrow = cbox.row(align=True)
                wf = wrow.row(align=True)
                wf.enabled = chold[ci]
                wf.prop(self, 'col_width_%d' % (ci + 1),
                        text="Column %d Width" % (ci + 1))
                if not chold[ci] and dim_x:
                    wrow.label(text="%.2f\"" % units.meter_to_inch(solved_w[ci]))
                wrow.prop(self, 'col_hold_%d' % (ci + 1), text="",
                          icon='LOCKED' if chold[ci] else 'UNLOCKED')
            idxs = [g for g, _l in col_fronts]
            if not dim_z:
                h_solved = [sizes[i] for i in idxs]
            elif banner_fronts:
                h_solved = _solve_region(region_h, [holds[i] for i in idxs],
                                         [sizes[i] for i in idxs])
            else:
                h_solved = _solve(dim_z, [holds[i] for i in idxs],
                                  [sizes[i] for i in idxs])
            for pos, (g, lbl) in enumerate(reversed(col_fronts)):
                k = len(col_fronts) - 1 - pos
                row = cbox.row(align=True)
                row.label(text=lbl)
                if holds[g]:
                    row.prop(self, 'size_%d' % (g + 1), text="")
                elif dim_z:
                    row.label(text="%.2f\"" % units.meter_to_inch(h_solved[k]))
                row.prop(self, 'hold_%d' % (g + 1), text="",
                         icon='LOCKED' if holds[g] else 'UNLOCKED')
        if banner_fronts:
            cbox = box.column(align=True)
            for bi, (g, lbl) in enumerate(banner_fronts):
                row = cbox.row(align=True)
                row.label(text="%s (full width)" % lbl)
                if holds[g]:
                    row.prop(self, 'size_%d' % (g + 1), text="")
                elif dim_z and banner_h:
                    row.label(text="%.2f\"" % units.meter_to_inch(banner_h[bi]))
                row.prop(self, 'hold_%d' % (g + 1), text="",
                         icon='LOCKED' if holds[g] else 'UNLOCKED')


classes = (
    hb_face_frame_OT_add_appliance_panels,
)

register, unregister = bpy.utils.register_classes_factory(classes)
