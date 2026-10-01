"""Definições embutidas do Padrão de Dimensões (T014; D-04).

"Padrão Brasil" (valores do clarify C-3) e "Padrão EUA (HB5)" (padrões herdados das bibliotecas do Home Builder 5)
são somente leitura: o usuário duplica para editar. Os valores vêm de `data/dimension_schema.py`.
"""

import datetime

from ..data import dimension_schema as schema

BUILTINS = (
    # uid, nome, mercado
    ('builtin-br', "Padrão Brasil", 'BR'),
    ('builtin-us', "Padrão EUA (HB5)", 'US'),
)
BUILTIN_BR_UID = 'builtin-br'
BUILTIN_US_UID = 'builtin-us'


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


def fill_from_schema(definition, market):
    """Preenche (ou completa) os valores da definição com os padrões do esquema para o mercado."""
    existing = {item.name for item in definition.values}
    for key, param in schema.PARAMS.items():
        if key in existing:
            continue
        item = definition.values.add()
        item.name = key
        default = param.default(market)
        if param.type == 'ENUM':
            item.is_text = True
            item.text = str(default)
        else:
            item.value = float(default)


def ensure_builtins(standards):
    """Garante que as definições embutidas existam e estejam completas; devolve as embutidas por uid."""
    found = {}
    for definition in standards.definitions:
        if definition.builtin:
            found[definition.uid] = definition
    for uid, name, market in BUILTINS:
        definition = found.get(uid)
        if definition is None:
            definition = standards.definitions.add()
            definition.uid = uid
            definition.name = name
            definition.builtin = True
            definition.market = market
            definition.source = 'BUILTIN'
            definition.updated_at = now_iso()
            found[uid] = definition
        fill_from_schema(definition, market)
    # `definitions.add()` pode ter realocado a coleção: devolve referências novas.
    return {d.uid: d for d in standards.definitions if d.builtin}
