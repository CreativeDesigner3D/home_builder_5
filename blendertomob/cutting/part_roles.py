"""Papéis de peça → componente do Padrão de Dimensões (T022; D-09, D-11, clarify C-1).

Python puro. O frameless identifica as peças pelo nome do objeto (`Left Side`, `Back`, `Shelf`…); o closets, pela
propriedade `hb_part_role`. Peças sem correspondência ficam como `UNCLASSIFIED`; papéis de ferragem (cabideiro,
caixa de gaveta) não entram na lista de corte.
"""

import re

UNCLASSIFIED = "UNCLASSIFIED"
SKIP = None   # papel que não é peça de chapa

# Entradas de material de fita do GeoNodeCutpart → lado da fita.
# Lados 1–2 = bordas do comprimento (Edge L*), 3–4 = bordas da largura (Edge W*).
EDGE_INPUTS = (('Edge L1', 1), ('Edge L2', 2), ('Edge W1', 3), ('Edge W2', 4))

# Fundo conforme o tipo do gabinete frameless.
BACK_BY_CABINET_TYPE = {'BASE': "FUN_INF", 'UPPER': "FUN_SUP", 'TALL': "FUN_ALT"}

# Prefixo do nome da peça frameless → componente. A ordem importa: prefixos mais longos primeiro.
FRAMELESS_NAME_PREFIXES = (
    ("Interior Splitter Vertical", "DIV"),
    ("Interior Splitter Horizontal", "PRAT"),
    ("Interior Divider", "DIV"),
    ("Vertical Splitter", "DIV"),
    ("Splitter Vertical", "DIV"),
    ("Horizontal Splitter", "PRAT"),
    ("Splitter Horizontal", "PRAT"),
    ("Left Side", "LAT"),
    ("Right Side", "LAT"),
    ("Left Toe Kick", "ROD"),
    ("Right Toe Kick", "ROD"),
    ("Toe Kick", "ROD"),
    ("Front Stretcher", "TRA"),
    ("Back Stretcher", "TRA"),
    ("Left Back", "BACK"),
    ("Right Back", "BACK"),
    ("Back", "BACK"),
    ("Bottom", "BAS"),
    ("Top", "BAS"),
    ("Shelf", "PRAT"),
    ("Left Door", "POR"),
    ("Right Door", "POR"),
    ("Flip Up Door", "POR"),
    ("Door", "POR"),
    ("Drawer Front", "POR"),
    ("Pullout Front", "POR"),
    ("False Front", "POR"),
    ("Left Panel", "TAMPON"),
    ("Right Panel", "TAMPON"),
    ("Front Panel", "TAMPON"),
    ("Panel Board", "TAMPON"),
    ("Left End", "TAMPON"),
    ("Right End", "TAMPON"),
    ("Countertop", "TAMP"),
    ("Valance Board", "ESP"),
    ("Front Skin", "ESP"),
    ("Sink Apron", "ESP"),
    ("Support", "SAR"),
    ("Stud", "SAR"),
    ("Molding", "MOL"),
    ("Pull", SKIP),
)

# hb_part_role do closets → componente.
CLOSET_ROLES = {
    'CLOSET_PANEL': "LAT",
    'CLOSET_BOTTOM_SHELF': "BAS",
    'CLOSET_TOP_SHELF': "BAS",
    'CLOSET_TOE_KICK': "ROD",
    'CLOSET_CLEAT': "SAR",
    'CLOSET_HANG_RAIL': "SAR",
    'CLOSET_COUNTERTOP': "TAMP",
    'CLOSET_APPLIED_BACK': "FUN_ALT",
    'CLOSET_CENTER_BACK': "FUN_ALT",
    'CLOSET_FIXED_SHELF': "PRAT",
    'CLOSET_ADJ_SHELF': "PRAT",
    'CLOSET_CUBBY_SHELF': "PRAT",
    'CLOSET_BRIDGE_SHELF': "PRAT",
    'CLOSET_CUBBY_DIVISION': "DIV",
    'CLOSET_DOOR_FRONT': "POR",
    'CLOSET_DRAWER_FRONT': "POR",
    'CLOSET_ROD': SKIP,
    'CLOSET_DRAWER_BOX': SKIP,
}

_SUFFIX = re.compile(r"\.\d{3}$")


def base_name(name):
    """Nome sem o sufixo numérico do Blender (`Shelf.003` → `Shelf`)."""
    return _SUFFIX.sub("", name or "").strip()


def classify(name, role=None, cabinet_type=None):
    """Componente da peça. Devolve o código, `UNCLASSIFIED` ou `SKIP` (None) para o que não é peça de chapa."""
    if role:
        if role in CLOSET_ROLES:
            return CLOSET_ROLES[role]
    clean = base_name(name)
    for prefix, component in FRAMELESS_NAME_PREFIXES:
        if clean.startswith(prefix):
            if component == "BACK":
                return BACK_BY_CABINET_TYPE.get(cabinet_type or "", "FUN_INF")
            return component
    return UNCLASSIFIED


def is_unclassified(component):
    return component == UNCLASSIFIED
