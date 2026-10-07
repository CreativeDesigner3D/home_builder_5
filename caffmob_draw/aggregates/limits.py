"""Limites do agregado no espaço do pai (feature 003, T003; RN-08, RN-09, D-12). Python puro, sem `bpy`.

Tudo é medido no referencial local do pai, com caixas alinhadas aos eixos dele: `(lo, hi)` com tuplas (x, y, z).
O agregado fica preso a uma face do pai (`POS_X`, `NEG_X`, ..., `NEG_Z`):
- `u`, `v`: distância do canto mínimo do pai ao canto mínimo do agregado nos dois eixos da face;
- `offset`: distância da face do pai à face do agregado voltada para ela; > 0 afasta, < 0 afunda.
O agregado nunca sai do contorno da face (RN-08) e afunda no máximo a espessura do pai nesse eixo (RN-09).
"""

FACES = ('POS_X', 'NEG_X', 'POS_Y', 'NEG_Y', 'POS_Z', 'NEG_Z')
FACE_LABELS = {'POS_X': "Direita (+X)", 'NEG_X': "Esquerda (−X)", 'POS_Y': "Fundo (+Y)", 'NEG_Y': "Frente (−Y)",
               'POS_Z': "Topo (+Z)", 'NEG_Z': "Base (−Z)"}
_AXIS = {'X': 0, 'Y': 1, 'Z': 2}


def face_axes(face):
    """(eixo normal, sinal, eixo u, eixo v)."""
    normal = _AXIS[face[-1]]
    sign = 1.0 if face.startswith('POS') else -1.0
    u, v = [i for i in range(3) if i != normal]
    return normal, sign, u, v


def size(box):
    lo, hi = box
    return tuple(hi[i] - lo[i] for i in range(3))


def thickness(parent_box, face):
    return size(parent_box)[face_axes(face)[0]]


def nearest_face(parent_box, point):
    """Face do pai mais próxima de `point` (centro do agregado, no espaço do pai)."""
    lo, hi = parent_box
    best, best_d = None, None
    for face in FACES:
        n, sign, _u, _v = face_axes(face)
        plane = hi[n] if sign > 0 else lo[n]
        d = abs(point[n] - plane)
        if best_d is None or d < best_d:
            best, best_d = face, d
    return best


def limits(parent_box, agg_size, face):
    """{'u': (mín, máx), 'v': (mín, máx), 'offset': (mín, None)}; agregado maior que a face fica preso em 0."""
    n, _sign, u, v = face_axes(face)
    ps = size(parent_box)
    return {'u': (0.0, max(0.0, ps[u] - agg_size[u])),
            'v': (0.0, max(0.0, ps[v] - agg_size[v])),
            'offset': (-ps[n], None)}


def clamp(parent_box, agg_size, face, u, v, offset):
    lim = limits(parent_box, agg_size, face)

    def fit(value, bounds):
        lo, hi = bounds
        value = max(lo, float(value))
        return value if hi is None else min(hi, value)

    return fit(u, lim['u']), fit(v, lim['v']), fit(offset, lim['offset'])


def box_for(parent_box, agg_size, face, u, v, offset):
    """Caixa do agregado (já com clamp) no espaço do pai."""
    u, v, offset = clamp(parent_box, agg_size, face, u, v, offset)
    lo, hi = parent_box
    n, sign, ua, va = face_axes(face)
    new_lo = [0.0, 0.0, 0.0]
    new_lo[ua] = lo[ua] + u
    new_lo[va] = lo[va] + v
    new_lo[n] = hi[n] + offset if sign > 0 else lo[n] - offset - agg_size[n]
    new_lo = tuple(new_lo)
    return new_lo, tuple(new_lo[i] + agg_size[i] for i in range(3))


def params_from_box(parent_box, agg_box, face):
    """(u, v, offset) da caixa atual do agregado; o inverso de `box_for` sem clamp."""
    lo, hi = parent_box
    a_lo, a_hi = agg_box
    n, sign, ua, va = face_axes(face)
    offset = a_lo[n] - hi[n] if sign > 0 else lo[n] - a_hi[n]
    return a_lo[ua] - lo[ua], a_lo[va] - lo[va], offset


def sunk_box(parent_box, agg_box, face):
    """Volume em que o agregado entra no pai (para o recorte), ou None se não afunda."""
    lo = tuple(max(parent_box[0][i], agg_box[0][i]) for i in range(3))
    hi = tuple(min(parent_box[1][i], agg_box[1][i]) for i in range(3))
    if any(hi[i] - lo[i] <= 1e-9 for i in range(3)):
        return None
    return lo, hi


def sunk_depth(parent_box, agg_box, face):
    box = sunk_box(parent_box, agg_box, face)
    return 0.0 if box is None else size(box)[face_axes(face)[0]]
