import contextlib
from datetime import date, timedelta
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import phonenumbers
from associated_names import associated_names, basic_report, load_evidence, workflow_main


class AssociatedNamesTests(unittest.TestCase):
    def setUp(self):
        self.number = phonenumbers.format_number(
            phonenumbers.example_number_for_type('BR', phonenumbers.PhoneNumberType.MOBILE),
            phonenumbers.PhoneNumberFormat.E164)
        self.item = dict(number=self.number, name='PESSOA FICTÍCIA A', source='truecaller',
                         checked_on=date.today().isoformat(), authorized=True)

    def test_no_result_and_no_network(self):
        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            result = associated_names(self.number)
            self.assertEqual(result['names'], [])
            self.assertNotIn(self.number, json.dumps(result))
            self.assertNotIn(self.number, basic_report(self.number))

    def test_name_provenance_and_conflict(self):
        second = dict(self.item, name='PESSOA FICTÍCIA B', source='sync_me')
        result = associated_names(self.number, [self.item, self.item, second])
        self.assertEqual(len(result['names']), 2)
        self.assertTrue(result['conflicting_names'])
        self.assertEqual(result['names'][0]['status'], 'nome associado, não verificado')
        self.assertEqual(result['names'][0]['checked_on'], date.today().isoformat())

    def test_invalid_or_unauthorized_source_evidence(self):
        cases = [None, dict(self.item, authorized=False), dict(self.item, source='unknown'),
                 dict(self.item, name=''), dict(self.item, checked_on='bad'),
                 dict(self.item, checked_on=(date.today()+timedelta(days=1)).isoformat()),
                 dict(self.item, name='::warning::\nforged'), dict(self.item, source=[])]
        result = associated_names(self.number, cases)
        self.assertEqual(result['names'], [])
        self.assertEqual(result['rejected_records'], len(cases))

    def test_other_number_is_not_used(self):
        self.assertEqual(associated_names(self.number, [dict(self.item, number='+551100000000')])['names'], [])

    def test_file_failure_is_sanitized(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'private.evidence.json'
            for content in ('not JSON ' + self.number, '{}', '[null]'):
                path.write_text(content)
                if content == '[null]':
                    self.assertEqual(load_evidence(path), [None])
                else:
                    with self.assertRaisesRegex(ValueError, '^Falha ao ler evidências locais'):
                        load_evidence(path)
            with patch.object(Path, 'read_text', side_effect=OSError(self.number)):
                with self.assertRaises(ValueError) as error:
                    load_evidence(path)
                self.assertNotIn(self.number, str(error.exception))

    def test_workflow_secret_precedence_and_private_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = Path(folder)/'summary'
            with patch.dict(os.environ, dict(AUTHORIZED='true', PHONE_SECRET=self.number,
                            PHONE_INPUT='invalid', GITHUB_STEP_SUMMARY=str(summary)), clear=True):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    workflow_main()
                self.assertEqual(output.getvalue(), summary.read_text()+'\n')
                self.assertNotIn(self.number, summary.read_text())
                self.assertIn('https://sync.me/', summary.read_text())

    def test_workflow_requires_consent_and_sanitizes_invalid_input(self):
        for consent, number in [('false', self.number), ('true', 'PRIVATE-INVALID'), ('true', '')]:
            with patch.dict(os.environ, dict(AUTHORIZED=consent, PHONE_INPUT=number), clear=True):
                with self.assertRaises(SystemExit) as error:
                    workflow_main()
                if number:
                    self.assertNotIn(number, str(error.exception))


if __name__ == '__main__':
    unittest.main()
