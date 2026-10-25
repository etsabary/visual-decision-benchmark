"""Public aggregate, timing, format-variant and presentation checks; offline only."""
from collections import Counter
import csv
from hashlib import sha256
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import statistics
from urllib.parse import urlsplit

from benchmark import rows
from repo_layout import ROOT

NAME='local_images_2026-10-25'
DATA=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/fastino_2026-10-23'
EXPECTED={'local_h2o_lightning_4b':117,'local_fovea_4b':110}
TIMING_FIELDS={'model_id','model_requested','request_index','candidate_id','family_id','attempt','status','latency_ms',
               'request_payload_sha256','image_sha256','image_variant','output_tokens','state_truncated'}


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.cells=[];self.links=[];self.summary=[];self.local_summary=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and 'data-family' in a:self.cells.append(a)
        if tag=='tr' and 'data-summary-model' in a:
            self.summary.append(a['data-summary-model'])
            if a.get('class')=='local-model':self.local_summary.append(a['data-summary-model'])
        self.links.extend(v for k,v in attrs if k in ('href','src'))
        if 'id' in a:self.ids.add(a['id'])


def percentile(xs):
    xs=sorted(xs);p=(len(xs)-1)*.95;a,b=math.floor(p),math.ceil(p)
    return xs[a]+(xs[b]-xs[a])*(p-a)


def validate():
    s=json.loads((DATA/'summary.json').read_text());old=json.loads((OLD/'summary.json').read_text())
    assert len(s['models'])==len(s['rank_order'])==s['decision_models_ranked']==17
    assert s['rank_order']==sorted(s['models'],key=lambda mid:(-s['models'][mid]['correct'],s['models'][mid]['median_ms']))
    assert s['hosted_model_count']==15 and s['local_model_count']==2 and set(s['local_model_ids'])==set(EXPECTED)
    assert all(s['models'][mid]==m for mid,m in old['models'].items()),'Previous model record changed'
    assert s['exclusions']==old['exclusions'] and s['prior_summary_sha256']==digest(OLD/'summary.json')
    assert s['location_colors']=={'local':'#7c3aed','hosted':'#16728c'}
    assert s['random_uniform_baseline']==old['random_uniform_baseline']
    questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    original={a['asset_id']:a for a in rows(ROOT/'data/assets.jsonl')}
    variant=json.loads((DATA/'image_variant_manifest.json').read_text())
    protocol=json.loads((DATA/'execution_protocol.json').read_text())
    assert variant['pillow_version']=='12.3.0' and len(variant['assets'])==227
    assert variant['questions_sha256']==protocol['question_sha256']==digest(ROOT/'data/questions.jsonl')
    assert len(protocol['question_order'])==len(set(protocol['question_order']))==200
    assert set(protocol['question_order'])==set(questions)
    assert sum(a['converted'] for a in variant['assets'].values())==47
    assert sum(a['original_public_path'] is None for a in variant['assets'].values())==6
    for aid,a in variant['assets'].items():
        assert a['original_sha256']==original[aid]['sha256'] and a['original_mime']==original[aid]['mime']
        assert a['mime']=='image/png' and a['width']==original[aid]['width'] and a['height']==original[aid]['height']
        assert len(a['decoded_rgb_sha256'])==len(a['sha256'])==64
        assert set(a)=={'mime','sha256','original_sha256','original_mime','converted','decoded_rgb_sha256','width','height','bytes','original_public_path'}
        if not a['converted']:assert a['sha256']==a['original_sha256']
        if a['original_public_path'] is not None:assert digest(ROOT/a['original_public_path'])==a['original_sha256']
    rr=rows(DATA/'local_timing_evidence.jsonl');assert len(rr)==400
    assert all(set(r)==TIMING_FIELDS for r in rr)
    for mid,correct in EXPECTED.items():
        m=s['models'][mid];r=[r for r in rr if r['model_id']==mid]
        assert m['n']==m['usable']==len(r)==200 and m['correct']==correct and m['accuracy']==correct/200
        assert m['execution_location']=='local' and m['core_cost_per_1000_known_usd'] is None and not m['public_free_access']
        assert m['cost_source']=='local_hardware_electricity_unmeasured' and m['device']=='cuda:0'
        assert [x['candidate_id'] for x in r]==protocol['question_order'] and [x['request_index'] for x in r]==list(range(1,201))
        assert len({x['candidate_id'] for x in r})==200
        assert Counter(x['family_id'] for x in r)=={f'V{i:02}':10 for i in range(1,21)}
        assert sum(v['correct'] for v in m['families'].values())==correct
        for x in r:
            assert x['status']=='ok' and x['attempt']==1 and x['output_tokens']==0 and x['state_truncated'] is False
            assert x['model_requested']==m['model_requested'] and x['family_id']==questions[x['candidate_id']]['family_id']
            assert x['image_sha256']==[variant['assets'][aid]['sha256'] for aid in questions[x['candidate_id']]['asset_ids']]
            assert len(x['request_payload_sha256'])==64 and x['latency_ms']>0
        times=[x['latency_ms'] for x in r]
        assert abs(m['mean_ms']-statistics.mean(times))<1e-8 and m['median_ms']==statistics.median(times)
        assert abs(m['p95_ms']-percentile(times))<1e-8
        assert max(statistics.median(times[:n]) for n in range(20,201))<=2000
    findings=json.loads((DATA/'local_admission_findings.json').read_text())
    assert len(findings)==7 and all(v['scored_attempts']==0 for v in findings)
    assert all(v['model'] not in {m['model_requested'] for m in s['models'].values()} for v in findings)
    with (DATA/'family_scores.csv').open() as f:cells=list(csv.DictReader(f))
    assert len(cells)==len({(c['model_id'],c['family_id']) for c in cells})==340
    for c in cells:assert int(c['correct'])==s['models'][c['model_id']]['families'][c['family_id']]['correct']
    page=Page();page.feed((ROOT/'docs/report.html').read_text())
    assert page.summary==s['rank_order'] and set(page.local_summary)==set(EXPECTED)
    assert len(page.cells)==340
    for c in page.cells:assert int(c['data-correct'])==s['models'][c['data-model-id']]['families'][c['data-family']]['correct']
    assert digest(ROOT/'docs/report.html')==digest(DATA/'report.html')
    html=(ROOT/'docs/report.html').read_text()
    for text in ('#7c3aed','#16728c','PNG-lossless-from-reviewed-decoded-RGB-v1','Pillow 12.3.0','58.5%','55.0%','Cost / 1,000','Unmeasured local compute'):
        assert text in html,text
    from build_image_site import build
    build()
    for target in page.links:
        url=urlsplit(target)
        if url.scheme or url.netloc:continue
        if url.path:assert (ROOT/'_site'/url.path).exists(),target
        elif url.fragment:assert url.fragment in page.ids,target
    for path in DATA.rglob('*'):
        if path.is_file():assert digest(ROOT/'docs'/NAME/path.relative_to(DATA))==digest(path),path
    for stem in ('overview','abilities_1','abilities_2','abilities_3','abilities_4'):
        svg=(DATA/(stem+'.svg')).read_text();assert '#7c3aed' in svg and '#16728c' in svg
    forbidden=('192.168.','127.0.0.1','/Users/','correct_option_id','"choice":','"probabilities":','api_key','Authorization: Bearer')
    for filename in ('local_timing_evidence.jsonl','image_variant_manifest.json','local_model_metadata.json','local_admission_findings.json','audit_receipt.json'):
        text=(DATA/filename).read_text()
        for item in forbidden:assert item not in text,(filename,item)
    manifest=DATA/'manifest.json'
    if manifest.exists():
        for name,h in json.loads(manifest.read_text())['artifacts'].items():assert digest(DATA/name)==h,name
        for name,h in json.loads((DATA/'release_checksums.json').read_text()).items():assert digest(ROOT/name)==h,name
    print('PASS: 17 routes; prior 15 unchanged; 400 local first-attempt timings; 340 category cells; PNG provenance; purple local hosting; private-field exclusions; exact docs mirror.')
    return s


if __name__=='__main__':validate()
