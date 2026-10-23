import csv
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from benchmark import ROOT,rows
from image_publication_history import historical_path
from validate_native_images import validate

class NativePublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=ROOT/'native_images_2026-10-20'
        cls.summary=json.loads((cls.folder/'summary.json').read_text())

    def test_no_partial_or_llm_in_primary_ranking(self):
        self.assertEqual(len(self.summary['rank_order']),14)
        self.assertNotIn('respan02',self.summary['rank_order'])
        self.assertEqual(len(self.summary['original_llm_references']),3)
        self.assertTrue(all(s['n']==200 for s in self.summary['models'].values()))

    def test_named_families_and_rectangular_csv(self):
        with (self.folder/'family_scores.csv').open() as f:rr=list(csv.DictReader(f))
        self.assertEqual(len(rr),280)
        self.assertEqual(len({(r['model_id'],r['family_id']) for r in rr}),280)
        self.assertTrue(all(r['family'] and r['questions']=='10' for r in rr))

    def test_free_does_not_claim_reported_zero(self):
        for mid in ('amos_large','d3_turbo'):
            s=self.summary['models'][mid]
            self.assertTrue(s['public_free_access']);self.assertEqual(s['core_cost']['reported_records'],0)
            self.assertEqual(s['core_cost']['missing_api_records'],200)

    def test_original_seal_unchanged_and_archive_exact(self):
        from hashlib import sha256
        seal=json.loads((ROOT/'checksums.json').read_text())
        for name,h in seal['files'].items():self.assertEqual(sha256(historical_path(ROOT,name).read_bytes()).hexdigest(),h)

    def test_report_has_visible_names_and_exactly_280_score_cells(self):
        page=(ROOT/'report.html').read_text()
        self.assertEqual(page.count('class="accuracy"'),280)
        for value in self.summary['families'].values():self.assertIn(value['name'],page)
        self.assertIn('model-filter',page);self.assertIn('Free access',page)
        self.assertIn('Cost / 1,000 is a normalization',page)

    def test_sanitized_attempts_do_not_expose_gold_or_accounts(self):
        forbidden={'correct_option_id','correct_first','correct_eventual','raw_response','charge','api_key','account_id'}
        for r in rows(self.folder/'attempts.jsonl'):self.assertFalse(forbidden.intersection(r))

    def test_full_public_validation_without_network_or_private_assets(self):
        result=validate(verify_seal=(self.folder/'checksums.json').exists())
        self.assertEqual(result['status'],'PASS');self.assertEqual(result['new_first_attempts'],2421)

if __name__=='__main__':unittest.main()
