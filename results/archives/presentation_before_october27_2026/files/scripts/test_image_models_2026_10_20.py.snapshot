from repo_layout import repo_file, frozen_file
import base64
from copy import deepcopy
import json
from pathlib import Path
import unittest

import image_models_2026_10_20 as run


class NativeImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assets={a['asset_id']:a for a in run.rows(repo_file('data/assets.jsonl', root=run.ROOT))}
        cls.q=next(q for q in run.rows(repo_file('data/questions.jsonl', root=run.ROOT)) if all(assets[a]['path'] for a in q['asset_ids']))
        cls.assets={aid:{**assets[aid],'path':str(repo_file(assets[aid]['path'], root=run.ROOT))} for aid in cls.q['asset_ids']}

    def response(self,mid='d3_turbo',choice='2',probs=None):
        return dict(http_status=200,error='',raw_response={
            'model':run.config(mid)['model'],'answers':{'decision':{'choice':choice,
            'probabilities':probs or {'1':.1,'2':.8,'3':.1}}},'usage':{'input_tokens':100,'output_tokens':0}})

    def test_exact_original_openrouter_image_body_except_model_and_pin(self):
        original=run.bank.payload(self.q,self.assets,'typesafe/jev-1.14')
        new=run.payload(self.q,self.assets,'jev113');new.pop('provider');new['model']='typesafe/jev-1.14'
        self.assertEqual(new,original)

    def test_top_images_contain_same_ordered_bytes_and_no_caption(self):
        for mid in ('amos_large','d3_turbo'):
            p=run.payload(self.q,self.assets,mid)
            self.assertEqual(p['state'],'')
            self.assertEqual([base64.b64decode(v.split(',',1)[1] if v.startswith('data:') else v) for v in p['images']],
                [Path(self.assets[a]['path']).read_bytes() for a in self.q['asset_ids']])
            self.assertEqual(p['questions']['decision']['instructions'],self.q['question']+'\n\nRules: '+self.q['rules'])

    def test_provider_pinned_without_fallback(self):
        for mid in run.MODELS:
            p=run.payload(self.q,self.assets,mid)
            if run.config(mid)['provider']:
                self.assertEqual(p['provider']['only'],[run.config(mid)['provider']])
                self.assertFalse(p['provider']['allow_fallbacks'])
            else:self.assertNotIn('provider',p)

    def test_parser_uses_actual_variable_choice_set(self):
        r=run.parse(self.response(),{'1','2','3'},'d3_turbo')
        self.assertEqual(r['status'],'ok');self.assertTrue(r['probabilities_valid'])
        self.assertEqual(run.parse(self.response(choice='4'),{'1','2','3'},'d3_turbo')['status'],'invalid_answer')

    def test_probability_warning_is_not_choice_retry(self):
        r=run.parse(self.response(probs={'1':.5,'2':.5,'3':.5}),{'1','2','3'},'d3_turbo')
        self.assertEqual(r['status'],'ok');self.assertFalse(r['probabilities_valid'])

    def test_no_default_model_and_output_telemetry_is_not_an_architecture_claim(self):
        r=self.response();r['raw_response']['model']='vllm-sr/d3-flash'
        self.assertEqual(run.parse(r,{'1','2','3'},'d3_turbo')['status'],'identity_mismatch')
        for value in (1,None,False):
            r=self.response();r['raw_response']['usage']['output_tokens']=value
            parsed=run.parse(r,{'1','2','3'},'d3_turbo')
            self.assertEqual(parsed['status'],'ok')
            self.assertEqual(parsed['reported_output_tokens'],value)

    def test_cost_distinguishes_unreported_free_access_and_real_receipts(self):
        free=run.parse(self.response(),{'1','2','3'},'d3_turbo')
        self.assertIsNone(free['reported_cost_usd']);self.assertEqual(free['accounted_cost_usd'],'0')
        r=self.response('kettei_fat');r['raw_response']['charge']={'amount_usd':'0.000001920'}
        paid=run.parse(r,{'1','2','3'},'kettei_fat')
        self.assertEqual(paid['reported_cost_usd'],'0.000001920')
        r=self.response('respan02')
        self.assertIsNone(run.parse(r,{'1','2','3'},'respan02')['accounted_cost_usd'])

    def test_public_amos_does_not_load_a_key(self):
        self.assertEqual(run.credentials('amos_large'),'')

    def test_only_fourteen_new_decision_models(self):
        self.assertEqual(len(run.MODELS),14)
        self.assertNotIn('reference_sol',run.MODELS)
        self.assertNotIn('nimble_v4_max',run.MODELS)
        self.assertNotIn('jev114',run.MODELS)

    def test_speed_screen_requires_twenty_and_strictly_more_than_two_seconds(self):
        self.assertFalse(run.speed_stop([3000]*19))
        self.assertFalse(run.speed_stop([2000]*20))
        self.assertTrue(run.speed_stop([2001]*20))
        self.assertFalse(run.speed_stop([200]*19+[90000]))


if __name__=='__main__':unittest.main()
