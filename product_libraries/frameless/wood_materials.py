import math

def get_color(color):
    c1 = [1,1,1,1]
    c2 = [1,1,1,1]     
    if color == 'White':
        c1 = [0.806947, 0.752943, 0.679543, 1.000000]
        c2 = [0.806947, 0.752943, 0.679543, 1.000000] 
    if color == 'Black':
        c1 = [0.013702, 0.009721, 0.010960, 1.000000]
        c2 = [0.031896, 0.023153, 0.020289, 1.000000]
    if color == 'Blue':
        c1 = [0.057805, 0.107023, 0.138432, 1.000000]
        c2 = [0.057805, 0.107023, 0.138432, 1.000000] 
    if color == 'Green':
        c1 = [0.035601, 0.043735, 0.028426, 1.000000]
        c2 = [0.035601, 0.043735, 0.028426, 1.000000] 
    if color == 'Red':
        c1 = [0.104616, 0.049707, 0.051269, 1.000000]
        c2 = [0.072271, 0.043735, 0.045186, 1.000000] 
    if color == 'Yellow':
        c1 = [0.558337, 0.238398, 0.090842, 1.000000]
        c2 = [0.423265, 0.158961, 0.051270, 1.000000]
    if color == 'Brown':
        c1 = [0.155926, 0.068478, 0.034340, 1.000000]
        c2 = [0.086500, 0.051270, 0.038204, 1.000000] 
    if color == 'Grey':
        c1 = [0.202503, 0.193292, 0.182563, 1.000000]
        c2 = [0.119111, 0.113844, 0.107702, 1.000000] 
    return c1,c2

def update_finish_material(cabinet_style):
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

    #Assign Default Values
    c1 = [1,1,1,1]
    c2 = [1,1,1,1]
    noise_scale_1 = 0
    noise_scale_2 = 0
    texture_variation_1 = 0
    texture_variation_2 = 0
    noise_detail = 0
    voronoi_detail_1 = 0
    voronoi_detail_2 = 0
    knots_scale = 0
    knots_darkness = 0
    roughness = 1    

    if cabinet_style.wood_species == 'MAPLE':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 0.1
        texture_variation_2 = 12.5
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    if cabinet_style.wood_species == 'OAK':
        noise_scale_1 = 15.0
        noise_scale_2 = 2.5
        texture_variation_1 = 5.5
        texture_variation_2 = 1.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2  
    if cabinet_style.wood_species == 'CHERRY':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 2.0
        texture_variation_2 = 5.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    if cabinet_style.wood_species == 'WALNUT':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 11.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    if cabinet_style.wood_species == 'BIRCH':
        noise_scale_1 = 3.5
        noise_scale_2 = 0.5
        texture_variation_1 = 0.1
        texture_variation_2 = 16.0
        noise_detail = 0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2  
    if cabinet_style.wood_species == 'HICKORY':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 15.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 
    if cabinet_style.wood_species == 'ALDER':
        noise_scale_1 = 3.5
        noise_scale_2 = 2.5
        texture_variation_1 = 3.5
        texture_variation_2 = 11.0
        noise_detail = 15.0
        voronoi_detail_1 = 0.0
        voronoi_detail_2 = 0.2 

    if cabinet_style.wood_species == 'PAINT_GRADE':
        c1,c2 = get_color(cabinet_style.paint_color)
    else:
        c1,c2 = get_color(cabinet_style.stain_color)

    for input in mat_node.inputs:
        if input.name == 'Rotation':
            input.default_value[2] = math.radians(90)
        if input.name == 'Wood Color 1':
            input.default_value = c1
        if input.name == 'Wood Color 2':
            input.default_value = c2
        if input.name == 'Noise Scale 1':
            input.default_value = noise_scale_1
        if input.name == 'Noise Scale 2':
            input.default_value = noise_scale_2
        if input.name == 'Texture Variation 1':
            input.default_value = texture_variation_1
        if input.name == 'Texture Variation 2':
            input.default_value = texture_variation_2
        if input.name == 'Noise Detail':
            input.default_value = noise_detail
        if input.name == 'Voronoi Detail 1':
            input.default_value = voronoi_detail_1
        if input.name == 'Voronoi Detail 2':
            input.default_value = voronoi_detail_2
        if input.name == 'Knots Scale':
            input.default_value = knots_scale
        if input.name == 'Knots Darkness':
            input.default_value = knots_darkness
        if input.name == 'Roughness':
            input.default_value = roughness    

    for input in rotated_node.inputs:
        if input.name == 'Rotation':
            input.default_value[2] = math.radians(0)        
        if input.name == 'Wood Color 1':
            input.default_value = c1
        if input.name == 'Wood Color 2':
            input.default_value = c2
        if input.name == 'Noise Scale 1':
            input.default_value = noise_scale_1
        if input.name == 'Noise Scale 2':
            input.default_value = noise_scale_2
        if input.name == 'Texture Variation 1':
            input.default_value = texture_variation_1
        if input.name == 'Texture Variation 2':
            input.default_value = texture_variation_2
        if input.name == 'Noise Detail':
            input.default_value = noise_detail
        if input.name == 'Voronoi Detail 1':
            input.default_value = voronoi_detail_1
        if input.name == 'Voronoi Detail 2':
            input.default_value = voronoi_detail_2
        if input.name == 'Knots Scale':
            input.default_value = knots_scale
        if input.name == 'Knots Darkness':
            input.default_value = knots_darkness
        if input.name == 'Roughness':
            input.default_value = roughness