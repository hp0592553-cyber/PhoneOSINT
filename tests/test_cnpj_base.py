from datetime import date
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from cnpj_base import import_cnpj, lookup_cnpj, public_phone


class CNPJBaseTests(unittest.TestCase):
    def test_phone_format(self):
        self.assertEqual(public_phone("31", "987654321"), "+5531987654321")
        self.assertIsNone(public_phone("31", "00000000"))
        self.assertIsNone(public_phone("", "987654321"))

    def test_import_filters_personal_names_and_inactive_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            emp, est, db = root / "Empresas0.zip", root / "Estabelecimentos0.zip", root / "local.sqlite"
            company_lines = [
                '"12345678";"EXEMPLO COMERCIAL LTDA";"2062"',
                '"87654321";"NOME DE PESSOA FISICA";"2135"',
                '"33334444";"OUTRA EMPRESA LTDA";"2062"',
            ]
            def row(base, status, phone):
                x = [""] * 30
                x[0], x[1], x[2], x[5] = base, "0001", "90", status
                x[21], x[22] = "31", phone
                return ";".join('"' + field + '"' for field in x)
            with ZipFile(emp, "w") as z:
                z.writestr("Empresas0.CSV", "\n".join(company_lines))
            with ZipFile(est, "w") as z:
                z.writestr("Estabelecimentos0.CSV", "\n".join([
                    row("12345678", "02", "987654321"),
                    row("87654321", "02", "912345678"),
                    row("33334444", "08", "998877665"),
                ]))
            result = import_cnpj(emp, est, db, date.today().isoformat())
            self.assertEqual(result["associations_indexed"], 1)
            matched = lookup_cnpj("+5531987654321", db)
            self.assertEqual(matched["matches"], [{"cnpj": "12345678000190", "name": "EXEMPLO COMERCIAL LTDA"}])
            self.assertEqual(lookup_cnpj("+5531912345678", db)["matches"], [])
            self.assertEqual(lookup_cnpj("+5531998877665", db)["matches"], [])
            with self.assertRaises(FileExistsError):
                import_cnpj(emp, est, db, date.today().isoformat())

    def test_invalid_future_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test.sqlite"
            with self.assertRaises(ValueError):
                import_cnpj(Path("n"), Path("n"), p, "2999-01-01")


if __name__ == "__main__":
    unittest.main()
