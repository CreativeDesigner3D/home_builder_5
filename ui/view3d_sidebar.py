import bpy

class HOME_BUILDER_5_PRO_PT_library(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Home Builder 5 Pro"
    bl_category = "Home Builder 5 Pro"    
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        hb_scene = context.scene.home_builder

        layout = self.layout

        # Developer Tools Section
        box = layout.box()
        box.label(text="Developer", icon='CONSOLE')
        box.operator("home_builder.reload_addon", text="Reload Add-on", icon='FILE_REFRESH')    

        main_box = layout.box()
        main_box.label(text="Recommended Settings")
        row = main_box.row(align=True)
        row.operator('home_builder.set_recommended_settings',text="Set Recommended Settings",icon='PREFERENCES')

        main_box = layout.box()
        main_box.label(text="Home Builder 5 Pro")
        
        col = main_box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.2
        row.prop_enum(hb_scene, "main_tab", 'ROOM',icon='CHECKBOX_DEHLT' if hb_scene.main_tab !='ROOM' else 'CHECKBOX_HLT') 
        row.separator()

        row.prop_enum(hb_scene, "main_tab", 'PRODUCTS',icon='CHECKBOX_DEHLT' if hb_scene.main_tab =='ROOM' else 'CHECKBOX_HLT') 
        row.prop(hb_scene, "product_tab",text="")

        main_col = main_box.column(align=True)

        if hb_scene.main_tab == 'ROOM':
            wall_box = main_col.box()
            wall_box.label(text="Walls")

            row = wall_box.row(align=True)
            row.scale_y = 1.3
            row.operator('home_builder_walls.draw_walls',text="Draw Walls",icon='GREASEPENCIL')
            row.separator()
            row.prop(hb_scene,'wall_type',text="")

            wall_col = wall_box.column()
            wall_col.use_property_split = True
            wall_col.use_property_decorate = False
            if hb_scene.wall_type in {'Exterior','Interior'}:
                row = wall_col.row()
                row.prop(hb_scene,'ceiling_height',text="Ceiling Height")
                row.operator('home_builder_walls.update_wall_height',text="",icon='FILE_REFRESH',emboss=False)
                row = wall_col.row()
                row.prop(hb_scene,'wall_thickness')
                row.operator('home_builder_walls.update_wall_thickness',text="",icon='FILE_REFRESH',emboss=False)
                # row = wall_col.row()
                # row.prop(hb_scene,'wall_material')
            elif hb_scene.wall_type == 'Half': 
                row = wall_col.row()
                row.prop(hb_scene,'half_wall_height',text="Half Wall Height")
                row.operator('home_builder_walls.update_wall_height',text="",icon='FILE_REFRESH',emboss=False)
                row = wall_col.row()
                row.prop(hb_scene,'wall_thickness')
                row.operator('home_builder_walls.update_wall_thickness',text="",icon='FILE_REFRESH',emboss=False)
                # row = wall_col.row()
                # row.prop(hb_scene,'wall_material')
            else:
                row = wall_col.row()
                row.prop(hb_scene,'fake_wall_height',text="Fake Wall Height")
                row.operator('home_builder_walls.update_wall_height',text="",icon='FILE_REFRESH',emboss=False)             
            
            box = main_col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(hb_scene,'show_entry_doors_and_windows',text="Entry Doors and Windows",icon='TRIA_DOWN' if hb_scene.show_entry_doors_and_windows else 'TRIA_RIGHT',emboss=False)
            row.separator()
            if hb_scene.show_entry_doors_and_windows:
                row = box.row()
                row.operator('home_builder_doors_windows.place_door',text="Door",icon='GREASEPENCIL')
                row.operator('home_builder_doors_windows.place_window',text="Window",icon='GREASEPENCIL')

            box = main_col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(hb_scene,'show_obstacles',text="Obstacles",icon='TRIA_DOWN' if hb_scene.show_obstacles else 'TRIA_RIGHT',emboss=False)
            row.separator()
            if hb_scene.show_obstacles:
                row = box.row()
                row.label(text="TODO: Create UI")

            box = main_col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(hb_scene,'show_decorations',text="Decorations",icon='TRIA_DOWN' if hb_scene.show_decorations else 'TRIA_RIGHT',emboss=False)
            row.separator()
            if hb_scene.show_decorations:
                row = box.row()
                row.label(text="TODO: Create UI")

            box = main_col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(hb_scene,'show_materials',text="Materials",icon='TRIA_DOWN' if hb_scene.show_materials else 'TRIA_RIGHT',emboss=False)
            row.separator()
            if hb_scene.show_materials:
                row = box.row()
                row.prop_search(hb_scene,'wall_material',bpy.data,'materials',text="Wall Material")

            box = main_col.box()
            row = box.row()
            row.alignment = 'LEFT'        
            row.prop(hb_scene,'show_room_settings',text="Room Settings",icon='TRIA_DOWN' if hb_scene.show_room_settings else 'TRIA_RIGHT',emboss=False)
            row.separator()
            if hb_scene.show_room_settings:
                row = box.row()
                row.label(text="TODO: Create UI")
        else:
            if hb_scene.product_tab == 'FRAMELESS':
                context.scene.hb_frameless.draw_library_ui(main_col,context)
            elif hb_scene.product_tab == 'FACE FRAME':
                context.scene.hb_face_frame.draw_library_ui(main_col,context)
            else:
                context.scene.hb_closets.draw_library_ui(main_col,context)

        # #EXAMPLE UI
        # # Kitchen Layouts Section
        # kitchen_box = layout.box()
        # kitchen_box.label(text="Kitchen Layouts", icon='HOME')
        
        # # Create a grid layout for kitchen buttons
        # grid = kitchen_box.grid_flow(columns=2, align=True)
        
        # grid.operator("ps_face_frame.draw_item_from_library", text="Cabinet")
        # grid.operator("ps_face_frame.draw_kitchen", text="L-Shaped")

classes = (
    HOME_BUILDER_5_PRO_PT_library,
)

register, unregister = bpy.utils.register_classes_factory(classes)             