from repo_layout import repo_file, frozen_file
import unittest
from analyze_native_images import percentile,wilson,money,sanitized,summarize

class NativeAnalysis(unittest.TestCase):
    def test_inclusive_linear_p95(self):
        self.assertEqual(percentile(list(range(1,201)),.95),190.04999999999998)
        self.assertEqual(percentile([4],.95),4)
        self.assertIsNone(percentile([],.95))

    def test_missing_cost_not_free(self):
        m=money([{'reported_cost_usd':None,'accounted_cost_usd':None}])
        self.assertEqual(m['missing_api_records'],1)
        self.assertEqual(m['reported_records'],0)

    def test_free_access_distinct_from_api_price(self):
        m=money([{'reported_cost_usd':None,'accounted_cost_usd':'0'}])
        self.assertEqual(m['missing_api_records'],1)
        self.assertEqual(m['accounted_usd'],'0')

    def test_no_account_fields_or_gold_in_export(self):
        r=sanitized({'choice':'2','correct_option_id':'1','account':'secret','charge':{'balance':123},
            'usage':{'input_tokens':10,'cost':.2,'account_id':'secret'},'raw_response':{'api_key':'secret'}})
        self.assertEqual(r,{'choice':'2','usage':{'input_tokens':10,'cost':.2}})

    def test_wilson_not_a_guarantee(self):
        low,hi=wilson(10,10)
        self.assertLess(low,.73);self.assertLessEqual(hi,1)

    def test_first_attempt_only_primary_and_failed_case_stays_denominator(self):
        r=dict(request_index=1,attempt=1,candidate_id='x',status='http_failure',choice=None,
            latency_ms=10,started={'toronto':'t'},completed={'toronto':'u'})
        s=summarize([r,dict(r,attempt=2,status='ok',choice='1')],{'x':'1'},
            {'x':{'family_id':'V01'}},{'x':{'analysis_subset':'perception_control'}})
        self.assertEqual((s['n'],s['correct'],s['eventual_correct'],s['retries']),(1,0,1,1))

if __name__=='__main__':unittest.main()
