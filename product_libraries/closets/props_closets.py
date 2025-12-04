import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )

class Closets_Scene_Props(PropertyGroup):   
    
    def draw_library_ui(self,layout,context):
        layout.label(text="Closets Library")

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_closets = PointerProperty(
            name="Closets Props",
            description="Pro Kitchen Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_closets            

classes = (
    Closets_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)         