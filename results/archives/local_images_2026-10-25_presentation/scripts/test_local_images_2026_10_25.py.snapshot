import json
import unittest

from local_image_protocol import payload, wire
from validate_local_images_2026_10_25 import validate, DATA, TIMING_FIELDS
from benchmark import rows


class LocalImagePublication(unittest.TestCase):
    def test_complete_publication_and_unchanged_hosted_records(self):
        s=validate()
        self.assertEqual(s['models']['local_h2o_lightning_4b']['correct'],117)
        self.assertEqual(s['models']['local_fovea_4b']['correct'],110)

    def test_ordered_images_and_options_are_not_silently_rewritten(self):
        question=dict(question='Compare the images.',rules='Use supplied order.',options=[dict(id='2',text='Second'),dict(id='1',text='First')])
        result=payload('model',question,[b'first',b'second'])
        self.assertEqual(result['images'],['Zmlyc3Q=','c2Vjb25k'])
        self.assertEqual(list(result['questions']['decision']['criteria']),['2','1'])
        self.assertEqual(result['questions']['decision']['instructions'],'Compare the images.\n\nRules: Use supplied order.')

    def test_local_cost_and_unscored_failures_are_not_zero_scores(self):
        s=json.loads((DATA/'summary.json').read_text())
        for mid in s['local_model_ids']:
            self.assertIsNone(s['models'][mid]['core_cost_per_1000_known_usd'])
        blocked=json.loads((DATA/'local_admission_findings.json').read_text())
        self.assertTrue(all('accuracy' not in row and 'correct' not in row for row in blocked))

    def test_local_wire_preserves_captured_unicode_escaping(self):
        self.assertEqual(wire({'state':'café'}), b'{"state":"caf\\u00e9"}')

    def test_new_public_timing_ledger_is_answer_free(self):
        for row in rows(DATA/'local_timing_evidence.jsonl'):
            self.assertEqual(set(row),TIMING_FIELDS)
            self.assertFalse({'choice','probabilities','correct','correct_option_id','raw_response','response'} & set(row))


if __name__=='__main__':unittest.main()
