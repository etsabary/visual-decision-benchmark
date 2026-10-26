import json
import unittest
from repo_layout import ROOT,repo_file


class FastinoImages(unittest.TestCase):
    def test_complete_publication(self):
        from validate_fastino_images import validate
        d=validate()
        self.assertEqual(d['rank_order'][:2],['amos_large','fastino_glide'])

    def test_old_metrics_exactly_unchanged(self):
        old=json.loads((repo_file('native_images_2026-10-20')/'summary.json').read_text())
        new=json.loads((ROOT/'results/releases/fastino_2026-10-23/summary.json').read_text())
        for mid,s in old['models'].items():self.assertEqual(new['models'][mid],s)


if __name__=='__main__':unittest.main()
