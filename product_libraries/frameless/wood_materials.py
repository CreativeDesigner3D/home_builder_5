import math
from . import finish_colors


def get_color(color_name, color_type='stain'):
    """Get color pair for a given color name.
    
    Args:
        color_name: Name of the color (e.g. 'Natural', 'Espresso')
        color_type: 'stain' or 'paint'
    
    Returns:
        (c1, c2) tuple of RGBA lists
    """
    data = finish_colors.get_color_data(color_name, color_type)
    
    c1 = data.get('color_1', [1, 1, 1, 1])
    c2 = data.get('color_2', [1, 1, 1, 1])
    return c1, c2


def update_finish_material(cabinet_style):
    """Update the finish material nodes based on the cabinet style settings.
    
    Reads wood species + color settings from the cabinet style,
    applies all shader parameters to the Wood node group.
    """
    material = cabinet_style.material
    material_rotated = cabinet_style.material_rotated

    mat_node = None
    rotated_node = None

    for n in material.node_tree.nodes:
        if n.label == 'Wood':
            mat_node = n
            break

    for n in material_rotated.node_tree.nodes:
        if n.label == 'Wood':
            rotated_node = n
            break

    if not mat_node or not rotated_node:
        return

    # --- Determine color type and get color data ---
    if cabinet_style.wood_species == 'PAINT_GRADE':
        color_name = cabinet_style.paint_color
        color_type = 'paint'
    else:
        color_name = cabinet_style.stain_color
        color_type = 'stain'

    color_data = finish_colors.get_color_data(color_name, color_type)

    c1 = color_data.get('color_1', [1, 1, 1, 1])
    c2 = color_data.get('color_2', [1, 1, 1, 1])

    # --- Determine wood grain parameters from species ---
    noise_scale_1 = 0
    noise_scale_2 = 0
    texture_variation_1 = 0
    texture_variation_2 = 0
    noise_detail = 0
    voronoi_detail_1 = 0
    voronoi_detail_2 = 0
    knots_scale = 0
    knots_darkness = 0

    if cabinet_style.wood_species == 'MAPLE':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 0.1
        texture_variation_2 = 12.5
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    elif cabinet_style.wood_species == 'OAK':
        noise_scale_1 = 15.0
        noise_scale_2 = 2.5
        texture_variation_1 = 5.5
        texture_variation_2 = 1.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2  
    elif cabinet_style.wood_species == 'CHERRY':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 2.0
        texture_variation_2 = 5.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    elif cabinet_style.wood_species == 'WALNUT':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 11.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    elif cabinet_style.wood_species == 'BIRCH':
        noise_scale_1 = 3.5
        noise_scale_2 = 0.5
        texture_variation_1 = 0.1
        texture_variation_2 = 16.0
        noise_detail = 0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2  
    elif cabinet_style.wood_species == 'HICKORY':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 15.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    elif cabinet_style.wood_species == 'ALDER':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 11.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 

    # --- Apply color overrides from color data (user adjustable) ---
    roughness = color_data.get('roughness', finish_colors.SHADER_DEFAULTS['roughness'])
    noise_bump_strength = color_data.get('noise_bump_strength', finish_colors.SHADER_DEFAULTS['noise_bump_strength'])
    knots_bump_strength = color_data.get('knots_bump_strength', finish_colors.SHADER_DEFAULTS['knots_bump_strength'])
    wood_bump_strength = color_data.get('wood_bump_strength', finish_colors.SHADER_DEFAULTS['wood_bump_strength'])

    # --- Apply to both material and rotated material ---
    for node, rotation in [(mat_node, math.radians(90)), (rotated_node, math.radians(0))]:
        for inp in node.inputs:
            if inp.name == 'Rotation':
                inp.default_value[2] = rotation
            elif inp.name == 'Wood Color 1':
                inp.default_value = c1
            elif inp.name == 'Wood Color 2':
                inp.default_value = c2
            elif inp.name == 'Noise Scale 1':
                inp.default_value = noise_scale_1
            elif inp.name == 'Noise Scale 2':
                inp.default_value = noise_scale_2
            elif inp.name == 'Texture Variation 1':
                inp.default_value = texture_variation_1
            elif inp.name == 'Texture Variation 2':
                inp.default_value = texture_variation_2
            elif inp.name == 'Noise Detail':
                inp.default_value = noise_detail
            elif inp.name == 'Voronoi Detail 1':
                inp.default_value = voronoi_detail_1
            elif inp.name == 'Voronoi Detail 2':
                inp.default_value = voronoi_detail_2
            elif inp.name == 'Knots Scale':
                inp.default_value = knots_scale
            elif inp.name == 'Knots Darkness':
                inp.default_value = knots_darkness
            elif inp.name == 'Roughness':
                inp.default_value = roughness
            elif inp.name == 'Noise Bump Strength':
                inp.default_value = noise_bump_strength
            elif inp.name == 'Knots Bump Strength':
                inp.default_value = knots_bump_strength
            elif inp.name == 'Wood Bump Strength':
                inp.default_value = wood_bump_strength
