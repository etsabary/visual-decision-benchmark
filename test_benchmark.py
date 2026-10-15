import json
import tempfile
import unittest
from pathlib import Path
from benchmark import ROOT, MODELS, DECISION_MODELS, LLM_MODELS, rows, payload, canonical, cost, parse_saved_choice, confidence_profile
from score import load_key


class PublicPacket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
        cls.assets={a['asset_id']:a for a in rows(ROOT/'data/assets.jsonl')}
        cls.q=next(q for q in cls.questions.values() if all(cls.assets[a]['path'] for a in q['asset_ids']))

    def test_coverage(self):
        self.assertEqual(len(self.questions),200);self.assertEqual(len(self.assets),227)

    def test_model_whitelist(self):
        with self.assertRaises(ValueError):payload(self.q,self.assets,'unapproved-model')

    def test_withheld_not_silently_substituted(self):
        q=next(q for q in self.questions.values() if any(not self.assets[a]['path'] for a in q['asset_ids']))
        with self.assertRaises(FileNotFoundError):payload(q,self.assets,MODELS[0])

    def test_decision_schema(self):
        p=payload(self.q,self.assets,MODELS[0])
        self.assertEqual(p['questions']['decision']['criteria'],{o['id']:o['text'] for o in self.q['options']})
        self.assertNotIn('messages',p)

    def test_llm_profile(self):
        for m in LLM_MODELS:
            p=payload(self.q,self.assets,m)
            self.assertEqual(p['max_tokens'],32);self.assertFalse(p['reasoning']['enabled'])
            self.assertFalse(p['provider']['allow_fallbacks'])
            if m.startswith('openai/'):self.assertEqual(p['reasoning']['effort'],'none')

    def test_same_llm_messages(self):
        pp=[payload(self.q,self.assets,m)['messages'] for m in LLM_MODELS]
        self.assertEqual(pp[0],pp[1]);self.assertEqual(pp[1],pp[2])

    def test_no_key_or_family_transmitted(self):
        p=canonical(payload(self.q,self.assets,MODELS[0])).decode()
        self.assertNotIn('correct_option_id',p);self.assertNotIn('family_id',p)

    def test_cost_exact_and_missing(self):
        c=cost([{'reported_cost_usd':.1},{'reported_cost_usd':.2},{'reported_cost_usd':None}])
        self.assertEqual(c['known_usd'],'0.3');self.assertEqual(c['missing_records'],1)

    def test_truncated_id_not_valid(self):
        r={'http_status':200,'model_requested':LLM_MODELS[0],'output_text':'1','finish_reason':'length'}
        self.assertIsNone(parse_saved_choice(r,{'1','2'}))

    def test_wrong_allowed_choice_remains_usable(self):
        r={'http_status':200,'model_requested':DECISION_MODELS[0],'choice':'2'}
        self.assertEqual(parse_saved_choice(r,{'1','2'}),'2')

    def test_external_key_requires_unique_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'fixture.jsonl'
            path.write_text(json.dumps({'candidate_id':'fixture','correct_option_id':'1'})+'\n'+json.dumps({'candidate_id':'fixture','correct_option_id':'2'})+'\n')
            with self.assertRaises(ValueError):load_key(path)

    def test_confidence_coverage_uses_scheduled(self):
        records=[{'model_requested':MODELS[0],'attempt':1,'status':'ok','confidence':.95,'candidate_id':'fixture','choice':'1'}]
        d=confidence_profile({'fixture':'1'},records,scheduled=200,thresholds=(.9,))
        self.assertEqual(d[MODELS[0]]['0.9']['coverage_scheduled'],.005)
        self.assertEqual(d[MODELS[0]]['0.9']['accuracy_retained'],1)

    def test_boolean_confidence_excluded(self):
        records=[{'model_requested':MODELS[0],'attempt':1,'status':'ok','confidence':True,'candidate_id':'fixture','choice':'1'}]
        d=confidence_profile({'fixture':'1'},records,thresholds=(.9,))
        self.assertEqual(d[MODELS[0]]['0.9']['retained'],0)


if __name__=='__main__':unittest.main()
