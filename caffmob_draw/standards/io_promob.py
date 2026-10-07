"""Importação e exportação do `DIMENSIONEXPORT` do Promob (T017; RF-058).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/promob-dimensionexport.md`.

Python puro (sem `bpy`): lê/escreve o XML e converte para um dicionário de definição
(`values` por chave do esquema + `raw_attributes` na ordem original). A gravação nas PropertyGroups fica em
`operators/ops_standards.py`, via `standards/api.py`.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from ..data import dimension_schema as schema


class PromobFormatError(Exception):
    """Arquivo que não é um DIMENSIONEXPORT válido (mensagem pronta para o usuário)."""


@dataclass
class PromobDocument:
    name: str
    version: str = "-1"
    is_system: str = "False"
    changed: str = "True"
    attributes: list = field(default_factory=list)   # [(id, valor original)], na ordem do arquivo


def read_dimensionexport(path):
    """Lê um arquivo `.xml`/`.dimensionExport` do Promob."""
    try:
        tree = ET.parse(str(path))
    except ET.ParseError as exc:
        line, column = getattr(exc, 'position', (0, 0))
        raise PromobFormatError(f"Arquivo XML inválido (linha {line}, coluna {column}).") from None
    except OSError as exc:
        raise PromobFormatError(f"Não foi possível ler o arquivo: {exc}") from None
    root = tree.getroot()
    if root.tag != 'DIMENSIONEXPORT':
        raise PromobFormatError(f"Não é uma configuração de dimensões do Promob (raiz <{root.tag}>).")
    definition = root.find('DEFINITION')
    name = " ".join((definition.get('DESCRIPTION', '') if definition is not None else '').split())
    doc = PromobDocument(
        name=name or "Configuração importada do Promob",
        version=root.get('VERSION', '-1'),
        is_system=definition.get('ISSYSTEM', 'False') if definition is not None else 'False',
        changed=definition.get('CHANGED', 'True') if definition is not None else 'True',
    )
    for attr in root.iter('ATTRIBUTE'):
        attr_id = attr.get('ID')
        if attr_id:
            doc.attributes.append((attr_id, attr.get('VALUE', '')))
    if not doc.attributes:
        raise PromobFormatError("O arquivo não contém atributos de dimensão.")
    return doc


def _parse_number(text):
    return float(text.strip().replace(',', '.'))


def to_definition_data(doc):
    """Converte o documento em dados de definição.

    Retorna dict com `name`, `values` (chave → valor em mm ou texto), `raw_attributes`
    (lista de {id, value, key} na ordem original; `key` vazio = não reconhecido) e `report`
    (`total`, `mapped`, `unrecognized`, `invalid`, `duplicates`, `confirmed_without_equivalent`).
    """
    values = {}
    raw = []
    report = {'total': len(doc.attributes), 'mapped': 0, 'unrecognized': [], 'invalid': [], 'duplicates': [],
              'confirmed_without_equivalent': []}
    seen = {}
    for attr_id, text in doc.attributes:
        if attr_id in seen:
            report['duplicates'].append(attr_id)
        seen[attr_id] = text

    for attr_id, text in doc.attributes:
        key = schema.PROMOB_INDEX.get(attr_id, "")
        if key:
            param = schema.PARAMS[key]
            current = seen[attr_id]   # ID duplicado: vale o último
            try:
                value = current.strip() if param.type == 'ENUM' else _parse_number(current)
            except ValueError:
                value = None
            ok = value is not None and schema.validate(param, value)[0]
            if ok:
                values[key] = value
                report['mapped'] += 1
            else:
                report['invalid'].append(attr_id)
                report['unrecognized'].append(attr_id)
                key = ""
        else:
            report['unrecognized'].append(attr_id)
            if schema.parse_promob_id(attr_id):
                report['confirmed_without_equivalent'].append(attr_id)
        raw.append({'id': attr_id, 'value': text, 'key': key})
    return {'name': doc.name, 'values': values, 'raw_attributes': raw, 'report': report}


def _format_number(value):
    text = f"{float(value):.4f}".rstrip('0').rstrip('.')
    return (text or '0').replace('.', ',')


def build_attributes(values, raw_attributes):
    """Lista (id, valor) para exportação: atributos mapeados recebem o valor atual; os demais, o original."""
    pairs = []
    for raw in raw_attributes:
        key = raw.get('key') or ""
        original = raw.get('value', '')
        if key and key in values:
            param = schema.PARAMS[key]
            current = values[key]
            if param.type == 'ENUM':
                text = str(current)
            else:
                try:
                    same = abs(_parse_number(original) - float(current)) < 1e-6
                except ValueError:
                    same = False
                text = original if same else _format_number(current)
            pairs.append((raw['id'], text))
        else:
            pairs.append((raw['id'], original))
    return pairs


def write_dimensionexport(path, name, values, raw_attributes):
    """Grava o DIMENSIONEXPORT (escrita atômica). `raw_attributes` define a ordem e os IDs exportados.

    Para uma definição criada no BlenderToMob (sem arquivo de origem), use `attributes_from_values`.
    """
    root = ET.Element('DIMENSIONEXPORT', VERSION="-1")
    definition = ET.SubElement(root, 'DEFINITION', DESCRIPTION=name, ISSYSTEM="False", CHANGED="True")
    attributes = ET.SubElement(definition, 'ATTRIBUTES')
    for attr_id, text in build_attributes(values, raw_attributes):
        ET.SubElement(attributes, 'ATTRIBUTE', ID=attr_id, VALUE=text)
    ET.indent(root, space="  ")
    data = ET.tostring(root, encoding='unicode')
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write('<?xml version="1.0" encoding="utf-8"?>\n')
            handle.write(data)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def attributes_from_values(values):
    """`raw_attributes` sintéticos (um por código Promob conhecido) para exportar uma definição sem origem Promob."""
    raw = []
    for key, param in schema.PARAMS.items():
        if key not in values:
            continue
        for code in param.promob_codes:
            raw.append({'id': code, 'value': '', 'key': key})
    return raw
