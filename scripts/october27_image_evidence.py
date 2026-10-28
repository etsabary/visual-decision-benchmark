"""Offline publication reconciliation for D3 Ultra and Liquid d1.1 images."""
import base64
from collections import Counter
from copy import deepcopy
from decimal import Decimal
from hashlib import sha256
import json,math,statistics
from pathlib import Path
from score import load_key
from benchmark import canonical,rows

ROOT=Path(__file__).resolve().parents[1]
CAPTURE=ROOT.parent/'text-decision-hardening/runs/d3_ultra_liquid11_images_2026-10-27_224454'
OLD=ROOT/'results/releases/celeris_2026-10-26'
DEST=ROOT/'results/releases/native_updates_2026-10-27'
KEY_HASH='f62348cb73594146497858473fb01c4f78bb06a0649a857329ca47197688fe7c'
MODELS={'d3_ultra':('d3_ultra','D3 Ultra','vllm-sr/d3-ultra'),
        'liquid11':('liquid11_decision','Liquid d1.1','liquid/d1.1')}
FIELDS={'model_id','model_requested','model_returned','request_index','candidate_id','family_id','attempt','status','latency_ms',
        'question_sha256','request_payload_sha256','image_sha256','input_tokens','output_tokens','reported_cost_usd','cost_source','response_sha256'}
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def packet(v):return sha256(canonical(v)).hexdigest()

def payload(q,images,mid):
    urls=['data:'+mime+';base64,'+base64.b64encode(b).decode('ascii') for mime,b in images]
    question=dict(type='choice',instructions=q['question']+'\n\nRules: '+q['rules'],criteria={o['id']:o['text'] for o in q['options']})
    if mid=='d3_ultra':return dict(model=MODELS[mid][2],state='',images=urls,questions={'decision':question})
    return dict(model=MODELS[mid][2],state=[dict(type='image_url',image_url={'url':u}) for u in urls],questions={'decision':question},
        provider=dict(only=['liquid'],allow_fallbacks=False,require_parameters=True))

def load(key_path):
    assert digest(key_path)==KEY_HASH;gold=load_key(key_path)
    seal=json.loads((CAPTURE/'seal.json').read_text())
    for name,h in seal['files_sha256'].items():assert digest(CAPTURE/name)==h,name
    qq={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')};assert len(qq)==200 and set(qq)==set(gold)
    old=json.loads((OLD/'summary.json').read_text());s=deepcopy(old)
    inputs=ROOT.parent/'jev-1.14-comparison-benchmark/runs/visual_benchmark_curation_PRIVATE/codex_execution_2026-10-15/run_01/input_variant_manifest.json'
    assert digest(inputs)=='4ce82fcc59fd3238d638d2c2d0e5e54baca69a0e3877835f100eb9ef1f8c1fea'
    assets=json.loads(inputs.read_text())['assets'];public={a['asset_id']:a for a in rows(ROOT/'data/assets.jsonl')}
    image_bytes={}
    for aid,a in assets.items():
        b=Path(a['path']).read_bytes();assert sha256(b).hexdigest()==a['sha256']==public[aid]['sha256']
        image_bytes[aid]=(a['mime'],b)
    timings=[];metadata={};protocols={}
    for folder,(mid,label,model) in MODELS.items():
        p=CAPTURE/folder;m=json.loads((p/'manifest.json').read_text());report=json.loads((p/'final_report.json').read_text())
        audit=json.loads((p/'audit_receipt.json').read_text());aa=rows(p/'attempts.jsonl');dd=rows(p/'dispatches.jsonl')
        assert audit['status']=='PASS' and report['state']=='complete'
        assert len(aa)==len(dd)==len({a['item_id'] for a in aa})==200
        assert [a['item_id'] for a in aa]==m['question_order']
        assert m['question_bank_sha256']==digest(ROOT/'data/questions.jsonl')
        for i,(a,d) in enumerate(zip(aa,dd),1):
            q=qq[a['item_id']];raw=a['transport']['raw_response'];answer=raw['answers']['decision']
            assert a['request_index']==d['request_index']==i and a['attempt']==d['attempt']==1
            assert a['request_payload_sha256']==d['request_payload_sha256']==packet(payload(q,[image_bytes[aid] for aid in q['asset_ids']],folder))
            assert a['question_sha256']==packet(q) and a['image_sha256']==[assets[aid]['sha256'] for aid in q['asset_ids']]
            assert a['transport']['http_status']==200 and a['status']=='ok' and answer['type']=='choice'
            assert answer['choice']==a['choice'] and a['choice'] in [o['id'] for o in q['options']]
            assert raw['usage']['output_tokens']==0 and not any(raw.get(k) or answer.get(k) for k in ('reasoning','reasoning_content','explanation','content','text'))
            assert a['latency_ms']==a['transport']['latency_ms'] and a['family_id']==q['family_id']
            assert raw['model'] in ([model] if folder=='d3_ultra' else [model,'liquid/d1.1-20261027'])
            if folder=='liquid11':assert raw['provider']=='Liquid' and a['reported_cost_usd'] is not None
            timings.append(dict(model_id=mid,model_requested=model,model_returned=a['model_returned'],request_index=i,candidate_id=a['item_id'],
                family_id=q['family_id'],attempt=1,status='ok',latency_ms=a['latency_ms'],question_sha256=packet(q),
                request_payload_sha256=a['request_payload_sha256'],image_sha256=a['image_sha256'],input_tokens=a['usage']['input_tokens'],output_tokens=0,
                reported_cost_usd=a['reported_cost_usd'],cost_source=a['cost_source'],response_sha256=packet(raw)))
        hit=sum(a['choice']==gold[a['item_id']] for a in aa);assert hit==report['correct']
        fs={fid:dict(n=10,correct=sum(a['family_id']==fid and a['choice']==gold[a['item_id']] for a in aa),usable=10) for fid in old['families']}
        assert Counter(a['family_id'] for a in aa)=={fid:10 for fid in fs}
        assert all(v['correct']==report['families'][fid]['correct'] for fid,v in fs.items())
        xs=sorted(a['latency_ms'] for a in aa);pos=199*.95;lo=int(pos)
        tt=dict(mean_ms=statistics.mean(xs),median_ms=statistics.median(xs),p95_ms=xs[lo]+(xs[lo+1]-xs[lo])*(pos-lo))
        assert all(math.isclose(v,report[k],rel_tol=1e-12) for k,v in tt.items())
        assert max(statistics.median(a['latency_ms'] for a in aa[:i]) for i in range(20,201))<=2000
        probes=rows(p/'admission.jsonl');assert len(probes)==5 and [a['choice'] for a in probes]==['1','2','1','2','1']
        free=folder=='d3_ultra';cost=sum((Decimal(str(a['reported_cost_usd'])) for a in aa),Decimal(0)) if not free else Decimal(0)
        assert cost==Decimal(report['cost_known_usd'])
        v=dict(model_id=mid,label=label,model_requested=model,model_kind='hosted_decision',execution_location='hosted',
            route='Direct D3 native SystemOne; explicit Ultra' if free else 'OpenRouter native Decisions; pinned Liquid',date='2026-10-27',
            complete=True,reused=False,n=200,correct=hit,accuracy=hit/200,usable=200,accuracy_usable=hit/200,**tt,status_counts={'ok':200},retries=0,
            families=fs,public_free_access=free,cost_source='public_free_access_not_api_reported' if free else 'api_reported',
            core_cost=dict(known_api_usd=str(cost),reported_records=0 if free else 200,missing_api_records=200 if free else 0,accounted_usd=str(cost)),
            core_cost_per_1000_known_usd=str(cost*5),reported_input_tokens=report['input_tokens'],reported_output_tokens=0,reported_reasoning_text=0,
            image_variant='Original reviewed mixed PNG/JPEG',probe_cost_usd=report['admission_cost_usd'],admission_probes=5,
            reasoning_verification='Native choices; zero reported output tokens; internal computation not independently attested',
            processed_input_attestation='Exact delivered image bytes and packets; provider internal image preprocessing not attested')
        s['models'][mid]=v
        metadata[mid]=dict(requested_model=model,returned_identities=report['returned_identities'],selected_catalog=m['selected_catalog'],
            selected_catalog_unchanged=True,pricing_basis='Free public access at test time' if free else 'API-reported charges',
            source_evidence_sha256={n:digest(p/n) for n in ('manifest.json','attempts.jsonl','dispatches.jsonl','admission.jsonl','final_report.json','audit_receipt.json','catalog_start.json','catalog_end.json','executor_source.py.snapshot')})
        protocols[mid]=dict(model=model,question_order=m['question_order'],question_bank_sha256=m['question_bank_sha256'],
            image_manifest_sha256=m['image_manifest_sha256'],image_variant=m['image_variant'],scored_retries=0,admission_calls=5,
            concurrency=1,median_cutoff_ms=2000,pacing_seconds=.2,timing=m['timing'],content=m['content'],processing=m['processing'])
    s.update(version='native-image-updates-20261027-v1',updated_date_toronto='2026-10-27',complete_routes=21,hosted_model_count=18,
        decision_models_ranked=20,decision_models_reviewed=old['decision_models_reviewed']+2,
        decision_model_ids=[*old['decision_model_ids'],'d3_ultra','liquid11_decision'],complete_first_attempt_cases=4200,
        prior_summary_sha256=digest(OLD/'summary.json'),added_model_ids=['d3_ultra','liquid11_decision'])
    s['rank_order']=sorted(s['models'],key=lambda mid:(-s['models'][mid]['correct'],s['models'][mid]['median_ms']))
    assert all(s['models'][mid]==v for mid,v in old['models'].items())
    return s,timings,metadata,protocols,{aid:{k:a[k] for k in ('sha256','mime')} for aid,a in assets.items()}
