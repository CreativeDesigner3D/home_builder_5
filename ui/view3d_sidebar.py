import bpy
from .. import hb_project
from .. import hb_layouts
from .. import hb_details

CATEGORY_NAME = "Home Builder"
# =============================================================================
# HOME BUILDER UI PANELS
# All panels in the "Home Builder" category tab
# =============================================================================

# -----------------------------------------------------------------------------
# PANEL 0: ROOMS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_hidden_header(bpy.types.Panel):
    bl_label = "Project"
    bl_idname = "HOME_BUILDER_PT_hidden_header"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 0
    bl_options = {'HIDE_HEADER'}
    
    def draw(self, context):
        layout = self.layout
        in_layout_view = context.scene.get('IS_LAYOUT_VIEW')
        in_detail_view = context.scene.get('IS_DETAIL_VIEW')
        
        if in_layout_view:
            box = layout.box()
            box.label(text="Current Layout View: " + context.scene.name, icon='INFO')
            box.label(text="You are in a layout view. Select a room below.",icon='BLANK1')
        if in_detail_view:
            box = layout.box()
            box.label(text="Current Detail View: " + context.scene.name, icon='INFO')
            box.label(text="You are in a detail view. Select a room below.",icon='BLANK1')

        if not in_layout_view and not in_detail_view:
            text = context.scene.name
        else:
            text = "Select a Room"

        row = layout.row()
        row.scale_y = 1.5
        row.menu("HOME_BUILDER_MT_room_list", text=text, icon='LOOP_BACK')

        hb_frameless = context.scene.hb_frameless

        selection_mod_box = layout.box()
        selection_mod_box.label(text="Frameless Selection Mode")
        row = selection_mod_box.row(align=True)
        row.scale_y = 1.5
        row.prop_enum(hb_frameless, "frameless_selection_mode", 'Cabinets', icon='MESH_CUBE')
        row.prop_enum(hb_frameless, "frameless_selection_mode", 'Bays', icon='MESH_CUBE')
        row.prop_enum(hb_frameless, "frameless_selection_mode", 'Openings', icon='OBJECT_DATAMODE')
        row.prop_enum(hb_frameless, "frameless_selection_mode", 'Interiors', icon='OBJECT_HIDDEN')    
        row.prop_enum(hb_frameless, "frameless_selection_mode", 'Parts', icon='EDITMODE_HLT')  

        #TODO: IMPLEMENT SELECTION MODE FOR OTHER PRODUCT TYPES   

# -----------------------------------------------------------------------------
# PANEL 1: ROOMS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_project(bpy.types.Panel):
    bl_label = "Project"
    bl_idname = "HOME_BUILDER_PT_project"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view or detail view
        if context.scene.get('IS_DETAIL_VIEW'):
            return False
        return not context.scene.get('IS_LAYOUT_VIEW')

    def draw(self, context):
        layout = self.layout
        project = hb_project.get_project_props(context)
        
        # Project name prominently displayed
        row = layout.row()
        row.scale_y = 1.2
        row.prop(project, "project_name", text="")


class HOME_BUILDER_PT_project_info(bpy.types.Panel):
    bl_label = "Project Info"
    bl_idname = "HOME_BUILDER_PT_project_info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_project"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        project = hb_project.get_project_props(context)
        
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        
        # Project info
        col.prop(project, "project_number")
        col.prop(project, "project_date")
        
        col.separator()
        
        # Designer
        box = layout.box()
        box.label(text="Designer", icon='USER')
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(project, "designer_name", text="Name")
        col.prop(project, "designer_phone", text="Phone")
        col.prop(project, "designer_email", text="Email")
        
        # Client info
        box = layout.box()
        box.label(text="Client", icon='COMMUNITY')
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(project, "client_name", text="Name")
        col.prop(project, "client_address")
        col.prop(project, "client_city")
        
        row = col.row(align=True)
        row.prop(project, "client_state", text="State")
        row.prop(project, "client_zip", text="Zip")
        
        col.prop(project, "client_phone", text="Phone")
        col.prop(project, "client_email", text="Email")
        
        # Notes
        box = layout.box()
        box.label(text="Notes", icon='TEXT')
        box.prop(project, "project_notes", text="")


class HOME_BUILDER_PT_project_rooms(bpy.types.Panel):
    bl_label = "Rooms"
    bl_idname = "HOME_BUILDER_PT_project_rooms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_project"
    
    def draw(self, context):
        layout = self.layout
        
        # Get all room scenes using hb_project helper
        room_scenes = hb_project.get_room_scenes()
        
        col = layout.column(align=True)
        for scene in room_scenes:
            row = col.row(align=True)
            
            # Use checkbox icon for selection state
            is_selected = scene == context.scene
            icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'
            
            # Switch button
            op = row.operator("home_builder.switch_room", text=scene.name, icon=icon)
            op.scene_name = scene.name
            
            # Delete button (only if more than one room)
            if len(room_scenes) > 1:
                op = row.operator("home_builder.delete_room", text="", icon='X')
                op.scene_name = scene.name
        
        # Room management buttons
        col.separator()
        row = col.row(align=True)
        row.operator("home_builder.create_room", text="Add", icon='ADD')
        
        # Only show these if not in a layout view
        if not context.scene.get('IS_LAYOUT_VIEW'):
            row.operator("home_builder.rename_room", text="Rename", icon='GREASEPENCIL')
            row.operator("home_builder.duplicate_room", text="Duplicate", icon='DUPLICATE')


# -----------------------------------------------------------------------------
# PANEL 2: ROOM LAYOUT
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_room_layout(bpy.types.Panel):
    bl_label = "Room Layout"
    bl_idname = "HOME_BUILDER_PT_room_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view or detail view
        if context.scene.get('IS_DETAIL_VIEW'):
            return False        
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder


# SUBPANEL: Walls
class HOME_BUILDER_PT_room_layout_walls(bpy.types.Panel):
    bl_label = "Walls"
    bl_idname = "HOME_BUILDER_PT_room_layout_walls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder
        
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator('home_builder_walls.draw_walls', text="Draw Walls", icon='GREASEPENCIL')
        row.prop(hb_scene, 'wall_type', text="")
        
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        
        if hb_scene.wall_type in {'Exterior', 'Interior'}:
            row = col.row()
            row.prop(hb_scene, 'ceiling_height', text="Ceiling Height")
            row.operator('home_builder_walls.update_wall_height', text="", icon='FILE_REFRESH', emboss=False)
            row = col.row()
            row.prop(hb_scene, 'wall_thickness')
            row.operator('home_builder_walls.update_wall_thickness', text="", icon='FILE_REFRESH', emboss=False)
        elif hb_scene.wall_type == 'Half':
            row = col.row()
            row.prop(hb_scene, 'half_wall_height', text="Half Wall Height")
            row.operator('home_builder_walls.update_wall_height', text="", icon='FILE_REFRESH', emboss=False)
            row = col.row()
            row.prop(hb_scene, 'wall_thickness')
            row.operator('home_builder_walls.update_wall_thickness', text="", icon='FILE_REFRESH', emboss=False)
        else:
            row = col.row()
            row.prop(hb_scene, 'fake_wall_height', text="Fake Wall Height")
            row.operator('home_builder_walls.update_wall_height', text="", icon='FILE_REFRESH', emboss=False)


# SUBPANEL: Doors & Windows
class HOME_BUILDER_PT_room_layout_doors_windows(bpy.types.Panel):
    bl_label = "Doors & Windows"
    bl_idname = "HOME_BUILDER_PT_room_layout_doors_windows"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder
        
        box = layout.box()
        box.prop(hb_scene, 'show_entry_door_and_window_cages', text="Show Entry Door and Window Cages")
        
        row = layout.row(align=True)
        row.scale_y = 1.2
        row.operator('home_builder_doors_windows.place_door', text="Door", icon='MESH_CUBE')
        row.operator('home_builder_doors_windows.place_window', text="Window", icon='MESH_PLANE')


# SUBPANEL: Floor & Ceiling
class HOME_BUILDER_PT_room_layout_floor(bpy.types.Panel):
    bl_label = "Floor & Ceiling"
    bl_idname = "HOME_BUILDER_PT_room_layout_floor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.add_floor")


# SUBPANEL: Lighting
class HOME_BUILDER_PT_room_layout_lighting(bpy.types.Panel):
    bl_label = "Lighting"
    bl_idname = "HOME_BUILDER_PT_room_layout_lighting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_walls.add_room_lights")


# SUBPANEL: Obstacles
class HOME_BUILDER_PT_room_layout_obstacles(bpy.types.Panel):
    bl_label = "Obstacles"
    bl_idname = "HOME_BUILDER_PT_room_layout_obstacles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Check if hb_obstacles property exists
        if not hasattr(context.scene, 'hb_obstacles'):
            layout.label(text="Obstacles module not loaded", icon='ERROR')
            return
        
        hb_obs = context.scene.hb_obstacles
        
        # Obstacle type selection
        col = layout.column(align=True)
        col.label(text="Obstacle Type:", icon='OBJECT_DATA')
        col.prop(hb_obs, "obstacle_type", text="")
        
        # Don't show controls for header items
        if hb_obs.obstacle_type.startswith('HEADER_'):
            col.label(text="Select an obstacle type above", icon='INFO')
            return
        
        col.separator()
        
        # Place button
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("home_builder_obstacles.place_obstacle", 
                    text="Place Obstacle", icon='ADD')
        
        # Dimensions section
        box = layout.box()
        row = box.row()
        row.label(text="Dimensions", icon='ARROW_LEFTRIGHT')
        
        col = box.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        
        col.prop(hb_obs, "obstacle_width", text="Width")
        col.prop(hb_obs, "obstacle_height", text="Height")
        col.prop(hb_obs, "obstacle_depth", text="Depth")
        col.prop(hb_obs, "obstacle_height_from_floor", text="From Floor")
        
        # Scene obstacles section
        obstacles_in_scene = [obj for obj in context.scene.objects if obj.get('IS_OBSTACLE')]
        
        if obstacles_in_scene:
            box = layout.box()
            row = box.row()
            row.label(text=f"Obstacles in Scene ({len(obstacles_in_scene)})", icon='OUTLINER_OB_MESH')
            row.operator("home_builder_obstacles.select_all", text="", icon='RESTRICT_SELECT_OFF')
            
            col = box.column(align=True)
            for obj in obstacles_in_scene[:10]:  # Show first 10
                row = col.row(align=True)
                
                # Select button
                is_selected = obj.select_get()
                icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'
                op = row.operator("home_builder_obstacles.select_obstacle", text="", icon=icon)
                op.object_name = obj.name
                
                # Obstacle name with type icon
                obs_type = obj.get('OBSTACLE_TYPE', 'CUSTOM_RECT')
                if 'OUTLET' in obs_type or 'SWITCH' in obs_type:
                    type_icon = 'PLUGIN'
                elif 'VENT' in obs_type:
                    type_icon = 'MESH_GRID'
                elif 'LIGHT' in obs_type or 'FAN' in obs_type:
                    type_icon = 'LIGHT'
                elif 'FIRE' in obs_type or 'SMOKE' in obs_type or 'SPRINKLER' in obs_type:
                    type_icon = 'ERROR'
                else:
                    type_icon = 'OBJECT_DATA'
                row.label(text=obj.name, icon=type_icon)
                
                # Delete button
                op = row.operator("home_builder_obstacles.delete_obstacle", text="", icon='X')
                op.object_name = obj.name
            
            if len(obstacles_in_scene) > 10:
                col.label(text=f"... and {len(obstacles_in_scene) - 10} more")


# -----------------------------------------------------------------------------
# PANEL 3: PRODUCT LIBRARY
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_product_library(bpy.types.Panel):
    bl_label = "Product Library"
    bl_idname = "HOME_BUILDER_PT_product_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view or detail view
        if context.scene.get('IS_DETAIL_VIEW'):
            return False
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hb_scene = scene.home_builder
        
        # Product type selector
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(hb_scene, "product_tab",text="")

        if hb_scene.product_tab == 'FRAMELESS':
            scene.hb_frameless.draw_library_ui(layout, context)
        elif hb_scene.product_tab == 'FACE FRAME':
            scene.hb_face_frame.draw_library_ui(layout, context)
        else:
            scene.hb_closets.draw_library_ui(layout, context)

# -----------------------------------------------------------------------------
# PANEL 4: LAYOUT VIEWS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_layout_views(bpy.types.Panel):
    bl_label = "Layout Views"
    bl_idname = "HOME_BUILDER_PT_layout_views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a detail view
        if context.scene.get('IS_DETAIL_VIEW'):
            return False
        return True

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.menu("HOME_BUILDER_MT_layout_views_create")

        is_layout_view = context.scene.get('IS_LAYOUT_VIEW', False)

        # Layout Views List
        layout_views = hb_layouts.LayoutView.get_all_layout_views()
        
        if layout_views:
            box = layout.box()
            box.label(text="Available Layout Views", icon='VIEW_ORTHO')
            col = box.column(align=True)
            for scene in layout_views:
                row = col.row(align=True)
                
                # Use checkbox icon for selection state
                is_selected = scene == context.scene
                icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'
                
                op = row.operator("home_builder_layouts.go_to_layout_view",
                                 text=scene.name, icon=icon)
                op.scene_name = scene.name
                
                if scene.get('IS_ELEVATION_VIEW'):
                    op = row.operator("home_builder_layouts.update_elevation_view",
                                     text="", icon='FILE_REFRESH')
                
                op = row.operator("home_builder_layouts.delete_layout_view",
                                 text="", icon='X')
                op.scene_name = scene.name
            if is_layout_view:
                box.prop(context.scene,'name',text="View Name")            
        else:
            layout.label(text="No layout views yet", icon='INFO')


class HOME_BUILDER_MT_layout_views_create(bpy.types.Menu):
    bl_label = "Create Layout Views"

    def draw(self, context):
        layout = self.layout
        layout.operator("home_builder_layouts.create_all_elevations", 
                    text="All Wall Elevations", icon='DOCUMENTS')
        layout.operator("home_builder_layouts.create_elevation_view", 
                        text="Elevation (Selected Wall)", icon='VIEW_ORTHO')
        layout.separator()
        layout.operator("home_builder_layouts.create_plan_view", 
                    text="Floor Plan", icon='MESH_GRID')
        layout.separator()
        op = layout.operator("home_builder_layouts.create_3d_view", 
                         text="3D Perspective", icon='VIEW_PERSPECTIVE')
        op.perspective = True
        
        op = layout.operator("home_builder_layouts.create_3d_view", 
                         text="Isometric", icon='VIEW_ORTHO')
        op.perspective = False
        layout.separator()
        layout.operator("home_builder_layouts.create_multi_view", 
                    text="Multi-View Layout", icon='OUTLINER_OB_GROUP_INSTANCE')


class HOME_BUILDER_MT_room_list(bpy.types.Menu):
    """Menu to select which room to return to"""
    bl_label = "Select Room"

    def draw(self, context):
        layout = self.layout
        room_scenes = [s for s in bpy.data.scenes 
                      if not s.get('IS_LAYOUT_VIEW') and not s.get('IS_DETAIL_VIEW')]
        
        for scene in room_scenes:
            op = layout.operator("home_builder_layouts.go_to_layout_view",
                               text=scene.name, icon='HOME')
            op.scene_name = scene.name


class HOME_BUILDER_MT_detail_library(bpy.types.Menu):
    bl_label = "Detail Library"
    bl_idname = "HOME_BUILDER_MT_detail_library"
    
    def draw(self, context):
        from .. import hb_detail_library
        
        layout = self.layout
        is_detail_view = context.scene.get('IS_DETAIL_VIEW', False)
        is_crown_detail = context.scene.get('IS_CROWN_DETAIL', False)
        
        # Save current detail option (in detail or crown detail view)
        if is_detail_view or is_crown_detail:
            layout.operator("home_builder_details.save_to_library", 
                           text="Save Current Detail", icon='FILE_NEW')
            layout.separator()
        
        # List saved details
        details = hb_detail_library.get_library_details()
        
        if details:
            layout.label(text="Create from Library:", icon='FILE_FOLDER')
            for detail in details:
                row = layout.row()
                op = row.operator("home_builder_details.create_from_library",
                                 text=detail.get("name", "Unnamed"), 
                                 icon='IMPORT')
                op.filepath = detail.get("filepath", "")
                op.name = detail.get("name", "Detail")
        else:
            layout.label(text="No saved details", icon='INFO')
        
        layout.separator()
        
        # Open folder
        layout.operator("home_builder_details.open_library_folder",
                       text="Open Library Folder", icon='FILE_FOLDER')



# SUBPANEL: Create Layout Views
class HOME_BUILDER_PT_layout_views_create(bpy.types.Panel):
    bl_label = "Create Views"
    bl_idname = "HOME_BUILDER_PT_layout_views_create"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_layout_views"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        
        # Elevation views
        if context.object and 'IS_WALL_BP' in context.object:
            col.operator("home_builder_layouts.create_elevation_view", 
                        text="Elevation (Selected Wall)", icon='VIEW_ORTHO')
        else:
            col.label(text="Select wall for elevation", icon='INFO')
        
        col.operator("home_builder_layouts.create_all_elevations", 
                    text="All Wall Elevations", icon='DOCUMENTS')
        
        col.separator()
        
        # Plan view
        col.operator("home_builder_layouts.create_plan_view", 
                    text="Floor Plan", icon='MESH_GRID')
        
        col.separator()
        
        # 3D views
        row = col.row(align=True)
        op = row.operator("home_builder_layouts.create_3d_view", 
                         text="3D Perspective", icon='VIEW_PERSPECTIVE')
        op.perspective = True
        
        op = row.operator("home_builder_layouts.create_3d_view", 
                         text="Isometric", icon='VIEW_ORTHO')
        op.perspective = False
        
        col.separator()
        
        # Multi-view for cabinet groups
        col.operator("home_builder_layouts.create_multi_view", 
                    text="Cabinet Group Layout", icon='OUTLINER_OB_GROUP_INSTANCE')


# SUBPANEL: Page Settings (only in layout view)
class HOME_BUILDER_PT_layout_views_settings(bpy.types.Panel):
    bl_label = "Page Settings"
    bl_idname = "HOME_BUILDER_PT_layout_views_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_layout_views"
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        
        col.prop(context.scene, "name", text="Name")
        
        # View type info
        # if context.scene.get('IS_ELEVATION_VIEW'):
        #     source_wall = context.scene.get('SOURCE_WALL', 'Unknown')
        #     col.label(text=f"Type: Elevation ({source_wall})")
        # elif context.scene.get('IS_PLAN_VIEW'):
        #     col.label(text="Type: Floor Plan")
        # elif context.scene.get('IS_3D_VIEW'):
        #     col.label(text="Type: 3D View")
        # elif context.scene.get('IS_MULTI_VIEW'):
        #     col.label(text="Type: Multi-View")
        
        col.separator()
        
        # Paper settings
        col.prop(context.scene, "hb_paper_size", text="Paper")
        # col.prop(context.scene, "hb_paper_landscape", text="Landscape")
        col.prop(context.scene, "hb_layout_scale", text="Scale")
        
        col.separator()
        
        row = col.row(align=True)
        row.scale_y = 1.5
        # row.operator("home_builder_layouts.fit_view_to_content", 
        #             text="Fit to Content", icon='FULLSCREEN_ENTER')
        row.operator("home_builder_layouts.render_layout", 
                    text="Render", icon='RENDER_STILL')
        row.operator("home_builder_layouts.export_all_to_pdf", 
                    text="Export PDF", icon='FILE')





# SUBPANEL: Add Details to Layout (only in layout view)
class HOME_BUILDER_PT_layout_views_details(bpy.types.Panel):
    bl_label = "Insert 2D Details"
    bl_idname = "HOME_BUILDER_PT_layout_views_details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_layout_views"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when in a layout view
        return context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        
        # Get all detail views
        detail_views = hb_details.DetailView.get_all_detail_views()
        
        if detail_views:
            col = layout.column(align=True)
            for scene in detail_views:
                op = col.operator("home_builder_layouts.add_detail_to_layout",
                                 text=scene.name, icon='IMPORT')
                op.detail_scene_name = scene.name
        else:
            layout.label(text="No 2D details available", icon='INFO')
            layout.label(text="Create details in the 2D Details panel")


# -----------------------------------------------------------------------------
# PANEL: 2D DETAILS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_2d_details(bpy.types.Panel):
    bl_label = "2D Details"
    bl_idname = "HOME_BUILDER_PT_2d_details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 4
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        is_detail_view = context.scene.get('IS_DETAIL_VIEW', False)
        
        # Create new detail button with library menu
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("home_builder_details.create_detail", 
                    text="New Detail", icon='ADD')
        row.menu("HOME_BUILDER_MT_detail_library", text="", icon='DOWNARROW_HLT')
        
        # List existing details
        detail_views = hb_details.DetailView.get_all_detail_views()
        
        if detail_views:
            box = layout.box()
            box.label(text="Available 2D Details", icon='VIEW_ORTHO')
            col = box.column(align=True)

            for scene in detail_views:
                row = col.row(align=True)
                
                # Use checkbox icon for selection state
                is_selected = scene == context.scene
                icon = 'CHECKBOX_HLT' if is_selected else 'CHECKBOX_DEHLT'
                
                op = row.operator("home_builder_layouts.go_to_layout_view",
                                 text=scene.name, icon=icon)
                op.scene_name = scene.name
                
                op = row.operator("home_builder_details.delete_detail",
                                 text="", icon='X')
                op.scene_name = scene.name
            if is_detail_view:
                box.prop(context.scene,'name',text="Detail Name")


# -----------------------------------------------------------------------------
# PANEL 5: ANNOTATIONS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_annotations(bpy.types.Panel):
    bl_label = "Annotations"
    bl_idname = "HOME_BUILDER_PT_annotations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 5
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout


# SUBPANEL: Drawing Tools
class HOME_BUILDER_PT_annotations_drawing(bpy.types.Panel):
    bl_label = "Drawing Tools"
    bl_idname = "HOME_BUILDER_PT_annotations_drawing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_annotations"
    
    def draw(self, context):
        layout = self.layout
        is_layout_view = context.scene.get('IS_LAYOUT_VIEW', False)
        is_detail_view = context.scene.get('IS_DETAIL_VIEW', False)
        
        col = layout.column(align=True)
        col.scale_y = 1.2
        
        # Line drawing
        col.operator("home_builder_details.draw_line", 
                    text="Draw Line", icon='IPO_LINEAR')
        
        # Rectangle drawing
        col.operator("home_builder_details.draw_rectangle", 
                    text="Draw Rectangle", icon='MESH_PLANE')
        
        # Circle drawing
        col.operator("home_builder_details.draw_circle", 
                    text="Draw Circle", icon='MESH_CIRCLE')
        
        col.separator()
        
        # Text annotation
        col.operator("home_builder_details.add_text", 
                    text="Add Text", icon='FONT_DATA')
        
        # Dimension - use appropriate operator based on view type
        if is_detail_view:
            col.operator("home_builder_details.add_dimension", 
                        text="Add Dimension", icon='DRIVER_DISTANCE')
        elif is_layout_view:
            col.operator("home_builder_layouts.add_dimension", 
                        text="Add Dimension", icon='DRIVER_DISTANCE')
        else:
            col.operator("home_builder_layouts.add_dimension_3d", 
                        text="Add Dimension", icon='DRIVER_DISTANCE')

# SUBPANEL: Molding Library
class HOME_BUILDER_PT_molding_library(bpy.types.Panel):
    bl_label = "Molding Library"
    bl_idname = "HOME_BUILDER_PT_molding_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_annotations"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Show in crown detail scenes or regular detail views
        return context.scene.get('IS_CROWN_DETAIL', False) or context.scene.get('IS_DETAIL_VIEW', False)
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder
        
        # Import the molding functions
        from ..product_libraries.frameless.operators import ops_crown
        
        # Category dropdown
        row = layout.row(align=True)
        row.label(text="Category:")
        row.prop(hb_scene, "molding_category", text="")
        
        # Molding dropdown
        row = layout.row(align=True)
        row.label(text="Molding:")
        row.prop(hb_scene, "molding_selection", text="")
        
        # Get the selected molding info for thumbnail and filepath
        category = hb_scene.molding_category
        selection = hb_scene.molding_selection
        
        if category and category != 'NONE' and selection and selection != 'NONE':
            # Get molding info
            items = ops_crown.get_molding_items(category)
            selected_item = None
            for item in items:
                if item['name'] == selection:
                    selected_item = item
                    break
            
            if selected_item:
                # Show thumbnail
                if selected_item.get('thumbnail'):
                    from ..product_libraries.frameless import props_hb_frameless
                    icon_id = props_hb_frameless.load_library_thumbnail(
                        selected_item['thumbnail'], 
                        f"molding_{selected_item['name']}"
                    )
                    if icon_id:
                        row = layout.row()
                        row.template_icon(icon_value=icon_id, scale=5.0)
                
                # Add button
                row = layout.row()
                row.scale_y = 1.3
                op = row.operator(
                    "hb_frameless.add_molding_profile", 
                    text="Add Molding Profile",
                    icon='ADD'
                )
                op.filepath = selected_item['filepath']
                op.molding_name = selected_item['name']
        
        row = layout.row()
        row.scale_y = 1.3
        row.operator("hb_frameless.add_solid_lumber", text="Add Solid Lumber", icon='MESH_PLANE')

# SUBPANEL: Edit Tools (for curves)
class HOME_BUILDER_PT_annotations_edit(bpy.types.Panel):
    bl_label = "Edit Tools"
    bl_idname = "HOME_BUILDER_PT_annotations_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_annotations"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Show when a curve is selected or in edit mode on a curve
        if context.mode == 'EDIT_CURVE':
            return True
        if context.active_object and context.active_object.type == 'CURVE':
            return True
        return False
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.scale_y = 1.2
        
        # Edit mode tools
        if context.mode == 'EDIT_CURVE':
            col.operator("home_builder_details.add_fillet", 
                        text="Add Fillet/Radius", icon='SPHERECURVE')
        
        # Object mode curve tools
        col.operator("home_builder_details.offset_curve", 
                    text="Offset Curve", icon='MOD_OFFSET')


# SUBPANEL: Annotation Settings
class HOME_BUILDER_PT_annotations_settings(bpy.types.Panel):
    bl_label = "Annotation Settings"
    bl_idname = "HOME_BUILDER_PT_annotations_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = "HOME_BUILDER_PT_annotations"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder
        
        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False
        
        # Line Settings
        box = layout.box()
        box.label(text="Lines", icon='IPO_LINEAR')
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(hb_scene, "annotation_line_thickness", text="Thickness")
        col.prop(hb_scene, "annotation_line_color", text="Color")
        
        # Text Settings
        box = layout.box()
        box.label(text="Text", icon='FONT_DATA')
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(hb_scene, "annotation_font", text="Font")
        col.prop(hb_scene, "annotation_text_size", text="Size")
        col.prop(hb_scene, "annotation_text_color", text="Color")
        
        # Dimension Settings
        box = layout.box()
        box.label(text="Dimensions", icon='DRIVER_DISTANCE')
        col = box.column()
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(hb_scene, "annotation_dimension_text_size", text="Text Size")
        col.prop(hb_scene, "annotation_dimension_tick_length", text="Tick Length")
        col.prop(hb_scene, "annotation_dimension_line_thickness", text="Line Thickness")
        
        # Apply to All button
        layout.separator()
        layout.operator("home_builder_annotations.apply_settings_to_all", 
                       text="Apply to All Annotations", icon='FILE_REFRESH')


# -----------------------------------------------------------------------------
# PANEL 6: SETTINGS & DEVELOPER
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_settings(bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "HOME_BUILDER_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_order = 6
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator('home_builder.set_recommended_settings', 
                    text="Set Recommended Settings", icon='PREFERENCES')
        
        col.separator()
        col.operator("home_builder.reload_addon", text="Reload Add-on", icon='FILE_REFRESH')


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    HOME_BUILDER_PT_hidden_header,
    HOME_BUILDER_PT_project,
    HOME_BUILDER_PT_project_info,
    HOME_BUILDER_PT_project_rooms,
    HOME_BUILDER_PT_room_layout,
    HOME_BUILDER_PT_room_layout_walls,
    HOME_BUILDER_PT_room_layout_doors_windows,
    HOME_BUILDER_PT_room_layout_floor,
    HOME_BUILDER_PT_room_layout_lighting,
    HOME_BUILDER_PT_room_layout_obstacles,
    HOME_BUILDER_PT_product_library,
    HOME_BUILDER_PT_layout_views,
    HOME_BUILDER_MT_layout_views_create,
    HOME_BUILDER_MT_room_list,
    HOME_BUILDER_MT_detail_library,
    HOME_BUILDER_PT_layout_views_settings,
    HOME_BUILDER_PT_layout_views_details,
    HOME_BUILDER_PT_2d_details,
    HOME_BUILDER_PT_annotations,
    HOME_BUILDER_PT_annotations_drawing,
    HOME_BUILDER_PT_molding_library,
    HOME_BUILDER_PT_annotations_edit,
    HOME_BUILDER_PT_annotations_settings,
    HOME_BUILDER_PT_settings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
