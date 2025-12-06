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
        
        # Developer Tools Section
        box = layout.box()
        box.label(text="Developer", icon='CONSOLE')
        box.operator("home_builder.reload_addon", text="Reload Add-on", icon='FILE_REFRESH')        

        # Check if we're in a layout view
        is_layout_view = context.scene.get('IS_LAYOUT_VIEW', False)
        
        # Create Views Section
        box = layout.box()
        box.label(text="Create Views", icon='ADD')
        
        col = box.column(align=True)
        
        # Elevation view (requires wall selection)
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
        
        # Layout Views List
        layout_views = hb_layouts.LayoutView.get_all_layout_views()
        
        if layout_views:
            box = layout.box()
            box.label(text=f"Layout Views ({len(layout_views)})", icon='DOCUMENTS')
            
            col = box.column(align=True)
            for scene in layout_views:
                row = col.row(align=True)
                
                # Icon based on type
                if scene.get('IS_ELEVATION_VIEW'):
                    icon = 'VIEW_ORTHO'
                elif scene.get('IS_PLAN_VIEW'):
                    icon = 'MESH_GRID'
                elif scene.get('IS_3D_VIEW'):
                    icon = 'VIEW_PERSPECTIVE'
                else:
                    icon = 'SCENE_DATA'
                
                # Highlight current scene
                if scene == context.scene:
                    row.alert = True
                
                # Go to view button
                op = row.operator("home_builder_layouts.go_to_layout_view",
                                 text=scene.name, icon=icon)
                op.scene_name = scene.name
        
        # Current View Actions
        if is_layout_view:
            box = layout.box()
            box.label(text="Current View", icon='SCENE_DATA')
            
            col = box.column(align=True)
            
            # View type info
            if context.scene.get('IS_ELEVATION_VIEW'):
                source_wall = context.scene.get('SOURCE_WALL', 'Unknown')
                col.label(text=f"Elevation: {source_wall}")
                col.operator("home_builder_layouts.update_elevation_view",
                            text="Update View", icon='FILE_REFRESH')
            elif context.scene.get('IS_PLAN_VIEW'):
                col.label(text="Floor Plan")
            elif context.scene.get('IS_3D_VIEW'):
                col.label(text="3D View")
            
            col.separator()
            col.operator("home_builder_layouts.delete_layout_view",
                        text="Delete This View", icon='TRASH')
            
            # Back to main scene button
            col.separator()
            main_scenes = [s for s in bpy.data.scenes if not s.get('IS_LAYOUT_VIEW')]
            if main_scenes:
                op = col.operator("home_builder_layouts.go_to_layout_view",
                                 text="Back to 3D Model", icon='LOOP_BACK')
                op.scene_name = main_scenes[0].name
        


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
