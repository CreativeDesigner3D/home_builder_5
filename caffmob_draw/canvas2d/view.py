"""Núcleo das telas 2D (T002; D-01). Python puro, sem `bpy`.

Uma `View2D` mapeia coordenadas do mundo 2D (metros) para pixels de uma área retangular da tela (`rect` =
x, y, largura, altura em pixels, origem embaixo à esquerda, como no desenho `POST_PIXEL` do Blender).
Também traz pan, zoom, enquadrar, grade, encaixe ortogonal e distâncias em pixels, usados pelo "Mover Sobre" e pelo
editor de paredes.
"""

import math

ORTHO_TOLERANCE_DEG = 2.5


class View2D:
    def __init__(self, rect, scale=100.0, center=(0.0, 0.0)):
        self.rect = tuple(float(v) for v in rect)    # x, y, largura, altura (px)
        self.scale = float(scale)                   # pixels por metro
        self.center = (float(center[0]), float(center[1]))   # ponto do mundo no centro do retângulo

    # Conversões -------------------------------------------------------------------------------------------
    def to_screen(self, point):
        x, y, w, h = self.rect
        return (x + w / 2.0 + (point[0] - self.center[0]) * self.scale,
                y + h / 2.0 + (point[1] - self.center[1]) * self.scale)

    def to_world(self, pixel):
        x, y, w, h = self.rect
        return (self.center[0] + (pixel[0] - x - w / 2.0) / self.scale,
                self.center[1] + (pixel[1] - y - h / 2.0) / self.scale)

    def contains(self, pixel):
        x, y, w, h = self.rect
        return x <= pixel[0] <= x + w and y <= pixel[1] <= y + h

    # Navegação --------------------------------------------------------------------------------------------
    def pan(self, dx_px, dy_px):
        self.center = (self.center[0] - dx_px / self.scale, self.center[1] - dy_px / self.scale)

    def zoom(self, factor, anchor_px=None):
        """Aproxima (`factor` > 1) ou afasta mantendo o ponto sob `anchor_px` parado na tela."""
        if anchor_px is None:
            self.scale = max(1e-6, self.scale * factor)
            return
        before = self.to_world(anchor_px)
        self.scale = max(1e-6, self.scale * factor)
        after = self.to_world(anchor_px)
        self.center = (self.center[0] + before[0] - after[0], self.center[1] + before[1] - after[1])

    def fit(self, bounds, margin=0.1):
        """Enquadra `bounds` = ((xmin, ymin), (xmax, ymax)) com margem relativa."""
        (x0, y0), (x1, y1) = bounds
        w_world = max(x1 - x0, 1e-6) * (1.0 + 2 * margin)
        h_world = max(y1 - y0, 1e-6) * (1.0 + 2 * margin)
        self.scale = min(self.rect[2] / w_world, self.rect[3] / h_world)
        self.center = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)

    # Grade e encaixe --------------------------------------------------------------------------------------
    def grid_lines(self, step):
        """Linhas de grade visíveis: (verticais, horizontais) em coordenadas do mundo."""
        if step <= 0:
            return [], []
        (x0, y0) = self.to_world((self.rect[0], self.rect[1]))
        (x1, y1) = self.to_world((self.rect[0] + self.rect[2], self.rect[1] + self.rect[3]))
        if (x1 - x0) / step > 400 or (y1 - y0) / step > 400:   # grade densa demais para desenhar
            return [], []
        xs = [i * step for i in range(math.floor(x0 / step), math.ceil(x1 / step) + 1)]
        ys = [i * step for i in range(math.floor(y0 / step), math.ceil(y1 / step) + 1)]
        return xs, ys


def snap_to_grid(point, step):
    if step <= 0:
        return tuple(point)
    return (round(point[0] / step) * step, round(point[1] / step) * step)


def ortho_snap(origin, point, tolerance_deg=ORTHO_TOLERANCE_DEG):
    """Encaixa `point` na direção 0°/90°/180°/270° a partir de `origin` quando estiver a até `tolerance_deg`.
    Devolve (ponto, travado)."""
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return tuple(point), False
    angle = math.degrees(math.atan2(dy, dx)) % 360.0
    nearest = round(angle / 90.0) * 90.0
    if abs(angle - nearest) <= tolerance_deg:
        rad = math.radians(nearest)
        return (origin[0] + math.cos(rad) * length, origin[1] + math.sin(rad) * length), True
    return tuple(point), False


def distance_point_point(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def distance_point_segment(point, a, b):
    ax, ay = a
    bx, by = b
    px, py = point
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-18:
        return distance_point_point(point, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
