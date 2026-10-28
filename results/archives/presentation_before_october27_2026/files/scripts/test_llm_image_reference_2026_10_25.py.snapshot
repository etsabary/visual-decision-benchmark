import json
import unittest

from llm_image_protocol import payload
from validate_llm_image_reference_2026_10_25 import validate,DATA,EXPECTED


class LLMImagePublication(unittest.TestCase):
    def test_full_publication_preserves_old_records_and_excludes_speed_stops(self):
        s=validate();self.assertEqual(s['complete_routes'],18)
        self.assertTrue(set(EXPECTED).isdisjoint(s['rank_order']))

    def test_sol_selection_claim_is_bounded_to_completed_text_references(self):
        basis=json.loads((DATA/'selection_basis.json').read_text())
        self.assertEqual(len(basis['models']),4)
        self.assertIn('text comparison',basis['claim'])
        self.assertEqual(basis['models']['reference_sol']['correct'],1143)

    def test_image_order_variable_choice_enum_and_reasoning_controls(self):
        q=dict(question='Which image?',rules='Use order.',options=[dict(id='1',text='First'),dict(id='2',text='Second'),dict(id='3',text='Neither')])
        sol=payload('sol',q,[b'one',b'two'])
        self.assertEqual(sol['reasoning'],{'enabled':False,'effort':'none'})
        self.assertEqual([p['image_url']['url'] for p in sol['messages'][0]['content'][1:]],['data:image/png;base64,b25l','data:image/png;base64,dHdv'])
        sonnet=payload('sonnet',q,[b'one']);opus=payload('opus',q,[b'one'])
        self.assertEqual(sonnet['thinking'],{'type':'between_tools'})
        self.assertEqual(opus['thinking'],{'type':'disabled'})
        self.assertEqual(sonnet['output_config']['format']['schema']['properties']['choice']['enum'],['1','2','3'])
        self.assertNotIn('tools',sonnet);self.assertEqual(payload('qwen',q,[b'one'])['reasoning_effort'],'none')

    def test_partial_costs_are_not_extrapolated_to_full_bank(self):
        for m in json.loads((DATA/'llm_speed_stops.json').read_text()):
            self.assertEqual(m['attempted'],20)
            self.assertNotIn('core_cost_per_1000_known_usd',m)
            self.assertFalse(m['included_in_full_ranking'])


if __name__=='__main__':unittest.main()
