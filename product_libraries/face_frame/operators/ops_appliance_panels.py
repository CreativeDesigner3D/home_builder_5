import bpy
import json
from bpy.props import EnumProperty, IntProperty, StringProperty
from .... import hb_utils, hb_types, units, appliance_spec_registry
from .. import appliance_panels as ap

# --- Appliance panels: face-frame door-style panels on a panel-ready appliance.
# The data lives on the appliance root (Object.appliance_panels, see
# face_frame/appliance_panels.py): a list of panel sections per column with
# their own face / backer sizes, plus the appliance-level options. Every
# property edit rebuilds the parts, so this operator only picks a
# manufacturer spec / preset and draws the groups.


def _appliance_type(context):
    obj = context.object
    bp = hb_utils.get_appliance_bp(obj) if obj else None
    return bp.get('APPLIANCE_TYPE') if bp else None


def _config_enum_items(self, context):
    return ap.CONFIG_ITEMS.get(_appliance_type(context), ap.DEFAULT_CONFIG_ITEMS)


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
        layout.label(text=ln, icon=icon if i == 0 else 'BLANK1')


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


def _fmt(v):
    return "%.3f\"" % units.meter_to_inch(v)


def _open_in_viewport(context, bp):
    """Show the run in the viewport panel instead of this dialog, when
    that panel is switched on. True when it took the job.

    The panel draws the appliance front and is edited on the picture;
    this dialog is the same model as a list of rows. One command opens
    whichever the user has, so there is no second menu entry and no
    choice to make.
    """
    try:
        from ....operators import (scene_navigator, appliance_panel_tab,
                                   viewport_hud)
    except ImportError:
        return False
    if not viewport_hud.enabled() or appliance_panel_tab.target(context) is None:
        return False
    if appliance_panel_tab.TAB_KEY not in scene_navigator.available_tabs(
            context.scene):
        return False
    if not bp.appliance_panels.sections:
        ap.seed_preset(bp, appliance_panel_tab.default_config(bp),
                       keep_options=False)
        ap.rebuild(bp)
    appliance_panel_tab.select(bp, 0)
    scene_navigator.set_active_tab(appliance_panel_tab.TAB_KEY)
    scene_navigator.open_panel()
    appliance_panel_tab.tag_redraw()
    return True


# --- Layout editing: the add / remove / reorder buttons in the dialog.
# They edit the appliance's property groups straight off context.object, so
# the dialog just draws them; the model does the list bookkeeping (ordering,
# column re-indexing) and rebuilds.
class _Appliance_Panel_Edit:
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        bp = hb_utils.get_appliance_bp(obj) if obj else None
        return bool(bp and bp.appliance_panels.sections)

    def execute(self, context):
        bp = hb_utils.get_appliance_bp(context.object)
        if bp is None:
            return {'CANCELLED'}
        return {'FINISHED'} if self.edit(bp) else {'CANCELLED'}


class hb_face_frame_OT_appliance_panel_add_column(_Appliance_Panel_Edit,
                                                  bpy.types.Operator):
    bl_idname = "hb_face_frame.appliance_panel_add_column"
    bl_label = "Add Column"
    bl_description = ("Add a panel column on the right of the appliance, with "
                      "one door face in it")

    def edit(self, bp):
        if ap.add_column(bp) < 0:
            self.report({'INFO'}, "Panels are limited to %d columns"
                        % ap.MAX_COLUMNS)
            return False
        return True


class hb_face_frame_OT_appliance_panel_remove_column(_Appliance_Panel_Edit,
                                                     bpy.types.Operator):
    bl_idname = "hb_face_frame.appliance_panel_remove_column"
    bl_label = "Remove Column"
    bl_description = "Remove this column and every face in it"

    index: IntProperty(default=0)  # type: ignore

    def edit(self, bp):
        if not ap.remove_column(bp, self.index):
            self.report({'INFO'}, "The last column can't be removed")
            return False
        return True


class hb_face_frame_OT_appliance_panel_add_section(_Appliance_Panel_Edit,
                                                   bpy.types.Operator):
    bl_idname = "hb_face_frame.appliance_panel_add_section"
    bl_label = "Add Face"
    bl_description = "Add a panel face to this column"

    column: IntProperty(default=0)  # type: ignore
    kind: EnumProperty(items=ap.SECTION_KIND_ITEMS, default='DOOR')  # type: ignore
    where: EnumProperty(items=[('BOTTOM', "Bottom", "At the bottom of the stack"),
                               ('TOP', "Top", "On top of the stack")],
                        default='BOTTOM')  # type: ignore

    def edit(self, bp):
        return ap.add_section(bp, self.column, self.kind, self.where) >= 0


class hb_face_frame_OT_appliance_panel_remove_section(_Appliance_Panel_Edit,
                                                      bpy.types.Operator):
    bl_idname = "hb_face_frame.appliance_panel_remove_section"
    bl_label = "Remove Face"
    bl_description = "Remove this face"

    index: IntProperty(default=0)  # type: ignore

    def edit(self, bp):
        if not ap.remove_section(bp, self.index):
            self.report({'INFO'}, "A column keeps its last face - remove the "
                                  "column instead")
            return False
        return True


class hb_face_frame_OT_appliance_panel_move_section(_Appliance_Panel_Edit,
                                                    bpy.types.Operator):
    bl_idname = "hb_face_frame.appliance_panel_move_section"
    bl_label = "Move Face"
    bl_description = "Move this face up or down its stack"

    index: IntProperty(default=0)  # type: ignore
    delta: IntProperty(default=1)  # type: ignore

    def edit(self, bp):
        return ap.move_section(bp, self.index, self.delta)


class hb_face_frame_OT_add_appliance_panels(bpy.types.Operator):
    bl_idname = "hb_face_frame.add_appliance_panels"
    bl_label = "Appliance Panels"
    bl_description = "Add or edit door-style panels on a panel-ready appliance"
    # UNDO only, no REGISTER: the dialog edits ID data (the appliance's
    # property groups) live, and a redo-style popup would swap that data
    # out from under its buttons on every operator-property change.
    bl_options = {'UNDO'}

    manufacturer: EnumProperty(name="Manufacturer", items=_manufacturer_enum)  # type: ignore
    model: EnumProperty(name="Model", items=_model_enum)  # type: ignore
    last_model: StringProperty(default="")  # type: ignore
    configuration: EnumProperty(name="Configuration", items=_config_enum_items)  # type: ignore
    last_config: StringProperty(default="")  # type: ignore
    notes: StringProperty(default="")  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            bp = hb_utils.get_appliance_bp(obj)
            if bp:
                return bp.get('APPLIANCE_TYPE') in {'DISHWASHER', 'REFRIGERATOR',
                                                    'UNDER_COUNTER'}
        return False

    def invoke(self, context, event):
        bp = hb_utils.get_appliance_bp(context.object)
        props = bp.appliance_panels
        # Older files: rebuild the section list from the flat stamp once.
        ap.seed_from_legacy(bp)
        if _open_in_viewport(context, bp):
            # The viewport panel draws the run rather than listing it,
            # so the command opens THAT and there is no dialog. Without
            # the panel switched on, the dialog below is the whole UI.
            return {'FINISHED'}
        cfg = props.config or bp.get('APPLIANCE_PANEL_CONFIG')
        if cfg:
            try:
                self.configuration = cfg
            except TypeError:
                cfg = None
        if not props.sections:
            ap.seed_preset(bp, self.configuration, keep_options=False)
        self.last_config = self.configuration
        if props.manufacturer:
            try:
                self.manufacturer = props.manufacturer
                self.model = props.model
                self.last_model = props.model
            except TypeError:
                pass
        self.notes = ""
        ap.rebuild(bp)
        # Wide: each face row carries its kind, name, size, locks and the
        # reorder / remove buttons, side by side per column.
        return context.window_manager.invoke_props_dialog(self, width=700)

    def check(self, context):
        """Live-bound like the Set-* dialogs: react to the operator's own
        picks here (spec model / preset); the property-group fields
        rebuild through their own update callbacks."""
        bp = hb_utils.get_appliance_bp(context.object)
        if bp is None:
            return False
        if (self.manufacturer not in ('MANUAL', '')
                and self.model not in ('NONE', '')
                and self.model != self.last_model):
            self._apply_spec(context, bp)
            self.last_model = self.model
            ap.rebuild(bp)
        if self.configuration != self.last_config:
            ap.seed_preset(bp, self.configuration, keep_options=True)
            self.last_config = self.configuration
            ap.rebuild(bp)
        return True

    def _apply_spec(self, context, bp):
        """Fill the section model from the selected manufacturer model."""
        p = appliance_spec_registry.get_provider()
        if p is None:
            return
        try:
            spec = p.resolve(self.manufacturer, self.model)
        except Exception as e:
            print("HB5 appliance spec resolve failed: %s" % e)
            return
        notes = ap.apply_spec(bp, spec)
        cfg = spec.get('operator_config')
        if cfg:
            try:
                self.configuration = cfg
                self.last_config = cfg
            except TypeError:
                pass
        self.notes = json.dumps(notes)
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
        # Live-bound via check() and the property-group updates; OK just
        # confirms the state that is already built.
        bp = hb_utils.get_appliance_bp(context.object)
        if bp is None:
            return {'CANCELLED'}
        ap.rebuild(bp)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        bp = hb_utils.get_appliance_bp(context.object)
        if bp is None:
            return
        props = bp.appliance_panels
        # The buttons below can turn a preset layout into a hand-built one
        # (they mark the run CUSTOM). Follow that here so the dropdown names
        # what is actually there, and so picking the old preset again seeds
        # from scratch instead of reading as "no change".
        if props.config == ap.CUSTOM_CONFIG and self.configuration != ap.CUSTOM_CONFIG:
            self.configuration = ap.CUSTOM_CONFIG
            self.last_config = ap.CUSTOM_CONFIG
        provider = appliance_spec_registry.get_provider()
        if provider is not None:
            layout.prop(self, 'manufacturer')
            if self.manufacturer not in ('MANUAL', ''):
                layout.prop(self, 'model')
                if props.spec_url or props.weight_max_lb or self.notes:
                    sbox = layout.box()
                    if props.weight_max_lb:
                        sbox.label(text="Max panel weight: %g lb" % props.weight_max_lb)
                    try:
                        for flag in json.loads(self.notes or "[]"):
                            _draw_wrapped(sbox, flag, icon='ERROR')
                    except ValueError:
                        pass
                    if props.spec_url:
                        sbox.operator("wm.url_open", text="Open spec sheet",
                                      icon='URL').url = props.spec_url
        layout.prop(self, 'configuration')

        row = layout.row(align=True)
        row.prop(props, 'panel_type', text="Backer")
        row.prop(props, 'install_type', text="")

        cage = hb_types.GeoNodeCage(bp)
        dim_x = cage.get_input('Dim X') or 0.0
        dim_z = cage.get_input('Dim Z') or 0.0
        faces, backers, rails = ap.solve(props, dim_x, dim_z)

        opts = layout.box()
        r = opts.row(align=True)
        if bp.get('APPLIANCE_TYPE') in ap.KICK_APPLIANCE_TYPES:
            r.prop(props, 'toe_kick')
        r.prop(props, 'end_reveal')
        r.prop(props, 'section_gap')
        opts.prop(props, 'backer_reveal')

        rbox = layout.box()
        rbox.label(text="Full Inset Integral Rails")
        r = rbox.row(align=True)
        r.prop(props, 'rail_top')
        r.prop(props, 'rail_bottom')
        if any(sum(1 for s in props.sections if s.column == ci) > 1
               for ci in range(len(props.columns))):
            r.prop(props, 'rail_between')
        r = rbox.row()
        r.enabled = props.rail_top or props.rail_bottom or props.rail_between
        r.prop(props, 'rail_width')

        box = layout.box()
        hdr = box.row(align=True)
        hdr.label(text="Sections (hold to fix a size; others share the rest)")
        add_col = hdr.row(align=True)
        add_col.enabled = len(props.columns) < ap.MAX_COLUMNS
        add_col.operator("hb_face_frame.appliance_panel_add_column",
                         text="Add Column", icon='ADD')
        ncol = len(props.columns)
        secs = list(enumerate(props.sections))
        col_idx = [i for i, s in secs if 0 <= s.column < ncol]
        first_col = col_idx[0] if col_idx else len(secs)
        last_col = col_idx[-1] if col_idx else -1
        top_b = [(i, s) for i, s in secs if s.column < 0 and i > last_col]
        bottom_b = [(i, s) for i, s in secs if s.column < 0 and i < first_col]

        def _sec_row(container, i, s):
            rect = faces.get(i)
            # Face: what it is, what it's called, how tall, and where it
            # sits in its stack.
            r = container.row(align=True)
            r.prop(s, 'kind', text="", icon_only=True)
            r.prop(s, 'label', text="")
            if s.height_hold:
                r.prop(s, 'height', text="")
            elif rect is not None:
                r.label(text=_fmt(rect[3] - rect[2]))
            r.prop(s, 'height_hold', text="", icon='LOCKED' if s.height_hold else 'UNLOCKED')
            peers = ap.peer_indices(props, i)
            mv = r.row(align=True)
            mv.enabled = len(peers) > 1
            up = mv.operator("hb_face_frame.appliance_panel_move_section",
                             text="", icon='TRIA_UP')
            up.index, up.delta = i, 1
            dn = mv.operator("hb_face_frame.appliance_panel_move_section",
                             text="", icon='TRIA_DOWN')
            dn.index, dn.delta = i, -1
            rm = r.row(align=True)
            rm.enabled = len(props.sections) > 1 and (s.column < 0 or len(peers) > 1)
            rm.operator("hb_face_frame.appliance_panel_remove_section",
                        text="", icon='X').index = i
            # Backer + the pinned bottom: the fields a spec fills in.
            r2 = container.row(align=True)
            r2.label(text="", icon='BLANK1')
            if s.z_hold:
                r2.prop(s, 'z_bottom', text="")
            elif rect is not None:
                r2.label(text="@ " + _fmt(rect[2]))
            r2.prop(s, 'z_hold', text="", icon='LOCKED' if s.z_hold else 'UNLOCKED')
            r2.prop(s, 'backer', text="")
            b = backers.get(i)
            if b is not None:
                if s.backer_width_hold:
                    r2.prop(s, 'backer_width', text="W")
                else:
                    r2.label(text="W " + _fmt(b[1] - b[0]))
                r2.prop(s, 'backer_width_hold', text="",
                        icon='LOCKED' if s.backer_width_hold else 'UNLOCKED')
                if s.backer_height_hold:
                    r2.prop(s, 'backer_height', text="H")
                else:
                    r2.label(text="H " + _fmt(b[3] - b[2]))
                r2.prop(s, 'backer_height_hold', text="",
                        icon='LOCKED' if s.backer_height_hold else 'UNLOCKED')
            if s.spec_note:
                container.label(text="    " + s.spec_note, icon='INFO')

        def _add_face_row(container, column):
            """The three kinds, added to the bottom of this column's stack -
            where the buttons sit, so a drawer added under a door lands
            under it."""
            r = container.row(align=True)
            for kind, label in (('DOOR', "Door"), ('DRAWER', "Drawer"),
                                ('PANEL', "Panel")):
                op = r.operator("hb_face_frame.appliance_panel_add_section",
                                text="+ " + label)
                op.column, op.kind, op.where = column, kind, 'BOTTOM'

        for i, s in reversed(top_b):
            _sec_row(box.column(align=True), i, s)
        cols_row = box.row()
        for ci, col in enumerate(props.columns):
            cbox = cols_row.column(align=True)
            hr = cbox.row(align=True)
            if col.width_hold:
                hr.prop(col, 'width', text="Col %d" % (ci + 1))
            else:
                w = next((faces[i][1] - faces[i][0] for i, s in secs
                          if s.column == ci and i in faces), 0.0)
                hr.label(text="Col %d  %s" % (ci + 1, _fmt(w)))
            hr.prop(col, 'width_hold', text="",
                    icon='LOCKED' if col.width_hold else 'UNLOCKED')
            rc = hr.row(align=True)
            rc.enabled = ncol > 1
            rc.operator("hb_face_frame.appliance_panel_remove_column",
                        text="", icon='X').index = ci
            for i, s in reversed([(i, s) for i, s in secs if s.column == ci]):
                _sec_row(cbox, i, s)
            _add_face_row(cbox, ci)
        for i, s in reversed(bottom_b):
            _sec_row(box.column(align=True), i, s)
        # Full-width faces: a freezer drawer under the columns, a grille over
        # them. Kinds are just the usual starting point - the row picks.
        fw = box.row(align=True)
        fw.label(text="Full width:")
        op = fw.operator("hb_face_frame.appliance_panel_add_section",
                         text="Add Above", icon='TRIA_UP_BAR')
        op.column, op.kind, op.where = -1, 'PANEL', 'TOP'
        op = fw.operator("hb_face_frame.appliance_panel_add_section",
                         text="Add Below", icon='TRIA_DOWN_BAR')
        op.column, op.kind, op.where = -1, 'DRAWER', 'BOTTOM'


classes = (
    hb_face_frame_OT_appliance_panel_add_column,
    hb_face_frame_OT_appliance_panel_remove_column,
    hb_face_frame_OT_appliance_panel_add_section,
    hb_face_frame_OT_appliance_panel_remove_section,
    hb_face_frame_OT_appliance_panel_move_section,
    hb_face_frame_OT_add_appliance_panels,
)

register, unregister = bpy.utils.register_classes_factory(classes)
