"""Testes de integridade do esquema do Padrão de Dimensões (T009; RN-05, RN-24, C-1, C-3)."""

import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from blendertomob.data import dimension_schema as ds

REFS = Path(_bootstrap.PACKAGE) / "assets" / "dimension_refs"


class SchemaIntegrityTest(unittest.TestCase):
    def test_todo_parametro_numerico_tem_unidade_e_faixa(self):
        for key, p in ds.PARAMS.items():
            if p.type != 'FLOAT':
                continue
            with self.subTest(key=key):
                self.assertEqual(p.unit, 'mm')
                self.assertLess(p.min, p.max)
                self.assertGreater(p.step, 0)

    def test_padroes_dentro_da_faixa(self):
        for key, p in ds.PARAMS.items():
            for market in ds.MARKETS:
                with self.subTest(key=key, market=market):
                    ok, msg = ds.validate(p, p.default(market))
                    self.assertTrue(ok, msg)

    def test_toda_imagem_de_referencia_existe(self):
        missing = sorted({p.image_key for p in ds.PARAMS.values() if not (REFS / f"{p.image_key}.png").exists()})
        self.assertEqual(missing, [], "Rode tools/render_dimension_refs.py")

    def test_codigos_promob_unicos(self):
        seen = {}
        for key, p in ds.PARAMS.items():
            for code in p.promob_codes:
                with self.subTest(code=code):
                    self.assertNotIn(code, seen, f"{code} em {seen.get(code)} e {key}")
                seen[code] = key

    def test_17_chapas_mais_componentes_em_todas_as_linhas(self):
        sheets = [c for c in ds.COMPONENTS if c.tree == ds.TREE_SHEETS]
        self.assertEqual(len(sheets), 17)
        for line in ds.LINE_CODES:
            for comp in ds.COMPONENTS:
                for fname in ds.SHEET_FIELDS:
                    with self.subTest(line=line, comp=comp.code, field=fname):
                        self.assertIn(ds.sheet_key(line, comp.code, fname), ds.PARAMS)


class BrazilDefaultsTest(unittest.TestCase):
    """Valores do Padrão Brasil aceitos no clarify C-3."""

    def value(self, key):
        return ds.PARAMS[key].default('BR')

    def test_cozinha(self):
        self.assertEqual(self.value('COZ.external.base_height'), 720.0)
        self.assertEqual(self.value('COZ.external.base_depth'), 550.0)
        self.assertEqual(self.value('COZ.external.upper_depth'), 350.0)
        self.assertEqual(self.value('COZ.external.install_height_upper'), 1500.0)
        self.assertEqual(self.value('COZ.external.tall_height'), 2200.0)
        self.assertEqual(self.value('COZ.external.toe_kick_height'), 100.0)
        self.assertEqual(self.value('COZ.external.toe_kick_setback'), 50.0)

    def test_espessuras(self):
        self.assertEqual(self.value('COZ.sheets.LAT.thickness'), 15.0)
        self.assertEqual(self.value('COZ.sheets.POR.thickness'), 18.0)
        self.assertEqual(self.value('COZ.sheets.FUN_INF.thickness'), 6.0)

    def test_fita_04_nas_bordas_visiveis(self):
        self.assertEqual(self.value('COZ.sheets.LAT.edge_1'), 0.4)
        self.assertEqual(self.value('COZ.sheets.LAT.edge_3'), 0.0)
        for side in (1, 2, 3, 4):
            self.assertEqual(self.value(f'COZ.sheets.POR.edge_{side}'), 0.4)

    def test_limite_de_chapa_e_chapa_menos_refilo(self):
        self.assertEqual(self.value('COZ.sheets.LAT.max_width'), 2730.0)
        self.assertEqual(self.value('COZ.sheets.LAT.max_length'), 1810.0)


class ValidationAndPromobTest(unittest.TestCase):
    def test_valor_invalido_informa_campo_unidade_e_faixa(self):
        ok, msg = ds.validate(ds.PARAMS['COZ.sheets.LAT.thickness'], 70)
        self.assertFalse(ok)
        for part in ("Valor Inválido", "Espessura da Chapa", "3", "60", "mm"):
            self.assertIn(part, msg)

    def test_enum_material(self):
        p = ds.PARAMS['COZ.sheets.LAT.material']
        self.assertTrue(ds.validate(p, 'MDF')[0])
        self.assertFalse(ds.validate(p, 'Granito')[0])

    def test_convencao_dos_lados_c1(self):
        # Promob 4 (esquerda, borda do comprimento numa lateral em pé) → lado 1 do BlenderToMob.
        self.assertEqual(ds.parse_promob_id('COZ_FIT_LAT_4A')['field'], 'edge_1')
        self.assertEqual(ds.parse_promob_id('COZ_FIT_LAT_1A')['field'], 'edge_3')
        self.assertEqual(ds.PROMOB_INDEX['COZ_FIT_POR_4A'], 'COZ.sheets.POR.edge_1')

    def test_familias_confirmadas(self):
        self.assertEqual(ds.PROMOB_INDEX['COZ_ESP_LAT'], 'COZ.sheets.LAT.thickness')
        self.assertEqual(ds.PROMOB_INDEX['COZ_L_LAT'], 'COZ.sheets.LAT.max_width')
        self.assertEqual(ds.PROMOB_INDEX['COZ_C_LAT'], 'COZ.sheets.LAT.max_length')
        self.assertEqual(ds.PROMOB_INDEX['COZ_MAT_PORTAS'], 'COZ.sheets.POR.material')
        self.assertIsNone(ds.parse_promob_id('DOR_AVA_FUN'))

    def test_destinos_legados(self):
        self.assertEqual(ds.PARAMS['COZ.sheets.LAT.thickness'].legacy_targets,
                         ('hb_frameless.default_carcass_part_thickness',))
        self.assertEqual(ds.PARAMS['DOR.sheets.LAT.thickness'].legacy_targets, ('hb_closets.panel_thickness',))


if __name__ == "__main__":
    unittest.main()
