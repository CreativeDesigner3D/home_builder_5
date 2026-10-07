"""Testes de importação/exportação do DIMENSIONEXPORT do Promob (T010; RF-058; contrato promob-dimensionexport.md).

Fixture: tests/fixtures/dimensionexport_me_moveis.xml (692 atributos, "ME MOVEIS - COZ. ESCR.").
"""

import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.data import dimension_schema as ds
from caffmob_draw.standards import io_promob

FIXTURE = _bootstrap.FIXTURES / "dimensionexport_me_moveis.xml"


def original_pairs():
    root = ET.parse(FIXTURE).getroot()
    return [(a.get('ID'), a.get('VALUE')) for a in root.iter('ATTRIBUTE')]


class ReadTest(unittest.TestCase):
    def setUp(self):
        self.doc = io_promob.read_dimensionexport(FIXTURE)
        self.data = io_promob.to_definition_data(self.doc)

    def test_leitura(self):
        self.assertEqual(len(self.doc.attributes), 692)
        self.assertEqual(self.doc.name, "ME MOVEIS - COZ. ESCR.")

    def test_familias_confirmadas_mapeadas(self):
        values = self.data['values']
        self.assertEqual(values['COZ.sheets.LAT.thickness'], 15.0)
        self.assertEqual(values['COZ.sheets.LAT.max_width'], 2730.0)
        self.assertEqual(values['COZ.sheets.LAT.max_length'], 1810.0)
        self.assertEqual(values['COZ.sheets.LAT.material'], 'MDF')
        self.assertEqual(values['COZ.sheets.POR.edge_1'], 0.4)      # COZ_FIT_POR_4A
        self.assertEqual(values['DOR.sheets.ESP.max_width'], 2750.0)
        self.assertEqual(values['DOR.external.tall_height'], 2400.0)  # ALT_ARM

    def test_todo_valor_mapeado_e_valido(self):
        for key, value in self.data['values'].items():
            with self.subTest(key=key):
                ok, msg = ds.validate(ds.PARAMS[key], value)
                self.assertTrue(ok, msg)

    def test_relatorio(self):
        report = self.data['report']
        self.assertEqual(report['total'], 692)
        self.assertEqual(report['mapped'] + len(report['unrecognized']), 692)
        self.assertGreater(report['mapped'], 100)
        self.assertIn('DOR_AVA_FUN', report['unrecognized'])

    def test_preserva_todos_os_atributos(self):
        self.assertEqual([(a['id'], a['value']) for a in self.data['raw_attributes']], original_pairs())


class RoundTripTest(unittest.TestCase):
    def test_reexporta_os_mesmos_692_pares(self):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "saida.dimensionExport"
            io_promob.write_dimensionexport(out, data['name'], data['values'], data['raw_attributes'])
            again = io_promob.read_dimensionexport(out)
        self.assertEqual(again.name, "ME MOVEIS - COZ. ESCR.")
        self.assertEqual(set(again.attributes), set(original_pairs()))

    def test_valor_alterado_e_exportado(self):
        data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
        data['values']['COZ.sheets.LAT.thickness'] = 18.0
        data['values']['COZ.sheets.POR.edge_1'] = 1.0
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "saida.xml"
            io_promob.write_dimensionexport(out, data['name'], data['values'], data['raw_attributes'])
            pairs = dict(io_promob.read_dimensionexport(out).attributes)
        self.assertEqual(pairs['COZ_ESP_LAT'], '18')
        self.assertEqual(pairs['COZ_FIT_POR_4A'], '1')
        self.assertEqual(pairs['DOR_AVA_FUN'], '-15')


class ErrorsTest(unittest.TestCase):
    def write(self, tmp, content):
        path = Path(tmp) / "x.xml"
        path.write_text(content, encoding='utf-8')
        return path

    def test_xml_malformado(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(io_promob.PromobFormatError):
            io_promob.read_dimensionexport(self.write(tmp, "<DIMENSIONEXPORT><DEFINITION>"))

    def test_raiz_errada(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(io_promob.PromobFormatError):
            io_promob.read_dimensionexport(self.write(tmp, "<OUTRA/>"))

    def test_sem_atributos(self):
        content = '<DIMENSIONEXPORT VERSION="-1"><DEFINITION DESCRIPTION="X"><ATTRIBUTES/></DEFINITION></DIMENSIONEXPORT>'
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(io_promob.PromobFormatError):
            io_promob.read_dimensionexport(self.write(tmp, content))

    def test_id_duplicado_mantem_o_ultimo(self):
        content = ('<DIMENSIONEXPORT VERSION="-1"><DEFINITION DESCRIPTION="X"><ATTRIBUTES>'
                   '<ATTRIBUTE ID="COZ_ESP_LAT" VALUE="15"/><ATTRIBUTE ID="COZ_ESP_LAT" VALUE="18"/>'
                   '</ATTRIBUTES></DEFINITION></DIMENSIONEXPORT>')
        with tempfile.TemporaryDirectory() as tmp:
            doc = io_promob.read_dimensionexport(self.write(tmp, content))
        data = io_promob.to_definition_data(doc)
        self.assertEqual(data['values']['COZ.sheets.LAT.thickness'], 18.0)
        self.assertIn('COZ_ESP_LAT', data['report']['duplicates'])

    def test_valor_fora_do_dominio_vai_para_nao_reconhecidos(self):
        content = ('<DIMENSIONEXPORT VERSION="-1"><DEFINITION DESCRIPTION="X"><ATTRIBUTES>'
                   '<ATTRIBUTE ID="COZ_ESP_LAT" VALUE="999"/></ATTRIBUTES></DEFINITION></DIMENSIONEXPORT>')
        with tempfile.TemporaryDirectory() as tmp:
            data = io_promob.to_definition_data(io_promob.read_dimensionexport(self.write(tmp, content)))
        self.assertNotIn('COZ.sheets.LAT.thickness', data['values'])
        self.assertEqual(len(data['report']['invalid']), 1)


if __name__ == "__main__":
    unittest.main()
