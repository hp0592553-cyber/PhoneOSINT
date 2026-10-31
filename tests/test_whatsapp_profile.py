import hashlib
import hmac
import unittest

from whatsapp_profile import example_payload, extract_profiles, valid_signature


class WhatsAppProfileTests(unittest.TestCase):
    def test_demo(self):
        profiles = extract_profiles(example_payload())
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["profile_name"], "USUARIO DE TESTE")

    def test_status_without_message(self):
        sample = example_payload()
        sample["entry"][0]["changes"][0]["value"]["messages"] = []
        self.assertEqual(extract_profiles(sample), [])

    def test_other_contact_cannot_be_mistaken_for_sender(self):
        sample = example_payload()
        sample["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"] = "5500000000000"
        self.assertEqual(extract_profiles(sample), [])

    def test_signature(self):
        body = b'{"example":true}'
        sig = "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(valid_signature(body, sig, "secret"))
        self.assertFalse(valid_signature(body + b"!", sig, "secret"))
        self.assertFalse(valid_signature(body, sig, ""))

    def test_username_without_phone(self):
        sample = example_payload()
        value = sample["entry"][0]["changes"][0]["value"]
        value["contacts"] = [{"profile": {"name": "TESTE", "username": "usuario.demo"}, "user_id": "BSUID_TESTE"}]
        value["messages"] = [{"id": "wamid.TESTE", "from_user_id": "BSUID_TESTE"}]
        profiles = extract_profiles(sample)
        self.assertEqual(profiles[0]["whatsapp_username"], "usuario.demo")
        self.assertIsNone(profiles[0]["number"])


if __name__ == "__main__":
    unittest.main()
