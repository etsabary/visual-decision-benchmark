from copy import deepcopy
import json
import unittest

import publish_celeris_images_2026_10_26 as b


class CelerisImagePublication(unittest.TestCase):
    def test_publication_and_previous_measurements(self):
        from validate_celeris_images_2026_10_26 import validate
        self.assertEqual(validate()['complete_routes'],19)

    def test_named_images_preserve_order_options_and_resolution(self):
        q=dict(question='Which image?',rules='Use order.',options=[dict(id='a',text='First'),dict(id='b',text='Second'),dict(id='c',text='Neither')])
        p=b.payload(q,[b'first',b'second'])
        self.assertEqual(p['x_celeris']['images'],{'image_1':'data:image/png;base64,Zmlyc3Q=','image_2':'data:image/png;base64,c2Vjb25k'})
        self.assertIn('image_1, image_2',p['state'])
        self.assertEqual(p['questions']['decision']['criteria'],{'a':'First','b':'Second','c':'Neither'})
        self.assertEqual(p['x_celeris']['max_soft_tokens'],1120)
        self.assertFalse(p['x_celeris']['explain'])

    def test_native_contract_rejects_wrong_identity_explanations_and_truncation(self):
        raw=dict(model=b.MODEL,answers={'decision':dict(type='choice',choice='a',probabilities={'a':.8,'b':.1,'c':.1})},usage=dict(input_tokens=20,output_tokens=0))
        self.assertEqual(b.native_choice(raw,['a','b','c']),'a')
        for mutate in (lambda r:r.update(model='other'),lambda r:r.update(reasoning='extra'),
            lambda r:r.update(state_truncated=True),lambda r:r['usage'].update(output_tokens=1)):
            changed=deepcopy(raw);mutate(changed)
            with self.assertRaises(AssertionError):b.native_choice(changed,['a','b','c'])

    def test_estimated_cost_stays_separate_from_receipts_and_probes(self):
        m=json.loads((b.DEST/'summary.json').read_text())['models'][b.MID]
        self.assertEqual(m['usage_based_core_cost_usd'],'0.01175164')
        self.assertEqual(m['core_cost']['reported_records'],0)
        self.assertEqual(m['probe_cost_usd'],'0.00042344')
        self.assertTrue(b.money(m).startswith('~$'))


if __name__=='__main__':unittest.main()
