import bpy

def run_calc_fix(context,obj=None):
    if obj:
        obj.location = obj.location                  
    else:
        for obj in bpy.data.objects:
            obj.location = obj.location                                 
    context.view_layer.update()

def add_driver_variables(driver,variables):
    for var in variables:
        new_var = driver.driver.variables.new()
        new_var.type = 'SINGLE_PROP'
        new_var.name = var.name
        new_var.targets[0].data_path = var.data_path
        new_var.targets[0].id = var.obj