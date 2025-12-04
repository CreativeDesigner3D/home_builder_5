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

class Face_Frame_Scene_Props(PropertyGroup):   
    
    def draw_library_ui(self,layout,context):
        layout.label(text="Face Frame Library")

    @classmethod
    def register(cls):
        bpy.types.Scene.hb_face_frame = PointerProperty(
            name="Face Frame Props",
            description="Face Frame Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.hb_face_frame            

classes = (
    Face_Frame_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)         