"""Esquema declarativo do Padrão de Dimensões (Configurador de Dimensões).

Define O QUE pode ser configurado — linhas de produto, dimensões externas, componentes de chapa, medidas máximas —
com rótulos, unidade, faixa, passo, precisão, padrões Brasil/EUA, imagem de referência, códigos do Promob e
propriedades legadas sincronizadas. Os VALORES ficam nas definições (`standards/model.py`).

Python puro (sem `bpy`): pode ser testado fora do Blender (`tests/test_dimension_schema.py`).

Unidades: comprimentos em **mm** neste esquema; a conversão para metros (unidade interna do Blender) acontece na
camada que escreve nas propriedades (`standards/`).

Convenção dos lados da fita (clarify C-1): lados 1 e 2 = bordas do COMPRIMENTO da peça; 3 e 4 = bordas da LARGURA.
O Promob numera 1 = topo, 2 = base, 3 = direita, 4 = esquerda numa lateral em pé (bordas da largura em 1/2);
`PROMOB_EDGE_TO_SIDE` converte entre as duas numerações.
"""

from dataclasses import dataclass

INCH_MM = 25.4

MARKETS = ('BR', 'US')

# (código, rótulo pt-BR, rótulo en)
LINES = (
    ('COZ', "Cozinhas", "Kitchens"),
    ('DOR', "Dormitórios", "Bedrooms"),
    ('BAN', "Banheiros", "Bathrooms"),
    ('SAL', "Salas", "Living rooms"),
    ('ESC', "Escritórios", "Offices"),
)
LINE_CODES = tuple(code for code, _pt, _en in LINES)

GROUP_MAX = 'MAX'
GROUP_EXTERNAL = 'EXTERNAL'
GROUP_SHEET = 'SHEET'

TREE_SHEETS = 'CHAPAS'
TREE_COMPONENTS = 'COMPONENTES'

# Classes de espessura padrão (mm): (Brasil, EUA)
_THICKNESS = {
    'CAIXA': (15.0, 0.75 * INCH_MM),
    'FRENTE': (18.0, 0.75 * INCH_MM),
    'FUNDO': (6.0, 0.25 * INCH_MM),
    'TAMPO': (15.0, 0.75 * INCH_MM),
}


@dataclass(frozen=True)
class Component:
    """Componente de chapa do Configurador (árvore "Chapas" ou "Componentes")."""
    code: str
    label_pt: str
    label_en: str
    tree: str
    thickness_class: str
    promob: tuple = ()        # códigos do Promob em C/L/ESP/MAT (ex.: PORTAS)
    promob_fit: tuple = ()    # códigos do Promob em FIT, quando diferentes (ex.: POR)
    visible_sides_br: tuple = (1,)  # lados com fita 0,4 mm no Padrão Brasil


# Ordem = ordem da árvore do Configurador (imagem da issue #20).
COMPONENTS = (
    Component('LAT', "Lateral", "Side", TREE_SHEETS, 'CAIXA', ('LAT',), ('LAT',)),
    Component('DIV', "Divisória", "Divider", TREE_SHEETS, 'CAIXA', ('DIV',), ('DIV',)),
    Component('BAS', "Base", "Bottom", TREE_SHEETS, 'CAIXA', ('BAS',), ('BAS',)),
    Component('FUN_INF', "Fundo - Inferiores", "Back - Base cabinets", TREE_SHEETS, 'FUNDO', ('FUN',), ('FUN',), ()),
    Component('FUN_SUP', "Fundo - Superiores", "Back - Upper cabinets", TREE_SHEETS, 'FUNDO', ('FUN_SUP',),
              ('FUN_SUP',), ()),
    Component('FUN_ALT', "Fundo - Altos", "Back - Tall cabinets", TREE_SHEETS, 'FUNDO', ('FUN_ALT',), ('FUN_ALT',), ()),
    Component('TRAS', "Traseira", "Rear panel", TREE_SHEETS, 'CAIXA', ('TRAS',), ('TRAS',)),
    Component('TRA', "Travessas Traseiras", "Rear stretchers", TREE_SHEETS, 'CAIXA', ('TRA',), ('TRA',)),
    Component('PRAT', "Prateleira", "Shelf", TREE_SHEETS, 'CAIXA', ('PRAT',), ('PRA', 'PRAT')),
    Component('POR', "Portas | Frentes", "Doors | Fronts", TREE_SHEETS, 'FRENTE', ('PORTAS',), ('POR',),
              (1, 2, 3, 4)),
    Component('PAI_POR', "Painel p/ Portas", "Door panel", TREE_SHEETS, 'FRENTE',
              ('PAI_PRO_MDF', 'PAI_POR_VID', 'PAI_PRO_PALHA', 'PAI_PRO_VID', 'PAI_PRO_MAD'), (), ()),
    Component('FRE_GAV_INT', "Frente Gav Int", "Inner drawer front", TREE_SHEETS, 'FRENTE', ('FRE_GAV_INT',),
              ('FRE_GAV_INT',), (1, 2, 3, 4)),
    Component('FRE_FORNO', "Frente Forno/Micro de Embutir", "Oven/microwave front", TREE_SHEETS, 'FRENTE',
              ('FRE_ELE_EMB',), ('FRE_ELE_EMB',), (1, 2, 3, 4)),
    Component('TAMP', "Tampo", "Top", TREE_SHEETS, 'TAMPO', ('TAMP',), ('TAMP',)),
    Component('TAMPON', "Tamponamento", "Cladding", TREE_SHEETS, 'CAIXA', ('TAMPON',), ('TAN', 'TAMPON')),
    Component('PAI', "Painel", "Panel", TREE_SHEETS, 'CAIXA', ('PAI',), ('PAI', 'PAINEL'), (1, 2, 3, 4)),
    Component('ESP', "Especial", "Special", TREE_SHEETS, 'CAIXA', ('ESP',), ('ESP',)),
    Component('SAR', "Sarrafo", "Batten", TREE_COMPONENTS, 'CAIXA', ('SAR',), ('SAR',)),
    Component('ROD', "Rodapé", "Toe kick", TREE_COMPONENTS, 'CAIXA', ('ROD',), ('ROD',)),
    Component('MOL', "Moldura", "Molding", TREE_COMPONENTS, 'CAIXA', ('MOL', 'MOL_ENG'), ('MOL',)),
)
COMPONENTS_BY_CODE = {c.code: c for c in COMPONENTS}

# Numeração do Promob (1 topo, 2 base, 3 direita, 4 esquerda) → numeração do BlenderToMob (C-1).
PROMOB_EDGE_TO_SIDE = {4: 1, 3: 2, 1: 3, 2: 4}
SIDE_TO_PROMOB_EDGE = {v: k for k, v in PROMOB_EDGE_TO_SIDE.items()}

MATERIALS = ('MDF', 'MDP', 'COMPENSADO', 'OSB', 'VIDRO', 'OUTRO')


@dataclass(frozen=True)
class Param:
    """Metadados de um parâmetro configurável (RN-05)."""
    key: str
    line: str
    group: str
    label_pt: str
    label_en: str
    unit: str
    type: str                     # 'FLOAT' | 'ENUM'
    default_br: object
    default_us: object
    min: float = 0.0
    max: float = 0.0
    step: float = 1.0
    precision: int = 1
    enum_items: tuple = ()
    zero_meaning: str = ""
    negative_allowed: bool = False
    image_key: str = ""
    promob_codes: tuple = ()
    legacy_targets: tuple = ()
    component: str = ""
    field: str = ""
    description_pt: str = ""

    def default(self, market='BR'):
        return self.default_br if market == 'BR' else self.default_us


# --------------------------------------------------------------------------------------------------------------
# Medidas Máximas (globais)
# --------------------------------------------------------------------------------------------------------------
_MAX_FIELDS = (
    # campo, rótulo pt, rótulo en, BR, EUA, mín., máx.
    ('module_width_max', "Largura máxima do módulo", "Max module width", 1200.0, 48 * INCH_MM, 100.0, 6000.0),
    ('module_height_max', "Altura máxima do módulo", "Max module height", 2700.0, 96 * INCH_MM, 100.0, 4000.0),
    ('module_depth_max', "Profundidade máxima do módulo", "Max module depth", 900.0, 30 * INCH_MM, 100.0, 2000.0),
    ('sheet_width_max', "Largura máxima da chapa", "Max sheet width", 2730.0, 2420.0, 300.0, 6000.0),
    ('sheet_length_max', "Comprimento máximo da chapa", "Max sheet length", 1810.0, 1200.0, 300.0, 6000.0),
)

# --------------------------------------------------------------------------------------------------------------
# Dimensões Externas (por linha) — itens A–L do Configurador (manual Promob §6.1.2)
# --------------------------------------------------------------------------------------------------------------
_EXTERNAL_FIELDS = (
    # campo, rótulo pt, rótulo en, BR, EUA, mín., máx.
    ('base_height', "Inferiores - Altura (sem tampo)", "Base - Height (no top)", 720.0, 34.5 * INCH_MM, 300.0, 1200.0),
    ('base_depth', "Inferiores - Profundidade", "Base - Depth", 550.0, 23.125 * INCH_MM, 200.0, 1000.0),
    ('upper_low_height', "Superiores baixos - Altura", "Upper short - Height", 350.0, 15 * INCH_MM, 100.0, 1500.0),
    ('upper_mid_height', "Superiores médios - Altura", "Upper medium - Height", 700.0, 30 * INCH_MM, 100.0, 1500.0),
    ('upper_high_height', "Superiores altos - Altura", "Upper tall - Height", 900.0, 42 * INCH_MM, 100.0, 1500.0),
    ('upper_depth', "Superiores - Profundidade", "Upper - Depth", 350.0, 13 * INCH_MM, 150.0, 800.0),
    ('install_height_upper', "Superiores - Altura de instalação (piso → base)", "Upper - Install height",
     1500.0, 54 * INCH_MM, 0.0, 2600.0),
    ('tall_height', "Altos/Despenseiros - Altura", "Tall - Height", 2200.0, 84 * INCH_MM, 1000.0, 3000.0),
    ('tall_depth', "Altos/Despenseiros - Profundidade", "Tall - Depth", 550.0, 25.5 * INCH_MM, 200.0, 1000.0),
    ('island_depth', "Ilhas - Profundidade", "Island - Depth", 900.0, 24 * INCH_MM, 300.0, 2000.0),
    ('top_overhang', "Tampo - Avanço", "Top - Overhang", 20.0, 1 * INCH_MM, 0.0, 200.0),
    ('toe_kick_height', "Rodapé - Altura", "Toe kick - Height", 100.0, 4 * INCH_MM, 0.0, 300.0),
    ('toe_kick_setback', "Rodapé - Recuo", "Toe kick - Setback", 50.0, 2.5 * INCH_MM, 0.0, 200.0),
)

# Exceções por linha: Dormitórios usam altura/profundidade de roupeiro (Promob ALT_ARM/PROF_ARM; closets HB5).
_EXTERNAL_OVERRIDES = {
    ('DOR', 'tall_height'): (2400.0, 2131.0),
    ('DOR', 'tall_depth'): (550.0, 14 * INCH_MM),
    ('DOR', 'base_height'): (720.0, 819.0),
    ('DOR', 'toe_kick_height'): (100.0, 96.0),
    ('DOR', 'toe_kick_setback'): (50.0, 1.625 * INCH_MM),
}

# Propriedades legadas sincronizadas (data-delta §6). Caminho "<Scene.attr>.<prop>", valores em metros.
_LEGACY_TARGETS = {
    'COZ.sheets.LAT.thickness': ('hb_frameless.default_carcass_part_thickness',),
    'COZ.external.base_height': ('hb_frameless.base_cabinet_height',),
    'COZ.external.base_depth': ('hb_frameless.base_cabinet_depth',),
    'COZ.external.upper_mid_height': ('hb_frameless.upper_cabinet_height',),
    'COZ.external.upper_depth': ('hb_frameless.upper_cabinet_depth',),
    'COZ.external.tall_height': ('hb_frameless.tall_cabinet_height',),
    'COZ.external.tall_depth': ('hb_frameless.tall_cabinet_depth',),
    'COZ.external.install_height_upper': ('hb_frameless.default_wall_cabinet_location',),
    'COZ.external.toe_kick_height': ('hb_frameless.default_toe_kick_height',),
    'COZ.external.toe_kick_setback': ('hb_frameless.default_toe_kick_setback',),
    'DOR.sheets.LAT.thickness': ('hb_closets.panel_thickness',),
    'DOR.sheets.PRAT.thickness': ('hb_closets.shelf_thickness',),
    'DOR.external.base_height': ('hb_closets.base_panel_height',),
    'DOR.external.tall_height': ('hb_closets.tall_panel_height',),
    'DOR.external.tall_depth': ('hb_closets.default_panel_depth',),
    'DOR.external.toe_kick_height': ('hb_closets.toe_kick_height',),
    'DOR.external.toe_kick_setback': ('hb_closets.toe_kick_setback',),
}

# Códigos globais do Promob mapeados para dimensões externas (🟡: semântica inferida por ARM = armário).
_PROMOB_EXTERNAL = {
    'ALT_ARM': 'DOR.external.tall_height',
    'PROF_ARM': 'DOR.external.tall_depth',
}

SHEET_FIELDS = ('material', 'max_width', 'max_length', 'thickness', 'edge_1', 'edge_2', 'edge_3', 'edge_4')
EDGE_FIELDS = ('edge_1', 'edge_2', 'edge_3', 'edge_4')

_SHEET_FIELD_LABELS = {
    'material': ("Material", "Material"),
    'max_width': ("Largura Máxima da Chapa", "Max sheet width"),
    'max_length': ("Comprimento Máximo da Chapa", "Max sheet length"),
    'thickness': ("Espessura da Chapa", "Sheet thickness"),
    'edge_1': ("Fita Borda 1 (comprimento)", "Edge band 1 (length)"),
    'edge_2': ("Fita Borda 2 (comprimento)", "Edge band 2 (length)"),
    'edge_3': ("Fita Borda 3 (largura)", "Edge band 3 (width)"),
    'edge_4': ("Fita Borda 4 (largura)", "Edge band 4 (width)"),
}

_PROMOB_SHEET_FAMILY = {'material': 'MAT', 'max_width': 'L', 'max_length': 'C', 'thickness': 'ESP'}


def sheet_key(line, component, field_name):
    return f"{line}.sheets.{component}.{field_name}"


def external_key(line, field_name):
    return f"{line}.external.{field_name}"


def max_key(field_name):
    return f"GLOBAL.max.{field_name}"


def _build():
    params = {}
    for name, pt, en, br, us, lo, hi in _MAX_FIELDS:
        key = max_key(name)
        params[key] = Param(key, 'GLOBAL', GROUP_MAX, pt, en, 'mm', 'FLOAT', br, round(us, 4), lo, hi, 1.0, 1,
                            image_key='max_measures', field=name)
    for line in LINE_CODES:
        for name, pt, en, br, us, lo, hi in _EXTERNAL_FIELDS:
            br, us = _EXTERNAL_OVERRIDES.get((line, name), (br, us))
            key = external_key(line, name)
            promob = tuple(code for code, target in _PROMOB_EXTERNAL.items() if target == key)
            params[key] = Param(key, line, GROUP_EXTERNAL, pt, en, 'mm', 'FLOAT', br, round(us, 4), lo, hi, 1.0, 1,
                                zero_meaning="sem rodapé" if name.startswith('toe_kick') else "",
                                image_key=f"ext_{name}", promob_codes=promob,
                                legacy_targets=_LEGACY_TARGETS.get(key, ()), field=name)
        for comp in COMPONENTS:
            br_th, us_th = _THICKNESS[comp.thickness_class]
            for fname in SHEET_FIELDS:
                key = sheet_key(line, comp.code, fname)
                pt, en = _SHEET_FIELD_LABELS[fname]
                if fname in _PROMOB_SHEET_FAMILY:
                    fam = _PROMOB_SHEET_FAMILY[fname]
                    promob = tuple(f"{line}_{fam}_{c}" for c in comp.promob)
                else:
                    side = int(fname[-1])
                    pedge = SIDE_TO_PROMOB_EDGE[side]
                    promob = tuple(f"{line}_FIT_{c}_{pedge}A" for c in (comp.promob_fit or comp.promob))
                common = dict(image_key=f"sheet_{comp.code.lower()}", promob_codes=promob,
                              legacy_targets=_LEGACY_TARGETS.get(key, ()), component=comp.code, field=fname)
                if fname == 'material':
                    params[key] = Param(key, line, GROUP_SHEET, pt, en, '', 'ENUM', 'MDF', 'MDF',
                                        enum_items=MATERIALS, **common)
                elif fname == 'thickness':
                    params[key] = Param(key, line, GROUP_SHEET, pt, en, 'mm', 'FLOAT', br_th, round(us_th, 4),
                                        3.0, 60.0, 0.5, 1, **common)
                elif fname == 'max_width':
                    params[key] = Param(key, line, GROUP_SHEET, pt, en, 'mm', 'FLOAT', 2730.0, 2420.0,
                                        100.0, 6000.0, 1.0, 1, **common)
                elif fname == 'max_length':
                    params[key] = Param(key, line, GROUP_SHEET, pt, en, 'mm', 'FLOAT', 1810.0, 1200.0,
                                        100.0, 6000.0, 1.0, 1, **common)
                else:
                    side = int(fname[-1])
                    br_edge = 0.4 if side in comp.visible_sides_br else 0.0
                    params[key] = Param(key, line, GROUP_SHEET, pt, en, 'mm', 'FLOAT', br_edge, 0.0,
                                        0.0, 5.0, 0.1, 1, zero_meaning="sem fita", **common)
    return params


PARAMS = _build()


def get_param(key):
    """Metadados do parâmetro `key`, ou None."""
    return PARAMS.get(key)


def params_for(line=None, group=None, component=None):
    """Parâmetros filtrados por linha, grupo e/ou componente, na ordem de declaração."""
    return [p for p in PARAMS.values()
            if (line is None or p.line == line)
            and (group is None or p.group == group)
            and (component is None or p.component == component)]


def label(param_or_key, lang='pt'):
    p = PARAMS[param_or_key] if isinstance(param_or_key, str) else param_or_key
    return p.label_pt if lang == 'pt' else p.label_en


def line_label(code, lang='pt'):
    for c, pt, en in LINES:
        if c == code:
            return pt if lang == 'pt' else en
    return code


def validate(param, value):
    """Valida `value` contra o domínio do parâmetro.

    Retorna (True, "") ou (False, mensagem "Valor Inválido" com campo, valor, unidade e faixa — RN-06).
    """
    if param.type == 'ENUM':
        if value in param.enum_items:
            return True, ""
        return False, (f"Valor Inválido: {param.label_pt} deve ser um de "
                       f"{', '.join(param.enum_items)} (recebido: {value}).")
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False, f"Valor Inválido: {param.label_pt} precisa ser numérico (recebido: {value})."
    if number < 0 and not param.negative_allowed:
        return False, f"Valor Inválido: {param.label_pt} não aceita valor negativo."
    if number < param.min or number > param.max:
        return False, (f"Valor Inválido: {param.label_pt} deve estar entre {_fmt(param.min)} e "
                       f"{_fmt(param.max)} {param.unit} (recebido: {_fmt(number)} {param.unit}).")
    return True, ""


def _fmt(number):
    text = f"{number:.1f}".rstrip('0').rstrip('.')
    return text.replace('.', ',')


# --------------------------------------------------------------------------------------------------------------
# Promob DIMENSIONEXPORT
# --------------------------------------------------------------------------------------------------------------

def _promob_index():
    index = {}
    for key, p in PARAMS.items():
        for code in p.promob_codes:
            index.setdefault(code, key)
    return index


PROMOB_INDEX = _promob_index()

_PROMOB_COMPONENT_ALIASES = {}
for _c in COMPONENTS:
    for _code in _c.promob + _c.promob_fit:
        _PROMOB_COMPONENT_ALIASES.setdefault(_code, _c.code)


def parse_promob_id(attr_id):
    """Interpreta um ID do DIMENSIONEXPORT pela estrutura `<LINHA>_<FAMÍLIA>_<COMPONENTE>[_<n>A]`.

    Retorna dict com `line`, `family`, `component` (código do Promob), `field` e `side` (já na numeração C-1),
    ou None quando não é uma família de chapa confirmada (C, L, ESP, MAT, FIT).
    """
    parts = attr_id.split('_')
    if len(parts) < 3 or parts[0] not in LINE_CODES:
        return None
    line, family = parts[0], parts[1]
    rest = parts[2:]
    if family in ('C', 'L', 'ESP', 'MAT'):
        fname = {'C': 'max_length', 'L': 'max_width', 'ESP': 'thickness', 'MAT': 'material'}[family]
        return {'line': line, 'family': family, 'component': '_'.join(rest), 'field': fname, 'side': None}
    if family == 'FIT' and len(rest) >= 2 and len(rest[-1]) == 2 and rest[-1][1] == 'A' and rest[-1][0].isdigit():
        pedge = int(rest[-1][0])
        if pedge not in PROMOB_EDGE_TO_SIDE:
            return None
        side = PROMOB_EDGE_TO_SIDE[pedge]
        return {'line': line, 'family': family, 'component': '_'.join(rest[:-1]), 'field': f"edge_{side}",
                'side': side}
    return None


def canonical_component(promob_component):
    """Código canônico do componente para um código do Promob (ou None se não houver equivalente)."""
    return _PROMOB_COMPONENT_ALIASES.get(promob_component)
