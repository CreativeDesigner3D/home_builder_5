"""
BlenderToMob Part Extractor — Extrai e decompõe módulos paramétricos em peças de marcenaria
Gera a lista de peças estruturais (laterais, bases, tampos, fundos, prateleiras, portas, gavetas)
com dimensões em milímetros, espessura, material, sentido do veio e fitas de borda.
"""

from .nesting import NestingPart


def extract_parts_from_scene(context):
    """
    Percorre todos os objetos da cena atual e extrai as peças individuais
    de marcenaria dos módulos paramétricos e elementos cadastrados.

    Retorna:
        Uma lista de objetos NestingPart.
    """
    parts = []
    scene = context.scene
    dim_settings = getattr(scene.btm_settings, 'dimension_settings', None)

    # Espessuras padrão caso não haja configurador
    def_carcass_th = (dim_settings.carcass_thickness * 1000.0) if dim_settings else 15.0
    def_back_th = (dim_settings.back_thickness * 1000.0) if dim_settings else 6.0
    def_door_th = (dim_settings.door_thickness * 1000.0) if dim_settings else 18.0
    def_shelf_th = (dim_settings.shelf_thickness * 1000.0) if dim_settings else 15.0

    for obj in scene.objects:
        if obj.type != 'MESH':
            continue

        # Verifica se o objeto é um módulo BlenderToMob ou possui propriedades de marcenaria
        is_btm_module = hasattr(obj, 'btm_plane') and obj.btm_plane.object_kind == 'MODULE'

        if is_btm_module:
            cab = getattr(obj, 'btm_cabinet', None)

            # Dimensões gerais em milímetros
            if cab:
                width_mm = cab.width * 1000.0
                height_mm = cab.height * 1000.0
                depth_mm = cab.depth * 1000.0
                carcass_th = (cab.thickness * 1000.0) if cab.thickness > 0 else def_carcass_th
                door_swing = cab.door_swing
            else:
                dims = obj.dimensions
                width_mm = dims.x * 1000.0
                height_mm = dims.z * 1000.0
                depth_mm = dims.y * 1000.0
                carcass_th = def_carcass_th
                door_swing = 'LEFT'

            mod_name = obj.name

            # 1. Laterais (Esquerda e Direita)
            # Altura = Altura total do móvel; Largura/Comprimento = Profundidade do móvel
            parts.append(NestingPart(
                id=f"{mod_name}_LAT_ESQ",
                name=f"Lateral Esquerda - {mod_name}",
                width=depth_mm,
                height=height_mm,
                thickness=carcass_th,
                quantity=1,
                material="MDF Branco TX",
                grain_direction='VERTICAL',
                module_ref=mod_name,
                edge_top=0.45,
                edge_bottom=0.45,
                edge_left=0.45,
                edge_right=1.0  # Fita frontal mais espessa
            ))

            parts.append(NestingPart(
                id=f"{mod_name}_LAT_DIR",
                name=f"Lateral Direita - {mod_name}",
                width=depth_mm,
                height=height_mm,
                thickness=carcass_th,
                quantity=1,
                material="MDF Branco TX",
                grain_direction='VERTICAL',
                module_ref=mod_name,
                edge_top=0.45,
                edge_bottom=0.45,
                edge_left=0.45,
                edge_right=1.0
            ))

            # 2. Base Inferior e Tampo Superior
            # Largura = Largura interna (Largura total - 2 * espessura da lateral); Altura = Profundidade
            internal_width = max(50.0, width_mm - (2.0 * carcass_th))

            parts.append(NestingPart(
                id=f"{mod_name}_BASE",
                name=f"Base Inferior - {mod_name}",
                width=internal_width,
                height=depth_mm,
                thickness=carcass_th,
                quantity=1,
                material="MDF Branco TX",
                grain_direction='HORIZONTAL',
                module_ref=mod_name,
                edge_top=0.45,
                edge_bottom=0.45,
                edge_left=0.45,
                edge_right=1.0
            ))

            parts.append(NestingPart(
                id=f"{mod_name}_TAMPO",
                name=f"Tampo Superior - {mod_name}",
                width=internal_width,
                height=depth_mm,
                thickness=carcass_th,
                quantity=1,
                material="MDF Branco TX",
                grain_direction='HORIZONTAL',
                module_ref=mod_name,
                edge_top=0.45,
                edge_bottom=0.45,
                edge_left=0.45,
                edge_right=1.0
            ))

            # 3. Fundo do Armário (Painel Traseiro)
            # Altura e largura com encaixe de rebaixo (canal)
            back_width = max(50.0, width_mm - (2.0 * carcass_th) + 16.0)
            back_height = max(50.0, height_mm - (2.0 * carcass_th) + 16.0)

            parts.append(NestingPart(
                id=f"{mod_name}_FUNDO",
                name=f"Fundo Traseiro - {mod_name}",
                width=back_width,
                height=back_height,
                thickness=def_back_th,
                quantity=1,
                material="MDF 6mm Branco",
                grain_direction='VERTICAL',
                module_ref=mod_name,
                edge_top=0.0,
                edge_bottom=0.0,
                edge_left=0.0,
                edge_right=0.0
            ))

            # 4. Prateleira Interna Móvel/Fixa
            parts.append(NestingPart(
                id=f"{mod_name}_PRAT_01",
                name=f"Prateleira Interna - {mod_name}",
                width=max(50.0, internal_width - 2.0),
                height=max(50.0, depth_mm - 20.0),
                thickness=def_shelf_th,
                quantity=1,
                material="MDF Branco TX",
                grain_direction='HORIZONTAL',
                module_ref=mod_name,
                edge_top=0.45,
                edge_bottom=0.45,
                edge_left=0.45,
                edge_right=1.0
            ))

            # 5. Portas / Frentes
            if door_swing != 'NONE':
                if door_swing == 'DOUBLE':
                    door_w = max(50.0, (width_mm / 2.0) - 3.0)
                    door_h = max(50.0, height_mm - 4.0)
                    parts.append(NestingPart(
                        id=f"{mod_name}_PORTA_PAR",
                        name=f"Portas Frontais (Par) - {mod_name}",
                        width=door_w,
                        height=door_h,
                        thickness=def_door_th,
                        quantity=2,
                        material="MDF Amadeirado / Cor",
                        grain_direction='VERTICAL',
                        module_ref=mod_name,
                        edge_top=1.0,
                        edge_bottom=1.0,
                        edge_left=1.0,
                        edge_right=1.0
                    ))
                else:
                    door_w = max(50.0, width_mm - 4.0)
                    door_h = max(50.0, height_mm - 4.0)
                    parts.append(NestingPart(
                        id=f"{mod_name}_PORTA_UN",
                        name=f"Porta Frontal - {mod_name}",
                        width=door_w,
                        height=door_h,
                        thickness=def_door_th,
                        quantity=1,
                        material="MDF Amadeirado / Cor",
                        grain_direction='VERTICAL',
                        module_ref=mod_name,
                        edge_top=1.0,
                        edge_bottom=1.0,
                        edge_left=1.0,
                        edge_right=1.0
                    ))

    return parts
