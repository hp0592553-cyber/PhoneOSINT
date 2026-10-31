import unittest

from demo_crosscheck import demo_report


class DemoCrosscheckTests(unittest.TestCase):
    def test_synthetic_and_conflicting(self):
        result = demo_report()
        self.assertEqual(result["mode"], "SIMULACAO - NENHUM DADO REAL")
        self.assertTrue(result["conflicting_names"])
        self.assertFalse(result["identity_confirmed"])
        self.assertEqual(result["matches"], 3)

    def test_no_sensitive_fields(self):
        result = demo_report()
        self.assertNotIn("cpf", result)
        self.assertNotIn("address", result)
        self.assertNotIn("phone", result)


if __name__ == "__main__":
    unittest.main()
