"""Testes dos contratos de produção (T011): JSON global v2 (interfaces/json-global-v2.md) e CSV de peças
(interfaces/csv-pecas.md), com o NestingPart estendido (T023)."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.cutting import csv_exporter, json_exporter
from caffmob_draw.cutting.nesting import NestingPart, optimize_nesting


def sample_parts():
    lateral = NestingPart(
        id="M1/LAT/0", name="Lateral esquerda", width=550, height=720, thickness=15, quantity=2,
        material="MDF", grain_direction='VERTICAL', module_ref="Balcão 600",
        uid="M1/LAT/0", component="LAT", edges=[0.4, 0, 0, 0], finish="Branco", source="CUTPART")
    porta = NestingPart(
        id="M1/POR/0", name="Porta", width=596, height=716, thickness=18, quantity=1,
        material="MDF", grain_direction='NONE', module_ref="Balcão 600",
        uid="M1/POR/0", component="POR", edges=[0.4, 0.4, 0.4, 0.4], finish="Cinza Fóssil", source="CUTPART")
    return [lateral, porta]


def sample_payload(with_plan=True):
    parts = sample_parts()
    result = optimize_nesting(parts) if with_plan else None
    return json_exporter.build_global_payload(
        project={"name": "Cozinha Teste", "uid": "P1", "rooms": [{"uid": "R1", "name": "Cozinha"}],
                 "client": {"name": "Maria"}, "company": {"name": "Marcenaria X", "author": "João"}},
        standard={"uid": "S1", "name": "Padrão Brasil", "version": 1, "market": "BR"},
        parts=parts,
        modules=[{"uid": "M1", "name": "Balcão 600", "room_uid": "R1", "line": "COZ", "library": "FRAMELESS",
                  "type": "BASE", "width_mm": 600, "height_mm": 720, "depth_mm": 550,
                  "location_mm": [0, 0, 0], "rotation_deg": [0, 0, 0], "finish": {}}],
        nesting_result=result,
        nesting_settings={"kerf_mm": 4.0, "allow_rotation": True, "respect_grain": True},
    )


class NestingPartTest(unittest.TestCase):
    def test_campos_novos_e_aliases(self):
        part = sample_parts()[0]
        self.assertEqual(part.uid, "M1/LAT/0")
        self.assertEqual(part.edges, [0.4, 0.0, 0.0, 0.0])
        self.assertEqual(part.edge_left, 0.4)        # lado 1 = borda do comprimento
        self.assertEqual(part.limit_status, "OK")

    def test_chapas_separadas_por_acabamento(self):
        a = NestingPart(id="a", name="a", width=500, height=500, thickness=18, material="MDF", finish="Branco")
        b = NestingPart(id="b", name="b", width=500, height=500, thickness=18, material="MDF", finish="Cinza")
        result = optimize_nesting([a, b])
        self.assertEqual(result["stats"]["sheets_count"], 2)
        self.assertEqual({s["finish"] for s in result["sheets"]}, {"Branco", "Cinza"})


class GlobalJsonTest(unittest.TestCase):
    def test_payload_valido(self):
        payload = sample_payload()
        self.assertEqual(json_exporter.validate_global_json(payload), [])
        self.assertEqual(payload["schema_version"], "2.1.0")      # 2.1: `machining` (feature 003)
        self.assertEqual(payload["unit"], "mm")
        part = payload["parts"][0]
        self.assertEqual(part["edges"][0], {"side": 1, "material_id": None, "thickness_mm": 0.4})
        self.assertIn(part["material_id"], {m["id"] for m in payload["materials"]})
        self.assertEqual(part["machining"], [])

    def test_versao_2_0_continua_valida(self):
        payload = sample_payload()
        payload["schema_version"] = "2.0.0"
        for part in payload["parts"]:
            del part["machining"]
        self.assertEqual(json_exporter.validate_global_json(payload), [])

    def test_machining_validado(self):
        payload = sample_payload()
        payload["parts"][0]["machining"] = [{"kind": "FURO", "x_mm": 1, "y_mm": 1, "end_x_mm": 2, "end_y_mm": 2,
                                             "depth_mm": 3}]
        self.assertTrue(any("machining[0].kind" in e for e in json_exporter.validate_global_json(payload)))

    def test_erro_aponta_caminho(self):
        payload = sample_payload()
        del payload["parts"][1]["thickness_mm"]
        payload["parts"][0]["material_id"] = "INEXISTENTE"
        errors = json_exporter.validate_global_json(payload)
        self.assertTrue(any("parts[1].thickness_mm" in e for e in errors), errors)
        self.assertTrue(any("parts[0].material_id" in e for e in errors), errors)

    def test_unidade_obrigatoria_mm(self):
        payload = sample_payload()
        payload["unit"] = "cm"
        self.assertTrue(json_exporter.validate_global_json(payload))

    def test_versao_maior_rejeitada(self):
        payload = sample_payload()
        payload["schema_version"] = "3.0.0"
        self.assertTrue(json_exporter.validate_global_json(payload))

    def test_sem_dados_do_cliente(self):
        payload = json_exporter.build_global_payload(
            project={"name": "X", "uid": "P", "rooms": [], "client": {"name": "Maria"}, "company": {"name": "Y"}},
            standard={"uid": "S", "name": "Padrão Brasil", "version": 1, "market": "BR"},
            parts=sample_parts(), include_client=False)
        self.assertIsNone(payload["project"]["client"])

    def test_ida_e_volta(self):
        payload = sample_payload()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "projeto.json"
            json_exporter.write_global_json(path, payload)
            again = json_exporter.read_global_json(path)
            json_exporter.write_global_json(Path(tmp) / "b.json", again)
            first = json.loads(path.read_text(encoding="utf-8"))
            second = json.loads((Path(tmp) / "b.json").read_text(encoding="utf-8"))
        first.pop("exported_at")
        second.pop("exported_at")
        self.assertEqual(first, second)
        parts = json_exporter.payload_to_parts(again)
        self.assertEqual([p.uid for p in parts], [p.uid for p in sample_parts()])

    def test_plano_de_corte(self):
        plan = sample_payload()["cut_plan"]
        self.assertEqual(plan["algorithm"], "guillotine-shelf-nfd")
        placed = {pl["part_uid"] for s in plan["sheets"] for pl in s["placements"]}
        self.assertEqual(placed, {"M1/LAT/0", "M1/POR/0"})

    def test_conversao_v1(self):
        v1 = {"schema_version": "1.0.0", "project": {"name": "Antigo"},
              "parts_catalog": [NestingPart(id="p1", name="Base", width=500, height=600).to_dict()],
              "sheets": [], "unplaced_parts": []}
        v2 = json_exporter.convert_v1(v1)
        self.assertEqual(v2["schema_version"], json_exporter.SCHEMA_VERSION)
        self.assertEqual(json_exporter.validate_global_json(v2), [])
        self.assertEqual(v2["parts"][0]["uid"], "p1")


class PartsCsvTest(unittest.TestCase):
    def test_formato(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pecas.csv"
            csv_exporter.write_parts_csv(path, sample_parts())
            raw = path.read_bytes()
            text = raw.decode("utf-8-sig")
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.reader(text.splitlines(), delimiter=";"))
        self.assertEqual(rows[0], list(csv_exporter.CSV_COLUMNS))
        self.assertEqual(len(rows), 3)
        lateral = dict(zip(rows[0], rows[1]))
        self.assertEqual(lateral["id"], "M1/LAT/0")
        self.assertEqual(lateral["comprimento"], "720")
        self.assertEqual(lateral["largura"], "550")
        self.assertEqual(lateral["fita_1"], "0,4")
        self.assertEqual(lateral["veio"], "COMPRIMENTO")
        self.assertEqual(lateral["quantidade"], "2")
        self.assertEqual(lateral["acabamento"], "Branco")

    def test_ordem_estavel(self):
        parts = list(reversed(sample_parts()))
        rows = csv_exporter.part_rows(parts)
        self.assertEqual([r["id"] for r in rows], ["M1/LAT/0", "M1/POR/0"])


if __name__ == "__main__":
    unittest.main()
