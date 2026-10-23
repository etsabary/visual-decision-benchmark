"""Answer-blind native-image expansion. No inference without --execute/--probe.

The executor reads only frozen public questions, an old blind image-path manifest,
and the exact image bytes. It never imports an answer key or a scoring module.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from contextlib import contextmanager
from datetime import datetime,timezone
from decimal import Decimal
from email.utils import parsedate_to_datetime
import fcntl
from hashlib import sha256
import base64
import http.client
import json
import math
import os
from pathlib import Path
import ssl
import statistics
import threading
import time
import urllib.request
from zoneinfo import ZoneInfo

import benchmark as bank

ROOT=Path(__file__).resolve().parent
TEXT=ROOT.parent/'jev-1.14-comparison-benchmark'
STAGING=TEXT/'runs/visual_benchmark_curation_PRIVATE'
OLD_INPUT=STAGING/'codex_execution_2026-10-15/run_01/input_variant_manifest.json'
OLD_INPUT_HASH='4ce82fcc59fd3238d638d2c2d0e5e54baca69a0e3877835f100eb9ef1f8c1fea'
QUESTION_HASH='0791918388e328cdd49acd37eb296143f50859d1f554462039db465a81f3f27f'
OUT=ROOT/'runs/native_images_2026-10-20'
ENV=ROOT.parent.parent/'the village 14947/.env'
REUSED=('typesafe/jev-1.14','openai/gpt-6-luna-decisions')
TRANSIENT={408,429,*range(500,600)}
MODELS={
 'respan02':('Respan Span-02','respan/span-02','respan'),
 'pplx_decider12':('Perplexity Decider v1.2','perplexity/pplx-decider-v1.2','perplexity'),
 'pplx_flash12':('Perplexity Decider Flash v1.2','perplexity/pplx-decider-flash-v1.2','perplexity'),
 'liquid_ultra':('Liquid d1-ultra','liquid/d1-ultra','liquid'),
 'liquid_d1':('Liquid d1','liquid/d1','liquid'),
 'jev113':('Jev 1.13','typesafe/jev-1.13','typesafe'),
 'mercury_decide':('Mercury Decide','inception/mercury-decide','inception'),
 'clef':('Cloudflare Clef','cloudflare/clef','cloudflare'),
 'clef_flash':('Cloudflare Clef Flash','cloudflare/clef-flash','cloudflare'),
 'clef_omni':('Cloudflare Clef Omni','cloudflare/clef-omni','cloudflare'),
 'classify1':('ScaleDown Classify-1','scaledown/classify-1','scaledown'),
 'd3_turbo':('d3-turbo','vllm-sr/d3-turbo',None),
 'amos_large':('Amos 1 Large','amos-1-large',None),
 'kettei_fat':('kettei-fat','kettei-fat',None),
}
SOFTWARE=('image_models_2026_10_20.py','test_image_models_2026_10_20.py','benchmark.py')
GLOBAL_GUARD=threading.Lock()


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return bank.canonical(value)
def rows(path):return bank.rows(path) if Path(path).exists() else []
def now():
    t=datetime.now(timezone.utc)
    return {'utc':t.isoformat(),'toronto':t.astimezone(ZoneInfo('America/Toronto')).isoformat()}
def append(path,value):
    with Path(path).open('a') as f:
        f.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def bound(path,value):
    path=Path(path)
    if path.exists():assert json.loads(path.read_text())==value,'Immutable binding changed: '+str(path)
    else:path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def config(mid):
    label,model,provider=MODELS[mid]
    if provider:return dict(label=label,model=model,provider=provider,host='openrouter.ai',path='/api/alpha/decisions',
        key='OPENROUTER_API_KEY',wire='state_parts',interval=.2,free=False)
    host,key,wire,interval={
       'd3_turbo':('decision.vllm-sr.ai','D3-TURBO_API_KEY','top_image_data_urls',.2),
       'amos_large':('api.amos.scira.ai',None,'top_images',1.1),
       'kettei_fat':('api.sqwish.ai','SQWISH_API_KEY','state_parts',2.1)}[mid]
    return dict(label=label,model=model,provider=None,host=host,path='/v1/systemone',key=key,
        wire=wire,interval=interval,free=mid!='kettei_fat')


def credentials(mid):
    name=config(mid)['key']
    if name is None:return ''
    from dotenv import dotenv_values
    values=dotenv_values(ENV)
    value=str(os.environ.get(name) or values.get(name) or '').strip()
    assert value,name+' is not configured'
    return value


def inputs():
    assert digest(ROOT/'data/questions.jsonl')==QUESTION_HASH
    assert digest(OLD_INPUT)==OLD_INPUT_HASH
    m=json.loads(OLD_INPUT.read_text());assets=m['assets']
    assert m['questions_sha256']==QUESTION_HASH and len(assets)==227
    public={r['asset_id']:r for r in rows(ROOT/'data/assets.jsonl')}
    for aid,a in assets.items():
        p=Path(a['path']);assert p.resolve().is_relative_to(STAGING.resolve()) and not p.is_symlink()
        assert digest(p)==a['sha256']==public[aid]['sha256'],aid
    questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    order=[r['candidate_id'] for r in rows(ROOT/'data/request_plan.jsonl') if r['model_requested']==REUSED[0]]
    assert len(questions)==len(order)==len(set(order))==200 and set(order)==set(questions)
    assert {q['family_id'] for q in questions.values()}=={f'V{i:02}' for i in range(1,21)}
    return questions,assets,order


def payload(q,assets,mid):
    cfg=config(mid);encoded=[]
    for aid in q['asset_ids']:
        a=assets[aid];raw=Path(a['path']).read_bytes();assert sha256(raw).hexdigest()==a['sha256']
        encoded.append((a['mime'],base64.b64encode(raw).decode('ascii')))
    question={'type':'choice','instructions':q['question']+'\n\nRules: '+q['rules'],
              'criteria':{o['id']:o['text'] for o in q['options']}}
    if cfg['wire'] in ('top_images','top_image_data_urls'):
        # Documented Amos/d3 image argument, not JSON image data disguised as text.
        images=['data:'+mime+';base64,'+v if cfg['wire']=='top_image_data_urls' else v for mime,v in encoded]
        body={'model':cfg['model'],'state':'','images':images,
              'questions':{'decision':question}}
    else:
        body={'model':cfg['model'],'state':[{'type':'image_url','image_url':{'url':'data:'+mime+';base64,'+v}}
              for mime,v in encoded],'questions':{'decision':question}}
    if cfg['provider']:body['provider']={'only':[cfg['provider']],'allow_fallbacks':False,'require_parameters':True}
    return body


def plan(mid,questions,assets,order):
    result=[]
    for index,qid in enumerate(order,1):
        q=questions[qid];body=canonical(payload(q,assets,mid))
        result.append(dict(request_index=index,candidate_id=qid,family_id=q['family_id'],
            model_id=mid,model_requested=config(mid)['model'],request_payload_sha256=sha256(body).hexdigest(),
            request_body_bytes=len(body),image_sha256=[assets[aid]['sha256'] for aid in q['asset_ids']],
            image_count=len(q['asset_ids']),
            semantic_input_sha256=bank.digest({k:q[k] for k in ('question','rules','options','asset_ids')})))
    return result


def send(body,key,mid,operation):
    cfg=config(mid);ctx=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
    conn=http.client.HTTPSConnection(cfg['host'],timeout=10,context=ctx)
    r=dict(http_status=0,raw_response={},error='',transport_failure=False,response_headers={},started=now())
    headers={'Content-Type':'application/json','Accept':'application/json'}
    if key:headers['Authorization']='Bearer '+key
    if mid=='kettei_fat':headers['Idempotency-Key']=operation
    start=time.perf_counter()
    try:
        conn.connect();conn.sock.settimeout(max(.001,90-(time.perf_counter()-start)))
        conn.request('POST',cfg['path'],body=body,headers=headers)
        conn.sock.settimeout(max(.001,90-(time.perf_counter()-start)));response=conn.getresponse()
        r.update(http_status=response.status,headers_latency_ms=(time.perf_counter()-start)*1000,
            response_headers={k.lower():v for k,v in response.getheaders() if k.lower() in
                {'retry-after','date','x-request-id','x-openrouter-request-id','content-type','idempotency-replayed'}})
        parts=[];size=0
        while True:
            left=90-(time.perf_counter()-start)
            if left<=0:raise TimeoutError('90-second total deadline')
            conn.sock.settimeout(left);chunk=response.read1(65536)
            if not chunk:break
            size+=len(chunk);assert size<=4*1024**2
            parts.append(chunk)
        text=b''.join(parts).decode()
        if key:text=text.replace(key,'[REDACTED]')
        try:r['raw_response']=json.loads(text)
        except ValueError:r['error']='Non-JSON response: '+text[:200]
        if response.status!=200:r['error']='HTTP '+str(response.status)
    except Exception as exc:
        message=type(exc).__name__+': '+str(exc)
        r['error']=message.replace(key,'[REDACTED]') if key else message
        r['transport_failure']=isinstance(exc,(OSError,http.client.HTTPException))
    finally:
        r.update(latency_ms=(time.perf_counter()-start)*1000,completed=now());conn.close()
    return r


def number(v):return not isinstance(v,bool) and isinstance(v,(int,float)) and math.isfinite(v) and v>=0


def parse(response,choices,mid):
    raw=response.get('raw_response');raw=raw if isinstance(raw,dict) else {}
    answers=raw.get('answers');answers=answers if isinstance(answers,dict) else {}
    answer=answers.get('decision');answer=answer if isinstance(answer,dict) else {}
    choice=answer.get('choice');usage=raw.get('usage');usage=usage if isinstance(usage,dict) else {}
    ok=response['http_status']==200 and not response.get('error') and isinstance(choice,str) and choice in choices and not raw.get('error')
    status='ok' if ok else 'http_failure' if response['http_status']!=200 else 'invalid_answer'
    if response.get('transport_failure'):status='transport_failure'
    returned=raw.get('model');wanted=config(mid)['model']
    if status=='ok' and not (isinstance(returned,str) and (returned==wanted or returned.startswith(wanted+'-')) and 'latest' not in returned):status='identity_mismatch'
    p=answer.get('probabilities');valid=isinstance(p,dict) and set(p)==set(choices)
    if valid:valid=all(number(v) and v<=1 for v in p.values()) and abs(math.fsum(p.values())-1)<=1e-6
    amount=(raw.get('charge') or {}).get('amount_usd') if mid=='kettei_fat' else usage.get('cost')
    reported=str(Decimal(str(amount))) if amount is not None else None
    if reported is not None:assert Decimal(reported).is_finite() and Decimal(reported)>=0
    accounted='0' if config(mid)['free'] else reported
    return dict(status=status,choice=choice if status=='ok' else None,probabilities=p if valid else None,
        probabilities_valid=bool(valid),confidence=answer.get('confidence'),usage=usage,
        reported_output_tokens=usage.get('output_tokens'),
        reasoning_text_present=any(raw.get(k) or answer.get(k) for k in ('reasoning','reasoning_content','explanation')),
        model_returned=returned,provider=raw.get('provider'),reported_cost_usd=reported,accounted_cost_usd=accounted,
        cost_source='public_free_access_not_api_reported' if config(mid)['free'] else 'api_reported' if reported is not None else 'unreported')


def metadata(mid,out):
    path=out/'metadata.json'
    if path.exists():return json.loads(path.read_text())
    cfg=config(mid)
    if cfg['provider']:
        url='https://openrouter.ai/api/v1/models/'+cfg['model']+'/endpoints'
        with urllib.request.urlopen(url,context=ssl.create_default_context(cafile='/etc/ssl/cert.pem'),timeout=30) as r:data=json.load(r)['data']
        matches=[e for e in data['endpoints'] if e['tag']==cfg['provider'] and e.get('status')==0 and not e.get('service_tier')]
        assert 'image' in data['architecture']['input_modalities'] and len(matches)==1,'Pinned image route not available: '+mid
        selected=matches[0]
        value=dict(retrieved=now(),source=url,architecture=data['architecture'],endpoint=selected)
    else:
        caps=json.loads((TEXT/'direct_additions_2026-10-20/image_capabilities.json').read_text())['models'][mid]
        assert caps['image_input'];value=dict(retrieved=now(),source=caps['source'],capability=caps)
    bound(path,value);return value


def probes():
    return [dict(candidate_id='PROBE_SINGLE',asset_ids=['CCA0131'],
        question='What number identifies the next exit on the road sign?',rules='Read the exit number, not the distance.',
        options=[{'id':'1','text':'2'},{'id':'2','text':'6'},{'id':'3','text':'5'}]),
      dict(candidate_id='PROBE_THREE',asset_ids=['NW_A0001_F1','NW_A0001_F2','NW_A0001_F3'],
        question='Which image shows broad flukes that are mostly uniform grey rather than near-black and mottled?',
        rules='Images are numbered 1, 2 and 3 in the supplied order. Inspect the broad fluke surfaces, not water or spray.',
        options=[{'id':'1','text':'Only Image 1'},{'id':'2','text':'Only Image 2'},
                 {'id':'3','text':'Only Image 3'},{'id':'4','text':'All three'}])]


def check_snapshot(row,cfg,snapshot=None,metadata_value=None):
    if row['status']!='ok':return snapshot
    value={k:row[k] for k in ('model_returned','provider')}
    if cfg['provider']:
        assert row['provider']==metadata_value['endpoint']['provider_name'],'Provider changed'
    if snapshot is not None:assert snapshot==value,'Hosted identity/provider changed'
    return value


def probe(mid,assets,out):
    cfg=config(mid);out.mkdir(parents=True,exist_ok=True);meta=metadata(mid,out);key=credentials(mid)
    snapshot=None
    for index,q in enumerate(probes(),1):
        path=out/f'probe_{index}.json';body=canonical(payload(q,assets,mid));h=sha256(body).hexdigest()
        dispatch=out/f'probe_{index}_dispatch.json'
        if not path.exists():
            assert not dispatch.exists(),'Unresolved probe dispatch; inspect before replay'
            bound(dispatch,dict(payload_sha256=h,image_sha256=[assets[a]['sha256'] for a in q['asset_ids']],
                software_sha256={n:digest(ROOT/n) for n in SOFTWARE},started=now()))
            response=send(body,key,mid,'image-20261020-'+mid+'-probe-'+str(index))
            bound(path,dict(payload_sha256=h,response=response,parsed=parse(response,{o['id'] for o in q['options']},mid)))
            time.sleep(cfg['interval'])
        value=json.loads(path.read_text());assert value['payload_sha256']==h,'Probe wire changed; retain this probe and use a new run label'
        row=parse(value['response'],{o['id'] for o in q['options']},mid)
        if row!=value['parsed']:
            review=out/f'probe_{index}_parser_review.json'
            if review.exists():
                prior=json.loads(review.read_text())
                assert prior['source_probe_sha256']==digest(path) and prior['parsed']==row
            else:
                bound(review,dict(source_probe_sha256=digest(path),
                    original_status=value['parsed']['status'],parsed=row,software_sha256={n:digest(ROOT/n) for n in SOFTWARE},
                    reason='Reinterpret the unscored raw response as a typed decision. Output-token telemetry is recorded, not required to be zero; no repeat inference or changed input.'))
        assert row['status']=='ok','Image compatibility probe failed: '+mid+' '+row['status']
        snapshot=check_snapshot(row,cfg,snapshot,meta)
    bound(out/'snapshot.json',snapshot)
    return snapshot,meta


@contextmanager
def execution_lock(out):
    with (out/'.execution.lock').open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:fcntl.flock(f,fcntl.LOCK_UN)


def prepare(mid,out,questions,assets,order):
    tasks=plan(mid,questions,assets,order);cfg=config(mid)
    bound(out/'manifest.json',dict(version='native-image-200-expansion-20261020-v1',model=cfg,
        question_sha256=QUESTION_HASH,old_input_manifest_sha256=OLD_INPUT_HASH,plan=tasks,
        images='Exact original reviewed compressed C1 bytes and order, all 227 files; no resizing, OCR or caption replacement',
        timing='Fresh HTTPS connect and image upload through complete response body; excludes preparation/admission/rate/retry waits',
        primary='All 200 first attempts, failures unsuccessful; no answer-dependent retries',
        retry='One recovery only for transport or HTTP408/429/5xx; same Sqwish idempotency key',
        speed_screen='First20 and after every subsequent first attempt: stop when cumulative first-attempt median exceeds2000ms',
        concurrency='Four models at most concurrently; one active HTTP request per model; no pooled state',
        spend_guard='Soft known/accounted global scored-attempt guard $5; missing or in-flight charges prevent a hard cap',
        identity='Explicit model ID, no model fallback; pin OpenRouter provider and freeze returned identity/provider',
        free_cost='Amos and d3 currently free public access, not API-reported monetary zeros',
        native_wire=cfg['wire'],key_access='Executor never reads answers, private derivations or earlier choices',
        authorization_date_toronto='2026-10-20',publication_authorized=True))
    bound(out/'software.json',{n:digest(ROOT/n) for n in SOFTWARE})
    return tasks


def reconcile(out,tasks):
    dispatches,attempts,results=(rows(out/n) for n in ('dispatches.jsonl','attempts.jsonl','results.jsonl'))
    assert len({(r['request_index'],r['attempt']) for r in attempts})==len(attempts)
    assert {(r['request_index'],r['attempt']) for r in dispatches}=={(r['request_index'],r['attempt']) for r in attempts},'Unresolved dispatch; do not silently replay'
    indexed={t['request_index']:t for t in tasks};groups={}
    for row in dispatches+attempts+results:assert all(row[k]==v for k,v in indexed[row['request_index']].items())
    for row in attempts:groups.setdefault(row['request_index'],[]).append(row)
    done={r['request_index'] for r in results};assert len(done)==len(results)==len(groups)
    for idx,g in groups.items():
        assert [r['attempt'] for r in g] in ([1],[1,2])
        result=next(r for r in results if r['request_index']==idx)
        assert result['attempts']==len(g) and result['first_status']==g[0]['status'] and result['eventual_status']==g[-1]['status']
    return attempts,results,done


def retry_wait(row):
    v=row.get('response_headers',{}).get('retry-after')
    try:return min(60,max(1,float(v)))
    except (ValueError,TypeError):
        try:return min(60,max(1,(parsedate_to_datetime(v)-datetime.now(timezone.utc)).total_seconds()))
        except (ValueError,TypeError):return 2


def speed_stop(latencies):
    return len(latencies)>=20 and statistics.median(latencies)>2000


def execute(mid,probe_only=False):
    questions,assets,order=inputs();out=OUT/mid;out.mkdir(parents=True,exist_ok=True);cfg=config(mid)
    with execution_lock(out):
        if (out/'exclusion.json').exists():print(mid+' EXCLUDED_INPUT_ROUTE',flush=True);return
        snapshot,meta=probe(mid,assets,out)
        if probe_only:print(mid+' IMAGE_PROBES_OK',flush=True);return
        tasks=prepare(mid,out,questions,assets,order);attempts,results,done=reconcile(out,tasks)
        if (out/'completion.json').exists() or (out/'stop_receipt.json').exists():return
        key=credentials(mid);last=0.
        for task in tasks:
            if task['request_index'] in done:continue
            q=questions[task['candidate_id']];body=canonical(payload(q,assets,mid))
            assert sha256(body).hexdigest()==task['request_payload_sha256']
            collected=[];fatal=False
            for attempt in (1,2):
                delay=max(0,cfg['interval']-(time.monotonic()-last))
                if delay:time.sleep(delay)
                last=time.monotonic()
                with GLOBAL_GUARD:
                    known=sum(Decimal(r['accounted_cost_usd']) for p in OUT.glob('*/attempts.jsonl') for r in rows(p) if r.get('accounted_cost_usd') is not None)
                    assert known<Decimal('5'),'Global known-spend guard'
                    append(out/'dispatches.jsonl',{**task,'attempt':attempt,'dispatch':now()})
                response=send(body,key,mid,'image-20261020-'+mid+'-'+task['request_payload_sha256'])
                row={**task,'attempt':attempt,**response,**parse(response,{o['id'] for o in q['options']},mid)}
                with GLOBAL_GUARD:append(out/'attempts.jsonl',row);attempts.append(row)
                collected.append(row)
                try:check_snapshot(row,cfg,snapshot,meta)
                except AssertionError: fatal=True
                fatal=fatal or row['status']=='identity_mismatch' or row['http_status'] in (401,402,403,404)
                if fatal:break
                if attempt==1 and (row['transport_failure'] or row['http_status'] in TRANSIENT):
                    wait=retry_wait(row);append(out/'retry_waits.jsonl',dict(request_index=task['request_index'],seconds=wait));time.sleep(wait);continue
                break
            result={**task,'attempts':len(collected),'first_status':collected[0]['status'],'eventual_status':collected[-1]['status']}
            append(out/'results.jsonl',result);results.append(result)
            first=[a for a in attempts if a['attempt']==1];latencies=[a['latency_ms'] for a in first]
            progress=dict(model=mid,n=len(first),planned=200,median_ms=statistics.median(latencies),mean_ms=statistics.mean(latencies),
                statuses=dict(Counter(r['status'] for r in first)),time=now())
            append(out/'progress.jsonl',progress)
            if len(first)%20==0:print(json.dumps(progress),flush=True)
            if fatal or speed_stop(latencies):
                bound(out/'stop_receipt.json',{**progress,'reason':'IDENTITY_OR_AUTH_ERROR' if fatal else 'MEDIAN_ABOVE_2000_MS',
                    'included_in_full_bank_ranking':False})
                print(mid+' STOPPED '+str(len(first)),flush=True);return
        reconcile(out,tasks)
        assert len(results)==200
        names=tuple(sorted(p.name for p in out.iterdir() if p.is_file() and p.name not in ('completion.json','.execution.lock')))
        bound(out/'completion.json',dict(status='COMPLETE_200',completed=now(),sha256={n:digest(out/n) for n in names}))
        print(mid+' COMPLETE_200',flush=True)


def validate(mid):
    questions,assets,order=inputs();out=OUT/mid;tasks=prepare(mid,out,questions,assets,order)
    attempts,results,done=reconcile(out,tasks)
    snapshot=json.loads((out/'snapshot.json').read_text());meta=json.loads((out/'metadata.json').read_text())
    for row in attempts:
        assert all(row[k]==v for k,v in parse(row,{o['id'] for o in questions[row['candidate_id']]['options']},mid).items())
        check_snapshot(row,config(mid),snapshot,meta)
    if (out/'completion.json').exists():
        assert len(done)==200
        for name,h in json.loads((out/'completion.json').read_text())['sha256'].items():assert digest(out/name)==h
    print(json.dumps(dict(model=mid,validated=len(done),attempts=len(attempts))))
    return attempts,results


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',choices=(*MODELS,'all'),required=True)
    p.add_argument('--execute',action='store_true');p.add_argument('--probe',action='store_true');p.add_argument('--validate',action='store_true')
    a=p.parse_args();selected=list(MODELS) if a.model=='all' else [a.model]
    if a.validate:
        for mid in selected:validate(mid)
    elif a.execute or a.probe:
        # One serial stream per provider/model; only four streams at once.
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(execute,mid,a.probe):mid for mid in selected}
            for f in as_completed(futures):
                try:f.result()
                except Exception as exc:
                    mid=futures[f];out=OUT/mid;out.mkdir(parents=True,exist_ok=True)
                    receipt=dict(model=mid,error_type=type(exc).__name__,error=str(exc),time=now(),
                        first_attempts=len([r for r in rows(out/'attempts.jsonl') if r['attempt']==1]),
                        included_in_full_bank_ranking=False)
                    bound(out/('operational_error_'+str(time.time_ns())+'.json'),receipt)
                    print(json.dumps(receipt),flush=True)
    else:
        q,assets,order=inputs()
        for mid in selected:
            tasks=plan(mid,q,assets,order)
            print(json.dumps({'model':mid,'planned':len(tasks),'largest_body_bytes':max(t['request_body_bytes'] for t in tasks),'inference_calls':0}))
