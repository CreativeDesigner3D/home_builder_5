import bpy

def build_material(name, color=(0.8, 0.7, 0.6, 1.0), roughness=0.4, texture_path=None, mapping_mode='CUBE', scale=(1.0, 1.0), rotation=0.0):
    """Creates a custom Principled BSDF material with custom node setup."""
    # Check if material already exists
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Standard output and Principled BSDF nodes
    node_output = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Roughness'].default_value = roughness
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])

    if texture_path:
        try:
            # Set up image texture node
            node_tex = nodes.new('ShaderNodeTexImage')
            img = bpy.data.images.load(texture_path, check_existing=True)
            node_tex.image = img

            # Texturing mapping nodes
            node_coord = nodes.new('ShaderNodeTexCoord')
            node_mapping = nodes.new('ShaderNodeMapping')

            node_mapping.inputs['Scale'].default_value = (scale[0], scale[1], 1.0)
            node_mapping.inputs['Rotation'].default_value = (0.0, 0.0, rotation)

            # Select texture coordinate output based on mapping mode
            if mapping_mode == 'CUBE':
                links.new(node_coord.outputs['Generated'], node_mapping.inputs['Vector'])
            else: # PLANAR / UV
                links.new(node_coord.outputs['UV'], node_mapping.inputs['Vector'])

            links.new(node_mapping.outputs['Vector'], node_tex.inputs['Vector'])

            # Add a Hue Saturation Value node for tone tweaking
            node_hsv = nodes.new('ShaderNodeHueSatVal')
            links.new(node_tex.outputs['Color'], node_hsv.inputs['Color'])
            links.new(node_hsv.outputs['Color'], node_bsdf.inputs['Base Color'])

        except Exception as e:
            print(f"Error loading texture {texture_path}: {e}")
            # Fallback to base color
            node_bsdf.inputs['Base Color'].default_value = color
    else:
        # Solid color default
        node_bsdf.inputs['Base Color'].default_value = color

    return mat

def update_material_hsv(mat_name, hue=0.5, saturation=1.0, value=1.0):
    """Updates the HSV node of a material to tweak color tones without rebuilding the graph."""
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.use_nodes:
        return False

    nodes = mat.node_tree.nodes
    hsv_node = None
    for node in nodes:
        if node.type == 'HUE_SAT':
            hsv_node = node
            break

    if hsv_node:
        hsv_node.inputs['Hue'].default_value = hue
        hsv_node.inputs['Saturation'].default_value = saturation
        hsv_node.inputs['Value'].default_value = value
        return True

    return False
