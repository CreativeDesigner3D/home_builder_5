"""Modelo da planta de paredes do Editor de Paredes (T003, T054; D-01, D-25, RN-15 a RN-18). Python puro.

Uma **cadeia** é uma sequência de trechos ligados ponta a ponta. Ela tem nós (pontos 2D, metros) e um trecho entre cada
par de nós consecutivos; fechada, o último nó liga de volta ao primeiro.

- **Os nós são a face interna** (medida real, RN-15): o comprimento interno de um trecho é a distância entre seus nós.
- **`side`** (Direção) diz para que lado do sentido dos nós a espessura cresce: `'LEFT'` (como o `GeoNodeWall` do Home
  Builder 5 faz, +Y local) ou `'RIGHT'`. A face externa é a linha deslocada pela espessura para esse lado, com as
  esquadrias (`t·tan(meia virada)`), e mede a interna + as espessuras nos cantos.
- Num contorno fechado, a espessura deve ficar para fora (`outward_side`): assim o interior fica do lado dos nós e, no
  3D, em −Y local — onde o Home Builder põe a frente dos módulos e o "para dentro" das portas.
"""

import copy
import math

INNER, OUTER = 'INNER', 'OUTER'
SIDES = ('LEFT', 'RIGHT')                       # lado da espessura em relação ao sentido dos nós (Direção)
WALL_TYPES = ('NORMAL', 'DIVISORIA', 'MURETA')
TYPE_DEFAULTS = {'NORMAL': {}, 'DIVISORIA': {'thickness': 0.10}, 'MURETA': {'height': 1.10, 'end_height': 1.10}}

LIMITS = {   # RN-18 (metros)
    'length': (0.01, 100.0), 'thickness': (0.01, 2.0), 'height': (0.5, 10.0), 'end_height': (0.5, 10.0),
    'angle_abs': (0.0, 360.0), 'angle_rel': (-180.0, 180.0),
}
LABELS = {'length': "Comprimento", 'thickness': "Espessura", 'height': "Pé-direito inicial",
          'end_height': "Pé-direito final", 'angle_abs': "Ângulo absoluto", 'angle_rel': "Ângulo relativo"}


def validate(field, value):
    lo, hi = LIMITS[field]
    if not lo <= value <= hi:
        unit = "°" if field.startswith('angle') else " m"
        raise ValueError(f"Valor Inválido: {LABELS[field]} deve estar entre {lo:g} e {hi:g}{unit} (recebido: "
                         f"{value:g}{unit}).")


def _norm_angle(rad):
    while rad > math.pi:
        rad -= 2 * math.pi
    while rad < -math.pi:
        rad += 2 * math.pi
    return rad


class Segment:
    def __init__(self, thickness=0.15, height=2.6, end_height=None, wall_type='NORMAL', lock_angle=False,
                 source=None):
        self.thickness = thickness
        self.height = height
        self.end_height = height if end_height is None else end_height
        self.wall_type = wall_type
        self.lock_angle = lock_angle
        self.source = source            # nome da parede existente (None = trecho novo)


class Chain:
    def __init__(self, nodes, segments, closed=False, side='LEFT'):
        if side not in SIDES:
            raise ValueError(f"Direção inválida: {side}")
        self.nodes = [tuple(map(float, n)) for n in nodes]
        self.segments = list(segments)
        self.closed = closed
        self.side = side

    # Topologia ---------------------------------------------------------------------------------------------
    def segment_count(self):
        return len(self.segments)

    def endpoints(self, i):
        n = len(self.nodes)
        return self.nodes[i], self.nodes[(i + 1) % n]

    def direction(self, i):
        (x0, y0), (x1, y1) = self.endpoints(i)
        return math.atan2(y1 - y0, x1 - x0)

    def length(self, i):
        (x0, y0), (x1, y1) = self.endpoints(i)
        return math.hypot(x1 - x0, y1 - y0)

    def prev_index(self, i):
        if i > 0:
            return i - 1
        return len(self.segments) - 1 if self.closed else None

    def next_index(self, i):
        if i < len(self.segments) - 1:
            return i + 1
        return 0 if self.closed else None

    # Ângulos -----------------------------------------------------------------------------------------------
    def angle_abs(self, i):
        return math.degrees(self.direction(i)) % 360.0

    def angle_rel(self, i):
        """Virada em relação ao trecho anterior (graus, −180 a 180; +90 = virou à esquerda)."""
        p = self.prev_index(i)
        if p is None:
            return 0.0
        return math.degrees(_norm_angle(self.direction(i) - self.direction(p)))

    def miter_angles(self, i):
        """(esquerda, direita) em radianos, como `calculate_wall_miter_angles` do legado."""
        p, n = self.prev_index(i), self.next_index(i)
        left = _norm_angle(self.direction(i) - self.direction(p)) / 2.0 if p is not None else 0.0
        right = -_norm_angle(self.direction(n) - self.direction(i)) / 2.0 if n is not None else 0.0
        return left, right

    def signed_turn(self):
        return sum(self.angle_rel(i) for i in range(len(self.segments)) if self.prev_index(i) is not None)

    def is_ccw(self):
        """Contorno anti-horário (área com sinal positivo) ou, aberto, virada total positiva."""
        if self.closed and len(self.nodes) >= 3:
            area = 0.0
            for k in range(len(self.nodes)):
                (x0, y0), (x1, y1) = self.nodes[k], self.nodes[(k + 1) % len(self.nodes)]
                area += x0 * y1 - x1 * y0
            return area > 0
        return self.signed_turn() >= 0

    def outward_side(self):
        """Lado que deixa a espessura para fora do contorno (anti-horário → direita; horário → esquerda)."""
        return 'RIGHT' if self.is_ccw() else 'LEFT'

    # Linhas ------------------------------------------------------------------------------------------------
    def inner_line(self, i):
        return self.endpoints(i)

    def outer_line(self, i):
        """Face deslocada pela espessura para `side`, com as esquadrias."""
        sign = 1.0 if self.side == 'LEFT' else -1.0
        (x0, y0), (x1, y1) = self.endpoints(i)
        d = self.direction(i)
        dx, dy = math.cos(d), math.sin(d)
        nx, ny = -dy * sign, dx * sign
        t = self.segments[i].thickness
        left, right = self.miter_angles(i)
        s0 = sign * t * math.tan(left)
        s1 = sign * t * math.tan(right)
        return ((x0 + nx * t + dx * s0, y0 + ny * t + dy * s0), (x1 + nx * t + dx * s1, y1 + ny * t + dy * s1))

    def line(self, i, which):
        return self.outer_line(i) if which == OUTER else self.inner_line(i)

    def face_length(self, i, which):
        (x0, y0), (x1, y1) = self.line(i, which)
        return math.hypot(x1 - x0, y1 - y0)

    def shifted_nodes(self, factor):
        """Nós deslocados `factor × espessura` para a esquerda do sentido (negativo = direita), com esquadria nos cantos:
        (n0 + n1) / (1 + cos θ) = (n0 + n1) / (2·cos²(θ/2)), θ = virada entre os trechos."""
        shifted = []
        for k in range(len(self.nodes)):
            segs = [k] if k < len(self.segments) else []
            prev = k - 1 if k > 0 else (len(self.segments) - 1 if self.closed else None)
            if prev is not None:
                segs.append(prev)
            nx = ny = 0.0
            for idx in segs:
                d = self.direction(idx)
                nx += -math.sin(d) * self.segments[idx].thickness * factor
                ny += math.cos(d) * self.segments[idx].thickness * factor
            if len(segs) == 2:
                half = _norm_angle(self.direction(segs[0]) - self.direction(segs[1])) / 2.0
                scale = 1.0 / (2.0 * math.cos(half) ** 2) if abs(math.cos(half)) > 1e-6 else 0.5
                nx, ny = nx * scale, ny * scale
            x, y = self.nodes[k]
            shifted.append((x + nx, y + ny))
        return shifted

    def hb_order(self):
        """(nós, trechos) na ordem do Home Builder 5, que sempre põe a espessura à esquerda: `side == 'RIGHT'`
        devolve a cadeia invertida (mesma geometria, sentido oposto)."""
        if self.side == 'LEFT':
            return list(self.nodes), list(self.segments)
        twin = Chain(self.nodes, self.segments, self.closed, self.side)
        twin.invert()
        return twin.nodes, twin.segments

    # Edição ------------------------------------------------------------------------------------------------
    def set_length(self, i, value, which=INNER):
        """Muda o comprimento medido na face `which`, movendo o nó final no sentido do trecho (RN-18)."""
        validate('length', value)
        direction = self.direction(i)
        if which == INNER:
            self._move_end(i, value, direction)
            return
        ref_len = self.length(i)
        # A esquadria depende do ângulo dos vizinhos, que muda quando o nó anda: ajuste iterativo.
        for _ in range(12):
            ref_len += value - self.face_length(i, which)
            validate('length', ref_len)
            self._move_end(i, ref_len, direction)
            if abs(self.face_length(i, which) - value) < 1e-7:
                break

    def set_angle_abs(self, i, degrees):
        validate('angle_abs', degrees % 360.0 if degrees != 360.0 else 360.0)
        self._move_end(i, self.length(i), math.radians(degrees))

    def set_angle_rel(self, i, degrees):
        validate('angle_rel', degrees)
        p = self.prev_index(i)
        base = self.direction(p) if p is not None else 0.0
        self._move_end(i, self.length(i), base + math.radians(degrees))

    def _move_end(self, i, length, direction):
        (x0, y0), _ = self.endpoints(i)
        end = (x0 + math.cos(direction) * length, y0 + math.sin(direction) * length)
        self.move_node((i + 1) % len(self.nodes), end)

    def move_node(self, k, point):
        """Move o nó `k`; com "Bloquear Ângulo" no trecho que termina nele, o nó só anda na direção do trecho."""
        k = k % len(self.nodes)
        incoming = k - 1 if k > 0 else (len(self.segments) - 1 if self.closed else None)
        if incoming is not None and self.segments[incoming].lock_angle:
            (x0, y0), (x1, y1) = self.endpoints(incoming)
            dx, dy = x1 - x0, y1 - y0
            size = math.hypot(dx, dy) or 1.0
            ux, uy = dx / size, dy / size
            proj = (point[0] - x0) * ux + (point[1] - y0) * uy
            point = (x0 + ux * proj, y0 + uy * proj)
        self.nodes[k] = (float(point[0]), float(point[1]))

    def set_segment_value(self, i, field, value):
        seg = self.segments[i]
        if field in ('thickness', 'height', 'end_height'):
            validate(field, value)
            setattr(seg, field, value)
            if field == 'height':
                seg.end_height = value          # o final acompanha o inicial (RN-18)
        elif field == 'wall_type':
            if value not in WALL_TYPES:
                raise ValueError(f"Valor Inválido: tipo de parede {value}.")
            seg.wall_type = value
            for key, default in TYPE_DEFAULTS[value].items():
                setattr(seg, key, default)
        elif field == 'lock_angle':
            seg.lock_angle = bool(value)
        else:
            raise ValueError(f"Campo desconhecido: {field}")

    def split(self, i, point):
        """Divide o trecho `i` no ponto (projetado na referência); os dois novos trechos herdam as propriedades."""
        (x0, y0), (x1, y1) = self.endpoints(i)
        dx, dy = x1 - x0, y1 - y0
        size_sq = dx * dx + dy * dy
        t = max(0.05, min(0.95, ((point[0] - x0) * dx + (point[1] - y0) * dy) / size_sq)) if size_sq else 0.5
        new_node = (x0 + dx * t, y0 + dy * t)
        self.nodes.insert(i + 1, new_node)
        clone = copy.copy(self.segments[i])
        clone.source = None
        self.segments.insert(i + 1, clone)
        return i + 1

    def remove_node(self, k):
        """Remove o nó `k`, unindo os dois trechos vizinhos (o de antes continua). Ponta de cadeia aberta: remove o
        trecho da ponta."""
        n = len(self.nodes)
        if len(self.segments) <= 1:
            raise ValueError("Uma cadeia precisa de pelo menos um trecho.")
        if not self.closed and k in (0, n - 1):
            del self.nodes[k]
            del self.segments[0 if k == 0 else -1]
            return
        del self.nodes[k]
        del self.segments[k if k < len(self.segments) else 0]

    def invert(self):
        """Inverte o sentido da cadeia mantendo a parede no lugar: os nós e trechos trocam de ordem e a Direção troca,
        de modo que a espessura continua do mesmo lado físico."""
        self.side = 'RIGHT' if self.side == 'LEFT' else 'LEFT'
        self.nodes.reverse()
        if self.closed:
            last = self.segments.pop(-1)
            self.segments.reverse()
            self.segments.insert(0, last)
            # nós: o primeiro continua sendo o primeiro após girar
            self.nodes.insert(0, self.nodes.pop(-1))
        else:
            self.segments.reverse()

    def touches_start(self, point, tolerance=0.01):
        """O ponto está a até `tolerance` (m) do primeiro nó?"""
        x0, y0 = self.nodes[0]
        return math.hypot(point[0] - x0, point[1] - y0) <= tolerance

    def close_if_touching(self, tolerance=0.01):
        """Fecha a cadeia aberta de 3+ trechos cujo último nó está a até `tolerance` do primeiro (tira o duplicado).
        Devolve True se fechou (D-34, D-35)."""
        if self.closed or len(self.segments) < 3 or len(self.nodes) < 4:
            return False
        if not self.touches_start(self.nodes[-1], tolerance):
            return False
        self.nodes.pop(-1)
        self.closed = True
        return True

    def close(self):
        """Fecha o contorno: o último nó coincide com o primeiro (sai da lista) e o último trecho liga ao primeiro."""
        if len(self.nodes) >= 4 and math.hypot(self.nodes[-1][0] - self.nodes[0][0],
                                                self.nodes[-1][1] - self.nodes[0][1]) < 1e-6:
            self.nodes.pop(-1)
        self.closed = True


class WallPlan:
    """Conjunto de cadeias (o ambiente) mais trechos existentes removidos.

    `references`: segmentos [(a, b)] só para ver (paredes da camada nova, D-05); não são editados nem aplicados.
    """

    def __init__(self, chains=None, references=None):
        self.chains = list(chains or [])
        self.removed_sources = []
        self.converted_sources = []      # objetos da camada nova convertidos: removidos no OK (D-22)
        self.references = list(references or [])

    def bounds(self):
        points = [p for c in self.chains for p in c.nodes] + [p for seg in self.references for p in seg]
        if not points:
            return ((-1.0, -1.0), (4.0, 3.0))
        return ((min(p[0] for p in points), min(p[1] for p in points)),
                (max(p[0] for p in points), max(p[1] for p in points)))

    def remove_chain_segment_sources(self, chain):
        for seg in chain.segments:
            if seg.source:
                self.removed_sources.append(seg.source)


def plan_signature(plan):
    """Assinatura do rascunho (para saber se houve alteração desde a abertura, D-30)."""
    chains = tuple(
        (tuple((round(x, 6), round(y, 6)) for x, y in c.nodes), c.closed, c.side,
         tuple((round(sg.thickness, 6), round(sg.height, 6), round(sg.end_height, 6), sg.wall_type, sg.lock_angle,
                sg.source) for sg in c.segments))
        for c in plan.chains)
    return chains, tuple(plan.removed_sources), tuple(plan.converted_sources)


def rectangle(width, depth, thickness=0.15, height=2.6, origin=(0.0, 0.0)):
    """Sala retangular com medidas **internas** `width` × `depth`, desenhada no sentido anti-horário e com a espessura
    para fora (Direção direita)."""
    x, y = origin
    nodes = [(x, y), (x + width, y), (x + width, y + depth), (x, y + depth)]
    return Chain(nodes, [Segment(thickness, height) for _ in range(4)], closed=True, side='RIGHT')
