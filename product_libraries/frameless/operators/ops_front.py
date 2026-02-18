import bpy
from .. import types_frameless
from .. import props_hb_frameless
from .... import hb_utils, units

class hb_frameless_OT_door_front_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.door_front_prompts"
    bl_label = "Front Prompts"
    bl_description = "Edit door/drawer front properties"
    bl_options = {'UNDO'}

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
            layout.prop(mod, '["' + node_input.identifier + '"]', text=text)

    def invoke(self, context, event):
        self.front = context.object
        self.door_style_mod = self.get_door_style_modifier(self.front)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def check(self, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        front = self.front
        if not front:
            return

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


classes = (
    hb_frameless_OT_door_front_prompts,
    hb_frameless_OT_delete_front,
)

register, unregister = bpy.utils.register_classes_factory(classes)
