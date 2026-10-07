"""
BlenderToMob Units System — Conversão e Formatação de Medidas Métricas e Imperiais
Suporta Milímetros (mm), Centímetros (cm), Metros (m), Polegadas (in) e Pés (ft).

Ponto único de parsing e formatação de medidas (RN-01, decisão D-07): a unidade interna é o metro do Blender;
a interface exibe e aceita mm, cm ou m com vírgula decimal. Sem `import bpy` no carregamento do módulo, para
que as funções puras possam ser testadas fora do Blender (`tests/test_units.py`).
"""

import re

# Fatores de conversão para metros (unidade base do Blender)
UNIT_CONVERSION_TO_METERS = {
    'MM': 0.001,
    'MILLIMETERS': 0.001,
    'CM': 0.01,
    'CENTIMETERS': 0.01,
    'M': 1.0,
    'METERS': 1.0,
    'IN': 0.0254,
    'INCHES': 0.0254,
    'FT': 0.3048,
    'FEET': 0.3048,
}

UNIT_LABELS = {
    'MM': 'mm',
    'MILLIMETERS': 'mm',
    'CM': 'cm',
    'CENTIMETERS': 'cm',
    'M': 'm',
    'METERS': 'm',
    'IN': 'in',
    'INCHES': '"',
    'FT': 'ft',
    'FEET': "'",
}


def to_meters(value, unit='MM'):
    """Converte um valor da unidade fornecida para metros (unidade interna do Blender)."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit.upper(), 0.001)
    return value * scale


def from_meters(value_in_meters, unit='MM'):
    """Converte um valor em metros (unidade interna do Blender) para a unidade fornecida."""
    scale = UNIT_CONVERSION_TO_METERS.get(unit.upper(), 0.001)
    if scale == 0:
        return value_in_meters
    return value_in_meters / scale


def get_scene_length_unit(scene=None):
    """Detecta a unidade de comprimento ativa nas configurações de cena do Blender."""
    if scene is None:
        try:
            import bpy  # type: ignore
            scene = getattr(bpy.context, 'scene', None)
        except ImportError:
            scene = None
    if not scene:
        return 'MM'

    if hasattr(scene, 'btm_settings') and hasattr(scene.btm_settings, 'btm_unit'):
        u = scene.btm_settings.btm_unit
        if u == 'MILLIMETERS':
            return 'MM'
        elif u == 'CENTIMETERS':
            return 'CM'
        elif u == 'METERS':
            return 'M'

    unit_settings = scene.unit_settings
    if unit_settings.system == 'METRIC':
        length_unit = unit_settings.length_unit
        if length_unit == 'MILLIMETERS':
            return 'MM'
        elif length_unit == 'CENTIMETERS':
            return 'CM'
        elif length_unit == 'METERS':
            return 'M'
    return 'MM'


def format_number(value):
    """Formata um número removendo zeros redundantes."""
    rounded = round(value, 3)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip('0').rstrip('.')


def format_value(value_in_meters, scene=None, unit=None):
    """Formata um valor em metros para exibição na UI com o sufixo correto (vírgula decimal)."""
    if unit is None:
        unit = get_scene_length_unit(scene)
    return format_length(value_in_meters, unit=unit)


# Casas decimais padrão por unidade: precisão de 0,1 mm (RNF de precisão).
DEFAULT_PRECISION = {'MM': 1, 'CM': 2, 'M': 4, 'IN': 3, 'FT': 4}

_CANONICAL_UNIT = {
    'MILLIMETERS': 'MM', 'CENTIMETERS': 'CM', 'METERS': 'M', 'INCHES': 'IN', 'FEET': 'FT',
    'MM': 'MM', 'CM': 'CM', 'M': 'M', 'IN': 'IN', 'FT': 'FT',
}

_SUFFIX_TO_UNIT = {'mm': 'MM', 'cm': 'CM', 'm': 'M'}

_NUMBER_RE = re.compile(r"^\s*([+-]?)\s*([0-9][0-9.,]*|[.,][0-9]+)\s*(mm|cm|m)?\s*$", re.IGNORECASE)


def canonical_unit(unit):
    """Normaliza o código de unidade ('MILLIMETERS' → 'MM'); desconhecido vira 'MM'."""
    return _CANONICAL_UNIT.get((unit or 'MM').upper(), 'MM')


def format_length(value_in_meters, unit='MM', precision=None, with_suffix=True, decimal_comma=True):
    """Formata metros na unidade pedida, sem zeros redundantes e com vírgula decimal.

    Ex.: format_length(0.7555, 'CM') → "75,55 cm"; format_length(0.0004, 'MM') → "0,4 mm".
    """
    unit = canonical_unit(unit)
    if precision is None:
        precision = DEFAULT_PRECISION.get(unit, 1)
    value = from_meters(value_in_meters, unit)
    text = f"{round(value, precision):.{precision}f}"
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    if text in ('-0', ''):
        text = '0'
    if decimal_comma:
        text = text.replace('.', ',')
    if with_suffix:
        return f"{text} {UNIT_LABELS.get(unit, 'mm')}"
    return text


def _to_float(number_text):
    """Converte texto numérico aceitando vírgula ou ponto como separador decimal.

    Com os dois presentes, o último é o decimal e o outro é separador de milhar ("1.234,5" → 1234.5).
    """
    if ',' in number_text and '.' in number_text:
        if number_text.rfind(',') > number_text.rfind('.'):
            number_text = number_text.replace('.', '').replace(',', '.')
        else:
            number_text = number_text.replace(',', '')
    else:
        number_text = number_text.replace(',', '.')
    if number_text.count('.') > 1:
        raise ValueError(number_text)
    return float(number_text)


def parse_length(text, default_unit='MM', allow_negative=False, allow_zero=True):
    """Interpreta uma medida digitada e devolve o valor em METROS.

    Aceita vírgula ou ponto decimal e sufixos `mm`, `cm` ou `m` (sem sufixo vale `default_unit`).
    Não aceita frações nem pés/polegadas (decisão PL-03). Levanta `ValueError` com mensagem em português.
    """
    if text is None:
        raise ValueError("Valor Inválido: medida vazia.")
    match = _NUMBER_RE.match(str(text))
    if not match:
        raise ValueError(f"Valor Inválido: \"{text}\" não é uma medida (use números com mm, cm ou m).")
    sign, number_text, suffix = match.groups()
    try:
        number = _to_float(number_text)
    except ValueError:
        raise ValueError(f"Valor Inválido: \"{text}\" não é um número válido.") from None
    if sign == '-':
        number = -number
    if number < 0 and not allow_negative:
        raise ValueError("Valor Inválido: a medida não pode ser negativa.")
    if number == 0 and not allow_zero:
        raise ValueError("Valor Inválido: a medida não pode ser zero.")
    unit = _SUFFIX_TO_UNIT[suffix.lower()] if suffix else canonical_unit(default_unit)
    return to_meters(number, unit)


def unit_to_string(unit_settings, value):
    """Texto de uma medida (metros) para rótulos legados (T041/T042).

    Em sistema métrico usa a unidade escolhida no BlenderToMob (`btm_settings.btm_unit`, vírgula decimal);
    em imperial mantém pés ou polegadas arredondadas a 1/16".
    """
    system = getattr(unit_settings, 'system', 'METRIC')
    if system == 'IMPERIAL':
        if getattr(unit_settings, 'length_unit', '') == 'FEET':
            return f"{round(value / 0.3048, 2):g}'"
        inches = round(value / 0.0254 * 16.0) / 16.0
        return f"{inches:g}\""
    return format_value(value)


# Aliases legados
def inch(value):
    return value * 0.0254

def feet(value):
    return value * 0.3048

def millimeter(value):
    return value * 0.001

def centimeter(value):
    return value * 0.01

def meter_to_inch(value):
    return round(value * 39.3701, 6)

def meter_to_millimeter(meter):
    return meter * 1000.0

def meter_to_feet(meter):
    return round(meter * 3.28084, 6)

def convert_to_meters(value, unit_code='MM'):
    return to_meters(value, unit_code)

def convert_from_meters(meters_val, unit_code='MM'):
    return from_meters(meters_val, unit_code)

def format_length_unit(meters_val, unit_code='MM'):
    return format_value(meters_val, unit=unit_code)
