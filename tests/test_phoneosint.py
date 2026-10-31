import unittest
from datetime import date

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType

from phoneosint import analyze, normalize_number


class PhoneOSINTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        example = phonenumbers.example_number_for_type("BR", PhoneNumberType.MOBILE)
        cls.example = phonenumbers.format_number(example, PhoneNumberFormat.E164)

    def test_valid_number_has_no_private_identity(self):
        result = analyze(self.example)
        self.assertEqual(result["number"], self.example)
        self.assertEqual(result["status"], "Titular não identificado")
        self.assertIsNone(result["company_name"])

    def test_invalid_number(self):
        with self.assertRaises(ValueError):
            normalize_number("abc")

    def test_foreign_number_rejected(self):
        with self.assertRaises(ValueError):
            normalize_number("+14155552671")

    def test_public_business_evidence_is_labeled_not_verified(self):
        item = {"number": self.example, "name": "EMPRESA FICTICIA",
                "kind": "company_public",
                "source_url": "https://www.qualempresameligou.com.br/",
                "checked_on": date.today().isoformat()}
        result = analyze(self.example, [item])
        self.assertEqual(result["company_name"], "EMPRESA FICTICIA")
        self.assertIn("não verificado automaticamente", result["status"])

    def test_personal_evidence_not_used(self):
        item = {"number": self.example, "name": "Pessoa X",
                "kind": "person",
                "source_url": "https://example.org",
                "checked_on": date.today().isoformat()}
        self.assertIsNone(analyze(self.example, [item])["company_name"])


if __name__ == "__main__":
    unittest.main()
