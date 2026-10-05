"""Matemática da abertura de frentes (T051; D-20, D-21, D-25). Python puro, sem `bpy` nem `mathutils`.

Vetores são tuplas (x, y, z) e matrizes 3×3 são tuplas de linhas. Convenções:
- articuladas (porta, basculante): valor em **graus**, 0 = fechada, até `MAX_ANGLE`;
- gaveta/pullout: valor como **fração** do curso, 0 = fechada, 1 = curso total.
"""

import math

MAX_ANGLE = 90.0                 # limite comum a todas as linhas (D-20)
SNAP_STOPS = (0.0, 45.0, 90.0)   # paradas do controle giratório (D-25)
SNAP_TOLERANCE = 5.0             # graus

# Teto físico de cada mecanismo legado, usado nas conversões (D-20).
FACE_FRAME_MAX_ANGLE = 100.0     # solver_face_frame.DOOR_MAX_SWING_ANGLE
CLOSETS_MAX_ANGLE = 110.0        # types_closets.DOOR_OPEN_ANGLE
BTM_MAX_ANGLE = 90.0             # geometry/door_controller.py (0,2 m de curso → 90°)


# ----------------------------------------------------------------------------------------------------------------
# Valores
# ----------------------------------------------------------------------------------------------------------------

def clamp_angle(degrees):
    return max(0.0, min(MAX_ANGLE, float(degrees)))


def clamp_fraction(fraction):
    return max(0.0, min(1.0, float(fraction)))


def snap_angle(degrees, stops=SNAP_STOPS, tolerance=SNAP_TOLERANCE):
    """Encaixa na parada mais próxima quando estiver a até `tolerance` graus; senão devolve o valor limitado."""
    value = clamp_angle(degrees)
    nearest = min(stops, key=lambda stop: abs(stop - value))
    return float(nearest) if abs(nearest - value) <= tolerance else value


def degrees_to_fraction(degrees, legacy_max):
    """Graus → fração do mecanismo legado (ex.: 90° no face frame = 0,9 de `swing_percent`)."""
    return clamp_fraction(clamp_angle(degrees) / float(legacy_max))


def fraction_to_degrees(fraction, legacy_max):
    return clamp_angle(float(fraction) * float(legacy_max))


# ----------------------------------------------------------------------------------------------------------------
# Vetores e matrizes
# ----------------------------------------------------------------------------------------------------------------

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def length(a):
    return math.sqrt(dot(a, a))


def normalize(a):
    size = length(a)
    if size < 1e-12:
        raise ValueError("Vetor nulo")
    return scale(a, 1.0 / size)


def mat_vec(m, v):
    return tuple(dot(row, v) for row in m)


def axis_angle_matrix(axis, radians):
    """Matriz de rotação (Rodrigues) em torno de `axis` (normalizado aqui)."""
    x, y, z = normalize(axis)
    c, s = math.cos(radians), math.sin(radians)
    t = 1.0 - c
    return (
        (t * x * x + c, t * x * y - s * z, t * x * z + s * y),
        (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
        (t * x * z - s * y, t * y * z + s * x, t * z * z + c),
    )


def matrix_to_euler_xyz(m):
    """Euler XYZ (ordem do Blender: R = Rz·Ry·Rx) de uma matriz de rotação."""
    sy = -m[2][0]
    sy = max(-1.0, min(1.0, sy))
    ry = math.asin(sy)
    if abs(math.cos(ry)) > 1e-9:
        rx = math.atan2(m[2][1], m[2][2])
        rz = math.atan2(m[1][0], m[0][0])
    else:  # trava de cardã
        rx = math.atan2(-m[1][2], m[1][1])
        rz = 0.0
    return (rx, ry, rz)


# ----------------------------------------------------------------------------------------------------------------
# Poses de abertura (espaço do pai da peça)
# ----------------------------------------------------------------------------------------------------------------

def swing_sign(axis, free_vector, outward):
    """+1 ou −1: sentido da rotação em torno de `axis` que leva `free_vector` (da dobradiça até a borda livre)
    para o lado de `outward` (face frontal da frente)."""
    return 1.0 if dot(cross(normalize(axis), free_vector), outward) >= 0.0 else -1.0


def edge_rotation(axis, hinge_offset, free_vector, outward, degrees):
    """Pose de uma frente que gira em torno de uma aresta.

    `axis`: direção da aresta da dobradiça; `hinge_offset`: da origem da peça até um ponto da aresta;
    `free_vector`: da aresta até a borda livre; `outward`: direção da face frontal.
    Devolve (`delta_rotation_euler`, `delta_location`) para aplicar com a rotação composta no espaço do pai
    (Blender: delta_rot · rot) e o pivô na origem da peça.
    """
    angle = math.radians(clamp_angle(degrees)) * swing_sign(axis, free_vector, outward)
    rotation = axis_angle_matrix(axis, angle)
    # Rotacionar em torno do ponto h = o + offset: o' = h + R(o − h) → delta = offset − R·offset
    delta_location = sub(hinge_offset, mat_vec(rotation, hinge_offset))
    return matrix_to_euler_xyz(rotation), delta_location


def slide(direction, travel, fraction):
    """`delta_location` de uma gaveta: `travel` metros na direção `direction` (normalizada) vezes a fração."""
    return scale(normalize(direction), float(travel) * clamp_fraction(fraction))


def frame_from_extents(rotation, length_vec, width_vec, thickness_vec):
    """Direções da peça no espaço do pai: `rotation` (3×3 da rotação fechada) aplicada aos vetores locais
    de comprimento (X), largura (Y) e espessura (Z) com sinal e tamanho."""
    return mat_vec(rotation, length_vec), mat_vec(rotation, width_vec), mat_vec(rotation, thickness_vec)


def side_hinge(length_dir, width_dir, thickness_dir):
    """Porta de giro lateral: dobradiça na aresta da origem ao longo do comprimento (vertical)."""
    return {'axis': length_dir, 'hinge_offset': (0.0, 0.0, 0.0), 'free': width_dir, 'outward': thickness_dir}


def top_hinge(length_dir, width_dir, thickness_dir):
    """Basculante: dobradiça na aresta de cima (ao longo da largura); a borda livre é a de baixo."""
    if length_dir[2] >= 0.0:      # comprimento sobe a partir da origem → dobradiça no fim do comprimento
        hinge_offset, free = length_dir, scale(length_dir, -1.0)
    else:                          # origem já está em cima
        hinge_offset, free = (0.0, 0.0, 0.0), length_dir
    return {'axis': width_dir, 'hinge_offset': hinge_offset, 'free': free, 'outward': thickness_dir}


def bottom_hinge(length_dir, width_dir, thickness_dir):
    """Basculante para baixo: dobradiça na aresta de baixo; a borda livre é a de cima."""
    if length_dir[2] >= 0.0:
        hinge_offset, free = (0.0, 0.0, 0.0), length_dir
    else:
        hinge_offset, free = length_dir, scale(length_dir, -1.0)
    return {'axis': width_dir, 'hinge_offset': hinge_offset, 'free': free, 'outward': thickness_dir}


def pose_for(hinge, degrees):
    return edge_rotation(hinge['axis'], hinge['hinge_offset'], hinge['free'], hinge['outward'], degrees)
