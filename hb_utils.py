import bpy

def run_calc_fix(context,obj=None):
    if obj:
        obj.location = obj.location                  
    else:
        for obj in bpy.data.objects:
            obj.location = obj.location                                 
    context.view_layer.update()