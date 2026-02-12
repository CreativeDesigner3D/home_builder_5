import bpy
from .... import hb_utils, hb_types, units


def get_product_bp(obj):
    """Walk up parent hierarchy to find the product base point."""
    if obj is None:
        return None
    if 'IS_FRAMELESS_PRODUCT_CAGE' in obj or 'IS_FRAMELESS_MISC_PART' in obj:
        return obj
    if obj.parent:
        return get_product_bp(obj.parent)
    return None


class hb_frameless_OT_product_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.product_prompts"
    bl_label = "Product Prompts"
    bl_description = "Edit product properties"
    bl_options = {'UNDO'}

    width: bpy.props.FloatProperty(name="Width", unit='LENGTH', precision=5)  # type: ignore
    height: bpy.props.FloatProperty(name="Height", unit='LENGTH', precision=5)  # type: ignore
    depth: bpy.props.FloatProperty(name="Depth", unit='LENGTH', precision=5)  # type: ignore

    product = None
    part_type = ""

    @classmethod
    def poll(cls, context):
        if context.object:
            return get_product_bp(context.object) is not None
        return False

    def invoke(self, context, event):
        product_bp = get_product_bp(context.object)
        self.part_type = product_bp.get('PART_TYPE', '')

        if product_bp.get('IS_FRAMELESS_MISC_PART'):
            self.product = hb_types.GeoNodeCutpart(product_bp)
            self.width = self.product.get_input('Length')
            self.height = self.product.get_input('Thickness')
            self.depth = self.product.get_input('Width')
        else:
            self.product = hb_types.GeoNodeCage(product_bp)
            self.width = self.product.get_input('Dim X')
            self.height = self.product.get_input('Dim Z')
            self.depth = self.product.get_input('Dim Y')

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def check(self, context):
        if self.product.obj.get('IS_FRAMELESS_MISC_PART'):
            self.product.set_input('Length', self.width)
            self.product.set_input('Thickness', self.height)
            self.product.set_input('Width', self.depth)
        else:
            self.product.set_input('Dim X', self.width)
            self.product.set_input('Dim Z', self.height)
            self.product.set_input('Dim Y', self.depth)
        hb_utils.run_calc_fix(context, self.product.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        obj = self.product.obj

        # --- Dimensions ---
        box = layout.box()
        box.label(text="Dimensions")
        col = box.column(align=True)

        row = col.row(align=True)
        row.label(text="Width:")
        row.prop(self, 'width', text="")

        row = col.row(align=True)
        row.label(text="Height:")
        row.prop(self, 'height', text="")

        row = col.row(align=True)
        row.label(text="Depth:")
        row.prop(self, 'depth', text="")

        # --- Product-specific properties ---
        if self.part_type == 'FLOATING_SHELF':
            self.draw_floating_shelf(layout, obj)
        elif self.part_type == 'VALANCE':
            self.draw_valance(layout, obj)
        elif self.part_type == 'SUPPORT_FRAME':
            self.draw_support_frame(layout, obj)
        elif self.part_type == 'HALF_WALL':
            self.draw_half_wall(layout, obj)
        elif self.part_type == 'LEG':
            self.draw_leg(layout, obj)
        elif self.part_type == 'UPPER_LEG':
            self.draw_upper_leg(layout, obj)

    def draw_floating_shelf(self, layout, obj):
        box = layout.box()
        box.label(text="Options")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Finish Left:")
        row.prop(obj, '["Finish Left"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Right:")
        row.prop(obj, '["Finish Right"]', text="")

        box = layout.box()
        box.label(text="LED Routing")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="LED Route Bottom:")
        row.prop(obj, '["Include LED Route Bottom"]', text="")
        row = col.row(align=True)
        row.label(text="LED Route Top:")
        row.prop(obj, '["Include LED Route Top"]', text="")

        row = col.row(align=True)
        row.label(text="LED Width Top:")
        row.prop(obj, '["LED Width Top"]', text="")
        row = col.row(align=True)
        row.label(text="LED Width Bottom:")
        row.prop(obj, '["LED Width Bottom"]', text="")
        row = col.row(align=True)
        row.label(text="LED Inset Top:")
        row.prop(obj, '["LED Inset Top"]', text="")
        row = col.row(align=True)
        row.label(text="LED Inset Bottom:")
        row.prop(obj, '["LED Inset Bottom"]', text="")
        row = col.row(align=True)
        row.label(text="LED Route Depth:")
        row.prop(obj, '["LED Route Depth"]', text="")

    def draw_valance(self, layout, obj):
        box = layout.box()
        box.label(text="Options")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Top Scribe Amount:")
        row.prop(obj, '["Top Scribe Amount"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Left:")
        row.prop(obj, '["Finish Left"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Right:")
        row.prop(obj, '["Finish Right"]', text="")
        row = col.row(align=True)
        row.label(text="Remove Cover:")
        row.prop(obj, '["Remove Cover"]', text="")
        row = col.row(align=True)
        row.label(text="Flush Bottom:")
        row.prop(obj, '["Flush Bottom"]', text="")

    def draw_support_frame(self, layout, obj):
        box = layout.box()
        box.label(text="Options")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Support Spacing:")
        row.prop(obj, '["Support Spacing"]', text="")

        box = layout.box()
        box.label(text="Legs")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Leg Width:")
        row.prop(obj, '["Leg Width"]', text="")
        row = col.row(align=True)
        row.label(text="Leg Depth:")
        row.prop(obj, '["Leg Depth"]', text="")
        row = col.row(align=True)
        row.label(text="Leg Height:")
        row.prop(obj, '["Leg Height"]', text="")

        col.separator()

        for corner in ('Front Left', 'Front Right', 'Back Left', 'Back Right'):
            row = col.row(align=True)
            row.label(text=f"{corner} Leg:")
            row.prop(obj, f'["{corner} Leg"]', text="")
            row.prop(obj, f'["{corner} Leg Type"]', text="")

    def draw_half_wall(self, layout, obj):
        box = layout.box()
        box.label(text="Construction")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Stud Thickness:")
        row.prop(obj, '["Stud Thickness"]', text="")
        row = col.row(align=True)
        row.label(text="Skin Thickness:")
        row.prop(obj, '["Skin Thickness"]', text="")
        row = col.row(align=True)
        row.label(text="Stud Spacing:")
        row.prop(obj, '["Stud Spacing"]', text="")
        row = col.row(align=True)
        row.label(text="End Stud From Edge:")
        row.prop(obj, '["End Stud From Edge"]', text="")

        box = layout.box()
        box.label(text="End Caps")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Left End Cap:")
        row.prop(obj, '["Left End Cap"]', text="")
        row = col.row(align=True)
        row.label(text="Right End Cap:")
        row.prop(obj, '["Right End Cap"]', text="")
        row = col.row(align=True)
        row.label(text="Finished End Setback:")
        row.prop(obj, '["Finished End Setback"]', text="")
        row = col.row(align=True)
        row.label(text="Left Finished Revel:")
        row.prop(obj, '["Left Finished Revel"]', text="")
        row = col.row(align=True)
        row.label(text="Right Finished Revel:")
        row.prop(obj, '["Right Finished Revel"]', text="")

        box = layout.box()
        box.label(text="Finish")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Finish Front:")
        row.prop(obj, '["Finish Front"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Back:")
        row.prop(obj, '["Finish Back"]', text="")

    def draw_leg(self, layout, obj):
        box = layout.box()
        box.label(text="Toe Kick")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Toe Kick Height:")
        row.prop(obj, '["Toe Kick Height"]', text="")
        row = col.row(align=True)
        row.label(text="Toe Kick Setback:")
        row.prop(obj, '["Toe Kick Setback"]', text="")

        box = layout.box()
        box.label(text="Options")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Override Left Panel Depth:")
        row.prop(obj, '["Override Left Panel Depth"]', text="")
        row = col.row(align=True)
        row.label(text="Override Right Panel Depth:")
        row.prop(obj, '["Override Right Panel Depth"]', text="")
        row = col.row(align=True)
        row.label(text="Only Include Filler:")
        row.prop(obj, '["Only Include Filler"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Type:")
        row.prop(obj, '["Finish Type"]', text="")


    def draw_upper_leg(self, layout, obj):
        box = layout.box()
        box.label(text="Options")
        col = box.column(align=True)
        row = col.row(align=True)
        row.label(text="Override Left Panel Depth:")
        row.prop(obj, '["Override Left Panel Depth"]', text="")
        row = col.row(align=True)
        row.label(text="Override Right Panel Depth:")
        row.prop(obj, '["Override Right Panel Depth"]', text="")
        row = col.row(align=True)
        row.label(text="Only Include Filler:")
        row.prop(obj, '["Only Include Filler"]', text="")
        row = col.row(align=True)
        row.label(text="Finish Type:")
        row.prop(obj, '["Finish Type"]', text="")


class hb_frameless_OT_delete_product(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_product"
    bl_label = "Delete Product"
    bl_description = "Delete this product"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object:
            return get_product_bp(context.object) is not None
        return False

    def execute(self, context):
        product_bp = get_product_bp(context.object)
        if product_bp:
            objs_to_delete = [product_bp] + list(product_bp.children_recursive)
            for obj in objs_to_delete:
                bpy.data.objects.remove(obj, do_unlink=True)
        return {'FINISHED'}


classes = (
    hb_frameless_OT_product_prompts,
    hb_frameless_OT_delete_product,
)

register, unregister = bpy.utils.register_classes_factory(classes)
