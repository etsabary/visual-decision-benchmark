import base64
from copy import deepcopy
import unittest
from october27_image_evidence import payload,packet

class NativeImageUpdateContract(unittest.TestCase):
    def setUp(self):self.q=dict(question='Which image?',rules='Use order.',options=[dict(id='a',text='First'),dict(id='b',text='Second'),dict(id='c',text='Neither')])
    def test_images_keep_mime_bytes_and_order(self):
        images=[('image/jpeg',b'first'),('image/png',b'second')]
        for mid in ('d3_ultra','liquid11'):
            p=payload(self.q,images,mid);urls=p['images'] if mid=='d3_ultra' else [x['image_url']['url'] for x in p['state']]
            self.assertEqual(urls,['data:image/jpeg;base64,Zmlyc3Q=','data:image/png;base64,c2Vjb25k'])
            self.assertEqual(p['questions']['decision']['criteria'],{'a':'First','b':'Second','c':'Neither'})
    def test_reversed_images_change_binding(self):
        images=[('image/png',b'a'),('image/png',b'b')]
        for mid in ('d3_ultra','liquid11'):self.assertNotEqual(packet(payload(self.q,images,mid)),packet(payload(self.q,list(reversed(images)),mid)))
    def test_no_generated_caption_or_modified_question(self):
        q=deepcopy(self.q)
        p=payload(q,[('image/png',b'a')],'liquid11')
        self.assertEqual(p['questions']['decision']['instructions'],'Which image?\n\nRules: Use order.')
        self.assertTrue(all(x['type']=='image_url' for x in p['state']))
        self.assertEqual(q,self.q)

if __name__=='__main__':unittest.main()
