"""Personalização de um módulo inserido (feature 003, T001; D-01, RN-01 a RN-06). Python puro, sem `bpy`.

Um `Spec` descreve só o que o usuário mudou na instância; campo vazio (`""`/`None`) = segue a biblioteca.
Estilos, materiais e puxadores são guardados **por nome** (RN-06). Os vãos são endereçados por um caminho estável
(`bay0/opening1`), calculado pelo adaptador da biblioteca a partir da ordem dos filhos.
"""

from dataclasses import asdict, dataclass, field

SECTIONS = ('FRONTS', 'PULLS', 'MATERIALS', 'INTERIOR')
SECTION_LABELS = {'FRONTS': "Frentes", 'PULLS': "Puxadores", 'MATERIALS': "Materiais", 'INTERIOR': "Divisões internas"}
FRONT_TYPES = ('DOOR_LEFT', 'DOOR_RIGHT', 'DOUBLE_DOORS', 'DRAWERS', 'FLIP_UP', 'PANEL', 'OPEN')
FRONT_LABELS = {'DOOR_LEFT': "Porta à esquerda", 'DOOR_RIGHT': "Porta à direita", 'DOUBLE_DOORS': "Duas portas",
                'DRAWERS': "Gavetas", 'FLIP_UP': "Basculante", 'PANEL': "Painel fixo", 'OPEN': "Vazio"}
PULL_POSITIONS = ('DEFAULT', 'TOP', 'MIDDLE', 'BOTTOM', 'SIDE')
NO_PULL = "__NONE__"
GROUPS = ('CAIXA', 'FRENTES', 'FUNDO', 'INTERNO')
GROUP_LABELS = {'CAIXA': "Caixa", 'FRENTES': "Frentes", 'FUNDO': "Fundo", 'INTERNO': "Interno"}
MAX_DRAWERS = 8
MAX_SHELVES = 20
MAX_DIVIDERS = 10


@dataclass
class Interior:
    shelves: int = 0
    dividers: int = 0
    drawers: int = 0
    heights: list = field(default_factory=list)   # alturas digitadas (m, a partir da base do vão); vazio = iguais


@dataclass
class Opening:
    path: str
    front: str = ""                 # um de FRONT_TYPES; vazio = como está
    drawer_count: int = 0           # só com front == 'DRAWERS'
    door_style: str = ""
    drawer_style: str = ""
    pull_model: str = ""            # nome do puxador; NO_PULL = sem puxador
    pull_position: str = 'DEFAULT'
    front_material: str = ""
    interior: Interior = None


@dataclass
class Spec:
    library: str = ""
    openings: list = field(default_factory=list)
    part_materials: dict = field(default_factory=dict)     # caminho da peça → material
    group_materials: dict = field(default_factory=dict)    # grupo (GROUPS) → material
    pull_all_fronts: str = ""                               # puxador para todas as frentes; vazio = por frente
    aggregates: list = field(default_factory=list)          # [{name, parent_path, kind}] (só no manifesto)

    def opening(self, path):
        for item in self.openings:
            if item.path == path:
                return item
        return None

    def ensure_opening(self, path):
        item = self.opening(path)
        if item is None:
            item = Opening(path=path)
            self.openings.append(item)
        return item

    def is_empty(self):
        return not (self.openings or self.part_materials or self.group_materials or self.pull_all_fronts
                    or self.aggregates)


# Serialização ---------------------------------------------------------------------------------------------------

def to_dict(spec):
    data = asdict(spec)
    for item in data['openings']:
        if item['interior'] is None:
            del item['interior']
    return data


def from_dict(data):
    data = dict(data or {})
    openings = []
    for raw in data.get('openings', []):
        raw = dict(raw)
        interior = raw.pop('interior', None)
        known = {k: raw[k] for k in Opening.__dataclass_fields__ if k in raw}
        item = Opening(**known)
        if interior is not None:
            item.interior = Interior(**{k: interior[k] for k in Interior.__dataclass_fields__ if k in interior})
            item.interior.heights = [float(h) for h in item.interior.heights]
        openings.append(item)
    return Spec(library=str(data.get('library', "")), openings=openings,
                part_materials=dict(data.get('part_materials', {})),
                group_materials=dict(data.get('group_materials', {})),
                pull_all_fronts=str(data.get('pull_all_fronts', "")),
                aggregates=list(data.get('aggregates', [])))


# Validação ------------------------------------------------------------------------------------------------------

def validate(spec):
    """Lista de mensagens (vazia = válido). Não conhece o Blender: só formato e domínios."""
    errors = []
    seen = set()
    for item in spec.openings:
        where = f"vão {item.path}"
        if not item.path:
            errors.append("vão sem caminho")
        if item.path in seen:
            errors.append(f"{where}: repetido")
        seen.add(item.path)
        if item.front and item.front not in FRONT_TYPES:
            errors.append(f"{where}: frente desconhecida '{item.front}'")
        if item.front == 'DRAWERS' and not 1 <= int(item.drawer_count) <= MAX_DRAWERS:
            errors.append(f"{where}: quantidade de gavetas fora de 1 a {MAX_DRAWERS}")
        if item.pull_position not in PULL_POSITIONS:
            errors.append(f"{where}: posição de puxador desconhecida '{item.pull_position}'")
        if item.interior is not None:
            errors += [f"{where}: {msg}" for msg in validate_interior(item.interior)]
    for group in spec.group_materials:
        if group not in GROUPS:
            errors.append(f"grupo de material desconhecido '{group}'")
    for key, name in list(spec.group_materials.items()) + list(spec.part_materials.items()):
        if not str(name).strip():
            errors.append(f"material vazio em '{key}'")
    return errors


def validate_interior(interior, inner_height=None):
    errors = []
    if not 0 <= int(interior.shelves) <= MAX_SHELVES:
        errors.append(f"prateleiras fora de 0 a {MAX_SHELVES}")
    if not 0 <= int(interior.dividers) <= MAX_DIVIDERS:
        errors.append(f"divisórias fora de 0 a {MAX_DIVIDERS}")
    if not 0 <= int(interior.drawers) <= MAX_DRAWERS:
        errors.append(f"gavetas internas fora de 0 a {MAX_DRAWERS}")
    heights = list(interior.heights)
    if heights:
        if len(heights) != int(interior.shelves):
            errors.append("a quantidade de alturas não bate com a de prateleiras")
        if any(b <= a for a, b in zip(heights, heights[1:])):
            errors.append("as alturas precisam ser crescentes")
        if heights[0] <= 0.0 or (inner_height is not None and heights[-1] >= inner_height):
            errors.append("altura fora do vão")
    return errors


def shelf_positions(count, inner_height, thickness, heights=None):
    """Altura da face de baixo de cada prateleira a partir da base do vão: digitadas ou vãos livres iguais."""
    count = int(count)
    if count <= 0:
        return []
    if heights:
        return [float(h) for h in heights]
    gap = (float(inner_height) - count * float(thickness)) / (count + 1)
    return [gap * (i + 1) + thickness * i for i in range(count)]


# Grupos de material ---------------------------------------------------------------------------------------------

def group_of_component(component):
    """Grupo de material (GROUPS) de um componente do Padrão de Dimensões (`cutting/part_roles.py`)."""
    if component == "POR":
        return 'FRENTES'
    if component in ("BACK", "FUN_INF", "FUN_SUP", "FUN_ALT"):
        return 'FUNDO'
    if component in ("PRAT", "DIV"):
        return 'INTERNO'
    return 'CAIXA'


def interior_to_json(interior):
    import json
    return json.dumps({"shelves": int(interior.shelves), "dividers": int(interior.dividers),
                       "drawers": int(interior.drawers), "heights": [float(h) for h in interior.heights]})


def interior_from_json(text):
    import json
    if not text:
        return None
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return Interior(shelves=int(data.get("shelves", 0)), dividers=int(data.get("dividers", 0)),
                    drawers=int(data.get("drawers", 0)), heights=[float(h) for h in data.get("heights", [])])

