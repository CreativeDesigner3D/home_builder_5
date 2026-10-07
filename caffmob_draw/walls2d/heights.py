"""Pé-direito do projeto nas paredes — regra pura (T075; D-37, D-38, RF-42, RF-43).

Paredes de **altura cheia** acompanham o pé-direito do projeto. Ficam de fora a Mureta do editor
(`btm_wall_type == 'MURETA'`) e a meia-parede e a parede falsa do construtor legado (`WALL_TYPE` `Half`/`Fake`,
marcadas `IS_HALF_WALL`/`IS_FAKE_WALL` em `operators/walls.py`).
"""

TOLERANCE = 0.001        # 1 mm
LOW_WALL_TYPES = frozenset({'Half', 'Fake'})


def follows_project_height(btm_wall_type=None, legacy_wall_type=None):
    """A parede acompanha o pé-direito do projeto?"""
    if btm_wall_type == 'MURETA':
        return False
    return legacy_wall_type not in LOW_WALL_TYPES


def walls_to_equalize(walls, project_height, tolerance=TOLERANCE):
    """Nomes das paredes de altura cheia com pé-direito inicial ou final diferente do projeto.

    `walls`: iterável de dicts com `name`, `height`, `end_height` e, opcionais, `btm_wall_type` e `legacy_wall_type`.
    """
    found = []
    for wall in walls:
        if not follows_project_height(wall.get('btm_wall_type'), wall.get('legacy_wall_type')):
            continue
        if abs(wall['height'] - project_height) > tolerance or abs(wall['end_height'] - project_height) > tolerance:
            found.append(wall['name'])
    return found
