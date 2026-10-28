"""Public checks for the 21-route image release; no credentials or inference."""
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
import csv,json,math,statistics
from urllib.parse import urlsplit
from benchmark import rows
from validate_llm_image_reference_2026_10_25 import Page,percentile
import publish_native_images_2026_10_27 as b

def historical_oct28(path):
    path=Path(path)
    archive=b.ROOT/'results/archives/presentation_before_m2_screens_2026-10-28'
    manifest=archive/'manifest.json'
    if not manifest.exists():return path
    entry=json.loads(manifest.read_text())['files'].get(path.relative_to(b.ROOT).as_posix())
    if not entry:return path
    saved=archive/entry['path']
    assert b.digest(saved)==entry['sha256'],path
    return saved

def validate():
    s=json.loads((b.DEST/'summary.json').read_text());old=json.loads((b.OLD/'summary.json').read_text())
    assert len(s['models'])==s['complete_routes']==21 and s['complete_first_attempt_cases']==4200
    assert (s['hosted_model_count'],s['local_model_count'],s['complete_llm_reference_count'])==(18,2,1)
    assert all(s['models'][mid]==m for mid,m in old['models'].items())
    assert set(s['models'])-set(old['models'])=={'d3_ultra','liquid11_decision'}
    assert all(s[k]==old[k] for k in ('llm_speed_stops','selection_basis','exclusions','local_model_ids','reference_model_ids'))
    assert s['rank_order']==sorted(s['models'],key=lambda m:(-s['models'][m]['correct'],s['models'][m]['median_ms']))
    assert s['rank_order'][:2]==old['rank_order'][:2]
    rr=rows(b.DEST/'october27_timing_evidence.jsonl');assert len(rr)==400 and all(set(r)==b.FIELDS for r in rr)
    qq={q['candidate_id']:q for q in rows(b.ROOT/'data/questions.jsonl')}
    assets=json.loads((b.DEST/'october27_original_asset_manifest.json').read_text())['assets']
    originals={a['asset_id']:a for a in rows(b.ROOT/'data/assets.jsonl')}
    assert len(assets)==227 and all(a['sha256']==originals[aid]['sha256'] for aid,a in assets.items())
    protocols=json.loads((b.DEST/'october27_execution_protocol.json').read_text());grouped=defaultdict(list)
    for r in rr:
        grouped[r['model_id']].append(r);q=qq[r['candidate_id']]
        assert r['question_sha256']==b.evidence.packet(q) and r['family_id']==q['family_id']
        assert r['image_sha256']==[assets[aid]['sha256'] for aid in q['asset_ids']]
        assert r['status']=='ok' and r['attempt']==1 and r['output_tokens']==0
        assert type(r['input_tokens']) is int and r['input_tokens']>0
        assert math.isfinite(r['latency_ms']) and r['latency_ms']>0
    for mid,correct in [('d3_ultra',148),('liquid11_decision',144)]:
        m=s['models'][mid];a=grouped[mid];private='d3_ultra' if mid=='d3_ultra' else 'liquid11'
        p=protocols[mid];assert p['question_order']==[r['candidate_id'] for r in a]
        assert len(a)==len({r['candidate_id'] for r in a})==200
        assert m['correct']==correct and m['usable']==m['n']==200 and m['retries']==0
        assert m['date']=='2026-10-27' and m['admission_probes']==5
        times=[r['latency_ms'] for r in a]
        assert m['median_ms']==statistics.median(times) and math.isclose(m['mean_ms'],statistics.mean(times),rel_tol=1e-12)
        assert math.isclose(m['p95_ms'],percentile(times),rel_tol=1e-12)
        assert max(statistics.median(times[:i]) for i in range(20,201))<=2000
        assert sum(v['correct'] for v in m['families'].values())==correct and all(v['n']==v['usable']==10 for v in m['families'].values())
        assert Counter(r['family_id'] for r in a)=={f'V{i:02}':10 for i in range(1,21)}
        assert p['question_bank_sha256']==b.digest(b.ROOT/'data/questions.jsonl') and p['scored_retries']==0
        assert p['image_variant'].startswith('Original reviewed')
    cost=sum((Decimal(str(r['reported_cost_usd'])) for r in grouped['liquid11_decision']),Decimal(0))
    m=s['models']['liquid11_decision']
    assert cost==Decimal('.00604404')==Decimal(m['core_cost']['known_api_usd'])
    assert cost*5==Decimal(m['core_cost_per_1000_known_usd']) and m['core_cost']['reported_records']==200
    assert s['models']['d3_ultra']['public_free_access'] and all(r['reported_cost_usd'] is None for r in grouped['d3_ultra'])
    with (b.DEST/'family_scores.csv').open() as f:cells=list(csv.DictReader(f))
    assert len(cells)==420
    for c in cells:assert int(c['correct'])==s['models'][c['model_id']]['families'][c['family_id']]['correct']
    from build_image_site import build
    build()
    for path,base in [(b.ROOT/'docs/report.html',b.ROOT/'_site'),(b.DEST/'report.html',b.ROOT/'_site'/b.NAME)]:
        text=path.read_text();page=Page();page.feed(text)
        assert page.rows==s['rank_order'] and len(page.cells)==420
        assert page.reference_rows==['reference_sol'] and set(page.local_rows)==set(s['local_model_ids'])
        assert set(page.stops)=={'reference_sonnet','reference_opus5','reference_qwen'}
        for c in page.cells:assert int(c['data-correct'])==s['models'][c['data-model-id']]['families'][c['data-family']]['correct']
        for phrase in ('D3 Ultra','Liquid d1.1','148/200','144/200','21 complete routes','0.00604404','SPEED STOP'):assert phrase in text,phrase
        for link in page.links:
            u=urlsplit(link)
            if u.scheme or u.netloc:continue
            if u.path:assert (base/u.path).exists(),(path,link)
            elif u.fragment:assert u.fragment in page.ids,(path,link)
    svg=(b.DEST/'overview.svg').read_text()
    assert all(x in svg for x in ('D3 Ultra','Liquid d1.1','#16728c','#7c3aed','fill-opacity: 0.6','21 complete routes'))
    for p in b.DEST.iterdir():
        if p.is_file():assert p.read_bytes()==(b.ROOT/'docs'/b.NAME/p.name).read_bytes(),p.name
        if p.suffix in ('.json','.jsonl','.csv','.md','.html','.svg'):
            t=p.read_text()
            for token in ('192.168.','/Users/','"correct_option_id":','"probabilities":','Authorization: Bearer'):assert token not in t,(p.name,token)
            if p.name!='llm_model_metadata.json':assert '"choice":' not in t,p.name
    if (b.DEST/'manifest.json').exists():
        for name,h in json.loads((b.DEST/'manifest.json').read_text())['artifacts'].items():assert b.digest(b.DEST/name)==h,name
        for name,h in json.loads((b.DEST/'release_checksums.json').read_text()).items():assert b.digest(historical_oct28(b.ROOT/name))==h,name
    from validate_celeris_images_2026_10_26 import validate as historical
    historical()
    print('PASS:21 image routes;400 new attempts;420 category cells;19 earlier records exact')
    return s

if __name__=='__main__':validate()
