"""Publish the sealed Celeris image run offline; never replay inference."""
import argparse
import base64
from collections import Counter
from copy import deepcopy
import csv
from decimal import Decimal
from hashlib import sha256
from html import escape
import io
import json
import math
from pathlib import Path
import re
import shutil
import statistics

from benchmark import canonical,rows
from repo_layout import ROOT,MANIFEST
from score import load_key
import publish_llm_image_reference_2026_10_25 as llm
import publish_local_images_2026_10_25 as previous

NAME='celeris_2026-10-26'
DEST=ROOT/'results/releases'/NAME
OLD=ROOT/'results/releases/llm_reference_2026-10-25'
CAPTURE=ROOT.parent/'text-decision-hardening/runs/celeris_image_benchmark_2026-10-25_233721'
MODEL='celeris-1.1-decision'
MID='celeris11_decision'
SITE='https://etsabary.github.io/visual-decision-benchmark/report.html'
KEY_HASH=llm.KEY_HASH
PURPLE,BLUE,YELLOW=llm.PURPLE,llm.BLUE,llm.YELLOW
digest,write,dump=llm.digest,llm.write,llm.dump
FIELDS={'model_id','model_requested','model_returned','request_index','candidate_id','family_id','attempt',
    'status','latency_ms','question_sha256','request_payload_sha256','image_sha256','input_tokens',
    'output_tokens','estimated_cost_usd','state_truncated_reported','response_sha256'}


def packet_digest(value):return sha256(canonical(value)).hexdigest()


def payload(q,images):
    named={'image_'+str(i):'data:image/png;base64,'+base64.b64encode(raw).decode() for i,raw in enumerate(images,1)}
    return dict(model=MODEL,state='The images in order are: '+', '.join(named)+'. Use their pixels to answer the question.',
        questions={'decision':dict(type='choice',instructions=q['question']+'\n\nRules: '+q['rules'],
            criteria={o['id']:o['text'] for o in q['options']})},
        x_celeris=dict(explain=False,images=named,max_soft_tokens=1120))


def native_choice(raw,options):
    assert raw['model']==MODEL and set(raw['answers'])=={'decision'}
    a=raw['answers']['decision'];p=a['probabilities']
    assert a['type']=='choice' and a['choice'] in options and set(p)==set(options)
    assert all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in p.values())
    assert abs(sum(p.values())-1)<=.005
    assert type(raw['usage']['output_tokens']) is int and raw['usage']['output_tokens']==0
    assert raw['usage']['input_tokens']>0 and raw.get('state_truncated') is not True
    assert not a.get('explanation') and not (raw.get('x_celeris') or {}).get('explanations')
    assert not any(raw.get(k) for k in ('text','content','reasoning','reasoning_content'))
    return a['choice']


def load(key_path):
    assert digest(key_path)==KEY_HASH
    gold=load_key(key_path);questions={q['candidate_id']:q for q in rows(ROOT/'data/questions.jsonl')}
    assert len(questions)==200 and set(gold)==set(questions)
    seal=json.loads((CAPTURE/'seal.json').read_text())
    for name,h in seal['files'].items():assert digest(CAPTURE/name)==h,name
    protocol=json.loads((CAPTURE/'manifest.json').read_text());report=json.loads((CAPTURE/'final_report.json').read_text())
    audit=json.loads((CAPTURE/'audit_receipt.json').read_text())
    assert audit['status']=='PASS' and audit['all_dispatches_resolved'] and audit['scored_retries']==0
    assert report['state']=='complete' and protocol['bank_sha256']==digest(ROOT/'data/questions.jsonl')
    assert protocol['model']==MODEL and protocol['max_soft_tokens']==1120 and not protocol['explanations']
    png=CAPTURE.parent/'local_image_png_2026-10-25/image_variant_manifest.json'
    assert digest(png)==protocol['image_variant_manifest_sha256']
    assets=json.loads(png.read_text())['assets'];pixels={}
    for aid,a in assets.items():
        data=Path(a['path']).read_bytes()
        assert data.startswith(bytes.fromhex('89504e470d0a1a0a')) and sha256(data).hexdigest()==a['sha256']
        pixels[aid]=data
    rr=rows(CAPTURE/'attempts.jsonl');dd=rows(CAPTURE/'dispatches.jsonl')
    assert len(rr)==len(dd)==len({r['item_id'] for r in rr})==200
    assert [r['item_id'] for r in rr]==protocol['question_order']
    timing=[]
    for i,(r,d) in enumerate(zip(rr,dd),1):
        q=questions[r['item_id']]
        assert r['request_index']==d['request_index']==i and r['item_id']==d['item_id']
        assert r['attempt']==d['attempt']==1 and r['status']=='ok' and r['transport']['http_status']==200
        assert r['request_payload_sha256']==d['request_payload_sha256']==packet_digest(payload(q,[pixels[aid] for aid in q['asset_ids']]))
        assert r['question_sha256']==d['question_sha256']==packet_digest(q)
        assert r['image_sha256']==d['image_sha256']==[assets[aid]['sha256'] for aid in q['asset_ids']]
        assert native_choice(r['transport']['raw'],[o['id'] for o in q['options']])==r['choice']
        assert r['model_returned']==MODEL and r['usage']==r['transport']['raw']['usage']
        assert r['latency_ms']==r['transport']['latency_ms'] and r['family_id']==q['family_id']
        timing.append(dict(model_id=MID,model_requested=MODEL,model_returned=MODEL,request_index=i,
            candidate_id=r['item_id'],family_id=r['family_id'],attempt=1,status='ok',latency_ms=r['latency_ms'],
            question_sha256=r['question_sha256'],request_payload_sha256=r['request_payload_sha256'],image_sha256=r['image_sha256'],
            input_tokens=r['usage']['input_tokens'],output_tokens=0,
            estimated_cost_usd=str(Decimal(r['usage']['input_tokens'])*Decimal('.00000004')),
            state_truncated_reported=r['state_truncated_reported'],response_sha256=packet_digest(r['transport']['raw'])))
    hit=sum(r['choice']==gold[r['item_id']] for r in rr)
    assert hit==report['correct']==143 and report['usable']==200
    families={f:dict(n=10,correct=sum(r['family_id']==f and r['choice']==gold[r['item_id']] for r in rr),usable=10)
        for f in sorted({q['family_id'] for q in questions.values()})}
    assert Counter(r['family_id'] for r in rr)=={f:10 for f in families}
    assert all((v['n'],v['correct'])==(report['families'][f]['n'],report['families'][f]['correct']) for f,v in families.items())
    times=[r['latency_ms'] for r in rr];ordered=sorted(times);pos=199*.95;lo=int(pos)
    quantiles=dict(mean_ms=statistics.mean(times),median_ms=statistics.median(times),p95_ms=ordered[lo]+(ordered[lo+1]-ordered[lo])*(pos-lo))
    assert all(math.isclose(v,report[k],rel_tol=1e-12) for k,v in quantiles.items())
    assert max(statistics.median(times[:k]) for k in range(20,201))<=2000
    cost=sum((Decimal(t['estimated_cost_usd']) for t in timing),Decimal(0))
    assert cost==Decimal(report['cost_usage_times_tariff_usd'])==Decimal('.01175164')
    probes=rows(CAPTURE/'admission.jsonl')
    assert len(probes)==len(rows(CAPTURE/'admission_dispatches.jsonl'))==5
    assert [p['choice'] for p in probes]==['1','2','1','2','1'] and all(p['status']=='ok' for p in probes)
    catalog=json.loads((CAPTURE/'catalog_start.json').read_text())['data']
    assert catalog==json.loads((CAPTURE/'catalog_end.json').read_text())['raw']
    old=json.loads((OLD/'summary.json').read_text());s=deepcopy(old)
    s['models'][MID]=dict(model_id=MID,label='Celeris 1.1 Decision',model_requested=MODEL,
        model_kind='hosted_decision',execution_location='hosted',route='Direct Celeris native SystemOne; explanations off',
        date='2026-10-25',complete=True,reused=False,n=200,correct=143,accuracy=.715,usable=200,accuracy_usable=.715,
        **quantiles,status_counts={'ok':200},retries=0,families=families,public_free_access=False,
        cost_source='usage_times_published_tariff',usage_based_core_cost_usd=str(cost),
        core_cost=dict(known_api_usd='0',reported_records=0,missing_api_records=200,accounted_usd=str(cost)),
        core_cost_per_1000_known_usd=str(cost*5),reported_input_tokens=sum(t['input_tokens'] for t in timing),
        reported_output_tokens=0,reported_reasoning_text=0,image_variant=protocol['input_variant'],
        max_soft_tokens=1120,probe_cost_usd=report['probe_cost_usage_times_tariff_usd'],admission_probes=5,
        cost_scope='Reported input usage times captured tariff; estimate, not monetary receipts',
        reasoning_verification='Explanations disabled; zero reported output tokens; internal computation not independently attested',
        processed_input_attestation='No per-item processed-input or truncation counter reported')
    s.update(version='image-celeris-20261026-v1',updated_date_toronto='2026-10-26',complete_routes=19,
        hosted_model_count=16,decision_models_ranked=18,decision_models_reviewed=old['decision_models_reviewed']+1,
        decision_model_ids=[*old['decision_model_ids'],MID],complete_first_attempt_cases=3800,
        prior_summary_sha256=digest(OLD/'summary.json'),added_model_ids=[MID],
        historical_cost_scope_note=old['historical_cost_scope_note']+' Later Sol and Celeris have separate model costs; inherited hosted aggregates are not totals for this 19-route release.',
        input_variant_note='Celeris, Sol and two local routes share the recorded PNG variant. Celeris requests max_soft_tokens=1120. Earlier 15 hosted decisions retain original mixed PNG/JPEG bytes.')
    s['rank_order']=sorted(s['models'],key=lambda mid:(-s['models'][mid]['correct'],s['models'][mid]['median_ms']))
    assert all(s['models'][mid]==v for mid,v in old['models'].items()) and s['llm_speed_stops']==old['llm_speed_stops']
    metadata=dict(model_requested=MODEL,selected_catalog=next(m for m in catalog['data'] if m['id']==MODEL),
        base_url=protocol['base_url'],endpoint=protocol['endpoint'],explanations=False,max_soft_tokens=1120,
        image_adapter='Named data:image/png;base64 URLs in x_celeris.images; ordered image markers in state',
        catalog_unchanged_at_end=True,concurrency=1,scored_retries=0,min_dispatch_spacing_seconds=.25,
        pricing=dict(input_usd_per_million='0.04',output='free',basis='Captured October25 documentation; usage-times-tariff estimate, not receipts'),
        sources=dict(models='https://docs.celeris.ai/models',images='https://docs.celeris.ai/images',pricing='https://docs.celeris.ai/pricing'),
        source_evidence_sha256={n:digest(CAPTURE/n) for n in ('runner.py','executor_source.py.snapshot','attempts.jsonl','dispatches.jsonl','admission.jsonl','manifest.json','final_report.json','audit_receipt.json','seal.json','docs_decisions.html','docs_models.html','docs_pricing.html','catalog_start.json','catalog_end.json')})
    return s,timing,metadata,protocol


def money(m,normalized=False):
    # Keep public validation independent of plotting dependencies.
    if previous.is_local(m):return 'Unmeasured local compute'
    if m['public_free_access']:return 'Free access†'
    calculated=m.get('cost_source')=='usage_times_published_tariff'
    value=Decimal(m['core_cost_per_1000_known_usd'] if normalized else
        m['usage_based_core_cost_usd'] if calculated else m['core_cost']['known_api_usd'])
    return ('~' if calculated else '')+f'${value:.6f}'+('*' if not calculated and m['core_cost']['missing_api_records'] else '')


def table(s):
    value=llm.table(s).replace('Actual 200 cost','200 cost / basis')
    line=next(line for line in value.splitlines() if '| Celeris 1.1 Decision |' in line)
    return value.replace(line,line.replace('Hosted decision · original PNG/JPEG','Hosted decision · PNG · resolution 1120'))


def narrative(s):
    m=s['models'][MID]
    high='; '.join(s['families'][f]['name']+f" {v['correct']}/10" for f,v in m['families'].items() if v['correct']==10)
    low='; '.join(s['families'][f]['name']+f" {v['correct']}/10" for f,v in m['families'].items() if v['correct']==3)
    intro='''The comparison contains **19 complete routes: 16 hosted decision models, two local models and GPT-6 Sol as a non-reasoning LLM reference**. Every complete row has 200 first attempts across 20 categories. All 18 prior records and the three separate LLM speed stops are unchanged.

**Celeris 1.1 Decision scored 143/200 (71.5%), with 667/585/1120 ms mean/median/p95 and 200 usable decisions.** It passed the existing two-second cumulative-median cutoff. Blue identifies its hosted route; purple identifies local RTX 2060 runs and pale yellow identifies Sol.

Amos 1 Large remains highest at 159/200 (79.5%), followed by GLiDE at 158 (79.0%) and d3-turbo at 155 (77.5%). Sol retains 147 (73.5%). Every previous score, cost, duration, date and exclusion is preserved; publication used saved evidence without new model calls.

## Celeris: accuracy, speed and cost

Celeris answered four fewer questions correctly than Sol, a two-percentage-point gap, with a 585 ms median versus Sol's 1,637 ms. It finished 16 answers behind Amos and 15 behind GLiDE. These observed gaps on one developing bank do not establish a general ability ordering. Celeris is the ninth complete route in the accuracy-sorted table.

Its estimated 200-question cost is **~$0.01175164**, or **~$0.05875820 per 1,000**. This is 293,791 reported input tokens times the captured USD 0.04/million tariff, not monetary receipts. Five separate image-binding probes cost an estimated $0.00042344. Sol's reported bank charge was $0.591634; GLiDE's usage-times-tariff estimate was $0.00767264. Local hardware and electricity cost remains unmeasured.

## Celeris category profile

<!-- HIGH_LOW -->

Every category has ten questions, so one answer changes a category score by ten percentage points. The full 380-cell matrix preserves all model profiles; a category's measured score is not a promise of reliability on other tasks.

## Celeris image settings and timing

The exact requested and returned model was `celeris-1.1-decision`, using the direct native SystemOne endpoint with explanations disabled. Images were named `image_1`, `image_2`, etc. in `x_celeris.images`, supplied as base64 PNG URLs in original order, with corresponding state markers. Question wording, rules, option IDs, order and the frozen answer key were unchanged. Variable three/four/five-choice outputs were checked against each question's exact choices.

The run used the exact recorded PNG bytes shared with Sol and the two local models. No image was resized, replaced with OCR or captioned. `max_soft_tokens=1120` selected the highest resolution control in the captured [Celeris image documentation](https://docs.celeris.ai/images). Its internal preprocessing is provider-controlled. Earlier 15 hosted decision records retain their original mixed PNG/JPEG bytes. File format, resolution, route, hardware, date and load qualify accuracy and timing comparisons.

Five synthetic probes checked red/blue recognition, reversed pair order and a three-image input; all passed. The initial 20 scored requests measured 677/572/1105 ms mean/median/p95. The cumulative median stayed below 2,000 ms through all 200. All first attempts are retained; no retries or accuracy-only stopping. Fresh HTTPS calls were serial, at least 0.25 seconds between dispatch starts; PNG/base64/JSON preparation and idle pacing were excluded, upload and complete response included.

All 200 outputs were native typed choices with probability distributions, zero reported output tokens and no generated explanation. These facts do not independently attest to hidden computation, model weights or per-item processed-input delivery. Start/end model catalogs matched. The [captured protocol](Celeris_PROTOCOL) and [answer-free timing/usage evidence](Celeris_TIMING) retain settings and bindings without publishing model choices or answer labels.

'''
    intro=intro.replace('<!-- HIGH_LOW -->','**10/10:** '+high+'.\n\n**3/10:** '+low+'.')
    old=(OLD/'analysis.md').read_text();old='## Why Sol'+old.split('## Why Sol',1)[1]
    return (intro+old.replace('360-cell category ranking','380-cell category ranking'))


def bind_layout():
    m=json.loads(MANIFEST.read_text())
    paths=set(m['current_files'])|{p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*.py')}|{'documents/CELERIS_IMAGE_RUN.md','docs/sitemap.xml'}
    m['current_files']={name:digest(ROOT/name) for name in sorted(paths)};dump(MANIFEST,m)


def mirror():shutil.copytree(DEST,ROOT/'docs'/NAME,dirs_exist_ok=True)


def plot(s):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Patch
    import numpy as np
    import textwrap
    from plot_native_images import speed_color,cost_color
    ids=s['rank_order'];models=[s['models'][mid] for mid in ids];labels=[m['label'] for m in models];y=np.arange(len(ids))
    colors=[YELLOW if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE for mid,m in zip(ids,models)]
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'celeris-image-20261026'}):
        def save(fig,stem):
            for ext in ('png','svg'):fig.savefig(DEST/(stem+'.'+ext),dpi=160,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            svg=DEST/(stem+'.svg');write(svg,'\n'.join(line.rstrip() for line in svg.read_text().splitlines()));plt.close(fig)
        fig,axes=plt.subplots(1,3,figsize=(18,12.5),sharey=True,gridspec_kw={'width_ratios':[1.2,1.1,1.25]})
        axes[0].barh(y,[m['accuracy']*100 for m in models],color=colors,height=.65)
        axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].set_xlim(0,112)
        axes[0].axvline(s['random_uniform_baseline']*100,color='#8b98a5',linestyle=':',linewidth=1)
        for i,(mid,m) in enumerate(zip(ids,models)):
            axes[0].text(m['accuracy']*100+1,i,f"{m['correct']}/200 · {m['accuracy']:.1%}",va='center',fontsize=9)
            axes[1].plot([m['median_ms'],m['p95_ms']],[i,i],color='#93a1ad',linewidth=2)
            axes[1].scatter(m['median_ms'],i,c=speed_color(m['median_ms']),s=50,edgecolor='#334155');axes[1].scatter(m['p95_ms'],i,c='#334155',marker='d',s=22)
            if previous.is_local(m):axes[2].text(.03,i,'Local compute · unmeasured',transform=axes[2].get_yaxis_transform(),color=PURPLE,va='center',fontsize=9)
            elif m['public_free_access']:axes[2].text(.03,i,'Free access†',transform=axes[2].get_yaxis_transform(),va='center',fontsize=9)
            else:
                v=float(m['core_cost_per_1000_known_usd']);axes[2].scatter(v,i,c=cost_color(v),s=50,edgecolor='#334155');axes[2].annotate(money(m,True),(v,i),xytext=(8,0),textcoords='offset points',va='center',fontsize=9)
        for tick,mid,m in zip(axes[0].get_yticklabels(),ids,models):
            tick.set_color('#8d6c0a' if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE)
            if mid=='reference_sol' or previous.is_local(m):tick.set_weight('bold')
        axes[1].set_xscale('log');axes[1].set_xlim(100,5000);axes[2].set_xscale('log');axes[2].set_xlim(.005,12)
        for a,title in zip(axes,['Accuracy · 200 first attempts','Response time · median and p95','USD / 1,000 questions']):
            a.set_title(title,fontweight='bold',pad=14);a.grid(axis='x',alpha=.15);a.set_axisbelow(True);a.tick_params(axis='y',length=0)
            for spine in a.spines.values():spine.set_visible(False)
        axes[0].set_xlabel('Accuracy (%) · dotted line: 23.44% guessing');axes[1].set_xlabel('ms, log scale · circle median · diamond p95');axes[2].set_xlabel('USD, log scale · rescales actual 200-question cost')
        fig.suptitle('19 complete routes · 16 hosted decisions + 2 local + Sol reasoning-off reference',fontsize=18,y=.98)
        handles=[Patch(color=BLUE,label='Hosted decisions'),Patch(color=PURPLE,label='Local RTX 2060 6 GB'),Patch(color=YELLOW,label='LLM reference, reasoning off')]
        fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.955),ncol=3,frameon=False)
        fig.text(.025,.025,'Celeris: 143/200, 667/585/1120 ms mean/median/p95; Sol: 147/200, 1637 ms median. All 18 earlier records unchanged.\nSonnet 5.5, Opus 5 and Qwen3.8-Max stopped after 20 above the two-second median cutoff; partial results are outside this figure.\nCeleris/Sol/local inputs share recorded PNGs; Celeris resolution 1120; earlier hosted rows keep original formats. Dates, routes and hardware differ.\nPurple locals use the deliberately chosen older RTX 2060 6 GB; hardware/electricity unmeasured. † Free access is not a production tariff; ~ tariff calculation; * missing charges.',fontsize=9)
        fig.subplots_adjust(left=.21,right=.98,top=.88,bottom=.16,wspace=.34);save(fig,'overview')
        cmap=LinearSegmentedColormap.from_list('accuracy',['#fff4d0','#d5ebce','#77c5c8','#338bac','#183f7a'])
        titles=['Objects, space and routes','Transformations, rules and state','Diagrams and documents','Comparison, perspective and uncertainty']
        for block in range(4):
            fs=list(s['families'])[block*5:block*5+5];values=np.array([[m['families'][f]['correct']/10 for f in fs] for m in models])
            fig,a=plt.subplots(figsize=(13.5,11.5));im=a.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto');a.set_yticks(range(len(models)),labels)
            for tick,mid,m in zip(a.get_yticklabels(),ids,models):
                tick.set_color('#8d6c0a' if mid=='reference_sol' else PURPLE if previous.is_local(m) else BLUE)
                if mid=='reference_sol' or previous.is_local(m):tick.set_weight('bold')
            a.set_xticks(range(5),['\n'.join(textwrap.wrap(s['families'][f]['name'],21))+'\n10 questions' for f in fs]);a.tick_params(length=0,pad=8)
            for i in range(len(models)):
                for j in range(5):a.text(j,i,f'{round(values[i,j]*10)}/10',ha='center',va='center',color='white' if values[i,j]>=.7 else '#183044')
            for spine in a.spines.values():spine.set_visible(False)
            fig.colorbar(im,ax=a,pad=.025,fraction=.025).set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
            fig.suptitle(titles[block],fontsize=19,y=.975);fig.text(.025,.025,'Purple names: local RTX 2060. Amber name: Sol reasoning-off LLM reference. Cells always encode accuracy on a fixed 0–100% scale.\nOnly complete 200-question routes; each cell is correct / 10. One answer changes a category by ten percentage points.',fontsize=10)
            fig.subplots_adjust(left=.29,right=.95,top=.91,bottom=.15);save(fig,'abilities_'+str(block+1))


def build(key_path):
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed dated evidence'
    s,timing,metadata,protocol=load(key_path);DEST.mkdir(parents=True,exist_ok=True)
    dump(DEST/'summary.json',s);dump(DEST/'celeris_model_metadata.json',metadata)
    dump(DEST/'celeris_execution_protocol.json',protocol)
    write(DEST/'celeris_timing_evidence.jsonl','\n'.join(json.dumps(r,ensure_ascii=False,allow_nan=False) for r in timing))
    for filename in ('image_variant_manifest.json','local_model_metadata.json','local_timing_evidence.jsonl',
        'local_admission_findings.json','llm_speed_stops.json','speed_stops.csv','llm_model_metadata.json',
        'selection_basis.json','llm_timing_evidence.jsonl','llm_execution_protocol.json','execution_source_hashes.json'):
        shutil.copyfile(OLD/filename,DEST/filename)
    for filename,fields,values in (
        ('leaderboard.csv',['model_id','model','kind','correct','questions','accuracy','usable','mean_ms','median_ms','p95_ms','bank_cost_basis','cost_per_1000','date'],
         ([mid,m['label'],('llm_reference' if mid=='reference_sol' else 'local' if previous.is_local(m) else 'hosted_decision'),m['correct'],200,m['accuracy'],m['usable'],m['mean_ms'],m['median_ms'],m['p95_ms'],money(m),money(m,True),m['date']] for mid in s['rank_order'] for m in [s['models'][mid]])),
        ('family_scores.csv',['model_id','model','family_id','family','correct','questions','accuracy'],
         ([mid,s['models'][mid]['label'],f,definition['name'],s['models'][mid]['families'][f]['correct'],10,s['models'][mid]['families'][f]['correct']/10] for mid in s['rank_order'] for f,definition in s['families'].items()))):
        stream=io.StringIO(newline='');w=csv.writer(stream,lineterminator='\n');w.writerow(fields);w.writerows(values);write(DEST/filename,stream.getvalue())
    notes=narrative(s).replace('Celeris_PROTOCOL','results/releases/'+NAME+'/celeris_execution_protocol.json').replace('Celeris_TIMING','results/releases/'+NAME+'/celeris_timing_evidence.jsonl')
    write(DEST/'analysis.md',notes.replace('](results/releases/'+NAME+'/',']('));plot(s)
    intro,detail=notes.split('## Why Sol',1)
    opening,celeris_notes=intro.split('## Celeris: accuracy, speed and cost',1)
    legend='**Colour key:** blue `#16728c` = hosted decisions; purple `#7c3aed` = local RTX 2060 6 GB; pale yellow with transparency = general LLM reference with reasoning off. Accuracy cells retain the fixed 0–100% scale; speed/cost bands are unchanged.'
    charts='\n\n'.join(f'![Named category scores, part {i}](results/releases/{NAME}/abilities_{i}.png)' for i in range(1,5))
    defs='\n'.join(f"- **[{f} {v['name']}](data/questions/{f}.md)**: {v['description']}" for f,v in s['families'].items())
    report='# Image-grounded System 1 decision benchmark\n\n'+opening.strip()+'\n\n[Open the colour-coded report]('+SITE+')'+f'\n\n![Accuracy, speed and cost](results/releases/{NAME}/overview.png)\n\n'+legend+'\n\n## Overall results\n\n'+table(s)+'\n\n## Celeris: accuracy, speed and cost'+celeris_notes+'\n\n## Why Sol'+detail+'\n\n## Results by named category\n\n'+charts+'\n\n## What the categories test\n\n'+defs+f'\n\n[Aggregate results](results/releases/{NAME}/summary.json) · [Category CSV](results/releases/{NAME}/family_scores.csv) · [Celeris timing/usage](results/releases/{NAME}/celeris_timing_evidence.jsonl) · [Audit](results/releases/{NAME}/audit_receipt.json) · [Celeris method](documents/CELERIS_IMAGE_RUN.md)\n\n[Questions and sources](data/questions/README.md) · [Gallery](docs/gallery.html) · [Attribution](documents/THIRD_PARTY_NOTICES.md) · [Local method](documents/LOCAL_IMAGE_RUNS.md)\n'
    write(ROOT/'README.md',report)
    import markdown
    md=report.replace(f'results/releases/{NAME}/',NAME+'/').replace('(data/questions/','(questions/').replace('(docs/gallery.html)','(gallery.html)')
    for filename in ('LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md','CELERIS_IMAGE_RUN.md'):md=md.replace('(documents/'+filename+')','('+filename+')')
    content=markdown.markdown(md,extensions=['tables','fenced_code','toc'])
    first=content.index('<table>');end=content.index('</table>',first)+len('</table>')
    summary=llm.reference_names(previous.summary_html(s),s).replace('Actual 200 cost','200 cost / basis')
    content=content[:first]+summary+content[end:]
    first=content.index('<p><img alt="Named category scores, part 1"');end=content.index('<h2 id="what-the-categories-test"',first)
    content=content[:first]+llm.reference_names(previous.categories_html(s),s)+content[end:]
    heading=content.index('<h2 id="llm-speed-stops"');first=content.index('<table>',heading);end=content.index('</table>',first)+len('</table>')
    partial=content[first:end]
    for m in s['llm_speed_stops']:partial=partial.replace('<tr>\n<td>'+escape(m['label'])+'</td>','<tr data-speed-stop="'+m['model_id']+'">\n<td>'+escape(m['label'])+'</td>')
    content=content[:first]+'<div class="table-scroll speed-stops">'+partial+'</div>'+content[end:]
    old_html=(OLD/'report.html').read_text();css=re.search(r'<style>(.*?)</style>',old_html,re.S).group(1);js=re.search(r'<script>(.*?)</script>',old_html,re.S).group(1)
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Compare 19 image decision routes on 200 questions: 16 hosted decision models, two local models and a reasoning-off Sol reference. Accuracy, latency, cost and 20 category profiles."><link rel="canonical" href="'+SITE+'"><title>Image decisions · 19 complete routes · Celeris 1.1 and Sol</title><style>'+css+'</style></head><body><nav><a href="#">Overview</a><a href="#overall-results">Scores, speed &amp; cost</a><a href="#celeris-accuracy-speed-and-cost">Celeris analysis</a><a href="#llm-speed-stops">Speed stops</a><a href="#results-by-named-category">Categories</a><a href="gallery.html">Questions &amp; images</a><a href="https://github.com/etsabary/visual-decision-benchmark">GitHub evidence</a></nav><main>'+content+'</main><footer>Updated October 26, 2026. All 18 prior records preserved; speed-stopped LLM samples remain outside the complete ranking.</footer><script>'+js+'</script></body></html>'
    write(ROOT/'docs/report.html',page)
    dated=page.replace(NAME+'/','')
    for href in ('gallery.html','LLM_IMAGE_REFERENCES.md','LOCAL_IMAGE_RUNS.md','THIRD_PARTY_NOTICES.md','CELERIS_IMAGE_RUN.md'):dated=dated.replace('href="'+href+'"','href="../'+href+'"')
    dated=dated.replace('href="questions/','href="../questions/');write(DEST/'report.html',dated)
    guide='# Celeris 1.1 image decisions\n\n'+intro.replace('](results/releases/'+NAME+'/','](../results/releases/'+NAME+'/')+'\n\n[Full image report]('+SITE+')\n'
    write(ROOT/'documents/CELERIS_IMAGE_RUN.md',guide);write(ROOT/'documents/native_image_analysis.md',notes.replace('](results/releases/'+NAME+'/','](../results/releases/'+NAME+'/'))
    method=ROOT/'documents/METHODOLOGY.md'
    if not method.read_text().startswith('# Celeris image addition'):write(method,'# Celeris image addition — October 26, 2026\n\nThe current comparison adds Celeris 1.1 as the 19th complete route. See [Celeris method](CELERIS_IMAGE_RUN.md) for native image binding, the recorded PNG variant, resolution 1120, timing, cost and audit limits. All 18 prior records and three partial speed stops are unchanged.\n\n'+method.read_text())
    release=ROOT/'documents/RELEASE_NOTES.md'
    if not release.read_text().startswith('# Celeris image publication'):write(release,'# Celeris image publication — October 26, 2026\n\n- Added Celeris 1.1: 143/200 (71.5%), 200 usable, 667/585/1120 ms mean/median/p95, primary estimated cost $0.01175164.\n- Preserved all 18 complete records and three partial LLM speed stops. No model calls during publication.\n- 19-route summary and 380 named category cells, hosted blue/local purple/LLM pale yellow, answer-free Celeris timing and private-key audit bindings.\n\n'+release.read_text())
    write(ROOT/'results/README.md','# Dated image results\n\n- [Current: 19 complete routes](releases/'+NAME+'/summary.json): 16 hosted decisions, two local and Sol reasoning-off reference. Celeris 71.5%, 585 ms median; [timing/usage](releases/'+NAME+'/celeris_timing_evidence.jsonl).\n- [Previous 18 routes and three LLM speed stops](releases/llm_reference_2026-10-25/summary.json): unchanged.\n- [Earlier 17-route local release](releases/local_images_2026-10-25/summary.json), [15-hosted release](releases/fastino_2026-10-23/summary.json), [14-model release](releases/native_images_2026-10-20/summary.json), [original release](original_2026-10-15/summary.json).\n\nPresentation snapshots under archives/ preserve historical seals. Celeris, Sol and local routes share recorded PNG bytes; earlier hosted rows keep original mixed formats.\n')
    dump(DEST/'audit_receipt.json',dict(status='VERIFIED_CELERIS_200',prior_18_records_unchanged=True,
        question_sha256=digest(ROOT/'data/questions.jsonl'),key_sha256=KEY_HASH,private_seal_sha256=digest(CAPTURE/'seal.json'),
        scored_first_attempts=200,correct=143,usable=200,admission_probes=5,retries=0,cutoff_ms=2000,
        payloads_rebuilt=200,png_hashes_verified=227,publication_inference_calls=0,
        primary_estimated_cost_usd='0.01175164',cost_basis='Reported input usage times captured tariff; not receipts',
        privacy='Answer-free timing, hashes and aggregates; no model choices, key labels, per-item correctness, credentials, LAN addresses or account state',
        public_scoring_limit='Frozen private-key scoring verified offline; public aggregates alone cannot independently reproduce it'))
    write(ROOT/'docs/sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+SITE+'</loc><lastmod>2026-10-26</lastmod></url></urlset>')
    mirror();bind_layout();print('Built 19 complete routes,380 category cells; prior18 unchanged; no inference.')


def seal():
    assert not (DEST/'manifest.json').exists(),'Never overwrite sealed evidence'
    dump(DEST/'manifest.json',dict(version='image-celeris-20261026-v1',complete_routes=19,questions_each=200,
        complete_llm_references=1,speed_stopped_llm_references=3,question_sha256=digest(ROOT/'data/questions.jsonl'),
        prior_summary_sha256=digest(OLD/'summary.json'),artifacts={p.relative_to(DEST).as_posix():digest(p) for p in sorted(DEST.rglob('*')) if p.is_file()}))
    mirror();bind_layout();paths={ROOT/name for name in json.loads(MANIFEST.read_text())['current_files']};paths.add(MANIFEST);paths.update(p for p in DEST.rglob('*') if p.is_file())
    dump(DEST/'release_checksums.json',{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)});mirror();print('Sealed Celeris image publication and exact dated mirror')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--answer-key',type=Path);p.add_argument('--seal',action='store_true');a=p.parse_args()
    if a.seal:seal()
    else:
        assert a.answer_key,'Explicit frozen external key required for offline scoring';build(a.answer_key)
