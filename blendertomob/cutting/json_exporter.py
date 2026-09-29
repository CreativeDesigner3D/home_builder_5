"""
BlenderToMob Global JSON Cut Plan Exporter
Exporta planos de corte e listas de peças estruturadas em JSON universal
compatível com CorteCloud, CutList Optimizer, Promob, OptiCut e softwares de marcenaria.
"""

import json
from datetime import datetime


def export_cut_plan_to_json(filepath, nesting_result, parts_list, project_name="Projeto Marcenaria"):
    """
    Gera e salva o arquivo JSON global contendo a lista completa de peças,
    chapas utilizadas, planos de posicionamento (coordenadas X, Y) e metadados.
    """
    stats = nesting_result.get("stats", {})
    sheets = nesting_result.get("sheets", [])
    unplaced = nesting_result.get("unplaced", [])

    unit_str = "mm"

    # Estrutura JSON Global Padronizada
    export_data = {
        "schema_version": "1.0.0",
        "generator": "BlenderToMob (Blender 5.2.0)",
        "timestamp": datetime.now().isoformat(),
        "project": {
            "name": project_name,
            "unit": unit_str,
            "total_parts_count": len(parts_list),
            "placed_parts_count": stats.get("total_placed_parts", 0),
            "unplaced_parts_count": stats.get("unplaced_count", 0),
            "sheets_count": stats.get("sheets_count", 0),
            "overall_utilization_percentage": stats.get("utilization_percentage", 0.0),
            "total_placed_area_m2": stats.get("total_placed_area_m2", 0.0),
            "total_sheet_area_m2": stats.get("total_sheet_area_m2", 0.0),
            "waste_area_m2": stats.get("waste_area_m2", 0.0),
        },
        "sheets": [],
        "parts_catalog": [p.to_dict() for p in parts_list],
        "unplaced_parts": unplaced
    }

    # Serialização das chapas e posicionamento de corte
    for s in sheets:
        sheet_data = {
            "sheet_id": s["id"],
            "material": s.get("material", "MDF"),
            "thickness_mm": s.get("thickness", 15.0),
            "dimensions_mm": {
                "width": s["width"],
                "height": s["height"],
                "usable_width": s["usable_width"],
                "usable_height": s["usable_height"]
            },
            "margins_mm": s.get("refilos", {}),
            "utilization_percentage": s.get("utilization_percentage", 0.0),
            "used_area_mm2": s.get("used_area_mm2", 0.0),
            "cuts": []
        }

        for shelf in s.get("shelves", []):
            for part in shelf.get("parts", []):
                sheet_data["cuts"].append({
                    "piece_id": part["id"],
                    "part_name": part["name"],
                    "module": part.get("module_ref", ""),
                    "x_mm": round(part["x"], 2),
                    "y_mm": round(part["y"], 2),
                    "width_mm": round(part["width"], 2),
                    "height_mm": round(part["height"], 2),
                    "thickness_mm": round(part["thickness"], 2),
                    "material": part.get("material", ""),
                    "rotated": part.get("rotated", False),
                    "edges": part.get("edges", {})
                })

        export_data["sheets"].append(sheet_data)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return filepath
