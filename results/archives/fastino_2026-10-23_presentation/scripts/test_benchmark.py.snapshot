from repo_layout import repo_file, frozen_file
import json
import tempfile
import unittest
from pathlib import Path
from benchmark import ROOT, MODELS, DECISION_MODELS, LLM_MODELS, rows, payload, canonical, cost, parse_saved_choice, confidence_profile
from score import load_key


class PublicPacket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions={q['candidate_id']:q for q in rows(repo_file('data/questions.jsonl', root=ROOT))}
        cls.assets={a['asset_id']:a for a in rows(repo_file('data/assets.jsonl', root=ROOT))}
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

    def test_october_16_capability_exclusions_are_not_zero_scores(self):
        capability=json.loads((repo_file('data/october_16_capabilities.json', root=ROOT)).read_text())
        self.assertEqual(capability['review_date_toronto'],'2026-10-16')
        self.assertEqual(capability['scored_image_questions_added'],0)
        self.assertEqual(len(capability['models']),3)
        for value in capability['models'].values():
            self.assertIsNone(value['accuracy'])
            self.assertEqual(value['scheduled_image_cases'],0)
        self.assertEqual(len(rows(repo_file('data/attempts.jsonl', root=ROOT))),1003)

    def test_http_200_does_not_establish_native_image_support(self):
        probes={r['model_id']:r for r in rows(repo_file('data/october_16_compatibility_probes.jsonl', root=ROOT))}
        self.assertEqual(len(probes),3)
        self.assertEqual(probes['microsoft_decision']['http_status'],400)
        for model in ('nimble_v4','nimble_v4_max'):
            self.assertEqual(probes[model]['http_status'],200)
            self.assertEqual(probes[model]['usage']['input_tokens'],26253)
        capability=json.loads((repo_file('data/october_16_capabilities.json', root=ROOT)).read_text())
        self.assertIn('JSON text',capability['nimble_contract']['state_description_excerpt'])
        self.assertFalse(capability['probe_cost']['included_in_scored_benchmark_costs'])


if __name__=='__main__':unittest.main()
