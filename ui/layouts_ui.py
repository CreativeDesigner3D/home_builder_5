import bpy
from .. import hb_layouts

# =============================================================================
# LAYOUT VIEWS UI PANEL
# =============================================================================

class HOME_BUILDER_PT_layout_views(bpy.types.Panel):
    bl_label = "Layout Views"
    bl_idname = "HOME_BUILDER_PT_layout_views"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Layout Views'
    
    def draw(self, context):
        layout = self.layout
        
        is_layout_view = context.scene.get('IS_LAYOUT_VIEW', False)
        
        # Layout Views List
        layout_views = hb_layouts.LayoutView.get_all_layout_views()
        
        if layout_views:
            box = layout.box()
            box.label(text=f"Layout Views ({len(layout_views)})", icon='DOCUMENTS')
            
            col = box.column(align=True)
            for scene in layout_views:
                row = col.row(align=True)
                
                if scene.get('IS_ELEVATION_VIEW'):
                    icon = 'VIEW_ORTHO'
                elif scene.get('IS_PLAN_VIEW'):
                    icon = 'MESH_GRID'
                elif scene.get('IS_3D_VIEW'):
                    icon = 'VIEW_PERSPECTIVE'
                else:
                    icon = 'SCENE_DATA'
                
                if scene == context.scene:
                    row.alert = True
                
                op = row.operator("home_builder_layouts.go_to_layout_view",
                                 text=scene.name, icon=icon)
                op.scene_name = scene.name
                
                if scene.get('IS_ELEVATION_VIEW'):
                    op = row.operator("home_builder_layouts.update_elevation_view",
                                     text="", icon='FILE_REFRESH')
                op = row.operator("home_builder_layouts.delete_layout_view",
                                 text="", icon='X')
                op.scene_name = scene.name
            
            col.separator()
            main_scenes = [s for s in bpy.data.scenes if not s.get('IS_LAYOUT_VIEW')]
            if main_scenes:
                op = col.operator("home_builder_layouts.go_to_layout_view",
                                 text="Back to 3D Model", icon='LOOP_BACK')
                op.scene_name = main_scenes[0].name
        
        # Page Settings (only show when in a layout view)
        if is_layout_view:
            box = layout.box()
            box.label(text="Page Settings", icon='FILE')
            
            col = box.column(align=True)
            
            col.prop(context.scene, "name", text="Name")
            
            if context.scene.get('IS_ELEVATION_VIEW'):
                source_wall = context.scene.get('SOURCE_WALL', 'Unknown')
                col.label(text=f"Type: Elevation ({source_wall})")
            elif context.scene.get('IS_PLAN_VIEW'):
                col.label(text="Type: Floor Plan")
            elif context.scene.get('IS_3D_VIEW'):
                col.label(text="Type: 3D View")
            
            col.separator()
            
            # Paper size and orientation
            col.prop(context.scene, "hb_paper_size", text="Paper")
            col.prop(context.scene, "hb_paper_landscape", text="Landscape")
            
            col.separator()
            
            # Scale
            col.prop(context.scene, "hb_layout_scale", text="Scale")
            
            # Fit to content button
            col.operator("home_builder_layouts.fit_view_to_content", 
                        text="Fit to Content", icon='FULLSCREEN_ENTER')
            
            # Render section
            col.separator()
            col.operator("home_builder_layouts.render_layout", 
                        text="Render Page", icon='RENDER_STILL')
        
        # Create Views Section
        box = layout.box()
        box.label(text="Create Views", icon='ADD')
        
        col = box.column(align=True)
        
        row = col.row(align=True)
        if context.object and 'IS_WALL_BP' in context.object:
            row.operator("home_builder_layouts.create_elevation_view", 
                        text="Elevation (Selected Wall)", icon='VIEW_ORTHO')
        else:
            row.label(text="Select wall for elevation", icon='INFO')
        
        col.operator("home_builder_layouts.create_all_elevations", 
                    text="All Wall Elevations", icon='DOCUMENTS')
        
        col.separator()
        col.operator("home_builder_layouts.create_plan_view", 
                    text="Floor Plan", icon='VIEW_ORTHO')
        
        col.separator()
        row = col.row(align=True)
        op = row.operator("home_builder_layouts.create_3d_view", 
                         text="3D Perspective", icon='VIEW_PERSPECTIVE')
        op.perspective = True
        
        op = row.operator("home_builder_layouts.create_3d_view", 
                         text="Isometric", icon='VIEW_ORTHO')
        op.perspective = False
        
        # Cabinet Group Layout
        col.separator()
        
        col.operator("home_builder_layouts.create_multi_view", 
                    text="Cabinet Group Layout", icon='OUTLINER_OB_GROUP_INSTANCE')
        
        # Developer Tools Section
        box = layout.box()
        box.label(text="Developer", icon='CONSOLE')
        box.operator("home_builder.reload_addon", text="Reload Add-on", icon='FILE_REFRESH')


# =============================================================================
# REGISTRATION
# =============================================================================

classes = (
    HOME_BUILDER_PT_layout_views,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
