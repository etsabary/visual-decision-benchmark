"""Offline public checks for Sol and three explicitly partial LLM speed stops."""
from collections import Counter
import csv
from decimal import Decimal
from hashlib import sha256
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import statistics
from urllib.parse import urlsplit

from benchmark import rows
from repo_layout import ROOT

NAME='llm_reference_2026-10-25'
DATA=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/local_images_2026-10-25'
EXPECTED={'reference_sonnet':(18,3150),'reference_opus5':(16,2628),'reference_qwen':(13,2837)}
FIELDS={'model_id','model_requested','request_index','candidate_id','family_id','attempt','status','latency_ms',
        'request_payload_sha256','request_body_bytes','image_sha256','reported_reasoning_tokens','reasoning_text_present',
        'reasoning_verification','reported_cost_usd','reported_hypercredits','model_returned','provider','image_variant'}


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def percentile(xs):
    xs=sorted(xs);p=(len(xs)-1)*.95;a,b=math.floor(p),math.ceil(p)
    return xs[a]+(xs[b]-xs[a])*(p-a)


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.rows=[];self.reference_rows=[];self.local_rows=[];self.cells=[];self.stops=[];self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='tr' and 'data-summary-model' in a:
            self.rows.append(a['data-summary-model'])
            if a.get('class')=='llm-reference':self.reference_rows.append(a['data-summary-model'])
            if a.get('class')=='local-model':self.local_rows.append(a['data-summary-model'])
        if tag=='tr' and 'data-speed-stop' in a:self.stops.append(a['data-speed-stop'])
        if tag=='td' and 'data-family' in a:self.cells.append(a)
        self.links.extend(v for k,v in attrs if k in ('href','src'))
        if 'id' in a:self.ids.add(a['id'])


def validate():
    s=json.loads((DATA/'summary.json').read_text());old=json.loads((OLD/'summary.json').read_text())
    assert len(s['models'])==len(s['rank_order'])==s['complete_routes']==18
    assert s['reference_model_ids']==['reference_sol'] and s['complete_llm_reference_count']==1 and s['llm_references_tested']==4
    assert all(s['models'][mid]==m for mid,m in old['models'].items()),'An earlier complete model record changed'
    assert s['exclusions']==old['exclusions'] and s['prior_summary_sha256']==digest(OLD/'summary.json')
    assert s['rank_order']==sorted(s['models'],key=lambda mid:(-s['models'][mid]['correct'],s['models'][mid]['median_ms']))
    assert s['complete_first_attempt_cases']==3600 and s['partial_llm_first_attempt_cases']==60
    stops=json.loads((DATA/'llm_speed_stops.json').read_text());assert stops==s['llm_speed_stops']
    assert {m['model_id'] for m in stops}==set(EXPECTED)
    rr=rows(DATA/'llm_timing_evidence.jsonl');assert len(rr)==260 and all(set(r)==FIELDS for r in rr)
    protocol=json.loads((DATA/'llm_execution_protocol.json').read_text());questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    assert protocol['question_sha256']==digest(ROOT/'data/questions.jsonl')
    assert protocol['scored_retries']==0 and protocol['concurrency']=={'global':2,'per_model':1}
    variant=json.loads((DATA/'image_variant_manifest.json').read_text())
    assert digest(DATA/'image_variant_manifest.json')==digest(OLD/'image_variant_manifest.json')
    for r in rr:
        assert r['status']=='ok' and r['attempt']==1 and not r['reasoning_text_present'] and r['latency_ms']>0
        assert r['family_id']==questions[r['candidate_id']]['family_id'] and len(r['request_payload_sha256'])==64
        assert r['image_sha256']==[variant['assets'][aid]['sha256'] for aid in questions[r['candidate_id']]['asset_ids']]
        if r['model_id']=='reference_qwen':assert r['reported_reasoning_tokens'] is None and r['reasoning_verification']=='requested_none_catalog_supported_no_token_telemetry'
        else:assert r['reported_reasoning_tokens']==0 and not isinstance(r['reported_reasoning_tokens'],bool) and r['reasoning_verification']=='explicit_reported_zero'
    for mid in ['reference_sol',*EXPECTED]:
        records=[r for r in rr if r['model_id']==mid];n=200 if mid=='reference_sol' else 20
        assert len(records)==len({r['candidate_id'] for r in records})==n
        assert [r['candidate_id'] for r in records]==protocol['question_order'][:n]
        assert [r['request_index'] for r in records]==list(range(1,n+1))
        m=s['models'][mid] if mid=='reference_sol' else next(m for m in stops if m['model_id']==mid)
        times=[r['latency_ms'] for r in records]
        assert abs(m['mean_ms']-statistics.mean(times))<1e-8 and m['median_ms']==statistics.median(times) and abs(m['p95_ms']-percentile(times))<1e-8
        total=sum((Decimal(r['reported_cost_usd']) for r in records),Decimal(0))
        if mid=='reference_sol':
            assert m['n']==m['usable']==200 and m['correct']==147 and m['accuracy']==.735
            assert m['reported_reasoning_text']==0 and m['retries']==0
            assert max(statistics.median(times[:k]) for k in range(20,201))<=2000
            assert sum(v['correct'] for v in m['families'].values())==147
            assert Counter(r['family_id'] for r in records)=={f'V{i:02}':10 for i in range(1,21)}
            assert total==Decimal(m['core_cost']['known_api_usd'])==Decimal('.591634')
            assert Decimal(m['core_cost_per_1000_known_usd'])==total*5==Decimal('2.958170')
        else:
            assert not m['complete'] and not m['included_in_full_ranking'] and m['state']=='stopped_slow' and m['attempted']==m['usable']==20
            assert m['correct']==EXPECTED[mid][0] and round(m['median_ms'])==EXPECTED[mid][1] and m['median_ms']>2000
            assert m['accuracy']==m['correct']/20 and mid not in s['models'] and total==Decimal(m['cost']['known_usd'])
            assert 'core_cost_per_1000_known_usd' not in m
    basis=json.loads((DATA/'selection_basis.json').read_text());assert basis==s['selection_basis']
    refs=basis['models'];assert len(refs)==4 and refs['reference_sol']['correct']==1143 and refs['reference_sol']['n']==1342
    assert max(refs,key=lambda mid:refs[mid]['correct'])=='reference_sol'
    assert 'completed text comparison' in basis['claim'] and 'Four selected' in basis['scope']
    for filename in ('local_model_metadata.json','local_timing_evidence.jsonl','local_admission_findings.json'):
        assert digest(DATA/filename)==digest(OLD/filename),filename
    with (DATA/'family_scores.csv').open() as f:cells=list(csv.DictReader(f))
    assert len(cells)==len({(c['model_id'],c['family_id']) for c in cells})==360
    for c in cells:assert int(c['correct'])==s['models'][c['model_id']]['families'][c['family_id']]['correct']
    html=(ROOT/'docs/report.html').read_text();page=Page();page.feed(html)
    assert page.rows==s['rank_order'] and page.reference_rows==['reference_sol'] and set(page.local_rows)==set(s['local_model_ids'])
    assert len(page.cells)==360 and set(page.stops)==set(EXPECTED)
    for c in page.cells:assert int(c['data-correct'])==s['models'][c['data-model-id']]['families'][c['data-family']]['correct']
    for phrase in ('147/200','1,143/1,342','85.2%','four tested configurations','SPEED STOP','partial','zero reasoning tokens','rgba(242,212,107,.6)','#7c3aed','#16728c'):
        assert phrase in html,phrase
    from build_image_site import build
    build()
    for url in page.links:
        target=urlsplit(url)
        if target.scheme or target.netloc:continue
        if target.path:assert (ROOT/'_site'/target.path).exists(),url
        elif target.fragment:assert target.fragment in page.ids,url
    dated=Page();dated.feed((DATA/'report.html').read_text());assert dated.rows==s['rank_order'] and len(dated.cells)==360
    for url in dated.links:
        target=urlsplit(url)
        if not target.scheme and not target.netloc and target.path:assert (ROOT/'_site'/NAME/target.path).exists(),url
    for p in DATA.rglob('*'):
        if p.is_file():assert digest(ROOT/'docs'/NAME/p.relative_to(DATA))==digest(p),p
    svg=(DATA/'overview.svg').read_text();assert '#7c3aed' in svg and '#16728c' in svg and 'fill-opacity: 0.6' in svg
    for path in DATA.glob('*'):
        if path.suffix not in ('.json','.jsonl','.csv','.md','.html','.svg'):continue
        text=path.read_text()
        banned_fields=('192.168.','127.0.0.1','/Users/','"probabilities":','"correct_option_id":','Authorization: Bearer')
        if path.name!='llm_model_metadata.json':banned_fields+=('"choice":',)
        # The metadata file retains the requested JSON schema's property named
        # choice; actual output choices are excluded by the timing allowlist.
        for banned in banned_fields:
            assert banned not in text,(path.name,banned)
    if (DATA/'manifest.json').exists():
        for name,h in json.loads((DATA/'manifest.json').read_text())['artifacts'].items():assert digest(DATA/name)==h,name
        for name,h in json.loads((DATA/'release_checksums.json').read_text()).items():assert digest(ROOT/name)==h,name
    print('PASS: 18 complete routes;17 earlier records exact;Sol147/200;three20-case speed stops excluded;260 answer-free timing rows;360 category cells;scoped text-selection claim;colour/mirror/privacy/seal checks.')
    return s


if __name__=='__main__':validate()
