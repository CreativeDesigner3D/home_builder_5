"""
BlenderToMob Cutting & Nesting Optimization Engine
Algoritmo de otimização de corte 2D Guilhotina / Bin-Packing para chapas de MDF.
Suporta refilo perimetral por borda, espessura da lâmina (kerf), veio da madeira e fitas de borda.
"""


class NestingPart:
    """Peça de corte em mm. `height` é o comprimento (veio VERTICAL acompanha o comprimento) e `width` a largura.

    `edges[4]`: espessura da fita por lado; lados 1–2 = bordas do comprimento, 3–4 = bordas da largura (clarify C-1).
    Os nomes antigos `edge_left/right/top/bottom` continuam aceitos e são aliases de leitura de `edges`.
    """

    def __init__(
        self,
        id,
        name,
        width,
        height,
        quantity=1,
        thickness=15.0,
        material="MDF Padrão",
        grain_direction='NONE',
        module_ref="",
        edge_top=0.0,
        edge_bottom=0.0,
        edge_left=0.0,
        edge_right=0.0,
        uid=None,
        component="UNCLASSIFIED",
        edges=None,
        finish="",
        source="SYNTHETIC",
        limit_status="OK",
        module_uid=None,
    ):
        self.id = id
        self.uid = str(uid) if uid else str(id)
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.quantity = int(quantity)
        self.thickness = float(thickness)
        self.material = material
        self.grain_direction = grain_direction.upper()  # 'NONE', 'VERTICAL', 'HORIZONTAL'
        self.module_ref = module_ref
        self.module_uid = module_uid
        self.component = component or "UNCLASSIFIED"
        if edges is None:
            edges = [edge_left, edge_right, edge_top, edge_bottom]
        self.edges = [float(e or 0.0) for e in list(edges)[:4]] + [0.0] * (4 - min(4, len(edges)))
        self.finish = finish or ""
        self.source = source
        self.limit_status = limit_status

    # Aliases dos nomes antigos (v1)
    @property
    def edge_left(self):
        return self.edges[0]

    @property
    def edge_right(self):
        return self.edges[1]

    @property
    def edge_top(self):
        return self.edges[2]

    @property
    def edge_bottom(self):
        return self.edges[3]

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "quantity": self.quantity,
            "thickness": self.thickness,
            "material": self.material,
            "finish": self.finish,
            "component": self.component,
            "source": self.source,
            "limit_status": self.limit_status,
            "grain_direction": self.grain_direction,
            "module_ref": self.module_ref,
            "module_uid": self.module_uid,
            "edges": {
                "top": self.edge_top,
                "bottom": self.edge_bottom,
                "left": self.edge_left,
                "right": self.edge_right
            }
        }


class NestingSheet:
    def __init__(self, id, width, height, refilo_top=10.0, refilo_bottom=10.0, refilo_left=10.0, refilo_right=10.0):
        self.id = id
        self.width = float(width)
        self.height = float(height)
        self.refilo_top = float(refilo_top)
        self.refilo_bottom = float(refilo_bottom)
        self.refilo_left = float(refilo_left)
        self.refilo_right = float(refilo_right)
        self.usable_width = self.width - (self.refilo_left + self.refilo_right)
        self.usable_height = self.height - (self.refilo_top + self.refilo_bottom)


def optimize_nesting(
    parts,
    sheet_width=2750.0,
    sheet_height=1830.0,
    refilo_top=10.0,
    refilo_bottom=10.0,
    refilo_left=10.0,
    refilo_right=10.0,
    kerf=4.0,
    allow_rotation=True,
    respect_grain=True
):
    """
    Executa a otimização de corte 2D (Guillotine / Shelf Best-Fit Decreasing).

    Args:
        parts: Lista de objetos NestingPart.
        sheet_width: Largura nominal da chapa MDF em mm (padrão: 2750mm).
        sheet_height: Altura nominal da chapa MDF em mm (padrão: 1830mm).
        refilo_*: Margens de refilo em mm para as 4 bordas.
        kerf: Espessura do corte da serra em mm (padrão: 4mm).
        allow_rotation: Permite girar peças se não houver restrição de veio.
        respect_grain: Habilita a checagem estrita de veio da madeira.

    Retorna:
        Dicionário estruturado com chapas usadas, peças alocadas, peças excedentes e estatísticas.
    """
    usable_width = sheet_width - (refilo_left + refilo_right)
    usable_height = sheet_height - (refilo_top + refilo_bottom)

    # Separação das chapas por matéria-prima, espessura e acabamento (clarify C-2)
    groups = {}
    for p in parts:
        key = (p.material, p.thickness, getattr(p, 'finish', ''))
        if key not in groups:
            groups[key] = []
        groups[key].append(p)

    all_sheets_used = []
    all_unplaced = []
    total_placed_area = 0.0
    total_nominal_sheet_area = 0.0

    global_sheet_id = 1

    for (mat, th, finish), group_parts in groups.items():
        flat_parts = []

        for p in group_parts:
            # Validação se a peça cabe na chapa útil
            w_norm = p.width <= usable_width and p.height <= usable_height
            w_rot = (p.height <= usable_width and p.width <= usable_height) if allow_rotation else False

            if not (w_norm or w_rot):
                all_unplaced.append({
                    "id": p.id,
                    "uid": p.uid,
                    "name": p.name,
                    "width": p.width,
                    "height": p.height,
                    "thickness": p.thickness,
                    "material": p.material,
                    "reason": f"Dimensões ({p.width}x{p.height}mm) excedem a área útil ({usable_width}x{usable_height}mm)"
                })
                continue

            for i in range(p.quantity):
                flat_parts.append({
                    "id": f"{p.id}_{i+1}" if p.quantity > 1 else p.id,
                    "part_id": p.id,
                    "part_uid": p.uid,
                    "name": p.name,
                    "width": p.width,
                    "height": p.height,
                    "thickness": p.thickness,
                    "material": p.material,
                    "grain_direction": p.grain_direction,
                    "module_ref": p.module_ref,
                    "edge_top": p.edge_top,
                    "edge_bottom": p.edge_bottom,
                    "edge_left": p.edge_left,
                    "edge_right": p.edge_right
                })

        # Ordenar peças por área decrescente
        flat_parts.sort(key=lambda x: x["width"] * x["height"], reverse=True)

        group_sheets = []

        for part in flat_parts:
            placed = False

            # 1. Tenta posicionar em prateleiras existentes
            for sheet in group_sheets:
                for shelf in sheet["shelves"]:
                    fits, rot = _can_fit_in_shelf(
                        part, shelf, usable_width, sheet["remaining_height"], kerf, allow_rotation, respect_grain
                    )
                    if fits:
                        w = part["height"] if rot else part["width"]
                        h = part["width"] if rot else part["height"]

                        x = shelf["current_x"]
                        y = shelf["y"]

                        shelf["parts"].append({
                            "id": part["id"],
                            "part_id": part["part_id"],
                            "part_uid": part["part_uid"],
                            "name": part["name"],
                            "x": x + refilo_left,
                            "y": y + refilo_bottom,
                            "width": w,
                            "height": h,
                            "thickness": part["thickness"],
                            "material": part["material"],
                            "rotated": rot,
                            "module_ref": part["module_ref"],
                            "edges": {
                                "top": part["edge_top"],
                                "bottom": part["edge_bottom"],
                                "left": part["edge_left"],
                                "right": part["edge_right"]
                            }
                        })

                        shelf["current_x"] += w + kerf
                        if h > shelf["height"]:
                            sheet["remaining_height"] -= (h - shelf["height"])
                            shelf["height"] = h

                        placed = True
                        break

                if placed:
                    break

                # 2. Tenta criar nova linha (shelf) na chapa existente
                fits, rot, req_h = _can_create_shelf(part, sheet["remaining_height"], usable_width, allow_rotation, respect_grain)
                if fits:
                    w = part["height"] if rot else part["width"]
                    h = part["width"] if rot else part["height"]

                    new_shelf = {
                        "y": usable_height - sheet["remaining_height"],
                        "height": h,
                        "current_x": w + kerf,
                        "parts": [{
                            "id": part["id"],
                            "part_id": part["part_id"],
                            "part_uid": part["part_uid"],
                            "name": part["name"],
                            "x": refilo_left,
                            "y": (usable_height - sheet["remaining_height"]) + refilo_bottom,
                            "width": w,
                            "height": h,
                            "thickness": part["thickness"],
                            "material": part["material"],
                            "rotated": rot,
                            "module_ref": part["module_ref"],
                            "edges": {
                                "top": part["edge_top"],
                                "bottom": part["edge_bottom"],
                                "left": part["edge_left"],
                                "right": part["edge_right"]
                            }
                        }]
                    }
                    sheet["shelves"].append(new_shelf)
                    sheet["remaining_height"] -= (h + kerf)
                    placed = True
                    break

            # 3. Se não couber em nenhuma chapa existente, aloca nova chapa MDF
            if not placed:
                fits, rot, req_h = _can_create_shelf(part, usable_height, usable_width, allow_rotation, respect_grain)
                if fits:
                    w = part["height"] if rot else part["width"]
                    h = part["width"] if rot else part["height"]

                    new_sheet = {
                        "id": global_sheet_id,
                        "material": mat,
                        "thickness": th,
                        "finish": finish,
                        "width": sheet_width,
                        "height": sheet_height,
                        "usable_width": usable_width,
                        "usable_height": usable_height,
                        "refilos": {
                            "top": refilo_top,
                            "bottom": refilo_bottom,
                            "left": refilo_left,
                            "right": refilo_right
                        },
                        "remaining_height": usable_height - (h + kerf),
                        "shelves": [{
                            "y": 0.0,
                            "height": h,
                            "current_x": w + kerf,
                            "parts": [{
                                "id": part["id"],
                                "part_id": part["part_id"],
                                "part_uid": part["part_uid"],
                                "name": part["name"],
                                "x": refilo_left,
                                "y": refilo_bottom,
                                "width": w,
                                "height": h,
                                "thickness": part["thickness"],
                                "material": part["material"],
                                "rotated": rot,
                                "module_ref": part["module_ref"],
                                "edges": {
                                    "top": part["edge_top"],
                                    "bottom": part["edge_bottom"],
                                    "left": part["edge_left"],
                                    "right": part["edge_right"]
                                }
                            }]
                        }]
                    }
                    group_sheets.append(new_sheet)
                    global_sheet_id += 1
                else:
                    all_unplaced.append({
                        "id": part["id"],
                        "uid": part["part_uid"],
                        "name": part["name"],
                        "width": part["width"],
                        "height": part["height"],
                        "thickness": part["thickness"],
                        "material": part["material"],
                        "reason": "Espaço insuficiente para inicializar chapa"
                    })

        all_sheets_used.extend(group_sheets)

    # Cálculo de métricas
    total_nominal_sheet_area = len(all_sheets_used) * sheet_width * sheet_height
    total_placed_count = 0

    for s in all_sheets_used:
        sheet_placed_area = 0.0
        for sh in s["shelves"]:
            for p in sh["parts"]:
                sheet_placed_area += p["width"] * p["height"]
                total_placed_count += 1
        s["used_area_mm2"] = sheet_placed_area
        s["utilization_percentage"] = round((sheet_placed_area / (sheet_width * sheet_height)) * 100.0, 2)
        total_placed_area += sheet_placed_area

    utilization_overall = (total_placed_area / total_nominal_sheet_area * 100.0) if total_nominal_sheet_area > 0 else 0.0

    return {
        "sheets": all_sheets_used,
        "unplaced": all_unplaced,
        "stats": {
            "sheets_count": len(all_sheets_used),
            "total_placed_parts": total_placed_count,
            "unplaced_count": len(all_unplaced),
            "utilization_percentage": round(utilization_overall, 2),
            "total_placed_area_m2": round(total_placed_area / 1_000_000.0, 3),
            "total_sheet_area_m2": round(total_nominal_sheet_area / 1_000_000.0, 3),
            "waste_area_m2": round(max(0.0, total_nominal_sheet_area - total_placed_area) / 1_000_000.0, 3)
        }
    }


def _can_fit_in_shelf(part, shelf, usable_width, remaining_height, kerf, allow_rotation, respect_grain):
    p_w = part["width"]
    p_h = part["height"]
    g_d = part["grain_direction"]

    # Tentativa sem rotação
    can_normal = not respect_grain or (g_d != 'HORIZONTAL')
    if can_normal and (shelf["current_x"] + p_w <= usable_width):
        h_diff = max(0.0, p_h - shelf["height"])
        if h_diff <= remaining_height:
            return True, False

    # Tentativa com rotação
    can_rotated = allow_rotation and (not respect_grain or (g_d != 'VERTICAL'))
    if can_rotated and (shelf["current_x"] + p_h <= usable_width):
        h_diff = max(0.0, p_w - shelf["height"])
        if h_diff <= remaining_height:
            return True, True

    return False, False


def _can_create_shelf(part, available_height, usable_width, allow_rotation, respect_grain):
    p_w = part["width"]
    p_h = part["height"]
    g_d = part["grain_direction"]

    can_normal = not respect_grain or (g_d != 'HORIZONTAL')
    if can_normal and (p_w <= usable_width and p_h <= available_height):
        return True, False, p_h

    can_rotated = allow_rotation and (not respect_grain or (g_d != 'VERTICAL'))
    if can_rotated and (p_h <= usable_width and p_w <= available_height):
        return True, True, p_w

    return False, False, 0.0
