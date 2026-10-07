"""Testes do parser/formatador de medidas (T008; RN-01, D-07). Rodar: python3 -m unittest discover tests"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.data import units


class ParseLengthTest(unittest.TestCase):
    def test_virgula_decimal_em_cm(self):
        self.assertAlmostEqual(units.parse_length("75,5", "CM"), 0.755)

    def test_ponto_decimal(self):
        self.assertAlmostEqual(units.parse_length("75.5", "CM"), 0.755)

    def test_fita_preserva_decimal(self):
        self.assertAlmostEqual(units.parse_length("0,4", "MM"), 0.0004)
        self.assertNotAlmostEqual(units.parse_length("0,4", "MM"), 0.004)

    def test_sufixo_sobrepoe_unidade_padrao(self):
        self.assertAlmostEqual(units.parse_length("2 m", "MM"), 2.0)
        self.assertAlmostEqual(units.parse_length("80cm", "MM"), 0.8)
        self.assertAlmostEqual(units.parse_length("15 MM", "CM"), 0.015)

    def test_milhar_e_decimal(self):
        self.assertAlmostEqual(units.parse_length("1.234,5", "MM"), 1.2345)
        self.assertAlmostEqual(units.parse_length("1,234.5", "MM"), 1.2345)

    def test_unidade_longa_do_blender(self):
        self.assertAlmostEqual(units.parse_length("10", "CENTIMETERS"), 0.1)

    def test_negativo_rejeitado_por_padrao(self):
        with self.assertRaises(ValueError) as ctx:
            units.parse_length("-15")
        self.assertIn("Valor Inválido", str(ctx.exception))

    def test_negativo_permitido(self):
        self.assertAlmostEqual(units.parse_length("-15", "MM", allow_negative=True), -0.015)

    def test_zero_pode_ser_proibido(self):
        self.assertEqual(units.parse_length("0"), 0.0)
        with self.assertRaises(ValueError):
            units.parse_length("0", allow_zero=False)

    def test_fracoes_e_imperial_rejeitados(self):
        for text in ("1 1/2", "2'6\"", "3/4", "12 in", "abc", "", "1,2,3"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                units.parse_length(text)


class FormatLengthTest(unittest.TestCase):
    def test_virgula_e_sem_zeros_redundantes(self):
        self.assertEqual(units.format_length(0.7555, "CM"), "75,55 cm")
        self.assertEqual(units.format_length(0.9, "MM"), "900 mm")
        self.assertEqual(units.format_length(0.0004, "MM"), "0,4 mm")

    def test_precisao_padrao_0_1_mm(self):
        self.assertEqual(units.format_length(0.12345, "MM"), "123,5 mm")
        self.assertEqual(units.format_length(1.23456, "M"), "1,2346 m")

    def test_sem_sufixo_e_ponto(self):
        self.assertEqual(units.format_length(0.0755, "CM", with_suffix=False, decimal_comma=False), "7.55")

    def test_zero_negativo_vira_zero(self):
        self.assertEqual(units.format_length(-0.00000001, "MM"), "0 mm")

    def test_format_value_com_unidade_explicita(self):
        self.assertEqual(units.format_value(0.8, unit="CENTIMETERS"), "80 cm")

    def test_ida_e_volta(self):
        for unit in ("MM", "CM", "M"):
            for meters in (0.0004, 0.015, 0.7555, 2.75):
                with self.subTest(unit=unit, meters=meters):
                    text = units.format_length(meters, unit)
                    self.assertAlmostEqual(units.parse_length(text, unit), meters, places=4)


if __name__ == "__main__":
    unittest.main()
