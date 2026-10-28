"""Public offline checks for Celeris and the unchanged 18-route history."""
from october27_history import previous as historical_path
from collections import Counter
import csv
from decimal import Decimal
import json
import math
import statistics
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

from benchmark import rows
from repo_layout import ROOT
import publish_celeris_images_2026_10_26 as b
from validate_llm_image_reference_2026_10_25 import Page,percentile


def validate():
    s=json.loads((b.DEST/'summary.json').read_text());old=json.loads((b.OLD/'summary.json').read_text())
    assert len(s['models'])==len(s['rank_order'])==s['complete_routes']==19
    assert (s['hosted_model_count'],s['local_model_count'],s['complete_llm_reference_count'])==(16,2,1)
    assert s['complete_first_attempt_cases']==3800 and s['partial_llm_first_attempt_cases']==60
    assert s['decision_models_ranked']==len(s['decision_model_ids'])==18
    assert set(s['models'])-set(old['models'])=={b.MID}
    assert all(s['models'][mid]==m for mid,m in old['models'].items()),'Previous model measurement changed'
    assert all(s[k]==old[k] for k in ('llm_speed_stops','selection_basis','exclusions','local_model_ids','reference_model_ids'))
    assert s['prior_summary_sha256']==b.digest(b.OLD/'summary.json')
    assert s['rank_order']==sorted(s['models'],key=lambda mid:(-s['models'][mid]['correct'],s['models'][mid]['median_ms']))
    assert s['rank_order'].index(b.MID)==8
    for filename in ('image_variant_manifest.json','local_model_metadata.json','local_timing_evidence.jsonl',
        'local_admission_findings.json','llm_speed_stops.json','speed_stops.csv','llm_model_metadata.json',
        'selection_basis.json','llm_timing_evidence.jsonl','llm_execution_protocol.json','execution_source_hashes.json'):
        assert (b.DEST/filename).read_bytes()==(b.OLD/filename).read_bytes(),filename
    rr=rows(b.DEST/'celeris_timing_evidence.jsonl');assert len(rr)==len({r['candidate_id'] for r in rr})==200
    assert all(set(r)==b.FIELDS for r in rr)
    protocol=json.loads((b.DEST/'celeris_execution_protocol.json').read_text())
    assert protocol['model']==b.MODEL and protocol['concurrency']==1 and protocol['scored_retries']==0
    assert protocol['bank_sha256']==b.digest(ROOT/'data/questions.jsonl')
    assert protocol['max_soft_tokens']==1120 and protocol['explanations'] is False
    assert [r['candidate_id'] for r in rr]==protocol['question_order']
    assert protocol['question_order']==json.loads((b.DEST/'llm_execution_protocol.json').read_text())['question_order']
    questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    images=json.loads((b.DEST/'image_variant_manifest.json').read_text())['assets']
    for i,r in enumerate(rr,1):
        q=questions[r['candidate_id']]
        assert r['request_index']==i and r['attempt']==1 and r['status']=='ok'
        assert r['model_id']==b.MID and r['model_requested']==r['model_returned']==b.MODEL
        assert r['family_id']==q['family_id'] and r['question_sha256']==b.packet_digest(q)
        assert r['image_sha256']==[images[aid]['sha256'] for aid in q['asset_ids']]
        assert all(len(r[k])==64 for k in ('question_sha256','request_payload_sha256','response_sha256'))
        assert r['output_tokens']==0 and type(r['input_tokens']) is int and r['input_tokens']>0
        assert r['state_truncated_reported'] is None
        assert math.isfinite(r['latency_ms']) and r['latency_ms']>0
        assert Decimal(r['estimated_cost_usd'])==Decimal(r['input_tokens'])*Decimal('.00000004')
    m=s['models'][b.MID];times=[r['latency_ms'] for r in rr]
    assert (m['n'],m['correct'],m['usable'],m['accuracy'],m['retries'])==(200,143,200,.715,0)
    assert m['mean_ms']==statistics.mean(times) and m['median_ms']==statistics.median(times)
    assert math.isclose(m['p95_ms'],percentile(times),rel_tol=1e-12)
    assert max(statistics.median(times[:i]) for i in range(20,201))<=2000
    assert sum(r['input_tokens'] for r in rr)==m['reported_input_tokens']==293791
    cost=sum((Decimal(r['estimated_cost_usd']) for r in rr),Decimal(0))
    assert cost==Decimal(m['usage_based_core_cost_usd'])==Decimal('.01175164')
    assert Decimal(m['core_cost_per_1000_known_usd'])==cost*5==Decimal('.05875820')
    assert m['cost_source']=='usage_times_published_tariff' and b.money(m).startswith('~$')
    assert m['core_cost']['reported_records']==0 and m['core_cost']['missing_api_records']==200
    assert m['admission_probes']==5 and Decimal(m['probe_cost_usd'])==Decimal('.00042344')
    assert Counter(r['family_id'] for r in rr)=={f'V{i:02}':10 for i in range(1,21)}
    assert sum(v['correct'] for v in m['families'].values())==143 and all(v['n']==v['usable']==10 for v in m['families'].values())
    with (b.DEST/'family_scores.csv').open() as stream:cells=list(csv.DictReader(stream))
    assert len(cells)==len({(r['model_id'],r['family_id']) for r in cells})==380
    for c in cells:assert int(c['correct'])==s['models'][c['model_id']]['families'][c['family_id']]['correct']
    from build_image_site import build
    build()
    for path,base in ((ROOT/'docs/report.html',ROOT/'_site'),(b.DEST/'report.html',ROOT/'_site'/b.NAME)):
        text=historical_path(path).read_text();page=Page();page.feed(text)
        assert page.rows==s['rank_order'] and len(page.cells)==380
        assert page.reference_rows==['reference_sol'] and set(page.local_rows)==set(s['local_model_ids'])
        assert set(page.stops)=={'reference_sonnet','reference_opus5','reference_qwen'}
        for c in page.cells:assert int(c['data-correct'])==s['models'][c['data-model-id']]['families'][c['data-family']]['correct']
        for phrase in ('Celeris 1.1 Decision','143/200','71.5%','585 ms','1120','not monetary receipts','19 complete routes','1,143/1,342','SPEED STOP'):
            assert phrase in text,(path,phrase)
        for link in page.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            if u.path:assert (base/u.path).exists(),(path,link)
            elif u.fragment:assert u.fragment in page.ids,(path,link)
    meta=json.loads((b.DEST/'celeris_model_metadata.json').read_text())
    assert meta['selected_catalog']['id']==b.MODEL and meta['catalog_unchanged_at_end'] and meta['max_soft_tokens']==1120
    assert meta['pricing']['input_usd_per_million']=='0.04'
    receipt=json.loads((b.DEST/'audit_receipt.json').read_text())
    assert (receipt['correct'],receipt['payloads_rebuilt'],receipt['png_hashes_verified'],receipt['publication_inference_calls'])==(143,200,227,0)
    svg=(b.DEST/'overview.svg').read_text()
    assert all(t in svg for t in ('Celeris 1.1 Decision','#16728c','#7c3aed','fill-opacity: 0.6','19 complete routes'))
    assert ET.parse(ROOT/'docs/sitemap.xml').getroot().find('{*}url/{*}loc').text==b.SITE
    for p in b.DEST.iterdir():
        if p.is_file():assert p.read_bytes()==(ROOT/'docs'/b.NAME/p.name).read_bytes(),p
        if p.suffix not in ('.json','.jsonl','.csv','.md','.html','.svg'):continue
        text=p.read_text()
        banned=('192.168.','127.0.0.1','/Users/','"probabilities":','"correct_option_id":','Authorization: Bearer')
        if p.name!='llm_model_metadata.json':banned+=('"choice":',)
        for token in banned:assert token not in text,(p.name,token)
    if (b.DEST/'manifest.json').exists():
        for name,h in json.loads((b.DEST/'manifest.json').read_text())['artifacts'].items():assert b.digest(b.DEST/name)==h,name
        for name,h in json.loads((b.DEST/'release_checksums.json').read_text()).items():assert b.digest(historical_path(ROOT/name))==h,name
    from validate_llm_image_reference_2026_10_25 import validate as historical
    historical()
    print('PASS: Celeris143/200;19 complete routes;18 prior records exact;200 answer-free timing rows;380 category cells;cost/PNG/mirror/privacy/seals checked.')
    return s


if __name__=='__main__':validate()
