import bpy  # type: ignore


# ---------------------------------------------------------------------------
# Update callbacks — regenerate geometry/drivers when property changes
# ---------------------------------------------------------------------------

def update_wall_geom(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        import json
        segments_str = obj.get("btm_wall_segments", "")
        if segments_str:
            try:
                segments_data = json.loads(segments_str)
                for seg in segments_data:
                    seg['thickness'] = self.thickness
                    seg['height'] = self.height_start
                obj["btm_wall_segments"] = json.dumps(segments_data)
                from ..geometry.mesh_gen import generate_wall_from_segments
                generate_wall_from_segments(obj, segments_data)
                return
            except Exception:
                pass

        # Fallback for single-segment walls
        from ..geometry.mesh_gen import generate_wall_mesh
        generate_wall_mesh(obj, self.length, self.thickness, self.height_start)


def update_cabinet_geom(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        from ..geometry.mesh_gen import generate_cabinet_mesh
        generate_cabinet_mesh(obj, self.width, self.height, self.depth, self.thickness)

        # Atualiza a geometria da porta e o controlador vazio
        from ..geometry import door_controller
        door_controller.update_door_geometry_and_controller(obj)


def update_door_properties(self, context):
    obj = self.id_data
    if obj and obj.type == 'MESH':
        from ..geometry import door_controller
        door_controller.update_door_rotation_from_property(obj)


def update_scene_unit(self, context):
    unit_settings = context.scene.unit_settings
    unit_settings.system = 'METRIC'
    if self.btm_unit == 'METERS':
        unit_settings.length_unit = 'METERS'
    elif self.btm_unit == 'CENTIMETERS':
        unit_settings.length_unit = 'CENTIMETERS'
    elif self.btm_unit == 'MILLIMETERS':
        unit_settings.length_unit = 'MILLIMETERS'
    # Cotas legadas já criadas passam a mostrar a nova unidade.
    from .. import hb_types
    hb_types.refresh_dimension_units(context.scene)


# ---------------------------------------------------------------------------
# Wall Segment PropertyGroup
# ---------------------------------------------------------------------------

class BTM_PG_WallSegment(bpy.types.PropertyGroup):
    length: bpy.props.FloatProperty(
        name="Comprimento",
        description="Comprimento do segmento de parede",
        default=2.0,
        min=0.01,
        max=100.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )  # type: ignore
    absolute_angle: bpy.props.FloatProperty(
        name="Ângulo Absoluto (°)",
        description="Ângulo do segmento em relação ao sistema global",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )  # type: ignore
    relative_angle: bpy.props.FloatProperty(
        name="Ângulo Relativo (°)",
        description="Ângulo em relação ao segmento anterior",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype='ANGLE'
    )  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Espessura",
        description="Espessura da parede",
        default=0.15,
        min=0.01,
        max=2.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )  # type: ignore
    height_start: bpy.props.FloatProperty(
        name="Pé-Direito Inicial",
        description="Altura da parede no ponto inicial",
        default=2.7,
        min=0.1,
        max=10.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )  # type: ignore
    height_end: bpy.props.FloatProperty(
        name="Pé-Direito Final",
        description="Altura da parede no ponto final",
        default=2.7,
        min=0.1,
        max=10.0,
        subtype='DISTANCE',
        update=update_wall_geom
    )  # type: ignore
    offset: bpy.props.FloatProperty(
        name="Afastamento",
        description="Afastamento da base da parede em relação ao piso",
        default=0.0,
        subtype='DISTANCE'
    )  # type: ignore
    sagitta: bpy.props.FloatProperty(
        name="Flecha",
        description="Flecha do arco para paredes curvas (0 para retas)",
        default=0.0,
        subtype='DISTANCE'
    )  # type: ignore
    linear_increment: bpy.props.FloatProperty(
        name="Incr. Linear",
        description="Passo do salto do cursor referente ao comprimento",
        default=0.05,
        min=0.001,
        max=1.0,
        subtype='DISTANCE'
    )  # type: ignore
    angular_increment: bpy.props.FloatProperty(
        name="Incr. Angular (°)",
        description="Passo do ângulo quando ajustado pelo mouse",
        default=5.0,
        min=0.5,
        max=90.0,
        subtype='ANGLE'
    )  # type: ignore
    orientation: bpy.props.EnumProperty(
        name="Construção",
        description="Lado da parede que recebe o valor de comprimento",
        items=[
            ('RIGHT', "Direita", "Construção no sentido horário"),
            ('LEFT', "Esquerda", "Construção no sentido anti-horário")
        ],
        default='RIGHT'
    )  # type: ignore
    wall_type: bpy.props.EnumProperty(
        name="Tipo de Parede",
        description="Preset de material/espessura/acabamento",
        items=[
            ('NORMAL', "Normal", "Parede de alvenaria padrão"),
            ('DRYWALL', "Drywall", "Parede de gesso acartonado"),
            ('GLASS', "Vidro", "Parede de vidro tempoerado"),
        ],
        default='NORMAL'
    )  # type: ignore
    use_as_default: bpy.props.BoolProperty(
        name="Utilizar valores como padrão",
        description="Salvar estes valores como padrão para novas paredes",
        default=False
    )  # type: ignore


# ---------------------------------------------------------------------------
# Insertion Plane PropertyGroup
# ---------------------------------------------------------------------------

class BTM_PG_InsertionPlane(bpy.types.PropertyGroup):
    object_kind: bpy.props.EnumProperty(
        name="Tipo de Objeto",
        items=[
            ('WALL', "Parede", "Parede de alvenaria"),
            ('FLOOR', "Piso", "Piso de referência"),
            ('MODULE', "Módulo", "Módulo de marcenaria/armário"),
            ('GEOMETRY', "Geometria", "Geometria livre paramétrica"),
            ('OPENING', "Abertura", "Porta ou janela de ambiente"),
        ],
        default='WALL'
    )  # type: ignore
    parent_plane: bpy.props.PointerProperty(
        name="Plano Pai",
        type=bpy.types.Object
    )  # type: ignore
    layer_id: bpy.props.StringProperty(
        name="ID da Camada",
        default="Default"
    )  # type: ignore
    collision_override: bpy.props.EnumProperty(
        name="Colisão",
        items=[
            ('INHERIT', "Herdar", "Herdar configuração global"),
            ('ON', "Ativa", "Colisão ativa"),
            ('OFF', "Desativada", "Ignorar colisão")
        ],
        default='INHERIT'
    )  # type: ignore


# ---------------------------------------------------------------------------
# Opening Properties (Portas e Janelas)
# ---------------------------------------------------------------------------

class BTM_PG_OpeningProperties(bpy.types.PropertyGroup):
    opening_type: bpy.props.EnumProperty(
        name="Tipo de Abertura",
        description="Tipo de abertura de parede",
        items=[
            ('DOOR', "Porta", "Porta de ambiente"),
            ('WINDOW', "Janela", "Janela de ambiente"),
        ],
        default='DOOR'
    )  # type: ignore
    width: bpy.props.FloatProperty(
        name="Largura",
        description="Largura do vão da abertura",
        default=0.8,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )  # type: ignore
    height: bpy.props.FloatProperty(
        name="Altura",
        description="Altura do vão da abertura",
        default=2.1,
        min=0.1,
        max=5.0,
        subtype='DISTANCE'
    )  # type: ignore
    sill_height: bpy.props.FloatProperty(
        name="Peitoril",
        description="Afastamento do piso até a base da abertura (0 para portas)",
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='DISTANCE'
    )  # type: ignore
    parent_wall: bpy.props.PointerProperty(
        name="Parede",
        description="Parede que contém esta abertura",
        type=bpy.types.Object
    )  # type: ignore


# ---------------------------------------------------------------------------
# Cabinet Properties
# ---------------------------------------------------------------------------

class BTM_PG_CabinetProperties(bpy.types.PropertyGroup):
    width: bpy.props.FloatProperty(
        name="Largura",
        default=0.8,
        min=0.1,
        max=3.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )  # type: ignore
    height: bpy.props.FloatProperty(
        name="Altura",
        default=0.7,
        min=0.1,
        max=3.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )  # type: ignore
    depth: bpy.props.FloatProperty(
        name="Profundidade",
        default=0.55,
        min=0.1,
        max=2.0,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Espessura Chapas",
        default=0.018,
        min=0.006,
        max=0.05,
        subtype='DISTANCE',
        update=update_cabinet_geom
    )  # type: ignore
    cabinet_type: bpy.props.EnumProperty(
        name="Tipo de Armário",
        items=[
            ('BASE', "Balcão Inferior", ""),
            ('WALL', "Aéreo", ""),
            ('TALL', "Paneleiro/Despensa", "")
        ],
        default='BASE'
    )  # type: ignore

    # Propriedades de abertura e swing da porta
    door_open: bpy.props.FloatProperty(
        name="Abertura Porta",
        description="Porcentagem de abertura da porta (0.0 = Fechada, 1.0 = Totalmente Aberta)",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=update_door_properties
    )  # type: ignore
    door_swing: bpy.props.EnumProperty(
        name="Sentido Abertura",
        description="Tipo e sentido de abertura das portas",
        items=[
            ('NONE', "Sem Porta", ""),
            ('LEFT', "Esquerda", "Porta simples abrindo para a esquerda"),
            ('RIGHT', "Direita", "Porta simples abrindo para a direita"),
            ('DOUBLE', "Dupla", "Portas duplas abrindo para os lados"),
            ('FLIP', "Basculante", "Porta abrindo para cima"),
        ],
        default='LEFT',
        update=update_cabinet_geom
    )  # type: ignore


# ---------------------------------------------------------------------------
# Component Configuration PropertyGroup (Dimension Configurator)
# ---------------------------------------------------------------------------

class BTM_PG_ComponentConfig(bpy.types.PropertyGroup):
    material: bpy.props.EnumProperty(
        name="Material",
        items=[
            ('MDF', "MDF", ""),
            ('MDP', "MDP", ""),
            ('WOOD', "Madeira Maciça", ""),
        ],
        default='MDF'
    )  # type: ignore
    max_width: bpy.props.FloatProperty(
        name="Largura Máxima da Chapa",
        default=2.73,
        min=0.1,
        max=10.0,
        subtype='DISTANCE'
    )  # type: ignore
    max_length: bpy.props.FloatProperty(
        name="Comprimento Máximo da Chapa",
        default=1.81,
        min=0.1,
        max=10.0,
        subtype='DISTANCE'
    )  # type: ignore
    thickness: bpy.props.FloatProperty(
        name="Espessura da Chapa",
        default=0.015,
        min=0.003,
        max=0.1,
        subtype='DISTANCE'
    )  # type: ignore
    # Edge bands (fitas de borda)
    edge_1: bpy.props.FloatProperty(
        name="Fita Borda 1 (Superior)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )  # type: ignore
    edge_2: bpy.props.FloatProperty(
        name="Fita Borda 2 (Inferior)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )  # type: ignore
    edge_3: bpy.props.FloatProperty(
        name="Fita Borda 3 (Direita/Traseira)",
        default=0.0,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )  # type: ignore
    edge_4: bpy.props.FloatProperty(
        name="Fita Borda 4 (Esquerda/Frontal)",
        default=0.0004,
        min=0.0,
        max=0.05,
        subtype='DISTANCE'
    )  # type: ignore


# ---------------------------------------------------------------------------
# MDF Sheet Limitations & Configuration
# ---------------------------------------------------------------------------

def update_mdf_format(self, context):
    if self.sheet_format == '2750x1830':
        self.sheet_width = 2.750
        self.sheet_height = 1.830
    elif self.sheet_format == '2440x1220':
        self.sheet_width = 2.440
        self.sheet_height = 1.220
    elif self.sheet_format == '2500x1600':
        self.sheet_width = 2.500
        self.sheet_height = 1.600
    elif self.sheet_format == '1830x1830':
        self.sheet_width = 1.830
        self.sheet_height = 1.830


class BTM_PG_MDFSheetConfig(bpy.types.PropertyGroup):
    sheet_format: bpy.props.EnumProperty(
        name="Formato Padrão",
        description="Formatos comerciais padrão de chapas MDF no mercado brasileiro",
        items=[
            ('2750x1830', "2750 x 1830 mm (Padrão Brasil)", "Chapa MDF padrão brasileira"),
            ('2440x1220', "2440 x 1220 mm (Padrão 8x4)", "Chapa 8x4 pés internacional"),
            ('2500x1600', "2500 x 1600 mm", "Formato intermediário"),
            ('1830x1830', "1830 x 1830 mm (Quadrada)", "Chapa quadrada"),
            ('CUSTOM', "Personalizado", "Definir dimensões manuais"),
        ],
        default='2750x1830',
        update=update_mdf_format
    )  # type: ignore

    sheet_width: bpy.props.FloatProperty(
        name="Largura da Chapa",
        description="Largura nominal da chapa de MDF",
        default=2.750,
        min=0.5,
        max=10.0,
        subtype='DISTANCE'
    )  # type: ignore

    sheet_height: bpy.props.FloatProperty(
        name="Altura da Chapa",
        description="Altura/comprimento nominal da chapa de MDF",
        default=1.830,
        min=0.5,
        max=10.0,
        subtype='DISTANCE'
    )  # type: ignore

    refilo_top: bpy.props.FloatProperty(
        name="Refilo Superior",
        description="Margem de descarte na borda superior da chapa",
        default=0.010,
        min=0.0,
        max=0.100,
        subtype='DISTANCE'
    )  # type: ignore

    refilo_bottom: bpy.props.FloatProperty(
        name="Refilo Inferior",
        description="Margem de descarte na borda inferior da chapa",
        default=0.010,
        min=0.0,
        max=0.100,
        subtype='DISTANCE'
    )  # type: ignore

    refilo_left: bpy.props.FloatProperty(
        name="Refilo Esquerdo",
        description="Margem de descarte na borda esquerda da chapa",
        default=0.010,
        min=0.0,
        max=0.100,
        subtype='DISTANCE'
    )  # type: ignore

    refilo_right: bpy.props.FloatProperty(
        name="Refilo Direito",
        description="Margem de descarte na borda direita da chapa",
        default=0.010,
        min=0.0,
        max=0.100,
        subtype='DISTANCE'
    )  # type: ignore

    kerf: bpy.props.FloatProperty(
        name="Espessura da Serra (Kerf)",
        description="Espessura do corte da lâmina de serra",
        default=0.004,
        min=0.001,
        max=0.020,
        subtype='DISTANCE'
    )  # type: ignore

    allow_rotation: bpy.props.BoolProperty(
        name="Permitir Rotação",
        description="Permite girar peças quando não houver restrição de veio da madeira",
        default=True
    )  # type: ignore

    respect_grain: bpy.props.BoolProperty(
        name="Respeitar Veio da Madeira",
        description="Garante que peças com textura amadeirada mantenham a orientação correta",
        default=True
    )  # type: ignore


# ---------------------------------------------------------------------------
# Global Dimension Settings (Dimension Configurator)
# ---------------------------------------------------------------------------

def update_dimension_preset(self, context):
    from .dimensions_preset import DIMENSION_PRESETS
    if self.preset in DIMENSION_PRESETS:
        p = DIMENSION_PRESETS[self.preset]
        self.width_default = p['width_default']
        self.width_min = p['width_min']
        self.width_max = p['width_max']
        self.height_default = p['height_default']
        self.height_min = p['height_min']
        self.height_max = p['height_max']
        self.depth_default = p['depth_default']
        self.depth_min = p['depth_min']
        self.depth_max = p['depth_max']
        self.step_increment = p['step_increment']
        self.base_height = p['base_height']
        self.wall_clearance = p['wall_clearance']
        self.carcass_thickness = p['carcass_thickness']
        self.back_thickness = p['back_thickness']
        self.door_thickness = p['door_thickness']
        self.shelf_thickness = p['shelf_thickness']
        self.door_gap = p['door_gap']
        self.back_inset = p['back_inset']
        self.groove_depth = p['groove_depth']
        self.edge_front = p['edge_front']
        self.edge_back = p['edge_back']
        self.edge_top = p['edge_top']
        self.edge_bottom = p['edge_bottom']


class BTM_PG_DimensionSettings(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        name="Preset de Marcenaria",
        description="Padrões dimensionais pré-configurados",
        items=[
            ('COZINHA_INFERIOR', "Cozinha - Balcão Inferior", "Balcões baixos de cozinha"),
            ('COZINHA_AEREO', "Cozinha - Armário Aéreo", "Armários suspensos de cozinha"),
            ('DORMITORIO_ROUPEIRO', "Dormitório - Roupeiro", "Guarda-roupas e roupeiros"),
            ('BANHEIRO_GABINETE', "Banheiro - Gabinete", "Gabinetes e toucadores"),
            ('PROMOB_STANDARD', "Promob Standard Brasil", "Padrão de fábrica Promob"),
            ('CUSTOM', "Personalizado", "Ajustes manuais"),
        ],
        default='COZINHA_INFERIOR',
        update=update_dimension_preset
    )  # type: ignore

    # Dimensões Gerais
    width_default: bpy.props.FloatProperty(name="Largura Padrão", default=0.80, min=0.1, max=5.0, subtype='DISTANCE')  # type: ignore
    width_min: bpy.props.FloatProperty(name="Largura Mínima", default=0.30, min=0.05, max=5.0, subtype='DISTANCE')  # type: ignore
    width_max: bpy.props.FloatProperty(name="Largura Máxima", default=1.20, min=0.1, max=5.0, subtype='DISTANCE')  # type: ignore

    height_default: bpy.props.FloatProperty(name="Altura Padrão", default=0.72, min=0.1, max=5.0, subtype='DISTANCE')  # type: ignore
    height_min: bpy.props.FloatProperty(name="Altura Mínima", default=0.30, min=0.05, max=5.0, subtype='DISTANCE')  # type: ignore
    height_max: bpy.props.FloatProperty(name="Altura Máxima", default=2.60, min=0.1, max=5.0, subtype='DISTANCE')  # type: ignore

    depth_default: bpy.props.FloatProperty(name="Profundidade Padrão", default=0.55, min=0.1, max=3.0, subtype='DISTANCE')  # type: ignore
    depth_min: bpy.props.FloatProperty(name="Profundidade Mínima", default=0.20, min=0.05, max=3.0, subtype='DISTANCE')  # type: ignore
    depth_max: bpy.props.FloatProperty(name="Profundidade Máxima", default=0.80, min=0.1, max=3.0, subtype='DISTANCE')  # type: ignore

    step_increment: bpy.props.FloatProperty(name="Passo / Incremento", default=0.05, min=0.001, max=0.5, subtype='DISTANCE')  # type: ignore
    base_height: bpy.props.FloatProperty(name="Altura do Rodapé / Base", default=0.15, min=0.0, max=0.5, subtype='DISTANCE')  # type: ignore
    wall_clearance: bpy.props.FloatProperty(name="Afastamento Traseiro", default=0.015, min=0.0, max=0.1, subtype='DISTANCE')  # type: ignore

    # Espessuras de Chapas
    carcass_thickness: bpy.props.FloatProperty(name="Espessura Caixa/Laterais", default=0.015, min=0.006, max=0.05, subtype='DISTANCE')  # type: ignore
    back_thickness: bpy.props.FloatProperty(name="Espessura do Fundo", default=0.006, min=0.003, max=0.025, subtype='DISTANCE')  # type: ignore
    door_thickness: bpy.props.FloatProperty(name="Espessura das Portas", default=0.018, min=0.006, max=0.05, subtype='DISTANCE')  # type: ignore
    shelf_thickness: bpy.props.FloatProperty(name="Espessura Prateleiras", default=0.015, min=0.006, max=0.05, subtype='DISTANCE')  # type: ignore

    # Folgas e Recuos
    door_gap: bpy.props.FloatProperty(name="Folga entre Portas", default=0.0025, min=0.0005, max=0.02, subtype='DISTANCE')  # type: ignore
    back_inset: bpy.props.FloatProperty(name="Recuo do Fundo", default=0.015, min=0.0, max=0.05, subtype='DISTANCE')  # type: ignore
    groove_depth: bpy.props.FloatProperty(name="Profundidade do Canal", default=0.008, min=0.0, max=0.02, subtype='DISTANCE')  # type: ignore

    # Fitas de Borda
    edge_front: bpy.props.FloatProperty(name="Fita Frontal", default=0.001, min=0.0, max=0.01, subtype='DISTANCE')  # type: ignore
    edge_back: bpy.props.FloatProperty(name="Fita Traseira", default=0.0004, min=0.0, max=0.01, subtype='DISTANCE')  # type: ignore
    edge_top: bpy.props.FloatProperty(name="Fita Superior", default=0.0004, min=0.0, max=0.01, subtype='DISTANCE')  # type: ignore
    edge_bottom: bpy.props.FloatProperty(name="Fita Inferior", default=0.0004, min=0.0, max=0.01, subtype='DISTANCE')  # type: ignore


# ---------------------------------------------------------------------------
# Scene Settings (Global)
# ---------------------------------------------------------------------------

class BTM_PG_SceneSettings(bpy.types.PropertyGroup):
    btm_active_tab: bpy.props.EnumProperty(
        name="Aba Ativa",
        items=[
            ('CONSTRUTOR', "CONSTRUTOR", "Ferramentas de desenho e construção", 'GREASEPENCIL', 0),
            ('GALERIA', "GALERIA", "Galeria de móveis e componentes", 'ASSET_MANAGER', 1),
            ('CONFIGURACOES', "CONFIGURAÇÕES", "Configurações do projeto e dimensões", 'PREFERENCES', 2),
            ('PLANO_CORTE', "PLANO DE CORTE", "Plano de corte e nesting", 'ALIGN_JUSTIFY', 3),
        ],
        default='CONSTRUTOR'
    )  # type: ignore

    # Dropdown de Unidade do add-on
    btm_unit: bpy.props.EnumProperty(
        name="Unidade",
        description="Escolha a unidade de medida do projeto",
        items=[
            ('METERS', "Metros (m)", "Entrada e exibição em metros"),
            ('CENTIMETERS', "Centímetros (cm)", "Entrada e exibição em centímetros"),
            ('MILLIMETERS', "Milímetros (mm)", "Entrada e exibição em milímetros"),
        ],
        default='MILLIMETERS',
        update=update_scene_unit
    )  # type: ignore

    # Snap settings
    snap_grid: bpy.props.BoolProperty(
        name="Snap ao Grid",
        description="Ativa o snap posicional em incrementos fixos",
        default=True
    )  # type: ignore
    snap_increment: bpy.props.FloatProperty(
        name="Incremento de Snap",
        description="Passo do snap para posicionamento",
        default=0.05,
        min=0.001,
        max=1.0,
        subtype='DISTANCE'
    )  # type: ignore
    collision_global: bpy.props.BoolProperty(
        name="Evitar Sobreposição",
        description=("Ligado, nenhum módulo ocupa o espaço de outro nem atravessa paredes ao ser posicionado; "
                     "desligado, sobrepor é permitido (RN-13)"),
        default=True
    )  # type: ignore
    save_fronts_open: bpy.props.BoolProperty(
        name="Salvar com Frentes Abertas",
        description=("Desligado (padrão), portas e gavetas abertas para inspeção são salvas fechadas e continuam "
                     "abertas na tela (RN-14)"),
        default=False
    )  # type: ignore

    # Grid overlay settings
    show_grid: bpy.props.BoolProperty(
        name="Exibir Grid no Piso",
        description="Mostra grid pontilhado sobre o piso para guia de posicionamento",
        default=True
    )  # type: ignore
    grid_spacing_x: bpy.props.FloatProperty(
        name="Intervalo Horizontal",
        description="Espaçamento horizontal das linhas da grade",
        default=0.5,
        min=0.05,
        max=5.0,
        subtype='DISTANCE'
    )  # type: ignore
    grid_spacing_y: bpy.props.FloatProperty(
        name="Intervalo Vertical",
        description="Espaçamento vertical das linhas da grade",
        default=0.5,
        min=0.05,
        max=5.0,
        subtype='DISTANCE'
    )  # type: ignore
    grid_snap_enabled: bpy.props.BoolProperty(
        name="Atrair ao Grid",
        description="Módulos são atraídos para a grade mais próxima",
        default=True
    )  # type: ignore
    grid_snap_gap: bpy.props.FloatProperty(
        name="Gap de Atração",
        description="Distância máxima na qual a atração da grade passa a agir",
        default=0.05,
        min=0.005,
        max=0.5,
        subtype='DISTANCE'
    )  # type: ignore

    # Insertion plane overlay
    show_insertion_plane: bpy.props.BoolProperty(
        name="Mostrar Planos de Inserção",
        description="Exibe sombreamento amarelo no plano de inserção sob o cursor",
        default=True
    )  # type: ignore

    # Dimension labels
    show_dimensions: bpy.props.BoolProperty(
        name="Exibir Cotas",
        description="Mostra dimensões dinâmicas sobre os objetos",
        default=True
    )  # type: ignore

    # Plano de corte (T037): marcado como desatualizado quando o padrão ou um módulo muda depois do cálculo.
    cut_plan_stale: bpy.props.BoolProperty(
        name="Plano de Corte Desatualizado",
        description="O projeto mudou depois do último cálculo do plano de corte",
        default=False
    )  # type: ignore
    cut_include_client: bpy.props.BoolProperty(
        name="Incluir Dados do Cliente",
        description="Grava nome e contato do cliente no JSON exportado (RN-21)",
        default=True
    )  # type: ignore

    # OBSOLETOS desde o Padrão de Dimensões (Scene.btm_standards): `dimension_settings` e `config_*` são mantidos
    # somente para a migração M-01 de arquivos antigos; nada novo deve ler ou escrever estes grupos.
    dimension_settings: bpy.props.PointerProperty(type=BTM_PG_DimensionSettings)  # type: ignore
    mdf_config: bpy.props.PointerProperty(type=BTM_PG_MDFSheetConfig)  # type: ignore

    # Configurador de componentes individuais (OBSOLETO: ver Scene.btm_standards; lido só pela migração)
    config_active_component: bpy.props.EnumProperty(
        name="Componente",
        description="Escolha o componente a configurar",
        items=[
            ('LATERAL', "Lateral", "Lateral do móvel"),
            ('DIVISORIA', "Divisória", "Divisória interna"),
            ('BASE', "Base", "Base ou tampo estrutural"),
            ('FUNDO', "Fundo", "Fundo do armário"),
            ('PRATELEIRA', "Prateleira", "Prateleira interna"),
            ('PORTA', "Porta / Frente", "Portas e frentes de gaveta"),
        ],
        default='LATERAL'
    )  # type: ignore

    config_lateral: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore
    config_divisoria: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore
    config_base: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore
    config_fundo: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore
    config_prateleira: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore
    config_porta: bpy.props.PointerProperty(type=BTM_PG_ComponentConfig)  # type: ignore


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    BTM_PG_WallSegment,
    BTM_PG_InsertionPlane,
    BTM_PG_OpeningProperties,
    BTM_PG_CabinetProperties,
    BTM_PG_ComponentConfig,
    BTM_PG_MDFSheetConfig,
    BTM_PG_DimensionSettings,
    BTM_PG_SceneSettings,
)


def unregister_properties():
    """Safely remove property pointers from Blender data types before unregistering classes."""
    for attr in ("btm_wall", "btm_plane", "btm_opening", "btm_cabinet"):
        if hasattr(bpy.types.Object, attr):
            try:
                delattr(bpy.types.Object, attr)
            except Exception:
                pass
    if hasattr(bpy.types.Scene, "btm_settings"):
        try:
            delattr(bpy.types.Scene, "btm_settings")
        except Exception:
            pass


def register():
    unregister_properties()
    for cls in classes:
        reg_cls = (cls if cls.is_registered else getattr(bpy.types, cls.__name__, None))
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass

    # Register property pointers on Blender data types
    try:
        bpy.types.Object.btm_wall = bpy.props.PointerProperty(type=BTM_PG_WallSegment)
    except Exception:
        pass
    try:
        bpy.types.Object.btm_plane = bpy.props.PointerProperty(type=BTM_PG_InsertionPlane)
    except Exception:
        pass
    try:
        bpy.types.Object.btm_opening = bpy.props.PointerProperty(type=BTM_PG_OpeningProperties)
    except Exception:
        pass
    try:
        bpy.types.Object.btm_cabinet = bpy.props.PointerProperty(type=BTM_PG_CabinetProperties)
    except Exception:
        pass
    try:
        bpy.types.Scene.btm_settings = bpy.props.PointerProperty(type=BTM_PG_SceneSettings)
    except Exception:
        pass


def unregister():
    unregister_properties()
    for cls in reversed(classes):
        reg_cls = (cls if cls.is_registered else getattr(bpy.types, cls.__name__, None))
        if reg_cls:
            try:
                bpy.utils.unregister_class(reg_cls)
            except Exception:
                pass

