import bpy
import math
from .. import types_frameless
from .. import solver_frameless
from .. import props_hb_frameless
from .. import interior_items
from .... import hb_utils, hb_types, units
from ....units import inch


def get_default_shelf_quantity(opening_height, opening_depth):
    """Determine the default number of shelves based on opening height and depth.
    
    Args:
        opening_height: The interior opening height in meters.
        opening_depth: The interior opening depth in meters.
        
    Returns:
        Integer shelf count.
    """
    height_inches = opening_height / inch(1)
    depth_inches = opening_depth / inch(1)
    
    if depth_inches <= 18:
        if height_inches <= 20:
            return 1
        elif height_inches <= 32:
            return 2
        elif height_inches <= 44:
            return 3
        else:
            return 4
    else:
        if height_inches <= 28:
            return 1
        elif height_inches <= 40:
            return 2
        elif height_inches <= 52:
            return 3
        else:
            return 4


# ---------------------------------------------------------------------------
# Drawers: box construction and accessories
# ---------------------------------------------------------------------------
# The construction and slide lists, the accessory search and the list
# widgets come from the face frame library; the picks are stored on the
# frameless drawer opening in the same property group.

def _ff_ops():
    from ...face_frame.operators import ops_cabinet
    return ops_cabinet


def _construction_enum(self, context):
    return _ff_ops()._drawer_box_construction_enum(self, context)


def _slides_enum(self, context):
    return _ff_ops()._drawer_slides_enum(self, context)


def _pick_owner(name):
    """The drawer opening or items interior a pick is stored on."""
    obj = bpy.data.objects.get(name) if name else None
    if obj is None:
        return None
    if interior_items.is_items_interior(obj):
        return obj
    return interior_items.drawer_opening_for(obj)


def _update_dialog_construction(self, context):
    owner = _pick_owner(self.opening_name)
    if owner is not None:
        _ff_ops()._set_opening_construction(owner, self.construction)


def _update_dialog_slides(self, context):
    owner = _pick_owner(self.opening_name)
    if owner is not None:
        _ff_ops()._set_opening_slides(owner, self.slides)


def _seed_picks(op, owner):
    """Show the owner's current picks in the dialog's dropdowns. A code
    the host no longer offers stays on Project Default."""
    default = _ff_ops().DRAWER_BOX_CONSTRUCTION_DEFAULT
    props = owner.face_frame_opening
    for attr, code in (('construction', props.drawer_box_construction),
                       ('slides', props.drawer_slides)):
        try:
            setattr(op, attr, code or default)
        except TypeError:
            pass


def draw_box_picks(layout, op):
    """Construction and slide dropdowns, each only when the host offers
    options."""
    ff = _ff_ops()
    shown = False
    if ff.drawer_box_construction_options():
        layout.prop(op, 'construction')
        shown = True
    if ff.drawer_slides_options():
        layout.prop(op, 'slides')
        shown = True
    return shown


class hb_frameless_AccessorySearchRow(bpy.types.PropertyGroup):
    """One result row in the drawer accessory search."""
    code: bpy.props.StringProperty() # type: ignore
    label: bpy.props.StringProperty() # type: ignore
    name: bpy.props.StringProperty() # type: ignore
    section: bpy.props.StringProperty() # type: ignore
    group: bpy.props.StringProperty() # type: ignore
    render_kind: bpy.props.StringProperty() # type: ignore


def _populate_search(self, context):
    _ff_ops()._populate_drawer_accessory_search(self, context)


class hb_frameless_OT_drawer_add_accessory(bpy.types.Operator):
    bl_idname = "hb_frameless.drawer_add_accessory"
    bl_label = "Add"
    bl_description = "Add this accessory to the drawer"
    bl_options = {'UNDO', 'INTERNAL'}

    opening_name: bpy.props.StringProperty(options={'HIDDEN'}) # type: ignore
    code: bpy.props.StringProperty(options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        opening = interior_items.drawer_opening_for(
            bpy.data.objects.get(self.opening_name))
        if opening is None or not self.code:
            return {'CANCELLED'}
        if interior_items.add_drawer_accessory(opening, self.code) is None:
            self.report({'WARNING'}, "Unknown accessory")
            return {'CANCELLED'}
        hb_utils.run_calc_fix(context, opening)
        return {'FINISHED'}


class hb_frameless_OT_drawer_remove_accessory(bpy.types.Operator):
    bl_idname = "hb_frameless.drawer_remove_accessory"
    bl_label = "Remove"
    bl_description = "Remove the selected accessory from the drawer"
    bl_options = {'UNDO', 'INTERNAL'}

    opening_name: bpy.props.StringProperty(options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        opening = interior_items.drawer_opening_for(
            bpy.data.objects.get(self.opening_name))
        if opening is None:
            return {'CANCELLED'}
        props = interior_items.item_props(opening)
        idx = props.interior_items_index
        if not 0 <= idx < len(props.interior_items):
            return {'CANCELLED'}
        props.interior_items.remove(idx)
        props.interior_items_index = min(idx, max(len(props.interior_items) - 1, 0))
        hb_utils.run_calc_fix(context, opening)
        return {'FINISHED'}


class hb_frameless_OT_drawer_interior(bpy.types.Operator):
    """Lay out the inside of a drawer: box construction, slides and the
    accessories in the box."""
    bl_idname = "hb_frameless.drawer_interior"
    bl_label = "Drawer Interior"
    bl_description = "Pick this drawer's box construction and add the accessories that go inside it"
    bl_options = {'UNDO'}

    opening_name: bpy.props.StringProperty(options={'HIDDEN'}) # type: ignore
    filter_text: bpy.props.StringProperty(
        name="Search",
        description="Filter the accessory list by name, group or code",
        options={'TEXTEDIT_UPDATE'}, update=_populate_search) # type: ignore
    matches: bpy.props.CollectionProperty(type=hb_frameless_AccessorySearchRow) # type: ignore
    match_index: bpy.props.IntProperty(default=0) # type: ignore
    construction: bpy.props.EnumProperty(
        name="Box Construction", items=_construction_enum,
        description="Construction this drawer's box is built to",
        update=_update_dialog_construction) # type: ignore
    slides: bpy.props.EnumProperty(
        name="Slides", items=_slides_enum,
        description="Slide hardware this drawer runs on",
        update=_update_dialog_slides) # type: ignore

    @classmethod
    def poll(cls, context):
        return interior_items.drawer_opening_for(context.object) is not None

    def invoke(self, context, event):
        opening = interior_items.drawer_opening_for(context.object)
        if opening is None:
            return {'CANCELLED'}
        self.opening_name = opening.name
        # Open the drawer so the user can see what they're laying out.
        from . import op_open_mode
        if solver_frameless.open_amount(opening) < 0.5:
            op_open_mode.set_open_amount(opening, 1.0)
        _seed_picks(self, opening)
        self.filter_text = ""
        self.match_index = 0
        _populate_search(self, context)
        return context.window_manager.invoke_props_dialog(self, width=520)

    def check(self, context):
        _populate_search(self, context)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        opening = bpy.data.objects.get(self.opening_name)
        if opening is None:
            layout.label(text="No drawer selected", icon='INFO')
            return
        props = interior_items.item_props(opening)
        if draw_box_picks(layout, self):
            layout.separator()

        pick = layout.box()
        pick.label(text="Add an accessory", icon='ADD')
        pick.prop(self, 'filter_text', text="", icon='VIEWZOOM')
        if len(self.matches) == 0:
            pick.label(text="Nothing matches that search", icon='INFO')
        else:
            row = pick.row()
            row.template_list("HB_UL_face_frame_drawer_catalog", "",
                              self, "matches", self, "match_index", rows=6)
            side = row.column(align=True)
            add = side.operator("hb_frameless.drawer_add_accessory", text="",
                                icon='ADD')
            add.opening_name = self.opening_name
            idx = max(0, min(self.match_index, len(self.matches) - 1))
            add.code = self.matches[idx].code
            note = pick.row()
            note.enabled = False
            note.label(text="Marked accessories are drawn in the drawer; "
                            "the rest are listed only", icon='MESH_GRID')

        layout.separator()
        layout.label(text="In this drawer")
        row = layout.row()
        row.template_list("HB_UL_face_frame_drawer_items", "",
                          props, "interior_items", props,
                          "interior_items_index", rows=4)
        side = row.column(align=True)
        rem = side.operator("hb_frameless.drawer_remove_accessory", text="",
                            icon='REMOVE')
        rem.opening_name = self.opening_name

        idx = props.interior_items_index
        if not 0 <= idx < len(props.interior_items):
            layout.label(text="Add an accessory to get started", icon='INFO')
            return
        item = props.interior_items[idx]
        if item.kind != 'ACCESSORY':
            return
        from ...face_frame import ui_face_frame
        box = layout.box()
        box.label(text=item.accessory_label or item.accessory_code)
        box.prop(item, 'accessory_qty', text="Quantity")
        ui_face_frame.draw_drawer_insert_settings(box, item)


def update_shelf_quantities(context, cabinet_obj):
    """Find all shelf interiors in a cabinet and set their quantity based on opening height.
    
    Should be called after run_calc_fix so drivers have resolved.
    
    Args:
        context: Blender context
        cabinet_obj: The cabinet base point object
    """
    for obj in cabinet_obj.children_recursive:
        if 'IS_FRAMELESS_INTERIOR_CAGE' in obj and 'Shelf Quantity' in obj:
            interior = hb_types.GeoNodeCage(obj)
            try:
                opening_height = interior.get_input('Dim Z')
                opening_depth = interior.get_input('Dim Y')
                qty = get_default_shelf_quantity(opening_height, opening_depth)
                obj['Shelf Quantity'] = qty
            except (ValueError, KeyError):
                pass


class hb_frameless_OT_interior_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.interior_prompts"
    bl_label = "Interior Prompts"
    bl_description = "Edit interior properties"
    bl_options = {'UNDO'}

    shelf_quantity: bpy.props.IntProperty(name="Shelf Quantity", min=0, max=10, default=1) # type: ignore
    shelf_setback: bpy.props.FloatProperty(name="Shelf Setback", unit='LENGTH', precision=5) # type: ignore
    shelf_clip_gap: bpy.props.FloatProperty(name="Shelf Clip Gap", unit='LENGTH', precision=5) # type: ignore
    # Roll-out box construction and slides on an items interior.
    opening_name: bpy.props.StringProperty(options={'HIDDEN'}) # type: ignore
    construction: bpy.props.EnumProperty(
        name="Box Construction", items=_construction_enum,
        description="Construction the roll-out boxes are built to",
        update=_update_dialog_construction) # type: ignore
    slides: bpy.props.EnumProperty(
        name="Slides", items=_slides_enum,
        description="Slide hardware the roll-outs run on",
        update=_update_dialog_slides) # type: ignore

    interior = None

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def invoke(self, context, event):
        interior_bp = hb_utils.get_interior_bp(context.object)
        self.interior = hb_types.GeoNodeCage(interior_bp)
        
        if 'Shelf Quantity' in interior_bp:
            self.shelf_quantity = interior_bp['Shelf Quantity']
        if 'Shelf Setback' in interior_bp:
            self.shelf_setback = interior_bp['Shelf Setback']
        if 'Shelf Clip Gap' in interior_bp:
            self.shelf_clip_gap = interior_bp['Shelf Clip Gap']
        
        if interior_items.is_items_interior(interior_bp):
            self.opening_name = interior_bp.name
            _seed_picks(self, interior_bp)
        wm = context.window_manager
        width = 340 if interior_items.is_items_interior(interior_bp) else 300
        return wm.invoke_props_dialog(self, width=width)

    def check(self, context):
        if 'Shelf Quantity' in self.interior.obj:
            self.interior.obj['Shelf Quantity'] = self.shelf_quantity
        if 'Shelf Setback' in self.interior.obj:
            self.interior.obj['Shelf Setback'] = self.shelf_setback
        if 'Shelf Clip Gap' in self.interior.obj:
            self.interior.obj['Shelf Clip Gap'] = self.shelf_clip_gap
        hb_utils.run_calc_fix(context, self.interior.obj)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        if interior_items.is_items_interior(self.interior.obj):
            items = interior_items.item_props(self.interior.obj).interior_items
            if any(it.kind == 'ROLLOUT' for it in items):
                if draw_box_picks(layout, self):
                    layout.separator()
            draw_interior_items(layout, self.interior.obj)
            return
        box = layout.box()
        col = box.column(align=True)

        if 'Shelf Quantity' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Quantity:")
            row.prop(self, 'shelf_quantity', text="")
        
        if 'Shelf Setback' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Setback:")
            row.prop(self, 'shelf_setback', text="")
        
        if 'Shelf Clip Gap' in self.interior.obj:
            row = col.row(align=True)
            row.label(text="Shelf Clip Gap:")
            row.prop(self, 'shelf_clip_gap', text="")


class hb_frameless_OT_change_interior_type(bpy.types.Operator):
    bl_idname = "hb_frameless.change_interior_type"
    bl_label = "Change Interior Type"
    bl_description = "Change the interior configuration"
    bl_options = {'UNDO'}

    interior_type: bpy.props.EnumProperty(
        name="Interior Type",
        items=[
            ('SHELVES', "Shelves", "Standard adjustable shelves"),
            ('ROLLOUTS', "Roll-outs", "Drawer boxes on slides behind the front"),
            ('PULLOUT_SHELVES', "Roll-out Shelves", "Flat shelves on slides behind the front"),
            ('GLASS_SHELVES', "Glass Shelves", "Adjustable glass shelves"),
            ('CLOSET_ROD', "Closet Rod", "Hang rod across the opening"),
            ('TRAY_DIVIDERS', "Tray Dividers", "Vertical dividers for trays and cookie sheets"),
            ('EMPTY', "Empty", "No interior parts"),
            ('WINE_CUBBY', "Wine Storage Cubby", "Plywood cubbies sized to the opening"),
            ('WINE_CELLAR', "Wine Cellar Rack", "Hardwood grid of 4 in bottle openings"),
            ('WINE_LATTICE', "Lattice Wine Rack", "45 degree lattice"),
            ('WINE_X', "X-Style Wine Rack", "Two panels crossing corner to corner"),
            ('WINE_DIAGONAL', "Diagonal Wine Dividers", "Parallel 45 degree dividers"),
            ('WINE_HALF_CIRCLE', "Half Circle Wine Rack", "Scalloped rails"),
            ('STEMWARE_RACK', "Stemware Rack", "Slotted slats at the top of the opening"),
            ('PLATE_RACK', "Plate Rack", "Dowels on 2 in centers"),
        ],
        default='SHELVES'
    ) # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            return (_target_interior(obj) is not None
                    or interior_host(obj) is not None)
        return False

    def delete_interior_children(self, interior_obj):
        """Delete all children of the interior."""
        children = list(interior_obj.children)
        for child in children:
            self.delete_interior_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def add_interior_to_opening(self, opening_obj, interior):
        """Add an interior to an opening with proper drivers."""
        interior.create('Interior')
        interior.obj.parent = opening_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in opening_obj:
            opening = types_frameless.CabinetOpening(opening_obj)
        else:
            opening = types_frameless.CabinetBay(opening_obj)
        
        solver_frameless.attach_cage(interior.obj, opening.obj)

    def execute(self, context):
        interior_bp = _target_interior(context.object)
        if interior_bp:
            # Get parent opening before deleting
            parent_opening = self.get_parent_opening(interior_bp)
        else:
            # An opening with no interior yet gets one.
            parent_opening = interior_host(context.object)
        if not parent_opening:
            self.report({'ERROR'}, "Could not find parent opening")
            return {'CANCELLED'}

        # Delete the old interior
        if interior_bp:
            self.delete_interior_children(interior_bp)
            bpy.data.objects.remove(interior_bp, do_unlink=True)

        # Create new interior based on type
        if self.interior_type == 'SHELVES':
            interior = types_frameless.CabinetShelves()
            self.add_interior_to_opening(parent_opening, interior)
        elif self.interior_type in _ITEM_INTERIOR_KINDS:
            interior = types_frameless.CabinetInteriorItems()
            interior.seed_kind = _ITEM_INTERIOR_KINDS[self.interior_type]
            self.add_interior_to_opening(parent_opening, interior)
        elif self.interior_type == 'EMPTY':
            pass  # No interior needed
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}


class hb_frameless_OT_interior_part_prompts(bpy.types.Operator):
    bl_idname = "hb_frameless.interior_part_prompts"
    bl_label = "Interior Part Prompts"
    bl_description = "Edit interior part properties"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and 'IS_FRAMELESS_INTERIOR_PART' in obj

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def tag_part(self, context):
        """5.2 modifier-input writes don't tag; rebuild the part."""
        if context.object:
            context.object.update_tag()

    def check(self, context):
        self.tag_part(context)
        return True

    def execute(self, context):
        self.tag_part(context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        box = layout.box()
        box.label(text=f"Part: {obj.name}")
        
        # Show relevant properties from the object
        if obj.modifiers:
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group:
                    for input in mod.node_group.interface.items_tree:
                        if input.item_type == 'SOCKET' and input.in_out == 'INPUT':
                            ui_ref = hb_utils.gn_input_ui_ref(mod, input.identifier)
                            if ui_ref is not None:
                                box.prop(ui_ref[0], ui_ref[1], text=input.name)


class hb_frameless_OT_delete_interior_part(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_interior_part"
    bl_label = "Delete Interior Part"
    bl_description = "Delete this interior part"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        # Item parts are rebuilt from their interior's item list; they
        # are removed there, not one part at a time.
        return (obj and 'IS_FRAMELESS_INTERIOR_PART' in obj
                and not obj.get(interior_items.PART_TAG)
                and not obj.get(interior_items.DRAWER_INSERT_TAG))

    def execute(self, context):
        obj = context.object
        hb_utils.delete_obj_and_children(obj)
        return {'FINISHED'}


class hb_frameless_OT_custom_interior_vertical(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_interior_vertical"
    bl_label = "Custom Vertical Interior Division"
    bl_description = "Create custom vertical interior divisions with adjustable sizes"
    bl_options = {'UNDO'}

    section_count: bpy.props.IntProperty(
        name="Number of Sections",
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_section_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_5_type: bpy.props.EnumProperty(name="Section 5", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_6_type: bpy.props.EnumProperty(name="Section 6", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_7_type: bpy.props.EnumProperty(name="Section 7", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_8_type: bpy.props.EnumProperty(name="Section 8", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_9_type: bpy.props.EnumProperty(name="Section 9", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_10_type: bpy.props.EnumProperty(name="Section 10", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent interior
        self.delete_children(parent_obj)
        
        # Remove the old interior object
        parent_opening = self.get_parent_opening(parent_obj)
        if parent_obj and parent_obj.name in bpy.data.objects:
            bpy.data.objects.remove(parent_obj, do_unlink=True)
        
        if not parent_opening:
            return None
        
        # Create empty splitter (no section types yet - just for sizing)
        splitter = types_frameless.InteriorSplitterVertical()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = [0] * self.section_count
        splitter.section_types = ['EMPTY'] * self.section_count  # Empty for preview
        splitter.create()
        
        # Parent to opening and set up dimension drivers
        splitter.obj.parent = parent_opening
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_opening:
            opening = types_frameless.CabinetOpening(parent_opening)
        else:
            opening = types_frameless.CabinetBay(parent_opening)
            
        solver_frameless.attach_cage(splitter.obj, opening.obj)
        
        self.splitter_obj_name = splitter.obj.name
        self.parent_obj_name = parent_opening.name
        self.previous_section_count = self.section_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find interior
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # Create initial splitter (replaces old interior)
        self.create_splitter(context, interior_bp)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If section count changed, recreate the splitter
        if self.section_count != self.previous_section_count:
            # Get current splitter and delete it
            splitter_obj = self.get_splitter_obj()
            if splitter_obj:
                self.delete_children(splitter_obj)
                bpy.data.objects.remove(splitter_obj, do_unlink=True)
            
            # Create new splitter directly in the opening
            splitter = types_frameless.InteriorSplitterVertical()
            splitter.splitter_qty = self.section_count - 1
            splitter.section_sizes = [0] * self.section_count
            splitter.section_types = ['EMPTY'] * self.section_count
            splitter.create()
            
            splitter.obj.parent = parent_obj
            
            if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
                opening = types_frameless.CabinetOpening(parent_obj)
            else:
                opening = types_frameless.CabinetBay(parent_obj)
                
            solver_frameless.attach_cage(splitter.obj, opening.obj)
            
            self.splitter_obj_name = splitter.obj.name
            self.previous_section_count = self.section_count
            
            cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        section_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    section_sizes.append(0)
                else:
                    section_sizes.append(prompt.distance_value)
        
        # Delete existing splitter and create final one with section types
        self.delete_children(splitter_obj)
        bpy.data.objects.remove(splitter_obj, do_unlink=True)
        
        type_props = [
            self.section_1_type, self.section_2_type, self.section_3_type,
            self.section_4_type, self.section_5_type, self.section_6_type,
            self.section_7_type, self.section_8_type, self.section_9_type,
            self.section_10_type
        ]
        
        section_types = []
        for i in range(self.section_count):
            section_types.append(type_props[i])
        
        # Create final splitter with section types
        splitter = types_frameless.InteriorSplitterVertical()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = section_sizes
        splitter.section_types = section_types
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
            opening = types_frameless.CabinetOpening(parent_obj)
        else:
            opening = types_frameless.CabinetBay(parent_obj)
            
        solver_frameless.attach_cage(splitter.obj, opening.obj)
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Section heights from calculator
        box = layout.box()
        box.label(text="Section Heights:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Section types
        box = layout.box()
        box.label(text="Section Types:", icon='MESH_PLANE')
        
        type_props = [
            'section_1_type', 'section_2_type', 'section_3_type',
            'section_4_type', 'section_5_type', 'section_6_type',
            'section_7_type', 'section_8_type', 'section_9_type',
            'section_10_type'
        ]
        
        col = box.column(align=True)
        for i in range(self.section_count):
            row = col.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, type_props[i], text="")


class hb_frameless_OT_custom_interior_horizontal(bpy.types.Operator):
    bl_idname = "hb_frameless.custom_interior_horizontal"
    bl_label = "Custom Horizontal Interior Division"
    bl_description = "Create custom horizontal interior divisions with adjustable sizes"
    bl_options = {'UNDO'}

    section_count: bpy.props.IntProperty(
        name="Number of Sections",
        min=2, max=10,
        default=2
    ) # type: ignore
    
    previous_section_count: bpy.props.IntProperty(default=0) # type: ignore
    splitter_obj_name: bpy.props.StringProperty(name="Splitter Object") # type: ignore
    parent_obj_name: bpy.props.StringProperty(name="Parent Object") # type: ignore

    # Section types
    section_1_type: bpy.props.EnumProperty(name="Section 1", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_2_type: bpy.props.EnumProperty(name="Section 2", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_3_type: bpy.props.EnumProperty(name="Section 3", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_4_type: bpy.props.EnumProperty(name="Section 4", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_5_type: bpy.props.EnumProperty(name="Section 5", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_6_type: bpy.props.EnumProperty(name="Section 6", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_7_type: bpy.props.EnumProperty(name="Section 7", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_8_type: bpy.props.EnumProperty(name="Section 8", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_9_type: bpy.props.EnumProperty(name="Section 9", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore
    section_10_type: bpy.props.EnumProperty(name="Section 10", items=[('SHELVES', "Shelves", ""), ('EMPTY', "Empty", "")], default='SHELVES') # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            interior_bp = hb_utils.get_interior_bp(obj)
            return interior_bp is not None
        return False

    def delete_children(self, obj):
        """Delete all children of the object."""
        children = list(obj.children)
        for child in children:
            self.delete_children(child)
            bpy.data.objects.remove(child, do_unlink=True)

    def get_splitter_obj(self):
        """Get the splitter object by name."""
        if self.splitter_obj_name and self.splitter_obj_name in bpy.data.objects:
            return bpy.data.objects[self.splitter_obj_name]
        return None

    def get_parent_obj(self):
        """Get the parent object by name."""
        if self.parent_obj_name and self.parent_obj_name in bpy.data.objects:
            return bpy.data.objects[self.parent_obj_name]
        return None

    def get_parent_opening(self, interior_obj):
        """Get the parent opening of the interior."""
        parent = interior_obj.parent
        while parent:
            if 'IS_FRAMELESS_OPENING_CAGE' in parent or 'IS_FRAMELESS_BAY_CAGE' in parent:
                return parent
            parent = parent.parent
        return None

    def create_splitter(self, context, parent_obj):
        """Create or recreate the splitter with current settings."""
        # Delete existing children of parent interior
        self.delete_children(parent_obj)
        
        # Remove the old interior object
        parent_opening = self.get_parent_opening(parent_obj)
        if parent_obj and parent_obj.name in bpy.data.objects:
            bpy.data.objects.remove(parent_obj, do_unlink=True)
        
        if not parent_opening:
            return None
        
        # Create empty splitter
        splitter = types_frameless.InteriorSplitterHorizontal()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = [0] * self.section_count
        splitter.section_types = ['EMPTY'] * self.section_count
        splitter.create()
        
        # Parent to opening and set up dimension drivers
        splitter.obj.parent = parent_opening
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_opening:
            opening = types_frameless.CabinetOpening(parent_opening)
        else:
            opening = types_frameless.CabinetBay(parent_opening)
            
        solver_frameless.attach_cage(splitter.obj, opening.obj)
        
        self.splitter_obj_name = splitter.obj.name
        self.parent_obj_name = parent_opening.name
        self.previous_section_count = self.section_count
        
        # Run calc fix
        cabinet_bp = hb_utils.get_cabinet_bp(parent_opening)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return splitter.obj

    def invoke(self, context, event):
        # Find interior
        interior_bp = hb_utils.get_interior_bp(context.object)
        if not interior_bp:
            self.report({'ERROR'}, "Could not find interior")
            return {'CANCELLED'}
        
        # Create initial splitter (replaces old interior)
        self.create_splitter(context, interior_bp)
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def check(self, context):
        parent_obj = self.get_parent_obj()
        if not parent_obj:
            return False
        
        # If section count changed, recreate the splitter
        if self.section_count != self.previous_section_count:
            splitter_obj = self.get_splitter_obj()
            if splitter_obj:
                self.delete_children(splitter_obj)
                bpy.data.objects.remove(splitter_obj, do_unlink=True)
            
            splitter = types_frameless.InteriorSplitterHorizontal()
            splitter.splitter_qty = self.section_count - 1
            splitter.section_sizes = [0] * self.section_count
            splitter.section_types = ['EMPTY'] * self.section_count
            splitter.create()
            
            splitter.obj.parent = parent_obj
            
            if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
                opening = types_frameless.CabinetOpening(parent_obj)
            else:
                opening = types_frameless.CabinetBay(parent_obj)
                
            solver_frameless.attach_cage(splitter.obj, opening.obj)
            
            self.splitter_obj_name = splitter.obj.name
            self.previous_section_count = self.section_count
            
            cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
            return True
        
        # Otherwise just recalculate
        splitter_obj = self.get_splitter_obj()
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                calculator.calculate()
            
            cabinet_bp = hb_utils.get_cabinet_bp(splitter_obj)
            if cabinet_bp:
                hb_utils.run_calc_fix(context, cabinet_bp)
        
        return True

    def execute(self, context):
        parent_obj = self.get_parent_obj()
        splitter_obj = self.get_splitter_obj()
        
        if not parent_obj or not splitter_obj:
            self.report({'ERROR'}, "Could not find objects")
            return {'CANCELLED'}
        
        # Get the current calculator values before recreating
        section_sizes = []
        for calculator in splitter_obj.home_builder.calculators:
            for prompt in calculator.prompts:
                if prompt.equal:
                    section_sizes.append(0)
                else:
                    section_sizes.append(prompt.distance_value)
        
        # Delete existing splitter and create final one with section types
        self.delete_children(splitter_obj)
        bpy.data.objects.remove(splitter_obj, do_unlink=True)
        
        type_props = [
            self.section_1_type, self.section_2_type, self.section_3_type,
            self.section_4_type, self.section_5_type, self.section_6_type,
            self.section_7_type, self.section_8_type, self.section_9_type,
            self.section_10_type
        ]
        
        section_types = []
        for i in range(self.section_count):
            section_types.append(type_props[i])
        
        # Create final splitter with section types
        splitter = types_frameless.InteriorSplitterHorizontal()
        splitter.splitter_qty = self.section_count - 1
        splitter.section_sizes = section_sizes
        splitter.section_types = section_types
        splitter.create()
        
        # Parent and set up drivers
        splitter.obj.parent = parent_obj
        
        if 'IS_FRAMELESS_OPENING_CAGE' in parent_obj:
            opening = types_frameless.CabinetOpening(parent_obj)
        else:
            opening = types_frameless.CabinetBay(parent_obj)
            
        solver_frameless.attach_cage(splitter.obj, opening.obj)
        
        # Run calc fix and update shelf quantities
        cabinet_bp = hb_utils.get_cabinet_bp(parent_obj)
        if cabinet_bp:
            hb_utils.run_calc_fix(context, cabinet_bp)
            update_shelf_quantities(context, cabinet_bp)
            hb_utils.run_calc_fix(context, cabinet_bp)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'section_count')
        
        splitter_obj = self.get_splitter_obj()
        
        # Section widths from calculator
        box = layout.box()
        box.label(text="Section Widths:", icon='SNAP_GRID')
        
        if splitter_obj:
            for calculator in splitter_obj.home_builder.calculators:
                col = box.column(align=True)
                for prompt in calculator.prompts:
                    row = col.row(align=True)
                    row.active = not prompt.equal
                    row.prop(prompt, 'distance_value', text=prompt.name)
                    row.prop(prompt, 'equal', text="", icon='LINKED' if prompt.equal else 'UNLINKED')
        
        # Section types
        box = layout.box()
        box.label(text="Section Types:", icon='MESH_PLANE')
        
        type_props = [
            'section_1_type', 'section_2_type', 'section_3_type',
            'section_4_type', 'section_5_type', 'section_6_type',
            'section_7_type', 'section_8_type', 'section_9_type',
            'section_10_type'
        ]
        
        col = box.column(align=True)
        for i in range(self.section_count):
            row = col.row(align=True)
            row.label(text=f"Section {i+1}:")
            row.prop(self, type_props[i], text="")


class hb_frameless_OT_calculate_shelf_quantity(bpy.types.Operator):
    """Calculate default shelf quantity based on opening height"""
    bl_idname = "hb_frameless.calculate_shelf_quantity"
    bl_label = "Calculate Shelf Quantity"
    bl_description = "Set shelf quantities based on opening heights"
    bl_options = {'UNDO'}

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name", default="") # type: ignore

    def execute(self, context):
        if self.cabinet_name and self.cabinet_name in bpy.data.objects:
            cabinet_obj = bpy.data.objects[self.cabinet_name]
        elif context.object:
            cabinet_obj = hb_utils.get_cabinet_bp(context.object)
        else:
            return {'CANCELLED'}

        if cabinet_obj:
            update_shelf_quantities(context, cabinet_obj)
            hb_utils.run_calc_fix(context, cabinet_obj)

        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Interior items (roll-outs, roll-out shelves, tray dividers, shelves)
# ---------------------------------------------------------------------------

# Change Interior choices that build an items interior, and the item
# each one starts with.
_ITEM_INTERIOR_KINDS = {
    'ROLLOUTS': 'ROLLOUT',
    'PULLOUT_SHELVES': 'PULLOUT_SHELF',
    'GLASS_SHELVES': 'GLASS_SHELF',
    'CLOSET_ROD': 'CLOSET_ROD',
    'TRAY_DIVIDERS': 'TRAY_DIVIDERS',
}
_ITEM_INTERIOR_KINDS.update(
    {kind: kind for kind in interior_items.BAR_STORAGE_KINDS})

_ITEM_KIND_ITEMS = [
    ('ROLLOUT', "Roll-outs", "Stack of drawer boxes on slides"),
    ('PULLOUT_SHELF', "Roll-out Shelves", "Stack of flat shelves on slides"),
    ('TRAY_DIVIDERS', "Tray Dividers", "Vertical dividers, optionally with a locked shelf above"),
    ('ADJUSTABLE_SHELF', "Adjustable Shelves", "Evenly spaced shelves on shelf pins"),
    ('GLASS_SHELF', "Glass Shelves", "Adjustable glass shelves"),
    ('CLOSET_ROD', "Closet Rod", "Hang rod across the opening, set down from the top"),
    ('WINE_CUBBY', "Wine Storage Cubby", "Plywood cubbies sized to the opening"),
    ('WINE_CELLAR', "Wine Cellar Rack", "Hardwood grid of 4 in bottle openings"),
    ('WINE_LATTICE', "Lattice Wine Rack", "45 degree lattice"),
    ('WINE_X', "X-Style Wine Rack", "Two panels crossing corner to corner"),
    ('WINE_DIAGONAL', "Diagonal Wine Dividers", "Parallel 45 degree dividers"),
    ('WINE_HALF_CIRCLE', "Half Circle Wine Rack", "Scalloped rails"),
    ('STEMWARE_RACK', "Stemware Rack", "Slotted slats at the top of the opening"),
    ('PLATE_RACK', "Plate Rack", "Dowels on 2 in centers"),
]
_ITEM_KIND_LABELS = {key: label for key, label, _desc in _ITEM_KIND_ITEMS}


def interior_host(obj):
    """The door or open opening at or above ``obj`` that can take an
    interior but has none, or None. Drawers, pullouts and split openings
    don't take one."""
    while obj is not None:
        if obj.get('IS_FRAMELESS_OPENING_CAGE') or obj.get('IS_FRAMELESS_BAY_CAGE'):
            break
        obj = obj.parent
    if obj is None:
        return None
    for child in obj.children:
        if (child.get('IS_FRAMELESS_INTERIOR_CAGE')
                or solver_frameless.is_cage_link(child)
                or child.get('IS_DRAWER_FRONT')
                or child.get('IS_PULLOUT_FRONT')):
            return None
    if 'Door Swing' in obj:
        return obj
    if not any(c.get('IS_CABINET_FRONT') for c in obj.children):
        return obj
    return None


def _target_interior(obj):
    """The interior at or above ``obj``, or the one directly inside the
    opening ``obj`` when the opening itself was picked."""
    interior = hb_utils.get_interior_bp(obj)
    if interior is None and obj is not None:
        interior = next((c for c in obj.children
                         if c.get('IS_FRAMELESS_INTERIOR_CAGE')), None)
    return interior


def _items_interior(name):
    obj = bpy.data.objects.get(name) if name else None
    return obj if interior_items.is_items_interior(obj) else None


def draw_interior_items(layout, interior_obj):
    """Item list with per-kind settings, laid out as the face frame
    library lays out the same items."""
    props = interior_items.item_props(interior_obj)
    name = interior_obj.name
    row = layout.row()
    row.label(text="Interior Items")
    row.operator_menu_enum("hb_frameless.add_interior_item", "kind",
                           text="Add", icon='ADD').interior_name = name
    if not props.interior_items:
        layout.label(text="(none)")
        return
    box = layout.box()
    for i, item in enumerate(props.interior_items):
        sub = box.column(align=True)
        header = sub.row(align=True)
        header.label(text=_ITEM_KIND_LABELS.get(item.kind, item.kind))
        rm = header.operator("hb_frameless.remove_interior_item", text="",
                             icon='X')
        rm.interior_name = name
        rm.index = i
        if item.kind in ('ADJUSTABLE_SHELF', 'GLASS_SHELF'):
            qty_row = sub.row(align=True)
            field = qty_row.row(align=True)
            field.enabled = item.unlock_shelf_qty
            field.prop(item, 'shelf_qty', text="Qty")
            lock_icon = 'UNLOCKED' if item.unlock_shelf_qty else 'LOCKED'
            qty_row.prop(item, 'unlock_shelf_qty', text="", icon=lock_icon)
            sub.prop(item, 'shelf_setback', text="Setback")
            sub.prop(item, 'bottom_offset', text="From Bottom")
        elif item.kind == 'PULLOUT_SHELF':
            sub.prop(item, 'qty', text="Qty")
            sub.prop(item, 'pullout_thickness', text="Thickness")
            sub.prop(item, 'distance_between', text="Gap Between")
            sub.prop(item, 'bottom_gap', text="Bottom Gap")
            sub.prop(item, 'item_setback', text="Front Setback")
            sub.prop(item, 'hide_rollout_spacers', text="Hide Spacer Ladders")
            lh = sub.row()
            lh.enabled = not item.hide_rollout_spacers
            lh.prop(item, 'rollout_spacer_height', text="Ladder Height (0 = Full)")
        elif item.kind == 'ROLLOUT':
            for j, rollout_box in enumerate(item.rollout_boxes):
                brow = sub.row(align=True)
                brow.label(text=f"Box {j + 1}")
                brow.prop(rollout_box, 'height_preset', text="")
                if rollout_box.height_preset == 'CUSTOM':
                    brow.prop(rollout_box, 'height', text="")
                rm_box = brow.operator("hb_frameless.remove_rollout_box",
                                       text="", icon='X')
                rm_box.interior_name = name
                rm_box.item_index = i
                rm_box.box_index = j
            add_box = sub.operator("hb_frameless.add_rollout_box",
                                   text="Add Box", icon='ADD')
            add_box.interior_name = name
            add_box.item_index = i
            sub.prop(item, 'distance_between', text="Gap Between")
            sub.prop(item, 'bottom_gap', text="Bottom Gap")
            sub.prop(item, 'item_setback', text="Front Setback")
            sub.prop(item, 'rollout_depth', text="Depth (0 = Auto)")
            sub.prop(item, 'hide_rollout_spacers', text="Hide Spacer Ladders")
            lh = sub.row()
            lh.enabled = not item.hide_rollout_spacers
            lh.prop(item, 'rollout_spacer_height', text="Ladder Height (0 = Full)")
            sub.prop(item, 'finger_scoop', text="Finger Scoop")
        elif item.kind == 'TRAY_DIVIDERS':
            sub.prop(item, 'tray_qty', text="Qty")
            sub.prop(item, 'tray_remove_shelf', text="Remove Locked Shelf")
            shelf_row = sub.row()
            shelf_row.enabled = not item.tray_remove_shelf
            shelf_row.prop(item, 'tray_opening_height', text="Opening Height")
            sub.prop(item, 'tray_divider_thickness', text="Divider Thickness")
            sub.prop(item, 'tray_setback', text="Setback")
            sub.prop(item, 'bottom_offset', text="From Bottom")
        elif item.kind == 'CLOSET_ROD':
            sub.prop(item, 'rod_distance_from_top', text="Distance From Top")
        elif item.kind in interior_items.BAR_STORAGE_KINDS:
            sub.label(text="Sized to the opening", icon='INFO')
        else:
            sub.label(text="Not built in frameless cabinets", icon='INFO')
        if i < len(props.interior_items) - 1:
            box.separator()


class hb_frameless_OT_add_interior_item(bpy.types.Operator):
    bl_idname = "hb_frameless.add_interior_item"
    bl_label = "Add Interior Item"
    bl_description = "Add an interior item to this interior"
    bl_options = {'UNDO'}

    kind: bpy.props.EnumProperty(name="Kind", items=_ITEM_KIND_ITEMS,
                                 default='ROLLOUT') # type: ignore
    interior_name: bpy.props.StringProperty(name="Interior Name") # type: ignore

    def execute(self, context):
        interior_obj = _items_interior(self.interior_name)
        if interior_obj is None:
            self.report({'WARNING'}, "Could not find the interior")
            return {'CANCELLED'}
        interior_items.add_item(interior_obj, self.kind)
        hb_utils.run_calc_fix(context, interior_obj)
        return {'FINISHED'}


class hb_frameless_OT_remove_interior_item(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_interior_item"
    bl_label = "Remove Interior Item"
    bl_description = "Remove this interior item"
    bl_options = {'UNDO'}

    index: bpy.props.IntProperty(name="Index", default=-1) # type: ignore
    interior_name: bpy.props.StringProperty(name="Interior Name") # type: ignore

    def execute(self, context):
        interior_obj = _items_interior(self.interior_name)
        if interior_obj is None:
            return {'CANCELLED'}
        props = interior_items.item_props(interior_obj)
        if not 0 <= self.index < len(props.interior_items):
            return {'CANCELLED'}
        props.interior_items.remove(self.index)
        props.interior_items_index = min(props.interior_items_index,
                                         max(len(props.interior_items) - 1, 0))
        hb_utils.run_calc_fix(context, interior_obj)
        return {'FINISHED'}


class hb_frameless_OT_add_rollout_box(bpy.types.Operator):
    bl_idname = "hb_frameless.add_rollout_box"
    bl_label = "Add Roll-out Box"
    bl_description = "Add a box to this roll-out stack"
    bl_options = {'UNDO'}

    item_index: bpy.props.IntProperty(name="Item Index", default=-1) # type: ignore
    interior_name: bpy.props.StringProperty(name="Interior Name") # type: ignore

    def execute(self, context):
        interior_obj = _items_interior(self.interior_name)
        if interior_obj is None:
            return {'CANCELLED'}
        props = interior_items.item_props(interior_obj)
        if not 0 <= self.item_index < len(props.interior_items):
            return {'CANCELLED'}
        props.interior_items[self.item_index].rollout_boxes.add()
        hb_utils.run_calc_fix(context, interior_obj)
        return {'FINISHED'}


class hb_frameless_OT_remove_rollout_box(bpy.types.Operator):
    bl_idname = "hb_frameless.remove_rollout_box"
    bl_label = "Remove Roll-out Box"
    bl_description = "Remove this box from the roll-out stack"
    bl_options = {'UNDO'}

    item_index: bpy.props.IntProperty(name="Item Index", default=-1) # type: ignore
    box_index: bpy.props.IntProperty(name="Box Index", default=-1) # type: ignore
    interior_name: bpy.props.StringProperty(name="Interior Name") # type: ignore

    def execute(self, context):
        interior_obj = _items_interior(self.interior_name)
        if interior_obj is None:
            return {'CANCELLED'}
        props = interior_items.item_props(interior_obj)
        if not 0 <= self.item_index < len(props.interior_items):
            return {'CANCELLED'}
        boxes = props.interior_items[self.item_index].rollout_boxes
        if not 0 <= self.box_index < len(boxes):
            return {'CANCELLED'}
        boxes.remove(self.box_index)
        hb_utils.run_calc_fix(context, interior_obj)
        return {'FINISHED'}


classes = (
    hb_frameless_AccessorySearchRow,
    hb_frameless_OT_drawer_add_accessory,
    hb_frameless_OT_drawer_remove_accessory,
    hb_frameless_OT_drawer_interior,
    hb_frameless_OT_calculate_shelf_quantity,
    hb_frameless_OT_interior_prompts,
    hb_frameless_OT_change_interior_type,
    hb_frameless_OT_interior_part_prompts,
    hb_frameless_OT_delete_interior_part,
    hb_frameless_OT_custom_interior_vertical,
    hb_frameless_OT_custom_interior_horizontal,
    hb_frameless_OT_add_interior_item,
    hb_frameless_OT_remove_interior_item,
    hb_frameless_OT_add_rollout_box,
    hb_frameless_OT_remove_rollout_box,
)

register, unregister = bpy.utils.register_classes_factory(classes)
