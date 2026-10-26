"""Offline, external-key image analysis and sanitized evidence export; no transport.

Run after every configured stream has completed or has an explicit stop receipt.
The executor never imports this file or receives the key loaded here.
"""
from repo_layout import repo_file, frozen_file
import argparse
from collections import Counter,defaultdict
from decimal import Decimal
from hashlib import sha256
import json
import math
from pathlib import Path
import statistics

import benchmark as bank
from image_models_2026_10_20 import MODELS,OUT,ROOT,QUESTION_HASH,SOFTWARE,config,digest,validate,parse,probes
from score import load_key

DEST=repo_file('native_images_2026-10-20', root=ROOT)
KEY_HASH='f62348cb73594146497858473fb01c4f78bb06a0649a857329ca47197688fe7c'
FAMILIES={
 'V01':('Attribute binding and set logic','Find objects that satisfy several visible properties at once.'),
 'V02':('Conditional counting','Count only the objects meeting the stated visual rule.'),
 'V03':('Spatial relationships','Apply left/right, above/below or relative-position constraints.'),
 'V04':('Connectivity and reachability','Follow connected paths or directed arrows between nodes.'),
 'V05':('Navigation and planning','Choose a feasible route under movement and obstacle rules.'),
 'V06':('Rotation and reflection','Recognize the result of a rotation or mirror transformation.'),
 'V07':('Geometry, folding and fit','Reason about shapes, folds, dimensions or what fits.'),
 'V08':('Visual rule application','Infer or apply a rule across symbols and pictured patterns.'),
 'V09':('Sequential state tracking','Track how successive visible actions change a state.'),
 'V10':('Constraint satisfaction','Find the arrangement satisfying all the stated restrictions.'),
 'V11':('Flowcharts and decision trees','Follow conditional branches to their final outcome.'),
 'V12':('Causal and counterfactual reasoning','Determine what changes when a pictured condition is altered.'),
 'V13':('Charts and quantitative comparisons','Read plotted values and compare or calculate the required quantity.'),
 'V14':('Document reconciliation','Combine entries across forms, receipts or tables and apply a rule.'),
 'V15':('Interface state decisions','Choose an action or identify a state from a screenshot.'),
 'V16':('Inspection against a reference','Compare an object or scene against a supplied reference.'),
 'V17':('Matching across images','Identify a corresponding object across two or three images.'),
 'V18':('Image and text consistency','Check whether a written claim agrees with the visible evidence.'),
 'V19':('Perspective and knowledge tracking','Apply line-of-sight constraints or track what an observer has seen.'),
 'V20':('Insufficient evidence','Recognize when the image cannot determine the requested answer.'),
}
LEGACY={'typesafe/jev-1.14':('jev114','Jev 1.14'),
        'openai/gpt-6-luna-decisions':('luna_decisions','Luna 6 Decisions')}

def dump(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def jsonl(path,values):
    Path(path).write_text(''.join(json.dumps(v,ensure_ascii=False,allow_nan=False)+'\n' for v in values))

def percentile(values,p):
    a=sorted(values)
    if not a:return None
    i=(len(a)-1)*p;lo=math.floor(i);hi=math.ceil(i)
    return a[lo]+(a[hi]-a[lo])*(i-lo)

def wilson(k,n):
    if not n:return [None,None]
    z=1.959963984540054;p=k/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]

def money(records):
    known=[Decimal(str(r['reported_cost_usd'])) for r in records if r.get('reported_cost_usd') is not None]
    accounted=[Decimal(str(r['accounted_cost_usd'])) for r in records if r.get('accounted_cost_usd') is not None]
    return dict(known_api_usd=str(sum(known,Decimal(0))),reported_records=len(known),
                missing_api_records=len(records)-len(known),accounted_usd=str(sum(accounted,Decimal(0))))

def summarize(records,key,questions,provenance):
    first=sorted((r for r in records if r['attempt']==1),key=lambda r:r['request_index'])
    groups=defaultdict(list)
    for r in records:groups[r['candidate_id']].append(r)
    assert len(first)==len(groups)==len({r['candidate_id'] for r in first})
    correct=sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in first)
    usable=sum(r['status']=='ok' for r in first)
    late=[r['latency_ms'] for r in first]
    result=dict(n=len(first),correct=correct,accuracy=correct/len(first) if first else None,
        usable=usable,accuracy_usable=correct/usable if usable else None,wilson95=wilson(correct,len(first)),
        mean_ms=statistics.mean(late) if late else None,median_ms=statistics.median(late) if late else None,
        p95_ms=percentile(late,.95),status_counts=dict(Counter(r['status'] for r in first)),
        retries=len(records)-len(first),core_cost=money(records),first_cost=money(first),
        probabilities_invalid=sum(r['status']=='ok' and not r.get('probabilities_valid',False) for r in first),
        eventual_correct=sum(g[-1]['status']=='ok' and g[-1]['choice']==key[qid] for qid,g in groups.items()),
        eventual_usable=sum(g[-1]['status']=='ok' for g in groups.values()),
        window=dict(first=first[0]['started']['toronto'],last=first[-1]['completed']['toronto']) if first else {},
        identities=sorted({(r.get('model_returned'),r.get('provider')) for r in first if r['status']=='ok'},key=str),
        reported_output_tokens=sum(r.get('usage',{}).get('output_tokens') or 0 for r in first),
        reported_reasoning_text=sum(bool(r.get('reasoning_text_present')) for r in first))
    result['families']={}
    for fid in FAMILIES:
        rr=[r for r in first if questions[r['candidate_id']]['family_id']==fid]
        result['families'][fid]=dict(n=len(rr),correct=sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in rr),
            usable=sum(r['status']=='ok' for r in rr))
    result['subsets']={}
    for subset in ('perception_control','reasoning_and_grounded_decision'):
        rr=[r for r in first if provenance[r['candidate_id']]['analysis_subset']==subset]
        result['subsets'][subset]=dict(n=len(rr),correct=sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in rr))
    result['confidence']={}
    for cutoff in (.5,.8,.9,.95,.99,1.):
        rr=[r for r in first if r['status']=='ok' and type(r.get('confidence')) in (float,int) and cutoff<=r['confidence']<=1]
        n=len(rr);k=sum(r['choice']==key[r['candidate_id']] for r in rr)
        result['confidence'][str(cutoff)]=dict(retained=n,correct=k,accuracy=k/n if n else None,coverage=n/len(first) if first else None)
    return result

PUBLIC_FIELDS=('request_index','attempt','candidate_id','family_id','model_id','model_requested',
    'model_returned','provider','request_payload_sha256','request_body_bytes','image_sha256','image_count',
    'semantic_input_sha256','http_status','headers_latency_ms','latency_ms','started','completed','status','choice',
    'probabilities','probabilities_valid','confidence','reported_cost_usd','accounted_cost_usd','cost_source',
    'reported_output_tokens','reasoning_text_present')

def sanitized(r):
    result={k:r[k] for k in PUBLIC_FIELDS if k in r}
    result['usage']={k:v for k,v in r.get('usage',{}).items() if k in ('input_tokens','output_tokens','cost','cached_tokens','cache_write_tokens')}
    error=r.get('raw_response',{}).get('error')
    if error:result['provider_error']={k:error[k] for k in ('code','message','type') if k in error} if isinstance(error,dict) else str(error)
    return result

def build(key_path):
    assert digest(key_path)==KEY_HASH,'Reference differs from the original frozen October15 manifest'
    key=load_key(key_path);questions={r['candidate_id']:r for r in bank.rows(repo_file('data/questions.jsonl', root=ROOT))}
    provenance={r['candidate_id']:r for r in bank.rows(repo_file('data/provenance.jsonl', root=ROOT))}
    assert set(key)==set(questions) and digest(repo_file('data/questions.jsonl', root=ROOT))==QUESTION_HASH
    DEST.mkdir(exist_ok=True);all_records={};scores={};exclusions=[];export=[];probe_export=[];manifests={}
    for mid in MODELS:
        out=OUT/mid;cfg=config(mid)
        if (out/'exclusion.json').exists():
            exclusions.append({'model_id':mid,'label':cfg['label'],'model_requested':cfg['model'],
                'reason':'Current pinned image route rejects image input','n':0,
                'receipt':json.loads((out/'exclusion.json').read_text())})
        else:
            assert (out/'completion.json').exists() or (out/'stop_receipt.json').exists(), 'Not settled: '+mid
            records,_=validate(mid);s=summarize(records,key,questions,provenance)
            s.update(model_id=mid,label=cfg['label'],model_requested=cfg['model'],route=cfg['host']+cfg['path'],
                date='2026-10-20',reused=False,public_free_access=cfg['free'],complete=s['n']==200)
            s['core_cost_per_1000_known_usd']=str(Decimal(s['core_cost']['known_api_usd'])*Decimal(1000)/Decimal(s['n']))
            if (out/'stop_receipt.json').exists():
                exclusions.append(dict(model_id=mid,label=cfg['label'],reason=json.loads((out/'stop_receipt.json').read_text())['reason'],
                    partial=s,receipt=json.loads((out/'stop_receipt.json').read_text()),n=s['n']))
            else:
                assert s['median_ms']<=2000;scores[mid]=s;all_records[mid]=records
            export.extend(dict(source='new_2026-10-20',**sanitized(r)) for r in records)
            manifest=json.loads((out/'manifest.json').read_text())
            manifests[mid]={'manifest':manifest,'software':json.loads((out/'software.json').read_text()),
                'metadata':json.loads((out/'metadata.json').read_text()),'snapshot':json.loads((out/'snapshot.json').read_text()),
                'completion':json.loads((out/'completion.json').read_text()) if (out/'completion.json').exists() else None}
        for path in sorted(out.glob('probe_[12]*.json')):
            if path.name.endswith('_dispatch.json') or 'parser_review' in path.name:continue
            v=json.loads(path.read_text());r=v['response']
            probe_index=int(path.stem.split('_')[1])
            r.update(parse(r,{o['id'] for o in probes()[probe_index-1]['options']},mid))
            r.update(model_id=mid,model_requested=cfg['model'])
            probe_export.append(dict(probe_file=path.name,payload_sha256=v['payload_sha256'],**sanitized(r)))
    old=bank.rows(repo_file('data/attempts.jsonl', root=ROOT));old_summary=json.loads((repo_file('results/summary.json', root=ROOT)).read_text())
    rescored=bank.score(key)
    for model,(mid,label) in LEGACY.items():
        records=[dict(r,accounted_cost_usd=r.get('reported_cost_usd'),cost_source='api_reported' if r.get('reported_cost_usd') is not None else 'unreported') for r in old if r['model_requested']==model]
        s=summarize(records,key,questions,provenance)
        assert s['correct']==old_summary['models'][model]['correct_first']==rescored[model]['correct_first']
        assert s['usable']==old_summary['models'][model]['usable_first']
        assert all(s['families'][f]['correct']==old_summary['models'][model]['groups']['family_id'][f]['correct_first'] for f in FAMILIES)
        assert abs(s['median_ms']-old_summary['models'][model]['latency_first_all_ms']['median'])<1e-6
        s.update(model_id=mid,label=label,model_requested=model,route='openrouter.ai/api/alpha/decisions',date='2026-10-15',
            reused=True,public_free_access=False,complete=True)
        s['core_cost_per_1000_known_usd']=str(Decimal(s['core_cost']['known_api_usd'])*5)
        scores[mid]=s;all_records[mid]=records
    # Verify all original five scores, including the archived LLM references, against the unchanged key.
    for model,s in rescored.items():assert s['correct_first']==old_summary['models'][model]['correct_first']
    order=sorted(scores,key=lambda m:(-scores[m]['correct'],scores[m]['median_ms']))
    paired={};leader=order[0]
    for mid in order:
        a={r['candidate_id']:r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in all_records[leader] if r['attempt']==1}
        b={r['candidate_id']:r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in all_records[mid] if r['attempt']==1}
        assert set(a)==set(b)==set(key)
        x=sum(a[q] and not b[q] for q in key);y=sum(b[q] and not a[q] for q in key);n=x+y
        p=min(1,2*sum(math.comb(n,i) for i in range(min(x,y)+1))/2**n) if n else 1
        paired[mid]=dict(leader_only=x,other_only=y,both_correct=sum(a[q] and b[q] for q in key),
            neither_correct=sum(not a[q] and not b[q] for q in key),unadjusted_exact_mcnemar_p=p)
    result=dict(version='native-image-expansion-20261020-v1',questions=200,image_files=227,images_public=221,
        decision_models_reviewed=16,decision_models_ranked=len(scores),rank_order=order,models=scores,exclusions=exclusions,
        families={f:dict(name=n,description=d,n=10) for f,(n,d) in FAMILIES.items()},
        random_uniform_baseline=sum(1/len(q['options']) for q in questions.values())/200,
        reused_models=list(LEGACY),new_complete_models=len(scores)-2,
        original_llm_references={m:old_summary['models'][m] for m in bank.LLM_MODELS},
        leader_pairwise=paired,
        audit=dict(key_sha256=digest(key_path),question_sha256=QUESTION_HASH,all_five_original_scores_reproduced=True,
            no_key_or_item_correctness_in_public_packet=True,
            note='Scored offline against unchanged external key; this reproduces the reference, not an independent new key audit.'),
        probe_cost=money(probe_export),new_scored_cost=money(export),
        caveats=['October15 measurements reused, not contemporaneous October20 reruns.',
            'Tiny within-family samples of10; repeated source collections and task types can induce dependence despite distinct files and assigned scene groups.',
            'Public-image training exposure unknown; no holdout or architecture-level causal claim.',
            'Confidence thresholds explored after observing these results; not deployment calibration.',
            'Cost per1000 is a normalization of actual200, not1000 extra questions per model.'])
    dump(DEST/'summary.json',result);jsonl(DEST/'attempts.jsonl',export);jsonl(DEST/'compatibility_probes.jsonl',probe_export)
    dump(DEST/'model_manifests.json',manifests)
    dump(DEST/'audit_receipt.json',dict(**result['audit'],scored_first_attempts=sum(s['n'] for s in scores.values()),
        new_complete_first_attempts=200*(len(scores)-2),
        excluded_first_attempts=sum(e['n'] for e in exclusions),software={n:digest(repo_file(n, root=ROOT)) for n in SOFTWARE},
        original_attempts_sha256=digest(repo_file('data/attempts.jsonl', root=ROOT)),original_checksums_sha256=digest(repo_file('checksums.json', root=ROOT))))
    print(json.dumps({m:{k:scores[m][k] for k in ('correct','usable','median_ms','p95_ms','core_cost')} for m in order},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--answer-key',type=Path,required=True)
    build(p.parse_args().answer_key)
