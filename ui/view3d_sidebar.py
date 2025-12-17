import bpy
from .. import hb_layouts
from .. import hb_details

# =============================================================================
# HOME BUILDER UI PANELS
# All panels in the "Home Builder" category tab
# =============================================================================

# -----------------------------------------------------------------------------
# PANEL 1: ROOMS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_rooms(bpy.types.Panel):
    bl_label = "Rooms"
    bl_idname = "HOME_BUILDER_PT_rooms"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Get all room scenes (non-layout and non-detail scenes)
        room_scenes = [s for s in bpy.data.scenes 
                      if not s.get('IS_LAYOUT_VIEW') and not s.get('IS_DETAIL_VIEW')]
        
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
    bl_category = 'Home Builder'
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view
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
    bl_category = 'Home Builder'
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
    bl_category = 'Home Builder'
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
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
    bl_category = 'Home Builder'
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="TODO: Floor & Ceiling tools")


# SUBPANEL: Lighting
class HOME_BUILDER_PT_room_layout_lighting(bpy.types.Panel):
    bl_label = "Lighting"
    bl_idname = "HOME_BUILDER_PT_room_layout_lighting"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_parent_id = "HOME_BUILDER_PT_room_layout"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="TODO: Lighting tools")


# SUBPANEL: Obstacles
class HOME_BUILDER_PT_room_layout_obstacles(bpy.types.Panel):
    bl_label = "Obstacles"
    bl_idname = "HOME_BUILDER_PT_room_layout_obstacles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
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
    bl_category = 'Home Builder'
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # Only show when not in a layout view
        return not context.scene.get('IS_LAYOUT_VIEW')
    
    def draw(self, context):
        layout = self.layout
        hb_scene = context.scene.home_builder
        
        # Product type selector
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(hb_scene, "product_tab",text="")

        if hb_scene.product_tab == 'FRAMELESS':
            context.scene.hb_frameless.draw_library_ui(layout, context)
        elif hb_scene.product_tab == 'FACE FRAME':
            context.scene.hb_face_frame.draw_library_ui(layout, context)
        else:
            context.scene.hb_closets.draw_library_ui(layout, context)


# -----------------------------------------------------------------------------
# PANEL 4: LAYOUT VIEWS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_layout_views(bpy.types.Panel):
    bl_label = "Layout Views"
    bl_idname = "HOME_BUILDER_PT_layout_views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.menu("HOME_BUILDER_MT_layout_views_create")

        is_layout_view = context.scene.get('IS_LAYOUT_VIEW', False)
        
        # Layout Views List
        layout_views = hb_layouts.LayoutView.get_all_layout_views()
        
        if layout_views:
            col = layout.column(align=True)
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
            
            # Back to room button(s)
            if is_layout_view:
                col.separator()
                room_scenes = [s for s in bpy.data.scenes if not s.get('IS_LAYOUT_VIEW')]
                
                if len(room_scenes) == 1:
                    # Single room - direct button
                    op = col.operator("home_builder_layouts.go_to_layout_view",
                                     text="Back to Room", icon='LOOP_BACK')
                    op.scene_name = room_scenes[0].name
                elif len(room_scenes) > 1:
                    # Multiple rooms - show menu
                    col.menu("HOME_BUILDER_MT_room_list", text="Go Back to Room", icon='LOOP_BACK')
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


# SUBPANEL: Create Layout Views
class HOME_BUILDER_PT_layout_views_create(bpy.types.Panel):
    bl_label = "Create Views"
    bl_idname = "HOME_BUILDER_PT_layout_views_create"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
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
    bl_category = 'Home Builder'
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
        if context.scene.get('IS_ELEVATION_VIEW'):
            source_wall = context.scene.get('SOURCE_WALL', 'Unknown')
            col.label(text=f"Type: Elevation ({source_wall})")
        elif context.scene.get('IS_PLAN_VIEW'):
            col.label(text="Type: Floor Plan")
        elif context.scene.get('IS_3D_VIEW'):
            col.label(text="Type: 3D View")
        elif context.scene.get('IS_MULTI_VIEW'):
            col.label(text="Type: Multi-View")
        
        col.separator()
        
        # Paper settings
        col.prop(context.scene, "hb_paper_size", text="Paper")
        col.prop(context.scene, "hb_paper_landscape", text="Landscape")
        col.prop(context.scene, "hb_layout_scale", text="Scale")
        
        col.separator()
        
        row = col.row(align=True)
        row.operator("home_builder_layouts.fit_view_to_content", 
                    text="Fit to Content", icon='FULLSCREEN_ENTER')
        row.operator("home_builder_layouts.render_layout", 
                    text="Render", icon='RENDER_STILL')



# -----------------------------------------------------------------------------
# PANEL: 2D DETAILS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_2d_details(bpy.types.Panel):
    bl_label = "2D Details"
    bl_idname = "HOME_BUILDER_PT_2d_details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_order = 4
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        is_detail_view = context.scene.get('IS_DETAIL_VIEW', False)
        
        # Create new detail button
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("home_builder_details.create_detail", 
                    text="New Detail", icon='ADD')
        
        # List existing details
        detail_views = hb_details.DetailView.get_all_detail_views()
        
        if detail_views:
            col = layout.column(align=True)
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
            
            # Back to room button(s)
            if is_detail_view:
                col.separator()
                room_scenes = [s for s in bpy.data.scenes if not s.get('IS_LAYOUT_VIEW')]
                
                if len(room_scenes) == 1:
                    # Single room - direct button
                    op = col.operator("home_builder_layouts.go_to_layout_view",
                                     text="Back to Room", icon='LOOP_BACK')
                    op.scene_name = room_scenes[0].name
                elif len(room_scenes) > 1:
                    # Multiple rooms - show menu
                    col.menu("HOME_BUILDER_MT_room_list", text="Go Back to Room", icon='LOOP_BACK')


# SUBPANEL: Drawing Tools - REMOVED (moved to Annotations panel)
# Drawing tools are now available in the Annotations panel for all scene types


# SUBPANEL: Detail Library (only visible in detail view)
class HOME_BUILDER_PT_2d_details_library(bpy.types.Panel):
    bl_label = "Detail Library"
    bl_idname = "HOME_BUILDER_PT_2d_details_library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
    bl_parent_id = "HOME_BUILDER_PT_2d_details"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.get('IS_DETAIL_VIEW', False)
    
    def draw(self, context):
        from .. import hb_detail_library
        
        layout = self.layout
        
        # Save current detail button
        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator("home_builder_details.save_to_library", 
                    text="Save Detail to Library", icon='FILE_NEW')
        
        layout.separator()
        
        # List saved details
        details = hb_detail_library.get_library_details()
        
        if details:
            box = layout.box()
            box.label(text=f"Saved Details ({len(details)}):", icon='FILE_FOLDER')
            
            for detail in details:
                row = box.row(align=True)
                
                # Load button
                op = row.operator("home_builder_details.load_from_library",
                                 text=detail.get("name", "Unnamed"), 
                                 icon='IMPORT')
                op.filepath = detail.get("filepath", "")
                
                # Delete button
                op = row.operator("home_builder_details.delete_library_detail",
                                 text="", icon='X')
                op.filename = detail.get("filename", "")
        else:
            layout.label(text="No saved details", icon='INFO')
        
        layout.separator()
        
        # Open folder button
        layout.operator("home_builder_details.open_library_folder",
                       text="Open Library Folder", icon='FILE_FOLDER')


# -----------------------------------------------------------------------------
# PANEL 5: ANNOTATIONS
# -----------------------------------------------------------------------------
class HOME_BUILDER_PT_annotations(bpy.types.Panel):
    bl_label = "Annotations"
    bl_idname = "HOME_BUILDER_PT_annotations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
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
    bl_category = 'Home Builder'
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
        if is_layout_view or is_detail_view:
            col.operator("home_builder_details.add_dimension", 
                        text="Add Dimension", icon='DRIVER_DISTANCE')
        else:
            col.operator("home_builder_layouts.add_dimension_3d", 
                        text="Add Dimension", icon='DRIVER_DISTANCE')


# SUBPANEL: Edit Tools (for curves)
class HOME_BUILDER_PT_annotations_edit(bpy.types.Panel):
    bl_label = "Edit Tools"
    bl_idname = "HOME_BUILDER_PT_annotations_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Home Builder'
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
    bl_category = 'Home Builder'
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
        col.prop(hb_scene, "annotation_dimension_arrow_size", text="Arrow Size")
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
    bl_category = 'Home Builder'
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
    HOME_BUILDER_PT_rooms,
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
    # HOME_BUILDER_PT_layout_views_create,
    HOME_BUILDER_PT_layout_views_settings,
    HOME_BUILDER_PT_2d_details,
    HOME_BUILDER_PT_2d_details_library,
    HOME_BUILDER_PT_annotations,
    HOME_BUILDER_PT_annotations_drawing,
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
