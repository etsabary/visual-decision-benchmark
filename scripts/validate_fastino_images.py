"""Offline public checks for 15 image models; never loads keys or credentials."""
from collections import Counter
import base64
import csv
from decimal import Decimal
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import statistics
from urllib.parse import urlsplit

from repo_layout import ROOT,repo_file
from benchmark import rows,canonical
from analyze_native_images import percentile

DATA=ROOT/'results/releases/fastino_2026-10-23'
OLD=repo_file('native_images_2026-10-20')
MID='fastino_glide'


def digest(path):return sha256(path.read_bytes()).hexdigest()


class Page(HTMLParser):
    def __init__(self):super().__init__();self.cells=[];self.links=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='td' and 'data-family' in a:self.cells.append(a)
        self.links.extend(v for k,v in attrs if k in ('href','src'))
    def handle_data(self,text):self.text.append(text)


def validate():
    s=json.loads((DATA/'summary.json').read_text());old=json.loads((OLD/'summary.json').read_text())
    manifest=json.loads((DATA/'manifest.json').read_text())
    assert len(s['models'])==len(s['rank_order'])==s['decision_models_ranked']==15
    assert s['rank_order'][:3]==['amos_large',MID,'d3_turbo']
    assert all(s['models'][mid]==m for mid,m in old['models'].items()),'Earlier model changed'
    assert s['exclusions']==old['exclusions']
    assert s['prior_summary_sha256']==manifest['prior_summary_sha256']==digest(OLD/'summary.json')
    assert manifest['bank_sha256']==digest(ROOT/'data/questions.jsonl')
    for name,h in manifest['artifacts'].items():assert digest(DATA/name)==h,name
    captured=json.loads((DATA/'model_manifests.json').read_text())[MID]
    for name,h in captured['software'].items():assert digest(DATA/'captured_software'/(name+'.snapshot'))==h,name
    records=rows(DATA/'attempts.jsonl');old_records=rows(OLD/'attempts.jsonl')
    assert records[:len(old_records)]==old_records
    rr=[r for r in records if r['model_id']==MID]
    assert len(rr)==len({r['candidate_id'] for r in rr})==200
    questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    assets={a['asset_id']:a for a in rows(ROOT/'data/assets.jsonl')}
    plan=captured['manifest']['request_plan'];tasks={p['candidate_id']:p for p in plan}
    assert set(tasks)==set(questions)==set(r['candidate_id'] for r in rr)
    reproduced=withheld=0
    for row in rr:
        assert row['attempt']==1 and row['status']=='ok' and row['model_returned']=='glide_v2'
        assert row['reported_cost_usd'] is None and row['cost_source']=='usage_times_published_tariff'
        assert row['usage']['output_tokens']==0 and row['response_headers']['x-fastino-data-retention']=='not-stored'
        assert row['probabilities_valid']
        assert all(row.get(k)==v for k,v in tasks[row['candidate_id']].items() if k not in ('wave','item_id'))
        assert not {'correct_option_id','correct_first','correct_eventual','raw_response','api_key','account_id'}&set(row)
        q=questions[row['candidate_id']]
        assert row['choice'] in {o['id'] for o in q['options']}
        assert row['image_sha256']==[assets[a]['sha256'] for a in q['asset_ids']]
        assert Decimal(str(row['accounted_cost_usd']))==Decimal(row['usage']['input_tokens'])*Decimal('.00000004')
        if any(assets[aid]['path'] is None for aid in q['asset_ids']):withheld+=1;continue
        parts=[]
        for aid in q['asset_ids']:
            asset=assets[aid];raw=repo_file(asset['path']).read_bytes();assert sha256(raw).hexdigest()==asset['sha256']
            parts.append(dict(type='image_url',image_url=dict(url='data:'+asset['mime']+';base64,'+base64.b64encode(raw).decode('ascii'))))
        body=dict(model='fastino/GLiDE',store=False,state=parts,questions=dict(decision=dict(type='choice',
            instructions=q['question']+'\n\nRules: '+q['rules'],criteria={o['id']:o['text'] for o in q['options']})))
        wire=canonical(body)
        assert sha256(wire).hexdigest()==row['request_payload_sha256'] and len(wire)==row['request_body_bytes']
        reproduced+=1
    f=s['models'][MID]
    assert f['correct']==158 and f['accuracy']==.79 and f['n']==f['usable']==200 and f['retries']==0
    assert f['correct']==sum(v['correct'] for v in f['families'].values())==sum(v['correct'] for v in f['subsets'].values())
    times=[r['latency_ms'] for r in rr]
    assert f['median_ms']==statistics.median(times)<2000 and f['p95_ms']==percentile(times,.95)
    assert abs(f['mean_ms']-statistics.mean(times))<1e-8
    assert sum((Decimal(str(r['accounted_cost_usd'])) for r in rr),Decimal(0))==Decimal('0.00767264')
    assert Decimal(f['core_cost_per_1000_known_usd'])==Decimal('0.0383632')
    with (DATA/'family_scores.csv').open() as handle:cells=list(csv.DictReader(handle))
    assert len(cells)==300 and len({(c['model_id'],c['family_id']) for c in cells})==300
    for c in cells:assert int(c['correct'])==s['models'][c['model_id']]['families'][c['family_id']]['correct']
    page=Page();page.feed(repo_file('report.html').read_text())
    assert len(page.cells)==300
    for c in page.cells:assert int(c['data-correct'])==s['models'][c['data-model-id']]['families'][c['data-family']]['correct']
    text=' '.join(page.text)
    for phrase in ('158/200','159/200','second','glide_v2','one answer','Cost / 1,000 is a normalization'):
        assert phrase.lower() in text.lower(),phrase
    from build_image_site import build
    build()
    for target in page.links:
        url=urlsplit(target)
        if not url.scheme and not url.netloc and url.path:assert (ROOT/'_site'/url.path).exists(),target
    seal=DATA/'release_checksums.json'
    if seal.exists():
        for name,h in json.loads(seal.read_text()).items():assert digest(ROOT/name)==h,name
    print(json.dumps(dict(status='PASS',models=15,category_cells=300,fastino_payloads_reconstructed=reproduced,
        withheld_payloads=withheld,prior_14_unchanged=True,core_cost='0.00767264',cost_basis='usage_times_tariff'),indent=2))
    return s


if __name__=='__main__':validate()
