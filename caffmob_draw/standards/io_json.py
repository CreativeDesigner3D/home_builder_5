"""Exportação e importação de definições `.btmdim.json` (T016; RF-057).

Contrato: `_reversa_forward/001-addon-moveis-planejados/interfaces/dimension-definition.md`.
Python puro na leitura/escrita do arquivo; a criação da definição na cena usa `standards/api.py`.
"""

import json
import os
import tempfile

from ..data import dimension_schema as schema

FORMAT = "caffmob_draw.dimension-standard"
# Arquivos exportados antes da identidade CAFFMob Draw continuam válidos na leitura (BUG-20261006-QAVK).
ACCEPTED_FORMATS = (FORMAT, "blendertomob.dimension-standard")
SCHEMA_VERSION = 1


class StandardFileError(Exception):
    """Arquivo de definição inválido (mensagem pronta para o usuário)."""


def user_folder():
    """Pasta das definições do usuário: extension_path_user(…/standards)."""
    import bpy
    package = __package__.rsplit('.', 1)[0]
    return bpy.utils.extension_path_user(package, path="standards", create=True)


# ----------------------------------------------------------------------------------------------------------------
# Conversão valores ↔ estrutura do arquivo
# ----------------------------------------------------------------------------------------------------------------

def values_to_document(name, uid, market, source, version, updated_at, values, raw_attributes=()):
    """Monta o dicionário do arquivo a partir de valores planos (chave → valor em mm ou texto)."""
    lines = {}
    max_measures = {}
    for key, value in values.items():
        param = schema.get_param(key)
        if param is None:
            continue
        if param.group == schema.GROUP_MAX:
            max_measures[param.field] = value
            continue
        line = lines.setdefault(param.line, {'external': {}, 'sheets': {}, 'components': {}})
        if param.group == schema.GROUP_EXTERNAL:
            line['external'][param.field] = value
        else:
            comp = schema.COMPONENTS_BY_CODE[param.component]
            bucket = line['sheets'] if comp.tree == schema.TREE_SHEETS else line['components']
            entry = bucket.setdefault(param.component, {'edges': [0.0, 0.0, 0.0, 0.0]})
            if param.field in schema.EDGE_FIELDS:
                entry['edges'][int(param.field[-1]) - 1] = value
            else:
                entry[param.field] = value
    return {
        "schema": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "uid": uid,
        "name": name,
        "market": market,
        "source": 'USER' if source == 'BUILTIN' else source,
        "version": version,
        "updated_at": updated_at,
        "unit": "mm",
        "max_measures": max_measures,
        "lines": lines,
        "raw_attributes": [{"id": r['id'], "value": r['value'], "key": r.get('key', '')} for r in raw_attributes],
    }


def document_to_values(document):
    """Valida o documento e devolve (valores planos, avisos). Levanta StandardFileError se algo for inválido."""
    if not isinstance(document, dict) or document.get("schema") not in ACCEPTED_FORMATS:
        raise StandardFileError("O arquivo não é uma definição de dimensões do CAFFMob Draw.")
    version = document.get("schema_version")
    if not isinstance(version, int):
        raise StandardFileError("Versão do formato ausente.")
    if version > SCHEMA_VERSION:
        raise StandardFileError("Arquivo criado por uma versão mais nova da extensão: atualize o CAFFMob Draw.")
    if document.get("unit", "mm") != "mm":
        raise StandardFileError("Unidade do arquivo deve ser mm.")
    values, warnings, errors = {}, [], []

    def put(key, value):
        param = schema.get_param(key)
        if param is None:
            warnings.append(f"Parâmetro desconhecido ignorado: {key}")
            return
        ok, message = schema.validate(param, value)
        if ok:
            values[key] = value if param.type == 'ENUM' else float(value)
        else:
            errors.append(message)

    for fname, value in (document.get("max_measures") or {}).items():
        put(schema.max_key(fname), value)
    for line, data in (document.get("lines") or {}).items():
        if line not in schema.LINE_CODES:
            warnings.append(f"Linha desconhecida ignorada: {line}")
            continue
        for fname, value in (data.get("external") or {}).items():
            put(schema.external_key(line, fname), value)
        for bucket in ("sheets", "components"):
            for comp, entry in (data.get(bucket) or {}).items():
                for fname, value in entry.items():
                    if fname == 'edges':
                        for side, edge in enumerate(value or [], start=1):
                            put(schema.sheet_key(line, comp, f"edge_{side}"), edge)
                    else:
                        put(schema.sheet_key(line, comp, fname), value)
    if errors:
        raise StandardFileError("Valores fora do domínio:\n" + "\n".join(errors))
    return values, warnings


# ----------------------------------------------------------------------------------------------------------------
# Arquivo
# ----------------------------------------------------------------------------------------------------------------

def write_document(path, document):
    """Escrita atômica, UTF-8 sem BOM."""
    directory = os.path.dirname(os.path.abspath(str(path))) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2, sort_keys=False)
            handle.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_document(path):
    try:
        with open(str(path), encoding='utf-8') as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise StandardFileError(f"JSON inválido (linha {exc.lineno}, coluna {exc.colno}).") from None
    except OSError as exc:
        raise StandardFileError(f"Não foi possível ler o arquivo: {exc}") from None


# ----------------------------------------------------------------------------------------------------------------
# Integração com as definições da cena (usa bpy por meio de standards/api.py)
# ----------------------------------------------------------------------------------------------------------------

def export_definition(path, definition):
    from . import api
    values = api.definition_values(definition)
    raw = [{"id": r.attr_id, "value": r.value, "key": r.key} for r in definition.raw_attributes]
    document = values_to_document(definition.name, definition.uid, definition.market, definition.source,
                                  definition.version, definition.updated_at, values, raw)
    write_document(path, document)
    return document


def import_definition(scene, path, on_conflict='rename'):
    """Cria a definição a partir do arquivo. `on_conflict`: 'rename' | 'replace'. Devolve (definição, avisos)."""
    from . import api, builtin
    document = read_document(path)
    values, warnings = document_to_values(document)
    data = api.ensure_ready(scene)
    name = str(document.get("name") or "Definição importada")
    existing = api.find_definition(scene, name=name)
    if existing is not None and on_conflict == 'replace' and not existing.builtin:
        api.remove_definition(scene, existing)
    elif existing is not None:
        name = api.unique_name(scene, name)
    definition = data.definitions.add()
    definition.uid = api.new_uid()
    definition.name = name
    definition.market = document.get("market") if document.get("market") in ('BR', 'US') else 'BR'
    definition.source = 'USER'
    definition.version = int(document.get("version") or 1)
    definition.updated_at = str(document.get("updated_at") or builtin.now_iso())
    builtin.fill_from_schema(definition, definition.market)
    for key, value in values.items():
        api.set_value(definition, key, value)
    for raw in document.get("raw_attributes") or []:
        item = definition.raw_attributes.add()
        item.attr_id, item.value, item.key = str(raw.get("id", "")), str(raw.get("value", "")), str(raw.get("key", ""))
    return definition, warnings
