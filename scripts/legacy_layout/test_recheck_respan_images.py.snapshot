import unittest
from unittest.mock import patch

import recheck_respan_images as repeat


class RespanRepeat(unittest.TestCase):
    def test_distinct_evidence_directory(self):
        self.assertNotEqual(repeat.REPEAT/'respan02',repeat.BASELINE)
        self.assertEqual(repeat.REPEAT.parent,repeat.BASELINE.parent.parent)

    def test_manifest_labels_single_stream_and_no_publication(self):
        with patch.object(repeat.original,'digest',return_value='baseline-hash'):
            value=repeat.repeat_manifest({'speed_screen':'original cutoff','model':'original model'})
        self.assertFalse(value['publication_authorized'])
        self.assertEqual(value['speed_screen'],'original cutoff')
        self.assertEqual(value['model'],'original model')
        self.assertEqual(value['repeat_of_stop_receipt_sha256'],'baseline-hash')
        self.assertIn('One serial',value['concurrency'])

if __name__=='__main__':unittest.main()
