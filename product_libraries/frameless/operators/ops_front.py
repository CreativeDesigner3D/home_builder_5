import bpy
from .. import types_frameless
from .. import solver_frameless
from .. import props_hb_frameless
from .. import edge_pulls
from .... import hb_utils, hb_project, units


_door_style_items = []


def _door_style_enum(self, context):
    """The room's door styles, by index."""
    _door_style_items.clear()
    styles = hb_project.get_main_scene().hb_frameless.door_styles
    for i, style in enumerate(styles):
        _door_style_items.append((str(i), style.name, ""))
    if not _door_style_items:
        _door_style_items.append(('0', "(none)", ""))
    return _door_style_items


def _front_insert(front):
    """The insert cage a front belongs to (a bi-fold's upper panel too)."""
    return front.parent if front is not None else None


class hb_frameless_OT_door_front_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.door_front_prompts"
    bl_label = "Front Prompts"
    bl_description = "Edit door/drawer front properties"
    bl_options = {'UNDO'}

    door_style: bpy.props.EnumProperty(
        name="Door Style", items=_door_style_enum,
        description="The door style this front wears") # type: ignore
    door_swing: bpy.props.EnumProperty(
        name="Hinge",
        items=[('0', "Left", "One door hinged on the left"),
               ('1', "Right", "One door hinged on the right"),
               ('2', "Double", "A pair of doors")],
        default='2') # type: ignore
    handle_type: bpy.props.EnumProperty(
        name="Handle",
        items=[('DEFAULT', "Room Default", "Follow the room's door or drawer handle")]
              + edge_pulls.HANDLE_TYPES,
        default='DEFAULT') # type: ignore

    front = None
    door_style_mod = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_CABINET_FRONT' in obj

    def get_door_style_modifier(self, obj):
        for mod in obj.modifiers:
            if mod.type == 'NODES' and 'Door Style' in mod.name:
                if mod.node_group and 'CPM_5PIECEDOOR' in mod.node_group.name:
                    return mod
        return None

    def draw_modifier_input(self, layout, mod, input_name, text):
        if input_name in mod.node_group.interface.items_tree:
            node_input = mod.node_group.interface.items_tree[input_name]
            ui_ref = hb_utils.gn_input_ui_ref(mod, node_input.identifier)
            if ui_ref is not None:
                layout.prop(ui_ref[0], ui_ref[1], text=text)

    def invoke(self, context, event):
        self.front = context.object
        self.door_style_mod = self.get_door_style_modifier(self.front)
        try:
            self.door_style = str(int(self.front.get('DOOR_STYLE_INDEX', 0)))
        except TypeError:
            pass
        insert = _front_insert(self.front)
        if insert is not None and 'Door Swing' in insert:
            self.door_swing = str(int(insert['Door Swing']))
        self.handle_type = self.front.get(edge_pulls.HANDLE_KEY, '') or 'DEFAULT'
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def apply_choices(self):
        """Write the style, hinge and handle picks where they live: the
        style and handle on the front, the hinge on its doors insert."""
        front = self.front
        styles = hb_project.get_main_scene().hb_frameless.door_styles
        index = int(self.door_style)
        if 0 <= index < len(styles) and index != int(front.get('DOOR_STYLE_INDEX', -1)):
            front['DOOR_STYLE_INDEX'] = index
            styles[index].assign_style_to_front(front)
            self.door_style_mod = self.get_door_style_modifier(front)
        insert = _front_insert(front)
        if insert is not None and 'Door Swing' in insert:
            insert['Door Swing'] = int(self.door_swing)
        if self.handle_type == 'DEFAULT':
            front.pop(edge_pulls.HANDLE_KEY, None)
        else:
            front[edge_pulls.HANDLE_KEY] = self.handle_type

    def tag_front(self):
        """5.2 modifier-input writes don't tag; rebuild the front. The
        pull is placed by the solver, so re-solve for the pull prompts."""
        if self.front:
            solver_frameless.recalculate_cabinet(self.front)
            self.front.update_tag()

    def check(self, context):
        self.apply_choices()
        self.tag_front()
        return True

    def execute(self, context):
        self.apply_choices()
        self.tag_front()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        front = self.front
        if not front:
            return

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Door Style:")
        row.prop(self, 'door_style', text="")
        insert = _front_insert(front)
        if insert is not None and 'Door Swing' in insert:
            row = col.row(align=True)
            row.label(text="Hinge:")
            row.prop(self, 'door_swing', text="")
        row = col.row(align=True)
        row.label(text="Handle:")
        row.prop(self, 'handle_type', text="")

        # Pull Location (doors and pullout fronts)
        if 'Pull Location' in front:
            box = layout.box()
            box.label(text="Pull Location")
            col = box.column(align=True)
            col.prop(front, '["Pull Location"]', text="Location")
            pull_loc = front.get('Pull Location', 0)
            if pull_loc == 0 and 'Base Pull Vertical Location' in front:
                col.prop(front, '["Base Pull Vertical Location"]', text="Vertical Location")
            elif pull_loc == 1 and 'Tall Pull Vertical Location' in front:
                col.prop(front, '["Tall Pull Vertical Location"]', text="Vertical Location")
            elif pull_loc == 2 and 'Upper Pull Vertical Location' in front:
                col.prop(front, '["Upper Pull Vertical Location"]', text="Vertical Location")
            if 'Handle Horizontal Location' in front:
                col.prop(front, '["Handle Horizontal Location"]', text="Horizontal Location")

        # 5-Piece Door Frame Properties
        mod = self.door_style_mod
        if mod and mod.node_group:
            box = layout.box()
            box.label(text="Frame Sizes")
            col = box.column(align=True)
            self.draw_modifier_input(col, mod, "Left Stile Width", "Left Stile")
            self.draw_modifier_input(col, mod, "Right Stile Width", "Right Stile")
            self.draw_modifier_input(col, mod, "Top Rail Width", "Top Rail")
            self.draw_modifier_input(col, mod, "Bottom Rail Width", "Bottom Rail")

            box = layout.box()
            box.label(text="Mid Rail")
            col = box.column(align=True)
            self.draw_modifier_input(col, mod, "Add Mid Rail", "Add Mid Rail")
            self.draw_modifier_input(col, mod, "Mid Rail Width", "Width")
            self.draw_modifier_input(col, mod, "Center Mid Rail", "Center Mid Rail")
            self.draw_modifier_input(col, mod, "Mid Rail Location", "Location")


class hb_frameless_OT_delete_front(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_front"
    bl_label = "Delete Front"
    bl_description = "Delete this door or drawer front"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_CABINET_FRONT' in obj

    def execute(self, context):
        front = context.object
        hb_utils.delete_obj_and_children(front)
        return {'FINISHED'}


class hb_frameless_OT_set_front_handle_type(bpy.types.Operator):
    """Set how the selected fronts are opened, or hand them back to the
    room's door / drawer default"""
    bl_idname = "hb_frameless.set_front_handle_type"
    bl_label = "Handle"
    bl_description = "Set how these fronts are opened"
    bl_options = {'UNDO'}

    handle_type: bpy.props.EnumProperty(
        name="Handle",
        items=[('DEFAULT', "Room Default", "Follow the room's door or drawer handle")]
              + edge_pulls.HANDLE_TYPES,
        default='DEFAULT') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.get('IS_CABINET_FRONT')

    def execute(self, context):
        fronts = {o for o in context.selected_objects if o.get('IS_CABINET_FRONT')}
        if context.object is not None and context.object.get('IS_CABINET_FRONT'):
            fronts.add(context.object)
        for front in fronts:
            if self.handle_type == 'DEFAULT':
                front.pop(edge_pulls.HANDLE_KEY, None)
            else:
                front[edge_pulls.HANDLE_KEY] = self.handle_type
        solver_frameless.solve_roots(list(fronts))
        return {'FINISHED'}


class hb_frameless_OT_toggle_front_lock(bpy.types.Operator):
    """Add or take off a lock on the selected fronts"""
    bl_idname = "hb_frameless.toggle_front_lock"
    bl_label = "Lock"
    bl_description = "Add or remove a lock on these fronts"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.get('IS_CABINET_FRONT')

    def execute(self, context):
        fronts = {o for o in context.selected_objects if o.get('IS_CABINET_FRONT')}
        fronts.add(context.object)
        on = not bool(context.object.get(edge_pulls.LOCK_KEY))
        for front in fronts:
            front[edge_pulls.LOCK_KEY] = on
        solver_frameless.solve_roots(list(fronts))
        return {'FINISHED'}


classes = (
    hb_frameless_OT_door_front_prompts,
    hb_frameless_OT_delete_front,
    hb_frameless_OT_set_front_handle_type,
    hb_frameless_OT_toggle_front_lock,
)

register, unregister = bpy.utils.register_classes_factory(classes)
